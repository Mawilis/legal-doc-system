"""Wilsy OS authentication projection guarded by durable principal authority.

TITLE: WILSY OS Authentication Projection
VERSION: v1.2.0-R10C2F9-ACCESS-PURPOSE-DURABLE-REVISION-ENFORCEMENT
AUTHORITY: Cryptographic credential verification and current PrincipalAuthority gating.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authentication.py
CHANGELOG:
    v1.2.0-R10C2F9-ACCESS-PURPOSE-DURABLE-REVISION-ENFORCEMENT requires
    ACCESS purpose and a fresh exact durable credential revision before any
    protected identity projection; PRE_AUTH and legacy-purpose tokens fail
    closed without changing router, provider, or AuthRegistry authority.
    v1.1.0 removes synthetic identity/API-key authority and requires durable ACTIVE status.
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

from pymongo.errors import PyMongoError
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from tools.eos.api.exceptions import UnauthorizedAccessException
from tools.eos.auth.audit import log_auth_event
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.jwt_provider import CREDENTIAL_REVISION_MAX, TokenPurpose, verify_access_token
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.global_principal_session_authority import GlobalPrincipalSessionAuthority
from tools.eos.auth.global_principal_system_session_authority import (
    SESSION_COLLECTION as SYSTEM_SESSION_COLLECTION,
    GlobalPrincipalSystemSessionAuthority,
    GlobalPrincipalSystemSessionRejected,
    GlobalPrincipalSystemSessionUnavailable,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.auth.auth_registry import AuthRegistry

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

def _valid_access_revision(value: object) -> bool:
    """Accept only the provider's bounded, non-boolean integer revision shape."""
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and 0 <= value <= CREDENTIAL_REVISION_MAX
    )

async def get_current_identity(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    api_key: Optional[str] = Security(api_key_header),
    repository: PrincipalAuthorityRepository = Depends(get_principal_authority_repository),
) -> SovereignIdentity:
    """Authenticate one ACCESS JWT against current durable principal authority.

    Cryptographic verification is followed by exact ACCESS-purpose and
    credential-revision checks.  The durable revision is read through
    ``AuthRegistry.get_credential_revision`` only after the canonical principal
    is ACTIVE, and the token is accepted only on exact equality.  PRE_AUTH,
    legacy-purpose, stale, future, malformed, missing, and unavailable states
    fail closed without exposing revision values or owning persistence.
    """
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
    if payload.get("token_purpose") != TokenPurpose.ACCESS.value:
        log_auth_event("JWT_AUTH", "unresolved", False, {"reason": "access_purpose_required"})
        raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")
    token_revision = payload.get("credential_revision")
    if not _valid_access_revision(token_revision):
        log_auth_event("JWT_AUTH", "unresolved", False, {"reason": "credential_revision_required"})
        raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")
    if not isinstance(token_revision, int) or isinstance(token_revision, bool):
        raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")
    principal_id = _claim(payload, "identity_id")
    if principal_id is None:
        log_auth_event("JWT_AUTH", "unresolved", False, {"reason": "missing_principal_reference"})
        raise UnauthorizedAccessException("Authentication principal is required.")
    authority = _resolve_authority(repository, principal_id)
    if authority.status is not PrincipalStatus.ACTIVE:
        log_auth_event("JWT_AUTH", principal_id, False, {"reason": "principal_not_active"})
        raise UnauthorizedAccessException("Authentication principal is not active.")
    principal_scope = payload.get("principal_scope")
    if principal_scope == "SYSTEM":
        tenant_scope = _claim(payload, "tenant_id")
        session_reference = _claim(payload, "session_reference")
        workspace_id = _claim(payload, "workspace_id")
        roles = payload.get("roles")
        permissions = payload.get("permissions")
        if (
            tenant_scope != "SYSTEM"
            or session_reference is None
            or workspace_id != "SYSTEM_SERVICES"
            or roles != ["SYSTEM_SERVICES"]
            or permissions != []
        ):
            raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")
        client = get_client()
        database = get_database()
        authorizer = getattr(request.app.state, "system_services_authorizer", None)
        if client is None or database is None or authorizer is None:
            raise HTTPException(status_code=503, detail="SYSTEM authentication authority is unavailable.")
        session = client.start_session()
        try:
            session.start_transaction()
            current = GlobalPrincipalSystemSessionAuthority(
                sessions=database[SYSTEM_SESSION_COLLECTION],
                authorizer=authorizer,
            ).is_session_current(
                principal_id=authority.principal_id,
                session_reference=session_reference,
                expected_credential_revision=token_revision,
                session=session,
            )
            if not current:
                session.abort_transaction()
                raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")
            session.commit_transaction()
        except UnauthorizedAccessException:
            raise
        except GlobalPrincipalSystemSessionRejected as error:
            marker = getattr(session, "in_transaction", False)
            if (marker() if callable(marker) else marker) is True:
                session.abort_transaction()
            raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.") from error
        except (GlobalPrincipalSystemSessionUnavailable, PyMongoError) as error:
            marker = getattr(session, "in_transaction", False)
            if (marker() if callable(marker) else marker) is True:
                session.abort_transaction()
            raise HTTPException(status_code=503, detail="SYSTEM authentication authority is unavailable.") from error
        except Exception as error:
            marker = getattr(session, "in_transaction", False)
            if (marker() if callable(marker) else marker) is True:
                session.abort_transaction()
            raise HTTPException(status_code=503, detail="SYSTEM authentication authority is unavailable.") from error
        finally:
            session.end_session()
        identity = SovereignIdentity(
            identity_id=authority.principal_id,
            tenant_id="SYSTEM",
            username=_claim(payload, "username"),
            email=_claim(payload, "email"),
            roles=["SYSTEM_SERVICES"],
            permissions=[],
            auth_method="JWT",
            status=authority.status,
            session_reference=session_reference,
        )
        log_auth_event("SYSTEM_JWT_AUTH", authority.principal_id, True, {"scope": "SYSTEM"})
        return identity

    tenant_id = _claim(payload, "tenant_id")
    if tenant_id is None:
        raise UnauthorizedAccessException("Tenant context is required.")

    if principal_scope == "GLOBAL":
        session_reference = _claim(payload, "session_reference")
        workspace_id = _claim(payload, "workspace_id")
        roles = payload.get("roles")
        permissions = payload.get("permissions")
        membership_revision = payload.get("membership_revision")
        capacity_revision = payload.get("capacity_revision")
        if (
            session_reference is None
            or workspace_id is None
            or not isinstance(roles, list)
            or len(roles) != 1
            or not isinstance(roles[0], str)
            or not roles[0].strip()
            or permissions != []
            or not _valid_access_revision(membership_revision)
            or not _valid_access_revision(capacity_revision)
        ):
            raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")
        current = GlobalPrincipalSessionAuthority().is_session_current(
            principal_id=authority.principal_id,
            tenant_id=tenant_id,
            session_reference=session_reference,
            expected_business_role=roles[0],
            expected_workspace_id=workspace_id,
            expected_credential_revision=token_revision,
            expected_membership_revision=membership_revision,
            expected_capacity_revision=capacity_revision,
        )
        if not current:
            raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")
        identity = SovereignIdentity(
            identity_id=authority.principal_id,
            tenant_id=tenant_id,
            username=_claim(payload, "username"),
            email=_claim(payload, "email"),
            roles=roles,
            permissions=[],
            auth_method="JWT",
            status=authority.status,
            session_reference=session_reference,
            principal_scope="GLOBAL",
            workspace_id=workspace_id,
            membership_revision=membership_revision,
            capacity_revision=capacity_revision,
        )
        log_auth_event("GLOBAL_JWT_AUTH", authority.principal_id, True, {"tenant": tenant_id})
        return identity
    if principal_scope not in (None, "TENANT"):
        raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")

    try:
        durable_revision = AuthRegistry().get_credential_revision(
            tenant_id,
            authority.principal_id,
        )
    except Exception as error:
        log_auth_event(
            "JWT_AUTH",
            authority.principal_id,
            False,
            {"reason": "credential_revision_unavailable"},
        )
        raise UnauthorizedAccessException("Authentication authority is unavailable.") from error
    if token_revision != durable_revision:
        log_auth_event(
            "JWT_AUTH",
            authority.principal_id,
            False,
            {"reason": "credential_revision_mismatch"},
        )
        raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")
    identity = SovereignIdentity(
        identity_id=authority.principal_id,
        tenant_id=tenant_id,
        username=_claim(payload, "username"),
        email=_claim(payload, "email"),
        roles=payload.get("roles", []) if isinstance(payload.get("roles", []), list) else [],
        permissions=payload.get("permissions", []) if isinstance(payload.get("permissions", []), list) else [],
        auth_method="JWT",
        status=authority.status,
        session_reference=_claim(payload, "session_reference"),
    )
    log_auth_event("JWT_AUTH", authority.principal_id, True, {"tenant": tenant_id})
    return identity

__all__ = ["get_current_identity", "get_principal_authority_repository", "security_scheme", "api_key_header"]

# ARTIFACT: authentication.py
# VERSION: v1.2.0-R10C2F9-ACCESS-PURPOSE-DURABLE-REVISION-ENFORCEMENT
# AUTHORITY BOUNDARY: credential verification plus durable ACTIVE principal gate
# TENANT POSTURE: tenant claim is context only; membership authority is separate
# FAIL-CLOSED POSTURE: missing, invalid, absent, unavailable, suspended, and revoked authority denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
