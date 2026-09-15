# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots
#
# Supreme Gateway — Session signing, validation, and URL wrapping.
# This module is destination-agnostic: it wraps ANY valid HTTPS URL
# (AroLinks shortener, other shorteners, raw t.me links, permanent links, etc.)

import hmac
import hashlib
import base64
import json
import time
from urllib.parse import urlparse
from config import SUPREME_SECRET_KEY, SUPREME_SESSION_TTL


# ---------------------------------------------------------
#  BASE64 URL-SAFE HELPERS
# ---------------------------------------------------------
def _base64_url_encode(data: str) -> str:
    """URL-safe base64 encoding without padding."""
    return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")


def _base64_url_decode(data: str) -> str:
    """URL-safe base64 decoding with padding restoration."""
    data += "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data.encode()).decode()


# ---------------------------------------------------------
#  DESTINATION SAFETY CHECK
# ---------------------------------------------------------
def _is_safe_destination(url: str) -> bool:
    """
    Only allow http:// and https:// destinations.
    Rejects javascript:, data:, file:, vbscript:, etc.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in ("https", "http"):
            return False
        if not parsed.netloc:
            return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------
#  SESSION GENERATION & VERIFICATION
# ---------------------------------------------------------
def generate_supreme_session(destination_b64: str) -> str:
    """
    Returns: base64(payload).signature
    payload = {"url": <base64 dest>, "exp": <unix ts>, "iat": <unix ts>}
    """
    payload = {
        "url": destination_b64,
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
    """Verify signature + expiry. Returns payload dict or None."""
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

        payload = json.loads(_base64_url_decode(payload_b64))

        if time.time() > payload.get("exp", 0):
            return None

        return payload
    except Exception:
        return None


# ---------------------------------------------------------
#  UNIVERSAL SUPREME URL WRAPPER
# ---------------------------------------------------------
def generate_supreme_url(destination_url: str) -> str:
    """
    Wrap ANY valid HTTPS destination in the Supreme Gateway URL.
    Fails open (returns original) if Supreme is disabled or dest is unsafe.
    """
    from config import SUPREME_ENABLED, SUPREME_BASE_URL, SUPREME_GATEWAY_PATH

    if not SUPREME_ENABLED:
        return destination_url

    if not _is_safe_destination(destination_url):
        return destination_url

    base64_dest = _base64_url_encode(destination_url)
    session_id = generate_supreme_session(base64_dest)

    return f"{SUPREME_BASE_URL}{SUPREME_GATEWAY_PATH}/{session_id}?url={base64_dest}"
