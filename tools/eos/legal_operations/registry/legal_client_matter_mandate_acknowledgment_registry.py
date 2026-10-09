"""WILSY OS append-only firm mandate acknowledgment registry.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment Registry
VERSION: v1.0.0-L9B10-FIRM-MANDATE-ACKNOWLEDGMENT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and read immutable, exact-grant-bound firm acknowledgment
         decisions with tenant-scoped replay, strict hydration and deterministic
         history. This registry stores evidence only; it never resolves
         currentness or forms a mandate.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_mandate_acknowledgment_registry.py
COLLABORATION / OWNERSHIP: LegalClientMatterMandateAcknowledgment owns the
                            canonical value, decision vocabulary and fingerprint;
                            this registry owns append-only persistence and reads.
                            IAM, grant currentness, mandate, Engagement,
                            Representation, Court and finance remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B10-FIRM-MANDATE-ACKNOWLEDGMENT-REGISTRY establishes the
           dedicated tenant-scoped collection, three replay identities, exact
           grant-history indexes, strict reconstruction, caller-owned sessions,
           deterministic history and fail-closed collision handling. No TTL,
           currentness, lifecycle, mutable summary or downstream authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded opaque domain fields and SHA3-512
                             fingerprints are persisted; no PII, credentials,
                             bearer tokens or unrestricted evidence bodies.
TENANT BOUNDARY: Every identity, replay and history query includes the exact
                 tenant_id. There is no global acknowledgment lookup.
AUTHORITY BOUNDARY: Immutable historical acknowledgment evidence persistence
                    and reads only. The registry does not authorize actors,
                    read grant currentness, or select a current decision.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, release or execution;
                              Kennel EOS remains exclusive financial authority.
TRANSACTION BOUNDARY: The caller supplies and owns an active Mongo transaction;
                      this registry never begins, commits, aborts, retries or
                      owns a session lifecycle.
FAIL-CLOSED DECLARATION: Missing transactions, malformed rows, divergent
                         collisions, duplicate races, schema drift and
                         persistence failures reject without repair or deletion.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    ACKNOWLEDGMENT_FIELDS,
    LegalClientMatterMandateAcknowledgment,
    LegalClientMatterMandateAcknowledgmentError,
)


VERSION: Final[str] = "v1.0.0-L9B10-FIRM-MANDATE-ACKNOWLEDGMENT-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_mandate_acknowledgments"
ACKNOWLEDGMENT_ID_INDEX_NAME: Final[str] = (
    "legal_client_matter_mandate_acknowledgment_tenant_id_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_mandate_acknowledgment_tenant_fingerprint_unique"
)
IDEMPOTENCY_INDEX_NAME: Final[str] = (
    "legal_client_matter_mandate_acknowledgment_tenant_idempotency_unique"
)
HISTORY_INDEX_NAME: Final[str] = "legal_client_matter_mandate_acknowledgment_grant_history"
DECISION_INDEX_NAME: Final[str] = "legal_client_matter_mandate_acknowledgment_grant_decision"
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientMatterMandateAcknowledgmentRegistryError(RuntimeError):
    """Base non-sensitive, fail-closed persistence error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterMandateAcknowledgmentRegistryInputError(
    LegalClientMatterMandateAcknowledgmentRegistryError
):
    """Malformed value, query, limit or collection interface."""


class LegalClientMatterMandateAcknowledgmentRegistryTransactionRequiredError(
    LegalClientMatterMandateAcknowledgmentRegistryError
):
    """A caller-owned active transaction was not supplied."""


class LegalClientMatterMandateAcknowledgmentRegistryNotFoundError(
    LegalClientMatterMandateAcknowledgmentRegistryError
):
    """The exact tenant-scoped acknowledgment identity is absent."""


class LegalClientMatterMandateAcknowledgmentRegistryConflictError(
    LegalClientMatterMandateAcknowledgmentRegistryError
):
    """An immutable identity collides with divergent evidence."""


class LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError(
    LegalClientMatterMandateAcknowledgmentRegistryError
):
    """Durable data failed strict domain hydration or scope validation."""


class LegalClientMatterMandateAcknowledgmentRegistryRetryRequiredError(
    LegalClientMatterMandateAcknowledgmentRegistryError
):
    """A duplicate or transient race requires a fresh whole transaction."""


class LegalClientMatterMandateAcknowledgmentRegistryPersistenceUnavailableError(
    LegalClientMatterMandateAcknowledgmentRegistryError
):
    """Mongo persistence failed without a safe replay classification."""


def _fail(
    error_type: type[LegalClientMatterMandateAcknowledgmentRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise a stable code without exposing supplied evidence or identities."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    """Classify Mongo failures without owning transaction recovery."""
    if error.has_error_label("TransientTransactionError"):
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryRetryRequiredError,
            "L9B10_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    _fail(
        LegalClientMatterMandateAcknowledgmentRegistryPersistenceUnavailableError,
        "L9B10_PERSISTENCE_UNAVAILABLE",
        error,
    )


def _target(collection: Any | None) -> Any:
    """Resolve an explicit collection or the canonical EOS collection."""
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
            LegalClientMatterMandateAcknowledgmentRegistryPersistenceUnavailableError,
            "L9B10_PERSISTENCE_UNAVAILABLE",
            error,
        )


def _active_transaction(session: Any) -> Any:
    """Require an active caller transaction without starting or ending it."""
    if session is None:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryTransactionRequiredError,
            "L9B10_ACTIVE_TRANSACTION_REQUIRED",
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryTransactionRequiredError,
            "L9B10_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryTransactionRequiredError,
            "L9B10_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _identity(value: object, name: str) -> str:
    """Validate a bounded opaque lookup identity without coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryInputError,
            f"L9B10_{name.upper()}_INVALID",
        )
    return value


def _bounded_limit(limit: object) -> int:
    """Reject unbounded or non-integer history requests."""
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 < limit <= MAX_HISTORY_READS:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryInputError,
            "L9B10_LIMIT_INVALID",
        )
    return limit


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    """Remove only Mongo's generated identifier before strict hydration."""
    result = dict(document)
    result.pop("_id", None)
    return result


def _hydrate(document: Mapping[str, object]) -> LegalClientMatterMandateAcknowledgment:
    """Hydrate one exact domain value and reject schema or fingerprint drift."""
    payload = _canonical(document)
    if set(payload) != set(ACKNOWLEDGMENT_FIELDS):
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
            "L9B10_PERSISTED_RECORD_INVALID",
        )
    try:
        value = LegalClientMatterMandateAcknowledgment.from_dict(payload)
    except (TypeError, ValueError, LegalClientMatterMandateAcknowledgmentError) as error:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
            "L9B10_PERSISTED_RECORD_INVALID",
            error,
        )
    if value.to_dict() != payload:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
            "L9B10_PERSISTED_RECORD_INVALID",
        )
    return value


def _document(value: LegalClientMatterMandateAcknowledgment) -> dict[str, object]:
    """Serialize only the exact immutable domain fields."""
    if type(value) is not LegalClientMatterMandateAcknowledgment:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryInputError,
            "L9B10_ACKNOWLEDGMENT_REQUIRED",
        )
    return value.to_dict()


def _rows(
    target: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int | None = None,
) -> list[Mapping[str, object]]:
    """Read rows with exact caller-session propagation and deterministic order."""
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort(
                [
                    ("effective_from", ASCENDING),
                    ("occurred_at", ASCENDING),
                    ("fingerprint", ASCENDING),
                    ("acknowledgment_id", ASCENDING),
                ]
            )
        if limit is not None and hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryInputError,
            "L9B10_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _one(
    target: Any,
    query: Mapping[str, object],
    *,
    session: Any,
) -> Mapping[str, object] | None:
    """Read one identity and reject malformed duplicate durable state."""
    rows = _rows(target, query, session=session, limit=2)
    if len(rows) > 1:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
            "L9B10_DUPLICATE_IDENTITY",
        )
    return rows[0] if rows else None


def ensure_indexes(collection: Any | None = None) -> None:
    """Create exact replay/history indexes; no TTL or currentness index."""
    target = _target(collection)
    indexes = (
        (
            [("tenant_id", ASCENDING), ("acknowledgment_id", ASCENDING)],
            True,
            ACKNOWLEDGMENT_ID_INDEX_NAME,
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
                ("client_grant_id", ASCENDING),
                ("client_grant_fingerprint", ASCENDING),
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
                ("client_grant_id", ASCENDING),
                ("client_grant_fingerprint", ASCENDING),
                ("effective_from", DESCENDING),
                ("decision", ASCENDING),
            ],
            False,
            DECISION_INDEX_NAME,
        ),
    )
    try:
        for keys, unique, name in indexes:
            target.create_index(keys, unique=unique, name=name)
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryInputError,
            "L9B10_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _collision_queries(
    value: LegalClientMatterMandateAcknowledgment,
) -> tuple[dict[str, object], ...]:
    """Return the three exact tenant-scoped replay identities."""
    return (
        {"tenant_id": value.tenant_id, "acknowledgment_id": value.acknowledgment_id},
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        {"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key},
    )


def persist_acknowledgment(
    value: LegalClientMatterMandateAcknowledgment,
    acknowledgment_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterMandateAcknowledgment:
    """Append one immutable acknowledgment or return its exact replay.

    The caller owns transaction lifecycle. Same-identity exact payloads replay;
    divergent identity collisions fail closed. Mongo duplicate races require a
    fresh whole-transaction restart and never trigger a hidden retry here.
    """
    tx = _active_transaction(session)
    document = _document(value)
    target = _target(acknowledgment_collection)
    labels = ("ACKNOWLEDGMENT_ID", "FINGERPRINT", "IDEMPOTENCY_KEY")
    for query, label in zip(_collision_queries(value), labels):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryConflictError,
            f"L9B10_{label}_COLLISION",
        )
    try:
        target.insert_one(dict(document), session=tx)
    except DuplicateKeyError as error:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryRetryRequiredError,
            "L9B10_WHOLE_TRANSACTION_RETRY_REQUIRED",
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
            LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
            "L9B10_POST_WRITE_RECONCILIATION_FAILED",
        )
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
            "L9B10_POST_WRITE_RECONCILIATION_FAILED",
        )
    return result


def get_acknowledgment(
    tenant_id: str,
    acknowledgment_id: str,
    acknowledgment_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterMandateAcknowledgment:
    """Read one exact acknowledgment under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(acknowledgment_collection),
        {
            "tenant_id": _identity(tenant_id, "tenant_id"),
            "acknowledgment_id": _identity(acknowledgment_id, "acknowledgment_id"),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryNotFoundError,
            "L9B10_ACKNOWLEDGMENT_NOT_FOUND",
        )
    return _hydrate(row)


def get_acknowledgment_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    acknowledgment_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterMandateAcknowledgment:
    """Read one exact fingerprint under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(acknowledgment_collection),
        {
            "tenant_id": _identity(tenant_id, "tenant_id"),
            "fingerprint": _identity(fingerprint, "fingerprint"),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryNotFoundError,
            "L9B10_ACKNOWLEDGMENT_NOT_FOUND",
        )
    return _hydrate(row)


def list_acknowledgments_for_grant(
    tenant_id: str,
    client_grant_id: str,
    acknowledgment_collection: Any | None = None,
    *,
    session: Any = None,
    limit: int = MAX_HISTORY_READS,
) -> tuple[LegalClientMatterMandateAcknowledgment, ...]:
    """Return bounded immutable grant history in deterministic traversal order.

    Ordering is traversal only. This method deliberately does not select a
    latest or current decision; a future currentness composer owns that rule.
    """
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    rows = _rows(
        _target(acknowledgment_collection),
        {
            "tenant_id": _identity(tenant_id, "tenant_id"),
            "client_grant_id": _identity(client_grant_id, "client_grant_id"),
        },
        session=tx,
        limit=bounded + 1,
    )
    if len(rows) > bounded:
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
            "L9B10_READ_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    if any(value.tenant_id != tenant_id or value.client_grant_id != client_grant_id for value in values):
        _fail(
            LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
            "L9B10_HISTORY_SCOPE_INVALID",
        )
    return values


class LegalClientMatterMandateAcknowledgmentRegistry:
    """Static namespace for append-only acknowledgment evidence persistence."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_acknowledgment = staticmethod(persist_acknowledgment)
    get_acknowledgment = staticmethod(get_acknowledgment)
    get_acknowledgment_by_fingerprint = staticmethod(get_acknowledgment_by_fingerprint)
    list_acknowledgments_for_grant = staticmethod(list_acknowledgments_for_grant)


__all__ = [
    "ACKNOWLEDGMENT_ID_INDEX_NAME",
    "COLLECTION",
    "DECISION_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME",
    "IDEMPOTENCY_INDEX_NAME",
    "MAX_HISTORY_READS",
    "READ_CONCERN",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientMatterMandateAcknowledgmentRegistry",
    "LegalClientMatterMandateAcknowledgmentRegistryConflictError",
    "LegalClientMatterMandateAcknowledgmentRegistryError",
    "LegalClientMatterMandateAcknowledgmentRegistryInputError",
    "LegalClientMatterMandateAcknowledgmentRegistryNotFoundError",
    "LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError",
    "LegalClientMatterMandateAcknowledgmentRegistryPersistenceUnavailableError",
    "LegalClientMatterMandateAcknowledgmentRegistryRetryRequiredError",
    "LegalClientMatterMandateAcknowledgmentRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_acknowledgment",
    "get_acknowledgment_by_fingerprint",
    "list_acknowledgments_for_grant",
    "persist_acknowledgment",
]


# ARTIFACT: legal_client_matter_mandate_acknowledgment_registry.py
# VERSION: v1.0.0-L9B10-FIRM-MANDATE-ACKNOWLEDGMENT-REGISTRY
# AUTHORITY BOUNDARY: immutable acknowledgment evidence persistence/read only
# TENANT POSTURE: every identity, replay and grant history query is tenant-scoped
# FAIL-CLOSED POSTURE: strict hydration, divergent collision, duplicate race and persistence rejection; no TTL/currentness
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
