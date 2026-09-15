# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

import hmac
import hashlib
import base64
import json
import time
from urllib.parse import urlparse
from config import SUPREME_SECRET_KEY, SUPREME_SESSION_TTL


def _base64_url_encode(data: str) -> str:
    """URL-safe base64 encoding without padding."""
    return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")


def _base64_url_decode(data: str) -> str:
    """URL-safe base64 decoding with padding restoration."""
    data += "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data.encode()).decode()


def _is_safe_destination(url: str) -> bool:
    """
    Validate that the destination URL is safe to redirect to.
    Only allows https:// (and optionally http://) schemes.
    Rejects javascript:, data:, file:, vbscript:, etc.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        # Only allow http and https. Prefer https.
        if parsed.scheme not in ("https", "http"):
            return False
        # Must have a network location (domain)
        if not parsed.netloc:
            return False
        return True
    except Exception:
        return False


def generate_supreme_session(destination_url: str) -> str:
    """
    Generates a signed session token.
    Payload contains the destination URL and expiration timestamp.
    Format: base64(payload).signature
    """
    payload = {
        "url": destination_url,
        "exp": int(time.time()) + SUPREME_SESSION_TTL,
        "iat": int(time.time())
    }
    payload_b64 = _base64_url_encode(json.dumps(payload, separators=(',', ':')))

    signature = hmac.new(
        SUPREME_SECRET_KEY.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}.{signature}"


def verify_supreme_session(token: str) -> dict | None:
    """
    Verifies the session token signature and expiration.
    Returns the payload dictionary if valid, None otherwise.
    """
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None

        payload_b64, signature = parts

        expected_sig = hmac.new(
            SUPREME_SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            return None

        payload_json = _base64_url_decode(payload_b64)
        payload = json.loads(payload_json)

        if time.time() > payload.get("exp", 0):
            return None

        return payload
    except Exception:
        return None


def generate_supreme_url(destination_url: str) -> str:
    """
    Universal Supreme Gateway wrapper.
    Accepts ANY valid HTTPS destination (AroLinks, any shortener,
    direct t.me link, permanent website link, etc.) and wraps it
    in the Supreme Gateway URL.

    If SUPREME_ENABLED is False, returns the destination unchanged.
    If the destination is invalid/unsafe, returns it unchanged
    (fail-open so we never break a working link).
    """
    from config import SUPREME_ENABLED, SUPREME_BASE_URL, SUPREME_GATEWAY_PATH

    if not SUPREME_ENABLED:
        return destination_url

    # Safety: never wrap a non-http(s) URL
    if not _is_safe_destination(destination_url):
        return destination_url

    base64_dest = _base64_url_encode(destination_url)
    session_id = generate_supreme_session(base64_dest)

    return f"{SUPREME_BASE_URL}{SUPREME_GATEWAY_PATH}/{session_id}?url={base64_dest}"
