"""WILSY OS durable legal conflict-screening registry.

TITLE: Legal Conflict Screening Registry
VERSION: v1.0.2-L8-8E-UTC-CODEC-CORRELATION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable L8-8D exact-subject screening results with strict
         tenant isolation, replay integrity, review-queue lookup and caller-
         owned transaction semantics without creating mutable conflict
         resolution, waiver or clearance authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_conflict_screening_registry.py
COLLABORATION / OWNERSHIP: L8-8D owns screening semantics; L8-8E owns immutable
                            screening persistence/read evidence only. Later
                            orchestration owns authoritative L8-8B subject lookup
                            and later human-review domains must separately own
                            conflict determination, recusal, waiver or ethical
                            wall evidence.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.2-L8-8E-UTC-CODEC-CORRELATION applies an explicit UTC-aware BSON codec to screening reads/writes so immutable timestamp correlation remains valid through the canonical Kernel Mongo client.
           v1.0.1-L8-8E-LEGAL-CONFLICT-SCREENING-REGISTRY narrows the L8-8D status union to LegalConflictScreeningStatus at persistence serialization/correlation boundaries for exact Pyright alignment; stored values and runtime semantics are unchanged.
           v1.0.0-L8-8E-LEGAL-CONFLICT-SCREENING-REGISTRY establishes exact
           tenant+screening identity, strict immutable replay, data-minimized
           envelope correlation, tenant+source and tenant+subject histories,
           tenant+status review queue lookup, bounded reads, caller-owned active
           transactions and governed whole-transaction retry signaling. No TTL
           or mutable status transition is created.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only L8-8D opaque identities/fingerprints
                             and match topology; no raw party PII, legal narrative,
                             credentials, documents or financial data is added.
TENANT BOUNDARY: Every lookup/write/index begins with exact tenant_id.
AUTHORITY BOUNDARY: Screening persistence only. NO_MATCH_FOUND remains only an
                    observed no-exact-match result and REVIEW_REQUIRED remains
                    only a review signal; neither becomes legal clearance,
                    conflict determination, client acceptance or representation
                    authority through persistence.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: All operational reads/writes require an already-active
                      caller-owned Mongo transaction. Registry owns no session,
                      transaction, retry, commit or abort lifecycle.
FAIL-CLOSED DECLARATION: Missing transaction, malformed/corrupt envelope,
                         divergent replay, duplicate identity, query overflow,
                         races and persistence outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import timezone
from typing import Any, Final, NoReturn, cast
import hashlib
import json

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from bson.codec_options import CodecOptions

from tools.eos.legal_operations.domain.legal_conflict_screening import (
    SCREENING_FIELDS,
    LegalConflictScreeningError,
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
)


VERSION: Final[str] = "v1.0.2-L8-8E-UTC-CODEC-CORRELATION"
RECORD_SCHEMA: Final[str] = "WILSY-LEGAL-CONFLICT-SCREENING-RECORD/V1"
COLLECTION: Final[str] = "legal_conflict_screenings"
SCREENING_ID_INDEX_NAME: Final[str] = "legal_conflict_tenant_screening_unique"
SOURCE_HISTORY_INDEX_NAME: Final[str] = "legal_conflict_tenant_source_history"
SUBJECT_HISTORY_INDEX_NAME: Final[str] = "legal_conflict_tenant_subject_history"
REVIEW_QUEUE_INDEX_NAME: Final[str] = "legal_conflict_tenant_status_queue"
MAX_SOURCE_SCREENINGS: Final[int] = 1000
MAX_SUBJECT_SCREENINGS: Final[int] = 2000
MAX_REVIEW_QUEUE: Final[int] = 2000
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")

_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "screening_id",
        "source_party_id",
        "source_case_matter_id",
        "source_party_fingerprint",
        "subject_identity_fingerprint",
        "screened_at",
        "status",
        "screening_fingerprint",
        "evidence_identity",
        "screening_payload",
    }
)


class LegalConflictScreeningRegistryError(RuntimeError):
    """Base fail-closed L8-8E persistence/read error with stable code."""

    default_code = "L8_8E_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalConflictScreeningRegistryInputError(
    LegalConflictScreeningRegistryError
):
    """Malformed registry input or collection interface."""

    default_code = "L8_8E_INPUT_INVALID"


class LegalConflictScreeningRegistryTransactionRequiredError(
    LegalConflictScreeningRegistryError
):
    """Caller did not provide one already-active transaction."""

    default_code = "L8_8E_ACTIVE_TRANSACTION_REQUIRED"


class LegalConflictScreeningRegistryNotFoundError(
    LegalConflictScreeningRegistryError
):
    """No exact tenant/screening identity exists."""

    default_code = "L8_8E_SCREENING_NOT_FOUND"


class LegalConflictScreeningRegistryConflictError(
    LegalConflictScreeningRegistryError
):
    """An immutable screening identity is bound to divergent evidence."""

    default_code = "L8_8E_SCREENING_CONFLICT"


class LegalConflictScreeningRegistryPersistedRecordInvalidError(
    LegalConflictScreeningRegistryError
):
    """Persisted screening envelope or payload is corrupt/divergent."""

    default_code = "L8_8E_PERSISTED_RECORD_INVALID"


class LegalConflictScreeningRegistryRetryRequiredError(
    LegalConflictScreeningRegistryError
):
    """Caller must abort and restart the complete transaction."""

    default_code = "L8_8E_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalConflictScreeningRegistryPersistenceUnavailableError(
    LegalConflictScreeningRegistryError
):
    """Mongo persistence could not be safely read or written."""

    default_code = "L8_8E_PERSISTENCE_UNAVAILABLE"


def _raise(
    error_type: type[LegalConflictScreeningRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _raise(LegalConflictScreeningRegistryRetryRequiredError, cause=error)
    _raise(LegalConflictScreeningRegistryPersistenceUnavailableError, cause=error)


def _target(collection: Any) -> Any:
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc),
        )
    except AttributeError:
        return collection


def _collection(value: Any) -> Any:
    if value is None:
        _raise(
            LegalConflictScreeningRegistryInputError,
            "L8_8E_COLLECTION_REQUIRED",
        )
    return _target(value)


def _active_transaction(session: Any) -> Any:
    if session is None:
        _raise(LegalConflictScreeningRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(LegalConflictScreeningRegistryTransactionRequiredError)
    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(
            LegalConflictScreeningRegistryInputError,
            f"L8_8E_{name.upper()}_INVALID",
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    text = _text(name, value)
    if (
        len(text) != 128
        or any(character not in "0123456789abcdef" for character in text)
    ):
        _raise(
            LegalConflictScreeningRegistryInputError,
            f"L8_8E_{name.upper()}_INVALID",
        )
    return text


def _sha3(value: object) -> str:
    return hashlib.sha3_512(
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _evidence_identity(value: LegalConflictScreeningResult) -> str:
    return _sha3(
        {
            "schema": RECORD_SCHEMA,
            "version": VERSION,
            "tenant_id": value.tenant_id,
            "screening_id": value.screening_id,
            "screening_fingerprint": value.fingerprint,
        }
    )


def _record(value: LegalConflictScreeningResult) -> dict[str, object]:
    return {
        "schema": RECORD_SCHEMA,
        "version": VERSION,
        "entity_type": "LegalConflictScreeningRecord",
        "tenant_id": value.tenant_id,
        "screening_id": value.screening_id,
        "source_party_id": value.source_party_id,
        "source_case_matter_id": value.source_case_matter_id,
        "source_party_fingerprint": value.source_party_fingerprint,
        "subject_identity_fingerprint": value.subject_identity_fingerprint,
        "screened_at": value.screened_at,
        "status": cast(LegalConflictScreeningStatus, value.status).value,
        "screening_fingerprint": value.fingerprint,
        "evidence_identity": _evidence_identity(value),
        "screening_payload": value.to_dict(),
    }


def _hydrate(document: Mapping[str, Any]) -> LegalConflictScreeningResult:
    if not isinstance(document, Mapping):
        _raise(LegalConflictScreeningRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _RECORD_FIELDS:
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_RECORD_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != RECORD_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type") != "LegalConflictScreeningRecord"
    ):
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_RECORD_VERSION_UNSUPPORTED",
        )
    payload = raw.get("screening_payload")
    if not isinstance(payload, Mapping) or set(payload) != set(SCREENING_FIELDS):
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_SCREENING_PAYLOAD_SCHEMA_INVALID",
        )
    try:
        value = LegalConflictScreeningResult.from_dict(
            cast(Mapping[str, object], payload)
        )
    except (TypeError, ValueError, LegalConflictScreeningError) as error:
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_SCREENING_PAYLOAD_INVALID",
            error,
        )
    if (
        raw.get("tenant_id") != value.tenant_id
        or raw.get("screening_id") != value.screening_id
        or raw.get("source_party_id") != value.source_party_id
        or raw.get("source_case_matter_id") != value.source_case_matter_id
        or raw.get("source_party_fingerprint") != value.source_party_fingerprint
        or raw.get("subject_identity_fingerprint")
        != value.subject_identity_fingerprint
        or raw.get("screened_at") != value.screened_at
        or raw.get("status") != cast(LegalConflictScreeningStatus, value.status).value
        or raw.get("screening_fingerprint") != value.fingerprint
        or raw.get("evidence_identity") != _evidence_identity(value)
    ):
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_RECORD_CORRELATION_INVALID",
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
            cursor = cursor.sort(
                [("screened_at", DESCENDING), ("screening_id", ASCENDING)]
            )
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalConflictScreeningRegistryInputError,
            "L8_8E_COLLECTION_INTERFACE_INVALID",
            error,
        )


def ensure_indexes(collection: Any) -> None:
    """Create immutable tenant-scoped screening identity/read indexes only."""
    target = _collection(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("screening_id", ASCENDING)],
            unique=True,
            name=SCREENING_ID_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("source_party_id", ASCENDING),
                ("screened_at", DESCENDING),
            ],
            unique=False,
            name=SOURCE_HISTORY_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("subject_identity_fingerprint", ASCENDING),
                ("screened_at", DESCENDING),
            ],
            unique=False,
            name=SUBJECT_HISTORY_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("status", ASCENDING),
                ("screened_at", DESCENDING),
            ],
            unique=False,
            name=REVIEW_QUEUE_INDEX_NAME,
        )
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalConflictScreeningRegistryInputError,
            "L8_8E_COLLECTION_INTERFACE_INVALID",
            error,
        )


def get_screening(
    tenant_id: str,
    screening_id: str,
    collection: Any,
    *,
    session: Any,
) -> LegalConflictScreeningResult:
    """Read one exact immutable screening identity under caller transaction."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    identity = _text("screening_id", screening_id)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "screening_id": identity},
        session=tx,
        limit=2,
    )
    if not rows:
        _raise(LegalConflictScreeningRegistryNotFoundError)
    if len(rows) > 1:
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_DUPLICATE_SCREENING_ID",
        )
    return _hydrate(rows[0])


def list_source_screenings(
    tenant_id: str,
    source_party_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalConflictScreeningResult, ...]:
    """Read bounded immutable screening history for one exact source party."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    source = _text("source_party_id", source_party_id)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "source_party_id": source},
        session=tx,
        limit=MAX_SOURCE_SCREENINGS + 1,
    )
    if len(rows) > MAX_SOURCE_SCREENINGS:
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_SOURCE_SCREENING_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    if any(
        value.tenant_id != tenant or value.source_party_id != source
        for value in values
    ):
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_SOURCE_QUERY_CORRELATION_INVALID",
        )
    return values


def list_subject_screenings(
    tenant_id: str,
    subject_identity_fingerprint: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalConflictScreeningResult, ...]:
    """Read bounded immutable screening history for one exact subject digest."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    subject = _fingerprint(
        "subject_identity_fingerprint",
        subject_identity_fingerprint,
    )
    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "subject_identity_fingerprint": subject,
        },
        session=tx,
        limit=MAX_SUBJECT_SCREENINGS + 1,
    )
    if len(rows) > MAX_SUBJECT_SCREENINGS:
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_SUBJECT_SCREENING_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    if any(
        value.tenant_id != tenant
        or value.subject_identity_fingerprint != subject
        for value in values
    ):
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_SUBJECT_QUERY_CORRELATION_INVALID",
        )
    return values


def list_review_required(
    tenant_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalConflictScreeningResult, ...]:
    """Read bounded immutable REVIEW_REQUIRED results; no resolution is implied."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "status": LegalConflictScreeningStatus.REVIEW_REQUIRED.value,
        },
        session=tx,
        limit=MAX_REVIEW_QUEUE + 1,
    )
    if len(rows) > MAX_REVIEW_QUEUE:
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_REVIEW_QUEUE_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    if any(
        value.tenant_id != tenant
        or value.status is not LegalConflictScreeningStatus.REVIEW_REQUIRED
        for value in values
    ):
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_REVIEW_QUERY_CORRELATION_INVALID",
        )
    return values


def persist_screening(
    value: LegalConflictScreeningResult,
    collection: Any,
    *,
    session: Any,
) -> LegalConflictScreeningResult:
    """Persist one immutable screening or return exact replay."""
    tx = _active_transaction(session)
    if type(value) is not LegalConflictScreeningResult:
        _raise(
            LegalConflictScreeningRegistryInputError,
            "L8_8E_SCREENING_REQUIRED",
        )
    target = _collection(collection)
    existing = _rows(
        target,
        {
            "tenant_id": value.tenant_id,
            "screening_id": value.screening_id,
        },
        session=tx,
        limit=2,
    )
    if len(existing) > 1:
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_DUPLICATE_SCREENING_ID",
        )
    if existing:
        hydrated = _hydrate(existing[0])
        if hydrated.to_dict() == value.to_dict():
            return hydrated
        _raise(LegalConflictScreeningRegistryConflictError)

    try:
        target.insert_one(_record(value), session=tx)
    except DuplicateKeyError as error:
        _raise(LegalConflictScreeningRegistryRetryRequiredError, cause=error)
    except PyMongoError as error:
        _raise_mongo(error)

    persisted = get_screening(
        value.tenant_id,
        value.screening_id,
        target,
        session=tx,
    )
    if persisted.to_dict() != value.to_dict():
        _raise(
            LegalConflictScreeningRegistryPersistedRecordInvalidError,
            "L8_8E_POST_WRITE_CORRELATION_INVALID",
        )
    return persisted


class LegalConflictScreeningRegistry:
    """Namespace facade for immutable L8-8E screening persistence/read APIs."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_screening = staticmethod(get_screening)
    list_source_screenings = staticmethod(list_source_screenings)
    list_subject_screenings = staticmethod(list_subject_screenings)
    list_review_required = staticmethod(list_review_required)
    persist_screening = staticmethod(persist_screening)


__all__ = [
    "COLLECTION",
    "MAX_REVIEW_QUEUE",
    "MAX_SOURCE_SCREENINGS",
    "MAX_SUBJECT_SCREENINGS",
    "READ_CONCERN",
    "RECORD_SCHEMA",
    "REVIEW_QUEUE_INDEX_NAME",
    "SCREENING_ID_INDEX_NAME",
    "SOURCE_HISTORY_INDEX_NAME",
    "SUBJECT_HISTORY_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "LegalConflictScreeningRegistry",
    "LegalConflictScreeningRegistryConflictError",
    "LegalConflictScreeningRegistryError",
    "LegalConflictScreeningRegistryInputError",
    "LegalConflictScreeningRegistryNotFoundError",
    "LegalConflictScreeningRegistryPersistedRecordInvalidError",
    "LegalConflictScreeningRegistryPersistenceUnavailableError",
    "LegalConflictScreeningRegistryRetryRequiredError",
    "LegalConflictScreeningRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_screening",
    "list_review_required",
    "list_source_screenings",
    "list_subject_screenings",
    "persist_screening",
]


# ARTIFACT: legal_conflict_screening_registry.py
# VERSION: v1.0.2-L8-8E-UTC-CODEC-CORRELATION
# AUTHORITY BOUNDARY: immutable screening persistence/read evidence only; no determination or clearance
# TENANT POSTURE: every lookup/write/index begins with exact tenant_id
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/overflow/race/outage rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
