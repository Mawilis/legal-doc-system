"""WILSY OS immutable authorization-role revocation evidence value object.

TITLE: Authorization Role Revocation Evidence
VERSION: v1.0.0-P1-R3B-E1-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Preserve deterministic evidence of one completed ACTIVE revision N to
         REVOKED revision N+1 authorization-role assignment transition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authorization_role_revocation_evidence.py
COLLABORATION / OWNERSHIP: P1-R3B-E1 owns only the immutable evidence shape;
                            later trusted orchestration supplies provenance and
                            a separately authorized registry owns persistence.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-P1-R3B-E1 establishes strict identifiers, contiguous
           revisions, canonical ACTIVE-to-REVOKED semantics, UTC time,
           authorization provenance, idempotency identity, strict hydration,
           and deterministic SHA3-512 corruption detection.
COMPLIANCE: NIST privileged-access lifecycle principles; POPIA section 19;
            GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque bounded identifiers, no credentials or PII,
                             deterministic canonical serialization, and
                             constant-time stored-digest comparison.
TENANT BOUNDARY: Evidence binds one explicit non-pseudo tenant, actor principal,
                 target principal, and target authorization role; nothing is inferred.
AUTHORITY BOUNDARY: Immutable revocation evidence only. This artifact does not
                    grant or prove current authority, authorize the actor,
                    evaluate revocation policy, mutate role assignments, own
                    transactions or persistence, perform root rotation,
                    implement privileged activation or break glass, or execute
                    financial operations.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial
                              execution and settlement.
FAIL-CLOSED DECLARATION: Malformed identities, pseudo tenants, invalid
                         operation/provenance/revisions/time/schema/shape, and
                         stored fingerprint corruption reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
import json
import re
import unicodedata
from typing import Any, Final


VERSION: Final[str] = "v1.0.0-P1-R3B-E1-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE"
SCHEMA: Final[str] = "WILSY-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE/V1"
OPERATION: Final[str] = "role_revoke"
PRIOR_STATUS: Final[str] = "ACTIVE"
RESULT_STATUS: Final[str] = "REVOKED"
MAX_IDENTIFIER_LENGTH: Final[int] = 256
_SHA3_512: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}\Z")


class AuthorizationRoleRevocationEvidenceError(ValueError):
    """Stable fail-closed validation error for revocation evidence."""


def _text(name: str, value: object) -> str:
    """Require one exact bounded opaque string without silent normalization."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > MAX_IDENTIFIER_LENGTH
        or any(unicodedata.category(character) == "Cc" for character in value)
    ):
        raise AuthorizationRoleRevocationEvidenceError(f"{name} is invalid")
    return value


def _tenant(value: object) -> str:
    """Require an explicit non-pseudo tenant identity."""
    tenant_id = _text("tenant_id", value)
    if tenant_id.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        raise AuthorizationRoleRevocationEvidenceError("tenant_id is invalid")
    return tenant_id


def _revision(name: str, value: object) -> int:
    """Require a non-negative, non-boolean assignment revision."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AuthorizationRoleRevocationEvidenceError(f"{name} is invalid")
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require exactly one lowercase SHA3-512 hexadecimal digest."""
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise AuthorizationRoleRevocationEvidenceError(f"{name} is invalid")
    return value


def _timestamp(value: object) -> datetime:
    """Require one aware datetime and canonicalize it exactly once to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise AuthorizationRoleRevocationEvidenceError("revoked_at is invalid")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class AuthorizationRoleRevocationEvidence:
    """Immutable evidence for one completed ACTIVE-to-REVOKED transition.

    Construction records supplied historical facts only. It never evaluates
    policy, proves current authority, performs assignment mutation, persists,
    owns a transaction, or exercises root, break-glass, activation, or finance
    authority. The required idempotency key supports later registry replay but
    this value object enforces no uniqueness.
    """

    revocation_id: str
    tenant_id: str
    actor_principal_id: str
    target_principal_id: str
    target_role_id: str
    target_assignment_prior_revision: int
    target_assignment_result_revision: int
    operation: str
    reason_reference: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    idempotency_key: str
    revoked_at: datetime

    def __post_init__(self) -> None:
        """Validate and canonicalize evidence without generating authority."""
        for name in (
            "revocation_id",
            "actor_principal_id",
            "target_principal_id",
            "target_role_id",
            "operation",
            "reason_reference",
            "authorization_evidence_reference",
            "idempotency_key",
        ):
            object.__setattr__(self, name, _text(name, getattr(self, name)))
        object.__setattr__(self, "tenant_id", _tenant(self.tenant_id))
        prior = _revision("target_assignment_prior_revision", self.target_assignment_prior_revision)
        result = _revision("target_assignment_result_revision", self.target_assignment_result_revision)
        if result != prior + 1:
            raise AuthorizationRoleRevocationEvidenceError("assignment revisions are not contiguous")
        if self.operation != OPERATION:
            raise AuthorizationRoleRevocationEvidenceError("operation is invalid")
        object.__setattr__(
            self,
            "authorization_evidence_fingerprint",
            _fingerprint("authorization_evidence_fingerprint", self.authorization_evidence_fingerprint),
        )
        object.__setattr__(self, "revoked_at", _timestamp(self.revoked_at))

    def evidence_payload(self) -> dict[str, object]:
        """Return the exact canonical semantic payload used for fingerprinting."""
        return {
            "schema": SCHEMA,
            "revocation_id": self.revocation_id,
            "tenant_id": self.tenant_id,
            "actor_principal_id": self.actor_principal_id,
            "target_principal_id": self.target_principal_id,
            "target_role_id": self.target_role_id,
            "target_assignment_prior_revision": self.target_assignment_prior_revision,
            "target_assignment_result_revision": self.target_assignment_result_revision,
            "prior_status": PRIOR_STATUS,
            "result_status": RESULT_STATUS,
            "operation": self.operation,
            "reason_reference": self.reason_reference,
            "authorization_evidence_reference": self.authorization_evidence_reference,
            "authorization_evidence_fingerprint": self.authorization_evidence_fingerprint,
            "idempotency_key": self.idempotency_key,
            "revoked_at": self.revoked_at.isoformat(timespec="microseconds"),
        }

    @property
    def revocation_evidence_fingerprint(self) -> str:
        """Return deterministic lowercase SHA3-512 over the canonical payload."""
        canonical = json.dumps(
            self.evidence_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        return sha3_512(canonical).hexdigest()

    def to_persisted(self) -> dict[str, object]:
        """Return the exact strict persisted shape; no persistence is performed."""
        return {
            **self.evidence_payload(),
            "revocation_evidence_fingerprint": self.revocation_evidence_fingerprint,
        }

    @classmethod
    def from_persisted(cls, document: Mapping[str, object]) -> "AuthorizationRoleRevocationEvidence":
        """Strictly hydrate and verify one persisted evidence mapping.

        Unknown/missing fields, schema/transition drift, noncanonical time, and
        digest mismatch reject. Historical authorization provenance remains
        evidence only and is never treated as current authority.
        """
        data_fields = {field.name for field in fields(cls)}
        expected = data_fields | {
            "schema",
            "prior_status",
            "result_status",
            "revocation_evidence_fingerprint",
        }
        if not isinstance(document, Mapping) or set(document) != expected:
            raise AuthorizationRoleRevocationEvidenceError("persisted evidence shape is invalid")
        if document.get("schema") != SCHEMA:
            raise AuthorizationRoleRevocationEvidenceError("schema is invalid")
        if document.get("prior_status") != PRIOR_STATUS or document.get("result_status") != RESULT_STATUS:
            raise AuthorizationRoleRevocationEvidenceError("transition is invalid")
        raw_time = document.get("revoked_at")
        if not isinstance(raw_time, str):
            raise AuthorizationRoleRevocationEvidenceError("revoked_at is not a canonical string")
        try:
            parsed_time = datetime.fromisoformat(raw_time)
        except ValueError as error:
            raise AuthorizationRoleRevocationEvidenceError("revoked_at is invalid") from error
        canonical_time = _timestamp(parsed_time).isoformat(timespec="microseconds")
        if raw_time != canonical_time:
            raise AuthorizationRoleRevocationEvidenceError("revoked_at is not canonical")
        arguments = {name: document[name] for name in data_fields}
        arguments["revoked_at"] = parsed_time
        value = cls(**arguments)  # type: ignore[arg-type]
        stored = _fingerprint(
            "revocation_evidence_fingerprint",
            document.get("revocation_evidence_fingerprint"),
        )
        if not hmac.compare_digest(stored, value.revocation_evidence_fingerprint):
            raise AuthorizationRoleRevocationEvidenceError("persisted evidence fingerprint is invalid")
        return value


__all__ = [
    "VERSION",
    "SCHEMA",
    "OPERATION",
    "PRIOR_STATUS",
    "RESULT_STATUS",
    "AuthorizationRoleRevocationEvidence",
    "AuthorizationRoleRevocationEvidenceError",
]

# ARTIFACT: authorization_role_revocation_evidence.py
# VERSION: v1.0.0-P1-R3B-E1-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE
# AUTHORITY BOUNDARY: immutable revocation evidence only; no authority proof/grant, policy evaluation, mutation, persistence, transaction, root rotation, activation, break glass, or finance
# TENANT POSTURE: one explicit non-pseudo tenant, actor, target principal, and target role are bound; no default or cross-tenant inference
# FAIL-CLOSED POSTURE: malformed semantics, noncanonical time, shape/schema/transition drift, and fingerprint corruption reject
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
