"""Direct certificate for G7G-R9 Legal Workflow Gate Satisfaction."""
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
    LegalMatterWorkflowInstance,
)
from tools.eos.legal_operations.domain.legal_workflow_gate_satisfaction import (
    SCHEMA,
    VERSION,
    LegalWorkflowGateEvidence,
    LegalWorkflowGateSatisfaction,
    LegalWorkflowGateSatisfactionError,
)


AT = datetime(
    2026,
    10,
    13,
    1,
    5,
    0,
    123456,
    tzinfo=timezone.utc,
)


def authorities() -> tuple[
    LegalMatterWorkflowInstance,
    LegalWorkflowTopology,
    LegalWorkflowStage,
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
        description_reference=
            "workflow-description",
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    source_stage = (
        LegalWorkflowStage.from_workflow_definition(
            workflow_definition=definition,
            stage_definition_id="s1",
            name="Conflict Review",
            description_reference=
                "stage-conflict",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
            work_requirement_references=(),
            completion_gate_references=(
                "gate:conflict-current",
            ),
            automation_references=(),
        )
    )

    terminal_stage = (
        LegalWorkflowStage.from_workflow_definition(
            workflow_definition=definition,
            stage_definition_id="s2",
            name="Engagement",
            description_reference=
                "stage-engagement",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
            work_requirement_references=(),
            completion_gate_references=(),
            automation_references=(),
        )
    )

    topology = (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=definition,
            stages=(
                source_stage,
                terminal_stage,
            ),
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

    instance = (
        LegalMatterWorkflowInstance.from_authorities(
            workflow_instance_id=
                "instance-1",
            case_matter_id=
                "matter-1",
            activation=
                activation,
            workflow_definition=
                definition,
            workflow_topology=
                topology,
            started_at=
                AT,
            started_by_principal_id=
                "principal-1",
            start_authorization_evidence_reference=
                "start-auth-proof",
        )
    )

    return (
        instance,
        topology,
        source_stage,
    )


def evidence(
    *,
    kind: str = "LEGAL_CONFLICT_DISPOSITION_CURRENTNESS",
    reference: str = "conflict-currentness:1",
    fingerprint: str = "a" * 128,
) -> LegalWorkflowGateEvidence:
    return LegalWorkflowGateEvidence(
        evidence_kind=kind,
        evidence_reference=reference,
        evidence_fingerprint=fingerprint,
    )


def satisfaction(
    *,
    canonical_evidence: tuple[
        LegalWorkflowGateEvidence,
        ...
    ] | None = None,
) -> LegalWorkflowGateSatisfaction:
    instance, topology, stage = authorities()

    actual_evidence = (
        canonical_evidence
        if canonical_evidence is not None
        else (evidence(),)
    )

    return (
        LegalWorkflowGateSatisfaction.from_authorities(
            gate_satisfaction_id=
                "gate-satisfaction-1",
            workflow_instance=
                instance,
            workflow_topology=
                topology,
            source_stage=
                stage,
            gate_reference=
                "gate:conflict-current",
            canonical_evidence=
                actual_evidence,
            evaluated_at=
                AT,
            evaluated_by_principal_id=
                "principal-2",
            evaluation_authorization_evidence_reference=
                "gate-eval-auth-proof",
        )
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.1-G7G-R9-LEGAL-WORKFLOW-GATE-SATISFACTION"
    )
    assert (
        SCHEMA
        == "WILSY-LEGAL-WORKFLOW-GATE-SATISFACTION/V1"
    )


def test_positive_gate_satisfaction_is_exact() -> None:
    value = satisfaction()

    assert value.tenant_id == "tenant-1"
    assert value.case_matter_id == "matter-1"
    assert (
        value.gate_reference
        == "gate:conflict-current"
    )
    assert len(value.fingerprint) == 128


def test_stage_and_instance_bindings_are_exact() -> None:
    instance, topology, stage = authorities()
    value = satisfaction()

    assert (
        value.workflow_instance_id
        == instance.workflow_instance_id
    )
    assert (
        value.workflow_instance_fingerprint
        == instance.fingerprint
    )
    assert (
        value.workflow_topology_fingerprint
        == topology.fingerprint
    )
    assert (
        value.source_stage_definition_id
        == stage.stage_definition_id
    )
    assert (
        value.source_stage_fingerprint
        == stage.fingerprint
    )


def test_gate_must_be_configured_on_source_stage() -> None:
    instance, topology, stage = authorities()

    with pytest.raises(
        LegalWorkflowGateSatisfactionError,
        match="G7G_R9_GATE_NOT_CONFIGURED_ON_STAGE",
    ):
        LegalWorkflowGateSatisfaction.from_authorities(
            gate_satisfaction_id="x",
            workflow_instance=instance,
            workflow_topology=topology,
            source_stage=stage,
            gate_reference="gate:not-configured",
            canonical_evidence=(evidence(),),
            evaluated_at=AT,
            evaluated_by_principal_id="p1",
            evaluation_authorization_evidence_reference=
                "auth-proof",
        )


def test_canonical_evidence_is_required() -> None:
    with pytest.raises(
        LegalWorkflowGateSatisfactionError,
        match="G7G_R9_CANONICAL_EVIDENCE_REQUIRED",
    ):
        satisfaction(
            canonical_evidence=(),
        )


def test_multiple_canonical_evidence_bindings_are_supported() -> None:
    first = evidence(
        kind="LEGAL_CONFLICT_REVIEW_DETERMINATION",
        reference="conflict-review:1",
        fingerprint="b" * 128,
    )

    second = evidence(
        kind="LEGAL_CONFLICT_DISPOSITION_CURRENTNESS",
        reference="conflict-currentness:1",
        fingerprint="a" * 128,
    )

    value = satisfaction(
        canonical_evidence=(
            second,
            first,
        ),
    )

    assert tuple(
        item.evidence_kind
        for item in value.canonical_evidence
    ) == (
        "LEGAL_CONFLICT_DISPOSITION_CURRENTNESS",
        "LEGAL_CONFLICT_REVIEW_DETERMINATION",
    )


def test_evidence_order_does_not_change_fingerprint() -> None:
    first = evidence(
        kind="A",
        reference="ref-a",
        fingerprint="a" * 128,
    )
    second = evidence(
        kind="B",
        reference="ref-b",
        fingerprint="b" * 128,
    )

    one = satisfaction(
        canonical_evidence=(
            first,
            second,
        ),
    )
    two = satisfaction(
        canonical_evidence=(
            second,
            first,
        ),
    )

    assert one == two
    assert one.fingerprint == two.fingerprint


def test_duplicate_evidence_rejects() -> None:
    value = evidence()

    with pytest.raises(
        LegalWorkflowGateSatisfactionError,
        match=(
            "G7G_R9_CANONICAL_EVIDENCE_DUPLICATE"
        ),
    ):
        satisfaction(
            canonical_evidence=(
                value,
                value,
            ),
        )


def test_invalid_evidence_fingerprint_rejects() -> None:
    with pytest.raises(
        LegalWorkflowGateSatisfactionError,
        match=(
            "G7G_R9_EVIDENCE_FINGERPRINT_INVALID"
        ),
    ):
        evidence(
            fingerprint="bad",
        )


def test_microseconds_are_preserved() -> None:
    assert (
        satisfaction().evaluated_at.microsecond
        == 123456
    )


def test_actor_and_auth_reference_are_audit_only() -> None:
    payload = satisfaction().to_dict()

    assert (
        payload["evaluated_by_principal_id"]
        == "principal-2"
    )
    assert (
        payload[
            "evaluation_authorization_evidence_reference"
        ]
        == "gate-eval-auth-proof"
    )

    assert "permission" not in payload
    assert "permissions" not in payload
    assert "authorization_role" not in payload


def test_no_unsatisfied_status_transition_or_currentness_authority() -> None:
    keys = set(
        satisfaction().to_dict()
    )

    forbidden = {
        "satisfied",
        "is_satisfied",
        "status",
        "transition_id",
        "target_stage_definition_id",
        "current_stage_definition_id",
        "workflow_status",
        "is_current",
    }

    assert not keys & forbidden


def test_no_work_generation_assignment_supervision_or_legal_event_authority() -> None:
    keys = set(
        satisfaction().to_dict()
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
        satisfaction().to_dict()
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
    original = satisfaction()

    restored = (
        LegalWorkflowGateSatisfaction.from_dict(
            original.to_dict()
        )
    )

    assert restored == original


def test_corrupt_fingerprint_rejects() -> None:
    payload = satisfaction().to_dict()
    payload["fingerprint"] = "f" * 128

    with pytest.raises(
        LegalWorkflowGateSatisfactionError,
        match="G7G_R9_FINGERPRINT_MISMATCH",
    ):
        LegalWorkflowGateSatisfaction.from_dict(
            payload
        )


def test_extra_or_missing_field_rejects() -> None:
    payload = satisfaction().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        LegalWorkflowGateSatisfactionError,
        match="G7G_R9_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkflowGateSatisfaction.from_dict(
            payload
        )

    payload = satisfaction().to_dict()
    del payload["gate_reference"]

    with pytest.raises(
        LegalWorkflowGateSatisfactionError,
        match="G7G_R9_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkflowGateSatisfaction.from_dict(
            payload
        )


# ARTIFACT: test_legal_workflow_gate_satisfaction.py
# VERSION: v1.0.1-G7G-R9-LEGAL-WORKFLOW-GATE-SATISFACTION-CERT
