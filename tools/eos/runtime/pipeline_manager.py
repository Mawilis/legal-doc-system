from __future__ import annotations

"""
===============================================================================
WILSY OS RUNTIME — EXECUTION PIPELINE MANAGER (FG179)
===============================================================================
Epitome:
    Automated pipeline manager driving engine state machine lifecycles.
    Decouples task orchestration from the Wilsy OS kernel by consuming an
    ExecutionPlan, dispatching steps to the Scheduler, enforcing retry/fail-fast
    policies, and returning a cryptographically sealed PipelineResult.

Biblical Worth Billions:
    "The horse is prepared against the day of battle: but safety is of the Lord."
    — Proverbs 21:31
    "Where no counsel is, the people fall: but in the multitude of counsellors
    there is safety." — Proverbs 11:14
    Enterprise architecture decouples execution from orchestration.

Collaboration & Ownership:
    - Founder & Lead Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Execution Pipeline Runtime
    - Phase / Milestone: FG179 - Execution Pipeline Manager
    - Target Directory: tools/eos/runtime/
    - File Path: tools/eos/runtime/pipeline_manager.py
    - Runtime Alignment: Python 3.10+ Production Environment

Downstream Consumers:
    - Kernel Entrypoint (`tools/eos/kernel.py`)
    - Async Worker Pools & Distributed Queue Processors
    - Unified Reporting Module & Executive Dashboard Snapshots
===============================================================================
"""

import logging
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from tools.eos.core.engine import BaseKernelEngine, EngineResult, EngineStatus
from tools.eos.runtime.pipeline_result import PipelineResult
from tools.eos.runtime.pipeline_statistics import PipelineStatistics
from tools.eos.runtime.pipeline_status import PipelineStatus, PipelineStatusValidator

logger = logging.getLogger("WilsyOS.Runtime.PipelineManager")


class PipelineManager:
    """
    Drives automated execution plans across kernel engines.

    Handles:
      - Plan extraction and engine sequencing
      - Scheduler integration & fallback execution loops
      - Fail-fast and retry policy enforcement
      - Event and Artifact bus aggregation
      - Statistical telemetry generation
    """

    def __init__(
        self,
        pipeline_id: Optional[str] = None,
        scheduler: Optional[Any] = None,
        event_bus_publisher: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        artifact_bus_publisher: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        """
        Initializes the PipelineManager.

        Args:
            pipeline_id: Unique pipeline run identifier (auto-generated if omitted)
            scheduler: Optional Scheduler component for task dispatching
            event_bus_publisher: Callback for event notifications
            artifact_bus_publisher: Callback for artifact collection
        """
        self.pipeline_id = pipeline_id or f"PIPE-{uuid.uuid4().hex[:8].upper()}"
        self.scheduler = scheduler
        self._status = PipelineStatus.CREATED
        self._lock = threading.RLock()

        self.events: List[Dict[str, Any]] = []
        self.artifacts: List[Dict[str, Any]] = []

        self.event_publisher = event_bus_publisher or self._record_event
        self.artifact_publisher = artifact_bus_publisher or self._record_artifact

    @property
    def status(self) -> PipelineStatus:
        """Returns the current pipeline operational status under thread lock."""
        with self._lock:
            return self._status

    def _set_status(self, new_status: PipelineStatus) -> None:
        """Transitions state while validating against legal state transitions."""
        with self._lock:
            if not PipelineStatusValidator.can_transition(self._status, new_status):
                error_msg = (
                    f"Illegal pipeline state transition in '{self.pipeline_id}': "
                    f"Cannot move from '{self._status.value}' to '{new_status.value}'."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            logger.info(f"Pipeline '{self.pipeline_id}' state transition: {self._status.value} -> {new_status.value}")
            self._status = new_status

    def _record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Default event log handler that collects events into internal state."""
        event_entry = {"event_type": event_type, "payload": payload, "timestamp": time.time()}
        self.events.append(event_entry)
        logger.debug(f"[PIPELINE-EVENT] {event_type}: {payload}")

    def _record_artifact(self, schema_id: str, artifact_payload: Dict[str, Any]) -> None:
        """Default artifact log handler that collects generated artifacts."""
        artifact_entry = {"schema_id": schema_id, "payload": artifact_payload, "timestamp": time.time()}
        self.artifacts.append(artifact_entry)
        logger.debug(f"[PIPELINE-ARTIFACT] {schema_id}")

    def run(self, execution_plan: Any) -> PipelineResult:
        """
        Consumes an ExecutionPlan, coordinates engine execution, enforces policies,
        and returns a signed PipelineResult.

        Args:
            execution_plan: Object or dict containing plan_id, context, engines/steps,
                            and policies (fail_fast, max_retries).

        Returns:
            PipelineResult: Cryptographically sealed output container.
        """
        plan_id = getattr(execution_plan, "plan_id", getattr(execution_plan, "id", f"PLAN-{uuid.uuid4().hex[:6].upper()}"))
        context = getattr(execution_plan, "context", execution_plan)
        engines: List[BaseKernelEngine] = getattr(
            execution_plan, "engines", getattr(execution_plan, "steps", [])
        )
        fail_fast: bool = getattr(execution_plan, "fail_fast", True)
        max_retries: int = getattr(execution_plan, "max_retries", 0)

        stats = PipelineStatistics()
        stats.start(
            total_engines=len(engines),
            queue_depth=len(engines),
            parallelism=getattr(execution_plan, "parallelism", 1),
        )

        self._set_status(PipelineStatus.READY)
        self._set_status(PipelineStatus.RUNNING)

        engine_results: List[EngineResult] = []
        errors: List[str] = []

        self.event_publisher("PipelineStarted", {
            "pipeline_id": self.pipeline_id,
            "plan_id": plan_id,
            "engine_count": len(engines),
            "fail_fast": fail_fast,
        })

        for index, engine in enumerate(engines):
            if not isinstance(engine, BaseKernelEngine):
                logger.warning(f"Item at index {index} is not a BaseKernelEngine subclass. Skipping.")
                continue

            attempts = 0
            success = False
            result: Optional[EngineResult] = None
            was_retried = False

            while attempts <= max_retries and not success:
                if attempts > 0:
                    was_retried = True
                    logger.warning(
                        f"Retrying engine '{engine.engine_id}' (Attempt {attempts}/{max_retries})..."
                    )

                try:
                    if self.scheduler and hasattr(self.scheduler, "dispatch"):
                        result = self.scheduler.dispatch(engine, context)
                    else:
                        result = engine.run_lifecycle(context)

                    if result and result.status == EngineStatus.COMPLETED:
                        success = True
                    else:
                        attempts += 1
                except Exception as ex:
                    attempts += 1
                    err_msg = f"Engine '{engine.engine_id}' raised unhandled exception: {str(ex)}"
                    logger.exception(err_msg)
                    errors.append(err_msg)

            stats.record_engine_completion(success=success, retried=was_retried)

            if result:
                engine_results.append(result)
                if result.errors:
                    errors.extend(result.errors)

            if not success:
                msg = f"Engine '{engine.engine_id}' failed execution."
                logger.error(msg)
                if fail_fast:
                    logger.error(f"Fail-fast policy triggered on pipeline '{self.pipeline_id}'. Aborting.")
                    self._set_status(PipelineStatus.FAILED)
                    stats.stop()
                    return PipelineResult(
                        pipeline_id=self.pipeline_id,
                        plan_id=plan_id,
                        status=PipelineStatus.FAILED,
                        engine_results=engine_results,
                        artifacts=self.artifacts,
                        events=self.events,
                        statistics=stats,
                        errors=errors,
                    )

        stats.stop()

        final_status = PipelineStatus.COMPLETED if stats.failed_engines == 0 else PipelineStatus.FAILED
        self._set_status(final_status)

        self.event_publisher("PipelineFinished", {
            "pipeline_id": self.pipeline_id,
            "plan_id": plan_id,
            "status": final_status.value,
            "duration_ms": stats.duration_ms,
        })

        return PipelineResult(
            pipeline_id=self.pipeline_id,
            plan_id=plan_id,
            status=final_status,
            engine_results=engine_results,
            artifacts=self.artifacts,
            events=self.events,
            statistics=stats,
            errors=errors,
        )


__all__ = ["PipelineManager"]
