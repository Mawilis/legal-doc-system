"""Immutable post-reset security-notification state for WILSY OS auth.

TITLE: WILSY OS Password Reset Security Notification Domain
VERSION: v1.0.0-R10G1-PASSWORD-RESET-NOTIFICATION-DOMAIN
AUTHORITY: Wilsy OS Core Governance
EPITOME: Defines one immutable, tenant/principal-bound password-reset security
         notification intent whose delivery lifecycle is retryable without
         storing any recovery address, token, password, or transport secret.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_reset_notification.py
COLLABORATION / OWNERSHIP: PasswordResetService will create notification intent
                           inside its caller-owned reset transaction; a later
                           registry persists it and a later dispatcher performs
                           external delivery only after durable reset commit.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10G1-PASSWORD-RESET-NOTIFICATION-DOMAIN — Introduces exact
           tenant/principal binding, PASSWORD_RESET_COMPLETED event semantics,
           retryable PENDING delivery state, terminal SENT state, deterministic
           attempt accounting, strict UTC lifecycle validation, serialization,
           and secret-free hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No raw email/recovery address, password, reset token,
                            capability digest, JWT, session, refresh token, MFA
                            secret, SMTP credential, or message body is stored.
TENANT BOUNDARY: Each event is bound to one exact canonical tenant_id and
                 principal_id; no alias resolution or cross-tenant fallback.
AUTHORITY BOUNDARY: Durable notification-intent lifecycle state only. This file
                    grants no password, recovery, delivery, authentication,
                    persistence, HTTP, tenant, role, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: No database, client session, transaction, network,
                      environment, or wall-clock ownership exists.
FAIL-CLOSED POSTURE: Malformed identifiers, timestamps, attempts, contradictory
                     delivery state, replayed terminal delivery, and unknown
                     persisted fields raise stable domain errors.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping, Self


VERSION: Final[str] = "v1.0.0-R10G1-PASSWORD-RESET-NOTIFICATION-DOMAIN"
SCHEMA: Final[str] = "WILSY-PASSWORD-RESET-NOTIFICATION/V1"
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(r"^[^\s\x00-\x1f\x7f]{1,256}$")
_MAX_ATTEMPTS: Final[int] = (1 << 31) - 1


class PasswordResetNotificationError(ValueError):
    """Stable failure for malformed or contradictory notification state.

    The deterministic code contains no password, reset token, address, tenant
    lookup result, principal lookup result, transport detail, or secret.
    Raising this error grants no password-reset, recovery, delivery, session,
    JWT, tenant, role, or financial authority.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class PasswordResetNotificationEvent(StrEnum):
    """Supported security-notification event vocabulary."""

    PASSWORD_RESET_COMPLETED = "PASSWORD_RESET_COMPLETED"


class PasswordResetNotificationChannel(StrEnum):
    """Supported notification delivery channels.

    EMAIL is the only admitted channel until another channel has separately
    certified recipient authority and delivery semantics.
    """

    EMAIL = "EMAIL"


class PasswordResetNotificationStatus(StrEnum):
    """Retryable delivery lifecycle for one durable notification intent."""

    PENDING = "PENDING"
    SENT = "SENT"


def _identifier(value: object, code: str) -> str:
    """Require one exact durable identifier without trimming or aliasing."""

    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise PasswordResetNotificationError(code)
    return value


def _utc(value: object, code: str) -> datetime:
    """Require an aware timestamp and normalize it to UTC."""

    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise PasswordResetNotificationError(code)
    try:
        return value.astimezone(timezone.utc)
    except (OverflowError, ValueError) as error:
        raise PasswordResetNotificationError(code) from error


def _optional_utc(value: object, code: str) -> datetime | None:
    """Validate one optional timestamp without consulting the wall clock."""

    if value is None:
        return None
    return _utc(value, code)


def _parse_timestamp(value: object, code: str) -> datetime:
    """Parse one persisted ISO timestamp and validate awareness later."""

    if not isinstance(value, str):
        raise PasswordResetNotificationError(code)
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise PasswordResetNotificationError(code) from error


def _attempt_count(value: object) -> int:
    """Require a bounded non-negative integer delivery-attempt count."""

    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= _MAX_ATTEMPTS:
        raise PasswordResetNotificationError("ATTEMPT_COUNT_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class PasswordResetNotification:
    """Immutable durable intent for one post-reset security notification.

    issue creates PENDING state with zero attempts. record_failure keeps the
    notification PENDING and records one retryable attempt without storing
    transport error detail. mark_sent transitions exactly once to SENT.
    Callers own persistence, retry scheduling, address resolution, delivery,
    transaction boundaries, and wall-clock selection.
    """

    notification_id: str
    tenant_id: str
    principal_id: str
    event: PasswordResetNotificationEvent
    channel: PasswordResetNotificationChannel
    occurred_at: datetime
    status: PasswordResetNotificationStatus
    attempt_count: int
    last_attempt_at: datetime | None = None
    delivered_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate complete immutable state and delivery invariants fail-closed."""

        notification_id = _identifier(self.notification_id, "NOTIFICATION_ID_INVALID")
        tenant_id = _identifier(self.tenant_id, "TENANT_ID_INVALID")
        principal_id = _identifier(self.principal_id, "PRINCIPAL_ID_INVALID")
        if not isinstance(self.event, PasswordResetNotificationEvent):
            raise PasswordResetNotificationError("EVENT_INVALID")
        if not isinstance(self.channel, PasswordResetNotificationChannel):
            raise PasswordResetNotificationError("CHANNEL_INVALID")
        if not isinstance(self.status, PasswordResetNotificationStatus):
            raise PasswordResetNotificationError("STATUS_INVALID")

        occurred_at = _utc(self.occurred_at, "OCCURRED_AT_INVALID")
        attempt_count = _attempt_count(self.attempt_count)
        last_attempt_at = _optional_utc(self.last_attempt_at, "LAST_ATTEMPT_AT_INVALID")
        delivered_at = _optional_utc(self.delivered_at, "DELIVERED_AT_INVALID")

        if attempt_count == 0 and last_attempt_at is not None:
            raise PasswordResetNotificationError("ATTEMPT_TIMESTAMP_MISMATCH")
        if attempt_count > 0 and last_attempt_at is None:
            raise PasswordResetNotificationError("ATTEMPT_TIMESTAMP_MISMATCH")
        if last_attempt_at is not None and last_attempt_at < occurred_at:
            raise PasswordResetNotificationError("LAST_ATTEMPT_BEFORE_OCCURRED")

        if self.status is PasswordResetNotificationStatus.PENDING:
            if delivered_at is not None:
                raise PasswordResetNotificationError("STATUS_TIMESTAMP_MISMATCH")
        else:
            if delivered_at is None or last_attempt_at is None or attempt_count < 1:
                raise PasswordResetNotificationError("STATUS_TIMESTAMP_MISMATCH")
            if delivered_at != last_attempt_at:
                raise PasswordResetNotificationError("DELIVERED_ATTEMPT_MISMATCH")
            if delivered_at < occurred_at:
                raise PasswordResetNotificationError("DELIVERED_BEFORE_OCCURRED")

        object.__setattr__(self, "notification_id", notification_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "principal_id", principal_id)
        object.__setattr__(self, "occurred_at", occurred_at)
        object.__setattr__(self, "attempt_count", attempt_count)
        object.__setattr__(self, "last_attempt_at", last_attempt_at)
        object.__setattr__(self, "delivered_at", delivered_at)

    @classmethod
    def issue(
        cls,
        *,
        notification_id: str,
        tenant_id: str,
        principal_id: str,
        occurred_at: datetime,
        channel: PasswordResetNotificationChannel = PasswordResetNotificationChannel.EMAIL,
    ) -> Self:
        """Create one PENDING password-reset notification intent.

        Creation owns no database write, email lookup, recipient verification,
        external delivery, password mutation, recovery capability, session,
        token, role, tenant resolution, or financial authority.
        """

        return cls(
            notification_id=notification_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            event=PasswordResetNotificationEvent.PASSWORD_RESET_COMPLETED,
            channel=channel,
            occurred_at=occurred_at,
            status=PasswordResetNotificationStatus.PENDING,
            attempt_count=0,
        )

    def record_failure(self, attempted_at: datetime) -> Self:
        """Record one failed external delivery attempt while remaining retryable."""

        if self.status is not PasswordResetNotificationStatus.PENDING:
            raise PasswordResetNotificationError("NOTIFICATION_ALREADY_SENT")
        observed = _utc(attempted_at, "ATTEMPTED_AT_INVALID")
        if observed < self.occurred_at:
            raise PasswordResetNotificationError("ATTEMPT_BEFORE_OCCURRED")
        if self.last_attempt_at is not None and observed < self.last_attempt_at:
            raise PasswordResetNotificationError("ATTEMPT_BEFORE_PRIOR_ATTEMPT")
        if self.attempt_count >= _MAX_ATTEMPTS:
            raise PasswordResetNotificationError("ATTEMPT_COUNT_EXHAUSTED")
        return replace(
            self,
            attempt_count=self.attempt_count + 1,
            last_attempt_at=observed,
        )

    def mark_sent(self, delivered_at: datetime) -> Self:
        """Return terminal SENT state for one successful external delivery."""

        if self.status is not PasswordResetNotificationStatus.PENDING:
            raise PasswordResetNotificationError("NOTIFICATION_ALREADY_SENT")
        observed = _utc(delivered_at, "DELIVERED_AT_INVALID")
        if observed < self.occurred_at:
            raise PasswordResetNotificationError("DELIVERED_BEFORE_OCCURRED")
        if self.last_attempt_at is not None and observed < self.last_attempt_at:
            raise PasswordResetNotificationError("DELIVERED_BEFORE_PRIOR_ATTEMPT")
        if self.attempt_count >= _MAX_ATTEMPTS:
            raise PasswordResetNotificationError("ATTEMPT_COUNT_EXHAUSTED")
        return replace(
            self,
            status=PasswordResetNotificationStatus.SENT,
            attempt_count=self.attempt_count + 1,
            last_attempt_at=observed,
            delivered_at=observed,
        )

    def to_document(self) -> dict[str, Any]:
        """Serialize stable primitive state without recipient or secret material."""

        return {
            "schema": SCHEMA,
            "notification_id": self.notification_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "event": self.event.value,
            "channel": self.channel.value,
            "occurred_at": self.occurred_at.isoformat(),
            "status": self.status.value,
            "attempt_count": self.attempt_count,
            "last_attempt_at": None if self.last_attempt_at is None else self.last_attempt_at.isoformat(),
            "delivered_at": None if self.delivered_at is None else self.delivered_at.isoformat(),
        }

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> Self:
        """Hydrate exact persisted state and reject unknown or secret fields."""

        required = {
            "schema",
            "notification_id",
            "tenant_id",
            "principal_id",
            "event",
            "channel",
            "occurred_at",
            "status",
            "attempt_count",
            "last_attempt_at",
            "delivered_at",
        }
        if not isinstance(payload, Mapping) or set(payload) != required:
            raise PasswordResetNotificationError("PERSISTED_NOTIFICATION_SHAPE_INVALID")
        if payload.get("schema") != SCHEMA:
            raise PasswordResetNotificationError("PERSISTED_NOTIFICATION_SCHEMA_INVALID")
        try:
            return cls(
                notification_id=payload["notification_id"],
                tenant_id=payload["tenant_id"],
                principal_id=payload["principal_id"],
                event=PasswordResetNotificationEvent(payload["event"]),
                channel=PasswordResetNotificationChannel(payload["channel"]),
                occurred_at=_parse_timestamp(payload["occurred_at"], "OCCURRED_AT_INVALID"),
                status=PasswordResetNotificationStatus(payload["status"]),
                attempt_count=payload["attempt_count"],
                last_attempt_at=(
                    None
                    if payload["last_attempt_at"] is None
                    else _parse_timestamp(payload["last_attempt_at"], "LAST_ATTEMPT_AT_INVALID")
                ),
                delivered_at=(
                    None
                    if payload["delivered_at"] is None
                    else _parse_timestamp(payload["delivered_at"], "DELIVERED_AT_INVALID")
                ),
            )
        except PasswordResetNotificationError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise PasswordResetNotificationError("PERSISTED_NOTIFICATION_INVALID") from error


__all__ = [
    "PasswordResetNotification",
    "PasswordResetNotificationChannel",
    "PasswordResetNotificationError",
    "PasswordResetNotificationEvent",
    "PasswordResetNotificationStatus",
    "SCHEMA",
    "VERSION",
]


# ARTIFACT: password_reset_notification.py
# VERSION: v1.0.0-R10G1-PASSWORD-RESET-NOTIFICATION-DOMAIN
# AUTHORITY BOUNDARY: immutable post-reset notification-intent lifecycle state only
# TENANT POSTURE: exact tenant/principal binding; no alias or cross-tenant fallback
# FAIL-CLOSED POSTURE: malformed, contradictory, replayed, and reversed-attempt state rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
