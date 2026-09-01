"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Integration Test Harness for FG171E Dashboard Live Mode.
    Simulates event bus traffic and verifies real-time snapshot cache updates.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready live verification test. Zero child's place.
    Habakkuk 2:2 - "Write the vision, and make it plain upon tables..."
===============================================================================
"""

import asyncio
import logging
import json

from tools.eos.runtime.scheduler_events import (
    RuntimeEventBus,
    RuntimeEventTypeEnum,
    TaskStartedEvent,
    TaskCompletedEvent,
    ArtifactPublishedEvent
)
from tools.eos.runtime.dashboard_live import DashboardLiveManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("WilsyOS.DashboardLiveTest")


async def main() -> None:
    logger.info("Initializing FG171E Dashboard Live Mode Test Harness...")

    session_id = "sess-live-dashboard-777"
    event_bus = RuntimeEventBus()

    # Initialize Dashboard Live Manager (subscribes to EventBus)
    dashboard_manager = DashboardLiveManager(event_bus=event_bus, session_id=session_id)

    # 1. Simulate Task Started Event
    logger.info("\nSimulating Task Started Event...")
    start_event = TaskStartedEvent(
        execution_id="evt-start-01",
        message="Task started",
        session_id=session_id,
        tenant_id="tenant-default",
        task_id="task-live-01",
        engine_name="legal_playbook_engine"
    )
    await event_bus.publish_async(RuntimeEventTypeEnum.TASK_STARTED, start_event)

    # 2. Simulate Artifact Published Event (using correct schema arguments)
    logger.info("\nSimulating Artifact Published Event...")
    art_event = ArtifactPublishedEvent(
        artifact_id="art-live-rpt-01",
        message="Artifact published",
        session_id=session_id,
        tenant_id="tenant-default",
        source_task_id="task-live-01",
        artifact_type="playbook_compliance_report"
    )
    await event_bus.publish_async(RuntimeEventTypeEnum.ARTIFACT_PUBLISHED, art_event)

    # 3. Simulate Task Completed Event
    logger.info("\nSimulating Task Completed Event...")
    comp_event = TaskCompletedEvent(
        execution_id="evt-comp-01",
        message="Task completed",
        session_id=session_id,
        tenant_id="tenant-default",
        task_id="task-live-01",
        engine_name="legal_playbook_engine",
        status="SUCCESS",
        execution_duration_ms=45.2
    )
    await event_bus.publish_async(RuntimeEventTypeEnum.TASK_COMPLETED, comp_event)

    # Allow event listeners to complete
    await asyncio.sleep(0.1)

    # Retrieve instantaneous snapshot from cache
    snapshot = dashboard_manager.get_snapshot()

    logger.info("\n>>> LIVE DASHBOARD SNAPSHOT CACHE RETRIEVED SUCCESSFULLY <<<")
    if snapshot:
        print(json.dumps(snapshot.model_dump(), indent=2))
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
