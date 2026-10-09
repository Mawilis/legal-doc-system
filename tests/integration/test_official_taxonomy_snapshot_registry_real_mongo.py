# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN REAL-MONGO CERTIFICATION ARTIFACT
OFFICIAL TAXONOMY SNAPSHOT REGISTRY
===============================================================================

TITLE:
    WILSY OS Official Taxonomy Snapshot Registry Real Mongo Certificate

VERSION:
    v1.0.0-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-REAL-MONGO-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Certifies immutable OfficialTaxonomySnapshot persistence against a real
    loopback MongoDB replica set with UUID-isolated database state.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_official_taxonomy_snapshot_registry_real_mongo.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.0-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-REAL-MONGO-TEST
        - Certifies exact Mongo index metadata.
        - Certifies absence of TTL deletion indexes.
        - Certifies caller-owned active transaction requirement.
        - Certifies commit durability and abort-zero-write semantics.
        - Certifies strict hydration and corrupt-row rejection.
        - Certifies immutable exact replay behavior against real unique indexes.
        - Certifies conflicting identity rejection.
        - Certifies competing identical and conflicting consumer behavior.

DATABASE BOUNDARY:
    Disposable UUID-named database on loopback replica set only.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
===============================================================================
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import hashlib
import uuid
from typing import Iterator

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import (
    OperationFailure,
    PyMongoError,
)

from tools.eos.saas.domain.official_taxonomy_snapshot import (
    OfficialTaxonomyArtifactKind,
    OfficialTaxonomySnapshot,
    OfficialTaxonomySourceArtifact,
)

from tools.eos.saas.official_taxonomy_snapshot_registry import (
    COLLECTION_NAME,
    OfficialTaxonomySnapshotRegistry,
    OfficialTaxonomySnapshotRegistryError,
)


MONGO_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)


def sha(value: bytes) -> str:
    return hashlib.sha3_512(
        value
    ).hexdigest()


def artifact(
    artifact_id: str = "STRUCTURE",
) -> OfficialTaxonomySourceArtifact:
    return OfficialTaxonomySourceArtifact(
        artifact_id=artifact_id,
        kind=OfficialTaxonomyArtifactKind.STRUCTURE,
        source_reference=(
            "https://example.invalid/"
            + artifact_id.lower()
            + ".csv"
        ),
        media_type="text/csv",
        language_tag="en",
        source_digest=sha(
            artifact_id.encode("utf-8")
        ),
        size_bytes=123,
        retrieved_at=datetime(
            2026,
            10,
            8,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        rights_reference="official publisher terms",
    )


def snapshot(
    *,
    snapshot_id: str = "SNAPSHOT-1",
    scheme_version: str = "REV5",
    publisher_status: str = "official",
    supersedes_snapshot_id: str | None = None,
) -> OfficialTaxonomySnapshot:
    return OfficialTaxonomySnapshot(
        snapshot_id=snapshot_id,
        scheme_id="ISIC",
        scheme_version=scheme_version,
        publisher="United Nations",
        jurisdiction="GLOBAL",
        publisher_status=publisher_status,
        release_date=date(2025, 1, 1),
        effective_from=date(2025, 1, 1),
        effective_until=None,
        ingested_at=datetime(
            2026,
            10,
            8,
            0,
            1,
            tzinfo=timezone.utc,
        ),
        source_artifacts=(artifact(),),
        supersedes_snapshot_id=supersedes_snapshot_id,
    )


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient,
        Database,
        Collection,
        OfficialTaxonomySnapshotRegistry,
    ]
]:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    client.admin.command("ping")

    database_name = (
        "wilsy_taxonomy_snapshot_cert_"
        + uuid.uuid4().hex
    )

    database = client[
        database_name
    ]

    collection = database[
        COLLECTION_NAME
    ]

    registry = OfficialTaxonomySnapshotRegistry(
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
            database_name
        )
        client.close()


def test_real_index_metadata_and_no_ttl(
    mongo_context,
) -> None:
    _, _, collection, _ = mongo_context

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    id_index = indexes[
        "official_taxonomy_snapshot_id_unique"
    ]

    digest_index = indexes[
        "official_taxonomy_snapshot_digest_unique"
    ]

    coordinate_index = indexes[
        "official_taxonomy_scheme_version_jurisdiction"
    ]

    supersession_index = indexes[
        "official_taxonomy_supersedes_snapshot"
    ]

    assert id_index["key"] == {
        "snapshot_id": 1,
    }

    assert id_index["unique"] is True

    assert digest_index["key"] == {
        "snapshot_digest": 1,
    }

    assert digest_index["unique"] is True

    assert coordinate_index["key"] == {
        "scheme_id": 1,
        "scheme_version": 1,
        "jurisdiction": 1,
    }

    assert supersession_index["key"] == {
        "supersedes_snapshot_id": 1,
    }

    for item in indexes.values():
        assert (
            "expireAfterSeconds"
            not in item
        )


def test_real_missing_or_inactive_transaction_rejected_before_write(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context

    expected = snapshot()

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        registry.create(
            expected,
            session=None,
        )

    with client.start_session() as session:
        assert session.in_transaction is False

        with pytest.raises(
            OfficialTaxonomySnapshotRegistryError
        ):
            registry.create(
                expected,
                session=session,
            )

    assert collection.count_documents(
        {}
    ) == 0


def test_real_commit_is_durable_and_hydrates_exactly(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context

    expected = snapshot()

    with client.start_session() as session:
        with session.start_transaction():
            created = registry.create(
                expected,
                session=session,
            )

            assert created == expected

    assert collection.count_documents(
        {}
    ) == 1

    observed = registry.get(
        expected.snapshot_id
    )

    assert observed == expected

    by_digest = registry.get_by_digest(
        expected.snapshot_digest
    )

    assert by_digest == expected


def test_real_aborted_transaction_leaves_zero_write(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context

    expected = snapshot()

    with client.start_session() as session:
        session.start_transaction()

        registry.create(
            expected,
            session=session,
        )

        assert session.in_transaction is True

        session.abort_transaction()

    assert collection.count_documents(
        {}
    ) == 0


def test_real_corrupt_durable_truth_rejected(
    mongo_context,
) -> None:
    _, _, collection, registry = mongo_context

    expected = snapshot()

    document = expected.to_dict()
    document[
        "snapshot_digest"
    ] = "0" * 128

    collection.insert_one(
        document
    )

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        registry.get(
            expected.snapshot_id
        )


def test_real_read_indexes_and_supersession_are_read_only(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context

    first = snapshot(
        snapshot_id="S1",
        scheme_version="REV4",
    )

    second = snapshot(
        snapshot_id="S2",
        scheme_version="REV5",
        supersedes_snapshot_id="S1",
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.create(
                first,
                session=session,
            )
            registry.create(
                second,
                session=session,
            )

    before = list(
        collection.find(
            {},
            {
                "_id": 0,
            },
        )
    )

    by_coordinates = (
        registry.get_by_scheme_version_jurisdiction(
            scheme_id="ISIC",
            scheme_version="REV5",
            jurisdiction="GLOBAL",
        )
    )

    superseding = (
        registry.find_superseding_snapshots(
            "S1"
        )
    )

    after = list(
        collection.find(
            {},
            {
                "_id": 0,
            },
        )
    )

    assert by_coordinates == (
        second,
    )

    assert superseding == (
        second,
    )

    assert after == before


def test_real_exact_replay_idempotence(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context

    expected = snapshot()

    with client.start_session() as first_session:
        with first_session.start_transaction():
            first = registry.create(
                expected,
                session=first_session,
            )

    assert first == expected
    assert collection.count_documents(
        {}
    ) == 1

    with client.start_session() as replay_session:
        with replay_session.start_transaction():
            replay = registry.create(
                expected,
                session=replay_session,
            )

    assert replay == expected

    assert collection.count_documents(
        {}
    ) == 1


def test_real_same_identity_different_truth_is_rejected(
    mongo_context,
) -> None:
    client, _, collection, registry = mongo_context

    first = snapshot()

    conflicting = snapshot(
        publisher_status="corrected official",
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.create(
                first,
                session=session,
            )

    with client.start_session() as session:
        with pytest.raises(
            (
                OfficialTaxonomySnapshotRegistryError,
                PyMongoError,
            )
        ):
            with session.start_transaction():
                registry.create(
                    conflicting,
                    session=session,
                )

    assert collection.count_documents(
        {}
    ) == 1

    observed = registry.get(
        first.snapshot_id
    )

    assert observed == first


def test_real_competing_identical_consumers_converge_to_one_truth(
    mongo_context,
) -> None:
    _, database, collection, _ = mongo_context

    expected = snapshot()

    def consumer() -> str:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            uuidRepresentation="standard",
        )

        try:
            registry = OfficialTaxonomySnapshotRegistry(
                client[
                    database.name
                ][
                    COLLECTION_NAME
                ]
            )

            with client.start_session() as session:
                try:
                    with session.start_transaction():
                        value = registry.create(
                            expected,
                            session=session,
                        )

                    return (
                        "SUCCESS:"
                        + value.snapshot_digest
                    )

                except (
                    OfficialTaxonomySnapshotRegistryError,
                    PyMongoError,
                ) as error:
                    return (
                        "ERROR:"
                        + type(error).__name__
                    )
        finally:
            client.close()

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        results = tuple(
            pool.map(
                lambda _index: consumer(),
                range(2),
            )
        )

    assert collection.count_documents(
        {}
    ) == 1

    observed = OfficialTaxonomySnapshotRegistry(
        collection
    ).get(
        expected.snapshot_id
    )

    assert observed == expected

    assert any(
        item.startswith(
            "SUCCESS:"
        )
        for item in results
    )


def test_real_competing_conflicting_consumers_preserve_one_truth(
    mongo_context,
) -> None:
    _, database, collection, _ = mongo_context

    first = snapshot(
        publisher_status="official-A",
    )

    second = snapshot(
        publisher_status="official-B",
    )

    def consumer(
        candidate: OfficialTaxonomySnapshot,
    ) -> str:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            uuidRepresentation="standard",
        )

        try:
            registry = OfficialTaxonomySnapshotRegistry(
                client[
                    database.name
                ][
                    COLLECTION_NAME
                ]
            )

            with client.start_session() as session:
                try:
                    with session.start_transaction():
                        value = registry.create(
                            candidate,
                            session=session,
                        )

                    return (
                        "SUCCESS:"
                        + value.publisher_status
                    )

                except (
                    OfficialTaxonomySnapshotRegistryError,
                    PyMongoError,
                ) as error:
                    return (
                        "ERROR:"
                        + type(error).__name__
                    )
        finally:
            client.close()

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        futures = (
            pool.submit(
                consumer,
                first,
            ),
            pool.submit(
                consumer,
                second,
            ),
        )

        results = tuple(
            future.result()
            for future in futures
        )

    assert collection.count_documents(
        {}
    ) == 1

    durable = collection.find_one(
        {},
        {
            "_id": 0,
        },
    )

    assert durable is not None

    assert durable[
        "publisher_status"
    ] in {
        "official-A",
        "official-B",
    }

    assert sum(
        item.startswith(
            "SUCCESS:"
        )
        for item in results
    ) == 1


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_official_taxonomy_snapshot_registry_real_mongo.py
# VERSION: v1.0.0-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-REAL-MONGO-TEST
# AUTHORITY BOUNDARY: real-Mongo certification of immutable platform snapshot
# persistence only
# DATABASE BOUNDARY: disposable UUID-isolated loopback replica-set database
# TRANSACTION POSTURE: caller-owned transaction semantics certified
# TTL / DELETION POSTURE: no TTL, update, replace or delete authority
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
