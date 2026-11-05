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

    def find(self, decision_id: str, *, session: Any) -> SecurityIncidentResponseDecision | None:
        """Read an optional decision without hiding persistence failures."""
        _require_transaction(session)
        if not isinstance(decision_id, str) or not decision_id or decision_id != decision_id.strip():
            raise SecurityIncidentResponseDecisionRegistryError("RESPONSE_DECISION_ID_INVALID")
        try:
            raw = self._decisions.find_one({"decision_id": decision_id}, session=session)
            return _hydrate(dict(raw)) if raw is not None else None
        except PyMongoError as error:
            raise SecurityIncidentResponseDecisionRegistryError("RESPONSE_DECISION_READ_FAILED") from error

    def get(self, decision_id: str, *, session: Any) -> SecurityIncidentResponseDecision:
        """Read one decision only inside the caller-owned transaction."""
        _require_transaction(session)
        if not isinstance(decision_id, str) or not decision_id or decision_id != decision_id.strip():
            raise SecurityIncidentResponseDecisionRegistryError("RESPONSE_DECISION_ID_INVALID")
        try:
            raw = self._decisions.find_one({"decision_id": decision_id}, session=session)
            if raw is None:
                raise SecurityIncidentResponseDecisionRegistryError("RESPONSE_DECISION_NOT_FOUND")
            return _hydrate(dict(raw))
        except SecurityIncidentResponseDecisionRegistryError:
            raise
        except PyMongoError as error:
            raise SecurityIncidentResponseDecisionRegistryError("RESPONSE_DECISION_READ_FAILED") from error

    @staticmethod
    def _execution_idempotency_fingerprint(value: str) -> str:
        if not isinstance(value, str) or not value or value != value.strip() or "*" in value:
            raise SecurityIncidentResponseDecisionRegistryError("RESPONSE_EXECUTION_IDEMPOTENCY_INVALID")
        return hashlib.sha3_256(value.encode("utf-8")).hexdigest()

    def find_execution(
        self,
        *,
        decision: SecurityIncidentResponseDecision,
        actor_principal_id: str,
        idempotency_key: str,
        session: Any,
    ) -> dict[str, Any] | None:
        """Resolve one exact execution receipt for safe timestamp-stable replay."""
        _require_transaction(session)
        key_fingerprint = self._execution_idempotency_fingerprint(idempotency_key)
        try:
            event = self._events.find_one(
                {"decision_id": decision.decision_id, "revision": 2},
                session=session,
            )
            if event is None:
                return None
            if (
                event.get("event_type") != "SECURITY_INCIDENT_RESPONSE_EXECUTED"
                or event.get("actor_principal_id") != actor_principal_id
                or event.get("execution_idempotency_fingerprint") != key_fingerprint
            ):
                raise SecurityIncidentResponseDecisionConflictError(
                    "RESPONSE_EXECUTION_REPLAY_CONFLICT"
                )
            occurred_at = event.get("occurred_at")
            payload = {
                "decision_id": decision.decision_id,
                "incident_id": decision.incident_id,
                "tenant_id": decision.tenant_id,
                "target_principal_id": decision.target_principal_id,
                "action": decision.action.value,
                "target_assignment_id": decision.target_assignment_id,
                "target_permission_id": decision.target_permission_id,
                "actor_principal_id": actor_principal_id,
                "execution_idempotency_fingerprint": key_fingerprint,
                "occurred_at": occurred_at,
                "result_status": event.get("result_status"),
                "result_revision": event.get("result_revision"),
            }
            expected_fingerprint = hashlib.sha3_256(
                json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
            ).hexdigest()
            if event.get("decision_fingerprint") != expected_fingerprint:
                raise SecurityIncidentResponseDecisionConflictError(
                    "RESPONSE_EXECUTION_FINGERPRINT_INVALID"
                )
            event_key = "system-services-response-execution:" + decision.decision_id + ":revision:2"
            common = {
                "event_key": event_key,
                "schema_version": AUDIT_SCHEMA_VERSION,
                "event_type": event["event_type"],
                "tenant_id": decision.tenant_id,
                "actor_principal_id": actor_principal_id,
                "target_id": decision.decision_id,
                "fingerprint": event["decision_fingerprint"],
                "occurred_at": event["occurred_at"],
            }
            audit = self._audit_events.find_one({"event_key": event_key}, session=session)
            outbox = self._outbox.find_one({"event_key": event_key}, session=session)
            if (
                audit is None
                or any(audit.get(key) != expected for key, expected in common.items())
                or outbox is None
                or any(outbox.get(key) != expected for key, expected in common.items())
                or outbox.get("status") != "PENDING"
                or outbox.get("attempts") != 0
            ):
                raise SecurityIncidentResponseDecisionConflictError(
                    "RESPONSE_EXECUTION_AUDIT_REPLAY_CONFLICT"
                )
            return dict(event)
        except (SecurityIncidentResponseDecisionRegistryError, SecurityIncidentResponseDecisionConflictError):
            raise
        except PyMongoError as error:
            raise SecurityIncidentResponseDecisionRegistryError(
                "RESPONSE_EXECUTION_READ_FAILED"
            ) from error

    def record_execution(
        self,
        *,
        decision: SecurityIncidentResponseDecision,
        actor_principal_id: str,
        idempotency_key: str,
        occurred_at: datetime,
        result_status: str,
        result_revision: int,
        session: Any,
    ) -> dict[str, Any]:
        """Atomically record execution evidence, platform audit, and pending outbox intent."""
        _require_transaction(session)
        if (
            decision.status is not SecurityIncidentResponseDecisionStatus.APPROVED
            or decision.revision != 1
            or decision.action is not SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION
            or decision.decided_at is None
            or not isinstance(actor_principal_id, str)
            or not actor_principal_id
            or actor_principal_id != actor_principal_id.strip()
            or actor_principal_id in {
                decision.requested_by_principal_id,
                decision.decided_by_principal_id,
                decision.target_principal_id,
            }
            or result_status != "REVOKED"
            or result_revision != 2
            or not isinstance(occurred_at, datetime)
            or occurred_at.tzinfo is None
            or occurred_at.utcoffset() is None
            or occurred_at < decision.decided_at
            or not isinstance(result_status, str)
            or not result_status
            or not isinstance(result_revision, int)
            or isinstance(result_revision, bool)
            or result_revision < 1
        ):
            raise SecurityIncidentResponseDecisionConflictError(
                "RESPONSE_EXECUTION_EVIDENCE_INVALID"
            )
        key_fingerprint = self._execution_idempotency_fingerprint(idempotency_key)
        event_key = "system-services-response-execution:" + decision.decision_id + ":revision:2"
        payload = {
            "decision_id": decision.decision_id,
            "incident_id": decision.incident_id,
            "tenant_id": decision.tenant_id,
            "target_principal_id": decision.target_principal_id,
            "action": decision.action.value,
            "target_assignment_id": decision.target_assignment_id,
            "target_permission_id": decision.target_permission_id,
            "actor_principal_id": actor_principal_id,
            "execution_idempotency_fingerprint": key_fingerprint,
            "occurred_at": occurred_at.astimezone(timezone.utc).isoformat(),
            "result_status": result_status,
            "result_revision": result_revision,
        }
        fingerprint = hashlib.sha3_256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        event = {
            "decision_id": decision.decision_id,
            "revision": 2,
            "event_type": "SECURITY_INCIDENT_RESPONSE_EXECUTED",
            "actor_principal_id": actor_principal_id,
            "occurred_at": payload["occurred_at"],
            "decision_fingerprint": fingerprint,
            "execution_idempotency_fingerprint": key_fingerprint,
            "event_id": decision.decision_id + ":revision:2",
            "result_status": result_status,
            "result_revision": result_revision,
        }
        common = {
            "event_key": event_key,
            "schema_version": AUDIT_SCHEMA_VERSION,
            "event_type": event["event_type"],
            "tenant_id": decision.tenant_id,
            "actor_principal_id": actor_principal_id,
            "target_id": decision.decision_id,
            "fingerprint": fingerprint,
            "occurred_at": event["occurred_at"],
        }
        try:
            existing = self._events.find_one(
                {"decision_id": decision.decision_id, "revision": 2},
                session=session,
            )
            if existing is not None:
                if any(existing.get(key) != expected for key, expected in event.items()):
                    raise SecurityIncidentResponseDecisionConflictError(
                        "RESPONSE_EXECUTION_REPLAY_CONFLICT"
                    )
                audit = self._audit_events.find_one({"event_key": event_key}, session=session)
                outbox = self._outbox.find_one({"event_key": event_key}, session=session)
                if (
                    audit is None
                    or any(audit.get(key) != expected for key, expected in common.items())
                    or outbox is None
                    or any(outbox.get(key) != expected for key, expected in common.items())
                    or outbox.get("status") != "PENDING"
                    or outbox.get("attempts") != 0
                ):
                    raise SecurityIncidentResponseDecisionConflictError(
                        "RESPONSE_EXECUTION_AUDIT_REPLAY_CONFLICT"
                    )
                return dict(existing)
            self._events.insert_one(event, session=session)
            self._audit_events.insert_one(common, session=session)
            self._outbox.insert_one(
                {**common, "status": "PENDING", "attempts": 0, "created_at": event["occurred_at"]},
                session=session,
            )
            return event
        except (SecurityIncidentResponseDecisionRegistryError, SecurityIncidentResponseDecisionConflictError):
            raise
        except DuplicateKeyError as error:
            raise SecurityIncidentResponseDecisionConflictError(
                "RESPONSE_EXECUTION_CONCURRENT_DUPLICATE"
            ) from error
        except PyMongoError as error:
            raise SecurityIncidentResponseDecisionRegistryError(
                "RESPONSE_EXECUTION_PERSISTENCE_FAILED"
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
        if not isinstance(approved, bool):
            raise SecurityIncidentResponseDecisionConflictError("RESPONSE_DECISION_APPROVAL_INVALID")
        if (
            not isinstance(decided_at, datetime)
            or decided_at.tzinfo is None
            or decided_at.utcoffset() is None
        ):
            raise SecurityIncidentResponseDecisionConflictError("DECISION_AT_INVALID")
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
