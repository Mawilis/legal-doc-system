"""Durable MongoDB-backed EOS task execution queue.

The queue provides at-least-once delivery with idempotent enqueue, atomic
leases, lease fencing, bounded retries, and terminal dead-letter state.
It is orchestration/persistence only: it grants no IAM, tenant, KEXEC, or
financial authority. Callers own transactions and downstream idempotency.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import re
from typing import Any, Mapping
from uuid import uuid4

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection


class DurableTaskQueueError(RuntimeError):
    """Fail-closed queue contract or state error."""


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise DurableTaskQueueError("TASK_QUEUE_TIMESTAMP_INVALID")
    return value.astimezone(timezone.utc)


def _required(value: str, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DurableTaskQueueError(code)
    return value.strip()


def ensure_task_queue_indexes(tasks: Collection, audit: Collection, *, session: Any = None) -> None:
    """Provision stable uniqueness and claim-order indexes; no client is created."""
    tasks.create_index([("tenant_id", 1), ("task_id", 1)], unique=True, name="uq_eos_task_identity", session=session)
    tasks.create_index([("status", 1), ("available_at", 1), ("priority", 1), ("created_at", 1)], name="ix_eos_task_claim", session=session)
    tasks.create_index([("status", 1), ("lease_until", 1)], name="ix_eos_task_expired_lease", session=session)
    audit.create_index([("tenant_id", 1), ("task_id", 1), ("sequence", 1)], unique=True, name="uq_eos_task_audit_sequence", session=session)


def enqueue_task(
    tasks: Collection,
    *,
    tenant_id: str,
    task_id: str,
    task_type: str,
    payload: Mapping[str, Any],
    engine_name: str | None = None,
    now: datetime,
    priority: int = 10,
    max_attempts: int = 5,
    session: Any = None,
) -> dict[str, Any]:
    """Insert a tenant-scoped task once; a duplicate identity never overwrites it."""
    tenant_id = _required(tenant_id, "TASK_QUEUE_TENANT_REQUIRED")
    task_id = _required(task_id, "TASK_QUEUE_TASK_ID_REQUIRED")
    task_type = _required(task_type, "TASK_QUEUE_TYPE_REQUIRED")
    engine_name = _required(engine_name or task_type, "TASK_QUEUE_ENGINE_REQUIRED")
    now = _utc(now)
    if not isinstance(payload, Mapping) or max_attempts < 1 or not isinstance(priority, int):
        raise DurableTaskQueueError("TASK_QUEUE_ENQUEUE_ARGUMENT_INVALID")
    try:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=None)
    except (TypeError, ValueError) as exc:
        raise DurableTaskQueueError("TASK_QUEUE_PAYLOAD_NOT_JSON") from exc
    digest = sha256(encoded.encode("utf-8")).hexdigest()
    document = {
        "tenant_id": tenant_id,
        "task_id": task_id,
        "task_type": task_type,
        "engine_name": engine_name,
        "payload": json.loads(encoded),
        "payload_sha256": digest,
        "status": "PENDING",
        "attempts": 0,
        "max_attempts": max_attempts,
        "priority": priority,
        "available_at": now,
        "created_at": now,
        "updated_at": now,
    }
    try:
        tasks.insert_one(document, session=session)
        return document
    except DuplicateKeyError:
        existing = tasks.find_one({"tenant_id": tenant_id, "task_id": task_id}, session=session)
        if existing is None or existing.get("payload_sha256") != digest or existing.get("task_type") != task_type or existing.get("engine_name", task_type) != engine_name:
            raise DurableTaskQueueError("TASK_QUEUE_IDEMPOTENCY_CONFLICT")
        return existing


def claim_next_task(
    tasks: Collection,
    *,
    worker_id: str,
    lease_token: str,
    now: datetime,
    lease_seconds: int = 60,
    session: Any = None,
) -> dict[str, Any] | None:
    """Atomically claim due work or reclaim an expired lease."""
    worker_id = _required(worker_id, "TASK_QUEUE_WORKER_REQUIRED")
    lease_token = _required(lease_token, "TASK_QUEUE_LEASE_REQUIRED")
    now = _utc(now)
    if lease_seconds < 1:
        raise DurableTaskQueueError("TASK_QUEUE_LEASE_DURATION_INVALID")
    query = {
        "$or": [
            {"status": {"$in": ["PENDING", "RETRY"]}, "available_at": {"$lte": now}},
            {"status": "CLAIMED", "lease_until": {"$lte": now}},
        ],
    }
    # Mongo query expressions compare the two attempt fields without client-side races.
    query["$expr"] = {"$lt": ["$attempts", "$max_attempts"]}
    return tasks.find_one_and_update(
        query,
        {
            "$set": {
                "status": "CLAIMED",
                "claimed_by": worker_id,
                "lease_token": lease_token,
                "lease_until": now + timedelta(seconds=lease_seconds),
                "updated_at": now,
            },
            "$inc": {"attempts": 1},
        },
        sort=[("priority", 1), ("available_at", 1), ("created_at", 1), ("task_id", 1)],
        return_document=ReturnDocument.AFTER,
        session=session,
    )


def complete_task(
    tasks: Collection,
    audit: Collection,
    *,
    tenant_id: str,
    task_id: str,
    worker_id: str,
    lease_token: str,
    now: datetime,
    result: Mapping[str, Any] | None = None,
    session: Any = None,
) -> bool:
    """Complete only the current lease owner; audit and state share caller transaction."""
    now = _utc(now)
    if session is None:
        raise DurableTaskQueueError("TASK_QUEUE_AUDIT_TRANSACTION_REQUIRED")
    identity = {
        "tenant_id": _required(tenant_id, "TASK_QUEUE_TENANT_REQUIRED"),
        "task_id": _required(task_id, "TASK_QUEUE_TASK_ID_REQUIRED"),
        "status": "CLAIMED",
        "claimed_by": _required(worker_id, "TASK_QUEUE_WORKER_REQUIRED"),
        "lease_token": _required(lease_token, "TASK_QUEUE_LEASE_REQUIRED"),
    }
    updated = tasks.update_one(
        identity,
        {"$set": {"status": "COMPLETED", "result": dict(result or {}), "completed_at": now, "updated_at": now},
         "$unset": {"claimed_by": "", "lease_token": "", "lease_until": ""}},
        session=session,
    )
    if updated.modified_count != 1:
        return False
    _append_audit(audit, identity["tenant_id"], identity["task_id"], "COMPLETED", now, session)
    return True


def fail_task(
    tasks: Collection,
    audit: Collection,
    *,
    tenant_id: str,
    task_id: str,
    worker_id: str,
    lease_token: str,
    now: datetime,
    error_code: str,
    retry_base_seconds: int = 2,
    retry_max_seconds: int = 3600,
    session: Any = None,
) -> str:
    """Record bounded failure evidence and retry or dead-letter the task."""
    now = _utc(now)
    if session is None:
        raise DurableTaskQueueError("TASK_QUEUE_AUDIT_TRANSACTION_REQUIRED")
    if not re.fullmatch(r"[A-Z0-9_]{1,96}", error_code or ""):
        raise DurableTaskQueueError("TASK_QUEUE_ERROR_CODE_INVALID")
    identity = {
        "tenant_id": _required(tenant_id, "TASK_QUEUE_TENANT_REQUIRED"),
        "task_id": _required(task_id, "TASK_QUEUE_TASK_ID_REQUIRED"),
        "status": "CLAIMED",
        "claimed_by": _required(worker_id, "TASK_QUEUE_WORKER_REQUIRED"),
        "lease_token": _required(lease_token, "TASK_QUEUE_LEASE_REQUIRED"),
    }
    current = tasks.find_one(identity, {"attempts": 1, "max_attempts": 1}, session=session)
    if current is None:
        raise DurableTaskQueueError("TASK_QUEUE_LEASE_LOST")
    attempts = int(current["attempts"])
    terminal = attempts >= int(current["max_attempts"])
    delay = min(retry_max_seconds, retry_base_seconds * (2 ** max(0, attempts - 1)))
    status = "DEAD_LETTER" if terminal else "RETRY"
    update = {
        "$set": {
            "status": status,
            "last_error_code": error_code,
            "updated_at": now,
            "available_at": now + timedelta(seconds=delay),
        },
        "$unset": {"claimed_by": "", "lease_token": "", "lease_until": ""},
        "$push": {"failure_history": {"attempt": attempts, "error_code": error_code, "at": now}},
    }
    changed = tasks.update_one(identity, update, session=session)
    if changed.modified_count != 1:
        raise DurableTaskQueueError("TASK_QUEUE_LEASE_LOST")
    _append_audit(audit, identity["tenant_id"], identity["task_id"], status, now, session, error_code)
    return status


def _append_audit(
    audit: Collection,
    tenant_id: str,
    task_id: str,
    event_type: str,
    occurred_at: datetime,
    session: Any,
    error_code: str | None = None,
) -> None:
    """Append a separately stored lifecycle event; caller supplies transaction."""
    sequence = audit.count_documents({"tenant_id": tenant_id, "task_id": task_id}, session=session) + 1
    audit.insert_one(
        {"tenant_id": tenant_id, "task_id": task_id, "sequence": sequence,
         "event_type": event_type, "occurred_at": occurred_at,
         **({"error_code": error_code} if error_code else {})},
        session=session,
    )


__all__ = [
    "DurableTaskQueueError", "ensure_task_queue_indexes", "enqueue_task",
    "claim_next_task", "complete_task", "fail_task",
]
