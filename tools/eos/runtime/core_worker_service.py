"""Supervised Python EOS background service composition.

The service runs the durable queue consumer and daily compliance scheduler
against the same kernel-owned Mongo client/database. It does not start at
module import; the deployment/runtime owner must invoke it explicitly.
"""
from __future__ import annotations

import asyncio
from typing import Any

from .compliance_scan_scheduler import run_daily_compliance_scheduler
from .core_worker_registry import build_core_worker_registry
from .durable_worker_runner import DurableWorkerRunner
from .durable_worker_runtime import (
    TASK_AUDIT_COLLECTION,
    TASK_COLLECTION,
)


async def run_core_worker_service(
    *,
    database: Any,
    mongo_client: Any,
    worker_id: str,
    stop_event: asyncio.Event,
    lease_seconds: int = 60,
    idle_poll_seconds: float = 1.0,
) -> None:
    """Run durable task processing and compliance scheduling until shutdown."""
    if database is None or mongo_client is None:
        raise RuntimeError("EOS_KERNEL_DATABASE_NOT_READY")
    if getattr(database, "client", None) is not mongo_client:
        raise RuntimeError("EOS_WORKER_DATABASE_CLIENT_MISMATCH")

    registry = build_core_worker_registry(
        database=database,
        mongo_client=mongo_client,
    )
    runner = DurableWorkerRunner(
        tasks=database[TASK_COLLECTION],
        audit=database[TASK_AUDIT_COLLECTION],
        mongo_client=mongo_client,
        worker_registry=registry,
        worker_id=worker_id,
        lease_seconds=lease_seconds,
    )
    worker_task = asyncio.create_task(
        runner.run_forever(
            stop_event=stop_event,
            idle_poll_seconds=idle_poll_seconds,
        ),
        name="eos-durable-worker",
    )
    scheduler_task = asyncio.create_task(
        run_daily_compliance_scheduler(
            tenants=database["tenants"],
            tasks=database[TASK_COLLECTION],
            stop_event=stop_event,
        ),
        name="eos-compliance-scheduler",
    )
    try:
        await asyncio.gather(worker_task, scheduler_task)
    finally:
        stop_event.set()
        for task in (worker_task, scheduler_task):
            if not task.done():
                task.cancel()
        await asyncio.gather(worker_task, scheduler_task, return_exceptions=True)


__all__ = ["run_core_worker_service"]
