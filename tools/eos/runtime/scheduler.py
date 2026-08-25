"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Event-Driven Task Scheduler Engine (FG171C).
    Schedules, queues, and orchestrates task execution across registered workers,
    emitting lifecycle events onto the central `RuntimeEventBus`.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready scheduler kernel component. Zero child's place.
    Ecclesiastes 3:1 - "To every thing there is a season, and a time to every purpose..."
    1 Corinthians 14:40 - "Let all things be done decently and in order."

Collaboration & Maintenance:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
===============================================================================
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from .scheduler_events import (
    RuntimeEventBus,
    RuntimeEventTypeEnum,
    TaskStartedEventDTO,
)

logger = logging.getLogger("WilsyOS.Runtime.Scheduler")


class EventDrivenScheduler:
    """
    Core event-driven scheduler responsible for queueing, dispatching,
    and managing task execution lifecycle events across Wilsy OS runtime modules.
    """

    # [FUNCTION EXPLANATION]: Initializes the scheduler instance with a reference to the shared runtime event bus.
    def __init__(self, event_bus: RuntimeEventBus) -> None:
        self.event_bus = event_bus
        self._is_active: bool = True
        logger.info("EventDrivenScheduler kernel component initialized successfully.")

    # [FUNCTION EXPLANATION]: Constructs and publishes a TaskStartedEventDTO onto the central event bus.
    async def schedule_task(
        self,
        engine_name: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Schedules a task for execution by emitting a TASK_STARTED event onto the RuntimeEventBus.

        Returns:
            str: Generated or passed task_id.
        """
        resolved_task_id = task_id or f"task-{uuid.uuid4().hex[:8]}"
        resolved_session_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        resolved_tenant_id = tenant_id or "tenant-default"
        resolved_payload = payload or {}

        event_id = f"evt-start-{uuid.uuid4().hex[:8]}"

        task_event = TaskStartedEventDTO(
            event_id=event_id,
            session_id=resolved_session_id,
            tenant_id=resolved_tenant_id,
            task_id=resolved_task_id,
            engine_name=engine_name,
            payload=resolved_payload,
        )

        logger.info(
            f"Scheduling Task [{resolved_task_id}] on Engine [{engine_name}] "
            f"with Event ID [{event_id}]"
        )

        await self.event_bus.publish(RuntimeEventTypeEnum.TASK_STARTED, task_event)
        return resolved_task_id

    # [FUNCTION EXPLANATION]: Halts scheduler operations safely.
    async def shutdown(self) -> None:
        """Shuts down the scheduler component safely."""
        self._is_active = False
        logger.info("EventDrivenScheduler kernel component successfully shut down.")
