"""Durable, caller-transaction-owned WILSY System Services case registry.

The registry stores sanitized case metadata and append-only transition events.
It does not authenticate actors, authorize commands, verify identity, send
notifications, reset credentials, or own transaction lifecycle.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.system_services.support_case import (
    SupportCase,
    SupportCaseEvent,
    SupportCaseScope,
    SupportCaseStatus,
)

VERSION: Final[str] = "v1.0.0-SYSTEM-SERVICES-CASE-REGISTRY"
CASE_COLLECTION: Final[str] = "system_service_cases"
EVENT_COLLECTION: Final[str] = "system_service_case_events"

CASE_INDEXES: Final = (
    ((( "case_id", ASCENDING),), True, "system_service_case_identity_unique"),
    ((("scope", ASCENDING), ("tenant_id", ASCENDING), ("status", ASCENDING), ("created_at", ASCENDING)), False, "system_service_case_scope_status_created"),
    ((("principal_id", ASCENDING), ("created_at", ASCENDING)), False, "system_service_case_principal_created"),
)
EVENT_INDEXES: Final = (
    ((( "event_id", ASCENDING),), True, "system_service_case_event_identity_unique"),
    ((("actor_principal_id", ASCENDING), ("idempotency_key", ASCENDING)), True, "system_service_case_actor_idempotency_unique"),
    ((("case_id", ASCENDING), ("idempotency_key", ASCENDING)), True, "system_service_case_event_idempotency_unique"),
    ((("case_id", ASCENDING), ("occurred_at", ASCENDING)), False, "system_service_case_event_timeline"),
)


class SupportCaseRegistryError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SupportCaseNotFoundError(SupportCaseRegistryError):
    pass


class SupportCaseConflictError(SupportCaseRegistryError):
    pass


class SupportCasePersistenceError(SupportCaseRegistryError):
    pass


def _require_transaction(session: Any) -> None:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise SupportCaseRegistryError("ACTIVE_TRANSACTION_REQUIRED")


def _target(collection: Any | None, collection_name: str) -> Any:
    if collection is not None:
        return collection
    from tools.eos.kernel import db as kernel_db
    database = kernel_db.get_database()
    if database is None:
        raise SupportCasePersistenceError("SYSTEM_SERVICES_DATABASE_UNAVAILABLE")
    return database[collection_name]


def _scope_query(case: SupportCase) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "scope": case.scope.value,
        "tenant_id": case.tenant_id,
    }


def _hydrate_case(row: Any) -> SupportCase:
    if not isinstance(row, dict):
        try:
            row = dict(row)
        except (TypeError, ValueError) as error:
            raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_RECORD_INVALID") from error
    row.pop("_id", None)
    # PyMongo decodes BSON datetimes as naive UTC unless tz_aware is enabled.
    for field in ("created_at", "updated_at"):
        value = row.get(field)
        if isinstance(value, datetime) and value.tzinfo is None:
            row[field] = value.replace(tzinfo=timezone.utc)
    try:
        return SupportCase.from_document(row)
    except (TypeError, ValueError) as error:
        raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_RECORD_INVALID") from error


class SupportCaseRegistry:
    """Persist case state and its append-only events in caller-owned transactions."""

    def __init__(self, *, cases: Any | None = None, events: Any | None = None) -> None:
        self._cases = cases
        self._events = events

    def ensure_indexes(self) -> None:
        """Install deterministic indexes at canonical startup, never per request."""
        try:
            cases = _target(self._cases, CASE_COLLECTION)
            events = _target(self._events, EVENT_COLLECTION)
            for keys, unique, name in CASE_INDEXES:
                cases.create_index(list(keys), unique=unique, name=name)
            for keys, unique, name in EVENT_INDEXES:
                events.create_index(list(keys), unique=unique, name=name)
        except PyMongoError as error:
            raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_INDEX_FAILED") from error

    def create(self, case: SupportCase, event: SupportCaseEvent, *, session: Any) -> SupportCase:
        """Insert one OPEN case and its first event atomically."""
        _require_transaction(session)
        if not isinstance(case, SupportCase) or case.status is not SupportCaseStatus.OPEN or case.revision != 0:
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_CREATE_INVALID")
        if (
            not isinstance(event, SupportCaseEvent)
            or event.case_id != case.case_id
            or event.from_status is not None
            or event.to_status is not SupportCaseStatus.OPEN
        ):
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_CREATE_EVENT_INVALID")
        try:
            case_collection = _target(self._cases, CASE_COLLECTION)
            event_collection = _target(self._events, EVENT_COLLECTION)
            prior_event = event_collection.find_one(
                {
                    "actor_principal_id": event.actor_principal_id,
                    "idempotency_key": event.idempotency_key,
                },
                session=session,
            )
            if prior_event is not None:
                prior_event.pop("_id", None)
                occurred = prior_event.get("occurred_at")
                if isinstance(occurred, datetime) and occurred.tzinfo is None:
                    prior_event["occurred_at"] = occurred.replace(tzinfo=timezone.utc)
                prior = SupportCaseEvent.from_document(prior_event)
                prior_case = self.get(
                    case_id=prior.case_id,
                    scope=case.scope,
                    tenant_id=case.tenant_id,
                    session=session,
                )
                if (
                    prior.action == event.action
                    and prior.to_status is SupportCaseStatus.OPEN
                    and prior.from_status is None
                    and prior_case.principal_id == case.principal_id
                    and prior_case.category is case.category
                ):
                    return prior_case
                raise SupportCaseConflictError("SYSTEM_SERVICES_CASE_CREATE_REPLAY_DIVERGED")
            case_collection.insert_one(case.to_document(), session=session)
            event_collection.insert_one(event.to_document(), session=session)
        except DuplicateKeyError as error:
            raise SupportCaseConflictError("SYSTEM_SERVICES_CASE_ALREADY_EXISTS_OR_REPLAYED") from error
        except PyMongoError as error:
            raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_CREATE_FAILED") from error
        return case

    def get(
        self,
        *,
        case_id: str,
        scope: SupportCaseScope,
        tenant_id: str | None = None,
        session: Any | None = None,
    ) -> SupportCase:
        """Read one exact scope-bound case; never infer tenant or cross-scope fallback."""
        if (
            not isinstance(case_id, str)
            or not case_id
            or case_id != case_id.strip()
            or len(case_id) > 256
            or any(ord(character) < 33 or ord(character) == 127 for character in case_id)
        ):
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_ID_INVALID")
        if not isinstance(scope, SupportCaseScope):
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_SCOPE_INVALID")
        if scope is SupportCaseScope.SYSTEM and tenant_id is not None:
            raise SupportCaseRegistryError("SYSTEM_CASE_MUST_NOT_BIND_TENANT")
        if scope is SupportCaseScope.TENANT and (not isinstance(tenant_id, str) or not tenant_id or tenant_id != tenant_id.strip()):
            raise SupportCaseRegistryError("TENANT_CASE_SCOPE_REQUIRED")
        query = {"case_id": case_id, "scope": scope.value, "tenant_id": tenant_id}
        try:
            row = _target(self._cases, CASE_COLLECTION).find_one(query, session=session)
        except PyMongoError as error:
            raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_READ_FAILED") from error
        if row is None:
            raise SupportCaseNotFoundError("SYSTEM_SERVICES_CASE_NOT_FOUND")
        value = _hydrate_case(row)
        if value.case_id != case_id or value.scope is not scope or value.tenant_id != tenant_id:
            raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_SCOPE_MISMATCH")
        return value

    def list_cases(
        self,
        *,
        scope: SupportCaseScope,
        tenant_id: str | None = None,
        principal_id: str | None = None,
        statuses: tuple[SupportCaseStatus, ...] = (),
        limit: int = 50,
        session: Any | None = None,
    ) -> tuple[SupportCase, ...]:
        """Return a bounded exact-scope queue projection; callers authorize first."""
        if not isinstance(scope, SupportCaseScope):
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_SCOPE_INVALID")
        if scope is SupportCaseScope.SYSTEM and tenant_id is not None:
            raise SupportCaseRegistryError("SYSTEM_CASE_MUST_NOT_BIND_TENANT")
        if scope is SupportCaseScope.TENANT and (
            not isinstance(tenant_id, str) or not tenant_id or tenant_id != tenant_id.strip()
        ):
            raise SupportCaseRegistryError("TENANT_CASE_SCOPE_REQUIRED")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_LIMIT_INVALID")
        if principal_id is not None and (
            not isinstance(principal_id, str) or not principal_id or principal_id != principal_id.strip()
        ):
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_PRINCIPAL_FILTER_INVALID")
        if not isinstance(statuses, tuple) or any(
            not isinstance(item, SupportCaseStatus) for item in statuses
        ):
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_STATUS_FILTER_INVALID")
        query: dict[str, object] = {
            "scope": scope.value,
            "tenant_id": tenant_id,
        }
        if principal_id is not None:
            query["principal_id"] = principal_id
        if statuses:
            query["status"] = {"$in": [item.value for item in statuses]}
        try:
            rows = _target(self._cases, CASE_COLLECTION).find(
                query, session=session
            ).sort([("created_at", DESCENDING), ("case_id", DESCENDING)]).limit(limit)
            return tuple(_hydrate_case(row) for row in rows)
        except PyMongoError as error:
            raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_QUEUE_READ_FAILED") from error

    def list_events(
        self,
        *,
        case_id: str,
        scope: SupportCaseScope,
        tenant_id: str | None = None,
        session: Any | None = None,
        limit: int = 100,
    ) -> tuple[SupportCaseEvent, ...]:
        """Return ordered event history only after exact-scope case existence is proven."""
        self.get(case_id=case_id, scope=scope, tenant_id=tenant_id, session=session)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 500:
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_EVENT_LIMIT_INVALID")
        try:
            rows = _target(self._events, EVENT_COLLECTION).find(
                {"case_id": case_id}, session=session
            ).sort([("occurred_at", ASCENDING), ("event_id", ASCENDING)]).limit(limit)
            values: list[SupportCaseEvent] = []
            for raw in rows:
                if not isinstance(raw, dict):
                    raw = dict(raw)
                raw.pop("_id", None)
                occurred = raw.get("occurred_at")
                if isinstance(occurred, datetime) and occurred.tzinfo is None:
                    raw["occurred_at"] = occurred.replace(tzinfo=timezone.utc)
                try:
                    event = SupportCaseEvent.from_document(raw)
                except (TypeError, ValueError) as error:
                    raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_EVENT_RECORD_INVALID") from error
                if event.case_id != case_id:
                    raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_EVENT_SCOPE_MISMATCH")
                values.append(event)
            return tuple(values)
        except PyMongoError as error:
            raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_HISTORY_READ_FAILED") from error

    def transition(
        self,
        *,
        current: SupportCase,
        next_status: SupportCaseStatus,
        event: SupportCaseEvent,
        expected_revision: int,
        session: Any,
    ) -> SupportCase:
        """CAS one status transition and append its event inside one transaction."""
        _require_transaction(session)
        if not isinstance(current, SupportCase) or expected_revision != current.revision:
            raise SupportCaseConflictError("SYSTEM_SERVICES_CASE_REVISION_INVALID")
        if (
            not isinstance(event, SupportCaseEvent)
            or event.case_id != current.case_id
            or event.from_status is not current.status
            or event.to_status is not next_status
        ):
            raise SupportCaseRegistryError("SYSTEM_SERVICES_CASE_EVENT_MISMATCH")
        updated = current.transition(next_status, observed_at=event.occurred_at)
        query = {
            **_scope_query(current),
            "status": current.status.value,
            "revision": expected_revision,
        }
        try:
            result = _target(self._cases, CASE_COLLECTION).replace_one(
                query,
                updated.to_document(),
                upsert=False,
                session=session,
            )
            if getattr(result, "matched_count", 0) != 1:
                raise SupportCaseConflictError("SYSTEM_SERVICES_CASE_CONCURRENT_TRANSITION")
            _target(self._events, EVENT_COLLECTION).insert_one(event.to_document(), session=session)
        except DuplicateKeyError as error:
            raise SupportCaseConflictError("SYSTEM_SERVICES_CASE_EVENT_REPLAYED") from error
        except PyMongoError as error:
            raise SupportCasePersistenceError("SYSTEM_SERVICES_CASE_TRANSITION_FAILED") from error
        return updated


__all__ = [
    "VERSION", "CASE_COLLECTION", "EVENT_COLLECTION", "SupportCaseRegistry",
    "SupportCaseRegistryError", "SupportCaseNotFoundError",
    "SupportCaseConflictError", "SupportCasePersistenceError",
]
