"""Durable asynchronous EOS worker runner.

Claims persisted work, dispatches only through the canonical worker registry,
and commits terminal state together with lifecycle audit evidence. Mongo client
and transaction ownership remain with the application composition root.
"""
from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Callable
from uuid import uuid4

from pymongo.collection import Collection

from .worker_registry import EngineWorkerRegistry
from .worker_result import WorkerExecutionStatusEnum
from .durable_task_queue import (
    claim_next_task,
    complete_task,
    fail_task,
)

logger = logging.getLogger("WilsyOS.Runtime.DurableWorkerRunner")


class DurableWorkerRunner:
    """One-claim-at-a-time runner over the canonical EOS worker registry."""

    def __init__(
        self,
        *,
        tasks: Collection,
        audit: Collection,
        mongo_client: Any,
        worker_registry: EngineWorkerRegistry,
        worker_id: str,
        lease_seconds: int = 60,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise ValueError("TASK_QUEUE_WORKER_REQUIRED")
        if lease_seconds < 1:
            raise ValueError("TASK_QUEUE_LEASE_DURATION_INVALID")
        self.tasks = tasks
        self.audit = audit
        self.mongo_client = mongo_client
        self.worker_registry = worker_registry
        self.worker_id = worker_id.strip()
        self.lease_seconds = lease_seconds
        self._now = now or (lambda: datetime.now(timezone.utc))

    async def run_once(self) -> str:
        """Process at most one task; a crash leaves a reclaimable lease."""
        lease_token = uuid4().hex
        task = claim_next_task(
            self.tasks,
            worker_id=self.worker_id,
            lease_token=lease_token,
            now=self._now(),
            lease_seconds=self.lease_seconds,
        )
        if task is None:
            return "EMPTY"

        tenant_id = task["tenant_id"]
        task_id = task["task_id"]
        result = await self.worker_registry.dispatch_task(
            task["engine_name"], task_id, dict(task.get("payload") or {})
        )
        now = self._now()

        with self.mongo_client.start_session() as session:
            if result.status is WorkerExecutionStatusEnum.SUCCESS:
                completed = session.with_transaction(
                    lambda active_session: complete_task(
                        self.tasks,
                        self.audit,
                        tenant_id=tenant_id,
                        task_id=task_id,
                        worker_id=self.worker_id,
                        lease_token=lease_token,
                        now=now,
                        result=result.output,
                        session=active_session,
                    )
                )
                if not completed:
                    logger.warning("Task lease lost before completion: %s", task_id)
                    return "LEASE_LOST"
                return "COMPLETED"

            state = session.with_transaction(
                lambda active_session: fail_task(
                    self.tasks,
                    self.audit,
                    tenant_id=tenant_id,
                    task_id=task_id,
                    worker_id=self.worker_id,
                    lease_token=lease_token,
                    now=now,
                    error_code=(
                        "WORKER_CANCELLED"
                        if result.status is WorkerExecutionStatusEnum.CANCELLED
                        else "WORKER_EXECUTION_FAILED"
                    ),
                    session=active_session,
                )
            )
            return state


__all__ = ["DurableWorkerRunner"]
