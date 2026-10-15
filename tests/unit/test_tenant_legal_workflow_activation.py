"""Direct certificate for G7G-R5 Tenant Legal Workflow Activation."""
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
    SCHEMA,
    VERSION,
    TenantLegalWorkflowActivation,
    TenantLegalWorkflowActivationError,
)


AT = datetime(
    2026,
    10,
    12,
    22,
    45,
    0,
    123456,
    tzinfo=timezone.utc,
)


def operating_model(
    *,
    tenant_id: str = "tenant-1",
    operating_model_id: str = "model-1",
    revision: int = 1,
    activated_item_ids: tuple[str, ...] = (
        "PRACTICE_DISPUTES",
        "RISK_PROFESSIONAL",
    ),
) -> TenantLegalOperatingModel:
    return TenantLegalOperatingModel(
        tenant_id=tenant_id,
        operating_model_id=
            operating_model_id,
        revision=revision,
        activated_item_ids=
            activated_item_ids,
        effective_from=AT,
        supersedes_operating_model_id=None,
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )


def workflow_definition(
    *,
    owner: str = "PLATFORM",
    owner_tenant_id: str | None = None,
    required_operating_item_ids: tuple[str, ...] = (
        "PRACTICE_DISPUTES",
    ),
) -> LegalWorkflowDefinition:
    return LegalWorkflowDefinition(
        workflow_definition_id=
            "workflow-litigation-core",
        definition_revision=1,
        owner=owner,
        owner_tenant_id=
            owner_tenant_id,
        name="Litigation Core",
        description_reference=
            "workflow-description",
        required_operating_item_ids=
            required_operating_item_ids,
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )


def topology(
    definition: LegalWorkflowDefinition,
) -> LegalWorkflowTopology:
    s1 = (
        LegalWorkflowStage.from_workflow_definition(
            workflow_definition=
                definition,
            stage_definition_id="s1",
            name="Intake",
            description_reference=
                "stage-intake",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
            work_requirement_references=(),
            completion_gate_references=(),
            automation_references=(),
        )
    )

    s2 = (
        LegalWorkflowStage.from_workflow_definition(
            workflow_definition=
                definition,
            stage_definition_id="s2",
            name="Close",
            description_reference=
                "stage-close",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
            work_requirement_references=(),
            completion_gate_references=(),
            automation_references=(),
        )
    )

    return (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=
                definition,
            stages=(s1, s2),
        )
    )


def activation(
    *,
    model: TenantLegalOperatingModel | None = None,
    definition: LegalWorkflowDefinition | None = None,
    activation_id: str = "activation-1",
    activation_revision: int = 1,
    supersedes_activation_id: str | None = None,
) -> TenantLegalWorkflowActivation:
    actual_model = (
        model
        if model is not None
        else operating_model()
    )

    actual_definition = (
        definition
        if definition is not None
        else workflow_definition()
    )

    return TenantLegalWorkflowActivation.from_authorities(
        activation_id=
            activation_id,
        activation_revision=
            activation_revision,
        operating_model=
            actual_model,
        workflow_definition=
            actual_definition,
        workflow_topology=
            topology(
                actual_definition
            ),
        commercial_eligibility_evidence_reference=
            "commercial-proof-1",
        activation_reason_reference=
            "activation-reason-1",
        effective_from=AT,
        supersedes_activation_id=
            supersedes_activation_id,
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.1-G7G-R5-TENANT-LEGAL-WORKFLOW-ACTIVATION"
    )

    assert (
        SCHEMA
        == "WILSY-TENANT-LEGAL-WORKFLOW-ACTIVATION/V1"
    )


def test_platform_workflow_activation_is_exact() -> None:
    value = activation()
    model = operating_model()

    assert value.tenant_id == "tenant-1"
    assert (
        value.operating_model_fingerprint
        == model.fingerprint
    )
    assert value.activation_revision == 1
    assert len(value.fingerprint) == 128


def test_tenant_owned_workflow_for_same_tenant_is_supported() -> None:
    definition = workflow_definition(
        owner="TENANT",
        owner_tenant_id="tenant-1",
    )

    value = activation(
        definition=definition,
    )

    assert (
        value.workflow_definition_fingerprint
        == definition.fingerprint
    )


def test_tenant_owned_workflow_for_other_tenant_rejects() -> None:
    definition = workflow_definition(
        owner="TENANT",
        owner_tenant_id="tenant-2",
    )

    with pytest.raises(
        TenantLegalWorkflowActivationError,
        match=(
            "G7G_R5_TENANT_WORKFLOW_OWNER_MISMATCH"
        ),
    ):
        activation(
            definition=definition,
        )


def test_required_operating_items_must_be_activated() -> None:
    model = operating_model(
        activated_item_ids=(
            "PRACTICE_DISPUTES",
        ),
    )

    definition = workflow_definition(
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
            "RISK_PROFESSIONAL",
        ),
    )

    with pytest.raises(
        TenantLegalWorkflowActivationError,
        match=(
            "G7G_R5_OPERATING_MODEL_CAPABILITY_MISMATCH"
        ),
    ):
        activation(
            model=model,
            definition=definition,
        )


def test_multiple_required_operating_items_supported_when_activated() -> None:
    definition = workflow_definition(
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
            "RISK_PROFESSIONAL",
        ),
    )

    value = activation(
        definition=definition,
    )

    assert (
        value.workflow_definition_id
        == definition.workflow_definition_id
    )


@pytest.mark.parametrize(
    "revision",
    (
        0,
        -1,
        True,
    ),
)
def test_invalid_activation_revision_rejects(
    revision: int,
) -> None:
    with pytest.raises(
        TenantLegalWorkflowActivationError,
        match=(
            "G7G_R5_ACTIVATION_REVISION_INVALID"
        ),
    ):
        activation(
            activation_revision=revision,
        )


def test_self_supersession_rejects() -> None:
    with pytest.raises(
        TenantLegalWorkflowActivationError,
        match="G7G_R5_SELF_SUPERSESSION_INVALID",
    ):
        activation(
            activation_id="activation-1",
            supersedes_activation_id=
                "activation-1",
        )


def test_supersession_history_is_supported() -> None:
    value = activation(
        activation_id="activation-2",
        activation_revision=2,
        supersedes_activation_id=
            "activation-1",
    )

    assert (
        value.supersedes_activation_id
        == "activation-1"
    )


def test_microseconds_are_preserved() -> None:
    value = activation()

    assert (
        value.effective_from.microsecond
        == 123456
    )


def test_no_self_declared_currentness() -> None:
    keys = set(
        activation().to_dict()
    )

    assert "is_current" not in keys
    assert "current" not in keys
    assert "active" not in keys
    assert "status" not in keys


def test_no_iam_assignment_supervision_or_instance_authority() -> None:
    keys = set(
        activation().to_dict()
    )

    forbidden = {
        "principal_id",
        "permission",
        "permissions",
        "authorization_role",
        "assignee_principal_id",
        "supervisor_principal_id",
        "workflow_instance_id",
        "current_stage_id",
        "work_item_id",
    }

    assert not keys & forbidden


def test_commercial_reference_is_evidence_not_commercial_authority() -> None:
    payload = activation().to_dict()

    assert (
        payload[
            "commercial_eligibility_evidence_reference"
        ]
        == "commercial-proof-1"
    )

    forbidden = {
        "plan_id",
        "subscription_id",
        "entitlement_id",
        "price",
        "amount",
        "billing_frequency",
        "financial_execution",
    }

    assert not set(payload) & forbidden


def test_round_trip_preserves_exact_truth() -> None:
    original = activation()

    restored = (
        TenantLegalWorkflowActivation.from_dict(
            original.to_dict()
        )
    )

    assert restored == original


def test_corrupt_fingerprint_rejects() -> None:
    payload = activation().to_dict()
    payload["fingerprint"] = "a" * 128

    with pytest.raises(
        TenantLegalWorkflowActivationError,
        match="G7G_R5_FINGERPRINT_MISMATCH",
    ):
        TenantLegalWorkflowActivation.from_dict(
            payload
        )


def test_extra_or_missing_field_rejects() -> None:
    payload = activation().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        TenantLegalWorkflowActivationError,
        match="G7G_R5_PAYLOAD_SCHEMA_INVALID",
    ):
        TenantLegalWorkflowActivation.from_dict(
            payload
        )

    payload = activation().to_dict()
    del payload["workflow_topology_fingerprint"]

    with pytest.raises(
        TenantLegalWorkflowActivationError,
        match="G7G_R5_PAYLOAD_SCHEMA_INVALID",
    ):
        TenantLegalWorkflowActivation.from_dict(
            payload
        )


# ARTIFACT: test_tenant_legal_workflow_activation.py
# VERSION: v1.0.1-G7G-R5-TENANT-LEGAL-WORKFLOW-ACTIVATION-CERT
