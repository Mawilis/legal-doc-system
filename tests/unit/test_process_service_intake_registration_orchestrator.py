"""Direct certificate for canonical Legal Operations intake registration.

TITLE: WILSY OS Process Service Intake Registration Direct Certificate
VERSION: v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-CERT
AUTHORITY: Direct certificate for L8-2 initial intake registration composition only.
EPITOME: Prove active-transaction CaseMatter -> LegalInstruction ->
         ProcessDocument -> REGISTERED custody creation, exact replay,
         progressed-history replay, chronology, partial-state rejection,
         tenant/identity divergence rejection, session propagation, and
         non-financial authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_intake_registration_orchestrator.py
COLLABORATION / OWNERSHIP: Certificate for
                            process_service_intake_registration_orchestrator.py;
                            P1/P2/L8-0 remain independent canonical authorities
                            and authenticated transport remains a later gate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-CERT
           establishes adversarial direct evidence for complete initial intake,
           exact replay after later valid lifecycle progression, partial and
           divergent durable state rejection, chronology, caller-session
           propagation, and explicit non-financial/no-transaction-ownership bounds.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and references only;
                             no real customer, credential, secret, provider,
                             browser, payment, or settlement data.
TENANT BOUNDARY: Every fake P2 history/read/write records exact tenant scope and
                 the same caller-owned transaction session.
AUTHORITY BOUNDARY: Certificate only. REGISTERED does not imply ACCEPTED,
                    RECEIVED, allocation, attempt, service, return, invoice,
                    payment, execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Inactive transaction, malformed P1 values, chronology,
                         partial state, divergent history/identity, or persistence
                         mismatch must reject without healing or invented truth.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, Callable

import pytest

import tools.eos.legal_operations.orchestration.process_service_intake_registration_orchestrator as intake
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    LegalInstructionState,
    ProcessDocument,
    ProcessDocumentState,
)
from tools.eos.legal_operations.orchestration.process_service_intake_registration_orchestrator import (
    VERSION as PRODUCTION_VERSION,
    ProcessServiceIntakeRegistrationDisposition,
    ProcessServiceIntakeRegistrationError,
    ProcessServiceIntakeTransactionRequiredError,
    register_process_service_intake,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-CERT"
BASE = datetime(2026, 9, 23, 7, 0, tzinfo=timezone.utc)


class FakeSession:
    """Minimal caller-owned transaction marker for direct composition tests."""

    def __init__(self, in_transaction: bool) -> None:
        self.in_transaction = in_transaction


class FakeCollection:
    """In-memory collection implementing the exact P2 calls used by L8-2."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, dict[str, object]]] = []

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, Any]]:
        """Return exact matching rows while recording tenant/session scope."""
        self.calls.append(("find", session, deepcopy(query)))
        return [
            deepcopy(document)
            for document in self.docs
            if all(document.get(key) == value for key, value in query.items())
        ]

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        """Return the first exact matching row while recording scope."""
        self.calls.append(("find_one", session, deepcopy(query)))
        for document in self.docs:
            if all(document.get(key) == value for key, value in query.items()):
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


def _kwargs(tenant_id: str = "tenant-a") -> dict[str, object]:
    """Return one complete canonical synthetic intake registration."""
    return {
        "tenant_id": tenant_id,
        "case_matter_id": "matter-1",
        "matter_reference": "CASE-2026-0001",
        "case_opened_at": BASE,
        "matter_evidence_reference": "matter-registration",
        "instruction_id": "instruction-1",
        "instruction_registered_at": BASE + timedelta(minutes=1),
        "instruction_evidence_reference": "instruction-registration",
        "document_id": "document-1",
        "document_type": "summons",
        "document_registered_at": BASE + timedelta(minutes=2),
        "document_registration_evidence_reference": "document-registration",
        "registration_custody_event_id": "custody-registration-1",
    }


def _call(
    collection: FakeCollection,
    session: object,
    **overrides: object,
) -> intake.ProcessServiceIntakeRegistrationResult:
    """Invoke L8-2 with the canonical fake persistence surface."""
    values = _kwargs()
    values.update(overrides)
    return register_process_service_intake(
        tenant_id=values["tenant_id"],  # type: ignore[arg-type]
        case_matter_id=values["case_matter_id"],  # type: ignore[arg-type]
        matter_reference=values["matter_reference"],  # type: ignore[arg-type]
        case_opened_at=values["case_opened_at"],
        matter_evidence_reference=values["matter_evidence_reference"],  # type: ignore[arg-type]
        instruction_id=values["instruction_id"],  # type: ignore[arg-type]
        instruction_registered_at=values["instruction_registered_at"],
        instruction_evidence_reference=values["instruction_evidence_reference"],  # type: ignore[arg-type]
        document_id=values["document_id"],  # type: ignore[arg-type]
        document_type=values["document_type"],  # type: ignore[arg-type]
        document_registered_at=values["document_registered_at"],
        document_registration_evidence_reference=values[
            "document_registration_evidence_reference"
        ],  # type: ignore[arg-type]
        registration_custody_event_id=values[
            "registration_custody_event_id"
        ],  # type: ignore[arg-type]
        lifecycle_collection=collection,
        session=session,
    )


def _expect_code(
    code: str,
    operation: Callable[[], object],
    *,
    error_type: type[ProcessServiceIntakeRegistrationError] = (
        ProcessServiceIntakeRegistrationError
    ),
) -> None:
    """Assert one stable L8-2 failure code."""
    with pytest.raises(error_type) as caught:
        operation()
    assert caught.value.code == code
    assert str(caught.value) == code


def _insert_count(collection: FakeCollection) -> int:
    """Return the number of durable writes attempted by P2."""
    return sum(call[0] == "insert_one" for call in collection.calls)


def test_complete_initial_intake_creates_four_distinct_registration_facts() -> None:
    """Initial intake persists matter, instruction, document, and custody only."""
    collection = FakeCollection()
    session = FakeSession(True)

    result = _call(collection, session)

    assert result.disposition is ProcessServiceIntakeRegistrationDisposition.CREATED
    assert result.case_matter.state is CaseMatterState.OPEN
    assert result.instruction.state is LegalInstructionState.REGISTERED
    assert result.document.state is ProcessDocumentState.REGISTERED
    assert result.custody_event.event_type is DocumentCustodyEventType.REGISTERED
    assert result.custody_event.sequence_number == 1
    assert result.instruction.case_matter_id == result.case_matter.case_matter_id
    assert result.document.case_matter_id == result.case_matter.case_matter_id
    assert result.instruction.document_id == result.document.document_id
    assert result.custody_event.document_id == result.document.document_id
    assert result.custody_event.occurred_at == result.document.registered_at
    assert len(collection.docs) == 4
    assert {row["entity_type"] for row in collection.docs} == {
        "CaseMatter",
        "LegalInstruction",
        "ProcessDocument",
        "DocumentCustodyEvent",
    }


def test_exact_replay_writes_nothing_and_returns_original_registration() -> None:
    """Repeating the exact initial command is a no-write durable replay."""
    collection = FakeCollection()
    session = FakeSession(True)

    created = _call(collection, session)
    writes = _insert_count(collection)
    replayed = _call(collection, session)

    assert created.disposition is ProcessServiceIntakeRegistrationDisposition.CREATED
    assert replayed.disposition is ProcessServiceIntakeRegistrationDisposition.REPLAYED
    assert replayed.case_matter.fingerprint == created.case_matter.fingerprint
    assert replayed.instruction.fingerprint == created.instruction.fingerprint
    assert replayed.document.fingerprint == created.document.fingerprint
    assert replayed.custody_event.fingerprint == created.custody_event.fingerprint
    assert _insert_count(collection) == writes
    assert len(collection.docs) == 4


def test_exact_registration_replays_after_valid_lifecycle_progression() -> None:
    """Later accepted/received/closed snapshots do not erase registration replay."""
    collection = FakeCollection()
    session = FakeSession(True)
    created = _call(collection, session)

    closed_case = created.case_matter.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-close",
        occurred_at=BASE + timedelta(hours=1),
    )
    accepted_instruction = created.instruction.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="instruction-accept",
        occurred_at=BASE + timedelta(minutes=10),
    )
    received_document = created.document.transition_to(
        ProcessDocumentState.RECEIVED,
        evidence_reference="office-receipt",
        occurred_at=BASE + timedelta(minutes=15),
    )
    for value in (closed_case, accepted_instruction, received_document):
        LegalOperationsLifecycleRegistry.create(
            value,
            collection,
            session=session,
        )

    writes = _insert_count(collection)
    replayed = _call(collection, session)

    assert replayed.disposition is ProcessServiceIntakeRegistrationDisposition.REPLAYED
    assert replayed.case_matter.state is CaseMatterState.OPEN
    assert replayed.instruction.state is LegalInstructionState.REGISTERED
    assert replayed.document.state is ProcessDocumentState.REGISTERED
    assert _insert_count(collection) == writes
    assert len(collection.docs) == 7


def test_partial_registration_rejects_without_healing() -> None:
    """One durable component cannot be silently completed into a four-fact intake."""
    collection = FakeCollection()
    session = FakeSession(True)
    values = _kwargs()
    case_matter = CaseMatter(
        tenant_id="tenant-a",
        case_matter_id="matter-1",
        matter_reference="CASE-2026-0001",
        opened_at=BASE,
        evidence_reference="matter-registration",
    )
    LegalOperationsLifecycleRegistry.create(
        case_matter,
        collection,
        session=session,
    )
    writes = _insert_count(collection)

    _expect_code(
        "L8_2_PARTIAL_REGISTRATION",
        lambda: _call(collection, session),
    )

    assert _insert_count(collection) == writes
    assert len(collection.docs) == 1
    assert values["case_matter_id"] == case_matter.case_matter_id


def test_same_identity_different_registration_rejects_before_write() -> None:
    """A pre-existing different initial fact cannot be turned into a new branch."""
    collection = FakeCollection()
    session = FakeSession(True)
    divergent = CaseMatter(
        tenant_id="tenant-a",
        case_matter_id="matter-1",
        matter_reference="DIFFERENT-CASE",
        opened_at=BASE,
        evidence_reference="different-registration",
    )
    LegalOperationsLifecycleRegistry.create(
        divergent,
        collection,
        session=session,
    )
    writes = _insert_count(collection)

    _expect_code(
        "L8_2_REGISTRATION_IDENTITY_DIVERGENCE",
        lambda: _call(collection, session),
    )

    assert _insert_count(collection) == writes
    assert len(collection.docs) == 1


def test_preexisting_divergent_history_rejects_without_arbitrary_selection() -> None:
    """Static lineage forks are rejected through L8-0 before any new fact."""
    collection = FakeCollection()
    session = FakeSession(True)
    first = CaseMatter(
        "tenant-a",
        "matter-1",
        "CASE-2026-0001",
        BASE,
        "matter-registration",
    )
    second = CaseMatter(
        "tenant-a",
        "matter-1",
        "DIFFERENT-CASE",
        BASE,
        "different-registration",
    )
    LegalOperationsLifecycleRegistry.create(first, collection, session=session)
    LegalOperationsLifecycleRegistry.create(second, collection, session=session)
    writes = _insert_count(collection)

    _expect_code(
        "L8_2_REGISTRATION_HISTORY_DIVERGENT",
        lambda: _call(collection, session),
    )

    assert _insert_count(collection) == writes
    assert len(collection.docs) == 2


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("case_opened_at", BASE + timedelta(minutes=2)),
        ("instruction_registered_at", BASE + timedelta(minutes=3)),
    ),
)
def test_registration_chronology_rejects_before_database_access(
    field: str,
    value: object,
) -> None:
    """Matter -> instruction -> document chronology is mandatory before P2."""
    collection = FakeCollection()
    session = FakeSession(True)

    _expect_code(
        "L8_2_REGISTRATION_CHRONOLOGY_INVALID",
        lambda: _call(collection, session, **{field: value}),
    )

    assert collection.calls == []


def test_inactive_transaction_rejects_before_any_database_access() -> None:
    """Missing or inactive caller transaction cannot reach P2."""
    for session in (None, FakeSession(False)):
        collection = FakeCollection()
        _expect_code(
            "L8_2_ACTIVE_TRANSACTION_REQUIRED",
            lambda collection=collection, session=session: _call(
                collection,
                session,
            ),
            error_type=ProcessServiceIntakeTransactionRequiredError,
        )
        assert collection.calls == []


def test_malformed_p1_input_is_bounded_before_persistence() -> None:
    """Pseudo tenant and malformed identity remain P1-governed registration failure."""
    for overrides in (
        {"tenant_id": "global"},
        {"instruction_id": "invalid/instruction"},
        {"document_type": ""},
    ):
        collection = FakeCollection()
        _expect_code(
            "L8_2_REGISTRATION_VALUE_INVALID",
            lambda collection=collection, overrides=overrides: _call(
                collection,
                FakeSession(True),
                **overrides,
            ),
        )
        assert collection.calls == []


def test_exact_tenant_and_session_reach_every_p2_operation() -> None:
    """Every history/read/write is exact tenant scoped and shares one session."""
    collection = FakeCollection()
    session = FakeSession(True)

    _call(collection, session)

    assert collection.calls
    assert all(call[1] is session for call in collection.calls)
    assert all(
        query.get("tenant_id") == "tenant-a"
        for _, _, query in collection.calls
        if "tenant_id" in query
    )


def test_result_has_no_downstream_or_financial_authority() -> None:
    """Registration output contains no acceptance, service, invoice, or payment truth."""
    result = _call(FakeCollection(), FakeSession(True))
    serialized = str(result.to_dict())
    for forbidden in (
        "ACCEPTED",
        "RECEIVED_IN_OFFICE",
        "ALLOCATED_TO_DEPUTY",
        "ServiceAttempt",
        "ServiceExecution",
        "ReturnOfService",
        "invoice",
        "payment",
        "settlement",
        "paid_state",
    ):
        assert forbidden not in serialized
    assert not hasattr(intake, "start_transaction")
    assert not hasattr(intake, "commit_transaction")
    assert not hasattr(intake, "abort_transaction")


def test_versions_are_frozen_to_l8_2_initial_release() -> None:
    """Certificate remains bound to the intended sovereign production release."""
    assert PRODUCTION_VERSION == "v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION"
    assert VERSION == "v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-CERT"


# ARTIFACT: test_process_service_intake_registration_orchestrator.py
# VERSION: v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-CERT
# AUTHORITY BOUNDARY: direct L8-2 initial intake registration certificate only
# TENANT POSTURE: exact synthetic tenant and caller-session propagation
# FAIL-CLOSED POSTURE: invalid transaction/value/chronology/partial/history/divergence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
