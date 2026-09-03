# -*- coding: utf-8 -*-
"""WILSY OS — SubscriptionRegistry real-Mongo certification.

TITLE:
    WILSY OS Subscription Registry Real-Mongo Certification

VERSION:
    v1.0.2-SUBSCRIPTION-REGISTRY-REAL-MONGO-CERT

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
import os
import subprocess
import sys
import uuid
from unittest.mock import patch
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.subscription_registry as registry
from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry,
    SubscriptionRegistryError,
    VERSION as REGISTRY_VERSION,
)


TEST_VERSION = (
    "v1.0.2-SUBSCRIPTION-REGISTRY-REAL-MONGO-CERT"
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
        database_name: str,
        database_uri: str,
    ) -> None:
        self.client = client
        self.collection = collection
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


def _payload(
    tenant_id: str,
    idempotency_key: str,
    *,
    amount: float = 499.0,
    plan: str = "ENTERPRISE",
) -> dict[str, Any]:
    """Build explicit synthetic subscription command input."""
    return {
        "tenantId": tenant_id,
        "planId": f"PLAN-{plan}",
        "plan": plan,
        "amount": amount,
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "startDate": "2026-09-03T10:00:00+00:00",
        "currentPeriodStart":
            "2026-09-03T10:00:00+00:00",
        "currentPeriodEnd":
            "2026-10-03T10:00:00+00:00",
        "idempotencyKey": idempotency_key,
        "tier": plan,
        "billingMode": "PLATFORM",
        "onboardingRef":
            f"ONBOARD-{tenant_id}",
        "sector": "LEGAL",
        "region": "ZA",
        "metadata": {
            "certificate": True
        },
    }


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

    original_collection = (
        registry.subscriptions_collection
    )

    registry.subscriptions_collection = (
        collection
    )

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
    yield
    mongo_context.collection.delete_many({})


def test_real_mongo_version_database_and_index_contract(
    mongo_context: _MongoContext,
) -> None:
    """Prove actual Mongo, isolated database and deterministic indexes."""
    assert (
        REGISTRY_VERSION
        == "v1.1.1-SUBSCRIPTION-REAL-MONGO"
    )
    assert (
        TEST_VERSION
        == "v1.0.2-SUBSCRIPTION-REGISTRY-REAL-MONGO-CERT"
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
            "amount": 799.0,
            "metadata": {
                "updated": True
            },
        },
        tenant_id_header=tenant_a,
    )

    assert updated["success"] is True
    assert (
        updated["subscription"].amount
        == 799.0
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
    assert persisted_a["amount"] == 799.0
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
        '"amount":499.0',
        '"amount":999.0',
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


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tests/integration/test_subscription_registry_real_mongo.py
# VERSION: v1.0.2-SUBSCRIPTION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY:
#   Real Mongo subscription-persistence, idempotency, lifecycle and tenant
#   isolation certification only. HTTP authorization is not certified here.
# TENANT POSTURE:
#   UUID-isolated synthetic tenants; cross-tenant absence and neighboring truth
#   preservation are asserted against actual Mongo persistence.
# FAIL-CLOSED POSTURE:
#   Mongo unavailability is a test failure; malformed persisted truth and real
#   network failure must produce explicit registry errors.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
