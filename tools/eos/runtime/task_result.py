"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Runtime Execution Framework - Task Execution Result Contract (FG149B).
    Defines the frozen, immutable output artifact of a completed or failed Task.
    Captures telemetry, wall-clock duration, generated artifact links, and error state.

Biblical Scale & Architecture:
    Institutional-grade runtime task result model. Pure, immutable data record.
    Ecclesiastes 3:14 - "I know that everything God does will endure forever; nothing can be added to it and nothing taken from it."

Collaboration & Maintenance:
    - [Architecture]: Decoupled task outcome record isolating status from runtime state.
    - Consumed by: Scheduler (FG149D), Telemetry Engine, Unified Report Engine.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from tools.eos.runtime.task import TaskStatus

logger = logging.getLogger("WilsyRuntimeTaskResult")


@dataclass(frozen=True)
class TaskResult:
    """
    Immutable record of a Task execution outcome.
    Guarantees thread-safe auditing, telemetry tracking, and failure isolation.
    """

    task_id: str
    engine_id: str
    execution_id: str
    status: TaskStatus
    started_at: str
    completed_at: str
    duration_ms: float
    success: bool
    artifact_ids: Tuple[str, ...] = ()
    error: Optional[str] = None
    telemetry: Dict[str, Any] = field(default_factory=dict)

    # [FUNCTION EXPLANATION]: Factory constructor for successful task completions.
    @classmethod
    def create_success(
        cls,
        task_id: str,
        engine_id: str,
        execution_id: str,
        started_at: str,
        completed_at: str,
        duration_ms: float,
        artifact_ids: Tuple[str, ...] = (),
        telemetry: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """
        Constructs an immutable TaskResult for a successfully executed task.

        Args:
            task_id (str): Unique task identifier.
            engine_id (str): Identifier of the executing engine.
            execution_id (str): Global execution run correlation ID.
            started_at (str): ISO 8601 start timestamp.
            completed_at (str): ISO 8601 completion timestamp.
            duration_ms (float): Wall-clock execution duration in milliseconds.
            artifact_ids (Tuple[str, ...]): Produced artifact keys.
            telemetry (Optional[Dict[str, Any]]): Engine telemetry metrics.

        Returns:
            TaskResult: Immutable success outcome record.
        """
        return cls(
            task_id=task_id,
            engine_id=engine_id,
            execution_id=execution_id,
            status=TaskStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            success=True,
            artifact_ids=artifact_ids,
            error=None,
            telemetry=telemetry or {},
        )

    # [FUNCTION EXPLANATION]: Factory constructor for failed task executions.
    @classmethod
    def create_failure(
        cls,
        task_id: str,
        engine_id: str,
        execution_id: str,
        started_at: str,
        completed_at: str,
        duration_ms: float,
        error: str,
        telemetry: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """
        Constructs an immutable TaskResult for a failed task execution.

        Args:
            task_id (str): Unique task identifier.
            engine_id (str): Identifier of the failing engine.
            execution_id (str): Global execution run correlation ID.
            started_at (str): ISO 8601 start timestamp.
            completed_at (str): ISO 8601 failure timestamp.
            duration_ms (float): Wall-clock execution duration prior to failure.
            error (str): Error message or stack trace string.
            telemetry (Optional[Dict[str, Any]]): Telemetry captured prior to failure.

        Returns:
            TaskResult: Immutable failure outcome record.
        """
        return cls(
            task_id=task_id,
            engine_id=engine_id,
            execution_id=execution_id,
            status=TaskStatus.FAILED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            success=False,
            artifact_ids=(),
            error=error,
            telemetry=telemetry or {},
        )

    # [FUNCTION EXPLANATION]: Serializes execution outcome into a JSON-compatible dictionary.
    def to_dict(self) -> Dict[str, Any]:
        """Serializes task result into a JSON-serializable dictionary."""
        return {
            "task_id": self.task_id,
            "engine_id": self.engine_id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "artifact_ids": list(self.artifact_ids),
            "error": self.error,
            "telemetry": self.telemetry,
        }
