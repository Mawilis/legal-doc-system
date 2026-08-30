# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
TENANT ROUTER — CONTROLLED GET + ARCHIVE AUTHORITY WIRING
===============================================================================

TITLE:
    WILSY OS Tenant Router

FILE:
    tools/eos/api/tenant_router.py

VERSION:
    v1.1.0-TENANT-GET-ARCHIVE-AUTHORITY-WIRING

AUTHORITY:
    Wilsy OS Core Governance.
    Canonical FastAPI tenant HTTP surface for bounded tenant registry operations.

EPITOME:
    Activates only own-tenant profile GET and lifecycle archive through the
    frozen durable tenant authorization dependency. Collection listing, tenant
    creation, and profile mutation remain fail-closed and cannot reach registry
    persistence. X-Tenant-ID is requested scope only and must exactly match the
    detail-route tenant path before persistence is accessed.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/tenant_router.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.1.0-TENANT-GET-ARCHIVE-AUTHORITY-WIRING
        - Activates GET /api/tenants/{tenant_id} with canonical
          tenant:profile:read + profile_read authorization.
        - Activates DELETE /api/tenants/{tenant_id} as archive-only with canonical
          tenant:lifecycle:archive + lifecycle_archive authorization.
        - Requires exact authorized X-Tenant-ID scope to equal the tenant path
          before either activated route accesses TenantRegistry.
        - Adds a route-safe RequireTenantAuthorization adapter that preserves
          X-Tenant-ID semantics while avoiding FastAPI path/header name
          collision on canonical {tenant_id} detail routes.
        - Maps genuine GET absence to HTTP 404.
        - Maps persisted GET corruption and registry infrastructure failures to
          deterministic HTTP 503 responses.
        - Preserves archive no-modification semantics as the historical
          "not found or already archived" HTTP 404 result.
        - Keeps collection GET, POST create, and PUT mutation contained at
          TENANT_AUTHORITY_UNAVAILABLE before registry access.

    v1.0.4-TENANT-AUTHORITY-CONTAINMENT
        - Contained all five tenant routes until governed authority composition
          and persistence failure semantics were available.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Durable principal, membership, tenant-business-role, permission, and role
    assignment truth are composed by RequireTenantAuthorization. Request
    headers, JWT role projections, request.state values, and Node-side role
    labels never become business authority. Registry failures fail closed.

TENANT BOUNDARY:
    X-Tenant-ID is explicit requested scope and never membership evidence.
    Activated detail routes require authorized X-Tenant-ID scope to exactly
    equal the path tenant_id before persistence access. Cross-tenant mismatch
    returns HTTP 403. Global tenant listing remains unavailable.

AUTHORITY BOUNDARY:
    This artifact owns HTTP route composition and persistence invocation only.
    It does not authenticate callers, establish principal truth, establish
    membership, resolve business roles, assign permissions, or grant authority.
    Those decisions remain owned by the frozen authorization stack.

FINANCIAL AUTHORITY BOUNDARY:
    No financial execution authority exists in this artifact.
    Tenant profile read and lifecycle archive are non-financial operations.
    Kennel EOS remains the exclusive financial execution authority.

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    Full-file sovereign artifact.
    Fail-closed.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, NoReturn

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field

import tools.eos.api.tenant_authorization_http as tenant_authorization_http
from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.saas.domain.tenant import TenantEntity
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
    TenantRegistryError,
)


# =============================================================================
# SOVEREIGN VERSION
# =============================================================================

VERSION = "v1.1.0-TENANT-GET-ARCHIVE-AUTHORITY-WIRING"


# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger("WilsyOS.API.TenantRouter")


# =============================================================================
# CANONICAL AUTHORIZATION BINDINGS
# =============================================================================


class _RouteTenantAuthorization(RequireTenantAuthorization):
    """Expose the frozen tenant authorization dependency safely on detail routes.

    FastAPI resolves dependency parameter names against path parameters before
    applying field annotations. The frozen reusable dependency intentionally
    names its X-Tenant-ID Header parameter ``tenant_id``. Detail routes also own
    the canonical path parameter ``{tenant_id}``, so using the frozen callable
    directly would cause FastAPI to reject Header metadata for a path parameter.

    This bounded adapter changes only the FastAPI-visible Python parameter name
    to ``tenant_scope`` while preserving the public Header alias ``X-Tenant-ID``.
    It delegates all authorization semantics to the frozen
    RequireTenantAuthorization implementation and therefore does not duplicate
    or reinterpret principal, membership, role, permission, or decision truth.
    """

    async def __call__(
        self,
        identity: SovereignIdentity = Depends(
            tenant_authorization_http.get_current_identity
        ),
        tenant_scope: str | None = Header(
            default=None,
            alias="X-Tenant-ID",
        ),
        principal_repository: Any = Depends(
            tenant_authorization_http.get_principal_authority_repository
        ),
        membership_repository: Any = Depends(
            tenant_authorization_http.get_tenant_membership_repository
        ),
        role_assignment_repository: Any = Depends(
            tenant_authorization_http.get_role_assignment_repository
        ),
    ) -> TenantAuthorizationContext:
        """Delegate exact current-truth authorization with route-safe scope naming."""
        return await super().__call__(
            identity=identity,
            tenant_id=tenant_scope,
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            role_assignment_repository=role_assignment_repository,
        )


_PROFILE_READ_AUTHORIZATION = _RouteTenantAuthorization(
    "tenant:profile:read",
    "profile_read",
)

_LIFECYCLE_ARCHIVE_AUTHORIZATION = _RouteTenantAuthorization(
    "tenant:lifecycle:archive",
    "lifecycle_archive",
)

_KNOWN_REGISTRY_UNAVAILABLE_REASONS = frozenset(
    {
        "TENANT_REGISTRY_GET_UNAVAILABLE",
        "TENANT_REGISTRY_GET_INVALID_DOCUMENT",
        "TENANT_REGISTRY_ARCHIVE_UNAVAILABLE",
    }
)


# =============================================================================
# PUBLIC REQUEST / RESPONSE CONTRACTS
# =============================================================================


class TenantCreateRequest(BaseModel):
    """Represent the contained tenant-creation request contract.

    Authority:
        Schema validation only. Constructing this model does not authorize
        lifecycle creation.

    Tenant scope:
        tenant_id is request data only and never authority.

    Mutation semantics:
        The POST route remains contained and does not persist this model.

    Financial boundary:
        No financial execution authority.
    """

    name: str = Field(..., description="Organization name")
    tenant_id: str | None = Field(
        default=None,
        description="Optional custom tenant ID; auto-generated if omitted",
    )
    alias: str | None = Field(
        default=None,
        description="Human-readable alias",
    )
    industry: str | None = None
    region: str | None = None
    sector: str | None = None
    legal_name: str | None = None
    tax_id: str | None = None
    contact_email: str | None = None
    plan: str | None = "ENTERPRISE"
    status: str | None = "ACTIVE"
    compliance_flags: dict[str, Any] | None = None
    checksum: str | None = None
    verified: bool | None = None


class TenantUpdateRequest(BaseModel):
    """Represent the contained tenant-profile mutation request contract.

    Authority:
        Schema validation only. Constructing this model does not authorize
        profile mutation.

    Tenant scope:
        The path tenant remains outside this model.

    Mutation semantics:
        The PUT route remains contained until profile storage and policy fields
        are aligned in the subsequent migration phase.

    Financial boundary:
        No financial execution authority.
    """

    name: str | None = None
    alias: str | None = None
    industry: str | None = None
    region: str | None = None
    sector: str | None = None
    legal_name: str | None = None
    tax_id: str | None = None
    contact_email: str | None = None
    plan: str | None = None
    status: str | None = None
    checksum: str | None = None
    verified: bool | None = None


class TenantResponse(BaseModel):
    """Represent the bounded tenant profile returned by an activated GET."""

    tenant_id: str
    alias: str | None
    name: str
    legal_name: str | None
    tax_id: str | None
    contact_email: str | None
    industry: str | None
    region: str | None
    sector: str | None
    status: str
    subscription_tier: str | None
    compliance_flags: dict[str, Any] | None
    created_at: str | None
    updated_at: str | None
    proof_hash: str | None
    verified: bool | None


class TenantListResponse(BaseModel):
    """Represent the legacy tenant-list response shape while listing is contained."""

    tenants: list[TenantResponse]
    total: int


# =============================================================================
# RESPONSE / FAILURE HELPERS
# =============================================================================


def _entity_to_response(entity: TenantEntity) -> TenantResponse:
    """Convert one TenantEntity to the bounded HTTP response model.

    Authority:
        Serialization only. This helper never authorizes access.

    Tenant scope:
        The entity must already have been resolved after exact route authorization.

    Mutation semantics:
        Read-only.

    Failure semantics:
        A missing object is rejected rather than converted into a fabricated
        response.

    Financial boundary:
        No financial execution authority.
    """
    if entity is None:
        raise ValueError("Tenant entity is None")

    organization = entity.organization
    return TenantResponse(
        tenant_id=entity.tenant_id,
        alias=getattr(entity, "alias", None),
        name=organization.organization_name,
        legal_name=organization.legal_name,
        tax_id=organization.tax_id,
        contact_email=organization.contact_email,
        industry=organization.industry,
        region=getattr(entity, "region", None),
        sector=None,
        status=entity.status,
        subscription_tier=getattr(entity, "subscription_tier", None),
        compliance_flags=getattr(entity, "compliance_flags", None),
        created_at=entity.created_at,
        updated_at=None,
        proof_hash=getattr(entity, "proof_hash", None),
        verified=getattr(entity, "verified", False),
    )


def _require_tenant_authority_available() -> NoReturn:
    """Keep non-migrated tenant routes deterministically unavailable.

    Authority:
        This helper grants nothing.

    Tenant scope:
        No tenant scope is resolved.

    Persistence semantics:
        Raises before any TenantRegistry access.

    Financial boundary:
        No financial execution authority.
    """
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="TENANT_AUTHORITY_UNAVAILABLE",
    )


def _require_exact_path_scope(
    tenant_id: str,
    authorization: TenantAuthorizationContext,
) -> None:
    """Require authorized request scope to exactly equal the detail-route path.

    The frozen authorization dependency proves authority for X-Tenant-ID.
    This route-level check binds that proven scope to the concrete path target
    before persistence is accessed.
    """
    if authorization.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TENANT_SCOPE_PATH_MISMATCH",
        )


def _raise_registry_service_unavailable(error: TenantRegistryError) -> NoReturn:
    """Translate bounded registry failures into deterministic HTTP 503.

    Known registry reasons are preserved verbatim for operational distinction.
    Unknown future registry errors remain fail-closed under a generic bounded
    service-unavailable token rather than escaping as HTTP 500.
    """
    reason = str(error).strip()
    detail = (
        reason
        if reason in _KNOWN_REGISTRY_UNAVAILABLE_REASONS
        else "TENANT_REGISTRY_UNAVAILABLE"
    )
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=detail,
    ) from error


# =============================================================================
# CANONICAL TENANT ROUTER
# =============================================================================

tenant_router = APIRouter(
    prefix="/api/tenants",
    tags=["tenants"],
)


@tenant_router.get("", response_model=TenantListResponse)
async def list_tenants(
    request: Request,
    search: str | None = Query(
        default=None,
        description="Search by name or alias (case-insensitive)",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Pagination offset",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Items per page",
    ),
) -> TenantListResponse:
    """Keep global tenant listing unavailable before any persistence access.

    Global listing is not an own-tenant operation and is outside B2B authority.
    """
    del request, search, skip, limit
    _require_tenant_authority_available()


@tenant_router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    request: Request,
    authorization: TenantAuthorizationContext = Depends(
        _PROFILE_READ_AUTHORIZATION
    ),
) -> TenantResponse:
    """Read one authorized own-tenant profile.

    Authority:
        Requires canonical tenant:profile:read bound to profile_read through
        RequireTenantAuthorization. No caller/header/JWT role is interpreted here.

    Tenant scope:
        The authorized X-Tenant-ID must exactly equal tenant_id before registry
        access.

    Return semantics:
        Healthy persisted truth returns TenantResponse.
        Genuine absence returns HTTP 404.

    Fail-closed semantics:
        Invalid persisted truth and MongoDB GET outage return HTTP 503 with the
        bounded registry reason.

    Mutation semantics:
        Read-only.

    Financial boundary:
        No financial execution authority.
    """
    del request
    _require_exact_path_scope(tenant_id, authorization)

    try:
        entity = TenantRegistry.get(tenant_id)
    except TenantRegistryError as error:
        logger.error("Authorized tenant GET registry failure: %s", error)
        _raise_registry_service_unavailable(error)

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        )

    return _entity_to_response(entity)


@tenant_router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tenant(
    payload: TenantCreateRequest,
    request: Request,
) -> TenantResponse:
    """Keep tenant lifecycle creation unavailable before persistence access.

    Lifecycle creation requires system authority and is outside B2B.
    """
    del payload, request
    _require_tenant_authority_available()


@tenant_router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    payload: TenantUpdateRequest,
    request: Request,
) -> TenantResponse:
    """Keep tenant profile mutation unavailable before persistence access.

    Profile mutation remains blocked until mutable-field policy and storage
    semantics are aligned in the subsequent migration phase.
    """
    del tenant_id, payload, request
    _require_tenant_authority_available()


@tenant_router.delete(
    "/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def archive_tenant(
    tenant_id: str,
    request: Request,
    authorization: TenantAuthorizationContext = Depends(
        _LIFECYCLE_ARCHIVE_AUTHORIZATION
    ),
) -> Response:
    """Archive one authorized own tenant without hard deletion.

    Authority:
        Requires canonical tenant:lifecycle:archive bound to lifecycle_archive
        through RequireTenantAuthorization.

    Tenant scope:
        The authorized X-Tenant-ID must exactly equal tenant_id before registry
        access.

    Mutation semantics:
        Calls TenantRegistry.archive only. The registry performs a soft
        ``status = ARCHIVED`` update and never hard deletion.

    Return semantics:
        A modified tenant returns HTTP 204.
        A no-modification result preserves historical ambiguity as HTTP 404
        "Tenant not found or already archived."

    Fail-closed semantics:
        MongoDB archive outage returns HTTP 503 with the bounded registry reason.

    Financial boundary:
        No financial execution authority.
    """
    del request
    _require_exact_path_scope(tenant_id, authorization)

    try:
        archived = TenantRegistry.archive(tenant_id)
    except TenantRegistryError as error:
        logger.error("Authorized tenant archive registry failure: %s", error)
        _raise_registry_service_unavailable(error)

    if archived is not True:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or already archived.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =============================================================================
# EXPLICIT PUBLIC EXPORT SURFACE
# =============================================================================

__all__ = [
    "VERSION",
    "TenantCreateRequest",
    "TenantUpdateRequest",
    "TenantResponse",
    "TenantListResponse",
    "tenant_router",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: tenant_router.py
# VERSION: v1.1.0-TENANT-GET-ARCHIVE-AUTHORITY-WIRING
# AUTHORITY BOUNDARY: tenant HTTP composition and bounded registry invocation only; durable authentication, membership, role, permission, and authorization truth remain external authorities
# TENANT POSTURE: authorized X-Tenant-ID must exactly equal the detail path tenant before GET/archive persistence; global list, create, and PUT remain contained
# FAIL-CLOSED POSTURE: only canonical profile_read and lifecycle_archive dependencies can reach registry; scope mismatch denies 403; absence is 404; registry corruption/outage is 503
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
