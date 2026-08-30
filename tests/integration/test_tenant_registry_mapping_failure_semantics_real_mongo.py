# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION ARTIFACT
TENANT REGISTRY — MAPPING FAILURE SEMANTICS — REAL-MONGO CERTIFICATE
===============================================================================

TITLE:
    WILSY OS Tenant Registry Mapping Failure Semantics Real-Mongo Certification

FILE:
    tests/integration/test_tenant_registry_mapping_failure_semantics_real_mongo.py

VERSION:
    v1.0.0-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Isolated real-MongoDB certification of TenantRegistry GET persistence and
    read-integrity semantics.

EPITOME:
    Certifies against a real replica-set-backed MongoDB that healthy persisted
    tenant truth maps, genuine absence remains None, malformed persisted tenant
    truth raises the exact GET-invalid-document error, the malformed document is
    not deleted, neighboring tenant truth remains unchanged, legacy list behavior
    still skips malformed hydration, compatibility transport input is not
    authority, and cleanup remains UUID-bounded.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_registry_mapping_failure_semantics_real_mongo.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.0.0-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS-REAL-MONGO-CERT
        - Establishes real-Mongo B1.1 mapping-failure certification.
        - Proves persisted corruption is not converted into absence.
        - Proves failed hydration is non-destructive.
        - Proves neighboring persisted tenant truth remains unchanged.
        - Proves legacy list tolerance and compatibility-header non-authority.
        - Proves UUID-bounded database cleanup and collection restoration.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Local certification MongoDB only.
    UUID-bounded database names.
    Generated tenant identifiers only.
    No production tenant data or credentials are emitted.

TENANT BOUNDARY:
    Every certification tenant is generated uniquely.
    Malformed and healthy neighboring tenant documents remain separately scoped.
    No cross-tenant mutation is permitted.

AUTHORITY BOUNDARY:
    Persistence/read-integrity evidence only.
    Compatibility headers, caller roles, JWT claims, and permissions never grant
    registry authority.

FINANCIAL AUTHORITY BOUNDARY:
    No financial state or execution is touched.
    Kennel EOS remains the exclusive financial execution authority.

CERTIFICATION CLASS:
    INTEGRATION / REAL-MONGO / FAIL-CLOSED

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
===============================================================================
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

import tools.eos.saas.tenancy.tenant_registry as registry_module
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
    TenantRegistryError,
)


# =============================================================================
# CERTIFICATION CONSTANTS
# =============================================================================

VERSION = "v1.0.0-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS-REAL-MONGO-CERT"
CERT_URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_CERT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
INVALID_DOCUMENT = "TENANT_REGISTRY_GET_INVALID_DOCUMENT"
DATABASE_PREFIX = "tenant_registry_mapping_cert_"


# =============================================================================
# REAL-MONGO PERSISTED DOCUMENT BUILDERS
# =============================================================================


def _tenant_doc(tenant_id: str, *, name: str) -> dict[str, Any]:
    """Build one healthy generated persistence document."""
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


def _invalid_doc(tenant_id: str) -> dict[str, Any]:
    """Build a persisted document that enters and fails the real entity mapper."""
    doc = _tenant_doc(tenant_id, name="Malformed Tenant")
    doc["subscription"] = "corrupt"
    return doc


# =============================================================================
# UUID-BOUNDED REAL-MONGO CERTIFICATION STATE
# =============================================================================


@contextmanager
def _state() -> Iterator[
    tuple[
        Any,
        Collection[dict[str, Any]],
        str,
        str,
        str,
        str,
    ]
]:
    """Create, bind, yield, and destroy one isolated real-Mongo evidence scope."""
    uri = os.environ.get(CERT_URI_ENV, DEFAULT_CERT_URI)
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=5000,
    )

    database_name = f"{DATABASE_PREFIX}{uuid4().hex}"
    collection: Collection[dict[str, Any]] = client[database_name]["tenants"]

    valid_id = f"tenant-valid-{uuid4().hex}"
    malformed_id = f"tenant-malformed-{uuid4().hex}"
    neighbor_id = f"tenant-neighbor-{uuid4().hex}"

    original_collection = registry_module.tenants_collection

    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET

        collection.insert_many(
            [
                _tenant_doc(valid_id, name="Valid Tenant"),
                _invalid_doc(malformed_id),
                _tenant_doc(neighbor_id, name="Neighbor Tenant"),
            ]
        )

        registry_module.tenants_collection = collection

        yield (
            client,
            collection,
            database_name,
            valid_id,
            malformed_id,
            neighbor_id,
        )
    finally:
        registry_module.tenants_collection = original_collection
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


# =============================================================================
# HEALTHY GET / GENUINE ABSENCE REAL-MONGO CERTIFICATION
# =============================================================================


def test_real_mongo_valid_lookup_and_genuine_absence() -> None:
    """Real Mongo distinguishes healthy persisted truth from genuine absence."""
    with _state() as (_, collection, _, valid_id, _, _):
        found = TenantRegistry.get(valid_id)
        missing = TenantRegistry.get(f"missing-{uuid4().hex}")

        assert found is not None
        assert found.tenant_id == valid_id
        assert missing is None
        assert collection.count_documents({}) == 3


# =============================================================================
# INVALID PERSISTED TRUTH REAL-MONGO CERTIFICATION
# =============================================================================


def test_real_mongo_invalid_document_raises_exact_error_and_remains_persisted() -> None:
    """Malformed persisted truth raises exactly and remains non-destructively stored."""
    with _state() as (_, collection, _, _, malformed_id, _):
        before = collection.find_one({"tenant_id": malformed_id})
        assert before is not None

        with pytest.raises(TenantRegistryError) as raised:
            TenantRegistry.get(malformed_id)

        assert str(raised.value) == INVALID_DOCUMENT
        assert raised.value.__cause__ is None

        after = collection.find_one({"tenant_id": malformed_id})
        assert after == before
        assert collection.count_documents({"tenant_id": malformed_id}) == 1


def test_real_mongo_invalid_document_never_becomes_none() -> None:
    """Real persisted mapping corruption is structurally distinct from absence."""
    with _state() as (_, _, _, _, malformed_id, _):
        with pytest.raises(TenantRegistryError, match=f"^{INVALID_DOCUMENT}$"):
            TenantRegistry.get(malformed_id)


# =============================================================================
# TENANT ISOLATION / NON-MUTATION CERTIFICATION
# =============================================================================


def test_real_mongo_neighbor_remains_unchanged_after_invalid_read() -> None:
    """A malformed read cannot mutate or contaminate a healthy neighboring tenant."""
    with _state() as (_, collection, _, _, malformed_id, neighbor_id):
        neighbor_before = collection.find_one({"tenant_id": neighbor_id})
        assert neighbor_before is not None

        with pytest.raises(TenantRegistryError, match=f"^{INVALID_DOCUMENT}$"):
            TenantRegistry.get(malformed_id)

        assert collection.find_one({"tenant_id": neighbor_id}) == neighbor_before
        assert collection.count_documents({}) == 3


# =============================================================================
# LEGACY LIST BEHAVIOR REAL-MONGO CERTIFICATION
# =============================================================================


def test_real_mongo_list_preserves_skip_malformed_behavior() -> None:
    """Legacy list keeps total truth while excluding the unmappable item payload."""
    with _state() as (_, collection, _, valid_id, malformed_id, neighbor_id):
        result = TenantRegistry.list(skip=0, limit=20)

        assert result["total"] == 3

        returned_ids = {
            tenant.tenant_id
            for tenant in result["items"]
        }
        assert returned_ids == {valid_id, neighbor_id}
        assert malformed_id not in returned_ids
        assert collection.count_documents({}) == 3


# =============================================================================
# TRANSPORT NON-AUTHORITY REAL-MONGO CERTIFICATION
# =============================================================================


def test_real_mongo_compatibility_header_is_not_mapping_authority() -> None:
    """Compatibility header input cannot redirect an invalid persisted GET."""
    with _state() as (_, collection, _, _, malformed_id, neighbor_id):
        with pytest.raises(TenantRegistryError, match=f"^{INVALID_DOCUMENT}$"):
            TenantRegistry.get(
                malformed_id,
                tenant_id_header=neighbor_id,
            )

        assert collection.count_documents({"tenant_id": malformed_id}) == 1
        neighbor = collection.find_one({"tenant_id": neighbor_id})
        assert neighbor is not None
        assert neighbor["status"] == "ACTIVE"


# =============================================================================
# AUTHORITY-SURFACE REAL-MONGO CERTIFICATION
# =============================================================================


def test_real_mongo_registry_surface_has_no_role_jwt_permission_or_financial_authority() -> None:
    """Registry inputs expose no role/JWT/permission/financial grant path."""
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

    for method in (
        TenantRegistry.get,
        TenantRegistry.list,
        TenantRegistry.archive,
    ):
        assert not forbidden.intersection(inspect.signature(method).parameters)


# =============================================================================
# CLEANUP-SCOPE REAL-MONGO CERTIFICATION
# =============================================================================


def test_real_mongo_cleanup_scope_is_uuid_bounded() -> None:
    """Certification database naming is UUID-bounded and cleanup is contextual."""
    with _state() as (_, _, database_name, _, _, _):
        assert database_name.startswith(DATABASE_PREFIX)

        suffix = database_name.removeprefix(DATABASE_PREFIX)
        assert len(suffix) == 32
        int(suffix, 16)


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_tenant_registry_mapping_failure_semantics_real_mongo.py
# VERSION: v1.0.0-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo persistence/read-integrity evidence only; no authentication, membership, role, permission, JWT, HTTP, or financial authority
# TENANT POSTURE: existing malformed tenant truth never becomes absence and neighboring tenant truth remains unchanged
# FAIL-CLOSED POSTURE: real persisted corruption raises TENANT_REGISTRY_GET_INVALID_DOCUMENT while legacy list continues its bounded tolerant mapping behavior
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
