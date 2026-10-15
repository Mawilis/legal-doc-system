"""Direct certificate for G7G-R10 Legal Matter Workflow Transition."""
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
from tools.eos.legal_operations.domain.legal_workflow_gate_satisfaction import (
    LegalWorkflowGateEvidence,
    LegalWorkflowGateSatisfaction,
)
from tools.eos.legal_operations.domain.legal_matter_workflow_transition import (
    SCHEMA,
    VERSION,
    LegalMatterWorkflowTransition,
    LegalMatterWorkflowTransitionError,
)


AT = datetime(
    2026,
    10,
    13,
    1,
    20,
    0,
    123456,
    tzinfo=timezone.utc,
)


def context(
    *,
    branching: bool = False,
    with_gate: bool = True,
) -> tuple[
    LegalMatterWorkflowInstance,
    LegalWorkflowTopology,
    LegalWorkflowStage,
    LegalWorkflowStage,
    LegalWorkflowStage | None,
    tuple[LegalWorkflowGateSatisfaction, ...],
]:
    model = TenantLegalOperatingModel(
        tenant_id="tenant-1",
        operating_model_id="model-1",
        revision=1,
        activated_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        effective_from=AT,
        supersedes_operating_model_id=None,
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    definition = LegalWorkflowDefinition(
        workflow_definition_id="workflow-1",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Workflow",
        description_reference="workflow-desc",
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    successors = (
        ("s2", "s3")
        if branching
        else ("s2",)
    )

    gates = (
        ("gate:source-complete",)
        if with_gate
        else ()
    )

    source = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=definition,
        stage_definition_id="s1",
        name="Source",
        description_reference="source-desc",
        is_entry_stage=True,
        is_terminal_stage=False,
        successor_stage_ids=successors,
        work_requirement_references=(),
        completion_gate_references=gates,
        automation_references=(),
    )

    target = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=definition,
        stage_definition_id="s2",
        name="Target",
        description_reference="target-desc",
        is_entry_stage=False,
        is_terminal_stage=True,
        successor_stage_ids=(),
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )

    alternate = None

    stages: tuple[LegalWorkflowStage, ...]

    if branching:
        alternate = (
            LegalWorkflowStage.from_workflow_definition(
                workflow_definition=definition,
                stage_definition_id="s3",
                name="Alternate",
                description_reference="alternate-desc",
                is_entry_stage=False,
                is_terminal_stage=True,
                successor_stage_ids=(),
                work_requirement_references=(),
                completion_gate_references=(),
                automation_references=(),
            )
        )

        stages = (
            source,
            target,
            alternate,
        )
    else:
        stages = (
            source,
            target,
        )

    topology = (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=definition,
            stages=stages,
        )
    )

    activation = (
        TenantLegalWorkflowActivation.from_authorities(
            activation_id="activation-1",
            activation_revision=1,
            operating_model=model,
            workflow_definition=definition,
            workflow_topology=topology,
            commercial_eligibility_evidence_reference=
                "commercial-proof",
            activation_reason_reference=
                "activation-reason",
            effective_from=AT,
        )
    )

    instance = (
        LegalMatterWorkflowInstance.from_authorities(
            workflow_instance_id="instance-1",
            case_matter_id="matter-1",
            activation=activation,
            workflow_definition=definition,
            workflow_topology=topology,
            started_at=AT,
            started_by_principal_id="principal-1",
            start_authorization_evidence_reference=
                "start-auth",
        )
    )

    satisfactions: tuple[
        LegalWorkflowGateSatisfaction,
        ...
    ] = ()

    if with_gate:
        evidence = LegalWorkflowGateEvidence(
            evidence_kind="CANONICAL_FACT",
            evidence_reference="canonical:1",
            evidence_fingerprint="a" * 128,
        )

        satisfaction = (
            LegalWorkflowGateSatisfaction.from_authorities(
                gate_satisfaction_id="gate-sat-1",
                workflow_instance=instance,
                workflow_topology=topology,
                source_stage=source,
                gate_reference="gate:source-complete",
                canonical_evidence=(evidence,),
                evaluated_at=AT,
                evaluated_by_principal_id="principal-2",
                evaluation_authorization_evidence_reference=
                    "gate-auth",
            )
        )

        satisfactions = (
            satisfaction,
        )

    return (
        instance,
        topology,
        source,
        target,
        alternate,
        satisfactions,
    )


def transition(
    *,
    branching: bool = False,
    with_gate: bool = True,
    branch_reference: str | None = None,
) -> LegalMatterWorkflowTransition:
    (
        instance,
        topology,
        source,
        target,
        _,
        satisfactions,
    ) = context(
        branching=branching,
        with_gate=with_gate,
    )

    return LegalMatterWorkflowTransition.from_authorities(
        transition_id="transition-1",
        workflow_instance=instance,
        workflow_topology=topology,
        source_stage=source,
        target_stage=target,
        gate_satisfactions=satisfactions,
        transitioned_at=AT + timedelta(minutes=1),
        transitioned_by_principal_id="principal-3",
        transition_authorization_evidence_reference=
            "transition-auth",
        branch_selection_evidence_reference=
            branch_reference,
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.1-G7G-R10-LEGAL-MATTER-WORKFLOW-TRANSITION"
    )

    assert (
        SCHEMA
        == "WILSY-LEGAL-MATTER-WORKFLOW-TRANSITION/V1"
    )


def test_first_transition_is_exactly_chained_from_instance_entry() -> None:
    value = transition()

    assert value.sequence_number == 1
    assert (
        value.previous_transition_fingerprint
        is None
    )
    assert (
        value.source_stage_definition_id
        == "s1"
    )
    assert (
        value.target_stage_definition_id
        == "s2"
    )


def test_configured_gate_must_have_exact_satisfaction() -> None:
    (
        instance,
        topology,
        source,
        target,
        _,
        _,
    ) = context(
        with_gate=True,
    )

    with pytest.raises(
        LegalMatterWorkflowTransitionError,
        match="G7G_R10_GATE_SATISFACTION_SET_MISMATCH",
    ):
        LegalMatterWorkflowTransition.from_authorities(
            transition_id="x",
            workflow_instance=instance,
            workflow_topology=topology,
            source_stage=source,
            target_stage=target,
            gate_satisfactions=(),
            transitioned_at=AT + timedelta(minutes=1),
            transitioned_by_principal_id="p",
            transition_authorization_evidence_reference="auth",
        )


def test_gate_free_stage_accepts_no_satisfaction() -> None:
    value = transition(
        with_gate=False,
    )

    assert value.gate_bindings == ()


def test_target_must_be_certified_successor() -> None:
    (
        instance,
        topology,
        source,
        target,
        alternate,
        satisfactions,
    ) = context(
        branching=False,
        with_gate=True,
    )

    assert alternate is None

    bad_definition = LegalWorkflowDefinition(
        workflow_definition_id="other",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Other",
        description_reference="other",
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    outside = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=bad_definition,
        stage_definition_id="outside",
        name="Outside",
        description_reference="outside",
        is_entry_stage=True,
        is_terminal_stage=True,
        successor_stage_ids=(),
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )

    with pytest.raises(
        LegalMatterWorkflowTransitionError,
        match="G7G_R10_TARGET_STAGE_NOT_IN_TOPOLOGY",
    ):
        LegalMatterWorkflowTransition.from_authorities(
            transition_id="x",
            workflow_instance=instance,
            workflow_topology=topology,
            source_stage=source,
            target_stage=outside,
            gate_satisfactions=satisfactions,
            transitioned_at=AT + timedelta(minutes=1),
            transitioned_by_principal_id="p",
            transition_authorization_evidence_reference="auth",
        )

    assert target.stage_definition_id == "s2"


def test_branch_evidence_required_only_for_multi_successor_source() -> None:
    with pytest.raises(
        LegalMatterWorkflowTransitionError,
        match="G7G_R10_BRANCH_SELECTION_EVIDENCE_REQUIRED",
    ):
        transition(
            branching=True,
            branch_reference=None,
        )

    value = transition(
        branching=True,
        branch_reference="branch-decision:1",
    )

    assert (
        value.branch_selection_evidence_reference
        == "branch-decision:1"
    )

    with pytest.raises(
        LegalMatterWorkflowTransitionError,
        match="G7G_R10_BRANCH_SELECTION_EVIDENCE_FORBIDDEN",
    ):
        transition(
            branching=False,
            branch_reference="decorative-branch",
        )


def test_later_transition_chains_sequence_and_previous_fingerprint() -> None:
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
        workflow_definition_id="wf-chain",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Chain",
        description_reference="chain",
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
        activation_id="activation-chain",
        activation_revision=1,
        operating_model=model,
        workflow_definition=definition,
        workflow_topology=topology,
        commercial_eligibility_evidence_reference="commercial",
        activation_reason_reference="reason",
        effective_from=AT,
    )

    instance = LegalMatterWorkflowInstance.from_authorities(
        workflow_instance_id="instance-chain",
        case_matter_id="matter-1",
        activation=activation,
        workflow_definition=definition,
        workflow_topology=topology,
        started_at=AT,
        started_by_principal_id="p1",
        start_authorization_evidence_reference="auth-start",
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

    assert second.sequence_number == 2
    assert (
        second.previous_transition_fingerprint
        == first.fingerprint
    )
    assert (
        second.source_stage_definition_id
        == first.target_stage_definition_id
        == "s2"
    )


def test_later_transition_rejects_wrong_previous_target() -> None:
    (
        instance,
        topology,
        source,
        target,
        _,
        satisfactions,
    ) = context()

    first = LegalMatterWorkflowTransition.from_authorities(
        transition_id="t1",
        workflow_instance=instance,
        workflow_topology=topology,
        source_stage=source,
        target_stage=target,
        gate_satisfactions=satisfactions,
        transitioned_at=AT + timedelta(minutes=1),
        transitioned_by_principal_id="p",
        transition_authorization_evidence_reference="auth",
    )

    with pytest.raises(
        LegalMatterWorkflowTransitionError,
        match="G7G_R10_PREVIOUS_TARGET_SOURCE_MISMATCH",
    ):
        LegalMatterWorkflowTransition.from_authorities(
            transition_id="t2",
            workflow_instance=instance,
            workflow_topology=topology,
            source_stage=source,
            target_stage=target,
            gate_satisfactions=satisfactions,
            transitioned_at=AT + timedelta(minutes=2),
            transitioned_by_principal_id="p",
            transition_authorization_evidence_reference="auth",
            previous_transition=first,
        )


def test_gate_binding_order_is_deterministic() -> None:
    value = transition()
    restored = LegalMatterWorkflowTransition.from_dict(
        value.to_dict()
    )

    assert restored == value


def test_transition_actor_and_auth_are_audit_only() -> None:
    payload = transition().to_dict()

    assert (
        payload["transitioned_by_principal_id"]
        == "principal-3"
    )
    assert (
        payload[
            "transition_authorization_evidence_reference"
        ]
        == "transition-auth"
    )

    assert "permission" not in payload
    assert "authorization_role" not in payload


def test_no_currentness_work_assignment_supervision_or_legal_event_authority() -> None:
    keys = set(
        transition().to_dict()
    )

    forbidden = {
        "current_stage_definition_id",
        "is_current",
        "workflow_status",
        "work_item_id",
        "assignee_principal_id",
        "supervisor_principal_id",
        "legal_event_id",
        "matter_status",
        "matter_state",
    }

    assert not keys & forbidden


def test_no_commercial_or_financial_authority() -> None:
    keys = set(
        transition().to_dict()
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


def test_corrupt_fingerprint_rejects() -> None:
    payload = transition().to_dict()
    payload["fingerprint"] = "f" * 128

    with pytest.raises(
        LegalMatterWorkflowTransitionError,
        match="G7G_R10_FINGERPRINT_MISMATCH",
    ):
        LegalMatterWorkflowTransition.from_dict(
            payload
        )


def test_extra_or_missing_field_rejects() -> None:
    payload = transition().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        LegalMatterWorkflowTransitionError,
        match="G7G_R10_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalMatterWorkflowTransition.from_dict(
            payload
        )

    payload = transition().to_dict()
    del payload["sequence_number"]

    with pytest.raises(
        LegalMatterWorkflowTransitionError,
        match="G7G_R10_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalMatterWorkflowTransition.from_dict(
            payload
        )


# ARTIFACT: test_legal_matter_workflow_transition.py
# VERSION: v1.0.1-G7G-R10-LEGAL-MATTER-WORKFLOW-TRANSITION-CERT
