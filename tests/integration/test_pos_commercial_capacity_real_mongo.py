"""Real replica-set certification of cumulative POS return/refund limits."""
from __future__ import annotations

import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.pos_commercial import POSLineItem, POSSale, POSStatus
from tools.eos.saas.billing.pos_commercial_capacity_registry import (
    COLLECTION_NAME, POSCommercialCapacityRegistry, POSCommercialCapacityExceeded,
)


URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture
def runtime():
    client = MongoClient(URI, serverSelectionTimeoutMS=3000)
    db = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"Mongo unavailable: {type(error).__name__}")
        if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary"):
            pytest.skip("expected writable wilsyVendorCertRS replica set")
        db = client[f"pos_capacity_{uuid.uuid4().hex}"]
        collection = db.get_collection(COLLECTION_NAME, write_concern=WriteConcern(w="majority", j=True))
        POSCommercialCapacityRegistry.ensure_indexes(collection)
        yield client, collection
    finally:
        if db is not None:
            client.drop_database(db.name)
        client.close()


def _sale():
    return POSSale(
        "tenant-a", "store-a", f"sale-{uuid.uuid4().hex}", "ZAR",
        (POSLineItem("p1", "SKU-1", "Widget", 2, 100, 0, 0, "ZAR"),),
        POSStatus.COMPLETED_COMMERCIAL, f"sale-idem-{uuid.uuid4().hex}",
    )


def _transaction(client, callback):
    with client.start_session() as session:
        return session.with_transaction(callback)


def test_replica_set_enforces_cumulative_return_quantity(runtime):
    client, collection = runtime
    sale = _sale()
    first = _transaction(client, lambda tx: POSCommercialCapacityRegistry.reserve_return(
        sale=sale, sku="SKU-1", quantity=1, idempotency_key="return-1",
        collection=collection, session=tx,
    ))
    second = _transaction(client, lambda tx: POSCommercialCapacityRegistry.reserve_return(
        sale=sale, sku="SKU-1", quantity=1, idempotency_key="return-2",
        collection=collection, session=tx,
    ))
    assert first["reserved_amount"] == 1 and second["reserved_amount"] == 2
    with pytest.raises(POSCommercialCapacityExceeded):
        _transaction(client, lambda tx: POSCommercialCapacityRegistry.reserve_return(
            sale=sale, sku="SKU-1", quantity=1, idempotency_key="return-3",
            collection=collection, session=tx,
        ))
    current = collection.find_one({"tenant_id": sale.tenant_id, "sale_id": sale.sale_id, "capacity_type": "RETURN_QUANTITY"})
    assert current["reserved_amount"] == 2 and current["revision"] == 1


def test_replica_set_enforces_cumulative_refund_amount(runtime):
    client, collection = runtime
    sale = _sale()
    first = _transaction(client, lambda tx: POSCommercialCapacityRegistry.reserve_refund(
        sale=sale, amount_minor=100, idempotency_key="refund-1",
        collection=collection, session=tx,
    ))
    second = _transaction(client, lambda tx: POSCommercialCapacityRegistry.reserve_refund(
        sale=sale, amount_minor=100, idempotency_key="refund-2",
        collection=collection, session=tx,
    ))
    assert first["reserved_amount"] == 100 and second["reserved_amount"] == 200
    with pytest.raises(POSCommercialCapacityExceeded):
        _transaction(client, lambda tx: POSCommercialCapacityRegistry.reserve_refund(
            sale=sale, amount_minor=1, idempotency_key="refund-3",
            collection=collection, session=tx,
        ))
    current = collection.find_one({"tenant_id": sale.tenant_id, "sale_id": sale.sale_id, "capacity_type": "REFUND_AMOUNT"})
    assert current["reserved_amount"] == sale.total_minor and current["revision"] == 1
