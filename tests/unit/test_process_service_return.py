"""Direct certificate for P5F ReturnOfService generation and persistence.

TITLE: Wilsy OS Process-Service Return Certificate
VERSION: v1.0.0-PROCESS-SERVICE-RETURN-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: P5F return authority, registry, and caller-transaction orchestration.
TENANT BOUNDARY: Every source lookup and durable write is tenant-scoped.
AUTHORITY BOUNDARY: ReturnOfService derives only from canonical ServiceExecution;
                     no attempt, service, or caller claim can substitute it.
TRANSACTION BOUNDARY: Tests own the synthetic session; production never does.
FINANCIAL BOUNDARY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: malformed source, chronology, provenance, replay, and scope reject.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-RETURN-CERT certifies completed and
           non-completed return derivation, replay, isolation, and boundaries.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    ServiceExecutionOutcome,
)
from tools.eos.legal_operations.domain.process_service_return_authority import (
    ProcessServiceReturnAuthorityError,
    ProcessServiceReturnDecision,
    authorize_process_service_return,
)
from tools.eos.legal_operations.orchestration.process_service_return_orchestrator import (
    ProcessServiceReturnOrchestratorError,
    generate_process_service_return,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)
from tools.eos.legal_operations.registry.process_service_return_registry import (
    ProcessServiceReturnRegistry,
    ProcessServiceReturnRegistryError,
)

VERSION = "v1.0.0-PROCESS-SERVICE-RETURN-CERT"
BASE = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
TERMINAL_FINGERPRINT = "e" * 128


class Session:
    """Minimal caller-owned active transaction marker."""

    in_transaction = True


class Collection:
    """Deterministic Mongo-compatible collection double."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.sessions: list[object] = []

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"key": keys, "unique": unique, "name": name})
        return name

    def _match(self, row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def find_one(self, query: dict[str, Any], *, session: object = None) -> dict[str, Any] | None:
        self.sessions.append(session)
        for row in self.rows:
            if self._match(row, query):
                return dict(row)
        return None

    def find(self, query: dict[str, Any], *, session: object = None) -> list[dict[str, Any]]:
        self.sessions.append(session)
        return [dict(row) for row in self.rows if self._match(row, query)]

    def insert_one(self, row: dict[str, Any], *, session: object = None) -> object:
        self.sessions.append(session)
        for index in self.indexes:
            if index["unique"]:
                keys = tuple(key for key, _direction in index["key"])
                if any(all(existing.get(key) == row.get(key) for key in keys) for existing in self.rows):
                    raise DuplicateKeyError("duplicate")
        self.rows.append(dict(row))
        return object()

    def count_documents(self, query: dict[str, Any]) -> int:
        return sum(1 for row in self.rows if self._match(row, query))


def _attempt(tenant: str, suffix: str) -> tuple[ServiceAttempt, ServiceAttempt, ServiceAttempt]:
    allocated = ServiceAttempt(
        tenant_id=tenant,
        attempt_id=f"attempt-{suffix}",
        instruction_id=f"instruction-{suffix}",
        document_id=f"document-{suffix}",
        deputy_id=f"deputy-{suffix}",
        allocated_at=BASE,
        allocation_evidence_reference=f"allocation:{suffix}",
    )
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference=f"attempt:{suffix}",
        occurred_at=BASE + timedelta(minutes=1),
    )
    terminal = attempted.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference=f"terminal:{suffix}",
        evidence_fingerprint=TERMINAL_FINGERPRINT,
        occurred_at=BASE + timedelta(minutes=2),
    )
    return allocated, attempted, terminal


def _noncompleted_attempt(tenant: str, suffix: str) -> ServiceAttempt:
    allocated, attempted, _ = _attempt(tenant, suffix)
    return attempted.transition_to(
        ServiceAttemptState.NOT_COMPLETED,
        evidence_reference=f"terminal-not:{suffix}",
        evidence_fingerprint=TERMINAL_FINGERPRINT,
        occurred_at=BASE + timedelta(minutes=2),
    )


def _seed_execution(
    lifecycle: Collection,
    tenant: str,
    suffix: str,
    *,
    noncompleted: bool = False,
) -> tuple[ServiceAttempt, ServiceExecution, str]:
    allocated, attempted, completed = _attempt(tenant, suffix)
    terminal = _noncompleted_attempt(tenant, suffix) if noncompleted else completed
    session = Session()
    for snapshot in (allocated, attempted, terminal):
        LegalOperationsLifecycleRegistry.create(snapshot, lifecycle, session=session)
    execution = ServiceExecution.from_attempt(
        attempt=terminal,
        service_execution_id=f"execution-{suffix}",
        executed_at=BASE + timedelta(minutes=3),
    )
    LegalOperationsLifecycleRegistry.create(execution, lifecycle, session=session, source_attempt=terminal)
    row = lifecycle.find_one(
        {"tenant_id": tenant, "entity_type": "ServiceExecution", "entity_identity": execution.service_execution_id},
        session=session,
    )
    assert row is not None
    return terminal, execution, row["evidence_identity"]


def test_p1_factories_support_both_outcomes_and_bind_source() -> None:
    _, completed, _ = _seed_execution(Collection(), "tenant-a", "completed")
    noncompleted_attempt = _noncompleted_attempt("tenant-a", "not-completed")
    noncompleted = ServiceExecution.from_attempt(
        attempt=noncompleted_attempt,
        service_execution_id="execution-not-completed",
        executed_at=BASE + timedelta(minutes=3),
    )
    generated = ReturnOfService.from_service_execution(
        instruction_id=completed.instruction_id,
        service_execution=completed,
        return_id="return-completed",
        generated_at=BASE + timedelta(minutes=4),
    )
    generated_not = ReturnOfService.from_service_execution(
        instruction_id=noncompleted.instruction_id,
        service_execution=noncompleted,
        return_id="return-not-completed",
        generated_at=BASE + timedelta(minutes=4),
    )
    assert generated.service_execution_id == completed.service_execution_id
    assert generated.service_outcome is ServiceExecutionOutcome.COMPLETED
    assert generated_not.service_outcome is ServiceExecutionOutcome.NOT_COMPLETED
    assert generated.service_evidence_fingerprint == TERMINAL_FINGERPRINT


def test_direct_return_and_authority_construction_and_chronology_fail_closed() -> None:
    _, execution, _ = _seed_execution(Collection(), "tenant-a", "direct")
    with pytest.raises(Exception, match="validated service-execution factory"):
        ReturnOfService()  # type: ignore[call-arg]
    with pytest.raises(ProcessServiceReturnAuthorityError, match="P5F_DECISION_FACTORY_REQUIRED"):
        ProcessServiceReturnDecision(
            tenant_id="tenant-a",
            service_execution_id=execution.service_execution_id,
            attempt_id=execution.attempt_id,
            instruction_id=execution.instruction_id,
            document_id=execution.document_id,
            outcome=execution.outcome,
            source_execution_fingerprint=execution.fingerprint,
            return_id="return-direct",
            generated_at=BASE + timedelta(minutes=4),
            evidence_identity="f" * 128,
        )
    with pytest.raises(Exception, match="return generation chronology"):
        ReturnOfService.from_service_execution(
            instruction_id=execution.instruction_id,
            service_execution=execution,
            return_id="return-early",
            generated_at=BASE + timedelta(minutes=2),
        )
    with pytest.raises(Exception, match="return instruction binding"):
        ReturnOfService.from_service_execution(
            instruction_id="instruction-other",
            service_execution=execution,
            return_id="return-mismatch",
            generated_at=BASE + timedelta(minutes=4),
        )


def test_orchestrator_derives_execution_and_return_without_caller_claims() -> None:
    lifecycle, returns = Collection(), Collection()
    LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
    ProcessServiceReturnRegistry.ensure_indexes(returns)
    terminal, execution, execution_identity = _seed_execution(lifecycle, "tenant-a", "orchestrated")
    execution_before = execution.to_dict()
    result = generate_process_service_return(
        tenant_id="tenant-a",
        execution_evidence_identity=execution_identity,
        lifecycle_collection=lifecycle,
        return_collection=returns,
        return_id="return-orchestrated",
        generated_at=BASE + timedelta(minutes=4),
        session=Session(),
    )
    assert result.tenant_id == terminal.tenant_id == execution.tenant_id
    assert result.attempt_id == execution.attempt_id == terminal.attempt_id
    assert result.document_id == execution.document_id == terminal.document_id
    assert result.service_execution_id == execution.service_execution_id
    assert result.service_outcome is execution.outcome
    assert result.service_evidence_fingerprint == execution.evidence_fingerprint
    assert execution.to_dict() == execution_before
    assert execution.to_dict() == ServiceExecution.from_attempt(
        attempt=terminal,
        service_execution_id=execution.service_execution_id,
        executed_at=execution.executed_at,
    ).to_dict()
    assert lifecycle.count_documents({"tenant_id": "tenant-a", "entity_type": "ReturnOfService"}) == 1
    assert returns.count_documents({"tenant_id": "tenant-a"}) == 1


def test_orchestrator_supports_not_completed_and_requires_active_transaction() -> None:
    lifecycle, returns = Collection(), Collection()
    LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
    ProcessServiceReturnRegistry.ensure_indexes(returns)
    _, execution, identity = _seed_execution(lifecycle, "tenant-a", "not-completed", noncompleted=True)
    result = generate_process_service_return(
        tenant_id="tenant-a",
        execution_evidence_identity=identity,
        lifecycle_collection=lifecycle,
        return_collection=returns,
        return_id="return-not-completed",
        generated_at=BASE + timedelta(minutes=4),
        session=Session(),
    )
    assert result.service_outcome is ServiceExecutionOutcome.NOT_COMPLETED
    with pytest.raises(ProcessServiceReturnOrchestratorError, match="P5F_TRANSACTION_REQUIRED"):
        generate_process_service_return(
            tenant_id="tenant-a",
            execution_evidence_identity=identity,
            lifecycle_collection=lifecycle,
            return_collection=returns,
            return_id="return-no-transaction",
            generated_at=BASE + timedelta(minutes=4),
            session=object(),
        )
    assert execution.to_dict()["outcome"] == "NOT_COMPLETED"


def test_exact_replay_and_divergent_return_reject_without_overwrite() -> None:
    lifecycle, returns = Collection(), Collection()
    LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
    ProcessServiceReturnRegistry.ensure_indexes(returns)
    _, _, identity = _seed_execution(lifecycle, "tenant-a", "replay")
    first = generate_process_service_return(
        tenant_id="tenant-a", execution_evidence_identity=identity, lifecycle_collection=lifecycle,
        return_collection=returns, return_id="return-replay", generated_at=BASE + timedelta(minutes=4), session=Session()
    )
    replay = generate_process_service_return(
        tenant_id="tenant-a", execution_evidence_identity=identity, lifecycle_collection=lifecycle,
        return_collection=returns, return_id="return-replay", generated_at=BASE + timedelta(minutes=4), session=Session()
    )
    assert replay.to_dict() == first.to_dict()
    assert len(returns.rows) == 1
    with pytest.raises(ProcessServiceReturnRegistryError, match="P5F_REPLAY_CONFLICT"):
        generate_process_service_return(
            tenant_id="tenant-a", execution_evidence_identity=identity, lifecycle_collection=lifecycle,
            return_collection=returns, return_id="return-replay", generated_at=BASE + timedelta(minutes=5), session=Session()
        )
    assert len(returns.rows) == 1


def test_p2_return_factory_provenance_requires_matching_attempt_and_execution() -> None:
    lifecycle = Collection()
    _, execution, _ = _seed_execution(lifecycle, "tenant-a", "provenance")
    _, other_execution, _ = _seed_execution(lifecycle, "tenant-a", "other-provenance")
    return_value = ReturnOfService.from_service_execution(
        instruction_id=execution.instruction_id,
        service_execution=execution,
        return_id="return-provenance",
        generated_at=BASE + timedelta(minutes=4),
    )
    with pytest.raises(Exception, match="M2_FACTORY_SOURCE_INVALID"):
        LegalOperationsLifecycleRegistry.create(
            return_value,
            lifecycle,
            session=Session(),
            source_attempt=_attempt("tenant-a", "provenance")[2],
            source_execution=other_execution,
        )
    with pytest.raises(Exception, match="M2_FACTORY_SOURCE_REQUIRED"):
        LegalOperationsLifecycleRegistry.create(
            return_value,
            lifecycle,
            session=Session(),
            source_attempt=_attempt("tenant-a", "provenance")[2],
        )
def test_tenant_isolation_source_validation_and_hard_financial_exclusions() -> None:
    lifecycle, returns = Collection(), Collection()
    LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
    ProcessServiceReturnRegistry.ensure_indexes(returns)
    _, _, identity = _seed_execution(lifecycle, "tenant-a", "scope")
    with pytest.raises(Exception, match="M2_EVIDENCE_NOT_FOUND"):
        LegalOperationsLifecycleRegistry.get("tenant-b", identity, lifecycle, session=Session())
    with pytest.raises(Exception, match="P5F_EVIDENCE_NOT_FOUND"):
        ProcessServiceReturnRegistry.get("tenant-b", "0" * 128, returns, session=Session())
    with pytest.raises(Exception):
        generate_process_service_return(
            tenant_id="global", execution_evidence_identity=identity, lifecycle_collection=lifecycle,
            return_collection=returns, return_id="return-global", generated_at=BASE + timedelta(minutes=4), session=Session()
        )
    import tools.eos.legal_operations.domain.process_service_return_authority as authority
    import tools.eos.legal_operations.registry.process_service_return_registry as registry
    import tools.eos.legal_operations.orchestration.process_service_return_orchestrator as orchestrator
    for module in (authority, registry, orchestrator):
        assert not hasattr(module, "invoice")
        assert not hasattr(module, "payment")
        assert not hasattr(module, "settlement")
    assert not hasattr(ProcessServiceReturnRegistry, "start_transaction")
    assert not hasattr(ProcessServiceReturnRegistry, "commit")
    assert not hasattr(ProcessServiceReturnRegistry, "abort")


# ARTIFACT: test_process_service_return.py
# VERSION: v1.0.0-PROCESS-SERVICE-RETURN-CERT
# CERTIFICATION SCOPE: direct P5F return authority, persistence, and composition.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
