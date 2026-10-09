"""WILSY OS durable immutable client-matter Engagement registry.

TITLE: WILSY OS Legal Client Matter Engagement Registry
VERSION: v1.0.0-L9C10-P1-CLIENT-MATTER-ENGAGEMENT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and read exact ``LegalClientMatterEngagement`` evidence with
         tenant-scoped replay identities, strict domain hydration, bounded
         lineage history and caller-owned Mongo transaction semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_engagement_registry.py
COLLABORATION / OWNERSHIP: The Engagement domain owns semantic validation and
                            SHA3-512 fingerprints. This registry owns only
                            append-only durability and exact tenant reads.
                            Formation, currentness, IAM, Representation,
                            Court and financial authorities remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C10-P1 establishes the canonical
           legal_client_matter_engagements collection, tenant-scoped unique
           replay identities, strict hydration, bounded deterministic history,
           majority durability and caller-owned active transactions. It adds
           no TTL, current pointer, lifecycle, formation, IAM, Representation,
           Court or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only canonical immutable Engagement fields and
                             their SHA3-512 fingerprint are persisted. No raw
                             credentials, bearer tokens or unbounded narrative
                             are introduced by this registry.
TENANT BOUNDARY: Every write, replay lookup and history query begins with the
                 exact tenant_id. Cross-tenant identity reuse is not an
                 existence oracle.
AUTHORITY BOUNDARY: Immutable Engagement evidence persistence and reads only.
                    This module never reconstructs prerequisites, adjudicates
                    formation, calculates currentness or grants permission.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive
                               financial execution and settlement authority.
TRANSACTION BOUNDARY: The caller supplies an already-active Mongo transaction
                      and owns commit, abort, retry and reconciliation policy.
FAIL-CLOSED DECLARATION: Missing transactions, malformed rows, divergent
                         collisions, duplicate races, read overflow and
                         persistence failures reject without repair.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    ENGAGEMENT_FIELDS,
    LegalClientMatterEngagement,
    LegalClientMatterEngagementError,
)


VERSION: Final[str] = "v1.0.0-L9C10-P1-CLIENT-MATTER-ENGAGEMENT-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_engagements"
ENGAGEMENT_ID_INDEX_NAME: Final[str] = (
    "legal_client_matter_engagement_tenant_id_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_engagement_tenant_fingerprint_unique"
)
IDEMPOTENCY_INDEX_NAME: Final[str] = (
    "legal_client_matter_engagement_tenant_idempotency_unique"
)
HISTORY_INDEX_NAME: Final[str] = "legal_client_matter_engagement_context_history"
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientMatterEngagementRegistryError(RuntimeError):
    """Base non-sensitive, fail-closed registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterEngagementRegistryInputError(
    LegalClientMatterEngagementRegistryError
):
    """Input or collection-interface contract failed."""


class LegalClientMatterEngagementRegistryTransactionRequiredError(
    LegalClientMatterEngagementRegistryError
):
    """The caller did not supply an active transaction."""


class LegalClientMatterEngagementRegistryNotFoundError(
    LegalClientMatterEngagementRegistryError
):
    """The exact tenant-scoped Engagement identity is absent."""


class LegalClientMatterEngagementRegistryConflictError(
    LegalClientMatterEngagementRegistryError
):
    """An immutable replay identity collides with divergent evidence."""


class LegalClientMatterEngagementRegistryPersistedRecordInvalidError(
    LegalClientMatterEngagementRegistryError
):
    """Durable data failed strict schema, fingerprint or scope validation."""


class LegalClientMatterEngagementRegistryRetryRequiredError(
    LegalClientMatterEngagementRegistryError
):
    """A duplicate or transient race requires a fresh caller transaction."""


class LegalClientMatterEngagementRegistryPersistenceUnavailableError(
    LegalClientMatterEngagementRegistryError
):
    """Mongo persistence failed without a safe replay classification."""


def _fail(
    error_type: type[LegalClientMatterEngagementRegistryError],
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
            LegalClientMatterEngagementRegistryRetryRequiredError,
            "L9C10_P1_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    _fail(
        LegalClientMatterEngagementRegistryPersistenceUnavailableError,
        "L9C10_P1_PERSISTENCE_UNAVAILABLE",
        error,
    )


def _target(collection: Any) -> Any:
    """Resolve the explicit collection with canonical durability options."""
    if collection is None:
        _fail(
            LegalClientMatterEngagementRegistryInputError,
            "L9C10_P1_COLLECTION_REQUIRED",
        )
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(tz_aware=True),
        )
    except AttributeError:
        return collection


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller transaction without owning it."""
    if session is None:
        _fail(
            LegalClientMatterEngagementRegistryTransactionRequiredError,
            "L9C10_P1_ACTIVE_TRANSACTION_REQUIRED",
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            LegalClientMatterEngagementRegistryTransactionRequiredError,
            "L9C10_P1_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _fail(
            LegalClientMatterEngagementRegistryTransactionRequiredError,
            "L9C10_P1_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _identity(name: str, value: object) -> str:
    """Validate an opaque lookup identity without coercion or value leakage."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientMatterEngagementRegistryInputError,
            f"L9C10_P1_{name.upper()}_INVALID",
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    """Validate a lowercase SHA3-512 query fingerprint."""
    text = _identity(name, value)
    if len(text) != 128 or any(c not in "0123456789abcdef" for c in text):
        _fail(
            LegalClientMatterEngagementRegistryInputError,
            f"L9C10_P1_{name.upper()}_INVALID",
        )
    return text


def _bounded_limit(limit: object) -> int:
    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or not 0 < limit <= MAX_HISTORY_READS
    ):
        _fail(
            LegalClientMatterEngagementRegistryInputError,
            "L9C10_P1_LIMIT_INVALID",
        )
    return limit


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    raw = dict(document)
    raw.pop("_id", None)
    return raw


def _hydrate(
    document: Mapping[str, object],
) -> LegalClientMatterEngagement:
    """Hydrate only the exact published domain schema and verify integrity."""
    raw = _canonical(document)
    if set(raw) != set(ENGAGEMENT_FIELDS):
        _fail(
            LegalClientMatterEngagementRegistryPersistedRecordInvalidError,
            "L9C10_P1_PERSISTED_RECORD_INVALID",
        )
    try:
        value = LegalClientMatterEngagement.from_dict(
            cast(Mapping[str, object], raw)
        )
    except (TypeError, ValueError, LegalClientMatterEngagementError) as error:
        _fail(
            LegalClientMatterEngagementRegistryPersistedRecordInvalidError,
            "L9C10_P1_PERSISTED_RECORD_INVALID",
            error,
        )
    if value.to_dict() != raw:
        _fail(
            LegalClientMatterEngagementRegistryPersistedRecordInvalidError,
            "L9C10_P1_PERSISTED_RECORD_INVALID",
        )
    return value


def _canonical_document(
    value: LegalClientMatterEngagement,
) -> dict[str, object]:
    """Re-hydrate input to reject forged or internally divergent state."""
    document = value.to_dict()
    try:
        checked = LegalClientMatterEngagement.from_dict(
            cast(Mapping[str, object], document)
        )
    except (TypeError, ValueError, LegalClientMatterEngagementError) as error:
        _fail(
            LegalClientMatterEngagementRegistryInputError,
            "L9C10_P1_ENGAGEMENT_INVALID",
            error,
        )
    if checked.to_dict() != document:
        _fail(
            LegalClientMatterEngagementRegistryInputError,
            "L9C10_P1_ENGAGEMENT_INVALID",
        )
    return document


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int,
) -> list[Mapping[str, object]]:
    """Read bounded rows while propagating the exact caller session."""
    try:
        cursor = _target(collection).find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort(
                [
                    ("effective_from", ASCENDING),
                    ("fingerprint", ASCENDING),
                    ("engagement_id", ASCENDING),
                ]
            )
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientMatterEngagementRegistryInputError,
            "L9C10_P1_COLLECTION_INTERFACE_INVALID",
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
            LegalClientMatterEngagementRegistryPersistedRecordInvalidError,
            "L9C10_P1_DUPLICATE_IDENTITY",
        )
    return rows[0] if rows else None


def ensure_indexes(collection: Any) -> None:
    """Create replay and history indexes; never create TTL/currentness state."""
    indexes = (
        (
            [("tenant_id", ASCENDING), ("engagement_id", ASCENDING)],
            True,
            ENGAGEMENT_ID_INDEX_NAME,
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
                ("case_matter_id", ASCENDING),
                ("matter_fingerprint", ASCENDING),
                ("client_party_id", ASCENDING),
                ("subject_identity_fingerprint", ASCENDING),
                ("effective_from", ASCENDING),
                ("fingerprint", ASCENDING),
                ("engagement_id", ASCENDING),
            ],
            False,
            HISTORY_INDEX_NAME,
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
            LegalClientMatterEngagementRegistryInputError,
            "L9C10_P1_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _collision_queries(
    value: LegalClientMatterEngagement,
) -> tuple[tuple[dict[str, object], str], ...]:
    return (
        (
            {"tenant_id": value.tenant_id, "engagement_id": value.engagement_id},
            "ENGAGEMENT_ID",
        ),
        (
            {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
            "FINGERPRINT",
        ),
        (
            {
                "tenant_id": value.tenant_id,
                "idempotency_key": value.idempotency_key,
            },
            "IDEMPOTENCY_KEY",
        ),
    )


def _reconcile_duplicate(
    target: Any,
    value: LegalClientMatterEngagement,
    document: Mapping[str, object],
    *,
    session: Any,
) -> LegalClientMatterEngagement:
    """Classify a duplicate-key race without turning errors into success."""
    for query, label in _collision_queries(value):
        row = _one(target, query, session=session)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == dict(document):
            return existing
        _fail(
            LegalClientMatterEngagementRegistryConflictError,
            f"L9C10_P1_{label}_COLLISION",
        )
    _fail(
        LegalClientMatterEngagementRegistryRetryRequiredError,
        "L9C10_P1_WHOLE_TRANSACTION_RETRY_REQUIRED",
    )


def persist_engagement(
    value: LegalClientMatterEngagement,
    engagement_collection: Any,
    *,
    session: Any,
) -> LegalClientMatterEngagement:
    """Append one exact Engagement or return its immutable replay.

    The caller owns the active transaction. The registry accepts only a fully
    constructed domain value, performs no prerequisite rereads, and returns a
    hydrated historic value only when every tenant-scoped replay identity and
    the complete canonical payload agree.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterEngagement:
        _fail(
            LegalClientMatterEngagementRegistryInputError,
            "L9C10_P1_ENGAGEMENT_REQUIRED",
        )
    target = _target(engagement_collection)
    document = _canonical_document(value)
    for query, label in _collision_queries(value):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(
            LegalClientMatterEngagementRegistryConflictError,
            f"L9C10_P1_{label}_COLLISION",
        )
    try:
        target.insert_one(dict(document), session=tx)
    except DuplicateKeyError:
        return _reconcile_duplicate(target, value, document, session=tx)
    except PyMongoError as error:
        _raise_mongo(error)
    persisted = _one(
        target,
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        session=tx,
    )
    if persisted is None:
        _fail(
            LegalClientMatterEngagementRegistryPersistedRecordInvalidError,
            "L9C10_P1_POST_WRITE_RECONCILIATION_FAILED",
        )
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(
            LegalClientMatterEngagementRegistryPersistedRecordInvalidError,
            "L9C10_P1_POST_WRITE_RECONCILIATION_FAILED",
        )
    return result


def get_engagement(
    tenant_id: str,
    engagement_id: str,
    engagement_collection: Any,
    *,
    session: Any,
) -> LegalClientMatterEngagement:
    """Read one exact Engagement identity under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        engagement_collection,
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "engagement_id": _identity("engagement_id", engagement_id),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterEngagementRegistryNotFoundError,
            "L9C10_P1_ENGAGEMENT_NOT_FOUND",
        )
    return _hydrate(row)


def get_engagement_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    engagement_collection: Any,
    *,
    session: Any,
) -> LegalClientMatterEngagement:
    """Read one exact fingerprint under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        engagement_collection,
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "fingerprint": _fingerprint("fingerprint", fingerprint),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterEngagementRegistryNotFoundError,
            "L9C10_P1_ENGAGEMENT_NOT_FOUND",
        )
    return _hydrate(row)


def get_engagement_by_idempotency_key(
    tenant_id: str,
    idempotency_key: str,
    engagement_collection: Any,
    *,
    session: Any,
) -> LegalClientMatterEngagement:
    """Read replay authority by tenant-scoped idempotency key only."""
    tx = _active_transaction(session)
    row = _one(
        engagement_collection,
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "idempotency_key": _identity("idempotency_key", idempotency_key),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterEngagementRegistryNotFoundError,
            "L9C10_P1_ENGAGEMENT_NOT_FOUND",
        )
    return _hydrate(row)


def list_engagements_for_context(
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    engagement_collection: Any,
    *,
    session: Any,
    limit: int = MAX_HISTORY_READS,
) -> tuple[LegalClientMatterEngagement, ...]:
    """Return bounded immutable lineage history in deterministic order.

    Ordering is traversal only. This method never selects a current or active
    Engagement and never infers Representation, Court or financial authority.
    """
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    values = (
        ("case_matter_id", _identity("case_matter_id", case_matter_id)),
        ("matter_fingerprint", _fingerprint("matter_fingerprint", matter_fingerprint)),
        ("client_party_id", _identity("client_party_id", client_party_id)),
        (
            "subject_identity_fingerprint",
            _fingerprint(
                "subject_identity_fingerprint", subject_identity_fingerprint
            ),
        ),
    )
    query = {
        "tenant_id": _identity("tenant_id", tenant_id),
        **dict(values),
    }
    rows = _rows(
        engagement_collection,
        query,
        session=tx,
        limit=bounded + 1,
    )
    if len(rows) > bounded:
        _fail(
            LegalClientMatterEngagementRegistryPersistedRecordInvalidError,
            "L9C10_P1_READ_LIMIT_EXCEEDED",
        )
    engagements = tuple(_hydrate(row) for row in rows)
    expected = (("tenant_id", query["tenant_id"]),) + values
    if any(
        any(getattr(engagement, field) != expected_value for field, expected_value in expected)
        for engagement in engagements
    ):
        _fail(
            LegalClientMatterEngagementRegistryPersistedRecordInvalidError,
            "L9C10_P1_HISTORY_SCOPE_INVALID",
        )
    return engagements


class LegalClientMatterEngagementRegistry:
    """Static namespace for immutable Engagement persistence and reads only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_engagement = staticmethod(persist_engagement)
    get_engagement = staticmethod(get_engagement)
    get_engagement_by_fingerprint = staticmethod(get_engagement_by_fingerprint)
    get_engagement_by_idempotency_key = staticmethod(
        get_engagement_by_idempotency_key
    )
    list_engagements_for_context = staticmethod(list_engagements_for_context)


__all__ = [
    "COLLECTION",
    "ENGAGEMENT_ID_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME",
    "IDEMPOTENCY_INDEX_NAME",
    "MAX_HISTORY_READS",
    "READ_CONCERN",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientMatterEngagementRegistry",
    "LegalClientMatterEngagementRegistryConflictError",
    "LegalClientMatterEngagementRegistryError",
    "LegalClientMatterEngagementRegistryInputError",
    "LegalClientMatterEngagementRegistryNotFoundError",
    "LegalClientMatterEngagementRegistryPersistedRecordInvalidError",
    "LegalClientMatterEngagementRegistryPersistenceUnavailableError",
    "LegalClientMatterEngagementRegistryRetryRequiredError",
    "LegalClientMatterEngagementRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_engagement",
    "get_engagement_by_fingerprint",
    "get_engagement_by_idempotency_key",
    "list_engagements_for_context",
    "persist_engagement",
]


# ARTIFACT: legal_client_matter_engagement_registry.py
# VERSION: v1.0.0-L9C10-P1-CLIENT-MATTER-ENGAGEMENT-REGISTRY
# AUTHORITY BOUNDARY: immutable Engagement persistence/read only
# TENANT POSTURE: every identity, replay and history query is tenant-scoped
# FAIL-CLOSED POSTURE: active transaction, strict hydration, collision, race and persistence failures reject; no formation/currentness is calculated
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
