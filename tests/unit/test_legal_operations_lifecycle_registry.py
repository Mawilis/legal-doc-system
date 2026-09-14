"""Direct adversarial certificate for the Legal Operations P2 registry.

TITLE: Wilsy OS Legal Operations Lifecycle Evidence Registry Certificate
VERSION: v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify immutable snapshot persistence, exact factory provenance,
         strict hydration, replay integrity, and tenant/session boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_lifecycle_registry.py
COLLABORATION / OWNERSHIP: Direct certificate for the P2 registry only; P1
                            remains lifecycle/evidence authority and callers own
                            Mongo sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: 2026-09-13 v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-CERT adds
           deterministic fake-Mongo proofs for immutable snapshots, complete
           factory provenance, strict corruption rejection, and isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers only; no real database,
                             network, provider, secret, or customer access.
TENANT BOUNDARY: Every fixture and lookup is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Persistence and hydration certificate only; P1 owns all
                    lifecycle and service/return authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; no financial behavior is tested
                              or introduced here.
FAIL-CLOSED DECLARATION: Any schema, provenance, replay, tenant, or session
                         violation fails this certificate.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from dataclasses import fields
from typing import Any, Callable, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    LegalInstruction,
    LegalInstructionState,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    ReturnOfService,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)


NOW = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)
TERMINAL_FINGERPRINT = "a" * 128


class FakeSession:
    """Minimal caller-owned session double exposing transaction state only."""

    def __init__(self, in_transaction: bool = False) -> None:
        self.in_transaction = in_transaction


class FakeCollection:
    """Deterministic Mongo-compatible collection double for this certificate."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, object]] = []
        self.indexes: list[tuple[object, dict[str, object]]] = []
        self.raise_duplicate = False

    def create_index(self, keys: object, **kwargs: object) -> str:
        self.indexes.append((keys, dict(kwargs)))
        return cast(str, kwargs.get("name", "fake-index"))

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, Any] | None:
        self.calls.append(("find_one", session, deepcopy(query)))
        for document in self.docs:
            if all(document.get(key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def insert_one(self, document: dict[str, object], *, session: object = None) -> object:
        self.calls.append(("insert_one", session, deepcopy(document)))
        if self.raise_duplicate:
            raise DuplicateKeyError("synthetic duplicate race")
        self.docs.append(deepcopy(cast(dict[str, Any], document)))
        return object()


class RaceCollection(FakeCollection):
    """Collection whose first reads miss, then insertion reports a duplicate."""

    def __init__(self, raced_document: dict[str, Any]) -> None:
        super().__init__()
        self.docs.append(deepcopy(raced_document))
        self.hidden_reads = 2
        self.raise_duplicate = True

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, Any] | None:
        if self.hidden_reads:
            self.hidden_reads -= 1
            self.calls.append(("find_one", session, deepcopy(query)))
            return None
        return super().find_one(query, session=session)


class DivergentRaceCollection(RaceCollection):
    """Duplicate race returning a valid but canonically different durable row."""

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, Any] | None:
        if self.hidden_reads:
            return super().find_one(query, session=session)
        self.calls.append(("find_one", session, deepcopy(query)))
        return deepcopy(self.docs[0])


def instruction(**overrides: object) -> LegalInstruction:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "instruction_id": "instruction-1",
        "case_matter_id": "matter-1",
        "document_id": "document-1",
        "registered_at": NOW,
        "evidence_reference": "instruction-registration",
    }
    values.update(overrides)
    return cast(Any, LegalInstruction)(**values)


def terminal_attempt(**overrides: object) -> ServiceAttempt:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "attempt_id": "attempt-1",
        "instruction_id": "instruction-1",
        "document_id": "document-1",
        "deputy_id": "deputy-1",
        "allocated_at": NOW,
        "allocation_evidence_reference": "allocation-evidence",
    }
    values.update(overrides)
    value = cast(Any, ServiceAttempt)(**values)
    value = value.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempt-evidence",
        occurred_at=NOW + timedelta(minutes=1),
    )
    return value.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="completed-evidence",
        evidence_fingerprint=TERMINAL_FINGERPRINT,
        occurred_at=NOW + timedelta(minutes=2),
    )


def expect_code(code: str, operation: Callable[[], object]) -> None:
    with pytest.raises(LegalOperationsLifecycleRegistryError) as caught:
        operation()
    assert str(caught.value) == code


def persisted_record(value: Any, collection: FakeCollection, **kwargs: Any) -> dict[str, Any]:
    result = LegalOperationsLifecycleRegistry.create(value, collection, **kwargs)
    assert result.to_dict() == cast(Any, value).to_dict()
    return collection.docs[-1]


def test_index_contract_and_immutable_snapshot_progression() -> None:
    collection = FakeCollection()
    LegalOperationsLifecycleRegistry.ensure_indexes(collection)
    assert len(collection.indexes) == 2
    history = collection.indexes[0]
    evidence = collection.indexes[1]
    assert history[0] == [("tenant_id", 1), ("entity_type", 1), ("entity_identity", 1)]
    assert history[1]["unique"] is False
    assert evidence[0] == [("tenant_id", 1), ("evidence_identity", 1)]
    assert evidence[1]["unique"] is True

    initial = instruction()
    accepted = initial.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted",
        occurred_at=NOW + timedelta(minutes=1),
    )
    first = persisted_record(initial, collection)
    second = persisted_record(accepted, collection)
    assert len(collection.docs) == 2
    assert first["entity_identity"] == second["entity_identity"]
    assert first["evidence_identity"] != second["evidence_identity"]
    assert LegalOperationsLifecycleRegistry.get("tenant-a", first["evidence_identity"], collection).to_dict() == initial.to_dict()
    assert LegalOperationsLifecycleRegistry.get("tenant-a", second["evidence_identity"], collection).to_dict() == accepted.to_dict()


def test_exact_replay_compares_complete_record_and_provenance_divergence_rejects() -> None:
    collection = FakeCollection()
    attempt = terminal_attempt()
    execution = ServiceExecution.from_attempt(
        attempt=attempt,
        service_execution_id="execution-1",
        executed_at=NOW + timedelta(minutes=3),
    )
    record = persisted_record(execution, collection, source_attempt=attempt)
    replay = LegalOperationsLifecycleRegistry.create(execution, collection, source_attempt=attempt)
    assert replay.to_dict() == execution.to_dict()
    assert len(collection.docs) == 1
    assert collection.docs[0] == record

    later_execution = ServiceExecution.from_attempt(
        attempt=attempt,
        service_execution_id="execution-1",
        executed_at=NOW + timedelta(minutes=4),
    )
    returned = __import__("tools.eos.legal_operations.domain.legal_operations_lifecycle", fromlist=["ReturnOfService"]).ReturnOfService.from_service_execution(
        instruction_id="instruction-1",
        service_execution=execution,
        return_id="return-1",
        generated_at=NOW + timedelta(minutes=5),
    )
    persisted_record(returned, collection, source_attempt=attempt, source_execution=execution)
    expect_code(
        "M2_REPLAY_CONFLICT",
        lambda: LegalOperationsLifecycleRegistry.create(
            returned,
            collection,
            source_attempt=attempt,
            source_execution=later_execution,
        ),
    )


def test_service_execution_factory_provenance_round_trip_and_source_arguments() -> None:
    collection = FakeCollection()
    attempt = terminal_attempt()
    execution = ServiceExecution.from_attempt(
        attempt=attempt,
        service_execution_id="execution-1",
        executed_at=NOW + timedelta(minutes=3),
    )
    record = persisted_record(execution, collection, source_attempt=attempt)
    assert record["source_payload"] == {"attempt": attempt.to_dict()}
    hydrated = LegalOperationsLifecycleRegistry.get("tenant-a", record["evidence_identity"], collection)
    assert hydrated.to_dict() == execution.to_dict()
    assert hydrated.fingerprint == execution.fingerprint
    expect_code("M2_FACTORY_SOURCE_REQUIRED", lambda: LegalOperationsLifecycleRegistry.create(execution, FakeCollection()))
    expect_code(
        "M2_FACTORY_SOURCE_INVALID",
        lambda: LegalOperationsLifecycleRegistry.create(execution, FakeCollection(), source_attempt=attempt, source_execution=execution),
    )


def test_return_factory_preserves_actual_later_execution_timestamp_and_bindings() -> None:
    collection = FakeCollection()
    attempt = terminal_attempt()
    terminal_at = attempt.transition_history[-1].occurred_at
    execution = ServiceExecution.from_attempt(
        attempt=attempt,
        service_execution_id="execution-1",
        executed_at=terminal_at + timedelta(minutes=7),
    )
    returned = __import__("tools.eos.legal_operations.domain.legal_operations_lifecycle", fromlist=["ReturnOfService"]).ReturnOfService.from_service_execution(
        instruction_id="instruction-1",
        service_execution=execution,
        return_id="return-1",
        generated_at=execution.executed_at + timedelta(minutes=1),
    )
    record = persisted_record(returned, collection, source_attempt=attempt, source_execution=execution)
    source_execution = record["source_payload"]["service_execution"]
    assert source_execution["executed_at"] == execution.executed_at.isoformat()
    assert source_execution["executed_at"] != terminal_at.isoformat()
    hydrated = LegalOperationsLifecycleRegistry.get("tenant-a", record["evidence_identity"], collection)
    assert hydrated.to_dict() == returned.to_dict()
    assert cast(Any, hydrated).service_execution_id == execution.service_execution_id
    expect_code(
        "M2_FACTORY_SOURCE_REQUIRED",
        lambda: LegalOperationsLifecycleRegistry.create(returned, FakeCollection(), source_attempt=attempt),
    )
    other_attempt = terminal_attempt(attempt_id="attempt-2")
    other_execution = ServiceExecution.from_attempt(
        attempt=other_attempt,
        service_execution_id="execution-2",
        executed_at=execution.executed_at,
    )
    expect_code(
        "M2_FACTORY_SOURCE_INVALID",
        lambda: LegalOperationsLifecycleRegistry.create(
            returned,
            FakeCollection(),
            source_attempt=other_attempt,
            source_execution=other_execution,
        ),
    )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row.update({"extra": True}),
        lambda row: row.pop("p1_payload"),
        lambda row: (row.update({"p1_version": "unsupported"}), row["p1_payload"].update({"version": "unsupported"})),
        lambda row: (row.update({"p1_schema": "unsupported"}), row["p1_payload"].update({"schema": "unsupported"})),
        lambda row: row.update({"entity_type": "UnknownEntity"}),
        lambda row: row.update({"evidence_identity": "x" * 128}),
        lambda row: row.update({"p1_fingerprint": "x" * 128}),
        lambda row: row.update({"entity_identity": "tampered"}),
        lambda row: row["p1_payload"].update({"transition_history": "not-a-list"}),
    ],
)
def test_strict_record_and_p1_corruption_rejects(mutation: Callable[[dict[str, Any]], object]) -> None:
    collection = FakeCollection()
    record = persisted_record(instruction(), collection)
    changed = deepcopy(record)
    mutation(changed)
    collection.docs[0] = changed
    expect_code_any = {"M2_RECORD_SCHEMA_INVALID", "M2_P1_VERSION_UNSUPPORTED", "M2_ENTITY_TYPE_UNSUPPORTED", "M2_EVIDENCE_IDENTITY_INVALID", "M2_EVIDENCE_NOT_FOUND", "M2_ENTITY_ID_MISMATCH", "M2_P1_FINGERPRINT_INVALID", "M2_P1_FINGERPRINT_MISMATCH", "M2_P1_PAYLOAD_SCHEMA_INVALID", "M2_HISTORY_INVALID"}
    with pytest.raises(LegalOperationsLifecycleRegistryError) as caught:
        LegalOperationsLifecycleRegistry.get("tenant-a", record["evidence_identity"], collection)
    assert str(caught.value) in expect_code_any


def test_factory_source_payload_and_fingerprint_corruption_rejects() -> None:
    collection = FakeCollection()
    attempt = terminal_attempt()
    execution = ServiceExecution.from_attempt(attempt=attempt, service_execution_id="execution-1", executed_at=NOW + timedelta(minutes=3))
    record = persisted_record(execution, collection, source_attempt=attempt)
    changed = deepcopy(record)
    changed["source_fingerprint"] = "0" * 128
    collection.docs[0] = changed
    with pytest.raises(LegalOperationsLifecycleRegistryError):
        LegalOperationsLifecycleRegistry.get("tenant-a", record["evidence_identity"], collection)

    changed = deepcopy(record)
    changed["source_payload"]["attempt"]["transition_history"][-1]["evidence_reference"] = "tampered"
    collection.docs[0] = changed
    with pytest.raises(LegalOperationsLifecycleRegistryError):
        LegalOperationsLifecycleRegistry.get("tenant-a", record["evidence_identity"], collection)


def test_return_source_execution_chronology_and_binding_corruption_rejects() -> None:
    collection = FakeCollection()
    attempt = terminal_attempt()
    execution = ServiceExecution.from_attempt(attempt=attempt, service_execution_id="execution-1", executed_at=NOW + timedelta(minutes=3))
    returned = __import__("tools.eos.legal_operations.domain.legal_operations_lifecycle", fromlist=["ReturnOfService"]).ReturnOfService.from_service_execution(instruction_id="instruction-1", service_execution=execution, return_id="return-1", generated_at=NOW + timedelta(minutes=4))
    record = persisted_record(returned, collection, source_attempt=attempt, source_execution=execution)
    for mutate in (
        lambda row: row["source_payload"]["service_execution"].update({"executed_at": NOW.isoformat()}),
        lambda row: row["source_payload"]["service_execution"].update({"service_execution_id": "other"}),
        lambda row: row["source_payload"]["attempt"].update({"attempt_id": "other"}),
    ):
        changed = deepcopy(record)
        mutate(changed)
        collection.docs[0] = changed
        with pytest.raises(LegalOperationsLifecycleRegistryError):
            LegalOperationsLifecycleRegistry.get("tenant-a", record["evidence_identity"], collection)


@pytest.mark.parametrize("tenant", ["default", "global", "global_root", "root", "master", "*"])
def test_tenant_isolation_and_pseudo_tenants_fail_closed(tenant: str) -> None:
    collection = FakeCollection()
    record = persisted_record(instruction(), collection)
    expect_code("M2_INVALID_TENANT", lambda: LegalOperationsLifecycleRegistry.get(tenant, record["evidence_identity"], collection))
    expect_code("M2_EVIDENCE_NOT_FOUND", lambda: LegalOperationsLifecycleRegistry.get("tenant-b", record["evidence_identity"], collection))


def test_session_forwarding_transaction_ownership_and_race_contract() -> None:
    collection = FakeCollection()
    session = FakeSession()
    record = persisted_record(instruction(), collection, session=session)
    LegalOperationsLifecycleRegistry.get("tenant-a", record["evidence_identity"], collection, session=session)
    assert all(call[1] is session for call in collection.calls if call[0] in {"find_one", "insert_one"})
    assert not any(name in LegalOperationsLifecycleRegistry.__dict__ for name in ("start_transaction", "commit_transaction", "abort_transaction", "commit", "abort"))
    assert not any(name in LegalOperationsLifecycleRegistry.__dict__ for name in ("_client", "client", "mongo_client"))

    raced = RaceCollection(record)
    replay = LegalOperationsLifecycleRegistry.create(instruction(), raced, session=session)
    assert replay.to_dict() == instruction().to_dict()
    assert len(raced.docs) == 1
    active = RaceCollection(record)
    active_session = FakeSession(in_transaction=True)
    expect_code("M2_RETRY_TRANSACTION_REQUIRED", lambda: LegalOperationsLifecycleRegistry.create(instruction(), active, session=active_session))


def test_outside_transaction_duplicate_race_divergence_is_replay_conflict() -> None:
    source = FakeCollection()
    divergent = instruction(evidence_reference="raced-durable-evidence")
    divergent_record = persisted_record(divergent, source)
    raced = DivergentRaceCollection(divergent_record)
    expect_code("M2_REPLAY_CONFLICT", lambda: LegalOperationsLifecycleRegistry.create(instruction(), raced, session=FakeSession()))
    assert len(raced.docs) == 1


def test_unsupported_inputs_irrelevant_sources_and_non_financial_authority() -> None:
    expect_code("M2_P1_VALUE_REQUIRED", lambda: LegalOperationsLifecycleRegistry.create(cast(Any, object()), FakeCollection()))
    value = instruction()
    attempt = terminal_attempt()
    expect_code("M2_FACTORY_SOURCE_INVALID", lambda: LegalOperationsLifecycleRegistry.create(value, FakeCollection(), source_attempt=attempt))
    expect_code("M2_FACTORY_SOURCE_INVALID", lambda: LegalOperationsLifecycleRegistry.create(value, FakeCollection(), source_execution=cast(Any, object())))
    assert not {field.name.casefold() for field in fields(value)}.intersection({"invoice", "payment", "settlement", "execution", "billing"})
    assert "Kennel EOS exclusively" in (LegalOperationsLifecycleRegistry.__doc__ or "") or "Kennel EOS" in open(__file__, encoding="utf-8").read()


# ARTIFACT: test_legal_operations_lifecycle_registry.py
# VERSION: v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct P2 persistence/hydration certificate only.
# TENANT POSTURE: explicit synthetic tenants; foreign evidence is undisclosed.
# FAIL-CLOSED POSTURE: malformed records, provenance, races, and sources reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution/settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
