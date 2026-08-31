# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION
TENANT PROFILE MUTATION — REAL MONGO CERTIFICATE
===============================================================================

TITLE:
    Tenant Registry Profile Mutation Real-Mongo Certification

FILE:
    tests/integration/test_tenant_registry_profile_mutation_real_mongo.py

VERSION:
    v1.0.1-TENANT-PROFILE-MUTATION-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Actual MongoDB replica-set persistence certification for C1.

EPITOME:
    Proves strict profile mutation against a UUID-bounded real Mongo database:
    sector round-trip, all six mutable fields, protected-truth preservation,
    checksum regeneration, proof-hash preservation, same-value idempotency,
    forbidden-field no-mutation, genuine absence, invalid-document no-mutation,
    legacy update compatibility, and deterministic cleanup/restoration.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_registry_profile_mutation_real_mongo.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.0.1-TENANT-PROFILE-MUTATION-REAL-MONGO-CERT
        - Certifies created_at preservation by exact UTC instant across BSON/PyMongo timezone-naive decoding.
        - Preserves every v1.0.0 mutation, isolation, protected-field, idempotency, and cleanup assertion.

    v1.0.0-TENANT-PROFILE-MUTATION-REAL-MONGO-CERT
        - Initial actual-Mongo C1 certification.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Uses only synthetic UUID-bounded tenant truth in an isolated certification
    database. No production tenant data is required or modified.

TENANT BOUNDARY:
    Every write targets an explicit synthetic tenant id; neighboring synthetic
    tenant truth is checked for preservation.

AUTHORITY BOUNDARY:
    Persistence evidence only. No HTTP or business authorization is simulated.

FINANCIAL AUTHORITY BOUNDARY:
    Proves strict profile mutation cannot change plan or financial authority.
    Kennel EOS remains exclusive.

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
===============================================================================
"""

from __future__ import annotations

import copy
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection

import tools.eos.saas.tenancy.tenant_registry as registry
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
    TenantRegistryError,
)


TEST_VENDOR_MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)


def _utc_instant(value: datetime) -> datetime:
    """Normalize BSON/PyMongo datetime values to the same UTC instant.

    PyMongo decodes BSON datetimes as timezone-naive UTC by default unless the
    client is configured tz_aware=True. This helper does not relax timestamp
    preservation: it compares the exact represented UTC instant while accounting
    only for that transport representation detail.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class _MongoContext:
    """Hold the isolated certification database and collection."""

    def __init__(
        self,
        client: Any,
        collection: Collection[dict[str, Any]],
        database_name: str,
    ) -> None:
        self.client = client
        self.collection = collection
        self.database_name = database_name


def _tenant_document(tenant_id: str) -> dict[str, Any]:
    created_at = datetime(2026, 8, 30, tzinfo=timezone.utc)
    return {
        "tenant_id": tenant_id,
        "name": "Tenant A",
        "organization": {
            "organization_name": "Tenant A",
            "industry": "Legal",
            "plan": "ENTERPRISE",
            "legal_name": "Tenant A Legal",
            "tax_id": "tax-a",
            "contact_email": "tenant-a@example.test",
            "regions": ["Africa"],
            "created_at": created_at.isoformat(),
        },
        "industry": "Legal",
        "legal_name": "Tenant A Legal",
        "tax_id": "tax-a",
        "contact_email": "tenant-a@example.test",
        "plan": "ENTERPRISE",
        "status": "ACTIVE",
        "created_at": created_at,
        "checksum": "legacy-checksum",
        "alias": "tenant-a",
        "region": "ZA",
        "sector": "Law",
        "compliance_flags": {"certified": True},
        "proof_hash": "proof-before",
        "verified": True,
    }


@pytest.fixture(scope="module")
def mongo_context() -> Iterator[_MongoContext]:
    """Bind TenantRegistry to an isolated real replica-set certification database."""
    mongo_client = MongoClient(
        TEST_VENDOR_MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )
    hello = mongo_client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"

    database_name = f"wilsy_c1_profile_mutation_{uuid.uuid4().hex}"
    database = mongo_client[database_name]
    collection: Collection[dict[str, Any]] = database["tenants"]

    original_collection = registry.tenants_collection
    registry.tenants_collection = collection

    context = _MongoContext(
        mongo_client,
        collection,
        database_name,
    )
    try:
        yield context
    finally:
        registry.tenants_collection = original_collection
        mongo_client.drop_database(database_name)
        assert database_name not in mongo_client.list_database_names()
        mongo_client.close()


@pytest.fixture(autouse=True)
def clean_certification_collection(
    mongo_context: _MongoContext,
) -> Iterator[None]:
    """Ensure every test starts and ends with an empty isolated collection."""
    mongo_context.collection.delete_many({})
    yield
    mongo_context.collection.delete_many({})


def test_real_mongo_replica_set_and_uuid_database_contract(
    mongo_context: _MongoContext,
) -> None:
    """Certification executes on the required replica set and UUID database."""
    hello = mongo_context.client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert mongo_context.database_name.startswith(
        "wilsy_c1_profile_mutation_"
    )
    suffix = mongo_context.database_name.removeprefix(
        "wilsy_c1_profile_mutation_"
    )
    assert len(suffix) == 32
    int(suffix, 16)


def test_real_mongo_sector_round_trip_through_registry_get(
    mongo_context: _MongoContext,
) -> None:
    """Persisted sector hydrates as top-level TenantEntity profile truth."""
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    mongo_context.collection.insert_one(_tenant_document(tenant_id))

    entity = TenantRegistry.get(tenant_id)

    assert entity is not None
    assert entity.sector == "Law"


def test_real_mongo_all_six_fields_mutate_and_protected_truth_is_preserved(
    mongo_context: _MongoContext,
) -> None:
    """Actual Mongo persistence changes only profile fields plus internal checksum."""
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    neighbor_id = f"tenant-{uuid.uuid4().hex}"
    before = _tenant_document(tenant_id)
    neighbor = _tenant_document(neighbor_id)
    neighbor["name"] = "Neighbor"
    neighbor["organization"]["organization_name"] = "Neighbor"

    mongo_context.collection.insert_many([before, neighbor])
    before_neighbor = copy.deepcopy(
        mongo_context.collection.find_one(
            {"tenant_id": neighbor_id},
            {"_id": 0},
        )
    )

    entity = TenantRegistry.update_profile(
        tenant_id,
        {
            "name": "Tenant Alpha",
            "alias": "alpha",
            "industry": "Technology",
            "region": "EU",
            "sector": "AI",
            "legal_name": "Tenant Alpha Legal",
        },
    )

    assert entity is not None
    assert entity.organization.organization_name == "Tenant Alpha"
    assert entity.organization.industry == "Technology"
    assert entity.organization.legal_name == "Tenant Alpha Legal"
    assert entity.alias == "alpha"
    assert entity.region == "EU"
    assert entity.sector == "AI"

    persisted = mongo_context.collection.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0},
    )
    assert persisted is not None
    assert persisted["name"] == "Tenant Alpha"
    assert persisted["organization"]["organization_name"] == "Tenant Alpha"
    assert persisted["industry"] == "Technology"
    assert persisted["organization"]["industry"] == "Technology"
    assert persisted["legal_name"] == "Tenant Alpha Legal"
    assert persisted["organization"]["legal_name"] == "Tenant Alpha Legal"
    assert persisted["alias"] == "alpha"
    assert persisted["region"] == "EU"
    assert persisted["sector"] == "AI"

    for field_name in (
        "tenant_id",
        "status",
        "plan",
        "tax_id",
        "contact_email",
        "verified",
        "compliance_flags",
        "proof_hash",
    ):
        assert persisted[field_name] == before[field_name]

    persisted_created_at = persisted["created_at"]
    before_created_at = before["created_at"]
    assert isinstance(persisted_created_at, datetime)
    assert isinstance(before_created_at, datetime)
    assert _utc_instant(persisted_created_at) == _utc_instant(before_created_at)

    assert persisted["checksum"] != "legacy-checksum"
    assert persisted["checksum"] == entity.checksum
    assert persisted["proof_hash"] == "proof-before"

    after_neighbor = mongo_context.collection.find_one(
        {"tenant_id": neighbor_id},
        {"_id": 0},
    )
    assert after_neighbor == before_neighbor
    assert mongo_context.collection.count_documents({}) == 2


def test_real_mongo_same_value_mutation_is_idempotent_success(
    mongo_context: _MongoContext,
) -> None:
    """Repeated identical mutation succeeds and leaves persisted truth unchanged."""
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    mongo_context.collection.insert_one(_tenant_document(tenant_id))

    first = TenantRegistry.update_profile(
        tenant_id,
        {"alias": "tenant-a"},
    )
    assert first is not None
    before_repeat = mongo_context.collection.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0},
    )

    repeated = TenantRegistry.update_profile(
        tenant_id,
        {"alias": "tenant-a"},
    )
    after_repeat = mongo_context.collection.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0},
    )

    assert repeated is not None
    assert after_repeat == before_repeat
    assert mongo_context.collection.count_documents(
        {"tenant_id": tenant_id}
    ) == 1


def test_real_mongo_forbidden_fields_fail_without_mutation(
    mongo_context: _MongoContext,
) -> None:
    """Lifecycle/billing/security/evidence fields cannot reach actual Mongo writes."""
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    mongo_context.collection.insert_one(_tenant_document(tenant_id))
    before = mongo_context.collection.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0},
    )

    for field_name in (
        "status",
        "plan",
        "tax_id",
        "contact_email",
        "verified",
        "checksum",
        "proof_hash",
        "compliance_flags",
        "tenant_id",
    ):
        with pytest.raises(
            TenantRegistryError,
            match="^TENANT_REGISTRY_PROFILE_UPDATE_INVALID_FIELDS$",
        ):
            TenantRegistry.update_profile(
                tenant_id,
                {field_name: "forbidden"},
            )

    after = mongo_context.collection.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0},
    )
    assert after == before
    assert mongo_context.collection.count_documents({}) == 1


def test_real_mongo_genuine_absence_returns_none_and_preserves_neighbor(
    mongo_context: _MongoContext,
) -> None:
    """Absent target is None and cannot mutate neighboring tenant truth."""
    neighbor_id = f"tenant-{uuid.uuid4().hex}"
    mongo_context.collection.insert_one(_tenant_document(neighbor_id))
    before = mongo_context.collection.find_one(
        {"tenant_id": neighbor_id},
        {"_id": 0},
    )

    result = TenantRegistry.update_profile(
        f"missing-{uuid.uuid4().hex}",
        {"alias": "missing"},
    )

    assert result is None
    after = mongo_context.collection.find_one(
        {"tenant_id": neighbor_id},
        {"_id": 0},
    )
    assert after == before
    assert mongo_context.collection.count_documents({}) == 1


def test_real_mongo_invalid_existing_truth_fails_before_mutation(
    mongo_context: _MongoContext,
) -> None:
    """Malformed matching truth is explicit and remains byte-semantically unchanged."""
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    malformed = {
        "tenant_id": tenant_id,
        "organization": "corrupt",
        "status": "ACTIVE",
        "proof_hash": "preserve",
    }
    mongo_context.collection.insert_one(copy.deepcopy(malformed))
    before = mongo_context.collection.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0},
    )

    with pytest.raises(
        TenantRegistryError,
        match="^TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT$",
    ):
        TenantRegistry.update_profile(
            tenant_id,
            {"alias": "must-not-write"},
        )

    after = mongo_context.collection.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0},
    )
    assert after == before
    assert mongo_context.collection.count_documents({}) == 1


def test_real_mongo_legacy_update_contract_remains_available(
    mongo_context: _MongoContext,
) -> None:
    """C1 does not silently redefine the existing broad legacy update API."""
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    mongo_context.collection.insert_one(_tenant_document(tenant_id))

    result = TenantRegistry.update(
        tenant_id,
        {"status": "SUSPENDED"},
    )

    assert result["success"] is True
    persisted = mongo_context.collection.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0},
    )
    assert persisted is not None
    assert persisted["status"] == "SUSPENDED"


def test_real_mongo_strict_profile_update_never_deletes_document(
    mongo_context: _MongoContext,
) -> None:
    """Profile mutation preserves document identity/count and is never hard delete."""
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    inserted = mongo_context.collection.insert_one(
        _tenant_document(tenant_id)
    )
    count_before = mongo_context.collection.count_documents({})

    entity = TenantRegistry.update_profile(
        tenant_id,
        {"sector": "RegTech"},
    )

    assert entity is not None
    persisted = mongo_context.collection.find_one(
        {"tenant_id": tenant_id}
    )
    assert persisted is not None
    assert persisted["_id"] == inserted.inserted_id
    assert persisted["sector"] == "RegTech"
    assert mongo_context.collection.count_documents({}) == count_before


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_tenant_registry_profile_mutation_real_mongo.py
# VERSION: v1.0.1-TENANT-PROFILE-MUTATION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated actual-Mongo persistence evidence only; no HTTP, authentication, membership, role, permission, or financial authority
# TENANT POSTURE: every write is explicit tenant-id scoped inside a UUID-bounded database; neighboring truth and document identity are preserved
# FAIL-CLOSED POSTURE: forbidden fields and malformed truth do not mutate Mongo; absence is None; same-value mutation succeeds; cleanup restores the production collection reference
# FINANCIAL EXECUTION AUTHORITY: None. Plan cannot mutate through strict profile persistence.
# END OF WILSY OS SOVEREIGN ARTIFACT
