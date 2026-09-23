"""TITLE: WILSY OS Legal Operations live-IAM current/history read API real-Mongo certificate.
VERSION: v1.3.0-L8-5-LIVE-IAM-CURRENT-HISTORY-READ-API-RM-CERT
AUTHORITY: Host-backed certificate for durable tenant authorization and canonical projections.
EPITOME: Proves the real RequireTenantAuthorization chain resolves durable principal,
membership, business-role, and granting-role truth before the canonical L8-5
entity read model exposes deterministic current-plus-history projections.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_http_real_mongo.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering; P1/P2 remain canonical authorities.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: v1.3.0-L8-5-LIVE-IAM-CURRENT-HISTORY-READ-API-RM-CERT certifies the L8-5 HTTP
current-plus-history projection through the unchanged durable principal,
membership, business-role, and granting-role chain, preserving current data
compatibility while proving canonical immutable history and no raw P2 leakage.
v1.2.1-L8-0-LIVE-IAM-CURRENT-READ-API-RM-CERT aligns the host-backed
IAM fixture with the canonical dedicated tenant_business_roles store introduced
by tenant_authorization_http v1.1.0, preserving separate business-role and
authorization-role truth while retaining deterministic current-read proofs.
v1.2.0-L8-0-LIVE-IAM-CURRENT-READ-API-RM-CERT added real-Mongo multi-snapshot
current selection and fork rejection while preserving the full durable IAM
authorization chain before lifecycle access.
v1.1.0-L7A-LIVE-IAM-READ-API-RM-CERT removed the final-authorization override
and certified durable principal, membership, business-role, granting-role,
revocation, inactive-state, ambiguity, cross-tenant, and client-policy denials.
v1.0.0-L7A-LEGAL-OPERATIONS-READ-API-RM-CERT certified own-tenant visibility,
foreign absence, and bounded output on Mongo.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated database and synthetic identifiers; no secrets or provider calls.
TENANT BOUNDARY: Every read predicate includes the exact authorized tenant.
AUTHORITY BOUNDARY: Certificate and current/history read projection only; no lifecycle or command mutation.
TRANSACTION BOUNDARY: This certificate uses no transaction; the registry owns none.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Host availability alone may skip; all post-hello product failures fail.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
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
    LegalInstruction,
    LegalInstructionState,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.3.0-L8-5-LIVE-IAM-CURRENT-HISTORY-READ-API-RM-CERT"
MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 15, 8, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Provide isolated majority collections; skip only pre-cert host absence."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
    except PyMongoError as error:
        client.close()
        pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}")
    if hello.get("setName") != EXPECTED_REPLICA_SET:
        client.close()
        pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
    if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
        client.close()
        pytest.skip("replica set has no writable primary")
    database = client[f"l7a_legal_{uuid.uuid4().hex}"]
    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    principal_collection = database.get_collection(
        "principal_authorities",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    membership_collection = database.get_collection(
        "tenant_memberships",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    role_collection = database.get_collection(
        "role_assignments",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    business_role_collection = database.get_collection(
        "tenant_business_roles",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    try:
        LegalOperationsLifecycleRegistry.ensure_indexes(collection)
        from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
        from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
        from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
        from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository

        PrincipalAuthorityRepository.ensure_indexes(principal_collection)
        TenantMembershipRepository.ensure_indexes(membership_collection)
        RoleAssignmentRepository.ensure_indexes(role_collection)
        TenantBusinessRoleRepository.ensure_indexes(business_role_collection)
        yield {
            "database": database,
            "lifecycle": collection,
            "principal": principal_collection,
            "membership": membership_collection,
            "roles": role_collection,
            "business_roles": business_role_collection,
        }
    finally:
        if database is not None:
            try:
                client.drop_database(database.name)
            except PyMongoError:
                pass
        client.close()


def _instruction(tenant_id: str) -> LegalInstruction:
    return LegalInstruction(
        tenant_id=tenant_id,
        instruction_id="instruction-1",
        case_matter_id="matter-1",
        document_id="document-1",
        registered_at=NOW,
        evidence_reference="registration-evidence",
    )


def _identity(tenant_id: str) -> SovereignIdentity:
    identity = SovereignIdentity(
        identity_id="principal-1",
        tenant_id=tenant_id,
        username="operator",
        email="operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    return identity


class _PrincipalReader:
    """Trace durable principal resolution while delegating to the canonical repository."""

    def __init__(self, collection: Any, calls: list[str]) -> None:
        self._collection = collection
        self._calls = calls

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        self._calls.append("principal")
        from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository

        return PrincipalAuthorityRepository.get(principal_id, self._collection, session=session)


class _MembershipReader:
    """Trace durable membership resolution while delegating to the canonical repository."""

    def __init__(self, collection: Any, calls: list[str]) -> None:
        self._collection = collection
        self._calls = calls

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        self._calls.append("membership")
        from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository

        return TenantMembershipRepository.resolve(principal_id, tenant_id, self._collection, session=session)


class _RoleReader:
    """Trace the canonical split business-role and authorization-role stores."""

    def __init__(
        self,
        authorization_collection: Any,
        business_collection: Any,
        calls: list[str],
    ) -> None:
        self._authorization_collection = authorization_collection
        self._business_collection = business_collection
        self._calls = calls

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
            self._calls.append("business_role")
            try:
                value = TenantBusinessRoleRepository.resolve(
                    principal_id,
                    tenant_id,
                    self._business_collection,
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

        self._calls.append("authorization_role")
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self._authorization_collection,
            session=session,
        )


class _LifecycleReader:
    """Trace lifecycle repository access and preserve the real Mongo collection contract."""

    def __init__(self, collection: Any, calls: list[str]) -> None:
        self._collection = collection
        self._calls = calls

    def find_one(self, query: Any, **kwargs: Any) -> Any:
        """Delegate exact single-record reads while preserving caller options."""
        self._calls.append("lifecycle")
        return self._collection.find_one(query, **kwargs)

    def find(self, query: Any, **kwargs: Any) -> Any:
        """Delegate exact history reads while preserving caller session/options."""
        self._calls.append("lifecycle")
        return self._collection.find(query, **kwargs)


def _app(
    collections: dict[str, Any],
    tenant_id: str,
    calls: list[str],
) -> FastAPI:
    """Compose the real final authorization dependency with isolated durable providers."""
    import tools.eos.auth.authentication as authentication
    import tools.eos.auth.tenant_access as tenant_access
    import tools.eos.api.tenant_authorization_http as authorization_http

    app = FastAPI()
    register_error_handlers(app, debug=False)
    principal_reader = _PrincipalReader(collections["principal"], calls)
    membership_reader = _MembershipReader(collections["membership"], calls)
    role_reader = _RoleReader(
        collections["roles"],
        collections["business_roles"],
        calls,
    )
    app.dependency_overrides[authorization_http.get_current_identity] = lambda: _identity(tenant_id)
    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: principal_reader
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = lambda: membership_reader
    app.dependency_overrides[authorization_http.get_role_assignment_repository] = lambda: role_reader
    app.dependency_overrides[legal_router.get_lifecycle_collection] = lambda: _LifecycleReader(collections["lifecycle"], calls)
    assert legal_router._INSTRUCTION_READ not in app.dependency_overrides
    app.include_router(legal_router.router, prefix="/api")
    return app


def _persist_iam(collections: dict[str, Any], tenant_id: str, *, business_role: str = "tenant_legal_partner") -> None:
    """Persist active principal, membership, business role, and granting role evidence."""
    from tools.eos.auth.principal_authority import PrincipalAuthority
    from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
    from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
    from tools.eos.auth.tenant_business_role import (
        TenantBusinessRoleAuthority,
        TenantBusinessRoleStatus,
    )
    from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
    from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
    from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository

    PrincipalAuthorityRepository.create(
        PrincipalAuthority("principal-1", PrincipalStatus.ACTIVE, 0),
        collections["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority("principal-1", tenant_id, TenantMembershipStatus.ACTIVE, 0),
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
            "LEGAL_PARTNER",
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collections["roles"],
    )


def _prepare(
    collections: dict[str, Any],
    *,
    business_role: str = "tenant_legal_partner",
) -> tuple[str, LegalInstruction, list[str]]:
    """Persist one complete durable IAM model and one canonical lifecycle fact."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    _persist_iam(collections, tenant, business_role=business_role)
    value = _instruction(tenant)
    assert LegalOperationsLifecycleRegistry.create(value, collections["lifecycle"]) == value
    calls: list[str] = []
    return tenant, value, calls


def _request(collections: dict[str, Any], tenant: str, calls: list[str]) -> Any:
    """Issue the real route request with only authentication identity injected."""
    with TestClient(_app(collections, tenant, calls)) as client:
        return client.get(
            "/api/legal-operations/instructions/instruction-1",
            headers={"X-Tenant-ID": tenant},
        )


def test_real_mongo_live_iam_authorizes_and_precedes_lifecycle_read(mongo_context: dict[str, Any]) -> None:
    """Durable IAM truth authorizes the own-tenant P2 projection."""
    tenant, value, calls = _prepare(mongo_context)
    response = _request(mongo_context, tenant, calls)
    assert response.status_code == 200
    assert response.json()["data"] == value.to_dict()
    assert response.json()["history"] == [value.to_dict()]
    assert "principal" in calls
    assert "membership" in calls
    assert "business_role" in calls
    assert "authorization_role" in calls
    assert "lifecycle" in calls
    assert max(calls.index("principal"), calls.index("membership"), calls.index("business_role"), calls.index("authorization_role")) < calls.index("lifecycle")


def test_real_mongo_multiple_snapshots_resolve_current_and_forks_reject(
    mongo_context: dict[str, Any],
) -> None:
    """Complete durable history resolves one linear current state and rejects forks."""
    tenant, registered, calls = _prepare(mongo_context)
    accepted = registered.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted-evidence",
        occurred_at=NOW + timedelta(minutes=1),
    )
    assert (
        LegalOperationsLifecycleRegistry.create(
            accepted,
            mongo_context["lifecycle"],
        )
        == accepted
    )

    response = _request(mongo_context, tenant, calls)
    assert response.status_code == 200
    assert response.json()["data"] == accepted.to_dict()
    history = response.json()["history"]
    assert len(history) == 2
    assert registered.to_dict() in history
    assert accepted.to_dict() in history

    cancelled = registered.transition_to(
        LegalInstructionState.CANCELLED,
        evidence_reference="cancelled-evidence",
        occurred_at=NOW + timedelta(minutes=1),
    )
    assert (
        LegalOperationsLifecycleRegistry.create(
            cancelled,
            mongo_context["lifecycle"],
        )
        == cancelled
    )

    divergent = _request(mongo_context, tenant, calls)
    assert divergent.status_code == 503
    assert divergent.json()["detail"] == "LEGAL_OPERATIONS_EVIDENCE_UNAVAILABLE"


def test_real_mongo_revoked_grant_denies_before_lifecycle(mongo_context: dict[str, Any]) -> None:
    """Revoking the durable granting role cannot be bypassed by injected claims."""
    from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
    from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository

    tenant, _, calls = _prepare(mongo_context)
    RoleAssignmentRepository.compare_and_swap(
        RoleAssignmentAuthority("principal-1", tenant, "LEGAL_PARTNER", RoleAssignmentStatus.REVOKED, 1),
        0,
        mongo_context["roles"],
    )
    response = _request(mongo_context, tenant, calls)
    assert response.status_code == 403
    assert "lifecycle" not in calls


def test_real_mongo_inactive_principal_denies_before_lifecycle(mongo_context: dict[str, Any]) -> None:
    """Durable principal inactivity dominates any projected identity status."""
    from tools.eos.auth.principal_authority import PrincipalAuthority
    from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
    from tools.eos.auth.principal_status import PrincipalStatus

    tenant, _, calls = _prepare(mongo_context)
    PrincipalAuthorityRepository.compare_and_swap(
        PrincipalAuthority("principal-1", PrincipalStatus.SUSPENDED, 1),
        0,
        mongo_context["principal"],
    )
    response = _request(mongo_context, tenant, calls)
    assert response.status_code == 403
    assert "lifecycle" not in calls


def test_real_mongo_inactive_membership_denies_before_lifecycle(mongo_context: dict[str, Any]) -> None:
    """Durable membership inactivity denies the selected tenant scope."""
    from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
    from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository

    tenant, _, calls = _prepare(mongo_context)
    TenantMembershipRepository.compare_and_swap(
        TenantMembershipAuthority("principal-1", tenant, TenantMembershipStatus.SUSPENDED, 1),
        0,
        mongo_context["membership"],
    )
    response = _request(mongo_context, tenant, calls)
    assert response.status_code == 403
    assert "lifecycle" not in calls


def test_real_mongo_ineligible_business_role_denies_before_lifecycle(mongo_context: dict[str, Any]) -> None:
    """A durable but ineligible Legal Operations business role cannot authorize reads."""
    tenant, _, calls = _prepare(mongo_context, business_role="tenant_legal_client")
    response = _request(mongo_context, tenant, calls)
    assert response.status_code == 403
    assert "lifecycle" not in calls


def test_real_mongo_cross_tenant_denies_without_foreign_repository_access(mongo_context: dict[str, Any]) -> None:
    """A foreign X-Tenant-ID is denied before any lifecycle lookup."""
    tenant, _, calls = _prepare(mongo_context)
    foreign = f"tenant-{uuid.uuid4().hex}"
    response = _request(mongo_context, foreign, calls)
    assert tenant != foreign
    assert response.status_code == 403
    assert "lifecycle" not in calls


def test_real_mongo_client_role_is_denied_until_projection_policy_exists(mongo_context: dict[str, Any]) -> None:
    """Client business-role evidence cannot reach internal lifecycle projections."""
    tenant, _, calls = _prepare(mongo_context, business_role="tenant_legal_client")
    response = _request(mongo_context, tenant, calls)
    assert response.status_code == 403
    assert "lifecycle" not in calls


def test_real_mongo_unknown_resource_and_projection_boundary_remain_bounded(mongo_context: dict[str, Any]) -> None:
    """Unknown resources remain bounded and successful projections exclude internals."""
    tenant, value, calls = _prepare(mongo_context)
    with TestClient(_app(mongo_context, tenant, calls)) as client:
        missing = client.get(
            "/api/legal-operations/instructions/missing",
            headers={"X-Tenant-ID": tenant},
        )
        own = client.get(
            "/api/legal-operations/instructions/instruction-1",
            headers={"X-Tenant-ID": tenant},
        )
    assert missing.status_code == 404
    assert "stack_trace" not in missing.text
    assert own.status_code == 200
    payload = own.json()["data"]
    history = own.json()["history"]
    assert payload == value.to_dict()
    assert history == [value.to_dict()]
    assert "_id" not in payload
    assert all(
        forbidden not in snapshot
        for snapshot in (payload, *history)
        for forbidden in ("_id", "p1_payload", "source_payload")
    )
    assert not any(token in key.casefold() for key in payload for token in ("payment", "settlement", "invoice", "billing_execution"))
    assert legal_router.VERSION == "v1.2.0-L8-5-LEGAL-OPERATIONS-CURRENT-HISTORY-READ-API"


# ARTIFACT: test_legal_operations_http_real_mongo.py
# VERSION: v1.3.0-L8-5-LIVE-IAM-CURRENT-HISTORY-READ-API-RM-CERT
# AUTHORITY BOUNDARY: real-Mongo live-IAM deterministic current-plus-history projection certificate only
# TENANT POSTURE: exact tenant predicates, durable membership, and foreign absence
# FAIL-CLOSED POSTURE: post-hello failures, read-model divergence, and projection leakage fail certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT