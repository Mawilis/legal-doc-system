"""TITLE: WILSY OS HR Employee Relation Write IAM Certification.
VERSION: v1.0.0-P0-C12E4B3B-HR-EMPLOYEE-RELATION-WRITE-IAM-CERT
AUTHORITY: Direct certification of bounded own-tenant EmployeeRelation write authorization.
EPITOME: Proves one exact HR EmployeeRelation write permission, five single-purpose
authorization roles, five eligible HR business roles, 96 denied HR business
roles, exact operation-permission binding, full current-truth composition,
and preserved Legal, general-enterprise and financial authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_employee_relation_write_iam.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12E4B3B-HR-EMPLOYEE-RELATION-WRITE-IAM-CERT
establishes the first direct HR IAM certificate. It proves the frozen 101-role
HR business vocabulary is canonical while exactly tenant_hr_director,
tenant_hr_manager, tenant_employee_relations_director,
tenant_employee_relations_manager and tenant_employee_relations_specialist are
eligible for hr_employee_relation_write. It proves exact static grant roles,
canonical TENANT permission metadata, conjunctive ACTIVE current truth,
cross-pair denial, excluded-role denial, and financial-execution prohibition.
It grants no HTTP route, payroll execution, payment execution, settlement,
job-title-derived authority or manager-relationship-derived authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Test-only read/resolve doubles; no credentials,
network, persistence mutation or transport-projected authority.
TENANT BOUNDARY: Exact principal and tenant scope, ACTIVE membership, one
eligible tenant HR business role, exact permission-operation pair and one
ACTIVE granting authorization role are conjunctively required.
AUTHORITY BOUNDARY: Certifies IAM composition only; does not create HTTP,
EmployeeRelation service, payroll, employment-outcome or financial authority.
FINANCIAL AUTHORITY BOUNDARY: No payment execution or settlement authority;
Kennel EOS remains exclusive.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pytest

import tools.eos.auth.tenant_authorization as ta

from tools.eos.auth.hr_business_role_catalog import (
    ALL_HR_BUSINESS_ROLES,
    EMPLOYEE_RELATION_FORMAL_WRITE_ROLE_CANDIDATES,
    EMPLOYEE_RELATION_REPORT_ONLY_ROLE_CANDIDATES,
)
from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    canonical_permissions,
    permission_metadata,
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
    SystemAuthorityClassification,
    normalize_tenant_business_role,
    permission_for_business_role_operation,
    requires_system_authority,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipStatus,
)


VERSION = "v1.0.0-P0-C12E4B3B-HR-EMPLOYEE-RELATION-WRITE-IAM-CERT"


PERMISSION = "hr:employee_relation:write"
OPERATION = "hr_employee_relation_write"

BUSINESS_ROLES = (
    "tenant_hr_director",
    "tenant_hr_manager",
    "tenant_employee_relations_director",
    "tenant_employee_relations_manager",
    "tenant_employee_relations_specialist",
)

AUTH_ROLES = (
    "HR_DIRECTOR",
    "HR_MANAGER",
    "EMPLOYEE_RELATIONS_DIRECTOR",
    "EMPLOYEE_RELATIONS_MANAGER",
    "EMPLOYEE_RELATIONS_SPECIALIST",
)

PAIRS = tuple(
    zip(
        BUSINESS_ROLES,
        AUTH_ROLES,
        strict=True,
    )
)

PID = "principal-hr-iam-cert"
TENANT = "tenant-hr-iam-cert"


@dataclass(frozen=True, slots=True)
class StatusRecord:
    status: object


class PrincipalRepository:
    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> object:
        assert principal_id == PID
        return StatusRecord(
            PrincipalStatus.ACTIVE
        )


class MembershipRepository:
    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object:
        assert (
            principal_id,
            tenant_id,
        ) == (
            PID,
            TENANT,
        )
        return StatusRecord(
            TenantMembershipStatus.ACTIVE
        )


class BusinessRoleRepository:
    def __init__(
        self,
        active_role: str,
    ) -> None:
        self.active_role = active_role

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        assert (
            principal_id,
            tenant_id,
        ) == (
            PID,
            TENANT,
        )

        if role_id != self.active_role:
            raise RoleAssignmentNotFoundError(
                "missing"
            )

        return StatusRecord(
            RoleAssignmentStatus.ACTIVE
        )


class AuthorizationRoleRepository:
    def __init__(
        self,
        *active_roles: str,
    ) -> None:
        self.active_roles = frozenset(
            active_roles
        )

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        assert (
            principal_id,
            tenant_id,
        ) == (
            PID,
            TENANT,
        )

        if role_id not in self.active_roles:
            raise RoleAssignmentNotFoundError(
                "missing"
            )

        return StatusRecord(
            RoleAssignmentStatus.ACTIVE
        )


def decision(
    *,
    business_role: str,
    auth_roles: tuple[str, ...],
    permission: str = PERMISSION,
    operation: str = OPERATION,
) -> TenantAuthorizationDecision:
    return authorize_tenant_operation(
        principal_id=PID,
        tenant_id=TENANT,
        permission_id=permission,
        operation=operation,
        principal_repository=PrincipalRepository(),
        membership_repository=MembershipRepository(),
        business_role_repository=BusinessRoleRepository(
            business_role
        ),
        role_assignment_repository=AuthorizationRoleRepository(
            *auth_roles
        ),
    )


def test_permission_registry_expands_exactly_one_canonical_row() -> None:
    rows = json.loads(
        canonical_permissions()
    )

    assert len(
        [
            row
            for row in rows
            if row["disposition"]
            == "CANONICAL"
        ]
    ) == 73

    assert len(rows) == 76

    assert sum(
        row["permission_id"]
        == PERMISSION
        for row in rows
    ) == 1


def test_permission_metadata_is_exact_tenant_non_financial() -> None:
    metadata = permission_metadata(
        PERMISSION
    )

    assert metadata.permission_id == PERMISSION
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is False
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert metadata.deprecated_or_legacy is False

    assert (
        metadata.disposition
        is PermissionDisposition.CANONICAL
    )


def test_all_101_hr_roles_are_canonical_business_role_vocabulary() -> None:
    assert len(
        ALL_HR_BUSINESS_ROLES
    ) == 101

    assert len(
        TENANT_ROLES
    ) == 119

    assert (
        ALL_HR_BUSINESS_ROLES
        <= TENANT_ROLES
    )

    for role in ALL_HR_BUSINESS_ROLES:
        assert (
            normalize_tenant_business_role(
                role
            )
            == role
        )


def test_exact_five_static_auth_roles_grant_permission() -> None:
    assert (
        get_roles_granting_permission(
            PERMISSION
        )
        == tuple(
            sorted(
                AUTH_ROLES
            )
        )
    )


@pytest.mark.parametrize(
    "role",
    AUTH_ROLES,
)
def test_each_new_static_auth_role_is_single_purpose(
    role: str,
) -> None:
    assert (
        ROLE_PERMISSIONS_MAP[
            role
        ]
        == [
            PERMISSION
        ]
    )


def test_operation_permission_binding_is_exact_and_unique() -> None:
    assert OPERATION in OPERATIONS

    assert (
        permission_for_business_role_operation(
            OPERATION
        )
        == PERMISSION
    )

    assert (
        ta._BINDINGS[
            OPERATION
        ]
        == PERMISSION
    )

    assert (
        list(
            ta._BINDINGS
        ).count(
            OPERATION
        )
        == 1
    )


@pytest.mark.parametrize(
    "role",
    BUSINESS_ROLES,
)
def test_only_formal_write_candidates_are_eligible(
    role: str,
) -> None:
    assert (
        role
        in EMPLOYEE_RELATION_FORMAL_WRITE_ROLE_CANDIDATES
    )

    assert (
        tenant_role_operation_eligibility(
            role,
            OPERATION,
        )
        == ELIGIBLE
    )


def test_every_other_hr_role_remains_denied() -> None:
    denied = (
        ALL_HR_BUSINESS_ROLES
        - set(BUSINESS_ROLES)
    )

    assert len(denied) == 96

    assert all(
        tenant_role_operation_eligibility(
            role,
            OPERATION,
        )
        == DENY
        for role in denied
    )


def test_report_only_candidates_remain_denied() -> None:
    assert (
        EMPLOYEE_RELATION_REPORT_ONLY_ROLE_CANDIDATES
        <= ALL_HR_BUSINESS_ROLES
    )

    assert all(
        tenant_role_operation_eligibility(
            role,
            OPERATION,
        )
        == DENY
        for role
        in EMPLOYEE_RELATION_REPORT_ONLY_ROLE_CANDIDATES
    )


@pytest.mark.parametrize(
    "role",
    (
        "tenant_owner",
        "tenant_admin",
        "tenant_manager",
        "tenant_auditor",
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "tenant_legal_client",
    ),
)
def test_existing_non_hr_business_roles_receive_no_hr_write_eligibility(
    role: str,
) -> None:
    assert (
        tenant_role_operation_eligibility(
            role,
            OPERATION,
        )
        == DENY
    )


def test_operation_is_non_system() -> None:
    assert (
        requires_system_authority(
            OPERATION
        )
        is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    )


@pytest.mark.parametrize(
    (
        "business_role",
        "auth_role",
    ),
    PAIRS,
)
def test_full_current_truth_authorizes_each_certified_hr_pair(
    business_role: str,
    auth_role: str,
) -> None:
    result = decision(
        business_role=business_role,
        auth_roles=(
            auth_role,
        ),
    )

    assert result == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        business_role,
        auth_role,
    )


def test_eligible_business_role_without_active_grant_denies() -> None:
    result = decision(
        business_role="tenant_hr_director",
        auth_roles=(),
    )

    assert result.authorized is False
    assert (
        result.reason
        is TenantAuthorizationReason.PERMISSION_NOT_GRANTED
    )


def test_enterprise_admin_does_not_inherit_hr_write() -> None:
    result = decision(
        business_role="tenant_hr_director",
        auth_roles=(
            "ENTERPRISE_ADMIN",
        ),
    )

    assert result.authorized is False
    assert (
        result.reason
        is TenantAuthorizationReason.PERMISSION_NOT_GRANTED
    )


@pytest.mark.parametrize(
    "business_role",
    (
        "tenant_hr_business_partner",
        "tenant_hr_generalist",
        "tenant_line_manager",
        "tenant_department_manager",
        "tenant_employee",
        "tenant_payroll_director",
        "tenant_payroll_manager",
        "tenant_payroll_administrator",
    ),
)
def test_excluded_hr_business_roles_deny_even_with_hr_director_assignment(
    business_role: str,
) -> None:
    result = decision(
        business_role=business_role,
        auth_roles=(
            "HR_DIRECTOR",
        ),
    )

    assert result.authorized is False
    assert (
        result.reason
        is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    )


def test_crossed_permission_operation_pair_fails_closed() -> None:
    result = decision(
        business_role="tenant_hr_director",
        auth_roles=(
            "HR_DIRECTOR",
        ),
        permission="tenant:profile:read",
        operation=OPERATION,
    )

    assert result.authorized is False
    assert (
        result.reason
        is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    )


def test_financial_execution_remains_prohibited() -> None:
    result = decision(
        business_role="tenant_hr_director",
        auth_roles=(
            "HR_DIRECTOR",
        ),
        operation="financial_execution",
    )

    assert result.authorized is False
    assert (
        result.reason
        is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED
    )

# ARTIFACT: tests/unit/test_hr_employee_relation_write_iam.py
# VERSION: v1.0.0-P0-C12E4B3B-HR-EMPLOYEE-RELATION-WRITE-IAM-CERT
# AUTHORITY BOUNDARY: direct IAM certification only; no HTTP, persistence, payroll or financial execution authority
# TENANT POSTURE: exact ACTIVE principal, ACTIVE membership, eligible HR business role, exact permission-operation pair and ACTIVE granting role required
# FAIL-CLOSED POSTURE: unknown, excluded, missing, crossed, inactive, projected and financial paths deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
