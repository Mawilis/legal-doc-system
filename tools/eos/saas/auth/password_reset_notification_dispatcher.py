"""Post-reset security-notification dispatch orchestration for WILSY OS.

TITLE: WILSY OS Password Reset Notification Dispatcher
VERSION: v1.0.0-R10G5-PASSWORD-RESET-NOTIFICATION-DISPATCHER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Rehydrates one durable reset-notification intent, re-proves the
         principal's current email against ACTIVE verified recovery-contact
         authority, delegates token-free external delivery, and records exact
         failed-attempt or terminal SENT evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_reset_notification_dispatcher.py
COLLABORATION / OWNERSHIP: R10G3 owns durable notification lifecycle state;
                           R10E verified-contact authority proves recipient
                           eligibility; AuthRegistry supplies current durable
                           principal/email truth; an injected delivery adapter
                           owns external transport only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10G5-PASSWORD-RESET-NOTIFICATION-DISPATCHER — Adds exact
           tenant/notification lookup, current-principal and verified-contact
           revalidation, transient recipient construction, retry evidence on
           transport failure, terminal SENT persistence, and idempotent handling
           of already-SENT durable notification state.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Recipient email exists only in transient process
                            memory and the delivery message. No reset token,
                            password, recovery capability, digest, JWT, session,
                            refresh token, MFA secret, or SMTP credential enters
                            durable notification state or public results.
TENANT BOUNDARY: Tenant scope comes from the caller's durable outbox selector
                 and is rechecked against the persisted notification, verified
                 contact, and current principal. No cross-tenant fallback.
AUTHORITY BOUNDARY: Notification delivery orchestration only. This service
                    cannot reset passwords, issue recovery capabilities, verify
                    contacts, create sessions/JWTs, mutate roles, or create
                    tenant/financial truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: External delivery occurs outside Mongo transactions.
                      Registry state transitions are single atomic CAS writes.
FAIL-CLOSED POSTURE: Missing/corrupt notification, missing/stale verified
                     recipient authority, principal mismatch, transport failure,
                     and unconfirmed delivery evidence raise stable code-only
                     errors. A failed transport remains durably retryable.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Final, Protocol, runtime_checkable

from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.auth.password_recovery_contact import (
    VerifiedRecoveryContactChannel,
)
from tools.eos.saas.auth.password_recovery_contact_registry import (
    VerifiedRecoveryContactPersistenceError,
    VerifiedRecoveryContactRegistry,
    VerifiedRecoveryContactRegistryError,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    PasswordRecoveryRequestServiceError,
    normalize_recovery_email,
    recovery_address_digest,
)

from .password_reset_notification import (
    PasswordResetNotification,
    PasswordResetNotificationStatus,
)
from .password_reset_notification_registry import (
    PasswordResetNotificationLifecycleConflictError,
    PasswordResetNotificationNotFoundError,
    PasswordResetNotificationPersistenceError,
    PasswordResetNotificationRegistry,
    PasswordResetNotificationRegistryError,
)

VERSION: Final[str] = "v1.0.0-R10G5-PASSWORD-RESET-NOTIFICATION-DISPATCHER"


class PasswordResetNotificationDispatchError(RuntimeError):
    """Stable secret-free dispatch failure.

    The code contains no recipient, tenant lookup result, principal lookup
    result, transport detail, password, reset token, or recovery capability.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class PasswordResetNotificationDeliveryMessage:
    """Transient token-free message payload for an authorized recipient.

    The recipient email is never persisted by this value. No reset token, login
    token, password, capability, session, JWT, or MFA material is admitted.
    """

    recipient_email: str
    occurred_at: datetime

    def __post_init__(self) -> None:
        try:
            normalized = normalize_recovery_email(self.recipient_email)
        except PasswordRecoveryRequestServiceError as error:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_RECIPIENT_INVALID"
            ) from error
        if normalized != self.recipient_email:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_RECIPIENT_NOT_NORMALIZED"
            )
        if (
            not isinstance(self.occurred_at, datetime)
            or self.occurred_at.tzinfo is None
            or self.occurred_at.utcoffset() is None
        ):
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_OCCURRED_AT_INVALID"
            )
        object.__setattr__(self, "occurred_at", self.occurred_at.astimezone(timezone.utc))


@dataclass(frozen=True, slots=True)
class PasswordResetNotificationDispatchResult:
    """Non-sensitive receipt for dispatch completion or prior durable completion."""

    status: str = "PASSWORD_RESET_NOTIFICATION_SENT"


@runtime_checkable
class PasswordResetNotificationDeliveryAdapter(Protocol):
    """External token-free transport boundary for one security notification."""

    def deliver(self, message: PasswordResetNotificationDeliveryMessage) -> None:
        """Deliver one already-authorized message or raise without leaking secrets."""


def _utc(value: object) -> datetime:
    """Require one aware observation timestamp and normalize it to UTC."""

    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise PasswordResetNotificationDispatchError(
            "PASSWORD_RESET_NOTIFICATION_OBSERVED_AT_INVALID"
        )
    try:
        return value.astimezone(timezone.utc)
    except (OverflowError, ValueError) as error:
        raise PasswordResetNotificationDispatchError(
            "PASSWORD_RESET_NOTIFICATION_OBSERVED_AT_INVALID"
        ) from error


def _selector(value: object, code: str) -> str:
    """Require one exact non-empty selector without trimming or aliasing."""

    if not isinstance(value, str) or not value or value != value.strip():
        raise PasswordResetNotificationDispatchError(code)
    return value


class PasswordResetNotificationDispatcher:
    """Dispatch durable post-reset security notifications from sovereign truth.

    Callers supply only the durable tenant and notification selectors plus an
    explicit observation time. Recipient authority is resolved server-side from
    the notification principal, ACTIVE verified recovery-contact evidence, and
    the principal's current durable email. External delivery is never attempted
    when any of those bindings diverge.
    """

    def __init__(
        self,
        *,
        notification_registry: PasswordResetNotificationRegistry,
        contact_registry: VerifiedRecoveryContactRegistry,
        auth_registry: AuthRegistry,
        delivery_adapter: PasswordResetNotificationDeliveryAdapter,
    ) -> None:
        """Bind canonical authorities and one external delivery capability."""

        if not isinstance(notification_registry, PasswordResetNotificationRegistry):
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_REGISTRY_INVALID"
            )
        if not isinstance(contact_registry, VerifiedRecoveryContactRegistry):
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_CONTACT_REGISTRY_INVALID"
            )
        if not isinstance(auth_registry, AuthRegistry):
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_AUTH_REGISTRY_INVALID"
            )
        if not isinstance(delivery_adapter, PasswordResetNotificationDeliveryAdapter):
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_DELIVERY_ADAPTER_INVALID"
            )

        self._notification_registry = notification_registry
        self._contact_registry = contact_registry
        self._auth_registry = auth_registry
        self._delivery_adapter = delivery_adapter

    def dispatch(
        self,
        *,
        tenant_id: str,
        notification_id: str,
        observed_at: datetime,
    ) -> PasswordResetNotificationDispatchResult:
        """Deliver one pending notification and record durable attempt evidence.

        Already-SENT state is idempotent success. Missing or stale recipient
        authority leaves the notification PENDING without claiming a transport
        attempt. External transport failure records one retryable failed attempt
        before returning a stable internal error.
        """

        tenant = _selector(
            tenant_id,
            "PASSWORD_RESET_NOTIFICATION_TENANT_INVALID",
        )
        identity = _selector(
            notification_id,
            "PASSWORD_RESET_NOTIFICATION_ID_INVALID",
        )
        observed = _utc(observed_at)

        try:
            notification = self._notification_registry.get(
                tenant_id=tenant,
                notification_id=identity,
            )
        except PasswordResetNotificationNotFoundError as error:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_NOT_FOUND"
            ) from error
        except PasswordResetNotificationPersistenceError as error:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_READ_FAILED"
            ) from error
        except PasswordResetNotificationRegistryError as error:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_INTEGRITY_FAILED"
            ) from error

        if notification is None:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_NOT_FOUND"
            )
        if (
            notification.tenant_id != tenant
            or notification.notification_id != identity
        ):
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_BINDING_MISMATCH"
            )
        if notification.status is PasswordResetNotificationStatus.SENT:
            return PasswordResetNotificationDispatchResult()

        try:
            contact = self._contact_registry.get_active_by_principal(
                tenant_id=tenant,
                principal_id=notification.principal_id,
                channel=VerifiedRecoveryContactChannel.EMAIL,
            )
        except VerifiedRecoveryContactPersistenceError as error:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_CONTACT_LOOKUP_FAILED"
            ) from error
        except VerifiedRecoveryContactRegistryError as error:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_CONTACT_INTEGRITY_FAILED"
            ) from error
        if contact is None:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_RECIPIENT_UNAVAILABLE"
            )
        if (
            contact.tenant_id != tenant
            or contact.principal_id != notification.principal_id
        ):
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_RECIPIENT_BINDING_MISMATCH"
            )

        try:
            user = self._auth_registry.get_user_by_id(notification.principal_id)
        except Exception as error:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_PRINCIPAL_LOOKUP_FAILED"
            ) from error
        if (
            user is None
            or user.id != notification.principal_id
            or user.tenantId != tenant
        ):
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_PRINCIPAL_UNAVAILABLE"
            )

        try:
            current_email = normalize_recovery_email(str(user.email))
        except PasswordRecoveryRequestServiceError as error:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_RECIPIENT_UNAVAILABLE"
            ) from error
        if recovery_address_digest(current_email) != contact.address_digest:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_RECIPIENT_STALE"
            )

        message = PasswordResetNotificationDeliveryMessage(
            recipient_email=current_email,
            occurred_at=notification.occurred_at,
        )
        try:
            self._delivery_adapter.deliver(message)
        except Exception as delivery_error:
            try:
                self._notification_registry.record_failure(
                    notification,
                    observed,
                )
            except Exception as evidence_error:
                raise PasswordResetNotificationDispatchError(
                    "PASSWORD_RESET_NOTIFICATION_DELIVERY_FAILED_EVIDENCE_UNCONFIRMED"
                ) from evidence_error
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_DELIVERY_FAILED"
            ) from delivery_error

        try:
            self._notification_registry.mark_sent(notification, observed)
        except PasswordResetNotificationLifecycleConflictError as error:
            try:
                current = self._notification_registry.get(
                    tenant_id=tenant,
                    notification_id=identity,
                )
            except Exception as read_error:
                raise PasswordResetNotificationDispatchError(
                    "PASSWORD_RESET_NOTIFICATION_SENT_EVIDENCE_UNCONFIRMED"
                ) from read_error
            if (
                current is not None
                and current.status is PasswordResetNotificationStatus.SENT
            ):
                return PasswordResetNotificationDispatchResult()
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_SENT_EVIDENCE_UNCONFIRMED"
            ) from error
        except PasswordResetNotificationRegistryError as error:
            raise PasswordResetNotificationDispatchError(
                "PASSWORD_RESET_NOTIFICATION_SENT_EVIDENCE_UNCONFIRMED"
            ) from error

        return PasswordResetNotificationDispatchResult()


__all__ = [
    "PasswordResetNotificationDeliveryAdapter",
    "PasswordResetNotificationDeliveryMessage",
    "PasswordResetNotificationDispatchError",
    "PasswordResetNotificationDispatchResult",
    "PasswordResetNotificationDispatcher",
    "VERSION",
]


# ARTIFACT: password_reset_notification_dispatcher.py
# VERSION: v1.0.0-R10G5-PASSWORD-RESET-NOTIFICATION-DISPATCHER
# AUTHORITY BOUNDARY: verified-recipient notification delivery orchestration only
# TENANT POSTURE: exact notification/contact/principal tenant binding; no fallback
# FAIL-CLOSED POSTURE: stale recipient, transport failure, and unconfirmed evidence reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
