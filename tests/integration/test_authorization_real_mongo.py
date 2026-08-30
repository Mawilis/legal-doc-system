"""TITLE: WILSY OS Real-Mongo Current Authorization Integration Certification
VERSION: v1.0.1-WILSY-CURRENT-AUTHORIZATION-REAL-MONGO-INTEGRATION
AUTHORITY: Integration certification of final tenant-scoped authorization decisions over actual persisted current RoleAssignmentAuthority.
EPITOME: Proves frozen Python authorization consumes exact real-Mongo current role assignment truth and preserves principal/tenant scoping.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_authorization_real_mongo.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30
CHANGELOG: v1.0.1-WILSY-CURRENT-AUTHORIZATION-REAL-MONGO-INTEGRATION proves removed legacy and ambiguous permissions remain denied even with valid persisted current role assignments.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Dedicated synthetic integration records only; no production credentials, customer data, secrets, or financial records.
TENANT BOUNDARY: Every proof uses explicit principal/tenant/role natural keys and includes negative cross-tenant evidence.
AUTHORITY BOUNDARY: Real-Mongo current role-assignment composition into frozen authorization only; authentication, membership runtime, HTTP enforcement, and financial execution remain outside scope.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""
from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from typing import Any, cast

import pytest
from pymongo import MongoClient

from tools.eos.api.exceptions import ForbiddenOperationException
from tools.eos.auth.authorization import RequirePermission, RequireRole
from tools.eos.auth.identity import PrincipalStatus, SovereignIdentity
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentPersistedRecordInvalidError,
    RoleAssignmentRepository,
)

VERSION = "v1.0.1-WILSY-CURRENT-AUTHORIZATION-REAL-MONGO-INTEGRATION"
URI = os.getenv("TEST_VENDOR_MONGO_URI")


class CollectionRepository:
    """Bind frozen repository resolution to this fixture's isolated collection."""

    def __init__(self, collection: object) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, collection: object = None, *, session: object = None) -> RoleAssignmentAuthority:
        return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, self.collection, session=session)  # type: ignore[arg-type]


@pytest.fixture()
def mongo_context() -> Iterator[tuple[object, CollectionRepository]]:
    """Provide a UUID-isolated real-Mongo collection and deterministic cleanup."""
    if not URI:
        pytest.fail("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database = client[f"authorization_cert_{uuid.uuid4().hex}"]
    collection = database["role_assignments"]
    if client.admin.command("hello").get("setName") != "wilsyVendorCertRS":
        client.close()
        pytest.fail("wrong certification replica set")
    RoleAssignmentRepository.ensure_indexes(collection)
    try:
        yield collection, CollectionRepository(collection)
    finally:
        client.drop_database(database.name)
        client.close()


def identity(principal: str = "principal-p", tenant: str = "tenant-t", roles: list[str] | None = None, permissions: list[str] | None = None) -> SovereignIdentity:
    """Build an explicit already membership-admitted identity projection."""
    return SovereignIdentity(identity_id=principal, tenant_id=tenant, username="synthetic", email="synthetic@example.test", roles=roles or [], permissions=permissions or [], auth_method="JWT", status=PrincipalStatus.ACTIVE)


def authority(principal: str, tenant: str, role: str, status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE) -> RoleAssignmentAuthority:
    """Build revision-zero persisted assignment authority."""
    return RoleAssignmentAuthority(principal, tenant, role, status, 0)


def persist(collection: object, value: RoleAssignmentAuthority) -> None:
    """Insert one assignment through the frozen repository contract."""
    RoleAssignmentRepository.insert(value, collection)  # type: ignore[arg-type]


@pytest.mark.anyio
async def test_real_mongo_role_matrix(mongo_context: tuple[object, CollectionRepository]) -> None:
    """Prove active, absent, tenant, principal, revoked, and candidate role decisions."""
    collection, repository = mongo_context
    persist(collection, authority("principal-p", "tenant-t", "AUDITOR"))
    typed = cast(Any, repository)
    assert await RequireRole(["AUDITOR"]).__call__(identity(), repository=typed) is not None
    with pytest.raises(ForbiddenOperationException):
        await RequireRole(["MISSING"]).__call__(identity(), repository=typed)
    with pytest.raises(ForbiddenOperationException):
        await RequireRole(["AUDITOR"]).__call__(identity(tenant="tenant-other"), repository=typed)
    with pytest.raises(ForbiddenOperationException):
        await RequireRole(["AUDITOR"]).__call__(identity(principal="principal-other"), repository=typed)
    persist(collection, authority("principal-p", "tenant-t", "REVOKED_ROLE", RoleAssignmentStatus.REVOKED))
    with pytest.raises(ForbiddenOperationException):
        await RequireRole(["REVOKED_ROLE"]).__call__(identity(), repository=typed)
    persist(collection, authority("principal-p", "tenant-t", "SERVICE_WORKER"))
    assert await RequireRole(["AUDITOR", "SERVICE_WORKER"]).__call__(identity(), repository=typed) is not None


@pytest.mark.anyio
async def test_real_mongo_permission_projection_and_admin_literal(mongo_context: tuple[object, CollectionRepository]) -> None:
    """Prove governed permission definitions and persisted assignments dominate projections."""
    collection, repository = mongo_context
    persist(collection, authority("principal-p", "tenant-t", "SERVICE_WORKER"))
    typed = cast(Any, repository)
    with pytest.raises(ForbiddenOperationException):
        await RequirePermission("execution:trigger").__call__(identity(roles=[], permissions=[]), repository=typed)
    with pytest.raises(ForbiddenOperationException):
        await RequirePermission("admin:all").__call__(identity(roles=["SOVEREIGN_ARCHITECT"], permissions=["admin:all"]), repository=typed)
    persist(collection, authority("principal-p", "tenant-t", "SOVEREIGN_ARCHITECT"))
    with pytest.raises(ForbiddenOperationException):
        await RequirePermission("admin:all").__call__(identity(), repository=typed)
    persist(collection, authority("principal-p", "tenant-t", "ENTERPRISE_ADMIN"))
    with pytest.raises(ForbiddenOperationException):
        await RequirePermission("tenant:manage").__call__(identity(), repository=typed)
    persist(collection, authority("principal-p", "tenant-t", "AUDITOR"))
    assert await RequirePermission("audit:read").__call__(identity(roles=[], permissions=[]), repository=typed) is not None
    with pytest.raises(ForbiddenOperationException):
        await RequirePermission("tenant:delete").__call__(identity(), repository=typed)


def test_real_mongo_malformed_persisted_authority_is_bounded(mongo_context: tuple[object, CollectionRepository]) -> None:
    """Prove malformed persisted state is rejected by the frozen repository."""
    collection, _ = mongo_context
    collection.insert_one({"principal_id": "principal-p", "tenant_id": "tenant-t", "role_id": "AUDITOR", "status": "BROKEN", "revision": 0})  # type: ignore[attr-defined]
    with pytest.raises(RoleAssignmentPersistedRecordInvalidError):
        RoleAssignmentRepository.resolve("principal-p", "tenant-t", "AUDITOR", collection)  # type: ignore[arg-type]


# ARTIFACT: test_authorization_real_mongo.py
# VERSION: v1.0.1-WILSY-CURRENT-AUTHORIZATION-REAL-MONGO-INTEGRATION
# AUTHORITY BOUNDARY: real-Mongo current role-assignment integration into frozen tenant-scoped authorization decisions only
# TENANT POSTURE: exact principal/tenant/role authority keys with negative cross-tenant proof; no inference or default
# FAIL-CLOSED POSTURE: absent, revoked, malformed, cross-tenant, cross-principal, and projected-only authority never grants access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
