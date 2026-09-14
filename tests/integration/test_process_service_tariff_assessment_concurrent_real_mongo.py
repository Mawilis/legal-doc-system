"""Deterministic P6A concurrent tariff-assessment certificate.

TITLE: Wilsy OS P6A Tariff Assessment Concurrent Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-CONCURRENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Two caller-owned Mongo transactions racing on one canonical assessment.
TENANT BOUNDARY: UUID-isolated database and tenant predicates on every operation.
AUTHORITY BOUNDARY: P6A assessment evidence only; P1/P2 remain source authority.
TRANSACTION BOUNDARY: Workers own sessions, transactions, abort, commit, and end.
FINANCIAL BOUNDARY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Only the governed P6A retry code classifies the transaction loser.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-CONCURRENT-REAL-MONGO-CERT
           certifies one durable winner, one governed retry loser, immutable replay,
           historical version binding, and absence of partial financial authority.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import os
import sys
import threading
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import District, ReturnOfService, ServiceAttempt, ServiceAttemptState, ServiceExecution
from tools.eos.legal_operations.domain.process_service_tariff_authority import TariffQuantityBasis, TariffRule, TariffSchedule, TariffVersion
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_allocation_registry import ProcessServiceAllocationReceipt, _record_for
from tools.eos.legal_operations.registry.process_service_tariff_registry import ProcessServiceTariffRegistry, ProcessServiceTariffRegistryError

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 16, 0, tzinfo=timezone.utc)
HASH = "c" * 128


class BarrierAssessmentCollection:
    """Delegate a real Mongo collection while synchronizing both inserts."""

    def __init__(self, collection: Any, barrier: threading.Barrier) -> None:
        self._collection = collection
        self._barrier = barrier

    def find_one(self, query: dict[str, Any], *, session: object = None) -> Any:
        return self._collection.find_one(query, session=session)

    def find(self, query: dict[str, Any], *, session: object = None) -> Any:
        return self._collection.find(query, session=session)

    def insert_one(self, document: dict[str, Any], *, session: object = None) -> Any:
        self._barrier.wait(timeout=15)
        return self._collection.insert_one(document, session=session)

    def count_documents(self, query: dict[str, Any], *, session: object = None) -> int:
        return self._collection.count_documents(query, session=session)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any, Any, Any, Any]]:
    """Yield isolated majority/journaled collections and always close Mongo."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"MONGO_RUNTIME_UNAVAILABLE: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"MONGO_REPLICA_SET_UNAVAILABLE: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
        database = client[f"p6a_tariff_race_{uuid.uuid4().hex}"]
        concerns = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        lifecycle = database.get_collection("lifecycle", **concerns)
        receipts = database.get_collection("allocation_receipts", **concerns)
        schedules = database.get_collection("tariff_schedules", **concerns)
        versions = database.get_collection("tariff_versions", **concerns)
        assessments = database.get_collection("tariff_assessments", **concerns)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        ProcessServiceTariffRegistry.ensure_indexes(schedules, versions, assessments)
        yield client, lifecycle, receipts, schedules, versions, assessments
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _tx(client: MongoClient) -> Any:
    session = client.start_session()
    session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    return session


def _seed_return(lifecycle: Any, client: MongoClient, tenant: str) -> tuple[ReturnOfService, str]:
    allocated = ServiceAttempt(tenant, "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation-1")
    attempted = allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempt-1", occurred_at=BASE + timedelta(minutes=1))
    terminal = attempted.transition_to(ServiceAttemptState.COMPLETED, evidence_reference="terminal-1", evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=2))
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-1", executed_at=BASE + timedelta(minutes=3))
    returned = ReturnOfService.from_service_execution(instruction_id=terminal.instruction_id, service_execution=execution, return_id="return-1", generated_at=BASE + timedelta(minutes=4))
    session = _tx(client)
    try:
        district = District(tenant, "district-1", "District One", "ZA-GP", "district-source")
        LegalOperationsLifecycleRegistry.create(district, lifecycle, session=session)
        for snapshot in (allocated, attempted, terminal):
            LegalOperationsLifecycleRegistry.create(snapshot, lifecycle, session=session)
        LegalOperationsLifecycleRegistry.create(execution, lifecycle, session=session, source_attempt=terminal)
        LegalOperationsLifecycleRegistry.create(returned, lifecycle, session=session, source_attempt=terminal, source_execution=execution)
        session.commit_transaction()
    finally:
        session.end_session()
    row = lifecycle.find_one({"tenant_id": tenant, "entity_type": "ReturnOfService", "entity_identity": returned.return_id})
    assert row is not None
    return returned, row["evidence_identity"]


def _allocation_record(tenant: str) -> dict[str, object]:
    receipt = ProcessServiceAllocationReceipt(tenant_id=tenant, allocation_command_id="allocation-1", idempotency_key="idem-1", instruction_id="instruction-1", case_matter_id="case-1", document_id="document-1", district_id="district-1", sheriff_office_id="office-1", deputy_id="deputy-1", assignment_decision_id="decision-1", assignment_decision_fingerprint=HASH, source_instruction_fingerprint=HASH, source_document_fingerprint=HASH, source_district_fingerprint=HASH, source_sheriff_office_fingerprint=HASH, source_deputy_fingerprint=HASH, prior_custody_chain_fingerprint=HASH, prior_custody_head_event_id="custody-0", prior_custody_head_fingerprint=HASH, prior_custody_head_sequence_number=1, from_holder_reference="office-1", to_holder_reference="deputy-1", allocation_custody_event_id="custody-1", allocation_evidence_reference="allocation-evidence", allocated_at=BASE, allocated_document_fingerprint=HASH, allocation_custody_event_fingerprint=HASH, result_custody_chain_fingerprint=HASH)
    return _record_for(receipt)


def test_real_mongo_p6a_duplicate_writer_has_one_governed_retry_loser(mongo_context: tuple[MongoClient, Any, Any, Any, Any, Any]) -> None:
    client, lifecycle, receipts, schedules, versions, assessments = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    returned, return_identity = _seed_return(lifecycle, client, tenant)
    receipts.insert_one(_allocation_record(tenant))
    schedule = TariffSchedule(tenant, "schedule-1", "district-1", "ZA-GP", None, None, "schedule-source")
    version = TariffVersion(tenant, schedule.schedule_id, "version-1", BASE, BASE + timedelta(minutes=10), (TariffRule("SERVICE-001", "Service fee", "SERVICE", TariffQuantityBasis.SERVICE, 12500, "ZAR", "none", "EXEMPT", "return evidence"),), "version-source")
    setup = _tx(client)
    try:
        ProcessServiceTariffRegistry.create_schedule(schedule, schedules, session=setup)
        ProcessServiceTariffRegistry.create_version(version, schedule, versions, session=setup)
        setup.commit_transaction()
    finally:
        setup.end_session()

    barrier = threading.Barrier(2)
    raced_assessments = BarrierAssessmentCollection(assessments, barrier)
    outcomes: list[dict[str, Any]] = []
    outcome_lock = threading.Lock()

    def worker(label: str) -> None:
        session = _tx(client)
        try:
            value = ProcessServiceTariffRegistry.assess_return(tenant_id=tenant, return_evidence_identity=return_identity, lifecycle_collection=lifecycle, allocation_receipt_collection=receipts, schedule_collection=schedules, version_collection=versions, assessment_collection=raced_assessments, schedule_id=schedule.schedule_id, version_id=version.version_id, assessment_id="assessment-race", assessment_at=BASE + timedelta(minutes=5), session=session)
            session.commit_transaction()
            record = {"label": label, "status": "WINNER", "value": value}
        except ProcessServiceTariffRegistryError as error:
            session.abort_transaction()
            cause = error.__cause__
            raw_code = getattr(cause, "code", None)
            labels = [name for name in ("TransientTransactionError", "UnknownTransactionCommitResult") if isinstance(cause, PyMongoError) and cause.has_error_label(name)]
            record = {"label": label, "status": "RETRY", "error": error, "exception_type": type(error).__name__, "governed_code": error.code, "raw_cause": cause, "raw_cause_type": type(cause).__name__ if cause is not None else None, "raw_mongo_code": raw_code if isinstance(raw_code, int) else None, "mongo_labels": labels}
        except BaseException as error:
            try:
                session.abort_transaction()
            except Exception:
                pass
            record = {"label": label, "status": "OTHER", "error": error}
        finally:
            session.end_session()
        with outcome_lock:
            outcomes.append(record)

    threads = [threading.Thread(target=worker, args=(f"worker-{index}",)) for index in (1, 2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    assert all(not thread.is_alive() for thread in threads)
    assert len(outcomes) == 2
    winners = [item for item in outcomes if item["status"] == "WINNER"]
    losers = [item for item in outcomes if item["status"] == "RETRY"]
    assert len(winners) == 1
    assert len(losers) == 1
    loser = losers[0]
    print(f"LOSER_EXCEPTION_TYPE={loser['exception_type']}")
    print(f"LOSER_GOVERNED_CODE={loser['governed_code']}")
    print(f"LOSER_RAW_CAUSE_TYPE={loser['raw_cause_type']}")
    print(f"LOSER_RAW_MONGO_CODE={loser['raw_mongo_code']}")
    print(f"LOSER_MONGO_LABELS={loser['mongo_labels']}")
    assert loser["exception_type"] == "ProcessServiceTariffRegistryError"
    assert loser["governed_code"] == "P6A_RETRY_TRANSACTION_REQUIRED"
    cause = loser["raw_cause"]
    assert isinstance(cause, PyMongoError)
    if isinstance(cause, DuplicateKeyError):
        assert not cause.has_error_label("UnknownTransactionCommitResult")
    else:
        assert cause.has_error_label("TransientTransactionError")
        assert not cause.has_error_label("UnknownTransactionCommitResult")

    durable = assessments.count_documents({"tenant_id": tenant, "entity_identity": "assessment-race"})
    assert durable == 1
    winner = winners[0]["value"]
    assert winner.tariff_version_id == version.version_id
    assert winner.tariff_version_fingerprint == version.fingerprint
    assert winner.effective_time_source == "ServiceExecution.executed_at"
    durable_record = assessments.find_one({"tenant_id": tenant, "entity_identity": "assessment-race"})
    assert durable_record is not None
    assert not (set(durable_record) & {"payment", "settlement", "paid_state", "refund", "invoice", "billing_execution"})

    replay = ProcessServiceTariffRegistry.create_assessment(winner, assessments)
    assert replay.to_dict() == winner.to_dict()
    assert assessments.count_documents({"tenant_id": tenant, "entity_identity": "assessment-race"}) == 1
    divergent = replace(winner, assessment_at=BASE + timedelta(minutes=6))
    with pytest.raises(ProcessServiceTariffRegistryError, match="P6A_REPLAY_CONFLICT"):
        ProcessServiceTariffRegistry.create_assessment(divergent, assessments)

    future = TariffVersion(tenant, schedule.schedule_id, "version-2", BASE + timedelta(minutes=10), None, (TariffRule("SERVICE-001", "Service fee v2", "SERVICE", TariffQuantityBasis.SERVICE, 13000, "ZAR", "none", "EXEMPT", "return evidence"),), "version-source-2")
    history_session = _tx(client)
    try:
        ProcessServiceTariffRegistry.create_version(future, schedule, versions, session=history_session)
        history_session.commit_transaction()
    finally:
        history_session.end_session()
    assert ProcessServiceTariffRegistry.get_version(tenant, schedule.schedule_id, version.version_id, schedules, versions).fingerprint == version.fingerprint
    assert winner.tariff_version_fingerprint == version.fingerprint

    assert not any(hasattr(ProcessServiceTariffRegistry, name) for name in ("start_session", "start_transaction", "commit_transaction", "abort_transaction", "end_session"))
    assert returned.service_execution_id == winner.service_execution_id


# ARTIFACT: test_process_service_tariff_assessment_concurrent_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-CONCURRENT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: deterministic P6A assessment race evidence only.
# TENANT POSTURE: every worker and durable lookup is tenant scoped.
# FAIL-CLOSED POSTURE: exactly one governed retry loser is required.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
