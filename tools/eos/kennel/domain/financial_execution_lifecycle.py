"""Provider-neutral asynchronous financial execution attempt lifecycle.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-LIFECYCLE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, tenant-scoped attempt evidence distinct from final execution truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution_lifecycle.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
CERTIFICATION DATE: 2026-08-28
CHANGELOG: v1.0.0 establishes provider-neutral asynchronous states, deterministic transitions, reconciliation and finalization gates.
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
SECURITY / PRIVACY: opaque references only; raw payloads and credentials are forbidden.
TENANT BOUNDARY: tenant_id and execution_command_id are mandatory and immutable.
AUTHORITY BOUNDARY: this contract records attempt evidence; Kennel EOS owns execution truth.
FINANCIAL AUTHORITY BOUNDARY: execution is not settlement; no persistence, network, payment, or settlement behavior.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-LIFECYCLE"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class FinancialExecutionLifecycleError(ValueError):
    """Fail-closed lifecycle validation or transition error."""


class FinancialExecutionAttemptState(StrEnum):
    """Operational attempt states; no state represents settlement."""

    PREPARED = "PREPARED"
    TRANSMISSION_STARTED = "TRANSMISSION_STARTED"
    TRANSMITTED = "TRANSMITTED"
    ACCEPTED = "ACCEPTED"
    PENDING = "PENDING"
    AMBIGUOUS = "AMBIGUOUS"
    CONFIRMED_EXECUTED = "CONFIRMED_EXECUTED"
    CONFIRMED_FAILED = "CONFIRMED_FAILED"
    CANCELLED = "CANCELLED"


class ExecutionReconciliationOutcome(StrEnum):
    """Provider-neutral conclusions consumed by the finalization gate."""

    CONFIRMED_EXECUTED = "CONFIRMED_EXECUTED"
    CONFIRMED_FAILED = "CONFIRMED_FAILED"
    STILL_PENDING = "STILL_PENDING"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class ExecutionReconciliationDecision:
    """Immutable safe reconciliation conclusion and evidence reference."""

    outcome: ExecutionReconciliationOutcome
    evidence_reference: str
    confirmed_at: datetime | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, ExecutionReconciliationOutcome) or not isinstance(self.evidence_reference, str) or not self.evidence_reference.strip():
            raise FinancialExecutionLifecycleError("invalid reconciliation decision")
        if self.confirmed_at is not None and (not isinstance(self.confirmed_at, datetime) or self.confirmed_at.tzinfo is None):
            raise FinancialExecutionLifecycleError("confirmed_at must be timezone-aware")
        if not isinstance(self.reason, str):
            raise FinancialExecutionLifecycleError("reason must be text")


@dataclass(frozen=True)
class FinancialExecutionAttempt:
    """Immutable attempt identity, lifecycle state, safe evidence, and timestamps."""

    execution_attempt_id: str
    tenant_id: str
    execution_command_id: str
    provider_name: str
    state: FinancialExecutionAttemptState = FinancialExecutionAttemptState.PREPARED
    payment_destination_reference: str | None = None
    provider_request_reference: str | None = None
    request_fingerprint: str | None = None
    destination_fingerprint: str | None = None
    request_evidence_reference: str | None = None
    response_evidence_reference: str | None = None
    latest_provider_evidence_reference: str | None = None
    reconciliation_evidence_reference: str | None = None
    created_at: datetime | None = None
    transmission_started_at: datetime | None = None
    transmitted_at: datetime | None = None
    provider_accepted_at: datetime | None = None
    confirmed_at: datetime | None = None

    def __post_init__(self) -> None:
        for name in ("execution_attempt_id", "tenant_id", "execution_command_id", "provider_name"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise FinancialExecutionLifecycleError(f"{name} must be non-empty")
        if self.execution_attempt_id == self.execution_command_id:
            raise FinancialExecutionLifecycleError("attempt and command identities must differ")
        if not isinstance(self.state, FinancialExecutionAttemptState):
            raise FinancialExecutionLifecycleError("state is invalid")
        for name in ("payment_destination_reference", "provider_request_reference", "request_evidence_reference", "response_evidence_reference", "latest_provider_evidence_reference", "reconciliation_evidence_reference"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise FinancialExecutionLifecycleError(f"{name} must be an opaque reference")
        for name in ("created_at", "transmission_started_at", "transmitted_at", "provider_accepted_at", "confirmed_at"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, datetime) or value.tzinfo is None):
                raise FinancialExecutionLifecycleError(f"{name} must be timezone-aware")
        for name in ("request_fingerprint", "destination_fingerprint"):
            value = getattr(self, name)
            if value is not None and _HEX.fullmatch(value) is None:
                raise FinancialExecutionLifecycleError(f"{name} must be lowercase SHA3-512 hex")
        if self.state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED and self.confirmed_at is None:
            raise FinancialExecutionLifecycleError("confirmed execution requires confirmed_at")

    @property
    def is_final(self) -> bool:
        """Whether the attempt has reached a terminal evidence state."""
        return self.state in {FinancialExecutionAttemptState.CONFIRMED_EXECUTED, FinancialExecutionAttemptState.CONFIRMED_FAILED, FinancialExecutionAttemptState.CANCELLED}

    @property
    def may_retry(self) -> bool:
        """Return conservative retry eligibility; ambiguous delivery is never blindly retried."""
        return self.state in {FinancialExecutionAttemptState.PREPARED, FinancialExecutionAttemptState.CONFIRMED_FAILED}

    def transition_to(self, state: FinancialExecutionAttemptState, *, evidence_reference: str | None = None, confirmed_at: datetime | None = None) -> "FinancialExecutionAttempt":
        """Apply one permitted monotonic transition, rejecting reversal and missing evidence."""
        if not isinstance(state, FinancialExecutionAttemptState):
            raise FinancialExecutionLifecycleError("state is invalid")
        if state is self.state:
            if evidence_reference is None or evidence_reference == self.latest_provider_evidence_reference:
                return self
            raise FinancialExecutionLifecycleError("divergent same-state replay")
        allowed = {
            FinancialExecutionAttemptState.PREPARED: {FinancialExecutionAttemptState.TRANSMISSION_STARTED, FinancialExecutionAttemptState.TRANSMITTED, FinancialExecutionAttemptState.AMBIGUOUS, FinancialExecutionAttemptState.CONFIRMED_FAILED},
            FinancialExecutionAttemptState.TRANSMISSION_STARTED: {FinancialExecutionAttemptState.TRANSMITTED, FinancialExecutionAttemptState.AMBIGUOUS, FinancialExecutionAttemptState.CONFIRMED_FAILED},
            FinancialExecutionAttemptState.TRANSMITTED: {FinancialExecutionAttemptState.ACCEPTED, FinancialExecutionAttemptState.PENDING, FinancialExecutionAttemptState.AMBIGUOUS, FinancialExecutionAttemptState.CONFIRMED_EXECUTED, FinancialExecutionAttemptState.CONFIRMED_FAILED},
            FinancialExecutionAttemptState.ACCEPTED: {FinancialExecutionAttemptState.PENDING, FinancialExecutionAttemptState.AMBIGUOUS, FinancialExecutionAttemptState.CONFIRMED_EXECUTED, FinancialExecutionAttemptState.CONFIRMED_FAILED},
            FinancialExecutionAttemptState.PENDING: {FinancialExecutionAttemptState.CONFIRMED_EXECUTED, FinancialExecutionAttemptState.CONFIRMED_FAILED, FinancialExecutionAttemptState.AMBIGUOUS},
            FinancialExecutionAttemptState.AMBIGUOUS: {FinancialExecutionAttemptState.CONFIRMED_EXECUTED, FinancialExecutionAttemptState.CONFIRMED_FAILED},
        }
        if state not in allowed.get(self.state, set()):
            raise FinancialExecutionLifecycleError("illegal lifecycle transition")
        if state in {FinancialExecutionAttemptState.CONFIRMED_EXECUTED, FinancialExecutionAttemptState.CONFIRMED_FAILED} and (not evidence_reference or not evidence_reference.strip()):
            raise FinancialExecutionLifecycleError("final state requires reconciliation evidence")
        if state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED and confirmed_at is None:
            raise FinancialExecutionLifecycleError("confirmed execution requires timestamp")
        return FinancialExecutionAttempt(**{**self.__dict__, "state": state, "latest_provider_evidence_reference": evidence_reference or self.latest_provider_evidence_reference, "reconciliation_evidence_reference": evidence_reference or self.reconciliation_evidence_reference, "confirmed_at": confirmed_at or self.confirmed_at})

    def finalize(self, decision: ExecutionReconciliationDecision) -> "FinancialExecutionFinalization":
        """Gate emission of final execution truth; conflicts and non-final outcomes cannot pass."""
        if not isinstance(decision, ExecutionReconciliationDecision) or decision.outcome in {ExecutionReconciliationOutcome.UNKNOWN, ExecutionReconciliationOutcome.STILL_PENDING, ExecutionReconciliationOutcome.CONFLICT}:
            raise FinancialExecutionLifecycleError("reconciliation does not permit finalization")
        if decision.outcome is ExecutionReconciliationOutcome.CONFIRMED_EXECUTED and decision.confirmed_at is None:
            raise FinancialExecutionLifecycleError("executed finalization requires reliable timestamp")
        return FinancialExecutionFinalization(self.execution_attempt_id, self.tenant_id, self.execution_command_id, self.provider_name, decision.outcome, decision.evidence_reference, decision.confirmed_at)

    def to_dict(self) -> dict[str, object]:
        """Serialize safe lifecycle evidence deterministically; no payloads or settlement fields."""
        return {k: (v.value if isinstance(v, StrEnum) else v.isoformat() if isinstance(v, datetime) else v) for k, v in self.__dict__.items()}

    @property
    def fingerprint(self) -> str:
        """Return canonical SHA3-512 attempt evidence fingerprint."""
        return hashlib.sha3_512(json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FinancialExecutionFinalization:
    """Pure finalization decision; persistence into FinancialExecutionTruth is separate."""

    execution_attempt_id: str
    tenant_id: str
    execution_command_id: str
    provider_name: str
    outcome: ExecutionReconciliationOutcome
    evidence_reference: str
    confirmed_at: datetime | None

    def __post_init__(self) -> None:
        if self.outcome not in {ExecutionReconciliationOutcome.CONFIRMED_EXECUTED, ExecutionReconciliationOutcome.CONFIRMED_FAILED}:
            raise FinancialExecutionLifecycleError("finalization outcome is not final")
        if not isinstance(self.evidence_reference, str) or not self.evidence_reference.strip():
            raise FinancialExecutionLifecycleError("finalization evidence is required")
        if self.outcome is ExecutionReconciliationOutcome.CONFIRMED_EXECUTED and (not isinstance(self.confirmed_at, datetime) or self.confirmed_at.tzinfo is None):
            raise FinancialExecutionLifecycleError("executed finalization timestamp is required")


# ARTIFACT: financial_execution_lifecycle.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-LIFECYCLE
# AUTHORITY BOUNDARY: attempt evidence is distinct from Kennel execution truth and settlement.
# TENANT POSTURE: immutable tenant and command identity; no cross-tenant inference.
# FAIL-CLOSED POSTURE: illegal transitions, conflicts, and ambiguous outcomes cannot finalize.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth; execution is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
