"""WILSY OS durable legal-client acceptance-context registry.

TITLE: Legal Client Acceptance Context Registry
VERSION: v1.0.0-L9A4-P2C2-CLIENT-ACCEPTANCE-CONTEXT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable server-composed LegalClientAcceptanceContext
         evidence with exact tenant isolation, deterministic replay, expiry-
         aware reads and caller-owned Mongo transaction semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_acceptance_context_registry.py
COLLABORATION / OWNERSHIP: P2C1 owns the immutable context value; P2C2 owns
                            only append-only durability and exact tenant-
                            scoped reads. A later P2C3 composer owns issuance.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2C2-CLIENT-ACCEPTANCE-CONTEXT-REGISTRY establishes
           the legal_client_acceptance_contexts collection, tenant-scoped
           context/fingerprint/replay uniqueness, strict hydration, exact
           replay/collision handling, valid-time reads and bounded actor,
           matter and party queries. No TTL, mutation, acceptance, IAM,
           engagement, representation, Court or financial authority exists.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores only the exact P2C1 serialized evidence
                             and Mongo _id. The raw content locator remains
                             server-only and is never projected by this module.
TENANT BOUNDARY: Every operational identity, index and read begins with the
                 exact tenant_id; cross-tenant fallback is impossible.
AUTHORITY BOUNDARY: Immutable context evidence persistence/read only. A
                    time-valid context is not proof that its dependencies are
                    still current and does not record ClientAcceptance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: The caller supplies and owns an active Mongo session;
                      this registry never starts, commits, aborts or retries a
                      transaction.
FAIL-CLOSED DECLARATION: Missing transaction, malformed rows, divergent
                         identity, duplicate races, overflow, cross-scope
                         queries and persistence failures reject.
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

from tools.eos.legal_operations.domain.legal_client_acceptance_context import (
    CONTEXT_FIELDS,
    LegalClientAcceptanceContext,
    LegalClientAcceptanceContextError,
)


VERSION: Final[str] = "v1.0.0-L9A4-P2C2-CLIENT-ACCEPTANCE-CONTEXT-REGISTRY"
COLLECTION: Final[str] = "legal_client_acceptance_contexts"
CONTEXT_ID_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_context_tenant_context_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_context_tenant_fingerprint_unique"
)
REPLAY_KEY_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_context_tenant_replay_unique"
)
ACTOR_ISSUED_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_context_tenant_actor_issued"
)
MATTER_ISSUED_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_context_tenant_matter_issued"
)
MATTER_PARTY_ISSUED_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_context_tenant_matter_party_issued"
)
EXPIRES_INDEX_NAME: Final[str] = "legal_client_acceptance_context_tenant_expires"
ACTOR_EXPIRES_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_context_tenant_actor_expires"
)
MAX_CONTEXT_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")
UTC = timezone.utc


class LegalClientAcceptanceContextRegistryError(RuntimeError):
    """Base non-sensitive, fail-closed registry error with a stable code."""

    default_code = "L9A4_P2C2_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Expose only a bounded error code; never include context data."""
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalClientAcceptanceContextRegistryInputError(
    LegalClientAcceptanceContextRegistryError
):
    """Input or collection-interface validation failed."""

    default_code = "L9A4_P2C2_INPUT_INVALID"


class LegalClientAcceptanceContextRegistryTransactionRequiredError(
    LegalClientAcceptanceContextRegistryError
):
    """An active caller-owned transaction/session was not supplied."""

    default_code = "L9A4_P2C2_ACTIVE_TRANSACTION_REQUIRED"


class LegalClientAcceptanceContextRegistryNotFoundError(
    LegalClientAcceptanceContextRegistryError
):
    """No exact tenant-scoped context identity exists."""

    default_code = "L9A4_P2C2_CONTEXT_NOT_FOUND"


class LegalClientAcceptanceContextRegistryConflictError(
    LegalClientAcceptanceContextRegistryError
):
    """An immutable identity is already bound to divergent evidence."""

    default_code = "L9A4_P2C2_CONTEXT_CONFLICT"


class LegalClientAcceptanceContextRegistryPersistedRecordInvalidError(
    LegalClientAcceptanceContextRegistryError
):
    """Durable context data is corrupt, duplicated or schema-divergent."""

    default_code = "L9A4_P2C2_PERSISTED_RECORD_INVALID"


class LegalClientAcceptanceContextRegistryRetryRequiredError(
    LegalClientAcceptanceContextRegistryError
):
    """The caller must abort and restart the complete transaction."""

    default_code = "L9A4_P2C2_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalClientAcceptanceContextRegistryPersistenceUnavailableError(
    LegalClientAcceptanceContextRegistryError
):
    """Mongo persistence failed without a safe replay classification."""

    default_code = "L9A4_P2C2_PERSISTENCE_UNAVAILABLE"


def _fail(
    error_type: type[LegalClientAcceptanceContextRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded registry error while retaining a technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    """Translate Mongo failures without owning transaction recovery."""
    if error.has_error_label("TransientTransactionError"):
        _fail(LegalClientAcceptanceContextRegistryRetryRequiredError, cause=error)
    _fail(LegalClientAcceptanceContextRegistryPersistenceUnavailableError, cause=error)


def _target(collection: Any) -> Any:
    """Apply canonical majority durability and UTC-aware BSON options."""
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(tz_aware=True, tzinfo=UTC),
        )
    except AttributeError:
        return collection


def _collection(collection: Any) -> Any:
    """Require a collection-like target without creating shared state."""
    if collection is None:
        _fail(LegalClientAcceptanceContextRegistryInputError, "L9A4_P2C2_COLLECTION_REQUIRED")
    return _target(collection)


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller-owned transaction."""
    if session is None:
        _fail(LegalClientAcceptanceContextRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail(LegalClientAcceptanceContextRegistryTransactionRequiredError)
    return session


def _text(name: str, value: object) -> str:
    """Require one non-empty, non-coerced exact query identity."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientAcceptanceContextRegistryInputError,
            f"L9A4_P2C2_{name.upper()}_INVALID",
        )
    return value


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and canonicalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(
                LegalClientAcceptanceContextRegistryInputError,
                f"L9A4_P2C2_{name.upper()}_INVALID",
                error,
            )
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(
            LegalClientAcceptanceContextRegistryInputError,
            f"L9A4_P2C2_{name.upper()}_INVALID",
        )
    return parsed.astimezone(UTC).replace(microsecond=parsed.microsecond)


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int,
) -> list[Mapping[str, Any]]:
    """Read bounded rows with the exact caller session on every read."""
    target = _collection(collection)
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort([("issued_at", DESCENDING), ("fingerprint", ASCENDING)])
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientAcceptanceContextRegistryInputError,
            "L9A4_P2C2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _one(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
) -> Mapping[str, Any] | None:
    """Read one identity while preserving caller-session context."""
    target = _collection(collection)
    try:
        finder = getattr(target, "find_one", None)
        if callable(finder):
            row = finder(dict(query), session=session)
            return cast(Mapping[str, Any], row) if row is not None else None
        rows = _rows(target, query, session=session, limit=2)
        return rows[0] if rows else None
    except PyMongoError as error:
        _raise_mongo(error)


def _hydrate(document: Mapping[str, Any]) -> LegalClientAcceptanceContext:
    """Hydrate one exact P2C1 payload and reject every schema drift."""
    if not isinstance(document, Mapping):
        _fail(LegalClientAcceptanceContextRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != set(CONTEXT_FIELDS):
        _fail(
            LegalClientAcceptanceContextRegistryPersistedRecordInvalidError,
            "L9A4_P2C2_RECORD_SCHEMA_INVALID",
        )
    try:
        value = LegalClientAcceptanceContext.from_dict(cast(Mapping[str, object], raw))
    except (TypeError, ValueError, LegalClientAcceptanceContextError) as error:
        _fail(
            LegalClientAcceptanceContextRegistryPersistedRecordInvalidError,
            "L9A4_P2C2_CONTEXT_PAYLOAD_INVALID",
            error,
        )
    if value.to_dict() != raw:
        _fail(
            LegalClientAcceptanceContextRegistryPersistedRecordInvalidError,
            "L9A4_P2C2_RECORD_CORRELATION_INVALID",
        )
    return value


def ensure_indexes(collection: Any) -> None:
    """Create exact identity/read indexes without a TTL lifecycle.

    Index creation is administrative and intentionally outside operational
    transactions. Contexts remain durable evidence after expiry.
    """
    target = _collection(collection)
    indexes = (
        ([ ("tenant_id", ASCENDING), ("acceptance_context_id", ASCENDING) ], True, CONTEXT_ID_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("fingerprint", ASCENDING) ], True, FINGERPRINT_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("replay_key", ASCENDING) ], True, REPLAY_KEY_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("actor_principal_id", ASCENDING), ("issued_at", DESCENDING) ], False, ACTOR_ISSUED_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("issued_at", DESCENDING) ], False, MATTER_ISSUED_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("party_id", ASCENDING), ("issued_at", DESCENDING) ], False, MATTER_PARTY_ISSUED_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("expires_at", ASCENDING) ], False, EXPIRES_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("actor_principal_id", ASCENDING), ("expires_at", ASCENDING) ], False, ACTOR_EXPIRES_INDEX_NAME),
    )
    try:
        for keys, unique, name in indexes:
            target.create_index(keys, unique=unique, name=name)
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientAcceptanceContextRegistryInputError,
            "L9A4_P2C2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _collision_queries(value: LegalClientAcceptanceContext) -> tuple[dict[str, object], ...]:
    """Return all tenant-scoped immutable identities protected by indexes."""
    return (
        {"tenant_id": value.tenant_id, "acceptance_context_id": value.acceptance_context_id},
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        {"tenant_id": value.tenant_id, "replay_key": value.replay_key},
    )


def persist_context(
    value: LegalClientAcceptanceContext,
    context_collection: Any,
    *,
    session: Any,
) -> LegalClientAcceptanceContext:
    """Append one context or return its exact replay.

    The method performs no transaction lifecycle work. Same tenant-scoped
    identity plus identical serialized evidence is a replay; any divergent
    identity fails closed. Mongo duplicate races require the caller to abort
    and restart its complete transaction. No plaintext, client projection or
    dependency-currentness decision is returned.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientAcceptanceContext:
        _fail(
            LegalClientAcceptanceContextRegistryInputError,
            "L9A4_P2C2_CONTEXT_REQUIRED",
        )
    target = _collection(context_collection)
    document = value.to_dict()
    for index, query in enumerate(_collision_queries(value)):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        labels = ("CONTEXT_ID", "FINGERPRINT", "REPLAY_KEY")
        _fail(
            LegalClientAcceptanceContextRegistryConflictError,
            f"L9A4_P2C2_{labels[index]}_COLLISION",
        )
    try:
        target.insert_one(dict(document), session=tx)
    except DuplicateKeyError as error:
        _fail(
            LegalClientAcceptanceContextRegistryRetryRequiredError,
            "L9A4_P2C2_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    except PyMongoError as error:
        _raise_mongo(error)
    persisted = _one(
        target,
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        session=tx,
    )
    if persisted is None or _hydrate(persisted).to_dict() != document:
        _fail(
            LegalClientAcceptanceContextRegistryPersistedRecordInvalidError,
            "L9A4_P2C2_POST_WRITE_RECONCILIATION_FAILED",
        )
    return _hydrate(persisted)


def get_context(
    tenant_id: str,
    acceptance_context_id: str,
    context_collection: Any,
    *,
    session: Any,
) -> LegalClientAcceptanceContext:
    """Read one exact durable context under exact tenant scope."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    identity = _text("acceptance_context_id", acceptance_context_id)
    rows = _rows(
        context_collection,
        {"tenant_id": tenant, "acceptance_context_id": identity},
        session=tx,
        limit=2,
    )
    if not rows:
        _fail(LegalClientAcceptanceContextRegistryNotFoundError)
    if len(rows) > 1:
        _fail(
            LegalClientAcceptanceContextRegistryPersistedRecordInvalidError,
            "L9A4_P2C2_DUPLICATE_CONTEXT_ID",
        )
    return _hydrate(rows[0])


def get_valid_context(
    tenant_id: str,
    acceptance_context_id: str,
    at: datetime,
    context_collection: Any,
    *,
    session: Any,
) -> LegalClientAcceptanceContext | None:
    """Return a context only when ``issued_at <= at < expires_at``.

    This is temporal validity only. It does not establish current matter,
    visibility, capacity, lifecycle, approval, content or IAM validity.
    Expired contexts remain durable and can still be read with ``get_context``.
    """
    instant = _timestamp("at", at)
    try:
        value = get_context(
            tenant_id,
            acceptance_context_id,
            context_collection,
            session=session,
        )
    except LegalClientAcceptanceContextRegistryNotFoundError:
        return None
    return value if value.issued_at <= instant < value.expires_at else None


def _bounded_limit(limit: object) -> int:
    """Require a positive bounded read limit and reject overflow."""
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 < limit <= MAX_CONTEXT_READS:
        _fail(
            LegalClientAcceptanceContextRegistryInputError,
            "L9A4_P2C2_LIMIT_INVALID",
        )
    return limit


def _list_contexts(
    query: Mapping[str, object],
    context_collection: Any,
    *,
    session: Any,
    limit: int,
) -> tuple[LegalClientAcceptanceContext, ...]:
    """Hydrate a bounded tenant-scoped context history."""
    tx = _active_transaction(session)
    rows = _rows(
        context_collection,
        query,
        session=tx,
        limit=_bounded_limit(limit) + 1,
    )
    if len(rows) > limit:
        _fail(
            LegalClientAcceptanceContextRegistryPersistedRecordInvalidError,
            "L9A4_P2C2_CONTEXT_READ_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    tenant = cast(str, query["tenant_id"])
    if any(value.tenant_id != tenant for value in values):
        _fail(
            LegalClientAcceptanceContextRegistryPersistedRecordInvalidError,
            "L9A4_P2C2_TENANT_CORRELATION_INVALID",
        )
    return values


def list_contexts_for_actor(
    tenant_id: str,
    actor_principal_id: str,
    context_collection: Any,
    *,
    session: Any,
    limit: int = MAX_CONTEXT_READS,
) -> tuple[LegalClientAcceptanceContext, ...]:
    """List bounded contexts for one actor within one exact tenant."""
    return _list_contexts(
        {"tenant_id": _text("tenant_id", tenant_id), "actor_principal_id": _text("actor_principal_id", actor_principal_id)},
        context_collection,
        session=session,
        limit=limit,
    )


def list_contexts_for_matter(
    tenant_id: str,
    case_matter_id: str,
    context_collection: Any,
    *,
    session: Any,
    limit: int = MAX_CONTEXT_READS,
) -> tuple[LegalClientAcceptanceContext, ...]:
    """List bounded contexts for one matter within one exact tenant."""
    return _list_contexts(
        {"tenant_id": _text("tenant_id", tenant_id), "case_matter_id": _text("case_matter_id", case_matter_id)},
        context_collection,
        session=session,
        limit=limit,
    )


def list_contexts_for_party(
    tenant_id: str,
    case_matter_id: str,
    party_id: str,
    context_collection: Any,
    *,
    session: Any,
    limit: int = MAX_CONTEXT_READS,
) -> tuple[LegalClientAcceptanceContext, ...]:
    """List bounded contexts for one party within one matter and tenant."""
    return _list_contexts(
        {
            "tenant_id": _text("tenant_id", tenant_id),
            "case_matter_id": _text("case_matter_id", case_matter_id),
            "party_id": _text("party_id", party_id),
        },
        context_collection,
        session=session,
        limit=limit,
    )


class LegalClientAcceptanceContextRegistry:
    """Static namespace for immutable context persistence and reads only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_context = staticmethod(persist_context)
    get_context = staticmethod(get_context)
    get_valid_context = staticmethod(get_valid_context)
    list_contexts_for_actor = staticmethod(list_contexts_for_actor)
    list_contexts_for_matter = staticmethod(list_contexts_for_matter)
    list_contexts_for_party = staticmethod(list_contexts_for_party)


__all__ = [
    "ACTOR_EXPIRES_INDEX_NAME",
    "ACTOR_ISSUED_INDEX_NAME",
    "COLLECTION",
    "CONTEXT_ID_INDEX_NAME",
    "EXPIRES_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "MATTER_ISSUED_INDEX_NAME",
    "MATTER_PARTY_ISSUED_INDEX_NAME",
    "MAX_CONTEXT_READS",
    "READ_CONCERN",
    "REPLAY_KEY_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientAcceptanceContextRegistry",
    "LegalClientAcceptanceContextRegistryConflictError",
    "LegalClientAcceptanceContextRegistryError",
    "LegalClientAcceptanceContextRegistryInputError",
    "LegalClientAcceptanceContextRegistryNotFoundError",
    "LegalClientAcceptanceContextRegistryPersistedRecordInvalidError",
    "LegalClientAcceptanceContextRegistryPersistenceUnavailableError",
    "LegalClientAcceptanceContextRegistryRetryRequiredError",
    "LegalClientAcceptanceContextRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_context",
    "get_valid_context",
    "list_contexts_for_actor",
    "list_contexts_for_matter",
    "list_contexts_for_party",
    "persist_context",
]


# ARTIFACT: legal_client_acceptance_context_registry.py
# VERSION: v1.0.0-L9A4-P2C2-CLIENT-ACCEPTANCE-CONTEXT-REGISTRY
# AUTHORITY BOUNDARY: immutable acceptance-context evidence persistence/read only
# TENANT POSTURE: every operational identity/index/read begins with exact tenant_id
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/race/outage rejects; no TTL or mutable writes
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
