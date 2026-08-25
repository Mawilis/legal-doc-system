"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Logging Framework - Execution Logger.
    Specialized logger for tracking pipeline execution runs, engine telemetry,
    and runtime performance across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise execution logger. Zero child's place.
    Provides structured step and execution telemetry logging.

Collaboration & Maintenance:
    - [Architecture]: Contextual execution logger for pipeline auditing.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from .logger import get_logger

logger = get_logger("Execution")


class ExecutionLogger:
    """
    Specialized logger for recording institutional execution events, stages, and metrics.
    """

    def __init__(self, execution_id: str) -> None:
        self.execution_id = execution_id

    def log_start(self, pipeline_name: str, total_engines: int) -> None:
        """Log the start of an execution pipeline."""
        logger.info(f"[{self.execution_id}] Pipeline Started: '{pipeline_name}' ({total_engines} engines scheduled).")

    def log_engine_start(self, engine_id: str) -> None:
        """Log the start of an individual engine execution."""
        logger.info(f"[{self.execution_id}] Engine Starting: '{engine_id}'")

    def log_engine_success(self, engine_id: str, duration_ms: float) -> None:
        """Log successful completion of an engine."""
        logger.info(f"[{self.execution_id}] Engine Success: '{engine_id}' completed in {duration_ms:.2f}ms.")

    def log_engine_failure(self, engine_id: str, error: str, duration_ms: float) -> None:
        """Log engine execution failure."""
        logger.error(f"[{self.execution_id}] Engine Failed: '{engine_id}' -> {error} (Duration: {duration_ms:.2f}ms)")

    def log_complete(self, pipeline_name: str, total_time_ms: float, success: bool) -> None:
        """Log pipeline execution completion."""
        status = "SUCCESS" if success else "FAILED"
        level = logger.info if success else logger.error
        level(f"[{self.execution_id}] Pipeline Completed: '{pipeline_name}' [{status}] in {total_time_ms:.2f}ms.")
