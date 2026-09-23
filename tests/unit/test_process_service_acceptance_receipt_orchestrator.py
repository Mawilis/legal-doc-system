"""Direct certificate for Legal Operations acceptance and office receipt.

TITLE: WILSY OS Process Service Acceptance and Receipt Direct Certificate
VERSION: v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-CERT
AUTHORITY: Direct certificate for L8-3 instruction acceptance and office receipt only.
EPITOME: Prove active-transaction LegalInstruction ACCEPTED, ProcessDocument
         RECEIVED, sequence-two RECEIVED_IN_OFFICE custody, canonical
         SheriffOffice binding, exact replay, progressed-history replay,
         partial/divergent-state rejection, chronology, tenant isolation,
         caller-session propagation, and non-financial authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_acceptance_receipt_orchestrator.py
COLLABORATION / OWNERSHIP: Certificate for
                            process_service_acceptance_receipt_orchestrator.py;
                            P1/P2/L8-0 remain independent canonical authorities,
                            L8-1 owns directory truth, L8-2 owns registration,
                            and authenticated transport remains a later gate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-CERT
           establishes adversarial direct evidence for acceptance plus office
           receipt, exact replay after later valid progression, partial and
           divergent durable state rejection, timestamp validation, foreign
           office non-disclosure, exact caller-session propagation, and
           explicit no-allocation/no-service/no-financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and references only;
                             no real customer, credential, secret, provider,
                             browser, payment, or settlement data.
TENANT BOUNDARY: Every fake P2 history/read/write is exact-tenant scoped and
                 records the same caller-owned active transaction session.
AUTHORITY BOUNDARY: Certificate only. ACCEPTED does not imply service;
                    RECEIVED/RECEIVED_IN_OFFICE do not imply deputy allocation,
                    attempt, service execution, return, invoice, payment,
                    execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Inactive transaction, missing/foreign office,
                         malformed timestamps, invalid chronology, partial
                         state, divergent evidence/history, or persistence
                         mismatch must reject without healing or invented truth.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, Callable

import pytest

import tools.eos.legal_operations.orchestration.process_service_acceptance_receipt_orchestrator as receipt
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    LegalInstructionState,
    ProcessDocument,
    ProcessDocumentState,
    SheriffOffice,
)
from tools.eos.legal_operations.orchestration.process_service_acceptance_receipt_orchestrator import (
    VERSION as PRODUCTION_VERSION,
    ProcessServiceAcceptanceReceiptDisposition,
    ProcessServiceAcceptanceReceiptError,
    ProcessServiceAcceptanceReceiptTransactionRequiredError,
    accept_instruction_and_receive_document,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-CERT"
BASE = datetime(2026, 9, 23, 9, 0, tzinfo=timezone.utc)
TENANT = "tenant-l8-3"
FOREIGN_TENANT = "tenant-l8-3-foreign"


class FakeSession:
    """Minimal caller-owned transaction marker for direct L8-3 tests."""

    def __init__(self, in_transaction: bool) -> None:
        self.in_transaction = in_transaction


def _lookup(document: dict[str, Any], key: str) -> Any:
    """Resolve a Mongo-style dotted field path inside one fake document."""
    value: Any = document
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


class FakeCollection:
    """In-memory collection implementing the exact P2/Mongo calls used by L8-3."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, dict[str, object]]] = []

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, Any]]:
        """Return exact matching rows with dotted-path support."""
        self.calls.append(("find", session, deepcopy(query)))
        return [
            deepcopy(document)
            for document in self.docs
            if all(_lookup(document, key) == value for key, value in query.items())
        ]

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        """Return the first exact matching row while recording scope/session."""
        self.calls.append(("find_one", session, deepcopy(query)))
        for document in self.docs:
            if all(_lookup(document, key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        """Append one immutable P2 row without adding semantics."""
        self.calls.append(("insert_one", session, deepcopy(document)))
        self.docs.append(deepcopy(document))
        return SimpleNamespace(inserted_id=len(self.docs))


def _seed_registration(
    collection: FakeCollection,
    session: object,
    *,
    tenant_id: str = TENANT,
    sheriff_office_id: str = "office-1",
) -> tuple[
    LegalInstruction,
    ProcessDocument,
    DocumentCustodyEvent,
    SheriffOffice,
]:
    """Persist the exact registered intake prerequisites and canonical office."""
    instruction = LegalInstruction(
        tenant_id=tenant_id,
        instruction_id="instruction-1",
        case_matter_id="matter-1",
        document_id="document-1",
        registered_at=BASE + timedelta(minutes=1),
        evidence_reference="instruction-registration",
    )
    document = ProcessDocument(
        tenant_id=tenant_id,
        document_id="document-1",
        case_matter_id="matter-1",
        document_type="summons",
        registered_at=BASE + timedelta(minutes=2),
        registration_evidence_reference="document-registration",
    )
    registration = DocumentCustodyEvent(
        tenant_id=tenant_id,
        custody_event_id="custody-registration-1",
        document_id="document-1",
        event_type=DocumentCustodyEventType.REGISTERED,
        occurred_at=BASE + timedelta(minutes=2),
        sequence_number=1,
        evidence_reference="document-registration",
    )
    office = SheriffOffice(
        tenant_id=tenant_id,
        sheriff_office_id=sheriff_office_id,
        district_id="district-1",
        name="Sheriff Johannesburg Central",
        evidence_reference="office-provisioning",
    )
    for value in (instruction, document, registration, office):
        LegalOperationsLifecycleRegistry.create(
            value,
            collection,
            session=session,
        )
    return instruction, document, registration, office


def _call(
    collection: FakeCollection,
    session: object,
    **overrides: object,
) -> receipt.ProcessServiceAcceptanceReceiptResult:
    """Invoke L8-3 using one canonical synthetic acceptance/receipt command."""
    values: dict[str, object] = {
        "tenant_id": TENANT,
        "instruction_id": "instruction-1",
        "document_id": "document-1",
        "sheriff_office_id": "office-1",
        "accepted_at": BASE + timedelta(minutes=10),
        "acceptance_evidence_reference": "instruction-accepted",
        "received_at": BASE + timedelta(minutes=15),
        "receipt_evidence_reference": "office-receipt",
        "receipt_custody_event_id": "custody-received-1",
    }
    values.update(overrides)
    return accept_instruction_and_receive_document(
        tenant_id=str(values["tenant_id"]),
        instruction_id=str(values["instruction_id"]),
        document_id=str(values["document_id"]),
        sheriff_office_id=str(values["sheriff_office_id"]),
        accepted_at=values["accepted_at"],  # type: ignore[arg-type]
        acceptance_evidence_reference=str(
            values["acceptance_evidence_reference"]
        ),
        received_at=values["received_at"],  # type: ignore[arg-type]
        receipt_evidence_reference=str(values["receipt_evidence_reference"]),
        receipt_custody_event_id=str(values["receipt_custody_event_id"]),
        lifecycle_collection=collection,
        session=session,
    )


def _expect_code(
    code: str,
    operation: Callable[[], object],
    *,
    error_type: type[ProcessServiceAcceptanceReceiptError] = (
        ProcessServiceAcceptanceReceiptError
    ),
) -> None:
    """Assert one stable L8-3 failure code."""
    with pytest.raises(error_type) as caught:
        operation()
    assert caught.value.code == code
    assert str(caught.value) == code


def _insert_count(collection: FakeCollection) -> int:
    """Return the number of durable P2 writes attempted by the fake collection."""
    return sum(call[0] == "insert_one" for call in collection.calls)


def test_acceptance_and_receipt_create_exact_three_new_facts() -> None:
    """L8-3 creates accepted instruction, received document, and receipt custody."""
    collection = FakeCollection()
    session = FakeSession(True)
    _seed_registration(collection, session)
    writes_before = _insert_count(collection)

    result = _call(collection, session)

    assert result.disposition is ProcessServiceAcceptanceReceiptDisposition.CREATED
    assert result.accepted_instruction.state is LegalInstructionState.ACCEPTED
    assert result.received_document.state is ProcessDocumentState.RECEIVED
    assert (
        result.receipt_custody_event.event_type
        is DocumentCustodyEventType.RECEIVED_IN_OFFICE
    )
    assert result.receipt_custody_event.sequence_number == 2
    assert result.receipt_custody_event.to_holder_reference == "office-1"
    assert len(result.receipt_custody_chain) == 2
    assert _insert_count(collection) == writes_before + 3
    assert len(collection.docs) == 7


def test_exact_replay_writes_nothing() -> None:
    """Repeating the exact L8-3 command replays without duplicate durable rows."""
    collection = FakeCollection()
    session = FakeSession(True)
    _seed_registration(collection, session)
    created = _call(collection, session)
    writes = _insert_count(collection)

    replayed = _call(collection, session)

    assert created.disposition is ProcessServiceAcceptanceReceiptDisposition.CREATED
    assert replayed.disposition is ProcessServiceAcceptanceReceiptDisposition.REPLAYED
    assert (
        replayed.accepted_instruction.fingerprint
        == created.accepted_instruction.fingerprint
    )
    assert replayed.received_document.fingerprint == created.received_document.fingerprint
    assert (
        replayed.receipt_custody_event.fingerprint
        == created.receipt_custody_event.fingerprint
    )
    assert _insert_count(collection) == writes
    assert len(collection.docs) == 7


def test_exact_receipt_replays_after_valid_later_progression() -> None:
    """Later close/allocation/custody facts do not erase exact L8-3 replay."""
    collection = FakeCollection()
    session = FakeSession(True)
    _seed_registration(collection, session)
    created = _call(collection, session)

    closed_instruction = created.accepted_instruction.transition_to(
        LegalInstructionState.CLOSED,
        evidence_reference="instruction-close",
        occurred_at=BASE + timedelta(hours=1),
    )
    allocated_document = created.received_document.transition_to(
        ProcessDocumentState.ALLOCATED_TO_DEPUTY,
        evidence_reference="allocation",
        occurred_at=BASE + timedelta(minutes=30),
    )
    allocated_custody = DocumentCustodyEvent(
        tenant_id=TENANT,
        custody_event_id="custody-allocated-1",
        document_id="document-1",
        event_type=DocumentCustodyEventType.ALLOCATED_TO_DEPUTY,
        occurred_at=BASE + timedelta(minutes=30),
        sequence_number=3,
        evidence_reference="allocation",
        from_holder_reference="office-1",
        to_holder_reference="deputy-1",
    )
    for value in (closed_instruction, allocated_document, allocated_custody):
        LegalOperationsLifecycleRegistry.create(
            value,
            collection,
            session=session,
        )

    writes = _insert_count(collection)
    replayed = _call(collection, session)

    assert replayed.disposition is ProcessServiceAcceptanceReceiptDisposition.REPLAYED
    assert replayed.accepted_instruction.state is LegalInstructionState.ACCEPTED
    assert replayed.received_document.state is ProcessDocumentState.RECEIVED
    assert len(replayed.receipt_custody_chain) == 2
    assert _insert_count(collection) == writes
    assert len(collection.docs) == 10


def test_partial_acceptance_receipt_rejects_without_healing() -> None:
    """One already-created L8-3 fact cannot be silently completed into the bundle."""
    collection = FakeCollection()
    session = FakeSession(True)
    instruction, _, _, _ = _seed_registration(collection, session)
    accepted = instruction.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="instruction-accepted",
        occurred_at=BASE + timedelta(minutes=10),
    )
    LegalOperationsLifecycleRegistry.create(
        accepted,
        collection,
        session=session,
    )
    writes = _insert_count(collection)

    _expect_code(
        "L8_3_PARTIAL_ACCEPTANCE_RECEIPT",
        lambda: _call(collection, session),
    )

    assert _insert_count(collection) == writes
    assert len(collection.docs) == 5


def test_different_acceptance_evidence_for_same_lifecycle_rejects() -> None:
    """Existing ACCEPTED truth with different evidence cannot be replaced."""
    collection = FakeCollection()
    session = FakeSession(True)
    instruction, _, _, _ = _seed_registration(collection, session)
    divergent = instruction.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="different-acceptance",
        occurred_at=BASE + timedelta(minutes=10),
    )
    LegalOperationsLifecycleRegistry.create(
        divergent,
        collection,
        session=session,
    )
    writes = _insert_count(collection)

    _expect_code(
        "L8_3_ACCEPTANCE_IDENTITY_DIVERGENCE",
        lambda: _call(collection, session),
    )

    assert _insert_count(collection) == writes


def test_foreign_office_is_indistinguishable_from_absence() -> None:
    """A SheriffOffice existing only in another tenant never crosses scope."""
    collection = FakeCollection()
    session = FakeSession(True)
    _seed_registration(collection, session)
    foreign_office = SheriffOffice(
        tenant_id=FOREIGN_TENANT,
        sheriff_office_id="foreign-office",
        district_id="district-foreign",
        name="Foreign Sheriff Office",
        evidence_reference="foreign-office-source",
    )
    LegalOperationsLifecycleRegistry.create(
        foreign_office,
        collection,
        session=session,
    )
    writes = _insert_count(collection)

    _expect_code(
        "L8_3_SHERIFFOFFICE_NOT_FOUND",
        lambda: _call(
            collection,
            session,
            sheriff_office_id="foreign-office",
        ),
    )

    assert _insert_count(collection) == writes


@pytest.mark.parametrize(
    ("overrides", "code"),
    (
        (
            {
                "accepted_at": BASE + timedelta(minutes=20),
                "received_at": BASE + timedelta(minutes=15),
            },
            "L8_3_ACCEPTANCE_RECEIPT_CHRONOLOGY_INVALID",
        ),
        (
            {"accepted_at": datetime(2026, 9, 23, 9, 10)},
            "L8_3_ACCEPTED_AT_INVALID",
        ),
        (
            {"received_at": datetime(2026, 9, 23, 9, 15)},
            "L8_3_RECEIVED_AT_INVALID",
        ),
    ),
)
def test_invalid_timestamps_reject_without_writes(
    overrides: dict[str, object],
    code: str,
) -> None:
    """Malformed or reversed acceptance/receipt chronology never reaches writes."""
    collection = FakeCollection()
    session = FakeSession(True)
    _seed_registration(collection, session)
    writes = _insert_count(collection)

    _expect_code(
        code,
        lambda: _call(collection, session, **overrides),
    )

    assert _insert_count(collection) == writes


def test_inactive_transaction_rejects_before_database_access() -> None:
    """Missing/inactive caller transaction cannot read or write lifecycle truth."""
    for session in (None, FakeSession(False)):
        collection = FakeCollection()
        _expect_code(
            "L8_3_ACTIVE_TRANSACTION_REQUIRED",
            lambda collection=collection, session=session: _call(
                collection,
                session,
            ),
            error_type=ProcessServiceAcceptanceReceiptTransactionRequiredError,
        )
        assert collection.calls == []


def test_exact_tenant_and_session_reach_every_database_operation() -> None:
    """All history/custody/read/write operations carry exact tenant and session."""
    collection = FakeCollection()
    session = FakeSession(True)
    _seed_registration(collection, session)
    collection.calls.clear()

    _call(collection, session)

    assert collection.calls
    assert all(call[1] is session for call in collection.calls)
    for _, _, query in collection.calls:
        if "tenant_id" in query:
            assert query["tenant_id"] == TENANT


def test_result_excludes_allocation_service_and_financial_authority() -> None:
    """L8-3 output contains receipt truth only, never downstream authority."""
    collection = FakeCollection()
    session = FakeSession(True)
    _seed_registration(collection, session)
    result = _call(collection, session)
    serialized = str(result.to_dict())

    for forbidden in (
        "ALLOCATED_TO_DEPUTY",
        "ServiceAttempt",
        "ServiceExecution",
        "ReturnOfService",
        "invoice",
        "payment",
        "settlement",
        "paid_state",
        "bank_execution",
        "provider_execution",
    ):
        assert forbidden not in serialized

    assert not hasattr(receipt, "start_transaction")
    assert not hasattr(receipt, "commit_transaction")
    assert not hasattr(receipt, "abort_transaction")


def test_versions_are_frozen_to_l8_3_release() -> None:
    """Certificate remains bound to the intended production release."""
    assert (
        PRODUCTION_VERSION
        == "v1.0.1-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT"
    )
    assert VERSION == "v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-CERT"


# ARTIFACT: test_process_service_acceptance_receipt_orchestrator.py
# VERSION: v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-CERT
# AUTHORITY BOUNDARY: direct L8-3 acceptance/office-receipt certificate only
# TENANT POSTURE: exact synthetic tenant and caller-session propagation
# FAIL-CLOSED POSTURE: invalid transaction/scope/time/partial/divergence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
