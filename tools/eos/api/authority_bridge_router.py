"""WILSY OS Python Authority Bridge Router
TITLE: WILSY OS Python Authority Bridge Router
VERSION: v1.0.0-WILSY-PYTHON-AUTHORITY-BRIDGE
AUTHORITY: HTTP composition of existing Python service-trust, identity, tenant, and authorization authorities.
EPITOME: Verifies a Node service assertion without allowing service metadata to become user or tenant authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/authority_bridge_router.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering; Python owns authority decisions.
CERTIFICATION/UPDATE DATE: 2026-08-30
CHANGELOG: v1.0.0-WILSY-PYTHON-AUTHORITY-BRIDGE — raw HTTP trust, durable replay, and delegated Python authorization composition.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Fail closed; bounded responses; secrets, credentials, claims, and repository details are never returned.
TENANT BOUNDARY: X-Tenant-ID is untrusted context and is admitted only by current Python membership authority.
AUTHORITY BOUNDARY: Owns HTTP composition only; it does not own identity, lifecycle, membership, role, or permission truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import os
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Protocol

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, ConfigDict

from tools.eos.api.exceptions import ForbiddenOperationException, UnauthorizedAccessException, WilsyAPIException
from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.authorization import RequirePermission, get_role_assignment_repository
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.internal_service_replay_registry import InternalServiceReplayRegistry
from tools.eos.auth.internal_service_trust import (
    InternalServiceTrustAuthenticationError,
    InternalServiceTrustConfigurationError,
    InternalServiceTrustError,
    InternalServiceTrustFreshnessError,
    InternalServiceTrustMalformedRequestError,
    InternalServiceTrustReplayError,
    TrustResult,
    verify_internal_service_request,
)
from tools.eos.auth.tenant_access import get_current_tenant_identity

VERSION = "v1.0.0-WILSY-PYTHON-AUTHORITY-BRIDGE"
ROUTE_PATH = "/internal/authority/authorize"
SERVICE_HEADERS = (
    "X-Wilsy-Auth-Version", "X-Wilsy-Service-ID", "X-Wilsy-Audience", "X-Wilsy-Key-ID",
    "X-Wilsy-Timestamp", "X-Wilsy-Nonce", "X-Wilsy-Body-SHA3-512", "X-Wilsy-Correlation-ID",
    "X-Wilsy-Signature",
)


class ReplayProvider(Protocol):
    def consume_once(self, *, service_id: str, key_id: str, nonce: str, expires_at: int) -> bool: ...


class BridgeRequest(BaseModel):
    """Only a server-controlled policy identifier may cross this boundary."""
    model_config = ConfigDict(extra="forbid")
    policy_id: str


def _service_config(env: Mapping[str, str] | None = None) -> tuple[dict[str, tuple[str, str]], str, str]:
    values = env or os.environ
    names = ("WILSY_INTERNAL_AUTH_SERVICE_ID", "WILSY_INTERNAL_AUTH_AUDIENCE", "WILSY_INTERNAL_AUTH_KEY_ID", "WILSY_INTERNAL_AUTH_SECRET")
    resolved = {name: values.get(name) for name in names}
    if any(not isinstance(value, str) or not value.strip() for value in resolved.values()):
        raise WilsyAPIException("Service trust is unavailable.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    service_id = resolved[names[0]].strip()  # type: ignore[union-attr]
    audience = resolved[names[1]].strip()  # type: ignore[union-attr]
    key_id = resolved[names[2]].strip()  # type: ignore[union-attr]
    secret = resolved[names[3]]
    assert isinstance(secret, str)
    return {key_id: (service_id, secret)}, service_id, audience


def _origin_form(request: Request) -> str:
    raw_path = request.scope.get("raw_path")
    query = request.scope.get("query_string", b"")
    if not isinstance(raw_path, bytes) or not isinstance(query, bytes):
        raise WilsyAPIException("Service trust is unavailable.", status_code=503)
    try:
        return (raw_path + (b"?" + query if query else b"")).decode("ascii")
    except UnicodeDecodeError as error:
        raise WilsyAPIException("Service trust denied.", status_code=401) from error


def _trust_headers(request: Request) -> dict[str, str]:
    mapping = {
        "version": "X-Wilsy-Auth-Version", "service_id": "X-Wilsy-Service-ID",
        "audience": "X-Wilsy-Audience", "key_id": "X-Wilsy-Key-ID",
        "timestamp": "X-Wilsy-Timestamp", "nonce": "X-Wilsy-Nonce",
        "body_sha3_512": "X-Wilsy-Body-SHA3-512", "correlation_id": "X-Wilsy-Correlation-ID",
        "signature": "X-Wilsy-Signature",
    }
    headers = {field: request.headers.get(header, "") for field, header in mapping.items()}
    headers.update({"method": request.method, "path": _origin_form(request)})
    return headers


def _trust_failure(error: Exception) -> WilsyAPIException:
    if isinstance(error, InternalServiceTrustConfigurationError) and str(error) == "unknown trust key":
        return WilsyAPIException("Service trust denied.", status_code=401)
    if isinstance(error, InternalServiceTrustReplayError):
        return WilsyAPIException("Service trust denied.", status_code=401)
    if isinstance(error, InternalServiceTrustConfigurationError):
        return WilsyAPIException("Service trust is unavailable.", status_code=503)
    if isinstance(error, (InternalServiceTrustError, InternalServiceTrustAuthenticationError, InternalServiceTrustFreshnessError, InternalServiceTrustMalformedRequestError)):
        return WilsyAPIException("Service trust denied.", status_code=401)
    return WilsyAPIException("Service trust is unavailable.", status_code=503)


async def authorize_request(
    request: Request,
    payload: BridgeRequest,
    *,
    identity_provider: Callable[[], Awaitable[SovereignIdentity]] | None = None,
    tenant_provider: Callable[[SovereignIdentity], Awaitable[SovereignIdentity]] | None = None,
    authorization_provider: Callable[[SovereignIdentity, str], Awaitable[SovereignIdentity]] | None = None,
    replay_store: ReplayProvider | None = None,
    config: Mapping[str, str] | None = None,
    trust_verifier: Callable[..., TrustResult] = verify_internal_service_request,
) -> dict[str, Any]:
    """Execute the fixed fail-closed authority sequence with narrow test seams."""
    body = await request.body()
    try:
        keys, service_id, audience = _service_config(config)
        selected_replay = replay_store or InternalServiceReplayRegistry()
        if replay_store is None:
            InternalServiceReplayRegistry.ensure_indexes()
        trust = trust_verifier(request=_trust_headers(request), body=body, keys=keys, replay_store=selected_replay)
    except Exception as error:
        if isinstance(error, WilsyAPIException):
            raise
        raise _trust_failure(error) from error
    try:
        identity = await (identity_provider or (lambda: get_current_identity()))()  # type: ignore[call-arg]
        tenant_identity = await (tenant_provider or (lambda value: get_current_tenant_identity(tenant_id=request.headers.get("X-Tenant-ID"), identity=value))) (identity)  # type: ignore[call-arg]
        authorized = await (authorization_provider or _authorize_policy)(tenant_identity, payload.policy_id)
    except (UnauthorizedAccessException, ForbiddenOperationException):
        raise
    except Exception as error:
        raise WilsyAPIException("Authorization authority is unavailable.", status_code=503) from error
    return {"allowed": True, "identity_id": authorized.identity_id, "tenant_id": authorized.tenant_id, "correlation_id": trust.correlation_id}


async def _authorize_policy(identity: SovereignIdentity, policy_id: str) -> SovereignIdentity:
    policies = {"audit:read": RequirePermission("audit:read")}
    policy = policies.get(policy_id)
    if policy is None:
        raise ForbiddenOperationException("Requested authorization policy is not available.")
    return await policy(identity=identity, repository=get_role_assignment_repository())


router = APIRouter(tags=["Internal Python Authority"])


@router.post(ROUTE_PATH)
async def authorize(request: Request, payload: BridgeRequest, identity: SovereignIdentity = Depends(get_current_identity), tenant_identity: SovereignIdentity = Depends(get_current_tenant_identity)) -> dict[str, Any]:
    """Authorize one server-controlled policy after service, user, tenant, and role gates."""
    async def current_identity() -> SovereignIdentity:
        return identity
    async def current_tenant(_: SovereignIdentity) -> SovereignIdentity:
        return tenant_identity
    return await authorize_request(request, payload, identity_provider=current_identity, tenant_provider=current_tenant)


__all__ = ["BridgeRequest", "ROUTE_PATH", "authorize", "authorize_request", "router"]

# ARTIFACT: authority_bridge_router.py
# VERSION: v1.0.0-WILSY-PYTHON-AUTHORITY-BRIDGE
# AUTHORITY BOUNDARY: HTTP composition only; Python identity, membership, and authorization remain authoritative.
# TENANT POSTURE: Explicit X-Tenant-ID requires current ACTIVE membership; service metadata never substitutes for tenant authority.
# FAIL-CLOSED POSTURE: Trust, replay, authentication, membership, or authorization failures deny or return bounded 503.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
