"""Direct certificate for WILSY OS post-reset notification dispatch.

TITLE: WILSY OS Password Reset Notification Dispatcher Direct Certificate
VERSION: v1.0.1-R10G12-DISPATCHER-EMAIL-FIXTURE-CLOSURE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies server-derived recipient authority, exact tenant/principal
         binding, stale-recipient rejection, token-free delivery, retry evidence,
         terminal SENT evidence, and idempotent already-SENT dispatch.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_reset_notification_dispatcher.py
COLLABORATION / OWNERSHIP: Exercises R10G5 with deterministic registry, auth,
                           and delivery fakes; performs no network or Mongo I/O.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.1-R10G12-DISPATCHER-EMAIL-FIXTURE-CLOSURE — Replaces reserved .test email fixtures with
           standards-valid example.com addresses so the certificate reaches
           dispatcher behavior under the canonical EmailStr validator.
           v1.0.0-R10G6-PASSWORD-RESET-NOTIFICATION-DISPATCHER-CERT — Adds direct
           evidence that callers cannot nominate recipients, only ACTIVE verified
           contact matching current durable principal email permits delivery,
           transport failure remains retryable, and success is durably terminal.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic addresses only; no reset tokens/passwords.
TENANT BOUNDARY: Exact synthetic tenant/principal bindings are asserted.
AUTHORITY BOUNDARY: Deterministic dispatcher evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import inspect
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.auth.password_recovery_contact import (
    VerifiedRecoveryContact,
    VerifiedRecoveryContactChannel,
)
from tools.eos.saas.auth.password_recovery_contact_registry import (
    VerifiedRecoveryContactRegistry,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    recovery_address_digest,
)
from tools.eos.saas.auth.password_reset_notification import (
    PasswordResetNotification,
    PasswordResetNotificationStatus,
)
from tools.eos.saas.auth.password_reset_notification_dispatcher import (
    PasswordResetNotificationDeliveryMessage,
    PasswordResetNotificationDispatchError,
    PasswordResetNotificationDispatcher,
)
from tools.eos.saas.auth.password_reset_notification_registry import (
    PasswordResetNotificationRegistry,
)
from tools.eos.saas.domain.auth import User


UTC = timezone.utc
TENANT = "WILSY-TENANT-R10G-DISPATCH"
PRINCIPAL = "WILSYAUTH-R10G-DISPATCH"
NOTICE_ID = "WILSYRESETNOTICE-R10G-DISPATCH"
CONTACT_ID = "WILSYCONTACT-R10G-DISPATCH"
EMAIL = "verified.user@example.com"
OCCURRED = datetime(2026, 9, 22, 21, 0, tzinfo=UTC)


class _Collection:
    """Small deterministic PyMongo-shaped collection for registry operations."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.fail_update = False

    @staticmethod
    def _matches(row: dict[str, object], query: dict[str, object]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def insert_one(self, document, **kwargs):
        del kwargs
        self.rows.append(deepcopy(document))
        return object()

    def find_one(self, query, **kwargs):
        del kwargs
        for row in self.rows:
            if self._matches(row, query):
                return deepcopy(row)
        return None

    def find_one_and_update(self, query, update, *, return_document=None, **kwargs):
        del return_document, kwargs
        if self.fail_update:
            raise RuntimeError("update disabled")
        for row in self.rows:
            if self._matches(row, query):
                row.update(deepcopy(update.get("$set", {})))
                return deepcopy(row)
        return None


class _AuthRegistry(AuthRegistry):
    """AuthRegistry-shaped current-principal projection for dispatcher tests."""

    def __init__(self, user: User | None) -> None:
        self.user = user
        self.raise_lookup = False

    def get_user_by_id(self, user_id: str, *, session=None):
        del session
        if self.raise_lookup:
            raise RuntimeError("lookup failed")
        if self.user is None or self.user.id != user_id:
            return None
        return self.user


class _Delivery:
    """Protocol-compatible token-free delivery fake."""

    def __init__(self) -> None:
        self.messages: list[PasswordResetNotificationDeliveryMessage] = []
        self.fail = False

    def deliver(self, message: PasswordResetNotificationDeliveryMessage) -> None:
        if self.fail:
            raise RuntimeError("transport failed")
        self.messages.append(message)


def _user(*, email: str = EMAIL, tenant_id: str = TENANT) -> User:
    return User(
        id=PRINCIPAL,
        email=email,
        firstName="Recovery",
        lastName="User",
        role="USER",
        permissions=[],
        tenantId=tenant_id,
        passwordHash="$2b$12$synthetic-not-used",
    )


def _notification() -> PasswordResetNotification:
    return PasswordResetNotification.issue(
        notification_id=NOTICE_ID,
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        occurred_at=OCCURRED,
    )


def _contact(*, digest: str | None = None, tenant_id: str = TENANT) -> VerifiedRecoveryContact:
    return VerifiedRecoveryContact.issue(
        contact_id=CONTACT_ID,
        tenant_id=tenant_id,
        principal_id=PRINCIPAL,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=digest or recovery_address_digest(EMAIL),
        verified_at=OCCURRED - timedelta(days=1),
    )


def _subject(
    *,
    user: User | None = None,
    contact: VerifiedRecoveryContact | None = None,
) -> tuple[
    PasswordResetNotificationDispatcher,
    PasswordResetNotificationRegistry,
    _Collection,
    _Delivery,
]:
    notification_collection = _Collection()
    notification_registry = PasswordResetNotificationRegistry(notification_collection)
    notification_registry.create(_notification())

    contact_collection = _Collection()
    if contact is not None:
        contact_collection.rows.append(contact.to_document())
    contact_registry = VerifiedRecoveryContactRegistry(contact_collection)

    delivery = _Delivery()
    dispatcher = PasswordResetNotificationDispatcher(
        notification_registry=notification_registry,
        contact_registry=contact_registry,
        auth_registry=_AuthRegistry(user if user is not None else _user()),
        delivery_adapter=delivery,
    )
    return dispatcher, notification_registry, notification_collection, delivery


def test_dispatch_signature_accepts_no_recipient_or_email_authority() -> None:
    parameters = inspect.signature(PasswordResetNotificationDispatcher.dispatch).parameters
    assert set(parameters) == {"self", "tenant_id", "notification_id", "observed_at"}
    assert "email" not in parameters
    assert "recipient" not in parameters


def test_success_reproves_verified_current_email_and_marks_sent() -> None:
    dispatcher, registry, _collection, delivery = _subject(contact=_contact())
    observed = OCCURRED + timedelta(minutes=2)

    result = dispatcher.dispatch(
        tenant_id=TENANT,
        notification_id=NOTICE_ID,
        observed_at=observed,
    )

    assert result.status == "PASSWORD_RESET_NOTIFICATION_SENT"
    assert len(delivery.messages) == 1
    message = delivery.messages[0]
    assert message.recipient_email == EMAIL
    assert message.occurred_at == OCCURRED
    assert set(message.__slots__) == {"recipient_email", "occurred_at"}

    persisted = registry.get(tenant_id=TENANT, notification_id=NOTICE_ID)
    assert persisted is not None
    assert persisted.status is PasswordResetNotificationStatus.SENT
    assert persisted.attempt_count == 1
    assert persisted.delivered_at == observed


def test_already_sent_is_idempotent_and_does_not_redeliver() -> None:
    dispatcher, registry, _collection, delivery = _subject(contact=_contact())
    observed = OCCURRED + timedelta(minutes=1)
    dispatcher.dispatch(
        tenant_id=TENANT,
        notification_id=NOTICE_ID,
        observed_at=observed,
    )
    assert len(delivery.messages) == 1

    result = dispatcher.dispatch(
        tenant_id=TENANT,
        notification_id=NOTICE_ID,
        observed_at=observed + timedelta(minutes=1),
    )
    assert result.status == "PASSWORD_RESET_NOTIFICATION_SENT"
    assert len(delivery.messages) == 1
    assert registry.get(tenant_id=TENANT, notification_id=NOTICE_ID).attempt_count == 1


@pytest.mark.parametrize(
    ("contact", "user", "code"),
    [
        (None, _user(), "PASSWORD_RESET_NOTIFICATION_RECIPIENT_UNAVAILABLE"),
        (
            _contact(digest=recovery_address_digest("other@example.com")),
            _user(),
            "PASSWORD_RESET_NOTIFICATION_RECIPIENT_STALE",
        ),
        (
            _contact(),
            _user(tenant_id="OTHER-TENANT"),
            "PASSWORD_RESET_NOTIFICATION_PRINCIPAL_UNAVAILABLE",
        ),
    ],
)
def test_missing_or_stale_recipient_authority_never_delivers(
    contact: VerifiedRecoveryContact | None,
    user: User,
    code: str,
) -> None:
    dispatcher, registry, _collection, delivery = _subject(user=user, contact=contact)

    with pytest.raises(PasswordResetNotificationDispatchError) as captured:
        dispatcher.dispatch(
            tenant_id=TENANT,
            notification_id=NOTICE_ID,
            observed_at=OCCURRED + timedelta(minutes=1),
        )

    assert captured.value.code == code
    assert delivery.messages == []
    persisted = registry.get(tenant_id=TENANT, notification_id=NOTICE_ID)
    assert persisted is not None
    assert persisted.status is PasswordResetNotificationStatus.PENDING
    assert persisted.attempt_count == 0


def test_cross_tenant_selector_cannot_resolve_notification() -> None:
    dispatcher, _registry, _collection, delivery = _subject(contact=_contact())

    with pytest.raises(PasswordResetNotificationDispatchError) as captured:
        dispatcher.dispatch(
            tenant_id="OTHER-TENANT",
            notification_id=NOTICE_ID,
            observed_at=OCCURRED + timedelta(minutes=1),
        )

    assert captured.value.code == "PASSWORD_RESET_NOTIFICATION_NOT_FOUND"
    assert delivery.messages == []


def test_transport_failure_records_retryable_attempt_and_returns_stable_error() -> None:
    dispatcher, registry, _collection, delivery = _subject(contact=_contact())
    delivery.fail = True
    observed = OCCURRED + timedelta(minutes=1)

    with pytest.raises(PasswordResetNotificationDispatchError) as captured:
        dispatcher.dispatch(
            tenant_id=TENANT,
            notification_id=NOTICE_ID,
            observed_at=observed,
        )

    assert captured.value.code == "PASSWORD_RESET_NOTIFICATION_DELIVERY_FAILED"
    persisted = registry.get(tenant_id=TENANT, notification_id=NOTICE_ID)
    assert persisted is not None
    assert persisted.status is PasswordResetNotificationStatus.PENDING
    assert persisted.attempt_count == 1
    assert persisted.last_attempt_at == observed
    assert persisted.delivered_at is None


def test_delivery_failure_without_evidence_confirmation_fails_closed() -> None:
    dispatcher, _registry, collection, delivery = _subject(contact=_contact())
    delivery.fail = True
    collection.fail_update = True

    with pytest.raises(PasswordResetNotificationDispatchError) as captured:
        dispatcher.dispatch(
            tenant_id=TENANT,
            notification_id=NOTICE_ID,
            observed_at=OCCURRED + timedelta(minutes=1),
        )

    assert (
        captured.value.code
        == "PASSWORD_RESET_NOTIFICATION_DELIVERY_FAILED_EVIDENCE_UNCONFIRMED"
    )


def test_invalid_selectors_and_naive_time_reject_before_delivery() -> None:
    dispatcher, _registry, _collection, delivery = _subject(contact=_contact())

    with pytest.raises(PasswordResetNotificationDispatchError) as tenant_error:
        dispatcher.dispatch(
            tenant_id=" bad",
            notification_id=NOTICE_ID,
            observed_at=OCCURRED,
        )
    assert tenant_error.value.code == "PASSWORD_RESET_NOTIFICATION_TENANT_INVALID"

    with pytest.raises(PasswordResetNotificationDispatchError) as id_error:
        dispatcher.dispatch(
            tenant_id=TENANT,
            notification_id="",
            observed_at=OCCURRED,
        )
    assert id_error.value.code == "PASSWORD_RESET_NOTIFICATION_ID_INVALID"

    with pytest.raises(PasswordResetNotificationDispatchError) as time_error:
        dispatcher.dispatch(
            tenant_id=TENANT,
            notification_id=NOTICE_ID,
            observed_at=datetime(2026, 9, 22, 21, 1),
        )
    assert time_error.value.code == "PASSWORD_RESET_NOTIFICATION_OBSERVED_AT_INVALID"
    assert delivery.messages == []


# ARTIFACT: test_password_reset_notification_dispatcher.py
# VERSION: v1.0.1-R10G12-DISPATCHER-EMAIL-FIXTURE-CLOSURE
# AUTHORITY BOUNDARY: deterministic verified-recipient dispatch evidence only
# TENANT POSTURE: exact tenant/contact/principal binding certified
# FAIL-CLOSED POSTURE: stale recipient, cross-tenant, transport, and evidence failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
