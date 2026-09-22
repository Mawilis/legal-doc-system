"""Direct certificate for the WILSY OS post-reset notification domain.

TITLE: WILSY OS Password Reset Notification Domain Certificate
VERSION: v1.0.0-R10G2-PASSWORD-RESET-NOTIFICATION-DOMAIN-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves immutable issue/retry/send lifecycle, UTC normalization,
         strict persistence hydration, replay rejection, and secret exclusion.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_reset_notification.py
COLLABORATION / OWNERSHIP: Certifies password_reset_notification.py only; no
                           database, transport, reset transaction, or HTTP call.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10G2-PASSWORD-RESET-NOTIFICATION-DOMAIN-CERT — Adds direct
           deterministic coverage for R10G1 domain invariants and lifecycle.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identifiers/timestamps only; no secrets.
TENANT BOUNDARY: Synthetic exact tenant/principal identifiers only.
AUTHORITY BOUNDARY: Unit evidence only; grants no recovery/reset/delivery authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.auth.password_reset_notification import (
    SCHEMA,
    PasswordResetNotification,
    PasswordResetNotificationChannel,
    PasswordResetNotificationError,
    PasswordResetNotificationEvent,
    PasswordResetNotificationStatus,
)


UTC = timezone.utc
OCCURRED = datetime(2026, 9, 22, 20, 0, tzinfo=UTC)
TENANT = "WILSYTENANT-R10G"
PRINCIPAL = "WILSYAUTH-R10G"
NOTIFICATION = "WILSYRESETNOTICE-R10G"


def issue() -> PasswordResetNotification:
    """Return one valid synthetic PENDING notification."""

    return PasswordResetNotification.issue(
        notification_id=NOTIFICATION,
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        occurred_at=OCCURRED,
    )


def test_issue_creates_exact_secret_free_pending_state() -> None:
    notice = issue()

    assert notice.notification_id == NOTIFICATION
    assert notice.tenant_id == TENANT
    assert notice.principal_id == PRINCIPAL
    assert notice.event is PasswordResetNotificationEvent.PASSWORD_RESET_COMPLETED
    assert notice.channel is PasswordResetNotificationChannel.EMAIL
    assert notice.status is PasswordResetNotificationStatus.PENDING
    assert notice.attempt_count == 0
    assert notice.last_attempt_at is None
    assert notice.delivered_at is None

    document = notice.to_document()
    assert document["schema"] == SCHEMA
    assert set(document) == {
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
    forbidden = {"email", "address", "password", "token", "digest", "jwt", "session", "refresh"}
    assert forbidden.isdisjoint(document)


def test_issue_normalizes_aware_timestamp_to_utc() -> None:
    source = datetime(2026, 9, 22, 22, 0, tzinfo=timezone(timedelta(hours=2)))
    notice = PasswordResetNotification.issue(
        notification_id=NOTIFICATION,
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        occurred_at=source,
    )
    assert notice.occurred_at == OCCURRED
    assert notice.occurred_at.tzinfo is UTC


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("notification_id", "", "NOTIFICATION_ID_INVALID"),
        ("notification_id", " bad", "NOTIFICATION_ID_INVALID"),
        ("tenant_id", "TENANT WITH SPACE", "TENANT_ID_INVALID"),
        ("principal_id", "PRINCIPAL\nBAD", "PRINCIPAL_ID_INVALID"),
    ],
)
def test_invalid_identifiers_fail_closed(field: str, value: str, code: str) -> None:
    values = {
        "notification_id": NOTIFICATION,
        "tenant_id": TENANT,
        "principal_id": PRINCIPAL,
        "occurred_at": OCCURRED,
    }
    values[field] = value
    with pytest.raises(PasswordResetNotificationError) as exc:
        PasswordResetNotification.issue(**values)
    assert exc.value.code == code


def test_naive_occurred_at_is_rejected() -> None:
    with pytest.raises(PasswordResetNotificationError) as exc:
        PasswordResetNotification.issue(
            notification_id=NOTIFICATION,
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            occurred_at=datetime(2026, 9, 22, 20, 0),
        )
    assert exc.value.code == "OCCURRED_AT_INVALID"


def test_failure_attempt_is_retryable_and_monotonic() -> None:
    first_at = OCCURRED + timedelta(minutes=1)
    second_at = OCCURRED + timedelta(minutes=2)

    first = issue().record_failure(first_at)
    second = first.record_failure(second_at)

    assert first.status is PasswordResetNotificationStatus.PENDING
    assert first.attempt_count == 1
    assert first.last_attempt_at == first_at
    assert first.delivered_at is None

    assert second.status is PasswordResetNotificationStatus.PENDING
    assert second.attempt_count == 2
    assert second.last_attempt_at == second_at
    assert second.delivered_at is None

    with pytest.raises(PasswordResetNotificationError) as exc:
        second.record_failure(first_at)
    assert exc.value.code == "ATTEMPT_BEFORE_PRIOR_ATTEMPT"


def test_success_after_prior_failure_is_terminal_and_counts_attempt() -> None:
    failed_at = OCCURRED + timedelta(minutes=1)
    delivered_at = OCCURRED + timedelta(minutes=3)

    sent = issue().record_failure(failed_at).mark_sent(delivered_at)

    assert sent.status is PasswordResetNotificationStatus.SENT
    assert sent.attempt_count == 2
    assert sent.last_attempt_at == delivered_at
    assert sent.delivered_at == delivered_at

    with pytest.raises(PasswordResetNotificationError) as exc:
        sent.mark_sent(delivered_at + timedelta(minutes=1))
    assert exc.value.code == "NOTIFICATION_ALREADY_SENT"

    with pytest.raises(PasswordResetNotificationError) as exc:
        sent.record_failure(delivered_at + timedelta(minutes=1))
    assert exc.value.code == "NOTIFICATION_ALREADY_SENT"


def test_attempt_before_occurrence_is_rejected() -> None:
    with pytest.raises(PasswordResetNotificationError) as exc:
        issue().record_failure(OCCURRED - timedelta(microseconds=1))
    assert exc.value.code == "ATTEMPT_BEFORE_OCCURRED"

    with pytest.raises(PasswordResetNotificationError) as exc:
        issue().mark_sent(OCCURRED - timedelta(microseconds=1))
    assert exc.value.code == "DELIVERED_BEFORE_OCCURRED"


@pytest.mark.parametrize(
    "payload",
    [
        {
            "schema": SCHEMA,
            "notification_id": NOTIFICATION,
            "tenant_id": TENANT,
            "principal_id": PRINCIPAL,
            "event": PasswordResetNotificationEvent.PASSWORD_RESET_COMPLETED.value,
            "channel": PasswordResetNotificationChannel.EMAIL.value,
            "occurred_at": OCCURRED.isoformat(),
            "status": PasswordResetNotificationStatus.PENDING.value,
            "attempt_count": 1,
            "last_attempt_at": None,
            "delivered_at": None,
        },
        {
            "schema": SCHEMA,
            "notification_id": NOTIFICATION,
            "tenant_id": TENANT,
            "principal_id": PRINCIPAL,
            "event": PasswordResetNotificationEvent.PASSWORD_RESET_COMPLETED.value,
            "channel": PasswordResetNotificationChannel.EMAIL.value,
            "occurred_at": OCCURRED.isoformat(),
            "status": PasswordResetNotificationStatus.SENT.value,
            "attempt_count": 1,
            "last_attempt_at": (OCCURRED + timedelta(minutes=1)).isoformat(),
            "delivered_at": None,
        },
    ],
)
def test_contradictory_persisted_state_is_rejected(payload: dict[str, object]) -> None:
    with pytest.raises(PasswordResetNotificationError):
        PasswordResetNotification.from_document(payload)


def test_round_trip_preserves_exact_state() -> None:
    sent = issue().record_failure(OCCURRED + timedelta(minutes=1)).mark_sent(
        OCCURRED + timedelta(minutes=2)
    )
    assert PasswordResetNotification.from_document(sent.to_document()) == sent


def test_hydration_rejects_unknown_or_secret_fields() -> None:
    base = issue().to_document()

    for field, value in (
        ("email", "person@example.test"),
        ("recovery_token", "secret"),
        ("password", "secret"),
        ("token_digest", "0" * 128),
    ):
        payload = dict(base)
        payload[field] = value
        with pytest.raises(PasswordResetNotificationError) as exc:
            PasswordResetNotification.from_document(payload)
        assert exc.value.code == "PERSISTED_NOTIFICATION_SHAPE_INVALID"


def test_hydration_rejects_wrong_schema() -> None:
    payload = issue().to_document()
    payload["schema"] = "WRONG"
    with pytest.raises(PasswordResetNotificationError) as exc:
        PasswordResetNotification.from_document(payload)
    assert exc.value.code == "PERSISTED_NOTIFICATION_SCHEMA_INVALID"


# ARTIFACT: test_password_reset_notification.py
# VERSION: v1.0.0-R10G2-PASSWORD-RESET-NOTIFICATION-DOMAIN-CERT
# AUTHORITY BOUNDARY: deterministic unit evidence only
# TENANT POSTURE: synthetic exact tenant/principal identities only
# FAIL-CLOSED POSTURE: malformed, contradictory, secret-bearing, and replayed state rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
