"""TITLE: WILSY OS Plan Router Authority Real-Mongo Certificate.
VERSION: v1.1.2-PLAN-ROUTER-VERSION-ALIGNMENT-CERT
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certifies private Plan HTTP authority against actual isolated Mongo
principal, membership, role-assignment and Plan catalogue truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_plan_router_authority_real_mongo.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-03.
CHANGELOG:
    v1.1.2-PLAN-ROUTER-VERSION-ALIGNMENT-CERT aligns the static contract with the current Plan Router production and certificate identities.
    v1.1.1-PLAN-ROUTER-GLOBAL-PLAN-TYPING-CERT widens only the direct Plan fixture tenant annotation to accept
    tenantless/global catalogue evidence required by exact-tenant denial certification.
    v1.1.0-PLAN-ROUTER-EXACT-TENANT-CERT certifies authenticated tenants cannot list,
    read, update or archive tenantless/global Plans through /api/plans.
    v1.0.2-PLAN-ROUTER-RESPONSE-LIFECYCLE-CERT certifies complete response-formatting 503 containment and
    MongoClient closure from the first post-construction setup action.
    v1.0.1-PLAN-ROUTER-AUTHORITY-REMEDIATION-CERT certifies fail-closed fixture cleanup,
    bounded Plan-not-found responses, evidence-serialization 503
    containment, and the current HTTP 422 compatibility contract.
    v1.0.0-PLAN-ROUTER-AUTHORITY-REAL-MONGO-CERT establishes real-Mongo HTTP
    proof for plan:read/plan:manage, exact tenant isolation, body redirect
    denial, role separation and bounded persistence failure semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated local certification database only;
generated principal/tenant identifiers; all databases are destroyed after use.
TENANT BOUNDARY: Tests require current ACTIVE membership in the exact selected
tenant and prove body fields, JWT projections and neighboring tenant data cannot
manufacture cross-tenant Plan authority.
AUTHORITY BOUNDARY: Evidence only. Production authentication, membership,
role-assignment, permission and Plan Router composition execute unchanged.
FINANCIAL AUTHORITY BOUNDARY: No payment execution occurs. Kennel EOS remains
the exclusive financial execution authority.
CERTIFICATION CLASS: INTEGRATION / REAL-MONGO / HTTP-RUNTIME / FAIL-CLOSED.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as registry_module
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.plan_router import (
    PLAN_MANAGE_PERMISSION,
    PLAN_READ_PERMISSION,
    VERSION as PLAN_ROUTER_VERSION,
    plan_router,
)
from tools.eos.auth.authentication import (
    get_principal_authority_repository,
)
from tools.eos.auth.authorization import (
    get_role_assignment_repository,
)
from tools.eos.auth.jwt_provider import (
    create_access_token,
)
from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)
from tools.eos.auth.principal_authority import (
    PrincipalAuthority,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.roles import (
    get_roles_granting_permission,
)
from tools.eos.auth.tenant_access import (
    get_tenant_membership_repository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.saas.billing.plan_registry import (
    PlanRegistry,
)


VERSION = (
    "v1.1.2-PLAN-ROUTER-VERSION-ALIGNMENT-CERT"
)

URI = os.getenv(
    "TEST_VENDOR_MONGO_URI"
)

EXPECTED_REPLICA_SET = (
    "wilsyVendorCertRS"
)

DATABASE_PREFIX = (
    "plan_router_auth_cert_"
)

_PRINCIPAL = (
    "principal-plan-router-cert"
)

_TENANT_A = (
    "tenant-plan-router-a"
)

_TENANT_B = (
    "tenant-plan-router-b"
)


@dataclass
class Context:
    """Actual-Mongo resources for one isolated Plan HTTP certification."""

    client: MongoClient[Any]
    database_name: str
    principals: Collection[dict[str, Any]]
    memberships: Collection[dict[str, Any]]
    roles: Collection[dict[str, Any]]
    plans: Collection[dict[str, Any]]
    app: FastAPI


class PrincipalFacade:
    """Bind current authentication authority to actual isolated Mongo."""

    def __init__(
        self,
        collection: Collection[dict[str, Any]],
    ) -> None:
        self.collection = collection

    def get(
        self,
        principal_id: str,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> PrincipalAuthority:
        """Resolve current persisted principal truth."""
        try:
            return PrincipalAuthorityRepository.get(
                principal_id,
                self.collection,
                session=session,
            )
        except PrincipalAuthorityRepositoryError:
            raise


class MembershipFacade:
    """Bind membership authority to actual isolated Mongo."""

    def __init__(
        self,
        collection: Collection[dict[str, Any]],
    ) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> TenantMembershipAuthority:
        """Resolve current persisted membership truth."""
        try:
            return TenantMembershipRepository.resolve(
                principal_id,
                tenant_id,
                self.collection,
                session=session,
            )
        except TenantMembershipRepositoryError:
            raise


class RoleFacade:
    """Bind permission possession authority to actual isolated Mongo."""

    def __init__(
        self,
        collection: Collection[dict[str, Any]],
    ) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> RoleAssignmentAuthority:
        """Resolve current persisted role-assignment truth."""
        try:
            return RoleAssignmentRepository.resolve(
                principal_id,
                tenant_id,
                role_id,
                self.collection,
                session=session,
            )
        except RoleAssignmentRepositoryError:
            raise


@pytest.fixture(
    scope="module"
)
def context() -> Iterator[Context]:
    """Create isolated actual authority plus Plan catalogue persistence."""
    if not URI:
        pytest.fail(
            "TEST_VENDOR_MONGO_URI is required"
        )

    mongo: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
    )
    try:

        hello = mongo.admin.command(
            "hello"
        )

        if (
            hello.get(
                "setName"
            )
            != EXPECTED_REPLICA_SET
        ):
            pytest.fail(
                "wrong certification replica set"
            )

        if (
            hello.get(
                "isWritablePrimary"
            )
            is not True
        ):
            pytest.fail(
                "certification Mongo is not writable primary"
            )

        database_name = (
            DATABASE_PREFIX
            + uuid.uuid4().hex
        )

        if len(
            database_name.encode(
                "utf-8"
            )
        ) > 63:
            pytest.fail(
                "certification database namespace too long"
            )

        database = mongo[
            database_name
        ]

        principals = database[
            "principal_authorities"
        ]

        memberships = database[
            "tenant_memberships"
        ]

        roles = database[
            "role_assignments"
        ]

        plans: Collection[
            dict[str, Any]
        ] = database.get_collection(
            "plans",
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
            read_concern=ReadConcern(
                "majority"
            ),
        )

        original_collection = (
            registry_module.plans_collection
        )

        try:
            PrincipalAuthorityRepository.ensure_indexes(
                principals
            )

            TenantMembershipRepository.ensure_indexes(
                memberships
            )

            RoleAssignmentRepository.ensure_indexes(
                roles
            )

            registry_module.plans_collection = (
                plans
            )

            PlanRegistry._ensure_indexes()

            app = FastAPI()

            register_error_handlers(
                app,
                debug=False,
            )

            app.include_router(
                plan_router
            )

            app.dependency_overrides[
                get_principal_authority_repository
            ] = lambda: PrincipalFacade(
                principals
            )

            app.dependency_overrides[
                get_tenant_membership_repository
            ] = lambda: MembershipFacade(
                memberships
            )

            app.dependency_overrides[
                get_role_assignment_repository
            ] = lambda: RoleFacade(
                roles
            )

            value = Context(
                client=mongo,
                database_name=database_name,
                principals=principals,
                memberships=memberships,
                roles=roles,
                plans=plans,
                app=app,
            )

            yield value

        finally:
            registry_module.plans_collection = (
                original_collection
            )

            mongo.drop_database(
                database_name
            )

            assert (
                database_name
                not in mongo.list_database_names()
            )
    finally:
        mongo.close()


@pytest.fixture(
    autouse=True
)
def clean_collections(
    context: Context,
) -> Iterator[None]:
    """Make every HTTP certificate independent inside the UUID database."""
    for collection in (
        context.principals,
        context.memberships,
        context.roles,
        context.plans,
    ):
        collection.delete_many(
            {}
        )

    yield

    for collection in (
        context.principals,
        context.memberships,
        context.roles,
        context.plans,
    ):
        collection.delete_many(
            {}
        )


def _seed(
    context: Context,
    *,
    principal_id: str = _PRINCIPAL,
    tenant_id: str = _TENANT_A,
    role_id: str | None = "ENTERPRISE_ADMIN",
    principal_status:
        PrincipalStatus = PrincipalStatus.ACTIVE,
    membership_status:
        TenantMembershipStatus =
            TenantMembershipStatus.ACTIVE,
    role_status:
        RoleAssignmentStatus =
            RoleAssignmentStatus.ACTIVE,
) -> None:
    """Persist exact current principal, membership and role truth."""
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            principal_id,
            principal_status,
            0,
        ),
        context.principals,
    )

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            membership_status,
            0,
        ),
        context.memberships,
    )

    if role_id is not None:
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal_id,
                tenant_id,
                role_id,
                role_status,
                0,
            ),
            context.roles,
        )


def _token(
    principal_id: str = _PRINCIPAL,
    *,
    projected: bool = False,
) -> str:
    """Create JWT projections that remain non-authoritative."""
    return create_access_token(
        {
            "identity_id":
                principal_id,
            "tenant_id":
                "jwt-projected-tenant",
            "roles":
                ["ENTERPRISE_ADMIN"]
                if projected
                else [],
            "permissions":
                [
                    PLAN_READ_PERMISSION,
                    PLAN_MANAGE_PERMISSION,
                ]
                if projected
                else [],
        },
        expires_in_seconds=3600,
    )


def _headers(
    tenant_id: str = _TENANT_A,
    *,
    principal_id: str = _PRINCIPAL,
    projected: bool = False,
) -> dict[str, str]:
    """Return transport-selected tenant context plus bearer credential."""
    return {
        "Authorization":
            (
                "Bearer "
                + _token(
                    principal_id,
                    projected=projected,
                )
            ),
        "X-Tenant-ID":
            tenant_id,
    }


def _payload(
    *,
    idempotency_key: str,
    tenant_id: str | None = None,
    plan_id: str | None = None,
    price: Any = 499.0,
) -> dict[str, Any]:
    """Return the certified minimal canonical Plan creation vocabulary."""
    payload: dict[str, Any] = {
        "name":
            "Professional",
        "price":
            price,
        "currency":
            "ZAR",
        "billingFrequency":
            "monthly",
        "planType":
            "PROFESSIONAL",
        "idempotencyKey":
            idempotency_key,
        "active":
            True,
        "features": [
            "crm.core",
            "legal.documents",
        ],
        "metadata": {
            "certificate":
                True
        },
        "tags": [
            "plan-router-authority-cert"
        ],
        "user":
            "PLAN-ROUTER-AUTH-CERT",
    }

    if tenant_id is not None:
        payload[
            "tenantId"
        ] = tenant_id

    if plan_id is not None:
        payload[
            "plan_id"
        ] = plan_id

    return payload


def _client(
    context: Context,
) -> TestClient:
    """Construct bounded HTTP transport with server exceptions contained."""
    return TestClient(
        context.app,
        raise_server_exceptions=False,
    )


def _response_data(
    response: Any,
) -> dict[str, Any]:
    """Extract the institutional response data envelope."""
    body = response.json()

    assert isinstance(
        body,
        dict,
    )

    data = body.get(
        "data"
    )

    assert isinstance(
        data,
        dict,
    )

    return data


def _create_direct(
    *,
    tenant_id: str | None,
    idempotency_key: str,
    plan_id: str,
) -> Any:
    """Persist one Plan directly for HTTP read/isolation preparation."""
    result = PlanRegistry.create(
        _payload(
            idempotency_key=
                idempotency_key,
            plan_id=
                plan_id,
        ),
        tenant_id=tenant_id,
    )

    assert (
        result.get(
            "success"
        )
        is True
    )

    return result[
        "plan"
    ]


def test_version_permission_and_static_router_authority_contract() -> None:
    """The committed C1 policy and C2 HTTP source remain exact and explicit."""
    assert (
        PLAN_ROUTER_VERSION
        == "v1.2.0-EXACT-TENANT-REGISTRY-SCOPE"
    )

    read = permission_metadata(
        PLAN_READ_PERMISSION
    )

    manage = permission_metadata(
        PLAN_MANAGE_PERMISSION
    )

    for metadata in (
        read,
        manage,
    ):
        assert (
            metadata.disposition
            is PermissionDisposition.CANONICAL
        )

        assert (
            metadata.namespace
            == "TENANT"
        )

        assert (
            metadata.scope_kind
            == "TENANT"
        )

        assert (
            metadata.tenant_membership_required
            is True
        )

        assert (
            metadata.cross_tenant_capable
            is False
        )

        assert (
            metadata.financial_execution_capable
            is False
        )

        assert (
            metadata.authorizes_by_itself
            is False
        )

    assert (
        get_roles_granting_permission(
            PLAN_READ_PERMISSION
        )
        == (
            "AUDITOR",
            "ENTERPRISE_ADMIN",
        )
    )

    assert (
        get_roles_granting_permission(
            PLAN_MANAGE_PERMISSION
        )
        == (
            "ENTERPRISE_ADMIN",
        )
    )

    source = Path(
        "tools/eos/api/plan_router.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "Header(" not in source
    assert "_extract_request_tenant_id" not in source
    assert "x_tenant_id" not in source
    assert "PLAN_READ_AUTHORITY" in source
    assert "PLAN_MANAGE_AUTHORITY" in source
    assert "PLAN_TENANT_SCOPE_MISMATCH" in source
    assert "PLAN_PERSISTENCE_UNAVAILABLE" in source
    assert '"message": str(' not in source
    assert "fully production" not in source.lower()
    assert (
        "HTTP_422_UNPROCESSABLE_ENTITY"
        not in source
    )
    assert (
        "HTTP_422_UNPROCESSABLE_CONTENT"
        in source
    )


def test_enterprise_admin_real_mongo_full_plan_http_lifecycle(
    context: Context,
) -> None:
    """Admin receives exact read/manage authority and tenant-bound persistence."""
    _seed(
        context
    )

    with _client(
        context
    ) as client:
        created = client.post(
            "/api/plans",
            json=_payload(
                idempotency_key=
                    "HTTP-ADMIN-CREATE",
            ),
            headers=_headers(),
        )

        assert (
            created.status_code
            == 201
        )

        persisted = (
            context.plans.find_one(
                {
                    "idempotency_key":
                        "HTTP-ADMIN-CREATE"
                }
            )
        )

        assert persisted is not None

        assert (
            persisted[
                "tenant_id"
            ]
            == _TENANT_A
        )

        plan_id = str(
            persisted[
                "plan_id"
            ]
        )

        listed = client.get(
            "/api/plans",
            headers=_headers(),
        )

        assert (
            listed.status_code
            == 200
        )

        data = _response_data(
            listed
        )

        assert (
            data[
                "total"
            ]
            == 1
        )

        assert (
            len(
                data[
                    "plans"
                ]
            )
            == 1
        )

        fetched = client.get(
            f"/api/plans/{plan_id}",
            headers=_headers(),
        )

        assert (
            fetched.status_code
            == 200
        )

        updated = client.put(
            f"/api/plans/{plan_id}",
            json={
                "price":
                    599.0,
                "tenantId":
                    _TENANT_A,
                "tenant_id":
                    _TENANT_A,
            },
            headers=_headers(),
        )

        assert (
            updated.status_code
            == 200
        )

        current = PlanRegistry.get(
            plan_id,
            tenant_id=_TENANT_A,
        )

        assert current is not None

        assert (
            current.price
            == 599.0
        )

        assert (
            current.tenant_id
            == _TENANT_A
        )

        archived = client.delete(
            f"/api/plans/{plan_id}",
            headers=_headers(),
        )

        assert (
            archived.status_code
            == 204
        )

        stored = PlanRegistry.get(
            plan_id,
            tenant_id=_TENANT_A,
        )

        assert stored is not None
        assert stored.active is False


def test_auditor_can_read_but_cannot_manage(
    context: Context,
) -> None:
    """AUDITOR has plan:read only and cannot create/update/archive."""
    plan = _create_direct(
        tenant_id=_TENANT_A,
        idempotency_key="AUDITOR-READ",
        plan_id="WILSYPLAN-A0A0A0A0",
    )

    _seed(
        context,
        role_id="AUDITOR",
    )

    with _client(
        context
    ) as client:
        assert (
            client.get(
                "/api/plans",
                headers=_headers(),
            ).status_code
            == 200
        )

        assert (
            client.get(
                f"/api/plans/{plan.plan_id}",
                headers=_headers(),
            ).status_code
            == 200
        )

        assert (
            client.post(
                "/api/plans",
                json=_payload(
                    idempotency_key=
                        "AUDITOR-DENIED-CREATE",
                ),
                headers=_headers(),
            ).status_code
            == 403
        )

        assert (
            client.put(
                f"/api/plans/{plan.plan_id}",
                json={
                    "price":
                        700.0
                },
                headers=_headers(),
            ).status_code
            == 403
        )

        assert (
            client.delete(
                f"/api/plans/{plan.plan_id}",
                headers=_headers(),
            ).status_code
            == 403
        )


@pytest.mark.parametrize(
    "role_id",
    [
        "SERVICE_WORKER",
        "SOVEREIGN_ARCHITECT",
    ],
)
def test_non_bypass_roles_receive_neither_plan_permission(
    context: Context,
    role_id: str,
) -> None:
    """Non-bypass roles cannot read or manage the private catalogue."""
    _seed(
        context,
        role_id=role_id,
    )

    with _client(
        context
    ) as client:
        assert (
            client.get(
                "/api/plans",
                headers=_headers(),
            ).status_code
            == 403
        )

        assert (
            client.post(
                "/api/plans",
                json=_payload(
                    idempotency_key=
                        "NON-BYPASS-DENY",
                ),
                headers=_headers(),
            ).status_code
            == 403
        )


def test_projected_jwt_permissions_without_current_assignment_deny(
    context: Context,
) -> None:
    """JWT roles/permissions cannot manufacture current Plan authority."""
    _seed(
        context,
        role_id=None,
    )

    with _client(
        context
    ) as client:
        headers = _headers(
            projected=True
        )

        assert (
            client.get(
                "/api/plans",
                headers=headers,
            ).status_code
            == 403
        )

        assert (
            client.post(
                "/api/plans",
                json=_payload(
                    idempotency_key=
                        "PROJECTED-DENY",
                ),
                headers=headers,
            ).status_code
            == 403
        )


def test_raw_header_and_global_root_cannot_open_private_catalogue(
    context: Context,
) -> None:
    """Raw tenant transport context is never sufficient authentication."""
    with _client(
        context
    ) as client:
        for headers in (
            {
                "X-Tenant-ID":
                    _TENANT_A
            },
            {
                "X-Tenant-ID":
                    "GLOBAL_ROOT"
            },
        ):
            response = client.get(
                "/api/plans",
                headers=headers,
            )

            assert (
                response.status_code
                == 401
            )


@pytest.mark.parametrize(
    "membership_status",
    [
        item
        for item in TenantMembershipStatus
        if item
        is not TenantMembershipStatus.ACTIVE
    ],
)
def test_non_active_membership_denies_before_plan_access(
    context: Context,
    membership_status: TenantMembershipStatus,
) -> None:
    """Every non-ACTIVE membership fails the HTTP tenant-admission gate."""
    _seed(
        context,
        membership_status=
            membership_status,
    )

    with _client(
        context
    ) as client:
        assert (
            client.get(
                "/api/plans",
                headers=_headers(),
            ).status_code
            == 401
        )


@pytest.mark.parametrize(
    "principal_status",
    [
        item
        for item in PrincipalStatus
        if item
        is not PrincipalStatus.ACTIVE
    ],
)
def test_non_active_principal_denies_before_plan_access(
    context: Context,
    principal_status: PrincipalStatus,
) -> None:
    """Every non-ACTIVE principal fails authentication authority."""
    _seed(
        context,
        principal_status=
            principal_status,
    )

    with _client(
        context
    ) as client:
        assert (
            client.get(
                "/api/plans",
                headers=_headers(),
            ).status_code
            == 401
        )


@pytest.mark.parametrize(
    "role_status",
    [
        item
        for item in RoleAssignmentStatus
        if item
        is not RoleAssignmentStatus.ACTIVE
    ],
)
def test_non_active_role_assignment_denies_plan_permission(
    context: Context,
    role_status: RoleAssignmentStatus,
) -> None:
    """Every non-ACTIVE assignment fails exact permission possession."""
    _seed(
        context,
        role_status=
            role_status,
    )

    with _client(
        context
    ) as client:
        assert (
            client.get(
                "/api/plans",
                headers=_headers(),
            ).status_code
            == 403
        )


def test_wrong_tenant_membership_denies(
    context: Context,
) -> None:
    """A valid principal cannot select a tenant without current membership."""
    _seed(
        context,
        tenant_id=_TENANT_A,
    )

    with _client(
        context
    ) as client:
        response = client.get(
            "/api/plans",
            headers=_headers(
                _TENANT_B
            ),
        )

        assert (
            response.status_code
            == 401
        )


def test_neighbor_tenant_plan_is_not_visible(
    context: Context,
) -> None:
    """Authorized tenant A receives neither tenant B list nor single Plan truth."""
    neighbor = _create_direct(
        tenant_id=_TENANT_B,
        idempotency_key="NEIGHBOR-PLAN",
        plan_id="WILSYPLAN-B0B0B0B0",
    )

    _seed(
        context,
        tenant_id=_TENANT_A,
    )

    with _client(
        context
    ) as client:
        listed = client.get(
            "/api/plans",
            headers=_headers(
                _TENANT_A
            ),
        )

        assert (
            listed.status_code
            == 200
        )

        data = _response_data(
            listed
        )

        assert (
            data[
                "total"
            ]
            == 0
        )

        assert (
            data[
                "plans"
            ]
            == []
        )

        fetched = client.get(
            f"/api/plans/{neighbor.plan_id}",
            headers=_headers(
                _TENANT_A
            ),
        )

        assert (
            fetched.status_code
            == 404
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "tenantId",
        "tenant_id",
    ],
)
def test_create_body_tenant_redirect_denies_before_registry(
    context: Context,
    monkeypatch: pytest.MonkeyPatch,
    field_name: str,
) -> None:
    """Create body tenant redirection is rejected before Registry invocation."""
    _seed(
        context
    )

    calls = 0

    def forbidden(
        *_args: object,
        **_kwargs: object,
    ) -> Any:
        nonlocal calls
        calls += 1
        raise AssertionError(
            "PlanRegistry.create must not execute"
        )

    monkeypatch.setattr(
        PlanRegistry,
        "create",
        forbidden,
    )

    payload = _payload(
        idempotency_key=
            "CREATE-REDIRECT-DENY",
    )

    payload[
        field_name
    ] = _TENANT_B

    with _client(
        context
    ) as client:
        response = client.post(
            "/api/plans",
            json=payload,
            headers=_headers(),
        )

    assert (
        response.status_code
        == 403
    )

    assert calls == 0


@pytest.mark.parametrize(
    "field_name",
    [
        "tenantId",
        "tenant_id",
    ],
)
def test_update_body_tenant_redirect_denies_before_registry(
    context: Context,
    monkeypatch: pytest.MonkeyPatch,
    field_name: str,
) -> None:
    """Update tenant redirection is rejected before Registry invocation."""
    _seed(
        context
    )

    calls = 0

    def forbidden(
        *_args: object,
        **_kwargs: object,
    ) -> Any:
        nonlocal calls
        calls += 1
        raise AssertionError(
            "PlanRegistry.update must not execute"
        )

    monkeypatch.setattr(
        PlanRegistry,
        "update",
        forbidden,
    )

    with _client(
        context
    ) as client:
        response = client.put(
            "/api/plans/WILSYPLAN-C0C0C0C0",
            json={
                "price":
                    600.0,
                field_name:
                    _TENANT_B,
            },
            headers=_headers(),
        )

    assert (
        response.status_code
        == 403
    )

    assert calls == 0


def test_matching_update_tenant_aliases_are_scope_only_not_mutation(
    context: Context,
) -> None:
    """Matching tenant aliases are validated then stripped from update data."""
    plan = _create_direct(
        tenant_id=_TENANT_A,
        idempotency_key="UPDATE-SCOPE-ONLY",
        plan_id="WILSYPLAN-D0D0D0D0",
    )

    _seed(
        context
    )

    with _client(
        context
    ) as client:
        response = client.put(
            f"/api/plans/{plan.plan_id}",
            json={
                "price":
                    777.0,
                "tenantId":
                    _TENANT_A,
                "tenant_id":
                    _TENANT_A,
            },
            headers=_headers(),
        )

        assert (
            response.status_code
            == 200
        )

    current = PlanRegistry.get(
        plan.plan_id,
        tenant_id=_TENANT_A,
    )

    assert current is not None
    assert current.tenant_id == _TENANT_A
    assert current.price == 777.0


def test_create_validation_and_duplicate_conflict_are_bounded(
    context: Context,
) -> None:
    """Observed caller-contract errors are bounded without exposing diagnostics."""
    _seed(
        context
    )

    with _client(
        context
    ) as client:
        missing = client.post(
            "/api/plans",
            json={
                "name":
                    "Missing"
            },
            headers=_headers(),
        )

        assert (
            missing.status_code
            == 422
        )

        invalid_type_payload = _payload(
            idempotency_key=
                "INVALID-TYPE"
        )

        invalid_type_payload[
            "planType"
        ] = "NOT_A_PLAN"

        invalid_type = client.post(
            "/api/plans",
            json=invalid_type_payload,
            headers=_headers(),
        )

        assert (
            invalid_type.status_code
            == 422
        )

        invalid_frequency_payload = _payload(
            idempotency_key=
                "INVALID-FREQUENCY"
        )

        invalid_frequency_payload[
            "billingFrequency"
        ] = "fortnightly"

        invalid_frequency = client.post(
            "/api/plans",
            json=
                invalid_frequency_payload,
            headers=_headers(),
        )

        assert (
            invalid_frequency.status_code
            == 422
        )

        first_payload = _payload(
            idempotency_key=
                "HTTP-DUPLICATE"
        )

        first = client.post(
            "/api/plans",
            json=first_payload,
            headers=_headers(),
        )

        assert (
            first.status_code
            == 201
        )

        second = client.post(
            "/api/plans",
            json=first_payload,
            headers=_headers(),
        )

        assert (
            second.status_code
            == 409
        )

        assert (
            "HTTP-DUPLICATE"
            not in second.text
        )


def test_genuine_empty_and_absence_are_not_persistence_failure(
    context: Context,
) -> None:
    """Validated empty list is 200; genuine single-resource absence is 404."""
    _seed(
        context
    )

    with _client(
        context
    ) as client:
        listed = client.get(
            "/api/plans",
            headers=_headers(),
        )

        assert (
            listed.status_code
            == 200
        )

        data = _response_data(
            listed
        )

        assert data["plans"] == []
        assert data["total"] == 0

        missing_plan_id = (
            "WILSYPLAN-E0E0E0E0"
        )

        missing_get = client.get(
            f"/api/plans/{missing_plan_id}",
            headers=_headers(),
        )

        assert (
            missing_get.status_code
            == 404
        )

        missing_update = client.put(
            f"/api/plans/{missing_plan_id}",
            json={
                "price":
                    900.0
            },
            headers=_headers(),
        )

        assert (
            missing_update.status_code
            == 404
        )

        missing_archive = client.delete(
            f"/api/plans/{missing_plan_id}",
            headers=_headers(),
        )

        assert (
            missing_archive.status_code
            == 404
        )

        for response in (
            missing_get,
            missing_update,
            missing_archive,
        ):
            assert (
                missing_plan_id
                not in response.text
            )




@pytest.mark.parametrize(
    "operation",
    [
        "list",
        "get",
        "create",
        "update",
    ],
)
def test_plan_evidence_serialization_failure_is_bounded_503(
    context: Context,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    """Plan evidence serialization failure is bounded persistence-unavailable."""
    _seed(
        context
    )

    secret = (
        "SERIALIZATION-SECRET-MUST-NOT-LEAK"
    )

    class ExplodingPlan:
        def to_dict(
            self,
        ) -> dict[str, Any]:
            raise RuntimeError(
                secret
            )

    def forced(
        _cls: type[PlanRegistry],
        *_args: object,
        **_kwargs: object,
    ) -> Any:
        plan = ExplodingPlan()

        if operation == "list":
            return {
                "items": [
                    plan
                ],
                "total":
                    1,
                "pages":
                    1,
            }

        if operation == "get":
            return plan

        return {
            "success":
                True,
            "plan":
                plan,
        }

    monkeypatch.setattr(
        PlanRegistry,
        operation,
        classmethod(
            forced
        ),
    )

    with _client(
        context
    ) as client:
        if operation == "list":
            response = client.get(
                "/api/plans",
                headers=_headers(),
            )

        elif operation == "get":
            response = client.get(
                "/api/plans/WILSYPLAN-SERIALIZE",
                headers=_headers(),
            )

        elif operation == "create":
            response = client.post(
                "/api/plans",
                json=_payload(
                    idempotency_key=
                        "SERIALIZATION-CREATE",
                ),
                headers=_headers(),
            )

        else:
            response = client.put(
                "/api/plans/WILSYPLAN-SERIALIZE",
                json={
                    "price":
                        611.0
                },
                headers=_headers(),
            )

    assert (
        response.status_code
        == 503
    )

    assert (
        "PLAN_PERSISTENCE_UNAVAILABLE"
        in response.text
    )

    assert (
        secret
        not in response.text
    )




@pytest.mark.parametrize(
    "operation",
    [
        "list",
        "get",
        "create",
        "update",
    ],
)
def test_plan_response_formatting_failure_is_bounded_503(
    context: Context,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    """Structurally unserializable response evidence is bounded as 503."""
    _seed(
        context
    )

    class UnserializablePlan:
        def to_dict(
            self,
        ) -> dict[str, Any]:
            return {
                "opaque":
                    object()
            }

    def forced(
        _cls: type[PlanRegistry],
        *_args: object,
        **_kwargs: object,
    ) -> Any:
        plan = (
            UnserializablePlan()
        )

        if operation == "list":
            return {
                "items": [
                    plan
                ],
                "total":
                    1,
                "pages":
                    1,
            }

        if operation == "get":
            return plan

        return {
            "success":
                True,
            "plan":
                plan,
        }

    monkeypatch.setattr(
        PlanRegistry,
        operation,
        classmethod(
            forced
        ),
    )

    with _client(
        context
    ) as client:
        if operation == "list":
            response = client.get(
                "/api/plans",
                headers=_headers(),
            )

        elif operation == "get":
            response = client.get(
                "/api/plans/WILSYPLAN-FORMAT",
                headers=_headers(),
            )

        elif operation == "create":
            response = client.post(
                "/api/plans",
                json=_payload(
                    idempotency_key=
                        "FORMAT-CREATE",
                ),
                headers=_headers(),
            )

        else:
            response = client.put(
                "/api/plans/WILSYPLAN-FORMAT",
                json={
                    "price":
                        612.0
                },
                headers=_headers(),
            )

    assert (
        response.status_code
        == 503
    )

    assert (
        "PLAN_PERSISTENCE_UNAVAILABLE"
        in response.text
    )

    assert (
        "not JSON serializable"
        not in response.text
    )


def test_registry_outage_is_503_for_all_plan_http_operations(
    context: Context,
) -> None:
    """Persistence outage cannot masquerade as absence or caller error."""
    _seed(
        context
    )

    dead_client: MongoClient[
        Any
    ] = MongoClient(
        "mongodb://127.0.0.1:1/"
        "?directConnection=true",
        serverSelectionTimeoutMS=100,
        connectTimeoutMS=100,
        socketTimeoutMS=100,
    )

    dead_collection: Collection[
        dict[str, Any]
    ] = (
        dead_client[
            "wilsy_plan_router_dead"
        ].get_collection(
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

    original = (
        registry_module.plans_collection
    )

    registry_module.plans_collection = (
        dead_collection
    )

    try:
        with _client(
            context
        ) as client:
            responses = (
                client.get(
                    "/api/plans",
                    headers=_headers(),
                ),
                client.get(
                    "/api/plans/WILSYPLAN-F0F0F0F0",
                    headers=_headers(),
                ),
                client.post(
                    "/api/plans",
                    json=_payload(
                        idempotency_key=
                            "OUTAGE-CREATE",
                    ),
                    headers=_headers(),
                ),
                client.put(
                    "/api/plans/WILSYPLAN-F0F0F0F0",
                    json={
                        "price":
                            999.0
                    },
                    headers=_headers(),
                ),
                client.delete(
                    "/api/plans/WILSYPLAN-F0F0F0F0",
                    headers=_headers(),
                ),
            )

        for response in responses:
            assert (
                response.status_code
                == 503
            )

            assert (
                "PLAN_PERSISTENCE_UNAVAILABLE"
                in response.text
            )

            assert (
                "127.0.0.1:1"
                not in response.text
            )

            assert (
                "ServerSelection"
                not in response.text
            )

    finally:
        registry_module.plans_collection = (
            original
        )

        dead_client.close()



def test_authenticated_tenant_cannot_read_or_mutate_global_plan(
    context: Context,
) -> None:
    """Private Plan HTTP authority excludes tenantless/global catalogue truth."""
    global_plan = _create_direct(
        tenant_id=None,
        idempotency_key=
            "HTTP-GLOBAL-EXACT-DENY",
        plan_id=
            "WILSYPLAN-Z0Z0Z0Z0",
    )

    _seed(
        context,
        tenant_id=_TENANT_A,
    )

    with _client(
        context
    ) as client:
        listed = client.get(
            "/api/plans",
            headers=_headers(
                _TENANT_A
            ),
        )

        assert listed.status_code == 200

        listed_data = _response_data(
            listed
        )

        assert listed_data["total"] == 0
        assert listed_data["plans"] == []

        fetched = client.get(
            f"/api/plans/{global_plan.plan_id}",
            headers=_headers(
                _TENANT_A
            ),
        )

        assert fetched.status_code == 404

        updated = client.put(
            f"/api/plans/{global_plan.plan_id}",
            json={
                "price":
                    2222.0
            },
            headers=_headers(
                _TENANT_A
            ),
        )

        assert updated.status_code == 404

        archived = client.delete(
            f"/api/plans/{global_plan.plan_id}",
            headers=_headers(
                _TENANT_A
            ),
        )

        assert archived.status_code == 404

    surviving = PlanRegistry.get(
        global_plan.plan_id
    )

    assert surviving is not None
    assert surviving.active is True



"""
INSTITUTIONAL CERTIFICATION SEAL

Artifact:
    tests/integration/test_plan_router_authority_real_mongo.py

Version:
    v1.1.2-PLAN-ROUTER-VERSION-ALIGNMENT-CERT

Production owner:
    tools/eos/api/plan_router.py

Authority sequence:
    credential -> ACTIVE principal -> exact ACTIVE membership ->
    ACTIVE role assignment -> exact plan permission -> private Plan access.

Tenant authority:
    Body tenant fields and JWT projections are non-sovereign.
    Exact membership-admitted identity tenant is authoritative HTTP scope.

Persistence:
    Actual governed Mongo replica set with majority read/write truth.

Financial execution:
    NONE. Kennel EOS remains exclusive.

Status:
    DIRECT REAL-MONGO / HTTP AUTHORITY CERTIFICATE.

Certification date:
    2026-09-03

WILSY OS — ALL OR NOTHING.
"""
