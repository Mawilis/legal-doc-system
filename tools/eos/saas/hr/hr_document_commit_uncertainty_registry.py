"""WILSY OS HR Document Commit-Uncertainty Registry.

TITLE: HR Document Commit-Uncertainty Registry
VERSION: v1.0.0-P0-C12F6D-HR-COMMIT-UNCERTAINTY-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Persist immutable HrDocumentCommitUncertainty evidence so provider-complete /
Mongo-unproven HR document state survives process restart and can later be
reconciled by a separately certified service.

EPITOME:
FROZEN F6C UNCERTAINTY
+ CALLER-OWNED ACTIVE MONGO TRANSACTION
-> APPEND-ONCE DURABLE UNCERTAINTY

IDENTITY:
- tenant_id + uncertainty_id is unique;
- tenant_id + ingestion_reference is unique;
- tenant_id + provider_name + storage_reference +
  object_version_reference is unique.

AUTHORITY BOUNDARY:
Immutable uncertainty persistence only. This registry grants no provider I/O,
reconciliation, provider deletion, retention/disposal, IAM, HTTP, payroll,
billing, payment, settlement or financial execution authority.

TRANSACTION BOUNDARY:
Caller owns every transaction. This module never starts, commits, aborts or
retries a transaction. All reads and writes require one already-active
transaction.

IMMUTABILITY:
Append-once exact replay only. No update, delete, purge or TTL authority.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/hr/hr_document_commit_uncertainty_registry.py

CERTIFICATION / UPDATE DATE: 2026-10-05

CHANGELOG:
2026-10-05 v1.0.0-P0-C12F6D-HR-COMMIT-UNCERTAINTY-REGISTRY
establishes durable append-once HR commit-uncertainty persistence.

FAIL-CLOSED DECLARATION:
Missing/inactive transactions, malformed inputs, unknown persisted fields,
fingerprint corruption, divergent immutable replay, ingestion/provider identity
collisions, duplicate-key races and Mongo failures reject.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import (
    DuplicateKeyError,
    PyMongoError,
)
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    HrDocumentCommitUncertainty,
    HrDocumentCommitUncertaintyError,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F6D-"
    "HR-COMMIT-UNCERTAINTY-REGISTRY"
)

COLLECTION: Final[str] = (
    "hr_document_commit_uncertainties"
)

UNCERTAINTY_INDEX_NAME: Final[str] = (
    "hr_document_commit_uncertainty_tenant_identity_unique"
)

INGESTION_INDEX_NAME: Final[str] = (
    "hr_document_commit_uncertainty_tenant_ingestion_unique"
)

PROVIDER_OBJECT_INDEX_NAME: Final[str] = (
    "hr_document_commit_uncertainty_tenant_provider_object_unique"
)

DETECTED_INDEX_NAME: Final[str] = (
    "hr_document_commit_uncertainty_tenant_detected"
)

MAX_TENANT_UNCERTAINTIES: Final[int] = 2000

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(
    w="majority",
    j=True,
)

READ_CONCERN: Final[ReadConcern] = ReadConcern(
    "majority"
)

_UNCERTAINTY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "uncertainty_id",
        "tenant_id",
        "employee_id",
        "document_id",
        "document_version_id",
        "ingestion_reference",
        "media_type",
        "original_filename",
        "admitted_max_content_length",
        "document_class",
        "created_at",
        "created_by_principal_id",
        "retention_until",
        "legal_hold",
        "supersedes_version_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "provider_integrity_reference",
        "write_intent_fingerprint",
        "content_length",
        "content_fingerprint",
        "detected_at",
        "schema",
        "uncertainty_version",
        "fingerprint",
    }
)


class HrDocumentCommitUncertaintyRegistryError(
    RuntimeError
):
    """Base fail-closed F6D registry error."""

    default_code = (
        "P0_C12F6D_REGISTRY_ERROR"
    )

    def __init__(
        self,
        code: str | None = None,
    ) -> None:
        self.code = (
            code
            or self.default_code
        )
        super().__init__(
            self.code
        )


class HrDocumentCommitUncertaintyRegistryInputError(
    HrDocumentCommitUncertaintyRegistryError
):
    default_code = (
        "P0_C12F6D_INPUT_INVALID"
    )


class HrDocumentCommitUncertaintyRegistryTransactionRequiredError(
    HrDocumentCommitUncertaintyRegistryError
):
    default_code = (
        "P0_C12F6D_ACTIVE_TRANSACTION_REQUIRED"
    )


class HrDocumentCommitUncertaintyRegistryNotFoundError(
    HrDocumentCommitUncertaintyRegistryError
):
    default_code = (
        "P0_C12F6D_UNCERTAINTY_NOT_FOUND"
    )


class HrDocumentCommitUncertaintyRegistryConflictError(
    HrDocumentCommitUncertaintyRegistryError
):
    default_code = (
        "P0_C12F6D_UNCERTAINTY_CONFLICT"
    )


class HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError(
    HrDocumentCommitUncertaintyRegistryError
):
    default_code = (
        "P0_C12F6D_PERSISTED_RECORD_INVALID"
    )


class HrDocumentCommitUncertaintyRegistryRetryRequiredError(
    HrDocumentCommitUncertaintyRegistryError
):
    default_code = (
        "P0_C12F6D_WHOLE_TRANSACTION_RETRY_REQUIRED"
    )


class HrDocumentCommitUncertaintyRegistryPersistenceUnavailableError(
    HrDocumentCommitUncertaintyRegistryError
):
    default_code = (
        "P0_C12F6D_PERSISTENCE_UNAVAILABLE"
    )


def _raise(
    error_type: type[
        HrDocumentCommitUncertaintyRegistryError
    ],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _raise_mongo(
    error: PyMongoError,
) -> NoReturn:
    if error.has_error_label(
        "TransientTransactionError"
    ):
        _raise(
            HrDocumentCommitUncertaintyRegistryRetryRequiredError,
            cause=error,
        )

    _raise(
        HrDocumentCommitUncertaintyRegistryPersistenceUnavailableError,
        cause=error,
    )


def _target(
    collection: Any,
) -> Any:
    if collection is None:
        _raise(
            HrDocumentCommitUncertaintyRegistryInputError,
            "P0_C12F6D_COLLECTION_REQUIRED",
        )

    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(
                tz_aware=True,
            ),
        )
    except AttributeError:
        return collection


def _active_transaction(
    session: Any,
) -> Any:
    if session is None:
        _raise(
            HrDocumentCommitUncertaintyRegistryTransactionRequiredError
        )

    marker = getattr(
        session,
        "in_transaction",
        None,
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except (
        AttributeError,
        TypeError,
    ):
        active = False

    if active is not True:
        _raise(
            HrDocumentCommitUncertaintyRegistryTransactionRequiredError
        )

    return session


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(
            value
        ) > 2048
    ):
        _raise(
            HrDocumentCommitUncertaintyRegistryInputError,
            f"P0_C12F6D_{name.upper()}_INVALID",
        )

    return cast(
        str,
        value,
    )


def _serialize(
    value: HrDocumentCommitUncertainty,
) -> dict[str, object]:
    """Serialize frozen F6C evidence exactly for durable storage."""

    if (
        type(
            value
        )
        is not HrDocumentCommitUncertainty
    ):
        _raise(
            HrDocumentCommitUncertaintyRegistryInputError,
            "P0_C12F6D_UNCERTAINTY_REQUIRED",
        )

    document = value.to_dict()

    if (
        set(
            document
        )
        != _UNCERTAINTY_FIELDS
    ):
        _raise(
            HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError,
            "P0_C12F6D_RECORD_SCHEMA_INVALID",
        )

    if any(
        isinstance(
            item,
            (
                bytes,
                bytearray,
                memoryview,
            ),
        )
        for item in document.values()
    ):
        _raise(
            HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError,
            "P0_C12F6D_RAW_BYTES_FORBIDDEN",
        )

    # F6C serializes all UTC datetimes to exact ISO text, preserving
    # microseconds and avoiding Mongo datetime precision loss.
    return dict(
        document
    )


def _hydrate(
    row: Mapping[
        str,
        Any,
    ],
) -> HrDocumentCommitUncertainty:
    """Strictly hydrate one exact persisted F6C uncertainty row."""

    try:
        if not isinstance(
            row,
            Mapping,
        ):
            _raise(
                HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError
            )

        persisted = dict(
            row
        )

        persisted.pop(
            "_id",
            None,
        )

        if (
            set(
                persisted
            )
            != _UNCERTAINTY_FIELDS
        ):
            _raise(
                HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError,
                "P0_C12F6D_RECORD_SCHEMA_INVALID",
            )

        if any(
            isinstance(
                item,
                (
                    bytes,
                    bytearray,
                    memoryview,
                ),
            )
            for item in persisted.values()
        ):
            _raise(
                HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError,
                "P0_C12F6D_RAW_BYTES_FORBIDDEN",
            )

        value = (
            HrDocumentCommitUncertainty.from_dict(
                cast(
                    Mapping[
                        str,
                        object,
                    ],
                    persisted,
                )
            )
        )

        if (
            _serialize(
                value
            )
            != persisted
        ):
            _raise(
                HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError,
                "P0_C12F6D_RECORD_CORRELATION_INVALID",
            )

        return value

    except HrDocumentCommitUncertaintyRegistryError:
        raise

    except (
        KeyError,
        TypeError,
        ValueError,
        HrDocumentCommitUncertaintyError,
    ) as error:
        _raise(
            HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError,
            cause=error,
        )


def ensure_indexes(
    collection: Any,
) -> None:
    """Create the closed append-only F6D index surface."""

    target = _target(
        collection
    )

    try:
        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "uncertainty_id",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=UNCERTAINTY_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "ingestion_reference",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=INGESTION_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "provider_name",
                    ASCENDING,
                ),
                (
                    "storage_reference",
                    ASCENDING,
                ),
                (
                    "object_version_reference",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=PROVIDER_OBJECT_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "detected_at",
                    DESCENDING,
                ),
                (
                    "uncertainty_id",
                    ASCENDING,
                ),
            ],
            unique=False,
            name=DETECTED_INDEX_NAME,
        )

    except PyMongoError as error:
        _raise_mongo(
            error
        )

    except AttributeError as error:
        _raise(
            HrDocumentCommitUncertaintyRegistryInputError,
            "P0_C12F6D_COLLECTION_INTERFACE_INVALID",
            error,
        )


class HrDocumentCommitUncertaintyRegistry:
    """Append-once durable F6C uncertainty persistence."""

    __slots__ = (
        "_collection",
    )

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = _target(
            collection
        )

    def ensure_indexes(
        self,
    ) -> None:
        """Create exact indexes; never create TTL indexes."""

        ensure_indexes(
            self._collection
        )

    def create_or_replay(
        self,
        value: HrDocumentCommitUncertainty,
        *,
        session: Any,
    ) -> HrDocumentCommitUncertainty:
        """Persist once or return one exact immutable replay."""

        tx = _active_transaction(
            session
        )

        if (
            type(
                value
            )
            is not HrDocumentCommitUncertainty
        ):
            _raise(
                HrDocumentCommitUncertaintyRegistryInputError,
                "P0_C12F6D_UNCERTAINTY_REQUIRED",
            )

        # Exact uncertainty identity.
        try:
            existing = (
                self._collection.find_one(
                    {
                        "tenant_id":
                            value.tenant_id,
                        "uncertainty_id":
                            value.uncertainty_id,
                    },
                    session=tx,
                )
            )
        except PyMongoError as error:
            _raise_mongo(
                error
            )
        except AttributeError as error:
            _raise(
                HrDocumentCommitUncertaintyRegistryInputError,
                "P0_C12F6D_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if existing is not None:
            persisted = _hydrate(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    existing,
                )
            )

            if persisted != value:
                _raise(
                    HrDocumentCommitUncertaintyRegistryConflictError,
                    "P0_C12F6D_DIVERGENT_UNCERTAINTY_IDENTITY",
                )

            return persisted

        # One tenant ingestion reference can bind only one uncertainty.
        try:
            ingestion = (
                self._collection.find_one(
                    {
                        "tenant_id":
                            value.tenant_id,
                        "ingestion_reference":
                            value.ingestion_reference,
                    },
                    session=tx,
                )
            )
        except PyMongoError as error:
            _raise_mongo(
                error
            )
        except AttributeError as error:
            _raise(
                HrDocumentCommitUncertaintyRegistryInputError,
                "P0_C12F6D_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if ingestion is not None:
            persisted = _hydrate(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    ingestion,
                )
            )

            if persisted != value:
                _raise(
                    HrDocumentCommitUncertaintyRegistryConflictError,
                    "P0_C12F6D_DIVERGENT_INGESTION_IDENTITY",
                )

            return persisted

        # One exact provider object version can bind only one uncertainty
        # inside a tenant boundary.
        try:
            provider_object = (
                self._collection.find_one(
                    {
                        "tenant_id":
                            value.tenant_id,
                        "provider_name":
                            value.provider_name,
                        "storage_reference":
                            value.storage_reference,
                        "object_version_reference":
                            value.object_version_reference,
                    },
                    session=tx,
                )
            )
        except PyMongoError as error:
            _raise_mongo(
                error
            )
        except AttributeError as error:
            _raise(
                HrDocumentCommitUncertaintyRegistryInputError,
                "P0_C12F6D_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if provider_object is not None:
            persisted = _hydrate(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    provider_object,
                )
            )

            if persisted != value:
                _raise(
                    HrDocumentCommitUncertaintyRegistryConflictError,
                    "P0_C12F6D_DIVERGENT_PROVIDER_OBJECT_IDENTITY",
                )

            return persisted

        document = _serialize(
            value
        )

        try:
            # PyMongo may mutate its input by injecting _id;
            # preserve canonical candidate bytes by passing a copy.
            self._collection.insert_one(
                dict(
                    document
                ),
                session=tx,
            )

        except DuplicateKeyError as error:
            _raise(
                HrDocumentCommitUncertaintyRegistryRetryRequiredError,
                cause=error,
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )

        except AttributeError as error:
            _raise(
                HrDocumentCommitUncertaintyRegistryInputError,
                "P0_C12F6D_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return value

    def get(
        self,
        *,
        tenant_id: str,
        uncertainty_id: str,
        session: Any,
    ) -> HrDocumentCommitUncertainty:
        """Read one exact tenant-scoped uncertainty."""

        tx = _active_transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        uncertainty = _text(
            "uncertainty_id",
            uncertainty_id,
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "uncertainty_id":
                        uncertainty,
                },
                session=tx,
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )

        except AttributeError as error:
            _raise(
                HrDocumentCommitUncertaintyRegistryInputError,
                "P0_C12F6D_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                HrDocumentCommitUncertaintyRegistryNotFoundError
            )

        value = _hydrate(
            cast(
                Mapping[
                    str,
                    Any,
                ],
                row,
            )
        )

        if (
            value.tenant_id
            != tenant
            or value.uncertainty_id
            != uncertainty
        ):
            _raise(
                HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError,
                "P0_C12F6D_SCOPE_CORRELATION_INVALID",
            )

        return value

    def list_tenant_uncertainties(
        self,
        *,
        tenant_id: str,
        session: Any,
    ) -> tuple[
        HrDocumentCommitUncertainty,
        ...,
    ]:
        """Return bounded deterministic tenant-scoped uncertainty evidence."""

        tx = _active_transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        try:
            cursor = self._collection.find(
                {
                    "tenant_id":
                        tenant,
                },
                session=tx,
            )

            if hasattr(
                cursor,
                "limit",
            ):
                cursor = cursor.limit(
                    MAX_TENANT_UNCERTAINTIES
                    + 1
                )

            rows = tuple(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    row,
                )
                for row in cursor
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )

        except AttributeError as error:
            _raise(
                HrDocumentCommitUncertaintyRegistryInputError,
                "P0_C12F6D_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if (
            len(
                rows
            )
            > MAX_TENANT_UNCERTAINTIES
        ):
            _raise(
                HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError,
                "P0_C12F6D_TENANT_UNCERTAINTY_LIMIT_EXCEEDED",
            )

        values = tuple(
            _hydrate(
                row
            )
            for row in rows
        )

        if any(
            value.tenant_id
            != tenant
            for value in values
        ):
            _raise(
                HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError,
                "P0_C12F6D_SCOPE_CORRELATION_INVALID",
            )

        return tuple(
            sorted(
                values,
                key=lambda item: (
                    item.detected_at,
                    item.uncertainty_id,
                ),
                reverse=True,
            )
        )


__all__ = [
    "VERSION",
    "COLLECTION",
    "UNCERTAINTY_INDEX_NAME",
    "INGESTION_INDEX_NAME",
    "PROVIDER_OBJECT_INDEX_NAME",
    "DETECTED_INDEX_NAME",
    "MAX_TENANT_UNCERTAINTIES",
    "WRITE_CONCERN",
    "READ_CONCERN",
    "HrDocumentCommitUncertaintyRegistry",
    "HrDocumentCommitUncertaintyRegistryError",
    "HrDocumentCommitUncertaintyRegistryInputError",
    "HrDocumentCommitUncertaintyRegistryTransactionRequiredError",
    "HrDocumentCommitUncertaintyRegistryNotFoundError",
    "HrDocumentCommitUncertaintyRegistryConflictError",
    "HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError",
    "HrDocumentCommitUncertaintyRegistryRetryRequiredError",
    "HrDocumentCommitUncertaintyRegistryPersistenceUnavailableError",
    "ensure_indexes",
]


# ARTIFACT: tools/eos/saas/hr/hr_document_commit_uncertainty_registry.py
# VERSION: v1.0.0-P0-C12F6D-HR-COMMIT-UNCERTAINTY-REGISTRY
# AUTHORITY: immutable HR commit-uncertainty persistence only
# TRANSACTION: caller-owned active transaction required
# REPLAY: append-once exact replay only
# TTL AUTHORITY: none
# UPDATE AUTHORITY: none
# DELETE AUTHORITY: none
# PROVIDER IO AUTHORITY: none
# RECONCILIATION AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
