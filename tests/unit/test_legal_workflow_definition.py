"""Direct certificate for G7G-R2 Legal Workflow Definition."""
from __future__ import annotations

import pytest

from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    SCHEMA,
    VERSION,
    LegalWorkflowDefinition,
    LegalWorkflowDefinitionError,
    LegalWorkflowDefinitionOwner,
)


def definition(
    *,
    workflow_definition_id: str = "workflow-litigation-core",
    definition_revision: int = 1,
    owner: LegalWorkflowDefinitionOwner | str = "PLATFORM",
    owner_tenant_id: str | None = None,
    name: str = "Litigation Core",
    description_reference: str = "workflow-description-litigation-core",
    required_operating_item_ids: tuple[str, ...] = (
        "PRACTICE_DISPUTES",
    ),
    jurisdiction_references: tuple[str, ...] = (),
    catalogue_fingerprint: str = CATALOGUE_FINGERPRINT,
) -> LegalWorkflowDefinition:
    return LegalWorkflowDefinition(
        workflow_definition_id=
            workflow_definition_id,
        definition_revision=
            definition_revision,
        owner=
            owner,
        owner_tenant_id=
            owner_tenant_id,
        name=
            name,
        description_reference=
            description_reference,
        required_operating_item_ids=
            required_operating_item_ids,
        jurisdiction_references=
            jurisdiction_references,
        catalogue_fingerprint=
            catalogue_fingerprint,
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.1-G7G-R2-LEGAL-WORKFLOW-DEFINITION"
    )
    assert (
        SCHEMA
        == "WILSY-LEGAL-WORKFLOW-DEFINITION/V1"
    )


def test_platform_definition_is_exact() -> None:
    value = definition()

    assert (
        value.owner
        is LegalWorkflowDefinitionOwner.PLATFORM
    )
    assert value.owner_tenant_id is None
    assert value.definition_revision == 1
    assert value.required_operating_item_ids == (
        "PRACTICE_DISPUTES",
    )
    assert len(value.fingerprint) == 128


def test_tenant_definition_is_supported() -> None:
    value = definition(
        workflow_definition_id=
            "tenant-workflow-1",
        owner="TENANT",
        owner_tenant_id="tenant-1",
    )

    assert (
        value.owner
        is LegalWorkflowDefinitionOwner.TENANT
    )
    assert value.owner_tenant_id == "tenant-1"


def test_platform_owner_forbids_tenant() -> None:
    with pytest.raises(
        LegalWorkflowDefinitionError,
        match=(
            "G7G_R2_PLATFORM_OWNER_FORBIDS_TENANT"
        ),
    ):
        definition(
            owner_tenant_id="tenant-1",
        )


def test_tenant_owner_requires_tenant() -> None:
    with pytest.raises(
        LegalWorkflowDefinitionError,
        match=(
            "G7G_R2_TENANT_OWNER_REQUIRES_TENANT"
        ),
    ):
        definition(
            owner="TENANT",
            owner_tenant_id=None,
        )


@pytest.mark.parametrize(
    "tenant",
    (
        "default",
        "global",
        "root",
        "*",
    ),
)
def test_pseudo_tenant_owner_rejects(
    tenant: str,
) -> None:
    with pytest.raises(
        LegalWorkflowDefinitionError,
        match="G7G_R2_OWNER_TENANT_INVALID",
    ):
        definition(
            owner="TENANT",
            owner_tenant_id=tenant,
        )


@pytest.mark.parametrize(
    "revision",
    (
        0,
        -1,
        True,
    ),
)
def test_invalid_revision_rejects(
    revision: int,
) -> None:
    with pytest.raises(
        LegalWorkflowDefinitionError,
        match=(
            "G7G_R2_DEFINITION_REVISION_INVALID"
        ),
    ):
        definition(
            definition_revision=revision,
        )


def test_unknown_operating_item_rejects_through_local_boundary() -> None:
    with pytest.raises(
        LegalWorkflowDefinitionError,
        match=(
            "G7G_R2_REQUIRED_OPERATING_ITEM_UNKNOWN"
        ),
    ):
        definition(
            required_operating_item_ids=(
                "NOT_REAL",
            ),
        )


def test_duplicate_operating_items_reject() -> None:
    with pytest.raises(
        LegalWorkflowDefinitionError,
        match=(
            "G7G_R2_REQUIRED_OPERATING_ITEM_DUPLICATE"
        ),
    ):
        definition(
            required_operating_item_ids=(
                "PRACTICE_DISPUTES",
                "PRACTICE_DISPUTES",
            ),
        )


def test_multiple_operating_dimensions_supported() -> None:
    value = definition(
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
            "RISK_PROFESSIONAL",
            "INFO_LITIGATION_SUPPORT",
        ),
    )

    assert value.required_operating_item_ids == (
        "PRACTICE_DISPUTES",
        "RISK_PROFESSIONAL",
        "INFO_LITIGATION_SUPPORT",
    )


def test_jurisdiction_overlay_references_are_opaque() -> None:
    value = definition(
        jurisdiction_references=(
            "ZA",
            "ZA-GP",
            "court:Gauteng-High-Court",
        ),
    )

    assert value.jurisdiction_references == (
        "ZA",
        "ZA-GP",
        "court:Gauteng-High-Court",
    )


def test_duplicate_jurisdiction_reference_rejects() -> None:
    with pytest.raises(
        LegalWorkflowDefinitionError,
        match=(
            "G7G_R2_JURISDICTION_REFERENCE_DUPLICATE"
        ),
    ):
        definition(
            jurisdiction_references=(
                "ZA",
                "ZA",
            ),
        )


def test_catalogue_fingerprint_drift_rejects() -> None:
    with pytest.raises(
        LegalWorkflowDefinitionError,
        match=(
            "G7G_R2_CATALOGUE_BINDING_INVALID"
        ),
    ):
        definition(
            catalogue_fingerprint=
                "a" * 128,
        )


def test_no_stage_instance_assignment_or_supervision_authority() -> None:
    keys = set(
        definition().to_dict()
    )

    forbidden = {
        "stage_id",
        "current_stage_id",
        "workflow_instance_id",
        "work_item_id",
        "assignee_principal_id",
        "supervisor_principal_id",
        "permission",
        "authorization_role",
    }

    assert not keys & forbidden


def test_no_commercial_or_financial_authority() -> None:
    keys = set(
        definition().to_dict()
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
    original = definition(
        jurisdiction_references=(
            "ZA",
        ),
    )

    restored = (
        LegalWorkflowDefinition.from_dict(
            original.to_dict()
        )
    )

    assert restored == original


def test_corrupt_fingerprint_rejects() -> None:
    payload = definition().to_dict()
    payload["fingerprint"] = "a" * 128

    with pytest.raises(
        LegalWorkflowDefinitionError,
        match="G7G_R2_FINGERPRINT_MISMATCH",
    ):
        LegalWorkflowDefinition.from_dict(
            payload
        )


def test_extra_or_missing_field_rejects() -> None:
    payload = definition().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        LegalWorkflowDefinitionError,
        match=(
            "G7G_R2_PAYLOAD_SCHEMA_INVALID"
        ),
    ):
        LegalWorkflowDefinition.from_dict(
            payload
        )

    payload = definition().to_dict()
    del payload["name"]

    with pytest.raises(
        LegalWorkflowDefinitionError,
        match=(
            "G7G_R2_PAYLOAD_SCHEMA_INVALID"
        ),
    ):
        LegalWorkflowDefinition.from_dict(
            payload
        )


# ARTIFACT: test_legal_workflow_definition.py
# VERSION: v1.0.1-G7G-R2-LEGAL-WORKFLOW-DEFINITION-CERT
