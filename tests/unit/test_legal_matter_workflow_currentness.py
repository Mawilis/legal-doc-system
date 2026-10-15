"""Direct certificate for G7G-R11 Legal Matter Workflow Currentness."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
)
from tools.eos.legal_operations.domain.legal_workflow_stage import (
    LegalWorkflowStage,
)
from tools.eos.legal_operations.domain.legal_workflow_topology import (
    LegalWorkflowTopology,
)
from tools.eos.legal_operations.domain.tenant_legal_operating_model import (
    TenantLegalOperatingModel,
)
from tools.eos.legal_operations.domain.tenant_legal_workflow_activation import (
    TenantLegalWorkflowActivation,
)
from tools.eos.legal_operations.domain.legal_matter_workflow_instance import (
    LegalMatterWorkflowInstance,
)
from tools.eos.legal_operations.domain.legal_matter_workflow_transition import (
    LegalMatterWorkflowTransition,
)
from tools.eos.legal_operations.domain.legal_matter_workflow_currentness import (
    SCHEMA,
    VERSION,
    LegalMatterWorkflowCurrentness,
    LegalMatterWorkflowCurrentnessError,
)


AT = datetime(
    2026,
    10,
    13,
    1,
    40,
    0,
    123456,
    tzinfo=timezone.utc,
)


def chain() -> tuple[
    LegalMatterWorkflowInstance,
    LegalMatterWorkflowTransition,
    LegalMatterWorkflowTransition,
]:
    model = TenantLegalOperatingModel(
        tenant_id="tenant-1",
        operating_model_id="model-1",
        revision=1,
        activated_item_ids=("PRACTICE_DISPUTES",),
        effective_from=AT,
        supersedes_operating_model_id=None,
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    definition = LegalWorkflowDefinition(
        workflow_definition_id="wf-current",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Workflow",
        description_reference="workflow",
        required_operating_item_ids=("PRACTICE_DISPUTES",),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    s1 = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=definition,
        stage_definition_id="s1",
        name="S1",
        description_reference="s1",
        is_entry_stage=True,
        is_terminal_stage=False,
        successor_stage_ids=("s2",),
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )

    s2 = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=definition,
        stage_definition_id="s2",
        name="S2",
        description_reference="s2",
        is_entry_stage=False,
        is_terminal_stage=False,
        successor_stage_ids=("s3",),
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )

    s3 = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=definition,
        stage_definition_id="s3",
        name="S3",
        description_reference="s3",
        is_entry_stage=False,
        is_terminal_stage=True,
        successor_stage_ids=(),
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )

    topology = LegalWorkflowTopology.from_definition_and_stages(
        workflow_definition=definition,
        stages=(s1, s2, s3),
    )

    activation = TenantLegalWorkflowActivation.from_authorities(
        activation_id="activation-current",
        activation_revision=1,
        operating_model=model,
        workflow_definition=definition,
        workflow_topology=topology,
        commercial_eligibility_evidence_reference="commercial",
        activation_reason_reference="reason",
        effective_from=AT,
    )

    instance = LegalMatterWorkflowInstance.from_authorities(
        workflow_instance_id="instance-current",
        case_matter_id="matter-1",
        activation=activation,
        workflow_definition=definition,
        workflow_topology=topology,
        started_at=AT,
        started_by_principal_id="p1",
        start_authorization_evidence_reference="start-auth",
    )

    first = LegalMatterWorkflowTransition.from_authorities(
        transition_id="t1",
        workflow_instance=instance,
        workflow_topology=topology,
        source_stage=s1,
        target_stage=s2,
        gate_satisfactions=(),
        transitioned_at=AT + timedelta(minutes=1),
        transitioned_by_principal_id="p2",
        transition_authorization_evidence_reference="auth-1",
    )

    second = LegalMatterWorkflowTransition.from_authorities(
        transition_id="t2",
        workflow_instance=instance,
        workflow_topology=topology,
        source_stage=s2,
        target_stage=s3,
        gate_satisfactions=(),
        transitioned_at=AT + timedelta(minutes=2),
        transitioned_by_principal_id="p2",
        transition_authorization_evidence_reference="auth-2",
        previous_transition=first,
    )

    return instance, first, second


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.1-G7G-R11-LEGAL-MATTER-WORKFLOW-CURRENTNESS"
    )
    assert (
        SCHEMA
        == "WILSY-LEGAL-MATTER-WORKFLOW-CURRENTNESS/V1"
    )


def test_empty_history_derives_instance_entry_stage() -> None:
    instance, _, _ = chain()

    value = LegalMatterWorkflowCurrentness.derive(
        currentness_id="current-0",
        workflow_instance=instance,
        transitions=(),
    )

    assert (
        value.current_stage_definition_id
        == instance.entry_stage_definition_id
        == "s1"
    )

    assert value.transition_count == 0
    assert value.head_transition_id is None
    assert value.head_transition_fingerprint is None


def test_complete_history_derives_final_target() -> None:
    instance, first, second = chain()

    value = LegalMatterWorkflowCurrentness.derive(
        currentness_id="current-2",
        workflow_instance=instance,
        transitions=(first, second),
    )

    assert value.current_stage_definition_id == "s3"
    assert value.transition_count == 2
    assert value.head_transition_id == "t2"
    assert (
        value.head_transition_fingerprint
        == second.fingerprint
    )


def test_input_order_does_not_change_currentness() -> None:
    instance, first, second = chain()

    ordered = LegalMatterWorkflowCurrentness.derive(
        currentness_id="current-x",
        workflow_instance=instance,
        transitions=(first, second),
    )

    reversed_value = LegalMatterWorkflowCurrentness.derive(
        currentness_id="current-x",
        workflow_instance=instance,
        transitions=(second, first),
    )

    assert ordered == reversed_value
    assert ordered.fingerprint == reversed_value.fingerprint


def test_sequence_gap_rejects() -> None:
    instance, _, second = chain()

    with pytest.raises(
        LegalMatterWorkflowCurrentnessError,
        match="G7G_R11_SEQUENCE_GAP",
    ):
        LegalMatterWorkflowCurrentness.derive(
            currentness_id="bad",
            workflow_instance=instance,
            transitions=(second,),
        )


def test_duplicate_sequence_rejects() -> None:
    instance, first, _ = chain()

    payload = first.to_dict()
    payload["transition_id"] = "duplicate-sequence-id"
    payload["fingerprint"] = ""

    duplicate = LegalMatterWorkflowTransition.from_dict(
        payload
    )

    with pytest.raises(
        LegalMatterWorkflowCurrentnessError,
        match="G7G_R11_SEQUENCE_DUPLICATE",
    ):
        LegalMatterWorkflowCurrentness.derive(
            currentness_id="bad",
            workflow_instance=instance,
            transitions=(first, duplicate),
        )


def test_broken_previous_fingerprint_rejects() -> None:
    instance, first, second = chain()

    payload = second.to_dict()
    payload["previous_transition_fingerprint"] = (
        "f" * 128
    )
    payload["fingerprint"] = ""

    broken = LegalMatterWorkflowTransition.from_dict(
        payload
    )

    with pytest.raises(
        LegalMatterWorkflowCurrentnessError,
        match="G7G_R11_FINGERPRINT_CHAIN_INVALID",
    ):
        LegalMatterWorkflowCurrentness.derive(
            currentness_id="bad",
            workflow_instance=instance,
            transitions=(first, broken),
        )


def test_stage_discontinuity_rejects() -> None:
    instance, first, second = chain()

    payload = second.to_dict()
    payload["source_stage_definition_id"] = "wrong-source"
    payload["fingerprint"] = ""

    broken = LegalMatterWorkflowTransition.from_dict(
        payload
    )

    with pytest.raises(
        LegalMatterWorkflowCurrentnessError,
        match="G7G_R11_STAGE_CONTINUITY_INVALID",
    ):
        LegalMatterWorkflowCurrentness.derive(
            currentness_id="bad",
            workflow_instance=instance,
            transitions=(first, broken),
        )


def test_chronology_reversal_rejects() -> None:
    instance, first, second = chain()

    payload = second.to_dict()
    payload["transitioned_at"] = (
        first.transitioned_at.isoformat()
    )
    payload["fingerprint"] = ""

    broken = LegalMatterWorkflowTransition.from_dict(
        payload
    )

    with pytest.raises(
        LegalMatterWorkflowCurrentnessError,
        match="G7G_R11_CHRONOLOGY_INVALID",
    ):
        LegalMatterWorkflowCurrentness.derive(
            currentness_id="bad",
            workflow_instance=instance,
            transitions=(first, broken),
        )


def test_mixed_instance_scope_rejects() -> None:
    instance, first, second = chain()

    payload = second.to_dict()
    payload["workflow_instance_id"] = "other-instance"
    payload["fingerprint"] = ""

    mixed = LegalMatterWorkflowTransition.from_dict(
        payload
    )

    with pytest.raises(
        LegalMatterWorkflowCurrentnessError,
        match="G7G_R11_TRANSITION_SCOPE_MISMATCH",
    ):
        LegalMatterWorkflowCurrentness.derive(
            currentness_id="bad",
            workflow_instance=instance,
            transitions=(first, mixed),
        )


def test_round_trip_preserves_exact_truth() -> None:
    instance, first, second = chain()

    original = LegalMatterWorkflowCurrentness.derive(
        currentness_id="current",
        workflow_instance=instance,
        transitions=(first, second),
    )

    restored = LegalMatterWorkflowCurrentness.from_dict(
        original.to_dict()
    )

    assert restored == original


def test_corrupt_fingerprint_rejects() -> None:
    instance, first, second = chain()

    value = LegalMatterWorkflowCurrentness.derive(
        currentness_id="current",
        workflow_instance=instance,
        transitions=(first, second),
    )

    payload = value.to_dict()
    payload["fingerprint"] = "f" * 128

    with pytest.raises(
        LegalMatterWorkflowCurrentnessError,
        match="G7G_R11_FINGERPRINT_MISMATCH",
    ):
        LegalMatterWorkflowCurrentness.from_dict(
            payload
        )


def test_currentness_contains_no_progression_or_iam_authority() -> None:
    instance, first, second = chain()

    keys = set(
        LegalMatterWorkflowCurrentness.derive(
            currentness_id="current",
            workflow_instance=instance,
            transitions=(first, second),
        ).to_dict()
    )

    forbidden = {
        "target_stage_definition_id",
        "transition_authorization_evidence_reference",
        "permission",
        "authorization_role",
        "work_item_id",
        "assignee_principal_id",
        "supervisor_principal_id",
        "legal_event_id",
    }

    assert not keys & forbidden


def test_no_commercial_or_financial_authority() -> None:
    instance, first, second = chain()

    keys = set(
        LegalMatterWorkflowCurrentness.derive(
            currentness_id="current",
            workflow_instance=instance,
            transitions=(first, second),
        ).to_dict()
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


# ARTIFACT: test_legal_matter_workflow_currentness.py
# VERSION: v1.0.1-G7G-R11-LEGAL-MATTER-WORKFLOW-CURRENTNESS-CERT
