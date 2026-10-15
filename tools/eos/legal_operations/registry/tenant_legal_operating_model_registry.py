"""WILSY OS durable Tenant Legal Operating Model registry.

TITLE: Tenant Legal Operating Model Registry
VERSION: v1.0.0-CX26-R2-DURABLE-TENANT-LEGAL-OPERATING-MODEL-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable tenant Legal operating-model configuration and derive
         historical currentness without mutable pointer or IAM authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/tenant_legal_operating_model_registry.py
COLLABORATION / OWNERSHIP: G7B owns canonical configuration semantics; CX26 R2
                            owns only exact-tenant durable persistence, replay,
                            strict hydration, history, and currentness projection.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-CX26-R2 establishes immutable storage, tenant-first indexes,
           exact replay, collision/race handling, strict corruption rejection,
           and deterministic history-derived currentness with no TTL.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores only canonical configuration fields; no PII,
                             credentials, principal, permission, or role truth.
TENANT BOUNDARY: Every operational predicate begins with exact non-pseudo tenant_id.
AUTHORITY BOUNDARY: Persistence and historical projection only; configuration
                    does not authenticate or authorize any principal or action.
COMMERCIAL BOUNDARY: No plan, subscription, entitlement, or feature ownership.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: Caller supplies and owns every active Mongo transaction;
                      this registry never starts, commits, aborts, or retries it.
FAIL-CLOSED DECLARATION: Invalid input, absent transaction, corruption,
                         divergence, fingerprint collision, ambiguous lineage,
                         duplicate race, and persistence outage reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hmac
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.tenant_legal_operating_model import (
    TenantLegalOperatingModel,
    TenantLegalOperatingModelError,
)

VERSION: Final[str] = "v1.0.0-CX26-R2-DURABLE-TENANT-LEGAL-OPERATING-MODEL-REGISTRY"
COLLECTION_NAME: Final[str] = "legal_tenant_operating_models"
IDENTITY_INDEX_NAME: Final[str] = "legal_tenant_operating_model_identity_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "legal_tenant_operating_model_fingerprint_unique"
TENANT_HISTORY_INDEX_NAME: Final[str] = "legal_tenant_operating_model_tenant_revision_history"
CURRENTNESS_INDEX_NAME: Final[str] = "legal_tenant_operating_model_tenant_effective_history"
SUPERSESSION_INDEX_NAME: Final[str] = "legal_tenant_operating_model_tenant_supersession"


class TenantLegalOperatingModelRegistryError(RuntimeError):
    """Base fail-closed registry failure containing one stable non-secret code."""

    default_code = "CX26_R2_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class TenantLegalOperatingModelRegistryInputError(TenantLegalOperatingModelRegistryError):
    """Caller input or collection interface is invalid."""

    default_code = "CX26_R2_INPUT_INVALID"


class TenantLegalOperatingModelRegistryTransactionRequiredError(TenantLegalOperatingModelRegistryError):
    """Caller omitted an already-active transaction."""

    default_code = "CX26_R2_ACTIVE_TRANSACTION_REQUIRED"


class TenantLegalOperatingModelRegistryNotFoundError(TenantLegalOperatingModelRegistryError):
    """No exact tenant-scoped model satisfies the request."""

    default_code = "CX26_R2_MODEL_NOT_FOUND"


class TenantLegalOperatingModelRegistryConflictError(TenantLegalOperatingModelRegistryError):
    """Immutable identity, fingerprint, or lineage is contradictory."""

    default_code = "CX26_R2_IMMUTABLE_CONFLICT"


class TenantLegalOperatingModelRegistryPersistedRecordInvalidError(TenantLegalOperatingModelRegistryError):
    """A durable row failed strict domain hydration or scope correlation."""

    default_code = "CX26_R2_PERSISTED_RECORD_INVALID"


class TenantLegalOperatingModelRegistryPersistenceError(TenantLegalOperatingModelRegistryError):
    """Mongo persistence failed without a safe retry classification."""

    default_code = "CX26_R2_PERSISTENCE_FAILURE"


class TenantLegalOperatingModelRegistryRetryTransactionError(TenantLegalOperatingModelRegistryError):
    """Caller must abort and restart the complete transaction."""

    default_code = "CX26_R2_WHOLE_TRANSACTION_RETRY_REQUIRED"


def _raise(
    error_type: type[TenantLegalOperatingModelRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded registry error while retaining its technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _mongo_failure(error: PyMongoError) -> NoReturn:
    """Translate Mongo failures without taking retry or transaction ownership."""
    try:
        transient = error.has_error_label("TransientTransactionError")
    except Exception:
        transient = False
    if transient:
        _raise(TenantLegalOperatingModelRegistryRetryTransactionError, cause=error)
    _raise(TenantLegalOperatingModelRegistryPersistenceError, cause=error)


def _active_transaction(session: Any) -> Any:
    """Require one caller-owned session whose transaction is already active."""
    if session is None:
        _raise(TenantLegalOperatingModelRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        _raise(TenantLegalOperatingModelRegistryTransactionRequiredError, cause=error)
    if active is not True:
        _raise(TenantLegalOperatingModelRegistryTransactionRequiredError)
    return session


def _identifier(name: str, value: object) -> str:
    """Require one bounded non-coerced persistence identity."""
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 320:
        _raise(TenantLegalOperatingModelRegistryInputError, f"CX26_R2_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    """Require one explicit non-pseudo tenant boundary."""
    tenant = _identifier("tenant_id", value)
    if tenant.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        _raise(TenantLegalOperatingModelRegistryInputError, "CX26_R2_TENANT_REQUIRED")
    return tenant


def _moment(value: object) -> datetime:
    """Require and normalize one timezone-aware currentness instant."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _raise(TenantLegalOperatingModelRegistryInputError, "CX26_R2_AT_INVALID")
    return value.astimezone(timezone.utc)


def _canonical_row(raw: Mapping[str, object]) -> dict[str, object]:
    """Remove only Mongo transport identity from a durable row."""
    row = dict(raw)
    row.pop("_id", None)
    return row


def _hydrate(raw: Mapping[str, object]) -> TenantLegalOperatingModel:
    """Hydrate one exact canonical row and reject all schema/correlation drift."""
    if not isinstance(raw, Mapping):
        _raise(TenantLegalOperatingModelRegistryPersistedRecordInvalidError)
    row = _canonical_row(raw)
    try:
        value = TenantLegalOperatingModel.from_dict(row)
    except (TenantLegalOperatingModelError, TypeError, ValueError, KeyError) as error:
        _raise(TenantLegalOperatingModelRegistryPersistedRecordInvalidError, cause=error)
    if value.to_dict() != row:
        _raise(
            TenantLegalOperatingModelRegistryPersistedRecordInvalidError,
            "CX26_R2_RECORD_CORRELATION_INVALID",
        )
    return value


def _same(left: TenantLegalOperatingModel, right: TenantLegalOperatingModel) -> bool:
    """Compare immutable semantic identity using canonical SHA3-512 evidence."""
    return hmac.compare_digest(left.fingerprint, right.fingerprint) and left == right


class TenantLegalOperatingModelRegistry:
    """Immutable exact-tenant operating-model persistence and currentness facade.

    The registry owns no transaction lifecycle, IAM decision, mutable current
    pointer, commercial truth, or financial execution authority.
    """

    def __init__(self, collection: Any) -> None:
        """Bind one explicit collection without opening persistence lifecycle."""
        if collection is None:
            _raise(TenantLegalOperatingModelRegistryInputError, "CX26_R2_COLLECTION_REQUIRED")
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create only tenant-first immutable identity/history indexes; no TTL."""
        indexes = (
            ([('tenant_id', ASCENDING), ('operating_model_id', ASCENDING)], True, IDENTITY_INDEX_NAME),
            ([('tenant_id', ASCENDING), ('fingerprint', ASCENDING)], True, FINGERPRINT_INDEX_NAME),
            ([('tenant_id', ASCENDING), ('revision', ASCENDING), ('effective_from', ASCENDING), ('operating_model_id', ASCENDING)], False, TENANT_HISTORY_INDEX_NAME),
            ([('tenant_id', ASCENDING), ('effective_from', ASCENDING), ('revision', ASCENDING), ('operating_model_id', ASCENDING)], False, CURRENTNESS_INDEX_NAME),
            ([('tenant_id', ASCENDING), ('supersedes_operating_model_id', ASCENDING)], False, SUPERSESSION_INDEX_NAME),
        )
        try:
            for keys, unique, name in indexes:
                self._collection.create_index(keys, unique=unique, name=name)
        except AttributeError as error:
            _raise(TenantLegalOperatingModelRegistryInputError, "CX26_R2_COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _mongo_failure(error)

    def create_or_replay(self, value: TenantLegalOperatingModel, *, session: Any) -> TenantLegalOperatingModel:
        """Insert an immutable model or return its exact durable replay.

        Divergent same-ID content and cross-ID fingerprint collision reject.
        Duplicate-key races signal whole-transaction retry; no replacement,
        update, transaction control, or implicit retry is performed.
        """
        if type(value) is not TenantLegalOperatingModel:
            _raise(TenantLegalOperatingModelRegistryInputError, "CX26_R2_MODEL_REQUIRED")
        tx = _active_transaction(session)
        identity_query = {"tenant_id": value.tenant_id, "operating_model_id": value.operating_model_id}
        fingerprint_query = {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint}
        try:
            existing = self._collection.find_one(identity_query, session=tx)
            if existing is not None:
                persisted = _hydrate(cast(Mapping[str, object], existing))
                if _same(persisted, value):
                    return persisted
                _raise(TenantLegalOperatingModelRegistryConflictError, "CX26_R2_DIVERGENT_REPLAY")
            collision = self._collection.find_one(fingerprint_query, session=tx)
            if collision is not None:
                collision_identity = cast(Mapping[str, object], collision).get("operating_model_id")
                if collision_identity != value.operating_model_id:
                    _raise(TenantLegalOperatingModelRegistryConflictError, "CX26_R2_FINGERPRINT_COLLISION")
                persisted = _hydrate(cast(Mapping[str, object], collision))
                if _same(persisted, value):
                    return persisted
                _raise(TenantLegalOperatingModelRegistryConflictError, "CX26_R2_FINGERPRINT_COLLISION")
            self._collection.insert_one(value.to_dict(), session=tx)
        except DuplicateKeyError as error:
            _raise(TenantLegalOperatingModelRegistryRetryTransactionError, "CX26_R2_DUPLICATE_RACE_RETRY_TRANSACTION", error)
        except TenantLegalOperatingModelRegistryError:
            raise
        except AttributeError as error:
            _raise(TenantLegalOperatingModelRegistryInputError, "CX26_R2_COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _mongo_failure(error)
        return value

    def get_by_id(self, tenant_id: str, operating_model_id: str, *, session: Any) -> TenantLegalOperatingModel:
        """Read one immutable model under its exact tenant-scoped identity."""
        tenant = _tenant(tenant_id)
        identity = _identifier("operating_model_id", operating_model_id)
        tx = _active_transaction(session)
        try:
            raw = self._collection.find_one(
                {"tenant_id": tenant, "operating_model_id": identity}, session=tx,
            )
        except AttributeError as error:
            _raise(TenantLegalOperatingModelRegistryInputError, "CX26_R2_COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _mongo_failure(error)
        if raw is None:
            _raise(TenantLegalOperatingModelRegistryNotFoundError)
        value = _hydrate(cast(Mapping[str, object], raw))
        if value.tenant_id != tenant or value.operating_model_id != identity:
            _raise(TenantLegalOperatingModelRegistryPersistedRecordInvalidError, "CX26_R2_PERSISTED_SCOPE_MISMATCH")
        return value

    def list_tenant_history(self, tenant_id: str, *, session: Any) -> tuple[TenantLegalOperatingModel, ...]:
        """Return deterministic immutable history for one exact tenant."""
        tenant = _tenant(tenant_id)
        tx = _active_transaction(session)
        try:
            cursor = self._collection.find({"tenant_id": tenant}, session=tx)
            if hasattr(cursor, "sort"):
                cursor = cursor.sort([("revision", ASCENDING), ("effective_from", ASCENDING), ("operating_model_id", ASCENDING)])
            rows = tuple(cursor)
        except AttributeError as error:
            _raise(TenantLegalOperatingModelRegistryInputError, "CX26_R2_COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _mongo_failure(error)
        values = tuple(_hydrate(cast(Mapping[str, object], raw)) for raw in rows)
        if any(value.tenant_id != tenant for value in values):
            _raise(TenantLegalOperatingModelRegistryPersistedRecordInvalidError, "CX26_R2_PERSISTED_SCOPE_MISMATCH")
        return tuple(sorted(values, key=lambda item: (item.revision, item.effective_from, item.operating_model_id)))

    def resolve_current(self, tenant_id: str, at: datetime, *, session: Any) -> TenantLegalOperatingModel:
        """Derive current configuration from coherent applicable immutable history.

        Applicable revisions must form exactly one contiguous chain beginning at
        revision one. Every later revision must name the immediately preceding
        model and become effective strictly after it. Branches, gaps, duplicate
        revisions, contradictory supersession, and time ambiguity fail closed.
        """
        tenant = _tenant(tenant_id)
        moment = _moment(at)
        history = self.list_tenant_history(tenant, session=session)
        applicable = tuple(value for value in history if value.effective_from <= moment)
        if not applicable:
            _raise(TenantLegalOperatingModelRegistryNotFoundError, "CX26_R2_CURRENT_MODEL_NOT_FOUND")
        ordered = tuple(sorted(applicable, key=lambda item: (item.revision, item.effective_from, item.operating_model_id)))
        for index, value in enumerate(ordered):
            expected_revision = index + 1
            if value.revision != expected_revision:
                _raise(TenantLegalOperatingModelRegistryConflictError, "CX26_R2_AMBIGUOUS_OR_GAPPED_HISTORY")
            if index == 0:
                if value.supersedes_operating_model_id is not None:
                    _raise(TenantLegalOperatingModelRegistryConflictError, "CX26_R2_ROOT_SUPERSESSION_INVALID")
                continue
            predecessor = ordered[index - 1]
            if (
                value.supersedes_operating_model_id != predecessor.operating_model_id
                or value.effective_from <= predecessor.effective_from
            ):
                _raise(TenantLegalOperatingModelRegistryConflictError, "CX26_R2_SUPERSESSION_INCONSISTENT")
        return ordered[-1]


def ensure_indexes(collection: Any) -> None:
    """Create governed indexes on one explicit collection without transaction ownership."""
    TenantLegalOperatingModelRegistry(collection).ensure_indexes()


__all__ = [
    "VERSION", "COLLECTION_NAME", "IDENTITY_INDEX_NAME", "FINGERPRINT_INDEX_NAME",
    "TENANT_HISTORY_INDEX_NAME", "CURRENTNESS_INDEX_NAME", "SUPERSESSION_INDEX_NAME",
    "TenantLegalOperatingModelRegistry", "TenantLegalOperatingModelRegistryError",
    "TenantLegalOperatingModelRegistryInputError",
    "TenantLegalOperatingModelRegistryTransactionRequiredError",
    "TenantLegalOperatingModelRegistryNotFoundError",
    "TenantLegalOperatingModelRegistryConflictError",
    "TenantLegalOperatingModelRegistryPersistedRecordInvalidError",
    "TenantLegalOperatingModelRegistryPersistenceError",
    "TenantLegalOperatingModelRegistryRetryTransactionError", "ensure_indexes",
]

# ARTIFACT: tenant_legal_operating_model_registry.py
# VERSION: v1.0.0-CX26-R2-DURABLE-TENANT-LEGAL-OPERATING-MODEL-REGISTRY
# AUTHORITY BOUNDARY: immutable configuration persistence and historical currentness only
# TENANT POSTURE: every operational predicate begins with exact tenant_id
# FAIL-CLOSED POSTURE: transaction, corruption, divergence, collision, ambiguity, race, and outage reject
# COMMERCIAL AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TTL INDEX: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
