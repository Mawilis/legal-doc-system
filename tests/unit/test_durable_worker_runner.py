import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock

from tools.eos.runtime.durable_worker_runner import DurableWorkerRunner
from tools.eos.runtime.worker_registry import EngineWorkerRegistry
from tools.eos.runtime.worker_result import WorkerResultDTO, WorkerExecutionStatusEnum

NOW = datetime(2026, 11, 8, 12, tzinfo=timezone.utc)


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def with_transaction(self, callback):
        return callback(self)


class SuccessfulWorker:
    engine_name = "DOCUMENT_VERIFY"

    async def execute(self, task_id, payload):
        return WorkerResultDTO(task_id=task_id, status=WorkerExecutionStatusEnum.SUCCESS,
                               execution_duration_ms=3.0, output={"verified": True})


class FailedWorker:
    engine_name = "DOCUMENT_VERIFY"

    async def execute(self, task_id, payload):
        return WorkerResultDTO(task_id=task_id, status=WorkerExecutionStatusEnum.FAILED,
                               execution_duration_ms=2.0, output={}, error_details="sensitive detail")


def runner_for(worker):
    tasks, audit, client = Mock(), Mock(), Mock()
    client.start_session.return_value = FakeSession()
    tasks.find_one_and_update.return_value = {
        "tenant_id": "tenant-a", "task_id": "task-a", "engine_name": "DOCUMENT_VERIFY",
        "payload": {"evidence_ref": "opaque"}, "status": "CLAIMED",
    }
    tasks.update_one.return_value.modified_count = 1
    tasks.find_one.return_value = {"attempts": 1, "max_attempts": 5}
    audit.count_documents.return_value = 0
    registry = EngineWorkerRegistry()
    registry.register_worker(worker)
    runner = DurableWorkerRunner(
        tasks=tasks, audit=audit, mongo_client=client,
        worker_registry=registry, worker_id="worker-a", now=lambda: NOW,
    )
    return runner, tasks, audit


def test_runner_executes_and_commits_success_with_audit():
    runner, tasks, audit = runner_for(SuccessfulWorker())
    assert asyncio.run(runner.run_once()) == "COMPLETED"
    assert tasks.update_one.call_args.args[1]["$set"]["status"] == "COMPLETED"
    assert audit.insert_one.call_args.args[0]["event_type"] == "COMPLETED"


def test_runner_records_failure_without_persisting_exception_text():
    runner, tasks, audit = runner_for(FailedWorker())
    assert asyncio.run(runner.run_once()) == "RETRY"
    update = tasks.update_one.call_args.args[1]
    assert update["$set"]["last_error_code"] == "WORKER_EXECUTION_FAILED"
    assert "sensitive detail" not in repr(update)
    assert audit.insert_one.call_args.args[0]["event_type"] == "RETRY"


def test_runner_returns_empty_without_starting_transaction():
    runner, tasks, audit = runner_for(SuccessfulWorker())
    tasks.find_one_and_update.return_value = None
    assert asyncio.run(runner.run_once()) == "EMPTY"
    assert audit.insert_one.call_count == 0
