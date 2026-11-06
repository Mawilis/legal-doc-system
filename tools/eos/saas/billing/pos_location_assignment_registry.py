"""Durable POS location assignment authority registry.

The registry owns immutable assignment history and a CAS-guarded current
pointer. Callers own the Mongo session/transaction and must supply already
authenticated, independently authorized issuance/revocation decisions.
"""
from __future__ import annotations

from typing import Any
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.pos_location_assignment import POSLocationAssignment, POSLocationAssignmentStatus


HISTORY_COLLECTION = "pos_location_assignment_history"
CURRENT_COLLECTION = "pos_location_assignment_current"
HISTORY_INDEX = "pos_location_assignment_revision_unique"
CURRENT_INDEX = "pos_location_assignment_identity_unique"
IDEMPOTENCY_INDEX = "pos_location_assignment_idempotency_unique"


class POSLocationAssignmentRegistryError(RuntimeError):
    pass


class POSLocationAssignmentNotFound(POSLocationAssignmentRegistryError):
    pass


class POSLocationAssignmentConflict(POSLocationAssignmentRegistryError):
    pass


class POSLocationAssignmentUnavailable(POSLocationAssignmentRegistryError):
    pass


def _transaction(session: Any) -> Any:
    if session is None or not callable(getattr(session, "with_transaction", None)) or getattr(session, "has_ended", True):
        raise POSLocationAssignmentRegistryError("POS_LOCATION_LIVE_CALLER_SESSION_REQUIRED")
    return session


def ensure_indexes(history: Any, current: Any) -> None:
    try:
        history.create_index(
            [("tenant_id", ASCENDING), ("assignment_id", ASCENDING), ("revision", ASCENDING)],
            unique=True, name=HISTORY_INDEX,
        )
        history.create_index(
            [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
            unique=True, name=IDEMPOTENCY_INDEX,
        )
        current.create_index(
            [("tenant_id", ASCENDING), ("location_id", ASCENDING), ("principal_id", ASCENDING)],
            unique=True, name=CURRENT_INDEX,
        )
    except (AttributeError, PyMongoError) as error:
        raise POSLocationAssignmentUnavailable("POS_LOCATION_INDEX_AUTHORITY_UNAVAILABLE") from error


def _hydrate(document: dict) -> POSLocationAssignment:
    raw = dict(document)
    raw.pop("_id", None)
    try:
        value = POSLocationAssignment(
            tenant_id=raw["tenant_id"], location_id=raw["location_id"],
            principal_id=raw["principal_id"], assignment_id=raw["assignment_id"],
            revision=raw["revision"], status=POSLocationAssignmentStatus(raw["status"]),
            authority_reference=raw["authority_reference"],
            authority_fingerprint=raw["authority_fingerprint"],
            idempotency_key=raw["idempotency_key"],
            occurred_at=__import__("datetime").datetime.fromisoformat(raw["occurred_at"]),
            changed_by_principal_id=raw["changed_by_principal_id"], reason=raw.get("reason"),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise POSLocationAssignmentRegistryError("POS_LOCATION_PERSISTED_RECORD_INVALID") from error
    if raw != value.to_dict():
        raise POSLocationAssignmentRegistryError("POS_LOCATION_FINGERPRINT_OR_SCHEMA_INVALID")
    return value


def _current(tenant_id: str, location_id: str, principal_id: str, collection: Any, *, session: Any):
    row = collection.find_one(
        {"tenant_id": tenant_id, "location_id": location_id, "principal_id": principal_id},
        session=session,
    )
    return None if row is None else _hydrate(row)


def issue(assignment: POSLocationAssignment, history: Any, current: Any, *, session: Any) -> POSLocationAssignment:
    tx = _transaction(session)
    if assignment.revision != 0 or assignment.status is not POSLocationAssignmentStatus.ACTIVE:
        raise POSLocationAssignmentRegistryError("POS_LOCATION_INITIAL_ACTIVE_ASSIGNMENT_REQUIRED")
    existing = _current(assignment.tenant_id, assignment.location_id, assignment.principal_id, current, session=tx)
    if existing is not None:
        if existing.to_dict() == assignment.to_dict():
            return existing
        raise POSLocationAssignmentConflict("POS_LOCATION_ASSIGNMENT_ALREADY_EXISTS")
    try:
        history.insert_one(assignment.to_dict(), session=tx)
        current.insert_one(assignment.to_dict(), session=tx)
    except DuplicateKeyError as error:
        raise POSLocationAssignmentConflict("POS_LOCATION_ASSIGNMENT_REPLAY_CONFLICT") from error
    except PyMongoError as error:
        raise POSLocationAssignmentUnavailable("POS_LOCATION_PERSISTENCE_UNAVAILABLE") from error
    persisted = _current(assignment.tenant_id, assignment.location_id, assignment.principal_id, current, session=tx)
    if persisted is None or persisted.to_dict() != assignment.to_dict():
        raise POSLocationAssignmentRegistryError("POS_LOCATION_CREATE_CORRELATION_INVALID")
    return persisted


def resolve(tenant_id: str, location_id: str, principal_id: str, current: Any, *, session: Any) -> POSLocationAssignment:
    tx = _transaction(session)
    value = _current(tenant_id, location_id, principal_id, current, session=tx)
    if value is None or value.status is not POSLocationAssignmentStatus.ACTIVE:
        raise POSLocationAssignmentNotFound("POS_LOCATION_ACCESS_DENIED")
    return value


def revoke(*, tenant_id: str, location_id: str, principal_id: str, assignment_id: str,
           expected_revision: int, authority_reference: str, authority_fingerprint: str,
           idempotency_key: str, occurred_at, changed_by_principal_id: str, reason: str,
           history: Any, current: Any, session: Any) -> POSLocationAssignment:
    tx = _transaction(session)
    prior = resolve(tenant_id, location_id, principal_id, current, session=tx)
    if prior.assignment_id != assignment_id or prior.revision != expected_revision:
        raise POSLocationAssignmentConflict("POS_LOCATION_STALE_ASSIGNMENT_REVISION")
    next_value = POSLocationAssignment(
        tenant_id=tenant_id, location_id=location_id, principal_id=principal_id,
        assignment_id=assignment_id, revision=expected_revision + 1,
        status=POSLocationAssignmentStatus.REVOKED,
        authority_reference=authority_reference, authority_fingerprint=authority_fingerprint,
        idempotency_key=idempotency_key, occurred_at=occurred_at,
        changed_by_principal_id=changed_by_principal_id, reason=reason,
    )
    try:
        history.insert_one(next_value.to_dict(), session=tx)
        result = current.replace_one(prior.to_dict(), next_value.to_dict(), session=tx)
        if getattr(result, "matched_count", 0) != 1:
            raise POSLocationAssignmentConflict("POS_LOCATION_REVOCATION_CAS_CONFLICT")
    except DuplicateKeyError as error:
        raise POSLocationAssignmentConflict("POS_LOCATION_REVOCATION_REPLAY_CONFLICT") from error
    except PyMongoError as error:
        raise POSLocationAssignmentUnavailable("POS_LOCATION_PERSISTENCE_UNAVAILABLE") from error
    persisted = _current(tenant_id, location_id, principal_id, current, session=tx)
    if persisted is None or persisted.to_dict() != next_value.to_dict():
        raise POSLocationAssignmentRegistryError("POS_LOCATION_REVOCATION_CORRELATION_INVALID")
    return persisted


class POSLocationAssignmentRegistry:
    ensure_indexes = staticmethod(ensure_indexes)
    issue = staticmethod(issue)
    resolve = staticmethod(resolve)
    revoke = staticmethod(revoke)


__all__ = [
    "CURRENT_COLLECTION", "HISTORY_COLLECTION", "POSLocationAssignmentConflict",
    "POSLocationAssignmentNotFound", "POSLocationAssignmentRegistry",
    "POSLocationAssignmentRegistryError", "POSLocationAssignmentUnavailable",
]
