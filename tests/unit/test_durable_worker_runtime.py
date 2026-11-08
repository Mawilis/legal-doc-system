from unittest.mock import MagicMock

import pytest

from tools.eos.runtime.durable_worker_runtime import (
    TASK_AUDIT_COLLECTION,
    TASK_COLLECTION,
    create_durable_worker_runner,
    provision_durable_worker_indexes,
)
from tools.eos.runtime.worker_registry import EngineWorkerRegistry


def test_runner_uses_only_the_injected_canonical_database_graph():
    client, database = object(), MagicMock()
    database.client = client
    registry = EngineWorkerRegistry()
    runner = create_durable_worker_runner(
        worker_registry=registry, worker_id="worker-a",
        database=database, mongo_client=client,
    )
    assert runner.mongo_client is client
    assert runner.tasks is database[TASK_COLLECTION]
    assert runner.audit is database[TASK_AUDIT_COLLECTION]


def test_runner_rejects_mixed_database_and_client_graphs():
    database = MagicMock()
    database.client = object()
    with pytest.raises(RuntimeError, match="EOS_WORKER_DATABASE_CLIENT_MISMATCH"):
        create_durable_worker_runner(
            worker_registry=EngineWorkerRegistry(), worker_id="worker-a",
            database=database, mongo_client=object(),
        )


def test_runner_fails_closed_when_kernel_database_is_unavailable(monkeypatch):
    monkeypatch.setattr("tools.eos.runtime.durable_worker_runtime.get_database", lambda: None)
    monkeypatch.setattr("tools.eos.runtime.durable_worker_runtime.get_client", lambda: None)
    with pytest.raises(RuntimeError, match="EOS_KERNEL_DATABASE_NOT_READY"):
        create_durable_worker_runner(
            worker_registry=EngineWorkerRegistry(), worker_id="worker-a"
        )


def test_index_provisioning_is_explicit_and_uses_named_collections():
    database = MagicMock()
    tasks, audit = MagicMock(), MagicMock()
    database.__getitem__.side_effect = {
        TASK_COLLECTION: tasks,
        TASK_AUDIT_COLLECTION: audit,
    }.get
    provision_durable_worker_indexes(database)
    assert tasks.create_index.call_count == 3
    assert audit.create_index.call_count == 1
