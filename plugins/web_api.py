# Made by @Awakeners_Bots
# web_api.py — API endpoints for Vercel gateway

from aiohttp import web
from datetime import datetime

_bot_client = None


async def _get_config(key: str, default):
    try:
        return await _bot_client.mongodb.get_bot_config(key, default)
    except Exception:
        return default


# ══════════════════════════════════════════════════════
#  TOKEN VALIDATION  (called on gateway page load)
# ══════════════════════════════════════════════════════

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

    # ── Determine gateway behaviour from settings ──
    verification_enabled = await _get_config('token_verification_enabled', True)
    bypass_check_enabled = await _get_config('bypass_check_enabled', True)
    bypass_timer = int(await _get_config('bypass_timer', 60))
    shortener_url = link_data.get("shortener_url")
    bot_link = link_data.get("bot_link") or shortener_url  # fallback for old records

    return web.json_response({
        "status": "OK",
        "verification_enabled": verification_enabled,
        "bypass_check_enabled": bypass_check_enabled,
        "bypass_timer": bypass_timer,
        "shortener_url": shortener_url,
        "bot_link": bot_link,
    })


# ══════════════════════════════════════════════════════
#  TIMESTAMP MARKERS
# ══════════════════════════════════════════════════════

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


async def mark_direct_access(request):
    """When verification is disabled, mark gateway + redirect in one call."""
    token = request.query.get("token")
    if not token or _bot_client is None:
        return web.json_response({"error": "bad request"}, status=400)
    now = datetime.now()
    await _bot_client.mongodb.masked_links.update_one(
        {"_id": token},
        {"$set": {"gateway_opened_at": now, "shortener_redirected_at": now}},
    )
    return web.json_response({"ok": True})


# ══════════════════════════════════════════════════════
#  CORS  (so Vercel can call the API)
# ══════════════════════════════════════════════════════

@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response()
    else:
        response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def setup_routes(aiohttp_app, bot_client):
    global _bot_client
    _bot_client = bot_client
    aiohttp_app.middlewares.append(cors_middleware)
    aiohttp_app.router.add_get("/api/verify_token", verify_token)
    aiohttp_app.router.add_get("/api/mark_gateway_opened", mark_gateway_opened)
    aiohttp_app.router.add_get("/api/mark_shortener_redirect", mark_shortener_redirect)
    aiohttp_app.router.add_get("/api/mark_direct_access", mark_direct_access)
