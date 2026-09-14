"""Host-backed certificate for the P5 offline field-evidence journal.

TITLE: Process-Service Offline Field Evidence Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verify durable immutable observation replay, ordering, tenant
         isolation, and caller-owned transaction semantics against MongoDB.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_field_evidence_real_mongo.py
CERTIFICATION DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0 establishes host-backed P5 evidence coverage.
TENANT BOUNDARY: Every operation is exact tenant scoped; foreign evidence is absence.
AUTHORITY BOUNDARY: Sync evidence only; no legal attempt/service/return mutation.
TRANSACTION BOUNDARY: The test owns sessions, starts/commits/aborts, and P5 propagates them.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED DECLARATION: After hello, index, persistence, and product failures fail the test.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator, cast
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState
from tools.eos.legal_operations.orchestration.process_service_field_evidence_orchestrator import sync_offline_field_evidence
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry, _record_for
from tools.eos.legal_operations.registry.process_service_allocation_registry import ProcessServiceAllocationCurrent, ProcessServiceAllocationReceipt, _record_for as allocation_record_for
from tools.eos.legal_operations.registry.process_service_field_evidence_registry import ProcessServiceFieldEvidenceRegistry

VERSION = "v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-REAL-MONGO-CERT"
MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
HASH = "a" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any, Any, Any, Any]]:
    """Yield an isolated verified Mongo namespace, cleaning it without masking failures."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"Mongo hello unavailable: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("Mongo replica set has no writable primary")
        database = client[f"p5m_field_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection("legal_operations_lifecycle_evidence", read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
        journal = database.get_collection("process_service_field_evidence", read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
        allocation_receipts = database.get_collection("process_service_allocation_receipts", read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
        allocation_current = database.get_collection("process_service_allocation_current", read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        ProcessServiceFieldEvidenceRegistry.ensure_indexes(journal)
        yield client, database, lifecycle, journal, allocation_receipts, allocation_current
    finally:
        active_error = bool(__import__("sys").exc_info()[0])
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _attempt() -> ServiceAttempt:
    allocated = ServiceAttempt("tenant-a", "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation")
    return allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=1))


def _identity(source: ServiceAttempt) -> str:
    return cast(str, _record_for(source)["evidence_identity"])


def _allocation() -> tuple[ProcessServiceAllocationReceipt, ProcessServiceAllocationCurrent]:
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
        tenant_id="tenant-a", document_id="document-1", process_document_fingerprint=HASH, custody_chain_fingerprint=HASH,
        custody_head_event_id="allocation-event", custody_head_fingerprint=HASH, custody_head_sequence_number=2,
        current_holder_reference="deputy-1", authority_evidence_reference="allocation-command", authority_evidence_fingerprint=receipt.fingerprint,
    )
    return receipt, current


def _sync(*, client: MongoClient, lifecycle: Any, journal: Any, allocation_receipts: Any, allocation_current: Any, receipt_id: str, event_id: str, sequence: int, previous: str | None = None) -> Any:
    source = _attempt()
    with client.start_session() as session:
        with session.start_transaction():
            return sync_offline_field_evidence(
                tenant_id="tenant-a", attempt_evidence_identity=_identity(source), device_id="device-1", event_id=event_id,
                sequence_number=sequence, occurred_at=BASE + timedelta(minutes=2 + sequence), evidence_reference=f"field-{sequence}",
                evidence_fingerprint=("b" if sequence == 1 else "c") * 128, previous_event_fingerprint=previous,
                receipt_id=receipt_id, accepted_at=BASE + timedelta(minutes=4 + sequence), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_receipts, allocation_current_collection=allocation_current, journal_collection=journal, session=session,
            )


def test_real_mongo_field_evidence_contract(mongo_context: tuple[MongoClient, Any, Any, Any, Any, Any]) -> None:
    client, database, lifecycle, journal, allocation_receipts, allocation_current = mongo_context
    source = _attempt()
    LegalOperationsLifecycleRegistry.create(ServiceAttempt("tenant-a", "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation"), lifecycle)
    LegalOperationsLifecycleRegistry.create(source, lifecycle)
    allocation_receipt, allocation_pointer = _allocation()
    allocation_receipts.insert_one(allocation_record_for(allocation_receipt))
    allocation_current.insert_one(allocation_pointer.to_dict())
    identity = _identity(source)
    with client.start_session() as session:
        with session.start_transaction():
            first = sync_offline_field_evidence(tenant_id="tenant-a", attempt_evidence_identity=identity, device_id="device-1", event_id="event-1", sequence_number=1, occurred_at=BASE + timedelta(minutes=3), evidence_reference="field-1", evidence_fingerprint="b" * 128, receipt_id="receipt-1", accepted_at=BASE + timedelta(minutes=4), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_receipts, allocation_current_collection=allocation_current, journal_collection=journal, session=session)
    with client.start_session() as session:
        with session.start_transaction():
            replay = sync_offline_field_evidence(tenant_id="tenant-a", attempt_evidence_identity=identity, device_id="device-1", event_id="event-1", sequence_number=1, occurred_at=BASE + timedelta(minutes=3), evidence_reference="field-1", evidence_fingerprint="b" * 128, receipt_id="receipt-1", accepted_at=BASE + timedelta(minutes=4), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_receipts, allocation_current_collection=allocation_current, journal_collection=journal, session=session)
    assert replay.to_dict() == first.to_dict()
    assert first.district_id == "district-1"
    assert first.sheriff_office_id == "office-1"
    assert journal.count_documents({}) == 1
    with client.start_session() as session:
        with session.start_transaction():
            second = sync_offline_field_evidence(tenant_id="tenant-a", attempt_evidence_identity=identity, device_id="device-1", event_id="event-2", sequence_number=2, occurred_at=BASE + timedelta(minutes=5), evidence_reference="field-2", evidence_fingerprint="c" * 128, previous_event_fingerprint=first.evidence_fingerprint, receipt_id="receipt-2", accepted_at=BASE + timedelta(minutes=6), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_receipts, allocation_current_collection=allocation_current, journal_collection=journal, session=session)
    assert second.sequence_number == 2
    assert journal.count_documents({}) == 2
    durable = journal.find_one({"evidence_identity": first.evidence_identity})
    assert durable is not None
    assert not {"invoice", "payment", "settlement", "paid_state", "billing_execution"}.intersection(durable)
    with pytest.raises(Exception):
        _sync(client=client, lifecycle=lifecycle, journal=journal, allocation_receipts=allocation_receipts, allocation_current=allocation_current, receipt_id="receipt-gap", event_id="event-gap", sequence=4, previous=second.evidence_fingerprint)
    with pytest.raises(Exception):
        with client.start_session() as session:
            with session.start_transaction():
                sync_offline_field_evidence(tenant_id="tenant-b", attempt_evidence_identity=identity, device_id="device-1", event_id="event-foreign", sequence_number=1, occurred_at=BASE + timedelta(minutes=3), evidence_reference="field", evidence_fingerprint="d" * 128, receipt_id="receipt-foreign", accepted_at=BASE + timedelta(minutes=4), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_receipts, allocation_current_collection=allocation_current, journal_collection=journal, session=session)
    pristine = journal.find_one({"evidence_identity": first.evidence_identity})
    assert pristine is not None
    corrupted = deepcopy(pristine)
    corrupted["command_fingerprint"] = "f" * 128
    journal.replace_one({"_id": pristine["_id"]}, corrupted)
    with pytest.raises(Exception):
        ProcessServiceFieldEvidenceRegistry.get("tenant-a", first.evidence_identity, journal)


# ARTIFACT: test_process_service_field_evidence_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed immutable evidence persistence only.
# FAIL-CLOSED POSTURE: runtime/product failures are never converted to success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
