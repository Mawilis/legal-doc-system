import json
from datetime import datetime, timezone

import pytest

from tools.eos.saas.domain.financial_approval_effective_result import (
    FinancialApprovalDecisionExclusionReason, FinancialApprovalEffectiveResult,
    FinancialApprovalEffectiveState, FinancialApprovalExcludedDecision,
    FinancialApprovalRequirementResult,
)
from tools.eos.saas.domain.financial_approval_policy_evaluation import FinancialApprovalPolicySubjectType


def result(state=FinancialApprovalEffectiveState.APPROVED):
    req = FinancialApprovalRequirementResult("r", "CFO", 1, 1 if state is FinancialApprovalEffectiveState.APPROVED else 0, state is FinancialApprovalEffectiveState.APPROVED, ("A",) if state is FinancialApprovalEffectiveState.APPROVED else (), ("d",) if state is FinancialApprovalEffectiveState.APPROVED else (), ("a",) if state is FinancialApprovalEffectiveState.APPROVED else ())
    return FinancialApprovalEffectiveResult("t", "result", FinancialApprovalPolicySubjectType.VENDOR_BILL, "p", 2, "e", "P", "1", state, datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, tzinfo=timezone.utc), (req,), req.counted_decision_ids, req.counted_authorization_ids, source_evidence_fingerprint="a" * 128)


def test_lossless_deterministic_round_trip_and_json_bson_safe():
    original = result(); payload = original.to_persistence_dict(); hydrated = FinancialApprovalEffectiveResult.from_persistence_dict(payload)
    assert hydrated == original and payload == original.to_persistence_dict()
    json.dumps(payload)


def test_nested_input_is_not_shared_and_missing_fields_fail():
    payload = result().to_persistence_dict(); payload["requirement_results"][0]["counted_actor_ids"].append("MUTATION")
    assert "MUTATION" not in result().requirement_results[0].counted_actor_ids
    with pytest.raises(ValueError): FinancialApprovalEffectiveResult.from_persistence_dict({})


def test_invalid_persistence_payloads_fail_strictly():
    payload = result().to_persistence_dict()
    for key, value in (("effective_state", "BROKEN"), ("evaluated_at", "bad"), ("source_evidence_fingerprint", "bad")):
        candidate = dict(payload); candidate[key] = value
        with pytest.raises(ValueError): FinancialApprovalEffectiveResult.from_persistence_dict(candidate)
