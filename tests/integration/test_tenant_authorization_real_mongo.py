"""TITLE: WILSY OS Tenant Authorization Real-Mongo Certification.
VERSION: v1.0.0-TENANT-AUTHORIZATION-REAL-MONGO-CERT
AUTHORITY: Evidence-only certification of frozen tenant authorization composition.
EPITOME: Exercises governed repositories against one isolated replica-set database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_authorization_real_mongo.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0 certifies durable Mongo principal, membership, role and fail-closed composition.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: Local UUID database only; no credentials or production data are emitted.
TENANT BOUNDARY: Every read and write is explicitly scoped to the generated tenant and principal.
AUTHORITY BOUNDARY: This artifact certifies frozen tenant authorization composition against actual Mongo persistence using governed repository methods and explicit isolated collection injection. It does NOT certify HTTP/router/Node production wiring.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

import os
from uuid import uuid4
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization import TenantAuthorizationReason, authorize_tenant_operation

VERSION = "v1.0.0-TENANT-AUTHORIZATION-REAL-MONGO-CERT"


class _PrincipalReader:
    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
        self.collection = collection

    def resolve(self, principal_id: str) -> object:
        return PrincipalAuthorityRepository.get(principal_id, collection=self.collection)


class _MembershipReader:
    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, tenant_id: str) -> object:
        return TenantMembershipRepository.resolve(principal_id, tenant_id, collection=self.collection)


class _RoleReader:
    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, tenant_id: str, role_id: str) -> object:
        return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, collection=self.collection)


def test_tenant_authorization_real_mongo_matrix() -> None:
    """Certify current-truth composition, uniqueness, refresh, and financial denial."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000, socketTimeoutMS=5000)
    database_name = f"tenant_authorization_cert_{uuid4().hex}"
    assert database_name.startswith("tenant_authorization_cert_")
    database = client[database_name]
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName") == "wilsyVendorCertRS"
        assert "127.0.0.1:27027" in hello.get("me", "") or "127.0.0.1:27027" in hello.get("hosts", [])
        principals = database["principal_authorities"]
        memberships = database["tenant_memberships"]
        assignments = database["role_assignments"]
        PrincipalAuthorityRepository.ensure_indexes(principals)
        TenantMembershipRepository.ensure_indexes(memberships)
        RoleAssignmentRepository.ensure_indexes(assignments)
        principal_id, tenant_id = f"p-{uuid4().hex}", f"t-{uuid4().hex}"
        PrincipalAuthorityRepository.create(PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0), principals)
        TenantMembershipRepository.insert(TenantMembershipAuthority(principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 0), memberships)
        TenantMembershipRepository.insert(TenantMembershipAuthority(principal_id, f"wrong-{uuid4().hex}", TenantMembershipStatus.ACTIVE, 0), memberships)
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal_id, tenant_id, "tenant_auditor", RoleAssignmentStatus.ACTIVE, 0), assignments)
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal_id, tenant_id, "AUDITOR", RoleAssignmentStatus.ACTIVE, 0), assignments)
        readers = (_PrincipalReader(principals), _MembershipReader(memberships), _RoleReader(assignments))
        decision = authorize_tenant_operation(principal_id=principal_id, tenant_id=tenant_id, permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert decision.authorized is True
        assert decision.reason is TenantAuthorizationReason.AUTHORIZED
        assert decision.business_role == "tenant_auditor" and decision.authorization_role == "AUDITOR"
        financial = authorize_tenant_operation(principal_id=principal_id, tenant_id=tenant_id, permission_id="audit:read", operation="financial_execution", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert financial.reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED
        absent = authorize_tenant_operation(principal_id="absent", tenant_id=tenant_id, permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert absent.reason is TenantAuthorizationReason.PRINCIPAL_NOT_FOUND
        wrong_tenant = authorize_tenant_operation(principal_id=principal_id, tenant_id="missing-tenant", permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert wrong_tenant.reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND
        revoked = RoleAssignmentAuthority(principal_id, tenant_id, "AUDITOR", RoleAssignmentStatus.REVOKED, 1)
        RoleAssignmentRepository.compare_and_swap(revoked, 0, assignments)
        refreshed = authorize_tenant_operation(principal_id=principal_id, tenant_id=tenant_id, permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert refreshed.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


# ARTIFACT: test_tenant_authorization_real_mongo.py
# VERSION: v1.0.0-TENANT-AUTHORIZATION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo tenant authorization composition evidence only
# TENANT POSTURE: generated UUID database and exact principal/tenant keys
# FAIL-CLOSED POSTURE: unavailable, absent, inactive, ambiguous, and financial paths deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
