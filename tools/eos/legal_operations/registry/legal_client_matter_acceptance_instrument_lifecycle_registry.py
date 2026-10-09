"""Durable append-only lifecycle history for matter acceptance instruments.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Lifecycle Registry
VERSION: v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist explicit ACTIVE baseline and one terminal lifecycle successor
         for each exact tenant, CaseMatter, instrument and version. Resolve
         current lifecycle state only from complete immutable history, verify
         superseding instrument identity when supplied, and fail closed on
         corruption, races, divergent replay or chronology drift.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_acceptance_instrument_lifecycle_registry.py
COLLABORATION / OWNERSHIP: P2A owns immutable lifecycle value semantics;
                            this P2A2 registry owns append-only persistence,
                            history integrity and current-state derivation.
                            The certified instrument registry remains the
                            authority for successor instrument existence.
                            IAM, visibility, acting capacity, approval and
                            ClientAcceptance remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY
           establishes explicit ACTIVE baselines, terminal transition
           persistence, exact replay, tenant/matter isolation, successor
           verification, strict hydration, race classification, deterministic
           current-state reads, and justified non-TTL indexes. No in-place
           update/delete, approval currentness, acceptance or finance truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and bounded evidence only; no
                             credentials, tokens, client PII or document body.
TENANT BOUNDARY: Every history query, index, successor lookup and returned
                 value is exact tenant/matter/instrument/version scoped.
AUTHORITY BOUNDARY: Append-only lifecycle persistence/currentness only. ACTIVE
                    lifecycle evidence is not approval, presentability,
                    visibility, IAM, acting capacity or acceptance authority.
FINANCIAL AUTHORITY BOUNDARY: No fee, billing, payment, execution or
                              settlement truth; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller must provide one already-active Mongo
                      transaction. The registry never starts, commits,
                      aborts, retries or owns a transaction.
FAIL-CLOSED DECLARATION: Missing transaction, malformed rows, divergent
                         history, cross-scope successor, chronology reversal,
                         duplicate terminal state and persistence races reject
                         without healing or deletion.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LIFECYCLE_FIELDS,
    SCHEMA,
    VERSION as LIFECYCLE_VERSION,
    LegalClientMatterAcceptanceInstrumentLifecycle,
    LegalClientMatterAcceptanceInstrumentLifecycleError,
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
)


VERSION: Final[str] = (
    "v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY"
)
COLLECTION: Final[str] = "legal_client_matter_acceptance_instrument_lifecycle"
IDENTITY_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_lifecycle_identity_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_lifecycle_fingerprint_unique"
)
TERMINAL_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_lifecycle_terminal_unique"
)
HISTORY_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_lifecycle_history"
)
STATE_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_lifecycle_state_history"
)
READ_LIMIT: Final[int] = 8


class LegalClientMatterAcceptanceInstrumentLifecycleRegistryError(RuntimeError):
    """Base fail-closed lifecycle persistence/currentness failure."""

    def __init__(self, code: str) -> None:
        """Expose only a stable non-sensitive error code."""
        self.code = code
        super().__init__(code)


class LegalClientMatterAcceptanceInstrumentLifecycleRegistryInputError(
    LegalClientMatterAcceptanceInstrumentLifecycleRegistryError
):
    """Malformed input or unsupported collection interface."""


class LegalClientMatterAcceptanceInstrumentLifecycleRegistryTransactionRequiredError(
    LegalClientMatterAcceptanceInstrumentLifecycleRegistryError
):
    """Caller omitted an active transaction/session."""


class LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError(
    LegalClientMatterAcceptanceInstrumentLifecycleRegistryError
):
    """Immutable lifecycle identity or transition conflicts with history."""


class LegalClientMatterAcceptanceInstrumentLifecycleRegistryNotFoundError(
    LegalClientMatterAcceptanceInstrumentLifecycleRegistryError
):
    """Exact lifecycle history is absent."""


class LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError(
    LegalClientMatterAcceptanceInstrumentLifecycleRegistryError
):
    """Persisted lifecycle data failed strict value or chain validation."""


class LegalClientMatterAcceptanceInstrumentLifecycleRegistryRetryRequiredError(
    LegalClientMatterAcceptanceInstrumentLifecycleRegistryError
):
    """Caller must abort and restart the whole transaction after a race."""


class LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistenceUnavailableError(
    LegalClientMatterAcceptanceInstrumentLifecycleRegistryError
):
    """Mongo persistence failed without a safe replay classification."""


def _fail(
    error_type: type[LegalClientMatterAcceptanceInstrumentLifecycleRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded registry failure while retaining technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _target(collection: Collection[Any] | Any | None) -> Any:
    """Resolve one explicit/default collection with UTC-aware BSON options."""
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
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistenceUnavailableError,
            "L9A4_P2A2_PERSISTENCE_UNAVAILABLE",
            error,
        )
    if database is None:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistenceUnavailableError,
            "L9A4_P2A2_PERSISTENCE_UNAVAILABLE",
        )
    return database.get_collection(
        COLLECTION,
        codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc),
    )


def _active_transaction(session: Any) -> Any:
    """Require one caller-owned active transaction before any database call."""
    if session is None:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryTransactionRequiredError,
            "L9A4_P2A2_ACTIVE_TRANSACTION_REQUIRED",
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryTransactionRequiredError,
            "L9A4_P2A2_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryTransactionRequiredError,
            "L9A4_P2A2_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _query_identity(value: object, name: str) -> str:
    """Validate one exact non-empty lookup identity."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryInputError,
            f"L9A4_P2A2_{name.upper()}_INVALID",
        )
    return value


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    """Remove only Mongo's generated identifier from one stored document."""
    result = dict(document)
    result.pop("_id", None)
    return result


def _parse_time(value: object) -> datetime:
    """Parse persisted chronology and require an aware timestamp."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(
                LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
                "L9A4_P2A2_PERSISTED_RECORD_INVALID",
                error,
            )
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
            "L9A4_P2A2_PERSISTED_RECORD_INVALID",
        )
    return parsed.astimezone(timezone.utc)


def _hydrate(document: Mapping[str, object]) -> LegalClientMatterAcceptanceInstrumentLifecycle:
    """Strictly hydrate one lifecycle value and verify canonical equality."""
    payload = _canonical(document)
    if set(payload) != set(LIFECYCLE_FIELDS):
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
            "L9A4_P2A2_PERSISTED_RECORD_INVALID",
        )
    if payload.get("schema") != SCHEMA or payload.get("lifecycle_version") != LIFECYCLE_VERSION:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
            "L9A4_P2A2_PERSISTED_RECORD_INVALID",
        )
    values = dict(payload)
    values["occurred_at"] = _parse_time(values["occurred_at"])
    try:
        value = LegalClientMatterAcceptanceInstrumentLifecycle.from_dict(values)
    except LegalClientMatterAcceptanceInstrumentLifecycleError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
            "L9A4_P2A2_PERSISTED_RECORD_INVALID",
            error,
        )
    if value.to_dict() != payload:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
            "L9A4_P2A2_PERSISTED_RECORD_INVALID",
        )
    return value


def _scope_query(
    tenant_id: str,
    case_matter_id: str,
    instrument_id: str,
    version: str,
) -> dict[str, object]:
    """Build the exact tenant/matter/instrument/version history predicate."""
    return {
        "tenant_id": _query_identity(tenant_id, "tenant_id"),
        "case_matter_id": _query_identity(case_matter_id, "case_matter_id"),
        "instrument_id": _query_identity(instrument_id, "instrument_id"),
        "version": _query_identity(version, "version"),
    }


def _history(target: Any, query: Mapping[str, object], *, session: Any) -> list[Mapping[str, object]]:
    """Read bounded exact history with caller-session propagation."""
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort([("occurred_at", ASCENDING), ("fingerprint", ASCENDING)])
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(READ_LIMIT)
        return [cast(Mapping[str, object], row) for row in cursor]
    except PyMongoError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistenceUnavailableError,
            "L9A4_P2A2_PERSISTENCE_UNAVAILABLE",
            error,
        )
    except AttributeError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryInputError,
            "L9A4_P2A2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _same_subject(
    expected: LegalClientMatterAcceptanceInstrumentLifecycle,
    actual: LegalClientMatterAcceptanceInstrumentLifecycle,
) -> bool:
    """Compare immutable subject and instrument semantics, excluding lifecycle state."""
    return (
        expected.tenant_id == actual.tenant_id
        and expected.case_matter_id == actual.case_matter_id
        and expected.matter_fingerprint == actual.matter_fingerprint
        and expected.instrument_id == actual.instrument_id
        and expected.version == actual.version
        and expected.instrument_fingerprint == actual.instrument_fingerprint
    )


def _classify_history(
    rows: list[Mapping[str, object]],
    *,
    expected: LegalClientMatterAcceptanceInstrumentLifecycle | None = None,
) -> tuple[
    LegalClientMatterAcceptanceInstrumentLifecycle | None,
    LegalClientMatterAcceptanceInstrumentLifecycle | None,
]:
    """Validate one exact history and return ACTIVE plus optional terminal fact."""
    if not rows:
        return None, None
    values = [_hydrate(row) for row in rows]
    if expected is not None and any(not _same_subject(expected, value) for value in values):
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
            "L9A4_P2A2_HISTORY_SCOPE_INVALID",
        )
    active = [
        value
        for value in values
        if value.status is LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE
    ]
    terminal = [
        value
        for value in values
        if value.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE
    ]
    if len(active) > 1 or len(terminal) > 1 or len(values) != len(active) + len(terminal):
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
            "L9A4_P2A2_HISTORY_INVALID",
        )
    if terminal and not active:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
            "L9A4_P2A2_ACTIVE_BASELINE_REQUIRED",
        )
    if terminal:
        terminal_value = terminal[0]
        assert active
        if terminal_value.prior_status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
            _fail(
                LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
                "L9A4_P2A2_TRANSITION_INVALID",
            )
        if terminal_value.occurred_at < active[0].occurred_at:
            _fail(
                LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError,
                "L9A4_P2A2_CHRONOLOGY_INVALID",
            )
        return active[0], terminal_value
    return active[0], None


def _document(value: LegalClientMatterAcceptanceInstrumentLifecycle) -> dict[str, object]:
    """Serialize one exact lifecycle value without derived metadata."""
    if type(value) is not LegalClientMatterAcceptanceInstrumentLifecycle:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryInputError,
            "L9A4_P2A2_VALUE_INVALID",
        )
    return value.to_dict()


def ensure_indexes(collection: Collection[Any] | Any | None = None) -> None:
    """Create exact tenant/history indexes; lifecycle evidence has no TTL."""
    target = _target(collection)
    try:
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("instrument_id", ASCENDING),
                ("version", ASCENDING),
                ("status", ASCENDING),
            ],
            unique=True,
            name=IDENTITY_INDEX_NAME,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
            unique=True,
            name=FINGERPRINT_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("instrument_id", ASCENDING),
                ("version", ASCENDING),
                ("prior_status", ASCENDING),
            ],
            unique=True,
            partialFilterExpression={
                "status": {
                    "$in": [
                        LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED.value,
                        LegalClientMatterAcceptanceInstrumentLifecycleStatus.RETIRED.value,
                        LegalClientMatterAcceptanceInstrumentLifecycleStatus.WITHDRAWN.value,
                    ]
                }
            },
            name=TERMINAL_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("instrument_id", ASCENDING),
                ("version", ASCENDING),
                ("occurred_at", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            name=HISTORY_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("status", ASCENDING),
                ("occurred_at", DESCENDING),
            ],
            name=STATE_INDEX_NAME,
        )
    except PyMongoError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistenceUnavailableError,
            "L9A4_P2A2_PERSISTENCE_UNAVAILABLE",
            error,
        )


def _verify_successor(
    value: LegalClientMatterAcceptanceInstrumentLifecycle,
    instrument_collection: Any,
    *,
    session: Any,
) -> None:
    """Verify exact same-chain successor instrument and fingerprint."""
    if value.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED:
        return
    if instrument_collection is None or value.superseding_version_id is None:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryInputError,
            "L9A4_P2A2_SUCCESSOR_COLLECTION_REQUIRED",
        )
    _instrument_id, separator, successor_version = value.superseding_version_id.partition(":")
    if not separator or not successor_version:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError,
            "L9A4_P2A2_SUCCESSOR_ID_INVALID",
        )
    try:
        successor = instrument_registry.get_instrument(
            value.tenant_id,
            value.case_matter_id,
            _instrument_id,
            successor_version,
            instrument_collection,
            session=session,
        )
    except instrument_registry.LegalClientMatterAcceptanceInstrumentRegistryNotFoundError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError,
            "L9A4_P2A2_SUCCESSOR_INSTRUMENT_NOT_FOUND",
            error,
        )
    except instrument_registry.LegalClientMatterAcceptanceInstrumentRegistryError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistenceUnavailableError,
            "L9A4_P2A2_SUCCESSOR_INSTRUMENT_UNAVAILABLE",
            error,
        )
    if successor.fingerprint != value.superseding_instrument_fingerprint:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError,
            "L9A4_P2A2_SUCCESSOR_FINGERPRINT_MISMATCH",
        )


def _load_subject_history(
    *,
    lifecycle_collection: Any,
    value: LegalClientMatterAcceptanceInstrumentLifecycle,
    session: Any,
) -> tuple[
    LegalClientMatterAcceptanceInstrumentLifecycle | None,
    LegalClientMatterAcceptanceInstrumentLifecycle | None,
]:
    """Load and classify one exact subject history."""
    rows = _history(
        lifecycle_collection,
        _scope_query(value.tenant_id, value.case_matter_id, value.instrument_id, value.version),
        session=session,
    )
    return _classify_history(rows, expected=value)


def persist_lifecycle(
    value: LegalClientMatterAcceptanceInstrumentLifecycle,
    lifecycle_collection: Collection[Any] | Any | None = None,
    *,
    instrument_collection: Collection[Any] | Any | None = None,
    session: Any = None,
) -> LegalClientMatterAcceptanceInstrumentLifecycle:
    """Append one lifecycle fact, return exact replay, or reject divergence.

    The caller owns the active transaction. The first fact must be ACTIVE;
    terminal facts require that baseline and only one terminal successor may
    exist. SUPERSEDED additionally verifies the exact successor instrument in
    the same caller session. No update, delete, retry or transaction control
    is performed here.
    """
    _active_transaction(session)
    document = _document(value)
    target = _target(lifecycle_collection)
    active, terminal = _load_subject_history(
        lifecycle_collection=target,
        value=value,
        session=session,
    )
    if active is None and value.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError,
            "L9A4_P2A2_ACTIVE_BASELINE_REQUIRED",
        )
    if active is not None and not _same_subject(active, value):
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError,
            "L9A4_P2A2_SUBJECT_CONFLICT",
        )
    if value.status is LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE and active is not None:
        if active.to_dict() == document and terminal is None:
            return active
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError,
            "L9A4_P2A2_ACTIVE_REPLAY_DIVERGENCE",
        )
    if terminal is not None:
        if terminal.to_dict() == document:
            return terminal
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError,
            "L9A4_P2A2_TERMINAL_REPLAY_DIVERGENCE",
        )
    if value.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
        _verify_successor(value, instrument_collection, session=session)
    try:
        target.insert_one(dict(document), session=session)
    except DuplicateKeyError as error:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryRetryRequiredError,
            "L9A4_P2A2_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    except PyMongoError as error:
        if error.has_error_label("TransientTransactionError"):
            _fail(
                LegalClientMatterAcceptanceInstrumentLifecycleRegistryRetryRequiredError,
                "L9A4_P2A2_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistenceUnavailableError,
            "L9A4_P2A2_PERSISTENCE_UNAVAILABLE",
            error,
        )

    persisted_rows = _history(
        target,
        _scope_query(value.tenant_id, value.case_matter_id, value.instrument_id, value.version),
        session=session,
    )
    persisted_active, persisted_terminal = _classify_history(persisted_rows, expected=value)
    result = persisted_active if value.status is LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE else persisted_terminal
    if result is None or result.to_dict() != document:
        _fail(
            LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError,
            "L9A4_P2A2_POST_WRITE_RECONCILIATION_FAILED",
        )
    return result


def get_lifecycle_history(
    tenant_id: str,
    case_matter_id: str,
    instrument_id: str,
    version: str,
    lifecycle_collection: Collection[Any] | Any | None = None,
    *,
    session: Any = None,
) -> tuple[LegalClientMatterAcceptanceInstrumentLifecycle, ...]:
    """Return strict exact history; absence is an empty tuple."""
    _active_transaction(session)
    target = _target(lifecycle_collection)
    rows = _history(
        target,
        _scope_query(tenant_id, case_matter_id, instrument_id, version),
        session=session,
    )
    values = tuple(_hydrate(row) for row in rows)
    _classify_history(list(rows))
    return tuple(sorted(values, key=lambda item: (item.occurred_at, item.fingerprint)))


def get_current_lifecycle(
    tenant_id: str,
    case_matter_id: str,
    instrument_id: str,
    version: str,
    lifecycle_collection: Collection[Any] | Any | None = None,
    *,
    session: Any = None,
) -> LegalClientMatterAcceptanceInstrumentLifecycle | None:
    """Resolve current state from complete history, or ``None`` without evidence."""
    history = get_lifecycle_history(
        tenant_id,
        case_matter_id,
        instrument_id,
        version,
        lifecycle_collection,
        session=session,
    )
    if not history:
        return None
    active, terminal = _classify_history([value.to_dict() for value in history])
    return terminal or active


class LegalClientMatterAcceptanceInstrumentLifecycleRegistry:
    """Append-only lifecycle persistence and current-state resolution only."""

    ensure_indexes = staticmethod(ensure_indexes)
    persist_lifecycle = staticmethod(persist_lifecycle)
    get_lifecycle_history = staticmethod(get_lifecycle_history)
    get_current_lifecycle = staticmethod(get_current_lifecycle)


__all__ = [
    "COLLECTION",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME",
    "IDENTITY_INDEX_NAME",
    "STATE_INDEX_NAME",
    "TERMINAL_INDEX_NAME",
    "VERSION",
    "LegalClientMatterAcceptanceInstrumentLifecycleRegistry",
    "LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError",
    "LegalClientMatterAcceptanceInstrumentLifecycleRegistryError",
    "LegalClientMatterAcceptanceInstrumentLifecycleRegistryInputError",
    "LegalClientMatterAcceptanceInstrumentLifecycleRegistryNotFoundError",
    "LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError",
    "LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistenceUnavailableError",
    "LegalClientMatterAcceptanceInstrumentLifecycleRegistryRetryRequiredError",
    "LegalClientMatterAcceptanceInstrumentLifecycleRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_current_lifecycle",
    "get_lifecycle_history",
    "persist_lifecycle",
]


# ARTIFACT: legal_client_matter_acceptance_instrument_lifecycle_registry.py
# VERSION: v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY
# AUTHORITY BOUNDARY: append-only lifecycle evidence and current-state derivation only
# TENANT POSTURE: exact tenant/matter/instrument/version predicates on every read/write
# FAIL-CLOSED POSTURE: missing baseline, corruption, races, divergent replay and chronology drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
