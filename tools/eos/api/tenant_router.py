# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
TENANT ROUTER — CONTROLLED PROFILE UPDATE AUTHORITY WIRING
===============================================================================

TITLE:
    WILSY OS Tenant Router

FILE:
    tools/eos/api/tenant_router.py

VERSION:
    v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-WIRING

AUTHORITY:
    Wilsy OS Core Governance.
    Canonical FastAPI tenant HTTP surface for bounded tenant registry operations.

EPITOME:
    Activates own-tenant profile GET, strict six-field profile PUT, and lifecycle
    archive through the frozen durable tenant authorization dependency. Global
    tenant listing and tenant creation remain fail-closed before persistence.
    X-Tenant-ID is requested scope only and must exactly match the detail-route
    tenant path before any activated detail operation reaches TenantRegistry.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/tenant_router.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-31

CHANGELOG:
    v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-WIRING
        - Activates PUT /api/tenants/{tenant_id} with canonical
          tenant:profile:write + profile_update authorization.
        - Narrows TenantUpdateRequest to the frozen six-field profile mutation
          canon and rejects extra request fields.
        - Requires exact authorized X-Tenant-ID scope to equal the path tenant
          before strict profile persistence.
        - Routes PUT exclusively through TenantRegistry.update_profile; the broad
          legacy TenantRegistry.update compatibility API is never invoked.
        - Maps genuine profile-update absence to HTTP 404.
        - Maps strict profile-input registry failures to bounded HTTP 422.
        - Maps invalid persisted truth, post-write inconsistency, infrastructure
          outage, and unknown registry failures to bounded HTTP 503.
        - Aligns TenantResponse sector with durable top-level TenantEntity.sector.
        - Preserves GET detail and DELETE/archive B2B semantics exactly.
        - Keeps collection GET and POST create contained before persistence.
        - Uses Starlette's canonical HTTP_422_UNPROCESSABLE_CONTENT symbol for
          strict profile-input failure translation without changing HTTP status.

    v1.1.0-TENANT-GET-ARCHIVE-AUTHORITY-WIRING
        - Activated GET /api/tenants/{tenant_id} and DELETE/archive through the
          frozen durable tenant authorization dependency.
        - Kept collection GET, POST create, and PUT mutation contained.

    v1.0.4-TENANT-AUTHORITY-CONTAINMENT
        - Contained all five tenant routes before governed authority composition.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Durable principal, membership, tenant-business-role, permission, and role
    assignment truth are composed only by RequireTenantAuthorization. Request
    headers, JWT role projections, request.state values, Node-side role labels,
    and caller-supplied profile fields never become business authority. PUT input
    is schema-bounded and strict persistence independently enforces the same
    six-field canon. Registry failures fail closed.

TENANT BOUNDARY:
    X-Tenant-ID is explicit requested scope and never membership evidence.
    Every activated detail route requires authorized X-Tenant-ID scope to exactly
    equal path tenant_id before persistence access. Cross-tenant mismatch returns
    HTTP 403 without registry access. Global tenant listing remains unavailable.

AUTHORITY BOUNDARY:
    This artifact owns HTTP route composition, request-shape validation, exact
    path/scope binding, bounded registry invocation, and HTTP failure translation.
    It does not authenticate callers, establish principal or membership truth,
    resolve business roles, assign permissions, or independently authorize.
    Those decisions remain owned by the frozen authorization stack.

FINANCIAL AUTHORITY BOUNDARY:
    No financial execution authority exists in this artifact.
    Profile mutation cannot change plan or financial metadata through the strict
    six-field persistence boundary. Kennel EOS remains exclusive.

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    Full-file sovereign artifact.
    Fail-closed.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, NoReturn

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from pydantic import BaseModel, ConfigDict, Field

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

VERSION = "v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-WIRING"


# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger("WilsyOS.API.TenantRouter")


# =============================================================================
# CANONICAL AUTHORIZATION BINDINGS
# =============================================================================


class _RouteTenantAuthorization(RequireTenantAuthorization):
    """Expose the frozen tenant authorization dependency safely on detail routes.

    Authority:
        Delegation only. This adapter does not duplicate or reinterpret durable
        authorization logic.

    Tenant scope:
        The public header remains X-Tenant-ID. ``tenant_scope`` exists only to
        avoid FastAPI's path/header Python-parameter collision on {tenant_id}.

    Mutation semantics:
        None.

    Financial boundary:
        No financial execution authority.
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
        """Delegate current-truth authorization with route-safe scope naming."""
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

_PROFILE_UPDATE_AUTHORIZATION = _RouteTenantAuthorization(
    "tenant:profile:write",
    "profile_update",
)

_LIFECYCLE_ARCHIVE_AUTHORIZATION = _RouteTenantAuthorization(
    "tenant:lifecycle:archive",
    "lifecycle_archive",
)

_PROFILE_UPDATE_CLIENT_ERROR_REASONS = frozenset(
    {
        "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_TENANT_ID",
        "TENANT_REGISTRY_PROFILE_UPDATE_EMPTY",
        "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_FIELDS",
        "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_VALUES",
    }
)

_KNOWN_REGISTRY_UNAVAILABLE_REASONS = frozenset(
    {
        "TENANT_REGISTRY_GET_UNAVAILABLE",
        "TENANT_REGISTRY_GET_INVALID_DOCUMENT",
        "TENANT_REGISTRY_ARCHIVE_UNAVAILABLE",
        "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT",
        "TENANT_REGISTRY_PROFILE_UPDATE_INCONSISTENT_STATE",
        "TENANT_REGISTRY_PROFILE_UPDATE_UNAVAILABLE",
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
        POST remains contained and does not persist this model.

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
    """Represent the exact C2 tenant-profile mutation request contract.

    Authority:
        Schema validation only. Construction never authorizes profile mutation.

    Tenant scope:
        The path tenant remains outside this model and is independently bound to
        authorized X-Tenant-ID before persistence.

    Mutation semantics:
        Exposes exactly the frozen PROFILE_MUTABLE_FIELDS_V1 surface:
        name, alias, industry, region, sector, legal_name. Extra fields are
        rejected by Pydantic before the route can invoke registry persistence.
        Omitted fields remain untouched; explicit null remains meaningful for the
        optional alias/region/sector/legal_name fields and is passed through using
        model_dump(exclude_unset=True).

    Financial boundary:
        Plan and financial metadata are absent. No financial execution authority.
    """

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    alias: str | None = None
    industry: str | None = None
    region: str | None = None
    sector: str | None = None
    legal_name: str | None = None


class TenantResponse(BaseModel):
    """Represent the bounded tenant profile returned by activated detail routes.

    Authority:
        Response schema only.

    Tenant scope:
        The entity must already be resolved after governed authorization.

    Mutation semantics:
        None; this is serialization only.

    Financial boundary:
        Subscription metadata is descriptive only and grants no execution.
    """

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
    """Represent the legacy tenant-list response while collection GET is contained."""

    tenants: list[TenantResponse]
    total: int


# =============================================================================
# RESPONSE / FAILURE HELPERS
# =============================================================================


def _entity_to_response(entity: TenantEntity) -> TenantResponse:
    """Convert one resolved TenantEntity to the bounded HTTP response.

    Authority:
        Serialization only.

    Tenant scope:
        Caller must already have completed authorization and scope/path binding.

    Mutation semantics:
        Read-only.

    Failure semantics:
        Missing entities are rejected rather than fabricated.

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
        sector=getattr(entity, "sector", None),
        status=entity.status,
        subscription_tier=getattr(entity, "subscription_tier", None),
        compliance_flags=getattr(entity, "compliance_flags", None),
        created_at=entity.created_at,
        updated_at=None,
        proof_hash=getattr(entity, "proof_hash", None),
        verified=getattr(entity, "verified", False),
    )


def _require_tenant_authority_available() -> NoReturn:
    """Keep non-migrated collection/lifecycle routes unavailable before persistence.

    Authority:
        Grants nothing.

    Tenant scope:
        Resolves no tenant.

    Persistence semantics:
        Raises before TenantRegistry access.

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
    """Require authorized X-Tenant-ID scope to exactly equal the detail path.

    Authority:
        Consumes already-proven authorization context; does not authorize.

    Tenant scope:
        Prevents an authorization decision for one tenant from being applied to
        another path target.

    Mutation semantics:
        Must complete before registry access.

    Financial boundary:
        No financial execution authority.
    """
    if authorization.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TENANT_SCOPE_PATH_MISMATCH",
        )


def _raise_registry_service_unavailable(error: TenantRegistryError) -> NoReturn:
    """Translate bounded registry service/integrity failures to HTTP 503."""
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


def _raise_profile_update_registry_failure(
    error: TenantRegistryError,
) -> NoReturn:
    """Translate strict profile persistence errors without leaking internals.

    Client-shape/value failures are bounded HTTP 422. Persisted-truth,
    consistency, infrastructure, and unknown failures are fail-closed HTTP 503.
    """
    reason = str(error).strip()
    if reason in _PROFILE_UPDATE_CLIENT_ERROR_REASONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=reason,
        ) from error
    _raise_registry_service_unavailable(error)


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

    Global listing is not an own-tenant operation and remains outside C2.
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
        Requires tenant:profile:read / profile_read through the frozen
        RequireTenantAuthorization composition.

    Tenant scope:
        Authorized X-Tenant-ID must exactly equal tenant_id before registry access.

    Return semantics:
        Healthy persisted truth -> HTTP 200.
        Genuine absence -> HTTP 404.

    Fail-closed semantics:
        Invalid persisted truth or GET outage -> bounded HTTP 503.

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

    Lifecycle creation requires separately governed system authority and remains
    outside C2.
    """
    del payload, request
    _require_tenant_authority_available()


@tenant_router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    payload: TenantUpdateRequest,
    request: Request,
    authorization: TenantAuthorizationContext = Depends(
        _PROFILE_UPDATE_AUTHORIZATION
    ),
) -> TenantResponse:
    """Mutate exactly the authorized own-tenant six-field profile.

    Authority:
        Requires canonical tenant:profile:write bound to profile_update through
        frozen RequireTenantAuthorization. Transport/JWT/header role projections
        are never interpreted as business authority here.

    Tenant scope:
        Authorized X-Tenant-ID must exactly equal tenant_id before persistence.
        A mismatch returns HTTP 403 and performs no registry call.

    Mutation semantics:
        Only name, alias, industry, region, sector, and legal_name are representable
        by TenantUpdateRequest. The resulting exclude-unset payload is sent only to
        TenantRegistry.update_profile. Legacy TenantRegistry.update is not used.

    Return semantics:
        Healthy mutation, including same-value idempotent mutation -> HTTP 200.
        Genuine target absence -> HTTP 404.

    Fail-closed semantics:
        Strict profile input/value errors -> bounded HTTP 422.
        Invalid persisted truth, post-write inconsistency, Mongo outage, and
        unknown registry failures -> bounded HTTP 503.

    Financial boundary:
        Plan is not requestable or persistable through this route.
        No financial execution authority.
    """
    del request
    _require_exact_path_scope(tenant_id, authorization)
    mutation = payload.model_dump(exclude_unset=True)

    try:
        entity = TenantRegistry.update_profile(
            tenant_id,
            mutation,
        )
    except TenantRegistryError as error:
        logger.error("Authorized tenant PUT registry failure: %s", error)
        _raise_profile_update_registry_failure(error)

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        )

    return _entity_to_response(entity)


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
        Requires tenant:lifecycle:archive / lifecycle_archive through the frozen
        RequireTenantAuthorization composition.

    Tenant scope:
        Authorized X-Tenant-ID must exactly equal tenant_id before registry access.

    Mutation semantics:
        Calls TenantRegistry.archive only; archive remains soft status mutation.

    Return semantics:
        Modified tenant -> HTTP 204.
        No modification -> historical HTTP 404.

    Fail-closed semantics:
        Mongo archive outage -> bounded HTTP 503.

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
# VERSION: v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-WIRING
# AUTHORITY BOUNDARY: tenant HTTP composition, exact request schema, path/scope binding, bounded registry invocation, and HTTP translation only; durable authentication, membership, role, permission, and authorization truth remain external authorities
# TENANT POSTURE: authorized X-Tenant-ID must exactly equal the detail path tenant before GET/PUT/archive persistence; collection list and create remain contained
# FAIL-CLOSED POSTURE: GET uses profile_read, PUT uses profile_update, archive uses lifecycle_archive; extra PUT fields are rejected; mismatch denies 403; absence is 404; client mutation errors are 422; persistence corruption/outage/inconsistency is 503
# FINANCIAL EXECUTION AUTHORITY: None. Profile PUT cannot mutate plan; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
