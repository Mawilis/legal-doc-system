"""WILSY OS durable client Representation-authorization evidence registry.

TITLE: WILSY OS Legal Client Matter Representation Authorization Evidence Registry
VERSION: v1.0.0-L9C11-P18-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable P17 client self-appointment authorization evidence
         with exact tenant-scoped replay identities, strict BSON hydration,
         bounded appointment-lineage history and caller-owned transactions.
         This registry never evaluates authority or creates new authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_representation_authorization_evidence_registry.py
COLLABORATION / OWNERSHIP: P17 owns the immutable evidence value and its
                            fingerprints; P18 owns append-only durability and
                            exact reads. P1, IAM, currentness, orchestration,
                            Representation formation, Court and finance remain
                            separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P18 establishes explicit-collection persistence,
           tenant-scoped evidence/fingerprint/idempotency identities,
           deterministic appointment-lineage history, strict BSON hydration,
           exact replay/collision handling and caller-owned transactions.
           It adds no authority, currentness, consumption, IAM, Court,
           financial, HTTP, UI or Node behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only the exact P17 serialized evidence payload is
                             persisted. No secrets, credentials, tokens or raw
                             foreign authority objects are added.
TENANT BOUNDARY: Every write, replay probe, lookup and history query includes
                 exact tenant_id; cross-tenant fallback is impossible.
AUTHORITY BOUNDARY: Immutable client self-appointment evidence persistence and
                    reads only. This registry does not authenticate, authorize,
                    select roles, evaluate currentness or construct P1.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
TRANSACTION BOUNDARY: Caller supplies and owns an already-active transaction.
                      This module never starts, commits, aborts or retries a
                      whole transaction.
FAIL-CLOSED DECLARATION: Missing transactions, malformed rows, divergent
                         collisions, duplicate races, query overflow and
                         persistence failures reject without inference, repair
                         or deletion.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_representation_authorization_evidence import (
    REPRESENTATION_AUTHORIZATION_EVIDENCE_FIELDS,
    LegalClientMatterRepresentationAuthorizationEvidence,
    LegalClientMatterRepresentationAuthorizationEvidenceError,
)


VERSION: Final[str] = (
    "v1.0.0-L9C11-P18-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-REGISTRY"
)
COLLECTION: Final[str] = "legal_client_matter_representation_authorization_evidence"
EVIDENCE_ID_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_authorization_evidence_tenant_id_unique"
)
AUTHORIZATION_EVIDENCE_ID_INDEX_NAME: Final[str] = EVIDENCE_ID_INDEX_NAME
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_authorization_evidence_tenant_fingerprint_unique"
)
IDEMPOTENCY_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_authorization_evidence_tenant_idempotency_unique"
)
HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_representation_authorization_evidence_lineage_history"
)
MAX_HISTORY_READS: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")
_BSON_TUPLE_FIELDS: Final[tuple[str, ...]] = (
    "mandate_capabilities",
    "representation_scope_capabilities",
)
_HISTORY_FILTER_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_identity_fingerprint",
    "appointing_principal_id",
    "acting_capacity_id",
    "acting_capacity_fingerprint",
    "engagement_id",
    "engagement_fingerprint",
    "mandate_id",
    "mandate_fingerprint",
    "representative_principal_id",
    "representative_role",
)
HISTORY_INDEX_FIELDS: Final[tuple[str, ...]] = _HISTORY_FILTER_FIELDS + (
    "effective_from",
    "occurred_at",
    "fingerprint",
    "evidence_id",
)


class LegalClientMatterRepresentationAuthorizationEvidenceRegistryError(
    RuntimeError
):
    """Base non-sensitive, fail-closed registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError(
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryError
):
    """Malformed input or unsupported collection interface."""


class LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError(
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryError
):
    """The caller did not provide an already-active transaction."""


class LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError(
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryError
):
    """The exact tenant-scoped evidence identity is absent."""


class LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError(
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryError
):
    """An immutable replay identity collides with divergent evidence."""


class LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError(
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryError
):
    """Durable data failed strict schema, BSON or fingerprint validation."""


class LegalClientMatterRepresentationAuthorizationEvidenceRegistryRetryRequiredError(
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryError
):
    """A duplicate or transient race requires a fresh caller transaction."""


class LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistenceUnavailableError(
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryError
):
    """Mongo persistence failed without a safe replay classification."""


def _fail(
    error_type: type[LegalClientMatterRepresentationAuthorizationEvidenceRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded error while retaining technical cause internally."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    """Translate Mongo failures without owning transaction recovery."""
    if error.has_error_label("TransientTransactionError"):
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryRetryRequiredError,
            "L9C11_P18_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    _fail(
        LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistenceUnavailableError,
        "L9C11_P18_PERSISTENCE_UNAVAILABLE",
        error,
    )


def _target(collection: Any | None) -> Any:
    """Require explicit collection injection and apply canonical concerns."""
    if collection is None:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError,
            "L9C11_P18_COLLECTION_REQUIRED",
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
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError,
            "L9C11_P18_ACTIVE_TRANSACTION_REQUIRED",
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError,
            "L9C11_P18_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError,
            "L9C11_P18_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _identity(name: str, value: object) -> str:
    """Validate an opaque query identity without coercion or value leakage."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError,
            f"L9C11_P18_{name.upper()}_INVALID",
        )
    return value


def _bounded_limit(limit: object) -> int:
    """Require a positive bounded history limit."""
    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or not 0 < limit <= MAX_HISTORY_READS
    ):
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError,
            "L9C11_P18_LIMIT_INVALID",
        )
    return limit


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    """Remove only Mongo identity and normalize P17 BSON array variants."""
    if not isinstance(document, Mapping):
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
            "L9C11_P18_PERSISTED_RECORD_INVALID",
        )
    raw = dict(document)
    raw.pop("_id", None)
    for field in _BSON_TUPLE_FIELDS:
        value = raw.get(field)
        if isinstance(value, list):
            raw[field] = tuple(value)
        elif not isinstance(value, tuple):
            _fail(
                LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
                "L9C11_P18_PERSISTED_RECORD_INVALID",
            )
    return raw


def _domain_payload(raw: Mapping[str, object]) -> dict[str, object]:
    """Bridge only known immutable tuples to P17's strict serialized lists."""
    payload = dict(raw)
    for field in _BSON_TUPLE_FIELDS:
        value = payload[field]
        if isinstance(value, tuple):
            payload[field] = list(value)
    return payload


def _serialized_shape(raw: Mapping[str, object]) -> dict[str, object]:
    """Return the exact P17 serialized shape for post-hydration comparison."""
    return _domain_payload(raw)


def _hydrate(
    document: Mapping[str, object],
) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Hydrate exact P17 evidence after narrow BSON normalization."""
    raw = _canonical(document)
    if set(raw) != set(REPRESENTATION_AUTHORIZATION_EVIDENCE_FIELDS):
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
            "L9C11_P18_PERSISTED_RECORD_INVALID",
        )
    try:
        value = LegalClientMatterRepresentationAuthorizationEvidence.from_dict(
            cast(Mapping[str, object], _domain_payload(raw))
        )
    except (
        TypeError,
        ValueError,
        LegalClientMatterRepresentationAuthorizationEvidenceError,
    ) as error:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
            "L9C11_P18_PERSISTED_RECORD_INVALID",
            error,
        )
    if value.to_dict() != _serialized_shape(raw):
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
            "L9C11_P18_PERSISTED_RECORD_INVALID",
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
                    ("evidence_id", ASCENDING),
                ]
            )
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError,
            "L9C11_P18_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _one(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
) -> Mapping[str, object] | None:
    """Read one identity and reject duplicate durable identities."""
    rows = _rows(collection, query, session=session, limit=2)
    if len(rows) > 1:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
            "L9C11_P18_DUPLICATE_IDENTITY",
        )
    return rows[0] if rows else None


def ensure_indexes(collection: Any | None = None) -> None:
    """Create three replay identities and one deterministic history index."""
    indexes = (
        (
            [("tenant_id", ASCENDING), ("evidence_id", ASCENDING)],
            True,
            EVIDENCE_ID_INDEX_NAME,
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
            [(field, ASCENDING) for field in HISTORY_INDEX_FIELDS],
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
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError,
            "L9C11_P18_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _collision_queries(
    value: LegalClientMatterRepresentationAuthorizationEvidence,
) -> tuple[tuple[dict[str, object], str], ...]:
    """Return all tenant-scoped immutable identities protected by indexes."""
    return (
        (
            {"tenant_id": value.tenant_id, "evidence_id": value.evidence_id},
            "EVIDENCE_ID",
        ),
        (
            {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
            "FINGERPRINT",
        ),
        (
            {
                "tenant_id": value.tenant_id,
                "idempotency_key": value.idempotency_key,
            },
            "IDEMPOTENCY_KEY",
        ),
    )


def _reconcile_duplicate(
    target: Any,
    value: LegalClientMatterRepresentationAuthorizationEvidence,
    document: Mapping[str, object],
    *,
    session: Any,
) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Reconcile a duplicate-key race only against exact canonical evidence."""
    for query, label in _collision_queries(value):
        row = _one(target, query, session=session)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == dict(document):
            return existing
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError,
            f"L9C11_P18_{label}_COLLISION",
        )
    _fail(
        LegalClientMatterRepresentationAuthorizationEvidenceRegistryRetryRequiredError,
        "L9C11_P18_WHOLE_TRANSACTION_RETRY_REQUIRED",
    )


def persist_authorization_evidence(
    value: LegalClientMatterRepresentationAuthorizationEvidence,
    evidence_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Append one exact P17 evidence value or return its exact replay."""
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterRepresentationAuthorizationEvidence:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError,
            "L9C11_P18_EVIDENCE_REQUIRED",
        )
    document = value.to_dict()
    target = _target(evidence_collection)
    for query, label in _collision_queries(value):
        row = _one(target, query, session=tx)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError,
            f"L9C11_P18_{label}_COLLISION",
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
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
            "L9C11_P18_POST_WRITE_RECONCILIATION_FAILED",
        )
    result = _hydrate(persisted)
    if result.to_dict() != document:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
            "L9C11_P18_POST_WRITE_RECONCILIATION_FAILED",
        )
    return result


def get_authorization_evidence(
    tenant_id: str,
    evidence_id: str,
    evidence_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Read one exact evidence identity under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(evidence_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "evidence_id": _identity("evidence_id", evidence_id),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError,
            "L9C11_P18_EVIDENCE_NOT_FOUND",
        )
    return _hydrate(row)


def get_authorization_evidence_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    evidence_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Read one exact fingerprint under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(evidence_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "fingerprint": _identity("fingerprint", fingerprint),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError,
            "L9C11_P18_EVIDENCE_NOT_FOUND",
        )
    return _hydrate(row)


def get_authorization_evidence_by_idempotency_key(
    tenant_id: str,
    idempotency_key: str,
    evidence_collection: Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Read one exact replay identity under exact tenant scope."""
    tx = _active_transaction(session)
    row = _one(
        _target(evidence_collection),
        {
            "tenant_id": _identity("tenant_id", tenant_id),
            "idempotency_key": _identity("idempotency_key", idempotency_key),
        },
        session=tx,
    )
    if row is None:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError,
            "L9C11_P18_EVIDENCE_NOT_FOUND",
        )
    return _hydrate(row)


def list_authorization_evidence_for_context(
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    appointing_principal_id: str,
    acting_capacity_id: str,
    acting_capacity_fingerprint: str,
    engagement_id: str,
    engagement_fingerprint: str,
    mandate_id: str,
    mandate_fingerprint: str,
    representative_principal_id: str,
    representative_role: str,
    evidence_collection: Any | None = None,
    *,
    session: Any = None,
    limit: int = MAX_HISTORY_READS,
) -> tuple[LegalClientMatterRepresentationAuthorizationEvidence, ...]:
    """Return bounded exact appointment-lineage history, never currentness."""
    tx = _active_transaction(session)
    bounded = _bounded_limit(limit)
    values = {
        "tenant_id": _identity("tenant_id", tenant_id),
        "case_matter_id": _identity("case_matter_id", case_matter_id),
        "matter_fingerprint": _identity("matter_fingerprint", matter_fingerprint),
        "client_party_id": _identity("client_party_id", client_party_id),
        "subject_identity_fingerprint": _identity(
            "subject_identity_fingerprint", subject_identity_fingerprint
        ),
        "appointing_principal_id": _identity(
            "appointing_principal_id", appointing_principal_id
        ),
        "acting_capacity_id": _identity("acting_capacity_id", acting_capacity_id),
        "acting_capacity_fingerprint": _identity(
            "acting_capacity_fingerprint", acting_capacity_fingerprint
        ),
        "engagement_id": _identity("engagement_id", engagement_id),
        "engagement_fingerprint": _identity(
            "engagement_fingerprint", engagement_fingerprint
        ),
        "mandate_id": _identity("mandate_id", mandate_id),
        "mandate_fingerprint": _identity("mandate_fingerprint", mandate_fingerprint),
        "representative_principal_id": _identity(
            "representative_principal_id", representative_principal_id
        ),
        "representative_role": _identity("representative_role", representative_role),
    }
    query = {field: values[field] for field in _HISTORY_FILTER_FIELDS}
    rows = _rows(_target(evidence_collection), query, session=tx, limit=bounded + 1)
    if len(rows) > bounded:
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
            "L9C11_P18_READ_LIMIT_EXCEEDED",
        )
    evidence = tuple(_hydrate(row) for row in rows)
    if any(
        any(getattr(item, field) != expected for field, expected in query.items())
        for item in evidence
    ):
        _fail(
            LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
            "L9C11_P18_HISTORY_SCOPE_INVALID",
        )
    return evidence


class LegalClientMatterRepresentationAuthorizationEvidenceRegistry:
    """Static namespace for immutable P17 evidence persistence and reads."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_authorization_evidence = staticmethod(persist_authorization_evidence)
    get_authorization_evidence = staticmethod(get_authorization_evidence)
    get_authorization_evidence_by_fingerprint = staticmethod(
        get_authorization_evidence_by_fingerprint
    )
    get_authorization_evidence_by_idempotency_key = staticmethod(
        get_authorization_evidence_by_idempotency_key
    )
    list_authorization_evidence_for_context = staticmethod(
        list_authorization_evidence_for_context
    )


__all__ = [
    "AUTHORIZATION_EVIDENCE_ID_INDEX_NAME",
    "COLLECTION",
    "EVIDENCE_ID_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_FIELDS",
    "HISTORY_INDEX_NAME",
    "IDEMPOTENCY_INDEX_NAME",
    "MAX_HISTORY_READS",
    "READ_CONCERN",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientMatterRepresentationAuthorizationEvidenceRegistry",
    "LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError",
    "LegalClientMatterRepresentationAuthorizationEvidenceRegistryError",
    "LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError",
    "LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError",
    "LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError",
    "LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistenceUnavailableError",
    "LegalClientMatterRepresentationAuthorizationEvidenceRegistryRetryRequiredError",
    "LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_authorization_evidence",
    "get_authorization_evidence_by_fingerprint",
    "get_authorization_evidence_by_idempotency_key",
    "list_authorization_evidence_for_context",
    "persist_authorization_evidence",
]


# ARTIFACT: legal_client_matter_representation_authorization_evidence_registry.py
# VERSION: v1.0.0-L9C11-P18-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-REGISTRY
# AUTHORITY BOUNDARY: immutable P17 evidence persistence/read only
# TENANT POSTURE: every identity, replay and history query is tenant-scoped
# FAIL-CLOSED POSTURE: strict transaction, BSON, hydration, collision and race validation
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
