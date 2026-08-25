from __future__ import annotations

"""
===============================================================================
WILSY OS RUNTIME — PIPELINE EXECUTION STATISTICS (FG179)
===============================================================================
Epitome:
    High-precision telemetry tracker capturing real-time pipeline performance
    metrics, throughput ratios, parallelism levels, and queue metrics.

Biblical Worth Billions:
    "He counteth the number of the stars; he calleth them all by their names."
    — Psalm 147:4
    Microsecond-level precision telemetry turns execution metrics into executive
    intelligence for enterprise scaling.

Collaboration & Ownership:
    - Founder & Lead Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Execution Pipeline Runtime
    - Phase / Milestone: FG179 - Execution Pipeline Manager
    - Target Directory: tools/eos/runtime/
    - File Path: tools/eos/runtime/pipeline_statistics.py
    - Runtime Alignment: Python 3.10+ Production Environment
===============================================================================
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PipelineStatistics:
    """
    Captures runtime performance and quantitative metrics for a single pipeline run.
    """

    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_engines: int = 0
    executed_engines: int = 0
    successful_engines: int = 0
    failed_engines: int = 0
    retried_engines: int = 0
    parallelism_level: int = 1
    queue_depth: int = 0

    def start(self, total_engines: int = 0, queue_depth: int = 0, parallelism: int = 1) -> None:
        """
        Registers the start timestamp and initializes baseline operational bounds.
        """
        self.start_time = time.perf_counter()
        self.total_engines = total_engines
        self.queue_depth = queue_depth
        self.parallelism_level = max(1, parallelism)

    def record_engine_completion(self, success: bool, retried: bool = False) -> None:
        """
        Increments engine execution outcome counters.
        """
        self.executed_engines += 1
        if success:
            self.successful_engines += 1
        else:
            self.failed_engines += 1

        if retried:
            self.retried_engines += 1

    def stop(self) -> None:
        """
        Registers the pipeline completion timestamp.
        """
        self.end_time = time.perf_counter()

    @property
    def duration_ms(self) -> float:
        """
        Calculates wall-clock runtime in milliseconds.
        """
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time is not None else time.perf_counter()
        return (end - self.start_time) * 1000.0

    @property
    def engine_throughput(self) -> float:
        """
        Calculates engine execution throughput per second.
        """
        duration_sec = self.duration_ms / 1000.0
        if duration_sec <= 0:
            return 0.0
        return self.executed_engines / duration_sec

    @property
    def success_ratio(self) -> float:
        """
        Ratio of successfully executed engines over total attempted.
        """
        if self.executed_engines == 0:
            return 0.0
        return self.successful_engines / self.executed_engines

    @property
    def failure_ratio(self) -> float:
        """
        Ratio of failed engines over total attempted.
        """
        if self.executed_engines == 0:
            return 0.0
        return self.failed_engines / self.executed_engines

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes pipeline metrics for JSON export and audit logs.
        """
        return {
            "duration_ms": round(self.duration_ms, 3),
            "engine_throughput_per_sec": round(self.engine_throughput, 2),
            "total_engines": self.total_engines,
            "executed_engines": self.executed_engines,
            "successful_engines": self.successful_engines,
            "failed_engines": self.failed_engines,
            "retried_engines": self.retried_engines,
            "parallelism_level": self.parallelism_level,
            "queue_depth": self.queue_depth,
            "success_ratio": round(self.success_ratio, 4),
            "failure_ratio": round(self.failure_ratio, 4),
        }


__all__ = ["PipelineStatistics"]
