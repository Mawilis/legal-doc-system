from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from tools.eos.saas.billing.platform_settlement_outbox import (
    SettlementOutboxError,
    claim_next_settlement_event,
    dispatch_one_settlement_event,
    mark_settlement_event_delivered,
    schedule_settlement_event_retry,
)

NOW = datetime(2026, 11, 5, 8, tzinfo=timezone.utc)


def test_claim_uses_lease_and_increments_attempt_count():
    collection = Mock()
    collection.find_one_and_update.return_value = {
        "tenant_id": "tenant-a",
        "event_key": "event-a",
        "delivery_status": "CLAIMED",
        "delivery_attempts": 1,
    }
    result = claim_next_settlement_event(
        collection, worker_id="worker-a", lease_token="lease-a", now=NOW
    )
    assert result["delivery_status"] == "CLAIMED"
    args, kwargs = collection.find_one_and_update.call_args
    update = args[1]
    assert update["$inc"] == {"delivery_attempts": 1}
    assert update["$set"]["lease_token"] == "lease-a"
    assert update["$set"]["lease_until"] == NOW + timedelta(seconds=60)


def test_ack_is_fenced_by_worker_and_lease_token():
    collection = Mock()
    collection.update_one.return_value.modified_count = 1
    assert mark_settlement_event_delivered(
        collection,
        tenant_id="tenant-a",
        event_key="event-a",
        worker_id="worker-a",
        lease_token="lease-a",
        delivered_at=NOW,
    )
    query = collection.update_one.call_args.args[0]
    assert query["claimed_by"] == "worker-a"
    assert query["lease_token"] == "lease-a"


def test_stale_worker_cannot_acknowledge():
    collection = Mock()
    collection.update_one.return_value.modified_count = 0
    assert not mark_settlement_event_delivered(
        collection,
        tenant_id="tenant-a",
        event_key="event-a",
        worker_id="old-worker",
        lease_token="expired-lease",
        delivered_at=NOW,
    )


def test_retry_releases_lease_and_stores_only_error_code():
    collection = Mock()
    collection.update_one.return_value.modified_count = 1
    assert schedule_settlement_event_retry(
        collection,
        tenant_id="tenant-a",
        event_key="event-a",
        worker_id="worker-a",
        lease_token="lease-a",
        retry_at=NOW + timedelta(minutes=1),
        error_code="DELIVERY_FAILED",
    )
    update = collection.update_one.call_args.args[1]
    assert update["$set"]["delivery_status"] == "RETRY"
    assert "last_error" not in update["$set"]


def test_dispatch_requires_downstream_idempotency_key():
    collection = Mock()
    collection.find_one_and_update.return_value = {
        "tenant_id": "tenant-a",
        "event_key": "event-a",
        "delivery_status": "CLAIMED",
    }
    collection.update_one.return_value.modified_count = 1
    delivered = []
    result = dispatch_one_settlement_event(
        collection,
        worker_id="worker-a",
        lease_token="lease-a",
        now=NOW,
        deliver=lambda event, key: delivered.append(key),
    )
    assert result == "DELIVERED"
    assert delivered == ["event-a"]


def test_dispatch_retries_without_leaking_exception_text():
    collection = Mock()
    collection.find_one_and_update.return_value = {
        "tenant_id": "tenant-a",
        "event_key": "event-a",
        "delivery_status": "CLAIMED",
    }
    collection.update_one.return_value.modified_count = 1
    result = dispatch_one_settlement_event(
        collection,
        worker_id="worker-a",
        lease_token="lease-a",
        now=NOW,
        deliver=lambda event, key: (_ for _ in ()).throw(RuntimeError("secret-bearing error")),
    )
    assert result == "RETRY"
    update = collection.update_one.call_args.args[1]
    assert update["$set"]["last_error_code"] == "DELIVERY_FAILED"
    assert "secret-bearing error" not in repr(update)


def test_invalid_error_code_fails_closed():
    with pytest.raises(SettlementOutboxError):
        schedule_settlement_event_retry(
            Mock(),
            tenant_id="tenant-a",
            event_key="event-a",
            worker_id="worker-a",
            lease_token="lease-a",
            retry_at=NOW,
            error_code="credential=secret",
        )
