"""WILSY OS immutable privileged break-glass command evidence.

TITLE: Privileged Break-Glass Command Evidence
VERSION: v1.0.0-P7-PRIVILEGED-BREAK-GLASS-COMMAND-EVIDENCE
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Seal one exact, dual-control, short-lived emergency activation command.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/privileged_break_glass_command_evidence.py
COLLABORATION / OWNERSHIP: P7 composes sealed D12, P2, P3, P4 and P6 authorities.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes deterministic secret-free command evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque reason reference only; no narrative or credential material.
TENANT BOUNDARY: Exact target class and tenant scope; platform scope forbids tenant material.
AUTHORITY BOUNDARY: Evidence is not authority without fresh service-side currentness checks.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes finance.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final, Mapping

from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass

VERSION: Final[str] = "v1.0.0-P7-PRIVILEGED-BREAK-GLASS-COMMAND-EVIDENCE"
SCHEMA: Final[str] = "WILSY-PRIVILEGED-BREAK-GLASS-COMMAND-EVIDENCE/V1"
BREAK_GLASS_PERMISSION: Final[str] = "privileged_activation:break_glass"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class PrivilegedBreakGlassCommandEvidenceError(ValueError):
    """Reject malformed, secret-bearing, or scope-divergent P7 evidence."""


def _text(name: str, value: object, *, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "*" in value or len(value) > maximum:
        raise PrivilegedBreakGlassCommandEvidenceError(name + "_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        raise PrivilegedBreakGlassCommandEvidenceError(name + "_INVALID")
    return value


def _revision(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PrivilegedBreakGlassCommandEvidenceError(name + "_INVALID")
    return value


def _moment(name: str, value: object, *, persisted: bool = False) -> datetime:
    if not isinstance(value, datetime):
        raise PrivilegedBreakGlassCommandEvidenceError(name + "_INVALID")
    if value.tzinfo is None or value.utcoffset() is None:
        if not persisted:
            raise PrivilegedBreakGlassCommandEvidenceError(name + "_INVALID")
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class PrivilegedBreakGlassCommandEvidence:
    """One immutable dual-control P7 authorization and activation lineage fact."""

    evidence_id: str
    idempotency_key: str
    requester_principal_id: str
    approver_principal_id: str
    tenant_id: str | None
    target_class: PrivilegedTargetClass
    privileged_role_id: str
    reason_reference: str
    requester_assignment_id: str
    requester_assignment_revision: int
    requester_assignment_fingerprint: str
    approver_assignment_id: str
    approver_assignment_revision: int
    approver_assignment_fingerprint: str
    eligibility_evidence_id: str
    eligibility_evidence_fingerprint: str
    requester_assurance_evidence_id: str
    requester_assurance_evidence_fingerprint: str
    approver_assurance_evidence_id: str
    approver_assurance_evidence_fingerprint: str
    activation_id: str
    activation_fingerprint: str
    authorized_at: datetime
    effective_until: datetime

    def __post_init__(self) -> None:
        for name in ("evidence_id", "idempotency_key", "requester_principal_id", "approver_principal_id", "privileged_role_id", "reason_reference", "requester_assignment_id", "approver_assignment_id", "eligibility_evidence_id", "requester_assurance_evidence_id", "approver_assurance_evidence_id", "activation_id"):
            object.__setattr__(self, name, _text(name.upper(), getattr(self, name)))
        if self.requester_principal_id == self.approver_principal_id:
            raise PrivilegedBreakGlassCommandEvidenceError("DUAL_CONTROL_REQUIRED")
        if not isinstance(self.target_class, PrivilegedTargetClass):
            raise PrivilegedBreakGlassCommandEvidenceError("TARGET_CLASS_INVALID")
        if self.target_class is PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT:
            if self.tenant_id is not None:
                raise PrivilegedBreakGlassCommandEvidenceError("PLATFORM_SCOPE_TENANT_FORBIDDEN")
        elif self.target_class is PrivilegedTargetClass.TENANT_PRIVILEGED:
            object.__setattr__(self, "tenant_id", _text("TENANT_ID", self.tenant_id))
        else:
            raise PrivilegedBreakGlassCommandEvidenceError("TARGET_CLASS_INVALID")
        for name in ("requester_assignment_revision", "approver_assignment_revision"):
            object.__setattr__(self, name, _revision(name.upper(), getattr(self, name)))
        for name in ("requester_assignment_fingerprint", "approver_assignment_fingerprint", "eligibility_evidence_fingerprint", "requester_assurance_evidence_fingerprint", "approver_assurance_evidence_fingerprint", "activation_fingerprint"):
            object.__setattr__(self, name, _fingerprint(name.upper(), getattr(self, name)))
        start = _moment("AUTHORIZED_AT", self.authorized_at)
        end = _moment("EFFECTIVE_UNTIL", self.effective_until)
        if end <= start:
            raise PrivilegedBreakGlassCommandEvidenceError("LIFETIME_INVALID")
        object.__setattr__(self, "authorized_at", start)
        object.__setattr__(self, "effective_until", end)

    def authority_payload(self) -> dict[str, object]:
        """Return the complete deterministic authority-bearing payload."""
        return {"schema": SCHEMA, "version": VERSION, **{name: (value.value if isinstance(value, PrivilegedTargetClass) else value.isoformat(timespec="microseconds") if isinstance(value, datetime) else value) for name, value in ((field, getattr(self, field)) for field in self.__dataclass_fields__)}}

    @property
    def evidence_fingerprint(self) -> str:
        """Return SHA3-512 over canonical secret-free semantics."""
        return sha3_512(json.dumps(self.authority_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()

    def fingerprint_matches(self, candidate: object) -> bool:
        """Compare a candidate evidence seal in timing-safe form."""
        return isinstance(candidate, str) and _HEX.fullmatch(candidate) is not None and hmac.compare_digest(candidate, self.evidence_fingerprint)

    def to_document(self) -> dict[str, object]:
        """Serialize for immutable Mongo persistence."""
        return {
            **{name: (value.value if isinstance(value, PrivilegedTargetClass) else value) for name, value in ((field, getattr(self, field)) for field in self.__dataclass_fields__)},
            "schema": SCHEMA,
            "version": VERSION,
            "evidence_fingerprint": self.evidence_fingerprint,
        }

    @classmethod
    def from_document(cls, document: Mapping[str, object]) -> "PrivilegedBreakGlassCommandEvidence":
        """Strictly hydrate one Mongo row, tolerating only BSON UTC tzinfo loss."""
        allowed = set(cls.__dataclass_fields__) | {"schema", "version", "evidence_fingerprint", "_id"}
        if set(document) - allowed or document.get("schema") != SCHEMA or document.get("version") != VERSION:
            raise PrivilegedBreakGlassCommandEvidenceError("PERSISTED_SCHEMA_INVALID")
        values = {name: document.get(name) for name in cls.__dataclass_fields__}
        values["target_class"] = PrivilegedTargetClass(values["target_class"])
        values["authorized_at"] = _moment("AUTHORIZED_AT", values["authorized_at"], persisted=True)
        values["effective_until"] = _moment("EFFECTIVE_UNTIL", values["effective_until"], persisted=True)
        value = cls(**values)  # type: ignore[arg-type]
        if not value.fingerprint_matches(document.get("evidence_fingerprint")):
            raise PrivilegedBreakGlassCommandEvidenceError("PERSISTED_FINGERPRINT_INVALID")
        return value


__all__ = ["VERSION", "SCHEMA", "BREAK_GLASS_PERMISSION", "PrivilegedBreakGlassCommandEvidenceError", "PrivilegedBreakGlassCommandEvidence"]

# ARTIFACT: privileged_break_glass_command_evidence.py
# VERSION: v1.0.0-P7-PRIVILEGED-BREAK-GLASS-COMMAND-EVIDENCE
# AUTHORITY BOUNDARY: immutable dual-control command evidence only
# TENANT POSTURE: exact tenant or platform scope; no wildcard or rebinding
# FAIL-CLOSED POSTURE: malformed, corrupt, divergent, or secret-bearing material rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
