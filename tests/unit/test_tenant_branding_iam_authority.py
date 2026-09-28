"""D21B branding-management IAM direct certificate.

TITLE: Tenant Branding Management IAM Certificate
VERSION: v1.0.0-L10-P2C4-D21B-BRANDING-IAM-DIRECT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify dedicated tenant-branding read/profile/asset permissions and
         conjunctive least-privilege authorization without transport or UI.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_iam_authority.py
AUTHORITY BOUNDARY: Permission, business-role eligibility and authorization
                    composition only; no profile or asset mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
from tools.eos.auth.permission_namespace import PermissionDisposition, permission_metadata
from tools.eos.auth.roles import get_roles_granting_permission


TENANT = "tenant-branding"
PRINCIPAL = "principal-branding"


class Principal:
    status = PrincipalStatus.ACTIVE

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        if principal_id != PRINCIPAL:
            raise PrincipalAuthorityNotFoundError()
        return self


class Membership:
    status = TenantMembershipStatus.ACTIVE

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        if principal_id != PRINCIPAL or tenant_id != TENANT:
            raise TenantMembershipNotFoundError()
        return self


class Assignments:
    def __init__(self, *, business_role: str = "tenant_owner", auth_role: str = "ENTERPRISE_ADMIN", active: bool = True) -> None:
        self.business_role = business_role
        self.auth_role = auth_role
        self.active = active

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> Any:
        if principal_id != PRINCIPAL or tenant_id != TENANT:
            raise RoleAssignmentNotFoundError()
        if role_id == self.business_role:
            return SimpleNamespace(status=SimpleNamespace(value="ACTIVE"))
        if role_id == self.auth_role:
            return SimpleNamespace(status=RoleAssignmentStatus.ACTIVE if self.active else RoleAssignmentStatus.REVOKED)
        raise RoleAssignmentNotFoundError()


def _authorize(*, permission: str, operation: str, business_role: str = "tenant_owner", auth_role: str = "ENTERPRISE_ADMIN", active: bool = True, principal: Any = Principal(), membership: Any = Membership()):
    return authorize_tenant_operation(
        principal_id=PRINCIPAL,
        tenant_id=TENANT,
        permission_id=permission,
        operation=operation,
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=Assignments(auth_role=auth_role, active=active),
        business_role_repository=Assignments(business_role=business_role),
    )


def test_canonical_permissions_are_dedicated_and_nonfinancial() -> None:
    for permission in ("tenant_branding:read", "tenant_branding:profile:manage", "tenant_branding:asset:manage"):
        metadata = permission_metadata(permission)
        assert metadata.disposition is PermissionDisposition.CANONICAL
        assert metadata.namespace == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False


@pytest.mark.parametrize(
    ("operation", "permission"),
    [("tenant_branding_read", "tenant_branding:read"), ("tenant_branding_profile_manage", "tenant_branding:profile:manage"), ("tenant_branding_asset_manage", "tenant_branding:asset:manage")],
)
def test_operation_bindings_are_exact(operation: str, permission: str) -> None:
    assert permission_for_business_role_operation(operation) == permission


def test_enterprise_admin_role_grants_exact_branding_permissions() -> None:
    assert set(get_roles_granting_permission("tenant_branding:read")) == {"AUDITOR", "ENTERPRISE_ADMIN"}
    assert get_roles_granting_permission("tenant_branding:profile:manage") == ("ENTERPRISE_ADMIN",)
    assert get_roles_granting_permission("tenant_branding:asset:manage") == ("ENTERPRISE_ADMIN",)


@pytest.mark.parametrize("role", ["tenant_owner", "tenant_admin"])
def test_authorized_admin_business_roles_pass_profile_and_asset(role: str) -> None:
    assert _authorize(permission="tenant_branding:profile:manage", operation="tenant_branding_profile_manage", business_role=role).authorized
    assert _authorize(permission="tenant_branding:asset:manage", operation="tenant_branding_asset_manage", business_role=role).authorized


def test_authorized_read_manager_passes() -> None:
    result = _authorize(permission="tenant_branding:read", operation="tenant_branding_read", business_role="tenant_manager")
    assert result.authorized


def test_inactive_principal_denies() -> None:
    class InactivePrincipal(Principal):
        status = PrincipalStatus.REVOKED
    result = _authorize(permission="tenant_branding:read", operation="tenant_branding_read", principal=InactivePrincipal())
    assert not result.authorized and result.reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE


def test_inactive_membership_denies() -> None:
    class InactiveMembership(Membership):
        status = TenantMembershipStatus.SUSPENDED
    result = _authorize(permission="tenant_branding:read", operation="tenant_branding_read", membership=InactiveMembership())
    assert not result.authorized and result.reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE


def test_inactive_role_assignment_denies() -> None:
    result = _authorize(permission="tenant_branding:profile:manage", operation="tenant_branding_profile_manage", active=False)
    assert not result.authorized and result.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE


def test_missing_permission_denies() -> None:
    result = _authorize(permission="tenant_branding:read", operation="tenant_branding_profile_manage")
    assert not result.authorized and result.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


def test_wrong_permission_denies() -> None:
    result = _authorize(permission="subscription:manage", operation="tenant_branding_profile_manage")
    assert not result.authorized and result.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


def test_cross_tenant_denies() -> None:
    result = authorize_tenant_operation(
        principal_id=PRINCIPAL, tenant_id="other-tenant", permission_id="tenant_branding:read", operation="tenant_branding_read",
        principal_repository=Principal(), membership_repository=Membership(), role_assignment_repository=Assignments(), business_role_repository=Assignments(),
    )
    assert not result.authorized and result.reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND


def test_ambiguous_business_roles_deny() -> None:
    class Ambiguous(Assignments):
        def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> Any:
            if role_id in {"tenant_owner", "tenant_admin"}:
                return SimpleNamespace(status=SimpleNamespace(value="ACTIVE"))
            raise RoleAssignmentNotFoundError()
    result = authorize_tenant_operation(
        principal_id=PRINCIPAL, tenant_id=TENANT, permission_id="tenant_branding:read", operation="tenant_branding_read",
        principal_repository=Principal(), membership_repository=Membership(), role_assignment_repository=Assignments(), business_role_repository=Ambiguous(),
    )
    assert not result.authorized and result.reason is TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES


@pytest.mark.parametrize("role", ["tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_client", "tenant_auditor", "tenant_inbound_merchant_configuration_admin", "tenant_deputy", "tenant_sheriff"])
def test_nonbranding_mutation_roles_deny(role: str) -> None:
    assert tenant_role_operation_eligibility(role, "tenant_branding_profile_manage") == DENY
    assert tenant_role_operation_eligibility(role, "tenant_branding_asset_manage") == DENY


def test_read_roles_are_separate_from_mutation() -> None:
    assert tenant_role_operation_eligibility("tenant_auditor", "tenant_branding_read") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_auditor", "tenant_branding_profile_manage") == DENY


def test_subscription_manage_is_not_branding_binding() -> None:
    assert _authorize(permission="subscription:manage", operation="tenant_branding_read").reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


def test_financial_execution_remains_prohibited() -> None:
    result = _authorize(permission="tenant_branding:asset:manage", operation="financial_execution")
    assert not result.authorized and result.reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED


# ARTIFACT: test_tenant_branding_iam_authority.py
# VERSION: v1.0.0-L10-P2C4-D21B-BRANDING-IAM-DIRECT-CERT
# AUTHORITY BOUNDARY: dedicated IAM policy and composition only
# FAIL-CLOSED POSTURE: absent, inactive, ambiguous, cross-tenant and mismatched authority denies
# END OF WILSY OS SOVEREIGN ARTIFACT
