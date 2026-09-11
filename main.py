# -*- coding: utf-8 -*-
"""Authority-neutral root adapter for the canonical Wilsy Engineering Kernel.

TITLE: WILSY OS Root Kernel Bootstrap Adapter
VERSION: v1.0.0-WILSY-ROOT-KERNEL-BOOTSTRAP-ADAPTER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Executes the canonical Engineering Kernel only with explicit authority supplied by an upstream trusted ingress.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/main.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder & Chief Architect); Wilsy Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 establishes the first sovereign certification of the root kernel adapter, retires the fractured legacy ExecutionContext bootstrap path, removes synthetic tenant/principal/request authority, and requires explicit per-execution kernel authority and deployment environment.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; authority provenance remains upstream-owned and fail-closed.
SECURITY / PRIVACY POSTURE: This adapter stores no credentials, claims, tenant state, principal state, request state, or reusable execution authority.
TENANT BOUNDARY: tenant_id is accepted only inside an already-constructed KernelBootstrapRequest and is never created, defaulted, rewritten, or retained here.
AUTHORITY BOUNDARY: Authentication, tenant membership, authorization, request ingress, correlation trust, and deployment policy are upstream responsibilities; this module only forwards their explicit result to the canonical kernel API.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    The repository-root compatibility seam for invoking the canonical
    EngineeringKernel API. The adapter is deliberately authority-neutral:
    callers must establish tenant, principal, request, optional correlation,
    and deployment context before execution reaches this module.

    Direct ``python main.py`` execution cannot establish those authorities and
    therefore fails closed rather than manufacturing system, tenant, principal,
    request, correlation, or deployment truth.

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    Engineering Collaboration: Wilsy Core Engineering
    File Path: main.py
"""
from __future__ import annotations

import sys

from tools.eos.kernel.api import EngineeringKernel
from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.kernel.runner import EngineeringKernelSession

VERSION = "v1.0.0-WILSY-ROOT-KERNEL-BOOTSTRAP-ADAPTER"


class RootKernelBootstrapAuthorityError(RuntimeError):
    """Fail-closed error raised when root execution lacks an authority-bearing ingress."""


def bootstrap(
    request: KernelBootstrapRequest,
    deployment_environment: str,
) -> EngineeringKernelSession:
    """Execute one canonical kernel run using explicit upstream-proven authority.

    Authority:
        ``request`` remains caller-owned. This adapter does not create,
        reconstruct, substitute, normalize, or retain tenant, principal,
        request, correlation, session, or execution identity.

    Tenant scope:
        The exact tenant carried by ``KernelBootstrapRequest`` is forwarded
        unchanged. This function performs no membership or tenant authorization
        lookup and therefore cannot grant tenant authority.

    Deployment:
        ``deployment_environment`` is required for every execution and is
        forwarded unchanged. No production, development, test, or other
        environment fallback exists here.

    Mutation and persistence:
        This adapter owns no persistence, transaction, session, retry,
        idempotency, or durable state. Reusable module state retains no
        per-execution authority.

    Fail-closed behavior:
        Kernel request validation and execution errors propagate unchanged.
        Missing authority is never replaced with compatibility literals.

    Financial boundary:
        This adapter has no financial execution authority. Kennel EOS remains
        the exclusive authority for financial execution truth.
    """
    kernel = EngineeringKernel()
    return kernel.execute(
        request=request,
        deployment_environment=deployment_environment,
    )


def main() -> int:
    """Refuse direct root execution because this process owns no authority ingress.

    ``python main.py`` has no authenticated principal, authorized tenant,
    inbound request boundary, trusted correlation assertion, or governed
    deployment context from which a valid ``KernelBootstrapRequest`` can be
    derived. Direct execution therefore terminates explicitly and performs no
    kernel work.

    Returns:
        Non-zero process status indicating fail-closed refusal.

    Financial boundary:
        No financial execution or settlement authority is exercised.
    """
    error = RootKernelBootstrapAuthorityError(
        "ROOT_KERNEL_AUTHORITY_REQUIRED: direct main.py execution has no "
        "authority-bearing ingress; supply an authorized KernelBootstrapRequest "
        "and explicit deployment environment through a trusted caller"
    )
    print(f"[CRITICAL FAILURE] {error}", file=sys.stderr)
    return 1


__all__ = [
    "VERSION",
    "RootKernelBootstrapAuthorityError",
    "bootstrap",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())


# ARTIFACT: main.py
# VERSION: v1.0.0-WILSY-ROOT-KERNEL-BOOTSTRAP-ADAPTER
# AUTHORITY BOUNDARY: authority-neutral adapter; authentication, tenant authorization, request ingress, correlation trust, and deployment policy remain upstream
# TENANT POSTURE: exact explicit KernelBootstrapRequest tenant is forwarded unchanged; no tenant default, synthesis, retention, or cross-tenant authority
# FAIL-CLOSED POSTURE: direct execution and missing authority cannot fall back to synthetic tenant, principal, request, correlation, or deployment values
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains the exclusive financial execution authority
# END OF WILSY OS SOVEREIGN ARTIFACT
