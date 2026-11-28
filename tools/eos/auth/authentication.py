"""
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering; adjacent authorities remain independent.
Wilsy OS authentication projection guarded by durable principal authority.

TITLE: WILSY OS Authentication Projection
VERSION: v1.5.0-NONBLOCKING-DURABLE-IDENTITY-RESOLUTION
AUTHORITY: Cryptographic credential verification and current PrincipalAuthority gating.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authentication.py
CERTIFICATION / UPDATE DATE: 2026-11-24
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
CHANGELOG:
    2026-11-24 v1.5.0-NONBLOCKING-DURABLE-IDENTITY-RESOLUTION keeps the
    canonical async FastAPI dependency but offloads its existing complete
    synchronous authentication/currentness and caller-owned SYSTEM transaction
    to one worker thread. An opaque trace is established before dispatch and
    propagated by AnyIO contextvars. No token, IAM, collision, session,
    transaction, tenant or error semantics change; a slow MongoDB command
    cannot monopolize the asyncio event loop.
    2026-11-15 v1.4.0-CREDENTIAL-CURRENTNESS-SUBSTAGES emits an overall
    credential-currentness observation for both success and failure outcomes;
    AuthRegistry emits bounded read-stage timing under the same safe trace.
    Telemetry adds no authority, persistence, caching, or bypass behavior.
    2026-11-15 v1.3.0-SCOPED-REQUEST-TIMING adds opt-in, trace-correlated,
    privacy-safe timing for ACCESS-token verification, durable principal
    currentness, and GLOBAL session currentness. The observation has no
    authentication, authorization, persistence, output, or caching authority.
    v1.2.0-R10C2F9-ACCESS-PURPOSE-DURABLE-REVISION-ENFORCEMENT requires
    ACCESS purpose and a fresh exact durable credential revision before any
    protected identity projection; PRE_AUTH and legacy-purpose tokens fail
    closed without changing router, provider, or AuthRegistry authority.
    v1.1.0 removes synthetic identity/API-key authority and requires durable ACTIVE status.
SECURITY / PRIVACY POSTURE: Missing or malformed credentials fail closed; secrets are never logged.
TENANT BOUNDARY: Tenant claims remain non-authoritative request context; membership is a later contract.
AUTHORITY BOUNDARY: SovereignIdentity is a projection, not lifecycle, credential, tenant, role, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS exclusively owns financial execution.

EPITOME:
    Authentication verifies a credential, resolves the exact durable principal,
    and only then returns a projection for downstream authorization.

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

COLLABORATION / OWNERSHIP:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/authentication.py
"""
from __future__ import annotations

import logging
import os
import re
import time
import uuid
from contextvars import ContextVar
from typing import Any, Final, Optional

from pymongo.errors import PyMongoError
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from starlette.concurrency import run_in_threadpool
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
VERSION: Final[str] = "v1.5.0-NONBLOCKING-DURABLE-IDENTITY-RESOLUTION"
logger = logging.getLogger("WilsyOS.Auth.Authentication")
_TIMING_ENVIRONMENT_VARIABLE: Final[str] = "WILSY_MY_WORK_TIMING"
_TRACE_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"TRC-[A-Z0-9]{8}-[A-Z0-9]{6}"
)
_TIMING_CORRELATION: ContextVar[str] = ContextVar(
    "wilsy_request_timing_correlation",
    default="TRACE_UNAVAILABLE",
)


def request_timing_enabled() -> bool:
    """Return whether the explicit My Work latency diagnostic is enabled.

    @institutional The switch observes latency only. It never changes token
    verification, currentness, authorization, response content, or caching.
    """

    return os.getenv(_TIMING_ENVIRONMENT_VARIABLE, "").strip() == "1"


def establish_request_timing_correlation(request: Request) -> str:
    """Bind one safe existing trace reference to the current request context.

    @institutional Only canonical ``TRC-`` trace identifiers are logged. Any
    absent or malformed caller value is replaced by a server-generated opaque
    reference, preventing headers, tokens, cookies, identities, and tenant
    values from entering timing telemetry.
    """

    try:
        candidate = request.headers.get("x-trace-id", "")
    except (AttributeError, KeyError):
        # Direct dependency callers and narrow test scopes may intentionally
        # omit ASGI headers. Diagnostics must remain inert in that posture.
        candidate = ""
    correlation = (
        candidate
        if isinstance(candidate, str) and _TRACE_IDENTIFIER.fullmatch(candidate)
        else f"TRC-SERVER-{uuid.uuid4().hex[:12].upper()}"
    )
    _TIMING_CORRELATION.set(correlation)
    return correlation


def current_request_timing_correlation() -> str:
    """Return the request-local opaque diagnostic correlation reference.

    @institutional This is request-context diagnostic metadata only; it is not
    authentication, tenant, session, role, or command authority.
    """

    return _TIMING_CORRELATION.get()


def emit_request_timing(
    *,
    stage: str,
    outcome: str,
    started_ns: int,
    correlation: str | None = None,
    duration_ms: float | None = None,
) -> None:
    """Emit one bounded opt-in timing event without affecting request truth.

    @institutional Callers provide closed, source-owned stage/outcome labels.
    Raw credentials, headers other than a validated trace identifier, tenant
    identifiers, principal identifiers, work records, and exception messages
    are intentionally excluded.
    """

    if not request_timing_enabled():
        return
    logger.info(
        "WILSY_REQUEST_TIMING trace_id=%s stage=%s outcome=%s duration_ms=%.3f",
        correlation or current_request_timing_correlation(),
        stage,
        outcome,
        (
            max(0.0, duration_ms)
            if isinstance(duration_ms, float)
            else max(0, time.perf_counter_ns() - started_ns) / 1_000_000
        ),
    )

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
    """Authenticate against fresh durable authority without blocking asyncio.

    FastAPI owns injection, the request trace is established in its task, and
    AnyIO copies that trace into the worker thread. Every canonical principal,
    credential-revision, GLOBAL/SYSTEM session-currentness and transaction
    check is performed by the unchanged synchronous verifier before returning
    an identity. No authority is cached, delegated or skipped.
    """
    correlation = establish_request_timing_correlation(request)
    return await run_in_threadpool(
        _get_current_identity_sync, request, credentials, api_key, repository,
        correlation,
    )


def _get_current_identity_sync(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials],
    api_key: Optional[str],
    repository: PrincipalAuthorityRepository,
    correlation: str,
) -> SovereignIdentity:
    """Run one complete exact-currentness authentication on a worker thread.

    SYSTEM Mongo ClientSession start/commit/abort/end remain in the same worker
    thread. Caller dependencies and all error classification remain unchanged.
    The trace is an opaque diagnostic only, not authentication authority.
    """
    authentication_started_ns = time.perf_counter_ns()
    if api_key:
        log_auth_event("API_KEY_AUTH", "unresolved", False, {"reason": "principal_resolution_required"})
        raise UnauthorizedAccessException("API-key principal is not mapped to durable authority.")
    if not credentials or not credentials.credentials:
        log_auth_event("MISSING_CREDENTIALS", "unresolved", False, {})
        raise UnauthorizedAccessException("Missing authentication credentials.")
    verification_started_ns = time.perf_counter_ns()
    verification_outcome = "INVALID"
    try:
        payload = verify_access_token(credentials.credentials)
        if payload:
            verification_outcome = "VERIFIED"
    finally:
        emit_request_timing(
            stage="AUTH_ACCESS_TOKEN_VERIFICATION",
            outcome=verification_outcome,
            started_ns=verification_started_ns,
            correlation=correlation,
        )
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
    authority_started_ns = time.perf_counter_ns()
    authority_outcome = "UNAVAILABLE"
    try:
        authority = _resolve_authority(repository, principal_id)
        authority_outcome = "ACTIVE" if authority.status is PrincipalStatus.ACTIVE else "NOT_ACTIVE"
    finally:
        emit_request_timing(
            stage="AUTH_PRINCIPAL_CURRENTNESS",
            outcome=authority_outcome,
            started_ns=authority_started_ns,
            correlation=correlation,
        )
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
            session_currentness_started_ns = time.perf_counter_ns()
            session_currentness_outcome = "UNAVAILABLE"
            current = GlobalPrincipalSystemSessionAuthority(
                sessions=database[SYSTEM_SESSION_COLLECTION],
                authorizer=authorizer,
            ).is_session_current(
                principal_id=authority.principal_id,
                session_reference=session_reference,
                expected_credential_revision=token_revision,
                session=session,
            )
            session_currentness_outcome = "CURRENT" if current else "NOT_CURRENT"
            emit_request_timing(
                stage="AUTH_SYSTEM_SESSION_CURRENTNESS",
                outcome=session_currentness_outcome,
                started_ns=session_currentness_started_ns,
                correlation=correlation,
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
            principal_scope="SYSTEM",
            workspace_id=workspace_id,
            membership_revision=None,
            capacity_revision=None,
        )
        log_auth_event("SYSTEM_JWT_AUTH", authority.principal_id, True, {"scope": "SYSTEM"})
        emit_request_timing(
            stage="AUTHENTICATION_TOTAL",
            outcome="AUTHORIZED",
            started_ns=authentication_started_ns,
            correlation=correlation,
        )
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
        session_currentness_started_ns = time.perf_counter_ns()
        session_currentness_outcome = "UNAVAILABLE"
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
        session_currentness_outcome = "CURRENT" if current else "NOT_CURRENT"
        emit_request_timing(
            stage="AUTH_GLOBAL_SESSION_CURRENTNESS",
            outcome=session_currentness_outcome,
            started_ns=session_currentness_started_ns,
            correlation=correlation,
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
        emit_request_timing(
            stage="AUTHENTICATION_TOTAL",
            outcome="AUTHORIZED",
            started_ns=authentication_started_ns,
            correlation=correlation,
        )
        return identity
    if principal_scope not in (None, "TENANT"):
        raise UnauthorizedAccessException("Invalid or expired sovereign JWT token.")

    credential_currentness_started_ns = time.perf_counter_ns()
    credential_currentness_outcome = "UNAVAILABLE"
    try:
        durable_revision = AuthRegistry().get_credential_revision(
            tenant_id,
            authority.principal_id,
        )
        credential_currentness_outcome = "CURRENT" if token_revision == durable_revision else "NOT_CURRENT"
    except Exception as error:
        log_auth_event(
            "JWT_AUTH",
            authority.principal_id,
            False,
            {"reason": "credential_revision_unavailable"},
        )
        raise UnauthorizedAccessException("Authentication authority is unavailable.") from error
    finally:
        emit_request_timing(
            stage="AUTH_TENANT_CREDENTIAL_CURRENTNESS",
            outcome=credential_currentness_outcome,
            started_ns=credential_currentness_started_ns,
            correlation=correlation,
        )
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
        principal_scope=principal_scope,
        workspace_id=None,
        membership_revision=None,
        capacity_revision=None,
    )
    log_auth_event("JWT_AUTH", authority.principal_id, True, {"tenant": tenant_id})
    emit_request_timing(
        stage="AUTHENTICATION_TOTAL",
        outcome="AUTHORIZED",
        started_ns=authentication_started_ns,
        correlation=correlation,
    )
    return identity

__all__ = [
    "VERSION",
    "get_current_identity",
    "get_principal_authority_repository",
    "request_timing_enabled",
    "establish_request_timing_correlation",
    "current_request_timing_correlation",
    "emit_request_timing",
    "security_scheme",
    "api_key_header",
]

# ARTIFACT: authentication.py
# VERSION: v1.5.0-NONBLOCKING-DURABLE-IDENTITY-RESOLUTION
# AUTHORITY BOUNDARY: credential verification plus durable ACTIVE principal gate
# TENANT POSTURE: tenant claim is context only; membership authority is separate
# FAIL-CLOSED POSTURE: missing, invalid, absent, unavailable, suspended, and revoked authority denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
