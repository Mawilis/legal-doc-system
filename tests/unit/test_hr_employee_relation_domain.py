"""Direct certificate for immutable sovereign HR employee-relation domain."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
import dataclasses
from typing import Any

import pytest

from tools.eos.saas.domain.hr_operations import (
    EmployeeRelation,
    EmployeeRelationActionType,
    EmployeeRelationError,
    EmployeeRelationStatus,
)


TENANT = "tenant-acme"
RELATION_ID = "relation-001"
EMPLOYEE_ID = "employee-001"
ARTIFACT_ID = "artifact-001"
ARTIFACT_FP = "a" * 128


def issued_relation(**overrides: Any) -> EmployeeRelation:
    values: dict[str, Any] = {
        "tenant_id": TENANT,
        "relation_id": RELATION_ID,
        "employee_id": EMPLOYEE_ID,
        "action_type": EmployeeRelationActionType.WRITTEN_WARNING,
        "incident_date": date(2026, 10, 1),
        "policy_breach": "Attendance policy",
        "incident_summary": "Documented attendance exception.",
        "corrective_action": "Written warning and review.",
        "employee_response": None,
        "hearing_date": None,
        "outcome": None,
        "status": EmployeeRelationStatus.ISSUED,
        "source_artifact_id": ARTIFACT_ID,
        "source_artifact_fingerprint": ARTIFACT_FP,
    }
    values.update(overrides)
    return EmployeeRelation(**values)


def test_employee_relation_is_frozen_and_slotted() -> None:
    value = issued_relation()
    assert dataclasses.is_dataclass(value)
    assert value.__slots__
    with pytest.raises(FrozenInstanceError):
        value.status = EmployeeRelationStatus.CLOSED  # type: ignore[misc]


def test_employee_relation_issued_round_trip_and_fingerprint() -> None:
    value = issued_relation()
    payload = value.to_dict()

    assert payload["tenant_id"] == TENANT
    assert payload["relation_id"] == RELATION_ID
    assert payload["employee_id"] == EMPLOYEE_ID
    assert payload["action_type"] == "Written warning"
    assert payload["status"] == "ISSUED"
    assert payload["incident_date"] == "2026-10-01"
    assert payload["source_artifact_id"] == ARTIFACT_ID
    assert payload["source_artifact_fingerprint"] == ARTIFACT_FP

    fingerprint = payload["fingerprint"]
    assert isinstance(fingerprint, str)
    assert len(fingerprint) == 128
    assert fingerprint == fingerprint.lower()

    hydrated = EmployeeRelation.from_dict(payload)
    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint


def test_employee_relation_draft_can_remain_incomplete() -> None:
    value = EmployeeRelation(
        tenant_id=TENANT,
        relation_id=RELATION_ID,
        employee_id=EMPLOYEE_ID,
        action_type=EmployeeRelationActionType.VERBAL_WARNING,
        status=EmployeeRelationStatus.DRAFT,
    )

    assert value.incident_date is None
    assert value.policy_breach is None
    assert value.incident_summary is None
    assert value.corrective_action is None


@pytest.mark.parametrize(
    "status",
    [
        EmployeeRelationStatus.ISSUED,
        EmployeeRelationStatus.EMPLOYEE_RESPONSE_PENDING,
        EmployeeRelationStatus.HEARING_SCHEDULED,
        EmployeeRelationStatus.CLOSED,
    ],
)
def test_non_draft_relation_requires_core_evidence(
    status: EmployeeRelationStatus,
) -> None:
    with pytest.raises(EmployeeRelationError) as captured:
        EmployeeRelation(
            tenant_id=TENANT,
            relation_id=RELATION_ID,
            employee_id=EMPLOYEE_ID,
            action_type=EmployeeRelationActionType.WRITTEN_WARNING,
            status=status,
        )

    assert captured.value.code == (
        "P0_C12E1_EMPLOYEE_RELATION_EVIDENCE_REQUIRED"
    )


@pytest.mark.parametrize(
    "tenant",
    [
        "MASTER",
        "GLOBAL_ROOT",
        "global",
        "default",
        "*",
        "",
    ],
)
def test_employee_relation_rejects_pseudo_or_missing_tenant(
    tenant: str,
) -> None:
    with pytest.raises(EmployeeRelationError):
        EmployeeRelation(
            tenant_id=tenant,
            relation_id=RELATION_ID,
            employee_id=EMPLOYEE_ID,
            action_type=EmployeeRelationActionType.VERBAL_WARNING,
            status=EmployeeRelationStatus.DRAFT,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("relation_id", " bad"),
        ("relation_id", ""),
        ("employee_id", "employee id"),
        ("employee_id", ""),
    ],
)
def test_employee_relation_rejects_invalid_opaque_identity(
    field: str,
    value: str,
) -> None:
    kwargs: dict[str, Any] = {
        "tenant_id": TENANT,
        "relation_id": RELATION_ID,
        "employee_id": EMPLOYEE_ID,
        "action_type": EmployeeRelationActionType.VERBAL_WARNING,
        "status": EmployeeRelationStatus.DRAFT,
    }

    kwargs[field] = value

    with pytest.raises(EmployeeRelationError):
        EmployeeRelation(**kwargs)


def test_employee_relation_rejects_unbounded_action_type() -> None:
    with pytest.raises(EmployeeRelationError) as captured:
        EmployeeRelation(
            tenant_id=TENANT,
            relation_id=RELATION_ID,
            employee_id=EMPLOYEE_ID,
            action_type="Instant termination authority",
            status=EmployeeRelationStatus.DRAFT,
        )

    assert captured.value.code == (
        "P0_C12E1_EMPLOYEE_RELATION_ACTION_TYPE_INVALID"
    )


def test_employee_relation_rejects_unbounded_status() -> None:
    with pytest.raises(EmployeeRelationError) as captured:
        EmployeeRelation(
            tenant_id=TENANT,
            relation_id=RELATION_ID,
            employee_id=EMPLOYEE_ID,
            action_type=EmployeeRelationActionType.VERBAL_WARNING,
            status="APPROVED",
        )

    assert captured.value.code == (
        "P0_C12E1_EMPLOYEE_RELATION_STATUS_INVALID"
    )


def test_employee_relation_requires_complete_artifact_evidence_pair() -> None:
    with pytest.raises(EmployeeRelationError) as captured:
        issued_relation(
            source_artifact_id=ARTIFACT_ID,
            source_artifact_fingerprint=None,
        )

    assert captured.value.code == (
        "P0_C12E1_EMPLOYEE_RELATION_ARTIFACT_EVIDENCE_INCOMPLETE"
    )


def test_employee_relation_rejects_invalid_artifact_fingerprint() -> None:
    with pytest.raises(EmployeeRelationError) as captured:
        issued_relation(
            source_artifact_fingerprint="A" * 128,
        )

    assert captured.value.code == (
        "P0_C12E1_SOURCE_ARTIFACT_FINGERPRINT_INVALID"
    )


def test_employee_relation_hydration_rejects_schema_drift() -> None:
    payload = issued_relation().to_dict()
    payload["unexpected"] = "authority"

    with pytest.raises(EmployeeRelationError) as captured:
        EmployeeRelation.from_dict(payload)

    assert captured.value.code == (
        "P0_C12E1_EMPLOYEE_RELATION_SCHEMA_INVALID"
    )


def test_employee_relation_hydration_rejects_tampered_fingerprint() -> None:
    payload = issued_relation().to_dict()
    payload["corrective_action"] = "Different sanction"

    with pytest.raises(EmployeeRelationError) as captured:
        EmployeeRelation.from_dict(payload)

    assert captured.value.code == (
        "P0_C12E1_EMPLOYEE_RELATION_FINGERPRINT_MISMATCH"
    )


def test_employee_relation_contains_no_financial_execution_authority() -> None:
    field_names = {
        field.name
        for field in dataclasses.fields(EmployeeRelation)
    }

    forbidden = {
        "payment_id",
        "payment_status",
        "execution_id",
        "settlement_id",
        "bank_account",
        "release_authority",
        "financial_execution",
        "amount",
    }

    assert field_names.isdisjoint(forbidden)
