"""Direct certificate for D22B3-P17 issuance authority substrate.

TITLE: Tenant Product Entitlement Issuance Authority Substrate Certificate
VERSION: v1.0.0-D22B3-P17-TENANT-PRODUCT-ENTITLEMENT-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove the exact permission, business eligibility, static role grant,
         operation binding and conjunctive authorization for future issuance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_product_entitlement_authority_substrate.py
COLLABORATION / OWNERSHIP: Certifies existing sovereign authorization composition;
                            it does not implement or invoke entitlement issuance.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-P17-TENANT-PRODUCT-ENTITLEMENT-AUTHORITY-CERT establishes
           exact canonical, malformed, separation, role and conjunction proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identities and resolve-only fakes.
TENANT BOUNDARY: Authorization requires exact ACTIVE own-tenant membership.
AUTHORITY BOUNDARY: Authority substrate evidence only; no issuance or mutation.
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


PERMISSION = "tenant_product_entitlement:issue"
OPERATION = "tenant_product_entitlement_issue"
PRINCIPAL = "principal-a"
TENANT = "tenant-a"


@dataclass(frozen=True, slots=True)
class Record:
    """Minimal immutable current-authority record."""

    status: object


class PrincipalReader:
    """Resolve one exact principal without mutation surface."""

    def __init__(self, status: PrincipalStatus = PrincipalStatus.ACTIVE) -> None:
        self.status = status

    def resolve(self, principal_id: str) -> Record:
        if principal_id != PRINCIPAL:
            raise PrincipalAuthorityNotFoundError("missing")
        return Record(self.status)


class MembershipReader:
    """Resolve one exact tenant membership without mutation surface."""

    def __init__(
        self,
        status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    ) -> None:
        self.status = status

    def resolve(self, principal_id: str, tenant_id: str) -> Record:
        if (principal_id, tenant_id) != (PRINCIPAL, TENANT):
            raise TenantMembershipNotFoundError("missing")
        return Record(self.status)


class AssignmentReader:
    """Resolve exact business/authorization role assignments."""

    def __init__(self, roles: dict[str, RoleAssignmentStatus]) -> None:
        self.roles = dict(roles)

    def resolve(self, principal_id: str, tenant_id: str, role_id: str) -> Record:
        if (principal_id, tenant_id) != (PRINCIPAL, TENANT):
            raise RoleAssignmentNotFoundError("missing")
        status = self.roles.get(role_id)
        if status is None:
            raise RoleAssignmentNotFoundError("missing")
        return Record(status)


def decision(
    *,
    business_role: str = "tenant_owner",
    authorization_role: str = "ENTERPRISE_ADMIN",
    membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    assignment_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
    permission: object = PERMISSION,
    operation: object = OPERATION,
    tenant_id: object = TENANT,
):
    """Exercise the production conjunctive authorization pipeline."""
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


def test_canonical_permission_metadata_is_exact_bounded_and_nonfinancial() -> None:
    """The new canonical vocabulary describes issuance metadata only."""
    metadata = permission_metadata(PERMISSION)
    assert metadata.disposition is PermissionDisposition.CANONICAL
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.business_capability == (
        "issue bounded own-tenant product entitlement evidence from canonical commercial truth"
    )
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is False
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    forbidden_claims = (
        "payment",
        "settlement",
        "subscription mutation",
        "plan mutation",
        "business classification",
        "artificial intelligence",
        "route admission",
        "branding",
    )
    assert all(claim not in metadata.business_capability.casefold() for claim in forbidden_claims)


@pytest.mark.parametrize(
    "value",
    [
        "tenant_product_entitlement",
        "tenant_product_entitlement:*",
        "tenant_product_entitlement:manage",
        "tenant_product_entitlement:issue:",
        "tenant_product_entitlement:issue ",
        " tenant_product_entitlement:issue",
        "TENANT_PRODUCT_ENTITLEMENT:ISSUE",
    ],
)
def test_malformed_and_wildcard_permissions_fail_closed(value: str) -> None:
    """No partial, wildcard, whitespace or case alias becomes canonical."""
    with pytest.raises(ValueError, match="UNKNOWN_PERMISSION"):
        permission_metadata(value)
    assert get_roles_granting_permission(value) == ()


def test_closed_operation_binding_and_subscription_separation_are_exact() -> None:
    """The new operation binds only its permission, never subscription manage."""
    assert OPERATION in OPERATIONS
    assert permission_for_business_role_operation(OPERATION) == PERMISSION
    assert PERMISSION != "subscription:manage"
    assert permission_for_business_role_operation(OPERATION) != "subscription:manage"
    subscription_operations = {
        operation for operation in OPERATIONS if operation.startswith("subscription_")
    }
    assert all(
        permission_for_business_role_operation(operation) != PERMISSION
        for operation in subscription_operations
    )
    for malformed in ("", "unknown", f"{OPERATION} ", f" {OPERATION}", OPERATION.upper()):
        assert permission_for_business_role_operation(malformed) is None
        assert tenant_role_operation_eligibility("tenant_owner", malformed) == DENY


def test_business_role_eligibility_is_exactly_three_general_roles() -> None:
    """Only owner, admin and manager receive non-authorizing eligibility."""
    eligible = {
        role
        for role in TENANT_ROLES
        if tenant_role_operation_eligibility(role, OPERATION) == ELIGIBLE
    }
    assert eligible == {"tenant_owner", "tenant_admin", "tenant_manager"}
    assert tenant_role_operation_eligibility("tenant_auditor", OPERATION) == DENY


def test_static_authorization_role_grant_is_enterprise_admin_only() -> None:
    """AUDITOR and every specialized role remain without issuance permission."""
    assert get_roles_granting_permission(PERMISSION) == ("ENTERPRISE_ADMIN",)
    assert ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"].count(PERMISSION) == 1
    assert PERMISSION not in ROLE_PERMISSIONS_MAP["AUDITOR"]
    assert all(
        role == "ENTERPRISE_ADMIN" or PERMISSION not in permissions
        for role, permissions in ROLE_PERMISSIONS_MAP.items()
    )


@pytest.mark.parametrize("business_role", ["tenant_owner", "tenant_admin", "tenant_manager"])
def test_full_conjunction_authorizes_only_approved_business_roles(
    business_role: str,
) -> None:
    """ACTIVE membership, eligibility, assignment and exact pair authorize."""
    result = decision(business_role=business_role)
    assert result.authorized is True
    assert result.reason is TenantAuthorizationReason.AUTHORIZED
    assert result.authorization_role == "ENTERPRISE_ADMIN"


def test_conjunctive_failures_cannot_be_bypassed() -> None:
    """Permission possession alone cannot bypass any required authority fact."""
    cases = (
        decision(authorization_role="AUDITOR"),
        decision(business_role="tenant_auditor"),
        decision(membership_status=TenantMembershipStatus.SUSPENDED),
        decision(assignment_status=RoleAssignmentStatus.REVOKED),
        decision(permission="subscription:manage"),
        decision(operation="subscription_create"),
        decision(permission=f"{PERMISSION} "),
        decision(tenant_id="other-tenant"),
    )
    assert all(result.authorized is False for result in cases)


def test_operation_is_nonfinancial_and_cannot_reach_system_execution() -> None:
    """The new substrate adds no Kennel or platform-release binding."""
    assert authorization_module._BINDINGS[OPERATION] == PERMISSION
    assert authorization_module._BINDINGS[OPERATION] not in {
        "platform_billing:release",
        "execution:trigger",
        "payment",
        "settlement",
    }
    assert decision(operation="financial_execution").authorized is False


# ARTIFACT: test_tenant_product_entitlement_authority_substrate.py
# VERSION: v1.0.0-D22B3-P17-TENANT-PRODUCT-ENTITLEMENT-AUTHORITY-CERT
# AUTHORITY BOUNDARY: issuance authority substrate certification only; no issuance, persistence, route or financial authority
# TENANT POSTURE: exact ACTIVE own-tenant membership plus business and authorization role conjunction
# FAIL-CLOSED POSTURE: malformed values, missing conjuncts, specialization, wildcard and authority crossing deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
