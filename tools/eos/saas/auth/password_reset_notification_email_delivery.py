"""SMTP adapter for WILSY OS post-reset security notifications.

TITLE: WILSY OS Password Reset Notification Email Adapter
VERSION: v1.0.0-R10G7-PASSWORD-RESET-NOTIFICATION-EMAIL-DELIVERY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Delivers one already-authorized, token-free password-reset security
         notification through the certified recovery SMTP configuration.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_reset_notification_email_delivery.py
COLLABORATION / OWNERSHIP: R10G5 supplies one transient verified-recipient
                           message; R10E7 PasswordRecoveryEmailConfiguration
                           supplies validated encrypted SMTP capability only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10G7-PASSWORD-RESET-NOTIFICATION-EMAIL-DELIVERY — Adds
           token-free password-change security copy, STARTTLS/implicit-TLS
           dispatch using the existing recovery SMTP configuration, and
           secret-free stable transport failures.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Recipient exists only in the transient message and
                            SMTP envelope. No password, reset/recovery token,
                            capability, digest, JWT, session, MFA material, or
                            login link is admitted into message content.
TENANT BOUNDARY: This external transport adapter owns no tenant resolution or
                 tenant authority; R10G5 already proved recipient binding.
AUTHORITY BOUNDARY: External encrypted email transport only; no password reset,
                    contact verification, recovery issuance, authentication,
                    persistence, retry scheduling, or HTTP authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
FAIL-CLOSED POSTURE: Invalid configuration/message, TLS/authentication failure,
                     and SMTP rejection raise stable code-only delivery errors.
"""

from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from typing import Final

from .password_recovery_email_delivery import PasswordRecoveryEmailConfiguration
from .password_reset_notification_dispatcher import (
    PasswordResetNotificationDeliveryMessage,
)

VERSION: Final[str] = "v1.0.0-R10G7-PASSWORD-RESET-NOTIFICATION-EMAIL-DELIVERY"


class PasswordResetNotificationEmailDeliveryError(RuntimeError):
    """Stable secret-free failure for post-reset email transport."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class PasswordResetNotificationEmailDelivery:
    """Deliver R10G5 token-free security notifications over encrypted SMTP."""

    def __init__(self, configuration: PasswordRecoveryEmailConfiguration) -> None:
        """Bind one already-validated recovery SMTP configuration."""

        if not isinstance(configuration, PasswordRecoveryEmailConfiguration):
            raise PasswordResetNotificationEmailDeliveryError(
                "PASSWORD_RESET_NOTIFICATION_EMAIL_CONFIGURATION_INVALID"
            )
        self._configuration = configuration

    @classmethod
    def from_environment(cls) -> "PasswordResetNotificationEmailDelivery":
        """Build from the certified WILSY recovery SMTP environment contract."""

        try:
            configuration = PasswordRecoveryEmailConfiguration.from_environment()
        except Exception as error:
            raise PasswordResetNotificationEmailDeliveryError(
                "PASSWORD_RESET_NOTIFICATION_EMAIL_CONFIGURATION_UNAVAILABLE"
            ) from error
        return cls(configuration)

    @staticmethod
    def _message(
        delivery: PasswordResetNotificationDeliveryMessage,
        sender: str,
    ) -> EmailMessage:
        """Construct one token-free security notification email."""

        if not isinstance(delivery, PasswordResetNotificationDeliveryMessage):
            raise PasswordResetNotificationEmailDeliveryError(
                "PASSWORD_RESET_NOTIFICATION_EMAIL_MESSAGE_INVALID"
            )
        if not isinstance(sender, str) or not sender.strip():
            raise PasswordResetNotificationEmailDeliveryError(
                "PASSWORD_RESET_NOTIFICATION_EMAIL_SENDER_INVALID"
            )

        occurred = delivery.occurred_at.strftime("%Y-%m-%d %H:%M UTC")
        message = EmailMessage()
        message["Subject"] = "Your WILSY OS password was changed"
        message["From"] = sender
        message["To"] = delivery.recipient_email

        text = (
            "Your WILSY OS password was changed successfully.\n\n"
            f"Time: {occurred}\n\n"
            "If you made this change, no further action is required.\n"
            "If you did not change your password, contact your institution's "
            "administrator or security team immediately.\n\n"
            "For your protection, this security notice contains no sign-in or "
            "password-reset link."
        )
        message.set_content(text)
        message.add_alternative(
            "<h2>Your WILSY OS password was changed</h2>"
            f"<p>Time: {occurred}</p>"
            "<p>If you made this change, no further action is required.</p>"
            "<p>If you did not change your password, contact your institution's "
            "administrator or security team immediately.</p>"
            "<p>For your protection, this security notice contains no sign-in "
            "or password-reset link.</p>",
            subtype="html",
        )
        return message

    def deliver(self, message: PasswordResetNotificationDeliveryMessage) -> None:
        """Deliver one authorized token-free security notification.

        Connection and authentication are established per call. No SMTP session,
        recipient, or message is retained by this adapter after return.
        """

        email_message = self._message(message, self._configuration.sender)
        context = ssl.create_default_context()
        try:
            if self._configuration.use_ssl:
                with smtplib.SMTP_SSL(
                    self._configuration.host,
                    self._configuration.port,
                    timeout=15,
                    context=context,
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
            raise PasswordResetNotificationEmailDeliveryError(
                "PASSWORD_RESET_NOTIFICATION_EMAIL_DELIVERY_FAILED"
            ) from error


__all__ = [
    "PasswordResetNotificationEmailDelivery",
    "PasswordResetNotificationEmailDeliveryError",
    "VERSION",
]


# ARTIFACT: password_reset_notification_email_delivery.py
# VERSION: v1.0.0-R10G7-PASSWORD-RESET-NOTIFICATION-EMAIL-DELIVERY
# AUTHORITY BOUNDARY: token-free encrypted SMTP transport capability only
# TENANT POSTURE: no tenant resolution or authority; recipient pre-authorized by R10G5
# FAIL-CLOSED POSTURE: invalid message/configuration, TLS/auth, and SMTP failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
