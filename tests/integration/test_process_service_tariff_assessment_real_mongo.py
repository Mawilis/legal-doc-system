"""Host-backed P6A tariff assessment certificate.

TITLE: Wilsy OS P6A Tariff Assessment Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Durable schedule/version/assessment evidence and canonical P2 return source.
TENANT BOUNDARY: UUID-isolated database and tenant predicates on every operation.
AUTHORITY BOUNDARY: P6A tariff evidence only; P1/P2 remain return authority.
TRANSACTION BOUNDARY: The certificate owns sessions; production does not.
FINANCIAL BOUNDARY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Runtime unavailability may skip; product, corruption, replay, or
             transaction failures fail the certificate.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-REAL-MONGO-CERT
           certifies durable exact version selection, return hydration, replay,
           tenant isolation, and caller-owned transaction semantics.
"""
from datetime import datetime, timedelta, timezone
from dataclasses import replace
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import District, ReturnOfService, ServiceAttempt, ServiceAttemptState, ServiceExecution
from tools.eos.legal_operations.domain.process_service_tariff_authority import TariffQuantityBasis, TariffRule, TariffSchedule, TariffVersion
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_allocation_registry import ProcessServiceAllocationReceipt, _record_for
from tools.eos.legal_operations.registry.process_service_tariff_registry import ProcessServiceTariffRegistry

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 15, 0, tzinfo=timezone.utc)
HASH = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any, Any, Any, Any]]:
    """Yield isolated majority/journaled collections and always clean up."""
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
        database = client[f"p6a_tariff_{uuid.uuid4().hex}"]
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


def test_real_mongo_p6a_version_selection_assessment_replay_and_isolation(mongo_context: tuple[MongoClient, Any, Any, Any, Any, Any]) -> None:
    client, lifecycle, receipts, schedules, versions, assessments = mongo_context
    tenant = f"tenant-a-{uuid.uuid4().hex}"
    returned, return_identity = _seed_return(lifecycle, client, tenant)
    receipts.insert_one(_allocation_record(tenant))
    schedule = TariffSchedule(tenant, "schedule-1", "district-1", "ZA-GP", None, None, "schedule-source")
    version = TariffVersion(tenant, schedule.schedule_id, "version-1", BASE, BASE + timedelta(minutes=10), (TariffRule("SERVICE-001", "Service fee", "SERVICE", TariffQuantityBasis.SERVICE, 12500, "ZAR", "none", "EXEMPT", "return evidence"),), "version-source")
    session = _tx(client)
    try:
        ProcessServiceTariffRegistry.create_schedule(schedule, schedules, session=session)
        ProcessServiceTariffRegistry.create_version(version, schedule, versions, session=session)
        first = ProcessServiceTariffRegistry.assess_return(tenant_id=tenant, return_evidence_identity=return_identity, lifecycle_collection=lifecycle, allocation_receipt_collection=receipts, schedule_collection=schedules, version_collection=versions, assessment_collection=assessments, schedule_id=schedule.schedule_id, version_id=version.version_id, assessment_id="assessment-1", assessment_at=BASE + timedelta(minutes=5), session=session)
        replay = ProcessServiceTariffRegistry.assess_return(tenant_id=tenant, return_evidence_identity=return_identity, lifecycle_collection=lifecycle, allocation_receipt_collection=receipts, schedule_collection=schedules, version_collection=versions, assessment_collection=assessments, schedule_id=schedule.schedule_id, version_id=version.version_id, assessment_id="assessment-1", assessment_at=BASE + timedelta(minutes=5), session=session)
        session.commit_transaction()
    finally:
        session.end_session()
    assert replay.to_dict() == first.to_dict()
    assert assessments.count_documents({"tenant_id": tenant}) == 1
    assert first.tariff_version_fingerprint == version.fingerprint
    assert first.assessed_total_minor_units == 12500
    assert ProcessServiceTariffRegistry.get_schedule(tenant, schedule.schedule_id, schedules).to_dict() == schedule.to_dict()
    assert ProcessServiceTariffRegistry.get_version(tenant, schedule.schedule_id, version.version_id, schedules, versions).fingerprint == version.fingerprint
    future_version = TariffVersion(tenant, schedule.schedule_id, "version-2", BASE + timedelta(minutes=10), None, (TariffRule("SERVICE-001", "Service fee v2", "SERVICE", TariffQuantityBasis.SERVICE, 13000, "ZAR", "none", "EXEMPT", "return evidence"),), "version-source-2")
    version_session = _tx(client)
    try:
        ProcessServiceTariffRegistry.create_version(future_version, schedule, versions, session=version_session)
        version_session.commit_transaction()
    finally:
        version_session.end_session()
    assert ProcessServiceTariffRegistry.get_version(tenant, schedule.schedule_id, version.version_id, schedules, versions).fingerprint == version.fingerprint
    assert first.tariff_version_id == version.version_id
    assert first.tariff_version_fingerprint == version.fingerprint
    divergent = replace(first, assessment_at=BASE + timedelta(minutes=6))
    with pytest.raises(Exception, match="P6A_REPLAY_CONFLICT"):
        ProcessServiceTariffRegistry.create_assessment(divergent, assessments)
    durable = assessments.find_one({"tenant_id": tenant, "entity_identity": first.tariff_assessment_id})
    assert durable is not None
    pristine = dict(durable)
    assessments.replace_one({"tenant_id": tenant, "entity_identity": first.tariff_assessment_id}, {**pristine, "fingerprint": "0" * 128})
    with pytest.raises(Exception, match="P6A_RECORD_FINGERPRINT_INVALID"):
        ProcessServiceTariffRegistry.get_assessment(tenant, pristine["evidence_identity"], assessments)
    assessments.replace_one({"tenant_id": tenant, "entity_identity": first.tariff_assessment_id}, pristine)
    assert not (set(pristine) & {"payment", "settlement", "paid_state", "refund", "invoice", "billing_execution"})
    rollback = _tx(client)
    try:
        ProcessServiceTariffRegistry.assess_return(tenant_id=tenant, return_evidence_identity=return_identity, lifecycle_collection=lifecycle, allocation_receipt_collection=receipts, schedule_collection=schedules, version_collection=versions, assessment_collection=assessments, schedule_id=schedule.schedule_id, version_id=version.version_id, assessment_id="assessment-rollback", assessment_at=BASE + timedelta(minutes=7), session=rollback)
        rollback.abort_transaction()
    finally:
        rollback.end_session()
    assert assessments.count_documents({"tenant_id": tenant}) == 1
    with pytest.raises(Exception, match="P6A_NOT_FOUND"):
        ProcessServiceTariffRegistry.get_assessment(f"tenant-b-{uuid.uuid4().hex}", first.fingerprint, assessments)
    assert returned.service_execution_id == first.service_execution_id


# ARTIFACT: test_process_service_tariff_assessment_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed P6A persistence and canonical-source certificate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
