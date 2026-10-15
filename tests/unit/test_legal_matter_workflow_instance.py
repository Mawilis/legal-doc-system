"""Direct certificate for G7G-R6 Legal Matter Workflow Instance."""
from __future__ import annotations

from datetime import datetime, timezone

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
    SCHEMA,
    VERSION,
    LegalMatterWorkflowInstance,
    LegalMatterWorkflowInstanceError,
)


AT = datetime(
    2026,
    10,
    13,
    0,
    50,
    0,
    123456,
    tzinfo=timezone.utc,
)


def authorities() -> tuple[
    TenantLegalWorkflowActivation,
    LegalWorkflowDefinition,
    LegalWorkflowTopology,
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
        workflow_definition_id=
            "workflow-litigation-core",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Litigation Core",
        description_reference="workflow-description",
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    s1 = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=definition,
        stage_definition_id="s1",
        name="Intake",
        description_reference="stage-intake",
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
        name="Close",
        description_reference="stage-close",
        is_entry_stage=False,
        is_terminal_stage=True,
        successor_stage_ids=(),
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )

    topology = (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=definition,
            stages=(s1, s2),
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
                "tenant-selected-workflow",
            effective_from=AT,
        )
    )

    return activation, definition, topology


def instance() -> LegalMatterWorkflowInstance:
    activation, definition, topology = authorities()

    return LegalMatterWorkflowInstance.from_authorities(
        workflow_instance_id="instance-1",
        case_matter_id="matter-1",
        activation=activation,
        workflow_definition=definition,
        workflow_topology=topology,
        started_at=AT,
        started_by_principal_id="principal-1",
        start_authorization_evidence_reference=
            "auth-evidence-1",
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.1-G7G-R6-LEGAL-MATTER-WORKFLOW-INSTANCE"
    )

    assert (
        SCHEMA
        == "WILSY-LEGAL-MATTER-WORKFLOW-INSTANCE/V1"
    )


def test_instance_binds_exact_tenant_and_matter() -> None:
    value = instance()

    assert value.tenant_id == "tenant-1"
    assert value.case_matter_id == "matter-1"
    assert value.workflow_instance_id == "instance-1"


def test_instance_binds_exact_activation_definition_and_topology() -> None:
    activation, definition, topology = authorities()
    value = instance()

    assert value.activation_id == activation.activation_id

    assert (
        value.activation_fingerprint
        == activation.fingerprint
    )

    assert (
        value.workflow_definition_fingerprint
        == definition.fingerprint
    )

    assert (
        value.workflow_topology_fingerprint
        == topology.fingerprint
    )


def test_entry_stage_is_derived_from_certified_topology() -> None:
    _, _, topology = authorities()
    value = instance()

    assert (
        value.entry_stage_definition_id
        == topology.entry_stage_definition_id
        == "s1"
    )


def test_microseconds_are_preserved() -> None:
    assert instance().started_at.microsecond == 123456


def test_start_actor_is_audit_not_authority() -> None:
    payload = instance().to_dict()

    assert (
        payload["started_by_principal_id"]
        == "principal-1"
    )

    assert (
        payload[
            "start_authorization_evidence_reference"
        ]
        == "auth-evidence-1"
    )

    assert "permission" not in payload
    assert "permissions" not in payload
    assert "authorization_role" not in payload


def test_no_current_stage_or_progression_authority() -> None:
    keys = set(
        instance().to_dict()
    )

    forbidden = {
        "current_stage_id",
        "current_stage_definition_id",
        "stage_status",
        "workflow_status",
        "status",
        "completed_at",
        "is_complete",
        "next_stage_id",
        "transition_id",
    }

    assert not keys & forbidden


def test_no_work_assignment_supervision_or_legal_event_authority() -> None:
    keys = set(
        instance().to_dict()
    )

    forbidden = {
        "work_item_id",
        "assignee_principal_id",
        "supervisor_principal_id",
        "supervisee_principal_id",
        "legal_event_id",
        "matter_status",
        "matter_state",
    }

    assert not keys & forbidden


def test_no_commercial_or_financial_authority() -> None:
    keys = set(
        instance().to_dict()
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


@pytest.mark.parametrize(
    "tenant",
    (
        "default",
        "global",
        "root",
        "*",
    ),
)
def test_pseudo_tenants_reject_direct_hydration(
    tenant: str,
) -> None:
    payload = instance().to_dict()
    payload["tenant_id"] = tenant
    payload["fingerprint"] = ""

    with pytest.raises(
        LegalMatterWorkflowInstanceError,
        match="G7G_R6_TENANT_REQUIRED",
    ):
        LegalMatterWorkflowInstance.from_dict(
            payload
        )


def test_round_trip_preserves_exact_truth() -> None:
    original = instance()

    restored = LegalMatterWorkflowInstance.from_dict(
        original.to_dict()
    )

    assert restored == original


def test_corrupt_fingerprint_rejects() -> None:
    payload = instance().to_dict()
    payload["fingerprint"] = "a" * 128

    with pytest.raises(
        LegalMatterWorkflowInstanceError,
        match="G7G_R6_FINGERPRINT_MISMATCH",
    ):
        LegalMatterWorkflowInstance.from_dict(
            payload
        )


def test_extra_or_missing_field_rejects() -> None:
    payload = instance().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        LegalMatterWorkflowInstanceError,
        match="G7G_R6_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalMatterWorkflowInstance.from_dict(
            payload
        )

    payload = instance().to_dict()
    del payload["entry_stage_definition_id"]

    with pytest.raises(
        LegalMatterWorkflowInstanceError,
        match="G7G_R6_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalMatterWorkflowInstance.from_dict(
            payload
        )


# ARTIFACT: test_legal_matter_workflow_instance.py
# VERSION: v1.0.1-G7G-R6-LEGAL-MATTER-WORKFLOW-INSTANCE-CERT
