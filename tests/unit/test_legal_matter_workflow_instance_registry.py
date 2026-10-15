"""Direct certificate for G7G-R14 Legal Matter Workflow Instance Registry."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

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
from tools.eos.legal_operations.registry.legal_matter_workflow_instance_registry import (
    COLLECTION_NAME,
    DEFINITION_HISTORY_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    MATTER_HISTORY_INDEX_NAME,
    VERSION,
    LegalMatterWorkflowInstanceRegistry,
    LegalMatterWorkflowInstanceRegistryConflictError,
    LegalMatterWorkflowInstanceRegistryNotFoundError,
    LegalMatterWorkflowInstanceRegistryPersistedRecordInvalidError,
    LegalMatterWorkflowInstanceRegistryTransactionRequiredError,
)


AT = datetime(
    2026,
    10,
    13,
    2,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


class Session:
    def __init__(
        self,
        active: bool,
    ) -> None:
        self.in_transaction = active


class Cursor:
    def __init__(
        self,
        rows: list[dict[str, object]],
    ) -> None:
        self.rows = [
            dict(row)
            for row in rows
        ]

    def sort(
        self,
        specification: list[
            tuple[str, int]
        ],
    ) -> "Cursor":
        for field, direction in reversed(
            specification
        ):
            self.rows.sort(
                key=lambda row:
                    str(row.get(field, "")),
                reverse=direction < 0,
            )
        return self

    def __iter__(self) -> Any:
        return iter(self.rows)


class Collection:
    def __init__(self) -> None:
        self.rows: list[
            dict[str, object]
        ] = []

        self.index_calls: list[
            tuple[
                list[tuple[str, int]],
                dict[str, object],
            ]
        ] = []

        self.database_name = "unit"

    def create_index(
        self,
        specification: list[
            tuple[str, int]
        ],
        **kwargs: object,
    ) -> str:
        self.index_calls.append(
            (
                list(specification),
                dict(kwargs),
            )
        )
        return str(
            kwargs.get("name", "")
        )

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        assert bool(
            getattr(
                session,
                "in_transaction",
                False,
            )
        )

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value
                in query.items()
            ):
                return dict(row)

        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> object:
        assert bool(
            getattr(
                session,
                "in_transaction",
                False,
            )
        )

        self.rows.append(
            dict(document)
        )

        return object()

    def find(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> Cursor:
        assert bool(
            getattr(
                session,
                "in_transaction",
                False,
            )
        )

        rows = [
            dict(row)
            for row in self.rows
            if all(
                row.get(key) == value
                for key, value
                in query.items()
            )
        ]

        return Cursor(rows)


def authorities() -> tuple[
    TenantLegalOperatingModel,
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
            "workflow-runtime",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Runtime Workflow",
        description_reference=
            "runtime-workflow",
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    entry = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=definition,
        stage_definition_id="entry",
        name="Entry",
        description_reference="entry",
        is_entry_stage=True,
        is_terminal_stage=False,
        successor_stage_ids=("terminal",),
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )

    terminal = LegalWorkflowStage.from_workflow_definition(
        workflow_definition=definition,
        stage_definition_id="terminal",
        name="Terminal",
        description_reference="terminal",
        is_entry_stage=False,
        is_terminal_stage=True,
        successor_stage_ids=(),
        work_requirement_references=(),
        completion_gate_references=(),
        automation_references=(),
    )

    topology = LegalWorkflowTopology.from_definition_and_stages(
        workflow_definition=definition,
        stages=(
            entry,
            terminal,
        ),
    )

    return (
        model,
        definition,
        topology,
    )


def instance(
    *,
    workflow_instance_id: str =
        "instance-1",
    case_matter_id: str =
        "matter-1",
    started_at: datetime = AT,
    start_authorization_evidence_reference: str =
        "start-auth",
) -> LegalMatterWorkflowInstance:
    (
        model,
        definition,
        topology,
    ) = authorities()

    activation = TenantLegalWorkflowActivation.from_authorities(
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

    return LegalMatterWorkflowInstance.from_authorities(
        workflow_instance_id=
            workflow_instance_id,
        case_matter_id=
            case_matter_id,
        activation=
            activation,
        workflow_definition=
            definition,
        workflow_topology=
            topology,
        started_at=
            started_at,
        started_by_principal_id=
            "principal-1",
        start_authorization_evidence_reference=
            start_authorization_evidence_reference,
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.1-G7G-R14-LEGAL-MATTER-WORKFLOW-INSTANCE-REGISTRY"
    )

    assert (
        COLLECTION_NAME
        == "legal_matter_workflow_instances"
    )


def test_indexes_are_exact_and_non_ttl() -> None:
    collection = Collection()
    registry = (
        LegalMatterWorkflowInstanceRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    names = {
        str(kwargs["name"])
        for _, kwargs
        in collection.index_calls
    }

    assert names == {
        IDENTITY_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        MATTER_HISTORY_INDEX_NAME,
        DEFINITION_HISTORY_INDEX_NAME,
    }

    by_name = {
        str(kwargs["name"]):
            (
                specification,
                kwargs,
            )
        for specification, kwargs
        in collection.index_calls
    }

    assert (
        by_name[
            IDENTITY_INDEX_NAME
        ][1]["unique"]
        is True
    )

    assert (
        by_name[
            FINGERPRINT_INDEX_NAME
        ][1]["unique"]
        is True
    )

    assert (
        by_name[
            MATTER_HISTORY_INDEX_NAME
        ][1]["unique"]
        is False
    )

    assert (
        by_name[
            DEFINITION_HISTORY_INDEX_NAME
        ][1]["unique"]
        is False
    )

    assert all(
        "expireAfterSeconds"
        not in kwargs
        for _, kwargs
        in collection.index_calls
    )


def test_active_transaction_required_before_read_or_write() -> None:
    collection = Collection()
    registry = (
        LegalMatterWorkflowInstanceRegistry(
            collection
        )
    )

    with pytest.raises(
        LegalMatterWorkflowInstanceRegistryTransactionRequiredError,
        match="G7G_R14_ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            instance(),
            session=Session(False),
        )

    assert collection.rows == []

    with pytest.raises(
        LegalMatterWorkflowInstanceRegistryTransactionRequiredError,
        match="G7G_R14_ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.get_by_id(
            "tenant-1",
            "instance-1",
            session=Session(False),
        )


def test_create_and_exact_replay() -> None:
    collection = Collection()
    registry = (
        LegalMatterWorkflowInstanceRegistry(
            collection
        )
    )

    tx = Session(True)
    value = instance()

    created = registry.create_or_replay(
        value,
        session=tx,
    )

    replayed = registry.create_or_replay(
        value,
        session=tx,
    )

    assert created == value
    assert replayed == value
    assert len(collection.rows) == 1


def test_same_identity_divergent_replay_rejects() -> None:
    collection = Collection()
    registry = (
        LegalMatterWorkflowInstanceRegistry(
            collection
        )
    )

    tx = Session(True)

    first = instance(
        workflow_instance_id="same-id",
        start_authorization_evidence_reference=
            "auth-a",
    )

    divergent = instance(
        workflow_instance_id="same-id",
        start_authorization_evidence_reference=
            "auth-b",
    )

    registry.create_or_replay(
        first,
        session=tx,
    )

    with pytest.raises(
        LegalMatterWorkflowInstanceRegistryConflictError,
        match="G7G_R14_DIVERGENT_REPLAY",
    ):
        registry.create_or_replay(
            divergent,
            session=tx,
        )

    assert len(collection.rows) == 1


def test_get_by_id_is_exactly_tenant_scoped() -> None:
    collection = Collection()
    registry = (
        LegalMatterWorkflowInstanceRegistry(
            collection
        )
    )

    tx = Session(True)
    value = instance()

    registry.create_or_replay(
        value,
        session=tx,
    )

    loaded = registry.get_by_id(
        "tenant-1",
        "instance-1",
        session=tx,
    )

    assert loaded == value

    with pytest.raises(
        LegalMatterWorkflowInstanceRegistryNotFoundError,
        match="G7G_R14_INSTANCE_NOT_FOUND",
    ):
        registry.get_by_id(
            "tenant-other",
            "instance-1",
            session=tx,
        )


def test_multiple_instances_per_matter_are_supported() -> None:
    collection = Collection()
    registry = (
        LegalMatterWorkflowInstanceRegistry(
            collection
        )
    )

    tx = Session(True)

    first = instance(
        workflow_instance_id="instance-1",
        case_matter_id="matter-1",
        started_at=AT,
    )

    second = instance(
        workflow_instance_id="instance-2",
        case_matter_id="matter-1",
        started_at=(
            AT
            + timedelta(minutes=1)
        ),
    )

    registry.create_or_replay(
        first,
        session=tx,
    )

    registry.create_or_replay(
        second,
        session=tx,
    )

    values = registry.list_matter_instances(
        "tenant-1",
        "matter-1",
        session=tx,
    )

    assert values == (
        first,
        second,
    )


def test_matter_history_is_tenant_and_matter_scoped() -> None:
    collection = Collection()
    registry = (
        LegalMatterWorkflowInstanceRegistry(
            collection
        )
    )

    tx = Session(True)

    wanted = instance(
        workflow_instance_id="wanted",
        case_matter_id="matter-1",
    )

    other = instance(
        workflow_instance_id="other",
        case_matter_id="matter-2",
    )

    registry.create_or_replay(
        wanted,
        session=tx,
    )

    registry.create_or_replay(
        other,
        session=tx,
    )

    assert (
        registry.list_matter_instances(
            "tenant-1",
            "matter-1",
            session=tx,
        )
        == (wanted,)
    )

    assert (
        registry.list_matter_instances(
            "tenant-other",
            "matter-1",
            session=tx,
        )
        == ()
    )


def test_corrupt_persisted_record_rejects() -> None:
    collection = Collection()
    registry = (
        LegalMatterWorkflowInstanceRegistry(
            collection
        )
    )

    tx = Session(True)

    value = instance()
    row = value.to_dict()
    row["fingerprint"] = "f" * 128

    collection.rows.append(
        dict(row)
    )

    with pytest.raises(
        LegalMatterWorkflowInstanceRegistryPersistedRecordInvalidError,
        match="G7G_R14_PERSISTED_RECORD_INVALID",
    ):
        registry.get_by_id(
            "tenant-1",
            "instance-1",
            session=tx,
        )


def test_registry_contains_no_current_stage_transition_work_or_iam_authority() -> None:
    value = instance()
    keys = set(
        value.to_dict()
    )

    forbidden = {
        "current_stage_definition_id",
        "transition_id",
        "sequence_number",
        "head_transition_fingerprint",
        "work_item_id",
        "assignee_principal_id",
        "supervisor_principal_id",
        "permission",
        "authorization_role",
    }

    assert not keys & forbidden


def test_registry_contains_no_commercial_or_financial_authority() -> None:
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


# ARTIFACT: test_legal_matter_workflow_instance_registry.py
# VERSION: v1.0.1-G7G-R14-LEGAL-MATTER-WORKFLOW-INSTANCE-REGISTRY-CERT
