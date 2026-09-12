"""M12-P2 bounded real-Mongo certificate for durable intelligence evidence.

TITLE: Durable Billing Intelligence Evidence Real-Mongo Certificate
VERSION: v1.0.0-M12-P2-RM
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify actual replica-set durability, replay, corruption rejection,
         tenant isolation, and caller-owned transaction semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_billing_intelligence_registry_real_mongo.py
COLLABORATION / OWNERSHIP: M12-P2 bounded integration certificate; registry
                            owns persistence only and caller owns transactions.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0 establishes bounded M12-P2 durable evidence certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic test tenants only.
TENANT BOUNDARY: Every lookup and index is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Persistence certificate only; no derivation or authority.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, paid state, closure,
                              provider, payment, or refund authority.
FAIL-CLOSED DECLARATION: Mongo outage, wrong replica set, corruption, and
                         divergent replay fail the certificate.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing.billing_intelligence_engine import derive_billing_intelligence
from tools.eos.saas.billing.billing_intelligence_registry import (
    COLLECTION,
    BillingIntelligenceRegistry,
    BillingIntelligenceRegistryError,
)
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


def _value(tenant_id: str, *, amount: int = 1250) -> Any:
    receivable = CommercialReceivable(
        tenant_id=tenant_id,
        receivable_family=ReceivableFamily.CLIENT,
        receivable_id="r-1",
        source_invoice_id="invoice-1",
        currency="ZAR",
        original_amount_minor=amount,
        adjustment_amount_minor=0,
        outstanding_amount_minor=amount,
        source_invoice_fingerprint="a" * 128,
        status=ReceivableStatus.OPEN,
    )
    aging = CommercialReceivableAging.from_receivable(
        receivable,
        due_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        as_of=AS_OF,
    )
    dunning = CommercialReceivableDunning.from_aging(aging, effective_at=AS_OF)
    return derive_billing_intelligence(
        tenant_id=tenant_id,
        receivables=(receivable,),
        aging=(aging,),
        dunning=(dunning,),
        as_of=AS_OF,
    )


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Collection[dict[str, Any]]]]:
    client: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary") is True
        database = client[f"m12p2_billing_intelligence_{uuid.uuid4().hex}"]
        collection = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        BillingIntelligenceRegistry.ensure_indexes(collection)
        yield client, database, collection
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def test_real_mongo_persist_hydrate_and_indexes(mongo_context: Any) -> None:
    _, database, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _value(tenant)
    created = BillingIntelligenceRegistry.create(value, collection)
    identity = collection.find_one({"tenant_id": tenant})["evidence_identity"]
    hydrated = BillingIntelligenceRegistry.get(tenant, identity, collection)
    assert created == hydrated == value
    assert collection.count_documents({"tenant_id": tenant}) == 1
    names = {item["name"]: item for item in collection.list_indexes()}
    assert names["tenant_billing_intelligence_identity_unique"]["unique"] is True
    assert names["tenant_billing_intelligence_fingerprint_unique"]["unique"] is True
    assert database.name.startswith("m12p2_billing_intelligence_")


def test_exact_replay_and_divergence_are_durable_fail_closed(mongo_context: Any) -> None:
    _, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _value(tenant)
    first = BillingIntelligenceRegistry.create(value, collection)
    second = BillingIntelligenceRegistry.create(value, collection)
    assert first == second
    assert collection.count_documents({"tenant_id": tenant}) == 1
    divergent = _value(tenant, amount=1249)
    with pytest.raises(BillingIntelligenceRegistryError):
        BillingIntelligenceRegistry.create(divergent, collection)


def test_cross_tenant_and_all_corruption_classes_reject(mongo_context: Any) -> None:
    _, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _value(tenant)
    BillingIntelligenceRegistry.create(value, collection)
    original = collection.find_one({"tenant_id": tenant})
    assert original is not None
    identity = original["evidence_identity"]
    with pytest.raises(BillingIntelligenceRegistryError, match="NOT_FOUND"):
        BillingIntelligenceRegistry.get("other-tenant", identity, collection)
    for field, replacement in (
        ("evidence_fingerprint", "b" * 128),
        ("source_provenance", [["commercial_receivable", "r-1", "c" * 128]]),
        ("receivable_count", 99),
        ("evidence_contract", "WILSY-BILLING-INTELLIGENCE-EVIDENCE/V2"),
    ):
        collection.update_one({"tenant_id": tenant}, {"$set": {field: replacement}})
        with pytest.raises(BillingIntelligenceRegistryError):
            BillingIntelligenceRegistry.get(tenant, identity, collection)
        collection.replace_one({"tenant_id": tenant}, deepcopy(original))


def test_caller_transaction_abort_rolls_back_and_commit_is_visible(mongo_context: Any) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _value(tenant)
    with client.start_session() as session:
        session.start_transaction()
        BillingIntelligenceRegistry.create(value, collection, session=session)
        assert collection.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 0
    with client.start_session() as session:
        session.start_transaction()
        BillingIntelligenceRegistry.create(value, collection, session=session)
        session.commit_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_registry_persists_no_financial_authority_fields(mongo_context: Any) -> None:
    _, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    BillingIntelligenceRegistry.create(_value(tenant), collection)
    document = collection.find_one({"tenant_id": tenant})
    assert document is not None
    for forbidden in ("execution", "settlement", "paid_state", "refund", "payment"):
        assert forbidden not in document
