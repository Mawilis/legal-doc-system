"""Direct certificate for post-reset security email delivery.

TITLE: WILSY OS Password Reset Notification Email Delivery Certificate
VERSION: v1.0.1-R10G13-DECODED-MESSAGE-CERTIFICATE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies token-free message construction, encrypted SMTP ordering,
         reuse of the certified recovery SMTP configuration, and secret-free
         transport failure for post-reset security notifications.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_reset_notification_email_delivery.py
COLLABORATION / OWNERSHIP: Exercises R10G7 with monkeypatched SMTP only; no
                           network, production credentials, or account data.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.1-R10G13-DECODED-MESSAGE-CERTIFICATE — Decodes MIME text/plain content before semantic
           copy assertions so quoted-printable transport wrapping cannot create
           a false certificate failure.
           v1.0.0-R10G8-PASSWORD-RESET-NOTIFICATION-EMAIL-CERT — Adds direct
           STARTTLS/SSL, token/link exclusion, message timestamp, configuration
           reuse, invalid-message, and stable transport-failure evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic email/SMTP credentials only.
TENANT BOUNDARY: Adapter remains tenant-authority-stateless.
AUTHORITY BOUNDARY: Deterministic external-transport evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

import pytest

from tools.eos.saas.auth.password_recovery_email_delivery import (
    PasswordRecoveryEmailConfiguration,
)
from tools.eos.saas.auth.password_reset_notification_dispatcher import (
    PasswordResetNotificationDeliveryMessage,
)
from tools.eos.saas.auth.password_reset_notification_email_delivery import (
    PasswordResetNotificationEmailDelivery,
    PasswordResetNotificationEmailDeliveryError,
)

RECIPIENT = "verified.user@example.test"
OCCURRED = datetime(2026, 9, 22, 21, 15, tzinfo=timezone.utc)


class _SMTPRecorder:
    """Context-managed SMTP fake recording encryption/auth/send ordering."""

    instances: list["_SMTPRecorder"] = []
    fail_send = False

    def __init__(self, host, port, *, timeout, context=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.context = context
        self.events: list[object] = []
        self.message: EmailMessage | None = None
        type(self).instances.append(self)

    def __enter__(self):
        self.events.append("enter")
        return self

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb
        self.events.append("exit")
        return False

    def ehlo(self):
        self.events.append("ehlo")

    def starttls(self, *, context):
        assert context is not None
        self.events.append("starttls")

    def login(self, username, password):
        self.events.append(("login", username, password))

    def send_message(self, message):
        self.events.append("send_message")
        self.message = message
        if type(self).fail_send:
            raise smtplib.SMTPException("synthetic failure")


def _configuration(*, use_ssl: bool = False) -> PasswordRecoveryEmailConfiguration:
    return PasswordRecoveryEmailConfiguration(
        host="smtp.wilsy.example",
        port=465 if use_ssl else 587,
        username="recovery-user",
        password="synthetic-password",
        sender="security@wilsy.example",
        use_ssl=use_ssl,
    )


def _message() -> PasswordResetNotificationDeliveryMessage:
    return PasswordResetNotificationDeliveryMessage(
        recipient_email=RECIPIENT,
        occurred_at=OCCURRED,
    )


@pytest.fixture(autouse=True)
def _reset_smtp_fake() -> None:
    _SMTPRecorder.instances.clear()
    _SMTPRecorder.fail_send = False


def test_security_message_is_token_free_link_free_and_timestamped() -> None:
    email = PasswordResetNotificationEmailDelivery._message(
        _message(),
        "security@wilsy.example",
    )

    assert email["Subject"] == "Your WILSY OS password was changed"
    assert email["From"] == "security@wilsy.example"
    assert email["To"] == RECIPIENT
    plain = email.get_body(preferencelist=("plain",))
    assert plain is not None
    rendered = plain.get_content()
    assert "2026-09-22 21:15 UTC" in rendered
    assert "administrator or security team" in rendered
    assert "http://" not in rendered
    assert "https://" not in rendered
    assert "recovery=" not in rendered
    assert "#tenant=" not in rendered
    assert "reset your password securely" not in rendered.lower()


def test_starttls_encrypts_before_authentication_and_send(monkeypatch) -> None:
    monkeypatch.setattr(smtplib, "SMTP", _SMTPRecorder)
    delivery = PasswordResetNotificationEmailDelivery(_configuration(use_ssl=False))

    delivery.deliver(_message())

    assert len(_SMTPRecorder.instances) == 1
    client = _SMTPRecorder.instances[0]
    assert client.host == "smtp.wilsy.example"
    assert client.port == 587
    assert client.timeout == 15
    assert client.events == [
        "enter",
        "ehlo",
        "starttls",
        "ehlo",
        ("login", "recovery-user", "synthetic-password"),
        "send_message",
        "exit",
    ]
    assert client.message is not None
    assert client.message["To"] == RECIPIENT


def test_implicit_tls_uses_ssl_transport(monkeypatch) -> None:
    monkeypatch.setattr(smtplib, "SMTP_SSL", _SMTPRecorder)
    delivery = PasswordResetNotificationEmailDelivery(_configuration(use_ssl=True))

    delivery.deliver(_message())

    client = _SMTPRecorder.instances[0]
    assert client.port == 465
    assert client.context is not None
    assert client.events == [
        "enter",
        ("login", "recovery-user", "synthetic-password"),
        "send_message",
        "exit",
    ]


def test_from_environment_reuses_recovery_smtp_contract(monkeypatch) -> None:
    monkeypatch.setenv("WILSY_RECOVERY_SMTP_HOST", "smtp.wilsy.example")
    monkeypatch.setenv("WILSY_RECOVERY_SMTP_PORT", "587")
    monkeypatch.setenv("WILSY_RECOVERY_SMTP_USERNAME", "recovery-user")
    monkeypatch.setenv("WILSY_RECOVERY_SMTP_PASSWORD", "synthetic-password")
    monkeypatch.setenv("WILSY_RECOVERY_EMAIL_FROM", "security@wilsy.example")
    monkeypatch.setenv("WILSY_RECOVERY_SMTP_SSL", "false")

    delivery = PasswordResetNotificationEmailDelivery.from_environment()
    assert isinstance(delivery, PasswordResetNotificationEmailDelivery)


def test_invalid_message_and_configuration_fail_before_transport() -> None:
    with pytest.raises(PasswordResetNotificationEmailDeliveryError) as message_error:
        PasswordResetNotificationEmailDelivery._message(
            object(),  # type: ignore[arg-type]
            "security@wilsy.example",
        )
    assert message_error.value.code == "PASSWORD_RESET_NOTIFICATION_EMAIL_MESSAGE_INVALID"

    with pytest.raises(PasswordResetNotificationEmailDeliveryError) as config_error:
        PasswordResetNotificationEmailDelivery(object())  # type: ignore[arg-type]
    assert config_error.value.code == "PASSWORD_RESET_NOTIFICATION_EMAIL_CONFIGURATION_INVALID"


def test_smtp_failure_is_stable_and_secret_free(monkeypatch) -> None:
    monkeypatch.setattr(smtplib, "SMTP", _SMTPRecorder)
    _SMTPRecorder.fail_send = True
    delivery = PasswordResetNotificationEmailDelivery(_configuration(use_ssl=False))

    with pytest.raises(PasswordResetNotificationEmailDeliveryError) as captured:
        delivery.deliver(_message())

    assert captured.value.code == "PASSWORD_RESET_NOTIFICATION_EMAIL_DELIVERY_FAILED"
    rendered = str(captured.value)
    assert "synthetic-password" not in rendered
    assert RECIPIENT not in rendered


# ARTIFACT: test_password_reset_notification_email_delivery.py
# VERSION: v1.0.1-R10G13-DECODED-MESSAGE-CERTIFICATE
# AUTHORITY BOUNDARY: deterministic token-free SMTP evidence only
# TENANT POSTURE: external adapter remains tenant-authority-stateless
# FAIL-CLOSED POSTURE: invalid configuration/message and SMTP failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
