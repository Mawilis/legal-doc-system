"""Direct certificate for G7G-R4 Legal Workflow Topology."""
from __future__ import annotations

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
    SCHEMA,
    VERSION,
    LegalWorkflowTopology,
    LegalWorkflowTopologyError,
)


def definition() -> LegalWorkflowDefinition:
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
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )


def stage(
    workflow_definition: LegalWorkflowDefinition,
    *,
    stage_definition_id: str,
    is_entry_stage: bool,
    is_terminal_stage: bool,
    successor_stage_ids: tuple[str, ...],
) -> LegalWorkflowStage:
    return LegalWorkflowStage.from_workflow_definition(
        workflow_definition=
            workflow_definition,
        stage_definition_id=
            stage_definition_id,
        name=
            stage_definition_id,
        description_reference=
            f"description:{stage_definition_id}",
        is_entry_stage=
            is_entry_stage,
        is_terminal_stage=
            is_terminal_stage,
        successor_stage_ids=
            successor_stage_ids,
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )


def linear_topology() -> LegalWorkflowTopology:
    value = definition()

    stages = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=False,
            successor_stage_ids=("s3",),
        ),
        stage(
            value,
            stage_definition_id="s3",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    return (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=stages,
        )
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.1-G7G-R4-LEGAL-WORKFLOW-TOPOLOGY"
    )
    assert (
        SCHEMA
        == "WILSY-LEGAL-WORKFLOW-TOPOLOGY/V1"
    )


def test_linear_topology_is_certified() -> None:
    topology = linear_topology()

    assert (
        topology.entry_stage_definition_id
        == "s1"
    )

    assert (
        topology.terminal_stage_definition_ids
        == ("s3",)
    )

    assert len(topology.fingerprint) == 128


def test_branching_topology_is_supported() -> None:
    value = definition()

    stages = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=(
                "s2",
                "s3",
            ),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=False,
            successor_stage_ids=("s4",),
        ),
        stage(
            value,
            stage_definition_id="s3",
            is_entry_stage=False,
            is_terminal_stage=False,
            successor_stage_ids=("s4",),
        ),
        stage(
            value,
            stage_definition_id="s4",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    topology = (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=stages,
        )
    )

    assert topology.entry_stage_definition_id == "s1"
    assert (
        topology.terminal_stage_definition_ids
        == ("s4",)
    )


def test_multiple_terminal_paths_are_supported() -> None:
    value = definition()

    stages = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s2", "s3"),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
        stage(
            value,
            stage_definition_id="s3",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    topology = (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=stages,
        )
    )

    assert (
        topology.terminal_stage_definition_ids
        == ("s2", "s3")
    )


def test_exactly_one_entry_is_required() -> None:
    value = definition()

    no_entry = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=False,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    with pytest.raises(
        LegalWorkflowTopologyError,
        match="G7G_R4_EXACTLY_ONE_ENTRY_REQUIRED",
    ):
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=no_entry,
        )

    two_entries = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s3",),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s3",),
        ),
        stage(
            value,
            stage_definition_id="s3",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    with pytest.raises(
        LegalWorkflowTopologyError,
        match="G7G_R4_EXACTLY_ONE_ENTRY_REQUIRED",
    ):
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=two_entries,
        )


def test_terminal_stage_is_required() -> None:
    value = definition()

    stages = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=False,
            successor_stage_ids=("s1",),
        ),
    )

    with pytest.raises(
        LegalWorkflowTopologyError,
        match="G7G_R4_TERMINAL_STAGE_REQUIRED",
    ):
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=stages,
        )


def test_dangling_successor_rejects() -> None:
    value = definition()

    stages = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("missing",),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    with pytest.raises(
        LegalWorkflowTopologyError,
        match="G7G_R4_DANGLING_SUCCESSOR",
    ):
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=stages,
        )


def test_orphan_stage_rejects() -> None:
    value = definition()

    stages = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
        stage(
            value,
            stage_definition_id="orphan",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    with pytest.raises(
        LegalWorkflowTopologyError,
        match="G7G_R4_ORPHAN_STAGE",
    ):
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=stages,
        )


def test_cycle_with_terminal_escape_is_supported() -> None:
    value = definition()

    stages = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=False,
            successor_stage_ids=("s3",),
        ),
        stage(
            value,
            stage_definition_id="s3",
            is_entry_stage=False,
            is_terminal_stage=False,
            successor_stage_ids=(
                "s2",
                "s4",
            ),
        ),
        stage(
            value,
            stage_definition_id="s4",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    topology = (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=stages,
        )
    )

    assert topology.entry_stage_definition_id == "s1"


def test_non_terminating_reachable_region_rejects() -> None:
    value = definition()

    stages = (
        stage(
            value,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=(
                "s2",
                "s4",
            ),
        ),
        stage(
            value,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=False,
            successor_stage_ids=("s3",),
        ),
        stage(
            value,
            stage_definition_id="s3",
            is_entry_stage=False,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
        ),
        stage(
            value,
            stage_definition_id="s4",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    with pytest.raises(
        LegalWorkflowTopologyError,
        match="G7G_R4_NON_TERMINATING_STAGE_REGION",
    ):
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=stages,
        )


def test_stage_definition_binding_mismatch_rejects() -> None:
    canonical = definition()

    other = LegalWorkflowDefinition(
        workflow_definition_id="other-workflow",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Other",
        description_reference="other-description",
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    mixed = (
        stage(
            canonical,
            stage_definition_id="s1",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
        ),
        stage(
            other,
            stage_definition_id="s2",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
        ),
    )

    with pytest.raises(
        LegalWorkflowTopologyError,
        match=(
            "G7G_R4_STAGE_DEFINITION_BINDING_MISMATCH"
        ),
    ):
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=canonical,
            stages=mixed,
        )


def test_round_trip_preserves_exact_truth() -> None:
    original = linear_topology()

    restored = LegalWorkflowTopology.from_dict(
        original.to_dict()
    )

    assert restored == original


def test_stage_order_does_not_change_topology_fingerprint() -> None:
    value = definition()

    s1 = stage(
        value,
        stage_definition_id="s1",
        is_entry_stage=True,
        is_terminal_stage=False,
        successor_stage_ids=("s2",),
    )

    s2 = stage(
        value,
        stage_definition_id="s2",
        is_entry_stage=False,
        is_terminal_stage=True,
        successor_stage_ids=(),
    )

    first = (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=(s1, s2),
        )
    )

    second = (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=value,
            stages=(s2, s1),
        )
    )

    assert first.fingerprint == second.fingerprint
    assert first == second


def test_corrupt_topology_fingerprint_rejects() -> None:
    payload = linear_topology().to_dict()
    payload["fingerprint"] = "a" * 128

    with pytest.raises(
        LegalWorkflowTopologyError,
        match="G7G_R4_FINGERPRINT_MISMATCH",
    ):
        LegalWorkflowTopology.from_dict(
            payload
        )


def test_no_runtime_iam_or_financial_authority() -> None:
    keys = set(
        linear_topology().to_dict()
    )

    forbidden = {
        "workflow_instance_id",
        "current_stage_id",
        "principal_id",
        "assignee_principal_id",
        "supervisor_principal_id",
        "permission",
        "authorization_role",
        "plan_id",
        "subscription_id",
        "entitlement_id",
        "invoice_id",
        "payment_id",
        "financial_execution",
    }

    assert not keys & forbidden


# ARTIFACT: test_legal_workflow_topology.py
# VERSION: v1.0.1-G7G-R4-LEGAL-WORKFLOW-TOPOLOGY-CERT
