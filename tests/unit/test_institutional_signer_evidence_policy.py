from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.security.institutional_signer_evidence_policy import (
    InstitutionalSignerEvidencePolicyError,
    InstitutionalSignerEvidencePolicyParameters,
)


NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)


def policy(**overrides):
    values = {
        "policy_reference": "governance-policy://institutional-signer/v1",
        "policy_revision": "revision-1",
        "effective_at": datetime(2026, 11, 1, tzinfo=timezone.utc),
        "expires_at": datetime(2027, 1, 1, tzinfo=timezone.utc),
        "maximum_evidence_age_by_kind": {
            "IDENTITY_PROOFING": timedelta(hours=1),
            "SIGNATORY_MANDATE": timedelta(hours=2),
            "INDEPENDENT_APPROVAL": timedelta(minutes=30),
        },
        "currentness_lease_duration": timedelta(minutes=15),
        "reconciliation_cadence": timedelta(minutes=5),
        "clock_skew_tolerance": timedelta(seconds=30),
    }
    values.update(overrides)
    return InstitutionalSignerEvidencePolicyParameters(**values)


def test_policy_requires_explicit_per_kind_age_and_immutable_parameters():
    configured = policy()
    assert set(configured.maximum_evidence_age_by_kind) == {
        "IDENTITY_PROOFING", "SIGNATORY_MANDATE", "INDEPENDENT_APPROVAL"
    }
    with pytest.raises(TypeError):
        configured.maximum_evidence_age_by_kind["IDENTITY_PROOFING"] = timedelta(days=1)


@pytest.mark.parametrize("ages", [
    {},
    {"IDENTITY_PROOFING": timedelta(hours=1)},
    {
        "IDENTITY_PROOFING": timedelta(hours=1),
        "SIGNATORY_MANDATE": timedelta(hours=2),
        "INDEPENDENT_APPROVAL": timedelta(0),
    },
])
def test_policy_rejects_missing_or_nonpositive_evidence_age(ages):
    with pytest.raises(InstitutionalSignerEvidencePolicyError):
        policy(maximum_evidence_age_by_kind=ages)


def test_policy_rejects_missing_or_nonpositive_lease_and_cadence():
    for field in ("currentness_lease_duration", "reconciliation_cadence"):
        with pytest.raises(InstitutionalSignerEvidencePolicyError):
            policy(**{field: timedelta(0)})


def test_policy_rejects_invalid_effective_interval_and_naive_timestamps():
    with pytest.raises(InstitutionalSignerEvidencePolicyError):
        policy(expires_at=datetime(2026, 11, 1, tzinfo=timezone.utc))
    with pytest.raises(InstitutionalSignerEvidencePolicyError):
        policy(effective_at=datetime(2026, 11, 1))


def test_policy_rejects_use_before_effective_or_after_expiry():
    configured = policy()
    for instant in (
        datetime(2026, 10, 31, tzinfo=timezone.utc),
        datetime(2027, 1, 1, tzinfo=timezone.utc),
    ):
        with pytest.raises(InstitutionalSignerEvidencePolicyError) as error:
            configured.assert_effective(evaluated_at=instant)
        assert error.value.code == "INSTITUTIONAL_SIGNER_POLICY_NOT_EFFECTIVE"


def test_policy_applies_distinct_evidence_age_and_clock_skew_rules():
    configured = policy()
    configured.assert_evidence_fresh(
        evidence_kind="IDENTITY_PROOFING",
        observed_at=NOW - timedelta(minutes=59),
        evaluated_at=NOW,
    )
    with pytest.raises(InstitutionalSignerEvidencePolicyError) as error:
        configured.assert_evidence_fresh(
            evidence_kind="INDEPENDENT_APPROVAL",
            observed_at=NOW - timedelta(minutes=31),
            evaluated_at=NOW,
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_POLICY_EVIDENCE_TOO_OLD"
    with pytest.raises(InstitutionalSignerEvidencePolicyError) as error:
        configured.assert_evidence_fresh(
            evidence_kind="IDENTITY_PROOFING",
            observed_at=NOW + timedelta(minutes=1),
            evaluated_at=NOW,
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_POLICY_OBSERVATION_FROM_FUTURE"


def test_policy_computes_bounded_lease_and_reconciliation_due_time():
    configured = policy()
    assert configured.currentness_lease_until(checked_at=NOW) == NOW + timedelta(minutes=15)
    assert configured.next_reconciliation_at(checked_at=NOW) == NOW + timedelta(minutes=5)


def test_policy_lease_and_reconciliation_are_capped_at_policy_expiry():
    configured = policy(
        expires_at=NOW + timedelta(minutes=3),
        currentness_lease_duration=timedelta(minutes=15),
        reconciliation_cadence=timedelta(minutes=5),
    )
    assert configured.currentness_lease_until(checked_at=NOW) == NOW + timedelta(minutes=3)
    assert configured.next_reconciliation_at(checked_at=NOW) == NOW + timedelta(minutes=3)
