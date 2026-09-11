"""TITLE: Financial Execution Truth Derivation
VERSION: v1.2.0-M11-P5-R2D-R1
AUTHORITY: Kennel EOS / Wilsy OS Core Governance.
EPITOME: Derives execution truth only after exact attempt-to-command lineage correlation and authenticated observation terminalization.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/financial_execution_truth_derivation.py
COLLABORATION / OWNERSHIP: Kennel EOS execution-truth orchestration owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.2.0-M11-P5-R2D-R1 adds subject-neutral execution-fact derivation from canonical command, attempt, and authenticated observation evidence; v1.1.0-M11-P5-R2D-R0-R1 enforces exact durable attempt-to-command tenant, ID, fingerprint, provider, and destination correlation before truth construction.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque provider references; no payloads or credentials.
TENANT BOUNDARY: Attempt, command, observation, and truth reads are tenant-correlated.
AUTHORITY BOUNDARY: Durable command and authenticated observation evidence only; no caller-declared execution truth.
FINANCIAL AUTHORITY BOUNDARY: No provider call, settlement, paid state, or projection.
TRANSACTION BOUNDARY: Caller-owned active session is forwarded to every registry read/write.
FAIL-CLOSED DECLARATION: Missing, divergent, stale, or corrupted lineage rejects before truth construction.
"""
from __future__ import annotations

from datetime import timezone

from pymongo.collection import Collection
from pymongo.client_session import ClientSession

from ..domain.financial_execution import FinancialExecutionFact, FinancialExecutionStatus, FinancialExecutionTruth
from ..domain.financial_execution_command import FinancialExecutionCommand
from ..domain.financial_execution_execution_time_evidence import FinancialExecutionTimeEvidence
from ..domain.financial_execution_terminalization import TerminalizationDecision, evaluate_terminalization
from ..registry.financial_execution_attempt_registry import FinancialExecutionAttemptRegistry
from ..registry.financial_execution_command_registry import FinancialExecutionCommandRegistry
from ..registry.financial_execution_provider_observation_registry import FinancialExecutionProviderObservationRegistry
from ..registry.financial_execution_registry import FinancialExecutionCreateResult, FinancialExecutionTruthRegistry, FinancialExecutionFactCreateResult, FinancialExecutionFactRegistry

VERSION = "v1.2.0-M11-P5-R2D-R1"


class FinancialExecutionTruthDerivationError(RuntimeError):
    """Fail-closed derivation error."""


def _correlate_attempt_to_command(attempt: object, command: FinancialExecutionCommand) -> None:
    """Require every command-projected attempt field to match durable command material."""
    if (
        getattr(attempt, "tenant_id", None) != command.tenant_id
        or getattr(attempt, "execution_command_id", None) != command.execution_command_id
        or getattr(attempt, "request_fingerprint", None) != command.fingerprint
        or getattr(attempt, "provider_name", None) != command.provider_name
        or getattr(attempt, "payment_destination_reference", None) != command.payment_destination_reference
    ):
        raise FinancialExecutionTruthDerivationError(
            "ATTEMPT_CANONICAL_COMMAND_LINEAGE_MISMATCH"
        )


def derive_financial_execution_truth(
    tenant_id: str,
    execution_attempt_id: str,
    *,
    command_collection: Collection,
    attempt_collection: Collection,
    observation_collection: Collection,
    truth_collection: Collection,
    execution_time_evidence: FinancialExecutionTimeEvidence,
    session: ClientSession,
) -> FinancialExecutionCreateResult:
    """Derive and persist AP execution truth from exact lineage and observation evidence.

    Platform commands are lineage-validated without accessing the AP-only
    ``payable_id`` projection; Platform subject truth remains a later gate.
    """
    if session is None or not bool(getattr(session, "in_transaction", False)):
        raise FinancialExecutionTruthDerivationError("M11E2D2_ACTIVE_SESSION_REQUIRED")
    attempt = FinancialExecutionAttemptRegistry.get(
        tenant_id, execution_attempt_id, attempt_collection, session=session
    )
    command = FinancialExecutionCommandRegistry.get(
        tenant_id, attempt.execution_command_id, command_collection, session=session
    )
    if not isinstance(command, FinancialExecutionCommand):
        raise FinancialExecutionTruthDerivationError("M11E2D2_COMMAND_INVALID")
    _correlate_attempt_to_command(attempt, command)
    observations = FinancialExecutionProviderObservationRegistry.list_for_attempt(
        tenant_id, execution_attempt_id, collection=observation_collection, session=session
    )
    if not isinstance(execution_time_evidence, FinancialExecutionTimeEvidence):
        raise FinancialExecutionTruthDerivationError("M11E2D2_EXECUTION_TIME_INVALID")
    decision = evaluate_terminalization(attempt, observations, execution_time_evidence)
    if decision.decision not in {
        TerminalizationDecision.ELIGIBLE_EXECUTED,
        TerminalizationDecision.ELIGIBLE_FAILED,
    }:
        raise FinancialExecutionTruthDerivationError("M11E2D2_TERMINALIZATION_NOT_ELIGIBLE")
    selected = [
        item
        for item in observations
        if item.provider_execution_reference == execution_time_evidence.provider_execution_reference
    ]
    if len(selected) != 1 or selected[0].provider_name != command.provider_name:
        raise FinancialExecutionTruthDerivationError("M11E2D2_PROVIDER_CORRELATION_MISMATCH")
    if command.source_authority_kind.value == "PLATFORM_BILLING":
        raise FinancialExecutionTruthDerivationError("PLATFORM_TRUTH_SUBJECT_UNSUPPORTED")
    item = selected[0]
    status = (
        FinancialExecutionStatus.EXECUTED
        if decision.decision is TerminalizationDecision.ELIGIBLE_EXECUTED
        else FinancialExecutionStatus.FAILED
    )
    created_at = command.created_at.astimezone(timezone.utc)
    truth = FinancialExecutionTruth(
        command.execution_command_id,
        command.tenant_id,
        command.payable_id,
        command.release_authorization_id,
        item.provider_name,
        item.provider_execution_reference or "",
        status,
        command.amount_minor,
        command.currency,
        decision.executed_at if status is FinancialExecutionStatus.EXECUTED else None,
        command.payment_destination_reference,
        item.provider_evidence_reference or item.observation_id,
        command.fingerprint,
        decision.fingerprint,
        created_at,
    )
    return FinancialExecutionTruthRegistry.create(
        truth, command.idempotency_key, truth_collection, session=session
    )


def derive_financial_execution_fact(
    tenant_id: str,
    execution_attempt_id: str,
    *,
    command_collection: Collection,
    attempt_collection: Collection,
    observation_collection: Collection,
    fact_collection: Collection,
    execution_time_evidence: FinancialExecutionTimeEvidence,
    session: ClientSession,
) -> FinancialExecutionFactCreateResult:
    """Derive one subject-neutral execution fact from exact command/attempt evidence.

    The neutral path deliberately does not inspect payable, platform-invoice, or
    receivable fields.  A later family-specific bridge may project this fact.
    """
    if session is None or not bool(getattr(session, "in_transaction", False)):
        raise FinancialExecutionTruthDerivationError("M11E2D2_ACTIVE_SESSION_REQUIRED")
    attempt = FinancialExecutionAttemptRegistry.get(tenant_id, execution_attempt_id, attempt_collection, session=session)
    command = FinancialExecutionCommandRegistry.get(tenant_id, attempt.execution_command_id, command_collection, session=session)
    if not isinstance(command, FinancialExecutionCommand):
        raise FinancialExecutionTruthDerivationError("M11E2D2_COMMAND_INVALID")
    _correlate_attempt_to_command(attempt, command)
    observations = FinancialExecutionProviderObservationRegistry.list_for_attempt(tenant_id, execution_attempt_id, collection=observation_collection, session=session)
    if not isinstance(execution_time_evidence, FinancialExecutionTimeEvidence):
        raise FinancialExecutionTruthDerivationError("M11E2D2_EXECUTION_TIME_INVALID")
    decision = evaluate_terminalization(attempt, observations, execution_time_evidence)
    if decision.decision not in {TerminalizationDecision.ELIGIBLE_EXECUTED, TerminalizationDecision.ELIGIBLE_FAILED}:
        raise FinancialExecutionTruthDerivationError("M11E2D2_TERMINALIZATION_NOT_ELIGIBLE")
    selected = [item for item in observations if item.provider_execution_reference == execution_time_evidence.provider_execution_reference]
    if len(selected) != 1 or selected[0].provider_name != command.provider_name:
        raise FinancialExecutionTruthDerivationError("M11E2D2_PROVIDER_CORRELATION_MISMATCH")
    item = selected[0]
    status = FinancialExecutionStatus.EXECUTED if decision.decision is TerminalizationDecision.ELIGIBLE_EXECUTED else FinancialExecutionStatus.FAILED
    fact = FinancialExecutionFact(
        execution_fact_id=FinancialExecutionFact.deterministic_id(command.tenant_id, execution_attempt_id),
        tenant_id=command.tenant_id,
        execution_command_id=command.execution_command_id,
        execution_command_fingerprint=command.fingerprint,
        execution_attempt_id=execution_attempt_id,
        provider=item.provider_name,
        provider_execution_reference=item.provider_execution_reference or "",
        execution_status=status,
        executed_amount_minor=command.amount_minor,
        currency=command.currency,
        executed_at=decision.executed_at if status is FinancialExecutionStatus.EXECUTED else None,
        payment_destination_reference=command.payment_destination_reference,
        provider_evidence_reference=item.provider_evidence_reference or item.observation_id,
        execution_evidence_fingerprint=decision.fingerprint,
        created_at=command.created_at.astimezone(timezone.utc),
    )
    return FinancialExecutionFactRegistry.create(fact, fact_collection, session=session)


# ARTIFACT: financial_execution_truth_derivation.py
# VERSION: v1.2.0-M11-P5-R2D-R1
# AUTHORITY BOUNDARY: exact command-lineage and observation-gated execution truth only; no settlement.
# TENANT POSTURE: durable tenant-correlated evidence and caller-owned transaction.
# FAIL-CLOSED POSTURE: projected-field divergence and unsupported Platform subjects reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
