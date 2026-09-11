"""WILSY OS legacy generic-command issuance boundary.

TITLE: Financial Execution Command Legacy Issuance Boundary
VERSION: v2.0.0-M11-P5-R2A
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Retire authority-ambiguous caller-driven issuance until typed bridges exist.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/financial_execution_command_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS generic command boundary owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v2.0.0-M11-P5-R2A preserves the public legacy shape while failing closed before command construction or persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No provider, destination, or credential material is transformed.
TENANT BOUNDARY: Legacy issuance performs no persistence or cross-tenant lookup.
AUTHORITY BOUNDARY: Typed AP and Platform Billing bridges own future command issuance.
FINANCIAL AUTHORITY BOUNDARY: No command, provider execution, attempt, truth, settlement, or receivable mutation.
TRANSACTION BOUNDARY: No transaction lifecycle is opened or owned.
FAIL-CLOSED DECLARATION: Legacy caller-driven authority is explicitly rejected with a stable error.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from tools.eos.kennel.domain.financial_execution_command import FinancialExecutionCommand
from tools.eos.saas.domain.vendor_bill_financial_execution_request import VendorBillFinancialExecutionRequest

VERSION = "v2.0.0-M11-P5-R2A"


class FinancialExecutionCommandLegacyIssuanceError(RuntimeError):
    """Stable error for the retired untyped issuance surface."""

    code = "FINANCIAL_EXECUTION_COMMAND_LEGACY_ISSUANCE_DISABLED"

    def __init__(self) -> None:
        super().__init__(self.code)


@dataclass(frozen=True)
class FinancialExecutionCommandIssuance:
    """Preserved legacy value shape; it no longer grants command authority."""

    execution_command_id: str
    idempotency_key: str
    issued_at: datetime
    provider_name: str | None = None
    provider_metadata_reference: str | None = None


def issue_financial_execution_command(
    request: VendorBillFinancialExecutionRequest,
    issuance: FinancialExecutionCommandIssuance,
) -> FinancialExecutionCommand:
    """Reject the retired caller-driven path before construction or side effects."""
    del request, issuance
    raise FinancialExecutionCommandLegacyIssuanceError()


# ARTIFACT: financial_execution_command_issuance.py
# VERSION: v2.0.0-M11-P5-R2A
# AUTHORITY BOUNDARY: retired untyped issuance only; typed bridges own future authority.
# TENANT POSTURE: no lookup, persistence, or tenant disclosure occurs.
# FAIL-CLOSED POSTURE: stable explicit authority error; no command construction.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns later execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
