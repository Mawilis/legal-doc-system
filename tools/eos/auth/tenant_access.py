"""Tenant-scoped access dependency enforcing current membership authority.

TITLE: WILSY OS Tenant Membership Access Enforcement
VERSION: v1.0.0-WILSY-TENANT-MEMBERSHIP-ACCESS
AUTHORITY: Tenant context admission after active principal authentication.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_access.py
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.0 adds explicit tenant context and durable ACTIVE membership gating.
COMPLIANCE: Separate tenant access from global authentication and role authorization.
SECURITY/PRIVACY POSTURE: Fail closed without exposing membership existence or secrets.
TENANT BOUNDARY: Explicit X-Tenant-ID context is verified against the principal/tenant pair.
AUTHORITY BOUNDARY: Does not own principal lifecycle, role, credential, or tenant persistence policy.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    A tenant-scoped FastAPI dependency that admits only an ACTIVE global
    principal with a current ACTIVE membership in the selected tenant.

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/tenant_access.py
"""
from __future__ import annotations
from typing import Optional
from fastapi import Depends, Header
from tools.eos.api.exceptions import UnauthorizedAccessException
from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError, TenantMembershipRepository, TenantMembershipRepositoryError, TenantMembershipPersistedRecordInvalidError

def get_tenant_membership_repository() -> TenantMembershipRepository:
    """Provide the frozen membership repository through dependency injection."""
    return TenantMembershipRepository()

async def get_current_tenant_identity(
    tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
    identity: SovereignIdentity = Depends(get_current_identity),
    repository: TenantMembershipRepository = Depends(get_tenant_membership_repository),
) -> SovereignIdentity:
    """Admit explicit tenant context only after current ACTIVE membership resolution."""
    if identity.status is not PrincipalStatus.ACTIVE or not tenant_id or not tenant_id.strip() or tenant_id != tenant_id.strip():
        raise UnauthorizedAccessException("Tenant access denied.")
    try:
        membership = repository.resolve(identity.identity_id, tenant_id)
    except TenantMembershipNotFoundError as error:
        raise UnauthorizedAccessException("Tenant access denied.") from error
    except (TenantMembershipPersistedRecordInvalidError, TenantMembershipRepositoryError) as error:
        raise UnauthorizedAccessException("Tenant access authority is unavailable.") from error
    if membership.status is not TenantMembershipStatus.ACTIVE:
        raise UnauthorizedAccessException("Tenant access denied.")
    return identity.model_copy(update={"tenant_id": tenant_id})

__all__ = ["get_current_tenant_identity", "get_tenant_membership_repository"]

# ARTIFACT: tenant_access.py
# VERSION: v1.0.0-WILSY-TENANT-MEMBERSHIP-ACCESS
# AUTHORITY BOUNDARY: tenant admission after principal and membership ACTIVE gates
# TENANT POSTURE: explicit selected tenant is verified, never inferred or defaulted
# FAIL-CLOSED POSTURE: missing, stale, absent, malformed, or unavailable authority denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
