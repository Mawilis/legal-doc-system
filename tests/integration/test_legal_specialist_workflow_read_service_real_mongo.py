# pyright: reportPrivateUsage=false
"""
WILSY OS — Legal Specialist Workflow P1 Composite Real-Mongo Certificate.

Uses real durable Legal registries and one caller-owned Mongo transaction.
The service remains read-only and explanatory.
"""

from __future__ import annotations

from datetime import timedelta
import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient

from tests.integration.test_legal_transition_work_materialization_service_real_mongo import (
    _Context,
    _commit_policy,
    _policy,
)
from tests.unit.test_legal_matter_workflow_transition import AT

from tools.eos.legal_operations.domain.legal_matter_workflow_instance import (
    LegalMatterWorkflowInstance,
)
from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
)
from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)
from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
)
from tools.eos.legal_operations.domain.legal_workflow_gate_satisfaction import (
    LegalWorkflowGateEvidence,
    LegalWorkflowGateSatisfaction,
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
from tools.eos.legal_operations.registry.legal_work_completion_event_registry import (
    COLLECTION_NAME as COMPLETION_COLLECTION,
    LegalWorkCompletionEventRegistry,
)
from tools.eos.legal_operations.service.legal_specialist_workflow_read_service import (
    LegalSpecialistWorkflowReadService,
    LegalSpecialistWorkflowReadServiceError,
    LegalSpecialistWorkflowReadServiceTransactionRequiredError,
)


MONGO_URI = os.environ[
    "TEST_LEGAL_SPECIALIST_WORKFLOW_MONGO_URI"
]
EXPECTED_RS = os.environ[
    "TEST_LEGAL_SPECIALIST_WORKFLOW_MONGO_REPLICA_SET"
]


class Context:
    def __init__(
        self,
        client: MongoClient[Any],
        database: Any,
    ) -> None:
        self.base = _Context(
            client,
            database,
        )

        self.client = client
        self.database = database

        self.completions = (
            LegalWorkCompletionEventRegistry(
                database[
                    COMPLETION_COLLECTION
                ]
            )
        )

        self.completions.ensure_indexes()

        self.service = (
            LegalSpecialistWorkflowReadService(
                work_item_registry=
                    self.base.work,
                receipt_registry=
                    self.base.receipts,
                workflow_instance_registry=
                    self.base.instances,
                workflow_transition_registry=
                    self.base.transitions,
                workflow_stage_registry=
                    self.base.stages,
                dependency_registry=
                    self.base.dependencies,
                completion_registry=
                    self.completions,
                gate_satisfaction_registry=
                    self.base.gates,
            )
        )


@pytest.fixture
def mongo_context() -> Iterator[Context]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        tz_aware=True,
    )

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get("setName")
        == EXPECTED_RS
    )
    assert (
        hello.get("isWritablePrimary")
        is True
    )

    database = client[
        "wilsy_p1_specialist_"
        + uuid.uuid4().hex
    ]

    ctx = Context(
        client,
        database,
    )

    try:
        yield ctx
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def _seed_workflow(
    ctx: Context,
):
    model = TenantLegalOperatingModel(
        tenant_id="tenant-1",
        operating_model_id="model-p1",
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
        name="P1 specialist workflow",
        description_reference="p1-desc",
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        jurisdiction_references=(
            "ZA",
        ),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )

    source = (
        LegalWorkflowStage.from_workflow_definition(
            workflow_definition=definition,
            stage_definition_id="s1",
            name="Source",
            description_reference="source",
            is_entry_stage=True,
            is_terminal_stage=False,
            successor_stage_ids=("s2",),
            work_requirement_references=(),
            completion_gate_references=(),
            automation_references=(),
        )
    )

    target = (
        LegalWorkflowStage.from_workflow_definition(
            workflow_definition=definition,
            stage_definition_id="s2",
            name="Review",
            description_reference="review",
            is_entry_stage=False,
            is_terminal_stage=True,
            successor_stage_ids=(),
            work_requirement_references=(),
            completion_gate_references=(
                "gate:review",
            ),
            automation_references=(),
        )
    )

    topology = (
        LegalWorkflowTopology.from_definition_and_stages(
            workflow_definition=definition,
            stages=(
                source,
                target,
            ),
        )
    )

    activation = (
        TenantLegalWorkflowActivation.from_authorities(
            activation_id="activation-p1",
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
            started_by_principal_id=
                "principal-start",
            start_authorization_evidence_reference=
                "start-auth",
        )
    )

    with ctx.client.start_session() as session:
        with session.start_transaction():
            ctx.base.definitions.create_or_replay(
                definition,
                session=session,
            )
            ctx.base.topologies.create_or_replay(
                topology,
                owner="PLATFORM",
                owner_tenant_id=None,
                session=session,
            )

            for stage in (
                source,
                target,
            ):
                ctx.base.stages.create_or_replay(
                    stage,
                    owner="PLATFORM",
                    owner_tenant_id=None,
                    session=session,
                )

            ctx.base.instances.create_or_replay(
                instance,
                session=session,
            )

    return (
        instance,
        topology,
        source,
        target,
    )


def _transition_and_materialize(
    ctx: Context,
):
    (
        instance,
        topology,
        _source,
        target,
    ) = _seed_workflow(
        ctx
    )

    with ctx.client.start_session() as session:
        with session.start_transaction():
            transition = (
                ctx.base.transition_service.execute(
                    tenant_id="tenant-1",
                    transitioned_by_principal_id=
                        "principal-transition",
                    transition_id=
                        "transition-p1",
                    workflow_instance_id=
                        "instance-1",
                    target_stage_definition_id=
                        "s2",
                    gate_satisfaction_ids=(),
                    branch_selection_evidence_reference=
                        None,
                    transitioned_at=
                        AT + timedelta(minutes=1),
                    transition_authorization_evidence_reference=
                        "transition-auth",
                    session=session,
                )
            )

    policy = _policy(
        instance,
        target,
        policy_id="policy-p1",
        titles=(
            "Predecessor work",
            "Successor work",
        ),
    )

    _commit_policy(
        ctx.base,
        policy,
    )

    with ctx.client.start_session() as session:
        with session.start_transaction():
            materialized = (
                ctx.base.materializer.materialize(
                    "tenant-1",
                    "instance-1",
                    transition.transition_id,
                    session=session,
                )
            )

    assert (
        materialized.receipt
        is not None
    )
    assert (
        len(materialized.work_items)
        == 2
    )

    return (
        instance,
        topology,
        target,
        transition,
        materialized,
    )


def _projection(
    item: LegalWorkItem,
    *,
    tenant_id: str = "tenant-1",
) -> LegalProductiveWorkProjection:
    return LegalProductiveWorkProjection(
        tenant_id=tenant_id,
        principal_id="principal-specialist",
        as_of=AT + timedelta(minutes=3),
        operating_contexts=(),
        capability_ids=(),
        assigned_work_items=(item,),
        supervised_work_items=(),
        overdue_work_items=(),
        due_soon_work_items=(),
    )


def _project(
    ctx: Context,
    work: LegalWorkItem,
):
    with ctx.client.start_session() as session:
        with session.start_transaction():
            return ctx.service.project(
                tenant_id="tenant-1",
                principal_id=
                    "principal-specialist",
                as_of=
                    AT + timedelta(minutes=3),
                productive_work=
                    _projection(work),
                session=session,
            )


def test_real_not_completed_dependency_and_unsatisfied_gate_block(
    mongo_context: Context,
) -> None:
    (
        _instance,
        _topology,
        _target,
        transition,
        materialized,
    ) = _transition_and_materialize(
        mongo_context
    )

    predecessor = (
        materialized.work_items[0]
    )
    successor = (
        materialized.work_items[1]
    )

    result = _project(
        mongo_context,
        successor,
    )

    assert len(result.rows) == 1

    row = result.rows[0]

    assert (
        row.work_item_id
        == successor.work_item_id
    )
    assert (
        row.blocking_dependency_work_item_ids
        == (
            predecessor.work_item_id,
        )
    )
    assert (
        row.unsatisfied_gate_references
        == (
            "gate:review",
        )
    )
    assert (
        row.materialization_transition_id
        == transition.transition_id
    )
    assert (
        row.readiness
        == "BLOCKED_DEPENDENCY_AND_GATE"
    )


def test_real_completion_and_positive_gate_release_to_actionable(
    mongo_context: Context,
) -> None:
    (
        instance,
        topology,
        target,
        _transition,
        materialized,
    ) = _transition_and_materialize(
        mongo_context
    )

    predecessor = (
        materialized.work_items[0]
    )
    successor = (
        materialized.work_items[1]
    )

    completion = LegalWorkCompletionEvent(
        tenant_id=
            predecessor.tenant_id,
        case_matter_id=
            predecessor.case_matter_id,
        work_item_id=
            predecessor.work_item_id,
        work_item_fingerprint=
            predecessor.fingerprint,
        completion_evidence_reference=
            "completion:p1",
        completion_evidence_fingerprint=
            "2" * 128,
        completed_at=
            AT + timedelta(minutes=2),
        actor_principal_id=
            "principal-completer",
        authorization_evidence_reference=
            "completion-auth",
        authorization_evidence_fingerprint=
            "3" * 128,
    )

    gate = (
        LegalWorkflowGateSatisfaction.from_authorities(
            gate_satisfaction_id=
                "gate-p1-review",
            workflow_instance=
                instance,
            workflow_topology=
                topology,
            source_stage=
                target,
            gate_reference=
                "gate:review",
            canonical_evidence=(
                LegalWorkflowGateEvidence(
                    evidence_kind=
                        "CANONICAL_FACT",
                    evidence_reference=
                        "review:complete",
                    evidence_fingerprint=
                        "4" * 128,
                ),
            ),
            evaluated_at=
                AT + timedelta(
                    minutes=2,
                    seconds=10,
                ),
            evaluated_by_principal_id=
                "principal-reviewer",
            evaluation_authorization_evidence_reference=
                "review-auth",
        )
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.completions.create_or_replay(
                completion,
                session=session,
            )
            mongo_context.base.gates.create_or_replay(
                gate,
                session=session,
            )

    result = _project(
        mongo_context,
        successor,
    )

    row = result.rows[0]

    assert (
        row.blocking_dependency_work_item_ids
        == ()
    )
    assert (
        row.unsatisfied_gate_references
        == ()
    )
    assert (
        row.readiness
        == "ACTIONABLE"
    )


def test_real_visible_durable_work_without_receipt_creates_no_workflow_row(
    mongo_context: Context,
) -> None:
    standalone = LegalWorkItem(
        work_item_id="standalone-work",
        tenant_id="tenant-1",
        case_matter_id="matter-standalone",
        title="Standalone",
        source_kind="MANUAL",
        source_reference="manual:1",
        source_evidence_fingerprint=
            "5" * 128,
        status=LegalWorkItemStatus.OPEN,
        created_at=AT,
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.base.work.create_or_replay(
                standalone,
                session=session,
            )

    result = _project(
        mongo_context,
        standalone,
    )

    assert result.rows == ()


def test_real_foreign_tenant_receipts_are_non_disclosing(
    mongo_context: Context,
) -> None:
    _transition_and_materialize(
        mongo_context
    )

    foreign = LegalWorkItem(
        work_item_id="foreign-work",
        tenant_id="tenant-foreign",
        case_matter_id="matter-1",
        title="Foreign",
        source_kind="MANUAL",
        source_reference="foreign:1",
        source_evidence_fingerprint=
            "6" * 128,
        status=LegalWorkItemStatus.OPEN,
        created_at=AT,
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.base.work.create_or_replay(
                foreign,
                session=session,
            )

    projection = _projection(
        foreign,
        tenant_id="tenant-foreign",
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            result = (
                mongo_context.service.project(
                    tenant_id="tenant-foreign",
                    principal_id=
                        "principal-specialist",
                    as_of=
                        AT + timedelta(minutes=3),
                    productive_work=
                        projection,
                    session=session,
                )
            )

    assert result.rows == ()


def test_real_inactive_transaction_rejects_before_read(
    mongo_context: Context,
) -> None:
    standalone = LegalWorkItem(
        work_item_id="inactive-work",
        tenant_id="tenant-1",
        case_matter_id="matter-inactive",
        title="Inactive",
        source_kind="MANUAL",
        source_reference="inactive:1",
        source_evidence_fingerprint=
            "7" * 128,
        status=LegalWorkItemStatus.OPEN,
        created_at=AT,
    )

    with pytest.raises(
        LegalSpecialistWorkflowReadServiceTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        mongo_context.service.project(
            tenant_id="tenant-1",
            principal_id=
                "principal-specialist",
            as_of=
                AT + timedelta(minutes=3),
            productive_work=
                _projection(standalone),
            session=object(),
        )


def test_real_corrupt_receipt_fails_closed_without_inference(
    mongo_context: Context,
) -> None:
    (
        _instance,
        _topology,
        _target,
        transition,
        materialized,
    ) = _transition_and_materialize(
        mongo_context
    )

    successor = (
        materialized.work_items[1]
    )

    mongo_context.database[
        "legal_transition_work_materialization_receipts"
    ].update_one(
        {
            "tenant_id":
                "tenant-1",
            "transition_id":
                transition.transition_id,
        },
        {
            "$set": {
                "fingerprint":
                    "8" * 128,
            }
        },
    )

    with pytest.raises(Exception):
        _project(
            mongo_context,
            successor,
        )


def test_real_service_exposes_no_mutation_authority(
    mongo_context: Context,
) -> None:
    for name in (
        "create",
        "create_or_replay",
        "assign",
        "supervise",
        "complete",
        "transition",
        "authorize",
        "ensure_indexes",
        "update",
        "delete",
        "pay",
        "settle",
    ):
        assert not hasattr(
            mongo_context.service,
            name,
        )
