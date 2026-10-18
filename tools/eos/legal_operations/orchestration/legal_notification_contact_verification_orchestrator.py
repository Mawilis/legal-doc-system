"""Atomic Legal notification-contact verification completion orchestration.

TITLE: WILSY OS Legal Notification Contact Verification Orchestrator
VERSION: v1.0.0-L8-8H7E-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-ORCHESTRATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Consume one exact Legal contact-control verification and establish or
         preserve one ACTIVE Legal notification-contact authority atomically.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_notification_contact_verification_orchestrator.py
COLLABORATION / OWNERSHIP:
    H7A owns verification semantics.
    H7B owns verified Legal notification-contact authority semantics.
    H7C owns durable verification lifecycle.
    H7D owns durable verified-contact lifecycle.
    H7E owns only their atomic caller-transaction composition.
CERTIFICATION / UPDATE DATE: 2026-10-12
SECURITY / PRIVACY POSTURE:
    Raw verification token is transient call data only. Only its lowercase
    SHA3-512 digest is admitted to H7C lookup. Raw address is never accepted or
    persisted here.
TENANT BOUNDARY:
    Caller tenant is only an exact lookup selector. Durable H7A supplies the
    authoritative tenant/principal/channel/address binding.
AUTHORITY BOUNDARY:
    Legal notification-contact verification completion only. No recipient
    selection, IAM grant, HTTP authentication, dispatch, delivery, Court, AI,
    billing, payment, settlement or financial execution authority.
TRANSACTION BOUNDARY:
    Caller supplies one already-active Mongo transaction and owns commit, abort,
    whole-transaction retry and unknown-commit handling. This module never
    starts, commits, aborts, retries or reconciles a transaction.
REPLAY POSTURE:
    Exact consumed-H7A provenance replay returns its durable H7D authority.
    A consumed verification with no provenance may return only the exact ACTIVE
    same tenant/principal/channel/address authority, covering the certified
    same-address no-replacement completion path. All other replay rejects.
ADDRESS-DRIFT POSTURE:
    One differing ACTIVE authority in the exact tenant/principal/channel scope
    is revoked in the same caller transaction before replacement.
SAME-ADDRESS POSTURE:
    Existing ACTIVE authority for the verified address is retained; the H7A
    capability is still atomically consumed and no duplicate H7D row is minted.
FAIL-CLOSED DECLARATION:
    Missing/inactive transaction, malformed token/identity/time, missing or
    invalid verification, multiple ACTIVE authorities, replay divergence,
    corruption, persistence uncertainty or stale races reject.
FINANCIAL AUTHORITY BOUNDARY:
    None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from typing import Any, ClassVar, Final, NoReturn

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactVerification,
    LegalNotificationContactVerificationError,
    LegalNotificationContactVerificationStatus,
)
from tools.eos.legal_operations.domain.legal_verified_notification_contact import (
    VerifiedLegalNotificationContact,
    VerifiedLegalNotificationContactError,
    VerifiedLegalNotificationContactStatus,
)
from tools.eos.legal_operations.registry.legal_notification_contact_verification_registry import (
    LegalNotificationContactVerificationRegistry,
    LegalNotificationContactVerificationRegistryConflictError,
    LegalNotificationContactVerificationRegistryError,
    LegalNotificationContactVerificationRegistryPersistedRecordInvalidError,
    LegalNotificationContactVerificationRegistryPersistenceError,
    LegalNotificationContactVerificationRegistryRetryTransactionError,
    LegalNotificationContactVerificationRegistryTransactionRequiredError,
)
from tools.eos.legal_operations.registry.legal_verified_notification_contact_registry import (
    VerifiedLegalNotificationContactRegistry,
    VerifiedLegalNotificationContactRegistryConflictError,
    VerifiedLegalNotificationContactRegistryError,
    VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
    VerifiedLegalNotificationContactRegistryPersistenceError,
    VerifiedLegalNotificationContactRegistryRetryTransactionError,
    VerifiedLegalNotificationContactRegistryTransactionRequiredError,
)


VERSION: Final[str] = (
    "v1.0.0-L8-8H7E-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-ORCHESTRATION"
)

MAX_TOKEN_LENGTH: Final[int] = 4096


class LegalNotificationContactVerificationOrchestrationError(RuntimeError):
    """Stable code-only H7E orchestration failure."""

    default_code: ClassVar[str] = "L8_8H7E_ORCHESTRATION_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalNotificationContactVerificationOrchestrationRetryRequiredError(
    LegalNotificationContactVerificationOrchestrationError
):
    """Caller must abort and retry the entire transaction from fresh state."""

    default_code: ClassVar[str] = "L8_8H7E_WHOLE_TRANSACTION_RETRY_REQUIRED"


@dataclass(frozen=True, slots=True)
class LegalNotificationContactVerificationResult:
    """Non-sensitive durable result from one H7E completion."""

    contact: VerifiedLegalNotificationContact
    verification: LegalNotificationContactVerification
    authority_created: bool


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = LegalNotificationContactVerificationOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(
    cause: BaseException,
) -> NoReturn:
    raise LegalNotificationContactVerificationOrchestrationRetryRequiredError(
        "L8_8H7E_WHOLE_TRANSACTION_RETRY_REQUIRED"
    ) from cause


def _active_session(session: object) -> object:
    """Require one already-active caller-owned transaction."""

    if session is None:
        _fail("L8_8H7E_ACTIVE_TRANSACTION_REQUIRED")

    marker = getattr(session, "in_transaction", None)

    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False

    if active is not True:
        _fail("L8_8H7E_ACTIVE_TRANSACTION_REQUIRED")

    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str):
        _fail(f"L8_8H7E_{name.upper()}_INVALID")

    if not value or value != value.strip() or len(value) > 256:
        _fail(f"L8_8H7E_{name.upper()}_INVALID")

    return value


def _observed_at(value: object) -> datetime:
    if not isinstance(value, datetime):
        _fail("L8_8H7E_OBSERVED_AT_INVALID")

    if value.tzinfo is None or value.utcoffset() is None:
        _fail("L8_8H7E_OBSERVED_AT_INVALID")

    return value.astimezone(timezone.utc)


def _token_digest(raw_token: object) -> str:
    """Derive lowercase SHA3-512 digest from transient raw verification token."""

    if (
        not isinstance(raw_token, str)
        or not raw_token
        or len(raw_token) > MAX_TOKEN_LENGTH
    ):
        _fail("L8_8H7E_VERIFICATION_TOKEN_INVALID")

    try:
        return hashlib.sha3_512(raw_token.encode("utf-8")).hexdigest()
    except UnicodeEncodeError:
        _fail("L8_8H7E_VERIFICATION_TOKEN_INVALID")


def _active_contacts(
    *,
    verification: LegalNotificationContactVerification,
    registry: VerifiedLegalNotificationContactRegistry,
    session: object,
) -> tuple[VerifiedLegalNotificationContact, ...]:
    try:
        history = registry.list_principal_scope(
            verification.tenant_id,
            verification.principal_id,
            verification.channel,
            session=session,
        )
    except VerifiedLegalNotificationContactRegistryRetryTransactionError as error:
        _retry(error)
    except VerifiedLegalNotificationContactRegistryTransactionRequiredError as error:
        _fail("L8_8H7E_ACTIVE_TRANSACTION_REQUIRED", error)
    except (
        VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
        VerifiedLegalNotificationContactRegistryPersistenceError,
        VerifiedLegalNotificationContactRegistryError,
    ) as error:
        _fail("L8_8H7E_CONTACT_READ_UNAVAILABLE", error)

    active = tuple(
        value
        for value in history
        if value.status is VerifiedLegalNotificationContactStatus.ACTIVE
    )

    if len(active) > 1:
        _fail("L8_8H7E_MULTIPLE_ACTIVE_CONTACTS")

    return active


def _provenance_replay(
    *,
    verification: LegalNotificationContactVerification,
    registry: VerifiedLegalNotificationContactRegistry,
    session: object,
) -> VerifiedLegalNotificationContact | None:
    try:
        value = registry.get_by_verification_fingerprint(
            verification.tenant_id,
            verification.fingerprint,
            session=session,
        )
    except VerifiedLegalNotificationContactRegistryRetryTransactionError as error:
        _retry(error)
    except VerifiedLegalNotificationContactRegistryTransactionRequiredError as error:
        _fail("L8_8H7E_ACTIVE_TRANSACTION_REQUIRED", error)
    except (
        VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
        VerifiedLegalNotificationContactRegistryPersistenceError,
        VerifiedLegalNotificationContactRegistryError,
    ) as error:
        _fail("L8_8H7E_CONTACT_READ_UNAVAILABLE", error)

    if value is None:
        return None

    if (
        value.tenant_id != verification.tenant_id
        or value.principal_id != verification.principal_id
        or value.channel is not verification.channel
        or value.address_digest != verification.address_digest
        or value.verification_id != verification.verification_id
        or value.verification_fingerprint != verification.fingerprint
    ):
        _fail("L8_8H7E_REPLAY_PROVENANCE_INVALID")

    return value


def complete_legal_notification_contact_verification(
    *,
    tenant_id: str,
    contact_id: str,
    verification_token: str,
    observed_at: datetime,
    verification_registry: LegalNotificationContactVerificationRegistry,
    contact_registry: VerifiedLegalNotificationContactRegistry,
    session: object,
) -> LegalNotificationContactVerificationResult:
    """Complete one Legal contact verification inside caller-owned transaction.

    The caller tenant is an exact verification lookup selector only. Durable H7A
    is the authoritative tenant/principal/channel/address source. The supplied
    ``contact_id`` is used only when a new H7D authority must be created.

    This function starts, commits, aborts and retries no transaction.
    """

    tx = _active_session(session)
    tenant = _text("tenant_id", tenant_id)
    identity = _text("contact_id", contact_id)
    observed = _observed_at(observed_at)
    digest = _token_digest(verification_token)

    if not isinstance(
        verification_registry,
        LegalNotificationContactVerificationRegistry,
    ):
        _fail("L8_8H7E_VERIFICATION_REGISTRY_REQUIRED")

    if not isinstance(
        contact_registry,
        VerifiedLegalNotificationContactRegistry,
    ):
        _fail("L8_8H7E_CONTACT_REGISTRY_REQUIRED")

    try:
        verification = verification_registry.get_by_token_digest(
            tenant,
            digest,
            session=tx,
        )
    except LegalNotificationContactVerificationRegistryRetryTransactionError as error:
        _retry(error)
    except LegalNotificationContactVerificationRegistryTransactionRequiredError as error:
        _fail("L8_8H7E_ACTIVE_TRANSACTION_REQUIRED", error)
    except (
        LegalNotificationContactVerificationRegistryPersistedRecordInvalidError,
        LegalNotificationContactVerificationRegistryPersistenceError,
        LegalNotificationContactVerificationRegistryError,
    ) as error:
        _fail("L8_8H7E_VERIFICATION_READ_UNAVAILABLE", error)

    if verification is None:
        _fail("L8_8H7E_VERIFICATION_INVALID")

    if verification.tenant_id != tenant:
        _fail("L8_8H7E_VERIFICATION_SCOPE_INVALID")

    active = _active_contacts(
        verification=verification,
        registry=contact_registry,
        session=tx,
    )
    existing = active[0] if active else None

    if verification.status is LegalNotificationContactVerificationStatus.CONSUMED:
        replay = _provenance_replay(
            verification=verification,
            registry=contact_registry,
            session=tx,
        )

        if replay is not None:
            return LegalNotificationContactVerificationResult(
                contact=replay,
                verification=verification,
                authority_created=False,
            )

        if (
            existing is not None
            and existing.address_digest == verification.address_digest
        ):
            return LegalNotificationContactVerificationResult(
                contact=existing,
                verification=verification,
                authority_created=False,
            )

        _fail("L8_8H7E_VERIFICATION_REPLAY_INVALID")

    if verification.status is not LegalNotificationContactVerificationStatus.ACTIVE:
        _fail("L8_8H7E_VERIFICATION_INVALID")

    try:
        verification.assert_usable_at(observed)
    except LegalNotificationContactVerificationError as error:
        _fail("L8_8H7E_VERIFICATION_INVALID", error)

    same_address = (
        existing is not None
        and existing.address_digest == verification.address_digest
    )

    if existing is not None and not same_address:
        try:
            contact_registry.revoke(
                existing,
                observed,
                session=tx,
            )
        except VerifiedLegalNotificationContactRegistryRetryTransactionError as error:
            _retry(error)
        except VerifiedLegalNotificationContactRegistryTransactionRequiredError as error:
            _fail("L8_8H7E_ACTIVE_TRANSACTION_REQUIRED", error)
        except VerifiedLegalNotificationContactRegistryConflictError as error:
            _fail("L8_8H7E_CONTACT_REPLACEMENT_CONFLICT", error)
        except (
            VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
            VerifiedLegalNotificationContactRegistryPersistenceError,
            VerifiedLegalNotificationContactRegistryError,
        ) as error:
            _fail("L8_8H7E_CONTACT_REPLACEMENT_FAILED", error)

    try:
        consumed = verification_registry.consume(
            verification,
            observed,
            session=tx,
        )
    except LegalNotificationContactVerificationRegistryRetryTransactionError as error:
        _retry(error)
    except LegalNotificationContactVerificationRegistryTransactionRequiredError as error:
        _fail("L8_8H7E_ACTIVE_TRANSACTION_REQUIRED", error)
    except LegalNotificationContactVerificationRegistryConflictError as error:
        _fail("L8_8H7E_VERIFICATION_CONSUME_CONFLICT", error)
    except (
        LegalNotificationContactVerificationRegistryPersistedRecordInvalidError,
        LegalNotificationContactVerificationRegistryPersistenceError,
        LegalNotificationContactVerificationRegistryError,
    ) as error:
        _fail("L8_8H7E_VERIFICATION_CONSUME_FAILED", error)

    if (
        consumed.status is not LegalNotificationContactVerificationStatus.CONSUMED
        or consumed.tenant_id != verification.tenant_id
        or consumed.principal_id != verification.principal_id
        or consumed.channel is not verification.channel
        or consumed.address_digest != verification.address_digest
    ):
        _fail("L8_8H7E_CONSUMED_VERIFICATION_INVALID")

    if same_address:
        assert existing is not None

        return LegalNotificationContactVerificationResult(
            contact=existing,
            verification=consumed,
            authority_created=False,
        )

    try:
        contact = VerifiedLegalNotificationContact.from_consumed_verification(
            contact_id=identity,
            verification=consumed,
            verified_at=observed,
        )
    except VerifiedLegalNotificationContactError as error:
        _fail("L8_8H7E_CONTACT_ELEVATION_INVALID", error)

    try:
        persisted = contact_registry.create(
            contact,
            session=tx,
        )
    except VerifiedLegalNotificationContactRegistryRetryTransactionError as error:
        _retry(error)
    except VerifiedLegalNotificationContactRegistryTransactionRequiredError as error:
        _fail("L8_8H7E_ACTIVE_TRANSACTION_REQUIRED", error)
    except VerifiedLegalNotificationContactRegistryConflictError as error:
        _fail("L8_8H7E_CONTACT_CREATE_CONFLICT", error)
    except (
        VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
        VerifiedLegalNotificationContactRegistryPersistenceError,
        VerifiedLegalNotificationContactRegistryError,
    ) as error:
        _fail("L8_8H7E_CONTACT_CREATE_FAILED", error)

    if (
        persisted.tenant_id != consumed.tenant_id
        or persisted.contact_id != identity
        or persisted.principal_id != consumed.principal_id
        or persisted.channel is not consumed.channel
        or persisted.address_digest != consumed.address_digest
        or persisted.verification_id != consumed.verification_id
        or persisted.verification_fingerprint != consumed.fingerprint
        or persisted.status is not VerifiedLegalNotificationContactStatus.ACTIVE
    ):
        _fail("L8_8H7E_CONTACT_CORRELATION_INVALID")

    return LegalNotificationContactVerificationResult(
        contact=persisted,
        verification=consumed,
        authority_created=True,
    )


__all__ = [
    "MAX_TOKEN_LENGTH",
    "VERSION",
    "LegalNotificationContactVerificationOrchestrationError",
    "LegalNotificationContactVerificationOrchestrationRetryRequiredError",
    "LegalNotificationContactVerificationResult",
    "complete_legal_notification_contact_verification",
]


# ARTIFACT: legal_notification_contact_verification_orchestrator.py
# VERSION: v1.0.0-L8-8H7E-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-ORCHESTRATION
# AUTHORITY BOUNDARY: atomic H7A/H7B/H7C/H7D Legal contact completion only
# TENANT POSTURE: caller tenant selector plus exact durable H7A authority binding
# TRANSACTION POSTURE: caller owns active transaction, commit, abort and retry
# SAME-ADDRESS POSTURE: consume verification, retain existing ACTIVE authority
# ADDRESS-DRIFT POSTURE: revoke prior ACTIVE authority before same-tx replacement
# RAW TOKEN POSTURE: transient only; lookup uses lowercase SHA3-512 digest
# DISPATCH / DELIVERY AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
