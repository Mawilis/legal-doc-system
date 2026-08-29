"""Wilsy OS authentication projection guarded by durable principal authority.

TITLE: WILSY OS Authentication Projection
VERSION: v1.1.0-PRINCIPAL-AUTHORITY-PROJECTION
AUTHORITY: Cryptographic credential verification and current PrincipalAuthority gating.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authentication.py
CHANGELOG: v1.1.0 removes synthetic identity/API-key authority and requires durable ACTIVE status.
SECURITY/PRIVACY POSTURE: Missing or malformed credentials fail closed; secrets are never logged.
TENANT BOUNDARY: Tenant claims remain non-authoritative request context; membership is a later contract.
AUTHORITY BOUNDARY: SovereignIdentity is a projection, not lifecycle, credential, tenant, role, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS exclusively owns financial execution.

Epitome:
    Authentication verifies a credential, resolves the exact durable principal,
    and only then returns a projection for downstream authorization.

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/authentication.py
"""
from __future__ import annotations

from typing import Any, Optional
from fastapi import Depends, Request, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from tools.eos.api.exceptions import UnauthorizedAccessException
from tools.eos.auth.audit import log_auth_event
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.jwt_provider import verify_access_token
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError
from tools.eos.auth.principal_status import PrincipalStatus

security_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_principal_authority_repository() -> PrincipalAuthorityRepository:
    """Provide the durable authority repository through FastAPI dependency injection."""
    return PrincipalAuthorityRepository()

def _claim(payload: dict[str, Any], name: str) -> Optional[str]:
    """Return a non-empty string claim without creating a sentinel value."""
    value = payload.get(name)
    return value if isinstance(value, str) and value.strip() else None

def _resolve_authority(repository: PrincipalAuthorityRepository, principal_id: str) -> PrincipalAuthority:
    """Resolve current authority and collapse absence/infrastructure to safe denial."""
    try:
        return repository.get(principal_id)
    except PrincipalAuthorityNotFoundError as error:
        raise UnauthorizedAccessException("Invalid authentication principal.") from error
    except PrincipalAuthorityRepositoryError as error:
        raise UnauthorizedAccessException("Authentication authority is unavailable.") from error

async def get_current_identity(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    api_key: Optional[str] = Security(api_key_header),
    repository: PrincipalAuthorityRepository = Depends(get_principal_authority_repository),
) -> SovereignIdentity:
    """Authenticate a credential only after durable ACTIVE principal resolution."""
    del request
    if api_key:
        log_auth_event("API_KEY_AUTH", "unresolved", False, {"reason": "principal_resolution_required"})
        raise UnauthorizedAccessException("API-key principal is not mapped to durable authority.")
    if not credentials or not credentials.credentials:
        log_auth_event("MISSING_CREDENTIALS", "unresolved", False, {})
        raise UnauthorizedAccessException("Missing authentication credentials.")
    payload = verify_access_token(credentials.credentials)
    if not payload:
        log_auth_event("JWT_AUTH", "unresolved", False, {"reason": "invalid_credential"})
        raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")
    principal_id = _claim(payload, "identity_id")
    if principal_id is None:
        log_auth_event("JWT_AUTH", "unresolved", False, {"reason": "missing_principal_reference"})
        raise UnauthorizedAccessException("Authentication principal is required.")
    authority = _resolve_authority(repository, principal_id)
    if authority.status is not PrincipalStatus.ACTIVE:
        log_auth_event("JWT_AUTH", principal_id, False, {"reason": "principal_not_active"})
        raise UnauthorizedAccessException("Authentication principal is not active.")
    tenant_id = _claim(payload, "tenant_id")
    if tenant_id is None:
        raise UnauthorizedAccessException("Tenant context is required.")
    identity = SovereignIdentity(
        identity_id=authority.principal_id,
        tenant_id=tenant_id,
        username=_claim(payload, "username"),
        email=_claim(payload, "email"),
        roles=payload.get("roles", []) if isinstance(payload.get("roles", []), list) else [],
        permissions=payload.get("permissions", []) if isinstance(payload.get("permissions", []), list) else [],
        auth_method="JWT",
        status=authority.status,
    )
    log_auth_event("JWT_AUTH", authority.principal_id, True, {"tenant": tenant_id})
    return identity

__all__ = ["get_current_identity", "get_principal_authority_repository", "security_scheme", "api_key_header"]

# ARTIFACT: authentication.py
# VERSION: v1.1.0-PRINCIPAL-AUTHORITY-PROJECTION
# AUTHORITY BOUNDARY: credential verification plus durable ACTIVE principal gate
# TENANT POSTURE: tenant claim is context only; membership authority is separate
# FAIL-CLOSED POSTURE: missing, invalid, absent, unavailable, suspended, and revoked authority denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
