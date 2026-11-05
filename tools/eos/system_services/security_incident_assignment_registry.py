"""Revision-guarded responder assignment registry with immutable event history."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.system_services.security_incident_assignment import (
    SecurityIncidentAssignment, SecurityIncidentAssignmentEvent,
    SecurityIncidentAssignmentStatus,
)

COLLECTION = "system_security_incident_assignments"
EVENT_COLLECTION = "system_security_incident_assignment_events"


class IncidentAssignmentRegistryError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class IncidentAssignmentConflictError(IncidentAssignmentRegistryError):
    pass


class IncidentAssignmentNotFoundError(IncidentAssignmentRegistryError):
    pass


class IncidentAssignmentPersistenceError(IncidentAssignmentRegistryError):
    pass


def _require_transaction(session: Any) -> None:
    try:
        active = getattr(session, "in_transaction")
        active = active() if callable(active) else active
    except Exception as error:
        raise IncidentAssignmentRegistryError("INCIDENT_ASSIGNMENT_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise IncidentAssignmentRegistryError("INCIDENT_ASSIGNMENT_TRANSACTION_REQUIRED")


def _doc(value: SecurityIncidentAssignment) -> dict[str, object]:
    return {
        "assignment_id": value.assignment_id,
        "incident_id": value.incident_id,
        "tenant_id": value.tenant_id,
        "reporter_principal_id": value.reporter_principal_id,
        "assigned_by_principal_id": value.assigned_by_principal_id,
        "assigned_to_principal_id": value.assigned_to_principal_id,
        "status": value.status.value,
        "revision": value.revision,
        "created_at": value.created_at,
        "updated_at": value.updated_at,
        "idempotency_fingerprint": value.idempotency_fingerprint,
    }


def _event_doc(value: SecurityIncidentAssignmentEvent) -> dict[str, object]:
    return {
        "event_id": value.event_id,
        "assignment_id": value.assignment_id,
        "actor_principal_id": value.actor_principal_id,
        "idempotency_fingerprint": value.idempotency_fingerprint,
        "from_status": None if value.from_status is None else value.from_status.value,
        "to_status": value.to_status.value,
        "action": value.action,
        "occurred_at": value.occurred_at,
    }


def _hydrate(raw: dict[str, Any]) -> SecurityIncidentAssignment:
    for key in ("created_at", "updated_at"):
        if isinstance(raw.get(key), datetime) and raw[key].tzinfo is None:
            raw[key] = raw[key].replace(tzinfo=timezone.utc)
    return SecurityIncidentAssignment(
        assignment_id=raw["assignment_id"], incident_id=raw["incident_id"],
        tenant_id=raw["tenant_id"], reporter_principal_id=raw["reporter_principal_id"],
        assigned_by_principal_id=raw["assigned_by_principal_id"],
        assigned_to_principal_id=raw["assigned_to_principal_id"],
        status=SecurityIncidentAssignmentStatus(raw["status"]),
        revision=raw["revision"], created_at=raw["created_at"],
        updated_at=raw["updated_at"],
        idempotency_fingerprint=raw["idempotency_fingerprint"],
    )


class SecurityIncidentAssignmentRegistry:
    def __init__(self, *, assignments: Any, events: Any) -> None:
        if assignments is None or events is None:
            raise IncidentAssignmentRegistryError("INCIDENT_ASSIGNMENT_COLLECTION_REQUIRED")
        self._assignments = assignments
        self._events = events

    def ensure_indexes(self) -> None:
        self._assignments.create_index([("assignment_id", ASCENDING)], unique=True, name="incident_assignment_identity_unique")
        self._assignments.create_index([("incident_id", ASCENDING)], unique=True, name="incident_assignment_one_owner_unique")
        self._assignments.create_index([("idempotency_fingerprint", ASCENDING)], unique=True, name="incident_assignment_idempotency_unique")
        self._events.create_index([("event_id", ASCENDING)], unique=True, name="incident_assignment_event_identity_unique")
        self._events.create_index([("idempotency_fingerprint", ASCENDING)], unique=True, name="incident_assignment_event_idempotency_unique")

    def get(self, *, assignment_id: str, session: Any) -> SecurityIncidentAssignment:
        _require_transaction(session)
        try:
            row = self._assignments.find_one({"assignment_id": assignment_id}, session=session)
        except PyMongoError as error:
            raise IncidentAssignmentPersistenceError("INCIDENT_ASSIGNMENT_READ_FAILED") from error
        if row is None:
            raise IncidentAssignmentNotFoundError("INCIDENT_ASSIGNMENT_NOT_FOUND")
        return _hydrate(dict(row))

    def get_for_incident(self, *, incident_id: str, session: Any) -> SecurityIncidentAssignment | None:
        _require_transaction(session)
        try:
            row = self._assignments.find_one({"incident_id": incident_id}, session=session)
            return None if row is None else _hydrate(dict(row))
        except PyMongoError as error:
            raise IncidentAssignmentPersistenceError("INCIDENT_ASSIGNMENT_READ_FAILED") from error

    def create(self, value: SecurityIncidentAssignment, event: SecurityIncidentAssignmentEvent, *, session: Any) -> SecurityIncidentAssignment:
        _require_transaction(session)
        if (
            not isinstance(value, SecurityIncidentAssignment)
            or not isinstance(event, SecurityIncidentAssignmentEvent)
            or event.assignment_id != value.assignment_id
            or event.from_status is not None
            or event.to_status is not SecurityIncidentAssignmentStatus.PENDING_ACCEPTANCE
            or event.actor_principal_id != value.assigned_by_principal_id
            or event.action != "INCIDENT_RESPONDER_ASSIGNED"
        ):
            raise IncidentAssignmentRegistryError("INCIDENT_ASSIGNMENT_EVENT_MISMATCH")
        try:
            prior = self._assignments.find_one(
                {"idempotency_fingerprint": value.idempotency_fingerprint},
                session=session,
            )
            if prior is not None:
                existing = _hydrate(dict(prior))
                if (
                    existing.assignment_id != value.assignment_id
                    or existing.incident_id != value.incident_id
                    or existing.assigned_to_principal_id != value.assigned_to_principal_id
                    or existing.assigned_by_principal_id != value.assigned_by_principal_id
                ):
                    raise IncidentAssignmentConflictError("INCIDENT_ASSIGNMENT_IDEMPOTENCY_CONFLICT")
                prior_event = self._events.find_one(
                    {"assignment_id": existing.assignment_id, "from_status": None},
                    session=session,
                )
                if (
                    prior_event is None
                    or prior_event.get("idempotency_fingerprint") != event.idempotency_fingerprint
                ):
                    raise IncidentAssignmentPersistenceError("INCIDENT_ASSIGNMENT_INITIAL_EVENT_INVALID")
                return existing
            self._assignments.insert_one(_doc(value), session=session)
            self._events.insert_one(_event_doc(event), session=session)
            return value
        except DuplicateKeyError as error:
            raise IncidentAssignmentConflictError("INCIDENT_ALREADY_ASSIGNED_OR_REPLAYED") from error
        except PyMongoError as error:
            raise IncidentAssignmentPersistenceError("INCIDENT_ASSIGNMENT_CREATE_FAILED") from error

    def transition(self, *, current: SecurityIncidentAssignment, updated: SecurityIncidentAssignment, event: SecurityIncidentAssignmentEvent, expected_revision: int, session: Any) -> SecurityIncidentAssignment:
        _require_transaction(session)
        if (
            updated.assignment_id != current.assignment_id
            or updated.revision != expected_revision + 1
            or current.revision != expected_revision
            or event.assignment_id != current.assignment_id
            or event.from_status is not current.status
            or event.to_status is not updated.status
            or current.status is not SecurityIncidentAssignmentStatus.PENDING_ACCEPTANCE
            or updated.status not in {
                SecurityIncidentAssignmentStatus.ACCEPTED,
                SecurityIncidentAssignmentStatus.DECLINED,
            }
            or updated.incident_id != current.incident_id
            or updated.tenant_id != current.tenant_id
            or updated.reporter_principal_id != current.reporter_principal_id
            or updated.assigned_by_principal_id != current.assigned_by_principal_id
            or updated.assigned_to_principal_id != current.assigned_to_principal_id
            or updated.created_at != current.created_at
            or updated.idempotency_fingerprint != current.idempotency_fingerprint
            or updated.updated_at < current.updated_at
            or event.actor_principal_id != current.assigned_to_principal_id
            or event.action != (
                "INCIDENT_ASSIGNMENT_ACCEPTED"
                if updated.status is SecurityIncidentAssignmentStatus.ACCEPTED
                else "INCIDENT_ASSIGNMENT_DECLINED"
            )
            or isinstance(expected_revision, bool)
            or not isinstance(expected_revision, int)
            or expected_revision < 0
        ):
            raise IncidentAssignmentConflictError("INCIDENT_ASSIGNMENT_REVISION_OR_EVENT_INVALID")
        try:
            result = self._assignments.replace_one(
                {"assignment_id": current.assignment_id, "revision": expected_revision, "status": current.status.value},
                _doc(updated), upsert=False, session=session,
            )
            if getattr(result, "matched_count", 0) != 1:
                raise IncidentAssignmentConflictError("INCIDENT_ASSIGNMENT_STALE_REVISION")
            self._events.insert_one(_event_doc(event), session=session)
            return updated
        except DuplicateKeyError as error:
            raise IncidentAssignmentConflictError("INCIDENT_ASSIGNMENT_EVENT_REPLAYED") from error
        except PyMongoError as error:
            raise IncidentAssignmentPersistenceError("INCIDENT_ASSIGNMENT_TRANSITION_FAILED") from error


__all__ = [
    "COLLECTION", "EVENT_COLLECTION", "SecurityIncidentAssignmentRegistry",
    "IncidentAssignmentRegistryError", "IncidentAssignmentConflictError",
    "IncidentAssignmentNotFoundError", "IncidentAssignmentPersistenceError",
]
