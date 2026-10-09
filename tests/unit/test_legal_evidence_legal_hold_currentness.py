"""Direct certificate for pure Legal Evidence legal-hold currentness.

TITLE: Legal Evidence Legal Hold Currentness Direct Certificate
VERSION: v1.0.0-L10A2R-C4D4B-CURRENTNESS-R3-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Certify pure explicit-time legal-hold currentness derivation,
         exact lineage release semantics, ambiguity/corruption precedence,
         duplicate normalization, deterministic evidence and absence of
         deletion or provider authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_legal_hold_currentness.py
COLLABORATION / OWNERSHIP:
    Test-only certificate for frozen C4D4B currentness production domain.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0 certifies the frozen pure currentness semantic matrix.
COMPLIANCE:
    Pure in-process direct certificate; no persistence or runtime IO.
SECURITY / PRIVACY POSTURE:
    Synthetic opaque evidence only.
TENANT BOUNDARY:
    Exact tenant/provider-object correlation; cross-scope evidence blocks.
AUTHORITY BOUNDARY:
    Currentness projection only; no hold issuance/release, retention
    satisfaction, orphan proof, deletion authorization or provider mutation.
FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TypedDict

import pytest

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
    LegalEvidenceLegalHoldState,
)
from tools.eos.legal_operations.domain.legal_evidence_legal_hold_currentness import (
    LegalEvidenceLegalHoldCurrentness,
    LegalEvidenceLegalHoldCurrentnessError,
    LegalEvidenceLegalHoldCurrentnessReason,
    LegalEvidenceLegalHoldCurrentnessState,
    evaluate_legal_evidence_legal_hold_currentness,
    project_legal_evidence_legal_hold_currentness,
)


BASE = datetime(
    2026,
    10,
    1,
    12,
    0,
    tzinfo=timezone.utc,
)

class _Scope(TypedDict):
    """Exact keyword scope shared by currentness test helpers."""

    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str


SCOPE: _Scope = {
    "tenant_id": "tenant-currentness-cert",
    "provider_name": "s3",
    "storage_reference": "bucket-currentness-cert",
    "object_version_reference": "object-v1",
}


def _fact(
    *,
    hold: str = "hold-a",
    source: str = "source-a",
    source_fp: str = "a" * 128,
    imposed_at: datetime = BASE,
    state: LegalEvidenceLegalHoldState = (
        LegalEvidenceLegalHoldState.ACTIVE
    ),
    released_at: datetime | None = None,
) -> LegalEvidenceLegalHoldConstraint:
    return LegalEvidenceLegalHoldConstraint(
        **SCOPE,
        hold_reference=hold,
        source_evidence_reference=source,
        source_evidence_fingerprint=source_fp,
        imposed_at=imposed_at,
        state=state,
        released_at=released_at,
    )


def _project(
    *,
    evaluated_at: datetime,
    history: tuple[
        LegalEvidenceLegalHoldConstraint,
        ...,
    ],
) -> LegalEvidenceLegalHoldCurrentness:
    return project_legal_evidence_legal_hold_currentness(
        **SCOPE,
        evaluated_at=evaluated_at,
        history=history,
    )


def test_empty_history_is_no_hold_evidence_not_delete_authority() -> None:
    result = _project(
        evaluated_at=BASE,
        history=(),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.NO_HOLD_EVIDENCE
    )
    assert result.reason is (
        LegalEvidenceLegalHoldCurrentnessReason.NO_HOLD_EVIDENCE
    )
    assert result.preservation_blocking is False
    assert result.deletion_authorized is False
    assert result.provider_delete_authorized is False


def test_active_hold_blocks_at_imposition_boundary() -> None:
    active = _fact()

    result = _project(
        evaluated_at=BASE,
        history=(active,),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.HOLD_BLOCKING
    )
    assert result.reason is (
        LegalEvidenceLegalHoldCurrentnessReason.ACTIVE_HOLD
    )
    assert result.blocking_hold_fingerprints == (
        active.fingerprint,
    )


def test_exact_lineage_release_blocks_before_release_boundary() -> None:
    active = _fact()
    released = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=5),
    )

    result = _project(
        evaluated_at=BASE + timedelta(days=4),
        history=(
            active,
            released,
        ),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.HOLD_BLOCKING
    )
    assert result.reason is (
        LegalEvidenceLegalHoldCurrentnessReason.RELEASED_HOLD_BEFORE_RELEASE
    )
    assert result.applicable_hold_references == (
        "hold-a",
        "hold-a",
    )


def test_exact_lineage_release_stops_blocking_at_release_boundary() -> None:
    active = _fact()
    released = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=5),
    )

    result = _project(
        evaluated_at=BASE + timedelta(days=5),
        history=(
            active,
            released,
        ),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.NO_HOLD_BLOCK_DEMONSTRATED
    )
    assert result.reason is (
        LegalEvidenceLegalHoldCurrentnessReason.ALL_APPLICABLE_HOLDS_RELEASED
    )
    assert result.deletion_authorized is False
    assert result.provider_delete_authorized is False


def test_multiple_release_times_same_lineage_are_ambiguous_blocked() -> None:
    active = _fact()
    release_one = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=5),
    )
    release_two = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=6),
    )

    result = _project(
        evaluated_at=BASE + timedelta(days=7),
        history=(
            active,
            release_one,
            release_two,
        ),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.AMBIGUOUS_BLOCKED
    )
    assert result.reason is (
        LegalEvidenceLegalHoldCurrentnessReason.AMBIGUOUS_RELEASE_EVIDENCE
    )
    assert result.preservation_blocking is True


def test_future_fact_is_excluded() -> None:
    future = _fact(
        imposed_at=BASE + timedelta(days=2),
    )

    result = _project(
        evaluated_at=BASE,
        history=(future,),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.NO_HOLD_EVIDENCE
    )


def test_independent_active_hold_blocks_after_other_hold_released() -> None:
    active_a = _fact()

    released_a = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=2),
    )

    active_b = _fact(
        hold="hold-b",
        source="source-b",
        source_fp="b" * 128,
        imposed_at=BASE + timedelta(days=1),
    )

    result = _project(
        evaluated_at=BASE + timedelta(days=3),
        history=(
            active_a,
            released_a,
            active_b,
        ),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.HOLD_BLOCKING
    )
    assert "hold-b" in result.blocking_hold_references


def test_source_lineage_drift_cannot_release_active_hold() -> None:
    active = _fact()

    foreign_release = _fact(
        source="source-other",
        source_fp="c" * 128,
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=2),
    )

    result = _project(
        evaluated_at=BASE + timedelta(days=3),
        history=(
            active,
            foreign_release,
        ),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.HOLD_BLOCKING
    )
    assert active.fingerprint in (
        result.blocking_hold_fingerprints
    )


def test_imposition_drift_cannot_release_active_hold() -> None:
    active = _fact()

    foreign_release = _fact(
        imposed_at=BASE + timedelta(hours=1),
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=2),
    )

    result = _project(
        evaluated_at=BASE + timedelta(days=3),
        history=(
            active,
            foreign_release,
        ),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.HOLD_BLOCKING
    )
    assert active.fingerprint in (
        result.blocking_hold_fingerprints
    )


def test_exact_duplicate_fact_normalizes_by_fingerprint() -> None:
    active = _fact()

    result = _project(
        evaluated_at=BASE,
        history=(
            active,
            active,
        ),
    )

    assert result.applicable_hold_references == (
        "hold-a",
    )

    assert result.applicable_hold_fingerprints == (
        active.fingerprint,
    )


def test_cross_scope_history_is_corrupt_blocked() -> None:
    valid = _fact()

    foreign = LegalEvidenceLegalHoldConstraint(
        tenant_id="tenant-foreign",
        provider_name=SCOPE["provider_name"],
        storage_reference=SCOPE["storage_reference"],
        object_version_reference=SCOPE[
            "object_version_reference"
        ],
        hold_reference="hold-foreign",
        source_evidence_reference="source-foreign",
        source_evidence_fingerprint="d" * 128,
        imposed_at=BASE,
        state=LegalEvidenceLegalHoldState.ACTIVE,
    )

    result = _project(
        evaluated_at=BASE,
        history=(
            valid,
            foreign,
        ),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.CORRUPT_BLOCKED
    )
    assert result.reason is (
        LegalEvidenceLegalHoldCurrentnessReason.CORRUPT_EVIDENCE
    )
    assert result.preservation_blocking is True


def test_post_construction_tampering_is_corrupt_blocked() -> None:
    active = _fact()

    object.__setattr__(
        active,
        "provider_delete_authorized",
        True,
    )

    result = _project(
        evaluated_at=BASE,
        history=(active,),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.CORRUPT_BLOCKED
    )


def test_corruption_outranks_otherwise_valid_blocking_evidence() -> None:
    valid = _fact()

    foreign = LegalEvidenceLegalHoldConstraint(
        tenant_id="tenant-foreign",
        provider_name=SCOPE["provider_name"],
        storage_reference=SCOPE["storage_reference"],
        object_version_reference=SCOPE[
            "object_version_reference"
        ],
        hold_reference="hold-foreign",
        source_evidence_reference="source-foreign",
        source_evidence_fingerprint="e" * 128,
        imposed_at=BASE,
        state=LegalEvidenceLegalHoldState.ACTIVE,
    )

    result = _project(
        evaluated_at=BASE,
        history=(
            valid,
            foreign,
        ),
    )

    assert result.state is (
        LegalEvidenceLegalHoldCurrentnessState.CORRUPT_BLOCKED
    )


def test_projection_is_input_order_independent() -> None:
    active = _fact()

    released = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=5),
    )

    left = _project(
        evaluated_at=BASE + timedelta(days=4),
        history=(
            active,
            released,
        ),
    )

    right = _project(
        evaluated_at=BASE + timedelta(days=4),
        history=(
            released,
            active,
        ),
    )

    assert left == right
    assert left.fingerprint == right.fingerprint


def test_alias_matches_primary_projection() -> None:
    active = _fact()

    primary = _project(
        evaluated_at=BASE,
        history=(active,),
    )

    alias = evaluate_legal_evidence_legal_hold_currentness(
        **SCOPE,
        evaluated_at=BASE,
        history=(active,),
    )

    assert alias == primary


def test_serialization_round_trip_and_tampering_reject() -> None:
    active = _fact()

    result = _project(
        evaluated_at=BASE,
        history=(active,),
    )

    payload = result.to_dict()

    assert (
        LegalEvidenceLegalHoldCurrentness.from_dict(
            payload
        )
        == result
    )

    corrupt = dict(
        payload
    )

    corrupt[
        "tenant_id"
    ] = "tenant-other"

    with pytest.raises(
        LegalEvidenceLegalHoldCurrentnessError
    ):
        LegalEvidenceLegalHoldCurrentness.from_dict(
            corrupt
        )


def test_projection_rejects_naive_evaluation_time() -> None:
    with pytest.raises(
        LegalEvidenceLegalHoldCurrentnessError
    ):
        project_legal_evidence_legal_hold_currentness(
            **SCOPE,
            evaluated_at=datetime(
                2026,
                10,
                1,
                12,
                0,
            ),
            history=(),
        )


def test_currentness_public_authority_surface_is_bounded() -> None:
    public = {
        name
        for name in dir(
            LegalEvidenceLegalHoldCurrentness
        )
        if not name.startswith("_")
    }

    assert "preservation_blocking" in public
    assert "deletion_authorized" in public
    assert "provider_delete_authorized" in public

    instance = _project(
        evaluated_at=BASE,
        history=(),
    )

    assert instance.deletion_authorized is False
    assert instance.provider_delete_authorized is False

    for forbidden in (
        "issue_hold",
        "release_hold",
        "satisfy_retention",
        "prove_orphan",
        "authorize_delete",
        "delete_provider_object",
        "settle",
        "execute_payment",
    ):
        assert forbidden not in public


# ARTIFACT: test_legal_evidence_legal_hold_currentness.py
# VERSION: v1.0.0-L10A2R-C4D4B-CURRENTNESS-R3-CERT
# AUTHORITY BOUNDARY: direct certificate for pure legal-hold currentness only
# TENANT POSTURE: cross-scope evidence fails closed
# LINEAGE POSTURE: release applies only to exact immutable lineage
# AMBIGUITY POSTURE: multiple distinct release times block
# CORRUPTION POSTURE: corruption outranks normal currentness
# TIME POSTURE: explicit aware evaluation instant only
# PERSISTENCE POSTURE: none
# DELETION POSTURE: no deletion/provider authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
