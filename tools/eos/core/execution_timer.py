"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Core Framework - Execution Timer.
    High-precision performance telemetry context manager for engine executions
    across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise timer. Zero child's place.
    Utilizes monotonic performance counters for accurate sub-millisecond telemetry.

Collaboration & Maintenance:
    - [Telemetry]: High-precision timing context manager.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Any, Optional


class ExecutionTimer:
    """
    Context manager and utility to measure precise execution duration in milliseconds.
    """

    def __init__(self) -> None:
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.duration_ms: float = 0.0

    def __enter__(self) -> ExecutionTimer:
        self.start_time = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        self.end_time = time.perf_counter()
        self.duration_ms = (self.end_time - self.start_time) * 1000.0
