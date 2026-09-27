"""WILSY OS durable client-matter conflict-disposition registry.

TITLE: WILSY OS Legal Client Matter Conflict Disposition Registry
VERSION: v1.0.0-L9C3-CONFLICT-DISPOSITION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and read immutable, explicit conflict-disposition evidence
         with exact tenant-scoped replay identities, strict domain hydration,
         bounded history and caller-owned Mongo transaction semantics. This
         registry records history only; it never resolves currentness.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_conflict_disposition_registry.py
COLLABORATION / OWNERSHIP: L9B2 owns the immutable disposition value and
                            fingerprint; L9C3 owns only append-only durability
                            and tenant-scoped history reads. A later
                            currentness composer owns effective-time selection;
                            Engagement, Representation, Court and finance remain
                            separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9C3-CONFLICT-DISPOSITION-REGISTRY establishes the canonical
           tenant-scoped collection, four immutable replay identities,
           review-lineage uniqueness, strict reconstruction, bounded history,
           majority+journal durability and caller-owned transaction semantics.
           It creates no current pointer, currentness result, IAM authority,
           Engagement, Representation, Court or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only the published opaque disposition fields and
                             SHA3-512 fingerprint are stored. No raw subject
                             narrative, credentials, bearer tokens or PII is
                             introduced by this registry.
TENANT BOUNDARY: Every operational query and replay identity starts with the
                 exact tenant_id; there is no global lookup or cross-tenant
                 existence oracle.
AUTHORITY BOUNDARY: Immutable disposition evidence persistence and history
                    reads only. Screening/review evidence is not reinterpreted,
                    and no currentness or authorization is inferred here.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: The caller supplies and owns an already-active Mongo
                      transaction. This module owns no session lifecycle,
                      transaction lifecycle or whole-transaction recovery.
FAIL-CLOSED DECLARATION: Missing transactions, malformed/corrupt rows,
                         divergent collisions, duplicate races, query overflow
                         and persistence failures reject without repair,
                         replacement or destructive mutation.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    DISPOSITION_FIELDS,
    LegalClientMatterConflictDisposition,
    LegalClientMatterConflictDispositionError,
)


VERSION: Final[str] = "v1.0.0-L9C3-CONFLICT-DISPOSITION-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_conflict_dispositions"
DISPOSITION_ID_INDEX_NAME: Final[str] = (
    "legal_client_matter_conflict_disposition_tenant_id_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_conflict_disposition_tenant_fingerprint_unique"
)
IDEMPOTENCY_INDEX_NAME: Final[str] = (
    "legal_client_matter_conflict_disposition_tenant_idempotency_unique"
)
REVIEW_LINEAGE_INDEX_NAME: Final[str] = (
    "legal_client_matter_conflict_disposition_review_lineage_unique"
)
HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_conflict_disposition_matter_history"
)
MATTER_FINGERPRINT_HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_conflict_disposition_matter_fingerprint_history"
)
CLIENT_PARTY_HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_conflict_disposition_client_party_history"
)
SUBJECT_HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_conflict_disposition_subject_history"
)
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientMatterConflictDispositionRegistryError(RuntimeError):
    """Base non-sensitive, fail-closed registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterConflictDispositionRegistryInputError(
    LegalClientMatterConflictDispositionRegistryError
):
    """Input or collection-interface contract failed."""


class LegalClientMatterConflictDispositionRegistryTransactionRequiredError(
    LegalClientMatterConflictDispositionRegistryError
):
    """Caller did not supply an active transaction."""


class LegalClientMatterConflictDispositionRegistryNotFoundError(
    LegalClientMatterConflictDispositionRegistryError
):
    """Exact tenant-scoped disposition identity is absent."""


class LegalClientMatterConflictDispositionRegistryConflictError(
    LegalClientMatterConflictDispositionRegistryError
):
    """An immutable replay identity collides with divergent evidence."""


class LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError(
    LegalClientMatterConflictDispositionRegistryError
):
    """Durable data failed strict schema, domain or scope reconstruction."""


class LegalClientMatterConflictDispositionRegistryRetryRequiredError(
    LegalClientMatterConflictDispositionRegistryError
):
    """A duplicate or transient race requires a fresh caller transaction."""


class LegalClientMatterConflictDispositionRegistryPersistenceUnavailableError(
    LegalClientMatterConflictDispositionRegistryError
):
    """Mongo persistence failed without a safe replay classification."""


def _fail(
    error_type: type[LegalClientMatterConflictDispositionRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _fail(
            LegalClientMatterConflictDispositionRegistryRetryRequiredError,
            "L9C3_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    _fail(
        LegalClientMatterConflictDispositionRegistryPersistenceUnavailableError,
        "L9C3_PERSISTENCE_UNAVAILABLE",
        error,
    )


def _target(collection: Any | None) -> Any:
    """Resolve the explicit or canonical collection with durable concerns."""
    if collection is not None:
        try:
            return collection.with_options(
                write_concern=WRITE_CONCERN,
                read_concern=READ_CONCERN,
                codec_options=CodecOptions(tz_aware=True),
            )
        except AttributeError:
            return collection
    try:
        from tools.eos.kernel.db import get_database

        database = get_database()
        if database is None:
            raise RuntimeError("database unavailable")
        return database.get_collection(
            COLLECTION,
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(tz_aware=True),
        )
    except Exception as error:
        _fail(
            LegalClientMatterConflictDispositionRegistryPersistenceUnavailableError,
            "L9C3_PERSISTENCE_UNAVAILABLE",
            error,
        )


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller transaction without starting one."""
    if session is None:
        _fail(
            LegalClientMatterConflictDispositionRegistryTransactionRequiredError,
            "L9C3_ACTIVE_TRANSACTION_REQUIRED",
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            LegalClientMatterConflictDispositionRegistryTransactionRequiredError,
            "L9C3_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _fail(
            LegalClientMatterConflictDispositionRegistryTransactionRequiredError,
            "L9C3_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _identity(name: str, value: object) -> str:
    """Validate an opaque lookup value without coercion or value leakage."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientMatterConflictDispositionRegistryInputError,
            f"L9C3_{name.upper()}_INVALID",
        )
    return value


def _bounded_limit(limit: object) -> int:
    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or not 0 < limit <= MAX_HISTORY_READS
    ):
        _fail(
            LegalClientMatterConflictDispositionRegistryInputError,
            "L9C3_LIMIT_INVALID",
        )
    return limit


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    raw = dict(document)
    raw.pop("_id", None)
    return raw


def _hydrate(
    document: Mapping[str, object],
) -> LegalClientMatterConflictDisposition:
    """Reconstruct only the exact published domain schema."""
    raw = _canonical(document)
    if set(raw) != set(DISPOSITION_FIELDS):
        _fail(
            LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError,
            "L9C3_PERSISTED_RECORD_INVALID",
        )
    try:
        value = LegalClientMatterConflictDisposition.from_dict(
            cast(Mapping[str, object], raw)
        )
    except (TypeError, ValueError, LegalClientMatterConflictDispositionError) as error:
        _fail(
            LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError,
            "L9C3_PERSISTED_RECORD_INVALID",
            error,
        )
    if value.to_dict() != raw:
        _fail(
            LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError,
            "L9C3_PERSISTED_RECORD_INVALID",
        )
    return value


def _document(
    value: LegalClientMatterConflictDisposition,
) -> dict[str, object]:
    """Canonicalize a published domain instance before persistence."""
    if type(value) is not LegalClientMatterConflictDisposition:
        _fail(
            LegalClientMatterConflictDispositionRegistryInputError,
            "L9C3_DISPOSITION_REQUIRED",
        )
    document = value.to_dict()
    try:
        checked = LegalClientMatterConflictDisposition.from_dict(
            cast(Mapping[str, object], document)
        )
    except (TypeError, ValueError, LegalClientMatterConflictDispositionError) as error:
        _fail(
            LegalClientMatterConflictDispositionRegistryInputError,
            "L9C3_DISPOSITION_INVALID",
            error,
        )
    if checked.to_dict() != document:
        _fail(
            LegalClientMatterConflictDispositionRegistryInputError,
            "L9C3_DISPOSITION_INVALID",
        )
    return document


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int,
) -> list[Mapping[str, object]]:
    """Read bounded rows with exact caller-session propagation."""
    try:
        cursor = _target(collection).find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort(
                [
                    ("effective_from", ASCENDING),
                    ("occurred_at", ASCENDING),
                    ("fingerprint", ASCENDING),
                    ("disposition_id", ASCENDING),
                ]
            )
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientMatterConflictDispositionRegistryInputError,
            "L9C3_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _one(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
) -> Mapping[str, object] | None:
    rows = _rows(collection, query, session=session, limit=2)
    if len(rows) > 1:
        _fail(
            LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError,
            "L9C3_DUPLICATE_IDENTITY",
        )
    return rows[0] if rows else None


def ensure_indexes(collection: Any | None = None) -> None:
    """Create tenant/replay/history indexes; no expiry or currentness index."""
    indexes = (
        (
            [("tenant_id", ASCENDING), ("disposition_id", ASCENDING)],
            True,
            DISPOSITION_ID_INDEX_NAME,
        ),
        (
            [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
            True,
            FINGERPRINT_INDEX_NAME,
        ),
        (
            [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
            True,
            IDEMPOTENCY_INDEX_NAME,
        ),
        (
            [
                ("tenant_id", ASCENDING),
                ("conflict_review_id", ASCENDING),
                ("conflict_review_fingerprint", ASCENDING),
            ],
            True,
            REVIEW_LINEAGE_INDEX_NAME,
        ),
        (
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("client_party_id", ASCENDING),
                ("effective_from", ASCENDING),
                ("occurred_at", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            False,
            HISTORY_INDEX_NAME,
        ),
        (
            [
                ("tenant_id", ASCENDING),
                ("matter_fingerprint", ASCENDING),
                ("effective_from", ASCENDING),
                ("occurred_at", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            False,
            MATTER_FINGERPRINT_HISTORY_INDEX_NAME,
        ),
        (
            [
                ("tenant_id", ASCENDING),
                ("client_party_id", ASCENDING),
                ("effective_from", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            False,
            CLIENT_PARTY_HISTORY_INDEX_NAME,
        ),
        (
            [
                ("tenant_id", ASCENDING),
                ("subject_identity_fingerprint", ASCENDING),
                ("effective_from", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            False,
            SUBJECT_HISTORY_INDEX_NAME,
        ),
    )
    try:
        target = _target(collection)
        for keys, unique, name in indexes:
            target.create_index(keys, unique=unique, name=name)
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientMatterConflictDispositionRegistryInputError,
            "L9C3_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _collision_queries(
    value: LegalClientMatterConflictDisposition,
) -> tuple[tuple[dict[str, object], str], ...]:
    return (
        (
            {"tenant_id": value.tenant_id, "disposition_id": value.disposition_id},
            "DISPOSITION_ID",
        ),
        (
            {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
            "FINGERPRINT",
        ),
        (
            {"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key},
            "IDEMPOTENCY_KEY",
        ),
        (
            {
                "tenant_id": value.tenant_id,
                "conflict_review_id": value.conflict_review_id,
                "conflict_review_fingerprint": value.conflict_review_fingerprint,
            },
            "REVIEW_LINEAGE",
        ),
    )


def persist_disposition(
    value: LegalClientMatterConflictDisposition,
    disposition_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterConflictDisposition:
    """Append one disposition or return an exact immutable replay.

    The caller owns transaction lifecycle. All four tenant-scoped replay
    identities must either resolve to the identical complete payload or be
    absent. Any divergent collision fails closed; duplicate races signal that
    the caller must restart its whole transaction.
    """
    tx = _active_transaction(session)
    document = _document(value)
    target = _target(disposition_collection)
    for query, label in _collision_queries(value):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(
            LegalClientMatterConflictDispositionRegistryConflictError,
            f"L9C3_{label}_COLLISION",
        )
    try:
        target.insert_one(dict(document), session=tx)
    except DuplicateKeyError as error:
        _fail(
            LegalClientMatterConflictDispositionRegistryRetryRequiredError,
            "L9C3_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    except PyMongoError as error:
        _raise_mongo(error)
    persisted = _one(
        target,
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        session=tx,
    )
    if persisted is None:
        _fail(
            LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError,
            "L9C3_POST_WRITE_RECONCILIATION_FAILED",
        )
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(
            LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError,
            "L9C3_POST_WRITE_RECONCILIATION_FAILED",
        )
    return result


def get_disposition(
    tenant_id: str,
    disposition_id: str,
    disposition_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterConflictDisposition:
    """Read one exact disposition under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(disposition_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "disposition_id": _identity("disposition_id", disposition_id),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterConflictDispositionRegistryNotFoundError,
            "L9C3_DISPOSITION_NOT_FOUND",
        )
    return _hydrate(row)


def get_disposition_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    disposition_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterConflictDisposition:
    """Read one exact fingerprint under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(disposition_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "fingerprint": _identity("fingerprint", fingerprint),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterConflictDispositionRegistryNotFoundError,
            "L9C3_DISPOSITION_NOT_FOUND",
        )
    return _hydrate(row)


def _history(
    query: Mapping[str, object],
    tenant_id: str,
    disposition_collection: Any | None,
    *,
    session: Any,
    limit: int,
    correlation: tuple[tuple[str, object], ...],
) -> tuple[LegalClientMatterConflictDisposition, ...]:
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    tenant = _identity("tenant_id", tenant_id)
    scoped = {"tenant_id": tenant, **dict(query)}
    rows = _rows(
        _target(disposition_collection),
        scoped,
        session=tx,
        limit=bounded + 1,
    )
    if len(rows) > bounded:
        _fail(
            LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError,
            "L9C3_READ_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    expected = (("tenant_id", tenant),) + correlation
    if any(
        any(getattr(value, field) != expected_value for field, expected_value in expected)
        for value in values
    ):
        _fail(
            LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError,
            "L9C3_HISTORY_SCOPE_INVALID",
        )
    return values


def list_dispositions_for_matter(
    tenant_id: str,
    case_matter_id: str,
    client_party_id: str,
    disposition_collection: Any | None = None,
    *,
    session: Any = None,
    limit: int = MAX_HISTORY_READS,
) -> tuple[LegalClientMatterConflictDisposition, ...]:
    """Return bounded immutable history for one tenant/matter/client scope.

    Traversal order is deterministic only; this method never chooses a current
    disposition or interprets effective time.
    """
    matter = _identity("case_matter_id", case_matter_id)
    party = _identity("client_party_id", client_party_id)
    return _history(
        {"case_matter_id": matter, "client_party_id": party},
        tenant_id,
        disposition_collection,
        session=session,
        limit=limit,
        correlation=(("case_matter_id", matter), ("client_party_id", party)),
    )


def list_dispositions_for_context(
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    disposition_collection: Any | None = None,
    *,
    session: Any = None,
    limit: int = MAX_HISTORY_READS,
) -> tuple[LegalClientMatterConflictDisposition, ...]:
    """Return bounded history for the exact future-currentness context.

    All five dimensions are exact tenant-scoped filters. Effective-time
    precedence and ambiguity remain outside this registry.
    """
    values = (
        ("case_matter_id", _identity("case_matter_id", case_matter_id)),
        ("matter_fingerprint", _identity("matter_fingerprint", matter_fingerprint)),
        ("client_party_id", _identity("client_party_id", client_party_id)),
        (
            "subject_identity_fingerprint",
            _identity("subject_identity_fingerprint", subject_identity_fingerprint),
        ),
    )
    return _history(
        dict(values),
        tenant_id,
        disposition_collection,
        session=session,
        limit=limit,
        correlation=values,
    )


class LegalClientMatterConflictDispositionRegistry:
    """Static namespace for immutable disposition persistence and reads only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_disposition = staticmethod(persist_disposition)
    get_disposition = staticmethod(get_disposition)
    get_disposition_by_fingerprint = staticmethod(get_disposition_by_fingerprint)
    list_dispositions_for_matter = staticmethod(list_dispositions_for_matter)
    list_dispositions_for_context = staticmethod(list_dispositions_for_context)


__all__ = [
    "CLIENT_PARTY_HISTORY_INDEX_NAME",
    "COLLECTION",
    "DISPOSITION_ID_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME",
    "IDEMPOTENCY_INDEX_NAME",
    "MATTER_FINGERPRINT_HISTORY_INDEX_NAME",
    "MAX_HISTORY_READS",
    "READ_CONCERN",
    "REVIEW_LINEAGE_INDEX_NAME",
    "SUBJECT_HISTORY_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientMatterConflictDispositionRegistry",
    "LegalClientMatterConflictDispositionRegistryConflictError",
    "LegalClientMatterConflictDispositionRegistryError",
    "LegalClientMatterConflictDispositionRegistryInputError",
    "LegalClientMatterConflictDispositionRegistryNotFoundError",
    "LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError",
    "LegalClientMatterConflictDispositionRegistryPersistenceUnavailableError",
    "LegalClientMatterConflictDispositionRegistryRetryRequiredError",
    "LegalClientMatterConflictDispositionRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_disposition",
    "get_disposition_by_fingerprint",
    "list_dispositions_for_context",
    "list_dispositions_for_matter",
    "persist_disposition",
]


# ARTIFACT: legal_client_matter_conflict_disposition_registry.py
# VERSION: v1.0.0-L9C3-CONFLICT-DISPOSITION-REGISTRY
# AUTHORITY BOUNDARY: immutable conflict-disposition evidence persistence/read only
# TENANT POSTURE: every replay, identity read and history query is tenant-scoped
# FAIL-CLOSED POSTURE: active transaction, strict hydration, collision, race and persistence failures reject; no currentness state is stored
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
