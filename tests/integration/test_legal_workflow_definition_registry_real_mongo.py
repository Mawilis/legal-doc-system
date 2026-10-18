"""Real-Mongo certificate for P9C Legal Workflow Definition Registry."""

from __future__ import annotations

import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tests.unit.test_legal_workflow_definition_registry import (
    definition,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    COLLECTION_NAME,
    FINGERPRINT_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    LegalWorkflowDefinitionRegistry,
    LegalWorkflowDefinitionRegistryConflictError,
    LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
    LegalWorkflowDefinitionRegistryRetryTransactionError,
)

VERSION = (
    "v1.0.0-P9C-LEGAL-WORKFLOW-DEFINITION-REGISTRY-REAL-MONGO-CERT"
)

MONGO_URI = os.environ[
    "TEST_LEGAL_WORKFLOW_DEFINITION_MONGO_URI"
]


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        Any,
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
        "wilsy_p9c_definition_"
        + uuid.uuid4().hex
    ]

    collection = database[
        COLLECTION_NAME
    ]

    try:
        yield (
            client,
            database,
            collection,
        )
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def _commit(
    client: MongoClient[Any],
    registry: LegalWorkflowDefinitionRegistry,
    value,
):
    with client.start_session() as session:
        with session.start_transaction():
            result = registry.create_or_replay(
                value,
                session=session,
            )
    return result


def test_real_indexes_and_no_ttl(
    mongo_context,
) -> None:
    client, _, collection = mongo_context
    registry = LegalWorkflowDefinitionRegistry(
        collection
    )

    registry.ensure_indexes()

    indexes = {
        row["name"]: row
        for row in collection.list_indexes()
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

    assert client is not None


def test_real_platform_create_replay_and_latest(
    mongo_context,
) -> None:
    client, _, collection = mongo_context
    registry = LegalWorkflowDefinitionRegistry(
        collection
    )
    registry.ensure_indexes()

    value = definition()

    first = _commit(
        client,
        registry,
        value,
    )
    replay = _commit(
        client,
        registry,
        value,
    )

    assert first == value
    assert replay == value
    assert collection.count_documents(
        {}
    ) == 1

    with client.start_session() as session:
        with session.start_transaction():
            latest = registry.resolve_latest(
                "PLATFORM",
                None,
                value.workflow_definition_id,
                session=session,
            )

    assert latest == value


def test_real_platform_and_tenant_scopes_do_not_alias(
    mongo_context,
) -> None:
    client, _, collection = mongo_context
    registry = LegalWorkflowDefinitionRegistry(
        collection
    )
    registry.ensure_indexes()

    platform = definition(
        workflow_definition_id=
            "shared-real-workflow",
    )
    tenant = definition(
        workflow_definition_id=
            "shared-real-workflow",
        owner="TENANT",
        owner_tenant_id="tenant-real-1",
        name="Tenant Real Workflow",
    )

    _commit(
        client,
        registry,
        platform,
    )
    _commit(
        client,
        registry,
        tenant,
    )

    assert (
        collection.count_documents({})
        == 2
    )

    with client.start_session() as session:
        with session.start_transaction():
            platform_read = registry.get_revision(
                "PLATFORM",
                None,
                platform.workflow_definition_id,
                1,
                session=session,
            )
            tenant_read = registry.get_revision(
                "TENANT",
                "tenant-real-1",
                tenant.workflow_definition_id,
                1,
                session=session,
            )

    assert platform_read == platform
    assert tenant_read == tenant


def test_real_revision_history_and_gap_rejection(
    mongo_context,
) -> None:
    client, _, collection = mongo_context
    registry = LegalWorkflowDefinitionRegistry(
        collection
    )
    registry.ensure_indexes()

    first = definition()
    second = definition(
        definition_revision=2,
        name="Litigation Core R2",
    )

    _commit(
        client,
        registry,
        first,
    )
    _commit(
        client,
        registry,
        second,
    )

    with client.start_session() as session:
        with session.start_transaction():
            history = registry.get_history(
                "PLATFORM",
                None,
                first.workflow_definition_id,
                session=session,
            )

    assert history == (
        first,
        second,
    )

    collection.delete_one(
        {
            "owner": "PLATFORM",
            "owner_tenant_id": None,
            "workflow_definition_id":
                first.workflow_definition_id,
            "definition_revision": 1,
        }
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
                match="P9B_PERSISTED_REVISION_GAP",
            ):
                registry.get_history(
                    "PLATFORM",
                    None,
                    first.workflow_definition_id,
                    session=session,
                )


def test_real_divergent_replay_rejects(
    mongo_context,
) -> None:
    client, _, collection = mongo_context
    registry = LegalWorkflowDefinitionRegistry(
        collection
    )
    registry.ensure_indexes()

    original = definition()
    divergent = definition(
        name="Divergent Real Definition",
    )

    _commit(
        client,
        registry,
        original,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkflowDefinitionRegistryConflictError,
                match="P9B_DIVERGENT_REPLAY",
            ):
                registry.create_or_replay(
                    divergent,
                    session=session,
                )


def test_real_corrupt_fingerprint_rejects(
    mongo_context,
) -> None:
    client, _, collection = mongo_context
    registry = LegalWorkflowDefinitionRegistry(
        collection
    )
    registry.ensure_indexes()

    value = definition()

    _commit(
        client,
        registry,
        value,
    )

    collection.update_one(
        {
            "owner": "PLATFORM",
            "owner_tenant_id": None,
            "workflow_definition_id":
                value.workflow_definition_id,
            "definition_revision": 1,
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
                LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
                match="P9B_PERSISTED_RECORD_INVALID",
            ):
                registry.get_revision(
                    "PLATFORM",
                    None,
                    value.workflow_definition_id,
                    1,
                    session=session,
                )


def test_real_competing_insert_requires_transaction_retry(
    mongo_context,
) -> None:
    client, _, collection = mongo_context
    registry = LegalWorkflowDefinitionRegistry(
        collection
    )
    registry.ensure_indexes()

    value = definition()

    original_insert = collection.insert_one

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

    collection.insert_one = duplicate_insert  # type: ignore[method-assign]

    try:
        with client.start_session() as session:
            session.start_transaction()

            with pytest.raises(
                LegalWorkflowDefinitionRegistryRetryTransactionError,
                match="P9B_WHOLE_TRANSACTION_RETRY_REQUIRED",
            ):
                registry.create_or_replay(
                    value,
                    session=session,
                )

            session.abort_transaction()
    finally:
        collection.insert_one = original_insert  # type: ignore[method-assign]


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_workflow_definition_registry_real_mongo.py
# VERSION: v1.0.0-P9C-LEGAL-WORKFLOW-DEFINITION-REGISTRY-REAL-MONGO-CERT
# MONGO: disposable dynamically-selected local replica set
# PROTECTED VENDOR-CERT MONGO ENDPOINT: MUST NOT BE USED
# UUID-ISOLATED DATABASE: YES
# PLATFORM / TENANT OWNER ISOLATION: CERTIFIED
# REPLAY / REVISION / CORRUPTION / RACE: CERTIFIED
# TTL INDEX: NONE
# PRODUCTION FILE MUTATION: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
