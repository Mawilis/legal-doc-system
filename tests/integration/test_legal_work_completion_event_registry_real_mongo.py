"""
WILSY OS — P14-R14 Legal Work Completion Event Registry Real-Mongo Certificate.

Uses only an explicitly injected disposable replica set.
Protected Mongo port 27027 is forbidden.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
)
from tools.eos.legal_operations.registry.legal_work_completion_event_registry import (
    ACTOR_HISTORY_INDEX_NAME,
    COLLECTION_NAME,
    FINGERPRINT_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    MATTER_HISTORY_INDEX_NAME,
    WORK_HISTORY_INDEX_NAME,
    LegalWorkCompletionEventRegistry,
    LegalWorkCompletionEventRegistryConflictError,
    LegalWorkCompletionEventRegistryPersistedRecordInvalidError,
)


AT = datetime(
    2026,
    10,
    16,
    19,
    0,
    tzinfo=timezone.utc,
)


def event(
    **overrides: object,
) -> LegalWorkCompletionEvent:
    values: dict[str, object] = {
        "tenant_id": "tenant-law",
        "case_matter_id": "matter-1",
        "work_item_id": "work-1",
        "work_item_fingerprint": "a" * 128,
        "completion_evidence_reference": "evidence:complete:1",
        "completion_evidence_fingerprint": "b" * 128,
        "completed_at": AT,
        "actor_principal_id": "principal-1",
        "authorization_evidence_reference": "iam:decision:1",
        "authorization_evidence_fingerprint": "c" * 128,
    }

    values.update(
        overrides
    )

    return LegalWorkCompletionEvent(
        **values  # type: ignore[arg-type]
    )


@pytest.fixture()
def mongo_context():
    uri = os.environ[
        "TEST_LEGAL_WORK_COMPLETION_EVENT_MONGO_URI"
    ]
    replica_set = os.environ[
        "TEST_LEGAL_WORK_COMPLETION_EVENT_REPLICA_SET"
    ]

    client = MongoClient(
        uri,
        replicaSet=replica_set,
    )

    database = client[
        "wilsy_p14_r14_"
        + uuid.uuid4().hex
    ]

    collection = database[
        COLLECTION_NAME
    ]

    registry = LegalWorkCompletionEventRegistry(
        collection
    )
    registry.ensure_indexes()

    try:
        yield (
            client,
            database,
            collection,
            registry,
        )
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def commit_create(
    client,
    registry,
    value,
):
    with client.start_session() as session:
        with session.start_transaction():
            return registry.create_or_replay(
                value,
                session=session,
            )


def test_real_indexes_are_exact_unique_tenant_first_and_non_ttl(
    mongo_context,
) -> None:
    _, _, collection, _ = mongo_context

    indexes = {
        value["name"]:
            value
        for value in collection.list_indexes()
    }

    assert indexes[
        IDENTITY_INDEX_NAME
    ]["unique"] is True

    assert indexes[
        FINGERPRINT_INDEX_NAME
    ]["unique"] is True

    assert indexes[
        WORK_HISTORY_INDEX_NAME
    ]["unique"] is True

    for name in (
        IDENTITY_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        WORK_HISTORY_INDEX_NAME,
        MATTER_HISTORY_INDEX_NAME,
        ACTOR_HISTORY_INDEX_NAME,
    ):
        keys = list(
            indexes[name]["key"].items()
        )

        assert keys[0][0] == "tenant_id"
        assert (
            "expireAfterSeconds"
            not in indexes[name]
        )


def test_real_first_insert_exact_replay_and_mongo_id_boundary(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context
    value = event()

    first = commit_create(
        client,
        registry,
        value,
    )
    replay = commit_create(
        client,
        registry,
        value,
    )

    assert first == value
    assert replay == value

    raw = collection.find_one({})

    assert raw is not None
    assert "_id" in raw
    assert collection.count_documents({}) == 1


def test_real_same_work_divergence_fails_closed(
    mongo_context,
) -> None:
    client, _, _, registry = mongo_context

    commit_create(
        client,
        registry,
        event(),
    )

    with pytest.raises(
        LegalWorkCompletionEventRegistryConflictError
    ):
        commit_create(
            client,
            registry,
            event(
                completion_evidence_reference=
                    "evidence:other"
            ),
        )


def test_real_cross_tenant_same_work_identity_isolated(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context

    commit_create(
        client,
        registry,
        event(),
    )

    commit_create(
        client,
        registry,
        event(
            tenant_id="tenant-other"
        ),
    )

    assert collection.count_documents({}) == 2


def test_real_work_matter_and_actor_queries_are_exact(
    mongo_context,
) -> None:
    client, _, _, registry = mongo_context

    first = event()
    second = event(
        case_matter_id="matter-2",
        work_item_id="work-2",
        work_item_fingerprint="d" * 128,
        completion_evidence_reference="evidence:2",
        completion_evidence_fingerprint="e" * 128,
        actor_principal_id="principal-2",
        authorization_evidence_reference="iam:2",
        authorization_evidence_fingerprint="f" * 128,
    )

    for value in (
        first,
        second,
    ):
        commit_create(
            client,
            registry,
            value,
        )

    with client.start_session() as session:
        with session.start_transaction():
            assert registry.list_work_history(
                "tenant-law",
                "work-1",
                session=session,
            ) == (
                first,
            )

            assert registry.list_matter_history(
                "tenant-law",
                "matter-2",
                session=session,
            ) == (
                second,
            )

            assert registry.list_actor_history(
                "tenant-law",
                "principal-2",
                session=session,
            ) == (
                second,
            )


def test_real_caller_abort_removes_completion_event(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context

    with client.start_session() as session:
        session.start_transaction()

        registry.create_or_replay(
            event(),
            session=session,
        )

        assert collection.count_documents(
            {},
            session=session,
        ) == 1

        session.abort_transaction()

    assert collection.count_documents({}) == 0


def test_real_persisted_corruption_and_extra_field_reject(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context
    value = event()

    commit_create(
        client,
        registry,
        value,
    )

    collection.update_one(
        {
            "completion_event_id":
                value.completion_event_id,
        },
        {
            "$set": {
                "fingerprint":
                    "0" * 128,
            }
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkCompletionEventRegistryPersistedRecordInvalidError
            ):
                registry.get_by_id(
                    "tenant-law",
                    value.completion_event_id,
                    session=session,
                )

    collection.replace_one(
        {},
        {
            **value.to_dict(),
            "unexpected": True,
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkCompletionEventRegistryPersistedRecordInvalidError
            ):
                registry.get_by_id(
                    "tenant-law",
                    value.completion_event_id,
                    session=session,
                )


def test_real_unique_indexes_enforce_identity_fingerprint_and_work(
    mongo_context,
) -> None:
    _, _, collection, _ = mongo_context
    value = event()

    collection.insert_one(
        value.to_dict()
    )

    duplicate_identity = value.to_dict()
    duplicate_identity[
        "fingerprint"
    ] = "d" * 128

    with pytest.raises(
        DuplicateKeyError
    ):
        collection.insert_one(
            duplicate_identity
        )

    duplicate_fingerprint = event(
        work_item_id="work-2",
        work_item_fingerprint="e" * 128,
    ).to_dict()

    duplicate_fingerprint[
        "fingerprint"
    ] = value.fingerprint

    with pytest.raises(
        DuplicateKeyError
    ):
        collection.insert_one(
            duplicate_fingerprint
        )

    duplicate_work = event(
        completion_evidence_reference="evidence:other",
        completion_evidence_fingerprint="f" * 128,
    ).to_dict()

    with pytest.raises(
        DuplicateKeyError
    ):
        collection.insert_one(
            duplicate_work
        )


def test_real_registry_has_no_ttl_current_pointer_or_auxiliary_collection(
    mongo_context,
) -> None:
    _, database, collection, registry = mongo_context

    indexes = tuple(
        collection.list_indexes()
    )

    assert all(
        "expireAfterSeconds"
        not in entry
        for entry in indexes
    )

    assert not hasattr(
        registry,
        "_current_collection",
    )

    assert database.list_collection_names() == [
        COLLECTION_NAME
    ]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_completion_event_registry_real_mongo.py
# VERSION: v1.0.0-P14-R14-WORK-COMPLETION-EVENT-REGISTRY-REAL-MONGO
# REAL MONGO DURABILITY: CERTIFIED
# CALLER TRANSACTION ROLLBACK: CERTIFIED
# TENANT ISOLATION: CERTIFIED
# EXACT REPLAY: CERTIFIED
# TTL: ABSENT
# MUTABLE CURRENT POINTER: ABSENT
# COMPLETION AUTHORITY: NONE
# DEPENDENCY SATISFACTION AUTHORITY: NONE
# FINANCIAL AUTHORITY: NONE
# PROTECTED MONGO 27027: FORBIDDEN
# END OF WILSY OS SOVEREIGN ARTIFACT
