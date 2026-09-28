"""WILSY OS immutable firm Representation decision registry.

TITLE: WILSY OS Legal Client Matter Representation Firm Decision Registry
VERSION: v1.0.0-L9C11-P9-FIRM-REPRESENTATION-DECISION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist already-formed immutable firm Representation decision
         evidence with exact tenant-scoped replay identities, strict BSON
         hydration, bounded lineage history and caller-owned transactions.
         This registry never authorizes a decision or forms Representation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_representation_firm_decision_registry.py
COLLABORATION / OWNERSHIP: The P2 domain owns decision semantics and
                            fingerprints; the client-authority registry owns
                            its separate evidence; P9 owns only persistence.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P9 establishes tenant-scoped immutable persistence,
           exact replay/collision handling, BSON list normalization for the
           three P2 capability tuples, and bounded client-authority lineage
           history. It adds no IAM, currentness, lifecycle, Representation,
           Court, HTTP, Node or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only opaque domain evidence and SHA3-512
                             fingerprints are persisted; no raw PII,
                             credentials, tokens or authorization issuance.
TENANT BOUNDARY: Every identity, replay and history query includes exact
                 tenant_id; cross-tenant absence is canonical absence.
AUTHORITY BOUNDARY: Append-only firm-decision evidence persistence/read only.
                    IAM and client-authority currentness remain separate.
FINANCIAL AUTHORITY BOUNDARY: No billing, payment, settlement, trust,
                              release or execution truth; Kennel EOS remains
                              exclusive.
TRANSACTION BOUNDARY: Caller supplies an already-active Mongo transaction.
                      This registry never starts, commits, aborts, retries or
                      reconciles a whole transaction.
FAIL-CLOSED DECLARATION: Missing transactions, malformed rows, divergent
                         collisions, race ambiguity and persistence failures
                         reject without repair or inference.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    REPRESENTATION_FIRM_DECISION_FIELDS,
    LegalClientMatterRepresentationFirmDecision,
    LegalClientMatterRepresentationFirmDecisionError,
)


VERSION: Final[str] = "v1.0.0-L9C11-P9-FIRM-REPRESENTATION-DECISION-REGISTRY"
COLLECTION: Final[str] = "legal_client_matter_representation_firm_decisions"
DECISION_ID_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_firm_decision_tenant_id_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_firm_decision_tenant_fingerprint_unique"
)
IDEMPOTENCY_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_firm_decision_tenant_idempotency_unique"
)
HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_firm_decision_lineage_history"
)
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")
_BSON_TUPLE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "client_authority_scope_capabilities",
        "mandate_capabilities",
        "representation_scope_capabilities",
    }
)


class LegalClientMatterRepresentationFirmDecisionRegistryError(RuntimeError):
    """Base non-sensitive, fail-closed registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterRepresentationFirmDecisionRegistryInputError(
    LegalClientMatterRepresentationFirmDecisionRegistryError
):
    """Input or collection-interface contract failed."""


class LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError(
    LegalClientMatterRepresentationFirmDecisionRegistryError
):
    """The caller did not supply an active transaction."""


class LegalClientMatterRepresentationFirmDecisionRegistryNotFoundError(
    LegalClientMatterRepresentationFirmDecisionRegistryError
):
    """The exact tenant-scoped decision identity is absent."""


class LegalClientMatterRepresentationFirmDecisionRegistryConflictError(
    LegalClientMatterRepresentationFirmDecisionRegistryError
):
    """An immutable replay identity collides with divergent evidence."""


class LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError(
    LegalClientMatterRepresentationFirmDecisionRegistryError
):
    """Durable data failed strict schema, BSON, scope or fingerprint checks."""


class LegalClientMatterRepresentationFirmDecisionRegistryRetryRequiredError(
    LegalClientMatterRepresentationFirmDecisionRegistryError
):
    """A duplicate or transient race requires a fresh caller transaction."""


class LegalClientMatterRepresentationFirmDecisionRegistryPersistenceUnavailableError(
    LegalClientMatterRepresentationFirmDecisionRegistryError
):
    """Mongo persistence failed without a safe replay classification."""


def _fail(
    error_type: type[LegalClientMatterRepresentationFirmDecisionRegistryError],
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
            LegalClientMatterRepresentationFirmDecisionRegistryRetryRequiredError,
            "L9C11_P9_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    _fail(
        LegalClientMatterRepresentationFirmDecisionRegistryPersistenceUnavailableError,
        "L9C11_P9_PERSISTENCE_UNAVAILABLE",
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
            LegalClientMatterRepresentationFirmDecisionRegistryPersistenceUnavailableError,
            "L9C11_P9_PERSISTENCE_UNAVAILABLE",
            error,
        )


def _active_transaction(session: Any) -> Any:
    """Require an active caller transaction without starting one."""
    if session is None:
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError,
            "L9C11_P9_ACTIVE_TRANSACTION_REQUIRED",
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError,
            "L9C11_P9_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError,
            "L9C11_P9_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _identity(name: str, value: object) -> str:
    """Validate one opaque lookup value without coercion or value leakage."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryInputError,
            f"L9C11_P9_{name.upper()}_INVALID",
        )
    return value


def _bounded_limit(limit: object) -> int:
    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or not 0 < limit <= MAX_HISTORY_READS
    ):
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryInputError,
            "L9C11_P9_LIMIT_INVALID",
        )
    return limit


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    """Remove Mongo identity and normalize only known BSON capability arrays."""
    raw = dict(document)
    raw.pop("_id", None)
    for field in _BSON_TUPLE_FIELDS:
        value = raw.get(field)
        if isinstance(value, list):
            raw[field] = tuple(value)
        elif not isinstance(value, tuple):
            _fail(
                LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
                "L9C11_P9_PERSISTED_RECORD_INVALID",
            )
    return raw


def _hydrate(
    document: Mapping[str, object],
) -> LegalClientMatterRepresentationFirmDecision:
    """Reconstruct only the exact P2 schema and verify its integrity."""
    raw = _canonical(document)
    if set(raw) != set(REPRESENTATION_FIRM_DECISION_FIELDS):
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C11_P9_PERSISTED_RECORD_INVALID",
        )
    try:
        value = LegalClientMatterRepresentationFirmDecision.from_dict(
            cast(Mapping[str, object], raw)
        )
    except (TypeError, ValueError, LegalClientMatterRepresentationFirmDecisionError) as error:
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C11_P9_PERSISTED_RECORD_INVALID",
            error,
        )
    if value.to_dict() != raw:
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C11_P9_PERSISTED_RECORD_INVALID",
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
            LegalClientMatterRepresentationFirmDecisionRegistryInputError,
            "L9C11_P9_COLLECTION_INTERFACE_INVALID",
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
            LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C11_P9_DUPLICATE_IDENTITY",
        )
    return rows[0] if rows else None


def ensure_indexes(collection: Any | None = None) -> None:
    """Create exact tenant identities and deterministic lineage history indexes."""
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
                ("representation_authority_id", ASCENDING),
                ("representation_authority_fingerprint", ASCENDING),
                ("representative_principal_id", ASCENDING),
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
            LegalClientMatterRepresentationFirmDecisionRegistryInputError,
            "L9C11_P9_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _collision_queries(
    value: LegalClientMatterRepresentationFirmDecision,
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
    value: LegalClientMatterRepresentationFirmDecision,
    document: Mapping[str, object],
    *,
    session: Any,
) -> LegalClientMatterRepresentationFirmDecision:
    """Classify a duplicate-key race without turning arbitrary errors into success."""
    for query, label in _collision_queries(value):
        row = _one(target, query, session=session)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == dict(document):
            return existing
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryConflictError,
            f"L9C11_P9_{label}_COLLISION",
        )
    _fail(
        LegalClientMatterRepresentationFirmDecisionRegistryRetryRequiredError,
        "L9C11_P9_WHOLE_TRANSACTION_RETRY_REQUIRED",
    )


def persist_firm_decision(
    value: LegalClientMatterRepresentationFirmDecision,
    decision_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationFirmDecision:
    """Append one exact immutable decision or return its exact replay.

    The caller owns the transaction. No client-authority, IAM, currentness or
    Representation lookup is performed; divergent identities fail closed.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterRepresentationFirmDecision:
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryInputError,
            "L9C11_P9_FIRM_DECISION_REQUIRED",
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
            LegalClientMatterRepresentationFirmDecisionRegistryConflictError,
            f"L9C11_P9_{label}_COLLISION",
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
            LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C11_P9_POST_WRITE_RECONCILIATION_FAILED",
        )
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C11_P9_POST_WRITE_RECONCILIATION_FAILED",
        )
    return result


def get_firm_decision(
    tenant_id: str,
    decision_id: str,
    decision_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationFirmDecision:
    """Read one exact decision identity under exact tenant scope."""
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
            LegalClientMatterRepresentationFirmDecisionRegistryNotFoundError,
            "L9C11_P9_FIRM_DECISION_NOT_FOUND",
        )
    return _hydrate(row)


def get_firm_decision_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    decision_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationFirmDecision:
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
            LegalClientMatterRepresentationFirmDecisionRegistryNotFoundError,
            "L9C11_P9_FIRM_DECISION_NOT_FOUND",
        )
    return _hydrate(row)


def get_firm_decision_by_idempotency_key(
    tenant_id: str,
    idempotency_key: str,
    decision_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationFirmDecision:
    """Read one exact replay identity under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(decision_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "idempotency_key": _identity("idempotency_key", idempotency_key),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryNotFoundError,
            "L9C11_P9_FIRM_DECISION_NOT_FOUND",
        )
    return _hydrate(row)


def list_firm_decisions_for_context(
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    representation_authority_id: str,
    representation_authority_fingerprint: str,
    representative_principal_id: str,
    decision_collection: Any | None = None,
    *,
    session: Any = None,
    limit: int = MAX_HISTORY_READS,
) -> tuple[LegalClientMatterRepresentationFirmDecision, ...]:
    """Return bounded exact client-authority lineage history.

    The registry preserves all immutable rows in deterministic order. It does
    not select a current decision, infer eligibility or form Representation.
    """
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
            "representation_authority_id",
            _identity("representation_authority_id", representation_authority_id),
        ),
        (
            "representation_authority_fingerprint",
            _identity(
                "representation_authority_fingerprint",
                representation_authority_fingerprint,
            ),
        ),
        (
            "representative_principal_id",
            _identity("representative_principal_id", representative_principal_id),
        ),
    )
    query = {"tenant_id": _identity("tenant_id", tenant_id), **dict(values)}
    rows = _rows(_target(decision_collection), query, session=tx, limit=bounded + 1)
    if len(rows) > bounded:
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C11_P9_READ_LIMIT_EXCEEDED",
        )
    decisions = tuple(_hydrate(row) for row in rows)
    expected = (("tenant_id", query["tenant_id"]),) + values
    if any(
        any(getattr(decision, field) != expected_value for field, expected_value in expected)
        for decision in decisions
    ):
        _fail(
            LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
            "L9C11_P9_HISTORY_SCOPE_INVALID",
        )
    return decisions


class LegalClientMatterRepresentationFirmDecisionRegistry:
    """Static namespace for immutable decision persistence and reads only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_firm_decision = staticmethod(persist_firm_decision)
    get_firm_decision = staticmethod(get_firm_decision)
    get_firm_decision_by_fingerprint = staticmethod(get_firm_decision_by_fingerprint)
    get_firm_decision_by_idempotency_key = staticmethod(
        get_firm_decision_by_idempotency_key
    )
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
    "LegalClientMatterRepresentationFirmDecisionRegistry",
    "LegalClientMatterRepresentationFirmDecisionRegistryConflictError",
    "LegalClientMatterRepresentationFirmDecisionRegistryError",
    "LegalClientMatterRepresentationFirmDecisionRegistryInputError",
    "LegalClientMatterRepresentationFirmDecisionRegistryNotFoundError",
    "LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError",
    "LegalClientMatterRepresentationFirmDecisionRegistryPersistenceUnavailableError",
    "LegalClientMatterRepresentationFirmDecisionRegistryRetryRequiredError",
    "LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_firm_decision",
    "get_firm_decision_by_fingerprint",
    "get_firm_decision_by_idempotency_key",
    "list_firm_decisions_for_context",
    "persist_firm_decision",
]


# ARTIFACT: legal_client_matter_representation_firm_decision_registry.py
# VERSION: v1.0.0-L9C11-P9-FIRM-REPRESENTATION-DECISION-REGISTRY
# AUTHORITY BOUNDARY: immutable firm Representation decision persistence/read only
# TENANT POSTURE: every identity, replay and lineage query is tenant-scoped
# FAIL-CLOSED POSTURE: strict transaction, BSON hydration, collision, race and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
