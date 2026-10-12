"""WILSY OS durable Legal Operations courier observation registry.

TITLE: Legal Operations Courier Observation Registry
VERSION: v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable L8-8A courier observations append-only with exact
         tenant scope, exact replay, strict corruption rejection, bounded
         document history reads and caller-owned Mongo transaction semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_courier_observation_registry.py
COLLABORATION / OWNERSHIP: L8-8A owns courier observation meaning/integrity.
                            This registry owns durable persistence and bounded
                            reads only. Callers own sessions, transactions,
                            retries and commit/abort reconciliation.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY establishes
           exact tenant+observation and tenant+provider-event uniqueness,
           append-only replay, strict hydration, bounded document/provider
           history indexes, no TTL lifecycle, cross-tenant absence, caller
           transaction propagation, and duplicate-race whole-transaction retry.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only L8-8A opaque normalized observation
                             evidence. No raw provider payload, address, GPS,
                             signature image, document bytes, credentials,
                             tokens, personal contact data or payment data.
TENANT BOUNDARY: Every operational read/write begins with exact tenant_id;
                 there is no global observation/provider-event lookup or
                 cross-tenant existence oracle.
AUTHORITY BOUNDARY: Persistence and bounded evidence-history reads only. This
                    registry does not contact couriers, mutate ProcessDocument
                    or custody, decide service, generate returns, send
                    notifications, file with Court, issue invoices, execute
                    payment, settle funds, authenticate or authorize callers.
TRANSACTION BOUNDARY: Caller supplies and owns every active Mongo transaction.
                      This registry never starts, commits, aborts, retries or
                      reconciles a transaction. Duplicate-key races require
                      caller abort and fresh whole-transaction retry.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority; settlement remains separate.
FAIL-CLOSED DECLARATION: Missing transaction, malformed scope, persisted-shape
                         drift, fingerprint corruption, divergent replay,
                         duplicate races, oversized history and Mongo failures
                         reject without repair, inference or authority expansion.
"""
from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_courier_observation import (
    LEGAL_COURIER_OBSERVATION_FIELDS,
    LegalCourierObservation,
    LegalCourierObservationError,
)


VERSION: Final[str] = "v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY"
COLLECTION: Final[str] = "legal_courier_observations"

INDEX_TENANT_OBSERVATION: Final[str] = (
    "legal_courier_tenant_observation_unique"
)
INDEX_TENANT_PROVIDER_EVENT: Final[str] = (
    "legal_courier_tenant_provider_event_unique"
)
INDEX_TENANT_DOCUMENT_OBSERVED: Final[str] = (
    "legal_courier_tenant_document_observed"
)
INDEX_TENANT_TRACKING_OBSERVED: Final[str] = (
    "legal_courier_tenant_tracking_observed"
)

MAX_DOCUMENT_OBSERVATIONS: Final[int] = 1000

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_PERSISTED_FIELDS: Final[frozenset[str]] = frozenset(
    set(LEGAL_COURIER_OBSERVATION_FIELDS) | {"_id"}
)


class LegalCourierObservationRegistryError(RuntimeError):
    """Base non-sensitive fail-closed courier observation registry error."""


class LegalCourierObservationRegistryConflictError(
    LegalCourierObservationRegistryError
):
    """An immutable replay identity collides with divergent evidence."""


class LegalCourierObservationRegistryTransactionRequiredError(
    LegalCourierObservationRegistryError
):
    """Caller did not provide one active Mongo transaction."""


class LegalCourierObservationRegistryRetryTransactionError(
    LegalCourierObservationRegistryError
):
    """A write race requires caller abort and fresh whole-transaction retry."""


class LegalCourierObservationRegistryPersistenceError(
    LegalCourierObservationRegistryError
):
    """Mongo persistence/read infrastructure is unavailable or failed."""


def _fail(code: str) -> NoReturn:
    """Raise one bounded registry validation failure."""
    raise LegalCourierObservationRegistryError(code)


def _tenant(value: object) -> str:
    """Require one exact non-pseudo tenant identity for registry scope."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
        or value.casefold() in _FORBIDDEN_TENANTS
    ):
        _fail("L8_8B_TENANT_INVALID")
    return value


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity for a read predicate."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L8_8B_{name.upper()}_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    """Return the caller session only when one transaction is active."""
    if session is None:
        raise LegalCourierObservationRegistryTransactionRequiredError(
            "L8_8B_TRANSACTION_REQUIRED"
        )
    active = getattr(session, "in_transaction", False)
    if callable(active):
        active = active()
    if active is not True:
        raise LegalCourierObservationRegistryTransactionRequiredError(
            "L8_8B_TRANSACTION_REQUIRED"
        )
    return session


def _target(collection: Any) -> Any:
    """Require one Mongo-like collection handle."""
    if collection is None:
        _fail("L8_8B_COLLECTION_REQUIRED")
    return collection


def _raise_mongo(error: PyMongoError) -> NoReturn:
    """Translate driver failures without leaking provider/database details."""
    raise LegalCourierObservationRegistryPersistenceError(
        "L8_8B_PERSISTENCE_UNAVAILABLE"
    ) from error


def _hydrate(row: Mapping[str, object]) -> LegalCourierObservation:
    """Strictly hydrate one durable row and reject injected/corrupt fields."""
    try:
        if (
            not isinstance(row, Mapping)
            or not set(row).issubset(_PERSISTED_FIELDS)
            or not set(LEGAL_COURIER_OBSERVATION_FIELDS).issubset(row)
        ):
            _fail("L8_8B_CORRUPT_OBSERVATION")
        payload = {
            field: row[field]
            for field in LEGAL_COURIER_OBSERVATION_FIELDS
        }
        return LegalCourierObservation.from_dict(payload)
    except LegalCourierObservationRegistryError:
        raise
    except (KeyError, TypeError, LegalCourierObservationError) as error:
        raise LegalCourierObservationRegistryError(
            "L8_8B_CORRUPT_OBSERVATION"
        ) from error


def ensure_indexes(collection: Any) -> None:
    """Create deterministic immutable identity/read indexes with no TTL."""
    target = _target(collection)
    try:
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("observation_id", ASCENDING),
            ],
            name=INDEX_TENANT_OBSERVATION,
            unique=True,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("provider_key", ASCENDING),
                ("provider_event_reference", ASCENDING),
            ],
            name=INDEX_TENANT_PROVIDER_EVENT,
            unique=True,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("document_id", ASCENDING),
                ("observed_at", ASCENDING),
            ],
            name=INDEX_TENANT_DOCUMENT_OBSERVED,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("provider_key", ASCENDING),
                ("tracking_reference", ASCENDING),
                ("observed_at", ASCENDING),
            ],
            name=INDEX_TENANT_TRACKING_OBSERVED,
        )
    except PyMongoError as error:
        _raise_mongo(error)


class LegalCourierObservationRegistry:
    """Append-only caller-transaction persistence for L8-8A observations."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        """Bind one explicit collection without owning its client/session."""
        self._collection = _target(collection)

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create L8-8B indexes outside operational transactions."""
        ensure_indexes(collection)

    def create_or_replay(
        self,
        observation: LegalCourierObservation,
        *,
        session: Any,
    ) -> LegalCourierObservation:
        """Persist one immutable observation or return one exact durable replay.

        Replay may be reached by either canonical observation identity or the
        exact provider-event identity. Any divergence fails closed. A duplicate
        key raised by Mongo is not reconciled inside the current transaction;
        callers must abort and retry the entire transaction from fresh state.
        """
        tx = _active_transaction(session)
        if type(observation) is not LegalCourierObservation:
            _fail("L8_8B_OBSERVATION_REQUIRED")
        try:
            observation.__post_init__()
        except LegalCourierObservationError as error:
            raise LegalCourierObservationRegistryError(
                "L8_8B_OBSERVATION_INVALID"
            ) from error

        tenant = observation.tenant_id
        observation_query = {
            "tenant_id": tenant,
            "observation_id": observation.observation_id,
        }
        provider_event_query = {
            "tenant_id": tenant,
            "provider_key": observation.provider_key,
            "provider_event_reference": observation.provider_event_reference,
        }

        try:
            existing = self._collection.find_one(
                observation_query,
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)

        if existing is not None:
            persisted = _hydrate(existing)
            if persisted != observation:
                raise LegalCourierObservationRegistryConflictError(
                    "L8_8B_DIVERGENT_OBSERVATION_IDENTITY"
                )
            return persisted

        try:
            provider_existing = self._collection.find_one(
                provider_event_query,
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)

        if provider_existing is not None:
            persisted = _hydrate(provider_existing)
            if persisted != observation:
                raise LegalCourierObservationRegistryConflictError(
                    "L8_8B_DIVERGENT_PROVIDER_EVENT"
                )
            return persisted

        try:
            self._collection.insert_one(
                observation.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            raise LegalCourierObservationRegistryRetryTransactionError(
                "L8_8B_RETRY_TRANSACTION_REQUIRED"
            ) from error
        except PyMongoError as error:
            _raise_mongo(error)

        return observation

    def get_by_observation_id(
        self,
        *,
        tenant_id: str,
        observation_id: str,
        session: Any,
    ) -> LegalCourierObservation | None:
        """Return exact tenant-scoped observation evidence or canonical absence."""
        tx = _active_transaction(session)
        tenant = _tenant(tenant_id)
        identity = _identity("observation_id", observation_id)
        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "observation_id": identity,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)
        if row is None:
            return None
        value = _hydrate(row)
        if (
            value.tenant_id != tenant
            or value.observation_id != identity
        ):
            _fail("L8_8B_BINDING_MISMATCH")
        return value

    def list_document_observations(
        self,
        *,
        tenant_id: str,
        case_matter_id: str,
        document_id: str,
        session: Any,
    ) -> tuple[LegalCourierObservation, ...]:
        """Return bounded chronological observation history for one document.

        The query is exact tenant/matter/document scoped. Every returned row is
        strictly hydrated and recorrelation-checked before sorting. This method
        exposes history only; it does not select a provider or Legal current
        state, infer delivery, or drive a lifecycle transition.
        """
        tx = _active_transaction(session)
        tenant = _tenant(tenant_id)
        matter = _identity("case_matter_id", case_matter_id)
        document = _identity("document_id", document_id)

        try:
            cursor = self._collection.find(
                {
                    "tenant_id": tenant,
                    "case_matter_id": matter,
                    "document_id": document,
                },
                session=tx,
            )
            if hasattr(cursor, "limit"):
                cursor = cursor.limit(MAX_DOCUMENT_OBSERVATIONS + 1)
            rows = list(cursor)
        except PyMongoError as error:
            _raise_mongo(error)

        if len(rows) > MAX_DOCUMENT_OBSERVATIONS:
            _fail("L8_8B_DOCUMENT_HISTORY_LIMIT_EXCEEDED")

        values: list[LegalCourierObservation] = []
        for row in rows:
            value = _hydrate(row)
            if (
                value.tenant_id != tenant
                or value.case_matter_id != matter
                or value.document_id != document
            ):
                _fail("L8_8B_BINDING_MISMATCH")
            values.append(value)

        values.sort(
            key=lambda item: (
                item.observed_at,
                item.observation_id,
            )
        )
        return tuple(values)


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_DOCUMENT_OBSERVED",
    "INDEX_TENANT_OBSERVATION",
    "INDEX_TENANT_PROVIDER_EVENT",
    "INDEX_TENANT_TRACKING_OBSERVED",
    "MAX_DOCUMENT_OBSERVATIONS",
    "VERSION",
    "LegalCourierObservationRegistry",
    "LegalCourierObservationRegistryConflictError",
    "LegalCourierObservationRegistryError",
    "LegalCourierObservationRegistryPersistenceError",
    "LegalCourierObservationRegistryRetryTransactionError",
    "LegalCourierObservationRegistryTransactionRequiredError",
    "ensure_indexes",
]


# ARTIFACT: legal_courier_observation_registry.py
# VERSION: v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY
# AUTHORITY BOUNDARY: append-only courier observation persistence/history reads only; no provider, lifecycle, custody, service, return, notification, Court, IAM, AI, billing or financial authority
# TENANT POSTURE: every operational query and immutable identity is exact-tenant scoped; cross-tenant absence is canonical absence
# TRANSACTION POSTURE: caller owns one active transaction; duplicate races require caller abort plus fresh whole-transaction retry
# TTL POSTURE: no TTL deletion index; courier observations remain durable evidence
# FAIL-CLOSED POSTURE: malformed scope, corruption, divergence, duplicate race, history overflow and Mongo failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
