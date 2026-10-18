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
from datetime import timedelta
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tests.unit.test_legal_workflow_gate_satisfaction import authorities, evidence, satisfaction
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




def _real_stage_satisfaction(
    *,
    gate_satisfaction_id: str,
    evaluated_offset_seconds: int,
    evidence_reference: str,
    evidence_fingerprint: str,
):
    """Build one exact positive gate fact in the certified source-stage scope."""
    instance, topology, source_stage = authorities()
    baseline = satisfaction()
    return type(baseline).from_authorities(
        gate_satisfaction_id=gate_satisfaction_id,
        workflow_instance=instance,
        workflow_topology=topology,
        source_stage=source_stage,
        gate_reference="gate:conflict-current",
        canonical_evidence=(
            evidence(
                reference=evidence_reference,
                fingerprint=evidence_fingerprint,
            ),
        ),
        evaluated_at=(
            baseline.evaluated_at
            + timedelta(
                seconds=evaluated_offset_seconds
            )
        ),
        evaluated_by_principal_id="principal-2",
        evaluation_authorization_evidence_reference=(
            "gate-eval-auth-proof"
        ),
    )


def test_real_instance_history_index_exact_shape_is_unchanged(
    mongo_context,
) -> None:
    """Prove enumeration uses the existing six-field non-TTL index."""
    _, _, collection, _ = mongo_context

    indexes = {
        row["name"]: row
        for row in collection.list_indexes()
    }

    history = indexes[
        INSTANCE_HISTORY_INDEX_NAME
    ]

    assert list(history["key"].items()) == [
        ("tenant_id", 1),
        ("workflow_instance_id", 1),
        ("source_stage_definition_id", 1),
        ("gate_reference", 1),
        ("evaluated_at", 1),
        ("gate_satisfaction_id", 1),
    ]
    assert history.get("unique", False) is False
    assert "expireAfterSeconds" not in history


def test_real_list_workflow_stage_is_deterministic_and_exact(
    mongo_context,
) -> None:
    """Prove real Mongo returns every positive fact in deterministic order."""
    client, database, collection, gate_registry = mongo_context

    baseline, _ = persist_authorities(
        client,
        database,
        gate_registry,
    )

    middle = _real_stage_satisfaction(
        gate_satisfaction_id="gate-satisfaction-2",
        evaluated_offset_seconds=20,
        evidence_reference="conflict-currentness:2",
        evidence_fingerprint="b" * 128,
    )
    later = _real_stage_satisfaction(
        gate_satisfaction_id="gate-satisfaction-3",
        evaluated_offset_seconds=30,
        evidence_reference="conflict-currentness:3",
        evidence_fingerprint="c" * 128,
    )

    with client.start_session() as session:
        with session.start_transaction():
            # Insert in an order different from the required read order.
            gate_registry.create_or_replay(
                later,
                session=session,
            )
            gate_registry.create_or_replay(
                middle,
                session=session,
            )

    assert collection.count_documents({}) == 3

    with client.start_session() as session:
        with session.start_transaction():
            result = gate_registry.list_workflow_stage(
                baseline.tenant_id,
                baseline.workflow_instance_id,
                baseline.source_stage_definition_id,
                session=session,
            )

    assert isinstance(result, tuple)
    assert result == (
        baseline,
        middle,
        later,
    )


def test_real_list_workflow_stage_empty_and_cross_tenant_scopes_are_non_disclosing(
    mongo_context,
) -> None:
    """Prove absence and foreign-tenant reads return no positive facts."""
    client, database, _, gate_registry = mongo_context

    value, _ = persist_authorities(
        client,
        database,
        gate_registry,
    )

    with client.start_session() as session:
        with session.start_transaction():
            missing_stage = (
                gate_registry.list_workflow_stage(
                    value.tenant_id,
                    value.workflow_instance_id,
                    "stage-not-present",
                    session=session,
                )
            )
            foreign_tenant = (
                gate_registry.list_workflow_stage(
                    "tenant-foreign",
                    value.workflow_instance_id,
                    value.source_stage_definition_id,
                    session=session,
                )
            )

    assert missing_stage == ()
    assert foreign_tenant == ()


def test_real_list_workflow_stage_corrupt_row_fails_closed(
    mongo_context,
) -> None:
    """Prove every enumerated real-Mongo row is strictly hydrated."""
    client, database, collection, gate_registry = mongo_context

    value, _ = persist_authorities(
        client,
        database,
        gate_registry,
    )

    collection.update_one(
        {
            "tenant_id": value.tenant_id,
            "gate_satisfaction_id":
                value.gate_satisfaction_id,
        },
        {
            "$set": {
                "fingerprint": "f" * 128,
            }
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError,
                match="P12B_PERSISTED_RECORD_INVALID",
            ):
                gate_registry.list_workflow_stage(
                    value.tenant_id,
                    value.workflow_instance_id,
                    value.source_stage_definition_id,
                    session=session,
                )


def test_real_list_workflow_stage_requires_active_caller_transaction(
    mongo_context,
) -> None:
    """Prove enumeration cannot run outside the existing transaction contract."""
    _, _, _, gate_registry = mongo_context

    with pytest.raises(
        Exception,
        match="P12B_ACTIVE_TRANSACTION_REQUIRED",
    ):
        gate_registry.list_workflow_stage(
            "tenant-1",
            "instance-1",
            "stage-1",
            session=object(),
        )


def test_real_list_workflow_stage_creates_no_new_authority_surface(
    mongo_context,
) -> None:
    """Prove the new real-Mongo surface remains positive-evidence read-only."""
    _, _, _, gate_registry = mongo_context

    for name in (
        "mark_unsatisfied",
        "set_unsatisfied",
        "set_current",
        "transition",
        "authorize",
        "assign",
        "complete",
        "approve",
        "grant",
        "revoke",
        "pay",
        "settle",
    ):
        assert not hasattr(
            gate_registry,
            name,
        )

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
