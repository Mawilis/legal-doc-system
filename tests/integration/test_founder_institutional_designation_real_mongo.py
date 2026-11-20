"""TITLE: WILSY Founder Designation Real Mongo Certification
VERSION: v1.0.0-FOUNDER-DESIGNATION-REPLAY-ISOLATION-CERT
AUTHORITY: Exact synthetic active principal, membership, capacity and IAM.
EPITOME: Certify non-IAM Founder title issuance, readback, replay, owner MFA
  denial, wrong-principal isolation and no IAM/commercial mutation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_founder_institutional_designation_real_mongo.py
COLLABORATION / OWNERSHIP: Founder institutional designation source and
  canonical identity/role repositories; disposable Global Principal Mongo.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.0.0-FOUNDER-DESIGNATION-REPLAY-ISOLATION-CERT initial durable
  test of current authorization, title/audit, replay and negative proof.
COMPLIANCE: POPIA s19; GDPR Article32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic credentials, UUID database, no live keys.
TENANT BOUNDARY: Test-only tenant value patch, no live Founder mutation.
AUTHORITY BOUNDARY: Non-IAM designation never creates roles or memberships.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: Missing MFA or unmatched identity yields no title.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
import uuid
from types import SimpleNamespace
from typing import Any

from bson import ObjectId
from pymongo import MongoClient
import pytest

from tools.eos.auth import founder_institutional_designation as subject
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository


class DatabaseFacade:
    name = "wilsy"
    def __init__(self, db: Any):
        self.db = db
    def __getitem__(self, key: str) -> Any:
        return self.db[key]


class FakeOwnerAuth:
    def __init__(self, principal: str, tenant: str):
        self.principal = principal
        self.tenant = tenant
    def authenticate(self, email: str, password: str) -> Any:
        if password != "known-owner-password":
            return None
        return SimpleNamespace(
            id=self.principal, tenantId=self.tenant, mfaRegistered=True,
        )
    def verify_otp(self, principal_id: str, code: str) -> bool:
        return principal_id == self.principal and code == "123456"


@pytest.fixture()
def live_replica(monkeypatch: pytest.MonkeyPatch):
    uri = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI")
    if not uri:
        pytest.fail("TEST_GLOBAL_PRINCIPAL_MONGO_URI_REQUIRED")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    if hello.get("setName") != "wilsyGlobalPrincipalCertRS":
        pytest.fail("WRONG_GLOBAL_PRINCIPAL_TEST_REPLICA")
    database = client["founder_designation_cert_" + uuid.uuid4().hex]
    tenant = "synthetic-tenant-" + uuid.uuid4().hex
    email = "founder-cert@example.com"
    oid = ObjectId()
    principal = str(oid)
    database["users"].insert_one({
        "_id": oid, "tenantId": tenant, "email": email,
    })
    PrincipalAuthorityRepository.insert(
        PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0),
        database["principal_authorities"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(principal, tenant, TenantMembershipStatus.ACTIVE, 0),
        database["tenant_memberships"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal, tenant, "tenant_owner",
            TenantBusinessRoleStatus.ACTIVE, 0, datetime.now(timezone.utc), None,
        ), database["tenant_business_roles"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal, tenant, "ENTERPRISE_ADMIN", RoleAssignmentStatus.ACTIVE, 0,
        ), database["role_assignments"],
    )
    database["principal_credentials"].insert_one({
        "principal_id": principal, "normalized_email": email,
        "password_hash": "$2b$12$" + "a" * 53,
        "credential_revision": 0, "mfa_enabled": True,
    })
    database["global_principal_mfa_factors"].insert_one({
        "principal_id": principal, "status": "ACTIVE",
    })
    monkeypatch.setattr(subject, "TENANT", tenant)
    monkeypatch.setattr(subject, "EMAIL", email)
    monkeypatch.setattr(subject.kernel_db, "get_client", lambda: client)
    monkeypatch.setattr(subject.kernel_db, "get_database",
                        lambda: DatabaseFacade(database))
    monkeypatch.setattr(subject, "get_auth_registry",
                        lambda value: FakeOwnerAuth(principal, tenant))
    try:
        yield database, principal, tenant
    finally:
        client.drop_database(database.name)
        client.close()


def test_founder_title_is_persisted_source_checked_and_replay_safe(live_replica):
    db, principal, tenant = live_replica
    assert subject.read_founder_designation(
        principal_id=principal, tenant_id=tenant, database=db,
    ) is None
    result = subject.issue_founder_designation(
        password="known-owner-password", otp_code="123456",
    )
    assert result == {"designation": "Founder", "status": "ACTIVE"}
    display = subject.read_founder_designation(
        principal_id=principal, tenant_id=tenant, database=db,
    )
    assert display == {
        "title": "Founder", "state": "ACTIVE",
        "authority": "INSTITUTIONAL_DESIGNATION",
        "operating_capacity": "tenant_owner",
    }
    assert subject.issue_founder_designation(
        password="known-owner-password", otp_code="123456",
    )["status"] == "ALREADY_ACTIVE"
    assert db[subject.COLLECTION].count_documents({}) == 1
    assert db[subject.AUDIT].count_documents({}) == 1
    assert db["role_assignments"].count_documents({}) == 1
    assert db["tenant_memberships"].count_documents({}) == 1
    assert db["tenant_business_roles"].count_documents({}) == 1
    assert db["subscriptions"].count_documents({}) == 0


def test_wrong_owner_factor_never_creates_founder_title(live_replica):
    db, principal, tenant = live_replica
    with pytest.raises(subject.FounderDesignationRejected,
                       match="FOUNDER_OWNER_PASSWORD_PROOF_DENIED"):
        subject.issue_founder_designation(
            password="wrong-password", otp_code="123456",
        )
    with pytest.raises(subject.FounderDesignationRejected,
                       match="FOUNDER_OWNER_MFA_PROOF_DENIED"):
        subject.issue_founder_designation(
            password="known-owner-password", otp_code="000000",
        )
    assert db[subject.COLLECTION].count_documents({}) == 0
    assert db[subject.AUDIT].count_documents({}) == 0


def test_other_principal_and_tenant_never_inherit_founder_title(live_replica):
    db, principal, tenant = live_replica
    subject.issue_founder_designation(
        password="known-owner-password", otp_code="123456",
    )
    assert subject.read_founder_designation(
        principal_id="other-principal", tenant_id=tenant, database=db,
    ) is None
    assert subject.read_founder_designation(
        principal_id=principal, tenant_id="other-tenant", database=db,
    ) is None


# ARTIFACT: test_founder_institutional_designation_real_mongo.py
# VERSION: v1.0.0-FOUNDER-DESIGNATION-REPLAY-ISOLATION-CERT
# AUTHORITY BOUNDARY: test confirms non-IAM title never assigns grants
# TENANT POSTURE: UUID synthetic membership and Owner identity
# FAIL-CLOSED POSTURE: invalid proof and cross-principal do not claim Founder
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
