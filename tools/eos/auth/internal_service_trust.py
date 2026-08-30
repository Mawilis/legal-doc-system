"""WILSY OS Internal Service Trust Verification Authority

TITLE: WILSY OS Internal Service Trust Verification Authority
VERSION: v1.0.0-WILSY-INTERNAL-SERVICE-TRUST
AUTHORITY: Internal service authentication only.
EPITOME: Verifies authenticated Node-to-EOS requests without owning user authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/internal_service_trust.py
COLLABORATION / OWNERSHIP: EOS Python authority; Node transport consumes bounded results.
CERTIFICATION/UPDATE DATE: 2026-08-30
CHANGELOG: v1.0.0-WILSY-INTERNAL-SERVICE-TRUST - deterministic HMAC trust verifier.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Fail closed; no user or secret material is returned.
TENANT BOUNDARY: No tenant membership authority.
AUTHORITY BOUNDARY: Internal service authentication only; no user authorization.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import time
from dataclasses import dataclass
from typing import Mapping, Protocol

VERSION = "v1.0.0-WILSY-INTERNAL-SERVICE-TRUST"
PROTOCOL_VERSION = "v1"
MAX_CLOCK_SKEW_SECONDS = 30
NONCE_ACCEPTANCE_SECONDS = 90
_HEX128 = re.compile(r"^[0-9a-f]{128}$")
_NONCE = re.compile(r"^[0-9a-f]{32}$")
_SIG = re.compile(r"^[0-9a-f]{64}$")


class ReplayStore(Protocol):
    def consume_once(self, *, service_id: str, key_id: str, nonce: str, expires_at: int) -> bool: ...


class InternalServiceTrustError(Exception):
    """Bounded base error; never contains secrets, signatures, or credentials."""


class InternalServiceTrustConfigurationError(InternalServiceTrustError): pass
class InternalServiceTrustMalformedRequestError(InternalServiceTrustError): pass
class InternalServiceTrustAuthenticationError(InternalServiceTrustError): pass
class InternalServiceTrustReplayError(InternalServiceTrustError): pass
class InternalServiceTrustFreshnessError(InternalServiceTrustError): pass


@dataclass(frozen=True)
class TrustResult:
    service_id: str
    audience: str
    key_id: str
    correlation_id: str
    verified_at: int
    protocol_version: str = PROTOCOL_VERSION


def body_sha3_512(body: bytes) -> str:
    """Hash exact transmitted bytes, including the zero-byte empty body."""
    return hashlib.sha3_512(body).hexdigest()


def canonical_request(*, version: str, service_id: str, audience: str, method: str,
                      path: str, timestamp: str, nonce: str, body_sha3_512_value: str,
                      correlation_id: str) -> bytes:
    fields = (version, service_id, audience, method, path, timestamp, nonce,
              body_sha3_512_value, correlation_id)
    if any("\r" in value or "\n" in value for value in fields):
        raise InternalServiceTrustMalformedRequestError("newline in trust request")
    if not all(isinstance(value, str) and 1 <= len(value) <= 256 for value in fields):
        raise InternalServiceTrustMalformedRequestError("invalid trust field")
    if version != PROTOCOL_VERSION or method != method.upper() or not method.isascii():
        raise InternalServiceTrustMalformedRequestError("invalid protocol or method")
    if not path.startswith("/") or path.startswith("//") or "://" in path or len(path) > 2048:
        raise InternalServiceTrustMalformedRequestError("invalid origin-form path")
    if not timestamp.isdecimal() or (len(timestamp) > 1 and timestamp.startswith("0")):
        raise InternalServiceTrustMalformedRequestError("invalid timestamp")
    if not _NONCE.fullmatch(nonce) or not _HEX128.fullmatch(body_sha3_512_value):
        raise InternalServiceTrustMalformedRequestError("invalid digest or nonce")
    return "\n".join(fields).encode("utf-8")


def verify_internal_service_request(*, request: Mapping[str, str], body: bytes,
                                    keys: Mapping[str, tuple[str, str]],
                                    replay_store: ReplayStore | None, now: int | None = None) -> TrustResult:
    """Verify only internal service trust; user authority is intentionally excluded."""
    required = ("version", "service_id", "audience", "key_id", "method", "path", "timestamp",
                "nonce", "body_sha3_512", "correlation_id", "signature")
    if replay_store is None:
        raise InternalServiceTrustConfigurationError("replay store required")
    if any(name not in request for name in required):
        raise InternalServiceTrustMalformedRequestError("missing trust field")
    version, service_id, audience, key_id = (request[x] for x in ("version", "service_id", "audience", "key_id"))
    if key_id not in keys:
        raise InternalServiceTrustConfigurationError("unknown trust key")
    allowed_service, secret = keys[key_id]
    if not secret or service_id != allowed_service:
        raise InternalServiceTrustAuthenticationError("untrusted service")
    expected_body = body_sha3_512(body)
    if not hmac.compare_digest(expected_body, request["body_sha3_512"]):
        raise InternalServiceTrustAuthenticationError("body digest mismatch")
    canonical = canonical_request(version=version, service_id=service_id, audience=audience, method=request["method"],
                                  path=request["path"], timestamp=request["timestamp"], nonce=request["nonce"],
                                  body_sha3_512_value=request["body_sha3_512"], correlation_id=request["correlation_id"])
    if not _SIG.fullmatch(request["signature"]):
        raise InternalServiceTrustMalformedRequestError("invalid signature")
    expected = hmac.new(secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, request["signature"]):
        raise InternalServiceTrustAuthenticationError("signature mismatch")
    current = int(time.time()) if now is None else now
    stamp = int(request["timestamp"])
    if abs(current - stamp) > MAX_CLOCK_SKEW_SECONDS:
        raise InternalServiceTrustFreshnessError("timestamp outside acceptance window")
    if not replay_store.consume_once(service_id=service_id, key_id=key_id, nonce=request["nonce"],
                                     expires_at=stamp + NONCE_ACCEPTANCE_SECONDS):
        raise InternalServiceTrustReplayError("replayed nonce")
    return TrustResult(service_id, audience, key_id, request["correlation_id"], current)


# ARTIFACT: internal_service_trust.py
# VERSION: v1.0.0-WILSY-INTERNAL-SERVICE-TRUST
# AUTHORITY BOUNDARY: Internal service trust verification only.
# TENANT POSTURE: No tenant membership authority.
# FAIL-CLOSED POSTURE: Missing, malformed, stale, replayed, or untrusted requests deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
