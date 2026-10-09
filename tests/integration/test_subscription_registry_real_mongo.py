# -*- coding: utf-8 -*-
"""WILSY OS — SubscriptionRegistry real-Mongo certification.

TITLE:
    WILSY OS Subscription Registry Real-Mongo Certification

VERSION:
    v1.2.2-SUBSCRIPTION-CALENDAR-BILLING-CERT

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
    v1.2.2-SUBSCRIPTION-CALENDAR-BILLING-CERT:
        - Aligns the current production-version assertion with the bounded
          v1.3.1 billing-intelligence read seam.
        - Preserves all v1.3.0 calendar-billing derivation, provenance,
          tenant-isolation and fail-closed persistence assertions.

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
    "v1.2.2-SUBSCRIPTION-CALENDAR-BILLING-CERT"
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
        == "v1.4.0-CALLER-TRANSACTION-INJECTION"
    )
    assert (
        TEST_VERSION
        == "v1.2.2-SUBSCRIPTION-CALENDAR-BILLING-CERT"
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
# VERSION: v1.2.2-SUBSCRIPTION-CALENDAR-BILLING-CERT
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

def test_real_mongo_rich_legacy_subscription_migrates_in_place(
    mongo_context: _MongoContext,
) -> None:
    """Migrate one rich legacy Node subscription into canonical registry truth."""
    from bson import ObjectId
    from tools.eos.saas.domain.subscription import (
        SubscriptionEntity,
        verify_subscription_integrity,
    )

    legacy_id = ObjectId()
    legacy_tenant_id = "695fe2a3ebabacb9a4a6850f"
    canonical_tenant_id = "WILSYTENANT-4CD2FZ4O"
    canonical_plan_id = (
        "WILSYPLAN-B877349B938833072C388A182ED4B497"
    )
    legacy_proof = "A" * 128
    seal_nonce = "15582cf15af65e9529941c71c59bc86e"

    legacy_merkle = hashlib.sha3_512(
        (
            f"{legacy_tenant_id}|"
            f"{legacy_proof}|"
            f"{seal_nonce}"
        ).encode("utf-8")
    ).hexdigest().upper()

    legacy = {
        "_id": legacy_id,
        "tenantId": legacy_tenant_id,
        "plan": "PROFESSIONAL",
        "planId": "6a78082d0c6c4942c7b20b16",
        "planName": "Pro",
        "amount": 299,
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "status": "active",
        "startDate": datetime.fromisoformat(
            "2026-08-09T00:00:00+00:00"
        ),
        "currentPeriodStart": datetime.fromisoformat(
            "2026-08-09T00:00:00+00:00"
        ),
        "currentPeriodEnd": datetime.fromisoformat(
            "2026-09-09T00:00:00+00:00"
        ),
        "idempotencyKey": (
            "WILSY-SUB-695FE2A3EBABACB9A4A6850F-B999F358B21E4A57"
        ),
        "sealNonce": seal_nonce,
        "proofHash": legacy_proof,
        "merkleRoot": legacy_merkle,
        "auditTrail": [
            {
                "action": "create",
                "timestamp": datetime.fromisoformat(
                    "2026-08-09T06:30:37.305000+00:00"
                ),
                "user": "695e423c9d355c0675c6835d",
                "reason": "Subscription created via BillingHUD",
                "previousStatus": None,
                "newStatus": "active",
                "metadata": {
                    "planSynthetic": False,
                },
                "proofHash": "B" * 128,
            }
        ],
        "metadata": {
            "source": "BILLING_HUD",
            "createdVia": "useSubscriptions.create",
            "planSnapshot": {
                "name": "Pro",
                "price": 299,
                "currency": "ZAR",
                "synthetic": False,
            },
        },
        "__v": 1,
    }

    mongo_context.collection.insert_one(
        copy.deepcopy(legacy)
    )

    observed = mongo_context.collection.find_one(
        {"_id": legacy_id}
    )
    assert observed is not None

    migrated = SubscriptionEntity.migrate_legacy_dict(
        observed,
        canonical_tenant_id=canonical_tenant_id,
        canonical_plan_id=canonical_plan_id,
    )

    create_payload = {
        "tenantId": canonical_tenant_id,
        "planId": canonical_plan_id,
        "startDate": migrated.start_date.isoformat(),
        "idempotencyKey": migrated.idempotency_key,
        "billingMode": migrated.billing_mode,
        "metadata": {
            "migration": (
                "LEGACY_NODE_SUBSCRIPTION_"
                "STRUCTURALLY_CONSISTENT_CONTENT_UNVERIFIED"
            )
        },
    }

    create_material = registry._create_material(
        canonical_tenant_id,
        create_payload,
    )
    create_fingerprint = (
        registry._fingerprint_create_material(
            create_material
        )
    )

    replacement = registry._document_for(
        migrated,
        create_material=create_material,
        create_fingerprint=create_fingerprint,
        revision=1,
    )
    replacement["_id"] = legacy_id

    cas_filter = copy.deepcopy(
        observed
    )

    result = mongo_context.collection.replace_one(
        cas_filter,
        replacement,
        upsert=False,
    )

    assert result.matched_count == 1
    assert result.modified_count == 1

    persisted = mongo_context.collection.find_one(
        {"_id": legacy_id}
    )
    assert persisted is not None
    assert persisted["_id"] == legacy_id
    assert persisted["_registry_revision"] == 1
    assert (
        persisted["_registry_schema"]
        == "WILSY-SUBSCRIPTION-REGISTRY/V1"
    )
    assert (
        persisted["legacy_evidence_status"]
        == (
            "LEGACY_NODE_SUBSCRIPTION_"
            "STRUCTURALLY_CONSISTENT_CONTENT_UNVERIFIED"
        )
    )

    hydrated = registry._hydrate(
        persisted
    )

    assert hydrated.tenant_id == canonical_tenant_id
    assert hydrated.plan_id == canonical_plan_id
    assert hydrated.subscription_id == migrated.subscription_id
    assert hydrated.idempotency_key == migrated.idempotency_key
    assert hydrated.legacy_proof_hash == legacy_proof
    assert hydrated.legacy_node_merkle_root == legacy_merkle
    assert verify_subscription_integrity(hydrated) is True

def _legacy_subscription_cert_row(
    *,
    legacy_id: Any,
    legacy_tenant_id: str = "695fe2a3ebabacb9a4a6850f",
) -> dict[str, Any]:
    """Build one synthetic rich BillingHUD legacy subscription row."""
    proof_hash = "A" * 128
    seal_nonce = "15582cf15af65e9529941c71c59bc86e"
    merkle_root = hashlib.sha3_512(
        (
            f"{legacy_tenant_id}|"
            f"{proof_hash}|"
            f"{seal_nonce}"
        ).encode("utf-8")
    ).hexdigest().upper()

    return {
        "_id": legacy_id,
        "tenantId": legacy_tenant_id,
        "plan": "PROFESSIONAL",
        "planId": "6a78082d0c6c4942c7b20b16",
        "planName": "Pro",
        "amount": 299,
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "status": "active",
        "startDate": datetime.fromisoformat(
            "2026-08-09T00:00:00+00:00"
        ),
        "currentPeriodStart": datetime.fromisoformat(
            "2026-08-09T00:00:00+00:00"
        ),
        "currentPeriodEnd": datetime.fromisoformat(
            "2026-09-09T00:00:00+00:00"
        ),
        "idempotencyKey": (
            "WILSY-SUB-"
            + str(legacy_id).upper()
        ),
        "sealNonce": seal_nonce,
        "proofHash": proof_hash,
        "merkleRoot": merkle_root,
        "auditTrail": [
            {
                "action": "create",
                "timestamp": datetime.fromisoformat(
                    "2026-08-09T06:30:37.305000+00:00"
                ),
                "user": "SUBSCRIPTION-MIGRATION-CERT",
                "reason": "Subscription created via BillingHUD",
                "previousStatus": None,
                "newStatus": "active",
                "metadata": {
                    "planSynthetic": False,
                },
                "proofHash": "B" * 128,
            }
        ],
        "metadata": {
            "source": "BILLING_HUD",
            "createdVia": "useSubscriptions.create",
            "planSnapshot": {
                "name": "Pro",
                "price": 299,
                "currency": "ZAR",
                "synthetic": False,
            },
        },
        "__v": 1,
    }


def _canonical_legacy_replacement(
    observed: dict[str, Any],
) -> dict[str, Any]:
    """Build canonical registry truth from one observed rich legacy row."""
    from tools.eos.saas.domain.subscription import SubscriptionEntity

    canonical_tenant_id = "WILSYTENANT-4CD2FZ4O"
    canonical_plan_id = (
        "WILSYPLAN-B877349B938833072C388A182ED4B497"
    )

    entity = SubscriptionEntity.migrate_legacy_dict(
        observed,
        canonical_tenant_id=canonical_tenant_id,
        canonical_plan_id=canonical_plan_id,
    )

    payload = {
        "tenantId": canonical_tenant_id,
        "planId": canonical_plan_id,
        "startDate": entity.start_date.isoformat(),
        "idempotencyKey": entity.idempotency_key,
        "billingMode": entity.billing_mode,
        "metadata": {
            "migration": entity.legacy_evidence_status,
        },
    }

    create_material = registry._create_material(
        canonical_tenant_id,
        payload,
    )

    replacement = registry._document_for(
        entity,
        create_material=create_material,
        create_fingerprint=(
            registry._fingerprint_create_material(
                create_material
            )
        ),
        revision=1,
    )
    replacement["_id"] = observed["_id"]
    return replacement


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("proofHash", "malformed"),
        ("merkleRoot", "1234"),
    ],
)
def test_real_mongo_legacy_malformed_crypto_rejects_without_write(
    mongo_context: _MongoContext,
    field_name: str,
    invalid_value: str,
) -> None:
    """Malformed historical cryptographic evidence never mutates persisted truth."""
    from bson import ObjectId
    from tools.eos.saas.domain.subscription import SubscriptionEntity

    row = _legacy_subscription_cert_row(
        legacy_id=ObjectId(),
    )
    row[field_name] = invalid_value

    mongo_context.collection.insert_one(
        copy.deepcopy(row)
    )

    before = copy.deepcopy(
        mongo_context.collection.find_one(
            {"_id": row["_id"]}
        )
    )
    assert before is not None

    with pytest.raises(
        ValueError,
        match="legacy subscription evidence incomplete",
    ):
        SubscriptionEntity.migrate_legacy_dict(
            before,
            canonical_tenant_id="WILSYTENANT-4CD2FZ4O",
            canonical_plan_id=(
                "WILSYPLAN-B877349B938833072C388A182ED4B497"
            ),
        )

    after = mongo_context.collection.find_one(
        {"_id": row["_id"]}
    )
    assert after == before


def test_real_mongo_incomplete_legacy_row_remains_untouched(
    mongo_context: _MongoContext,
) -> None:
    """Incomplete zero-price legacy evidence is preserved, never fabricated."""
    from bson import ObjectId
    from tools.eos.saas.domain.subscription import SubscriptionEntity

    row = {
        "_id": ObjectId(),
        "tenantId": "695fe2a3ebabacb9a4a6850f",
        "price": 0,
        "period": "yearly",
        "active": True,
        "__v": 0,
    }

    mongo_context.collection.insert_one(
        copy.deepcopy(row)
    )

    before = copy.deepcopy(
        mongo_context.collection.find_one(
            {"_id": row["_id"]}
        )
    )
    assert before is not None

    with pytest.raises(
        ValueError,
        match="legacy subscription evidence incomplete",
    ):
        SubscriptionEntity.migrate_legacy_dict(
            before,
            canonical_tenant_id="WILSYTENANT-4CD2FZ4O",
            canonical_plan_id="WILSYPLAN-DO-NOT-INVENT",
        )

    after = mongo_context.collection.find_one(
        {"_id": row["_id"]}
    )
    assert after == before


def test_real_mongo_legacy_migration_cas_rejects_stale_generation(
    mongo_context: _MongoContext,
) -> None:
    """Observed-generation CAS prevents overwriting concurrent legacy change."""
    from bson import ObjectId

    row = _legacy_subscription_cert_row(
        legacy_id=ObjectId(),
    )
    mongo_context.collection.insert_one(
        copy.deepcopy(row)
    )

    observed = mongo_context.collection.find_one(
        {"_id": row["_id"]}
    )
    assert observed is not None

    replacement = _canonical_legacy_replacement(
        observed
    )

    concurrent = mongo_context.collection.update_one(
        {"_id": row["_id"]},
        {
            "$set": {
                "metadata.concurrentMutation": True,
            }
        },
    )
    assert concurrent.modified_count == 1

    result = mongo_context.collection.replace_one(
        copy.deepcopy(observed),
        replacement,
        upsert=False,
    )

    assert result.matched_count == 0
    assert result.modified_count == 0

    persisted = mongo_context.collection.find_one(
        {"_id": row["_id"]}
    )
    assert persisted is not None
    assert (
        persisted["metadata"]["concurrentMutation"]
        is True
    )
    assert "_registry_schema" not in persisted


def test_real_mongo_legacy_migration_preserves_neighbor(
    mongo_context: _MongoContext,
) -> None:
    """Pre-index migration changes one rich row and preserves its neighbor.

    Legacy reconciliation intentionally precedes canonical unique-index
    installation because multiple historical rows may lack canonical
    ``tenant_id`` and ``subscription_id`` coordinates.
    """
    from bson import ObjectId

    database = mongo_context.client[
        mongo_context.database_name
    ]
    migration_collection = database.get_collection(
        "subscriptions_legacy_migration_cert",
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
        read_concern=ReadConcern(
            "majority"
        ),
    )

    migration_collection.drop()

    try:
        target = _legacy_subscription_cert_row(
            legacy_id=ObjectId(),
        )
        neighbor = {
            "_id": ObjectId(),
            "tenantId": "695fe2a3ebabacb9a4a6850f",
            "price": 0,
            "period": "yearly",
            "active": True,
            "__v": 0,
        }

        migration_collection.insert_many(
            [
                copy.deepcopy(target),
                copy.deepcopy(neighbor),
            ]
        )

        observed = migration_collection.find_one(
            {"_id": target["_id"]}
        )
        assert observed is not None

        neighbor_before = copy.deepcopy(
            migration_collection.find_one(
                {"_id": neighbor["_id"]}
            )
        )
        assert neighbor_before is not None

        replacement = _canonical_legacy_replacement(
            observed
        )

        result = migration_collection.replace_one(
            copy.deepcopy(observed),
            replacement,
            upsert=False,
        )

        assert result.matched_count == 1
        assert result.modified_count == 1

        neighbor_after = migration_collection.find_one(
            {"_id": neighbor["_id"]}
        )
        assert neighbor_after == neighbor_before

        migrated = migration_collection.find_one(
            {"_id": target["_id"]}
        )
        assert migrated is not None
        assert (
            migrated["_registry_schema"]
            == "WILSY-SUBSCRIPTION-REGISTRY/V1"
        )

        indexes = migration_collection.index_information()
        assert set(indexes) == {"_id_"}

    finally:
        migration_collection.drop()


def test_real_mongo_legacy_reconcile_then_install_canonical_indexes(
    mongo_context: _MongoContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify the exact production ordering before any Atlas mutation.

    Two legacy rows coexist before canonical indexes. Only the rich row is
    migrated by observed-generation CAS. The incomplete neighbor remains
    untouched. Canonical indexes are then installed through the production
    registry implementation, and the migrated row strictly hydrates.
    """
    from bson import ObjectId
    from tools.eos.saas.domain.subscription import (
        verify_subscription_integrity,
    )

    database = mongo_context.client[
        mongo_context.database_name
    ]
    collection = database.get_collection(
        "subscriptions_reconcile_index_cert",
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
        read_concern=ReadConcern(
            "majority"
        ),
    )

    collection.drop()

    rich = _legacy_subscription_cert_row(
        legacy_id=ObjectId(),
    )
    rich["merkleRoot"] = rich["merkleRoot"].lower()

    minimal = {
        "_id": ObjectId(),
        "tenantId": "695fe2a3ebabacb9a4a6850f",
        "price": 0,
        "period": "yearly",
        "active": True,
        "__v": 0,
    }

    try:
        collection.insert_many(
            [
                copy.deepcopy(rich),
                copy.deepcopy(minimal),
            ]
        )

        assert set(
            collection.index_information()
        ) == {"_id_"}

        observed_rich = collection.find_one(
            {"_id": rich["_id"]}
        )
        assert observed_rich is not None

        minimal_before = copy.deepcopy(
            collection.find_one(
                {"_id": minimal["_id"]}
            )
        )
        assert minimal_before is not None

        replacement = _canonical_legacy_replacement(
            observed_rich
        )

        result = collection.replace_one(
            copy.deepcopy(observed_rich),
            replacement,
            upsert=False,
        )

        assert result.matched_count == 1
        assert result.modified_count == 1

        minimal_after_migration = collection.find_one(
            {"_id": minimal["_id"]}
        )
        assert minimal_after_migration == minimal_before

        monkeypatch.setattr(
            registry,
            "subscriptions_collection",
            collection,
        )

        registry._ensure_indexes()

        indexes = {
            entry["name"]: entry
            for entry in collection.list_indexes()
        }

        assert (
            indexes["tenant_subscription_unique"]["key"]
            == {
                "tenant_id": 1,
                "subscription_id": 1,
            }
        )
        assert (
            indexes["tenant_subscription_unique"]["unique"]
            is True
        )

        assert (
            indexes["tenant_idempotency_unique"]["key"]
            == {
                "tenant_id": 1,
                "idempotency_key": 1,
            }
        )
        assert (
            indexes["tenant_idempotency_unique"]["unique"]
            is True
        )

        assert (
            indexes["tenant_status"]["key"]
            == {
                "tenant_id": 1,
                "status": 1,
            }
        )
        assert (
            indexes["tenant_plan"]["key"]
            == {
                "tenant_id": 1,
                "plan": 1,
            }
        )

        persisted_rich = collection.find_one(
            {"_id": rich["_id"]}
        )
        assert persisted_rich is not None

        hydrated = registry._hydrate(
            persisted_rich
        )

        assert (
            hydrated.tenant_id
            == "WILSYTENANT-4CD2FZ4O"
        )
        assert (
            hydrated.plan_id
            == "WILSYPLAN-B877349B938833072C388A182ED4B497"
        )
        assert (
            hydrated.legacy_evidence_status
            == (
                "LEGACY_NODE_SUBSCRIPTION_"
                "STRUCTURALLY_CONSISTENT_CONTENT_UNVERIFIED"
            )
        )
        assert (
            hydrated.legacy_proof_hash
            == rich["proofHash"]
        )
        assert (
            hydrated.legacy_node_merkle_root
            == rich["merkleRoot"]
        )
        assert verify_subscription_integrity(
            hydrated
        ) is True

        minimal_after_indexes = collection.find_one(
            {"_id": minimal["_id"]}
        )
        assert minimal_after_indexes == minimal_before

        assert collection.count_documents({}) == 2
        assert (
            collection.count_documents(
                {
                    "_registry_schema":
                    "WILSY-SUBSCRIPTION-REGISTRY/V1"
                }
            )
            == 1
        )
        assert (
            collection.count_documents(
                {
                    "tenant_id": {
                        "$exists": False
                    }
                }
            )
            == 1
        )

    finally:
        collection.drop()


def test_real_mongo_legacy_idempotency_index_reconciliation_precedes_migration(
    mongo_context: _MongoContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify legacy unique-index removal before canonical reconciliation.

    The historical Node index ``idempotencyKey_1`` is unique and non-sparse.
    A canonical replacement removes camelCase ``idempotencyKey`` and therefore
    collides with an incomplete legacy neighbor that also lacks that field.
    The safe sequence is:
      1. prove direct replacement fails atomically;
      2. drop only the obsolete legacy index;
      3. migrate the rich row by full observed-generation CAS;
      4. preserve the incomplete neighbor;
      5. install canonical registry indexes;
      6. strict-hydrate canonical truth.
    """
    from bson import ObjectId
    from pymongo.errors import DuplicateKeyError
    from tools.eos.saas.domain.subscription import (
        verify_subscription_integrity,
    )

    database = mongo_context.client[
        mongo_context.database_name
    ]
    collection = database.get_collection(
        "subscriptions_legacy_index_reconcile_cert",
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
        read_concern=ReadConcern(
            "majority"
        ),
    )

    collection.drop()

    rich = _legacy_subscription_cert_row(
        legacy_id=ObjectId(),
    )
    rich["merkleRoot"] = rich["merkleRoot"].lower()

    minimal = {
        "_id": ObjectId(),
        "tenantId": "695fe2a3ebabacb9a4a6850f",
        "price": 0,
        "period": "yearly",
        "active": True,
        "__v": 0,
    }

    try:
        collection.insert_many(
            [
                copy.deepcopy(rich),
                copy.deepcopy(minimal),
            ]
        )

        collection.create_index(
            [("idempotencyKey", 1)],
            unique=True,
            name="idempotencyKey_1",
        )

        observed_rich = collection.find_one(
            {"_id": rich["_id"]}
        )
        assert observed_rich is not None

        minimal_before = copy.deepcopy(
            collection.find_one(
                {"_id": minimal["_id"]}
            )
        )
        assert minimal_before is not None

        replacement = _canonical_legacy_replacement(
            observed_rich
        )

        with pytest.raises(
            DuplicateKeyError,
        ):
            collection.replace_one(
                copy.deepcopy(observed_rich),
                replacement,
                upsert=False,
            )

        # Failed write must be atomic.
        rich_after_failed_write = collection.find_one(
            {"_id": rich["_id"]}
        )
        assert rich_after_failed_write == observed_rich

        minimal_after_failed_write = collection.find_one(
            {"_id": minimal["_id"]}
        )
        assert minimal_after_failed_write == minimal_before

        index_names_before_drop = {
            entry["name"]
            for entry in collection.list_indexes()
        }
        assert "idempotencyKey_1" in index_names_before_drop

        # Remove only the obsolete legacy camelCase uniqueness constraint.
        collection.drop_index(
            "idempotencyKey_1"
        )

        index_names_after_drop = {
            entry["name"]
            for entry in collection.list_indexes()
        }
        assert "idempotencyKey_1" not in index_names_after_drop
        assert "_id_" in index_names_after_drop

        # Re-observe after index reconciliation and use that exact generation.
        fresh_observed_rich = collection.find_one(
            {"_id": rich["_id"]}
        )
        assert fresh_observed_rich is not None
        assert fresh_observed_rich == observed_rich

        fresh_replacement = _canonical_legacy_replacement(
            fresh_observed_rich
        )

        result = collection.replace_one(
            copy.deepcopy(fresh_observed_rich),
            fresh_replacement,
            upsert=False,
        )

        assert result.matched_count == 1
        assert result.modified_count == 1

        minimal_after_migration = collection.find_one(
            {"_id": minimal["_id"]}
        )
        assert minimal_after_migration == minimal_before

        monkeypatch.setattr(
            registry,
            "subscriptions_collection",
            collection,
        )

        registry._ensure_indexes()

        canonical_indexes = {
            entry["name"]: entry
            for entry in collection.list_indexes()
        }

        assert "idempotencyKey_1" not in canonical_indexes
        assert "tenant_subscription_unique" in canonical_indexes
        assert "tenant_idempotency_unique" in canonical_indexes
        assert "tenant_status" in canonical_indexes
        assert "tenant_plan" in canonical_indexes

        persisted_rich = collection.find_one(
            {"_id": rich["_id"]}
        )
        assert persisted_rich is not None

        hydrated = registry._hydrate(
            persisted_rich
        )

        assert verify_subscription_integrity(
            hydrated
        ) is True

        assert (
            hydrated.legacy_proof_hash
            == rich["proofHash"]
        )
        assert (
            hydrated.legacy_node_merkle_root
            == rich["merkleRoot"]
        )

        minimal_after_indexes = collection.find_one(
            {"_id": minimal["_id"]}
        )
        assert minimal_after_indexes == minimal_before

        assert collection.count_documents({}) == 2

    finally:
        collection.drop()



def test_real_mongo_founder_enterprise_subscription_derives_catalogue_truth_from_plan_registry(
    mongo_context: _MongoContext,
) -> None:
    """Certify Founder subscription truth is derived from PlanRegistry only."""
    from tools.eos.saas.domain.plan import PlanTiers
    from tools.eos.saas.domain.subscription import (
        BillingFrequency,
        SubscriptionStatus,
    )

    tenant_id = "WILSYTENANT-4CD2FZ4O"
    plan_id = "WILSYPLAN-F0F0F0F0"
    branding_feature = (
        "wilsy.vas.tenant_branding.enterprise.v1"
    )
    plan_idempotency = (
        "FOUNDER-PLAN-SUBSCRIPTION-CERT-V1"
    )
    subscription_idempotency = (
        "FOUNDER-SUBSCRIPTION-CERT-V1"
    )

    plan_result = PlanRegistry.create(
        {
            "name": "Founder Enterprise",
            "description": (
                "Tenant-scoped Founder subscription certificate plan."
            ),
            "price": 0,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "FOUNDER_ENTERPRISE",
            "idempotencyKey": plan_idempotency,
            "tenantId": tenant_id,
            "plan_id": plan_id,
            "active": True,
            "trialDays": 0,
            "features": [
                branding_feature,
            ],
            "metadata": {
                "certificate": True,
                "catalogueAuthority": "PlanRegistry",
            },
            "tags": [
                "founder-enterprise",
                "subscription-catalogue-cert",
            ],
            "user": "SUBSCRIPTION-CATALOGUE-CERT",
        }
    )

    assert plan_result["success"] is True

    catalogue_plan = plan_result["plan"]

    assert catalogue_plan.plan_type is PlanTiers.FOUNDER_ENTERPRISE
    assert catalogue_plan.price == 0.0
    assert catalogue_plan.catalogue_version == 1
    assert catalogue_plan.features == (
        branding_feature,
    )
    assert catalogue_plan.tenant_id == tenant_id

    command = _command(
        tenant_id,
        subscription_idempotency,
        plan_id=plan_id,
    )

    # Commercial truth is deliberately absent from the caller command.
    assert "amount" not in command
    assert "currency" not in command
    assert "billingFrequency" not in command
    assert "planFeatures" not in command
    assert "plan_features" not in command
    assert "planCatalogueVersion" not in command
    assert "plan_catalogue_version" not in command
    assert "planType" not in command

    created = SubscriptionRegistry.create(
        command,
        tenant_id_header=tenant_id,
    )

    assert created["success"] is True
    assert created["replayed"] is False

    subscription = created["subscription"]

    assert subscription.tenant_id == tenant_id
    assert subscription.plan_id == plan_id
    assert subscription.plan.value == "FOUNDER_ENTERPRISE"
    assert subscription.plan_name == "Founder Enterprise"
    assert subscription.amount == 0.0
    assert subscription.currency == "ZAR"
    assert subscription.billing_frequency is BillingFrequency.MONTHLY
    assert subscription.plan_catalogue_version == 1
    assert subscription.plan_features == (
        branding_feature,
    )
    assert subscription.status is SubscriptionStatus.ACTIVE

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": tenant_id,
            "subscription_id": subscription.subscription_id,
        }
    )

    assert persisted is not None
    assert persisted["plan_id"] == plan_id
    assert persisted["amount"] == 0.0
    assert persisted["currency"] == "ZAR"
    assert persisted["plan_catalogue_version"] == 1
    assert persisted["plan_features"] == [
        branding_feature,
    ]
    assert persisted["_registry_revision"] == 1

    replay = SubscriptionRegistry.create(
        command,
        tenant_id_header=tenant_id,
    )

    assert replay["success"] is True
    assert replay["replayed"] is True
    assert (
        replay["subscription"].subscription_id
        == subscription.subscription_id
    )

    # A caller may not redirect canonical commercial truth.
    redirected = dict(
        command,
        amount=999.0,
    )

    rejected = SubscriptionRegistry.create(
        redirected,
        tenant_id_header=tenant_id,
    )

    assert rejected == {
        "success": False,
        "error": "SUBSCRIPTION_COMMERCIAL_REDIRECTION_FORBIDDEN",
    }

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": tenant_id,
        }
    ) == 1
