"""Direct certificate for terminal service/non-service outcome development.

TITLE: Wilsy OS Process-Service Attempt Outcome Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: P5E terminal outcome, ServiceExecution derivation, and P2 composition.
TENANT BOUNDARY: Every persistence operation is explicitly tenant-scoped.
AUTHORITY BOUNDARY: ATTEMPTED -> terminal only; ReturnOfService is excluded.
FINANCIAL BOUNDARY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Naked outcome claims, malformed evidence, divergence, and inactive
              transactions reject.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-CERT certifies
           completed/non-completed paths, replay, provenance, and boundaries.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState, ServiceExecution, ServiceExecutionOutcome
from tools.eos.legal_operations.domain.process_service_attempt_outcome_authority import ProcessServiceAttemptOutcomeAuthorityError, authorize_process_service_attempt_outcome
from tools.eos.legal_operations.orchestration.process_service_attempt_outcome_orchestrator import ProcessServiceAttemptOutcomeOrchestratorError, transition_process_service_attempt_outcome
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_attempt_outcome_registry import ProcessServiceAttemptOutcomeRegistry, ProcessServiceAttemptOutcomeRegistryError

BASE = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
FINGERPRINT = "c" * 128


class Session:
    in_transaction = True


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.sessions: list[object] = []

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"key": keys, "unique": unique, "name": name})
        return name

    def find_one(self, query: dict[str, Any], *, session: object = None) -> dict[str, Any] | None:
        self.sessions.append(session)
        return next((dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, row: dict[str, Any], *, session: object = None) -> object:
        self.sessions.append(session)
        for index in self.indexes:
            if index["unique"]:
                keys = tuple(k for k, _direction in index["key"])
                if any(all(existing.get(k) == row.get(k) for k in keys) for existing in self.rows):
                    raise DuplicateKeyError("duplicate")
        self.rows.append(dict(row))
        return object()


def source() -> ServiceAttempt:
    return ServiceAttempt(tenant_id="TENANT_A", attempt_id="attempt-outcome", instruction_id="instruction-outcome", document_id="document-outcome", deputy_id="deputy-outcome", allocated_at=BASE, allocation_evidence_reference="p5b:allocation")


def attempted() -> ServiceAttempt:
    return source().transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="field:attempt", occurred_at=BASE + timedelta(minutes=1))


def decision(outcome: ServiceAttemptState = ServiceAttemptState.COMPLETED, *, evidence_reference: str = "field:terminal") -> Any:
    return authorize_process_service_attempt_outcome(current_attempt=attempted(), outcome=outcome, evidence_reference=evidence_reference, evidence_fingerprint=FINGERPRINT, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-outcome", executed_at=BASE + timedelta(minutes=3))


def test_completed_and_not_completed_paths_bind_terminal_evidence() -> None:
    for state, expected in ((ServiceAttemptState.COMPLETED, ServiceExecutionOutcome.COMPLETED), (ServiceAttemptState.NOT_COMPLETED, ServiceExecutionOutcome.NOT_COMPLETED)):
        value = decision(state)
        terminal = attempted().transition_to(state, evidence_reference=value.evidence_reference, occurred_at=value.occurred_at, evidence_fingerprint=value.evidence_fingerprint)
        execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id=value.service_execution_id, executed_at=value.executed_at)
        assert execution.outcome is expected
        assert execution.evidence_fingerprint == FINGERPRINT
        assert execution.tenant_id == "TENANT_A"


def test_terminal_authority_rejects_allocated_bad_evidence_and_chronology() -> None:
    with pytest.raises(ProcessServiceAttemptOutcomeAuthorityError, match="P5E_SOURCE_STATE_INVALID"):
        authorize_process_service_attempt_outcome(current_attempt=source(), outcome=ServiceAttemptState.COMPLETED, evidence_reference="x", evidence_fingerprint=FINGERPRINT, occurred_at=BASE, service_execution_id="execution", executed_at=BASE)
    with pytest.raises(ProcessServiceAttemptOutcomeAuthorityError, match="P5E_EVIDENCE_FINGERPRINT_INVALID"):
        authorize_process_service_attempt_outcome(current_attempt=attempted(), outcome=ServiceAttemptState.COMPLETED, evidence_reference="x", evidence_fingerprint="bad", occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution", executed_at=BASE + timedelta(minutes=3))
    with pytest.raises(ProcessServiceAttemptOutcomeAuthorityError, match="P5E_CHRONOLOGY_INVALID"):
        authorize_process_service_attempt_outcome(current_attempt=attempted(), outcome=ServiceAttemptState.COMPLETED, evidence_reference="x", evidence_fingerprint=FINGERPRINT, occurred_at=BASE, service_execution_id="execution", executed_at=BASE)


def test_registry_replay_and_divergence_are_fail_closed() -> None:
    collection = Collection()
    ProcessServiceAttemptOutcomeRegistry.ensure_indexes(collection)
    first = decision()
    assert ProcessServiceAttemptOutcomeRegistry.persist(first, collection, session=Session()).fingerprint == first.fingerprint
    assert ProcessServiceAttemptOutcomeRegistry.persist(first, collection, session=Session()).to_dict() == first.to_dict()
    with pytest.raises(ProcessServiceAttemptOutcomeRegistryError, match="P5E_REPLAY_CONFLICT"):
        ProcessServiceAttemptOutcomeRegistry.persist(decision(evidence_reference="field:changed"), collection, session=Session())
    assert len(collection.rows) == 1


def test_orchestrator_persists_terminal_attempt_and_execution_atomically() -> None:
    lifecycle, outcomes = Collection(), Collection()
    session = Session()
    initial = LegalOperationsLifecycleRegistry.create(source(), lifecycle, session=session)
    assert isinstance(initial, ServiceAttempt)
    attempted_value = source().transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="field:attempt", occurred_at=BASE + timedelta(minutes=1))
    persisted_attempted = LegalOperationsLifecycleRegistry.create(attempted_value, lifecycle, session=session)
    assert isinstance(persisted_attempted, ServiceAttempt)
    attempted_identity = next(row["evidence_identity"] for row in lifecycle.rows if row["p1_fingerprint"] == attempted_value.fingerprint)
    execution = transition_process_service_attempt_outcome(tenant_id="TENANT_A", current_evidence_identity=attempted_identity, lifecycle_collection=lifecycle, outcome_collection=outcomes, outcome=ServiceAttemptState.COMPLETED, evidence_reference="field:terminal", evidence_fingerprint=FINGERPRINT, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-outcome", executed_at=BASE + timedelta(minutes=3), session=session)
    assert execution.outcome is ServiceExecutionOutcome.COMPLETED
    assert len(outcomes.rows) == 1
    assert len(lifecycle.rows) == 4
    with pytest.raises(ProcessServiceAttemptOutcomeOrchestratorError, match="P5E_TRANSACTION_REQUIRED"):
        transition_process_service_attempt_outcome(tenant_id="TENANT_A", current_evidence_identity=attempted_identity, lifecycle_collection=lifecycle, outcome_collection=outcomes, outcome=ServiceAttemptState.COMPLETED, evidence_reference="field:terminal", evidence_fingerprint=FINGERPRINT, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-outcome", executed_at=BASE + timedelta(minutes=3), session=object())


def test_hard_exclusions_remain_absent() -> None:
    import tools.eos.legal_operations.domain.process_service_attempt_outcome_authority as authority
    import tools.eos.legal_operations.orchestration.process_service_attempt_outcome_orchestrator as orchestrator
    assert not hasattr(authority, "ReturnOfService")
    assert not hasattr(orchestrator, "ReturnOfService")
    assert not hasattr(orchestrator, "invoice")
    assert not hasattr(orchestrator, "payment")
    assert not hasattr(orchestrator, "settlement")


# ARTIFACT: test_process_service_attempt_outcome.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-CERT
# CERTIFICATION SCOPE: direct P5E unit evidence; no host runtime.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
