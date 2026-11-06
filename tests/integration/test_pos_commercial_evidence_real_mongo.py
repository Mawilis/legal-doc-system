"""Real replica-set certificate for durable POS tender, cash, return and refund evidence."""
from __future__ import annotations

import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.pos_commercial import (
    POSCashTender, POSLineItem, POSSale, POSRefundIntent, POSReturnIntent,
    POSStatus, POSTenderIntent, POSTenderType,
)
from tools.eos.saas.billing import pos_commercial_evidence_registry as registry


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture
def mongo_context():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET or not hello.get("isWritablePrimary"):
            pytest.skip("expected writable wilsyVendorCertRS replica set")
        database = client[f"pos_evidence_rm_{uuid.uuid4().hex}"]
        collection = database.get_collection(registry.COLLECTION_NAME, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        registry.ensure_indexes(collection)
        yield client, collection
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _sale():
    return POSSale(
        "tenant-a", "store-a", f"sale-{uuid.uuid4().hex}", "ZAR",
        (POSLineItem("product-1", "SKU-1", "Widget", 2, 100, 0, 0, "ZAR"),),
        POSStatus.COMPLETED_COMMERCIAL, f"sale-idem-{uuid.uuid4().hex}",
    )


def _transaction(client, callback):
    with client.start_session() as session:
        return session.with_transaction(callback)


def test_real_replica_set_persists_all_four_commercial_evidence_types(mongo_context):
    client, collection = mongo_context
    sale = _sale()
    tender = POSTenderIntent(sale.tenant_id, sale.location_id, sale.sale_id, POSTenderType.CARD, sale.total_minor, "ZAR", "tender-source-1")
    cash = POSCashTender(sale.tenant_id, sale.location_id, sale.sale_id, "ZAR", sale.total_minor, sale.total_minor + 25, "operator-a", "2026-11-06T10:00:00+00:00")
    returned = POSReturnIntent(sale.tenant_id, sale.location_id, "return-1", sale.sale_id, "SKU-1", 1, "customer return", "return-source-1")
    refund = POSRefundIntent(sale.tenant_id, sale.location_id, "refund-1", sale.sale_id, 100, "ZAR", "return-1", "refund-source-1")
    values = [
        (tender, "tender-1", "tender-idem"),
        (cash, "cash-1", "cash-idem"),
        (returned, "return-1", "return-idem"),
        (refund, "refund-1", "refund-idem"),
    ]
    stored = _transaction(client, lambda tx: [
        registry.record_evidence(
            sale=sale, evidence=value, evidence_id=evidence_id,
            idempotency_key=idempotency, recorded_by_principal_id="operator-a",
            collection=collection, session=tx,
        )
        for value, evidence_id, idempotency in values
    ])
    assert {row["evidence_type"] for row in stored} == {"TENDER_INTENT", "CASH_TENDER", "RETURN_INTENT", "REFUND_INTENT"}
    assert all(row["sale_fingerprint"] == sale.fingerprint for row in stored)
    assert all(row["recorded_by_principal_id"] == "operator-a" for row in stored)
    assert all(row["recorded_at"] for row in stored)
    assert collection.count_documents({"tenant_id": sale.tenant_id, "location_id": sale.location_id, "sale_id": sale.sale_id}) == 4

    replay = _transaction(client, lambda tx: registry.record_evidence(
        sale=sale, evidence=tender, evidence_id="tender-1",
        idempotency_key="tender-idem", recorded_by_principal_id="operator-a",
        collection=collection, session=tx,
    ))
    history = _transaction(client, lambda tx: registry.list_sale_evidence(
        tenant_id=sale.tenant_id, location_id=sale.location_id,
        sale_id=sale.sale_id, collection=collection, session=tx,
    ))
    foreign = _transaction(client, lambda tx: registry.list_sale_evidence(
        tenant_id="tenant-b", location_id=sale.location_id,
        sale_id=sale.sale_id, collection=collection, session=tx,
    ))
    assert replay["fingerprint"] == stored[0]["fingerprint"]
    assert len(history) == 4 and foreign == ()


def test_real_replica_set_rejects_divergent_replay_and_cross_location_evidence(mongo_context):
    client, collection = mongo_context
    sale = _sale()
    tender = POSTenderIntent(sale.tenant_id, sale.location_id, sale.sale_id, POSTenderType.CARD, sale.total_minor, "ZAR", "same-source")
    _transaction(client, lambda tx: registry.record_evidence(
        sale=sale, evidence=tender, evidence_id="tender-1", idempotency_key="idem-1",
        recorded_by_principal_id="operator-a", collection=collection, session=tx,
    ))
    divergent = POSTenderIntent(sale.tenant_id, sale.location_id, sale.sale_id, POSTenderType.BANK, sale.total_minor, "ZAR", "same-source")
    with pytest.raises(registry.POSCommercialEvidenceConflict):
        _transaction(client, lambda tx: registry.record_evidence(
            sale=sale, evidence=divergent, evidence_id="tender-1", idempotency_key="idem-1",
            recorded_by_principal_id="operator-a", collection=collection, session=tx,
        ))
    other_location_sale = POSSale("tenant-a", "store-b", sale.sale_id, "ZAR", sale.lines, POSStatus.COMPLETED_COMMERCIAL, "other-sale-idem")
    with pytest.raises(registry.POSCommercialEvidenceRegistryError):
        _transaction(client, lambda tx: registry.record_evidence(
            sale=other_location_sale, evidence=tender, evidence_id="tender-2", idempotency_key="idem-2",
            recorded_by_principal_id="operator-a", collection=collection, session=tx,
        ))
    assert collection.count_documents({"sale_id": sale.sale_id}) == 1
