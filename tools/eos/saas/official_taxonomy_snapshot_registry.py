# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN PRODUCTION ARTIFACT
OFFICIAL TAXONOMY SNAPSHOT REGISTRY
===============================================================================

TITLE:
    WILSY OS Official Taxonomy Snapshot Registry

VERSION:
    v1.0.1-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Immutable transactional persistence authority for platform-level
    OfficialTaxonomySnapshot truth. The registry stores only validated domain
    serialization, supports exact replay, rejects conflicting durable truth and
    exposes read-only retrieval surfaces without TTL or mutation APIs.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/official_taxonomy_snapshot_registry.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.1-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY
        - Introduces immutable snapshot persistence authority.
        - Requires an active transaction for every create operation.
        - Persists exact OfficialTaxonomySnapshot serialization only.
        - Provides exact replay idempotence after unique-key collision.
        - Rejects conflicting snapshot identity or digest truth.
        - Defines unique snapshot-id and snapshot-digest indexes.
        - Defines read indexes for scheme/version/jurisdiction and supersession.
        - Provides strict domain hydration with corruption rejection.
        - Defines no TTL, update, replace or delete authority.
        - Defines no acquisition, parsing, hierarchy, correspondence, tenant,
          classification, commercial or financial authority.

    v1.0.1-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY
        - Repairs exact replay for real Mongo transaction semantics.
        - Resolves immutable snapshot identity and digest before insert.
        - Returns exact replay without deliberately triggering a unique-index
          violation that would abort the caller-owned transaction.
        - Rejects known identity, digest and corrupt durable conflicts before
          attempting a write.
        - Converts a post-preflight duplicate-key race into a fail-closed
          registry conflict without reading through the aborted transaction.

TENANT BOUNDARY:
    Platform reference truth only. No tenant or principal scoping exists here.

AUTHORITY BOUNDARY:
    OfficialTaxonomySnapshot persistence only. Hierarchy, correspondence,
    acquisition, parsing and tenant classification remain separate authorities.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

NETWORK BOUNDARY:
    No remote fetch, download, crawl or source acquisition occurs here.

RUNTIME SIDE EFFECTS:
    Mongo-compatible collection reads, immutable inserts and index creation only.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Final, Iterable, Mapping

from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.official_taxonomy_snapshot import (
    OfficialTaxonomySnapshot,
    OfficialTaxonomySnapshotError,
)

VERSION: Final[str] = (
    "v1.0.1-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "official_taxonomy_snapshots"
)


class OfficialTaxonomySnapshotRegistryError(RuntimeError):
    """Represent fail-closed snapshot persistence or hydration failure."""


class OfficialTaxonomySnapshotRegistry:
    """Persist immutable OfficialTaxonomySnapshot reference truth.

    Writes require an already-active caller-owned transaction. This registry
    never starts, commits or aborts that transaction and never mutates existing
    snapshot rows.
    """

    def __init__(
        self,
        collection: Any,
    ) -> None:
        """Bind one Mongo-compatible collection."""
        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        """Create exact immutable snapshot registry indexes."""
        self._collection.create_index(
            [
                (
                    "snapshot_id",
                    1,
                ),
            ],
            name=(
                "official_taxonomy_snapshot_id_unique"
            ),
            unique=True,
        )

        self._collection.create_index(
            [
                (
                    "snapshot_digest",
                    1,
                ),
            ],
            name=(
                "official_taxonomy_snapshot_digest_unique"
            ),
            unique=True,
        )

        self._collection.create_index(
            [
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
            ],
            name=(
                "official_taxonomy_scheme_version_jurisdiction"
            ),
        )

        self._collection.create_index(
            [
                (
                    "supersedes_snapshot_id",
                    1,
                ),
            ],
            name=(
                "official_taxonomy_supersedes_snapshot"
            ),
        )

    @staticmethod
    def _require_active_transaction(
        session: Any,
    ) -> None:
        """Require caller-owned active Mongo transaction before write."""
        if (
            session is None
            or getattr(
                session,
                "in_transaction",
                False,
            )
            is not True
        ):
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_ACTIVE_TRANSACTION_REQUIRED"
            )

    @staticmethod
    def _clean_document(
        document: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Remove Mongo transport identity without changing domain truth."""
        value = dict(
            document
        )

        value.pop(
            "_id",
            None,
        )

        return value

    @classmethod
    def _hydrate(
        cls,
        document: Mapping[str, Any],
    ) -> OfficialTaxonomySnapshot:
        """Strictly hydrate one durable row through canonical domain authority."""
        try:
            return OfficialTaxonomySnapshot.from_dict(
                cls._clean_document(
                    document
                )
            )
        except (
            OfficialTaxonomySnapshotError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_CORRUPT_PERSISTED_TRUTH"
            ) from error

    @staticmethod
    def _materialize(
        documents: Iterable[
            Mapping[str, Any]
        ],
    ) -> tuple[
        Mapping[str, Any],
        ...,
    ]:
        """Materialize a Mongo cursor or fake iterable deterministically."""
        return tuple(
            documents
        )

    def _find_all(
        self,
        query: Mapping[str, Any],
        *,
        session: Any = None,
    ) -> tuple[
        Mapping[str, Any],
        ...,
    ]:
        """Return all rows matching a query without mutation."""
        documents = self._collection.find(
            dict(
                query
            ),
            session=session,
        )

        return self._materialize(
            documents
        )

    def _get_single_by_snapshot_id(
        self,
        snapshot_id: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomySnapshot | None:
        """Read one unique snapshot identity and reject impossible multiplicity."""
        rows = self._find_all(
            {
                "snapshot_id": snapshot_id,
            },
            session=session,
        )

        if not rows:
            return None

        if len(rows) != 1:
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SNAPSHOT_ID_AMBIGUOUS"
            )

        return self._hydrate(
            rows[0]
        )

    def create(
        self,
        snapshot: OfficialTaxonomySnapshot,
        *,
        session: Any,
    ) -> OfficialTaxonomySnapshot:
        """Persist one immutable snapshot or return an exact durable replay.

        Durable identity and digest truth are resolved before attempting an
        insert. This avoids deliberately triggering Mongo unique-index errors
        for ordinary replay because a duplicate-key error aborts the active
        transaction. If a concurrent writer wins after clean preflight, the
        resulting DuplicateKeyError fails closed without any post-error read
        through the aborted transaction.
        """
        self._require_active_transaction(
            session
        )

        if not isinstance(
            snapshot,
            OfficialTaxonomySnapshot,
        ):
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_DOMAIN_INVALID"
            )

        document = snapshot.to_dict()

        by_id = self._find_all(
            {
                "snapshot_id": snapshot.snapshot_id,
            },
            session=session,
        )

        by_digest = self._find_all(
            {
                "snapshot_digest": snapshot.snapshot_digest,
            },
            session=session,
        )

        if len(by_id) > 1:
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SNAPSHOT_ID_AMBIGUOUS"
            )

        if len(by_digest) > 1:
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SNAPSHOT_DIGEST_AMBIGUOUS"
            )

        existing_by_id = (
            self._hydrate(
                by_id[0]
            )
            if by_id
            else None
        )

        existing_by_digest = (
            self._hydrate(
                by_digest[0]
            )
            if by_digest
            else None
        )

        if existing_by_id is not None:
            if existing_by_id != snapshot:
                raise OfficialTaxonomySnapshotRegistryError(
                    "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SNAPSHOT_ID_CONFLICT"
                )

            if existing_by_digest is None:
                raise OfficialTaxonomySnapshotRegistryError(
                    "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_DURABLE_DIGEST_BINDING_MISSING"
                )

            if existing_by_digest != snapshot:
                raise OfficialTaxonomySnapshotRegistryError(
                    "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SNAPSHOT_DIGEST_CONFLICT"
                )

            return snapshot

        if existing_by_digest is not None:
            if existing_by_digest != snapshot:
                raise OfficialTaxonomySnapshotRegistryError(
                    "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SNAPSHOT_DIGEST_CONFLICT"
                )

            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_DURABLE_IDENTITY_BINDING_MISSING"
            )

        try:
            self._collection.insert_one(
                dict(
                    document
                ),
                session=session,
            )

        except DuplicateKeyError as error:
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_CONCURRENT_INSERT_CONFLICT"
            ) from error

        return snapshot

    def get(
        self,
        snapshot_id: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomySnapshot | None:
        """Read one snapshot by exact immutable identity."""
        if (
            not isinstance(
                snapshot_id,
                str,
            )
            or not snapshot_id
            or snapshot_id != snapshot_id.strip()
        ):
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SNAPSHOT_ID_INVALID"
            )

        return self._get_single_by_snapshot_id(
            snapshot_id,
            session=session,
        )

    def get_by_digest(
        self,
        snapshot_digest: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomySnapshot | None:
        """Read one snapshot by unique canonical snapshot digest."""
        if (
            not isinstance(
                snapshot_digest,
                str,
            )
            or len(
                snapshot_digest
            )
            != 128
            or snapshot_digest
            != snapshot_digest.lower()
            or any(
                character
                not in "0123456789abcdef"
                for character
                in snapshot_digest
            )
        ):
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SNAPSHOT_DIGEST_INVALID"
            )

        rows = self._find_all(
            {
                "snapshot_digest": snapshot_digest,
            },
            session=session,
        )

        if not rows:
            return None

        if len(rows) != 1:
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SNAPSHOT_DIGEST_AMBIGUOUS"
            )

        snapshot = self._hydrate(
            rows[0]
        )

        if (
            snapshot.snapshot_digest
            != snapshot_digest
        ):
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_DIGEST_BINDING_MISMATCH"
            )

        return snapshot

    def get_by_scheme_version_jurisdiction(
        self,
        *,
        scheme_id: str,
        scheme_version: str,
        jurisdiction: str,
        session: Any = None,
    ) -> tuple[
        OfficialTaxonomySnapshot,
        ...,
    ]:
        """Read snapshots matching exact scheme/version/jurisdiction coordinates."""
        for name, value in (
            (
                "scheme_id",
                scheme_id,
            ),
            (
                "scheme_version",
                scheme_version,
            ),
            (
                "jurisdiction",
                jurisdiction,
            ),
        ):
            if (
                not isinstance(
                    value,
                    str,
                )
                or not value
                or value != value.strip()
            ):
                raise OfficialTaxonomySnapshotRegistryError(
                    "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_"
                    + name.upper()
                    + "_INVALID"
                )

        rows = self._find_all(
            {
                "scheme_id": scheme_id,
                "scheme_version": scheme_version,
                "jurisdiction": jurisdiction,
            },
            session=session,
        )

        hydrated = tuple(
            self._hydrate(
                row
            )
            for row in rows
        )

        return tuple(
            sorted(
                hydrated,
                key=lambda value: (
                    value.release_date,
                    value.effective_from,
                    value.snapshot_id,
                ),
            )
        )

    def find_superseding_snapshots(
        self,
        superseded_snapshot_id: str,
        *,
        session: Any = None,
    ) -> tuple[
        OfficialTaxonomySnapshot,
        ...,
    ]:
        """Read immutable snapshots that explicitly supersede one identity."""
        if (
            not isinstance(
                superseded_snapshot_id,
                str,
            )
            or not superseded_snapshot_id
            or superseded_snapshot_id
            != superseded_snapshot_id.strip()
        ):
            raise OfficialTaxonomySnapshotRegistryError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_REGISTRY_SUPERSEDED_SNAPSHOT_ID_INVALID"
            )

        rows = self._find_all(
            {
                "supersedes_snapshot_id": superseded_snapshot_id,
            },
            session=session,
        )

        hydrated = tuple(
            self._hydrate(
                row
            )
            for row in rows
        )

        return tuple(
            sorted(
                hydrated,
                key=lambda value: (
                    value.release_date,
                    value.effective_from,
                    value.snapshot_id,
                ),
            )
        )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: official_taxonomy_snapshot_registry.py
# VERSION: v1.0.1-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT-REGISTRY
# AUTHORITY BOUNDARY: immutable platform OfficialTaxonomySnapshot persistence
# only; no hierarchy, correspondence, acquisition, parsing, tenant
# classification, service activation, commercial or financial authority
# TRANSACTION POSTURE: caller-owned active transaction required for writes
# IMMUTABILITY POSTURE: insert-only; exact replay allowed; conflicts rejected
# TTL / DELETION POSTURE: no TTL, update, replace or delete authority
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
