"""Canonical pure issuance boundary from AP request to Kennel command.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-COMMAND-ISSUANCE
TITLE: Financial Execution Command Issuance Adapter
PURPOSE: Convert an authoritative AP execution request into one canonical durable command.
AUTHORITY: Pure value conversion only; no persistence, attempts, providers, truth, or settlement.
EPITOME: Explicit issuance material prevents hidden identity or clock generation.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/financial_execution_command_issuance.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque destination and metadata references only; credentials are forbidden.
TRANSACTION BOUNDARY: pure conversion; caller owns all persistence and transaction lifecycle.
CHANGELOG: v1.0.0 establishes explicit request-to-canonical-command issuance authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from tools.eos.kennel.domain.financial_execution_command import FinancialExecutionCommand
from tools.eos.saas.domain.vendor_bill_financial_execution_request import VendorBillFinancialExecutionRequest

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-COMMAND-ISSUANCE"


@dataclass(frozen=True)
class FinancialExecutionCommandIssuance:
    """Explicit caller-supplied authority for immutable command issuance."""

    execution_command_id: str
    idempotency_key: str
    issued_at: datetime
    provider_name: str | None = None
    provider_metadata_reference: str | None = None


def issue_financial_execution_command(
    request: VendorBillFinancialExecutionRequest,
    issuance: FinancialExecutionCommandIssuance,
) -> FinancialExecutionCommand:
    """Convert one AP request and explicit issuance authority to the canonical command."""
    if not isinstance(request, VendorBillFinancialExecutionRequest):
        raise TypeError("request must be VendorBillFinancialExecutionRequest")
    if not isinstance(issuance, FinancialExecutionCommandIssuance):
        raise TypeError("issuance must be FinancialExecutionCommandIssuance")
    return FinancialExecutionCommand(
        tenant_id=request.tenant_id,
        payable_id=request.payable_id,
        release_authorization_id=request.release_authorization_id,
        execution_command_id=issuance.execution_command_id,
        idempotency_key=issuance.idempotency_key,
        amount_minor=request.amount_minor,
        currency=request.currency,
        payment_destination_reference=request.payment_destination_reference,
        created_at=issuance.issued_at,
        provider_name=issuance.provider_name,
        provider_metadata_reference=issuance.provider_metadata_reference,
    )


# ARTIFACT: financial_execution_command_issuance.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-COMMAND-ISSUANCE
# AUTHORITY BOUNDARY: pure AP request conversion; no persistence, attempt, provider, truth, or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
