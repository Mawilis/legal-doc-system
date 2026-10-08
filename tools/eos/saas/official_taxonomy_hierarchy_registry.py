"""
WILSY OS — Official Taxonomy Hierarchy Registry

TITLE:
    WILSY OS Official Taxonomy Hierarchy Registry

VERSION:
    v1.0.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Immutable transactional persistence for authoritative official-taxonomy
    hierarchy aggregates after exact durable Snapshot resolution and pure
    hierarchy-domain Snapshot-binding validation.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/official_taxonomy_hierarchy_registry.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY
        - Introduces immutable insert-only hierarchy persistence.
        - Requires a caller-owned active transaction before dependency reads
          or hierarchy writes.
        - Resolves authoritative Snapshot truth independently by identity and
          digest and requires both reads to describe the same durable truth.
        - Delegates cross-object coordinate and source-artifact validation to
          OfficialTaxonomyHierarchy.validate_snapshot_binding().
        - Performs identity and digest replay/conflict preflight before insert.
        - Never reads through a transaction after a DuplicateKeyError race.
        - Provides strict read hydration and platform-reference read indexes.
        - Provides no mutation path after creation and no expiry index.

TENANT BOUNDARY:
    Platform reference persistence only. No customer-specific classification
    or authorization scope is owned here.

AUTHORITY BOUNDARY:
    Persists an already-valid OfficialTaxonomyHierarchy only after its
    authoritative Snapshot dependency has been resolved. Snapshot creation,
    graph construction, correspondence, commercial activation and business
    classification remain outside this registry.

NETWORK BOUNDARY:
    No remote source acquisition, HTTP transport or parsing authority.

FINANCIAL AUTHORITY BOUNDARY:
    None. No payment, settlement, billing or financial execution authority.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Final

from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.official_taxonomy_hierarchy import (
    OfficialTaxonomyHierarchy,
    OfficialTaxonomyHierarchyError,
)


VERSION: Final[str] = (
    "v1.0.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "official_taxonomy_hierarchies"
)


class OfficialTaxonomyHierarchyRegistryError(
    RuntimeError
):
    """Fail-closed hierarchy-registry persistence error."""


class OfficialTaxonomyHierarchyRegistry:
    """Immutable transactional persistence for official hierarchy truth."""

    def __init__(
        self,
        collection: Any,
        *,
        snapshot_registry: Any,
    ) -> None:
        """Bind one hierarchy collection and read-only Snapshot dependency."""
        self._collection = collection
        self._snapshot_registry = (
            snapshot_registry
        )

    @staticmethod
    def ensure_indexes(
        collection: Any,
    ) -> None:
        """Ensure immutable uniqueness and certified read indexes."""
        collection.create_index(
            [
                (
                    "hierarchy_id",
                    1,
                ),
            ],
            name=(
                "official_taxonomy_"
                "hierarchy_id_unique"
            ),
            unique=True,
        )

        collection.create_index(
            [
                (
                    "hierarchy_digest",
                    1,
                ),
            ],
            name=(
                "official_taxonomy_"
                "hierarchy_digest_unique"
            ),
            unique=True,
        )

        collection.create_index(
            [
                (
                    "snapshot_id",
                    1,
                ),
                (
                    "snapshot_digest",
                    1,
                ),
            ],
            name=(
                "official_taxonomy_"
                "hierarchy_snapshot_binding"
            ),
        )

        collection.create_index(
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
                "official_taxonomy_"
                "hierarchy_scheme_version_"
                "jurisdiction"
            ),
        )

    @staticmethod
    def _require_active_transaction(
        session: Any,
    ) -> None:
        """Reject absent or inactive caller transaction before any I/O."""
        if (
            session is None
            or not bool(
                getattr(
                    session,
                    "in_transaction",
                    False,
                )
            )
        ):
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_ACTIVE_TRANSACTION_REQUIRED"
                )
            )

    @staticmethod
    def _document_payload(
        document: Any,
    ) -> dict[str, Any]:
        """Copy one Mongo document while excluding storage metadata."""
        if not isinstance(
            document,
            dict,
        ):
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_DOCUMENT_TYPE_INVALID"
                )
            )

        payload = deepcopy(
            document
        )

        payload.pop(
            "_id",
            None,
        )

        return payload

    @classmethod
    def _hydrate(
        cls,
        document: Any,
    ) -> OfficialTaxonomyHierarchy:
        """Strictly hydrate durable hierarchy truth or reject corruption."""
        try:
            return (
                OfficialTaxonomyHierarchy.from_dict(
                    cls._document_payload(
                        document
                    )
                )
            )
        except (
            OfficialTaxonomyHierarchyRegistryError
        ):
            raise
        except Exception as exc:
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_DURABLE_TRUTH_INVALID:"
                    + str(exc)
                )
            ) from exc

    def _find_documents(
        self,
        query: dict[str, Any],
        *,
        session: Any = None,
    ) -> list[dict[str, Any]]:
        """Read matching durable documents without creating authority."""
        try:
            cursor = self._collection.find(
                query,
                session=session,
            )

            return [
                self._document_payload(
                    row
                )
                for row in cursor
            ]
        except (
            OfficialTaxonomyHierarchyRegistryError
        ):
            raise
        except Exception as exc:
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_READ_FAILED:"
                    + str(exc)
                )
            ) from exc

    def _find_one_hydrated(
        self,
        query: dict[str, Any],
        *,
        session: Any = None,
    ) -> OfficialTaxonomyHierarchy | None:
        """Resolve zero or one hierarchy and fail closed on multiplicity."""
        documents = (
            self._find_documents(
                query,
                session=session,
            )
        )

        if len(
            documents
        ) > 1:
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_MULTIPLE_DURABLE_MATCHES"
                )
            )

        if not documents:
            return None

        return self._hydrate(
            documents[0]
        )

    @staticmethod
    def _same_snapshot_truth(
        left: Any,
        right: Any,
    ) -> bool:
        """Return whether two Snapshot reads represent exactly equal truth."""
        if (
            left is None
            or right is None
        ):
            return False

        try:
            return (
                left.to_dict()
                == right.to_dict()
            )
        except Exception:
            return False

    def _resolve_snapshot(
        self,
        hierarchy: OfficialTaxonomyHierarchy,
        *,
        session: Any,
    ) -> Any:
        """Resolve exact durable Snapshot identity and digest truth."""
        try:
            by_id = (
                self._snapshot_registry.get(
                    hierarchy.snapshot_id,
                    session=session,
                )
            )

            by_digest = (
                self._snapshot_registry.get_by_digest(
                    hierarchy.snapshot_digest,
                    session=session,
                )
            )
        except Exception as exc:
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_SNAPSHOT_READ_FAILED:"
                    + str(exc)
                )
            ) from exc

        if (
            by_id is None
            or by_digest is None
        ):
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_SNAPSHOT_BINDING_MISSING"
                )
            )

        if not self._same_snapshot_truth(
            by_id,
            by_digest,
        ):
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_SNAPSHOT_BINDING_CONFLICT"
                )
            )

        try:
            hierarchy.validate_snapshot_binding(
                by_id
            )
        except (
            OfficialTaxonomyHierarchyError
        ) as exc:
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    str(exc)
                )
            ) from exc
        except Exception as exc:
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_SNAPSHOT_BINDING_INVALID:"
                    + str(exc)
                )
            ) from exc

        return by_id

    def create(
        self,
        hierarchy: OfficialTaxonomyHierarchy,
        *,
        session: Any,
    ) -> OfficialTaxonomyHierarchy:
        """Persist one hierarchy immutably inside the caller transaction."""
        self._require_active_transaction(
            session
        )

        if not isinstance(
            hierarchy,
            OfficialTaxonomyHierarchy,
        ):
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_VALUE_TYPE_INVALID"
                )
            )

        self._resolve_snapshot(
            hierarchy,
            session=session,
        )

        by_identity = (
            self._find_one_hydrated(
                {
                    "hierarchy_id":
                        hierarchy.hierarchy_id,
                },
                session=session,
            )
        )

        by_digest = (
            self._find_one_hydrated(
                {
                    "hierarchy_digest":
                        hierarchy.hierarchy_digest,
                },
                session=session,
            )
        )

        if (
            by_identity is not None
            and by_identity
            != hierarchy
        ):
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_IDENTITY_CONFLICT"
                )
            )

        if (
            by_digest is not None
            and by_digest
            != hierarchy
        ):
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_DIGEST_CONFLICT"
                )
            )

        if (
            by_identity is not None
            and by_digest is not None
        ):
            if (
                by_identity
                != by_digest
            ):
                raise (
                    OfficialTaxonomyHierarchyRegistryError(
                        "OFFICIAL_TAXONOMY_HIERARCHY_"
                        "REGISTRY_REPLAY_CONFLICT"
                    )
                )

            return by_identity

        if (
            by_identity is not None
            or by_digest is not None
        ):
            durable = (
                by_identity
                if by_identity is not None
                else by_digest
            )

            if durable == hierarchy:
                return hierarchy

            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_PARTIAL_REPLAY_CONFLICT"
                )
            )

        try:
            self._collection.insert_one(
                hierarchy.to_dict(),
                session=session,
            )
        except DuplicateKeyError as exc:
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_CONCURRENT_INSERT_CONFLICT"
                )
            ) from exc
        except Exception as exc:
            raise (
                OfficialTaxonomyHierarchyRegistryError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_"
                    "REGISTRY_INSERT_FAILED:"
                    + str(exc)
                )
            ) from exc

        return hierarchy

    def get(
        self,
        hierarchy_id: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomyHierarchy | None:
        """Read one hierarchy by immutable identity."""
        return self._find_one_hydrated(
            {
                "hierarchy_id":
                    hierarchy_id,
            },
            session=session,
        )

    def get_by_digest(
        self,
        hierarchy_digest: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomyHierarchy | None:
        """Read one hierarchy by immutable semantic digest."""
        return self._find_one_hydrated(
            {
                "hierarchy_digest":
                    hierarchy_digest,
            },
            session=session,
        )

    def get_by_snapshot_binding(
        self,
        snapshot_id: str,
        snapshot_digest: str,
        *,
        session: Any = None,
    ) -> tuple[
        OfficialTaxonomyHierarchy,
        ...,
    ]:
        """Read all hierarchies bound to one exact Snapshot truth."""
        documents = (
            self._find_documents(
                {
                    "snapshot_id":
                        snapshot_id,
                    "snapshot_digest":
                        snapshot_digest,
                },
                session=session,
            )
        )

        return tuple(
            self._hydrate(
                document
            )
            for document in documents
        )

    def get_by_scheme_version_jurisdiction(
        self,
        scheme_id: str,
        scheme_version: str,
        jurisdiction: str,
        *,
        session: Any = None,
    ) -> tuple[
        OfficialTaxonomyHierarchy,
        ...,
    ]:
        """Read hierarchies for exact scheme/version/jurisdiction coordinates."""
        documents = (
            self._find_documents(
                {
                    "scheme_id":
                        scheme_id,
                    "scheme_version":
                        scheme_version,
                    "jurisdiction":
                        jurisdiction,
                },
                session=session,
            )
        )

        return tuple(
            self._hydrate(
                document
            )
            for document in documents
        )


# ============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# ============================================================================
# VERSION: v1.0.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY-REGISTRY
# AUTHORITY BOUNDARY: immutable transaction-bound hierarchy persistence after
# exact authoritative Snapshot resolution and pure-domain binding validation.
# NETWORK AUTHORITY: none.
# FINANCIAL EXECUTION AUTHORITY: none.
# END OF WILSY OS SOVEREIGN ARTIFACT
