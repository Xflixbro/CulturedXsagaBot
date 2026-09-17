# Made by @Awakeners_Bots
# antibypass.py — Link Masking & Anti-Bypass System (FULLY INTEGRATED)

import secrets
import base64
from datetime import datetime, timedelta
from pyrogram import Client

# =====================================================
#  CONFIG
# =====================================================
GATEWAY_BASE_URL = "https://oggyflix2.vercel.app"
ACCESS_TOKEN_EXPIRY_MINUTES = 10


# ══════════════════════════════════════════════════════
#  SETTINGS RESOLVERS — MongoDB is the single source
# ══════════════════════════════════════════════════════

async def _get_config(client, key: str, default):
    """Safely read a bot config value from MongoDB."""
    try:
        return await client.mongodb.get_bot_config(key, default)
    except Exception:
        return default


async def is_global_verification_enabled(client) -> bool:
    """Global Verification System toggle (settings.py → global_token_toggle)."""
    return await _get_config(client, 'token_verification_enabled', True)


async def is_bypass_check_enabled(client) -> bool:
    """Anti-bypass timer check toggle (settings.py → anti_bypass_settings)."""
    return await _get_config(client, 'bypass_check_enabled', True)


async def get_bypass_timer(client) -> int:
    """Minimum seconds a user must spend on the shortener (settings.py)."""
    return int(await _get_config(client, 'bypass_timer', 60))


def is_masking_enabled() -> bool:
    """Masking is enabled when a valid gateway URL is configured."""
    url = (GATEWAY_BASE_URL or "").strip()
    return url.startswith("http://") or url.startswith("https://")


# ══════════════════════════════════════════════════════
#  TOKEN GENERATORS
# ══════════════════════════════════════════════════════

def generate_hex_token() -> str:
    return secrets.token_hex(8)


def generate_access_token() -> str:
    # hex only → never contains underscores, safe for split("_", 2)
    return secrets.token_hex(16)


# ══════════════════════════════════════════════════════
#  CREATE MASKED LINK  (stores bot_link for direct redirect)
# ══════════════════════════════════════════════════════

async def create_masked_link(
    client: Client,
    user_id: int,
    original_base64: str,
    shortener_url: str,
    bot_link: str = None,
    is_batch: bool = False,
    restricted: bool = False,
) -> dict:
    """Create a masked gateway link record in MongoDB."""
    if not is_masking_enabled():
        return {
            "masked_url": shortener_url,
            "hex_token": None,
            "access_token": None,
            "expires_at": None,
            "masked": False,
        }

    hex_token = generate_hex_token()
    access_token = generate_access_token()
    now = datetime.now()
    expires_at = now + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)

    await client.mongodb.masked_links.insert_one({
        "_id": hex_token,
        "user_id": user_id,
        "original_base64": original_base64,
        "shortener_url": shortener_url,
        "bot_link": bot_link,
        "access_token": access_token,
        "is_batch": is_batch,
        "restricted": restricted,
        "created_at": now,
        "expires_at": expires_at,
        "used": False,
        "gateway_opened_at": None,
        "shortener_redirected_at": None,
        "access_granted_at": None,
        "bypass_attempted": False,
        "bypass_reason": None,
    })

    url_b64 = base64.urlsafe_b64encode(shortener_url.encode()).decode().rstrip("=")
    masked_url = f"{GATEWAY_BASE_URL.rstrip('/')}/access/{hex_token}?url={url_b64}"

    return {
        "masked_url": masked_url,
        "hex_token": hex_token,
        "access_token": access_token,
        "expires_at": expires_at,
        "masked": True,
    }


# ══════════════════════════════════════════════════════
#  SEND MASKED LINK  (used by start.py when generating links)
# ══════════════════════════════════════════════════════

async def send_masked_link(
    client: Client,
    message,
    file_token: str,
    is_batch: bool = False,
    restricted: bool = False,
) -> dict:
    """Build the full masked link flow for a file token."""
    from helper.helper_func import shorten_url

    # ── Masking disabled → send plain shortener link ──
    if not is_masking_enabled():
        bot_link = f"https://t.me/{client.username}?start={file_token}"
        shortener_url = await shorten_url(bot_link)
        return {
            "masked_url": shortener_url,
            "shortener_url": shortener_url,
            "bot_link": bot_link,
            "hex_token": None,
            "masked": False,
        }

    # 1. generate tokens
    hex_token = generate_hex_token()
    access_token = generate_access_token()
    now = datetime.now()
    expires_at = now + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)

    # 2. build deep link with 3 parts: FILE_HEX_ACCESS
    bot_link = (
        f"https://t.me/{client.username}"
        f"?start={file_token}_{hex_token}_{access_token}"
    )

    # 3. shorten it
    shortener_url = await shorten_url(bot_link)

    # 4. store record with bot_link for direct redirect
    await client.mongodb.masked_links.insert_one({
        "_id": hex_token,
        "user_id": message.from_user.id,
        "original_base64": file_token,
        "shortener_url": shortener_url,
        "bot_link": bot_link,
        "access_token": access_token,
        "is_batch": is_batch,
        "restricted": restricted,
        "created_at": now,
        "expires_at": expires_at,
        "used": False,
        "gateway_opened_at": None,
        "shortener_redirected_at": None,
        "access_granted_at": None,
        "bypass_attempted": False,
        "bypass_reason": None,
    })

    # 5. build gateway URL with the real shortener URL
    url_b64 = base64.urlsafe_b64encode(shortener_url.encode()).decode().rstrip("=")
    masked_url = f"{GATEWAY_BASE_URL.rstrip('/')}/access/{hex_token}?url={url_b64}"

    return {
        "masked_url": masked_url,
        "shortener_url": shortener_url,
        "bot_link": bot_link,
        "hex_token": hex_token,
        "masked": True,
    }


# ══════════════════════════════════════════════════════
#  VERIFY ACCESS  (called from start.py when user returns)
# ══════════════════════════════════════════════════════

async def verify_access(client, user_id, hex_token, access_token) -> dict:
    """
    Verify a masked-link return path.
    Backward compatible with old records (missing bot_link).
    """
    if not is_masking_enabled():
        return {"status": "DISABLED", "reason": "Masking off", "original_base64": None}

    link_data = await client.mongodb.masked_links.find_one({"_id": hex_token})
    if not link_data:
        return {"status": "INVALID", "reason": "Token not found", "original_base64": None}

    # ── User match (None user_id = admin / channel post) ──
    stored_user = link_data.get("user_id")
    if stored_user is not None and stored_user != user_id:
        return {"status": "INVALID", "reason": "Token mismatch", "original_base64": None}

    # ── Expiry ──
    if datetime.now() > link_data.get("expires_at", datetime.now()):
        await client.mongodb.masked_links.update_one(
            {"_id": hex_token},
            {"$set": {"bypass_attempted": True, "bypass_reason": "EXPIRED"}},
        )
        return {"status": "EXPIRED", "reason": "Link expired", "original_base64": None}

    # ── Reuse ──
    if link_data.get("used", False):
        await client.mongodb.masked_links.update_one(
            {"_id": hex_token},
            {"$set": {"bypass_attempted": True, "bypass_reason": "TOKEN_REUSE"}},
        )
        return {"status": "REUSED", "reason": "Token already used", "original_base64": None}

    # ── Access token match ──
    if link_data.get("access_token") != access_token:
        await client.mongodb.masked_links.update_one(
            {"_id": hex_token},
            {"$set": {"bypass_attempted": True, "bypass_reason": "INVALID_ACCESS_TOKEN"}},
        )
        return {"status": "INVALID", "reason": "Access token mismatch", "original_base64": None}

    # ── Timer check (only when enabled in settings) ──
    bypass_enabled = await is_bypass_check_enabled(client)
    if bypass_enabled:
        gateway_opened = link_data.get("gateway_opened_at")
        shortener_redirected = link_data.get("shortener_redirected_at")
        if gateway_opened and shortener_redirected:
            elapsed = (shortener_redirected - gateway_opened).total_seconds()
            min_time = await get_bypass_timer(client)
            if elapsed < min_time:
                await client.mongodb.masked_links.update_one(
                    {"_id": hex_token},
                    {"$set": {"bypass_attempted": True, "bypass_reason": "TOO_FAST"}},
                )
                try:
                    await client.mongodb.log_bypass_attempt(user_id, "MASKED_LINK_TOO_FAST")
                except Exception:
                    pass
                return {
                    "status": "BYPASS",
                    "reason": f"Solved too fast ({elapsed:.0f}s < {min_time}s)",
                    "original_base64": None,
                }

    # ── Success ──
    await client.mongodb.masked_links.update_one(
        {"_id": hex_token},
        {"$set": {"used": True, "access_granted_at": datetime.now()}},
    )

    return {
        "status": "OK",
        "reason": "Access granted",
        "original_base64": link_data.get("original_base64"),
        "is_batch": link_data.get("is_batch", False),
        "restricted": link_data.get("restricted", False),
        "bot_link": link_data.get("bot_link"),
    }
