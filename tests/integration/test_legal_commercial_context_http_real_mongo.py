"""Real HTTP + real authority + real Mongo certificate for Legal commercial context.

TITLE:
    WILSY OS Legal Commercial Context HTTP Authority Real-Mongo Certificate

VERSION:
    v1.0.1-LEGAL-COMMERCIAL-CONTEXT-HTTP-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Execute the production Legal Operations commercial-context HTTP route with
    actual JWT authentication, actual Mongo principal/membership/role truth,
    actual canonical Plan/Subscription persistence and actual current Legal
    product-entitlement persistence. Prove least-privilege commercial visibility,
    exact tenant isolation and fail-closed behavior without widening Legal IAM.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_commercial_context_http_real_mongo.py

COLLABORATION / OWNERSHIP:
    Authentication owns principal admission.
    Tenant membership and role-assignment repositories own current IAM truth.
    subscription:read owns commercial-read permission vocabulary.
    SubscriptionRegistry owns commercial persistence.
    D22B2 owns product-entitlement history/current persistence.
    LegalOperationsRouter owns bounded HTTP projection only.
    This artifact owns certification evidence only.

CERTIFICATION / UPDATE DATE:
    2026-10-16

CHANGELOG:
    v1.0.1-LEGAL-COMMERCIAL-CONTEXT-HTTP-REAL-MONGO-CERT
        - Aligns expected workspace_key with canonical product catalogue
          projection LEGAL_DASHBOARD rather than a test-authored alias.
        - Accepts authentication/tenant authority denial as either 401 or
          403 while still requiring fail-closed non-disclosure.
        - Changes certificate expectations only; production HTTP, IAM,
          subscription, entitlement and financial authority are unchanged.

    v1.0.0-LEGAL-COMMERCIAL-CONTEXT-HTTP-REAL-MONGO-CERT
        - Certifies ENTERPRISE_ADMIN and AUDITOR commercial-context reads.
        - Proves LEGAL_PARTNER receives no implicit commercial pricing authority.
        - Proves raw tenant/JWT projections cannot bypass persisted IAM.
        - Proves foreign-tenant selection is denied.
        - Proves canonical Legal subscription/entitlement values reach HTTP.
        - Proves response creates no mutation or financial execution authority.

COMPLIANCE:
    POPIA section 19 technical controls.
    GDPR Article 32 technical controls.
    SOC 2 CC7.2-aligned technical controls.
    ISO 27001-aligned technical controls.
    No independent legal-compliance claim is created.

SECURITY / PRIVACY POSTURE:
    UUID-isolated synthetic principals, tenants and commercial records only.
    No credentials, customer data, production tenants or protected Mongo instance.

TENANT BOUNDARY:
    X-Tenant-ID is request context only. ACTIVE persisted membership and current
    role assignment must admit the exact tenant. Foreign tenant scope denies.

AUTHORITY BOUNDARY:
    subscription:read is required through current Python authority.
    Legal role possession alone does not grant commercial read authority.
    This test grants no role, permission, Legal lifecycle or commercial mutation.

FINANCIAL AUTHORITY BOUNDARY:
    Plan and subscription amounts are descriptive commercial evidence only.
    APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
    Kennel EOS remains exclusive financial execution authority.

TRANSACTION BOUNDARY:
    The HTTP route owns one read-only snapshot transaction.
    Setup writes use existing canonical owners and explicit real transactions.

FAIL-CLOSED POSTURE:
    Missing identity, projected JWT permission, absent role grant, foreign tenant,
    entitlement/subscription mismatch or persistence failure cannot become success.

CONSTITUTION:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    NO EVIDENCE = NO FACT.
"""
from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

os.environ.setdefault(
    "WILSY_JWT_SECRET",
    "LEGAL-COMMERCIAL-CONTEXT-HTTP-CERT-ONLY-SECRET",
)

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.legal_operations_router as legal_router
import tools.eos.auth.authentication as authentication_module
import tools.eos.kernel.db as kernel_db
import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_active_entitlement_composition_service as service_module
import tools.eos.saas.billing.subscription_registry as registry_module
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.authentication import get_principal_authority_repository
from tools.eos.auth.authorization import get_role_assignment_repository
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.jwt_provider import TokenPurpose, create_access_token
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
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_active_entitlement_composition_service import (
    SubscriptionActiveEntitlementCompositionService,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as ENTITLEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as ENTITLEMENT_HISTORY_COLLECTION,
    ensure_indexes as ensure_entitlement_indexes,
)


VERSION = "v1.0.1-LEGAL-COMMERCIAL-CONTEXT-HTTP-REAL-MONGO-CERT"
MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 10, 16, 9, 0, tzinfo=timezone.utc)


class PrincipalFacade:
    """Bind authentication principal reads to isolated actual Mongo."""

    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
        self.collection = collection

    def get(
        self,
        principal_id: str,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> PrincipalAuthority:
        try:
            return PrincipalAuthorityRepository.get(
                principal_id,
                self.collection,
                session=session,
            )
        except PrincipalAuthorityRepositoryError:
            raise


class CredentialRevisionFacade:
    """Expose revision-zero credentials for persisted synthetic principals."""

    def __init__(self, principals: Collection[dict[str, Any]]) -> None:
        self.principals = principals

    def get_credential_revision(
        self,
        tenant_id: str,
        principal_id: str,
        *,
        session: Any = None,
    ) -> int:
        PrincipalAuthorityRepository.get(
            principal_id,
            self.principals,
            session=session,
        )
        return 0


class MembershipFacade:
    """Bind tenant membership resolution to isolated actual Mongo."""

    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        collection: Any = None,
        *,
        session: Any = None,
    ) -> TenantMembershipAuthority:
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
    """Bind current role possession to isolated actual Mongo."""

    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
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
    client: MongoClient[Any]
    database: Any
    principals: Collection[dict[str, Any]]
    memberships: Collection[dict[str, Any]]
    roles: Collection[dict[str, Any]]
    subscriptions: Collection[dict[str, Any]]
    plans: Collection[dict[str, Any]]
    app: FastAPI


@pytest.fixture()
def context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Context]:
    """Create one UUID-isolated real authority + commercial Mongo environment."""
    if not MONGO_URI:
        pytest.fail("TEST_VENDOR_MONGO_URI is required")

    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=4000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None

    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"commercial HTTP Mongo unavailable: {type(error).__name__}"
            )

        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None

        database = client[
            f"wilsy_legal_commercial_http_{uuid.uuid4().hex}"
        ]

        principals = database["principal_authorities"]
        memberships = database["tenant_memberships"]
        roles = database["role_assignments"]

        subscriptions: Collection[dict[str, Any]] = database.get_collection(
            "subscriptions",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        plans: Collection[dict[str, Any]] = database.get_collection(
            "plans",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )

        PrincipalAuthorityRepository.ensure_indexes(principals)
        TenantMembershipRepository.ensure_indexes(memberships)
        RoleAssignmentRepository.ensure_indexes(roles)

        monkeypatch.setattr(
            registry_module,
            "subscriptions_collection",
            subscriptions,
        )
        monkeypatch.setattr(
            plan_registry_module,
            "plans_collection",
            plans,
        )
        monkeypatch.setattr(
            kernel_db,
            "get_client",
            lambda: client,
        )
        monkeypatch.setattr(
            kernel_db,
            "get_database",
            lambda: database,
        )
        monkeypatch.setattr(
            service_module,
            "get_client",
            lambda: client,
        )
        monkeypatch.setattr(
            service_module,
            "get_database",
            lambda: database,
        )
        monkeypatch.setattr(
            legal_router,
            "_db_handles",
            lambda: (client, database),
        )

        PlanRegistry.provision_indexes()
        registry_module._ensure_indexes()
        service_module._authorization_registry(database).ensure_indexes()
        ensure_entitlement_indexes(
            database[ENTITLEMENT_HISTORY_COLLECTION],
            database[ENTITLEMENT_CURRENT_COLLECTION],
        )

        app = FastAPI()
        register_error_handlers(app, debug=False)
        app.include_router(
            legal_router.router,
            prefix="/api",
        )

        app.dependency_overrides[
            get_principal_authority_repository
        ] = lambda: PrincipalFacade(principals)
        app.dependency_overrides[
            get_tenant_membership_repository
        ] = lambda: MembershipFacade(memberships)
        app.dependency_overrides[
            get_role_assignment_repository
        ] = lambda: RoleFacade(roles)

        original_auth_registry = authentication_module.AuthRegistry
        authentication_module.AuthRegistry = (
            lambda: CredentialRevisionFacade(principals)
        )

        try:
            yield Context(
                client=client,
                database=database,
                principals=principals,
                memberships=memberships,
                roles=roles,
                subscriptions=subscriptions,
                plans=plans,
                app=app,
            )
        finally:
            authentication_module.AuthRegistry = original_auth_registry
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed_principal(
    context: Context,
    *,
    principal_id: str,
    tenant_id: str,
    role_id: str,
    add_tenant_owner: bool = False,
) -> None:
    """Persist exact current principal, membership and role authority."""
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            principal_id,
            PrincipalStatus.ACTIVE,
            0,
        ),
        context.principals,
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        context.memberships,
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal_id,
            tenant_id,
            role_id,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        context.roles,
    )
    if add_tenant_owner:
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal_id,
                tenant_id,
                "tenant_owner",
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            context.roles,
        )


def _identity(
    principal_id: str,
    tenant_id: str,
) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="LEGAL-COMMERCIAL-HTTP-CERT",
        status=PrincipalStatus.ACTIVE,
    )


def _token(
    principal_id: str,
    tenant_id: str,
    *,
    projected_permissions: bool = False,
) -> str:
    """Create transport projections that remain non-authoritative."""
    return create_access_token(
        {
            "identity_id": principal_id,
            "tenant_id": tenant_id,
            "roles": ["ENTERPRISE_ADMIN"]
            if projected_permissions
            else [],
            "permissions": [
                "subscription:read",
                "plan:read",
            ]
            if projected_permissions
            else [],
        },
        expires_in_seconds=3600,
        token_purpose=TokenPurpose.ACCESS,
        credential_revision=0,
    )


def _headers(
    principal_id: str,
    tenant_id: str,
    *,
    projected_permissions: bool = False,
) -> dict[str, str]:
    return {
        "Authorization": (
            "Bearer "
            + _token(
                principal_id,
                tenant_id,
                projected_permissions=projected_permissions,
            )
        ),
        "X-Tenant-ID": tenant_id,
    }


def _seed_legal_commercial_truth(
    context: Context,
    *,
    tenant_id: str,
    principal_id: str,
) -> Any:
    """Create canonical plan + ACTIVE subscription + ACTIVE Legal entitlement."""
    plan = PlanRegistry.create(
        {
            "name": "WILSY Legal Enterprise",
            "price": 14400.0,
            "currency": "ZAR",
            "billingFrequency": "annual",
            "planType": "ENTERPRISE",
            "idempotencyKey": f"plan-{tenant_id}",
            "active": True,
            "features": ["legal.core"],
            "metadata": {
                "certificate":
                    "LEGAL-COMMERCIAL-HTTP-REAL-MONGO",
            },
            "tags": ["legal-commercial-http-cert"],
            "user": "LEGAL-COMMERCIAL-HTTP-CERT",
        }
    )
    assert plan["success"] is True

    result = SubscriptionActiveEntitlementCompositionService.create(
        {
            "tenantId": tenant_id,
            "planId": plan["plan"].plan_id,
            "startDate": NOW.isoformat(),
            "idempotencyKey": f"subscription-{tenant_id}",
            "billingMode": "PLATFORM",
            "onboardingRef": f"ONBOARD-{tenant_id}",
            "metadata": {
                "certificate":
                    "LEGAL-COMMERCIAL-HTTP-REAL-MONGO",
            },
        },
        _identity(
            principal_id,
            tenant_id,
        ),
    )

    assert result.legal_entitlement_applicable is True
    assert result.entitlement_issuance_result is not None
    return result


def _get(
    context: Context,
    *,
    principal_id: str,
    tenant_id: str,
    projected_permissions: bool = False,
) -> Any:
    with TestClient(
        context.app,
        raise_server_exceptions=False,
    ) as client:
        return client.get(
            "/api/legal-operations/commercial-context",
            headers=_headers(
                principal_id,
                tenant_id,
                projected_permissions=projected_permissions,
            ),
        )


def test_enterprise_admin_reads_exact_canonical_commercial_context(
    context: Context,
) -> None:
    """Current ENTERPRISE_ADMIN sees canonical Legal commercial evidence."""
    principal = f"principal-admin-{uuid.uuid4().hex}"
    tenant = f"tenant-admin-{uuid.uuid4().hex}"

    _seed_principal(
        context,
        principal_id=principal,
        tenant_id=tenant,
        role_id="ENTERPRISE_ADMIN",
        add_tenant_owner=True,
    )
    created = _seed_legal_commercial_truth(
        context,
        tenant_id=tenant,
        principal_id=principal,
    )

    response = _get(
        context,
        principal_id=principal,
        tenant_id=tenant,
    )

    assert response.status_code == 200
    body = response.json()

    assert body["tenant_id"] == tenant
    assert (
        body["visibility"]
        == "LEGAL_COMMERCIAL_CONTEXT_SUBSCRIPTION_READ"
    )
    assert body["product"] == {
        "product_id": "LEGAL_OPERATIONS",
        "workspace_key": "LEGAL_DASHBOARD",
        "available": True,
        "entitlement_state": "ACTIVE",
    }
    assert (
        body["subscription"]["subscription_id"]
        == created.subscription.subscription_id
    )
    assert body["subscription"]["status"] == "active"
    assert body["plan"]["tier"] == "ENTERPRISE"
    assert body["plan"]["name"] == "WILSY Legal Enterprise"
    assert body["plan"]["features"] == ["legal.core"]
    assert body["commercial"]["amount"] == 14400.0
    assert body["commercial"]["currency"] == "ZAR"
    assert body["commercial"]["billing_frequency"] == "annual"
    assert body["commercial"]["monthly_equivalent_amount"] == 1200.0
    assert body["commercial"]["financial_execution_authority"] is False


def test_auditor_can_read_existing_commercial_context(
    context: Context,
) -> None:
    """AUDITOR can read but receives no mutation authority."""
    admin = f"principal-admin-{uuid.uuid4().hex}"
    auditor = f"principal-auditor-{uuid.uuid4().hex}"
    tenant = f"tenant-auditor-{uuid.uuid4().hex}"

    _seed_principal(
        context,
        principal_id=admin,
        tenant_id=tenant,
        role_id="ENTERPRISE_ADMIN",
        add_tenant_owner=True,
    )
    _seed_principal(
        context,
        principal_id=auditor,
        tenant_id=tenant,
        role_id="AUDITOR",
    )
    _seed_legal_commercial_truth(
        context,
        tenant_id=tenant,
        principal_id=admin,
    )

    before = (
        context.subscriptions.count_documents({"tenant_id": tenant}),
        context.database[ENTITLEMENT_HISTORY_COLLECTION]
        .count_documents({"tenant_id": tenant}),
        context.database[ENTITLEMENT_CURRENT_COLLECTION]
        .count_documents({"tenant_id": tenant}),
    )

    response = _get(
        context,
        principal_id=auditor,
        tenant_id=tenant,
    )

    after = (
        context.subscriptions.count_documents({"tenant_id": tenant}),
        context.database[ENTITLEMENT_HISTORY_COLLECTION]
        .count_documents({"tenant_id": tenant}),
        context.database[ENTITLEMENT_CURRENT_COLLECTION]
        .count_documents({"tenant_id": tenant}),
    )

    assert response.status_code == 200
    assert before == after == (1, 2, 1)


def test_legal_partner_does_not_inherit_commercial_read(
    context: Context,
) -> None:
    """Legal practice role alone cannot read subscription/price context."""
    admin = f"principal-admin-{uuid.uuid4().hex}"
    partner = f"principal-partner-{uuid.uuid4().hex}"
    tenant = f"tenant-partner-{uuid.uuid4().hex}"

    _seed_principal(
        context,
        principal_id=admin,
        tenant_id=tenant,
        role_id="ENTERPRISE_ADMIN",
        add_tenant_owner=True,
    )
    _seed_principal(
        context,
        principal_id=partner,
        tenant_id=tenant,
        role_id="LEGAL_PARTNER",
    )
    _seed_legal_commercial_truth(
        context,
        tenant_id=tenant,
        principal_id=admin,
    )

    response = _get(
        context,
        principal_id=partner,
        tenant_id=tenant,
    )

    assert response.status_code == 403
    assert "14400" not in response.text
    assert "1200" not in response.text
    assert "WILSY Legal Enterprise" not in response.text


def test_projected_jwt_permission_without_persisted_role_denies(
    context: Context,
) -> None:
    """JWT role/permission projections never substitute for current IAM truth."""
    principal = f"principal-jwt-{uuid.uuid4().hex}"
    tenant = f"tenant-jwt-{uuid.uuid4().hex}"

    _seed_principal(
        context,
        principal_id=principal,
        tenant_id=tenant,
        role_id="LEGAL_PARTNER",
    )

    response = _get(
        context,
        principal_id=principal,
        tenant_id=tenant,
        projected_permissions=True,
    )

    assert response.status_code == 403


def test_foreign_tenant_header_cannot_redirect_commercial_read(
    context: Context,
) -> None:
    """Current admin for tenant A cannot select tenant B by transport header."""
    principal = f"principal-foreign-{uuid.uuid4().hex}"
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"

    _seed_principal(
        context,
        principal_id=principal,
        tenant_id=tenant_a,
        role_id="ENTERPRISE_ADMIN",
        add_tenant_owner=True,
    )
    _seed_legal_commercial_truth(
        context,
        tenant_id=tenant_a,
        principal_id=principal,
    )

    response = _get(
        context,
        principal_id=principal,
        tenant_id=tenant_b,
    )

    assert response.status_code in {401, 403}
    assert tenant_a not in response.text
    assert "14400" not in response.text


def test_raw_tenant_header_without_authenticated_principal_denies(
    context: Context,
) -> None:
    """X-Tenant-ID alone is not commercial authority."""
    tenant = f"tenant-raw-{uuid.uuid4().hex}"

    with TestClient(
        context.app,
        raise_server_exceptions=False,
    ) as client:
        response = client.get(
            "/api/legal-operations/commercial-context",
            headers={"X-Tenant-ID": tenant},
        )

    assert response.status_code in {401, 403}


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_commercial_context_http_real_mongo.py
# VERSION: v1.0.1-LEGAL-COMMERCIAL-CONTEXT-HTTP-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: certification only; existing subscription:read remains sole commercial-read permission
# TENANT POSTURE: exact persisted principal + ACTIVE membership + current role assignment + exact tenant
# FAIL-CLOSED POSTURE: raw headers, projected JWT grants, Legal role inheritance and foreign tenant selection deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
