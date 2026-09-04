"""WILSY OS — TENANT AUTHORIZATION DECISION EVIDENCE DOMAIN

TITLE: Tenant Authorization Decision Evidence
VERSION: v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE
AUTHORITY: Python EOS sovereign authorization evidence shape only.
PURPOSE: Preserve the exact successful authorization inputs and provenance snapshot.
EPITOME: Immutable, deterministic evidence; construction grants no authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_authorization_decision_evidence.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-09-04
CHANGELOG: v1.0.0 establishes explicit tenant-scoped authorization decision evidence.
COMPLIANCE: POPIA §19 | GDPR Article 32 | SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identifiers and SHA3-512 fingerprints; no secrets.
TENANT BOUNDARY: Every record is explicitly bound to one tenant and principal.
AUTHORITY BOUNDARY: Value contract is not an authority grant; durable issuance is P1B2B.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement; Kennel EOS exclusively executes finance.
TRANSACTION / PERSISTENCE BOUNDARY: Pure value object; caller owns persistence and sessions.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

VERSION = "v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE"
SCHEMA = "WILSY-TENANT-AUTHORIZATION-DECISION-EVIDENCE/V1"
_BASIS_SCHEMA = "WILSY-TENANT-AUTHORIZATION-BASIS/V1"
_HEX = re.compile(r"[0-9a-f]{128}\Z")
_MAX = 256


class TenantAuthorizationDecisionEvidenceError(ValueError):
    """Fail-closed error for malformed authorization evidence."""


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > _MAX:
        raise TenantAuthorizationDecisionEvidenceError(f"{name} is invalid")
    return value

def _decision_id(value: Any) -> str:
    result = _text(value, "authorization_decision_id")
    if result != result.strip() or ":" in result or any(unicodedata.category(char) == "Cc" for char in result):
        raise TenantAuthorizationDecisionEvidenceError("authorization_decision_id is invalid")
    return result


def _revision(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TenantAuthorizationDecisionEvidenceError(f"{name} is invalid")
    return value


def _fingerprint(value: Any, name: str) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        raise TenantAuthorizationDecisionEvidenceError(f"{name} is invalid")
    return value


@dataclass(frozen=True, slots=True)
class TenantAuthorizationDecisionEvidence:
    """Immutable evidence of one successful, already-authorized decision.

    All identity, policy, revision, timestamp, and idempotency values are supplied
    by a trusted issuer. This object cannot represent denial, discover authority,
    generate IDs or clocks, persist records, or execute business/financial work.
    """

    tenant_id: str
    authorization_decision_id: str
    principal_id: str
    operation: str
    permission: str
    business_role: str
    authorization_role: str
    membership_revision: int
    role_assignment_revision: int
    subject_reference: str
    subject_evidence_fingerprint: str
    permission_namespace_version: str
    authorization_role_policy_version: str
    tenant_business_role_policy_version: str
    tenant_authorization_composition_version: str
    idempotency_key: str
    authorized_at: datetime

    def __post_init__(self) -> None:
        for name in ("tenant_id", "principal_id", "operation", "permission", "business_role", "authorization_role", "subject_reference", "permission_namespace_version", "authorization_role_policy_version", "tenant_business_role_policy_version", "tenant_authorization_composition_version", "idempotency_key"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(self, "authorization_decision_id", _decision_id(self.authorization_decision_id))
        object.__setattr__(self, "membership_revision", _revision(self.membership_revision, "membership_revision"))
        object.__setattr__(self, "role_assignment_revision", _revision(self.role_assignment_revision, "role_assignment_revision"))
        object.__setattr__(self, "subject_evidence_fingerprint", _fingerprint(self.subject_evidence_fingerprint, "subject_evidence_fingerprint"))
        if not isinstance(self.authorized_at, datetime) or self.authorized_at.tzinfo is None or self.authorized_at.utcoffset() is None:
            raise TenantAuthorizationDecisionEvidenceError("authorized_at is invalid")
        object.__setattr__(self, "authorized_at", self.authorized_at.astimezone(timezone.utc))

    def authorization_basis_payload(self) -> dict[str, Any]:
        return {"schema": _BASIS_SCHEMA, **{name: getattr(self, name) for name in ("tenant_id", "principal_id", "operation", "permission", "business_role", "authorization_role", "membership_revision", "role_assignment_revision", "permission_namespace_version", "authorization_role_policy_version", "tenant_business_role_policy_version", "tenant_authorization_composition_version")}}

    @property
    def authorization_basis_reference(self) -> str:
        raw = json.dumps(self.authorization_basis_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        return "tenant-authorization-basis:sha3-512:" + hashlib.sha3_512(raw).hexdigest()

    @property
    def authorization_evidence_reference(self) -> str:
        return f"tenant-authorization-decision:{self.authorization_decision_id}"

    def evidence_payload(self) -> dict[str, Any]:
        return {"schema": SCHEMA, **{name: getattr(self, name).isoformat(timespec="microseconds") if name == "authorized_at" else getattr(self, name) for name in self.__dataclass_fields__}, "authorization_basis_reference": self.authorization_basis_reference}

    @property
    def authorization_evidence_fingerprint(self) -> str:
        raw = json.dumps(self.evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        return hashlib.sha3_512(raw).hexdigest()

    @property
    def authorized_by_principal_id(self) -> str:
        return self.principal_id

    def to_persisted(self) -> dict[str, Any]:
        return {**self.evidence_payload(), "authorization_evidence_fingerprint": self.authorization_evidence_fingerprint}

    @classmethod
    def from_persisted(cls, document: Mapping[str, Any]) -> "TenantAuthorizationDecisionEvidence":
        if not isinstance(document, Mapping) or set(document) != set(cls.__dataclass_fields__) | {"schema", "authorization_basis_reference", "authorization_evidence_fingerprint"}:
            raise TenantAuthorizationDecisionEvidenceError("persisted evidence shape is invalid")
        if document.get("schema") != SCHEMA:
            raise TenantAuthorizationDecisionEvidenceError("schema is invalid")
        body = {name: document[name] for name in cls.__dataclass_fields__}
        if not isinstance(body["authorized_at"], str):
            raise TenantAuthorizationDecisionEvidenceError("authorized_at is not a canonical string")
        try: body["authorized_at"] = datetime.fromisoformat(body["authorized_at"])
        except ValueError as error: raise TenantAuthorizationDecisionEvidenceError("authorized_at is invalid") from error
        if document["authorized_at"] != body["authorized_at"].astimezone(timezone.utc).isoformat(timespec="microseconds"):
            raise TenantAuthorizationDecisionEvidenceError("authorized_at is not canonical")
        value = cls(**body)
        if document["authorization_basis_reference"] != value.authorization_basis_reference or document["authorization_evidence_fingerprint"] != value.authorization_evidence_fingerprint:
            raise TenantAuthorizationDecisionEvidenceError("persisted evidence fingerprint is invalid")
        return value


__all__ = ["VERSION", "SCHEMA", "TenantAuthorizationDecisionEvidence", "TenantAuthorizationDecisionEvidenceError"]

# ARTIFACT: tenant_authorization_decision_evidence.py
# VERSION: v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE
# AUTHORITY BOUNDARY: evidence shape only; no authorization grant or persistence.
# TENANT POSTURE: explicit tenant and principal scope; no cross-tenant inference.
# FAIL-CLOSED POSTURE: malformed identity, scope, provenance, timestamp, or integrity rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
