"""WILSY OS worker registry direct contract certificate.

TITLE: WILSY Runtime Worker Registry Certificate
VERSION: v1.0.2-WILSY-WORKER-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Directly certifies worker routing and result validation only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_worker_registry.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.2 strengthens valid explicit/inferred registration certification with direct canonical WorkerResultDTO type and exact output assertions while preserving all v1.0.1 coverage; no production behavior or authority boundary changes.
COMPLIANCE: Deterministic in-memory unit certificate; POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No external systems, payload persistence, or authority inference.
TENANT BOUNDARY: engine_name is routing configuration and task_id is execution correlation, neither authorization proof.
AUTHORITY BOUNDARY: Worker routing/result behavior only; no tenant authentication, authorization, or KEXEC authority.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
"""

import asyncio
from typing import Any

import pytest

from tools.eos.runtime.worker_registry import (
    DuplicateWorkerRegistrationError,
    EngineWorkerRegistry,
    WorkerRegistrationError,
)
from tools.eos.runtime.worker_result import WorkerExecutionStatusEnum, WorkerResultDTO


class AsyncWorker:
    def __init__(self, result: Any = None, *, engine_name: Any = None, error: Exception | None = None) -> None:
        self.result = result
        self.engine_name = engine_name
        self.error = error
        self.received_payload: dict[str, Any] | None = None

    async def execute(self, task_id: str, payload: dict[str, Any]) -> Any:
        self.received_payload = payload
        if self.error:
            raise self.error
        return self.result


def result(task_id: str, status: WorkerExecutionStatusEnum = WorkerExecutionStatusEnum.SUCCESS, output: dict[str, Any] | None = None, error: str | None = None, duration: float = 7.5) -> WorkerResultDTO:
    return WorkerResultDTO(task_id=task_id, status=status, execution_duration_ms=duration, output=output or {}, error_details=error)


def dispatch(registry: EngineWorkerRegistry, engine: str, task_id: str, payload: dict[str, Any] | None = None) -> WorkerResultDTO:
    return asyncio.run(registry.dispatch_task(engine, task_id, payload or {}))


@pytest.mark.parametrize("name", ["", "   "])
def test_blank_explicit_engine_names_rejected(name: str) -> None:
    registry = EngineWorkerRegistry()
    with pytest.raises(WorkerRegistrationError, match="ENGINE_NAME_REQUIRED"):
        registry.register_worker(name, AsyncWorker(result("t")))


def test_non_string_explicit_engine_name_is_rejected_before_registration() -> None:
    registry = EngineWorkerRegistry()
    with pytest.raises(WorkerRegistrationError, match="ENGINE_NAME_REQUIRED"):
        registry.register_worker(7, AsyncWorker(result("t")))
    assert dispatch(registry, "7", "t").status is WorkerExecutionStatusEnum.FAILED


def test_registration_forms_and_name_normalization() -> None:
    registry = EngineWorkerRegistry()
    explicit = AsyncWorker(result("t", output={"source": "explicit-worker"}))
    inferred = AsyncWorker(result("t", output={"source": "inferred-worker"}), engine_name="  engine-d  ")
    registry.register_worker("  engine-c  ", explicit)
    registry.register_worker(inferred)
    explicit_result = dispatch(registry, "engine-c", "t")
    assert isinstance(explicit_result, WorkerResultDTO)
    assert explicit_result.status is WorkerExecutionStatusEnum.SUCCESS
    assert explicit_result.task_id == "t"
    assert explicit_result.output == {"source": "explicit-worker"}
    inferred_result = dispatch(registry, "engine-d", "t")
    assert isinstance(inferred_result, WorkerResultDTO)
    assert inferred_result.status is WorkerExecutionStatusEnum.SUCCESS
    assert inferred_result.task_id == "t"
    assert inferred_result.output == {"source": "inferred-worker"}


@pytest.mark.parametrize(
    "worker",
    [
        pytest.param(AsyncWorker(result("t")), id="missing-engine-name"),
        pytest.param(AsyncWorker(result("t"), engine_name=""), id="blank-engine-name"),
        pytest.param(AsyncWorker(result("t"), engine_name="   "), id="whitespace-engine-name"),
        pytest.param(AsyncWorker(result("t"), engine_name=7), id="non-string-engine-name"),
        pytest.param(object(), id="invalid-object"),
    ],
)
def test_invalid_workers_and_inferred_names_rejected(worker: Any) -> None:
    registry = EngineWorkerRegistry()
    if isinstance(worker, AsyncWorker) and worker.engine_name is None:
        with pytest.raises(WorkerRegistrationError):
            registry.register_worker(worker)
    else:
        with pytest.raises(WorkerRegistrationError):
            registry.register_worker(worker)
    assert dispatch(registry, "engine-c", "t").status is WorkerExecutionStatusEnum.FAILED


def test_raw_callables_sync_execute_and_process_only_rejected() -> None:
    async def raw_async(task_id: str, payload: dict[str, Any]) -> Any:
        return result(task_id)
    def raw_sync(task_id: str, payload: dict[str, Any]) -> Any:
        return result(task_id)
    class Sync:
        def execute(self, task_id: str, payload: dict[str, Any]) -> Any: return result(task_id)
    class ProcessOnly:
        async def process_task(self, task_id: str, payload: dict[str, Any]) -> Any: return {}
    class NonCallable:
        execute = "invalid"
    workers: tuple[Any, ...] = (raw_async, raw_sync, Sync(), ProcessOnly(), NonCallable())
    for worker in workers:
        with pytest.raises(WorkerRegistrationError):
            EngineWorkerRegistry().register_worker("engine", worker)


def test_duplicate_registration_rejected_before_overwrite() -> None:
    registry = EngineWorkerRegistry()
    first = AsyncWorker(result("t", output={"worker": "first"}))
    registry.register_worker("engine", first)
    with pytest.raises(DuplicateWorkerRegistrationError, match="DUPLICATE_ENGINE_NAME"):
        registry.register_worker("  engine  ", AsyncWorker(result("t", output={"worker": "second"})))
    assert dispatch(registry, "engine", "t").output == {"worker": "first"}


def test_unknown_engine_is_failed_result() -> None:
    value = dispatch(EngineWorkerRegistry(), "missing-engine", "task-missing-001")
    assert isinstance(value, WorkerResultDTO)
    assert value.status is WorkerExecutionStatusEnum.FAILED
    assert value.task_id == "task-missing-001"
    assert value.output == {}
    assert "No worker registered" in (value.error_details or "")


def test_worker_exception_is_failed_without_payload_leakage() -> None:
    registry = EngineWorkerRegistry(); registry.register_worker("engine", AsyncWorker(error=RuntimeError("boom")))
    value = dispatch(registry, "engine", "task-exception-001", {"secret": "payload"})
    assert value.status is WorkerExecutionStatusEnum.FAILED
    assert value.task_id == "task-exception-001"; assert value.output == {}
    assert value.error_details == "boom"
    assert "payload" not in value.error_details


@pytest.mark.parametrize("invalid", [{"x": 1}, 4, None])
def test_non_dto_results_fail_closed(invalid: Any) -> None:
    registry = EngineWorkerRegistry(); registry.register_worker("engine", AsyncWorker(invalid))
    value = dispatch(registry, "engine", "task-invalid")
    assert value.status is WorkerExecutionStatusEnum.FAILED
    assert value.task_id == "task-invalid"; assert value.output == {}
    assert value.error_details == "INVALID_WORKER_RESULT_TYPE"


def test_mismatched_result_identity_fails_closed() -> None:
    registry = EngineWorkerRegistry(); registry.register_worker("engine", AsyncWorker(result("other-task", output={"success": True})))
    value = dispatch(registry, "engine", "task-dispatched")
    assert value.status is WorkerExecutionStatusEnum.FAILED
    assert value.task_id == "task-dispatched"; assert value.output == {}
    assert value.error_details == "WORKER_RESULT_TASK_ID_MISMATCH"


@pytest.mark.parametrize("status,error", [(WorkerExecutionStatusEnum.SUCCESS, None), (WorkerExecutionStatusEnum.FAILED, "failed"), (WorkerExecutionStatusEnum.CANCELLED, "cancelled")])
def test_matching_terminal_dto_preserved(status: WorkerExecutionStatusEnum, error: str | None) -> None:
    original = result("task-valid", status, {"evidence": status.value}, error, 12.25)
    registry = EngineWorkerRegistry(); registry.register_worker("engine", AsyncWorker(original))
    value = dispatch(registry, "engine", "task-valid")
    assert value is original
    assert (value.task_id, value.status, value.output, value.error_details, value.execution_duration_ms) == ("task-valid", status, {"evidence": status.value}, error, 12.25)


def test_registry_passes_original_payload_without_copy_layer() -> None:
    worker = AsyncWorker(result("task-payload")); registry = EngineWorkerRegistry(); registry.register_worker("engine", worker)
    payload = {"nested": {"value": 1}}
    dispatch(registry, "engine", "task-payload", payload)
    assert worker.received_payload is payload


# ARTIFACT: test_worker_registry.py
# VERSION: v1.0.2-WILSY-WORKER-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct worker routing/result behavior only.
# TENANT POSTURE: engine_name/task_id are not authorization proof.
# FAIL-CLOSED POSTURE: invalid configuration and result evidence are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
