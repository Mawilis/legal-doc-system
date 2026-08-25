"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Runtime Execution Framework - Task Metadata Contract (FG149A).
    Defines the immutable, pure-data unit of work dispatched by the Scheduler.
    Carries engine descriptors, execution correlation IDs, and lifecycle states.

Biblical Scale & Architecture:
    Institutional grade task specification. Zero execution side-effects inside model.
    Colossians 3:23 - "Whatever you do, work at it with all your heart, as working for the Lord."

Collaboration & Maintenance:
    - [Architecture]: Decoupled unit of work contract isolating metadata from dispatch.
    - Consumed by: Scheduler (FG149D), TaskResult (FG149B), Telemetry Buses.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from tools.eos.registry.engine_descriptor import EngineDescriptor

logger = logging.getLogger("WilsyRuntimeTask")


class TaskStatus(str, Enum):
    """Lifecycle statuses for a runtime Task."""

    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class Task:
    """
    Immutable specification of a single engine unit of work.
    Guarantees thread-safe transition tracking and deterministic execution binding.
    """

    task_id: str
    engine_descriptor: EngineDescriptor
    execution_id: str
    status: TaskStatus
    created_at: str
    priority: int

    # [FUNCTION EXPLANATION]: Factory constructor enforcing UTC timestamping and deterministic UUID assignments.
    @classmethod
    def create(
        cls,
        engine_descriptor: EngineDescriptor,
        execution_id: str,
        priority: Optional[int] = None,
        task_id: Optional[str] = None,
    ) -> Task:
        """
        Factory method constructing an immutable Task instance.

        Args:
            engine_descriptor (EngineDescriptor): Registry engine descriptor for this task.
            execution_id (str): Global execution run correlation ID.
            priority (Optional[int]): Execution priority override. Defaults to descriptor priority.
            task_id (Optional[str]): Custom task identifier.

        Returns:
            Task: An immutable Task metadata instance.
        """
        assigned_id = task_id or f"task-{engine_descriptor.identifier}-{uuid.uuid4().hex[:8]}"
        now_utc = datetime.now(timezone.utc).isoformat()
        assigned_priority = priority if priority is not None else getattr(engine_descriptor, "priority", 100)

        return cls(
            task_id=assigned_id,
            engine_descriptor=engine_descriptor,
            execution_id=execution_id,
            status=TaskStatus.PENDING,
            created_at=now_utc,
            priority=assigned_priority,
        )

    # [FUNCTION EXPLANATION]: Functional state mutation method returning a new immutable Task instance.
    def with_status(self, new_status: TaskStatus) -> Task:
        """
        Returns a new Task instance with updated lifecycle status.

        Args:
            new_status (TaskStatus): Target status enumeration.

        Returns:
            Task: A new frozen Task instance reflecting the state transition.
        """
        return Task(
            task_id=self.task_id,
            engine_descriptor=self.engine_descriptor,
            execution_id=self.execution_id,
            status=new_status,
            created_at=self.created_at,
            priority=self.priority,
        )

    # [FUNCTION EXPLANATION]: Convenience accessor returning the target engine identifier string.
    @property
    def engine_id(self) -> str:
        """Returns the unique identifier of the target engine."""
        return self.engine_descriptor.identifier

    # [FUNCTION EXPLANATION]: Serializes task metadata for audit trails, logging, and remote dispatch.
    def to_dict(self) -> Dict[str, Any]:
        """Serializes task metadata into a JSON-compatible dictionary."""
        return {
            "task_id": self.task_id,
            "engine_id": self.engine_id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "priority": self.priority,
            "engine_descriptor": self.engine_descriptor.to_dict(),
        }
