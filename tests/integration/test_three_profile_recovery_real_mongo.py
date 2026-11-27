"""TITLE: WILSY OS Three-Profile Recovery Real-Mongo Certificate.
VERSION: v1.0.0-THREE-PROFILE-RECOVERY-CERT
AUTHORITY: Disposable development replica-set certification only.
EPITOME: Reproduce legacy Owner read ambiguity and prove explicitly selected
Owner, HR Director and HR Manager retain independent durable authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_three_profile_recovery_real_mongo.py
COLLABORATION / OWNERSHIP: Global Principal sessions, canonical tenant IAM,
company document HTTP boundary and source-owned document lifecycle.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.0.0-THREE-PROFILE-RECOVERY-CERT certifies selected capacity,
refresh/currentness, HTTP required reads versus optional grants, cross-tenant
denial and immutable publication preservation using existing repositories.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities and isolated UUID database;
no canonical Atlas access, real credentials, personal data or IAM mutation.
TENANT BOUNDARY: Canonical-company-shaped synthetic scope in disposable data.
AUTHORITY BOUNDARY: HTTP identity and credential/MFA issuance preconditions are
fixture-owned; real authentication/MFA is covered by the companion suites.
TRANSACTION BOUNDARY: Fixture owns transactions and cleanup. Production
repositories own persistence semantics; test adapters only inject collections.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient

from tools.eos.api import company_operating_document_router as documents
from tools.eos.api import tenant_authorization_http as boundary
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth import global_principal_session_authority as session_module
from tools.eos.auth.global_principal_session_authority import (
    GlobalPrincipalSessionAuthority, GlobalPrincipalSessionRejected,
)
from tools.eos.auth.membership_selection_challenge import SelectedMembershipContext
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization import authorize_tenant_operation
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID as TENANT
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.company_operating_document_registry import CompanyOperatingDocumentRegistry
from tools.eos.saas.domain.company_operating_document import CompanyDocumentClass

VERSION = "v1.0.0-THREE-PROFILE-RECOVERY-CERT"
PRINCIPAL = "three-profile-synthetic-principal"
ROLES = ("tenant_owner", "tenant_hr_director", "tenant_hr_manager")


def _snapshot(database):
    """Fingerprint source-owned IAM and documents, excluding generated BSON IDs."""
    names = ("principal_authorities", "tenant_memberships", "role_assignments",
             "tenant_business_roles", "tenant_business_role_assignments",
             "tenant_business_role_assignment_history",
             "company_operating_document_revisions", "company_operating_document_commands")
    rows = {name: sorted((json.dumps({k: v for k, v in row.items() if k != "_id"},
                                    sort_keys=True, default=str)
                          for row in database[name].find({}))) for name in names}
    return hashlib.sha3_512(json.dumps(rows, sort_keys=True).encode()).hexdigest()


@pytest.fixture
def recovery(monkeypatch):
    """Bind existing authorities to a private database on the certified replica."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.fail("TEST_VENDOR_MONGO_URI must explicitly select disposable Mongo")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    database = client["wilsy_three_profile_cert_" + uuid4().hex]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == "wilsyVendorCertRS"
        assert hello.get("isWritablePrimary") is True
        monkeypatch.setattr(kernel_db, "get_database", lambda: database)
        monkeypatch.setattr(kernel_db, "get_client", lambda: client)
        PrincipalAuthorityRepository.ensure_indexes()
        TenantMembershipRepository.ensure_indexes()
        RoleAssignmentRepository.ensure_indexes()
        TenantBusinessRoleRepository.ensure_indexes()
        TenantBusinessRoleRepository.ensure_multi_capacity_indexes(database)
        PrincipalAuthorityRepository.create(PrincipalAuthority(PRINCIPAL, PrincipalStatus.ACTIVE, 0))
        TenantMembershipRepository.insert(TenantMembershipAuthority(PRINCIPAL, TENANT, TenantMembershipStatus.ACTIVE, 0))
        stamp = datetime.now(timezone.utc) - timedelta(minutes=1)
        TenantBusinessRoleRepository.insert(TenantBusinessRoleAuthority(
            PRINCIPAL, TENANT, "tenant_owner", TenantBusinessRoleStatus.ACTIVE, 0, stamp, None))
        for role in ("ENTERPRISE_ADMIN", "TENANT_OWNER", "HR_DIRECTOR", "HR_MANAGER"):
            RoleAssignmentRepository.insert(RoleAssignmentAuthority(PRINCIPAL, TENANT, role, RoleAssignmentStatus.ACTIVE, 0))
        reader = boundary.get_role_assignment_repository()
        session_authority = GlobalPrincipalSessionAuthority(
            sessions=database[session_module.SESSION_COLLECTION],
            refresh_tokens=database[session_module.REFRESH_COLLECTION],
            credential_repository=SimpleNamespace(get_by_principal=lambda pid, **_: SimpleNamespace(
                principal_id=pid, credential_revision=0, mfa_enabled=True)),
            tenant_resolver=lambda tenant_id, **_: SimpleNamespace(tenant_id=tenant_id),
        )
        GlobalPrincipalSessionAuthority.ensure_indexes(
            database[session_module.SESSION_COLLECTION], database[session_module.REFRESH_COLLECTION])
        monkeypatch.setattr(session_module, "create_access_token", lambda *_, **__: "synthetic-access")
        yield SimpleNamespace(client=client, database=database, reader=reader,
                              sessions=session_authority, stamp=stamp)
    finally:
        client.drop_database(database.name)
        client.close()


def _add_hr(state):
    """Append independent HR capacities through the existing caller transaction."""
    with state.client.start_session() as session:
        with session.start_transaction():
            for role in ROLES[1:]:
                TenantBusinessRoleRepository.record_capacity_revision(
                    TenantBusinessRoleAuthority(PRINCIPAL, TENANT, role,
                        TenantBusinessRoleStatus.ACTIVE, 0, state.stamp, None),
                    None, state.database, session=session)


def _decision(state, role, suffix="read", tenant=TENANT, **pair):
    """Evaluate canonical IAM only, without caller-owned permission inference."""
    return authorize_tenant_operation(
        principal_id=PRINCIPAL, tenant_id=tenant,
        permission_id=pair.get("permission", "company_operating_document:" + suffix),
        operation=pair.get("operation", "company_operating_document_" + suffix),
        principal_repository=PrincipalAuthorityRepository(),
        membership_repository=TenantMembershipRepository(),
        business_role_repository=state.reader, role_assignment_repository=state.reader,
        selected_business_role=role)


def test_owner_read_regression_is_selected_capacity_ambiguity_not_a_missing_grant(recovery):
    """Original Owner succeeds; added HR capacities require explicit selection."""
    assert _decision(recovery, None).authorized
    _add_hr(recovery)
    before = _snapshot(recovery.database)
    assert _decision(recovery, None).reason.value == "MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES"
    selected = _decision(recovery, "tenant_owner")
    assert selected.authorized and selected.authorization_role == "ENTERPRISE_ADMIN"
    for role in ROLES:
        assert _decision(recovery, role).authorized
    for suffix in ("author", "publish"):
        assert _decision(recovery, "tenant_owner", suffix).reason.value == "PERMISSION_NOT_GRANTED"
        for role in ROLES[1:]:
            assert _decision(recovery, role, suffix).reason.value == "BUSINESS_ROLE_INELIGIBLE"
    assert _decision(recovery, "tenant_owner", tenant="foreign-tenant").authorized is False
    assert _decision(recovery, "malformed-capacity").authorized is False
    assert _decision(recovery, "tenant_hr_director", permission="platform_employer:headcount_requisition:decide",
                     operation="platform_employer_headcount_requisition_decide").authorized
    assert _decision(recovery, "tenant_hr_manager", permission="platform_employer:headcount_requisition:decide",
                     operation="platform_employer_headcount_requisition_decide").reason.value == "BUSINESS_ROLE_INELIGIBLE"
    assert _decision(recovery, "tenant_hr_director", permission="subscription:manage",
                     operation="subscription_create").reason.value == "BUSINESS_ROLE_INELIGIBLE"
    assert before == _snapshot(recovery.database)


@pytest.mark.parametrize("role", ROLES)
def test_selected_capacity_refresh_and_revocation_remain_exact(recovery, role):
    """Real persisted session rotation preserves role/tenant and rejects replay."""
    _add_hr(recovery)
    workspace = "WILSY_HEADQUARTERS" if role == "tenant_owner" else "PEOPLE_OPERATIONS"
    selected = SelectedMembershipContext(PRINCIPAL, TENANT, role, workspace, 0, 0, 0)
    before = _snapshot(recovery.database)
    with recovery.client.start_session() as session:
        with session.start_transaction():
            receipt = recovery.sessions.issue_after_mfa(selected, session=session)
    assert recovery.sessions.is_session_current(principal_id=PRINCIPAL, tenant_id=TENANT,
        session_reference=receipt.session_reference, expected_business_role=role)
    assert not recovery.sessions.is_session_current(principal_id=PRINCIPAL, tenant_id="foreign-tenant",
        session_reference=receipt.session_reference)
    with recovery.client.start_session() as session:
        with session.start_transaction():
            rotated = recovery.sessions.rotate_refresh_token(receipt.refresh_token, session=session)
    assert (rotated.business_role, rotated.tenant_id, rotated.workspace_id) == (role, TENANT, workspace)
    with recovery.client.start_session() as session:
        with pytest.raises(GlobalPrincipalSessionRejected):
            with session.start_transaction():
                recovery.sessions.rotate_refresh_token(receipt.refresh_token, session=session)
    recovery.database[session_module.SESSION_COLLECTION].update_one(
        {"session_reference": receipt.session_reference, "tenant_id": TENANT, "principal_id": PRINCIPAL},
        {"$set": {"revoked_at": datetime.now(timezone.utc)}})
    assert not recovery.sessions.is_session_current(principal_id=PRINCIPAL, tenant_id=TENANT,
        session_reference=receipt.session_reference)
    assert before == _snapshot(recovery.database)


@pytest.mark.parametrize("role", ROLES[1:])
def test_hr_cannot_use_founder_commands_through_concurrent_owner_assignment(recovery, role):
    """Actual HTTP IAM admits read but selected HR cannot execute Founder lifecycle."""
    _add_hr(recovery)
    registry = CompanyOperatingDocumentRegistry(recovery.database)
    registry.provision_indexes()
    before = _snapshot(recovery.database)
    identity = SimpleNamespace(identity_id=PRINCIPAL, tenant_id=TENANT,
                               principal_scope="GLOBAL", roles=(role,))
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(documents.router, prefix="/api")
    app.dependency_overrides[documents.get_current_identity] = lambda: identity
    app.dependency_overrides[documents._require_current_company_session] = lambda: None
    client = TestClient(app)
    for suffix, payload in (
        ("founder-drafts", {"title": "Denied HR draft", "document_version": "1.0.0",
            "expected_revision": 0, "sections": [{"section_id": "pillar-one", "title": "Denied", "body": "Must never persist."}]}),
        ("founder-submit", {"expected_revision": 1}),
        ("founder-ratify", {"expected_revision": 2, "effective_from": recovery.stamp.isoformat()}),
    ):
        response = client.post("/api/company-operating-documents/STRATEGY/" + suffix,
            json=payload, headers={"X-Tenant-ID": TENANT, "Idempotency-Key": "hr-denied"})
        assert response.status_code == 403
        assert response.json()["detail"]["error"] == "COMPANY_DOCUMENT_FOUNDER_OWNER_CAPACITY_REQUIRED"
    assert before == _snapshot(recovery.database)


@pytest.mark.parametrize("classification", list(CompanyDocumentClass))
def test_required_published_document_http_read_is_independent_of_optional_roles(recovery, classification):
    """Read original publication through actual IAM without author/publisher grants."""
    registry = CompanyOperatingDocumentRegistry(recovery.database)
    registry.provision_indexes()
    with recovery.client.start_session() as session:
        with session.start_transaction():
            for action, revision, actor, payload in (
                ("CREATE_DRAFT", 0, "synthetic-author", {"title": "Synthetic publication",
                    "document_version": "1.0.0", "sections": [{"section_id": "pillar-1",
                    "title": "Synthetic section", "body": "Disposable certificate content only."}]}),
                ("SUBMIT", 1, "synthetic-author", {}),
                ("PUBLISH", 2, "independent-publisher", {"approval_reference": "synthetic-approval",
                    "effective_from": recovery.stamp.isoformat()}),
            ):
                publication = registry.command(TENANT, classification, actor_id=actor,
                    action=action, payload=payload, expected_revision=revision,
                    idempotency_key=classification.value + action, now=recovery.stamp, session=session)
    _add_hr(recovery)
    before = _snapshot(recovery.database)
    identity = SimpleNamespace(identity_id=PRINCIPAL, tenant_id=TENANT,
                               principal_scope="TENANT", roles=())
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(documents.router, prefix="/api")
    app.dependency_overrides[documents.get_current_identity] = lambda: identity
    # This certificate starts after authentication; companion authentication
    # suites certify bearer/MFA/currentness instead of inventing browser tokens.
    app.dependency_overrides[documents._require_current_company_session] = lambda: None
    client = TestClient(app)
    path = "/api/company-operating-documents/" + classification.value
    assert client.get(path, headers={"X-Tenant-ID": TENANT}).status_code == 403
    identity.principal_scope = "GLOBAL"
    identity.roles = ("tenant_owner",)
    response = client.get(path, headers={"X-Tenant-ID": TENANT})
    assert response.status_code == 200
    assert response.json()["document"]["fingerprint"] == publication.fingerprint
    assert response.headers["cache-control"] == "no-store"
    assert client.get(path, headers={"X-Tenant-ID": "foreign-tenant"}).status_code == 403
    assert before == _snapshot(recovery.database)

# ARTIFACT: tests/integration/test_three_profile_recovery_real_mongo.py
# VERSION: v1.0.0-THREE-PROFILE-RECOVERY-CERT
# AUTHORITY BOUNDARY: Disposable integration evidence; no live MFA or IAM authority.
# TENANT POSTURE: Exact synthetic principal and tenant in an isolated UUID database.
# FAIL-CLOSED POSTURE: Ambiguous, foreign, malformed, revoked and replayed evidence deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
