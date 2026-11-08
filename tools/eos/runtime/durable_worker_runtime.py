"""Canonical EOS composition boundary for durable background execution.

This module reuses the kernel-owned Mongo client/database. It never creates a
connection and accepts an explicitly populated worker registry from the
application composition root.
"""
from __future__ import annotations

from typing import Any

from pymongo.collection import Collection

from tools.eos.kernel.db import get_client, get_database
from .durable_worker_runner import DurableWorkerRunner
from .worker_registry import EngineWorkerRegistry

TASK_COLLECTION = "eos_runtime_tasks"
TASK_AUDIT_COLLECTION = "eos_runtime_task_audit"


def create_durable_worker_runner(
    *,
    worker_registry: EngineWorkerRegistry,
    worker_id: str,
    database: Any = None,
    mongo_client: Any = None,
    lease_seconds: int = 60,
) -> DurableWorkerRunner:
    """Compose the worker runner only from the canonical kernel DB graph."""
    resolved_database = database if database is not None else get_database()
    resolved_client = mongo_client if mongo_client is not None else get_client()
    if resolved_database is None or resolved_client is None:
        raise RuntimeError("EOS_KERNEL_DATABASE_NOT_READY")
    if getattr(resolved_database, "client", None) is not resolved_client:
        raise RuntimeError("EOS_WORKER_DATABASE_CLIENT_MISMATCH")
    if not isinstance(worker_registry, EngineWorkerRegistry):
        raise TypeError("EOS_WORKER_REGISTRY_REQUIRED")
    return DurableWorkerRunner(
        tasks=resolved_database[TASK_COLLECTION],
        audit=resolved_database[TASK_AUDIT_COLLECTION],
        mongo_client=resolved_client,
        worker_registry=worker_registry,
        worker_id=worker_id,
        lease_seconds=lease_seconds,
    )


def provision_durable_worker_indexes(database: Any = None) -> None:
    """Explicit operator/deployment action; never provisions indexes at import."""
    from .durable_task_queue import ensure_task_queue_indexes

    resolved_database = database if database is not None else get_database()
    if resolved_database is None:
        raise RuntimeError("EOS_KERNEL_DATABASE_NOT_READY")
    ensure_task_queue_indexes(
        resolved_database[TASK_COLLECTION],
        resolved_database[TASK_AUDIT_COLLECTION],
    )


__all__ = [
    "TASK_COLLECTION",
    "TASK_AUDIT_COLLECTION",
    "create_durable_worker_runner",
    "provision_durable_worker_indexes",
]
