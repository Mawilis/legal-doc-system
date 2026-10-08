"""WILSY OS — immutable Business Identity registry.

TITLE: Business Identity Registry
VERSION: v1.0.0-WILSY-BUSINESS-IDENTITY-REGISTRY
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Persist immutable BusinessIdentity revisions within exact tenant ownership
    scope while validating canonical tenant existence through a read-only
    tenant dependency.

AUTHORITY BOUNDARY:
- Insert-only immutable Business Identity revision history.
- Caller-owned active transaction required before dependency reads or writes.
- Tenant dependency is read-only canonical identity validation.
- business_identity_id identifies a subject; revision identifies one immutable
  revision of that subject.
- No unversioned subject read.
- No latest/current authority.
- No invented N-1 supersession rule.
- No classification, taxonomy, entitlement, subscription, permission,
  authorization, role, activation, regulatory-status, tax-validity,
  AI-execution, or financial authority.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.business_identity import (
    BusinessIdentity,
    BusinessIdentityError,
)


VERSION = (
    "v1.0.0-WILSY-BUSINESS-IDENTITY-REGISTRY"
)

COLLECTION_NAME = "business_identities"


class BusinessIdentityRegistryError(
    RuntimeError
):
    """Raised when Business Identity persistence fails closed."""


class BusinessIdentityRegistry:
    """Insert-only immutable Business Identity revision registry."""

    def __init__(
        self,
        collection: Any,
        *,
        tenant_registry: Any,
    ) -> None:
        """Bind persistence and read-only canonical tenant authority."""
        self._collection = collection
        self._tenant_registry = tenant_registry

    @staticmethod
    def ensure_indexes(
        collection: Any,
    ) -> None:
        """Create the exact frozen durable index model."""
        collection.create_index(
            [
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
                "business_identity_"
                "subject_revision_unique"
            ),
        )

        collection.create_index(
            [
                (
                    "identity_fingerprint",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=(
                "business_identity_"
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
            name=(
                "business_identity_"
                "tenant_subject_revision"
            ),
        )

        collection.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "effective_from",
                    ASCENDING,
                ),
            ],
            name=(
                "business_identity_"
                "tenant_effective_from"
            ),
        )

        collection.create_index(
            [
                (
                    "business_identity_id",
                    ASCENDING,
                ),
                (
                    "supersedes_revision",
                    ASCENDING,
                ),
            ],
            name=(
                "business_identity_"
                "subject_supersedes_revision"
            ),
        )

    @staticmethod
    def _require_active_transaction(
        session: Any,
    ) -> None:
        """Reject before tenant dependency reads or durable writes."""
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
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "ACTIVE_TRANSACTION_REQUIRED"
            )

    @staticmethod
    def _strict_candidate(
        value: object,
    ) -> BusinessIdentity:
        """Strictly rehydrate candidate domain truth."""
        if not isinstance(
            value,
            BusinessIdentity,
        ):
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_VALUE_INVALID"
            )

        try:
            restored = BusinessIdentity.from_dict(
                value.to_dict()
            )
        except (
            BusinessIdentityError,
            TypeError,
            ValueError,
        ) as error:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_VALUE_INVALID"
            ) from error

        if restored != value:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "VALUE_REHYDRATION_MISMATCH"
            )

        return restored

    @staticmethod
    def _document(
        row: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Strip Mongo persistence metadata from one durable row."""
        value = deepcopy(
            dict(
                row
            )
        )

        value.pop(
            "_id",
            None,
        )

        return value

    @classmethod
    def _hydrate(
        cls,
        row: Mapping[str, Any],
    ) -> BusinessIdentity:
        """Strictly hydrate one persisted Business Identity revision."""
        try:
            return BusinessIdentity.from_dict(
                cls._document(
                    row
                )
            )
        except (
            BusinessIdentityError,
            TypeError,
            ValueError,
        ) as error:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "PERSISTED_RECORD_INVALID"
            ) from error

    def _validate_tenant(
        self,
        tenant_id: str,
        *,
        session: Any,
    ) -> None:
        """Validate canonical tenant existence without mutating tenant truth."""
        try:
            tenant = (
                self._tenant_registry.resolve_canonical_tenant(
                    tenant_id,
                    session=session,
                    allow_alias=False,
                )
            )
        except Exception as error:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "TENANT_INVALID"
            ) from error

        if (
            tenant is None
            or getattr(
                tenant,
                "tenant_id",
                None,
            )
            != tenant_id
        ):
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "TENANT_INVALID"
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
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_READ_FAILED"
            ) from error

        if row is None:
            return None

        return self._document(
            row
        )

    def _validate_predecessor(
        self,
        value: BusinessIdentity,
        *,
        session: Any,
    ) -> None:
        """Validate only the explicitly declared predecessor revision."""
        if value.revision == 1:
            return

        predecessor_revision = (
            value.supersedes_revision
        )

        if predecessor_revision is None:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "PREDECESSOR_REQUIRED"
            )

        row = self._find_one(
            {
                "business_identity_id":
                    value.business_identity_id,
                "revision":
                    predecessor_revision,
            },
            session=session,
        )

        if row is None:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "PREDECESSOR_MISSING"
            )

        predecessor = self._hydrate(
            row
        )

        if (
            predecessor.business_identity_id
            != value.business_identity_id
        ):
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "PREDECESSOR_SUBJECT_MISMATCH"
            )

        if (
            predecessor.tenant_id
            != value.tenant_id
        ):
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "PREDECESSOR_TENANT_MISMATCH"
            )

    def create(
        self,
        value: BusinessIdentity,
        *,
        session: Any,
    ) -> BusinessIdentity:
        """Insert one immutable revision or return an exact durable replay."""
        self._require_active_transaction(
            session
        )

        candidate = self._strict_candidate(
            value
        )

        self._validate_tenant(
            candidate.tenant_id,
            session=session,
        )

        self._validate_predecessor(
            candidate,
            session=session,
        )

        by_revision = self._find_one(
            {
                "business_identity_id":
                    candidate.business_identity_id,
                "revision":
                    candidate.revision,
            },
            session=session,
        )

        if by_revision is not None:
            durable = self._hydrate(
                by_revision
            )

            if durable == candidate:
                return durable

            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "SUBJECT_REVISION_CONFLICT"
            )

        by_fingerprint = self._find_one(
            {
                "identity_fingerprint":
                    candidate.identity_fingerprint,
            },
            session=session,
        )

        if by_fingerprint is not None:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "FINGERPRINT_CONFLICT"
            )

        try:
            self._collection.insert_one(
                candidate.to_dict(),
                session=session,
            )
        except DuplicateKeyError as error:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "CONCURRENT_INSERT_CONFLICT"
            ) from error
        except PyMongoError as error:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_"
                "INSERT_FAILED"
            ) from error

        return candidate

    def get_revision(
        self,
        business_identity_id: str,
        revision: int,
        *,
        session: Any = None,
    ) -> BusinessIdentity | None:
        """Read one exact Business Identity subject revision."""
        row = self._find_one(
            {
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

    def get_by_fingerprint(
        self,
        identity_fingerprint: str,
        *,
        session: Any = None,
    ) -> BusinessIdentity | None:
        """Read one revision by immutable integrity fingerprint."""
        row = self._find_one(
            {
                "identity_fingerprint":
                    identity_fingerprint,
            },
            session=session,
        )

        if row is None:
            return None

        return self._hydrate(
            row
        )

    def get_history(
        self,
        business_identity_id: str,
        *,
        session: Any = None,
    ) -> tuple[
        BusinessIdentity,
        ...,
    ]:
        """Read one subject's immutable history in revision order."""
        try:
            cursor = self._collection.find(
                {
                    "business_identity_id":
                        business_identity_id,
                },
                session=session,
            ).sort(
                "revision",
                ASCENDING,
            )
        except PyMongoError as error:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_READ_FAILED"
            ) from error

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
        BusinessIdentity,
        ...,
    ]:
        """Read tenant-owned subjects ordered by subject then revision."""
        try:
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
        except PyMongoError as error:
            raise BusinessIdentityRegistryError(
                "BUSINESS_IDENTITY_REGISTRY_READ_FAILED"
            ) from error

        return tuple(
            self._hydrate(
                row
            )
            for row in cursor
        )


__all__ = [
    "VERSION",
    "COLLECTION_NAME",
    "BusinessIdentityRegistryError",
    "BusinessIdentityRegistry",
]


# ARTIFACT: business_identity_registry.py
