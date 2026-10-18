"""
WILSY OS — P14-R9 Work Dependency Edge Registry Real-Mongo Certificate

VERSION: v1.0.0-P14-R9-WORK-DEPENDENCY-EDGE-REGISTRY-REAL-MONGO

AUTHORITY:
    Immutable runtime dependency-edge persistence only.

PROTECTED MONGO:
    Port 27027 is forbidden. Test execution requires an explicitly injected
    owned disposable replica set.
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_work_dependency_edge import (
    LegalWorkDependencyEdge,
)
from tools.eos.legal_operations.registry.legal_work_dependency_edge_registry import (
    COLLECTION_NAME,
    LegalWorkDependencyEdgeRegistry,
    LegalWorkDependencyEdgeRegistryConflictError,
    LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
)


MONGO_URI = os.environ[
    "TEST_LEGAL_WORK_DEPENDENCY_EDGE_MONGO_URI"
]
EXPECTED_REPLICA_SET = os.environ[
    "TEST_LEGAL_WORK_DEPENDENCY_EDGE_REPLICA_SET"
]

FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
FP_D = "d" * 128
FP_E = "e" * 128


class _Context:
    def __init__(
        self,
        client: MongoClient[Any],
        database: Any,
    ) -> None:
        self.client = client
        self.database = database
        self.collection = database[
            COLLECTION_NAME
        ]
        self.registry = LegalWorkDependencyEdgeRegistry(
            self.collection
        )
        self.registry.ensure_indexes()


@pytest.fixture
def mongo_context() -> Iterator[_Context]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        tz_aware=True,
    )

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get("setName")
        == EXPECTED_REPLICA_SET
    )
    assert (
        hello.get("isWritablePrimary")
        is True
    )

    database = client[
        "wilsy_p14_dependency_edge_"
        + uuid.uuid4().hex
    ]

    context = _Context(
        client,
        database,
    )

    try:
        yield context
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def _edge(
    *,
    tenant: str = "tenant-law",
    matter: str = "matter-1",
    receipt_id: str = FP_A,
    receipt_fingerprint: str = FP_B,
    predecessor_id: str = "work-a",
    predecessor_fingerprint: str = FP_C,
    successor_id: str = "work-b",
    successor_fingerprint: str = FP_D,
) -> LegalWorkDependencyEdge:
    return LegalWorkDependencyEdge(
        tenant_id=tenant,
        case_matter_id=matter,
        source_materialization_receipt_id=receipt_id,
        source_materialization_receipt_fingerprint=receipt_fingerprint,
        predecessor_work_item_id=predecessor_id,
        predecessor_work_item_fingerprint=predecessor_fingerprint,
        successor_work_item_id=successor_id,
        successor_work_item_fingerprint=successor_fingerprint,
    )


def _commit(
    context: _Context,
    value: LegalWorkDependencyEdge,
) -> LegalWorkDependencyEdge:
    with context.client.start_session() as session:
        with session.start_transaction():
            return context.registry.create_or_replay(
                value,
                session=session,
            )


def test_real_indexes_are_exact_unique_tenant_first_and_non_ttl(
    mongo_context: _Context,
) -> None:
    indexes = {
        entry["name"]: entry
        for entry in mongo_context.collection.list_indexes()
    }

    assert indexes[
        "legal_work_dependency_edge_identity_unique"
    ]["unique"] is True

    assert indexes[
        "legal_work_dependency_edge_relation_unique"
    ]["unique"] is True

    assert indexes[
        "legal_work_dependency_edge_fingerprint_unique"
    ]["unique"] is True

    for entry in indexes.values():
        assert "expireAfterSeconds" not in entry


def test_real_first_insert_exact_replay_and_mongo_id_boundary(
    mongo_context: _Context,
) -> None:
    value = _edge()

    assert _commit(
        mongo_context,
        value,
    ) == value

    assert _commit(
        mongo_context,
        value,
    ) == value

    assert mongo_context.collection.count_documents(
        {}
    ) == 1

    raw = mongo_context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
        }
    )

    assert raw is not None
    assert "_id" in raw


def test_real_same_runtime_relation_divergence_fails_closed(
    mongo_context: _Context,
) -> None:
    original = _edge()

    _commit(
        mongo_context,
        original,
    )

    divergent = _edge(
        predecessor_fingerprint=FP_E,
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkDependencyEdgeRegistryConflictError,
                match="DIVERGENT_RELATION_REPLAY",
            ):
                mongo_context.registry.create_or_replay(
                    divergent,
                    session=session,
                )

            session.abort_transaction()

    assert mongo_context.collection.count_documents(
        {}
    ) == 1


def test_real_cross_tenant_same_relation_isolated(
    mongo_context: _Context,
) -> None:
    left = _edge(
        tenant="tenant-left",
    )
    right = _edge(
        tenant="tenant-right",
    )

    _commit(
        mongo_context,
        left,
    )
    _commit(
        mongo_context,
        right,
    )

    assert mongo_context.collection.count_documents(
        {}
    ) == 2

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            assert mongo_context.registry.list_by_receipt(
                "tenant-left",
                FP_A,
                session=session,
            ) == (
                left,
            )

            assert mongo_context.registry.list_by_receipt(
                "tenant-right",
                FP_A,
                session=session,
            ) == (
                right,
            )


def test_real_predecessor_successor_and_receipt_queries(
    mongo_context: _Context,
) -> None:
    first = _edge(
        predecessor_id="work-a",
        successor_id="work-b",
    )

    second = _edge(
        predecessor_id="work-b",
        predecessor_fingerprint=FP_D,
        successor_id="work-c",
        successor_fingerprint=FP_E,
    )

    _commit(
        mongo_context,
        first,
    )
    _commit(
        mongo_context,
        second,
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            assert mongo_context.registry.list_by_receipt(
                "tenant-law",
                FP_A,
                session=session,
            ) == (
                first,
                second,
            )

            assert mongo_context.registry.list_predecessors(
                "tenant-law",
                "work-c",
                session=session,
            ) == (
                second,
            )

            assert mongo_context.registry.list_successors(
                "tenant-law",
                "work-a",
                session=session,
            ) == (
                first,
            )


def test_real_caller_abort_removes_edge(
    mongo_context: _Context,
) -> None:
    value = _edge()

    with mongo_context.client.start_session() as session:
        session.start_transaction()

        assert mongo_context.registry.create_or_replay(
            value,
            session=session,
        ) == value

        assert mongo_context.collection.count_documents(
            {},
            session=session,
        ) == 1

        session.abort_transaction()

    assert mongo_context.collection.count_documents(
        {}
    ) == 0


def test_real_persisted_corruption_and_extra_field_reject(
    mongo_context: _Context,
) -> None:
    value = _edge()

    _commit(
        mongo_context,
        value,
    )

    original = mongo_context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
            "dependency_edge_id":
                value.dependency_edge_id,
        }
    )

    assert original is not None

    mongo_context.collection.update_one(
        {
            "_id":
                original["_id"],
        },
        {
            "$set": {
                "fingerprint":
                    FP_E,
            }
        },
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
            ):
                mongo_context.registry.get_by_id(
                    value.tenant_id,
                    value.dependency_edge_id,
                    session=session,
                )

    mongo_context.collection.replace_one(
        {
            "_id":
                original["_id"],
        },
        original,
    )

    mongo_context.collection.update_one(
        {
            "_id":
                original["_id"],
        },
        {
            "$set": {
                "blocked":
                    True,
            }
        },
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
            ):
                mongo_context.registry.get_by_id(
                    value.tenant_id,
                    value.dependency_edge_id,
                    session=session,
                )


def test_real_unique_relation_and_fingerprint_indexes_enforce(
    mongo_context: _Context,
) -> None:
    value = _edge()

    _commit(
        mongo_context,
        value,
    )

    raw = value.to_dict()

    duplicate_relation = dict(
        raw
    )
    duplicate_relation[
        "dependency_edge_id"
    ] = FP_E
    duplicate_relation[
        "fingerprint"
    ] = "0" * 128

    with pytest.raises(
        DuplicateKeyError
    ):
        mongo_context.collection.insert_one(
            duplicate_relation
        )

    duplicate_fingerprint = dict(
        raw
    )
    duplicate_fingerprint[
        "predecessor_work_item_id"
    ] = "work-x"
    duplicate_fingerprint[
        "successor_work_item_id"
    ] = "work-y"
    duplicate_fingerprint[
        "dependency_edge_id"
    ] = "1" * 128

    with pytest.raises(
        DuplicateKeyError
    ):
        mongo_context.collection.insert_one(
            duplicate_fingerprint
        )


def test_real_registry_has_no_ttl_current_pointer_or_auxiliary_collection(
    mongo_context: _Context,
) -> None:
    indexes = tuple(
        mongo_context.collection.list_indexes()
    )

    assert all(
        "expireAfterSeconds" not in entry
        for entry in indexes
    )

    assert not hasattr(
        mongo_context.registry,
        "_current_collection",
    )

    assert mongo_context.database.list_collection_names() == [
        COLLECTION_NAME
    ]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_dependency_edge_registry_real_mongo.py
# VERSION: v1.0.0-P14-R9-WORK-DEPENDENCY-EDGE-REGISTRY-REAL-MONGO
# REAL APPEND-ONLY DURABILITY: CERTIFIED
# EXACT REPLAY: CERTIFIED
# RELATION DIVERGENCE: FAIL CLOSED
# TENANT ISOLATION: CERTIFIED
# CALLER TRANSACTION ABORT: CERTIFIED
# REAL UNIQUE INDEXES: CERTIFIED
# TTL: ABSENT
# MUTABLE CURRENT POINTER: ABSENT
# SATISFACTION / COMPLETION AUTHORITY: NONE
# BLOCKED / RELEASE AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# PROTECTED MONGO 27027: FORBIDDEN
# END OF WILSY OS SOVEREIGN ARTIFACT
