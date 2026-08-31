# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION ARTIFACT
TENANT ROUTER — C2 PROFILE UPDATE — REAL-MONGO RUNTIME CERTIFICATE
===============================================================================

TITLE:
    WILSY OS Tenant Router C2 Profile Update Real-Mongo Runtime Certification

FILE:
    tests/integration/test_tenant_router_get_archive_real_mongo.py

VERSION:
    v1.1.0-TENANT-ROUTER-PROFILE-UPDATE-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Isolated actual-Mongo certification of GET/PUT/archive tenant HTTP wiring.

EPITOME:
    Evolves the B2B actual-Mongo certificate to prove controlled strict profile
    PUT through the real router, frozen durable authorization dependency, and C1
    TenantRegistry.update_profile. Proves all-six-field persistence, durable
    sector response, protected-truth preservation, checksum regeneration,
    proof-hash preservation, same-value idempotency, absence/corruption/scope
    failure semantics, schema non-mutation, soft archive, containment, neighboring
    tenant isolation, and UUID-bounded cleanup.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_router_get_archive_real_mongo.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-31

CHANGELOG:
    v1.1.0-TENANT-ROUTER-PROFILE-UPDATE-REAL-MONGO-CERT
        - Adds authorized all-six-field PUT persistence proof.
        - Adds checksum regeneration and proof-hash preservation proof.
        - Adds same-value idempotent PUT proof.
        - Adds PUT absence, malformed truth, forbidden-field, empty-payload, and
          scope-mismatch non-destructive failure proof.
        - Preserves B2B healthy GET, GET absence/corruption, soft archive,
          repeated archive, collection/list-create containment, tenant isolation,
          and UUID cleanup assertions.

    v1.0.0-TENANT-ROUTER-GET-ARCHIVE-REAL-MONGO-CERT
        - Certified B2B GET/archive actual-Mongo wiring while PUT remained
          contained.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Local certification replica set only. Generated tenant/principal identifiers
    only. Real Mongo persistence is UUID-bounded and destroyed after each proof.
    Durable authorization readers are deterministic current-truth fixtures and do
    not replace production authorization composition.

TENANT BOUNDARY:
    Exact own-tenant authorized scope must equal the path tenant before any
    registry access. Neighboring generated tenant documents are independently
    verified against cross-tenant mutation.

AUTHORITY BOUNDARY:
    Evidence only. Production authentication/authorization code and real registry
    persistence are used as wired; fixtures supply bounded current truth.

FINANCIAL AUTHORITY BOUNDARY:
    No financial state or execution is touched. PUT plan mutation is rejected.
    Kennel EOS remains the exclusive financial execution authority.

CERTIFICATION CLASS:
    INTEGRATION / REAL-MONGO / HTTP-RUNTIME / FAIL-CLOSED

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
===============================================================================
"""

from __future__ import annotations

import copy
import os
from contextlib import contextmanager
from typing import Any, Iterator
from uuid import uuid4

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


VERSION = "v1.1.0-TENANT-ROUTER-PROFILE-UPDATE-REAL-MONGO-CERT"

CERT_URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_CERT_URI = (
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "tenant_router_c2_cert_"

_PID = "principal-c2-real-mongo"


class _RecordingReader:
    """Resolve deterministic current truth without mutation authority."""

    def __init__(
        self,
        values: dict[tuple[str, ...], object] | None = None,
    ) -> None:
        self.values = dict(values or {})
        self.read_calls: list[tuple[str, ...]] = []

    def resolve(self, *keys: str) -> object:
        """Resolve one exact authority key or raise repository not-found."""
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
            "tax_id": f"tax-{tenant_id}",
            "contact_email": f"{tenant_id}@example.test",
            "regions": ["Africa"],
            "created_at": "2026-08-31T00:00:00+00:00",
        },
        "industry": "Legal",
        "legal_name": f"{name} Legal",
        "tax_id": f"tax-{tenant_id}",
        "contact_email": f"{tenant_id}@example.test",
        "plan": "ENTERPRISE",
        "regions": ["Africa"],
        "status": "ACTIVE",
        "created_at": "2026-08-31T00:00:00+00:00",
        "checksum": "legacy-checksum",
        "alias": f"{tenant_id}-alias",
        "region": "ZA",
        "sector": "Legal Services",
        "compliance_flags": {"certification": True},
        "proof_hash": f"proof-{tenant_id}",
        "verified": True,
    }


def _invalid_doc(tenant_id: str) -> dict[str, Any]:
    """Build persisted truth that fails the frozen mapping contract."""
    document = _tenant_doc(
        tenant_id,
        name="Malformed Tenant",
    )
    document["subscription"] = "corrupt"
    return document


def _identity() -> SovereignIdentity:
    """Build authenticated identity projections that remain non-authority."""
    return SovereignIdentity(
        identity_id=_PID,
        tenant_id="wrong-token-tenant",
        username="c2-real-mongo",
        email="c2-real-mongo@example.test",
        auth_method="test",
        status=PrincipalStatus.ACTIVE,
        roles=["ROOT", "GLOBAL_ROOT", "ENTERPRISE_ADMIN"],
        permissions=[
            "*",
            "tenant:profile:read",
            "tenant:profile:write",
            "tenant:lifecycle:archive",
        ],
    )


def _app_for_scope(tenant_id: str) -> FastAPI:
    """Compose the real router with deterministic current-truth readers."""
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
    """Create UUID-bounded real Mongo truth and restore registry globally."""
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
                _tenant_doc(tenant_a, name="Tenant A"),
                _tenant_doc(tenant_b, name="Tenant B"),
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


def _without_id(document: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return a comparison copy without Mongo _id."""
    if document is None:
        return None
    result = copy.deepcopy(document)
    result.pop("_id", None)
    return result


def test_real_mongo_authorized_get_returns_healthy_tenant_and_sector() -> None:
    """Authorized GET reaches real Mongo and exposes durable sector."""
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
        assert payload["sector"] == "Legal Services"
        assert payload["status"] == "ACTIVE"
        assert payload["verified"] is True
        assert collection.count_documents({"tenant_id": tenant_a}) == 1
        assert collection.count_documents({}) == 3


def test_real_mongo_authorized_get_genuine_absence_is_404() -> None:
    """Missing own-tenant target retains bounded GET 404."""
    with _state() as (collection, _, _, _, _):
        missing_id = f"missing-{uuid4().hex}"
        app = _app_for_scope(missing_id)
        before = collection.count_documents({})

        with TestClient(app) as client:
            response = client.get(
                f"/api/tenants/{missing_id}",
                headers={"X-Tenant-ID": missing_id},
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Tenant not found."}
        assert collection.count_documents({}) == before


def test_real_mongo_invalid_persisted_get_is_503_and_non_destructive() -> None:
    """Malformed persisted GET truth remains explicit and stored."""
    with _state() as (collection, _, _, _, malformed_id):
        app = _app_for_scope(malformed_id)
        before = _without_id(
            collection.find_one({"tenant_id": malformed_id})
        )

        with TestClient(app) as client:
            response = client.get(
                f"/api/tenants/{malformed_id}",
                headers={"X-Tenant-ID": malformed_id},
            )

        assert response.status_code == 503
        assert response.json() == {
            "detail": "TENANT_REGISTRY_GET_INVALID_DOCUMENT"
        }
        assert _without_id(
            collection.find_one({"tenant_id": malformed_id})
        ) == before


def test_real_mongo_authorized_put_persists_exact_six_and_preserves_protected_truth() -> None:
    """Authorized PUT mutates all six profile fields plus internal checksum only."""
    with _state() as (collection, _, tenant_a, tenant_b, _):
        app = _app_for_scope(tenant_a)

        target_before = _without_id(
            collection.find_one({"tenant_id": tenant_a})
        )
        neighbor_before = _without_id(
            collection.find_one({"tenant_id": tenant_b})
        )
        assert target_before is not None
        assert neighbor_before is not None
        count_before = collection.count_documents({})

        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_a},
                json={
                    "name": "Tenant Alpha",
                    "alias": "alpha",
                    "industry": "Technology",
                    "region": "EU",
                    "sector": "AI",
                    "legal_name": "Tenant Alpha Legal",
                },
            )

        assert response.status_code == 200
        payload = response.json()
        assert payload["tenant_id"] == tenant_a
        assert payload["name"] == "Tenant Alpha"
        assert payload["alias"] == "alpha"
        assert payload["industry"] == "Technology"
        assert payload["region"] == "EU"
        assert payload["sector"] == "AI"
        assert payload["legal_name"] == "Tenant Alpha Legal"

        persisted = _without_id(
            collection.find_one({"tenant_id": tenant_a})
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
            "created_at",
            "proof_hash",
        ):
            assert persisted[field_name] == target_before[field_name]

        assert persisted["checksum"] != target_before["checksum"]
        assert persisted["proof_hash"] == target_before["proof_hash"]
        assert _without_id(
            collection.find_one({"tenant_id": tenant_b})
        ) == neighbor_before
        assert collection.count_documents({}) == count_before


def test_real_mongo_put_same_value_is_idempotent_200() -> None:
    """Repeated canonical same-value PUT leaves real persisted truth unchanged."""
    with _state() as (collection, _, tenant_a, _, _):
        app = _app_for_scope(tenant_a)

        with TestClient(app) as client:
            first = client.put(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_a},
                json={"sector": "Legal Services"},
            )
            assert first.status_code == 200

            before_repeat = _without_id(
                collection.find_one({"tenant_id": tenant_a})
            )

            second = client.put(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_a},
                json={"sector": "Legal Services"},
            )

        after_repeat = _without_id(
            collection.find_one({"tenant_id": tenant_a})
        )
        assert second.status_code == 200
        assert second.json()["sector"] == "Legal Services"
        assert after_repeat == before_repeat


def test_real_mongo_put_genuine_absence_is_404_and_non_mutating() -> None:
    """Missing PUT target returns 404 without changing neighbors."""
    with _state() as (collection, _, tenant_a, _, _):
        missing_id = f"missing-{uuid4().hex}"
        app = _app_for_scope(missing_id)
        before = list(collection.find({}).sort("tenant_id", 1))

        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{missing_id}",
                headers={"X-Tenant-ID": missing_id},
                json={"alias": "missing"},
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Tenant not found."}
        after = list(collection.find({}).sort("tenant_id", 1))
        assert after == before
        assert collection.count_documents({"tenant_id": tenant_a}) == 1


def test_real_mongo_put_invalid_persisted_truth_is_503_and_non_destructive() -> None:
    """Malformed matching tenant fails strict PUT and remains unchanged."""
    with _state() as (collection, _, _, _, malformed_id):
        app = _app_for_scope(malformed_id)
        before = _without_id(
            collection.find_one({"tenant_id": malformed_id})
        )

        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{malformed_id}",
                headers={"X-Tenant-ID": malformed_id},
                json={"alias": "must-not-write"},
            )

        assert response.status_code == 503
        assert response.json() == {
            "detail": "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT"
        }
        assert _without_id(
            collection.find_one({"tenant_id": malformed_id})
        ) == before


def test_real_mongo_put_forbidden_field_is_422_and_non_mutating() -> None:
    """Schema-protected lifecycle/billing input cannot mutate real Mongo."""
    with _state() as (collection, _, tenant_a, _, _):
        app = _app_for_scope(tenant_a)
        before = _without_id(
            collection.find_one({"tenant_id": tenant_a})
        )

        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_a},
                json={
                    "alias": "attacker",
                    "status": "ARCHIVED",
                    "plan": "FREE",
                },
            )

        assert response.status_code == 422
        assert _without_id(
            collection.find_one({"tenant_id": tenant_a})
        ) == before


def test_real_mongo_put_empty_payload_is_422_and_non_mutating() -> None:
    """Empty profile mutation reaches strict registry EMPTY and changes nothing."""
    with _state() as (collection, _, tenant_a, _, _):
        app = _app_for_scope(tenant_a)
        before = _without_id(
            collection.find_one({"tenant_id": tenant_a})
        )

        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_a},
                json={},
            )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "TENANT_REGISTRY_PROFILE_UPDATE_EMPTY"
        }
        assert _without_id(
            collection.find_one({"tenant_id": tenant_a})
        ) == before


def test_real_mongo_authorized_scope_cannot_cross_to_other_path_tenant() -> None:
    """Authority for tenant-b cannot read, mutate, or archive tenant-a path truth."""
    with _state() as (collection, _, tenant_a, tenant_b, _):
        app = _app_for_scope(tenant_b)

        tenant_a_before = _without_id(
            collection.find_one({"tenant_id": tenant_a})
        )
        tenant_b_before = _without_id(
            collection.find_one({"tenant_id": tenant_b})
        )

        with TestClient(app) as client:
            get_response = client.get(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_b},
            )
            put_response = client.put(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_b},
                json={"alias": "cross-tenant"},
            )
            delete_response = client.delete(
                f"/api/tenants/{tenant_a}",
                headers={"X-Tenant-ID": tenant_b},
            )

        for response in (get_response, put_response, delete_response):
            assert response.status_code == 403
            assert response.json() == {
                "detail": "TENANT_SCOPE_PATH_MISMATCH"
            }

        assert _without_id(
            collection.find_one({"tenant_id": tenant_a})
        ) == tenant_a_before
        assert _without_id(
            collection.find_one({"tenant_id": tenant_b})
        ) == tenant_b_before
        assert collection.count_documents({}) == 3


def test_real_mongo_authorized_delete_soft_archives_only() -> None:
    """Authorized DELETE still changes only status and never deletes."""
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
        target_after = collection.find_one({"tenant_id": tenant_a})
        assert target_after is not None
        assert target_after["status"] == "ARCHIVED"

        for key, value in target_before.items():
            if key != "status":
                assert target_after[key] == value

        assert collection.find_one({"tenant_id": tenant_b}) == neighbor_before
        assert collection.count_documents({}) == count_before


def test_real_mongo_repeated_archive_maps_no_change_to_historical_404() -> None:
    """Second archive retains historical no-change HTTP 404."""
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


def test_real_mongo_list_and_create_remain_contained_and_non_mutating() -> None:
    """The two non-migrated routes remain 503 and leave Mongo unchanged."""
    with _state() as (collection, _, tenant_a, _, _):
        app = _app_for_scope(tenant_a)
        before = list(collection.find({}).sort("tenant_id", 1))

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

        for response in (list_response, create_response):
            assert response.status_code == 503
            assert response.json() == {
                "detail": "TENANT_AUTHORITY_UNAVAILABLE"
            }

        after = list(collection.find({}).sort("tenant_id", 1))
        assert after == before
        assert collection.count_documents({}) == 3


def test_real_mongo_scope_is_uuid_bounded_and_registry_reference_restores() -> None:
    """Certification database is UUID-bounded and global registry binding restores."""
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
# VERSION: v1.1.0-TENANT-ROUTER-PROFILE-UPDATE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual-Mongo HTTP wiring evidence only; production durable authorization and strict registry persistence remain the governing authorities
# TENANT POSTURE: exact own-tenant scope/path congruence gates GET/PUT/archive; all-six-field PUT is isolated to its target; malformed truth remains stored; collection GET and POST stay contained
# FAIL-CLOSED POSTURE: GET retains 200/404/503; PUT proves 200/403/404/422/503 with protected-field nonmutation and strict update_profile semantics; archive remains soft 204 then bounded 404
# FINANCIAL EXECUTION AUTHORITY: None. Plan mutation is rejected; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
