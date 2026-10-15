"""TITLE: WILSY OS System Permission Command Evidence.
VERSION: v1.0.0-D12-COMMAND-EVIDENCE
AUTHORITY: Immutable deterministic evidence for ASSIGN, REVOKE, and BOOTSTRAP_SEED.
EPITOME: Binds every actor, target, permission, operation, timestamp, replay key, and seed lineage.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_command_evidence.py
COLLABORATION: D12 command services and durable assignment registry.
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes SHA3-512 command evidence and operation-specific bindings.
COMPLIANCE / SECURITY: Canonical JSON; secret-free; POPIA 19, GDPR 32, SOC2 CC7.2.
TENANT BOUNDARY: No tenant authority or tenant identifier.
AUTHORITY BOUNDARY: Evidence records a command; it does not authorize it.
FINANCIAL AUTHORITY BOUNDARY: No financial fields or execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
from typing import Final

VERSION: Final[str] = "v1.0.0-D12-COMMAND-EVIDENCE"


class SystemPermissionCommandOperation(StrEnum):
    """Closed command operation vocabulary."""
    ASSIGN = "ASSIGN"
    REVOKE = "REVOKE"
    BOOTSTRAP_SEED = "BOOTSTRAP_SEED"


class SystemPermissionCommandEvidenceError(ValueError):
    """Reject malformed or internally inconsistent command evidence."""


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "*" in value:
        raise SystemPermissionCommandEvidenceError(name + "_INVALID")
    return value


def _time(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise SystemPermissionCommandEvidenceError("OCCURRED_AT_INVALID")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class SystemPermissionCommandEvidence:
    """Immutable command evidence; authorization and transaction ownership remain external."""
    operation: SystemPermissionCommandOperation
    actor_principal_id: str
    target_principal_id: str
    permission_id: str
    evidence_reference: str
    occurred_at: datetime
    idempotency_key: str
    assignment_id: str | None = None
    bootstrap_id: str | None = None
    bootstrap_purpose: str | None = None
    evidence_fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.operation, SystemPermissionCommandOperation):
            raise SystemPermissionCommandEvidenceError("OPERATION_INVALID")
        for name in ("actor_principal_id", "target_principal_id", "permission_id", "evidence_reference", "idempotency_key"):
            object.__setattr__(self, name, _text(name.upper(), getattr(self, name)))
        occurred = _time(self.occurred_at)
        object.__setattr__(self, "occurred_at", occurred)
        if self.operation is SystemPermissionCommandOperation.BOOTSTRAP_SEED:
            if self.assignment_id is not None:
                raise SystemPermissionCommandEvidenceError("ASSIGNMENT_ID_FORBIDDEN")
            object.__setattr__(self, "bootstrap_id", _text("BOOTSTRAP_ID", self.bootstrap_id))
            object.__setattr__(self, "bootstrap_purpose", _text("BOOTSTRAP_PURPOSE", self.bootstrap_purpose))
        elif self.operation is SystemPermissionCommandOperation.REVOKE:
            object.__setattr__(self, "assignment_id", _text("ASSIGNMENT_ID", self.assignment_id))
            if self.bootstrap_id is not None or self.bootstrap_purpose is not None:
                raise SystemPermissionCommandEvidenceError("BOOTSTRAP_BINDING_FORBIDDEN")
        elif self.assignment_id is not None or self.bootstrap_id is not None or self.bootstrap_purpose is not None:
            raise SystemPermissionCommandEvidenceError("EXTRANEOUS_BINDING_FORBIDDEN")
        payload = self.to_payload()
        object.__setattr__(self, "evidence_fingerprint", sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest())

    def to_payload(self) -> dict[str, object]:
        """Return complete canonical evidence material excluding its derived digest."""
        return {"schema": "WILSY-SYSTEM-PERMISSION-COMMAND-EVIDENCE/V1", "version": VERSION, "operation": self.operation.value, "actor_principal_id": self.actor_principal_id, "target_principal_id": self.target_principal_id, "permission_id": self.permission_id, "evidence_reference": self.evidence_reference, "occurred_at": self.occurred_at.isoformat(), "idempotency_key": self.idempotency_key, "assignment_id": self.assignment_id, "bootstrap_id": self.bootstrap_id, "bootstrap_purpose": self.bootstrap_purpose}

    def derived_assignment_id(self) -> str:
        """Derive a stable assignment identity for ASSIGN or BOOTSTRAP_SEED replay."""
        if self.operation is SystemPermissionCommandOperation.REVOKE:
            raise SystemPermissionCommandEvidenceError("ASSIGNMENT_ID_DERIVATION_FORBIDDEN")
        return "WILSYSYSPERM-" + self.evidence_fingerprint[:32]


__all__ = ["VERSION", "SystemPermissionCommandOperation", "SystemPermissionCommandEvidenceError", "SystemPermissionCommandEvidence"]
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: system_permission_command_evidence.py
# VERSION: v1.0.0-D12-COMMAND-EVIDENCE
# AUTHORITY BOUNDARY: EVIDENCE ONLY; AUTHORIZATION EXTERNAL
# TENANT POSTURE: TENANT-NEUTRAL SYSTEM COMMAND
# FAIL-CLOSED POSTURE: COMPLETE OPERATION-SPECIFIC SHA3-512 BINDING
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
