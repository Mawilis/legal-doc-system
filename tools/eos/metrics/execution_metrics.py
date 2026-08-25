"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Metrics Framework - Execution Metrics.
    Aggregates overall execution pipeline statistics, engine success/failure counts,
    and aggregate throughput across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise execution telemetry container. Zero child's place.
    Provides immutable aggregation of pipeline execution statistics.

Collaboration & Maintenance:
    - [Architecture]: Dataclass tracking execution counts, statuses, and aggregate results.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ExecutionMetrics:
    """
    Container for execution pipeline metrics, including total engines, successes, failures, and status counts.
    """

    execution_id: str
    total_engines: int = 0
    success_count: int = 0
    failure_count: int = 0
    skipped_count: int = 0
    rolled_back_count: int = 0
    aggregate_duration_ms: float = 0.0
    status_breakdown: Dict[str, int] = field(default_factory=lambda: {
        "SUCCESS": 0,
        "FAILED": 0,
        "SKIPPED": 0,
        "ROLLED_BACK": 0,
    })

    def record_engine_result(self, status: str, duration_ms: float) -> None:
        """
        Record the completion of an engine execution.

        Args:
            status (str): The resulting engine status string.
            duration_ms (float): Execution duration in milliseconds.
        """
        self.aggregate_duration_ms += duration_ms
        if status in self.status_breakdown:
            self.status_breakdown[status] += 1

        if status == "SUCCESS":
            self.success_count += 1
        elif status == "FAILED":
            self.failure_count += 1
        elif status == "SKIPPED":
            self.skipped_count += 1
        elif status == "ROLLED_BACK":
            self.rolled_back_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes execution metrics into an institutional dictionary payload.

        Returns:
            Dict[str, Any]: Serialized metrics.
        """
        return {
            "execution_id": self.execution_id,
            "total_engines": self.total_engines,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "skipped_count": self.skipped_count,
            "rolled_back_count": self.rolled_back_count,
            "aggregate_duration_ms": self.aggregate_duration_ms,
            "status_breakdown": dict(self.status_breakdown),
        }
