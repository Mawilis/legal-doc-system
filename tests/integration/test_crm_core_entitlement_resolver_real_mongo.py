# -*- coding: utf-8 -*-
"""
WILSY OS — CRM Core Entitlement Resolver Real-Mongo Certification.

TITLE:
    WILSY OS CRM Core Entitlement Resolver Real-Mongo Certification

VERSION:
    v1.0.0-P0-CRM-CORE-ENTITLEMENT-RESOLVER-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Certifies that server-derived, tenant-bound, persisted SubscriptionRegistry
    truth in actual MongoDB resolves to crm.core entitlement without caller-
    asserted commercial authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_crm_core_entitlement_resolver_real_mongo.py

CERTIFICATION / UPDATE DATE:
    2026-10-07

SOURCE OF COMMERCIAL TRUTH:
    PlanRegistry -> SubscriptionRegistry persisted immutable plan snapshot.

CERTIFIED:
    - exact crm.core persisted feature resolves;
    - persisted canonical uppercase SubscriptionEntity proof is accepted;
    - activation evidence is lowercase SHA3-512 of exact proof bytes;
    - zero ACTIVE subscription denies;
    - ACTIVE subscription without exact crm.core denies;
    - multiple ACTIVE rows fail closed as SUBSCRIPTION_AMBIGUOUS;
    - neighboring tenant subscription cannot authorize the requested tenant;
    - caller-owned Mongo session is accepted by the resolver read seam;
    - caller command does not provide plan_features or catalogue version.

NOT CERTIFIED:
    - transactional subscription creation;
    - HTTP/BFF routes;
    - UI;
    - trial commercialization policy;
    - payment, settlement or financial execution.

FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as registry_module
from tools.eos.crm.domain.crm_core_entitlement import (
    CRM_CORE_FEATURE_ID,
    CrmCoreEntitlementState,
)
from tools.eos.crm.service.crm_core_entitlement_resolver import (
    CrmCoreEntitlementResolverError,
    resolve_crm_core_entitlement,
)
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry

VERSION = (
    "v1.0.0-P0-CRM-CORE-ENTITLEMENT-RESOLVER-REAL-MONGO-CERT"
)

CERT_URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_CERT_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

TEST_MONGO_URI = os.getenv(
    CERT_URI_ENV,
    DEFAULT_CERT_URI,
)


class _MongoContext:
    def __init__(
        self,
        *,
        client: MongoClient[Any],
        subscriptions: Collection[dict[str, Any]],
        plans: Collection[dict[str, Any]],
        database_name: str,
    ) -> None:
        self.client = client
        self.subscriptions = subscriptions
        self.plans = plans
        self.database_name = database_name


def _plan(
    *,
    tenant_id: str | None,
    features: tuple[str, ...],
    plan_type: str = "ENTERPRISE",
) -> Any:
    material = (
        f"{tenant_id or 'GLOBAL'}|"
        f"{plan_type}|"
        f"{'|'.join(features)}|"
        f"{uuid.uuid4().hex}"
    )

    digest = hashlib.sha3_256(
        material.encode("utf-8")
    ).hexdigest().upper()

    plan_id = (
        "WILSYPLAN-CRMCORE-"
        + digest[:16]
    )

    payload: dict[str, Any] = {
        "name": "CRM Core Certificate Plan",
        "description": (
            "Synthetic CRM Core real-Mongo certificate plan."
        ),
        "price": 499,
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "planType": plan_type,
        "idempotencyKey": (
            "CRM-CORE-PLAN-"
            + digest[:24]
        ),
        "plan_id": plan_id,
        "active": True,
        "features": list(features),
        "metadata": {
            "certificate": True,
            "catalogueAuthority": "PlanRegistry",
        },
        "tags": [
            "crm-core-resolver-cert",
        ],
        "user": "CRM-CORE-RESOLVER-CERT",
    }

    if tenant_id is not None:
        payload["tenantId"] = tenant_id

    result = PlanRegistry.create(payload)

    assert result["success"] is True
    return result["plan"]


def _subscription_command(
    tenant_id: str,
    plan_id: str,
    *,
    key: str,
) -> dict[str, Any]:
    command: dict[str, Any] = {
        "tenantId": tenant_id,
        "planId": plan_id,
        "startDate": "2026-10-07T06:00:00+00:00",
        "idempotencyKey": key,
        "billingMode": "PLATFORM",
        "onboardingRef": f"CRM-CORE-{tenant_id}",
        "sector": "LEGAL",
        "region": "ZA",
        "metadata": {
            "certificate": True,
        },
    }

    assert "plan_features" not in command
    assert "planFeatures" not in command
    assert "plan_catalogue_version" not in command
    assert "planCatalogueVersion" not in command
    assert "amount" not in command
    assert "currency" not in command
    assert "billingFrequency" not in command
    assert "planType" not in command

    return command


def _create_subscription(
    tenant_id: str,
    features: tuple[str, ...],
    *,
    key: str,
) -> Any:
    plan = _plan(
        tenant_id=None,
        features=features,
    )

    result = SubscriptionRegistry.create(
        _subscription_command(
            tenant_id,
            plan.plan_id,
            key=key,
        ),
        tenant_id_header=tenant_id,
    )

    assert result["success"] is True
    assert result["replayed"] is False

    subscription = result["subscription"]

    assert subscription.tenant_id == tenant_id
    assert subscription.plan_id == plan.plan_id
    assert subscription.plan_features == tuple(plan.features)
    assert (
        subscription.plan_catalogue_version
        == plan.catalogue_version
    )

    assert subscription.proof_hash
    assert len(subscription.proof_hash) == 128
    assert (
        subscription.proof_hash
        == subscription.proof_hash.upper()
    )
    assert all(
        character in "0123456789ABCDEF"
        for character in subscription.proof_hash
    )

    return subscription


@pytest.fixture(scope="module")
def mongo_context() -> Iterator[_MongoContext]:
    client: MongoClient[Any] = MongoClient(
        TEST_MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    client.admin.command("ping")

    hello = client.admin.command("hello")

    if hello.get("setName") != EXPECTED_REPLICA_SET:
        raise RuntimeError(
            "CRM_CORE_RESOLVER_CERT_WRONG_MONGO_TOPOLOGY"
        )

    database_name = (
        "wilsy_crmcore_cert_"
        + uuid.uuid4().hex
    )

    assert len(database_name.encode("utf-8")) <= 63

    database = client[database_name]

    subscriptions: Collection[dict[str, Any]] = (
        database.get_collection(
            "subscriptions",
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
            read_concern=ReadConcern(
                "majority"
            ),
        )
    )

    plans: Collection[dict[str, Any]] = (
        database.get_collection(
            "plans",
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
            read_concern=ReadConcern(
                "majority"
            ),
        )
    )

    original_subscriptions = (
        registry_module.subscriptions_collection
    )
    original_plans = (
        plan_registry_module.plans_collection
    )

    registry_module.subscriptions_collection = subscriptions
    plan_registry_module.plans_collection = plans

    PlanRegistry._ensure_indexes()

    bootstrap_tenant = (
        "tenant-bootstrap-"
        + uuid.uuid4().hex
    )

    bootstrap_plan = _plan(
        tenant_id=None,
        features=(CRM_CORE_FEATURE_ID,),
    )

    bootstrap = SubscriptionRegistry.create(
        _subscription_command(
            bootstrap_tenant,
            bootstrap_plan.plan_id,
            key="bootstrap-crm-core",
        ),
        tenant_id_header=bootstrap_tenant,
    )

    assert bootstrap["success"] is True

    subscriptions.delete_many({})
    plans.delete_many({})

    context = _MongoContext(
        client=client,
        subscriptions=subscriptions,
        plans=plans,
        database_name=database_name,
    )

    try:
        yield context
    finally:
        registry_module.subscriptions_collection = (
            original_subscriptions
        )
        plan_registry_module.plans_collection = (
            original_plans
        )

        client.drop_database(database_name)

        assert (
            database_name
            not in client.list_database_names()
        )

        client.close()


@pytest.fixture(autouse=True)
def clean_database(
    mongo_context: _MongoContext,
) -> Iterator[None]:
    mongo_context.subscriptions.delete_many({})
    mongo_context.plans.delete_many({})

    yield

    mongo_context.subscriptions.delete_many({})
    mongo_context.plans.delete_many({})


def _resolve(
    context: _MongoContext,
    tenant_id: str,
):
    with context.client.start_session() as session:
        assert isinstance(session, ClientSession)

        return resolve_crm_core_entitlement(
            tenant_id,
            context.subscriptions,
            session,
        )


def test_real_mongo_exact_crm_core_subscription_resolves(
    mongo_context: _MongoContext,
) -> None:
    tenant = "tenant-" + uuid.uuid4().hex

    subscription = _create_subscription(
        tenant,
        (
            CRM_CORE_FEATURE_ID,
            "legal.documents",
        ),
        key="crm-core-positive",
    )

    persisted = mongo_context.subscriptions.find_one(
        {
            "tenant_id": tenant,
            "subscription_id":
                subscription.subscription_id,
        }
    )

    assert persisted is not None
    assert CRM_CORE_FEATURE_ID in persisted["plan_features"]
    assert (
        persisted["plan_catalogue_version"]
        == subscription.plan_catalogue_version
    )
    assert (
        persisted["proof_hash"]
        == subscription.proof_hash
    )

    result = _resolve(
        mongo_context,
        tenant,
    )

    assert result is not None
    assert result.tenant_id == tenant
    assert result.subscription_id == subscription.subscription_id
    assert result.plan_id == subscription.plan_id
    assert (
        result.plan_catalogue_version
        == subscription.plan_catalogue_version
    )
    assert result.subscription_proof_hash == subscription.proof_hash
    assert result.lifecycle_state is CrmCoreEntitlementState.ACTIVE

    expected_activation = hashlib.sha3_512(
        subscription.proof_hash.encode("ascii")
    ).hexdigest()

    assert (
        result.activation_evidence_fingerprint
        == expected_activation
    )
    assert (
        result.activation_evidence_fingerprint
        != subscription.proof_hash
    )


def test_real_mongo_zero_active_subscription_denies(
    mongo_context: _MongoContext,
) -> None:
    tenant = "tenant-" + uuid.uuid4().hex

    result = _resolve(
        mongo_context,
        tenant,
    )

    assert result is None


def test_real_mongo_active_without_exact_crm_core_denies(
    mongo_context: _MongoContext,
) -> None:
    tenant = "tenant-" + uuid.uuid4().hex

    _create_subscription(
        tenant,
        (
            "crm.analytics",
            "legal.documents",
        ),
        key="crm-core-absent",
    )

    result = _resolve(
        mongo_context,
        tenant,
    )

    assert result is None


def test_real_mongo_multiple_active_subscriptions_fail_closed(
    mongo_context: _MongoContext,
) -> None:
    tenant = "tenant-" + uuid.uuid4().hex

    _create_subscription(
        tenant,
        (
            CRM_CORE_FEATURE_ID,
        ),
        key="crm-core-ambiguous-a",
    )

    _create_subscription(
        tenant,
        (
            CRM_CORE_FEATURE_ID,
            "legal.documents",
        ),
        key="crm-core-ambiguous-b",
    )

    with pytest.raises(
        CrmCoreEntitlementResolverError,
        match=(
            "CRM_CORE_ENTITLEMENT_SUBSCRIPTION_AMBIGUOUS"
        ),
    ):
        _resolve(
            mongo_context,
            tenant,
        )


def test_real_mongo_neighbor_subscription_cannot_authorize_tenant(
    mongo_context: _MongoContext,
) -> None:
    tenant_a = "tenant-" + uuid.uuid4().hex
    tenant_b = "tenant-" + uuid.uuid4().hex

    _create_subscription(
        tenant_b,
        (
            CRM_CORE_FEATURE_ID,
        ),
        key="crm-core-neighbor",
    )

    result = _resolve(
        mongo_context,
        tenant_a,
    )

    assert result is None

    assert (
        mongo_context.subscriptions.count_documents(
            {"tenant_id": tenant_b}
        )
        == 1
    )


def test_real_mongo_persisted_subscription_is_server_derived(
    mongo_context: _MongoContext,
) -> None:
    tenant = "tenant-" + uuid.uuid4().hex

    plan = _plan(
        tenant_id=None,
        features=(
            CRM_CORE_FEATURE_ID,
            "legal.documents",
        ),
    )

    command = _subscription_command(
        tenant,
        plan.plan_id,
        key="crm-core-server-derived",
    )

    created = SubscriptionRegistry.create(
        command,
        tenant_id_header=tenant,
    )

    assert created["success"] is True

    subscription = created["subscription"]

    persisted = mongo_context.subscriptions.find_one(
        {
            "tenant_id": tenant,
            "subscription_id":
                subscription.subscription_id,
        }
    )

    assert persisted is not None
    assert persisted["plan_features"] == list(plan.features)
    assert (
        persisted["plan_catalogue_version"]
        == plan.catalogue_version
    )

    assert "plan_features" not in command
    assert "plan_catalogue_version" not in command
    assert "amount" not in command
    assert "currency" not in command


# ARTIFACT: test_crm_core_entitlement_resolver_real_mongo.py
# VERSION: v1.0.0-P0-CRM-CORE-ENTITLEMENT-RESOLVER-REAL-MONGO-CERT
# AUTHORITY SOURCE: PlanRegistry -> SubscriptionRegistry persisted tenant truth
# DATABASE: UUID-isolated actual MongoDB replica-set certificate
# TRANSACTION: resolver read accepts exact caller-owned ClientSession
# FINANCIAL EXECUTION: NONE; Kennel EOS remains exclusive
# NODE CRM AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN CERTIFICATE
