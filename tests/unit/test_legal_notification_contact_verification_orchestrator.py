"""Direct unit certificate for H7E Legal notification-contact completion."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha3_512
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactChannel,
    LegalNotificationContactVerification,
    LegalNotificationContactVerificationStatus,
)
from tools.eos.legal_operations.domain.legal_verified_notification_contact import (
    VerifiedLegalNotificationContact,
    VerifiedLegalNotificationContactStatus,
)
from tools.eos.legal_operations.orchestration.legal_notification_contact_verification_orchestrator import (
    LegalNotificationContactVerificationOrchestrationError,
    LegalNotificationContactVerificationOrchestrationRetryRequiredError,
    complete_legal_notification_contact_verification,
)
from tools.eos.legal_operations.registry.legal_notification_contact_verification_registry import (
    LegalNotificationContactVerificationRegistry,
    LegalNotificationContactVerificationRegistryRetryTransactionError,
)
from tools.eos.legal_operations.registry.legal_verified_notification_contact_registry import (
    VerifiedLegalNotificationContactRegistry,
    VerifiedLegalNotificationContactRegistryRetryTransactionError,
)


NOW = datetime(2026, 10, 12, 18, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-legal-a"
PRINCIPAL = "principal-legal-a"
TOKEN = "legal-contact-verification-token"
TOKEN_DIGEST = sha3_512(TOKEN.encode("utf-8")).hexdigest()
ADDRESS_A = sha3_512(b"legal-a@example.invalid").hexdigest()
ADDRESS_B = sha3_512(b"legal-b@example.invalid").hexdigest()


class _Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


def _verification(
    *,
    verification_id: str = "legal-verification-1",
    address_digest: str = ADDRESS_A,
) -> LegalNotificationContactVerification:
    return LegalNotificationContactVerification.issue(
        tenant_id=TENANT,
        verification_id=verification_id,
        principal_id=PRINCIPAL,
        channel=LegalNotificationContactChannel.EMAIL,
        address_digest=address_digest,
        token_digest=TOKEN_DIGEST,
        issued_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )


def _contact_from(
    verification: LegalNotificationContactVerification,
    *,
    contact_id: str,
) -> VerifiedLegalNotificationContact:
    consumed = verification.consume(NOW + timedelta(seconds=1))
    return VerifiedLegalNotificationContact.from_consumed_verification(
        contact_id=contact_id,
        verification=consumed,
        verified_at=NOW + timedelta(seconds=1),
    )


class _VerificationRegistryStub(LegalNotificationContactVerificationRegistry):
    def __init__(
        self,
        value: LegalNotificationContactVerification | None,
        *,
        retry_on_read: bool = False,
        retry_on_consume: bool = False,
    ) -> None:
        self.value = value
        self.retry_on_read = retry_on_read
        self.retry_on_consume = retry_on_consume
        self.reads: list[tuple[str, str, object]] = []
        self.consumes: list[
            tuple[LegalNotificationContactVerification, datetime, object]
        ] = []

    def get_by_token_digest(
        self,
        tenant_id: str,
        token_digest: str,
        *,
        session: object,
    ) -> LegalNotificationContactVerification | None:
        self.reads.append((tenant_id, token_digest, session))
        if self.retry_on_read:
            raise LegalNotificationContactVerificationRegistryRetryTransactionError(
                "L8_8H7C_DUPLICATE_RACE_RETRY_TRANSACTION"
            )
        return self.value

    def consume(
        self,
        source: LegalNotificationContactVerification,
        consumed_at: datetime,
        *,
        session: object,
    ) -> LegalNotificationContactVerification:
        self.consumes.append((source, consumed_at, session))
        if self.retry_on_consume:
            raise LegalNotificationContactVerificationRegistryRetryTransactionError(
                "L8_8H7C_TRANSITION_RACE_RETRY_TRANSACTION"
            )
        consumed = source.consume(consumed_at)
        self.value = consumed
        return consumed


class _ContactRegistryStub(VerifiedLegalNotificationContactRegistry):
    def __init__(
        self,
        history: tuple[VerifiedLegalNotificationContact, ...] = (),
        *,
        provenance: VerifiedLegalNotificationContact | None = None,
        retry_on_create: bool = False,
        retry_on_revoke: bool = False,
    ) -> None:
        self.history = history
        self.provenance = provenance
        self.retry_on_create = retry_on_create
        self.retry_on_revoke = retry_on_revoke
        self.history_reads: list[tuple[str, str, object, object]] = []
        self.provenance_reads: list[tuple[str, str, object]] = []
        self.created: list[tuple[VerifiedLegalNotificationContact, object]] = []
        self.revoked: list[
            tuple[VerifiedLegalNotificationContact, datetime, object]
        ] = []

    def list_principal_scope(
        self,
        tenant_id: str,
        principal_id: str,
        channel: LegalNotificationContactChannel | str,
        *,
        session: object,
    ) -> tuple[VerifiedLegalNotificationContact, ...]:
        self.history_reads.append((tenant_id, principal_id, channel, session))
        return self.history

    def get_by_verification_fingerprint(
        self,
        tenant_id: str,
        verification_fingerprint: str,
        *,
        session: object,
    ) -> VerifiedLegalNotificationContact | None:
        self.provenance_reads.append(
            (tenant_id, verification_fingerprint, session)
        )
        return self.provenance

    def revoke(
        self,
        source: VerifiedLegalNotificationContact,
        revoked_at: object,
        *,
        session: object,
    ) -> VerifiedLegalNotificationContact:
        if self.retry_on_revoke:
            raise VerifiedLegalNotificationContactRegistryRetryTransactionError(
                "L8_8H7D_REVOKE_RACE_RETRY_TRANSACTION"
            )
        assert isinstance(revoked_at, datetime)
        self.revoked.append((source, revoked_at, session))
        replacement = source.revoke(revoked_at)
        self.history = tuple(
            replacement if item.contact_id == source.contact_id else item
            for item in self.history
        )
        return replacement

    def create(
        self,
        value: VerifiedLegalNotificationContact,
        *,
        session: object,
    ) -> VerifiedLegalNotificationContact:
        if self.retry_on_create:
            raise VerifiedLegalNotificationContactRegistryRetryTransactionError(
                "L8_8H7D_DUPLICATE_RACE_RETRY_TRANSACTION"
            )
        self.created.append((value, session))
        self.history = (*self.history, value)
        return value


def test_requires_already_active_caller_transaction() -> None:
    verification = _verification()
    vr = _VerificationRegistryStub(verification)
    cr = _ContactRegistryStub()

    with pytest.raises(
        LegalNotificationContactVerificationOrchestrationError
    ) as captured:
        complete_legal_notification_contact_verification(
            tenant_id=TENANT,
            contact_id="legal-contact-1",
            verification_token=TOKEN,
            observed_at=NOW + timedelta(seconds=1),
            verification_registry=vr,
            contact_registry=cr,
            session=_Session(False),
        )

    assert captured.value.code == "L8_8H7E_ACTIVE_TRANSACTION_REQUIRED"
    assert vr.reads == []
    assert cr.history_reads == []


def test_fresh_verification_creates_authority_and_consumes_h7a() -> None:
    verification = _verification()
    session = _Session()
    vr = _VerificationRegistryStub(verification)
    cr = _ContactRegistryStub()
    observed = NOW + timedelta(seconds=1)

    result = complete_legal_notification_contact_verification(
        tenant_id=TENANT,
        contact_id="legal-contact-1",
        verification_token=TOKEN,
        observed_at=observed,
        verification_registry=vr,
        contact_registry=cr,
        session=session,
    )

    assert vr.reads == [(TENANT, TOKEN_DIGEST, session)]
    assert len(vr.consumes) == 1
    assert len(cr.created) == 1
    assert cr.revoked == []
    assert result.authority_created is True
    assert result.verification.status is LegalNotificationContactVerificationStatus.CONSUMED
    assert result.contact.status is VerifiedLegalNotificationContactStatus.ACTIVE
    assert result.contact.contact_id == "legal-contact-1"
    assert result.contact.address_digest == ADDRESS_A
    assert result.contact.verification_fingerprint == result.verification.fingerprint


def test_same_address_retains_existing_authority_but_consumes_verification() -> None:
    verification = _verification(verification_id="legal-verification-2")
    prior_verification = _verification(verification_id="legal-verification-prior")
    existing = _contact_from(
        prior_verification,
        contact_id="legal-contact-existing",
    )
    session = _Session()
    vr = _VerificationRegistryStub(verification)
    cr = _ContactRegistryStub((existing,))

    result = complete_legal_notification_contact_verification(
        tenant_id=TENANT,
        contact_id="legal-contact-unused",
        verification_token=TOKEN,
        observed_at=NOW + timedelta(seconds=2),
        verification_registry=vr,
        contact_registry=cr,
        session=session,
    )

    assert len(vr.consumes) == 1
    assert cr.revoked == []
    assert cr.created == []
    assert result.authority_created is False
    assert result.contact == existing
    assert result.verification.status is LegalNotificationContactVerificationStatus.CONSUMED


def test_address_drift_revokes_old_authority_and_creates_replacement() -> None:
    verification = _verification(
        verification_id="legal-verification-new",
        address_digest=ADDRESS_B,
    )
    prior_verification = _verification(
        verification_id="legal-verification-old",
        address_digest=ADDRESS_A,
    )
    existing = _contact_from(
        prior_verification,
        contact_id="legal-contact-old",
    )
    session = _Session()
    vr = _VerificationRegistryStub(verification)
    cr = _ContactRegistryStub((existing,))
    observed = NOW + timedelta(seconds=2)

    result = complete_legal_notification_contact_verification(
        tenant_id=TENANT,
        contact_id="legal-contact-new",
        verification_token=TOKEN,
        observed_at=observed,
        verification_registry=vr,
        contact_registry=cr,
        session=session,
    )

    assert len(cr.revoked) == 1
    assert cr.revoked[0][0] == existing
    assert len(vr.consumes) == 1
    assert len(cr.created) == 1
    assert result.authority_created is True
    assert result.contact.contact_id == "legal-contact-new"
    assert result.contact.address_digest == ADDRESS_B


def test_consumed_verification_exact_provenance_replays_without_mutation() -> None:
    source = _verification(verification_id="legal-verification-replay")
    consumed = source.consume(NOW + timedelta(seconds=1))
    contact = VerifiedLegalNotificationContact.from_consumed_verification(
        contact_id="legal-contact-replay",
        verification=consumed,
        verified_at=NOW + timedelta(seconds=1),
    )
    session = _Session()
    vr = _VerificationRegistryStub(consumed)
    cr = _ContactRegistryStub((contact,), provenance=contact)

    result = complete_legal_notification_contact_verification(
        tenant_id=TENANT,
        contact_id="ignored-on-replay",
        verification_token=TOKEN,
        observed_at=NOW + timedelta(seconds=2),
        verification_registry=vr,
        contact_registry=cr,
        session=session,
    )

    assert result.contact == contact
    assert result.verification == consumed
    assert result.authority_created is False
    assert vr.consumes == []
    assert cr.created == []
    assert cr.revoked == []


def test_consumed_same_address_without_provenance_returns_existing_authority() -> None:
    source = _verification(verification_id="legal-verification-consumed")
    consumed = source.consume(NOW + timedelta(seconds=1))
    prior = _verification(verification_id="legal-verification-prior-same")
    existing = _contact_from(prior, contact_id="legal-contact-prior")
    session = _Session()
    vr = _VerificationRegistryStub(consumed)
    cr = _ContactRegistryStub((existing,), provenance=None)

    result = complete_legal_notification_contact_verification(
        tenant_id=TENANT,
        contact_id="unused",
        verification_token=TOKEN,
        observed_at=NOW + timedelta(seconds=2),
        verification_registry=vr,
        contact_registry=cr,
        session=session,
    )

    assert result.contact == existing
    assert result.authority_created is False
    assert vr.consumes == []
    assert cr.created == []
    assert cr.revoked == []


def test_consumed_verification_without_lawful_replay_path_fails_closed() -> None:
    source = _verification(
        verification_id="legal-verification-invalid-replay",
        address_digest=ADDRESS_B,
    )
    consumed = source.consume(NOW + timedelta(seconds=1))
    prior = _verification(
        verification_id="legal-verification-prior-other",
        address_digest=ADDRESS_A,
    )
    existing = _contact_from(prior, contact_id="legal-contact-prior-other")
    vr = _VerificationRegistryStub(consumed)
    cr = _ContactRegistryStub((existing,), provenance=None)

    with pytest.raises(
        LegalNotificationContactVerificationOrchestrationError
    ) as captured:
        complete_legal_notification_contact_verification(
            tenant_id=TENANT,
            contact_id="unused",
            verification_token=TOKEN,
            observed_at=NOW + timedelta(seconds=2),
            verification_registry=vr,
            contact_registry=cr,
            session=_Session(),
        )

    assert captured.value.code == "L8_8H7E_VERIFICATION_REPLAY_INVALID"
    assert vr.consumes == []
    assert cr.created == []
    assert cr.revoked == []


def test_multiple_active_contacts_fail_closed_before_mutation() -> None:
    verification = _verification()
    first = _contact_from(
        _verification(verification_id="legal-verification-first"),
        contact_id="legal-contact-first",
    )
    second = _contact_from(
        _verification(verification_id="legal-verification-second"),
        contact_id="legal-contact-second",
    )
    vr = _VerificationRegistryStub(verification)
    cr = _ContactRegistryStub((first, second))

    with pytest.raises(
        LegalNotificationContactVerificationOrchestrationError
    ) as captured:
        complete_legal_notification_contact_verification(
            tenant_id=TENANT,
            contact_id="legal-contact-new",
            verification_token=TOKEN,
            observed_at=NOW + timedelta(seconds=1),
            verification_registry=vr,
            contact_registry=cr,
            session=_Session(),
        )

    assert captured.value.code == "L8_8H7E_MULTIPLE_ACTIVE_CONTACTS"
    assert vr.consumes == []
    assert cr.created == []
    assert cr.revoked == []


@pytest.mark.parametrize(
    ("verification_retry", "contact_retry"),
    [
        ("consume", None),
        (None, "create"),
        (None, "revoke"),
    ],
)
def test_child_retry_signals_become_h7e_whole_transaction_retry(
    verification_retry: str | None,
    contact_retry: str | None,
) -> None:
    verification = _verification(
        address_digest=ADDRESS_B if contact_retry == "revoke" else ADDRESS_A
    )
    vr = _VerificationRegistryStub(
        verification,
        retry_on_consume=verification_retry == "consume",
    )

    history: tuple[VerifiedLegalNotificationContact, ...] = ()
    if contact_retry == "revoke":
        existing = _contact_from(
            _verification(
                verification_id="legal-verification-existing-retry",
                address_digest=ADDRESS_A,
            ),
            contact_id="legal-contact-existing-retry",
        )
        history = (existing,)

    cr = _ContactRegistryStub(
        history,
        retry_on_create=contact_retry == "create",
        retry_on_revoke=contact_retry == "revoke",
    )

    with pytest.raises(
        LegalNotificationContactVerificationOrchestrationRetryRequiredError
    ) as captured:
        complete_legal_notification_contact_verification(
            tenant_id=TENANT,
            contact_id="legal-contact-retry",
            verification_token=TOKEN,
            observed_at=NOW + timedelta(seconds=2),
            verification_registry=vr,
            contact_registry=cr,
            session=_Session(),
        )

    assert captured.value.code == "L8_8H7E_WHOLE_TRANSACTION_RETRY_REQUIRED"


def test_raw_token_is_used_only_to_derive_digest_for_registry_lookup() -> None:
    verification = _verification()
    session = _Session()
    vr = _VerificationRegistryStub(verification)
    cr = _ContactRegistryStub()

    complete_legal_notification_contact_verification(
        tenant_id=TENANT,
        contact_id="legal-contact-token-proof",
        verification_token=TOKEN,
        observed_at=NOW + timedelta(seconds=1),
        verification_registry=vr,
        contact_registry=cr,
        session=session,
    )

    assert vr.reads == [(TENANT, TOKEN_DIGEST, session)]
    assert TOKEN not in repr(vr.reads)
    assert TOKEN not in repr(cr.created)


def test_orchestrator_never_owns_transaction_lifecycle() -> None:
    class TrapSession:
        in_transaction = True

        def start_transaction(self) -> None:
            raise AssertionError("H7E must not start transaction")

        def commit_transaction(self) -> None:
            raise AssertionError("H7E must not commit transaction")

        def abort_transaction(self) -> None:
            raise AssertionError("H7E must not abort transaction")

        def with_transaction(self, callback: Any) -> None:
            raise AssertionError("H7E must not retry transaction")

    verification = _verification()
    vr = _VerificationRegistryStub(verification)
    cr = _ContactRegistryStub()

    result = complete_legal_notification_contact_verification(
        tenant_id=TENANT,
        contact_id="legal-contact-transaction-proof",
        verification_token=TOKEN,
        observed_at=NOW + timedelta(seconds=1),
        verification_registry=vr,
        contact_registry=cr,
        session=TrapSession(),
    )

    assert result.authority_created is True


# ARTIFACT: test_legal_notification_contact_verification_orchestrator.py
# VERSION: v1.0.0-L8-8H7E-DIRECT-UNIT-CERTIFICATE
# AUTHORITY: direct H7E orchestration semantics only
# TRANSACTION POSTURE: caller-owned active transaction certified
# RAW TOKEN POSTURE: transient-only digest lookup certified
# END OF WILSY OS SOVEREIGN ARTIFACT
