"""TITLE: Tenant Authorization Composition Certification.
VERSION: v1.1.0-TENANT-AUTHORIZATION-COMPOSITION-CERT
AUTHORITY: Certification of read-only current-truth tenant authorization composition.
EPITOME: Proves migrated tenant permission grants remain conjunctive with principal, membership, business-role, and durable final-role truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_authorization.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.1.0 migrates the certificate from deliberately ungranted tenant permissions to the governed ENTERPRISE_ADMIN/AUDITOR tenant-permission grant matrix while preserving fail-closed gate precedence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Deterministic resolve-only readers; projected transport authority cannot grant; mutation tripwires remain armed.
TENANT BOUNDARY: Exact principal and tenant scope, ACTIVE membership, one eligible tenant business role, and an ACTIVE granting authorization role are conjunctively required.
AUTHORITY BOUNDARY: Certifies the frozen composition against migrated role-definition policy; tests do not authorize by themselves, wire routes, or own persistence.
FINANCIAL AUTHORITY BOUNDARY: Financial execution remains prohibited; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import pytest

import tools.eos.auth.tenant_authorization as ta
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepositoryError,
)

VERSION = "v1.1.0-TENANT-AUTHORIZATION-COMPOSITION-CERT"

_PID = "p"
_TENANT = "t"


@dataclass(frozen=True, slots=True)
class _StatusRecord:
    """Minimal immutable authority-shaped record for status-gate certification."""

    status: object


class _PrincipalReader:
    """Resolve-only principal reader with explicit mutation tripwires."""

    def __init__(self, value: object, *, outage: bool = False) -> None:
        self.value = value
        self.outage = outage
        self.calls: list[str] = []
        self.write_calls = 0

    def resolve(self, principal_id: str) -> object:
        self.calls.append(principal_id)
        if self.outage:
            raise PrincipalAuthorityRepositoryError("outage")
        if principal_id != _PID:
            raise PrincipalAuthorityNotFoundError("missing")
        return self.value

    def _write_forbidden(self, *_args: object, **_kwargs: object) -> None:
        self.write_calls += 1
        pytest.fail("tenant authorization attempted principal mutation")

    create = _write_forbidden
    insert = _write_forbidden
    update = _write_forbidden
    replace = _write_forbidden
    compare_and_swap = _write_forbidden
    delete = _write_forbidden
    archive = _write_forbidden


class _MembershipReader:
    """Resolve-only membership reader with explicit mutation tripwires."""

    def __init__(self, value: object, *, outage: bool = False) -> None:
        self.value = value
        self.outage = outage
        self.calls: list[tuple[str, str]] = []
        self.write_calls = 0

    def resolve(self, principal_id: str, tenant_id: str) -> object:
        self.calls.append((principal_id, tenant_id))
        if self.outage:
            raise TenantMembershipRepositoryError("outage")
        if (principal_id, tenant_id) != (_PID, _TENANT):
            raise TenantMembershipNotFoundError("missing")
        return self.value

    def _write_forbidden(self, *_args: object, **_kwargs: object) -> None:
        self.write_calls += 1
        pytest.fail("tenant authorization attempted membership mutation")

    create = _write_forbidden
    insert = _write_forbidden
    update = _write_forbidden
    replace = _write_forbidden
    compare_and_swap = _write_forbidden
    delete = _write_forbidden
    archive = _write_forbidden


class _AssignmentReader:
    """Resolve-only assignment reader with explicit outage and mutation controls."""

    def __init__(
        self,
        values: dict[tuple[str, str, str], object] | None = None,
        *,
        outage_keys: set[tuple[str, str, str]] | None = None,
    ) -> None:
        self.values = dict(values or {})
        self.outage_keys = set(outage_keys or set())
        self.calls: list[tuple[str, str, str]] = []
        self.write_calls = 0

    def resolve(self, principal_id: str, tenant_id: str, role_id: str) -> object:
        key = (principal_id, tenant_id, role_id)
        self.calls.append(key)
        if key in self.outage_keys:
            raise RoleAssignmentRepositoryError("outage")
        if key not in self.values:
            raise RoleAssignmentNotFoundError("missing")
        return self.values[key]

    def _write_forbidden(self, *_args: object, **_kwargs: object) -> None:
        self.write_calls += 1
        pytest.fail("tenant authorization attempted role-assignment mutation")

    create = _write_forbidden
    insert = _write_forbidden
    update = _write_forbidden
    replace = _write_forbidden
    replace_one = _write_forbidden
    compare_and_swap = _write_forbidden
    delete = _write_forbidden
    delete_one = _write_forbidden
    archive = _write_forbidden
    grant = _write_forbidden
    revoke = _write_forbidden


def _principal(*, status: PrincipalStatus = PrincipalStatus.ACTIVE, outage: bool = False) -> _PrincipalReader:
    return _PrincipalReader(_StatusRecord(status), outage=outage)


def _membership(
    *,
    status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    outage: bool = False,
) -> _MembershipReader:
    return _MembershipReader(_StatusRecord(status), outage=outage)


def _business(role: str) -> _AssignmentReader:
    return _AssignmentReader(
        {(_PID, _TENANT, role): _StatusRecord(RoleAssignmentStatus.ACTIVE)}
    )


def _assignments(
    *active_roles: str,
    revoked_roles: tuple[str, ...] = (),
    outage_roles: tuple[str, ...] = (),
) -> _AssignmentReader:
    values: dict[tuple[str, str, str], object] = {
        (_PID, _TENANT, role): _StatusRecord(RoleAssignmentStatus.ACTIVE)
        for role in active_roles
    }
    values.update(
        {
            (_PID, _TENANT, role): _StatusRecord(RoleAssignmentStatus.REVOKED)
            for role in revoked_roles
        }
    )
    return _AssignmentReader(
        values,
        outage_keys={(_PID, _TENANT, role) for role in outage_roles},
    )


def _decision(
    *,
    permission_id: object,
    operation: object,
    business_repository: _AssignmentReader,
    assignment_repository: _AssignmentReader,
    principal_repository: _PrincipalReader | None = None,
    membership_repository: _MembershipReader | None = None,
    principal_id: object = _PID,
    tenant_id: object = _TENANT,
) -> TenantAuthorizationDecision:
    return authorize_tenant_operation(
        principal_id=principal_id,
        tenant_id=tenant_id,
        permission_id=permission_id,
        operation=operation,
        principal_repository=principal_repository or _principal(),
        membership_repository=membership_repository or _membership(),
        business_role_repository=business_repository,
        role_assignment_repository=assignment_repository,
    )


def test_existing_audit_authorization_remains_green() -> None:
    """The pre-migration AUDITOR audit grant remains a real positive composition."""

    result = _decision(
        permission_id="audit:read",
        operation="audit_read",
        business_repository=_business("tenant_auditor"),
        assignment_repository=_assignments("AUDITOR"),
    )
    assert result == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_auditor",
        "AUDITOR",
    )


@pytest.mark.parametrize(
    ("business_role", "authorization_role", "permission_id", "operation"),
    (
        ("tenant_auditor", "AUDITOR", "tenant:profile:read", "profile_read"),
        ("tenant_auditor", "AUDITOR", "tenant:membership:read", "membership_read"),
        (
            "tenant_auditor",
            "AUDITOR",
            "tenant:role_assignment:read",
            "role_assignment_read",
        ),
        ("tenant_owner", "ENTERPRISE_ADMIN", "tenant:profile:write", "profile_update"),
        (
            "tenant_owner",
            "ENTERPRISE_ADMIN",
            "tenant:lifecycle:archive",
            "lifecycle_archive",
        ),
        (
            "tenant_admin",
            "ENTERPRISE_ADMIN",
            "tenant:membership:write",
            "membership_invite",
        ),
        (
            "tenant_admin",
            "ENTERPRISE_ADMIN",
            "tenant:role_assignment:write",
            "role_grant",
        ),
    ),
)
def test_migrated_tenant_permission_grants_authorize_only_with_full_current_truth(
    business_role: str,
    authorization_role: str,
    permission_id: str,
    operation: str,
) -> None:
    """Each migrated grant succeeds only through the frozen conjunctive composition."""

    result = _decision(
        permission_id=permission_id,
        operation=operation,
        business_repository=_business(business_role),
        assignment_repository=_assignments(authorization_role),
    )
    assert result.authorized is True
    assert result.reason is TenantAuthorizationReason.AUTHORIZED
    assert result.business_role == business_role
    assert result.authorization_role == authorization_role


@pytest.mark.parametrize("authorization_role", ("AUDITOR", "ENTERPRISE_ADMIN"))
def test_profile_read_real_multigrant_accepts_each_explicit_granting_role(
    authorization_role: str,
) -> None:
    """A read permission may be satisfied by either explicitly configured final role."""

    assignments = _assignments(authorization_role)
    result = _decision(
        permission_id="tenant:profile:read",
        operation="profile_read",
        business_repository=_business("tenant_auditor"),
        assignment_repository=assignments,
    )
    assert result.authorized is True
    assert result.reason is TenantAuthorizationReason.AUTHORIZED
    assert result.authorization_role == authorization_role
    assert set(assignments.calls) == {
        (_PID, _TENANT, "AUDITOR"),
        (_PID, _TENANT, "ENTERPRISE_ADMIN"),
    }


@pytest.mark.parametrize(
    ("business_role", "authorization_role", "permission_id", "operation"),
    (
        (
            "tenant_manager",
            "ENTERPRISE_ADMIN",
            "tenant:profile:write",
            "profile_update",
        ),
        (
            "tenant_admin",
            "ENTERPRISE_ADMIN",
            "tenant:lifecycle:archive",
            "lifecycle_archive",
        ),
        ("tenant_auditor", "AUDITOR", "tenant:profile:write", "profile_update"),
        (
            "tenant_owner",
            "ENTERPRISE_ADMIN",
            "tenant:role_assignment:write",
            "role_grant",
        ),
    ),
)
def test_final_permission_grants_do_not_override_business_role_eligibility(
    business_role: str,
    authorization_role: str,
    permission_id: str,
    operation: str,
) -> None:
    """A broad final-role grant cannot bypass the narrower tenant business policy."""

    assignments = _assignments(authorization_role)
    result = _decision(
        permission_id=permission_id,
        operation=operation,
        business_repository=_business(business_role),
        assignment_repository=assignments,
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    assert result.business_role == business_role
    assert result.authorization_role is None
    assert assignments.calls == []


def test_missing_granting_assignment_is_permission_not_granted() -> None:
    """Canonical permission plus eligible business role is insufficient without final assignment."""

    assignments = _assignments()
    result = _decision(
        permission_id="tenant:profile:write",
        operation="profile_update",
        business_repository=_business("tenant_owner"),
        assignment_repository=assignments,
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED
    assert assignments.calls == [(_PID, _TENANT, "ENTERPRISE_ADMIN")]


def test_revoked_granting_assignment_is_distinct() -> None:
    """A present but revoked final assignment remains distinguishable from absence."""

    result = _decision(
        permission_id="tenant:profile:write",
        operation="profile_update",
        business_repository=_business("tenant_owner"),
        assignment_repository=_assignments(revoked_roles=("ENTERPRISE_ADMIN",)),
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE


def test_final_role_repository_outage_remains_unavailable() -> None:
    """A final-role repository outage cannot degrade to an ordinary permission denial."""

    result = _decision(
        permission_id="tenant:profile:write",
        operation="profile_update",
        business_repository=_business("tenant_owner"),
        assignment_repository=_assignments(outage_roles=("ENTERPRISE_ADMIN",)),
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE


def test_real_multigrant_outage_dominates_an_active_grant() -> None:
    """All granting roles are evaluated; an outage remains fail-closed even after one active grant."""

    assignments = _assignments("AUDITOR", outage_roles=("ENTERPRISE_ADMIN",))
    result = _decision(
        permission_id="tenant:profile:read",
        operation="profile_read",
        business_repository=_business("tenant_auditor"),
        assignment_repository=assignments,
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE
    assert assignments.calls == [
        (_PID, _TENANT, "AUDITOR"),
        (_PID, _TENANT, "ENTERPRISE_ADMIN"),
    ]


def test_invalid_input_precedes_all_authority_reads() -> None:
    """Malformed principal or tenant scope performs zero durable-authority reads."""

    for field, values in (
        ("principal_id", ("", " ", " p", "p ", None, 123)),
        ("tenant_id", ("", " ", " t", "t ", None, 123)),
    ):
        for value in values:
            principal = _principal()
            membership = _membership()
            business = _business("tenant_auditor")
            assignments = _assignments("AUDITOR")
            kwargs: dict[str, object] = {
                "principal_id": _PID,
                "tenant_id": _TENANT,
            }
            kwargs[field] = value
            result = _decision(
                principal_id=kwargs["principal_id"],
                tenant_id=kwargs["tenant_id"],
                permission_id="audit:read",
                operation="audit_read",
                principal_repository=principal,
                membership_repository=membership,
                business_repository=business,
                assignment_repository=assignments,
            )
            assert result.reason is TenantAuthorizationReason.INVALID_INPUT
            assert principal.calls == []
            assert membership.calls == []
            assert business.calls == []
            assert assignments.calls == []


def test_principal_failures_short_circuit_downstream_authority() -> None:
    """Missing, inactive, and unavailable principal truth fail before tenant authority."""

    missing_principal = _principal()
    membership = _membership()
    business = _business("tenant_auditor")
    assignments = _assignments("AUDITOR")
    result = _decision(
        principal_id="other",
        tenant_id=_TENANT,
        permission_id="audit:read",
        operation="audit_read",
        principal_repository=missing_principal,
        membership_repository=membership,
        business_repository=business,
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.PRINCIPAL_NOT_FOUND
    assert membership.calls == []
    assert business.calls == []
    assert assignments.calls == []

    inactive = _principal(status=PrincipalStatus.SUSPENDED)
    membership = _membership()
    business = _business("tenant_auditor")
    assignments = _assignments("AUDITOR")
    result = _decision(
        permission_id="audit:read",
        operation="audit_read",
        principal_repository=inactive,
        membership_repository=membership,
        business_repository=business,
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE
    assert membership.calls == []
    assert business.calls == []
    assert assignments.calls == []

    outage = _principal(outage=True)
    membership = _membership()
    business = _business("tenant_auditor")
    assignments = _assignments("AUDITOR")
    result = _decision(
        permission_id="audit:read",
        operation="audit_read",
        principal_repository=outage,
        membership_repository=membership,
        business_repository=business,
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE
    assert membership.calls == []
    assert business.calls == []
    assert assignments.calls == []


def test_membership_failures_short_circuit_role_authority() -> None:
    """Missing, inactive, and unavailable membership truth fail before role lookup."""

    principal = _principal()
    membership = _membership()
    business = _business("tenant_auditor")
    assignments = _assignments("AUDITOR")
    result = _decision(
        tenant_id="other",
        permission_id="audit:read",
        operation="audit_read",
        principal_repository=principal,
        membership_repository=membership,
        business_repository=business,
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND
    assert business.calls == []
    assert assignments.calls == []

    for status in (TenantMembershipStatus.SUSPENDED, TenantMembershipStatus.REVOKED):
        membership = _membership(status=status)
        business = _business("tenant_auditor")
        assignments = _assignments("AUDITOR")
        result = _decision(
            permission_id="audit:read",
            operation="audit_read",
            membership_repository=membership,
            business_repository=business,
            assignment_repository=assignments,
        )
        assert result.reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE
        assert business.calls == []
        assert assignments.calls == []

    membership = _membership(outage=True)
    business = _business("tenant_auditor")
    assignments = _assignments("AUDITOR")
    result = _decision(
        permission_id="audit:read",
        operation="audit_read",
        membership_repository=membership,
        business_repository=business,
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE
    assert business.calls == []
    assert assignments.calls == []


def test_business_role_absence_ambiguity_and_outage_fail_closed() -> None:
    """Business-role current truth remains exactly-one and fail-closed."""

    assignments = _assignments("AUDITOR")
    absent = _AssignmentReader()
    result = _decision(
        permission_id="audit:read",
        operation="audit_read",
        business_repository=absent,
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE
    assert assignments.calls == []

    assignments = _assignments("AUDITOR")
    ambiguous = _AssignmentReader(
        {
            (_PID, _TENANT, "tenant_owner"): _StatusRecord(RoleAssignmentStatus.ACTIVE),
            (_PID, _TENANT, "tenant_admin"): _StatusRecord(RoleAssignmentStatus.ACTIVE),
        }
    )
    result = _decision(
        permission_id="audit:read",
        operation="audit_read",
        business_repository=ambiguous,
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES
    assert assignments.calls == []

    assignments = _assignments("AUDITOR")
    business_outage = _AssignmentReader(
        outage_keys={(_PID, _TENANT, "tenant_auditor")}
    )
    result = _decision(
        permission_id="audit:read",
        operation="audit_read",
        business_repository=business_outage,
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE
    assert assignments.calls == []


@pytest.mark.parametrize(
    ("permission_id", "expected_reason"),
    (
        ("admin:all", TenantAuthorizationReason.PERMISSION_NOT_CANONICAL),
        ("execution:trigger", TenantAuthorizationReason.PERMISSION_NOT_CANONICAL),
        ("tenant:manage", TenantAuthorizationReason.PERMISSION_NOT_CANONICAL),
        ("kernel:read", TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH),
        ("governance:read", TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH),
        ("tenant:*", TenantAuthorizationReason.PERMISSION_UNKNOWN),
        ("tenant:all", TenantAuthorizationReason.PERMISSION_UNKNOWN),
        ("unknown", TenantAuthorizationReason.PERMISSION_UNKNOWN),
        (" tenant:profile:read", TenantAuthorizationReason.INVALID_INPUT),
        ("tenant:profile:read ", TenantAuthorizationReason.INVALID_INPUT),
    ),
)
def test_permission_namespace_failures_remain_exact(
    permission_id: str,
    expected_reason: TenantAuthorizationReason,
) -> None:
    """Legacy, ambiguous, non-tenant, wildcard-like, and malformed permission IDs deny."""

    assignments = _assignments("AUDITOR", "ENTERPRISE_ADMIN")
    result = _decision(
        permission_id=permission_id,
        operation="audit_read",
        business_repository=_business("tenant_auditor"),
        assignment_repository=assignments,
    )
    assert result.authorized is False
    assert result.reason is expected_reason
    assert assignments.calls == []


def test_permission_operation_binding_remains_exact() -> None:
    """A canonical permission cannot be used under a different tenant operation."""

    assignments = _assignments("ENTERPRISE_ADMIN")
    result = _decision(
        permission_id="tenant:profile:write",
        operation="profile_read",
        business_repository=_business("tenant_owner"),
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    assert assignments.calls == []


@pytest.mark.parametrize(
    "operation",
    ("lifecycle_create", "cross_tenant", "platform_lifecycle"),
)
def test_system_authority_operations_remain_outside_tenant_grants(operation: str) -> None:
    """Tenant permission migration cannot create system/cross-tenant authority."""

    assignments = _assignments("ENTERPRISE_ADMIN")
    result = _decision(
        permission_id="tenant:profile:read",
        operation=operation,
        business_repository=_business("tenant_owner"),
        assignment_repository=assignments,
    )
    assert result.reason is TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED
    assert assignments.calls == []


def test_financial_execution_remains_prohibited_before_final_grant_lookup() -> None:
    """No migrated tenant grant can become financial execution authority."""

    assignments = _assignments("ENTERPRISE_ADMIN", "AUDITOR")
    result = _decision(
        permission_id="tenant:profile:read",
        operation="financial_execution",
        business_repository=_business("tenant_owner"),
        assignment_repository=assignments,
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED
    assert assignments.calls == []


def test_wrong_assignment_scope_cannot_grant() -> None:
    """Final role assignments for another tenant or principal cannot satisfy current scope."""

    wrong_tenant = _AssignmentReader(
        {
            (_PID, "other", "ENTERPRISE_ADMIN"): _StatusRecord(
                RoleAssignmentStatus.ACTIVE
            )
        }
    )
    result = _decision(
        permission_id="tenant:profile:write",
        operation="profile_update",
        business_repository=_business("tenant_owner"),
        assignment_repository=wrong_tenant,
    )
    assert result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    wrong_principal = _AssignmentReader(
        {
            ("other", _TENANT, "ENTERPRISE_ADMIN"): _StatusRecord(
                RoleAssignmentStatus.ACTIVE
            )
        }
    )
    result = _decision(
        permission_id="tenant:profile:write",
        operation="profile_update",
        business_repository=_business("tenant_owner"),
        assignment_repository=wrong_principal,
    )
    assert result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED


def test_malformed_operation_values_fail_closed_before_grant_lookup() -> None:
    """Malformed and unknown operations cannot reach the final grant gate."""

    for operation in ("", " ", "unknown", None, 123):
        assignments = _assignments("AUDITOR", "ENTERPRISE_ADMIN")
        result = _decision(
            permission_id="audit:read",
            operation=operation,
            business_repository=_business("tenant_auditor"),
            assignment_repository=assignments,
        )
        assert result.authorized is False
        assert result.reason is TenantAuthorizationReason.INVALID_INPUT
        assert assignments.calls == []


def test_decisions_are_deterministic_and_immutable() -> None:
    """Repeated identical current truth yields equal immutable decisions."""

    decisions = [
        _decision(
            permission_id="tenant:profile:read",
            operation="profile_read",
            business_repository=_business("tenant_auditor"),
            assignment_repository=_assignments("AUDITOR"),
        )
        for _ in range(3)
    ]
    assert all(decision == decisions[0] for decision in decisions)
    with pytest.raises((AttributeError, TypeError)):
        cast(Any, decisions[0]).authorized = False


def test_operation_binding_is_immutable() -> None:
    """The frozen operation-to-permission binding cannot be changed by callers."""

    with pytest.raises(TypeError):
        cast(Any, ta._BINDINGS)["profile_read"] = "tenant:profile:write"


def test_transport_or_caller_projection_cannot_enter_composition() -> None:
    """Caller/JWT/header roles remain outside the frozen composition signature."""

    with pytest.raises(TypeError):
        cast(Any, authorize_tenant_operation)(
            principal_id=_PID,
            tenant_id=_TENANT,
            permission_id="tenant:profile:read",
            operation="profile_read",
            role="AUDITOR",
            jwt_role="ENTERPRISE_ADMIN",
            permissions=["tenant:profile:write"],
            tenant_header=_TENANT,
            principal_repository=_principal(),
            membership_repository=_membership(),
            business_role_repository=_business("tenant_auditor"),
            role_assignment_repository=_assignments("AUDITOR"),
        )


def test_authorization_is_read_only_across_success_denial_and_financial_paths() -> None:
    """Success, ordinary denial, and financial denial perform no persistence mutation."""

    cases = (
        ("tenant:profile:read", "profile_read", "tenant_auditor", _assignments("AUDITOR")),
        ("tenant:profile:write", "profile_update", "tenant_owner", _assignments()),
        (
            "tenant:profile:read",
            "financial_execution",
            "tenant_owner",
            _assignments("ENTERPRISE_ADMIN"),
        ),
    )
    for permission_id, operation, business_role, assignments in cases:
        principal = _principal()
        membership = _membership()
        business = _business(business_role)
        _decision(
            permission_id=permission_id,
            operation=operation,
            principal_repository=principal,
            membership_repository=membership,
            business_repository=business,
            assignment_repository=assignments,
        )
        assert principal.write_calls == 0
        assert membership.write_calls == 0
        assert business.write_calls == 0
        assert assignments.write_calls == 0


# FORMAL EVIDENCE MAP — executable tests above remain the source of truth.
# 1 positive legacy audit: test_existing_audit_authorization_remains_green
# 2-8 migrated tenant grants: test_migrated_tenant_permission_grants_authorize_only_with_full_current_truth
# 9 real multigrant success: test_profile_read_real_multigrant_accepts_each_explicit_granting_role
# 10-13 business eligibility intersection: test_final_permission_grants_do_not_override_business_role_eligibility
# 14 missing final assignment: test_missing_granting_assignment_is_permission_not_granted
# 15 revoked final assignment: test_revoked_granting_assignment_is_distinct
# 16 final repository outage: test_final_role_repository_outage_remains_unavailable
# 17 multigrant outage precedence: test_real_multigrant_outage_dominates_an_active_grant
# 18 malformed principal/tenant zero-call: test_invalid_input_precedes_all_authority_reads
# 19-21 principal missing/inactive/outage: test_principal_failures_short_circuit_downstream_authority
# 22-25 membership missing/inactive/outage: test_membership_failures_short_circuit_role_authority
# 26-28 business-role absence/multiple/outage: test_business_role_absence_ambiguity_and_outage_fail_closed
# 29 permission/namespace locks: test_permission_namespace_failures_remain_exact
# 30 operation binding: test_permission_operation_binding_remains_exact
# 31 system/cross-tenant lock: test_system_authority_operations_remain_outside_tenant_grants
# 32 financial lock: test_financial_execution_remains_prohibited_before_final_grant_lookup
# 33 final assignment scope: test_wrong_assignment_scope_cannot_grant
# 34 malformed operations: test_malformed_operation_values_fail_closed_before_grant_lookup
# 35 determinism and immutability: test_decisions_are_deterministic_and_immutable
# 36 immutable composition binding: test_operation_binding_is_immutable
# 37 caller/JWT/header non-authority: test_transport_or_caller_projection_cannot_enter_composition
# 38-40 read-only success/denial/financial paths: test_authorization_is_read_only_across_success_denial_and_financial_paths

# ARTIFACT: test_tenant_authorization.py
# VERSION: v1.1.0-TENANT-AUTHORIZATION-COMPOSITION-CERT
# AUTHORITY BOUNDARY: frozen current-truth composition certification only; role grants remain policy, not assignment truth
# TENANT POSTURE: exact active principal, membership, eligible business role, and scoped final assignment are conjunctively required
# FAIL-CLOSED POSTURE: missing, inactive, ambiguous, unavailable, mismatched, projected, cross-tenant, system, and financial paths deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
