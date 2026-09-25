"""Direct certificate for L8-8G human conflict-review determination.

VERSION: v1.0.0-L8-8G-LEGAL-CONFLICT-REVIEW-DETERMINATION-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_conflict_review.py
AUTHORITY BOUNDARY: Pure immutable human conflict-review determination evidence.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import inspect

import pytest

from tools.eos.legal_operations.domain.legal_conflict_review import (
    REVIEW_FIELDS,
    LegalConflictReviewDetermination,
    LegalConflictReviewError,
    LegalConflictReviewOutcome,
    determine_legal_conflict_review,
)
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
)


NOW = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


def screening(
    *,
    status: LegalConflictScreeningStatus = LegalConflictScreeningStatus.REVIEW_REQUIRED,
) -> LegalConflictScreeningResult:
    return LegalConflictScreeningResult(
        tenant_id="tenant-law",
        screening_id="screening-1",
        source_party_id="party-1",
        source_case_matter_id="matter-1",
        source_party_fingerprint=FP_A,
        subject_identity_fingerprint=FP_B,
        screened_at=NOW,
        status=status,
        matches=(),
        source_evidence_reference="screening-source:1",
        source_evidence_fingerprint=FP_C,
    )


def review(
    *,
    source: LegalConflictScreeningResult | None = None,
    outcome: LegalConflictReviewOutcome = LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
    reviewed_at: datetime | None = None,
) -> LegalConflictReviewDetermination:
    return determine_legal_conflict_review(
        screening=source or screening(),
        review_id="review-1",
        reviewer_principal_id="principal-reviewer-1",
        reviewer_authorization_reference="iam-authorization:reviewer-1",
        reviewer_authorization_fingerprint=FP_A,
        outcome=outcome,
        review_reason_reference="review-reason:1",
        reviewed_at=reviewed_at or (NOW + timedelta(minutes=5)),
        source_evidence_reference="review-evidence:1",
        source_evidence_fingerprint=FP_B,
    )


@pytest.mark.parametrize(
    "outcome",
    [
        LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
        LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
        LegalConflictReviewOutcome.ESCALATION_REQUIRED,
    ],
)
def test_review_required_accepts_only_closed_human_outcomes(
    outcome: LegalConflictReviewOutcome,
) -> None:
    value = review(outcome=outcome)
    assert value.outcome is outcome
    assert value.screening_status is LegalConflictScreeningStatus.REVIEW_REQUIRED
    assert len(value.fingerprint) == 128


def test_no_match_found_may_only_be_recorded_as_no_conflict_identified() -> None:
    source = screening(status=LegalConflictScreeningStatus.NO_MATCH_FOUND)
    value = review(
        source=source,
        outcome=LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
    )
    assert value.outcome is LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED

    for incompatible in (
        LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
        LegalConflictReviewOutcome.ESCALATION_REQUIRED,
    ):
        with pytest.raises(LegalConflictReviewError) as raised:
            review(source=source, outcome=incompatible)
        assert raised.value.code == "L8_8G_OUTCOME_INCOMPATIBLE_WITH_SCREENING"


def test_review_is_bound_to_exact_screening_identity_and_fingerprint() -> None:
    source = screening()
    value = review(source=source)
    assert value.tenant_id == source.tenant_id
    assert value.screening_id == source.screening_id
    assert value.screening_fingerprint == source.fingerprint
    assert value.source_party_id == source.source_party_id
    assert value.source_case_matter_id == source.source_case_matter_id
    assert value.subject_identity_fingerprint == source.subject_identity_fingerprint


def test_review_chronology_cannot_precede_screening() -> None:
    with pytest.raises(LegalConflictReviewError) as raised:
        review(reviewed_at=NOW - timedelta(seconds=1))
    assert raised.value.code == "L8_8G_REVIEWED_AT_INVALID"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("reviewer_principal_id", " principal", "L8_8G_REVIEWER_PRINCIPAL_ID_INVALID"),
        (
            "reviewer_authorization_reference",
            "",
            "L8_8G_REVIEWER_AUTHORIZATION_REFERENCE_INVALID",
        ),
        (
            "reviewer_authorization_fingerprint",
            "A" * 128,
            "L8_8G_REVIEWER_AUTHORIZATION_FINGERPRINT_INVALID",
        ),
        (
            "source_evidence_fingerprint",
            "g" * 128,
            "L8_8G_SOURCE_EVIDENCE_FINGERPRINT_INVALID",
        ),
    ],
)
def test_reviewer_and_source_evidence_are_strict(
    field: str,
    value: str,
    code: str,
) -> None:
    kwargs = {
        "screening": screening(),
        "review_id": "review-1",
        "reviewer_principal_id": "principal-reviewer-1",
        "reviewer_authorization_reference": "iam-authorization:reviewer-1",
        "reviewer_authorization_fingerprint": FP_A,
        "outcome": LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
        "review_reason_reference": "review-reason:1",
        "reviewed_at": NOW + timedelta(minutes=1),
        "source_evidence_reference": "review-evidence:1",
        "source_evidence_fingerprint": FP_B,
    }
    kwargs[field] = value
    with pytest.raises(LegalConflictReviewError) as raised:
        determine_legal_conflict_review(**kwargs)
    assert raised.value.code == code


def test_round_trip_integrity_and_tamper_rejection() -> None:
    value = review()
    payload = value.to_dict()
    assert set(payload) == set(REVIEW_FIELDS)
    assert LegalConflictReviewDetermination.from_dict(payload) == value

    tampered = dict(payload)
    tampered["review_reason_reference"] = "different-reason"
    with pytest.raises(LegalConflictReviewError) as raised:
        LegalConflictReviewDetermination.from_dict(tampered)
    assert raised.value.code == "L8_8G_FINGERPRINT_MISMATCH"


def test_value_is_frozen_and_semantic_divergence_changes_fingerprint() -> None:
    value = review()
    with pytest.raises(FrozenInstanceError):
        value.review_reason_reference = "mutated"  # type: ignore[misc]
    divergent = replace(
        value,
        review_reason_reference="review-reason:2",
        fingerprint="",
    )
    assert divergent.fingerprint != value.fingerprint


def test_public_api_excludes_waiver_resolution_and_representation_authority() -> None:
    parameters = set(inspect.signature(determine_legal_conflict_review).parameters)
    assert parameters == {
        "screening",
        "review_id",
        "reviewer_principal_id",
        "reviewer_authorization_reference",
        "reviewer_authorization_fingerprint",
        "outcome",
        "review_reason_reference",
        "reviewed_at",
        "source_evidence_reference",
        "source_evidence_fingerprint",
    }
    forbidden = {
        "waiver",
        "waiver_granted",
        "client_consent",
        "ethical_wall",
        "recusal",
        "accept_client",
        "client_accepted",
        "engagement",
        "authorize_representation",
        "representation_authorized",
        "clearance",
        "clear",
    }
    assert parameters.isdisjoint(forbidden)


def test_schema_contains_no_privileged_review_narrative_or_raw_party_pii() -> None:
    payload = review().to_dict()
    forbidden = {
        "description",
        "comments",
        "notes",
        "analysis",
        "legal_advice",
        "party_name",
        "email",
        "phone",
        "address",
        "id_number",
        "passport_number",
        "tax_number",
    }
    assert forbidden.isdisjoint(payload)


def test_direct_constructor_rejects_pseudo_tenant() -> None:
    value = review()
    with pytest.raises(LegalConflictReviewError) as raised:
        replace(value, tenant_id="GLOBAL_ROOT", fingerprint="")
    assert raised.value.code == "L8_8G_TENANT_REQUIRED"


# ARTIFACT: test_legal_conflict_review.py
# VERSION: v1.0.0-L8-8G-LEGAL-CONFLICT-REVIEW-DETERMINATION-CERT
# AUTHORITY BOUNDARY: pure human review determination semantics only
# TENANT POSTURE: tenant/party/matter/subject derive from exact screening
# FAIL-CLOSED POSTURE: incompatible/stale/malformed/drifted review evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
