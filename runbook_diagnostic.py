"""Local smoke diagnostic for the canonical WILSY Engineering Kernel API.

This script uses synthetic authority references and the supported public API.
It does not connect to production services or grant business authority.
"""

from __future__ import annotations

import sys

from tools.eos.kernel.api import EngineeringKernel
from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.kernel.runner import EngineeringKernelSession


def run_diagnostic() -> None:
    print("--- [LOCAL SMOKE TEST] WILSY Engineering Kernel ---")
    request = KernelBootstrapRequest(
        tenant_id="diagnostic-tenant",
        principal_id="diagnostic-principal",
        request_id="diagnostic-runbook",
    )
    session = EngineeringKernel().execute(
        request=request,
        deployment_environment="development",
    )

    if not isinstance(session, EngineeringKernelSession):
        raise TypeError(
            "EngineeringKernel.execute() returned an unexpected session type"
        )
    if not session.success or session.result.get("status") != "SUCCESS":
        raise RuntimeError(
            f"Engineering Kernel diagnostic failed: {session.result.get('error', 'unknown error')}"
        )

    print(f"[PASS] EngineeringKernel session: {session.execution_id}")
    print("[PASS] Canonical bootstrap pipeline completed successfully.")
    print("--- [LOCAL SMOKE TEST] All checks passed ---")


if __name__ == "__main__":
    try:
        run_diagnostic()
    except Exception as error:
        print(f"[CRITICAL FAILURE] {error}", file=sys.stderr)
        sys.exit(1)
