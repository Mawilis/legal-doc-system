"""Recovery-contact verification completion transaction for WILSY OS.

TITLE: WILSY OS Recovery Contact Verification Completion Service
VERSION: v1.0.0-R10E21-RECOVERY-CONTACT-VERIFICATION-COMPLETION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Atomically consumes one email-control verification capability and
         establishes exactly one ACTIVE verified recovery contact for the bound
         tenant/principal/current durable email.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_contact_verification_service.py
COLLABORATION / OWNERSHIP: R10E15/R10E16 own verification lifecycle; R10E1/R10E19
                           own verified-contact state; AuthRegistry re-proves the
                           exact durable principal/email; this service owns only
                           the composite Mongo transaction.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E21-RECOVERY-CONTACT-VERIFICATION-COMPLETION introduces
           digest-only token lookup, transaction-scoped verification re-read,
           exact tenant/principal credential binding, current-email digest
           recheck, atomic prior-contact replacement, contact creation, and
           verification consume with PyMongo transaction retry ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Raw verification tokens remain transient call data.
                            Raw email is read only from durable user authority and
                            never persisted in verification/contact records.
TENANT BOUNDARY: The durable verification supplies authoritative tenant/principal
                 binding; caller tenant is a lookup selector only.
AUTHORITY BOUNDARY: Verified recovery-contact enrollment transaction only; no
                    password reset, delivery, session, JWT, MFA, membership,
                    role, HTTP, Node, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: This service owns one Mongo ClientSession and one
                      with_transaction callback. Child registries only receive
                      the caller-owned session and never commit or retry.
FAIL-CLOSED POSTURE: Missing, malformed, replayed, expired, revoked, stale-email,
                     tenant/principal mismatch, persistence, or transaction
                     failure cannot return committed contact authority.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable, Final, Protocol

from tools.eos.kernel import db as kernel_db

from .auth_registry import AuthRegistry, AuthRegistryTenantError
from .password_recovery_contact import (
    VerifiedRecoveryContact,
    VerifiedRecoveryContactChannel,
)
from .password_recovery_contact_registry import (
    VerifiedRecoveryContactLifecycleConflictError,
    VerifiedRecoveryContactPersistenceError,
    VerifiedRecoveryContactRegistry,
    VerifiedRecoveryContactRegistryError,
)
from .password_recovery_contact_verification import (
    RecoveryContactVerification,
    RecoveryContactVerificationError,
)
from .password_recovery_contact_verification_registry import (
    RecoveryContactVerificationLifecycleConflictError,
    RecoveryContactVerificationNotFoundError,
    RecoveryContactVerificationPersistedRecordInvalidError,
    RecoveryContactVerificationPersistenceError,
    RecoveryContactVerificationRegistry,
    RecoveryContactVerificationRegistryError,
)
from .password_recovery_request_service import (
    normalize_recovery_email,
    recovery_address_digest,
)

VERSION: Final[str] = "v1.0.0-R10E21-RECOVERY-CONTACT-VERIFICATION-COMPLETION"


class RecoveryContactVerificationCode(StrEnum):
    """Stable completion outcomes without contact/token disclosure."""

    INVALID_REQUEST = "RECOVERY_CONTACT_VERIFICATION_INVALID_REQUEST"
    VERIFICATION_INVALID = "RECOVERY_CONTACT_VERIFICATION_INVALID"
    VERIFICATION_REPLAYED = "RECOVERY_CONTACT_VERIFICATION_REPLAYED"
    PRINCIPAL_MISMATCH = "RECOVERY_CONTACT_VERIFICATION_PRINCIPAL_MISMATCH"
    EMAIL_CHANGED = "RECOVERY_CONTACT_VERIFICATION_EMAIL_CHANGED"
    PERSISTENCE_FAILURE = "RECOVERY_CONTACT_VERIFICATION_PERSISTENCE_FAILURE"
    TRANSACTION_FAILURE = "RECOVERY_CONTACT_VERIFICATION_TRANSACTION_FAILURE"


class RecoveryContactVerificationServiceError(RuntimeError):
    """Bounded code-only completion failure."""

    def __init__(self, code: RecoveryContactVerificationCode) -> None:
        if not isinstance(code, RecoveryContactVerificationCode):
            raise TypeError("recovery contact verification code is invalid")
        self.code = code
        super().__init__(code.value)

    def __str__(self) -> str:
        return self.code.value


@dataclass(frozen=True, slots=True)
class RecoveryContactVerificationResult:
    """Non-sensitive receipt for one committed verified-contact enrollment."""

    status: str = "RECOVERY_CONTACT_VERIFIED"


class _VerificationRegistry(Protocol):
    def get_by_token_digest(
        self,
        *,
        tenant_id: str,
        token_digest: str,
        session: Any | None = None,
    ) -> RecoveryContactVerification | None: ...

    def consume(
        self,
        verification: RecoveryContactVerification,
        consumed_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerification: ...


class _ContactRegistry(Protocol):
    def get_active_by_principal(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        channel: VerifiedRecoveryContactChannel = VerifiedRecoveryContactChannel.EMAIL,
        session: Any | None = None,
    ) -> VerifiedRecoveryContact | None: ...

    def create(
        self,
        contact: VerifiedRecoveryContact,
        *,
        session: Any | None = None,
    ) -> VerifiedRecoveryContact: ...

    def revoke(
        self,
        contact: VerifiedRecoveryContact,
        revoked_at: datetime,
        *,
        session: Any | None = None,
    ) -> VerifiedRecoveryContact: ...


class _AuthAuthority(Protocol):
    def get_credential_revision(
        self,
        tenant_id: str,
        user_id: str,
        *,
        session: Any = None,
    ) -> int: ...

    def get_user_by_id(self, user_id: str, *, session: Any = None) -> Any: ...


class _MongoClient(Protocol):
    def start_session(self) -> Any: ...


def _token_digest(raw_token: object) -> str:
    """Derive lowercase SHA3-512 lookup digest from transient raw capability."""

    if not isinstance(raw_token, str) or not raw_token or len(raw_token) > 4096:
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationCode.INVALID_REQUEST
        )
    try:
        return hashlib.sha3_512(raw_token.encode("utf-8")).hexdigest()
    except UnicodeEncodeError:
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationCode.INVALID_REQUEST
        ) from None


def _tenant_selector(value: object) -> str:
    """Validate caller tenant lookup selector without granting authority."""

    if not isinstance(value, str):
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationCode.INVALID_REQUEST
        )
    normalized = value.strip()
    if not normalized or normalized != value or len(normalized) > 256:
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationCode.INVALID_REQUEST
        )
    return normalized


def _map_verification_error(error: Exception) -> RecoveryContactVerificationServiceError:
    """Map verification registry/domain failure to bounded completion codes."""

    if isinstance(error, RecoveryContactVerificationLifecycleConflictError):
        if error.code == "RECOVERY_CONTACT_VERIFICATION_CONSUMED":
            return RecoveryContactVerificationServiceError(
                RecoveryContactVerificationCode.VERIFICATION_REPLAYED
            )
        return RecoveryContactVerificationServiceError(
            RecoveryContactVerificationCode.VERIFICATION_INVALID
        )
    if isinstance(
        error,
        (
            RecoveryContactVerificationNotFoundError,
            RecoveryContactVerificationPersistedRecordInvalidError,
            RecoveryContactVerificationError,
        ),
    ):
        return RecoveryContactVerificationServiceError(
            RecoveryContactVerificationCode.VERIFICATION_INVALID
        )
    if isinstance(
        error,
        (
            RecoveryContactVerificationPersistenceError,
            RecoveryContactVerificationRegistryError,
        ),
    ):
        return RecoveryContactVerificationServiceError(
            RecoveryContactVerificationCode.PERSISTENCE_FAILURE
        )
    return RecoveryContactVerificationServiceError(
        RecoveryContactVerificationCode.TRANSACTION_FAILURE
    )


class RecoveryContactVerificationService:
    """Consume one email-control proof and establish recovery-contact authority."""

    def __init__(
        self,
        *,
        client: _MongoClient | None = None,
        verification_registry: _VerificationRegistry | None = None,
        contact_registry: _ContactRegistry | None = None,
        auth_registry: _AuthAuthority | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Bind explicit authorities without opening Mongo or retaining secrets."""

        self._client = client
        self._verification_registry = verification_registry
        self._contact_registry = contact_registry
        self._auth_registry = auth_registry
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _client_or_fail(self) -> _MongoClient:
        client = self._client if self._client is not None else kernel_db.get_client()
        if client is None:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationCode.PERSISTENCE_FAILURE
            )
        return client

    def _verification_or_default(self) -> _VerificationRegistry:
        return self._verification_registry or RecoveryContactVerificationRegistry()

    def _contact_or_default(self) -> _ContactRegistry:
        return self._contact_registry or VerifiedRecoveryContactRegistry()

    def _auth_or_default(self) -> _AuthAuthority:
        return self._auth_registry or AuthRegistry()

    def verify_contact(
        self,
        *,
        tenant_id: str,
        verification_token: str,
    ) -> RecoveryContactVerificationResult:
        """Consume one verification capability and commit verified contact truth.

        The caller-provided tenant is only the registry lookup selector. The
        durable verification supplies authoritative tenant/principal/address
        binding. The transaction re-reads the durable user and requires its
        current email digest to equal the verification address digest before
        replacing or creating ACTIVE recovery-contact authority.
        """

        tenant = _tenant_selector(tenant_id)
        token_digest = _token_digest(verification_token)
        verification_registry = self._verification_or_default()
        contact_registry = self._contact_or_default()
        auth = self._auth_or_default()
        client = self._client_or_fail()
        contact_id = f"WILSYRECOVERYCONTACT-{uuid.uuid4()}"
        holder: dict[str, RecoveryContactVerificationResult] = {}

        def callback(session: Any) -> None:
            try:
                current = verification_registry.get_by_token_digest(
                    tenant_id=tenant,
                    token_digest=token_digest,
                    session=session,
                )
                if current is None:
                    raise RecoveryContactVerificationServiceError(
                        RecoveryContactVerificationCode.VERIFICATION_INVALID
                    )

                observed = self._clock()
                current.assert_usable_at(observed)
                if current.tenant_id != tenant or current.token_digest != token_digest:
                    raise RecoveryContactVerificationServiceError(
                        RecoveryContactVerificationCode.VERIFICATION_INVALID
                    )

                auth.get_credential_revision(
                    current.tenant_id,
                    current.principal_id,
                    session=session,
                )
                user = auth.get_user_by_id(current.principal_id, session=session)
                if (
                    user is None
                    or user.id != current.principal_id
                    or user.tenantId != current.tenant_id
                ):
                    raise RecoveryContactVerificationServiceError(
                        RecoveryContactVerificationCode.PRINCIPAL_MISMATCH
                    )

                try:
                    current_email = normalize_recovery_email(str(user.email))
                except Exception:
                    raise RecoveryContactVerificationServiceError(
                        RecoveryContactVerificationCode.EMAIL_CHANGED
                    ) from None
                if recovery_address_digest(current_email) != current.address_digest:
                    raise RecoveryContactVerificationServiceError(
                        RecoveryContactVerificationCode.EMAIL_CHANGED
                    )

                existing = contact_registry.get_active_by_principal(
                    tenant_id=current.tenant_id,
                    principal_id=current.principal_id,
                    channel=VerifiedRecoveryContactChannel.EMAIL,
                    session=session,
                )
                if existing is not None and existing.address_digest != current.address_digest:
                    contact_registry.revoke(existing, observed, session=session)
                    existing = None

                if existing is None:
                    contact = VerifiedRecoveryContact.issue(
                        contact_id=contact_id,
                        tenant_id=current.tenant_id,
                        principal_id=current.principal_id,
                        channel=VerifiedRecoveryContactChannel.EMAIL,
                        address_digest=current.address_digest,
                        verified_at=observed,
                    )
                    contact_registry.create(contact, session=session)

                verification_registry.consume(current, observed, session=session)
                holder["result"] = RecoveryContactVerificationResult()
            except RecoveryContactVerificationServiceError:
                raise
            except (
                RecoveryContactVerificationLifecycleConflictError,
                RecoveryContactVerificationNotFoundError,
                RecoveryContactVerificationPersistedRecordInvalidError,
                RecoveryContactVerificationPersistenceError,
                RecoveryContactVerificationRegistryError,
                RecoveryContactVerificationError,
            ) as error:
                raise _map_verification_error(error) from None
            except AuthRegistryTenantError:
                raise RecoveryContactVerificationServiceError(
                    RecoveryContactVerificationCode.PRINCIPAL_MISMATCH
                ) from None
            except (
                VerifiedRecoveryContactLifecycleConflictError,
                VerifiedRecoveryContactPersistenceError,
                VerifiedRecoveryContactRegistryError,
            ):
                raise RecoveryContactVerificationServiceError(
                    RecoveryContactVerificationCode.PERSISTENCE_FAILURE
                ) from None
            except Exception:
                raise RecoveryContactVerificationServiceError(
                    RecoveryContactVerificationCode.TRANSACTION_FAILURE
                ) from None

        try:
            with client.start_session() as session:
                session.with_transaction(callback)
        except RecoveryContactVerificationServiceError:
            raise
        except Exception:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationCode.TRANSACTION_FAILURE
            ) from None

        if "result" not in holder:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationCode.TRANSACTION_FAILURE
            )
        return holder["result"]


__all__ = [
    "RecoveryContactVerificationCode",
    "RecoveryContactVerificationResult",
    "RecoveryContactVerificationService",
    "RecoveryContactVerificationServiceError",
    "VERSION",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_contact_verification_service.py
# VERSION: v1.0.0-R10E21-RECOVERY-CONTACT-VERIFICATION-COMPLETION
# AUTHORITY BOUNDARY: atomic verified recovery-contact enrollment only
# TENANT POSTURE: durable verification supplies exact tenant/principal/address
# FAIL-CLOSED POSTURE: replay, expiry, email drift, mismatch, partial failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
