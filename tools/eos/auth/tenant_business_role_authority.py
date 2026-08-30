"""TITLE: WILSY OS Tenant Business Role Authority Resolver.
VERSION: v1.0.0-TENANT-BUSINESS-ROLE-AUTHORITY
AUTHORITY: Current durable tenant business-role evidence only; never authorization.
EPITOME: Resolves exactly one ACTIVE canonical business role for an exact principal and tenant.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_business_role_authority.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0 establishes exact-scope, active-only, ambiguity-safe role evidence resolution.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: No caller role, JWT, Node projection, persistence mutation, or financial authority is trusted.
TENANT BOUNDARY: Every lookup binds exact principal_id, tenant_id, and canonical role_id.
AUTHORITY BOUNDARY: Business eligibility evidence only; does not authenticate, authorize, grant permissions, or prove membership.
FINANCIAL AUTHORITY BOUNDARY: No financial semantics; Kennel EOS remains exclusive.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Final, Protocol
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError, RoleAssignmentRepositoryError
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES

VERSION = "v1.0.0-TENANT-BUSINESS-ROLE-AUTHORITY"

class BusinessRoleResolution(StrEnum):
    RESOLVED = "RESOLVED"
    NO_ACTIVE_TENANT_BUSINESS_ROLE = "NO_ACTIVE_TENANT_BUSINESS_ROLE"
    MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES = "MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES"
    TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE = "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
    INVALID_INPUT = "INVALID_INPUT"

@dataclass(frozen=True, slots=True)
class TenantBusinessRoleResult:
    role: str | None
    resolution: BusinessRoleResolution

class RoleAssignmentReader(Protocol):
    def resolve(self, principal_id: str, tenant_id: str, role_id: str) -> object: ...

def resolve_current_tenant_business_role(*, principal_id: object, tenant_id: object, repository: RoleAssignmentReader) -> TenantBusinessRoleResult:
    """Return current durable business-role evidence; membership and authorization remain separate."""
    if not isinstance(principal_id, str) or not principal_id.strip() or principal_id != principal_id.strip() or not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id != tenant_id.strip():
        return TenantBusinessRoleResult(None, BusinessRoleResolution.INVALID_INPUT)
    active: list[str] = []
    try:
        for role_id in TENANT_ROLES:
            try:
                assignment = repository.resolve(principal_id, tenant_id, role_id)
            except RoleAssignmentNotFoundError:
                continue
            if getattr(assignment, "status", None) is RoleAssignmentStatus.ACTIVE:
                active.append(role_id)
    except (RoleAssignmentRepositoryError, AttributeError, TypeError):
        return TenantBusinessRoleResult(None, BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE)
    if len(active) == 1:
        return TenantBusinessRoleResult(active[0], BusinessRoleResolution.RESOLVED)
    if len(active) > 1:
        return TenantBusinessRoleResult(None, BusinessRoleResolution.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES)
    return TenantBusinessRoleResult(None, BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE)

__all__ = ["VERSION", "TENANT_ROLES", "BusinessRoleResolution", "TenantBusinessRoleResult", "resolve_current_tenant_business_role"]

# ARTIFACT: tenant_business_role_authority.py
# VERSION: v1.0.0-TENANT-BUSINESS-ROLE-AUTHORITY
# AUTHORITY BOUNDARY: current business-role evidence only; no authorization or permission grant
# TENANT POSTURE: exact principal/tenant/role lookup; membership remains separate
# FAIL-CLOSED POSTURE: absent, revoked, ambiguous, malformed, and unavailable state denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
