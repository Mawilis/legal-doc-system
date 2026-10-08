"""
WILSY OS — Official Taxonomy Correspondence Registry

TITLE:
    WILSY OS Official Taxonomy Correspondence Registry

VERSION:
    v1.0.0-WILSY-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Immutable transaction-bound persistence for certified official taxonomy
    correspondence truth, resolved against authoritative source and target
    hierarchy identity/digest bindings.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/official_taxonomy_correspondence_registry.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.0-WILSY-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY
        - Introduces immutable insert-only correspondence persistence.
        - Requires an active caller transaction before dependency reads or
          persistence writes.
        - Resolves source and target hierarchy identity/digest pairs through
          authoritative hierarchy read surfaces using the same session.
        - Strictly rehydrates candidate and durable correspondence truth
          through OfficialTaxonomyCorrespondence.from_dict().
        - Provides exact replay and fail-closed identity/digest conflict
          handling.
        - Provides immutable identity, digest, source-binding and
          target-binding read surfaces.
        - Defines no TTL, update, replacement or deletion authority.

AUTHORITY BOUNDARY:
    Correspondence persistence only. Hierarchy truth is consumed through
    authoritative read surfaces and is never mutated here.

NETWORK BOUNDARY:
    No remote acquisition or parser authority.

FINANCIAL AUTHORITY BOUNDARY:
    None.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.official_taxonomy_correspondence import (
    OfficialTaxonomyCorrespondence,
)


VERSION: Final[str] = (
    "v1.0.0-WILSY-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "official_taxonomy_correspondences"
)


class OfficialTaxonomyCorrespondenceRegistryError(
    RuntimeError
):
    """Raised when correspondence durable truth cannot be trusted."""


class OfficialTaxonomyCorrespondenceRegistry:
    """Persist immutable correspondence truth against hierarchy authority."""

    def __init__(
        self,
        collection: Any,
        *,
        hierarchy_registry: Any,
    ) -> None:
        """Bind one collection and one authoritative hierarchy reader."""
        self._collection = collection
        self._hierarchy_registry = (
            hierarchy_registry
        )

    @staticmethod
    def ensure_indexes(
        collection: Any,
    ) -> None:
        """Create the exact immutable correspondence index contract."""
        collection.create_index(
            [
                (
                    "correspondence_id",
                    1,
                ),
            ],
            name=(
                "official_taxonomy_correspondence_id_unique"
            ),
            unique=True,
        )

        collection.create_index(
            [
                (
                    "correspondence_digest",
                    1,
                ),
            ],
            name=(
                "official_taxonomy_correspondence_digest_unique"
            ),
            unique=True,
        )

        collection.create_index(
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
            name=(
                "official_taxonomy_correspondence_source_hierarchy_binding"
            ),
        )

        collection.create_index(
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
            name=(
                "official_taxonomy_correspondence_target_hierarchy_binding"
            ),
        )

    @staticmethod
    def _require_active_transaction(
        session: Any,
    ) -> None:
        """Require a caller-owned active transaction."""
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
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_ACTIVE_TRANSACTION_REQUIRED"
                )
            )

    def _resolve_hierarchy(
        self,
        *,
        hierarchy_id: str,
        hierarchy_digest: str,
        role: str,
        session: Any,
    ) -> Any:
        """Resolve one hierarchy by both immutable coordinates."""
        try:
            by_identity = (
                self._hierarchy_registry.get(
                    hierarchy_id,
                    session=session,
                )
            )

            by_digest = (
                self._hierarchy_registry.get_by_digest(
                    hierarchy_digest,
                    session=session,
                )
            )
        except Exception as exc:
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_"
                    + role
                    + "_HIERARCHY_READ_FAILED:"
                    + str(exc)
                )
            ) from exc

        if (
            by_identity is None
            or by_digest is None
        ):
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_"
                    + role
                    + "_HIERARCHY_BINDING_MISSING"
                )
            )

        if (
            by_identity
            != by_digest
        ):
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_"
                    + role
                    + "_HIERARCHY_BINDING_CONFLICT"
                )
            )

        if (
            getattr(
                by_identity,
                "hierarchy_id",
                None,
            )
            != hierarchy_id
            or getattr(
                by_identity,
                "hierarchy_digest",
                None,
            )
            != hierarchy_digest
        ):
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_"
                    + role
                    + "_HIERARCHY_BINDING_CONFLICT"
                )
            )

        return by_identity

    def _resolve_correspondence_hierarchies(
        self,
        value: OfficialTaxonomyCorrespondence,
        *,
        session: Any,
    ) -> tuple[Any, Any]:
        """Resolve both hierarchy authorities for one correspondence."""
        source = self._resolve_hierarchy(
            hierarchy_id=(
                value.source_hierarchy_id
            ),
            hierarchy_digest=(
                value.source_hierarchy_digest
            ),
            role="SOURCE",
            session=session,
        )

        target = self._resolve_hierarchy(
            hierarchy_id=(
                value.target_hierarchy_id
            ),
            hierarchy_digest=(
                value.target_hierarchy_digest
            ),
            role="TARGET",
            session=session,
        )

        return (
            source,
            target,
        )

    def _resolve_document_hierarchies(
        self,
        payload: Mapping[str, Any],
        *,
        session: Any,
    ) -> tuple[Any, Any]:
        """Resolve hierarchy authority from durable binding coordinates."""
        required = (
            "source_hierarchy_id",
            "source_hierarchy_digest",
            "target_hierarchy_id",
            "target_hierarchy_digest",
        )

        for field_name in required:
            value = payload.get(
                field_name
            )

            if (
                not isinstance(
                    value,
                    str,
                )
                or not value
            ):
                raise (
                    OfficialTaxonomyCorrespondenceRegistryError(
                        "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                        "REGISTRY_DURABLE_BINDING_INVALID:"
                        + field_name
                    )
                )

        source = self._resolve_hierarchy(
            hierarchy_id=(
                payload[
                    "source_hierarchy_id"
                ]
            ),
            hierarchy_digest=(
                payload[
                    "source_hierarchy_digest"
                ]
            ),
            role="SOURCE",
            session=session,
        )

        target = self._resolve_hierarchy(
            hierarchy_id=(
                payload[
                    "target_hierarchy_id"
                ]
            ),
            hierarchy_digest=(
                payload[
                    "target_hierarchy_digest"
                ]
            ),
            role="TARGET",
            session=session,
        )

        return (
            source,
            target,
        )

    def _hydrate(
        self,
        document: Mapping[str, Any],
        *,
        session: Any = None,
    ) -> OfficialTaxonomyCorrespondence:
        """Strictly hydrate one durable document against hierarchy truth."""
        if not isinstance(
            document,
            Mapping,
        ):
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_DURABLE_DOCUMENT_INVALID"
                )
            )

        payload = dict(
            document
        )

        payload.pop(
            "_id",
            None,
        )

        source, target = (
            self._resolve_document_hierarchies(
                payload,
                session=session,
            )
        )

        try:
            return (
                OfficialTaxonomyCorrespondence.from_dict(
                    payload,
                    source_hierarchy=source,
                    target_hierarchy=target,
                )
            )
        except Exception as exc:
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_DURABLE_DOCUMENT_CORRUPT:"
                    + str(exc)
                )
            ) from exc

    def _find_documents(
        self,
        query: Mapping[str, Any],
        *,
        session: Any = None,
    ) -> tuple[Mapping[str, Any], ...]:
        """Read immutable documents matching one exact query."""
        try:
            cursor = self._collection.find(
                dict(
                    query
                ),
                session=session,
            )

            return tuple(
                cursor
            )
        except Exception as exc:
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_READ_FAILED:"
                    + str(exc)
                )
            ) from exc

    def _find_one_hydrated(
        self,
        query: Mapping[str, Any],
        *,
        session: Any = None,
    ) -> OfficialTaxonomyCorrespondence | None:
        """Read zero or one exact correspondence and hydrate strictly."""
        documents = self._find_documents(
            query,
            session=session,
        )

        if not documents:
            return None

        if len(
            documents
        ) != 1:
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_DURABLE_MULTIPLICITY_CORRUPT"
                )
            )

        return self._hydrate(
            documents[0],
            session=session,
        )

    def _find_many_hydrated(
        self,
        query: Mapping[str, Any],
        *,
        session: Any = None,
    ) -> tuple[
        OfficialTaxonomyCorrespondence,
        ...,
    ]:
        """Read all exact matches and hydrate each against hierarchy truth."""
        documents = self._find_documents(
            query,
            session=session,
        )

        return tuple(
            self._hydrate(
                document,
                session=session,
            )
            for document in documents
        )

    def create(
        self,
        correspondence: OfficialTaxonomyCorrespondence,
        *,
        session: Any,
    ) -> OfficialTaxonomyCorrespondence:
        """Persist one immutable correspondence inside the caller transaction."""
        self._require_active_transaction(
            session
        )

        if not isinstance(
            correspondence,
            OfficialTaxonomyCorrespondence,
        ):
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_VALUE_TYPE_INVALID"
                )
            )

        source, target = (
            self._resolve_correspondence_hierarchies(
                correspondence,
                session=session,
            )
        )

        try:
            rebound = (
                OfficialTaxonomyCorrespondence.from_dict(
                    correspondence.to_dict(),
                    source_hierarchy=source,
                    target_hierarchy=target,
                )
            )
        except Exception as exc:
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_BINDING_VALIDATION_FAILED:"
                    + str(exc)
                )
            ) from exc

        if (
            rebound
            != correspondence
        ):
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_BINDING_VALIDATION_FAILED"
                )
            )

        by_identity = (
            self._find_one_hydrated(
                {
                    "correspondence_id":
                        correspondence.correspondence_id,
                },
                session=session,
            )
        )

        by_digest = (
            self._find_one_hydrated(
                {
                    "correspondence_digest":
                        correspondence.correspondence_digest,
                },
                session=session,
            )
        )

        if (
            by_identity is not None
            and by_identity
            != correspondence
        ):
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_IDENTITY_CONFLICT"
                )
            )

        if (
            by_digest is not None
            and by_digest
            != correspondence
        ):
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
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
                    OfficialTaxonomyCorrespondenceRegistryError(
                        "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
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

            if (
                durable
                == correspondence
            ):
                return correspondence

            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_PARTIAL_REPLAY_CONFLICT"
                )
            )

        try:
            self._collection.insert_one(
                correspondence.to_dict(),
                session=session,
            )
        except DuplicateKeyError as exc:
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_CONCURRENT_INSERT_CONFLICT"
                )
            ) from exc
        except Exception as exc:
            raise (
                OfficialTaxonomyCorrespondenceRegistryError(
                    "OFFICIAL_TAXONOMY_CORRESPONDENCE_"
                    "REGISTRY_INSERT_FAILED:"
                    + str(exc)
                )
            ) from exc

        return correspondence

    def get(
        self,
        correspondence_id: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomyCorrespondence | None:
        """Read one correspondence by immutable identity."""
        return self._find_one_hydrated(
            {
                "correspondence_id":
                    correspondence_id,
            },
            session=session,
        )

    def get_by_digest(
        self,
        correspondence_digest: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomyCorrespondence | None:
        """Read one correspondence by immutable semantic digest."""
        return self._find_one_hydrated(
            {
                "correspondence_digest":
                    correspondence_digest,
            },
            session=session,
        )

    def get_by_source_hierarchy_binding(
        self,
        hierarchy_id: str,
        hierarchy_digest: str,
        *,
        session: Any = None,
    ) -> tuple[
        OfficialTaxonomyCorrespondence,
        ...,
    ]:
        """Read correspondences bound to one source hierarchy."""
        return self._find_many_hydrated(
            {
                "source_hierarchy_id":
                    hierarchy_id,
                "source_hierarchy_digest":
                    hierarchy_digest,
            },
            session=session,
        )

    def get_by_target_hierarchy_binding(
        self,
        hierarchy_id: str,
        hierarchy_digest: str,
        *,
        session: Any = None,
    ) -> tuple[
        OfficialTaxonomyCorrespondence,
        ...,
    ]:
        """Read correspondences bound to one target hierarchy."""
        return self._find_many_hydrated(
            {
                "target_hierarchy_id":
                    hierarchy_id,
                "target_hierarchy_digest":
                    hierarchy_digest,
            },
            session=session,
        )


# ============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# ============================================================================
# VERSION: v1.0.0-WILSY-OFFICIAL-TAXONOMY-CORRESPONDENCE-REGISTRY
# AUTHORITY BOUNDARY: immutable correspondence persistence only.
# DEPENDENCY BOUNDARY: source/target hierarchy identity and digest reads only.
# MUTATION BOUNDARY: insert-only; no update, replacement or deletion surface.
# NETWORK AUTHORITY: none.
# FINANCIAL EXECUTION AUTHORITY: none.
# END OF WILSY OS SOVEREIGN ARTIFACT
