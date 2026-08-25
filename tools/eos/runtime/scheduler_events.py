"""
===============================================================================
WILSY OS KERNEL — RUNTIME SCHEDULER EVENTS (PRODUCTION GRADE)
===============================================================================
[EPITOME]:
    Provides immutable runtime event DTOs, event types, task event DTO aliases,
    artifact event aliases, and event bus dispatch structures for tracking
    scheduling and execution events across Wilsy OS.
    Engineered to billion-dollar enterprise production standards with zero tolerance
    for missing symbols or technical debt.

[BIBLICAL FOUNDATION]:
    Ecclesiastes 3:1 — "To everything there is a season, and a time to every purpose under the heaven."

[PRODUCTION MANDATE]:
    - Full alignment with KernelEngine expectations (execution_id, event_type, message, session_id, tenant_id, etc.)
    - Zero‑loss event publishing with async/await support.
    - Immutable DTOs with complete field coverage.
    - Enum includes all event types: TASK_STARTED, TASK_COMPLETED, ARTIFACT_PUBLISHED, etc.

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Scheduler Events
===============================================================================
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("WilsyOS.RuntimeEventBus")


class RuntimeEventTypeEnum(str, Enum):
    """All runtime event types recognised by the Wilsy OS Kernel."""
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    ARTIFACT_PUBLISHED = "ARTIFACT_PUBLISHED"
    DISPATCHED = "DISPATCHED"
    RETRY = "RETRY"


# Backward compatibility alias
SchedulerEventTypeEnum = RuntimeEventTypeEnum


class TaskStartedEvent(BaseModel):
    """Task Started Event – published when an engine task begins."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(description="Unique execution identifier.")
    event_type: str = Field(default="TASK_STARTED")
    message: str = Field(description="Descriptive message.")
    session_id: Optional[str] = Field(default=None)
    tenant_id: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)
    engine_name: Optional[str] = Field(default=None)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskCompletedEvent(BaseModel):
    """Task Completed Event – published when a task finishes successfully."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(description="Unique execution identifier.")
    event_type: str = Field(default="TASK_COMPLETED")
    message: str = Field(description="Descriptive message.")
    session_id: Optional[str] = Field(default=None)
    tenant_id: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)
    engine_name: Optional[str] = Field(default=None)
    status: str = Field(default="SUCCESS")
    execution_duration_ms: float = Field(default=0.0)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskFailedEvent(BaseModel):
    """Task Failed Event – published when a task fails."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(description="Unique execution identifier.")
    event_type: str = Field(default="TASK_FAILED")
    message: str = Field(description="Error message.")
    session_id: Optional[str] = Field(default=None)
    tenant_id: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)
    engine_name: Optional[str] = Field(default=None)
    error_details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ArtifactPublishedEvent(BaseModel):
    """Artifact Published Event – produced when a pipeline artifact is created."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    artifact_id: str = Field(description="Unique artifact identifier.")
    event_type: str = Field(default="ARTIFACT_PUBLISHED")
    message: str = Field(default="Artifact published")
    session_id: Optional[str] = Field(default=None)
    tenant_id: Optional[str] = Field(default=None)
    source_task_id: Optional[str] = Field(default=None)
    artifact_type: Optional[str] = Field(default=None)
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SchedulerEvent(BaseModel):
    """Generic Scheduler Event (legacy compatibility)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str = Field(description="Unique event identifier.")
    execution_id: str = Field(description="Associated execution identifier.")
    event_type: RuntimeEventTypeEnum = Field(description="Type of scheduler event.")
    message: str = Field(description="Descriptive event message.")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Type aliases for backward compatibility
SchedulerEventDTO = SchedulerEvent
TaskStartedEventDTO = TaskStartedEvent
TaskCompletedEventDTO = TaskCompletedEvent
TaskFailedEventDTO = TaskFailedEvent
ArtifactPublishedEventDTO = ArtifactPublishedEvent


class RuntimeEventBus:
    """
    Runtime Event Bus – dispatches and records scheduler events.
    Supports both synchronous and asynchronous publishing.
    """

    def __init__(self) -> None:
        self._events: List[SchedulerEvent] = []
        self._subscribers: Dict[str, List[Callable]] = {}
        self._async_subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register a synchronous subscriber."""
        self._subscribers.setdefault(event_type, []).append(handler)

    def subscribe_async(self, event_type: str, handler: Callable) -> None:
        """Register an asynchronous subscriber."""
        self._async_subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, event: Any) -> None:
        """
        Synchronously publish an event to all registered sync subscribers.
        Also stores the event in the history.
        """
        # Store raw event for audit
        if isinstance(event, (TaskStartedEvent, TaskCompletedEvent, ArtifactPublishedEvent, SchedulerEvent)):
            stored = SchedulerEvent(
                event_id=getattr(event, 'execution_id', str(uuid.uuid4())),
                execution_id=getattr(event, 'execution_id', ''),
                event_type=RuntimeEventTypeEnum(event_type),
                message=getattr(event, 'message', ''),
                metadata=getattr(event, 'metadata', {})
            )
            self._events.append(stored)

        # Dispatch to synchronous subscribers
        for handler in self._subscribers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    # Should not happen for sync subscribers, but handle gracefully
                    asyncio.create_task(handler(event))
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Sync subscriber error for {event_type}: {e}", exc_info=True)

    async def publish_async(self, event_type: str, event: Any) -> None:
        """
        Asynchronously publish an event to all registered async subscribers.
        Also stores the event synchronously.
        """
        # Store event synchronously
        self.publish(event_type, event)

        # Dispatch to async subscribers
        for handler in self._async_subscribers.get(event_type, []):
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Async subscriber error for {event_type}: {e}", exc_info=True)

    def get_events(self) -> List[SchedulerEvent]:
        """Retrieve all published events for forensic audit."""
        return list(self._events)

    def clear_events(self) -> None:
        """Clear event history – useful for test isolation."""
        self._events.clear()

    def event_count(self) -> int:
        """Return the number of events published."""
        return len(self._events)
