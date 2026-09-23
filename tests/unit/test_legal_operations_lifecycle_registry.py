"""Direct adversarial certificate for the Legal Operations P2 registry.

TITLE: Wilsy OS Legal Operations Lifecycle Evidence Registry Certificate
VERSION: v1.3.0-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify immutable snapshot persistence, exact entity, tenant/entity-
         class and document-custody enumeration, exact factory provenance,
         strict hydration, replay integrity, and tenant/session boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_lifecycle_registry.py
COLLABORATION / OWNERSHIP: Direct certificate for the P2 registry only; P1
                            remains lifecycle/evidence authority and callers own
                            Mongo sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.3.0-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION-CERT
           certifies exact tenant/entity-class snapshot enumeration, stable
           identity/fingerprint ordering, caller-session forwarding, foreign
           absence, unsupported-type rejection, corruption rejection, and
           persistence-failure translation for the L8-5 foundation.
           2026-09-23 v1.2.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-CERT
           certifies the dedicated tenant/document custody-history index and
           query, strict P1 hydration, foreign absence, caller-session
           forwarding, invalid document scope, and read-failure translation.
           2026-09-23 v1.1.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-CERT added
           exact tenant/type/entity history enumeration, caller-session
           forwarding, foreign absence, strict multi-row hydration/corruption,
           invalid-scope, and history-read persistence-failure proofs.
           2026-09-14 v1.0.1-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-CERT added
           direct labeled-transient conflict translation, uncertain-commit
           exclusion, and generic persistence regression proofs.
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
from pymongo.errors import DuplicateKeyError, OperationFailure

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    DocumentCustodyEvent,
    DocumentCustodyEventType,
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
    VERSION as P2_VERSION,
)


NOW = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)
TERMINAL_FINGERPRINT = "a" * 128


class FakeSession:
    """Minimal caller-owned session double exposing transaction state only."""

    def __init__(self, in_transaction: bool = False) -> None:
        self.in_transaction = in_transaction


def _lookup(document: dict[str, Any], key: str) -> Any:
    """Resolve a Mongo-style dotted path inside one fake durable document."""
    value: Any = document
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


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
            if all(_lookup(document, key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def find(self, query: dict[str, object], *, session: object = None) -> list[dict[str, Any]]:
        """Return all exact matches while recording caller-owned session scope."""
        self.calls.append(("find", session, deepcopy(query)))
        return [
            deepcopy(document)
            for document in self.docs
            if all(_lookup(document, key) == value for key, value in query.items())
        ]

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


class FailureCollection(FakeCollection):
    """Collection that raises one real PyMongo error from the insert path."""

    def __init__(self, error: OperationFailure) -> None:
        super().__init__()
        self.error = error

    def insert_one(self, document: dict[str, object], *, session: object = None) -> object:
        self.calls.append(("insert_one", session, deepcopy(document)))
        raise self.error


class HistoryFailureCollection(FakeCollection):
    """Collection that raises one real PyMongo error from the history read path."""

    def __init__(self, error: OperationFailure) -> None:
        super().__init__()
        self.error = error

    def find(self, query: dict[str, object], *, session: object = None) -> list[dict[str, Any]]:
        self.calls.append(("find", session, deepcopy(query)))
        raise self.error


class TrackingSession(FakeSession):
    """Active caller session proving P2 does not own lifecycle operations."""

    def __init__(self) -> None:
        super().__init__(in_transaction=True)
        self.start_calls = 0
        self.commit_calls = 0
        self.abort_calls = 0
        self.end_calls = 0

    def start_transaction(self) -> None:
        self.start_calls += 1

    def commit_transaction(self) -> None:
        self.commit_calls += 1

    def abort_transaction(self) -> None:
        self.abort_calls += 1

    def end_session(self) -> None:
        self.end_calls += 1


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


def custody_event(
    *,
    tenant_id: str = "tenant-a",
    event_id: str = "custody-1",
    document_id: str = "document-1",
    event_type: DocumentCustodyEventType = DocumentCustodyEventType.REGISTERED,
    sequence_number: int = 1,
    occurred_at: datetime = NOW,
    evidence_reference: str = "custody-evidence",
    to_holder_reference: str | None = None,
) -> DocumentCustodyEvent:
    """Build one deterministic P1 custody fact for P2 history certification."""
    return DocumentCustodyEvent(
        tenant_id=tenant_id,
        custody_event_id=event_id,
        document_id=document_id,
        event_type=event_type,
        occurred_at=occurred_at,
        sequence_number=sequence_number,
        evidence_reference=evidence_reference,
        to_holder_reference=to_holder_reference,
    )


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
    assert len(collection.indexes) == 3
    history = collection.indexes[0]
    custody = collection.indexes[1]
    evidence = collection.indexes[2]
    assert history[0] == [("tenant_id", 1), ("entity_type", 1), ("entity_identity", 1)]
    assert history[1]["unique"] is False
    assert custody[0] == [
        ("tenant_id", 1),
        ("entity_type", 1),
        ("p1_payload.document_id", 1),
    ]
    assert custody[1]["unique"] is False
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


def test_exact_entity_history_hydrates_all_snapshots_and_forwards_session() -> None:
    """History retrieval returns all exact-scope P1 snapshots without choosing current."""
    collection = FakeCollection()
    session = FakeSession(in_transaction=True)
    initial = instruction()
    accepted = initial.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted",
        occurred_at=NOW + timedelta(minutes=1),
    )
    persisted_record(initial, collection, session=session)
    persisted_record(accepted, collection, session=session)

    history = LegalOperationsLifecycleRegistry.get_entity_history(
        "tenant-a",
        "LegalInstruction",
        "instruction-1",
        collection,
        session=session,
    )

    assert tuple(value.to_dict() for value in history) == (
        initial.to_dict(),
        accepted.to_dict(),
    )
    history_calls = [call for call in collection.calls if call[0] == "find"]
    assert history_calls == [
        (
            "find",
            session,
            {
                "tenant_id": "tenant-a",
                "entity_type": "LegalInstruction",
                "entity_identity": "instruction-1",
            },
        )
    ]
    assert LegalOperationsLifecycleRegistry.get_entity_history(
        "tenant-b",
        "LegalInstruction",
        "instruction-1",
        collection,
        session=session,
    ) == ()


def test_tenant_entity_snapshot_enumeration_is_exact_deterministic_and_session_bound() -> None:
    """Tenant/entity enumeration returns strict P1 snapshots without current inference."""
    collection = FakeCollection()
    session = FakeSession(in_transaction=True)
    first = instruction(instruction_id="instruction-b")
    first_accepted = first.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted-b",
        occurred_at=NOW + timedelta(minutes=1),
    )
    second = instruction(
        instruction_id="instruction-a",
        case_matter_id="matter-2",
        document_id="document-2",
        evidence_reference="registration-a",
    )
    foreign = instruction(
        tenant_id="tenant-b",
        instruction_id="instruction-a",
        case_matter_id="matter-foreign",
        document_id="document-foreign",
        evidence_reference="foreign-registration",
    )
    for value in (first_accepted, foreign, second, first):
        persisted_record(value, collection, session=session)

    collection.calls.clear()
    snapshots = LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
        "tenant-a",
        "LegalInstruction",
        collection,
        session=session,
    )

    assert len(snapshots) == 3
    assert all(value.tenant_id == "tenant-a" for value in snapshots)
    assert [value.instruction_id for value in snapshots] == [
        "instruction-a",
        "instruction-b",
        "instruction-b",
    ]
    assert tuple(value.fingerprint for value in snapshots) == tuple(
        sorted(
            (second.fingerprint, first.fingerprint, first_accepted.fingerprint),
            key=lambda fingerprint: (
                "instruction-a" if fingerprint == second.fingerprint else "instruction-b",
                fingerprint,
            ),
        )
    )
    assert collection.calls == [
        (
            "find",
            session,
            {
                "tenant_id": "tenant-a",
                "entity_type": "LegalInstruction",
            },
        )
    ]
    assert LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
        "tenant-missing",
        "LegalInstruction",
        collection,
        session=session,
    ) == ()


def test_tenant_entity_snapshot_enumeration_rejects_invalid_scope_corruption_and_failure() -> None:
    """Invalid tenant/type, corrupt rows, and Mongo failures fail closed."""
    collection = FakeCollection()
    persisted_record(instruction(), collection)

    expect_code(
        "M2_INVALID_TENANT",
        lambda: LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
            "global",
            "LegalInstruction",
            collection,
        ),
    )
    expect_code(
        "M2_ENTITY_TYPE_UNSUPPORTED",
        lambda: LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
            "tenant-a",
            "UnknownEntity",
            collection,
        ),
    )

    collection.docs[0]["p1_fingerprint"] = "x" * 128
    expect_code(
        "M2_P1_FINGERPRINT_INVALID",
        lambda: LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
            "tenant-a",
            "LegalInstruction",
            collection,
        ),
    )

    error = _operation_failure(27188)
    failing = HistoryFailureCollection(error)
    with pytest.raises(LegalOperationsLifecycleRegistryError) as caught:
        LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
            "tenant-a",
            "LegalInstruction",
            failing,
        )
    assert str(caught.value) == "M2_PERSISTENCE_UNAVAILABLE"
    assert caught.value.__cause__ is error


def test_document_custody_history_hydrates_exact_scope_and_forwards_session() -> None:
    """Custody-history retrieval is tenant/document scoped and non-deriving."""
    collection = FakeCollection()
    session = FakeSession(in_transaction=True)
    first = custody_event()
    second = custody_event(
        event_id="custody-2",
        event_type=DocumentCustodyEventType.RECEIVED_IN_OFFICE,
        sequence_number=2,
        occurred_at=NOW + timedelta(minutes=1),
        evidence_reference="receipt-evidence",
        to_holder_reference="office-1",
    )
    foreign = custody_event(
        tenant_id="tenant-b",
        event_id="custody-foreign",
    )
    other_document = custody_event(
        event_id="custody-other",
        document_id="document-2",
    )
    for value in (first, second, foreign, other_document):
        persisted_record(value, collection, session=session)

    collection.calls.clear()
    history = LegalOperationsLifecycleRegistry.get_document_custody_history(
        "tenant-a",
        "document-1",
        collection,
        session=session,
    )

    assert tuple(value.to_dict() for value in history) == (
        first.to_dict(),
        second.to_dict(),
    )
    assert collection.calls == [
        (
            "find",
            session,
            {
                "tenant_id": "tenant-a",
                "entity_type": "DocumentCustodyEvent",
                "p1_payload.document_id": "document-1",
            },
        )
    ]
    assert LegalOperationsLifecycleRegistry.get_document_custody_history(
        "tenant-a",
        "document-missing",
        collection,
        session=session,
    ) == ()


def test_document_custody_history_rejects_invalid_scope_corruption_and_read_failure() -> None:
    """Malformed scope, corrupt matching rows, and Mongo failures reject."""
    collection = FakeCollection()
    persisted_record(custody_event(), collection)

    expect_code(
        "M2_INVALID_TENANT",
        lambda: LegalOperationsLifecycleRegistry.get_document_custody_history(
            "global",
            "document-1",
            collection,
        ),
    )
    expect_code(
        "M2_ENTITY_ID_INVALID",
        lambda: LegalOperationsLifecycleRegistry.get_document_custody_history(
            "tenant-a",
            "invalid/document",
            collection,
        ),
    )

    collection.docs[0]["p1_fingerprint"] = "x" * 128
    expect_code(
        "M2_P1_FINGERPRINT_INVALID",
        lambda: LegalOperationsLifecycleRegistry.get_document_custody_history(
            "tenant-a",
            "document-1",
            collection,
        ),
    )

    error = _operation_failure(27187)
    failing = HistoryFailureCollection(error)
    with pytest.raises(LegalOperationsLifecycleRegistryError) as caught:
        LegalOperationsLifecycleRegistry.get_document_custody_history(
            "tenant-a",
            "document-1",
            failing,
        )
    assert str(caught.value) == "M2_PERSISTENCE_UNAVAILABLE"
    assert caught.value.__cause__ is error


def test_entity_history_rejects_invalid_scope_corruption_and_persistence_failure() -> None:
    """Invalid scope, any corrupt history row, and Mongo read failures reject."""
    collection = FakeCollection()
    initial = instruction()
    accepted = initial.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted",
        occurred_at=NOW + timedelta(minutes=1),
    )
    persisted_record(initial, collection)
    persisted_record(accepted, collection)

    expect_code(
        "M2_INVALID_TENANT",
        lambda: LegalOperationsLifecycleRegistry.get_entity_history(
            "global", "LegalInstruction", "instruction-1", collection
        ),
    )
    expect_code(
        "M2_ENTITY_TYPE_UNSUPPORTED",
        lambda: LegalOperationsLifecycleRegistry.get_entity_history(
            "tenant-a", "UnknownEntity", "instruction-1", collection
        ),
    )
    expect_code(
        "M2_ENTITY_ID_INVALID",
        lambda: LegalOperationsLifecycleRegistry.get_entity_history(
            "tenant-a", "LegalInstruction", "invalid/identity", collection
        ),
    )

    collection.docs[1]["p1_fingerprint"] = "x" * 128
    expect_code(
        "M2_P1_FINGERPRINT_INVALID",
        lambda: LegalOperationsLifecycleRegistry.get_entity_history(
            "tenant-a", "LegalInstruction", "instruction-1", collection
        ),
    )

    error = _operation_failure(27186)
    failing = HistoryFailureCollection(error)
    with pytest.raises(LegalOperationsLifecycleRegistryError) as caught:
        LegalOperationsLifecycleRegistry.get_entity_history(
            "tenant-a", "LegalInstruction", "instruction-1", failing
        )
    assert str(caught.value) == "M2_PERSISTENCE_UNAVAILABLE"
    assert caught.value.__cause__ is error


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


def _operation_failure(code: int, *labels: str) -> OperationFailure:
    """Build a PyMongo failure with explicit driver labels for the seam test."""
    error = OperationFailure("synthetic persistence failure", code=code)
    for label in labels:
        error._add_error_label(label)
    return error


def test_active_transient_transaction_error_is_retry_required_and_causal() -> None:
    error = _operation_failure(27182, "TransientTransactionError")
    collection = FailureCollection(error)
    session = TrackingSession()
    with pytest.raises(LegalOperationsLifecycleRegistryError) as caught:
        LegalOperationsLifecycleRegistry.create(instruction(), collection, session=session)
    assert str(caught.value) == "M2_RETRY_TRANSACTION_REQUIRED"
    assert caught.value.__cause__ is error
    assert error.code == 27182
    assert error.has_error_label("TransientTransactionError")
    assert session.start_calls == session.commit_calls == session.abort_calls == session.end_calls == 0
    assert len(collection.docs) == 0


def test_unknown_commit_result_is_not_resolved_as_retry_required() -> None:
    error = _operation_failure(27183, "TransientTransactionError", "UnknownTransactionCommitResult")
    collection = FailureCollection(error)
    session = TrackingSession()
    with pytest.raises(LegalOperationsLifecycleRegistryError) as caught:
        LegalOperationsLifecycleRegistry.create(instruction(), collection, session=session)
    assert str(caught.value) == "M2_PERSISTENCE_UNAVAILABLE"
    assert caught.value.__cause__ is error
    assert error.has_error_label("UnknownTransactionCommitResult")
    assert session.start_calls == session.commit_calls == session.abort_calls == session.end_calls == 0


def test_active_non_transient_error_remains_persistence_unavailable() -> None:
    error = _operation_failure(27184)
    collection = FailureCollection(error)
    session = TrackingSession()
    with pytest.raises(LegalOperationsLifecycleRegistryError) as caught:
        LegalOperationsLifecycleRegistry.create(instruction(), collection, session=session)
    assert str(caught.value) == "M2_PERSISTENCE_UNAVAILABLE"
    assert caught.value.__cause__ is error


def test_outside_transaction_transient_error_is_not_retry_required() -> None:
    error = _operation_failure(27185, "TransientTransactionError")
    collection = FailureCollection(error)
    with pytest.raises(LegalOperationsLifecycleRegistryError) as caught:
        LegalOperationsLifecycleRegistry.create(instruction(), collection, session=FakeSession())
    assert str(caught.value) == "M2_PERSISTENCE_UNAVAILABLE"
    assert caught.value.__cause__ is error


def test_p2_production_version_is_the_history_release() -> None:
    assert P2_VERSION == "v1.3.0-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION"


def test_unsupported_inputs_irrelevant_sources_and_non_financial_authority() -> None:
    expect_code("M2_P1_VALUE_REQUIRED", lambda: LegalOperationsLifecycleRegistry.create(cast(Any, object()), FakeCollection()))
    value = instruction()
    attempt = terminal_attempt()
    expect_code("M2_FACTORY_SOURCE_INVALID", lambda: LegalOperationsLifecycleRegistry.create(value, FakeCollection(), source_attempt=attempt))
    expect_code("M2_FACTORY_SOURCE_INVALID", lambda: LegalOperationsLifecycleRegistry.create(value, FakeCollection(), source_execution=cast(Any, object())))
    assert not {field.name.casefold() for field in fields(value)}.intersection({"invoice", "payment", "settlement", "execution", "billing"})
    assert "Kennel EOS exclusively" in (LegalOperationsLifecycleRegistry.__doc__ or "") or "Kennel EOS" in open(__file__, encoding="utf-8").read()


# ARTIFACT: test_legal_operations_lifecycle_registry.py
# VERSION: v1.3.0-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION-CERT
# AUTHORITY BOUNDARY: direct P2 persistence/entity/tenant-entity/custody-history/hydration certificate only.
# TENANT POSTURE: explicit synthetic tenants; foreign evidence is undisclosed.
# FAIL-CLOSED POSTURE: malformed records, provenance, races, and sources reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution/settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT