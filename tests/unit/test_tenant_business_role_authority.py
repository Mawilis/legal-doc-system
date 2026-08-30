"""TITLE: Tenant Business Role Authority Certification.
VERSION: v1.0.1-TENANT-BUSINESS-ROLE-AUTHORITY-CERT
AUTHORITY: Certification of durable business-role evidence resolver only.
EPITOME: Proves exact scope, ACTIVE-only resolution, ambiguity denial, and non-authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_business_role_authority.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.1 certifies compound principal/tenant scope and malformed-input isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: No network, persistence mutation, credentials, or financial execution.
TENANT BOUNDARY: Exact principal and tenant are always required.
AUTHORITY BOUNDARY: Evidence is not membership, permission, or authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from dataclasses import dataclass
import pytest
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_business_role_authority import *
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepositoryError

@dataclass
class Assignment:
    status: RoleAssignmentStatus

class Repo:
    def __init__(self, values=None, error=None): self.values, self.error, self.calls = values or {}, error, []
    def resolve(self, principal_id, tenant_id, role_id):
        self.calls.append((principal_id, tenant_id, role_id))
        if self.error: raise self.error
        value = self.values.get((principal_id, tenant_id, role_id))
        if value is None: from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError; raise RoleAssignmentNotFoundError("missing")
        return value

@pytest.mark.parametrize("role", sorted(TENANT_ROLES))
def test_each_active_canonical_role_resolves(role):
    result = resolve_current_tenant_business_role(principal_id="p", tenant_id="t", repository=Repo({("p", "t", role): Assignment(RoleAssignmentStatus.ACTIVE)}))
    assert result.role == role and result.resolution is BusinessRoleResolution.RESOLVED

def test_fail_closed_matrix():
    revoked = Repo({("p", "t", "tenant_owner"): Assignment(RoleAssignmentStatus.REVOKED)})
    assert resolve_current_tenant_business_role(principal_id="p", tenant_id="t", repository=Repo()).resolution is BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE
    assert resolve_current_tenant_business_role(principal_id="p", tenant_id="t", repository=revoked).role is None
    assert resolve_current_tenant_business_role(principal_id="p", tenant_id="t", repository=Repo({("p", "t", "ADMIN"): Assignment(RoleAssignmentStatus.ACTIVE)})).role is None
    assert resolve_current_tenant_business_role(principal_id="p", tenant_id="t", repository=Repo({("p", "t", "tenant_owner"): Assignment(RoleAssignmentStatus.ACTIVE), ("p", "t", "tenant_admin"): Assignment(RoleAssignmentStatus.ACTIVE)})).resolution is BusinessRoleResolution.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES
    assert resolve_current_tenant_business_role(principal_id="p", tenant_id="t", repository=Repo({("p", "t", "tenant_owner"): Assignment(RoleAssignmentStatus.ACTIVE), ("p", "t", "tenant_admin"): Assignment(RoleAssignmentStatus.REVOKED)})).role == "tenant_owner"
    assert resolve_current_tenant_business_role(principal_id="", tenant_id="t", repository=Repo()).resolution is BusinessRoleResolution.INVALID_INPUT
    assert resolve_current_tenant_business_role(principal_id="p", tenant_id="other", repository=Repo({("p", "tenant-a", "tenant_owner"): Assignment(RoleAssignmentStatus.ACTIVE)})).role is None
    assert resolve_current_tenant_business_role(principal_id="p", tenant_id="t", repository=Repo(error=RoleAssignmentRepositoryError("down"))).resolution is BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE

def test_exact_scope_and_non_authority():
    repo = Repo({("p", "t", "tenant_owner"): Assignment(RoleAssignmentStatus.ACTIVE)})
    result = resolve_current_tenant_business_role(principal_id="p", tenant_id="t", repository=repo)
    assert all(call[0] == "p" and call[1] == "t" and call[2] in TENANT_ROLES for call in repo.calls)
    with pytest.raises((AttributeError, TypeError)): result.role = "tenant_admin"  # type: ignore[misc]
    assert "permission" not in result.__class__.__annotations__

def test_compound_scope_and_invalid_inputs() -> None:
    repo = Repo({("p", "tenant-a", "tenant_owner"): Assignment(RoleAssignmentStatus.ACTIVE)})
    assert resolve_current_tenant_business_role(principal_id="p", tenant_id="tenant-a", repository=repo).role == "tenant_owner"
    assert resolve_current_tenant_business_role(principal_id="p", tenant_id="tenant-b", repository=repo).resolution is BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE
    assert resolve_current_tenant_business_role(principal_id="principal-b", tenant_id="tenant-a", repository=repo).resolution is BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE
    before = len(repo.calls)
    for principal in ("", " ", " p", "p ", None, 123):
        assert resolve_current_tenant_business_role(principal_id=principal, tenant_id="t", repository=repo).resolution is BusinessRoleResolution.INVALID_INPUT
    for tenant in ("", " ", " t", "t ", None, 123):
        assert resolve_current_tenant_business_role(principal_id="p", tenant_id=tenant, repository=repo).resolution is BusinessRoleResolution.INVALID_INPUT
    assert len(repo.calls) == before

# ARTIFACT: test_tenant_business_role_authority.py
# VERSION: v1.0.1-TENANT-BUSINESS-ROLE-AUTHORITY-CERT
# AUTHORITY BOUNDARY: evidence resolver certification only
# TENANT POSTURE: exact scope; no membership is fabricated
# FAIL-CLOSED POSTURE: ambiguity and unavailable storage deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
