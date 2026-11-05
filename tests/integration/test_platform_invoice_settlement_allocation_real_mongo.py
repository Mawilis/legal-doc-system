"""Real replica-set certificate for immutable settlement allocations."""
from datetime import datetime, timezone
import os
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.saas.domain.platform_invoice_settlement_allocation import PlatformInvoiceSettlementAllocation
from tools.eos.saas.billing.platform_invoice_settlement_allocation_registry import (
    PlatformInvoiceSettlementAllocationConflict,
    PlatformInvoiceSettlementAllocationRegistry,
)

URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"


@pytest.fixture()
def mongo_allocation_collection():
    assert os.environ.get("TEST_VENDOR_MONGO_URI") == URI
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    assert client.admin.command("hello").get("isWritablePrimary") is True
    db = client[f"invoice_allocation_{uuid4().hex}"]
    collection = db["allocations"]
    PlatformInvoiceSettlementAllocationRegistry.ensure_indexes(collection)
    try:
        yield client, collection
    finally:
        client.drop_database(db.name)
        client.close()


def value(tenant_id="tenant-a", observation_id="obs-1", amount=4000):
    return PlatformInvoiceSettlementAllocation(
        tenant_id=tenant_id,
        allocation_id=f"allocation-{observation_id}",
        observation_id=observation_id,
        observation_fingerprint="a" * 128,
        execution_truth_id="execution-1",
        invoice_id="invoice-1",
        invoice_evidence_fingerprint="b" * 128,
        currency="ZAR",
        amount_minor=amount,
        cumulative_paid_minor=amount,
        outstanding_minor=10000 - amount,
        allocation_sequence=1,
        allocated_at=datetime(2026, 11, 5, tzinfo=timezone.utc),
        allocation_status="PARTIAL",
    )


def test_durable_exact_replay_and_divergent_replay_rejection(mongo_allocation_collection):
    client, collection = mongo_allocation_collection
    first = value()
    with client.start_session() as session:
        with session.start_transaction():
            PlatformInvoiceSettlementAllocationRegistry.create(first, collection, session=session)
    with client.start_session() as session:
        with session.start_transaction():
            replay = PlatformInvoiceSettlementAllocationRegistry.create(first, collection, session=session)
            assert replay.fingerprint == first.fingerprint
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(PlatformInvoiceSettlementAllocationConflict):
                PlatformInvoiceSettlementAllocationRegistry.create(
                    value(amount=5000), collection, session=session
                )
    assert collection.count_documents({"tenant_id": "tenant-a"}) == 1


def test_allocation_abort_rolls_back_and_tenant_identity_isolated(mongo_allocation_collection):
    client, collection = mongo_allocation_collection
    with client.start_session() as session:
        with pytest.raises(RuntimeError, match="abort"):
            with session.start_transaction():
                PlatformInvoiceSettlementAllocationRegistry.create(value(), collection, session=session)
                raise RuntimeError("abort")
    assert collection.count_documents({"tenant_id": "tenant-a"}) == 0
    with client.start_session() as session:
        with session.start_transaction():
            PlatformInvoiceSettlementAllocationRegistry.create(value("tenant-a"), collection, session=session)
    with client.start_session() as session:
        with session.start_transaction():
            PlatformInvoiceSettlementAllocationRegistry.create(value("tenant-b"), collection, session=session)
    assert collection.count_documents({"observation_id": "obs-1"}) == 2
