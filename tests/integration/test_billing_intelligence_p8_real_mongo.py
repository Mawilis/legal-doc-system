"""WILSY OS M12-P8 host-backed recurring-revenue-growth certificate.

TITLE: Canonical Billing Intelligence P8 Real-Mongo Growth Certificate
VERSION: v1.0.0-M12-P8
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify explicit prior-evidence growth durability, strict hydration,
         exact replay, tenant isolation, and caller-owned transactions on the
         certified Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_billing_intelligence_p8_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed P8 certificate; P1 derives evidence,
                            P2 persists and hydrates it, P3 composes it, and
                            the test caller owns transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M12-P8 certifies durable nested growth evidence, exact replay,
           strict corruption rejection, and financial-authority separation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated bounded test database; no secrets,
                             providers, KMS, or external clients.
TENANT BOUNDARY: Every source, lookup, and durable evidence record is keyed by
                 the explicit test tenant.
AUTHORITY BOUNDARY: Billing-intelligence evidence durability only; no payment,
                    execution, settlement, refund, paid-state, or closure truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and
                               settlement truth.
FAIL-CLOSED DECLARATION: Replica-set, transaction, schema, replay, tenant, and
                          corruption drift fail the certificate.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Callable, Iterator
import uuid

from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
import pytest

from tools.eos.saas.billing.billing_intelligence_orchestrator import (
    BillingIntelligenceOrchestrator,
    BillingIntelligenceOrchestratorError,
)
from tools.eos.saas.billing.billing_intelligence_registry import (
    BillingIntelligenceRegistry,
    BillingIntelligenceRegistryError,
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
TENANT = "tenant-m12-p8-real"
OTHER_TENANT = "tenant-m12-p8-other"
PRIOR_AS_OF = datetime(2026, 9, 11, 12, tzinfo=timezone.utc)
CURRENT_AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


def _subscription_document(tenant: str, amount: float) -> dict[str, Any]:
    """Create one strict subscription-registry document for the bounded DB."""
    value = SubscriptionEntity(
        tenant_id=tenant,
        plan_id="plan-p8-real",
        plan=PlanTiers.PROFESSIONAL,
        amount=amount,
        currency="ZAR",
        billing_frequency=BillingFrequency.MONTHLY,
        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        current_period_start=datetime(2026, 9, 1, tzinfo=timezone.utc),
        current_period_end=datetime(2026, 10, 1, tzinfo=timezone.utc),
        idempotency_key=f"{tenant}-subscription",
        subscription_id=f"{tenant}-subscription",
        status=SubscriptionStatus.ACTIVE,
        plan_catalogue_version=1,
    )
    material = _create_material(tenant, {"idempotencyKey": value.idempotency_key})
    return value.to_dict() | {
        "_registry_schema": "WILSY-SUBSCRIPTION-REGISTRY/V1",
        "_registry_create_material": material,
        "_registry_create_fingerprint": _fingerprint_create_material(material),
        "_registry_revision": 1,
    }


def _orchestrator(database: Any) -> tuple[BillingIntelligenceOrchestrator, dict[str, Any]]:
    """Build the P8 composition from explicit majority read/write collections."""
    options = {
        "write_concern": WriteConcern(w="majority", j=True),
        "read_concern": ReadConcern("majority"),
    }
    collections = {
        name: database.get_collection(name, **options)
        for name in (
            "commercial_receivables",
            "commercial_receivable_aging",
            "commercial_receivable_dunning",
            "billing_intelligence_evidence",
            "subscriptions",
        )
    }
    return (
        BillingIntelligenceOrchestrator(
            receivable_collection=collections["commercial_receivables"],
            aging_collection=collections["commercial_receivable_aging"],
            dunning_collection=collections["commercial_receivable_dunning"],
            evidence_collection=collections["billing_intelligence_evidence"],
            subscription_collection=collections["subscriptions"],
        ),
        collections,
    )


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any]]:
    """Yield a writable certified replica-set client and one isolated database."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database: Any = None
    try:
        hello = client.admin.command("hello")
    except Exception as error:
        client.close()
        pytest.fail(f"M12P8_MONGO_UNAVAILABLE:{type(error).__name__}")
    if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary"):
        client.close()
        pytest.fail("M12P8_CERTIFIED_REPLICA_SET_REQUIRED")
    if hello.get("logicalSessionTimeoutMinutes") is None:
        client.close()
        pytest.fail("M12P8_TRANSACTIONS_REQUIRED")
    database = client[f"m12p8_billing_{uuid.uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


def test_growth_durability_replay_tenant_isolation_and_corruption(
    mongo_context: tuple[MongoClient, Any],
) -> None:
    """Certify the complete P8 durable growth contract on real Mongo."""
    client, database = mongo_context
    owner, collections = _orchestrator(database)
    evidence = collections["billing_intelligence_evidence"]
    subscriptions = collections["subscriptions"]
    BillingIntelligenceRegistry.ensure_indexes(evidence)

    subscriptions.insert_one(_subscription_document(TENANT, 100.0))
    with client.start_session() as session:
        session.start_transaction()
        prior = owner.collect_and_persist(TENANT, as_of=PRIOR_AS_OF, session=session)
        assert session.in_transaction
        session.commit_transaction()
    assert prior.recurring_revenue is not None
    prior_identity = owner.response_payload(prior)["evidence_identity"]
    assert isinstance(prior_identity, str) and len(prior_identity) == 128
    assert evidence.count_documents({"tenant_id": TENANT}) == 1

    subscriptions.delete_many({"tenant_id": TENANT})
    subscriptions.insert_one(_subscription_document(TENANT, 125.0))
    with client.start_session() as session:
        session.start_transaction()
        current = owner.collect_and_persist(
            TENANT,
            as_of=CURRENT_AS_OF,
            session=session,
            prior_evidence_identity=prior_identity,
        )
        assert session.in_transaction
        session.commit_transaction()

    assert current.recurring_revenue is not None
    growth = current.recurring_revenue_growth
    assert growth is not None
    assert growth.prior_source_fingerprint == prior.recurring_revenue.fingerprint
    assert growth.current_source_fingerprint == current.recurring_revenue.fingerprint
    assert growth.prior_mrr_minor == 10000
    assert growth.current_mrr_minor == 12500
    assert growth.delta_mrr_minor == 2500
    assert growth.growth_numerator == 2500
    assert growth.growth_denominator == 10000
    assert growth.classification.value == "POSITIVE"

    current_identity = owner.response_payload(current)["evidence_identity"]
    assert isinstance(current_identity, str) and len(current_identity) == 128
    hydrated = BillingIntelligenceRegistry.get(TENANT, current_identity, evidence)
    assert hydrated == current
    assert hydrated.recurring_revenue_growth == growth
    assert evidence.count_documents({"tenant_id": TENANT}) == 2

    before_replay_count = evidence.count_documents({"tenant_id": TENANT})
    with client.start_session() as session:
        session.start_transaction()
        replay = owner.collect_and_persist(
            TENANT,
            as_of=CURRENT_AS_OF,
            session=session,
            prior_evidence_identity=prior_identity,
        )
        assert session.in_transaction
        session.commit_transaction()
    assert replay == current
    assert evidence.count_documents({"tenant_id": TENANT}) == before_replay_count

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(BillingIntelligenceOrchestratorError, match="NOT_FOUND"):
            owner.collect_and_persist(
                OTHER_TENANT,
                as_of=CURRENT_AS_OF,
                session=session,
                prior_evidence_identity=prior_identity,
            )
        assert session.in_transaction
        session.abort_transaction()
    assert evidence.count_documents({"tenant_id": OTHER_TENANT}) == 0

    stored = evidence.find_one({"tenant_id": TENANT, "evidence_identity": current_identity})
    assert stored is not None

    def assert_corruption(mutator: Callable[[dict[str, Any]], None]) -> None:
        corrupted = deepcopy(stored)
        growth_document = corrupted["recurring_revenue_growth"]
        assert isinstance(growth_document, dict)
        mutator(growth_document)
        evidence.replace_one({"_id": stored["_id"]}, corrupted)
        with pytest.raises(BillingIntelligenceRegistryError):
            BillingIntelligenceRegistry.get(TENANT, current_identity, evidence)
        evidence.replace_one({"_id": stored["_id"]}, stored)

    assert_corruption(lambda value: value.__setitem__("fingerprint", "0" * 128))
    assert_corruption(lambda value: value.__setitem__("prior_source_fingerprint", "0" * 128))
    assert_corruption(lambda value: value.__setitem__("current_source_fingerprint", "0" * 128))
    assert_corruption(lambda value: value.__setitem__("growth_numerator", 1))
    assert_corruption(lambda value: value.__setitem__("growth_denominator", 1))
    assert_corruption(lambda value: value.__setitem__("classification", "NO_CHANGE"))

    restored = BillingIntelligenceRegistry.get(TENANT, current_identity, evidence)
    assert restored == current
    forbidden_authority_fields = {
        "execution_state",
        "settlement_state",
        "payment_state",
        "paid_state",
        "refund_state",
        "receivable_closure",
        "commercial_receivable_closure",
    }
    assert forbidden_authority_fields.isdisjoint(stored)
    assert "growth_rate" in stored["unsupported_outputs"]
    assert "arpu" in stored["unsupported_outputs"]
    assert evidence.count_documents({"tenant_id": TENANT}) == 2


# ARTIFACT: test_billing_intelligence_p8_real_mongo.py
# VERSION: v1.0.0-M12-P8
# AUTHORITY BOUNDARY: Host-backed P8 evidence durability certificate only.
# TENANT POSTURE: UUID-isolated database and explicit tenant-scoped lookups.
# FAIL-CLOSED POSTURE: Replica, transaction, replay, and corruption drift reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
