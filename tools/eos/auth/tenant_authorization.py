"""TITLE: WILSY OS Tenant Authorization Composition.
VERSION: v1.7.0-M11-R8-R3B-P8-P3D-P4A
AUTHORITY: Read-only composition of current principal, membership, role and permission truth.
EPITOME: Produces deterministic fail-closed tenant authorization decisions; it does not mutate or transport.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_authorization.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-09.
CHANGELOG: v1.7.0-M11-R8-R3B-P8-P3D-P4A binds four exact credential-security
operations to four dedicated permissions without changing decision schema.
v1.6.0-M11-R8-R3B-P8-P3B-I2-R3 binds the explicit
tenant_inbound_merchant_configuration_remediate operation to its dedicated
permission; no state parsing or lifecycle execution authority is added.
v1.5.0-M11-R8-R3B-P8-P3A binds eight tenant inbound
merchant-configuration/provider-policy operations to their exact permissions;
authorization remains conjunctive and fail-closed with no automatic owner grant.
v1.4.0-M11-R8-R3B-P6A binds the provider-neutral
inbound_collection_authorization_create operation to its exact tenant
privilege; no typed authorization or durable evidence is created here.
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
from typing import Any
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

VERSION = "v1.7.0-M11-R8-R3B-P8-P3D-P4A"
class TenantAuthorizationReason(StrEnum):
    AUTHORIZED="AUTHORIZED"; INVALID_INPUT="INVALID_INPUT"; PRINCIPAL_NOT_FOUND="PRINCIPAL_NOT_FOUND"; PRINCIPAL_INACTIVE="PRINCIPAL_INACTIVE"; PRINCIPAL_AUTHORITY_UNAVAILABLE="PRINCIPAL_AUTHORITY_UNAVAILABLE"; MEMBERSHIP_NOT_FOUND="MEMBERSHIP_NOT_FOUND"; MEMBERSHIP_INACTIVE="MEMBERSHIP_INACTIVE"; MEMBERSHIP_AUTHORITY_UNAVAILABLE="MEMBERSHIP_AUTHORITY_UNAVAILABLE"; NO_ACTIVE_TENANT_BUSINESS_ROLE="NO_ACTIVE_TENANT_BUSINESS_ROLE"; MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES="MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES"; TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE="TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"; PERMISSION_UNKNOWN="PERMISSION_UNKNOWN"; PERMISSION_NOT_CANONICAL="PERMISSION_NOT_CANONICAL"; PERMISSION_NAMESPACE_MISMATCH="PERMISSION_NAMESPACE_MISMATCH"; PERMISSION_OPERATION_MISMATCH="PERMISSION_OPERATION_MISMATCH"; PERMISSION_NOT_GRANTED="PERMISSION_NOT_GRANTED"; ROLE_ASSIGNMENT_INACTIVE="ROLE_ASSIGNMENT_INACTIVE"; BUSINESS_ROLE_INELIGIBLE="BUSINESS_ROLE_INELIGIBLE"; SYSTEM_AUTHORITY_REQUIRED="SYSTEM_AUTHORITY_REQUIRED"; FINANCIAL_EXECUTION_PROHIBITED="FINANCIAL_EXECUTION_PROHIBITED"; ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE="ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE"
@dataclass(frozen=True, slots=True)
class TenantAuthorizationDecision:
    authorized: bool
    reason: TenantAuthorizationReason
    business_role: str | None = None
    authorization_role: str | None = None
class PrincipalReader(Protocol):
    def resolve(self, principal_id: str, *, session: Any = None) -> object: ...
class MembershipReader(Protocol):
    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> object: ...
class AssignmentReader(Protocol):
    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> object: ...
_BINDINGS = MappingProxyType({"profile_read":"tenant:profile:read","profile_update":"tenant:profile:write","lifecycle_archive":"tenant:lifecycle:archive","membership_read":"tenant:membership:read","membership_invite":"tenant:membership:write","membership_deactivate":"tenant:membership:write","role_assignment_read":"tenant:role_assignment:read","role_grant":"tenant:role_assignment:write","role_revoke":"tenant:role_assignment:write","audit_read":"audit:read","plan_read":"plan:read","plan_create":"plan:manage","plan_update":"plan:manage","plan_archive":"plan:manage","subscription_read":"subscription:read","subscription_audit_read":"subscription:read","subscription_metrics_read":"subscription:read","subscription_create":"subscription:manage","subscription_update":"subscription:manage","subscription_archive":"subscription:manage","subscription_pause":"subscription:manage","subscription_resume":"subscription:manage","subscription_cancel":"subscription:manage","subscription_upgrade":"subscription:manage","subscription_downgrade":"subscription:manage","subscription_reactivate":"subscription:manage","platform_billing_release":"platform_billing:release","platform_billing_provider_policy_create":"platform_billing:provider_policy:admin","platform_billing_provider_policy_revise":"platform_billing:provider_policy:admin","platform_billing_provider_policy_activate":"platform_billing:provider_policy:admin","platform_billing_provider_policy_revoke":"platform_billing:provider_policy:admin","inbound_collection_authorization_create":"inbound_collection:authorization:create","tenant_inbound_merchant_configuration_register":"inbound_merchant_configuration:register","tenant_inbound_merchant_configuration_lifecycle_transition":"inbound_merchant_configuration:lifecycle","tenant_inbound_merchant_configuration_compromise":"inbound_merchant_configuration:security","tenant_inbound_merchant_configuration_remediate":"inbound_merchant_configuration:remediate","tenant_inbound_provider_policy_create":"inbound_provider_policy:author","tenant_inbound_provider_policy_revise":"inbound_provider_policy:author","tenant_inbound_provider_policy_activate":"inbound_provider_policy:activate","tenant_inbound_provider_policy_deactivate":"inbound_provider_policy:deactivate","tenant_inbound_provider_policy_emergency_disable":"inbound_provider_policy:emergency_disable","tenant_inbound_provider_credential_security_eligibility_issue":"inbound_provider_credential_security:eligibility_issue","tenant_inbound_provider_credential_security_revoke":"inbound_provider_credential_security:revoke","tenant_inbound_provider_credential_security_compromise":"inbound_provider_credential_security:compromise","tenant_inbound_provider_credential_security_rotate":"inbound_provider_credential_security:rotate"})
def authorize_tenant_operation(*, principal_id: object, tenant_id: object, permission_id: object, operation: object, principal_repository: Any, membership_repository: Any, role_assignment_repository: Any, business_role_repository: Any, session: Any = None) -> TenantAuthorizationDecision:
    """Compose current truth; ELIGIBLE is only one conjunct and never authorization alone."""
    if not all(isinstance(v, str) and v and v == v.strip() for v in (principal_id, tenant_id, permission_id, operation)):
        return TenantAuthorizationDecision(False, TenantAuthorizationReason.INVALID_INPUT)
    pid, tid, perm, op = cast(str, principal_id), cast(str, tenant_id), cast(str, permission_id), cast(str, operation)
    try: principal = principal_repository.resolve(pid) if session is None else principal_repository.resolve(pid, session=session)
    except PrincipalAuthorityNotFoundError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PRINCIPAL_NOT_FOUND)
    except PrincipalAuthorityRepositoryError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE)
    if getattr(principal, "status", None) is not PrincipalStatus.ACTIVE: return TenantAuthorizationDecision(False, TenantAuthorizationReason.PRINCIPAL_INACTIVE)
    try: membership = membership_repository.resolve(pid, tid) if session is None else membership_repository.resolve(pid, tid, session=session)
    except TenantMembershipNotFoundError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND)
    except TenantMembershipRepositoryError: return TenantAuthorizationDecision(False, TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE)
    if getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE: return TenantAuthorizationDecision(False, TenantAuthorizationReason.MEMBERSHIP_INACTIVE)
    role_result = resolve_current_tenant_business_role(principal_id=pid, tenant_id=tid, repository=business_role_repository, session=session)
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
        try: assignment = role_assignment_repository.resolve(pid, tid, auth_role) if session is None else role_assignment_repository.resolve(pid, tid, auth_role, session=session)
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
# VERSION: v1.7.0-M11-R8-R3B-P8-P3D-P4A
# AUTHORITY BOUNDARY: current-truth composition only; no mutation or transport
# TENANT POSTURE: exact active principal, membership, role and target tenant required
# FAIL-CLOSED POSTURE: unknown, inactive, missing, ambiguous, unavailable, mismatched, or financial requests deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
