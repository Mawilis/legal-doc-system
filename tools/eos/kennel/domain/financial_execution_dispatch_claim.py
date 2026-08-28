"""Immutable provider-neutral authority for claiming one prepared attempt.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM
TITLE: Financial Execution Dispatch Claim Domain
PURPOSE: Bind one explicit claimant to one PREPARED attempt and deterministic transport material.
AUTHORITY: Claim/recovery evidence only; no CAS, provider transport, execution truth, or settlement.
EPITOME: Durable identities and fingerprints fence stale workers without treating expiry as resend permission.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution_dispatch_claim.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references and fingerprints only; no credentials or payloads.
TRANSACTION BOUNDARY: pure value object; caller owns persistence and transaction lifecycle.
CHANGELOG: v1.0.0 establishes explicit PREPARED-attempt dispatch claim authority.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from .financial_execution_lifecycle import FinancialExecutionAttemptState

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class FinancialExecutionDispatchClaimError(ValueError):
    """Fail-closed dispatch claim validation error."""


@dataclass(frozen=True)
class FinancialExecutionDispatchClaim:
    """Immutable claimant, fencing version, and transport-material authority."""

    dispatch_claim_id: str
    tenant_id: str
    execution_command_id: str
    execution_attempt_id: str
    expected_attempt_fingerprint: str
    provider_name: str
    claimed_at: datetime
    transport_correlation_id: str
    transport_material_fingerprint: str
    expected_state: FinancialExecutionAttemptState = FinancialExecutionAttemptState.PREPARED
    recovery_posture: str = "RECONCILE_BEFORE_RESEND"

    def __post_init__(self) -> None:
        for name in ("dispatch_claim_id", "tenant_id", "execution_command_id", "execution_attempt_id", "provider_name", "transport_correlation_id", "recovery_posture"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise FinancialExecutionDispatchClaimError(f"{name} is invalid")
        if self.dispatch_claim_id in {self.execution_command_id, self.execution_attempt_id}:
            raise FinancialExecutionDispatchClaimError("claim identity must differ from command and attempt")
        if not isinstance(self.expected_state, FinancialExecutionAttemptState) or self.expected_state is not FinancialExecutionAttemptState.PREPARED:
            raise FinancialExecutionDispatchClaimError("claim expected_state must be PREPARED")
        if not isinstance(self.claimed_at, datetime) or self.claimed_at.tzinfo is None:
            raise FinancialExecutionDispatchClaimError("claimed_at must be timezone-aware")
        for name in ("expected_attempt_fingerprint", "transport_material_fingerprint"):
            if not isinstance(getattr(self, name), str) or _HEX.fullmatch(getattr(self, name)) is None:
                raise FinancialExecutionDispatchClaimError(f"{name} must be lowercase SHA3-512 hex")


# ARTIFACT: financial_execution_dispatch_claim.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM
# AUTHORITY BOUNDARY: pure claim authority; no CAS, provider, truth, or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
