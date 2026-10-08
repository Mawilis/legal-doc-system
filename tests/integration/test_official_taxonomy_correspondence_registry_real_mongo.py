"""
WILSY OS — Official Taxonomy Correspondence Registry Real Mongo Certificate

TITLE:
    WILSY OS Official Taxonomy Correspondence Registry Real Mongo Certificate

VERSION:
    v1.0.1-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY-REAL-MONGO-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Certifies immutable correspondence persistence against real transactional
    MongoDB through the complete authoritative Snapshot -> Hierarchy ->
    Correspondence dependency chain.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_official_taxonomy_correspondence_registry_real_mongo.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.1-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY-REAL-MONGO-TEST
        - Repairs only the disposable database-name prefix so every UUID
          database remains within MongoDB's 63-character namespace limit.
        - Preserves the frozen seventeen-test operational certificate.

DATABASE BOUNDARY:
    Disposable UUID-named database on loopback replica set only.

AUTHORITY BOUNDARY:
    Official taxonomy platform reference truth only.

TENANT BOUNDARY:
    None.

NETWORK BOUNDARY:
    Loopback MongoDB only. No public-network taxonomy acquisition.

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

from tools.eos.saas.domain.official_taxonomy_correspondence import (
    OfficialTaxonomyCorrespondence,
    OfficialTaxonomyCorrespondenceRelation,
)
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
from tools.eos.saas.official_taxonomy_correspondence_registry import (
    COLLECTION_NAME as CORRESPONDENCE_COLLECTION,
    OfficialTaxonomyCorrespondenceRegistry,
    OfficialTaxonomyCorrespondenceRegistryError,
)
from tools.eos.saas.official_taxonomy_hierarchy_registry import (
    COLLECTION_NAME as HIERARCHY_COLLECTION,
    OfficialTaxonomyHierarchyRegistry,
)
from tools.eos.saas.official_taxonomy_snapshot_registry import (
    COLLECTION_NAME as SNAPSHOT_COLLECTION,
    OfficialTaxonomySnapshotRegistry,
)


MONGO_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

DATABASE_PREFIX = (
    "wilsy_taxcorr_cert_"
)


class CountingHierarchyRegistry:
    """Observe dependency reads while delegating to real hierarchy truth."""

    def __init__(
        self,
        delegate: OfficialTaxonomyHierarchyRegistry,
    ) -> None:
        self.delegate = delegate
        self.get_calls = 0
        self.digest_calls = 0

    def get(
        self,
        hierarchy_id: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomyHierarchy | None:
        self.get_calls += 1
        return self.delegate.get(
            hierarchy_id,
            session=session,
        )

    def get_by_digest(
        self,
        hierarchy_digest: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomyHierarchy | None:
        self.digest_calls += 1
        return self.delegate.get_by_digest(
            hierarchy_digest,
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
    snapshot_id: str,
    scheme_version: str,
) -> OfficialTaxonomySnapshot:
    """Build one authoritative snapshot for a specific taxonomy version."""
    return OfficialTaxonomySnapshot(
        snapshot_id=snapshot_id,
        scheme_id="ISIC",
        scheme_version=scheme_version,
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
        source_artifacts=(
            source_artifact(
                snapshot_id
                + "-STRUCTURE"
            ),
            source_artifact(
                snapshot_id
                + "-NOTES"
            ),
        ),
        supersedes_snapshot_id=None,
    )


def hierarchy(
    bound_snapshot: OfficialTaxonomySnapshot,
    *,
    hierarchy_id: str,
    category_prefix: str,
) -> OfficialTaxonomyHierarchy:
    """Build one graph-valid hierarchy exactly bound to one Snapshot."""
    structure_ref = (
        bound_snapshot.source_artifacts[
            0
        ].artifact_id
    )

    notes_ref = (
        bound_snapshot.source_artifacts[
            1
        ].artifact_id
    )

    root_id = (
        category_prefix
        + "-ROOT"
    )
    child_id = (
        category_prefix
        + "-C1"
    )

    root_text = OfficialTaxonomyCategoryText(
        language_tag="en",
        title=(
            category_prefix
            + " Root"
        ),
        definition=None,
        explanatory_notes=(),
        inclusions=(),
        exclusions=(),
        source_artifact_refs=(
            structure_ref,
        ),
    )

    child_text = OfficialTaxonomyCategoryText(
        language_tag="en",
        title=(
            category_prefix
            + " Division"
        ),
        definition=None,
        explanatory_notes=(),
        inclusions=(),
        exclusions=(),
        source_artifact_refs=(
            notes_ref,
        ),
    )

    return OfficialTaxonomyHierarchy(
        hierarchy_id=hierarchy_id,
        snapshot_id=(
            bound_snapshot.snapshot_id
        ),
        snapshot_digest=(
            bound_snapshot.snapshot_digest
        ),
        scheme_id=(
            bound_snapshot.scheme_id
        ),
        scheme_version=(
            bound_snapshot.scheme_version
        ),
        jurisdiction=(
            bound_snapshot.jurisdiction
        ),
        source_artifact_refs=(
            structure_ref,
            notes_ref,
        ),
        levels=(
            OfficialTaxonomyHierarchyLevel(
                level_id="ROOT",
                rank=0,
                title="Root",
                source_artifact_refs=(
                    structure_ref,
                ),
            ),
            OfficialTaxonomyHierarchyLevel(
                level_id="CHILD",
                rank=1,
                title="Child",
                source_artifact_refs=(
                    structure_ref,
                ),
            ),
        ),
        categories=(
            OfficialTaxonomyCategory(
                category_id=root_id,
                level_id="ROOT",
                code="A",
                parent_category_id=None,
                terminal=False,
                source_artifact_refs=(
                    structure_ref,
                ),
                texts=(
                    root_text,
                ),
            ),
            OfficialTaxonomyCategory(
                category_id=child_id,
                level_id="CHILD",
                code="01",
                parent_category_id=(
                    root_id
                ),
                terminal=True,
                source_artifact_refs=(
                    notes_ref,
                ),
                texts=(
                    child_text,
                ),
            ),
        ),
    )


def correspondence(
    source: OfficialTaxonomyHierarchy,
    target: OfficialTaxonomyHierarchy,
    *,
    correspondence_id: str = "CORR-1",
    description: str = (
        "publisher supplied description"
    ),
) -> OfficialTaxonomyCorrespondence:
    """Build one valid set-to-set correspondence."""
    return OfficialTaxonomyCorrespondence(
        correspondence_id=(
            correspondence_id
        ),
        source_hierarchy=source,
        target_hierarchy=target,
        source_artifact_refs=(
            "CORRESPONDENCE",
        ),
        relations=(
            OfficialTaxonomyCorrespondenceRelation(
                relationship_id="R1",
                source_category_ids=(
                    source.categories[
                        1
                    ].category_id,
                ),
                target_category_ids=(
                    target.categories[
                        1
                    ].category_id,
                ),
                publisher_change_type=(
                    "publisher supplied change type"
                ),
                publisher_description=(
                    description
                ),
                source_artifact_refs=(
                    "CORRESPONDENCE",
                ),
            ),
        ),
    )


@pytest.fixture
def mongo_context() -> Any:
    """Provide one UUID-isolated real-Mongo dependency chain per test."""
    client: Any = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    client.admin.command(
        "ping"
    )

    database_name = (
        DATABASE_PREFIX
        + uuid.uuid4().hex
    )

    assert len(
        database_name
    ) <= 63

    database = client[
        database_name
    ]

    snapshot_collection = database[
        SNAPSHOT_COLLECTION
    ]
    hierarchy_collection = database[
        HIERARCHY_COLLECTION
    ]
    correspondence_collection = database[
        CORRESPONDENCE_COLLECTION
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

    OfficialTaxonomyCorrespondenceRegistry.ensure_indexes(
        correspondence_collection
    )

    correspondence_registry = (
        OfficialTaxonomyCorrespondenceRegistry(
            correspondence_collection,
            hierarchy_registry=(
                hierarchy_registry
            ),
        )
    )

    try:
        yield (
            client,
            database,
            snapshot_collection,
            hierarchy_collection,
            correspondence_collection,
            snapshot_registry,
            hierarchy_registry,
            correspondence_registry,
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
    """Commit one snapshot through production persistence."""
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
    """Commit one hierarchy through production persistence."""
    with client.start_session() as session:
        with session.start_transaction():
            registry.create(
                value,
                session=session,
            )


def persist_correspondence(
    client: Any,
    registry: OfficialTaxonomyCorrespondenceRegistry,
    value: OfficialTaxonomyCorrespondence,
) -> None:
    """Commit one correspondence through production persistence."""
    with client.start_session() as session:
        with session.start_transaction():
            registry.create(
                value,
                session=session,
            )


def authoritative_chain(
    mongo_context: Any,
) -> tuple[
    Any,
    OfficialTaxonomySnapshot,
    OfficialTaxonomySnapshot,
    OfficialTaxonomyHierarchy,
    OfficialTaxonomyHierarchy,
    OfficialTaxonomyCorrespondence,
]:
    """Persist source/target Snapshot and Hierarchy truth."""
    (
        client,
        _database,
        _snapshot_collection,
        _hierarchy_collection,
        _correspondence_collection,
        snapshot_registry,
        hierarchy_registry,
        _correspondence_registry,
    ) = mongo_context

    source_snapshot = snapshot(
        snapshot_id="SOURCE-S",
        scheme_version="REV4",
    )

    target_snapshot = snapshot(
        snapshot_id="TARGET-S",
        scheme_version="REV5",
    )

    persist_snapshot(
        client,
        snapshot_registry,
        source_snapshot,
    )

    persist_snapshot(
        client,
        snapshot_registry,
        target_snapshot,
    )

    source_hierarchy = hierarchy(
        source_snapshot,
        hierarchy_id="SOURCE-H",
        category_prefix="SOURCE",
    )

    target_hierarchy = hierarchy(
        target_snapshot,
        hierarchy_id="TARGET-H",
        category_prefix="TARGET",
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        source_hierarchy,
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        target_hierarchy,
    )

    candidate = correspondence(
        source_hierarchy,
        target_hierarchy,
    )

    return (
        client,
        source_snapshot,
        target_snapshot,
        source_hierarchy,
        target_hierarchy,
        candidate,
    )


def test_real_index_metadata_and_no_ttl(
    mongo_context: Any,
) -> None:
    (
        _client,
        _database,
        _snapshot_collection,
        _hierarchy_collection,
        correspondence_collection,
        _snapshot_registry,
        _hierarchy_registry,
        _correspondence_registry,
    ) = mongo_context

    indexes = {
        entry["name"]: entry
        for entry in correspondence_collection.list_indexes()
    }

    identity = indexes[
        "official_taxonomy_correspondence_id_unique"
    ]

    assert list(
        identity["key"].items()
    ) == [
        (
            "correspondence_id",
            1,
        ),
    ]
    assert identity[
        "unique"
    ] is True

    digest = indexes[
        "official_taxonomy_correspondence_digest_unique"
    ]

    assert list(
        digest["key"].items()
    ) == [
        (
            "correspondence_digest",
            1,
        ),
    ]
    assert digest[
        "unique"
    ] is True

    source_binding = indexes[
        "official_taxonomy_correspondence_source_hierarchy_binding"
    ]

    assert list(
        source_binding[
            "key"
        ].items()
    ) == [
        (
            "source_hierarchy_id",
            1,
        ),
        (
            "source_hierarchy_digest",
            1,
        ),
    ]

    assert not source_binding.get(
        "unique",
        False,
    )

    target_binding = indexes[
        "official_taxonomy_correspondence_target_hierarchy_binding"
    ]

    assert list(
        target_binding[
            "key"
        ].items()
    ) == [
        (
            "target_hierarchy_id",
            1,
        ),
        (
            "target_hierarchy_digest",
            1,
        ),
    ]

    assert not target_binding.get(
        "unique",
        False,
    )

    for entry in indexes.values():
        assert (
            "expireAfterSeconds"
            not in entry
        )


def test_real_missing_session_rejected_before_hierarchy_read_or_write(
    mongo_context: Any,
) -> None:
    (
        _client,
        _source_snapshot,
        _target_snapshot,
        _source,
        _target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    correspondence_collection = (
        mongo_context[
            4
        ]
    )

    hierarchy_registry = (
        mongo_context[
            6
        ]
    )

    counting = CountingHierarchyRegistry(
        hierarchy_registry
    )

    registry = OfficialTaxonomyCorrespondenceRegistry(
        correspondence_collection,
        hierarchy_registry=counting,
    )

    with pytest.raises(
        OfficialTaxonomyCorrespondenceRegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create(
            candidate,
            session=None,
        )

    assert counting.get_calls == 0
    assert counting.digest_calls == 0

    assert correspondence_collection.count_documents(
        {}
    ) == 0


def test_real_inactive_transaction_rejected_before_hierarchy_read_or_write(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        _source,
        _target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    correspondence_collection = (
        mongo_context[
            4
        ]
    )

    hierarchy_registry = (
        mongo_context[
            6
        ]
    )

    counting = CountingHierarchyRegistry(
        hierarchy_registry
    )

    registry = OfficialTaxonomyCorrespondenceRegistry(
        correspondence_collection,
        hierarchy_registry=counting,
    )

    with client.start_session() as session:
        assert not session.in_transaction

        with pytest.raises(
            OfficialTaxonomyCorrespondenceRegistryError,
            match="ACTIVE_TRANSACTION_REQUIRED",
        ):
            registry.create(
                candidate,
                session=session,
            )

    assert counting.get_calls == 0
    assert counting.digest_calls == 0

    assert correspondence_collection.count_documents(
        {}
    ) == 0


def test_real_committed_snapshot_hierarchy_correspondence_roundtrip(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        _source,
        _target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    registry = mongo_context[
        7
    ]

    persist_correspondence(
        client,
        registry,
        candidate,
    )

    assert (
        registry.get(
            candidate.correspondence_id
        )
        == candidate
    )

    assert (
        registry.get_by_digest(
            candidate.correspondence_digest
        )
        == candidate
    )


def test_real_aborted_correspondence_insert_leaves_zero_correspondence_rows(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        _source,
        _target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    collection = mongo_context[
        4
    ]
    registry = mongo_context[
        7
    ]

    with client.start_session() as session:
        session.start_transaction()

        registry.create(
            candidate,
            session=session,
        )

        assert collection.count_documents(
            {},
            session=session,
        ) == 1

        session.abort_transaction()

    assert collection.count_documents(
        {}
    ) == 0


def test_real_exact_replay_inside_transaction_is_idempotent(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        _source,
        _target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    collection = mongo_context[
        4
    ]
    registry = mongo_context[
        7
    ]

    persist_correspondence(
        client,
        registry,
        candidate,
    )

    with client.start_session() as session:
        with session.start_transaction():
            observed = registry.create(
                candidate,
                session=session,
            )

            assert observed == candidate

    assert collection.count_documents(
        {}
    ) == 1


def test_real_same_correspondence_id_different_truth_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        source,
        target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    registry = mongo_context[
        7
    ]
    collection = mongo_context[
        4
    ]

    conflicting = correspondence(
        source,
        target,
        correspondence_id=(
            candidate.correspondence_id
        ),
        description=(
            "different publisher supplied description"
        ),
    )

    assert (
        conflicting.correspondence_digest
        != candidate.correspondence_digest
    )

    persist_correspondence(
        client,
        registry,
        conflicting,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyCorrespondenceRegistryError,
                match="IDENTITY_CONFLICT",
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert collection.count_documents(
        {}
    ) == 1


def test_real_corrupt_digest_collision_rejected_before_insert(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        _source,
        _target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    collection = mongo_context[
        4
    ]
    registry = mongo_context[
        7
    ]

    corrupt = candidate.to_dict()
    corrupt[
        "correspondence_id"
    ] = "CORR-CORRUPT"

    collection.insert_one(
        corrupt
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyCorrespondenceRegistryError,
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert collection.count_documents(
        {}
    ) == 1


def test_real_missing_source_hierarchy_binding_rejected_before_insert(
    mongo_context: Any,
) -> None:
    client = mongo_context[
        0
    ]
    collection = mongo_context[
        4
    ]
    snapshot_registry = mongo_context[
        5
    ]
    hierarchy_registry = mongo_context[
        6
    ]
    registry = mongo_context[
        7
    ]

    source_snapshot = snapshot(
        snapshot_id="SOURCE-S",
        scheme_version="REV4",
    )

    target_snapshot = snapshot(
        snapshot_id="TARGET-S",
        scheme_version="REV5",
    )

    persist_snapshot(
        client,
        snapshot_registry,
        target_snapshot,
    )

    source = hierarchy(
        source_snapshot,
        hierarchy_id="SOURCE-H",
        category_prefix="SOURCE",
    )

    target = hierarchy(
        target_snapshot,
        hierarchy_id="TARGET-H",
        category_prefix="TARGET",
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        target,
    )

    candidate = correspondence(
        source,
        target,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyCorrespondenceRegistryError,
                match="SOURCE_HIERARCHY_BINDING_MISSING",
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert collection.count_documents(
        {}
    ) == 0


def test_real_missing_target_hierarchy_binding_rejected_before_insert(
    mongo_context: Any,
) -> None:
    client = mongo_context[
        0
    ]
    collection = mongo_context[
        4
    ]
    snapshot_registry = mongo_context[
        5
    ]
    hierarchy_registry = mongo_context[
        6
    ]
    registry = mongo_context[
        7
    ]

    source_snapshot = snapshot(
        snapshot_id="SOURCE-S",
        scheme_version="REV4",
    )

    target_snapshot = snapshot(
        snapshot_id="TARGET-S",
        scheme_version="REV5",
    )

    persist_snapshot(
        client,
        snapshot_registry,
        source_snapshot,
    )

    source = hierarchy(
        source_snapshot,
        hierarchy_id="SOURCE-H",
        category_prefix="SOURCE",
    )

    target = hierarchy(
        target_snapshot,
        hierarchy_id="TARGET-H",
        category_prefix="TARGET",
    )

    persist_hierarchy(
        client,
        hierarchy_registry,
        source,
    )

    candidate = correspondence(
        source,
        target,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyCorrespondenceRegistryError,
                match="TARGET_HIERARCHY_BINDING_MISSING",
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert collection.count_documents(
        {}
    ) == 0


def test_real_corrupt_source_hierarchy_binding_rejected_before_insert(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        source,
        _target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    hierarchy_collection = mongo_context[
        3
    ]
    collection = mongo_context[
        4
    ]
    registry = mongo_context[
        7
    ]

    hierarchy_collection.update_one(
        {
            "hierarchy_id":
                source.hierarchy_id,
        },
        {
            "$set": {
                "unexpected_corruption":
                    True,
            },
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyCorrespondenceRegistryError,
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert collection.count_documents(
        {}
    ) == 0


def test_real_corrupt_target_hierarchy_binding_rejected_before_insert(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        _source,
        target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    hierarchy_collection = mongo_context[
        3
    ]
    collection = mongo_context[
        4
    ]
    registry = mongo_context[
        7
    ]

    hierarchy_collection.update_one(
        {
            "hierarchy_id":
                target.hierarchy_id,
        },
        {
            "$set": {
                "unexpected_corruption":
                    True,
            },
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                OfficialTaxonomyCorrespondenceRegistryError,
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert collection.count_documents(
        {}
    ) == 0


def test_real_source_hierarchy_binding_read_surface_returns_exact_rows(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        source,
        target,
        first,
    ) = authoritative_chain(
        mongo_context
    )

    registry = mongo_context[
        7
    ]

    second = correspondence(
        source,
        target,
        correspondence_id="CORR-2",
        description="second mapping",
    )

    persist_correspondence(
        client,
        registry,
        first,
    )

    persist_correspondence(
        client,
        registry,
        second,
    )

    observed = (
        registry.get_by_source_hierarchy_binding(
            source.hierarchy_id,
            source.hierarchy_digest,
        )
    )

    assert {
        value.correspondence_id
        for value in observed
    } == {
        "CORR-1",
        "CORR-2",
    }


def test_real_target_hierarchy_binding_read_surface_returns_exact_rows(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        source,
        target,
        first,
    ) = authoritative_chain(
        mongo_context
    )

    registry = mongo_context[
        7
    ]

    second = correspondence(
        source,
        target,
        correspondence_id="CORR-2",
        description="second mapping",
    )

    persist_correspondence(
        client,
        registry,
        first,
    )

    persist_correspondence(
        client,
        registry,
        second,
    )

    observed = (
        registry.get_by_target_hierarchy_binding(
            target.hierarchy_id,
            target.hierarchy_digest,
        )
    )

    assert {
        value.correspondence_id
        for value in observed
    } == {
        "CORR-1",
        "CORR-2",
    }


def test_real_corrupt_persisted_correspondence_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        _source,
        _target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    collection = mongo_context[
        4
    ]
    registry = mongo_context[
        7
    ]

    persist_correspondence(
        client,
        registry,
        candidate,
    )

    collection.update_one(
        {
            "correspondence_id":
                candidate.correspondence_id,
        },
        {
            "$set": {
                "unexpected_corruption":
                    True,
            },
        },
    )

    with pytest.raises(
        OfficialTaxonomyCorrespondenceRegistryError,
    ):
        registry.get(
            candidate.correspondence_id
        )


def test_real_concurrent_identical_create_converges_to_one_durable_truth(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        _source,
        _target,
        candidate,
    ) = authoritative_chain(
        mongo_context
    )

    collection = mongo_context[
        4
    ]
    registry = mongo_context[
        7
    ]

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

                    observed = registry.create(
                        candidate,
                        session=session,
                    )

                    assert (
                        observed
                        == candidate
                    )

            return (
                "SUCCESS",
                candidate.correspondence_digest,
            )
        except Exception as exc:
            return (
                "FAILURE",
                type(
                    exc
                ).__name__,
            )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        results = tuple(
            executor.map(
                lambda _: consume(),
                range(
                    2
                ),
            )
        )

    successes = tuple(
        item
        for item in results
        if item[
            0
        ] == "SUCCESS"
    )

    assert len(
        successes
    ) >= 1

    assert all(
        item[
            1
        ] == candidate.correspondence_digest
        for item in successes
    )

    assert collection.count_documents(
        {}
    ) == 1

    assert (
        registry.get(
            candidate.correspondence_id
        )
        == candidate
    )


def test_real_concurrent_conflicting_create_results_in_one_durable_truth(
    mongo_context: Any,
) -> None:
    (
        client,
        _source_snapshot,
        _target_snapshot,
        source,
        target,
        first,
    ) = authoritative_chain(
        mongo_context
    )

    second = correspondence(
        source,
        target,
        correspondence_id=(
            first.correspondence_id
        ),
        description=(
            "conflicting concurrent truth"
        ),
    )

    assert (
        second.correspondence_digest
        != first.correspondence_digest
    )

    collection = mongo_context[
        4
    ]
    registry = mongo_context[
        7
    ]

    barrier = Barrier(
        2
    )

    def consume(
        candidate: OfficialTaxonomyCorrespondence,
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

                    registry.create(
                        candidate,
                        session=session,
                    )

            return (
                "SUCCESS",
                candidate.correspondence_digest,
            )
        except Exception as exc:
            return (
                "FAILURE",
                type(
                    exc
                ).__name__,
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
        item[
            0
        ] == "SUCCESS"
        for item in results
    ) == 1

    assert sum(
        item[
            0
        ] == "FAILURE"
        for item in results
    ) == 1

    assert collection.count_documents(
        {}
    ) == 1

    durable = registry.get(
        first.correspondence_id
    )

    assert durable in (
        first,
        second,
    )


# ============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# ============================================================================
# VERSION: v1.0.1-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY-REAL-MONGO-TEST
# DATABASE BOUNDARY: UUID-isolated disposable loopback replica-set database.
# DATABASE PREFIX: wilsy_taxcorr_cert_
# DEPENDENCY CHAIN: Snapshot -> Hierarchy -> Correspondence.
# IDENTICAL CONCURRENCY: one durable truth; successful exact replay permitted.
# CONFLICTING CONCURRENCY: exactly one durable winner.
# TENANT AUTHORITY: none.
# NETWORK AUTHORITY: loopback Mongo only.
# FINANCIAL EXECUTION AUTHORITY: none.
# END OF WILSY OS SOVEREIGN ARTIFACT
