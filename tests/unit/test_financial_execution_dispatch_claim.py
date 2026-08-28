"""Unit certification for provider-neutral dispatch claim authority.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM-UNIT-CERT
AUTHORITY: claim and recovery context only; no persistence, CAS, transport, truth, or settlement.
EPITOME: Deterministic immutable authority binding one tenant, command, and PREPARED attempt.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_dispatch_claim.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
CERTIFICATION DATE: 2026-08-28
CHANGELOG: v1.0.0 certifies identity binding, fingerprint validation, state fencing, and confidentiality boundaries.
COMPLIANCE: POPIA | GDPR | SOC2
FINANCIAL AUTHORITY: Kennel EOS owns execution truth; execution is not settlement.
"""
from datetime import datetime, timezone

import pytest

from tools.eos.kennel.domain.financial_execution_dispatch_claim import (
    FinancialExecutionDispatchClaim,
    FinancialExecutionDispatchClaimError,
)
from tools.eos.kennel.domain.financial_execution_lifecycle import FinancialExecutionAttemptState


NOW = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
FINGERPRINT = "a" * 128
TRANSPORT_FINGERPRINT = "b" * 128


def claim(**changes: object) -> FinancialExecutionDispatchClaim:
    values: dict[str, object] = {
        "dispatch_claim_id": "claim-1",
        "tenant_id": "tenant-1",
        "execution_command_id": "command-1",
        "execution_attempt_id": "attempt-1",
        "expected_attempt_fingerprint": FINGERPRINT,
        "provider_name": "PAYSHAP",
        "claimed_at": NOW,
        "transport_correlation_id": "wilsy-correlation-1",
        "transport_material_fingerprint": TRANSPORT_FINGERPRINT,
    }
    values.update(changes)
    return FinancialExecutionDispatchClaim(**values)  # type: ignore[arg-type]


def test_valid_claim_preserves_explicit_authority_lineage() -> None:
    value = claim()
    assert value.dispatch_claim_id == "claim-1"
    assert value.tenant_id == "tenant-1"
    assert value.execution_command_id == "command-1"
    assert value.execution_attempt_id == "attempt-1"
    assert value.expected_attempt_fingerprint == FINGERPRINT
    assert value.provider_name == "PAYSHAP"
    assert value.claimed_at == NOW
    assert value.transport_correlation_id == "wilsy-correlation-1"
    assert value.transport_material_fingerprint == TRANSPORT_FINGERPRINT
    assert value.expected_state is FinancialExecutionAttemptState.PREPARED
    assert value.recovery_posture == "RECONCILE_BEFORE_RESEND"


def test_three_way_identities_do_not_collapse() -> None:
    value = claim()
    assert len({value.dispatch_claim_id, value.execution_command_id, value.execution_attempt_id}) == 3


@pytest.mark.parametrize("field", ["dispatch_claim_id", "tenant_id", "execution_command_id", "execution_attempt_id", "provider_name", "transport_correlation_id", "recovery_posture"])
def test_required_text_is_fail_closed(field: str) -> None:
    with pytest.raises(FinancialExecutionDispatchClaimError):
        claim(**{field: " "})


@pytest.mark.parametrize("field", ["execution_command_id", "execution_attempt_id"])
def test_claim_identity_collision_is_rejected(field: str) -> None:
    with pytest.raises(FinancialExecutionDispatchClaimError):
        claim(dispatch_claim_id="command-1" if field == "execution_command_id" else "attempt-1")


@pytest.mark.parametrize("field", ["expected_attempt_fingerprint", "transport_material_fingerprint"])
@pytest.mark.parametrize("value", ["", "a", "A" * 128, "g" * 128])
def test_fingerprints_require_lowercase_sha3_512_hex(field: str, value: str) -> None:
    with pytest.raises(FinancialExecutionDispatchClaimError):
        claim(**{field: value})


@pytest.mark.parametrize("state", [state for state in FinancialExecutionAttemptState if state is not FinancialExecutionAttemptState.PREPARED])
def test_only_prepared_is_a_valid_claim_source(state: FinancialExecutionAttemptState) -> None:
    with pytest.raises(FinancialExecutionDispatchClaimError):
        claim(expected_state=state)


def test_claimed_at_must_be_timezone_aware() -> None:
    with pytest.raises(FinancialExecutionDispatchClaimError):
        claim(claimed_at=datetime(2026, 8, 28, 12, 0))


def test_claim_is_immutable() -> None:
    value = claim()
    with pytest.raises(AttributeError):
        value.provider_name = "ZAPPER"  # type: ignore[misc]


def test_fingerprint_fields_are_not_provider_evidence() -> None:
    value = claim()
    assert value.expected_attempt_fingerprint != value.transport_material_fingerprint
    assert "provider_request_reference" not in value.__dict__


def test_transport_material_is_secret_free_and_no_settlement_authority() -> None:
    value = claim()
    serialized = value.__dict__
    forbidden = {"bank_account", "card_number", "credentials", "payload", "settled", "settlement_id", "provider_response"}
    assert not forbidden.intersection(serialized)


def test_claim_has_no_execution_or_resend_side_effects() -> None:
    value = claim()
    assert not hasattr(value, "persist")
    assert not hasattr(value, "send")
    assert not hasattr(value, "resend")
    assert not hasattr(value, "cas")


def test_custom_recovery_posture_remains_explicit_and_immutable() -> None:
    value = claim(recovery_posture="RECONCILE_BEFORE_RESEND")
    assert value.recovery_posture == "RECONCILE_BEFORE_RESEND"


# ARTIFACT: test_financial_execution_dispatch_claim.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM-UNIT-CERT
# AUTHORITY BOUNDARY: tests certify claim context only; persistence and transport remain outside scope.
# TENANT POSTURE: tenant, command, and attempt identities remain explicit and bound.
# FAIL-CLOSED POSTURE: malformed fingerprints, collisions, naive time, and non-PREPARED states are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
