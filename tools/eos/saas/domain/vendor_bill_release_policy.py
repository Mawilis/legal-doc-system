"""WILSY OS — VENDOR BILL RELEASE POLICY
Version: v1.0.1-VENDOR-BILL-RELEASE-POLICY
Authority: Wilsy OS Core Governance | Classification: Institutional Artifact — Production Only
EPITOME: Pure fail-closed eligibility rules for release authorization.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/vendor_bill_release_policy.py
COLLABORATION: Wilson Khanyezi — Founder / Chief Architect; AI Engineering (Codex)
Date: 2026-08-26 | COMPLIANCE: POPIA §19 | GDPR §32 | SOC2 CC7.2
APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
Kennel EOS remains the exclusive financial execution authority.
CHANGELOG:
- 2026-08-26 — v1.0.1 corrected obligation-state access; added tenant,
  approval-policy, and requested-currency bindings; hardened trusted-input validation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from .financial_approval_effective_result import (
    FinancialApprovalEffectiveResult,
    FinancialApprovalEffectiveState,
)
from .financial_approval_policy_evaluation import FinancialApprovalPolicySubjectType
from .vendor_bill import VendorBill, VendorBillApprovalState, VendorBillObligationState

VERSION = "v1.0.1-VENDOR-BILL-RELEASE-POLICY"


class VendorBillReleasePolicyError(ValueError):
    """Description: invalid trusted policy input.

    Collaboration: raised for malformed orchestration evidence.
    Institutional: policy evaluation remains pure and fail closed.
    """


class VendorBillReleaseIneligibilityReason(StrEnum):
    """Description: stable reasons a release request is not eligible.

    Collaboration: consumed by future orchestration and user-facing controls.
    Institutional: explicit reasons prevent unsafe implicit authorization.
    """

    ELIGIBLE = "ELIGIBLE"
    INVALID_OBLIGATION_STATE = "INVALID_OBLIGATION_STATE"
    APPROVAL_NOT_APPROVED = "APPROVAL_NOT_APPROVED"
    CURRENT_APPROVAL_RESULT_MISSING = "CURRENT_APPROVAL_RESULT_MISSING"
    CURRENT_APPROVAL_RESULT_MISMATCH = "CURRENT_APPROVAL_RESULT_MISMATCH"
    APPROVAL_TENANT_MISMATCH = "APPROVAL_TENANT_MISMATCH"
    APPROVAL_SUBJECT_MISMATCH = "APPROVAL_SUBJECT_MISMATCH"
    APPROVAL_REVISION_MISMATCH = "APPROVAL_REVISION_MISMATCH"
    APPROVAL_POLICY_MISMATCH = "APPROVAL_POLICY_MISMATCH"
    APPROVAL_RESULT_NOT_APPROVED = "APPROVAL_RESULT_NOT_APPROVED"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
    INVALID_RELEASE_AMOUNT = "INVALID_RELEASE_AMOUNT"
    RESERVATION_REQUIRED = "RESERVATION_REQUIRED"
    CUMULATIVE_AUTHORITY_EXCEEDED = "CUMULATIVE_AUTHORITY_EXCEEDED"
    STALE_APPROVAL_PROJECTION = "STALE_APPROVAL_PROJECTION"


@dataclass(frozen=True)
class VendorBillReleaseEligibilityDecision:
    """Description: immutable result of pure release-policy evaluation.

    Collaboration: future orchestration uses this decision before persistence.
    Institutional: eligible means policy conditions pass, not execution or settlement.
    """

    eligible: bool
    reason: VendorBillReleaseIneligibilityReason


def fingerprint_financial_approval_effective_result(result: FinancialApprovalEffectiveResult) -> str:
    """Description: fingerprint complete effective-result persistence evidence.

    Collaboration: binds release authorization to immutable approval evidence.
    Institutional: this is distinct from ``source_evidence_fingerprint`` and performs no I/O.
    Args: result, a hydrated effective approval result.
    Returns: lowercase SHA3-512 hexadecimal digest.
    Raises: VendorBillReleasePolicyError when result has the wrong type.
    """
    if not isinstance(result, FinancialApprovalEffectiveResult):
        raise VendorBillReleasePolicyError("result must be a FinancialApprovalEffectiveResult")
    canonical = json.dumps(result.to_persistence_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


def evaluate_vendor_bill_release_eligibility(
    bill: VendorBill,
    result: Optional[FinancialApprovalEffectiveResult],
    requested_amount_minor: int,
    requested_currency: str,
    expected_approval_projection_revision: int,
    existing_active_reserved_amount_minor: Optional[int] = None,
) -> VendorBillReleaseEligibilityDecision:
    """Description: evaluate frozen release rules from hydrated inputs only.

    Collaboration: future orchestration supplies current bill/result snapshots.
    Institutional: OPEN plus APPROVED is required; reservation proof is mandatory
    for cumulative authority and no execution or settlement is performed.
    Args: bill, result, amount, expected projection revision, trusted reservation total.
    Returns: immutable eligibility decision.
    Raises: VendorBillReleasePolicyError for malformed numeric inputs.
    """
    if not isinstance(requested_amount_minor, int) or isinstance(requested_amount_minor, bool) or requested_amount_minor <= 0:
        raise VendorBillReleasePolicyError("requested_amount_minor is invalid")
    if not isinstance(requested_currency, str) or len(requested_currency) != 3 or not requested_currency.isascii() or not requested_currency.isupper() or not requested_currency.isalpha():
        raise VendorBillReleasePolicyError("requested_currency is invalid")
    if not isinstance(expected_approval_projection_revision, int) or isinstance(expected_approval_projection_revision, bool) or expected_approval_projection_revision < 0:
        raise VendorBillReleasePolicyError("expected_approval_projection_revision is invalid")
    if not isinstance(bill, VendorBill):
        raise VendorBillReleasePolicyError("bill must be a VendorBill")
    if result is not None and not isinstance(result, FinancialApprovalEffectiveResult):
        raise VendorBillReleasePolicyError("result must be a FinancialApprovalEffectiveResult")
    if bill.obligation_state is not VendorBillObligationState.OPEN:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.INVALID_OBLIGATION_STATE)
    if bill.approval_state is not VendorBillApprovalState.APPROVED:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.APPROVAL_NOT_APPROVED)
    if result is None:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.CURRENT_APPROVAL_RESULT_MISSING)
    if result.tenant_id != bill.tenant_id:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.APPROVAL_TENANT_MISMATCH)
    if bill.approval_effective_result_id != result.result_id:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.CURRENT_APPROVAL_RESULT_MISMATCH)
    if result.subject_type is not FinancialApprovalPolicySubjectType.VENDOR_BILL or result.subject_id != bill.payable_id:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.APPROVAL_SUBJECT_MISMATCH)
    if result.subject_revision != bill.revision:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.APPROVAL_REVISION_MISMATCH)
    if result.approval_policy_reference != bill.approval_policy_reference:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.APPROVAL_POLICY_MISMATCH)
    if result.effective_state is not FinancialApprovalEffectiveState.APPROVED:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.APPROVAL_RESULT_NOT_APPROVED)
    if bill.approval_projection_revision != expected_approval_projection_revision:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.STALE_APPROVAL_PROJECTION)
    if requested_currency != bill.currency:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.CURRENCY_MISMATCH)
    outstanding = bill.outstanding_amount_minor
    if not isinstance(outstanding, int) or isinstance(outstanding, bool) or outstanding < 0:
        raise VendorBillReleasePolicyError("bill outstanding amount is invalid")
    if requested_amount_minor > outstanding:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.INVALID_RELEASE_AMOUNT)
    if existing_active_reserved_amount_minor is None:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.RESERVATION_REQUIRED)
    if not isinstance(existing_active_reserved_amount_minor, int) or isinstance(existing_active_reserved_amount_minor, bool) or existing_active_reserved_amount_minor < 0:
        raise VendorBillReleasePolicyError("existing_active_reserved_amount_minor is invalid")
    if existing_active_reserved_amount_minor + requested_amount_minor > outstanding:
        return VendorBillReleaseEligibilityDecision(False, VendorBillReleaseIneligibilityReason.CUMULATIVE_AUTHORITY_EXCEEDED)
    return VendorBillReleaseEligibilityDecision(True, VendorBillReleaseIneligibilityReason.ELIGIBLE)


# INSTITUTIONAL CERTIFICATION SEAL
# Pure technical policy contract only; no independent legal-compliance claim.
# No I/O, persistence, execution, settlement, or Kennel invocation.
