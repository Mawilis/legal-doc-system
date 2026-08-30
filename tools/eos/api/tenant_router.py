# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS — TENANT ROUTER (KENNEL EOS) – WITH VERIFIED FIELD                                                   ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ FILE:           tools/eos/api/tenant_router.py                                                                ║
║ VERSION:        v1.0.4-TENANT-AUTHORITY-CONTAINMENT                                                          ║
║ AUTHORITY:      Wilsy OS Core Governance                                                                       ║
║ EPITOME:        FastAPI router for tenant registry operations (CRUD + search).                                 ║
║                 Added verified field to response and request models.                                           ║
║ CLASSIFICATION: Production Artifact                                                                            ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🔧 CHANGE LOG:                                                                                                  ║
║   2026-08-30 v1.0.4-TENANT-AUTHORITY-CONTAINMENT – Temporarily deny all tenant routes until governed authority ║
║                composition exists; removes anonymous and legacy role/header authority paths.                 ║
║   2026-08-23 v1.0.3-VERIFIED-FIELD – Added verified field to TenantResponse, TenantCreateRequest, and           ║
║                TenantUpdateRequest; updated _entity_to_response to include verified.                           ║
║   2026-08-21 v1.0.2-TENANT-RESPONSE – Changed response field from "items" to "tenants" for frontend compat.   ║
║   2026-08-21 v1.0.1-TENANT-ENDPOINTS – Fixed Pylance errors.                                                  ║
║   2026-08-21 v1.0.0-TENANT-ENDPOINTS – Initial production release.                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COMPLIANCE:    POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001                                                  ║
║ ROUTES:        /api/tenants (GET, POST), /api/tenants/{tenant_id} (GET, PUT, DELETE)                          ║
║ DEPENDENCIES:  fastapi, pydantic, tenant_registry                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import logging
from typing import List, NoReturn, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

# Import the tenant registry
from ..saas.tenancy.tenant_registry import TenantRegistry

logger = logging.getLogger("WilsyOS.API.TenantRouter")

# ─── Pydantic Models ──────────────────────────────────────────────────────────

class TenantCreateRequest(BaseModel):
    name: str = Field(..., description="Organization name")
    tenant_id: Optional[str] = Field(None, description="Optional custom tenant ID; auto‑generated if omitted")
    alias: Optional[str] = Field(None, description="Human‑readable alias (unique)")
    industry: Optional[str] = None
    region: Optional[str] = None
    sector: Optional[str] = None
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    contact_email: Optional[str] = None
    plan: Optional[str] = "ENTERPRISE"
    status: Optional[str] = "ACTIVE"
    compliance_flags: Optional[dict] = None
    checksum: Optional[str] = None
    verified: Optional[bool] = None   # <-- NEW

class TenantUpdateRequest(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    sector: Optional[str] = None
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    contact_email: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None
    checksum: Optional[str] = None
    verified: Optional[bool] = None   # <-- NEW

class TenantResponse(BaseModel):
    tenant_id: str
    alias: Optional[str]
    name: str
    legal_name: Optional[str]
    tax_id: Optional[str]
    contact_email: Optional[str]
    industry: Optional[str]
    region: Optional[str]
    sector: Optional[str]
    status: str
    subscription_tier: Optional[str]
    compliance_flags: Optional[dict]
    created_at: Optional[str]
    updated_at: Optional[str]
    proof_hash: Optional[str]
    verified: Optional[bool]   # <-- NEW

class TenantListResponse(BaseModel):
    tenants: List[TenantResponse]   # <--- CHANGED FROM "items" TO "tenants"
    total: int

# ─── Helper ──────────────────────────────────────────────────────────────────

def _entity_to_response(entity) -> TenantResponse:
    """Convert a TenantEntity to a TenantResponse Pydantic model."""
    if not entity:
        raise ValueError("Tenant entity is None")
    org = entity.organization
    return TenantResponse(
        tenant_id=entity.tenant_id,
        alias=getattr(entity, "alias", None),
        name=org.organization_name,
        legal_name=org.legal_name,
        tax_id=org.tax_id,
        contact_email=org.contact_email,
        industry=org.industry,
        region=getattr(entity, "region", None),
        sector=None,
        status=entity.status,
        subscription_tier=getattr(entity, "subscription_tier", None),
        compliance_flags=getattr(entity, "compliance_flags", None),
        created_at=entity.created_at,
        updated_at=None,
        proof_hash=getattr(entity, "proof_hash", None),
        verified=getattr(entity, "verified", False),   # <-- NEW
    )

# ─── Router ──────────────────────────────────────────────────────────────────

tenant_router = APIRouter(prefix="/api/tenants", tags=["tenants"])
VERSION = "v1.0.4-TENANT-AUTHORITY-CONTAINMENT"


def _require_tenant_authority_available() -> NoReturn:
    """Deny until a governed tenant authority composition is available."""
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="TENANT_AUTHORITY_UNAVAILABLE")

@tenant_router.get("", response_model=TenantListResponse)
async def list_tenants(
    request: Request,
    search: Optional[str] = Query(None, description="Search by name or alias (case‑insensitive)"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Temporarily deny tenant listing before any persistence access."""
    del request, search, skip, limit
    _require_tenant_authority_available()


@tenant_router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    request: Request,
):
    """Temporarily deny tenant reads before any persistence access."""
    del tenant_id, request
    _require_tenant_authority_available()


@tenant_router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreateRequest,
    request: Request,
):
    """Temporarily deny tenant creation before any persistence access."""
    del payload, request
    _require_tenant_authority_available()


@tenant_router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    payload: TenantUpdateRequest,
    request: Request,
):
    """Temporarily deny tenant updates before any persistence access."""
    del tenant_id, payload, request
    _require_tenant_authority_available()


@tenant_router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_tenant(
    tenant_id: str,
    request: Request,
):
    """Temporarily deny tenant archival before any persistence access."""
    del tenant_id, request
    _require_tenant_authority_available()


"""
════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL CERTIFICATION SEAL — Tenant Router v1.0.4-TENANT-AUTHORITY-CONTAINMENT
════════════════════════════════════════════════════════════════════════════════
Status:          CERTIFIED PRODUCTION ARTIFACT
Version:         v1.0.4-TENANT-AUTHORITY-CONTAINMENT
Change:          All tenant routes deny before registry access until governed authority exists.
Routes:          /api/tenants (GET, POST) · /api/tenants/{id} (GET, PUT, DELETE)
Compliance:      POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001
Authentication:  No route assumes authentication, role names, GLOBAL_ROOT, or X-Tenant-ID authority.
Tenant Isolation: Tenant operations are unavailable until explicit governed authority is composed.
════════════════════════════════════════════════════════════════════════════════
"""

# ARTIFACT: tenant_router.py
# VERSION: v1.0.4-TENANT-AUTHORITY-CONTAINMENT
# AUTHORITY BOUNDARY: tenant HTTP surface only; no authentication, membership, role, authorization, or financial authority
# TENANT POSTURE: all tenant operations fail closed until governed tenant authority is available
# FAIL-CLOSED POSTURE: deterministic HTTP 503 TENANT_AUTHORITY_UNAVAILABLE before any registry access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
