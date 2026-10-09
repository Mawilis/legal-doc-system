"""WILSY OS durable immutable client-acceptance registry.

TITLE: Legal Client Acceptance Registry
VERSION: v1.0.0-L9A2-CLIENT-ACCEPTANCE-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable L9A client-acceptance evidence with exact tenant
         and matter isolation, strict hydration, deterministic replay and
         caller-owned Mongo transaction semantics without creating engagement,
         representation, Court or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_acceptance_registry.py
COLLABORATION / OWNERSHIP: L9A owns immutable acceptance semantics; L9A2 owns
                            only append-only durable persistence and exact
                            tenant/matter reads. A later IAM orchestrator must
                            prove actor authority before admission.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A2-CLIENT-ACCEPTANCE-REGISTRY establishes dedicated
           legal_client_acceptances persistence, tenant-scoped immutable
           identity indexes, strict domain hydration, exact replay/divergence
           handling, UTC ISO chronology preservation, bounded matter reads and
           caller-owned active transactions. No TTL, mutable status, update,
           delete, engagement, representation, Court or financial authority is
           created.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only canonical L9A serialized fields plus
                             Mongo _id. No raw PII, credentials, tokens,
                             engagement terms or legal narrative are added.
TENANT BOUNDARY: Every operational read/write/index includes exact tenant_id;
                 no cross-tenant fallback is available.
AUTHORITY BOUNDARY: Durable client-acceptance evidence only. Persistence does
                    not authenticate actors or create client relationship,
                    engagement, representation, conflict clearance, Court or
                    matter-activation truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: Caller supplies and owns every active Mongo transaction;
                      this registry never starts, commits, aborts or retries a
                      transaction.
FAIL-CLOSED DECLARATION: Missing transaction, malformed/corrupt rows,
                         divergent replay, duplicate identity, races, query
                         overflow and persistence outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import timezone
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_acceptance import (
    ACCEPTANCE_FIELDS,
    LegalClientAcceptance,
    LegalClientAcceptanceError,
)


VERSION: Final[str] = "v1.0.0-L9A2-CLIENT-ACCEPTANCE-REGISTRY"
RECORD_SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-ACCEPTANCE/V1"
COLLECTION: Final[str] = "legal_client_acceptances"
ACCEPTANCE_ID_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_tenant_acceptance_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_tenant_fingerprint_unique"
)
MATTER_LOOKUP_INDEX_NAME: Final[str] = (
    "legal_client_acceptance_tenant_matter_lookup"
)
MAX_MATTER_ACCEPTANCES: Final[int] = 500
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class LegalClientAcceptanceRegistryError(RuntimeError):
    """Base fail-closed L9A2 persistence/read error with stable code."""

    default_code = "L9A2_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create an error containing only a non-secret stable code."""
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalClientAcceptanceRegistryInputError(LegalClientAcceptanceRegistryError):
    """Malformed input or unsupported collection interface."""

    default_code = "L9A2_INPUT_INVALID"


class LegalClientAcceptanceRegistryTransactionRequiredError(
    LegalClientAcceptanceRegistryError
):
    """Caller did not provide an already-active transaction."""

    default_code = "L9A2_ACTIVE_TRANSACTION_REQUIRED"


class LegalClientAcceptanceRegistryNotFoundError(LegalClientAcceptanceRegistryError):
    """No exact tenant-scoped immutable acceptance identity exists."""

    default_code = "L9A2_ACCEPTANCE_NOT_FOUND"


class LegalClientAcceptanceRegistryConflictError(LegalClientAcceptanceRegistryError):
    """An immutable acceptance identity is bound to divergent evidence."""

    default_code = "L9A2_ACCEPTANCE_CONFLICT"


class LegalClientAcceptanceRegistryPersistedRecordInvalidError(
    LegalClientAcceptanceRegistryError
):
    """Persisted acceptance data is corrupt or internally divergent."""

    default_code = "L9A2_PERSISTED_RECORD_INVALID"


class LegalClientAcceptanceRegistryRetryRequiredError(
    LegalClientAcceptanceRegistryError
):
    """Caller must abort and restart the complete transaction."""

    default_code = "L9A2_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalClientAcceptanceRegistryPersistenceUnavailableError(
    LegalClientAcceptanceRegistryError
):
    """Mongo persistence could not be safely read or written."""

    default_code = "L9A2_PERSISTENCE_UNAVAILABLE"


def _raise(
    error_type: type[LegalClientAcceptanceRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded registry error while retaining technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    """Translate Mongo failures without owning transaction recovery."""
    if error.has_error_label("TransientTransactionError"):
        _raise(LegalClientAcceptanceRegistryRetryRequiredError, cause=error)
    _raise(LegalClientAcceptanceRegistryPersistenceUnavailableError, cause=error)


def _target(collection: Any) -> Any:
    """Apply canonical majority durability and UTC-aware BSON options."""
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc),
        )
    except AttributeError:
        return collection


def _collection(value: Any) -> Any:
    """Require a collection-like persistence target."""
    if value is None:
        _raise(LegalClientAcceptanceRegistryInputError, "L9A2_COLLECTION_REQUIRED")
    return _target(value)


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller-owned Mongo transaction."""
    if session is None:
        _raise(LegalClientAcceptanceRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(LegalClientAcceptanceRegistryTransactionRequiredError)
    return session


def _text(name: str, value: object) -> str:
    """Require one non-empty, non-coerced query identity."""
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(
            LegalClientAcceptanceRegistryInputError,
            f"L9A2_{name.upper()}_INVALID",
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 query fingerprint."""
    text = _text(name, value)
    if len(text) != 128 or any(character not in "0123456789abcdef" for character in text):
        _raise(
            LegalClientAcceptanceRegistryInputError,
            f"L9A2_{name.upper()}_INVALID",
        )
    return text


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int,
) -> list[Mapping[str, Any]]:
    """Read bounded rows with exact caller-session propagation."""
    target = _collection(collection)
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "sort"):
            cursor = cursor.sort(
                [("accepted_at", DESCENDING), ("acceptance_id", ASCENDING)]
            )
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalClientAcceptanceRegistryInputError,
            "L9A2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def ensure_indexes(collection: Any) -> None:
    """Create only immutable acceptance identity and proven read indexes.

    This setup is administrative and does not require an operational transaction.
    No TTL index is created because acceptance evidence is durable institutional
    history and must not expire automatically.
    """
    target = _collection(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("acceptance_id", ASCENDING)],
            unique=True,
            name=ACCEPTANCE_ID_INDEX_NAME,
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
                ("accepted_at", DESCENDING),
            ],
            unique=False,
            name=MATTER_LOOKUP_INDEX_NAME,
        )
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalClientAcceptanceRegistryInputError,
            "L9A2_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _hydrate(document: Mapping[str, Any]) -> LegalClientAcceptance:
    """Hydrate one exact canonical domain payload and reject corruption."""
    if not isinstance(document, Mapping):
        _raise(LegalClientAcceptanceRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != set(ACCEPTANCE_FIELDS):
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_RECORD_SCHEMA_INVALID",
        )
    # Canonical ISO text intentionally avoids BSON millisecond truncation and
    # preserves the domain's exact microsecond chronology across readback.
    if not isinstance(raw.get("accepted_at"), str):
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_ACCEPTED_AT_CODEC_INVALID",
        )
    try:
        value = LegalClientAcceptance.from_dict(
            cast(Mapping[str, object], raw)
        )
    except (TypeError, ValueError, LegalClientAcceptanceError) as error:
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_ACCEPTANCE_PAYLOAD_INVALID",
            error,
        )
    if value.to_dict() != raw:
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_RECORD_CORRELATION_INVALID",
        )
    return value


def get_acceptance(
    tenant_id: str,
    acceptance_id: str,
    collection: Any,
    *,
    session: Any,
) -> LegalClientAcceptance:
    """Read one exact immutable acceptance identity under tenant scope."""
    tx = _active_transaction(session)
    target = _collection(collection)
    tenant = _text("tenant_id", tenant_id)
    identity = _text("acceptance_id", acceptance_id)
    rows = _rows(
        target,
        {"tenant_id": tenant, "acceptance_id": identity},
        session=tx,
        limit=2,
    )
    if not rows:
        _raise(LegalClientAcceptanceRegistryNotFoundError)
    if len(rows) > 1:
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_DUPLICATE_ACCEPTANCE_ID",
        )
    return _hydrate(rows[0])


def get_acceptance_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    collection: Any,
    *,
    session: Any,
) -> LegalClientAcceptance:
    """Read one exact acceptance fingerprint under exact tenant scope."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    digest = _fingerprint("fingerprint", fingerprint)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "fingerprint": digest},
        session=tx,
        limit=2,
    )
    if not rows:
        _raise(LegalClientAcceptanceRegistryNotFoundError)
    if len(rows) > 1:
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_DUPLICATE_ACCEPTANCE_FINGERPRINT",
        )
    return _hydrate(rows[0])


def list_matter_acceptances(
    tenant_id: str,
    case_matter_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalClientAcceptance, ...]:
    """Read bounded immutable acceptance history for one tenant/matter."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    matter = _text("case_matter_id", case_matter_id)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "case_matter_id": matter},
        session=tx,
        limit=MAX_MATTER_ACCEPTANCES + 1,
    )
    if len(rows) > MAX_MATTER_ACCEPTANCES:
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_MATTER_ACCEPTANCE_LIMIT_EXCEEDED",
        )
    values = tuple(_hydrate(row) for row in rows)
    if any(
        value.tenant_id != tenant
        or value.case_matter_id != matter
        for value in values
    ):
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_MATTER_QUERY_CORRELATION_INVALID",
        )
    return tuple(
        sorted(values, key=lambda item: (item.accepted_at, item.acceptance_id))
    )


def persist_acceptance(
    value: LegalClientAcceptance,
    collection: Any,
    *,
    session: Any,
) -> LegalClientAcceptance:
    """Persist one immutable acceptance or return its exact replay.

    Same tenant/acceptance identity plus identical canonical evidence returns
    the hydrated durable value. Divergent evidence fails closed. Duplicate-key
    races become a whole-transaction retry signal; the registry never performs
    transaction lifecycle or retry work itself.
    """
    tx = _active_transaction(session)
    if type(value) is not LegalClientAcceptance:
        _raise(
            LegalClientAcceptanceRegistryInputError,
            "L9A2_ACCEPTANCE_REQUIRED",
        )
    target = _collection(collection)
    existing = _rows(
        target,
        {"tenant_id": value.tenant_id, "acceptance_id": value.acceptance_id},
        session=tx,
        limit=2,
    )
    if len(existing) > 1:
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_DUPLICATE_ACCEPTANCE_ID",
        )
    if existing:
        hydrated = _hydrate(existing[0])
        if hydrated.to_dict() == value.to_dict():
            return hydrated
        _raise(LegalClientAcceptanceRegistryConflictError)

    try:
        target.insert_one(value.to_dict(), session=tx)
    except DuplicateKeyError as error:
        _raise(LegalClientAcceptanceRegistryRetryRequiredError, cause=error)
    except PyMongoError as error:
        _raise_mongo(error)

    persisted = get_acceptance(
        value.tenant_id,
        value.acceptance_id,
        target,
        session=tx,
    )
    if persisted.to_dict() != value.to_dict():
        _raise(
            LegalClientAcceptanceRegistryPersistedRecordInvalidError,
            "L9A2_POST_WRITE_CORRELATION_INVALID",
        )
    return persisted


class LegalClientAcceptanceRegistry:
    """Namespace facade for immutable acceptance persistence/read operations."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_acceptance = staticmethod(get_acceptance)
    get_acceptance_by_fingerprint = staticmethod(get_acceptance_by_fingerprint)
    list_matter_acceptances = staticmethod(list_matter_acceptances)
    persist_acceptance = staticmethod(persist_acceptance)


__all__ = [
    "ACCEPTANCE_ID_INDEX_NAME",
    "COLLECTION",
    "FINGERPRINT_INDEX_NAME",
    "MATTER_LOOKUP_INDEX_NAME",
    "MAX_MATTER_ACCEPTANCES",
    "READ_CONCERN",
    "RECORD_SCHEMA",
    "VERSION",
    "WRITE_CONCERN",
    "LegalClientAcceptanceRegistry",
    "LegalClientAcceptanceRegistryConflictError",
    "LegalClientAcceptanceRegistryError",
    "LegalClientAcceptanceRegistryInputError",
    "LegalClientAcceptanceRegistryNotFoundError",
    "LegalClientAcceptanceRegistryPersistedRecordInvalidError",
    "LegalClientAcceptanceRegistryPersistenceUnavailableError",
    "LegalClientAcceptanceRegistryRetryRequiredError",
    "LegalClientAcceptanceRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_acceptance",
    "get_acceptance_by_fingerprint",
    "list_matter_acceptances",
    "persist_acceptance",
]


# ARTIFACT: legal_client_acceptance_registry.py
# VERSION: v1.0.0-L9A2-CLIENT-ACCEPTANCE-REGISTRY
# AUTHORITY BOUNDARY: immutable client-acceptance persistence/read evidence only
# TENANT POSTURE: every operational lookup/write/index begins with exact tenant_id
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/race/outage rejects; no TTL or mutable status
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
