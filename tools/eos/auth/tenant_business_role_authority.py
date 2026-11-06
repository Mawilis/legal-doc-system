"""TITLE: WILSY OS Tenant Business Role Authority Resolver.
VERSION: v1.1.0-TENANT-BUSINESS-ROLE-DIRECT-RESOLUTION
AUTHORITY: Current durable tenant business-role evidence only; never authorization.
EPITOME: Resolves exactly one ACTIVE canonical business role for an exact principal and tenant.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_business_role_authority.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.1.0 adds single-read resolution for canonical business-role adapters while preserving exact scope and active-only semantics.
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
from typing import Any, Final, Protocol
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError, RoleAssignmentRepositoryError
from tools.eos.auth.tenant_authority_policy import ELIGIBLE, TENANT_ROLES, tenant_role_operation_eligibility
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepositoryError,
)

VERSION = "v1.1.0-TENANT-BUSINESS-ROLE-DIRECT-RESOLUTION"

class BusinessRoleResolution(StrEnum):
    RESOLVED = "RESOLVED"
    NO_ACTIVE_TENANT_BUSINESS_ROLE = "NO_ACTIVE_TENANT_BUSINESS_ROLE"
    MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES = "MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES"
    TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE = "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
    INVALID_INPUT = "INVALID_INPUT"
    NO_ELIGIBLE_TENANT_BUSINESS_ROLE = "NO_ELIGIBLE_TENANT_BUSINESS_ROLE"

@dataclass(frozen=True, slots=True)
class TenantBusinessRoleResult:
    role: str | None
    resolution: BusinessRoleResolution
    evidence_role: str | None = None

class RoleAssignmentReader(Protocol):
    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> object: ...

def resolve_current_tenant_business_role(*, principal_id: object, tenant_id: object, repository: Any, session: Any = None, operation: str | None = None, selected_business_role: str | None = None) -> TenantBusinessRoleResult:
    """Return current durable business-role evidence; membership and authorization remain separate.

    A selected capacity is accepted only from a caller that has already verified
    the principal-bound global session. It narrows the resolver to one exact
    durable role; it never unions permissions or creates a grant.
    """
    if not isinstance(principal_id, str) or not principal_id.strip() or principal_id != principal_id.strip() or not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id != tenant_id.strip():
        return TenantBusinessRoleResult(None, BusinessRoleResolution.INVALID_INPUT)
    if selected_business_role is not None:
        if (
            not isinstance(selected_business_role, str)
            or selected_business_role not in TENANT_ROLES
            or selected_business_role != selected_business_role.strip()
        ):
            return TenantBusinessRoleResult(None, BusinessRoleResolution.INVALID_INPUT)
        try:
            assignment = (
                repository.resolve(principal_id, tenant_id, selected_business_role)
                if session is None
                else repository.resolve(
                    principal_id, tenant_id, selected_business_role, session=session
                )
            )
        except (RoleAssignmentNotFoundError, TenantBusinessRoleNotFoundError):
            return TenantBusinessRoleResult(
                None, BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE
            )
        except (
            RoleAssignmentRepositoryError,
            TenantBusinessRoleRepositoryError,
            AttributeError,
            TypeError,
        ):
            return TenantBusinessRoleResult(
                None, BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE
            )
        if (
            getattr(assignment, "principal_id", None) != principal_id
            or getattr(assignment, "tenant_id", None) != tenant_id
            or getattr(assignment, "business_role", None) != selected_business_role
        ):
            return TenantBusinessRoleResult(
                None, BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE
            )
        if (
            getattr(getattr(assignment, "status", None), "value", None)
            != TenantBusinessRoleStatus.ACTIVE.value
        ):
            return TenantBusinessRoleResult(
                None, BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE
            )
        if (
            operation is not None
            and tenant_role_operation_eligibility(selected_business_role, operation) != ELIGIBLE
        ):
            return TenantBusinessRoleResult(
                None,
                BusinessRoleResolution.NO_ELIGIBLE_TENANT_BUSINESS_ROLE,
                evidence_role=selected_business_role,
            )
        return TenantBusinessRoleResult(
            selected_business_role, BusinessRoleResolution.RESOLVED
        )
    if operation is not None:
        resolve_all = getattr(repository, "resolve_all_business_roles", None)
        if callable(resolve_all):
            try:
                values = resolve_all(principal_id, tenant_id, session=session)
            except (TenantBusinessRoleNotFoundError, RoleAssignmentNotFoundError):
                return TenantBusinessRoleResult(None, BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE)
            except (TenantBusinessRoleRepositoryError, RoleAssignmentRepositoryError, AttributeError, TypeError):
                return TenantBusinessRoleResult(None, BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE)
            active_by_role: dict[str, object] = {}
            if not isinstance(values, (tuple, list)):
                return TenantBusinessRoleResult(None, BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE)
            for value in values:
                if getattr(value, "principal_id", None) != principal_id or getattr(value, "tenant_id", None) != tenant_id:
                    return TenantBusinessRoleResult(None, BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE)
                role = getattr(value, "business_role", None)
                if role not in TENANT_ROLES:
                    return TenantBusinessRoleResult(None, BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE)
                if getattr(getattr(value, "status", None), "value", None) == TenantBusinessRoleStatus.ACTIVE.value:
                    active_by_role[role] = value
            eligible = [role for role in active_by_role if tenant_role_operation_eligibility(role, operation) == ELIGIBLE]
            if len(eligible) == 1:
                return TenantBusinessRoleResult(eligible[0], BusinessRoleResolution.RESOLVED)
            if len(eligible) > 1:
                return TenantBusinessRoleResult(None, BusinessRoleResolution.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES)
            if active_by_role:
                # Retain one exact active role as denial evidence. This does
                # not select it for authorization: resolution remains
                # NO_ELIGIBLE_TENANT_BUSINESS_ROLE and the permission lookup
                # must not run. Multiple active roles remain non-singular.
                sole_active = next(iter(active_by_role)) if len(active_by_role) == 1 else None
                return TenantBusinessRoleResult(
                    None,
                    BusinessRoleResolution.NO_ELIGIBLE_TENANT_BUSINESS_ROLE,
                    evidence_role=sole_active,
                )
            return TenantBusinessRoleResult(None, BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE)

    # The HTTP role reader can resolve the dedicated business-role record
    # directly. Prefer that exact-scope, single-read contract when available;
    # generic role-assignment readers retain the established exhaustive path.
    direct_resolver = getattr(repository, "resolve_current_business_role", None)
    if callable(direct_resolver):
        try:
            assignment = (
                direct_resolver(principal_id, tenant_id)
                if session is None
                else direct_resolver(principal_id, tenant_id, session=session)
            )
        except (RoleAssignmentNotFoundError, TenantBusinessRoleNotFoundError):
            return TenantBusinessRoleResult(
                None, BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE
            )
        except (
            RoleAssignmentRepositoryError,
            TenantBusinessRoleRepositoryError,
            AttributeError,
            TypeError,
        ):
            return TenantBusinessRoleResult(
                None,
                BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE,
            )

        if (
            getattr(assignment, "principal_id", None) != principal_id
            or getattr(assignment, "tenant_id", None) != tenant_id
        ):
            return TenantBusinessRoleResult(
                None,
                BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE,
            )

        role = getattr(assignment, "business_role", None)
        if role not in TENANT_ROLES:
            return TenantBusinessRoleResult(
                None, BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE
            )
        if (
            getattr(getattr(assignment, "status", None), "value", None)
            == TenantBusinessRoleStatus.ACTIVE.value
        ):
            if operation is not None and tenant_role_operation_eligibility(role, operation) != ELIGIBLE:
                return TenantBusinessRoleResult(
                    None,
                    BusinessRoleResolution.NO_ELIGIBLE_TENANT_BUSINESS_ROLE,
                    evidence_role=role,
                )
            return TenantBusinessRoleResult(role, BusinessRoleResolution.RESOLVED)
        return TenantBusinessRoleResult(
            None, BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE
        )

    active: list[str] = []
    try:
        for role_id in TENANT_ROLES:
            try:
                assignment = repository.resolve(principal_id, tenant_id, role_id) if session is None else repository.resolve(principal_id, tenant_id, role_id, session=session)
            except RoleAssignmentNotFoundError:
                continue
            if getattr(getattr(assignment, "status", None), "value", None) == TenantBusinessRoleStatus.ACTIVE.value:
                active.append(role_id)
    except (RoleAssignmentRepositoryError, AttributeError, TypeError):
        return TenantBusinessRoleResult(None, BusinessRoleResolution.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE)
    if len(active) == 1:
        if operation is not None and tenant_role_operation_eligibility(active[0], operation) != ELIGIBLE:
            return TenantBusinessRoleResult(
                None,
                BusinessRoleResolution.NO_ELIGIBLE_TENANT_BUSINESS_ROLE,
                evidence_role=active[0],
            )
        return TenantBusinessRoleResult(active[0], BusinessRoleResolution.RESOLVED)
    if len(active) > 1:
        return TenantBusinessRoleResult(None, BusinessRoleResolution.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES)
    return TenantBusinessRoleResult(None, BusinessRoleResolution.NO_ACTIVE_TENANT_BUSINESS_ROLE)

__all__ = ["VERSION", "TENANT_ROLES", "BusinessRoleResolution", "TenantBusinessRoleResult", "resolve_current_tenant_business_role"]

# ARTIFACT: tenant_business_role_authority.py
# VERSION: v1.1.0-TENANT-BUSINESS-ROLE-DIRECT-RESOLUTION
# AUTHORITY BOUNDARY: current business-role evidence only; no authorization or permission grant
# TENANT POSTURE: exact principal/tenant/role lookup; membership remains separate
# FAIL-CLOSED POSTURE: absent, revoked, ambiguous, malformed, and unavailable state denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
