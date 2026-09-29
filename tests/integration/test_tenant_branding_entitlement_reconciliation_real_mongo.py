"""WILSY OS D21C2 tenant-branding entitlement reconciliation real-Mongo certificate.

TITLE: Tenant Branding Entitlement Reconciliation Real-Mongo Certificate
VERSION: v1.0.0-L10-P2C5-D21C2-RECONCILIATION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exercise the published source-bound D21C2 currentness service against
         canonical PlanRegistry, SubscriptionRegistry and D21B2B persistence
         on a UUID-isolated replica-set database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_branding_entitlement_reconciliation_real_mongo.py
COLLABORATION / OWNERSHIP: PlanRegistry and SubscriptionRegistry own commercial
                            truth; D21C1 owns entitlement composition; D21C2
                            owns currentness reconciliation; D21B2B owns
                            immutable lifecycle persistence; this file owns
                            disposable real-Mongo certification only.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: v1.0.0 certifies topology, source-bound currentness, commercial-loss
           transitions, replacement lineage closure, CAS/replay, rollback,
           strict corruption rejection and authority boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic UUID tenants and disposable Mongo only;
                             no credentials, provider secrets or production data.
TENANT BOUNDARY: Every subscription and entitlement read/write is tenant-scoped.
AUTHORITY BOUNDARY: D21C2 currentness and D21B2 lifecycle only; no IAM,
                    profile, asset, browser, HTTP, UI or Kennel authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution or settlement truth.
TRANSACTION BOUNDARY: The certificate owns sessions and commit/abort; production
                      services receive and propagate the caller session.
FAIL-CLOSED DECLARATION: Mongo outage, corruption, ambiguity, stale CAS and
                          divergent replay fail or are reported as unavailable.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import json
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
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.billing.tenant_branding_entitlement_reconciliation import (
    TenantBrandingEntitlementReconciliationError,
    TenantBrandingEntitlementReconciliationOutcome,
    TenantBrandingEntitlementReconciliationService,
)
from tools.eos.saas.billing.tenant_branding_entitlement_registry import (
    TenantBrandingEntitlementRegistryConflictError,
    TenantBrandingEntitlementRegistryNotFoundError,
    TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
    TenantBrandingEntitlementRegistry as EntitlementRegistry,
)
from tools.eos.saas.billing.tenant_branding_subscription_entitlement_composer import (
    TenantBrandingSubscriptionEntitlementComposer,
)
from tools.eos.saas.billing.tenant_branding_vas_catalogue import (
    BRANDING_VAS_ENTERPRISE_ID,
    BRANDING_VAS_INSTITUTIONAL_ID,
    BRANDING_VAS_PROFESSIONAL_ID,
)
from tools.eos.saas.domain.subscription import SubscriptionStatus
from tools.eos.saas.domain.tenant_branding_commercial_eligibility import (
    derive_tenant_branding_commercial_eligibility,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlementState,
)


VERSION = "v1.0.0-L10-P2C5-D21C2-RECONCILIATION-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class _MongoContext:
    client: MongoClient[Any]
    database: Any
    plans: Any
    subscriptions: Any
    history: Any
    current: Any
    database_name: str


def _database_uri(uri: str, database_name: str) -> str:
    base, separator, query = uri.partition("?")
    prefix = base.rsplit("/", 1)[0]
    result = f"{prefix}/{database_name}"
    return f"{result}?{query}" if separator else result


def _plan_ids() -> dict[str, str]:
    return {
        "PROFESSIONAL": "WILSYPLAN-P2C5-PROFESSIONAL",
        "INSTITUTIONAL": "WILSYPLAN-P2C5-INSTITUTIONAL",
        "ENTERPRISE": "WILSYPLAN-P2C5-ENTERPRISE",
    }


def _seed_plans() -> None:
    features = {
        "PROFESSIONAL": BRANDING_VAS_PROFESSIONAL_ID,
        "INSTITUTIONAL": BRANDING_VAS_INSTITUTIONAL_ID,
        "ENTERPRISE": BRANDING_VAS_ENTERPRISE_ID,
    }
    for tier, plan_id in _plan_ids().items():
        result = PlanRegistry.create(
            {
                "name": f"P2C5 {tier.title()}",
                "price": 101.0,
                "currency": "ZAR",
                "billingFrequency": "monthly",
                "planType": "PROFESSIONAL",
                "idempotencyKey": f"P2C5-PLAN-{tier}",
                "plan_id": plan_id,
                "features": [features[tier]],
                "metadata": {"certificate": True, "vas": "tenant_branding"},
                "tags": ["p2c5-real-mongo"],
                "user": "P2C5-REAL-MONGO-CERT",
            }
        )
        assert result["success"] is True, result


def _subscription(
    tenant_id: str,
    tier: str = "PROFESSIONAL",
    *,
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    subscription_key: str | None = None,
) -> Any:
    result = SubscriptionRegistry.create(
        {
            "tenantId": tenant_id,
            "planId": _plan_ids()[tier],
            "startDate": NOW.isoformat(),
            "idempotencyKey": subscription_key or f"P2C5-SUB-{uuid.uuid4().hex}",
            "status": status.value,
            "billingMode": "PLATFORM",
            "sector": "LEGAL",
            "region": "ZA",
            "metadata": {"certificate": True},
            "tags": ["p2c5-real-mongo"],
        },
        tenant_id_header=tenant_id,
    )
    assert result["success"] is True, result
    return result["subscription"]


def _compose(context: _MongoContext, subscription: Any, entitlement_id: str) -> Any:
    with context.client.start_session() as session:
        session.start_transaction()
        try:
            result = TenantBrandingSubscriptionEntitlementComposer(
                subscription_collection=context.subscriptions,
                history_collection=context.history,
                current_collection=context.current,
            ).compose(
                tenant_id=subscription.tenant_id,
                subscription_id=subscription.subscription_id,
                entitlement_id=entitlement_id,
                evaluated_at=NOW,
                occurred_at=NOW,
                idempotency_key=f"P2C5-COMPOSE-{entitlement_id}",
                session=session,
            )
            session.commit_transaction()
            assert result.entitlement is not None
            return result
        except Exception:
            if session.in_transaction:
                session.abort_transaction()
            raise


def _reconcile(
    context: _MongoContext,
    tenant_id: str,
    entitlement_id: str,
    *,
    evaluated_at: datetime = NOW,
    commit: bool = True,
) -> Any:
    with context.client.start_session() as session:
        session.start_transaction()
        try:
            result = TenantBrandingEntitlementReconciliationService(
                subscription_collection=context.subscriptions,
                history_collection=context.history,
                current_collection=context.current,
            ).reconcile(
                tenant_id=tenant_id,
                entitlement_id=entitlement_id,
                evaluated_at=evaluated_at,
                occurred_at=NOW,
                session=session,
            )
            if commit:
                session.commit_transaction()
            else:
                session.abort_transaction()
            return result
        except Exception:
            if session.in_transaction:
                session.abort_transaction()
            raise


def _set_status(subscription: Any, tenant_id: str, status: SubscriptionStatus) -> Any:
    if status is SubscriptionStatus.PAUSED:
        result = SubscriptionRegistry.pause(subscription.subscription_id, tenant_id_header=tenant_id, pause_reason="P2C5")
    elif status is SubscriptionStatus.CANCELLED:
        result = SubscriptionRegistry.cancel(subscription.subscription_id, tenant_id_header=tenant_id, cancel_reason="P2C5", cancel_at_period_end=False)
    else:
        result = SubscriptionRegistry.update(subscription.subscription_id, {"status": status.value, "user": "P2C5"}, tenant_id_header=tenant_id)
    assert result["success"] is True, result
    return result["subscription"]


@pytest.fixture(scope="module")
def mongo_context() -> Iterator[_MongoContext]:
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
            pytest.skip(f"real Mongo unavailable: {type(error).__name__}: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical sessions")
        database_name = f"wilsy_d21c2_reconciliation_{uuid.uuid4().hex}"
        assert len(database_name.encode("utf-8")) <= 63
        database = client[database_name]
        options = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        plans = database.get_collection("plans", **options)
        subscriptions = database.get_collection("subscriptions", **options)
        history = database.get_collection("tenant_branding_entitlement_history", **options)
        current = database.get_collection("tenant_branding_entitlement_current", **options)
        plan_registry_module.plans_collection = plans
        subscription_registry_module.subscriptions_collection = subscriptions
        PlanRegistry._ensure_indexes()
        subscription_registry_module._ensure_indexes()
        EntitlementRegistry.ensure_indexes(history, current)
        _seed_plans()
        yield _MongoContext(client, database, plans, subscriptions, history, current, database_name)
    finally:
        plan_registry_module.plans_collection = original_plans
        subscription_registry_module.subscriptions_collection = original_subscriptions
        if database is not None:
            client.drop_database(database.name)
        client.close()


@pytest.fixture(autouse=True)
def clean_truth(mongo_context: _MongoContext) -> Iterator[None]:
    mongo_context.subscriptions.delete_many({})
    mongo_context.history.delete_many({})
    mongo_context.current.delete_many({})
    yield
    mongo_context.subscriptions.delete_many({})
    mongo_context.history.delete_many({})
    mongo_context.current.delete_many({})


def test_real_replica_set_disposable_database_and_canonical_isolation(mongo_context: _MongoContext) -> None:
    hello = mongo_context.client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    assert mongo_context.database_name.startswith("wilsy_d21c2_reconciliation_")
    assert mongo_context.database_name != "wilsy"
    assert len(mongo_context.database_name.encode("utf-8")) <= 63
    assert _database_uri(MONGO_URI, mongo_context.database_name).split("/")[-1]
    assert mongo_context.client["wilsy"].name == "wilsy"


def test_active_exact_source_current_noop_and_replay(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-current-{uuid.uuid4().hex}"
    subscription = _subscription(tenant)
    composed = _compose(mongo_context, subscription, "current-ent")
    before = mongo_context.history.count_documents({"tenant_id": tenant})
    first = _reconcile(mongo_context, tenant, "current-ent")
    second = _reconcile(mongo_context, tenant, "current-ent")
    assert first.outcome is second.outcome is TenantBrandingEntitlementReconciliationOutcome.CURRENT
    assert first.entitlement.to_dict() == composed.entitlement.to_dict()
    assert second.entitlement.to_dict() == first.entitlement.to_dict()
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == before


def test_closed_history_does_not_create_false_ambiguity_and_order_is_independent(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-history-{uuid.uuid4().hex}"
    old = _subscription(tenant, subscription_key=f"old-{uuid.uuid4().hex}")
    _set_status(old, tenant, SubscriptionStatus.CANCELLED)
    current = _subscription(tenant, subscription_key=f"current-{uuid.uuid4().hex}")
    _compose(mongo_context, current, "history-ent")
    assert _reconcile(mongo_context, tenant, "history-ent").outcome is TenantBrandingEntitlementReconciliationOutcome.CURRENT
    older = _subscription(tenant, subscription_key=f"older-{uuid.uuid4().hex}")
    _set_status(older, tenant, SubscriptionStatus.EXPIRED)
    result = _reconcile(mongo_context, tenant, "history-ent")
    assert result.outcome is TenantBrandingEntitlementReconciliationOutcome.CURRENT


def test_paused_source_transitions_once_and_replays(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-paused-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    composed = _compose(mongo_context, source, "paused-ent")
    _set_status(source, tenant, SubscriptionStatus.PAUSED)
    first = _reconcile(mongo_context, tenant, "paused-ent")
    second = _reconcile(mongo_context, tenant, "paused-ent")
    assert first.target_state is TenantBrandingEntitlementState.SUSPENDED
    assert second.outcome is TenantBrandingEntitlementReconciliationOutcome.IDEMPOTENT_REPLAY
    assert first.entitlement.lifecycle_revision == composed.entitlement.lifecycle_revision + 1
    assert first.entitlement.suspended_at == NOW
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 3


def test_past_due_source_transitions_to_suspended(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-pastdue-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "pastdue-ent")
    _set_status(source, tenant, SubscriptionStatus.PAST_DUE)
    result = _reconcile(mongo_context, tenant, "pastdue-ent")
    assert result.target_state is TenantBrandingEntitlementState.SUSPENDED


def test_cancelled_source_transitions_to_revoked(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-cancelled-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "cancelled-ent")
    _set_status(source, tenant, SubscriptionStatus.CANCELLED)
    result = _reconcile(mongo_context, tenant, "cancelled-ent")
    assert result.target_state is TenantBrandingEntitlementState.REVOKED
    assert result.entitlement.revoked_at == NOW


def test_expired_source_transitions_directly_to_revoked(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-expired-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "expired-ent")
    _set_status(source, tenant, SubscriptionStatus.EXPIRED)
    result = _reconcile(mongo_context, tenant, "expired-ent")
    assert result.target_state is TenantBrandingEntitlementState.REVOKED


def test_trial_existing_active_fails_closed_without_mutation(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-trial-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "trial-ent")
    _set_status(source, tenant, SubscriptionStatus.TRIAL)
    before = mongo_context.history.count_documents({"tenant_id": tenant})
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="TRIAL_EXISTING_ACTIVE"):
        _reconcile(mongo_context, tenant, "trial-ent")
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == before


def test_cancelled_professional_plus_active_enterprise_revokes_old_lineage(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-replace-enterprise-{uuid.uuid4().hex}"
    professional = _subscription(tenant, subscription_key=f"professional-{uuid.uuid4().hex}")
    composed = _compose(mongo_context, professional, "professional-ent")
    _set_status(professional, tenant, SubscriptionStatus.CANCELLED)
    enterprise = _subscription(tenant, "ENTERPRISE", subscription_key=f"enterprise-{uuid.uuid4().hex}")
    result = _reconcile(mongo_context, tenant, "professional-ent")
    assert result.target_state is TenantBrandingEntitlementState.REVOKED
    assert result.entitlement.branding_tier is composed.entitlement.branding_tier
    assert result.entitlement.source_evidence_reference == composed.entitlement.source_evidence_reference
    assert enterprise.subscription_id != professional.subscription_id
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 3


def test_expired_professional_plus_active_enterprise_revokes_old_lineage(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-replace-expired-{uuid.uuid4().hex}"
    professional = _subscription(tenant)
    _compose(mongo_context, professional, "professional-ent")
    _set_status(professional, tenant, SubscriptionStatus.EXPIRED)
    _subscription(tenant, "ENTERPRISE")
    result = _reconcile(mongo_context, tenant, "professional-ent")
    assert result.target_state is TenantBrandingEntitlementState.REVOKED


def test_same_tier_new_source_revokes_old_lineage(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-replace-same-{uuid.uuid4().hex}"
    old = _subscription(tenant, subscription_key=f"old-{uuid.uuid4().hex}")
    _compose(mongo_context, old, "professional-ent")
    _set_status(old, tenant, SubscriptionStatus.CANCELLED)
    _subscription(tenant, subscription_key=f"new-{uuid.uuid4().hex}")
    result = _reconcile(mongo_context, tenant, "professional-ent")
    assert result.target_state is TenantBrandingEntitlementState.REVOKED


def test_multiple_currently_eligible_subscriptions_fail_closed(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-multiple-{uuid.uuid4().hex}"
    first = _subscription(tenant, subscription_key=f"first-{uuid.uuid4().hex}")
    _compose(mongo_context, first, "multiple-ent")
    _subscription(tenant, "ENTERPRISE", subscription_key=f"second-{uuid.uuid4().hex}")
    before = mongo_context.history.count_documents({"tenant_id": tenant})
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="MULTIPLE_ELIGIBLE"):
        _reconcile(mongo_context, tenant, "multiple-ent")
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == before


def test_source_not_resolved_fails_closed_without_tier_selection(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-source-missing-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "missing-source-ent")
    raw = mongo_context.subscriptions.find_one({"tenant_id": tenant, "subscription_id": source.subscription_id})
    assert isinstance(raw, dict)
    mongo_context.subscriptions.delete_one({"_id": raw["_id"]})
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="SOURCE_SUBSCRIPTION_NOT_RESOLVED"):
        _reconcile(mongo_context, tenant, "missing-source-ent")
    mongo_context.subscriptions.insert_one(raw)


def test_unknown_feature_fails_closed(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-unknown-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "unknown-ent")
    raw = mongo_context.subscriptions.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)
    mongo_context.subscriptions.update_one({"_id": raw["_id"]}, {"$set": {"plan_features": ["unknown.branding.v99"], "proof_hash": ""}})
    with pytest.raises(TenantBrandingEntitlementReconciliationError):
        _reconcile(mongo_context, tenant, "unknown-ent")


def test_conflicting_features_fail_closed(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-conflict-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "conflict-ent")
    raw = mongo_context.subscriptions.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)
    mongo_context.subscriptions.update_one({"_id": raw["_id"]}, {"$set": {"plan_features": [BRANDING_VAS_PROFESSIONAL_ID, BRANDING_VAS_ENTERPRISE_ID], "proof_hash": ""}})
    with pytest.raises(TenantBrandingEntitlementReconciliationError):
        _reconcile(mongo_context, tenant, "conflict-ent")


def test_tenant_isolation_prevents_foreign_truth_and_pointer_access(mongo_context: _MongoContext) -> None:
    tenant_a = f"p2c5-a-{uuid.uuid4().hex}"
    tenant_b = f"p2c5-b-{uuid.uuid4().hex}"
    source_a = _subscription(tenant_a)
    _compose(mongo_context, source_a, "tenant-a-ent")
    _subscription(tenant_b)
    tenant_a_history_before = tuple(mongo_context.history.find({"tenant_id": tenant_a}))
    tenant_a_current_before = tuple(mongo_context.current.find({"tenant_id": tenant_a}))
    tenant_b_history_before = tuple(mongo_context.history.find({"tenant_id": tenant_b}))
    tenant_b_current_before = tuple(mongo_context.current.find({"tenant_id": tenant_b}))
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="D21C2_ENTITLEMENT_NOT_FOUND") as error:
        _reconcile(mongo_context, tenant_b, "tenant-a-ent")
    assert "tenant-a-ent" not in str(error.value)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(TenantBrandingEntitlementRegistryNotFoundError):
            EntitlementRegistry.get_current(tenant_b, "tenant-a-ent", mongo_context.history, mongo_context.current, session=session)
        session.abort_transaction()
    assert tuple(mongo_context.history.find({"tenant_id": tenant_a})) == tenant_a_history_before
    assert tuple(mongo_context.current.find({"tenant_id": tenant_a})) == tenant_a_current_before
    assert tuple(mongo_context.history.find({"tenant_id": tenant_b})) == tenant_b_history_before
    assert tuple(mongo_context.current.find({"tenant_id": tenant_b})) == tenant_b_current_before


def test_missing_and_inactive_transactions_reject(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-session-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "session-ent")
    service = TenantBrandingEntitlementReconciliationService(
        subscription_collection=mongo_context.subscriptions,
        history_collection=mongo_context.history,
        current_collection=mongo_context.current,
    )
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="ACTIVE_TRANSACTION"):
        service.reconcile(tenant_id=tenant, entitlement_id="session-ent", evaluated_at=NOW, occurred_at=NOW, session=None)
    class Inactive:
        in_transaction = False
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="ACTIVE_TRANSACTION"):
        service.reconcile(tenant_id=tenant, entitlement_id="session-ent", evaluated_at=NOW, occurred_at=NOW, session=Inactive())


def test_same_session_propagates_and_service_owns_no_transaction(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-propagation-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "propagation-ent")
    calls: list[Any] = []
    original = SubscriptionRegistry.list_entities
    def reader(*args: Any, **kwargs: Any) -> Any:
        calls.append(kwargs.get("session"))
        return original(*args, **kwargs)
    class SpySubscription:
        list_entities = staticmethod(reader)
    service = TenantBrandingEntitlementReconciliationService(
        subscription_collection=mongo_context.subscriptions,
        history_collection=mongo_context.history,
        current_collection=mongo_context.current,
        subscription_registry=SpySubscription,
    )
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        result = service.reconcile(tenant_id=tenant, entitlement_id="propagation-ent", evaluated_at=NOW, occurred_at=NOW, session=session)
        assert result.outcome is TenantBrandingEntitlementReconciliationOutcome.CURRENT
        assert calls == [session]
        assert session.in_transaction is True
        session.abort_transaction()


def test_competing_transition_cas_rejects_divergent_replay(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-cas-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    composed = _compose(mongo_context, source, "cas-ent")
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(TenantBrandingEntitlementRegistryConflictError, match="D21B2B_TRANSITION_REPLAY_CONFLICT"):
            EntitlementRegistry.transition(
                tenant_id=tenant,
                entitlement_id="cas-ent",
                target_state=TenantBrandingEntitlementState.SUSPENDED,
                expected_revision=composed.entitlement.lifecycle_revision - 1,
                evidence_reference="stale",
                evidence_fingerprint="a" * 128,
                occurred_at=NOW,
                history_collection=mongo_context.history,
                current_collection=mongo_context.current,
                session=session,
            )
        session.abort_transaction()


def test_true_stale_revision_cas_rejects_after_two_legal_revisions(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-true-stale-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    composed = _compose(mongo_context, source, "true-stale-ent")
    _set_status(source, tenant, SubscriptionStatus.PAUSED)
    suspended = _reconcile(mongo_context, tenant, "true-stale-ent")
    assert suspended.target_state is TenantBrandingEntitlementState.SUSPENDED
    assert suspended.entitlement.lifecycle_revision == composed.entitlement.lifecycle_revision + 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        durable_before = EntitlementRegistry.get_current(
            tenant,
            "true-stale-ent",
            mongo_context.history,
            mongo_context.current,
            session=session,
        )
        assert durable_before.lifecycle_revision == 2
        expected_revision = durable_before.lifecycle_revision - 2
        history_before = tuple(
            mongo_context.history.find(
                {"tenant_id": tenant, "entitlement_id": "true-stale-ent"},
                session=session,
            ).sort("lifecycle_revision", 1)
        )
        current_before = tuple(
            mongo_context.current.find(
                {"tenant_id": tenant, "entitlement_id": "true-stale-ent"},
                session=session,
            )
        )
        assert expected_revision == 0
        assert durable_before.lifecycle_revision - expected_revision >= 2
        with pytest.raises(TenantBrandingEntitlementRegistryConflictError, match="D21B2B_STALE_REVISION"):
            EntitlementRegistry.transition(
                tenant_id=tenant,
                entitlement_id="true-stale-ent",
                target_state=TenantBrandingEntitlementState.REVOKED,
                expected_revision=expected_revision,
                evidence_reference="true-stale",
                evidence_fingerprint="b" * 128,
                occurred_at=NOW,
                history_collection=mongo_context.history,
                current_collection=mongo_context.current,
                session=session,
            )
        current_after = EntitlementRegistry.get_current(
            tenant,
            "true-stale-ent",
            mongo_context.history,
            mongo_context.current,
            session=session,
        )
        assert current_after.to_dict() == durable_before.to_dict()
        history_after = tuple(
            mongo_context.history.find(
                {"tenant_id": tenant, "entitlement_id": "true-stale-ent"},
                session=session,
            ).sort("lifecycle_revision", 1)
        )
        current_after_documents = tuple(
            mongo_context.current.find(
                {"tenant_id": tenant, "entitlement_id": "true-stale-ent"},
                session=session,
            )
        )
        assert history_after == history_before
        assert current_after_documents == current_before
        assert sum(1 for item in history_after if item["lifecycle_revision"] == 2) == 1
        session.abort_transaction()


def test_abort_rolls_back_reconciliation(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-abort-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "abort-ent")
    _set_status(source, tenant, SubscriptionStatus.PAUSED)
    _reconcile(mongo_context, tenant, "abort-ent", commit=False)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        current = EntitlementRegistry.get_current(tenant, "abort-ent", mongo_context.history, mongo_context.current, session=session)
        assert current.lifecycle_state is TenantBrandingEntitlementState.ACTIVE
        session.abort_transaction()
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 2


def test_exact_and_divergent_terminal_replay(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-replay-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "replay-ent")
    _set_status(source, tenant, SubscriptionStatus.PAUSED)
    first = _reconcile(mongo_context, tenant, "replay-ent")
    second = _reconcile(mongo_context, tenant, "replay-ent")
    assert first.target_state is TenantBrandingEntitlementState.SUSPENDED
    assert second.outcome is TenantBrandingEntitlementReconciliationOutcome.IDEMPOTENT_REPLAY
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="DIVERGENT_TERMINAL_REPLAY"):
        _reconcile(mongo_context, tenant, "replay-ent", evaluated_at=NOW + timedelta(hours=1))


def test_replacement_evidence_is_deterministic(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-evidence-{uuid.uuid4().hex}"
    old = _subscription(tenant)
    composed = _compose(mongo_context, old, "evidence-ent")
    _set_status(old, tenant, SubscriptionStatus.CANCELLED)
    replacement = _subscription(tenant, "ENTERPRISE")
    result = _reconcile(mongo_context, tenant, "evidence-ent")
    replacement_persisted = SubscriptionRegistry.get(replacement.subscription_id, tenant_id_header=tenant)
    assert replacement_persisted is not None
    eligibility = derive_tenant_branding_commercial_eligibility(
        tenant_id=tenant,
        subscription=replacement_persisted,
        evaluated_at=NOW,
    )
    payload = {
        "tenant_id": composed.entitlement.tenant_id,
        "entitlement_id": composed.entitlement.entitlement_id,
        "entitlement_revision": composed.entitlement.lifecycle_revision,
        "previous_entitlement_fingerprint": composed.entitlement.fingerprint,
        "subscription_id": eligibility.subscription_id,
        "plan_id": eligibility.plan_id,
        "plan_catalogue_version": eligibility.plan_catalogue_version,
        "catalogue_fingerprint": eligibility.catalogue_fingerprint,
        "branding_vas_id": eligibility.branding_vas_id,
        "branding_tier": eligibility.branding_tier.value if eligibility.branding_tier else None,
        "subscription_status": eligibility.subscription_status.value,
        "evaluated_at": NOW.isoformat().replace("+00:00", "Z"),
        "eligibility_fingerprint": eligibility.fingerprint,
    }
    expected = hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert result.transition_evidence_fingerprint == expected


def test_current_pointer_and_history_hydrate_exactly(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-hydrate-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    composed = _compose(mongo_context, source, "hydrate-ent")
    _set_status(source, tenant, SubscriptionStatus.CANCELLED)
    result = _reconcile(mongo_context, tenant, "hydrate-ent")
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        current = EntitlementRegistry.get_current(tenant, "hydrate-ent", mongo_context.history, mongo_context.current, session=session)
        assert current.to_dict() == result.entitlement.to_dict()
        assert mongo_context.history.count_documents({"tenant_id": tenant}, session=session) == 3
        session.abort_transaction()
    assert composed.entitlement.lifecycle_revision == result.entitlement.lifecycle_revision - 1


def test_corrupt_current_pointer_fails_closed_and_is_restored(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-corrupt-current-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "corrupt-ent")
    original = deepcopy(mongo_context.current.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)
    mongo_context.current.update_one({"_id": original["_id"]}, {"$set": {"fingerprint": "f" * 128}})
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="ENTITLEMENT_READ_REJECTED"):
        _reconcile(mongo_context, tenant, "corrupt-ent")
    mongo_context.current.replace_one({"_id": original["_id"]}, original)


def test_corrupt_subscription_integrity_fails_before_transition(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-corrupt-sub-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "corrupt-sub-ent")
    original = deepcopy(mongo_context.subscriptions.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)
    history_before = tuple(mongo_context.history.find({"tenant_id": tenant}))
    current_before = tuple(mongo_context.current.find({"tenant_id": tenant}))
    mongo_context.subscriptions.update_one({"_id": original["_id"]}, {"$set": {"proof_hash": "f" * 128}})
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="D21C1_SUBSCRIPTION_INTEGRITY_INVALID"):
        _reconcile(mongo_context, tenant, "corrupt-sub-ent")
    mongo_context.subscriptions.replace_one({"_id": original["_id"]}, original)
    assert tuple(mongo_context.history.find({"tenant_id": tenant})) == history_before
    assert tuple(mongo_context.current.find({"tenant_id": tenant})) == current_before


def test_authority_boundaries_have_no_external_writes_or_surfaces(mongo_context: _MongoContext) -> None:
    source_text = inspect.getsource(TenantBrandingEntitlementReconciliationService)
    public_methods = {name for name, member in inspect.getmembers(TenantBrandingEntitlementReconciliationService, predicate=inspect.isfunction) if not name.startswith("_")}
    assert public_methods == {"reconcile"}
    assert not {"kennel", "payment", "settlement", "profile", "asset", "browser", "iam"} & set(source_text.lower().split())
    tenant = f"p2c5-authority-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "authority-ent")
    raw = mongo_context.current.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)
    assert not {"logo", "favicon", "profile_id", "asset_url", "permission", "role", "payment", "settlement", "invoice"} & set(raw)
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 2


def test_paused_pointer_and_history_preserve_active_predecessor(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-paused-pointer-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    composed = _compose(mongo_context, source, "paused-pointer-ent")
    _set_status(source, tenant, SubscriptionStatus.PAUSED)
    result = _reconcile(mongo_context, tenant, "paused-pointer-ent")
    assert result.entitlement.lifecycle_state is TenantBrandingEntitlementState.SUSPENDED
    assert result.entitlement.lifecycle_revision == composed.entitlement.lifecycle_revision + 1
    assert mongo_context.history.count_documents({"tenant_id": tenant, "lifecycle_revision": composed.entitlement.lifecycle_revision}) == 1
    pointer = mongo_context.current.find_one({"tenant_id": tenant})
    assert isinstance(pointer, dict)
    assert pointer["lifecycle_revision"] == result.entitlement.lifecycle_revision
    assert pointer["lifecycle_state"] == TenantBrandingEntitlementState.SUSPENDED.value


def test_past_due_replay_does_not_add_revision(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-pastdue-replay-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "pastdue-replay-ent")
    _set_status(source, tenant, SubscriptionStatus.PAST_DUE)
    first = _reconcile(mongo_context, tenant, "pastdue-replay-ent")
    count = mongo_context.history.count_documents({"tenant_id": tenant})
    second = _reconcile(mongo_context, tenant, "pastdue-replay-ent")
    assert first.entitlement.lifecycle_state is TenantBrandingEntitlementState.SUSPENDED
    assert second.outcome is TenantBrandingEntitlementReconciliationOutcome.IDEMPOTENT_REPLAY
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == count


def test_cancelled_replay_does_not_add_revision(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-cancelled-replay-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "cancelled-replay-ent")
    _set_status(source, tenant, SubscriptionStatus.CANCELLED)
    first = _reconcile(mongo_context, tenant, "cancelled-replay-ent")
    count = mongo_context.history.count_documents({"tenant_id": tenant})
    second = _reconcile(mongo_context, tenant, "cancelled-replay-ent")
    assert first.entitlement.lifecycle_state is TenantBrandingEntitlementState.REVOKED
    assert second.outcome is TenantBrandingEntitlementReconciliationOutcome.IDEMPOTENT_REPLAY
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == count


def test_expired_replay_does_not_add_revision(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-expired-replay-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "expired-replay-ent")
    _set_status(source, tenant, SubscriptionStatus.EXPIRED)
    first = _reconcile(mongo_context, tenant, "expired-replay-ent")
    count = mongo_context.history.count_documents({"tenant_id": tenant})
    second = _reconcile(mongo_context, tenant, "expired-replay-ent")
    assert first.entitlement.lifecycle_state is TenantBrandingEntitlementState.REVOKED
    assert second.outcome is TenantBrandingEntitlementReconciliationOutcome.IDEMPOTENT_REPLAY
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == count


def test_replacement_reconciliation_does_not_create_new_entitlement(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-replacement-no-create-{uuid.uuid4().hex}"
    old = _subscription(tenant)
    _compose(mongo_context, old, "old-ent")
    _set_status(old, tenant, SubscriptionStatus.CANCELLED)
    replacement = _subscription(tenant, "ENTERPRISE")
    result = _reconcile(mongo_context, tenant, "old-ent")
    assert result.entitlement.entitlement_id == "old-ent"
    assert result.entitlement.lifecycle_state is TenantBrandingEntitlementState.REVOKED
    assert mongo_context.current.count_documents({"tenant_id": tenant}) == 1
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 3
    assert replacement.subscription_id != old.subscription_id


def test_current_source_lineage_remains_immutable_after_noop(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-lineage-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    composed = _compose(mongo_context, source, "lineage-ent")
    result = _reconcile(mongo_context, tenant, "lineage-ent")
    assert result.entitlement.source_evidence_reference == composed.entitlement.source_evidence_reference
    assert result.entitlement.source_evidence_fingerprint == composed.entitlement.source_evidence_fingerprint
    assert result.entitlement.branding_tier == composed.entitlement.branding_tier


def test_reversed_closed_history_insertion_order_is_current(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-order-{uuid.uuid4().hex}"
    first = _subscription(tenant, subscription_key=f"first-{uuid.uuid4().hex}")
    second = _subscription(tenant, subscription_key=f"second-{uuid.uuid4().hex}")
    current = _subscription(tenant, subscription_key=f"current-{uuid.uuid4().hex}")
    _set_status(first, tenant, SubscriptionStatus.CANCELLED)
    _set_status(second, tenant, SubscriptionStatus.EXPIRED)
    _compose(mongo_context, current, "order-ent")
    assert _reconcile(mongo_context, tenant, "order-ent").outcome is TenantBrandingEntitlementReconciliationOutcome.CURRENT


def test_noop_leaves_current_pointer_document_unchanged(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-pointer-noop-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "pointer-noop-ent")
    before = deepcopy(mongo_context.current.find_one({"tenant_id": tenant}))
    assert isinstance(before, dict)
    _reconcile(mongo_context, tenant, "pointer-noop-ent")
    after = mongo_context.current.find_one({"tenant_id": tenant})
    assert isinstance(after, dict)
    assert {key: value for key, value in before.items() if key != "_id"} == {key: value for key, value in after.items() if key != "_id"}


def test_corrupt_history_payload_fails_closed(mongo_context: _MongoContext) -> None:
    tenant = f"p2c5-corrupt-history-{uuid.uuid4().hex}"
    source = _subscription(tenant)
    _compose(mongo_context, source, "corrupt-history-ent")
    original = deepcopy(mongo_context.history.find_one({"tenant_id": tenant, "lifecycle_revision": 1}))
    assert isinstance(original, dict)
    payload = dict(original["entitlement_payload"])
    payload["lifecycle_state"] = TenantBrandingEntitlementState.REVOKED.value
    mongo_context.history.update_one({"_id": original["_id"]}, {"$set": {"entitlement_payload": payload}})
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="ENTITLEMENT_READ_REJECTED"):
        _reconcile(mongo_context, tenant, "corrupt-history-ent")
    mongo_context.history.replace_one({"_id": original["_id"]}, original)


# ARTIFACT: test_tenant_branding_entitlement_reconciliation_real_mongo.py
# VERSION: v1.0.0-L10-P2C5-D21C2-RECONCILIATION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: source-bound D21C2 currentness and D21B2B lifecycle persistence only
# TENANT POSTURE: UUID-isolated disposable replica-set database and exact tenant scope
# FAIL-CLOSED POSTURE: topology, ambiguity, corruption, replay and transaction misuse reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
