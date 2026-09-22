"""Durable registry for WILSY OS password-reset security notifications.

TITLE: WILSY OS Password Reset Notification Registry
VERSION: v1.0.0-R10G3-PASSWORD-RESET-NOTIFICATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persists tenant-scoped post-reset notification intent and atomically
         records retryable failed-delivery attempts or terminal SENT evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_reset_notification_registry.py
COLLABORATION / OWNERSHIP: PasswordResetService will create R10G1 notification
                           intent inside its caller-owned reset transaction; a
                           later dispatcher will read and transition delivery
                           evidence after reset commit.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10G3-PASSWORD-RESET-NOTIFICATION-REGISTRY — Adds deterministic
           indexes, insert-only PENDING creation, exact tenant-scoped reads,
           caller-session propagation, strict R10G1 hydration, and CAS
           transitions for retryable failure and terminal SENT evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No email/recovery address, password, token, digest,
                            JWT, session, MFA secret, SMTP credential, or message
                            body is accepted or persisted.
TENANT BOUNDARY: Every public read/mutation requires exact tenant scope; absence
                 does not disclose another tenant's notification evidence.
AUTHORITY BOUNDARY: Durable notification-intent persistence only. No password,
                    recovery, recipient, email delivery, HTTP, authentication,
                    tenant, role, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: Callers own ClientSession and transaction lifecycle. This
                      registry never starts, commits, aborts, or retries one.
FAIL-CLOSED POSTURE: Duplicate identity, corrupt state, stale CAS, replayed SENT
                     transition, invalid tenant scope, and persistence failure
                     raise stable errors.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, Mapping, NoReturn

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from .password_reset_notification import (
    PasswordResetNotification,
    PasswordResetNotificationError,
    PasswordResetNotificationStatus,
)

VERSION: Final[str] = "v1.0.0-R10G3-PASSWORD-RESET-NOTIFICATION-REGISTRY"
COLLECTION: Final[str] = "password_reset_notifications"


class PasswordResetNotificationRegistryError(RuntimeError):
    """Stable base failure for notification persistence boundaries."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class PasswordResetNotificationNotFoundError(PasswordResetNotificationRegistryError):
    """The requested notification is absent inside the supplied tenant."""


class PasswordResetNotificationAlreadyExistsError(PasswordResetNotificationRegistryError):
    """Insert-only creation collided with an existing notification identity."""


class PasswordResetNotificationPersistedRecordInvalidError(
    PasswordResetNotificationRegistryError
):
    """Persisted notification evidence cannot hydrate through R10G1."""


class PasswordResetNotificationLifecycleConflictError(
    PasswordResetNotificationRegistryError
):
    """An exact delivery-state CAS lost to stale, divergent, or terminal state."""


class PasswordResetNotificationPersistenceError(PasswordResetNotificationRegistryError):
    """Canonical notification persistence could not complete an operation."""


def _target(collection: Any | None) -> Any:
    """Resolve an injected collection or canonical Kernel database lazily."""

    if collection is not None:
        return collection
    from tools.eos.kernel import db as kernel_db

    database = kernel_db.get_database()
    if database is None:
        raise PasswordResetNotificationPersistenceError(
            "PASSWORD_RESET_NOTIFICATION_DATABASE_UNAVAILABLE"
        )
    return database[COLLECTION]


def _session_kwargs(session: Any | None) -> dict[str, Any]:
    """Forward exactly one caller-owned session when supplied."""

    return {} if session is None else {"session": session}


def _hydrate(row: Mapping[str, Any]) -> PasswordResetNotification:
    """Hydrate persisted state only through R10G1 and reject corruption."""

    try:
        payload = dict(row)
        payload.pop("_id", None)
        return PasswordResetNotification.from_document(payload)
    except (TypeError, ValueError, PasswordResetNotificationError) as error:
        raise PasswordResetNotificationPersistedRecordInvalidError(
            "PASSWORD_RESET_NOTIFICATION_PERSISTED_RECORD_INVALID"
        ) from error


def _validate_scope(tenant_id: object, notification_id: object) -> tuple[str, str]:
    """Validate exact tenant/notification selectors without normalization."""

    if (
        not isinstance(tenant_id, str)
        or not tenant_id.strip()
        or tenant_id != tenant_id.strip()
        or not isinstance(notification_id, str)
        or not notification_id.strip()
        or notification_id != notification_id.strip()
    ):
        raise PasswordResetNotificationNotFoundError(
            "PASSWORD_RESET_NOTIFICATION_NOT_FOUND"
        )
    return tenant_id, notification_id


def _identity_query(notification: PasswordResetNotification) -> dict[str, Any]:
    """Build the exact persisted binding required for one lifecycle CAS."""

    return {
        "notification_id": notification.notification_id,
        "tenant_id": notification.tenant_id,
        "principal_id": notification.principal_id,
        "event": notification.event.value,
        "channel": notification.channel.value,
        "occurred_at": notification.occurred_at.isoformat(),
        "status": notification.status.value,
        "attempt_count": notification.attempt_count,
        "last_attempt_at": (
            None
            if notification.last_attempt_at is None
            else notification.last_attempt_at.isoformat()
        ),
        "delivered_at": (
            None
            if notification.delivered_at is None
            else notification.delivered_at.isoformat()
        ),
    }


def _transition_failure(
    source: Any,
    notification: PasswordResetNotification,
    *,
    session: Any | None,
) -> NoReturn:
    """Classify a failed CAS without broadening beyond exact tenant scope."""

    try:
        row = source.find_one(
            {
                "tenant_id": notification.tenant_id,
                "notification_id": notification.notification_id,
            },
            **_session_kwargs(session),
        )
    except PyMongoError as error:
        raise PasswordResetNotificationPersistenceError(
            "PASSWORD_RESET_NOTIFICATION_READ_FAILED"
        ) from error
    if row is None:
        raise PasswordResetNotificationNotFoundError(
            "PASSWORD_RESET_NOTIFICATION_NOT_FOUND"
        )
    persisted = _hydrate(row)
    if (
        persisted.principal_id != notification.principal_id
        or persisted.event is not notification.event
        or persisted.channel is not notification.channel
        or persisted.occurred_at != notification.occurred_at
    ):
        raise PasswordResetNotificationLifecycleConflictError(
            "PASSWORD_RESET_NOTIFICATION_BINDING_CONFLICT"
        )
    if persisted.status is PasswordResetNotificationStatus.SENT:
        raise PasswordResetNotificationLifecycleConflictError(
            "PASSWORD_RESET_NOTIFICATION_ALREADY_SENT"
        )
    raise PasswordResetNotificationLifecycleConflictError(
        "PASSWORD_RESET_NOTIFICATION_LIFECYCLE_CONFLICT"
    )


class PasswordResetNotificationRegistry:
    """Persist and transition R10G1 password-reset notification intent.

    The registry accepts an injected PyMongo collection for deterministic tests
    and otherwise resolves the canonical Kernel database lazily. It never
    accepts a recipient address or owns external delivery, retry scheduling,
    password-reset authority, authentication, or transaction lifecycle.
    """

    def __init__(self, collection: Any | None = None) -> None:
        """Bind one optional collection dependency without opening Mongo."""

        self._collection = collection

    def _source(self) -> Any:
        """Return the injected or canonical collection at operation time."""

        return _target(self._collection)

    def ensure_indexes(self) -> None:
        """Create stable identity and tenant delivery-query indexes.

        Index creation occurs outside transactions and never transitions
        notification lifecycle state.
        """

        source = self._source()
        try:
            source.create_index(
                [("notification_id", ASCENDING)],
                unique=True,
                name="password_reset_notification_identity_unique",
            )
            source.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("principal_id", ASCENDING),
                    ("status", ASCENDING),
                    ("occurred_at", ASCENDING),
                ],
                unique=False,
                name="password_reset_notification_tenant_principal_status",
            )
            source.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("status", ASCENDING),
                    ("last_attempt_at", ASCENDING),
                    ("occurred_at", ASCENDING),
                ],
                unique=False,
                name="password_reset_notification_tenant_delivery_queue",
            )
        except PyMongoError as error:
            raise PasswordResetNotificationPersistenceError(
                "PASSWORD_RESET_NOTIFICATION_INDEX_CREATION_FAILED"
            ) from error

    def create(
        self,
        notification: PasswordResetNotification,
        *,
        session: Any | None = None,
    ) -> PasswordResetNotification:
        """Insert exactly one pristine PENDING notification intent.

        Creation is insert-only and requires zero delivery attempts. The caller
        owns any surrounding reset transaction and supplies the same session to
        preserve atomic reset-plus-notification-intent commit semantics.
        """

        if not isinstance(notification, PasswordResetNotification):
            raise PasswordResetNotificationRegistryError(
                "PASSWORD_RESET_NOTIFICATION_CREATE_INVALID"
            )
        if (
            notification.status is not PasswordResetNotificationStatus.PENDING
            or notification.attempt_count != 0
            or notification.last_attempt_at is not None
            or notification.delivered_at is not None
        ):
            raise PasswordResetNotificationRegistryError(
                "PASSWORD_RESET_NOTIFICATION_CREATE_REQUIRES_PRISTINE_PENDING"
            )
        try:
            self._source().insert_one(
                notification.to_document(),
                **_session_kwargs(session),
            )
            return notification
        except DuplicateKeyError as error:
            raise PasswordResetNotificationAlreadyExistsError(
                "PASSWORD_RESET_NOTIFICATION_DUPLICATE"
            ) from error
        except PyMongoError as error:
            raise PasswordResetNotificationPersistenceError(
                "PASSWORD_RESET_NOTIFICATION_CREATE_FAILED"
            ) from error

    def get(
        self,
        *,
        tenant_id: str,
        notification_id: str,
        session: Any | None = None,
    ) -> PasswordResetNotification | None:
        """Read one exact notification within one tenant scope.

        Absence returns None and never broadens the query to another tenant.
        """

        tenant, identity = _validate_scope(tenant_id, notification_id)
        try:
            row = self._source().find_one(
                {"tenant_id": tenant, "notification_id": identity},
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise PasswordResetNotificationPersistenceError(
                "PASSWORD_RESET_NOTIFICATION_READ_FAILED"
            ) from error
        return None if row is None else _hydrate(row)

    def record_failure(
        self,
        notification: PasswordResetNotification,
        attempted_at: datetime,
        *,
        session: Any | None = None,
    ) -> PasswordResetNotification:
        """Atomically record one retryable failed external delivery attempt.

        The caller owns the session and transport failure classification. This
        mutation stores no error text or recipient and keeps lifecycle PENDING.
        """

        if not isinstance(notification, PasswordResetNotification):
            raise PasswordResetNotificationRegistryError(
                "PASSWORD_RESET_NOTIFICATION_FAILURE_INVALID"
            )
        replacement = notification.record_failure(attempted_at)
        source = self._source()
        query = _identity_query(notification)
        try:
            row = source.find_one_and_update(
                query,
                {
                    "$set": {
                        "attempt_count": replacement.attempt_count,
                        "last_attempt_at": replacement.last_attempt_at.isoformat()
                        if replacement.last_attempt_at is not None
                        else None,
                    }
                },
                return_document=ReturnDocument.AFTER,
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise PasswordResetNotificationPersistenceError(
                "PASSWORD_RESET_NOTIFICATION_FAILURE_RECORD_FAILED"
            ) from error
        if row is None:
            _transition_failure(source, notification, session=session)
        return _hydrate(row)

    def mark_sent(
        self,
        notification: PasswordResetNotification,
        delivered_at: datetime,
        *,
        session: Any | None = None,
    ) -> PasswordResetNotification:
        """Atomically record terminal SENT delivery evidence.

        The caller owns external delivery and only calls this after successful
        transport. Replayed, stale, or divergent state fails closed.
        """

        if not isinstance(notification, PasswordResetNotification):
            raise PasswordResetNotificationRegistryError(
                "PASSWORD_RESET_NOTIFICATION_SENT_INVALID"
            )
        replacement = notification.mark_sent(delivered_at)
        source = self._source()
        query = _identity_query(notification)
        try:
            row = source.find_one_and_update(
                query,
                {
                    "$set": {
                        "status": replacement.status.value,
                        "attempt_count": replacement.attempt_count,
                        "last_attempt_at": replacement.last_attempt_at.isoformat()
                        if replacement.last_attempt_at is not None
                        else None,
                        "delivered_at": replacement.delivered_at.isoformat()
                        if replacement.delivered_at is not None
                        else None,
                    }
                },
                return_document=ReturnDocument.AFTER,
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise PasswordResetNotificationPersistenceError(
                "PASSWORD_RESET_NOTIFICATION_SENT_RECORD_FAILED"
            ) from error
        if row is None:
            _transition_failure(source, notification, session=session)
        return _hydrate(row)


__all__ = [
    "COLLECTION",
    "PasswordResetNotificationAlreadyExistsError",
    "PasswordResetNotificationLifecycleConflictError",
    "PasswordResetNotificationNotFoundError",
    "PasswordResetNotificationPersistedRecordInvalidError",
    "PasswordResetNotificationPersistenceError",
    "PasswordResetNotificationRegistry",
    "PasswordResetNotificationRegistryError",
    "VERSION",
]


# ARTIFACT: password_reset_notification_registry.py
# VERSION: v1.0.0-R10G3-PASSWORD-RESET-NOTIFICATION-REGISTRY
# AUTHORITY BOUNDARY: durable post-reset notification-intent persistence only
# TENANT POSTURE: exact tenant-scoped reads/CAS; no cross-tenant fallback
# FAIL-CLOSED POSTURE: duplicate, corrupt, stale, replayed, and persistence failure rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
