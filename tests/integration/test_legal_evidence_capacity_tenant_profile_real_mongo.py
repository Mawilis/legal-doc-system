"""Actual-Mongo certificate for tenant Legal Evidence capacity-profile resolution.

TITLE: Tenant Legal Evidence Capacity Profile Actual-Mongo Certificate
VERSION: v1.0.0-L10A2Q-P2-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Prove the durable composition chain:

        PlanRegistry persisted plan
        -> SubscriptionRegistry persisted ACTIVE subscription
        -> canonical SubscriptionEntity hydration/integrity
        -> ACTIVE LEGAL_OPERATIONS entitlement evidence
        -> immutable tenant Legal Evidence capacity-profile evidence

CERTIFICATION / UPDATE DATE: 2026-09-29

MONGO POSTURE:
    Uses TEST_VENDOR_MONGO_URI when supplied, otherwise only the certified
    loopback replica set at 127.0.0.1:27027 / wilsyVendorCertRS.
    Uses one UUID-isolated certification database and drops it deterministically.

TENANT POSTURE:
    Exact tenant scope is mandatory. Cross-tenant subscription reads appear
    absent and cross-tenant composition rejects.

AUTHORITY BOUNDARY:
    Certification only. No production tenant mutation, entitlement persistence,
    IAM, storage admission, billing, payment, settlement or financial execution.

FAIL-CLOSED POSTURE:
    Environment/topology failure is certificate failure; no skip.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
import os
import uuid
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as subscription_registry_module
from tools.eos.saas.billing.legal_evidence_capacity_profile_resolver import (
    CAPACITY_FEATURE_STARTER,
)
from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityProfile,
)
from tools.eos.saas.billing.legal_evidence_capacity_tenant_profile_resolver import (
    LegalEvidenceCapacityTenantProfileError,
    derive_legal_evidence_capacity_tenant_profile,
)
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.subscription import SubscriptionStatus
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId


TEST_VERSION = "v1.0.0-L10A2Q-P2-REAL-MONGO-CERT"
CERT_URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_CERT_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
TEST_MONGO_URI = os.getenv(CERT_URI_ENV, DEFAULT_CERT_URI)

STAMP = datetime(2026, 9, 29, 20, 30, tzinfo=timezone.utc)
TENANT = "tenant-l10a2q-p2-real-mongo"
OTHER_TENANT = "tenant-l10a2q-p2-neighbor"


class _MongoContext:
    """Hold one UUID-isolated actual-Mongo certification database."""

    def __init__(
        self,
        *,
        client: MongoClient[Any],
        plans: Collection[dict[str, Any]],
        subscriptions: Collection[dict[str, Any]],
        database_name: str,
    ) -> None:
        self.client = client
        self.plans = plans
        self.subscriptions = subscriptions
        self.database_name = database_name


@pytest.fixture(scope="module")
def mongo_context() -> Iterator[_MongoContext]:
    """Bind canonical registries to one isolated actual-Mongo database."""
    client: MongoClient[Any] = MongoClient(
        TEST_MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    # Deliberately no skip: environment failure is certificate failure.
    client.admin.command("ping")
    hello = client.admin.command("hello")

    if hello.get("setName") != EXPECTED_REPLICA_SET:
        raise RuntimeError("L10A2Q_P2_CERT_WRONG_MONGO_TOPOLOGY")

    if hello.get("isWritablePrimary") is not True:
        raise RuntimeError("L10A2Q_P2_CERT_MONGO_NOT_PRIMARY")

    database_name = "wilsy_l10a2q_p2_" + uuid.uuid4().hex
    database = client[database_name]

    plans: Collection[dict[str, Any]] = database.get_collection(
        "plans",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    subscriptions: Collection[dict[str, Any]] = database.get_collection(
        "subscriptions",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )

    original_plans = plan_registry_module.plans_collection
    original_subscriptions = (
        subscription_registry_module.subscriptions_collection
    )

    plan_registry_module.plans_collection = plans
    subscription_registry_module.subscriptions_collection = subscriptions

    try:
        PlanRegistry._ensure_indexes()
        yield _MongoContext(
            client=client,
            plans=plans,
            subscriptions=subscriptions,
            database_name=database_name,
        )
    finally:
        plan_registry_module.plans_collection = original_plans
        subscription_registry_module.subscriptions_collection = (
            original_subscriptions
        )

        client.drop_database(database_name)

        assert database_name not in client.list_database_names()
        client.close()


def _create_catalogue_plan(
    *,
    name: str,
    price: float,
    idempotency_key: str,
) -> str:
    """Persist one canonical global plan with explicit Legal Evidence binding."""
    result = PlanRegistry.create(
        {
            "name": name,
            "price": price,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "PROFESSIONAL",
            "idempotencyKey": idempotency_key,
            "active": True,
            "features": [
                "legal.documents",
                CAPACITY_FEATURE_STARTER,
            ],
            "metadata": {
                "certificate": True,
                "capacityAuthority": "explicit-plan-feature",
            },
            "tags": [
                "l10a2q-p2-real-mongo-cert",
            ],
            "user": "L10A2Q-P2-REAL-MONGO-CERT",
        }
    )

    assert result["success"] is True
    return result["plan"].plan_id


def _create_subscription(
    *,
    tenant_id: str,
    plan_id: str,
    idempotency_key: str,
) -> str:
    """Persist one subscription selecting canonical PlanRegistry identity."""
    result = SubscriptionRegistry.create(
        {
            "tenantId": tenant_id,
            "planId": plan_id,
            "startDate": "2026-09-29T20:30:00+00:00",
            "idempotencyKey": idempotency_key,
            "billingMode": "PLATFORM",
            "onboardingRef": f"ONBOARD-{tenant_id}",
            "sector": "LEGAL",
            "region": "ZA",
            "metadata": {
                "certificate": True,
            },
        },
        tenant_id_header=tenant_id,
    )

    assert result["success"] is True
    return result["subscription"].subscription_id


def _active_legal_entitlement(tenant_id: str):
    """Create domain-valid ACTIVE Legal Operations entitlement evidence."""
    pending = create_tenant_product_entitlement(
        tenant_id=tenant_id,
        entitlement_id=f"ent-legal-{tenant_id}",
        product_id=TenantProductId.LEGAL_OPERATIONS,
        source_evidence_reference="real-mongo-subscription-source",
        source_evidence_fingerprint="c" * 128,
    )

    return pending.transition(
        TenantProductEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="legal-operations-activation",
        evidence_fingerprint="d" * 128,
        occurred_at=STAMP,
    )


def test_actual_mongo_plan_subscription_entitlement_profile_chain(
    mongo_context: _MongoContext,
) -> None:
    """Prove the complete persisted-plan -> persisted-subscription -> P2 chain."""
    plan_id = _create_catalogue_plan(
        name="Untrusted Display Name Has No Capacity Authority",
        price=12345.67,
        idempotency_key="l10a2q-p2-plan-main",
    )

    subscription_id = _create_subscription(
        tenant_id=TENANT,
        plan_id=plan_id,
        idempotency_key="l10a2q-p2-sub-main",
    )

    loaded_plan = PlanRegistry.get(
        plan_id,
        tenant_id=None,
    )
    assert loaded_plan is not None
    assert loaded_plan.plan_id == plan_id
    assert CAPACITY_FEATURE_STARTER in loaded_plan.features

    loaded_subscription = SubscriptionRegistry.get(
        subscription_id,
        tenant_id_header=TENANT,
    )

    assert loaded_subscription is not None
    assert loaded_subscription.tenant_id == TENANT
    assert loaded_subscription.plan_id == plan_id
    assert loaded_subscription.status is SubscriptionStatus.ACTIVE
    assert loaded_subscription.plan_catalogue_version is not None
    assert CAPACITY_FEATURE_STARTER in loaded_subscription.plan_features

    entitlement = _active_legal_entitlement(TENANT)

    result = derive_legal_evidence_capacity_tenant_profile(
        tenant_id=TENANT,
        subscription=loaded_subscription,
        entitlement=entitlement,
        evaluated_at=STAMP,
    )

    assert result.tenant_id == TENANT
    assert result.subscription_id == subscription_id
    assert result.plan_id == plan_id
    assert (
        result.plan_catalogue_version
        == loaded_subscription.plan_catalogue_version
    )
    assert result.subscription_proof_hash == loaded_subscription.proof_hash
    assert result.entitlement_id == entitlement.entitlement_id
    assert result.entitlement_revision == 1
    assert result.entitlement_fingerprint == entitlement.fingerprint
    assert result.product_id is TenantProductId.LEGAL_OPERATIONS
    assert result.profile is LegalEvidenceCapacityProfile.STARTER
    assert len(result.fingerprint) == 128
    int(result.fingerprint, 16)

    # The deliberately arbitrary display name and price are not projected.
    evidence = result.to_dict()
    assert "price" not in evidence
    assert "amount" not in evidence
    assert "currency" not in evidence
    assert "plan_name" not in evidence


def test_actual_mongo_cross_tenant_subscription_read_is_absent(
    mongo_context: _MongoContext,
) -> None:
    """Prove tenant-scoped registry read does not disclose neighbor subscription."""
    plan_id = _create_catalogue_plan(
        name="Cross Tenant Certificate",
        price=1.0,
        idempotency_key="l10a2q-p2-plan-cross-tenant",
    )
    subscription_id = _create_subscription(
        tenant_id=TENANT,
        plan_id=plan_id,
        idempotency_key="l10a2q-p2-sub-cross-tenant",
    )

    assert (
        SubscriptionRegistry.get(
            subscription_id,
            tenant_id_header=OTHER_TENANT,
        )
        is None
    )


def test_actual_mongo_cross_tenant_entitlement_composition_rejects(
    mongo_context: _MongoContext,
) -> None:
    """Prove entitlement evidence from a neighbor cannot compose for tenant."""
    plan_id = _create_catalogue_plan(
        name="Entitlement Isolation Certificate",
        price=777.0,
        idempotency_key="l10a2q-p2-plan-entitlement-isolation",
    )
    subscription_id = _create_subscription(
        tenant_id=TENANT,
        plan_id=plan_id,
        idempotency_key="l10a2q-p2-sub-entitlement-isolation",
    )

    subscription = SubscriptionRegistry.get(
        subscription_id,
        tenant_id_header=TENANT,
    )
    assert subscription is not None

    neighbor_entitlement = _active_legal_entitlement(OTHER_TENANT)

    with pytest.raises(
        LegalEvidenceCapacityTenantProfileError,
        match="L10A2Q_P2_ENTITLEMENT_TENANT_MISMATCH",
    ):
        derive_legal_evidence_capacity_tenant_profile(
            tenant_id=TENANT,
            subscription=subscription,
            entitlement=neighbor_entitlement,
            evaluated_at=STAMP,
        )


def test_actual_mongo_plan_without_explicit_capacity_binding_rejects(
    mongo_context: _MongoContext,
) -> None:
    """Prove plan price/name/tier alone never infer a non-Founder profile."""
    result = PlanRegistry.create(
        {
            "name": "Starter",
            "price": 499.0,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "PROFESSIONAL",
            "idempotencyKey": "l10a2q-p2-plan-no-binding",
            "active": True,
            "features": [
                "legal.documents",
            ],
            "metadata": {
                "certificate": True,
            },
            "tags": [
                "l10a2q-p2-real-mongo-cert",
            ],
            "user": "L10A2Q-P2-REAL-MONGO-CERT",
        }
    )
    assert result["success"] is True
    plan_id = result["plan"].plan_id

    subscription_id = _create_subscription(
        tenant_id=TENANT,
        plan_id=plan_id,
        idempotency_key="l10a2q-p2-sub-no-binding",
    )

    subscription = SubscriptionRegistry.get(
        subscription_id,
        tenant_id_header=TENANT,
    )
    assert subscription is not None

    with pytest.raises(
        LegalEvidenceCapacityTenantProfileError,
        match="L10A2Q_P2_PROFILE_BINDING_REQUIRED",
    ):
        derive_legal_evidence_capacity_tenant_profile(
            tenant_id=TENANT,
            subscription=subscription,
            entitlement=_active_legal_entitlement(TENANT),
            evaluated_at=STAMP,
        )


# ARTIFACT: test_legal_evidence_capacity_tenant_profile_real_mongo.py
# VERSION: v1.0.0-L10A2Q-P2-REAL-MONGO-CERT
# MONGO POSTURE: actual loopback replica-set Mongo; UUID-isolated database
# TENANT POSTURE: exact tenant reads/composition; cross-tenant absence/rejection
# AUTHORITY BOUNDARY: certification only; no runtime admission/financial authority
# CLEANUP POSTURE: certification database dropped deterministically
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
