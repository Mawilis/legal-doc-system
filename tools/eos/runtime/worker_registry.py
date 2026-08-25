"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Worker Registry for Event Driven Scheduler Architecture (FG171C).
    Registers and dispatches tasks to engine worker implementations with
    type-safe invocation, error handling, and latency benchmarking.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready worker registry layer. Zero child's place.
    Colossians 3:23 - "And whatsoever ye do, do it heartily, as to the Lord..."

Collaboration & Maintenance:
    - [Architecture]: Dynamic dispatch registry mapping engine names to executable worker instances.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from .worker_result import WorkerExecutionStatusEnum, WorkerResultDTO

logger = logging.getLogger("WilsyOS.Runtime.WorkerRegistry")


class EngineWorkerRegistry:
    """
    Central registry for managing engine workers and dispatching tasks asynchronously.
    """

    def __init__(self) -> None:
        self._workers: Dict[str, Any] = {}
        logger.info("EngineWorkerRegistry initialized successfully.")

    # [FUNCTION EXPLANATION]: Registers an engine worker instance under a target engine name.
    def register_worker(self, engine_name_or_worker: Any, worker: Optional[Any] = None) -> None:
        """
        Registers a worker with the registry.
        Supports both register_worker("engine_name", worker) and register_worker(worker).
        """
        if worker is not None:
            engine_name = str(engine_name_or_worker)
            target_worker = worker
        else:
            target_worker = engine_name_or_worker
            engine_name = getattr(target_worker, "engine_name", target_worker.__class__.__name__)

        self._workers[engine_name] = target_worker
        logger.info(f"Worker [{target_worker.__class__.__name__}] registered for engine [{engine_name}]")

    # [FUNCTION EXPLANATION]: Dispatches a task to the registered engine worker and captures output/latency.
    async def dispatch_task(
        self,
        engine_name: str,
        task_id: str,
        payload: Dict[str, Any],
    ) -> WorkerResultDTO:
        """
        Executes a registered worker for the given engine, returning a standardized WorkerResultDTO.
        """
        worker = self._workers.get(engine_name)
        if not worker:
            logger.error(f"No worker registered for engine [{engine_name}]")
            return WorkerResultDTO(
                task_id=task_id,
                status=WorkerExecutionStatusEnum.FAILED,
                execution_duration_ms=0.0,
                output={},
                error_details=f"No worker registered for engine '{engine_name}'",
            )

        start_time = time.perf_counter()
        try:
            if hasattr(worker, "execute"):
                raw_result = await worker.execute(task_id, payload)
            elif callable(worker):
                raw_result = await worker(task_id, payload)
            else:
                raise TypeError(f"Worker for '{engine_name}' is not callable and has no 'execute' method.")

            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if isinstance(raw_result, WorkerResultDTO):
                return raw_result

            output_dict = getattr(raw_result, "output", raw_result)
            if not isinstance(output_dict, dict):
                output_dict = {"data": output_dict}

            status = getattr(raw_result, "status", WorkerExecutionStatusEnum.SUCCESS)
            error = getattr(raw_result, "error_details", None)

            return WorkerResultDTO(
                task_id=task_id,
                status=status if isinstance(status, WorkerExecutionStatusEnum) else WorkerExecutionStatusEnum.SUCCESS,
                execution_duration_ms=duration_ms,
                output=output_dict,
                error_details=error,
            )

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.exception(f"Error executing worker for engine [{engine_name}]: {str(exc)}")
            return WorkerResultDTO(
                task_id=task_id,
                status=WorkerExecutionStatusEnum.FAILED,
                execution_duration_ms=duration_ms,
                output={},
                error_details=str(exc),
            )
