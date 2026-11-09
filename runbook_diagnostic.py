"""WILSY OS — local Kennel EOS bootstrap diagnostic.

TITLE: Kennel EOS Local Runbook Diagnostic
VERSION: v1.0.0-WILSY-KENNEL-EOS-RUNBOOK-DIAGNOSTIC
AUTHORITY: Wilsy OS Core Governance
EPITOME: Executes one synthetic, development-only bootstrap through the canonical public EngineeringKernel API and fails closed unless the runner returns a successful session.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/runbook_diagnostic.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
CERTIFICATION / UPDATE DATE: 2026-11-08
CHANGELOG:
- v1.0.0-WILSY-KENNEL-EOS-RUNBOOK-DIAGNOSTIC: Establishes the canonical public-API local smoke diagnostic with explicit synthetic tenant/principal/request references and non-zero failure exit.
COMPLIANCE: WILSY OS Sovereign Codex Governance Contract v1.2.0; development-only diagnostic.
SECURITY / PRIVACY POSTURE: Uses synthetic references only; emits no credentials, tokens, personal data, or production configuration.
TENANT BOUNDARY: The request is scoped to the explicit synthetic diagnostic tenant; no real tenant is impersonated or accessed.
AUTHORITY BOUNDARY: Exercises bootstrap orchestration only; it does not authenticate a user, grant membership/capacity, authorize business actions, or mutate canonical business records.
FINANCIAL AUTHORITY BOUNDARY: No payment, provider, financial execution, settlement, invoice, or ledger authority.
TRANSACTION BOUNDARY: No database connection or transaction is opened by this diagnostic.

WILSY OWNS BUSINESS TRUTH. KENNEL EOS IS THE EXCLUSIVE FINANCIAL EXECUTION AUTHORITY.
EOS ALL THE WAY.
"""

from __future__ import annotations

import sys

from tools.eos.kernel.api import EngineeringKernel
from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.kernel.runner import EngineeringKernelSession


def run_diagnostic() -> None:
    """Run the isolated development bootstrap smoke test.

    Authority: invokes only the public EngineeringKernel bootstrap façade.
    Tenant scope: uses a synthetic diagnostic tenant and principal, never a
    production identity or caller-supplied tenant.
    Mutation and transaction semantics: this diagnostic creates no business
    records, performs no persistence operation, and owns no transaction.
    Idempotency: each invocation is a fresh diagnostic request; no durable
    idempotency or replay guarantee is asserted.
    Fail-closed behavior: unexpected session types, unsuccessful results, and
    bootstrap exceptions cause a non-zero process exit at the CLI boundary.
    Financial boundary: this diagnostic has no payment, provider, settlement,
    invoice, ledger, or other financial execution authority.
    """
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
            "Engineering Kernel diagnostic failed: "
            f"{session.result.get('error', 'unknown error')}"
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


# ARTIFACT: runbook_diagnostic.py
# VERSION: v1.0.0-WILSY-KENNEL-EOS-RUNBOOK-DIAGNOSTIC
# AUTHORITY BOUNDARY: synthetic development bootstrap diagnostic only.
# TENANT POSTURE: explicit synthetic tenant/principal references; no production tenant access.
# FAIL-CLOSED POSTURE: unexpected session or failed bootstrap exits non-zero.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
