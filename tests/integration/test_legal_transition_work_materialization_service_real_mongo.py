"""
WILSY OS — P14-R6 Transition Work Materialization Atomic Real-Mongo Certificate

VERSION:
    v1.0.0-P14-R6-TRANSITION-WORK-MATERIALIZER-REAL-MONGO

PURPOSE:
    Certify that one persisted workflow transition materializes deterministic
    operational work and one immutable transition-work receipt atomically
    inside the caller-owned MongoDB transaction.

AUTHORITY:
    Operational work materialization only.

EXPLICIT NON-AUTHORITY:
    No assignment, supervision, IAM, professional authority, legal deadline,
    notification delivery, AI execution, billing, payment or settlement.

MONGO:
    Explicitly injected owned disposable replica set only.
    Protected localhost port 27027 is forbidden.
"""

from __future__ import annotations

from datetime import timedelta
import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient

from tests.unit.test_legal_matter_workflow_transition import AT, context
from tests.unit.test_legal_matter_workflow_transition_command_service import (
    definition,
)

from tools.eos.legal_operations.domain.legal_work_materialization_policy import (
    LegalOperationalDueRule,
    LegalWorkMaterializationPolicy,
    LegalWorkMaterializationTemplate,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_instance_registry import (
    COLLECTION_NAME as INSTANCE_COLLECTION,
    LegalMatterWorkflowInstanceRegistry,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_transition_registry import (
    COLLECTION_NAME as TRANSITION_COLLECTION,
    LegalMatterWorkflowTransitionRegistry,
)
from tools.eos.legal_operations.registry.legal_transition_work_materialization_receipt_registry import (
    COLLECTION_NAME as RECEIPT_COLLECTION,
    LegalTransitionWorkMaterializationReceiptRegistry,
)
from tools.eos.legal_operations.registry.legal_work_dependency_edge_registry import (
    COLLECTION_NAME as DEPENDENCY_COLLECTION,
    LegalWorkDependencyEdgeRegistry,
    LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
)
from tools.eos.legal_operations.registry.legal_work_item_registry import (
    COLLECTION_NAME as WORK_COLLECTION,
    LegalWorkItemRegistry,
)
from tools.eos.legal_operations.registry.legal_work_materialization_policy_registry import (
    COLLECTION_NAME as POLICY_COLLECTION,
    LegalWorkMaterializationPolicyRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    COLLECTION_NAME as DEFINITION_COLLECTION,
    LegalWorkflowDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_gate_satisfaction_registry import (
    COLLECTION_NAME as GATE_COLLECTION,
    LegalWorkflowGateSatisfactionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    COLLECTION_NAME as STAGE_COLLECTION,
    LegalWorkflowStageRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    COLLECTION_NAME as TOPOLOGY_COLLECTION,
    LegalWorkflowTopologyRegistry,
)
from tools.eos.legal_operations.service.legal_matter_workflow_transition_command_service import (
    LegalMatterWorkflowTransitionCommandService,
)
from tools.eos.legal_operations.service.legal_transition_work_materialization_service import (
    LegalTransitionWorkMaterializationService,
    LegalTransitionWorkMaterializationServiceError,
)


VERSION = "v1.0.0-P14-R6-TRANSITION-WORK-MATERIALIZER-REAL-MONGO"
MONGO_URI = os.environ["TEST_LEGAL_MATERIALIZER_MONGO_URI"]
EXPECTED_REPLICA_SET = os.environ[
    "TEST_LEGAL_MATERIALIZER_REPLICA_SET"
]


class _Context:
    def __init__(
        self,
        client: MongoClient[Any],
        database: Any,
    ) -> None:
        self.client = client
        self.database = database

        self.definitions = LegalWorkflowDefinitionRegistry(
            database[DEFINITION_COLLECTION]
        )
        self.topologies = LegalWorkflowTopologyRegistry(
            database[TOPOLOGY_COLLECTION],
            definition_registry=self.definitions,
        )
        self.stages = LegalWorkflowStageRegistry(
            database[STAGE_COLLECTION],
            definition_registry=self.definitions,
            topology_registry=self.topologies,
        )
        self.instances = LegalMatterWorkflowInstanceRegistry(
            database[INSTANCE_COLLECTION]
        )
        self.gates = LegalWorkflowGateSatisfactionRegistry(
            database[GATE_COLLECTION],
            instance_registry=self.instances,
            topology_registry=self.topologies,
            stage_registry=self.stages,
        )
        self.transitions = LegalMatterWorkflowTransitionRegistry(
            database[TRANSITION_COLLECTION]
        )
        self.policies = LegalWorkMaterializationPolicyRegistry(
            database[POLICY_COLLECTION]
        )
        self.work = LegalWorkItemRegistry(
            database[WORK_COLLECTION]
        )
        self.dependencies = LegalWorkDependencyEdgeRegistry(
            database[DEPENDENCY_COLLECTION]
        )
        self.receipts = LegalTransitionWorkMaterializationReceiptRegistry(
            database[RECEIPT_COLLECTION]
        )

        self.transition_service = LegalMatterWorkflowTransitionCommandService(
            definition_registry=self.definitions,
            instance_registry=self.instances,
            topology_registry=self.topologies,
            stage_registry=self.stages,
            gate_registry=self.gates,
            transition_registry=self.transitions,
        )

        self.materializer = LegalTransitionWorkMaterializationService(
            transition_registry=self.transitions,
            workflow_instance_registry=self.instances,
            policy_registry=self.policies,
            work_item_registry=self.work,
            receipt_registry=self.receipts,
            dependency_registry=self.dependencies,
        )

        for registry in (
            self.definitions,
            self.topologies,
            self.stages,
            self.instances,
            self.gates,
            self.transitions,
            self.policies,
            self.work,
            self.receipts,
            self.dependencies,
        ):
            registry.ensure_indexes()


@pytest.fixture
def mongo_context() -> Iterator[_Context]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        tz_aware=True,
    )

    hello = client.admin.command("hello")

    assert hello.get("setName") == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary") is True

    database = client[
        "wilsy_p14_materializer_" + uuid.uuid4().hex
    ]

    value = _Context(
        client,
        database,
    )

    try:
        yield value
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def _seed_workflow(
    ctx: _Context,
) -> tuple[Any, Any]:
    instance, topology, source, target, _, gates = context()

    with ctx.client.start_session() as session:
        with session.start_transaction():
            ctx.definitions.create_or_replay(
                definition(),
                session=session,
            )

            ctx.topologies.create_or_replay(
                topology,
                owner="PLATFORM",
                owner_tenant_id=None,
                session=session,
            )

            for stage in (
                source,
                target,
            ):
                ctx.stages.create_or_replay(
                    stage,
                    owner="PLATFORM",
                    owner_tenant_id=None,
                    session=session,
                )

            ctx.instances.create_or_replay(
                instance,
                session=session,
            )

            for gate in gates:
                ctx.gates.create_or_replay(
                    gate,
                    session=session,
                )

    return instance, target


def _create_transition(
    ctx: _Context,
    *,
    transition_id: str = "transition-materialize-1",
) -> Any:
    with ctx.client.start_session() as session:
        with session.start_transaction():
            return ctx.transition_service.execute(
                tenant_id="tenant-1",
                transitioned_by_principal_id="principal-authorized",
                transition_id=transition_id,
                workflow_instance_id="instance-1",
                target_stage_definition_id="s2",
                gate_satisfaction_ids=("gate-sat-1",),
                branch_selection_evidence_reference=None,
                transitioned_at=AT + timedelta(minutes=1),
                transition_authorization_evidence_reference=(
                    "tenant-authorization-decision:"
                    + transition_id
                ),
                session=session,
            )


def _policy(
    instance: Any,
    target: Any,
    *,
    policy_id: str = "policy-materialize",
    revision: int = 1,
    supersedes: str | None = None,
    titles: tuple[str, ...] = ("Prepare filing",),
    due_rule: LegalOperationalDueRule = LegalOperationalDueRule.NONE,
    due_offset_seconds: int | None = None,
    conditions: tuple[str, ...] = (),
) -> LegalWorkMaterializationPolicy:
    templates = tuple(
        LegalWorkMaterializationTemplate(
            work_template_id=f"template-{index}",
            title=title,
            due_rule=due_rule,
            due_offset_seconds=due_offset_seconds,
            dependency_template_ids=(
                ()
                if index == 1
                else (f"template-{index - 1}",)
            ),
            condition_references=conditions,
        )
        for index, title in enumerate(
            titles,
            start=1,
        )
    )

    return LegalWorkMaterializationPolicy(
        tenant_id=instance.tenant_id,
        policy_id=policy_id,
        policy_revision=revision,
        workflow_definition_id=instance.workflow_definition_id,
        workflow_definition_fingerprint=(
            instance.workflow_definition_fingerprint
        ),
        target_stage_definition_id=target.stage_definition_id,
        target_stage_fingerprint=target.fingerprint,
        templates=templates,
        supersedes_fingerprint=supersedes,
    )


def _commit_policy(
    ctx: _Context,
    value: LegalWorkMaterializationPolicy,
) -> None:
    with ctx.client.start_session() as session:
        with session.start_transaction():
            assert (
                ctx.policies.create_or_replay(
                    value,
                    session=session,
                )
                == value
            )


def _materialize(
    ctx: _Context,
    *,
    transition_id: str = "transition-materialize-1",
) -> Any:
    with ctx.client.start_session() as session:
        with session.start_transaction():
            return ctx.materializer.materialize(
                "tenant-1",
                "instance-1",
                transition_id,
                session=session,
            )


def test_real_atomic_first_materialization_and_exact_replay(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    transition = _create_transition(
        mongo_context
    )

    policy = _policy(
        instance,
        target,
    )

    _commit_policy(
        mongo_context,
        policy,
    )

    first = _materialize(
        mongo_context
    )

    assert first.receipt is not None
    assert first.replayed is False
    assert first.no_policy is False
    assert len(first.work_items) == 1

    assert (
        first.receipt.transition_id
        == transition.transition_id
    )

    assert first.receipt.policy_revision == 1

    assert first.receipt.outputs[0].work_item_id == (
        first.work_items[0].work_item_id
    )

    assert first.receipt.outputs[0].work_item_fingerprint == (
        first.work_items[0].fingerprint
    )

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 1

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 1

    replay = _materialize(
        mongo_context
    )

    assert replay.replayed is True
    assert replay.receipt == first.receipt
    assert replay.work_items == first.work_items

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 1

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 1


def test_real_later_policy_revision_does_not_reinterpret_receipt(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    first_policy = _policy(
        instance,
        target,
    )

    _commit_policy(
        mongo_context,
        first_policy,
    )

    first = _materialize(
        mongo_context
    )

    second_policy = _policy(
        instance,
        target,
        revision=2,
        supersedes=first_policy.fingerprint,
        titles=("Different future work",),
    )

    _commit_policy(
        mongo_context,
        second_policy,
    )

    replay = _materialize(
        mongo_context
    )

    assert replay.replayed is True
    assert replay.receipt is not None
    assert replay.receipt.policy_revision == 1
    assert replay.receipt.policy_fingerprint == (
        first_policy.fingerprint
    )
    assert replay.work_items == first.work_items

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 1

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 1


def test_real_multi_template_order_and_operational_due(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    transition = _create_transition(
        mongo_context
    )

    policy = _policy(
        instance,
        target,
        titles=(
            "First task",
            "Second task",
            "Third task",
        ),
        due_rule=LegalOperationalDueRule.TRANSITION_OFFSET,
        due_offset_seconds=3600,
    )

    _commit_policy(
        mongo_context,
        policy,
    )

    result = _materialize(
        mongo_context
    )

    assert [
        value.title
        for value in result.work_items
    ] == [
        "First task",
        "Second task",
        "Third task",
    ]

    assert result.receipt is not None

    assert tuple(
        output.work_item_id
        for output in result.receipt.outputs
    ) == tuple(
        value.work_item_id
        for value in result.work_items
    )

    expected_due = (
        transition.transitioned_at
        + timedelta(seconds=3600)
    )

    assert all(
        value.due_at == expected_due
        for value in result.work_items
    )


def test_real_none_due_rule_persists_none(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    _commit_policy(
        mongo_context,
        _policy(
            instance,
            target,
        ),
    )

    result = _materialize(
        mongo_context
    )

    assert result.work_items
    assert all(
        value.due_at is None
        for value in result.work_items
    )


def test_real_condition_policy_fails_closed_without_partial_graph(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    _commit_policy(
        mongo_context,
        _policy(
            instance,
            target,
            conditions=("condition-unresolved",),
        ),
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationServiceError,
        match="CONDITION_RESOLVER_ABSENT",
    ):
        _materialize(
            mongo_context
        )

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 0

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 0


def test_real_ambiguous_policy_families_fail_closed_without_partial_graph(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    _commit_policy(
        mongo_context,
        _policy(
            instance,
            target,
            policy_id="policy-a",
        ),
    )

    _commit_policy(
        mongo_context,
        _policy(
            instance,
            target,
            policy_id="policy-b",
        ),
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationServiceError,
        match="AMBIGUOUS_POLICY_FAMILIES",
    ):
        _materialize(
            mongo_context
        )

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 0

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 0


def test_real_caller_abort_rolls_back_work_and_receipt_atomically(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    _commit_policy(
        mongo_context,
        _policy(
            instance,
            target,
            titles=(
                "First",
                "Second",
            ),
        ),
    )

    with mongo_context.client.start_session() as session:
        session.start_transaction()

        result = mongo_context.materializer.materialize(
            "tenant-1",
            "instance-1",
            "transition-materialize-1",
            session=session,
        )

        assert result.receipt is not None

        assert mongo_context.database[
            WORK_COLLECTION
        ].count_documents(
            {},
            session=session,
        ) == 2

        assert mongo_context.database[
            RECEIPT_COLLECTION
        ].count_documents(
            {},
            session=session,
        ) == 1

        session.abort_transaction()

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 0

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 0


def test_real_missing_receipt_bound_work_fails_closed_without_regeneration(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    _commit_policy(
        mongo_context,
        _policy(
            instance,
            target,
        ),
    )

    result = _materialize(
        mongo_context
    )

    assert result.receipt is not None

    work_id = result.work_items[0].work_item_id

    mongo_context.database[
        WORK_COLLECTION
    ].delete_one(
        {
            "tenant_id": "tenant-1",
            "work_item_id": work_id,
        }
    )

    with pytest.raises(Exception):
        _materialize(
            mongo_context
        )

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 0

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 1


def test_real_corrupt_receipt_fails_closed(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    _commit_policy(
        mongo_context,
        _policy(
            instance,
            target,
        ),
    )

    _materialize(
        mongo_context
    )

    mongo_context.database[
        RECEIPT_COLLECTION
    ].update_one(
        {
            "tenant_id": "tenant-1",
            "transition_id": "transition-materialize-1",
        },
        {
            "$set": {
                "fingerprint": "0" * 128,
            }
        },
    )

    with pytest.raises(Exception):
        _materialize(
            mongo_context
        )

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 1

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 1


def test_real_corrupt_work_fails_closed_without_replacement(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    _commit_policy(
        mongo_context,
        _policy(
            instance,
            target,
        ),
    )

    result = _materialize(
        mongo_context
    )

    work_id = result.work_items[0].work_item_id

    mongo_context.database[
        WORK_COLLECTION
    ].update_one(
        {
            "tenant_id": "tenant-1",
            "work_item_id": work_id,
        },
        {
            "$set": {
                "fingerprint": "0" * 128,
            }
        },
    )

    with pytest.raises(Exception):
        _materialize(
            mongo_context
        )

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 1

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 1


def test_real_foreign_tenant_cannot_materialize_or_write(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    _commit_policy(
        mongo_context,
        _policy(
            instance,
            target,
        ),
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(Exception):
                mongo_context.materializer.materialize(
                    "tenant-foreign",
                    "instance-1",
                    "transition-materialize-1",
                    session=session,
                )

            session.abort_transaction()

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 0

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 0


def test_real_materializer_collections_are_non_ttl_and_no_current_pointer(
    mongo_context: _Context,
) -> None:
    for collection_name in (
        POLICY_COLLECTION,
        WORK_COLLECTION,
        RECEIPT_COLLECTION,
    ):
        indexes = tuple(
            mongo_context.database[
                collection_name
            ].list_indexes()
        )

        assert all(
            "expireAfterSeconds" not in entry
            for entry in indexes
        )

    assert not hasattr(
        mongo_context.receipts,
        "_current_collection",
    )

    assert not hasattr(
        mongo_context.policies,
        "_current_collection",
    )



def test_real_dependency_edges_commit_with_work_and_receipt_atomically(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    policy = _policy(
        instance,
        target,
        titles=(
            "Prepare source",
            "Review source",
            "Approve source",
        ),
    )

    _commit_policy(
        mongo_context,
        policy,
    )

    result = _materialize(
        mongo_context
    )

    assert result.receipt is not None
    assert len(result.work_items) == 3

    edges = tuple(
        mongo_context.database[
            DEPENDENCY_COLLECTION
        ].find({})
    )

    # _policy declares:
    # template-2 -> template-1
    # template-3 -> template-2
    assert len(edges) == 2

    by_work_id = {
        item.work_item_id:
            item
        for item in result.work_items
    }

    for edge in edges:
        assert (
            edge[
                "source_materialization_receipt_id"
            ]
            == result.receipt.receipt_id
        )
        assert (
            edge[
                "source_materialization_receipt_fingerprint"
            ]
            == result.receipt.fingerprint
        )
        assert (
            edge[
                "predecessor_work_item_id"
            ]
            in by_work_id
        )
        assert (
            edge[
                "successor_work_item_id"
            ]
            in by_work_id
        )

        predecessor = by_work_id[
            edge[
                "predecessor_work_item_id"
            ]
        ]
        successor = by_work_id[
            edge[
                "successor_work_item_id"
            ]
        ]

        assert (
            edge[
                "predecessor_work_item_fingerprint"
            ]
            == predecessor.fingerprint
        )
        assert (
            edge[
                "successor_work_item_fingerprint"
            ]
            == successor.fingerprint
        )

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 3

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 1

    assert mongo_context.database[
        DEPENDENCY_COLLECTION
    ].count_documents({}) == 2


def test_real_dependency_graph_exact_replay_creates_no_duplicates(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    policy = _policy(
        instance,
        target,
        titles=(
            "Prepare source",
            "Review source",
            "Approve source",
        ),
    )

    _commit_policy(
        mongo_context,
        policy,
    )

    first = _materialize(
        mongo_context
    )

    replay = _materialize(
        mongo_context
    )

    assert first.receipt is not None
    assert replay.receipt == first.receipt
    assert replay.work_items == first.work_items
    assert replay.replayed is True

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 3

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 1

    assert mongo_context.database[
        DEPENDENCY_COLLECTION
    ].count_documents({}) == 2


def test_real_dependency_graph_caller_abort_rolls_back_all_artifacts(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    policy = _policy(
        instance,
        target,
        titles=(
            "Prepare source",
            "Review source",
            "Approve source",
        ),
    )

    _commit_policy(
        mongo_context,
        policy,
    )

    with mongo_context.client.start_session() as session:
        session.start_transaction()

        result = (
            mongo_context.materializer.materialize(
                "tenant-1",
                "instance-1",
                "transition-materialize-1",
                session=session,
            )
        )

        assert result.receipt is not None

        assert mongo_context.database[
            WORK_COLLECTION
        ].count_documents(
            {},
            session=session,
        ) == 3

        assert mongo_context.database[
            RECEIPT_COLLECTION
        ].count_documents(
            {},
            session=session,
        ) == 1

        assert mongo_context.database[
            DEPENDENCY_COLLECTION
        ].count_documents(
            {},
            session=session,
        ) == 2

        session.abort_transaction()

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 0

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 0

    assert mongo_context.database[
        DEPENDENCY_COLLECTION
    ].count_documents({}) == 0


def test_real_missing_dependency_edge_replay_fails_closed_without_regeneration(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    policy = _policy(
        instance,
        target,
        titles=(
            "Prepare source",
            "Review source",
            "Approve source",
        ),
    )

    _commit_policy(
        mongo_context,
        policy,
    )

    result = _materialize(
        mongo_context
    )

    assert result.receipt is not None

    edge = mongo_context.database[
        DEPENDENCY_COLLECTION
    ].find_one({})

    assert edge is not None

    mongo_context.database[
        DEPENDENCY_COLLECTION
    ].delete_one(
        {
            "_id":
                edge["_id"],
        }
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationServiceError,
        match="REPLAY_DEPENDENCY_EDGE_MISMATCH",
    ):
        _materialize(
            mongo_context
        )

    # Historical truth is not silently regenerated.
    assert mongo_context.database[
        DEPENDENCY_COLLECTION
    ].count_documents({}) == 1

    assert mongo_context.database[
        WORK_COLLECTION
    ].count_documents({}) == 3

    assert mongo_context.database[
        RECEIPT_COLLECTION
    ].count_documents({}) == 1


def test_real_corrupt_dependency_edge_replay_fails_closed(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    policy = _policy(
        instance,
        target,
        titles=(
            "Prepare source",
            "Review source",
        ),
    )

    _commit_policy(
        mongo_context,
        policy,
    )

    result = _materialize(
        mongo_context
    )

    assert result.receipt is not None

    edge = mongo_context.database[
        DEPENDENCY_COLLECTION
    ].find_one({})

    assert edge is not None

    mongo_context.database[
        DEPENDENCY_COLLECTION
    ].update_one(
        {
            "_id":
                edge["_id"],
        },
        {
            "$set": {
                "fingerprint":
                    "0" * 128,
            }
        },
    )

    with pytest.raises(
        LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
    ):
        _materialize(
            mongo_context
        )

    assert mongo_context.database[
        DEPENDENCY_COLLECTION
    ].count_documents({}) == 1


def test_real_zero_dependency_policy_persists_zero_edges(
    mongo_context: _Context,
) -> None:
    instance, target = _seed_workflow(
        mongo_context
    )

    _create_transition(
        mongo_context
    )

    policy = _policy(
        instance,
        target,
        titles=(
            "Independent work",
        ),
    )

    _commit_policy(
        mongo_context,
        policy,
    )

    result = _materialize(
        mongo_context
    )

    assert result.receipt is not None
    assert len(
        result.work_items
    ) == 1

    assert mongo_context.database[
        DEPENDENCY_COLLECTION
    ].count_documents({}) == 0


def test_real_dependency_collection_is_non_ttl_and_has_no_current_pointer(
    mongo_context: _Context,
) -> None:
    indexes = tuple(
        mongo_context.database[
            DEPENDENCY_COLLECTION
        ].list_indexes()
    )

    assert all(
        "expireAfterSeconds"
        not in entry
        for entry in indexes
    )

    assert not hasattr(
        mongo_context.dependencies,
        "_current_collection",
    )

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_transition_work_materialization_service_real_mongo.py
# VERSION: v1.0.0-P14-R6-TRANSITION-WORK-MATERIALIZER-REAL-MONGO
# ATOMIC WORK + RECEIPT TRANSACTION: CERTIFIED BY CALLER-OWNED TRANSACTION
# EXACT REPLAY: REQUIRED
# HISTORICAL POLICY REVISION LOCK: REQUIRED
# MULTI-TEMPLATE ORDER: REQUIRED
# OPERATIONAL DUE ONLY: REQUIRED
# CONDITION / POLICY AMBIGUITY: FAIL CLOSED
# PARTIAL GRAPH ON CALLER ABORT: FORBIDDEN
# TENANT ISOLATION: REQUIRED
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# LEGAL-DEADLINE / NOTIFICATION / AI AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# PROTECTED MONGO 27027: FORBIDDEN
# END OF WILSY OS SOVEREIGN ARTIFACT
