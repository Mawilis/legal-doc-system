"""WILSY OS durable Engagement firm-decision registry.

TITLE: WILSY OS Legal Client Matter Engagement Firm Decision Registry
VERSION: v1.0.0-L9C9-P1-ENGAGEMENT-FIRM-DECISION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable firm-decision evidence with exact tenant-scoped
         replay identities, strict domain hydration, bounded history and
         caller-owned Mongo transaction semantics. This registry never
         resolves currentness or forms Engagement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_engagement_firm_decision_registry.py
COLLABORATION / OWNERSHIP: The L9C1 domain owns decision semantics and
                            fingerprints; L9C8 owns authorization and source
                            correlation; L9C9-P1 owns append-only durability
                            and tenant-scoped history. A later currentness
                            composer owns effective-time selection.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C9-P1-ENGAGEMENT-FIRM-DECISION-REGISTRY establishes the
           canonical collection, tenant-scoped replay identities, strict
           hydration, bounded context history and caller-owned transaction
           semantics. It creates no current pointer, TTL, IAM, Engagement,
           Representation, Court or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only canonical opaque decision fields and their
                             SHA3-512 fingerprint are persisted. No raw PII,
                             credentials, bearer tokens or review narrative.
TENANT BOUNDARY: Every identity lookup, replay probe and history query starts
                 with the exact tenant_id; no cross-tenant oracle exists.
AUTHORITY BOUNDARY: Immutable firm-decision evidence persistence/read only.
                    Authorization, matter, party, acceptance, conflict,
                    mandate and currentness are not reinterpreted.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive
                               financial execution and settlement authority.
TRANSACTION BOUNDARY: Caller supplies an already-active Mongo transaction.
                      This module never starts, commits, aborts, retries or
                      reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing transactions, malformed rows, divergent
                         collisions, duplicate races, query overflow and
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

from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    FIRM_DECISION_FIELDS,
    LegalClientMatterEngagementFirmDecision,
    LegalClientMatterEngagementFirmDecisionError,
)


VERSION: Final[str] = "v1.0.0-L9C9-P1-ENGAGEMENT-FIRM-DECISION-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_engagement_firm_decisions"
DECISION_ID_INDEX_NAME: Final[str] = (
    "legal_client_matter_engagement_firm_decision_tenant_id_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_engagement_firm_decision_tenant_fingerprint_unique"
)
IDEMPOTENCY_INDEX_NAME: Final[str] = (
    "legal_client_matter_engagement_firm_decision_tenant_idempotency_unique"
)
HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_engagement_firm_decision_context_history"
)
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientMatterEngagementFirmDecisionRegistryError(RuntimeError):
    """Base non-sensitive, fail-closed registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterEngagementFirmDecisionRegistryInputError(
    LegalClientMatterEngagementFirmDecisionRegistryError
):
    """Input or collection-interface contract failed."""


class LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError(
    LegalClientMatterEngagementFirmDecisionRegistryError
):
    """The caller did not supply an active transaction."""


class LegalClientMatterEngagementFirmDecisionRegistryNotFoundError(
    LegalClientMatterEngagementFirmDecisionRegistryError
):
    """The exact tenant-scoped decision identity is absent."""


class LegalClientMatterEngagementFirmDecisionRegistryConflictError(
    LegalClientMatterEngagementFirmDecisionRegistryError
):
    """An immutable replay identity collides with divergent evidence."""


class LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError(
    LegalClientMatterEngagementFirmDecisionRegistryError
):
    """Durable data failed strict schema, fingerprint or scope validation."""


class LegalClientMatterEngagementFirmDecisionRegistryRetryRequiredError(
    LegalClientMatterEngagementFirmDecisionRegistryError
):
    """A duplicate or transient race requires a fresh caller transaction."""


class LegalClientMatterEngagementFirmDecisionRegistryPersistenceUnavailableError(
    LegalClientMatterEngagementFirmDecisionRegistryError
):
    """Mongo persistence failed without a safe replay classification."""


def _fail(
    error_type: type[LegalClientMatterEngagementFirmDecisionRegistryError],
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
            LegalClientMatterEngagementFirmDecisionRegistryRetryRequiredError,
            "L9C9_P1_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    _fail(
        LegalClientMatterEngagementFirmDecisionRegistryPersistenceUnavailableError,
        "L9C9_P1_PERSISTENCE_UNAVAILABLE",
        error,
    )


def _target(collection: Any | None) -> Any:
    """Resolve an explicit collection with canonical durability concerns."""
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
            LegalClientMatterEngagementFirmDecisionRegistryPersistenceUnavailableError,
            "L9C9_P1_PERSISTENCE_UNAVAILABLE",
            error,
        )


def _active_transaction(session: Any) -> Any:
    """Require an active caller transaction without starting one."""
    if session is None:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError,
            "L9C9_P1_ACTIVE_TRANSACTION_REQUIRED",
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError,
            "L9C9_P1_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError,
            "L9C9_P1_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _identity(name: str, value: object) -> str:
    """Validate an opaque lookup value without coercion or value leakage."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryInputError,
            f"L9C9_P1_{name.upper()}_INVALID",
        )
    return value


def _bounded_limit(limit: object) -> int:
    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or not 0 < limit <= MAX_HISTORY_READS
    ):
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryInputError,
            "L9C9_P1_LIMIT_INVALID",
        )
    return limit


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    raw = dict(document)
    raw.pop("_id", None)
    return raw


def _hydrate(
    document: Mapping[str, object],
) -> LegalClientMatterEngagementFirmDecision:
    """Reconstruct only the exact published domain schema."""
    raw = _canonical(document)
    if set(raw) != set(FIRM_DECISION_FIELDS):
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C9_P1_PERSISTED_RECORD_INVALID",
        )
    try:
        value = LegalClientMatterEngagementFirmDecision.from_dict(
            cast(Mapping[str, object], raw)
        )
    except (TypeError, ValueError, LegalClientMatterEngagementFirmDecisionError) as error:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C9_P1_PERSISTED_RECORD_INVALID",
            error,
        )
    if value.to_dict() != raw:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C9_P1_PERSISTED_RECORD_INVALID",
        )
    return value


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
                    ("occurred_at", ASCENDING),
                    ("fingerprint", ASCENDING),
                    ("decision_id", ASCENDING),
                ]
            )
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryInputError,
            "L9C9_P1_COLLECTION_INTERFACE_INVALID",
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
            LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C9_P1_DUPLICATE_IDENTITY",
        )
    return rows[0] if rows else None


def ensure_indexes(collection: Any | None = None) -> None:
    """Create deterministic replay/history indexes; never TTL or currentness."""
    indexes = (
        (
            [("tenant_id", ASCENDING), ("decision_id", ASCENDING)],
            True,
            DECISION_ID_INDEX_NAME,
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
                ("occurred_at", ASCENDING),
                ("fingerprint", ASCENDING),
                ("decision_id", ASCENDING),
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
            LegalClientMatterEngagementFirmDecisionRegistryInputError,
            "L9C9_P1_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _collision_queries(
    value: LegalClientMatterEngagementFirmDecision,
) -> tuple[tuple[dict[str, object], str], ...]:
    return (
        (
            {"tenant_id": value.tenant_id, "decision_id": value.decision_id},
            "DECISION_ID",
        ),
        (
            {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
            "FINGERPRINT",
        ),
        (
            {"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key},
            "IDEMPOTENCY_KEY",
        ),
    )


def _reconcile_duplicate(
    target: Any,
    value: LegalClientMatterEngagementFirmDecision,
    document: Mapping[str, object],
    *,
    session: Any,
) -> LegalClientMatterEngagementFirmDecision:
    """Classify a duplicate-key race without turning arbitrary errors into success."""
    for query, label in _collision_queries(value):
        row = _one(target, query, session=session)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == dict(document):
            return existing
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryConflictError,
            f"L9C9_P1_{label}_COLLISION",
        )
    _fail(
        LegalClientMatterEngagementFirmDecisionRegistryRetryRequiredError,
        "L9C9_P1_WHOLE_TRANSACTION_RETRY_REQUIRED",
    )


def persist_firm_decision(
    value: LegalClientMatterEngagementFirmDecision,
    decision_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterEngagementFirmDecision:
    """Append one exact firm decision or return its immutable replay.

    The caller owns transaction lifecycle. Only an exact tenant-scoped
    canonical replay is accepted; all divergent collisions and corrupt rows
    fail closed. No currentness or Engagement decision is calculated.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterEngagementFirmDecision:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryInputError,
            "L9C9_P1_FIRM_DECISION_REQUIRED",
        )
    document = value.to_dict()
    target = _target(decision_collection)
    for query, label in _collision_queries(value):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryConflictError,
            f"L9C9_P1_{label}_COLLISION",
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
            LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C9_P1_POST_WRITE_RECONCILIATION_FAILED",
        )
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C9_P1_POST_WRITE_RECONCILIATION_FAILED",
        )
    return result


def get_firm_decision(
    tenant_id: str,
    decision_id: str,
    decision_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterEngagementFirmDecision:
    """Read one exact decision under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(decision_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "decision_id": _identity("decision_id", decision_id),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryNotFoundError,
            "L9C9_P1_FIRM_DECISION_NOT_FOUND",
        )
    return _hydrate(row)


def get_firm_decision_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    decision_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterEngagementFirmDecision:
    """Read one exact fingerprint under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(decision_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "fingerprint": _identity("fingerprint", fingerprint),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryNotFoundError,
            "L9C9_P1_FIRM_DECISION_NOT_FOUND",
        )
    return _hydrate(row)


def list_firm_decisions_for_context(
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    decision_collection: Any | None = None,
    *,
    session: Any = None,
    limit: int = MAX_HISTORY_READS,
) -> tuple[LegalClientMatterEngagementFirmDecision, ...]:
    """Return exact bounded history; never calculate currentness."""
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    values = (
        ("case_matter_id", _identity("case_matter_id", case_matter_id)),
        ("matter_fingerprint", _identity("matter_fingerprint", matter_fingerprint)),
        ("client_party_id", _identity("client_party_id", client_party_id)),
        (
            "subject_identity_fingerprint",
            _identity("subject_identity_fingerprint", subject_identity_fingerprint),
        ),
    )
    query = {"tenant_id": _identity("tenant_id", tenant_id), **dict(values)}
    rows = _rows(
        _target(decision_collection),
        query,
        session=tx,
        limit=bounded + 1,
    )
    if len(rows) > bounded:
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C9_P1_READ_LIMIT_EXCEEDED",
        )
    decisions = tuple(_hydrate(row) for row in rows)
    expected = (("tenant_id", query["tenant_id"]),) + values
    if any(
        any(getattr(decision, field) != expected_value for field, expected_value in expected)
        for decision in decisions
    ):
        _fail(
            LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C9_P1_HISTORY_SCOPE_INVALID",
        )
    return decisions


class LegalClientMatterEngagementFirmDecisionRegistry:
    """Static namespace for immutable decision persistence and reads only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_firm_decision = staticmethod(persist_firm_decision)
    get_firm_decision = staticmethod(get_firm_decision)
    get_firm_decision_by_fingerprint = staticmethod(get_firm_decision_by_fingerprint)
    list_firm_decisions_for_context = staticmethod(list_firm_decisions_for_context)


__all__ = [
    "COLLECTION",
    "DECISION_ID_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME",
    "IDEMPOTENCY_INDEX_NAME",
    "MAX_HISTORY_READS",
    "READ_CONCERN",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientMatterEngagementFirmDecisionRegistry",
    "LegalClientMatterEngagementFirmDecisionRegistryConflictError",
    "LegalClientMatterEngagementFirmDecisionRegistryError",
    "LegalClientMatterEngagementFirmDecisionRegistryInputError",
    "LegalClientMatterEngagementFirmDecisionRegistryNotFoundError",
    "LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError",
    "LegalClientMatterEngagementFirmDecisionRegistryPersistenceUnavailableError",
    "LegalClientMatterEngagementFirmDecisionRegistryRetryRequiredError",
    "LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_firm_decision",
    "get_firm_decision_by_fingerprint",
    "list_firm_decisions_for_context",
    "persist_firm_decision",
]


# ARTIFACT: legal_client_matter_engagement_firm_decision_registry.py
# VERSION: v1.0.0-L9C9-P1-ENGAGEMENT-FIRM-DECISION-REGISTRY
# AUTHORITY BOUNDARY: immutable firm-decision evidence persistence/read only
# TENANT POSTURE: every identity, replay and history query is tenant-scoped
# FAIL-CLOSED POSTURE: active transaction, strict hydration, collision, race and persistence failures reject; no currentness is calculated
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
