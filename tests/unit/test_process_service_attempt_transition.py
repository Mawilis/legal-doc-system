"""Direct certificate for the P5D field-attempt transition slice.

TITLE: Wilsy OS Process-Service Attempt Transition Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: P5D ALLOCATED -> ATTEMPTED evidence, registry, and orchestration only.
FAIL-CLOSED: This certificate never treats ATTEMPT as SERVICE or financial truth.
TENANT BOUNDARY: All fake persistence queries retain explicit tenant scope.
AUTHORITY BOUNDARY: P1/P2 remain authoritative; callers own transactions.
FINANCIAL BOUNDARY: Kennel EOS exclusively owns financial execution/settlement.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-CERT
           certifies immutable evidence, replay, divergence, and caller-owned
           transaction composition for one non-terminal field attempt.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState
from tools.eos.legal_operations.domain.process_service_attempt_transition_authority import (
    ProcessServiceAttemptTransitionAuthorityError,
    authorize_process_service_attempt_transition,
)
from tools.eos.legal_operations.orchestration.process_service_attempt_transition_orchestrator import (
    ProcessServiceAttemptTransitionOrchestratorError,
    transition_process_service_attempt,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_attempt_transition_registry import (
    ProcessServiceAttemptTransitionRegistry,
    ProcessServiceAttemptTransitionRegistryError,
)

BASE = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
EVIDENCE_HASH = "a" * 128


class FakeSession:
    """Minimal caller-owned transaction double."""

    in_transaction = True


class FakeCollection:
    """Deterministic Mongo-compatible collection double with session tracing."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.sessions: list[object] = []
        self.indexes: list[dict[str, Any]] = []

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"key": keys, "unique": unique, "name": name})
        return name

    def find_one(self, query: dict[str, Any], *, session: object = None) -> dict[str, Any] | None:
        self.sessions.append(session)
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def insert_one(self, row: dict[str, Any], *, session: object = None) -> object:
        self.sessions.append(session)
        for index in self.indexes:
            if index["unique"]:
                pair = tuple(key for key, _direction in index["key"])
                if any(all(existing.get(k) == row.get(k) for k in pair) for existing in self.rows):
                    raise DuplicateKeyError("duplicate")
        self.rows.append(dict(row))
        return object()


def allocated() -> ServiceAttempt:
    """Build the canonical P1 initial attempt."""
    return ServiceAttempt(
        tenant_id="TENANT_A",
        attempt_id="attempt-1",
        instruction_id="instruction-1",
        document_id="document-1",
        deputy_id="deputy-1",
        allocated_at=BASE,
        allocation_evidence_reference="p5b:receipt-1",
    )


def test_authority_requires_evidence_and_preserves_source_identity() -> None:
    source = allocated()
    decision = authorize_process_service_attempt_transition(
        current_attempt=source,
        evidence_reference="field:observation-1",
        evidence_fingerprint=EVIDENCE_HASH,
        occurred_at=BASE + timedelta(minutes=1),
    )
    assert decision.tenant_id == source.tenant_id
    assert decision.attempt_id == source.attempt_id
    assert decision.source_attempt_fingerprint == source.fingerprint
    assert decision.to_dict()["to_state"] == "ATTEMPTED"
    assert decision.fingerprint == authorize_process_service_attempt_transition(
        current_attempt=source,
        evidence_reference="field:observation-1",
        evidence_fingerprint=EVIDENCE_HASH,
        occurred_at=BASE + timedelta(minutes=1),
    ).fingerprint
    with pytest.raises(ProcessServiceAttemptTransitionAuthorityError, match="P5D_DECISION_FACTORY_REQUIRED"):
        type(decision)(**{key: getattr(decision, key) for key in decision.__dataclass_fields__ if key != "_construction_proof"})
    with pytest.raises(FrozenInstanceError):
        decision.evidence_reference = "forged"  # type: ignore[misc]


def test_authority_rejects_terminal_source_bad_chronology_and_pseudo_tenant() -> None:
    source = allocated()
    with pytest.raises(ProcessServiceAttemptTransitionAuthorityError, match="P5D_CHRONOLOGY_INVALID"):
        authorize_process_service_attempt_transition(current_attempt=source, evidence_reference="x", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE - timedelta(seconds=1))
    attempted = source.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="prior", occurred_at=BASE + timedelta(seconds=1))
    with pytest.raises(ProcessServiceAttemptTransitionAuthorityError, match="P5D_SOURCE_STATE_INVALID"):
        authorize_process_service_attempt_transition(current_attempt=attempted, evidence_reference="x", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE + timedelta(seconds=2))
    with pytest.raises(Exception):
        ServiceAttempt(tenant_id="global", attempt_id="a", instruction_id="i", document_id="d", deputy_id="p", allocated_at=BASE, allocation_evidence_reference="x")


def test_registry_replay_divergence_and_tenant_isolation() -> None:
    collection = FakeCollection()
    session = FakeSession()
    ProcessServiceAttemptTransitionRegistry.ensure_indexes(collection)
    source = allocated()
    first = authorize_process_service_attempt_transition(current_attempt=source, evidence_reference="field:1", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE + timedelta(minutes=1))
    assert ProcessServiceAttemptTransitionRegistry.persist(first, collection, session=session).to_dict() == first.to_dict()
    assert ProcessServiceAttemptTransitionRegistry.persist(first, collection, session=session).fingerprint == first.fingerprint
    assert len(collection.rows) == 1
    second = authorize_process_service_attempt_transition(current_attempt=source, evidence_reference="field:2", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE + timedelta(minutes=2))
    with pytest.raises(ProcessServiceAttemptTransitionRegistryError, match="P5D_REPLAY_CONFLICT"):
        ProcessServiceAttemptTransitionRegistry.persist(second, collection, session=session)
    with pytest.raises(ProcessServiceAttemptTransitionRegistryError, match="P5D_EVIDENCE_NOT_FOUND"):
        ProcessServiceAttemptTransitionRegistry.get("TENANT_B", first.evidence_identity, collection, session=session)
    assert all(item is session for item in collection.sessions)


def test_orchestrator_persists_only_attempted_and_requires_caller_transaction() -> None:
    lifecycle = FakeCollection()
    transition = FakeCollection()
    session = FakeSession()
    source = allocated()
    persisted_source = LegalOperationsLifecycleRegistry.create(source, lifecycle, session=session)
    source_identity = next(row["evidence_identity"] for row in lifecycle.rows if row["entity_type"] == "ServiceAttempt")
    result = transition_process_service_attempt(
        tenant_id="TENANT_A",
        current_evidence_identity=source_identity,
        lifecycle_collection=lifecycle,
        transition_collection=transition,
        evidence_reference="field:observation-1",
        evidence_fingerprint=EVIDENCE_HASH,
        occurred_at=BASE + timedelta(minutes=1),
        session=session,
    )
    assert isinstance(persisted_source, ServiceAttempt)
    assert persisted_source.state is ServiceAttemptState.ALLOCATED
    assert result.state is ServiceAttemptState.ATTEMPTED
    assert len(lifecycle.rows) == 2
    assert len(transition.rows) == 1
    with pytest.raises(ProcessServiceAttemptTransitionOrchestratorError, match="P5D_TRANSACTION_REQUIRED"):
        transition_process_service_attempt(
            tenant_id="TENANT_A", current_evidence_identity=source_identity,
            lifecycle_collection=lifecycle, transition_collection=transition,
            evidence_reference="field:observation-1", evidence_fingerprint=EVIDENCE_HASH,
            occurred_at=BASE + timedelta(minutes=1), session=object(),
        )


def test_service_execution_and_return_are_not_exposed_by_slice() -> None:
    from tools.eos.legal_operations.domain import process_service_attempt_transition_authority as authority
    from tools.eos.legal_operations.orchestration import process_service_attempt_transition_orchestrator as orchestrator
    assert not hasattr(authority, "ServiceExecution")
    assert not hasattr(authority, "ReturnOfService")
    assert not hasattr(orchestrator, "ServiceExecution")
    assert not hasattr(orchestrator, "ReturnOfService")
    assert not hasattr(ProcessServiceAttemptTransitionRegistry, "start_transaction")
    assert not hasattr(ProcessServiceAttemptTransitionRegistry, "commit")
    assert not hasattr(ProcessServiceAttemptTransitionRegistry, "abort")


# ARTIFACT: test_process_service_attempt_transition.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-CERT
# CERTIFICATION SCOPE: direct P5D evidence and composition; no host runtime.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
