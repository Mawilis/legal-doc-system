from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from tools.eos.runtime.durable_task_queue import (
    DurableTaskQueueError,
    claim_next_task,
    complete_task,
    enqueue_task,
    fail_task,
    renew_task_lease,
)

NOW = datetime(2026, 11, 8, 12, tzinfo=timezone.utc)


def test_enqueue_is_tenant_scoped_and_idempotency_keyed():
    tasks = Mock()
    document = enqueue_task(
        tasks, tenant_id="tenant-a", task_id="task-a", task_type="EMAIL",
        payload={"recipient_ref": "opaque-1"}, now=NOW,
    )
    assert document["status"] == "PENDING"
    assert document["payload_sha256"]
    assert tasks.insert_one.call_args.kwargs["session"] is None


def test_enqueue_rejects_missing_tenant_and_non_json_payload():
    with pytest.raises(DurableTaskQueueError, match="TASK_QUEUE_TENANT_REQUIRED"):
        enqueue_task(Mock(), tenant_id=" ", task_id="t", task_type="EMAIL", payload={}, now=NOW)
    with pytest.raises(DurableTaskQueueError, match="TASK_QUEUE_PAYLOAD_NOT_JSON"):
        enqueue_task(Mock(), tenant_id="tenant-a", task_id="t", task_type="EMAIL", payload={"bad": object()}, now=NOW)


def test_claim_uses_atomic_lease_and_field_to_field_attempt_guard():
    tasks = Mock()
    tasks.find_one_and_update.return_value = {"task_id": "task-a", "status": "CLAIMED", "attempts": 1}
    claimed = claim_next_task(tasks, worker_id="worker-a", lease_token="lease-a", now=NOW)
    assert claimed["attempts"] == 1
    query = tasks.find_one_and_update.call_args.args[0]
    assert query["$expr"] == {"$lt": ["$attempts", "$max_attempts"]}
    update = tasks.find_one_and_update.call_args.args[1]
    assert update["$inc"] == {"attempts": 1}
    assert update["$set"]["lease_until"] == NOW + timedelta(seconds=60)


def test_claim_rejects_nonpositive_lease():
    with pytest.raises(DurableTaskQueueError, match="TASK_QUEUE_LEASE_DURATION_INVALID"):
        claim_next_task(Mock(), worker_id="worker", lease_token="lease", now=NOW, lease_seconds=0)


def test_completion_requires_caller_transaction_and_fences_lease_owner():
    tasks, audit = Mock(), Mock()
    audit.count_documents.return_value = 0
    with pytest.raises(DurableTaskQueueError, match="TASK_QUEUE_AUDIT_TRANSACTION_REQUIRED"):
        complete_task(tasks, audit, tenant_id="tenant-a", task_id="task-a",
                      worker_id="worker-a", lease_token="lease-a", now=NOW)
    tasks.update_one.return_value.modified_count = 1
    session = object()
    assert complete_task(tasks, audit, tenant_id="tenant-a", task_id="task-a",
                         worker_id="worker-a", lease_token="lease-a", now=NOW,
                         result={"artifact_ref": "opaque"}, session=session)
    query = tasks.update_one.call_args.args[0]
    assert query["lease_token"] == "lease-a"
    assert audit.insert_one.call_args.kwargs["session"] is session


def test_stale_worker_cannot_complete_or_append_audit():
    tasks, audit = Mock(), Mock()
    tasks.update_one.return_value.modified_count = 0
    assert not complete_task(tasks, audit, tenant_id="tenant-a", task_id="task-a",
                             worker_id="worker-old", lease_token="stale", now=NOW, session=object())
    audit.insert_one.assert_not_called()


def test_failure_retries_with_exponential_backoff_and_redacted_code():
    tasks, audit = Mock(), Mock()
    audit.count_documents.return_value = 0
    tasks.find_one.return_value = {"attempts": 2, "max_attempts": 5}
    tasks.update_one.return_value.modified_count = 1
    session = object()
    state = fail_task(tasks, audit, tenant_id="tenant-a", task_id="task-a",
                      worker_id="worker-a", lease_token="lease-a", now=NOW,
                      error_code="DELIVERY_FAILED", retry_base_seconds=2, session=session)
    assert state == "RETRY"
    update = tasks.update_one.call_args.args[1]
    assert update["$set"]["available_at"] == NOW + timedelta(seconds=4)
    assert "credential" not in repr(update).lower()
    assert audit.insert_one.call_args.kwargs["session"] is session


def test_failure_dead_letters_after_attempt_limit():
    tasks, audit = Mock(), Mock()
    audit.count_documents.return_value = 0
    tasks.find_one.return_value = {"attempts": 5, "max_attempts": 5}
    tasks.update_one.return_value.modified_count = 1
    assert fail_task(tasks, audit, tenant_id="tenant-a", task_id="task-a",
                     worker_id="worker-a", lease_token="lease-a", now=NOW,
                     error_code="WORKER_FAILED", session=object()) == "DEAD_LETTER"


def test_failure_rejects_untrusted_error_text_and_lost_lease():
    with pytest.raises(DurableTaskQueueError, match="TASK_QUEUE_ERROR_CODE_INVALID"):
        fail_task(Mock(), Mock(), tenant_id="tenant-a", task_id="task-a",
                  worker_id="worker-a", lease_token="lease-a", now=NOW,
                  error_code="secret=credential", session=object())
    tasks = Mock()
    tasks.find_one.return_value = None
    with pytest.raises(DurableTaskQueueError, match="TASK_QUEUE_LEASE_LOST"):
        fail_task(tasks, Mock(), tenant_id="tenant-a", task_id="task-a",
                  worker_id="worker-a", lease_token="lease-a", now=NOW,
                  error_code="WORKER_FAILED", session=object())


def test_lease_renewal_is_fenced_by_live_owner_and_token():
    tasks = Mock()
    tasks.update_one.return_value.modified_count = 1
    assert renew_task_lease(tasks, tenant_id="tenant-a", task_id="task-a",
                            worker_id="worker-a", lease_token="lease-a",
                            now=NOW, lease_seconds=90)
    query = tasks.update_one.call_args.args[0]
    assert query["lease_token"] == "lease-a"
    assert query["lease_until"] == {"$gt": NOW}
    assert tasks.update_one.call_args.args[1]["$set"]["lease_until"] == NOW + timedelta(seconds=90)



def test_claim_is_restricted_to_registered_engine_names():
    tasks = Mock()
    tasks.find_one_and_update.return_value = None
    claim_next_task(tasks, worker_id="worker-a", lease_token="lease-a",
                    now=NOW, engine_names=("COMPLIANCE_SCAN",))
    assert tasks.find_one_and_update.call_args.args[0]["engine_name"] == {
        "$in": ["COMPLIANCE_SCAN"]
    }
