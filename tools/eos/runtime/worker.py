"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Base Engine Worker & Task Execution Harness (FG171C).
    Defines abstract base classes and standard execution routines for engine workers
    operating within the event-driven scheduler runtime kernel.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready base worker component. Zero child's place.
    Ecclesiastes 9:10 - "Whatsoever thy hand findeth to do, do it with thy might..."
    Colossians 3:23 - "And whatsoever ye do, do it heartily, as to the Lord..."

Collaboration & Maintenance:
    - [Architecture]: Standardized async worker execution contract.
    - [Diagnostics]: Full latency tracking and safety wrappers.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import abc
import logging
import time
from typing import Any, Dict, Optional

from .worker_result import (
    EngineWorkerResultDTO,
    WorkerExecutionStatusEnum,
    WorkerResultDTO,
)

logger = logging.getLogger("WilsyOS.Runtime.Worker")


class BaseEngineWorker(abc.ABC):
    """
    Abstract base class for all legal OS engine worker implementations.
    Provides unified exception handling, benchmarking, and result packaging.
    """

    def __init__(self, engine_name: Optional[str] = None) -> None:
        self._engine_name = engine_name or self.__class__.__name__

    @property
    def engine_name(self) -> str:
        """Returns the registered engine name identifier."""
        return self._engine_name

    # [FUNCTION EXPLANATION]: Abstract execution method to be overridden by domain engines.
    @abc.abstractmethod
    async def process_task(self, task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes domain logic for a task and returns the output payload.
        Must be implemented by concrete worker subclasses.
        """
        raise NotImplementedError("Subclasses must implement process_task()")

    # [FUNCTION EXPLANATION]: Main execution harness wrapping task execution in safety, benchmarking, and DTO formatting.
    async def execute(self, task_id: str, payload: Dict[str, Any]) -> EngineWorkerResultDTO:
        """
        Invokes task processing with automated benchmarking, exception handling,
        and standardized EngineWorkerResultDTO packaging.
        """
        start_time = time.perf_counter()
        logger.info(f"Worker [{self.engine_name}] starting task [{task_id}] execution.")

        try:
            output = await self.process_task(task_id, payload)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(f"Worker [{self.engine_name}] completed task [{task_id}] in {duration_ms}ms.")

            return EngineWorkerResultDTO(
                task_id=task_id,
                status=WorkerExecutionStatusEnum.SUCCESS,
                execution_duration_ms=duration_ms,
                output=output,
                error_details=None,
            )

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            error_msg = f"Task [{task_id}] failed on worker [{self.engine_name}]: {str(exc)}"
            logger.exception(error_msg)

            return EngineWorkerResultDTO(
                task_id=task_id,
                status=WorkerExecutionStatusEnum.FAILURE,
                execution_duration_ms=duration_ms,
                output={},
                error_details=error_msg,
            )
