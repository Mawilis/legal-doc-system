"""Replica-set certification for durable EOS worker leases and audit atomicity."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.runtime.durable_task_queue import (
    claim_next_task,
    complete_task,
    enqueue_task,
    ensure_task_queue_indexes,
    renew_task_lease,
    fail_task,
)

URI = os.environ.get("TEST_EOS_WORKER_MONGO_URI")
pytestmark = pytest.mark.skipif(not URI, reason="TEST_EOS_WORKER_MONGO_URI is not configured")
NOW = datetime(2026, 11, 8, 12, tzinfo=timezone.utc)


@pytest.fixture()
def queue_collections():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    assert client.admin.command("hello").get("isWritablePrimary") is True
    db = client[f"eos_worker_queue_{uuid4().hex}"]
    tasks, audit = db["tasks"], db["audit"]
    ensure_task_queue_indexes(tasks, audit)
    try:
        yield client, tasks, audit
    finally:
        client.drop_database(db.name)
        client.close()


def _enqueue(tasks):
    return enqueue_task(tasks, tenant_id="tenant-a", task_id="task-a",
                        task_type="DOCUMENT_VERIFY", payload={"evidence_ref": "opaque-1"},
                        now=NOW, max_attempts=2)


def test_replica_set_claim_fencing_and_transactional_completion(queue_collections):
    client, tasks, audit = queue_collections
    _enqueue(tasks)
    first = claim_next_task(tasks, worker_id="worker-a", lease_token="lease-a", now=NOW)
    assert first["attempts"] == 1
    assert claim_next_task(tasks, worker_id="worker-b", lease_token="lease-b", now=NOW) is None
    second = claim_next_task(tasks, worker_id="worker-b", lease_token="lease-b",
                             now=NOW + timedelta(seconds=61))
    assert second["lease_token"] == "lease-b"
    with client.start_session() as session:
        def commit(session):
            assert not complete_task(tasks, audit, tenant_id="tenant-a", task_id="task-a",
                                     worker_id="worker-a", lease_token="lease-a",
                                     now=NOW + timedelta(seconds=62), session=session)
            assert complete_task(tasks, audit, tenant_id="tenant-a", task_id="task-a",
                                 worker_id="worker-b", lease_token="lease-b",
                                 now=NOW + timedelta(seconds=62),
                                 result={"verification_ref": "verified-opaque"}, session=session)
        session.with_transaction(commit)
    assert tasks.find_one({"task_id": "task-a"})["status"] == "COMPLETED"
    assert list(audit.find({"task_id": "task-a"}))[0]["event_type"] == "COMPLETED"


def test_replica_set_retry_and_dead_letter_are_durable(queue_collections):
    client, tasks, audit = queue_collections
    _enqueue(tasks)
    claimed = claim_next_task(tasks, worker_id="worker-a", lease_token="lease-a", now=NOW)
    with client.start_session() as session:
        session.with_transaction(lambda s: fail_task(
            tasks, audit, tenant_id="tenant-a", task_id="task-a",
            worker_id="worker-a", lease_token="lease-a", now=NOW,
            error_code="TRANSIENT_FAILURE", session=s,
        ))
    retry = claim_next_task(tasks, worker_id="worker-b", lease_token="lease-b",
                            now=NOW + timedelta(seconds=2))
    assert retry["attempts"] == 2
    with client.start_session() as session:
        session.with_transaction(lambda s: fail_task(
            tasks, audit, tenant_id="tenant-a", task_id="task-a",
            worker_id="worker-b", lease_token="lease-b",
            now=NOW + timedelta(seconds=2), error_code="RETRY_EXHAUSTED", session=s,
        ))
    saved = tasks.find_one({"task_id": "task-a"})
    assert saved["status"] == "DEAD_LETTER"
    assert saved["attempts"] == 2
    assert audit.count_documents({"task_id": "task-a"}) == 2


def test_replica_set_lease_renewal_prevents_premature_reclaim(queue_collections):
    _, tasks, _ = queue_collections
    _enqueue(tasks)
    claim_next_task(tasks, worker_id="worker-a", lease_token="lease-a",
                    now=NOW, lease_seconds=5)
    assert renew_task_lease(tasks, tenant_id="tenant-a", task_id="task-a",
                            worker_id="worker-a", lease_token="lease-a",
                            now=NOW + timedelta(seconds=4), lease_seconds=10)
    assert claim_next_task(tasks, worker_id="worker-b", lease_token="lease-b",
                           now=NOW + timedelta(seconds=6), lease_seconds=5) is None
    reclaimed = claim_next_task(tasks, worker_id="worker-b", lease_token="lease-b",
                                now=NOW + timedelta(seconds=15), lease_seconds=5)
    assert reclaimed["lease_token"] == "lease-b"
