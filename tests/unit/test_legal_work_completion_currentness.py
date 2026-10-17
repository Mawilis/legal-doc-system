"""
WILSY OS — P14-R16 Legal Work Completion Currentness Unit Certificate.

Pure projection only. No persistence, command authority, dependency
satisfaction, assignment, supervision, IAM, legal-event or financial authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_work_completion_currentness import (
    SCHEMA,
    VERSION,
    LegalWorkCompletionCurrentness,
    LegalWorkCompletionCurrentnessError,
    LegalWorkCompletionCurrentnessReason,
    LegalWorkCompletionCurrentnessState,
    project_legal_work_completion_currentness,
)
from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)


CREATED = datetime(
    2026,
    10,
    16,
    18,
    0,
    tzinfo=timezone.utc,
)

COMPLETED = CREATED + timedelta(
    hours=1
)

EVALUATED = CREATED + timedelta(
    hours=2
)


def work(
    **overrides: object,
) -> LegalWorkItem:
    values: dict[str, object] = {
        "work_item_id": "work-1",
        "tenant_id": "tenant-law",
        "case_matter_id": "matter-1",
        "title": "Review source",
        "source_kind": "WORKFLOW_TRANSITION",
        "source_reference": "transition-1",
        "source_evidence_fingerprint":
            "a" * 128,
        "status":
            LegalWorkItemStatus.OPEN,
        "created_at":
            CREATED,
        "due_at":
            None,
        "completion_evidence_reference":
            None,
        "completion_evidence_fingerprint":
            None,
        "completed_at":
            None,
        "cancellation_reason_reference":
            None,
        "cancelled_at":
            None,
    }

    values.update(
        overrides
    )

    return LegalWorkItem(
        **values  # type: ignore[arg-type]
    )


def completion(
    exact_work: LegalWorkItem,
    **overrides: object,
) -> LegalWorkCompletionEvent:
    values: dict[str, object] = {
        "tenant_id":
            exact_work.tenant_id,
        "case_matter_id":
            exact_work.case_matter_id,
        "work_item_id":
            exact_work.work_item_id,
        "work_item_fingerprint":
            exact_work.fingerprint,
        "completion_evidence_reference":
            "completion:evidence:1",
        "completion_evidence_fingerprint":
            "b" * 128,
        "completed_at":
            COMPLETED,
        "actor_principal_id":
            "principal-attorney-1",
        "authorization_evidence_reference":
            "iam:decision:complete:1",
        "authorization_evidence_fingerprint":
            "c" * 128,
    }

    values.update(
        overrides
    )

    return LegalWorkCompletionEvent(
        **values  # type: ignore[arg-type]
    )


def project(
    exact_work: LegalWorkItem,
    events: tuple[
        LegalWorkCompletionEvent,
        ...,
    ],
    *,
    evaluated_at: datetime = EVALUATED,
) -> LegalWorkCompletionCurrentness:
    return project_legal_work_completion_currentness(
        work_item=exact_work,
        completion_events=events,
        evaluated_at=evaluated_at,
    )


def test_schema_version_and_closed_state_vocabulary_are_exact() -> None:
    assert (
        SCHEMA
        == "WILSY-LEGAL-WORK-COMPLETION-CURRENTNESS/V1"
    )
    assert (
        VERSION
        == "v1.0.0-P14-R16-WORK-COMPLETION-CURRENTNESS"
    )

    assert {
        value.value
        for value
        in LegalWorkCompletionCurrentnessState
    } == {
        "NOT_COMPLETED",
        "COMPLETED",
        "AMBIGUOUS",
        "CORRUPT_BLOCKED",
    }

    assert {
        value.value
        for value
        in LegalWorkCompletionCurrentnessReason
    } == {
        "NO_COMPLETION_EVENT",
        "EXACT_COMPLETION_EVENT",
        "MULTIPLE_COMPLETION_EVENTS",
        "CORRUPT_COMPLETION_EVIDENCE",
    }


def test_zero_events_is_not_completed() -> None:
    exact_work = work()

    result = project(
        exact_work,
        (),
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.NOT_COMPLETED
    )
    assert (
        result.reason
        is LegalWorkCompletionCurrentnessReason.NO_COMPLETION_EVENT
    )
    assert (
        result.decisive_completion_event_id
        is None
    )
    assert (
        result.decisive_completion_event_fingerprint
        is None
    )
    assert result.candidate_completion_event_ids == ()
    assert (
        result.candidate_completion_event_fingerprints
        == ()
    )
    assert result.normalized_event_count == 0
    assert result.eligible_event_count == 0


def test_one_exact_event_is_completed() -> None:
    exact_work = work()
    event = completion(
        exact_work
    )

    result = project(
        exact_work,
        (
            event,
        ),
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.COMPLETED
    )
    assert (
        result.reason
        is LegalWorkCompletionCurrentnessReason.EXACT_COMPLETION_EVENT
    )
    assert (
        result.decisive_completion_event_id
        == event.completion_event_id
    )
    assert (
        result.decisive_completion_event_fingerprint
        == event.fingerprint
    )
    assert result.normalized_event_count == 1
    assert result.eligible_event_count == 1


def test_exact_duplicate_input_normalizes_by_fingerprint() -> None:
    exact_work = work()
    event = completion(
        exact_work
    )

    result = project(
        exact_work,
        (
            event,
            event,
        ),
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.COMPLETED
    )
    assert result.normalized_event_count == 1
    assert result.eligible_event_count == 1


def test_distinct_multiple_events_are_ambiguous() -> None:
    exact_work = work()

    first = completion(
        exact_work
    )

    second = completion(
        exact_work,
        completion_evidence_reference=
            "completion:evidence:2",
        completion_evidence_fingerprint=
            "d" * 128,
        authorization_evidence_reference=
            "iam:decision:complete:2",
        authorization_evidence_fingerprint=
            "e" * 128,
    )

    result = project(
        exact_work,
        (
            first,
            second,
        ),
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.AMBIGUOUS
    )
    assert (
        result.reason
        is LegalWorkCompletionCurrentnessReason.MULTIPLE_COMPLETION_EVENTS
    )
    assert (
        result.decisive_completion_event_id
        is None
    )
    assert (
        set(
            result.candidate_completion_event_ids
        )
        == {
            first.completion_event_id,
            second.completion_event_id,
        }
    )


@pytest.mark.parametrize(
    (
        "field",
        "value",
    ),
    (
        (
            "tenant_id",
            "tenant-other",
        ),
        (
            "case_matter_id",
            "matter-other",
        ),
        (
            "work_item_id",
            "work-other",
        ),
        (
            "work_item_fingerprint",
            "f" * 128,
        ),
    ),
)
def test_cross_scope_or_wrong_work_binding_is_corrupt_blocked(
    field: str,
    value: object,
) -> None:
    exact_work = work()

    corrupt = completion(
        exact_work,
        **{
            field:
                value
        },
    )

    result = project(
        exact_work,
        (
            corrupt,
        ),
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.CORRUPT_BLOCKED
    )
    assert (
        result.reason
        is LegalWorkCompletionCurrentnessReason.CORRUPT_COMPLETION_EVIDENCE
    )
    assert (
        result.decisive_completion_event_id
        is None
    )
    assert result.corruption_evidence_fingerprints


def test_completion_before_work_creation_is_corrupt_blocked() -> None:
    exact_work = work()

    corrupt = completion(
        exact_work,
        completed_at=(
            CREATED
            - timedelta(
                seconds=1
            )
        ),
    )

    result = project(
        exact_work,
        (
            corrupt,
        ),
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.CORRUPT_BLOCKED
    )


def test_future_completion_event_is_excluded_at_prior_evaluation() -> None:
    exact_work = work()

    future = completion(
        exact_work,
        completed_at=(
            EVALUATED
            + timedelta(
                seconds=1
            )
        ),
    )

    result = project(
        exact_work,
        (
            future,
        ),
        evaluated_at=EVALUATED,
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.NOT_COMPLETED
    )
    assert result.normalized_event_count == 1
    assert result.eligible_event_count == 0


def test_corruption_outranks_otherwise_valid_completion() -> None:
    exact_work = work()

    valid = completion(
        exact_work
    )

    corrupt = completion(
        exact_work,
        case_matter_id="matter-other",
        completion_evidence_reference=
            "completion:evidence:corrupt",
        completion_evidence_fingerprint=
            "d" * 128,
        authorization_evidence_reference=
            "iam:decision:corrupt",
        authorization_evidence_fingerprint=
            "e" * 128,
    )

    result = project(
        exact_work,
        (
            valid,
            corrupt,
        ),
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.CORRUPT_BLOCKED
    )
    assert (
        result.decisive_completion_event_id
        is None
    )


def test_embedded_work_completed_status_does_not_create_currentness() -> None:
    completed_work = work(
        status=LegalWorkItemStatus.COMPLETED,
        completion_evidence_reference=
            "legacy:completion",
        completion_evidence_fingerprint=
            "f" * 128,
        completed_at=COMPLETED,
    )

    result = project(
        completed_work,
        (),
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.NOT_COMPLETED
    )


def test_open_work_with_exact_event_projects_completed_without_mutation() -> None:
    exact_work = work()

    assert (
        exact_work.status
        is LegalWorkItemStatus.OPEN
    )

    event = completion(
        exact_work
    )

    result = project(
        exact_work,
        (
            event,
        ),
    )

    assert (
        result.state
        is LegalWorkCompletionCurrentnessState.COMPLETED
    )
    assert (
        exact_work.status
        is LegalWorkItemStatus.OPEN
    )


def test_currentness_is_deterministic_immutable_and_round_trips() -> None:
    exact_work = work()
    event = completion(
        exact_work
    )

    first = project(
        exact_work,
        (
            event,
        ),
    )

    second = project(
        exact_work,
        (
            event,
        ),
    )

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert first.currentness_id == second.currentness_id

    hydrated = (
        LegalWorkCompletionCurrentness.from_dict(
            first.to_dict()
        )
    )

    assert hydrated == first

    with pytest.raises(
        FrozenInstanceError
    ):
        first.state = (  # type: ignore[misc]
            LegalWorkCompletionCurrentnessState.NOT_COMPLETED
        )


def test_hydration_rejects_extra_missing_and_corrupt_fingerprint() -> None:
    exact_work = work()
    value = project(
        exact_work,
        (),
    )
    raw = value.to_dict()

    missing = dict(
        raw
    )
    missing.pop(
        "reason"
    )

    with pytest.raises(
        LegalWorkCompletionCurrentnessError
    ):
        LegalWorkCompletionCurrentness.from_dict(
            missing
        )

    extra = dict(
        raw
    )
    extra[
        "authorized"
    ] = True

    with pytest.raises(
        LegalWorkCompletionCurrentnessError
    ):
        LegalWorkCompletionCurrentness.from_dict(
            extra
        )

    corrupt = dict(
        raw
    )
    corrupt[
        "fingerprint"
    ] = "f" * 128

    with pytest.raises(
        LegalWorkCompletionCurrentnessError,
        match="FINGERPRINT_MISMATCH",
    ):
        LegalWorkCompletionCurrentness.from_dict(
            corrupt
        )


def test_projection_requires_exact_utc_evaluation_time() -> None:
    exact_work = work()

    with pytest.raises(
        LegalWorkCompletionCurrentnessError,
        match="EVALUATED_AT",
    ):
        project_legal_work_completion_currentness(
            work_item=exact_work,
            completion_events=(),
            evaluated_at=datetime(
                2026,
                10,
                16,
                20,
                0,
            ),
        )


def test_currentness_contains_no_command_dependency_or_other_authority() -> None:
    exact_work = work()
    result = project(
        exact_work,
        (),
    )

    raw = result.to_dict()

    forbidden = {
        "permission_granted",
        "completion_authorized",
        "dependency_satisfied",
        "blocked",
        "released",
        "assignee_principal_id",
        "supervisor_principal_id",
        "legal_event_completed",
        "ai_execution_authorized",
        "payment_id",
        "settlement_id",
    }

    assert forbidden.isdisjoint(
        raw
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_completion_currentness.py
# VERSION: v1.0.0-P14-R16-WORK-COMPLETION-CURRENTNESS-UNIT
# PURE CURRENTNESS: YES
# PERSISTENCE: NONE
# ORIGINAL WORK MUTATION: NONE
# FUTURE FACTS: EXCLUDED
# EXACT DUPLICATES: NORMALIZED
# CORRUPTION: FAIL CLOSED
# AMBIGUITY: FAIL CLOSED
# COMPLETION COMMAND AUTHORITY: NONE
# DEPENDENCY SATISFACTION AUTHORITY: NONE
# IAM / ASSIGNMENT / SUPERVISION AUTHORITY: NONE
# FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
