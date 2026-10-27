"""Append-only persistence for non-authorizing G64 ratification evidence.

TITLE: G64 Ratification Workspace Registry
VERSION: v1.0.0-G64-IMMUTABLE-WORKSPACE-REGISTRY
AUTHORITY: Immutable evidence persistence only; no institutional or IAM authority.
EPITOME: Store exact G64 workspace evidence in caller-owned Mongo transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/g64_ratification_workspace_registry.py
COLLABORATION / OWNERSHIP: G64 domain owns evidence semantics; authenticated API
                            composition must own principal/tenant admission and
                            caller-owned transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-27
CHANGELOG: v1.0.0 adds append-only, tenant/institution-scoped evidence persistence,
           strict replay identity, majority+journal durability and bounded reads.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and fingerprints only; no credentials
                            or raw company documents are accepted by this registry.
TENANT BOUNDARY: Every query includes exact tenant and institution identifiers.
AUTHORITY BOUNDARY: Stored evidence is never interpreted as ratification or access.
TRANSACTION BOUNDARY: Caller supplies and owns an already-active Mongo transaction.
FAIL-CLOSED DECLARATION: Missing transactions, malformed records, divergent replay,
                         corrupt rows, races and storage errors reject.
"""
from __future__ import annotations

from typing import Any, Final, Mapping

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64RatificationWorkspaceRecord,
)

VERSION: Final[str] = "v1.0.0-G64-IMMUTABLE-WORKSPACE-REGISTRY"
COLLECTION: Final[str] = "g64_ratification_workspace_evidence"
RECORD_SCHEMA: Final[str] = "WILSY-G64-RATIFICATION-WORKSPACE-REGISTRY/V1"
RECORD_ID_INDEX: Final[str] = "g64_workspace_institution_record_unique"
MAX_HISTORY: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class G64RegistryError(RuntimeError):
    """Base registry error with stable, content-free code."""

    code = "G64_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or type(self).code
        super().__init__(self.code)


class G64RegistryInputError(G64RegistryError):
    code = "G64_REGISTRY_INPUT_INVALID"


class G64RegistryTransactionRequiredError(G64RegistryError):
    code = "G64_REGISTRY_ACTIVE_TRANSACTION_REQUIRED"


class G64RegistryConflictError(G64RegistryError):
    code = "G64_REGISTRY_IMMUTABLE_ID_CONFLICT"


class G64RegistryCorruptRecordError(G64RegistryError):
    code = "G64_REGISTRY_PERSISTED_RECORD_INVALID"


class G64RegistryRetryRequiredError(G64RegistryError):
    code = "G64_REGISTRY_WHOLE_TRANSACTION_RETRY_REQUIRED"


class G64RegistryUnavailableError(G64RegistryError):
    code = "G64_REGISTRY_PERSISTENCE_UNAVAILABLE"


def _active_transaction(session: Any) -> None:
    if session is None:
        raise G64RegistryTransactionRequiredError()
    try:
        active = session.in_transaction
        if callable(active):
            active = active()
    except Exception as error:
        raise G64RegistryTransactionRequiredError() from error
    if active is not True:
        raise G64RegistryTransactionRequiredError()


def _collection(collection: Any) -> Any:
    if collection is None:
        raise G64RegistryInputError("G64_REGISTRY_COLLECTION_REQUIRED")
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN, read_concern=READ_CONCERN
        )
    except AttributeError:
        return collection


def _key(record: G64RatificationWorkspaceRecord) -> dict[str, str]:
    return {
        "institution_id": record.institution_id,
        "record_id": record.record_id,
    }


def _envelope(record: G64RatificationWorkspaceRecord) -> dict[str, Any]:
    payload = record.to_document()
    return {
        "schema": RECORD_SCHEMA,
        "version": VERSION,
        **_key(record),
        "evidence_sha3_512": record.evidence_fingerprint(),
        "payload": payload,
    }


def ensure_indexes(collection: Any) -> None:
    """Create only the registry's declared unique identity index at startup."""
    target = _collection(collection)
    try:
        target.create_index(
            [("institution_id", ASCENDING), ("record_id", ASCENDING)],
            unique=True,
            name=RECORD_ID_INDEX,
        )
    except PyMongoError as error:
        raise G64RegistryUnavailableError() from error


def append_record(
    *, record: G64RatificationWorkspaceRecord, collection: Any, session: Any
) -> G64RatificationWorkspaceRecord:
    """Append or exactly replay an immutable evidence record inside caller transaction."""
    _active_transaction(session)
    if type(record) is not G64RatificationWorkspaceRecord:
        raise G64RegistryInputError("G64_REGISTRY_RECORD_INVALID")
    target = _collection(collection)
    envelope = _envelope(record)
    query = _key(record)
    try:
        existing = target.find_one(query, session=session)
        if existing is not None:
            if existing != envelope:
                raise G64RegistryConflictError()
            return record
        target.insert_one(envelope, session=session)
        return record
    except G64RegistryConflictError:
        raise
    except DuplicateKeyError as error:
        raise G64RegistryRetryRequiredError() from error
    except PyMongoError as error:
        if error.has_error_label("TransientTransactionError"):
            raise G64RegistryRetryRequiredError() from error
        raise G64RegistryUnavailableError() from error


def read_record(
    *, institution_id: str, record_id: str, collection: Any, session: Any
) -> Mapping[str, Any]:
    """Read one exact institution-scoped envelope inside caller transaction."""
    _active_transaction(session)
    if not isinstance(institution_id, str) or not institution_id.strip():
        raise G64RegistryInputError("G64_REGISTRY_INSTITUTION_ID_INVALID")
    if not isinstance(record_id, str) or not record_id.strip():
        raise G64RegistryInputError("G64_REGISTRY_RECORD_ID_INVALID")
    target = _collection(collection)
    try:
        envelope = target.find_one(
            {"institution_id": institution_id, "record_id": record_id},
            session=session,
        )
    except PyMongoError as error:
        raise G64RegistryUnavailableError() from error
    if envelope is None:
        raise G64RegistryError("G64_REGISTRY_RECORD_NOT_FOUND")
    if (
        not isinstance(envelope, dict)
        or envelope.get("schema") != RECORD_SCHEMA
        or envelope.get("version") != VERSION
        or not isinstance(envelope.get("payload"), dict)
        or envelope.get("institution_id") != institution_id
        or envelope.get("record_id") != record_id
    ):
        raise G64RegistryCorruptRecordError()
    payload = envelope["payload"]
    expected = envelope.get("evidence_sha3_512")
    actual = payload.get("evidence_sha3_512")
    if expected != actual or not isinstance(expected, str) or len(expected) != 128:
        raise G64RegistryCorruptRecordError()
    return envelope


def list_history(
    *, institution_id: str, collection: Any, session: Any, limit: int = 100
) -> tuple[Mapping[str, Any], ...]:
    """Return bounded institution-scoped immutable history in deterministic order."""
    _active_transaction(session)
    if not isinstance(institution_id, str) or not institution_id.strip():
        raise G64RegistryInputError("G64_REGISTRY_INSTITUTION_ID_INVALID")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_HISTORY:
        raise G64RegistryInputError("G64_REGISTRY_HISTORY_LIMIT_INVALID")
    target = _collection(collection)
    try:
        cursor = target.find(
            {"institution_id": institution_id}, session=session
        ).sort([("payload.created_at", ASCENDING), ("record_id", ASCENDING)]).limit(limit + 1)
        rows = tuple(cursor)
    except PyMongoError as error:
        raise G64RegistryUnavailableError() from error
    if len(rows) > limit:
        raise G64RegistryInputError("G64_REGISTRY_HISTORY_LIMIT_EXCEEDED")
    for row in rows:
        if (
            not isinstance(row, dict)
            or row.get("schema") != RECORD_SCHEMA
            or row.get("institution_id") != institution_id
            or not isinstance(row.get("payload"), dict)
            or row.get("evidence_sha3_512") != row["payload"].get("evidence_sha3_512")
        ):
            raise G64RegistryCorruptRecordError()
    return rows
