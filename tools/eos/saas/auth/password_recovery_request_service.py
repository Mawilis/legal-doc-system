"""Password-recovery request issuance orchestration for WILSY OS.

TITLE: WILSY OS Password Recovery Request Service
VERSION: v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-ISSUANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Accepts one bounded recovery request, consumes pre-existing verified
         contact authority, generates one high-entropy recovery capability in
         Python, persists only its SHA3-512 digest, and delegates one transient
         recovery link to a delivery adapter.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_request_service.py
COLLABORATION / OWNERSHIP: R10E1/R10E2 prove verified-contact authority; R10B1/
                           R10B2 own recovery capability lifecycle; AuthRegistry
                           re-proves the current principal/email binding; an
                           injected rate gate and delivery adapter provide
                           capability only and never become recovery authority.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-ISSUANCE introduces generic
           anti-enumeration acceptance, deterministic email normalization and
           SHA3-512 contact lookup, mandatory rate gating, current-principal
           binding recheck, secrets-based token generation, digest-only durable
           issuance, trusted HTTPS origin validation, URL-fragment capability
           delivery, and fail-closed revocation when delivery fails.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; OWASP-style
            anti-enumeration and single-use recovery posture.
SECURITY / PRIVACY POSTURE: Raw recovery tokens exist only in transient local
                            variables and the delivery message; they are never
                            returned, logged, or persisted. Recovery links place
                            secret material in the URL fragment, not query/path.
TENANT BOUNDARY: Tenant scope is explicit on contact lookup, principal recheck,
                 capability persistence, and delivery message construction.
AUTHORITY BOUNDARY: This service owns issuance orchestration only. It does not
                    verify an email address, mutate passwords, consume reset
                    capabilities, issue auth tokens, create sessions, or own MFA.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: Capability creation is one durable insert. External mail
                      delivery is never placed inside a Mongo transaction. If
                      delivery fails after persistence, the created capability
                      is immediately revoked through the canonical registry.
FAIL-CLOSED POSTURE: Missing verified contact produces generic acceptance with
                     no issuance; dependency/integrity failures are stable
                     code-only errors and never expose account existence.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Final, Protocol, runtime_checkable
from urllib.parse import urlencode, urlsplit, urlunsplit

from .auth_registry import AuthRegistry
from .password_recovery import PasswordRecoveryCapability
from .password_recovery_contact import VerifiedRecoveryContactChannel
from .password_recovery_contact_registry import (
    VerifiedRecoveryContactPersistenceError,
    VerifiedRecoveryContactRegistry,
    VerifiedRecoveryContactRegistryError,
)
from .password_recovery_registry import (
    PasswordRecoveryCapabilityPersistenceError,
    PasswordRecoveryCapabilityRegistry,
    PasswordRecoveryCapabilityRegistryError,
)

VERSION: Final[str] = "v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-ISSUANCE"
DEFAULT_CAPABILITY_TTL: Final[timedelta] = timedelta(minutes=30)
TOKEN_ENTROPY_BYTES: Final[int] = 48
RESET_PATH: Final[str] = "/reset-password"


class PasswordRecoveryRequestServiceError(RuntimeError):
    """Stable code-only failure for recovery-request orchestration."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class PasswordRecoveryRequestRateLimitedError(PasswordRecoveryRequestServiceError):
    """The mandatory request-density gate rejected this recovery request."""


class PasswordRecoveryRequestDependencyError(PasswordRecoveryRequestServiceError):
    """A canonical persistence or delivery dependency failed closed."""


@dataclass(frozen=True, slots=True)
class PasswordRecoveryRequestResult:
    """Public-safe result for one accepted recovery request.

    The result intentionally contains no account-existence, principal, contact,
    capability, delivery, or timing truth.
    """

    accepted: bool = True


@dataclass(frozen=True, slots=True)
class PasswordRecoveryDeliveryMessage:
    """Transient delivery payload for an authorized recovery capability.

    The reset URL is secret-bearing. Adapters must not persist, log, serialize
    to telemetry, or return it to callers. The adapter gains transport
    capability only and never password-reset authority.
    """

    recipient_email: str
    reset_url: str
    expires_at: datetime


@runtime_checkable
class PasswordRecoveryRateLimitGate(Protocol):
    """Capability-only request density gate."""

    def require_allowed(
        self,
        *,
        tenant_id: str,
        address_digest: str,
        observed_at: datetime,
    ) -> None:
        """Require this request to remain inside configured recovery limits."""


@runtime_checkable
class PasswordRecoveryDeliveryAdapter(Protocol):
    """Capability-only delivery boundary for one transient recovery message."""

    def deliver(self, message: PasswordRecoveryDeliveryMessage) -> None:
        """Deliver one secret-bearing recovery message or raise on failure."""


def _utc(value: object) -> datetime:
    """Require one explicit timezone-aware UTC observation timestamp."""

    if not isinstance(value, datetime):
        raise PasswordRecoveryRequestServiceError("RECOVERY_REQUEST_TIME_INVALID")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise PasswordRecoveryRequestServiceError("RECOVERY_REQUEST_TIME_INVALID")
    return value


def _tenant_id(value: object) -> str:
    """Validate one exact caller-selected canonical tenant identifier."""

    if not isinstance(value, str):
        raise PasswordRecoveryRequestServiceError("RECOVERY_REQUEST_INVALID")
    normalized = value.strip()
    if not normalized or normalized != value or len(normalized) > 256:
        raise PasswordRecoveryRequestServiceError("RECOVERY_REQUEST_INVALID")
    return normalized


def normalize_recovery_email(value: object) -> str:
    """Normalize one email lookup value for digest comparison only.

    This is not email-address verification. It performs bounded whitespace and
    lowercase normalization and rejects malformed or control-bearing input.
    """

    if not isinstance(value, str):
        raise PasswordRecoveryRequestServiceError("RECOVERY_REQUEST_INVALID")
    normalized = value.strip().lower()
    if (
        not normalized
        or len(normalized) > 320
        or normalized.count("@") != 1
        or normalized.startswith("@")
        or normalized.endswith("@")
        or any(ord(character) < 32 or ord(character) == 127 for character in normalized)
    ):
        raise PasswordRecoveryRequestServiceError("RECOVERY_REQUEST_INVALID")
    local, domain = normalized.rsplit("@", 1)
    if not local or not domain or "." not in domain:
        raise PasswordRecoveryRequestServiceError("RECOVERY_REQUEST_INVALID")
    return normalized


def recovery_address_digest(normalized_email: str) -> str:
    """Return lowercase SHA3-512 digest for one normalized recovery address."""

    if not isinstance(normalized_email, str):
        raise PasswordRecoveryRequestServiceError("RECOVERY_REQUEST_INVALID")
    return hashlib.sha3_512(normalized_email.encode("utf-8")).hexdigest()


def _token_digest(raw_token: str) -> str:
    """Return the canonical R10B1 SHA3-512 digest for one raw token."""

    return hashlib.sha3_512(raw_token.encode("utf-8")).hexdigest()


def _trusted_reset_origin(value: object) -> str:
    """Validate one configured HTTPS public origin independent of request Host."""

    if not isinstance(value, str) or value != value.strip():
        raise PasswordRecoveryRequestServiceError("RECOVERY_PUBLIC_ORIGIN_INVALID")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise PasswordRecoveryRequestServiceError("RECOVERY_PUBLIC_ORIGIN_INVALID")
    path = parsed.path.rstrip("/")
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def _reset_url(origin: str, *, tenant_id: str, raw_token: str) -> str:
    """Build one fragment-secret reset URL from a trusted configured origin."""

    fragment = urlencode({"tenant": tenant_id, "recovery": raw_token})
    return f"{origin}{RESET_PATH}#{fragment}"


class PasswordRecoveryRequestService:
    """Issue recovery capabilities from verified contact authority.

    Account existence is never returned. Token generation occurs after
    syntactic validation and before contact existence is known so absent-contact
    requests do not take a cryptographic shortcut. Only ACTIVE verified-contact
    authority that still matches the principal current durable email may cause
    capability persistence and delivery.

    The rate gate is mandatory for both existent and absent contacts. Delivery
    is outside Mongo transactions; a delivery failure triggers immediate
    fail-closed capability revocation.
    """

    def __init__(
        self,
        *,
        contact_registry: VerifiedRecoveryContactRegistry,
        capability_registry: PasswordRecoveryCapabilityRegistry,
        auth_registry: AuthRegistry,
        rate_limit_gate: PasswordRecoveryRateLimitGate,
        delivery_adapter: PasswordRecoveryDeliveryAdapter,
        public_reset_origin: str,
        capability_ttl: timedelta = DEFAULT_CAPABILITY_TTL,
    ) -> None:
        """Bind canonical authorities and external capabilities."""

        if not isinstance(contact_registry, VerifiedRecoveryContactRegistry):
            raise PasswordRecoveryRequestServiceError("RECOVERY_CONTACT_REGISTRY_INVALID")
        if not isinstance(capability_registry, PasswordRecoveryCapabilityRegistry):
            raise PasswordRecoveryRequestServiceError("RECOVERY_CAPABILITY_REGISTRY_INVALID")
        if not isinstance(auth_registry, AuthRegistry):
            raise PasswordRecoveryRequestServiceError("RECOVERY_AUTH_REGISTRY_INVALID")
        if not isinstance(rate_limit_gate, PasswordRecoveryRateLimitGate):
            raise PasswordRecoveryRequestServiceError("RECOVERY_RATE_GATE_INVALID")
        if not isinstance(delivery_adapter, PasswordRecoveryDeliveryAdapter):
            raise PasswordRecoveryRequestServiceError("RECOVERY_DELIVERY_ADAPTER_INVALID")
        if (
            not isinstance(capability_ttl, timedelta)
            or capability_ttl <= timedelta(0)
            or capability_ttl > timedelta(hours=24)
        ):
            raise PasswordRecoveryRequestServiceError("RECOVERY_TTL_INVALID")

        self._contact_registry = contact_registry
        self._capability_registry = capability_registry
        self._auth_registry = auth_registry
        self._rate_limit_gate = rate_limit_gate
        self._delivery_adapter = delivery_adapter
        self._public_reset_origin = _trusted_reset_origin(public_reset_origin)
        self._capability_ttl = capability_ttl

    def request_password_reset(
        self,
        *,
        tenant_id: str,
        email: str,
        observed_at: datetime,
    ) -> PasswordRecoveryRequestResult:
        """Accept one password-recovery request without account enumeration.

        Missing/stale contact authority returns generic acceptance with no
        issuance. Dependency failures are code-only internal errors. This method
        owns no authentication session, password mutation, or Mongo transaction.
        """

        tenant = _tenant_id(tenant_id)
        normalized_email = normalize_recovery_email(email)
        observed = _utc(observed_at)
        address_digest = recovery_address_digest(normalized_email)

        try:
            self._rate_limit_gate.require_allowed(
                tenant_id=tenant,
                address_digest=address_digest,
                observed_at=observed,
            )
        except PasswordRecoveryRequestRateLimitedError:
            raise
        except Exception as error:
            raise PasswordRecoveryRequestDependencyError(
                "RECOVERY_RATE_GATE_FAILED"
            ) from error

        raw_token = secrets.token_urlsafe(TOKEN_ENTROPY_BYTES)
        token_digest = _token_digest(raw_token)

        try:
            contact = self._contact_registry.get_active_by_address_digest(
                tenant_id=tenant,
                channel=VerifiedRecoveryContactChannel.EMAIL,
                address_digest=address_digest,
            )
        except VerifiedRecoveryContactPersistenceError as error:
            raise PasswordRecoveryRequestDependencyError(
                "RECOVERY_CONTACT_LOOKUP_FAILED"
            ) from error
        except VerifiedRecoveryContactRegistryError as error:
            raise PasswordRecoveryRequestDependencyError(
                "RECOVERY_CONTACT_INTEGRITY_FAILED"
            ) from error

        if contact is None:
            return PasswordRecoveryRequestResult()

        try:
            user = self._auth_registry.get_user_by_id(contact.principal_id)
        except Exception as error:
            raise PasswordRecoveryRequestDependencyError(
                "RECOVERY_PRINCIPAL_LOOKUP_FAILED"
            ) from error

        if user is None or user.id != contact.principal_id or user.tenantId != tenant:
            return PasswordRecoveryRequestResult()

        try:
            current_email = normalize_recovery_email(str(user.email))
        except PasswordRecoveryRequestServiceError:
            return PasswordRecoveryRequestResult()
        if recovery_address_digest(current_email) != contact.address_digest:
            return PasswordRecoveryRequestResult()

        capability = PasswordRecoveryCapability.issue(
            capability_id=f"WILSYREC-{uuid.uuid4()}",
            tenant_id=tenant,
            principal_id=contact.principal_id,
            token_digest=token_digest,
            issued_at=observed,
            expires_at=observed + self._capability_ttl,
        )

        try:
            self._capability_registry.create(capability)
        except PasswordRecoveryCapabilityPersistenceError as error:
            raise PasswordRecoveryRequestDependencyError(
                "RECOVERY_CAPABILITY_CREATE_FAILED"
            ) from error
        except PasswordRecoveryCapabilityRegistryError as error:
            raise PasswordRecoveryRequestDependencyError(
                "RECOVERY_CAPABILITY_INTEGRITY_FAILED"
            ) from error

        message = PasswordRecoveryDeliveryMessage(
            recipient_email=current_email,
            reset_url=_reset_url(
                self._public_reset_origin,
                tenant_id=tenant,
                raw_token=raw_token,
            ),
            expires_at=capability.expires_at,
        )

        try:
            self._delivery_adapter.deliver(message)
        except Exception as delivery_error:
            try:
                self._capability_registry.revoke(capability, observed)
            except Exception as revoke_error:
                raise PasswordRecoveryRequestDependencyError(
                    "RECOVERY_DELIVERY_FAILED_REVOCATION_UNCONFIRMED"
                ) from revoke_error
            raise PasswordRecoveryRequestDependencyError(
                "RECOVERY_DELIVERY_FAILED"
            ) from delivery_error

        return PasswordRecoveryRequestResult()


__all__ = [
    "DEFAULT_CAPABILITY_TTL",
    "PasswordRecoveryDeliveryAdapter",
    "PasswordRecoveryDeliveryMessage",
    "PasswordRecoveryRateLimitGate",
    "PasswordRecoveryRequestDependencyError",
    "PasswordRecoveryRequestRateLimitedError",
    "PasswordRecoveryRequestResult",
    "PasswordRecoveryRequestService",
    "PasswordRecoveryRequestServiceError",
    "RESET_PATH",
    "TOKEN_ENTROPY_BYTES",
    "VERSION",
    "normalize_recovery_email",
    "recovery_address_digest",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_request_service.py
# VERSION: v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-ISSUANCE
# AUTHORITY BOUNDARY: verified-contact-gated recovery capability issuance only
# TENANT POSTURE: exact tenant/contact/principal/capability binding; no fallback
# FAIL-CLOSED POSTURE: dependency failure rejects; absence remains generic accepted
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
