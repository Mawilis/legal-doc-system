# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION ARTIFACT
TENANT ROUTER — CONTROLLED GET + ARCHIVE — REAL-MONGO RUNTIME CERTIFICATE
===============================================================================

TITLE:
    WILSY OS Tenant Router GET + Archive Real-Mongo Runtime Certification

FILE:
    tests/integration/test_tenant_router_get_archive_real_mongo.py

VERSION:
    v1.0.0-TENANT-ROUTER-GET-ARCHIVE-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Isolated real-Mongo certification of activated tenant GET/archive HTTP wiring.

EPITOME:
    Proves the real tenant router, frozen durable authorization dependency, and
    real Mongo-backed TenantRegistry compose correctly for healthy GET, genuine
    absence, invalid persisted truth, exact path/scope isolation, soft archive,
    repeated archive no-change, preserved neighboring tenant truth, continued
    containment of global list/create/PUT, and UUID-bounded cleanup.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_router_get_archive_real_mongo.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.0.0-TENANT-ROUTER-GET-ARCHIVE-REAL-MONGO-CERT
        - Establishes B2B real-Mongo HTTP-to-registry certification.
        - Proves authorized healthy GET returns HTTP 200.
        - Proves genuine absence returns HTTP 404.
        - Proves invalid persisted tenant truth returns HTTP 503 and remains
          persisted.
        - Proves authorized scope/path mismatch returns HTTP 403 without
          cross-tenant mutation.
        - Proves DELETE performs soft archive only, preserves document count,
          and leaves neighboring tenant truth unchanged.
        - Proves repeated archive returns historical no-change HTTP 404.
        - Proves collection GET, POST, and PUT remain 503-contained.
        - Proves UUID-bounded database cleanup and registry collection restoration.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Local certification replica set only.
    Generated tenant/principal identifiers only.
    Real Mongo persistence is UUID-bounded and destroyed after each proof.
    Durable authorization readers are deterministic test-local current-truth
    fixtures; they do not replace the production authorization composition.

TENANT BOUNDARY:
    Exact own-tenant authorized scope must equal the path tenant before registry
    access. Neighboring generated tenant documents are independently verified
    against cross-tenant mutation.

AUTHORITY BOUNDARY:
    Evidence only. Production authentication/authorization code is used as wired;
    test dependency overrides provide deterministic principal/membership/role
    repository truth without creating alternate business-authority logic.

FINANCIAL AUTHORITY BOUNDARY:
    No financial state or execution is touched.
    Kennel EOS remains the exclusive financial execution authority.

CERTIFICATION CLASS:
    INTEGRATION / REAL-MONGO / HTTP-RUNTIME / FAIL-CLOSED

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
===============================================================================
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.collection import Collection

import tools.eos.api.tenant_authorization_http as boundary
import tools.eos.saas.tenancy.tenant_registry as registry_module
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.tenant_router import tenant_router
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
)


# =============================================================================
# CERTIFICATION CONSTANTS
# =============================================================================

VERSION = "v1.0.0-TENANT-ROUTER-GET-ARCHIVE-REAL-MONGO-CERT"

CERT_URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_CERT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "tenant_router_b2b_cert_"

_PID = "principal-b2b-real-mongo"


# =============================================================================
# DETERMINISTIC DURABLE-AUTHORITY READERS
# =============================================================================


class _RecordingReader:
    """Resolve deterministic current truth without mutation authority."""

    def __init__(self, values: dict[tuple[str, ...], object] | None = None) -> None:
        self.values = dict(values or {})
        self.read_calls: list[tuple[str, ...]] = []

    def resolve(self, *keys: str) -> object:
        """Resolve one exact authority key or raise its repository not-found type."""
        key = tuple(keys)
        self.read_calls.append(key)
        if key in self.values:
            return self.values[key]
        if len(key) == 1:
            raise PrincipalAuthorityNotFoundError(
                "PRINCIPAL_AUTHORITY_NOT_FOUND"
            )
        if len(key) == 2:
            raise TenantMembershipNotFoundError(
                "TENANT_MEMBERSHIP_NOT_FOUND"
            )
        raise RoleAssignmentNotFoundError(
            "ROLE_ASSIGNMENT_NOT_FOUND"
        )


# =============================================================================
# PERSISTED DOCUMENT BUILDERS
# =============================================================================


def _tenant_doc(
    tenant_id: str,
    *,
    name: str,
) -> dict[str, Any]:
    """Build one healthy generated persisted tenant document."""
    return {
        "tenant_id": tenant_id,
        "name": name,
        "organization": {
            "organization_name": name,
            "industry": "Legal",
            "plan": "ENTERPRISE",
            "legal_name": f"{name} Legal",
            "tax_id": None,
            "contact_email": None,
            "regions": ["Africa"],
            "created_at": "2026-08-30T00:00:00+00:00",
        },
        "industry": "Legal",
        "plan": "ENTERPRISE",
        "regions": ["Africa"],
        "status": "ACTIVE",
        "created_at": "2026-08-30T00:00:00+00:00",
        "alias": f"{tenant_id}-alias",
        "region": "ZA",
        "compliance_flags": {"certification": True},
        "proof_hash": f"proof-{tenant_id}",
        "verified": True,
    }


def _invalid_doc(tenant_id: str) -> dict[str, Any]:
    """Build a real persisted document that fails the production mapper."""
    document = _tenant_doc(
        tenant_id,
        name="Malformed Tenant",
    )
    document["subscription"] = "corrupt"
    return document


# =============================================================================
# AUTHORIZATION FIXTURE BUILDERS
# =============================================================================


def _identity() -> SovereignIdentity:
    """Build one authenticated identity; projected roles remain non-authority."""
    return SovereignIdentity(
        identity_id=_PID,
        tenant_id="wrong-token-tenant",
        username="b2b-real-mongo",
        email="b2b-real-mongo@example.test",
        auth_method="test",
        status=PrincipalStatus.ACTIVE,
        roles=["ROOT", "GLOBAL_ROOT", "ENTERPRISE_ADMIN"],
        permissions=["*", "tenant:profile:read", "tenant:lifecycle:archive"],
    )


def _app_for_scope(tenant_id: str) -> FastAPI:
    """Compose the real router with deterministic durable current-truth readers."""
    principal_reader = _RecordingReader(
        {
            (_PID,): PrincipalAuthority(
                _PID,
                PrincipalStatus.ACTIVE,
                0,
            ),
        }
    )
    membership_reader = _RecordingReader(
        {
            (_PID, tenant_id): TenantMembershipAuthority(
                _PID,
                tenant_id,
                TenantMembershipStatus.ACTIVE,
                0,
            ),
        }
    )
    role_reader = _RecordingReader(
        {
            (_PID, tenant_id, "tenant_owner"): RoleAssignmentAuthority(
                _PID,
                tenant_id,
                "tenant_owner",
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            (_PID, tenant_id, "ENTERPRISE_ADMIN"): RoleAssignmentAuthority(
                _PID,
                tenant_id,
                "ENTERPRISE_ADMIN",
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
        }
    )

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(tenant_router)

    app.dependency_overrides[boundary.get_current_identity] = _identity
    app.dependency_overrides[
        boundary.get_principal_authority_repository
    ] = lambda: principal_reader
    app.dependency_overrides[
        boundary.get_tenant_membership_repository
    ] = lambda: membership_reader
    app.dependency_overrides[
        boundary.get_role_assignment_repository
    ] = lambda: role_reader

    return app


# =============================================================================
# UUID-BOUNDED REAL-MONGO STATE
# =============================================================================


@contextmanager
def _state() -> Iterator[
    tuple[
        Collection[dict[str, Any]],
        str,
        str,
        str,
        str,
    ]
]:
    """Create isolated real-Mongo tenant truth and restore the registry globally."""
    uri = os.environ.get(
        CERT_URI_ENV,
        DEFAULT_CERT_URI,
    )
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=5000,
    )

    database_name = f"{DATABASE_PREFIX}{uuid4().hex}"
    collection: Collection[dict[str, Any]] = client[database_name]["tenants"]

    tenant_a = f"tenant-a-{uuid4().hex}"
    tenant_b = f"tenant-b-{uuid4().hex}"
    malformed_id = f"tenant-malformed-{uuid4().hex}"

    original_collection = registry_module.tenants_collection

    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET

        collection.insert_many(
            [
                _tenant_doc(
                    tenant_a,
                    name="Tenant A",
                ),
                _tenant_doc(
                    tenant_b,
                    name="Tenant B",
                ),
                _invalid_doc(malformed_id),
            ]
        )

        registry_module.tenants_collection = collection

        yield (
            collection,
            database_name,
            tenant_a,
            tenant_b,
            malformed_id,
        )
    finally:
        registry_module.tenants_collection = original_collection
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


# =============================================================================
# AUTHORIZED GET REAL-MONGO CERTIFICATION
# =============================================================================


def test_real_mongo_authorized_get_returns_healthy_tenant() -> None:
    """Authorized own-tenant HTTP GET reaches real Mongo and returns HTTP 200."""
    with _state() as (collection, _, tenant_a, _, _):
        app = _app_for_scope(tenant_a)

        with TestClient(app) as client:
            response = client.get(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_a},
            )

        assert response.status_code == 200
        payload = response.json()
        assert payload["tenant_id"] == tenant_a
        assert payload["name"] == "Tenant A"
        assert payload["status"] == "ACTIVE"
        assert payload["verified"] is True
        assert collection.count_documents({"tenant_id": tenant_a}) == 1
        assert collection.count_documents({}) == 3


def test_real_mongo_authorized_get_genuine_absence_is_404() -> None:
    """A genuinely missing own-tenant target maps to the bounded GET 404."""
    with _state() as (collection, _, tenant_a, _, _):
        missing_id = f"missing-{uuid4().hex}"
        app = _app_for_scope(missing_id)

        before = collection.count_documents({})

        with TestClient(app) as client:
            response = client.get(
                f"/api/tenants/{missing_id}",
                headers={"X-Tenant-ID": missing_id},
            )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Tenant not found."
        }
        assert collection.count_documents({}) == before


def test_real_mongo_invalid_persisted_get_is_503_and_non_destructive() -> None:
    """Malformed persisted truth reaches strict GET semantics and remains stored."""
    with _state() as (collection, _, _, _, malformed_id):
        app = _app_for_scope(malformed_id)
        before = collection.find_one({"tenant_id": malformed_id})
        assert before is not None

        with TestClient(app) as client:
            response = client.get(
                f"/api/tenants/{malformed_id}",
                headers={"X-Tenant-ID": malformed_id},
            )

        assert response.status_code == 503
        assert response.json() == {
            "detail": "TENANT_REGISTRY_GET_INVALID_DOCUMENT"
        }
        assert collection.find_one({"tenant_id": malformed_id}) == before
        assert collection.count_documents({}) == 3


# =============================================================================
# TENANT PATH / SCOPE ISOLATION REAL-MONGO CERTIFICATION
# =============================================================================


def test_real_mongo_authorized_scope_cannot_cross_to_other_path_tenant() -> None:
    """Authority for tenant-b cannot read or mutate tenant-a path truth."""
    with _state() as (collection, _, tenant_a, tenant_b, _):
        app = _app_for_scope(tenant_b)

        tenant_a_before = collection.find_one({"tenant_id": tenant_a})
        tenant_b_before = collection.find_one({"tenant_id": tenant_b})
        assert tenant_a_before is not None
        assert tenant_b_before is not None

        with TestClient(app) as client:
            get_response = client.get(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_b},
            )
            delete_response = client.delete(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_b},
            )

        assert get_response.status_code == 403
        assert get_response.json() == {
            "detail": "TENANT_SCOPE_PATH_MISMATCH"
        }
        assert delete_response.status_code == 403
        assert delete_response.json() == {
            "detail": "TENANT_SCOPE_PATH_MISMATCH"
        }
        assert collection.find_one({"tenant_id": tenant_a}) == tenant_a_before
        assert collection.find_one({"tenant_id": tenant_b}) == tenant_b_before
        assert collection.count_documents({}) == 3


# =============================================================================
# SOFT ARCHIVE REAL-MONGO CERTIFICATION
# =============================================================================


def test_real_mongo_authorized_delete_soft_archives_only() -> None:
    """Authorized DELETE changes only status and never deletes target or neighbor."""
    with _state() as (collection, _, tenant_a, tenant_b, _):
        app = _app_for_scope(tenant_a)

        target_before = collection.find_one({"tenant_id": tenant_a})
        neighbor_before = collection.find_one({"tenant_id": tenant_b})
        assert target_before is not None
        assert neighbor_before is not None
        count_before = collection.count_documents({})

        with TestClient(app) as client:
            response = client.delete(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_a},
            )

        assert response.status_code == 204
        assert response.content == b""

        target_after = collection.find_one({"tenant_id": tenant_a})
        assert target_after is not None
        assert target_after["status"] == "ARCHIVED"

        for key, value in target_before.items():
            if key != "status":
                assert target_after[key] == value

        assert collection.find_one({"tenant_id": tenant_b}) == neighbor_before
        assert collection.count_documents({}) == count_before


def test_real_mongo_repeated_archive_maps_no_change_to_historical_404() -> None:
    """A second soft archive makes no Mongo change and maps to exact HTTP 404."""
    with _state() as (collection, _, tenant_a, _, _):
        app = _app_for_scope(tenant_a)

        with TestClient(app) as client:
            first = client.delete(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_a},
            )
            second = client.delete(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_a},
            )

        assert first.status_code == 204
        assert second.status_code == 404
        assert second.json() == {
            "detail": "Tenant not found or already archived."
        }
        persisted = collection.find_one({"tenant_id": tenant_a})
        assert persisted is not None
        assert persisted["status"] == "ARCHIVED"
        assert collection.count_documents({}) == 3


# =============================================================================
# NON-MIGRATED ROUTE CONTAINMENT AGAINST REAL PERSISTENCE
# =============================================================================


def test_real_mongo_list_create_and_put_remain_contained_and_non_mutating() -> None:
    """Non-migrated routes remain exact 503 and leave real Mongo unchanged."""
    with _state() as (collection, _, tenant_a, _, _):
        app = _app_for_scope(tenant_a)

        before = list(
            collection.find({}).sort("tenant_id", 1)
        )

        headers = {
            "X-Tenant-ID": tenant_a,
            "X-Role": "GLOBAL_ROOT",
            "X-Permissions": "*",
        }

        with TestClient(app) as client:
            list_response = client.get(
                "/api/tenants",
                headers=headers,
            )
            create_response = client.post(
                "/api/tenants",
                headers=headers,
                json={"name": "Forbidden Create"},
            )
            put_response = client.put(
                f"/api/tenants/{tenant_a}",
                headers=headers,
                json={"name": "Forbidden Update"},
            )

        for response in (
            list_response,
            create_response,
            put_response,
        ):
            assert response.status_code == 503
            assert response.json() == {
                "detail": "TENANT_AUTHORITY_UNAVAILABLE"
            }

        after = list(
            collection.find({}).sort("tenant_id", 1)
        )
        assert after == before
        assert collection.count_documents({}) == 3


# =============================================================================
# CLEANUP / GLOBAL-REFERENCE CERTIFICATION
# =============================================================================


def test_real_mongo_scope_is_uuid_bounded_and_registry_reference_restores() -> None:
    """Certification DB naming is UUID-bounded and registry binding restores."""
    original_collection = registry_module.tenants_collection

    with _state() as (_, database_name, _, _, _):
        assert registry_module.tenants_collection is not original_collection
        assert database_name.startswith(DATABASE_PREFIX)

        suffix = database_name.removeprefix(DATABASE_PREFIX)
        assert len(suffix) == 32
        int(suffix, 16)

    assert registry_module.tenants_collection is original_collection


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_tenant_router_get_archive_real_mongo.py
# VERSION: v1.0.0-TENANT-ROUTER-GET-ARCHIVE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo HTTP wiring evidence only; production durable authorization logic remains frozen and no test-local projection grants business authority
# TENANT POSTURE: exact own-tenant scope/path congruence is required; malformed truth remains persisted; archive is soft and neighboring tenant truth remains unchanged; global list/create/PUT stay contained
# FAIL-CLOSED POSTURE: healthy GET is 200; genuine absence is 404; invalid persisted GET truth is 503; cross-tenant mismatch is 403; archive is 204 then bounded 404 on no-change
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
