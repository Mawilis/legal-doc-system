"""Durable append-only lifecycle history for client mandate grants.

TITLE: WILSY OS Legal Client Matter Mandate Grant Lifecycle Registry
VERSION: v1.0.0-L9B8-CLIENT-MANDATE-GRANT-LIFECYCLE-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and read exact immutable REVOKED and SUPERSEDED lifecycle
         events for one client mandate grant. This registry preserves evidence
         only; it never checks formation existence, chooses currentness, or
         mutates grant, acknowledgment, mandate, Engagement, or authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_mandate_grant_lifecycle_registry.py
COLLABORATION / OWNERSHIP: LegalClientMatterMandateGrantLifecycle owns event
                            semantics and fingerprints; this registry owns only
                            append-only lifecycle durability and evidentiary
                            reads. Formation and future currentness composition
                            remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B8-CLIENT-MANDATE-GRANT-LIFECYCLE-REGISTRY establishes a
           dedicated history collection, tenant-scoped event/fingerprint/
           idempotency uniqueness, strict hydration, deterministic replay,
           caller-owned transactions, and chronology indexes. Equal-effective
           valid events are preserved for later fail-closed composition. No
           TTL, currentness, formation lookup or mutable summary is created.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded opaque identities, evidence references
                             and SHA3-512 fingerprints are persisted; no PII,
                             credentials, tokens or raw evidence bodies.
TENANT BOUNDARY: Every replay, read and history query begins with exact tenant;
                 there is no global event lookup or cross-tenant oracle.
AUTHORITY BOUNDARY: Immutable lifecycle evidence persistence/read only. The
                    registry does not answer whether a grant is current.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, release or execution;
                              Kennel EOS remains exclusive financial authority.
TRANSACTION BOUNDARY: Caller supplies and owns an active Mongo transaction;
                      this registry never opens, commits, aborts, retries or
                      reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing session, malformed rows, divergent replay,
                         duplicate identity, schema drift and persistence
                         failures reject without repair or destructive action.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LIFECYCLE_FIELDS,
    LegalClientMatterMandateGrantLifecycle,
    LegalClientMatterMandateGrantLifecycleError,
)


VERSION: Final[str] = "v1.0.0-L9B8-CLIENT-MANDATE-GRANT-LIFECYCLE-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_mandate_grant_lifecycle"
EVENT_ID_INDEX_NAME: Final[str] = "legal_client_matter_grant_lifecycle_tenant_event_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "legal_client_matter_grant_lifecycle_tenant_fingerprint_unique"
IDEMPOTENCY_INDEX_NAME: Final[str] = "legal_client_matter_grant_lifecycle_tenant_idempotency_unique"
HISTORY_INDEX_NAME: Final[str] = "legal_client_matter_grant_lifecycle_history"
EVENT_INDEX_NAME: Final[str] = "legal_client_matter_grant_lifecycle_event_history"
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientMatterMandateGrantLifecycleRegistryError(RuntimeError):
    """Base non-sensitive fail-closed lifecycle registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterMandateGrantLifecycleRegistryInputError(LegalClientMatterMandateGrantLifecycleRegistryError):
    """Malformed value, query, collection, or limit."""


class LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError(LegalClientMatterMandateGrantLifecycleRegistryError):
    """An active caller-owned transaction was not supplied."""


class LegalClientMatterMandateGrantLifecycleRegistryNotFoundError(LegalClientMatterMandateGrantLifecycleRegistryError):
    """The exact tenant-scoped event identity is absent."""


class LegalClientMatterMandateGrantLifecycleRegistryConflictError(LegalClientMatterMandateGrantLifecycleRegistryError):
    """An immutable event identity collides with divergent evidence."""


class LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError(LegalClientMatterMandateGrantLifecycleRegistryError):
    """Durable lifecycle data failed strict hydration or identity checks."""


class LegalClientMatterMandateGrantLifecycleRegistryRetryRequiredError(LegalClientMatterMandateGrantLifecycleRegistryError):
    """A duplicate race requires a caller-owned whole-transaction restart."""


class LegalClientMatterMandateGrantLifecycleRegistryPersistenceUnavailableError(LegalClientMatterMandateGrantLifecycleRegistryError):
    """Mongo persistence failed without a safe replay classification."""


def _fail(error_type: type[LegalClientMatterMandateGrantLifecycleRegistryError], code: str, cause: BaseException | None = None) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _fail(LegalClientMatterMandateGrantLifecycleRegistryRetryRequiredError, "L9B8_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistenceUnavailableError, "L9B8_PERSISTENCE_UNAVAILABLE", error)


def _target(collection: Any) -> Any:
    if collection is None:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryInputError, "L9B8_COLLECTION_REQUIRED")
    try:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN, codec_options=CodecOptions(tz_aware=True))
    except AttributeError:
        return collection


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError, "L9B8_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError, "L9B8_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(LegalClientMatterMandateGrantLifecycleRegistryInputError, f"L9B8_{name.upper()}_INVALID")
    return value


def _rows(collection: Any, query: Mapping[str, object], *, session: Any, limit: int) -> list[Mapping[str, Any]]:
    target = _target(collection)
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort([("effective_from", ASCENDING), ("occurred_at", ASCENDING), ("fingerprint", ASCENDING), ("lifecycle_event_id", ASCENDING)])
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryInputError, "L9B8_COLLECTION_INTERFACE_INVALID", error)


def _one(collection: Any, query: Mapping[str, object], *, session: Any) -> Mapping[str, Any] | None:
    rows = _rows(collection, query, session=session, limit=2)
    if len(rows) > 1:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError, "L9B8_DUPLICATE_IDENTITY")
    return rows[0] if rows else None


def _hydrate(document: Mapping[str, Any]) -> LegalClientMatterMandateGrantLifecycle:
    if not isinstance(document, Mapping):
        _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError, "L9B8_RECORD_INVALID")
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != set(LIFECYCLE_FIELDS):
        _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError, "L9B8_RECORD_SCHEMA_INVALID")
    try:
        value = LegalClientMatterMandateGrantLifecycle.from_dict(cast(Mapping[str, object], raw))
    except (TypeError, ValueError, LegalClientMatterMandateGrantLifecycleError) as error:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError, "L9B8_EVENT_PAYLOAD_INVALID", error)
    if value.to_dict() != raw:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError, "L9B8_RECORD_CORRELATION_INVALID")
    return value


def ensure_indexes(collection: Any) -> None:
    """Create exact lifecycle-history indexes without a TTL index."""
    target = _target(collection)
    indexes = (
        ([("tenant_id", ASCENDING), ("lifecycle_event_id", ASCENDING)], True, EVENT_ID_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("fingerprint", ASCENDING)], True, FINGERPRINT_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)], True, IDEMPOTENCY_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("client_grant_id", ASCENDING), ("client_grant_fingerprint", ASCENDING), ("effective_from", ASCENDING), ("occurred_at", ASCENDING), ("fingerprint", ASCENDING)], False, HISTORY_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("client_grant_id", ASCENDING), ("event", ASCENDING), ("effective_from", ASCENDING)], False, EVENT_INDEX_NAME),
    )
    try:
        for keys, unique, name in indexes:
            target.create_index(keys, unique=unique, name=name)
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryInputError, "L9B8_COLLECTION_INTERFACE_INVALID", error)


def _collision_queries(value: LegalClientMatterMandateGrantLifecycle) -> tuple[dict[str, object], ...]:
    return (
        {"tenant_id": value.tenant_id, "lifecycle_event_id": value.lifecycle_event_id},
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        {"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key},
    )


def persist_event(value: LegalClientMatterMandateGrantLifecycle, lifecycle_collection: Any, *, session: Any) -> LegalClientMatterMandateGrantLifecycle:
    """Append one exact lifecycle event or return its exact replay.

    Valid events with equal effective times are both retained. A later
    currentness composer, not this persistence registry, decides whether such
    history is ambiguous.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterMandateGrantLifecycle:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryInputError, "L9B8_EVENT_REQUIRED")
    target = _target(lifecycle_collection)
    document = value.to_dict()
    labels = ("EVENT_ID", "FINGERPRINT", "IDEMPOTENCY_KEY")
    for query, label in zip(_collision_queries(value), labels):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(LegalClientMatterMandateGrantLifecycleRegistryConflictError, f"L9B8_{label}_COLLISION")
    try:
        target.insert_one(dict(document), session=tx)
    except DuplicateKeyError as error:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryRetryRequiredError, "L9B8_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except PyMongoError as error:
        _raise_mongo(error)
    persisted = _one(target, {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}, session=tx)
    if persisted is None:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError, "L9B8_POST_WRITE_RECONCILIATION_FAILED")
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError, "L9B8_POST_WRITE_RECONCILIATION_FAILED")
    return result


def get_event(tenant_id: str, lifecycle_event_id: str, lifecycle_collection: Any, *, session: Any) -> LegalClientMatterMandateGrantLifecycle:
    """Read one exact lifecycle event under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(lifecycle_collection, {"tenant_id": _text("tenant_id", tenant_id), "lifecycle_event_id": _text("lifecycle_event_id", lifecycle_event_id)}, session=tx)
    if row is None:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryNotFoundError, "L9B8_EVENT_NOT_FOUND")
    return _hydrate(row)


def get_event_by_fingerprint(tenant_id: str, fingerprint: str, lifecycle_collection: Any, *, session: Any) -> LegalClientMatterMandateGrantLifecycle:
    """Read one exact fingerprint under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(lifecycle_collection, {"tenant_id": _text("tenant_id", tenant_id), "fingerprint": _text("fingerprint", fingerprint)}, session=tx)
    if row is None:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryNotFoundError, "L9B8_EVENT_NOT_FOUND")
    return _hydrate(row)


def _bounded_limit(limit: object) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 < limit <= MAX_HISTORY_READS:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryInputError, "L9B8_LIMIT_INVALID")
    return limit


def list_events_for_grant(tenant_id: str, client_grant_id: str, lifecycle_collection: Any, *, session: Any, limit: int = MAX_HISTORY_READS) -> tuple[LegalClientMatterMandateGrantLifecycle, ...]:
    """Return bounded immutable history without resolving currentness."""
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    rows = _rows(lifecycle_collection, {"tenant_id": _text("tenant_id", tenant_id), "client_grant_id": _text("client_grant_id", client_grant_id)}, session=tx, limit=bounded + 1)
    if len(rows) > bounded:
        _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError, "L9B8_READ_LIMIT_EXCEEDED")
    values = tuple(_hydrate(row) for row in rows)
    if any(value.tenant_id != tenant_id or value.client_grant_id != client_grant_id for value in values):
        _fail(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError, "L9B8_SCOPE_CORRELATION_INVALID")
    return values


class LegalClientMatterMandateGrantLifecycleRegistry:
    """Static namespace for lifecycle evidence persistence and history reads."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_event = staticmethod(persist_event)
    get_event = staticmethod(get_event)
    get_event_by_fingerprint = staticmethod(get_event_by_fingerprint)
    list_events_for_grant = staticmethod(list_events_for_grant)


__all__ = [
    "COLLECTION", "EVENT_ID_INDEX_NAME", "EVENT_INDEX_NAME", "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME", "IDEMPOTENCY_INDEX_NAME", "MAX_HISTORY_READS", "READ_CONCERN",
    "VERSION", "WRITE_CONCERN", "LegalClientMatterMandateGrantLifecycleRegistry",
    "LegalClientMatterMandateGrantLifecycleRegistryConflictError",
    "LegalClientMatterMandateGrantLifecycleRegistryError",
    "LegalClientMatterMandateGrantLifecycleRegistryInputError",
    "LegalClientMatterMandateGrantLifecycleRegistryNotFoundError",
    "LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError",
    "LegalClientMatterMandateGrantLifecycleRegistryPersistenceUnavailableError",
    "LegalClientMatterMandateGrantLifecycleRegistryRetryRequiredError",
    "LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError",
    "ensure_indexes", "get_event", "get_event_by_fingerprint", "list_events_for_grant", "persist_event",
]


# ARTIFACT: legal_client_matter_mandate_grant_lifecycle_registry.py
# VERSION: v1.0.0-L9B8-CLIENT-MANDATE-GRANT-LIFECYCLE-REGISTRY
# AUTHORITY BOUNDARY: immutable lifecycle evidence persistence/read only
# TENANT POSTURE: every event identity, replay and history query is tenant-scoped
# FAIL-CLOSED POSTURE: strict hydration, collision, duplicate and persistence rejection; no TTL/currentness
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
