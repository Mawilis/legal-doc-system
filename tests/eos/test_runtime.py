"""WILSY OS — canonical runtime integration certificate.

TITLE: FG171C Runtime Scheduler Integration Certificate
VERSION: v1.0.1-WILSY-RUNTIME-INTEGRATION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies one explicit-tenant scheduler-to-worker success and artifact path.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/eos/test_runtime.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.1 closes the async-subscriber certification gap by replacing synchronous callbacks passed to subscribe_async with explicit awaited coroutine collectors; v1.0.0 migrated stale FG171C/FG172A expectations.
COMPLIANCE: Explicit tenant scope; no persistence, authentication, authorization, KEXEC, or financial execution authority.
SECURITY / PRIVACY POSTURE: Local deterministic worker only; no credentials, network, filesystem, database, or external service.
TENANT BOUNDARY: tenant_id is explicit scheduling scope evidence, not authentication or authorization proof.
AUTHORITY BOUNDARY: Scheduler-to-worker event integration only; upstream identity and tenant authorization remain external.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive financial execution authority.
"""
from __future__ import annotations
import asyncio
from typing import Any
import pytest
from tools.eos.runtime import EventDrivenScheduler, RuntimeEventBus, WorkerEventBridge
from tools.eos.runtime.scheduler_events import ArtifactPublishedEventDTO, RuntimeEventTypeEnum, TaskCompletedEventDTO, TaskStartedEventDTO
from tools.eos.runtime.worker_registry import EngineWorkerRegistry
from tools.eos.runtime.worker_result import WorkerExecutionStatusEnum, WorkerResultDTO

class MockDocumentEngineWorker:
    async def execute(self, task_id: str, payload: dict[str, Any]) -> WorkerResultDTO:
        return WorkerResultDTO(task_id=task_id, status=WorkerExecutionStatusEnum.SUCCESS, execution_duration_ms=15.0, output={"status": "completed", "artifact_id": f"art-{task_id}", "artifact_type": "contract_pdf", "artifact": True})

def test_event_driven_scheduler_lifecycle() -> None:
    asyncio.run(_test_event_driven_scheduler_lifecycle())


async def _test_event_driven_scheduler_lifecycle() -> None:
    event_bus = RuntimeEventBus(); worker_registry = EngineWorkerRegistry()
    worker_registry.register_worker("doc_engine", MockDocumentEngineWorker())
    scheduler = EventDrivenScheduler(event_bus=event_bus)
    WorkerEventBridge(event_bus=event_bus, worker_registry=worker_registry)
    started: list[TaskStartedEventDTO] = []; completed: list[TaskCompletedEventDTO] = []; artifacts: list[ArtifactPublishedEventDTO] = []
    async def capture_started(event: TaskStartedEventDTO) -> None: started.append(event)
    async def capture_completed(event: TaskCompletedEventDTO) -> None: completed.append(event)
    async def capture_artifact(event: ArtifactPublishedEventDTO) -> None: artifacts.append(event)
    event_bus.subscribe_async(RuntimeEventTypeEnum.TASK_STARTED.value, capture_started)
    event_bus.subscribe_async(RuntimeEventTypeEnum.TASK_COMPLETED.value, capture_completed)
    event_bus.subscribe_async(RuntimeEventTypeEnum.ARTIFACT_PUBLISHED.value, capture_artifact)
    expected = {"status": "completed", "artifact_id": "art-task-compliance-001", "artifact_type": "contract_pdf", "artifact": True}
    task_id = await scheduler.schedule_task(engine_name="doc_engine", session_id="sess-test-100", tenant_id="tenant-wilsy", task_id="task-compliance-001", payload={"document": "commercial_agreement.pdf"})
    assert task_id == "task-compliance-001" and len(started) == len(completed) == len(artifacts) == 1
    start, finish, artifact = started[0], completed[0], artifacts[0]
    assert start.execution_id == start.task_id == task_id and start.session_id == "sess-test-100" and start.tenant_id == "tenant-wilsy" and start.engine_name == "doc_engine" and start.metadata == {"document": "commercial_agreement.pdf"}
    assert finish.execution_id == finish.task_id == task_id and finish.session_id == "sess-test-100" and finish.tenant_id == "tenant-wilsy" and finish.engine_name == "doc_engine" and finish.status == "SUCCESS" and finish.metadata == expected
    assert artifact.source_task_id == task_id and artifact.session_id == "sess-test-100" and artifact.tenant_id == "tenant-wilsy" and artifact.artifact_id == expected["artifact_id"] and artifact.artifact_type == expected["artifact_type"] and artifact.payload == expected
    await scheduler.shutdown()

# ARTIFACT: test_runtime.py
# VERSION: v1.0.1-WILSY-RUNTIME-INTEGRATION-CERT
# AUTHORITY BOUNDARY: scheduler-to-worker integration evidence only.
# TENANT POSTURE: explicit tenant scope; no fallback or substitution.
# FAIL-CLOSED POSTURE: canonical async contracts and explicit tenant are required.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
