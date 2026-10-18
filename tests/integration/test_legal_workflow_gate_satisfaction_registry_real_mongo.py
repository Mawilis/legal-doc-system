"""
WILSY OS — P12C Gate Satisfaction Registry Real-Mongo Certificate

VERSION: v1.0.0-P12C-LEGAL-WORKFLOW-GATE-SATISFACTION-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance / Legal Operations.
EPITOME: Certify P12B against one disposable writable replica set using real
definition, topology, stage, workflow-instance, and gate registries.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/
    test_legal_workflow_gate_satisfaction_registry_real_mongo.py
CERTIFICATION DATE: 2026-10-16
CHANGELOG: v1.0.0-P12C — Initial disposable real-Mongo certificate.
COMPLIANCE: POPIA section 19 / GDPR Article 32 / SOC 2 CC7.2.
TENANT BOUNDARY: UUID-isolated database plus tenant-scoped durable identities.
AUTHORITY BOUNDARY: Gate evidence only; no transition or current-stage write.
FINANCIAL AUTHORITY BOUNDARY: NONE.
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tests.unit.test_legal_workflow_gate_satisfaction import authorities, satisfaction
from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_instance_registry import (
    COLLECTION_NAME as INSTANCE_COLLECTION_NAME,
    LegalMatterWorkflowInstanceRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    COLLECTION_NAME as DEFINITION_COLLECTION_NAME,
    LegalWorkflowDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_gate_satisfaction_registry import (
    COLLECTION_NAME as GATE_COLLECTION_NAME,
    FINGERPRINT_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    INSTANCE_HISTORY_INDEX_NAME,
    LegalWorkflowGateSatisfactionRegistry,
    LegalWorkflowGateSatisfactionRegistryNotFoundError,
    LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError,
    LegalWorkflowGateSatisfactionRegistryRetryTransactionError,
)
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    COLLECTION_NAME as STAGE_COLLECTION_NAME,
    LegalWorkflowStageRegistry,
    LegalWorkflowStageRegistryNotFoundError,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    COLLECTION_NAME as TOPOLOGY_COLLECTION_NAME,
    LegalWorkflowTopologyRegistry,
)


VERSION = "v1.0.0-P12C-LEGAL-WORKFLOW-GATE-SATISFACTION-REAL-MONGO"
MONGO_URI = os.environ["TEST_LEGAL_WORKFLOW_GATE_SATISFACTION_MONGO_URI"]


def definition() -> LegalWorkflowDefinition:
    """Reconstruct the exact platform definition used by domain authorities."""
    return LegalWorkflowDefinition(
        workflow_definition_id="workflow-litigation-core",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Litigation Core",
        description_reference="workflow-description",
        required_operating_item_ids=("PRACTICE_DISPUTES",),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=CATALOGUE_FINGERPRINT,
    )


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any]]:
    """Compose all real registries over one UUID-isolated database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI, serverSelectionTimeoutMS=3000, tz_aware=True
    )
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True
    database = client["wilsy_p12c_gate_" + uuid.uuid4().hex]
    definition_registry = LegalWorkflowDefinitionRegistry(
        database[DEFINITION_COLLECTION_NAME]
    )
    topology_registry = LegalWorkflowTopologyRegistry(
        database[TOPOLOGY_COLLECTION_NAME],
        definition_registry=definition_registry,
    )
    stage_registry = LegalWorkflowStageRegistry(
        database[STAGE_COLLECTION_NAME],
        definition_registry=definition_registry,
        topology_registry=topology_registry,
    )
    instance_registry = LegalMatterWorkflowInstanceRegistry(
        database[INSTANCE_COLLECTION_NAME]
    )
    gate_registry = LegalWorkflowGateSatisfactionRegistry(
        database[GATE_COLLECTION_NAME],
        instance_registry=instance_registry,
        topology_registry=topology_registry,
        stage_registry=stage_registry,
    )
    definition_registry.ensure_indexes()
    topology_registry.ensure_indexes()
    stage_registry.ensure_indexes()
    instance_registry.ensure_indexes()
    gate_registry.ensure_indexes()
    try:
        yield client, database, database[GATE_COLLECTION_NAME], gate_registry
    finally:
        client.drop_database(database.name)
        client.close()


def persist_authorities(client, database, gate_registry):
    """Persist the entire authority chain and P12 fact atomically."""
    instance, topology, source_stage = authorities()
    value = satisfaction()
    definition_registry = LegalWorkflowDefinitionRegistry(
        database[DEFINITION_COLLECTION_NAME]
    )
    topology_registry = LegalWorkflowTopologyRegistry(
        database[TOPOLOGY_COLLECTION_NAME],
        definition_registry=definition_registry,
    )
    stage_registry = LegalWorkflowStageRegistry(
        database[STAGE_COLLECTION_NAME],
        definition_registry=definition_registry,
        topology_registry=topology_registry,
    )
    instance_registry = LegalMatterWorkflowInstanceRegistry(
        database[INSTANCE_COLLECTION_NAME]
    )
    with client.start_session() as session:
        with session.start_transaction():
            definition_registry.create_or_replay(definition(), session=session)
            topology_registry.create_or_replay(
                topology,
                owner="PLATFORM",
                owner_tenant_id=None,
                session=session,
            )
            stage_registry.create_or_replay(
                source_stage,
                owner="PLATFORM",
                owner_tenant_id=None,
                session=session,
            )
            instance_registry.create_or_replay(instance, session=session)
            created = gate_registry.create_or_replay(value, session=session)
    return value, created


def test_real_indexes_are_unique_and_non_ttl(mongo_context) -> None:
    """Prove exact index shape and absence of lifecycle-erasing TTL."""
    _, _, collection, _ = mongo_context
    indexes = {row["name"]: row for row in collection.list_indexes()}
    assert indexes[IDENTITY_INDEX_NAME]["unique"] is True
    assert indexes[FINGERPRINT_INDEX_NAME]["unique"] is True
    assert indexes[INSTANCE_HISTORY_INDEX_NAME].get("unique", False) is False
    assert all("expireAfterSeconds" not in row for row in indexes.values())


def test_real_create_replay_and_tenant_read(mongo_context) -> None:
    """Prove atomic creation, exact replay, and durable authority re-proof."""
    client, database, collection, gate_registry = mongo_context
    value, created = persist_authorities(client, database, gate_registry)
    with client.start_session() as session:
        with session.start_transaction():
            replayed = gate_registry.create_or_replay(value, session=session)
            read = gate_registry.get_by_id(
                value.tenant_id, value.gate_satisfaction_id, session=session
            )
    assert created == value
    assert replayed == value
    assert read == value
    assert collection.count_documents({}) == 1


def test_real_cross_tenant_read_is_non_disclosing_not_found(mongo_context) -> None:
    """Prove a foreign tenant cannot observe the durable fact's existence."""
    client, database, _, gate_registry = mongo_context
    value, _ = persist_authorities(client, database, gate_registry)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowGateSatisfactionRegistryNotFoundError,
                match="P12B_GATE_SATISFACTION_NOT_FOUND",
            ):
                gate_registry.get_by_id(
                    "tenant-foreign",
                    value.gate_satisfaction_id,
                    session=session,
                )


def test_real_corrupt_persisted_fact_rejects(mongo_context) -> None:
    """Prove strict hydration rejects post-persistence fingerprint drift."""
    client, database, collection, gate_registry = mongo_context
    value, _ = persist_authorities(client, database, gate_registry)
    collection.update_one(
        {"tenant_id": value.tenant_id, "gate_satisfaction_id": value.gate_satisfaction_id},
        {"$set": {"fingerprint": "f" * 128}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError,
                match="P12B_PERSISTED_RECORD_INVALID",
            ):
                gate_registry.get_by_id(
                    value.tenant_id, value.gate_satisfaction_id, session=session
                )


def test_real_removed_configured_gate_rejects_before_insert(mongo_context) -> None:
    """Prove a stage binding mismatch cannot become durable gate truth."""
    client, database, collection, gate_registry = mongo_context
    value, _ = persist_authorities(client, database, gate_registry)
    collection.delete_many({})
    database[STAGE_COLLECTION_NAME].delete_many({})
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowStageRegistryNotFoundError,
                match="P11B_STAGE_NOT_FOUND",
            ):
                gate_registry.create_or_replay(value, session=session)
    assert collection.count_documents({}) == 0


def test_real_duplicate_race_requires_whole_transaction_retry(
    mongo_context, monkeypatch
) -> None:
    """Prove duplicate insert races never become inferred replay success."""
    client, database, collection, gate_registry = mongo_context
    value, _ = persist_authorities(client, database, gate_registry)
    collection.delete_many({})

    def duplicate_insert(document, *, session):
        raise DuplicateKeyError("synthetic duplicate race")

    monkeypatch.setattr(gate_registry._collection, "insert_one", duplicate_insert)
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(
            LegalWorkflowGateSatisfactionRegistryRetryTransactionError,
            match="P12B_WHOLE_TRANSACTION_RETRY_REQUIRED",
        ):
            gate_registry.create_or_replay(value, session=session)
        session.abort_transaction()


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_workflow_gate_satisfaction_registry_real_mongo.py
# VERSION: v1.0.0-P12C-LEGAL-WORKFLOW-GATE-SATISFACTION-REAL-MONGO
# MONGO: disposable dynamically selected writable replica set only
# PROTECTED VENDOR-CERT ENDPOINT: FORBIDDEN AND ABSENT FROM SOURCE
# UUID-ISOLATED DATABASE: YES
# FULL DURABLE AUTHORITY COMPOSITION: CERTIFIED BY THIS ARTIFACT
# TENANT POSTURE: exact tenant-scoped identities
# FAIL-CLOSED POSTURE: corruption, missing authority, and race rejection
# MUTABLE CURRENT POINTER / SUPERSESSION: NONE
# TRANSITION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
