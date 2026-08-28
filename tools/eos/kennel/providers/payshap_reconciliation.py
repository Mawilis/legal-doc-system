# -*- coding: utf-8 -*-
"""Pure PayShap ambiguous-outcome reconciliation contract.

VERSION: v1.0.0-KENNEL-PAYSHAP-AMBIGUOUS-OUTCOME-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministic execution-evidence classification; no HTTP, persistence, or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/providers/payshap_reconciliation.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
CERTIFICATION DATE: 2026-08-28
CHANGELOG: v1.0.0 defines immutable context/observations, fail-closed ambiguous-outcome classification, and retry/operator-review boundaries.
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
SECURITY / PRIVACY: only opaque references and fingerprints are accepted; raw payloads and credentials are forbidden.
TENANT BOUNDARY: every observation is correlated to the context tenant and execution command.
AUTHORITY BOUNDARY: this module classifies provider evidence only; Kennel EOS owns execution truth.
FINANCIAL AUTHORITY BOUNDARY: reconciliation never authorizes settlement, payment, invoice, or ledger mutation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Iterable

from .payshap_contract import PayShapStatus

VERSION = "v1.0.0-KENNEL-PAYSHAP-AMBIGUOUS-OUTCOME-RECONCILIATION"


class PayShapReconciliationError(ValueError):
    """Raised when reconciliation input violates the tenant/evidence boundary."""


class PayShapObservationSource(StrEnum):
    """Supported observation channels, none of which is settlement truth."""

    INITIATION_RESPONSE = "INITIATION_RESPONSE"
    POLLING_RESPONSE = "POLLING_RESPONSE"
    WEBHOOK_EVIDENCE = "WEBHOOK_EVIDENCE"
    PROVIDER_QUERY_RESULT = "PROVIDER_QUERY_RESULT"
    DURABLE_EXISTING_EVIDENCE = "DURABLE_EXISTING_EVIDENCE"


class PayShapReconciliationOutcome(StrEnum):
    """Execution-evidence outcomes; settlement and paid states are excluded."""

    UNKNOWN = "UNKNOWN"
    CONFIRMED_FAILED = "CONFIRMED_FAILED"
    CONFIRMED_EXECUTED = "CONFIRMED_EXECUTED"
    STILL_PENDING = "STILL_PENDING"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class PayShapReconciliationContext:
    """Immutable tenant-scoped identity against which observations are checked."""

    tenant_id: str
    execution_command_id: str
    provider_reference: str
    destination_reference: str
    request_fingerprint: str
    known_evidence_references: tuple[str, ...] = ()
    reconciliation_requested_at: datetime | None = None

    def __post_init__(self) -> None:
        for name in ("tenant_id", "execution_command_id", "provider_reference", "destination_reference", "request_fingerprint"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise PayShapReconciliationError(f"{name} must be non-empty")
        if not isinstance(self.known_evidence_references, tuple) or any(not isinstance(v, str) or not v.strip() for v in self.known_evidence_references):
            raise PayShapReconciliationError("known_evidence_references must contain opaque references")
        if self.reconciliation_requested_at is not None and (not isinstance(self.reconciliation_requested_at, datetime) or self.reconciliation_requested_at.tzinfo is None):
            raise PayShapReconciliationError("reconciliation_requested_at must be timezone-aware")


@dataclass(frozen=True)
class PayShapProviderObservation:
    """Immutable safe metadata observation; raw provider payload is not a field."""

    source: PayShapObservationSource
    tenant_id: str
    execution_command_id: str | None
    provider_reference: str
    provider_status: PayShapStatus
    provider_timestamp: datetime | None
    observed_at: datetime
    evidence_reference: str | None = None
    payload_fingerprint: str | None = None
    authenticated: bool = False
    amount_minor: int | None = None
    currency: str | None = None

    def __post_init__(self) -> None:
        for name in ("tenant_id", "provider_reference"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise PayShapReconciliationError(f"{name} must be non-empty")
        if not isinstance(self.source, PayShapObservationSource) or not isinstance(self.provider_status, PayShapStatus):
            raise PayShapReconciliationError("observation vocabulary is invalid")
        for name in ("observed_at", "provider_timestamp"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, datetime) or value.tzinfo is None):
                raise PayShapReconciliationError(f"{name} must be timezone-aware")
        if not isinstance(self.authenticated, bool):
            raise PayShapReconciliationError("authenticated must be boolean")
        if self.amount_minor is not None and (not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool) or self.amount_minor <= 0):
            raise PayShapReconciliationError("amount_minor must be positive")
        if self.currency is not None and (not isinstance(self.currency, str) or len(self.currency) != 3 or self.currency != self.currency.upper() or not self.currency.isalpha()):
            raise PayShapReconciliationError("currency must be uppercase 3-letter code")
        if self.source is not PayShapObservationSource.INITIATION_RESPONSE and (not isinstance(self.evidence_reference, str) or not self.evidence_reference.strip()):
            raise PayShapReconciliationError("durable observation requires evidence_reference")


@dataclass(frozen=True)
class PayShapReconciliationResult:
    """Immutable classification with explicit retry and operator-review semantics."""

    outcome: PayShapReconciliationOutcome
    reason: str
    may_retry: bool
    requires_operator_review: bool
    evidence_references: tuple[str, ...]


def reconcile(context: PayShapReconciliationContext, observations: Iterable[PayShapProviderObservation]) -> PayShapReconciliationResult:
    """Classify correlated observations without mutating execution or settlement truth."""
    if not isinstance(context, PayShapReconciliationContext):
        raise PayShapReconciliationError("context is invalid")
    items = tuple(observations)
    if any(not isinstance(item, PayShapProviderObservation) for item in items):
        raise PayShapReconciliationError("observations are invalid")
    refs = tuple(item.evidence_reference for item in items if item.evidence_reference is not None)
    for item in items:
        if item.tenant_id != context.tenant_id or item.provider_reference != context.provider_reference or (item.execution_command_id is not None and item.execution_command_id != context.execution_command_id):
            return PayShapReconciliationResult(PayShapReconciliationOutcome.CONFLICT, "IDENTITY_MISMATCH", False, True, refs)
        if item.amount_minor is not None or item.currency is not None:
            if item.amount_minor is None or item.currency is None:
                return PayShapReconciliationResult(PayShapReconciliationOutcome.CONFLICT, "AMOUNT_CURRENCY_INCOMPLETE", False, True, refs)
    if not items:
        return PayShapReconciliationResult(PayShapReconciliationOutcome.UNKNOWN, "NO_EVIDENCE", False, True, ())
    statuses = {item.provider_status for item in items}
    if PayShapStatus.EXECUTED in statuses and (PayShapStatus.FAILED in statuses or PayShapStatus.CANCELLED in statuses):
        return PayShapReconciliationResult(PayShapReconciliationOutcome.CONFLICT, "CONFLICTING_EXECUTION_EVIDENCE", False, True, refs)
    executed = [item for item in items if item.provider_status is PayShapStatus.EXECUTED]
    if executed:
        if all(item.authenticated and item.evidence_reference and item.provider_timestamp is not None for item in executed):
            return PayShapReconciliationResult(PayShapReconciliationOutcome.CONFIRMED_EXECUTED, "AUTHENTICATED_EXECUTION_EVIDENCE", False, False, refs)
        return PayShapReconciliationResult(PayShapReconciliationOutcome.UNKNOWN, "INSUFFICIENT_EXECUTION_EVIDENCE", False, True, refs)
    if statuses.intersection({PayShapStatus.FAILED, PayShapStatus.CANCELLED}) and all(item.authenticated and item.evidence_reference for item in items):
        return PayShapReconciliationResult(PayShapReconciliationOutcome.CONFIRMED_FAILED, "AUTHENTICATED_PROVIDER_FAILURE", True, False, refs)
    if statuses.intersection({PayShapStatus.PENDING, PayShapStatus.REQUESTED, PayShapStatus.INITIATED, PayShapStatus.ACCEPTED}):
        return PayShapReconciliationResult(PayShapReconciliationOutcome.STILL_PENDING, "NON_FINAL_PROVIDER_STATUS", False, False, refs)
    return PayShapReconciliationResult(PayShapReconciliationOutcome.UNKNOWN, "UNRESOLVED_PROVIDER_STATUS", False, True, refs)


# ARTIFACT: payshap_reconciliation.py
# VERSION: v1.0.0-KENNEL-PAYSHAP-AMBIGUOUS-OUTCOME-RECONCILIATION
# AUTHORITY BOUNDARY: evidence classification only; no provider initiation, persistence, execution, or settlement.
# TENANT POSTURE: every observation is tenant and provider-reference correlated.
# FAIL-CLOSED POSTURE: ambiguous, unauthenticated, or conflicting evidence cannot authorize blind retry.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth; reconciliation is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
