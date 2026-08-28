"""Pure preparation boundary from canonical command to PREPARED attempt.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-ISSUANCE
TITLE: Financial Execution Attempt Issuance
PURPOSE: Construct one immutable PREPARED attempt without persistence or transport.
AUTHORITY: Pure value conversion only; caller owns all transaction and lifecycle effects.
EPITOME: Command-derived identity and explicit attempt authority prevent orphaned or fabricated attempts.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/financial_execution_attempt_issuance.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references only; no credentials or provider payloads.
TRANSACTION BOUNDARY: no sessions, transactions, commits, aborts, retries, or I/O.
CHANGELOG: v1.0.0 establishes explicit canonical-command to PREPARED-attempt conversion.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from tools.eos.kennel.domain.financial_execution_command import FinancialExecutionCommand
from tools.eos.kennel.domain.financial_execution_lifecycle import FinancialExecutionAttempt, FinancialExecutionAttemptState

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-ISSUANCE"


@dataclass(frozen=True)
class FinancialExecutionAttemptIssuance:
    """Explicit attempt-only authority; command material is never duplicated."""

    execution_attempt_id: str
    provider_name: str
    created_at: datetime
    destination_fingerprint: str | None = None
    request_evidence_reference: str | None = None


def issue_financial_execution_attempt(
    command: FinancialExecutionCommand,
    issuance: FinancialExecutionAttemptIssuance,
) -> FinancialExecutionAttempt:
    """Construct exactly one PREPARED attempt from a canonical command."""
    if not isinstance(command, FinancialExecutionCommand):
        raise TypeError("command must be FinancialExecutionCommand")
    if not isinstance(issuance, FinancialExecutionAttemptIssuance):
        raise TypeError("issuance must be FinancialExecutionAttemptIssuance")
    if command.provider_name is not None and issuance.provider_name != command.provider_name:
        raise ValueError("attempt provider differs from command provider")
    return FinancialExecutionAttempt(
        execution_attempt_id=issuance.execution_attempt_id,
        tenant_id=command.tenant_id,
        execution_command_id=command.execution_command_id,
        provider_name=issuance.provider_name,
        state=FinancialExecutionAttemptState.PREPARED,
        payment_destination_reference=command.payment_destination_reference,
        request_fingerprint=command.fingerprint,
        destination_fingerprint=issuance.destination_fingerprint,
        request_evidence_reference=issuance.request_evidence_reference,
        created_at=issuance.created_at,
    )


# ARTIFACT: financial_execution_attempt_issuance.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-ISSUANCE
# AUTHORITY BOUNDARY: pure PREPARED attempt construction; no persistence, provider, truth, or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
