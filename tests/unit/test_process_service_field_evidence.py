"""Direct adversarial certificate for P5 mobile/offline field evidence.

TITLE: WILSY OS Process-Service Field Evidence and Command Capability Certificate
VERSION: v1.3.0-L8-6F-P5M-SEQUENCE-HEAD-LOOKUP-CERT
AUTHORITY: Direct certification of P5M evidence and L8-6D read projection.
EPITOME: Preserve offline evidence ordering/provenance/replay certification,
         prove exact tenant/event command+receipt recovery and validated sequence
         head resolution for retry-safe server composition,
         and prove the field-command capability descriptor maps only canonical
         active ServiceAttempt states to existing command kinds, binds one
         opaque P2 evidence locator, and never becomes IAM, service, return,
         billing, AI, payment, execution, or settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_field_evidence.py
COLLABORATION / OWNERSHIP: Direct certificate for P5M authority/registry/
                            orchestrator/projection surfaces; P1 owns attempt
                            lifecycle, P2 owns snapshot identity, and callers
                            own authorization and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.3.0-L8-6F-P5M-SEQUENCE-HEAD-LOOKUP-CERT
           certifies exact event command+receipt recovery, empty/head resolution,
           caller-session forwarding, contiguous 1..N sequence validation, and
           fail-closed rejection of durable sequence-history corruption.
           2026-09-23 v1.2.0-L8-6E-P5M-EVENT-REPLAY-LOOKUP-CERT
           certifies exact tenant/event receipt lookup, caller-session forwarding,
           foreign-tenant absence, and strict persisted-evidence hydration for the
           L8-6E replay-safe P5M composition primitive.
           2026-09-23 v1.1.1-L8-6D-FIELD-COMMAND-CAPABILITY-CERT
           repairs the sovereign module-header terminator so the certificate
           imports as valid Python; test assertions, runtime coverage, authority
           boundaries, and production behavior remain unchanged.
           2026-09-23 v1.1.0-L8-6D-FIELD-COMMAND-CAPABILITY-CERT
           adds exact ALLOCATED and ATTEMPTED command-capability mapping,
           immutable descriptor validation, terminal-state rejection, malformed
           locator rejection, and non-authority/non-financial shape proof.
           2026-09-14 v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-CERT established direct P5 mobile evidence coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and hashes only; no
                             customer, credential, geolocation, secret, payment,
                             provider, or external data.
TENANT BOUNDARY: Canonical context derives from exact P1/P2 ServiceAttempt
                 evidence; cross-tenant projection inputs reject.
AUTHORITY BOUNDARY: Evidence acceptance and derived state capability only;
                    capability never substitutes for current IAM authorization.
FINANCIAL AUTHORITY BOUNDARY: No financial semantics; Kennel EOS exclusively
                              owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Invalid identity, ordering, provenance, replay, tenant,
                         state-command mapping, or locator rejects deterministically.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState
from tools.eos.legal_operations.domain.process_service_field_evidence_authority import (
    OfflineFieldEvidenceCommand,
    OfflineFieldEvidenceSyncReceipt,
    ProcessServiceFieldEvidenceAuthorityError,
    _issue_sync_receipt,
    create_offline_field_evidence_command,
)
from tools.eos.legal_operations.orchestration.process_service_field_evidence_orchestrator import sync_offline_field_evidence
from tools.eos.legal_operations.domain.process_service_field_evidence_projection import (
    FieldCommandCapabilityEntry,
    FieldCommandKind,
    ProcessServiceFieldEvidenceProjectionError,
    VERSION as PROJECTION_VERSION,
    project_field_command_capability,
    project_for_deputy,
    project_for_law_firm,
)
from tools.eos.legal_operations.registry import legal_operations_lifecycle_registry as p2
from tools.eos.legal_operations.registry.process_service_allocation_registry import ProcessServiceAllocationCurrent, ProcessServiceAllocationReceipt, _record_for as allocation_record_for
from tools.eos.legal_operations.registry.process_service_field_evidence_registry import (
    ProcessServiceFieldEvidenceRegistry,
    ProcessServiceFieldEvidenceRegistryError,
)

BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
HASH = "a" * 128


class Session:
    in_transaction = True


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.calls: list[tuple[str, object]] = []

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        self.calls.append(("find_one", session))
        return next((row for row in self.rows if all(row.get(key) == value for key, value in query.items())), None)

    def find(self, query: dict[str, object], *, session: object = None) -> list[dict[str, object]]:
        self.calls.append(("find", session))
        return [row for row in self.rows if all(row.get(key) == value for key, value in query.items())]

    def insert_one(self, row: dict[str, object], *, session: object = None) -> None:
        self.calls.append(("insert_one", session))
        self.rows.append(dict(row))


def allocated_attempt() -> ServiceAttempt:
    """Build one canonical active ALLOCATED attempt."""
    return ServiceAttempt(
        tenant_id="tenant-a",
        attempt_id="attempt-1",
        instruction_id="instruction-1",
        document_id="document-1",
        deputy_id="deputy-1",
        allocated_at=BASE,
        allocation_evidence_reference="allocation",
    )


def attempt() -> ServiceAttempt:
    """Build one canonical active ATTEMPTED attempt."""
    return allocated_attempt().transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempt-proof",
        evidence_fingerprint=HASH,
        occurred_at=BASE + timedelta(minutes=1),
    )


def allocation() -> tuple[ProcessServiceAllocationReceipt, ProcessServiceAllocationCurrent]:
    receipt = ProcessServiceAllocationReceipt(
        tenant_id="tenant-a", allocation_command_id="allocation-command", idempotency_key="allocation-key",
        instruction_id="instruction-1", case_matter_id="matter-1", document_id="document-1", district_id="district-1",
        sheriff_office_id="office-1", deputy_id="deputy-1", assignment_decision_id="assignment-1",
        assignment_decision_fingerprint=HASH, source_instruction_fingerprint=HASH, source_document_fingerprint=HASH,
        source_district_fingerprint=HASH, source_sheriff_office_fingerprint=HASH, source_deputy_fingerprint=HASH,
        prior_custody_chain_fingerprint=HASH, prior_custody_head_event_id="head-1", prior_custody_head_fingerprint=HASH,
        prior_custody_head_sequence_number=1, from_holder_reference="office-1", to_holder_reference="deputy-1",
        allocation_custody_event_id="allocation-event", allocation_evidence_reference="allocation", allocated_at=BASE,
        allocated_document_fingerprint=HASH, allocation_custody_event_fingerprint=HASH, result_custody_chain_fingerprint=HASH,
    )
    current = ProcessServiceAllocationCurrent(
        tenant_id="tenant-a", document_id="document-1", process_document_fingerprint=HASH,
        custody_chain_fingerprint=HASH, custody_head_event_id="allocation-event", custody_head_fingerprint=HASH,
        custody_head_sequence_number=2, current_holder_reference="deputy-1", authority_evidence_reference="allocation-command",
        authority_evidence_fingerprint=receipt.fingerprint,
    )
    return receipt, current
def command(source: ServiceAttempt | None = None, *, sequence: int = 1, previous: str | None = None, event: str = "event-1") -> OfflineFieldEvidenceCommand:
    receipt, current = allocation()
    return create_offline_field_evidence_command(
        attempt=source or attempt(),
        allocation_receipt=receipt,
        allocation_current=current,
        device_id="device-1",
        event_id=event,
        sequence_number=sequence,
        occurred_at=BASE + timedelta(minutes=2 + sequence),
        evidence_reference=f"field-{sequence}",
        evidence_fingerprint=("b" if sequence == 1 else "c") * 128,
        previous_event_fingerprint=previous,
    )


def test_command_is_immutable_and_deterministic() -> None:
    value = command()
    assert value.to_dict() == command().to_dict()
    assert value.fingerprint == command().fingerprint
    with pytest.raises(ProcessServiceFieldEvidenceAuthorityError):
        OfflineFieldEvidenceCommand(
            tenant_id=value.tenant_id,
            attempt_id=value.attempt_id,
            instruction_id=value.instruction_id,
            document_id=value.document_id,
            deputy_id=value.deputy_id,
            district_id=value.district_id,
            sheriff_office_id=value.sheriff_office_id,
            source_attempt_fingerprint=value.source_attempt_fingerprint,
            device_id=value.device_id,
            event_id=value.event_id,
            sequence_number=value.sequence_number,
            occurred_at=value.occurred_at,
            evidence_reference=value.evidence_reference,
            evidence_fingerprint=value.evidence_fingerprint,
        )
    with pytest.raises(AttributeError):
        value.device_id = "other"  # type: ignore[misc]


def test_rejects_bad_tenant_time_and_evidence() -> None:
    source = attempt()
    receipt, current = allocation()
    with pytest.raises(ProcessServiceFieldEvidenceAuthorityError):
        create_offline_field_evidence_command(attempt=source, allocation_receipt=receipt, allocation_current=current, device_id="device", event_id="event", sequence_number=1, occurred_at=BASE.replace(tzinfo=None), evidence_reference="x", evidence_fingerprint=HASH)
    with pytest.raises(ProcessServiceFieldEvidenceAuthorityError):
        create_offline_field_evidence_command(attempt=source, allocation_receipt=receipt, allocation_current=current, device_id="device", event_id="event", sequence_number=1, occurred_at=BASE, evidence_reference="x", evidence_fingerprint="bad")
    with pytest.raises(Exception):
        ServiceAttempt("global", "attempt", "instruction", "document", "deputy", BASE, "allocation")


def test_registry_ordering_replay_and_divergence() -> None:
    collection = Collection()
    first = command()
    receipt = _issue_sync_receipt(command=first, receipt_id="receipt-1", accepted_at=BASE + timedelta(minutes=5))
    persisted = ProcessServiceFieldEvidenceRegistry.persist(first, receipt, collection, session=Session())
    assert persisted.to_dict() == receipt.to_dict()
    assert ProcessServiceFieldEvidenceRegistry.persist(first, receipt, collection, session=Session()).to_dict() == receipt.to_dict()
    second = command(sequence=2, previous=first.evidence_fingerprint, event="event-2")
    second_receipt = _issue_sync_receipt(command=second, receipt_id="receipt-2", accepted_at=BASE + timedelta(minutes=6))
    ProcessServiceFieldEvidenceRegistry.persist(second, second_receipt, collection, session=Session())
    assert len(collection.rows) == 2
    divergent = command(event="event-3")
    divergent_receipt = _issue_sync_receipt(command=divergent, receipt_id="receipt-3", accepted_at=BASE + timedelta(minutes=7))
    with pytest.raises(ProcessServiceFieldEvidenceRegistryError) as error:
        ProcessServiceFieldEvidenceRegistry.persist(divergent, divergent_receipt, collection, session=Session())
    assert error.value.code == "P5M_REPLAY_CONFLICT"
    gap = command(sequence=4, previous=second.evidence_fingerprint, event="event-4")
    gap_receipt = _issue_sync_receipt(command=gap, receipt_id="receipt-4", accepted_at=BASE + timedelta(minutes=8))
    with pytest.raises(ProcessServiceFieldEvidenceRegistryError) as gap_error:
        ProcessServiceFieldEvidenceRegistry.persist(gap, gap_receipt, collection, session=Session())
    assert gap_error.value.code == "P5M_SEQUENCE_GAP"


def test_registry_resolve_by_event_is_exact_tenant_scoped_and_strict() -> None:
    """Recover one immutable receipt by tenant/event without widening authority."""
    collection = Collection()
    source = command()
    receipt = _issue_sync_receipt(
        command=source,
        receipt_id="receipt-event-lookup",
        accepted_at=BASE + timedelta(minutes=5),
    )
    ProcessServiceFieldEvidenceRegistry.persist(
        source,
        receipt,
        collection,
        session=Session(),
    )

    session = Session()
    resolved = ProcessServiceFieldEvidenceRegistry.resolve_by_event(
        "tenant-a",
        "event-1",
        collection,
        session=session,
    )
    assert resolved.to_dict() == receipt.to_dict()
    assert resolved.fingerprint == receipt.fingerprint
    assert collection.calls[-1] == ("find_one", session)

    with pytest.raises(ProcessServiceFieldEvidenceRegistryError) as foreign:
        ProcessServiceFieldEvidenceRegistry.resolve_by_event(
            "tenant-b",
            "event-1",
            collection,
            session=session,
        )
    assert foreign.value.code == "P5M_EVIDENCE_NOT_FOUND"

    corrupted = dict(collection.rows[0])
    corrupted["receipt_fingerprint"] = "f" * 128
    collection.rows[0] = corrupted
    with pytest.raises(ProcessServiceFieldEvidenceRegistryError) as invalid:
        ProcessServiceFieldEvidenceRegistry.resolve_by_event(
            "tenant-a",
            "event-1",
            collection,
            session=session,
        )
    assert invalid.value.code == "P5M_RECEIPT_FINGERPRINT_MISMATCH"


def test_registry_recovers_exact_event_command_and_contiguous_sequence_head() -> None:
    """Recover replay inputs and one strict tenant/attempt/device journal head."""
    collection = Collection()
    session = Session()

    assert ProcessServiceFieldEvidenceRegistry.resolve_latest_for_attempt_device(
        "tenant-a",
        "attempt-1",
        "device-1",
        collection,
        session=session,
    ) is None
    assert collection.calls[-1] == ("find", session)

    first_command = command()
    first_receipt = _issue_sync_receipt(
        command=first_command,
        receipt_id="receipt-head-1",
        accepted_at=BASE + timedelta(minutes=5),
    )
    ProcessServiceFieldEvidenceRegistry.persist(
        first_command,
        first_receipt,
        collection,
        session=session,
    )
    second_command = command(
        sequence=2,
        previous=first_command.evidence_fingerprint,
        event="event-2",
    )
    second_receipt = _issue_sync_receipt(
        command=second_command,
        receipt_id="receipt-head-2",
        accepted_at=BASE + timedelta(minutes=6),
    )
    ProcessServiceFieldEvidenceRegistry.persist(
        second_command,
        second_receipt,
        collection,
        session=session,
    )

    replay_command, replay_receipt = (
        ProcessServiceFieldEvidenceRegistry.resolve_command_receipt_by_event(
            "tenant-a",
            "event-1",
            collection,
            session=session,
        )
    )
    assert replay_command.to_dict() == first_command.to_dict()
    assert replay_command.fingerprint == first_command.fingerprint
    assert replay_receipt.to_dict() == first_receipt.to_dict()

    head = ProcessServiceFieldEvidenceRegistry.resolve_latest_for_attempt_device(
        "tenant-a",
        "attempt-1",
        "device-1",
        collection,
        session=session,
    )
    assert head is not None
    assert head.to_dict() == second_receipt.to_dict()
    assert head.sequence_number == 2
    assert head.evidence_fingerprint == second_command.evidence_fingerprint

    corrupted = dict(collection.rows[1])
    corrupted["sequence_number"] = 3
    corrupted_command = dict(corrupted["command_payload"])
    corrupted_receipt = dict(corrupted["receipt_payload"])
    corrupted_command["sequence_number"] = 3
    corrupted_receipt["sequence_number"] = 3
    corrupted["command_payload"] = corrupted_command
    corrupted["receipt_payload"] = corrupted_receipt
    collection.rows[1] = corrupted
    with pytest.raises(ProcessServiceFieldEvidenceRegistryError) as invalid:
        ProcessServiceFieldEvidenceRegistry.resolve_latest_for_attempt_device(
            "tenant-a",
            "attempt-1",
            "device-1",
            collection,
            session=session,
        )
    assert invalid.value.code in {
        "P5M_COMMAND_FINGERPRINT_MISMATCH",
        "P5M_RECEIPT_FINGERPRINT_MISMATCH",
        "P5M_SEQUENCE_HISTORY_INVALID",
        "P5M_RECORD_BINDING_MISMATCH",
    }


def test_orchestrator_uses_canonical_attempt_and_forwards_session(monkeypatch: pytest.MonkeyPatch) -> None:
    source = attempt()
    monkeypatch.setattr(p2.LegalOperationsLifecycleRegistry, "get", staticmethod(lambda *args, **kwargs: source))
    lifecycle = Collection()
    allocation_receipt, allocation_current = allocation()
    allocation_collection = Collection()
    allocation_collection.rows.append(allocation_record_for(allocation_receipt))
    current_collection = Collection()
    current_collection.rows.append(allocation_current.to_dict())
    journal = Collection()
    session = Session()
    receipt = sync_offline_field_evidence(
        tenant_id="tenant-a", attempt_evidence_identity="e" * 128, device_id="device-1", event_id="event-1", sequence_number=1,
        occurred_at=BASE + timedelta(minutes=3), evidence_reference="field", evidence_fingerprint=HASH, receipt_id="receipt-1",
        accepted_at=BASE + timedelta(minutes=4), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_collection,
        allocation_current_collection=current_collection, journal_collection=journal, session=session,
    )
    assert receipt.tenant_id == source.tenant_id
    assert source.state is ServiceAttemptState.ATTEMPTED
    assert all(call_session is session for _, call_session in journal.calls)
    with pytest.raises(Exception):
        sync_offline_field_evidence(
            tenant_id="tenant-a", attempt_evidence_identity="e" * 128, device_id="device-1", event_id="event-2", sequence_number=1,
            occurred_at=BASE + timedelta(minutes=3), evidence_reference="field", evidence_fingerprint=HASH, receipt_id="receipt-2",
            accepted_at=BASE + timedelta(minutes=4), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_collection,
            allocation_current_collection=current_collection, journal_collection=journal, session=object(),
        )


def test_receipt_direct_construction_rejected_and_no_service_surfaces() -> None:
    with pytest.raises(ProcessServiceFieldEvidenceAuthorityError):
        OfflineFieldEvidenceSyncReceipt("tenant-a", "receipt", "event", "device", 1, "attempt", "instruction", "document", "deputy", "district", "office", "ref", HASH, HASH, BASE, HASH)
    assert not hasattr(__import__("tools.eos.legal_operations.domain.process_service_field_evidence_authority", fromlist=["x"]), "ServiceExecution")
    assert not hasattr(__import__("tools.eos.legal_operations.domain.process_service_field_evidence_authority", fromlist=["x"]), "ReturnOfService")


def test_field_command_capability_maps_only_exact_active_state_commands() -> None:
    """State capability is deterministic and carries only the opaque P2 locator."""
    allocated = project_field_command_capability(
        attempt=allocated_attempt(),
        current_evidence_identity="d" * 128,
    )
    assert allocated.current_state is ServiceAttemptState.ALLOCATED
    assert allocated.next_command_kinds == (
        FieldCommandKind.TRANSITION_TO_ATTEMPTED,
    )
    assert allocated.to_dict() == {
        "tenant_id": "tenant-a",
        "attempt_id": "attempt-1",
        "instruction_id": "instruction-1",
        "document_id": "document-1",
        "deputy_id": "deputy-1",
        "current_state": "ALLOCATED",
        "current_evidence_identity": "d" * 128,
        "next_command_kinds": ["TRANSITION_TO_ATTEMPTED"],
    }

    attempted = project_field_command_capability(
        attempt=attempt(),
        current_evidence_identity="e" * 128,
    )
    assert attempted.current_state is ServiceAttemptState.ATTEMPTED
    assert attempted.next_command_kinds == (
        FieldCommandKind.RECORD_COMPLETED_OUTCOME,
        FieldCommandKind.RECORD_NOT_COMPLETED_OUTCOME,
    )


def test_field_command_capability_rejects_terminal_locator_and_manual_mismatch() -> None:
    """Terminal states, malformed locators and fabricated command tuples reject."""
    terminal = attempt().transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="completed",
        evidence_fingerprint=HASH,
        occurred_at=BASE + timedelta(minutes=2),
    )
    with pytest.raises(
        ProcessServiceFieldEvidenceProjectionError,
        match="P5M_FIELD_COMMAND_STATE_UNSUPPORTED",
    ):
        project_field_command_capability(
            attempt=terminal,
            current_evidence_identity="f" * 128,
        )

    with pytest.raises(
        ProcessServiceFieldEvidenceProjectionError,
        match="P5M_PROJECTION_EVIDENCE_IDENTITY_INVALID",
    ):
        project_field_command_capability(
            attempt=attempt(),
            current_evidence_identity="not-a-sha3",
        )

    with pytest.raises(
        ProcessServiceFieldEvidenceProjectionError,
        match="P5M_PROJECTION_COMMAND_STATE_MISMATCH",
    ):
        FieldCommandCapabilityEntry(
            tenant_id="tenant-a",
            attempt_id="attempt-1",
            instruction_id="instruction-1",
            document_id="document-1",
            deputy_id="deputy-1",
            current_state=ServiceAttemptState.ALLOCATED,
            current_evidence_identity="a" * 128,
            next_command_kinds=(
                FieldCommandKind.RECORD_COMPLETED_OUTCOME,
            ),
        )


def test_field_command_capability_contains_no_iam_service_or_financial_authority() -> None:
    value = project_field_command_capability(
        attempt=attempt(),
        current_evidence_identity="a" * 128,
    )
    serialized = str(value.to_dict()).casefold()
    for forbidden in (
        "authorized",
        "permission",
        "role",
        "service_completed",
        "return_generated",
        "invoice",
        "payment",
        "settlement",
        "revenue",
        "ai_score",
        "client_name",
        "gps",
        "distance",
    ):
        assert forbidden not in serialized
    assert PROJECTION_VERSION == (
        "v1.1.0-L8-6D-FIELD-COMMAND-CAPABILITY-PROJECTION"
    )


def test_projections_are_scoped_derived_views() -> None:
    source = attempt()
    first = command(source)
    receipt = _issue_sync_receipt(command=first, receipt_id="receipt-projection", accepted_at=BASE + timedelta(minutes=5))
    deputy = project_for_deputy(tenant_id="tenant-a", district_id="district-1", sheriff_office_id="office-1", deputy_id="deputy-1", attempts=(source,), receipts=(receipt,))
    office = project_for_law_firm(tenant_id="tenant-a", attempts=(source,), receipts=(receipt,))
    assert len(deputy.entries) == 1
    assert deputy.entries[0].attempt_state is ServiceAttemptState.ATTEMPTED
    assert deputy.entries[0].evidence_event_count == 1
    assert office.entries == deputy.entries
    with pytest.raises(Exception):
        project_for_law_firm(tenant_id="tenant-b", attempts=(source,), receipts=(receipt,))


# ARTIFACT: test_process_service_field_evidence.py
# VERSION: v1.3.0-L8-6F-P5M-SEQUENCE-HEAD-LOOKUP-CERT
# AUTHORITY BOUNDARY: direct P5M evidence acceptance plus L8-6D state-capability projection certificate only.
# TENANT POSTURE: exact synthetic P1/P2/P5M tenant scope; cross-tenant projection inputs reject.
# FAIL-CLOSED POSTURE: no evidence, command authorization, service or financial truth is inferred from projection state.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
