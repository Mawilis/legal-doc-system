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

VERSION: v1.3.0-R10C2F4-JWT-PURPOSE-CREDENTIAL-REVISION-CONTRACT
AUTHORITY: Credential signing and verification only; no identity or tenant authority.
TENANT BOUNDARY: Claims are untrusted projections until downstream durable admission.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive financial execution authority.
CHANGELOG: v1.3.0-R10C2F4-JWT-PURPOSE-CREDENTIAL-REVISION-CONTRACT adds the
            explicit ACCESS/PRE_AUTH purpose vocabulary and validates the
            optional credential_revision claim while retaining temporary
            acceptance of both claims' absence; durable revision comparison,
            reset invalidation, and caller migration remain outside this gate.
            v1.2.0-R1D-B0F-B4-R2-CANONICAL-TOKEN-CONTRACT made this module the
            sole access-token encoder/verifier and enforced the canonical
            identity/tenant projection; v1.1.0 removed the hard-coded fallback.
SECURITY POSTURE: Purpose and revision claims are structural JWT data only;
                 cryptographic validity does not grant durable authority.
PERSISTENCE POSTURE: This module performs no database or repository access.
LEGACY COMPATIBILITY: Missing purpose/revision claims remain structurally
                       accepted only while callers migrate to the explicit
                       contract; later authentication cutover owns enforcement.

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
from enum import Enum
from typing import Any, Dict, Optional

VERSION = "v1.3.0-R10C2F4-JWT-PURPOSE-CREDENTIAL-REVISION-CONTRACT"
ALGORITHM = "HS256"
REQUIRED_CLAIMS = ("identity_id", "tenant_id", "iat", "exp")
CREDENTIAL_REVISION_CLAIM = "credential_revision"
TOKEN_PURPOSE_CLAIM = "token_purpose"
CREDENTIAL_REVISION_MAX = 9_223_372_036_854_775_807


class TokenPurpose(str, Enum):
    """Canonical purpose values carried by migrated JWT issuers.

    Authority remains with downstream authentication.  This enum only limits
    the provider-owned serialized vocabulary and does not decide whether a
    token may access a protected route.
    """

    ACCESS = "ACCESS"
    PRE_AUTH = "PRE_AUTH"


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


def _purpose_value(value: Any) -> Optional[str]:
    """Return a canonical purpose value or ``None`` for an invalid value."""
    if isinstance(value, TokenPurpose):
        return value.value
    if isinstance(value, str):
        try:
            return TokenPurpose(value).value
        except ValueError:
            return None
    return None


def _valid_credential_revision(value: Any) -> bool:
    """Validate the bounded JSON integer representation of a revision."""
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and 0 <= value <= CREDENTIAL_REVISION_MAX
    )


def _validate_optional_claims(payload: Dict[str, Any]) -> bool:
    """Validate present purpose/revision claims without requiring either one."""
    if TOKEN_PURPOSE_CLAIM in payload:
        purpose = payload[TOKEN_PURPOSE_CLAIM]
        if _purpose_value(purpose) is None:
            return False
    if CREDENTIAL_REVISION_CLAIM in payload:
        if not _valid_credential_revision(payload[CREDENTIAL_REVISION_CLAIM]):
            return False
    return True


def _validate_identity_claims(payload: Dict[str, Any]) -> bool:
    """Validate canonical and optional claims without granting durable authority."""
    for name in ("identity_id", "tenant_id"):
        value = payload.get(name)
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            return False
    for name in ("roles", "permissions"):
        if name in payload:
            value = payload[name]
            if not isinstance(value, list) or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                return False
    for name in ("iat", "exp"):
        value = payload.get(name)
        if not isinstance(value, int) or isinstance(value, bool):
            return False
    return payload["exp"] > payload["iat"] and _validate_optional_claims(payload)


def create_access_token(
    identity_data: Dict[str, Any],
    expires_in_seconds: int = 86400,
    *,
    token_purpose: Optional[TokenPurpose | str] = None,
    credential_revision: Optional[int] = None,
) -> str:
    """Encode a signed token while preserving the legacy caller shape.

    ``token_purpose`` and ``credential_revision`` are optional, keyword-only
    structural claims.  Exact ACCESS/PRE_AUTH values and bounded integer
    revisions are serialized when supplied; omitted claims are not invented.
    This provider never reads durable state, hashes credentials, or decides
    route authority.  Missing claims remain temporarily compatible until the
    later issuer and authentication cutover.
    """
    if not isinstance(identity_data, dict):
        raise TypeError("identity_data must be a mapping")
    if not isinstance(expires_in_seconds, int) or isinstance(expires_in_seconds, bool) or expires_in_seconds <= 0:
        raise ValueError("expires_in_seconds must be a positive integer")
    payload = dict(identity_data)
    if token_purpose is not None:
        purpose = _purpose_value(token_purpose)
        if purpose is None:
            raise ValueError("token_purpose is invalid")
        payload[TOKEN_PURPOSE_CLAIM] = purpose
    if credential_revision is not None:
        if not _valid_credential_revision(credential_revision):
            raise ValueError("credential_revision is invalid")
        payload[CREDENTIAL_REVISION_CLAIM] = credential_revision
    now = int(time.time())
    payload["iat"] = now
    payload["exp"] = now + expires_in_seconds
    if not _validate_identity_claims(payload):
        raise ValueError("canonical access-token claims are invalid")
    header = {"alg": ALGORITHM, "typ": "JWT"}

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
        header = json.loads(_base64url_decode(encoded_header).decode("utf-8"))
        if not isinstance(header, dict) or header.get("alg") != ALGORITHM or header.get("typ") != "JWT":
            return None
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

        if not isinstance(payload, dict) or not _validate_identity_claims(payload):
            return None
        if payload["exp"] < time.time():
            return None  # Token expired

        return payload
    except Exception:
        return None


# ARTIFACT: jwt_provider.py
# VERSION: v1.3.0-R10C2F4-JWT-PURPOSE-CREDENTIAL-REVISION-CONTRACT
# AUTHORITY BOUNDARY: credential signing and verification only.
# TENANT POSTURE: token claims are untrusted context until durable admission.
# FAIL-CLOSED POSTURE: absent or malformed signing configuration cannot mint or validate tokens.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
