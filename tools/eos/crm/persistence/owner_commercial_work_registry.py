"""TITLE: WILSY OS CRM Source-Owned Work Registry
VERSION: v1.1.0-AUDITED-OPTIMISTIC-WORK-REVISION
AUTHORITY: Python EOS CRM persistence under caller-owned Mongo transactions.
EPITOME: Persist exact-tenant commercial task creation, completion and an
         independently permission-gated edit with immutable audit evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/crm/persistence/owner_commercial_work_registry.py
COLLABORATION / OWNERSHIP: OwnerCommercialWorkspaceService, owner CRM router,
         strict OwnerCommercialWorkItem domain and active session IAM.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.1.0-AUDITED-OPTIMISTIC-WORK-REVISION introduces a separate
           same-source append-only edit event collection, exact-tenant
           expected-updated-at compare-and-set, idempotency fingerprint,
           terminal-state denial and validated replay. Existing creation,
           completion, queue and source identity behavior remain unchanged.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No raw event content in logs; audit is stored
                            only with tenant-scoped source coordinates.
TENANT BOUNDARY: Both record and event queries require exact tenant_id.
AUTHORITY BOUNDARY: Caller must separately prove CRM edit IAM and entitlement;
                    persistence grants no principal, workforce or assignment.
TRANSACTION / IDEMPOTENCY BOUNDARY: Caller owns majority transaction; audit and
                                    task revision commit atomically.
FINANCIAL AUTHORITY BOUNDARY: No approval, payment, settlement or execution.
FAIL-CLOSED POSTURE: Invalid input, mismatch, terminal record, duplicate
                     divergence and persistence failure never yield success.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha3_512
import json
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.crm.domain.owner_commercial_work_item import (
    OwnerCommercialWorkItem,
    OwnerWorkItemError, OwnerWorkStatus, OwnerWorkPriority,
    build_daily_queue,
    command_fingerprint,
)

COLLECTION = "owner_commercial_work_items"
IDENTITY_INDEX = "owner_work_tenant_identity_unique"
IDEMPOTENCY_INDEX = "owner_work_tenant_idempotency_unique"
QUEUE_INDEX = "owner_work_tenant_status_due"
EVENTS_COLLECTION = "owner_commercial_work_events"
EVENT_IDEMPOTENCY_INDEX = "owner_work_edit_tenant_record_key_unique"


class OwnerWorkRegistryError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class OwnerWorkRegistryConflict(OwnerWorkRegistryError):
    pass


class OwnerWorkRegistryNotFound(OwnerWorkRegistryError):
    pass


def _exact(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise OwnerWorkRegistryError(code)
    return value


def _session(value: object) -> object:
    if value is None:
        raise OwnerWorkRegistryError("OWNER_WORK_SESSION_REQUIRED")
    return value


def _collection(value: Any) -> Any:
    if value is None:
        raise OwnerWorkRegistryError("OWNER_WORK_COLLECTION_REQUIRED")
    return value


def _hydrate(row: Mapping[str, object]) -> OwnerCommercialWorkItem:
    try:
        projected = {
            "schema": row["schema"],
            **{key: row[key] for key in (
                "work_item_id", "tenant_id", "title", "description", "kind",
                "status", "priority", "owner_principal_id", "due_at",
                "source_type", "source_id", "created_at", "updated_at",
                "completed_at", "completion_note",
            )},
        }
        return OwnerCommercialWorkItem.from_dict(projected)
    except (KeyError, TypeError, ValueError, OwnerWorkItemError) as error:
        raise OwnerWorkRegistryError("OWNER_WORK_CORRUPT_DOCUMENT") from error


def ensure_indexes(collection: Any, events_collection: Any = None) -> None:
    target = _collection(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("work_item_id", ASCENDING)],
            unique=True, name=IDENTITY_INDEX,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
            unique=True, name=IDEMPOTENCY_INDEX,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("status", ASCENDING),
             ("due_at", ASCENDING), ("priority", ASCENDING)],
            name=QUEUE_INDEX,
        )
        if events_collection is not None:
            events_collection.create_index(
                [("tenant_id", ASCENDING), ("work_item_id", ASCENDING),
                 ("idempotency_key", ASCENDING)],
                unique=True, name=EVENT_IDEMPOTENCY_INDEX,
            )
    except PyMongoError as error:
        raise OwnerWorkRegistryError("OWNER_WORK_INDEX_UNAVAILABLE") from error


class OwnerCommercialWorkRegistry:
    """Durable, tenant-scoped creation and read projection."""

    __slots__ = ("_collection", "_events")

    def __init__(self, collection: Any, events_collection: Any = None) -> None:
        self._collection = _collection(collection)
        self._events = events_collection

    def create_or_replay(
        self, item: OwnerCommercialWorkItem, *, idempotency_key: str,
        session: Any,
    ) -> OwnerCommercialWorkItem:
        if not isinstance(item, OwnerCommercialWorkItem):
            raise OwnerWorkRegistryError("OWNER_WORK_ITEM_REQUIRED")
        key = _exact(idempotency_key, "OWNER_WORK_IDEMPOTENCY_KEY_INVALID")
        caller_session = _session(session)
        fingerprint = command_fingerprint(item, key)
        coordinate = {"tenant_id": item.tenant_id, "idempotency_key": key}
        try:
            existing = self._collection.find_one(coordinate, session=caller_session)
            if existing is not None:
                if existing.get("command_fingerprint") != fingerprint:
                    raise OwnerWorkRegistryConflict("OWNER_WORK_DIVERGENT_REPLAY")
                return _hydrate(existing)
            document = item.to_dict()
            document.update({
                "idempotency_key": key,
                "command_fingerprint": fingerprint,
            })
            self._collection.insert_one(document, session=caller_session)
            return item
        except OwnerWorkRegistryConflict:
            raise
        except DuplicateKeyError as error:
            try:
                raced = self._collection.find_one(coordinate, session=caller_session)
            except PyMongoError as read_error:
                raise OwnerWorkRegistryError("OWNER_WORK_PERSISTENCE_UNAVAILABLE") from read_error
            if raced is not None and raced.get("command_fingerprint") == fingerprint:
                return _hydrate(raced)
            raise OwnerWorkRegistryConflict("OWNER_WORK_DUPLICATE_OR_DIVERGENT_COMMAND") from error
        except PyMongoError as error:
            raise OwnerWorkRegistryError("OWNER_WORK_PERSISTENCE_UNAVAILABLE") from error

    def get(
        self, *, tenant_id: str, work_item_id: str, session: Any,
    ) -> OwnerCommercialWorkItem:
        tenant = _exact(tenant_id, "OWNER_WORK_TENANT_INVALID")
        identity = _exact(work_item_id, "OWNER_WORK_ID_INVALID")
        caller_session = _session(session)
        try:
            row = self._collection.find_one(
                {"tenant_id": tenant, "work_item_id": identity},
                session=caller_session,
            )
        except PyMongoError as error:
            raise OwnerWorkRegistryError("OWNER_WORK_PERSISTENCE_UNAVAILABLE") from error
        if row is None:
            raise OwnerWorkRegistryNotFound("OWNER_WORK_NOT_FOUND")
        return _hydrate(row)

    def list_for_tenant(
        self, *, tenant_id: str, session: Any, limit: int = 250,
    ) -> tuple[OwnerCommercialWorkItem, ...]:
        tenant = _exact(tenant_id, "OWNER_WORK_TENANT_INVALID")
        caller_session = _session(session)
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise OwnerWorkRegistryError("OWNER_WORK_LIMIT_INVALID")
        try:
            cursor = self._collection.find(
                {"tenant_id": tenant}, session=caller_session,
            ).sort([("due_at", ASCENDING), ("created_at", ASCENDING)]).limit(limit)
            return tuple(_hydrate(row) for row in cursor)
        except PyMongoError as error:
            raise OwnerWorkRegistryError("OWNER_WORK_PERSISTENCE_UNAVAILABLE") from error

    def complete(
        self, *, tenant_id: str, work_item_id: str, completion_note: str,
        now: Any, session: Any,
    ) -> OwnerCommercialWorkItem:
        """Complete one own-tenant active task using a status compare-and-set."""
        tenant = _exact(tenant_id, "OWNER_WORK_TENANT_INVALID")
        identity = _exact(work_item_id, "OWNER_WORK_ID_INVALID")
        caller_session = _session(session)
        current = self.get(tenant_id=tenant, work_item_id=identity, session=caller_session)
        if current.status is OwnerWorkStatus.COMPLETED:
            if current.completion_note == completion_note:
                return current
            raise OwnerWorkRegistryConflict("OWNER_WORK_DIVERGENT_COMPLETION_REPLAY")
        if current.status is OwnerWorkStatus.CANCELLED:
            raise OwnerWorkRegistryConflict("OWNER_WORK_TERMINAL_STATE")
        updated = replace(
            current, status=OwnerWorkStatus.COMPLETED,
            updated_at=now, completed_at=now, completion_note=completion_note,
        )
        try:
            result = self._collection.update_one(
                {"tenant_id": tenant, "work_item_id": identity, "status": current.status.value},
                {"$set": updated.to_dict()}, session=caller_session,
            )
        except PyMongoError as error:
            raise OwnerWorkRegistryError("OWNER_WORK_PERSISTENCE_UNAVAILABLE") from error
        if getattr(result, "matched_count", 0) != 1:
            raise OwnerWorkRegistryConflict("OWNER_WORK_CONCURRENT_TRANSITION")
        return updated


    def revise(
        self, *, tenant_id: str, work_item_id: str, actor_principal_id: str,
        title: str, description: str, priority: OwnerWorkPriority,
        due_at: datetime | None, expected_updated_at: datetime,
        idempotency_key: str, now: datetime, session: Any,
    ) -> OwnerCommercialWorkItem:
        """Atomically edit active own-tenant CRM work with a durable audit event.

        The authenticated caller must already pass CRM update IAM and current
        entitlement. Its principal is used solely as audit actor; it does not
        change the task owner. Replays return the original committed response,
        while divergent keys and stale versions conflict. Both writes use the
        caller's existing Mongo transaction. No financial authority is created.
        """
        tenant = _exact(tenant_id, "OWNER_WORK_TENANT_INVALID")
        identity = _exact(work_item_id, "OWNER_WORK_ID_INVALID")
        actor = _exact(actor_principal_id, "OWNER_WORK_ACTOR_INVALID")
        key = _exact(idempotency_key, "OWNER_WORK_IDEMPOTENCY_KEY_INVALID")
        caller_session = _session(session)
        if self._events is None:
            raise OwnerWorkRegistryError("OWNER_WORK_AUDIT_STORE_REQUIRED")
        if not isinstance(title, str) or not 1 <= len(title) <= 240:
            raise OwnerWorkItemError("TITLE_INVALID")
        if not isinstance(description, str) or len(description) > 4000:
            raise OwnerWorkItemError("DESCRIPTION_INVALID")
        if not isinstance(priority, OwnerWorkPriority):
            raise OwnerWorkItemError("PRIORITY_INVALID")
        for instant in (expected_updated_at, now, due_at):
            if instant is not None and (
                not isinstance(instant, datetime) or instant.tzinfo is None
                or instant.utcoffset() is None
            ):
                raise OwnerWorkItemError("WORK_TIMESTAMP_INVALID")
        if not isinstance(expected_updated_at, datetime) or not isinstance(now, datetime):
            raise OwnerWorkItemError("WORK_TIMESTAMP_REQUIRED")
        expected = expected_updated_at.astimezone(timezone.utc)
        changed_due = due_at.astimezone(timezone.utc) if due_at else None
        command = {
            "tenant_id": tenant, "work_item_id": identity,
            "actor_principal_id": actor, "title": title,
            "description": description, "priority": priority.value,
            "due_at": changed_due.isoformat() if changed_due else None,
            "expected_updated_at": expected.isoformat(),
        }
        fingerprint = sha3_512(json.dumps(
            command, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8")).hexdigest()
        coordinate = {
            "tenant_id": tenant, "work_item_id": identity, "idempotency_key": key,
        }
        try:
            existing = self._events.find_one(coordinate, session=caller_session)
            if existing is not None:
                if existing.get("fingerprint") != fingerprint:
                    raise OwnerWorkRegistryConflict("OWNER_WORK_DIVERGENT_EDIT_REPLAY")
                return _hydrate(existing["after"])
            current = self.get(
                tenant_id=tenant, work_item_id=identity, session=caller_session,
            )
            if current.status in (OwnerWorkStatus.COMPLETED, OwnerWorkStatus.CANCELLED):
                raise OwnerWorkRegistryConflict("OWNER_WORK_TERMINAL_STATE")
            if current.updated_at != expected:
                raise OwnerWorkRegistryConflict("OWNER_WORK_STALE_REVISION")
            if now < current.updated_at:
                raise OwnerWorkRegistryConflict("OWNER_WORK_CLOCK_REGRESSION")
            updated = replace(
                current, title=title, description=description, priority=priority,
                due_at=changed_due, updated_at=now,
            )
            result = self._collection.update_one(
                {
                    "tenant_id": tenant, "work_item_id": identity,
                    "status": current.status.value,
                    "updated_at": current.updated_at.isoformat(),
                },
                {"$set": updated.to_dict()}, session=caller_session,
            )
            if getattr(result, "matched_count", 0) != 1:
                raise OwnerWorkRegistryConflict("OWNER_WORK_CONCURRENT_REVISION")
            self._events.insert_one({
                **coordinate, "fingerprint": fingerprint,
                "actor_principal_id": actor, "recorded_at": now.isoformat(),
                "before": current.to_dict(), "after": updated.to_dict(),
            }, session=caller_session)
            return updated
        except (OwnerWorkRegistryConflict, OwnerWorkRegistryError, OwnerWorkItemError):
            raise
        except DuplicateKeyError as error:
            raise OwnerWorkRegistryConflict("OWNER_WORK_CONCURRENT_EDIT_REPLAY") from error
        except (KeyError, TypeError, ValueError) as error:
            raise OwnerWorkRegistryError("OWNER_WORK_CORRUPT_AUDIT_EVENT") from error
        except PyMongoError as error:
            raise OwnerWorkRegistryError("OWNER_WORK_REVISION_UNAVAILABLE") from error

    def revision_history(
        self, *, tenant_id: str, work_item_id: str, session: Any,
        limit: int = 100,
    ) -> tuple[dict[str, object], ...]:
        """Return source-owned audited revisions, newest first, exact tenant only.

        Caller must separately authorize CRM read and entitlement. No mutation
        or inference of unrecorded legacy history occurs; no financial authority.
        """
        tenant = _exact(tenant_id, "OWNER_WORK_TENANT_INVALID")
        identity = _exact(work_item_id, "OWNER_WORK_ID_INVALID")
        caller_session = _session(session)
        if self._events is None:
            raise OwnerWorkRegistryError("OWNER_WORK_AUDIT_STORE_REQUIRED")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise OwnerWorkRegistryError("OWNER_WORK_HISTORY_LIMIT_INVALID")
        self.get(tenant_id=tenant, work_item_id=identity, session=caller_session)
        try:
            records = self._events.find(
                {"tenant_id": tenant, "work_item_id": identity},
                {"_id": 0, "idempotency_key": 0, "fingerprint": 0},
                session=caller_session,
            ).sort("recorded_at", -1).limit(limit)
            return tuple(dict(entry) for entry in records)
        except PyMongoError as error:
            raise OwnerWorkRegistryError("OWNER_WORK_HISTORY_UNAVAILABLE") from error

    def daily_queue(
        self, *, tenant_id: str, now: Any, session: Any, limit: int = 250,
    ) -> tuple[dict[str, object], ...]:
        return build_daily_queue(
            self.list_for_tenant(tenant_id=tenant_id, session=session, limit=limit),
            tenant_id=tenant_id, now=now,
        )


__all__ = [
    "COLLECTION", "EVENTS_COLLECTION", "OwnerCommercialWorkRegistry", "OwnerWorkRegistryConflict",
    "OwnerWorkRegistryError", "OwnerWorkRegistryNotFound", "ensure_indexes",
]

# ARTIFACT: tools/eos/crm/persistence/owner_commercial_work_registry.py
# VERSION: v1.1.0-AUDITED-OPTIMISTIC-WORK-REVISION
# AUTHORITY BOUNDARY: CRM source-only transactional updates; IAM owned by API.
# TENANT POSTURE: Exact tenant for task, replay and append-only audit event.
# FAIL-CLOSED POSTURE: Stale CAS, replay divergence, corrupt input or missing audit store reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
