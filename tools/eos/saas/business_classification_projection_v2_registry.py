"""WILSY OS — Business Classification Projection V2 Registry.

TITLE: Business Classification Projection V2 Registry
VERSION: v2.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION-REGISTRY
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Persist immutable business-bound V2 classification projections while
    validating exact Business Identity and official taxonomy snapshot truth.

AUTHORITY BOUNDARY:
- Caller-owned active transaction required before dependency reads.
- Business Identity dependency is read-only and exact-revision/fingerprint bound.
- Official taxonomy snapshot dependency is read-only.
- V1 persistence remains separate and untouched.
- No latest/current identity or projection inference.
- No entitlement, subscription, permission, activation, regulatory, AI, or
  financial authority.
"""

from __future__ import annotations

from typing import Any, Mapping

from pymongo import ASCENDING
from pymongo.errors import (
    DuplicateKeyError,
    PyMongoError,
)

from tools.eos.saas.domain.business_classification_projection_v2 import (
    BusinessClassificationProjectionV2,
    BusinessClassificationProjectionV2Error,
)


VERSION = (
    "v2.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION-REGISTRY"
)

COLLECTION_NAME = (
    "business_classification_projections_v2"
)


class BusinessClassificationProjectionV2RegistryError(
    ValueError
):
    """Raised when V2 projection persistence truth is invalid."""


class BusinessClassificationProjectionV2Registry:
    """Insert-only V2 business classification persistence authority."""

    def __init__(
        self,
        collection: Any,
        *,
        business_identity_registry: Any,
        snapshot_registry: Any,
    ) -> None:
        """Bind persistence and read-only dependency authorities."""
        self._collection = collection
        self._business_identity_registry = (
            business_identity_registry
        )
        self._snapshot_registry = (
            snapshot_registry
        )

    @staticmethod
    def ensure_indexes(
        collection: Any,
    ) -> None:
        """Create the exact immutable V2 registry indexes."""
        collection.create_index(
            [
                (
                    "projection_id",
                    ASCENDING,
                )
            ],
            unique=True,
            name=(
                "business_classification_v2_"
                "projection_id_unique"
            ),
        )

        collection.create_index(
            [
                (
                    "fingerprint",
                    ASCENDING,
                )
            ],
            unique=True,
            name=(
                "business_classification_v2_"
                "fingerprint_unique"
            ),
        )

        collection.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "business_identity_id",
                    ASCENDING,
                ),
                (
                    "revision",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=(
                "business_classification_v2_"
                "tenant_business_revision_unique"
            ),
        )

        collection.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "business_identity_id",
                    ASCENDING,
                ),
                (
                    "effective_from",
                    ASCENDING,
                ),
            ],
            name=(
                "business_classification_v2_"
                "tenant_business_effective_from"
            ),
        )

        collection.create_index(
            [
                (
                    "business_identity_id",
                    ASCENDING,
                ),
                (
                    "business_identity_revision",
                    ASCENDING,
                ),
                (
                    "business_identity_fingerprint",
                    ASCENDING,
                ),
            ],
            name=(
                "business_classification_v2_"
                "business_identity_binding"
            ),
        )

        collection.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "business_identity_id",
                    ASCENDING,
                ),
                (
                    "supersedes_projection_id",
                    ASCENDING,
                ),
            ],
            name=(
                "business_classification_v2_"
                "tenant_supersedes_projection"
            ),
        )

    @staticmethod
    def _require_active_transaction(
        session: Any,
    ) -> None:
        """Reject before dependency reads or durable writes."""
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
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "ACTIVE_TRANSACTION_REQUIRED"
            )

    @staticmethod
    def _strict_candidate(
        value: object,
    ) -> BusinessClassificationProjectionV2:
        """Strictly rehydrate candidate V2 domain truth."""
        if not isinstance(
            value,
            BusinessClassificationProjectionV2,
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_VALUE_INVALID"
            )

        try:
            restored = (
                BusinessClassificationProjectionV2.from_dict(
                    value.to_dict()
                )
            )
        except (
            BusinessClassificationProjectionV2Error,
            TypeError,
            ValueError,
        ) as error:
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_VALUE_INVALID"
            ) from error

        if restored != value:
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "VALUE_REHYDRATION_MISMATCH"
            )

        return restored

    @staticmethod
    def _document(
        row: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Strip Mongo persistence metadata from one durable row."""
        return {
            key: value
            for key, value in row.items()
            if key != "_id"
        }

    @classmethod
    def _hydrate(
        cls,
        row: Mapping[str, Any],
    ) -> BusinessClassificationProjectionV2:
        """Strictly hydrate one durable V2 row."""
        try:
            return (
                BusinessClassificationProjectionV2.from_dict(
                    cls._document(
                        row
                    )
                )
            )
        except (
            BusinessClassificationProjectionV2Error,
            TypeError,
            ValueError,
        ) as error:
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "PERSISTED_RECORD_INVALID"
            ) from error

    def _find_one(
        self,
        query: dict[str, Any],
        *,
        session: Any,
    ) -> Mapping[str, Any] | None:
        """Perform one caller-session-bound durable read."""
        value = self._collection.find_one(
            query,
            session=session,
        )

        if value is None:
            return None

        if not isinstance(
            value,
            Mapping,
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "PERSISTED_RECORD_INVALID"
            )

        return value

    @staticmethod
    def _identity_coordinate(
        value: Any,
    ) -> tuple[
        Any,
        Any,
        Any,
        Any,
    ]:
        """Return exact immutable Business Identity coordinate."""
        return (
            getattr(
                value,
                "business_identity_id",
                None,
            ),
            getattr(
                value,
                "revision",
                None,
            ),
            getattr(
                value,
                "identity_fingerprint",
                None,
            ),
            getattr(
                value,
                "tenant_id",
                None,
            ),
        )

    def _validate_business_identity_binding(
        self,
        value: BusinessClassificationProjectionV2,
        *,
        session: Any,
    ) -> None:
        """Resolve exact revision and fingerprint to the same Business Identity."""
        by_revision = (
            self._business_identity_registry.get_revision(
                value.business_identity_id,
                value.business_identity_revision,
                session=session,
            )
        )

        by_fingerprint = (
            self._business_identity_registry.get_by_fingerprint(
                value.business_identity_fingerprint,
                session=session,
            )
        )

        if (
            by_revision is None
            or by_fingerprint is None
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "BUSINESS_IDENTITY_MISSING"
            )

        revision_coordinate = (
            self._identity_coordinate(
                by_revision
            )
        )

        fingerprint_coordinate = (
            self._identity_coordinate(
                by_fingerprint
            )
        )

        if (
            revision_coordinate
            != fingerprint_coordinate
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "BUSINESS_IDENTITY_BINDING_MISMATCH"
            )

        expected = (
            value.business_identity_id,
            value.business_identity_revision,
            value.business_identity_fingerprint,
            value.tenant_id,
        )

        if (
            revision_coordinate
            != expected
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "BUSINESS_IDENTITY_BINDING_MISMATCH"
            )

    @staticmethod
    def _snapshot_coordinate(
        value: Any,
    ) -> tuple[
        Any,
        Any,
        Any,
        Any,
        Any,
    ]:
        """Return exact immutable taxonomy snapshot coordinate."""
        return (
            getattr(
                value,
                "snapshot_id",
                None,
            ),
            getattr(
                value,
                "snapshot_digest",
                None,
            ),
            getattr(
                value,
                "scheme_id",
                None,
            ),
            getattr(
                value,
                "scheme_version",
                None,
            ),
            getattr(
                value,
                "jurisdiction",
                None,
            ),
        )

    def _resolve_snapshot_binding(
        self,
        *,
        snapshot_id: str,
        snapshot_digest: str,
        scheme_id: str,
        scheme_version: str,
        jurisdiction: str,
        session: Any,
    ) -> None:
        """Resolve exact snapshot ID and digest to one immutable coordinate."""
        by_id = self._snapshot_registry.get(
            snapshot_id,
            session=session,
        )

        by_digest = (
            self._snapshot_registry.get_by_digest(
                snapshot_digest,
                session=session,
            )
        )

        if (
            by_id is None
            or by_digest is None
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "SNAPSHOT_MISSING"
            )

        id_coordinate = (
            self._snapshot_coordinate(
                by_id
            )
        )

        digest_coordinate = (
            self._snapshot_coordinate(
                by_digest
            )
        )

        if (
            id_coordinate
            != digest_coordinate
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "SNAPSHOT_BINDING_MISMATCH"
            )

        expected = (
            snapshot_id,
            snapshot_digest,
            scheme_id,
            scheme_version,
            jurisdiction,
        )

        if (
            id_coordinate
            != expected
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "SNAPSHOT_BINDING_MISMATCH"
            )

    def _validate_snapshot_bindings(
        self,
        value: BusinessClassificationProjectionV2,
        *,
        session: Any,
    ) -> None:
        """Validate every distinct nested taxonomy snapshot exactly once."""
        bindings: dict[
            tuple[str, str],
            tuple[str, str, str],
        ] = {}

        for activity in value.activities:
            for reference in activity.classifications:
                key = (
                    reference.taxonomy_snapshot_id,
                    reference.taxonomy_snapshot_digest,
                )

                coordinate = (
                    reference.scheme_id,
                    reference.scheme_version,
                    reference.jurisdiction,
                )

                previous = bindings.get(
                    key
                )

                if (
                    previous is not None
                    and previous != coordinate
                ):
                    raise BusinessClassificationProjectionV2RegistryError(
                        "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                        "SNAPSHOT_REFERENCE_CONFLICT"
                    )

                bindings[
                    key
                ] = coordinate

        for (
            snapshot_id,
            snapshot_digest,
        ), (
            scheme_id,
            scheme_version,
            jurisdiction,
        ) in bindings.items():
            self._resolve_snapshot_binding(
                snapshot_id=snapshot_id,
                snapshot_digest=snapshot_digest,
                scheme_id=scheme_id,
                scheme_version=scheme_version,
                jurisdiction=jurisdiction,
                session=session,
            )

    def _validate_supersession(
        self,
        value: BusinessClassificationProjectionV2,
        *,
        session: Any,
    ) -> None:
        """Validate caller-declared V2 supersession within the same business."""
        if value.revision == 1:
            return

        superseded_id = (
            value.supersedes_projection_id
        )

        if superseded_id is None:
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "SUPERSESSION_REQUIRED"
            )

        row = self._find_one(
            {
                "projection_id":
                    superseded_id,
            },
            session=session,
        )

        if row is None:
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "SUPERSEDED_PROJECTION_MISSING"
            )

        superseded = self._hydrate(
            row
        )

        if (
            superseded.tenant_id
            != value.tenant_id
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "CROSS_TENANT_SUPERSESSION_FORBIDDEN"
            )

        if (
            superseded.business_identity_id
            != value.business_identity_id
        ):
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "CROSS_BUSINESS_SUPERSESSION_FORBIDDEN"
            )

    def create(
        self,
        value: BusinessClassificationProjectionV2,
        *,
        session: Any,
    ) -> BusinessClassificationProjectionV2:
        """Insert immutable V2 truth or return one exact durable replay."""
        self._require_active_transaction(
            session
        )

        candidate = self._strict_candidate(
            value
        )

        self._validate_business_identity_binding(
            candidate,
            session=session,
        )

        self._validate_snapshot_bindings(
            candidate,
            session=session,
        )

        self._validate_supersession(
            candidate,
            session=session,
        )

        by_identity = self._find_one(
            {
                "projection_id":
                    candidate.projection_id,
            },
            session=session,
        )

        if by_identity is not None:
            durable = self._hydrate(
                by_identity
            )

            if durable == candidate:
                return durable

            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "IDENTITY_CONFLICT"
            )

        by_fingerprint = self._find_one(
            {
                "fingerprint":
                    candidate.fingerprint,
            },
            session=session,
        )

        if by_fingerprint is not None:
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "FINGERPRINT_CONFLICT"
            )

        by_revision = self._find_one(
            {
                "tenant_id":
                    candidate.tenant_id,
                "business_identity_id":
                    candidate.business_identity_id,
                "revision":
                    candidate.revision,
            },
            session=session,
        )

        if by_revision is not None:
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "TENANT_BUSINESS_REVISION_CONFLICT"
            )

        try:
            self._collection.insert_one(
                candidate.to_dict(),
                session=session,
            )
        except DuplicateKeyError as error:
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "CONCURRENT_INSERT_CONFLICT"
            ) from error
        except PyMongoError as error:
            raise BusinessClassificationProjectionV2RegistryError(
                "BUSINESS_CLASSIFICATION_V2_REGISTRY_"
                "INSERT_FAILED"
            ) from error

        return candidate

    def get(
        self,
        projection_id: str,
        *,
        session: Any = None,
    ) -> BusinessClassificationProjectionV2 | None:
        """Read exactly one V2 projection by immutable projection ID."""
        row = self._collection.find_one(
            {
                "projection_id":
                    projection_id,
            },
            session=session,
        )

        if row is None:
            return None

        return self._hydrate(
            row
        )

    def get_by_fingerprint(
        self,
        fingerprint: str,
        *,
        session: Any = None,
    ) -> BusinessClassificationProjectionV2 | None:
        """Read exactly one V2 projection by immutable fingerprint."""
        row = self._collection.find_one(
            {
                "fingerprint":
                    fingerprint,
            },
            session=session,
        )

        if row is None:
            return None

        return self._hydrate(
            row
        )

    def get_by_business_revision(
        self,
        tenant_id: str,
        business_identity_id: str,
        revision: int,
        *,
        session: Any = None,
    ) -> BusinessClassificationProjectionV2 | None:
        """Read one explicit classification revision for one business."""
        row = self._collection.find_one(
            {
                "tenant_id":
                    tenant_id,
                "business_identity_id":
                    business_identity_id,
                "revision":
                    revision,
            },
            session=session,
        )

        if row is None:
            return None

        return self._hydrate(
            row
        )

    def get_by_business(
        self,
        tenant_id: str,
        business_identity_id: str,
        *,
        session: Any = None,
    ) -> tuple[
        BusinessClassificationProjectionV2,
        ...,
    ]:
        """Read explicit immutable classification history for one business."""
        cursor = self._collection.find(
            {
                "tenant_id":
                    tenant_id,
                "business_identity_id":
                    business_identity_id,
            },
            session=session,
        ).sort(
            "revision",
            ASCENDING,
        )

        return tuple(
            self._hydrate(
                row
            )
            for row in cursor
        )

    def get_by_tenant(
        self,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> tuple[
        BusinessClassificationProjectionV2,
        ...,
    ]:
        """Read all V2 business histories in deterministic tenant order."""
        cursor = self._collection.find(
            {
                "tenant_id":
                    tenant_id,
            },
            session=session,
        ).sort(
            [
                (
                    "business_identity_id",
                    ASCENDING,
                ),
                (
                    "revision",
                    ASCENDING,
                ),
            ]
        )

        return tuple(
            self._hydrate(
                row
            )
            for row in cursor
        )


__all__ = [
    "VERSION",
    "COLLECTION_NAME",
    "BusinessClassificationProjectionV2RegistryError",
    "BusinessClassificationProjectionV2Registry",
]


# ARTIFACT: business_classification_projection_v2_registry.py
