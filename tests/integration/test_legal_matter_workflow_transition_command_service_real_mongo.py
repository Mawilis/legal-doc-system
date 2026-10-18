"""
WILSY OS — P13R6 Workflow Transition Command Service Real-Mongo Certificate

VERSION: v1.0.0-P13R6-LEGAL-MATTER-WORKFLOW-TRANSITION-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance / Legal Operations.
EPITOME: Certify real durable definition, instance, topology, stage, gate and
transition composition on one explicitly injected disposable replica set.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/
    test_legal_matter_workflow_transition_command_service_real_mongo.py
CERTIFICATION DATE: 2026-10-16
CHANGELOG: v1.0.0-P13R6 — Initial real-registry transition certificate.
COMPLIANCE: POPIA section 19 / GDPR Article 32 / SOC 2 CC7.2.
TENANT BOUNDARY: UUID-isolated database and exact tenant predicates.
AUTHORITY BOUNDARY: Transition persistence only; IAM is certified separately.
FINANCIAL AUTHORITY BOUNDARY: NONE.
"""

from __future__ import annotations

from datetime import timedelta
import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient

from tests.unit.test_legal_matter_workflow_transition import AT, context
from tests.unit.test_legal_matter_workflow_transition_command_service import definition
from tools.eos.legal_operations.registry.legal_matter_workflow_instance_registry import (
    COLLECTION_NAME as INSTANCE_COLLECTION,
    LegalMatterWorkflowInstanceRegistry,
    LegalMatterWorkflowInstanceRegistryNotFoundError,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_transition_registry import (
    COLLECTION_NAME as TRANSITION_COLLECTION,
    LegalMatterWorkflowTransitionRegistry,
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
    LegalWorkflowStageRegistryNotFoundError,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    COLLECTION_NAME as TOPOLOGY_COLLECTION,
    LegalWorkflowTopologyRegistry,
)
from tools.eos.legal_operations.service.legal_matter_workflow_transition_command_service import (
    LegalMatterWorkflowTransitionCommandConflictError,
    LegalMatterWorkflowTransitionCommandService,
)


VERSION = "v1.0.0-P13R6-LEGAL-MATTER-WORKFLOW-TRANSITION-REAL-MONGO"
MONGO_URI = os.environ["TEST_LEGAL_WORKFLOW_TRANSITION_MONGO_URI"]
EXPECTED_REPLICA_SET = os.environ["TEST_LEGAL_WORKFLOW_TRANSITION_REPLICA_SET"]


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one real composed service over an isolated database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI, serverSelectionTimeoutMS=3000, tz_aware=True
    )
    hello = client.admin.command("hello")
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary") is True
    database = client["wilsy_p13r6_transition_" + uuid.uuid4().hex]
    definitions = LegalWorkflowDefinitionRegistry(database[DEFINITION_COLLECTION])
    topologies = LegalWorkflowTopologyRegistry(
        database[TOPOLOGY_COLLECTION], definition_registry=definitions
    )
    stages = LegalWorkflowStageRegistry(
        database[STAGE_COLLECTION],
        definition_registry=definitions,
        topology_registry=topologies,
    )
    instances = LegalMatterWorkflowInstanceRegistry(database[INSTANCE_COLLECTION])
    gates = LegalWorkflowGateSatisfactionRegistry(
        database[GATE_COLLECTION],
        instance_registry=instances,
        topology_registry=topologies,
        stage_registry=stages,
    )
    transitions = LegalMatterWorkflowTransitionRegistry(
        database[TRANSITION_COLLECTION]
    )
    service = LegalMatterWorkflowTransitionCommandService(
        definition_registry=definitions,
        instance_registry=instances,
        topology_registry=topologies,
        stage_registry=stages,
        gate_registry=gates,
        transition_registry=transitions,
    )
    for registry in (definitions, topologies, stages, instances, gates, transitions):
        registry.ensure_indexes()
    try:
        yield client, database, service
    finally:
        client.drop_database(database.name)
        client.close()


def seed(client, database) -> None:
    """Persist the complete immutable authority chain atomically."""
    instance, topology, source, target, _, gates = context()
    definitions = LegalWorkflowDefinitionRegistry(database[DEFINITION_COLLECTION])
    topologies = LegalWorkflowTopologyRegistry(
        database[TOPOLOGY_COLLECTION], definition_registry=definitions
    )
    stages = LegalWorkflowStageRegistry(
        database[STAGE_COLLECTION],
        definition_registry=definitions,
        topology_registry=topologies,
    )
    instances = LegalMatterWorkflowInstanceRegistry(database[INSTANCE_COLLECTION])
    gate_registry = LegalWorkflowGateSatisfactionRegistry(
        database[GATE_COLLECTION],
        instance_registry=instances,
        topology_registry=topologies,
        stage_registry=stages,
    )
    with client.start_session() as session:
        with session.start_transaction():
            definitions.create_or_replay(definition(), session=session)
            topologies.create_or_replay(
                topology, owner="PLATFORM", owner_tenant_id=None, session=session
            )
            for stage in (source, target):
                stages.create_or_replay(
                    stage, owner="PLATFORM", owner_tenant_id=None, session=session
                )
            instances.create_or_replay(instance, session=session)
            for gate in gates:
                gate_registry.create_or_replay(gate, session=session)


def execute(client, service, *, tenant="tenant-1", target="s2", gates=("gate-sat-1",)):
    """Run one service command inside one caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return service.execute(
                tenant_id=tenant,
                transitioned_by_principal_id="principal-authorized",
                transition_id="transition-real-1",
                workflow_instance_id="instance-1",
                target_stage_definition_id=target,
                gate_satisfaction_ids=gates,
                branch_selection_evidence_reference=None,
                transitioned_at=AT + timedelta(minutes=1),
                transition_authorization_evidence_reference=(
                    "tenant-authorization-decision:real-1"
                ),
                session=session,
            )


def test_real_transition_and_exact_replay(mongo_context) -> None:
    client, database, service = mongo_context
    seed(client, database)
    created = execute(client, service)
    replayed = execute(client, service)
    assert replayed == created
    assert database[TRANSITION_COLLECTION].count_documents({}) == 1


def test_real_missing_gate_rolls_back_without_transition(mongo_context) -> None:
    client, database, service = mongo_context
    seed(client, database)
    with pytest.raises(
        LegalMatterWorkflowTransitionCommandConflictError,
        match="G7G_R10_GATE_SATISFACTION_SET_MISMATCH",
    ):
        execute(client, service, gates=())
    assert database[TRANSITION_COLLECTION].count_documents({}) == 0


def test_real_invalid_target_rolls_back_without_transition(mongo_context) -> None:
    client, database, service = mongo_context
    seed(client, database)
    with pytest.raises(
        LegalWorkflowStageRegistryNotFoundError,
        match="P11B_STAGE_NOT_FOUND",
    ):
        execute(client, service, target="outside")
    assert database[TRANSITION_COLLECTION].count_documents({}) == 0


def test_real_foreign_tenant_is_non_disclosing_and_writes_nothing(mongo_context) -> None:
    client, database, service = mongo_context
    seed(client, database)
    with pytest.raises(
        LegalMatterWorkflowInstanceRegistryNotFoundError,
        match="G7G_R14_INSTANCE_NOT_FOUND",
    ):
        execute(client, service, tenant="tenant-foreign")
    assert database[TRANSITION_COLLECTION].count_documents({}) == 0


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_matter_workflow_transition_command_service_real_mongo.py
# VERSION: v1.0.0-P13R6-LEGAL-MATTER-WORKFLOW-TRANSITION-REAL-MONGO
# MONGO: explicit disposable dynamically selected replica set only
# UUID-ISOLATED DATABASE: YES
# REAL AUTHORITY STACK: definition, instance, topology, stage, gate, transition
# TENANT POSTURE: exact tenant and foreign-tenant non-disclosure
# FAIL-CLOSED POSTURE: missing gate/target and foreign tenant leave no append
# IAM AUTHORITY: NOT CLAIMED BY THIS SERVICE CERTIFICATE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
