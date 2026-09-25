"""TITLE: Tenant Authorization Composition Certification.
VERSION: v1.18.0-L8-8I-CONFLICT-REVIEW-BINDING-CERT
AUTHORITY: Certification of read-only current-truth tenant authorization composition.
EPITOME: Proves migrated tenant permission grants, including WILSY AI
capacity and billing-intelligence evidence reads, remain conjunctive with
principal, membership, business-role, and durable final-role truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_authorization.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-23.
CHANGELOG: 2026-09-25 v1.18.0-L8-8I-CONFLICT-REVIEW-BINDING-CERT
certifies legal_conflict_review_write ->
legal_operations:conflict_review:write as an exact conjunctive authorization
binding for tenant_legal_partner/LEGAL_PARTNER and
tenant_legal_attorney/LEGAL_ATTORNEY only. It proves both authorized pairs,
paralegal and non-legal business-role denial before final-role lookup, exact
permission-operation mismatch rejection, missing/revoked granting-role denial,
and unchanged current-truth/financial/session boundaries.
2026-09-23 v1.17.0-L8-7D4-CLIENT-MATTER-READ-BINDING-CERT
certifies legal_client_matter_read ->
legal_operations:client_matter:read as the exact conjunctive authorization
binding for tenant_legal_client + ACTIVE LEGAL_CLIENT only. It proves exact
success, law-firm/sheriff/deputy/finance denial, crossed permission/operation
denial, missing/revoked LEGAL_CLIENT denial, and unchanged financial-execution
prohibition. ACTIVE client-to-matter visibility remains a later independent
projection gate.
2026-09-23 v1.16.0-L8-7C3B-CLIENT-VISIBILITY-WRITE-BINDING-CERT
certifies legal_client_visibility_write ->
legal_operations:client_visibility:write as the exact conjunctive authorization
binding for approved law-firm provisioning roles. It proves partner/attorney/
paralegal success, client/secretary/finance/sheriff/deputy denial, crossed
permission/operation denial, missing/revoked final-role denial, and unchanged
financial-execution prohibition.
2026-09-23 v1.15.0-L8-6C-DEPUTY-PERSONAL-QUEUE-BINDING-CERT
certifies legal_deputy_queue_read -> legal_operations:deputy_queue:read as an
exact deputy-only conjunctive authorization binding with sheriff denial,
crossed business/authorization-role rejection, permission-operation mismatch
rejection, and unchanged financial-execution prohibition.
2026-09-23 v1.14.1-L8-6A-SHERIFF-QUEUE-READ-BINDING-CERT
repairs the certificate runtime VERSION to the current L8-6A release; test
semantics, IAM authority, and sheriff-only queue-read behavior are unchanged.
2026-09-23 v1.14.0-L8-6A-SHERIFF-QUEUE-READ-BINDING-CERT
certifies legal_queue_read -> legal_operations:queue:read as an exact
sheriff-only conjunctive authorization binding, with deputy denial, crossed-pair
rejection, and unchanged financial-execution prohibition.
2026-09-23 v1.13.1-L8-3-LEGAL-OPERATIONS-RECEIPT-BINDING-CERT
repairs the remaining stale WILSY AI Legal Tool runtime-version assertion to
the current v1.17.0 L8-3 receipt-binding production release; authorization,
grant, scope, and fail-closed semantics are unchanged.
2026-09-23 v1.13.0-L8-3-LEGAL-OPERATIONS-RECEIPT-BINDING-CERT
certifies legal_receipt_write -> legal_operations:receipt:write as an exact
sheriff-only conjunctive authorization binding with deputy/legal-client denial.
2026-09-23 v1.12.1-L8-1-LEGAL-OPERATIONS-DIRECTORY-BINDING-CERT
refreshes the remaining legacy WILSY AI Legal Tool version assertion to the
current v1.16.0 authorization release without altering authorization behavior.
2026-09-23 v1.12.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-BINDING-CERT
certifies the exact legal_directory_write -> legal_operations:directory:write
binding, sheriff-only conjunctive authorization, and deputy/client denial.
2026-09-17 v1.11.0-C1E-R1 certifies exact legal-advisory operation
bindings and current tenant authorization forwarding.
2026-09-15 v1.9.0-L7B-WILSY-AI-LEGAL-TOOL-BINDING-CERT adds direct
PrincipalReader.resolve identity/session protocol and transaction-ownership
proof while preserving the exact gateway binding and financial firewall.
2026-09-17 v1.10.0-C1C-R1B refreshes stale canonical-version assertions
without changing authorization decisions or permission scope.
2026-09-15 v1.8.0-L7B-WILSY-AI-LEGAL-TOOL-BINDING-CERT certifies the
exact own-tenant WILSY AI Legal Tool Gateway read binding, its canonical
permission metadata, and every current-truth/fail-closed gate without granting
underlying Legal Operations authority or financial execution.
2026-09-15 v1.7.0-L7A-LEGAL-OPERATIONS-IAM-BINDING-CERT adds explicit
legal-operation bindings and preserves all conjunctive denial gates.
certifies the exact billing-intelligence evidence-read binding alongside the
existing WILSY AI capacity binding, including full current-truth conjunctions
and fail-closed malformed/crossed pairs; no new authority is introduced.
v1.5.0-M11-R8-R3B-P8-P3D-P4A-CERT certifies four exact
credential-security operation-to-permission bindings and least-authority
role denials. No decision schema or replay semantics changed.
v1.4.0-M11-R8-R3B-P8-P3B-I2-R3-CERT certifies the explicit
merchant-configuration remediation binding while preserving fail-closed
composition and opaque subjects.
v1.3.0-M11-R8-R3B-P8-P3A-CERT certifies eight dedicated inbound
merchant-configuration/provider-policy operation bindings while preserving
conjunctive current-truth authorization.
v1.2.0-M11-R8-R3B-P6A-CERT certifies the exact inbound
collection authorization-request composition while preserving fail-closed gate precedence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Deterministic resolve-only readers; projected transport authority cannot grant; mutation tripwires remain armed.
TENANT BOUNDARY: Exact principal and tenant scope, ACTIVE membership, one eligible tenant business role, and an ACTIVE granting authorization role are conjunctively required for every certified binding, including own-tenant evidence reads.
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
from tools.eos.auth.permission_namespace import PermissionDisposition, permission_metadata
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

VERSION = "v1.18.0-L8-8I-CONFLICT-REVIEW-BINDING-CERT"

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
    ("permission_id", "operation"),
     (("plan:read", "plan_read"), ("plan:manage", "plan_create"),
     ("subscription:read", "subscription_read"),
     ("subscription:manage", "subscription_create")),
)
def test_plan_subscription_policy_requires_two_dimensions(permission_id: str, operation: str) -> None:
    result = _decision(
        permission_id=permission_id,
        operation=operation,
        business_repository=_business("tenant_admin"),
        assignment_repository=_assignments("ENTERPRISE_ADMIN"),
    )
    assert result.authorized is True


def test_plan_subscription_mutation_denies_auditor_even_with_enterprise_assignment() -> None:
    for permission_id, operation in (("plan:manage", "plan_create"), ("subscription:manage", "subscription_create")):
        result = _decision(permission_id=permission_id, operation=operation, business_repository=_business("tenant_auditor"), assignment_repository=_assignments("ENTERPRISE_ADMIN"))
        assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


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


def test_l8_1_directory_binding_is_exact_and_sheriff_only() -> None:
    """Directory provisioning requires the exact permission, operation, and roles."""

    assert ta._BINDINGS["legal_directory_write"] == (
        "legal_operations:directory:write"
    )
    assert list(ta._BINDINGS).count("legal_directory_write") == 1

    authorized = _decision(
        permission_id="legal_operations:directory:write",
        operation="legal_directory_write",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF"),
    )
    assert authorized == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_sheriff",
        "SHERIFF",
    )

    assert _decision(
        permission_id="legal_operations:directory:write",
        operation="legal_directory_write",
        business_repository=_business("tenant_deputy"),
        assignment_repository=_assignments("SHERIFF"),
    ).reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE

    assert _decision(
        permission_id="legal_operations:directory:write",
        operation="legal_directory_write",
        business_repository=_business("tenant_legal_client"),
        assignment_repository=_assignments("SHERIFF"),
    ).reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE

    assert _decision(
        permission_id="legal_operations:directory:write",
        operation="legal_allocation_write",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF"),
    ).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH

    assert _decision(
        permission_id="legal_operations:allocation:write",
        operation="legal_directory_write",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF"),
    ).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


def test_l8_3_receipt_binding_is_exact_and_sheriff_only() -> None:
    """Acceptance/receipt requires the exact permission, operation, and sheriff role."""

    assert ta._BINDINGS["legal_receipt_write"] == (
        "legal_operations:receipt:write"
    )
    assert list(ta._BINDINGS).count("legal_receipt_write") == 1

    authorized = _decision(
        permission_id="legal_operations:receipt:write",
        operation="legal_receipt_write",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF"),
    )
    assert authorized == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_sheriff",
        "SHERIFF",
    )

    for business_role in (
        "tenant_deputy",
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "tenant_legal_paralegal",
        "tenant_legal_secretary",
        "tenant_legal_client",
    ):
        denied = _decision(
            permission_id="legal_operations:receipt:write",
            operation="legal_receipt_write",
            business_repository=_business(business_role),
            assignment_repository=_assignments("SHERIFF"),
        )
        assert denied.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE

    assert _decision(
        permission_id="legal_operations:receipt:write",
        operation="legal_allocation_write",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF"),
    ).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH

    assert _decision(
        permission_id="legal_operations:allocation:write",
        operation="legal_receipt_write",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF"),
    ).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


def test_l8_7d4_client_matter_read_binding_authorizes_exact_legal_client_conjunction() -> None:
    """Explicit client-matter read requires tenant_legal_client plus ACTIVE LEGAL_CLIENT."""
    assert (
        ta._BINDINGS["legal_client_matter_read"]
        == "legal_operations:client_matter:read"
    )
    assert list(ta._BINDINGS).count("legal_client_matter_read") == 1

    authorized = _decision(
        permission_id="legal_operations:client_matter:read",
        operation="legal_client_matter_read",
        business_repository=_business("tenant_legal_client"),
        assignment_repository=_assignments("LEGAL_CLIENT"),
    )
    assert authorized == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_legal_client",
        "LEGAL_CLIENT",
    )


@pytest.mark.parametrize(
    ("business_role", "authorization_roles"),
    (
        ("tenant_legal_partner", ("LEGAL_PARTNER", "LEGAL_CLIENT")),
        ("tenant_legal_attorney", ("LEGAL_ATTORNEY", "LEGAL_CLIENT")),
        ("tenant_legal_paralegal", ("LEGAL_PARALEGAL", "LEGAL_CLIENT")),
        ("tenant_legal_secretary", ("LEGAL_SECRETARY", "LEGAL_CLIENT")),
        ("tenant_legal_finance", ("LEGAL_FINANCE", "LEGAL_CLIENT")),
        ("tenant_sheriff", ("SHERIFF", "LEGAL_CLIENT")),
        ("tenant_deputy", ("DEPUTY", "LEGAL_CLIENT")),
        ("tenant_owner", ("ENTERPRISE_ADMIN", "LEGAL_CLIENT")),
        ("tenant_admin", ("ENTERPRISE_ADMIN", "LEGAL_CLIENT")),
    ),
)
def test_l8_7d4_non_client_business_roles_cannot_cross_into_client_projection(
    business_role: str,
    authorization_roles: tuple[str, ...],
) -> None:
    """Even a supplied LEGAL_CLIENT assignment cannot bypass business-role eligibility."""
    assignments = _assignments(*authorization_roles)
    denied = _decision(
        permission_id="legal_operations:client_matter:read",
        operation="legal_client_matter_read",
        business_repository=_business(business_role),
        assignment_repository=assignments,
    )
    assert denied.authorized is False
    assert denied.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    assert denied.business_role == business_role
    assert denied.authorization_role is None
    assert assignments.calls == []


def test_l8_7d4_missing_revoked_and_crossed_client_read_bindings_fail_closed() -> None:
    """Final role possession and exact permission-operation pairing remain mandatory."""
    missing = _decision(
        permission_id="legal_operations:client_matter:read",
        operation="legal_client_matter_read",
        business_repository=_business("tenant_legal_client"),
        assignment_repository=_assignments(),
    )
    assert missing.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    revoked = _decision(
        permission_id="legal_operations:client_matter:read",
        operation="legal_client_matter_read",
        business_repository=_business("tenant_legal_client"),
        assignment_repository=_assignments(
            revoked_roles=("LEGAL_CLIENT",),
        ),
    )
    assert revoked.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE

    wrong_permission = _decision(
        permission_id="legal_operations:invoice:read",
        operation="legal_client_matter_read",
        business_repository=_business("tenant_legal_client"),
        assignment_repository=_assignments("LEGAL_CLIENT"),
    )
    assert (
        wrong_permission.reason
        is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    )

    wrong_operation = _decision(
        permission_id="legal_operations:client_matter:read",
        operation="legal_invoice_read",
        business_repository=_business("tenant_legal_client"),
        assignment_repository=_assignments("LEGAL_CLIENT"),
    )
    assert (
        wrong_operation.reason
        is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    )


@pytest.mark.parametrize(
    ("business_role", "authorization_role"),
    (
        ("tenant_legal_partner", "LEGAL_PARTNER"),
        ("tenant_legal_attorney", "LEGAL_ATTORNEY"),
    ),
)
def test_l8_8i_conflict_review_binding_authorizes_only_partner_attorney_conjunction(
    business_role: str,
    authorization_role: str,
) -> None:
    """Human conflict review requires exact business/final-role conjunction."""
    assert (
        ta._BINDINGS["legal_conflict_review_write"]
        == "legal_operations:conflict_review:write"
    )
    assert list(ta._BINDINGS).count("legal_conflict_review_write") == 1

    result = _decision(
        permission_id="legal_operations:conflict_review:write",
        operation="legal_conflict_review_write",
        business_repository=_business(business_role),
        assignment_repository=_assignments(authorization_role),
    )
    assert result == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        business_role,
        authorization_role,
    )


@pytest.mark.parametrize(
    ("business_role", "authorization_roles"),
    (
        ("tenant_legal_paralegal", ("LEGAL_PARALEGAL", "LEGAL_PARTNER")),
        ("tenant_legal_secretary", ("LEGAL_SECRETARY", "LEGAL_PARTNER")),
        ("tenant_legal_finance", ("LEGAL_FINANCE", "LEGAL_PARTNER")),
        ("tenant_legal_client", ("LEGAL_CLIENT", "LEGAL_PARTNER")),
        ("tenant_sheriff", ("SHERIFF", "LEGAL_PARTNER")),
        ("tenant_deputy", ("DEPUTY", "LEGAL_PARTNER")),
        ("tenant_owner", ("ENTERPRISE_ADMIN", "LEGAL_PARTNER")),
        ("tenant_admin", ("ENTERPRISE_ADMIN", "LEGAL_PARTNER")),
        ("tenant_auditor", ("AUDITOR", "LEGAL_PARTNER")),
    ),
)
def test_l8_8i_ineligible_business_roles_cannot_cross_into_conflict_review(
    business_role: str,
    authorization_roles: tuple[str, ...],
) -> None:
    """Even a supplied partner assignment cannot bypass business eligibility."""
    assignments = _assignments(*authorization_roles)
    denied = _decision(
        permission_id="legal_operations:conflict_review:write",
        operation="legal_conflict_review_write",
        business_repository=_business(business_role),
        assignment_repository=assignments,
    )
    assert denied.authorized is False
    assert denied.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    assert denied.business_role == business_role
    assert denied.authorization_role is None
    assert assignments.calls == []


def test_l8_8i_missing_revoked_and_crossed_conflict_review_bindings_fail_closed() -> None:
    """Permission, operation and active granting role remain separate conjuncts."""
    missing = _decision(
        permission_id="legal_operations:conflict_review:write",
        operation="legal_conflict_review_write",
        business_repository=_business("tenant_legal_partner"),
        assignment_repository=_assignments(),
    )
    assert missing.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    revoked = _decision(
        permission_id="legal_operations:conflict_review:write",
        operation="legal_conflict_review_write",
        business_repository=_business("tenant_legal_partner"),
        assignment_repository=_assignments(
            revoked_roles=("LEGAL_PARTNER",),
        ),
    )
    assert revoked.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE

    wrong_permission = _decision(
        permission_id="legal_operations:instruction:write",
        operation="legal_conflict_review_write",
        business_repository=_business("tenant_legal_partner"),
        assignment_repository=_assignments("LEGAL_PARTNER"),
    )
    assert (
        wrong_permission.reason
        is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    )

    wrong_operation = _decision(
        permission_id="legal_operations:conflict_review:write",
        operation="legal_instruction_write",
        business_repository=_business("tenant_legal_partner"),
        assignment_repository=_assignments("LEGAL_PARTNER"),
    )
    assert (
        wrong_operation.reason
        is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    )


@pytest.mark.parametrize(
    ("business_role", "authorization_role"),
    (
        ("tenant_legal_partner", "LEGAL_PARTNER"),
        ("tenant_legal_attorney", "LEGAL_ATTORNEY"),
        ("tenant_legal_paralegal", "LEGAL_PARALEGAL"),
    ),
)
def test_l8_7c3b_client_visibility_write_binding_authorizes_only_full_law_firm_conjunction(
    business_role: str,
    authorization_role: str,
) -> None:
    """Exact law-firm business/final-role conjunction authorizes provisioning."""
    assert (
        ta._BINDINGS["legal_client_visibility_write"]
        == "legal_operations:client_visibility:write"
    )
    assert list(ta._BINDINGS).count("legal_client_visibility_write") == 1

    result = _decision(
        permission_id="legal_operations:client_visibility:write",
        operation="legal_client_visibility_write",
        business_repository=_business(business_role),
        assignment_repository=_assignments(authorization_role),
    )
    assert result == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        business_role,
        authorization_role,
    )


@pytest.mark.parametrize(
    ("business_role", "authorization_roles"),
    (
        ("tenant_legal_client", ("LEGAL_CLIENT", "LEGAL_PARTNER")),
        ("tenant_legal_secretary", ("LEGAL_SECRETARY", "LEGAL_PARTNER")),
        ("tenant_legal_finance", ("LEGAL_FINANCE", "LEGAL_PARTNER")),
        ("tenant_sheriff", ("SHERIFF", "LEGAL_PARTNER")),
        ("tenant_deputy", ("DEPUTY", "LEGAL_PARTNER")),
        ("tenant_owner", ("ENTERPRISE_ADMIN", "LEGAL_PARTNER")),
        ("tenant_admin", ("ENTERPRISE_ADMIN", "LEGAL_PARTNER")),
    ),
)
def test_l8_7c3b_ineligible_business_roles_deny_before_grant_lookup(
    business_role: str,
    authorization_roles: tuple[str, ...],
) -> None:
    """Static final-role grants cannot bypass business-role eligibility."""
    assignments = _assignments(*authorization_roles)
    result = _decision(
        permission_id="legal_operations:client_visibility:write",
        operation="legal_client_visibility_write",
        business_repository=_business(business_role),
        assignment_repository=assignments,
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    assert result.business_role == business_role
    assert result.authorization_role is None
    assert assignments.calls == []


def test_l8_7c3b_missing_revoked_and_crossed_bindings_fail_closed() -> None:
    """Permission, operation and active granting role remain separate conjuncts."""
    missing = _decision(
        permission_id="legal_operations:client_visibility:write",
        operation="legal_client_visibility_write",
        business_repository=_business("tenant_legal_partner"),
        assignment_repository=_assignments(),
    )
    assert missing.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    revoked = _decision(
        permission_id="legal_operations:client_visibility:write",
        operation="legal_client_visibility_write",
        business_repository=_business("tenant_legal_partner"),
        assignment_repository=_assignments(
            revoked_roles=("LEGAL_PARTNER",),
        ),
    )
    assert revoked.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE

    wrong_permission = _decision(
        permission_id="legal_operations:instruction:write",
        operation="legal_client_visibility_write",
        business_repository=_business("tenant_legal_partner"),
        assignment_repository=_assignments("LEGAL_PARTNER"),
    )
    assert (
        wrong_permission.reason
        is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    )

    wrong_operation = _decision(
        permission_id="legal_operations:client_visibility:write",
        operation="legal_instruction_write",
        business_repository=_business("tenant_legal_partner"),
        assignment_repository=_assignments("LEGAL_PARTNER"),
    )
    assert (
        wrong_operation.reason
        is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    )


def test_l8_6c_deputy_personal_queue_binding_is_exact_and_deputy_only() -> None:
    """Personal work reads require the exact deputy IAM conjunction."""

    assert (
        ta._BINDINGS["legal_deputy_queue_read"]
        == "legal_operations:deputy_queue:read"
    )
    assert list(ta._BINDINGS).count("legal_deputy_queue_read") == 1

    authorized = _decision(
        permission_id="legal_operations:deputy_queue:read",
        operation="legal_deputy_queue_read",
        business_repository=_business("tenant_deputy"),
        assignment_repository=_assignments("DEPUTY"),
    )
    assert authorized == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_deputy",
        "DEPUTY",
    )

    sheriff = _decision(
        permission_id="legal_operations:deputy_queue:read",
        operation="legal_deputy_queue_read",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF", "DEPUTY"),
    )
    assert sheriff.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE

    crossed_deputy = _decision(
        permission_id="legal_operations:deputy_queue:read",
        operation="legal_deputy_queue_read",
        business_repository=_business("tenant_deputy"),
        assignment_repository=_assignments("SHERIFF"),
    )
    assert crossed_deputy.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    assert _decision(
        permission_id="legal_operations:queue:read",
        operation="legal_deputy_queue_read",
        business_repository=_business("tenant_deputy"),
        assignment_repository=_assignments("DEPUTY"),
    ).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH

    assert _decision(
        permission_id="legal_operations:deputy_queue:read",
        operation="legal_queue_read",
        business_repository=_business("tenant_deputy"),
        assignment_repository=_assignments("DEPUTY"),
    ).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


def test_l8_6a_queue_read_binding_is_exact_and_sheriff_only() -> None:
    """Operational queue reads require the exact sheriff IAM conjunction."""

    assert ta._BINDINGS["legal_queue_read"] == "legal_operations:queue:read"
    assert list(ta._BINDINGS).count("legal_queue_read") == 1

    authorized = _decision(
        permission_id="legal_operations:queue:read",
        operation="legal_queue_read",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF"),
    )
    assert authorized == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_sheriff",
        "SHERIFF",
    )

    for business_role, grant_role in (
        ("tenant_deputy", "DEPUTY"),
        ("tenant_legal_partner", "LEGAL_PARTNER"),
        ("tenant_legal_attorney", "LEGAL_ATTORNEY"),
        ("tenant_legal_paralegal", "LEGAL_PARALEGAL"),
        ("tenant_legal_secretary", "LEGAL_SECRETARY"),
        ("tenant_legal_finance", "LEGAL_FINANCE"),
        ("tenant_legal_client", "LEGAL_CLIENT"),
    ):
        denied = _decision(
            permission_id="legal_operations:queue:read",
            operation="legal_queue_read",
            business_repository=_business(business_role),
            assignment_repository=_assignments(grant_role, "SHERIFF"),
        )
        assert denied.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE

    assert _decision(
        permission_id="legal_operations:queue:read",
        operation="legal_attempt_read",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF"),
    ).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH

    assert _decision(
        permission_id="legal_operations:attempt:read",
        operation="legal_queue_read",
        business_repository=_business("tenant_sheriff"),
        assignment_repository=_assignments("SHERIFF"),
    ).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


def test_m14_evidence_bindings_are_exact_and_unique() -> None:
    """Both evidence operations resolve only through their immutable exact pairs."""

    assert ta.VERSION == "v1.22.0-L8-8I-CONFLICT-REVIEW-BINDING"
    assert ta._BINDINGS["wilsy_ai_usage_capacity_read"] == (
        "wilsy_ai:usage_capacity:read"
    )
    assert ta._BINDINGS["billing_intelligence_evidence_read"] == (
        "billing_intelligence:evidence:read"
    )
    assert list(ta._BINDINGS).count("wilsy_ai_usage_capacity_read") == 1
    assert list(ta._BINDINGS).count("billing_intelligence_evidence_read") == 1


def test_wilsy_ai_legal_tool_binding_is_exact_tenant_and_fail_closed() -> None:
    """Gateway reads require canonical own-tenant IAM and never create authority."""

    assert ta.VERSION == "v1.22.0-L8-8I-CONFLICT-REVIEW-BINDING"
    assert ta._BINDINGS["wilsy_ai_legal_tool_read"] == "wilsy_ai:legal_tool:read"
    assert list(ta._BINDINGS).count("wilsy_ai_legal_tool_read") == 1

    metadata = permission_metadata("wilsy_ai:legal_tool:read")
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert metadata.disposition is PermissionDisposition.CANONICAL

    authorized = _decision(
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        business_repository=_business("tenant_legal_attorney"),
        assignment_repository=_assignments("LEGAL_ATTORNEY"),
    )
    assert authorized == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_legal_attorney",
        "LEGAL_ATTORNEY",
    )

    assert _decision(
        permission_id="legal_operations:instruction:read",
        operation="wilsy_ai_legal_tool_read",
        business_repository=_business("tenant_legal_attorney"),
        assignment_repository=_assignments("LEGAL_ATTORNEY"),
    ).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    assert _decision(
        permission_id="unknown",
        operation="wilsy_ai_legal_tool_read",
        business_repository=_business("tenant_legal_attorney"),
        assignment_repository=_assignments("LEGAL_ATTORNEY"),
    ).reason is TenantAuthorizationReason.PERMISSION_UNKNOWN
    assert _decision(
        permission_id="wilsy_ai:legal_tool:read",
        operation=" wilsy_ai_legal_tool_read",
        business_repository=_business("tenant_legal_attorney"),
        assignment_repository=_assignments("LEGAL_ATTORNEY"),
    ).reason is TenantAuthorizationReason.INVALID_INPUT
    assert _decision(
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        tenant_id="foreign-tenant",
        business_repository=_business("tenant_legal_attorney"),
        assignment_repository=_assignments("LEGAL_ATTORNEY"),
    ).reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND
    assert _decision(
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        principal_repository=_principal(status=PrincipalStatus.SUSPENDED),
        business_repository=_business("tenant_legal_attorney"),
        assignment_repository=_assignments("LEGAL_ATTORNEY"),
    ).reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE
    assert _decision(
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        membership_repository=_membership(status=TenantMembershipStatus.SUSPENDED),
        business_repository=_business("tenant_legal_attorney"),
        assignment_repository=_assignments("LEGAL_ATTORNEY"),
    ).reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE
    assert _decision(
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        business_repository=_business("tenant_legal_client"),
        assignment_repository=_assignments("LEGAL_ATTORNEY"),
    ).reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    assert _decision(
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        business_repository=_business("tenant_legal_attorney"),
        assignment_repository=_assignments(revoked_roles=("LEGAL_ATTORNEY",)),
    ).reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE
    assert _decision(
        permission_id="wilsy_ai:legal_tool:read",
        operation="financial_execution",
        business_repository=_business("tenant_legal_attorney"),
        assignment_repository=_assignments("LEGAL_ATTORNEY"),
    ).reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED


def test_principal_reader_resolve_preserves_identity_session_and_ownership() -> None:
    """The resolve protocol receives caller truth without transaction authority."""

    session = object()
    principal_ids: list[str] = []
    principal_sessions: list[object] = []
    transaction_calls: list[str] = []

    class _TransactionProbe:
        def start_transaction(self) -> None:
            transaction_calls.append("start")

        def commit(self) -> None:
            transaction_calls.append("commit")

        def commit_transaction(self) -> None:
            transaction_calls.append("commit_transaction")

        def abort(self) -> None:
            transaction_calls.append("abort")

        def abort_transaction(self) -> None:
            transaction_calls.append("abort_transaction")

        def retry_transaction(self) -> None:
            transaction_calls.append("retry")

    class _PrincipalReader(_TransactionProbe):
        def resolve(self, principal_id: str, *, session: object = None) -> object:
            principal_ids.append(principal_id)
            principal_sessions.append(session)
            return _StatusRecord(PrincipalStatus.ACTIVE)

    class _MembershipReader(_TransactionProbe):
        def __init__(self, status: TenantMembershipStatus) -> None:
            self.status = status

        def resolve(
            self, principal_id: str, tenant_id: str, *, session: object = None
        ) -> object:
            assert (principal_id, tenant_id) == (_PID, _TENANT)
            assert session is session_object
            return _StatusRecord(self.status)

    class _RoleReader(_TransactionProbe):
        def __init__(self, active: set[str]) -> None:
            self.active = active

        def resolve(
            self,
            principal_id: str,
            tenant_id: str,
            role_id: str,
            *,
            session: object = None,
        ) -> object:
            assert (principal_id, tenant_id) == (_PID, _TENANT)
            assert session is session_object
            if role_id not in self.active:
                raise RoleAssignmentNotFoundError("missing")
            return _StatusRecord(RoleAssignmentStatus.ACTIVE)

    session_object = session
    principal = _PrincipalReader()
    membership = _MembershipReader(TenantMembershipStatus.ACTIVE)
    business = _RoleReader({"tenant_legal_attorney"})
    assignments = _RoleReader({"LEGAL_ATTORNEY"})

    result = authorize_tenant_operation(
        principal_id=_PID,
        tenant_id=_TENANT,
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=business,
        role_assignment_repository=assignments,
        session=session,
    )
    assert result.authorized is True
    assert principal_ids == [_PID]
    assert principal_sessions == [session]
    assert transaction_calls == []

    no_grant = _RoleReader(set())
    denied_without_assignment = authorize_tenant_operation(
        principal_id=_PID,
        tenant_id=_TENANT,
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=business,
        role_assignment_repository=no_grant,
        session=session,
    )
    assert denied_without_assignment.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    denied_inactive_membership = authorize_tenant_operation(
        principal_id=_PID,
        tenant_id=_TENANT,
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        principal_repository=principal,
        membership_repository=_MembershipReader(TenantMembershipStatus.SUSPENDED),
        business_role_repository=business,
        role_assignment_repository=assignments,
        session=session,
    )
    assert denied_inactive_membership.reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE

    denied_ineligible_business = authorize_tenant_operation(
        principal_id=_PID,
        tenant_id=_TENANT,
        permission_id="wilsy_ai:legal_tool:read",
        operation="wilsy_ai_legal_tool_read",
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=_RoleReader({"tenant_legal_client"}),
        role_assignment_repository=assignments,
        session=session,
    )
    assert denied_ineligible_business.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE

    denied_underlying_permission = authorize_tenant_operation(
        principal_id=_PID,
        tenant_id=_TENANT,
        permission_id="legal_operations:instruction:read",
        operation="wilsy_ai_legal_tool_read",
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=business,
        role_assignment_repository=assignments,
        session=session,
    )
    assert denied_underlying_permission.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH

    denied_financial = authorize_tenant_operation(
        principal_id=_PID,
        tenant_id=_TENANT,
        permission_id="wilsy_ai:legal_tool:read",
        operation="financial_execution",
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=business,
        role_assignment_repository=assignments,
        session=session,
    )
    assert denied_financial.reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED
    assert transaction_calls == []


@pytest.mark.parametrize(
    ("permission", "operation", "business_role", "authorization_role"),
    [
        ("legal_operations:instruction:read", "legal_instruction_read", "tenant_legal_partner", "LEGAL_PARTNER"),
        ("legal_operations:attempt:write", "legal_attempt_write", "tenant_deputy", "DEPUTY"),
        ("legal_operations:invoice:read", "legal_invoice_read", "tenant_legal_client", "LEGAL_CLIENT"),
    ],
)
def test_legal_operations_bindings_remain_fully_conjunctive(permission: str, operation: str, business_role: str, authorization_role: str) -> None:
    """New legal bindings require exact current role and permission evidence."""
    result = _decision(permission_id=permission, operation=operation, business_repository=_business(business_role), assignment_repository=_assignments(authorization_role))
    assert result == TenantAuthorizationDecision(True, TenantAuthorizationReason.AUTHORIZED, business_role, authorization_role)
    crossed = _decision(permission_id=permission, operation="legal_instruction_write", business_repository=_business(business_role), assignment_repository=_assignments(authorization_role))
    assert crossed.authorized is False


def test_billing_intelligence_permission_metadata_is_canonical_tenant_read() -> None:
    """The bound permission retains its non-financial own-tenant metadata contract."""

    metadata = permission_metadata("billing_intelligence:evidence:read")
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.business_capability == (
        "read own-tenant canonical billing-intelligence evidence"
    )
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is False
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert metadata.disposition is PermissionDisposition.CANONICAL


@pytest.mark.parametrize(
    ("business_role", "authorization_role"),
    (
        ("tenant_owner", "ENTERPRISE_ADMIN"),
        ("tenant_admin", "ENTERPRISE_ADMIN"),
        ("tenant_manager", "ENTERPRISE_ADMIN"),
        ("tenant_auditor", "AUDITOR"),
    ),
)
def test_billing_intelligence_read_requires_full_current_truth(
    business_role: str, authorization_role: str
) -> None:
    """The billing evidence read succeeds only with every existing authority conjunct."""

    result = _decision(
        permission_id="billing_intelligence:evidence:read",
        operation="billing_intelligence_evidence_read",
        business_repository=_business(business_role),
        assignment_repository=_assignments(authorization_role),
    )
    assert result == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        business_role,
        authorization_role,
    )


def test_wilsy_ai_capacity_binding_remains_authorized_through_current_truth() -> None:
    """The pre-existing M13 WILSY AI binding remains a normal conjunctive decision."""

    result = _decision(
        permission_id="wilsy_ai:usage_capacity:read",
        operation="wilsy_ai_usage_capacity_read",
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
    ("permission_id", "operation"),
    (
        ("billing_intelligence:evidence:read", "wilsy_ai_usage_capacity_read"),
        ("wilsy_ai:usage_capacity:read", "billing_intelligence_evidence_read"),
        ("billing_intelligence:evidence:read", "billing_intelligence_evidence"),
        ("billing_intelligence:evidence:read", "BILLING_INTELLIGENCE_EVIDENCE_READ"),
        ("billing_intelligence:evidence:read", " billing_intelligence_evidence_read"),
        ("billing_intelligence:evidence:read", "billing_intelligence_evidence_read "),
        ("billing_intelligence:evidence:READ", "billing_intelligence_evidence_read"),
        ("billing_intelligence:evidence:read ", "billing_intelligence_evidence_read"),
        ("billing_intelligence:*", "billing_intelligence_evidence_read"),
    ),
)
def test_m14_evidence_binding_cross_pairs_and_aliases_fail_closed(
    permission_id: str, operation: str
) -> None:
    """Crossed, unknown, case, whitespace, and wildcard forms stop before grants."""

    assignments = _assignments("ENTERPRISE_ADMIN", "AUDITOR")
    result = _decision(
        permission_id=permission_id,
        operation=operation,
        business_repository=_business("tenant_owner"),
        assignment_repository=assignments,
    )
    assert result.authorized is False
    assert result.reason in {
        TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH,
        TenantAuthorizationReason.PERMISSION_UNKNOWN,
        TenantAuthorizationReason.INVALID_INPUT,
    }
    assert assignments.calls == []


@pytest.mark.parametrize(
    "authorization_role",
    (
        "SOVEREIGN_ARCHITECT",
        "SERVICE_WORKER",
        "PLATFORM_BILLING_PROVIDER_POLICY_ADMIN",
        "ACCOUNTS_PAYABLE_PROVIDER_POLICY_ADMIN",
        "INBOUND_COLLECTION_AUTHORIZATION_ADMIN",
        "INBOUND_MERCHANT_CONFIGURATION_ADMIN",
        "INBOUND_PROVIDER_SECURITY_ADMIN",
        "INBOUND_PROVIDER_POLICY_ADMIN",
        "INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN",
    ),
)
def test_billing_intelligence_read_rejects_unrelated_assignments(
    authorization_role: str,
) -> None:
    """Specialized or platform roles cannot cross-grant billing evidence reads."""

    result = _decision(
        permission_id="billing_intelligence:evidence:read",
        operation="billing_intelligence_evidence_read",
        business_repository=_business("tenant_owner"),
        assignment_repository=_assignments(authorization_role),
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED


def test_billing_intelligence_read_missing_inactive_and_wrong_assignments_deny() -> None:
    """Eligibility alone, inactive grants, and wrong scope never authorize."""

    missing = _decision(
        permission_id="billing_intelligence:evidence:read",
        operation="billing_intelligence_evidence_read",
        business_repository=_business("tenant_admin"),
        assignment_repository=_assignments(),
    )
    assert missing.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    inactive = _decision(
        permission_id="billing_intelligence:evidence:read",
        operation="billing_intelligence_evidence_read",
        business_repository=_business("tenant_admin"),
        assignment_repository=_assignments(revoked_roles=("ENTERPRISE_ADMIN",)),
    )
    assert inactive.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE

    wrong_scope = _AssignmentReader(
        {("other", _TENANT, "ENTERPRISE_ADMIN"): _StatusRecord(RoleAssignmentStatus.ACTIVE)}
    )
    wrong = _decision(
        permission_id="billing_intelligence:evidence:read",
        operation="billing_intelligence_evidence_read",
        business_repository=_business("tenant_admin"),
        assignment_repository=wrong_scope,
    )
    assert wrong.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    inactive_principal = _decision(
        permission_id="billing_intelligence:evidence:read",
        operation="billing_intelligence_evidence_read",
        principal_repository=_principal(status=PrincipalStatus.SUSPENDED),
        business_repository=_business("tenant_admin"),
        assignment_repository=_assignments("ENTERPRISE_ADMIN"),
    )
    assert inactive_principal.reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE

    inactive_membership = _decision(
        permission_id="billing_intelligence:evidence:read",
        operation="billing_intelligence_evidence_read",
        membership_repository=_membership(status=TenantMembershipStatus.SUSPENDED),
        business_repository=_business("tenant_admin"),
        assignment_repository=_assignments("ENTERPRISE_ADMIN"),
    )
    assert inactive_membership.reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE


def test_inbound_collection_authorization_composition_is_exact_and_opaque() -> None:
    """Current principal, membership, business role, and dedicated grant compose exactly."""
    result = _decision(
        permission_id="inbound_collection:authorization:create",
        operation="inbound_collection_authorization_create",
        business_repository=_business("tenant_inbound_collection_authorization_admin"),
        assignment_repository=_assignments("INBOUND_COLLECTION_AUTHORIZATION_ADMIN"),
    )
    assert result == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_inbound_collection_authorization_admin",
        "INBOUND_COLLECTION_AUTHORIZATION_ADMIN",
    )
    assert result.business_role == "tenant_inbound_collection_authorization_admin"
    assert result.authorization_role == "INBOUND_COLLECTION_AUTHORIZATION_ADMIN"


@pytest.mark.parametrize(
    ("permission_id", "operation"),
    (
        ("inbound_collection:authorization:create", "audit_read"),
        ("audit:read", "inbound_collection_authorization_create"),
        ("unknown", "inbound_collection_authorization_create"),
    ),
)
def test_inbound_collection_operation_permission_pairing_is_exact(
    permission_id: str,
    operation: str,
) -> None:
    """Wrong, unknown, and cross-capability pairs fail before role grant lookup."""
    assignments = _assignments("INBOUND_COLLECTION_AUTHORIZATION_ADMIN", "AUDITOR")
    result = _decision(
        permission_id=permission_id,
        operation=operation,
        business_repository=_business("tenant_inbound_collection_authorization_admin"),
        assignment_repository=assignments,
    )
    assert result.authorized is False
    assert result.reason in {
        TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH,
        TenantAuthorizationReason.PERMISSION_UNKNOWN,
    }
    assert assignments.calls == []


@pytest.mark.parametrize(
    "authorization_role",
    (
        "AUDITOR",
        "ENTERPRISE_ADMIN",
        "PLATFORM_BILLING_PROVIDER_POLICY_ADMIN",
        "ACCOUNTS_PAYABLE_PROVIDER_POLICY_ADMIN",
    ),
)
def test_inbound_collection_does_not_accept_unrelated_authorization_roles(
    authorization_role: str,
) -> None:
    """Invoice-read, provider-policy, AP, and administrative roles do not cross-grant."""
    result = _decision(
        permission_id="inbound_collection:authorization:create",
        operation="inbound_collection_authorization_create",
        business_repository=_business("tenant_inbound_collection_authorization_admin"),
        assignment_repository=_assignments(authorization_role),
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED


@pytest.mark.parametrize(
    ("operation", "permission", "business_role", "authorization_role"),
    (
        ("tenant_inbound_merchant_configuration_register", "inbound_merchant_configuration:register", "tenant_inbound_merchant_configuration_admin", "INBOUND_MERCHANT_CONFIGURATION_ADMIN"),
        ("tenant_inbound_merchant_configuration_lifecycle_transition", "inbound_merchant_configuration:lifecycle", "tenant_inbound_merchant_configuration_admin", "INBOUND_MERCHANT_CONFIGURATION_ADMIN"),
        ("tenant_inbound_merchant_configuration_compromise", "inbound_merchant_configuration:security", "tenant_inbound_provider_security_admin", "INBOUND_PROVIDER_SECURITY_ADMIN"),
        ("tenant_inbound_merchant_configuration_remediate", "inbound_merchant_configuration:remediate", "tenant_inbound_provider_security_admin", "INBOUND_PROVIDER_SECURITY_ADMIN"),
        ("tenant_inbound_provider_policy_create", "inbound_provider_policy:author", "tenant_inbound_provider_policy_admin", "INBOUND_PROVIDER_POLICY_ADMIN"),
        ("tenant_inbound_provider_policy_revise", "inbound_provider_policy:author", "tenant_inbound_provider_policy_admin", "INBOUND_PROVIDER_POLICY_ADMIN"),
        ("tenant_inbound_provider_policy_activate", "inbound_provider_policy:activate", "tenant_inbound_provider_policy_activation_admin", "INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN"),
        ("tenant_inbound_provider_policy_deactivate", "inbound_provider_policy:deactivate", "tenant_inbound_provider_policy_activation_admin", "INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN"),
        ("tenant_inbound_provider_policy_emergency_disable", "inbound_provider_policy:emergency_disable", "tenant_inbound_provider_security_admin", "INBOUND_PROVIDER_SECURITY_ADMIN"),
    ),
)
def test_inbound_provider_operation_mappings_are_exact(
    operation: str,
    permission: str,
    business_role: str,
    authorization_role: str,
) -> None:
    result = _decision(
        permission_id=permission,
        operation=operation,
        business_repository=_business(business_role),
        assignment_repository=_assignments(authorization_role),
    )
    assert result == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        business_role,
        authorization_role,
    )


def test_inbound_provider_privileges_do_not_cross_grant() -> None:
    result = _decision(
        permission_id="inbound_provider_policy:activate",
        operation="tenant_inbound_provider_policy_activate",
        business_repository=_business("tenant_inbound_provider_policy_admin"),
        assignment_repository=_assignments("INBOUND_PROVIDER_POLICY_ADMIN"),
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


def test_remediation_is_limited_to_security_business_and_authorization_roles() -> None:
    result = _decision(
        permission_id="inbound_merchant_configuration:remediate",
        operation="tenant_inbound_merchant_configuration_remediate",
        business_repository=_business("tenant_inbound_merchant_configuration_admin"),
        assignment_repository=_assignments("INBOUND_PROVIDER_SECURITY_ADMIN"),
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


@pytest.mark.parametrize(
    ("operation", "permission"),
    (
        ("tenant_inbound_provider_credential_security_eligibility_issue", "inbound_provider_credential_security:eligibility_issue"),
        ("tenant_inbound_provider_credential_security_revoke", "inbound_provider_credential_security:revoke"),
        ("tenant_inbound_provider_credential_security_compromise", "inbound_provider_credential_security:compromise"),
        ("tenant_inbound_provider_credential_security_rotate", "inbound_provider_credential_security:rotate"),
    ),
)
def test_credential_security_operation_permission_bindings_are_exact(
    operation: str, permission: str,
) -> None:
    result = _decision(
        permission_id=permission,
        operation=operation,
        business_repository=_business("tenant_inbound_provider_security_admin"),
        assignment_repository=_assignments("INBOUND_PROVIDER_SECURITY_ADMIN"),
    )
    assert result == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_inbound_provider_security_admin",
        "INBOUND_PROVIDER_SECURITY_ADMIN",
    )


@pytest.mark.parametrize(
    "authorization_role",
    (
        "INBOUND_MERCHANT_CONFIGURATION_ADMIN",
        "INBOUND_PROVIDER_POLICY_ADMIN",
        "INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN",
        "ENTERPRISE_ADMIN",
        "AUDITOR",
    ),
)
def test_credential_security_requires_security_admin_role(authorization_role: str) -> None:
    result = _decision(
        permission_id="inbound_provider_credential_security:eligibility_issue",
        operation="tenant_inbound_provider_credential_security_eligibility_issue",
        business_repository=_business("tenant_inbound_provider_security_admin"),
        assignment_repository=_assignments(authorization_role),
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED


def test_credential_security_operation_permission_cross_pairing_fails_closed() -> None:
    result = _decision(
        permission_id="inbound_provider_credential_security:revoke",
        operation="tenant_inbound_provider_credential_security_compromise",
        business_repository=_business("tenant_inbound_provider_security_admin"),
        assignment_repository=_assignments("INBOUND_PROVIDER_SECURITY_ADMIN"),
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


def test_credential_security_unknown_operation_and_permission_fail_closed() -> None:
    for operation, permission in (
        ("tenant_inbound_provider_credential_security_unknown", "inbound_provider_credential_security:eligibility_issue"),
        ("tenant_inbound_provider_credential_security_eligibility_issue", "inbound_provider_credential_security:unknown"),
    ):
        assignments = _assignments("INBOUND_PROVIDER_SECURITY_ADMIN")
        result = _decision(
            permission_id=permission,
            operation=operation,
            business_repository=_business("tenant_inbound_provider_security_admin"),
            assignment_repository=assignments,
        )
        assert result.authorized is False
        assert result.reason in {TenantAuthorizationReason.INVALID_INPUT, TenantAuthorizationReason.PERMISSION_UNKNOWN}
        assert assignments.calls == []

def test_platform_billing_release_requires_owner_and_enterprise_admin() -> None:
    result = _decision(permission_id="platform_billing:release", operation="platform_billing_release", business_repository=_business("tenant_owner"), assignment_repository=_assignments("ENTERPRISE_ADMIN"))
    assert result.authorized is True
    assert result.reason is TenantAuthorizationReason.AUTHORIZED

@pytest.mark.parametrize("business_role", ("tenant_admin", "tenant_manager", "tenant_auditor"))
def test_platform_billing_release_rejects_non_owner_business_roles(business_role: str) -> None:
    result = _decision(permission_id="platform_billing:release", operation="platform_billing_release", business_repository=_business(business_role), assignment_repository=_assignments("ENTERPRISE_ADMIN"))
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


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

    for operation in ("", " ", "unknown", "tenant_inbound_merchant_configuration_remediation", None, 123):
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

    assert ta._BINDINGS["inbound_collection_authorization_create"] == (
        "inbound_collection:authorization:create"
    )
    assert list(ta._BINDINGS).count("inbound_collection_authorization_create") == 1
    with pytest.raises(TypeError):
        cast(Any, ta._BINDINGS)["profile_read"] = "tenant:profile:write"
    with pytest.raises(TypeError):
        cast(Any, ta._BINDINGS)["billing_intelligence_evidence_read"] = "tenant:profile:read"


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
# 31-32 M14 exact evidence bindings and full-truth successes:
#     test_m14_evidence_bindings_are_exact_and_unique,
#     test_billing_intelligence_read_requires_full_current_truth
# 33 B4 exact gateway binding and current-truth/fail-closed gates:
#     test_wilsy_ai_legal_tool_binding_is_exact_tenant_and_fail_closed


def test_c1e_advisory_bindings_are_exact_and_seven_role_scoped() -> None:
    assert ta._BINDINGS["wilsy_ai_legal_advisory_generate"] == "wilsy_ai:legal_advisory:generate"
    assert ta._BINDINGS["wilsy_ai_legal_advisory_read"] == "wilsy_ai:legal_advisory:read"
    assert list(ta._BINDINGS).count("wilsy_ai_legal_advisory_generate") == 1
    assert list(ta._BINDINGS).count("wilsy_ai_legal_advisory_read") == 1
    for permission, operation in (("wilsy_ai:legal_advisory:generate", "wilsy_ai_legal_advisory_generate"), ("wilsy_ai:legal_advisory:read", "wilsy_ai_legal_advisory_read")):
        metadata = permission_metadata(permission)
        assert metadata.namespace == "TENANT" and metadata.scope_kind == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False
        assert ta._BINDINGS[operation] == permission


def test_c1e_advisory_operation_crossing_fails_closed() -> None:
    result = _decision(permission_id="wilsy_ai:legal_advisory:generate", operation="wilsy_ai_legal_advisory_read", business_repository=_business("tenant_deputy"), assignment_repository=_assignments("DEPUTY"))
    assert result.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
# 34 B4 principal-reader resolve/session/transaction protocol:
#     test_principal_reader_resolve_preserves_identity_session_and_ownership
# 35 existing M13 binding success: test_wilsy_ai_capacity_binding_remains_authorized_through_current_truth
# 36-44 M14 crossed/alias/specialized/assignment locks:
#     test_m14_evidence_binding_cross_pairs_and_aliases_fail_closed,
#     test_billing_intelligence_read_rejects_unrelated_assignments,
#     test_billing_intelligence_read_missing_inactive_and_wrong_assignments_deny
# 45 system/cross-tenant lock: test_system_authority_operations_remain_outside_tenant_grants
# 46 financial lock: test_financial_execution_remains_prohibited_before_final_grant_lookup
# 47 final assignment scope: test_wrong_assignment_scope_cannot_grant
# 48 malformed operations: test_malformed_operation_values_fail_closed_before_grant_lookup
# 49 determinism and immutability: test_decisions_are_deterministic_and_immutable
# 50 immutable composition binding: test_operation_binding_is_immutable
# 51 caller/JWT/header non-authority: test_transport_or_caller_projection_cannot_enter_composition
# 52-54 read-only success/denial/financial paths: test_authorization_is_read_only_across_success_denial_and_financial_paths

# Caller-owned session propagation contract.
def test_caller_owned_session_is_forwarded_to_authority_reads() -> None:
    session = object()
    seen: list[object] = []
    principal = _principal(); membership = _membership(); business = _business("tenant_owner"); assignments = _assignments("ENTERPRISE_ADMIN")
    class P:
        def resolve(self, principal_id: str, *, session: object = None) -> object: seen.append(session); return principal.resolve(principal_id)
    class M:
        def resolve(self, principal_id: str, tenant_id: str, *, session: object = None) -> object: seen.append(session); return membership.resolve(principal_id, tenant_id)
    class A:
        def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: object = None) -> object: seen.append(session); return assignments.resolve(principal_id, tenant_id, role_id)
    class B(A):
        def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: object = None) -> object: seen.append(session); return business.resolve(principal_id, tenant_id, role_id)
    result = authorize_tenant_operation(principal_id=_PID, tenant_id=_TENANT, permission_id="platform_billing:release", operation="platform_billing_release", principal_repository=P(), membership_repository=M(), role_assignment_repository=A(), business_role_repository=B(), session=session)
    assert result.authorized is True
    assert seen and all(item is session for item in seen)

# ARTIFACT: test_tenant_authorization.py
# VERSION: v1.18.0-L8-8I-CONFLICT-REVIEW-BINDING-CERT
# AUTHORITY BOUNDARY: frozen current-truth composition certification only; role grants remain policy, not assignment truth
# TENANT POSTURE: exact active principal, membership, tenant_legal_client eligibility, exact client-matter permission-operation binding, and ACTIVE LEGAL_CLIENT assignment are conjunctively required; ACTIVE visibility remains separate
# FAIL-CLOSED POSTURE: missing, inactive, ambiguous, unavailable, mismatched, projected, cross-tenant, system, and financial paths deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT