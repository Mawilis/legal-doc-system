"""G63 independent tests for the pure fail-closed institutional policy boundary."""
from dataclasses import FrozenInstanceError, fields
from itertools import product

import pytest

from tools.eos.legal_operations.service.legal_practitioner_institutional_policy_evaluation import (
    OPERATIONAL_ADMISSION_ENABLED,
    InstitutionalEvidenceState as State,
    InstitutionalPolicyDecision as Decision,
    InstitutionalPolicyInputs,
    evaluate_institutional_policy_boundary,
)


INPUT_FIELDS = tuple(field.name for field in fields(InstitutionalPolicyInputs))


def test_default_inputs_deny_every_unassigned_dependency() -> None:
    result = evaluate_institutional_policy_boundary(InstitutionalPolicyInputs())

    assert result.decision is Decision.DENY
    assert result.operational_admission is False
    assert OPERATIONAL_ADMISSION_ENABLED is False
    assert result.reason_codes == tuple(
        f"G63_{name.upper()}_UNASSIGNED" for name in INPUT_FIELDS
    )


def test_even_all_approved_labels_cannot_enable_operational_admission() -> None:
    inputs = InstitutionalPolicyInputs(
        **{name: State.APPROVED for name in INPUT_FIELDS}
    )

    result = evaluate_institutional_policy_boundary(inputs)

    assert result.decision is Decision.DENY
    assert result.operational_admission is False
    assert result.reason_codes == ("G63_OPERATIONAL_ADMISSION_DISABLED",)
    assert "ALLOW" not in Decision.__members__


@pytest.mark.parametrize("state", list(State))
def test_every_single_dependency_state_remains_fail_closed(state: State) -> None:
    inputs = InstitutionalPolicyInputs(wall_enforcement=state)

    result = evaluate_institutional_policy_boundary(inputs)

    assert result.decision is Decision.DENY
    assert result.operational_admission is False
    if state is State.APPROVED:
        assert "G63_OPERATIONAL_ADMISSION_DISABLED" in result.reason_codes
    else:
        assert f"G63_WALL_ENFORCEMENT_{state.value}" in result.reason_codes


def test_explicit_negative_evidence_has_stable_precedence() -> None:
    inputs = InstitutionalPolicyInputs(
        reviewer_authority=State.DENIED,
        wall_policy_authority=State.UNASSIGNED,
        wall_enforcement=State.REVOKED,
        emergency_denial_authority=State.APPROVED,
    )

    result = evaluate_institutional_policy_boundary(inputs)

    assert result.decision is Decision.DENY
    assert result.reason_codes[0] == "G63_EXPLICIT_NEGATIVE_PRECEDENCE"
    assert result.reason_codes[1:4] == (
        "G63_REVIEWER_AUTHORITY_DENIED",
        "G63_WALL_POLICY_AUTHORITY_UNASSIGNED",
        "G63_WALL_ENFORCEMENT_REVOKED",
    )


def test_evaluation_is_deterministic_for_identical_inputs() -> None:
    inputs = InstitutionalPolicyInputs(
        reviewer_authority=State.APPROVED,
        wall_policy_authority=State.UNVERIFIED,
        wall_enforcement=State.INEFFECTIVE,
        institutional_ratification=State.STALE,
    )

    assert evaluate_institutional_policy_boundary(inputs) == (
        evaluate_institutional_policy_boundary(inputs)
    )


@pytest.mark.parametrize("name", INPUT_FIELDS)
def test_inputs_reject_bare_strings_and_booleans(name: str) -> None:
    with pytest.raises(ValueError, match="G63_INSTITUTIONAL_EVIDENCE_STATE_INVALID"):
        InstitutionalPolicyInputs(**{name: "APPROVED"})


def test_wrong_container_type_rejects_without_evaluation() -> None:
    with pytest.raises(ValueError, match="G63_INSTITUTIONAL_POLICY_INPUTS_INVALID"):
        evaluate_institutional_policy_boundary(object())  # type: ignore[arg-type]


def test_input_and_result_are_immutable_and_non_authorizing() -> None:
    inputs = InstitutionalPolicyInputs()
    result = evaluate_institutional_policy_boundary(inputs)

    with pytest.raises(FrozenInstanceError):
        inputs.reviewer_authority = State.APPROVED  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.operational_admission = True  # type: ignore[misc]

    assert not any(hasattr(result, name) for name in ("grant", "authorize", "read", "write"))
