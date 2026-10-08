"""
WILSY OS — Official Taxonomy Correspondence Registry Unit Contract

TITLE:
    WILSY OS Official Taxonomy Correspondence Registry Unit Contract

VERSION:
    v1.0.1-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Test-first contract for immutable transaction-bound persistence of
    OfficialTaxonomyCorrespondence truth against authoritative source and
    target OfficialTaxonomyHierarchy registry reads.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_official_taxonomy_correspondence_registry.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.1-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY-TEST
        - Reauthors the test-first contract with the full certified transitive
          fixture dependency closure.
        - Ensures category(), SOURCE_SNAPSHOT_DIGEST and
          TARGET_SNAPSHOT_DIGEST are present.
        - Corrects same-identity conflict construction to use different
          semantic correspondence truth under the same correspondence_id.
        - Preserves the frozen thirty-test registry contract.

TENANT BOUNDARY:
    Platform reference truth only. No tenant persistence or authorization
    authority.

AUTHORITY BOUNDARY:
    Correspondence persistence only. Source and target hierarchy truth are
    consumed read-only from authoritative hierarchy persistence.

NETWORK BOUNDARY:
    No network acquisition, parser, classification or activation authority.

FINANCIAL AUTHORITY BOUNDARY:
    None.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.official_taxonomy_correspondence import (
    OfficialTaxonomyCorrespondence,
    OfficialTaxonomyCorrespondenceCardinality,
    OfficialTaxonomyCorrespondenceError,
    OfficialTaxonomyCorrespondenceRelation,
)
from tools.eos.saas.domain.official_taxonomy_hierarchy import (
    OfficialTaxonomyCategory,
    OfficialTaxonomyCategoryText,
    OfficialTaxonomyHierarchy,
    OfficialTaxonomyHierarchyLevel,
)


SOURCE_SNAPSHOT_DIGEST = hashlib.sha3_512(
    b"source-snapshot"
).hexdigest()

TARGET_SNAPSHOT_DIGEST = hashlib.sha3_512(
    b"target-snapshot"
).hexdigest()


def category_text(
    title: str,
) -> OfficialTaxonomyCategoryText:
    """Build one category text fixture."""
    return OfficialTaxonomyCategoryText(
        language_tag="en",
        title=title,
        definition=None,
        explanatory_notes=(),
        inclusions=(),
        exclusions=(),
        source_artifact_refs=("STRUCTURE",),
    )


def category(
    category_id: str,
    level_id: str,
    code: str,
    parent_category_id: str | None,
    terminal: bool,
) -> OfficialTaxonomyCategory:
    """Build one category fixture."""
    return OfficialTaxonomyCategory(
        category_id=category_id,
        level_id=level_id,
        code=code,
        parent_category_id=parent_category_id,
        terminal=terminal,
        source_artifact_refs=("STRUCTURE",),
        texts=(
            category_text(
                category_id,
            ),
        ),
    )


def hierarchy(
    *,
    hierarchy_id: str,
    snapshot_id: str,
    snapshot_digest: str,
    scheme_id: str,
    scheme_version: str,
    jurisdiction: str = "GLOBAL",
    root_code: str = "A",
    child_codes: tuple[str, ...] = (
        "01",
        "02",
    ),
) -> OfficialTaxonomyHierarchy:
    """Build one two-level certified hierarchy fixture."""
    root_id = (
        hierarchy_id
        + "-ROOT"
    )

    children = tuple(
        category(
            hierarchy_id
            + "-C"
            + str(index),
            "CHILD",
            code,
            root_id,
            True,
        )
        for index, code in enumerate(
            child_codes,
            start=1,
        )
    )

    return OfficialTaxonomyHierarchy(
        hierarchy_id=hierarchy_id,
        snapshot_id=snapshot_id,
        snapshot_digest=snapshot_digest,
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        jurisdiction=jurisdiction,
        source_artifact_refs=(
            "STRUCTURE",
        ),
        levels=(
            OfficialTaxonomyHierarchyLevel(
                level_id="ROOT",
                rank=0,
                title="Root",
                source_artifact_refs=(
                    "STRUCTURE",
                ),
            ),
            OfficialTaxonomyHierarchyLevel(
                level_id="CHILD",
                rank=1,
                title="Child",
                source_artifact_refs=(
                    "STRUCTURE",
                ),
            ),
        ),
        categories=(
            category(
                root_id,
                "ROOT",
                root_code,
                None,
                False,
            ),
            *children,
        ),
    )


def source_hierarchy() -> OfficialTaxonomyHierarchy:
    """Build source hierarchy fixture."""
    return hierarchy(
        hierarchy_id="SOURCE-H",
        snapshot_id="SOURCE-S",
        snapshot_digest=SOURCE_SNAPSHOT_DIGEST,
        scheme_id="ISIC",
        scheme_version="REV4",
    )


def target_hierarchy() -> OfficialTaxonomyHierarchy:
    """Build target hierarchy fixture."""
    return hierarchy(
        hierarchy_id="TARGET-H",
        snapshot_id="TARGET-S",
        snapshot_digest=TARGET_SNAPSHOT_DIGEST,
        scheme_id="ISIC",
        scheme_version="REV5",
        child_codes=(
            "11",
            "12",
            "13",
        ),
    )


def relation(
    relationship_id: str = "R1",
    *,
    source_ids: tuple[str, ...] = (
        "SOURCE-H-C1",
    ),
    target_ids: tuple[str, ...] = (
        "TARGET-H-C1",
    ),
    publisher_change_type: str = (
        "publisher supplied change type"
    ),
    publisher_description: str | None = (
        "publisher supplied description"
    ),
    source_refs: tuple[str, ...] = (
        "CORRESPONDENCE",
    ),
) -> OfficialTaxonomyCorrespondenceRelation:
    """Build one set-to-set correspondence relation fixture."""
    return OfficialTaxonomyCorrespondenceRelation(
        relationship_id=relationship_id,
        source_category_ids=source_ids,
        target_category_ids=target_ids,
        publisher_change_type=publisher_change_type,
        publisher_description=publisher_description,
        source_artifact_refs=source_refs,
    )


def correspondence(
    *,
    source: OfficialTaxonomyHierarchy | None = None,
    target: OfficialTaxonomyHierarchy | None = None,
    relations: tuple[
        OfficialTaxonomyCorrespondenceRelation,
        ...,
    ] | None = None,
    source_refs: tuple[str, ...] = (
        "CORRESPONDENCE",
    ),
) -> OfficialTaxonomyCorrespondence:
    """Build one complete correspondence aggregate fixture."""
    return OfficialTaxonomyCorrespondence(
        correspondence_id="CORR-1",
        source_hierarchy=(
            source
            if source is not None
            else source_hierarchy()
        ),
        target_hierarchy=(
            target
            if target is not None
            else target_hierarchy()
        ),
        source_artifact_refs=source_refs,
        relations=(
            relations
            if relations is not None
            else (
                relation(),
            )
        ),
    )


class FakeSession:
    """Minimal caller-owned transaction seam."""

    def __init__(
        self,
        *,
        in_transaction: bool = True,
    ) -> None:
        self.in_transaction = in_transaction


class FakeCollection:
    """Minimal immutable Mongo-like collection seam."""

    def __init__(
        self,
        rows: list[dict[str, Any]] | None = None,
    ) -> None:
        self.rows = [
            deepcopy(row)
            for row in (
                rows
                or []
            )
        ]
        self.find_calls: list[
            tuple[dict[str, Any], Any]
        ] = []
        self.insert_calls: list[
            tuple[dict[str, Any], Any]
        ] = []
        self.index_calls: list[
            tuple[Any, dict[str, Any]]
        ] = []

    def create_index(
        self,
        keys: Any,
        **kwargs: Any,
    ) -> str:
        self.index_calls.append(
            (
                deepcopy(keys),
                deepcopy(kwargs),
            )
        )

        return str(
            kwargs.get(
                "name",
                "index",
            )
        )

    def find(
        self,
        query: dict[str, Any],
        *,
        session: Any = None,
    ) -> list[dict[str, Any]]:
        self.find_calls.append(
            (
                deepcopy(query),
                session,
            )
        )

        return [
            deepcopy(row)
            for row in self.rows
            if all(
                row.get(key)
                == value
                for key, value in query.items()
            )
        ]

    def insert_one(
        self,
        payload: dict[str, Any],
        *,
        session: Any,
    ) -> object:
        self.insert_calls.append(
            (
                deepcopy(payload),
                session,
            )
        )
        self.rows.append(
            deepcopy(payload)
        )
        return object()


class InsertForbiddenCollection(
    FakeCollection
):
    """Fail if a preflight rejection incorrectly reaches insert."""

    def insert_one(
        self,
        payload: dict[str, Any],
        *,
        session: Any,
    ) -> object:
        raise AssertionError(
            "INSERT_MUST_NOT_OCCUR"
        )


class RaceDuplicateCollection(
    FakeCollection
):
    """Raise duplicate after clean preflight to simulate a race."""

    def insert_one(
        self,
        payload: dict[str, Any],
        *,
        session: Any,
    ) -> object:
        raise DuplicateKeyError(
            "simulated duplicate race"
        )


class FakeHierarchyRegistry:
    """Read-only identity/digest resolver for authoritative hierarchies."""

    def __init__(
        self,
        *values: OfficialTaxonomyHierarchy,
    ) -> None:
        self.values = tuple(
            values
        )
        self.get_calls: list[
            tuple[str, Any]
        ] = []
        self.digest_calls: list[
            tuple[str, Any]
        ] = []

    def get(
        self,
        hierarchy_id: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomyHierarchy | None:
        self.get_calls.append(
            (
                hierarchy_id,
                session,
            )
        )

        for value in self.values:
            if (
                value.hierarchy_id
                == hierarchy_id
            ):
                return value

        return None

    def get_by_digest(
        self,
        hierarchy_digest: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomyHierarchy | None:
        self.digest_calls.append(
            (
                hierarchy_digest,
                session,
            )
        )

        for value in self.values:
            if (
                value.hierarchy_digest
                == hierarchy_digest
            ):
                return value

        return None


def registry_types() -> tuple[
    type[Any],
    type[Exception],
    str,
    str,
]:
    """Import the intentionally absent production registry."""
    from tools.eos.saas.official_taxonomy_correspondence_registry import (
        COLLECTION_NAME,
        VERSION,
        OfficialTaxonomyCorrespondenceRegistry,
        OfficialTaxonomyCorrespondenceRegistryError,
    )

    return (
        OfficialTaxonomyCorrespondenceRegistry,
        OfficialTaxonomyCorrespondenceRegistryError,
        VERSION,
        COLLECTION_NAME,
    )


def build_registry(
    collection: Any,
    hierarchy_registry: Any,
) -> Any:
    Registry, _, _, _ = (
        registry_types()
    )

    return Registry(
        collection,
        hierarchy_registry=hierarchy_registry,
    )


def authoritative_values() -> tuple[
    OfficialTaxonomyHierarchy,
    OfficialTaxonomyHierarchy,
    OfficialTaxonomyCorrespondence,
]:
    """Return two authoritative hierarchies and their correspondence."""
    source = source_hierarchy()
    target = target_hierarchy()

    value = correspondence(
        source=source,
        target=target,
    )

    return (
        source,
        target,
        value,
    )


def different_source_same_identity(
    source: OfficialTaxonomyHierarchy,
) -> OfficialTaxonomyHierarchy:
    """Build conflicting source truth carrying the same hierarchy identity."""
    return hierarchy(
        hierarchy_id=source.hierarchy_id,
        snapshot_id="SOURCE-S-OTHER",
        snapshot_digest=hashlib.sha3_512(
            b"source-other"
        ).hexdigest(),
        scheme_id="ISIC",
        scheme_version="REV4",
    )


def different_target_same_identity(
    target: OfficialTaxonomyHierarchy,
) -> OfficialTaxonomyHierarchy:
    """Build conflicting target truth carrying the same hierarchy identity."""
    return hierarchy(
        hierarchy_id=target.hierarchy_id,
        snapshot_id="TARGET-S-OTHER",
        snapshot_digest=hashlib.sha3_512(
            b"target-other"
        ).hexdigest(),
        scheme_id="ISIC",
        scheme_version="REV5",
        child_codes=(
            "11",
            "12",
            "13",
        ),
    )


def test_version_and_collection_name_exact() -> None:
    _, _, version, collection = (
        registry_types()
    )

    assert version == (
        "v1.0.0-WILSY-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY"
    )
    assert collection == (
        "official_taxonomy_correspondences"
    )


def test_registry_exposes_only_correspondence_persistence_authority() -> None:
    Registry, _, _, _ = (
        registry_types()
    )

    public = {
        name
        for name in dir(
            Registry
        )
        if (
            not name.startswith("_")
            and callable(
                getattr(
                    Registry,
                    name,
                )
            )
        )
    }

    assert {
        "ensure_indexes",
        "create",
        "get",
        "get_by_digest",
        "get_by_source_hierarchy_binding",
        "get_by_target_hierarchy_binding",
    }.issubset(
        public
    )

    assert not {
        "update",
        "replace",
        "delete",
        "upsert",
        "create_hierarchy",
        "create_snapshot",
        "classify",
        "activate",
    } & public


def test_ensure_indexes_exact_contract() -> None:
    Registry, _, _, _ = (
        registry_types()
    )

    collection = FakeCollection()

    Registry.ensure_indexes(
        collection
    )

    assert collection.index_calls == [
        (
            [
                (
                    "correspondence_id",
                    1,
                ),
            ],
            {
                "name":
                    "official_taxonomy_correspondence_id_unique",
                "unique": True,
            },
        ),
        (
            [
                (
                    "correspondence_digest",
                    1,
                ),
            ],
            {
                "name":
                    "official_taxonomy_correspondence_digest_unique",
                "unique": True,
            },
        ),
        (
            [
                (
                    "source_hierarchy_id",
                    1,
                ),
                (
                    "source_hierarchy_digest",
                    1,
                ),
            ],
            {
                "name":
                    "official_taxonomy_correspondence_source_hierarchy_binding",
            },
        ),
        (
            [
                (
                    "target_hierarchy_id",
                    1,
                ),
                (
                    "target_hierarchy_digest",
                    1,
                ),
            ],
            {
                "name":
                    "official_taxonomy_correspondence_target_hierarchy_binding",
            },
        ),
    ]


def test_no_ttl_index() -> None:
    Registry, _, _, _ = (
        registry_types()
    )

    collection = FakeCollection()

    Registry.ensure_indexes(
        collection
    )

    assert all(
        "expireAfterSeconds"
        not in kwargs
        for _, kwargs in collection.index_calls
    )


def test_missing_session_rejected_before_hierarchy_read_or_write() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    collection = FakeCollection()
    dependency = FakeHierarchyRegistry(
        source,
        target,
    )

    registry = build_registry(
        collection,
        dependency,
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(
        Error,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create(
            candidate,
            session=None,
        )

    assert dependency.get_calls == []
    assert dependency.digest_calls == []
    assert collection.find_calls == []
    assert collection.insert_calls == []


def test_inactive_transaction_rejected_before_hierarchy_read_or_write() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    collection = FakeCollection()
    dependency = FakeHierarchyRegistry(
        source,
        target,
    )

    registry = build_registry(
        collection,
        dependency,
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(
        Error,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create(
            candidate,
            session=FakeSession(
                in_transaction=False
            ),
        )

    assert dependency.get_calls == []
    assert dependency.digest_calls == []
    assert collection.find_calls == []
    assert collection.insert_calls == []


def test_create_accepts_only_correspondence_domain() -> None:
    source, target, _candidate = (
        authoritative_values()
    )

    collection = FakeCollection()

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(
        Error
    ):
        registry.create(
            object(),
            session=FakeSession(),
        )

    assert collection.insert_calls == []


def test_source_hierarchy_id_and_digest_both_resolved() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    dependency = FakeHierarchyRegistry(
        source,
        target,
    )

    registry = build_registry(
        FakeCollection(),
        dependency,
    )

    session = FakeSession()

    registry.create(
        candidate,
        session=session,
    )

    assert (
        source.hierarchy_id,
        session,
    ) in dependency.get_calls

    assert (
        source.hierarchy_digest,
        session,
    ) in dependency.digest_calls


def test_source_hierarchy_id_digest_mismatch_rejected() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    source_by_id = (
        different_source_same_identity(
            source
        )
    )

    dependency = FakeHierarchyRegistry(
        source_by_id,
        source,
        target,
    )

    collection = FakeCollection()

    registry = build_registry(
        collection,
        dependency,
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.create(
            candidate,
            session=FakeSession(),
        )

    assert collection.insert_calls == []


def test_target_hierarchy_id_and_digest_both_resolved() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    dependency = FakeHierarchyRegistry(
        source,
        target,
    )

    registry = build_registry(
        FakeCollection(),
        dependency,
    )

    session = FakeSession()

    registry.create(
        candidate,
        session=session,
    )

    assert (
        target.hierarchy_id,
        session,
    ) in dependency.get_calls

    assert (
        target.hierarchy_digest,
        session,
    ) in dependency.digest_calls


def test_target_hierarchy_id_digest_mismatch_rejected() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    target_by_id = (
        different_target_same_identity(
            target
        )
    )

    dependency = FakeHierarchyRegistry(
        source,
        target_by_id,
        target,
    )

    collection = FakeCollection()

    registry = build_registry(
        collection,
        dependency,
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.create(
            candidate,
            session=FakeSession(),
        )

    assert collection.insert_calls == []


def test_missing_source_hierarchy_rejected_before_insert() -> None:
    _source, target, candidate = (
        authoritative_values()
    )

    collection = FakeCollection()

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            target,
        ),
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.create(
            candidate,
            session=FakeSession(),
        )

    assert collection.insert_calls == []


def test_missing_target_hierarchy_rejected_before_insert() -> None:
    source, _target, candidate = (
        authoritative_values()
    )

    collection = FakeCollection()

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
        ),
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.create(
            candidate,
            session=FakeSession(),
        )

    assert collection.insert_calls == []


def test_candidate_strict_rehydration_against_authoritative_hierarchies() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    collection = FakeCollection()

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    observed = registry.create(
        candidate,
        session=FakeSession(),
    )

    assert observed == candidate
    assert len(
        collection.insert_calls
    ) == 1
    assert (
        collection.insert_calls[0][0]
        == candidate.to_dict()
    )


def test_candidate_binding_mismatch_rejected_before_insert() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    object.__setattr__(
        candidate,
        "source_hierarchy_id",
        "MISMATCH",
    )

    collection = FakeCollection()

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.create(
            candidate,
            session=FakeSession(),
        )

    assert collection.insert_calls == []


def test_create_persists_exact_domain_serialization() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    collection = FakeCollection()

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    registry.create(
        candidate,
        session=FakeSession(),
    )

    assert (
        collection.insert_calls[0][0]
        == candidate.to_dict()
    )


def test_exact_replay_resolved_before_duplicate_insert() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    collection = (
        InsertForbiddenCollection(
            [
                candidate.to_dict(),
            ]
        )
    )

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    observed = registry.create(
        candidate,
        session=FakeSession(),
    )

    assert observed == candidate


def test_same_identity_conflict_rejected_before_insert() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    conflicting = correspondence(
        source=source,
        target=target,
        relations=(
            relation(
                publisher_description=(
                    "different publisher supplied description"
                )
            ),
        ),
    )

    assert (
        conflicting.correspondence_id
        == candidate.correspondence_id
    )

    assert (
        conflicting.correspondence_digest
        != candidate.correspondence_digest
    )

    collection = (
        InsertForbiddenCollection(
            [
                conflicting.to_dict(),
            ]
        )
    )

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.create(
            candidate,
            session=FakeSession(),
        )


def test_corrupt_durable_digest_collision_rejected_before_insert() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    corrupt = candidate.to_dict()

    corrupt[
        "correspondence_id"
    ] = "CORR-CORRUPT-ID"

    collection = (
        InsertForbiddenCollection(
            [
                corrupt,
            ]
        )
    )

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.create(
            candidate,
            session=FakeSession(),
        )


def test_post_preflight_duplicate_race_never_reads_after_duplicate_error() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    collection = (
        RaceDuplicateCollection()
    )

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.create(
            candidate,
            session=FakeSession(),
        )

    assert len(
        collection.find_calls
    ) == 2


def test_get_returns_strictly_hydrated_correspondence() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    registry = build_registry(
        FakeCollection(
            [
                candidate.to_dict(),
            ]
        ),
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    assert (
        registry.get(
            candidate.correspondence_id
        )
        == candidate
    )


def test_get_missing_returns_none() -> None:
    source, target, _candidate = (
        authoritative_values()
    )

    registry = build_registry(
        FakeCollection(),
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    assert (
        registry.get(
            "MISSING"
        )
        is None
    )


def test_get_by_digest_returns_exact_correspondence() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    registry = build_registry(
        FakeCollection(
            [
                candidate.to_dict(),
            ]
        ),
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    assert (
        registry.get_by_digest(
            candidate.correspondence_digest
        )
        == candidate
    )


def test_get_by_source_hierarchy_binding_is_read_only() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    collection = FakeCollection(
        [
            candidate.to_dict(),
        ]
    )

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    observed = (
        registry.get_by_source_hierarchy_binding(
            source.hierarchy_id,
            source.hierarchy_digest,
        )
    )

    assert tuple(
        observed
    ) == (
        candidate,
    )

    assert (
        collection.insert_calls
        == []
    )


def test_get_by_target_hierarchy_binding_is_read_only() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    collection = FakeCollection(
        [
            candidate.to_dict(),
        ]
    )

    registry = build_registry(
        collection,
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    observed = (
        registry.get_by_target_hierarchy_binding(
            target.hierarchy_id,
            target.hierarchy_digest,
        )
    )

    assert tuple(
        observed
    ) == (
        candidate,
    )

    assert (
        collection.insert_calls
        == []
    )


def test_corrupt_persisted_truth_rejected() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    corrupt = candidate.to_dict()

    corrupt[
        "correspondence_digest"
    ] = "0" * 128

    registry = build_registry(
        FakeCollection(
            [
                corrupt,
            ]
        ),
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.get(
            candidate.correspondence_id
        )


def test_extra_persisted_field_rejected() -> None:
    source, target, candidate = (
        authoritative_values()
    )

    corrupt = candidate.to_dict()

    corrupt[
        "unexpected"
    ] = True

    registry = build_registry(
        FakeCollection(
            [
                corrupt,
            ]
        ),
        FakeHierarchyRegistry(
            source,
            target,
        ),
    )

    _, Error, _, _ = (
        registry_types()
    )

    with pytest.raises(Error):
        registry.get(
            candidate.correspondence_id
        )


def test_registry_has_no_mutation_methods_after_create() -> None:
    Registry, _, _, _ = (
        registry_types()
    )

    for name in (
        "update",
        "replace",
        "delete",
        "upsert",
    ):
        assert not hasattr(
            Registry,
            name,
        )


def test_registry_contains_no_tenant_commercial_classification_activation_authority() -> None:
    path = (
        Path(__file__).parents[2]
        / "tools/eos/saas/"
        / "official_taxonomy_correspondence_registry.py"
    )

    source = path.read_text(
        encoding="utf-8",
    ).lower()

    for token in (
        "tenant_id",
        "tenant_scope",
        "subscription",
        "entitlement",
        "service_pack",
        "classify(",
        "activate(",
        "payment",
        "settlement",
    ):
        assert token not in source


def test_hierarchy_dependency_is_used_only_for_authoritative_reads() -> None:
    path = (
        Path(__file__).parents[2]
        / "tools/eos/saas/"
        / "official_taxonomy_correspondence_registry.py"
    )

    source = path.read_text(
        encoding="utf-8",
    )

    assert ".get(" in source
    assert ".get_by_digest(" in source

    for forbidden in (
        ".create(",
        ".update(",
        ".replace(",
        ".delete(",
        ".upsert(",
    ):
        assert forbidden not in source


# ============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# ============================================================================
# VERSION: v1.0.1-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY-TEST
# AUTHORITY BOUNDARY: immutable correspondence persistence contract only.
# HIERARCHY DEPENDENCY: authoritative read-only ID/digest resolution.
# TENANT / COMMERCIAL / CLASSIFICATION / ACTIVATION AUTHORITY: none.
# NETWORK AUTHORITY: none.
# FINANCIAL EXECUTION AUTHORITY: none.
# END OF WILSY OS SOVEREIGN ARTIFACT
