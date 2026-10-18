"""Real-Mongo certificate for P11C Legal Workflow Stage Registry."""

from __future__ import annotations

import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tests.unit.test_legal_workflow_definition import (
    definition,
)
from tests.unit.test_legal_workflow_stage_registry import (
    stage_value,
)
from tests.unit.test_legal_workflow_topology_registry import (
    make_topology,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    COLLECTION_NAME as DEFINITION_COLLECTION_NAME,
    LegalWorkflowDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    COLLECTION_NAME as STAGE_COLLECTION_NAME,
    DEFINITION_LOOKUP_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    LegalWorkflowStageRegistry,
    LegalWorkflowStageRegistryConflictError,
    LegalWorkflowStageRegistryPersistedRecordInvalidError,
    LegalWorkflowStageRegistryRetryTransactionError,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    COLLECTION_NAME as TOPOLOGY_COLLECTION_NAME,
    LegalWorkflowTopologyRegistry,
)

VERSION = (
    "v1.0.0-P11C-LEGAL-WORKFLOW-STAGE-REGISTRY-REAL-MONGO-CERT"
)

MONGO_URI = os.environ[
    "TEST_LEGAL_WORKFLOW_STAGE_MONGO_URI"
]


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
        LegalWorkflowDefinitionRegistry,
        LegalWorkflowTopologyRegistry,
        LegalWorkflowStageRegistry,
    ]
]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        tz_aware=True,
    )

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get(
            "isWritablePrimary"
        )
        is True
    )

    database = client[
        "wilsy_p11c_stage_"
        + uuid.uuid4().hex
    ]

    definition_collection = database[
        DEFINITION_COLLECTION_NAME
    ]
    topology_collection = database[
        TOPOLOGY_COLLECTION_NAME
    ]
    stage_collection = database[
        STAGE_COLLECTION_NAME
    ]

    definition_registry = (
        LegalWorkflowDefinitionRegistry(
            definition_collection
        )
    )

    topology_registry = (
        LegalWorkflowTopologyRegistry(
            topology_collection,
            definition_registry=
                definition_registry,
        )
    )

    stage_registry = (
        LegalWorkflowStageRegistry(
            stage_collection,
            definition_registry=
                definition_registry,
            topology_registry=
                topology_registry,
        )
    )

    definition_registry.ensure_indexes()
    topology_registry.ensure_indexes()
    stage_registry.ensure_indexes()

    try:
        yield (
            client,
            database,
            definition_collection,
            topology_collection,
            stage_collection,
            definition_registry,
            topology_registry,
            stage_registry,
        )
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def _persist_definition(
    client: MongoClient[Any],
    registry: LegalWorkflowDefinitionRegistry,
    value,
):
    with client.start_session() as session:
        with session.start_transaction():
            return registry.create_or_replay(
                value,
                session=session,
            )


def _persist_topology(
    client: MongoClient[Any],
    registry: LegalWorkflowTopologyRegistry,
    value,
    *,
    owner: str,
    owner_tenant_id: str | None,
):
    with client.start_session() as session:
        with session.start_transaction():
            return registry.create_or_replay(
                value,
                owner=owner,
                owner_tenant_id=
                    owner_tenant_id,
                session=session,
            )


def _persist_stage(
    client: MongoClient[Any],
    registry: LegalWorkflowStageRegistry,
    value,
    *,
    owner: str,
    owner_tenant_id: str | None,
):
    with client.start_session() as session:
        with session.start_transaction():
            return registry.create_or_replay(
                value,
                owner=owner,
                owner_tenant_id=
                    owner_tenant_id,
                session=session,
            )


def _prepare_platform_stack(
    client: MongoClient[Any],
    definition_registry:
        LegalWorkflowDefinitionRegistry,
    topology_registry:
        LegalWorkflowTopologyRegistry,
):
    durable = definition()
    topology = make_topology(
        durable
    )

    _persist_definition(
        client,
        definition_registry,
        durable,
    )

    _persist_topology(
        client,
        topology_registry,
        topology,
        owner="PLATFORM",
        owner_tenant_id=None,
    )

    return durable, topology


def test_real_indexes_and_no_ttl(
    mongo_context,
) -> None:
    (
        _,
        _,
        _,
        _,
        stage_collection,
        _,
        _,
        _,
    ) = mongo_context

    indexes = {
        row["name"]: row
        for row
        in stage_collection.list_indexes()
    }

    assert (
        IDENTITY_INDEX_NAME
        in indexes
    )
    assert (
        FINGERPRINT_INDEX_NAME
        in indexes
    )
    assert (
        DEFINITION_LOOKUP_INDEX_NAME
        in indexes
    )

    assert (
        indexes[
            IDENTITY_INDEX_NAME
        ]["unique"]
        is True
    )

    assert (
        indexes[
            FINGERPRINT_INDEX_NAME
        ]["unique"]
        is True
    )

    assert all(
        "expireAfterSeconds"
        not in row
        for row in indexes.values()
    )


def test_real_platform_create_replay_and_reads(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        _,
        stage_collection,
        definition_registry,
        topology_registry,
        stage_registry,
    ) = mongo_context

    durable, _ = _prepare_platform_stack(
        client,
        definition_registry,
        topology_registry,
    )

    value = stage_value(
        durable
    )

    created = _persist_stage(
        client,
        stage_registry,
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
    )

    replayed = _persist_stage(
        client,
        stage_registry,
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
    )

    assert created == value
    assert replayed == value

    assert (
        stage_collection.count_documents({})
        == 1
    )

    with client.start_session() as session:
        with session.start_transaction():
            by_identity = (
                stage_registry
                .get_by_definition_stage(
                    durable.fingerprint,
                    value.stage_definition_id,
                    session=session,
                )
            )

            by_fingerprint = (
                stage_registry
                .get_by_fingerprint(
                    value.fingerprint,
                    session=session,
                )
            )

    assert by_identity == value
    assert by_fingerprint == value


def test_real_tenant_scope_not_persisted(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        _,
        stage_collection,
        definition_registry,
        topology_registry,
        stage_registry,
    ) = mongo_context

    durable = definition(
        workflow_definition_id=
            "tenant-stage-workflow",
        owner="TENANT",
        owner_tenant_id=
            "tenant-stage-real",
    )

    topology = make_topology(
        durable
    )
    value = stage_value(
        durable
    )

    _persist_definition(
        client,
        definition_registry,
        durable,
    )

    _persist_topology(
        client,
        topology_registry,
        topology,
        owner="TENANT",
        owner_tenant_id=
            "tenant-stage-real",
    )

    _persist_stage(
        client,
        stage_registry,
        value,
        owner="TENANT",
        owner_tenant_id=
            "tenant-stage-real",
    )

    persisted = stage_collection.find_one(
        {
            "workflow_definition_fingerprint":
                durable.fingerprint,
            "stage_definition_id":
                value.stage_definition_id,
        }
    )

    assert persisted is not None
    assert "owner" not in persisted
    assert "owner_tenant_id" not in persisted
    assert "tenant_id" not in persisted
    assert (
        "workflow_topology_fingerprint"
        not in persisted
    )


def test_real_stage_not_in_durable_topology_rejects(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        _,
        stage_collection,
        definition_registry,
        topology_registry,
        stage_registry,
    ) = mongo_context

    durable, _ = _prepare_platform_stack(
        client,
        definition_registry,
        topology_registry,
    )

    outsider = stage_value(
        durable,
        stage_definition_id="outside",
        is_entry_stage=False,
        is_terminal_stage=True,
        successor_stage_ids=(),
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowStageRegistryConflictError,
                match=(
                    "P11B_STAGE_NOT_IN_DURABLE_TOPOLOGY"
                ),
            ):
                stage_registry.create_or_replay(
                    outsider,
                    owner="PLATFORM",
                    owner_tenant_id=None,
                    session=session,
                )

    assert (
        stage_collection.count_documents({})
        == 0
    )


def test_real_stage_fingerprint_mismatch_rejects(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        _,
        stage_collection,
        definition_registry,
        topology_registry,
        stage_registry,
    ) = mongo_context

    durable, _ = _prepare_platform_stack(
        client,
        definition_registry,
        topology_registry,
    )

    changed = stage_value(
        durable,
        stage_definition_id="s1",
        is_entry_stage=True,
        is_terminal_stage=False,
        successor_stage_ids=("s3",),
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowStageRegistryConflictError,
                match="P11B_STAGE_FINGERPRINT_MISMATCH",
            ):
                stage_registry.create_or_replay(
                    changed,
                    owner="PLATFORM",
                    owner_tenant_id=None,
                    session=session,
                )

    assert (
        stage_collection.count_documents({})
        == 0
    )


def test_real_corrupt_persisted_stage_rejects(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        _,
        stage_collection,
        definition_registry,
        topology_registry,
        stage_registry,
    ) = mongo_context

    durable, _ = _prepare_platform_stack(
        client,
        definition_registry,
        topology_registry,
    )

    value = stage_value(
        durable
    )

    _persist_stage(
        client,
        stage_registry,
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
    )

    stage_collection.update_one(
        {
            "workflow_definition_fingerprint":
                durable.fingerprint,
            "stage_definition_id":
                value.stage_definition_id,
        },
        {
            "$set": {
                "fingerprint":
                    "f" * 128
            }
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowStageRegistryPersistedRecordInvalidError,
                match="P11B_PERSISTED_RECORD_INVALID",
            ):
                stage_registry.get_by_definition_stage(
                    durable.fingerprint,
                    value.stage_definition_id,
                    session=session,
                )


def test_real_competing_insert_requires_whole_transaction_retry(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        _,
        stage_collection,
        definition_registry,
        topology_registry,
        stage_registry,
    ) = mongo_context

    durable, _ = _prepare_platform_stack(
        client,
        definition_registry,
        topology_registry,
    )

    value = stage_value(
        durable
    )

    original_insert = (
        stage_collection.insert_one
    )

    def duplicate_insert(
        document,
        *,
        session,
    ):
        original_insert(
            document,
            session=session,
        )
        raise DuplicateKeyError(
            "synthetic post-insert duplicate"
        )

    stage_collection.insert_one = duplicate_insert  # type: ignore[method-assign]

    try:
        with client.start_session() as session:
            session.start_transaction()

            with pytest.raises(
                LegalWorkflowStageRegistryRetryTransactionError,
                match="P11B_WHOLE_TRANSACTION_RETRY_REQUIRED",
            ):
                stage_registry.create_or_replay(
                    value,
                    owner="PLATFORM",
                    owner_tenant_id=None,
                    session=session,
                )

            session.abort_transaction()
    finally:
        stage_collection.insert_one = original_insert  # type: ignore[method-assign]


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_workflow_stage_registry_real_mongo.py
# VERSION: v1.0.0-P11C-LEGAL-WORKFLOW-STAGE-REGISTRY-REAL-MONGO-CERT
# MONGO: disposable dynamically-selected local replica set
# PROTECTED VENDOR-CERT MONGO ENDPOINT: MUST NOT BE USED
# UUID-ISOLATED DATABASE: YES
# REAL DURABLE DEFINITION REGISTRY COMPOSITION: CERTIFIED
# REAL DURABLE TOPOLOGY REGISTRY COMPOSITION: CERTIFIED
# DEFINITION BINDING: CERTIFIED
# TOPOLOGY MEMBERSHIP + STAGE FINGERPRINT: CERTIFIED
# STAGE OWNER / TENANT FIELD INVENTED: NO
# STAGE TOPOLOGY FIELD INVENTED: NO
# TTL INDEX: NONE
# PRODUCTION FILE MUTATION: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
