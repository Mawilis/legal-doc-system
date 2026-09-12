"""WILSY OS sovereign Python API server composition root.

TITLE: WILSY OS EOS Kernel API Server Factory
VERSION: v1.6.0-M11-HOST-PAYSHAP-MOUNT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Mounts sovereign Python API routers, including authenticated PayShap provider evidence ingress.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/server.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.6.0 mounts the authenticated PayShap host-runtime evidence router without changing billing or settlement authority; v1.5.1 dual-mounted billing for BFF parity.
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

VERSION = "v1.6.0-M11-HOST-PAYSHAP-MOUNT"

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
    ) -> None:
        """Initialize immutable server configuration and build the FastAPI app."""
        self.title = title
        self.description = description
        self.version = version
        self.debug = debug
        self.allowed_origins = allowed_origins or ["*"]
        self.app: FastAPI = self._build_app()

    def _build_app(self) -> FastAPI:
        """Compose middleware, lifecycle hooks, and sovereign routers."""
        app = FastAPI(
            title=self.title,
            description=self.description,
            version=self.version,
            debug=self.debug,
            docs_url="/docs",
            redoc_url="/redoc",
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allowed_origins,
            allow_credentials=True,
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
        async def start_dunning_scheduler() -> None:
            """Arm the daily dunning scheduler when enabled by environment policy."""
            enabled = os.getenv(
                "WILSY_DUNNING_SCHEDULER_ENABLED",
                "true",
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
# VERSION: v1.6.0-M11-HOST-PAYSHAP-MOUNT
# AUTHORITY BOUNDARY: HTTP application composition only; domain authorities remain separate.
# TENANT POSTURE: Mounted routers retain their canonical tenant isolation and admission rules.
# FAIL-CLOSED POSTURE: Unmounted or failed router composition is never represented as operational authority.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
