"""WILSY OS internal-service workload credential authority domain.

TITLE: Internal-Service Workload Credential Authority
VERSION: v1.0.0-P3-R3G-S6-A1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, secret-free binding of one internal service key generation to one canonical principal.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/internal_service_workload_credential_authority.py
COLLABORATION / OWNERSHIP: Internal-service HMAC verifier, credential registry, and workload-proof issuer.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P3-R3G-S6-A1 establishes platform-internal binding, generation, lifecycle, and SHA3-512 evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No HMAC secret, bearer token, signature, nonce, or caller-selected proof reference is represented.
TENANT BOUNDARY: Platform/internal only; this artifact grants no tenant authority.
AUTHORITY BOUNDARY: Credential-to-principal binding/currentness only; no role, permission, or privileged activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, Mapping, cast

VERSION: Final[str] = "v1.0.0-P3-R3G-S6-A1"
SCHEMA: Final[str] = "WILSY-INTERNAL-SERVICE-WORKLOAD-CREDENTIAL-AUTHORITY/V1"
PLATFORM_INTERNAL_SCOPE: Final[str] = "PLATFORM_INTERNAL"
_DIGEST = re.compile(r"^[0-9a-f]{128}$")


class InternalServiceWorkloadCredentialAuthorityError(ValueError):
    """Reject malformed, secret-bearing, or cryptographically corrupt authority facts."""


class WorkloadCredentialLifecycleStatus(StrEnum):
    """Closed credential-generation lifecycle; only CURRENT is admissible."""

    CURRENT = "CURRENT"
    REVOKED = "REVOKED"
    ROTATED = "ROTATED"
    INVALIDATED = "INVALIDATED"


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
        raise InternalServiceWorkloadCredentialAuthorityError(f"INVALID_{name.upper()}")
    return value


def _positive(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InternalServiceWorkloadCredentialAuthorityError(f"INVALID_{name.upper()}")
    return value


def _time(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise InternalServiceWorkloadCredentialAuthorityError(f"INVALID_{name.upper()}")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class InternalServiceWorkloadCredentialAuthority:
    """One immutable lifecycle snapshot for an exact service/key generation.

    It carries no secret and grants no tenant, role, permission, activation, or
    financial authority. The registry, not callers, decides currentness.
    """

    service_id: str
    key_id: str
    principal_id: str
    credential_scope: str
    credential_revision: int
    lifecycle_revision: int
    lifecycle_status: WorkloadCredentialLifecycleStatus
    status_changed_at: datetime
    previous_fingerprint: str | None = None
    authority_fingerprint: str | None = None

    def __post_init__(self) -> None:
        for name in ("service_id", "key_id", "principal_id"):
            object.__setattr__(self, name, _text(name, getattr(self, name)))
        if self.credential_scope != PLATFORM_INTERNAL_SCOPE:
            raise InternalServiceWorkloadCredentialAuthorityError("INVALID_CREDENTIAL_SCOPE")
        object.__setattr__(self, "credential_revision", _positive("credential_revision", self.credential_revision))
        object.__setattr__(self, "lifecycle_revision", _positive("lifecycle_revision", self.lifecycle_revision))
        if not isinstance(self.lifecycle_status, WorkloadCredentialLifecycleStatus):
            raise InternalServiceWorkloadCredentialAuthorityError("INVALID_LIFECYCLE_STATUS")
        object.__setattr__(self, "status_changed_at", _time("status_changed_at", self.status_changed_at))
        if self.lifecycle_revision == 1:
            if self.previous_fingerprint is not None or self.lifecycle_status is not WorkloadCredentialLifecycleStatus.CURRENT:
                raise InternalServiceWorkloadCredentialAuthorityError("INVALID_INITIAL_LIFECYCLE")
        elif not isinstance(self.previous_fingerprint, str) or _DIGEST.fullmatch(self.previous_fingerprint) is None:
            raise InternalServiceWorkloadCredentialAuthorityError("INVALID_PREVIOUS_FINGERPRINT")
        expected = self.compute_fingerprint()
        if self.authority_fingerprint is not None and (
            not isinstance(self.authority_fingerprint, str)
            or not hmac.compare_digest(self.authority_fingerprint, expected)
        ):
            raise InternalServiceWorkloadCredentialAuthorityError("AUTHORITY_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "authority_fingerprint", expected)

    def semantic_payload(self) -> dict[str, object]:
        """Return the deterministic, secret-free semantic payload."""
        return {
            "schema": SCHEMA,
            "service_id": self.service_id,
            "key_id": self.key_id,
            "principal_id": self.principal_id,
            "credential_scope": self.credential_scope,
            "credential_revision": self.credential_revision,
            "lifecycle_revision": self.lifecycle_revision,
            "lifecycle_status": self.lifecycle_status.value,
            "status_changed_at": self.status_changed_at.isoformat(timespec="microseconds"),
            "previous_fingerprint": self.previous_fingerprint,
        }

    def compute_fingerprint(self) -> str:
        """Compute SHA3-512 identity over every authoritative field."""
        encoded = json.dumps(self.semantic_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        return hashlib.sha3_512(encoded).hexdigest()

    def to_persisted(self) -> dict[str, object]:
        """Serialize the exact secret-free persisted schema."""
        result = self.semantic_payload()
        result.pop("schema")
        result["authority_fingerprint"] = self.authority_fingerprint
        return result

    @classmethod
    def from_persisted(cls, row: Mapping[str, object]) -> "InternalServiceWorkloadCredentialAuthority":
        """Hydrate one exact row and fail closed on missing, extra, or corrupt fields."""
        expected = {
            "service_id", "key_id", "principal_id", "credential_scope", "credential_revision",
            "lifecycle_revision", "lifecycle_status", "status_changed_at", "previous_fingerprint",
            "authority_fingerprint",
        }
        clean = cast(dict[str, Any], {key: value for key, value in row.items() if key != "_id"})
        if set(clean) != expected:
            raise InternalServiceWorkloadCredentialAuthorityError("PERSISTED_SCHEMA_INVALID")
        try:
            changed_at = clean["status_changed_at"]
            if isinstance(changed_at, str):
                changed_at = datetime.fromisoformat(changed_at)
            return cls(
                service_id=clean["service_id"], key_id=clean["key_id"], principal_id=clean["principal_id"],
                credential_scope=clean["credential_scope"], credential_revision=clean["credential_revision"],
                lifecycle_revision=clean["lifecycle_revision"],
                lifecycle_status=WorkloadCredentialLifecycleStatus(clean["lifecycle_status"]),
                status_changed_at=changed_at, previous_fingerprint=clean["previous_fingerprint"],
                authority_fingerprint=clean["authority_fingerprint"],
            )  # type: ignore[arg-type]
        except (TypeError, ValueError) as error:
            if isinstance(error, InternalServiceWorkloadCredentialAuthorityError):
                raise
            raise InternalServiceWorkloadCredentialAuthorityError("PERSISTED_AUTHORITY_INVALID") from error


__all__ = [
    "VERSION", "SCHEMA", "PLATFORM_INTERNAL_SCOPE", "InternalServiceWorkloadCredentialAuthorityError",
    "WorkloadCredentialLifecycleStatus", "InternalServiceWorkloadCredentialAuthority",
]

# ARTIFACT: internal_service_workload_credential_authority.py
# VERSION: v1.0.0-P3-R3G-S6-A1
# AUTHORITY BOUNDARY: Secret-free internal-service credential binding and lifecycle only.
# TENANT POSTURE: Platform/internal; grants no tenant authority.
# FAIL-CLOSED POSTURE: Malformed state, scope drift, and fingerprint drift reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
