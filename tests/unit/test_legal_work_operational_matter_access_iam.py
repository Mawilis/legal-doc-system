"""WILSY OS P47-R95-G28 — Dedicated operational grant IAM contract.

This contract registers Partner-only issuance, never matter access.
All facts must originate from sovereign IAM, not service-local constants.
"""

from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.tenant_authority_policy import (
    SystemAuthorityClassification,
    requires_system_authority,
)
from tools.eos.auth.tenant_authorization import _BINDINGS
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP

PERMISSION = "legal_operations:operational_matter_access:issue"
OPERATION = "legal_work_operational_matter_access_issue"


def test_permission_is_canonical_tenant_nonfinancial():
    meta = permission_metadata(PERMISSION)
    assert getattr(meta.disposition, "value", meta.disposition) == "CANONICAL"
    assert meta.namespace == "TENANT"
    assert meta.tenant_membership_required is True
    assert meta.cross_tenant_capable is False
    assert meta.financial_execution_capable is False


def test_operation_has_exact_canonical_binding():
    assert _BINDINGS.get(OPERATION) == PERMISSION
    assert (
        requires_system_authority(OPERATION)
        is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    )


def test_only_legal_partner_has_static_issuer_permission():
    holders = {
        role
        for role, permissions in ROLE_PERMISSIONS_MAP.items()
        if PERMISSION in permissions
    }
    assert holders == {"LEGAL_PARTNER"}


def test_issuer_permission_not_reused_as_practitioner_binding():
    assert (
        _BINDINGS.get("legal_practitioner_matter_binding_provision")
        == "legal_operations:practitioner_matter_binding:provision"
    )
    assert _BINDINGS.get(OPERATION) != _BINDINGS.get(
        "legal_practitioner_matter_binding_provision"
    )


def test_no_authority_for_financial_execution():
    meta = permission_metadata(PERMISSION)
    assert meta.financial_execution_capable is False
    assert meta.cross_tenant_capable is False


def test_only_tenant_legal_partner_eligible_to_issue_operational_access():
    from tools.eos.auth.tenant_authority_policy import (
        ELIGIBLE,
        DENY,
        OPERATIONS,
        TENANT_ROLES,
        tenant_role_operation_eligibility,
    )

    assert OPERATION in OPERATIONS
    for role in TENANT_ROLES:
        expected = ELIGIBLE if role == "tenant_legal_partner" else DENY
        assert tenant_role_operation_eligibility(role, OPERATION) == expected

    assert tenant_role_operation_eligibility("LEGAL_PARTNER", OPERATION) == DENY
    assert tenant_role_operation_eligibility("tenant_admin", OPERATION) == DENY
    assert tenant_role_operation_eligibility(None, OPERATION) == DENY


# P47-R95-G32: No mocked authorization decision.
# Repository readers follow the existing sovereign IAM unit-test contract.

from types import SimpleNamespace
import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.legal_operations.service import (
    legal_work_operational_matter_access_issuance as issuance,
)

TENANT = "tenant-operational-access"
ACTOR = "partner-operational-access"


class ActiveSession:
    in_transaction = True


class PrincipalFacts:
    def __init__(self, status=PrincipalStatus.ACTIVE):
        self.status = status
        self.calls = []

    def resolve(self, principal_id, *, session=None):
        self.calls.append((principal_id, session))
        assert principal_id == ACTOR
        return SimpleNamespace(status=self.status)


class MembershipFacts:
    def __init__(self, status=TenantMembershipStatus.ACTIVE):
        self.status = status
        self.calls = []

    def resolve(self, principal_id, tenant_id, *, session=None):
        self.calls.append((principal_id, tenant_id, session))
        assert principal_id == ACTOR
        assert tenant_id == TENANT
        return SimpleNamespace(status=self.status)


class BusinessRoleFacts:
    def __init__(self, roles=("tenant_legal_partner",)):
        self.roles = roles
        self.calls = []

    def resolve(self, principal_id, tenant_id, role_id, *, session=None):
        self.calls.append((principal_id, tenant_id, role_id, session))
        if (
            principal_id != ACTOR
            or tenant_id != TENANT
            or role_id not in self.roles
        ):
            raise RoleAssignmentNotFoundError("NOT_ACTIVE")
        return SimpleNamespace(status=TenantBusinessRoleStatus.ACTIVE)


class PermissionGrantFacts:
    def __init__(self, status=RoleAssignmentStatus.ACTIVE):
        self.status = status
        self.calls = []

    def resolve(self, principal_id, tenant_id, role_id, *, session=None):
        self.calls.append((principal_id, tenant_id, role_id, session))
        if (
            principal_id != ACTOR
            or tenant_id != TENANT
            or role_id != "LEGAL_PARTNER"
        ):
            raise RoleAssignmentNotFoundError("NOT_GRANTED")
        return SimpleNamespace(status=self.status)


def exercise_real_issuer(
    *,
    tenant=TENANT,
    principal_status=PrincipalStatus.ACTIVE,
    membership_status=TenantMembershipStatus.ACTIVE,
    roles=("tenant_legal_partner",),
    grant_status=RoleAssignmentStatus.ACTIVE,
):
    session = ActiveSession()
    principal = PrincipalFacts(principal_status)
    membership = MembershipFacts(membership_status)
    business = BusinessRoleFacts(roles)
    grants = PermissionGrantFacts(grant_status)

    try:
        issuance._issuer(
            principal_id=ACTOR,
            tenant_id=tenant,
            principal_repository=principal,
            membership_repository=membership,
            business_role_repository=business,
            role_assignment_repository=grants,
            session=session,
        )
        return True, (principal, membership, business, grants), session
    except issuance.LegalWorkOperationalMatterAccessIssuanceDenied:
        return False, (principal, membership, business, grants), session


def nonactive(enum):
    return next(x for x in enum if x is not enum.ACTIVE)


def test_real_operational_issuer_partner_positive():
    allowed, readers, session = exercise_real_issuer()
    assert allowed is True
    principal, membership, business, grants = readers
    assert principal.calls == [(ACTOR, session)]
    assert membership.calls == [(ACTOR, TENANT, session)]
    assert business.calls
    assert all(call[3] is session for call in business.calls)
    assert grants.calls == [(ACTOR, TENANT, "LEGAL_PARTNER", session)]


def test_real_operational_issuer_inactive_principal_denied():
    allowed, readers, _ = exercise_real_issuer(
        principal_status=nonactive(PrincipalStatus)
    )
    assert allowed is False
    assert readers[1].calls == []


def test_real_operational_issuer_inactive_membership_denied():
    allowed, readers, _ = exercise_real_issuer(
        membership_status=nonactive(TenantMembershipStatus)
    )
    assert allowed is False
    assert readers[2].calls == []


@pytest.mark.parametrize("roles", [
    (),
    ("tenant_legal_attorney",),
    ("tenant_legal_partner", "tenant_legal_attorney"),
])
def test_real_operational_issuer_wrong_or_ambiguous_role_denied(roles):
    allowed, readers, _ = exercise_real_issuer(roles=roles)
    assert allowed is False
    assert readers[3].calls == []


def test_real_operational_issuer_inactive_partner_grant_denied():
    allowed, _, _ = exercise_real_issuer(
        grant_status=nonactive(RoleAssignmentStatus)
    )
    assert allowed is False


def test_real_operational_issuer_cross_tenant_denied():
    # Repository contract must reject foreign tenant scope.
    allowed, _, _ = exercise_real_issuer(
        tenant="tenant-foreign"
    )
    assert allowed is False
