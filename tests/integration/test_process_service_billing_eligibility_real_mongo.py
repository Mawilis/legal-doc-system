"""Host-backed P6B billing-eligibility certificate.

TITLE: Wilsy OS P6B Billing Eligibility Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Durable completed-only eligibility evidence and strict source hydration.
TENANT BOUNDARY: UUID-isolated database and tenant predicates on every operation.
AUTHORITY BOUNDARY: P6B evidence only; Billing owns invoices and Kennel owns execution.
TRANSACTION BOUNDARY: Certificate owns test sessions; registry never does.
FAIL-CLOSED: Runtime unavailable may skip; product/corruption/replay failures fail.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-REAL-MONGO-CERT
           certifies durable source provenance, replay, isolation, and rollback.
"""
from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator, cast
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import District, ReturnOfService, ServiceAttempt, ServiceAttemptState, ServiceExecution
from tools.eos.legal_operations.domain.process_service_tariff_authority import TariffQuantityBasis, TariffRule, TariffSchedule, TariffVersion, assess_from_return
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_billing_eligibility_registry import ProcessServiceBillingEligibilityRegistry, ProcessServiceBillingEligibilityRegistryError
from tools.eos.legal_operations.registry.process_service_tariff_registry import ProcessServiceTariffRegistry, _record as tariff_record

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
HASH = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any, Any]]:
    """Yield majority/journaled isolated collections and always close/drop safely."""
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
        database = client[f"p6b_elig_{uuid.uuid4().hex}"]
        concerns = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        lifecycle = database.get_collection("lifecycle", **concerns)
        assessments = database.get_collection("assessments", **concerns)
        eligibility = database.get_collection("eligibility", **concerns)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        ProcessServiceBillingEligibilityRegistry.ensure_indexes(eligibility)
        yield client, lifecycle, assessments, eligibility
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


def test_real_mongo_p6b_completed_hydration_replay_isolation_and_rollback(mongo_context: tuple[MongoClient, Any, Any, Any]) -> None:
    client, lifecycle, assessments, eligibility = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    allocated = ServiceAttempt(tenant, "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation-1")
    attempted = allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", occurred_at=BASE + timedelta(minutes=1))
    terminal = attempted.transition_to(ServiceAttemptState.COMPLETED, evidence_reference="terminal", evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=2))
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-1", executed_at=BASE + timedelta(minutes=3))
    returned = ReturnOfService.from_service_execution(instruction_id=terminal.instruction_id, service_execution=execution, return_id="return-1", generated_at=BASE + timedelta(minutes=4))
    setup = _tx(client)
    try:
        LegalOperationsLifecycleRegistry.create(District(tenant, "district-1", "District", "ZA-GP", "source"), lifecycle, session=setup)
        for snapshot in (allocated, attempted, terminal):
            LegalOperationsLifecycleRegistry.create(snapshot, lifecycle, session=setup)
        LegalOperationsLifecycleRegistry.create(execution, lifecycle, session=setup, source_attempt=terminal)
        LegalOperationsLifecycleRegistry.create(returned, lifecycle, session=setup, source_attempt=terminal, source_execution=execution)
        setup.commit_transaction()
    finally:
        setup.end_session()
    return_identity = next(row["evidence_identity"] for row in lifecycle.find({"tenant_id": tenant, "entity_type": "ReturnOfService", "entity_identity": returned.return_id}))
    schedule = TariffSchedule(tenant, "schedule-1", "district-1", "ZA-GP", None, None, "schedule-source")
    version = TariffVersion(tenant, "schedule-1", "version-1", BASE, None, (TariffRule("SERVICE-001", "Service", "SERVICE", TariffQuantityBasis.SERVICE, 12500, "ZAR", "none", "EXEMPT", "return"),), "version-source")
    assessment = assess_from_return(return_of_service=returned, return_evidence_identity=return_identity, schedule=schedule, tariff_version=version, assessment_id="assessment-1", assessment_at=BASE + timedelta(minutes=5), sheriff_office_id="office-1", effective_at=BASE + timedelta(minutes=3))
    assessment_session = _tx(client)
    try:
        ProcessServiceTariffRegistry.create_assessment(assessment, assessments, session=assessment_session)
        assessment_session.commit_transaction()
    finally:
        assessment_session.end_session()
    assessment_identity = cast(str, tariff_record(assessment)["evidence_identity"])
    issue_session = _tx(client)
    try:
        first = ProcessServiceBillingEligibilityRegistry.issue(tenant_id=tenant, assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=6), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=issue_session)
        replay = ProcessServiceBillingEligibilityRegistry.issue(tenant_id=tenant, assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=6), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=issue_session)
        issue_session.commit_transaction()
    finally:
        issue_session.end_session()
    assert replay.to_dict() == first.to_dict()
    assert eligibility.count_documents({"tenant_id": tenant}) == 1
    hydrated = ProcessServiceBillingEligibilityRegistry.get(tenant, next(row["evidence_identity"] for row in eligibility.find({"tenant_id": tenant})), eligibility)
    assert hydrated.to_dict() == first.to_dict()
    with pytest.raises(ProcessServiceBillingEligibilityRegistryError, match="P6B_NOT_FOUND"):
        ProcessServiceBillingEligibilityRegistry.get(f"foreign-{uuid.uuid4().hex}", first.fingerprint, eligibility)
    durable = eligibility.find_one({"tenant_id": tenant})
    assert durable is not None and not set(durable) & {"invoice", "payment", "settlement", "paid_state", "receivable"}
    rollback = _tx(client)
    try:
        with pytest.raises(ProcessServiceBillingEligibilityRegistryError, match="P6B_REPLAY_CONFLICT"):
            ProcessServiceBillingEligibilityRegistry.issue(tenant_id=tenant, assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=7), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=rollback)
        rollback.abort_transaction()
    finally:
        rollback.end_session()


# ARTIFACT: test_process_service_billing_eligibility_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed P6B evidence only.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
