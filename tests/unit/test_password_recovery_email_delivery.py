"""Direct certificate for WILSY OS password-recovery email delivery.

TITLE: WILSY OS Password Recovery Email Delivery Direct Certificate
VERSION: v1.0.0-R10E28-PASSWORD-RECOVERY-EMAIL-DELIVERY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies strict recovery-specific SMTP configuration, encrypted
         transport, bounded message construction, and fail-closed secret-free
         delivery errors without granting recovery authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_email_delivery.py
COLLABORATION / OWNERSHIP: Exercises password_recovery_email_delivery.py with
                           monkeypatched SMTP capability only; no network.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E28-PASSWORD-RECOVERY-EMAIL-DELIVERY-CERT introduces direct
           evidence for environment validation, STARTTLS/SSL paths, login and
           message dispatch ordering, secret-bearing link placement, bounded
           copy, invalid-message rejection, and stable delivery failure.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic credentials and recovery URL only; no
                            network, logs, persistence, or production secrets.
TENANT BOUNDARY: Delivery adapter has no tenant authority.
AUTHORITY BOUNDARY: Direct transport evidence only; no contact verification,
                    capability issuance, reset, password, session, JWT, or MFA.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

import pytest

from tools.eos.saas.auth.password_recovery_email_delivery import (
    PasswordRecoveryEmailConfiguration,
    PasswordRecoveryEmailDelivery,
    PasswordRecoveryEmailDeliveryError,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    PasswordRecoveryDeliveryMessage,
)

RECIPIENT = "verified.user@example.com"
RESET_URL = "https://app.wilsy.example/reset-password#tenant=T1&recovery=secret-token"
EXPIRES = datetime(2026, 9, 22, 19, 30, tzinfo=timezone.utc)


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
            raise smtplib.SMTPException("synthetic send failure")


def _delivery_message() -> PasswordRecoveryDeliveryMessage:
    return PasswordRecoveryDeliveryMessage(
        recipient_email=RECIPIENT,
        reset_url=RESET_URL,
        expires_at=EXPIRES,
    )


def _configuration(*, use_ssl: bool = False) -> PasswordRecoveryEmailConfiguration:
    return PasswordRecoveryEmailConfiguration(
        host="smtp.wilsy.example",
        port=465 if use_ssl else 587,
        username="recovery-user",
        password="synthetic-password",
        sender="WILSY OS <recovery@wilsy.example>",
        use_ssl=use_ssl,
    )


@pytest.fixture(autouse=True)
def _reset_smtp_fake() -> None:
    _SMTPRecorder.instances.clear()
    _SMTPRecorder.fail_send = False


def test_configuration_rejects_missing_or_malformed_values() -> None:
    with pytest.raises(PasswordRecoveryEmailDeliveryError) as host_error:
        PasswordRecoveryEmailConfiguration(
            host="",
            port=587,
            username="u",
            password="p",
            sender="s@example.com",
        )
    assert host_error.value.code == "RECOVERY_EMAIL_HOST_INVALID"

    with pytest.raises(PasswordRecoveryEmailDeliveryError) as port_error:
        PasswordRecoveryEmailConfiguration(
            host="smtp.example.com",
            port=0,
            username="u",
            password="p",
            sender="s@example.com",
        )
    assert port_error.value.code == "RECOVERY_EMAIL_PORT_INVALID"

    with pytest.raises(PasswordRecoveryEmailDeliveryError) as ssl_error:
        PasswordRecoveryEmailConfiguration(
            host="smtp.example.com",
            port=587,
            username="u",
            password="p",
            sender="s@example.com",
            use_ssl="false",  # type: ignore[arg-type]
        )
    assert ssl_error.value.code == "RECOVERY_EMAIL_SSL_INVALID"


def test_environment_requires_recovery_specific_configuration(monkeypatch) -> None:
    for key in (
        "WILSY_RECOVERY_SMTP_HOST",
        "WILSY_RECOVERY_SMTP_PORT",
        "WILSY_RECOVERY_SMTP_USERNAME",
        "WILSY_RECOVERY_SMTP_PASSWORD",
        "WILSY_RECOVERY_EMAIL_FROM",
        "WILSY_RECOVERY_SMTP_SSL",
    ):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(PasswordRecoveryEmailDeliveryError) as captured:
        PasswordRecoveryEmailConfiguration.from_environment()
    assert captured.value.code == "RECOVERY_EMAIL_CONFIGURATION_MISSING"

    monkeypatch.setenv("WILSY_RECOVERY_SMTP_HOST", "smtp.wilsy.example")
    monkeypatch.setenv("WILSY_RECOVERY_SMTP_PORT", "587")
    monkeypatch.setenv("WILSY_RECOVERY_SMTP_USERNAME", "recovery-user")
    monkeypatch.setenv("WILSY_RECOVERY_SMTP_PASSWORD", "secret")
    monkeypatch.setenv("WILSY_RECOVERY_EMAIL_FROM", "recovery@wilsy.example")
    monkeypatch.setenv("WILSY_RECOVERY_SMTP_SSL", "false")

    config = PasswordRecoveryEmailConfiguration.from_environment()
    assert config == PasswordRecoveryEmailConfiguration(
        host="smtp.wilsy.example",
        port=587,
        username="recovery-user",
        password="secret",
        sender="recovery@wilsy.example",
        use_ssl=False,
    )


def test_message_contains_only_authorized_recipient_link_and_expiry() -> None:
    email = PasswordRecoveryEmailDelivery._message(
        _delivery_message(),
        "recovery@wilsy.example",
    )

    assert email["Subject"] == "Reset your WILSY OS password"
    assert email["From"] == "recovery@wilsy.example"
    assert email["To"] == RECIPIENT
    rendered = email.as_string()
    assert "Reset your WILSY OS password" in rendered
    assert RECIPIENT in rendered
    assert "2026-09-22 19:30 UTC" in rendered
    assert "secret-token" in rendered
    assert "ignore this message" in rendered.lower()


def test_starttls_path_encrypts_before_authentication_and_send(monkeypatch) -> None:
    monkeypatch.setattr(smtplib, "SMTP", _SMTPRecorder)
    delivery = PasswordRecoveryEmailDelivery(_configuration(use_ssl=False))

    delivery.deliver(_delivery_message())

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


def test_implicit_tls_path_uses_ssl_transport_and_authentication(monkeypatch) -> None:
    monkeypatch.setattr(smtplib, "SMTP_SSL", _SMTPRecorder)
    delivery = PasswordRecoveryEmailDelivery(_configuration(use_ssl=True))

    delivery.deliver(_delivery_message())

    assert len(_SMTPRecorder.instances) == 1
    client = _SMTPRecorder.instances[0]
    assert client.port == 465
    assert client.context is not None
    assert client.events == [
        "enter",
        ("login", "recovery-user", "synthetic-password"),
        "send_message",
        "exit",
    ]


def test_invalid_delivery_object_rejects_before_transport() -> None:
    with pytest.raises(PasswordRecoveryEmailDeliveryError) as captured:
        PasswordRecoveryEmailDelivery._message(object(), "recovery@wilsy.example")  # type: ignore[arg-type]
    assert captured.value.code == "RECOVERY_EMAIL_MESSAGE_INVALID"


def test_smtp_failure_is_stable_and_does_not_echo_secret(monkeypatch) -> None:
    monkeypatch.setattr(smtplib, "SMTP", _SMTPRecorder)
    _SMTPRecorder.fail_send = True
    delivery = PasswordRecoveryEmailDelivery(_configuration(use_ssl=False))

    with pytest.raises(PasswordRecoveryEmailDeliveryError) as captured:
        delivery.deliver(_delivery_message())

    assert captured.value.code == "RECOVERY_EMAIL_DELIVERY_FAILED"
    assert RESET_URL not in str(captured.value)
    assert "synthetic-password" not in str(captured.value)


def test_constructor_rejects_unvalidated_configuration() -> None:
    with pytest.raises(PasswordRecoveryEmailDeliveryError) as captured:
        PasswordRecoveryEmailDelivery(object())  # type: ignore[arg-type]
    assert captured.value.code == "RECOVERY_EMAIL_CONFIGURATION_INVALID"


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_email_delivery.py
# VERSION: v1.0.0-R10E28-PASSWORD-RECOVERY-EMAIL-DELIVERY-CERT
# AUTHORITY BOUNDARY: deterministic direct transport evidence only
# TENANT POSTURE: adapter remains tenant-authority-stateless
# FAIL-CLOSED POSTURE: invalid configuration/message and SMTP failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
