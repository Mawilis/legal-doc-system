"""Durable append-only registry for immutable client-matter mandates.

TITLE: WILSY OS Legal Client Matter Mandate Registry
VERSION: v1.0.0-L9B11-CLIENT-MATTER-MANDATE-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and read exact LegalClientMatterMandate formation evidence
         with tenant-scoped replay, exact grant/acknowledgment-pair
         uniqueness, strict hydration and caller-owned transaction semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_mandate_registry.py
COLLABORATION / OWNERSHIP: LegalClientMatterMandate owns immutable value and
                            fingerprint semantics; this registry owns only
                            append-only durability and exact tenant reads.
                            Formation, currentness, lifecycle, Engagement,
                            IAM and financial authorities remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0 establishes tenant-scoped mandate/fingerprint/idempotency
           and exact grant/acknowledgment-pair uniqueness, strict hydration,
           deterministic history, majority durability and caller-owned
           transactions. No TTL, currentness, lifecycle or downstream write.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded mandate-domain fields and SHA3-512
                             fingerprints are persisted; no raw PII,
                             credentials, tokens or document bodies.
TENANT BOUNDARY: Every write, replay and read begins with exact tenant_id;
                 no global mandate lookup or cross-tenant oracle exists.
AUTHORITY BOUNDARY: Immutable formation evidence persistence/read only. This
                    registry never reads currentness, IAM or upstream objects.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, release or execution;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns the active session and
                      transaction; this registry never starts, commits,
                      aborts, retries or owns session lifecycle.
FAIL-CLOSED DECLARATION: Missing transaction, malformed BSON, divergent
                         replay, duplicate races and persistence failures
                         reject without repair or destructive mutation.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    MANDATE_FIELDS,
    LegalClientMatterMandate,
    LegalClientMatterMandateError,
)

VERSION: Final[str] = "v1.0.0-L9B11-CLIENT-MATTER-MANDATE-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_mandates"
MANDATE_ID_INDEX_NAME: Final[str] = "legal_client_matter_mandate_tenant_id_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "legal_client_matter_mandate_tenant_fingerprint_unique"
IDEMPOTENCY_INDEX_NAME: Final[str] = "legal_client_matter_mandate_tenant_idempotency_unique"
HISTORY_INDEX_NAME: Final[str] = "legal_client_matter_mandate_matter_history"
PAIR_INDEX_NAME: Final[str] = "legal_client_matter_mandate_grant_ack_pair_unique"
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientMatterMandateRegistryError(RuntimeError):
    """Base non-sensitive persistence failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterMandateRegistryInputError(LegalClientMatterMandateRegistryError):
    """Malformed value, query, limit or collection interface."""


class LegalClientMatterMandateRegistryTransactionRequiredError(LegalClientMatterMandateRegistryError):
    """Caller did not supply an active transaction."""


class LegalClientMatterMandateRegistryNotFoundError(LegalClientMatterMandateRegistryError):
    """Exact tenant-scoped mandate identity is absent."""


class LegalClientMatterMandateRegistryConflictError(LegalClientMatterMandateRegistryError):
    """Immutable identity or grant/ack pair collides with divergent evidence."""


class LegalClientMatterMandateRegistryPersistedRecordInvalidError(LegalClientMatterMandateRegistryError):
    """Persisted BSON failed strict domain reconstruction."""


class LegalClientMatterMandateRegistryRetryRequiredError(LegalClientMatterMandateRegistryError):
    """Duplicate race requires a caller-owned whole-transaction restart."""


class LegalClientMatterMandateRegistryPersistenceUnavailableError(LegalClientMatterMandateRegistryError):
    """Mongo persistence failed without a safe replay classification."""


def _fail(error_type: type[LegalClientMatterMandateRegistryError], code: str, cause: BaseException | None = None) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _fail(LegalClientMatterMandateRegistryRetryRequiredError, "L9B11_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    _fail(LegalClientMatterMandateRegistryPersistenceUnavailableError, "L9B11_PERSISTENCE_UNAVAILABLE", error)


def _target(collection: Any) -> Any:
    if collection is None:
        _fail(LegalClientMatterMandateRegistryInputError, "L9B11_COLLECTION_REQUIRED")
    try:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN, codec_options=CodecOptions(tz_aware=True))
    except AttributeError:
        return collection


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail(LegalClientMatterMandateRegistryTransactionRequiredError, "L9B11_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail(LegalClientMatterMandateRegistryTransactionRequiredError, "L9B11_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(LegalClientMatterMandateRegistryInputError, f"L9B11_{name.upper()}_INVALID")
    return value


def _bounded_limit(limit: object) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 < limit <= MAX_HISTORY_READS:
        _fail(LegalClientMatterMandateRegistryInputError, "L9B11_LIMIT_INVALID")
    return limit


def _rows(collection: Any, query: Mapping[str, object], *, session: Any, limit: int) -> list[Mapping[str, Any]]:
    try:
        cursor = _target(collection).find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort([("effective_from", ASCENDING), ("occurred_at", ASCENDING), ("fingerprint", ASCENDING), ("mandate_id", ASCENDING)])
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalClientMatterMandateRegistryInputError, "L9B11_COLLECTION_INTERFACE_INVALID", error)


def _one(collection: Any, query: Mapping[str, object], *, session: Any) -> Mapping[str, Any] | None:
    rows = _rows(collection, query, session=session, limit=2)
    if len(rows) > 1:
        _fail(LegalClientMatterMandateRegistryPersistedRecordInvalidError, "L9B11_DUPLICATE_IDENTITY")
    return rows[0] if rows else None


def _hydrate(document: Mapping[str, Any]) -> LegalClientMatterMandate:
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != set(MANDATE_FIELDS):
        _fail(LegalClientMatterMandateRegistryPersistedRecordInvalidError, "L9B11_PERSISTED_RECORD_INVALID")
    try:
        value = LegalClientMatterMandate.from_dict(cast(Mapping[str, object], raw))
    except (TypeError, ValueError, LegalClientMatterMandateError) as error:
        _fail(LegalClientMatterMandateRegistryPersistedRecordInvalidError, "L9B11_PERSISTED_RECORD_INVALID", error)
    if value.to_dict() != raw:
        _fail(LegalClientMatterMandateRegistryPersistedRecordInvalidError, "L9B11_PERSISTED_RECORD_INVALID")
    return value


def _canonical_document(value: LegalClientMatterMandate) -> dict[str, object]:
    """Re-hydrate caller input so forged frozen-object state fails closed."""
    document = value.to_dict()
    try:
        checked = LegalClientMatterMandate.from_dict(cast(Mapping[str, object], document))
    except (TypeError, ValueError, LegalClientMatterMandateError) as error:
        _fail(LegalClientMatterMandateRegistryInputError, "L9B11_MANDATE_INVALID", error)
    if checked.to_dict() != document:
        _fail(LegalClientMatterMandateRegistryInputError, "L9B11_MANDATE_INVALID")
    return document


def ensure_indexes(collection: Any) -> None:
    """Create immutable tenant/replay/history indexes; never create TTL."""
    indexes = (
        ([('tenant_id', ASCENDING), ('mandate_id', ASCENDING)], True, MANDATE_ID_INDEX_NAME),
        ([('tenant_id', ASCENDING), ('fingerprint', ASCENDING)], True, FINGERPRINT_INDEX_NAME),
        ([('tenant_id', ASCENDING), ('idempotency_key', ASCENDING)], True, IDEMPOTENCY_INDEX_NAME),
        ([('tenant_id', ASCENDING), ('client_grant_fingerprint', ASCENDING), ('firm_acknowledgment_fingerprint', ASCENDING)], True, PAIR_INDEX_NAME),
        ([('tenant_id', ASCENDING), ('case_matter_id', ASCENDING), ('client_party_id', ASCENDING), ('effective_from', ASCENDING), ('occurred_at', ASCENDING), ('fingerprint', ASCENDING)], False, HISTORY_INDEX_NAME),
    )
    try:
        target = _target(collection)
        for keys, unique, name in indexes:
            target.create_index(keys, unique=unique, name=name)
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalClientMatterMandateRegistryInputError, "L9B11_COLLECTION_INTERFACE_INVALID", error)


def _collision_queries(value: LegalClientMatterMandate) -> tuple[tuple[dict[str, object], str], ...]:
    return (
        ({"tenant_id": value.tenant_id, "mandate_id": value.mandate_id}, "MANDATE_ID"),
        ({"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}, "FINGERPRINT"),
        ({"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key}, "IDEMPOTENCY_KEY"),
        ({"tenant_id": value.tenant_id, "client_grant_fingerprint": value.client_grant_fingerprint, "firm_acknowledgment_fingerprint": value.firm_acknowledgment_fingerprint}, "GRANT_ACK_PAIR"),
    )


def persist_mandate(value: LegalClientMatterMandate, mandate_collection: Any, *, session: Any) -> LegalClientMatterMandate:
    """Append one immutable mandate or return its exact tenant-scoped replay.

    The caller owns the active transaction. Same identity or exact grant/ack
    pair replays only when the complete payload is identical; divergent
    evidence fails closed and duplicate races request a whole retry.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterMandate:
        _fail(LegalClientMatterMandateRegistryInputError, "L9B11_MANDATE_REQUIRED")
    target = _target(mandate_collection)
    document = _canonical_document(value)
    for query, label in _collision_queries(value):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(LegalClientMatterMandateRegistryConflictError, f"L9B11_{label}_COLLISION")
    try:
        target.insert_one(dict(document), session=tx)
    except DuplicateKeyError as error:
        _fail(LegalClientMatterMandateRegistryRetryRequiredError, "L9B11_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except PyMongoError as error:
        _raise_mongo(error)
    persisted = _one(target, {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}, session=tx)
    if persisted is None:
        _fail(LegalClientMatterMandateRegistryPersistedRecordInvalidError, "L9B11_POST_WRITE_RECONCILIATION_FAILED")
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(LegalClientMatterMandateRegistryPersistedRecordInvalidError, "L9B11_POST_WRITE_RECONCILIATION_FAILED")
    return result


def get_mandate(tenant_id: str, mandate_id: str, mandate_collection: Any, *, session: Any) -> LegalClientMatterMandate:
    """Read one exact immutable mandate under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(mandate_collection, {"tenant_id": _text("tenant_id", tenant_id), "mandate_id": _text("mandate_id", mandate_id)}, session=tx)
    if row is None:
        _fail(LegalClientMatterMandateRegistryNotFoundError, "L9B11_MANDATE_NOT_FOUND")
    return _hydrate(row)


def get_mandate_by_fingerprint(tenant_id: str, fingerprint: str, mandate_collection: Any, *, session: Any) -> LegalClientMatterMandate:
    """Read one exact immutable mandate by tenant-scoped fingerprint."""
    tx = _active_transaction(session)
    row = _one(mandate_collection, {"tenant_id": _text("tenant_id", tenant_id), "fingerprint": _text("fingerprint", fingerprint)}, session=tx)
    if row is None:
        _fail(LegalClientMatterMandateRegistryNotFoundError, "L9B11_MANDATE_NOT_FOUND")
    return _hydrate(row)


def list_mandates_for_matter(tenant_id: str, case_matter_id: str, client_party_id: str, mandate_collection: Any, *, session: Any, limit: int = MAX_HISTORY_READS) -> tuple[LegalClientMatterMandate, ...]:
    """Return bounded immutable mandate history in deterministic order."""
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    rows = _rows(mandate_collection, {"tenant_id": _text("tenant_id", tenant_id), "case_matter_id": _text("case_matter_id", case_matter_id), "client_party_id": _text("client_party_id", client_party_id)}, session=tx, limit=bounded + 1)
    if len(rows) > bounded:
        _fail(LegalClientMatterMandateRegistryPersistedRecordInvalidError, "L9B11_READ_LIMIT_EXCEEDED")
    values = tuple(_hydrate(row) for row in rows)
    if any(value.tenant_id != tenant_id or value.case_matter_id != case_matter_id or value.client_party_id != client_party_id for value in values):
        _fail(LegalClientMatterMandateRegistryPersistedRecordInvalidError, "L9B11_SCOPE_CORRELATION_INVALID")
    return values


class LegalClientMatterMandateRegistry:
    """Static namespace for immutable mandate persistence and reads only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_mandate = staticmethod(persist_mandate)
    get_mandate = staticmethod(get_mandate)
    get_mandate_by_fingerprint = staticmethod(get_mandate_by_fingerprint)
    list_mandates_for_matter = staticmethod(list_mandates_for_matter)


__all__ = [
    "COLLECTION", "FINGERPRINT_INDEX_NAME", "HISTORY_INDEX_NAME", "IDEMPOTENCY_INDEX_NAME",
    "MANDATE_ID_INDEX_NAME", "MAX_HISTORY_READS", "PAIR_INDEX_NAME", "READ_CONCERN", "VERSION",
    "WRITE_CONCERN", "LegalClientMatterMandateRegistry", "LegalClientMatterMandateRegistryConflictError",
    "LegalClientMatterMandateRegistryError", "LegalClientMatterMandateRegistryInputError",
    "LegalClientMatterMandateRegistryNotFoundError", "LegalClientMatterMandateRegistryPersistedRecordInvalidError",
    "LegalClientMatterMandateRegistryPersistenceUnavailableError", "LegalClientMatterMandateRegistryRetryRequiredError",
    "LegalClientMatterMandateRegistryTransactionRequiredError", "ensure_indexes", "get_mandate",
    "get_mandate_by_fingerprint", "list_mandates_for_matter", "persist_mandate",
]

# ARTIFACT: legal_client_matter_mandate_registry.py
# VERSION: v1.0.0-L9B11-CLIENT-MATTER-MANDATE-REGISTRY
# AUTHORITY BOUNDARY: immutable mandate formation persistence/read only
# TENANT POSTURE: every identity, replay and history query is tenant-scoped
# FAIL-CLOSED POSTURE: strict hydration, collision, race and persistence rejection; no TTL/currentness
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
