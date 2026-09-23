"""Live-IAM real-Mongo certificate for deputy personal active-work reads.

TITLE: WILSY OS Deputy Personal Active Work Live-IAM Real-Mongo Certificate
VERSION: v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-LIVE-IAM-RM-CERT
AUTHORITY: Host-backed certification of DEPUTY IAM + L8-6B binding + L8-6C read.
EPITOME: Prove durable ACTIVE deputy IAM authorizes the personal-work route,
         immutable principal-to-Deputy binding determines exact deputy identity,
         real lifecycle history yields only that deputy's ALLOCATED/ATTEMPTED
         current attempts, terminal/other-deputy work is excluded, SHERIFF is
         denied, and missing binding never falls back to tenant-wide queues.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_deputy_personal_active_work_http_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for L8-6C composition only. IAM,
                            L8-6B, P1/P2/L8-0/L8-5 retain canonical authority.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-LIVE-IAM-RM-CERT
           establishes durable deputy allow, sheriff denial, exact bound-deputy
           filtering, current-state supersession, missing-binding denial,
           foreign work exclusion, and bounded non-financial response proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic principals/deputies/attempts.
TENANT BOUNDARY: IAM, binding and lifecycle evidence all use one exact tenant.
AUTHORITY BOUNDARY: Host read certificate only; no lifecycle mutation/service.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Setup uses durable writes; product read route owns no tx.
FAIL-CLOSED DECLARATION: Runtime/IAM/binding/evidence/scope failure denies
                         without sheriff queue or invented personal work.
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
import tools.eos.api.tenant_authorization_http as authorization_http
import tools.eos.auth.authentication as authentication
import tools.eos.auth.tenant_access as tenant_access
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.deputy_principal_binding import (
    DeputyPrincipalBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    COLLECTION as BINDING_COLLECTION,
    DeputyPrincipalBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-LIVE-IAM-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 20, 0, tzinfo=timezone.utc)


class _PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self.collection,
            session=session,
        )


class _MembershipReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


class _RoleReader:
    """Resolve business roles and final authorization roles from split stores."""

    def __init__(self, role_collection: Any, business_collection: Any) -> None:
        self.role_collection = role_collection
        self.business_collection = business_collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> Any:
        if role_id in TENANT_ROLES:
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
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self.role_collection,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
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
                f"L8_6C_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(f"L8_6C_REPLICA_SET_MISMATCH:{hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_6C_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client.get_database(
            f"l8_6c_personal_work_{uuid.uuid4().hex}",
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collections = {
            "lifecycle": database.get_collection(LIFECYCLE_COLLECTION),
            "binding": database.get_collection(BINDING_COLLECTION),
            "principal": database.get_collection("principal_authorities"),
            "membership": database.get_collection("tenant_memberships"),
            "business": database.get_collection("tenant_business_roles"),
            "role": database.get_collection("role_assignments"),
        }
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        DeputyPrincipalBindingRegistry.ensure_indexes(collections["binding"])
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        RoleAssignmentRepository.ensure_indexes(collections["role"])
        yield {"client": client, "database": database, "collections": collections}
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


def _seed_iam(
    collections: dict[str, Any],
    *,
    principal_id: str,
    tenant_id: str,
    business_role: str,
    authorization_role: str,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
        collections["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collections["membership"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal_id,
            tenant_id,
            business_role,
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        collections["business"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal_id,
            tenant_id,
            authorization_role,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collections["role"],
    )


def _deputy(
    collections: dict[str, Any],
    *,
    tenant_id: str,
    deputy_id: str,
) -> Deputy:
    value = Deputy(
        tenant_id=tenant_id,
        deputy_id=deputy_id,
        sheriff_office_id="office-1",
        display_name=f"Deputy {deputy_id}",
        badge_reference=f"badge-{deputy_id}",
        evidence_reference=f"directory-{deputy_id}",
    )
    LegalOperationsLifecycleRegistry.create(value, collections["lifecycle"])
    return value


def _bind(
    collections: dict[str, Any],
    *,
    tenant_id: str,
    principal_id: str,
    deputy: Deputy,
) -> None:
    value = DeputyPrincipalBinding.from_deputy(
        principal_id=principal_id,
        deputy=deputy,
        bound_at=NOW,
        evidence_reference="binding-evidence",
    )
    DeputyPrincipalBindingRegistry.create(value, collections["binding"])


def _persist_attempt_chain(
    collections: dict[str, Any],
    *,
    tenant_id: str,
    attempt_id: str,
    deputy_id: str,
    terminal: ServiceAttemptState | None = None,
    attempted: bool = False,
) -> None:
    allocated = ServiceAttempt(
        tenant_id=tenant_id,
        attempt_id=attempt_id,
        instruction_id=f"instruction-{attempt_id}",
        document_id=f"document-{attempt_id}",
        deputy_id=deputy_id,
        allocated_at=NOW,
        allocation_evidence_reference=f"allocation-{attempt_id}",
    )
    LegalOperationsLifecycleRegistry.create(allocated, collections["lifecycle"])
    if terminal is ServiceAttemptState.CANCELLED:
        cancelled = allocated.transition_to(
            ServiceAttemptState.CANCELLED,
            evidence_reference=f"cancelled-{attempt_id}",
            occurred_at=NOW + timedelta(minutes=1),
        )
        LegalOperationsLifecycleRegistry.create(cancelled, collections["lifecycle"])
        return
    if attempted or terminal is not None:
        attempted_value = allocated.transition_to(
            ServiceAttemptState.ATTEMPTED,
            evidence_reference=f"attempted-{attempt_id}",
            occurred_at=NOW + timedelta(minutes=1),
        )
        LegalOperationsLifecycleRegistry.create(
            attempted_value,
            collections["lifecycle"],
        )
        if terminal is not None:
            terminal_value = attempted_value.transition_to(
                terminal,
                evidence_reference=f"terminal-{attempt_id}",
                evidence_fingerprint="a" * 128,
                occurred_at=NOW + timedelta(minutes=2),
            )
            LegalOperationsLifecycleRegistry.create(
                terminal_value,
                collections["lifecycle"],
            )


def _identity(principal_id: str, tenant_id: str) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username=principal_id,
        email=f"{principal_id}@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _app(
    context: dict[str, Any],
    *,
    principal_id: str,
    tenant_id: str,
) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    collections = context["collections"]
    app.dependency_overrides[authorization_http.get_current_identity] = (
        lambda: _identity(principal_id, tenant_id)
    )
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalReader(collections["principal"])
    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: _MembershipReader(collections["membership"])
    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: _RoleReader(
        collections["role"],
        collections["business"],
    )
    app.dependency_overrides[legal_router.get_lifecycle_collection] = (
        lambda: collections["lifecycle"]
    )
    app.dependency_overrides[
        legal_router.get_deputy_principal_binding_collection
    ] = lambda: collections["binding"]
    assert legal_router._DEPUTY_QUEUE_READ not in app.dependency_overrides
    app.include_router(legal_router.router, prefix="/api")
    return app


def _get(
    context: dict[str, Any],
    *,
    principal_id: str,
    tenant_id: str,
) -> Any:
    with TestClient(
        _app(context, principal_id=principal_id, tenant_id=tenant_id)
    ) as client:
        return client.get(
            "/api/legal-operations/deputy/active-work",
            headers={"X-Tenant-ID": tenant_id},
        )


def test_real_deputy_gets_only_bound_active_work_with_current_supersession(
    mongo_context: dict[str, Any],
) -> None:
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"
    other_deputy = f"deputy-{uuid.uuid4().hex}"

    _seed_iam(
        collections,
        principal_id=principal,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )
    deputy = _deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _deputy(collections, tenant_id=tenant, deputy_id=other_deputy)
    _bind(
        collections,
        tenant_id=tenant,
        principal_id=principal,
        deputy=deputy,
    )

    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-allocated",
        deputy_id=deputy_id,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-attempted",
        deputy_id=deputy_id,
        attempted=True,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-completed",
        deputy_id=deputy_id,
        terminal=ServiceAttemptState.COMPLETED,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-other",
        deputy_id=other_deputy,
    )

    response = _get(
        mongo_context,
        principal_id=principal,
        tenant_id=tenant,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == tenant
    assert body["visibility"] == "DEPUTY_PERSONAL_ACTIVE_WORK"
    assert body["deputy_id"] == deputy_id
    assert [
        item["attempt_id"] for item in body["active_attempts"]
    ] == ["attempt-allocated", "attempt-attempted"]
    assert all(item["deputy_id"] == deputy_id for item in body["active_attempts"])
    assert "attempt-completed" not in str(body)
    assert "attempt-other" not in str(body)


def test_real_sheriff_is_denied_deputy_personal_route(
    mongo_context: dict[str, Any],
) -> None:
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff = f"sheriff-{uuid.uuid4().hex}"
    _seed_iam(
        collections,
        principal_id=sheriff,
        tenant_id=tenant,
        business_role="tenant_sheriff",
        authorization_role="SHERIFF",
    )

    response = _get(
        mongo_context,
        principal_id=sheriff,
        tenant_id=tenant,
    )

    assert response.status_code == 403
    assert collections["binding"].count_documents({}) == 0


def test_real_authorized_deputy_without_binding_is_denied_without_fallback(
    mongo_context: dict[str, Any],
) -> None:
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"
    _seed_iam(
        collections,
        principal_id=principal,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )
    _deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-unbound",
        deputy_id=deputy_id,
    )

    response = _get(
        mongo_context,
        principal_id=principal,
        tenant_id=tenant,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "DEPUTY_IDENTITY_BINDING_REQUIRED"
    assert "attempt-unbound" not in response.text


def test_real_response_excludes_sheriff_invented_and_financial_truth(
    mongo_context: dict[str, Any],
) -> None:
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"
    _seed_iam(
        collections,
        principal_id=principal,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )
    deputy = _deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _bind(
        collections,
        tenant_id=tenant,
        principal_id=principal,
        deputy=deputy,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-1",
        deputy_id=deputy_id,
    )

    response = _get(
        mongo_context,
        principal_id=principal,
        tenant_id=tenant,
    )
    assert response.status_code == 200
    serialized = str(response.json()).casefold()
    for forbidden in (
        "office_receipt",
        "deputy_assignment",
        "principal_id",
        "urgent",
        "distance",
        "gps",
        "billing",
        "invoice",
        "payment",
        "settlement",
        "revenue",
        "ai_score",
        "client_name",
    ):
        assert forbidden not in serialized

    assert legal_router.VERSION == (
        "v1.4.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-READ-API"
    )
    assert VERSION == (
        "v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-LIVE-IAM-RM-CERT"
    )


# ARTIFACT: test_deputy_personal_active_work_http_real_mongo.py
# VERSION: v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-LIVE-IAM-RM-CERT
# AUTHORITY BOUNDARY: live-IAM real-Mongo bound-deputy personal-work read certificate only
# TENANT POSTURE: exact authorized tenant + immutable principal-to-Deputy binding
# FAIL-CLOSED POSTURE: sheriff/missing-binding/evidence/scope failures deny without fallback
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
