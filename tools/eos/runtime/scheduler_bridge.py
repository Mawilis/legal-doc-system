"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Worker Event Bridge & Artifact Event Publisher (FG171C).
    Subscribes to `TASK_STARTED` events, dispatches task payloads through the
    central `EngineWorkerRegistry` (FG171B), and emits `TASK_COMPLETED` /
    `ARTIFACT_PUBLISHED` events onto the `RuntimeEventBus`.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready bridge layer. Zero child's place.
    Ephesians 4:16 - "From whom the whole body fitly joined together and compacted..."
    Proverbs 16:3 - "Commit thy works unto the Lord, and thy thoughts shall be established."

Collaboration & Maintenance:
    - [Architecture]: Event-driven orchestration bridge linking Scheduler events to Workers.
    - [Automation]: Automatic artifact publication upon task execution completion.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from .scheduler_events import (
    ArtifactPublishedEventDTO,
    RuntimeEventBus,
    RuntimeEventTypeEnum,
    TaskCompletedEventDTO,
    TaskStartedEventDTO,
)
from .worker_registry import EngineWorkerRegistry
from .worker_result import WorkerExecutionStatusEnum

logger = logging.getLogger("WilsyOS.Runtime.SchedulerBridge")


class WorkerEventBridge:
    """
    Event bridge wiring the EventDrivenScheduler to EngineWorker instances via EngineWorkerRegistry.
    Listens for TASK_STARTED, dispatches via registry, and publishes completion / artifact events.
    """

    # [FUNCTION EXPLANATION]: Initializes WorkerEventBridge and registers subscribers on the event bus.
    def __init__(self, event_bus: RuntimeEventBus, worker_registry: EngineWorkerRegistry) -> None:
        self.event_bus = event_bus
        self.worker_registry = worker_registry
        self._register_subscribers()
        logger.info("WorkerEventBridge successfully initialized and subscribed to EventBus.")

    # [FUNCTION EXPLANATION]: Registers handler for TASK_STARTED topics on the shared event bus.
    def _register_subscribers(self) -> None:
        """Registers listener callbacks on the shared event bus."""
        self.event_bus.subscribe(RuntimeEventTypeEnum.TASK_STARTED, self._handle_task_started)

    # [FUNCTION EXPLANATION]: Intercepts TASK_STARTED event, dispatches task via EngineWorkerRegistry, and emits completion/artifact events.
    async def _handle_task_started(self, event: Any) -> None:
        """
        Intercepts TASK_STARTED event, dispatches execution to registered worker,
        emits TASK_COMPLETED event, and triggers ARTIFACT_PUBLISHED if output contains artifact data.
        """
        if not isinstance(event, TaskStartedEventDTO):
            logger.warning(f"WorkerEventBridge received unexpected event payload type: {type(event)}")
            return

        logger.info(
            f"Bridge handling TASK_STARTED event [{event.event_id}] for Task [{event.task_id}] "
            f"on Engine [{event.engine_name}]"
        )

        # 1. Dispatch task to worker via central EngineWorkerRegistry (FG171B Guarantee)
        worker_result = await self.worker_registry.dispatch_task(
            engine_name=event.engine_name,
            task_id=event.task_id,
            payload=event.payload,
        )

        # 2. Construct and publish TaskCompleted event with duration telemetry
        completed_event = TaskCompletedEventDTO(
            event_id=f"evt-comp-{uuid.uuid4().hex[:8]}",
            session_id=event.session_id,
            tenant_id=event.tenant_id,
            task_id=event.task_id,
            engine_name=event.engine_name,
            status=worker_result.status.value,
            execution_duration_ms=worker_result.execution_duration_ms,
            output=worker_result.output,
            error_details=worker_result.error_details,
        )

        event_topic = (
            RuntimeEventTypeEnum.TASK_COMPLETED
            if worker_result.status == WorkerExecutionStatusEnum.SUCCESS
            else RuntimeEventTypeEnum.TASK_FAILED
        )

        await self.event_bus.publish(event_topic, completed_event)

        # 3. Check for artifact creation and publish ARTIFACT_PUBLISHED if present
        if worker_result.status == WorkerExecutionStatusEnum.SUCCESS:
            output_data = worker_result.output
            if "artifact_id" in output_data or "artifact_type" in output_data or output_data.get("artifact") is True:
                artifact_id = str(output_data.get("artifact_id", f"art-{uuid.uuid4().hex[:8]}"))
                artifact_type = str(output_data.get("artifact_type", f"{event.engine_name}_result"))

                artifact_event = ArtifactPublishedEventDTO(
                    artifact_id=artifact_id,
                    session_id=event.session_id,
                    tenant_id=event.tenant_id,
                    source_task_id=event.task_id,
                    artifact_type=artifact_type,
                    metadata=output_data,
                )

                logger.info(
                    f"Bridge emitting ARTIFACT_PUBLISHED [{artifact_id}] "
                    f"for Task [{event.task_id}]"
                )
                await self.event_bus.publish(RuntimeEventTypeEnum.ARTIFACT_PUBLISHED, artifact_event)
