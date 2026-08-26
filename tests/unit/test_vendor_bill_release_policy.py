"""WILSY OS — VENDOR BILL RELEASE POLICY UNIT CERTIFICATION
Version: v1.0.0-VENDOR-BILL-RELEASE-POLICY-UNIT-CERT
Authority: Wilsy OS Core Governance | Classification: Institutional Artifact — Production Certification
EPITOME: Pure fail-closed financial-authority policy certification.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_vendor_bill_release_policy.py
COLLABORATION: Wilson Khanyezi — Founder / Chief Architect; AI Engineering (Codex)
Date: 2026-08-26 | CHANGELOG: initial R2B-03 policy suite
COMPLIANCE: POPIA §19 | GDPR §32 | SOC2 CC7.2
APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
"""

from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timezone
import hashlib
import json
from typing import Any
import inspect

import pytest

from tools.eos.saas.domain.financial_approval_effective_result import (
    FinancialApprovalEffectiveResult, FinancialApprovalEffectiveState, FinancialApprovalRequirementResult,
)
from tools.eos.saas.domain.financial_approval_policy_evaluation import FinancialApprovalPolicySubjectType
from tools.eos.saas.domain.vendor_bill import VendorBill, VendorBillApprovalState, VendorBillObligationState
from tools.eos.saas.domain.vendor_bill_release_policy import (
    VERSION, VendorBillReleaseEligibilityDecision, VendorBillReleaseIneligibilityReason,
    VendorBillReleasePolicyError, evaluate_vendor_bill_release_eligibility,
    fingerprint_financial_approval_effective_result,
)


def make_bill(**changes: Any) -> VendorBill:
    """Description: build a legal deterministic VendorBill fixture.

    Collaboration: supplies hydrated obligation snapshots to pure policy evaluation.
    Institutional: fixed UTC timestamps and accounting dates avoid environmental drift.
    Returns: canonical VendorBill.
    """
    values: dict[str, Any] = dict(tenant_id="tenant-a", vendor_id="vendor-a", payable_id="payable-a", gross_amount_minor=1000, currency="ZAR", issue_date=date(2026, 1, 1), due_date=date(2026, 1, 31), obligation_state=VendorBillObligationState.OPEN, approval_state=VendorBillApprovalState.APPROVED, approval_projection_revision=1, approval_effective_result_id="result-a", approval_policy_reference="policy-a", revision=1, created_at=datetime(2026, 1, 1, tzinfo=timezone.utc), updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc), received_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    values.update(changes)
    return VendorBill(**values)


def make_result(**changes: Any) -> FinancialApprovalEffectiveResult:
    """Create a deterministic approved effective result fixture."""
    values: dict[str, Any] = dict(tenant_id="tenant-a", result_id="result-a", subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL, subject_id="payable-a", subject_revision=1, evaluation_id="evaluation-a", approval_policy_reference="policy-a", approval_policy_version="policy-v1", effective_state=FinancialApprovalEffectiveState.APPROVED, evaluated_at=datetime(2026, 1, 1, tzinfo=timezone.utc), created_at=datetime(2026, 1, 1, tzinfo=timezone.utc), requirement_results=(FinancialApprovalRequirementResult("req-a", "actor", 1, 1, True, ("actor-a",)),), counted_decision_ids=("decision-a",), source_evidence_fingerprint="a" * 128)
    values.update(changes)
    return FinancialApprovalEffectiveResult(**values)


def test_version_and_fingerprint_contract():
    """Description: version and SHA3-512 evidence binding are stable.

    Institutional: fingerprint is distinct from source_evidence_fingerprint.
    """
    result = make_result()
    expected = hashlib.sha3_512(json.dumps(result.to_persistence_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()
    assert VERSION == "v1.0.1-VENDOR-BILL-RELEASE-POLICY"
    assert fingerprint_financial_approval_effective_result(result) == expected
    assert fingerprint_financial_approval_effective_result(result) != result.source_evidence_fingerprint
    bad_result: Any = object()
    with pytest.raises(VendorBillReleasePolicyError):
        fingerprint_financial_approval_effective_result(bad_result)


def test_eligible_case_and_immutability():
    """Description: complete current snapshots can be eligible with reservation proof.

    Institutional: eligibility is prerequisite evidence, never execution truth.
    """
    decision = evaluate_vendor_bill_release_eligibility(make_bill(), make_result(), 400, "ZAR", 1, 0)
    assert decision == VendorBillReleaseEligibilityDecision(True, VendorBillReleaseIneligibilityReason.ELIGIBLE)
    with pytest.raises(FrozenInstanceError):
        setattr(decision, "eligible", False)


@pytest.mark.parametrize("state", list(VendorBillObligationState))
def test_obligation_state_matrix(state):
    """Description: only OPEN obligations are release candidates.

    Institutional: lifecycle boundaries fail closed.
    """
    kwargs = {"obligation_state": state}
    if state is VendorBillObligationState.PARTIALLY_SETTLED:
        kwargs["outstanding_amount_minor"] = 500
    elif state in (VendorBillObligationState.SETTLED, VendorBillObligationState.VOIDED):
        kwargs.update(outstanding_amount_minor=0, approval_state=VendorBillApprovalState.NOT_REQUIRED, approval_effective_result_id=None, approval_projection_revision=0)
    decision = evaluate_vendor_bill_release_eligibility(make_bill(**kwargs), make_result(), 100, "ZAR", kwargs.get("approval_projection_revision", 1), 0)
    assert decision.reason is (VendorBillReleaseIneligibilityReason.ELIGIBLE if state is VendorBillObligationState.OPEN else VendorBillReleaseIneligibilityReason.INVALID_OBLIGATION_STATE)


@pytest.mark.parametrize("reason", [VendorBillReleaseIneligibilityReason.APPROVAL_NOT_APPROVED])
def test_approval_and_binding_matrix(reason):
    """Description: approval, tenant, subject, policy, currency, and freshness bind exactly.

    Institutional: historical or cross-tenant evidence cannot authorize release.
    """
    assert evaluate_vendor_bill_release_eligibility(make_bill(approval_state=VendorBillApprovalState.PENDING), make_result(), 100, "ZAR", 1, 0).reason is reason
    assert evaluate_vendor_bill_release_eligibility(make_bill(), make_result(tenant_id="tenant-b"), 100, "ZAR", 1, 0).reason is VendorBillReleaseIneligibilityReason.APPROVAL_TENANT_MISMATCH
    assert evaluate_vendor_bill_release_eligibility(make_bill(), make_result(approval_policy_reference="other"), 100, "ZAR", 1, 0).reason is VendorBillReleaseIneligibilityReason.APPROVAL_POLICY_MISMATCH
    assert evaluate_vendor_bill_release_eligibility(make_bill(), make_result(), 100, "USD", 1, 0).reason is VendorBillReleaseIneligibilityReason.CURRENCY_MISMATCH
    assert evaluate_vendor_bill_release_eligibility(make_bill(), None, 100, "ZAR", 1, 0).reason is VendorBillReleaseIneligibilityReason.CURRENT_APPROVAL_RESULT_MISSING
    assert evaluate_vendor_bill_release_eligibility(make_bill(), make_result(), 100, "ZAR", 2, 0).reason is VendorBillReleaseIneligibilityReason.STALE_APPROVAL_PROJECTION


def test_amount_reservation_and_type_fail_closed():
    """Description: amount and reservation rules fail closed at boundaries.

    Institutional: cumulative authority cannot exceed outstanding balance.
    """
    bill, result = make_bill(), make_result()
    assert evaluate_vendor_bill_release_eligibility(bill, result, 100, "ZAR", 1, None).reason is VendorBillReleaseIneligibilityReason.RESERVATION_REQUIRED
    assert evaluate_vendor_bill_release_eligibility(bill, result, 1001, "ZAR", 1, 0).reason is VendorBillReleaseIneligibilityReason.INVALID_RELEASE_AMOUNT
    assert evaluate_vendor_bill_release_eligibility(bill, result, 600, "ZAR", 1, 500).reason is VendorBillReleaseIneligibilityReason.CUMULATIVE_AUTHORITY_EXCEEDED
    for amount in (0, -1, 1.2, True, "1"):
        amount_any: Any = amount
        with pytest.raises(VendorBillReleasePolicyError): evaluate_vendor_bill_release_eligibility(bill, result, amount_any, "ZAR", 1, 0)
    bad_bill: Any = object()
    with pytest.raises(VendorBillReleasePolicyError): evaluate_vendor_bill_release_eligibility(bad_bill, result, 1, "ZAR", 1, 0)


def test_exported_contract_and_reason_values():
    """Description: exported policy symbols and reason strings are stable.

    Institutional: callers can safely classify every fail-closed outcome.
    """
    assert callable(fingerprint_financial_approval_effective_result)
    assert callable(evaluate_vendor_bill_release_eligibility)
    expected = ["ELIGIBLE", "INVALID_OBLIGATION_STATE", "APPROVAL_NOT_APPROVED", "CURRENT_APPROVAL_RESULT_MISSING", "CURRENT_APPROVAL_RESULT_MISMATCH", "APPROVAL_TENANT_MISMATCH", "APPROVAL_SUBJECT_MISMATCH", "APPROVAL_REVISION_MISMATCH", "APPROVAL_POLICY_MISMATCH", "APPROVAL_RESULT_NOT_APPROVED", "CURRENCY_MISMATCH", "INVALID_RELEASE_AMOUNT", "RESERVATION_REQUIRED", "CUMULATIVE_AUTHORITY_EXCEEDED", "STALE_APPROVAL_PROJECTION"]
    assert [reason.value for reason in VendorBillReleaseIneligibilityReason] == expected


def test_current_result_subject_revision_and_projection_bindings():
    """Description: current result identity, subject, revision, and freshness bind exactly.

    Institutional: historical or cross-revision evidence cannot authorize release.
    """
    bill, result = make_bill(), make_result()
    assert evaluate_vendor_bill_release_eligibility(bill, None, 1, "ZAR", 1, 0).reason is VendorBillReleaseIneligibilityReason.CURRENT_APPROVAL_RESULT_MISSING
    assert evaluate_vendor_bill_release_eligibility(bill, replace(result, result_id="historical"), 1, "ZAR", 1, 0).reason is VendorBillReleaseIneligibilityReason.CURRENT_APPROVAL_RESULT_MISMATCH
    assert evaluate_vendor_bill_release_eligibility(bill, replace(result, subject_id="other"), 1, "ZAR", 1, 0).reason is VendorBillReleaseIneligibilityReason.APPROVAL_SUBJECT_MISMATCH
    assert evaluate_vendor_bill_release_eligibility(replace(bill, revision=2, approval_effective_result_id="result-a"), result, 1, "ZAR", 1, 0).reason is VendorBillReleaseIneligibilityReason.APPROVAL_REVISION_MISMATCH
    assert evaluate_vendor_bill_release_eligibility(bill, result, 1, "ZAR", 0, 0).reason is VendorBillReleaseIneligibilityReason.STALE_APPROVAL_PROJECTION
    assert evaluate_vendor_bill_release_eligibility(bill, result, 1, "ZAR", 2, 0).reason is VendorBillReleaseIneligibilityReason.STALE_APPROVAL_PROJECTION


@pytest.mark.parametrize("state", [VendorBillApprovalState.NOT_REQUIRED, VendorBillApprovalState.PENDING, VendorBillApprovalState.REJECTED])
def test_complete_approval_state_matrix(state):
    """Description: every non-approved bill approval state is ineligible.

    Institutional: approval state must be explicitly approved before release.
    """
    bill = make_bill(approval_state=state, approval_effective_result_id=None, approval_projection_revision=0)
    assert evaluate_vendor_bill_release_eligibility(bill, make_result(), 1, "ZAR", 0, 0).reason is VendorBillReleaseIneligibilityReason.APPROVAL_NOT_APPROVED


@pytest.mark.parametrize("effective_state, expected", [(FinancialApprovalEffectiveState.PENDING, VendorBillReleaseIneligibilityReason.APPROVAL_RESULT_NOT_APPROVED), (FinancialApprovalEffectiveState.REJECTED, VendorBillReleaseIneligibilityReason.APPROVAL_RESULT_NOT_APPROVED)])
def test_effective_result_state_matrix(effective_state, expected):
    """Description: legal non-approved effective results cannot authorize release.

    Institutional: effective approval state is evaluated independently of bill state.
    """
    requirement = FinancialApprovalRequirementResult("req-a", "actor", 1, 0, False)
    kwargs = {"effective_state": effective_state, "requirement_results": (requirement,)}
    if effective_state is FinancialApprovalEffectiveState.REJECTED:
        kwargs.update(rejection_decision_ids=("decision-a",), rejection_actor_ids=("actor-a",), rejections_counted=1, rejections_required=1)
    result = make_result(**kwargs)
    assert evaluate_vendor_bill_release_eligibility(make_bill(), result, 1, "ZAR", 1, 0).reason is expected


def test_malformed_projection_currency_and_reservation_inputs():
    """Description: malformed numeric, currency, and reservation inputs fail closed.

    Institutional: policy never coerces untrusted orchestration evidence.
    """
    bill, result = make_bill(), make_result()
    for value in (-1, 1.5, True, "1"):
        value_any: Any = value
        with pytest.raises(VendorBillReleasePolicyError):
            evaluate_vendor_bill_release_eligibility(bill, result, 1, "ZAR", value_any, 0)
        with pytest.raises(VendorBillReleasePolicyError):
            evaluate_vendor_bill_release_eligibility(bill, result, 1, "ZAR", 1, value_any)
    for currency in ("usd", "UsD", "US", "USDD", "123", "U$D", "", None):
        currency_any: Any = currency
        with pytest.raises(VendorBillReleasePolicyError):
            evaluate_vendor_bill_release_eligibility(bill, result, 1, currency_any, 1, 0)
    assert evaluate_vendor_bill_release_eligibility(bill, result, 1, "USD", 1, 0).reason is VendorBillReleaseIneligibilityReason.CURRENCY_MISMATCH


def test_cumulative_authority_boundaries_and_public_api_surface():
    """Description: reservation boundaries and public APIs remain execution-free.

    Institutional: cumulative authority cannot exceed outstanding; no payment controls are exposed.
    """
    bill, result = make_bill(), make_result()
    assert evaluate_vendor_bill_release_eligibility(bill, result, 1000, "ZAR", 1, 0).eligible
    assert evaluate_vendor_bill_release_eligibility(bill, result, 400, "ZAR", 1, 500).eligible
    assert evaluate_vendor_bill_release_eligibility(bill, result, 500, "ZAR", 1, 500).eligible
    assert evaluate_vendor_bill_release_eligibility(bill, result, 600, "ZAR", 1, 500).reason is VendorBillReleaseIneligibilityReason.CUMULATIVE_AUTHORITY_EXCEEDED
    for callable_obj in (fingerprint_financial_approval_effective_result, evaluate_vendor_bill_release_eligibility):
        signature = inspect.signature(callable_obj)
        names = set(signature.parameters)
        assert not names.intersection({"bank_account", "payment_destination", "provider_payment_id", "execution_status", "settlement_status", "paid", "payment_mutation", "kennel_command"})


# INSTITUTIONAL CERTIFICATION SEAL
# Runtime posture: PURE / NO DB / NO NETWORK / NO KENNEL EXECUTION
# Technical-control-only; no independent legal-compliance claim.
