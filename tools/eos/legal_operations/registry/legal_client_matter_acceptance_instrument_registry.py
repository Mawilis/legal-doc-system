"""WILSY OS durable matter-specific client-review instrument registry.

TITLE: Legal Client Matter Acceptance Instrument Registry
VERSION: v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable tenant- and CaseMatter-scoped client-reviewable
         instrument versions with exact replay, strict corruption rejection,
         caller-owned Mongo transactions and deterministic latest-effective
         unsuperseded selection. This registry does not create approval,
         acceptance, visibility, engagement, representation, Court or finance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_acceptance_instrument_registry.py
COLLABORATION / OWNERSHIP: L9A4-P1B owns the pure instrument value; this
                            L9A4-P1B2 registry owns only immutable durable
                            instrument/version truth and bounded reads. Future
                            acceptance context owns visibility, party,
                            acting-capacity and current approval composition.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY
           establishes a dedicated append-only collection, tenant-scoped
           identity/fingerprint uniqueness, exact replay/divergent collision
           handling, existing-chain supersession validation, strict hydration,
           latest-effective unsuperseded selection and caller-owned active
           transactions. Approval currentness and retirement remain external.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists canonical instrument metadata plus
                             Mongo _id only. No document body, client PII,
                             credentials, browser state or approval mutation.
TENANT BOUNDARY: Every identity, fingerprint, supersession and read predicate
                 begins with exact tenant_id and matter scope where applicable.
AUTHORITY BOUNDARY: Durable immutable reviewable-instrument evidence only;
                    persistence is not approval, presentation eligibility,
                    ClientAcceptance, acting capacity, engagement, mandate,
                    representation, Court authority or legal sufficiency.
FINANCIAL AUTHORITY BOUNDARY: No fee, billing, payment, execution or
                              settlement truth; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns every operational transaction.
                      Registry never starts, commits, aborts, retries or
                      reconciles a Mongo transaction.
FAIL-CLOSED DECLARATION: Missing transaction, malformed/corrupt rows,
                         divergent replay, duplicate identity, unknown or
                         cross-scope supersession, race, invalid query and
                         persistence outage reject without mutation fallback.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    INSTRUMENT_FIELDS,
    LegalClientMatterAcceptanceInstrument,
    LegalClientMatterAcceptanceInstrumentError,
)


VERSION: Final[str] = (
    "v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY"
)
RECORD_SCHEMA: Final[str] = (
    "WILSY-LEGAL-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT/V1"
)
COLLECTION: Final[str] = "legal_client_matter_acceptance_instruments"
IDENTITY_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_tenant_identity_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_tenant_fingerprint_unique"
)
MATTER_INSTRUMENT_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_tenant_matter_instrument_effective"
)
MATTER_KIND_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_tenant_matter_kind_effective"
)
MATTER_EFFECTIVE_INDEX_NAME: Final[str] = (
    "legal_client_matter_instrument_tenant_matter_effective"
)
MAX_VERSIONS: Final[int] = 1000
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientMatterAcceptanceInstrumentRegistryError(RuntimeError):
    """Base fail-closed registry error with a bounded stable code."""

    default_code = "L9A4_P1B2_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Expose only a stable non-sensitive error code."""
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalClientMatterAcceptanceInstrumentRegistryInputError(
    LegalClientMatterAcceptanceInstrumentRegistryError
):
    """Malformed input or unsupported collection interface."""

    default_code = "L9A4_P1B2_INPUT_INVALID"


class LegalClientMatterAcceptanceInstrumentRegistryTransactionRequiredError(
    LegalClientMatterAcceptanceInstrumentRegistryError
):
    """Caller did not provide an already-active transaction."""

    default_code = "L9A4_P1B2_ACTIVE_TRANSACTION_REQUIRED"


class LegalClientMatterAcceptanceInstrumentRegistryNotFoundError(
    LegalClientMatterAcceptanceInstrumentRegistryError
):
    """No exact tenant/matter-scoped immutable instrument exists."""

    default_code = "L9A4_P1B2_INSTRUMENT_NOT_FOUND"


class LegalClientMatterAcceptanceInstrumentRegistryConflictError(
    LegalClientMatterAcceptanceInstrumentRegistryError
):
    """An immutable identity or fingerprint is bound to divergent evidence."""

    default_code = "L9A4_P1B2_INSTRUMENT_CONFLICT"


class LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError(
    LegalClientMatterAcceptanceInstrumentRegistryError
):
    """Persisted data is corrupt or violates its immutable relation."""

    default_code = "L9A4_P1B2_PERSISTED_RECORD_INVALID"


class LegalClientMatterAcceptanceInstrumentRegistryRetryRequiredError(
    LegalClientMatterAcceptanceInstrumentRegistryError
):
    """Caller must abort and restart the complete transaction after a race."""

    default_code = "L9A4_P1B2_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalClientMatterAcceptanceInstrumentRegistryPersistenceUnavailableError(
    LegalClientMatterAcceptanceInstrumentRegistryError
):
    """Persistence failed without a safe replay or retry classification."""

    default_code = "L9A4_P1B2_PERSISTENCE_UNAVAILABLE"


def _raise(
    error_type: type[LegalClientMatterAcceptanceInstrumentRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded registry error while retaining a technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    """Translate Mongo errors without owning transaction recovery."""
    if error.has_error_label("TransientTransactionError"):
        _raise(LegalClientMatterAcceptanceInstrumentRegistryRetryRequiredError, cause=error)
    _raise(
        LegalClientMatterAcceptanceInstrumentRegistryPersistenceUnavailableError,
        cause=error,
    )


def _target(collection: Any) -> Any:
    """Apply majority durability and timezone-aware UTC BSON options."""
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc),
        )
    except AttributeError:
        return collection


def _collection(collection: Any) -> Any:
    """Require one explicit collection target; no implicit database access."""
    if collection is None:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryInputError,
            "L9A4_P1B2_COLLECTION_REQUIRED",
        )
    return _target(collection)


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller-owned Mongo transaction."""
    if session is None:
        _raise(LegalClientMatterAcceptanceInstrumentRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(LegalClientMatterAcceptanceInstrumentRegistryTransactionRequiredError)
    return session


def _text(name: str, value: object) -> str:
    """Require one bounded non-empty query identity without coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryInputError,
            f"L9A4_P1B2_{name.upper()}_INVALID",
        )
    return value


def _timestamp(value: object) -> datetime:
    """Require aware chronology and normalize it to UTC."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _raise(
                LegalClientMatterAcceptanceInstrumentRegistryInputError,
                "L9A4_P1B2_AT_INVALID",
                error,
            )
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryInputError,
            "L9A4_P1B2_AT_INVALID",
        )
    return parsed.astimezone(timezone.utc)


def _canonical_timestamp(value: datetime) -> str:
    """Return the exact microsecond-preserving ISO UTC query representation."""
    return (
        value.astimezone(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int,
    sort: list[tuple[str, int]] | None = None,
) -> list[Mapping[str, Any]]:
    """Read bounded rows with exact caller-session propagation."""
    target = _collection(collection)
    try:
        cursor = target.find(dict(query), session=session)
        if sort is not None and hasattr(cursor, "sort"):
            cursor = cursor.sort(sort)
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryInputError,
            "L9A4_P1B2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def ensure_indexes(collection: Any) -> None:
    """Create justified identity and bounded-read indexes without TTL.

    Administrative index setup is outside operational transaction ownership.
    Historical instrument versions are institutional evidence and must remain
    durable; automatic expiry is therefore deliberately absent.
    """
    target = _collection(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("instrument_id", ASCENDING), ("version", ASCENDING)],
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
                ("effective_from", DESCENDING),
                ("version", DESCENDING),
            ],
            unique=False,
            name=MATTER_INSTRUMENT_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("instrument_kind", ASCENDING),
                ("effective_from", DESCENDING),
            ],
            unique=False,
            name=MATTER_KIND_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("effective_from", DESCENDING),
            ],
            unique=False,
            name=MATTER_EFFECTIVE_INDEX_NAME,
        )
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryInputError,
            "L9A4_P1B2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _hydrate(document: Mapping[str, Any]) -> LegalClientMatterAcceptanceInstrument:
    """Hydrate one exact canonical payload and reject all corruption."""
    if not isinstance(document, Mapping):
        _raise(LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != set(INSTRUMENT_FIELDS):
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_RECORD_SCHEMA_INVALID",
        )
    for field in ("created_at", "effective_from"):
        if not isinstance(raw[field], str):
            _raise(
                LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
                "L9A4_P1B2_TIMESTAMP_CODEC_INVALID",
            )
    try:
        value = LegalClientMatterAcceptanceInstrument.from_dict(
            cast(Mapping[str, object], raw)
        )
    except (TypeError, ValueError, LegalClientMatterAcceptanceInstrumentError) as error:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_INSTRUMENT_PAYLOAD_INVALID",
            error,
        )
    if value.to_dict() != raw:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_RECORD_CORRELATION_INVALID",
        )
    return value


def _scope_values(
    rows: list[Mapping[str, Any]],
    *,
    tenant_id: str,
    case_matter_id: str,
) -> tuple[LegalClientMatterAcceptanceInstrument, ...]:
    """Hydrate and revalidate tenant/matter correlation for returned rows."""
    values = tuple(_hydrate(row) for row in rows)
    if any(
        value.tenant_id != tenant_id or value.case_matter_id != case_matter_id
        for value in values
    ):
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_SCOPE_CORRELATION_INVALID",
        )
    return values


def get_instrument(
    tenant_id: str,
    case_matter_id: str,
    instrument_id: str,
    version: str,
    collection: Any,
    *,
    session: Any,
) -> LegalClientMatterAcceptanceInstrument:
    """Read one exact immutable instrument version under tenant/matter scope."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    matter = _text("case_matter_id", case_matter_id)
    identity = _text("instrument_id", instrument_id)
    version_value = _text("version", version)
    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "case_matter_id": matter,
            "instrument_id": identity,
            "version": version_value,
        },
        session=tx,
        limit=2,
    )
    if not rows:
        _raise(LegalClientMatterAcceptanceInstrumentRegistryNotFoundError)
    if len(rows) > 1:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_DUPLICATE_INSTRUMENT_IDENTITY",
        )
    return _scope_values(rows, tenant_id=tenant, case_matter_id=matter)[0]


def get_instrument_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    collection: Any,
    *,
    session: Any,
) -> LegalClientMatterAcceptanceInstrument:
    """Read one exact immutable fingerprint under tenant scope."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    digest = _text("fingerprint", fingerprint)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "fingerprint": digest},
        session=tx,
        limit=2,
    )
    if not rows:
        _raise(LegalClientMatterAcceptanceInstrumentRegistryNotFoundError)
    if len(rows) > 1:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_DUPLICATE_INSTRUMENT_FINGERPRINT",
        )
    return _hydrate(rows[0])


def list_instrument_versions(
    tenant_id: str,
    case_matter_id: str,
    instrument_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalClientMatterAcceptanceInstrument, ...]:
    """List bounded immutable versions for one exact tenant/matter/instrument."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    matter = _text("case_matter_id", case_matter_id)
    identity = _text("instrument_id", instrument_id)
    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "case_matter_id": matter,
            "instrument_id": identity,
        },
        session=tx,
        limit=MAX_VERSIONS + 1,
        sort=[("effective_from", DESCENDING), ("version", DESCENDING)],
    )
    if len(rows) > MAX_VERSIONS:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_VERSION_LIMIT_EXCEEDED",
        )
    values = _scope_values(rows, tenant_id=tenant, case_matter_id=matter)
    if any(value.instrument_id != identity for value in values):
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_INSTRUMENT_SCOPE_CORRELATION_INVALID",
        )
    return tuple(
        sorted(values, key=lambda item: (item.effective_from, item.version), reverse=True)
    )


def list_matter_instruments_by_kind(
    tenant_id: str,
    case_matter_id: str,
    instrument_kind: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalClientMatterAcceptanceInstrument, ...]:
    """List bounded instrument versions of one kind within one matter."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    matter = _text("case_matter_id", case_matter_id)
    kind = _text("instrument_kind", instrument_kind)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "case_matter_id": matter, "instrument_kind": kind},
        session=tx,
        limit=MAX_VERSIONS + 1,
        sort=[("effective_from", DESCENDING), ("instrument_id", ASCENDING), ("version", DESCENDING)],
    )
    if len(rows) > MAX_VERSIONS:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_KIND_LIMIT_EXCEEDED",
        )
    values = _scope_values(rows, tenant_id=tenant, case_matter_id=matter)
    if any(value.instrument_kind != kind for value in values):
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_KIND_SCOPE_CORRELATION_INVALID",
        )
    return tuple(
        sorted(
            values,
            key=lambda item: (item.effective_from, item.instrument_id, item.version),
            reverse=True,
        )
    )


def get_latest_effective_version(
    tenant_id: str,
    case_matter_id: str,
    instrument_id: str,
    at: datetime,
    collection: Any,
    *,
    session: Any,
) -> LegalClientMatterAcceptanceInstrument | None:
    """Return latest effective unsuperseded version at an aware UTC instant.

    This is deliberately not named ``current`` or ``approved``: approval
    currentness and retirement authority are not available in this registry.
    Only persisted versions effective at ``at`` participate, and a version is
    excluded when another effective version in the same exact chain points to
    its immutable ``version_id`` via ``supersedes_version_id``.
    """
    values = list(
        list_instrument_versions(
            tenant_id,
            case_matter_id,
            instrument_id,
            collection,
            session=session,
        )
    )
    instant = _timestamp(at)
    effective = [value for value in values if value.effective_from <= instant]
    if not effective:
        return None
    superseded = {
        value.supersedes_version_id
        for value in effective
        if value.supersedes_version_id is not None
    }
    candidates = [value for value in effective if value.version_id not in superseded]
    if not candidates:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_SUPERSESSION_CHAIN_INVALID",
        )
    return max(candidates, key=lambda item: (item.effective_from, item.version))


def _superseded_predecessor(
    value: LegalClientMatterAcceptanceInstrument,
    collection: Any,
    *,
    session: Any,
) -> LegalClientMatterAcceptanceInstrument | None:
    """Require an exact same-chain predecessor when supersession is supplied."""
    reference = value.supersedes_version_id
    if reference is None:
        return None
    separator = reference.rfind(":")
    if separator <= 0 or separator == len(reference) - 1:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryConflictError,
            "L9A4_P1B2_SUPERSESSION_REFERENCE_INVALID",
        )
    predecessor_instrument = reference[:separator]
    predecessor_version = reference[separator + 1 :]
    if predecessor_instrument != value.instrument_id:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryConflictError,
            "L9A4_P1B2_SUPERSESSION_INSTRUMENT_MISMATCH",
        )
    try:
        predecessor = get_instrument(
            value.tenant_id,
            value.case_matter_id,
            predecessor_instrument,
            predecessor_version,
            collection,
            session=session,
        )
    except LegalClientMatterAcceptanceInstrumentRegistryNotFoundError as error:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryConflictError,
            "L9A4_P1B2_SUPERSESSION_VERSION_NOT_FOUND",
            error,
        )
    if predecessor.version_id != reference:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_SUPERSESSION_CORRELATION_INVALID",
        )
    return predecessor


def persist_instrument(
    value: LegalClientMatterAcceptanceInstrument,
    collection: Any,
    *,
    session: Any,
) -> LegalClientMatterAcceptanceInstrument:
    """Append one instrument or return its exact immutable replay.

    Same tenant/instrument/version identity plus identical canonical metadata
    replays. Any divergent identity or fingerprint collision fails closed. A
    duplicate-key race signals that the caller must restart the whole Mongo
    transaction; this method never performs lifecycle or retry work.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientMatterAcceptanceInstrument:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryInputError,
            "L9A4_P1B2_INSTRUMENT_REQUIRED",
        )
    target = _collection(collection)
    existing = _rows(
        target,
        {
            "tenant_id": value.tenant_id,
            "case_matter_id": value.case_matter_id,
            "instrument_id": value.instrument_id,
            "version": value.version,
        },
        session=tx,
        limit=2,
    )
    if len(existing) > 1:
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_DUPLICATE_INSTRUMENT_IDENTITY",
        )
    if existing:
        hydrated = _hydrate(existing[0])
        if hydrated.to_dict() == value.to_dict():
            return hydrated
        _raise(LegalClientMatterAcceptanceInstrumentRegistryConflictError)

    by_fingerprint = _rows(
        target,
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        session=tx,
        limit=2,
    )
    if by_fingerprint:
        hydrated = _hydrate(by_fingerprint[0])
        if hydrated.to_dict() == value.to_dict():
            return hydrated
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryConflictError,
            "L9A4_P1B2_FINGERPRINT_IDENTITY_CONFLICT",
        )

    _superseded_predecessor(value, target, session=tx)
    try:
        target.insert_one(value.to_dict(), session=tx)
    except DuplicateKeyError as error:
        _raise(LegalClientMatterAcceptanceInstrumentRegistryRetryRequiredError, cause=error)
    except PyMongoError as error:
        _raise_mongo(error)

    persisted = get_instrument(
        value.tenant_id,
        value.case_matter_id,
        value.instrument_id,
        value.version,
        target,
        session=tx,
    )
    if persisted.to_dict() != value.to_dict():
        _raise(
            LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError,
            "L9A4_P1B2_POST_WRITE_CORRELATION_INVALID",
        )
    return persisted


class LegalClientMatterAcceptanceInstrumentRegistry:
    """Namespace facade for immutable instrument persistence and selection."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_instrument = staticmethod(get_instrument)
    get_instrument_by_fingerprint = staticmethod(get_instrument_by_fingerprint)
    get_latest_effective_version = staticmethod(get_latest_effective_version)
    list_instrument_versions = staticmethod(list_instrument_versions)
    list_matter_instruments_by_kind = staticmethod(list_matter_instruments_by_kind)
    persist_instrument = staticmethod(persist_instrument)


__all__ = [
    "COLLECTION",
    "FINGERPRINT_INDEX_NAME",
    "IDENTITY_INDEX_NAME",
    "MATTER_EFFECTIVE_INDEX_NAME",
    "MATTER_INSTRUMENT_INDEX_NAME",
    "MATTER_KIND_INDEX_NAME",
    "MAX_VERSIONS",
    "RECORD_SCHEMA",
    "READ_CONCERN",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientMatterAcceptanceInstrumentRegistry",
    "LegalClientMatterAcceptanceInstrumentRegistryConflictError",
    "LegalClientMatterAcceptanceInstrumentRegistryError",
    "LegalClientMatterAcceptanceInstrumentRegistryInputError",
    "LegalClientMatterAcceptanceInstrumentRegistryNotFoundError",
    "LegalClientMatterAcceptanceInstrumentRegistryPersistenceUnavailableError",
    "LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError",
    "LegalClientMatterAcceptanceInstrumentRegistryRetryRequiredError",
    "LegalClientMatterAcceptanceInstrumentRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_instrument",
    "get_instrument_by_fingerprint",
    "get_latest_effective_version",
    "list_instrument_versions",
    "list_matter_instruments_by_kind",
    "persist_instrument",
]


# ARTIFACT: legal_client_matter_acceptance_instrument_registry.py
# VERSION: v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY
# AUTHORITY BOUNDARY: immutable matter-scoped instrument persistence/read evidence only
# TENANT POSTURE: every operational predicate begins with exact tenant_id and matter scope
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/supersession/race/outage rejects; no TTL/update/delete
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
