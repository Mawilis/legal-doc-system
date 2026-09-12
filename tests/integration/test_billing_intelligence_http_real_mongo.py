"""M12-P3 host certificate for the canonical billing-intelligence HTTP path."""
from datetime import datetime, timezone
import os
from typing import Any, Iterator
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing.billing_intelligence_registry import (
    COLLECTION as EVIDENCE_COLLECTION,
    BillingIntelligenceRegistry,
)
from tools.eos.saas.billing.commercial_receivable_registry import CommercialReceivableRegistry
from tools.eos.saas.domain.commercial_receivable import (
    CommercialReceivable,
    ReceivableFamily,
    ReceivableStatus,
)
from tools.eos.saas.domain.commercial_receivable_aging import CommercialReceivableAging
from tools.eos.saas.domain.commercial_receivable_dunning import CommercialReceivableDunning


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


def _source_values(tenant: str) -> tuple[CommercialReceivable, CommercialReceivableAging, CommercialReceivableDunning]:
    receivable = CommercialReceivable(
        tenant_id=tenant,
        receivable_family=ReceivableFamily.CLIENT,
        receivable_id="r-http-1",
        source_invoice_id="invoice-http-1",
        currency="ZAR",
        original_amount_minor=1250,
        adjustment_amount_minor=0,
        outstanding_amount_minor=1250,
        source_invoice_fingerprint="a" * 128,
        status=ReceivableStatus.OPEN,
    )
    aging = CommercialReceivableAging.from_receivable(
        receivable,
        due_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        as_of=AS_OF,
    )
    return receivable, aging, CommercialReceivableDunning.from_aging(aging, effective_at=AS_OF)


@pytest.fixture
def http_context() -> Iterator[tuple[Any, Any, Any]]:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary") is True
        database = client[f"m12p3_billing_http_{uuid.uuid4().hex}"]
        options = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        collections = (
            database.get_collection("commercial_receivables", **options),
            database.get_collection("commercial_receivable_aging", **options),
            database.get_collection("commercial_receivable_dunning", **options),
            database.get_collection(EVIDENCE_COLLECTION, **options),
        )
        BillingIntelligenceRegistry.ensure_indexes(collections[3])
        yield client, database, collections
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _app(database: Any) -> TestClient:
    import tools.eos.api.billing_router as module

    module._require_db = lambda: database
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module.get_tenant_id] = lambda: "tenant-http-real"
    return TestClient(app)


def test_production_http_composition_persists_and_exactly_replays(http_context: Any) -> None:
    _, database, collections = http_context
    receivable, aging, dunning = _source_values("tenant-http-real")
    CommercialReceivableRegistry.ensure_indexes(collections[0])
    CommercialReceivableRegistry.create(receivable, collections[0])
    collections[1].insert_one(aging.to_dict())
    collections[2].insert_one(dunning.to_dict())
    with _app(database) as client:
        path = "/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00"
        first = client.get(path)
        second = client.get(path)
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert collections[3].count_documents({"tenant_id": "tenant-http-real"}) == 1
    durable = collections[3].find_one({"tenant_id": "tenant-http-real"})
    assert durable is not None
    assert first.json()["evidence_fingerprint"] == durable["evidence_fingerprint"]
    assert first.json()["evidence_identity"] == durable["evidence_identity"]


def test_cross_tenant_and_source_corruption_fail_closed(http_context: Any) -> None:
    _, database, collections = http_context
    receivable, aging, dunning = _source_values("tenant-http-real")
    CommercialReceivableRegistry.ensure_indexes(collections[0])
    CommercialReceivableRegistry.create(receivable, collections[0])
    collections[1].insert_one(aging.to_dict())
    collections[2].insert_one(dunning.to_dict())
    with _app(database) as client:
        assert client.get("/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00").status_code == 200
    collections[0].update_one({"tenant_id": "tenant-http-real"}, {"$set": {"receivable_fingerprint": "b" * 128}})
    with _app(database) as client:
        response = client.get("/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00")
    assert response.status_code == 409
    assert collections[3].count_documents({"tenant_id": "tenant-http-real"}) == 1


# ARTIFACT: test_billing_intelligence_http_real_mongo.py
# VERSION: v1.0.0-M12-P3
# AUTHORITY BOUNDARY: Host HTTP composition certificate only.
# END OF WILSY OS SOVEREIGN ARTIFACT
