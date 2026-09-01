"""Canonical public API for the Wilsy Engineering Kernel.

VERSION: v1.1.0-WILSY-ENGINEERING-KERNEL-API
PURPOSE: Expose the runner-owned EngineeringKernel execution contract.
AUTHORITY: Kernel API boundary only; no financial, provider, settlement, or ledger authority.
EPITOME: One stable façade returns the exact immutable session produced by the canonical runner.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kernel/api.py
CERTIFICATION DATE: 2026-08-29
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: delegates execution to the canonical runner; no credential or payment material handling.
TRANSACTION BOUNDARY: no Mongo transaction, provider I/O, settlement, or financial truth mutation.
TENANT BOUNDARY: caller tenant authority is explicit per execution and never retained.
AUTHORITY BOUNDARY: public façade forwards immutable bootstrap authority only.
DEPLOYMENT AUTHORITY: deployment environment is explicit per execution and never defaulted.
FINANCIAL AUTHORITY BOUNDARY: no financial, provider, settlement, or ledger authority.
RETURN CONTRACT: runner-produced EngineeringKernelSession is passed through unchanged.
CERTIFICATION LIMITATION: API certification waits for runner session/execution identity correction.
CHANGELOG: v1.1.0 requires and forwards per-execution request and deployment authority; v1.0.1 aligned execute() with the runner-owned session; v1.0.0 established the stable façade.
"""

from __future__ import annotations

from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest

from .runner import EngineeringKernelRunner, EngineeringKernelSession

VERSION = "v1.1.0-WILSY-ENGINEERING-KERNEL-API"


class EngineeringKernel:
    """
    Stable institutional Engineering Kernel API.

    Responsible only for exposing the canonical
    Engineering Kernel execution interface.
    """

    def __init__(self) -> None:
        """Initialize the canonical runner."""
        self._runner = EngineeringKernelRunner()

    def execute(
        self,
        request: KernelBootstrapRequest,
        deployment_environment: str,
    ) -> EngineeringKernelSession:
        """Forward explicit per-execution authority and return the runner session."""
        return self._runner.run(
            request=request,
            deployment_environment=deployment_environment,
        )


# ARTIFACT: api.py
# VERSION: v1.1.0-WILSY-ENGINEERING-KERNEL-API
# AUTHORITY BOUNDARY: public kernel façade only; no financial, provider, settlement, or ledger authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
