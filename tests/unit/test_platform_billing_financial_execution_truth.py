# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
"""TITLE: Platform Billing Financial Execution Truth Certificate
VERSION: v2.0.0-M11-P5-R2D-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Certify strict neutral-fact to Platform-command evidence projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_financial_execution_truth.py
COLLABORATION / OWNERSHIP: Kennel EOS Platform Billing evidence certificate.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v2.0.0-M11-P5-R2D-R1 certifies typed Platform provenance and correlation firewalls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every fixture and projection is tenant-scoped.
AUTHORITY BOUNDARY: Generic Platform command plus neutral fact only.
FINANCIAL AUTHORITY BOUNDARY: No provider execution, settlement, paid state, or receivable closure.
FAIL-CLOSED DECLARATION: Wrong family, missing fields, and correlation drift reject.
"""
from datetime import datetime, timezone
import pytest
from tools.eos.kennel.domain.financial_execution import FinancialExecutionFact, FinancialExecutionStatus
from tools.eos.kennel.domain.financial_execution_command import FinancialExecutionCommand, PlatformBillingCommandSource, AccountsPayableCommandSource
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformBillingFinancialExecutionTruth, PlatformBillingFinancialExecutionTruthError, PlatformExecutionStatus

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc); FP = "a" * 128; RF = "b" * 128; AF = "c" * 128
def command(platform=True):
    source = PlatformBillingCommandSource("request-1", FP, "routing-1", RF, "invoice-1", "release-1", AF, "PAYSHAP") if platform else AccountsPayableCommandSource("request-1", FP, "selection-1", RF, "payable-1", "release-1", "PAYSHAP")
    return FinancialExecutionCommand("tenant-1", "command-1", "idem-1", 100, "ZAR", "destination-1", source, "PAYSHAP", NOW)
def execution_fact(c=None, **changes):
    c = c or command(); values = dict(execution_fact_id=FinancialExecutionFact.deterministic_id("tenant-1", "attempt-1"), tenant_id="tenant-1", execution_command_id="command-1", execution_command_fingerprint=c.fingerprint, execution_attempt_id="attempt-1", provider="PAYSHAP", provider_execution_reference="provider-ref", execution_status=FinancialExecutionStatus.EXECUTED, executed_amount_minor=100, currency="ZAR", executed_at=NOW, payment_destination_reference="destination-1", provider_evidence_reference="evidence-1", execution_evidence_fingerprint="d" * 128, created_at=NOW); values.update(changes); return FinancialExecutionFact(**values)
def truth(): return PlatformBillingFinancialExecutionTruth.from_execution_fact(execution_fact(), command())
def test_projection_type(): assert isinstance(truth(), PlatformBillingFinancialExecutionTruth)
def test_platform_invoice_projection(): assert truth().platform_invoice_id == "invoice-1"
def test_request_provenance(): assert truth().execution_request_id == "request-1" and truth().execution_request_fingerprint == FP
def test_routing_provenance(): assert truth().routing_decision_id == "routing-1" and truth().routing_decision_fingerprint == RF
def test_release_provenance(): assert truth().release_authorization_id == "release-1" and truth().release_authorization_fingerprint == AF
def test_command_provenance(): assert truth().execution_command_id == "command-1" and truth().execution_command_fingerprint == command().fingerprint
def test_fact_provenance(): assert truth().source_execution_fact_id == execution_fact().execution_fact_id
def test_fact_fingerprint_provenance(): assert truth().source_execution_fact_fingerprint == execution_fact().fingerprint
def test_provider_projection(): assert truth().provider == "PAYSHAP" and truth().provider_execution_reference == "provider-ref"
def test_amount_currency_destination(): assert (truth().executed_amount_minor, truth().currency, truth().payment_destination_reference) == (100, "ZAR", "destination-1")
def test_status_projection(): assert truth().execution_status is PlatformExecutionStatus.EXECUTED
def test_no_payable_field(): assert not hasattr(truth(), "payable_id")
def test_no_settlement_field(): assert "settled" not in truth().to_dict()
def test_round_trip(): assert PlatformBillingFinancialExecutionTruth.from_mapping(truth().to_dict()) == truth()
def test_fingerprint_stable(): assert truth().fingerprint == truth().fingerprint
def test_execution_identity_canonical(): assert truth().execution_truth_id == "platform-truth-request-1"
def test_ap_command_rejected():
    with pytest.raises(PlatformBillingFinancialExecutionTruthError): PlatformBillingFinancialExecutionTruth.from_execution_fact(execution_fact(command(False)), command(False))
def test_fact_tenant_mismatch_rejected():
    bad = execution_fact(tenant_id="other", execution_fact_id=FinancialExecutionFact.deterministic_id("other", "attempt-1"))
    with pytest.raises(PlatformBillingFinancialExecutionTruthError): PlatformBillingFinancialExecutionTruth.from_execution_fact(bad, command())
def test_fact_command_mismatch_rejected():
    with pytest.raises(PlatformBillingFinancialExecutionTruthError): PlatformBillingFinancialExecutionTruth.from_execution_fact(execution_fact(execution_command_id="other"), command())
def test_fact_provider_mismatch_rejected():
    with pytest.raises(PlatformBillingFinancialExecutionTruthError): PlatformBillingFinancialExecutionTruth.from_execution_fact(execution_fact(provider="OTHER"), command())
def test_fact_destination_mismatch_rejected():
    with pytest.raises(PlatformBillingFinancialExecutionTruthError): PlatformBillingFinancialExecutionTruth.from_execution_fact(execution_fact(payment_destination_reference="other"), command())
def test_unknown_mapping_rejected():
    with pytest.raises(PlatformBillingFinancialExecutionTruthError): PlatformBillingFinancialExecutionTruth.from_mapping({**truth().to_dict(), "unknown": 1})
def test_legacy_source_names_rejected():
    with pytest.raises(PlatformBillingFinancialExecutionTruthError): PlatformBillingFinancialExecutionTruth.from_mapping({**truth().to_dict(), "source_financial_execution_truth_id": "old"})

# ARTIFACT: test_platform_billing_financial_execution_truth.py
# VERSION: v2.0.0-M11-P5-R2D-R1
# AUTHORITY BOUNDARY: Platform execution-evidence projection certificate only.
# TENANT POSTURE: synthetic tenant-scoped immutable values.
# FAIL-CLOSED POSTURE: mixed-family and divergent source material reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
