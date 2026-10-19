"""
TITLE: WILSY OS P9 Legal Work Reassignment Static Grant RED Certificate
VERSION: v1.0.0-P9-R22-REASSIGNMENT-STATIC-GRANTS-RED
AUTHORITY: Wilsy OS Core Engineering / Python EOS IAM
EPITOME:
    Freeze the exact least-privilege static authorization-role matrix
    for later bounded own-tenant Legal work-item reassignment admission.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_work_reassignment_static_role_grants.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R22-REASSIGNMENT-STATIC-GRANTS-RED
    certifies Partner/Attorney-only static policy and every-other-role denial.
COMPLIANCE: Test-first, exact grant enumeration, no wildcard authority.
SECURITY / PRIVACY POSTURE: All unspecified roles remain denied.
TENANT BOUNDARY:
    Static grants do not prove current exact-tenant ACTIVE membership.
AUTHORITY BOUNDARY:
    This certificate does not create active role assignment, business-role
    eligibility, operation binding, target membership, matter scope,
    supervisor entitlement, work assignment or reassignment command.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)
from tools.eos.auth.roles import (
    ROLE_PERMISSIONS_MAP,
    get_roles_granting_permission,
)

PERMISSION = "legal_operations:work_item:reassign"
ALLOWED_ROLES = ("LEGAL_ATTORNEY", "LEGAL_PARTNER")


def test_reassignment_static_grant_is_exactly_partner_and_attorney() -> None:
    assert get_roles_granting_permission(PERMISSION) == ALLOWED_ROLES

    for role, grants in ROLE_PERMISSIONS_MAP.items():
        assert grants.count(PERMISSION) == (
            1 if role in ALLOWED_ROLES else 0
        ), f"STATIC_GRANT_SCOPE_INVALID:{role}"


def test_every_other_role_excluded_including_enterprise_and_sovereign() -> None:
    assert len(ROLE_PERMISSIONS_MAP) == 38

    for role, grants in ROLE_PERMISSIONS_MAP.items():
        if role not in ALLOWED_ROLES:
            assert PERMISSION not in grants, role

    for role in (
        "LEGAL_PARALEGAL",
        "LEGAL_SECRETARY",
        "LEGAL_FINANCE",
        "LEGAL_CLIENT",
        "SHERIFF",
        "DEPUTY",
        "ENTERPRISE_ADMIN",
        "AUDITOR",
        "SOVEREIGN_ARCHITECT",
        "SERVICE_WORKER",
    ):
        assert role in ROLE_PERMISSIONS_MAP
        assert PERMISSION not in ROLE_PERMISSIONS_MAP[role]


def test_static_policy_does_not_convert_vocabulary_to_execution_authority() -> None:
    metadata = permission_metadata(PERMISSION)

    assert metadata.disposition is PermissionDisposition.CANONICAL
    assert metadata.namespace == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is False
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert PERMISSION != "legal_operations:work_item:write"
    assert PERMISSION != "legal_operations:work_item:complete"


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_reassignment_static_role_grants.py
# VERSION: v1.0.0-P9-R22-REASSIGNMENT-STATIC-GRANTS-RED
# AUTHORITY BOUNDARY: static role-grant test only; no actual possession
# TENANT POSTURE: separately prove exact current tenant membership
# FAIL-CLOSED POSTURE: all non-Partner/Attorney roles denied
# ACTIVE ROLE ASSIGNMENT AUTHORITY: NONE
# BUSINESS-ROLE ELIGIBILITY AUTHORITY: NONE
# OPERATION BINDING AUTHORITY: NONE
# REASSIGNMENT COMMAND AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
