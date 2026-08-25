"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG212 INSTITUTIONAL AUTHENTICATION - JWT PROVIDER
FILE: tools/eos/auth/jwt_provider.py
===============================================================================
Epitome:
    Cryptographic JSON Web Token encoding, decoding, and signature verification
    engine using robust HMAC-SHA256 sovereign signing keys.

Biblical Worth Billions:
    "In the mouth of two or three witnesses shall every word be established."
    — 2 Corinthians 13:1

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/auth/jwt_provider.py
===============================================================================
"""

import os
import hmac
import hashlib
import base64
import json
import time
from typing import Any, Dict, Optional

# Sovereign secret key (in production, loaded from secure hardware enclave or environment)
SOVEREIGN_JWT_SECRET = os.environ.get("WILSY_JWT_SECRET", "WILSY-OS-SOVEREIGN-BILLION-DOLLAR-SECRET-2026")


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding < 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("utf-8"))


def create_access_token(identity_data: Dict[str, Any], expires_in_seconds: int = 86400) -> str:
    """Encodes a cryptographically signed sovereign JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = dict(identity_data)
    now = int(time.time())
    payload["iat"] = now
    payload["exp"] = now + expires_in_seconds

    header_json = json.dumps(header, separators=(",", ":"), sort_keys=True)
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)

    encoded_header = _base64url_encode(header_json.encode("utf-8"))
    encoded_payload = _base64url_encode(payload_json.encode("utf-8"))

    signing_input = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        SOVEREIGN_JWT_SECRET.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256
    ).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies sovereign JWT signature and checks expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        encoded_header, encoded_payload, encoded_signature = parts
        signing_input = f"{encoded_header}.{encoded_payload}"

        expected_sig = hmac.new(
            SOVEREIGN_JWT_SECRET.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256
        ).digest()

        if not hmac.compare_digest(_base64url_encode(expected_sig), encoded_signature):
            return None

        payload_bytes = _base64url_decode(encoded_payload)
        payload = json.loads(payload_bytes.decode("utf-8"))

        if payload.get("exp", 0) < time.time():
            return None  # Token expired

        return payload
    except Exception:
        return None
