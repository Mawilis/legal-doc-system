"""Direct certificate for G7E Legal Work Item."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_work_item import (
    SCHEMA,
    VERSION,
    LegalWorkItem,
    LegalWorkItemError,
    LegalWorkItemStatus,
)


CREATED = datetime(
    2026,
    10,
    12,
    20,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)

FP = "a" * 128
COMPLETE_FP = "b" * 128


def item(**changes: object) -> LegalWorkItem:
    values: dict[str, object] = {
        "work_item_id": "work-1",
        "tenant_id": "tenant-1",
        "case_matter_id": "matter-1",
        "title": "Review conflict screening",
        "source_kind": "LEGAL_CONFLICT_SCREENING",
        "source_reference": "screening-1",
        "source_evidence_fingerprint": FP,
        "status": LegalWorkItemStatus.OPEN,
        "created_at": CREATED,
        "due_at": CREATED + timedelta(days=1),
    }
    values.update(changes)
    return LegalWorkItem(**values)  # type: ignore[arg-type]


def test_identity_is_exact() -> None:
    assert VERSION == "v1.0.1-G7E-LEGAL-WORK-ITEM"
    assert SCHEMA == "WILSY-LEGAL-WORK-ITEM/V1"


def test_open_item_is_exact_matter_scoped_truth() -> None:
    value = item()

    assert value.tenant_id == "tenant-1"
    assert value.case_matter_id == "matter-1"
    assert value.status is LegalWorkItemStatus.OPEN
    assert value.created_at.microsecond == 123456
    assert len(value.fingerprint) == 128


@pytest.mark.parametrize(
    "tenant",
    ("default", "global", "root", "*"),
)
def test_pseudo_tenants_reject(
    tenant: str,
) -> None:
    with pytest.raises(
        LegalWorkItemError,
        match="G7E_TENANT_REQUIRED",
    ):
        item(tenant_id=tenant)


def test_status_is_closed_and_case_sensitive() -> None:
    with pytest.raises(
        LegalWorkItemError,
        match="G7E_STATUS_INVALID",
    ):
        item(status="open")


def test_due_before_creation_rejects() -> None:
    with pytest.raises(
        LegalWorkItemError,
        match="G7E_DUE_AT_BEFORE_CREATED",
    ):
        item(
            due_at=CREATED - timedelta(seconds=1),
        )


def test_due_at_is_optional_and_not_calculated() -> None:
    value = item(due_at=None)
    assert value.due_at is None


def test_completed_requires_exact_completion_evidence() -> None:
    with pytest.raises(
        LegalWorkItemError,
        match="G7E_COMPLETION_EVIDENCE_REQUIRED",
    ):
        item(status="COMPLETED")


def test_completed_accepts_evidence_without_source_truth_mutation() -> None:
    value = item(
        status="COMPLETED",
        completion_evidence_reference="completion-1",
        completion_evidence_fingerprint=COMPLETE_FP,
        completed_at=CREATED + timedelta(hours=2),
    )

    assert value.status is LegalWorkItemStatus.COMPLETED
    assert value.source_kind == "LEGAL_CONFLICT_SCREENING"
    assert value.source_reference == "screening-1"
    assert value.source_evidence_fingerprint == FP


def test_completion_evidence_rejects_on_non_completed_item() -> None:
    with pytest.raises(
        LegalWorkItemError,
        match="G7E_COMPLETION_EVIDENCE_NOT_ALLOWED",
    ):
        item(
            completion_evidence_reference="completion-1",
            completion_evidence_fingerprint=COMPLETE_FP,
            completed_at=CREATED + timedelta(hours=2),
        )


def test_cancelled_requires_reason_and_time() -> None:
    with pytest.raises(
        LegalWorkItemError,
        match="G7E_CANCELLATION_EVIDENCE_REQUIRED",
    ):
        item(status="CANCELLED")


def test_cancelled_accepts_reference_without_completion() -> None:
    value = item(
        status="CANCELLED",
        cancellation_reason_reference="cancel-1",
        cancelled_at=CREATED + timedelta(hours=1),
    )

    assert value.status is LegalWorkItemStatus.CANCELLED
    assert value.completion_evidence_reference is None


def test_completion_and_cancellation_cannot_coexist() -> None:
    with pytest.raises(
        LegalWorkItemError,
        match="G7E_COMPLETION_CANCELLATION_CONFLICT",
    ):
        item(
            status="COMPLETED",
            completion_evidence_reference="completion-1",
            completion_evidence_fingerprint=COMPLETE_FP,
            completed_at=CREATED + timedelta(hours=1),
            cancellation_reason_reference="cancel-1",
            cancelled_at=CREATED + timedelta(hours=1),
        )


def test_round_trip_preserves_exact_truth() -> None:
    original = item()
    restored = LegalWorkItem.from_dict(
        original.to_dict()
    )
    assert restored == original


def test_corrupt_fingerprint_rejects() -> None:
    payload = item().to_dict()
    payload["fingerprint"] = "c" * 128

    with pytest.raises(
        LegalWorkItemError,
        match="G7E_FINGERPRINT_MISMATCH",
    ):
        LegalWorkItem.from_dict(payload)


def test_extra_or_missing_fields_reject() -> None:
    payload = item().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        LegalWorkItemError,
        match="G7E_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkItem.from_dict(payload)

    payload = item().to_dict()
    del payload["title"]

    with pytest.raises(
        LegalWorkItemError,
        match="G7E_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkItem.from_dict(payload)


def test_domain_contains_no_assignment_iam_or_commercial_authority() -> None:
    keys = set(item().to_dict())

    forbidden = {
        "principal_id",
        "assignee_id",
        "supervisor_id",
        "role_id",
        "permission",
        "authorization",
        "plan_id",
        "subscription_id",
        "entitlement_id",
        "price",
        "invoice_id",
        "payment_id",
    }

    assert not keys & forbidden


def test_status_does_not_reuse_matter_or_source_domain_state() -> None:
    values = {
        state.value
        for state in LegalWorkItemStatus
    }

    assert values == {
        "OPEN",
        "IN_PROGRESS",
        "BLOCKED",
        "COMPLETED",
        "CANCELLED",
    }

    assert "REVIEW_REQUIRED" not in values
    assert "OVERDUE" not in values
    assert "APPOINTED" not in values
    assert "ACKNOWLEDGED" not in values


# ARTIFACT: test_legal_work_item.py
# VERSION: v1.0.1-G7E-LEGAL-WORK-ITEM-CERT
