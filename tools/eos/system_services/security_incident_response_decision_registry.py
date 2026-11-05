"""Caller-transaction-owned persistence for independent response decisions."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from .security_incident_response_decision import (
    SecurityIncidentResponseAction,
    SecurityIncidentResponseDecision,
    SecurityIncidentResponseDecisionError,
    SecurityIncidentResponseDecisionStatus,
)

COLLECTION: Final[str] = "system_security_incident_response_decisions"
EVENT_COLLECTION: Final[str] = "system_security_incident_response_decision_events"
PLATFORM_AUDIT_COLLECTION: Final[str] = "system_platform_audit_events"
PLATFORM_OUTBOX_COLLECTION: Final[str] = "system_platform_audit_outbox"
AUDIT_SCHEMA_VERSION: Final[str] = "WILSY-PLATFORM-AUDIT/V1"


class SecurityIncidentResponseDecisionRegistryError(RuntimeError):
    """Stable fail-closed decision persistence error."""


class SecurityIncidentResponseDecisionConflictError(SecurityIncidentResponseDecisionRegistryError):
    """Decision identity or expected revision conflicts with durable state."""


def _require_transaction(session: Any) -> None:
    try:
        marker = getattr(session, "in_transaction")
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise SecurityIncidentResponseDecisionRegistryError(
            "RESPONSE_DECISION_TRANSACTION_REQUIRED"
        ) from error
    if active is not True:
        raise SecurityIncidentResponseDecisionRegistryError(
            "RESPONSE_DECISION_TRANSACTION_REQUIRED"
        )


def _document(value: SecurityIncidentResponseDecision) -> dict[str, object]:
    return {
        "decision_id": value.decision_id,
        "incident_id": value.incident_id,
        "tenant_id": value.tenant_id,
        "target_principal_id": value.target_principal_id,
        "action": value.action.value,
        "requested_by_principal_id": value.requested_by_principal_id,
        "requested_at": value.requested_at,
        "request_evidence_reference": value.request_evidence_reference,
        "target_assignment_id": value.target_assignment_id,
        "target_permission_id": value.target_permission_id,
        "status": value.status.value,
        "revision": value.revision,
        "decided_by_principal_id": value.decided_by_principal_id,
        "decided_at": value.decided_at,
        "decision_evidence_reference": value.decision_evidence_reference,
    }


def _hydrate(raw: dict[str, Any]) -> SecurityIncidentResponseDecision:
    for key in ("requested_at", "decided_at"):
        value = raw.get(key)
        if isinstance(value, datetime) and value.tzinfo is None:
            raw[key] = value.replace(tzinfo=timezone.utc)
    return SecurityIncidentResponseDecision(
        decision_id=raw["decision_id"],
        incident_id=raw["incident_id"],
        tenant_id=raw["tenant_id"],
        target_principal_id=raw["target_principal_id"],
        action=SecurityIncidentResponseAction(raw["action"]),
        requested_by_principal_id=raw["requested_by_principal_id"],
        requested_at=raw["requested_at"],
        request_evidence_reference=raw["request_evidence_reference"],
        target_assignment_id=raw.get("target_assignment_id"),
        target_permission_id=raw.get("target_permission_id"),
        status=SecurityIncidentResponseDecisionStatus(raw["status"]),
        revision=raw["revision"],
        decided_by_principal_id=raw.get("decided_by_principal_id"),
        decided_at=raw.get("decided_at"),
        decision_evidence_reference=raw.get("decision_evidence_reference"),
    )


def _event(value: SecurityIncidentResponseDecision, *, event_type: str, actor: str, occurred_at: datetime) -> dict[str, object]:
    payload = {
        "decision_id": value.decision_id,
        "revision": value.revision,
        "event_type": event_type,
        "actor_principal_id": actor,
        "occurred_at": occurred_at.astimezone(timezone.utc).isoformat(),
        "decision_fingerprint": hashlib.sha3_256(
            json.dumps(_document(value), sort_keys=True, default=str, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    payload["event_id"] = f"{value.decision_id}:revision:{value.revision}"
    return payload


class SecurityIncidentResponseDecisionRegistry:
    """Persist decision projection, immutable history, and independent audit intent."""

    def __init__(self, *, decisions: Any, events: Any, audit_events: Any, outbox: Any) -> None:
        if any(item is None for item in (decisions, events, audit_events, outbox)):
            raise SecurityIncidentResponseDecisionRegistryError("RESPONSE_DECISION_STORAGE_REQUIRED")
        self._decisions = decisions
        self._events = events
        self._audit_events = audit_events
        self._outbox = outbox

    def ensure_indexes(self) -> None:
        self._decisions.create_index(
            [("decision_id", ASCENDING)], unique=True,
            name="system_response_decision_identity_unique",
        )
        self._decisions.create_index(
            [("incident_id", ASCENDING), ("tenant_id", ASCENDING), ("target_principal_id", ASCENDING)],
            name="system_response_decision_incident_target",
        )
        self._events.create_index(
            [("event_id", ASCENDING)], unique=True,
            name="system_response_decision_event_identity_unique",
        )
        self._events.create_index(
            [("decision_id", ASCENDING), ("revision", ASCENDING)], unique=True,
            name="system_response_decision_revision_unique",
        )
        self._audit_events.create_index(
            [("event_key", ASCENDING)], unique=True,
            name="system_platform_audit_event_key_unique",
        )
        self._outbox.create_index(
            [("event_key", ASCENDING)], unique=True,
            name="system_platform_audit_outbox_event_key_unique",
        )

    def _verify_event_and_audit(
        self,
        value: SecurityIncidentResponseDecision,
        *,
        event_type: str,
        actor: str,
        occurred_at: datetime,
        session: Any,
    ) -> None:
        event = _event(value, event_type=event_type, actor=actor, occurred_at=occurred_at)
        stored_event = self._events.find_one({"event_id": event["event_id"]}, session=session)
        if stored_event is None or any(stored_event.get(key) != expected for key, expected in event.items()):
            raise SecurityIncidentResponseDecisionConflictError("RESPONSE_DECISION_EVENT_REPLAY_CONFLICT")
        event_key = "system-services-response-decision:" + str(event["event_id"])
        common = {
            "event_key": event_key,
            "schema_version": AUDIT_SCHEMA_VERSION,
            "event_type": event_type,
            "tenant_id": value.tenant_id,
            "actor_principal_id": actor,
            "target_id": value.decision_id,
            "fingerprint": event["decision_fingerprint"],
            "occurred_at": event["occurred_at"],
        }
        stored_audit = self._audit_events.find_one({"event_key": event_key}, session=session)
        stored_outbox = self._outbox.find_one({"event_key": event_key}, session=session)
        if (
            stored_audit is None
            or any(stored_audit.get(key) != expected for key, expected in common.items())
            or stored_outbox is None
            or any(stored_outbox.get(key) != expected for key, expected in common.items())
            or stored_outbox.get("status") != "PENDING"
            or stored_outbox.get("attempts") != 0
        ):
            raise SecurityIncidentResponseDecisionConflictError("RESPONSE_DECISION_AUDIT_REPLAY_CONFLICT")

    def _persist_event_and_audit(
        self,
        value: SecurityIncidentResponseDecision,
        *,
        event_type: str,
        actor: str,
        occurred_at: datetime,
        session: Any,
    ) -> None:
        event = _event(value, event_type=event_type, actor=actor, occurred_at=occurred_at)
        try:
            self._events.insert_one(event, session=session)
            event_key = "system-services-response-decision:" + str(event["event_id"])
            common = {
                "event_key": event_key,
                "schema_version": AUDIT_SCHEMA_VERSION,
                "event_type": event_type,
                "tenant_id": value.tenant_id,
                "actor_principal_id": actor,
                "target_id": value.decision_id,
                "fingerprint": event["decision_fingerprint"],
                "occurred_at": event["occurred_at"],
            }
            self._audit_events.insert_one(common, session=session)
            self._outbox.insert_one(
                {**common, "status": "PENDING", "attempts": 0, "created_at": event["occurred_at"]},
                session=session,
            )
        except DuplicateKeyError as error:
            raise SecurityIncidentResponseDecisionConflictError(
                "RESPONSE_DECISION_EVENT_DUPLICATE"
            ) from error
        except PyMongoError as error:
            raise SecurityIncidentResponseDecisionRegistryError(
                "RESPONSE_DECISION_EVENT_PERSISTENCE_FAILED"
            ) from error

    def create(self, value: SecurityIncidentResponseDecision, *, session: Any) -> SecurityIncidentResponseDecision:
        _require_transaction(session)
        if not isinstance(value, SecurityIncidentResponseDecision) or value.revision != 0:
            raise SecurityIncidentResponseDecisionRegistryError("RESPONSE_DECISION_REQUEST_INVALID")
        document = _document(value)
        try:
            prior = self._decisions.find_one({"decision_id": value.decision_id}, session=session)
            if prior is not None:
                current = _hydrate(dict(prior))
                immutable_request = (
                    "decision_id", "incident_id", "tenant_id", "target_principal_id",
                    "action", "requested_by_principal_id", "requested_at",
                    "request_evidence_reference", "target_assignment_id", "target_permission_id",
                )
                if any(getattr(current, field) != getattr(value, field) for field in immutable_request):
                    raise SecurityIncidentResponseDecisionConflictError(
                        "RESPONSE_DECISION_IDENTITY_CONFLICT"
                    )
                self._verify_event_and_audit(
                    value,
                    event_type="SECURITY_INCIDENT_RESPONSE_REQUESTED",
                    actor=value.requested_by_principal_id,
                    occurred_at=value.requested_at,
                    session=session,
                )
                return current
            self._decisions.insert_one(document, session=session)
            self._persist_event_and_audit(
                value,
                event_type="SECURITY_INCIDENT_RESPONSE_REQUESTED",
                actor=value.requested_by_principal_id,
                occurred_at=value.requested_at,
                session=session,
            )
            return value
        except SecurityIncidentResponseDecisionRegistryError:
            raise
        except DuplicateKeyError as error:
            raise SecurityIncidentResponseDecisionConflictError(
                "RESPONSE_DECISION_CONCURRENT_DUPLICATE"
            ) from error
        except PyMongoError as error:
            raise SecurityIncidentResponseDecisionRegistryError(
                "RESPONSE_DECISION_CREATE_FAILED"
            ) from error

    def decide(
        self,
        decision_id: str,
        *,
        approved: bool,
        decided_by_principal_id: str,
        decided_at: datetime,
        decision_evidence_reference: str,
        expected_revision: int,
        session: Any,
    ) -> SecurityIncidentResponseDecision:
        _require_transaction(session)
        try:
            raw = self._decisions.find_one({"decision_id": decision_id}, session=session)
            if raw is None:
                raise SecurityIncidentResponseDecisionRegistryError("RESPONSE_DECISION_NOT_FOUND")
            current = _hydrate(dict(raw))
            desired_status = (
                SecurityIncidentResponseDecisionStatus.APPROVED
                if approved else SecurityIncidentResponseDecisionStatus.REJECTED
            )
            if current.revision == 1:
                if (
                    current.status is desired_status
                    and current.decided_by_principal_id == decided_by_principal_id
                    and current.decided_at == decided_at.astimezone(timezone.utc)
                    and current.decision_evidence_reference == decision_evidence_reference
                    and expected_revision == 0
                ):
                    self._verify_event_and_audit(
                        current,
                        event_type=(
                            "SECURITY_INCIDENT_RESPONSE_APPROVED"
                            if approved else "SECURITY_INCIDENT_RESPONSE_REJECTED"
                        ),
                        actor=decided_by_principal_id,
                        occurred_at=current.decided_at,  # type: ignore[arg-type]
                        session=session,
                    )
                    return current
                raise SecurityIncidentResponseDecisionConflictError(
                    "RESPONSE_DECISION_REVISION_CONFLICT"
                )
            updated = current.decide(
                approved=approved,
                decided_by_principal_id=decided_by_principal_id,
                decided_at=decided_at,
                decision_evidence_reference=decision_evidence_reference,
                expected_revision=expected_revision,
            )
            result = self._decisions.update_one(
                {
                    "decision_id": decision_id,
                    "revision": expected_revision,
                    "status": SecurityIncidentResponseDecisionStatus.PENDING.value,
                },
                {"$set": _document(updated)},
                session=session,
            )
            if result.matched_count != 1:
                raise SecurityIncidentResponseDecisionConflictError(
                    "RESPONSE_DECISION_REVISION_CONFLICT"
                )
            self._persist_event_and_audit(
                updated,
                event_type=(
                    "SECURITY_INCIDENT_RESPONSE_APPROVED"
                    if approved else "SECURITY_INCIDENT_RESPONSE_REJECTED"
                ),
                actor=decided_by_principal_id,
                occurred_at=updated.decided_at,  # type: ignore[arg-type]
                session=session,
            )
            return updated
        except (SecurityIncidentResponseDecisionRegistryError, SecurityIncidentResponseDecisionConflictError):
            raise
        except SecurityIncidentResponseDecisionError as error:
            raise SecurityIncidentResponseDecisionConflictError(error.args[0]) from error
        except DuplicateKeyError as error:
            raise SecurityIncidentResponseDecisionConflictError(
                "RESPONSE_DECISION_CONCURRENT_DUPLICATE"
            ) from error
        except PyMongoError as error:
            raise SecurityIncidentResponseDecisionRegistryError(
                "RESPONSE_DECISION_UPDATE_FAILED"
            ) from error


__all__ = [
    "COLLECTION", "EVENT_COLLECTION", "PLATFORM_AUDIT_COLLECTION",
    "PLATFORM_OUTBOX_COLLECTION", "SecurityIncidentResponseDecisionRegistry",
    "SecurityIncidentResponseDecisionRegistryError",
    "SecurityIncidentResponseDecisionConflictError",
]
