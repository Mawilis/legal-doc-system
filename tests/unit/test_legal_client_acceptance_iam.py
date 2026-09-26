"""Direct L9A3 certificate for the client-acceptance IAM boundary."""
from __future__ import annotations

from dataclasses import dataclass

from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus


TENANT = "tenant-client"
PRINCIPAL = "principal-client"
PERMISSION = "legal_operations:client_acceptance:write"
OPERATION = "legal_client_acceptance_write"


@dataclass(frozen=True)
class StatusRecord:
    status: object


class Principal:
    def resolve(self, principal_id: str, **_kwargs: object) -> object:
        assert principal_id == PRINCIPAL
        return StatusRecord(PrincipalStatus.ACTIVE)


class Membership:
    def resolve(self, principal_id: str, tenant_id: str, **_kwargs: object) -> object:
        assert (principal_id, tenant_id) == (PRINCIPAL, TENANT)
        return StatusRecord(TenantMembershipStatus.ACTIVE)


class Assignment:
    def __init__(self, roles: dict[str, object]) -> None:
        self.roles = roles

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, **_kwargs: object) -> object:
        assert (principal_id, tenant_id) == (PRINCIPAL, TENANT)
        if role_id not in self.roles:
            raise RoleAssignmentNotFoundError(role_id)
        return self.roles[role_id]


def decision(business_role: str, authorization_role: str):
    return authorize_tenant_operation(
        principal_id=PRINCIPAL,
        tenant_id=TENANT,
        permission_id=PERMISSION,
        operation=OPERATION,
        principal_repository=Principal(),
        membership_repository=Membership(),
        business_role_repository=Assignment(
            {business_role: StatusRecord(RoleAssignmentStatus.ACTIVE)}
        ),
        role_assignment_repository=Assignment(
            {authorization_role: StatusRecord(RoleAssignmentStatus.ACTIVE)}
        ),
    )


def test_permission_is_tenant_membership_gated_non_financial_and_not_self_authorizing() -> None:
    metadata = permission_metadata(PERMISSION)
    assert metadata.namespace == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False


def test_only_legal_client_conjunctive_pair_is_authorized() -> None:
    result = decision("tenant_legal_client", "LEGAL_CLIENT")
    assert result.authorized is True
    assert result.business_role == "tenant_legal_client"
    assert result.authorization_role == "LEGAL_CLIENT"


def test_law_firm_role_is_denied_even_with_otherwise_active_assignment() -> None:
    result = decision("tenant_legal_partner", "LEGAL_PARTNER")
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


# ARTIFACT: test_legal_client_acceptance_iam.py
# VERSION: v1.0.0-L9A3-CLIENT-ACCEPTANCE-IAM-CERT
# AUTHORITY BOUNDARY: direct permission/role/operation composition certificate
# TENANT POSTURE: exact active membership and client role are required
# FAIL-CLOSED POSTURE: non-client business roles deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
