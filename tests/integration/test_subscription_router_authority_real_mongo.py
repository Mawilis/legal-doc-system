"""TITLE: WILSY OS Subscription Router Authority Real-Mongo Certification.
VERSION: v1.2.0-SUBSCRIPTION-CALENDAR-BILLING-HTTP-CERT
AUTHORITY: Actual-Mongo HTTP certification of subscription identity, tenant
membership, permission and persistence composition.
EPITOME: Executes the real FastAPI subscription router with current JWT
authentication, actual Mongo principal/membership/role assignment truth and
actual Mongo subscription persistence. Proves raw tenant context, JWT
projections and cross-tenant requests cannot bypass durable authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_subscription_router_authority_real_mongo.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-03.
CHANGELOG:
    v1.2.0-SUBSCRIPTION-CALENDAR-BILLING-HTTP-CERT certifies real HTTP
    calendar-period authority composition. Authorized callers provide startDate
    and Plan selection only; SubscriptionRegistry derives the current calendar
    period from canonical Plan frequency. Caller period redirection, generic
    period replacement and naive startDate fail closed without replacing
    persisted subscription period truth. Production HTTP router authority
    composition remains unchanged.
    v1.1.0-SUBSCRIPTION-CATALOGUE-PROVENANCE-HTTP-CERT binds the real HTTP authority certificate to actual
    PlanRegistry catalogue persistence in the same isolated Mongo database;
    certifies planId/newPlanId-only selection, commercial redirection denial,
    tenant/global catalogue scope, inactive/neighbor denial, canonical snapshot
    persistence and bounded catalogue-outage HTTP failure.
    v1.0.0-SUBSCRIPTION-ROUTER-AUTHORITY-REAL-MONGO-CERT establishes real HTTP,
    real authority Mongo and real SubscriptionRegistry Mongo certification for
    subscription:read/subscription:manage wiring.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic principals/tenants only; UUID-isolated
local certification database; deterministic cleanup; no production secrets,
production tenants or production databases.
TENANT BOUNDARY: X-Tenant-ID is request context only. Current ACTIVE membership
and current role assignment must admit the exact tenant before subscription
persistence access.
AUTHORITY BOUNDARY: Certifies real HTTP composition and actual persistence only.
It creates no new authentication, membership, role, permission or subscription
authority owner.
FINANCIAL AUTHORITY BOUNDARY: Subscription commercial state never proves
payment authorization, release, execution or settlement. Kennel EOS remains
exclusive.
CERTIFICATION CLASSIFICATION: REAL HTTP / REAL AUTHORITY MONGO / REAL
SUBSCRIPTION MONGO / FAIL-CLOSED.
"""

from __future__ import annotations

import hashlib
import inspect
import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

os.environ.setdefault(
    "WILSY_JWT_SECRET",
    "SUBSCRIPTION-ROUTER-REAL-MONGO-CERT-ONLY-SECRET",
)

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.subscription_router as router_module
import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as registry_module
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.subscription_router import subscription_router
from tools.eos.auth.authentication import (
    get_principal_authority_repository,
)
from tools.eos.auth.authorization import (
    get_role_assignment_repository,
)
from tools.eos.auth.jwt_provider import create_access_token
from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
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
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry,
)


VERSION = (
    "v1.2.0-SUBSCRIPTION-CALENDAR-BILLING-HTTP-CERT"
)

URI = os.getenv("TEST_VENDOR_MONGO_URI")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "sub_router_auth_cert_"


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


@dataclass(slots=True)
class Context:
    """Actual-Mongo resources for one isolated HTTP certification."""

    client: MongoClient[Any]
    database_name: str
    principals: Collection[dict[str, Any]]
    memberships: Collection[dict[str, Any]]
    roles: Collection[dict[str, Any]]
    subscriptions: Collection[dict[str, Any]]
    plans: Collection[dict[str, Any]]
    app: FastAPI


def _plan_identity(
    *,
    plan: str,
    amount: float,
    tenant_id: str | None,
    active: bool,
) -> tuple[str, str]:
    material = (
        f"{tenant_id or 'GLOBAL'}"
        f"|{plan.upper()}"
        f"|{float(amount):.6f}"
        f"|{active}"
    )

    digest = hashlib.sha3_256(
        material.encode("utf-8")
    ).hexdigest().upper()

    return (
        "WILSYPLAN-HTTPCERT" + digest[:12],
        "PLAN-HTTP-CERT-" + digest[:20],
    )


def _seed_plan(
    *,
    plan: str = "ENTERPRISE",
    amount: float = 499.0,
    tenant_id: str | None = None,
    active: bool = True,
    features: tuple[str, ...] = (
        "crm.core",
        "legal.documents",
    ),
):
    """Persist one real PlanRegistry row for HTTP provenance certification."""
    plan_id, idempotency_key = _plan_identity(
        plan=plan,
        amount=amount,
        tenant_id=tenant_id,
        active=active,
    )

    existing = PlanRegistry.get(
        plan_id,
        tenant_id=tenant_id,
    )

    if existing is not None:
        return existing

    payload: dict[str, Any] = {
        "name": f"HTTP Certificate {plan.title()}",
        "price": amount,
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "planType": plan,
        "idempotencyKey": idempotency_key,
        "plan_id": plan_id,
        "active": active,
        "features": list(features),
        "metadata": {
            "certificate": True,
            "catalogueAuthority": "PlanRegistry",
        },
        "tags": [
            "subscription-http-catalogue-cert"
        ],
        "user": "SUBSCRIPTION-HTTP-CERT",
    }

    if tenant_id is not None:
        payload["tenantId"] = tenant_id

    result = PlanRegistry.create(
        payload
    )

    assert result["success"] is True

    return result["plan"]


def _command(
    tenant_id: str,
    key: str,
    *,
    plan_id: str,
) -> dict[str, Any]:
    return {
        "tenantId": tenant_id,
        "planId": plan_id,
        "startDate":
            "2026-09-03T00:00:00+00:00",
        "idempotencyKey": key,
        "billingMode": "PLATFORM",
        "onboardingRef":
            f"ONBOARD-{tenant_id}",
        "sector": "LEGAL",
        "region": "ZA",
        "metadata": {
            "certificate": True
        },
    }


def _payload(
    tenant_id: str,
    key: str,
    *,
    amount: float = 499.0,
    plan: str = "ENTERPRISE",
) -> dict[str, Any]:
    """Build HTTP command containing plan selection only."""
    catalogue_plan = _seed_plan(
        plan=plan,
        amount=amount,
        tenant_id=None,
        active=True,
    )

    return _command(
        tenant_id,
        key,
        plan_id=catalogue_plan.plan_id,
    )

@pytest.fixture()
def context() -> Iterator[Context]:
    """Create actual authority and subscription persistence in isolated Mongo."""
    if not URI:
        pytest.fail(
            "TEST_VENDOR_MONGO_URI is required"
        )

    mongo: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
    )

    hello = mongo.admin.command("hello")

    if (
        hello.get("setName")
        != EXPECTED_REPLICA_SET
    ):
        mongo.close()
        pytest.fail(
            "wrong certification replica set"
        )

    database_name = (
        DATABASE_PREFIX
        + uuid.uuid4().hex
    )

    if len(
        database_name.encode("utf-8")
    ) > 63:
        mongo.close()
        pytest.fail(
            "certification database namespace too long"
        )

    database = mongo[database_name]

    principals = database[
        "principal_authorities"
    ]
    memberships = database[
        "tenant_memberships"
    ]
    roles = database[
        "role_assignments"
    ]

    subscriptions: Collection[
        dict[str, Any]
    ] = database.get_collection(
        "subscriptions",
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
        read_concern=ReadConcern(
            "majority"
        ),
    )

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

    PrincipalAuthorityRepository.ensure_indexes(
        principals
    )
    TenantMembershipRepository.ensure_indexes(
        memberships
    )
    RoleAssignmentRepository.ensure_indexes(
        roles
    )

    original_collection = (
        registry_module.subscriptions_collection
    )

    original_plan_collection = (
        plan_registry_module.plans_collection
    )

    registry_module.subscriptions_collection = (
        subscriptions
    )

    plan_registry_module.plans_collection = (
        plans
    )

    PlanRegistry._ensure_indexes()

    app = FastAPI()
    register_error_handlers(
        app,
        debug=False,
    )
    app.include_router(
        subscription_router
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
        subscriptions=subscriptions,
        plans=plans,
        app=app,
    )

    try:
        yield value
    finally:
        registry_module.subscriptions_collection = (
            original_collection
        )
        plan_registry_module.plans_collection = (
            original_plan_collection
        )
        mongo.drop_database(
            database_name
        )
        assert (
            database_name
            not in mongo.list_database_names()
        )
        mongo.close()


def _seed(
    context: Context,
    *,
    principal_id: str,
    tenant_id: str,
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
    """Persist exact current principal/membership/role authority."""
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
    principal_id: str,
    *,
    projected: bool = False,
) -> str:
    """Create synthetic JWT projections that remain non-authoritative."""
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
                    "subscription:read",
                    "subscription:manage",
                ]
                if projected
                else [],
        },
        expires_in_seconds=3600,
    )


def _headers(
    principal_id: str,
    tenant_id: str,
    *,
    projected: bool = False,
) -> dict[str, str]:
    """Return transport context only."""
    return {
        "Authorization":
            f"Bearer {_token(principal_id, projected=projected)}",
        "X-Tenant-ID":
            tenant_id,
    }


def _client(
    context: Context,
) -> TestClient:
    """Construct bounded FastAPI test transport."""
    return TestClient(
        context.app,
        raise_server_exceptions=False,
    )


def _persist_subscription(
    context: Context,
    tenant_id: str,
    *,
    key: str,
):
    """Persist one subscription through the real canonical registry."""
    result = SubscriptionRegistry.create(
        _payload(
            tenant_id,
            key,
        ),
        tenant_id_header=tenant_id,
    )

    assert result["success"] is True

    return result["subscription"]


def test_permission_canon_role_grants_and_router_surface_are_fail_closed() -> None:
    """Canonical vocabulary and router signatures contain no raw registry tenant authority."""
    read = permission_metadata(
        "subscription:read"
    )
    manage = permission_metadata(
        "subscription:manage"
    )

    for metadata in (
        read,
        manage,
    ):
        assert (
            metadata.disposition
            is PermissionDisposition.CANONICAL
        )
        assert metadata.namespace == "TENANT"
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
        assert metadata.authorizes_by_itself is False

    assert (
        get_roles_granting_permission(
            "subscription:read"
        )
        == (
            "AUDITOR",
            "ENTERPRISE_ADMIN",
        )
    )

    assert (
        get_roles_granting_permission(
            "subscription:manage"
        )
        == ("ENTERPRISE_ADMIN",)
    )

    public_routes = (
        router_module.list_subscriptions,
        router_module.get_subscription,
        router_module.create_subscription,
        router_module.update_subscription,
        router_module.archive_subscription,
        router_module.pause_subscription,
        router_module.resume_subscription,
        router_module.cancel_subscription,
        router_module.upgrade_subscription,
        router_module.downgrade_subscription,
        router_module.reactivate_subscription,
        router_module.get_subscription_audit,
        router_module.get_subscription_metrics,
    )

    for route in public_routes:
        assert (
            "x_tenant_id"
            not in inspect.signature(
                route
            ).parameters
        )


def test_enterprise_admin_reads_real_subscription(
    context: Context,
) -> None:
    """Current admin role permits real own-tenant subscription read."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant = (
        "tenant-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    subscription = _persist_subscription(
        context,
        tenant,
        key="admin-read",
    )

    response = _client(
        context
    ).get(
        (
            "/api/subscriptions/"
            + subscription.subscription_id
        ),
        headers=_headers(
            principal,
            tenant,
        ),
    )

    assert response.status_code == 200
    assert (
        subscription.subscription_id
        in response.text
    )


def test_auditor_reads_but_cannot_manage(
    context: Context,
) -> None:
    """AUDITOR has read authority but no subscription mutation authority."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant = (
        "tenant-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
        role_id="AUDITOR",
    )

    subscription = _persist_subscription(
        context,
        tenant,
        key="auditor-existing",
    )

    client = _client(context)

    read = client.get(
        (
            "/api/subscriptions/"
            + subscription.subscription_id
        ),
        headers=_headers(
            principal,
            tenant,
        ),
    )

    assert read.status_code == 200

    count_before = (
        context.subscriptions
        .count_documents({})
    )

    create = client.post(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant,
        ),
        json=_payload(
            tenant,
            "auditor-denied",
        ),
    )

    assert create.status_code == 403
    assert (
        context.subscriptions
        .count_documents({})
        == count_before
    )


def test_enterprise_admin_create_persists_real_authorized_tenant(
    context: Context,
) -> None:
    """Manage permission reaches real persistence only after durable authority."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant = (
        "tenant-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    response = _client(
        context
    ).post(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant,
        ),
        json=_payload(
            tenant,
            "http-create",
        ),
    )

    assert response.status_code == 201

    persisted = (
        context.subscriptions
        .find_one(
            {
                "tenant_id": tenant,
                "idempotency_key":
                    "http-create",
            }
        )
    )

    assert persisted is not None
    assert persisted["tenant_id"] == tenant


def test_payload_cannot_redirect_authorized_tenant(
    context: Context,
) -> None:
    """A body tenant cannot override membership-admitted tenant scope."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant_a = (
        "tenant-a-"
        + uuid.uuid4().hex
    )
    tenant_b = (
        "tenant-b-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant_a,
    )

    before = (
        context.subscriptions
        .count_documents({})
    )

    response = _client(
        context
    ).post(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant_a,
        ),
        json=_payload(
            tenant_b,
            "redirect-denied",
        ),
    )

    assert response.status_code == 403
    assert (
        context.subscriptions
        .count_documents({})
        == before
    )


def test_projected_jwt_permissions_without_current_assignment_deny(
    context: Context,
) -> None:
    """JWT role/permission projections never replace persisted role assignment."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant = (
        "tenant-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
        role_id=None,
    )

    response = _client(
        context
    ).post(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant,
            projected=True,
        ),
        json=_payload(
            tenant,
            "projected-denied",
        ),
    )

    assert response.status_code == 403
    assert (
        context.subscriptions
        .count_documents({})
        == 0
    )


def test_raw_tenant_header_without_authenticated_principal_denies(
    context: Context,
) -> None:
    """Possession of X-Tenant-ID alone never reaches subscription truth."""
    tenant = (
        "tenant-"
        + uuid.uuid4().hex
    )

    response = _client(
        context
    ).get(
        "/api/subscriptions",
        headers={
            "X-Tenant-ID": tenant
        },
    )

    assert response.status_code == 401
    assert (
        context.subscriptions
        .count_documents({})
        == 0
    )


def test_wrong_tenant_membership_denies_without_cross_tenant_leak(
    context: Context,
) -> None:
    """Authenticated principal cannot select a tenant without ACTIVE membership."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant_a = (
        "tenant-a-"
        + uuid.uuid4().hex
    )
    tenant_b = (
        "tenant-b-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant_a,
    )

    subscription = _persist_subscription(
        context,
        tenant_a,
        key="tenant-a-secret",
    )

    response = _client(
        context
    ).get(
        (
            "/api/subscriptions/"
            + subscription.subscription_id
        ),
        headers=_headers(
            principal,
            tenant_b,
        ),
    )

    assert response.status_code == 401
    assert (
        subscription.subscription_id
        not in response.text
    )


@pytest.mark.parametrize(
    "membership_status",
    [
        TenantMembershipStatus.REVOKED,
        TenantMembershipStatus.SUSPENDED,
    ],
)
def test_non_active_membership_denies(
    context: Context,
    membership_status: TenantMembershipStatus,
) -> None:
    """Revoked or suspended membership cannot exercise subscription permission."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant = (
        "tenant-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
        membership_status=
            membership_status,
    )

    response = _client(
        context
    ).get(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant,
        ),
    )

    assert response.status_code == 401


def test_revoked_role_assignment_denies(
    context: Context,
) -> None:
    """Static role definition never replaces current ACTIVE assignment."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant = (
        "tenant-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
        role_status=
            RoleAssignmentStatus.REVOKED,
    )

    response = _client(
        context
    ).get(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant,
        ),
    )

    assert response.status_code == 403


def test_metrics_path_cannot_escape_authorized_tenant(
    context: Context,
) -> None:
    """Authorized read permission cannot target another tenant in path."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant_a = (
        "tenant-a-"
        + uuid.uuid4().hex
    )
    tenant_b = (
        "tenant-b-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant_a,
    )

    response = _client(
        context
    ).get(
        (
            "/api/subscriptions/metrics/"
            + tenant_b
        ),
        headers=_headers(
            principal,
            tenant_a,
        ),
    )

    assert response.status_code == 403


def test_authorized_manage_lifecycle_persists_real_pause(
    context: Context,
) -> None:
    """Manage permission reaches real lifecycle mutation after all gates."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant = (
        "tenant-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    subscription = _persist_subscription(
        context,
        tenant,
        key="pause-real",
    )

    response = _client(
        context
    ).post(
        (
            "/api/subscriptions/"
            + subscription.subscription_id
            + "/pause"
        ),
        headers=_headers(
            principal,
            tenant,
        ),
        json={
            "pauseReason":
                "real-authority-cert"
        },
    )

    assert response.status_code == 200

    persisted = (
        context.subscriptions
        .find_one(
            {
                "tenant_id": tenant,
                "subscription_id":
                    subscription.subscription_id,
            }
        )
    )

    assert persisted is not None
    assert persisted["status"] == "paused"


def test_registry_network_failure_after_valid_authority_is_bounded_503(
    context: Context,
) -> None:
    """Valid user authority cannot turn persistence outage into false absence."""
    principal = (
        "principal-"
        + uuid.uuid4().hex
    )
    tenant = (
        "tenant-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    dead = MongoClient(
        "mongodb://127.0.0.1:1/sub_router_dead",
        serverSelectionTimeoutMS=150,
    )

    original = (
        registry_module.subscriptions_collection
    )

    registry_module.subscriptions_collection = (
        dead["sub_router_dead"][
            "subscriptions"
        ]
    )

    try:
        response = _client(
            context
        ).get(
            "/api/subscriptions",
            headers=_headers(
                principal,
                tenant,
            ),
        )
    finally:
        registry_module.subscriptions_collection = (
            original
        )
        dead.close()

    assert response.status_code == 503
    assert (
        "SUBSCRIPTION_PERSISTENCE_UNAVAILABLE"
        in response.text
    )


def test_catalogue_provenance_certificate_versions_are_exact() -> None:
    assert (
        router_module.VERSION
        == "v1.2.0-CATALOGUE-PROVENANCE"
    )
    assert (
        registry_module.VERSION
        == "v1.3.0-CALENDAR-BILLING-WIRING"
    )
    assert (
        VERSION
        == "v1.2.0-SUBSCRIPTION-CALENDAR-BILLING-HTTP-CERT"
    )


def test_http_create_persists_planregistry_derived_snapshot(
    context: Context,
) -> None:
    """Authorized create stores actual canonical PlanRegistry evidence."""
    principal = "principal-" + uuid.uuid4().hex
    tenant = "tenant-" + uuid.uuid4().hex

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    payload = _payload(
        tenant,
        "http-catalogue-snapshot",
        amount=777.0,
    )

    plan = PlanRegistry.get(
        payload["planId"],
        tenant_id=tenant,
    )

    assert plan is not None

    response = _client(context).post(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant,
        ),
        json=payload,
    )

    assert response.status_code == 201

    persisted = context.subscriptions.find_one(
        {
            "tenant_id": tenant,
            "idempotency_key":
                "http-catalogue-snapshot",
        }
    )

    assert persisted is not None
    assert persisted["plan_id"] == plan.plan_id
    assert persisted["plan_name"] == plan.name
    assert persisted["plan_features"] == list(plan.features)
    assert (
        persisted["plan_catalogue_version"]
        == plan.catalogue_version
    )
    assert persisted["amount"] == float(plan.price)
    assert persisted["currency"] == plan.currency
    assert (
        persisted["billing_frequency"]
        == plan.billing_frequency.value
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("plan", "SOVEREIGN"),
        ("amount", 1.0),
        ("currency", "USD"),
        ("billingFrequency", "annual"),
        ("planFeatures", ["caller.feature"]),
        ("planCatalogueVersion", 999),
    ],
)
def test_http_create_rejects_caller_commercial_redirection(
    context: Context,
    field: str,
    value: Any,
) -> None:
    principal = "principal-" + uuid.uuid4().hex
    tenant = "tenant-" + uuid.uuid4().hex

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    payload = _payload(
        tenant,
        "http-redirection-" + field,
    )
    payload[field] = value

    response = _client(context).post(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant,
        ),
        json=payload,
    )

    assert response.status_code == 422
    assert (
        "SUBSCRIPTION_COMMERCIAL_REDIRECTION_FORBIDDEN"
        in response.text
    )
    assert (
        context.subscriptions.count_documents({})
        == 0
    )


def test_http_neighbor_and_inactive_plans_fail_closed(
    context: Context,
) -> None:
    principal = "principal-" + uuid.uuid4().hex
    tenant_a = "tenant-a-" + uuid.uuid4().hex
    tenant_b = "tenant-b-" + uuid.uuid4().hex

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant_b,
    )

    neighbor_plan = _seed_plan(
        plan="PROFESSIONAL",
        amount=333.0,
        tenant_id=tenant_a,
    )

    neighbor = _client(context).post(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant_b,
        ),
        json=_command(
            tenant_b,
            "neighbor-plan-denied",
            plan_id=neighbor_plan.plan_id,
        ),
    )

    assert neighbor.status_code == 404
    assert (
        "SUBSCRIPTION_PLAN_NOT_AVAILABLE"
        in neighbor.text
    )

    inactive_plan = _seed_plan(
        plan="ENTERPRISE",
        amount=444.0,
        active=False,
    )

    inactive = _client(context).post(
        "/api/subscriptions",
        headers=_headers(
            principal,
            tenant_b,
        ),
        json=_command(
            tenant_b,
            "inactive-plan-denied",
            plan_id=inactive_plan.plan_id,
        ),
    )

    assert inactive.status_code == 404
    assert (
        "SUBSCRIPTION_PLAN_NOT_AVAILABLE"
        in inactive.text
    )

    assert (
        context.subscriptions.count_documents({})
        == 0
    )


def test_http_generic_update_cannot_redirect_price(
    context: Context,
) -> None:
    principal = "principal-" + uuid.uuid4().hex
    tenant = "tenant-" + uuid.uuid4().hex

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    subscription = _persist_subscription(
        context,
        tenant,
        key="http-update-redirection",
    )

    before = context.subscriptions.find_one(
        {
            "tenant_id": tenant,
            "subscription_id":
                subscription.subscription_id,
        },
        {"_id": 0},
    )

    response = _client(context).put(
        (
            "/api/subscriptions/"
            + subscription.subscription_id
        ),
        headers=_headers(
            principal,
            tenant,
        ),
        json={
            "amount": 0.01,
        },
    )

    assert response.status_code == 422
    assert (
        "SUBSCRIPTION_UPDATE_INVALID_FIELDS"
        in response.text
    )

    after = context.subscriptions.find_one(
        {
            "tenant_id": tenant,
            "subscription_id":
                subscription.subscription_id,
        },
        {"_id": 0},
    )

    assert after == before


def test_http_upgrade_uses_newplanid_only_and_derives_snapshot(
    context: Context,
) -> None:
    principal = "principal-" + uuid.uuid4().hex
    tenant = "tenant-" + uuid.uuid4().hex

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    subscription = _persist_subscription(
        context,
        tenant,
        key="http-upgrade-base",
    )

    target = _seed_plan(
        plan="SOVEREIGN",
        amount=2500.0,
        features=(
            "crm.core",
            "legal.documents",
            "wilsy.ai",
        ),
    )

    response = _client(context).post(
        (
            "/api/subscriptions/"
            + subscription.subscription_id
            + "/upgrade"
        ),
        headers=_headers(
            principal,
            tenant,
        ),
        json={
            "newPlanId": target.plan_id,
        },
    )

    assert response.status_code == 200

    persisted = context.subscriptions.find_one(
        {
            "tenant_id": tenant,
            "subscription_id":
                subscription.subscription_id,
        }
    )

    assert persisted is not None
    assert persisted["plan_id"] == target.plan_id
    assert persisted["amount"] == float(target.price)
    assert persisted["currency"] == target.currency
    assert persisted["plan_features"] == list(target.features)
    assert (
        persisted["plan_catalogue_version"]
        == target.catalogue_version
    )

    redirected = _client(context).post(
        (
            "/api/subscriptions/"
            + subscription.subscription_id
            + "/upgrade"
        ),
        headers=_headers(
            principal,
            tenant,
        ),
        json={
            "newPlanId": target.plan_id,
            "newAmount": 1.0,
        },
    )

    assert redirected.status_code == 422
    assert (
        "SUBSCRIPTION_PLAN_CHANGE_INVALID_FIELDS"
        in redirected.text
    )


def test_http_plan_catalogue_outage_after_valid_authority_is_bounded_503(
    context: Context,
) -> None:
    principal = "principal-" + uuid.uuid4().hex
    tenant = "tenant-" + uuid.uuid4().hex

    _seed(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    plan = _seed_plan(
        plan="ENTERPRISE",
        amount=612.0,
    )

    dead = MongoClient(
        "mongodb://127.0.0.1:1/sub_plan_dead",
        serverSelectionTimeoutMS=150,
    )

    original = plan_registry_module.plans_collection

    plan_registry_module.plans_collection = (
        dead["sub_plan_dead"]["plans"]
    )

    try:
        response = _client(context).post(
            "/api/subscriptions",
            headers=_headers(
                principal,
                tenant,
            ),
            json=_command(
                tenant,
                "http-plan-outage",
                plan_id=plan.plan_id,
            ),
        )
    finally:
        plan_registry_module.plans_collection = original
        dead.close()

    assert response.status_code == 503

    # Bounded failure: no Mongo internals or caller-selected commercial truth.
    assert (
        "SUBSCRIPTION_PERSISTENCE_UNAVAILABLE"
        in response.text
    )
    assert plan.plan_id not in response.text
    assert (
        context.subscriptions.count_documents({})
        == 0
    )


def test_http_create_derives_calendar_period_and_denies_period_redirection(
    context: Context,
) -> None:
    """Certify server-derived period truth and deny caller redirection."""
    principal_id = (
        "principal-calendar-"
        + uuid.uuid4().hex
    )

    tenant_id = (
        "tenant-calendar-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal_id,
        tenant_id=tenant_id,
    )

    with TestClient(
        context.app
    ) as client:
        created = client.post(
            "/api/subscriptions",
            json=_payload(
                tenant_id,
                "http-calendar-derived",
            ),
            headers=_headers(
                principal_id,
                tenant_id,
            ),
        )

        assert created.status_code == 201

        assert (
            "2026-09-01T00:00:00+00:00"
            in created.text
        )

        assert (
            "2026-10-01T00:00:00+00:00"
            in created.text
        )

        count_before = (
            context.subscriptions.count_documents(
                {
                    "tenant_id":
                        tenant_id
                }
            )
        )

        redirected = _payload(
            tenant_id,
            "http-period-redirection",
        )

        redirected[
            "currentPeriodStart"
        ] = "2026-09-03T00:00:00+00:00"

        redirected[
            "currentPeriodEnd"
        ] = "2026-10-03T00:00:00+00:00"

        denied = client.post(
            "/api/subscriptions",
            json=redirected,
            headers=_headers(
                principal_id,
                tenant_id,
            ),
        )

        assert denied.status_code == 422

        assert (
            "SUBSCRIPTION_COMMERCIAL_REDIRECTION_FORBIDDEN"
            in denied.text
        )

        assert (
            context.subscriptions.count_documents(
                {
                    "tenant_id":
                        tenant_id
                }
            )
            == count_before
        )


def test_http_generic_update_cannot_replace_calendar_period(
    context: Context,
) -> None:
    """Certify manage authority cannot replace registry period truth."""
    principal_id = (
        "principal-calendar-update-"
        + uuid.uuid4().hex
    )

    tenant_id = (
        "tenant-calendar-update-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal_id,
        tenant_id=tenant_id,
    )

    with TestClient(
        context.app
    ) as client:
        created = client.post(
            "/api/subscriptions",
            json=_payload(
                tenant_id,
                "http-calendar-update-create",
            ),
            headers=_headers(
                principal_id,
                tenant_id,
            ),
        )

        assert created.status_code == 201

        persisted_before = (
            context.subscriptions.find_one(
                {
                    "tenant_id":
                        tenant_id
                }
            )
        )

        assert persisted_before is not None

        subscription_id = (
            persisted_before[
                "subscription_id"
            ]
        )

        period_start_before = (
            persisted_before[
                "current_period_start"
            ]
        )

        period_end_before = (
            persisted_before[
                "current_period_end"
            ]
        )

        denied = client.put(
            (
                "/api/subscriptions/"
                + subscription_id
            ),
            json={
                "current_period_end":
                    "2099-01-01T00:00:00+00:00",
            },
            headers=_headers(
                principal_id,
                tenant_id,
            ),
        )

        assert denied.status_code == 422

        assert (
            "SUBSCRIPTION_UPDATE_INVALID_FIELDS"
            in denied.text
        )

        persisted_after = (
            context.subscriptions.find_one(
                {
                    "tenant_id":
                        tenant_id,
                    "subscription_id":
                        subscription_id,
                }
            )
        )

        assert persisted_after is not None

        assert (
            persisted_after[
                "current_period_start"
            ]
            == period_start_before
        )

        assert (
            persisted_after[
                "current_period_end"
            ]
            == period_end_before
        )


def test_http_naive_start_date_fails_closed_without_subscription_persistence(
    context: Context,
) -> None:
    """Certify explicit timezone is mandatory through the HTTP path."""
    principal_id = (
        "principal-naive-calendar-"
        + uuid.uuid4().hex
    )

    tenant_id = (
        "tenant-naive-calendar-"
        + uuid.uuid4().hex
    )

    _seed(
        context,
        principal_id=principal_id,
        tenant_id=tenant_id,
    )

    payload = _payload(
        tenant_id,
        "http-naive-calendar",
    )

    payload["startDate"] = (
        "2026-09-03T00:00:00"
    )

    with TestClient(
        context.app
    ) as client:
        response = client.post(
            "/api/subscriptions",
            json=payload,
            headers=_headers(
                principal_id,
                tenant_id,
            ),
        )

    assert response.status_code == 400

    assert (
        "SUBSCRIPTION_CREATE_FAILED"
        in response.text
    )

    assert (
        context.subscriptions.count_documents(
            {
                "tenant_id":
                    tenant_id
            }
        )
        == 0
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tests/integration/test_subscription_router_authority_real_mongo.py
# VERSION: v1.2.0-SUBSCRIPTION-CALENDAR-BILLING-HTTP-CERT
# AUTHORITY BOUNDARY: real HTTP composition of principal, membership, permission, canonical PlanRegistry catalogue provenance and real subscription persistence only
# TENANT POSTURE: raw tenant context must survive ACTIVE persisted membership and current role-assignment permission authority
# FAIL-CLOSED POSTURE: missing identity, wrong tenant, inactive membership, absent/revoked role, projected JWT grants and persistence outage never become subscription access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
