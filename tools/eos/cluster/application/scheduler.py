"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/application/scheduler.py

Epitome:
    Decoupled cluster scheduler queueing execution requests and delegating dispatch 
    to cluster orchestrators without binding to physical execution locations.

Biblical Worth Billions:
    "To every thing there is a season, and a time to every purpose under the heaven."
    — Ecclesiastes 3:1

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import threading
import queue
import logging
import uuid
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Set, List

from tools.eos.cluster.application.dispatcher import TaskExecutionResult
from tools.eos.cluster.application.load_balancer import LoadBalancingStrategy

logger = logging.getLogger("wilsy_os.cluster.scheduler")


@dataclass(order=True)
class ScheduledJob:
    """Priority queue container for decoupled cluster job scheduling."""
    priority: int
    job_id: str = field(compare=False)
    action_name: str = field(compare=False)
    executable: Callable[..., Any] = field(compare=False)
    parameters: Dict[str, Any] = field(compare=False, default_factory=dict)
    required_capabilities: Set[str] = field(compare=False, default_factory=set)
    tenant_id: Optional[str] = field(compare=False, default=None)
    created_at: float = field(compare=False, default_factory=time.time)
    strategy: Optional[LoadBalancingStrategy] = field(compare=False, default=None)


class Scheduler:
    """
    Decoupled cluster scheduler queueing incoming ExecutionContext work units 
    and feeding them directly into the cluster orchestrator.
    """

    def __init__(self, cluster_manager: Any) -> None:
        self.cluster_manager = cluster_manager
        self._job_queue: queue.PriorityQueue[ScheduledJob] = queue.PriorityQueue()
        self._lock = threading.RLock()
        self._active_job_count = 0
        self._completed_jobs: Dict[str, TaskExecutionResult] = {}

    def schedule(
        self,
        action_name: str,
        executable: Callable[..., Any],
        parameters: Optional[Dict[str, Any]] = None,
        required_capabilities: Optional[Set[str]] = None,
        tenant_id: Optional[str] = None,
        priority: int = 10,
        strategy: Optional[LoadBalancingStrategy] = None
    ) -> str:
        """
        Enqueues a job for decoupled execution across the worker cluster.
        Returns the generated unique job_id.
        """
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        req_caps = required_capabilities or set()
        params = parameters or {}

        scheduled_job = ScheduledJob(
            priority=priority,
            job_id=job_id,
            action_name=action_name,
            executable=executable,
            parameters=params,
            required_capabilities=req_caps,
            tenant_id=tenant_id,
            strategy=strategy
        )

        with self._lock:
            self._job_queue.put(scheduled_job)
            self._active_job_count += 1

        logger.info(
            f"[SCHEDULER_JOB_QUEUED] Job ID: {job_id} | Action: {action_name} | "
            f"Priority: {priority} | Queue Depth: {self.pending_job_count}"
        )
        return job_id

    def execute_next(self) -> Optional[TaskExecutionResult]:
        """
        Pulls the highest priority job from queue and submits to ClusterManager.
        """
        try:
            job: ScheduledJob = self._job_queue.get_nowait()
        except queue.Empty:
            return None

        try:
            logger.info(
                f"[SCHEDULER_EXECUTING_JOB] Job ID: {job.job_id} | Action: {job.action_name}"
            )
            result = self.cluster_manager.execute_job(
                action_name=job.action_name,
                executable=job.executable,
                parameters=job.parameters,
                required_capabilities=job.required_capabilities,
                tenant_id=job.tenant_id,
                strategy=job.strategy
            )

            with self._lock:
                self._completed_jobs[job.job_id] = result
                self._active_job_count = max(0, self._active_job_count - 1)

            return result

        except Exception as err:
            logger.error(f"[SCHEDULER_JOB_ERROR] Job ID: {job.job_id}: {err}", exc_info=True)
            error_result = TaskExecutionResult(
                task_id=job.job_id,
                action_name=job.action_name,
                assigned_worker_id="none",
                success=False,
                error_message=str(err)
            )
            with self._lock:
                self._completed_jobs[job.job_id] = error_result
                self._active_job_count = max(0, self._active_job_count - 1)
            return error_result

    def process_all_pending(self) -> List[TaskExecutionResult]:
        """Drains and executes all pending queued jobs in priority order."""
        results: List[TaskExecutionResult] = []
        while not self._job_queue.empty():
            res = self.execute_next()
            if res:
                results.append(res)
        return results

    @property
    def pending_job_count(self) -> int:
        """Returns the number of jobs waiting in the queue."""
        return self._job_queue.qsize()

    def get_job_result(self, job_id: str) -> Optional[TaskExecutionResult]:
        """Retrieves completed job outcome by job_id."""
        with self._lock:
            return self._completed_jobs.get(job_id)
