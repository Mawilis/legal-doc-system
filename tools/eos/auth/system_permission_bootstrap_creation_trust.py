"""TITLE: WILSY OS System Permission Bootstrap Creation Trust.
VERSION: v1.0.0-P4-R4-D11-R5-CREATION-TRUST
AUTHORITY: Source-owned Ed25519 public trust metadata for bootstrap creation only.
EPITOME: Binds exact creator identities to one closed bootstrap-create operation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_bootstrap_creation_trust.py
COLLABORATION / OWNERSHIP: D11 signed creation authorization verifier only.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes immutable trust records and roots.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY: Public keys only; private signing material is forbidden.
TENANT / AUTHORITY / FINANCIAL BOUNDARY: SYSTEM trust metadata only; no role,
tenant, founder, activation, break-glass, permission grant, or finance.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import base64
import json
import re
from typing import Final

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

VERSION: Final[str] = "v1.0.0-P4-R4-D11-R5-CREATION-TRUST"
ALGORITHM: Final[str] = "Ed25519"
SCOPE: Final[str] = "SYSTEM"
OPERATION: Final[str] = "CREATE_SYSTEM_PERMISSION_BOOTSTRAP_AUTHORITY"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class SystemPermissionBootstrapCreationTrustError(ValueError):
    """Reject malformed, unknown, or non-current creation trust."""


class SystemPermissionBootstrapCreationTrustStatus(StrEnum):
    """Closed public-key lifecycle vocabulary."""
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "*" in value:
        raise SystemPermissionBootstrapCreationTrustError(name + "_INVALID")
    return value


def _time(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise SystemPermissionBootstrapCreationTrustError("TRUST_VALIDITY_INVALID")
    return value.astimezone(timezone.utc)


def _decode(value: str) -> bytes:
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        Ed25519PublicKey.from_public_bytes(raw)
    except (ValueError, TypeError) as error:
        raise SystemPermissionBootstrapCreationTrustError("PUBLIC_KEY_INVALID") from error
    if len(raw) != 32 or base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") != value:
        raise SystemPermissionBootstrapCreationTrustError("PUBLIC_KEY_INVALID")
    return raw


@dataclass(frozen=True, slots=True)
class SystemPermissionBootstrapCreationTrustedKey:
    """Immutable public trust record; never a private signing surface."""
    key_id: str
    creator_principal_id: str
    public_key_base64url: str
    valid_from: datetime
    valid_until: datetime
    status: SystemPermissionBootstrapCreationTrustStatus
    revision: int
    provenance: str
    algorithm: str
    scope: str
    operation: str
    trust_fingerprint: str

    def __post_init__(self) -> None:
        raw = _decode(_text("PUBLIC_KEY", self.public_key_base64url))
        creator = _text("CREATOR_PRINCIPAL_ID", self.creator_principal_id)
        provenance = _text("PROVENANCE", self.provenance)
        start, end = _time(self.valid_from), _time(self.valid_until)
        if start >= end or self.algorithm != ALGORITHM or self.scope != SCOPE or self.operation != OPERATION:
            raise SystemPermissionBootstrapCreationTrustError("TRUST_CONTRACT_INVALID")
        if not isinstance(self.status, SystemPermissionBootstrapCreationTrustStatus) or isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise SystemPermissionBootstrapCreationTrustError("TRUST_LIFECYCLE_INVALID")
        expected_id = self.derive_key_id(self.public_key_base64url)
        if self.key_id != expected_id:
            raise SystemPermissionBootstrapCreationTrustError("KEY_ID_INVALID")
        payload = {"algorithm": ALGORITHM, "creator_principal_id": creator, "key_id": expected_id, "operation": OPERATION, "provenance": provenance, "public_key_base64url": self.public_key_base64url, "revision": self.revision, "scope": SCOPE, "status": self.status.value, "valid_from": start.isoformat(), "valid_until": end.isoformat()}
        expected_fp = sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if not isinstance(self.trust_fingerprint, str) or _HEX.fullmatch(self.trust_fingerprint) is None or self.trust_fingerprint != expected_fp:
            raise SystemPermissionBootstrapCreationTrustError("TRUST_FINGERPRINT_INVALID")
        object.__setattr__(self, "creator_principal_id", creator); object.__setattr__(self, "provenance", provenance); object.__setattr__(self, "valid_from", start); object.__setattr__(self, "valid_until", end)

    @staticmethod
    def derive_key_id(public_key_base64url: str) -> str:
        """Derive deterministic public-key identity without authority creation."""
        return "WILSYBOOTSTRAPKEY-" + sha3_512(_decode(public_key_base64url)).hexdigest()[:32]

    @classmethod
    def create(cls, *, creator_principal_id: str, public_key_base64url: str, valid_from: datetime, valid_until: datetime, status: SystemPermissionBootstrapCreationTrustStatus, revision: int, provenance: str) -> "SystemPermissionBootstrapCreationTrustedKey":
        """Create one source-owned public trust record from explicit metadata."""
        key_id = cls.derive_key_id(public_key_base64url); start, end = _time(valid_from), _time(valid_until)
        payload = {"algorithm": ALGORITHM, "creator_principal_id": _text("CREATOR_PRINCIPAL_ID", creator_principal_id), "key_id": key_id, "operation": OPERATION, "provenance": _text("PROVENANCE", provenance), "public_key_base64url": public_key_base64url, "revision": revision, "scope": SCOPE, "status": status.value, "valid_from": start.isoformat(), "valid_until": end.isoformat()}
        return cls(key_id, creator_principal_id, public_key_base64url, start, end, status, revision, provenance, ALGORITHM, SCOPE, OPERATION, sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest())

    def public_key(self) -> Ed25519PublicKey:
        """Return the verified public Ed25519 key."""
        return Ed25519PublicKey.from_public_bytes(_decode(self.public_key_base64url))

    def can_issue(self, *, creator_principal_id: str, operation: str, scope: str, at: datetime) -> bool:
        """Evaluate authenticated claims against current exact trust metadata."""
        moment = _time(at)
        return self.status is SystemPermissionBootstrapCreationTrustStatus.ACTIVE and creator_principal_id == self.creator_principal_id and operation == OPERATION and scope == SCOPE and self.valid_from <= moment < self.valid_until


@dataclass(frozen=True, slots=True)
class SystemPermissionBootstrapCreationTrustRoot:
    """Immutable membership of exact bootstrap-creation public keys."""
    trusted_keys: tuple[SystemPermissionBootstrapCreationTrustedKey, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.trusted_keys, tuple) or len({key.key_id for key in self.trusted_keys}) != len(self.trusted_keys):
            raise SystemPermissionBootstrapCreationTrustError("TRUST_ROOT_INVALID")

    def resolve(self, key_id: str) -> SystemPermissionBootstrapCreationTrustedKey:
        """Resolve one exact key or fail closed."""
        identity = _text("KEY_ID", key_id)
        for key in self.trusted_keys:
            if key.key_id == identity: return key
        raise SystemPermissionBootstrapCreationTrustError("BOOTSTRAP_CREATION_KEY_UNKNOWN")


__all__ = ["VERSION", "ALGORITHM", "SCOPE", "OPERATION", "SystemPermissionBootstrapCreationTrustError", "SystemPermissionBootstrapCreationTrustStatus", "SystemPermissionBootstrapCreationTrustedKey", "SystemPermissionBootstrapCreationTrustRoot"]
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: system_permission_bootstrap_creation_trust.py
# VERSION: v1.0.0-P4-R4-D11-R5-CREATION-TRUST
# PRIVATE KEY / TENANT / ROLE / ACTIVATION / BREAK GLASS / FINANCE: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
