"""Direct adversarial certificate for the Legal P4A allocation orchestrator.

TITLE: Wilsy OS Process Service Allocation Orchestrator Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify deterministic composition of validated P1/P3 evidence,
         P2 immutable snapshots, and P4B receipt/current CAS without creating
         service, transport, IAM, invoice, payment, or settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_allocation_orchestrator.py
COLLABORATION / OWNERSHIP: Direct P4A unit certificate; P1 remains lifecycle
                            and custody authority, P2 remains durable evidence
                            persistence, P3 remains assignment authority, and
                            P4B remains allocation receipt/current authority.
                            The caller owns session and transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR-CERT
           certifies created allocation, exact replay, source binding,
           custody chronology, durable-current preflight, and fail-closed
           partial replay behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every fixture, query, replay, P2 identity, custody event,
                 and current pointer is explicitly tenant/document scoped.
AUTHORITY BOUNDARY: Certificate scope is P4A composition evidence only; no
                    test helper grants assignment, custody, service, IAM, or
                    transport authority.
FINANCIAL AUTHORITY BOUNDARY: Allocation is not invoicing, payment,
                              execution, or settlement; Kennel EOS exclusively
                              owns financial execution and settlement.
FAIL-CLOSED DECLARATION: The certificate rejects malformed source values,
                         tenant/lineage mismatches, history gaps, chronology
                         failures, replay divergence, stale currentness,
                         corruption, and upstream errors without weakening
                         production contracts.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import json
from typing import Any, Callable

import pytest
from pymongo.errors import AutoReconnect

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    District,
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    LegalInstructionState,
    ProcessDocument,
    ProcessDocumentState,
    SheriffOffice,
)
from tools.eos.legal_operations.domain.process_service_assignment_authority import (
    authorize_process_service_assignment,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistryError,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationPersistenceOutcome,
    ProcessServiceAllocationPersistenceResult,
    ProcessServiceAllocationRegistryCurrentPointerConflictError,
    ProcessServiceAllocationRegistryCurrentPointerMissingError,
    ProcessServiceAllocationRegistryPersistenceUnavailableError,
)
from tools.eos.legal_operations.orchestration import process_service_allocation_orchestrator as orchestrator


VERSION = "v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR-CERT"
BASE = datetime(2026, 9, 14, 9, 0, tzinfo=timezone.utc)
TENANT = "tenant-p4a-certificate"
OTHER_TENANT = "tenant-p4a-other"
HEX_A = "a" * 128
HEX_B = "b" * 128


class _Cursor:
    """Minimal Mongo-compatible cursor whose iteration is deterministic."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def limit(self, amount: int) -> "_Cursor":
        return _Cursor(self._rows[:amount])

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self._rows)


class _WriteResult:
    def __init__(self, matched_count: int) -> None:
        self.matched_count = matched_count


class _Session:
    """Caller-owned session; P4A lifecycle takeover is a test failure."""

    def __init__(self, marker: bool | Callable[[], bool] = True) -> None:
        self.in_transaction = marker
        self.lifecycle_calls: list[str] = []

    def start_transaction(self) -> None:
        self.lifecycle_calls.append("start")
        raise AssertionError("P4A must not start transactions")

    def commit_transaction(self) -> None:
        self.lifecycle_calls.append("commit")
        raise AssertionError("P4A must not commit transactions")

    def abort_transaction(self) -> None:
        self.lifecycle_calls.append("abort")
        raise AssertionError("P4A must not abort transactions")


class _Collection:
    """Deterministic in-memory collection preserving every supplied session."""

    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.rows = rows or []
        self.sessions: list[object] = []
        self.operations: list[str] = []
        self.inserted: list[dict[str, Any]] = []
        self.updated: list[dict[str, Any]] = []
        self.find_error: BaseException | None = None
        self.insert_error: BaseException | None = None

    @staticmethod
    def _matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def find_one(self, query: dict[str, Any], *, session: object = None) -> dict[str, Any] | None:
        self.sessions.append(session)
        self.operations.append("find_one")
        if self.find_error is not None:
            raise self.find_error
        return next((row for row in self.rows if self._matches(row, query)), None)

    def find(self, query: dict[str, Any], *, session: object = None) -> _Cursor:
        self.sessions.append(session)
        self.operations.append("find")
        if self.find_error is not None:
            raise self.find_error
        return _Cursor([row for row in self.rows if self._matches(row, query)])

    def insert_one(self, record: dict[str, Any], *, session: object = None) -> object:
        self.sessions.append(session)
        self.operations.append("insert_one")
        if self.insert_error is not None:
            raise self.insert_error
        stored = dict(record)
        self.rows.append(stored)
        self.inserted.append(stored)
        return object()

    def update_one(
        self,
        query: dict[str, Any],
        update: dict[str, Any],
        *,
        session: object = None,
    ) -> _WriteResult:
        self.sessions.append(session)
        self.operations.append("update_one")
        row = next((item for item in self.rows if self._matches(item, query)), None)
        if row is None:
            return _WriteResult(0)
        replacement = update.get("$set")
        if not isinstance(replacement, dict):
            raise AssertionError("test collection received an unsupported update")
        row.clear()
        row.update(replacement)
        self.updated.append(dict(replacement))
        return _WriteResult(1)


class _Fixture:
    def __init__(self, *, suffix: str = "", tenant: str = TENANT) -> None:
        self.tenant = tenant
        self.session = _Session(True)
        self.lifecycle = _Collection()
        self.receipts = _Collection()
        self.current = _Collection()
        instruction_id = f"instruction-{suffix or '1'}"
        matter_id = f"matter-{suffix or '1'}"
        document_id = f"document-{suffix or '1'}"
        district_id = f"district-{suffix or '1'}"
        office_id = f"office-{suffix or '1'}"
        deputy_id = f"deputy-{suffix or '1'}"
        registered_instruction = LegalInstruction(tenant, instruction_id, matter_id, document_id, BASE, "instruction-registration")
        self.instruction = registered_instruction.transition_to(
            LegalInstructionState.ACCEPTED,
            evidence_reference="instruction-acceptance",
            occurred_at=BASE + timedelta(minutes=1),
        )
        registered_document = ProcessDocument(tenant, document_id, matter_id, "summons", BASE, "document-registration")
        self.document = registered_document.transition_to(
            ProcessDocumentState.RECEIVED,
            evidence_reference="document-receipt",
            occurred_at=BASE + timedelta(minutes=1),
        )
        self.district = District(tenant, district_id, "Central District", "ZA-GP-1", "district-evidence")
        self.office = SheriffOffice(tenant, office_id, district_id, "Central Office", "office-evidence")
        self.deputy = Deputy(tenant, deputy_id, office_id, "Deputy One", "badge-1", "deputy-evidence")
        self.decision = authorize_process_service_assignment(
            instruction=self.instruction,
            document=self.document,
            district=self.district,
            sheriff_office=self.office,
            deputy=self.deputy,
            assignment_decision_id=f"assignment-{suffix or '1'}",
            assignment_evidence_reference="assignment-evidence",
            decided_at=BASE + timedelta(minutes=2),
        )
        self.registered_event = DocumentCustodyEvent(tenant, f"custody-registered-{suffix or '1'}", document_id, DocumentCustodyEventType.REGISTERED, BASE, 1, "custody-registration")
        self.received_event = DocumentCustodyEvent(tenant, f"custody-received-{suffix or '1'}", document_id, DocumentCustodyEventType.RECEIVED_IN_OFFICE, BASE + timedelta(minutes=1), 2, "custody-receipt", "client-holder", office_id)
        self.prior_events = (self.registered_event, self.received_event)
        self.prior_chain_fingerprint = _chain_fingerprint(tenant, document_id, self.prior_events)
        self.expected_current = ProcessServiceAllocationCurrent(
            tenant_id=tenant,
            document_id=document_id,
            process_document_fingerprint=self.document.fingerprint,
            custody_chain_fingerprint=self.prior_chain_fingerprint,
            custody_head_event_id=self.received_event.custody_event_id,
            custody_head_fingerprint=self.received_event.fingerprint,
            custody_head_sequence_number=2,
            current_holder_reference=office_id,
            authority_evidence_reference="migration-head",
            authority_evidence_fingerprint=HEX_A,
        )
        self.current.rows.append(self.expected_current.to_dict())
        self.values: dict[str, Any] = {
            "instruction": self.instruction,
            "document": self.document,
            "district": self.district,
            "sheriff_office": self.office,
            "deputy": self.deputy,
            "assignment_decision": self.decision,
            "prior_custody_events": self.prior_events,
            "expected_prior_current": self.expected_current,
            "allocation_command_id": f"allocation-command-{suffix or '1'}",
            "idempotency_key": f"allocation-idempotency-{suffix or '1'}",
            "allocation_custody_event_id": f"custody-allocation-{suffix or '1'}",
            "allocation_evidence_reference": "allocation-evidence",
            "allocated_at": BASE + timedelta(minutes=3),
            "lifecycle_collection": self.lifecycle,
            "allocation_receipt_collection": self.receipts,
            "allocation_current_collection": self.current,
            "session": self.session,
        }

    def call(self, **overrides: Any) -> orchestrator.ProcessServiceAllocationOrchestrationResult:
        values = dict(self.values)
        values.update(overrides)
        return orchestrator.orchestrate_process_service_allocation(**values)

    def total_writes(self) -> int:
        return len(self.lifecycle.inserted) + len(self.receipts.inserted) + len(self.current.updated)


def _sha3(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _chain_fingerprint(tenant: str, document_id: str, events: tuple[DocumentCustodyEvent, ...]) -> str:
    return _sha3({"schema": orchestrator.CUSTODY_CHAIN_SCHEMA, "tenant_id": tenant, "document_id": document_id, "event_fingerprints": [event.fingerprint for event in events]})


def _assert_code(fixture: _Fixture, code: str, **overrides: Any) -> None:
    with pytest.raises(orchestrator.ProcessServiceAllocationOrchestratorError) as caught:
        fixture.call(**overrides)
    assert caught.value.code == code


def _p2_identity(value: ProcessDocument | DocumentCustodyEvent) -> str:
    identity = value.document_id if isinstance(value, ProcessDocument) else value.custody_event_id
    return _sha3({"tenant_id": value.tenant_id, "entity_type": type(value).__name__, "entity_identity": identity, "p1_fingerprint": value.fingerprint, "source_fingerprint": None})


def test_version_and_public_result_surface() -> None:
    assert VERSION == "v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR-CERT"
    assert orchestrator.VERSION == "v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR"
    parameters = set(inspect.signature(orchestrator.orchestrate_process_service_allocation).parameters)
    forbidden = {"allocated_document_fingerprint", "allocation_event_fingerprint", "result_custody_chain_fingerprint", "from_holder_reference", "to_holder_reference", "next_current"}
    assert parameters.isdisjoint(forbidden)


def test_created_happy_path_derives_document_event_chain_and_current() -> None:
    fixture = _Fixture()
    result = fixture.call()
    assert result.allocated_document.state is ProcessDocumentState.ALLOCATED_TO_DEPUTY
    assert result.allocated_document.transition_history[-1].resulting_state is ProcessDocumentState.ALLOCATED_TO_DEPUTY
    event = result.allocation_custody_event
    assert event.event_type is DocumentCustodyEventType.ALLOCATED_TO_DEPUTY
    assert event.sequence_number == 3
    assert event.from_holder_reference == fixture.office.sheriff_office_id
    assert event.to_holder_reference == fixture.deputy.deputy_id
    assert result.result_custody_chain == fixture.prior_events + (event,)
    assert result.persistence_result.outcome is ProcessServiceAllocationPersistenceOutcome.CREATED
    assert result.persistence_result.current.current_holder_reference == fixture.deputy.deputy_id
    assert len(fixture.lifecycle.rows) == 2
    assert {row["entity_type"] for row in fixture.lifecycle.rows} == {"ProcessDocument", "DocumentCustodyEvent"}
    assert len(fixture.receipts.rows) == 1


def test_exact_idempotent_replay_has_no_second_row_and_preserves_inputs() -> None:
    fixture = _Fixture()
    before = dict(fixture.values)
    created = fixture.call()
    counts = (len(fixture.lifecycle.rows), len(fixture.receipts.rows), len(fixture.current.updated))
    replay = fixture.call()
    assert replay.persistence_result.outcome is ProcessServiceAllocationPersistenceOutcome.IDEMPOTENT_REPLAY
    assert replay.persistence_result.receipt.to_dict() == created.persistence_result.receipt.to_dict()
    assert replay.persistence_result.current.to_dict() == created.persistence_result.current.to_dict()
    assert (len(fixture.lifecycle.rows), len(fixture.receipts.rows), len(fixture.current.updated)) == counts
    assert fixture.values == before


@pytest.mark.parametrize("marker", [False, lambda: False])
def test_inactive_transaction_rejects_before_any_read_or_write(marker: bool | Callable[[], bool]) -> None:
    fixture = _Fixture()
    fixture.session = _Session(marker)
    fixture.values["session"] = fixture.session
    _assert_code(fixture, "P4A_ACTIVE_TRANSACTION_REQUIRED")
    assert fixture.total_writes() == 0
    assert not fixture.lifecycle.operations and not fixture.receipts.operations and not fixture.current.operations


def test_none_transaction_rejects_and_callable_active_succeeds() -> None:
    fixture = _Fixture()
    _assert_code(fixture, "P4A_ACTIVE_TRANSACTION_REQUIRED", session=None)
    fixture.session = _Session(lambda: True)
    fixture.values["session"] = fixture.session
    assert fixture.call().persistence_result.outcome is ProcessServiceAllocationPersistenceOutcome.CREATED
    assert fixture.session.lifecycle_calls == []


def test_same_session_reaches_every_p2_and_p4b_operation() -> None:
    fixture = _Fixture()
    fixture.call()
    assert fixture.lifecycle.sessions and all(item is fixture.session for item in fixture.lifecycle.sessions)
    assert fixture.receipts.sessions and all(item is fixture.session for item in fixture.receipts.sessions)
    assert fixture.current.sessions and all(item is fixture.session for item in fixture.current.sessions)
    assert fixture.session.lifecycle_calls == []


def test_tenant_and_lineage_failures_are_before_writes() -> None:
    fixture = _Fixture()
    _assert_code(fixture, "P4A_DOCUMENT_INVALID", document=object())
    assert fixture.total_writes() == 0
    fixture = _Fixture()
    _assert_code(fixture, "P4A_TENANT_MISMATCH", document=replace(fixture.document, tenant_id=OTHER_TENANT))
    fixture = _Fixture()
    _assert_code(fixture, "P4A_INSTRUCTION_DOCUMENT_MISMATCH", document=replace(fixture.document, document_id="other-document"))
    fixture = _Fixture()
    registered_instruction = LegalInstruction(TENANT, "instruction-1", "matter-1", "document-1", BASE, "registration")
    _assert_code(fixture, "P4A_INSTRUCTION_NOT_ACCEPTED", instruction=registered_instruction)
    fixture = _Fixture()
    registered_document = ProcessDocument(TENANT, "document-1", "matter-1", "summons", BASE, "registration")
    _assert_code(fixture, "P4A_DOCUMENT_NOT_RECEIVED", document=registered_document)
    fixture = _Fixture()
    _assert_code(fixture, "P4A_DISTRICT_OFFICE_LINEAGE_MISMATCH", sheriff_office=replace(fixture.office, district_id="other-district"))
    fixture = _Fixture()
    _assert_code(fixture, "P4A_OFFICE_DEPUTY_LINEAGE_MISMATCH", deputy=replace(fixture.deputy, sheriff_office_id="other-office"))


def test_malformed_exact_source_revalidation_fails_governed() -> None:
    fixture = _Fixture()
    object.__setattr__(fixture.document, "transition_history", None)
    _assert_code(fixture, "P4A_DOCUMENT_INVALID")
    fixture = _Fixture()
    object.__setattr__(fixture.decision, "assignment_decision_id", "corrupted")
    _assert_code(fixture, "P4A_ASSIGNMENT_DECISION_INVALID")


def test_p3_source_binding_rejects_legitimate_alternative_evidence() -> None:
    fixture = _Fixture()
    altered = ProcessDocument(TENANT, "document-1", "matter-1", "summons", BASE, "different-registration").transition_to(
        ProcessDocumentState.RECEIVED,
        evidence_reference="different-receipt",
        occurred_at=BASE + timedelta(minutes=1),
    )
    _assert_code(fixture, "P4A_ASSIGNMENT_SOURCE_BINDING_INVALID", document=altered)
    fixture = _Fixture()
    alternate = _Fixture(suffix="2")
    _assert_code(fixture, "P4A_ASSIGNMENT_SOURCE_BINDING_INVALID", district=alternate.district, sheriff_office=alternate.office, deputy=alternate.deputy)
    assert fixture.total_writes() == 0


@pytest.mark.parametrize(
    "field",
    [
        "instruction_id",
        "case_matter_id",
        "document_id",
        "district_id",
        "sheriff_office_id",
        "deputy_id",
        "instruction_fingerprint",
        "document_fingerprint",
        "district_fingerprint",
        "sheriff_office_fingerprint",
        "deputy_fingerprint",
    ],
)
def test_every_p3_identity_and_fingerprint_binding_is_fail_closed(field: str) -> None:
    fixture = _Fixture()
    alternate = _Fixture(suffix="2")
    assert getattr(alternate.decision, field) != getattr(fixture.decision, field)
    _assert_code(fixture, "P4A_ASSIGNMENT_SOURCE_BINDING_INVALID", assignment_decision=alternate.decision)
    assert fixture.total_writes() == 0


@pytest.mark.parametrize(
    "kind,code",
    [
        ("empty", "P4A_PRIOR_CUSTODY_CHAIN_INVALID"),
        ("wrong-tenant", "P4A_PRIOR_CUSTODY_CHAIN_INVALID"),
        ("noncontiguous", "P4A_PRIOR_CUSTODY_CHAIN_INVALID"),
        ("duplicate", "P4A_PRIOR_CUSTODY_CHAIN_INVALID"),
        ("chronology", "P4A_PRIOR_CUSTODY_CHAIN_INVALID"),
        ("head-type", "P4A_PRIOR_CUSTODY_HEAD_INVALID"),
        ("head-holder", "P4A_PRIOR_CUSTODY_HEAD_INVALID"),
    ],
)
def test_prior_custody_and_holder_head_fail_closed(kind: str, code: str) -> None:
    fixture = _Fixture()
    prior = fixture.prior_events
    if kind == "empty":
        prior = ()
    elif kind == "wrong-tenant":
        prior = (prior[0], replace(prior[1], tenant_id=OTHER_TENANT))
    elif kind == "noncontiguous":
        prior = (prior[0], replace(prior[1], sequence_number=4))
    elif kind == "duplicate":
        prior = (prior[0], replace(prior[1], custody_event_id=prior[0].custody_event_id))
    elif kind == "chronology":
        prior = (prior[0], replace(prior[1], occurred_at=BASE - timedelta(seconds=1)))
    elif kind == "head-type":
        prior = (prior[0], replace(prior[1], event_type=DocumentCustodyEventType.TRANSFERRED))
    elif kind == "head-holder":
        prior = (prior[0], replace(prior[1], to_holder_reference="other-office"))
    _assert_code(fixture, code, prior_custody_events=prior)
    assert fixture.total_writes() == 0


@pytest.mark.parametrize(
    "field,code",
    [
        ("tenant_id", "P4A_EXPECTED_CURRENT_CORRELATION_INVALID"),
        ("document_id", "P4A_EXPECTED_CURRENT_CORRELATION_INVALID"),
        ("process_document_fingerprint", "P4A_EXPECTED_CURRENT_CORRELATION_INVALID"),
        ("custody_head_event_id", "P4A_EXPECTED_CURRENT_CORRELATION_INVALID"),
        ("custody_head_fingerprint", "P4A_EXPECTED_CURRENT_CORRELATION_INVALID"),
        ("custody_head_sequence_number", "P4A_EXPECTED_CURRENT_CORRELATION_INVALID"),
        ("current_holder_reference", "P4A_EXPECTED_CURRENT_CORRELATION_INVALID"),
        ("custody_chain_fingerprint", "P4A_PRIOR_CUSTODY_FINGERPRINT_INVALID"),
    ],
)
def test_expected_current_and_chain_binding_fail_closed(field: str, code: str) -> None:
    fixture = _Fixture()
    replacements: dict[str, object] = {
        "tenant_id": OTHER_TENANT,
        "document_id": "other-document",
        "process_document_fingerprint": HEX_B,
        "custody_head_event_id": "other-head",
        "custody_head_fingerprint": HEX_B,
        "custody_head_sequence_number": 9,
        "current_holder_reference": "other-holder",
        "custody_chain_fingerprint": HEX_B,
    }
    _assert_code(fixture, code, expected_prior_current=replace(fixture.expected_current, **{field: replacements[field]}))
    assert fixture.total_writes() == 0


@pytest.mark.parametrize(
    "allocated_at,code",
    [
        (datetime(2026, 9, 14, 9, 3), "P4A_ALLOCATED_AT_INVALID"),
        (datetime(2026, 9, 14, 11, 3, tzinfo=timezone(timedelta(hours=2))), "P4A_ALLOCATED_AT_INVALID"),
        (BASE - timedelta(seconds=1), "P4A_ALLOCATION_CHRONOLOGY_INVALID"),
        (BASE + timedelta(seconds=30), "P4A_ALLOCATION_CHRONOLOGY_INVALID"),
        (BASE + timedelta(minutes=1, seconds=30), "P4A_ALLOCATION_CHRONOLOGY_INVALID"),
        (BASE + timedelta(minutes=1, seconds=59), "P4A_ALLOCATION_CHRONOLOGY_INVALID"),
    ],
)
def test_allocation_chronology_is_explicit_utc_and_monotonic(allocated_at: datetime, code: str) -> None:
    fixture = _Fixture()
    _assert_code(fixture, code, allocated_at=allocated_at)
    assert fixture.total_writes() == 0


def test_custody_chain_digest_and_result_digest_are_deterministic() -> None:
    fixture = _Fixture()
    result = fixture.call()
    expected = _chain_fingerprint(TENANT, fixture.document.document_id, fixture.prior_events)
    assert result.persistence_result.receipt.prior_custody_chain_fingerprint == expected
    changed = _Fixture()
    changed.values["allocation_custody_event_id"] = "different-event"
    changed_result = changed.call()
    assert changed_result.persistence_result.receipt.result_custody_chain_fingerprint != result.persistence_result.receipt.result_custody_chain_fingerprint


def test_p2_identity_formula_is_used_for_both_derived_facts() -> None:
    fixture = _Fixture()
    result = fixture.call()
    allocated_document = fixture.document.transition_to(ProcessDocumentState.ALLOCATED_TO_DEPUTY, evidence_reference="allocation-evidence", occurred_at=BASE + timedelta(minutes=3))
    allocated_event = DocumentCustodyEvent(TENANT, "custody-allocation-1", "document-1", DocumentCustodyEventType.ALLOCATED_TO_DEPUTY, BASE + timedelta(minutes=3), 3, "allocation-evidence", "office-1", "deputy-1")
    identities = {row["evidence_identity"] for row in fixture.lifecycle.rows}
    assert _p2_identity(allocated_document) in identities
    assert _p2_identity(allocated_event) in identities
    assert result.allocated_document.fingerprint == allocated_document.fingerprint
    assert result.allocation_custody_event.fingerprint == allocated_event.fingerprint


def test_receipt_present_missing_result_never_heals() -> None:
    fixture = _Fixture()
    fixture.call()
    fixture.lifecycle.rows.pop(0)
    before = len(fixture.lifecycle.inserted)
    _assert_code(fixture, "P4A_PARTIAL_REPLAY")
    assert len(fixture.lifecycle.inserted) == before


def test_receipt_present_corrupt_result_fails_without_healing() -> None:
    fixture = _Fixture()
    fixture.call()
    fixture.lifecycle.rows[0]["p1_payload"]["document_type"] = "corrupt"
    with pytest.raises(LegalOperationsLifecycleRegistryError):
        fixture.call()
    assert len(fixture.lifecycle.inserted) == 2


def test_receipt_present_divergent_receipt_fails_without_p2_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _Fixture()
    receipt = fixture.call().persistence_result.receipt
    before = fixture.total_writes()
    divergent = replace(receipt, allocation_command_id="different-command")
    monkeypatch.setattr(
        orchestrator.ProcessServiceAllocationRegistry,
        "get_receipt_by_idempotency_key",
        staticmethod(lambda *args, **kwargs: divergent),
    )
    _assert_code(fixture, "P4A_REPLAY_RECEIPT_DIVERGENCE")
    assert fixture.total_writes() == before


@pytest.mark.parametrize("keep", ["document", "event", "both"])
def test_receipt_absent_partial_state_never_finishes(keep: str) -> None:
    fixture = _Fixture()
    fixture.call()
    fixture.receipts.rows.clear()
    if keep == "document":
        fixture.lifecycle.rows.pop()
    elif keep == "event":
        fixture.lifecycle.rows.pop(0)
    before = fixture.total_writes()
    _assert_code(fixture, "P4A_PARTIAL_REPLAY")
    assert fixture.total_writes() == before


def test_durable_current_preflight_precedes_all_p2_writes() -> None:
    fixture = _Fixture()
    fixture.current.rows[0]["authority_evidence_reference"] = "different-current"
    before = fixture.total_writes()
    _assert_code(fixture, "P4A_EXPECTED_CURRENT_DURABLE_MISMATCH")
    assert fixture.total_writes() == before
    assert fixture.current.operations[-1] == "find"
    assert "insert_one" not in fixture.lifecycle.operations


def test_p4b_current_read_errors_preserve_upstream_governed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _Fixture()
    error = ProcessServiceAllocationRegistryCurrentPointerMissingError()
    monkeypatch.setattr(orchestrator.ProcessServiceAllocationRegistry, "get_current", staticmethod(lambda *a, **k: (_ for _ in ()).throw(error)))
    with pytest.raises(ProcessServiceAllocationRegistryCurrentPointerMissingError) as caught:
        fixture.call()
    assert caught.value.code == "P4_CURRENT_POINTER_MISSING"
    assert fixture.total_writes() == 0


def test_p2_create_return_divergence_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _Fixture()
    calls = 0

    def divergent(value: object, collection: object, *, session: object = None) -> object:
        nonlocal calls
        calls += 1
        return object()

    monkeypatch.setattr(orchestrator.LegalOperationsLifecycleRegistry, "create", staticmethod(divergent))
    _assert_code(fixture, "P4A_P2_DOCUMENT_DIVERGENCE")
    assert calls == 2


def test_p4b_conflict_and_persistence_errors_are_not_converted_to_success(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _Fixture()
    conflict = ProcessServiceAllocationRegistryCurrentPointerConflictError()
    monkeypatch.setattr(orchestrator.ProcessServiceAllocationRegistry, "persist_receipt_and_advance_current", staticmethod(lambda *a, **k: (_ for _ in ()).throw(conflict)))
    with pytest.raises(ProcessServiceAllocationRegistryCurrentPointerConflictError):
        fixture.call()
    fixture = _Fixture()
    fixture.receipts.find_error = AutoReconnect("outage")
    with pytest.raises(ProcessServiceAllocationRegistryPersistenceUnavailableError):
        fixture.call()


def test_result_authority_separation_and_no_financial_surface() -> None:
    fixture = _Fixture()
    result = fixture.call()
    assert set(result.to_dict()) == {"allocated_document", "allocation_custody_event", "result_custody_chain", "persistence_result"}
    serialized = json.dumps(result.to_dict(), sort_keys=True)
    for forbidden in ("ServiceAttempt", "ServiceExecution", "ReturnOfService", "invoice", "payment", "settlement", "paid_state"):
        assert forbidden not in serialized
    assert not hasattr(orchestrator, "start_transaction")
    assert not hasattr(orchestrator, "commit_transaction")
    assert not hasattr(orchestrator, "abort_transaction")


def test_public_operation_does_not_own_transaction_or_mongo_client() -> None:
    assert "mongo_client" not in inspect.signature(orchestrator.orchestrate_process_service_allocation).parameters
    assert "client" not in orchestrator.__dict__


# ARTIFACT: test_process_service_allocation_orchestrator.py
# VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR-CERT
# AUTHORITY BOUNDARY: direct P4A composition certificate only.
# TENANT POSTURE: deterministic tenant-scoped fake persistence; no foreign disclosure.
# FAIL-CLOSED POSTURE: source, custody, chronology, replay, currentness, and upstream errors are asserted.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
