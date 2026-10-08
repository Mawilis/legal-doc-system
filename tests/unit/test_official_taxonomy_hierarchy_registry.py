"""
WILSY OS — Official Taxonomy Hierarchy Registry Direct Unit Contract

TITLE:
    WILSY OS Official Taxonomy Hierarchy Registry Direct Unit Contract

VERSION:
    v1.0.1-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Freezes immutable transactional persistence semantics for one
    OfficialTaxonomyHierarchy only after its authoritative Snapshot binding has
    resolved through the certified OfficialTaxonomySnapshotRegistry and passed
    the pure hierarchy-domain validate_snapshot_binding() contract.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_official_taxonomy_hierarchy_registry.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.1-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY-TEST
        - Freezes platform-reference hierarchy persistence authority.
        - Requires caller-owned active Mongo transaction before create.
        - Requires exact persisted Snapshot identity/digest lookup before any
          hierarchy insert.
        - Requires the hierarchy domain itself to validate Snapshot coordinates
          and source-artifact provenance before persistence.
        - Requires preflight exact replay and known conflict adjudication before
          insert so ordinary replay cannot abort a real Mongo transaction.
        - Requires post-preflight duplicate-key races to fail closed without
          reading through the Mongo-aborted transaction.
        - Freezes immutable insert-only persistence, strict hydration, indexes,
          read surfaces and absence of TTL/update/replace/delete authority.

    v1.0.1-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY-TEST
        - Repairs the direct unit harness by importing pathlib.Path.
        - Removes four unrelated NameError/Pyright failures so the only
          remaining static RED is the intentionally absent production
          hierarchy registry module.
        - Preserves all thirty persistence and authority tests unchanged.

TENANT BOUNDARY:
    Platform reference truth only. No tenant_id or tenant scope.

AUTHORITY BOUNDARY:
    This registry may persist an already-valid OfficialTaxonomyHierarchy and
    resolve its already-persisted authoritative Snapshot dependency. It may not
    create or mutate Snapshot truth, graph semantics, correspondence truth,
    tenant classifications, entitlements, commercial truth or service packs.

NETWORK BOUNDARY:
    No remote acquisition, HTTP, parser or live official-source lookup.

FINANCIAL AUTHORITY BOUNDARY:
    None. This artifact has no payment, settlement or financial execution
    authority.
"""

from __future__ import annotations

from pathlib import Path

from copy import deepcopy
from datetime import date, datetime, timezone
import hashlib
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

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


EXPECTED_VERSION = (
    "v1.0.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY"
)
EXPECTED_COLLECTION = "official_taxonomy_hierarchies"


class FakeTransaction:
    def __init__(self, *, active: bool = True) -> None:
        self.in_transaction = active


class FakeSession:
    def __init__(self, *, active: bool = True) -> None:
        self._transaction = FakeTransaction(active=active)

    @property
    def in_transaction(self) -> bool:
        return self._transaction.in_transaction


class FakeIndexCollection:
    def __init__(self) -> None:
        self.indexes: list[
            tuple[tuple[tuple[str, int], ...], dict[str, Any]]
        ] = []

    def create_index(
        self,
        keys: list[tuple[str, int]],
        **kwargs: Any,
    ) -> str:
        self.indexes.append((tuple(keys), dict(kwargs)))
        return str(kwargs.get("name", "index"))


class FakeCollection:
    def __init__(
        self,
        rows: list[dict[str, Any]] | None = None,
    ) -> None:
        self.rows = [
            deepcopy(row)
            for row in (rows if rows is not None else [])
        ]
        self.insert_calls = 0
        self.find_calls: list[dict[str, Any]] = []

    def find(
        self,
        query: dict[str, Any],
        *,
        session: Any | None = None,
    ) -> list[dict[str, Any]]:
        del session
        self.find_calls.append(deepcopy(query))

        return [
            deepcopy(row)
            for row in self.rows
            if all(
                row.get(key) == value
                for key, value in query.items()
            )
        ]

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: Any,
    ) -> object:
        assert session is not None
        self.insert_calls += 1
        self.rows.append(deepcopy(document))
        return object()


class InsertForbiddenCollection(FakeCollection):
    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: Any,
    ) -> object:
        del document, session
        raise AssertionError(
            "HIERARCHY_REGISTRY_PREFLIGHT_MUST_RESOLVE_BEFORE_INSERT"
        )


class RaceDuplicateCollection(FakeCollection):
    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: Any,
    ) -> object:
        del document, session
        self.insert_calls += 1
        raise DuplicateKeyError(
            "simulated concurrent unique conflict"
        )


class FakeSnapshotRegistry:
    def __init__(
        self,
        snapshot: OfficialTaxonomySnapshot | None,
    ) -> None:
        self.snapshot = snapshot
        self.get_calls: list[tuple[str, Any]] = []
        self.digest_calls: list[tuple[str, Any]] = []

    def get(
        self,
        snapshot_id: str,
        *,
        session: Any | None = None,
    ) -> OfficialTaxonomySnapshot | None:
        self.get_calls.append((snapshot_id, session))

        if (
            self.snapshot is not None
            and self.snapshot.snapshot_id == snapshot_id
        ):
            return self.snapshot

        return None

    def get_by_digest(
        self,
        snapshot_digest: str,
        *,
        session: Any | None = None,
    ) -> OfficialTaxonomySnapshot | None:
        self.digest_calls.append((snapshot_digest, session))

        if (
            self.snapshot is not None
            and self.snapshot.snapshot_digest == snapshot_digest
        ):
            return self.snapshot

        return None


def source_artifact(
    artifact_id: str,
) -> OfficialTaxonomySourceArtifact:
    return OfficialTaxonomySourceArtifact(
        artifact_id=artifact_id,
        kind=next(iter(OfficialTaxonomyArtifactKind)),
        source_reference=(
            "https://example.invalid/" + artifact_id.lower()
        ),
        media_type="text/csv",
        language_tag="en",
        source_digest=hashlib.sha3_512(
            artifact_id.encode("utf-8")
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
        rights_reference="official publisher terms",
    )


def snapshot(
    *,
    snapshot_id: str = "SNAPSHOT-1",
    scheme_id: str = "ISIC",
    scheme_version: str = "REV5",
    jurisdiction: str = "GLOBAL",
    artifact_ids: tuple[str, ...] = (
        "STRUCTURE",
        "NOTES",
    ),
) -> OfficialTaxonomySnapshot:
    return OfficialTaxonomySnapshot(
        snapshot_id=snapshot_id,
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        publisher="United Nations",
        jurisdiction=jurisdiction,
        publisher_status="official",
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
        source_artifacts=tuple(
            source_artifact(artifact_id)
            for artifact_id in artifact_ids
        ),
        supersedes_snapshot_id=None,
    )


def hierarchy(
    bound_snapshot: OfficialTaxonomySnapshot,
    *,
    hierarchy_id: str = "HIERARCHY-1",
    source_refs: tuple[str, ...] = (
        "STRUCTURE",
        "NOTES",
    ),
) -> OfficialTaxonomyHierarchy:
    root_text = OfficialTaxonomyCategoryText(
        language_tag="en",
        title="Root",
        definition=None,
        explanatory_notes=(),
        inclusions=(),
        exclusions=(),
        source_artifact_refs=("STRUCTURE",),
    )

    child_text = OfficialTaxonomyCategoryText(
        language_tag="en",
        title="Division",
        definition=None,
        explanatory_notes=(),
        inclusions=(),
        exclusions=(),
        source_artifact_refs=("NOTES",),
    )

    levels = (
        OfficialTaxonomyHierarchyLevel(
            level_id="SECTION",
            rank=0,
            title="Section",
            source_artifact_refs=("STRUCTURE",),
        ),
        OfficialTaxonomyHierarchyLevel(
            level_id="DIVISION",
            rank=1,
            title="Division",
            source_artifact_refs=("STRUCTURE",),
        ),
    )

    categories = (
        OfficialTaxonomyCategory(
            category_id="CAT-A",
            level_id="SECTION",
            code="A",
            parent_category_id=None,
            terminal=False,
            source_artifact_refs=("STRUCTURE",),
            texts=(root_text,),
        ),
        OfficialTaxonomyCategory(
            category_id="CAT-01",
            level_id="DIVISION",
            code="01",
            parent_category_id="CAT-A",
            terminal=True,
            source_artifact_refs=("NOTES",),
            texts=(child_text,),
        ),
    )

    return OfficialTaxonomyHierarchy(
        hierarchy_id=hierarchy_id,
        snapshot_id=bound_snapshot.snapshot_id,
        snapshot_digest=bound_snapshot.snapshot_digest,
        scheme_id=bound_snapshot.scheme_id,
        scheme_version=bound_snapshot.scheme_version,
        jurisdiction=bound_snapshot.jurisdiction,
        source_artifact_refs=source_refs,
        levels=levels,
        categories=categories,
    )


def registry_types() -> tuple[
    type[Any],
    type[Exception],
    str,
    str,
]:
    from tools.eos.saas.official_taxonomy_hierarchy_registry import (
        COLLECTION_NAME,
        VERSION,
        OfficialTaxonomyHierarchyRegistry,
        OfficialTaxonomyHierarchyRegistryError,
    )

    return (
        OfficialTaxonomyHierarchyRegistry,
        OfficialTaxonomyHierarchyRegistryError,
        VERSION,
        COLLECTION_NAME,
    )


def build_registry(
    collection: Any,
    snapshot_registry: Any,
) -> Any:
    Registry, _, _, _ = registry_types()
    return Registry(
        collection,
        snapshot_registry=snapshot_registry,
    )


def test_version_and_collection_name_are_exact() -> None:
    _, _, version, collection = registry_types()
    assert version == EXPECTED_VERSION
    assert collection == EXPECTED_COLLECTION


def test_registry_exposes_only_hierarchy_persistence_authority() -> None:
    Registry, _, _, _ = registry_types()

    public = {
        name
        for name in dir(Registry)
        if not name.startswith("_")
    }

    assert {
        "ensure_indexes",
        "create",
        "get",
        "get_by_digest",
        "get_by_snapshot_binding",
        "get_by_scheme_version_jurisdiction",
    }.issubset(public)

    for forbidden in (
        "update",
        "replace",
        "delete",
        "classify",
        "activate",
        "fetch",
        "parse",
        "create_snapshot",
    ):
        assert forbidden not in public


def test_ensure_indexes_freezes_required_contract() -> None:
    Registry, _, _, _ = registry_types()
    collection = FakeIndexCollection()

    Registry.ensure_indexes(collection)

    by_name = {
        kwargs["name"]: (keys, kwargs)
        for keys, kwargs in collection.indexes
    }

    hierarchy_id = by_name[
        "official_taxonomy_hierarchy_id_unique"
    ]
    assert hierarchy_id[0] == (("hierarchy_id", 1),)
    assert hierarchy_id[1]["unique"] is True

    digest = by_name[
        "official_taxonomy_hierarchy_digest_unique"
    ]
    assert digest[0] == (("hierarchy_digest", 1),)
    assert digest[1]["unique"] is True

    snapshot_binding = by_name[
        "official_taxonomy_hierarchy_snapshot_binding"
    ]
    assert snapshot_binding[0] == (
        ("snapshot_id", 1),
        ("snapshot_digest", 1),
    )
    assert not snapshot_binding[1].get("unique", False)

    coordinates = by_name[
        "official_taxonomy_hierarchy_scheme_version_jurisdiction"
    ]
    assert coordinates[0] == (
        ("scheme_id", 1),
        ("scheme_version", 1),
        ("jurisdiction", 1),
    )
    assert not coordinates[1].get("unique", False)


def test_registry_defines_no_ttl_index() -> None:
    Registry, _, _, _ = registry_types()
    collection = FakeIndexCollection()
    Registry.ensure_indexes(collection)

    for _keys, kwargs in collection.indexes:
        assert "expireAfterSeconds" not in kwargs


def test_create_requires_active_transaction_before_dependency_read_or_write() -> None:
    authoritative = snapshot()
    collection = FakeCollection()
    snapshots = FakeSnapshotRegistry(authoritative)

    value = build_registry(collection, snapshots)
    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.create(
            hierarchy(authoritative),
            session=FakeSession(active=False),
        )

    assert snapshots.get_calls == []
    assert snapshots.digest_calls == []
    assert collection.insert_calls == 0


def test_create_rejects_missing_session_before_dependency_read_or_write() -> None:
    authoritative = snapshot()
    collection = FakeCollection()
    snapshots = FakeSnapshotRegistry(authoritative)

    value = build_registry(collection, snapshots)
    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.create(
            hierarchy(authoritative),
            session=None,
        )

    assert snapshots.get_calls == []
    assert snapshots.digest_calls == []
    assert collection.insert_calls == 0


def test_create_accepts_only_hierarchy_domain() -> None:
    authoritative = snapshot()
    collection = FakeCollection()

    value = build_registry(
        collection,
        FakeSnapshotRegistry(authoritative),
    )

    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.create(
            object(),
            session=FakeSession(),
        )

    assert collection.insert_calls == 0


def test_snapshot_identity_and_digest_are_resolved_before_insert() -> None:
    authoritative = snapshot()
    collection = FakeCollection()
    snapshots = FakeSnapshotRegistry(authoritative)

    value = build_registry(collection, snapshots)
    candidate = hierarchy(authoritative)

    value.create(
        candidate,
        session=FakeSession(),
    )

    assert len(snapshots.get_calls) == 1
    assert snapshots.get_calls[0][0] == candidate.snapshot_id
    assert len(snapshots.digest_calls) == 1
    assert (
        snapshots.digest_calls[0][0]
        == candidate.snapshot_digest
    )
    assert collection.insert_calls == 1


def test_missing_snapshot_binding_is_rejected_before_insert() -> None:
    authoritative = snapshot()
    collection = FakeCollection()

    value = build_registry(
        collection,
        FakeSnapshotRegistry(None),
    )

    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.create(
            hierarchy(authoritative),
            session=FakeSession(),
        )

    assert collection.insert_calls == 0


def test_snapshot_id_and_digest_must_resolve_same_authoritative_object() -> None:
    authoritative = snapshot()

    class SplitSnapshotRegistry(FakeSnapshotRegistry):
        def get_by_digest(
            self,
            snapshot_digest: str,
            *,
            session: Any | None = None,
        ) -> OfficialTaxonomySnapshot | None:
            self.digest_calls.append(
                (snapshot_digest, session)
            )
            return snapshot(
                snapshot_id="SNAPSHOT-OTHER",
            )

    collection = FakeCollection()

    value = build_registry(
        collection,
        SplitSnapshotRegistry(authoritative),
    )

    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.create(
            hierarchy(authoritative),
            session=FakeSession(),
        )

    assert collection.insert_calls == 0


def test_domain_snapshot_binding_validation_occurs_before_insert() -> None:
    authoritative = snapshot(
        artifact_ids=("STRUCTURE",)
    )

    candidate = hierarchy(
        authoritative,
        source_refs=(
            "STRUCTURE",
            "NOTES",
        ),
    )

    collection = FakeCollection()

    value = build_registry(
        collection,
        FakeSnapshotRegistry(authoritative),
    )

    with pytest.raises(
        Exception,
        match=(
            "OFFICIAL_TAXONOMY_HIERARCHY_"
            "SOURCE_ARTIFACT_REF_UNRESOLVED"
        ),
    ):
        value.create(
            candidate,
            session=FakeSession(),
        )

    assert collection.insert_calls == 0


def test_create_persists_exact_domain_serialization() -> None:
    authoritative = snapshot()
    candidate = hierarchy(authoritative)

    collection = FakeCollection()

    value = build_registry(
        collection,
        FakeSnapshotRegistry(authoritative),
    )

    observed = value.create(
        candidate,
        session=FakeSession(),
    )

    assert observed == candidate
    assert collection.rows == [
        candidate.to_dict()
    ]


def test_exact_replay_is_resolved_before_duplicate_insert() -> None:
    authoritative = snapshot()
    candidate = hierarchy(authoritative)

    collection = InsertForbiddenCollection(
        [candidate.to_dict()]
    )

    value = build_registry(
        collection,
        FakeSnapshotRegistry(authoritative),
    )

    observed = value.create(
        candidate,
        session=FakeSession(),
    )

    assert observed == candidate


def test_same_identity_conflict_is_rejected_before_insert() -> None:
    authoritative = snapshot()

    existing = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-1",
    )

    different = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-2",
    )

    row = different.to_dict()
    row["hierarchy_id"] = existing.hierarchy_id

    collection = InsertForbiddenCollection([row])

    value = build_registry(
        collection,
        FakeSnapshotRegistry(authoritative),
    )

    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.create(
            existing,
            session=FakeSession(),
        )


def test_corrupt_durable_digest_collision_is_rejected_before_insert() -> None:
    authoritative = snapshot()
    candidate = hierarchy(authoritative)

    corrupt = candidate.to_dict()
    corrupt["hierarchy_id"] = "CORRUPT-OTHER-ID"

    collection = InsertForbiddenCollection([corrupt])

    value = build_registry(
        collection,
        FakeSnapshotRegistry(authoritative),
    )

    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.create(
            candidate,
            session=FakeSession(),
        )


def test_post_preflight_duplicate_race_never_reads_after_duplicate_error() -> None:
    authoritative = snapshot()
    candidate = hierarchy(authoritative)

    collection = RaceDuplicateCollection()

    value = build_registry(
        collection,
        FakeSnapshotRegistry(authoritative),
    )

    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.create(
            candidate,
            session=FakeSession(),
        )

    assert len(collection.find_calls) == 2


def test_get_returns_strictly_hydrated_hierarchy() -> None:
    authoritative = snapshot()
    candidate = hierarchy(authoritative)

    value = build_registry(
        FakeCollection([candidate.to_dict()]),
        FakeSnapshotRegistry(authoritative),
    )

    assert value.get(
        candidate.hierarchy_id
    ) == candidate


def test_get_missing_returns_none() -> None:
    authoritative = snapshot()

    value = build_registry(
        FakeCollection(),
        FakeSnapshotRegistry(authoritative),
    )

    assert value.get("MISSING") is None


def test_get_by_digest_returns_exact_hierarchy() -> None:
    authoritative = snapshot()
    candidate = hierarchy(authoritative)

    value = build_registry(
        FakeCollection([candidate.to_dict()]),
        FakeSnapshotRegistry(authoritative),
    )

    assert (
        value.get_by_digest(
            candidate.hierarchy_digest
        )
        == candidate
    )


def test_get_by_snapshot_binding_is_read_only() -> None:
    authoritative = snapshot()

    first = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-1",
    )
    second = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-2",
    )

    collection = FakeCollection(
        [
            first.to_dict(),
            second.to_dict(),
        ]
    )

    value = build_registry(
        collection,
        FakeSnapshotRegistry(authoritative),
    )

    observed = value.get_by_snapshot_binding(
        authoritative.snapshot_id,
        authoritative.snapshot_digest,
    )

    assert set(observed) == {
        first,
        second,
    }
    assert collection.insert_calls == 0


def test_get_by_scheme_version_jurisdiction_is_read_only() -> None:
    authoritative = snapshot()

    first = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-1",
    )
    second = hierarchy(
        authoritative,
        hierarchy_id="HIERARCHY-2",
    )

    collection = FakeCollection(
        [
            first.to_dict(),
            second.to_dict(),
        ]
    )

    value = build_registry(
        collection,
        FakeSnapshotRegistry(authoritative),
    )

    observed = (
        value.get_by_scheme_version_jurisdiction(
            "ISIC",
            "REV5",
            "GLOBAL",
        )
    )

    assert set(observed) == {
        first,
        second,
    }
    assert collection.insert_calls == 0


def test_corrupt_persisted_truth_is_rejected() -> None:
    authoritative = snapshot()
    candidate = hierarchy(authoritative)

    corrupt = candidate.to_dict()
    corrupt["hierarchy_digest"] = "0" * 128

    value = build_registry(
        FakeCollection([corrupt]),
        FakeSnapshotRegistry(authoritative),
    )

    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.get(
            candidate.hierarchy_id
        )


def test_extra_persisted_field_is_rejected() -> None:
    authoritative = snapshot()
    candidate = hierarchy(authoritative)

    corrupt = candidate.to_dict()
    corrupt["unexpected"] = True

    value = build_registry(
        FakeCollection([corrupt]),
        FakeSnapshotRegistry(authoritative),
    )

    _, Error, _, _ = registry_types()

    with pytest.raises(Error):
        value.get(
            candidate.hierarchy_id
        )


def test_registry_has_no_mutation_methods_after_create() -> None:
    Registry, _, _, _ = registry_types()

    for forbidden in (
        "update",
        "replace",
        "delete",
        "upsert",
    ):
        assert not hasattr(
            Registry,
            forbidden,
        )


def test_registry_contains_no_tenant_fields_or_scope() -> None:
    path = Path(__file__).parents[2] / (
        "tools/eos/saas/"
        "official_taxonomy_hierarchy_registry.py"
    )

    source = path.read_text(
        encoding="utf-8",
    )

    assert "tenant_id" not in source
    assert "tenant_scope" not in source


def test_registry_contains_no_network_parser_or_classification_authority() -> None:
    path = Path(__file__).parents[2] / (
        "tools/eos/saas/"
        "official_taxonomy_hierarchy_registry.py"
    )

    source = path.read_text(
        encoding="utf-8",
    )

    for forbidden in (
        "requests.",
        "httpx.",
        "urllib.",
        "fetch(",
        "parse(",
        "classify(",
        "activate(",
    ):
        assert forbidden not in source


def test_registry_never_calls_update_replace_or_delete_collection_apis() -> None:
    path = Path(__file__).parents[2] / (
        "tools/eos/saas/"
        "official_taxonomy_hierarchy_registry.py"
    )

    source = path.read_text(
        encoding="utf-8",
    )

    for forbidden in (
        ".update_one(",
        ".update_many(",
        ".replace_one(",
        ".delete_one(",
        ".delete_many(",
        ".find_one_and_update(",
        ".find_one_and_replace(",
        ".find_one_and_delete(",
    ):
        assert forbidden not in source


def test_registry_may_not_create_or_mutate_snapshot_truth() -> None:
    Registry, _, _, _ = registry_types()

    public = {
        name
        for name in dir(Registry)
        if not name.startswith("_")
    }

    assert "create_snapshot" not in public
    assert "update_snapshot" not in public
    assert "delete_snapshot" not in public


def test_registry_may_not_accept_correspondence_domain() -> None:
    path = Path(__file__).parents[2] / (
        "tools/eos/saas/"
        "official_taxonomy_hierarchy_registry.py"
    )

    source = path.read_text(
        encoding="utf-8",
    )

    assert (
        "OfficialTaxonomyCorrespondence"
        not in source
    )


def test_snapshot_dependency_is_used_only_for_authoritative_reads() -> None:
    authoritative = snapshot()
    candidate = hierarchy(authoritative)

    dependency = FakeSnapshotRegistry(authoritative)

    value = build_registry(
        FakeCollection(),
        dependency,
    )

    value.create(
        candidate,
        session=FakeSession(),
    )

    assert len(dependency.get_calls) == 1
    assert len(dependency.digest_calls) == 1


# ============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# ============================================================================
# VERSION: v1.0.1-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY-TEST
# AUTHORITY BOUNDARY: direct unit contract for immutable platform-reference
# hierarchy persistence after certified Snapshot resolution and pure-domain
# binding validation only.
# TENANT AUTHORITY: none.
# NETWORK AUTHORITY: none.
# FINANCIAL EXECUTION AUTHORITY: none.
# END OF WILSY OS SOVEREIGN ARTIFACT
