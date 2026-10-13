"""TITLE: WILSY OS FastAPI Current Authorization HTTP Integration Certification
VERSION: v1.0.2-WILSY-CURRENT-AUTHORIZATION-HTTP-INTEGRATION
AUTHORITY: Real FastAPI composition over current principal, tenant membership, and role-assignment authority.
EPITOME: Proves bearer authentication, explicit tenant admission, and current role/permission enforcement at an HTTP boundary.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_authorization_http.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30
CHANGELOG: v1.0.2-WILSY-CURRENT-AUTHORIZATION-HTTP-INTEGRATION migrates synthetic bearer credentials to the current explicit ACCESS purpose + durable credential-revision authentication contract, binds AuthRegistry and canonical TenantRegistry to the UUID-isolated real-Mongo certificate database, and constructs expired-token adversarial evidence without weakening the positive-duration production issuer. v1.0.1-WILSY-CURRENT-AUTHORIZATION-HTTP-INTEGRATION corrects the stale SERVICE_WORKER/execution:trigger allow assertion to the canonical fail-closed denial contract and strengthens the certificate against JWT role/permission projections. v1.0.0-WILSY-CURRENT-AUTHORIZATION-HTTP-INTEGRATION established the test-local FastAPI certification surface without production startup.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Synthetic identities, deterministic test secret, UUID-isolated Mongo, bounded responses, and no credential logging.
TENANT BOUNDARY: X-Tenant-ID and every persistence lookup are explicit and tenant-scoped; no default or global tenant exists.
AUTHORITY BOUNDARY: Certifies only FastAPI composition of frozen authentication, membership, role, and permission authorities.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from collections.abc import Iterator
from typing import Any, cast

os.environ.setdefault("WILSY_JWT_SECRET", "AUTHORIZATION-HTTP-CERT-ONLY-SECRET")

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient

from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.authentication import get_current_identity, get_principal_authority_repository
from tools.eos.auth.authorization import RequirePermission, RequireRole, get_role_assignment_repository
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.jwt_provider import TokenPurpose, create_access_token
import tools.eos.saas.auth.auth_registry as auth_registry_module
import tools.eos.saas.tenancy.tenant_registry as tenant_registry_module
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository, RoleAssignmentRepositoryError
from tools.eos.auth.tenant_access import get_current_tenant_identity, get_tenant_membership_repository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository, TenantMembershipRepositoryError

VERSION = "v1.0.2-WILSY-CURRENT-AUTHORIZATION-HTTP-INTEGRATION"
URI = os.getenv("TEST_VENDOR_MONGO_URI")


class PrincipalFacade:
    def __init__(self, collection: Any, failure: bool = False) -> None: self.collection, self.failure = collection, failure
    def get(self, principal_id: str, collection: Any = None, *, session: Any = None) -> PrincipalAuthority:
        if self.failure: raise PrincipalAuthorityRepositoryError("principal-internal-marker")
        return PrincipalAuthorityRepository.get(principal_id, self.collection, session=session)


class MembershipFacade:
    def __init__(self, collection: Any, failure: bool = False) -> None: self.collection, self.failure = collection, failure
    def resolve(self, principal_id: str, tenant_id: str, collection: Any = None, *, session: Any = None) -> TenantMembershipAuthority:
        if self.failure: raise TenantMembershipRepositoryError("tenant-internal-marker")
        return TenantMembershipRepository.resolve(principal_id, tenant_id, self.collection, session=session)


class RoleFacade:
    def __init__(self, collection: Any, failure: bool = False) -> None: self.collection, self.failure = collection, failure
    def resolve(self, principal_id: str, tenant_id: str, role_id: str, collection: Any = None, *, session: Any = None) -> RoleAssignmentAuthority:
        if self.failure: raise RoleAssignmentRepositoryError("role-internal-marker")
        return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, self.collection, session=session)


@pytest.fixture()
def context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[Any, Any, Any, Any, Any]]:
    """Yield isolated durable authentication + authorization truth."""
    if not URI:
        pytest.fail("TEST_VENDOR_MONGO_URI is required")

    mongo = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
    )

    if (
        mongo.admin.command("hello").get("setName")
        != "wilsyVendorCertRS"
    ):
        mongo.close()
        pytest.fail("wrong certification replica set")

    database = mongo[
        f"authorization_http_cert_{uuid.uuid4().hex}"
    ]

    principals = database["principal_authorities"]
    memberships = database["tenant_memberships"]
    roles = database["role_assignments"]
    users = database["users"]

    PrincipalAuthorityRepository.ensure_indexes(
        principals
    )
    TenantMembershipRepository.ensure_indexes(
        memberships
    )
    RoleAssignmentRepository.ensure_indexes(
        roles
    )

    # Bind the production AuthRegistry's kernel database lookup to this
    # certificate's UUID-isolated real-Mongo database. Authentication remains
    # real; get_current_identity is not overridden.
    monkeypatch.setattr(
        auth_registry_module.kernel_db,
        "get_database",
        lambda: database,
    )

    # Bind canonical TenantRegistry resolution to this same isolated database.
    monkeypatch.setattr(
        tenant_registry_module,
        "tenants_collection",
        database["tenants"],
    )

    for tenant_id in (
        "tenant-t",
        "tenant-other",
    ):
        result = TenantRegistry.create(
            {
                "name": (
                    "Authorization HTTP "
                    f"Certificate {tenant_id}"
                ),
                "tenant_id": tenant_id,
            }
        )

        if result.get("success") is not True:
            pytest.fail(
                "canonical tenant fixture creation failed"
            )

    # Durable authentication rows are distinct from PrincipalAuthority,
    # TenantMembership and RoleAssignment. Their sole purpose here is to
    # provide the exact credential-revision authority demanded by the real
    # authentication dependency.
    users.insert_many(
        [
            {
                "user_id": "principal-p",
                "email": "principal-p@wilsyos.org",
                "firstName": "Principal",
                "lastName": "P",
                "role": "USER",
                "permissions": [],
                "tenantId": "tenant-t",
                "passwordHash": "bcrypt-test-only",
                "credential_revision": 0,
                "mfaRegistered": False,
                "hasSignedCovenant": False,
            },
            {
                "user_id": "principal-p",
                "email": "principal-p-other@wilsyos.org",
                "firstName": "Principal",
                "lastName": "P",
                "role": "USER",
                "permissions": [],
                "tenantId": "tenant-other",
                "passwordHash": "bcrypt-test-only",
                "credential_revision": 0,
                "mfaRegistered": False,
                "hasSignedCovenant": False,
            },
            {
                "user_id": "principal-other",
                "email": "principal-other@wilsyos.org",
                "firstName": "Principal",
                "lastName": "Other",
                "role": "USER",
                "permissions": [],
                "tenantId": "tenant-t",
                "passwordHash": "bcrypt-test-only",
                "credential_revision": 0,
                "mfaRegistered": False,
                "hasSignedCovenant": False,
            },
        ]
    )

    app = FastAPI()
    register_error_handlers(
        app,
        debug=False,
    )
    app.dependency_overrides[get_principal_authority_repository] = lambda: PrincipalFacade(principals)
    app.dependency_overrides[get_tenant_membership_repository] = lambda: MembershipFacade(memberships)
    app.dependency_overrides[get_role_assignment_repository] = lambda: RoleFacade(roles)

    @app.get("/cert/role")
    async def cert_role(identity: SovereignIdentity = Depends(RequireRole(["ENTERPRISE_ADMIN"]))) -> dict[str, bool]:
        return {"authorized": True}

    @app.get("/cert/permission")
    async def cert_permission(identity: SovereignIdentity = Depends(RequirePermission("execution:trigger"))) -> dict[str, bool]:
        return {"authorized": True}

    try: yield principals, memberships, roles, app, mongo
    finally: mongo.drop_database(database.name); mongo.close()


def seed(context: tuple[Any, Any, Any, Any, Any], principal: str = "principal-p", tenant: str = "tenant-t", role: str = "ENTERPRISE_ADMIN", principal_status: PrincipalStatus = PrincipalStatus.ACTIVE, membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE, role_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE) -> None:
    principals, memberships, roles, _, _ = context
    PrincipalAuthorityRepository.create(PrincipalAuthority(principal, principal_status, 0), principals)
    TenantMembershipRepository.insert(TenantMembershipAuthority(principal, tenant, membership_status, 0), memberships)
    RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal, tenant, role, role_status, 0), roles)


def _base64url(value: bytes) -> str:
    """Encode deterministic JWT material for adversarial expiry evidence."""
    return (
        base64.urlsafe_b64encode(value)
        .rstrip(b"=")
        .decode("ascii")
    )


def _expired_access_token(
    *,
    principal: str,
    tenant: str,
    projected: bool,
) -> str:
    """Create an already-expired test JWT without weakening the issuer."""
    now = int(time.time())

    payload = {
        "identity_id": principal,
        "tenant_id": tenant,
        "roles": (
            ["ENTERPRISE_ADMIN"]
            if projected
            else []
        ),
        "permissions": (
            ["execution:trigger"]
            if projected
            else []
        ),
        "token_purpose": TokenPurpose.ACCESS.value,
        "credential_revision": 0,
        "iat": now - 60,
        "exp": now - 1,
    }

    header = {
        "alg": "HS256",
        "typ": "JWT",
    }

    encoded_header = _base64url(
        json.dumps(
            header,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )

    encoded_payload = _base64url(
        json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )

    signing_input = (
        f"{encoded_header}.{encoded_payload}"
    )

    secret = os.environ[
        "WILSY_JWT_SECRET"
    ]

    signature = _base64url(
        hmac.new(
            secret.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    )

    return (
        f"{signing_input}.{signature}"
    )


def token(
    principal: str = "principal-p",
    tenant: str = "tenant-t",
    projected: bool = False,
    expires: int = 3600,
) -> str:
    """Create one current ACCESS JWT bound to durable revision zero."""
    if expires <= 0:
        return _expired_access_token(
            principal=principal,
            tenant=tenant,
            projected=projected,
        )

    return create_access_token(
        {
            "identity_id": principal,
            "tenant_id": tenant,
            "roles": (
                ["ENTERPRISE_ADMIN"]
                if projected
                else []
            ),
            "permissions": (
                ["execution:trigger"]
                if projected
                else []
            ),
        },
        expires_in_seconds=expires,
        token_purpose=TokenPurpose.ACCESS,
        credential_revision=0,
    )


def client(app: FastAPI) -> TestClient: return TestClient(app, raise_server_exceptions=False)


def assert_error(response: Any, status_code: int) -> None:
    assert response.status_code == status_code
    body = response.json(); assert body["success"] is False; assert "internal-marker" not in response.text


def test_full_current_authority_allows(context: tuple[Any, Any, Any, Any, Any]) -> None:
    seed(context); response = client(context[3]).get("/cert/role", headers={"Authorization": f"Bearer {token()}" , "X-Tenant-ID": "tenant-t"}); assert response.status_code == 200


def test_projection_without_assignment_denies(context: tuple[Any, Any, Any, Any, Any]) -> None:
    seed(context, role="OTHER"); assert_error(client(context[3]).get("/cert/role", headers={"Authorization": f"Bearer {token(projected=True)}", "X-Tenant-ID": "tenant-t"}), 403)


@pytest.mark.parametrize("tenant, principal", [("tenant-other", "principal-p"), ("tenant-t", "principal-other")])
def test_wrong_scope_denies(context: tuple[Any, Any, Any, Any, Any], tenant: str, principal: str) -> None:
    seed(context); assert_error(client(context[3]).get("/cert/role", headers={"Authorization": f"Bearer {token(principal=principal, tenant=tenant)}", "X-Tenant-ID": tenant}), 401)


def test_revoked_role_denies(context: tuple[Any, Any, Any, Any, Any]) -> None:
    seed(context, role_status=RoleAssignmentStatus.REVOKED); assert_error(client(context[3]).get("/cert/role", headers={"Authorization": f"Bearer {token()}", "X-Tenant-ID": "tenant-t"}), 403)


@pytest.mark.parametrize("headers", [{"Authorization": f"Bearer {token()}"}, {"Authorization": "Bearer malformed"}])
def test_missing_tenant_or_invalid_token_denies(context: tuple[Any, Any, Any, Any, Any], headers: dict[str, str]) -> None:
    seed(context); assert_error(client(context[3]).get("/cert/role", headers=headers), 401)


@pytest.mark.parametrize("membership_status", [TenantMembershipStatus.REVOKED, TenantMembershipStatus.SUSPENDED])
def test_non_active_membership_denies(context: tuple[Any, Any, Any, Any, Any], membership_status: TenantMembershipStatus) -> None:
    seed(context, membership_status=membership_status); assert_error(client(context[3]).get("/cert/role", headers={"Authorization": f"Bearer {token()}", "X-Tenant-ID": "tenant-t"}), 401)


def test_non_active_principal_denies(context: tuple[Any, Any, Any, Any, Any]) -> None:
    seed(context, principal_status=PrincipalStatus.REVOKED); assert_error(client(context[3]).get("/cert/role", headers={"Authorization": f"Bearer {token()}", "X-Tenant-ID": "tenant-t"}), 401)


def test_blocked_permission_and_admin_projection_boundary_denies(context: tuple[Any, Any, Any, Any, Any]) -> None:
    """Blocked permission and JWT projections cannot override current authority."""
    seed(context, role="SERVICE_WORKER")

    for projected in (False, True):
        response = client(context[3]).get(
            "/cert/permission",
            headers={
                "Authorization": f"Bearer {token(projected=projected)}",
                "X-Tenant-ID": "tenant-t",
            },
        )
        assert_error(response, 403)


def test_expired_token_denies(context: tuple[Any, Any, Any, Any, Any]) -> None:
    seed(context); assert_error(client(context[3]).get("/cert/role", headers={"Authorization": f"Bearer {token(expires=-1)}", "X-Tenant-ID": "tenant-t"}), 401)


def test_repository_failures_are_bounded(context: tuple[Any, Any, Any, Any, Any]) -> None:
    principals, memberships, roles, app, _ = context
    seed(context)
    app.dependency_overrides[get_principal_authority_repository] = lambda: PrincipalFacade(principals, True)
    assert_error(client(app).get("/cert/role", headers={"Authorization": f"Bearer {token()}", "X-Tenant-ID": "tenant-t"}), 401)
    app.dependency_overrides[get_principal_authority_repository] = lambda: PrincipalFacade(principals)
    app.dependency_overrides[get_tenant_membership_repository] = lambda: MembershipFacade(memberships, True)
    assert_error(client(app).get("/cert/role", headers={"Authorization": f"Bearer {token()}", "X-Tenant-ID": "tenant-t"}), 401)
    app.dependency_overrides[get_tenant_membership_repository] = lambda: MembershipFacade(memberships)
    app.dependency_overrides[get_role_assignment_repository] = lambda: RoleFacade(roles, True)
    assert_error(client(app).get("/cert/role", headers={"Authorization": f"Bearer {token()}", "X-Tenant-ID": "tenant-t"}), 403)


# ARTIFACT: tests/integration/test_authorization_http.py
# VERSION: v1.0.1-WILSY-CURRENT-AUTHORIZATION-HTTP-INTEGRATION
# AUTHORITY BOUNDARY: test-local FastAPI composition of current principal, membership, role, and permission authority only
# TENANT POSTURE: explicit X-Tenant-ID and exact tenant-scoped persistence keys; no inference or default
# FAIL-CLOSED POSTURE: invalid credentials, inactive authority, absent authority, cross-scope authority, and repository failures deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
