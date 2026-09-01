"""WILSY OS — authority-forwarding engineering-kernel runner.

TITLE: Engineering Kernel Runner and Pipeline
VERSION: v1.2.0-WILSY-KERNEL-RUNNER
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Forward one immutable bootstrap request per execution to the canonical bootstrap provider.
EPITOME: Reusable runner orchestration remains authority-stateless while preserving caller and deployment inputs.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kernel/runner.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
UPDATED: 2026-08-29
TENANT / REQUEST AUTHORITY: Per-execution KernelBootstrapRequest is forwarded unchanged.
DEPLOYMENT AUTHORITY: Per-execution deployment_environment is explicit and never defaulted.
SESSION / EXECUTION: Bootstrap owns session identity; runner owns a distinct execution identity per run.
SECURITY / PRIVACY: No authority material is retained on reusable runner or pipeline instances.
PROVIDER / RUNTIME BOUNDARY: Constructs the canonical bootstrap provider; no financial or settlement authority.
CHANGELOG: v1.2.0 separates runner execution identity from bootstrap session identity; v1.1.0 forwards certified authority; v1.0.0 initial runner wrapper.

WILSY OWNS BUSINESS TRUTH. EOS ALL THE WAY.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Dict

from . import WilsyKernelBootstrap
from .domain.kernel_bootstrap_request import KernelBootstrapRequest

logger = logging.getLogger("WilsyOS.Kernel.Runner")


@dataclass
class EngineeringKernelSession:
    """Execution result containing distinct runner execution identity and report."""

    execution_id: str
    result: Dict[str, Any]
    success: bool = True

    def __post_init__(self) -> None:
        """Derive success from the provider result without changing its shape."""
        self.success = self.result.get("status") == "SUCCESS"


class EngineeringKernelPipeline:
    """Authority-stateless orchestration wrapper around the bootstrap provider."""

    def execute(
        self,
        request: KernelBootstrapRequest,
        deployment_environment: str,
    ) -> EngineeringKernelSession:
        """Forward per-execution authority to the sole bootstrap normalization boundary."""
        logger.info("Starting Engineering Kernel Pipeline...")
        kernel = WilsyKernelBootstrap(
            request=request,
            deployment_environment=deployment_environment,
        )
        try:
            result = asyncio.run(kernel.boot_and_execute())
            logger.info("Pipeline complete. Status: %s", result.get("status", "UNKNOWN"))
        except Exception as error:
            logger.error("Pipeline failed: %s", error, exc_info=True)
            result = {
                "status": "FAILED",
                "error": str(error),
                "session_id": getattr(kernel, "session_id", "unknown"),
            }
        return EngineeringKernelSession(
            execution_id=result.get("session_id", "unknown"),
            result=result,
        )


class EngineeringKernelRunner:
    """Reusable runner that retains no tenant, request, or deployment authority."""

    def __init__(self) -> None:
        """Initialize an authority-stateless pipeline wrapper."""
        self._pipeline = EngineeringKernelPipeline()

    def run(
        self,
        request: KernelBootstrapRequest,
        deployment_environment: str,
    ) -> EngineeringKernelSession:
        """Execute one request with explicit authority and a new execution identity."""
        execution_id = f"KEXEC-{uuid.uuid4().hex[:12].upper()}"
        session = self._pipeline.execute(request, deployment_environment)
        session.execution_id = execution_id
        return session


if __name__ == "__main__":
    import json
    import sys

    runner = EngineeringKernelRunner()
    request = KernelBootstrapRequest(
        tenant_id="cli-tenant",
        principal_id="cli-principal",
        request_id="cli-request",
    )
    session = runner.run(request, "development")
    print("\n>>> KERNEL RUNNER EXECUTION SESSION <<<")
    print(json.dumps(session.result, indent=2, default=str))
    print("=" * 80)
    print(f"Session ID: {session.execution_id}")
    print(f"Success: {session.success}")
    sys.exit(0 if session.success else 1)


# ARTIFACT: runner.py
# VERSION: v1.2.0-WILSY-KERNEL-RUNNER
# AUTHORITY BOUNDARY: per-execution forwarding to canonical bootstrap only.
# TENANT POSTURE: request authority is explicit and never retained as reusable state.
# FAIL-CLOSED POSTURE: request and deployment environment are required parameters.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel financial truth remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
