"""TITLE: WILSY OS Tenant Authorization HTTP Boundary.
VERSION: v1.0.0-TENANT-AUTHORIZATION-HTTP
AUTHORITY: FastAPI dependency translation of frozen durable tenant authorization.
EPITOME: Binds authenticated identity and explicit tenant scope to current truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/tenant_authorization_http.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0 establishes fail-closed tenant authorization HTTP dependency.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: Transport projections never grant authority; malformed scope denies.
TENANT BOUNDARY: X-Tenant-ID is explicit request scope and never membership evidence.
AUTHORITY BOUNDARY: Composes frozen durable authorization only; no authentication or persistence mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from fastapi import Depends, Header, status
from tools.eos.api.exceptions import ForbiddenOperationException, WilsyAPIException
from tools.eos.auth.authentication import get_current_identity, get_principal_authority_repository
from tools.eos.auth.authorization import get_role_assignment_repository
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason, authorize_tenant_operation

VERSION = "v1.0.0-TENANT-AUTHORIZATION-HTTP"
_UNAVAILABLE = frozenset({TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE, TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE, TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE, TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE})
_DENIED = frozenset({TenantAuthorizationReason.INVALID_INPUT, TenantAuthorizationReason.PRINCIPAL_NOT_FOUND, TenantAuthorizationReason.PRINCIPAL_INACTIVE, TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND, TenantAuthorizationReason.MEMBERSHIP_INACTIVE, TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE, TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES, TenantAuthorizationReason.PERMISSION_UNKNOWN, TenantAuthorizationReason.PERMISSION_NOT_CANONICAL, TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH, TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH, TenantAuthorizationReason.PERMISSION_NOT_GRANTED, TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE, TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE, TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED, TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED})

@dataclass(frozen=True, slots=True)
class TenantAuthorizationContext:
    identity: SovereignIdentity
    tenant_id: str
    decision: TenantAuthorizationDecision

class RequireTenantAuthorization:
    """FastAPI dependency requiring one canonical permission and operation."""
    def __init__(self, permission_id: str, operation: str) -> None:
        if not all(isinstance(v, str) and v and v == v.strip() for v in (permission_id, operation)):
            raise ValueError("permission_id and operation must be non-empty trimmed strings")
        self.permission_id, self.operation = permission_id, operation

    async def __call__(self, identity: SovereignIdentity = Depends(get_current_identity), tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"), principal_repository: Any = Depends(get_principal_authority_repository), membership_repository: Any = Depends(get_tenant_membership_repository), role_assignment_repository: Any = Depends(get_role_assignment_repository)) -> TenantAuthorizationContext:
        if not isinstance(tenant_id, str) or not tenant_id or tenant_id != tenant_id.strip():
            raise ForbiddenOperationException("Tenant scope is required.")
        decision = authorize_tenant_operation(principal_id=identity.identity_id, tenant_id=tenant_id, permission_id=self.permission_id, operation=self.operation, principal_repository=principal_repository, membership_repository=membership_repository, business_role_repository=role_assignment_repository, role_assignment_repository=role_assignment_repository)
        if decision.authorized is True and decision.reason is TenantAuthorizationReason.AUTHORIZED:
            return TenantAuthorizationContext(identity=identity, tenant_id=tenant_id, decision=decision)
        if decision.authorized is True or decision.reason is TenantAuthorizationReason.AUTHORIZED:
            raise WilsyAPIException("Authorization decision unavailable.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        if decision.reason in _UNAVAILABLE:
            raise WilsyAPIException("Authorization authority unavailable.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        if decision.reason in _DENIED:
            raise ForbiddenOperationException("Tenant authorization denied.")
        raise WilsyAPIException("Authorization decision unavailable.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

__all__ = ["VERSION", "TenantAuthorizationContext", "RequireTenantAuthorization"]
# ARTIFACT: tenant_authorization_http.py
# VERSION: v1.0.0-TENANT-AUTHORIZATION-HTTP
# AUTHORITY BOUNDARY: HTTP dependency composition only; no authentication truth ownership
# TENANT POSTURE: explicit X-Tenant-ID scope with durable membership required
# FAIL-CLOSED POSTURE: only AUTHORIZED succeeds; unknown reasons deny or unavailable
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
