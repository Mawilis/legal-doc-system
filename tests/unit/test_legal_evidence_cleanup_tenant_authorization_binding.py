"""TITLE: WILSY OS Legal Evidence Cleanup Tenant Authorization Certificate.
VERSION: v1.0.0-L10A2R-C4D6E-A3-P1D-CLEANUP-AUTHORIZATION-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS IAM certification only.
EPITOME: Certifies the exact Legal Evidence cleanup actor authorization
         conjunction before any cleanup command or provider mutation exists.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_cleanup_tenant_authorization_binding.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-10-02.
CHANGELOG:
    2026-10-02 v1.0.0-L10A2R-C4D6E-A3-P1D-CLEANUP-AUTHORIZATION-CERT
    establishes direct certification of the exact
    legal_evidence_cleanup_authorize ->
    legal_operations:evidence_cleanup:authorize conjunction across ACTIVE
    principal, ACTIVE membership, tenant_legal_partner business-role evidence
    and ACTIVE LEGAL_PARTNER assignment. It separately proves denial for
    inactive principal, inactive membership, wrong business role, missing or
    revoked final role, crossed permission and malformed operation vocabulary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Current durable authority truth only; caller/JWT
                          projection cannot manufacture authority.
TENANT BOUNDARY: Exact principal and tenant scope are required throughout.
AUTHORITY BOUNDARY: Actor command-admission authorization only. Authorization
                    does not bind A2 cleanup evidence by itself and does not
                    execute, request or prove provider deletion.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from dataclasses import dataclass
import inspect

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
)
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
import tools.eos.auth.tenant_authorization as tenant_authorization
from tools.eos.auth.tenant_membership import TenantMembershipStatus


VERSION = (
    "v1.0.0-L10A2R-C4D6E-A3-P1D-"
    "CLEANUP-AUTHORIZATION-CERT"
)

PID = "principal-cleanup-cert"
TENANT = "tenant-cleanup-cert"
OPERATION = "legal_evidence_cleanup_authorize"
PERMISSION = "legal_operations:evidence_cleanup:authorize"


@dataclass(frozen=True, slots=True)
class _Record:
    status: object


class _PrincipalRepository:
    def __init__(
        self,
        status: PrincipalStatus = PrincipalStatus.ACTIVE,
    ) -> None:
        self.status = status

    def resolve(
        self,
        principal_id: str,
        *,
        session: object = None,
    ) -> _Record:
        assert principal_id == PID
        return _Record(self.status)


class _MembershipRepository:
    def __init__(
        self,
        status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    ) -> None:
        self.status = status

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: object = None,
    ) -> _Record:
        assert (principal_id, tenant_id) == (PID, TENANT)
        return _Record(self.status)


class _BusinessRoleRepository:
    def __init__(
        self,
        role: str = "tenant_legal_partner",
    ) -> None:
        self.role = role

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: object = None,
    ) -> _Record:
        assert (principal_id, tenant_id) == (PID, TENANT)
        if role_id == self.role:
            return _Record(RoleAssignmentStatus.ACTIVE)
        raise RoleAssignmentNotFoundError(role_id)


class _AuthorizationRoleRepository:
    def __init__(
        self,
        status: RoleAssignmentStatus | None = RoleAssignmentStatus.ACTIVE,
    ) -> None:
        self.status = status
        self.calls: list[str] = []

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: object = None,
    ) -> _Record:
        assert (principal_id, tenant_id) == (PID, TENANT)
        self.calls.append(role_id)
        if role_id != "LEGAL_PARTNER" or self.status is None:
            raise RoleAssignmentNotFoundError(role_id)
        return _Record(self.status)


def _decision(
    *,
    permission: object = PERMISSION,
    operation: object = OPERATION,
    principal_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    business_role: str = "tenant_legal_partner",
    final_role_status: RoleAssignmentStatus | None = RoleAssignmentStatus.ACTIVE,
) -> TenantAuthorizationDecision:
    return authorize_tenant_operation(
        principal_id=PID,
        tenant_id=TENANT,
        permission_id=permission,
        operation=operation,
        principal_repository=_PrincipalRepository(principal_status),
        membership_repository=_MembershipRepository(membership_status),
        business_role_repository=_BusinessRoleRepository(business_role),
        role_assignment_repository=_AuthorizationRoleRepository(
            final_role_status
        ),
    )


def test_exact_cleanup_binding_and_full_conjunction_authorize() -> None:
    """Only the exact Partner conjunction authorizes actor command admission."""
    assert tenant_authorization.VERSION == (
        "v1.30.0-L10A2R-C4D6E-A3-P1D-"
        "LEGAL-EVIDENCE-CLEANUP-AUTHORIZATION-BINDING"
    )
    assert tenant_authorization._BINDINGS[OPERATION] == PERMISSION
    assert list(tenant_authorization._BINDINGS).count(OPERATION) == 1

    assert _decision() == TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_legal_partner",
        "LEGAL_PARTNER",
    )


def test_inactive_principal_denies_before_cleanup_authority() -> None:
    result = _decision(
        principal_status=PrincipalStatus.SUSPENDED,
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE


def test_inactive_membership_denies_before_cleanup_authority() -> None:
    result = _decision(
        membership_status=TenantMembershipStatus.SUSPENDED,
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE


def test_wrong_business_role_cannot_cross_into_cleanup_authority() -> None:
    result = _decision(
        business_role="tenant_legal_attorney",
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    assert result.authorization_role is None


def test_missing_and_revoked_partner_assignment_deny() -> None:
    missing = _decision(
        final_role_status=None,
    )
    assert missing.authorized is False
    assert missing.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    revoked = _decision(
        final_role_status=RoleAssignmentStatus.REVOKED,
    )
    assert revoked.authorized is False
    assert revoked.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE


def test_crossed_permission_denies_exact_binding() -> None:
    result = _decision(
        permission="legal_operations:evidence:write",
    )
    assert result.authorized is False
    assert result.reason is (
        TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    )


def test_malformed_cleanup_operation_aliases_fail_closed() -> None:
    malformed = (
        "legal_evidence_cleanup",
        "legal_evidence_cleanup_delete",
        "legal_evidence_cleanup_execute",
        "legal_evidence_cleanup_authorize ",
        " legal_evidence_cleanup_authorize",
        "LEGAL_EVIDENCE_CLEANUP_AUTHORIZE",
    )

    for operation in malformed:
        result = _decision(operation=operation)
        assert result.authorized is False
        assert result.reason in {
            TenantAuthorizationReason.INVALID_INPUT,
            TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH,
        }
        assert tenant_authorization._BINDINGS.get(operation) is None


def test_actor_authorized_is_not_provider_delete_executed() -> None:
    """IAM authorization remains strictly before A2 binding and provider mutation."""
    result = _decision()
    assert result.authorized is True

    source = inspect.getsource(tenant_authorization)

    forbidden_execution_symbols = (
        "delete_object",
        "provider_delete",
        "cleanup_execute",
        "cleanup_execution",
        "LegalEvidenceProviderCleanupAuthorizationRegistry",
        "create_or_replay",
    )

    for symbol in forbidden_execution_symbols:
        assert symbol not in source


# ARTIFACT: test_legal_evidence_cleanup_tenant_authorization_binding.py
# VERSION: v1.0.0-L10A2R-C4D6E-A3-P1D-CLEANUP-AUTHORIZATION-CERT
# AUTHORITY BOUNDARY: actor command-admission authorization certificate only; no cleanup execution
# TENANT POSTURE: ACTIVE principal + ACTIVE membership + tenant_legal_partner + exact permission/operation + ACTIVE LEGAL_PARTNER are conjunctively required
# FAIL-CLOSED POSTURE: inactive, missing, revoked, crossed and malformed authority facts deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
