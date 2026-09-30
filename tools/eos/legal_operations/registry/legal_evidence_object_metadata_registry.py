"""WILSY OS metadata-only Legal Evidence object registry.

TITLE: Legal Evidence Object Metadata Registry
VERSION: v1.1.0-L10A2R-C2R1-PROVIDER-OBJECT-LOOKUP
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Persist immutable L10A2R-C1 LegalEvidenceObjectMetadata values in the Mongo
    control plane without persisting or returning raw binary bodies.

EPITOME:
    OBJECT-BACKED CANONICAL METADATA
    -> METADATA-ONLY MONGO DURABILITY
    != RAW-BYTE STORAGE
    != PROVIDER EXECUTION
    != RESERVATION CONSUMPTION
    != USAGE COMMIT
    != AUTHORIZED AVAILABILITY

COLLABORATION / OWNERSHIP:
    L10A2R-C1 owns immutable canonical metadata/object-evidence binding.
    This C2 registry owns only metadata durability, exact replay, strict
    corruption detection and tenant/document-scoped reads.
    Provider execution remains owned by the certified binary-storage adapter.
    Reservation/usage lifecycle remains owned by L10A2Q-P5/P3.
    Production two-plane orchestration remains a later gate.

TRANSACTION POSTURE:
    Every operational read/write requires one already-active caller-owned Mongo
    transaction. This registry never starts, commits, aborts or retries it.

TENANT BOUNDARY:
    Every operational read/write begins with exact tenant scope. Cross-tenant
    absence is indistinguishable from not-found.

CONTROL-PLANE POSTURE:
    Persisted rows are exactly the C1 metadata-only serialization. There is no
    content_bytes field and no byte-returning API.

FAIL-CLOSED DECLARATION:
    Missing transactions, malformed scope, unknown/missing persisted fields,
    metadata fingerprint corruption, divergent immutable replay, duplicate-key
    races and Mongo failures reject without healing or inferred truth.

FINANCIAL AUTHORITY BOUNDARY:
    No billing, invoice, payment, financial execution or settlement authority.
    Kennel EOS remains exclusive financial execution authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_object_metadata import (
    LegalEvidenceObjectMetadata,
    LegalEvidenceObjectMetadataError,
)


VERSION: Final[str] = (
    "v1.1.0-L10A2R-C2R1-PROVIDER-OBJECT-LOOKUP"
)

COLLECTION: Final[str] = "legal_evidence_object_metadata"

REFERENCE_INDEX_NAME: Final[str] = (
    "legal_evidence_object_metadata_tenant_reference_unique"
)
DOCUMENT_INDEX_NAME: Final[str] = (
    "legal_evidence_object_metadata_tenant_matter_document_registered"
)
CONTENT_FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_evidence_object_metadata_tenant_content_fingerprint"
)
PROVIDER_OBJECT_INDEX_NAME: Final[str] = (
    "legal_evidence_object_metadata_tenant_provider_object"
)

MAX_DOCUMENT_METADATA: Final[int] = 500

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(
    w="majority",
    j=True,
)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")

_METADATA_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "tenant_id",
        "case_matter_id",
        "document_id",
        "content_reference",
        "media_type",
        "original_filename",
        "content_length",
        "content_fingerprint",
        "content_metadata_fingerprint",
        "registered_at",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "provider_integrity_reference",
        "write_intent_fingerprint",
        "schema",
        "object_metadata_version",
        "fingerprint",
    }
)


class LegalEvidenceObjectMetadataRegistryError(RuntimeError):
    """Base fail-closed C2 metadata persistence/read error."""

    default_code = "L10A2R_C2_REGISTRY_ERROR"

    def __init__(
        self,
        code: str | None = None,
    ) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalEvidenceObjectMetadataRegistryInputError(
    LegalEvidenceObjectMetadataRegistryError
):
    """Malformed caller input or unsupported collection surface."""

    default_code = "L10A2R_C2_INPUT_INVALID"


class LegalEvidenceObjectMetadataRegistryTransactionRequiredError(
    LegalEvidenceObjectMetadataRegistryError
):
    """Caller did not provide one active transaction."""

    default_code = "L10A2R_C2_TRANSACTION_REQUIRED"


class LegalEvidenceObjectMetadataRegistryNotFoundError(
    LegalEvidenceObjectMetadataRegistryError
):
    """No exact tenant-scoped object metadata exists."""

    default_code = "L10A2R_C2_METADATA_NOT_FOUND"


class LegalEvidenceObjectMetadataRegistryConflictError(
    LegalEvidenceObjectMetadataRegistryError
):
    """Immutable metadata identity is already bound divergently."""

    default_code = "L10A2R_C2_METADATA_CONFLICT"


class LegalEvidenceObjectMetadataRegistryRetryRequiredError(
    LegalEvidenceObjectMetadataRegistryError
):
    """Caller must abort and retry the complete transaction."""

    default_code = "L10A2R_C2_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalEvidenceObjectMetadataRegistryPersistenceUnavailableError(
    LegalEvidenceObjectMetadataRegistryError
):
    """Mongo persistence failed safely."""

    default_code = "L10A2R_C2_PERSISTENCE_UNAVAILABLE"


def _raise(
    error_type: type[LegalEvidenceObjectMetadataRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
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
            LegalEvidenceObjectMetadataRegistryRetryRequiredError,
            cause=error,
        )

    _raise(
        LegalEvidenceObjectMetadataRegistryPersistenceUnavailableError,
        cause=error,
    )


def _target(
    collection: Any,
) -> Any:
    if collection is None:
        _raise(
            LegalEvidenceObjectMetadataRegistryInputError,
            "L10A2R_C2_COLLECTION_REQUIRED",
        )

    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(
                tz_aware=True,
                tzinfo=timezone.utc,
            ),
        )
    except AttributeError:
        return collection


def _active_transaction(
    session: Any,
) -> Any:
    if session is None:
        _raise(
            LegalEvidenceObjectMetadataRegistryTransactionRequiredError,
            "L10A2R_C2_TRANSACTION_REQUIRED",
        )

    marker = getattr(
        session,
        "in_transaction",
        None,
    )

    try:
        active = marker() if callable(marker) else marker
    except (
        AttributeError,
        TypeError,
    ):
        active = False

    if active is not True:
        _raise(
            LegalEvidenceObjectMetadataRegistryTransactionRequiredError,
            "L10A2R_C2_TRANSACTION_REQUIRED",
        )

    return session


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 2048
    ):
        _raise(
            LegalEvidenceObjectMetadataRegistryInputError,
            f"L10A2R_C2_{name.upper()}_INVALID",
        )

    return value


def _serialize(
    value: LegalEvidenceObjectMetadata,
) -> dict[str, object]:
    """Encode one C1 value without BSON datetime precision loss.

    Mongo/BSON datetimes are millisecond precision. C1 preserves canonical
    microseconds in its fingerprint, so C2 stores ``registered_at`` as one
    exact UTC ISO-8601 string rather than allowing BSON to truncate it.
    """
    if type(value) is not LegalEvidenceObjectMetadata:
        _raise(
            LegalEvidenceObjectMetadataRegistryInputError,
            "L10A2R_C2_METADATA_REQUIRED",
        )

    document = value.to_dict()
    document["registered_at"] = value.registered_at.isoformat()

    if set(document) != _METADATA_FIELDS:
        _raise(
            LegalEvidenceObjectMetadataRegistryError,
            "L10A2R_C2_CORRUPT_METADATA",
        )

    return document


def _hydrate(
    row: Mapping[str, Any],
) -> LegalEvidenceObjectMetadata:
    """Strictly hydrate exactly one C1 metadata-only persisted row."""
    try:
        if not isinstance(
            row,
            Mapping,
        ):
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_CORRUPT_METADATA",
            )

        persisted = dict(row)
        persisted.pop(
            "_id",
            None,
        )

        if set(persisted) != _METADATA_FIELDS:
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_CORRUPT_METADATA",
            )

        registered_at = persisted.get(
            "registered_at"
        )
        if not isinstance(
            registered_at,
            str,
        ):
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_CORRUPT_METADATA",
            )

        try:
            parsed_registered_at = datetime.fromisoformat(
                registered_at
            )
        except ValueError as error:
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_CORRUPT_METADATA",
                error,
            )

        if (
            parsed_registered_at.tzinfo is None
            or parsed_registered_at.utcoffset() is None
            or parsed_registered_at.astimezone(
                timezone.utc
            ).isoformat()
            != registered_at
        ):
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_CORRUPT_METADATA",
            )

        domain_payload = dict(
            persisted
        )
        domain_payload["registered_at"] = (
            parsed_registered_at
        )

        value = LegalEvidenceObjectMetadata.from_dict(
            cast(
                Mapping[str, object],
                domain_payload,
            )
        )

        if _serialize(value) != persisted:
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_CORRUPT_METADATA",
            )

        return value

    except LegalEvidenceObjectMetadataRegistryError:
        raise
    except (
        KeyError,
        TypeError,
        ValueError,
        LegalEvidenceObjectMetadataError,
    ) as error:
        _raise(
            LegalEvidenceObjectMetadataRegistryError,
            "L10A2R_C2_CORRUPT_METADATA",
            error,
        )


def ensure_indexes(
    collection: Any,
) -> None:
    """Create the exact metadata-only immutable identity/read indexes."""
    target = _target(collection)

    try:
        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "content_reference",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=REFERENCE_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "case_matter_id",
                    ASCENDING,
                ),
                (
                    "document_id",
                    ASCENDING,
                ),
                (
                    "registered_at",
                    DESCENDING,
                ),
            ],
            unique=False,
            name=DOCUMENT_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "content_fingerprint",
                    ASCENDING,
                ),
            ],
            unique=False,
            name=CONTENT_FINGERPRINT_INDEX_NAME,
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
            unique=False,
            name=PROVIDER_OBJECT_INDEX_NAME,
        )

    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalEvidenceObjectMetadataRegistryInputError,
            "L10A2R_C2_COLLECTION_INTERFACE_INVALID",
            error,
        )


class LegalEvidenceObjectMetadataRegistry:
    """Immutable metadata-only Mongo control-plane registry."""

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
        """Create exact C2 indexes without TTL."""
        ensure_indexes(
            self._collection
        )

    def create_or_replay(
        self,
        value: LegalEvidenceObjectMetadata,
        *,
        session: Any,
    ) -> LegalEvidenceObjectMetadata:
        """Persist once or return one exact immutable replay."""
        tx = _active_transaction(
            session
        )

        if type(value) is not LegalEvidenceObjectMetadata:
            _raise(
                LegalEvidenceObjectMetadataRegistryInputError,
                "L10A2R_C2_METADATA_REQUIRED",
            )

        try:
            existing = self._collection.find_one(
                {
                    "tenant_id": value.tenant_id,
                    "content_reference": value.content_reference,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)
        except AttributeError as error:
            _raise(
                LegalEvidenceObjectMetadataRegistryInputError,
                "L10A2R_C2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if existing is not None:
            persisted = _hydrate(
                cast(
                    Mapping[str, Any],
                    existing,
                )
            )

            if persisted != value:
                _raise(
                    LegalEvidenceObjectMetadataRegistryConflictError,
                    "L10A2R_C2_DIVERGENT_CONTENT_REFERENCE",
                )

            return persisted

        document = _serialize(
            value
        )

        if any(
            isinstance(
                item,
                (
                    bytes,
                    bytearray,
                ),
            )
            for item in document.values()
        ):
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_RAW_BYTES_FORBIDDEN",
            )

        try:
            self._collection.insert_one(
                document,
                session=tx,
            )
        except DuplicateKeyError as error:
            _raise(
                LegalEvidenceObjectMetadataRegistryRetryRequiredError,
                cause=error,
            )
        except PyMongoError as error:
            _raise_mongo(error)
        except AttributeError as error:
            _raise(
                LegalEvidenceObjectMetadataRegistryInputError,
                "L10A2R_C2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return value

    def get(
        self,
        *,
        tenant_id: str,
        content_reference: str,
        session: Any,
    ) -> LegalEvidenceObjectMetadata:
        """Return one exact tenant-scoped strictly hydrated metadata row."""
        tx = _active_transaction(
            session
        )
        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        reference = _text(
            "content_reference",
            content_reference,
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "content_reference": reference,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)
        except AttributeError as error:
            _raise(
                LegalEvidenceObjectMetadataRegistryInputError,
                "L10A2R_C2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                LegalEvidenceObjectMetadataRegistryNotFoundError,
                "L10A2R_C2_METADATA_NOT_FOUND",
            )

        value = _hydrate(
            cast(
                Mapping[str, Any],
                row,
            )
        )

        if (
            value.tenant_id != tenant
            or value.content_reference != reference
        ):
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_CORRUPT_METADATA",
            )

        return value

    def get_provider_object(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        storage_reference: str,
        object_version_reference: str,
        session: Any,
    ) -> LegalEvidenceObjectMetadata:
        """Return one exact tenant/provider-object canonical metadata row."""
        tx = _active_transaction(
            session
        )
        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        provider = _text(
            "provider_name",
            provider_name,
        )
        storage = _text(
            "storage_reference",
            storage_reference,
        )
        version = _text(
            "object_version_reference",
            object_version_reference,
        )

        try:
            cursor = self._collection.find(
                {
                    "tenant_id": tenant,
                    "provider_name": provider,
                    "storage_reference": storage,
                    "object_version_reference": version,
                },
                session=tx,
            )

            if hasattr(
                cursor,
                "limit",
            ):
                cursor = cursor.limit(
                    2
                )

            rows = tuple(
                cast(
                    Mapping[str, Any],
                    row,
                )
                for row in cursor
            )

        except PyMongoError as error:
            _raise_mongo(error)
        except AttributeError as error:
            _raise(
                LegalEvidenceObjectMetadataRegistryInputError,
                "L10A2R_C2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if not rows:
            _raise(
                LegalEvidenceObjectMetadataRegistryNotFoundError,
                "L10A2R_C2_PROVIDER_OBJECT_NOT_FOUND",
            )

        if len(rows) != 1:
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_PROVIDER_OBJECT_AMBIGUOUS",
            )

        value = _hydrate(
            rows[0]
        )

        if (
            value.tenant_id != tenant
            or value.provider_name != provider
            or value.storage_reference != storage
            or value.object_version_reference != version
        ):
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_CORRUPT_METADATA",
            )

        return value

    def list_document_metadata(
        self,
        *,
        tenant_id: str,
        case_matter_id: str,
        document_id: str,
        session: Any,
    ) -> tuple[LegalEvidenceObjectMetadata, ...]:
        """Return bounded immutable metadata for one tenant matter/document."""
        tx = _active_transaction(
            session
        )
        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        matter = _text(
            "case_matter_id",
            case_matter_id,
        )
        document = _text(
            "document_id",
            document_id,
        )

        try:
            cursor = self._collection.find(
                {
                    "tenant_id": tenant,
                    "case_matter_id": matter,
                    "document_id": document,
                },
                session=tx,
            )

            if hasattr(
                cursor,
                "limit",
            ):
                cursor = cursor.limit(
                    MAX_DOCUMENT_METADATA + 1
                )

            rows = tuple(
                cast(
                    Mapping[str, Any],
                    row,
                )
                for row in cursor
            )

        except PyMongoError as error:
            _raise_mongo(error)
        except AttributeError as error:
            _raise(
                LegalEvidenceObjectMetadataRegistryInputError,
                "L10A2R_C2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if len(rows) > MAX_DOCUMENT_METADATA:
            _raise(
                LegalEvidenceObjectMetadataRegistryError,
                "L10A2R_C2_DOCUMENT_METADATA_LIMIT_EXCEEDED",
            )

        hydrated = tuple(
            _hydrate(
                row
            )
            for row in rows
        )

        for value in hydrated:
            if (
                value.tenant_id != tenant
                or value.case_matter_id != matter
                or value.document_id != document
            ):
                _raise(
                    LegalEvidenceObjectMetadataRegistryError,
                    "L10A2R_C2_CORRUPT_METADATA",
                )

        return tuple(
            sorted(
                hydrated,
                key=lambda item: (
                    item.registered_at,
                    item.content_reference,
                ),
                reverse=True,
            )
        )


__all__ = [
    "COLLECTION",
    "CONTENT_FINGERPRINT_INDEX_NAME",
    "DOCUMENT_INDEX_NAME",
    "MAX_DOCUMENT_METADATA",
    "PROVIDER_OBJECT_INDEX_NAME",
    "READ_CONCERN",
    "REFERENCE_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "LegalEvidenceObjectMetadataRegistry",
    "LegalEvidenceObjectMetadataRegistryConflictError",
    "LegalEvidenceObjectMetadataRegistryError",
    "LegalEvidenceObjectMetadataRegistryInputError",
    "LegalEvidenceObjectMetadataRegistryNotFoundError",
    "LegalEvidenceObjectMetadataRegistryPersistenceUnavailableError",
    "LegalEvidenceObjectMetadataRegistryRetryRequiredError",
    "LegalEvidenceObjectMetadataRegistryTransactionRequiredError",
    "ensure_indexes",
]


# ARTIFACT: legal_evidence_object_metadata_registry.py
# VERSION: v1.1.0-L10A2R-C2R1-PROVIDER-OBJECT-LOOKUP
# AUTHORITY BOUNDARY: immutable metadata-only Mongo durability
# CONTROL-PLANE POSTURE: no raw binary body persisted or returned
# OBJECT-PLANE POSTURE: no provider execution exists in registry
# TENANT POSTURE: exact tenant-scoped reads and immutable replay identity
# PROVIDER LOOKUP POSTURE: exact read-only provider-object lookup; ambiguity fails closed
# TRANSACTION POSTURE: caller owns one active transaction
# TTL POSTURE: no TTL index
# AVAILABILITY POSTURE: persistence does not authorize availability
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
