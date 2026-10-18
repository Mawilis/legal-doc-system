"""Real-Mongo certificate for Legal Operations commercial context.

TITLE:
    WILSY OS Legal Commercial Context Real-Mongo Certificate

VERSION:
    v1.0.0-LEGAL-COMMERCIAL-CONTEXT-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Prove that the Legal commercial-context projection reads exact tenant-scoped
    canonical subscription truth and current Legal product-entitlement truth
    from a real writable Mongo replica set inside one caller-owned snapshot
    transaction, without creating IAM, Legal lifecycle or financial authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_commercial_context_projection_real_mongo.py

COLLABORATION / OWNERSHIP:
    LegalCommercialContextProjection owns descriptive commercial conjunction.
    SubscriptionRegistry owns subscription persistence/hydration.
    D22B2 owns tenant-product entitlement history/current persistence.
    This certificate owns test evidence only.

CERTIFICATION / UPDATE DATE:
    2026-10-16

CHANGELOG:
    v1.0.0-LEGAL-COMMERCIAL-CONTEXT-REAL-MONGO-CERT
        - Establishes isolated real-Mongo positive projection proof.
        - Proves exact caller transaction propagation and tenant isolation.
        - Proves entitlement/subscription disagreement fails closed.
        - Proves no cross-tenant subscription or entitlement truth is admitted.

COMPLIANCE:
    POPIA section 19 technical controls.
    GDPR Article 32 technical controls.
    SOC 2 CC7.2-aligned technical controls.
    ISO 27001-aligned technical controls.
    No independent legal-compliance claim.

SECURITY / PRIVACY POSTURE:
    UUID-isolated synthetic records only. No credentials, production tenant
    data, protected Mongo instance or external provider data are used.

TENANT BOUNDARY:
    Every subscription and entitlement read is exact-tenant scoped. Foreign
    tenant evidence cannot satisfy or alter the requested tenant projection.

AUTHORITY BOUNDARY:
    Certification evidence only. Subscription and product entitlement do not
    grant IAM, Legal workspace admission, business role or Legal command truth.

FINANCIAL AUTHORITY BOUNDARY:
    Commercial amount evidence is descriptive only.
    APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
    Kennel EOS remains exclusive financial execution authority.

TRANSACTION BOUNDARY:
    Test caller starts and owns the exact Mongo transaction passed unchanged
    through the projection and underlying registries.

FAIL-CLOSED POSTURE:
    Missing transaction, cross-tenant evidence, entitlement/subscription
    disagreement, corruption or persistence failure cannot become success.

CONSTITUTION:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    NO EVIDENCE = NO FACT.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as subscription_registry_module
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionStatus,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.legal_commercial_context_projection import (
    LegalCommercialContextProjectionError,
    resolve_legal_commercial_context,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
import tools.eos.saas.entitlement.tenant_product_entitlement_registry as entitlement_registry


VERSION = "v1.0.0-LEGAL-COMMERCIAL-CONTEXT-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 10, 16, 8, 0, tzinfo=timezone.utc)
FP = "a" * 128


def _majority(database: Any, name: str) -> Any:
    """Return one majority/journal collection for exact certificate scope."""
    return database.get_collection(
        name,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )


@pytest.fixture
def mongo_context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    """Yield one UUID-isolated writable replica-set database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"sanctioned disposable Mongo unavailable: {type(error).__name__}"
            )

        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None

        database = client[
            f"wilsy_legal_commercial_context_{uuid4().hex}"
        ]
        collections = {
            "plans": _majority(database, "plans"),
            "subscriptions": _majority(database, "subscriptions"),
            "history": _majority(
                database,
                entitlement_registry.HISTORY_COLLECTION,
            ),
            "current": _majority(
                database,
                entitlement_registry.CURRENT_COLLECTION,
            ),
        }

        monkeypatch.setattr(
            plan_registry_module,
            "plans_collection",
            collections["plans"],
        )
        monkeypatch.setattr(
            subscription_registry_module,
            "subscriptions_collection",
            collections["subscriptions"],
        )

        PlanRegistry._ensure_indexes()
        subscription_registry_module._ensure_indexes()
        entitlement_registry.ensure_indexes(
            collections["history"],
            collections["current"],
        )

        yield client, database, collections
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _plan(tenant_id: str) -> Any:
    """Create one canonical tenant Legal plan with no caller pricing inference."""
    result = PlanRegistry.create(
        {
            "name": f"Legal Commercial {tenant_id}",
            "price": 14400.0,
            "currency": "ZAR",
            "billingFrequency": "annual",
            "planType": "PROFESSIONAL",
            "idempotencyKey": f"plan-{tenant_id}",
            "active": True,
            "features": ["legal.core"],
            "metadata": {
                "certificate":
                    "LEGAL-COMMERCIAL-CONTEXT-REAL-MONGO",
            },
            "tags": ["legal-commercial-context"],
            "user": "LEGAL-COMMERCIAL-CERT",
        }
    )
    assert result["success"] is True
    return result["plan"]


def _subscription(
    tenant_id: str,
    plan_id: str,
) -> Any:
    """Persist exact canonical ACTIVE Legal subscription truth."""
    result = SubscriptionRegistry.create(
        {
            "tenantId": tenant_id,
            "planId": plan_id,
            "startDate": NOW.isoformat(),
            "idempotencyKey": f"subscription-{tenant_id}",
            "billingMode": "PLATFORM",
            "metadata": {
                "certificate":
                    "LEGAL-COMMERCIAL-CONTEXT-REAL-MONGO",
            },
        },
        tenant_id_header=tenant_id,
    )
    assert result["success"] is True
    value = result["subscription"]
    assert value.status is SubscriptionStatus.ACTIVE
    assert value.plan is PlanTiers.PROFESSIONAL
    assert value.billing_frequency is BillingFrequency.ANNUAL
    assert "legal.core" in value.plan_features
    return value


def _activate_entitlement(
    client: MongoClient[Any],
    collections: dict[str, Any],
    tenant_id: str,
) -> Any:
    """Persist PENDING then ACTIVE current entitlement in caller-owned txs."""
    entitlement_id = derive_tenant_product_entitlement_id(
        tenant_id,
        TenantProductId.LEGAL_OPERATIONS,
    )
    pending = create_tenant_product_entitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
        product_id=TenantProductId.LEGAL_OPERATIONS,
        source_evidence_reference=f"subscription-{tenant_id}",
        source_evidence_fingerprint=FP,
    )

    with client.start_session() as session:
        with session.start_transaction():
            created = entitlement_registry.create_or_replay(
                pending,
                collections["history"],
                collections["current"],
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            activated = entitlement_registry.transition(
                tenant_id=tenant_id,
                entitlement_id=entitlement_id,
                target_state=TenantProductEntitlementState.ACTIVE,
                expected_revision=created.entitlement.lifecycle_revision,
                evidence_reference=f"activation-{tenant_id}",
                evidence_fingerprint=FP,
                occurred_at=NOW,
                history_collection=collections["history"],
                current_collection=collections["current"],
                session=session,
            )

    assert (
        activated.entitlement.lifecycle_state
        is TenantProductEntitlementState.ACTIVE
    )
    return activated.entitlement


def _project(
    client: MongoClient[Any],
    collections: dict[str, Any],
    tenant_id: str,
) -> Any:
    """Resolve one exact commercial snapshot inside caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return resolve_legal_commercial_context(
                tenant_id,
                collections["subscriptions"],
                collections["history"],
                collections["current"],
                session=session,
            )


def test_real_active_subscription_and_entitlement_project_exact_context(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Prove exact durable subscription + entitlement conjunction."""
    client, _database, collections = mongo_context
    tenant_id = f"tenant-commercial-{uuid4().hex}"

    plan = _plan(tenant_id)
    subscription = _subscription(
        tenant_id,
        plan.plan_id,
    )
    entitlement = _activate_entitlement(
        client,
        collections,
        tenant_id,
    )

    projected = _project(
        client,
        collections,
        tenant_id,
    )

    assert projected.tenant_id == tenant_id
    assert projected.product_id is TenantProductId.LEGAL_OPERATIONS
    assert projected.product_available is True
    assert projected.entitlement_id == entitlement.entitlement_id
    assert (
        projected.entitlement_state
        is TenantProductEntitlementState.ACTIVE
    )
    assert projected.subscription_id == subscription.subscription_id
    assert projected.subscription_status is SubscriptionStatus.ACTIVE
    assert projected.plan_id == plan.plan_id
    assert projected.plan_tier is PlanTiers.PROFESSIONAL
    assert projected.plan_name == plan.name
    assert projected.plan_features == tuple(plan.features)
    assert projected.plan_catalogue_version == plan.catalogue_version
    assert projected.amount == 14400.0
    assert projected.currency == "ZAR"
    assert projected.billing_frequency is BillingFrequency.ANNUAL
    assert projected.monthly_equivalent_amount == 1200.0


def test_real_foreign_tenant_cannot_reuse_commercial_truth(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Foreign tenant projection sees lawful absence, never another tenant."""
    client, _database, collections = mongo_context
    tenant_a = f"tenant-a-{uuid4().hex}"
    tenant_b = f"tenant-b-{uuid4().hex}"

    plan = _plan(tenant_a)
    _subscription(tenant_a, plan.plan_id)
    _activate_entitlement(client, collections, tenant_a)

    projected = _project(
        client,
        collections,
        tenant_b,
    )

    assert projected.tenant_id == tenant_b
    assert projected.product_available is False
    assert projected.subscription_id is None
    assert projected.plan_id is None
    assert projected.amount is None


def test_real_active_entitlement_without_subscription_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Durable ACTIVE entitlement cannot mask absent subscription truth."""
    client, _database, collections = mongo_context
    tenant_id = f"tenant-no-subscription-{uuid4().hex}"

    _activate_entitlement(
        client,
        collections,
        tenant_id,
    )

    with pytest.raises(
        LegalCommercialContextProjectionError
    ) as raised:
        _project(
            client,
            collections,
            tenant_id,
        )

    assert (
        raised.value.code
        == "LEGAL_COMMERCIAL_ENTITLEMENT_WITHOUT_ACTIVE_SUBSCRIPTION"
    )


def test_real_active_subscription_without_entitlement_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Durable ACTIVE subscription cannot masquerade as product availability."""
    client, _database, collections = mongo_context
    tenant_id = f"tenant-no-entitlement-{uuid4().hex}"

    plan = _plan(tenant_id)
    _subscription(
        tenant_id,
        plan.plan_id,
    )

    with pytest.raises(
        LegalCommercialContextProjectionError
    ) as raised:
        _project(
            client,
            collections,
            tenant_id,
        )

    assert (
        raised.value.code
        == "LEGAL_COMMERCIAL_ACTIVE_SUBSCRIPTION_WITHOUT_ENTITLEMENT"
    )


def test_real_inactive_session_is_not_accepted_as_product_authority(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Exact transaction requirement remains enforced by current entitlement read."""
    client, _database, collections = mongo_context
    tenant_id = f"tenant-inactive-session-{uuid4().hex}"

    plan = _plan(tenant_id)
    _subscription(
        tenant_id,
        plan.plan_id,
    )
    _activate_entitlement(
        client,
        collections,
        tenant_id,
    )

    with client.start_session() as session:
        assert session.in_transaction is False
        with pytest.raises(
            LegalCommercialContextProjectionError
        ) as raised:
            resolve_legal_commercial_context(
                tenant_id,
                collections["subscriptions"],
                collections["history"],
                collections["current"],
                session=session,
            )

    assert (
        raised.value.code
        == "LEGAL_COMMERCIAL_PRODUCT_AUTHORITY_UNAVAILABLE"
    )


def test_real_projection_is_read_only_and_creates_no_extra_rows(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Repeated projection does not mutate subscription or entitlement evidence."""
    client, _database, collections = mongo_context
    tenant_id = f"tenant-read-only-{uuid4().hex}"

    plan = _plan(tenant_id)
    _subscription(
        tenant_id,
        plan.plan_id,
    )
    _activate_entitlement(
        client,
        collections,
        tenant_id,
    )

    before = (
        collections["subscriptions"].count_documents(
            {"tenant_id": tenant_id}
        ),
        collections["history"].count_documents(
            {"tenant_id": tenant_id}
        ),
        collections["current"].count_documents(
            {"tenant_id": tenant_id}
        ),
    )

    first = _project(client, collections, tenant_id)
    second = _project(client, collections, tenant_id)

    after = (
        collections["subscriptions"].count_documents(
            {"tenant_id": tenant_id}
        ),
        collections["history"].count_documents(
            {"tenant_id": tenant_id}
        ),
        collections["current"].count_documents(
            {"tenant_id": tenant_id}
        ),
    )

    assert first == second
    assert before == after == (1, 2, 1)


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_commercial_context_projection_real_mongo.py
# VERSION: v1.0.0-LEGAL-COMMERCIAL-CONTEXT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo certification evidence only; no runtime authority
# TENANT POSTURE: UUID-isolated exact-tenant subscription and entitlement evidence
# FAIL-CLOSED POSTURE: isolation, mismatch and inactive transaction reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
