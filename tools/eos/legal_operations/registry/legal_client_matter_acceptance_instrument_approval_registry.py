"""Durable append-only approval history for matter acceptance instruments.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Approval Registry
VERSION: v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable APPROVED/REJECTED decisions for one exact tenant,
         CaseMatter, instrument version, instrument fingerprint and content
         fingerprint. Resolve current approval only from complete history and
         fail closed on corruption, ambiguity, stale subjects and races.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_acceptance_instrument_approval_registry.py
COLLABORATION / OWNERSHIP: P2B1 owns immutable approval value semantics;
                            this P2B2 registry owns append-only persistence,
                            replay and historical currentness composition.
                            IAM, presentability, client acceptance, engagement,
                            representation, Court and finance remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY
           establishes exact subject-scoped history, three collision identities,
           caller-owned transaction propagation, deterministic currentness and
           fail-closed race/corruption handling. No in-place mutation, TTL,
           IAM issuance, visibility, acceptance or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and SHA3-512 fingerprints only;
                             no document body, credentials, tokens or PII.
TENANT BOUNDARY: Every lookup and write carries exact tenant, matter,
                 instrument/version and both immutable fingerprints where the
                 subject is history-scoped. Cross-tenant inference is forbidden.
AUTHORITY BOUNDARY: Historical firm-side approval evidence and derived current
                    decision only. This registry does not authenticate an
                    approver or grant visibility, acceptance, representation,
                    Court, engagement or execution authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
TRANSACTION BOUNDARY: Caller must provide one active Mongo transaction. The
                      registry never begins, commits, aborts, retries or owns it.
FAIL-CLOSED DECLARATION: Missing transaction, malformed rows, divergent replay,
                         equal-time ambiguity, duplicate races and persistence
                         failures reject without healing or destructive action.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    APPROVAL_FIELDS,
    VERSION as APPROVAL_VERSION,
    LegalClientMatterAcceptanceInstrumentApproval,
    LegalClientMatterAcceptanceInstrumentApprovalDecision,
    LegalClientMatterAcceptanceInstrumentApprovalError,
)


VERSION: Final[str] = (
    "v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY"
)
COLLECTION: Final[str] = "legal_client_matter_acceptance_instrument_approvals"
APPROVAL_ID_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_approval_tenant_approval_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_approval_tenant_fingerprint_unique"
)
IDEMPOTENCY_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_approval_tenant_idempotency_unique"
)
HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_approval_subject_history"
)
DECISION_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_approval_subject_decision"
)


class LegalClientMatterAcceptanceInstrumentApprovalRegistryError(RuntimeError):
    """Base fail-closed approval persistence/currentness failure."""

    def __init__(self, code: str) -> None:
        """Expose only a stable, non-sensitive diagnostic code."""
        self.code = code
        super().__init__(code)


class LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError(
    LegalClientMatterAcceptanceInstrumentApprovalRegistryError
):
    """Malformed input or unsupported collection interface."""


class LegalClientMatterAcceptanceInstrumentApprovalRegistryTransactionRequiredError(
    LegalClientMatterAcceptanceInstrumentApprovalRegistryError
):
    """Caller omitted an active transaction/session."""


class LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError(
    LegalClientMatterAcceptanceInstrumentApprovalRegistryError
):
    """Immutable identity, replay or currentness conflict."""


class LegalClientMatterAcceptanceInstrumentApprovalRegistryNotFoundError(
    LegalClientMatterAcceptanceInstrumentApprovalRegistryError
):
    """Requested exact approval identity is absent."""


class LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError(
    LegalClientMatterAcceptanceInstrumentApprovalRegistryError
):
    """Persisted approval failed strict domain hydration or scope checks."""


class LegalClientMatterAcceptanceInstrumentApprovalRegistryRetryRequiredError(
    LegalClientMatterAcceptanceInstrumentApprovalRegistryError
):
    """A write race requires the caller to restart its whole transaction."""


class LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistenceUnavailableError(
    LegalClientMatterAcceptanceInstrumentApprovalRegistryError
):
    """Mongo persistence failed without a safe replay classification."""


class LegalClientMatterAcceptanceInstrumentApprovalRegistryAmbiguousCurrentError(
    LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError
):
    """Equal-effective-time decisions cannot be ordered safely."""


def _fail(
    error_type: type[LegalClientMatterAcceptanceInstrumentApprovalRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded registry error while retaining only an internal cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _target(collection: Collection[Any] | Any | None) -> Any:
    """Resolve an explicit collection or the canonical EOS database collection."""
    if collection is not None:
        try:
            return collection.with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc)
            )
        except AttributeError:
            return collection
    try:
        from tools.eos.kernel.db import get_database

        database = get_database()
    except Exception as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistenceUnavailableError,
            "L9A4_P2B2_PERSISTENCE_UNAVAILABLE",
            error,
        )
    if database is None:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistenceUnavailableError,
            "L9A4_P2B2_PERSISTENCE_UNAVAILABLE",
        )
    return database.get_collection(
        COLLECTION,
        codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc),
    )


def _active_transaction(session: Any) -> Any:
    """Require one caller-owned active transaction and never control it."""
    if session is None:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryTransactionRequiredError,
            "L9A4_P2B2_ACTIVE_TRANSACTION_REQUIRED",
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryTransactionRequiredError,
            "L9A4_P2B2_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryTransactionRequiredError,
            "L9A4_P2B2_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _identity(value: object, name: str) -> str:
    """Validate one exact non-empty lookup identity without coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError,
            f"L9A4_P2B2_{name.upper()}_INVALID",
        )
    return value


def _fingerprint(value: object, name: str) -> str:
    """Validate one exact lowercase SHA3-512 fingerprint through the domain."""
    if not isinstance(value, str) or len(value) != 128 or any(
        character not in "0123456789abcdef" for character in value
    ):
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError,
            f"L9A4_P2B2_{name.upper()}_INVALID",
        )
    return value


def _scope_query(
    tenant_id: str,
    case_matter_id: str,
    instrument_id: str,
    version: str,
    instrument_fingerprint: str,
    content_fingerprint: str,
) -> dict[str, object]:
    """Build the complete immutable subject predicate for history reads."""
    return {
        "tenant_id": _identity(tenant_id, "tenant_id"),
        "case_matter_id": _identity(case_matter_id, "case_matter_id"),
        "instrument_id": _identity(instrument_id, "instrument_id"),
        "version": _identity(version, "version"),
        "instrument_fingerprint": _fingerprint(
            instrument_fingerprint, "instrument_fingerprint"
        ),
        "content_fingerprint": _fingerprint(
            content_fingerprint, "content_fingerprint"
        ),
    }


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    """Remove only Mongo's generated identifier before strict hydration."""
    result = dict(document)
    result.pop("_id", None)
    return result


def _hydrate(document: Mapping[str, object]) -> LegalClientMatterAcceptanceInstrumentApproval:
    """Hydrate one exact persisted domain value and reject schema drift."""
    payload = _canonical(document)
    if set(payload) != set(APPROVAL_FIELDS):
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError,
            "L9A4_P2B2_PERSISTED_RECORD_INVALID",
        )
    try:
        value = LegalClientMatterAcceptanceInstrumentApproval.from_dict(payload)
    except LegalClientMatterAcceptanceInstrumentApprovalError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError,
            "L9A4_P2B2_PERSISTED_RECORD_INVALID",
            error,
        )
    if value.to_dict() != payload:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError,
            "L9A4_P2B2_PERSISTED_RECORD_INVALID",
        )
    return value


def _document(value: LegalClientMatterAcceptanceInstrumentApproval) -> dict[str, object]:
    """Serialize one exact immutable domain value without derived metadata."""
    if type(value) is not LegalClientMatterAcceptanceInstrumentApproval:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError,
            "L9A4_P2B2_VALUE_INVALID",
        )
    return value.to_dict()


def _rows(target: Any, query: Mapping[str, object], *, session: Any) -> list[Mapping[str, object]]:
    """Read complete exact history with the caller session on every read."""
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort(
                [("effective_from", ASCENDING), ("occurred_at", ASCENDING), ("fingerprint", ASCENDING)]
            )
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistenceUnavailableError,
            "L9A4_P2B2_PERSISTENCE_UNAVAILABLE",
            error,
        )
    except AttributeError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError,
            "L9A4_P2B2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _one(target: Any, query: Mapping[str, object], *, session: Any) -> Mapping[str, object] | None:
    """Read one collision identity while preserving caller-session context."""
    try:
        finder = getattr(target, "find_one", None)
        if callable(finder):
            row = finder(dict(query), session=session)
            return cast(Mapping[str, object], row) if row is not None else None
        values = _rows(target, query, session=session)
        return values[0] if values else None
    except PyMongoError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistenceUnavailableError,
            "L9A4_P2B2_PERSISTENCE_UNAVAILABLE",
            error,
        )


def _same_subject(
    expected: LegalClientMatterAcceptanceInstrumentApproval,
    actual: LegalClientMatterAcceptanceInstrumentApproval,
) -> bool:
    """Compare every immutable currentness subject component."""
    return (
        expected.tenant_id == actual.tenant_id
        and expected.case_matter_id == actual.case_matter_id
        and expected.matter_fingerprint == actual.matter_fingerprint
        and expected.instrument_id == actual.instrument_id
        and expected.version == actual.version
        and expected.instrument_fingerprint == actual.instrument_fingerprint
        and expected.content_fingerprint == actual.content_fingerprint
    )


def _hydrate_rows(rows: Iterable[Mapping[str, object]], value: LegalClientMatterAcceptanceInstrumentApproval | None = None) -> list[LegalClientMatterAcceptanceInstrumentApproval]:
    """Hydrate and scope-check all rows returned for one exact subject."""
    values = [_hydrate(row) for row in rows]
    if value is not None and any(not _same_subject(value, item) for item in values):
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError,
            "L9A4_P2B2_HISTORY_SCOPE_INVALID",
        )
    return values


def _collision_queries(value: LegalClientMatterAcceptanceInstrumentApproval) -> tuple[dict[str, object], ...]:
    """Return the three tenant-scoped immutable collision identities."""
    return (
        {"tenant_id": value.tenant_id, "approval_id": value.approval_id},
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        {"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key},
    )


def _collision_code(index: int) -> str:
    """Name one collision class without exposing the supplied identity."""
    return ("APPROVAL_ID", "FINGERPRINT", "IDEMPOTENCY_KEY")[index]


def ensure_indexes(collection: Collection[Any] | Any | None = None) -> None:
    """Create exact replay/history indexes; approvals have no TTL lifecycle."""
    target = _target(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("approval_id", ASCENDING)],
            unique=True,
            name=APPROVAL_ID_INDEX_NAME,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
            unique=True,
            name=FINGERPRINT_INDEX_NAME,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
            unique=True,
            name=IDEMPOTENCY_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("instrument_id", ASCENDING),
                ("version", ASCENDING),
                ("instrument_fingerprint", ASCENDING),
                ("content_fingerprint", ASCENDING),
                ("effective_from", ASCENDING),
                ("occurred_at", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            name=HISTORY_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("instrument_id", ASCENDING),
                ("version", ASCENDING),
                ("instrument_fingerprint", ASCENDING),
                ("content_fingerprint", ASCENDING),
                ("effective_from", DESCENDING),
                ("decision", ASCENDING),
            ],
            name=DECISION_INDEX_NAME,
        )
    except PyMongoError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistenceUnavailableError,
            "L9A4_P2B2_PERSISTENCE_UNAVAILABLE",
            error,
        )


def persist_approval(
    value: LegalClientMatterAcceptanceInstrumentApproval,
    approval_collection: Collection[Any] | Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterAcceptanceInstrumentApproval:
    """Append one immutable approval, returning exact replay when identical.

    All three identities are tenant-scoped. A divergent approval, fingerprint,
    or idempotency collision fails closed. The caller owns transaction
    lifecycle; this method performs one insert only and never starts, commits,
    aborts or retries a transaction. No raw secret or content is returned.
    """
    _active_transaction(session)
    document = _document(value)
    target = _target(approval_collection)
    subject = _scope_query(
        value.tenant_id,
        value.case_matter_id,
        value.instrument_id,
        value.version,
        value.instrument_fingerprint,
        value.content_fingerprint,
    )
    _hydrate_rows(_rows(target, subject, session=session), value)
    for index, query in enumerate(_collision_queries(value)):
        row = _one(target, query, session=session)
        if row is None:
            continue
        existing = _hydrate(row)
        if existing.to_dict() == document:
            return existing
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError,
            f"L9A4_P2B2_{_collision_code(index)}_COLLISION",
        )
    try:
        target.insert_one(dict(document), session=session)
    except DuplicateKeyError as error:
        # Mongo marks the caller transaction abort-only after a duplicate key;
        # no read is attempted on that session. The caller must restart the
        # whole transaction and then obtain the exact replay if applicable.
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryRetryRequiredError,
            "L9A4_P2B2_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    except PyMongoError as error:
        if error.has_error_label("TransientTransactionError"):
            _fail(
                LegalClientMatterAcceptanceInstrumentApprovalRegistryRetryRequiredError,
                "L9A4_P2B2_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistenceUnavailableError,
            "L9A4_P2B2_PERSISTENCE_UNAVAILABLE",
            error,
        )
    persisted = _one(target, {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}, session=session)
    if persisted is None or _hydrate(persisted).to_dict() != document:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError,
            "L9A4_P2B2_POST_WRITE_RECONCILIATION_FAILED",
        )
    return _hydrate(persisted)


def get_approval_history(
    tenant_id: str,
    case_matter_id: str,
    instrument_id: str,
    version: str,
    instrument_fingerprint: str,
    content_fingerprint: str,
    approval_collection: Collection[Any] | Any | None = None,
    *,
    session: Any = None,
) -> tuple[LegalClientMatterAcceptanceInstrumentApproval, ...]:
    """Return complete strict history for one exact immutable subject."""
    _active_transaction(session)
    target = _target(approval_collection)
    values = _hydrate_rows(
        _rows(
            target,
            _scope_query(
                tenant_id,
                case_matter_id,
                instrument_id,
                version,
                instrument_fingerprint,
                content_fingerprint,
            ),
            session=session,
        )
    )
    return tuple(
        sorted(values, key=lambda item: (item.effective_from, item.occurred_at, item.fingerprint))
    )


def get_current_approval(
    tenant_id: str,
    case_matter_id: str,
    instrument_id: str,
    version: str,
    instrument_fingerprint: str,
    content_fingerprint: str,
    approval_collection: Collection[Any] | Any | None = None,
    *,
    at: datetime,
    session: Any = None,
) -> LegalClientMatterAcceptanceInstrumentApproval | None:
    """Resolve the latest effective decision at ``at`` from complete history.

    Decisions after ``at`` are excluded. At the latest effective instant,
    conflicting decisions are ambiguous even when occurrence timestamps could
    suggest an ordering. APPROVED is returned as current, REJECTED as not
    current, and no applicable history as ``None``.
    """
    _active_transaction(session)
    if not isinstance(at, datetime) or at.tzinfo is None or at.utcoffset() is None:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError,
            "L9A4_P2B2_AT_INVALID",
        )
    moment = at.astimezone(timezone.utc)
    history = get_approval_history(
        tenant_id,
        case_matter_id,
        instrument_id,
        version,
        instrument_fingerprint,
        content_fingerprint,
        approval_collection,
        session=session,
    )
    applicable = [item for item in history if item.effective_from <= moment]
    if not applicable:
        return None
    latest_time = max(item.effective_from for item in applicable)
    latest = [item for item in applicable if item.effective_from == latest_time]
    decisions = {item.decision for item in latest}
    if len(decisions) > 1:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryAmbiguousCurrentError,
            "L9A4_P2B2_EQUAL_EFFECTIVE_TIME_AMBIGUOUS",
        )
    chosen = max(latest, key=lambda item: (item.occurred_at, item.fingerprint))
    if chosen.decision is LegalClientMatterAcceptanceInstrumentApprovalDecision.REJECTED:
        return None
    return chosen


def get_approval(
    tenant_id: str,
    approval_id: str,
    approval_collection: Collection[Any] | Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterAcceptanceInstrumentApproval:
    """Return one exact tenant-scoped approval identity or a bounded not-found."""
    _active_transaction(session)
    target = _target(approval_collection)
    row = _one(
        target,
        {"tenant_id": _identity(tenant_id, "tenant_id"), "approval_id": _identity(approval_id, "approval_id")},
        session=session,
    )
    if row is None:
        _fail(
            LegalClientMatterAcceptanceInstrumentApprovalRegistryNotFoundError,
            "L9A4_P2B2_APPROVAL_NOT_FOUND",
        )
    return _hydrate(row)


class LegalClientMatterAcceptanceInstrumentApprovalRegistry:
    """Append-only approval persistence and historical currentness only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_approval = staticmethod(persist_approval)
    get_approval = staticmethod(get_approval)
    get_approval_history = staticmethod(get_approval_history)
    get_current_approval = staticmethod(get_current_approval)


__all__ = [
    "APPROVAL_ID_INDEX_NAME",
    "COLLECTION",
    "DECISION_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME",
    "IDEMPOTENCY_INDEX_NAME",
    "VERSION",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistry",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistryAmbiguousCurrentError",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistryError",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistryNotFoundError",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistenceUnavailableError",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistryRetryRequiredError",
    "LegalClientMatterAcceptanceInstrumentApprovalRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_approval",
    "get_approval_history",
    "get_current_approval",
    "persist_approval",
]


# ARTIFACT: legal_client_matter_acceptance_instrument_approval_registry.py
# VERSION: v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY
# AUTHORITY BOUNDARY: append-only approval evidence and historical currentness only
# TENANT POSTURE: exact tenant/matter/instrument/version/fingerprint predicates
# FAIL-CLOSED POSTURE: corruption, ambiguity, stale scope, replay divergence and races reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
