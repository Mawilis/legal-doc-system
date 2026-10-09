"""Real-Mongo certificate for the D22B3 entitlement composer.

TITLE: Tenant Product Entitlement Composer Real-Mongo Certificate
VERSION: v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Physically prove subscription-backed deterministic Legal entitlement
         creation, activation, replay, rollback, isolation and race behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_product_entitlement_composer_real_mongo.py
COLLABORATION / OWNERSHIP: Uses actual PlanRegistry, SubscriptionRegistry and
                            D22B2 collections in a disposable local replica set.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER-REAL-MONGO-CERT
           establishes physical commit, abort, replay, cardinality, feature,
           terminality, tenant-isolation and competing-composition evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic local data only.
TENANT BOUNDARY: Every composition uses exact tenant-scoped subscription and
                 entitlement collections inside caller-owned transactions.
AUTHORITY BOUNDARY: Operational certificate only; no external authority.
TRANSACTION BOUNDARY: Tests own transactions; composer only propagates sessions.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing infrastructure skips only before fixture yield;
                         all post-yield invariant failures fail the certificate.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import os
from threading import Barrier
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
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement import tenant_product_entitlement_composer as composer
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION,
    HISTORY_COLLECTION,
    ensure_indexes,
    get_current,
    transition,
)


VERSION = "v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any, Any, Any]]:
    """Yield isolated registry and D22B2 collections on a real replica set."""
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
        database = client[f"wilsy_d22b3_composer_{uuid.uuid4().hex}"]
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
        history = database.get_collection(
            HISTORY_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        current = database.get_collection(
            CURRENT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        plan_registry_module.plans_collection = plans
        subscription_registry_module.subscriptions_collection = subscriptions
        PlanRegistry._ensure_indexes()
        subscription_registry_module._ensure_indexes()
        ensure_indexes(history, current)
        yield client, plans, subscriptions, history, current, database
    finally:
        plan_registry_module.plans_collection = original_plans
        subscription_registry_module.subscriptions_collection = original_subscriptions
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _plan(*, features: tuple[str, ...], key: str) -> str:
    """Persist one canonical PlanRegistry catalogue record."""
    result = PlanRegistry.create(
        {
            "name": f"D22B3 {key}",
            "price": 100.0,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "PROFESSIONAL",
            "idempotencyKey": f"plan-{key}",
            "active": True,
            "features": list(features),
            "metadata": {"certificate": True},
            "tags": ["d22b3-composer-cert"],
            "user": "D22B3-CERT",
        }
    )
    assert result["success"] is True
    return result["plan"].plan_id


def _subscription(tenant: str, plan_id: str, key: str) -> str:
    """Persist one actual canonical SubscriptionRegistry entity."""
    result = SubscriptionRegistry.create(
        {
            "tenantId": tenant,
            "planId": plan_id,
            "startDate": "2026-10-09T10:00:00+00:00",
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
    history: Any,
    current: Any,
) -> composer.TenantProductEntitlementCompositionResult:
    """Commit one composition in a caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return composer.compose_tenant_product_entitlement(
                tenant_id=tenant,
                product_id=TenantProductId.LEGAL_OPERATIONS,
                occurred_at=NOW,
                subscription_collection=subscriptions,
                entitlement_history_collection=history,
                entitlement_current_collection=current,
                session=session,
            )


def test_real_create_activate_hydrate_replay_and_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any],
) -> None:
    """Create pending+ACTIVE atomically, hydrate evidence and replay with zero rows."""
    client, plans, subscriptions, history, current, _ = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    plan_id = _plan(features=("legal.core",), key=uuid.uuid4().hex)
    _subscription(tenant, plan_id, uuid.uuid4().hex)
    plans_before = deepcopy(list(plans.find({})))
    subscriptions_before = deepcopy(list(subscriptions.find({"tenant_id": tenant})))
    first = _compose(client, tenant, subscriptions, history, current)
    assert first.entitlement.lifecycle_state is TenantProductEntitlementState.ACTIVE
    assert first.entitlement.lifecycle_revision == 1
    assert first.entitlement.entitlement_id == composer.derive_tenant_product_entitlement_id(
        tenant, TenantProductId.LEGAL_OPERATIONS
    )
    assert first.entitlement.source_evidence_reference.startswith("tpe-source:")
    assert first.entitlement.activation_evidence_reference is not None
    assert first.entitlement.activation_evidence_reference.startswith("tpe-activation:")
    assert history.count_documents({"tenant_id": tenant}) == 2
    assert current.count_documents({"tenant_id": tenant}) == 1
    replay = _compose(client, tenant, subscriptions, history, current)
    assert replay.exact_active_replay is True
    assert history.count_documents({"tenant_id": tenant}) == 2
    assert subscriptions_before == list(subscriptions.find({"tenant_id": tenant}))
    assert plans_before == list(plans.find({}))
    indexes = [*history.list_indexes(), *current.list_indexes()]
    assert all("expireAfterSeconds" not in item for item in indexes)


@pytest.mark.parametrize("mode", ["missing", "multiple"])
def test_real_commercial_failures_precede_entitlement_mutation(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any],
    mode: str,
) -> None:
    """Missing feature and multiple ACTIVE subscriptions persist no entitlement."""
    client, _, subscriptions, history, current, _ = mongo_context
    tenant = f"tenant-{mode}-{uuid.uuid4().hex}"
    features = () if mode == "missing" else ("legal.core",)
    plan_id = _plan(features=features, key=uuid.uuid4().hex)
    _subscription(tenant, plan_id, uuid.uuid4().hex)
    if mode == "multiple":
        second_plan = _plan(features=("legal.core",), key=uuid.uuid4().hex)
        _subscription(tenant, second_plan, uuid.uuid4().hex)
    with pytest.raises(composer.TenantProductEntitlementComposerCommercialError):
        _compose(client, tenant, subscriptions, history, current)
    assert history.count_documents({"tenant_id": tenant}) == 0
    assert current.count_documents({"tenant_id": tenant}) == 0


def test_real_abort_removes_both_revisions_and_pointer(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any],
) -> None:
    """Caller abort leaves zero D22B2 mutation while subscription remains."""
    client, _, subscriptions, history, current, _ = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    plan_id = _plan(features=("legal.core",), key=uuid.uuid4().hex)
    _subscription(tenant, plan_id, uuid.uuid4().hex)
    with client.start_session() as session:
        session.start_transaction()
        composer.compose_tenant_product_entitlement(
            tenant_id=tenant,
            product_id=TenantProductId.LEGAL_OPERATIONS,
            occurred_at=NOW,
            subscription_collection=subscriptions,
            entitlement_history_collection=history,
            entitlement_current_collection=current,
            session=session,
        )
        assert history.count_documents({"tenant_id": tenant}, session=session) == 2
        session.abort_transaction()
    assert history.count_documents({"tenant_id": tenant}) == 0
    assert current.count_documents({"tenant_id": tenant}) == 0
    assert subscriptions.count_documents({"tenant_id": tenant}) == 1


@pytest.mark.parametrize(
    "state",
    [TenantProductEntitlementState.SUSPENDED, TenantProductEntitlementState.REVOKED],
)
def test_real_terminal_lifecycle_is_not_resurrected(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any],
    state: TenantProductEntitlementState,
) -> None:
    """Physical suspended/revoked currentness blocks a second lineage."""
    client, _, subscriptions, history, current, _ = mongo_context
    tenant = f"tenant-terminal-{uuid.uuid4().hex}"
    plan_id = _plan(features=("legal.core",), key=uuid.uuid4().hex)
    _subscription(tenant, plan_id, uuid.uuid4().hex)
    active = _compose(client, tenant, subscriptions, history, current).entitlement
    with client.start_session() as session:
        with session.start_transaction():
            transition(
                tenant_id=tenant,
                entitlement_id=active.entitlement_id,
                target_state=state,
                expected_revision=1,
                evidence_reference=f"terminal-{state.value}",
                evidence_fingerprint="f" * 128,
                occurred_at=NOW,
                history_collection=history,
                current_collection=current,
                session=session,
            )
    with pytest.raises(composer.TenantProductEntitlementComposerConflictError):
        _compose(client, tenant, subscriptions, history, current)
    assert current.count_documents({"tenant_id": tenant}) == 1
    assert history.count_documents({"tenant_id": tenant}) == 3


def test_real_tenant_isolation_and_competing_composition_single_lineage(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any],
) -> None:
    """Foreign scope is absent and competitors cannot create two lineages."""
    client, _, subscriptions, history, current, _ = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    foreign = f"tenant-foreign-{uuid.uuid4().hex}"
    plan_id = _plan(features=("legal.core",), key=uuid.uuid4().hex)
    _subscription(tenant, plan_id, uuid.uuid4().hex)
    barrier = Barrier(2)

    def contender(_: int) -> str:
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                result = composer.compose_tenant_product_entitlement(
                    tenant_id=tenant,
                    product_id=TenantProductId.LEGAL_OPERATIONS,
                    occurred_at=NOW,
                    subscription_collection=subscriptions,
                    entitlement_history_collection=history,
                    entitlement_current_collection=current,
                    session=session,
                )
                session.commit_transaction()
                return result.outcome.value
            except composer.TenantProductEntitlementComposerError as error:
                if session.in_transaction:
                    session.abort_transaction()
                return error.code
            except PyMongoError as error:
                if session.in_transaction:
                    session.abort_transaction()
                return type(error).__name__

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(contender, (1, 2)))
    assert any(item == "COMPOSED" for item in outcomes)
    assert history.count_documents({"tenant_id": tenant}) == 2
    assert current.count_documents({"tenant_id": tenant}) == 1
    entitlement_id = composer.derive_tenant_product_entitlement_id(
        tenant, TenantProductId.LEGAL_OPERATIONS
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(Exception):
                get_current(foreign, entitlement_id, history, current, session=session)


# ARTIFACT: test_tenant_product_entitlement_composer_real_mongo.py
# VERSION: v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical positive-composition evidence only; no commercial mutation, IAM, route or financial authority
# TENANT POSTURE: UUID-isolated exact-tenant subscription and entitlement operations
# FAIL-CLOSED POSTURE: commercial ambiguity, absent features, terminal lifecycle, races and rollback are physically certified
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
