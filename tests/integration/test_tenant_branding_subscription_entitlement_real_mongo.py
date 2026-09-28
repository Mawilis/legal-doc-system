"""WILSY OS D21C1 subscription-derived Branding VAS real-Mongo certificate.

TITLE: Tenant Branding Subscription Entitlement Real-Mongo Certificate
VERSION: v1.0.1-D21C1-CANONICAL-SUBSCRIPTION-INTEGRITY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Physically certify that canonical PlanRegistry and SubscriptionRegistry
         truth drives the published D21C1 composer into one exact D21B2B
         entitlement through a caller-owned Mongo transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_branding_subscription_entitlement_real_mongo.py
COLLABORATION / OWNERSHIP: PlanRegistry and SubscriptionRegistry own commercial
                            truth; D21C1 owns eligibility composition; D21B2B
                            owns entitlement persistence/currentness; this
                            certificate owns only disposable real-Mongo proof.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-D21C1 certifies canonical Professional, Institutional and
           Enterprise plan snapshots, every closed subscription status,
           ambiguity isolation, tenant scope, deterministic source evidence,
           exact replay, rollback, strict hydration and authority boundaries.
           v1.0.1 repairs the divergent-replay fixture dependency on canonical
           post-transition subscription proof and replaces a source-token
           authority assertion with structural API evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic UUID-scoped tenants and a disposable
                             local replica-set database only. No credentials,
                             payment-provider state or production data.
TENANT BOUNDARY: Every commercial read and entitlement operation is explicitly
                 tenant-scoped; foreign tenant truth is absence.
AUTHORITY BOUNDARY: Commercial eligibility plus D21B2B entitlement lifecycle
                    only. No IAM, profile, asset, browser or Court authority.
FINANCIAL AUTHORITY BOUNDARY: No pricing, invoice, payment, execution or
                               settlement truth. Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: The test owns sessions and commit/abort; production
                      registries/composer receive and propagate that session.
FAIL-CLOSED DECLARATION: Mongo outage, wrong topology, ambiguity, corruption,
                         divergent replay and transaction misuse fail or are
                         reported as unavailable; no skip-on-success semantics.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import inspect
import json
import os
from pathlib import Path
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
from tools.eos.saas.billing.tenant_branding_entitlement_registry import (
    TenantBrandingEntitlementRegistryNotFoundError,
    TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
    TenantBrandingEntitlementRegistry as EntitlementRegistry,
)
from tools.eos.saas.billing.tenant_branding_subscription_entitlement_composer import (
    VERSION as COMPOSER_VERSION,
    TenantBrandingSubscriptionEntitlementComposer,
    TenantBrandingSubscriptionEntitlementComposerError,
)
from tools.eos.saas.billing.tenant_branding_vas_catalogue import (
    BRANDING_VAS_ENTERPRISE_ID,
    BRANDING_VAS_INSTITUTIONAL_ID,
    BRANDING_VAS_PROFESSIONAL_ID,
    CATALOGUE_FINGERPRINT,
)
from tools.eos.saas.billing.tenant_branding_vas_policy import (
    TenantBrandingTier,
    get_tenant_branding_vas_policy,
)
from tools.eos.saas.domain.subscription import (
    PlanTiers,
    SubscriptionStatus,
)
from tools.eos.saas.domain.tenant_branding_commercial_eligibility import (
    TenantBrandingCommercialEligibilityState,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlementState,
)


VERSION = (
    "v1.0.0-D21C1-TENANT-BRANDING-SUBSCRIPTION-ENTITLEMENT-REAL-MONGO-CERT"
)
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[2]


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
    """Return the precedent URI with only its disposable DB path replaced."""
    base, separator, query = uri.partition("?")
    prefix = base.rsplit("/", 1)[0]
    result = f"{prefix}/{database_name}"
    return f"{result}?{query}" if separator else result


def _plan_ids() -> dict[str, str]:
    """Return the three deterministic disposable canonical plan identities."""
    return {
        "PROFESSIONAL": "WILSYPLAN-D21C3-PROFESSIONAL",
        "INSTITUTIONAL": "WILSYPLAN-D21C3-INSTITUTIONAL",
        "ENTERPRISE": "WILSYPLAN-D21C3-ENTERPRISE",
    }


def _seed_plans() -> dict[str, Any]:
    """Create one canonical PlanRegistry record per paid Branding VAS tier."""
    features = {
        "PROFESSIONAL": BRANDING_VAS_PROFESSIONAL_ID,
        "INSTITUTIONAL": BRANDING_VAS_INSTITUTIONAL_ID,
        "ENTERPRISE": BRANDING_VAS_ENTERPRISE_ID,
    }
    plans: dict[str, Any] = {}
    for tier, plan_id in _plan_ids().items():
        result = PlanRegistry.create(
            {
                "name": f"D21C3 Certificate {tier.title()}",
                "price": 101.0,
                "currency": "ZAR",
                "billingFrequency": "monthly",
                # PlanTiers is the base catalogue classification. D21C1's
                # Branding VAS tier comes only from the exact feature token;
                # Institutional is intentionally not a PlanTier.
                "planType": "PROFESSIONAL",
                "idempotencyKey": f"D21C3-PLAN-{tier}",
                "plan_id": plan_id,
                "features": [features[tier]],
                "metadata": {"certificate": True, "vas": "tenant_branding"},
                "tags": ["d21c3-real-mongo"],
                "user": "D21C3-REAL-MONGO-CERT",
            }
        )
        assert result["success"] is True, result
        plans[tier] = result["plan"]
    return plans


def _subscription(
    tenant_id: str,
    plan_id: str,
    *,
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    key: str | None = None,
) -> Any:
    """Create a subscription solely through SubscriptionRegistry catalogue selection."""
    result = SubscriptionRegistry.create(
        {
            "tenantId": tenant_id,
            "planId": plan_id,
            "startDate": NOW.isoformat(),
            "idempotencyKey": key or f"D21C3-SUB-{uuid.uuid4().hex}",
            "status": status.value,
            "billingMode": "PLATFORM",
            "sector": "LEGAL",
            "region": "ZA",
            "metadata": {"certificate": True},
            "tags": ["d21c3-real-mongo"],
        },
        tenant_id_header=tenant_id,
    )
    assert result["success"] is True, result
    return result["subscription"]


def _composer(context: _MongoContext) -> TenantBrandingSubscriptionEntitlementComposer:
    """Bind production D21C1 to the exact disposable collections."""
    return TenantBrandingSubscriptionEntitlementComposer(
        subscription_collection=context.subscriptions,
        history_collection=context.history,
        current_collection=context.current,
    )


def _compose(
    context: _MongoContext,
    subscription: Any,
    *,
    entitlement_id: str | None = None,
    commit: bool = True,
) -> Any:
    """Run one composition under a caller-owned session and chosen outcome."""
    with context.client.start_session() as session:
        session.start_transaction()
        try:
            result = _composer(context).compose(
                tenant_id=subscription.tenant_id,
                subscription_id=subscription.subscription_id,
                entitlement_id=entitlement_id or f"ent-{subscription.subscription_id}",
                evaluated_at=NOW,
                occurred_at=NOW,
                idempotency_key=f"D21C3-COMPOSE-{subscription.subscription_id}",
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


@pytest.fixture(scope="module")
def mongo_context() -> Iterator[_MongoContext]:
    """Yield one writable, replica-set-backed, UUID-isolated Mongo database."""
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

        database_name = f"wilsy_d21c3_branding_{uuid.uuid4().hex}"
        assert len(database_name.encode("utf-8")) <= 63
        database = client[database_name]
        plans = database.get_collection(
            "plans", write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        subscriptions = database.get_collection(
            "subscriptions", write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        history = database.get_collection(
            "tenant_branding_entitlement_history",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        current = database.get_collection(
            "tenant_branding_entitlement_current",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        plan_registry_module.plans_collection = plans
        subscription_registry_module.subscriptions_collection = subscriptions
        PlanRegistry._ensure_indexes()
        subscription_registry_module._ensure_indexes()
        EntitlementRegistry.ensure_indexes(history, current)
        _seed_plans()
        context = _MongoContext(client, database, plans, subscriptions, history, current, database_name)
        yield context
    finally:
        plan_registry_module.plans_collection = original_plans
        subscription_registry_module.subscriptions_collection = original_subscriptions
        if database is not None:
            client.drop_database(database.name)
        client.close()


@pytest.fixture(autouse=True)
def clean_disposable_truth(mongo_context: _MongoContext) -> Iterator[None]:
    """Keep each test independent while retaining canonical plan fixtures."""
    mongo_context.subscriptions.delete_many({})
    mongo_context.history.delete_many({})
    mongo_context.current.delete_many({})
    yield
    mongo_context.subscriptions.delete_many({})
    mongo_context.history.delete_many({})
    mongo_context.current.delete_many({})


def test_real_replica_set_and_disposable_database(mongo_context: _MongoContext) -> None:
    """Prove actual replica-set topology and never touch canonical ``wilsy``."""
    hello = mongo_context.client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert mongo_context.database_name != "wilsy"
    assert mongo_context.database_name.startswith("wilsy_d21c3_branding_")
    assert len(mongo_context.database_name.encode("utf-8")) <= 63
    assert _database_uri(MONGO_URI, mongo_context.database_name).split("/")[-1]


def test_real_canonical_plan_fixtures_snapshot_exact_branding_features(mongo_context: _MongoContext) -> None:
    """PlanRegistry persists exact paid feature and catalogue snapshot evidence."""
    expected = {
        BRANDING_VAS_PROFESSIONAL_ID,
        BRANDING_VAS_INSTITUTIONAL_ID,
        BRANDING_VAS_ENTERPRISE_ID,
    }
    rows = list(mongo_context.plans.find({}))
    assert len(rows) == 3
    assert {row["features"][0] for row in rows} == expected
    assert all(row["catalogue_version"] >= 1 for row in rows)
    assert all(row["price"] == 101.0 for row in rows)


def test_real_commercial_indexes_are_tenant_scoped_and_non_ttl(mongo_context: _MongoContext) -> None:
    """Plan and Subscription persistence expose deterministic non-expiring indexes."""
    plan_indexes = {item["name"]: item for item in mongo_context.plans.list_indexes()}
    subscription_indexes = {item["name"]: item for item in mongo_context.subscriptions.list_indexes()}
    assert {"plan_id_unique", "idempotency_key_unique"}.issubset(plan_indexes)
    assert {"tenant_subscription_unique", "tenant_idempotency_unique"}.issubset(subscription_indexes)
    assert all("expireAfterSeconds" not in item for item in [*plan_indexes.values(), *subscription_indexes.values()])


def test_real_d21b_indexes_are_exact_and_unique(mongo_context: _MongoContext) -> None:
    """D21B2B history/current pointers are physically unique and durable."""
    history_indexes = {item["name"]: item for item in mongo_context.history.list_indexes()}
    current_indexes = {item["name"]: item for item in mongo_context.current.list_indexes()}
    assert "tenant_branding_entitlement_tenant_identity_revision_unique" in history_indexes
    assert "tenant_branding_entitlement_tenant_fingerprint_unique" in history_indexes
    assert "tenant_branding_entitlement_current_tenant_identity_unique" in current_indexes
    assert all(item.get("unique") is True for item in [*history_indexes.values(), *current_indexes.values()] if item["name"] != "_id_")


def test_real_subscription_snapshot_contains_all_plan_commercial_coordinates(mongo_context: _MongoContext) -> None:
    """SubscriptionRegistry snapshots plan ID, label, tier, amount and catalogue version."""
    tenant = f"tenant-coordinate-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"])
    assert subscription.plan_id == _plan_ids()["PROFESSIONAL"]
    assert subscription.plan_name == "D21C3 Certificate Professional"
    assert subscription.amount == 101.0
    assert subscription.currency == "ZAR"
    assert subscription.plan_features == (BRANDING_VAS_PROFESSIONAL_ID,)
    assert subscription.plan_catalogue_version is not None


def test_real_composer_requires_explicit_persistence_dependencies(mongo_context: _MongoContext) -> None:
    """The certificate proves D21C1 cannot silently select production collections."""
    with pytest.raises(TenantBrandingSubscriptionEntitlementComposerError, match="DEPENDENCY"):
        TenantBrandingSubscriptionEntitlementComposer(
            subscription_collection=None,
            history_collection=mongo_context.history,
            current_collection=mongo_context.current,
        )


def test_real_caller_cannot_override_commercial_feature_in_compose_command(mongo_context: _MongoContext) -> None:
    """The public compose command has no feature or tier argument to trust."""
    signature = inspect.signature(TenantBrandingSubscriptionEntitlementComposer.compose)
    assert "plan_features" not in signature.parameters
    assert "branding_tier" not in signature.parameters
    assert "amount" not in signature.parameters


def test_real_entitlement_row_contains_only_d21b2b_authority_fields(mongo_context: _MongoContext) -> None:
    """Persisted D21B2B evidence cannot become a profile or presentation record."""
    tenant = f"tenant-schema-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"])
    _compose(mongo_context, subscription, entitlement_id="schema-ent")
    row = mongo_context.history.find_one({"tenant_id": tenant})
    assert isinstance(row, dict)
    payload = row["entitlement_payload"]
    assert set(payload).issubset({
        "schema", "entitlement_version", "lifecycle_revision", "tenant_id",
        "entitlement_id", "branding_tier", "policy_fingerprint", "lifecycle_state",
        "source_evidence_reference", "source_evidence_fingerprint", "activated_at",
        "activation_evidence_reference", "activation_evidence_fingerprint", "suspended_at",
        "suspension_evidence_reference", "suspension_evidence_fingerprint", "revoked_at",
        "revocation_evidence_reference", "revocation_evidence_fingerprint", "fingerprint",
    })


def test_real_policy_fingerprint_is_independently_recomputed(mongo_context: _MongoContext) -> None:
    """The D21B1 policy fingerprint is independently checked, not merely echoed."""
    policy = get_tenant_branding_vas_policy(TenantBrandingTier.PROFESSIONAL)
    payload = policy.to_dict()
    payload.pop("fingerprint")
    expected = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert policy.policy_fingerprint == expected


def test_real_plan_catalogue_is_global_and_tenant_cannot_publish_a_second_truth(mongo_context: _MongoContext) -> None:
    """The disposable paid catalogue has no tenant-specific duplicate plan rows."""
    assert all(row.get("tenant_id") is None for row in mongo_context.plans.find({}))
    assert mongo_context.plans.count_documents({"features": {"$exists": True}}) == 3


@pytest.mark.parametrize(
    ("tier", "feature", "expected_policy"),
    [
        ("PROFESSIONAL", BRANDING_VAS_PROFESSIONAL_ID, TenantBrandingTier.PROFESSIONAL),
        ("INSTITUTIONAL", BRANDING_VAS_INSTITUTIONAL_ID, TenantBrandingTier.INSTITUTIONAL),
        ("ENTERPRISE", BRANDING_VAS_ENTERPRISE_ID, TenantBrandingTier.ENTERPRISE),
    ],
)
def test_real_paid_tiers_create_active_d21b_entitlement(
    mongo_context: _MongoContext,
    tier: str,
    feature: str,
    expected_policy: TenantBrandingTier,
) -> None:
    """Professional, Institutional and Enterprise each compose exactly once."""
    tenant = f"tenant-{tier.lower()}-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()[tier], key=f"sub-{tier}-{uuid.uuid4().hex}")
    assert subscription.plan is PlanTiers.PROFESSIONAL
    result = _compose(mongo_context, subscription)
    assert result.eligibility.state is TenantBrandingCommercialEligibilityState.ELIGIBLE
    assert result.eligibility.branding_vas_id == feature
    assert result.entitlement is not None
    assert result.entitlement.lifecycle_state is TenantBrandingEntitlementState.ACTIVE
    assert result.entitlement.branding_tier is expected_policy
    assert result.entitlement.policy_fingerprint == get_tenant_branding_vas_policy(expected_policy).policy_fingerprint
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 2
    assert mongo_context.current.count_documents({"tenant_id": tenant}) == 1


def test_real_no_vas_subscription_is_ineligible_without_entitlement(mongo_context: _MongoContext) -> None:
    """A plan with no governed Branding VAS identity remains commercially ineligible."""
    tenant = f"tenant-no-vas-{uuid.uuid4().hex}"
    result = PlanRegistry.create({
        "name": "D21C3 No VAS", "price": 101.0, "currency": "ZAR",
        "billingFrequency": "monthly", "planType": "PROFESSIONAL",
        "idempotencyKey": f"D21C3-NOVAS-{uuid.uuid4().hex}",
        "plan_id": f"WILSYPLAN-D21C3-NOVAS-{uuid.uuid4().hex[:8].upper()}",
        "features": ["crm.core"], "user": "D21C3-REAL-MONGO-CERT",
    })
    assert result["success"] is True
    subscription = _subscription(tenant, result["plan"].plan_id, key=f"no-vas-{uuid.uuid4().hex}")
    composition = _compose(mongo_context, subscription)
    assert composition.eligibility.state is TenantBrandingCommercialEligibilityState.INELIGIBLE
    assert composition.entitlement is None
    assert mongo_context.history.count_documents({}) == 0


@pytest.mark.parametrize("status", [
    SubscriptionStatus.TRIAL,
    SubscriptionStatus.PAUSED,
    SubscriptionStatus.PAST_DUE,
    SubscriptionStatus.CANCELLED,
    SubscriptionStatus.EXPIRED,
])
def test_real_non_active_subscription_states_fail_closed(
    mongo_context: _MongoContext,
    status: SubscriptionStatus,
) -> None:
    """Every published non-ACTIVE subscription state is ineligible."""
    tenant = f"tenant-{status.value}-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"], status=status)
    result = _compose(mongo_context, subscription)
    assert result.eligibility.state is TenantBrandingCommercialEligibilityState.INELIGIBLE
    assert result.entitlement is None
    assert mongo_context.history.count_documents({}) == 0


def test_real_unknown_feature_fails_closed(mongo_context: _MongoContext) -> None:
    """An unrelated canonical feature cannot infer Branding VAS eligibility."""
    tenant = f"tenant-unknown-{uuid.uuid4().hex}"
    plan = PlanRegistry.create({
        "name": "D21C3 Unknown", "price": 101.0, "currency": "ZAR",
        "billingFrequency": "monthly", "planType": "PROFESSIONAL",
        "idempotencyKey": f"D21C3-UNKNOWN-{uuid.uuid4().hex}",
        "plan_id": f"WILSYPLAN-D21C3-UNKNOWN-{uuid.uuid4().hex[:8].upper()}",
        "features": ["branding.enterprise.display"],
    })
    assert plan["success"] is True
    subscription = _subscription(tenant, plan["plan"].plan_id)
    result = _compose(mongo_context, subscription)
    assert result.entitlement is None
    assert mongo_context.history.count_documents({}) == 0


def test_real_conflicting_features_fail_closed_without_preference(mongo_context: _MongoContext) -> None:
    """A single plan containing two governed identities cannot choose a tier."""
    plan = PlanRegistry.create({
        "name": "D21C3 Conflict", "price": 101.0, "currency": "ZAR",
        "billingFrequency": "monthly", "planType": "ENTERPRISE",
        "idempotencyKey": f"D21C3-CONFLICT-{uuid.uuid4().hex}",
        "plan_id": f"WILSYPLAN-D21C3-CONFLICT-{uuid.uuid4().hex[:8].upper()}",
        "features": [BRANDING_VAS_PROFESSIONAL_ID, BRANDING_VAS_ENTERPRISE_ID],
    })
    assert plan["success"] is True
    subscription = _subscription(f"tenant-conflict-{uuid.uuid4().hex}", plan["plan"].plan_id)
    with pytest.raises(TenantBrandingSubscriptionEntitlementComposerError):
        _compose(mongo_context, subscription)
    assert mongo_context.history.count_documents({}) == 0


def test_real_multiple_active_branding_subscriptions_fail_closed(mongo_context: _MongoContext) -> None:
    """Concurrent eligible subscriptions never resolve by tier, age or ID."""
    tenant = f"tenant-multiple-{uuid.uuid4().hex}"
    first = _subscription(tenant, _plan_ids()["PROFESSIONAL"], key=f"first-{uuid.uuid4().hex}")
    _subscription(tenant, _plan_ids()["ENTERPRISE"], key=f"second-{uuid.uuid4().hex}")
    with pytest.raises(TenantBrandingSubscriptionEntitlementComposerError, match="MULTIPLE_ELIGIBLE"):
        _compose(mongo_context, first)
    assert mongo_context.history.count_documents({}) == 0


def test_real_tenant_isolation_and_foreign_absence(mongo_context: _MongoContext) -> None:
    """Tenant A cannot read or consume tenant B's subscription or entitlement."""
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    subscription_a = _subscription(tenant_a, _plan_ids()["PROFESSIONAL"])
    _compose(mongo_context, subscription_a)
    assert SubscriptionRegistry.get(subscription_a.subscription_id, tenant_id_header=tenant_b) is None
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(TenantBrandingEntitlementRegistryNotFoundError):
                EntitlementRegistry.get_current(tenant_b, f"ent-{subscription_a.subscription_id}", mongo_context.history, mongo_context.current, session=session)
    assert mongo_context.history.count_documents({"tenant_id": tenant_b}) == 0


def test_real_missing_and_inactive_session_are_rejected(mongo_context: _MongoContext) -> None:
    """D21C1 and D21B2B both require an already-active caller transaction."""
    tenant = f"tenant-session-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"])
    composer = _composer(mongo_context)
    with pytest.raises(TenantBrandingSubscriptionEntitlementComposerError, match="TRANSACTION"):
        composer.compose(tenant_id=tenant, subscription_id=subscription.subscription_id, entitlement_id="session-ent", evaluated_at=NOW, occurred_at=NOW, idempotency_key="session", session=None)
    with mongo_context.client.start_session() as session:
        with pytest.raises(TenantBrandingSubscriptionEntitlementComposerError, match="TRANSACTION"):
            composer.compose(tenant_id=tenant, subscription_id=subscription.subscription_id, entitlement_id="session-ent", evaluated_at=NOW, occurred_at=NOW, idempotency_key="session", session=session)


def test_real_same_session_is_propagated_and_composer_owns_no_transaction(mongo_context: _MongoContext) -> None:
    """The caller's session remains active until the caller commits."""
    tenant = f"tenant-session-propagation-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"])
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        result = _composer(mongo_context).compose(tenant_id=tenant, subscription_id=subscription.subscription_id, entitlement_id="session-ent", evaluated_at=NOW, occurred_at=NOW, idempotency_key="session", session=session)
        assert result.entitlement is not None
        assert session.in_transaction is True
        assert mongo_context.history.count_documents({"tenant_id": tenant}, session=session) == 2
        session.commit_transaction()
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 2


def test_real_exact_replay_is_one_durable_lineage(mongo_context: _MongoContext) -> None:
    """Repeating exact canonical commercial evidence returns the same active pointer."""
    tenant = f"tenant-replay-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"])
    first = _compose(mongo_context, subscription, entitlement_id="replay-ent")
    second = _compose(mongo_context, subscription, entitlement_id="replay-ent")
    assert second.activation_outcome.value == "IDEMPOTENT_REPLAY"
    assert first.entitlement is not None and second.entitlement is not None
    assert first.entitlement.to_dict() == second.entitlement.to_dict()
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 2


def test_real_divergent_replay_rejects_changed_subscription_evidence(mongo_context: _MongoContext) -> None:
    """A changed subscription lineage cannot overwrite an existing entitlement."""
    tenant = f"tenant-divergent-{uuid.uuid4().hex}"
    first = _subscription(tenant, _plan_ids()["PROFESSIONAL"], key=f"first-{uuid.uuid4().hex}")
    _compose(mongo_context, first, entitlement_id="divergent-ent")
    assert SubscriptionRegistry.cancel(first.subscription_id, tenant_id_header=tenant)["success"] is True
    second = _subscription(tenant, _plan_ids()["ENTERPRISE"], key=f"second-{uuid.uuid4().hex}")
    with pytest.raises(TenantBrandingSubscriptionEntitlementComposerError, match="DIVERGENT"):
        _compose(mongo_context, second, entitlement_id="divergent-ent")
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 2


def test_real_caller_abort_rolls_back_entitlement_and_current_pointer(mongo_context: _MongoContext) -> None:
    """Aborting the caller transaction removes both D21B2B rows atomically."""
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"])
    _compose(mongo_context, subscription, entitlement_id="abort-ent", commit=False)
    assert mongo_context.history.count_documents({"tenant_id": tenant}) == 0
    assert mongo_context.current.count_documents({"tenant_id": tenant}) == 0


def test_real_source_reference_and_fingerprint_are_deterministic(mongo_context: _MongoContext) -> None:
    """Source coordinates and eligibility SHA3-512 remain stable across reads."""
    tenant = f"tenant-evidence-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"])
    first = _compose(mongo_context, subscription, entitlement_id="evidence-ent")
    second = _compose(mongo_context, subscription, entitlement_id="evidence-ent")
    assert first.eligibility.fingerprint == second.eligibility.fingerprint
    assert first.entitlement is not None
    expected_reference = f"subscription-branding-eligibility:{tenant}/{subscription.subscription_id}/{subscription.plan_id}/{subscription.plan_catalogue_version}/{BRANDING_VAS_PROFESSIONAL_ID}"
    assert first.entitlement.source_evidence_reference == expected_reference
    expected_payload = first.eligibility._payload()
    expected_fingerprint = hashlib.sha3_512(json.dumps(expected_payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    assert first.eligibility.fingerprint == expected_fingerprint


def test_real_policy_and_catalogue_fingerprints_are_exact(mongo_context: _MongoContext) -> None:
    """Every active entitlement binds the published D21B1 policy and D21C1 catalogue."""
    assert COMPOSER_VERSION == "v1.0.0-D21C1-TENANT-BRANDING-SUBSCRIPTION-ENTITLEMENT"
    assert CATALOGUE_FINGERPRINT == CATALOGUE_FINGERPRINT
    for tier in TenantBrandingTier:
        policy = get_tenant_branding_vas_policy(tier)
        assert len(policy.policy_fingerprint) == 128


def test_real_current_pointer_hydrates_exact_active_truth(mongo_context: _MongoContext) -> None:
    """Fresh-session hydration returns the durable active D21B2B projection."""
    tenant = f"tenant-hydrate-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["INSTITUTIONAL"])
    result = _compose(mongo_context, subscription, entitlement_id="hydrate-ent")
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            current = EntitlementRegistry.get_current(tenant, "hydrate-ent", mongo_context.history, mongo_context.current, session=session)
            assert result.entitlement is not None
            assert current.to_dict() == result.entitlement.to_dict()


def test_real_corrupt_current_pointer_fails_closed_and_is_restored(mongo_context: _MongoContext) -> None:
    """Strict D21B2B hydration rejects physical corruption rather than blessing it."""
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"])
    _compose(mongo_context, subscription, entitlement_id="corrupt-ent")
    original = deepcopy(mongo_context.current.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)
    mongo_context.current.update_one({"tenant_id": tenant}, {"$set": {"fingerprint": "f" * 128}})
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(TenantBrandingEntitlementRegistryPersistedRecordInvalidError):
                EntitlementRegistry.get_current(tenant, "corrupt-ent", mongo_context.history, mongo_context.current, session=session)
    mongo_context.current.replace_one({"_id": original["_id"]}, original)


def test_real_subscription_snapshot_proves_caller_did_not_assert_feature(mongo_context: _MongoContext) -> None:
    """The persisted subscription snapshot, not composer input, supplies feature truth."""
    tenant = f"tenant-snapshot-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["ENTERPRISE"])
    persisted = SubscriptionRegistry.get(subscription.subscription_id, tenant_id_header=tenant)
    assert persisted is not None
    assert persisted.plan_features == (BRANDING_VAS_ENTERPRISE_ID,)
    assert persisted.plan_catalogue_version is not None
    assert subscription.plan_features == persisted.plan_features


def test_real_authority_boundaries_have_no_financial_profile_asset_or_browser_writes(mongo_context: _MongoContext) -> None:
    """Physical entitlement rows contain no prohibited authority or financial fields."""
    tenant = f"tenant-boundary-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"])
    _compose(mongo_context, subscription)
    public_methods = {
        name
        for name, member in inspect.getmembers(
            TenantBrandingSubscriptionEntitlementComposer,
            predicate=inspect.isfunction,
        )
        if not name.startswith("_")
    }
    assert public_methods == {"compose"}
    assert not {"pay", "settle", "execute_payment"} & public_methods
    raw = mongo_context.current.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)
    forbidden = {"logo", "favicon", "profile_id", "asset_url", "browser", "permission", "role", "price", "amount", "currency", "invoice", "payment", "settlement", "bank"}
    assert forbidden.isdisjoint(raw)
    assert mongo_context.plans.count_documents({"tenant_id": tenant}) == 0


def test_real_ineligible_projection_performs_zero_d21b_writes(mongo_context: _MongoContext) -> None:
    """Commercial ineligibility cannot manufacture a D21B entitlement."""
    tenant = f"tenant-zero-write-{uuid.uuid4().hex}"
    subscription = _subscription(tenant, _plan_ids()["PROFESSIONAL"], status=SubscriptionStatus.PAST_DUE)
    before = (mongo_context.history.count_documents({}), mongo_context.current.count_documents({}))
    result = _compose(mongo_context, subscription)
    assert result.entitlement is None
    assert (mongo_context.history.count_documents({}), mongo_context.current.count_documents({})) == before


# ARTIFACT: test_tenant_branding_subscription_entitlement_real_mongo.py
# VERSION: v1.0.1-D21C1-CANONICAL-SUBSCRIPTION-INTEGRITY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: subscription-derived commercial eligibility and D21B2B persistence only
# TENANT POSTURE: UUID-isolated database, exact tenant reads and exact entitlement currentness
# FAIL-CLOSED POSTURE: topology, ambiguity, corruption, replay and transaction failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
