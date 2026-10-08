"""
WILSY OS — Official Taxonomy Hierarchy Registry Real Mongo Certificate

TITLE:
    WILSY OS Official Taxonomy Hierarchy Registry Real Mongo Certificate

VERSION:
    v1.0.2-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY-REAL-MONGO-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Certifies immutable OfficialTaxonomyHierarchy persistence against a real
    loopback MongoDB replica set using UUID-isolated disposable databases and
    authoritative SnapshotRegistry dependencies.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_official_taxonomy_hierarchy_registry_real_mongo.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.2-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY-REAL-MONGO-TEST
        - Aligns competing-identical semantics with the already-certified
          SnapshotRegistry precedent and hierarchy exact-replay contract.
        - Identical consumers may both succeed through exact idempotent replay,
          or one may lose the insert race; exactly one durable identical truth
          is the invariant.
        - Preserves exactly-one-success semantics for competing conflicting
          consumers.
        - Preserves the fifteen-test real-Mongo certificate matrix.

    v1.0.1-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY-REAL-MONGO-TEST
        - Corrected SnapshotRegistry setup to instantiate the registry before
          invoking its instance-owned ensure_indexes() method.

DATABASE BOUNDARY:
    Disposable UUID-named database on loopback replica set only.

TENANT BOUNDARY:
    Platform reference truth only. No tenant authority.

NETWORK BOUNDARY:
    Loopback MongoDB only. No public network access or remote taxonomy fetch.

FINANCIAL AUTHORITY BOUNDARY:
    None.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import hashlib
from threading import Barrier
from typing import Any
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.saas.domain.official_taxonomy_hierarchy import (
    OfficialTaxonomyCategory,
    OfficialTaxonomyCategoryText,
    OfficialTaxonomyHierarchy,
    OfficialTaxonomyHierarchyLevel,
)
from tools.eos.saas.domain.official_taxonomy_snapshot import (
    OfficialTaxonomyArtifactKind,
    OfficialTaxonomySnapshot,
    OfficialTaxonomySourceArtifact,
)
from tools.eos.saas.official_taxonomy_hierarchy_registry import (
    COLLECTION_NAME as HIERARCHY_COLLECTION,
    OfficialTaxonomyHierarchyRegistry,
    OfficialTaxonomyHierarchyRegistryError,
)
from tools.eos.saas.official_taxonomy_snapshot_registry import (
    COLLECTION_NAME as SNAPSHOT_COLLECTION,
    OfficialTaxonomySnapshotRegistry,
)


MONGO_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)


class CountingSnapshotRegistry:
    """Observe authoritative Snapshot reads while delegating to real Mongo."""

    def __init__(
        self,
        delegate: OfficialTaxonomySnapshotRegistry,
    ) -> None:
        self.delegate = delegate
        self.get_calls = 0
        self.digest_calls = 0

    def get(
        self,
        snapshot_id: str,
        *,
        session: Any | None = None,
    ) -> OfficialTaxonomySnapshot | None:
        self.get_calls += 1
        return self.delegate.get(
            snapshot_id,
            session=session,
        )

    def get_by_digest(
        self,
        snapshot_digest: str,
        *,
        session: Any | None = None,
    ) -> OfficialTaxonomySnapshot | None:
        self.digest_calls += 1
        return self.delegate.get_by_digest(
            snapshot_digest,
            session=session,
        )


def source_artifact(
    artifact_id: str,
) -> OfficialTaxonomySourceArtifact:
    """Build one deterministic admitted source artifact."""
    return OfficialTaxonomySourceArtifact(
        artifact_id=artifact_id,
        kind=next(
            iter(
                OfficialTaxonomyArtifactKind
            )
        ),
        source_reference=(
            "https://example.invalid/"
            + artifact_id.lower()
        ),
        media_type="text/csv",
        language_tag="en",
        source_digest=hashlib.sha3_512(
            artifact_id.encode(
                "utf-8"
            )
        ).hexdigest(),
        size_bytes=100,
        retrieved_at=datetime(
            2026,
            10,
            8,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        rights_reference=(
            "official publisher terms"
        ),
    )


def snapshot(
    *,
    snapshot_id: str = "SNAPSHOT-1",
    artifact_ids: tuple[str, ...] = (
        "STRUCTURE",
        "NOTES",
    ),
) -> OfficialTaxonomySnapshot:
    """Build one authoritative Snapshot aggregate."""
    return OfficialTaxonomySnapshot(
        snapshot_id=snapshot_id,
        scheme_id="ISIC",
        scheme_version="REV5",
        publisher="United Nations",
        jurisdiction="GLOBAL",
        publisher_status="official",
        release_date=date(
            2025,
            1,
            1,
        ),
        effective_from=date(
            2025,
            1,
            1,
        ),
        effective_until=None,
        ingested_at=datetime(
            2026,
            10,
            8,
            0,
            1,
            tzinfo=timezone.utc,
        ),
        source_artifacts=tuple(
            source_artifact(
                artifact_id
            )
            for artifact_id in artifact_ids
        ),
        supersedes_snapshot_id=None,
    )


def hierarchy(
    bound_snapshot: OfficialTaxonomySnapshot,
    *,
    hierarchy_id: str = "HIERARCHY-1",
    root_title: str = "Root",
) -> OfficialTaxonomyHierarchy:
    """Build one graph-valid hierarchy exactly bound to one Snapshot."""
    root_text = OfficialTaxonomyCategoryText(
        language_tag="en",
        title=root_title,
        definition=None,
        explanatory_notes=(),
        inclusions=(),
        exclusions=(),
        source_artifact_refs=(
            "STRUCTURE",
        ),
    )

    child_text = OfficialTaxonomyCategoryText(
        language_tag="en",
        title="Division",
        definition=None,
        explanatory_notes=(),
        inclusions=(),
        exclusions=(),
        source_artifact_refs=(
            "NOTES",
        ),
    )

    levels = (
        OfficialTaxonomyHierarchyLevel(
            level_id="SECTION",
            rank=0,
            title="Section",
            source_artifact_refs=(
                "STRUCTURE",
            ),
        ),
        OfficialTaxonomyHierarchyLevel(
            level_id="DIVISION",
            rank=1,
            title="Division",
            source_artifact_refs=(
                "STRUCTURE",
            ),
        ),
    )

    categories = (
        OfficialTaxonomyCategory(
            category_id="CAT-A",
            level_id="SECTION",
            code="A",
            parent_category_id=None,
            terminal=False,
            source_artifact_refs=(
                "STRUCTURE",
            ),
            texts=(
                root_text,
            ),
        ),
        OfficialTaxonomyCategory(
            category_id="CAT-01",
            level_id="DIVISION",
            code="01",
            parent_category_id="CAT-A",
            terminal=True,
            source_artifact_refs=(
                "NOTES",
            ),
            texts=(
                child_text,
            ),
        ),
    )

    return OfficialTaxonomyHierarchy(
        hierarchy_id=hierarchy_id,
        snapshot_id=bound_snapshot.snapshot_id,
        snapshot_digest=bound_snapshot.snapshot_digest,
        scheme_id=bound_snapshot.scheme_id,
        scheme_version=bound_snapshot.scheme_version,
        jurisdiction=bound_snapshot.jurisdiction,
        source_artifact_refs=(
            "STRUCTURE",
            "NOTES",
        ),
        levels=levels,
        categories=categories,
    )


@pytest.fixture
def mongo_context() -> Any:
    """Provide one UUID-isolated real-Mongo registry context per test."""
    client: Any = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    client.admin.command(
        "ping"
    )

    database_name = (
        "wilsy_taxonomy_hierarchy_cert_"
        + uuid.uuid4().hex
    )

    database = client[
        database_name
    ]

    snapshot_collection = database[
        SNAPSHOT_COLLECTION
    ]

    hierarchy_collection = database[
        HIERARCHY_COLLECTION
    ]

    snapshot_registry = (
        OfficialTaxonomySnapshotRegistry(
            snapshot_collection
        )
    )

    snapshot_registry.ensure_indexes()

    OfficialTaxonomyHierarchyRegistry.ensure_indexes(
        hierarchy_collection
    )

    hierarchy_registry = (
        OfficialTaxonomyHierarchyRegistry(
            hierarchy_collection,
            snapshot_registry=snapshot_registry,
        )
    )

    try:
        yield (
            client,
            database,
            snapshot_collection,
            hierarchy_collection,
            snapshot_registry,
            hierarchy_registry,
        )
    finally:
        client.drop_database(
            database_name
        )
        client.close()


def persist_snapshot(
    client: Any,
    registry: OfficialTaxonomySnapshotRegistry,
    value: OfficialTaxonomySnapshot,
) -> None:
    """Commit one authoritative Snapshot before hierarchy operations."""
    with client.start_session() as session:
        with session.start_transaction():
            registry.create(
                value,
                session=session,
            )


def persist_hierarchy(
    client: Any,
    registry: OfficialTaxonomyHierarchyRegistry,
    value: OfficialTaxonomyHierarchy,
) -> None:
    """Commit one hierarchy through the production registry."""
    with client.start_session() as session:
        with session.start_transaction():
            registry.create(
                value,
                session=session,
            )


def test_real_index_metadata_and_no_ttl(
    mongo_context: Any,
) -> None:
    (
        _client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        _snapshot_registry,
        _hierarchy_registry,
    ) = mongo_context

    indexes = {
        entry["name"]: entry
        for entry in hierarchy_collection.list_indexes()
    }

    identity = indexes[
        "official_taxonomy_hierarchy_id_unique"
    ]

    assert list(
        identity["key"].items()
    ) == [
        (
            "hierarchy_id",
            1,
        ),
    ]
    assert identity["unique"] is True

    digest = indexes[
        "official_taxonomy_hierarchy_digest_unique"
    ]

    assert list(
        digest["key"].items()
    ) == [
        (
            "hierarchy_digest",
            1,
        ),
    ]
    assert digest["unique"] is True

    binding = indexes[
        "official_taxonomy_hierarchy_snapshot_binding"
    ]

    assert list(
        binding["key"].items()
    ) == [
        (
            "snapshot_id",
            1,
        ),
        (
            "snapshot_digest",
            1,
        ),
    ]
    assert not binding.get(
        "unique",
        False,
    )

    coordinates = indexes[
        "official_taxonomy_hierarchy_scheme_version_jurisdiction"
    ]

    assert list(
        coordinates["key"].items()
    ) == [
        (
            "scheme_id",
            1,
        ),
        (
            "scheme_version",
            1,
        ),
        (
            "jurisdiction",
            1,
        ),
    ]

    assert not coordinates.get(
        "unique",
        False,
    )

    for entry in indexes.values():
        assert (
            "expireAfterSeconds"
            not in entry
        )


def test_real_missing_session_rejected_before_snapshot_read_or_write(
    mongo_context: Any,
) -> None:
    (
        _client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        _hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()
    candidate = hierarchy(
        authoritative
    )

    counting = CountingSnapshotRegistry(
        snapshot_registry
    )

    registry = OfficialTaxonomyHierarchyRegistry(
        hierarchy_collection,
        snapshot_registry=counting,
    )

    with pytest.raises(
        OfficialTaxonomyHierarchyRegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create(
            candidate,
            session=None,
        )

    assert counting.get_calls == 0
    assert counting.digest_calls == 0

    assert hierarchy_collection.count_documents(
        {}
    ) == 0


def test_real_inactive_transaction_rejected_before_snapshot_read_or_write(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        _hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()
    candidate = hierarchy(
        authoritative
    )

    counting = CountingSnapshotRegistry(
        snapshot_registry
    )

    registry = OfficialTaxonomyHierarchyRegistry(
        hierarchy_collection,
        snapshot_registry=counting,
    )

    with client.start_session() as session:
        assert not session.in_transaction

        with pytest.raises(
            OfficialTaxonomyHierarchyRegistryError,
            match="ACTIVE_TRANSACTION_REQUIRED",
        ):
            registry.create(
                candidate,
                session=session,
            )

    assert counting.get_calls == 0
    assert counting.digest_calls == 0

    assert hierarchy_collection.count_documents(
        {}
    ) == 0


def test_real_committed_snapshot_then_hierarchy_roundtrip(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = hierarchy(
        authoritative
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        candidate,
    )

    assert hierarchy_collection.count_documents(
        {}
    ) == 1

    assert (
        hierarchy_registry.get(
            candidate.hierarchy_id
        )
        == candidate
    )

    assert (
        hierarchy_registry.get_by_digest(
            candidate.hierarchy_digest
        )
        == candidate
    )


def test_real_aborted_hierarchy_insert_leaves_zero_hierarchy_rows(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = hierarchy(
        authoritative
    )

    with client.start_session() as session:
        session.start_transaction()

        hierarchy_registry.create(
            candidate,
            session=session,
        )

        assert hierarchy_collection.count_documents(
            {},
            session=session,
        ) == 1

        session.abort_transaction()

    assert hierarchy_collection.count_documents(
        {}
    ) == 0


def test_real_exact_replay_inside_transaction_is_idempotent(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = hierarchy(
        authoritative
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        candidate,
    )

    with client.start_session() as session:
        with session.start_transaction():
            observed = hierarchy_registry.create(
                candidate,
                session=session,
            )

            assert observed == candidate

    assert hierarchy_collection.count_documents(
        {}
    ) == 1


def test_real_same_hierarchy_id_different_truth_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    first = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-SAME",
        root_title="First",
    )

    second = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-SAME",
        root_title="Second",
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        first,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyHierarchyRegistryError,
                match="IDENTITY_CONFLICT",
            ):
                hierarchy_registry.create(
                    second,
                    session=session,
                )

    assert hierarchy_collection.count_documents(
        {}
    ) == 1

    assert (
        hierarchy_registry.get(
            first.hierarchy_id
        )
        == first
    )


def test_real_corrupt_digest_collision_rejected_before_insert(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = hierarchy(
        authoritative
    )

    corrupt = candidate.to_dict()
    corrupt["hierarchy_id"] = (
        "CORRUPT-OTHER-ID"
    )

    hierarchy_collection.insert_one(
        corrupt
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyHierarchyRegistryError,
            ):
                hierarchy_registry.create(
                    candidate,
                    session=session,
                )

    assert hierarchy_collection.count_documents(
        {}
    ) == 1


def test_real_snapshot_binding_missing_rejected_before_hierarchy_insert(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        _snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()
    candidate = hierarchy(
        authoritative
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyHierarchyRegistryError,
                match="SNAPSHOT_BINDING_MISSING",
            ):
                hierarchy_registry.create(
                    candidate,
                    session=session,
                )

    assert hierarchy_collection.count_documents(
        {}
    ) == 0


def test_real_snapshot_binding_corruption_rejected_before_hierarchy_insert(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    snapshot_collection.update_one(
        {
            "snapshot_id":
                authoritative.snapshot_id,
        },
        {
            "$set": {
                "unexpected_corruption":
                    True,
            },
        },
    )

    candidate = hierarchy(
        authoritative
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyHierarchyRegistryError,
            ):
                hierarchy_registry.create(
                    candidate,
                    session=session,
                )

    assert hierarchy_collection.count_documents(
        {}
    ) == 0


def test_real_snapshot_binding_read_surface_returns_exact_rows(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        _hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    first = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-1",
        root_title="First",
    )

    second = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-2",
        root_title="Second",
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        first,
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        second,
    )

    observed = (
        hierarchy_registry.get_by_snapshot_binding(
            authoritative.snapshot_id,
            authoritative.snapshot_digest,
        )
    )

    assert set(
        observed
    ) == {
        first,
        second,
    }


def test_real_scheme_version_jurisdiction_read_surface_returns_exact_rows(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        _hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    first = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-1",
        root_title="First",
    )

    second = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-2",
        root_title="Second",
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        first,
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        second,
    )

    observed = (
        hierarchy_registry.get_by_scheme_version_jurisdiction(
            "ISIC",
            "REV5",
            "GLOBAL",
        )
    )

    assert set(
        observed
    ) == {
        first,
        second,
    }


def test_real_corrupt_persisted_hierarchy_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = hierarchy(
        authoritative
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        candidate,
    )

    hierarchy_collection.update_one(
        {
            "hierarchy_id":
                candidate.hierarchy_id,
        },
        {
            "$set": {
                "unexpected_corruption":
                    True,
            },
        },
    )

    with pytest.raises(
        OfficialTaxonomyHierarchyRegistryError,
    ):
        hierarchy_registry.get(
            candidate.hierarchy_id
        )


def test_real_concurrent_identical_create_results_in_one_durable_truth(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = hierarchy(
        authoritative
    )

    barrier = Barrier(
        2
    )

    def consume() -> tuple[
        str,
        str,
    ]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    barrier.wait(
                        timeout=5
                    )

                    observed = (
                        hierarchy_registry.create(
                            candidate,
                            session=session,
                        )
                    )

                    assert observed == candidate

            return (
                "SUCCESS",
                candidate.hierarchy_digest,
            )
        except Exception as exc:
            return (
                "FAILURE",
                type(exc).__name__,
            )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        results = tuple(
            executor.map(
                lambda _: consume(),
                range(2),
            )
        )

    success_results = tuple(
        result
        for result in results
        if result[0] == "SUCCESS"
    )

    assert len(
        success_results
    ) >= 1

    assert all(
        result[1]
        == candidate.hierarchy_digest
        for result in success_results
    )

    assert hierarchy_collection.count_documents(
        {}
    ) == 1

    durable = hierarchy_registry.get(
        candidate.hierarchy_id
    )

    assert durable == candidate

    assert (
        hierarchy_registry.get_by_digest(
            candidate.hierarchy_digest
        )
        == candidate
    )


def test_real_concurrent_conflicting_create_results_in_one_durable_truth(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        hierarchy_collection,
        snapshot_registry,
        hierarchy_registry,
    ) = mongo_context

    authoritative = snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    first = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-CONFLICT",
        root_title="First",
    )

    second = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-CONFLICT",
        root_title="Second",
    )

    barrier = Barrier(
        2
    )

    def consume(
        candidate: OfficialTaxonomyHierarchy,
    ) -> tuple[
        str,
        str,
    ]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    barrier.wait(
                        timeout=5
                    )

                    hierarchy_registry.create(
                        candidate,
                        session=session,
                    )

            return (
                "SUCCESS",
                candidate.hierarchy_digest,
            )
        except Exception as exc:
            return (
                "FAILURE",
                type(exc).__name__,
            )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        results = tuple(
            executor.map(
                consume,
                (
                    first,
                    second,
                ),
            )
        )

    assert sum(
        result[0] == "SUCCESS"
        for result in results
    ) == 1

    assert sum(
        result[0] == "FAILURE"
        for result in results
    ) == 1

    assert hierarchy_collection.count_documents(
        {}
    ) == 1

    durable = hierarchy_registry.get(
        "HIERARCHY-CONFLICT"
    )

    assert durable in (
        first,
        second,
    )


# ============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# ============================================================================
# VERSION: v1.0.2-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY-REAL-MONGO-TEST
# DATABASE BOUNDARY: disposable UUID-isolated loopback replica-set database.
# AUTHORITY BOUNDARY: immutable hierarchy persistence after durable Snapshot
# resolution and pure-domain binding validation only.
# IDENTICAL CONCURRENCY: one durable truth; successful exact replay allowed.
# CONFLICTING CONCURRENCY: exactly one durable winner.
# TENANT AUTHORITY: none.
# NETWORK AUTHORITY: loopback Mongo only.
# FINANCIAL EXECUTION AUTHORITY: none.
# END OF WILSY OS SOVEREIGN ARTIFACT
