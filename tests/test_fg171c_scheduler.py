"""WILSY OS — FG171C scheduler contract certificate.

TITLE: Canonical Event-Driven Scheduler Contract Tests
VERSION: v1.0.4-FG171C-SCHEDULER-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies explicit tenant-scoped scheduling and deterministic async worker bridging.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/test_fg171c_scheduler.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.4 closes the artifact-evidence gap by certifying complete ArtifactPublishedEventDTO.payload against deterministic worker output including type and nested evidence; v1.0.3 closed identity and failure gaps.
COMPLIANCE: Explicit tenant scope; no persistence, authentication, authorization, or financial execution authority.
SECURITY / PRIVACY POSTURE: Local fakes only; payloads are isolated and credentials are absent.
TENANT BOUNDARY: tenant_id is explicit scope; no default, membership, or cross-tenant authority is created.
AUTHORITY BOUNDARY: Scheduling and worker event translation only; identity and authorization remain external.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive financial execution authority.
"""
from __future__ import annotations
import asyncio
from typing import Any
import pytest
from tools.eos.runtime import EventDrivenScheduler, RuntimeEventBus, WorkerEventBridge
from tools.eos.runtime.scheduler import SchedulerAuthorityError, SchedulerLifecycleError
from tools.eos.runtime.scheduler_events import ArtifactPublishedEventDTO, RuntimeEventTypeEnum, TaskCompletedEventDTO, TaskFailedEventDTO, TaskStartedEventDTO
from tools.eos.runtime.worker_registry import EngineWorkerRegistry
from tools.eos.runtime.worker_result import WorkerExecutionStatusEnum, WorkerResultDTO

class SuccessWorker:
    async def execute(self, task_id: str, payload: dict[str, Any]) -> WorkerResultDTO:
        payload["worker_mutation"] = True
        return WorkerResultDTO(task_id=task_id, status=WorkerExecutionStatusEnum.SUCCESS, execution_duration_ms=1.0, output={"artifact_id": "artifact-1", "artifact_type": "report", "nested": {"value": 7}})

class FailureWorker:
    async def execute(self, task_id: str, payload: dict[str, Any]) -> WorkerResultDTO:
        return WorkerResultDTO(task_id=task_id, status=WorkerExecutionStatusEnum.FAILED, execution_duration_ms=1.0, output={}, error_details="worker failed")

def _components(worker: Any | None = None) -> tuple[RuntimeEventBus, EventDrivenScheduler]:
    bus = RuntimeEventBus(); registry = EngineWorkerRegistry()
    if worker is not None: registry.register_worker("engine", worker)
    WorkerEventBridge(event_bus=bus, worker_registry=registry)
    return bus, EventDrivenScheduler(event_bus=bus)

def _run(coro: Any) -> Any: return asyncio.run(coro)

def test_public_exports_are_canonical() -> None:
    from tools.eos.runtime.scheduler import EventDrivenScheduler as S
    from tools.eos.runtime.scheduler_bridge import WorkerEventBridge as B
    from tools.eos.runtime.scheduler_events import RuntimeEventBus as R
    assert EventDrivenScheduler is S and WorkerEventBridge is B and RuntimeEventBus is R

@pytest.mark.parametrize("tenant_id", [None, "", "   ", "unknown", "none", "null", "tenant-default", " UNKNOWN ", " NONE ", " NULL ", " TENANT-DEFAULT "])
def test_invalid_tenant_references_fail_closed(tenant_id: str | None) -> None:
    bus, scheduler = _components()
    before = bus.event_count()
    with pytest.raises(SchedulerAuthorityError): _run(scheduler.schedule_task("engine", tenant_id=tenant_id))
    assert bus.event_count() == before

def test_schedule_awaits_bridge_and_isolates_payload() -> None:
    bus, scheduler = _components(SuccessWorker()); captured: list[Any] = []
    for kind in (RuntimeEventTypeEnum.TASK_STARTED, RuntimeEventTypeEnum.TASK_COMPLETED, RuntimeEventTypeEnum.ARTIFACT_PUBLISHED): bus.subscribe(kind.value, captured.append)
    expected_output = {"artifact_id": "artifact-1", "artifact_type": "report", "nested": {"value": 7}}
    payload = {"nested": {"value": 1}}
    assert _run(scheduler.schedule_task("engine", task_id="task-1", session_id="session-1", tenant_id="tenant-a", payload=payload)) == "task-1"
    payload["nested"]["value"] = 99
    assert isinstance(captured[0], TaskStartedEventDTO) and captured[0].execution_id == captured[0].task_id == "task-1"
    assert captured[0].engine_name == "engine" and captured[0].tenant_id == "tenant-a" and captured[0].metadata["nested"]["value"] == 1
    assert isinstance(captured[1], TaskCompletedEventDTO) and isinstance(captured[2], ArtifactPublishedEventDTO)
    assert captured[1].execution_id == captured[1].task_id == "task-1" and captured[1].tenant_id == "tenant-a" and captured[1].engine_name == "engine" and captured[1].session_id == "session-1" and captured[1].status == "SUCCESS"
    assert captured[1].metadata == expected_output
    assert captured[2].payload == expected_output and bus.event_count() == 3
    assert captured[2].source_task_id == "task-1" and captured[2].tenant_id == "tenant-a" and captured[2].session_id == "session-1" and captured[2].artifact_id == "artifact-1" and captured[2].artifact_type == "report"
    assert captured[1].metadata["nested"] == captured[2].payload["nested"]
    captured[1].metadata["nested"]["value"] = 42
    assert captured[2].payload["nested"]["value"] == 7

def test_worker_failure_and_missing_worker_emit_failed_dto() -> None:
    for worker, marker in ((FailureWorker(), "worker failed"), (None, "No worker registered")):
        bus, scheduler = _components(worker); failed: list[Any] = []; completed: list[Any] = []; artifacts: list[Any] = []
        bus.subscribe(RuntimeEventTypeEnum.TASK_FAILED.value, failed.append)
        bus.subscribe(RuntimeEventTypeEnum.TASK_COMPLETED.value, completed.append)
        bus.subscribe(RuntimeEventTypeEnum.ARTIFACT_PUBLISHED.value, artifacts.append)
        _run(scheduler.schedule_task("engine", task_id="task-f", tenant_id="tenant-a", payload={}))
        assert len(failed) == 1 and isinstance(failed[0], TaskFailedEventDTO)
        assert failed[0].execution_id == failed[0].task_id == "task-f"
        assert failed[0].tenant_id == "tenant-a" and failed[0].engine_name == "engine"
        assert failed[0].error_details["status"] == "FAILED"
        assert isinstance(failed[0].error_details["error"], str) and failed[0].error_details["error"] and marker in failed[0].error_details["error"]
        if worker is None: assert "engine" in failed[0].error_details["error"]
        assert not completed and not artifacts

def test_worker_mutation_does_not_mutate_started_metadata() -> None:
    bus, scheduler = _components(SuccessWorker()); started: list[Any] = []
    bus.subscribe(RuntimeEventTypeEnum.TASK_STARTED.value, started.append)
    _run(scheduler.schedule_task("engine", task_id="task-m", tenant_id="tenant-a", payload={"original": True}))
    assert "worker_mutation" not in started[0].metadata

def test_execution_task_mismatch_fails_closed_before_worker_dispatch() -> None:
    class SpyWorker:
        calls = 0
        async def execute(self, task_id: str, payload: dict[str, Any]) -> WorkerResultDTO:
            self.calls += 1
            return WorkerResultDTO(task_id=task_id, execution_duration_ms=1.0)

    bus = RuntimeEventBus(); registry = EngineWorkerRegistry(); worker = SpyWorker()
    registry.register_worker("engine", worker)
    WorkerEventBridge(event_bus=bus, worker_registry=registry)
    event = TaskStartedEventDTO(execution_id="exec-a", task_id="task-b", engine_name="engine", tenant_id="tenant-a", message="start", metadata={})
    completed: list[Any] = []; failed: list[Any] = []; artifacts: list[Any] = []
    bus.subscribe(RuntimeEventTypeEnum.TASK_COMPLETED.value, completed.append)
    bus.subscribe(RuntimeEventTypeEnum.TASK_FAILED.value, failed.append)
    bus.subscribe(RuntimeEventTypeEnum.ARTIFACT_PUBLISHED.value, artifacts.append)
    _run(bus.publish_async(RuntimeEventTypeEnum.TASK_STARTED, event))
    assert worker.calls == 0
    assert not completed and not failed and not artifacts

def test_shutdown_rejects_later_scheduling() -> None:
    bus, scheduler = _components(); before = bus.event_count(); _run(scheduler.shutdown()); _run(scheduler.shutdown())
    with pytest.raises(SchedulerLifecycleError): _run(scheduler.schedule_task("engine", tenant_id="tenant-a"))
    assert bus.event_count() == before

def test_no_synthetic_authority_defaults() -> None:
    _, scheduler = _components(); assert not hasattr(scheduler, "tenant_id")
    with pytest.raises(SchedulerAuthorityError): _run(scheduler.schedule_task("engine"))

# ARTIFACT: test_fg171c_scheduler.py
# VERSION: v1.0.4-FG171C-SCHEDULER-CERT
# AUTHORITY BOUNDARY: scheduler contract evidence only; no authentication, authorization, or execution authority.
# TENANT POSTURE: explicit tenant scope; no fallback or cross-tenant substitution.
# FAIL-CLOSED POSTURE: invalid tenant, malformed identity, missing worker, and shutdown paths are denied.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
