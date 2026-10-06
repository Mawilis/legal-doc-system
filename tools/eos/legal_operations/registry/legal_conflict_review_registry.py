"""WILSY OS durable legal conflict-review determination registry.

TITLE: Legal Conflict Review Registry
VERSION: v1.0.1-L8-8H-LEGAL-CONFLICT-REVIEW-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable L8-8G human conflict-review determinations with exact
         tenant isolation, screening-history reads, reviewer/outcome audit
         indexes, strict hydration and caller-owned transaction semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_conflict_review_registry.py
COLLABORATION / OWNERSHIP: L8-8G owns human review semantics; L8-8H owns
                            immutable review persistence/read evidence only.
                            Later IAM composition must prove reviewer authority
                            before calling persistence. Later resolution,
                            waiver, ethical-wall, recusal, engagement and
                            representation domains remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.1-L8-8H-LEGAL-CONFLICT-REVIEW-REGISTRY stores the envelope reviewed_at as the exact canonical UTC ISO string already emitted by the immutable L8-8G payload. This prevents MongoDB BSON millisecond normalization from truncating authorization-derived microseconds and falsely triggering record-correlation failure after a valid write, while preserving deterministic lexical chronology, immutable fingerprints, strict replay and audit indexes.
           v1.0.0-L8-8H-LEGAL-CONFLICT-REVIEW-REGISTRY establishes exact
           tenant+review identity replay, screening history, reviewer history,
           outcome audit lookup, strict envelope correlation, bounded reads,
           majority concern, caller-owned active transactions and governed
           whole-transaction retry signaling. It deliberately creates no
           mutable current pointer because multiple immutable reviews may exist
           for one screening across escalation/final-review chronology.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only L8-8G opaque identities, bounded
                             references and SHA3-512 evidence fingerprints; no
                             privileged review narrative or raw party PII is
                             added by this registry.
TENANT BOUNDARY: Every operational lookup/write/index begins with exact tenant_id.
AUTHORITY BOUNDARY: Persistence/read evidence only. Persistence does not prove
                    reviewer IAM, conflict clearance, waiver, ethical wall,
                    recusal, client acceptance, engagement or representation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Every operational read/write requires an already-active
                      caller-owned Mongo transaction. Registry owns no session,
                      transaction, retry, commit or abort lifecycle.
FAIL-CLOSED DECLARATION: Missing transaction, malformed/corrupt envelope,
                         divergent replay, duplicate review identity, bounded
                         query overflow, races and persistence outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast
import hashlib
import json

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_conflict_review import (
    REVIEW_FIELDS,
    LegalConflictReviewDetermination,
    LegalConflictReviewError,
    LegalConflictReviewOutcome,
)


VERSION: Final[str] = "v1.0.1-L8-8H-LEGAL-CONFLICT-REVIEW-REGISTRY"
RECORD_SCHEMA: Final[str] = "WILSY-LEGAL-CONFLICT-REVIEW-RECORD/V1"
COLLECTION: Final[str] = "legal_conflict_reviews"
REVIEW_ID_INDEX_NAME: Final[str] = "legal_conflict_review_tenant_review_unique"
SCREENING_HISTORY_INDEX_NAME: Final[str] = (
    "legal_conflict_review_tenant_screening_history"
)
REVIEWER_HISTORY_INDEX_NAME: Final[str] = (
    "legal_conflict_review_tenant_reviewer_history"
)
OUTCOME_HISTORY_INDEX_NAME: Final[str] = (
    "legal_conflict_review_tenant_outcome_history"
)
MAX_SCREENING_REVIEWS: Final[int] = 500
MAX_REVIEWER_REVIEWS: Final[int] = 2000
MAX_OUTCOME_REVIEWS: Final[int] = 5000
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")

_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "review_id",
        "screening_id",
        "screening_fingerprint",
        "source_party_id",
        "source_case_matter_id",
        "subject_identity_fingerprint",
        "screening_status",
        "reviewer_principal_id",
        "outcome",
        "reviewed_at",
        "review_fingerprint",
        "evidence_identity",
        "review_payload",
    }
)


class LegalConflictReviewRegistryError(RuntimeError):
    """Base fail-closed L8-8H persistence/read error with stable code."""

    default_code = "L8_8H_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalConflictReviewRegistryInputError(LegalConflictReviewRegistryError):
    """Malformed registry input or collection interface."""

    default_code = "L8_8H_INPUT_INVALID"


class LegalConflictReviewRegistryTransactionRequiredError(
    LegalConflictReviewRegistryError
):
    """Caller did not provide one already-active transaction."""

    default_code = "L8_8H_ACTIVE_TRANSACTION_REQUIRED"


class LegalConflictReviewRegistryNotFoundError(LegalConflictReviewRegistryError):
    """No exact tenant/review identity exists."""

    default_code = "L8_8H_REVIEW_NOT_FOUND"


class LegalConflictReviewRegistryConflictError(LegalConflictReviewRegistryError):
    """An immutable review identity is bound to divergent evidence."""

    default_code = "L8_8H_REVIEW_CONFLICT"


class LegalConflictReviewRegistryPersistedRecordInvalidError(
    LegalConflictReviewRegistryError
):
    """Persisted review envelope or payload is corrupt/divergent."""

    default_code = "L8_8H_PERSISTED_RECORD_INVALID"


class LegalConflictReviewRegistryRetryRequiredError(
    LegalConflictReviewRegistryError
):
    """Caller must abort and restart the complete transaction."""

    default_code = "L8_8H_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalConflictReviewRegistryPersistenceUnavailableError(
    LegalConflictReviewRegistryError
):
    """Mongo persistence could not be safely read or written."""

    default_code = "L8_8H_PERSISTENCE_UNAVAILABLE"


def _raise(
    error_type: type[LegalConflictReviewRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _raise(LegalConflictReviewRegistryRetryRequiredError, cause=error)
    _raise(LegalConflictReviewRegistryPersistenceUnavailableError, cause=error)


def _target(collection: Any) -> Any:
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
        )
    except AttributeError:
        return collection


def _collection(value: Any) -> Any:
    if value is None:
        _raise(
            LegalConflictReviewRegistryInputError,
            "L8_8H_COLLECTION_REQUIRED",
        )
    return _target(value)


def _active_transaction(session: Any) -> Any:
    if session is None:
        _raise(LegalConflictReviewRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(LegalConflictReviewRegistryTransactionRequiredError)
    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(
            LegalConflictReviewRegistryInputError,
            f"L8_8H_{name.upper()}_INVALID",
        )
    return value


def _outcome(value: LegalConflictReviewOutcome | str) -> LegalConflictReviewOutcome:
    try:
        return LegalConflictReviewOutcome(value)
    except (TypeError, ValueError) as error:
        _raise(
            LegalConflictReviewRegistryInputError,
            "L8_8H_OUTCOME_INVALID",
            error,
        )


def _sha3(value: object) -> str:
    return hashlib.sha3_512(
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def _evidence_identity(value: LegalConflictReviewDetermination) -> str:
    return _sha3(
        {
            "schema": RECORD_SCHEMA,
            "version": VERSION,
            "tenant_id": value.tenant_id,
            "review_id": value.review_id,
            "review_fingerprint": value.fingerprint,
        }
    )


def _record(value: LegalConflictReviewDetermination) -> dict[str, object]:
    return {
        "schema": RECORD_SCHEMA,
        "version": VERSION,
        "entity_type": "LegalConflictReviewRecord",
        "tenant_id": value.tenant_id,
        "review_id": value.review_id,
        "screening_id": value.screening_id,
        "screening_fingerprint": value.screening_fingerprint,
        "source_party_id": value.source_party_id,
        "source_case_matter_id": value.source_case_matter_id,
        "subject_identity_fingerprint": value.subject_identity_fingerprint,
        "screening_status": str(value.screening_status),
        "reviewer_principal_id": value.reviewer_principal_id,
        "outcome": cast(LegalConflictReviewOutcome, value.outcome).value,
        "reviewed_at": cast(str, value.to_dict()["reviewed_at"]),
        "review_fingerprint": value.fingerprint,
        "evidence_identity": _evidence_identity(value),
        "review_payload": value.to_dict(),
    }


def _hydrate(document: Mapping[str, Any]) -> LegalConflictReviewDetermination:
    if not isinstance(document, Mapping):
        _raise(LegalConflictReviewRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _RECORD_FIELDS:
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_RECORD_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != RECORD_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type") != "LegalConflictReviewRecord"
    ):
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_RECORD_VERSION_UNSUPPORTED",
        )
    payload = raw.get("review_payload")
    if not isinstance(payload, Mapping) or set(payload) != set(REVIEW_FIELDS):
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_REVIEW_PAYLOAD_SCHEMA_INVALID",
        )
    try:
        value = LegalConflictReviewDetermination.from_dict(
            cast(Mapping[str, object], payload)
        )
    except (TypeError, ValueError, LegalConflictReviewError) as error:
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_REVIEW_PAYLOAD_INVALID",
            error,
        )
    if (
        raw.get("tenant_id") != value.tenant_id
        or raw.get("review_id") != value.review_id
        or raw.get("screening_id") != value.screening_id
        or raw.get("screening_fingerprint") != value.screening_fingerprint
        or raw.get("source_party_id") != value.source_party_id
        or raw.get("source_case_matter_id") != value.source_case_matter_id
        or raw.get("subject_identity_fingerprint")
        != value.subject_identity_fingerprint
        or raw.get("screening_status") != str(value.screening_status)
        or raw.get("reviewer_principal_id") != value.reviewer_principal_id
        or raw.get("outcome")
        != cast(LegalConflictReviewOutcome, value.outcome).value
        or raw.get("reviewed_at") != value.to_dict()["reviewed_at"]
        or raw.get("review_fingerprint") != value.fingerprint
        or raw.get("evidence_identity") != _evidence_identity(value)
    ):
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_RECORD_CORRELATION_INVALID",
        )
    return value


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int,
) -> list[Mapping[str, Any]]:
    target = _collection(collection)
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort([("reviewed_at", ASCENDING), ("review_id", ASCENDING)])
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalConflictReviewRegistryInputError,
            "L8_8H_COLLECTION_INTERFACE_INVALID",
            error,
        )


def ensure_indexes(collection: Any) -> None:
    """Create only immutable tenant-scoped review-history indexes."""
    target = _collection(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("review_id", ASCENDING)],
            unique=True,
            name=REVIEW_ID_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("screening_id", ASCENDING),
                ("reviewed_at", ASCENDING),
            ],
            unique=False,
            name=SCREENING_HISTORY_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("reviewer_principal_id", ASCENDING),
                ("reviewed_at", DESCENDING),
            ],
            unique=False,
            name=REVIEWER_HISTORY_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("outcome", ASCENDING),
                ("reviewed_at", DESCENDING),
            ],
            unique=False,
            name=OUTCOME_HISTORY_INDEX_NAME,
        )
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalConflictReviewRegistryInputError,
            "L8_8H_COLLECTION_INTERFACE_INVALID",
            error,
        )


def get_review(
    tenant_id: str,
    review_id: str,
    collection: Any,
    *,
    session: Any,
) -> LegalConflictReviewDetermination:
    """Read one exact immutable review under exact tenant scope."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    identity = _text("review_id", review_id)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "review_id": identity},
        session=tx,
        limit=2,
    )
    if not rows:
        _raise(LegalConflictReviewRegistryNotFoundError)
    if len(rows) > 1:
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_DUPLICATE_REVIEW_ID",
        )
    return _hydrate(rows[0])


def list_screening_reviews(
    tenant_id: str,
    screening_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalConflictReviewDetermination, ...]:
    """Read complete bounded immutable review history for one screening."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    screening = _text("screening_id", screening_id)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "screening_id": screening},
        session=tx,
        limit=MAX_SCREENING_REVIEWS + 1,
    )
    if len(rows) > MAX_SCREENING_REVIEWS:
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_SCREENING_REVIEW_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    if any(
        item.tenant_id != tenant or item.screening_id != screening
        for item in values
    ):
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_SCREENING_QUERY_CORRELATION_INVALID",
        )
    return values


def list_reviewer_reviews(
    tenant_id: str,
    reviewer_principal_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalConflictReviewDetermination, ...]:
    """Read bounded immutable review history for one exact reviewer principal."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    reviewer = _text("reviewer_principal_id", reviewer_principal_id)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "reviewer_principal_id": reviewer},
        session=tx,
        limit=MAX_REVIEWER_REVIEWS + 1,
    )
    if len(rows) > MAX_REVIEWER_REVIEWS:
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_REVIEWER_REVIEW_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    if any(
        item.tenant_id != tenant or item.reviewer_principal_id != reviewer
        for item in values
    ):
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_REVIEWER_QUERY_CORRELATION_INVALID",
        )
    return values


def list_outcome_reviews(
    tenant_id: str,
    outcome: LegalConflictReviewOutcome | str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalConflictReviewDetermination, ...]:
    """Read bounded immutable audit history for one closed review outcome."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    normalized = _outcome(outcome)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "outcome": normalized.value},
        session=tx,
        limit=MAX_OUTCOME_REVIEWS + 1,
    )
    if len(rows) > MAX_OUTCOME_REVIEWS:
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_OUTCOME_REVIEW_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    if any(
        item.tenant_id != tenant
        or cast(LegalConflictReviewOutcome, item.outcome) is not normalized
        for item in values
    ):
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_OUTCOME_QUERY_CORRELATION_INVALID",
        )
    return values


def persist_review(
    review: LegalConflictReviewDetermination,
    collection: Any,
    *,
    session: Any,
) -> LegalConflictReviewDetermination:
    """Persist one immutable review or return exact replay.

    Same tenant/review identity plus identical canonical evidence returns the
    durable value. Same identity plus divergent evidence fails closed. Duplicate
    key races under an active transaction become a whole-transaction retry
    signal; the registry never performs internal retry or transaction lifecycle.
    """
    tx = _active_transaction(session)
    if type(review) is not LegalConflictReviewDetermination:
        _raise(
            LegalConflictReviewRegistryInputError,
            "L8_8H_REVIEW_REQUIRED",
        )
    target = _collection(collection)
    existing = _rows(
        target,
        {"tenant_id": review.tenant_id, "review_id": review.review_id},
        session=tx,
        limit=2,
    )
    if len(existing) > 1:
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_DUPLICATE_REVIEW_ID",
        )
    if existing:
        hydrated = _hydrate(existing[0])
        if hydrated.to_dict() == review.to_dict():
            return hydrated
        _raise(LegalConflictReviewRegistryConflictError)

    try:
        target.insert_one(_record(review), session=tx)
    except DuplicateKeyError as error:
        _raise(LegalConflictReviewRegistryRetryRequiredError, cause=error)
    except PyMongoError as error:
        _raise_mongo(error)

    persisted = get_review(
        review.tenant_id,
        review.review_id,
        target,
        session=tx,
    )
    if persisted.to_dict() != review.to_dict():
        _raise(
            LegalConflictReviewRegistryPersistedRecordInvalidError,
            "L8_8H_POST_WRITE_CORRELATION_INVALID",
        )
    return persisted


class LegalConflictReviewRegistry:
    """Institutional namespace for L8-8H persistence/read operations."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_review = staticmethod(get_review)
    list_screening_reviews = staticmethod(list_screening_reviews)
    list_reviewer_reviews = staticmethod(list_reviewer_reviews)
    list_outcome_reviews = staticmethod(list_outcome_reviews)
    persist_review = staticmethod(persist_review)


__all__ = [
    "COLLECTION",
    "MAX_OUTCOME_REVIEWS",
    "MAX_REVIEWER_REVIEWS",
    "MAX_SCREENING_REVIEWS",
    "OUTCOME_HISTORY_INDEX_NAME",
    "READ_CONCERN",
    "RECORD_SCHEMA",
    "REVIEWER_HISTORY_INDEX_NAME",
    "REVIEW_ID_INDEX_NAME",
    "SCREENING_HISTORY_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "LegalConflictReviewRegistry",
    "LegalConflictReviewRegistryConflictError",
    "LegalConflictReviewRegistryError",
    "LegalConflictReviewRegistryInputError",
    "LegalConflictReviewRegistryNotFoundError",
    "LegalConflictReviewRegistryPersistenceUnavailableError",
    "LegalConflictReviewRegistryPersistedRecordInvalidError",
    "LegalConflictReviewRegistryRetryRequiredError",
    "LegalConflictReviewRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_review",
    "list_outcome_reviews",
    "list_reviewer_reviews",
    "list_screening_reviews",
    "persist_review",
]


# ARTIFACT: legal_conflict_review_registry.py
# VERSION: v1.0.1-L8-8H-LEGAL-CONFLICT-REVIEW-REGISTRY
# AUTHORITY BOUNDARY: immutable human-review persistence/read evidence only
# TENANT POSTURE: every operational lookup/write/index begins with exact tenant_id
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/overflow/race/outage rejects; canonical string chronology preserves microseconds across BSON; no mutable current pointer
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
