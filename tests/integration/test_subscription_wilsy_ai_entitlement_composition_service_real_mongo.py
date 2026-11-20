"""Real-Mongo certificate for D57B WILSY AI entitlement composition.

TITLE: Subscription-Backed WILSY AI Composition Real-Mongo Certificate
VERSION: v1.2.1-CANONICAL-REGISTRY-READBACK-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Physically prove subscription-backed tier derivation, durable P4
         persistence, transaction rollback, replay and tenant isolation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_subscription_wilsy_ai_entitlement_composition_service_real_mongo.py
COLLABORATION / OWNERSHIP: Uses actual PlanRegistry, SubscriptionRegistry and
                            P4 registry in a disposable sanctioned replica set.
CERTIFICATION / UPDATE DATE: 2026-10-10
CHANGELOG: v1.2.1-CANONICAL-REGISTRY-READBACK-CERT reads staged plan
           and subscription state through canonical registry accessors.
           v1.2.0-AUTHENTICATED-STAGED-FOUNDER-ISSUANCE-CERT certifies
           the complete authenticated-orchestrator plan/upgrade/P4 state chain,
           source zero rating, ACTIVE readback, and idempotent exact replay
           against a disposable Mongo replica; Founder identifiers are
           rebound to synthetic objects inside the isolated test only.
           v1.1.0-STAGED-AI-COMMERCIAL-REAL-MONGO-CERT proves a zero-priced
           canonical plan's amended AI feature propagates via audited
           same-plan subscription snapshot upgrade and D57B/P4 activation.
           v1.0.0-D57B-SUBSCRIPTION-WILSY-AI-COMPOSITION-REAL-MONGO-CERT
           establishes physical commit/hydration, all tiers, zero-write denial,
           tenant isolation, abort, exact replay and divergent replay evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic local data only.
TENANT BOUNDARY: Every composition executes in exact tenant scope and one
                 caller-owned Mongo transaction.
AUTHORITY BOUNDARY: Operational certificate only; no external authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Infrastructure absence skips only before fixture yield;
                         every post-yield invariant failure fails certification.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as subscription_registry_module
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing import (
    founder_ai_authenticated_activation as founder_activation,
    founder_ai_entitlement_reconciliation as founder_reconciliation,
)
from tools.eos.saas.billing.subscription_term_policy import SubscriptionTermKind
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.billing import (
    subscription_wilsy_ai_entitlement_composition_service as service,
)
from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_provisioning import MODULE_ID
from tools.eos.saas.billing.wilsy_ai_entitlement_provisioning import (
    activate_wilsy_ai_reasoning_entitlement,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlementState
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    COLLECTION as ENTITLEMENT_COLLECTION,
    WilsyAIEntitlementNotFoundError,
    WilsyAIEntitlementRegistry,
    ensure_indexes,
)


VERSION = "v1.2.1-CANONICAL-REGISTRY-READBACK-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any, Any]]:
    """Yield isolated majority-concern Plan, Subscription and P4 collections."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    original_plans = plan_registry_module.plans_collection
    original_subscriptions = subscription_registry_module.subscriptions_collection
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable before fixture yield: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip("wrong local replica set")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("local replica set has no writable primary")
        database = client[f"wilsy_d57b_composition_{uuid.uuid4().hex}"]
        plans = database.get_collection(
            "plans",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        subscriptions = database.get_collection(
            "subscriptions",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        entitlements = database.get_collection(
            ENTITLEMENT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        plan_registry_module.plans_collection = plans
        subscription_registry_module.subscriptions_collection = subscriptions
        PlanRegistry.provision_indexes()
        subscription_registry_module._ensure_indexes()
        ensure_indexes(entitlements)
        yield client, plans, subscriptions, entitlements, database
    finally:
        plan_registry_module.plans_collection = original_plans
        subscription_registry_module.subscriptions_collection = original_subscriptions
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _plan(features: tuple[str, ...], key: str) -> str:
    """Persist one canonical plan carrying an exact immutable feature set."""
    result = PlanRegistry.create(
        {
            "name": f"D57B {key}",
            "price": 100.0,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "PROFESSIONAL",
            "idempotencyKey": f"plan-{key}",
            "active": True,
            "features": list(features),
            "metadata": {"certificate": True},
            "tags": ["d57b-cert"],
            "user": "D57B-CERT",
        }
    )
    assert result["success"] is True
    return result["plan"].plan_id


def _subscription(tenant: str, features: tuple[str, ...], key: str) -> str:
    """Persist one actual canonical ACTIVE SubscriptionRegistry entity."""
    plan_id = _plan(features, key)
    result = SubscriptionRegistry.create(
        {
            "tenantId": tenant,
            "planId": plan_id,
            "startDate": "2026-10-10T10:00:00+00:00",
            "idempotencyKey": f"subscription-{key}",
            "billingMode": "PLATFORM",
            "onboardingRef": f"ONBOARD-{key}",
            "metadata": {"certificate": True},
        },
        tenant_id_header=tenant,
    )
    assert result["success"] is True
    return result["subscription"].subscription_id


def _compose(
    client: MongoClient[Any],
    tenant: str,
    subscriptions: Any,
    entitlements: Any,
    *,
    key: str = "compose-key",
) -> service.SubscriptionWilsyAIEntitlementCompositionResult:
    """Commit one D57B composition in a caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return service.compose_subscription_wilsy_ai_entitlement(
                tenant_id=tenant,
                idempotency_key=key,
                subscription_collection=subscriptions,
                entitlement_collection=entitlements,
                session=session,
            )



def test_real_zero_rated_source_plan_upgrade_and_p4_ai_activation(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Certify each commercial stage without touching the live Founder DB.

    This UUID-isolated zero-rated tenant uses the canonical registry lifecycle.
    Provider execution and actual Founder subscription state are not claimed.
    """
    client, _plans, subscriptions, entitlements, _db = mongo_context
    tenant = f"tenant-zero-rated-{uuid.uuid4().hex}"
    unique = uuid.uuid4().hex
    branding = "wilsy.vas.tenant_branding.enterprise.v1"
    feature = "ai.wilsy.institutional"
    created = PlanRegistry.create({
        "name": f"Zero-rated staged AI {unique}",
        "price": 0,
        "currency": "ZAR",
        "billingFrequency": "annual",
        "planType": "FOUNDER_ENTERPRISE",
        "idempotencyKey": f"zero-rated-plan-{unique}",
        "active": True,
        "features": [branding],
        "user": "D57B-REAL-MONGO-CERT",
    }, tenant_id=tenant)
    assert created["success"] is True, created
    plan_id = created["plan"].plan_id
    registered = SubscriptionRegistry.create({
        "tenantId": tenant,
        "planId": plan_id,
        "startDate": "2026-11-20T08:00:00+00:00",
        "idempotencyKey": f"zero-rated-sub-{unique}",
        "billingMode": "PLATFORM",
    }, tenant_id_header=tenant)
    assert registered["success"] is True, registered
    original = registered["subscription"]
    assert original.amount == 0
    assert feature not in original.plan_features

    evolved = PlanRegistry.update(
        plan_id, {"features": [branding, feature], "user": "D57B-REAL-MONGO-CERT"},
        tenant_id=tenant, exact_tenant=True,
    )
    assert evolved["success"] is True, evolved
    changed = SubscriptionRegistry.upgrade(
        original.subscription_id, tenant,
        {"newPlanId": plan_id}, collection=subscriptions,
    )
    assert changed["success"] is True, changed
    subscription = changed["subscription"]
    assert subscription.amount == 0
    assert tuple(subscription.plan_features) == tuple(evolved["plan"].features)
    assert subscription.plan_catalogue_version == evolved["plan"].catalogue_version

    with client.start_session() as session:
        with session.start_transaction():
            issued = service.compose_subscription_wilsy_ai_entitlement(
                tenant_id=tenant, idempotency_key=f"zero-rated-issue-{unique}",
                subscription_collection=subscriptions,
                entitlement_collection=entitlements, session=session,
            )
            assert issued.tier is WilsyAITier.INSTITUTIONAL
            assert issued.entitlement.lifecycle_state is WilsyAIEntitlementState.PENDING_SOURCE
            activated = activate_wilsy_ai_reasoning_entitlement(
                registry=WilsyAIEntitlementRegistry(entitlements),
                entitlement=issued.entitlement,
                activation_evidence_reference=f"synthetic-cert-{unique}",
                activation_evidence_fingerprint="f" * 128,
                occurred_at=datetime.now(timezone.utc), session=session,
            )
            assert activated.lifecycle_state is WilsyAIEntitlementState.ACTIVE
    with client.start_session() as session:
        hydrated = WilsyAIEntitlementRegistry(entitlements).get_by_module(
            tenant_id=tenant, module_id=MODULE_ID, session=session,
        )
        assert hydrated.lifecycle_state is WilsyAIEntitlementState.ACTIVE
    assert subscriptions.find_one({
        "tenant_id": tenant, "subscription_id": original.subscription_id,
    })["amount"] == 0



def test_real_authenticated_founder_ai_issuance_replay_and_zero_rating(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Actually persist plan, subscription and P4 via one staged orchestrator.

    Rebind immutable Founder ID constants only in a UUID-isolated disposable
    database. No real Founder, Atlas, production or authenticated real-user
    session is used; HTTP dual permission admission has its own unit certificate.
    """
    client, plans, subscriptions, entitlements, database = mongo_context
    tenant = f"founder-cert-{uuid.uuid4().hex}"
    uid = uuid.uuid4().hex
    branding = "wilsy.vas.tenant_branding.enterprise.v1"
    plan_created = PlanRegistry.create(
        {
            "name": f"Founder Institutional stage cert {uid}",
            "price": 0,
            "currency": "ZAR",
            "billingFrequency": "annual",
            "planType": "FOUNDER_ENTERPRISE",
            "idempotencyKey": f"plan-{uid}",
            "active": True,
            "features": [branding],
            "user": "founder-cert-principal",
        }, tenant_id=tenant,
    )
    assert plan_created["success"] is True
    plan_id = plan_created["plan"].plan_id
    subscribed = SubscriptionRegistry.create(
        {
            "tenantId": tenant, "planId": plan_id,
            "startDate": "2026-11-20T08:00:00+00:00",
            "idempotencyKey": f"sub-{uid}",
            "billingMode": "PLATFORM",
        }, tenant_id_header=tenant,
    )
    assert subscribed["success"] is True
    subscription_id = subscribed["subscription"].subscription_id
    assert subscribed["subscription"].amount == 0

    for module in (founder_activation, founder_reconciliation):
        monkeypatch.setattr(module, "FOUNDER_TENANT_ID", tenant)
        monkeypatch.setattr(module, "FOUNDER_PLAN_ID", plan_id)
        monkeypatch.setattr(module, "FOUNDER_SUBSCRIPTION_ID", subscription_id)
    # The platform perpetual-term policy is deliberately bound to the real
    # Founder tuple, not the synthetic UUID test tuple.
    term = lambda *_args, **_kwargs: SimpleNamespace(
        kind=SubscriptionTermKind.PERPETUAL_PLATFORM_OWNER,
    )
    monkeypatch.setattr(founder_activation, "evaluate_subscription_term", term)
    monkeypatch.setattr(founder_reconciliation, "evaluate_subscription_term", term)
    monkeypatch.setattr(founder_activation, "get_client", lambda: client)
    monkeypatch.setattr(founder_activation, "get_database", lambda: database)

    result = founder_activation.activate_authenticated_founder_institutional_ai(
        tenant_id=tenant, principal_id="founder-cert-principal",
        idempotency_key=f"cert-issue-{uid}",
    )
    assert result["entitlement_state"] == "ACTIVE"
    assert result["feature_id"] == "ai.wilsy.institutional"
    assert result["zero_rated_subscription"] is True
    assert result["activated_this_request"] is True

    stored_plan = PlanRegistry.get(
        plan_id, tenant_id=tenant, exact_tenant=True,
    )
    assert stored_plan is not None
    assert "ai.wilsy.institutional" in stored_plan.features
    with client.start_session() as session:
        updated_subscription = SubscriptionRegistry.get(
            subscription_id, tenant, collection=subscriptions, session=session,
        )
        p4 = WilsyAIEntitlementRegistry(entitlements).get_by_module(
            tenant_id=tenant, module_id=MODULE_ID, session=session,
        )
    assert updated_subscription.amount == 0
    assert "ai.wilsy.institutional" in updated_subscription.plan_features
    assert p4.lifecycle_state is WilsyAIEntitlementState.ACTIVE
    assert p4.tier is WilsyAITier.INSTITUTIONAL
    first_id = p4.entitlement_id

    replay = founder_activation.activate_authenticated_founder_institutional_ai(
        tenant_id=tenant, principal_id="founder-cert-principal",
        idempotency_key=f"cert-issue-{uid}",
    )
    assert replay["entitlement_state"] == "ACTIVE"
    assert replay["activated_this_request"] is False
    assert replay["entitlement_id"] == first_id
    assert entitlements.count_documents({"tenant_id": tenant}) == 1



@pytest.mark.parametrize(
    ("feature", "tier"),
    [
        ("ai.wilsy.starter", WilsyAITier.STARTER),
        ("ai.wilsy.growth", WilsyAITier.GROWTH),
        ("ai.wilsy.institutional", WilsyAITier.INSTITUTIONAL),
    ],
)
def test_real_tier_persist_commit_and_fresh_hydration(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
    feature: str,
    tier: WilsyAITier,
) -> None:
    """Each exact feature durably binds its tier, policy and fixed capability."""
    client, _, subscriptions, entitlements, _ = mongo_context
    tenant = f"tenant-{tier.value.casefold()}-{uuid.uuid4().hex}"
    _subscription(tenant, (feature,), uuid.uuid4().hex)
    result = _compose(client, tenant, subscriptions, entitlements)
    assert result.tier is tier and result.entitlement.tier is tier
    assert result.entitlement.module_id == MODULE_ID
    assert result.entitlement.policy_fingerprint == (
        get_wilsy_ai_commercial_policy(tier).policy_fingerprint
    )
    assert result.entitlement.capability_grants == service.CANONICAL_CAPABILITY_GRANTS
    with client.start_session() as session:
        hydrated = WilsyAIEntitlementRegistry(entitlements).get_by_module(
            tenant_id=tenant,
            module_id=MODULE_ID,
            session=session,
        )
    assert hydrated == result.entitlement


@pytest.mark.parametrize(
    "features",
    [
        (),
        ("ai.wilsy",),
        ("ai.wilsy.starter", "ai.wilsy.growth"),
    ],
)
def test_real_absent_generic_and_conflicting_features_write_zero(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
    features: tuple[str, ...],
) -> None:
    """Commercial denial paths physically leave the P4 collection empty."""
    client, _, subscriptions, entitlements, _ = mongo_context
    tenant = f"tenant-denied-{uuid.uuid4().hex}"
    _subscription(tenant, features, uuid.uuid4().hex)
    with pytest.raises(service.SubscriptionWilsyAIEntitlementCompositionCommercialError):
        _compose(client, tenant, subscriptions, entitlements)
    assert entitlements.count_documents({"tenant_id": tenant}) == 0


def test_real_tenant_isolation_and_wrong_scope_absence(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Foreign scope cannot compose, read or infer another tenant entitlement."""
    client, _, subscriptions, entitlements, _ = mongo_context
    tenant = f"tenant-owner-{uuid.uuid4().hex}"
    foreign = f"tenant-foreign-{uuid.uuid4().hex}"
    _subscription(tenant, ("ai.wilsy.starter",), uuid.uuid4().hex)
    result = _compose(client, tenant, subscriptions, entitlements)
    with pytest.raises(service.SubscriptionWilsyAIEntitlementCompositionCommercialError):
        _compose(client, foreign, subscriptions, entitlements)
    with client.start_session() as session:
        with pytest.raises(WilsyAIEntitlementNotFoundError):
            WilsyAIEntitlementRegistry(entitlements).get(
                tenant_id=foreign,
                entitlement_id=result.entitlement.entitlement_id,
                session=session,
            )
    assert entitlements.count_documents({"tenant_id": foreign}) == 0


def test_real_aborted_transaction_leaves_zero_durable_entitlement(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Caller abort removes the provisional P4 insert while subscription survives."""
    client, _, subscriptions, entitlements, _ = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    _subscription(tenant, ("ai.wilsy.starter",), uuid.uuid4().hex)
    with client.start_session() as session:
        session.start_transaction()
        service.compose_subscription_wilsy_ai_entitlement(
            tenant_id=tenant,
            idempotency_key="abort-key",
            subscription_collection=subscriptions,
            entitlement_collection=entitlements,
            session=session,
        )
        assert entitlements.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()
    assert entitlements.count_documents({"tenant_id": tenant}) == 0
    assert subscriptions.count_documents({"tenant_id": tenant}) == 1


def test_real_exact_replay_is_one_document_and_commercial_state_unchanged(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Exact replay hydrates one document without mutating plan/subscription truth."""
    client, plans, subscriptions, entitlements, _ = mongo_context
    tenant = f"tenant-replay-{uuid.uuid4().hex}"
    _subscription(tenant, ("ai.wilsy.growth",), uuid.uuid4().hex)
    plans_before = deepcopy(list(plans.find({})))
    subscriptions_before = deepcopy(list(subscriptions.find({"tenant_id": tenant})))
    first = _compose(client, tenant, subscriptions, entitlements)
    second = _compose(client, tenant, subscriptions, entitlements)
    assert first.entitlement == second.entitlement
    assert first.exact_replay is False and second.exact_replay is True
    assert entitlements.count_documents({"tenant_id": tenant}) == 1
    assert list(plans.find({})) == plans_before
    assert list(subscriptions.find({"tenant_id": tenant})) == subscriptions_before


def test_real_divergent_replay_fails_and_unrelated_collections_remain_empty(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any],
) -> None:
    """Changed canonical subscription proof cannot reuse an earlier command key."""
    client, _, subscriptions, entitlements, database = mongo_context
    tenant = f"tenant-divergent-{uuid.uuid4().hex}"
    subscription_id = _subscription(
        tenant,
        ("ai.wilsy.institutional",),
        uuid.uuid4().hex,
    )
    _compose(client, tenant, subscriptions, entitlements, key="fixed-key")
    updated = SubscriptionRegistry.update(
        subscription_id,
        {"metadata": {"certificate": True, "revision": 2}, "user": "D57B-CERT"},
        tenant_id_header=tenant,
    )
    assert updated["success"] is True
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionDivergentReplayError
    ):
        _compose(client, tenant, subscriptions, entitlements, key="fixed-key")
    assert entitlements.count_documents({"tenant_id": tenant}) == 1
    for collection_name in (
        "payments",
        "invoices",
        "settlements",
        "financial_executions",
    ):
        assert database[collection_name].count_documents({}) == 0


# ARTIFACT: test_subscription_wilsy_ai_entitlement_composition_service_real_mongo.py
# VERSION: v1.2.1-CANONICAL-REGISTRY-READBACK-CERT
# AUTHORITY BOUNDARY: real-Mongo D57B composition evidence only; no external authority
# TENANT POSTURE: UUID-isolated exact-tenant subscription and entitlement operations
# FAIL-CLOSED POSTURE: absent/generic/conflicting feature, foreign scope, rollback and divergent replay persist no false success
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
