"""WILSY OS durable Tenant Legal Workflow Activation registry.

TITLE: Tenant Legal Workflow Activation Registry
VERSION: v1.0.0-G7G-P0A-DURABLE-ACTIVATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable exact-tenant workflow activation evidence and derive
         current activation from complete, coherent effective history.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/tenant_legal_workflow_activation_registry.py
COLLABORATION / OWNERSHIP: TenantLegalWorkflowActivation owns domain semantics;
                            this registry owns durability, replay, history, and
                            deterministic currentness projection only.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0-G7G-P0A establishes tenant-first append-only persistence,
           exact replay, strict hydration, lineage validation, and no-TTL indexes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Exact tenant predicates precede every read and write.
TENANT BOUNDARY: Cross-tenant absence never discloses foreign durable truth.
AUTHORITY BOUNDARY: Persistence is not IAM, workflow execution, work assignment,
                    supervision, professional authority, or legal-event truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Caller owns the already-active Mongo transaction and any
                      whole-transaction retry.
FAIL-CLOSED DECLARATION: Invalid input, missing transaction, divergent replay,
                         corrupt history, gaps, forks, races, and outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hmac
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.tenant_legal_workflow_activation import (
    TenantLegalWorkflowActivation,
    TenantLegalWorkflowActivationError,
)

VERSION: Final[str] = "v1.0.0-G7G-P0A-DURABLE-ACTIVATION-REGISTRY"
COLLECTION_NAME: Final[str] = "tenant_legal_workflow_activations"
IDENTITY_INDEX_NAME: Final[str] = "tenant_legal_workflow_activation_identity_unique"
FINGERPRINT_INDEX_NAME: Final[str] = "tenant_legal_workflow_activation_fingerprint_unique"
HISTORY_INDEX_NAME: Final[str] = "tenant_legal_workflow_activation_revision_unique"
CURRENTNESS_INDEX_NAME: Final[str] = "tenant_legal_workflow_activation_effective_history"


class TenantLegalWorkflowActivationRegistryError(RuntimeError):
    """Base stable fail-closed registry failure."""
    default_code = "G7G_P0A_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class TenantLegalWorkflowActivationRegistryInputError(TenantLegalWorkflowActivationRegistryError):
    """Caller input or collection interface is invalid."""


class TenantLegalWorkflowActivationRegistryTransactionRequiredError(TenantLegalWorkflowActivationRegistryError):
    """Caller omitted an already-active transaction."""


class TenantLegalWorkflowActivationRegistryConflictError(TenantLegalWorkflowActivationRegistryError):
    """Immutable identity, replay, or lineage conflicts."""


class TenantLegalWorkflowActivationRegistryNotFoundError(TenantLegalWorkflowActivationRegistryError):
    """No exact tenant-scoped activation satisfies the request."""


class TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError(TenantLegalWorkflowActivationRegistryError):
    """Durable activation failed strict hydration or correlation."""


class TenantLegalWorkflowActivationRegistryRetryTransactionError(TenantLegalWorkflowActivationRegistryError):
    """Caller must abort and restart the complete transaction."""


class TenantLegalWorkflowActivationRegistryPersistenceError(TenantLegalWorkflowActivationRegistryError):
    """Mongo failed without a safe retry classification."""


def _raise(error_type: type[TenantLegalWorkflowActivationRegistryError], code: str, cause: BaseException | None = None) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _transaction(session: object) -> object:
    """Require one caller-owned session with an active transaction."""
    if session is None:
        _raise(TenantLegalWorkflowActivationRegistryTransactionRequiredError, "G7G_P0A_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        _raise(TenantLegalWorkflowActivationRegistryTransactionRequiredError, "G7G_P0A_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _raise(TenantLegalWorkflowActivationRegistryTransactionRequiredError, "G7G_P0A_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identifier(name: str, value: object) -> str:
    """Require one exact bounded persistence identity."""
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 320:
        _raise(TenantLegalWorkflowActivationRegistryInputError, f"G7G_P0A_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    """Require one explicit non-pseudo tenant."""
    tenant = _identifier("tenant_id", value)
    if tenant.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        _raise(TenantLegalWorkflowActivationRegistryInputError, "G7G_P0A_TENANT_REQUIRED")
    return tenant


def _moment(value: object) -> datetime:
    """Normalize one timezone-aware currentness instant."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _raise(TenantLegalWorkflowActivationRegistryInputError, "G7G_P0A_AT_INVALID")
    return value.astimezone(timezone.utc)


def _canonical_row(raw: Mapping[str, object]) -> dict[str, object]:
    row = dict(raw)
    row.pop("_id", None)
    return row


def _hydrate(raw: Mapping[str, object]) -> TenantLegalWorkflowActivation:
    """Strictly hydrate one canonical durable activation."""
    if not isinstance(raw, Mapping):
        _raise(TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError, "G7G_P0A_PERSISTED_RECORD_INVALID")
    row = _canonical_row(raw)
    try:
        value = TenantLegalWorkflowActivation.from_dict(row)
    except (TenantLegalWorkflowActivationError, TypeError, ValueError, KeyError) as error:
        _raise(TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError, "G7G_P0A_PERSISTED_RECORD_INVALID", error)
    if value.to_dict() != row:
        _raise(TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError, "G7G_P0A_RECORD_CORRELATION_INVALID")
    return value


def _same(left: TenantLegalWorkflowActivation, right: TenantLegalWorkflowActivation) -> bool:
    return hmac.compare_digest(left.fingerprint, right.fingerprint) and left == right


def _mongo_failure(error: PyMongoError) -> NoReturn:
    try:
        transient = error.has_error_label("TransientTransactionError")
    except Exception:
        transient = False
    if transient:
        _raise(TenantLegalWorkflowActivationRegistryRetryTransactionError, "G7G_P0A_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    _raise(TenantLegalWorkflowActivationRegistryPersistenceError, "G7G_P0A_PERSISTENCE_FAILURE", error)


def _validate_history(values: tuple[TenantLegalWorkflowActivation, ...]) -> tuple[TenantLegalWorkflowActivation, ...]:
    """Validate one contiguous, non-forking activation lineage."""
    ordered = tuple(sorted(values, key=lambda item: (item.activation_revision, item.effective_from, item.activation_id)))
    if not ordered:
        return ordered
    first = ordered[0]
    if first.activation_revision != 1 or first.supersedes_activation_id is not None:
        _raise(TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError, "G7G_P0A_HISTORY_ROOT_INVALID")
    for index, value in enumerate(ordered):
        if index == 0:
            continue
        previous = ordered[index - 1]
        if (
            value.activation_revision != previous.activation_revision + 1
            or value.supersedes_activation_id != previous.activation_id
            or value.effective_from <= previous.effective_from
            or value.tenant_id != first.tenant_id
            or value.workflow_definition_id != first.workflow_definition_id
        ):
            _raise(TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError, "G7G_P0A_HISTORY_LINEAGE_INVALID")
    return ordered


class TenantLegalWorkflowActivationRegistry:
    """Append-only exact-tenant activation persistence and currentness facade."""

    def __init__(self, collection: Any) -> None:
        """Bind one explicit collection without owning its lifecycle."""
        if collection is None:
            _raise(TenantLegalWorkflowActivationRegistryInputError, "G7G_P0A_COLLECTION_REQUIRED")
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create tenant-first immutable indexes without TTL or mutable pointer."""
        indexes = (
            ([("tenant_id", ASCENDING), ("activation_id", ASCENDING)], True, IDENTITY_INDEX_NAME),
            ([("tenant_id", ASCENDING), ("fingerprint", ASCENDING)], True, FINGERPRINT_INDEX_NAME),
            ([("tenant_id", ASCENDING), ("workflow_definition_id", ASCENDING), ("activation_revision", ASCENDING)], True, HISTORY_INDEX_NAME),
            ([("tenant_id", ASCENDING), ("workflow_definition_id", ASCENDING), ("effective_from", ASCENDING), ("activation_revision", ASCENDING)], False, CURRENTNESS_INDEX_NAME),
        )
        try:
            for keys, unique, name in indexes:
                self._collection.create_index(keys, unique=unique, name=name)
        except AttributeError as error:
            _raise(TenantLegalWorkflowActivationRegistryInputError, "G7G_P0A_COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _mongo_failure(error)

    def create_or_replay(self, value: TenantLegalWorkflowActivation, *, session: object) -> TenantLegalWorkflowActivation:
        """Insert one coherent immutable activation or return exact replay."""
        if type(value) is not TenantLegalWorkflowActivation:
            _raise(TenantLegalWorkflowActivationRegistryInputError, "G7G_P0A_ACTIVATION_REQUIRED")
        tx = _transaction(session)
        identity = {"tenant_id": value.tenant_id, "activation_id": value.activation_id}
        try:
            existing = self._collection.find_one(identity, session=tx)
            if existing is not None:
                persisted = _hydrate(cast(Mapping[str, object], existing))
                if _same(persisted, value):
                    return persisted
                _raise(TenantLegalWorkflowActivationRegistryConflictError, "G7G_P0A_DIVERGENT_REPLAY")
            collision = self._collection.find_one(
                {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
                session=tx,
            )
            if collision is not None:
                _raise(TenantLegalWorkflowActivationRegistryConflictError, "G7G_P0A_FINGERPRINT_COLLISION")
            history = self.list_history(
                value.tenant_id,
                value.workflow_definition_id,
                session=tx,
            )
            if not history:
                coherent = value.activation_revision == 1 and value.supersedes_activation_id is None
            else:
                previous = history[-1]
                coherent = (
                    value.activation_revision == previous.activation_revision + 1
                    and value.supersedes_activation_id == previous.activation_id
                    and value.effective_from > previous.effective_from
                )
            if not coherent:
                _raise(TenantLegalWorkflowActivationRegistryConflictError, "G7G_P0A_LINEAGE_CONFLICT")
            self._collection.insert_one(value.to_dict(), session=tx)
        except DuplicateKeyError as error:
            _raise(TenantLegalWorkflowActivationRegistryRetryTransactionError, "G7G_P0A_DUPLICATE_RACE_RETRY_TRANSACTION", error)
        except TenantLegalWorkflowActivationRegistryError:
            raise
        except AttributeError as error:
            _raise(TenantLegalWorkflowActivationRegistryInputError, "G7G_P0A_COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _mongo_failure(error)
        return value

    def get_by_id(self, tenant_id: str, activation_id: str, *, session: object) -> TenantLegalWorkflowActivation:
        """Read one activation without disclosing foreign-tenant existence."""
        tenant = _tenant(tenant_id)
        identity = _identifier("activation_id", activation_id)
        tx = _transaction(session)
        try:
            raw = self._collection.find_one({"tenant_id": tenant, "activation_id": identity}, session=tx)
        except PyMongoError as error:
            _mongo_failure(error)
        if raw is None:
            _raise(TenantLegalWorkflowActivationRegistryNotFoundError, "G7G_P0A_ACTIVATION_NOT_FOUND")
        value = _hydrate(cast(Mapping[str, object], raw))
        if value.tenant_id != tenant or value.activation_id != identity:
            _raise(TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError, "G7G_P0A_PERSISTED_SCOPE_MISMATCH")
        return value

    def list_history(self, tenant_id: str, workflow_definition_id: str, *, session: object) -> tuple[TenantLegalWorkflowActivation, ...]:
        """Return and validate complete immutable activation history."""
        tenant = _tenant(tenant_id)
        definition = _identifier("workflow_definition_id", workflow_definition_id)
        tx = _transaction(session)
        try:
            cursor = self._collection.find(
                {"tenant_id": tenant, "workflow_definition_id": definition},
                session=tx,
            )
            if hasattr(cursor, "sort"):
                cursor = cursor.sort([("activation_revision", ASCENDING), ("effective_from", ASCENDING), ("activation_id", ASCENDING)])
            rows = tuple(cursor)
        except AttributeError as error:
            _raise(TenantLegalWorkflowActivationRegistryInputError, "G7G_P0A_COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _mongo_failure(error)
        values = tuple(_hydrate(cast(Mapping[str, object], row)) for row in rows)
        if any(value.tenant_id != tenant or value.workflow_definition_id != definition for value in values):
            _raise(TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError, "G7G_P0A_PERSISTED_SCOPE_MISMATCH")
        return _validate_history(values)

    def resolve_current(self, tenant_id: str, workflow_definition_id: str, at: datetime, *, session: object) -> TenantLegalWorkflowActivation:
        """Derive the current activation from complete effective history."""
        moment = _moment(at)
        history = self.list_history(tenant_id, workflow_definition_id, session=session)
        applicable = tuple(value for value in history if value.effective_from <= moment)
        if not applicable:
            _raise(TenantLegalWorkflowActivationRegistryNotFoundError, "G7G_P0A_CURRENT_ACTIVATION_NOT_FOUND")
        return applicable[-1]


def ensure_indexes(collection: Any) -> None:
    """Create governed activation indexes on one explicit collection."""
    TenantLegalWorkflowActivationRegistry(collection).ensure_indexes()


__all__ = [
    "COLLECTION_NAME",
    "CURRENTNESS_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME",
    "IDENTITY_INDEX_NAME",
    "VERSION",
    "TenantLegalWorkflowActivationRegistry",
    "TenantLegalWorkflowActivationRegistryConflictError",
    "TenantLegalWorkflowActivationRegistryError",
    "TenantLegalWorkflowActivationRegistryInputError",
    "TenantLegalWorkflowActivationRegistryNotFoundError",
    "TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError",
    "TenantLegalWorkflowActivationRegistryPersistenceError",
    "TenantLegalWorkflowActivationRegistryRetryTransactionError",
    "TenantLegalWorkflowActivationRegistryTransactionRequiredError",
    "ensure_indexes",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: tenant_legal_workflow_activation_registry.py
# VERSION: v1.0.0-G7G-P0A-DURABLE-ACTIVATION-REGISTRY
# AUTHORITY BOUNDARY: immutable activation durability and derived currentness only
# TENANT POSTURE: exact tenant-first reads, writes, replay, history, and projection
# MUTABLE CURRENT POINTER: NONE
# TTL / UPDATE / REPLACE / DELETE AUTHORITY: NONE
# IAM / ASSIGNMENT / SUPERVISION AUTHORITY: NONE
# FAIL-CLOSED POSTURE: invalid input, transaction absence, conflict, corruption, ambiguity, race, and outage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
