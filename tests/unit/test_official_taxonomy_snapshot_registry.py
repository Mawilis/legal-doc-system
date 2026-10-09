# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN TEST-FIRST CERTIFICATION ARTIFACT
OFFICIAL TAXONOMY SNAPSHOT REGISTRY
===============================================================================

TITLE:
    WILSY OS Official Taxonomy Snapshot Registry Direct Unit Contract

VERSION:
    v1.0.4-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Freezes immutable transactional persistence semantics for platform-level
    OfficialTaxonomySnapshot truth without creating hierarchy, correspondence,
    tenant-classification, acquisition, parsing or commercial authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_official_taxonomy_snapshot_registry.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.4-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-TEST
        - Initial direct unit registry contract.
        - Requires active transaction before write.
        - Requires immutable insert-only persistence.
        - Requires exact replay idempotence.
        - Rejects same snapshot identity with different truth.
        - Freezes unique snapshot_id and snapshot_digest indexes.
        - Freezes scheme/version/jurisdiction and supersession read indexes.
        - Forbids TTL deletion indexes.
        - Forbids update, replace and delete mutation APIs.
        - Requires strict domain hydration and corruption rejection.
        - Keeps remote acquisition and parsing outside registry authority.

    v1.0.4-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-TEST
        - Repairs Mongo-like direct-test fixture semantics before production.
        - Uses pymongo DuplicateKeyError instead of a test-only exception type.
        - Adds collection.find() for legitimate multi-row read contracts.
        - Makes duplicate-digest ambiguity observable rather than hidden by
          find_one() first-match behavior.
        - Keeps production module absent and expected RED unchanged.

    v1.0.4-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-TEST
        - Freezes real-Mongo replay repair semantics discovered by R15.
        - Exact replay must be recognized by immutable preflight reads before
          attempting a duplicate insert.
        - Same identity with conflicting truth must reject before insert.
        - Same digest under a different identity must reject before insert.
        - A post-preflight duplicate-key race must fail closed without trying
          to read again through the now-aborted transaction.

    v1.0.4-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-TEST
        - Corrects digest-collision regression semantics.
        - Snapshot identity participates in canonical snapshot integrity, so
          same digest with another valid snapshot identity cannot be built as
          a legitimate domain candidate.
        - Freezes the actual invariant instead: a durable row presenting the
          candidate digest under another identity is corrupt persisted truth
          and must be rejected during preflight before insert.

    v1.0.4-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-TEST
        - Freezes production registry version v1.0.1 for the behavioral
          replay-preflight transaction repair proven necessary by real Mongo.
        - Requires exact replay and known conflicts to resolve before insert.
        - Requires a post-preflight duplicate-key race to fail closed without
          reading through the transaction Mongo has already aborted.
        - Keeps production v1.0.0 and the R15 real-Mongo certificate
          byte-identical until the separately bounded production repair.

TENANT BOUNDARY:
    Platform reference truth only; no tenant or principal scoping.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

FUTURE PRODUCTION PATH:
    tools/eos/saas/official_taxonomy_snapshot_registry.py
===============================================================================
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.official_taxonomy_snapshot import (
    OfficialTaxonomyArtifactKind,
    OfficialTaxonomySnapshot,
    OfficialTaxonomySourceArtifact,
)

from tools.eos.saas.official_taxonomy_snapshot_registry import (
    COLLECTION_NAME,
    VERSION,
    OfficialTaxonomySnapshotRegistry,
    OfficialTaxonomySnapshotRegistryError,
)


EXPECTED_VERSION = (
    "v1.0.1-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY"
)

EXPECTED_COLLECTION_NAME = (
    "official_taxonomy_snapshots"
)


class FakeSession:
    """Represent minimal active/inactive transaction state."""

    def __init__(
        self,
        *,
        in_transaction: bool,
    ) -> None:
        self.in_transaction = in_transaction


class FakeCollection:
    """Represent deterministic Mongo-like storage for direct registry tests."""

    def __init__(self) -> None:
        self.documents: list[
            dict[str, Any]
        ] = []

        self.indexes: list[
            tuple[
                tuple[
                    tuple[str, int],
                    ...
                ],
                dict[str, Any],
            ]
        ] = []

        self.insert_calls = 0
        self.find_calls = 0

    def create_index(
        self,
        keys: list[
            tuple[str, int]
        ],
        **kwargs: Any,
    ) -> str:
        self.indexes.append(
            (
                tuple(keys),
                dict(kwargs),
            )
        )

        return str(
            kwargs.get(
                "name",
                "index",
            )
        )

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: FakeSession,
    ) -> object:
        del session

        self.insert_calls += 1

        snapshot_id = document[
            "snapshot_id"
        ]

        snapshot_digest = document[
            "snapshot_digest"
        ]

        for existing in self.documents:
            if (
                existing[
                    "snapshot_id"
                ]
                == snapshot_id
                or existing[
                    "snapshot_digest"
                ]
                == snapshot_digest
            ):
                raise DuplicateKeyError(
                    "duplicate key"
                )

        self.documents.append(
            dict(document)
        )

        return object()

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: FakeSession | None = None,
    ) -> dict[str, Any] | None:
        del session

        self.find_calls += 1

        for document in self.documents:
            if all(
                document.get(key)
                == value
                for key, value in query.items()
            ):
                return dict(
                    document
                )

        return None

    def find(
        self,
        query: dict[str, Any],
        *,
        session: FakeSession | None = None,
    ) -> list[dict[str, Any]]:
        del session

        self.find_calls += 1

        return [
            dict(document)
            for document in self.documents
            if all(
                document.get(key)
                == value
                for key, value in query.items()
            )
        ]

    def update_one(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        raise AssertionError(
            "UPDATE_API_MUST_NOT_BE_USED"
        )

    def replace_one(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        raise AssertionError(
            "REPLACE_API_MUST_NOT_BE_USED"
        )

    def delete_one(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        raise AssertionError(
            "DELETE_API_MUST_NOT_BE_USED"
        )


def digest(
    value: bytes,
) -> str:
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
            + artifact_id
        ),
        media_type="text/csv",
        language_tag="en",
        source_digest=digest(
            artifact_id.encode(
                "utf-8"
            )
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
        rights_reference=(
            "official publisher terms"
        ),
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
            artifact(),
        ),
        supersedes_snapshot_id=supersedes_snapshot_id,
    )


def registry(
    collection: FakeCollection | None = None,
) -> tuple[
    OfficialTaxonomySnapshotRegistry,
    FakeCollection,
]:
    actual = (
        collection
        if collection is not None
        else FakeCollection()
    )

    return (
        OfficialTaxonomySnapshotRegistry(
            actual
        ),
        actual,
    )


def test_version_and_collection_name_are_exact() -> None:
    assert VERSION == EXPECTED_VERSION
    assert COLLECTION_NAME == EXPECTED_COLLECTION_NAME


def test_registry_exposes_only_snapshot_persistence_authority() -> None:
    public = {
        name
        for name in vars(
            OfficialTaxonomySnapshotRegistry
        )
        if not name.startswith(
            "_"
        )
    }

    forbidden = {
        "update",
        "replace",
        "delete",
        "download",
        "fetch",
        "parse",
        "normalize",
        "classify",
        "activate",
        "grant",
        "authorize",
    }

    assert forbidden.isdisjoint(
        public
    )


def test_ensure_indexes_freezes_required_index_contract() -> None:
    value, collection = registry()

    value.ensure_indexes()

    by_name = {
        options.get(
            "name"
        ): (
            keys,
            options,
        )
        for keys, options in collection.indexes
    }

    assert (
        by_name[
            "official_taxonomy_snapshot_id_unique"
        ][0]
        == (
            (
                "snapshot_id",
                1,
            ),
        )
    )

    assert (
        by_name[
            "official_taxonomy_snapshot_id_unique"
        ][1].get(
            "unique"
        )
        is True
    )

    assert (
        by_name[
            "official_taxonomy_snapshot_digest_unique"
        ][0]
        == (
            (
                "snapshot_digest",
                1,
            ),
        )
    )

    assert (
        by_name[
            "official_taxonomy_snapshot_digest_unique"
        ][1].get(
            "unique"
        )
        is True
    )

    assert (
        by_name[
            "official_taxonomy_scheme_version_jurisdiction"
        ][0]
        == (
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
        )
    )

    assert (
        by_name[
            "official_taxonomy_supersedes_snapshot"
        ][0]
        == (
            (
                "supersedes_snapshot_id",
                1,
            ),
        )
    )


def test_registry_defines_no_ttl_index() -> None:
    value, collection = registry()

    value.ensure_indexes()

    for _keys, options in collection.indexes:
        lowered = {
            str(key).lower(): value
            for key, value in options.items()
        }

        assert (
            "expireafterseconds"
            not in lowered
        )


def test_create_requires_active_transaction_before_write() -> None:
    value, collection = registry()

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.create(
            snapshot(),
            session=FakeSession(
                in_transaction=False
            ),
        )

    assert collection.insert_calls == 0


def test_create_rejects_missing_session_before_write() -> None:
    value, collection = registry()

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.create(
            snapshot(),
            session=None,
        )

    assert collection.insert_calls == 0


def test_create_accepts_only_official_taxonomy_snapshot_domain() -> None:
    value, collection = registry()

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.create(
            object(),  # type: ignore[arg-type]
            session=FakeSession(
                in_transaction=True
            ),
        )

    assert collection.insert_calls == 0


def test_create_persists_exact_domain_serialization() -> None:
    value, collection = registry()

    expected = snapshot()

    returned = value.create(
        expected,
        session=FakeSession(
            in_transaction=True
        ),
    )

    assert returned == expected
    assert collection.documents == [
        expected.to_dict()
    ]


def test_exact_replay_is_idempotent() -> None:
    value, collection = registry()
    session = FakeSession(
        in_transaction=True
    )

    expected = snapshot()

    first = value.create(
        expected,
        session=session,
    )

    second = value.create(
        expected,
        session=session,
    )

    assert first == expected
    assert second == expected
    assert len(
        collection.documents
    ) == 1


def test_same_snapshot_identity_with_different_truth_is_rejected() -> None:
    value, _collection = registry()
    session = FakeSession(
        in_transaction=True
    )

    value.create(
        snapshot(),
        session=session,
    )

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.create(
            snapshot(
                publisher_status="corrected official"
            ),
            session=session,
        )


def test_same_digest_under_different_snapshot_identity_is_rejected() -> None:
    value, collection = registry()
    session = FakeSession(
        in_transaction=True
    )

    original = snapshot()

    value.create(
        original,
        session=session,
    )

    forged = original.to_dict()
    forged[
        "snapshot_id"
    ] = "SNAPSHOT-OTHER"

    collection.documents.append(
        forged
    )

    assert len(
        collection.find(
            {
                "snapshot_digest": original.snapshot_digest,
            },
            session=session,
        )
    ) == 2

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.get_by_digest(
            original.snapshot_digest,
            session=session,
        )


def test_get_returns_strictly_hydrated_domain() -> None:
    value, _collection = registry()
    session = FakeSession(
        in_transaction=True
    )

    expected = snapshot()

    value.create(
        expected,
        session=session,
    )

    observed = value.get(
        expected.snapshot_id,
        session=session,
    )

    assert observed == expected


def test_get_missing_returns_none() -> None:
    value, _collection = registry()

    assert (
        value.get(
            "MISSING",
            session=FakeSession(
                in_transaction=False
            ),
        )
        is None
    )


def test_get_by_digest_returns_exact_snapshot() -> None:
    value, _collection = registry()
    session = FakeSession(
        in_transaction=True
    )

    expected = snapshot()

    value.create(
        expected,
        session=session,
    )

    observed = value.get_by_digest(
        expected.snapshot_digest,
        session=session,
    )

    assert observed == expected


def test_corrupt_persisted_digest_is_rejected() -> None:
    value, collection = registry()
    expected = snapshot()

    corrupt = expected.to_dict()
    corrupt[
        "snapshot_digest"
    ] = "0" * 128

    collection.documents.append(
        corrupt
    )

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.get(
            expected.snapshot_id,
            session=FakeSession(
                in_transaction=False
            ),
        )


def test_extra_persisted_field_is_rejected() -> None:
    value, collection = registry()
    expected = snapshot()

    corrupt = expected.to_dict()
    corrupt[
        "unexpected"
    ] = True

    collection.documents.append(
        corrupt
    )

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.get(
            expected.snapshot_id,
            session=FakeSession(
                in_transaction=False
            ),
        )


def test_get_by_scheme_version_jurisdiction_is_read_only() -> None:
    value, collection = registry()
    session = FakeSession(
        in_transaction=True
    )

    first = snapshot(
        snapshot_id="S1",
        scheme_version="REV4",
    )

    second = snapshot(
        snapshot_id="S2",
        scheme_version="REV5",
        supersedes_snapshot_id="S1",
    )

    value.create(
        first,
        session=session,
    )

    value.create(
        second,
        session=session,
    )

    before = list(
        collection.documents
    )

    result = value.get_by_scheme_version_jurisdiction(
        scheme_id="ISIC",
        scheme_version="REV5",
        jurisdiction="GLOBAL",
        session=FakeSession(
            in_transaction=False
        ),
    )

    assert result == (
        second,
    )

    assert collection.documents == before


def test_find_superseding_snapshots_is_read_only() -> None:
    value, collection = registry()
    session = FakeSession(
        in_transaction=True
    )

    first = snapshot(
        snapshot_id="S1",
        scheme_version="REV4",
    )

    second = snapshot(
        snapshot_id="S2",
        scheme_version="REV5",
        supersedes_snapshot_id="S1",
    )

    value.create(
        first,
        session=session,
    )

    value.create(
        second,
        session=session,
    )

    before = list(
        collection.documents
    )

    result = value.find_superseding_snapshots(
        "S1",
        session=FakeSession(
            in_transaction=False
        ),
    )

    assert result == (
        second,
    )

    assert collection.documents == before


def test_registry_has_no_mutation_methods_after_create() -> None:
    forbidden = {
        "update",
        "replace",
        "delete",
        "delete_one",
        "delete_many",
        "update_one",
        "update_many",
        "replace_one",
    }

    public = {
        name
        for name in vars(
            OfficialTaxonomySnapshotRegistry
        )
        if not name.startswith(
            "_"
        )
    }

    assert forbidden.isdisjoint(
        public
    )


def test_registry_contains_no_tenant_fields_or_scope() -> None:
    names = {
        name.lower()
        for name in vars(
            OfficialTaxonomySnapshotRegistry
        )
    }

    assert not any(
        "tenant" in name
        or "principal" in name
        for name in names
    )


def test_registry_contains_no_network_or_parser_methods() -> None:
    names = {
        name.lower()
        for name in vars(
            OfficialTaxonomySnapshotRegistry
        )
    }

    forbidden_fragments = (
        "fetch",
        "download",
        "crawl",
        "http",
        "parse",
        "normalize",
        "normalise",
        "classify",
    )

    assert not any(
        fragment in name
        for name in names
        for fragment in forbidden_fragments
    )


def test_snapshot_registry_does_not_accept_hierarchy_or_correspondence() -> None:
    value, collection = registry()

    for invalid in (
        {
            "hierarchy_id": "H1",
        },
        {
            "correspondence_id": "C1",
        },
    ):
        with pytest.raises(
            OfficialTaxonomySnapshotRegistryError
        ):
            value.create(
                invalid,  # type: ignore[arg-type]
                session=FakeSession(
                    in_transaction=True
                ),
            )

    assert collection.insert_calls == 0


def test_registry_never_calls_update_replace_or_delete_collection_apis() -> None:
    value, _collection = registry()
    session = FakeSession(
        in_transaction=True
    )

    expected = snapshot()

    value.create(
        expected,
        session=session,
    )

    assert (
        value.get(
            expected.snapshot_id,
            session=session,
        )
        == expected
    )


def test_multi_row_reads_use_collection_read_contract_without_mutation() -> None:
    value, collection = registry()
    session = FakeSession(
        in_transaction=True
    )

    first = snapshot(
        snapshot_id="S1",
        scheme_version="REV4",
    )

    second = snapshot(
        snapshot_id="S2",
        scheme_version="REV5",
        supersedes_snapshot_id="S1",
    )

    value.create(
        first,
        session=session,
    )

    value.create(
        second,
        session=session,
    )

    before = [
        dict(document)
        for document in collection.documents
    ]

    by_version = value.get_by_scheme_version_jurisdiction(
        scheme_id="ISIC",
        scheme_version="REV5",
        jurisdiction="GLOBAL",
        session=FakeSession(
            in_transaction=False
        ),
    )

    superseding = value.find_superseding_snapshots(
        "S1",
        session=FakeSession(
            in_transaction=False
        ),
    )

    assert by_version == (
        second,
    )

    assert superseding == (
        second,
    )

    assert collection.documents == before





class ReplayMustNotInsertCollection(FakeCollection):
    """Prove durable exact replay is resolved before any insert attempt."""

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: FakeSession,
    ) -> object:
        del document
        del session

        self.insert_calls += 1

        raise AssertionError(
            "EXACT_REPLAY_MUST_NOT_ATTEMPT_DUPLICATE_INSERT"
        )


class ConflictMustNotInsertCollection(FakeCollection):
    """Prove known immutable conflict is rejected before insert."""

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: FakeSession,
    ) -> object:
        del document
        del session

        self.insert_calls += 1

        raise AssertionError(
            "KNOWN_CONFLICT_MUST_NOT_ATTEMPT_INSERT"
        )


class RaceDuplicateCollection(FakeCollection):
    """Simulate unique collision after an initially-empty preflight."""

    def __init__(self) -> None:
        super().__init__()
        self.read_count = 0

    def find(
        self,
        query: dict[str, Any],
        *,
        session: FakeSession | None = None,
    ) -> list[dict[str, Any]]:
        del query
        del session

        self.read_count += 1
        self.find_calls += 1

        return []

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: FakeSession,
    ) -> object:
        del document
        del session

        self.insert_calls += 1

        raise DuplicateKeyError(
            "concurrent duplicate key"
        )


def test_exact_replay_is_resolved_before_duplicate_insert() -> None:
    expected = snapshot()

    collection = ReplayMustNotInsertCollection()
    collection.documents.append(
        expected.to_dict()
    )

    value = OfficialTaxonomySnapshotRegistry(
        collection
    )

    observed = value.create(
        expected,
        session=FakeSession(
            in_transaction=True
        ),
    )

    assert observed == expected
    assert collection.insert_calls == 0


def test_same_identity_conflict_is_rejected_before_insert() -> None:
    durable = snapshot()

    collection = ConflictMustNotInsertCollection()
    collection.documents.append(
        durable.to_dict()
    )

    value = OfficialTaxonomySnapshotRegistry(
        collection
    )

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.create(
            snapshot(
                publisher_status="different durable truth"
            ),
            session=FakeSession(
                in_transaction=True
            ),
        )

    assert collection.insert_calls == 0


def test_corrupt_durable_digest_collision_is_rejected_before_insert() -> None:
    candidate = snapshot()

    corrupt_durable = candidate.to_dict()
    corrupt_durable[
        "snapshot_id"
    ] = "OTHER-ID"

    collection = ConflictMustNotInsertCollection()
    collection.documents.append(
        corrupt_durable
    )

    value = OfficialTaxonomySnapshotRegistry(
        collection
    )

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.create(
            candidate,
            session=FakeSession(
                in_transaction=True
            ),
        )

    assert collection.insert_calls == 0


def test_post_preflight_duplicate_race_never_reads_after_duplicate_error() -> None:
    collection = RaceDuplicateCollection()

    value = OfficialTaxonomySnapshotRegistry(
        collection
    )

    with pytest.raises(
        OfficialTaxonomySnapshotRegistryError
    ):
        value.create(
            snapshot(),
            session=FakeSession(
                in_transaction=True
            ),
        )

    assert collection.insert_calls == 1

    # Two preflight reads are allowed: snapshot identity + digest.
    # The critical invariant is that no third read occurs after DuplicateKeyError.
    assert collection.read_count == 2


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_official_taxonomy_snapshot_registry.py
# VERSION: v1.0.4-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY-TEST
# AUTHORITY BOUNDARY: immutable platform-level OfficialTaxonomySnapshot
# persistence only; no hierarchy, correspondence, acquisition, parsing, tenant,
# classification, commercial, AI or financial execution authority
# FAIL-CLOSED POSTURE: active transaction required for write, exact replay only,
# conflicting identity/digest and corrupt persisted truth rejected
# TTL / DELETION POSTURE: no TTL indexes and no update/replace/delete APIs
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
