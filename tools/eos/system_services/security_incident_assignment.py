"""Governed System Services security-incident responder assignment evidence."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import re
from typing import Final

VERSION: Final[str] = "v1.0.0-EOS-SECURITY-INCIDENT-ASSIGNMENT"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")


class SecurityIncidentAssignmentStatus(StrEnum):
    PENDING_ACCEPTANCE = "PENDING_ACCEPTANCE"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


class SecurityIncidentAssignmentError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class SecurityIncidentAssignment:
    assignment_id: str
    incident_id: str
    tenant_id: str
    reporter_principal_id: str
    assigned_by_principal_id: str
    assigned_to_principal_id: str
    status: SecurityIncidentAssignmentStatus
    revision: int
    created_at: datetime
    updated_at: datetime
    idempotency_fingerprint: str

    def __post_init__(self) -> None:
        for value in (
            self.assignment_id, self.incident_id, self.tenant_id,
            self.reporter_principal_id, self.assigned_by_principal_id,
            self.assigned_to_principal_id, self.idempotency_fingerprint,
        ):
            if not isinstance(value, str) or not _ID.fullmatch(value):
                raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_IDENTIFIER_INVALID")
        if self.reporter_principal_id in {
            self.assigned_by_principal_id, self.assigned_to_principal_id
        } or self.assigned_by_principal_id == self.assigned_to_principal_id:
            raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_CONFLICT_OF_INTEREST")
        if not isinstance(self.status, SecurityIncidentAssignmentStatus):
            raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_STATUS_INVALID")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 0:
            raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_REVISION_INVALID")
        for value in (self.created_at, self.updated_at):
            if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
                raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_TIMESTAMP_INVALID")
        if self.updated_at < self.created_at:
            raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_TIMESTAMP_ORDER_INVALID")


@dataclass(frozen=True, slots=True)
class SecurityIncidentAssignmentEvent:
    event_id: str
    assignment_id: str
    actor_principal_id: str
    idempotency_fingerprint: str
    from_status: SecurityIncidentAssignmentStatus | None
    to_status: SecurityIncidentAssignmentStatus
    action: str
    occurred_at: datetime

    def __post_init__(self) -> None:
        for value in (self.event_id, self.assignment_id, self.actor_principal_id, self.idempotency_fingerprint, self.action):
            if not isinstance(value, str) or not _ID.fullmatch(value):
                raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_EVENT_INVALID")
        if not isinstance(self.to_status, SecurityIncidentAssignmentStatus):
            raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_EVENT_STATUS_INVALID")
        if self.from_status is not None and not isinstance(self.from_status, SecurityIncidentAssignmentStatus):
            raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_EVENT_STATUS_INVALID")
        if not isinstance(self.occurred_at, datetime) or self.occurred_at.tzinfo is None:
            raise SecurityIncidentAssignmentError("INCIDENT_ASSIGNMENT_EVENT_TIMESTAMP_INVALID")


__all__ = [
    "VERSION", "SecurityIncidentAssignmentStatus", "SecurityIncidentAssignmentError",
    "SecurityIncidentAssignment", "SecurityIncidentAssignmentEvent",
]
