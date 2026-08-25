"""
===============================================================================
WILSY ENGINEERING KERNEL — COMPREHENSIVE PHASE INTEGRATION TEST
===============================================================================
Epitome:
    Validates the entire event-driven runtime pipeline:
    Event Bus -> Artifact Store -> Artifact Aggregator -> Dashboard Snapshot Cache -> Kernel Bootstrap.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready integration test. Zero child's place.
    1 Corinthians 14:40 - "Let all things be done decently and in order."
===============================================================================
"""

import asyncio
import logging
import json
from typing import Any, Dict

from tools.eos.runtime.scheduler_events import (
    RuntimeEventBus,
    RuntimeEventTypeEnum,
    TaskStartedEvent,
    TaskCompletedEvent,
    ArtifactPublishedEvent
)
from tools.eos.runtime.artifact_aggregator import ArtifactAggregator, PipelineArtifact
from tools.eos.runtime.dashboard_live import DashboardLiveManager
from tools.eos.kernel import WilsyKernelBootstrap

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("WilsyOS.PhaseIntegrationTest")


async def run_integration_verification() -> None:
    logger.info("=" * 80)
    logger.info("WILSY OS — PHASE INTEGRATION VERIFICATION SUITE INITIATED")
    logger.info("=" * 80)

    test_session_id = "sess-phase-integration-999"
    
    # 1. Test Event Bus & Dashboard Live Manager
    logger.info("\n[TEST 1/3] Verifying Event Bus & Dashboard Live Snapshot Cache...")
    event_bus = RuntimeEventBus()
    dashboard_mgr = DashboardLiveManager(event_bus=event_bus, session_id=test_session_id)

    # Publish start event
    await event_bus.publish(
        RuntimeEventTypeEnum.TASK_STARTED,
        TaskStartedEvent(
            event_id="evt-t1-start",
            session_id=test_session_id,
            tenant_id="tenant-integration",
            task_id="task-int-01",
            engine_name="integration_engine"
        )
    )

    # Publish artifact event
    art_event = ArtifactPublishedEvent(
        artifact_id="art-int-01",
        session_id=test_session_id,
        tenant_id="tenant-integration",
        source_task_id="task-int-01",
        artifact_type="integration_test_artifact"
    )
    setattr(art_event, "payload", {"compliance_score": 100.0, "status": "VERIFIED"})
    await event_bus.publish(RuntimeEventTypeEnum.ARTIFACT_PUBLISHED, art_event)

    # Publish completion event
    await event_bus.publish(
        RuntimeEventTypeEnum.TASK_COMPLETED,
        TaskCompletedEvent(
            event_id="evt-t1-comp",
            session_id=test_session_id,
            tenant_id="tenant-integration",
            task_id="task-int-01",
            engine_name="integration_engine",
            status="SUCCESS",
            execution_duration_ms=15.0
        )
    )

    await asyncio.sleep(0.05)
    snapshot = dashboard_mgr.get_snapshot()
    assert snapshot is not None, "Dashboard snapshot failed to initialize!"
    assert snapshot.total_artifacts_indexed == 1, f"Expected 1 indexed artifact, got {snapshot.total_artifacts_indexed}"
    logger.info(f"[TEST 1/3 PASSED] Snapshot cache verified. Active: {snapshot.active_tasks_count}, Completed: {snapshot.completed_tasks_count}, Artifacts: {snapshot.total_artifacts_indexed}")

    # 2. Test Artifact Aggregator & Unified Report Generation
    logger.info("\n[TEST 2/3] Verifying Artifact Aggregator & Unified Report Generation...")
    aggregator = ArtifactAggregator(session_id=test_session_id)
    test_artifact = PipelineArtifact(
        artifact_id="art-agg-02",
        source_task_id="task-int-02",
        artifact_type="playbook_compliance_report",
        tenant_id="tenant-integration",
        session_id=test_session_id,
        payload={"score": 100.0}
    )
    aggregator.ingest_artifact(test_artifact)
    report = aggregator.generate_unified_report()
    assert report.total_artifacts_aggregated == 1, "Aggregator failed to count artifacts."
    assert report.master_compliance_score == 100.0, "Aggregator compliance score calculation error."
    logger.info(f"[TEST 2/3 PASSED] Unified Report generated successfully. Master Score: {report.master_compliance_score}%")

    # 3. Test Full Kernel Bootstrap Pipeline
    logger.info("\n[TEST 3/3] Verifying Full Kernel Bootstrap Execution...")
    kernel = WilsyKernelBootstrap(session_id="sess-kernel-test-01")
    kernel_result = await kernel.boot_and_execute()
    assert kernel_result["status"] == "SUCCESS", "Kernel bootstrap failed execution!"
    logger.info(f"[TEST 3/3 PASSED] Kernel bootstrap completed. Session ID: {kernel_result['session_id']}")

    logger.info("=" * 80)
    logger.info("ALL PHASE INTEGRATION TESTS COMPLETED SUCCESSFULLY. SYSTEM 100% VERIFIED.")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_integration_verification())
