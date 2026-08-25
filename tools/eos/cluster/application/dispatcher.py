"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/application/dispatcher.py

Epitome:
    Execution dispatcher managing task invocation, active worker load accounting,
    execution latency tracking, and artifact/event bus notification integration.

Biblical Worth Billions:
    "So shall my word be that goeth forth out of my mouth: it shall not return 
    unto me void, but it shall accomplish that which I please."
    — Isaiah 55:11

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from tools.eos.cluster.domain.worker import Worker
from tools.eos.cluster.domain.worker_status import WorkerStatus

logger = logging.getLogger("wilsy_os.cluster.dispatcher")


@dataclass
class TaskExecutionResult:
    """Encapsulates the immutable outcome of a task execution unit."""
    task_id: str
    action_name: str
    assigned_worker_id: str
    success: bool
    result_data: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Dispatcher:
    """
    Synchronous and asynchronous execution engine dispatching workload functions 
    to selected target workers with strict load accounting.
    """

    def __init__(
        self,
        event_bus: Optional[Any] = None,
        artifact_bus: Optional[Any] = None
    ) -> None:
        self.event_bus = event_bus
        self.artifact_bus = artifact_bus

    def dispatch(
        self,
        worker: Worker,
        action_name: str,
        executable: Callable[..., Any],
        parameters: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> TaskExecutionResult:
        """
        Dispatches an executable callable to a specified worker, handling load limits 
        and timing telemetry.
        """
        tid = task_id or f"task-dispatch-{time.time_ns()}"
        params = parameters or {}

        if not worker.increment_load():
            logger.error(
                f"[DISPATCH_REJECTED] Worker ID: {worker.worker_id} at max capacity "
                f"({worker.current_load}/{worker.max_capacity})."
            )
            return TaskExecutionResult(
                task_id=tid,
                action_name=action_name,
                assigned_worker_id=worker.worker_id,
                success=False,
                error_message=f"Worker {worker.worker_id} capacity exceeded."
            )

        start_time = time.perf_counter()
        original_status = worker.status
        worker.transition_to(WorkerStatus.EXECUTING)

        self._publish_event("WorkerExecuting", {
            "task_id": tid,
            "action_name": action_name,
            "worker_id": worker.worker_id
        })

        try:
            logger.info(
                f"[DISPATCH_START] Task ID: {tid} | Action: {action_name} | "
                f"Worker ID: {worker.worker_id}"
            )
            result = executable(**params)
            duration_ms = (time.perf_counter() - start_time) * 1000.0

            logger.info(
                f"[DISPATCH_SUCCESS] Task ID: {tid} completed in {duration_ms:.2f}ms "
                f"on Worker ID: {worker.worker_id}"
            )

            self._publish_event("WorkerCompleted", {
                "task_id": tid,
                "action_name": action_name,
                "worker_id": worker.worker_id,
                "duration_ms": duration_ms
            })

            self._publish_artifact(tid, action_name, result)

            return TaskExecutionResult(
                task_id=tid,
                action_name=action_name,
                assigned_worker_id=worker.worker_id,
                success=True,
                result_data=result,
                execution_time_ms=duration_ms
            )

        except Exception as err:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            error_str = str(err)
            logger.error(
                f"[DISPATCH_FAILED] Task ID: {tid} failed on Worker ID: {worker.worker_id} "
                f"after {duration_ms:.2f}ms: {error_str}", exc_info=True
            )

            self._publish_event("WorkerFailed", {
                "task_id": tid,
                "action_name": action_name,
                "worker_id": worker.worker_id,
                "error": error_str,
                "duration_ms": duration_ms
            })

            return TaskExecutionResult(
                task_id=tid,
                action_name=action_name,
                assigned_worker_id=worker.worker_id,
                success=False,
                error_message=error_str,
                execution_time_ms=duration_ms
            )

        finally:
            worker.decrement_load()
            if worker.current_load == 0:
                worker.transition_to(WorkerStatus.READY)

    def _publish_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Publishes lifecycle events to cluster event bus if attached."""
        if self.event_bus and hasattr(self.event_bus, "publish"):
            try:
                self.event_bus.publish(event_type, payload)
            except Exception as e:
                logger.warning(f"[EVENT_BUS_PUBLISH_FAILED] Event {event_type}: {e}")

    def _publish_artifact(self, task_id: str, action_name: str, result_data: Any) -> None:
        """Publishes execution output artifacts to artifact bus if attached."""
        if self.artifact_bus and hasattr(self.artifact_bus, "store_artifact"):
            try:
                self.artifact_bus.store_artifact(
                    artifact_id=f"art-{task_id}",
                    metadata={"action_name": action_name, "task_id": task_id},
                    data=result_data
                )
            except Exception as e:
                logger.warning(f"[ARTIFACT_BUS_PUBLISH_FAILED] Task {task_id}: {e}")
