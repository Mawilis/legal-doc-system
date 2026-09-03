# -*- coding: utf-8 -*-
"""WILSY OS — SubscriptionRegistry real-Mongo certification.

TITLE:
    WILSY OS Subscription Registry Real-Mongo Certification

VERSION:
    v1.2.1-SUBSCRIPTION-CALENDAR-BILLING-CERT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Executes the canonical SubscriptionRegistry against an actual MongoDB
    server and a UUID-isolated certification database. Certifies durable
    create/read/update/lifecycle behavior, tenant isolation, exact replay vs
    idempotency conflict, invalid persisted truth, infrastructure failure,
    deterministic indexes and independent-client restart durability.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_subscription_registry_real_mongo.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-09-03

CHANGELOG:
    v1.2.1-SUBSCRIPTION-CALENDAR-BILLING-CERT:
        - Corrects the synthetic legacy-period replay fixture to persist
          canonical registry ISO datetime strings rather than direct BSON
          datetime values.
        - Preserves explicit timezone offsets through canonical hydration while
          still certifying exact historical replay and changed-key conflict
          non-mutation.

    v1.2.0-SUBSCRIPTION-CALENDAR-BILLING-CERT:
        - Certifies actual-Mongo server-derived calendar period persistence.
        - Certifies new caller period redirection fails before persistence.
        - Certifies generic update cannot replace period coordinates.
        - Certifies naive startDate fails closed.
        - Certifies historical exact period-bearing command replay survives only
          for an exact stored command fingerprint; changed reuse conflicts.
        - Preserves catalogue provenance, tenant isolation and Kennel boundary.

    v1.1.0-SUBSCRIPTION-CATALOGUE-PROVENANCE-CERT:
        - Binds SubscriptionRegistry and PlanRegistry to the same UUID-isolated
          actual-Mongo certification database.
        - Replaces caller-authored price/currency/frequency/features with
          planId-only commercial selection.
        - Certifies global and tenant catalogue selection, neighbor-plan denial,
          inactive-plan denial and explicit catalogue outage.
        - Certifies persisted plan name/features/catalogue-version snapshot.
        - Certifies generic commercial update redirection is denied.
        - Certifies upgrade/downgrade derive all commercial truth from
          PlanRegistry by newPlanId only.

    v1.0.2-SUBSCRIPTION-REGISTRY-REAL-MONGO-CERT:
        - Certifies complete SHA3-512 fingerprint syntax validation.
        - Certifies persisted canonical create-material digest recomputation.
        - Certifies tampered create material fails closed.
        - Certifies actual Mongo subscription-ID duplicate classification.
        - Certifies same idempotency key remains independent across tenants.
        - Closes Codex findings VAS13-001 and VAS13-002.

    v1.0.1-SUBSCRIPTION-REGISTRY-REAL-MONGO-CERT:
        - Aligns the certificate with the repository-standard disposable
          real-Mongo certification topology.
        - Uses TEST_VENDOR_MONGO_URI as the canonical environment contract.
        - Defaults only to local port 27027 / wilsyVendorCertRS.
        - Explicitly verifies replica-set identity before certification.
        - Rejects accidental use of the authentication-required port 27017
          topology as a valid subscription persistence certificate target.
        - Preserves the MongoDB 63-byte certification namespace constraint.

    v1.0.0-SUBSCRIPTION-REGISTRY-REAL-MONGO-CERT:
        - Initial actual-Mongo subscription persistence certificate.
        - Uses UUID-isolated database and deterministic cleanup.
        - Constrains certification database names to MongoDB's 63-byte limit.
        - No mongomock, fake collection, in-memory registry or skip-on-outage.
        - Certifies exact idempotent replay and conflicting-key rejection.
        - Certifies tenant isolation and neighboring-tenant preservation.
        - Certifies invalid persisted truth and real network failure semantics.
        - Certifies independent-client restart durability.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001-aligned tenant-isolation certification.

SECURITY / PRIVACY POSTURE:
    Uses synthetic tenant/subscription identifiers in an isolated test database.
    No production tenant, payment destination, credential, settlement record or
    production evidence is created.

TENANT BOUNDARY:
    Every registry operation uses an explicit synthetic tenant scope. Tests
    prove cross-tenant absence and neighboring-tenant preservation.

AUTHORITY BOUNDARY:
    Certifies real subscription persistence only. It does not certify the
    current HTTP subscription router's raw-header authorization posture. Router
    authority rewiring remains a separate production barrier.

FINANCIAL AUTHORITY BOUNDARY:
    No payment execution or settlement is tested or inferred.
    Kennel EOS remains exclusive financial execution authority.

CERTIFICATION CLASSIFICATION:
    REAL DATABASE / PERSISTENCE / TENANT-ISOLATION CERTIFICATE.

CONSTITUTION:
    Local Mongo unavailability is test FAILURE, never PASS or SKIP.
"""

from __future__ import annotations

import copy
import hashlib
import os
import subprocess
import sys
import uuid
from unittest.mock import patch
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as registry
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry,
    SubscriptionRegistryError,
    VERSION as REGISTRY_VERSION,
)


TEST_VERSION = (
    "v1.2.1-SUBSCRIPTION-CALENDAR-BILLING-CERT"
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

_ROOT = Path(__file__).resolve().parents[2]


class _MongoContext:
    """Hold one isolated actual-Mongo certification database."""

    def __init__(
        self,
        *,
        client: MongoClient[Any],
        collection: Collection[dict[str, Any]],
        plans: Collection[dict[str, Any]],
        database_name: str,
        database_uri: str,
    ) -> None:
        self.client = client
        self.collection = collection
        self.plans = plans
        self.database_name = database_name
        self.database_uri = database_uri


def _database_uri(
    uri: str,
    database_name: str,
) -> str:
    """Replace any URI database path while preserving query options."""
    base, separator, query = uri.partition("?")
    prefix = base.rsplit("/", 1)[0]
    resolved = f"{prefix}/{database_name}"

    if separator:
        resolved += f"?{query}"

    return resolved


def _plan_identity(
    *,
    plan: str,
    amount: float,
    tenant_id: str | None,
    active: bool,
) -> tuple[str, str]:
    """Return deterministic synthetic Plan identity and idempotency evidence."""
    material = (
        f"{tenant_id or 'GLOBAL'}"
        f"|{plan.upper()}"
        f"|{float(amount):.6f}"
        f"|{active}"
    )

    digest = hashlib.sha3_256(
        material.encode("utf-8")
    ).hexdigest().upper()

    return (
        "WILSYPLAN-CERT" + digest[:16],
        "PLAN-CERT-" + digest[:24],
    )


def _seed_plan(
    *,
    plan: str = "ENTERPRISE",
    amount: float = 499.0,
    tenant_id: str | None = None,
    active: bool = True,
    features: tuple[str, ...] = (
        "crm.core",
        "legal.documents",
    ),
):
    """Persist one canonical synthetic PlanRegistry catalogue entry."""
    plan_id, idempotency_key = _plan_identity(
        plan=plan,
        amount=amount,
        tenant_id=tenant_id,
        active=active,
    )

    existing = PlanRegistry.get(
        plan_id,
        tenant_id=tenant_id,
    )

    if existing is not None:
        return existing

    payload: dict[str, Any] = {
        "name": f"Certificate {plan.title()}",
        "price": amount,
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "planType": plan,
        "idempotencyKey": idempotency_key,
        "plan_id": plan_id,
        "active": active,
        "features": list(features),
        "metadata": {
            "certificate": True,
            "catalogueAuthority": "PlanRegistry",
        },
        "tags": [
            "subscription-catalogue-cert"
        ],
        "user": "SUBSCRIPTION-CATALOGUE-CERT",
    }

    if tenant_id is not None:
        payload["tenantId"] = tenant_id

    result = PlanRegistry.create(
        payload
    )

    assert result["success"] is True

    return result["plan"]


def _command(
    tenant_id: str,
    idempotency_key: str,
    *,
    plan_id: str,
) -> dict[str, Any]:
    """Build a subscription command containing selection, not catalogue truth."""
    return {
        "tenantId": tenant_id,
        "planId": plan_id,
        "startDate": "2026-09-03T10:00:00+00:00",
        "idempotencyKey": idempotency_key,
        "billingMode": "PLATFORM",
        "onboardingRef":
            f"ONBOARD-{tenant_id}",
        "sector": "LEGAL",
        "region": "ZA",
        "metadata": {
            "certificate": True
        },
    }


def _payload(
    tenant_id: str,
    idempotency_key: str,
    *,
    amount: float = 499.0,
    plan: str = "ENTERPRISE",
) -> dict[str, Any]:
    """Build a command selecting a real canonical global PlanRegistry row."""
    catalogue_plan = _seed_plan(
        plan=plan,
        amount=amount,
        tenant_id=None,
        active=True,
    )

    return _command(
        tenant_id,
        idempotency_key,
        plan_id=catalogue_plan.plan_id,
    )

@pytest.fixture(scope="module")
def mongo_context() -> Iterator[_MongoContext]:
    """Bind the registry to one UUID-isolated actual Mongo database."""
    client: MongoClient[Any] = MongoClient(
        TEST_MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    # Deliberately no skip. Environment failure is certification failure.
    client.admin.command("ping")

    hello = client.admin.command("hello")

    if hello.get("setName") != EXPECTED_REPLICA_SET:
        raise RuntimeError(
            "SUBSCRIPTION_CERT_WRONG_MONGO_TOPOLOGY"
        )

    database_name = (
        "wilsy_sub_cert_"
        + uuid.uuid4().hex
    )

    database = client[database_name]

    collection: Collection[dict[str, Any]] = (
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

    original_collection = (
        registry.subscriptions_collection
    )

    original_plan_collection = (
        plan_registry_module.plans_collection
    )

    registry.subscriptions_collection = (
        collection
    )

    plan_registry_module.plans_collection = (
        plans
    )

    PlanRegistry._ensure_indexes()

    # Bootstrap indexes through the public create path, then clean.
    bootstrap_tenant = (
        "tenant-bootstrap-"
        + uuid.uuid4().hex
    )

    bootstrap = SubscriptionRegistry.create(
        _payload(
            bootstrap_tenant,
            "bootstrap-idempotency",
        ),
        tenant_id_header=
            bootstrap_tenant,
    )

    assert bootstrap["success"] is True

    collection.delete_many({})

    context = _MongoContext(
        client=client,
        collection=collection,
        plans=plans,
        database_name=database_name,
        database_uri=_database_uri(
            TEST_MONGO_URI,
            database_name,
        ),
    )

    try:
        yield context
    finally:
        registry.subscriptions_collection = (
            original_collection
        )
        plan_registry_module.plans_collection = (
            original_plan_collection
        )
        client.drop_database(
            database_name
        )
        assert (
            database_name
            not in client.list_database_names()
        )
        client.close()


@pytest.fixture(autouse=True)
def clean_collection(
    mongo_context: _MongoContext,
) -> Iterator[None]:
    """Ensure each certificate starts and ends with empty Mongo truth."""
    mongo_context.collection.delete_many({})
    mongo_context.plans.delete_many({})
    yield
    mongo_context.collection.delete_many({})
    mongo_context.plans.delete_many({})


def test_real_mongo_version_database_and_index_contract(
    mongo_context: _MongoContext,
) -> None:
    """Prove actual Mongo, isolated database and deterministic indexes."""
    assert (
        REGISTRY_VERSION
        == "v1.3.0-CALENDAR-BILLING-WIRING"
    )
    assert (
        TEST_VERSION
        == "v1.2.1-SUBSCRIPTION-CALENDAR-BILLING-CERT"
    )

    mongo_context.client.admin.command(
        "ping"
    )

    hello = mongo_context.client.admin.command(
        "hello"
    )

    assert (
        hello.get("setName")
        == EXPECTED_REPLICA_SET
    )

    assert (
        CERT_URI_ENV
        == "TEST_VENDOR_MONGO_URI"
    )

    assert mongo_context.database_name.startswith(
        "wilsy_sub_cert_"
    )

    suffix = (
        mongo_context.database_name
        .removeprefix(
            "wilsy_sub_cert_"
        )
    )
    assert len(suffix) == 32
    int(suffix, 16)

    # MongoDB database names must remain <= 63 bytes.
    assert (
        len(
            mongo_context.database_name.encode(
                "utf-8"
            )
        )
        <= 63
    )

    indexes = (
        mongo_context.collection
        .index_information()
    )

    assert "tenant_subscription_unique" in indexes
    assert "tenant_idempotency_unique" in indexes
    assert "tenant_status" in indexes
    assert "tenant_plan" in indexes


def test_real_mongo_create_persists_and_round_trips(
    mongo_context: _MongoContext,
) -> None:
    """Create through registry and hydrate the same persisted truth."""
    tenant_id = (
        "tenant-"
        + uuid.uuid4().hex
    )

    result = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "create-round-trip",
        ),
        tenant_id_header=tenant_id,
    )

    assert result["success"] is True
    assert result["replayed"] is False

    entity = result["subscription"]

    persisted = (
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_id,
                "subscription_id":
                    entity.subscription_id,
            },
            {"_id": 0},
        )
    )

    assert persisted is not None
    assert (
        persisted["_registry_schema"]
        == "WILSY-SUBSCRIPTION-REGISTRY/V1"
    )
    assert persisted["_registry_revision"] == 1
    assert (
        persisted[
            "_registry_create_fingerprint"
        ].startswith("sha3-512:")
    )

    loaded = SubscriptionRegistry.get(
        entity.subscription_id,
        tenant_id_header=tenant_id,
    )

    assert loaded is not None
    assert (
        loaded.to_dict()
        == entity.to_dict()
    )


def test_real_mongo_exact_idempotency_replays_exact_entity(
    mongo_context: _MongoContext,
) -> None:
    """Same tenant/key/command returns the durable original entity."""
    tenant_id = (
        "tenant-"
        + uuid.uuid4().hex
    )

    payload = _payload(
        tenant_id,
        "exact-replay",
    )

    first = SubscriptionRegistry.create(
        payload,
        tenant_id_header=tenant_id,
    )
    second = SubscriptionRegistry.create(
        payload,
        tenant_id_header=tenant_id,
    )

    assert first["success"] is True
    assert second["success"] is True
    assert first["replayed"] is False
    assert second["replayed"] is True

    assert (
        first["subscription"].subscription_id
        == second["subscription"].subscription_id
    )

    assert (
        first["subscription"].to_dict()
        == second["subscription"].to_dict()
    )

    assert (
        mongo_context.collection.count_documents(
            {
                "tenant_id": tenant_id,
                "idempotency_key":
                    "exact-replay",
            }
        )
        == 1
    )


def test_real_mongo_idempotency_conflict_fails_without_mutation(
    mongo_context: _MongoContext,
) -> None:
    """Same key with different canonical command fails closed."""
    tenant_id = (
        "tenant-"
        + uuid.uuid4().hex
    )

    first = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "conflicting-key",
            amount=499.0,
        ),
        tenant_id_header=tenant_id,
    )

    assert first["success"] is True

    before = copy.deepcopy(
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_id,
                "idempotency_key":
                    "conflicting-key",
            },
            {"_id": 0},
        )
    )

    conflict = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "conflicting-key",
            amount=999.0,
        ),
        tenant_id_header=tenant_id,
    )

    assert conflict == {
        "success": False,
        "error":
            "SUBSCRIPTION_IDEMPOTENCY_CONFLICT",
    }

    after = (
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_id,
                "idempotency_key":
                    "conflicting-key",
            },
            {"_id": 0},
        )
    )

    assert after == before


def test_real_mongo_tenant_isolation_and_missing_scope_fail_closed(
    mongo_context: _MongoContext,
) -> None:
    """Wrong tenant sees absence; missing tenant never becomes global scope."""
    tenant_a = (
        "tenant-a-"
        + uuid.uuid4().hex
    )
    tenant_b = (
        "tenant-b-"
        + uuid.uuid4().hex
    )

    created = SubscriptionRegistry.create(
        _payload(
            tenant_a,
            "tenant-isolation",
        ),
        tenant_id_header=tenant_a,
    )

    assert created["success"] is True

    subscription_id = (
        created["subscription"]
        .subscription_id
    )

    assert (
        SubscriptionRegistry.get(
            subscription_id,
            tenant_id_header=tenant_b,
        )
        is None
    )

    other_list = SubscriptionRegistry.list(
        tenant_id_header=tenant_b,
    )

    assert other_list["items"] == []
    assert other_list["total"] == 0

    with pytest.raises(
        SubscriptionRegistryError,
        match=(
            "^SUBSCRIPTION_REGISTRY_TENANT_REQUIRED$"
        ),
    ):
        SubscriptionRegistry.get(
            subscription_id,
            tenant_id_header=None,
        )

    assert (
        mongo_context.collection.count_documents(
            {"tenant_id": tenant_a}
        )
        == 1
    )


def test_real_mongo_payload_tenant_mismatch_fails_before_write(
    mongo_context: _MongoContext,
) -> None:
    """Payload tenant cannot redirect an already-scoped registry call."""
    tenant_a = (
        "tenant-a-"
        + uuid.uuid4().hex
    )
    tenant_b = (
        "tenant-b-"
        + uuid.uuid4().hex
    )

    result = SubscriptionRegistry.create(
        _payload(
            tenant_b,
            "scope-mismatch",
        ),
        tenant_id_header=tenant_a,
    )

    assert result == {
        "success": False,
        "error":
            "SUBSCRIPTION_TENANT_SCOPE_MISMATCH",
    }

    assert (
        mongo_context.collection.count_documents(
            {}
        )
        == 0
    )


def test_real_mongo_update_and_neighbor_preservation(
    mongo_context: _MongoContext,
) -> None:
    """One tenant mutation persists without altering neighboring truth."""
    tenant_a = (
        "tenant-a-"
        + uuid.uuid4().hex
    )
    tenant_b = (
        "tenant-b-"
        + uuid.uuid4().hex
    )

    created_a = SubscriptionRegistry.create(
        _payload(
            tenant_a,
            "update-a",
        ),
        tenant_id_header=tenant_a,
    )
    created_b = SubscriptionRegistry.create(
        _payload(
            tenant_b,
            "update-b",
        ),
        tenant_id_header=tenant_b,
    )

    assert created_a["success"] is True
    assert created_b["success"] is True

    subscription_a = (
        created_a["subscription"]
        .subscription_id
    )
    subscription_b = (
        created_b["subscription"]
        .subscription_id
    )

    neighbor_before = copy.deepcopy(
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_b,
                "subscription_id":
                    subscription_b,
            },
            {"_id": 0},
        )
    )

    updated = SubscriptionRegistry.update(
        subscription_a,
        {
            "metadata": {
                "updated": True
            },
        },
        tenant_id_header=tenant_a,
    )

    assert updated["success"] is True
    assert (
        updated["subscription"].amount
        == 499.0
    )
    assert (
        updated["subscription"]
        .to_dict()["metadata"]["updated"]
        is True
    )

    persisted_a = (
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_a,
                "subscription_id":
                    subscription_a,
            },
            {"_id": 0},
        )
    )

    neighbor_after = (
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_b,
                "subscription_id":
                    subscription_b,
            },
            {"_id": 0},
        )
    )

    assert persisted_a is not None
    assert persisted_a["amount"] == 499.0
    assert persisted_a["metadata"]["updated"] is True
    assert persisted_a["_registry_revision"] == 2
    assert neighbor_after == neighbor_before


def test_real_mongo_lifecycle_survives_persisted_round_trip(
    mongo_context: _MongoContext,
) -> None:
    """Pause and resume modify durable lifecycle and audit truth."""
    tenant_id = (
        "tenant-"
        + uuid.uuid4().hex
    )

    created = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "lifecycle",
        ),
        tenant_id_header=tenant_id,
    )

    assert created["success"] is True

    subscription_id = (
        created["subscription"]
        .subscription_id
    )

    paused = SubscriptionRegistry.pause(
        subscription_id,
        tenant_id_header=tenant_id,
        pause_reason="certificate",
    )

    assert paused["success"] is True
    assert (
        paused["subscription"].status.value
        == "paused"
    )

    resumed = SubscriptionRegistry.resume(
        subscription_id,
        tenant_id_header=tenant_id,
        metadata={
            "certificate": True
        },
    )

    assert resumed["success"] is True
    assert (
        resumed["subscription"].status.value
        == "active"
    )

    persisted = (
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_id,
                "subscription_id":
                    subscription_id,
            },
            {"_id": 0},
        )
    )

    assert persisted is not None
    assert persisted["status"] == "active"
    assert persisted["_registry_revision"] == 3

    actions = [
        item["action"]
        for item in persisted["audit_trail"]
    ]

    assert actions == [
        "create",
        "pause",
        "resume",
    ]


def test_real_mongo_invalid_persisted_truth_fails_closed(
    mongo_context: _MongoContext,
) -> None:
    """Malformed canonical document is not normalized into healthy truth."""
    tenant_id = (
        "tenant-"
        + uuid.uuid4().hex
    )
    subscription_id = (
        "WILSYSUB-INVALID"
    )

    mongo_context.collection.insert_one(
        {
            "_registry_schema":
                "WILSY-SUBSCRIPTION-REGISTRY/V1",
            "_registry_revision": 1,
            "_registry_create_fingerprint":
                "sha3-512:"
                + ("0" * 128),
            "tenant_id": tenant_id,
            "subscription_id":
                subscription_id,
            "idempotency_key":
                "invalid-document",
        }
    )

    with pytest.raises(
        SubscriptionRegistryError,
        match=(
            "^SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT$"
        ),
    ):
        SubscriptionRegistry.get(
            subscription_id,
            tenant_id_header=tenant_id,
        )


def test_real_mongo_network_failure_is_not_false_absence(
    mongo_context: _MongoContext,
) -> None:
    """Actual unreachable Mongo produces explicit infrastructure failure."""
    unreachable: MongoClient[Any] = (
        MongoClient(
            "mongodb://127.0.0.1:1/wilsy_unreachable",
            serverSelectionTimeoutMS=150,
        )
    )

    dead_collection: Collection[
        dict[str, Any]
    ] = (
        unreachable[
            "wilsy_unreachable"
        ].get_collection(
            "subscriptions"
        )
    )

    original = (
        registry.subscriptions_collection
    )

    registry.subscriptions_collection = (
        dead_collection
    )

    try:
        with pytest.raises(
            SubscriptionRegistryError,
            match=(
                "^SUBSCRIPTION_REGISTRY_UNAVAILABLE$"
            ),
        ):
            SubscriptionRegistry.get(
                "WILSYSUB-NOT-THERE",
                tenant_id_header=
                    "tenant-outage",
            )
    finally:
        registry.subscriptions_collection = (
            original
        )
        unreachable.close()

    # Prove the real certification collection remains intact.
    mongo_context.client.admin.command(
        "ping"
    )


def test_real_mongo_independent_process_restart_durability(
    mongo_context: _MongoContext,
) -> None:
    """A fresh Python process hydrates truth written before process restart."""
    tenant_id = (
        "tenant-"
        + uuid.uuid4().hex
    )

    created = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "restart-durability",
        ),
        tenant_id_header=tenant_id,
    )

    assert created["success"] is True

    subscription_id = (
        created["subscription"]
        .subscription_id
    )

    code = r'''
import sys
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry

subscription_id = sys.argv[1]
tenant_id = sys.argv[2]

entity = SubscriptionRegistry.get(
    subscription_id,
    tenant_id_header=tenant_id,
)

if entity is None:
    raise SystemExit("restart read returned absence")

print(entity.subscription_id)
print(entity.tenant_id)
'''

    environment = os.environ.copy()
    environment[
        "WILSY_SUBSCRIPTION_MONGO_URI"
    ] = mongo_context.database_uri
    environment[
        "WILSY_PLAN_MONGO_URI"
    ] = mongo_context.database_uri

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            code,
            subscription_id,
            tenant_id,
        ],
        cwd=_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
        timeout=15,
    )

    assert completed.returncode == 0, (
        completed.stdout
        + completed.stderr
    )

    output = completed.stdout.splitlines()

    assert subscription_id in output
    assert tenant_id in output


def test_real_mongo_metrics_are_persisted_tenant_truth(
    mongo_context: _MongoContext,
) -> None:
    """MRR/ARR metrics derive from actual persisted tenant subscription rows."""
    tenant_id = (
        "tenant-"
        + uuid.uuid4().hex
    )

    first = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "metrics-a",
            amount=100.0,
        ),
        tenant_id_header=tenant_id,
    )
    second = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "metrics-b",
            amount=200.0,
        ),
        tenant_id_header=tenant_id,
    )

    assert first["success"] is True
    assert second["success"] is True

    metrics = SubscriptionRegistry.get_metrics(
        tenant_id
    )

    assert metrics[
        "totalSubscriptions"
    ] == 2
    assert metrics[
        "activeSubscriptions"
    ] == 2
    assert metrics["totalMRR"] == 300.0
    assert metrics["totalARR"] == 3600.0




def test_real_mongo_fingerprint_integrity_rejects_malformed_and_mismatched_truth(
    mongo_context: _MongoContext,
) -> None:
    """Persisted create evidence must survive strict syntax and digest checks."""
    tenant_id = (
        "tenant-"
        + uuid.uuid4().hex
    )

    created = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "fingerprint-integrity",
        ),
        tenant_id_header=tenant_id,
    )

    assert created["success"] is True

    subscription_id = (
        created["subscription"]
        .subscription_id
    )

    selector = {
        "tenant_id": tenant_id,
        "subscription_id":
            subscription_id,
    }

    original = (
        mongo_context.collection.find_one(
            selector,
            {"_id": 0},
        )
    )

    assert original is not None

    # Wrong alphabet: syntactically invalid SHA3-512.
    mongo_context.collection.update_one(
        selector,
        {
            "$set": {
                "_registry_create_fingerprint":
                    "sha3-512:"
                    + ("g" * 128)
            }
        },
    )

    with pytest.raises(
        SubscriptionRegistryError,
        match=(
            "^SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT$"
        ),
    ):
        SubscriptionRegistry.get(
            subscription_id,
            tenant_id_header=tenant_id,
        )

    # Valid lowercase SHA3-512 syntax but wrong digest.
    mongo_context.collection.update_one(
        selector,
        {
            "$set": {
                "_registry_create_fingerprint":
                    "sha3-512:"
                    + ("0" * 128)
            }
        },
    )

    with pytest.raises(
        SubscriptionRegistryError,
        match=(
            "^SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT$"
        ),
    ):
        SubscriptionRegistry.get(
            subscription_id,
            tenant_id_header=tenant_id,
        )

    # Canonical material alteration with the original digest must fail.
    mongo_context.collection.replace_one(
        selector,
        original,
    )

    material = str(
        original[
            "_registry_create_material"
        ]
    )

    mutated_material = material.replace(
        '"billingMode":"PLATFORM"',
        '"billingMode":"CLIENT"',
        1,
    )

    assert mutated_material != material

    mongo_context.collection.update_one(
        selector,
        {
            "$set": {
                "_registry_create_material":
                    mutated_material
            }
        },
    )

    with pytest.raises(
        SubscriptionRegistryError,
        match=(
            "^SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT$"
        ),
    ):
        SubscriptionRegistry.get(
            subscription_id,
            tenant_id_header=tenant_id,
        )


def test_real_mongo_subscription_id_duplicate_is_not_idempotency_conflict(
    mongo_context: _MongoContext,
) -> None:
    """Actual subscription-identity collision has its own conflict class."""
    tenant_id = (
        "tenant-"
        + uuid.uuid4().hex
    )

    first = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "subscription-id-first",
        ),
        tenant_id_header=tenant_id,
    )

    assert first["success"] is True

    subscription_id = (
        first["subscription"]
        .subscription_id
    )

    suffix = subscription_id.removeprefix(
        "WILSYSUB-"
    ).lower()

    assert len(suffix) == 8

    before = (
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_id,
                "subscription_id":
                    subscription_id,
            },
            {"_id": 0},
        )
    )

    assert before is not None

    class _ForcedUUID:
        hex = suffix + ("0" * 24)

    with patch(
        "tools.eos.saas.billing."
        "subscription_registry.uuid.uuid4",
        return_value=_ForcedUUID(),
    ):
        collision = SubscriptionRegistry.create(
            _payload(
                tenant_id,
                "subscription-id-second",
            ),
            tenant_id_header=tenant_id,
        )

    assert collision == {
        "success": False,
        "error":
            "SUBSCRIPTION_ID_COLLISION",
    }

    assert (
        mongo_context.collection.count_documents(
            {
                "tenant_id": tenant_id,
                "subscription_id":
                    subscription_id,
            }
        )
        == 1
    )

    assert (
        mongo_context.collection.count_documents(
            {
                "tenant_id": tenant_id,
                "idempotency_key":
                    "subscription-id-second",
            }
        )
        == 0
    )

    after = (
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_id,
                "subscription_id":
                    subscription_id,
            },
            {"_id": 0},
        )
    )

    assert after == before


def test_real_mongo_same_idempotency_key_is_tenant_local(
    mongo_context: _MongoContext,
) -> None:
    """Identical idempotency keys remain independent between tenants."""
    tenant_a = (
        "tenant-a-"
        + uuid.uuid4().hex
    )
    tenant_b = (
        "tenant-b-"
        + uuid.uuid4().hex
    )

    shared_key = (
        "cross-tenant-idempotency"
    )

    first = SubscriptionRegistry.create(
        _payload(
            tenant_a,
            shared_key,
        ),
        tenant_id_header=tenant_a,
    )

    second = SubscriptionRegistry.create(
        _payload(
            tenant_b,
            shared_key,
        ),
        tenant_id_header=tenant_b,
    )

    assert first["success"] is True
    assert second["success"] is True
    assert first["replayed"] is False
    assert second["replayed"] is False

    assert (
        first["subscription"].tenant_id
        == tenant_a
    )
    assert (
        second["subscription"].tenant_id
        == tenant_b
    )

    assert (
        first["subscription"].subscription_id
        != second["subscription"].subscription_id
    )

    assert (
        mongo_context.collection.count_documents(
            {
                "idempotency_key":
                    shared_key
            }
        )
        == 2
    )


def test_real_mongo_create_derives_complete_global_catalogue_snapshot(
    mongo_context: _MongoContext,
) -> None:
    """Subscription commercial truth must come from a real global Plan row."""
    tenant = "tenant-" + uuid.uuid4().hex

    payload = _payload(
        tenant,
        "global-catalogue-snapshot",
        amount=749.0,
        plan="ENTERPRISE",
    )

    plan = PlanRegistry.get(
        payload["planId"],
        tenant_id=tenant,
    )

    assert plan is not None

    result = SubscriptionRegistry.create(
        payload,
        tenant_id_header=tenant,
    )

    assert result["success"] is True

    subscription = result["subscription"]

    assert subscription.plan_id == plan.plan_id
    assert subscription.plan.value == plan.plan_type.value
    assert subscription.plan_name == plan.name
    assert subscription.plan_features == tuple(plan.features)
    assert (
        subscription.plan_catalogue_version
        == plan.catalogue_version
    )
    assert subscription.amount == float(plan.price)
    assert subscription.currency == plan.currency
    assert (
        subscription.billing_frequency.value
        == plan.billing_frequency.value
    )

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
            "subscription_id":
                subscription.subscription_id,
        }
    )

    assert persisted is not None
    assert (
        persisted["plan_catalogue_version"]
        == plan.catalogue_version
    )
    assert persisted["plan_name"] == plan.name
    assert persisted["plan_features"] == list(plan.features)


def test_real_mongo_tenant_plan_admitted_only_to_own_tenant(
    mongo_context: _MongoContext,
) -> None:
    """Default catalogue semantics admit global/own plan but not neighbor plan."""
    tenant_a = "tenant-a-" + uuid.uuid4().hex
    tenant_b = "tenant-b-" + uuid.uuid4().hex

    plan = _seed_plan(
        plan="PROFESSIONAL",
        amount=321.0,
        tenant_id=tenant_a,
    )

    own = SubscriptionRegistry.create(
        _command(
            tenant_a,
            "tenant-plan-own",
            plan_id=plan.plan_id,
        ),
        tenant_id_header=tenant_a,
    )

    assert own["success"] is True

    neighbor = SubscriptionRegistry.create(
        _command(
            tenant_b,
            "tenant-plan-neighbor",
            plan_id=plan.plan_id,
        ),
        tenant_id_header=tenant_b,
    )

    assert neighbor == {
        "success": False,
        "error":
            "SUBSCRIPTION_PLAN_NOT_AVAILABLE",
    }

    assert (
        mongo_context.collection.count_documents(
            {"tenant_id": tenant_b}
        )
        == 0
    )


def test_real_mongo_inactive_plan_cannot_create_subscription(
    mongo_context: _MongoContext,
) -> None:
    """Persisted inactive catalogue state is not sellable subscription truth."""
    tenant = "tenant-" + uuid.uuid4().hex

    plan = _seed_plan(
        plan="ENTERPRISE",
        amount=811.0,
        active=False,
    )

    result = SubscriptionRegistry.create(
        _command(
            tenant,
            "inactive-plan",
            plan_id=plan.plan_id,
        ),
        tenant_id_header=tenant,
    )

    assert result == {
        "success": False,
        "error":
            "SUBSCRIPTION_PLAN_NOT_AVAILABLE",
    }

    assert (
        mongo_context.collection.count_documents({})
        == 0
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("plan", "SOVEREIGN"),
        ("amount", 1.0),
        ("currency", "USD"),
        ("billingFrequency", "annual"),
        ("planFeatures", ["caller.feature"]),
        ("planCatalogueVersion", 999),
        ("taxAmount", 123.0),
        ("proofHash", "caller-proof"),
        ("merkleRoot", "caller-root"),
    ],
)
def test_real_mongo_create_rejects_caller_commercial_redirection(
    mongo_context: _MongoContext,
    field: str,
    value: Any,
) -> None:
    """Plan selector never grants caller authority over canonical snapshot truth."""
    tenant = "tenant-" + uuid.uuid4().hex

    payload = _payload(
        tenant,
        "commercial-redirection-" + field,
    )

    payload[field] = value

    result = SubscriptionRegistry.create(
        payload,
        tenant_id_header=tenant,
    )

    assert result == {
        "success": False,
        "error":
            "SUBSCRIPTION_COMMERCIAL_REDIRECTION_FORBIDDEN",
    }

    assert (
        mongo_context.collection.count_documents({})
        == 0
    )


def test_real_mongo_generic_update_rejects_catalogue_commercial_fields(
    mongo_context: _MongoContext,
) -> None:
    """Generic update cannot become an alternate plan-price authority."""
    tenant = "tenant-" + uuid.uuid4().hex

    created = SubscriptionRegistry.create(
        _payload(
            tenant,
            "generic-commercial-update",
        ),
        tenant_id_header=tenant,
    )

    assert created["success"] is True

    subscription = created["subscription"]

    before = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
            "subscription_id":
                subscription.subscription_id,
        },
        {"_id": 0},
    )

    result = SubscriptionRegistry.update(
        subscription.subscription_id,
        {
            "amount": 999999.0,
        },
        tenant_id_header=tenant,
    )

    assert result == {
        "success": False,
        "error":
            "SUBSCRIPTION_UPDATE_INVALID_FIELDS",
    }

    after = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
            "subscription_id":
                subscription.subscription_id,
        },
        {"_id": 0},
    )

    assert after == before


def test_real_mongo_upgrade_and_downgrade_derive_catalogue_snapshot(
    mongo_context: _MongoContext,
) -> None:
    """Plan change commands carry only newPlanId selection authority."""
    tenant = "tenant-" + uuid.uuid4().hex

    created = SubscriptionRegistry.create(
        _payload(
            tenant,
            "catalogue-transition-base",
            amount=200.0,
            plan="PROFESSIONAL",
        ),
        tenant_id_header=tenant,
    )

    assert created["success"] is True

    subscription_id = (
        created["subscription"].subscription_id
    )

    upgrade_plan = _seed_plan(
        plan="ENTERPRISE",
        amount=900.0,
        features=(
            "crm.core",
            "legal.documents",
            "wilsy.ai",
        ),
    )

    upgraded = SubscriptionRegistry.upgrade(
        subscription_id,
        tenant_id_header=tenant,
        upgrade_data={
            "newPlanId": upgrade_plan.plan_id,
        },
    )

    assert upgraded["success"] is True

    upgraded_sub = upgraded["subscription"]

    assert upgraded_sub.plan_id == upgrade_plan.plan_id
    assert upgraded_sub.amount == float(upgrade_plan.price)
    assert upgraded_sub.currency == upgrade_plan.currency
    assert upgraded_sub.plan_features == tuple(upgrade_plan.features)
    assert (
        upgraded_sub.plan_catalogue_version
        == upgrade_plan.catalogue_version
    )

    invalid = SubscriptionRegistry.upgrade(
        subscription_id,
        tenant_id_header=tenant,
        upgrade_data={
            "newPlanId": upgrade_plan.plan_id,
            "newAmount": 1.0,
        },
    )

    assert invalid == {
        "success": False,
        "error":
            "SUBSCRIPTION_PLAN_CHANGE_INVALID_FIELDS",
    }

    downgrade_plan = _seed_plan(
        plan="PROFESSIONAL",
        amount=150.0,
    )

    downgraded = SubscriptionRegistry.downgrade(
        subscription_id,
        tenant_id_header=tenant,
        downgrade_data={
            "newPlanId": downgrade_plan.plan_id,
        },
    )

    assert downgraded["success"] is True

    downgraded_sub = downgraded["subscription"]

    assert downgraded_sub.plan_id == downgrade_plan.plan_id
    assert downgraded_sub.amount == float(downgrade_plan.price)
    assert (
        downgraded_sub.plan_catalogue_version
        == downgrade_plan.catalogue_version
    )


def test_real_mongo_plan_catalogue_outage_fails_explicitly(
    mongo_context: _MongoContext,
) -> None:
    """Plan persistence outage cannot masquerade as unavailable/absent plan."""
    tenant = "tenant-" + uuid.uuid4().hex

    plan = _seed_plan(
        plan="ENTERPRISE",
        amount=654.0,
    )

    dead = MongoClient(
        "mongodb://127.0.0.1:1/plan_catalogue_dead",
        serverSelectionTimeoutMS=150,
    )

    original = plan_registry_module.plans_collection

    plan_registry_module.plans_collection = (
        dead["plan_catalogue_dead"]["plans"]
    )

    try:
        with pytest.raises(
            SubscriptionRegistryError,
            match=(
                "^SUBSCRIPTION_PLAN_CATALOGUE_UNAVAILABLE$"
            ),
        ):
            SubscriptionRegistry.create(
                _command(
                    tenant,
                    "catalogue-outage",
                    plan_id=plan.plan_id,
                ),
                tenant_id_header=tenant,
            )
    finally:
        plan_registry_module.plans_collection = original
        dead.close()

    assert (
        mongo_context.collection.count_documents({})
        == 0
    )


def test_real_mongo_create_derives_calendar_period_from_start_and_plan(
    mongo_context: _MongoContext,
) -> None:
    tenant_id = (
        "tenant-calendar-"
        + uuid.uuid4().hex
    )

    result = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "calendar-derived-create",
        ),
        tenant_id_header=tenant_id,
    )

    assert result["success"] is True
    assert result["replayed"] is False

    subscription = result["subscription"]

    assert (
        subscription.current_period_start.isoformat()
        == "2026-09-01T00:00:00+00:00"
    )

    assert (
        subscription.current_period_end.isoformat()
        == "2026-10-01T00:00:00+00:00"
    )


def test_real_mongo_new_create_rejects_caller_period_redirection(
    mongo_context: _MongoContext,
) -> None:
    tenant_id = (
        "tenant-period-redirection-"
        + uuid.uuid4().hex
    )

    payload = _payload(
        tenant_id,
        "period-redirection",
    )

    payload["currentPeriodStart"] = (
        "2026-09-03T10:00:00+00:00"
    )
    payload["currentPeriodEnd"] = (
        "2026-10-03T10:00:00+00:00"
    )

    result = SubscriptionRegistry.create(
        payload,
        tenant_id_header=tenant_id,
    )

    assert result == {
        "success": False,
        "error":
            "SUBSCRIPTION_COMMERCIAL_REDIRECTION_FORBIDDEN",
    }

    assert (
        mongo_context.collection.count_documents(
            {"tenant_id": tenant_id}
        )
        == 0
    )


def test_real_mongo_generic_update_cannot_replace_calendar_period(
    mongo_context: _MongoContext,
) -> None:
    tenant_id = (
        "tenant-period-update-"
        + uuid.uuid4().hex
    )

    created = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            "period-update-create",
        ),
        tenant_id_header=tenant_id,
    )

    assert created["success"] is True

    subscription = created["subscription"]

    before_start = (
        subscription.current_period_start
    )
    before_end = (
        subscription.current_period_end
    )

    result = SubscriptionRegistry.update(
        subscription.subscription_id,
        {
            "current_period_end":
                "2099-01-01T00:00:00+00:00",
        },
        tenant_id_header=tenant_id,
    )

    assert result == {
        "success": False,
        "error":
            "SUBSCRIPTION_UPDATE_INVALID_FIELDS",
    }

    loaded = SubscriptionRegistry.get(
        subscription.subscription_id,
        tenant_id_header=tenant_id,
    )

    assert loaded is not None
    assert loaded.current_period_start == before_start
    assert loaded.current_period_end == before_end


def test_real_mongo_naive_start_date_fails_closed(
    mongo_context: _MongoContext,
) -> None:
    tenant_id = (
        "tenant-naive-calendar-"
        + uuid.uuid4().hex
    )

    payload = _payload(
        tenant_id,
        "naive-calendar",
    )

    payload["startDate"] = (
        "2026-09-03T10:00:00"
    )

    result = SubscriptionRegistry.create(
        payload,
        tenant_id_header=tenant_id,
    )

    assert result["success"] is False
    assert "timezone-aware" in result["error"]

    assert (
        mongo_context.collection.count_documents(
            {"tenant_id": tenant_id}
        )
        == 0
    )


def test_real_mongo_legacy_period_command_exact_replay_survives_but_change_conflicts(
    mongo_context: _MongoContext,
) -> None:
    tenant_id = (
        "tenant-legacy-period-"
        + uuid.uuid4().hex
    )

    key = "legacy-period-replay"

    canonical_payload = _payload(
        tenant_id,
        key,
    )

    created = SubscriptionRegistry.create(
        canonical_payload,
        tenant_id_header=tenant_id,
    )

    assert created["success"] is True

    subscription = created["subscription"]

    legacy_payload = copy.deepcopy(
        canonical_payload
    )

    legacy_payload["currentPeriodStart"] = (
        "2026-09-03T10:00:00+00:00"
    )
    legacy_payload["currentPeriodEnd"] = (
        "2026-10-03T10:00:00+00:00"
    )

    create_material = (
        registry._create_material(
            tenant_id,
            legacy_payload,
        )
    )

    fingerprint = (
        registry._fingerprint_create_material(
            create_material
        )
    )

    update_result = (
        mongo_context.collection.update_one(
            {
                "tenant_id": tenant_id,
                "subscription_id":
                    subscription.subscription_id,
            },
            {
                "$set": {
                    "_registry_create_material":
                        create_material,
                    "_registry_create_fingerprint":
                        fingerprint,
                    "current_period_start":
                        "2026-09-03T10:00:00+00:00",
                    "current_period_end":
                        "2026-10-03T10:00:00+00:00",
                }
            },
        )
    )

    assert update_result.matched_count == 1
    assert update_result.modified_count == 1

    replay = SubscriptionRegistry.create(
        legacy_payload,
        tenant_id_header=tenant_id,
    )

    assert replay["success"] is True
    assert replay["replayed"] is True

    assert (
        replay["subscription"].subscription_id
        == subscription.subscription_id
    )

    assert (
        replay[
            "subscription"
        ].current_period_start
        == datetime.fromisoformat(
            "2026-09-03T10:00:00+00:00"
        )
    )

    assert (
        replay[
            "subscription"
        ].current_period_end
        == datetime.fromisoformat(
            "2026-10-03T10:00:00+00:00"
        )
    )

    changed = copy.deepcopy(
        legacy_payload
    )

    changed["currentPeriodEnd"] = (
        "2026-11-03T10:00:00+00:00"
    )

    conflict = SubscriptionRegistry.create(
        changed,
        tenant_id_header=tenant_id,
    )

    assert conflict == {
        "success": False,
        "error":
            "SUBSCRIPTION_IDEMPOTENCY_CONFLICT",
    }

    persisted_after_conflict = (
        mongo_context.collection.find_one(
            {
                "tenant_id": tenant_id,
                "subscription_id":
                    subscription.subscription_id,
            }
        )
    )

    assert persisted_after_conflict is not None

    assert (
        persisted_after_conflict[
            "current_period_start"
        ]
        == "2026-09-03T10:00:00+00:00"
    )

    assert (
        persisted_after_conflict[
            "current_period_end"
        ]
        == "2026-10-03T10:00:00+00:00"
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tests/integration/test_subscription_registry_real_mongo.py
# VERSION: v1.2.1-SUBSCRIPTION-CALENDAR-BILLING-CERT
# AUTHORITY BOUNDARY:
#   Real Mongo subscription persistence plus canonical PlanRegistry
#   catalogue-provenance integration. HTTP authorization remains outside
#   this Registry-level certificate.
# TENANT POSTURE:
#   UUID-isolated synthetic tenants; cross-tenant absence and neighboring truth
#   preservation are asserted against actual Mongo persistence.
# FAIL-CLOSED POSTURE:
#   Mongo unavailability is a test failure; malformed persisted truth and real
#   network failure must produce explicit registry errors.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
