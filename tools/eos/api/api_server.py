"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG211 INSTITUTIONAL REST API - MAIN APPLICATION SERVER
FILE: tools/eos/api/api_server.py
===============================================================================
Epitome:
    Main FastAPI ASGI application entrypoint for the FG211 Kernel Gateway.
    Integrates security middleware, exception handlers, and API routers.

Biblical Worth Billions:
    "In the mouth of two or three witnesses shall every word be established."
    — 2 Corinthians 13:1

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/api/api_server.py
===============================================================================
"""

import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from tools.eos.api.router import router
from tools.eos.api.middleware import SovereignTelemetryMiddleware
from tools.eos.api.exceptions import WilsyAPIException
from tools.eos.api.responses import format_response

app = FastAPI(
    title="Wilsy OS Kernel Gateway API",
    description="Institutional REST API exposing every Wilsy OS kernel capability for Platform 1.0.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register Middleware
app.add_middleware(SovereignTelemetryMiddleware)

# Register Router
app.include_router(router)


@app.exception_handler(WilsyAPIException)
async def wilsy_exception_handler(request: Request, exc: WilsyAPIException):
    execution_id = getattr(request.state, "execution_id", "KEXEC-FG211-ERROR")
    return format_response(
        data=exc.details,
        message=exc.message,
        status_code=exc.status_code,
        success=False,
        execution_id=execution_id
    )


@app.get("/", tags=["Root"])
async def root(request: Request):
    """Root health and gateway identification probe."""
    info = {
        "system": "Wilsy OS Platform 1.0",
        "module": "FG211 Institutional REST API",
        "status": "Gold Production Ready",
        "docs": "/docs"
    }
    execution_id = getattr(request.state, "execution_id", "KEXEC-FG211-ROOT")
    return format_response(data=info, message="Wilsy OS Kernel Gateway is fully operational.", execution_id=execution_id)
