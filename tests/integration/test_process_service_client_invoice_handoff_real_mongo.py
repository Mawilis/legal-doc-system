"""Host-backed P6C source-hydration certificate.

TITLE: Wilsy OS Process-Service Client-Invoice Handoff Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Read-only P6A/P6B hydration into a derived Billing basis.
TENANT BOUNDARY: UUID-isolated database and tenant predicates on every read/write.
AUTHORITY BOUNDARY: No invoice, quotation, payment, execution, or settlement.
TRANSACTION BOUNDARY: Certificate owns setup sessions; handoff owns none.
FAIL-CLOSED: Runtime availability may skip; source, index, and hydration failures fail.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF-REAL-MONGO-CERT
           certifies source hydration, session forwarding, exact money, and blockers.
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
from tools.eos.legal_operations.domain.process_service_billing_eligibility_authority import ProcessServiceBillingEligibility
from tools.eos.legal_operations.domain.process_service_tariff_authority import FeeLine, ServiceExecutionOutcome, TariffAssessment
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_billing_eligibility_registry import ProcessServiceBillingEligibilityRegistry
from tools.eos.legal_operations.registry.process_service_tariff_registry import ProcessServiceTariffRegistry, _record as tariff_record
from tools.eos.saas.billing.process_service_client_invoice_handoff import InvoiceReadinessStatus, assess_invoice_issuance_readiness, build_process_service_client_invoice_basis

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
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
        database = client[f"p6c_handoff_{uuid.uuid4().hex}"]
        concerns = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        lifecycle = database.get_collection("lifecycle", **concerns)
        assessments = database.get_collection("assessments", **concerns)
        eligibility = database.get_collection("eligibility", **concerns)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        ProcessServiceTariffRegistry.ensure_indexes(database.get_collection("schedules", **concerns), database.get_collection("versions", **concerns), assessments)
        ProcessServiceBillingEligibilityRegistry.ensure_indexes(eligibility)
        yield client, lifecycle, assessments, eligibility, database, concerns
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


def test_real_mongo_hydrates_p6b_and_p6a_into_blocked_basis(mongo_context: tuple[MongoClient, Any, Any, Any, Any, Any]) -> None:
    client, lifecycle, assessments, eligibility, database, concerns = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    allocated = ServiceAttempt(tenant, "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation-1")
    attempted = allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", occurred_at=BASE + timedelta(minutes=1))
    terminal = attempted.transition_to(ServiceAttemptState.COMPLETED, evidence_reference="terminal", evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=2))
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-1", executed_at=BASE + timedelta(minutes=3))
    returned = ReturnOfService.from_service_execution(instruction_id=terminal.instruction_id, service_execution=execution, return_id="return-1", generated_at=BASE + timedelta(minutes=4))
    setup = _tx(client)
    try:
        LegalOperationsLifecycleRegistry.create(District(tenant, "district-1", "District One", "ZA-GP", "district-source"), lifecycle, session=setup)
        for snapshot in (allocated, attempted, terminal):
            LegalOperationsLifecycleRegistry.create(snapshot, lifecycle, session=setup)
        LegalOperationsLifecycleRegistry.create(execution, lifecycle, session=setup, source_attempt=terminal)
        LegalOperationsLifecycleRegistry.create(returned, lifecycle, session=setup, source_attempt=terminal, source_execution=execution)
        setup.commit_transaction()
    finally:
        setup.end_session()
    return_identity = cast(str, lifecycle.find_one({"tenant_id": tenant, "entity_type": "ReturnOfService", "entity_identity": returned.return_id})["evidence_identity"])
    assessment = TariffAssessment(tenant, "assessment-1", returned.return_id, execution.service_execution_id, terminal.attempt_id, terminal.instruction_id, terminal.document_id, "district-1", "ZA-GP", "office-1", ServiceExecutionOutcome.COMPLETED, "schedule-1", "version-1", HASH, "ServiceExecution.executed_at", execution.executed_at, (FeeLine("SERVICE-001", "Service fee", "SERVICE", 1, 12500, 12500, "ZAR", "return evidence"),), "ZAR", 12500, BASE + timedelta(minutes=5), return_identity, returned.fingerprint)
    assessment_session = _tx(client)
    try:
        ProcessServiceTariffRegistry.create_assessment(assessment, assessments, session=assessment_session)
        assessment_session.commit_transaction()
    finally:
        assessment_session.end_session()
    assessment_identity = cast(str, tariff_record(assessment)["evidence_identity"])
    issue = _tx(client)
    try:
        eligibility_value = ProcessServiceBillingEligibilityRegistry.issue(tenant_id=tenant, assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=6), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=issue)
        issue.commit_transaction()
    finally:
        issue.end_session()
    evidence_identity = cast(str, eligibility.find_one({"tenant_id": tenant, "entity_identity": eligibility_value.billing_eligibility_id})["evidence_identity"])
    read_session = _tx(client)
    try:
        basis = build_process_service_client_invoice_basis(tenant_id=tenant, billing_eligibility_evidence_identity=evidence_identity, eligibility_collection=eligibility, assessment_collection=assessments, session=read_session)
        readiness = assess_invoice_issuance_readiness(basis)
        read_session.abort_transaction()
    finally:
        read_session.end_session()
    assert basis.eligible_minor_units == 12500 and basis.currency == "ZAR"
    assert basis.tariff_assessment_id == assessment.tariff_assessment_id
    assert basis.return_id == returned.return_id and basis.service_execution_id == execution.service_execution_id
    assert readiness.status is InvoiceReadinessStatus.BLOCKED
    assert "CUSTOMER_IDENTITY_REQUIRED" in readiness.blockers and "MONEY_ROUNDTRIP_UNSAFE" in readiness.blockers
    assert all(getattr(collection, "name", "") for collection in (lifecycle, assessments, eligibility))
    assert database.name.startswith("p6c_handoff_") and concerns["read_concern"].level == "majority"


# ARTIFACT: test_process_service_client_invoice_handoff_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed P6C source hydration only.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
