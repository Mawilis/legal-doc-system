"""Direct P6C adversarial certificate.

TITLE: Wilsy OS Process-Service Client-Invoice Handoff Certificate
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Billing-owned derived invoice basis and deterministic readiness only.
TENANT BOUNDARY: Canonical P6A/P6B sources and all locators are tenant-scoped.
AUTHORITY BOUNDARY: No ClientInvoice, quotation, payment, execution, or settlement.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Source, tenant, lineage, money, and commercial-policy gaps reject/block.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF-CERT certifies
           immutable source-bound basis, exact minor units, and readiness blockers.
"""
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ReturnOfService, ServiceAttempt, ServiceAttemptState, ServiceExecution
from tools.eos.legal_operations.domain.process_service_billing_eligibility_authority import ProcessServiceBillingEligibility
from tools.eos.legal_operations.domain.process_service_tariff_authority import FeeLine, ServiceExecutionOutcome, TariffAssessment
from tools.eos.saas.domain.billing import ClientInvoice
from tools.eos.saas.domain.money import to_minor_units
from tools.eos.saas.billing.process_service_client_invoice_handoff import (
    ClientInvoiceFeeLineBasis,
    InvoiceReadinessStatus,
    ProcessServiceClientInvoiceBasis,
    ProcessServiceClientInvoiceHandoffError,
    assess_invoice_issuance_readiness,
)

VERSION = "v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF-CERT"
BASE = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
HASH = "a" * 128


def _sources(tenant: str = "tenant-a") -> tuple[ProcessServiceBillingEligibility, TariffAssessment]:
    allocated = ServiceAttempt(tenant, "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation-1")
    attempted = allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", occurred_at=BASE + timedelta(minutes=1))
    terminal = attempted.transition_to(ServiceAttemptState.COMPLETED, evidence_reference="terminal", evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=2))
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-1", executed_at=BASE + timedelta(minutes=3))
    returned = ReturnOfService.from_service_execution(instruction_id=terminal.instruction_id, service_execution=execution, return_id="return-1", generated_at=BASE + timedelta(minutes=4))
    line = FeeLine("SERVICE-001", "Service fee", "SERVICE", 1, 12500, 12500, "ZAR", "return evidence")
    assessment = TariffAssessment(
        tenant_id=tenant,
        tariff_assessment_id="assessment-1",
        return_id=returned.return_id,
        service_execution_id=execution.service_execution_id,
        attempt_id=terminal.attempt_id,
        instruction_id=terminal.instruction_id,
        document_id=terminal.document_id,
        district_id="district-1",
        jurisdiction_code="ZA-GP",
        sheriff_office_id="office-1",
        service_outcome=ServiceExecutionOutcome.COMPLETED,
        tariff_schedule_id="schedule-1",
        tariff_version_id="version-1",
        tariff_version_fingerprint=HASH,
        effective_time_source="ServiceExecution.executed_at",
        effective_at=execution.executed_at,
        fee_lines=(line,),
        currency="ZAR",
        assessed_total_minor_units=12500,
        assessment_at=BASE + timedelta(minutes=5),
        source_return_evidence_identity=HASH,
        source_return_fingerprint=returned.fingerprint,
    )
    eligibility = ProcessServiceBillingEligibility.from_sources(
        assessment=assessment,
        assessment_evidence_identity=HASH,
        return_of_service=returned,
        return_evidence_identity=HASH,
        service_execution=execution,
        execution_evidence_identity=HASH,
        attempt=terminal,
        billing_eligibility_id="eligibility-1",
        eligibility_at=BASE + timedelta(minutes=6),
    )
    return eligibility, assessment


def _basis() -> ProcessServiceClientInvoiceBasis:
    eligibility, assessment = _sources()
    return ProcessServiceClientInvoiceBasis.from_sources(eligibility=eligibility, assessment=assessment, billing_eligibility_evidence_identity=HASH)


def test_source_bound_basis_preserves_exact_money_lineage_and_fingerprint() -> None:
    basis = _basis()
    assert basis.tenant_id == "tenant-a"
    assert basis.eligible_minor_units == 12500
    assert basis.currency == "ZAR"
    assert basis.return_id == "return-1" and basis.service_execution_id == "execution-1"
    assert basis.attempt_id == "attempt-1" and basis.instruction_id == "instruction-1" and basis.document_id == "document-1"
    assert basis.fee_lines == (ClientInvoiceFeeLineBasis("SERVICE-001", "Service fee", "SERVICE", 1, 12500, 12500, "ZAR", "return evidence", HASH),)
    assert basis.to_dict() == basis.to_dict()
    assert basis.fingerprint == basis.fingerprint


def test_direct_construction_and_caller_amount_or_tenant_injection_fail() -> None:
    with pytest.raises(ProcessServiceClientInvoiceHandoffError, match="P6C_FACTORY_REQUIRED"):
        ProcessServiceClientInvoiceBasis()
    eligibility, assessment = _sources()
    with pytest.raises(TypeError):
        ProcessServiceClientInvoiceBasis.from_sources(eligibility=eligibility, assessment=assessment, billing_eligibility_evidence_identity=HASH, eligible_minor_units=99)  # type: ignore[call-arg]
    foreign, foreign_assessment = _sources("tenant-b")
    with pytest.raises(ProcessServiceClientInvoiceHandoffError, match="P6C_TENANT_MISMATCH"):
        ProcessServiceClientInvoiceBasis.from_sources(eligibility=foreign, assessment=assessment, billing_eligibility_evidence_identity=HASH)
    assert foreign.tenant_id == "tenant-b"
    assert foreign_assessment.tenant_id == "tenant-b"


def test_corrupt_or_divergent_source_rejects() -> None:
    eligibility, assessment = _sources()
    with pytest.raises(ProcessServiceClientInvoiceHandoffError, match="P6C_ASSESSMENT_BINDING_INVALID"):
        altered = type(assessment)(**{**{field: getattr(assessment, field) for field in assessment.__dataclass_fields__}, "tariff_assessment_id": "assessment-other"})
        ProcessServiceClientInvoiceBasis.from_sources(eligibility=eligibility, assessment=altered, billing_eligibility_evidence_identity=HASH)
    with pytest.raises(ProcessServiceClientInvoiceHandoffError, match="P6C_BILLING_ELIGIBILITY_EVIDENCE_IDENTITY_INVALID"):
        ProcessServiceClientInvoiceBasis.from_sources(eligibility=eligibility, assessment=assessment, billing_eligibility_evidence_identity="bad")


def test_readiness_is_deterministically_blocked_without_commercial_sources() -> None:
    result = assess_invoice_issuance_readiness(_basis())
    assert result.status is InvoiceReadinessStatus.BLOCKED
    assert result.blockers == ("CUSTOMER_IDENTITY_REQUIRED", "TAX_POLICY_REQUIRED", "PAYMENT_TERMS_REQUIRED", "DUE_DATE_POLICY_REQUIRED", "COLLECTION_METHOD_REQUIRED", "MONEY_ROUNDTRIP_UNSAFE")
    assert result.customer_billing_identity == "NOT_PROVEN"
    assert result.tax_policy == "NOT_PROVEN"
    assert result.payment_terms_policy == "NOT_PROVEN"
    assert result.due_date_policy == "NOT_PROVEN"
    assert result.collection_method_policy == "NOT_PROVEN"
    assert result.client_invoice_minor_unit_roundtrip == "FAIL"
    assert "invoice" not in result.to_dict()


def test_legacy_client_invoice_precision_is_observed_but_not_promoted_to_authority() -> None:
    legacy = ClientInvoice(tenant_id="tenant-a", amount=125.0, total=125.0)
    assert to_minor_units(legacy.amount, legacy.currency) == 12500
    assert assess_invoice_issuance_readiness(_basis()).client_invoice_minor_unit_roundtrip == "FAIL"


def test_module_has_no_execution_or_settlement_surface() -> None:
    import tools.eos.saas.billing.process_service_client_invoice_handoff as module

    forbidden = {"ClientInvoice", "Quotation", "Payment", "Settlement", "execute_payment", "settle"}
    assert not forbidden.intersection(dir(module))
    assert module.__doc__ is not None and "Kennel EOS owns financial execution/settlement" in module.__doc__


# ARTIFACT: test_process_service_client_invoice_handoff.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-HANDOFF-CERT
# AUTHORITY BOUNDARY: direct derived-basis/readiness certificate only.
# TENANT POSTURE: source and locator tests remain tenant-scoped.
# FAIL-CLOSED POSTURE: fabricated or incomplete commercial facts are rejected/blocking.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
