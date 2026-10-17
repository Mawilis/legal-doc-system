"""
WILSY OS — P14-R13 Legal Work Completion Event Unit Certificate

VERSION: v1.0.0-P14-R13-WORK-COMPLETION-EVENT-UNIT

PURPOSE:
    Certify one immutable work-completion fact bound to exact pre-existing
    work truth, exact completion evidence, actor provenance and exact
    authorization-evidence provenance without granting IAM, assignment,
    supervision, dependency-satisfaction, legal-event or financial authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_work_completion_event import (
    SCHEMA,
    VERSION,
    LegalWorkCompletionEvent,
    LegalWorkCompletionEventError,
)


AT = datetime(
    2026,
    10,
    16,
    19,
    0,
    tzinfo=timezone.utc,
)

WORK_FP = "a" * 128
COMPLETION_FP = "b" * 128
AUTH_FP = "c" * 128


def event(
    **overrides: object,
) -> LegalWorkCompletionEvent:
    values: dict[str, object] = {
        "tenant_id": "tenant-law",
        "case_matter_id": "matter-1",
        "work_item_id": "work-1",
        "work_item_fingerprint": WORK_FP,
        "completion_evidence_reference":
            "evidence:document-review:complete",
        "completion_evidence_fingerprint":
            COMPLETION_FP,
        "completed_at":
            AT,
        "actor_principal_id":
            "principal-attorney-1",
        "authorization_evidence_reference":
            "iam-decision:complete-work:1",
        "authorization_evidence_fingerprint":
            AUTH_FP,
    }

    values.update(
        overrides
    )

    return LegalWorkCompletionEvent(
        **values  # type: ignore[arg-type]
    )


def test_schema_version_identity_and_immutability_are_exact() -> None:
    value = event()

    assert (
        SCHEMA
        == "WILSY-LEGAL-WORK-COMPLETION-EVENT/V1"
    )
    assert (
        VERSION
        == "v1.0.0-P14-R13-WORK-COMPLETION-EVENT"
    )
    assert value.schema == SCHEMA
    assert value.completion_event_version == VERSION

    assert (
        len(value.completion_event_id)
        == 128
    )
    assert (
        len(value.fingerprint)
        == 128
    )
    assert (
        value.completion_event_id
        == value.completion_event_id.lower()
    )
    assert (
        value.fingerprint
        == value.fingerprint.lower()
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        value.actor_principal_id = "other"  # type: ignore[misc]


def test_identity_is_deterministic_for_exact_completion_fact() -> None:
    assert event() == event()
    assert (
        event().completion_event_id
        == event().completion_event_id
    )
    assert (
        event().fingerprint
        == event().fingerprint
    )


@pytest.mark.parametrize(
    (
        "field",
        "changed",
    ),
    (
        (
            "case_matter_id",
            "matter-2",
        ),
        (
            "work_item_id",
            "work-2",
        ),
        (
            "work_item_fingerprint",
            "d" * 128,
        ),
        (
            "completion_evidence_reference",
            "evidence:other",
        ),
        (
            "completion_evidence_fingerprint",
            "d" * 128,
        ),
        (
            "completed_at",
            AT + timedelta(seconds=1),
        ),
        (
            "actor_principal_id",
            "principal-attorney-2",
        ),
        (
            "authorization_evidence_reference",
            "iam-decision:complete-work:2",
        ),
        (
            "authorization_evidence_fingerprint",
            "d" * 128,
        ),
    ),
)
def test_any_completion_binding_change_changes_identity(
    field: str,
    changed: object,
) -> None:
    baseline = event()
    changed_value = event(
        **{
            field:
                changed
        }
    )

    assert (
        baseline.completion_event_id
        != changed_value.completion_event_id
    )
    assert (
        baseline.fingerprint
        != changed_value.fingerprint
    )


@pytest.mark.parametrize(
    "tenant",
    (
        "",
        " tenant-law",
        "tenant-law ",
        "default",
        "global",
        "root",
        "*",
    ),
)
def test_tenant_scope_is_exact_and_pseudo_tenants_reject(
    tenant: str,
) -> None:
    with pytest.raises(
        LegalWorkCompletionEventError
    ):
        event(
            tenant_id=tenant
        )


@pytest.mark.parametrize(
    "field",
    (
        "work_item_fingerprint",
        "completion_evidence_fingerprint",
        "authorization_evidence_fingerprint",
    ),
)
def test_all_bound_fingerprints_require_lowercase_sha3_512_shape(
    field: str,
) -> None:
    with pytest.raises(
        LegalWorkCompletionEventError,
        match="FINGERPRINT",
    ):
        event(
            **{
                field:
                    "A" * 128
            }
        )

    with pytest.raises(
        LegalWorkCompletionEventError,
        match="FINGERPRINT",
    ):
        event(
            **{
                field:
                    "a" * 127
            }
        )


def test_completed_at_requires_exact_utc_instant() -> None:
    with pytest.raises(
        LegalWorkCompletionEventError,
        match="COMPLETED_AT",
    ):
        event(
            completed_at=datetime(
                2026,
                10,
                16,
                19,
                0,
            )
        )

    with pytest.raises(
        LegalWorkCompletionEventError,
        match="COMPLETED_AT",
    ):
        event(
            completed_at=datetime(
                2026,
                10,
                16,
                21,
                0,
                tzinfo=timezone(
                    timedelta(
                        hours=2
                    )
                ),
            )
        )


def test_actor_and_evidence_references_are_required_exact_text() -> None:
    for field in (
        "work_item_id",
        "completion_evidence_reference",
        "actor_principal_id",
        "authorization_evidence_reference",
    ):
        with pytest.raises(
            LegalWorkCompletionEventError
        ):
            event(
                **{
                    field:
                        ""
                }
            )

        with pytest.raises(
            LegalWorkCompletionEventError
        ):
            event(
                **{
                    field:
                        " padded "
                }
            )


def test_round_trip_preserves_exact_truth() -> None:
    value = event()

    raw = value.to_dict()

    assert (
        LegalWorkCompletionEvent.from_dict(
            raw
        )
        == value
    )


def test_hydration_rejects_missing_extra_and_corrupt_truth() -> None:
    raw = event().to_dict()

    missing = dict(
        raw
    )
    missing.pop(
        "actor_principal_id"
    )

    with pytest.raises(
        LegalWorkCompletionEventError
    ):
        LegalWorkCompletionEvent.from_dict(
            missing
        )

    extra = dict(
        raw
    )
    extra[
        "satisfied"
    ] = True

    with pytest.raises(
        LegalWorkCompletionEventError
    ):
        LegalWorkCompletionEvent.from_dict(
            extra
        )

    corrupt = dict(
        raw
    )
    corrupt[
        "fingerprint"
    ] = "d" * 128

    with pytest.raises(
        LegalWorkCompletionEventError,
        match="FINGERPRINT_MISMATCH",
    ):
        LegalWorkCompletionEvent.from_dict(
            corrupt
        )


def test_domain_contains_no_dependency_satisfaction_or_mutable_work_state() -> None:
    public = {
        name
        for name in dir(
            LegalWorkCompletionEvent
        )
        if not name.startswith("_")
    }

    forbidden = {
        "satisfied",
        "mark_satisfied",
        "blocked",
        "is_blocked",
        "release",
        "status",
        "set_status",
        "update_work_item",
    }

    assert public.isdisjoint(
        forbidden
    )


def test_domain_contains_no_assignment_supervision_iam_or_finance_authority() -> None:
    value = event()
    raw = value.to_dict()

    forbidden_fields = {
        "assignee_principal_id",
        "supervisor_principal_id",
        "iam_granted",
        "permission_granted",
        "legal_event_completed",
        "payment_id",
        "settlement_id",
    }

    assert forbidden_fields.isdisjoint(
        raw
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_completion_event.py
# VERSION: v1.0.0-P14-R13-WORK-COMPLETION-EVENT-UNIT
# IMMUTABLE COMPLETION FACT: REQUIRED
# ORIGINAL WORK MUTATION: FORBIDDEN
# EXACT WORK ID/FINGERPRINT BINDING: REQUIRED
# COMPLETION EVIDENCE: REQUIRED
# ACTOR PROVENANCE: REQUIRED
# AUTHORIZATION EVIDENCE PROVENANCE: REQUIRED
# DEPENDENCY SATISFACTION AUTHORITY: NONE
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
