"""WILSY OS — immutable business-classification projection registry.

TITLE: Business Classification Projection Registry
VERSION: v1.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION-REGISTRY
AUTHORITY: Wilsy OS Core Governance
PURPOSE:
    Persist immutable tenant-scoped BusinessClassificationProjection history
    while validating each captured taxonomy reference against certified
    Official Taxonomy Snapshot authority.

ARCHITECTURAL BOUNDARY:
- Business classification truth only.
- Insert-only immutable projection history.
- Caller-owned active transaction required before dependency reads or writes.
- Snapshot dependency is read-only.
- Snapshot ID + digest must resolve the same authoritative snapshot.
- Scheme ID, scheme version and jurisdiction must match that snapshot.
- Classification code remains captured classification truth and is not promoted
  to hierarchy/category authority.
- No hierarchy or correspondence dependency.
- No latest/current authority.
- No N-1 supersession inference.
- No entitlement, permission, authorization-role, business-role, record-scope,
  service-pack activation, workflow activation, AI execution, regulatory-status
  inference, equivalence inference, billing, payment, settlement or financial
  execution authority.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.business_classification_projection import (
    BusinessClassificationProjection,
    BusinessClassificationProjectionError,
)


VERSION = (
    "v1.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION-REGISTRY"
)

COLLECTION_NAME = "business_classification_projections"


class BusinessClassificationProjectionRegistryError(
    RuntimeError
):
    """Raised when classification projection persistence fails closed."""


class BusinessClassificationProjectionRegistry:
    """Insert-only registry for immutable tenant classification projections."""

    def __init__(
        self,
        collection: Any,
        *,
        snapshot_registry: Any,
    ) -> None:
        """Bind persistence and read-only snapshot authority."""
        self._collection = collection
        self._snapshot_registry = snapshot_registry

    @staticmethod
    def ensure_indexes(
        collection: Any,
    ) -> None:
        """Create the exact frozen immutable registry indexes."""
        collection.create_index(
            [("projection_id", ASCENDING)],
            unique=True,
            name="business_classification_projection_id_unique",
        )

        collection.create_index(
            [("fingerprint", ASCENDING)],
            unique=True,
            name="business_classification_projection_fingerprint_unique",
        )

        collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("revision", ASCENDING),
            ],
            unique=True,
            name="business_classification_tenant_revision_unique",
        )

        collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("effective_from", ASCENDING),
            ],
            name="business_classification_tenant_effective_from",
        )

        collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("supersedes_projection_id", ASCENDING),
            ],
            name="business_classification_tenant_supersedes",
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
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_ACTIVE_TRANSACTION_REQUIRED"
            )

    @staticmethod
    def _strict_candidate(
        value: object,
    ) -> BusinessClassificationProjection:
        """Rehydrate candidate domain truth before persistence."""
        if not isinstance(
            value,
            BusinessClassificationProjection,
        ):
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_VALUE_INVALID"
            )

        try:
            restored = (
                BusinessClassificationProjection.from_dict(
                    value.to_dict()
                )
            )
        except (
            BusinessClassificationProjectionError,
            TypeError,
            ValueError,
        ) as error:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_VALUE_INVALID"
            ) from error

        if restored != value:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_VALUE_REHYDRATION_MISMATCH"
            )

        return restored

    @staticmethod
    def _document(
        row: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Strip persistence metadata without mutating durable input."""
        value = deepcopy(dict(row))
        value.pop("_id", None)
        return value

    @classmethod
    def _hydrate(
        cls,
        row: Mapping[str, Any],
    ) -> BusinessClassificationProjection:
        """Strictly hydrate durable projection truth."""
        try:
            return (
                BusinessClassificationProjection.from_dict(
                    cls._document(row)
                )
            )
        except (
            BusinessClassificationProjectionError,
            TypeError,
            ValueError,
        ) as error:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_PERSISTED_RECORD_INVALID"
            ) from error

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
        """Resolve one immutable snapshot binding by ID and digest."""
        try:
            by_identity = self._snapshot_registry.get(
                snapshot_id,
                session=session,
            )

            by_digest = (
                self._snapshot_registry.get_by_digest(
                    snapshot_digest,
                    session=session,
                )
            )
        except Exception as error:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_SNAPSHOT_READ_FAILED"
            ) from error

        if (
            by_identity is None
            or by_digest is None
        ):
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_SNAPSHOT_BINDING_MISSING"
            )

        if by_identity != by_digest:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_SNAPSHOT_BINDING_CONFLICT"
            )

        if (
            getattr(by_identity, "snapshot_id", None)
            != snapshot_id
            or getattr(
                by_identity,
                "snapshot_digest",
                None,
            )
            != snapshot_digest
        ):
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_SNAPSHOT_BINDING_CONFLICT"
            )

        if (
            getattr(by_identity, "scheme_id", None)
            != scheme_id
        ):
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_SNAPSHOT_SCHEME_MISMATCH"
            )

        if (
            getattr(
                by_identity,
                "scheme_version",
                None,
            )
            != scheme_version
        ):
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_SNAPSHOT_VERSION_MISMATCH"
            )

        if (
            getattr(
                by_identity,
                "jurisdiction",
                None,
            )
            != jurisdiction
        ):
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_SNAPSHOT_JURISDICTION_MISMATCH"
            )

    def _validate_snapshot_bindings(
        self,
        value: BusinessClassificationProjection,
        *,
        session: Any,
    ) -> None:
        """Validate each distinct nested snapshot binding exactly once."""
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

                coordinates = (
                    reference.scheme_id,
                    reference.scheme_version,
                    reference.jurisdiction,
                )

                previous = bindings.get(key)

                if (
                    previous is not None
                    and previous != coordinates
                ):
                    raise BusinessClassificationProjectionRegistryError(
                        "BUSINESS_CLASSIFICATION_PROJECTION_"
                        "REGISTRY_SNAPSHOT_REFERENCE_CONFLICT"
                    )

                bindings[key] = coordinates

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

    def _find_one(
        self,
        query: dict[str, Any],
        *,
        session: Any,
    ) -> dict[str, Any] | None:
        """Read one durable row using the supplied session."""
        try:
            row = self._collection.find_one(
                query,
                session=session,
            )
        except PyMongoError as error:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_READ_FAILED"
            ) from error

        if row is None:
            return None

        return self._document(row)

    def _validate_supersession(
        self,
        value: BusinessClassificationProjection,
        *,
        session: Any,
    ) -> None:
        """Validate only the caller-declared supersession relation."""
        if value.revision == 1:
            return

        superseded_id = (
            value.supersedes_projection_id
        )

        if superseded_id is None:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_SUPERSESSION_REQUIRED"
            )

        row = self._find_one(
            {
                "projection_id":
                    superseded_id,
            },
            session=session,
        )

        if row is None:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_SUPERSEDED_PROJECTION_MISSING"
            )

        superseded = self._hydrate(row)

        if (
            superseded.tenant_id
            != value.tenant_id
        ):
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_CROSS_TENANT_SUPERSESSION_FORBIDDEN"
            )

    def create(
        self,
        value: BusinessClassificationProjection,
        *,
        session: Any,
    ) -> BusinessClassificationProjection:
        """Insert one immutable projection or return an exact durable replay."""
        self._require_active_transaction(
            session
        )

        candidate = self._strict_candidate(
            value
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

            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_IDENTITY_CONFLICT"
            )

        by_fingerprint = self._find_one(
            {
                "fingerprint":
                    candidate.fingerprint,
            },
            session=session,
        )

        if by_fingerprint is not None:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_FINGERPRINT_CONFLICT"
            )

        by_revision = self._find_one(
            {
                "tenant_id":
                    candidate.tenant_id,
                "revision":
                    candidate.revision,
            },
            session=session,
        )

        if by_revision is not None:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_TENANT_REVISION_CONFLICT"
            )

        try:
            self._collection.insert_one(
                candidate.to_dict(),
                session=session,
            )
        except DuplicateKeyError as error:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_CONCURRENT_INSERT_CONFLICT"
            ) from error
        except PyMongoError as error:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_INSERT_FAILED"
            ) from error

        return candidate

    def get(
        self,
        projection_id: str,
        *,
        session: Any = None,
    ) -> BusinessClassificationProjection | None:
        """Read one projection by immutable projection identity."""
        row = self._find_one(
            {
                "projection_id":
                    projection_id,
            },
            session=session,
        )

        if row is None:
            return None

        return self._hydrate(row)

    def get_by_fingerprint(
        self,
        fingerprint: str,
        *,
        session: Any = None,
    ) -> BusinessClassificationProjection | None:
        """Read one projection by immutable integrity fingerprint."""
        row = self._find_one(
            {
                "fingerprint":
                    fingerprint,
            },
            session=session,
        )

        if row is None:
            return None

        return self._hydrate(row)

    def get_by_tenant_revision(
        self,
        tenant_id: str,
        revision: int,
        *,
        session: Any = None,
    ) -> BusinessClassificationProjection | None:
        """Read one exact tenant/revision projection coordinate."""
        row = self._find_one(
            {
                "tenant_id":
                    tenant_id,
                "revision":
                    revision,
            },
            session=session,
        )

        if row is None:
            return None

        return self._hydrate(row)

    def get_by_tenant(
        self,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> tuple[
        BusinessClassificationProjection,
        ...,
    ]:
        """Read immutable tenant projection history in revision order."""
        try:
            cursor = self._collection.find(
                {
                    "tenant_id":
                        tenant_id,
                },
                session=session,
            ).sort(
                "revision",
                ASCENDING,
            )
        except PyMongoError as error:
            raise BusinessClassificationProjectionRegistryError(
                "BUSINESS_CLASSIFICATION_PROJECTION_"
                "REGISTRY_READ_FAILED"
            ) from error

        return tuple(
            self._hydrate(row)
            for row in cursor
        )


__all__ = [
    "VERSION",
    "COLLECTION_NAME",
    "BusinessClassificationProjectionRegistryError",
    "BusinessClassificationProjectionRegistry",
]


# ARTIFACT: business_classification_projection_registry.py
