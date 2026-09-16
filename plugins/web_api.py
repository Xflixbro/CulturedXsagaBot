# Made by @Awakeners_Bots
# web_api.py — API endpoints for Vercel gateway

from aiohttp import web
from datetime import datetime

_bot_client = None


async def mark_gateway_opened(request):
    token = request.query.get("token")
    if not token or _bot_client is None:
        return web.json_response({"error": "bad request"}, status=400)
    await _bot_client.mongodb.masked_links.update_one(
        {"_id": token}, {"$set": {"gateway_opened_at": datetime.now()}}
    )
    return web.json_response({"ok": True})


async def mark_shortener_redirect(request):
    token = request.query.get("token")
    if not token or _bot_client is None:
        return web.json_response({"error": "bad request"}, status=400)
    await _bot_client.mongodb.masked_links.update_one(
        {"_id": token}, {"$set": {"shortener_redirected_at": datetime.now()}}
    )
    return web.json_response({"ok": True})


async def verify_token(request):
    token = request.query.get("token")
    if not token or _bot_client is None:
        return web.json_response({"error": "bad request"}, status=400)

    link_data = await _bot_client.mongodb.masked_links.find_one({"_id": token})
    if not link_data:
        return web.json_response({"status": "INVALID", "reason": "Token not found"})
    if datetime.now() > link_data.get("expires_at", datetime.now()):
        return web.json_response({"status": "EXPIRED", "reason": "Link expired"})
    if link_data.get("used", False):
        return web.json_response({"status": "REUSED", "reason": "Token already used"})
    if link_data.get("bypass_attempted", False):
        return web.json_response({
            "status": "BYPASS",
            "reason": link_data.get("bypass_reason", "Bypass detected"),
        })

    # ══════════════════════════════════════════════════════
    #  If global verification is disabled, tell the frontend
    #  to skip gateway + shortener → go straight to the bot.
    # ══════════════════════════════════════════════════════
    verification_enabled = await _bot_client.mongodb.get_bot_config(
        'token_verification_enabled', True
    )
    if not verification_enabled:
        return web.json_response({
            "status": "DISABLED",
            "reason": "Verification disabled",
            "bot_username": _bot_client.username,
            "file_token": link_data.get("original_base64"),
        })

    return web.json_response({"status": "OK"})


def setup_routes(aiohttp_app, bot_client):
    global _bot_client
    _bot_client = bot_client
    aiohttp_app.router.add_get("/api/mark_gateway_opened", mark_gateway_opened)
    aiohttp_app.router.add_get("/api/mark_shortener_redirect", mark_shortener_redirect)
    aiohttp_app.router.add_get("/api/verify_token", verify_token)
