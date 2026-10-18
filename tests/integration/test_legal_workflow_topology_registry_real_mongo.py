"""Real-Mongo certificate for P10C Legal Workflow Topology Registry."""

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
from tests.unit.test_legal_workflow_topology_registry import (
    make_topology,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    COLLECTION_NAME as DEFINITION_COLLECTION_NAME,
    LegalWorkflowDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    COLLECTION_NAME as TOPOLOGY_COLLECTION_NAME,
    DEFINITION_FINGERPRINT_INDEX_NAME,
    DEFINITION_LOOKUP_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    LegalWorkflowTopologyRegistry,
    LegalWorkflowTopologyRegistryConflictError,
    LegalWorkflowTopologyRegistryPersistedRecordInvalidError,
    LegalWorkflowTopologyRegistryRetryTransactionError,
)

VERSION = (
    "v1.0.0-P10C-LEGAL-WORKFLOW-TOPOLOGY-REGISTRY-REAL-MONGO-CERT"
)

MONGO_URI = os.environ[
    "TEST_LEGAL_WORKFLOW_TOPOLOGY_MONGO_URI"
]


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        LegalWorkflowDefinitionRegistry,
        LegalWorkflowTopologyRegistry,
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
        "wilsy_p10c_topology_"
        + uuid.uuid4().hex
    ]

    definition_collection = database[
        DEFINITION_COLLECTION_NAME
    ]
    topology_collection = database[
        TOPOLOGY_COLLECTION_NAME
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

    definition_registry.ensure_indexes()
    topology_registry.ensure_indexes()

    try:
        yield (
            client,
            database,
            definition_collection,
            topology_collection,
            definition_registry,
            topology_registry,
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


def test_real_indexes_and_no_ttl(
    mongo_context,
) -> None:
    (
        _,
        _,
        _,
        topology_collection,
        _,
        _,
    ) = mongo_context

    indexes = {
        row["name"]: row
        for row
        in topology_collection.list_indexes()
    }

    assert (
        DEFINITION_FINGERPRINT_INDEX_NAME
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
            DEFINITION_FINGERPRINT_INDEX_NAME
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


def test_real_platform_create_exact_replay_and_reads(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        topology_collection,
        definition_registry,
        topology_registry,
    ) = mongo_context

    durable = definition()
    value = make_topology(
        durable
    )

    _persist_definition(
        client,
        definition_registry,
        durable,
    )

    created = _persist_topology(
        client,
        topology_registry,
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
    )

    replayed = _persist_topology(
        client,
        topology_registry,
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
    )

    assert created == value
    assert replayed == value
    assert (
        topology_collection.count_documents({})
        == 1
    )

    with client.start_session() as session:
        with session.start_transaction():
            by_definition = (
                topology_registry
                .get_by_definition_fingerprint(
                    durable.fingerprint,
                    session=session,
                )
            )
            by_topology = (
                topology_registry
                .get_by_fingerprint(
                    value.fingerprint,
                    session=session,
                )
            )

    assert by_definition == value
    assert by_topology == value


def test_real_tenant_definition_scope_reproved_without_topology_tenant_field(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        topology_collection,
        definition_registry,
        topology_registry,
    ) = mongo_context

    durable = definition(
        workflow_definition_id=
            "tenant-real-topology",
        owner="TENANT",
        owner_tenant_id=
            "tenant-real-1",
    )
    value = make_topology(
        durable
    )

    _persist_definition(
        client,
        definition_registry,
        durable,
    )

    created = _persist_topology(
        client,
        topology_registry,
        value,
        owner="TENANT",
        owner_tenant_id=
            "tenant-real-1",
    )

    assert created == value

    persisted = topology_collection.find_one(
        {
            "workflow_definition_fingerprint":
                durable.fingerprint
        }
    )

    assert persisted is not None
    assert "owner" not in persisted
    assert "owner_tenant_id" not in persisted
    assert "tenant_id" not in persisted


def test_real_definition_binding_mismatch_rejects(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        topology_collection,
        definition_registry,
        topology_registry,
    ) = mongo_context

    platform = definition(
        workflow_definition_id=
            "shared-definition",
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Platform Shared",
    )

    tenant = definition(
        workflow_definition_id=
            "shared-definition",
        owner="TENANT",
        owner_tenant_id=
            "tenant-real-2",
        name="Tenant Shared",
    )

    tenant_topology = make_topology(
        tenant
    )

    _persist_definition(
        client,
        definition_registry,
        platform,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowTopologyRegistryConflictError,
                match=(
                    "P10B_DURABLE_DEFINITION_BINDING_MISMATCH"
                ),
            ):
                topology_registry.create_or_replay(
                    tenant_topology,
                    owner="PLATFORM",
                    owner_tenant_id=None,
                    session=session,
                )

    assert (
        topology_collection.count_documents({})
        == 0
    )


def test_real_divergent_replay_rejects(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        _,
        definition_registry,
        topology_registry,
    ) = mongo_context

    durable = definition()
    first = make_topology(
        durable,
        variant="linear",
    )
    divergent = make_topology(
        durable,
        variant="short",
    )

    assert first != divergent
    assert (
        first.workflow_definition_fingerprint
        == divergent.workflow_definition_fingerprint
    )

    _persist_definition(
        client,
        definition_registry,
        durable,
    )

    _persist_topology(
        client,
        topology_registry,
        first,
        owner="PLATFORM",
        owner_tenant_id=None,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowTopologyRegistryConflictError,
                match="P10B_DIVERGENT_REPLAY",
            ):
                topology_registry.create_or_replay(
                    divergent,
                    owner="PLATFORM",
                    owner_tenant_id=None,
                    session=session,
                )


def test_real_corrupt_persisted_topology_rejects(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        topology_collection,
        definition_registry,
        topology_registry,
    ) = mongo_context

    durable = definition()
    value = make_topology(
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
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
    )

    topology_collection.update_one(
        {
            "workflow_definition_fingerprint":
                durable.fingerprint
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
                LegalWorkflowTopologyRegistryPersistedRecordInvalidError,
                match="P10B_PERSISTED_RECORD_INVALID",
            ):
                (
                    topology_registry
                    .get_by_definition_fingerprint(
                        durable.fingerprint,
                        session=session,
                    )
                )


def test_real_competing_insert_requires_whole_transaction_retry(
    mongo_context,
) -> None:
    (
        client,
        _,
        _,
        topology_collection,
        definition_registry,
        topology_registry,
    ) = mongo_context

    durable = definition()
    value = make_topology(
        durable
    )

    _persist_definition(
        client,
        definition_registry,
        durable,
    )

    original_insert = (
        topology_collection.insert_one
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

    topology_collection.insert_one = duplicate_insert  # type: ignore[method-assign]

    try:
        with client.start_session() as session:
            session.start_transaction()

            with pytest.raises(
                LegalWorkflowTopologyRegistryRetryTransactionError,
                match="P10B_WHOLE_TRANSACTION_RETRY_REQUIRED",
            ):
                topology_registry.create_or_replay(
                    value,
                    owner="PLATFORM",
                    owner_tenant_id=None,
                    session=session,
                )

            session.abort_transaction()
    finally:
        topology_collection.insert_one = original_insert  # type: ignore[method-assign]


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_workflow_topology_registry_real_mongo.py
# VERSION: v1.0.0-P10C-LEGAL-WORKFLOW-TOPOLOGY-REGISTRY-REAL-MONGO-CERT
# MONGO: disposable dynamically-selected local replica set
# PROTECTED VENDOR-CERT MONGO ENDPOINT: MUST NOT BE USED
# UUID-ISOLATED DATABASE: YES
# REAL DURABLE DEFINITION REGISTRY COMPOSITION: CERTIFIED
# DEFINITION-FINGERPRINT TOPOLOGY SCOPE: CERTIFIED
# TOPOLOGY OWNER / TENANT FIELD INVENTED: NO
# EXACT REPLAY / DIVERGENCE / CORRUPTION / RACE: CERTIFIED
# TTL INDEX: NONE
# PRODUCTION FILE MUTATION: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
