"""
WILSY OS — Legal Specialist Workflow Projection Contract

PURPOSE:
    Freeze the first sovereign contract for projecting workflow explanation
    onto already-authorized Legal productive work.

ARCHITECTURE RULE:
    LegalProductiveWorkProjection is the visibility/authority ceiling.
    Workflow, stage, gate, dependency or materialization evidence may enrich
    only work already admitted by that projection. It must never introduce a
    new work item, assignment, supervision relationship, IAM permission,
    professional authority, workflow-transition authority, deadline truth,
    payment authority or settlement authority.

TEST-FIRST STATUS:
    RED contract. Production implementation intentionally does not yet exist.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)
from tools.eos.legal_operations.domain.legal_specialist_workflow_projection import (
    LegalSpecialistWorkflowContext,
    LegalSpecialistWorkflowProjection,
    LegalSpecialistWorkflowProjectionError,
    LegalSpecialistWorkflowRow,
    compose_legal_specialist_workflow_projection,
)


NOW = datetime(
    2026,
    10,
    18,
    5,
    30,
    tzinfo=timezone.utc,
)


def _productive_projection() -> LegalProductiveWorkProjection:
    """
    Build the smallest valid productive-work authority ceiling.

    Rows are intentionally empty here; later behavioral tests will use
    canonical LegalWorkItem values once the public projection contract exists.
    """
    return LegalProductiveWorkProjection(
        tenant_id="tenant-a",
        principal_id="principal-a",
        as_of=NOW,
        operating_contexts=(),
        capability_ids=(),
        assigned_work_items=(),
        supervised_work_items=(),
        overdue_work_items=(),
        due_soon_work_items=(),
    )


def test_public_projection_contract_is_frozen_and_non_authorizing() -> None:
    row = LegalSpecialistWorkflowRow(
        work_item_id="work-001",
        case_matter_id="matter-001",
        workflow_instance_id="instance-001",
        workflow_definition_id="workflow-001",
        stage_definition_id="stage-review",
        readiness="ACTIONABLE",
        blocking_dependency_work_item_ids=(),
        unsatisfied_gate_references=(),
        materialization_transition_id="transition-001",
        materialization_receipt_id="receipt-001",
    )

    projection = LegalSpecialistWorkflowProjection(
        tenant_id="tenant-a",
        principal_id="principal-a",
        as_of=NOW,
        rows=(row,),
    )

    assert projection.tenant_id == "tenant-a"
    assert projection.principal_id == "principal-a"
    assert projection.rows == (row,)

    with pytest.raises(FrozenInstanceError):
        projection.principal_id = "principal-b"  # type: ignore[misc]


def test_workflow_context_is_explanatory_not_authorizing() -> None:
    context = LegalSpecialistWorkflowContext(
        tenant_id="tenant-a",
        work_item_id="work-001",
        case_matter_id="matter-001",
        workflow_instance_id="instance-001",
        workflow_definition_id="workflow-001",
        stage_definition_id="stage-review",
        blocking_dependency_work_item_ids=(),
        unsatisfied_gate_references=("partner-approval",),
        materialization_transition_id="transition-001",
        materialization_receipt_id="receipt-001",
    )

    assert not hasattr(context, "permission")
    assert not hasattr(context, "role")
    assert not hasattr(context, "assignment")
    assert not hasattr(context, "authorize")
    assert not hasattr(context, "financial_authority")


def test_productive_work_projection_is_absolute_visibility_ceiling() -> None:
    """
    Workflow evidence cannot manufacture a daily-work row.

    The productive projection admits no work. Even if workflow context contains
    a work-item identity, the composed specialist projection must remain empty.
    """
    result = compose_legal_specialist_workflow_projection(
        productive_work=_productive_projection(),
        workflow_contexts=(
            LegalSpecialistWorkflowContext(
                tenant_id="tenant-a",
                work_item_id="work-not-authorized",
                case_matter_id="matter-001",
                workflow_instance_id="instance-001",
                workflow_definition_id="workflow-001",
                stage_definition_id="stage-review",
                blocking_dependency_work_item_ids=(),
                unsatisfied_gate_references=(),
                materialization_transition_id="transition-001",
                materialization_receipt_id="receipt-001",
            ),
        ),
    )

    assert result.rows == ()


def test_foreign_tenant_workflow_context_fails_closed() -> None:
    with pytest.raises(
        LegalSpecialistWorkflowProjectionError,
        match="TENANT",
    ):
        compose_legal_specialist_workflow_projection(
            productive_work=_productive_projection(),
            workflow_contexts=(
                LegalSpecialistWorkflowContext(
                    tenant_id="tenant-b",
                    work_item_id="work-001",
                    case_matter_id="matter-001",
                    workflow_instance_id="instance-001",
                    workflow_definition_id="workflow-001",
                    stage_definition_id="stage-review",
                    blocking_dependency_work_item_ids=(),
                    unsatisfied_gate_references=(),
                    materialization_transition_id="transition-001",
                    materialization_receipt_id="receipt-001",
                ),
            ),
        )


def test_readiness_vocabulary_is_closed_and_explanatory() -> None:
    """
    The projection may describe readiness but may not grant execution authority.

    Initial frozen vocabulary:
      ACTIONABLE
      BLOCKED_DEPENDENCY
      BLOCKED_GATE
      BLOCKED_DEPENDENCY_AND_GATE
    """
    valid = {
        "ACTIONABLE",
        "BLOCKED_DEPENDENCY",
        "BLOCKED_GATE",
        "BLOCKED_DEPENDENCY_AND_GATE",
    }

    for readiness in valid:
        row = LegalSpecialistWorkflowRow(
            work_item_id=f"work-{readiness.lower()}",
            case_matter_id="matter-001",
            workflow_instance_id="instance-001",
            workflow_definition_id="workflow-001",
            stage_definition_id="stage-review",
            readiness=readiness,
            blocking_dependency_work_item_ids=(),
            unsatisfied_gate_references=(),
            materialization_transition_id=None,
            materialization_receipt_id=None,
        )
        assert row.readiness == readiness

    with pytest.raises(
        LegalSpecialistWorkflowProjectionError,
        match="READINESS",
    ):
        LegalSpecialistWorkflowRow(
            work_item_id="work-invalid",
            case_matter_id="matter-001",
            workflow_instance_id="instance-001",
            workflow_definition_id="workflow-001",
            stage_definition_id="stage-review",
            readiness="AUTHORIZED_TO_EXECUTE",
            blocking_dependency_work_item_ids=(),
            unsatisfied_gate_references=(),
            materialization_transition_id=None,
            materialization_receipt_id=None,
        )
