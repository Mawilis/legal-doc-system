"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Runtime Kernel & Event Scheduler Test Suite (FG171C / FG172A).
    Validates end-to-end task scheduling, event routing via WorkerEventBridge,
    worker dispatch, and artifact publication across the RuntimeEventBus.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready test suite. Zero child's place.
    Psalms 119:160 - "Thy word is true from the beginning..."
    Proverbs 24:3-4 - "Through wisdom is an house builded; and by understanding it is established..."

Collaboration & Maintenance:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
===============================================================================
"""

import asyncio
from typing import Any, Dict
import pytest

from tools.eos.runtime import (
    ArtifactPublishedEventDTO,
    EventDrivenScheduler,
    RuntimeEventBus,
    RuntimeEventTypeEnum,
    TaskCompletedEventDTO,
    TaskStartedEventDTO,
    WorkerEventBridge,
)
from tools.eos.runtime.worker_registry import EngineWorkerRegistry
from tools.eos.runtime.worker_result import WorkerExecutionResult, WorkerExecutionStatusEnum


class MockDocumentEngineWorker:
    """Mock Worker Engine for verifying task dispatch and artifact creation."""

    # [FUNCTION EXPLANATION]: Simulates engine execution and returns a structured result payload.
    async def execute(self, task_id: str, payload: Dict[str, Any]) -> WorkerExecutionResult:
        return WorkerExecutionResult(
            status=WorkerExecutionStatusEnum.SUCCESS,
            execution_duration_ms=15.0,
            output={
                "status": "completed",
                "artifact_id": f"art-{task_id}",
                "artifact_type": "contract_pdf",
                "artifact": True,
            },
        )


@pytest.mark.asyncio
async def test_event_driven_scheduler_lifecycle():
    """Validates the complete async flow from schedule_task to event bridge execution and artifact emission."""
    
    # 1. Setup Kernel Components
    event_bus = RuntimeEventBus()
    worker_registry = EngineWorkerRegistry()
    
    # Register mock worker for testing
    worker_registry.register_worker("doc_engine", MockDocumentEngineWorker())

    # Initialize Scheduler and Bridge
    scheduler = EventDrivenScheduler(event_bus=event_bus)
    bridge = WorkerEventBridge(event_bus=event_bus, worker_registry=worker_registry)

    # 2. Capture published events
    published_events = []

    async def event_collector(event: Any) -> None:
        published_events.append(event)

    for event_type in RuntimeEventTypeEnum:
        event_bus.subscribe(event_type, event_collector)

    # 3. Schedule task through EventDrivenScheduler
    task_id = await scheduler.schedule_task(
        engine_name="doc_engine",
        session_id="sess-test-100",
        tenant_id="tenant-wilsy",
        payload={"document": "commercial_agreement.pdf"},
    )

    # Small delay for async event loop dispatch
    await asyncio.sleep(0.05)

    # 4. Assertions
    assert task_id is not None
    assert len(published_events) == 3

    # Check Event Types in Order
    assert isinstance(published_events[0], TaskStartedEventDTO)
    assert isinstance(published_events[1], TaskCompletedEventDTO)
    assert isinstance(published_events[2], ArtifactPublishedEventDTO)

    # Verify DTO Payload Accuracy
    assert published_events[0].task_id == task_id
    assert published_events[0].engine_name == "doc_engine"
    assert published_events[1].status == "SUCCESS"
    assert published_events[2].artifact_id == f"art-{task_id}"

    await scheduler.shutdown()
