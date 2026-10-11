"""Wilsy OS durable registry for immutable legal-matter deadlines.

TITLE: Wilsy OS Legal Matter Deadline Durable Registry
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist exact D1 LegalMatterDeadline evidence with tenant-scoped
         immutable replay and caller-owned Mongo transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system-legal-deadline-engine/tools/eos/legal_operations/registry/legal_matter_deadline_registry.py
COLLABORATION / OWNERSHIP: D1 owns semantics; D2 owns persistence and bounded
                            reads; later services own orchestration.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY establishes exact D1 payload persistence, tenant replay, strict hydration, deterministic non-TTL indexes, and active caller-transaction enforcement.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded D1 evidence is persisted; corruption rejects.
TENANT BOUNDARY: Every index, read, replay and write starts with tenant_id.
AUTHORITY BOUNDARY: Persistence/read evidence only; no calculation, overdue,
                    filing, service, court, representation, calendar, or AI authority.
TRANSACTION BOUNDARY: Caller supplies an active transaction; registry owns no
                      client, session, transaction, retry, commit, abort or upsert.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing transaction, divergence, race, corruption,
                         malformed scope or Mongo failure rejects.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_matter_deadline import LegalMatterDeadline, LegalMatterDeadlineError

VERSION: Final[str] = "v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY"
COLLECTION: Final[str] = "legal_matter_deadlines"
TENANT_DEADLINE_UNIQUE_INDEX: Final[str] = "legal_deadline_tenant_deadline_unique"
MATTER_DEADLINE_INDEX: Final[str] = "legal_deadline_tenant_matter_deadline"
MATTER_DUE_INDEX: Final[str] = "legal_deadline_tenant_matter_due"
MATTER_STATUS_DUE_INDEX: Final[str] = "legal_deadline_tenant_matter_status_due"
MAX_MATTER_DEADLINES: Final[int] = 5000
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalMatterDeadlineRegistryError(RuntimeError):
    """Base fail-closed registry error carrying one stable code."""
    default_code = "D2_DEADLINE_REGISTRY_ERROR"
    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalMatterDeadlineRegistryInputError(LegalMatterDeadlineRegistryError):
    """Registry input or collection interface is malformed."""
    default_code = "D2_DEADLINE_INPUT_INVALID"


class LegalMatterDeadlineRegistryTransactionRequiredError(LegalMatterDeadlineRegistryError):
    """Caller did not supply one already-active transaction."""
    default_code = "D2_DEADLINE_ACTIVE_TRANSACTION_REQUIRED"


class LegalMatterDeadlineRegistryNotFoundError(LegalMatterDeadlineRegistryError):
    """No exact tenant-scoped deadline exists."""
    default_code = "D2_DEADLINE_NOT_FOUND"


class LegalMatterDeadlineRegistryConflictError(LegalMatterDeadlineRegistryError):
    """The immutable identity is bound to divergent evidence."""
    default_code = "D2_DEADLINE_CONFLICT"


class LegalMatterDeadlineRegistryPersistedRecordInvalidError(LegalMatterDeadlineRegistryError):
    """Persisted material cannot hydrate as exact D1 evidence."""
    default_code = "D2_DEADLINE_PERSISTED_RECORD_INVALID"


class LegalMatterDeadlineRegistryRetryRequiredError(LegalMatterDeadlineRegistryError):
    """Caller must restart the whole transaction from fresh state."""
    default_code = "D2_DEADLINE_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalMatterDeadlineRegistryPersistenceUnavailableError(LegalMatterDeadlineRegistryError):
    """Mongo could not safely complete the requested operation."""
    default_code = "D2_DEADLINE_PERSISTENCE_UNAVAILABLE"


def _raise(kind: type[LegalMatterDeadlineRegistryError], code: str | None = None, cause: BaseException | None = None) -> NoReturn:
    error = kind(code)
    if cause is None:
        raise error
    raise error from cause


def _mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _raise(LegalMatterDeadlineRegistryRetryRequiredError, cause=error)
    _raise(LegalMatterDeadlineRegistryPersistenceUnavailableError, cause=error)


def _collection(value: Any) -> Any:
    if value is None:
        _raise(LegalMatterDeadlineRegistryInputError, "D2_COLLECTION_REQUIRED")
    try:
        return value.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)
    except AttributeError:
        return value


def _transaction(session: Any) -> Any:
    if session is None:
        _raise(LegalMatterDeadlineRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(LegalMatterDeadlineRegistryTransactionRequiredError)
    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(LegalMatterDeadlineRegistryInputError, f"D2_{name.upper()}_INVALID")
    return value


def _hydrate(document: Mapping[str, Any]) -> LegalMatterDeadline:
    raw = dict(document)
    raw.pop("_id", None)
    try:
        return LegalMatterDeadline.from_dict(cast(Mapping[str, object], raw))
    except (TypeError, ValueError, LegalMatterDeadlineError) as error:
        _raise(LegalMatterDeadlineRegistryPersistedRecordInvalidError, cause=error)


def _rows(collection: Any, query: Mapping[str, object], *, session: Any, limit: int) -> list[Mapping[str, Any]]:
    target = _collection(collection)
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort([("due_at", ASCENDING), ("deadline_id", ASCENDING)])
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _mongo(error)
    except AttributeError as error:
        _raise(LegalMatterDeadlineRegistryInputError, "D2_COLLECTION_INTERFACE_INVALID", error)


def ensure_indexes(collection: Any) -> None:
    """Create exactly four tenant-scoped durable indexes without TTL."""
    target = _collection(collection)
    definitions = (
        ([("tenant_id", 1), ("deadline_id", 1)], True, TENANT_DEADLINE_UNIQUE_INDEX),
        ([("tenant_id", 1), ("case_matter_id", 1), ("deadline_id", 1)], False, MATTER_DEADLINE_INDEX),
        ([("tenant_id", 1), ("case_matter_id", 1), ("due_at", 1)], False, MATTER_DUE_INDEX),
        ([("tenant_id", 1), ("case_matter_id", 1), ("status", 1), ("due_at", 1)], False, MATTER_STATUS_DUE_INDEX),
    )
    try:
        for keys, unique, name in definitions:
            target.create_index(keys, unique=unique, name=name)
    except PyMongoError as error:
        _mongo(error)
    except AttributeError as error:
        _raise(LegalMatterDeadlineRegistryInputError, "D2_COLLECTION_INTERFACE_INVALID", error)


def get_deadline(tenant_id: str, deadline_id: str, collection: Any, *, session: Any) -> LegalMatterDeadline:
    """Read one exact deadline; foreign scope is bounded absence."""
    tx = _transaction(session)
    tenant, identity = _text("tenant_id", tenant_id), _text("deadline_id", deadline_id)
    rows = _rows(collection, {"tenant_id": tenant, "deadline_id": identity}, session=tx, limit=2)
    if not rows:
        _raise(LegalMatterDeadlineRegistryNotFoundError)
    if len(rows) != 1:
        _raise(LegalMatterDeadlineRegistryPersistedRecordInvalidError)
    value = _hydrate(rows[0])
    if value.tenant_id != tenant or value.deadline_id != identity:
        _raise(LegalMatterDeadlineRegistryPersistedRecordInvalidError)
    return value


def list_matter_deadlines(tenant_id: str, case_matter_id: str, collection: Any, *, session: Any) -> tuple[LegalMatterDeadline, ...]:
    """Read bounded immutable matter deadlines in deterministic order."""
    tx = _transaction(session)
    tenant, matter = _text("tenant_id", tenant_id), _text("case_matter_id", case_matter_id)
    rows = _rows(collection, {"tenant_id": tenant, "case_matter_id": matter}, session=tx, limit=MAX_MATTER_DEADLINES + 1)
    if len(rows) > MAX_MATTER_DEADLINES:
        _raise(LegalMatterDeadlineRegistryPersistedRecordInvalidError, "D2_MATTER_DEADLINE_LIMIT_EXCEEDED")
    values = tuple(_hydrate(row) for row in rows)
    if any(value.tenant_id != tenant or value.case_matter_id != matter for value in values):
        _raise(LegalMatterDeadlineRegistryPersistedRecordInvalidError)
    return tuple(sorted(values, key=lambda item: (item.due_at, item.deadline_id)))


def persist_deadline(deadline: LegalMatterDeadline, collection: Any, *, session: Any) -> LegalMatterDeadline:
    """Persist exact D1 evidence, return replay, or reject divergence.

    The method performs no update, upsert, retry, commit, abort, clock
    observation, or persisted overdue-status inference.
    """
    tx = _transaction(session)
    if type(deadline) is not LegalMatterDeadline:
        _raise(LegalMatterDeadlineRegistryInputError, "D2_DEADLINE_REQUIRED")
    target = _collection(collection)
    rows = _rows(target, {"tenant_id": deadline.tenant_id, "deadline_id": deadline.deadline_id}, session=tx, limit=2)
    if len(rows) > 1:
        _raise(LegalMatterDeadlineRegistryPersistedRecordInvalidError)
    if rows:
        durable = _hydrate(rows[0])
        if durable.fingerprint == deadline.fingerprint and durable == deadline:
            return durable
        _raise(LegalMatterDeadlineRegistryConflictError)
    try:
        target.insert_one(deadline.to_dict(), session=tx)
    except DuplicateKeyError as error:
        _raise(LegalMatterDeadlineRegistryRetryRequiredError, cause=error)
    except PyMongoError as error:
        _mongo(error)
    except AttributeError as error:
        _raise(LegalMatterDeadlineRegistryInputError, "D2_COLLECTION_INTERFACE_INVALID", error)
    return deadline


class LegalMatterDeadlineRegistry:
    """Namespaced immutable persistence API owning no deadline semantics."""
    ensure_indexes = staticmethod(ensure_indexes)
    get_deadline = staticmethod(get_deadline)
    list_matter_deadlines = staticmethod(list_matter_deadlines)
    persist_deadline = staticmethod(persist_deadline)


__all__ = ["COLLECTION", "MATTER_DEADLINE_INDEX", "MATTER_DUE_INDEX", "MATTER_STATUS_DUE_INDEX", "TENANT_DEADLINE_UNIQUE_INDEX", "VERSION", "LegalMatterDeadlineRegistry", "LegalMatterDeadlineRegistryConflictError", "LegalMatterDeadlineRegistryError", "LegalMatterDeadlineRegistryInputError", "LegalMatterDeadlineRegistryNotFoundError", "LegalMatterDeadlineRegistryPersistedRecordInvalidError", "LegalMatterDeadlineRegistryPersistenceUnavailableError", "LegalMatterDeadlineRegistryRetryRequiredError", "LegalMatterDeadlineRegistryTransactionRequiredError", "ensure_indexes", "get_deadline", "list_matter_deadlines", "persist_deadline"]

# ARTIFACT: legal_matter_deadline_registry.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY
# AUTHORITY BOUNDARY: exact D1 immutable persistence and bounded reads only; no deadline calculation, overdue, AI, filing, service, court, or financial authority
# TENANT POSTURE: every index, query, replay and write is exact tenant scoped
# FAIL-CLOSED POSTURE: missing transaction, divergence, race, corruption, invalid scope and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
