"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Parallel Execution - Synchronization Barrier & Governance Gate (FG156).
    Enforces thread barrier synchronization across concurrent worker tasks.
    Guarantees Quality, Review, and Release gates wait until all parallel runs resolve.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready barrier synchronization engine. Zero child's place.
    Habakkuk 2:3 - "For still the vision awaits its appointed time... if it seems slow, wait for it; it will surely come."

Collaboration & Maintenance:
    - [Architecture]: Thread-safe barrier and future aggregator for governance checkpoints.
    - [Compliance]: Strict timeout management and fault aggregation prior to release.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import Future, wait, FIRST_EXCEPTION
from typing import Any, Dict, List, Tuple

from tools.eos.parallel.future_result import FutureResult, FutureStatus

logger = logging.getLogger("WilsyOS.Synchronization")


class SynchronizationBarrier:
    """
    Coordinates thread barrier synchronization across parallel kernel executions,
    blocking downstream governance gates (Quality, Review, Release) until completion.
    """

    # [FUNCTION EXPLANATION]: Blocks execution thread until all submitted parallel futures complete or time out.
    @staticmethod
    def wait_for_all(
        futures: List[Future],
        timeout_seconds: float = 30.0,
    ) -> Tuple[List[FutureResult], bool]:
        """
        Blocks until all parallel worker tasks complete execution or the timeout is reached.

        Args:
            futures (List[Future]): List of concurrent.futures.Future objects.
            timeout_seconds (float): Maximum time to wait in seconds.

        Returns:
            Tuple[List[FutureResult], bool]: Aggregated FutureResults and a boolean indicating overall success.
        """
        logger.info(f"Synchronization Barrier: Blocking for {len(futures)} parallel tasks (Timeout: {timeout_seconds}s)...")
        start_time = time.perf_counter()

        done, not_done = wait(futures, timeout=timeout_seconds)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(f"Barrier cleared in {elapsed_ms}ms. Completed: {len(done)}, Timed out/Pending: {len(not_done)}.")

        results: List[FutureResult] = []
        all_passed = True

        for fut in done:
            try:
                res: FutureResult = fut.result()
                results.append(res)
                if res.status != FutureStatus.COMPLETED:
                    all_passed = False
            except Exception as ex:
                all_passed = False
                logger.error(f"Uncaught exception during worker execution: {ex}")

        # Handle any tasks that timed out
        if not_done:
            all_passed = False
            for fut in not_done:
                results.append(
                    FutureResult(
                        task_id="timeout_task",
                        worker_id="unknown_worker",
                        status=FutureStatus.FAILED,
                        error=f"Task timed out after exceeding barrier limits ({timeout_seconds}s).",
                    )
                )

        return results, all_passed

    # [FUNCTION EXPLANATION]: Aggregates parallel execution results into a audit-ready dictionary report.
    @staticmethod
    def synthesize_report(results: List[FutureResult]) -> Dict[str, Any]:
        """
        Synthesizes individual worker FutureResults into a structured telemetry report.

        Args:
            results (List[FutureResult]): List of task execution envelopes.

        Returns:
            Dict[str, Any]: Consolidated parallel audit report.
        """
        successful_tasks = [r.task_id for r in results if r.status == FutureStatus.COMPLETED]
        failed_tasks = [r.task_id for r in results if r.status == FutureStatus.FAILED]
        total_time_ms = sum(r.execution_time_ms for r in results)

        return {
            "total_tasks_evaluated": len(results),
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "all_tasks_passed": len(failed_tasks) == 0,
            "aggregate_worker_time_ms": round(total_time_ms, 2),
            "task_telemetry": [r.to_dict() for r in results],
        }
