"""TITLE: WILSY OS Signed Bootstrap Creation Authorization.
VERSION: v1.0.0-P4-R4-D11-R5-SIGNED-CREATION-AUTHORIZATION
AUTHORITY: Ed25519-authenticated authorization for one exact bootstrap creation.
EPITOME: Authenticates complete claims before any claim drives trust decisions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_bootstrap_creation_authorization.py
COLLABORATION: D11 creation trust and issuance service.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes signature-first claim authorization.
COMPLIANCE / SECURITY: Public-key verification; no private keys or secrets.
TENANT / ROLE / ACTIVATION / BREAK-GLASS / FINANCIAL AUTHORITY: NONE.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Final
import base64, json
from cryptography.exceptions import InvalidSignature
from tools.eos.auth.system_permission_bootstrap_creation_trust import OPERATION, SCOPE, SystemPermissionBootstrapCreationTrustError, SystemPermissionBootstrapCreationTrustRoot, SystemPermissionBootstrapCreationTrustedKey

VERSION: Final[str] = "v1.0.0-P4-R4-D11-R5-SIGNED-CREATION-AUTHORIZATION"
MAXIMUM_LIFETIME: Final[timedelta] = timedelta(minutes=30)
_PURPOSES: Final[frozenset[str]] = frozenset({"SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY", "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"})
_TOKEN = object()

class SystemPermissionBootstrapCreationAuthorizationError(ValueError):
    """Fail-closed signed authorization validation or verification failure."""

def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "*" in value: raise SystemPermissionBootstrapCreationAuthorizationError(name + "_INVALID")
    return value
def _time(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None: raise SystemPermissionBootstrapCreationAuthorizationError(name + "_INVALID")
    return value.astimezone(timezone.utc)
def _decode_signature(value: str) -> bytes:
    try: raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except Exception as error: raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_SIGNATURE_INVALID") from error
    if len(raw) != 64 or base64.urlsafe_b64encode(raw).rstrip(b"=").decode() != value: raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_SIGNATURE_INVALID")
    return raw

@dataclass(frozen=True, slots=True)
class SystemPermissionBootstrapCreationAuthorization:
    """Immutable unverified signed envelope; construction is not authentication."""
    operation: str; scope: str; creator_principal_id: str; target_principal_id: str
    bootstrap_id: str; bootstrap_purpose: str; evidence_reference: str
    key_id: str; trust_fingerprint: str; issued_at: datetime; expires_at: datetime
    nonce: str; idempotency_key: str; signature_base64url: str
    def __post_init__(self) -> None:
        for name in ("operation", "scope", "creator_principal_id", "target_principal_id", "bootstrap_id", "evidence_reference", "key_id", "trust_fingerprint", "nonce", "idempotency_key", "signature_base64url"): object.__setattr__(self, name, _text(name.upper(), getattr(self, name)))
        if self.operation != OPERATION or self.scope != SCOPE: raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_CONTRACT_INVALID")
        purpose = _text("BOOTSTRAP_PURPOSE", self.bootstrap_purpose)
        if purpose not in _PURPOSES: raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_PURPOSE_NOT_ALLOWED")
        issued, expires = _time("ISSUED_AT", self.issued_at), _time("EXPIRES_AT", self.expires_at)
        if expires <= issued or expires - issued > MAXIMUM_LIFETIME: raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_LIFETIME_INVALID")
        _decode_signature(self.signature_base64url); object.__setattr__(self, "issued_at", issued); object.__setattr__(self, "expires_at", expires)
    def signed_payload(self) -> bytes:
        """Return the complete deterministic payload authenticated by Ed25519."""
        payload = {name: (getattr(self, name).isoformat() if name in {"issued_at", "expires_at"} else getattr(self, name)) for name in ("operation", "scope", "creator_principal_id", "target_principal_id", "bootstrap_id", "bootstrap_purpose", "evidence_reference", "key_id", "trust_fingerprint", "issued_at", "expires_at", "nonce", "idempotency_key")}
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

@dataclass(frozen=True, slots=True, init=False)
class VerifiedSystemPermissionBootstrapCreationAuthorization:
    """Unforgeable in-process proof returned only after complete verification."""
    authorization: SystemPermissionBootstrapCreationAuthorization
    trusted_key: SystemPermissionBootstrapCreationTrustedKey
    verified_at: datetime
    def __init__(self, authorization: SystemPermissionBootstrapCreationAuthorization, trusted_key: SystemPermissionBootstrapCreationTrustedKey, verified_at: datetime, *, _token: object = None) -> None:
        if _token is not _TOKEN: raise TypeError("verified authorization requires verifier")
        object.__setattr__(self, "authorization", authorization); object.__setattr__(self, "trusted_key", trusted_key); object.__setattr__(self, "verified_at", verified_at)

def verify_system_permission_bootstrap_creation_authorization(authorization: SystemPermissionBootstrapCreationAuthorization, trust_root: SystemPermissionBootstrapCreationTrustRoot, *, now: datetime) -> VerifiedSystemPermissionBootstrapCreationAuthorization:
    """Authenticate payload before evaluating any signed authorization claim."""
    if not isinstance(authorization, SystemPermissionBootstrapCreationAuthorization) or not isinstance(trust_root, SystemPermissionBootstrapCreationTrustRoot): raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_INPUT_INVALID")
    observed = _time("NOW", now)
    try: key = trust_root.resolve(authorization.key_id)
    except SystemPermissionBootstrapCreationTrustError as error: raise SystemPermissionBootstrapCreationAuthorizationError(str(error)) from error
    if key.trust_fingerprint != authorization.trust_fingerprint: raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_TRUST_FINGERPRINT_INVALID")
    try: key.public_key().verify(_decode_signature(authorization.signature_base64url), authorization.signed_payload())
    except (InvalidSignature, ValueError, TypeError) as error: raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_SIGNATURE_INVALID") from error
    if not key.can_issue(creator_principal_id=authorization.creator_principal_id, operation=authorization.operation, scope=authorization.scope, at=authorization.issued_at): raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_TRUST_NOT_CURRENT_AT_ISSUANCE")
    if not key.can_issue(creator_principal_id=authorization.creator_principal_id, operation=authorization.operation, scope=authorization.scope, at=observed): raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_TRUST_NOT_CURRENT")
    if not (authorization.issued_at <= observed < authorization.expires_at): raise SystemPermissionBootstrapCreationAuthorizationError("BOOTSTRAP_CREATION_AUTHORIZATION_NOT_CURRENT")
    return VerifiedSystemPermissionBootstrapCreationAuthorization(authorization, key, observed, _token=_TOKEN)

__all__ = ["VERSION", "MAXIMUM_LIFETIME", "SystemPermissionBootstrapCreationAuthorizationError", "SystemPermissionBootstrapCreationAuthorization", "VerifiedSystemPermissionBootstrapCreationAuthorization", "verify_system_permission_bootstrap_creation_authorization"]
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: system_permission_bootstrap_creation_authorization.py
# VERSION: v1.0.0-P4-R4-D11-R5-SIGNED-CREATION-AUTHORIZATION
# VERIFICATION ORDER: KEY -> FINGERPRINT -> SIGNATURE -> CLAIMS/CURRENTNESS
# ACTIVATION / BREAK GLASS / FINANCE: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
