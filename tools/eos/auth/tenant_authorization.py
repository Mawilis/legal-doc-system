"""TITLE: WILSY OS Tenant Authorization Composition.
VERSION: v1.0.2-TENANT-AUTHORIZATION-COMPOSITION
AUTHORITY: Read-only composition of current principal, membership, role and permission truth.
EPITOME: Produces deterministic fail-closed tenant authorization decisions; it does not mutate or transport.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_authorization.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.2 records multi-grant/outage fail-closed evaluation across all granting roles.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Exact scope, active-state, canonical permission, and fail-closed checks; no JWT/header trust.
TENANT BOUNDARY: Requires exact principal and tenant membership; cross-tenant requests deny.
AUTHORITY BOUNDARY: Does not mutate repositories, parse requests, or expose transport errors.
FINANCIAL AUTHORITY BOUNDARY: Financial execution always denies; Kennel EOS remains exclusive.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Protocol, cast
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepositoryError
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError, TenantMembershipRepositoryError
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError, RoleAssignmentRepositoryError
from tools.eos.auth.tenant_business_role_authority import BusinessRoleResolution, resolve_current_tenant_business_role
from tools.eos.auth.tenant_authority_policy import ELIGIBLE, tenant_role_operation_eligibility, requires_system_authority, SystemAuthorityClassification
from tools.eos.auth.permission_namespace import PermissionDisposition, permission_metadata
from tools.eos.auth.roles import get_roles_granting_permission

VERSION = "v1.0.2-TENANT-AUTHORIZATION-COMPOSITION"
class TenantAuthorizationReason(StrEnum):
    AUTHORIZED="AUTHORIZED"; INVALID_INPUT="INVALID_INPUT"; PRINCIPAL_NOT_FOUND="PRINCIPAL_NOT_FOUND"; PRINCIPAL_INACTIVE="PRINCIPAL_INACTIVE"; PRINCIPAL_AUTHORITY_UNAVAILABLE="PRINCIPAL_AUTHORITY_UNAVAILABLE"; MEMBERSHIP_NOT_FOUND="MEMBERSHIP_NOT_FOUND"; MEMBERSHIP_INACTIVE="MEMBERSHIP_INACTIVE"; MEMBERSHIP_AUTHORITY_UNAVAILABLE="MEMBERSHIP_AUTHORITY_UNAVAILABLE"; NO_ACTIVE_TENANT_BUSINESS_ROLE="NO_ACTIVE_TENANT_BUSINESS_ROLE"; MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES="MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES"; TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE="TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"; PERMISSION_UNKNOWN="PERMISSION_UNKNOWN"; PERMISSION_NOT_CANONICAL="PERMISSION_NOT_CANONICAL"; PERMISSION_NAMESPACE_MISMATCH="PERMISSION_NAMESPACE_MISMATCH"; PERMISSION_OPERATION_MISMATCH="PERMISSION_OPERATION_MISMATCH"; PERMISSION_NOT_GRANTED="PERMISSION_NOT_GRANTED"; ROLE_ASSIGNMENT_INACTIVE="ROLE_ASSIGNMENT_INACTIVE"; BUSINESS_ROLE_INELIGIBLE="BUSINESS_ROLE_INELIGIBLE"; SYSTEM_AUTHORITY_REQUIRED="SYSTEM_AUTHORITY_REQUIRED"; FINANCIAL_EXECUTION_PROHIBITED="FINANCIAL_EXECUTION_PROHIBITED"; ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE="ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE"
@dataclass(frozen=True, slots=True)
class TenantAuthorizationDecision:
    authorized: bool
    reason: TenantAuthorizationReason
    business_role: str | None = None
    authorization_role: str | None = None
class PrincipalReader(Protocol):
    def resolve(self, principal_id: str) -> object: ...
class MembershipReader(Protocol):
    def resolve(self, principal_id: str, tenant_id: str) -> object: ...
class AssignmentReader(Protocol):
    def resolve(self, principal_id: str, tenant_id: str, role_id: str) -> object: ...
_BINDINGS = MappingProxyType({"profile_read":"tenant:profile:read","profile_update":"tenant:profile:write","lifecycle_archive":"tenant:lifecycle:archive","membership_read":"tenant:membership:read","membership_invite":"tenant:membership:write","membership_deactivate":"tenant:membership:write","role_assignment_read":"tenant:role_assignment:read","role_grant":"tenant:role_assignment:write","role_revoke":"tenant:role_assignment:write","audit_read":"audit:read"})
def authorize_tenant_operation(*, principal_id: object, tenant_id: object, permission_id: object, operation: object, principal_repository: PrincipalReader, membership_repository: MembershipReader, role_assignment_repository: AssignmentReader, business_role_repository: AssignmentReader) -> TenantAuthorizationDecision:
    """Compose current truth; ELIGIBLE is only one conjunct and never authorization alone."""
    if not all(isinstance(v, str) and v and v == v.strip() for v in (principal_id, tenant_id, permission_id, operation)):
        return TenantAuthorizationDecision(False, TenantAuthorizationReason.INVALID_INPUT)
    pid, tid, perm, op = cast(str, principal_id), cast(str, tenant_id), cast(str, permission_id), cast(str, operation)
    try: principal = principal_repository.resolve(pid)
    except PrincipalAuthorityNotFoundError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PRINCIPAL_NOT_FOUND)
    except PrincipalAuthorityRepositoryError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE)
    if getattr(principal, "status", None) is not PrincipalStatus.ACTIVE: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PRINCIPAL_INACTIVE)
    try: membership = membership_repository.resolve(pid, tid)
    except TenantMembershipNotFoundError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND)
    except TenantMembershipRepositoryError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE)
    if getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE: return TenantAuthorizationDecision(False, TenantAuthorizationReason.MEMBERSHIP_INACTIVE)
    role_result = resolve_current_tenant_business_role(principal_id=pid, tenant_id=tid, repository=business_role_repository)
    if role_result.resolution is not BusinessRoleResolution.RESOLVED: return TenantAuthorizationDecision(False, TenantAuthorizationReason(role_result.resolution.value)) if role_result.resolution.value in TenantAuthorizationReason._value2member_map_ else TenantAuthorizationDecision(False, TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE)
    if op == "financial_execution": return TenantAuthorizationDecision(False, TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED, role_result.role)
    system = requires_system_authority(op)
    if system is SystemAuthorityClassification.SYSTEM_REQUIRED: return TenantAuthorizationDecision(False, TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED, role_result.role)
    if system is SystemAuthorityClassification.UNKNOWN: return TenantAuthorizationDecision(False, TenantAuthorizationReason.INVALID_INPUT, role_result.role)
    try: metadata = permission_metadata(perm)
    except ValueError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PERMISSION_UNKNOWN, role_result.role)
    if metadata.disposition is not PermissionDisposition.CANONICAL: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PERMISSION_NOT_CANONICAL, role_result.role)
    if metadata.namespace != "TENANT" or not metadata.tenant_membership_required or metadata.cross_tenant_capable or metadata.financial_execution_capable: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH, role_result.role)
    if _BINDINGS.get(op) != perm: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH, role_result.role)
    if tenant_role_operation_eligibility(role_result.role, op) != ELIGIBLE: return TenantAuthorizationDecision(False, TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE, role_result.role)
    inactive_seen = False
    active_role: str | None = None
    for auth_role in get_roles_granting_permission(perm):
        try: assignment = role_assignment_repository.resolve(pid, tid, auth_role)
        except RoleAssignmentNotFoundError: continue
        except RoleAssignmentRepositoryError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE, role_result.role)
        if getattr(assignment, "status", None) is RoleAssignmentStatus.ACTIVE:
            active_role = auth_role
        else:
            inactive_seen = True
    if active_role is not None:
        return TenantAuthorizationDecision(True, TenantAuthorizationReason.AUTHORIZED, role_result.role, active_role)
    return TenantAuthorizationDecision(False, TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE if inactive_seen else TenantAuthorizationReason.PERMISSION_NOT_GRANTED, role_result.role)

__all__ = ["VERSION", "TenantAuthorizationReason", "TenantAuthorizationDecision", "authorize_tenant_operation"]
# ARTIFACT: tenant_authorization.py
# VERSION: v1.0.2-TENANT-AUTHORIZATION-COMPOSITION
# AUTHORITY BOUNDARY: current-truth composition only; no mutation or transport
# TENANT POSTURE: exact active principal, membership, role and target tenant required
# FAIL-CLOSED POSTURE: unknown, inactive, missing, ambiguous, unavailable, mismatched, or financial requests deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
