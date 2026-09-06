"""TITLE: WILSY OS Authorization-Role Delegation Certificate.
VERSION: v1.0.0-WILSY-A0P-GD1
AUTHORITY: Direct certificate of explicit GD1 grant law.
EPITOME: Certifies all 16 matrix edges and fail-closed boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authorization_role_delegation_policy.py
COLLABORATION / OWNERSHIP: EOS auth policy certificate.
SECURITY / PRIVACY POSTURE: Pure in-memory evidence; no secrets or persistence.
TENANT BOUNDARY: Every positive case is exact same-tenant.
AUTHORITY BOUNDARY: Tests policy evaluation only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: No transaction ownership.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 certifies GD1 matrix and adversarial denials.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
import pytest
from tools.eos.auth.authorization_role_delegation_policy import *
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP

ROLES = ("SOVEREIGN_ARCHITECT", "ENTERPRISE_ADMIN", "AUDITOR", "SERVICE_WORKER")
EXPECTED = {("ENTERPRISE_ADMIN", "AUDITOR"), ("ENTERPRISE_ADMIN", "SERVICE_WORKER")}

def assignment(role="ENTERPRISE_ADMIN", tenant="t1", status=RoleAssignmentStatus.ACTIVE):
    return RoleAssignmentAuthority("p1", tenant, role, status, 0)

@pytest.mark.parametrize("inviter", ROLES)
@pytest.mark.parametrize("target", ROLES)
def test_complete_sixteen_edge_matrix(inviter, target):
    result = evaluate_authorization_role_grant(assignment(inviter), "t1", target)
    assert result.allowed is ((inviter, target) in EXPECTED)

def test_allowed_edges_require_canonical_permission():
    from unittest.mock import patch
    with patch.dict(ROLE_PERMISSIONS_MAP, {"ENTERPRISE_ADMIN": []}, clear=False):
        assert not evaluate_authorization_role_grant(assignment(), "t1", "AUDITOR").allowed

def test_tenant_and_lifecycle_boundaries():
    assert not evaluate_authorization_role_grant(assignment(), "other", "AUDITOR").allowed
    assert not evaluate_authorization_role_grant(assignment(status=RoleAssignmentStatus.REVOKED), "t1", "AUDITOR").allowed

@pytest.mark.parametrize("role", ["UNKNOWN"])
def test_unknown_inviter_denied(role):
    assert not evaluate_authorization_role_grant(assignment(role), "t1", "AUDITOR").allowed

def test_malformed_target_denied():
    assert not evaluate_authorization_role_grant(assignment(), "t1", " ").allowed

@pytest.mark.parametrize("role", ["UNKNOWN", "AUDITOR ", "future_role"])
def test_unknown_target_denied(role):
    assert not evaluate_authorization_role_grant(assignment(), "t1", role).allowed

def test_matrix_is_immutable_and_no_business_role_dependency():
    assert ALLOW_EDGES == EXPECTED
    assert isinstance(ALLOW_EDGES, frozenset)

def test_deterministic_and_side_effect_free():
    a = assignment(); first = evaluate_authorization_role_grant(a, "t1", "AUDITOR"); second = evaluate_authorization_role_grant(a, "t1", "AUDITOR")
    assert first == second and a.role_id == "ENTERPRISE_ADMIN"

# ARTIFACT: test_authorization_role_delegation_policy.py
# VERSION: v1.0.0-WILSY-A0P-GD1
# AUTHORITY BOUNDARY: certificate only; no authority grant
# END OF WILSY OS SOVEREIGN ARTIFACT
