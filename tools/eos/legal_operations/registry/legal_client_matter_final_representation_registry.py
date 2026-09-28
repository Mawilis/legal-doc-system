"""WILSY OS durable immutable final Representation registry.

TITLE: WILSY OS Legal Client Matter Final Representation Registry
VERSION: v1.0.0-L9C11-P24-FINAL-REPRESENTATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist exact immutable P24 final Representation snapshots with
         tenant-scoped replay identities, strict BSON hydration, bounded
         lineage history and caller-owned Mongo transactions. This registry
         never forms, selects currentness, revokes or authorizes a snapshot.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_final_representation_registry.py
COLLABORATION / OWNERSHIP: P24 domain owns truth and integrity; this module
                            owns append-only persistence and exact reads only.
                            Formation/orchestration, IAM, Court and finance
                            remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P24 establishes three tenant-scoped unique replay
           indexes, four bounded lineage indexes, exact duplicate replay,
           collision failure, strict hydration and no current-pointer/TTL
           behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only canonical opaque P24 snapshots are stored.
TENANT BOUNDARY: Every write, replay and history read includes tenant_id and
                 exact lineage; cross-tenant rows are indistinguishable from absence.
AUTHORITY BOUNDARY: Immutable persistence/read only; no IAM, currentness,
                    revocation, supersession, Court or financial authority.
TRANSACTION BOUNDARY: Caller supplies an already-active transaction. This
                      registry never starts, commits, aborts or retries one.
FAIL-CLOSED DECLARATION: Missing transactions, malformed rows, divergent
                         collisions, overflow and persistence failures reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_final_representation import (
    FINAL_REPRESENTATION_FIELDS,
    LegalClientMatterFinalRepresentation,
    LegalClientMatterFinalRepresentationError,
)


VERSION: Final[str] = "v1.0.0-L9C11-P24-FINAL-REPRESENTATION-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_final_representations"
REPRESENTATION_ID_INDEX_NAME: Final[str] = "legal_client_matter_final_representation_tenant_id_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "legal_client_matter_final_representation_tenant_fingerprint_unique"
IDEMPOTENCY_INDEX_NAME: Final[str] = "legal_client_matter_final_representation_tenant_idempotency_unique"
MATTER_CLIENT_REPRESENTATIVE_HISTORY_INDEX_NAME: Final[str] = "legal_client_matter_final_representation_matter_client_representative_history"
MATTER_AUTHORITY_HISTORY_INDEX_NAME: Final[str] = "legal_client_matter_final_representation_matter_authority_history"
MATTER_DECISION_HISTORY_INDEX_NAME: Final[str] = "legal_client_matter_final_representation_matter_decision_history"
MATTER_EFFECTIVE_HISTORY_INDEX_NAME: Final[str] = "legal_client_matter_final_representation_matter_effective_history"
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientMatterFinalRepresentationRegistryError(RuntimeError):
    """Base non-sensitive fail-closed registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterFinalRepresentationRegistryInputError(LegalClientMatterFinalRepresentationRegistryError):
    """Malformed input or unsupported collection interface."""


class LegalClientMatterFinalRepresentationRegistryTransactionRequiredError(LegalClientMatterFinalRepresentationRegistryError):
    """Caller did not provide an active transaction."""


class LegalClientMatterFinalRepresentationRegistryNotFoundError(LegalClientMatterFinalRepresentationRegistryError):
    """Exact tenant-scoped identity is absent."""


class LegalClientMatterFinalRepresentationRegistryConflictError(LegalClientMatterFinalRepresentationRegistryError):
    """Immutable replay identity collides with divergent evidence."""


class LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError(LegalClientMatterFinalRepresentationRegistryError):
    """Durable data failed strict P24 schema or fingerprint validation."""


class LegalClientMatterFinalRepresentationRegistryRetryRequiredError(LegalClientMatterFinalRepresentationRegistryError):
    """Duplicate or transient race requires a fresh caller transaction."""


class LegalClientMatterFinalRepresentationRegistryPersistenceUnavailableError(LegalClientMatterFinalRepresentationRegistryError):
    """Mongo persistence failed without a safe replay classification."""


def _fail(error_type: type[LegalClientMatterFinalRepresentationRegistryError], code: str, cause: BaseException | None = None) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _fail(LegalClientMatterFinalRepresentationRegistryRetryRequiredError, "L9C11_P24_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    _fail(LegalClientMatterFinalRepresentationRegistryPersistenceUnavailableError, "L9C11_P24_PERSISTENCE_UNAVAILABLE", error)


def _target(collection: Any | None) -> Any:
    if collection is not None:
        try:
            return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN, codec_options=CodecOptions(tz_aware=True))
        except AttributeError:
            return collection
    try:
        from tools.eos.kernel.db import get_database

        database = get_database()
        if database is None:
            raise RuntimeError("database unavailable")
        return database.get_collection(COLLECTION, write_concern=WRITE_CONCERN, read_concern=READ_CONCERN, codec_options=CodecOptions(tz_aware=True))
    except Exception as error:
        _fail(LegalClientMatterFinalRepresentationRegistryPersistenceUnavailableError, "L9C11_P24_PERSISTENCE_UNAVAILABLE", error)


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail(LegalClientMatterFinalRepresentationRegistryTransactionRequiredError, "L9C11_P24_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(LegalClientMatterFinalRepresentationRegistryTransactionRequiredError, "L9C11_P24_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail(LegalClientMatterFinalRepresentationRegistryTransactionRequiredError, "L9C11_P24_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(LegalClientMatterFinalRepresentationRegistryInputError, f"L9C11_P24_{name.upper()}_INVALID")
    return value


def _bounded_limit(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 < value <= MAX_HISTORY_READS:
        _fail(LegalClientMatterFinalRepresentationRegistryInputError, "L9C11_P24_LIMIT_INVALID")
    return value


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    raw = dict(document)
    raw.pop("_id", None)
    value = raw.get("representation_scope_capabilities")
    if isinstance(value, list):
        raw["representation_scope_capabilities"] = tuple(value)
    elif not isinstance(value, tuple):
        _fail(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError, "L9C11_P24_PERSISTED_RECORD_INVALID")
    return raw


def _hydrate(document: Mapping[str, object]) -> LegalClientMatterFinalRepresentation:
    raw = _canonical(document)
    if set(raw) != set(FINAL_REPRESENTATION_FIELDS):
        _fail(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError, "L9C11_P24_PERSISTED_RECORD_INVALID")
    try:
        value = LegalClientMatterFinalRepresentation.from_dict(cast(Mapping[str, object], raw))
    except (TypeError, ValueError, LegalClientMatterFinalRepresentationError) as error:
        _fail(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError, "L9C11_P24_PERSISTED_RECORD_INVALID", error)
    if value.to_dict() != raw:
        _fail(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError, "L9C11_P24_PERSISTED_RECORD_INVALID")
    return value


def _rows(collection: Any, query: Mapping[str, object], *, session: Any, limit: int) -> list[Mapping[str, object]]:
    try:
        cursor = _target(collection).find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort([("effective_from", ASCENDING), ("occurred_at", ASCENDING), ("fingerprint", ASCENDING), ("representation_id", ASCENDING)])
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalClientMatterFinalRepresentationRegistryInputError, "L9C11_P24_COLLECTION_INTERFACE_INVALID", error)


def _one(collection: Any, query: Mapping[str, object], *, session: Any) -> Mapping[str, object] | None:
    rows = _rows(collection, query, session=session, limit=2)
    if len(rows) > 1:
        _fail(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError, "L9C11_P24_DUPLICATE_IDENTITY")
    return rows[0] if rows else None


def ensure_indexes(collection: Any | None = None) -> None:
    """Create the three replay identities and four non-TTL history indexes."""
    indexes = (
        ([("tenant_id", ASCENDING), ("representation_id", ASCENDING)], True, REPRESENTATION_ID_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("fingerprint", ASCENDING)], True, FINGERPRINT_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)], True, IDEMPOTENCY_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("client_party_id", ASCENDING), ("representative_principal_id", ASCENDING), ("effective_from", ASCENDING)], False, MATTER_CLIENT_REPRESENTATIVE_HISTORY_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("representation_authority_id", ASCENDING), ("representation_authority_fingerprint", ASCENDING)], False, MATTER_AUTHORITY_HISTORY_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("firm_representation_decision_id", ASCENDING), ("firm_representation_decision_fingerprint", ASCENDING)], False, MATTER_DECISION_HISTORY_INDEX_NAME),
        ([("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("effective_from", ASCENDING)], False, MATTER_EFFECTIVE_HISTORY_INDEX_NAME),
    )
    try:
        target = _target(collection)
        for keys, unique, name in indexes:
            target.create_index(keys, unique=unique, name=name)
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalClientMatterFinalRepresentationRegistryInputError, "L9C11_P24_COLLECTION_INTERFACE_INVALID", error)


def _collision_queries(value: LegalClientMatterFinalRepresentation) -> tuple[tuple[dict[str, object], str], ...]:
    return (
        ({"tenant_id": value.tenant_id, "representation_id": value.representation_id}, "REPRESENTATION_ID"),
        ({"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}, "FINGERPRINT"),
        ({"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key}, "IDEMPOTENCY_KEY"),
    )


def _reconcile_duplicate(target: Any, value: LegalClientMatterFinalRepresentation, document: Mapping[str, object], *, session: Any) -> LegalClientMatterFinalRepresentation:
    for query, label in _collision_queries(value):
        row = _one(target, query, session=session)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == dict(document):
            return existing
        _fail(LegalClientMatterFinalRepresentationRegistryConflictError, f"L9C11_P24_{label}_COLLISION")
    _fail(LegalClientMatterFinalRepresentationRegistryRetryRequiredError, "L9C11_P24_WHOLE_TRANSACTION_RETRY_REQUIRED")


def persist_final_representation(value: LegalClientMatterFinalRepresentation, representation_collection: Any | None = None, *, session: Any = None) -> LegalClientMatterFinalRepresentation:
    """Persist one immutable P24 snapshot or return its exact replay."""
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterFinalRepresentation:
        _fail(LegalClientMatterFinalRepresentationRegistryInputError, "L9C11_P24_FINAL_REPRESENTATION_REQUIRED")
    document = value.to_dict()
    target = _target(representation_collection)
    for query, label in _collision_queries(value):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(LegalClientMatterFinalRepresentationRegistryConflictError, f"L9C11_P24_{label}_COLLISION")
    try:
        target.insert_one(dict(document), session=tx)
    except DuplicateKeyError:
        return _reconcile_duplicate(target, value, document, session=tx)
    except PyMongoError as error:
        _raise_mongo(error)
    persisted = _one(target, {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}, session=tx)
    if persisted is None:
        _fail(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError, "L9C11_P24_POST_WRITE_RECONCILIATION_FAILED")
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError, "L9C11_P24_POST_WRITE_RECONCILIATION_FAILED")
    return result


def get_final_representation(tenant_id: str, representation_id: str, representation_collection: Any | None = None, *, session: Any = None) -> LegalClientMatterFinalRepresentation:
    """Read one exact tenant-scoped representation identity."""
    tx = _active_transaction(session)
    row = _one(_target(representation_collection), {"tenant_id": _identity("tenant_id", tenant_id), "representation_id": _identity("representation_id", representation_id)}, session=tx)
    if row is None:
        _fail(LegalClientMatterFinalRepresentationRegistryNotFoundError, "L9C11_P24_FINAL_REPRESENTATION_NOT_FOUND")
    return _hydrate(row)


def get_final_representation_by_fingerprint(tenant_id: str, fingerprint: str, representation_collection: Any | None = None, *, session: Any = None) -> LegalClientMatterFinalRepresentation:
    """Read one exact fingerprint under tenant scope."""
    tx = _active_transaction(session)
    row = _one(_target(representation_collection), {"tenant_id": _identity("tenant_id", tenant_id), "fingerprint": _identity("fingerprint", fingerprint)}, session=tx)
    if row is None:
        _fail(LegalClientMatterFinalRepresentationRegistryNotFoundError, "L9C11_P24_FINAL_REPRESENTATION_NOT_FOUND")
    return _hydrate(row)


def get_final_representation_by_idempotency_key(tenant_id: str, idempotency_key: str, representation_collection: Any | None = None, *, session: Any = None) -> LegalClientMatterFinalRepresentation:
    """Read one exact replay identity under tenant scope."""
    tx = _active_transaction(session)
    row = _one(_target(representation_collection), {"tenant_id": _identity("tenant_id", tenant_id), "idempotency_key": _identity("idempotency_key", idempotency_key)}, session=tx)
    if row is None:
        _fail(LegalClientMatterFinalRepresentationRegistryNotFoundError, "L9C11_P24_FINAL_REPRESENTATION_NOT_FOUND")
    return _hydrate(row)


def list_final_representations_for_context(
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    representative_principal_id: str,
    representation_authority_id: str,
    firm_representation_decision_id: str,
    representation_collection: Any | None = None,
    *,
    session: Any = None,
    limit: int = MAX_HISTORY_READS,
) -> tuple[LegalClientMatterFinalRepresentation, ...]:
    """Return bounded exact tenant/matter/client/representative history."""
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    query = {
        "tenant_id": _identity("tenant_id", tenant_id),
        "case_matter_id": _identity("case_matter_id", case_matter_id),
        "matter_fingerprint": _identity("matter_fingerprint", matter_fingerprint),
        "client_party_id": _identity("client_party_id", client_party_id),
        "subject_identity_fingerprint": _identity("subject_identity_fingerprint", subject_identity_fingerprint),
        "representative_principal_id": _identity("representative_principal_id", representative_principal_id),
        "representation_authority_id": _identity("representation_authority_id", representation_authority_id),
        "firm_representation_decision_id": _identity("firm_representation_decision_id", firm_representation_decision_id),
    }
    rows = _rows(_target(representation_collection), query, session=tx, limit=bounded + 1)
    if len(rows) > bounded:
        _fail(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError, "L9C11_P24_READ_LIMIT_EXCEEDED")
    values = tuple(_hydrate(row) for row in rows)
    if any(any(getattr(value, field) != expected for field, expected in query.items()) for value in values):
        _fail(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError, "L9C11_P24_HISTORY_SCOPE_INVALID")
    return values


class LegalClientMatterFinalRepresentationRegistry:
    """Static namespace for immutable P24 persistence and reads."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_final_representation = staticmethod(persist_final_representation)
    get_final_representation = staticmethod(get_final_representation)
    get_final_representation_by_fingerprint = staticmethod(get_final_representation_by_fingerprint)
    get_final_representation_by_idempotency_key = staticmethod(get_final_representation_by_idempotency_key)
    list_final_representations_for_context = staticmethod(list_final_representations_for_context)


__all__ = [
    "COLLECTION",
    "FINGERPRINT_INDEX_NAME",
    "IDEMPOTENCY_INDEX_NAME",
    "MATTER_AUTHORITY_HISTORY_INDEX_NAME",
    "MATTER_CLIENT_REPRESENTATIVE_HISTORY_INDEX_NAME",
    "MATTER_DECISION_HISTORY_INDEX_NAME",
    "MATTER_EFFECTIVE_HISTORY_INDEX_NAME",
    "MAX_HISTORY_READS",
    "READ_CONCERN",
    "REPRESENTATION_ID_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientMatterFinalRepresentationRegistry",
    "LegalClientMatterFinalRepresentationRegistryConflictError",
    "LegalClientMatterFinalRepresentationRegistryError",
    "LegalClientMatterFinalRepresentationRegistryInputError",
    "LegalClientMatterFinalRepresentationRegistryNotFoundError",
    "LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError",
    "LegalClientMatterFinalRepresentationRegistryPersistenceUnavailableError",
    "LegalClientMatterFinalRepresentationRegistryRetryRequiredError",
    "LegalClientMatterFinalRepresentationRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_final_representation",
    "get_final_representation_by_fingerprint",
    "get_final_representation_by_idempotency_key",
    "list_final_representations_for_context",
    "persist_final_representation",
]


# ARTIFACT: legal_client_matter_final_representation_registry.py
# VERSION: v1.0.0-L9C11-P24-FINAL-REPRESENTATION-REGISTRY
# AUTHORITY BOUNDARY: immutable P24 persistence/read only
# TENANT POSTURE: every identity and history read is tenant-scoped
# FAIL-CLOSED POSTURE: collisions, corruption and transaction violations reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
