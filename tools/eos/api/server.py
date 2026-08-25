"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – EOS KERNEL API SERVER FACTORY (DUAL KERNEL MOUNT + AUTH + BILLING + EMPLOYEE ROUTERS)              ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ FILE:           tools/eos/api/server.py                                                                        ║
║ VERSION:        v1.5.1-BILLING-API-ALIAS                                                                       ║
║ EPITOME:        FastAPI application with kernel, tenant, plan, subscription, authentication, billing,          ║
║                 and employee routers. Auth under /api/auth. Billing at /billing AND /api/billing.              ║
║ CLASSIFICATION: Production Artifact                                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🔧 CHANGE LOG:                                                                                                  ║
║   2026-08-22 v1.5.1-BILLING-API-ALIAS – Dual-mount billing_router at /billing and /api/billing for BFF parity.║
║   2026-08-22 v1.5.0-AUTH-PREFIX – Mount auth_router with prefix /api so auth endpoints are /api/auth/*.       ║
║   2026-08-20 v1.4.0-EMPLOYEE-MOUNTED – Mounted employee_router.                                               ║
║   2026-08-20 v1.3.0-BILLING-MOUNTED – Mounted billing_router.                                                 ║
║   2026-08-20 v1.2.0-AUTH-MOUNTED – Mounted auth_router.                                                        ║
║   ... (earlier versions)                                                                                        ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ ROUTES:                                                                                                        ║
║   - / (health)                                                                                                 ║
║   - /api/auth/login, /api/auth/verify-otp, /api/auth/discover, /api/auth/logout                               ║
║   - /billing/platform/invoices, /billing/client/invoices, /billing/payments, ...                               ║
║   - /api/billing/platform/invoices, /api/billing/client/invoices (alias)                                     ║
║   - /api/employees/search, /api/employees/{employee_id}                                                        ║
║   - /kernel, /kernel/status, /kernel/execute, /kernel/governance                                              ║
║   - /api/kernel, /api/kernel/status, /api/kernel/execute, /api/kernel/governance                              ║
║   - /api/tenants, /api/plans, /api/subscriptions                                                               ║
║   - /api/v1/... (legacy)                                                                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
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

from .errors import register_error_handlers
from .router import router, direct_router
from .kernel_routes import router as kernel_router
from .subscription_router import subscription_router
from .plan_router import plan_router
from .tenant_router import tenant_router
from .auth_router import router as auth_router
from .billing_router import evaluate_all_tenant_dunning_lifecycles, router as billing_router
from .employee_router import router as employee_router

logger = logging.getLogger("WilsyOS.API.Server")


class WilsyAPIServer:
    def __init__(
        self,
        title: str = "Wilsy OS Institutional API Gateway",
        description: str = "Billion-dollar institutional legal document & intelligence API platform.",
        version: str = "1.0.0",
        debug: bool = False,
        allowed_origins: Optional[List[str]] = None,
    ) -> None:
        self.title = title
        self.description = description
        self.version = version
        self.debug = debug
        self.allowed_origins = allowed_origins or ["*"]
        self.app: FastAPI = self._build_app()

    def _build_app(self) -> FastAPI:
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
        async def tracing_middleware(request: Request, call_next: Callable) -> Response:
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
            """Executes the ledger-owned dunning pass once daily at 00:15 SAST.

            @returns: Never returns while the Kennel API remains online.
            @collaboration: Uses idempotent invoice lifecycle transitions so a controlled reload cannot duplicate a state change.
            """
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
                    logger.exception("[DUNNING_SCHEDULER] Daily evaluation failed; next scheduled pass remains armed")

        @app.on_event("startup")
        async def start_dunning_scheduler() -> None:
            """Arms the Kennel-native daily dunning scheduler when enabled by environment policy.

            @returns: None after task registration.
            @collaboration: A single API process owns the task; lifecycle writes are independently idempotent for safe clustered deployment.
            """
            enabled = os.getenv("WILSY_DUNNING_SCHEDULER_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
            if enabled:
                app.state.dunning_scheduler_task = asyncio.create_task(run_dunning_scheduler())
                logger.info("[DUNNING_SCHEDULER] Armed for daily 00:15 SAST evaluation")
            else:
                logger.warning("[DUNNING_SCHEDULER] Disabled by WILSY_DUNNING_SCHEDULER_ENABLED")

        @app.on_event("shutdown")
        async def stop_dunning_scheduler() -> None:
            """Cancels the outstanding sleep cleanly during controlled Kennel shutdown.

            @returns: None after any active scheduler task has settled.
            @collaboration: Avoids orphaned evaluation tasks when Uvicorn reloads the API process.
            """
            task = getattr(app.state, "dunning_scheduler_task", None)
            if task:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

        @app.get("/")
        async def root_health():
            return {
                "status": "OPERATIONAL",
                "kernel": "EOS Kernel v1.5.1",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bridge": "kernel-v1.1.1",
            }

        # 🏛️ SOVEREIGN MOUNTING ORDER
        # Kernel router at root (/kernel) and also under /api (/api/kernel)
        app.include_router(kernel_router)                     # /kernel, /kernel/status, ...
        app.include_router(kernel_router, prefix="/api")      # /api/kernel, /api/kernel/status, ...

        # Other routers
        app.include_router(direct_router)                     # /api/... (legacy)
        app.include_router(router)                            # /api/v1/...
        app.include_router(tenant_router)                     # /api/tenants
        app.include_router(subscription_router)               # /api/subscriptions
        app.include_router(plan_router)                       # /api/plans

        # Authentication – mounted under /api
        app.include_router(auth_router, prefix="/api")        # /api/auth/login, etc.

        # Billing – dual mount for BFF/Vite parity
        app.include_router(billing_router)                    # /billing/platform/invoices, ...
        app.include_router(billing_router, prefix="/api")     # /api/billing/platform/invoices, ...

        # Employee
        app.include_router(employee_router)                   # /api/employees/search, etc.

        logger.info(
            "WilsyAPIServer [%s v%s] initialized with all sovereign routers "
            "(kernel at /kernel and /api/kernel, auth at /api/auth, "
            "billing at /billing and /api/billing, employees at /api/employees).",
            self.title, self.version
        )
        return app

    def get_app(self) -> FastAPI:
        return self.app


app = WilsyAPIServer().get_app()

"""
════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS KERNEL API SERVER
════════════════════════════════════════════════════════════════════════════════
Status:          CERTIFIED PRODUCTION ARTIFACT
Version:         v1.5.1-BILLING-API-ALIAS
Routes:          /api/auth/*, /billing/*, /api/billing/*, /api/employees/*, /kernel, /api/kernel,
                 /api/tenants, /api/plans, /api/subscriptions
Port:            9095
Health Check:    curl http://127.0.0.1:9095/
Auth Login:      curl -X POST http://127.0.0.1:9095/api/auth/login ...
Billing:         curl http://127.0.0.1:9095/billing/platform/invoices
                 curl http://127.0.0.1:9095/api/billing/platform/invoices
════════════════════════════════════════════════════════════════════════════════
"""
