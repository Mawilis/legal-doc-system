"""WILSY OS durable tenant branding entitlement lifecycle registry.

TITLE: Tenant Branding Entitlement Registry
VERSION: v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist immutable D21B2 entitlement revisions and maintain one explicit
         tenant/entitlement current pointer with strict hydration, domain-owned
         lifecycle derivation and caller-owned transactional compare-and-set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_branding_entitlement_registry.py
COLLABORATION / OWNERSHIP: D21B1 owns branding package/capability policy; D21B2
                            owns immutable entitlement lifecycle semantics; this
                            registry owns durable revision history plus explicit
                            currentness for an exact tenant/entitlement identity.
                            D21B3/D21B4 consume exact entitlement evidence but do
                            not own entitlement lifecycle truth. Callers own all
                            Mongo session/transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY establishes
           immutable revision history, explicit tenant/entitlement current
           pointers, revision-zero creation/replay, domain-derived legal
           transitions, exact-current idempotent transition replay, CAS
           advancement, strict pointer-to-history correlation, tenant isolation,
           deterministic uniqueness and whole-transaction retry signaling.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only D21B2 entitlement/evidence fields and
                             compact currentness metadata. No logo, colour,
                             favicon, URL/path/base64, credentials, browser state,
                             subscription price, bank, invoice or payment data.
TENANT BOUNDARY: Every operational lookup, immutable history record, current
                 pointer and CAS predicate binds exact tenant_id plus the exact
                 entitlement_id where applicable. Foreign evidence is absence.
AUTHORITY BOUNDARY: Durable branding-package entitlement lifecycle/currentness
                    only. ACTIVE does not approve a brand profile, resolve an
                    asset, grant IAM/workspace access or authorize presentation.
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

from tools.eos.saas.domain.tenant_branding_entitlement import (
    ENTITLEMENT_FIELDS,
    TenantBrandingEntitlement,
    TenantBrandingEntitlementError,
    TenantBrandingEntitlementState,
)


VERSION: Final[str] = "v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY"
HISTORY_SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-ENTITLEMENT-HISTORY/V1"
CURRENT_SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-ENTITLEMENT-CURRENT/V1"

HISTORY_COLLECTION: Final[str] = "tenant_branding_entitlement_history"
CURRENT_COLLECTION: Final[str] = "tenant_branding_entitlement_current"

HISTORY_REVISION_INDEX_NAME: Final[str] = (
    "tenant_branding_entitlement_tenant_identity_revision_unique"
)
HISTORY_FINGERPRINT_INDEX_NAME: Final[str] = (
    "tenant_branding_entitlement_tenant_fingerprint_unique"
)
CURRENT_IDENTITY_INDEX_NAME: Final[str] = (
    "tenant_branding_entitlement_current_tenant_identity_unique"
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


class TenantBrandingEntitlementRegistryError(RuntimeError):
    """Base fail-closed D21B2B durable registry error with stable code."""

    default_code = "D21B2B_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create one governed registry failure without inventing durable truth."""
        self.code = code or self.default_code
        super().__init__(self.code)


class TenantBrandingEntitlementRegistryInputError(
    TenantBrandingEntitlementRegistryError
):
    """Caller input or collection dependency is invalid."""

    default_code = "D21B2B_INPUT_INVALID"


class TenantBrandingEntitlementRegistryTransactionRequiredError(
    TenantBrandingEntitlementRegistryError
):
    """An already-active caller-owned Mongo transaction is required."""

    default_code = "D21B2B_ACTIVE_TRANSACTION_REQUIRED"


class TenantBrandingEntitlementRegistryPersistedRecordInvalidError(
    TenantBrandingEntitlementRegistryError
):
    """Persisted entitlement history/currentness failed strict hydration."""

    default_code = "D21B2B_PERSISTED_RECORD_INVALID"


class TenantBrandingEntitlementRegistryNotFoundError(
    TenantBrandingEntitlementRegistryError
):
    """Exact tenant/entitlement current authority is absent."""

    default_code = "D21B2B_ENTITLEMENT_NOT_FOUND"


class TenantBrandingEntitlementRegistryConflictError(
    TenantBrandingEntitlementRegistryError
):
    """Caller evidence or requested revision conflicts with durable truth."""

    default_code = "D21B2B_ENTITLEMENT_CONFLICT"


class TenantBrandingEntitlementRegistryRetryRequiredError(
    TenantBrandingEntitlementRegistryError
):
    """Caller must abort and restart the complete transaction from fresh state."""

    default_code = "D21B2B_WHOLE_TRANSACTION_RETRY_REQUIRED"


class TenantBrandingEntitlementRegistryPersistenceUnavailableError(
    TenantBrandingEntitlementRegistryError
):
    """Mongo persistence is unavailable without a governed retry label."""

    default_code = "D21B2B_PERSISTENCE_UNAVAILABLE"


class TenantBrandingEntitlementPersistenceOutcome(StrEnum):
    """Durable outcome; neither value grants presentation authority."""

    CREATED = "CREATED"
    TRANSITIONED = "TRANSITIONED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


def _raise(
    error_type: type[TenantBrandingEntitlementRegistryError],
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
            TenantBrandingEntitlementRegistryRetryRequiredError,
            cause=error,
        )
    _raise(
        TenantBrandingEntitlementRegistryPersistenceUnavailableError,
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
            TenantBrandingEntitlementRegistryInputError,
            f"D21B2B_{name.upper()}_INVALID",
        )
    return cast(str, value)


def _tenant(value: object) -> str:
    """Validate one real tenant identity and reject pseudo-tenant scopes."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _raise(
            TenantBrandingEntitlementRegistryInputError,
            "D21B2B_TENANT_INVALID",
        )
    return tenant


def _revision(value: object) -> int:
    """Require one non-negative non-boolean lifecycle revision."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _raise(
            TenantBrandingEntitlementRegistryInputError,
            "D21B2B_REVISION_INVALID",
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require one canonical lowercase SHA3-512 fingerprint."""
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _raise(
            TenantBrandingEntitlementRegistryInputError,
            f"D21B2B_{name.upper()}_INVALID",
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
            TenantBrandingEntitlementRegistryInputError,
            f"D21B2B_{label}_COLLECTION_REQUIRED",
        )
    return _target(value)


def _active_transaction(session: Any) -> Any:
    """Require an active caller-owned transaction and own no lifecycle."""
    if session is None:
        _raise(TenantBrandingEntitlementRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(TenantBrandingEntitlementRegistryTransactionRequiredError)
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
                TenantBrandingEntitlementRegistryInputError,
                "D21B2B_COLLECTION_INTERFACE_INVALID",
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
    entitlement: TenantBrandingEntitlement,
) -> dict[str, object]:
    """Build one immutable strict history envelope for a D21B2 snapshot."""
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
        "entity_type": "TenantBrandingEntitlementHistoryRecord",
        "tenant_id": entitlement.tenant_id,
        "entitlement_id": entitlement.entitlement_id,
        "lifecycle_revision": entitlement.lifecycle_revision,
        "entitlement_fingerprint": entitlement.fingerprint,
        "evidence_identity": evidence_identity,
        "entitlement_payload": entitlement.to_dict(),
    }


def _hydrate_history(
    document: Mapping[str, Any],
) -> TenantBrandingEntitlement:
    """Strictly hydrate one immutable history record and verify correlation."""
    if not isinstance(document, Mapping):
        _raise(TenantBrandingEntitlementRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _HISTORY_FIELDS:
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_HISTORY_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != HISTORY_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type")
        != "TenantBrandingEntitlementHistoryRecord"
    ):
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_HISTORY_VERSION_UNSUPPORTED",
        )
    payload = raw.get("entitlement_payload")
    if not isinstance(payload, Mapping) or set(payload) != set(ENTITLEMENT_FIELDS):
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_ENTITLEMENT_PAYLOAD_SCHEMA_INVALID",
        )
    try:
        entitlement = TenantBrandingEntitlement.from_dict(
            cast(Mapping[str, object], payload)
        )
    except (TypeError, ValueError, TenantBrandingEntitlementError) as error:
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_ENTITLEMENT_PAYLOAD_INVALID",
            error,
        )
    expected = _history_record(entitlement)
    if expected != raw:
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_HISTORY_CORRELATION_INVALID",
        )
    return entitlement


@dataclass(frozen=True, slots=True)
class TenantBrandingEntitlementCurrentPointer:
    """Compact explicit currentness for one exact tenant/entitlement identity."""

    tenant_id: str
    entitlement_id: str
    lifecycle_revision: int
    entitlement_fingerprint: str
    lifecycle_state: str
    branding_tier: str
    policy_fingerprint: str

    def __post_init__(self) -> None:
        """Validate every pointer field without adding lifecycle authority."""
        _tenant(self.tenant_id)
        _identity("entitlement_id", self.entitlement_id)
        _revision(self.lifecycle_revision)
        _fingerprint("entitlement_fingerprint", self.entitlement_fingerprint)
        try:
            TenantBrandingEntitlementState(self.lifecycle_state)
        except (TypeError, ValueError) as error:
            _raise(
                TenantBrandingEntitlementRegistryInputError,
                "D21B2B_LIFECYCLE_STATE_INVALID",
                error,
            )
        _identity("branding_tier", self.branding_tier)
        _fingerprint("policy_fingerprint", self.policy_fingerprint)

    @property
    def fingerprint(self) -> str:
        """Return deterministic integrity for the exact pointer payload."""
        return _sha3(self.to_dict(include_fingerprint=False))

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        """Serialize compact currentness without profile/asset/browser truth."""
        payload: dict[str, object] = {
            "schema": CURRENT_SCHEMA,
            "version": VERSION,
            "entity_type": "TenantBrandingEntitlementCurrentPointer",
            "tenant_id": self.tenant_id,
            "entitlement_id": self.entitlement_id,
            "lifecycle_revision": self.lifecycle_revision,
            "entitlement_fingerprint": self.entitlement_fingerprint,
            "lifecycle_state": self.lifecycle_state,
            "branding_tier": self.branding_tier,
            "policy_fingerprint": self.policy_fingerprint,
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
        "branding_tier",
        "policy_fingerprint",
        "fingerprint",
    }
)


def _pointer_for(
    entitlement: TenantBrandingEntitlement,
) -> TenantBrandingEntitlementCurrentPointer:
    """Project the only permitted current pointer from one D21B2 snapshot."""
    return TenantBrandingEntitlementCurrentPointer(
        tenant_id=entitlement.tenant_id,
        entitlement_id=entitlement.entitlement_id,
        lifecycle_revision=entitlement.lifecycle_revision,
        entitlement_fingerprint=entitlement.fingerprint,
        lifecycle_state=str(entitlement.lifecycle_state.value),
        branding_tier=str(entitlement.branding_tier.value),
        policy_fingerprint=entitlement.policy_fingerprint,
    )


def _hydrate_current(
    document: Mapping[str, Any],
) -> TenantBrandingEntitlementCurrentPointer:
    """Strictly hydrate one current pointer and verify its integrity seal."""
    if not isinstance(document, Mapping):
        _raise(TenantBrandingEntitlementRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _CURRENT_FIELDS:
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_CURRENT_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != CURRENT_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type")
        != "TenantBrandingEntitlementCurrentPointer"
    ):
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_CURRENT_VERSION_UNSUPPORTED",
        )
    try:
        pointer = TenantBrandingEntitlementCurrentPointer(
            tenant_id=cast(str, raw["tenant_id"]),
            entitlement_id=cast(str, raw["entitlement_id"]),
            lifecycle_revision=cast(int, raw["lifecycle_revision"]),
            entitlement_fingerprint=cast(str, raw["entitlement_fingerprint"]),
            lifecycle_state=cast(str, raw["lifecycle_state"]),
            branding_tier=cast(str, raw["branding_tier"]),
            policy_fingerprint=cast(str, raw["policy_fingerprint"]),
        )
    except TenantBrandingEntitlementRegistryError as error:
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_CURRENT_RECORD_INVALID",
            error,
        )
    if raw.get("fingerprint") != pointer.fingerprint:
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_CURRENT_FINGERPRINT_MISMATCH",
        )
    if pointer.to_dict() != raw:
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_CURRENT_RECORD_MISMATCH",
        )
    return pointer


@dataclass(frozen=True, slots=True)
class TenantBrandingEntitlementPersistenceResult:
    """Outcome plus the exact durable current entitlement after one command."""

    outcome: TenantBrandingEntitlementPersistenceOutcome
    entitlement: TenantBrandingEntitlement

    def __post_init__(self) -> None:
        """Validate result shape without extending package authority."""
        if not isinstance(
            self.outcome,
            TenantBrandingEntitlementPersistenceOutcome,
        ):
            _raise(
                TenantBrandingEntitlementRegistryInputError,
                "D21B2B_OUTCOME_INVALID",
            )
        if type(self.entitlement) is not TenantBrandingEntitlement:
            _raise(
                TenantBrandingEntitlementRegistryInputError,
                "D21B2B_ENTITLEMENT_REQUIRED",
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
    except (AttributeError, PyMongoError) as error:
        _raise(
            TenantBrandingEntitlementRegistryPersistenceUnavailableError,
            cause=error,
        )


def _get_history_revision(
    tenant_id: str,
    entitlement_id: str,
    lifecycle_revision: int,
    history_collection: Any,
    *,
    session: Any,
) -> TenantBrandingEntitlement | None:
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
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_DUPLICATE_HISTORY_REVISION",
        )
    return None if not rows else _hydrate_history(rows[0])


def _get_current_pointer(
    tenant_id: str,
    entitlement_id: str,
    current_collection: Any,
    *,
    session: Any,
) -> TenantBrandingEntitlementCurrentPointer | None:
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
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_DUPLICATE_CURRENT_POINTER",
        )
    return None if not rows else _hydrate_current(rows[0])


def get_current(
    tenant_id: str,
    entitlement_id: str,
    history_collection: Any,
    current_collection: Any,
    *,
    session: Any,
) -> TenantBrandingEntitlement:
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
        _raise(TenantBrandingEntitlementRegistryNotFoundError)
    entitlement = _get_history_revision(
        pointer.tenant_id,
        pointer.entitlement_id,
        pointer.lifecycle_revision,
        history_collection,
        session=tx,
    )
    if entitlement is None:
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_CURRENT_HISTORY_MISSING",
        )
    if _pointer_for(entitlement).to_dict() != pointer.to_dict():
        _raise(
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_CURRENT_HISTORY_CORRELATION_INVALID",
        )
    return entitlement


def create_or_replay(
    entitlement: TenantBrandingEntitlement,
    history_collection: Any,
    current_collection: Any,
    *,
    session: Any,
) -> TenantBrandingEntitlementPersistenceResult:
    """Persist or exactly replay one revision-zero pending D21B2 entitlement.

    Creation accepts only canonical revision-zero PENDING_SOURCE evidence. A
    historical initial snapshot cannot be replayed after currentness advanced,
    so creation can never rewind or obscure the current lifecycle state.
    """
    tx = _active_transaction(session)
    if type(entitlement) is not TenantBrandingEntitlement:
        _raise(
            TenantBrandingEntitlementRegistryInputError,
            "D21B2B_ENTITLEMENT_REQUIRED",
        )
    if (
        entitlement.lifecycle_revision != 0
        or entitlement.lifecycle_state
        is not TenantBrandingEntitlementState.PENDING_SOURCE
    ):
        _raise(
            TenantBrandingEntitlementRegistryInputError,
            "D21B2B_INITIAL_PENDING_REVISION_REQUIRED",
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
                TenantBrandingEntitlementRegistryConflictError,
                "D21B2B_INITIAL_REPLAY_CONFLICT",
            )
        pointer = _get_current_pointer(
            entitlement.tenant_id,
            entitlement.entitlement_id,
            current,
            session=tx,
        )
        if pointer is None or _pointer_for(existing).to_dict() != pointer.to_dict():
            _raise(
                TenantBrandingEntitlementRegistryConflictError,
                "D21B2B_STALE_INITIAL_REPLAY",
            )
        return TenantBrandingEntitlementPersistenceResult(
            TenantBrandingEntitlementPersistenceOutcome.IDEMPOTENT_REPLAY,
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
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_CURRENT_WITHOUT_INITIAL_HISTORY",
        )

    record = _history_record(entitlement)
    pointer = _pointer_for(entitlement)
    try:
        history.insert_one(record, session=tx)
        current.insert_one(pointer.to_dict(), session=tx)
    except DuplicateKeyError as error:
        _raise(
            TenantBrandingEntitlementRegistryRetryRequiredError,
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
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_CREATE_CORRELATION_INVALID",
        )
    return TenantBrandingEntitlementPersistenceResult(
        TenantBrandingEntitlementPersistenceOutcome.CREATED,
        persisted,
    )


def transition(
    *,
    tenant_id: str,
    entitlement_id: str,
    target_state: TenantBrandingEntitlementState | str,
    expected_revision: int,
    evidence_reference: str,
    evidence_fingerprint: str,
    occurred_at: Any,
    history_collection: Any,
    current_collection: Any,
    session: Any,
) -> TenantBrandingEntitlementPersistenceResult:
    """Derive and persist one legal D21B2 transition with exact CAS currentness.

    The caller supplies only the requested lifecycle command and expected
    revision. Current durable D21B2 truth is re-hydrated first; this registry
    invokes the D21B2 transition authority itself, inserts the immutable next
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
                TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
                "D21B2B_PRIOR_HISTORY_MISSING",
            )
        try:
            expected_current = previous.transition(
                target_state,
                expected_revision=expected,
                evidence_reference=evidence_reference,
                evidence_fingerprint=evidence_fingerprint,
                occurred_at=occurred_at,
            )
        except TenantBrandingEntitlementError as error:
            _raise(
                TenantBrandingEntitlementRegistryConflictError,
                "D21B2B_TRANSITION_REPLAY_CONFLICT",
                error,
            )
        if expected_current.to_dict() == current.to_dict():
            return TenantBrandingEntitlementPersistenceResult(
                TenantBrandingEntitlementPersistenceOutcome.IDEMPOTENT_REPLAY,
                current,
            )
        _raise(
            TenantBrandingEntitlementRegistryConflictError,
            "D21B2B_TRANSITION_REPLAY_CONFLICT",
        )

    if current.lifecycle_revision != expected:
        _raise(
            TenantBrandingEntitlementRegistryConflictError,
            "D21B2B_STALE_REVISION",
        )

    try:
        transitioned = current.transition(
            target_state,
            expected_revision=expected,
            evidence_reference=evidence_reference,
            evidence_fingerprint=evidence_fingerprint,
            occurred_at=occurred_at,
        )
    except TenantBrandingEntitlementError as error:
        _raise(
            TenantBrandingEntitlementRegistryConflictError,
            "D21B2B_TRANSITION_INVALID",
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
            _raise(TenantBrandingEntitlementRegistryRetryRequiredError)
    except TenantBrandingEntitlementRegistryError:
        raise
    except DuplicateKeyError as error:
        _raise(
            TenantBrandingEntitlementRegistryRetryRequiredError,
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
            TenantBrandingEntitlementRegistryPersistedRecordInvalidError,
            "D21B2B_TRANSITION_CORRELATION_INVALID",
        )
    return TenantBrandingEntitlementPersistenceResult(
        TenantBrandingEntitlementPersistenceOutcome.TRANSITIONED,
        persisted,
    )


class TenantBrandingEntitlementRegistry:
    """Static durable facade; owns no Mongo client or transaction lifecycle."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_current = staticmethod(get_current)
    create_or_replay = staticmethod(create_or_replay)
    transition = staticmethod(transition)


__all__ = [
    "CURRENT_COLLECTION",
    "CURRENT_IDENTITY_INDEX_NAME",
    "CURRENT_SCHEMA",
    "HISTORY_COLLECTION",
    "HISTORY_FINGERPRINT_INDEX_NAME",
    "HISTORY_REVISION_INDEX_NAME",
    "HISTORY_SCHEMA",
    "READ_CONCERN",
    "TenantBrandingEntitlementCurrentPointer",
    "TenantBrandingEntitlementPersistenceOutcome",
    "TenantBrandingEntitlementPersistenceResult",
    "TenantBrandingEntitlementRegistry",
    "TenantBrandingEntitlementRegistryConflictError",
    "TenantBrandingEntitlementRegistryError",
    "TenantBrandingEntitlementRegistryInputError",
    "TenantBrandingEntitlementRegistryNotFoundError",
    "TenantBrandingEntitlementRegistryPersistedRecordInvalidError",
    "TenantBrandingEntitlementRegistryPersistenceUnavailableError",
    "TenantBrandingEntitlementRegistryRetryRequiredError",
    "TenantBrandingEntitlementRegistryTransactionRequiredError",
    "VERSION",
    "WRITE_CONCERN",
    "create_or_replay",
    "ensure_indexes",
    "get_current",
    "transition",
]

# ARTIFACT: tenant_branding_entitlement_registry.py
# VERSION: v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY
# AUTHORITY BOUNDARY: immutable D21B2 revision persistence plus explicit exact-entitlement currentness only; no profile, asset, browser, IAM or financial authority
# TENANT POSTURE: every history/current read, write, replay and CAS is exact-tenant and exact-entitlement scoped
# FAIL-CLOSED POSTURE: active caller transaction required; schema drift, corruption, stale revision, divergent replay, races and outages reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
