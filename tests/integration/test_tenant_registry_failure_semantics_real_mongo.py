"""TITLE: WILSY OS Tenant Registry Failure Semantics Real-Mongo Certification.
VERSION: v1.0.0-TENANT-REGISTRY-FAILURE-SEMANTICS-REAL-MONGO-CERT
AUTHORITY: Evidence-only certification of TenantRegistry get/archive semantics against isolated MongoDB.
EPITOME: Proves real persisted lookup, genuine absence, archive-only mutation, tenant isolation, cleanup, compatibility-header non-authority, and bounded outage translation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_registry_failure_semantics_real_mongo.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0 establishes isolated real-Mongo get/archive failure-semantics certification for 3K2.8B1.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: UUID-named local certification database only; no credentials or production tenant data are emitted.
TENANT BOUNDARY: Archive and lookup are asserted against exact generated tenant identifiers with a second tenant proving no cross-tenant mutation.
AUTHORITY BOUNDARY: Persistence evidence only; compatibility headers, caller roles, JWT state, and permissions never grant registry authority.
FINANCIAL AUTHORITY BOUNDARY: No financial state or execution is touched. Kennel EOS remains exclusive.
"""

from __future__ import annotations

import inspect
import os
from contextlib import contextmanager
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

import tools.eos.saas.tenancy.tenant_registry as registry_module
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry, TenantRegistryError

VERSION = "v1.0.0-TENANT-REGISTRY-FAILURE-SEMANTICS-REAL-MONGO-CERT"
CERT_URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_CERT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"


def _tenant_doc(tenant_id: str, *, name: str) -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "name": name,
        "organization": {
            "organization_name": name,
            "industry": "General",
            "plan": "ENTERPRISE",
            "legal_name": None,
            "tax_id": None,
            "contact_email": None,
            "regions": ["Africa"],
            "created_at": "2026-08-30T00:00:00+00:00",
        },
        "industry": "General",
        "plan": "ENTERPRISE",
        "regions": ["Africa"],
        "status": "ACTIVE",
        "created_at": "2026-08-30T00:00:00+00:00",
        "alias": tenant_id,
        "region": "ZA",
        "compliance_flags": {"certification": True},
        "verified": False,
    }


@contextmanager
def _state() -> Iterator[
    tuple[
        Any,
        Collection[dict[str, Any]],
        str,
        str,
        str,
    ]
]:
    uri = os.environ.get(CERT_URI_ENV, DEFAULT_CERT_URI)
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=5000,
    )
    database_name = f"tenant_registry_failure_cert_{uuid4().hex}"
    database = client[database_name]
    collection: Collection[dict[str, Any]] = database["tenants"]
    tenant_a = f"tenant-a-{uuid4().hex}"
    tenant_b = f"tenant-b-{uuid4().hex}"
    original_collection = registry_module.tenants_collection

    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName") == "wilsyVendorCertRS"

        collection.insert_many(
            [
                _tenant_doc(tenant_a, name="Tenant A"),
                _tenant_doc(tenant_b, name="Tenant B"),
            ]
        )
        registry_module.tenants_collection = collection
        yield client, collection, database_name, tenant_a, tenant_b
    finally:
        registry_module.tenants_collection = original_collection
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


def test_real_mongo_lookup_success_and_genuine_absence() -> None:
    """Real Mongo distinguishes a known tenant from genuine absence."""
    with _state() as (_, collection, _, tenant_a, _):
        found = TenantRegistry.get(tenant_a)
        missing = TenantRegistry.get(f"missing-{uuid4().hex}")

        assert found is not None
        assert found.tenant_id == tenant_a
        assert missing is None
        assert collection.count_documents({}) == 2


def test_real_mongo_archive_is_exact_and_never_hard_deletes() -> None:
    """Archive mutates only the requested tenant status and preserves both documents."""
    with _state() as (_, collection, _, tenant_a, tenant_b):
        before_count = collection.count_documents({})
        before_other = collection.find_one({"tenant_id": tenant_b})

        assert TenantRegistry.archive(tenant_a) is True

        archived = collection.find_one({"tenant_id": tenant_a})
        other = collection.find_one({"tenant_id": tenant_b})
        assert archived is not None and archived["status"] == "ARCHIVED"
        assert other is not None and other["status"] == "ACTIVE"
        assert before_other is not None and other["tenant_id"] == before_other["tenant_id"]
        assert collection.count_documents({}) == before_count == 2


def test_real_mongo_archive_missing_returns_false_without_cross_tenant_mutation() -> None:
    """Unknown archive target remains False and leaves every real tenant unchanged."""
    with _state() as (_, collection, _, tenant_a, tenant_b):
        before = {
            tenant_a: collection.find_one({"tenant_id": tenant_a}),
            tenant_b: collection.find_one({"tenant_id": tenant_b}),
        }

        assert TenantRegistry.archive(f"missing-{uuid4().hex}") is False

        assert collection.find_one({"tenant_id": tenant_a}) == before[tenant_a]
        assert collection.find_one({"tenant_id": tenant_b}) == before[tenant_b]
        assert collection.count_documents({}) == 2


def test_real_mongo_compatibility_header_is_not_authority() -> None:
    """Different compatibility header values cannot redirect lookup or archive scope."""
    with _state() as (_, collection, _, tenant_a, tenant_b):
        first = TenantRegistry.get(tenant_a, tenant_id_header="GLOBAL_ROOT")
        second = TenantRegistry.get(tenant_a, tenant_id_header=tenant_b)

        assert first is not None and second is not None
        assert first.tenant_id == second.tenant_id == tenant_a

        assert TenantRegistry.archive(tenant_a, tenant_id_header=tenant_b) is True
        archived = collection.find_one({"tenant_id": tenant_a})
        other = collection.find_one({"tenant_id": tenant_b})
        assert archived is not None and archived["status"] == "ARCHIVED"
        assert other is not None and other["status"] == "ACTIVE"


def test_real_mongo_get_and_archive_outages_raise_bounded_errors() -> None:
    """A real unreachable Mongo client proves outages cannot collapse into absence/no-change."""
    original_collection = registry_module.tenants_collection
    dead_client = MongoClient(
        "mongodb://127.0.0.1:27999",
        serverSelectionTimeoutMS=250,
        connectTimeoutMS=250,
        socketTimeoutMS=250,
    )
    dead_collection: Collection[dict[str, Any]] = dead_client["unreachable"]["tenants"]

    try:
        registry_module.tenants_collection = dead_collection

        with pytest.raises(TenantRegistryError) as get_error:
            TenantRegistry.get("tenant-a")
        assert isinstance(get_error.value.__cause__, PyMongoError)

        with pytest.raises(TenantRegistryError) as archive_error:
            TenantRegistry.archive("tenant-a")
        assert isinstance(archive_error.value.__cause__, PyMongoError)
    finally:
        registry_module.tenants_collection = original_collection
        dead_client.close()


def test_real_mongo_registry_surface_has_no_role_jwt_permission_or_financial_authority() -> None:
    """The persistence methods expose no grant-bearing role/JWT/permission inputs."""
    forbidden = {
        "role",
        "roles",
        "jwt_role",
        "jwt_roles",
        "caller_role",
        "permission",
        "permissions",
        "authorization",
        "financial_execution",
    }
    for method in (TenantRegistry.get, TenantRegistry.archive):
        assert not forbidden.intersection(inspect.signature(method).parameters)


def test_real_mongo_cleanup_scope_is_uuid_bounded() -> None:
    """Every certification database is uniquely named and removed by the state context."""
    with _state() as (_, _, database_name, _, _):
        assert database_name.startswith("tenant_registry_failure_cert_")
        assert len(database_name) > len("tenant_registry_failure_cert_")


# ARTIFACT: test_tenant_registry_failure_semantics_real_mongo.py
# VERSION: v1.0.0-TENANT-REGISTRY-FAILURE-SEMANTICS-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo persistence certification only; no authentication or authorization authority
# TENANT POSTURE: exact generated tenant ids prove lookup/archive isolation and no cross-tenant mutation
# FAIL-CLOSED POSTURE: unreachable Mongo raises bounded TenantRegistryError and cannot masquerade as absence or archive no-change
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
