"""Dedicated durable acceptance-instrument content authority.

TITLE: Legal Client Matter Acceptance Instrument Content Registry
VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and retrieve immutable instrument metadata plus exact bytes
         inside a caller-owned active Mongo transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_acceptance_instrument_content_registry.py
COLLABORATION / OWNERSHIP: The content domain owns identity; this registry owns
                            only dedicated storage and integrity reads.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0 establishes majority durability, exact replay,
           corruption detection and whole-transaction retry signaling.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Confidential bytes are always exact-tenant scoped
                             and cryptographically revalidated before return.
TENANT BOUNDARY: Every query starts with tenant_id and exact content reference.
AUTHORITY BOUNDARY: Storage only; no lifecycle, approval or acceptance authority.
TRANSACTION BOUNDARY: Caller owns start, commit, abort and whole retry.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing transaction, corruption, divergence, race or
                         outage rejects without update, delete or healing.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import timezone
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_content import (
    CONTENT_FIELDS,
    LegalClientMatterAcceptanceInstrumentContent,
    LegalClientMatterAcceptanceInstrumentContentError,
    content_fingerprint,
)


VERSION: Final[str] = "v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_acceptance_instrument_contents"
IDENTITY_INDEX_NAME: Final[str] = "client_acceptance_instrument_content_identity_unique"
REFERENCE_INDEX_NAME: Final[str] = "client_acceptance_instrument_content_reference_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "client_acceptance_instrument_content_fingerprint_lookup"
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")
_RECORD_FIELDS = frozenset((*CONTENT_FIELDS, "content_bytes"))


class LegalClientMatterAcceptanceInstrumentContentRegistryError(RuntimeError):
    """Base bounded persistence failure."""
    default_code = "CLIENT_ACCEPTANCE_CONTENT_REGISTRY_ERROR"
    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalClientMatterAcceptanceInstrumentContentRegistryInputError(LegalClientMatterAcceptanceInstrumentContentRegistryError):
    """Malformed input or collection capability."""
class LegalClientMatterAcceptanceInstrumentContentRegistryTransactionRequiredError(LegalClientMatterAcceptanceInstrumentContentRegistryError):
    """Caller-owned active transaction is absent."""
class LegalClientMatterAcceptanceInstrumentContentRegistryNotFoundError(LegalClientMatterAcceptanceInstrumentContentRegistryError):
    """Exact tenant-scoped content is absent."""
class LegalClientMatterAcceptanceInstrumentContentRegistryConflictError(LegalClientMatterAcceptanceInstrumentContentRegistryError):
    """Immutable identity is bound to divergent truth."""
class LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError(LegalClientMatterAcceptanceInstrumentContentRegistryError):
    """Stored metadata or bytes are corrupt."""
class LegalClientMatterAcceptanceInstrumentContentRegistryRetryRequiredError(LegalClientMatterAcceptanceInstrumentContentRegistryError):
    """Caller must restart the complete transaction."""
class LegalClientMatterAcceptanceInstrumentContentRegistryPersistenceUnavailableError(LegalClientMatterAcceptanceInstrumentContentRegistryError):
    """Persistence failed without durable certainty."""


def _raise(error_type: type[LegalClientMatterAcceptanceInstrumentContentRegistryError], code: str, cause: BaseException | None = None) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryRetryRequiredError, "CLIENT_ACCEPTANCE_CONTENT_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    _raise(LegalClientMatterAcceptanceInstrumentContentRegistryPersistenceUnavailableError, "CLIENT_ACCEPTANCE_CONTENT_PERSISTENCE_UNAVAILABLE", error)


def _active(session: Any) -> Any:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryTransactionRequiredError, "CLIENT_ACCEPTANCE_CONTENT_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _target(collection: Any) -> Any:
    if collection is None:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryInputError, "CLIENT_ACCEPTANCE_CONTENT_COLLECTION_REQUIRED")
    try:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN, codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
    except AttributeError:
        return collection


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryInputError, f"CLIENT_ACCEPTANCE_CONTENT_{name.upper()}_INVALID")
    return value


def _hydrate(row: Mapping[str, Any]) -> tuple[LegalClientMatterAcceptanceInstrumentContent, bytes]:
    raw = dict(row)
    raw.pop("_id", None)
    if set(raw) != _RECORD_FIELDS:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError, "CLIENT_ACCEPTANCE_CONTENT_RECORD_SCHEMA_INVALID")
    content = raw.pop("content_bytes")
    if not isinstance(content, (bytes, bytearray)):
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError, "CLIENT_ACCEPTANCE_CONTENT_BYTES_INVALID")
    exact = bytes(content)
    try:
        value = LegalClientMatterAcceptanceInstrumentContent.from_dict(cast(Mapping[str, object], raw))
        digest = content_fingerprint(exact)
    except (TypeError, ValueError, LegalClientMatterAcceptanceInstrumentContentError) as error:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError, "CLIENT_ACCEPTANCE_CONTENT_RECORD_INVALID", error)
    if value.to_dict() != raw or len(exact) != value.content_length or digest != value.content_fingerprint:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError, "CLIENT_ACCEPTANCE_CONTENT_CORRELATION_INVALID")
    return value, exact


def _rows(collection: Any, query: Mapping[str, object], *, session: Any) -> list[Mapping[str, Any]]:
    try:
        cursor = _target(collection).find(dict(query), session=session)
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(2)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _mongo(error)
    except AttributeError as error:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryInputError, "CLIENT_ACCEPTANCE_CONTENT_COLLECTION_INTERFACE_INVALID", error)


def ensure_indexes(collection: Any) -> None:
    """Create immutable lookup indexes and deliberately no TTL index."""
    target = _target(collection)
    try:
        target.create_index([("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("instrument_id", ASCENDING), ("instrument_version", ASCENDING)], unique=True, name=IDENTITY_INDEX_NAME)
        target.create_index([("tenant_id", ASCENDING), ("content_reference", ASCENDING)], unique=True, name=REFERENCE_INDEX_NAME)
        target.create_index([("tenant_id", ASCENDING), ("content_fingerprint", ASCENDING)], unique=False, name=FINGERPRINT_INDEX_NAME)
    except PyMongoError as error:
        _mongo(error)
    except AttributeError as error:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryInputError, "CLIENT_ACCEPTANCE_CONTENT_COLLECTION_INTERFACE_INVALID", error)


def read_content(tenant_id: str, content_reference: str, collection: Any, *, session: Any) -> tuple[LegalClientMatterAcceptanceInstrumentContent, bytes]:
    """Read exact tenant-scoped metadata and bytes after full revalidation."""
    tx = _active(session)
    tenant = _text("tenant_id", tenant_id)
    reference = _text("content_reference", content_reference)
    rows = _rows(collection, {"tenant_id": tenant, "content_reference": reference}, session=tx)
    if not rows:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryNotFoundError, "CLIENT_ACCEPTANCE_CONTENT_NOT_FOUND")
    if len(rows) != 1:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError, "CLIENT_ACCEPTANCE_CONTENT_DUPLICATE_REFERENCE")
    value, content = _hydrate(rows[0])
    if value.tenant_id != tenant or value.content_reference != reference:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError, "CLIENT_ACCEPTANCE_CONTENT_SCOPE_INVALID")
    return value, content


def persist_content(value: LegalClientMatterAcceptanceInstrumentContent, content: bytes, collection: Any, *, session: Any) -> LegalClientMatterAcceptanceInstrumentContent:
    """Persist exact immutable content, exactly replay, or reject divergence."""
    tx = _active(session)
    if type(value) is not LegalClientMatterAcceptanceInstrumentContent or not isinstance(content, bytes):
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryInputError, "CLIENT_ACCEPTANCE_CONTENT_VALUE_REQUIRED")
    try:
        digest = content_fingerprint(content)
    except LegalClientMatterAcceptanceInstrumentContentError as error:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryInputError, "CLIENT_ACCEPTANCE_CONTENT_BYTES_INVALID", error)
    if len(content) != value.content_length or digest != value.content_fingerprint:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryInputError, "CLIENT_ACCEPTANCE_CONTENT_INPUT_CORRELATION_INVALID")
    target = _target(collection)
    query = {"tenant_id": value.tenant_id, "content_reference": value.content_reference}
    existing = _rows(target, query, session=tx)
    if len(existing) > 1:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError, "CLIENT_ACCEPTANCE_CONTENT_DUPLICATE_REFERENCE")
    if existing:
        persisted, persisted_bytes = _hydrate(existing[0])
        if persisted.to_dict() == value.to_dict() and persisted_bytes == content:
            return persisted
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryConflictError, "CLIENT_ACCEPTANCE_CONTENT_REPLAY_CONFLICT")
    try:
        target.insert_one({**value.to_dict(), "content_bytes": content}, session=tx)
    except DuplicateKeyError as error:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryRetryRequiredError, "CLIENT_ACCEPTANCE_CONTENT_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except PyMongoError as error:
        _mongo(error)
    persisted, persisted_bytes = read_content(value.tenant_id, value.content_reference, target, session=tx)
    if persisted.to_dict() != value.to_dict() or persisted_bytes != content:
        _raise(LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError, "CLIENT_ACCEPTANCE_CONTENT_POST_WRITE_CORRELATION_INVALID")
    return persisted


class LegalClientMatterAcceptanceInstrumentContentRegistry:
    """Namespace facade for immutable dedicated content persistence."""
    ensure_indexes = staticmethod(ensure_indexes)
    persist_content = staticmethod(persist_content)
    read_content = staticmethod(read_content)


__all__ = ["COLLECTION", "FINGERPRINT_INDEX_NAME", "IDENTITY_INDEX_NAME", "REFERENCE_INDEX_NAME", "VERSION", "LegalClientMatterAcceptanceInstrumentContentRegistry", "LegalClientMatterAcceptanceInstrumentContentRegistryConflictError", "LegalClientMatterAcceptanceInstrumentContentRegistryError", "LegalClientMatterAcceptanceInstrumentContentRegistryInputError", "LegalClientMatterAcceptanceInstrumentContentRegistryNotFoundError", "LegalClientMatterAcceptanceInstrumentContentRegistryPersistedRecordInvalidError", "LegalClientMatterAcceptanceInstrumentContentRegistryPersistenceUnavailableError", "LegalClientMatterAcceptanceInstrumentContentRegistryRetryRequiredError", "LegalClientMatterAcceptanceInstrumentContentRegistryTransactionRequiredError", "ensure_indexes", "persist_content", "read_content"]

# ARTIFACT: legal_client_matter_acceptance_instrument_content_registry.py
# VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT-REGISTRY
# AUTHORITY BOUNDARY: dedicated immutable metadata and raw-byte persistence only
# TENANT POSTURE: every operational read/write is exact-tenant scoped
# FAIL-CLOSED POSTURE: transaction, corruption, divergence, race and outage reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
