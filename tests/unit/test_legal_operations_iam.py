"""TITLE: WILSY OS Legal Operations IAM certificate.
VERSION: v1.0.0-L7A-LEGAL-OPERATIONS-IAM-CERT
AUTHORITY: Direct adversarial certificate for conjunctive Legal Operations authorization.
EPITOME: Proves current principal, membership, business-role, permission, assignment,
          and tenant-scope gates without persistence or transport mutation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_iam.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: v1.0.0 certifies explicit Legal Operations role and permission gates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every decision is exact-principal and exact-tenant scoped.
AUTHORITY BOUNDARY: Test certificate only; no lifecycle, persistence, HTTP, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Missing, malformed, inactive, ambiguous, cross-tenant, and financial requests deny.
"""
from __future__ import annotations

from collections.abc import Mapping

import pytest

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.tenant_authorization import TenantAuthorizationReason, authorize_tenant_operation
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError


VERSION = "v1.0.0-L7A-LEGAL-OPERATIONS-IAM-CERT"
_PID = "principal-1"
_TENANT = "tenant-alpha"
_PERMISSION = "legal_operations:instruction:read"
_OPERATION = "legal_instruction_read"


class _Reader:
    """Read-only deterministic authority double with no mutation surface."""

    def __init__(self, values: Mapping[tuple[str, ...], object]) -> None:
        self.values = dict(values)

    def resolve(self, *keys: str) -> object:
        key = tuple(keys)
        if key in self.values:
            return self.values[key]
        if len(key) == 1:
            raise PrincipalAuthorityNotFoundError("PRINCIPAL_NOT_FOUND")
        if len(key) == 2:
            raise TenantMembershipNotFoundError("MEMBERSHIP_NOT_FOUND")
        raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")


def _principal(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> PrincipalAuthority:
    return PrincipalAuthority(_PID, status, 1)


def _membership(
    tenant: str = _TENANT,
    status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
) -> TenantMembershipAuthority:
    return TenantMembershipAuthority(_PID, tenant, status, 1)


def _assignment(
    role_id: str,
    status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
    tenant: str = _TENANT,
) -> RoleAssignmentAuthority:
    return RoleAssignmentAuthority(_PID, tenant, role_id, status, 1)


def _readers(
    *,
    business_role: str | None = "tenant_legal_partner",
    auth_role: str | None = "LEGAL_PARTNER",
    principal: PrincipalAuthority | None = None,
    membership: TenantMembershipAuthority | None = None,
    tenant: str = _TENANT,
) -> tuple[_Reader, _Reader, _Reader]:
    principal_reader = _Reader({(_PID,): principal or _principal()})
    membership_reader = _Reader({(_PID, tenant): membership or _membership(tenant)})
    values: dict[tuple[str, ...], object] = {}
    if business_role is not None:
        values[(_PID, tenant, business_role)] = _assignment(business_role, tenant=tenant)
    if auth_role is not None:
        values[(_PID, tenant, auth_role)] = _assignment(auth_role, tenant=tenant)
    return principal_reader, membership_reader, _Reader(values)


def _decision(
    *,
    permission: object = _PERMISSION,
    operation: object = _OPERATION,
    tenant: object = _TENANT,
    readers: tuple[_Reader, _Reader, _Reader] | None = None,
):
    principal_reader, membership_reader, role_reader = readers or _readers()
    return authorize_tenant_operation(
        principal_id=_PID,
        tenant_id=tenant,
        permission_id=permission,
        operation=operation,
        principal_repository=principal_reader,
        membership_repository=membership_reader,
        business_role_repository=role_reader,
        role_assignment_repository=role_reader,
    )


def test_exact_conjunction_authorizes_legal_partner() -> None:
    result = _decision()
    assert result.authorized is True
    assert result.reason is TenantAuthorizationReason.AUTHORIZED
    assert result.business_role == "tenant_legal_partner"
    assert result.authorization_role == "LEGAL_PARTNER"


@pytest.mark.parametrize(
    ("permission", "operation"),
    [
        ("legal_operations:unknown:read", _OPERATION),
        ("legal_operations:instruction:read ", _OPERATION),
        (_PERMISSION, "unknown_operation"),
        (_PERMISSION, "legal_instruction_write"),
    ],
)
def test_unknown_malformed_or_mismatched_permission_denies(permission: str, operation: str) -> None:
    result = _decision(permission=permission, operation=operation)
    assert result.authorized is False


def test_inactive_principal_denies() -> None:
    assert _decision(readers=_readers(principal=_principal(PrincipalStatus.SUSPENDED))).reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE


def test_inactive_membership_denies() -> None:
    readers = _readers(membership=_membership(status=TenantMembershipStatus.REVOKED))
    assert _decision(readers=readers).reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE


@pytest.mark.parametrize("business_role", [None, "tenant_legal_finance"])
def test_absent_or_ineligible_business_role_denies(business_role: str | None) -> None:
    result = _decision(readers=_readers(business_role=business_role))
    assert result.authorized is False
    assert result.reason in {
        TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE,
        TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE,
    }


def test_ambiguous_business_roles_deny() -> None:
    principal_reader, membership_reader, role_reader = _readers()
    role_reader.values[(_PID, _TENANT, "tenant_legal_attorney")] = _assignment("tenant_legal_attorney")
    result = _decision(readers=(principal_reader, membership_reader, role_reader))
    assert result.reason is TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES


@pytest.mark.parametrize("auth_role", [None, "LEGAL_PARTNER"])
def test_missing_or_inactive_authorization_assignment_denies(auth_role: str | None) -> None:
    readers = _readers(auth_role=auth_role)
    if auth_role is not None:
        readers[2].values[(_PID, _TENANT, auth_role)] = _assignment(auth_role, RoleAssignmentStatus.REVOKED)
    result = _decision(readers=readers)
    assert result.authorized is False
    assert result.reason in {
        TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
        TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE,
    }


def test_cross_tenant_scope_denies_before_authority_match() -> None:
    result = _decision(tenant="tenant-foreign", readers=_readers(tenant=_TENANT))
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND


def test_financial_execution_is_always_denied() -> None:
    result = _decision(permission="legal_operations:billing:read", operation="financial_execution")
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED


def test_reader_doubles_expose_no_write_calls() -> None:
    readers = _readers()
    for reader in readers:
        assert not any(name in dir(reader) for name in ("create", "insert", "update", "delete"))


# ARTIFACT: test_legal_operations_iam.py
# VERSION: v1.0.0-L7A-LEGAL-OPERATIONS-IAM-CERT
# AUTHORITY BOUNDARY: direct conjunctive authorization certificate only
# TENANT POSTURE: exact principal/membership/business-role/assignment scope
# FAIL-CLOSED POSTURE: all malformed, absent, inactive, ambiguous, and financial cases deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
