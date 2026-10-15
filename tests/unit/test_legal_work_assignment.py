"""Direct certificate for G7F-R3 Legal Work Assignment."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_work_assignment import (
    SCHEMA,
    VERSION,
    LegalWorkAssignment,
    LegalWorkAssignmentError,
)


AT = datetime(
    2026,
    10,
    12,
    20,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)


def assignment(**changes: object) -> LegalWorkAssignment:
    values: dict[str, object] = {
        "assignment_id": "assignment-1",
        "tenant_id": "tenant-1",
        "case_matter_id": "matter-1",
        "work_item_id": "work-1",
        "assignee_principal_id": "principal-worker-1",
        "assigned_by_principal_id": "principal-manager-1",
        "assigned_at": AT,
        "assignment_reason_reference": "reason-1",
        "authorization_evidence_reference":
            "authorization-proof-1",
        "supersedes_assignment_id": None,
    }
    values.update(changes)
    return LegalWorkAssignment(**values)  # type: ignore[arg-type]


def test_identity_is_exact() -> None:
    assert VERSION == "v1.0.1-G7F-R3-LEGAL-WORK-ASSIGNMENT"
    assert SCHEMA == "WILSY-LEGAL-WORK-ASSIGNMENT/V1"


def test_valid_assignment_is_exact_and_immutable() -> None:
    value = assignment()

    assert value.tenant_id == "tenant-1"
    assert value.case_matter_id == "matter-1"
    assert value.work_item_id == "work-1"
    assert value.assignee_principal_id == "principal-worker-1"
    assert value.assigned_at.microsecond == 123456
    assert len(value.fingerprint) == 128


@pytest.mark.parametrize(
    "tenant",
    ("default", "global", "root", "*"),
)
def test_pseudo_tenants_reject(
    tenant: str,
) -> None:
    with pytest.raises(
        LegalWorkAssignmentError,
        match="G7F_R3_TENANT_REQUIRED",
    ):
        assignment(tenant_id=tenant)


def test_self_supersession_rejects() -> None:
    with pytest.raises(
        LegalWorkAssignmentError,
        match="G7F_R3_SELF_SUPERSESSION_INVALID",
    ):
        assignment(
            assignment_id="assignment-1",
            supersedes_assignment_id="assignment-1",
        )


def test_reassignment_history_can_reference_previous_assignment() -> None:
    value = assignment(
        assignment_id="assignment-2",
        assignee_principal_id="principal-worker-2",
        supersedes_assignment_id="assignment-1",
    )

    assert value.supersedes_assignment_id == "assignment-1"
    assert value.assignee_principal_id == "principal-worker-2"


def test_assignment_does_not_require_role_name() -> None:
    keys = set(assignment().to_dict())

    assert "role" not in keys
    assert "business_role" not in keys
    assert "authorization_role" not in keys


def test_assignment_contains_no_supervision_authority() -> None:
    keys = set(assignment().to_dict())

    assert "supervisor_id" not in keys
    assert "supervisor_principal_id" not in keys
    assert "supervision_role" not in keys


def test_assignment_contains_no_permission_or_commercial_authority() -> None:
    keys = set(assignment().to_dict())

    forbidden = {
        "permission",
        "permissions",
        "plan_id",
        "subscription_id",
        "entitlement_id",
        "price",
        "invoice_id",
        "payment_id",
        "financial_execution",
    }

    assert not keys & forbidden


def test_assignment_does_not_embed_work_item_fingerprint() -> None:
    keys = set(assignment().to_dict())
    assert "work_item_fingerprint" not in keys


def test_round_trip_preserves_truth() -> None:
    original = assignment()
    restored = LegalWorkAssignment.from_dict(
        original.to_dict()
    )
    assert restored == original


def test_extra_or_missing_field_rejects() -> None:
    payload = assignment().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        LegalWorkAssignmentError,
        match="G7F_R3_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkAssignment.from_dict(payload)

    payload = assignment().to_dict()
    del payload["work_item_id"]

    with pytest.raises(
        LegalWorkAssignmentError,
        match="G7F_R3_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkAssignment.from_dict(payload)


def test_corrupt_fingerprint_rejects() -> None:
    payload = assignment().to_dict()
    payload["fingerprint"] = "a" * 128

    with pytest.raises(
        LegalWorkAssignmentError,
        match="G7F_R3_FINGERPRINT_MISMATCH",
    ):
        LegalWorkAssignment.from_dict(payload)


def test_assignment_is_not_self_declared_current() -> None:
    keys = set(assignment().to_dict())

    assert "is_current" not in keys
    assert "current" not in keys
    assert "active" not in keys
    assert "status" not in keys


# ARTIFACT: test_legal_work_assignment.py
# VERSION: v1.0.1-G7F-R3-LEGAL-WORK-ASSIGNMENT-CERT
