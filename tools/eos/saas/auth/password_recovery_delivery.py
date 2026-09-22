"""Python EOS adapter for the internal Node password-recovery delivery bridge.

TITLE: WILSY OS Node Password Recovery Delivery Adapter
VERSION: v1.0.0-R10E7-NODE-RECOVERY-DELIVERY-ADAPTER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Authenticates one post-commit recovery-delivery instruction to the
         Node transport boundary without transferring recovery or credential authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_delivery.py
COLLABORATION / OWNERSHIP: PasswordRecoveryRequestService owns issuance;
                           Node owns SMTP capability; this adapter owns only
                           bounded HTTP transport and request authentication.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E7-NODE-RECOVERY-DELIVERY-ADAPTER — Establishes explicit-config
    Node delivery transport with SHA3-512 HMAC, 60-second-compatible timestamp
    signing, exact three-field JSON, bounded timeout, 204-only success, and
    code-only failure mapping. No endpoint or secret default is invented.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Recovery bearer/email values are transient call
                            arguments only and are never logged or retained.
TENANT BOUNDARY: No tenant field is sent to Node; Python retains exact recovery
                 tenant/principal authority before this adapter is invoked.
AUTHORITY BOUNDARY: Authenticated HTTP delivery transport only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
FAIL-CLOSED POSTURE: Missing config, malformed inputs, HTTP/network failure, or
                     any non-204 response is a code-only delivery failure.
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

VERSION: Final[str] = "v1.0.0-R10E7-NODE-RECOVERY-DELIVERY-ADAPTER"
INTERNAL_DELIVERY_PATH: Final[str] = "/internal/auth/password-recovery-delivery"
NODE_URL_ENV: Final[str] = "WILSY_NODE_INTERNAL_URL"
DELIVERY_SECRET_ENV: Final[str] = "WILSY_RECOVERY_DELIVERY_SECRET"
TIMESTAMP_HEADER: Final[str] = "X-Wilsy-Recovery-Timestamp"
SIGNATURE_HEADER: Final[str] = "X-Wilsy-Recovery-Signature"
DEFAULT_TIMEOUT_SECONDS: Final[float] = 10.0


class PasswordRecoveryDeliveryCode(StrEnum):
    """Stable adapter failure classes with no secret-bearing detail."""

    CONFIGURATION_INVALID = "PASSWORD_RECOVERY_DELIVERY_CONFIGURATION_INVALID"
    REQUEST_INVALID = "PASSWORD_RECOVERY_DELIVERY_REQUEST_INVALID"
    TRANSPORT_FAILED = "PASSWORD_RECOVERY_DELIVERY_TRANSPORT_FAILED"
    DELIVERY_UNCONFIRMED = "PASSWORD_RECOVERY_DELIVERY_UNCONFIRMED"


class PasswordRecoveryDeliveryError(RuntimeError):
    """Code-only delivery error without URL, email, token, or provider detail."""

    def __init__(self, code: PasswordRecoveryDeliveryCode) -> None:
        if not isinstance(code, PasswordRecoveryDeliveryCode):
            raise TypeError("password recovery delivery code is invalid")
        self.code = code
        super().__init__(code.value)

    def __str__(self) -> str:
        return self.code.value

    def __repr__(self) -> str:
        return f"PasswordRecoveryDeliveryError(code={self.code.value!r})"


def _configured_base_url(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PasswordRecoveryDeliveryError(PasswordRecoveryDeliveryCode.CONFIGURATION_INVALID)
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
        raise PasswordRecoveryDeliveryError(PasswordRecoveryDeliveryCode.CONFIGURATION_INVALID)
    return raw.rstrip("/")


def _configured_secret(value: object) -> bytes:
    if not isinstance(value, str) or len(value) < 32:
        raise PasswordRecoveryDeliveryError(PasswordRecoveryDeliveryCode.CONFIGURATION_INVALID)
    try:
        return value.encode("utf-8")
    except UnicodeEncodeError:
        raise PasswordRecoveryDeliveryError(
            PasswordRecoveryDeliveryCode.CONFIGURATION_INVALID
        ) from None


def _normalise_email(value: object) -> str:
    if not isinstance(value, str):
        raise PasswordRecoveryDeliveryError(PasswordRecoveryDeliveryCode.REQUEST_INVALID)
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
        raise PasswordRecoveryDeliveryError(PasswordRecoveryDeliveryCode.REQUEST_INVALID)
    return email


def _normalise_token(value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) < 32
        or len(value) > 4096
        or any(character.isspace() for character in value)
    ):
        raise PasswordRecoveryDeliveryError(PasswordRecoveryDeliveryCode.REQUEST_INVALID)
    return value


def _normalise_expiry(value: object) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise PasswordRecoveryDeliveryError(PasswordRecoveryDeliveryCode.REQUEST_INVALID)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _utc_timestamp_seconds(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise PasswordRecoveryDeliveryError(PasswordRecoveryDeliveryCode.CONFIGURATION_INVALID)
    return str(int(value.astimezone(timezone.utc).timestamp()))


def _signing_payload(timestamp: str, body: Mapping[str, str]) -> bytes:
    return "\n".join(
        (
            timestamp,
            body["recipient_email"],
            body["recovery_token"],
            body["expires_at"],
        )
    ).encode("utf-8")


class NodePasswordRecoveryDelivery:
    """Send one already-issued bearer to the authenticated Node transport seam.

    Configuration may be injected explicitly for tests/deployment composition.
    Otherwise the adapter requires WILSY_NODE_INTERNAL_URL and
    WILSY_RECOVERY_DELIVERY_SECRET at construction. No default host, port, or
    shared secret is invented. The object retains only transport configuration;
    recipient and recovery bearer values remain local to each delivery call.
    """

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
            shared_secret if shared_secret is not None else environment_map.get(DELIVERY_SECRET_ENV)
        )
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or timeout_seconds <= 0
            or timeout_seconds > 30
        ):
            raise PasswordRecoveryDeliveryError(
                PasswordRecoveryDeliveryCode.CONFIGURATION_INVALID
            )
        self._timeout_seconds = float(timeout_seconds)
        self._opener = opener or urllib_request.urlopen
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def deliver_password_recovery(
        self,
        *,
        recipient_email: str,
        recovery_token: str,
        expires_at: datetime,
    ) -> None:
        """Deliver one bearer through Node; exact HTTP 204 is the sole success."""

        recipient = _normalise_email(recipient_email)
        token = _normalise_token(recovery_token)
        expiry = _normalise_expiry(expires_at)
        timestamp = _utc_timestamp_seconds(self._clock)
        body = {
            "recipient_email": recipient,
            "recovery_token": token,
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
                raise PasswordRecoveryDeliveryError(
                    PasswordRecoveryDeliveryCode.DELIVERY_UNCONFIRMED
                )
        except PasswordRecoveryDeliveryError:
            raise
        except (urllib_error.HTTPError, urllib_error.URLError, OSError, TimeoutError):
            raise PasswordRecoveryDeliveryError(
                PasswordRecoveryDeliveryCode.TRANSPORT_FAILED
            ) from None
        except Exception:
            raise PasswordRecoveryDeliveryError(
                PasswordRecoveryDeliveryCode.TRANSPORT_FAILED
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
    "NodePasswordRecoveryDelivery",
    "PasswordRecoveryDeliveryCode",
    "PasswordRecoveryDeliveryError",
    "SIGNATURE_HEADER",
    "TIMESTAMP_HEADER",
    "VERSION",
]

# ARTIFACT: tools/eos/saas/auth/password_recovery_delivery.py
# VERSION: v1.0.0-R10E7-NODE-RECOVERY-DELIVERY-ADAPTER
# AUTHORITY BOUNDARY: HMAC-authenticated Python-to-Node recovery delivery transport only
# TENANT POSTURE: no tenant field crosses the delivery boundary
# FAIL-CLOSED POSTURE: invalid configuration/request/network/status returns code-only failure
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
