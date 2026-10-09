"""WILSY OS durable immutable Legal evidence-content registry.

TITLE: Legal Evidence Content Registry
VERSION: v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist exact L10A1 Legal evidence metadata together with immutable raw
         bytes under tenant/matter/document scope, verify byte identity on every
         hydration, and provide bounded reads without creating lifecycle,
         Court, IAM, AI or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_content_registry.py
COLLABORATION / OWNERSHIP: L10A1 owns content identity and admissible media
                            semantics. L10A2 owns only durable byte persistence,
                            exact replay and corruption-detecting reads.
                            ProcessDocument/custody remain owned by the Legal
                            Operations lifecycle. HTTP/IAM admission is later.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: 2026-09-29 v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY establishes
           the legal_evidence_contents collection, exact tenant/reference
           uniqueness, tenant/matter/document bounded reads, majority durability,
           active caller-owned transaction requirements, exact replay,
           divergent-content conflict, whole-transaction duplicate-race signal,
           metadata/byte correlation verification and no TTL/update/delete path.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw admitted bytes are durable confidential tenant
                             content. Every read revalidates L10A1 metadata,
                             byte length and SHA3-512 content identity before
                             returning any value or bytes.
TENANT BOUNDARY: Every operational query and write begins with exact tenant_id
                 and every document listing additionally binds case_matter_id
                 and document_id. No foreign-tenant fallback exists.
AUTHORITY BOUNDARY: Durable content evidence only. Persistence does not create
                    CaseMatter, instruction, ProcessDocument, custody, service,
                    Court/Court Online filing, client visibility, IAM or AI
                    authority.
FINANCIAL AUTHORITY BOUNDARY: No billing, invoice, payment, execution or
                              settlement truth. Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Operational reads/writes require one already-active
                      caller-owned transaction. This registry never starts,
                      commits, aborts or retries transactions.
FAIL-CLOSED DECLARATION: Missing transactions, malformed scope, byte/metadata
                         corruption, divergent replay, duplicate races,
                         unsupported collection interfaces and Mongo outages
                         reject without healing or inferred truth.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from datetime import timezone
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_content import (
    LEGAL_EVIDENCE_CONTENT_FIELDS,
    LegalEvidenceContent,
    LegalEvidenceContentError,
    content_fingerprint,
)


VERSION: Final[str] = "v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY"
COLLECTION: Final[str] = "legal_evidence_contents"

REFERENCE_INDEX_NAME: Final[str] = (
    "legal_evidence_content_tenant_reference_unique"
)
DOCUMENT_INDEX_NAME: Final[str] = (
    "legal_evidence_content_tenant_matter_document_registered"
)
CONTENT_FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_evidence_content_tenant_document_content_fingerprint"
)

MAX_DOCUMENT_CONTENTS: Final[int] = 500

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")

_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    (*LEGAL_EVIDENCE_CONTENT_FIELDS, "content_bytes")
)


class LegalEvidenceContentRegistryError(RuntimeError):
    """Base fail-closed L10A2 persistence/read error."""

    default_code = "L10A2_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create one stable non-secret registry error."""
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalEvidenceContentRegistryInputError(
    LegalEvidenceContentRegistryError
):
    """Malformed caller input or unsupported persistence surface."""

    default_code = "L10A2_INPUT_INVALID"


class LegalEvidenceContentRegistryTransactionRequiredError(
    LegalEvidenceContentRegistryError
):
    """Caller did not provide one already-active transaction."""

    default_code = "L10A2_ACTIVE_TRANSACTION_REQUIRED"


class LegalEvidenceContentRegistryNotFoundError(
    LegalEvidenceContentRegistryError
):
    """No exact tenant-scoped evidence-content reference exists."""

    default_code = "L10A2_CONTENT_NOT_FOUND"


class LegalEvidenceContentRegistryConflictError(
    LegalEvidenceContentRegistryError
):
    """One immutable reference is already bound to divergent evidence."""

    default_code = "L10A2_CONTENT_CONFLICT"


class LegalEvidenceContentRegistryPersistedRecordInvalidError(
    LegalEvidenceContentRegistryError
):
    """Persisted metadata or raw bytes fail exact integrity validation."""

    default_code = "L10A2_PERSISTED_RECORD_INVALID"


class LegalEvidenceContentRegistryRetryRequiredError(
    LegalEvidenceContentRegistryError
):
    """Caller must restart the complete transaction after a write race."""

    default_code = "L10A2_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalEvidenceContentRegistryPersistenceUnavailableError(
    LegalEvidenceContentRegistryError
):
    """Mongo persistence is unavailable or failed safely."""

    default_code = "L10A2_PERSISTENCE_UNAVAILABLE"


def _raise(
    error_type: type[LegalEvidenceContentRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded registry error while preserving technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    """Translate Mongo failure without owning retry or transaction lifecycle."""
    if error.has_error_label("TransientTransactionError"):
        _raise(
            LegalEvidenceContentRegistryRetryRequiredError,
            cause=error,
        )
    _raise(
        LegalEvidenceContentRegistryPersistenceUnavailableError,
        cause=error,
    )


def _target(collection: Any) -> Any:
    """Apply majority durability and timezone-aware BSON options."""
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


def _collection(value: Any) -> Any:
    """Require one usable collection-like persistence target."""
    if value is None:
        _raise(
            LegalEvidenceContentRegistryInputError,
            "L10A2_COLLECTION_REQUIRED",
        )
    return _target(value)


def _active_transaction(session: Any) -> Any:
    """Require one already-active caller-owned transaction."""
    if session is None:
        _raise(
            LegalEvidenceContentRegistryTransactionRequiredError,
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(
            LegalEvidenceContentRegistryTransactionRequiredError,
        )
    return session


def _text(name: str, value: object) -> str:
    """Require one exact non-empty query identity without coercion."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        _raise(
            LegalEvidenceContentRegistryInputError,
            f"L10A2_{name.upper()}_INVALID",
        )
    return value


def _normalize_bytes(value: object) -> bytes:
    """Return exact BSON/Python bytes or reject persisted corruption."""
    if not isinstance(value, (bytes, bytearray)):
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_CONTENT_BYTES_INVALID",
        )
    return bytes(value)


def _hydrate(
    document: Mapping[str, Any],
) -> tuple[LegalEvidenceContent, bytes]:
    """Hydrate exact L10A1 metadata and cryptographically verify raw bytes."""
    if not isinstance(document, Mapping):
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
        )

    raw = dict(document)
    raw.pop("_id", None)

    if set(raw) != _RECORD_FIELDS:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_RECORD_SCHEMA_INVALID",
        )

    content = _normalize_bytes(raw.pop("content_bytes"))

    try:
        value = LegalEvidenceContent.from_dict(
            cast(Mapping[str, object], raw)
        )
    except (TypeError, ValueError, LegalEvidenceContentError) as error:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_METADATA_INVALID",
            error,
        )

    if value.to_dict() != raw:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_METADATA_CORRELATION_INVALID",
        )

    if len(content) != value.content_length:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_CONTENT_LENGTH_MISMATCH",
        )

    try:
        digest = content_fingerprint(content)
    except LegalEvidenceContentError as error:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_CONTENT_BYTES_INVALID",
            error,
        )

    if digest != value.content_fingerprint:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_CONTENT_FINGERPRINT_MISMATCH",
        )

    return value, content


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int,
    sort: list[tuple[str, int]] | None = None,
) -> list[Mapping[str, Any]]:
    """Read bounded rows with exact caller-session propagation."""
    target = _collection(collection)
    try:
        cursor = target.find(dict(query), session=session)
        if sort is not None and hasattr(cursor, "sort"):
            cursor = cursor.sort(sort)
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [
            cast(Mapping[str, Any], row)
            for row in cursor
        ]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalEvidenceContentRegistryInputError,
            "L10A2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def ensure_indexes(collection: Any) -> None:
    """Create immutable identity/read indexes; deliberately create no TTL."""
    target = _collection(collection)
    try:
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("content_reference", ASCENDING),
            ],
            unique=True,
            name=REFERENCE_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("document_id", ASCENDING),
                ("registered_at", DESCENDING),
            ],
            unique=False,
            name=DOCUMENT_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("document_id", ASCENDING),
                ("content_fingerprint", ASCENDING),
            ],
            unique=False,
            name=CONTENT_FINGERPRINT_INDEX_NAME,
        )
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalEvidenceContentRegistryInputError,
            "L10A2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def get_evidence_content(
    tenant_id: str,
    content_reference: str,
    collection: Any,
    *,
    session: Any,
) -> LegalEvidenceContent:
    """Read one exact tenant-scoped metadata identity after byte verification."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    reference = _text("content_reference", content_reference)

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "content_reference": reference,
        },
        session=tx,
        limit=2,
    )

    if not rows:
        _raise(LegalEvidenceContentRegistryNotFoundError)

    if len(rows) > 1:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_DUPLICATE_REFERENCE",
        )

    value, _ = _hydrate(rows[0])

    if (
        value.tenant_id != tenant
        or value.content_reference != reference
    ):
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_SCOPE_CORRELATION_INVALID",
        )

    return value


def read_evidence_content_bytes(
    tenant_id: str,
    content_reference: str,
    collection: Any,
    *,
    session: Any,
) -> bytes:
    """Read exact confidential bytes only after metadata/content revalidation."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    reference = _text("content_reference", content_reference)

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "content_reference": reference,
        },
        session=tx,
        limit=2,
    )

    if not rows:
        _raise(LegalEvidenceContentRegistryNotFoundError)

    if len(rows) > 1:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_DUPLICATE_REFERENCE",
        )

    value, content = _hydrate(rows[0])

    if (
        value.tenant_id != tenant
        or value.content_reference != reference
    ):
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_SCOPE_CORRELATION_INVALID",
        )

    return content


def list_document_evidence_contents(
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalEvidenceContent, ...]:
    """List bounded immutable content versions for one exact process document."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    matter = _text("case_matter_id", case_matter_id)
    document = _text("document_id", document_id)

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "case_matter_id": matter,
            "document_id": document,
        },
        session=tx,
        limit=MAX_DOCUMENT_CONTENTS + 1,
        sort=[
            ("registered_at", DESCENDING),
            ("content_reference", ASCENDING),
        ],
    )

    if len(rows) > MAX_DOCUMENT_CONTENTS:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_DOCUMENT_CONTENT_LIMIT_EXCEEDED",
        )

    values: list[LegalEvidenceContent] = []

    for row in rows:
        value, _ = _hydrate(row)
        if (
            value.tenant_id != tenant
            or value.case_matter_id != matter
            or value.document_id != document
        ):
            _raise(
                LegalEvidenceContentRegistryPersistedRecordInvalidError,
                "L10A2_SCOPE_CORRELATION_INVALID",
            )
        values.append(value)

    return tuple(
        sorted(
            values,
            key=lambda item: (
                item.registered_at,
                item.content_reference,
            ),
            reverse=True,
        )
    )


def persist_evidence_content(
    value: LegalEvidenceContent,
    content: bytes,
    collection: Any,
    *,
    session: Any,
) -> LegalEvidenceContent:
    """Persist one immutable metadata/byte pair or return its exact replay.

    The exact L10A1 metadata and exact bytes must correlate before any write.
    Existing identical durable evidence replays. Same reference with divergent
    metadata or bytes conflicts. Duplicate-key races require the caller to abort
    and restart the complete transaction.
    """
    tx = _active_transaction(session)

    if type(value) is not LegalEvidenceContent:
        _raise(
            LegalEvidenceContentRegistryInputError,
            "L10A2_CONTENT_VALUE_REQUIRED",
        )

    if not isinstance(content, bytes):
        _raise(
            LegalEvidenceContentRegistryInputError,
            "L10A2_CONTENT_BYTES_REQUIRED",
        )

    try:
        digest = content_fingerprint(content)
    except LegalEvidenceContentError as error:
        _raise(
            LegalEvidenceContentRegistryInputError,
            "L10A2_CONTENT_BYTES_INVALID",
            error,
        )

    if (
        len(content) != value.content_length
        or digest != value.content_fingerprint
    ):
        _raise(
            LegalEvidenceContentRegistryInputError,
            "L10A2_CONTENT_CORRELATION_INVALID",
        )

    target = _collection(collection)

    existing = _rows(
        target,
        {
            "tenant_id": value.tenant_id,
            "content_reference": value.content_reference,
        },
        session=tx,
        limit=2,
    )

    if len(existing) > 1:
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_DUPLICATE_REFERENCE",
        )

    if existing:
        persisted, persisted_bytes = _hydrate(existing[0])
        if (
            persisted.to_dict() == value.to_dict()
            and persisted_bytes == content
        ):
            return persisted
        _raise(LegalEvidenceContentRegistryConflictError)

    row = {
        **value.to_dict(),
        "content_bytes": content,
    }

    try:
        target.insert_one(row, session=tx)
    except DuplicateKeyError as error:
        _raise(
            LegalEvidenceContentRegistryRetryRequiredError,
            cause=error,
        )
    except PyMongoError as error:
        _raise_mongo(error)

    persisted = get_evidence_content(
        value.tenant_id,
        value.content_reference,
        target,
        session=tx,
    )
    persisted_bytes = read_evidence_content_bytes(
        value.tenant_id,
        value.content_reference,
        target,
        session=tx,
    )

    if (
        persisted.to_dict() != value.to_dict()
        or persisted_bytes != content
    ):
        _raise(
            LegalEvidenceContentRegistryPersistedRecordInvalidError,
            "L10A2_POST_WRITE_CORRELATION_INVALID",
        )

    return persisted


class LegalEvidenceContentRegistry:
    """Namespace facade for immutable Legal evidence-content persistence."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_evidence_content = staticmethod(get_evidence_content)
    read_evidence_content_bytes = staticmethod(
        read_evidence_content_bytes
    )
    list_document_evidence_contents = staticmethod(
        list_document_evidence_contents
    )
    persist_evidence_content = staticmethod(
        persist_evidence_content
    )


__all__ = [
    "COLLECTION",
    "CONTENT_FINGERPRINT_INDEX_NAME",
    "DOCUMENT_INDEX_NAME",
    "MAX_DOCUMENT_CONTENTS",
    "READ_CONCERN",
    "REFERENCE_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "LegalEvidenceContentRegistry",
    "LegalEvidenceContentRegistryConflictError",
    "LegalEvidenceContentRegistryError",
    "LegalEvidenceContentRegistryInputError",
    "LegalEvidenceContentRegistryNotFoundError",
    "LegalEvidenceContentRegistryPersistedRecordInvalidError",
    "LegalEvidenceContentRegistryPersistenceUnavailableError",
    "LegalEvidenceContentRegistryRetryRequiredError",
    "LegalEvidenceContentRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_evidence_content",
    "list_document_evidence_contents",
    "persist_evidence_content",
    "read_evidence_content_bytes",
]

# ARTIFACT: legal_evidence_content_registry.py
# VERSION: v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY
# AUTHORITY BOUNDARY: immutable Legal evidence metadata/raw-byte persistence and bounded reads only
# TENANT POSTURE: every operational query/write is exact-tenant scoped; document lists also bind exact matter/document
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/race/outage rejects; no TTL/update/delete
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
