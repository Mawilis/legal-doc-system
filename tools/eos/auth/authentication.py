"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG212 INSTITUTIONAL AUTHENTICATION - AUTHENTICATION MIDDLEWARE & DEPENDENCY
FILE: tools/eos/auth/authentication.py
===============================================================================
Epitome:
    FastAPI HTTP Bearer and API Key authentication dependencies enforcing Zero Trust
    validation across all FG211/FG212 API endpoints.

Biblical Worth Billions:
    "The name of the Lord is a strong tower; the righteous run into it and are safe."
    — Proverbs 18:10

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/auth/authentication.py
===============================================================================
"""

from fastapi import Security, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from tools.eos.api.exceptions import UnauthorizedAccessException, ForbiddenOperationException
from tools.eos.auth.jwt_provider import verify_access_token
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.audit import log_auth_event

security_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Sovereign hardcoded master API key for system integration
MASTER_SOVEREIGN_API_KEY = "WILSY-OS-MASTER-API-KEY-2026"


async def get_current_identity(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    api_key: str = Security(api_key_header)
) -> SovereignIdentity:
    """Zero Trust dependency: Authenticates incoming requests via JWT or API Key."""
    
    # 1. Check API Key Header
    if api_key:
        if api_key == MASTER_SOVEREIGN_API_KEY:
            identity = SovereignIdentity(
                identity_id="IDENTITY-MASTER-API-KEY",
                tenant_id="TENANT-SOVEREIGN-GLOBAL",
                username="system_master_key",
                roles=["SOVEREIGN_ARCHITECT"],
                permissions=["admin:all", "kernel:read", "kernel:write", "execution:trigger"],
                auth_method="API_KEY"
            )
            log_auth_event("API_KEY_AUTH", identity.username, True, {"tenant": identity.tenant_id})
            return identity
        else:
            log_auth_event("API_KEY_AUTH", "unknown_key", False, {})
            raise UnauthorizedAccessException("Invalid Sovereign API Key provided.")

    # 2. Check Bearer JWT Token
    if credentials and credentials.credentials:
        token = credentials.credentials
        payload = verify_access_token(token)
        if payload:
            identity = SovereignIdentity(
                identity_id=payload.get("identity_id", "UNKNOWN"),
                tenant_id=payload.get("tenant_id", "DEFAULT"),
                username=payload.get("username", "anonymous"),
                roles=payload.get("roles", []),
                is_service_account=payload.get("is_service_account", False),
                auth_method="JWT"
            )
            log_auth_event("JWT_AUTH", identity.username, True, {"tenant": identity.tenant_id})
            return identity
        else:
            log_auth_event("JWT_AUTH", "expired_or_invalid_token", False, {})
            raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")

    # 3. No credentials provided
    log_auth_event("MISSING_CREDENTIALS", "anonymous", False, {})
    raise UnauthorizedAccessException("Missing authentication credentials (Bearer JWT or X-API-Key required).")
