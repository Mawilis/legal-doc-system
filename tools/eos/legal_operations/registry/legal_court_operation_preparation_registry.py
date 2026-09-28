"""WILSY OS durable immutable Court Operation Preparation registry.

TITLE: WILSY OS Legal Court Operation Preparation Registry
VERSION: v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist tenant-scoped immutable internal Court preparation snapshots
         with exact replay, strict hydration, bounded history, and caller-owned
         Mongo transactions. No external Court action is performed here.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_court_operation_preparation_registry.py
COLLABORATION / OWNERSHIP: The P1 domain owns preparation truth; a future
                            orchestrator owns fresh prerequisite revalidation.
                            This module owns append-only persistence and reads.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0 establishes three tenant-scoped replay indexes, three
           bounded history indexes, strict BSON hydration, exact replay,
           divergent collision failure, and no TTL/current-pointer behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque references and SHA3-512 fingerprints only;
                             no raw documents, credentials, Court payloads, or PII.
TENANT BOUNDARY: Every write, replay, and read includes explicit tenant_id.
AUTHORITY BOUNDARY: Immutable internal preparation persistence only; no Court,
                    professional, IAM, financial, or external execution authority.
TRANSACTION BOUNDARY: Caller supplies an already-active transaction. This
                      registry never starts, commits, aborts, or retries one.
FAIL-CLOSED DECLARATION: Missing transactions, malformed rows, divergent
                         collisions, and persistence failures reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_court_operation_preparation import (
    COURT_OPERATION_PREPARATION_FIELDS,
    LegalCourtOperationPreparation,
    LegalCourtOperationPreparationError,
    LegalCourtOperationType,
)


VERSION: Final[str] = "v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION-REGISTRY"
COLLECTION: Final[str] = "legal_court_operation_preparations"
OPERATION_PREPARATION_ID_INDEX_NAME: Final[str] = "legal_court_operation_preparation_tenant_id_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "legal_court_operation_preparation_tenant_fingerprint_unique"
IDEMPOTENCY_INDEX_NAME: Final[str] = "legal_court_operation_preparation_tenant_idempotency_unique"
MATTER_OPERATION_HISTORY_INDEX_NAME: Final[str] = "legal_court_operation_preparation_matter_operation_history"
MATTER_REPRESENTATION_HISTORY_INDEX_NAME: Final[str] = "legal_court_operation_preparation_matter_representation_history"
TARGET_COURT_HISTORY_INDEX_NAME: Final[str] = "legal_court_operation_preparation_target_court_history"
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalCourtOperationPreparationRegistryError(RuntimeError):
    """Base non-sensitive fail-closed registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCourtOperationPreparationRegistryInputError(LegalCourtOperationPreparationRegistryError):
    """Malformed input or unsupported collection interface."""


class LegalCourtOperationPreparationRegistryTransactionRequiredError(LegalCourtOperationPreparationRegistryError):
    """Caller did not provide an active transaction."""


class LegalCourtOperationPreparationRegistryNotFoundError(LegalCourtOperationPreparationRegistryError):
    """Exact tenant-scoped identity is absent."""


class LegalCourtOperationPreparationRegistryConflictError(LegalCourtOperationPreparationRegistryError):
    """Immutable replay identity collides with divergent evidence."""


class LegalCourtOperationPreparationRegistryPersistedRecordInvalidError(LegalCourtOperationPreparationRegistryError):
    """Durable data failed strict P1 schema or fingerprint validation."""


class LegalCourtOperationPreparationRegistryRetryRequiredError(LegalCourtOperationPreparationRegistryError):
    """Duplicate or transient race requires a fresh caller transaction."""


class LegalCourtOperationPreparationRegistryPersistenceUnavailableError(LegalCourtOperationPreparationRegistryError):
    """Mongo persistence failed without a safe replay classification."""


def _fail(error_type: type[LegalCourtOperationPreparationRegistryError], code: str, cause: BaseException | None = None) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _fail(LegalCourtOperationPreparationRegistryRetryRequiredError, "L9C12_P1_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    _fail(LegalCourtOperationPreparationRegistryPersistenceUnavailableError, "L9C12_P1_PERSISTENCE_UNAVAILABLE", error)


def _target(collection: Any | None) -> Any:
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
        _fail(LegalCourtOperationPreparationRegistryPersistenceUnavailableError, "L9C12_P1_PERSISTENCE_UNAVAILABLE", error)


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail(LegalCourtOperationPreparationRegistryTransactionRequiredError, "L9C12_P1_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(LegalCourtOperationPreparationRegistryTransactionRequiredError, "L9C12_P1_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail(LegalCourtOperationPreparationRegistryTransactionRequiredError, "L9C12_P1_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(LegalCourtOperationPreparationRegistryInputError, f"L9C12_P1_{name.upper()}_INVALID")
    return value


def _bounded_limit(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 < value <= MAX_HISTORY_READS:
        _fail(LegalCourtOperationPreparationRegistryInputError, "L9C12_P1_LIMIT_INVALID")
    return value


def _operation_type(value: object) -> str:
    normalized = value.value if isinstance(value, LegalCourtOperationType) else value
    if normalized != LegalCourtOperationType.COURT_FILING_PREPARATION.value:
        _fail(LegalCourtOperationPreparationRegistryInputError, "L9C12_P1_OPERATION_TYPE_INVALID")
    return cast(str, normalized)


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    raw = dict(document)
    raw.pop("_id", None)
    for field in ("document_evidence_lineage", "requested_scope_capabilities"):
        value = raw.get(field)
        if isinstance(value, list):
            raw[field] = tuple(value)
        elif not isinstance(value, tuple):
            _fail(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError, "L9C12_P1_PERSISTED_RECORD_INVALID")
    return raw


def _hydrate(document: Mapping[str, object]) -> LegalCourtOperationPreparation:
    raw = _canonical(document)
    if set(raw) != set(COURT_OPERATION_PREPARATION_FIELDS):
        _fail(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError, "L9C12_P1_PERSISTED_RECORD_INVALID")
    try:
        value = LegalCourtOperationPreparation.from_dict(raw)
    except (TypeError, ValueError, LegalCourtOperationPreparationError) as error:
        _fail(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError, "L9C12_P1_PERSISTED_RECORD_INVALID", error)
    if value.to_dict() != raw:
        _fail(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError, "L9C12_P1_PERSISTED_RECORD_INVALID")
    return value


def _rows(collection: Any, query: Mapping[str, object], *, session: Any, limit: int) -> list[Mapping[str, object]]:
    try:
        cursor = _target(collection).find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort([("prepared_at", ASCENDING), ("occurred_at", ASCENDING), ("fingerprint", ASCENDING), ("operation_preparation_id", ASCENDING)])
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalCourtOperationPreparationRegistryInputError, "L9C12_P1_COLLECTION_INTERFACE_INVALID", error)


def _one(collection: Any, query: Mapping[str, object], *, session: Any) -> Mapping[str, object] | None:
    rows = _rows(collection, query, session=session, limit=2)
    if len(rows) > 1:
        _fail(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError, "L9C12_P1_DUPLICATE_IDENTITY")
    return rows[0] if rows else None


def ensure_indexes(collection: Any | None = None) -> None:
    """Create the three replay and three bounded-history indexes."""
    indexes = (
        ([('tenant_id', ASCENDING), ('operation_preparation_id', ASCENDING)], True, OPERATION_PREPARATION_ID_INDEX_NAME),
        ([('tenant_id', ASCENDING), ('fingerprint', ASCENDING)], True, FINGERPRINT_INDEX_NAME),
        ([('tenant_id', ASCENDING), ('idempotency_key', ASCENDING)], True, IDEMPOTENCY_INDEX_NAME),
        ([('tenant_id', ASCENDING), ('case_matter_id', ASCENDING), ('operation_type', ASCENDING), ('occurred_at', ASCENDING)], False, MATTER_OPERATION_HISTORY_INDEX_NAME),
        ([('tenant_id', ASCENDING), ('case_matter_id', ASCENDING), ('final_representation_id', ASCENDING), ('occurred_at', ASCENDING)], False, MATTER_REPRESENTATION_HISTORY_INDEX_NAME),
        ([('tenant_id', ASCENDING), ('target_court_reference', ASCENDING), ('occurred_at', ASCENDING)], False, TARGET_COURT_HISTORY_INDEX_NAME),
    )
    try:
        target = _target(collection)
        for keys, unique, name in indexes:
            target.create_index(keys, unique=unique, name=name)
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalCourtOperationPreparationRegistryInputError, "L9C12_P1_COLLECTION_INTERFACE_INVALID", error)


def _collision_queries(value: LegalCourtOperationPreparation) -> tuple[tuple[dict[str, object], str], ...]:
    return (
        ({"tenant_id": value.tenant_id, "operation_preparation_id": value.operation_preparation_id}, "OPERATION_PREPARATION_ID"),
        ({"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}, "FINGERPRINT"),
        ({"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key}, "IDEMPOTENCY_KEY"),
    )


def _reconcile_duplicate(target: Any, value: LegalCourtOperationPreparation, document: Mapping[str, object], *, session: Any) -> LegalCourtOperationPreparation:
    for query, label in _collision_queries(value):
        row = _one(target, query, session=session)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == dict(document):
            return existing
        _fail(LegalCourtOperationPreparationRegistryConflictError, f"L9C12_P1_{label}_COLLISION")
    _fail(LegalCourtOperationPreparationRegistryRetryRequiredError, "L9C12_P1_WHOLE_TRANSACTION_RETRY_REQUIRED")


def persist_court_operation_preparation(value: LegalCourtOperationPreparation, preparation_collection: Any | None = None, *, session: Any = None) -> LegalCourtOperationPreparation:
    """Persist one immutable preparation or return its exact replay."""
    tx = _active_transaction(session)
    if type(value) is not LegalCourtOperationPreparation:
        _fail(LegalCourtOperationPreparationRegistryInputError, "L9C12_P1_PREPARATION_REQUIRED")
    document = value.to_dict()
    target = _target(preparation_collection)
    for query, label in _collision_queries(value):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(LegalCourtOperationPreparationRegistryConflictError, f"L9C12_P1_{label}_COLLISION")
    try:
        target.insert_one(dict(document), session=tx)
    except DuplicateKeyError:
        return _reconcile_duplicate(target, value, document, session=tx)
    except PyMongoError as error:
        _raise_mongo(error)
    persisted = _one(target, {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}, session=tx)
    if persisted is None:
        _fail(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError, "L9C12_P1_POST_WRITE_RECONCILIATION_FAILED")
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError, "L9C12_P1_POST_WRITE_RECONCILIATION_FAILED")
    return result


def get_court_operation_preparation(tenant_id: str, operation_preparation_id: str, preparation_collection: Any | None = None, *, session: Any = None) -> LegalCourtOperationPreparation:
    """Read one exact tenant-scoped preparation identity."""
    tx = _active_transaction(session)
    row = _one(_target(preparation_collection), {"tenant_id": _identity("tenant_id", tenant_id), "operation_preparation_id": _identity("operation_preparation_id", operation_preparation_id)}, session=tx)
    if row is None:
        _fail(LegalCourtOperationPreparationRegistryNotFoundError, "L9C12_P1_PREPARATION_NOT_FOUND")
    return _hydrate(row)


def get_court_operation_preparation_by_fingerprint(tenant_id: str, fingerprint: str, preparation_collection: Any | None = None, *, session: Any = None) -> LegalCourtOperationPreparation:
    """Read one exact fingerprint under tenant scope."""
    tx = _active_transaction(session)
    row = _one(_target(preparation_collection), {"tenant_id": _identity("tenant_id", tenant_id), "fingerprint": _identity("fingerprint", fingerprint)}, session=tx)
    if row is None:
        _fail(LegalCourtOperationPreparationRegistryNotFoundError, "L9C12_P1_PREPARATION_NOT_FOUND")
    return _hydrate(row)


def get_court_operation_preparation_by_idempotency_key(tenant_id: str, idempotency_key: str, preparation_collection: Any | None = None, *, session: Any = None) -> LegalCourtOperationPreparation:
    """Read one exact replay identity under tenant scope."""
    tx = _active_transaction(session)
    row = _one(_target(preparation_collection), {"tenant_id": _identity("tenant_id", tenant_id), "idempotency_key": _identity("idempotency_key", idempotency_key)}, session=tx)
    if row is None:
        _fail(LegalCourtOperationPreparationRegistryNotFoundError, "L9C12_P1_PREPARATION_NOT_FOUND")
    return _hydrate(row)


def list_court_operation_preparations_for_matter(tenant_id: str, case_matter_id: str, operation_type: LegalCourtOperationType | str = LegalCourtOperationType.COURT_FILING_PREPARATION, preparation_collection: Any | None = None, *, session: Any = None, limit: int = MAX_HISTORY_READS) -> tuple[LegalCourtOperationPreparation, ...]:
    """Return bounded, deterministic, tenant/matter/operation history."""
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    query = {"tenant_id": _identity("tenant_id", tenant_id), "case_matter_id": _identity("case_matter_id", case_matter_id), "operation_type": _operation_type(operation_type)}
    rows = _rows(_target(preparation_collection), query, session=tx, limit=bounded + 1)
    if len(rows) > bounded:
        _fail(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError, "L9C12_P1_READ_LIMIT_EXCEEDED")
    values = tuple(_hydrate(row) for row in rows)
    if any(any(getattr(value, field) != expected for field, expected in query.items()) for value in values):
        _fail(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError, "L9C12_P1_HISTORY_SCOPE_INVALID")
    return values


class LegalCourtOperationPreparationRegistry:
    """Static namespace for immutable P1 persistence and reads."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_court_operation_preparation = staticmethod(persist_court_operation_preparation)
    get_court_operation_preparation = staticmethod(get_court_operation_preparation)
    get_court_operation_preparation_by_fingerprint = staticmethod(get_court_operation_preparation_by_fingerprint)
    get_court_operation_preparation_by_idempotency_key = staticmethod(get_court_operation_preparation_by_idempotency_key)
    list_court_operation_preparations_for_matter = staticmethod(list_court_operation_preparations_for_matter)


__all__ = [
    "COLLECTION", "FINGERPRINT_INDEX_NAME", "IDEMPOTENCY_INDEX_NAME",
    "MATTER_OPERATION_HISTORY_INDEX_NAME", "MATTER_REPRESENTATION_HISTORY_INDEX_NAME",
    "TARGET_COURT_HISTORY_INDEX_NAME", "MAX_HISTORY_READS", "OPERATION_PREPARATION_ID_INDEX_NAME",
    "READ_CONCERN", "VERSION", "WRITE_CONCERN", "LegalCourtOperationPreparationRegistry",
    "LegalCourtOperationPreparationRegistryConflictError", "LegalCourtOperationPreparationRegistryError",
    "LegalCourtOperationPreparationRegistryInputError", "LegalCourtOperationPreparationRegistryNotFoundError",
    "LegalCourtOperationPreparationRegistryPersistedRecordInvalidError",
    "LegalCourtOperationPreparationRegistryPersistenceUnavailableError",
    "LegalCourtOperationPreparationRegistryRetryRequiredError",
    "LegalCourtOperationPreparationRegistryTransactionRequiredError", "ensure_indexes",
    "get_court_operation_preparation", "get_court_operation_preparation_by_fingerprint",
    "get_court_operation_preparation_by_idempotency_key", "list_court_operation_preparations_for_matter",
    "persist_court_operation_preparation",
]


# ARTIFACT: legal_court_operation_preparation_registry.py
# VERSION: v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION-REGISTRY
# AUTHORITY BOUNDARY: immutable internal preparation persistence only
# TENANT POSTURE: every operation is explicit tenant-scoped
# FAIL-CLOSED POSTURE: missing transactions, malformed rows and collisions reject
# FINANCIAL EXECUTION AUTHORITY: none; external Court acts remain outside WILSY truth
# END OF WILSY OS SOVEREIGN ARTIFACT
