"""Python EOS adapter for Node recovery-contact verification delivery.

TITLE: WILSY OS Node Recovery Contact Verification Delivery Adapter
VERSION: v1.0.0-R10E18-NODE-RECOVERY-CONTACT-VERIFICATION-DELIVERY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Authenticates one already-issued email-possession challenge delivery to
         Node without transferring recovery-contact or credential authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/recovery_contact_verification_delivery.py
COLLABORATION / OWNERSHIP: RecoveryContactVerificationService owns challenge
                           issuance; Node owns SMTP capability; this adapter owns
                           only bounded HTTP transport and request authentication.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E18-NODE-RECOVERY-CONTACT-VERIFICATION-DELIVERY — Establishes
    explicit Node endpoint/dedicated-secret configuration, SHA3-512 HMAC,
    exact verification-delivery JSON, bounded timeout, 204-only success, and
    code-only failure mapping with no tenant/principal transfer.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Verification bearer/email are transient call values only.
TENANT BOUNDARY: No tenant/principal field crosses the Node delivery boundary.
AUTHORITY BOUNDARY: Authenticated HTTP transport only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
FAIL-CLOSED POSTURE: Missing config, malformed input, network failure, or any
                     non-204 response is a code-only delivery failure.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable, Final, Mapping
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import urlparse


VERSION: Final[str] = "v1.0.0-R10E18-NODE-RECOVERY-CONTACT-VERIFICATION-DELIVERY"
INTERNAL_DELIVERY_PATH: Final[str] = (
    "/internal/auth/recovery-contact-verification-delivery"
)
NODE_URL_ENV: Final[str] = "WILSY_NODE_INTERNAL_URL"
DELIVERY_SECRET_ENV: Final[str] = (
    "WILSY_RECOVERY_CONTACT_VERIFICATION_DELIVERY_SECRET"
)
TIMESTAMP_HEADER: Final[str] = "X-Wilsy-Recovery-Contact-Verification-Timestamp"
SIGNATURE_HEADER: Final[str] = "X-Wilsy-Recovery-Contact-Verification-Signature"
DEFAULT_TIMEOUT_SECONDS: Final[float] = 10.0


class RecoveryContactVerificationDeliveryCode(StrEnum):
    """Stable adapter failure classes with no secret-bearing detail."""

    CONFIGURATION_INVALID = "RECOVERY_CONTACT_VERIFICATION_DELIVERY_CONFIGURATION_INVALID"
    REQUEST_INVALID = "RECOVERY_CONTACT_VERIFICATION_DELIVERY_REQUEST_INVALID"
    TRANSPORT_FAILED = "RECOVERY_CONTACT_VERIFICATION_DELIVERY_TRANSPORT_FAILED"
    DELIVERY_UNCONFIRMED = "RECOVERY_CONTACT_VERIFICATION_DELIVERY_UNCONFIRMED"


class RecoveryContactVerificationDeliveryError(RuntimeError):
    """Code-only error without URL, email, token, or provider diagnostics."""

    def __init__(self, code: RecoveryContactVerificationDeliveryCode) -> None:
        if not isinstance(code, RecoveryContactVerificationDeliveryCode):
            raise TypeError("recovery contact verification delivery code is invalid")
        self.code = code
        super().__init__(code.value)

    def __repr__(self) -> str:
        return f"RecoveryContactVerificationDeliveryError(code={self.code.value!r})"


def _configured_base_url(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecoveryContactVerificationDeliveryError(
            RecoveryContactVerificationDeliveryCode.CONFIGURATION_INVALID
        )
    raw = value.strip()
    parsed = urlparse(raw)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise RecoveryContactVerificationDeliveryError(
            RecoveryContactVerificationDeliveryCode.CONFIGURATION_INVALID
        )
    return raw.rstrip("/")


def _configured_secret(value: object) -> bytes:
    if not isinstance(value, str) or len(value) < 32:
        raise RecoveryContactVerificationDeliveryError(
            RecoveryContactVerificationDeliveryCode.CONFIGURATION_INVALID
        )
    try:
        return value.encode("utf-8")
    except UnicodeEncodeError:
        raise RecoveryContactVerificationDeliveryError(
            RecoveryContactVerificationDeliveryCode.CONFIGURATION_INVALID
        ) from None


def _normalise_email(value: object) -> str:
    if not isinstance(value, str):
        raise RecoveryContactVerificationDeliveryError(
            RecoveryContactVerificationDeliveryCode.REQUEST_INVALID
        )
    email = value.strip().lower()
    parts = email.split("@")
    if (
        not email
        or len(email) > 320
        or len(parts) != 2
        or any(character.isspace() for character in email)
        or not parts[0]
        or not parts[1]
        or "." not in parts[1]
    ):
        raise RecoveryContactVerificationDeliveryError(
            RecoveryContactVerificationDeliveryCode.REQUEST_INVALID
        )
    return email


def _normalise_token(value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) < 32
        or len(value) > 4096
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise RecoveryContactVerificationDeliveryError(
            RecoveryContactVerificationDeliveryCode.REQUEST_INVALID
        )
    return value


def _normalise_expiry(value: object) -> str:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise RecoveryContactVerificationDeliveryError(
            RecoveryContactVerificationDeliveryCode.REQUEST_INVALID
        )
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _timestamp_seconds(clock: Callable[[], datetime]) -> str:
    value = clock()
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise RecoveryContactVerificationDeliveryError(
            RecoveryContactVerificationDeliveryCode.CONFIGURATION_INVALID
        )
    return str(int(value.astimezone(timezone.utc).timestamp()))


def _signing_payload(timestamp: str, body: Mapping[str, str]) -> bytes:
    return "\n".join(
        (
            timestamp,
            body["recipient_email"],
            body["verification_token"],
            body["expires_at"],
        )
    ).encode("utf-8")


class NodeRecoveryContactVerificationDelivery:
    """Send one already-issued possession challenge through the Node transport seam."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        shared_secret: str | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        opener: Callable[..., Any] | None = None,
        clock: Callable[[], datetime] | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        environment_map = os.environ if environment is None else environment
        self._base_url = _configured_base_url(
            base_url if base_url is not None else environment_map.get(NODE_URL_ENV)
        )
        self._shared_secret = _configured_secret(
            shared_secret
            if shared_secret is not None
            else environment_map.get(DELIVERY_SECRET_ENV)
        )
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or timeout_seconds <= 0
            or timeout_seconds > 30
        ):
            raise RecoveryContactVerificationDeliveryError(
                RecoveryContactVerificationDeliveryCode.CONFIGURATION_INVALID
            )
        self._timeout_seconds = float(timeout_seconds)
        self._opener = opener or urllib_request.urlopen
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def deliver_recovery_contact_verification(
        self,
        *,
        recipient_email: str,
        verification_token: str,
        expires_at: datetime,
    ) -> None:
        """Deliver one already-issued challenge; exact HTTP 204 is sole success."""

        recipient = _normalise_email(recipient_email)
        token = _normalise_token(verification_token)
        expiry = _normalise_expiry(expires_at)
        timestamp = _timestamp_seconds(self._clock)
        body = {
            "recipient_email": recipient,
            "verification_token": token,
            "expires_at": expiry,
        }
        signature = hmac.new(
            self._shared_secret,
            _signing_payload(timestamp, body),
            hashlib.sha3_512,
        ).hexdigest()
        payload = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
        request = urllib_request.Request(
            self._base_url + INTERNAL_DELIVERY_PATH,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                TIMESTAMP_HEADER: timestamp,
                SIGNATURE_HEADER: signature,
            },
        )

        response: Any | None = None
        try:
            response = self._opener(request, timeout=self._timeout_seconds)
            status = getattr(response, "status", None)
            if status is None:
                getter = getattr(response, "getcode", None)
                status = getter() if callable(getter) else None
            if status != 204:
                raise RecoveryContactVerificationDeliveryError(
                    RecoveryContactVerificationDeliveryCode.DELIVERY_UNCONFIRMED
                )
        except RecoveryContactVerificationDeliveryError:
            raise
        except (urllib_error.HTTPError, urllib_error.URLError, OSError, TimeoutError):
            raise RecoveryContactVerificationDeliveryError(
                RecoveryContactVerificationDeliveryCode.TRANSPORT_FAILED
            ) from None
        except Exception:
            raise RecoveryContactVerificationDeliveryError(
                RecoveryContactVerificationDeliveryCode.TRANSPORT_FAILED
            ) from None
        finally:
            closer = getattr(response, "close", None)
            if callable(closer):
                closer()


__all__ = [
    "DEFAULT_TIMEOUT_SECONDS",
    "DELIVERY_SECRET_ENV",
    "INTERNAL_DELIVERY_PATH",
    "NODE_URL_ENV",
    "NodeRecoveryContactVerificationDelivery",
    "RecoveryContactVerificationDeliveryCode",
    "RecoveryContactVerificationDeliveryError",
    "SIGNATURE_HEADER",
    "TIMESTAMP_HEADER",
    "VERSION",
]


# ARTIFACT: tools/eos/saas/auth/recovery_contact_verification_delivery.py
# VERSION: v1.0.0-R10E18-NODE-RECOVERY-CONTACT-VERIFICATION-DELIVERY
# AUTHORITY BOUNDARY: HMAC-authenticated Python-to-Node verification delivery transport only
# TENANT POSTURE: no tenant/principal field crosses the delivery boundary
# FAIL-CLOSED POSTURE: invalid configuration/request/network/status returns code-only failure
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
