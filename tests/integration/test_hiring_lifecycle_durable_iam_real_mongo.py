"""Durable current-truth authorization certification for WILSY hiring commands."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
from pymongo import MongoClient

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization import authorize_tenant_operation, TenantAuthorizationReason

URI = os.getenv("HIRING_TEST_MONGODB_URI")
NOW = datetime.now(timezone.utc)
pytestmark = pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")


class PrincipalReader:
    def __init__(self, collection): self.collection = collection
    def resolve(self, principal_id, *, session=None):
        return PrincipalAuthorityRepository.resolve(principal_id, collection=self.collection, session=session)


class MembershipReader:
    def __init__(self, collection): self.collection = collection
    def resolve(self, principal_id, tenant_id, *, session=None):
        return TenantMembershipRepository.resolve(principal_id, tenant_id, collection=self.collection, session=session)


class BusinessRoleReader:
    def __init__(self, collection): self.collection = collection
    def resolve(self, principal_id, tenant_id, *, session=None):
        return TenantBusinessRoleRepository.resolve(principal_id, tenant_id, collection=self.collection, session=session)


class AuthorizationRoleReader:
    def __init__(self, collection): self.collection = collection
    def resolve(self, principal_id, tenant_id, role_id, *, session=None):
        return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, collection=self.collection, session=session)


def test_real_mongo_hiring_authorization_requires_current_principal_membership_business_role_and_grant():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    db_name = f"hiring_iam_cert_{uuid.uuid4().hex}"
    db = client[db_name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        principals, memberships = db["principal_authorities"], db["tenant_memberships"]
        business, assignments = db["tenant_business_roles"], db["role_assignments"]
        PrincipalAuthorityRepository.ensure_indexes(principals)
        TenantMembershipRepository.ensure_indexes(memberships)
        TenantBusinessRoleRepository.ensure_indexes(business)
        RoleAssignmentRepository.ensure_indexes(assignments)

        def seed(pid, tenant, business_role, authorization_role):
            PrincipalAuthorityRepository.create(PrincipalAuthority(pid, PrincipalStatus.ACTIVE, 0), principals)
            TenantMembershipRepository.insert(TenantMembershipAuthority(pid, tenant, TenantMembershipStatus.ACTIVE, 0), memberships)
            TenantBusinessRoleRepository.insert(TenantBusinessRoleAuthority(
                principal_id=pid, tenant_id=tenant, business_role=business_role,
                status=TenantBusinessRoleStatus.ACTIVE, revision=0, effective_at=NOW, revoked_at=None,
            ), business)
            RoleAssignmentRepository.insert(RoleAssignmentAuthority(
                pid, tenant, authorization_role, RoleAssignmentStatus.ACTIVE, 0,
            ), assignments)

        manager_id, director_id = f"manager-{uuid.uuid4().hex}", f"director-{uuid.uuid4().hex}"
        tenant, other_tenant = f"tenant-{uuid.uuid4().hex}", f"other-{uuid.uuid4().hex}"
        seed(manager_id, tenant, "tenant_hr_manager", "HR_MANAGER")
        seed(director_id, tenant, "tenant_hr_director", "HR_DIRECTOR")
        readers = (
            PrincipalReader(principals), MembershipReader(memberships),
            BusinessRoleReader(business), AuthorizationRoleReader(assignments),
        )

        def authorize(pid, tid, permission, operation):
            return authorize_tenant_operation(
                principal_id=pid, tenant_id=tid, permission_id=permission,
                operation=operation, principal_repository=readers[0],
                membership_repository=readers[1], business_role_repository=readers[2],
                role_assignment_repository=readers[3],
            )

        allowed = authorize(manager_id, tenant, "hr:hiring_candidate:create", "hr_hiring_candidate_create")
        assert allowed.authorized is True
        assert allowed.reason is TenantAuthorizationReason.AUTHORIZED
        assert allowed.authorization_role == "HR_MANAGER"

        wrong_tenant = authorize(manager_id, other_tenant, "hr:hiring_candidate:create", "hr_hiring_candidate_create")
        assert wrong_tenant.authorized is False
        assert wrong_tenant.reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND

        insufficient = authorize(director_id, tenant, "hr:hiring_candidate:create", "hr_hiring_candidate_create")
        assert insufficient.authorized is False
        assert insufficient.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

        director_decision = authorize(director_id, tenant, "hr:hiring_offer:decide", "hr_hiring_offer_decide")
        assert director_decision.authorized is True
        manager_decision = authorize(manager_id, tenant, "hr:hiring_offer:decide", "hr_hiring_offer_decide")
        assert manager_decision.authorized is False
        assert manager_decision.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    finally:
        client.drop_database(db_name)
        assert db_name not in client.list_database_names()
        client.close()
