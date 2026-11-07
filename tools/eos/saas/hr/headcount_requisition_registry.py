"""Caller-transaction durable registry for WILSY headcount requisitions.

The registry persists HR planning evidence only. Callers own the Mongo session
and transaction; this module grants no hiring, employee, identity, membership,
capacity, IAM, payroll, or financial authority.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.headcount_requisition import (
    HeadcountRequisition, RequisitionError, RequisitionStatus,
)

COLLECTION = "wilsy_headcount_requisitions"
EVENT_COLLECTION = "wilsy_headcount_requisition_events"
IDENTITY_INDEX = "wilsy_headcount_requisition_tenant_identity_unique"
IDEMPOTENCY_INDEX = "wilsy_headcount_requisition_tenant_idempotency_unique"
EVENT_IDENTITY_INDEX = "wilsy_headcount_requisition_event_identity_unique"
EVENT_REVISION_INDEX = "wilsy_headcount_requisition_event_revision_unique"


class HeadcountRequisitionRegistryError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class HeadcountRequisitionRegistryConflict(HeadcountRequisitionRegistryError):
    pass


class HeadcountRequisitionNotFound(HeadcountRequisitionRegistryError):
    pass


def _exact(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise HeadcountRequisitionRegistryError(code)
    return value


def _session(value: object) -> object:
    if value is None:
        raise HeadcountRequisitionRegistryError("HEADCOUNT_TRANSACTION_SESSION_REQUIRED")
    return value


def _command_fingerprint(requisition: HeadcountRequisition, key: str, action: str) -> str:
    payload = {
        "tenant_id": requisition.tenant_id,
        "requisition_id": requisition.requisition_id,
        "idempotency_key": key,
        "action": action,
        "requisition": requisition.to_dict(),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha3_512(raw).hexdigest()


def _hydrate(row: Mapping[str, object]) -> HeadcountRequisition:
    try:
        payload = {key: row[key] for key in (
            "tenant_id", "requisition_id", "department_id", "position_title",
            "employment_type", "work_location", "headcount", "business_justification",
            "requested_by_principal_id", "status", "approval",
            "submitted_by_principal_id", "submitted_at", "revision",
            "schema", "version", "fingerprint",
        )}
        return HeadcountRequisition.from_dict(payload)
    except (KeyError, TypeError, ValueError, RequisitionError) as error:
        raise HeadcountRequisitionRegistryError("HEADCOUNT_PERSISTED_DOCUMENT_CORRUPT") from error


class HeadcountRequisitionRegistry:
    """Tenant-first immutable event history and revision-guarded current state."""

    __slots__ = ("_collection", "_events")

    def __init__(self, collection: Any, event_collection: Any) -> None:
        if collection is None or event_collection is None:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_COLLECTION_REQUIRED")
        self._collection = collection
        self._events = event_collection

    @staticmethod
    def ensure_indexes(collection: Any, event_collection: Any) -> None:
        if collection is None or event_collection is None:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_COLLECTION_REQUIRED")
        try:
            collection.create_index(
                [("tenant_id", ASCENDING), ("requisition_id", ASCENDING)],
                unique=True, name=IDENTITY_INDEX,
            )
            collection.create_index(
                [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True, name=IDEMPOTENCY_INDEX,
            )
            event_collection.create_index(
                [("tenant_id", ASCENDING), ("event_id", ASCENDING)],
                unique=True, name=EVENT_IDENTITY_INDEX,
            )
            event_collection.create_index(
                [("tenant_id", ASCENDING), ("requisition_id", ASCENDING), ("revision", ASCENDING)],
                unique=True, name=EVENT_REVISION_INDEX,
            )
        except PyMongoError as error:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_INDEX_UNAVAILABLE") from error

    def create_or_replay(
        self, requisition: HeadcountRequisition, *, idempotency_key: str,
        actor_principal_id: str, occurred_at: Any, session: Any,
    ) -> HeadcountRequisition:
        if not isinstance(requisition, HeadcountRequisition) or requisition.status is not RequisitionStatus.DRAFT:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_DRAFT_REQUIRED")
        key = _exact(idempotency_key, "HEADCOUNT_IDEMPOTENCY_KEY_INVALID")
        actor = _exact(actor_principal_id, "HEADCOUNT_ACTOR_INVALID")
        tx = _session(session)
        fingerprint = _command_fingerprint(requisition, key, "CREATE")
        coordinate = {"tenant_id": requisition.tenant_id, "idempotency_key": key}
        try:
            existing = self._collection.find_one(coordinate, session=tx)
            if existing is not None:
                if existing.get("command_fingerprint") != fingerprint:
                    raise HeadcountRequisitionRegistryConflict("HEADCOUNT_DIVERGENT_CREATE_REPLAY")
                return _hydrate(existing)
            document = requisition.to_dict()
            document.update({"idempotency_key": key, "command_fingerprint": fingerprint})
            self._collection.insert_one(document, session=tx)
            self._events.insert_one({
                "tenant_id": requisition.tenant_id,
                "event_id": f"headcount:{fingerprint}",
                "requisition_id": requisition.requisition_id,
                "event_type": "HEADCOUNT_REQUISITION_CREATED",
                "actor_principal_id": actor,
                "revision": requisition.revision,
                "prior_fingerprint": None,
                "result_fingerprint": requisition.fingerprint,
                "idempotency_key": key,
                "command_fingerprint": fingerprint,
                "occurred_at": occurred_at,
                "schema": "wilsy.hr.headcount_requisition_event.v1",
            }, session=tx)
            return requisition
        except HeadcountRequisitionRegistryConflict:
            raise
        except DuplicateKeyError as error:
            raise HeadcountRequisitionRegistryConflict("HEADCOUNT_DUPLICATE_CREATE") from error
        except PyMongoError as error:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_PERSISTENCE_UNAVAILABLE") from error

    def get(self, *, tenant_id: str, requisition_id: str, session: Any) -> HeadcountRequisition:
        tenant = _exact(tenant_id, "HEADCOUNT_TENANT_INVALID")
        identity = _exact(requisition_id, "HEADCOUNT_REQUISITION_ID_INVALID")
        try:
            row = self._collection.find_one(
                {"tenant_id": tenant, "requisition_id": identity}, session=_session(session),
            )
        except PyMongoError as error:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_PERSISTENCE_UNAVAILABLE") from error
        if row is None:
            raise HeadcountRequisitionNotFound("HEADCOUNT_REQUISITION_NOT_FOUND")
        return _hydrate(row)

    def list_for_tenant(self, *, tenant_id: str, session: Any, limit: int = 200) -> tuple[HeadcountRequisition, ...]:
        tenant = _exact(tenant_id, "HEADCOUNT_TENANT_INVALID")
        tx = _session(session)
        if type(limit) is not int or not 1 <= limit <= 500:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_LIMIT_INVALID")
        try:
            cursor = self._collection.find({"tenant_id": tenant}, session=tx).sort(
                [("revision", -1), ("requisition_id", ASCENDING)]
            ).limit(limit)
            return tuple(_hydrate(row) for row in cursor)
        except PyMongoError as error:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_PERSISTENCE_UNAVAILABLE") from error

    def transition(
        self, *, tenant_id: str, requisition_id: str,
        expected_revision: int, updated: HeadcountRequisition,
        action: str, actor_principal_id: str, idempotency_key: str,
        request_fingerprint: str, occurred_at: Any, session: Any,
    ) -> HeadcountRequisition:
        tenant = _exact(tenant_id, "HEADCOUNT_TENANT_INVALID")
        identity = _exact(requisition_id, "HEADCOUNT_REQUISITION_ID_INVALID")
        actor = _exact(actor_principal_id, "HEADCOUNT_ACTOR_INVALID")
        key = _exact(idempotency_key, "HEADCOUNT_IDEMPOTENCY_KEY_INVALID")
        tx = _session(session)
        if not isinstance(request_fingerprint, str) or len(request_fingerprint) != 128:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_REQUEST_FINGERPRINT_INVALID")
        try:
            prior = self._events.find_one(
                {"tenant_id": tenant, "idempotency_key": key}, session=tx,
            )
            if prior is not None:
                if prior.get("request_fingerprint") != request_fingerprint:
                    raise HeadcountRequisitionRegistryConflict("HEADCOUNT_DIVERGENT_TRANSITION_REPLAY")
                snapshot = prior.get("result_snapshot")
                if not isinstance(snapshot, dict):
                    raise HeadcountRequisitionRegistryError("HEADCOUNT_EVENT_SNAPSHOT_CORRUPT")
                return HeadcountRequisition.from_dict(snapshot)
            current = self.get(tenant_id=tenant, requisition_id=identity, session=tx)
            if updated.tenant_id != tenant or updated.requisition_id != identity:
                raise HeadcountRequisitionRegistryConflict("HEADCOUNT_SCOPE_IMMUTABLE")
            if current.revision != expected_revision or updated.revision != expected_revision + 1:
                raise HeadcountRequisitionRegistryConflict("HEADCOUNT_REVISION_CONFLICT")
            fingerprint = _command_fingerprint(updated, key, action)
            result = self._collection.update_one(
                {"tenant_id": tenant, "requisition_id": identity, "revision": expected_revision,
                 "fingerprint": current.fingerprint},
                {"$set": updated.to_dict()},
                session=tx,
            )
            if getattr(result, "matched_count", 0) != 1:
                raise HeadcountRequisitionRegistryConflict("HEADCOUNT_REVISION_CONFLICT")
            self._events.insert_one({
                "tenant_id": tenant,
                "event_id": f"headcount:{fingerprint}",
                "requisition_id": identity,
                "event_type": f"HEADCOUNT_REQUISITION_{action}",
                "actor_principal_id": actor,
                "revision": updated.revision,
                "prior_fingerprint": current.fingerprint,
                "result_fingerprint": updated.fingerprint,
                "command_fingerprint": fingerprint,
                "request_fingerprint": request_fingerprint,
                "result_snapshot": updated.to_dict(),
                "idempotency_key": key,
                "occurred_at": occurred_at,
                "schema": "wilsy.hr.headcount_requisition_event.v1",
            }, session=tx)
            return updated
        except HeadcountRequisitionRegistryConflict:
            raise
        except DuplicateKeyError as error:
            raise HeadcountRequisitionRegistryConflict("HEADCOUNT_DUPLICATE_TRANSITION") from error
        except PyMongoError as error:
            raise HeadcountRequisitionRegistryError("HEADCOUNT_PERSISTENCE_UNAVAILABLE") from error


__all__ = [
    "COLLECTION", "EVENT_COLLECTION", "HeadcountRequisitionRegistry",
    "HeadcountRequisitionRegistryError", "HeadcountRequisitionRegistryConflict",
    "HeadcountRequisitionNotFound",
]
