"""WILSY OS durable client Representation-authority registry.

TITLE: WILSY OS Legal Client Matter Representation Authority Registry
VERSION: v1.0.0-L9C11-P7-CLIENT-REPRESENTATION-AUTHORITY-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable client Representation-authority evidence with exact
         tenant-scoped replay identities, strict domain hydration, bounded
         lineage history and caller-owned Mongo transaction semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_representation_authority_registry.py
COLLABORATION / OWNERSHIP: P1 owns authority value semantics and fingerprints;
                            P7 owns append-only durability and exact reads.
                            IAM, currentness, lifecycle, firm decision,
                            Representation formation, Court and finance remain
                            separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P7 establishes tenant-scoped authority, fingerprint
           and idempotency identities, deterministic exact-lineage history,
           strict hydration, duplicate-race reconciliation and caller-owned
           transaction semantics. P7R1 adds only BSON list-to-tuple
           canonicalization for the two immutable capability arrays. It creates
           no IAM, currentness, lifecycle, firm-decision, Representation,
           Court or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only the canonical opaque domain payload and its
                             SHA3-512 fingerprint are persisted. No raw PII,
                             credentials, tokens or browser claims are added.
TENANT BOUNDARY: Every write, replay probe and read begins with exact
                 tenant_id; no cross-tenant fallback or existence oracle exists.
AUTHORITY BOUNDARY: Immutable client appointment evidence persistence/read
                    only. This registry never authenticates or authorizes an
                    appointing actor and never interprets decision currentness.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
TRANSACTION BOUNDARY: Caller supplies and owns an already-active transaction.
                      This module never starts, commits, aborts, retries or
                      reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing transactions, malformed rows, divergent
                         collisions, duplicate races, query overflow and
                         persistence failures reject without repair or deletion.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    REPRESENTATION_AUTHORITY_FIELDS,
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityError,
)


VERSION: Final[str] = "v1.0.0-L9C11-P7-CLIENT-REPRESENTATION-AUTHORITY-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_representation_authorities"
AUTHORITY_ID_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_authority_tenant_id_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_authority_tenant_fingerprint_unique"
)
IDEMPOTENCY_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_authority_tenant_idempotency_unique"
)
HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_authority_lineage_history"
)
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")
_BSON_TUPLE_FIELDS: Final[frozenset[str]] = frozenset(
    {"mandate_capabilities", "representation_scope_capabilities"}
)


class LegalClientMatterRepresentationAuthorityRegistryError(RuntimeError):
    """Base non-sensitive fail-closed registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterRepresentationAuthorityRegistryInputError(
    LegalClientMatterRepresentationAuthorityRegistryError
):
    """Malformed input or unsupported collection interface."""


class LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError(
    LegalClientMatterRepresentationAuthorityRegistryError
):
    """The caller did not provide an already-active transaction."""


class LegalClientMatterRepresentationAuthorityRegistryNotFoundError(
    LegalClientMatterRepresentationAuthorityRegistryError
):
    """The exact tenant-scoped authority identity is absent."""


class LegalClientMatterRepresentationAuthorityRegistryConflictError(
    LegalClientMatterRepresentationAuthorityRegistryError
):
    """An immutable replay identity collides with divergent evidence."""


class LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError(
    LegalClientMatterRepresentationAuthorityRegistryError
):
    """Durable data failed strict schema, fingerprint or scope validation."""


class LegalClientMatterRepresentationAuthorityRegistryRetryRequiredError(
    LegalClientMatterRepresentationAuthorityRegistryError
):
    """A duplicate or transient race requires a fresh caller transaction."""


class LegalClientMatterRepresentationAuthorityRegistryPersistenceUnavailableError(
    LegalClientMatterRepresentationAuthorityRegistryError
):
    """Mongo persistence failed without a safe replay classification."""


def _fail(
    error_type: type[LegalClientMatterRepresentationAuthorityRegistryError],
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
            LegalClientMatterRepresentationAuthorityRegistryRetryRequiredError,
            "L9C11_P7_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    _fail(
        LegalClientMatterRepresentationAuthorityRegistryPersistenceUnavailableError,
        "L9C11_P7_PERSISTENCE_UNAVAILABLE",
        error,
    )


def _target(collection: Any | None) -> Any:
    """Require the caller to supply the canonical collection explicitly."""
    if collection is None:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryInputError,
            "L9C11_P7_COLLECTION_REQUIRED",
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
    """Require an active caller transaction without starting one."""
    if session is None:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError,
            "L9C11_P7_ACTIVE_TRANSACTION_REQUIRED",
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError,
            "L9C11_P7_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError,
            "L9C11_P7_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _identity(name: str, value: object) -> str:
    """Validate an opaque lookup value without coercion or value leakage."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryInputError,
            f"L9C11_P7_{name.upper()}_INVALID",
        )
    return value


def _bounded_limit(limit: object) -> int:
    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or not 0 < limit <= MAX_HISTORY_READS
    ):
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryInputError,
            "L9C11_P7_LIMIT_INVALID",
        )
    return limit


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    """Normalize only BSON arrays that represent P1 immutable tuples."""
    raw = dict(document)
    raw.pop("_id", None)
    for field in _BSON_TUPLE_FIELDS:
        value = raw.get(field)
        if isinstance(value, list):
            raw[field] = tuple(value)
    return raw


def _hydrate(
    document: Mapping[str, object],
) -> LegalClientMatterRepresentationAuthority:
    """Reconstruct only the exact published P1 domain schema."""
    raw = _canonical(document)
    if set(raw) != set(REPRESENTATION_AUTHORITY_FIELDS):
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError,
            "L9C11_P7_PERSISTED_RECORD_INVALID",
        )
    try:
        value = LegalClientMatterRepresentationAuthority.from_dict(
            cast(Mapping[str, object], raw)
        )
    except (TypeError, ValueError, LegalClientMatterRepresentationAuthorityError) as error:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError,
            "L9C11_P7_PERSISTED_RECORD_INVALID",
            error,
        )
    if value.to_dict() != raw:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError,
            "L9C11_P7_PERSISTED_RECORD_INVALID",
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
                    ("authority_id", ASCENDING),
                ]
            )
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryInputError,
            "L9C11_P7_COLLECTION_INTERFACE_INVALID",
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
            LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError,
            "L9C11_P7_DUPLICATE_IDENTITY",
        )
    return rows[0] if rows else None


def ensure_indexes(collection: Any | None = None) -> None:
    """Create deterministic replay/history indexes; never TTL or currentness."""
    indexes = (
        (
            [("tenant_id", ASCENDING), ("authority_id", ASCENDING)],
            True,
            AUTHORITY_ID_INDEX_NAME,
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
                ("representative_principal_id", ASCENDING),
                ("effective_from", ASCENDING),
                ("occurred_at", ASCENDING),
                ("fingerprint", ASCENDING),
                ("authority_id", ASCENDING),
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
            LegalClientMatterRepresentationAuthorityRegistryInputError,
            "L9C11_P7_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _collision_queries(
    value: LegalClientMatterRepresentationAuthority,
) -> tuple[tuple[dict[str, object], str], ...]:
    return (
        (
            {"tenant_id": value.tenant_id, "authority_id": value.authority_id},
            "AUTHORITY_ID",
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
    value: LegalClientMatterRepresentationAuthority,
    document: Mapping[str, object],
    *,
    session: Any,
) -> LegalClientMatterRepresentationAuthority:
    """Classify a duplicate-key race without turning arbitrary errors into success."""
    for query, label in _collision_queries(value):
        row = _one(target, query, session=session)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == dict(document):
            return existing
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryConflictError,
            f"L9C11_P7_{label}_COLLISION",
        )
    _fail(
        LegalClientMatterRepresentationAuthorityRegistryRetryRequiredError,
        "L9C11_P7_WHOLE_TRANSACTION_RETRY_REQUIRED",
    )


def persist_representation_authority(
    value: LegalClientMatterRepresentationAuthority,
    authority_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationAuthority:
    """Append one exact authority or return its immutable replay.

    Only an exact tenant-scoped canonical replay is accepted. The caller owns
    transaction lifecycle and any whole-transaction retry. No IAM, currentness,
    lifecycle or downstream authority is calculated here.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterRepresentationAuthority:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryInputError,
            "L9C11_P7_REPRESENTATION_AUTHORITY_REQUIRED",
        )
    document = value.to_dict()
    target = _target(authority_collection)
    for query, label in _collision_queries(value):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryConflictError,
            f"L9C11_P7_{label}_COLLISION",
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
            LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError,
            "L9C11_P7_POST_WRITE_RECONCILIATION_FAILED",
        )
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError,
            "L9C11_P7_POST_WRITE_RECONCILIATION_FAILED",
        )
    return result


def get_representation_authority(
    tenant_id: str,
    authority_id: str,
    authority_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationAuthority:
    """Read one exact authority identity under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(authority_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "authority_id": _identity("authority_id", authority_id),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryNotFoundError,
            "L9C11_P7_REPRESENTATION_AUTHORITY_NOT_FOUND",
        )
    return _hydrate(row)


def get_representation_authority_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    authority_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationAuthority:
    """Read one exact fingerprint under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(authority_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "fingerprint": _identity("fingerprint", fingerprint),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryNotFoundError,
            "L9C11_P7_REPRESENTATION_AUTHORITY_NOT_FOUND",
        )
    return _hydrate(row)


def get_representation_authority_by_idempotency_key(
    tenant_id: str,
    idempotency_key: str,
    authority_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationAuthority:
    """Read one exact replay identity under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(authority_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "idempotency_key": _identity("idempotency_key", idempotency_key),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryNotFoundError,
            "L9C11_P7_REPRESENTATION_AUTHORITY_NOT_FOUND",
        )
    return _hydrate(row)


def list_representation_authorities_for_context(
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    representative_principal_id: str,
    authority_collection: Any | None = None,
    *,
    session: Any = None,
    limit: int = MAX_HISTORY_READS,
) -> tuple[LegalClientMatterRepresentationAuthority, ...]:
    """Return bounded exact-lineage history without calculating currentness."""
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
        (
            "representative_principal_id",
            _identity("representative_principal_id", representative_principal_id),
        ),
    )
    query = {"tenant_id": _identity("tenant_id", tenant_id), **dict(values)}
    rows = _rows(_target(authority_collection), query, session=tx, limit=bounded + 1)
    if len(rows) > bounded:
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError,
            "L9C11_P7_READ_LIMIT_EXCEEDED",
        )
    authorities = tuple(_hydrate(row) for row in rows)
    expected = (("tenant_id", query["tenant_id"]),) + values
    if any(
        any(getattr(authority, field) != expected_value for field, expected_value in expected)
        for authority in authorities
    ):
        _fail(
            LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError,
            "L9C11_P7_HISTORY_SCOPE_INVALID",
        )
    return authorities


class LegalClientMatterRepresentationAuthorityRegistry:
    """Static namespace for immutable authority persistence and reads only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_representation_authority = staticmethod(persist_representation_authority)
    get_representation_authority = staticmethod(get_representation_authority)
    get_representation_authority_by_fingerprint = staticmethod(
        get_representation_authority_by_fingerprint
    )
    get_representation_authority_by_idempotency_key = staticmethod(
        get_representation_authority_by_idempotency_key
    )
    list_representation_authorities_for_context = staticmethod(
        list_representation_authorities_for_context
    )


__all__ = [
    "AUTHORITY_ID_INDEX_NAME",
    "COLLECTION",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME",
    "IDEMPOTENCY_INDEX_NAME",
    "MAX_HISTORY_READS",
    "READ_CONCERN",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientMatterRepresentationAuthorityRegistry",
    "LegalClientMatterRepresentationAuthorityRegistryConflictError",
    "LegalClientMatterRepresentationAuthorityRegistryError",
    "LegalClientMatterRepresentationAuthorityRegistryInputError",
    "LegalClientMatterRepresentationAuthorityRegistryNotFoundError",
    "LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError",
    "LegalClientMatterRepresentationAuthorityRegistryPersistenceUnavailableError",
    "LegalClientMatterRepresentationAuthorityRegistryRetryRequiredError",
    "LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_representation_authority",
    "get_representation_authority_by_fingerprint",
    "get_representation_authority_by_idempotency_key",
    "list_representation_authorities_for_context",
    "persist_representation_authority",
]


# ARTIFACT: legal_client_matter_representation_authority_registry.py
# VERSION: v1.0.0-L9C11-P7-CLIENT-REPRESENTATION-AUTHORITY-REGISTRY
# AUTHORITY BOUNDARY: immutable client authority persistence/read only
# TENANT POSTURE: every identity, replay and history query is tenant-scoped
# FAIL-CLOSED POSTURE: strict transaction, hydration, collision, race and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
