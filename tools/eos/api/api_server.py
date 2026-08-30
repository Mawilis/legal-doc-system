# -*- coding: utf-8 -*-
"""TITLE: WILSY OS FG211 Institutional REST API Application Server.
VERSION: v1.1.0-TENANT-ROUTER-RUNTIME-REGISTRATION
AUTHORITY: Canonical FastAPI ASGI application composition for the Wilsy OS Kernel Gateway.
EPITOME: Preserves the governed kernel API surface while registering the frozen fail-closed tenant router in the canonical runtime application.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/api_server.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.1.0 registers the frozen tenant router exactly once in the canonical FastAPI application without activating tenant authorization or persistence access.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: ASGI composition only; router registration does not authenticate callers, derive authority, or access tenant persistence.
TENANT BOUNDARY: The application mounts the already-contained /api/tenants surface without changing tenant scope, membership, authorization, or persistence semantics.
AUTHORITY BOUNDARY: Owns FastAPI application composition and router registration only; authentication, tenant membership, role assignment, authorization, business truth, and transport authority remain outside this artifact.
FINANCIAL AUTHORITY BOUNDARY: No financial execution authority. Kennel EOS remains exclusive.
"""

from __future__ import annotations

import os
import sys
from typing import Any

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, Request

from tools.eos.api.exceptions import WilsyAPIException
from tools.eos.api.middleware import SovereignTelemetryMiddleware
from tools.eos.api.responses import format_response
from tools.eos.api.router import router
from tools.eos.api.tenant_router import tenant_router

VERSION = "v1.1.0-TENANT-ROUTER-RUNTIME-REGISTRATION"

app = FastAPI(
    title="Wilsy OS Kernel Gateway API",
    description="Institutional REST API exposing every Wilsy OS kernel capability for Platform 1.0.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Preserve canonical telemetry middleware.
app.add_middleware(SovereignTelemetryMiddleware)

# Preserve the existing general kernel/API router, then register the frozen
# fail-closed tenant HTTP surface without adding authority dependencies.
app.include_router(router)
app.include_router(tenant_router)


@app.exception_handler(WilsyAPIException)
async def wilsy_exception_handler(
    request: Request,
    exc: WilsyAPIException,
) -> Any:
    """Render governed Wilsy API exceptions through the canonical response envelope."""
    execution_id = getattr(request.state, "execution_id", "KEXEC-FG211-ERROR")
    return format_response(
        data=exc.details,
        message=exc.message,
        status_code=exc.status_code,
        success=False,
        execution_id=execution_id,
    )


@app.get("/", tags=["Root"])
async def root(request: Request) -> Any:
    """Return canonical FG211 gateway identity and health metadata."""
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


# ARTIFACT: api_server.py
# VERSION: v1.1.0-TENANT-ROUTER-RUNTIME-REGISTRATION
# AUTHORITY BOUNDARY: canonical ASGI composition and router registration only; no authentication, membership, role, authorization, or transport authority
# TENANT POSTURE: the frozen /api/tenants router is registered exactly once while every tenant operation remains fail-closed
# FAIL-CLOSED POSTURE: registration cannot activate tenant persistence or authorization; the frozen tenant router continues to deny before registry access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
