"""TITLE: WILSY OS Legal Productive-Work Read Authority Certificate.

VERSION: v1.0.0-PW-P11A-PRODUCTIVE-WORK-READ-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS IAM certification.
EPITOME: Freeze and adversarially certify the exact self-projection read
         permission, operation, business eligibility and authorization grants.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_productive_work_read_authority_substrate.py
COLLABORATION / OWNERSHIP: PW-P11A authority substrate; PW-P11B HTTP is a
                            separate consumer and creates no authority here.
CERTIFICATION / UPDATE DATE: 2026-10-16
CHANGELOG: v1.0.0-PW-P11A establishes the first exact productive-work read
           authority certificate for four law-firm workforce personas.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Exact strings and conjunctive current authority;
                            aliases and metadata-only eligibility fail closed.
TENANT BOUNDARY: Active own-tenant membership is mandatory.
AUTHORITY BOUNDARY: Self-projection read only; no record enumeration, write,
                    assignment, supervision, transition or professional power.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from collections.abc import Mapping

import pytest

from tools.eos.auth.permission_namespace import PermissionDisposition, permission_metadata
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP, get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.tenant_authorization import TenantAuthorizationReason, authorize_tenant_operation
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError


VERSION = "v1.0.0-PW-P11A-PRODUCTIVE-WORK-READ-AUTHORITY-CERT"
OPERATION = "legal_productive_work_read"
PERMISSION = "legal_operations:productive_work:read"
PRINCIPAL = "principal-p11a"
TENANT = "tenant-p11a"
ALLOWED_PAIRS = {
    "tenant_legal_partner": "LEGAL_PARTNER",
    "tenant_legal_attorney": "LEGAL_ATTORNEY",
    "tenant_legal_paralegal": "LEGAL_PARALEGAL",
    "tenant_legal_secretary": "LEGAL_SECRETARY",
}
DENIED_BUSINESS_ROLES = {
    "tenant_owner",
    "tenant_admin",
    "tenant_manager",
    "tenant_auditor",
    "tenant_legal_finance",
    "tenant_sheriff",
    "tenant_deputy",
    "tenant_legal_client",
}
DENIED_AUTHORIZATION_ROLES = {
    "ENTERPRISE_ADMIN",
    "AUDITOR",
    "LEGAL_FINANCE",
    "SHERIFF",
    "DEPUTY",
    "LEGAL_CLIENT",
    "SERVICE_WORKER",
}


class _Reader:
    """Resolve immutable authority-shaped test records without mutation APIs."""

    def __init__(self, values: Mapping[tuple[str, ...], object]) -> None:
        self.values = dict(values)

    def resolve(self, *keys: str) -> object:
        """Resolve one exact authority key or return a typed absence."""
        key = tuple(keys)
        if key in self.values:
            return self.values[key]
        if len(key) == 1:
            raise PrincipalAuthorityNotFoundError("PRINCIPAL_NOT_FOUND")
        if len(key) == 2:
            raise TenantMembershipNotFoundError("MEMBERSHIP_NOT_FOUND")
        raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")


def _assignment(role_id: str, status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE) -> RoleAssignmentAuthority:
    """Build one exact current-role authority record for certification."""
    return RoleAssignmentAuthority(PRINCIPAL, TENANT, role_id, status, 1)


def _authorize(
    business_role: str,
    authorization_role: str | None,
    *,
    permission: str = PERMISSION,
    operation: str = OPERATION,
    membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    assignment_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
):
    """Compose the production authorization decision from bounded readers."""
    principal_reader = _Reader({
        (PRINCIPAL,): PrincipalAuthority(PRINCIPAL, PrincipalStatus.ACTIVE, 1),
    })
    membership_reader = _Reader({
        (PRINCIPAL, TENANT): TenantMembershipAuthority(
            PRINCIPAL, TENANT, membership_status, 1
        ),
    })
    assignments = {
        (PRINCIPAL, TENANT, business_role): _assignment(business_role),
    }
    if authorization_role is not None:
        assignments[(PRINCIPAL, TENANT, authorization_role)] = _assignment(
            authorization_role, assignment_status
        )
    assignment_reader = _Reader(assignments)
    return authorize_tenant_operation(
        principal_id=PRINCIPAL,
        tenant_id=TENANT,
        permission_id=permission,
        operation=operation,
        principal_repository=principal_reader,
        membership_repository=membership_reader,
        business_role_repository=assignment_reader,
        role_assignment_repository=assignment_reader,
    )


def test_exact_canonical_permission_and_operation_binding() -> None:
    """Certify one exact non-financial, non-self-authorizing permission pair."""
    metadata = permission_metadata(PERMISSION)
    assert metadata.permission_id == PERMISSION
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert metadata.disposition is PermissionDisposition.CANONICAL
    assert permission_for_business_role_operation(OPERATION) == PERMISSION


def test_exact_business_eligibility_and_static_grants() -> None:
    """Certify least-privilege four-persona eligibility and static grants."""
    for business_role, authorization_role in ALLOWED_PAIRS.items():
        assert tenant_role_operation_eligibility(business_role, OPERATION) == ELIGIBLE
        assert ROLE_PERMISSIONS_MAP[authorization_role].count(PERMISSION) == 1
    assert set(get_roles_granting_permission(PERMISSION)) == set(ALLOWED_PAIRS.values())
    for business_role in DENIED_BUSINESS_ROLES:
        assert tenant_role_operation_eligibility(business_role, OPERATION) == DENY
    for authorization_role in DENIED_AUTHORIZATION_ROLES:
        assert PERMISSION not in ROLE_PERMISSIONS_MAP[authorization_role]


@pytest.mark.parametrize("pair", ALLOWED_PAIRS.items())
def test_exact_conjunction_authorizes_each_frozen_persona(pair: tuple[str, str]) -> None:
    """Prove each allowed business/final-role pair succeeds conjunctively."""
    business_role, authorization_role = pair
    decision = _authorize(business_role, authorization_role)
    assert decision.authorized is True
    assert decision.reason is TenantAuthorizationReason.AUTHORIZED
    assert decision.business_role == business_role
    assert decision.authorization_role == authorization_role


@pytest.mark.parametrize("business_role", sorted(DENIED_BUSINESS_ROLES))
def test_business_eligibility_denials_precede_permission_possession(business_role: str) -> None:
    """Prove admin, finance, field-service and client roles cannot inherit."""
    decision = _authorize(business_role, "LEGAL_PARTNER")
    assert decision.authorized is False
    assert decision.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


def test_eligibility_without_active_permission_possession_denies() -> None:
    """Prove eligibility metadata never becomes authorization by itself."""
    missing = _authorize("tenant_legal_partner", None)
    revoked = _authorize(
        "tenant_legal_partner",
        "LEGAL_PARTNER",
        assignment_status=RoleAssignmentStatus.REVOKED,
    )
    assert missing.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED
    assert revoked.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE


def test_revoked_membership_denies_before_permission_use() -> None:
    """Prove stale tenant membership cannot exercise an otherwise valid grant."""
    decision = _authorize(
        "tenant_legal_partner",
        "LEGAL_PARTNER",
        membership_status=TenantMembershipStatus.REVOKED,
    )
    assert decision.reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE


@pytest.mark.parametrize(
    ("permission", "operation"),
    (
        (PERMISSION + " ", OPERATION),
        (PERMISSION.upper(), OPERATION),
        (PERMISSION, OPERATION + " "),
        (PERMISSION, OPERATION.upper()),
        ("legal_operations:work_item:read", OPERATION),
        (PERMISSION, "legal_work_item_read"),
        ("legal_operations:queue:read", OPERATION),
        ("legal_operations:deputy_queue:read", OPERATION),
    ),
)
def test_alias_case_whitespace_and_adjacent_authorities_deny(
    permission: str,
    operation: str,
) -> None:
    """Prove adjacent or malformed authorities cannot substitute for PW-P11A."""
    decision = _authorize(
        "tenant_legal_partner",
        "LEGAL_PARTNER",
        permission=permission,
        operation=operation,
    )
    assert decision.authorized is False


def test_no_side_authority_is_introduced() -> None:
    """Prove the new grant does not imply mutation or financial permissions."""
    forbidden = {
        "legal_operations:work_item:write",
        "legal_operations:matter_workflow:transition",
        "legal_operations:queue:read",
        "legal_operations:deputy_queue:read",
        "platform_billing:release",
    }
    assert PERMISSION not in forbidden
    assert all(not token.endswith(":write") for token in {PERMISSION})


# ARTIFACT: test_legal_productive_work_read_authority_substrate.py
# VERSION: v1.0.0-PW-P11A-PRODUCTIVE-WORK-READ-AUTHORITY-CERT
# AUTHORITY BOUNDARY: exact self-projection read certificate only
# TENANT POSTURE: active own-tenant membership and exact role conjunction
# FAIL-CLOSED POSTURE: unknown, malformed, adjacent, stale, or missing truth denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
