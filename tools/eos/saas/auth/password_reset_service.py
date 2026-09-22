"""WILSY OS password-reset transaction orchestration.

TITLE: WILSY OS Password Reset Transaction Service
VERSION: v1.1.0-R10G9-ATOMIC-RESET-NOTIFICATION-INTENT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Composes recovery capability, password policy, credential revision,
         session/refresh revocation, capability consumption, and durable
         post-reset security-notification intent into one reset transaction,
         then optionally dispatches the notification only after durable commit.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_reset_service.py
COLLABORATION / OWNERSHIP: The HTTP adapter supplies the recovery token and
                           proposed password. This service owns the composite
                           reset transaction; child registries own caller-session
                           persistence. R10G5 may perform post-commit delivery.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.1.0-R10G9-ATOMIC-RESET-NOTIFICATION-INTENT — Adds one stable
           notification identity/event per reset call, creates PENDING
           PASSWORD_RESET_COMPLETED notification intent on the same transaction
           session after capability consumption, and invokes an injected
           dispatcher only after with_transaction has returned committed.
           Delivery failure does not roll back or misreport the committed reset.
           v1.0.0-R10D1 establishes pre-transaction policy and bcrypt work,
           tenant-scoped capability revalidation, atomic credential revision
           CAS, session and refresh revocation, single-use capability consume,
           and PyMongo with_transaction commit/retry ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw recovery tokens and proposed passwords remain
                            transient call data. Durable recovery state is digest
                            only; durable reset-notification state contains no
                            recipient, password, token, capability digest, JWT,
                            session, refresh, MFA secret, or transport credential.
TENANT BOUNDARY: The supplied tenant_id is only a lookup selector. The
                 digest-matched durable capability supplies authoritative
                 tenant_id/principal_id for credential mutations and notification
                 intent. No caller identity, role, permission, revision, email,
                 MFA, or session list is trusted.
AUTHORITY BOUNDARY: Reset transaction orchestration plus durable notification
                    intent composition only. Password policy, bcrypt, recovery
                    lifecycle, credential CAS, revocation, notification
                    persistence, external delivery, HTTP, and database connection
                    lifecycle remain separate bounded authorities.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: This service owns one Mongo client session and one
                      with_transaction callback. Credential/recovery/notification
                      persistence shares that exact session. External notification
                      dispatch is strictly post-commit and outside Mongo.
FAIL-CLOSED POSTURE: Missing, malformed, expired, consumed, revoked, mismatched,
                     stale, unavailable, notification-intent persistence, or
                     partially failing reset state returns no reset success.
                     Post-commit delivery failure leaves durable retry evidence
                     and does not revoke committed password-reset truth.
"""
from __future__ import annotations

import hashlib
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Protocol

from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import AuthRegistry, AuthRegistryTenantError

from .password_policy import (
    PasswordBlocklistChecker,
    PasswordPolicyViolation,
    validate_password,
)
from .password_recovery import (
    PasswordRecoveryCapability,
    PasswordRecoveryCapabilityError,
)
from .password_recovery_registry import (
    PasswordRecoveryCapabilityLifecycleConflictError,
    PasswordRecoveryCapabilityNotFoundError,
    PasswordRecoveryCapabilityPersistedRecordInvalidError,
    PasswordRecoveryCapabilityPersistenceError,
    PasswordRecoveryCapabilityRegistry,
)
from .password_reset_notification import (
    PasswordResetNotification,
    PasswordResetNotificationError,
)
from .password_reset_notification_dispatcher import (
    PasswordResetNotificationDispatchError,
)
from .password_reset_notification_registry import (
    PasswordResetNotificationRegistry,
    PasswordResetNotificationRegistryError,
)


VERSION: Final[str] = "v1.1.0-R10G9-ATOMIC-RESET-NOTIFICATION-INTENT"


class PasswordResetCode(StrEnum):
    """Candidate-free service classifications for reset outcomes.

    Codes disclose neither account existence, token digest, credential revision,
    password hash, notification identity, recipient, bearer session, nor refresh
    token material.
    """

    INVALID_REQUEST = "PASSWORD_RESET_INVALID_REQUEST"
    RECOVERY_INVALID = "PASSWORD_RESET_RECOVERY_INVALID"
    RECOVERY_REPLAYED = "PASSWORD_RESET_RECOVERY_REPLAYED"
    RECOVERY_PERSISTENCE_FAILURE = "PASSWORD_RESET_RECOVERY_PERSISTENCE_FAILURE"
    POLICY_REJECTED = "PASSWORD_RESET_POLICY_REJECTED"
    HASHING_FAILED = "PASSWORD_RESET_HASHING_FAILED"
    CREDENTIAL_CONFLICT = "PASSWORD_RESET_CREDENTIAL_CONFLICT"
    NOTIFICATION_PERSISTENCE_FAILURE = "PASSWORD_RESET_NOTIFICATION_PERSISTENCE_FAILURE"
    PERSISTENCE_FAILURE = "PASSWORD_RESET_PERSISTENCE_FAILURE"
    TRANSACTION_FAILURE = "PASSWORD_RESET_TRANSACTION_FAILURE"


class PasswordResetServiceError(RuntimeError):
    """Bounded reset failure without password, token, identity, or revision data.

    The service owns no durable error state and never places secret-bearing
    arguments on a long-lived object. Callers may use code for bounded response
    mapping while retaining HTTP, delivery, and financial authority.
    """

    def __init__(self, code: PasswordResetCode) -> None:
        """Create one stable code-only failure."""

        if not isinstance(code, PasswordResetCode):
            raise TypeError("password reset code is invalid")
        self.code = code
        super().__init__(code.value)

    def __str__(self) -> str:
        """Return only the stable public code."""

        return self.code.value

    def __repr__(self) -> str:
        """Return a candidate-free diagnostic representation."""

        return f"PasswordResetServiceError(code={self.code.value!r})"


@dataclass(frozen=True, slots=True)
class PasswordResetResult:
    """Non-sensitive receipt for one committed reset transaction.

    status is the only result authority. Hashes, revisions, identifiers,
    notification IDs, recipients, tokens, sessions, and capability digests are
    intentionally absent. The result creates no session or bearer authority.
    """

    status: str = "PASSWORD_RESET_COMMITTED"


class _RecoveryRegistry(Protocol):
    """Required caller-session recovery persistence contract."""

    def get_by_token_digest(
        self,
        *,
        tenant_id: str,
        token_digest: str,
        session: Any | None = None,
    ) -> PasswordRecoveryCapability | None: ...

    def consume(
        self,
        capability: PasswordRecoveryCapability,
        consumed_at: datetime,
        *,
        session: Any | None = None,
    ) -> PasswordRecoveryCapability: ...


class _AuthAuthority(Protocol):
    """Required password and tenant-scoped revocation contract."""

    def hash_password(self, password: str) -> str: ...

    def get_credential_revision(
        self, tenant_id: str, user_id: str, *, session: Any = None
    ) -> int: ...

    def compare_and_swap_password_hash(
        self,
        tenant_id: str,
        user_id: str,
        expected_credential_revision: int,
        new_password_hash: str,
        *,
        session: Any = None,
    ) -> int: ...

    def revoke_sessions(
        self, tenant_id: str, user_id: str, *, session: Any = None
    ) -> int: ...

    def revoke_refresh_tokens(
        self, tenant_id: str, user_id: str, *, session: Any = None
    ) -> int: ...


class _NotificationRegistry(Protocol):
    """Required caller-session notification-intent persistence contract."""

    def create(
        self,
        notification: PasswordResetNotification,
        *,
        session: Any | None = None,
    ) -> PasswordResetNotification: ...


class _NotificationDispatcher(Protocol):
    """Optional post-commit notification dispatch contract."""

    def dispatch(
        self,
        *,
        tenant_id: str,
        notification_id: str,
        observed_at: datetime,
    ) -> Any: ...


class _MongoClient(Protocol):
    """Minimal client-owned transaction protocol for production and smoke use."""

    def start_session(self) -> Any: ...


def _digest_recovery_token(recovery_token: str) -> str:
    """Derive the certified lowercase SHA3-512 lookup digest transiently."""

    if not isinstance(recovery_token, str) or not recovery_token:
        raise PasswordResetServiceError(PasswordResetCode.INVALID_REQUEST)
    try:
        return hashlib.sha3_512(recovery_token.encode("utf-8")).hexdigest()
    except UnicodeEncodeError:
        raise PasswordResetServiceError(PasswordResetCode.INVALID_REQUEST) from None


def _map_recovery_error(error: Exception) -> PasswordResetServiceError:
    """Map recovery registry/domain failures without exposing durable state."""

    if isinstance(error, PasswordRecoveryCapabilityPersistenceError):
        return PasswordResetServiceError(PasswordResetCode.RECOVERY_PERSISTENCE_FAILURE)
    if isinstance(error, PasswordRecoveryCapabilityLifecycleConflictError):
        if error.code == "RECOVERY_CAPABILITY_CONSUMED":
            return PasswordResetServiceError(PasswordResetCode.RECOVERY_REPLAYED)
        return PasswordResetServiceError(PasswordResetCode.RECOVERY_INVALID)
    if isinstance(
        error,
        (
            PasswordRecoveryCapabilityNotFoundError,
            PasswordRecoveryCapabilityPersistedRecordInvalidError,
            PasswordRecoveryCapabilityError,
        ),
    ):
        return PasswordResetServiceError(PasswordResetCode.RECOVERY_INVALID)
    return PasswordResetServiceError(PasswordResetCode.TRANSACTION_FAILURE)


class PasswordResetService:
    """Execute one exact atomic reset and commit notification intent with it.

    The durable recovery capability is sole reset authority. Policy validation
    and bcrypt hashing occur before Mongo transaction startup. A stable
    notification identity and event timestamp are also created once before the
    transaction callback so PyMongo callback retries represent the same logical
    post-reset event.

    The callback re-reads the capability, validates exact durable binding, reads
    credential revision, performs password/revision CAS, revokes sessions and
    refresh tokens, consumes the capability, and inserts pristine PENDING
    notification intent using the same caller-owned session. Any notification
    persistence failure aborts the whole reset transaction.

    After with_transaction returns successfully, an injected dispatcher may
    attempt external notification exactly once for this public call. A certified
    dispatcher failure is intentionally non-fatal to the already-committed reset:
    durable PENDING/attempt evidence remains available for retry. This service
    does not construct recipients or own SMTP.
    """

    def __init__(
        self,
        *,
        client: _MongoClient | None = None,
        recovery_registry: _RecoveryRegistry | None = None,
        auth_registry: _AuthAuthority | None = None,
        notification_registry: _NotificationRegistry | None = None,
        notification_dispatcher: _NotificationDispatcher | None = None,
        blocklist_checker: PasswordBlocklistChecker | None = None,
        clock: Callable[[], datetime] | None = None,
        notification_id_factory: Callable[[], str] | None = None,
    ) -> None:
        """Bind explicit authorities without opening Mongo or retaining secrets.

        notification_dispatcher is optional so transaction authority remains
        independent of external transport availability. Production wiring may
        inject the certified R10G5 dispatcher for immediate post-commit delivery.
        """

        self._client = client
        self._recovery_registry = recovery_registry
        self._auth_registry = auth_registry
        self._notification_registry = notification_registry
        self._notification_dispatcher = notification_dispatcher
        self._blocklist_checker = blocklist_checker
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._notification_id_factory = notification_id_factory or (
            lambda: f"WILSYRESETNOTICE-{uuid.uuid4()}"
        )

    def _client_or_fail(self) -> _MongoClient:
        """Resolve the canonical Kernel client only when execution begins."""

        client = self._client if self._client is not None else kernel_db.get_client()
        if client is None:
            raise PasswordResetServiceError(PasswordResetCode.PERSISTENCE_FAILURE)
        return client

    def _recovery_or_default(self) -> _RecoveryRegistry:
        """Resolve the certified recovery registry lazily."""

        return self._recovery_registry or PasswordRecoveryCapabilityRegistry()

    def _auth_or_default(self) -> _AuthAuthority:
        """Resolve the certified password/revocation authority lazily."""

        return self._auth_registry or AuthRegistry()

    def _notification_or_default(self) -> _NotificationRegistry:
        """Resolve the certified notification registry lazily."""

        return self._notification_registry or PasswordResetNotificationRegistry()

    def _preflight(
        self, *, tenant_id: str, token_digest: str
    ) -> PasswordRecoveryCapability:
        """Reject clearly unusable capability state before transaction startup.

        This read is an optimization only. The transaction callback repeats the
        lookup and usability check, so a preflight snapshot never authorizes a
        mutation or substitutes for lifecycle CAS.
        """

        registry = self._recovery_or_default()
        try:
            capability = registry.get_by_token_digest(
                tenant_id=tenant_id, token_digest=token_digest
            )
            if capability is None:
                raise PasswordResetServiceError(PasswordResetCode.RECOVERY_INVALID)
            capability.assert_usable_at(self._clock())
            return capability
        except PasswordResetServiceError:
            raise
        except Exception as error:
            mapped = _map_recovery_error(error)
            if mapped.code is PasswordResetCode.TRANSACTION_FAILURE:
                mapped = PasswordResetServiceError(
                    PasswordResetCode.RECOVERY_PERSISTENCE_FAILURE
                )
            raise mapped from None

    def reset_password(
        self,
        *,
        tenant_id: str,
        recovery_token: str,
        new_password: str,
        context_terms: Iterable[str] | None = None,
    ) -> PasswordResetResult:
        """Reset one capability-bound principal and atomically persist notice intent.

        Authority: the durable recovery capability is sole reset authorization.
        tenant_id remains only the registry lookup selector. The notification
        derives tenant/principal exclusively from that same durable capability.

        Secret handling: policy/bcrypt receive the proposed password before
        transaction startup. The raw recovery token becomes only a transient
        SHA3-512 lookup digest. Neither secret nor recipient address appears in
        notification state or the returned receipt.

        Transaction semantics: password CAS, session revocation, refresh
        revocation, capability consumption, and pristine PENDING notification
        creation all share one Mongo session and transaction callback. PyMongo
        owns whole-callback retry. notification_id/event time are created once
        outside the callback so transaction retries refer to one logical event.

        Post-commit semantics: when a dispatcher was injected, it runs only after
        with_transaction returns. A stable dispatch failure cannot roll back the
        committed reset and is not converted into a false reset failure.

        :param tenant_id: Required lookup selector, never trusted authority.
        :param recovery_token: One transient bearer capability value.
        :param new_password: Complete prospective password text.
        :param context_terms: Optional exact policy context terms.
        :returns: A non-sensitive committed receipt.
        :raises PasswordResetServiceError: For invalid/conflicting/unavailable
            pre-commit reset or notification-intent state.
        """

        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise PasswordResetServiceError(PasswordResetCode.INVALID_REQUEST)
        token_digest = _digest_recovery_token(recovery_token)
        capability = self._preflight(tenant_id=tenant_id, token_digest=token_digest)

        try:
            validate_password(
                new_password,
                checker=self._blocklist_checker,
                context_terms=context_terms,
            )
        except PasswordPolicyViolation:
            raise PasswordResetServiceError(PasswordResetCode.POLICY_REJECTED) from None

        try:
            password_hash = self._auth_or_default().hash_password(new_password)
        except Exception:
            raise PasswordResetServiceError(PasswordResetCode.HASHING_FAILED) from None
        if not isinstance(password_hash, str) or not password_hash:
            raise PasswordResetServiceError(PasswordResetCode.HASHING_FAILED)

        try:
            notification = PasswordResetNotification.issue(
                notification_id=self._notification_id_factory(),
                tenant_id=capability.tenant_id,
                principal_id=capability.principal_id,
                occurred_at=self._clock(),
            )
        except (PasswordResetNotificationError, Exception) as error:
            if isinstance(error, PasswordResetNotificationError):
                raise PasswordResetServiceError(
                    PasswordResetCode.NOTIFICATION_PERSISTENCE_FAILURE
                ) from None
            raise PasswordResetServiceError(
                PasswordResetCode.NOTIFICATION_PERSISTENCE_FAILURE
            ) from None

        registry = self._recovery_or_default()
        auth = self._auth_or_default()
        notification_registry = self._notification_or_default()
        client = self._client_or_fail()
        holder: dict[str, PasswordResetResult] = {}

        def callback(session: Any) -> None:
            """Revalidate and perform every reset mutation on one session."""

            try:
                current = registry.get_by_token_digest(
                    tenant_id=tenant_id,
                    token_digest=token_digest,
                    session=session,
                )
                if current is None:
                    raise PasswordResetServiceError(PasswordResetCode.RECOVERY_INVALID)
                current.assert_usable_at(self._clock())
                if (
                    current.tenant_id != capability.tenant_id
                    or current.principal_id != capability.principal_id
                    or current.token_digest != capability.token_digest
                ):
                    raise PasswordResetServiceError(PasswordResetCode.RECOVERY_INVALID)

                expected_revision = auth.get_credential_revision(
                    current.tenant_id,
                    current.principal_id,
                    session=session,
                )
                auth.compare_and_swap_password_hash(
                    current.tenant_id,
                    current.principal_id,
                    expected_revision,
                    password_hash,
                    session=session,
                )
                auth.revoke_sessions(
                    current.tenant_id,
                    current.principal_id,
                    session=session,
                )
                auth.revoke_refresh_tokens(
                    current.tenant_id,
                    current.principal_id,
                    session=session,
                )
                registry.consume(current, self._clock(), session=session)
                notification_registry.create(notification, session=session)
                holder["result"] = PasswordResetResult()
            except PasswordResetServiceError:
                raise
            except (
                PasswordRecoveryCapabilityLifecycleConflictError,
                PasswordRecoveryCapabilityNotFoundError,
                PasswordRecoveryCapabilityPersistedRecordInvalidError,
                PasswordRecoveryCapabilityPersistenceError,
                PasswordRecoveryCapabilityError,
            ) as error:
                raise _map_recovery_error(error) from None
            except PasswordResetNotificationRegistryError:
                raise PasswordResetServiceError(
                    PasswordResetCode.NOTIFICATION_PERSISTENCE_FAILURE
                ) from None
            except AuthRegistryTenantError as error:
                if "CREDENTIAL" in str(error):
                    raise PasswordResetServiceError(
                        PasswordResetCode.CREDENTIAL_CONFLICT
                    ) from None
                raise PasswordResetServiceError(
                    PasswordResetCode.PERSISTENCE_FAILURE
                ) from None
            except Exception:
                raise PasswordResetServiceError(
                    PasswordResetCode.TRANSACTION_FAILURE
                ) from None

        try:
            with client.start_session() as session:
                session.with_transaction(callback)
        except PasswordResetServiceError:
            raise
        except Exception:
            raise PasswordResetServiceError(
                PasswordResetCode.TRANSACTION_FAILURE
            ) from None

        if "result" not in holder:
            raise PasswordResetServiceError(PasswordResetCode.TRANSACTION_FAILURE)

        if self._notification_dispatcher is not None:
            try:
                self._notification_dispatcher.dispatch(
                    tenant_id=notification.tenant_id,
                    notification_id=notification.notification_id,
                    observed_at=self._clock(),
                )
            except PasswordResetNotificationDispatchError:
                pass

        return holder["result"]


__all__ = [
    "PasswordResetCode",
    "PasswordResetResult",
    "PasswordResetService",
    "PasswordResetServiceError",
    "VERSION",
]


# ARTIFACT: password_reset_service.py
# VERSION: v1.1.0-R10G9-ATOMIC-RESET-NOTIFICATION-INTENT
# AUTHORITY BOUNDARY: atomic password-reset plus durable notification-intent orchestration only
# TENANT POSTURE: durable recovery capability supplies exact tenant/principal for reset and notice
# FAIL-CLOSED POSTURE: pre-commit reset/notice failures deny success; post-commit dispatch failure cannot undo reset
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
