"""Replica-set certification for leased settlement outbox delivery."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.saas.billing.platform_settlement_outbox import (
    claim_next_settlement_event,
    mark_settlement_event_delivered,
    schedule_settlement_event_retry,
)

URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
NOW = datetime(2026, 11, 5, 8, tzinfo=timezone.utc)


@pytest.fixture()
def outbox():
    assert os.environ.get("TEST_VENDOR_MONGO_URI") == URI
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    assert client.admin.command("hello").get("isWritablePrimary") is True
    db = client[f"settlement_outbox_{uuid4().hex}"]
    collection = db["outbox"]
    collection.create_index([("tenant_id", 1), ("event_key", 1)], unique=True)
    try:
        yield collection
    finally:
        client.drop_database(db.name)
        client.close()


def _event(collection):
    collection.insert_one({
        "tenant_id": "tenant-a",
        "event_key": "settlement-a",
        "event_type": "PLATFORM_INVOICE_SETTLED",
        "delivery_status": "PENDING",
        "delivery_attempts": 0,
        "available_at": NOW.isoformat(),
    })


def test_claim_ack_and_audit_payload_remains_separate(outbox):
    _event(outbox)
    claimed = claim_next_settlement_event(
        outbox, worker_id="worker-a", lease_token="lease-a", now=NOW
    )
    assert claimed["delivery_attempts"] == 1
    assert mark_settlement_event_delivered(
        outbox, tenant_id="tenant-a", event_key="settlement-a",
        worker_id="worker-a", lease_token="lease-a", delivered_at=NOW,
    )
    saved = outbox.find_one({"event_key": "settlement-a"})
    assert saved["delivery_status"] == "DELIVERED"
    assert saved["event_type"] == "PLATFORM_INVOICE_SETTLED"


def test_expired_lease_can_be_reclaimed_and_stale_worker_is_fenced(outbox):
    _event(outbox)
    first = claim_next_settlement_event(
        outbox, worker_id="worker-a", lease_token="lease-a", now=NOW,
        lease_seconds=5,
    )
    second = claim_next_settlement_event(
        outbox, worker_id="worker-b", lease_token="lease-b",
        now=NOW + timedelta(seconds=6), lease_seconds=5,
    )
    assert first["lease_token"] == "lease-a"
    assert second["lease_token"] == "lease-b"
    assert not mark_settlement_event_delivered(
        outbox, tenant_id="tenant-a", event_key="settlement-a",
        worker_id="worker-a", lease_token="lease-a",
        delivered_at=NOW + timedelta(seconds=6),
    )
    assert mark_settlement_event_delivered(
        outbox, tenant_id="tenant-a", event_key="settlement-a",
        worker_id="worker-b", lease_token="lease-b",
        delivered_at=NOW + timedelta(seconds=6),
    )


def test_retry_becomes_claimable_at_scheduled_time(outbox):
    _event(outbox)
    claimed = claim_next_settlement_event(
        outbox, worker_id="worker-a", lease_token="lease-a", now=NOW
    )
    assert schedule_settlement_event_retry(
        outbox, tenant_id="tenant-a", event_key="settlement-a",
        worker_id="worker-a", lease_token="lease-a",
        retry_at=NOW + timedelta(minutes=1), error_code="DELIVERY_FAILED",
    )
    assert claim_next_settlement_event(
        outbox, worker_id="worker-b", lease_token="lease-b",
        now=NOW + timedelta(seconds=30),
    ) is None
    retried = claim_next_settlement_event(
        outbox, worker_id="worker-b", lease_token="lease-b",
        now=NOW + timedelta(minutes=1),
    )
    assert retried["delivery_attempts"] == 2
