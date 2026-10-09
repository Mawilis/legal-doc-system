"""WILSY OS durable tenant product entitlement lifecycle registry.

TITLE: Tenant Product Entitlement Registry
VERSION: v1.0.0-D22B2-TENANT-PRODUCT-ENTITLEMENT-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist immutable D22B1 product-entitlement revisions and maintain one explicit
         tenant/entitlement current pointer with strict hydration, domain-owned
         lifecycle derivation and caller-owned transactional compare-and-set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/entitlement/tenant_product_entitlement_registry.py
COLLABORATION / OWNERSHIP: D22A owns product catalogue identity; D22B1 owns
                            immutable entitlement lifecycle semantics; this
                            registry owns durable revision history plus explicit
                            currentness for an exact tenant/entitlement identity.
                            registry owns persistence only. PlanRegistry,
                            SubscriptionRegistry, IAM and VAS authorities remain
                            separate. Callers own all
                            Mongo session/transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B2-TENANT-PRODUCT-ENTITLEMENT-REGISTRY establishes immutable revision history, explicit
           tenant/entitlement current pointers, revision-zero creation/replay,
           domain-derived legal transitions, exact-current idempotent transition
           replay, CAS advancement, strict pointer-to-history correlation,
           tenant isolation, deterministic history reads, non-unique bounded
           product lookup, deterministic uniqueness and whole-transaction retry
           signaling.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only D22B1 entitlement/evidence fields and
                             compact currentness metadata. No credentials,
                             principal, subscription, invoice or payment data.
TENANT BOUNDARY: Every operational lookup, immutable history record, current
                 pointer and CAS predicate binds exact tenant_id plus the exact
                 entitlement_id where applicable. Foreign evidence is absence.
AUTHORITY BOUNDARY: Durable tenant-product entitlement lifecycle/currentness
                    only. ACTIVE does not grant IAM, route admission, Branding,
                    WILSY AI or commercial authority.
FINANCIAL AUTHORITY BOUNDARY: No pricing, charging, payment, execution or
                               settlement truth. Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Every operational read/write requires an already-active
                      caller-owned Mongo transaction. This registry never starts,
                      commits, aborts, retries or closes transactions.
FAIL-CLOSED DECLARATION: Missing transactions, schema drift, corruption,
                         foreign scope, stale revisions, illegal transitions,
                         divergent replay, duplicate identities, CAS races and
                         persistence outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.tenant_product_entitlement import (
    ENTITLEMENT_FIELDS,
    TenantProductEntitlement,
    TenantProductEntitlementError,
    TenantProductEntitlementState,
)


VERSION: Final[str] = "v1.0.0-D22B2-TENANT-PRODUCT-ENTITLEMENT-REGISTRY"
HISTORY_SCHEMA: Final[str] = "WILSY-TENANT-PRODUCT-ENTITLEMENT-HISTORY/V1"
CURRENT_SCHEMA: Final[str] = "WILSY-TENANT-PRODUCT-ENTITLEMENT-CURRENT/V1"

HISTORY_COLLECTION: Final[str] = "tenant_product_entitlement_history"
CURRENT_COLLECTION: Final[str] = "tenant_product_entitlement_current"

HISTORY_REVISION_INDEX_NAME: Final[str] = (
    "tenant_product_entitlement_tenant_identity_revision_unique"
)
HISTORY_FINGERPRINT_INDEX_NAME: Final[str] = (
    "tenant_product_entitlement_tenant_fingerprint_unique"
)
CURRENT_IDENTITY_INDEX_NAME: Final[str] = (
    "tenant_product_entitlement_current_tenant_identity_unique"
)
CURRENT_PRODUCT_INDEX_NAME: Final[str] = (
    "tenant_product_entitlement_current_tenant_product_lookup"
)

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class TenantProductEntitlementRegistryError(RuntimeError):
    """Base fail-closed D22B2 durable registry error with stable code."""

    default_code = "D22B2_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create one governed registry failure without inventing durable truth."""
        self.code = code or self.default_code
        super().__init__(self.code)


class TenantProductEntitlementRegistryInputError(
    TenantProductEntitlementRegistryError
):
    """Caller input or collection dependency is invalid."""

    default_code = "D22B2_INPUT_INVALID"


class TenantProductEntitlementRegistryTransactionRequiredError(
    TenantProductEntitlementRegistryError
):
    """An already-active caller-owned Mongo transaction is required."""

    default_code = "D22B2_ACTIVE_TRANSACTION_REQUIRED"


class TenantProductEntitlementRegistryPersistedRecordInvalidError(
    TenantProductEntitlementRegistryError
):
    """Persisted entitlement history/currentness failed strict hydration."""

    default_code = "D22B2_PERSISTED_RECORD_INVALID"


class TenantProductEntitlementRegistryNotFoundError(
    TenantProductEntitlementRegistryError
):
    """Exact tenant/entitlement current authority is absent."""

    default_code = "D22B2_ENTITLEMENT_NOT_FOUND"


class TenantProductEntitlementRegistryConflictError(
    TenantProductEntitlementRegistryError
):
    """Caller evidence or requested revision conflicts with durable truth."""

    default_code = "D22B2_ENTITLEMENT_CONFLICT"


class TenantProductEntitlementRegistryRetryRequiredError(
    TenantProductEntitlementRegistryError
):
    """Caller must abort and restart the complete transaction from fresh state."""

    default_code = "D22B2_WHOLE_TRANSACTION_RETRY_REQUIRED"


class TenantProductEntitlementRegistryPersistenceUnavailableError(
    TenantProductEntitlementRegistryError
):
    """Mongo persistence is unavailable without a governed retry label."""

    default_code = "D22B2_PERSISTENCE_UNAVAILABLE"


class TenantProductEntitlementPersistenceOutcome(StrEnum):
    """Durable persistence outcome; no value grants operational authority."""

    CREATED = "CREATED"
    TRANSITIONED = "TRANSITIONED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


def _raise(
    error_type: type[TenantProductEntitlementRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable registry error while preserving its technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo_operational_error(error: PyMongoError) -> NoReturn:
    """Translate only explicit Mongo transaction-race evidence to retry."""
    if error.has_error_label("TransientTransactionError"):
        _raise(
            TenantProductEntitlementRegistryRetryRequiredError,
            cause=error,
        )
    _raise(
        TenantProductEntitlementRegistryPersistenceUnavailableError,
        cause=error,
    )


def _identity(name: str, value: object) -> str:
    """Validate one bounded canonical identity."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _raise(
            TenantProductEntitlementRegistryInputError,
            f"D22B2_{name.upper()}_INVALID",
        )
    return cast(str, value)


def _tenant(value: object) -> str:
    """Validate one real tenant identity and reject pseudo-tenant scopes."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _raise(
            TenantProductEntitlementRegistryInputError,
            "D22B2_TENANT_INVALID",
        )
    return tenant


def _revision(value: object) -> int:
    """Require one non-negative non-boolean lifecycle revision."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _raise(
            TenantProductEntitlementRegistryInputError,
            "D22B2_REVISION_INVALID",
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require one canonical lowercase SHA3-512 fingerprint."""
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _raise(
            TenantProductEntitlementRegistryInputError,
            f"D22B2_{name.upper()}_INVALID",
        )
    return cast(str, value)


def _sha3(value: object) -> str:
    """Return deterministic SHA3-512 over canonical JSON."""
    return hashlib.sha3_512(
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _target(collection: Any) -> Any:
    """Apply majority/journal durability when collection options are available."""
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
        )
    except AttributeError:
        return collection


def _collection(value: Any, label: str) -> Any:
    """Require one collection-like dependency without creating a client."""
    if value is None:
        _raise(
            TenantProductEntitlementRegistryInputError,
            f"D22B2_{label}_COLLECTION_REQUIRED",
        )
    return _target(value)


def _active_transaction(session: Any) -> Any:
    """Require an active caller-owned transaction and own no lifecycle."""
    if session is None:
        _raise(TenantProductEntitlementRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(TenantProductEntitlementRegistryTransactionRequiredError)
    return session


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
) -> list[Mapping[str, Any]]:
    """Read at most two rows so impossible uniqueness drift is observable."""
    target = _collection(collection, "QUERY")
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(2)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except (AttributeError, TypeError):
        try:
            row = target.find_one(dict(query), session=session)
        except PyMongoError as error:
            _raise_mongo_operational_error(error)
        except (AttributeError, TypeError) as error:
            _raise(
                TenantProductEntitlementRegistryInputError,
                "D22B2_COLLECTION_INTERFACE_INVALID",
                error,
            )
        return [] if row is None else [cast(Mapping[str, Any], row)]
    except PyMongoError as error:
        _raise_mongo_operational_error(error)


_HISTORY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "entitlement_id",
        "lifecycle_revision",
        "entitlement_fingerprint",
        "evidence_identity",
        "entitlement_payload",
    }
)


def _history_record(
    entitlement: TenantProductEntitlement,
) -> dict[str, object]:
    """Build one immutable strict history envelope for a D22B1 snapshot."""
    evidence_identity = _sha3(
        {
            "schema": HISTORY_SCHEMA,
            "version": VERSION,
            "tenant_id": entitlement.tenant_id,
            "entitlement_id": entitlement.entitlement_id,
            "lifecycle_revision": entitlement.lifecycle_revision,
            "entitlement_fingerprint": entitlement.fingerprint,
        }
    )
    return {
        "schema": HISTORY_SCHEMA,
        "version": VERSION,
        "entity_type": "TenantProductEntitlementHistoryRecord",
        "tenant_id": entitlement.tenant_id,
        "entitlement_id": entitlement.entitlement_id,
        "lifecycle_revision": entitlement.lifecycle_revision,
        "entitlement_fingerprint": entitlement.fingerprint,
        "evidence_identity": evidence_identity,
        "entitlement_payload": entitlement.to_dict(),
    }


def _hydrate_history(
    document: Mapping[str, Any],
) -> TenantProductEntitlement:
    """Strictly hydrate one immutable history record and verify correlation."""
    if not isinstance(document, Mapping):
        _raise(TenantProductEntitlementRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _HISTORY_FIELDS:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_HISTORY_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != HISTORY_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type")
        != "TenantProductEntitlementHistoryRecord"
    ):
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_HISTORY_VERSION_UNSUPPORTED",
        )
    payload = raw.get("entitlement_payload")
    if not isinstance(payload, Mapping) or set(payload) != set(ENTITLEMENT_FIELDS):
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_ENTITLEMENT_PAYLOAD_SCHEMA_INVALID",
        )
    try:
        entitlement = TenantProductEntitlement.from_dict(
            cast(Mapping[str, object], payload)
        )
    except (TypeError, ValueError, TenantProductEntitlementError) as error:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_ENTITLEMENT_PAYLOAD_INVALID",
            error,
        )
    expected = _history_record(entitlement)
    if expected != raw:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_HISTORY_CORRELATION_INVALID",
        )
    return entitlement


@dataclass(frozen=True, slots=True)
class TenantProductEntitlementCurrentPointer:
    """Compact explicit currentness for one exact tenant/entitlement identity."""

    tenant_id: str
    entitlement_id: str
    lifecycle_revision: int
    entitlement_fingerprint: str
    lifecycle_state: str
    product_id: str
    product_catalogue_fingerprint: str

    def __post_init__(self) -> None:
        """Validate every pointer field without adding lifecycle authority."""
        _tenant(self.tenant_id)
        _identity("entitlement_id", self.entitlement_id)
        _revision(self.lifecycle_revision)
        _fingerprint("entitlement_fingerprint", self.entitlement_fingerprint)
        try:
            TenantProductEntitlementState(self.lifecycle_state)
        except (TypeError, ValueError) as error:
            _raise(
                TenantProductEntitlementRegistryInputError,
                "D22B2_LIFECYCLE_STATE_INVALID",
                error,
            )
        _identity("product_id", self.product_id)
        _fingerprint(
            "product_catalogue_fingerprint",
            self.product_catalogue_fingerprint,
        )

    @property
    def fingerprint(self) -> str:
        """Return deterministic integrity for the exact pointer payload."""
        return _sha3(self.to_dict(include_fingerprint=False))

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        """Serialize compact currentness without commercial or IAM truth."""
        payload: dict[str, object] = {
            "schema": CURRENT_SCHEMA,
            "version": VERSION,
            "entity_type": "TenantProductEntitlementCurrentPointer",
            "tenant_id": self.tenant_id,
            "entitlement_id": self.entitlement_id,
            "lifecycle_revision": self.lifecycle_revision,
            "entitlement_fingerprint": self.entitlement_fingerprint,
            "lifecycle_state": self.lifecycle_state,
            "product_id": self.product_id,
            "product_catalogue_fingerprint": self.product_catalogue_fingerprint,
        }
        if include_fingerprint:
            payload["fingerprint"] = _sha3(payload)
        return payload


_CURRENT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "entitlement_id",
        "lifecycle_revision",
        "entitlement_fingerprint",
        "lifecycle_state",
        "product_id",
        "product_catalogue_fingerprint",
        "fingerprint",
    }
)


def _pointer_for(
    entitlement: TenantProductEntitlement,
) -> TenantProductEntitlementCurrentPointer:
    """Project the only permitted current pointer from one D22B1 snapshot."""
    payload = entitlement.to_dict()
    return TenantProductEntitlementCurrentPointer(
        tenant_id=entitlement.tenant_id,
        entitlement_id=entitlement.entitlement_id,
        lifecycle_revision=entitlement.lifecycle_revision,
        entitlement_fingerprint=entitlement.fingerprint,
        lifecycle_state=cast(str, payload["lifecycle_state"]),
        product_id=cast(str, payload["product_id"]),
        product_catalogue_fingerprint=entitlement.product_catalogue_fingerprint,
    )


def _hydrate_current(
    document: Mapping[str, Any],
) -> TenantProductEntitlementCurrentPointer:
    """Strictly hydrate one current pointer and verify its integrity seal."""
    if not isinstance(document, Mapping):
        _raise(TenantProductEntitlementRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _CURRENT_FIELDS:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_CURRENT_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != CURRENT_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type")
        != "TenantProductEntitlementCurrentPointer"
    ):
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_CURRENT_VERSION_UNSUPPORTED",
        )
    try:
        pointer = TenantProductEntitlementCurrentPointer(
            tenant_id=cast(str, raw["tenant_id"]),
            entitlement_id=cast(str, raw["entitlement_id"]),
            lifecycle_revision=cast(int, raw["lifecycle_revision"]),
            entitlement_fingerprint=cast(str, raw["entitlement_fingerprint"]),
            lifecycle_state=cast(str, raw["lifecycle_state"]),
            product_id=cast(str, raw["product_id"]),
            product_catalogue_fingerprint=cast(
                str,
                raw["product_catalogue_fingerprint"],
            ),
        )
    except TenantProductEntitlementRegistryError as error:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_CURRENT_RECORD_INVALID",
            error,
        )
    if raw.get("fingerprint") != pointer.fingerprint:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_CURRENT_FINGERPRINT_MISMATCH",
        )
    if pointer.to_dict() != raw:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_CURRENT_RECORD_MISMATCH",
        )
    return pointer


@dataclass(frozen=True, slots=True)
class TenantProductEntitlementPersistenceResult:
    """Outcome plus the exact durable current entitlement after one command."""

    outcome: TenantProductEntitlementPersistenceOutcome
    entitlement: TenantProductEntitlement

    def __post_init__(self) -> None:
        """Validate result shape without extending product authority."""
        if not isinstance(
            self.outcome,
            TenantProductEntitlementPersistenceOutcome,
        ):
            _raise(
                TenantProductEntitlementRegistryInputError,
                "D22B2_OUTCOME_INVALID",
            )
        if type(self.entitlement) is not TenantProductEntitlement:
            _raise(
                TenantProductEntitlementRegistryInputError,
                "D22B2_ENTITLEMENT_REQUIRED",
            )


def ensure_indexes(history_collection: Any, current_collection: Any) -> None:
    """Create exact deterministic uniqueness indexes and no lifecycle facts."""
    history = _collection(history_collection, "HISTORY")
    current = _collection(current_collection, "CURRENT")
    try:
        history.create_index(
            [
                ("tenant_id", ASCENDING),
                ("entitlement_id", ASCENDING),
                ("lifecycle_revision", ASCENDING),
            ],
            unique=True,
            name=HISTORY_REVISION_INDEX_NAME,
        )
        history.create_index(
            [("tenant_id", ASCENDING), ("entitlement_fingerprint", ASCENDING)],
            unique=True,
            name=HISTORY_FINGERPRINT_INDEX_NAME,
        )
        current.create_index(
            [("tenant_id", ASCENDING), ("entitlement_id", ASCENDING)],
            unique=True,
            name=CURRENT_IDENTITY_INDEX_NAME,
        )
        current.create_index(
            [("tenant_id", ASCENDING), ("product_id", ASCENDING)],
            name=CURRENT_PRODUCT_INDEX_NAME,
        )
    except (AttributeError, PyMongoError) as error:
        _raise(
            TenantProductEntitlementRegistryPersistenceUnavailableError,
            cause=error,
        )


def _get_history_revision(
    tenant_id: str,
    entitlement_id: str,
    lifecycle_revision: int,
    history_collection: Any,
    *,
    session: Any,
) -> TenantProductEntitlement | None:
    """Read one exact immutable entitlement revision; absence is explicit."""
    tenant = _tenant(tenant_id)
    identity = _identity("entitlement_id", entitlement_id)
    revision = _revision(lifecycle_revision)
    rows = _rows(
        history_collection,
        {
            "tenant_id": tenant,
            "entitlement_id": identity,
            "lifecycle_revision": revision,
        },
        session=session,
    )
    if len(rows) > 1:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_DUPLICATE_HISTORY_REVISION",
        )
    return None if not rows else _hydrate_history(rows[0])


def _get_current_pointer(
    tenant_id: str,
    entitlement_id: str,
    current_collection: Any,
    *,
    session: Any,
) -> TenantProductEntitlementCurrentPointer | None:
    """Read the sole explicit current pointer for an exact entitlement."""
    tenant = _tenant(tenant_id)
    identity = _identity("entitlement_id", entitlement_id)
    rows = _rows(
        current_collection,
        {"tenant_id": tenant, "entitlement_id": identity},
        session=session,
    )
    if len(rows) > 1:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_DUPLICATE_CURRENT_POINTER",
        )
    return None if not rows else _hydrate_current(rows[0])


def get_revision(
    tenant_id: str,
    entitlement_id: str,
    lifecycle_revision: int,
    history_collection: Any,
    *,
    session: Any,
) -> TenantProductEntitlement:
    """Return one exact immutable revision inside a caller-owned transaction.

    The read is exact-tenant and exact-entitlement scoped, performs strict D22B1
    hydration, and grants no commercial, IAM, route or financial authority.
    """
    tx = _active_transaction(session)
    entitlement = _get_history_revision(
        tenant_id,
        entitlement_id,
        lifecycle_revision,
        history_collection,
        session=tx,
    )
    if entitlement is None:
        _raise(TenantProductEntitlementRegistryNotFoundError)
    return entitlement


def get_history(
    tenant_id: str,
    entitlement_id: str,
    history_collection: Any,
    *,
    session: Any,
) -> tuple[TenantProductEntitlement, ...]:
    """Return strictly hydrated lineage ordered by revision, never latest-wins.

    Currentness remains exclusively pointer-driven; this audit read cannot grant
    entitlement, IAM, route, subscription, payment or settlement authority.
    """
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    identity = _identity("entitlement_id", entitlement_id)
    target = _collection(history_collection, "HISTORY")
    try:
        cursor = target.find(
            {"tenant_id": tenant, "entitlement_id": identity},
            session=tx,
        )
        if hasattr(cursor, "sort"):
            cursor = cursor.sort("lifecycle_revision", ASCENDING)
        entitlements = tuple(_hydrate_history(row) for row in cursor)
    except TenantProductEntitlementRegistryError:
        raise
    except PyMongoError as error:
        _raise_mongo_operational_error(error)
    except (AttributeError, TypeError) as error:
        _raise(
            TenantProductEntitlementRegistryInputError,
            "D22B2_COLLECTION_INTERFACE_INVALID",
            error,
        )
    revisions = tuple(item.lifecycle_revision for item in entitlements)
    if revisions != tuple(sorted(revisions)) or len(revisions) != len(set(revisions)):
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_HISTORY_ORDER_INVALID",
        )
    return entitlements


def get_current(
    tenant_id: str,
    entitlement_id: str,
    history_collection: Any,
    current_collection: Any,
    *,
    session: Any,
) -> TenantProductEntitlement:
    """Hydrate exact explicit current entitlement inside caller transaction.

    Currentness is pointer-driven, never inferred by history sort order. The
    hydrated immutable history row must reproduce the pointer exactly.
    """
    tx = _active_transaction(session)
    pointer = _get_current_pointer(
        tenant_id,
        entitlement_id,
        current_collection,
        session=tx,
    )
    if pointer is None:
        _raise(TenantProductEntitlementRegistryNotFoundError)
    entitlement = _get_history_revision(
        pointer.tenant_id,
        pointer.entitlement_id,
        pointer.lifecycle_revision,
        history_collection,
        session=tx,
    )
    if entitlement is None:
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_CURRENT_HISTORY_MISSING",
        )
    if _pointer_for(entitlement).to_dict() != pointer.to_dict():
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_CURRENT_HISTORY_CORRELATION_INVALID",
        )
    return entitlement


def create_or_replay(
    entitlement: TenantProductEntitlement,
    history_collection: Any,
    current_collection: Any,
    *,
    session: Any,
) -> TenantProductEntitlementPersistenceResult:
    """Persist or exactly replay one revision-zero pending D22B1 entitlement.

    Creation accepts only canonical revision-zero PENDING_SOURCE evidence. A
    historical initial snapshot cannot be replayed after currentness advanced,
    so creation can never rewind or obscure the current lifecycle state.
    """
    tx = _active_transaction(session)
    if type(entitlement) is not TenantProductEntitlement:
        _raise(
            TenantProductEntitlementRegistryInputError,
            "D22B2_ENTITLEMENT_REQUIRED",
        )
    if (
        entitlement.lifecycle_revision != 0
        or entitlement.lifecycle_state
        is not TenantProductEntitlementState.PENDING_SOURCE
    ):
        _raise(
            TenantProductEntitlementRegistryInputError,
            "D22B2_INITIAL_PENDING_REVISION_REQUIRED",
        )
    history = _collection(history_collection, "HISTORY")
    current = _collection(current_collection, "CURRENT")

    existing = _get_history_revision(
        entitlement.tenant_id,
        entitlement.entitlement_id,
        0,
        history,
        session=tx,
    )
    if existing is not None:
        if existing.to_dict() != entitlement.to_dict():
            _raise(
                TenantProductEntitlementRegistryConflictError,
                "D22B2_INITIAL_REPLAY_CONFLICT",
            )
        pointer = _get_current_pointer(
            entitlement.tenant_id,
            entitlement.entitlement_id,
            current,
            session=tx,
        )
        if pointer is None or _pointer_for(existing).to_dict() != pointer.to_dict():
            _raise(
                TenantProductEntitlementRegistryConflictError,
                "D22B2_STALE_INITIAL_REPLAY",
            )
        return TenantProductEntitlementPersistenceResult(
            TenantProductEntitlementPersistenceOutcome.IDEMPOTENT_REPLAY,
            existing,
        )

    if (
        _get_current_pointer(
            entitlement.tenant_id,
            entitlement.entitlement_id,
            current,
            session=tx,
        )
        is not None
    ):
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_CURRENT_WITHOUT_INITIAL_HISTORY",
        )

    record = _history_record(entitlement)
    pointer = _pointer_for(entitlement)
    try:
        history.insert_one(record, session=tx)
        current.insert_one(pointer.to_dict(), session=tx)
    except DuplicateKeyError as error:
        _raise(
            TenantProductEntitlementRegistryRetryRequiredError,
            cause=error,
        )
    except PyMongoError as error:
        _raise_mongo_operational_error(error)

    persisted = get_current(
        entitlement.tenant_id,
        entitlement.entitlement_id,
        history,
        current,
        session=tx,
    )
    if persisted.to_dict() != entitlement.to_dict():
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_CREATE_CORRELATION_INVALID",
        )
    return TenantProductEntitlementPersistenceResult(
        TenantProductEntitlementPersistenceOutcome.CREATED,
        persisted,
    )


def transition(
    *,
    tenant_id: str,
    entitlement_id: str,
    target_state: TenantProductEntitlementState | str,
    expected_revision: int,
    evidence_reference: str,
    evidence_fingerprint: str,
    occurred_at: Any,
    history_collection: Any,
    current_collection: Any,
    session: Any,
) -> TenantProductEntitlementPersistenceResult:
    """Derive and persist one legal D22B1 transition with exact CAS currentness.

    The caller supplies only the requested lifecycle command and expected
    revision. Current durable D22B1 truth is re-hydrated first; this registry
    invokes the D22B1 transition authority itself, inserts the immutable next
    revision, then advances the exact prior pointer with compare-and-set.
    """
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    identity = _identity("entitlement_id", entitlement_id)
    expected = _revision(expected_revision)
    history = _collection(history_collection, "HISTORY")
    current_collection_target = _collection(current_collection, "CURRENT")

    current = get_current(
        tenant,
        identity,
        history,
        current_collection_target,
        session=tx,
    )

    if current.lifecycle_revision == expected + 1:
        previous = _get_history_revision(
            tenant,
            identity,
            expected,
            history,
            session=tx,
        )
        if previous is None:
            _raise(
                TenantProductEntitlementRegistryPersistedRecordInvalidError,
                "D22B2_PRIOR_HISTORY_MISSING",
            )
        try:
            expected_current = previous.transition(
                target_state,
                expected_revision=expected,
                evidence_reference=evidence_reference,
                evidence_fingerprint=evidence_fingerprint,
                occurred_at=occurred_at,
            )
        except TenantProductEntitlementError as error:
            _raise(
                TenantProductEntitlementRegistryConflictError,
                "D22B2_TRANSITION_REPLAY_CONFLICT",
                error,
            )
        if expected_current.to_dict() == current.to_dict():
            return TenantProductEntitlementPersistenceResult(
                TenantProductEntitlementPersistenceOutcome.IDEMPOTENT_REPLAY,
                current,
            )
        _raise(
            TenantProductEntitlementRegistryConflictError,
            "D22B2_TRANSITION_REPLAY_CONFLICT",
        )

    if current.lifecycle_revision != expected:
        _raise(
            TenantProductEntitlementRegistryConflictError,
            "D22B2_STALE_REVISION",
        )

    try:
        transitioned = current.transition(
            target_state,
            expected_revision=expected,
            evidence_reference=evidence_reference,
            evidence_fingerprint=evidence_fingerprint,
            occurred_at=occurred_at,
        )
    except TenantProductEntitlementError as error:
        _raise(
            TenantProductEntitlementRegistryConflictError,
            "D22B2_TRANSITION_INVALID",
            error,
        )

    next_record = _history_record(transitioned)
    prior_pointer = _pointer_for(current)
    next_pointer = _pointer_for(transitioned)

    try:
        history.insert_one(next_record, session=tx)
        result = current_collection_target.update_one(
            prior_pointer.to_dict(),
            {"$set": next_pointer.to_dict()},
            session=tx,
        )
        if getattr(result, "matched_count", 0) != 1:
            _raise(TenantProductEntitlementRegistryRetryRequiredError)
    except TenantProductEntitlementRegistryError:
        raise
    except DuplicateKeyError as error:
        _raise(
            TenantProductEntitlementRegistryRetryRequiredError,
            cause=error,
        )
    except PyMongoError as error:
        _raise_mongo_operational_error(error)

    persisted = get_current(
        tenant,
        identity,
        history,
        current_collection_target,
        session=tx,
    )
    if persisted.to_dict() != transitioned.to_dict():
        _raise(
            TenantProductEntitlementRegistryPersistedRecordInvalidError,
            "D22B2_TRANSITION_CORRELATION_INVALID",
        )
    return TenantProductEntitlementPersistenceResult(
        TenantProductEntitlementPersistenceOutcome.TRANSITIONED,
        persisted,
    )


class TenantProductEntitlementRegistry:
    """Static durable facade; owns no Mongo client or transaction lifecycle."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_current = staticmethod(get_current)
    get_revision = staticmethod(get_revision)
    get_history = staticmethod(get_history)
    create_or_replay = staticmethod(create_or_replay)
    transition = staticmethod(transition)


__all__ = [
    "CURRENT_COLLECTION",
    "CURRENT_IDENTITY_INDEX_NAME",
    "CURRENT_PRODUCT_INDEX_NAME",
    "CURRENT_SCHEMA",
    "HISTORY_COLLECTION",
    "HISTORY_FINGERPRINT_INDEX_NAME",
    "HISTORY_REVISION_INDEX_NAME",
    "HISTORY_SCHEMA",
    "READ_CONCERN",
    "TenantProductEntitlementCurrentPointer",
    "TenantProductEntitlementPersistenceOutcome",
    "TenantProductEntitlementPersistenceResult",
    "TenantProductEntitlementRegistry",
    "TenantProductEntitlementRegistryConflictError",
    "TenantProductEntitlementRegistryError",
    "TenantProductEntitlementRegistryInputError",
    "TenantProductEntitlementRegistryNotFoundError",
    "TenantProductEntitlementRegistryPersistedRecordInvalidError",
    "TenantProductEntitlementRegistryPersistenceUnavailableError",
    "TenantProductEntitlementRegistryRetryRequiredError",
    "TenantProductEntitlementRegistryTransactionRequiredError",
    "VERSION",
    "WRITE_CONCERN",
    "create_or_replay",
    "ensure_indexes",
    "get_current",
    "get_history",
    "get_revision",
    "transition",
]

# ARTIFACT: tenant_product_entitlement_registry.py
# VERSION: v1.0.0-D22B2-TENANT-PRODUCT-ENTITLEMENT-REGISTRY
# AUTHORITY BOUNDARY: immutable D22B1 revision persistence and explicit exact-entitlement currentness only; no commercial, IAM, route, VAS or financial authority
# TENANT POSTURE: every history/current read, write, replay and CAS is exact-tenant and exact-entitlement scoped
# FAIL-CLOSED POSTURE: active caller transaction required; schema drift, corruption, stale revision, divergent replay, races and outages reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
