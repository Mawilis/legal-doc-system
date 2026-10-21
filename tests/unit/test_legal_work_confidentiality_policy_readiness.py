"""TITLE: G63 confidentiality policy readiness tests.
VERSION: v1.0.0-P47-R95-G63
CHANGELOG: Fail-closed unresolved governance diagnostic certificate.
AUTHORITY: No approval or operational access.
"""
from dataclasses import FrozenInstanceError
import dataclasses
import pytest

from tools.eos.legal_operations.domain.legal_work_confidentiality_policy_readiness import (
    UNRESOLVED_DECISIONS,
    evaluate_policy_readiness,
    PolicyReadinessState,
)

def test_all_ten_decisions_unresolved():
    result = evaluate_policy_readiness()
    assert len(result.unresolved_decisions) == 10
    assert result.unresolved_decisions == UNRESOLVED_DECISIONS
    assert result.state is PolicyReadinessState.INSTITUTIONAL_APPROVAL_MISSING

def test_no_operational_authority():
    result = evaluate_policy_readiness()
    assert result.permits_operational_access is False
    assert result.permits_reviewer_authorization is False
    assert result.permits_wall_enforcement_claim is False

def test_no_caller_override_surface():
    with pytest.raises(TypeError):
        evaluate_policy_readiness(**{"approved": True})
    with pytest.raises(TypeError):
        evaluate_policy_readiness(**{"reviewer_authorized": True})
    with pytest.raises(TypeError):
        evaluate_policy_readiness(**{"wall_enforced": True})

def test_result_is_immutable():
    result = evaluate_policy_readiness()
    with pytest.raises(FrozenInstanceError):
        setattr(result, "state", PolicyReadinessState.INSTITUTIONAL_APPROVAL_MISSING)

def test_unique_decision_ids():
    ids = [item[0] for item in UNRESOLVED_DECISIONS]
    assert ids == [f"D{i:02d}" for i in range(1, 11)]
    assert len(ids) == len(set(ids))

def test_deterministic_projection():
    assert evaluate_policy_readiness() == evaluate_policy_readiness()

def test_no_positive_permission_even_after_copy():
    result = dataclasses.replace(evaluate_policy_readiness())
    assert result.permits_operational_access is False
    assert result.permits_reviewer_authorization is False
    assert result.permits_wall_enforcement_claim is False

# END OF WILSY OS SOVEREIGN ARTIFACT
