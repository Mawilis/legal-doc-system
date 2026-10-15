"""Direct certificate for G7G-R3 Legal Workflow Stage."""
from __future__ import annotations

import pytest

from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
)
from tools.eos.legal_operations.domain.legal_workflow_stage import (
    SCHEMA,
    VERSION,
    LegalWorkflowStage,
    LegalWorkflowStageError,
)


def workflow() -> LegalWorkflowDefinition:
    return LegalWorkflowDefinition(
        workflow_definition_id="workflow-litigation-core",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Litigation Core",
        description_reference="workflow-litigation-description",
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=CATALOGUE_FINGERPRINT,
    )


def stage(
    *,
    stage_definition_id: str = "stage-conflict",
    name: str = "Conflict Review",
    description_reference: str = "stage-conflict-description",
    is_entry_stage: bool = True,
    is_terminal_stage: bool = False,
    successor_stage_ids: tuple[str, ...] = (
        "stage-engagement",
    ),
    work_requirement_references: tuple[str, ...] = (
        "work-requirement:conflict-review",
    ),
    completion_gate_references: tuple[str, ...] = (
        "gate:conflict-disposition-current",
    ),
    automation_references: tuple[str, ...] = (),
) -> LegalWorkflowStage:
    return LegalWorkflowStage.from_workflow_definition(
        workflow_definition=workflow(),
        stage_definition_id=stage_definition_id,
        name=name,
        description_reference=description_reference,
        is_entry_stage=is_entry_stage,
        is_terminal_stage=is_terminal_stage,
        successor_stage_ids=successor_stage_ids,
        work_requirement_references=
            work_requirement_references,
        completion_gate_references=
            completion_gate_references,
        automation_references=
            automation_references,
    )


def test_identity_is_exact() -> None:
    assert VERSION == "v1.0.1-G7G-R3-LEGAL-WORKFLOW-STAGE"
    assert SCHEMA == "WILSY-LEGAL-WORKFLOW-STAGE/V1"


def test_stage_binds_exact_workflow_definition() -> None:
    definition = workflow()
    value = stage()

    assert (
        value.workflow_definition_id
        == definition.workflow_definition_id
    )
    assert (
        value.definition_revision
        == definition.definition_revision
    )
    assert (
        value.workflow_definition_fingerprint
        == definition.fingerprint
    )
    assert len(value.fingerprint) == 128


def test_branching_successors_are_supported() -> None:
    value = stage(
        successor_stage_ids=(
            "stage-engagement",
            "stage-escalation",
        ),
    )

    assert value.successor_stage_ids == (
        "stage-engagement",
        "stage-escalation",
    )


def test_terminal_stage_has_no_successor() -> None:
    value = stage(
        stage_definition_id="stage-close",
        is_entry_stage=False,
        is_terminal_stage=True,
        successor_stage_ids=(),
        work_requirement_references=(),
        completion_gate_references=(
            "gate:matter-close-ready",
        ),
    )

    assert value.is_terminal_stage is True
    assert value.successor_stage_ids == ()


def test_terminal_stage_with_successor_rejects() -> None:
    with pytest.raises(
        LegalWorkflowStageError,
        match="G7G_R3_TERMINAL_STAGE_HAS_SUCCESSOR",
    ):
        stage(
            is_terminal_stage=True,
            successor_stage_ids=(
                "stage-other",
            ),
        )


def test_non_terminal_stage_requires_successor() -> None:
    with pytest.raises(
        LegalWorkflowStageError,
        match=(
            "G7G_R3_NON_TERMINAL_STAGE_REQUIRES_SUCCESSOR"
        ),
    ):
        stage(
            successor_stage_ids=(),
        )


def test_self_successor_rejects() -> None:
    with pytest.raises(
        LegalWorkflowStageError,
        match="G7G_R3_SELF_SUCCESSOR_INVALID",
    ):
        stage(
            successor_stage_ids=(
                "stage-conflict",
            ),
        )


@pytest.mark.parametrize(
    (
        "field",
        "value",
        "code",
    ),
    (
        (
            "successor_stage_ids",
            (
                "stage-engagement",
                "stage-engagement",
            ),
            "G7G_R3_SUCCESSOR_STAGE_IDS_DUPLICATE",
        ),
        (
            "work_requirement_references",
            (
                "work:x",
                "work:x",
            ),
            "G7G_R3_WORK_REQUIREMENT_REFERENCES_DUPLICATE",
        ),
        (
            "completion_gate_references",
            (
                "gate:x",
                "gate:x",
            ),
            "G7G_R3_COMPLETION_GATE_REFERENCES_DUPLICATE",
        ),
        (
            "automation_references",
            (
                "automation:x",
                "automation:x",
            ),
            "G7G_R3_AUTOMATION_REFERENCES_DUPLICATE",
        ),
    ),
)
def test_duplicate_references_reject(
    field: str,
    value: tuple[str, ...],
    code: str,
) -> None:
    changes: dict[str, object] = {
        field: value,
    }

    with pytest.raises(
        LegalWorkflowStageError,
        match=code,
    ):
        if field == "successor_stage_ids":
            stage(
                successor_stage_ids=value,
            )
        elif field == "work_requirement_references":
            stage(
                work_requirement_references=value,
            )
        elif field == "completion_gate_references":
            stage(
                completion_gate_references=value,
            )
        else:
            stage(
                automation_references=value,
            )

    assert changes[field] == value


def test_work_gate_and_automation_references_are_configuration_only() -> None:
    value = stage(
        automation_references=(
            "automation:notify-client",
        ),
    )

    assert value.work_requirement_references == (
        "work-requirement:conflict-review",
    )
    assert value.completion_gate_references == (
        "gate:conflict-disposition-current",
    )
    assert value.automation_references == (
        "automation:notify-client",
    )


def test_no_assignment_supervision_or_iam_authority() -> None:
    keys = set(
        stage().to_dict()
    )

    forbidden = {
        "assignee_principal_id",
        "assigned_by_principal_id",
        "supervisor_principal_id",
        "supervisee_principal_id",
        "business_role",
        "authorization_role",
        "permission",
        "permissions",
    }

    assert not keys & forbidden


def test_no_instance_or_legal_event_authority() -> None:
    keys = set(
        stage().to_dict()
    )

    forbidden = {
        "workflow_instance_id",
        "current_stage_id",
        "stage_instance_id",
        "legal_event_id",
        "matter_status",
        "matter_state",
        "is_complete",
        "completed_at",
    }

    assert not keys & forbidden


def test_no_commercial_or_financial_authority() -> None:
    keys = set(
        stage().to_dict()
    )

    forbidden = {
        "plan_id",
        "subscription_id",
        "entitlement_id",
        "price",
        "invoice_id",
        "payment_id",
        "financial_execution",
    }

    assert not keys & forbidden


def test_round_trip_preserves_exact_truth() -> None:
    original = stage(
        successor_stage_ids=(
            "stage-engagement",
            "stage-escalation",
        ),
        automation_references=(
            "automation:notify-owner",
        ),
    )

    restored = LegalWorkflowStage.from_dict(
        original.to_dict()
    )

    assert restored == original


def test_corrupt_definition_fingerprint_shape_rejects() -> None:
    value = stage().to_dict()

    value[
        "workflow_definition_fingerprint"
    ] = "bad"

    with pytest.raises(
        LegalWorkflowStageError,
        match=(
            "G7G_R3_WORKFLOW_DEFINITION_FINGERPRINT_INVALID"
        ),
    ):
        LegalWorkflowStage.from_dict(
            value
        )


def test_corrupt_stage_fingerprint_rejects() -> None:
    payload = stage().to_dict()
    payload["fingerprint"] = "a" * 128

    with pytest.raises(
        LegalWorkflowStageError,
        match="G7G_R3_FINGERPRINT_MISMATCH",
    ):
        LegalWorkflowStage.from_dict(
            payload
        )


def test_extra_or_missing_field_rejects() -> None:
    payload = stage().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        LegalWorkflowStageError,
        match="G7G_R3_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkflowStage.from_dict(
            payload
        )

    payload = stage().to_dict()
    del payload["stage_definition_id"]

    with pytest.raises(
        LegalWorkflowStageError,
        match="G7G_R3_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkflowStage.from_dict(
            payload
        )


# ARTIFACT: test_legal_workflow_stage.py
# VERSION: v1.0.1-G7G-R3-LEGAL-WORKFLOW-STAGE-CERT
