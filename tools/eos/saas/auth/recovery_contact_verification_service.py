"""Authenticated recovery-contact enrollment and verification orchestration.

TITLE: WILSY OS Recovery Contact Verification Service
VERSION: v1.0.0-R10E14-RECOVERY-CONTACT-VERIFICATION-SERVICE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Lets one already-authenticated ACTIVE principal prove possession of an
         explicit recovery email before that address can authorize password
         recovery delivery.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/recovery_contact_verification_service.py
COLLABORATION / OWNERSHIP: PrincipalAuthorityRepository owns current principal
                           lifecycle; RecoveryContactAuthorityRegistry owns
                           recovery-contact truth; RecoveryContactVerificationRegistry
                           owns digest-only challenge evidence; an injected delivery
                           adapter owns email transport capability only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E14-RECOVERY-CONTACT-VERIFICATION-SERVICE — Establishes authenticated
    recovery-contact enrollment, 15-minute SHA3-512 digest-only possession
    challenges, transactional challenge supersession, post-commit delivery,
    delivery-failure compensation, and atomic challenge-consume/contact-verify
    completion without trusting JWT email metadata.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw verification bearers are transient call-stack
                            values only; they are never persisted, logged,
                            returned, or retained on the service object.
TENANT BOUNDARY: Caller tenant_id/principal_id must already come from authenticated
                 server identity and are revalidated against current ACTIVE
                 PrincipalAuthority before any recovery-contact transition.
AUTHORITY BOUNDARY: Recovery-contact verification ceremony orchestration only;
                    no password, recovery capability, login, MFA, role, membership,
                    session, refresh, JWT, or tenant-grant authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: This service owns Mongo ClientSession/with_transaction for
                      contact/challenge composition; registries receive and
                      propagate the caller-owned session unchanged.
FAIL-CLOSED POSTURE: Inactive principals, verified-contact replacement attempts,
                     corrupt/stale persistence, replayed/expired challenges,
                     transaction failures, and delivery failures never create
                     VERIFIED recovery-contact authority.
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

from .recovery_contact import (
    RecoveryContactAuthority,
    RecoveryContactStatus,
    RecoveryContactVerificationMethod,
)
from .recovery_contact_registry import (
    RecoveryContactAlreadyExistsError,
    RecoveryContactAuthorityRegistry,
    RecoveryContactLifecycleConflictError,
    RecoveryContactPersistedRecordInvalidError,
    RecoveryContactPersistenceError,
    RecoveryContactRegistryError,
)
from .recovery_contact_verification import (
    RecoveryContactVerificationChallenge,
    RecoveryContactVerificationStatus,
)
from .recovery_contact_verification_registry import (
    RecoveryContactVerificationAlreadyExistsError,
    RecoveryContactVerificationLifecycleConflictError,
    RecoveryContactVerificationPersistedRecordInvalidError,
    RecoveryContactVerificationPersistenceError,
    RecoveryContactVerificationRegistry,
    RecoveryContactVerificationRegistryError,
)


VERSION: Final[str] = "v1.0.0-R10E14-RECOVERY-CONTACT-VERIFICATION-SERVICE"
VERIFICATION_TTL: Final[timedelta] = timedelta(minutes=15)
VERIFICATION_TOKEN_BYTES: Final[int] = 32
CONTACT_ID_PREFIX: Final[str] = "WILSYRECOVERYCONTACT-"
CHALLENGE_ID_PREFIX: Final[str] = "WILSYRECOVERYVERIFY-"


class RecoveryContactVerificationServiceCode(StrEnum):
    """Stable non-secret operational failure classes."""

    INVALID_REQUEST = "RECOVERY_CONTACT_VERIFICATION_REQUEST_INVALID"
    PRINCIPAL_UNAVAILABLE = "RECOVERY_CONTACT_VERIFICATION_PRINCIPAL_UNAVAILABLE"
    REPLACEMENT_FORBIDDEN = "RECOVERY_CONTACT_VERIFIED_REPLACEMENT_FORBIDDEN"
    CHALLENGE_INVALID = "RECOVERY_CONTACT_VERIFICATION_CHALLENGE_INVALID"
    PERSISTENCE_FAILURE = "RECOVERY_CONTACT_VERIFICATION_PERSISTENCE_FAILURE"
    TRANSACTION_FAILURE = "RECOVERY_CONTACT_VERIFICATION_TRANSACTION_FAILURE"
    DELIVERY_FAILURE = "RECOVERY_CONTACT_VERIFICATION_DELIVERY_FAILURE"


class RecoveryContactVerificationServiceError(RuntimeError):
    """Code-only service failure that retains no email or verification bearer."""

    def __init__(self, code: RecoveryContactVerificationServiceCode) -> None:
        if not isinstance(code, RecoveryContactVerificationServiceCode):
            raise TypeError("recovery contact verification service code is invalid")
        self.code = code
        super().__init__(code.value)

    def __repr__(self) -> str:
        return f"RecoveryContactVerificationServiceError(code={self.code.value!r})"


@dataclass(frozen=True, slots=True)
class RecoveryContactVerificationRequestResult:
    """Bounded initiation result for one authenticated principal."""

    status: str


@dataclass(frozen=True, slots=True)
class RecoveryContactVerificationCompletionResult:
    """Bounded successful verification result with no address or secret projection."""

    status: str = "RECOVERY_CONTACT_VERIFIED"


class RecoveryContactVerificationDelivery(Protocol):
    """Transport-only port for an already-issued email-possession challenge."""

    def deliver_recovery_contact_verification(
        self,
        *,
        recipient_email: str,
        verification_token: str,
        expires_at: datetime,
    ) -> None: ...


class _PrincipalAuthority(Protocol):
    @staticmethod
    def get(principal_id: str, *, session: Any | None = None) -> Any: ...


class _ContactRegistry(Protocol):
    def get_current_for_principal(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        session: Any | None = None,
        **kwargs: Any,
    ) -> RecoveryContactAuthority | None: ...

    def get_by_contact_id(
        self,
        *,
        tenant_id: str,
        contact_id: str,
        session: Any | None = None,
    ) -> RecoveryContactAuthority | None: ...

    def create_pending(
        self,
        contact: RecoveryContactAuthority,
        *,
        session: Any | None = None,
    ) -> RecoveryContactAuthority: ...

    def verify(
        self,
        contact: RecoveryContactAuthority,
        *,
        verified_at: datetime,
        method: RecoveryContactVerificationMethod,
        session: Any | None = None,
    ) -> RecoveryContactAuthority: ...

    def revoke(
        self,
        contact: RecoveryContactAuthority,
        *,
        revoked_at: datetime,
        session: Any | None = None,
    ) -> RecoveryContactAuthority: ...


class _ChallengeRegistry(Protocol):
    def list_active_for_contact(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        contact_id: str,
        session: Any | None = None,
    ) -> tuple[RecoveryContactVerificationChallenge, ...]: ...

    def get_by_token_digest(
        self,
        *,
        tenant_id: str,
        token_digest: str,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge | None: ...

    def create(
        self,
        challenge: RecoveryContactVerificationChallenge,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge: ...

    def consume(
        self,
        challenge: RecoveryContactVerificationChallenge,
        consumed_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge: ...

    def expire(
        self,
        challenge: RecoveryContactVerificationChallenge,
        expired_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge: ...

    def revoke(
        self,
        challenge: RecoveryContactVerificationChallenge,
        revoked_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge: ...


class _MongoClient(Protocol):
    def start_session(self) -> Any: ...


def _identifier(value: object) -> str:
    if not isinstance(value, str):
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationServiceCode.INVALID_REQUEST
        )
    candidate = value.strip()
    if (
        not candidate
        or candidate != value
        or len(candidate) > 256
        or any(ord(character) < 32 or ord(character) == 127 for character in candidate)
    ):
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationServiceCode.INVALID_REQUEST
        )
    return candidate


def _email(value: object) -> str:
    if not isinstance(value, str):
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationServiceCode.INVALID_REQUEST
        )
    candidate = value.strip().lower()
    if (
        not candidate
        or len(candidate) > 320
        or candidate.count("@") != 1
        or any(character.isspace() for character in candidate)
    ):
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationServiceCode.INVALID_REQUEST
        )
    local, domain = candidate.split("@", 1)
    if not local or not domain or "." not in domain:
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationServiceCode.INVALID_REQUEST
        )
    return candidate


def _verification_token(value: object) -> str:
    if not isinstance(value, str) or len(value) < 32 or len(value) > 4096:
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationServiceCode.INVALID_REQUEST
        )
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationServiceCode.INVALID_REQUEST
        )
    return value


def _digest(value: str) -> str:
    return hashlib.sha3_512(value.encode("utf-8")).hexdigest()


def _utc_observation(clock: Callable[[], datetime]) -> datetime:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise RecoveryContactVerificationServiceError(
            RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE
        )
    return value.astimezone(timezone.utc)


class RecoveryContactVerificationService:
    """Own the authenticated email-possession ceremony for recovery contacts.

    Initiation may create a new PENDING contact or reuse the same PENDING address.
    A different PENDING address replaces the unverified contact transactionally.
    An existing VERIFIED contact is never silently replaced: same-address requests
    return bounded already-verified status, while a different address fails closed.

    Completion hashes the caller bearer, tenant-scopes the challenge read, rechecks
    current ACTIVE principal authority, then consumes the challenge and promotes
    the exact matching PENDING contact to VERIFIED in one Mongo transaction.
    """

    def __init__(
        self,
        *,
        delivery: RecoveryContactVerificationDelivery,
        client: _MongoClient | None = None,
        principal_repository: _PrincipalAuthority | None = None,
        contact_registry: _ContactRegistry | None = None,
        challenge_registry: _ChallengeRegistry | None = None,
        clock: Callable[[], datetime] | None = None,
        token_factory: Callable[[], str] | None = None,
        contact_id_factory: Callable[[], str] | None = None,
        challenge_id_factory: Callable[[], str] | None = None,
    ) -> None:
        """Bind dependencies without opening persistence or retaining secrets."""

        if delivery is None:
            raise TypeError("recovery contact verification delivery is required")
        self._delivery = delivery
        self._client = client
        self._principal_repository = principal_repository
        self._contact_registry = contact_registry
        self._challenge_registry = challenge_registry
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._token_factory = token_factory or (
            lambda: secrets.token_urlsafe(VERIFICATION_TOKEN_BYTES)
        )
        self._contact_id_factory = contact_id_factory or (
            lambda: f"{CONTACT_ID_PREFIX}{uuid.uuid4()}"
        )
        self._challenge_id_factory = challenge_id_factory or (
            lambda: f"{CHALLENGE_ID_PREFIX}{uuid.uuid4()}"
        )

    def _client_or_fail(self) -> _MongoClient:
        client = self._client if self._client is not None else kernel_db.get_client()
        if client is None:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PERSISTENCE_FAILURE
            )
        return client

    def _principal_or_default(self) -> _PrincipalAuthority:
        return self._principal_repository or PrincipalAuthorityRepository

    def _contacts_or_default(self) -> _ContactRegistry:
        return self._contact_registry or RecoveryContactAuthorityRegistry()

    def _challenges_or_default(self) -> _ChallengeRegistry:
        return self._challenge_registry or RecoveryContactVerificationRegistry()

    def _require_active_principal(
        self,
        tenant_id: str,
        principal_id: str,
        *,
        session: Any | None = None,
    ) -> None:
        """Require exact current ACTIVE principal lifecycle authority."""

        try:
            authority = self._principal_or_default().get(principal_id, session=session)
        except PrincipalAuthorityNotFoundError as error:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE
            ) from error
        except PrincipalAuthorityRepositoryError as error:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE
            ) from error
        if (
            getattr(authority, "principal_id", None) != principal_id
            or getattr(authority, "status", None) is not PrincipalStatus.ACTIVE
        ):
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE
            )
        authority_tenant = getattr(authority, "tenant_id", None)
        if authority_tenant is not None and authority_tenant != tenant_id:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE
            )

    @staticmethod
    def _retire_active_challenges(
        registry: _ChallengeRegistry,
        challenges: tuple[RecoveryContactVerificationChallenge, ...],
        observed: datetime,
        *,
        session: Any,
    ) -> None:
        """Expire elapsed challenges and revoke still-live challenges."""

        for challenge in challenges:
            if observed >= challenge.expires_at:
                registry.expire(challenge, observed, session=session)
            else:
                registry.revoke(challenge, observed, session=session)

    def _compensate_delivery_failure(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        contact_id: str,
        token_digest: str,
        revoke_contact: bool,
    ) -> None:
        """Best-effort transactionally revoke undelivered challenge authority."""

        contacts = self._contacts_or_default()
        challenges = self._challenges_or_default()
        client = self._client_or_fail()

        def callback(session: Any) -> None:
            observed = _utc_observation(self._clock)
            challenge = challenges.get_by_token_digest(
                tenant_id=tenant_id,
                token_digest=token_digest,
                session=session,
            )
            if (
                challenge is not None
                and challenge.principal_id == principal_id
                and challenge.contact_id == contact_id
                and challenge.status is RecoveryContactVerificationStatus.ACTIVE
            ):
                if observed >= challenge.expires_at:
                    challenges.expire(challenge, observed, session=session)
                else:
                    challenges.revoke(challenge, observed, session=session)
            if revoke_contact:
                contact = contacts.get_by_contact_id(
                    tenant_id=tenant_id,
                    contact_id=contact_id,
                    session=session,
                )
                if (
                    contact is not None
                    and contact.principal_id == principal_id
                    and contact.status is RecoveryContactStatus.PENDING
                ):
                    contacts.revoke(contact, revoked_at=observed, session=session)

        try:
            with client.start_session() as session:
                session.with_transaction(callback)
        except Exception:
            log_auth_event(
                "RECOVERY_CONTACT_VERIFICATION_DELIVERY_COMPENSATION",
                principal_id,
                False,
                {"reason": "compensation_failed"},
            )

    def request_verification(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        address: str,
    ) -> RecoveryContactVerificationRequestResult:
        """Create or refresh one PENDING recovery-contact possession challenge.

        The method never trusts identity email metadata. The proposed address is
        explicit input from an authenticated principal and remains PENDING until
        the separately delivered challenge is consumed successfully.
        """

        tenant = _identifier(tenant_id)
        principal = _identifier(principal_id)
        recipient = _email(address)
        self._require_active_principal(tenant, principal)

        contacts = self._contacts_or_default()
        challenges = self._challenges_or_default()
        client = self._client_or_fail()

        raw_token = self._token_factory()
        contact_id = self._contact_id_factory()
        challenge_id = self._challenge_id_factory()
        if not isinstance(raw_token, str) or len(raw_token) < 32:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE
            )
        if not isinstance(contact_id, str) or not contact_id.strip():
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE
            )
        if not isinstance(challenge_id, str) or not challenge_id.strip():
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE
            )
        token_digest = _digest(raw_token)

        holder: dict[str, Any] = {}

        def callback(session: Any) -> None:
            self._require_active_principal(tenant, principal, session=session)
            observed = _utc_observation(self._clock)
            current = contacts.get_current_for_principal(
                tenant_id=tenant,
                principal_id=principal,
                session=session,
            )

            if current is not None and current.status is RecoveryContactStatus.VERIFIED:
                if current.address == recipient:
                    holder["already_verified"] = True
                    return
                raise RecoveryContactVerificationServiceError(
                    RecoveryContactVerificationServiceCode.REPLACEMENT_FORBIDDEN
                )

            contact = current
            created_new = False
            if contact is not None:
                active = challenges.list_active_for_contact(
                    tenant_id=tenant,
                    principal_id=principal,
                    contact_id=contact.contact_id,
                    session=session,
                )
                self._retire_active_challenges(
                    challenges, active, observed, session=session
                )
                if contact.address != recipient:
                    contacts.revoke(contact, revoked_at=observed, session=session)
                    contact = None

            if contact is None:
                contact = RecoveryContactAuthority.pending(
                    contact_id=contact_id,
                    tenant_id=tenant,
                    principal_id=principal,
                    address=recipient,
                    created_at=observed,
                )
                contacts.create_pending(contact, session=session)
                created_new = True

            challenge = RecoveryContactVerificationChallenge.issue(
                challenge_id=challenge_id,
                tenant_id=tenant,
                principal_id=principal,
                contact_id=contact.contact_id,
                address=contact.address,
                token_digest=token_digest,
                issued_at=observed,
                expires_at=observed + VERIFICATION_TTL,
            )
            challenges.create(challenge, session=session)
            holder["contact"] = contact
            holder["challenge"] = challenge
            holder["created_new"] = created_new

        try:
            with client.start_session() as session:
                session.with_transaction(callback)
        except RecoveryContactVerificationServiceError:
            raise
        except (
            RecoveryContactAlreadyExistsError,
            RecoveryContactLifecycleConflictError,
            RecoveryContactPersistedRecordInvalidError,
            RecoveryContactPersistenceError,
            RecoveryContactRegistryError,
            RecoveryContactVerificationAlreadyExistsError,
            RecoveryContactVerificationLifecycleConflictError,
            RecoveryContactVerificationPersistedRecordInvalidError,
            RecoveryContactVerificationPersistenceError,
            RecoveryContactVerificationRegistryError,
        ) as error:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PERSISTENCE_FAILURE
            ) from error
        except Exception as error:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.TRANSACTION_FAILURE
            ) from error

        if holder.get("already_verified") is True:
            return RecoveryContactVerificationRequestResult(
                status="RECOVERY_CONTACT_ALREADY_VERIFIED"
            )

        contact = holder.get("contact")
        challenge = holder.get("challenge")
        if not isinstance(contact, RecoveryContactAuthority) or not isinstance(
            challenge, RecoveryContactVerificationChallenge
        ):
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.TRANSACTION_FAILURE
            )

        try:
            self._delivery.deliver_recovery_contact_verification(
                recipient_email=contact.address,
                verification_token=raw_token,
                expires_at=challenge.expires_at,
            )
        except Exception:
            self._compensate_delivery_failure(
                tenant_id=tenant,
                principal_id=principal,
                contact_id=contact.contact_id,
                token_digest=challenge.token_digest,
                revoke_contact=bool(holder.get("created_new")),
            )
            log_auth_event(
                "RECOVERY_CONTACT_VERIFICATION_DELIVERY",
                principal,
                False,
                {"reason": "delivery_failed"},
            )
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.DELIVERY_FAILURE
            ) from None

        log_auth_event(
            "RECOVERY_CONTACT_VERIFICATION_DELIVERY",
            principal,
            True,
            {"expires_in_seconds": int(VERIFICATION_TTL.total_seconds())},
        )
        return RecoveryContactVerificationRequestResult(
            status="RECOVERY_CONTACT_VERIFICATION_SENT"
        )

    def complete_verification(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        verification_token: str,
    ) -> RecoveryContactVerificationCompletionResult:
        """Consume one challenge and atomically promote its PENDING contact.

        The raw bearer is hashed immediately and never persisted. Tenant and
        principal are authenticated server inputs, not values derived from the
        challenge or browser-supplied contact metadata.
        """

        tenant = _identifier(tenant_id)
        principal = _identifier(principal_id)
        raw_token = _verification_token(verification_token)
        token_digest = _digest(raw_token)

        contacts = self._contacts_or_default()
        challenges = self._challenges_or_default()
        client = self._client_or_fail()
        holder: dict[str, Any] = {}

        def callback(session: Any) -> None:
            self._require_active_principal(tenant, principal, session=session)
            observed = _utc_observation(self._clock)
            challenge = challenges.get_by_token_digest(
                tenant_id=tenant,
                token_digest=token_digest,
                session=session,
            )
            if (
                challenge is None
                or challenge.principal_id != principal
                or challenge.status is not RecoveryContactVerificationStatus.ACTIVE
            ):
                holder["invalid"] = True
                return
            if observed >= challenge.expires_at:
                challenges.expire(challenge, observed, session=session)
                holder["invalid"] = True
                return

            contact = contacts.get_by_contact_id(
                tenant_id=tenant,
                contact_id=challenge.contact_id,
                session=session,
            )
            if (
                contact is None
                or contact.principal_id != principal
                or contact.address != challenge.address
                or contact.status is not RecoveryContactStatus.PENDING
            ):
                holder["invalid"] = True
                return

            challenges.consume(challenge, observed, session=session)
            verified = contacts.verify(
                contact,
                verified_at=observed,
                method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
                session=session,
            )
            holder["verified"] = verified

        try:
            with client.start_session() as session:
                session.with_transaction(callback)
        except RecoveryContactVerificationServiceError:
            raise
        except (
            RecoveryContactLifecycleConflictError,
            RecoveryContactPersistedRecordInvalidError,
            RecoveryContactPersistenceError,
            RecoveryContactRegistryError,
            RecoveryContactVerificationLifecycleConflictError,
            RecoveryContactVerificationPersistedRecordInvalidError,
            RecoveryContactVerificationPersistenceError,
            RecoveryContactVerificationRegistryError,
        ) as error:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.PERSISTENCE_FAILURE
            ) from error
        except Exception as error:
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.TRANSACTION_FAILURE
            ) from error

        if holder.get("invalid") is True or not isinstance(
            holder.get("verified"), RecoveryContactAuthority
        ):
            raise RecoveryContactVerificationServiceError(
                RecoveryContactVerificationServiceCode.CHALLENGE_INVALID
            )

        log_auth_event(
            "RECOVERY_CONTACT_VERIFIED",
            principal,
            True,
            {"method": RecoveryContactVerificationMethod.EMAIL_CHALLENGE.value},
        )
        return RecoveryContactVerificationCompletionResult()


__all__ = [
    "CHALLENGE_ID_PREFIX",
    "CONTACT_ID_PREFIX",
    "RecoveryContactVerificationCompletionResult",
    "RecoveryContactVerificationDelivery",
    "RecoveryContactVerificationRequestResult",
    "RecoveryContactVerificationService",
    "RecoveryContactVerificationServiceCode",
    "RecoveryContactVerificationServiceError",
    "VERIFICATION_TTL",
    "VERSION",
]


# ARTIFACT: tools/eos/saas/auth/recovery_contact_verification_service.py
# VERSION: v1.0.0-R10E14-RECOVERY-CONTACT-VERIFICATION-SERVICE
# AUTHORITY BOUNDARY: authenticated recovery-contact possession-verification orchestration only
# TENANT POSTURE: exact authenticated tenant/principal binding; identity email metadata grants no recovery authority
# FAIL-CLOSED POSTURE: inactive, stale, replayed, expired, replacement, transaction, and delivery failures never verify contact
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
