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

VERSION: v1.1.0-L7D-SECRET-FAIL-CLOSED
AUTHORITY: Credential signing and verification only; no identity or tenant authority.
TENANT BOUNDARY: Claims are untrusted projections until downstream durable admission.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive financial execution authority.
CHANGELOG: v1.1.0-L7D-SECRET-FAIL-CLOSED removes the hard-coded signing-key fallback;
            missing configuration now fails closed.

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

VERSION = "v1.1.0-L7D-SECRET-FAIL-CLOSED"


def _signing_secret() -> str:
    """Resolve the signing key from governed configuration, never a source fallback."""
    secret = os.getenv("WILSY_JWT_SECRET", "")
    if not secret.strip():
        raise RuntimeError("WILSY_JWT_SECRET is not configured")
    return secret


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
        _signing_secret().encode("utf-8"),
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
            _signing_secret().encode("utf-8"),
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


# ARTIFACT: jwt_provider.py
# VERSION: v1.1.0-L7D-SECRET-FAIL-CLOSED
# AUTHORITY BOUNDARY: credential signing and verification only.
# TENANT POSTURE: token claims are untrusted context until durable admission.
# FAIL-CLOSED POSTURE: absent or malformed signing configuration cannot mint or validate tokens.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
