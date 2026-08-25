"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Parallel Execution - Worker Pool Manager (FG156).
    Manages dedicated worker threads and process pools for simultaneous multi-engine
    computations (Repository, AI, Knowledge, Sentinel).
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready thread and process pool manager. Zero child's place.
    Nehemiah 4:6 - "So we built the wall... for the people had a mind to work."

Collaboration & Maintenance:
    - [Architecture]: Concurrent worker pool management and thread lifecycle control.
    - [Compliance]: Safe resource cleanup and thread isolation for parallel tasks.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

from tools.eos.parallel.future_result import FutureResult, FutureStatus

logger = logging.getLogger("WilsyOS.WorkerPool")


class WorkerPool:
    """
    Manages concurrent execution workers for high-bandwidth kernel domains.
    """

    def __init__(self, max_workers: int = 4) -> None:
        """
        Initializes the worker pool with a fixed thread allocation.

        Args:
            max_workers (int): Maximum number of concurrent worker threads.
        """
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="WilsyWorker",
        )
        logger.info(f"WorkerPool initialized with {self.max_workers} worker threads.")

    # [FUNCTION EXPLANATION]: Submits a callable task for concurrent execution in the worker pool.
    def submit_task(
        self,
        task_id: str,
        fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Future:
        """
        Submits a function for execution and returns a raw Python Future object wrapping a FutureResult.

        Args:
            task_id (str): Unique task identifier.
            fn (Callable[..., Any]): Target callable.

        Returns:
            Future: Python concurrent.futures.Future instance.
        """
        logger.info(f"Submitting task [{task_id}] to WorkerPool.")
        return self._executor.submit(self._wrap_execution, task_id, fn, *args, **kwargs)

    # [FUNCTION EXPLANATION]: Internal wrapper capturing timing, outputs, and errors into a FutureResult.
    @staticmethod
    def _wrap_execution(
        task_id: str,
        fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> FutureResult:
        """
        Executes target function inside worker context, calculating execution time and wrapping errors.
        """
        start_time = time.perf_counter()
        worker_name = f"worker-thread-{task_id}"

        try:
            result = fn(*args, **kwargs)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)
            return FutureResult(
                task_id=task_id,
                worker_id=worker_name,
                status=FutureStatus.COMPLETED,
                result=result,
                execution_time_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)
            logger.error(f"Task [{task_id}] failed during parallel execution: {e}")
            return FutureResult(
                task_id=task_id,
                worker_id=worker_name,
                status=FutureStatus.FAILED,
                error=str(e),
                execution_time_ms=elapsed_ms,
            )

    # [FUNCTION EXPLANATION]: Safely shuts down the pool and releases all allocated thread resources.
    def shutdown(self, wait: bool = True) -> None:
        """
        Gracefully shuts down the thread pool executor.
        """
        logger.info("Shutting down WorkerPool...")
        self._executor.shutdown(wait=wait)
        logger.info("WorkerPool shutdown complete.")
