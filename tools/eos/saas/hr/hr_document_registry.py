"""TITLE: WILSY OS HR Document Registry.
VERSION: v1.0.0-P0-C12F4B-HR-DOCUMENT-REGISTRY
AUTHORITY: Durable immutable HR document-version metadata persistence.
EPITOME: Persists exact HrDocument domain snapshots under caller-owned
active Mongo transactions with tenant, employee, document and version
scoping, exact replay and strict corruption rejection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/hr/hr_document_registry.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F4B-HR-DOCUMENT-REGISTRY
establishes append-only HR document metadata/version persistence.
AUTHORITY BOUNDARY: Persistence only. No binary storage execution,
IAM, HTTP, retention enforcement, deletion execution, payroll, billing,
payment execution or settlement authority.
TRANSACTION BOUNDARY: Caller owns every transaction; this module never
starts, commits, aborts or retries one.
IMMUTABILITY: Append-only exact replay. No update, delete or TTL authority.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.hr_document import (
    HR_DOCUMENT_SCHEMA,
    HrDocument,
    HrDocumentClass,
    HrDocumentDomainError,
    HrDocumentSensitivity,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F4B-HR-DOCUMENT-REGISTRY"
)

COLLECTION: Final[str] = "hr_documents"

DOCUMENT_VERSION_INDEX_NAME: Final[str] = (
    "hr_document_tenant_version_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "hr_document_tenant_fingerprint_unique"
)

EMPLOYEE_CREATED_INDEX_NAME: Final[str] = (
    "hr_document_tenant_employee_created"
)

DOCUMENT_HISTORY_INDEX_NAME: Final[str] = (
    "hr_document_tenant_employee_document_created"
)

EMPLOYEE_CLASS_INDEX_NAME: Final[str] = (
    "hr_document_tenant_employee_class_created"
)

EMPLOYEE_SENSITIVITY_INDEX_NAME: Final[str] = (
    "hr_document_tenant_employee_sensitivity_created"
)

MAX_HR_DOCUMENT_ROWS: Final[int] = 2000

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(
    w="majority",
    j=True,
)

READ_CONCERN: Final[ReadConcern] = ReadConcern(
    "majority"
)

HR_DOCUMENT_RECORD_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "employee_id",
    "document_id",
    "document_version_id",
    "document_class",
    "sensitivity",
    "original_filename",
    "media_type",
    "byte_length",
    "content_digest_sha3_512",
    "storage_provider_id",
    "storage_object_reference",
    "object_version_reference",
    "provider_integrity_reference",
    "created_at",
    "created_by_principal_id",
    "retention_until",
    "legal_hold",
    "supersedes_version_id",
    "schema",
    "fingerprint",
)


class HrDocumentRegistryError(RuntimeError):
    default_code = "P0_C12F4B_REGISTRY_ERROR"

    def __init__(
        self,
        code: str | None = None,
    ) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class HrDocumentRegistryInputError(
    HrDocumentRegistryError
):
    default_code = "P0_C12F4B_INPUT_INVALID"


class HrDocumentRegistryTransactionRequiredError(
    HrDocumentRegistryError
):
    default_code = (
        "P0_C12F4B_ACTIVE_TRANSACTION_REQUIRED"
    )


class HrDocumentRegistryNotFoundError(
    HrDocumentRegistryError
):
    default_code = "P0_C12F4B_DOCUMENT_NOT_FOUND"


class HrDocumentRegistryConflictError(
    HrDocumentRegistryError
):
    default_code = "P0_C12F4B_DOCUMENT_CONFLICT"


class HrDocumentRegistryPersistedRecordInvalidError(
    HrDocumentRegistryError
):
    default_code = (
        "P0_C12F4B_PERSISTED_RECORD_INVALID"
    )


class HrDocumentRegistryRetryRequiredError(
    HrDocumentRegistryError
):
    default_code = (
        "P0_C12F4B_WHOLE_TRANSACTION_RETRY_REQUIRED"
    )


class HrDocumentRegistryPersistenceUnavailableError(
    HrDocumentRegistryError
):
    default_code = (
        "P0_C12F4B_PERSISTENCE_UNAVAILABLE"
    )


def _raise(
    error_type: type[HrDocumentRegistryError],
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
            HrDocumentRegistryRetryRequiredError,
            cause=error,
        )

    _raise(
        HrDocumentRegistryPersistenceUnavailableError,
        cause=error,
    )


def _target(
    collection: Any,
) -> Any:
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


def _collection(
    value: Any,
) -> Any:
    if value is None:
        _raise(
            HrDocumentRegistryInputError,
            "P0_C12F4B_COLLECTION_REQUIRED",
        )

    return _target(value)


def _active_transaction(
    session: Any,
) -> Any:
    if session is None:
        _raise(
            HrDocumentRegistryTransactionRequiredError
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
            HrDocumentRegistryTransactionRequiredError
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
    ):
        _raise(
            HrDocumentRegistryInputError,
            f"P0_C12F4B_{name.upper()}_INVALID",
        )

    return value


def _fingerprint(
    value: object,
) -> str:
    text = _text(
        "fingerprint",
        value,
    )

    if (
        len(text) != 128
        or any(
            character not in "0123456789abcdef"
            for character in text
        )
    ):
        _raise(
            HrDocumentRegistryInputError,
            "P0_C12F4B_FINGERPRINT_INVALID",
        )

    return text


def _datetime_from_iso(
    name: str,
    value: object,
) -> datetime:
    text = _text(
        name,
        value,
    )

    try:
        parsed = datetime.fromisoformat(
            text
        )
    except ValueError as error:
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            f"P0_C12F4B_{name.upper()}_INVALID",
            error,
        )

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            f"P0_C12F4B_{name.upper()}_UTC_REQUIRED",
        )

    return parsed


def serialize_document(
    value: HrDocument,
) -> dict[str, object]:
    if type(value) is not HrDocument:
        _raise(
            HrDocumentRegistryInputError,
            "P0_C12F4B_HR_DOCUMENT_REQUIRED",
        )

    try:
        value.__post_init__()
    except Exception as error:
        _raise(
            HrDocumentRegistryInputError,
            "P0_C12F4B_HR_DOCUMENT_INVALID",
            error,
        )

    return {
        "tenant_id": value.tenant_id,
        "employee_id": value.employee_id,
        "document_id": value.document_id,
        "document_version_id": value.document_version_id,
        "document_class": value.document_class.value,
        "sensitivity": value.sensitivity.value,
        "original_filename": value.original_filename,
        "media_type": value.media_type,
        "byte_length": value.byte_length,
        "content_digest_sha3_512": value.content_digest_sha3_512,
        "storage_provider_id": value.storage_provider_id,
        "storage_object_reference": value.storage_object_reference,
        "object_version_reference": value.object_version_reference,
        "provider_integrity_reference": value.provider_integrity_reference,
        "created_at": value.created_at.isoformat(),
        "created_by_principal_id": value.created_by_principal_id,
        "retention_until": (
            value.retention_until.isoformat()
            if value.retention_until is not None
            else None
        ),
        "legal_hold": value.legal_hold,
        "supersedes_version_id": value.supersedes_version_id,
        "schema": value.schema,
        "fingerprint": value.fingerprint,
    }


def _hydrate(
    document: Mapping[str, Any],
) -> HrDocument:
    if not isinstance(document, Mapping):
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError
        )

    raw = dict(document)
    raw.pop("_id", None)

    if set(raw) != set(HR_DOCUMENT_RECORD_FIELDS):
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_RECORD_SCHEMA_INVALID",
        )

    try:
        value = HrDocument(
            tenant_id=cast(str, raw["tenant_id"]),
            employee_id=cast(str, raw["employee_id"]),
            document_id=cast(str, raw["document_id"]),
            document_version_id=cast(
                str,
                raw["document_version_id"],
            ),
            document_class=HrDocumentClass(
                cast(
                    str,
                    raw["document_class"],
                )
            ),
            sensitivity=HrDocumentSensitivity(
                cast(
                    str,
                    raw["sensitivity"],
                )
            ),
            original_filename=cast(
                str,
                raw["original_filename"],
            ),
            media_type=cast(
                str,
                raw["media_type"],
            ),
            byte_length=cast(
                int,
                raw["byte_length"],
            ),
            content_digest_sha3_512=cast(
                str,
                raw["content_digest_sha3_512"],
            ),
            storage_provider_id=cast(
                str,
                raw["storage_provider_id"],
            ),
            storage_object_reference=cast(
                str,
                raw["storage_object_reference"],
            ),
            object_version_reference=cast(
                str,
                raw["object_version_reference"],
            ),
            provider_integrity_reference=cast(
                str,
                raw["provider_integrity_reference"],
            ),
            created_at=_datetime_from_iso(
                "created_at",
                raw["created_at"],
            ),
            created_by_principal_id=cast(
                str,
                raw["created_by_principal_id"],
            ),
            retention_until=(
                None
                if raw["retention_until"] is None
                else _datetime_from_iso(
                    "retention_until",
                    raw["retention_until"],
                )
            ),
            legal_hold=cast(
                bool,
                raw["legal_hold"],
            ),
            supersedes_version_id=cast(
                str | None,
                raw["supersedes_version_id"],
            ),
            schema=cast(
                str,
                raw["schema"],
            ),
            fingerprint=cast(
                str,
                raw["fingerprint"],
            ),
        )

    except (
        TypeError,
        ValueError,
        HrDocumentDomainError,
    ) as error:
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_DOCUMENT_PAYLOAD_INVALID",
            error,
        )

    if serialize_document(value) != raw:
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_RECORD_CORRELATION_INVALID",
        )

    return value


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int,
    sort: list[tuple[str, int]] | None = None,
) -> list[Mapping[str, Any]]:
    target = _collection(collection)

    try:
        cursor = target.find(
            dict(query),
            session=session,
        )

        if (
            sort is not None
            and hasattr(cursor, "sort")
        ):
            cursor = cursor.sort(sort)

        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)

        return [
            cast(
                Mapping[str, Any],
                row,
            )
            for row in cursor
        ]

    except PyMongoError as error:
        _raise_mongo(error)

    except AttributeError as error:
        _raise(
            HrDocumentRegistryInputError,
            "P0_C12F4B_COLLECTION_INTERFACE_INVALID",
            error,
        )


def ensure_indexes(
    collection: Any,
) -> None:
    target = _collection(collection)

    try:
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("document_version_id", ASCENDING),
            ],
            unique=True,
            name=DOCUMENT_VERSION_INDEX_NAME,
        )

        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            unique=True,
            name=FINGERPRINT_INDEX_NAME,
        )

        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("employee_id", ASCENDING),
                ("created_at", DESCENDING),
            ],
            unique=False,
            name=EMPLOYEE_CREATED_INDEX_NAME,
        )

        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("employee_id", ASCENDING),
                ("document_id", ASCENDING),
                ("created_at", DESCENDING),
            ],
            unique=False,
            name=DOCUMENT_HISTORY_INDEX_NAME,
        )

        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("employee_id", ASCENDING),
                ("document_class", ASCENDING),
                ("created_at", DESCENDING),
            ],
            unique=False,
            name=EMPLOYEE_CLASS_INDEX_NAME,
        )

        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("employee_id", ASCENDING),
                ("sensitivity", ASCENDING),
                ("created_at", DESCENDING),
            ],
            unique=False,
            name=EMPLOYEE_SENSITIVITY_INDEX_NAME,
        )

    except PyMongoError as error:
        _raise_mongo(error)

    except AttributeError as error:
        _raise(
            HrDocumentRegistryInputError,
            "P0_C12F4B_COLLECTION_INTERFACE_INVALID",
            error,
        )


def get_document_version(
    tenant_id: str,
    document_version_id: str,
    collection: Any,
    *,
    session: Any,
) -> HrDocument:
    tx = _active_transaction(session)

    tenant = _text(
        "tenant_id",
        tenant_id,
    )

    version = _text(
        "document_version_id",
        document_version_id,
    )

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "document_version_id": version,
        },
        session=tx,
        limit=2,
    )

    if not rows:
        _raise(
            HrDocumentRegistryNotFoundError
        )

    if len(rows) > 1:
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_DUPLICATE_DOCUMENT_VERSION",
        )

    return _hydrate(rows[0])


def get_document_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    collection: Any,
    *,
    session: Any,
) -> HrDocument:
    tx = _active_transaction(session)

    tenant = _text(
        "tenant_id",
        tenant_id,
    )

    digest = _fingerprint(
        fingerprint
    )

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "fingerprint": digest,
        },
        session=tx,
        limit=2,
    )

    if not rows:
        _raise(
            HrDocumentRegistryNotFoundError
        )

    if len(rows) > 1:
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_DUPLICATE_DOCUMENT_FINGERPRINT",
        )

    return _hydrate(rows[0])


def _sorted_documents(
    rows: list[Mapping[str, Any]],
    *,
    tenant_id: str,
    employee_id: str,
) -> tuple[HrDocument, ...]:
    if len(rows) > MAX_HR_DOCUMENT_ROWS:
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_DOCUMENT_LIMIT_EXCEEDED",
        )

    values = tuple(
        _hydrate(row)
        for row in rows
    )

    if any(
        value.tenant_id != tenant_id
        or value.employee_id != employee_id
        for value in values
    ):
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_SCOPE_CORRELATION_INVALID",
        )

    return tuple(
        sorted(
            values,
            key=lambda item: (
                item.created_at,
                item.document_version_id,
            ),
            reverse=True,
        )
    )


def list_employee_documents(
    tenant_id: str,
    employee_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[HrDocument, ...]:
    tx = _active_transaction(session)

    tenant = _text(
        "tenant_id",
        tenant_id,
    )

    employee = _text(
        "employee_id",
        employee_id,
    )

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "employee_id": employee,
        },
        session=tx,
        limit=MAX_HR_DOCUMENT_ROWS + 1,
        sort=[
            ("created_at", DESCENDING),
            ("document_version_id", ASCENDING),
        ],
    )

    return _sorted_documents(
        rows,
        tenant_id=tenant,
        employee_id=employee,
    )


def list_document_versions(
    tenant_id: str,
    employee_id: str,
    document_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[HrDocument, ...]:
    tx = _active_transaction(session)

    tenant = _text(
        "tenant_id",
        tenant_id,
    )

    employee = _text(
        "employee_id",
        employee_id,
    )

    document = _text(
        "document_id",
        document_id,
    )

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "employee_id": employee,
            "document_id": document,
        },
        session=tx,
        limit=MAX_HR_DOCUMENT_ROWS + 1,
        sort=[
            ("created_at", DESCENDING),
            ("document_version_id", ASCENDING),
        ],
    )

    return _sorted_documents(
        rows,
        tenant_id=tenant,
        employee_id=employee,
    )


def list_employee_documents_by_class(
    tenant_id: str,
    employee_id: str,
    document_class: HrDocumentClass,
    collection: Any,
    *,
    session: Any,
) -> tuple[HrDocument, ...]:
    tx = _active_transaction(session)

    tenant = _text(
        "tenant_id",
        tenant_id,
    )

    employee = _text(
        "employee_id",
        employee_id,
    )

    if type(document_class) is not HrDocumentClass:
        _raise(
            HrDocumentRegistryInputError,
            "P0_C12F4B_DOCUMENT_CLASS_INVALID",
        )

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "employee_id": employee,
            "document_class": document_class.value,
        },
        session=tx,
        limit=MAX_HR_DOCUMENT_ROWS + 1,
        sort=[
            ("created_at", DESCENDING),
            ("document_version_id", ASCENDING),
        ],
    )

    return _sorted_documents(
        rows,
        tenant_id=tenant,
        employee_id=employee,
    )


def persist_document(
    document: HrDocument,
    collection: Any,
    *,
    session: Any,
) -> HrDocument:
    tx = _active_transaction(session)

    if type(document) is not HrDocument:
        _raise(
            HrDocumentRegistryInputError,
            "P0_C12F4B_HR_DOCUMENT_REQUIRED",
        )

    payload = serialize_document(
        document
    )

    target = _collection(
        collection
    )

    existing = _rows(
        target,
        {
            "tenant_id": document.tenant_id,
            "document_version_id": document.document_version_id,
        },
        session=tx,
        limit=2,
    )

    if len(existing) > 1:
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_DUPLICATE_DOCUMENT_VERSION",
        )

    if existing:
        hydrated = _hydrate(
            existing[0]
        )

        if serialize_document(hydrated) == payload:
            return hydrated

        _raise(
            HrDocumentRegistryConflictError
        )

    by_fingerprint = _rows(
        target,
        {
            "tenant_id": document.tenant_id,
            "fingerprint": document.fingerprint,
        },
        session=tx,
        limit=2,
    )

    if len(by_fingerprint) > 1:
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_DUPLICATE_DOCUMENT_FINGERPRINT",
        )

    if by_fingerprint:
        hydrated = _hydrate(
            by_fingerprint[0]
        )

        if serialize_document(hydrated) == payload:
            return hydrated

        _raise(
            HrDocumentRegistryConflictError
        )

    try:
        target.insert_one(
            dict(payload),
            session=tx,
        )

    except DuplicateKeyError:
        try:
            replay = get_document_version(
                document.tenant_id,
                document.document_version_id,
                target,
                session=tx,
            )

            if serialize_document(replay) == payload:
                return replay

            _raise(
                HrDocumentRegistryConflictError
            )

        except HrDocumentRegistryNotFoundError:
            try:
                replay = get_document_by_fingerprint(
                    document.tenant_id,
                    document.fingerprint,
                    target,
                    session=tx,
                )
            except HrDocumentRegistryNotFoundError:
                _raise(
                    HrDocumentRegistryRetryRequiredError
                )

            if serialize_document(replay) == payload:
                return replay

            _raise(
                HrDocumentRegistryConflictError
            )

    except PyMongoError as error:
        _raise_mongo(error)

    persisted = get_document_version(
        document.tenant_id,
        document.document_version_id,
        target,
        session=tx,
    )

    if serialize_document(
        persisted
    ) != payload:
        _raise(
            HrDocumentRegistryPersistedRecordInvalidError,
            "P0_C12F4B_POST_WRITE_CORRELATION_INVALID",
        )

    return persisted


class HrDocumentRegistry:
    ensure_indexes = staticmethod(
        ensure_indexes
    )
    get_document_version = staticmethod(
        get_document_version
    )
    get_document_by_fingerprint = staticmethod(
        get_document_by_fingerprint
    )
    list_employee_documents = staticmethod(
        list_employee_documents
    )
    list_document_versions = staticmethod(
        list_document_versions
    )
    list_employee_documents_by_class = staticmethod(
        list_employee_documents_by_class
    )
    persist_document = staticmethod(
        persist_document
    )


__all__ = [
    "VERSION",
    "COLLECTION",
    "DOCUMENT_VERSION_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "EMPLOYEE_CREATED_INDEX_NAME",
    "DOCUMENT_HISTORY_INDEX_NAME",
    "EMPLOYEE_CLASS_INDEX_NAME",
    "EMPLOYEE_SENSITIVITY_INDEX_NAME",
    "MAX_HR_DOCUMENT_ROWS",
    "WRITE_CONCERN",
    "READ_CONCERN",
    "HR_DOCUMENT_RECORD_FIELDS",
    "HrDocumentRegistry",
    "HrDocumentRegistryError",
    "HrDocumentRegistryInputError",
    "HrDocumentRegistryTransactionRequiredError",
    "HrDocumentRegistryNotFoundError",
    "HrDocumentRegistryConflictError",
    "HrDocumentRegistryPersistedRecordInvalidError",
    "HrDocumentRegistryRetryRequiredError",
    "HrDocumentRegistryPersistenceUnavailableError",
    "serialize_document",
    "ensure_indexes",
    "get_document_version",
    "get_document_by_fingerprint",
    "list_employee_documents",
    "list_document_versions",
    "list_employee_documents_by_class",
    "persist_document",
]


# ARTIFACT: tools/eos/saas/hr/hr_document_registry.py
# VERSION: v1.0.0-P0-C12F4B-HR-DOCUMENT-REGISTRY
# AUTHORITY BOUNDARY: immutable HR document-version metadata persistence only
# TRANSACTION BOUNDARY: caller-owned active transaction required
# STORAGE BOUNDARY: no raw document bytes stored by this registry
# RETENTION BOUNDARY: no TTL or deletion authority
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
