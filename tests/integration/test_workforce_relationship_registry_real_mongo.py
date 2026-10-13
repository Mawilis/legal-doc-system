"""Real-Mongo certificate for W3B workforce history."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.registry import (
    workforce_relationship_registry as registry,
)


AT = datetime(
    2026,
    10,
    13,
    6,
    0,
    tzinfo=timezone.utc,
)


def _client():
    """Open only the governed disposable certification replica set."""

    uri = os.getenv(
        "TEST_VENDOR_MONGO_URI",
        "mongodb://127.0.0.1:27027/"
        "?replicaSet=wilsyVendorCertRS",
    )

    try:
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            retryWrites=True,
        )

        hello = client.admin.command(
            "hello"
        )
    except PyMongoError as error:
        raise RuntimeError(
            "W3B_CERT_MONGO_UNAVAILABLE"
        ) from error

    if not hello.get("setName"):
        client.close()
        raise RuntimeError(
            "W3B_CERT_REPLICA_SET_REQUIRED"
        )

    if hello.get("isWritablePrimary") is not True:
        client.close()
        raise RuntimeError(
            "W3B_CERT_WRITABLE_PRIMARY_REQUIRED"
        )

    if hello.get(
        "logicalSessionTimeoutMinutes"
    ) is None:
        client.close()
        raise RuntimeError(
            "W3B_CERT_SESSIONS_REQUIRED"
        )

    return client


@pytest.fixture
def mongo():
    client = _client()
    database_name = (
        "wilsy_w3b_"
        + uuid4().hex
    )
    database = client[
        database_name
    ]
    collection = database[
        registry.COLLECTION_NAME
    ]

    registry.ensure_indexes(
        collection
    )

    try:
        yield client, database, collection
    finally:
        client.drop_database(
            database_name
        )
        client.close()


def relation(
    *,
    relationship_id="rel-001",
    revision=1,
    previous=None,
    status=WorkforceRelationshipStatus.ACTIVE,
):
    return WorkforceRelationship(
        relationship_id=relationship_id,
        revision=revision,
        scope_kind=WorkforceScopeKind.TENANT,
        scope_id="tenant-real",
        principal_id="principal-real",
        relationship_type=(
            WorkforceRelationshipType.EMPLOYEE
        ),
        status=status,
        effective_from=AT,
        effective_until=None,
        status_effective_at=AT,
        reason_reference=f"evidence-{revision}",
        supersedes_fingerprint=(
            None
            if previous is None
            else previous.fingerprint
        ),
    )


def test_real_indexes_have_no_ttl(
    mongo,
):
    _, _, collection = mongo

    indexes = {
        row["name"]: row
        for row in collection.list_indexes()
    }

    assert (
        registry.REVISION_INDEX_NAME
        in indexes
    )
    assert (
        registry.FINGERPRINT_INDEX_NAME
        in indexes
    )
    assert (
        registry.PRINCIPAL_INDEX_NAME
        in indexes
    )

    assert all(
        "expireAfterSeconds"
        not in row
        for row in indexes.values()
    )


def test_real_create_replay_history_and_abort(
    mongo,
):
    client, _, collection = mongo

    first = relation()

    with client.start_session() as session:
        with session.start_transaction():
            one = registry.persist_revision(
                first,
                collection=collection,
                session=session,
            )
            replay = registry.persist_revision(
                first,
                collection=collection,
                session=session,
            )

            assert one == first
            assert replay == first

    second = relation(
        revision=2,
        previous=first,
        status=WorkforceRelationshipStatus.SUSPENDED,
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist_revision(
                second,
                collection=collection,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            values = registry.list_history(
                "TENANT",
                "tenant-real",
                "rel-001",
                collection=collection,
                session=session,
            )

            assert values == (
                first,
                second,
            )

    aborted = relation(
        relationship_id="rel-aborted",
    )

    with client.start_session() as session:
        session.start_transaction()

        registry.persist_revision(
            aborted,
            collection=collection,
            session=session,
        )

        session.abort_transaction()

    assert (
        collection.count_documents(
            {
                "relationship_id":
                    "rel-aborted"
            }
        )
        == 0
    )


def test_real_corruption_fails_closed(
    mongo,
):
    client, _, collection = mongo
    first = relation()

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist_revision(
                first,
                collection=collection,
                session=session,
            )

    collection.update_one(
        {
            "relationship_id":
                first.relationship_id,
            "revision": 1,
        },
        {
            "$set": {
                "principal_id":
                    "tampered-principal",
            }
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.WorkforceRelationshipRegistryPersistedRecordInvalidError
            ):
                registry.get_revision(
                    "TENANT",
                    "tenant-real",
                    "rel-001",
                    1,
                    collection=collection,
                    session=session,
                )


def test_real_cross_scope_isolation(
    mongo,
):
    client, _, collection = mongo

    tenant = relation(
        relationship_id="same-id",
    )

    platform = WorkforceRelationship(
        relationship_id="same-id",
        revision=1,
        scope_kind=WorkforceScopeKind.PLATFORM,
        scope_id="wilsy-platform",
        principal_id="principal-real",
        relationship_type=(
            WorkforceRelationshipType.EMPLOYEE
        ),
        status=WorkforceRelationshipStatus.ACTIVE,
        effective_from=AT,
        effective_until=None,
        status_effective_at=AT,
        reason_reference="platform",
        supersedes_fingerprint=None,
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist_revision(
                tenant,
                collection=collection,
                session=session,
            )
            registry.persist_revision(
                platform,
                collection=collection,
                session=session,
            )

    assert (
        collection.count_documents(
            {"relationship_id": "same-id"}
        )
        == 2
    )


def test_real_competing_same_next_revision_one_admitted(
    mongo,
):
    client, _, collection = mongo

    first = relation(
        relationship_id="race",
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist_revision(
                first,
                collection=collection,
                session=session,
            )

    candidate = relation(
        relationship_id="race",
        revision=2,
        previous=first,
        status=WorkforceRelationshipStatus.SUSPENDED,
    )

    def worker():
        with client.start_session() as session:
            try:
                with session.start_transaction():
                    value = registry.persist_revision(
                        candidate,
                        collection=collection,
                        session=session,
                    )
                return (
                    "SUCCESS",
                    value.fingerprint,
                )
            except (
                registry.WorkforceRelationshipRegistryRetryTransactionError,
                registry.WorkforceRelationshipRegistryConflictError,
                PyMongoError,
            ):
                return (
                    "RETRY",
                    None,
                )

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        results = list(
            pool.map(
                lambda _: worker(),
                range(2),
            )
        )

    successes = [
        value
        for value in results
        if value[0] == "SUCCESS"
    ]

    assert len(successes) >= 1

    assert (
        collection.count_documents(
            {
                "relationship_id":
                    "race",
                "revision": 2,
            }
        )
        == 1
    )
