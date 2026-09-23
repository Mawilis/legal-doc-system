"""Live-IAM real-Mongo certificate for sheriff operational queues.

TITLE: WILSY OS Sheriff Operational Queue Live-IAM Real-Mongo Certificate
VERSION: v1.0.1-L8-6C-ROUTER-COMPAT-SHERIFF-QUEUE-LIVE-IAM-RM-CERT
AUTHORITY: Host-backed certification of sheriff-only operational queue reads.
EPITOME: Prove durable principal, membership, business-role, and authorization-
         role truth authorizes SHERIFF queue reads before lifecycle access,
         denies DEPUTY before lifecycle access, preserves exact tenant scope,
         and exposes only certified L8-5C current-state queue truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_sheriff_queue_http_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for L8-6A IAM+HTTP composition.
                            P1/P2/L8-0/L8-5/L8-5C remain canonical lifecycle
                            and queue authorities; IAM remains separate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-6C-ROUTER-COMPAT-SHERIFF-QUEUE-LIVE-IAM-RM-CERT
           rebinds the sealed live-IAM sheriff queue certificate to the
           additive L8-6C read router; sheriff allow/deputy tenant-wide denial
           and real-Mongo queue assertions are unchanged.
           2026-09-23 v1.0.0-L8-6A-SHERIFF-OPERATIONAL-QUEUE-LIVE-IAM-RM-CERT
           establishes durable sheriff allow/deputy deny ordering, exact-tenant
           queue projection, foreign-scope denial before lifecycle access, and
           exclusion of mock dashboard, billing, geospatial, AI, and financial
           truth on the verified Mongo replica set.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and opaque legal
                             identities only; no real client, credential,
                             provider, geospatial, AI, or payment data.
TENANT BOUNDARY: Durable membership, business role, final role assignment, and
                 lifecycle queue reads all bind the exact selected tenant.
AUTHORITY BOUNDARY: Certificate and read projection only; no receipt,
                    allocation, attempt, service, return, billing, payment,
                    execution, settlement, or deputy impersonation authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: No product transaction is started by the route; this
                      certificate uses majority durability for isolated setup.
FAIL-CLOSED DECLARATION: Wrong Mongo runtime, inactive/missing IAM truth,
                         ineligible deputy role, foreign scope, queue corruption,
                         or unsupported projection fails without fallback.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ProcessDocument,
    ProcessDocumentState,
    ServiceAttempt,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.1-L8-6C-ROUTER-COMPAT-SHERIFF-QUEUE-LIVE-IAM-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 14, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated database; runtime failure is fatal."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_6A_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_6A_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_6A_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_6a_sheriff_queue_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        principal = database.get_collection(
            "principal_authorities",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        membership = database.get_collection(
            "tenant_memberships",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        roles = database.get_collection(
            "role_assignments",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        business_roles = database.get_collection(
            "tenant_business_roles",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )

        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        from tools.eos.auth.principal_authority_repository import (
            PrincipalAuthorityRepository,
        )
        from tools.eos.auth.role_assignment_repository import (
            RoleAssignmentRepository,
        )
        from tools.eos.auth.tenant_business_role_repository import (
            TenantBusinessRoleRepository,
        )
        from tools.eos.auth.tenant_membership_repository import (
            TenantMembershipRepository,
        )

        PrincipalAuthorityRepository.ensure_indexes(principal)
        TenantMembershipRepository.ensure_indexes(membership)
        RoleAssignmentRepository.ensure_indexes(roles)
        TenantBusinessRoleRepository.ensure_indexes(business_roles)

        yield {
            "lifecycle": lifecycle,
            "principal": principal,
            "membership": membership,
            "roles": roles,
            "business_roles": business_roles,
        }
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _identity(tenant_id: str) -> SovereignIdentity:
    """Return one authenticated transport identity; durable stores still authorize."""
    return SovereignIdentity(
        identity_id="principal-1",
        tenant_id=tenant_id,
        username="operator",
        email="operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


class _PrincipalReader:
    def __init__(self, collection: Any, calls: list[str]) -> None:
        self.collection = collection
        self.calls = calls

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        self.calls.append("principal")
        from tools.eos.auth.principal_authority_repository import (
            PrincipalAuthorityRepository,
        )
        return PrincipalAuthorityRepository.get(
            principal_id,
            self.collection,
            session=session,
        )


class _MembershipReader:
    def __init__(self, collection: Any, calls: list[str]) -> None:
        self.collection = collection
        self.calls = calls

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        self.calls.append("membership")
        from tools.eos.auth.tenant_membership_repository import (
            TenantMembershipRepository,
        )
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


class _RoleReader:
    """Resolve tenant business roles and final authorization roles separately."""

    def __init__(
        self,
        authorization_collection: Any,
        business_collection: Any,
        calls: list[str],
    ) -> None:
        self.authorization_collection = authorization_collection
        self.business_collection = business_collection
        self.calls = calls

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> Any:
        from tools.eos.auth.role_assignment_repository import (
            RoleAssignmentNotFoundError,
            RoleAssignmentRepository,
        )
        from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
        from tools.eos.auth.tenant_business_role_repository import (
            TenantBusinessRoleNotFoundError,
            TenantBusinessRoleRepository,
        )

        if role_id in TENANT_ROLES:
            self.calls.append("business_role")
            try:
                value = TenantBusinessRoleRepository.resolve(
                    principal_id,
                    tenant_id,
                    self.business_collection,
                    session=session,
                )
            except TenantBusinessRoleNotFoundError as error:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from error
            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                )
            return value

        self.calls.append("authorization_role")
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self.authorization_collection,
            session=session,
        )


class _LifecycleReader:
    """Trace lifecycle access while delegating the real Mongo read contract."""

    def __init__(self, collection: Any, calls: list[str]) -> None:
        self.collection = collection
        self.calls = calls

    def find(self, query: Any, **kwargs: Any) -> Any:
        self.calls.append("lifecycle")
        return self.collection.find(query, **kwargs)

    def find_one(self, query: Any, **kwargs: Any) -> Any:
        self.calls.append("lifecycle")
        return self.collection.find_one(query, **kwargs)


def _persist_iam(
    collections: dict[str, Any],
    tenant_id: str,
    *,
    business_role: str,
    authorization_role: str,
) -> None:
    """Persist the four conjunctive durable authorization authorities."""
    from tools.eos.auth.principal_authority import PrincipalAuthority
    from tools.eos.auth.principal_authority_repository import (
        PrincipalAuthorityRepository,
    )
    from tools.eos.auth.role_assignment import (
        RoleAssignmentAuthority,
        RoleAssignmentStatus,
    )
    from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
    from tools.eos.auth.tenant_business_role import (
        TenantBusinessRoleAuthority,
        TenantBusinessRoleStatus,
    )
    from tools.eos.auth.tenant_business_role_repository import (
        TenantBusinessRoleRepository,
    )
    from tools.eos.auth.tenant_membership import (
        TenantMembershipAuthority,
        TenantMembershipStatus,
    )
    from tools.eos.auth.tenant_membership_repository import (
        TenantMembershipRepository,
    )

    PrincipalAuthorityRepository.create(
        PrincipalAuthority("principal-1", PrincipalStatus.ACTIVE, 0),
        collections["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            "principal-1",
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collections["membership"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            "principal-1",
            tenant_id,
            business_role,
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        collections["business_roles"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            "principal-1",
            tenant_id,
            authorization_role,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collections["roles"],
    )


def _persist_queue_truth(collection: Any, tenant_id: str) -> None:
    """Persist current states spanning all three certified L8-5C queue families."""
    office = ProcessDocument(
        tenant_id=tenant_id,
        document_id="document-office",
        case_matter_id="matter-office",
        document_type="summons",
        registered_at=NOW,
        registration_evidence_reference="registered-office",
    )
    received_base = ProcessDocument(
        tenant_id=tenant_id,
        document_id="document-received",
        case_matter_id="matter-received",
        document_type="summons",
        registered_at=NOW,
        registration_evidence_reference="registered-received",
    )
    received = received_base.transition_to(
        ProcessDocumentState.RECEIVED,
        evidence_reference="received-office",
        occurred_at=NOW + timedelta(minutes=1),
    )
    attempt = ServiceAttempt(
        tenant_id=tenant_id,
        attempt_id="attempt-active",
        instruction_id="instruction-active",
        document_id="document-active",
        deputy_id="deputy-canonical",
        allocated_at=NOW,
        allocation_evidence_reference="attempt-allocation",
    )
    for value in (office, received_base, received, attempt):
        assert LegalOperationsLifecycleRegistry.create(value, collection) == value


def _app(
    collections: dict[str, Any],
    identity_tenant: str,
    calls: list[str],
) -> FastAPI:
    """Mount the real queue route with only repository providers isolated."""
    import tools.eos.api.tenant_authorization_http as authorization_http
    import tools.eos.auth.authentication as authentication
    import tools.eos.auth.tenant_access as tenant_access

    app = FastAPI()
    register_error_handlers(app, debug=False)
    principal_reader = _PrincipalReader(collections["principal"], calls)
    membership_reader = _MembershipReader(collections["membership"], calls)
    role_reader = _RoleReader(
        collections["roles"],
        collections["business_roles"],
        calls,
    )

    app.dependency_overrides[authorization_http.get_current_identity] = (
        lambda: _identity(identity_tenant)
    )
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: principal_reader
    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: membership_reader
    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: role_reader
    app.dependency_overrides[legal_router.get_lifecycle_collection] = (
        lambda: _LifecycleReader(collections["lifecycle"], calls)
    )
    assert legal_router._QUEUE_READ not in app.dependency_overrides
    app.include_router(legal_router.router, prefix="/api")
    return app


def _queue_request(
    collections: dict[str, Any],
    identity_tenant: str,
    scope_tenant: str,
    calls: list[str],
) -> Any:
    with TestClient(_app(collections, identity_tenant, calls)) as client:
        return client.get(
            "/api/legal-operations/operational-queues",
            headers={"X-Tenant-ID": scope_tenant},
        )


def test_real_mongo_sheriff_authorizes_before_exact_queue_read(
    mongo_context: dict[str, Any],
) -> None:
    """Durable sheriff authority precedes and admits exact-tenant L8-5C reads."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    _persist_iam(
        mongo_context,
        tenant,
        business_role="tenant_sheriff",
        authorization_role="SHERIFF",
    )
    _persist_queue_truth(mongo_context["lifecycle"], tenant)
    calls: list[str] = []

    response = _queue_request(mongo_context, tenant, tenant, calls)

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == tenant
    assert body["visibility"] == "SHERIFF_OPERATIONAL_QUEUE"
    assert [item["document_id"] for item in body["office_receipt"]] == [
        "document-office"
    ]
    assert [item["document_id"] for item in body["deputy_assignment"]] == [
        "document-received"
    ]
    assert [item["attempt_id"] for item in body["active_attempts"]] == [
        "attempt-active"
    ]
    for required in ("principal", "membership", "business_role", "authorization_role"):
        assert required in calls
    assert "lifecycle" in calls
    assert max(
        calls.index("principal"),
        calls.index("membership"),
        calls.index("business_role"),
        calls.index("authorization_role"),
    ) < calls.index("lifecycle")

    serialized = str(body).casefold()
    for forbidden in (
        "urgent",
        "distance",
        "billing",
        "invoice",
        "payment",
        "settlement",
        "revenue",
        "gps",
        "ai_score",
        "client_name",
    ):
        assert forbidden not in serialized


def test_real_mongo_deputy_is_denied_before_any_tenant_wide_queue_read(
    mongo_context: dict[str, Any],
) -> None:
    """No principal-to-deputy binding means DEPUTY cannot read tenant-wide queues."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    _persist_iam(
        mongo_context,
        tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )
    _persist_queue_truth(mongo_context["lifecycle"], tenant)
    calls: list[str] = []

    response = _queue_request(mongo_context, tenant, tenant, calls)

    assert response.status_code == 403
    assert "principal" in calls
    assert "membership" in calls
    assert "business_role" in calls
    assert "lifecycle" not in calls


def test_real_mongo_foreign_scope_denies_before_lifecycle_access(
    mongo_context: dict[str, Any],
) -> None:
    """A sheriff identity cannot use a foreign tenant header as membership proof."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"
    _persist_iam(
        mongo_context,
        tenant,
        business_role="tenant_sheriff",
        authorization_role="SHERIFF",
    )
    _persist_queue_truth(mongo_context["lifecycle"], tenant)
    calls: list[str] = []

    response = _queue_request(mongo_context, tenant, foreign, calls)

    assert response.status_code == 403
    assert tenant != foreign
    assert "lifecycle" not in calls


def test_live_router_and_iam_bindings_match_l8_6a_release() -> None:
    """Host certificate remains bound to the exact L8-6A API/IAM vocabulary."""
    assert legal_router.VERSION == "v1.4.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-READ-API"
    assert legal_router._QUEUE_READ.permission_id == "legal_operations:queue:read"
    assert legal_router._QUEUE_READ.operation == "legal_queue_read"
    assert VERSION == "v1.0.1-L8-6C-ROUTER-COMPAT-SHERIFF-QUEUE-LIVE-IAM-RM-CERT"


# ARTIFACT: test_legal_operations_sheriff_queue_http_real_mongo.py
# VERSION: v1.0.1-L8-6C-ROUTER-COMPAT-SHERIFF-QUEUE-LIVE-IAM-RM-CERT
# AUTHORITY BOUNDARY: live-IAM real-Mongo sheriff operational-queue read certificate only
# TENANT POSTURE: exact durable sheriff tenant admitted; deputy and foreign scopes deny before lifecycle
# FAIL-CLOSED POSTURE: runtime/IAM/scope/queue evidence failures deny without personal-deputy or mock fallback
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
