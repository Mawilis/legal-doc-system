"""P21B direct certification for firm Representation-decision IAM.

TITLE: WILSY OS P21B Representation Firm Decision IAM Certificate
VERSION: v1.0.0-L9C11-P21B-FIRM-REPRESENTATION-DECISION-IAM-DIRECT-CERT
AUTHORITY: Pure canonical tenant-IAM certification only.
EPITOME: Prove the exact operation, permission, mapping, grants and exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_representation_firm_decision_authorization.py
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
AUTHORITY BOUNDARY: No persistence, Representation formation, Court or finance.
"""
from dataclasses import dataclass

import pytest

import tools.eos.auth.tenant_authorization as tenant_authorization
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.roles import get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import tenant_role_operation_eligibility
from tools.eos.auth.tenant_authorization import TenantAuthorizationReason, authorize_tenant_operation
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError


TENANT = "tenant-p21b-iam"
PRINCIPAL = "principal-p21b-iam"
OPERATION = "legal_matter_representation_firm_decision_write"
PERMISSION = "legal_operations:matter_representation_firm_decision:write"


@dataclass(frozen=True, slots=True)
class _Principal:
    status: PrincipalStatus


@dataclass(frozen=True, slots=True)
class _Membership:
    status: TenantMembershipStatus


@dataclass(frozen=True, slots=True)
class _Assignment:
    status: object


class _Authorities:
    def __init__(self, business_role: str, grants: tuple[str, ...] = ()) -> None:
        self.business_role = business_role
        self.grants = grants

    def resolve(self, *keys: str, **_kwargs: object) -> object:
        if len(keys) == 1:
            if keys[0] != PRINCIPAL:
                raise PrincipalAuthorityNotFoundError("not found")
            return _Principal(PrincipalStatus.ACTIVE)
        if len(keys) == 2:
            if keys != (PRINCIPAL, TENANT):
                raise TenantMembershipNotFoundError("not found")
            return _Membership(TenantMembershipStatus.ACTIVE)
        if len(keys) == 3:
            principal, tenant, role = keys
            if (principal, tenant) != (PRINCIPAL, TENANT):
                raise RoleAssignmentNotFoundError("not found")
            if role == self.business_role:
                return _Assignment(TenantBusinessRoleStatus.ACTIVE)
            if role in self.grants:
                return _Assignment(RoleAssignmentStatus.ACTIVE)
            raise RoleAssignmentNotFoundError("not found")
        raise AssertionError(keys)


def _decision(authorities: _Authorities, *, operation: str = OPERATION, permission: str = PERMISSION):
    return authorize_tenant_operation(
        principal_id=PRINCIPAL,
        tenant_id=TENANT,
        permission_id=permission,
        operation=operation,
        principal_repository=authorities,
        membership_repository=authorities,
        role_assignment_repository=authorities,
        business_role_repository=authorities,
    )


def test_exact_mapping_metadata_and_grants() -> None:
    assert tenant_authorization._BINDINGS[OPERATION] == PERMISSION
    assert list(tenant_authorization._BINDINGS).count(OPERATION) == 1
    metadata = permission_metadata(PERMISSION)
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert set(get_roles_granting_permission(PERMISSION)) == {"LEGAL_PARTNER", "LEGAL_ATTORNEY"}
    assert tenant_role_operation_eligibility("tenant_legal_partner", OPERATION) == "ELIGIBLE"
    assert tenant_role_operation_eligibility("tenant_legal_attorney", OPERATION) == "ELIGIBLE"


@pytest.mark.parametrize("business_role", ["tenant_legal_partner", "tenant_legal_attorney"])
def test_partner_and_attorney_are_authorized(business_role: str) -> None:
    role = "LEGAL_PARTNER" if business_role.endswith("partner") else "LEGAL_ATTORNEY"
    result = _decision(_Authorities(business_role, (role,)))
    assert result.authorized is True
    assert result.reason is TenantAuthorizationReason.AUTHORIZED


@pytest.mark.parametrize("business_role", ["tenant_legal_paralegal", "tenant_legal_secretary", "tenant_legal_finance", "tenant_legal_client"])
def test_excluded_roles_are_denied(business_role: str) -> None:
    result = _decision(_Authorities(business_role, ("LEGAL_PARTNER", "LEGAL_ATTORNEY")))
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


def test_crossed_permission_and_operation_fail_closed() -> None:
    result = _decision(_Authorities("tenant_legal_partner", ("LEGAL_PARTNER",)), permission="legal_operations:matter_engagement_firm_decision:write")
    assert result.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


# ARTIFACT: test_legal_matter_representation_firm_decision_authorization.py
# VERSION: v1.0.0-L9C11-P21B-FIRM-REPRESENTATION-DECISION-IAM-DIRECT-CERT
# AUTHORITY BOUNDARY: IAM contract only; no downstream legal authority
# FAIL-CLOSED POSTURE: exact mapping and conjunctive current truth required
# END OF WILSY OS SOVEREIGN ARTIFACT
