"""TITLE: WILSY OS Authorization-Role Delegation Certificate.
VERSION: v1.5.0-WILSY-PROJECT-CONTRIBUTOR-DELEGATION-CERT
AUTHORITY: Direct certificate of explicit GD1 grant law.
EPITOME: Certifies the explicit authorization-role delegation graph, exact WILSY-only admission-officer issuance, and fail-closed boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authorization_role_delegation_policy.py
COLLABORATION / OWNERSHIP: EOS auth policy certificate.
SECURITY / PRIVACY POSTURE: Pure in-memory evidence; no secrets or persistence.
TENANT BOUNDARY: Every positive case is exact same-tenant; admission-officer issuance is canonical WILSY-tenant only.
AUTHORITY BOUNDARY: Tests policy evaluation only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: No transaction ownership.
CERTIFICATION / UPDATE DATE: 2026-11-15
CHANGELOG:
    2026-11-22 v1.5.0-WILSY-PROJECT-CONTRIBUTOR-DELEGATION-CERT certifies exact WILSY-only Enterprise Admin invite of a narrow PROJECTS_PARTICIPANT_CONTRIBUTOR role and denies cross-tenant, revoked, other inviter or grant-free paths.
    2026-11-16 v1.4.0-PROJECTS-PLATFORM-OWNER-DELEGATION-CERT verifies the dedicated Projects role invitation edge is Enterprise-Admin-only and WILSY-tenant-only, with acceptance required before assignment.
    2026-11-15 v1.3.0-COMPANY-READER-DELEGATION-AND-ADMIN-READ-CERT confirms
    the static Enterprise Admin read permission does not alter the existing
    reader delegation edge or create author/publisher authority.
    v1.2.0-COMPANY-READER-DELEGATION-CERT preserves the full prior matrix and adds
    exact company-reader grant scope, permission and author/publisher denials.
    2026-11-12 v1.2.0-COMPANY-READER-DELEGATION-CERT certifies
    the new Enterprise Admin -> admission-officer grant edge only in the exact
    canonical WILSY employer tenant; no role assignment is created by this test.
    v1.0.0 certifies GD1 matrix and adversarial denials.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
import pytest
from tools.eos.auth.authorization_role_delegation_policy import *
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID

ROLES = (
    "SOVEREIGN_ARCHITECT",
    "ENTERPRISE_ADMIN",
    "AUDITOR",
    "SERVICE_WORKER",
    "PLATFORM_EMPLOYEE_ADMISSION_OFFICER",
    "PROJECTS_PLATFORM_OWNER",
    "PROJECTS_PARTICIPANT_CONTRIBUTOR",
)
EXPECTED = {
    ("ENTERPRISE_ADMIN", "AUDITOR"),
    ("ENTERPRISE_ADMIN", "SERVICE_WORKER"),
    ("ENTERPRISE_ADMIN", "PLATFORM_EMPLOYEE_ADMISSION_OFFICER"),
    ("ENTERPRISE_ADMIN", "COMPANY_DOCUMENT_READER"),
    ("ENTERPRISE_ADMIN", "PROJECTS_PLATFORM_OWNER"),
    ("ENTERPRISE_ADMIN", "PROJECTS_PARTICIPANT_CONTRIBUTOR"),
}

def assignment(role="ENTERPRISE_ADMIN", tenant="t1", status=RoleAssignmentStatus.ACTIVE):
    return RoleAssignmentAuthority("p1", tenant, role, status, 0)

@pytest.mark.parametrize("inviter", ROLES)
@pytest.mark.parametrize("target", ROLES)
def test_complete_seven_role_pair_matrix(inviter, target):
    result = evaluate_authorization_role_grant(assignment(inviter), "t1", target)
    expected = (inviter, target) in EXPECTED and target != PLATFORM_EMPLOYEE_ADMISSION_ROLE and not (target in {PROJECTS_PLATFORM_OWNER_ROLE, PROJECTS_PARTICIPANT_CONTRIBUTOR_ROLE} and "t1" != WILSY_COMPANY_TENANT_ID)
    assert result.allowed is expected

def test_allowed_edges_require_canonical_permission():
    from unittest.mock import patch
    with patch.dict(ROLE_PERMISSIONS_MAP, {"ENTERPRISE_ADMIN": []}, clear=False):
        assert not evaluate_authorization_role_grant(assignment(), "t1", "AUDITOR").allowed

def test_tenant_and_lifecycle_boundaries():
    assert not evaluate_authorization_role_grant(assignment(), "other", "AUDITOR").allowed
    assert not evaluate_authorization_role_grant(assignment(status=RoleAssignmentStatus.REVOKED), "t1", "AUDITOR").allowed


def test_admission_officer_delegation_is_wilsy_tenant_only():
    allowed = evaluate_authorization_role_grant(
        assignment(tenant=WILSY_COMPANY_TENANT_ID),
        WILSY_COMPANY_TENANT_ID,
        PLATFORM_EMPLOYEE_ADMISSION_ROLE,
    )
    assert allowed.allowed is True
    assert allowed.denial_code is None

    for tenant_id in ("customer-tenant", "t1"):
        denied = evaluate_authorization_role_grant(
            assignment(tenant=tenant_id),
            tenant_id,
            PLATFORM_EMPLOYEE_ADMISSION_ROLE,
        )
        assert denied.allowed is False
        assert denied.denial_code is AuthorizationRoleGrantDenialCode.GRANT_NOT_PERMITTED

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

@pytest.mark.parametrize("role", ["COMPANY_DOCUMENT_AUTHOR", "COMPANY_DOCUMENT_PUBLISHER"])
def test_reader_edge_does_not_delegate_preparation_or_publication(role):
    assert not evaluate_authorization_role_grant(assignment(tenant=WILSY_COMPANY_TENANT_ID), WILSY_COMPANY_TENANT_ID, role).allowed

def test_projects_platform_owner_delegation_is_wilsy_only_and_explicit():
    allowed = evaluate_authorization_role_grant(
        assignment(tenant=WILSY_COMPANY_TENANT_ID),
        WILSY_COMPANY_TENANT_ID,
        PROJECTS_PLATFORM_OWNER_ROLE,
    )
    assert allowed.allowed is True
    assert allowed.denial_code is None
    assert ROLE_PERMISSIONS_MAP[PROJECTS_PLATFORM_OWNER_ROLE] == [
        "project:read", "project:create", "project:update", "project:archive",
    ]
    for tenant_id in ("customer-tenant", "t1"):
        denied = evaluate_authorization_role_grant(
            assignment(tenant=tenant_id), tenant_id, PROJECTS_PLATFORM_OWNER_ROLE,
        )
        assert denied.allowed is False
        assert denied.denial_code is AuthorizationRoleGrantDenialCode.GRANT_NOT_PERMITTED


def test_project_contributor_grant_is_canonical_founder_only_and_not_inherited():
    target = PROJECTS_PARTICIPANT_CONTRIBUTOR_ROLE
    allowed = evaluate_authorization_role_grant(
        assignment(tenant=WILSY_COMPANY_TENANT_ID),
        WILSY_COMPANY_TENANT_ID, target,
    )
    assert allowed.allowed is True
    assert ROLE_PERMISSIONS_MAP[target] == [
        "project:participant:read", "project:participant:contribute",
    ]
    for tenant in ("t1", "customer-tenant"):
        result = evaluate_authorization_role_grant(
            assignment(tenant=tenant), tenant, target,
        )
        assert result.allowed is False
        assert result.denial_code is AuthorizationRoleGrantDenialCode.GRANT_NOT_PERMITTED
    for inviter in ("AUDITOR", "SERVICE_WORKER", "PROJECTS_PLATFORM_OWNER"):
        assert not evaluate_authorization_role_grant(
            assignment(role=inviter, tenant=WILSY_COMPANY_TENANT_ID),
            WILSY_COMPANY_TENANT_ID, target,
        ).allowed
    assert not evaluate_authorization_role_grant(
        assignment(tenant=WILSY_COMPANY_TENANT_ID, status=RoleAssignmentStatus.REVOKED),
        WILSY_COMPANY_TENANT_ID, target,
    ).allowed


def test_company_reader_edge_is_explicit_tenant_local_and_non_possessory():
    assert evaluate_authorization_role_grant(assignment(tenant=WILSY_COMPANY_TENANT_ID), WILSY_COMPANY_TENANT_ID, COMPANY_DOCUMENT_READER_ROLE).allowed
    assert not evaluate_authorization_role_grant(assignment(), "t1", COMPANY_DOCUMENT_READER_ROLE).allowed
    assert ROLE_PERMISSIONS_MAP[COMPANY_DOCUMENT_READER_ROLE] == ["company_operating_document:read"]
    assert ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"].count("company_operating_document:read") == 1
    assert "company_operating_document:author" not in ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"]
    assert "company_operating_document:publish" not in ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"]

# ARTIFACT: test_authorization_role_delegation_policy.py
# VERSION: v1.5.0-WILSY-PROJECT-CONTRIBUTOR-DELEGATION-CERT
# AUTHORITY BOUNDARY: certificate only; no authority grant or assignment is created
# TENANT POSTURE: platform-only Projects delegation is confined to the canonical WILSY company tenant
# FAIL-CLOSED POSTURE: non-WILSY and unlisted delegation edges deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
