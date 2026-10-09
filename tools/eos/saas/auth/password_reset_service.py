"""WILSY OS password-reset transaction orchestration.

TITLE: WILSY OS Password Reset Transaction Service
VERSION: v1.1.0-R10E76-PASSWORD-POLICY-DEPENDENCY-CLASSIFICATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Composes the certified recovery-capability, password-policy,
         credential-revision, session-revocation, and tenant-bearing
         refresh-revocation authorities into one caller-owned reset transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_reset_service.py
COLLABORATION / OWNERSHIP: A future HTTP/API adapter supplies the recovery
                           token and proposed password. This service owns the
                           composite reset transaction; child registries own
                           only their caller-session persistence operations.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: v1.1.0-R10E76-PASSWORD-POLICY-DEPENDENCY-CLASSIFICATION distinguishes user-correctable password-policy
           rejection from fail-closed compromised-password dependency failure
           before hashing or transaction startup; no reset authority is broadened.
           v1.0.0-R10D1 establishes pre-transaction policy and bcrypt work,
           tenant-scoped capability revalidation, atomic credential revision
           CAS, session and refresh revocation, single-use capability consume,
           and PyMongo with_transaction commit/retry ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw recovery tokens and proposed passwords remain
                            transient call data. Neither is stored, logged,
                            returned, placed in service state, or included in
                            public errors. Durable capability state is digest
                            only and all mutations are exact tenant/principal
                            operations.
TENANT BOUNDARY: The supplied tenant_id is only a lookup selector. The
                 digest-matched durable capability supplies the authoritative
                 tenant_id and principal_id; no caller identity, role,
                 permission, revision, MFA, or session list is trusted.
AUTHORITY BOUNDARY: Reset orchestration only. Password policy, bcrypt,
                    recovery lifecycle, credential CAS, session revocation,
                    refresh revocation, and Mongo connection lifecycle remain
                    separate injected authorities. No JWT, MFA, membership,
                    role, delivery, HTTP, Node, or financial authority exists.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: This service owns one Mongo client session and
                       ``with_transaction`` callback. Child registries never
                       start, commit, abort, or retry transactions.
FAIL-CLOSED POSTURE: Missing, malformed, expired, consumed, revoked,
                     mismatched, stale, unavailable, or partially failing
                     reset state raises a bounded service error; no partial
                     reset result is returned.
"""
from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Protocol

from .password_policy import (
    PasswordBlocklistChecker,
    PasswordPolicyCode,
    PasswordPolicyViolation,
    validate_password,
)
from .password_recovery import (
    PasswordRecoveryCapability,
    PasswordRecoveryCapabilityError,
    PasswordRecoveryCapabilityStatus,
)
from .password_recovery_registry import (
    PasswordRecoveryCapabilityLifecycleConflictError,
    PasswordRecoveryCapabilityNotFoundError,
    PasswordRecoveryCapabilityPersistedRecordInvalidError,
    PasswordRecoveryCapabilityPersistenceError,
    PasswordRecoveryCapabilityRegistry,
)
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import AuthRegistry, AuthRegistryTenantError


VERSION: Final[str] = "v1.0.0-R10D1-PASSWORD-RESET-TRANSACTION-ORCHESTRATION"


class PasswordResetCode(StrEnum):
    """Candidate-free service classifications for reset outcomes.

    Authority: service-domain failure vocabulary only. Codes disclose neither
    account existence, token digest, credential revision, hash, bearer session,
    nor refresh-token material.
    """

    INVALID_REQUEST = "PASSWORD_RESET_INVALID_REQUEST"
    RECOVERY_INVALID = "PASSWORD_RESET_RECOVERY_INVALID"
    RECOVERY_REPLAYED = "PASSWORD_RESET_RECOVERY_REPLAYED"
    RECOVERY_PERSISTENCE_FAILURE = "PASSWORD_RESET_RECOVERY_PERSISTENCE_FAILURE"
    POLICY_REJECTED = "PASSWORD_RESET_POLICY_REJECTED"
    POLICY_DEPENDENCY_FAILURE = "PASSWORD_RESET_POLICY_DEPENDENCY_FAILURE"
    HASHING_FAILED = "PASSWORD_RESET_HASHING_FAILED"
    CREDENTIAL_CONFLICT = "PASSWORD_RESET_CREDENTIAL_CONFLICT"
    PERSISTENCE_FAILURE = "PASSWORD_RESET_PERSISTENCE_FAILURE"
    TRANSACTION_FAILURE = "PASSWORD_RESET_TRANSACTION_FAILURE"


class PasswordResetServiceError(RuntimeError):
    """Bounded reset failure without password, token, identity, or revision data.

    The service owns no durable error state and never places secret-bearing
    arguments on a long-lived object. Callers may use ``code`` for bounded
    response mapping while retaining HTTP, delivery, and financial authority.
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

    ``status`` is the only result authority. Hashes, revisions, identifiers,
    tokens, sessions, and capability digests are intentionally absent. The
    result does not create a session or issue any JWT or refresh token.
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
    """Map registry/domain failures without exposing durable state details."""

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
    """Execute one exact, atomic password reset using certified authorities.

    The service requires a tenant routing selector because the certified
    recovery registry exposes a tenant-scoped digest lookup. That selector is
    never trusted as reset authority: the returned durable capability must bind
    the exact tenant and principal before any mutation. ``client``,
    ``recovery_registry``, ``auth_registry``, ``blocklist_checker``, and
    ``clock`` are injectable for deterministic certification; omitted client
    and registry dependencies resolve only through the canonical Kernel at
    invocation time.

    Policy validation and bcrypt hashing occur before a Mongo transaction. The
    transaction callback re-reads and validates the capability, reads the
    current credential revision, performs the atomic password/revision CAS,
    revokes exact tenant/principal sessions and refresh tokens, and consumes
    the capability through its lifecycle CAS. PyMongo ``with_transaction``
    owns transient transaction retry and unknown-commit retry semantics; this
    service never blindly invokes the callback a second time.

    No authenticated session, access JWT, refresh token, MFA change, role
    change, membership change, delivery action, HTTP request, Node call, or
    financial execution is performed here.
    """

    def __init__(
        self,
        *,
        client: _MongoClient | None = None,
        recovery_registry: _RecoveryRegistry | None = None,
        auth_registry: _AuthAuthority | None = None,
        blocklist_checker: PasswordBlocklistChecker | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Bind explicit authorities without opening Mongo or retaining secrets."""

        self._client = client
        self._recovery_registry = recovery_registry
        self._auth_registry = auth_registry
        self._blocklist_checker = blocklist_checker
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _client_or_fail(self) -> _MongoClient:
        """Resolve the canonical Kernel client only when execution begins."""

        client = self._client if self._client is not None else kernel_db.get_client()
        if client is None:
            raise PasswordResetServiceError(PasswordResetCode.PERSISTENCE_FAILURE)
        return client

    def _recovery_or_default(self) -> _RecoveryRegistry:
        """Resolve the certified registry without creating a hidden service locator."""

        return self._recovery_registry or PasswordRecoveryCapabilityRegistry()

    def _auth_or_default(self) -> _AuthAuthority:
        """Resolve the certified password/revocation authority lazily."""

        return self._auth_registry or AuthRegistry()

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
                mapped = PasswordResetServiceError(PasswordResetCode.RECOVERY_PERSISTENCE_FAILURE)
            raise mapped from None

    def reset_password(
        self,
        *,
        tenant_id: str,
        recovery_token: str,
        new_password: str,
        context_terms: Iterable[str] | None = None,
    ) -> PasswordResetResult:
        """Reset one capability-bound principal in one Mongo transaction.

        Authority: the durable recovery capability is the sole reset
        authorization. ``tenant_id`` is only the registry's required lookup
        selector; its returned capability supplies the authoritative tenant and
        principal. Mutation semantics are one atomic composition of password
        hash/revision CAS, session deletion, refresh deletion, and ACTIVE to
        CONSUMED capability CAS. Transaction ownership belongs exclusively to
        this service and the canonical Mongo client.

        Secret handling: policy and bcrypt receive the supplied password before
        transaction startup; the raw recovery token is reduced to a SHA3-512
        digest and is never persisted, logged, returned, or retained in object
        state. Failure messages contain stable codes only. No session, JWT,
        refresh token, MFA, role, membership, delivery, HTTP, Node, or financial
        mutation is performed.

        :param tenant_id: Required lookup selector, never trusted authority.
        :param recovery_token: One transient bearer capability value.
        :param new_password: Complete prospective password text.
        :param context_terms: Optional exact policy context terms.
        :returns: A non-sensitive committed receipt.
        :raises PasswordResetServiceError: For any invalid, conflicting,
            unavailable, or failed reset state.
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
        except PasswordPolicyViolation as error:
            if error.code in {
                PasswordPolicyCode.BLOCKLIST_UNAVAILABLE,
                PasswordPolicyCode.BLOCKLIST_FAILURE,
            }:
                raise PasswordResetServiceError(
                    PasswordResetCode.POLICY_DEPENDENCY_FAILURE
                ) from None
            raise PasswordResetServiceError(PasswordResetCode.POLICY_REJECTED) from None

        try:
            password_hash = self._auth_or_default().hash_password(new_password)
        except Exception:
            raise PasswordResetServiceError(PasswordResetCode.HASHING_FAILED) from None
        if not isinstance(password_hash, str) or not password_hash:
            raise PasswordResetServiceError(PasswordResetCode.HASHING_FAILED)

        registry = self._recovery_or_default()
        auth = self._auth_or_default()
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
                    current.tenant_id, current.principal_id, session=session
                )
                auth.compare_and_swap_password_hash(
                    current.tenant_id,
                    current.principal_id,
                    expected_revision,
                    password_hash,
                    session=session,
                )
                auth.revoke_sessions(
                    current.tenant_id, current.principal_id, session=session
                )
                auth.revoke_refresh_tokens(
                    current.tenant_id, current.principal_id, session=session
                )
                registry.consume(current, self._clock(), session=session)
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
            except AuthRegistryTenantError as error:
                if "CREDENTIAL" in str(error):
                    raise PasswordResetServiceError(PasswordResetCode.CREDENTIAL_CONFLICT) from None
                raise PasswordResetServiceError(PasswordResetCode.PERSISTENCE_FAILURE) from None
            except Exception:
                raise PasswordResetServiceError(PasswordResetCode.TRANSACTION_FAILURE) from None

        try:
            with client.start_session() as session:
                session.with_transaction(callback)
        except PasswordResetServiceError:
            raise
        except Exception:
            raise PasswordResetServiceError(PasswordResetCode.TRANSACTION_FAILURE) from None
        if "result" not in holder:
            raise PasswordResetServiceError(PasswordResetCode.TRANSACTION_FAILURE)
        return holder["result"]


__all__ = [
    "PasswordResetCode",
    "PasswordResetResult",
    "PasswordResetService",
    "PasswordResetServiceError",
    "VERSION",
]


# ARTIFACT: password_reset_service.py
# VERSION: v1.1.0-R10E76-PASSWORD-POLICY-DEPENDENCY-CLASSIFICATION
# AUTHORITY BOUNDARY: composite password-reset orchestration only; child registries retain their bounded authorities
# TENANT POSTURE: durable recovery capability supplies exact tenant/principal; selector is never trusted authority
# FAIL-CLOSED POSTURE: policy, capability, CAS, revocation, consume, and transaction failures never return success
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
