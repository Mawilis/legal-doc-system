"""P6F canonical-source ordinary real-Mongo certificate.

TITLE: Process-Service Client Invoice Issuance Canonical E2E Certificate
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Canonical P1/P2/P6A/P6B/P6D hydration composed through public P6F.
TENANT BOUNDARY: Every durable source and read is tenant-scoped.
TRANSACTION BOUNDARY: The certificate owns setup sessions; P6F never does.
AUTHORITY BOUNDARY: P6F issuance only; no quotation, payment, or settlement.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Runtime availability may skip; all post-hello product failures fail.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.1 replaces synthetic fixtures with canonical E2E proof.
"""
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import District, ServiceAttempt, ServiceAttemptState, ServiceExecution, ReturnOfService
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.domain.process_service_billing_eligibility_authority import ProcessServiceBillingEligibility
from tools.eos.legal_operations.domain.process_service_tariff_authority import TariffQuantityBasis, TariffRule, TariffSchedule, TariffVersion, assess_from_return
from tools.eos.legal_operations.registry.process_service_billing_eligibility_registry import ProcessServiceBillingEligibilityRegistry
from tools.eos.legal_operations.registry.process_service_tariff_registry import ProcessServiceTariffRegistry
from tools.eos.saas.billing.process_service_client_billing_authority import ClientBillingProfileVersion, CollectionMethod, CollectionMethodPolicy, DueDatePolicy, DueDateRule, InstructionBillingBinding, InvoiceTaxType, PaymentTerms, PaymentTermsRule, TaxCalculationScope, TaxPolicy, TaxRoundingRule, TaxTreatment
from tools.eos.saas.billing.process_service_client_billing_registry import ProcessServiceClientBillingRegistry
from tools.eos.saas.billing.process_service_client_invoice_issuance import ProcessServiceClientInvoiceIssuanceError, ProcessServiceClientInvoiceIssuanceRegistry, issue_process_service_client_invoice

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)


def _eid(collection: Any, query: dict[str, Any], *, session: Any = None) -> str:
    row = collection.find_one(query, session=session)
    assert row is not None
    return str(row["evidence_identity"])


def _seed_sources(client: MongoClient, database: Any, *, tenant: str, prefix: str) -> dict[str, Any]:
    lifecycle = database.get_collection("lifecycle")
    schedules = database.get_collection("tariff_schedules")
    versions = database.get_collection("tariff_versions")
    assessments = database.get_collection("tariff_assessments")
    eligibility = database.get_collection("billing_eligibility")
    profiles = database.get_collection("billing_profiles")
    bindings = database.get_collection("billing_bindings")
    LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
    ProcessServiceTariffRegistry.ensure_indexes(schedules, versions, assessments)
    ProcessServiceBillingEligibilityRegistry.ensure_indexes(eligibility)
    ProcessServiceClientBillingRegistry.ensure_indexes(profiles, bindings)
    session = client.start_session()
    session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    try:
        district = District(tenant, f"district-{prefix}", "Gauteng", "ZA-GP", f"district-{prefix}-evidence")
        attempt = ServiceAttempt(tenant, f"attempt-{prefix}", f"instruction-{prefix}", f"document-{prefix}", f"deputy-{prefix}", BASE, f"allocation-{prefix}")
        attempted = attempt.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference=f"attempted-{prefix}", occurred_at=BASE + timedelta(minutes=1))
        terminal = attempted.transition_to(ServiceAttemptState.COMPLETED, evidence_reference=f"terminal-{prefix}", evidence_fingerprint="a" * 128, occurred_at=BASE + timedelta(minutes=2))
        execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id=f"execution-{prefix}", executed_at=BASE + timedelta(minutes=3))
        returned = ReturnOfService.from_service_execution(instruction_id=terminal.instruction_id, service_execution=execution, return_id=f"return-{prefix}", generated_at=BASE + timedelta(minutes=4))
        for value in (district, attempt, attempted, terminal):
            LegalOperationsLifecycleRegistry.create(value, lifecycle, session=session)
        LegalOperationsLifecycleRegistry.create(execution, lifecycle, session=session, source_attempt=terminal)
        LegalOperationsLifecycleRegistry.create(returned, lifecycle, session=session, source_attempt=terminal, source_execution=execution)
        return_eid = _eid(
            lifecycle,
            {"tenant_id": tenant, "entity_type": "ReturnOfService", "entity_identity": returned.return_id},
            session=session,
        )
        schedule = TariffSchedule(tenant, f"schedule-{prefix}", district.district_id, district.jurisdiction_code, None, None, f"schedule-{prefix}-evidence")
        rule = TariffRule(f"SERVICE-{prefix}", "Process service", "SERVICE", TariffQuantityBasis.SERVICE, 12500, "ZAR", "none", "EXEMPT", f"return:{return_eid}")
        version = TariffVersion(tenant, schedule.schedule_id, f"version-{prefix}", BASE, None, (rule,), f"version-{prefix}-evidence")
        ProcessServiceTariffRegistry.create_schedule(schedule, schedules, session=session)
        ProcessServiceTariffRegistry.create_version(version, schedule, versions, session=session)
        assessment = assess_from_return(return_of_service=returned, return_evidence_identity=return_eid, schedule=schedule, tariff_version=version, assessment_id=f"assessment-{prefix}", assessment_at=BASE + timedelta(minutes=5), sheriff_office_id=f"office-{prefix}", effective_at=execution.executed_at)
        ProcessServiceTariffRegistry.create_assessment(assessment, assessments, session=session)
        assessment_eid = _eid(
            assessments,
            {"tenant_id": tenant, "entity_type": "TariffAssessment", "entity_identity": assessment.tariff_assessment_id},
            session=session,
        )
        eligible = ProcessServiceBillingEligibilityRegistry.issue(tenant_id=tenant, assessment_evidence_identity=assessment_eid, billing_eligibility_id=f"eligibility-{prefix}", eligibility_at=BASE + timedelta(minutes=6), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=session)
        eligibility_eid = _eid(
            eligibility,
            {"tenant_id": tenant, "entity_type": "ProcessServiceBillingEligibility", "entity_identity": eligible.billing_eligibility_id},
            session=session,
        )
        profile = ClientBillingProfileVersion(tenant, f"profile-{prefix}", f"profile-{prefix}-v1", f"customer-{prefix}", "Canonical Customer", None, "billing@example.test", None, "ZA-GP", "ZA-GP", TaxPolicy(f"tax-{prefix}", "tax-v1", TaxTreatment.EXEMPT, None, TaxCalculationScope.LINE, TaxRoundingRule.HALF_UP_MINOR_UNIT, False), PaymentTerms(f"terms-{prefix}", "terms-v1", PaymentTermsRule.DAYS_AFTER_ISSUE, 14), DueDatePolicy(f"due-{prefix}", "due-v1", DueDateRule.ISSUE_DATE_PLUS_PAYMENT_TERMS), CollectionMethodPolicy(f"collection-{prefix}", "collection-v1", CollectionMethod.SEND_INVOICE), BASE, None, f"profile-{prefix}-evidence", invoice_tax_type=InvoiceTaxType.VAT)
        binding = InstructionBillingBinding(tenant, f"binding-{prefix}", terminal.instruction_id, profile.billing_profile_id, profile.billing_profile_version_id, BASE + timedelta(minutes=1), f"binding-{prefix}-evidence")
        ProcessServiceClientBillingRegistry.create_profile(profile, profiles, session=session)
        ProcessServiceClientBillingRegistry.create_binding(binding, bindings, session=session)
        session.commit_transaction()
    finally:
        session.end_session()
    return {
        "tenant": tenant,
        "eligibility_eid": eligibility_eid,
        "binding_eid": _eid(
            bindings,
            {"tenant_id": tenant, "entity_type": "InstructionBillingBinding", "entity_identity": binding.binding_id},
            session=None,
        ),
        "profile_eid": _eid(
            profiles,
            {"tenant_id": tenant, "entity_type": "ClientBillingProfileVersion", "entity_identity": profile.billing_profile_version_id},
            session=None,
        ),
        "lifecycle": lifecycle,
        "assessments": assessments,
        "eligibility": eligibility,
        "profiles": profiles,
        "bindings": bindings,
    }


@pytest.fixture()
def mongo() -> Iterator[tuple[MongoClient, Any]]:
    client = MongoClient(URI, serverSelectionTimeoutMS=3000, replicaSet=REPLICA_SET)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"MONGO_RUNTIME_UNAVAILABLE: {type(error).__name__}")
        if hello.get("setName") != REPLICA_SET:
            pytest.skip(f"MONGO_REPLICA_SET_UNAVAILABLE: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
        database = client.get_database("p6f_e2e_" + uuid4().hex[:20], read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
        yield client, database
    finally:
        try:
            if database is not None:
                client.drop_database(database.name)
        finally:
            client.close()


def _issue(client: MongoClient, sources: dict[str, Any], invoices: Any, issuance: Any, *, clock: Any) -> tuple[Any, Any]:
    session = client.start_session()
    session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    try:
        result = issue_process_service_client_invoice(tenant_id=sources["tenant"], billing_eligibility_evidence_identity=sources["eligibility_eid"], binding_evidence_identity=sources["binding_eid"], profile_evidence_identity=sources["profile_eid"], eligibility_collection=sources["eligibility"], assessment_collection=sources["assessments"], profile_collection=sources["profiles"], binding_collection=sources["bindings"], client_invoice_collection=invoices, issuance_collection=issuance, session=session, clock=clock)
        session.commit_transaction()
        return result
    except Exception:
        if session.in_transaction:
            session.abort_transaction()
        raise
    finally:
        session.end_session()


def test_real_mongo_canonical_e2e_replay_corruption_and_abort(mongo: tuple[MongoClient, Any]) -> None:
    client, database = mongo
    sources = _seed_sources(client, database, tenant="tenant-a", prefix="a")
    invoices = database.get_collection("client_invoices")
    issuance = database.get_collection("issuance")
    ProcessServiceClientInvoiceIssuanceRegistry.ensure_indexes(issuance)
    fixed = BASE + timedelta(hours=1)
    invoice, evidence = _issue(client, sources, invoices, issuance, clock=lambda: fixed)
    assert invoices.count_documents({"tenant_id": "tenant-a"}) == 1
    assert issuance.count_documents({"tenant_id": "tenant-a"}) == 1
    assert evidence.invoice_id == invoice.invoice_id
    assert evidence.billing_eligibility_id == "eligibility-a"
    assert evidence.tariff_assessment_id == "assessment-a"
    assert evidence.profile_version_id == "profile-a-v1"
    assert evidence.binding_evidence_identity == sources["binding_eid"]
    assert evidence.profile_evidence_identity == sources["profile_eid"]
    stored = issuance.find_one({"tenant_id": "tenant-a", "entity_identity": evidence.issuance_id})
    assert stored is not None
    assert stored["fingerprint"] == evidence.fingerprint
    assert stored["payload"]["issuance_id"] == evidence.issuance_id
    durable_evidence_identity = stored["evidence_identity"]
    assert (
        type(durable_evidence_identity) is str
        and len(durable_evidence_identity) == 128
        and all(character in "0123456789abcdef" for character in durable_evidence_identity)
    )
    hydrated = ProcessServiceClientInvoiceIssuanceRegistry.get("tenant-a", durable_evidence_identity, issuance)
    assert hydrated.to_dict() == evidence.to_dict()
    replay_invoice, replay_evidence = _issue(client, sources, invoices, issuance, clock=lambda: (_ for _ in ()).throw(AssertionError("replay clock used")))
    assert replay_invoice.to_dict() == invoice.to_dict()
    assert replay_evidence.to_dict() == evidence.to_dict()
    with pytest.raises(ProcessServiceClientInvoiceIssuanceError, match="P6F_NOT_FOUND"):
        ProcessServiceClientInvoiceIssuanceRegistry.get("tenant-b", durable_evidence_identity, issuance)
    pristine = issuance.find_one({"tenant_id": "tenant-a"})
    assert pristine is not None
    issuance.update_one({"_id": pristine["_id"]}, {"$set": {"fingerprint": "b" * 128}})
    with pytest.raises(ProcessServiceClientInvoiceIssuanceError):
        ProcessServiceClientInvoiceIssuanceRegistry.get("tenant-a", durable_evidence_identity, issuance)
    issuance.replace_one({"_id": pristine["_id"]}, pristine)
    abort_sources = _seed_sources(client, database, tenant="tenant-abort", prefix="abort")
    abort_invoices = database.get_collection("client_invoices")
    abort_issuance = database.get_collection("issuance")
    session = client.start_session()
    session.start_transaction(write_concern=WriteConcern(w="majority", j=True))
    try:
        issue_process_service_client_invoice(tenant_id=abort_sources["tenant"], billing_eligibility_evidence_identity=abort_sources["eligibility_eid"], binding_evidence_identity=abort_sources["binding_eid"], profile_evidence_identity=abort_sources["profile_eid"], eligibility_collection=abort_sources["eligibility"], assessment_collection=abort_sources["assessments"], profile_collection=abort_sources["profiles"], binding_collection=abort_sources["bindings"], client_invoice_collection=abort_invoices, issuance_collection=abort_issuance, session=session, clock=lambda: fixed)
        session.abort_transaction()
    finally:
        session.end_session()
    assert abort_invoices.count_documents({"tenant_id": "tenant-abort"}) == 0
    assert abort_issuance.count_documents({"tenant_id": "tenant-abort"}) == 0


# ARTIFACT: test_process_service_client_invoice_issuance_real_mongo.py
# VERSION: v1.0.1-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: canonical persistence certificate only; no payment or settlement.
# TENANT POSTURE: every source and lookup is tenant-scoped with silent foreign absence.
# FAIL-CLOSED POSTURE: unavailable runtime skips; source, replay, corruption, and abort failures fail.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
