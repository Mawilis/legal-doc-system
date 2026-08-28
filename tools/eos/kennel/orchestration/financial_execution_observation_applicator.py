# -*- coding: utf-8 -*-
"""Wilsy OS caller-owned provider-observation application authority.

VERSION: v1.0.0-KENNEL-FINANCIAL-OBSERVATION-APPLICATOR
AUTHORITY: atomically coordinates observation persistence and attempt CAS only.
EPITOME: One active caller transaction binds immutable evidence to lifecycle state.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/financial_execution_observation_applicator.py
COLLABORATION: Wilson Khanyezi (Founder); Codex (AI Engineering)
DATE: 2026-08-28 | COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque evidence references only; no provider payloads or credentials.
TENANT / TRANSACTION / TRUTH BOUNDARY: exact tenant binding; caller owns session; no truth or settlement.
CHANGELOG: v1.0.0 establishes insert-first observation and bounded lifecycle CAS application.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, cast
from pymongo.client_session import ClientSession
from ..domain.financial_execution_lifecycle import FinancialExecutionAttempt, FinancialExecutionAttemptState
from ..domain.financial_execution_observation_policy import FinancialExecutionObservationDecision, ObservationPolicyAction, evaluate_provider_observation
from ..domain.financial_execution_provider_observation import FinancialExecutionProviderObservation
from ..registry.financial_execution_attempt_registry import FinancialExecutionAttemptRegistry, FinancialExecutionAttemptTransitionConflictError
from ..registry.financial_execution_provider_observation_registry import FinancialExecutionProviderObservationRegistry

VERSION = "v1.0.0-KENNEL-FINANCIAL-OBSERVATION-APPLICATOR"
class ObservationApplicationOutcome(StrEnum):
    OBSERVATION_CREATED = "OBSERVATION_CREATED"
    OBSERVATION_REPLAYED = "OBSERVATION_REPLAYED"
    ATTEMPT_ADVANCED = "ATTEMPT_ADVANCED"
    ATTEMPT_ALREADY_SATISFIED = "ATTEMPT_ALREADY_SATISFIED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"
    CONFLICT = "CONFLICT"
    REJECTED = "REJECTED"
    CAS_CONFLICT = "CAS_CONFLICT"

@dataclass(frozen=True)
class ObservationApplicationResult:
    """Immutable application result; it never implies execution truth or settlement."""
    outcome: ObservationApplicationOutcome
    attempt: FinancialExecutionAttempt
    decision: FinancialExecutionObservationDecision

class FinancialExecutionObservationApplicator:
    """Applies evidence inside a transaction owned entirely by the caller."""
    @staticmethod
    def apply(tenant_id: str, observation: FinancialExecutionProviderObservation, session: ClientSession, *, observation_collection=None, attempt_collection=None) -> ObservationApplicationResult:
        active = bool(cast(Any, session).in_transaction) if session is not None else False
        if not active:
            raise RuntimeError("FINANCIAL_EXECUTION_OBSERVATION_APPLICATOR_REQUIRES_ACTIVE_TRANSACTION")
        if observation.tenant_id != str(tenant_id).strip():
            raise ValueError("FINANCIAL_EXECUTION_OBSERVATION_TENANT_MISMATCH")
        created, _ = FinancialExecutionProviderObservationRegistry.create(observation, observation_collection, session=session)
        attempt = FinancialExecutionAttemptRegistry.get(tenant_id, observation.execution_attempt_id, attempt_collection, session=session)
        decision = evaluate_provider_observation(attempt, observation)
        outcome = ObservationApplicationOutcome.OBSERVATION_CREATED if created == "CREATED" else ObservationApplicationOutcome.OBSERVATION_REPLAYED
        if decision.action is ObservationPolicyAction.ADVANCE:
            target = attempt.transition_to(decision.proposed_state, evidence_reference=observation.provider_evidence_reference, confirmed_at=observation.provider_occurred_at if decision.proposed_state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED else None)
            try:
                persisted = FinancialExecutionAttemptRegistry.transition(tenant_id, attempt.execution_attempt_id, attempt.state, attempt.fingerprint, target, attempt_collection, session=session)
            except FinancialExecutionAttemptTransitionConflictError:
                return ObservationApplicationResult(ObservationApplicationOutcome.CAS_CONFLICT, attempt, decision)
            return ObservationApplicationResult(ObservationApplicationOutcome.ATTEMPT_ADVANCED, persisted, decision)
        mapping = {ObservationPolicyAction.NO_OP: ObservationApplicationOutcome.ATTEMPT_ALREADY_SATISFIED, ObservationPolicyAction.RECONCILIATION_REQUIRED: ObservationApplicationOutcome.RECONCILIATION_REQUIRED, ObservationPolicyAction.CONFLICT: ObservationApplicationOutcome.CONFLICT, ObservationPolicyAction.REJECT: ObservationApplicationOutcome.REJECTED, ObservationPolicyAction.AMBIGUOUS: ObservationApplicationOutcome.RECONCILIATION_REQUIRED}
        return ObservationApplicationResult(mapping[decision.action] if outcome == ObservationApplicationOutcome.OBSERVATION_REPLAYED else mapping.get(decision.action, outcome), attempt, decision)

# ARTIFACT: financial_execution_observation_applicator.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-OBSERVATION-APPLICATOR
# AUTHORITY BOUNDARY: caller-owned transaction only; no truth, settlement, or provider transport.
# END OF WILSY OS SOVEREIGN ARTIFACT
