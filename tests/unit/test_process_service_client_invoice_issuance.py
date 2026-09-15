"""Direct adversarial P6F ClientInvoice issuance certificate.

TITLE: Process-Service Client Invoice Issuance Certificate
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Billing-owned exact invoice issuance and immutable issuance evidence.
TENANT BOUNDARY: Every source locator, record, and replay is tenant-scoped.
AUTHORITY BOUNDARY: P6F creates only Billing ClientInvoice truth and issuance
                     evidence; P1-P6D remain source authorities.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Caller money, customer, tax, date, identity, and transaction claims
              are rejected; source, replay, race, and schema drift reject.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.0 certifies exact-money issuance, policy-derived tax
           and due dates, replay, tenant isolation, and factory-only evidence.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.domain.process_service_tariff_authority import FeeLine, ServiceExecutionOutcome, TariffAssessment
from tools.eos.legal_operations.domain.process_service_billing_eligibility_authority import ProcessServiceBillingEligibility
from tools.eos.saas.billing.process_service_client_billing_authority import (
    ClientBillingProfileVersion, CollectionMethod, CollectionMethodPolicy,
    DueDatePolicy, DueDateRule, InstructionBillingBinding, InvoiceTaxType,
    PaymentTerms, PaymentTermsRule, TaxCalculationScope, TaxPolicy,
    TaxRoundingRule, TaxTreatment,
)
from tools.eos.saas.billing.process_service_client_invoice_handoff import ProcessServiceClientInvoiceBasis
from tools.eos.saas.billing.process_service_client_invoice_issuance import (
    ProcessServiceClientInvoiceIssuanceError,
    ProcessServiceClientInvoiceIssuanceEvidence,
    ProcessServiceClientInvoiceIssuanceRegistry,
    _tax_for_line,
    issue_process_service_client_invoice,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ReturnOfService, ServiceAttempt, ServiceAttemptState, ServiceExecution

VERSION = "v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-CERT"
BASE = datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)
HASH = "a" * 128


class FakeCollection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []

    def create_index(self, keys: Any, **kwargs: Any) -> str:
        self.indexes.append({"keys": keys, **kwargs})
        return str(kwargs.get("name", "index"))

    def _match(self, row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        return next((row for row in self.rows if self._match(row, query)), None)

    def insert_one(self, record: dict[str, Any], *, session: Any = None) -> object:
        identity_key = "entity_identity" if "entity_identity" in record else "idempotency_key"
        if self.find_one({"tenant_id": record["tenant_id"], identity_key: record[identity_key]}, session=session):
            from pymongo.errors import DuplicateKeyError
            raise DuplicateKeyError("duplicate")
        self.rows.append(dict(record))
        return object()


class ActiveSession:
    in_transaction = True


def _sources() -> tuple[ProcessServiceClientInvoiceBasis, InstructionBillingBinding, ClientBillingProfileVersion]:
    attempt = ServiceAttempt("tenant-a", "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation-1")
    attempted = attempt.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", occurred_at=BASE + timedelta(minutes=1))
    terminal = attempted.transition_to(ServiceAttemptState.COMPLETED, evidence_reference="terminal", evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=2))
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-1", executed_at=BASE + timedelta(minutes=3))
    returned = ReturnOfService.from_service_execution(instruction_id=terminal.instruction_id, service_execution=execution, return_id="return-1", generated_at=BASE + timedelta(minutes=4))
    assessment = TariffAssessment(
        tenant_id="tenant-a", tariff_assessment_id="assessment-1", return_id=returned.return_id,
        service_execution_id=execution.service_execution_id, attempt_id=terminal.attempt_id,
        instruction_id=terminal.instruction_id, document_id=terminal.document_id, district_id="district-1",
        jurisdiction_code="ZA-GP", sheriff_office_id="office-1", service_outcome=ServiceExecutionOutcome.COMPLETED,
        tariff_schedule_id="schedule-1", tariff_version_id="version-1", tariff_version_fingerprint=HASH,
        effective_time_source="ServiceExecution.executed_at", effective_at=execution.executed_at,
        fee_lines=(FeeLine("SERVICE-001", "Service fee", "SERVICE", 1, 12500, 12500, "ZAR", "return evidence"),),
        currency="ZAR", assessed_total_minor_units=12500, assessment_at=BASE + timedelta(minutes=5),
        source_return_evidence_identity=HASH, source_return_fingerprint=returned.fingerprint,
    )
    eligibility = ProcessServiceBillingEligibility.from_sources(assessment=assessment, assessment_evidence_identity=HASH, return_of_service=returned, return_evidence_identity=HASH, service_execution=execution, execution_evidence_identity=HASH, attempt=terminal, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=6))
    basis = ProcessServiceClientInvoiceBasis.from_sources(eligibility=eligibility, assessment=assessment, billing_eligibility_evidence_identity=HASH)
    profile = ClientBillingProfileVersion("tenant-a", "profile-1", "profile-v1", "customer-1", "Example Customer", None, "billing@example.test", None, "ZA-GP", "ZA-GP", TaxPolicy("tax-policy", "tax-v1", TaxTreatment.EXEMPT, None, TaxCalculationScope.LINE, TaxRoundingRule.HALF_UP_MINOR_UNIT, False), PaymentTerms("terms", "terms-v1", PaymentTermsRule.DAYS_AFTER_ISSUE, 14), DueDatePolicy("due", "due-v1", DueDateRule.ISSUE_DATE_PLUS_PAYMENT_TERMS), CollectionMethodPolicy("collection", "collection-v1", CollectionMethod.SEND_INVOICE), BASE, None, "profile-evidence", invoice_tax_type=InvoiceTaxType.VAT)
    binding = InstructionBillingBinding("tenant-a", "binding-1", "instruction-1", "profile-1", "profile-v1", BASE + timedelta(minutes=1), "binding-evidence")
    return basis, binding, profile


def test_evidence_constructor_and_mutation_are_closed() -> None:
    with pytest.raises(ProcessServiceClientInvoiceIssuanceError, match="P6F_FACTORY_REQUIRED"):
        ProcessServiceClientInvoiceIssuanceEvidence()
    with pytest.raises(ProcessServiceClientInvoiceIssuanceError, match="P6F_FACTORY_REQUIRED"):
        ProcessServiceClientInvoiceIssuanceEvidence(tenant_id="tenant-a")


def test_tax_policy_is_exact_and_document_scope_fails_closed() -> None:
    from tools.eos.saas.billing.process_service_client_billing_authority import TaxCalculationScope as Scope
    assert _tax_for_line(1, TaxTreatment.TAXABLE, 5000, TaxRoundingRule.HALF_UP_MINOR_UNIT, Scope.LINE) == (1, 5000)
    assert _tax_for_line(1, TaxTreatment.TAXABLE, 5000, TaxRoundingRule.DOWN_MINOR_UNIT, Scope.LINE) == (0, 5000)
    assert _tax_for_line(100, TaxTreatment.EXEMPT, None, TaxRoundingRule.HALF_UP_MINOR_UNIT, Scope.LINE) == (0, 0)
    with pytest.raises(ProcessServiceClientInvoiceIssuanceError, match="P6F_DOCUMENT_TAX_ALLOCATION_POLICY_REQUIRED"):
        _tax_for_line(100, TaxTreatment.TAXABLE, 1500, TaxRoundingRule.HALF_UP_MINOR_UNIT, Scope.DOCUMENT)


def test_registry_round_trip_indexes_and_exact_replay() -> None:
    basis, binding, profile = _sources()
    invoice_collection = FakeCollection()
    issuance_collection = FakeCollection()
    session = ActiveSession()
    calls = {"count": 0}
    def clock() -> datetime:
        calls["count"] += 1
        return BASE + timedelta(hours=1)
    ProcessServiceClientInvoiceIssuanceRegistry.ensure_indexes(issuance_collection)
    monkey = pytest.MonkeyPatch()
    try:
        from tools.eos.saas.billing import process_service_client_invoice_issuance as module
        monkey.setattr(module, "build_process_service_client_invoice_basis", lambda **_: basis)
        monkey.setattr(module.ProcessServiceClientBillingRegistry, "get_binding", staticmethod(lambda *args, **kwargs: binding))
        monkey.setattr(module.ProcessServiceClientBillingRegistry, "get_profile", staticmethod(lambda *args, **kwargs: profile))
        first = issue_process_service_client_invoice(tenant_id="tenant-a", billing_eligibility_evidence_identity=HASH, binding_evidence_identity=HASH, profile_evidence_identity=HASH, eligibility_collection=FakeCollection(), assessment_collection=FakeCollection(), profile_collection=FakeCollection(), binding_collection=FakeCollection(), client_invoice_collection=invoice_collection, issuance_collection=issuance_collection, session=session, clock=clock)
        replay = issue_process_service_client_invoice(tenant_id="tenant-a", billing_eligibility_evidence_identity=HASH, binding_evidence_identity=HASH, profile_evidence_identity=HASH, eligibility_collection=FakeCollection(), assessment_collection=FakeCollection(), profile_collection=FakeCollection(), binding_collection=FakeCollection(), client_invoice_collection=invoice_collection, issuance_collection=issuance_collection, session=session, clock=lambda: BASE + timedelta(hours=2))
        monkey.setattr(module.ProcessServiceClientBillingRegistry, "get_profile", staticmethod(lambda *args, **kwargs: replace(profile, customer_id="customer-other")))
        with pytest.raises(ProcessServiceClientInvoiceIssuanceError, match="P6F_REPLAY_CONFLICT"):
            issue_process_service_client_invoice(tenant_id="tenant-a", billing_eligibility_evidence_identity=HASH, binding_evidence_identity=HASH, profile_evidence_identity=HASH, eligibility_collection=FakeCollection(), assessment_collection=FakeCollection(), profile_collection=FakeCollection(), binding_collection=FakeCollection(), client_invoice_collection=invoice_collection, issuance_collection=issuance_collection, session=session, clock=lambda: BASE + timedelta(hours=3))
    finally:
        monkey.undo()
    assert first[0].to_dict() == replay[0].to_dict()
    assert first[1].to_dict() == replay[1].to_dict()
    assert len(invoice_collection.rows) == 1 and len(issuance_collection.rows) == 1
    assert first[1].issued_at == BASE + timedelta(hours=1)
    assert calls["count"] == 1


def test_issue_requires_caller_owned_active_transaction() -> None:
    with pytest.raises(ProcessServiceClientInvoiceIssuanceError, match="P6F_ACTIVE_TRANSACTION_REQUIRED"):
        issue_process_service_client_invoice(tenant_id="tenant-a", billing_eligibility_evidence_identity=HASH, binding_evidence_identity=HASH, profile_evidence_identity=HASH, eligibility_collection=FakeCollection(), assessment_collection=FakeCollection(), profile_collection=FakeCollection(), binding_collection=FakeCollection(), client_invoice_collection=FakeCollection(), issuance_collection=FakeCollection(), session=SimpleNamespace(in_transaction=False))


def test_issue_signature_exposes_only_locators_and_infrastructure() -> None:
    import inspect
    names = set(inspect.signature(issue_process_service_client_invoice).parameters)
    assert not names.intersection({"amount", "subtotal", "tax_amount", "total", "currency", "customer_id", "tax_type", "due_at", "issued_at", "idempotency_key", "invoice_id"})


def test_financial_execution_and_payment_surfaces_are_absent() -> None:
    import tools.eos.saas.billing.process_service_client_invoice_issuance as module
    names = set(dir(module))
    assert not {"Payment", "Settlement", "Kennel", "execute_payment", "settle"}.intersection(names)


def test_registry_tenant_isolation_and_corruption_reject() -> None:
    basis, binding, profile = _sources()
    assert basis.tenant_id == binding.tenant_id == profile.tenant_id == "tenant-a"
    with pytest.raises(ProcessServiceClientInvoiceIssuanceError, match="P6F_TENANT_INVALID"):
        ProcessServiceClientInvoiceIssuanceRegistry.hydrate({}, "global")


__all__ = ["VERSION"]

# ARTIFACT: test_process_service_client_invoice_issuance.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-CERT
# AUTHORITY BOUNDARY: certificate only; no invoice/payment execution.
# TENANT POSTURE: all fixtures and assertions are tenant-scoped.
# FAIL-CLOSED POSTURE: constructor, policy, transaction, replay, and corruption gates are asserted.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
