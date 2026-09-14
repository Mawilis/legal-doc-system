"""Direct adversarial certificate for P5 mobile/offline field evidence.

TITLE: Process-Service Offline Field Evidence Certificate
VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove immutable observation ordering, provenance, replay, and tenant
         boundaries without elevating mobile evidence to legal-service truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_field_evidence.py
CERTIFICATION DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0 establishes direct P5 mobile evidence coverage.
TENANT BOUNDARY: All canonical context derives from exact P2 ServiceAttempt.
AUTHORITY BOUNDARY: Evidence acceptance only; no attempt/service/return state.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Invalid identity, ordering, provenance, replay, and
                         tenant scope reject deterministically.
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
from tools.eos.legal_operations.domain.process_service_field_evidence_projection import project_for_deputy, project_for_law_firm
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


def attempt() -> ServiceAttempt:
    allocated = ServiceAttempt(
        tenant_id="tenant-a",
        attempt_id="attempt-1",
        instruction_id="instruction-1",
        document_id="document-1",
        deputy_id="deputy-1",
        allocated_at=BASE,
        allocation_evidence_reference="allocation",
    )
    return allocated.transition_to(
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
# VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-CERT
# AUTHORITY BOUNDARY: direct evidence acceptance certificate only.
# FAIL-CLOSED POSTURE: no evidence truth is inferred from device observations.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
