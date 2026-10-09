# -*- coding: utf-8 -*-
"""
TITLE:
    WILSY OS — Legacy Node Plan Evidence Migration Real-Mongo Certificate

VERSION:
    v1.0.1-PLAN-LEGACY-NODE-EVIDENCE-MIGRATION-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Certify explicit migration of historically valid Node plan evidence into
    fresh current-v2 PlanEntity evidence without mutating canonical databases.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_plan_registry_legacy_evidence_migration_real_mongo.py

OWNERSHIP:
    Python EOS SaaS / Billing certification.

TENANT / AUTHORITY BOUNDARY:
    tenant_id is catalogue scope evidence only. This certificate creates no
    authentication, membership, role, entitlement, subscription or payment
    authority.

REAL-WORLD POSTURE:
    Actual UUID-isolated MongoDB only. The canonical ``wilsy`` database is
    never opened for writes by this certificate.

COMPLIANCE:
    POPIA §19 | GDPR Art. 32 | SOC2 CC7.2 | ISO 27001

CHANGELOG:
    2026-09-29 v1.0.1-PLAN-LEGACY-NODE-EVIDENCE-MIGRATION-REAL-MONGO-CERT
        - Repairs migration setup to insert and freshly read the persisted
          legacy BSON row before migration and exact compare-and-swap replace.
        - Preserves transport normalization boundaries without weakening CAS.

WILSY OS — ALL OR NOTHING.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from hashlib import sha3_512
import json
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as registry
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.domain.plan import PlanEntity

TEST_VERSION = (
    "v1.0.1-PLAN-LEGACY-NODE-EVIDENCE-MIGRATION-REAL-MONGO-CERT"
)
CERT_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


class _MongoContext:
    def __init__(
        self,
        client: MongoClient,
        collection: Collection[dict[str, object]],
        database_name: str,
    ) -> None:
        self.client = client
        self.collection = collection
        self.database_name = database_name


def _database_uri(uri: str, database_name: str) -> str:
    base, separator, query = uri.partition("?")
    prefix = base.rsplit("/", 1)[0]
    resolved = f"{prefix}/{database_name}"
    if separator:
        resolved += f"?{query}"
    return resolved


def _node_payload(
    *,
    index: int = 1,
    plan_type: str = "PROFESSIONAL",
    timestamp: datetime | None = None,
    proof_timestamp: datetime | None = None,
    tenant_id: str | None = "TENANT-NODE",
) -> dict[str, object]:
    created = timestamp or datetime(
        2026,
        1,
        5,
        12,
        0,
        index,
        123000,
        tzinfo=timezone.utc,
    )
    proof_time = proof_timestamp or created
    plan_id = f"507f1f77bcf86cd7994390{index:02d}"
    payload: dict[str, object] = {
        "_id": plan_id,
        "__v": 0,
        "name": f"Node Historical {index}",
        "description": "Historical Node catalogue row",
        "price": 499 + index,
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "trialDays": 14,
        "planType": plan_type,
        "features": ["FEATURE_A", "FEATURE_B"],
        "active": True,
        "tenantId": tenant_id,
        "kennelShard": "EOS_PRIMARY",
        "idempotencyKey": f"NODE-LEGACY-{index:03d}",
        "sealNonce": f"node-seal-nonce-{index}",
        "createdAt": created,
        "updatedAt": created,
        "metadata": {"tier": "historical", "index": index},
        "tags": ["legacy", "node"],
    }
    iso_timestamp = proof_time.astimezone(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S."
    ) + f"{proof_time.microsecond // 1000:03d}Z"
    proof_payload = {
        "action": "save",
        "planId": plan_id,
        "name": payload["name"],
        "planType": plan_type,
        "price": payload["price"],
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "trialDays": 14,
        "active": True,
        "tenantId": tenant_id,
        "kennelShard": "EOS_PRIMARY",
        "idempotencyKey": payload["idempotencyKey"],
        "timestamp": iso_timestamp,
        "metadata": {"autoSeal": True},
    }
    encoded = json.dumps(
        {key: proof_payload[key] for key in sorted(proof_payload)},
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    proof_hash = sha3_512(encoded).hexdigest().upper()
    root = sha3_512(
        f"{tenant_id or 'GLOBAL'}|{proof_hash}".encode("utf-8")
    ).hexdigest()
    payload["proofHash"] = proof_hash
    payload["merkleRoot"] = root
    return payload


def _python_legacy_payload() -> dict[str, object]:
    proof = "A" * 128
    root = sha3_512(
        f"TENANT-PYTHON|{proof}|python-seal".encode("utf-8")
    ).hexdigest().upper()
    return {
        "plan_id": "WILSYPLAN-PYTHONLEGACY",
        "name": "Python Legacy",
        "price": 100,
        "currency": "ZAR",
        "billing_frequency": "monthly",
        "plan_type": "PROFESSIONAL",
        "idempotency_key": "PYTHON-LEGACY-IDEMPOTENCY",
        "tenant_id": "TENANT-PYTHON",
        "seal_nonce": "python-seal",
        "proof_hash": proof,
        "merkle_root": root,
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }


@pytest.fixture(scope="module")
def mongo_context() -> Iterator[_MongoContext]:
    client: MongoClient = MongoClient(
        CERT_URI,
        serverSelectionTimeoutMS=5000,
    )
    client.admin.command("ping")
    hello = client.admin.command("hello")
    if hello.get("setName") != EXPECTED_REPLICA_SET:
        raise RuntimeError("PLAN_LEGACY_CERT_WRONG_MONGO_TOPOLOGY")
    if hello.get("isWritablePrimary") is not True:
        raise RuntimeError("PLAN_LEGACY_CERT_MONGO_NOT_PRIMARY")

    database_name = "wilsy_plan_legacy_migration_" + uuid.uuid4().hex
    collection = client[database_name].get_collection(
        "plans",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    original_collection = registry.plans_collection
    registry.plans_collection = collection
    PlanRegistry._ensure_indexes()
    context = _MongoContext(client, collection, database_name)
    try:
        yield context
    finally:
        registry.plans_collection = original_collection
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


@pytest.fixture(autouse=True)
def clean_collection(mongo_context: _MongoContext) -> Iterator[None]:
    mongo_context.collection.delete_many({})
    yield
    mongo_context.collection.delete_many({})


def _migrate_and_replace(
    context: _MongoContext,
    raw: dict[str, object],
) -> PlanEntity:
    seed = dict(raw)
    insert_result = context.collection.insert_one(seed)
    inserted_id = insert_result.inserted_id
    persisted = context.collection.find_one(
        {"_id": inserted_id}
    )
    assert persisted is not None
    assert persisted["_id"] == inserted_id

    # MongoDB is the transport authority for the migration input. In
    # particular, BSON dates are millisecond precision even when a Python
    # fixture carried a richer in-memory datetime. The legacy domain entry
    # point accepts the persisted identity marker for historical proof
    # reconstruction; __v remains transport-only and is excluded.
    migration_input = dict(persisted)
    migration_input.pop("__v", None)
    entity = PlanEntity.migrate_legacy_dict(migration_input)
    canonical = entity.to_dict()
    canonical["_id"] = inserted_id
    canonical["_registry_revision"] = 1

    # Bind replacement to the complete freshly observed legacy generation.
    # This is stronger than an _id-only selector and avoids pretending that
    # the pre-insert Python mapping is byte-for-byte identical to BSON.
    cas_predicate = {
        key: value
        for key, value in persisted.items()
        if key != "_id"
    }
    cas_predicate["_id"] = inserted_id
    result = context.collection.replace_one(
        cas_predicate,
        canonical,
        upsert=False,
    )
    assert result.matched_count == 1
    replaced = context.collection.find_one(
        {"_id": inserted_id}
    )
    assert replaced is not None
    assert replaced["_id"] == inserted_id
    assert replaced["_registry_revision"] == 1
    assert "__v" not in replaced
    assert PlanRegistry._hydrate(replaced).plan == entity
    return entity


def test_pre_migration_registry_read_fails_closed(
    mongo_context: _MongoContext,
) -> None:
    raw = _node_payload()
    mongo_context.collection.insert_one(raw)
    with pytest.raises(ValueError, match="PLAN_REGISTRY_REVISION_INVALID"):
        PlanRegistry.list()


@pytest.mark.parametrize(
    ("plan_type", "price"),
    (("PROFESSIONAL", 500), ("ENTERPRISE", 501), ("FREE", 502)),
)
def test_valid_node_rows_migrate_with_commercial_meaning(
    mongo_context: _MongoContext,
    plan_type: str,
    price: int,
) -> None:
    raw = _node_payload(plan_type=plan_type, index=price - 499)
    entity = _migrate_and_replace(mongo_context, raw)
    assert entity.plan_type.value == plan_type
    assert entity.price == float(price)
    assert entity.proof_version == 2
    assert entity.catalogue_version == 1


def test_migration_preserves_id_revision_and_removes_node_transport_version(
    mongo_context: _MongoContext,
) -> None:
    raw = _node_payload()
    entity = _migrate_and_replace(mongo_context, raw)
    stored = mongo_context.collection.find_one({"_id": raw["_id"]})
    assert stored is not None
    assert stored["_id"] == raw["_id"]
    assert stored["_registry_revision"] == 1
    assert "__v" not in stored
    assert stored["plan_id"] == entity.plan_id


def test_legacy_node_evidence_is_separate_and_current_evidence_is_fresh(
    mongo_context: _MongoContext,
) -> None:
    raw = _node_payload()
    entity = _migrate_and_replace(mongo_context, raw)
    assert entity.legacy_proof_hash == raw["proofHash"]
    assert entity.legacy_node_merkle_root == str(raw["merkleRoot"]).upper()
    assert entity.legacy_evidence_status == (
        "LEGACY_NODE_V1_EVIDENCE_CONSISTENT_CONTENT_UNVERIFIED"
    )
    assert entity.proof_hash != raw["proofHash"]
    assert entity.integrity_root != str(raw["merkleRoot"]).upper()


def test_registry_hydrate_get_list_and_exact_tenant(
    mongo_context: _MongoContext,
) -> None:
    raw = _node_payload(tenant_id="TENANT-EXACT")
    entity = _migrate_and_replace(mongo_context, raw)
    hydrated = PlanRegistry._hydrate(
        mongo_context.collection.find_one({"_id": raw["_id"]}) or {}
    )
    assert hydrated.plan == entity
    assert PlanRegistry.get(entity.plan_id, "TENANT-EXACT", exact_tenant=True) == entity
    assert PlanRegistry.get(entity.plan_id, "TENANT-OTHER", exact_tenant=True) is None
    listed = PlanRegistry.list("TENANT-EXACT", exact_tenant=True)
    assert listed["total"] == 1
    assert listed["items"][0] == entity


def test_registry_health_is_operational_after_migration(
    mongo_context: _MongoContext,
) -> None:
    _migrate_and_replace(mongo_context, _node_payload())
    health = PlanRegistry.health_check()
    assert health["status"] == "OPERATIONAL"
    assert health["plan_count"] == 1


@pytest.mark.parametrize("field", ("proofHash", "merkleRoot"))
def test_tampered_node_evidence_rejects_without_write(
    mongo_context: _MongoContext,
    field: str,
) -> None:
    raw = _node_payload()
    raw[field] = "0" * 128
    mongo_context.collection.insert_one(raw)
    with pytest.raises(ValueError, match="legacy"):
        PlanEntity.migrate_legacy_dict(raw)
    assert mongo_context.collection.count_documents({}) == 1
    stored = mongo_context.collection.find_one({})
    assert stored is not None
    assert "_registry_revision" not in stored


def test_commercial_tamper_rejects_without_recomputed_node_proof(
    mongo_context: _MongoContext,
) -> None:
    raw = _node_payload()
    raw["price"] = 9999
    mongo_context.collection.insert_one(raw)
    with pytest.raises(ValueError, match="Node evidence"):
        PlanEntity.migrate_legacy_dict(raw)


def test_timestamp_boundary_matches_exact_mongoose_lifecycle_rule(
    mongo_context: _MongoContext,
) -> None:
    created = datetime(2026, 1, 5, 12, 0, 0, 123000, tzinfo=timezone.utc)
    raw = _node_payload(timestamp=created, proof_timestamp=created + timedelta(milliseconds=1))
    entity = _migrate_and_replace(mongo_context, raw)
    assert entity.legacy_evidence_status.startswith("LEGACY_NODE_V1")
    changed = dict(raw, createdAt=created + timedelta(seconds=1), updatedAt=created + timedelta(seconds=1))
    with pytest.raises(ValueError, match="Node evidence"):
        PlanEntity.migrate_legacy_dict(changed)


def test_seal_nonce_is_not_bound_by_historical_node_producer(
    mongo_context: _MongoContext,
) -> None:
    raw = _node_payload()
    changed = dict(raw, sealNonce="different-seal")
    first = PlanEntity.migrate_legacy_dict(raw)
    second = PlanEntity.migrate_legacy_dict(changed)
    assert second.legacy_proof_hash == first.legacy_proof_hash
    assert second.legacy_node_merkle_root == first.legacy_node_merkle_root


def test_current_v2_row_is_not_reentered_through_legacy_migration(
    mongo_context: _MongoContext,
) -> None:
    entity = _migrate_and_replace(mongo_context, _node_payload())
    current = entity.to_dict()
    with pytest.raises(ValueError, match="unversioned"):
        PlanEntity.migrate_legacy_dict(current)


def test_python_legacy_envelope_path_is_unchanged(
    mongo_context: _MongoContext,
) -> None:
    entity = PlanEntity.migrate_legacy_dict(_python_legacy_payload())
    assert entity.legacy_evidence_status == (
        "LEGACY_V1_ENVELOPE_CONSISTENT_CONTENT_UNVERIFIED"
    )
    assert entity.legacy_node_merkle_root == ""


def test_unsealed_legacy_path_remains_explicitly_unverified(
    mongo_context: _MongoContext,
) -> None:
    entity = PlanEntity.migrate_legacy_dict({
        "name": "Unsealed",
        "price": 10,
        "currency": "ZAR",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    })
    assert entity.legacy_evidence_status == "LEGACY_UNVERSIONED_CONTENT_UNVERIFIED"
    assert entity.legacy_proof_hash == ""
    assert entity.legacy_node_merkle_root == ""


def test_current_from_dict_and_registry_hydration_remain_strict(
    mongo_context: _MongoContext,
) -> None:
    entity = _migrate_and_replace(mongo_context, _node_payload())
    payload = entity.to_dict()
    payload.pop("proof_hash")
    with pytest.raises(ValueError, match="complete proof_hash"):
        PlanEntity.from_dict(payload)


def test_global_uniqueness_indexes_remain_governed(
    mongo_context: _MongoContext,
) -> None:
    names = {
        index["name"]
        for index in mongo_context.collection.list_indexes()
    }
    assert "plan_id_unique" in names
    assert "idempotency_key_unique" in names


def test_no_subscription_or_entitlement_collections_are_touched(
    mongo_context: _MongoContext,
) -> None:
    _migrate_and_replace(mongo_context, _node_payload())
    names = set(mongo_context.client[mongo_context.database_name].list_collection_names())
    assert names == {"plans"}


"""
INSTITUTIONAL CERTIFICATION SEAL

Artifact:
    tests/integration/test_plan_registry_legacy_evidence_migration_real_mongo.py

Version:
    v1.0.1-PLAN-LEGACY-NODE-EVIDENCE-MIGRATION-REAL-MONGO-CERT

Status:
    DISPOSABLE REAL-MONGO CERTIFICATE — NO CANONICAL WRITES

Canonical database:
    NEVER USED; UUID-isolated database only.

Next gate:
    M_PLAN_CANONICAL_LEGACY_CATALOGUE_DRY_RUN_AND_APPLY

WILSY OS — ALL OR NOTHING.
"""
