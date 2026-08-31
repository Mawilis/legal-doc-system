# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
FG211 INSTITUTIONAL REST API — CANONICAL APPLICATION SERVER
===============================================================================

TITLE:
    WILSY OS FG211 Institutional REST API Application Server

FILE:
    tools/eos/api/api_server.py

VERSION:
    v1.3.0-TENANT-PROFILE-UPDATE-CONTROLLED-ACTIVATION

AUTHORITY:
    Wilsy OS Core Governance.
    Canonical FastAPI ASGI application composition for the Wilsy OS Kernel Gateway.

EPITOME:
    Preserves the governed kernel API surface while registering the canonical
    tenant router exactly once. Application composition grants no tenant authority:
    controlled profile GET, strict profile PUT, and lifecycle archive are governed
    inside tenant_router through the frozen durable authorization dependency,
    while global tenant list and lifecycle create remain contained.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/api_server.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-31

CHANGELOG:
    v1.3.0-TENANT-PROFILE-UPDATE-CONTROLLED-ACTIVATION
        - Aligns canonical application governance with C2 controlled profile PUT.
        - Records that GET detail, PUT detail, and DELETE/archive compose durable
          authority inside tenant_router and require exact tenant scope/path binding
          before persistence.
        - Records that collection GET and POST create remain contained.
        - Preserves exact router registration, middleware, exception handling,
          application metadata, root endpoint, and general API composition.

    v1.2.0-TENANT-ROUTER-CONTROLLED-ACTIVATION
        - Aligned application composition with B2B GET/archive activation while
          collection GET, POST, and PUT remained contained.

    v1.1.0-TENANT-ROUTER-RUNTIME-REGISTRATION
        - Registered the then-contained tenant router exactly once.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    ASGI composition only. Router registration never authenticates a caller,
    derives membership, interprets role projections, or grants permission.
    Activated tenant detail routes remain governed by their own durable
    authorization dependencies, exact scope/path checks, and persistence failure
    boundaries.

TENANT BOUNDARY:
    The application mounts exactly one /api/tenants router. Tenant scope and path
    congruence are enforced inside activated detail routes. No alternate tenant
    mount, global-list authority, or cross-tenant authority is created here.

AUTHORITY BOUNDARY:
    Owns FastAPI application composition and router registration only.
    Authentication, principal truth, tenant membership, business-role truth,
    permission grants, final authorization, and tenant persistence remain separate
    authorities.

FINANCIAL AUTHORITY BOUNDARY:
    No financial execution authority exists in this artifact.
    Kennel EOS remains the exclusive financial execution authority.

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    Full-file sovereign artifact.
    Fail-closed.
===============================================================================
"""

from __future__ import annotations

import os
import sys
from typing import Any

project_root = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../..",
    )
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, Request

from tools.eos.api.exceptions import WilsyAPIException
from tools.eos.api.middleware import SovereignTelemetryMiddleware
from tools.eos.api.responses import format_response
from tools.eos.api.router import router
from tools.eos.api.tenant_router import tenant_router


VERSION = "v1.3.0-TENANT-PROFILE-UPDATE-CONTROLLED-ACTIVATION"


app = FastAPI(
    title="Wilsy OS Kernel Gateway API",
    description=(
        "Institutional REST API exposing every Wilsy OS kernel capability "
        "for Platform 1.0."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(SovereignTelemetryMiddleware)


app.include_router(router)

# Registration itself grants no tenant authority. GET detail, strict PUT detail,
# and DELETE/archive compose frozen RequireTenantAuthorization inside
# tenant_router. Collection GET and POST create remain contained there.
app.include_router(tenant_router)


@app.exception_handler(WilsyAPIException)
async def wilsy_exception_handler(
    request: Request,
    exc: WilsyAPIException,
) -> Any:
    """Render governed Wilsy API exceptions through the canonical envelope.

    Authority:
        HTTP exception translation only.

    Tenant scope:
        No tenant resolution or authorization occurs here.

    Mutation semantics:
        Read-only response construction.

    Financial boundary:
        No financial execution authority.
    """
    execution_id = getattr(
        request.state,
        "execution_id",
        "KEXEC-FG211-ERROR",
    )
    return format_response(
        data=exc.details,
        message=exc.message,
        status_code=exc.status_code,
        success=False,
        execution_id=execution_id,
    )


@app.get("/", tags=["Root"])
async def root(request: Request) -> Any:
    """Return canonical FG211 gateway identity and health metadata.

    Authority:
        Health/identity metadata only.

    Tenant scope:
        No tenant access is performed.

    Mutation semantics:
        Read-only.

    Financial boundary:
        No financial execution authority.
    """
    info = {
        "system": "Wilsy OS Platform 1.0",
        "module": "FG211 Institutional REST API",
        "status": "Gold Production Ready",
        "docs": "/docs",
    }
    execution_id = getattr(
        request.state,
        "execution_id",
        "KEXEC-FG211-ROOT",
    )
    return format_response(
        data=info,
        message="Wilsy OS Kernel Gateway is fully operational.",
        execution_id=execution_id,
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: api_server.py
# VERSION: v1.3.0-TENANT-PROFILE-UPDATE-CONTROLLED-ACTIVATION
# AUTHORITY BOUNDARY: canonical ASGI composition and router registration only; authentication, membership, business-role, permission, authorization, and persistence authority remain outside this artifact
# TENANT POSTURE: exactly one tenant router is mounted; GET/PUT/DELETE detail operations are governed inside that router; collection GET and POST remain contained; no alternate mount creates cross-tenant authority
# FAIL-CLOSED POSTURE: application registration never grants authority; tenant persistence is reachable only through activated router dependencies, exact scope/path checks, and bounded persistence contracts
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
