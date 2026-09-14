"""Deterministic real-Mongo concurrent-writer certificate for P5M.

TITLE: Process-Service Offline Field-Evidence Concurrent Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-CONCURRENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove one durable winner and one governed whole-transaction retry loser
         when identical offline evidence writers race on Mongo uniqueness.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_field_evidence_concurrent_real_mongo.py
CERTIFICATION DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0 establishes deterministic two-worker race coverage.
TENANT BOUNDARY: Both workers use one exact canonical tenant and P4-derived scope.
AUTHORITY BOUNDARY: Evidence synchronization only; no lifecycle/service/return truth.
TRANSACTION BOUNDARY: Workers own sessions and transactions; production never does.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED DECLARATION: Ambiguous outcomes, duplicate durability, and unknown
                         race classifications fail the certificate.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from threading import Barrier
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterator, cast
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState
from tools.eos.legal_operations.domain.process_service_field_evidence_projection import project_for_deputy, project_for_law_firm
from tools.eos.legal_operations.orchestration.process_service_field_evidence_orchestrator import sync_offline_field_evidence
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry, _record_for
from tools.eos.legal_operations.registry.process_service_allocation_registry import ProcessServiceAllocationCurrent, ProcessServiceAllocationReceipt, _record_for as allocation_record_for
from tools.eos.legal_operations.registry.process_service_field_evidence_registry import ProcessServiceFieldEvidenceRegistry, ProcessServiceFieldEvidenceRegistryError

VERSION = "v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-CONCURRENT-REAL-MONGO-CERT"
MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
HASH = "a" * 128


class BarrierCollection:
    """Synchronization-only wrapper preserving all real collection operations."""

    def __init__(self, collection: Any, barrier: Barrier) -> None:
        self.collection = collection
        self.barrier = barrier

    def __getattr__(self, name: str) -> Any:
        return getattr(self.collection, name)

    def insert_one(self, document: dict[str, object], *, session: Any = None) -> Any:
        self.barrier.wait(timeout=20)
        return self.collection.insert_one(document, session=session)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any, Any, Any, Any]]:
    """Yield a verified writable replica-set namespace; only hello checks skip."""
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
        database = client[f"p5m_race_{uuid.uuid4().hex}"]
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
        tenant_id="tenant-a", allocation_command_id="allocation-command", idempotency_key="allocation-key", instruction_id="instruction-1", case_matter_id="matter-1", document_id="document-1", district_id="district-1", sheriff_office_id="office-1", deputy_id="deputy-1", assignment_decision_id="assignment-1", assignment_decision_fingerprint=HASH, source_instruction_fingerprint=HASH, source_document_fingerprint=HASH, source_district_fingerprint=HASH, source_sheriff_office_fingerprint=HASH, source_deputy_fingerprint=HASH, prior_custody_chain_fingerprint=HASH, prior_custody_head_event_id="head-1", prior_custody_head_fingerprint=HASH, prior_custody_head_sequence_number=1, from_holder_reference="office-1", to_holder_reference="deputy-1", allocation_custody_event_id="allocation-event", allocation_evidence_reference="allocation", allocated_at=BASE, allocated_document_fingerprint=HASH, allocation_custody_event_fingerprint=HASH, result_custody_chain_fingerprint=HASH,
    )
    current = ProcessServiceAllocationCurrent(tenant_id="tenant-a", document_id="document-1", process_document_fingerprint=HASH, custody_chain_fingerprint=HASH, custody_head_event_id="allocation-event", custody_head_fingerprint=HASH, custody_head_sequence_number=2, current_holder_reference="deputy-1", authority_evidence_reference="allocation-command", authority_evidence_fingerprint=receipt.fingerprint)
    return receipt, current


def test_deterministic_two_worker_race(mongo_context: tuple[MongoClient, Any, Any, Any, Any, Any]) -> None:
    client, database, lifecycle, journal, allocation_receipts, allocation_current = mongo_context
    source = _attempt()
    LegalOperationsLifecycleRegistry.create(ServiceAttempt("tenant-a", "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation"), lifecycle)
    LegalOperationsLifecycleRegistry.create(source, lifecycle)
    allocation_receipt, allocation_pointer = _allocation()
    allocation_receipts.insert_one(allocation_record_for(allocation_receipt))
    allocation_current.insert_one(allocation_pointer.to_dict())
    barrier = Barrier(2)
    raced_journal = BarrierCollection(journal, barrier)

    def worker() -> tuple[str, BaseException | None]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    sync_offline_field_evidence(tenant_id="tenant-a", attempt_evidence_identity=_identity(source), device_id="device-1", event_id="event-race", sequence_number=1, occurred_at=BASE + timedelta(minutes=3), evidence_reference="field-race", evidence_fingerprint="b" * 128, receipt_id="receipt-race", accepted_at=BASE + timedelta(minutes=4), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_receipts, allocation_current_collection=allocation_current, journal_collection=raced_journal, session=session)
            return "WIN", None
        except BaseException as error:
            return "ERR", error

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: worker(), (1, 2)))
    winners = [item for item in outcomes if item[0] == "WIN"]
    errors = [item[1] for item in outcomes if item[0] == "ERR"]
    assert len(winners) == 1
    assert len(errors) == 1
    loser = errors[0]
    assert isinstance(loser, ProcessServiceFieldEvidenceRegistryError)
    assert loser.code == "P5M_RETRY_TRANSACTION_REQUIRED"
    raw_cause = loser.__cause__
    print(
        "LOSER_DIAGNOSTICS="
        f"exception={type(loser).__name__};cause={type(raw_cause).__name__ if raw_cause else 'NONE'};"
        f"code={getattr(raw_cause, 'code', 'NONE')};labels={getattr(raw_cause, '_error_labels', 'NONE')}"
    )
    assert journal.count_documents({"event_id": "event-race"}) == 1
    durable = journal.find_one({"event_id": "event-race"})
    assert durable is not None
    receipt = ProcessServiceFieldEvidenceRegistry.get("tenant-a", cast(str, durable["evidence_identity"]), journal)
    assert (receipt.tenant_id, receipt.district_id, receipt.sheriff_office_id, receipt.deputy_id, receipt.device_id, receipt.attempt_id, receipt.sequence_number) == ("tenant-a", "district-1", "office-1", "deputy-1", "device-1", "attempt-1", 1)
    canonical = LegalOperationsLifecycleRegistry.get("tenant-a", _identity(source), lifecycle)
    assert isinstance(canonical, ServiceAttempt)
    assert canonical.state is ServiceAttemptState.ATTEMPTED
    assert project_for_deputy(tenant_id="tenant-a", district_id="district-1", sheriff_office_id="office-1", deputy_id="deputy-1", attempts=(canonical,), receipts=(receipt,)).entries[0].evidence_event_count == 1
    assert project_for_law_firm(tenant_id="tenant-a", attempts=(canonical,), receipts=(receipt,)).entries[0].evidence_event_count == 1
    with client.start_session() as session:
        with session.start_transaction():
            replay = sync_offline_field_evidence(tenant_id="tenant-a", attempt_evidence_identity=_identity(source), device_id="device-1", event_id="event-race", sequence_number=1, occurred_at=BASE + timedelta(minutes=3), evidence_reference="field-race", evidence_fingerprint="b" * 128, receipt_id="receipt-race", accepted_at=BASE + timedelta(minutes=4), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_receipts, allocation_current_collection=allocation_current, journal_collection=journal, session=session)
    assert replay.to_dict() == receipt.to_dict()
    with pytest.raises(Exception):
        with client.start_session() as session:
            with session.start_transaction():
                sync_offline_field_evidence(tenant_id="tenant-a", attempt_evidence_identity=_identity(source), device_id="device-1", event_id="event-race", sequence_number=1, occurred_at=BASE + timedelta(minutes=3), evidence_reference="field-divergent", evidence_fingerprint="c" * 128, receipt_id="receipt-race", accepted_at=BASE + timedelta(minutes=4), lifecycle_collection=lifecycle, allocation_receipt_collection=allocation_receipts, allocation_current_collection=allocation_current, journal_collection=journal, session=session)
    assert journal.count_documents({"event_id": "event-race"}) == 1
    assert not {"invoice", "payment", "settlement", "paid_state", "billing_execution"}.intersection(durable)
    assert "ServiceExecution" not in durable and "ReturnOfService" not in durable


# ARTIFACT: test_process_service_field_evidence_concurrent_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-CONCURRENT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: deterministic concurrent evidence persistence only.
# FAIL-CLOSED POSTURE: ambiguous or non-governed race outcomes fail.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
