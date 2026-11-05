"""Governed incident responder assignment and acknowledgement service.

Assignments require current platform workforce and exact existing SYSTEM
permissions. The service records routing/acceptance only; it never performs
containment, credential recovery, session revocation, or account mutation.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha3_256
from typing import Callable
from uuid import uuid4

from tools.eos.system_services.support_case_service import SystemServicesAuthorizer
from tools.eos.system_services.security_incident import SecurityIncident
from tools.eos.system_services.security_incident_registry import SecurityIncidentRegistry
from tools.eos.system_services.security_incident_assignment import (
    SecurityIncidentAssignment, SecurityIncidentAssignmentEvent,
    SecurityIncidentAssignmentStatus,
)
from tools.eos.system_services.security_incident_assignment_registry import (
    SecurityIncidentAssignmentRegistry, IncidentAssignmentConflictError,
    IncidentAssignmentNotFoundError,
)

PERMISSION_CASE_TRIAGE = "system_services:case:triage"
PERMISSION_INCIDENT_ESCALATE = "system_services:incident:escalate"


class SecurityIncidentEscalationError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SecurityIncidentEscalationService:
    def __init__(
        self, *, incidents: SecurityIncidentRegistry,
        assignments: SecurityIncidentAssignmentRegistry,
        authorizer: SystemServicesAuthorizer,
        clock: Callable[[], datetime] | None = None,
        id_factory: Callable[[str], str] | None = None,
    ) -> None:
        if not callable(getattr(authorizer, "require", None)):
            raise SecurityIncidentEscalationError("INCIDENT_ESCALATION_AUTHORIZER_REQUIRED")
        self._incidents = incidents
        self._assignments = assignments
        self._authorizer = authorizer
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._id_factory = id_factory or (lambda prefix: f"{prefix}-{uuid4().hex}")

    @staticmethod
    def _principal(value: object) -> str:
        if not isinstance(value, str) or not value or value != value.strip():
            raise SecurityIncidentEscalationError("INCIDENT_ESCALATION_PRINCIPAL_INVALID")
        return value

    def assign(
        self, *, actor_principal_id: str, assigned_to_principal_id: str,
        incident_id: str, idempotency_key: str, session: object,
    ) -> SecurityIncidentAssignment:
        actor = self._principal(actor_principal_id)
        responder = self._principal(assigned_to_principal_id)
        if actor == responder:
            raise SecurityIncidentEscalationError("INCIDENT_ASSIGNER_CANNOT_SELF_ASSIGN")
        if not isinstance(idempotency_key, str) or not idempotency_key or idempotency_key != idempotency_key.strip():
            raise SecurityIncidentEscalationError("INCIDENT_ASSIGNMENT_IDEMPOTENCY_INVALID")
        self._authorizer.require(
            principal_id=actor, permission_id=PERMISSION_CASE_TRIAGE, session=session,
        )
        incident = self._incidents.get_by_id(incident_id=incident_id, session=session)
        if incident.reporter_principal_id in {actor, responder}:
            raise SecurityIncidentEscalationError("INCIDENT_ASSIGNMENT_CONFLICT_OF_INTEREST")
        self._authorizer.require(
            principal_id=responder, permission_id=PERMISSION_INCIDENT_ESCALATE, session=session,
        )
        now = self._clock()
        fingerprint = sha3_256(
            (incident_id + "\\0" + actor + "\\0" + responder + "\\0" + idempotency_key).encode("utf-8")
        ).hexdigest()
        assignment_id = "assignment-" + fingerprint
        value = SecurityIncidentAssignment(
            assignment_id=assignment_id,
            incident_id=incident.incident_id,
            tenant_id=incident.tenant_id,
            reporter_principal_id=incident.reporter_principal_id,
            assigned_by_principal_id=actor,
            assigned_to_principal_id=responder,
            status=SecurityIncidentAssignmentStatus.PENDING_ACCEPTANCE,
            revision=0,
            created_at=now,
            updated_at=now,
            idempotency_fingerprint=fingerprint,
        )
        event = SecurityIncidentAssignmentEvent(
            event_id="assignment-event-" + fingerprint,
            assignment_id=assignment_id,
            actor_principal_id=actor,
            idempotency_fingerprint=sha3_256((fingerprint + "\\0ASSIGNED").encode("utf-8")).hexdigest(),
            from_status=None,
            to_status=SecurityIncidentAssignmentStatus.PENDING_ACCEPTANCE,
            action="INCIDENT_RESPONDER_ASSIGNED",
            occurred_at=now,
        )
        try:
            return self._assignments.create(value, event, session=session)
        except IncidentAssignmentConflictError as error:
            raise SecurityIncidentEscalationError("INCIDENT_ALREADY_ASSIGNED_OR_REPLAYED") from error

    def list_my_assignments(
        self, *, actor_principal_id: str, session: object, limit: int = 50,
    ) -> tuple[SecurityIncidentAssignment, ...]:
        actor = self._principal(actor_principal_id)
        self._authorizer.require(
            principal_id=actor, permission_id=PERMISSION_INCIDENT_ESCALATE, session=session,
        )
        return self._assignments.list_for_responder(
            principal_id=actor, session=session, limit=limit,
        )

    def read_my_assignment(
        self, *, actor_principal_id: str, assignment_id: str, session: object,
    ) -> tuple[SecurityIncidentAssignment, SecurityIncident]:
        actor = self._principal(actor_principal_id)
        self._authorizer.require(
            principal_id=actor, permission_id=PERMISSION_INCIDENT_ESCALATE, session=session,
        )
        assignment = self._assignments.get(assignment_id=assignment_id, session=session)
        if assignment.assigned_to_principal_id != actor:
            raise SecurityIncidentEscalationError("INCIDENT_ASSIGNMENT_RESPONDER_ONLY")
        incident = self._incidents.get_by_id(
            incident_id=assignment.incident_id, session=session,
        )
        if (
            incident.tenant_id != assignment.tenant_id
            or incident.reporter_principal_id != assignment.reporter_principal_id
        ):
            raise SecurityIncidentEscalationError("INCIDENT_ASSIGNMENT_SCOPE_MISMATCH")
        return assignment, incident

    def _respond(
        self, *, actor_principal_id: str, assignment_id: str,
        expected_revision: int, idempotency_key: str, accepted: bool,
        session: object,
    ) -> SecurityIncidentAssignment:
        actor = self._principal(actor_principal_id)
        if isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision < 0:
            raise SecurityIncidentEscalationError("INCIDENT_ASSIGNMENT_REVISION_INVALID")
        if not isinstance(idempotency_key, str) or not idempotency_key or idempotency_key != idempotency_key.strip():
            raise SecurityIncidentEscalationError("INCIDENT_ASSIGNMENT_IDEMPOTENCY_INVALID")
        self._authorizer.require(
            principal_id=actor, permission_id=PERMISSION_INCIDENT_ESCALATE, session=session,
        )
        current = self._assignments.get(assignment_id=assignment_id, session=session)
        if current.assigned_to_principal_id != actor:
            raise SecurityIncidentEscalationError("INCIDENT_ASSIGNMENT_RESPONDER_ONLY")
        if current.status is not SecurityIncidentAssignmentStatus.PENDING_ACCEPTANCE:
            raise IncidentAssignmentConflictError("INCIDENT_ASSIGNMENT_NOT_PENDING")
        now = self._clock()
        next_status = (
            SecurityIncidentAssignmentStatus.ACCEPTED
            if accepted else SecurityIncidentAssignmentStatus.DECLINED
        )
        updated = replace(
            current, status=next_status, revision=expected_revision + 1,
            updated_at=now,
        )
        fingerprint = sha3_256(
            (assignment_id + "\\0" + actor + "\\0" + idempotency_key + "\\0" + next_status.value).encode("utf-8")
        ).hexdigest()
        event = SecurityIncidentAssignmentEvent(
            event_id="assignment-event-" + fingerprint,
            assignment_id=assignment_id,
            actor_principal_id=actor,
            idempotency_fingerprint=fingerprint,
            from_status=current.status,
            to_status=next_status,
            action="INCIDENT_ASSIGNMENT_ACCEPTED" if accepted else "INCIDENT_ASSIGNMENT_DECLINED",
            occurred_at=now,
        )
        try:
            return self._assignments.transition(
                current=current, updated=updated, event=event,
                expected_revision=expected_revision, session=session,
            )
        except IncidentAssignmentConflictError:
            raise

    def accept(
        self, *, actor_principal_id: str, assignment_id: str,
        expected_revision: int, idempotency_key: str, session: object,
    ) -> SecurityIncidentAssignment:
        return self._respond(
            actor_principal_id=actor_principal_id, assignment_id=assignment_id,
            expected_revision=expected_revision, idempotency_key=idempotency_key,
            accepted=True, session=session,
        )

    def decline(
        self, *, actor_principal_id: str, assignment_id: str,
        expected_revision: int, idempotency_key: str, session: object,
    ) -> SecurityIncidentAssignment:
        return self._respond(
            actor_principal_id=actor_principal_id, assignment_id=assignment_id,
            expected_revision=expected_revision, idempotency_key=idempotency_key,
            accepted=False, session=session,
        )


__all__ = [
    "PERMISSION_CASE_TRIAGE", "PERMISSION_INCIDENT_ESCALATE",
    "SecurityIncidentEscalationError", "SecurityIncidentEscalationService",
]
