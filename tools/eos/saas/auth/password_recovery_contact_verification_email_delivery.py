"""SMTP delivery adapter for recovery-contact email verification.

TITLE: WILSY OS Recovery Contact Verification Email Delivery Adapter
VERSION: v1.0.0-R10E17-RECOVERY-CONTACT-VERIFICATION-EMAIL-DELIVERY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Delivers one already-authorized email-control verification link through
         configured encrypted SMTP without creating verification or recovery truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_contact_verification_email_delivery.py
COLLABORATION / OWNERSHIP: The verification-request service supplies one transient
                           verification message. R10E7 supplies shared recovery
                           SMTP configuration semantics only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E17-RECOVERY-CONTACT-VERIFICATION-EMAIL-DELIVERY introduces
           a verification-specific encrypted SMTP adapter with HTML escaping,
           no permissive credential defaults, and secret-free failures.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Recipient and verification URL exist only in transient
                            message memory and are never logged or persisted.
TENANT BOUNDARY: No tenant authority is accepted or inferred by this adapter.
AUTHORITY BOUNDARY: External email transport capability only; no email-control
                    verification, recovery contact, reset, password, session,
                    JWT, MFA, HTTP, or rate-limit authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Configuration, TLS, authentication, and delivery failures
                     raise stable code-only transport errors.
"""

from __future__ import annotations

import html
import smtplib
import ssl
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from typing import Final

from .password_recovery_email_delivery import PasswordRecoveryEmailConfiguration

VERSION: Final[str] = "v1.0.0-R10E17-RECOVERY-CONTACT-VERIFICATION-EMAIL-DELIVERY"


class RecoveryContactVerificationEmailDeliveryError(RuntimeError):
    """Stable secret-free failure for verification email transport."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class RecoveryContactVerificationDeliveryMessage:
    """Transient email-control verification delivery payload.

    The verification URL is secret-bearing. It must never be logged, persisted,
    returned to a browser API response, or reused after capability completion.
    """

    recipient_email: str
    verification_url: str
    expires_at: datetime


class RecoveryContactVerificationEmailDelivery:
    """Deliver recovery-contact verification messages through encrypted SMTP."""

    def __init__(self, configuration: PasswordRecoveryEmailConfiguration) -> None:
        """Bind validated recovery SMTP configuration without opening a socket."""

        if not isinstance(configuration, PasswordRecoveryEmailConfiguration):
            raise RecoveryContactVerificationEmailDeliveryError(
                "RECOVERY_CONTACT_EMAIL_CONFIGURATION_INVALID"
            )
        self._configuration = configuration

    @classmethod
    def from_environment(cls) -> "RecoveryContactVerificationEmailDelivery":
        """Build from the recovery-specific SMTP environment contract."""

        try:
            configuration = PasswordRecoveryEmailConfiguration.from_environment()
        except Exception as error:
            raise RecoveryContactVerificationEmailDeliveryError(
                "RECOVERY_CONTACT_EMAIL_CONFIGURATION_MISSING"
            ) from error
        return cls(configuration)

    @staticmethod
    def _message(
        delivery: RecoveryContactVerificationDeliveryMessage,
        sender: str,
    ) -> EmailMessage:
        """Construct one bounded multipart verification message."""

        if not isinstance(delivery, RecoveryContactVerificationDeliveryMessage):
            raise RecoveryContactVerificationEmailDeliveryError(
                "RECOVERY_CONTACT_EMAIL_MESSAGE_INVALID"
            )
        message = EmailMessage()
        message["Subject"] = "Verify your WILSY OS recovery email"
        message["From"] = sender
        message["To"] = delivery.recipient_email
        expiry = delivery.expires_at.strftime("%Y-%m-%d %H:%M UTC")
        message.set_content(
            "Verify this email as your WILSY OS password-recovery contact.\n\n"
            f"Open this single-use link before {expiry}:\n"
            f"{delivery.verification_url}\n\n"
            "If you did not initiate this verification, ignore this message. "
            "No recovery contact will be created without the single-use link."
        )
        safe_url = html.escape(delivery.verification_url, quote=True)
        safe_expiry = html.escape(expiry)
        message.add_alternative(
            "<!doctype html><html><body>"
            "<h2>Verify your WILSY OS recovery email</h2>"
            "<p>Confirm this address for password recovery.</p>"
            f'<p><a href="{safe_url}">Verify recovery email</a></p>'
            f"<p>This single-use link expires at {safe_expiry}.</p>"
            "<p>If you did not initiate this verification, ignore this message. "
            "No recovery contact will be created without the link.</p>"
            "</body></html>",
            subtype="html",
        )
        return message

    def deliver(self, message: RecoveryContactVerificationDeliveryMessage) -> None:
        """Deliver one verification message over mandatory encrypted SMTP."""

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
            raise RecoveryContactVerificationEmailDeliveryError(
                "RECOVERY_CONTACT_EMAIL_DELIVERY_FAILED"
            ) from error


__all__ = [
    "RecoveryContactVerificationDeliveryMessage",
    "RecoveryContactVerificationEmailDelivery",
    "RecoveryContactVerificationEmailDeliveryError",
    "VERSION",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_contact_verification_email_delivery.py
# VERSION: v1.0.0-R10E17-RECOVERY-CONTACT-VERIFICATION-EMAIL-DELIVERY
# AUTHORITY BOUNDARY: external encrypted email-control verification transport only
# TENANT POSTURE: no tenant authority; recipient selection is upstream authority
# FAIL-CLOSED POSTURE: configuration, TLS, authentication, or delivery failure rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
