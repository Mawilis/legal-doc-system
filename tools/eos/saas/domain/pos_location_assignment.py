"""Canonical POS location assignment authority contract.

Location assignment is explicit tenant-scoped authority. A location identifier
in a request is only a selector; this record must be resolved server-side
against the authenticated principal and tenant before POS operations proceed.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import re


class POSLocationAssignmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


def _required(value: str, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"POS_LOCATION_{field.upper()}_INVALID")
    return value


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("POS_LOCATION_TIMESTAMP_INVALID")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class POSLocationAssignment:
    tenant_id: str
    location_id: str
    principal_id: str
    assignment_id: str
    revision: int
    status: POSLocationAssignmentStatus
    authority_reference: str
    authority_fingerprint: str
    idempotency_key: str
    occurred_at: datetime
    changed_by_principal_id: str
    reason: str | None = None

    def __post_init__(self) -> None:
        for name in ("tenant_id", "location_id", "principal_id", "assignment_id",
                     "authority_reference", "idempotency_key", "changed_by_principal_id"):
            _required(getattr(self, name), name)
        if type(self.revision) is not int or self.revision < 0:
            raise ValueError("POS_LOCATION_REVISION_INVALID")
        if not isinstance(self.status, POSLocationAssignmentStatus):
            raise ValueError("POS_LOCATION_STATUS_INVALID")
        if not isinstance(self.authority_fingerprint, str) or not re.fullmatch(r"[0-9a-f]{128}", self.authority_fingerprint):
            raise ValueError("POS_LOCATION_AUTHORITY_FINGERPRINT_INVALID")
        object.__setattr__(self, "occurred_at", _utc(self.occurred_at))
        if self.status is POSLocationAssignmentStatus.REVOKED:
            _required(self.reason or "", "revocation_reason")
        elif self.reason is not None:
            raise ValueError("POS_LOCATION_ACTIVE_REASON_FORBIDDEN")

    def unsigned_dict(self) -> dict:
        return {
            "schema": "WILSY-POS-LOCATION-ASSIGNMENT/V1",
            "version": "v1.0.0-POS-LOCATION-AUTHORITY",
            "entity_type": "POSLocationAssignment",
            "tenant_id": self.tenant_id,
            "location_id": self.location_id,
            "principal_id": self.principal_id,
            "assignment_id": self.assignment_id,
            "revision": self.revision,
            "status": self.status.value,
            "authority_reference": self.authority_reference,
            "authority_fingerprint": self.authority_fingerprint,
            "idempotency_key": self.idempotency_key,
            "occurred_at": self.occurred_at.isoformat(),
            "changed_by_principal_id": self.changed_by_principal_id,
            "reason": self.reason,
        }

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(self.unsigned_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha3_512(payload.encode()).hexdigest()

    def to_dict(self) -> dict:
        value = self.unsigned_dict()
        value["fingerprint"] = self.fingerprint
        return value


__all__ = ["POSLocationAssignment", "POSLocationAssignmentStatus"]
