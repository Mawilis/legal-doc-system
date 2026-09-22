"""SMTP delivery adapter for WILSY OS password recovery.

TITLE: WILSY OS Password Recovery Email Delivery Adapter
VERSION: v1.0.0-R10E7-PASSWORD-RECOVERY-EMAIL-DELIVERY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Delivers one already-authorized recovery link through configured SMTP
         without generating tokens, verifying contacts, mutating credentials,
         persisting secrets, or becoming recovery authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_email_delivery.py
COLLABORATION / OWNERSHIP: R10E3 supplies one transient secret-bearing delivery
                           message. This adapter owns only mail transport to the
                           already-authorized recipient.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E7-PASSWORD-RECOVERY-EMAIL-DELIVERY introduces explicit
           recovery-specific SMTP configuration, mandatory TLS, no credential
           defaults, privacy-safe message construction, and secret-free errors.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Recipient and recovery URL exist only in transient
                            message memory; neither is logged or persisted.
TENANT BOUNDARY: This adapter receives no tenant authority and cannot alter
                 recipient selection supplied by the Python issuance service.
AUTHORITY BOUNDARY: External email transport capability only; no contact
                    verification, token issuance, reset, password, session,
                    JWT, MFA, HTTP, or rate-limit authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Missing configuration, TLS/authentication failure, or SMTP
                     rejection raises a stable delivery error.
"""

from __future__ import annotations

import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Final

from .password_recovery_request_service import PasswordRecoveryDeliveryMessage

VERSION: Final[str] = "v1.0.0-R10E7-PASSWORD-RECOVERY-EMAIL-DELIVERY"


class PasswordRecoveryEmailDeliveryError(RuntimeError):
    """Stable secret-free failure for recovery email transport."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class PasswordRecoveryEmailConfiguration:
    """Explicit SMTP transport configuration for recovery mail only."""

    host: str
    port: int
    username: str
    password: str
    sender: str
    use_ssl: bool = False

    def __post_init__(self) -> None:
        """Reject missing, malformed, or insecure transport configuration."""

        for value, code in (
            (self.host, "RECOVERY_EMAIL_HOST_INVALID"),
            (self.username, "RECOVERY_EMAIL_USERNAME_INVALID"),
            (self.password, "RECOVERY_EMAIL_PASSWORD_INVALID"),
            (self.sender, "RECOVERY_EMAIL_SENDER_INVALID"),
        ):
            if not isinstance(value, str) or not value.strip() or value != value.strip():
                raise PasswordRecoveryEmailDeliveryError(code)
        if isinstance(self.port, bool) or not isinstance(self.port, int) or not 1 <= self.port <= 65535:
            raise PasswordRecoveryEmailDeliveryError("RECOVERY_EMAIL_PORT_INVALID")
        if not isinstance(self.use_ssl, bool):
            raise PasswordRecoveryEmailDeliveryError("RECOVERY_EMAIL_SSL_INVALID")

    @classmethod
    def from_environment(cls) -> "PasswordRecoveryEmailConfiguration":
        """Load recovery-specific SMTP settings without permissive defaults."""

        try:
            port = int(os.environ["WILSY_RECOVERY_SMTP_PORT"])
        except (KeyError, ValueError) as error:
            raise PasswordRecoveryEmailDeliveryError(
                "RECOVERY_EMAIL_CONFIGURATION_MISSING"
            ) from error
        try:
            use_ssl_raw = os.environ["WILSY_RECOVERY_SMTP_SSL"].strip().lower()
            if use_ssl_raw not in {"true", "false"}:
                raise ValueError
            use_ssl = use_ssl_raw == "true"
            return cls(
                host=os.environ["WILSY_RECOVERY_SMTP_HOST"],
                port=port,
                username=os.environ["WILSY_RECOVERY_SMTP_USERNAME"],
                password=os.environ["WILSY_RECOVERY_SMTP_PASSWORD"],
                sender=os.environ["WILSY_RECOVERY_EMAIL_FROM"],
                use_ssl=use_ssl,
            )
        except (KeyError, ValueError) as error:
            raise PasswordRecoveryEmailDeliveryError(
                "RECOVERY_EMAIL_CONFIGURATION_MISSING"
            ) from error


class PasswordRecoveryEmailDelivery:
    """Deliver R10E3 recovery messages through mandatory encrypted SMTP."""

    def __init__(self, configuration: PasswordRecoveryEmailConfiguration) -> None:
        """Bind validated SMTP configuration without opening a connection."""

        if not isinstance(configuration, PasswordRecoveryEmailConfiguration):
            raise PasswordRecoveryEmailDeliveryError("RECOVERY_EMAIL_CONFIGURATION_INVALID")
        self._configuration = configuration

    @classmethod
    def from_environment(cls) -> "PasswordRecoveryEmailDelivery":
        """Construct the adapter from recovery-specific environment settings."""

        return cls(PasswordRecoveryEmailConfiguration.from_environment())

    @staticmethod
    def _message(delivery: PasswordRecoveryDeliveryMessage, sender: str) -> EmailMessage:
        """Construct one privacy-bounded multipart recovery message."""

        if not isinstance(delivery, PasswordRecoveryDeliveryMessage):
            raise PasswordRecoveryEmailDeliveryError("RECOVERY_EMAIL_MESSAGE_INVALID")
        message = EmailMessage()
        message["Subject"] = "Reset your WILSY OS password"
        message["From"] = sender
        message["To"] = delivery.recipient_email
        expiry = delivery.expires_at.strftime("%Y-%m-%d %H:%M UTC")
        text = (
            "A password reset was requested for your WILSY OS account.\n\n"
            f"Open this one-time recovery link before {expiry}:\n"
            f"{delivery.reset_url}\n\n"
            "If you did not request this reset, you can ignore this message. "
            "Your current password remains unchanged."
        )
        message.set_content(text)
        message.add_alternative(
            "<!doctype html><html><body>"
            "<h2>Reset your WILSY OS password</h2>"
            "<p>A password reset was requested for your WILSY OS account.</p>"
            f'<p><a href="{delivery.reset_url}">Reset password securely</a></p>'
            f"<p>This one-time recovery link expires at {expiry}.</p>"
            "<p>If you did not request this reset, ignore this message. "
            "Your current password remains unchanged.</p>"
            "</body></html>",
            subtype="html",
        )
        return message

    def deliver(self, message: PasswordRecoveryDeliveryMessage) -> None:
        """Deliver one authorized recovery message without logging secret data.

        Connection and authentication are established per delivery so no SMTP
        session or secret-bearing message is retained by the adapter.
        """

        email_message = self._message(message, self._configuration.sender)
        context = ssl.create_default_context()
        try:
            if self._configuration.use_ssl:
                with smtplib.SMTP_SSL(
                    self._configuration.host,
                    self._configuration.port,
                    context=context,
                    timeout=15,
                ) as client:
                    client.login(
                        self._configuration.username,
                        self._configuration.password,
                    )
                    client.send_message(email_message)
            else:
                with smtplib.SMTP(
                    self._configuration.host,
                    self._configuration.port,
                    timeout=15,
                ) as client:
                    client.ehlo()
                    client.starttls(context=context)
                    client.ehlo()
                    client.login(
                        self._configuration.username,
                        self._configuration.password,
                    )
                    client.send_message(email_message)
        except (OSError, smtplib.SMTPException) as error:
            raise PasswordRecoveryEmailDeliveryError(
                "RECOVERY_EMAIL_DELIVERY_FAILED"
            ) from error


__all__ = [
    "PasswordRecoveryEmailConfiguration",
    "PasswordRecoveryEmailDelivery",
    "PasswordRecoveryEmailDeliveryError",
    "VERSION",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_email_delivery.py
# VERSION: v1.0.0-R10E7-PASSWORD-RECOVERY-EMAIL-DELIVERY
# AUTHORITY BOUNDARY: external encrypted SMTP delivery capability only
# TENANT POSTURE: no tenant authority; recipient is pre-authorized upstream
# FAIL-CLOSED POSTURE: configuration, TLS, auth, and delivery failure rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
