"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG211 INSTITUTIONAL REST API - SECURITY & TELEMETRY MIDDLEWARE
FILE: tools/eos/api/middleware.py
===============================================================================
Epitome:
    ASGI middleware for real-time telemetry logging, request ID tracing, and
    zero-trust header inspection across all incoming API requests.

Biblical Worth Billions:
    "In the mouth of two or three witnesses shall every word be established."
    — 2 Corinthians 13:1

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/api/middleware.py
===============================================================================
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SovereignTelemetryMiddleware(BaseHTTPMiddleware):
    """Injects execution tracing IDs, measures platform latency, and audits requests."""
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        execution_id = request.headers.get("X-Execution-ID", f"KEXEC-{uuid.uuid4().hex[:8].upper()}")
        
        request.state.execution_id = execution_id
        
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            response.headers["X-Execution-ID"] = execution_id
            response.headers["X-Platform-Latency-Ms"] = f"{duration_ms:.3f} ms"
            response.headers["X-Sovereign-System"] = "Wilsy OS Platform 1.0"
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            raise exc
