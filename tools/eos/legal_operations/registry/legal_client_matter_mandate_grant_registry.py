"""Durable formation registry for immutable client mandate grants.

TITLE: WILSY OS Legal Client Matter Mandate Grant Registry
VERSION: v1.0.0-L9B7-CLIENT-MANDATE-GRANT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and read exact LegalClientMatterMandateGrant formation
         evidence with tenant-scoped replay, strict hydration and caller-owned
         Mongo transaction semantics. This registry never resolves lifecycle
         currentness, revokes, supersedes, or forms a mandate.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_mandate_grant_registry.py
COLLABORATION / OWNERSHIP: LegalClientMatterMandateGrant owns canonical
                            immutable value and fingerprint semantics; this
                            registry owns only append-only formation durability
                            and exact tenant-scoped reads. Lifecycle registry,
                            currentness, acknowledgment, mandate, Engagement,
                            Representation, Court and IAM remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B7-CLIENT-MANDATE-GRANT-REGISTRY establishes the dedicated
           formation collection, tenant-scoped grant/fingerprint/idempotency
           uniqueness, strict domain hydration, deterministic replay, bounded
           historical reads, majority durability and caller-owned transactions.
           No TTL, lifecycle, currentness, mutation or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only canonical opaque grant fields and fingerprints
                             are persisted; no raw PII, credentials, tokens or
                             browser state is introduced.
TENANT BOUNDARY: Every write, replay identity and read begins with exact
                 tenant_id; no global grant-id or cross-tenant existence oracle.
AUTHORITY BOUNDARY: Formation evidence persistence/read only. Expiry is stored
                    historically; lifecycle and current usability are not
                    inferred or answered.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, release or execution;
                              Kennel EOS remains exclusive financial authority.
TRANSACTION BOUNDARY: Caller supplies and owns an active Mongo session and
                      transaction; this registry never opens, commits, aborts,
                      retries, or reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing session, malformed rows, divergent replay,
                         duplicate races, schema drift and persistence failure
                         reject without repair or destructive action.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    MANDATE_GRANT_FIELDS,
    LegalClientMatterMandateGrant,
    LegalClientMatterMandateGrantError,
)


VERSION: Final[str] = "v1.0.0-L9B7-CLIENT-MANDATE-GRANT-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_mandate_grants"
GRANT_ID_INDEX_NAME: Final[str] = "legal_client_matter_grant_tenant_grant_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "legal_client_matter_grant_tenant_fingerprint_unique"
IDEMPOTENCY_INDEX_NAME: Final[str] = "legal_client_matter_grant_tenant_idempotency_unique"
MATTER_CLIENT_INDEX_NAME: Final[str] = "legal_client_matter_grant_tenant_matter_client_effective"
MATTER_CLIENT_SCOPE_INDEX_NAME: Final[str] = "legal_client_matter_grant_tenant_matter_client_scope_effective"
MAX_GRANT_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientMatterMandateGrantRegistryError(RuntimeError):
    """Base non-sensitive, fail-closed formation-registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterMandateGrantRegistryInputError(LegalClientMatterMandateGrantRegistryError):
    """Malformed value, query, collection, or limit."""


class LegalClientMatterMandateGrantRegistryTransactionRequiredError(LegalClientMatterMandateGrantRegistryError):
    """An active caller-owned transaction was not supplied."""


class LegalClientMatterMandateGrantRegistryNotFoundError(LegalClientMatterMandateGrantRegistryError):
    """The exact tenant-scoped formation identity is absent."""


class LegalClientMatterMandateGrantRegistryConflictError(LegalClientMatterMandateGrantRegistryError):
    """An immutable formation identity collides with divergent evidence."""


class LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError(LegalClientMatterMandateGrantRegistryError):
    """Durable data failed strict grant hydration or correlation checks."""


class LegalClientMatterMandateGrantRegistryRetryRequiredError(LegalClientMatterMandateGrantRegistryError):
    """A duplicate race requires a caller-owned whole-transaction restart."""


class LegalClientMatterMandateGrantRegistryPersistenceUnavailableError(LegalClientMatterMandateGrantRegistryError):
    """Mongo persistence failed without a safe replay classification."""


def _fail(error_type: type[LegalClientMatterMandateGrantRegistryError], code: str, cause: BaseException | None = None) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _fail(LegalClientMatterMandateGrantRegistryRetryRequiredError, "L9B7_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    _fail(LegalClientMatterMandateGrantRegistryPersistenceUnavailableError, "L9B7_PERSISTENCE_UNAVAILABLE", error)


def _target(collection: Any) -> Any:
    if collection is None:
        _fail(LegalClientMatterMandateGrantRegistryInputError, "L9B7_COLLECTION_REQUIRED")
    try:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN, codec_options=CodecOptions(tz_aware=True))
    except AttributeError:
        return collection


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail(LegalClientMatterMandateGrantRegistryTransactionRequiredError, "L9B7_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail(LegalClientMatterMandateGrantRegistryTransactionRequiredError, "L9B7_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(LegalClientMatterMandateGrantRegistryInputError, f"L9B7_{name.upper()}_INVALID")
    return value


def _rows(collection: Any, query: Mapping[str, object], *, session: Any, limit: int) -> list[Mapping[str, Any]]:
    target = _target(collection)
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort([("effective_from", ASCENDING), ("occurred_at", ASCENDING), ("fingerprint", ASCENDING), ("client_grant_id", ASCENDING)])
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalClientMatterMandateGrantRegistryInputError, "L9B7_COLLECTION_INTERFACE_INVALID", error)


def _one(collection: Any, query: Mapping[str, object], *, session: Any) -> Mapping[str, Any] | None:
    rows = _rows(collection, query, session=session, limit=2)
    if len(rows) > 1:
        _fail(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError, "L9B7_DUPLICATE_IDENTITY")
    return rows[0] if rows else None


def _hydrate(document: Mapping[str, Any]) -> LegalClientMatterMandateGrant:
    if not isinstance(document, Mapping):
        _fail(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError, "L9B7_RECORD_INVALID")
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != set(MANDATE_GRANT_FIELDS):
        _fail(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError, "L9B7_RECORD_SCHEMA_INVALID")
    try:
        value = LegalClientMatterMandateGrant.from_dict(cast(Mapping[str, object], raw))
    except (TypeError, ValueError, LegalClientMatterMandateGrantError) as error:
        _fail(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError, "L9B7_GRANT_PAYLOAD_INVALID", error)
    if value.to_dict() != raw:
        _fail(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError, "L9B7_RECORD_CORRELATION_INVALID")
    return value


def ensure_indexes(collection: Any) -> None:
    """Create deterministic formation indexes; no TTL or lifecycle indexes."""
    target = _target(collection)
    indexes = (
        ([ ("tenant_id", ASCENDING), ("client_grant_id", ASCENDING) ], True, GRANT_ID_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("fingerprint", ASCENDING) ], True, FINGERPRINT_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("idempotency_key", ASCENDING) ], True, IDEMPOTENCY_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("client_party_id", ASCENDING), ("effective_from", ASCENDING), ("occurred_at", ASCENDING), ("fingerprint", ASCENDING) ], False, MATTER_CLIENT_INDEX_NAME),
        ([ ("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("client_party_id", ASCENDING), ("scope_fingerprint", ASCENDING), ("effective_from", ASCENDING), ("fingerprint", ASCENDING) ], False, MATTER_CLIENT_SCOPE_INDEX_NAME),
    )
    try:
        for keys, unique, name in indexes:
            target.create_index(keys, unique=unique, name=name)
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(LegalClientMatterMandateGrantRegistryInputError, "L9B7_COLLECTION_INTERFACE_INVALID", error)


def _collision_queries(value: LegalClientMatterMandateGrant) -> tuple[dict[str, object], ...]:
    return (
        {"tenant_id": value.tenant_id, "client_grant_id": value.client_grant_id},
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        {"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key},
    )


def persist_grant(value: LegalClientMatterMandateGrant, grant_collection: Any, *, session: Any) -> LegalClientMatterMandateGrant:
    """Insert one immutable grant or return its exact tenant-scoped replay.

    The caller owns the active transaction. Any same-identity divergent
    payload fails closed; duplicate races require a whole transaction retry.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterMandateGrant:
        _fail(LegalClientMatterMandateGrantRegistryInputError, "L9B7_GRANT_REQUIRED")
    target = _target(grant_collection)
    document = value.to_dict()
    labels = ("GRANT_ID", "FINGERPRINT", "IDEMPOTENCY_KEY")
    for query, label in zip(_collision_queries(value), labels):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(LegalClientMatterMandateGrantRegistryConflictError, f"L9B7_{label}_COLLISION")
    try:
        target.insert_one(dict(document), session=tx)
    except DuplicateKeyError as error:
        _fail(LegalClientMatterMandateGrantRegistryRetryRequiredError, "L9B7_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except PyMongoError as error:
        _raise_mongo(error)
    persisted = _one(target, {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}, session=tx)
    if persisted is None:
        _fail(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError, "L9B7_POST_WRITE_RECONCILIATION_FAILED")
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError, "L9B7_POST_WRITE_RECONCILIATION_FAILED")
    return result


def _bounded_limit(limit: object) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 < limit <= MAX_GRANT_READS:
        _fail(LegalClientMatterMandateGrantRegistryInputError, "L9B7_LIMIT_INVALID")
    return limit


def get_grant(tenant_id: str, client_grant_id: str, grant_collection: Any, *, session: Any) -> LegalClientMatterMandateGrant:
    """Read one exact formation artifact under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(grant_collection, {"tenant_id": _text("tenant_id", tenant_id), "client_grant_id": _text("client_grant_id", client_grant_id)}, session=tx)
    if row is None:
        _fail(LegalClientMatterMandateGrantRegistryNotFoundError, "L9B7_GRANT_NOT_FOUND")
    return _hydrate(row)


def get_grant_by_fingerprint(tenant_id: str, fingerprint: str, grant_collection: Any, *, session: Any) -> LegalClientMatterMandateGrant:
    """Read one exact fingerprint under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(grant_collection, {"tenant_id": _text("tenant_id", tenant_id), "fingerprint": _text("fingerprint", fingerprint)}, session=tx)
    if row is None:
        _fail(LegalClientMatterMandateGrantRegistryNotFoundError, "L9B7_GRANT_NOT_FOUND")
    return _hydrate(row)


def list_grants_for_matter_client(tenant_id: str, case_matter_id: str, client_party_id: str, grant_collection: Any, *, session: Any, limit: int = MAX_GRANT_READS) -> tuple[LegalClientMatterMandateGrant, ...]:
    """List bounded formation history deterministically, including expired grants."""
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    rows = _rows(grant_collection, {"tenant_id": _text("tenant_id", tenant_id), "case_matter_id": _text("case_matter_id", case_matter_id), "client_party_id": _text("client_party_id", client_party_id)}, session=tx, limit=bounded + 1)
    if len(rows) > bounded:
        _fail(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError, "L9B7_READ_LIMIT_EXCEEDED")
    values = tuple(_hydrate(row) for row in rows)
    if any(value.tenant_id != tenant_id or value.case_matter_id != case_matter_id or value.client_party_id != client_party_id for value in values):
        _fail(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError, "L9B7_SCOPE_CORRELATION_INVALID")
    return values


class LegalClientMatterMandateGrantRegistry:
    """Static namespace for immutable formation persistence and reads only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_grant = staticmethod(persist_grant)
    get_grant = staticmethod(get_grant)
    get_grant_by_fingerprint = staticmethod(get_grant_by_fingerprint)
    list_grants_for_matter_client = staticmethod(list_grants_for_matter_client)


__all__ = [
    "COLLECTION", "FINGERPRINT_INDEX_NAME", "GRANT_ID_INDEX_NAME",
    "IDEMPOTENCY_INDEX_NAME", "MATTER_CLIENT_INDEX_NAME",
    "MATTER_CLIENT_SCOPE_INDEX_NAME", "MAX_GRANT_READS", "READ_CONCERN",
    "VERSION", "WRITE_CONCERN", "LegalClientMatterMandateGrantRegistry",
    "LegalClientMatterMandateGrantRegistryConflictError",
    "LegalClientMatterMandateGrantRegistryError",
    "LegalClientMatterMandateGrantRegistryInputError",
    "LegalClientMatterMandateGrantRegistryNotFoundError",
    "LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError",
    "LegalClientMatterMandateGrantRegistryPersistenceUnavailableError",
    "LegalClientMatterMandateGrantRegistryRetryRequiredError",
    "LegalClientMatterMandateGrantRegistryTransactionRequiredError",
    "ensure_indexes", "get_grant", "get_grant_by_fingerprint",
    "list_grants_for_matter_client", "persist_grant",
]


# ARTIFACT: legal_client_matter_mandate_grant_registry.py
# VERSION: v1.0.0-L9B7-CLIENT-MANDATE-GRANT-REGISTRY
# AUTHORITY BOUNDARY: immutable grant-formation persistence/read only
# TENANT POSTURE: every identity, replay query and read is tenant-scoped
# FAIL-CLOSED POSTURE: strict hydration, collision, race and persistence rejection; no TTL
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
