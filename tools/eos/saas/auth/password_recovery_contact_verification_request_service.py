"""Authenticated recovery-contact verification request orchestration.

TITLE: WILSY OS Recovery Contact Verification Request Service
VERSION: v1.0.0-R10E20-RECOVERY-CONTACT-VERIFICATION-REQUEST
AUTHORITY: Wilsy OS Core Governance
EPITOME: Uses an authenticated ACCESS identity only to select exact tenant and
         principal, re-reads the current durable user email, and issues one
         digest-only single-use email-control verification capability.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_contact_verification_request_service.py
COLLABORATION / OWNERSHIP: Authentication proves current ACCESS principal state;
                           AuthRegistry re-proves durable tenant/principal/email;
                           R10E16 persists verification lifecycle; R10E19 exposes
                           existing contact authority; rate and mail adapters are
                           external capabilities only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E20-RECOVERY-CONTACT-VERIFICATION-REQUEST introduces
           durable-email sourcing, exact ACCESS tenant/principal binding,
           separate verification rate gating, already-verified short-circuit,
           high-entropy token generation, digest-only persistence, trusted
           fragment-link delivery, and revocation on delivery failure.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: The browser cannot nominate a recovery address.
                            Raw verification tokens are transient and never
                            persisted, logged, or returned.
TENANT BOUNDARY: Identity tenant/principal must exactly match durable user state.
AUTHORITY BOUNDARY: Verification-request issuance only; no verified-contact
                    creation, password reset, session, JWT, MFA, or HTTP authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Verification creation is one insert. External delivery is
                      outside Mongo transaction; delivery failure revokes the
                      newly created verification capability.
FAIL-CLOSED POSTURE: Identity mismatch, durable email absence, persistence,
                     rate-limit, or delivery failure rejects with stable codes.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Final, Protocol, runtime_checkable
from urllib.parse import urlencode, urlsplit, urlunsplit

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus

from .auth_registry import AuthRegistry
from .password_recovery_contact import VerifiedRecoveryContactChannel
from .password_recovery_contact_registry import (
    VerifiedRecoveryContactRegistry,
    VerifiedRecoveryContactRegistryError,
)
from .password_recovery_contact_verification import RecoveryContactVerification
from .password_recovery_contact_verification_email_delivery import (
    RecoveryContactVerificationDeliveryMessage,
)
from .password_recovery_contact_verification_registry import (
    RecoveryContactVerificationPersistenceError,
    RecoveryContactVerificationRegistry,
    RecoveryContactVerificationRegistryError,
)
from .password_recovery_request_service import (
    PasswordRecoveryRequestRateLimitedError,
    normalize_recovery_email,
    recovery_address_digest,
)

VERSION: Final[str] = "v1.0.0-R10E20-RECOVERY-CONTACT-VERIFICATION-REQUEST"
DEFAULT_VERIFICATION_TTL: Final[timedelta] = timedelta(minutes=30)
TOKEN_ENTROPY_BYTES: Final[int] = 48
VERIFICATION_PATH: Final[str] = "/verify-recovery-contact"


class RecoveryContactVerificationRequestError(RuntimeError):
    """Stable code-only failure for verification-request orchestration."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class RecoveryContactVerificationRequestResult:
    """Secret-free receipt for authenticated verification initiation."""

    status: str


@runtime_checkable
class RecoveryContactVerificationRateGate(Protocol):
    """Request-density capability required before verification issuance."""

    def require_allowed(
        self,
        *,
        tenant_id: str,
        address_digest: str,
        observed_at: datetime,
    ) -> None:
        """Require this authenticated verification request to remain in policy."""


@runtime_checkable
class RecoveryContactVerificationDeliveryAdapter(Protocol):
    """External transport boundary for one secret-bearing verification message."""

    def deliver(self, message: RecoveryContactVerificationDeliveryMessage) -> None:
        """Deliver one verification message or raise on failure."""


def _utc(value: object) -> datetime:
    """Require one explicit UTC observation timestamp."""

    if not isinstance(value, datetime):
        raise RecoveryContactVerificationRequestError(
            "RECOVERY_CONTACT_VERIFICATION_TIME_INVALID"
        )
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise RecoveryContactVerificationRequestError(
            "RECOVERY_CONTACT_VERIFICATION_TIME_INVALID"
        )
    return value


def _trusted_origin(value: object) -> str:
    """Validate one configured HTTPS application origin, never request Host."""

    if not isinstance(value, str) or value != value.strip():
        raise RecoveryContactVerificationRequestError(
            "RECOVERY_CONTACT_VERIFICATION_ORIGIN_INVALID"
        )
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise RecoveryContactVerificationRequestError(
            "RECOVERY_CONTACT_VERIFICATION_ORIGIN_INVALID"
        )
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def _verification_url(origin: str, *, tenant_id: str, raw_token: str) -> str:
    """Build one fragment-secret verification URL."""

    fragment = urlencode({"tenant": tenant_id, "verification": raw_token})
    return f"{origin}{VERIFICATION_PATH}#{fragment}"


class RecoveryContactVerificationRequestService:
    """Issue email-control verification from current durable principal email.

    The ACCESS identity contributes only tenant/principal selectors. Email in the
    identity projection is intentionally ignored because it is non-authoritative.
    AuthRegistry exact credential-revision lookup proves tenant/principal binding
    before the durable user email is read.
    """

    def __init__(
        self,
        *,
        verification_registry: RecoveryContactVerificationRegistry,
        contact_registry: VerifiedRecoveryContactRegistry,
        auth_registry: AuthRegistry,
        rate_limit_gate: RecoveryContactVerificationRateGate,
        delivery_adapter: RecoveryContactVerificationDeliveryAdapter,
        public_origin: str,
        verification_ttl: timedelta = DEFAULT_VERIFICATION_TTL,
    ) -> None:
        """Bind canonical authorities and external capabilities."""

        if not isinstance(verification_registry, RecoveryContactVerificationRegistry):
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_VERIFICATION_REGISTRY_INVALID"
            )
        if not isinstance(contact_registry, VerifiedRecoveryContactRegistry):
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_REGISTRY_INVALID"
            )
        if not isinstance(auth_registry, AuthRegistry):
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_AUTH_REGISTRY_INVALID"
            )
        if not isinstance(rate_limit_gate, RecoveryContactVerificationRateGate):
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_RATE_GATE_INVALID"
            )
        if not isinstance(delivery_adapter, RecoveryContactVerificationDeliveryAdapter):
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_DELIVERY_ADAPTER_INVALID"
            )
        if (
            not isinstance(verification_ttl, timedelta)
            or verification_ttl <= timedelta(0)
            or verification_ttl > timedelta(hours=24)
        ):
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_VERIFICATION_TTL_INVALID"
            )

        self._verification_registry = verification_registry
        self._contact_registry = contact_registry
        self._auth_registry = auth_registry
        self._rate_limit_gate = rate_limit_gate
        self._delivery_adapter = delivery_adapter
        self._public_origin = _trusted_origin(public_origin)
        self._verification_ttl = verification_ttl

    def request_verification(
        self,
        *,
        identity: SovereignIdentity,
        observed_at: datetime,
    ) -> RecoveryContactVerificationRequestResult:
        """Issue one verification link for the authenticated principal email.

        No email address is accepted from the browser. If the current durable
        email already matches ACTIVE recovery-contact authority, the method
        returns VERIFICATION_NOT_REQUIRED without issuing or delivering another
        capability.
        """

        if not isinstance(identity, SovereignIdentity):
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_IDENTITY_INVALID"
            )
        if identity.status is not PrincipalStatus.ACTIVE:
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_PRINCIPAL_NOT_ACTIVE"
            )
        observed = _utc(observed_at)

        try:
            self._auth_registry.get_credential_revision(
                identity.tenant_id,
                identity.identity_id,
            )
            user = self._auth_registry.get_user_by_id(identity.identity_id)
        except Exception as error:
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_PRINCIPAL_LOOKUP_FAILED"
            ) from error

        if (
            user is None
            or user.id != identity.identity_id
            or user.tenantId != identity.tenant_id
        ):
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_PRINCIPAL_BINDING_MISMATCH"
            )

        try:
            current_email = normalize_recovery_email(str(user.email))
        except Exception as error:
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_EMAIL_INVALID"
            ) from error
        address_digest = recovery_address_digest(current_email)

        try:
            existing = self._contact_registry.get_active_by_principal(
                tenant_id=identity.tenant_id,
                principal_id=identity.identity_id,
                channel=VerifiedRecoveryContactChannel.EMAIL,
            )
        except VerifiedRecoveryContactRegistryError as error:
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_LOOKUP_FAILED"
            ) from error

        if existing is not None and existing.address_digest == address_digest:
            return RecoveryContactVerificationRequestResult(
                status="VERIFICATION_NOT_REQUIRED"
            )

        try:
            self._rate_limit_gate.require_allowed(
                tenant_id=identity.tenant_id,
                address_digest=address_digest,
                observed_at=observed,
            )
        except PasswordRecoveryRequestRateLimitedError as error:
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_VERIFICATION_RATE_LIMITED"
            ) from error
        except Exception as error:
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_VERIFICATION_RATE_GATE_FAILED"
            ) from error

        raw_token = secrets.token_urlsafe(TOKEN_ENTROPY_BYTES)
        token_digest = hashlib.sha3_512(raw_token.encode("utf-8")).hexdigest()
        verification = RecoveryContactVerification.issue(
            verification_id=f"WILSYRECVERIFY-{uuid.uuid4()}",
            tenant_id=identity.tenant_id,
            principal_id=identity.identity_id,
            address_digest=address_digest,
            token_digest=token_digest,
            issued_at=observed,
            expires_at=observed + self._verification_ttl,
        )

        try:
            self._verification_registry.create(verification)
        except (
            RecoveryContactVerificationPersistenceError,
            RecoveryContactVerificationRegistryError,
        ) as error:
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_VERIFICATION_CREATE_FAILED"
            ) from error

        message = RecoveryContactVerificationDeliveryMessage(
            recipient_email=current_email,
            verification_url=_verification_url(
                self._public_origin,
                tenant_id=identity.tenant_id,
                raw_token=raw_token,
            ),
            expires_at=verification.expires_at,
        )
        try:
            self._delivery_adapter.deliver(message)
        except Exception as delivery_error:
            try:
                self._verification_registry.revoke(verification, observed)
            except Exception as revoke_error:
                raise RecoveryContactVerificationRequestError(
                    "RECOVERY_CONTACT_VERIFICATION_DELIVERY_FAILED_REVOCATION_UNCONFIRMED"
                ) from revoke_error
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_VERIFICATION_DELIVERY_FAILED"
            ) from delivery_error

        return RecoveryContactVerificationRequestResult(
            status="VERIFICATION_SENT"
        )


__all__ = [
    "DEFAULT_VERIFICATION_TTL",
    "RecoveryContactVerificationDeliveryAdapter",
    "RecoveryContactVerificationRateGate",
    "RecoveryContactVerificationRequestError",
    "RecoveryContactVerificationRequestResult",
    "RecoveryContactVerificationRequestService",
    "TOKEN_ENTROPY_BYTES",
    "VERIFICATION_PATH",
    "VERSION",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_contact_verification_request_service.py
# VERSION: v1.0.0-R10E20-RECOVERY-CONTACT-VERIFICATION-REQUEST
# AUTHORITY BOUNDARY: authenticated current-email verification issuance only
# TENANT POSTURE: exact ACCESS tenant/principal + durable user binding
# FAIL-CLOSED POSTURE: mismatch, rate, persistence, or delivery failure rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
