"""WILSY OS password-recovery request and issuance orchestration.

TITLE: WILSY OS Password Recovery Request Service
VERSION: v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-ORCHESTRATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Admits one exact ACTIVE principal, supersedes earlier recovery windows,
         persists one digest-only capability transactionally, and delegates
         post-commit delivery without returning account-existence or token truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_request_service.py
COLLABORATION / OWNERSHIP: AuthRegistry resolves the exact tenant/email principal;
                           PrincipalAuthorityRepository owns current lifecycle truth;
                           PasswordRecoveryCapabilityRegistry owns capability persistence;
                           an injected delivery adapter owns transport capability only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-ORCHESTRATION — Establishes enumeration-safe request orchestration,
    30-minute single-use capability issuance, 60-second principal cooldown,
    transactional expiry/revocation of prior ACTIVE recovery windows, SHA3-512
    digest-only persistence, post-commit delivery, and compensating revocation
    when delivery fails.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw recovery tokens exist only transiently in the
                            request call stack and delivery invocation. They are
                            never persisted, logged, returned, or retained on
                            the service object.
TENANT BOUNDARY: Caller tenant_id is accepted only through AuthRegistry canonical
                 tenant resolution; all capability state is exact tenant/principal.
AUTHORITY BOUNDARY: This service owns recovery issuance orchestration only.
                    It grants no login, MFA, role, permission, membership, JWT,
                    session, refresh, password, or tenant authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
TRANSACTION BOUNDARY: This service owns Mongo ClientSession/with_transaction for
                      issuance reconciliation and delivery-failure compensation.
FAIL-CLOSED POSTURE: Ambiguity, corruption, transaction failure, unavailable
                     authority, and delivery failure never return a recovery secret.
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any, Callable, Final, Protocol

from tools.eos.auth.audit import log_auth_event
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import AuthRegistry, AuthRegistryTenantError

from .password_recovery import PasswordRecoveryCapability, PasswordRecoveryCapabilityStatus
from .password_recovery_registry import (
    PasswordRecoveryCapabilityLifecycleConflictError,
    PasswordRecoveryCapabilityPersistedRecordInvalidError,
    PasswordRecoveryCapabilityPersistenceError,
    PasswordRecoveryCapabilityRegistry,
    PasswordRecoveryCapabilityRegistryError,
)

VERSION: Final[str] = "v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-ORCHESTRATION"
RECOVERY_TTL: Final[timedelta] = timedelta(minutes=30)
RECOVERY_COOLDOWN: Final[timedelta] = timedelta(seconds=60)
RECOVERY_TOKEN_BYTES: Final[int] = 32
RECOVERY_CAPABILITY_PREFIX: Final[str] = "WILSYREC-"


class PasswordRecoveryRequestCode(StrEnum):
    """Stable non-secret failure classes for operational callers."""

    INVALID_REQUEST = "PASSWORD_RECOVERY_REQUEST_INVALID"
    AUTHORITY_UNAVAILABLE = "PASSWORD_RECOVERY_AUTHORITY_UNAVAILABLE"
    PERSISTENCE_FAILURE = "PASSWORD_RECOVERY_PERSISTENCE_FAILURE"
    TRANSACTION_FAILURE = "PASSWORD_RECOVERY_TRANSACTION_FAILURE"
    DELIVERY_FAILURE = "PASSWORD_RECOVERY_DELIVERY_FAILURE"


class PasswordRecoveryRequestServiceError(RuntimeError):
    """Code-only failure that never retains email, principal, token, or digest."""

    def __init__(self, code: PasswordRecoveryRequestCode) -> None:
        if not isinstance(code, PasswordRecoveryRequestCode):
            raise TypeError("password recovery request code is invalid")
        self.code = code
        super().__init__(code.value)

    def __str__(self) -> str:
        return self.code.value

    def __repr__(self) -> str:
        return f"PasswordRecoveryRequestServiceError(code={self.code.value!r})"


@dataclass(frozen=True, slots=True)
class PasswordRecoveryRequestResult:
    """Enumeration-safe receipt; it intentionally reveals no issuance outcome."""

    status: str = "PASSWORD_RECOVERY_REQUEST_ACCEPTED"


class _AuthRecoveryLookup(Protocol):
    def resolve_principal_id_by_email_for_tenant(
        self, tenant_id: str, email: str, *, session: Any = None
    ) -> str | None: ...


class _RecoveryRegistry(Protocol):
    def list_active_for_principal(
        self, *, tenant_id: str, principal_id: str, session: Any | None = None
    ) -> tuple[PasswordRecoveryCapability, ...]: ...

    def create(
        self, capability: PasswordRecoveryCapability, *, session: Any | None = None
    ) -> PasswordRecoveryCapability: ...

    def get_by_capability_id(
        self, *, tenant_id: str, capability_id: str, session: Any | None = None
    ) -> PasswordRecoveryCapability | None: ...

    def revoke(
        self, capability: PasswordRecoveryCapability, revoked_at: datetime, *, session: Any | None = None
    ) -> PasswordRecoveryCapability: ...

    def expire(
        self, capability: PasswordRecoveryCapability, expired_at: datetime, *, session: Any | None = None
    ) -> PasswordRecoveryCapability: ...


class _PrincipalAuthority(Protocol):
    @staticmethod
    def get(principal_id: str, *, session: Any | None = None) -> Any: ...


class PasswordRecoveryDelivery(Protocol):
    """Transport-only port. Implementations receive no password or auth authority."""

    def deliver_password_recovery(
        self, *, recipient_email: str, recovery_token: str, expires_at: datetime
    ) -> None: ...


class _MongoClient(Protocol):
    def start_session(self) -> Any: ...


def _normalise_email(value: object) -> str:
    """Normalize only the existing login-email representation, fail-closed."""

    if not isinstance(value, str):
        raise PasswordRecoveryRequestServiceError(PasswordRecoveryRequestCode.INVALID_REQUEST)
    email = value.strip().lower()
    if (
        not email
        or len(email) > 320
        or email.count("@") != 1
        or any(character.isspace() for character in email)
    ):
        raise PasswordRecoveryRequestServiceError(PasswordRecoveryRequestCode.INVALID_REQUEST)
    local, domain = email.split("@", 1)
    if not local or not domain or "." not in domain:
        raise PasswordRecoveryRequestServiceError(PasswordRecoveryRequestCode.INVALID_REQUEST)
    return email


def _utc_observation(clock: Callable[[], datetime]) -> datetime:
    """Require one timezone-aware UTC observation without silently coercing time."""

    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise PasswordRecoveryRequestServiceError(PasswordRecoveryRequestCode.AUTHORITY_UNAVAILABLE)
    return value.astimezone(timezone.utc)


def _digest_token(token: str) -> str:
    """Reduce one transient bearer value to lowercase SHA3-512 evidence."""

    return hashlib.sha3_512(token.encode("utf-8")).hexdigest()


class PasswordRecoveryRequestService:
    """Issue and deliver one replacement recovery capability fail-closed.

    Public callers receive only ``PasswordRecoveryRequestResult`` regardless of
    whether a principal is absent, inactive, or within cooldown. Infrastructure
    failures remain code-only exceptions for an HTTP adapter to mask or audit.
    The raw recovery token is generated before persistence, reduced to its
    SHA3-512 digest for durable state, and passed only to the injected delivery
    port after the issuance transaction commits.
    """

    def __init__(
        self,
        *,
        delivery: PasswordRecoveryDelivery,
        client: _MongoClient | None = None,
        auth_registry: _AuthRecoveryLookup | None = None,
        recovery_registry: _RecoveryRegistry | None = None,
        principal_repository: _PrincipalAuthority | None = None,
        clock: Callable[[], datetime] | None = None,
        token_factory: Callable[[], str] | None = None,
        capability_id_factory: Callable[[], str] | None = None,
    ) -> None:
        """Bind authorities without opening persistence or retaining request secrets."""

        if delivery is None:
            raise TypeError("password recovery delivery is required")
        self._delivery = delivery
        self._client = client
        self._auth_registry = auth_registry
        self._recovery_registry = recovery_registry
        self._principal_repository = principal_repository
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._token_factory = token_factory or (lambda: secrets.token_urlsafe(RECOVERY_TOKEN_BYTES))
        self._capability_id_factory = capability_id_factory or (
            lambda: f"{RECOVERY_CAPABILITY_PREFIX}{uuid.uuid4()}"
        )

    def _client_or_fail(self) -> _MongoClient:
        client = self._client if self._client is not None else kernel_db.get_client()
        if client is None:
            raise PasswordRecoveryRequestServiceError(PasswordRecoveryRequestCode.PERSISTENCE_FAILURE)
        return client

    def _auth_or_default(self) -> _AuthRecoveryLookup:
        return self._auth_registry or AuthRegistry()

    def _recovery_or_default(self) -> _RecoveryRegistry:
        return self._recovery_registry or PasswordRecoveryCapabilityRegistry()

    def _principal_or_default(self) -> _PrincipalAuthority:
        return self._principal_repository or PrincipalAuthorityRepository

    def _eligible_principal(
        self, tenant_id: str, email: str, *, session: Any | None = None
    ) -> str | None:
        """Resolve exact principal + ACTIVE lifecycle without exposing absence."""

        try:
            principal_id = self._auth_or_default().resolve_principal_id_by_email_for_tenant(
                tenant_id, email, session=session
            )
            if principal_id is None:
                return None
            authority = self._principal_or_default().get(principal_id, session=session)
            if authority.status is not PrincipalStatus.ACTIVE:
                return None
            return principal_id
        except PrincipalAuthorityNotFoundError:
            return None
        except (AuthRegistryTenantError, PrincipalAuthorityRepositoryError) as error:
            raise PasswordRecoveryRequestServiceError(
                PasswordRecoveryRequestCode.AUTHORITY_UNAVAILABLE
            ) from error

    def _compensate_delivery_failure(
        self, *, tenant_id: str, capability: PasswordRecoveryCapability
    ) -> None:
        """Best-effort transactional removal of undelivered bearer authority."""

        registry = self._recovery_or_default()
        client = self._client_or_fail()

        def callback(session: Any) -> None:
            current = registry.get_by_capability_id(
                tenant_id=tenant_id, capability_id=capability.capability_id, session=session
            )
            if current is None or current.status is not PasswordRecoveryCapabilityStatus.ACTIVE:
                return
            observed = _utc_observation(self._clock)
            if observed >= current.expires_at:
                registry.expire(current, observed, session=session)
            else:
                registry.revoke(current, observed, session=session)

        try:
            with client.start_session() as session:
                session.with_transaction(callback)
        except Exception:
            # The original delivery failure remains the public operational code.
            # No secret is logged; a later lifecycle sweep can expire the row.
            log_auth_event(
                "PASSWORD_RECOVERY_DELIVERY_COMPENSATION",
                capability.principal_id,
                False,
                {"reason": "compensation_failed"},
            )

    def request_recovery(self, *, tenant_id: str, email: str) -> PasswordRecoveryRequestResult:
        """Accept one recovery request without revealing account existence.

        A valid-shaped request always returns the same non-sensitive result for
        absent principals, inactive principals, and cooldown suppression. When
        an ACTIVE principal is eligible, one transaction expires stale ACTIVE
        rows, revokes earlier unexpired windows, and inserts one new digest-only
        capability. Delivery occurs only after commit. Delivery failure triggers
        a compensating lifecycle transaction and raises only a code-only error.
        """

        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise PasswordRecoveryRequestServiceError(PasswordRecoveryRequestCode.INVALID_REQUEST)
        tenant_selector = tenant_id.strip()
        normalized_email = _normalise_email(email)

        raw_token = self._token_factory()
        capability_id = self._capability_id_factory()
        if not isinstance(raw_token, str) or len(raw_token) < 32:
            raise PasswordRecoveryRequestServiceError(PasswordRecoveryRequestCode.AUTHORITY_UNAVAILABLE)
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise PasswordRecoveryRequestServiceError(PasswordRecoveryRequestCode.AUTHORITY_UNAVAILABLE)
        token_digest = _digest_token(raw_token)

        principal_id = self._eligible_principal(tenant_selector, normalized_email)
        if principal_id is None:
            return PasswordRecoveryRequestResult()

        registry = self._recovery_or_default()
        client = self._client_or_fail()
        holder: dict[str, PasswordRecoveryCapability | bool] = {}

        def callback(session: Any) -> None:
            current_principal = self._eligible_principal(
                tenant_selector, normalized_email, session=session
            )
            if current_principal is None or current_principal != principal_id:
                holder["suppressed"] = True
                return

            observed = _utc_observation(self._clock)
            active = registry.list_active_for_principal(
                tenant_id=tenant_selector, principal_id=principal_id, session=session
            )
            unexpired: list[PasswordRecoveryCapability] = []
            for previous in active:
                if observed >= previous.expires_at:
                    registry.expire(previous, observed, session=session)
                else:
                    unexpired.append(previous)

            if any(observed - previous.issued_at < RECOVERY_COOLDOWN for previous in unexpired):
                holder["suppressed"] = True
                return

            for previous in unexpired:
                registry.revoke(previous, observed, session=session)

            capability = PasswordRecoveryCapability.issue(
                capability_id=capability_id,
                tenant_id=tenant_selector,
                principal_id=principal_id,
                token_digest=token_digest,
                issued_at=observed,
                expires_at=observed + RECOVERY_TTL,
            )
            registry.create(capability, session=session)
            holder["capability"] = capability

        try:
            with client.start_session() as session:
                session.with_transaction(callback)
        except PasswordRecoveryRequestServiceError:
            raise
        except (
            PasswordRecoveryCapabilityLifecycleConflictError,
            PasswordRecoveryCapabilityPersistedRecordInvalidError,
            PasswordRecoveryCapabilityPersistenceError,
            PasswordRecoveryCapabilityRegistryError,
        ) as error:
            raise PasswordRecoveryRequestServiceError(
                PasswordRecoveryRequestCode.PERSISTENCE_FAILURE
            ) from error
        except Exception as error:
            raise PasswordRecoveryRequestServiceError(
                PasswordRecoveryRequestCode.TRANSACTION_FAILURE
            ) from error

        capability = holder.get("capability")
        if not isinstance(capability, PasswordRecoveryCapability):
            return PasswordRecoveryRequestResult()

        try:
            self._delivery.deliver_password_recovery(
                recipient_email=normalized_email,
                recovery_token=raw_token,
                expires_at=capability.expires_at,
            )
        except Exception:
            self._compensate_delivery_failure(
                tenant_id=tenant_selector, capability=capability
            )
            log_auth_event(
                "PASSWORD_RECOVERY_DELIVERY",
                principal_id,
                False,
                {"reason": "delivery_failed"},
            )
            raise PasswordRecoveryRequestServiceError(
                PasswordRecoveryRequestCode.DELIVERY_FAILURE
            ) from None

        log_auth_event(
            "PASSWORD_RECOVERY_DELIVERY",
            principal_id,
            True,
            {"expires_in_seconds": int(RECOVERY_TTL.total_seconds())},
        )
        return PasswordRecoveryRequestResult()


__all__ = [
    "PasswordRecoveryDelivery",
    "PasswordRecoveryRequestCode",
    "PasswordRecoveryRequestResult",
    "PasswordRecoveryRequestService",
    "PasswordRecoveryRequestServiceError",
    "RECOVERY_COOLDOWN",
    "RECOVERY_TTL",
    "VERSION",
]

# ARTIFACT: tools/eos/saas/auth/password_recovery_request_service.py
# VERSION: v1.0.0-R10E3-PASSWORD-RECOVERY-REQUEST-ORCHESTRATION
# AUTHORITY BOUNDARY: exact principal admission and recovery-capability issuance orchestration only
# TENANT POSTURE: canonical tenant/email resolution; durable capabilities remain exact tenant/principal
# FAIL-CLOSED POSTURE: ambiguity, corruption, transaction, and delivery failures return no secret or auth material
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
