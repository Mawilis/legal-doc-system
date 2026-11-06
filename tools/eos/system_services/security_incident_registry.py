"""Caller-transaction security-incident intake registry.

This registry is append-only: it accepts initial sanitized intake evidence and
has no status transition, containment, recovery, or account-action authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.system_services.security_incident import (
    SecurityIncident, SecurityIncidentEvent, SecurityIncidentCategory,
)

COLLECTION = "system_security_incidents"
EVENT_COLLECTION = "system_security_incident_events"
PLATFORM_AUDIT_COLLECTION = "system_platform_audit_events"
PLATFORM_OUTBOX_COLLECTION = "system_platform_audit_outbox"
AUDIT_SCHEMA_VERSION = "WILSY-PLATFORM-AUDIT/V1"


class SecurityIncidentRegistryError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SecurityIncidentConflictError(SecurityIncidentRegistryError):
    pass


class SecurityIncidentNotFoundError(SecurityIncidentRegistryError):
    pass


class SecurityIncidentPersistenceError(SecurityIncidentRegistryError):
    pass


def _transaction(session: Any) -> None:
    try:
        marker = getattr(session, "in_transaction")
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise SecurityIncidentRegistryError("SECURITY_INCIDENT_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise SecurityIncidentRegistryError("SECURITY_INCIDENT_TRANSACTION_REQUIRED")


def _doc(value: SecurityIncident) -> dict[str, object]:
    return {
        "incident_id": value.incident_id,
        "tenant_id": value.tenant_id,
        "reporter_principal_id": value.reporter_principal_id,
        "idempotency_fingerprint": value.idempotency_fingerprint,
        "category": value.category.value,
        "observed_at": value.observed_at,
        "received_at": value.received_at,
        "revision": value.revision,
        "status": value.status,
    }


def _event_doc(value: SecurityIncidentEvent) -> dict[str, object]:
    return {
        "event_id": value.event_id,
        "incident_id": value.incident_id,
        "tenant_id": value.tenant_id,
        "actor_principal_id": value.actor_principal_id,
        "event_type": value.event_type,
        "occurred_at": value.occurred_at,
        "fingerprint": value.fingerprint,
    }


def _hydrate(raw: dict[str, Any]) -> SecurityIncident:
    for key in ("observed_at", "received_at"):
        value = raw.get(key)
        if isinstance(value, datetime) and value.tzinfo is None:
            raw[key] = value.replace(tzinfo=timezone.utc)
    return SecurityIncident(
        incident_id=raw["incident_id"],
        tenant_id=raw["tenant_id"],
        reporter_principal_id=raw["reporter_principal_id"],
        idempotency_fingerprint=raw["idempotency_fingerprint"],
        category=SecurityIncidentCategory(raw["category"]),
        observed_at=raw["observed_at"],
        received_at=raw["received_at"],
        revision=raw["revision"],
        status=raw["status"],
    )


class SecurityIncidentRegistry:
    """Append-only intake persistence; caller owns transaction and authorization."""

    def __init__(self, *, incidents: Any, events: Any) -> None:
        if incidents is None or events is None:
            raise SecurityIncidentRegistryError("SECURITY_INCIDENT_COLLECTION_REQUIRED")
        self._incidents = incidents
        self._events = events
        try:
            database = incidents.database
            self._audit_events = database[PLATFORM_AUDIT_COLLECTION]
            self._outbox = database[PLATFORM_OUTBOX_COLLECTION]
        except Exception as error:
            raise SecurityIncidentRegistryError("SECURITY_INCIDENT_AUDIT_STORAGE_REQUIRED") from error

    def ensure_indexes(self) -> None:
        self._incidents.create_index(
            [("incident_id", ASCENDING)], unique=True,
            name="security_incident_identity_unique",
        )
        self._incidents.create_index(
            [("tenant_id", ASCENDING), ("reporter_principal_id", ASCENDING),
             ("idempotency_fingerprint", ASCENDING)],
            unique=True, name="security_incident_reporter_idempotency_unique",
        )
        self._events.create_index(
            [("event_id", ASCENDING)], unique=True,
            name="security_incident_event_identity_unique",
        )
        self._events.create_index(
            [("incident_id", ASCENDING), ("event_type", ASCENDING)],
            unique=True, name="security_incident_initial_event_unique",
        )
        self._audit_events.create_index([("event_key", ASCENDING)], unique=True, name="system_platform_audit_event_key_unique")
        self._outbox.create_index([("event_key", ASCENDING)], unique=True, name="system_platform_audit_outbox_event_key_unique")
        self._outbox.create_index([("status", ASCENDING), ("created_at", ASCENDING)], name="system_platform_audit_outbox_pending")

    @staticmethod
    def _insert_or_verify(collection: Any, document: dict[str, object], *, session: Any) -> None:
        key = document["event_key"]
        try:
            existing = collection.find_one({"event_key": key}, session=session)
            if existing is not None:
                for field, expected in document.items():
                    if existing.get(field) != expected:
                        raise SecurityIncidentConflictError("SECURITY_INCIDENT_AUDIT_EVIDENCE_CONFLICT")
                return
            collection.insert_one(document, session=session)
        except SecurityIncidentRegistryError:
            raise
        except DuplicateKeyError as error:
            raise SecurityIncidentConflictError("SECURITY_INCIDENT_AUDIT_CONCURRENT_DUPLICATE") from error
        except PyMongoError as error:
            raise SecurityIncidentPersistenceError("SECURITY_INCIDENT_AUDIT_WRITE_FAILED") from error

    def record_platform_audit(self, *, incident: SecurityIncident, event: SecurityIncidentEvent, session: Any) -> None:
        """Persist independent platform audit evidence and outbox intent in the caller transaction."""
        _transaction(session)
        if (
            not isinstance(incident, SecurityIncident)
            or not isinstance(event, SecurityIncidentEvent)
            or event.incident_id != incident.incident_id
            or event.tenant_id != incident.tenant_id
            or event.actor_principal_id != incident.reporter_principal_id
            or event.event_type != "INCIDENT_REPORTED"
        ):
            raise SecurityIncidentRegistryError("SECURITY_INCIDENT_AUDIT_INPUT_INVALID")
        stored_event = self._events.find_one({"event_id": event.event_id}, session=session)
        if (
            stored_event is None
            or stored_event.get("incident_id") != incident.incident_id
            or stored_event.get("tenant_id") != incident.tenant_id
            or stored_event.get("actor_principal_id") != incident.reporter_principal_id
            or stored_event.get("fingerprint") != event.fingerprint
            or stored_event.get("event_type") != "INCIDENT_REPORTED"
        ):
            raise SecurityIncidentRegistryError("SECURITY_INCIDENT_IMMUTABLE_EVENT_REQUIRED")
        occurred_at_value = stored_event.get("occurred_at")
        if not isinstance(occurred_at_value, datetime):
            raise SecurityIncidentRegistryError("SECURITY_INCIDENT_IMMUTABLE_EVENT_INVALID")
        if occurred_at_value.tzinfo is None:
            occurred_at_value = occurred_at_value.replace(tzinfo=timezone.utc)
        occurred_at = occurred_at_value.isoformat()
        event_key = "system-services:" + event.event_id
        common: dict[str, object] = {
            "event_key": event_key,
            "schema_version": AUDIT_SCHEMA_VERSION,
            "event_type": event.event_type,
            "tenant_id": incident.tenant_id,
            "actor_principal_id": event.actor_principal_id,
            "target_id": incident.incident_id,
            "fingerprint": event.fingerprint,
            "occurred_at": occurred_at,
        }
        self._insert_or_verify(self._audit_events, common, session=session)
        self._insert_or_verify(self._outbox, {**common, "status": "PENDING", "attempts": 0, "created_at": occurred_at}, session=session)

    def create_or_replay(
        self, incident: SecurityIncident, event: SecurityIncidentEvent, *, session: Any
    ) -> SecurityIncident:
        _transaction(session)
        if (
            not isinstance(incident, SecurityIncident)
            or not isinstance(event, SecurityIncidentEvent)
            or event.incident_id != incident.incident_id
            or event.tenant_id != incident.tenant_id
            or event.actor_principal_id != incident.reporter_principal_id
            or event.event_type != "INCIDENT_REPORTED"
        ):
            raise SecurityIncidentRegistryError("SECURITY_INCIDENT_EVENT_MISMATCH")
        query = {
            "tenant_id": incident.tenant_id,
            "reporter_principal_id": incident.reporter_principal_id,
            "idempotency_fingerprint": incident.idempotency_fingerprint,
        }
        try:
            prior = self._incidents.find_one(query, session=session)
            if prior is not None:
                value = _hydrate(dict(prior))
                if value.incident_id != incident.incident_id or value.category is not incident.category:
                    raise SecurityIncidentConflictError("SECURITY_INCIDENT_IDEMPOTENCY_CONFLICT")
                prior_event = self._events.find_one(
                    {"incident_id": value.incident_id, "event_type": "INCIDENT_REPORTED"},
                    session=session,
                )
                if (
                    prior_event is None
                    or prior_event.get("fingerprint") != event.fingerprint
                    or prior_event.get("actor_principal_id") != value.reporter_principal_id
                ):
                    raise SecurityIncidentPersistenceError("SECURITY_INCIDENT_INITIAL_EVENT_MISSING_OR_INVALID")
                return value
            self._incidents.insert_one(_doc(incident), session=session)
            self._events.insert_one(_event_doc(event), session=session)
            return incident
        except SecurityIncidentRegistryError:
            raise
        except DuplicateKeyError as error:
            raise SecurityIncidentConflictError("SECURITY_INCIDENT_CONCURRENT_REPLAY") from error
        except PyMongoError as error:
            raise SecurityIncidentPersistenceError("SECURITY_INCIDENT_INTAKE_FAILED") from error

    def get_by_id(self, *, incident_id: str, session: Any) -> SecurityIncident:
        """Read one exact incident for an independently authorized SYSTEM caller."""
        _transaction(session)
        if not isinstance(incident_id, str) or not incident_id:
            raise SecurityIncidentRegistryError("SECURITY_INCIDENT_ID_INVALID")
        try:
            row = self._incidents.find_one({"incident_id": incident_id}, session=session)
            if row is None:
                raise SecurityIncidentNotFoundError("SECURITY_INCIDENT_NOT_FOUND")
            return _hydrate(dict(row))
        except SecurityIncidentRegistryError:
            raise
        except PyMongoError as error:
            raise SecurityIncidentPersistenceError("SECURITY_INCIDENT_READ_FAILED") from error

    def list_system_queue(self, *, session: Any, limit: int = 100) -> tuple[SecurityIncident, ...]:
        """Return a bounded sanitized incident queue; caller proves SYSTEM queue permission."""
        _transaction(session)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise SecurityIncidentRegistryError("SECURITY_INCIDENT_LIMIT_INVALID")
        try:
            rows = self._incidents.find({}, session=session).sort(
                [("received_at", 1), ("incident_id", 1)]
            ).limit(limit)
            return tuple(_hydrate(dict(row)) for row in rows)
        except PyMongoError as error:
            raise SecurityIncidentPersistenceError("SECURITY_INCIDENT_QUEUE_READ_FAILED") from error

    def list_own(
        self, *, tenant_id: str, principal_id: str, session: Any, limit: int = 50
    ) -> tuple[SecurityIncident, ...]:
        _transaction(session)
        if not 1 <= limit <= 100:
            raise SecurityIncidentRegistryError("SECURITY_INCIDENT_LIMIT_INVALID")
        try:
            rows = self._incidents.find(
                {"tenant_id": tenant_id, "reporter_principal_id": principal_id},
                session=session,
            ).sort([("received_at", -1), ("incident_id", -1)]).limit(limit)
            return tuple(_hydrate(dict(row)) for row in rows)
        except PyMongoError as error:
            raise SecurityIncidentPersistenceError("SECURITY_INCIDENT_READ_FAILED") from error


__all__ = [
    "COLLECTION", "EVENT_COLLECTION", "SecurityIncidentRegistry",
    "SecurityIncidentRegistryError", "SecurityIncidentConflictError",
    "SecurityIncidentNotFoundError", "SecurityIncidentPersistenceError",
    "PLATFORM_AUDIT_COLLECTION", "PLATFORM_OUTBOX_COLLECTION",
]
