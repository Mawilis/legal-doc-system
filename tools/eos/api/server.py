"""WILSY OS sovereign Python API server composition root.

TITLE: WILSY OS EOS Kernel API Server Factory
VERSION: v1.13.0-C1B-R23-PRODUCTION-PROVIDER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Mounts sovereign Python API routers, including authenticated PayShap
         evidence ingress and the C1B authenticated reasoning command with a
         server-owned production provider binding.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/server.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.13.0-C1B-R23-PRODUCTION-PROVIDER composes one optional,
server-owned OpenAI Responses provider binding from environment configuration
and keeps reasoning I/O off the ASGI event loop;
v1.12.0-C1B-R19-AUTHENTICATED-REASONING mounts the server-owned,
authenticated C1B reasoning command and extends no-store privacy headers;
v1.11.0-L7B-WILSY-AI-LEGAL-TOOL-MOUNT mounts the composed
authenticated WILSY AI Legal Tool Gateway; v1.10.0-L7D-B-EXPLICIT-DB-BOOTSTRAP assigns explicit database
connect/disconnect ownership to the ASGI lifecycle; v1.9.0 remains historical.
debug/docs and credentialed wildcard CORS, adds architecture-independent
security headers and no-store Legal Operations responses, and defaults the
dunning scheduler off in production; v1.8.0-L7B-LEGAL-OPERATIONS-COMMAND-MOUNT mounts the dedicated
authenticated Legal Operations command and read routers under /api without
adding financial authority, plus authenticated GET-only Legal Operations
billing and client-invoice read projections without adding issuance, payment,
settlement, or Kennel execution authority; v1.6.0 mounts the authenticated
PayShap host-runtime evidence router without changing billing or settlement
authority; v1.5.1 dual-mounted billing for BFF parity.
v1.10.0-L7D-B-EXPLICIT-DB-BOOTSTRAP assigns database connect/disconnect to
the ASGI lifecycle, leaving kernel and billing imports inert and persistence
fail-closed until explicit startup succeeds.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned.
SECURITY / PRIVACY POSTURE: Router composition only; provider secrets and payloads are not logged or persisted here.
TENANT BOUNDARY: Mounted routers retain their own canonical tenant admission and isolation policies.
AUTHORITY BOUNDARY: HTTP application composition only; no identity, billing, provider, execution, or settlement truth is created here.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive financial execution authority; EXECUTION != SETTLEMENT.
FAIL-CLOSED DECLARATION: Router import/composition failures prevent the affected authority surface from being represented as mounted.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, List, Optional
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .auth_router import router as auth_router
from .authority_bridge_router import router as authority_bridge_router
from .billing_router import evaluate_all_tenant_dunning_lifecycles, router as billing_router
from .employee_router import router as employee_router
from .errors import register_error_handlers
from .kernel_routes import router as kernel_router
from .payshap_webhook_router import router as payshap_webhook_router
from .plan_router import plan_router
from .router import direct_router, router
from .subscription_router import subscription_router
from .tenant_router import tenant_router
from .legal_operations_router import router as legal_operations_router
from .legal_operations_command_router import router as legal_operations_command_router
from .legal_operations_billing_read_router import router as legal_operations_billing_read_router
from .wilsy_ai_legal_gateway_router import router as wilsy_ai_legal_gateway_router
from .wilsy_ai_reasoning_router import router as wilsy_ai_reasoning_router
from tools.eos.intelligence.providers.reasoning_provider_runtime import (
    build_reasoning_provider_binding_from_environment,
)
from tools.eos.kernel.db import connect_db, disconnect_db

VERSION = "v1.13.0-C1B-R23-PRODUCTION-PROVIDER"

logger = logging.getLogger("WilsyOS.API.Server")


class WilsyAPIServer:
    """Build the canonical FastAPI composition root without owning domain truth."""

    def __init__(
        self,
        title: str = "Wilsy OS Institutional API Gateway",
        description: str = "Billion-dollar institutional legal document & intelligence API platform.",
        version: str = "1.0.0",
        debug: bool = False,
        allowed_origins: Optional[List[str]] = None,
        reasoning_provider_binding: Any | None = None,
    ) -> None:
        """Initialize immutable server configuration and build the FastAPI app."""
        self.title = title
        self.description = description
        self.version = version
        self.production_mode = os.getenv("WILSY_ENV", os.getenv("ENV", "")).strip().lower() == "production"
        # Production must never inherit debug or wildcard credentialed CORS.
        self.debug = bool(debug) and not self.production_mode
        configured_origins = os.getenv("WILSY_CORS_ALLOWED_ORIGINS", "")
        parsed_origins = [item.strip() for item in configured_origins.split(",") if item.strip()]
        self.allowed_origins = list(allowed_origins) if allowed_origins is not None else parsed_origins
        if reasoning_provider_binding is None:
            try:
                reasoning_provider_binding = build_reasoning_provider_binding_from_environment()
            except Exception as error:
                # Configuration failure is isolated to optional reasoning; a
                # stable code is logged without exposing secrets or values.
                code = getattr(error, "code", "R23_PROVIDER_CONFIGURATION_INVALID")
                logger.error("[WILSY_AI_PROVIDER] binding unavailable: %s", code)
                reasoning_provider_binding = None
        self.reasoning_provider_binding = reasoning_provider_binding
        self.app: FastAPI = self._build_app()

    def _build_app(self) -> FastAPI:
        """Compose middleware, lifecycle hooks, and sovereign routers."""
        app = FastAPI(
            title=self.title,
            description=self.description,
            version=self.version,
            debug=self.debug,
            docs_url="/docs" if (not self.production_mode or os.getenv("WILSY_API_DOCS_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}) else None,
            redoc_url="/redoc" if (not self.production_mode or os.getenv("WILSY_API_DOCS_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}) else None,
        )
        app.state.wilsy_ai_reasoning_provider_binding = self.reasoning_provider_binding

        allow_credentials = "*" not in self.allowed_origins and bool(self.allowed_origins)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allowed_origins,
            allow_credentials=allow_credentials,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.middleware("http")
        async def tracing_middleware(
            request: Request,
            call_next: Callable[..., Any],
        ) -> Response:
            """Attach bounded request execution metadata without creating authority."""
            start_time = time.perf_counter()
            if not hasattr(request.state, "execution_id"):
                request.state.execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
            response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000
            response.headers["X-Process-Time-Ms"] = f"{process_time:.3f}"
            response.headers["X-Wilsy-OS-Kernel"] = "FG169-Active"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["X-Frame-Options"] = "DENY"
            if request.url.path.startswith(("/api/legal-operations", "/api/wilsy-ai/reasoning")):
                response.headers["Cache-Control"] = "no-store"
            if "x-trace-id" not in response.headers and "x-trace-id" in request.headers:
                response.headers["x-trace-id"] = request.headers["x-trace-id"]
            return response

        register_error_handlers(app, debug=self.debug)

        async def run_dunning_scheduler() -> None:
            """Execute the ledger-owned dunning pass once daily at 00:15 SAST."""
            timezone_sast = ZoneInfo("Africa/Johannesburg")
            while True:
                now = datetime.now(timezone_sast)
                next_run = now.replace(hour=0, minute=15, second=0, microsecond=0)
                if now >= next_run:
                    next_run += timedelta(days=1)
                await asyncio.sleep((next_run - now).total_seconds())
                try:
                    result = await evaluate_all_tenant_dunning_lifecycles()
                    logger.info(
                        "[DUNNING_SCHEDULER] Daily evaluation complete: tenants=%s transitions=%s",
                        result["evaluated_tenants"],
                        result["transition_count"],
                    )
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception(
                        "[DUNNING_SCHEDULER] Daily evaluation failed; next scheduled pass remains armed"
                    )

        @app.on_event("startup")
        async def start_database() -> None:
            """Own explicit database bootstrap at application startup."""
            connected, detail = connect_db()
            if not connected:
                logger.error("[KENNEL_DB] Explicit startup bootstrap unavailable: %s", detail)

        @app.on_event("shutdown")
        async def stop_database() -> None:
            """Release the kernel database during controlled application shutdown."""
            disconnect_db()

        @app.on_event("startup")
        async def start_dunning_scheduler() -> None:
            """Arm the daily dunning scheduler when enabled by environment policy."""
            enabled = os.getenv(
                "WILSY_DUNNING_SCHEDULER_ENABLED",
                "false" if self.production_mode else "true",
            ).strip().lower() in {"1", "true", "yes", "on"}
            if enabled:
                app.state.dunning_scheduler_task = asyncio.create_task(
                    run_dunning_scheduler()
                )
                logger.info(
                    "[DUNNING_SCHEDULER] Armed for daily 00:15 SAST evaluation"
                )
            else:
                logger.warning(
                    "[DUNNING_SCHEDULER] Disabled by WILSY_DUNNING_SCHEDULER_ENABLED"
                )

        @app.on_event("shutdown")
        async def stop_dunning_scheduler() -> None:
            """Cancel the scheduler cleanly during controlled API shutdown."""
            task = getattr(app.state, "dunning_scheduler_task", None)
            if task:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

        @app.get("/")
        async def root_health() -> dict[str, str]:
            """Return bounded API composition health metadata."""
            return {
                "status": "OPERATIONAL",
                "kernel": "EOS Kernel v1.6.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bridge": "kernel-v1.1.1",
            }

        # Sovereign mounting order.
        app.include_router(kernel_router)
        app.include_router(kernel_router, prefix="/api")

        app.include_router(direct_router)
        app.include_router(router)
        app.include_router(tenant_router)
        app.include_router(legal_operations_router, prefix="/api")
        app.include_router(legal_operations_command_router, prefix="/api")
        app.include_router(legal_operations_billing_read_router, prefix="/api")
        app.include_router(wilsy_ai_legal_gateway_router, prefix="/api")
        app.include_router(wilsy_ai_reasoning_router, prefix="/api")
        app.include_router(subscription_router)
        app.include_router(plan_router)

        app.include_router(auth_router, prefix="/api")

        app.include_router(billing_router)
        app.include_router(billing_router, prefix="/api")

        app.include_router(employee_router)
        app.include_router(authority_bridge_router)

        # Provider evidence ingress is mounted once at its canonical route.
        app.include_router(payshap_webhook_router)

        logger.info(
            "WilsyAPIServer [%s v%s] initialized with sovereign routers "
            "(kernel, auth, billing, employees, internal authority, PayShap evidence).",
            self.title,
            self.version,
        )
        return app

    def get_app(self) -> FastAPI:
        """Return the already-built canonical FastAPI application."""
        return self.app


app = WilsyAPIServer().get_app()

# ARTIFACT: server.py
# VERSION: v1.13.0-C1B-R23-PRODUCTION-PROVIDER
# AUTHORITY BOUNDARY: HTTP application composition only; domain authorities remain separate.
# TENANT POSTURE: Mounted routers retain their canonical tenant isolation and admission rules.
# FAIL-CLOSED POSTURE: Unmounted or failed router composition is never represented as operational authority.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
