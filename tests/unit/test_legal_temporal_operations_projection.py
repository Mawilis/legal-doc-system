"""
P4-P0 pure Legal Temporal Operations projection contract certificate.

TITLE:
    WILSY OS Legal Temporal Operations Pure Projection Certificate

AUTHORITY:
    Pure read-model composition only.

ABSOLUTE BOUNDARY:
    - Calendar is projection, never source authority.
    - Legal Productive Work is the v1 matter-visibility ceiling.
    - Legal Matter Deadline is the only v1 temporal source.
    - A deadline from an invisible matter must never create matter visibility.
    - No tenant-wide matter/deadline visibility.
    - No client-visibility reuse.
    - No IAM mutation.
    - No assignment or supervision mutation.
    - No deadline creation or calculation.
    - No browser overdue or legal-period inference.
    - No hearing or court-date fabrication.
    - No financial due-date crossover.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)
from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)
from tools.eos.legal_operations.domain.legal_temporal_operations_projection import (
    LegalTemporalOperationsProjectionError,
    compose_legal_temporal_operations_projection,
)


NOW = datetime(
    2026,
    10,
    18,
    14,
    45,
    tzinfo=timezone.utc,
)


def _productive(
    *matter_ids: str,
) -> LegalProductiveWorkProjection:
    rows = tuple(
        LegalWorkItem(
            work_item_id=f"work-{index}",
            tenant_id="tenant-a",
            case_matter_id=matter_id,
            title=f"Work {index}",
            source_kind="LEGAL_WORKFLOW_STAGE",
            source_reference=f"stage:work-{index}",
            source_evidence_fingerprint=(
                f"{index:0128x}"[-128:]
            ),
            status=LegalWorkItemStatus.OPEN,
            created_at=NOW,
            due_at=None,
        )
        for index, matter_id in enumerate(
            matter_ids,
            start=1,
        )
    )

    return LegalProductiveWorkProjection(
        tenant_id="tenant-a",
        principal_id="principal-a",
        as_of=NOW,
        operating_contexts=(),
        capability_ids=(),
        assigned_work_items=rows,
        supervised_work_items=(),
        overdue_work_items=(),
        due_soon_work_items=(),
    )


def _deadline(
    deadline_id: str,
    matter_id: str,
    *,
    days: int,
) -> LegalMatterDeadline:
    return LegalMatterDeadline(
        tenant_id="tenant-a",
        case_matter_id=matter_id,
        deadline_id=deadline_id,
        deadline_kind="FILING",
        title=f"Deadline {deadline_id}",
        due_at=NOW + timedelta(days=days),
        source_type="COURT_ORDER",
        source_reference=f"evidence:{deadline_id}",
        source_evidence_fingerprint="a" * 128,
        jurisdiction_reference="jurisdiction:za-high-court",
        created_at=NOW,
    )


def test_projection_contains_only_deadlines_from_productive_work_visible_matters():
    productive = _productive(
        "matter-a",
        "matter-b",
    )

    projection = compose_legal_temporal_operations_projection(
        productive_work=productive,
        deadlines=(
            _deadline(
                "deadline-a",
                "matter-a",
                days=2,
            ),
            _deadline(
                "deadline-b",
                "matter-b",
                days=4,
            ),
        ),
    )

    assert projection.tenant_id == "tenant-a"
    assert projection.principal_id == "principal-a"
    assert projection.as_of == NOW

    assert [
        row.case_matter_id
        for row in projection.rows
    ] == [
        "matter-a",
        "matter-b",
    ]

    assert [
        row.deadline_id
        for row in projection.rows
    ] == [
        "deadline-a",
        "deadline-b",
    ]


def test_invisible_matter_deadline_fails_closed():
    productive = _productive(
        "matter-visible",
    )

    with pytest.raises(
        LegalTemporalOperationsProjectionError,
        match="TEMPORAL_DEADLINE_MATTER_NOT_VISIBLE",
    ):
        compose_legal_temporal_operations_projection(
            productive_work=productive,
            deadlines=(
                _deadline(
                    "deadline-secret",
                    "matter-secret",
                    days=1,
                ),
            ),
        )


def test_projection_deduplicates_visible_matter_identity_without_broadening_scope():
    productive = _productive(
        "matter-a",
        "matter-a",
        "matter-b",
    )

    projection = compose_legal_temporal_operations_projection(
        productive_work=productive,
        deadlines=(
            _deadline(
                "deadline-a",
                "matter-a",
                days=1,
            ),
            _deadline(
                "deadline-b",
                "matter-b",
                days=2,
            ),
        ),
    )

    assert projection.visible_matter_ids == (
        "matter-a",
        "matter-b",
    )


def test_rows_are_deterministically_ordered_by_due_at_matter_and_deadline():
    productive = _productive(
        "matter-a",
        "matter-b",
    )

    projection = compose_legal_temporal_operations_projection(
        productive_work=productive,
        deadlines=(
            _deadline(
                "deadline-z",
                "matter-a",
                days=5,
            ),
            _deadline(
                "deadline-b",
                "matter-b",
                days=1,
            ),
            _deadline(
                "deadline-a",
                "matter-a",
                days=1,
            ),
        ),
    )

    assert [
        row.deadline_id
        for row in projection.rows
    ] == [
        "deadline-a",
        "deadline-b",
        "deadline-z",
    ]


def test_projection_preserves_deadline_provenance_exactly():
    productive = _productive(
        "matter-a",
    )

    deadline = _deadline(
        "deadline-a",
        "matter-a",
        days=3,
    )

    projection = compose_legal_temporal_operations_projection(
        productive_work=productive,
        deadlines=(deadline,),
    )

    row = projection.rows[0]

    assert row.case_matter_id == deadline.case_matter_id
    assert row.deadline_id == deadline.deadline_id
    assert row.deadline_kind == deadline.deadline_kind
    assert row.title == deadline.title
    assert row.due_at == deadline.due_at
    assert row.source_type == deadline.source_type
    assert row.source_reference == deadline.source_reference
    assert (
        row.source_evidence_fingerprint
        == deadline.source_evidence_fingerprint
    )
    assert (
        row.jurisdiction_reference
        == deadline.jurisdiction_reference
    )
    assert row.status == deadline.status


def test_cross_tenant_deadline_fails_closed():
    productive = _productive(
        "matter-a",
    )

    foreign = LegalMatterDeadline(
        tenant_id="tenant-b",
        case_matter_id="matter-a",
        deadline_id="deadline-foreign",
        deadline_kind="FILING",
        title="Foreign deadline",
        due_at=NOW + timedelta(days=1),
        source_type="COURT_ORDER",
        source_reference="evidence:foreign",
        source_evidence_fingerprint="b" * 128,
        jurisdiction_reference="jurisdiction:foreign",
        created_at=NOW,
    )

    with pytest.raises(
        LegalTemporalOperationsProjectionError,
        match="TEMPORAL_DEADLINE_TENANT_SCOPE_MISMATCH",
    ):
        compose_legal_temporal_operations_projection(
            productive_work=productive,
            deadlines=(foreign,),
        )


def test_duplicate_deadline_identity_fails_closed():
    productive = _productive(
        "matter-a",
    )

    value = _deadline(
        "deadline-a",
        "matter-a",
        days=1,
    )

    with pytest.raises(
        LegalTemporalOperationsProjectionError,
        match="TEMPORAL_DEADLINE_ID_DUPLICATE",
    ):
        compose_legal_temporal_operations_projection(
            productive_work=productive,
            deadlines=(
                value,
                value,
            ),
        )


def test_projection_is_deeply_immutable():
    productive = _productive(
        "matter-a",
    )

    projection = compose_legal_temporal_operations_projection(
        productive_work=productive,
        deadlines=(
            _deadline(
                "deadline-a",
                "matter-a",
                days=1,
            ),
        ),
    )

    assert isinstance(
        projection.rows,
        tuple,
    )

    assert isinstance(
        projection.visible_matter_ids,
        tuple,
    )

    with pytest.raises(FrozenInstanceError):
        projection.principal_id = "principal-other"  # type: ignore[misc]


def test_projection_exposes_no_command_or_authority_flags():
    productive = _productive(
        "matter-a",
    )

    projection = compose_legal_temporal_operations_projection(
        productive_work=productive,
        deadlines=(
            _deadline(
                "deadline-a",
                "matter-a",
                days=1,
            ),
        ),
    )

    serialized = repr(projection).lower()

    forbidden = (
        "can_file",
        "can_serve",
        "can_execute",
        "can_transition",
        "payment_authority",
        "settlement_authority",
        "hearing_authority",
        "court_authority",
        "ai_generated",
    )

    for token in forbidden:
        assert token not in serialized


def test_empty_visible_work_yields_empty_temporal_projection():
    productive = _productive()

    projection = compose_legal_temporal_operations_projection(
        productive_work=productive,
        deadlines=(),
    )

    assert projection.visible_matter_ids == ()
    assert projection.rows == ()


# AUTHORITY BOUNDARY:
# Pure temporal projection only.
# No IAM, assignment, supervision, deadline creation,
# legal-period calculation, court/hearing, AI,
# payment, billing, settlement or financial authority.
