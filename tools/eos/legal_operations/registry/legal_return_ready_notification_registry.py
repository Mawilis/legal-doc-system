"""WILSY OS durable Legal return-ready notification-intent registry.

TITLE: Legal Operations Return-Ready Notification Intent Registry
VERSION: v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable L8-8E RETURN_READY notification intents append-only
         with exact tenant scope, exact replay, strict corruption rejection,
         caller-owned active transactions and explicit no-TTL semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_return_ready_notification_registry.py
COLLABORATION / OWNERSHIP: L8-8E owns immutable RETURN_READY intent meaning and
                            integrity. This registry owns durable append/replay
                            and exact reads only. Recipient resolution, dispatch,
                            delivery attempts, transport and delivery evidence
                            remain separate future owners.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY
           establishes tenant+notification and tenant+return uniqueness,
           exact replay, strict hydration, caller-owned transaction semantics,
           cross-tenant absence, no TTL and duplicate-race whole-transaction
           retry without recipient/transport/delivery lifecycle authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only L8-8E opaque Legal notification intent
                             evidence. No recipient, email, phone, channel,
                             message body, provider, credential, secret, token,
                             document bytes, personal contact or payment data.
TENANT BOUNDARY: Every operational read/write begins with exact tenant_id; there
                 is no global notification/return lookup or existence oracle.
AUTHORITY BOUNDARY: Append-only intent persistence/read only. No recipient
                    resolution, delivery, retry scheduling, lifecycle mutation,
                    Court filing, invoice truth, payment, execution or settlement.
TRANSACTION BOUNDARY: Caller supplies and owns every active Mongo transaction.
                      Registry never starts, commits, aborts, retries or
                      reconciles a transaction. Duplicate races require caller
                      abort and fresh whole-transaction retry.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority; settlement remains separate.
FAIL-CLOSED DECLARATION: Missing transaction, malformed scope, injected/corrupt
                         persisted fields, fingerprint drift, divergent replay,
                         duplicate races and Mongo failures reject without repair.
"""
from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_return_ready_notification import (
    LegalReturnReadyNotification,
    LegalReturnReadyNotificationError,
)


VERSION: Final[str] = "v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY"
COLLECTION: Final[str] = "legal_return_ready_notifications"

INDEX_TENANT_NOTIFICATION: Final[str] = (
    "legal_return_ready_tenant_notification_unique"
)
INDEX_TENANT_RETURN: Final[str] = "legal_return_ready_tenant_return_unique"
INDEX_TENANT_DOCUMENT_OCCURRED: Final[str] = (
    "legal_return_ready_tenant_document_occurred"
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_PERSISTED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "_id",
        "schema",
        "notification_version",
        "tenant_id",
        "notification_id",
        "instruction_id",
        "document_id",
        "return_id",
        "return_fingerprint",
        "event",
        "occurred_at",
        "status",
        "fingerprint",
    }
)
_REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    _PERSISTED_FIELDS - {"_id"}
)


class LegalReturnReadyNotificationRegistryError(RuntimeError):
    """Base non-sensitive fail-closed notification registry error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalReturnReadyNotificationRegistryConflictError(
    LegalReturnReadyNotificationRegistryError
):
    """An immutable replay identity collides with divergent intent evidence."""


class LegalReturnReadyNotificationRegistryTransactionRequiredError(
    LegalReturnReadyNotificationRegistryError
):
    """Caller did not provide one active Mongo transaction."""


class LegalReturnReadyNotificationRegistryRetryTransactionError(
    LegalReturnReadyNotificationRegistryError
):
    """A write race requires caller abort and fresh whole-transaction retry."""


class LegalReturnReadyNotificationRegistryPersistenceError(
    LegalReturnReadyNotificationRegistryError
):
    """Mongo persistence/read infrastructure is unavailable or failed."""


def _fail(code: str) -> NoReturn:
    raise LegalReturnReadyNotificationRegistryError(code)


def _tenant(value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
        or value.casefold() in _FORBIDDEN_TENANTS
    ):
        _fail("L8_8F_TENANT_INVALID")
    return value


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L8_8F_{name.upper()}_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    if session is None:
        raise LegalReturnReadyNotificationRegistryTransactionRequiredError(
            "L8_8F_TRANSACTION_REQUIRED"
        )
    active = getattr(session, "in_transaction", False)
    if callable(active):
        active = active()
    if active is not True:
        raise LegalReturnReadyNotificationRegistryTransactionRequiredError(
            "L8_8F_TRANSACTION_REQUIRED"
        )
    return session


def _target(collection: Any) -> Any:
    if collection is None:
        _fail("L8_8F_COLLECTION_REQUIRED")
    return collection


def _raise_mongo(error: PyMongoError) -> NoReturn:
    raise LegalReturnReadyNotificationRegistryPersistenceError(
        "L8_8F_PERSISTENCE_UNAVAILABLE"
    ) from error


def _hydrate(row: Mapping[str, object]) -> LegalReturnReadyNotification:
    try:
        if (
            not isinstance(row, Mapping)
            or not set(row).issubset(_PERSISTED_FIELDS)
            or not _REQUIRED_FIELDS.issubset(row)
        ):
            _fail("L8_8F_CORRUPT_NOTIFICATION")
        payload = {field: row[field] for field in _REQUIRED_FIELDS}
        return LegalReturnReadyNotification.from_dict(payload)
    except LegalReturnReadyNotificationRegistryError:
        raise
    except (
        KeyError,
        TypeError,
        ValueError,
        LegalReturnReadyNotificationError,
    ) as error:
        raise LegalReturnReadyNotificationRegistryError(
            "L8_8F_CORRUPT_NOTIFICATION"
        ) from error


def ensure_indexes(collection: Any) -> None:
    """Create deterministic immutable identity/read indexes with no TTL."""
    target = _target(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("notification_id", ASCENDING)],
            name=INDEX_TENANT_NOTIFICATION,
            unique=True,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("return_id", ASCENDING)],
            name=INDEX_TENANT_RETURN,
            unique=True,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("document_id", ASCENDING),
                ("occurred_at", ASCENDING),
            ],
            name=INDEX_TENANT_DOCUMENT_OCCURRED,
        )
    except PyMongoError as error:
        _raise_mongo(error)


class LegalReturnReadyNotificationRegistry:
    """Append-only caller-transaction persistence for L8-8E notification intent."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        self._collection = _target(collection)

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create L8-8F indexes outside operational transactions."""
        ensure_indexes(collection)

    def create_or_replay(
        self,
        notification: LegalReturnReadyNotification,
        *,
        session: Any,
    ) -> LegalReturnReadyNotification:
        """Persist one immutable intent or return one exact durable replay.

        Replay may be reached by notification identity or canonical return
        identity. Any divergence fails closed. Duplicate-key races are surfaced
        as whole-transaction retry requirements; they are never reconciled
        inside the current transaction.
        """
        tx = _active_transaction(session)
        if type(notification) is not LegalReturnReadyNotification:
            _fail("L8_8F_NOTIFICATION_REQUIRED")
        try:
            notification.__post_init__()
        except LegalReturnReadyNotificationError as error:
            raise LegalReturnReadyNotificationRegistryError(
                "L8_8F_NOTIFICATION_INVALID"
            ) from error

        notification_query = {
            "tenant_id": notification.tenant_id,
            "notification_id": notification.notification_id,
        }
        return_query = {
            "tenant_id": notification.tenant_id,
            "return_id": notification.return_id,
        }

        try:
            existing = self._collection.find_one(
                notification_query,
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)
        if existing is not None:
            persisted = _hydrate(existing)
            if persisted != notification:
                raise LegalReturnReadyNotificationRegistryConflictError(
                    "L8_8F_DIVERGENT_NOTIFICATION_IDENTITY"
                )
            return persisted

        try:
            return_existing = self._collection.find_one(
                return_query,
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)
        if return_existing is not None:
            persisted = _hydrate(return_existing)
            if persisted != notification:
                raise LegalReturnReadyNotificationRegistryConflictError(
                    "L8_8F_DIVERGENT_RETURN_IDENTITY"
                )
            return persisted

        try:
            self._collection.insert_one(
                notification.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            raise LegalReturnReadyNotificationRegistryRetryTransactionError(
                "L8_8F_RETRY_TRANSACTION_REQUIRED"
            ) from error
        except PyMongoError as error:
            _raise_mongo(error)

        return notification

    def get_by_notification_id(
        self,
        *,
        tenant_id: str,
        notification_id: str,
        session: Any,
    ) -> LegalReturnReadyNotification | None:
        """Return exact tenant-scoped intent evidence or canonical absence."""
        tx = _active_transaction(session)
        tenant = _tenant(tenant_id)
        identity = _identity("notification_id", notification_id)
        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "notification_id": identity,
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
            or value.notification_id != identity
        ):
            _fail("L8_8F_SCOPE_MISMATCH")
        return value

    def get_by_return_id(
        self,
        *,
        tenant_id: str,
        return_id: str,
        session: Any,
    ) -> LegalReturnReadyNotification | None:
        """Return one exact tenant-scoped RETURN_READY intent by return identity."""
        tx = _active_transaction(session)
        tenant = _tenant(tenant_id)
        identity = _identity("return_id", return_id)
        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "return_id": identity,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)
        if row is None:
            return None
        value = _hydrate(row)
        if value.tenant_id != tenant or value.return_id != identity:
            _fail("L8_8F_SCOPE_MISMATCH")
        return value


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_DOCUMENT_OCCURRED",
    "INDEX_TENANT_NOTIFICATION",
    "INDEX_TENANT_RETURN",
    "VERSION",
    "LegalReturnReadyNotificationRegistry",
    "LegalReturnReadyNotificationRegistryConflictError",
    "LegalReturnReadyNotificationRegistryError",
    "LegalReturnReadyNotificationRegistryPersistenceError",
    "LegalReturnReadyNotificationRegistryRetryTransactionError",
    "LegalReturnReadyNotificationRegistryTransactionRequiredError",
    "ensure_indexes",
]


# ARTIFACT: legal_return_ready_notification_registry.py
# VERSION: v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY
# AUTHORITY BOUNDARY: append-only RETURN_READY intent persistence/read only
# TENANT POSTURE: every operation is exact tenant scoped; no global existence oracle
# TRANSACTION POSTURE: caller owns active transaction; duplicate races require fresh whole-transaction retry
# DELIVERY POSTURE: no recipient/channel/provider/message/attempt/delivery lifecycle fields or mutations
# TTL POSTURE: no TTL index; durable intent remains until separately governed retention exists
# FAIL-CLOSED POSTURE: malformed/corrupt/divergent/racy/persistence failure rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
