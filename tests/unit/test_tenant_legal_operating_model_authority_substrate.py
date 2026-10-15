"""TITLE: Tenant Legal Operating Model Authority Substrate Certificate
VERSION: v1.0.0-CX26-R3-LEGAL-OPERATING-MODEL-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact own-tenant operating-model management permission, business eligibility, static grant and conjunctive authorization.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_legal_operating_model_authority_substrate.py
COLLABORATION / OWNERSHIP: Certifies the existing tenant authorization substrate only; it does not configure an operating model.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes canonical permission metadata, exact operation binding, tenant_admin eligibility, ENTERPRISE_ADMIN grant and fail-closed conjunction.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identities and resolve-only authority readers.
TENANT BOUNDARY: Exact ACTIVE own-tenant membership is required.
AUTHORITY BOUNDARY: Configuration command admission substrate only; no role assignment, workflow, entitlement, professional, legal-execution or transport authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

import tools.eos.auth.tenant_authorization as authorization_module
from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
)
from tools.eos.auth.roles import (
    ROLE_PERMISSIONS_MAP,
    get_roles_granting_permission,
)
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    OPERATIONS,
    TENANT_ROLES,
    permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
)

PERMISSION = "legal_operations:operating_model:manage"
OPERATION = "legal_operating_model_manage"
PRINCIPAL = "principal-operating-model-admin"
TENANT = "tenant-operating-model"


@dataclass(frozen=True, slots=True)
class Record:
    """Minimal immutable current-authority projection."""

    status: object


class PrincipalReader:
    """Resolve exactly one synthetic principal."""

    def __init__(
        self,
        status: PrincipalStatus = PrincipalStatus.ACTIVE,
    ) -> None:
        self.status = status

    def resolve(self, principal_id: str) -> Record:
        if principal_id != PRINCIPAL:
            raise PrincipalAuthorityNotFoundError("missing")
        return Record(self.status)


class MembershipReader:
    """Resolve exact own-tenant membership."""

    def __init__(
        self,
        status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    ) -> None:
        self.status = status

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
    ) -> Record:
        if (principal_id, tenant_id) != (PRINCIPAL, TENANT):
            raise TenantMembershipNotFoundError("missing")
        return Record(self.status)


class AssignmentReader:
    """Resolve exact business and authorization role assignments."""

    def __init__(
        self,
        roles: dict[str, RoleAssignmentStatus],
    ) -> None:
        self.roles = dict(roles)

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
    ) -> Record:
        if (principal_id, tenant_id) != (PRINCIPAL, TENANT):
            raise RoleAssignmentNotFoundError("missing")
        status = self.roles.get(role_id)
        if status is None:
            raise RoleAssignmentNotFoundError("missing")
        return Record(status)


def decision(
    *,
    business_role: str = "tenant_admin",
    authorization_role: str = "ENTERPRISE_ADMIN",
    membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    assignment_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
    permission: object = PERMISSION,
    operation: object = OPERATION,
    tenant_id: object = TENANT,
):
    """Exercise the production conjunctive authorization path."""
    return authorize_tenant_operation(
        principal_id=PRINCIPAL,
        tenant_id=tenant_id,
        permission_id=permission,
        operation=operation,
        principal_repository=PrincipalReader(),
        membership_repository=MembershipReader(membership_status),
        business_role_repository=AssignmentReader(
            {business_role: RoleAssignmentStatus.ACTIVE}
        ),
        role_assignment_repository=AssignmentReader(
            {authorization_role: assignment_status}
        ),
    )


def test_permission_metadata_is_exact_own_tenant_and_nonfinancial() -> None:
    metadata = permission_metadata(PERMISSION)

    assert metadata.disposition is PermissionDisposition.CANONICAL
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.business_capability == (
        "manage own-tenant Legal operating-model configuration"
    )
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is False
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False


def test_static_authorization_grant_is_enterprise_admin_only() -> None:
    assert get_roles_granting_permission(PERMISSION) == (
        "ENTERPRISE_ADMIN",
    )
    assert ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"].count(PERMISSION) == 1
    assert all(
        role == "ENTERPRISE_ADMIN" or PERMISSION not in permissions
        for role, permissions in ROLE_PERMISSIONS_MAP.items()
    )


def test_business_eligibility_is_exactly_tenant_admin() -> None:
    eligible = {
        role
        for role in TENANT_ROLES
        if tenant_role_operation_eligibility(role, OPERATION) == ELIGIBLE
    }

    assert eligible == {"tenant_admin"}

    for role in (
        "tenant_owner",
        "tenant_manager",
        "tenant_auditor",
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "tenant_legal_client",
        "tenant_sheriff",
        "tenant_deputy",
    ):
        assert tenant_role_operation_eligibility(role, OPERATION) == DENY


def test_operation_binding_is_exact_and_unique() -> None:
    assert OPERATION in OPERATIONS
    assert permission_for_business_role_operation(OPERATION) == PERMISSION
    assert authorization_module._BINDINGS[OPERATION] == PERMISSION
    assert list(authorization_module._BINDINGS).count(OPERATION) == 1


def test_full_current_conjunction_authorizes() -> None:
    result = decision()

    assert result.authorized is True
    assert result.reason is TenantAuthorizationReason.AUTHORIZED
    assert result.business_role == "tenant_admin"
    assert result.authorization_role == "ENTERPRISE_ADMIN"


@pytest.mark.parametrize(
    ("business_role", "authorization_role"),
    [
        ("tenant_owner", "ENTERPRISE_ADMIN"),
        ("tenant_manager", "ENTERPRISE_ADMIN"),
        ("tenant_auditor", "AUDITOR"),
        ("tenant_legal_partner", "LEGAL_PARTNER"),
    ],
)
def test_ineligible_business_or_authorization_roles_fail_closed(
    business_role: str,
    authorization_role: str,
) -> None:
    result = decision(
        business_role=business_role,
        authorization_role=authorization_role,
    )
    assert result.authorized is False


def test_missing_conjuncts_and_cross_tenant_fail_closed() -> None:
    cases = (
        decision(
            membership_status=TenantMembershipStatus.SUSPENDED,
        ),
        decision(
            assignment_status=RoleAssignmentStatus.REVOKED,
        ),
        decision(
            authorization_role="AUDITOR",
        ),
        decision(
            tenant_id="other-tenant",
        ),
    )

    assert all(result.authorized is False for result in cases)


def test_cross_pair_alias_and_financial_paths_fail_closed() -> None:
    assert decision(
        permission="tenant:profile:write",
    ).authorized is False

    assert decision(
        operation="profile_update",
    ).authorized is False

    assert decision(
        permission=f"{PERMISSION} ",
    ).authorized is False

    assert decision(
        operation=OPERATION.upper(),
    ).authorized is False

    assert decision(
        operation="financial_execution",
    ).authorized is False


def test_substrate_creates_no_operating_model_or_financial_authority() -> None:
    result = decision()

    assert result.authorized is True
    assert authorization_module._BINDINGS[OPERATION] not in {
        "platform_billing:release",
        "execution:trigger",
        "payment",
        "settlement",
    }


# ARTIFACT: test_tenant_legal_operating_model_authority_substrate.py
# VERSION: v1.0.0-CX26-R3-LEGAL-OPERATING-MODEL-AUTHORITY-CERT
# AUTHORITY BOUNDARY: exact current IAM command-admission substrate only; no operating-model mutation or downstream authority
# TENANT POSTURE: exact ACTIVE own-tenant membership plus tenant_admin and ENTERPRISE_ADMIN conjunction
# FAIL-CLOSED POSTURE: malformed, missing, inactive, crossed, ineligible, cross-tenant, and financial paths deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
