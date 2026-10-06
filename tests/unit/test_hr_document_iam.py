"""WILSY OS HR Document IAM Direct Certificate.

TITLE: HR Document IAM Direct Certificate
VERSION: v1.0.0-P0-C12F7B-HR-DOCUMENT-IAM-CERT
AUTHORITY: Direct certification of sensitivity-specific own-tenant HR document authorization.

PURPOSE:
Freeze fourteen exact HR document permission-operation contracts across the
seven certified HrDocumentSensitivity classes without granting generic,
cross-sensitivity or role-family-derived document authority.

EPITOME:
ACTIVE PRINCIPAL
+ ACTIVE EXACT TENANT MEMBERSHIP
+ EXACT ELIGIBLE HR BUSINESS ROLE
+ EXACT SENSITIVITY-SPECIFIC OPERATION/PERMISSION
+ ACTIVE SINGLE-PURPOSE AUTHORIZATION ROLE
-> AUTHORIZED

AUTHORITY BOUNDARY:
IAM composition only. This certificate creates no HTTP route, document
business truth, provider authority, deletion authority, retention/disposal
execution, payroll payment, billing, settlement or financial execution.

PRIVACY BOUNDARY:
Highly-sensitive health and identity permissions remain narrower than broad
HR leadership. Job title, manager relationship, HRIS administration, tenant
ownership and system administration never imply HR document access.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_iam.py

CERTIFICATION / UPDATE DATE: 2026-10-05
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pytest

import tools.eos.auth.tenant_authorization as ta

from tools.eos.auth.hr_business_role_catalog import (
    ALL_HR_BUSINESS_ROLES,
)
from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    canonical_permissions,
    permission_metadata,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)
from tools.eos.auth.role_assignment import (
    RoleAssignmentStatus,
)
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
    SystemAuthorityClassification,
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


VERSION = (
    "v1.0.0-P0-C12F7B-"
    "HR-DOCUMENT-IAM-CERT"
)


MATRIX = {

    "hr_document_standard_employment_write": {
        "permission":
            "hr:document:standard_employment:write",
        "auth_role":
            "HR_DOCUMENT_STANDARD_EMPLOYMENT_WRITE",
        "roles": frozenset({
            "tenant_hr_administrator",
            "tenant_hr_director",
            "tenant_hr_manager",
            "tenant_onboarding_coordinator",
            "tenant_onboarding_manager",
            "tenant_personnel_administrator",
        }),
    },

    "hr_document_standard_employment_read": {
        "permission":
            "hr:document:standard_employment:read",
        "auth_role":
            "HR_DOCUMENT_STANDARD_EMPLOYMENT_READ",
        "roles": frozenset({
            "tenant_hr_administrator",
            "tenant_hr_business_partner",
            "tenant_hr_data_steward",
            "tenant_hr_director",
            "tenant_hr_generalist",
            "tenant_hr_manager",
            "tenant_hr_specialist",
            "tenant_offboarding_administrator",
            "tenant_onboarding_coordinator",
            "tenant_onboarding_manager",
            "tenant_personnel_administrator",
        }),
    },

    "hr_document_employee_relations_restricted_write": {
        "permission":
            "hr:document:employee_relations_restricted:write",
        "auth_role":
            "HR_DOCUMENT_EMPLOYEE_RELATIONS_RESTRICTED_WRITE",
        "roles": frozenset({
            "tenant_employee_relations_director",
            "tenant_employee_relations_manager",
            "tenant_employee_relations_specialist",
            "tenant_hr_director",
            "tenant_hr_manager",
        }),
    },

    "hr_document_employee_relations_restricted_read": {
        "permission":
            "hr:document:employee_relations_restricted:read",
        "auth_role":
            "HR_DOCUMENT_EMPLOYEE_RELATIONS_RESTRICTED_READ",
        "roles": frozenset({
            "tenant_disciplinary_case_manager",
            "tenant_disciplinary_outcome_approver",
            "tenant_employee_relations_director",
            "tenant_employee_relations_manager",
            "tenant_employee_relations_specialist",
            "tenant_grievance_manager",
            "tenant_hr_director",
            "tenant_hr_investigator",
            "tenant_hr_manager",
            "tenant_labour_relations_manager",
            "tenant_labour_relations_specialist",
        }),
    },

    "hr_document_performance_restricted_write": {
        "permission":
            "hr:document:performance_restricted:write",
        "auth_role":
            "HR_DOCUMENT_PERFORMANCE_RESTRICTED_WRITE",
        "roles": frozenset({
            "tenant_hr_director",
            "tenant_hr_manager",
            "tenant_performance_director",
            "tenant_performance_manager",
            "tenant_performance_specialist",
        }),
    },

    "hr_document_performance_restricted_read": {
        "permission":
            "hr:document:performance_restricted:read",
        "auth_role":
            "HR_DOCUMENT_PERFORMANCE_RESTRICTED_READ",
        "roles": frozenset({
            "tenant_hr_business_partner",
            "tenant_hr_director",
            "tenant_hr_manager",
            "tenant_performance_director",
            "tenant_performance_manager",
            "tenant_performance_specialist",
        }),
    },

    "hr_document_highly_sensitive_health_write": {
        "permission":
            "hr:document:highly_sensitive_health:write",
        "auth_role":
            "HR_DOCUMENT_HIGHLY_SENSITIVE_HEALTH_WRITE",
        "roles": frozenset({
            "tenant_health_safety_director",
            "tenant_health_safety_manager",
            "tenant_health_safety_officer",
            "tenant_occupational_health_administrator",
        }),
    },

    "hr_document_highly_sensitive_health_read": {
        "permission":
            "hr:document:highly_sensitive_health:read",
        "auth_role":
            "HR_DOCUMENT_HIGHLY_SENSITIVE_HEALTH_READ",
        "roles": frozenset({
            "tenant_health_safety_director",
            "tenant_health_safety_manager",
            "tenant_health_safety_officer",
            "tenant_occupational_health_administrator",
            "tenant_people_privacy_officer",
        }),
    },

    "hr_document_highly_sensitive_identity_write": {
        "permission":
            "hr:document:highly_sensitive_identity:write",
        "auth_role":
            "HR_DOCUMENT_HIGHLY_SENSITIVE_IDENTITY_WRITE",
        "roles": frozenset({
            "tenant_global_mobility_manager",
            "tenant_global_mobility_specialist",
            "tenant_immigration_administrator",
            "tenant_onboarding_coordinator",
            "tenant_onboarding_manager",
        }),
    },

    "hr_document_highly_sensitive_identity_read": {
        "permission":
            "hr:document:highly_sensitive_identity:read",
        "auth_role":
            "HR_DOCUMENT_HIGHLY_SENSITIVE_IDENTITY_READ",
        "roles": frozenset({
            "tenant_global_mobility_manager",
            "tenant_global_mobility_specialist",
            "tenant_immigration_administrator",
            "tenant_onboarding_coordinator",
            "tenant_onboarding_manager",
            "tenant_people_privacy_officer",
        }),
    },

    "hr_document_separation_restricted_write": {
        "permission":
            "hr:document:separation_restricted:write",
        "auth_role":
            "HR_DOCUMENT_SEPARATION_RESTRICTED_WRITE",
        "roles": frozenset({
            "tenant_employee_relations_director",
            "tenant_employee_relations_manager",
            "tenant_employee_relations_specialist",
            "tenant_hr_director",
            "tenant_hr_manager",
            "tenant_offboarding_administrator",
        }),
    },

    "hr_document_separation_restricted_read": {
        "permission":
            "hr:document:separation_restricted:read",
        "auth_role":
            "HR_DOCUMENT_SEPARATION_RESTRICTED_READ",
        "roles": frozenset({
            "tenant_employee_relations_director",
            "tenant_employee_relations_manager",
            "tenant_employee_relations_specialist",
            "tenant_hr_business_partner",
            "tenant_hr_director",
            "tenant_hr_generalist",
            "tenant_hr_manager",
            "tenant_offboarding_administrator",
        }),
    },

    "hr_document_general_write": {
        "permission":
            "hr:document:general:write",
        "auth_role":
            "HR_DOCUMENT_GENERAL_WRITE",
        "roles": frozenset({
            "tenant_hr_administrator",
            "tenant_hr_director",
            "tenant_hr_manager",
            "tenant_personnel_administrator",
        }),
    },

    "hr_document_general_read": {
        "permission":
            "hr:document:general:read",
        "auth_role":
            "HR_DOCUMENT_GENERAL_READ",
        "roles": frozenset({
            "tenant_hr_administrator",
            "tenant_hr_analyst",
            "tenant_hr_business_partner",
            "tenant_hr_director",
            "tenant_hr_generalist",
            "tenant_hr_manager",
            "tenant_hr_specialist",
            "tenant_personnel_administrator",
        }),
    },
}


PERMISSIONS = frozenset(
    row[
        "permission"
    ]
    for row in MATRIX.values()
)

AUTH_ROLES = frozenset(
    row[
        "auth_role"
    ]
    for row in MATRIX.values()
)

PID = "principal-hr-document-iam"
TENANT = "tenant-hr-document-iam"


@dataclass(
    frozen=True,
    slots=True,
)
class StatusRecord:
    status: object


class PrincipalRepository:
    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> object:
        del session

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
        del session

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
        del session

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
        del session

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
    permission: str,
    operation: str,
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


def test_exact_fourteen_permissions_are_present_in_canonical_namespace() -> None:
    rows = json.loads(
        canonical_permissions()
    )

    ids = {
        row[
            "permission_id"
        ]
        for row in rows
    }

    missing = (
        PERMISSIONS
        - ids
    )

    assert not missing, (
        "P0_C12F7B_EXPECTED_14_HR_DOCUMENT_PERMISSIONS_MISSING:"
        + ",".join(
            sorted(
                missing
            )
        )
    )

    assert len(
        [
            row
            for row in rows
            if row[
                "disposition"
            ] == "CANONICAL"
        ]
    ) == 87

    assert len(
        rows
    ) == 90


def test_each_permission_has_exact_non_financial_tenant_metadata() -> None:
    for permission in PERMISSIONS:
        metadata = permission_metadata(
            permission
        )

        assert (
            metadata.permission_id
            == permission
        )

        assert metadata.namespace == "TENANT"
        assert metadata.scope_kind == "TENANT"

        assert (
            metadata.tenant_membership_required
            is True
        )

        assert (
            metadata.system_assignment_required
            is False
        )

        assert (
            metadata.cross_tenant_capable
            is False
        )

        assert (
            metadata.financial_execution_capable
            is False
        )

        assert (
            metadata.authorizes_by_itself
            is False
        )

        assert (
            metadata.deprecated_or_legacy
            is False
        )

        assert (
            metadata.disposition
            is PermissionDisposition.CANONICAL
        )


def test_all_101_hr_roles_remain_canonical_vocabulary() -> None:
    assert len(
        ALL_HR_BUSINESS_ROLES
    ) == 101


def test_exact_fourteen_single_purpose_authorization_roles_exist() -> None:
    assert len(
        AUTH_ROLES
    ) == 14

    for operation, row in MATRIX.items():
        del operation

        permission = row[
            "permission"
        ]

        auth_role = row[
            "auth_role"
        ]

        assert (
            get_roles_granting_permission(
                permission
            )
            == (
                auth_role,
            )
        )

        assert (
            ROLE_PERMISSIONS_MAP[
                auth_role
            ]
            == [
                permission
            ]
        )


def test_all_fourteen_operation_permission_bindings_are_exact() -> None:
    for operation, row in MATRIX.items():
        permission = row[
            "permission"
        ]

        assert operation in OPERATIONS

        assert (
            permission_for_business_role_operation(
                operation
            )
            == permission
        )

        assert (
            ta._BINDINGS[
                operation
            ]
            == permission
        )

        assert (
            list(
                ta._BINDINGS
            ).count(
                operation
            )
            == 1
        )


def test_each_operation_has_exact_explicit_business_role_eligibility() -> None:
    for operation, row in MATRIX.items():
        allowed = row[
            "roles"
        ]

        assert isinstance(
            allowed,
            frozenset,
        )

        assert (
            allowed
            <= ALL_HR_BUSINESS_ROLES
        )

        for role in ALL_HR_BUSINESS_ROLES:
            expected = (
                ELIGIBLE
                if role in allowed
                else DENY
            )

            assert (
                tenant_role_operation_eligibility(
                    role,
                    operation,
                )
                == expected
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
def test_non_hr_business_roles_receive_no_hr_document_eligibility(
    role: str,
) -> None:
    for operation in MATRIX:
        assert (
            tenant_role_operation_eligibility(
                role,
                operation,
            )
            == DENY
        )


@pytest.mark.parametrize(
    "role",
    (
        "tenant_employee",
        "tenant_line_manager",
        "tenant_department_manager",
        "tenant_team_lead",
        "tenant_executive_manager",
        "tenant_hris_director",
        "tenant_hris_manager",
        "tenant_hris_administrator",
        "tenant_payroll_director",
        "tenant_payroll_manager",
        "tenant_payroll_administrator",
        "tenant_payroll_processor",
        "tenant_payroll_reviewer",
        "tenant_payroll_auditor",
        "tenant_external_hr_auditor",
    ),
)
def test_explicitly_deferred_hr_roles_remain_denied_for_all_document_operations(
    role: str,
) -> None:
    assert role in ALL_HR_BUSINESS_ROLES

    for operation in MATRIX:
        assert (
            tenant_role_operation_eligibility(
                role,
                operation,
            )
            == DENY
        )


def test_highly_sensitive_permissions_exclude_broad_hr_leadership() -> None:
    sensitive_operations = (
        "hr_document_highly_sensitive_health_read",
        "hr_document_highly_sensitive_health_write",
        "hr_document_highly_sensitive_identity_read",
        "hr_document_highly_sensitive_identity_write",
    )

    broad_roles = (
        "tenant_hr_director",
        "tenant_hr_manager",
        "tenant_hr_business_partner",
        "tenant_hr_generalist",
    )

    for operation in sensitive_operations:
        for role in broad_roles:
            assert (
                tenant_role_operation_eligibility(
                    role,
                    operation,
                )
                == DENY
            )


def test_every_hr_document_operation_is_non_system() -> None:
    for operation in MATRIX:
        assert (
            requires_system_authority(
                operation
            )
            is
            SystemAuthorityClassification
            .SYSTEM_NOT_INHERENTLY_REQUIRED
        )


def test_full_current_truth_authorizes_every_certified_business_role_pair() -> None:
    for operation, row in MATRIX.items():
        permission = row[
            "permission"
        ]

        auth_role = row[
            "auth_role"
        ]

        for business_role in row[
            "roles"
        ]:
            result = decision(
                business_role=business_role,
                auth_roles=(
                    auth_role,
                ),
                permission=permission,
                operation=operation,
            )

            assert result == (
                TenantAuthorizationDecision(
                    True,
                    TenantAuthorizationReason.AUTHORIZED,
                    business_role,
                    auth_role,
                )
            )


def test_eligible_business_role_without_active_auth_grant_denies() -> None:
    for operation, row in MATRIX.items():
        business_role = next(
            iter(
                row[
                    "roles"
                ]
            )
        )

        result = decision(
            business_role=business_role,
            auth_roles=(),
            permission=row[
                "permission"
            ],
            operation=operation,
        )

        assert result.authorized is False

        assert (
            result.reason
            is
            TenantAuthorizationReason
            .PERMISSION_NOT_GRANTED
        )


def test_ineligible_business_role_denies_even_with_exact_auth_role() -> None:
    for operation, row in MATRIX.items():
        result = decision(
            business_role="tenant_employee",
            auth_roles=(
                row[
                    "auth_role"
                ],
            ),
            permission=row[
                "permission"
            ],
            operation=operation,
        )

        assert result.authorized is False

        assert (
            result.reason
            is
            TenantAuthorizationReason
            .BUSINESS_ROLE_INELIGIBLE
        )


def test_crossed_permission_operation_pairs_fail_closed() -> None:
    operations = sorted(
        MATRIX
    )

    first = operations[
        0
    ]

    second = operations[
        1
    ]

    first_row = MATRIX[
        first
    ]

    second_row = MATRIX[
        second
    ]

    business_role = next(
        iter(
            first_row[
                "roles"
            ]
        )
    )

    result = decision(
        business_role=business_role,
        auth_roles=(
            first_row[
                "auth_role"
            ],
        ),
        permission=second_row[
            "permission"
        ],
        operation=first,
    )

    assert result.authorized is False

    assert (
        result.reason
        is
        TenantAuthorizationReason
        .PERMISSION_OPERATION_MISMATCH
    )


def test_enterprise_admin_static_role_does_not_inherit_hr_document_access() -> None:
    for operation, row in MATRIX.items():
        business_role = next(
            iter(
                row[
                    "roles"
                ]
            )
        )

        result = decision(
            business_role=business_role,
            auth_roles=(
                "ENTERPRISE_ADMIN",
            ),
            permission=row[
                "permission"
            ],
            operation=operation,
        )

        assert result.authorized is False

        assert (
            result.reason
            is
            TenantAuthorizationReason
            .PERMISSION_NOT_GRANTED
        )


def test_no_permission_is_generic_hr_document_read_or_write() -> None:
    assert (
        "hr:document:read"
        not in PERMISSIONS
    )

    assert (
        "hr:document:write"
        not in PERMISSIONS
    )

    assert all(
        permission.count(
            ":"
        ) == 3
        for permission in PERMISSIONS
    )


def test_document_iam_surface_does_not_create_financial_execution() -> None:
    assert all(
        not permission.startswith(
            (
                "billing:",
                "payment:",
                "settlement:",
                "execution:",
            )
        )
        for permission in PERMISSIONS
    )


# ARTIFACT: tests/unit/test_hr_document_iam.py
# VERSION: v1.0.0-P0-C12F7B-HR-DOCUMENT-IAM-CERT
# PERMISSIONS: fourteen sensitivity-specific own-tenant permissions
# OPERATIONS: fourteen exact read/write operation bindings
# BUSINESS ROLE ELIGIBILITY: explicit subsets of the 101-role HR canon only
# AUTHORIZATION ROLES: fourteen single-purpose static grant roles
# GENERIC HR DOCUMENT PERMISSION: prohibited
# EMPLOYEE SELF ACCESS: deferred
# MANAGER ACCESS: deferred
# HRIS ADMIN CONTENT ACCESS: deferred
# PAYROLL DOCUMENT ACCESS: deferred
# EXTERNAL AUDITOR ACCESS: deferred
# PROVIDER DELETE AUTHORITY: none
# RETENTION / DISPOSAL EXECUTION AUTHORITY: none
# IAM / HTTP COMPOSITION: IAM only; no HTTP route created here
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
