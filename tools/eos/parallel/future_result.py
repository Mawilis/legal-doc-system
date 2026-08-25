"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Parallel Execution - Future Result Envelope (FG156).
    Encapsulates asynchronous worker execution state, thread telemetry, error handling,
    and output payloads for parallel tasks.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready thread-safe result container. Zero child's place.
    Ecclesiastes 3:1 - "To every thing there is a season, and a time to every purpose under the heaven."

Collaboration & Maintenance:
    - [Architecture]: Thread-safe asynchronous result wrapper and telemetry payload.
    - [Compliance]: Guarantees deterministic error capture across parallel threads.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class FutureStatus(str, Enum):
    """Execution state of a parallel asynchronous task."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class FutureResult(Generic[T]):
    """
    Immutable envelope encapsulating the outcome and performance metrics of a parallel task execution.
    """
    task_id: str
    worker_id: str
    status: FutureStatus
    result: Optional[T] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # [FUNCTION EXPLANATION]: Unwraps the result payload or raises an exception if the parallel task failed.
    def unwrap(self) -> T:
        """
        Safely retrieves the inner result payload.

        Returns:
            T: The successful computation output.

        Raises:
            RuntimeError: If the task failed, was cancelled, or has no result available.
        """
        if self.status == FutureStatus.COMPLETED and self.result is not None:
            return self.result
        if self.status == FutureStatus.FAILED:
            raise RuntimeError(f"Parallel task [{self.task_id}] failed on worker [{self.worker_id}]: {self.error}")
        raise RuntimeError(f"Parallel task [{self.task_id}] is in invalid state for unwrap: {self.status.value}")

    # [FUNCTION EXPLANATION]: Checks if the task has reached a terminal state (COMPLETED or FAILED).
    def is_done(self) -> bool:
        """Returns True if the task completed or failed, False otherwise."""
        return self.status in (FutureStatus.COMPLETED, FutureStatus.FAILED, FutureStatus.CANCELLED)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the future result into a dictionary structure."""
        return asdict(self)

    def to_json(self) -> str:
        """Serializes the future result into a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
