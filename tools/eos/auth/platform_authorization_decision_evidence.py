"""WILSY OS — PLATFORM AUTHORIZATION DECISION EVIDENCE DOMAIN

TITLE: Platform Authorization Decision Evidence
VERSION: v1.0.0-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE
AUTHORITY: Wilsy OS Sovereign IAM / Core Governance
EPITOME: Immutable evidence of one platform-scoped allow/deny decision.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/platform_authorization_decision_evidence.py
COLLABORATION / OWNERSHIP: Pure evidence contract; the governed issuer and a
    separately approved durable registry own issuance and persistence.
CERTIFICATION / UPDATE DATE: 2026-10-25
CHANGELOG: v1.0.0 defines canonical platform decision disposition, identity
    trust posture, exact reconciliation scope provenance, and deterministic
    integrity fingerprinting without introducing persistence or authorization.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 control alignment.
SECURITY / PRIVACY POSTURE: No credentials, signatures, request bodies, secrets,
    or raw provider payloads are accepted or persisted.
TENANT BOUNDARY: Record scope is always PLATFORM; target tenant is a separate,
    optional server-resolved dimension and never creates caller authority.
AUTHORITY BOUNDARY: Evidence shape only; construction grants no permission,
    activation, authorization, provider access, or execution status.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority.
TRANSACTION BOUNDARY: Pure value object; no database, session, clock, or I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import re
import unicodedata
from typing import Any, Mapping

VERSION = "v1.0.0-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE"
SCHEMA = "WILSY-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE/V1"
PLATFORM_SCOPE = "PLATFORM"
_HEX_SHA3_512 = re.compile(r"[0-9a-f]{128}\Z")
_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}\Z")
_REASON = re.compile(r"[A-Z][A-Z0-9_]{0,127}\Z")


class PlatformAuthorizationDecisionEvidenceError(ValueError):
    """Fail-closed malformed platform authorization decision evidence."""


class PlatformAuthorizationDecision(str, Enum):
    """Disposition of an evaluated platform authorization request."""

    ALLOW = "ALLOW"
    DENY = "DENY"


class PlatformAuthorizationIdentityTrust(str, Enum):
    """Trust status of the workload identity at decision time."""

    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    REJECTED = "REJECTED"


def _token(value: Any, name: str) -> str:
    if (
        not isinstance(value, str)
        or _TOKEN.fullmatch(value) is None
        or any(unicodedata.category(char) == "Cc" for char in value)
    ):
        raise PlatformAuthorizationDecisionEvidenceError(f"{name} is invalid")
    return value


def _optional_token(value: Any, name: str) -> str | None:
    if value is None:
        return None
    return _token(value, name)


def _fingerprint(value: Any, name: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or _HEX_SHA3_512.fullmatch(value) is None:
        raise PlatformAuthorizationDecisionEvidenceError(f"{name} is invalid")
    return value


def _timestamp(value: Any, name: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PlatformAuthorizationDecisionEvidenceError(f"{name} is invalid")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class PlatformAuthorizationDecisionEvidence:
    """Immutable evidence for one platform-scoped authorization decision.

    A verified principal is present only when the canonical workload trust
    authority verified that identity. Denials before identity verification must
    leave principal_id absent. Target tenant/provider fields describe only the
    target resolved by server-owned configuration; they are not request inputs.

    The record means ALLOW or DENY was decided at evaluated_at. It never means
    reconciliation ran, provider data was read, a transaction committed, or
    any downstream action succeeded. Construction is not authorization and this
    value object performs no persistence, clock reads, or transaction management.
    """

    decision_id: str
    idempotency_key: str
    correlation_id: str
    decision: PlatformAuthorizationDecision
    reason_code: str
    evaluated_at: datetime
    identity_trust: PlatformAuthorizationIdentityTrust
    principal_id: str | None
    workload_service_id: str | None
    workload_key_id: str | None
    activation_id: str | None
    permission_assignment_id: str | None
    permission_assignment_fingerprint: str | None
    target_tenant_id: str | None
    provider_name: str | None
    target_scope_fingerprint: str | None
    authorization_policy_version: str
    authorization_gate_version: str
    authorization_scope: str = PLATFORM_SCOPE

    def __post_init__(self) -> None:
        for name in (
            "decision_id",
            "idempotency_key",
            "correlation_id",
            "authorization_policy_version",
            "authorization_gate_version",
        ):
            object.__setattr__(self, name, _token(getattr(self, name), name))

        if not isinstance(self.decision, PlatformAuthorizationDecision):
            raise PlatformAuthorizationDecisionEvidenceError("decision is invalid")
        if not isinstance(self.identity_trust, PlatformAuthorizationIdentityTrust):
            raise PlatformAuthorizationDecisionEvidenceError("identity_trust is invalid")
        if (
            not isinstance(self.reason_code, str)
            or _REASON.fullmatch(self.reason_code) is None
        ):
            raise PlatformAuthorizationDecisionEvidenceError("reason_code is invalid")
        if self.authorization_scope != PLATFORM_SCOPE:
            raise PlatformAuthorizationDecisionEvidenceError(
                "authorization_scope must be PLATFORM"
            )

        for name in (
            "principal_id",
            "workload_service_id",
            "workload_key_id",
            "activation_id",
            "permission_assignment_id",
            "target_tenant_id",
            "provider_name",
        ):
            object.__setattr__(
                self, name, _optional_token(getattr(self, name), name)
            )

        object.__setattr__(
            self,
            "permission_assignment_fingerprint",
            _fingerprint(
                self.permission_assignment_fingerprint,
                "permission_assignment_fingerprint",
                optional=True,
            ),
        )
        object.__setattr__(
            self,
            "target_scope_fingerprint",
            _fingerprint(
                self.target_scope_fingerprint,
                "target_scope_fingerprint",
                optional=True,
            ),
        )
        object.__setattr__(self, "evaluated_at", _timestamp(self.evaluated_at, "evaluated_at"))

        if self.identity_trust is PlatformAuthorizationIdentityTrust.VERIFIED:
            if self.principal_id is None:
                raise PlatformAuthorizationDecisionEvidenceError(
                    "verified identity requires principal_id"
                )
        elif self.principal_id is not None:
            raise PlatformAuthorizationDecisionEvidenceError(
                "unverified identity cannot claim principal_id"
            )

        if self.decision is PlatformAuthorizationDecision.ALLOW:
            required = (
                self.identity_trust is PlatformAuthorizationIdentityTrust.VERIFIED,
                self.principal_id is not None,
                self.activation_id is not None,
                self.permission_assignment_id is not None,
                self.permission_assignment_fingerprint is not None,
                self.target_tenant_id is not None,
                self.provider_name is not None,
                self.target_scope_fingerprint is not None,
            )
            if not all(required):
                raise PlatformAuthorizationDecisionEvidenceError(
                    "allow decision requires verified identity and complete authority/scope provenance"
                )

    def evidence_payload(self) -> dict[str, Any]:
        """Return the canonical JSON-compatible payload excluding its fingerprint."""
        return {
            "schema": SCHEMA,
            "decision_id": self.decision_id,
            "idempotency_key": self.idempotency_key,
            "correlation_id": self.correlation_id,
            "decision": self.decision.value,
            "reason_code": self.reason_code,
            "evaluated_at": self.evaluated_at.isoformat(timespec="microseconds"),
            "identity_trust": self.identity_trust.value,
            "principal_id": self.principal_id,
            "workload_service_id": self.workload_service_id,
            "workload_key_id": self.workload_key_id,
            "activation_id": self.activation_id,
            "permission_assignment_id": self.permission_assignment_id,
            "permission_assignment_fingerprint": self.permission_assignment_fingerprint,
            "target_tenant_id": self.target_tenant_id,
            "provider_name": self.provider_name,
            "target_scope_fingerprint": self.target_scope_fingerprint,
            "authorization_policy_version": self.authorization_policy_version,
            "authorization_gate_version": self.authorization_gate_version,
            "authorization_scope": self.authorization_scope,
        }

    @property
    def evidence_fingerprint(self) -> str:
        """Return SHA3-512 over the canonical serialized evidence payload."""
        encoded = json.dumps(
            self.evidence_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return hashlib.sha3_512(encoded).hexdigest()

    def to_persisted(self) -> dict[str, Any]:
        """Return the exact persistence shape; the caller owns durable issuance."""
        return {
            **self.evidence_payload(),
            "evidence_fingerprint": self.evidence_fingerprint,
        }

    @classmethod
    def from_persisted(
        cls, document: Mapping[str, Any]
    ) -> "PlatformAuthorizationDecisionEvidence":
        """Strictly hydrate a persisted row and verify its complete fingerprint."""
        expected = {
            "schema",
            "decision_id",
            "idempotency_key",
            "correlation_id",
            "decision",
            "reason_code",
            "evaluated_at",
            "identity_trust",
            "principal_id",
            "workload_service_id",
            "workload_key_id",
            "activation_id",
            "permission_assignment_id",
            "permission_assignment_fingerprint",
            "target_tenant_id",
            "provider_name",
            "target_scope_fingerprint",
            "authorization_policy_version",
            "authorization_gate_version",
            "authorization_scope",
            "evidence_fingerprint",
        }
        if not isinstance(document, Mapping) or set(document) != expected:
            raise PlatformAuthorizationDecisionEvidenceError(
                "persisted evidence shape is invalid"
            )
        if document.get("schema") != SCHEMA:
            raise PlatformAuthorizationDecisionEvidenceError("schema is invalid")
        if not isinstance(document.get("evaluated_at"), str):
            raise PlatformAuthorizationDecisionEvidenceError(
                "evaluated_at is not a canonical string"
            )
        try:
            evaluated_at = datetime.fromisoformat(document["evaluated_at"])
            decision = PlatformAuthorizationDecision(document["decision"])
            identity_trust = PlatformAuthorizationIdentityTrust(
                document["identity_trust"]
            )
        except (TypeError, ValueError) as error:
            raise PlatformAuthorizationDecisionEvidenceError(
                "persisted enum or timestamp is invalid"
            ) from error
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
            raise PlatformAuthorizationDecisionEvidenceError(
                "persisted evaluated_at must be timezone-aware"
            )
        if evaluated_at.astimezone(timezone.utc).isoformat(timespec="microseconds") != document["evaluated_at"]:
            raise PlatformAuthorizationDecisionEvidenceError(
                "persisted evaluated_at is not canonical UTC"
            )

        fields = {
            name: document[name]
            for name in (
                "decision_id",
                "idempotency_key",
                "correlation_id",
                "reason_code",
                "principal_id",
                "workload_service_id",
                "workload_key_id",
                "activation_id",
                "permission_assignment_id",
                "permission_assignment_fingerprint",
                "target_tenant_id",
                "provider_name",
                "target_scope_fingerprint",
                "authorization_policy_version",
                "authorization_gate_version",
                "authorization_scope",
            )
        }
        value = cls(
            **fields,
            decision=decision,
            identity_trust=identity_trust,
            evaluated_at=evaluated_at,
        )
        if document["evidence_fingerprint"] != value.evidence_fingerprint:
            raise PlatformAuthorizationDecisionEvidenceError(
                "persisted evidence fingerprint is invalid"
            )
        return value


__all__ = [
    "VERSION",
    "SCHEMA",
    "PLATFORM_SCOPE",
    "PlatformAuthorizationDecision",
    "PlatformAuthorizationIdentityTrust",
    "PlatformAuthorizationDecisionEvidence",
    "PlatformAuthorizationDecisionEvidenceError",
]

# ARTIFACT: platform_authorization_decision_evidence.py
# VERSION: v1.0.0-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE
# AUTHORITY BOUNDARY: immutable decision evidence only; no grant or execution truth.
# TENANT POSTURE: platform scope is fixed; target tenant is independently server-resolved.
# FAIL-CLOSED POSTURE: invalid identity, decision, scope, timestamp, shape, or fingerprint rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
