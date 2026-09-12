"""WILSY OS M12-P6 bounded host-backed billing-intelligence certificate.

TITLE: Billing Intelligence P6 Real-Mongo Durability Certificate
VERSION: v1.0.0-M12-P6
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify tenant-scoped recurring-revenue evidence survives a caller-
         owned Mongo transaction and exact replay on the certified replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_billing_intelligence_p6_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for P6; P1 derives, P2 persists,
                            P3 composes, and the caller owns transactions.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M12-P6 certifies bounded real-Mongo recurring evidence,
           durable fingerprint identity, tenant isolation, and exact replay.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Isolated random test database; no secrets or providers.
TENANT BOUNDARY: Every document and lookup is keyed by the explicit test tenant.
AUTHORITY BOUNDARY: Evidence durability only; no financial execution or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Replica-set, transaction, schema, and replay drift reject.
"""
from datetime import datetime, timezone
import os
from typing import Any, Iterator
import uuid

from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
import pytest

from tools.eos.saas.billing.billing_intelligence_orchestrator import BillingIntelligenceOrchestrator
from tools.eos.saas.billing.billing_intelligence_registry import (
    BillingIntelligenceRegistry,
)
from tools.eos.saas.billing.subscription_registry import (
    _create_material,
    _fingerprint_create_material,
)
from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


def _subscription(tenant: str) -> SubscriptionEntity:
    return SubscriptionEntity(
        tenant_id=tenant,
        plan_id="plan-pro",
        plan=PlanTiers.PROFESSIONAL,
        amount=120.0,
        currency="ZAR",
        billing_frequency=BillingFrequency.MONTHLY,
        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        current_period_start=datetime(2026, 9, 1, tzinfo=timezone.utc),
        current_period_end=datetime(2026, 10, 1, tzinfo=timezone.utc),
        idempotency_key="sub-create-1",
        subscription_id="sub-1",
        status=SubscriptionStatus.ACTIVE,
        plan_catalogue_version=1,
    )


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, str]]:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary"):
            pytest.fail("M12P6_CERTIFIED_REPLICA_SET_REQUIRED")
        database = client[f"m12p6_billing_{uuid.uuid4().hex}"]
        yield client, database, "tenant-m12-p6-real"
    except Exception as error:
        if database is None:
            pytest.fail(f"M12P6_MONGO_UNAVAILABLE:{error}")
        raise
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def test_recurring_evidence_is_durable_and_exactly_replayed(mongo_context: Any) -> None:
    client, database, tenant = mongo_context
    options = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
    receivables = database.get_collection("commercial_receivables", **options)
    aging = database.get_collection("commercial_receivable_aging", **options)
    dunning = database.get_collection("commercial_receivable_dunning", **options)
    subscriptions = database.get_collection("subscriptions", **options)
    evidence = database.get_collection("billing_intelligence_evidence", **options)
    BillingIntelligenceRegistry.ensure_indexes(evidence)
    value = _subscription(tenant)
    material = _create_material(tenant, {"idempotencyKey": value.idempotency_key})
    subscriptions.insert_one(value.to_dict() | {
        "_registry_schema": "WILSY-SUBSCRIPTION-REGISTRY/V1",
        "_registry_create_material": material,
        "_registry_create_fingerprint": _fingerprint_create_material(material),
        "_registry_revision": 1,
    })
    owner = BillingIntelligenceOrchestrator(
        receivable_collection=receivables,
        aging_collection=aging,
        dunning_collection=dunning,
        evidence_collection=evidence,
        subscription_collection=subscriptions,
    )
    with client.start_session() as session:
        session.start_transaction()
        first = owner.collect_and_persist(tenant, as_of=AS_OF, session=session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        replay = owner.collect_and_persist(tenant, as_of=AS_OF, session=session)
        session.commit_transaction()
    assert first == replay
    assert first.recurring_revenue is not None
    assert first.recurring_revenue.mrr_minor == 12000
    durable = evidence.find_one({"tenant_id": tenant})
    assert durable is not None
    assert durable["recurring_revenue"]["fingerprint"] == first.recurring_revenue.fingerprint
    assert evidence.count_documents({"tenant_id": tenant}) == 1
    assert evidence.count_documents({"tenant_id": "other-tenant"}) == 0


# ARTIFACT: test_billing_intelligence_p6_real_mongo.py
# VERSION: v1.0.0-M12-P6
# AUTHORITY BOUNDARY: Bounded host-backed durability certificate only.
# TENANT POSTURE: Random isolated database and explicit tenant filters.
# FAIL-CLOSED POSTURE: Host or transaction uncertainty is a certificate failure.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
