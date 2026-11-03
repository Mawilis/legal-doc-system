"""Tenant-first durable registry for owner-commercial work items.

The caller owns the Mongo session and active transaction. This registry has no
Legal matter access, IAM, assignment, entitlement, messaging or financial power.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.crm.domain.owner_commercial_work_item import (
    OwnerCommercialWorkItem,
    OwnerWorkItemError, OwnerWorkStatus,
    build_daily_queue,
    command_fingerprint,
)

COLLECTION = "owner_commercial_work_items"
IDENTITY_INDEX = "owner_work_tenant_identity_unique"
IDEMPOTENCY_INDEX = "owner_work_tenant_idempotency_unique"
QUEUE_INDEX = "owner_work_tenant_status_due"


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


def ensure_indexes(collection: Any) -> None:
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
    except PyMongoError as error:
        raise OwnerWorkRegistryError("OWNER_WORK_INDEX_UNAVAILABLE") from error


class OwnerCommercialWorkRegistry:
    """Durable, tenant-scoped creation and read projection."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        self._collection = _collection(collection)

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

    def daily_queue(
        self, *, tenant_id: str, now: Any, session: Any, limit: int = 250,
    ) -> tuple[dict[str, object], ...]:
        return build_daily_queue(
            self.list_for_tenant(tenant_id=tenant_id, session=session, limit=limit),
            tenant_id=tenant_id, now=now,
        )


__all__ = [
    "COLLECTION", "OwnerCommercialWorkRegistry", "OwnerWorkRegistryConflict",
    "OwnerWorkRegistryError", "OwnerWorkRegistryNotFound", "ensure_indexes",
]
