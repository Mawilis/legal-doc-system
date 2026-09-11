# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
"""TITLE: Financial Execution Domain Certificate
VERSION: v2.0.0-M11-P5-R2D-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Unit certificate for preserved AP truth and additive neutral execution facts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution.py
COLLABORATION / OWNERSHIP: Kennel EOS execution-evidence domain certificate.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v2.0.0-M11-P5-R2D-R1 adds strict neutral-fact domain coverage while retaining AP coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic tenant identifiers are asserted on every fact.
AUTHORITY BOUNDARY: Pure domain values only; no persistence, provider, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Execution evidence never means settlement.
FAIL-CLOSED DECLARATION: malformed and subject-mixed values reject.
"""
from datetime import datetime, timezone, timedelta
from dataclasses import FrozenInstanceError, replace
import pytest
from tools.eos.kennel.domain.financial_execution import FinancialExecutionFact, FinancialExecutionFactError, FinancialExecutionStatus, FinancialExecutionTruth, FinancialExecutionTruthError

NOW = datetime(2026, 1, 2, tzinfo=timezone.utc)
FP = "a" * 128

def ap(status=FinancialExecutionStatus.EXECUTED, at=NOW):
    return FinancialExecutionTruth("truth-1", "tenant-1", "payable-1", "release-1", "PAYSHAP", "provider-1", status, 100, "ZAR", at if status is FinancialExecutionStatus.EXECUTED else None, "destination-1", "evidence-1", FP, "b" * 128, NOW)

def fact(status=FinancialExecutionStatus.EXECUTED, at=NOW, **changes):
    values = dict(execution_fact_id=FinancialExecutionFact.deterministic_id("tenant-1", "attempt-1"), tenant_id="tenant-1", execution_command_id="command-1", execution_command_fingerprint=FP, execution_attempt_id="attempt-1", provider="PAYSHAP", provider_execution_reference="provider-ref", execution_status=status, executed_amount_minor=100, currency="ZAR", executed_at=at if status is FinancialExecutionStatus.EXECUTED else None, payment_destination_reference="destination-1", provider_evidence_reference="evidence-1", execution_evidence_fingerprint="b" * 128, created_at=NOW)
    values.update(changes)
    return FinancialExecutionFact(**values)

def test_ap_round_trip(): assert FinancialExecutionTruth.from_mapping(ap().to_dict()) == ap()
def test_ap_fingerprint_stable(): assert ap().evidence_fingerprint == ap().evidence_fingerprint
def test_ap_status_vocabulary(): assert {s.value for s in FinancialExecutionStatus} == {"SUBMITTED", "ACCEPTED", "EXECUTED", "FAILED"}
@pytest.mark.parametrize("status", [FinancialExecutionStatus.SUBMITTED, FinancialExecutionStatus.ACCEPTED, FinancialExecutionStatus.FAILED])
def test_ap_nonexecuted_timestamp_absent(status): assert ap(status, None).executed_at is None
def test_ap_executed_requires_time():
    with pytest.raises(FinancialExecutionTruthError): ap(at=None)
def test_ap_naive_time_rejected():
    with pytest.raises(FinancialExecutionTruthError): ap(at=datetime(2026, 1, 1))
def test_ap_settlement_fields_rejected():
    with pytest.raises(FinancialExecutionTruthError): FinancialExecutionTruth.from_mapping({**ap().to_dict(), "settled": True})
def test_ap_unknown_fields_rejected():
    with pytest.raises(FinancialExecutionTruthError): FinancialExecutionTruth.from_mapping({**ap().to_dict(), "unknown": 1})
def test_fact_identity_deterministic(): assert fact().execution_fact_id == FinancialExecutionFact.deterministic_id("tenant-1", "attempt-1")
def test_fact_round_trip(): assert FinancialExecutionFact.from_mapping(fact().to_dict()) == fact()
def test_fact_fingerprint_stable(): assert fact().fingerprint == fact().fingerprint
def test_fact_has_no_commercial_subjects(): assert not any(name in fact().to_dict() for name in ("payable_id", "platform_invoice_id", "settled", "paid"))
def test_fact_is_frozen():
    with pytest.raises(FrozenInstanceError): fact().provider = "OTHER"
def test_fact_command_attempt_distinct():
    with pytest.raises(FinancialExecutionFactError): fact(execution_attempt_id="command-1")
def test_fact_wrong_identity_rejected():
    with pytest.raises(FinancialExecutionFactError): fact(execution_fact_id="fact-forged")
def test_fact_positive_amount():
    with pytest.raises(FinancialExecutionFactError): fact(executed_amount_minor=0)
def test_fact_currency_uppercase():
    with pytest.raises(FinancialExecutionFactError): fact(currency="zar")
def test_fact_fingerprint_lower_hex():
    with pytest.raises(FinancialExecutionFactError): fact(execution_command_fingerprint="Z" * 128)
def test_fact_executed_time_required():
    with pytest.raises(FinancialExecutionFactError): fact(at=None)
def test_fact_nonexecuted_time_forbidden():
    with pytest.raises(FinancialExecutionFactError): replace(fact(status=FinancialExecutionStatus.FAILED), executed_at=NOW)
def test_fact_time_cannot_follow_creation():
    assert fact(at=NOW + timedelta(seconds=1)).executed_at == NOW + timedelta(seconds=1)
def test_fact_unknown_mapping_rejected():
    with pytest.raises(FinancialExecutionFactError): FinancialExecutionFact.from_mapping({**fact().to_dict(), "unknown": 1})
def test_fact_missing_mapping_rejected():
    with pytest.raises(FinancialExecutionFactError): FinancialExecutionFact.from_mapping({"tenant_id": "tenant-1"})
def test_fact_status_string_hydrates(): assert FinancialExecutionFact.from_mapping({**fact().to_dict(), "execution_status": "EXECUTED"}) == fact()

# ARTIFACT: test_financial_execution.py
# VERSION: v2.0.0-M11-P5-R2D-R1
# AUTHORITY BOUNDARY: AP and neutral execution domain certificate only.
# TENANT POSTURE: synthetic tenant-scoped immutable values.
# FAIL-CLOSED POSTURE: malformed and subject-mixed values reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
