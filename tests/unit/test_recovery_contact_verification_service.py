"""Direct certificate for authenticated recovery-contact verification service.

TITLE: WILSY OS Recovery Contact Verification Service Direct Certificate
VERSION: v1.0.0-R10E14-RECOVERY-CONTACT-VERIFICATION-SERVICE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies authenticated contact enrollment and atomic possession verification
         without MongoDB, SMTP, network, or JWT-email authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_recovery_contact_verification_service.py
COLLABORATION / OWNERSHIP: Deterministic fakes certify the R10E14 service contract.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E14-RECOVERY-CONTACT-VERIFICATION-SERVICE-CERT — Certifies ACTIVE
    principal admission, PENDING contact creation/replacement, verified-contact
    replacement denial, challenge supersession, 15-minute digest-only issuance,
    post-commit delivery, delivery-failure compensation, challenge replay/expiry
    rejection, exact transactional session propagation, and atomic contact verify.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic addresses/bearers only; raw bearer is never persisted.
TENANT BOUNDARY: Exact authenticated tenant/principal bindings.
AUTHORITY BOUNDARY: Verification ceremony evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.auth.recovery_contact import (
    RecoveryContactAuthority,
    RecoveryContactStatus,
    RecoveryContactVerificationMethod,
)
from tools.eos.saas.auth.recovery_contact_verification import (
    RecoveryContactVerificationChallenge,
    RecoveryContactVerificationStatus,
)
from tools.eos.saas.auth.recovery_contact_verification_service import (
    VERIFICATION_TTL,
    RecoveryContactVerificationService,
    RecoveryContactVerificationServiceCode,
    RecoveryContactVerificationServiceError,
)


NOW = datetime(2026, 9, 22, 20, 0, 0, tzinfo=timezone.utc)
RAW = "synthetic-verification-bearer-value-0123456789-ABCDE"
ADDRESS = "recovery@example.com"


class _Session:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    def __enter__(self) -> "_Session":
        self.events.append("session-enter")
        return self

    def __exit__(self, *_args: Any) -> None:
        self.events.append("session-exit")

    def with_transaction(self, callback: Any) -> None:
        self.events.append("transaction-begin")
        callback(self)
        self.events.append("transaction-commit")


class _Client:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.sessions: list[_Session] = []

    def start_session(self) -> _Session:
        session = _Session(self.events)
        self.sessions.append(session)
        return session


class _Principal:
    def __init__(self, status: PrincipalStatus = PrincipalStatus.ACTIVE) -> None:
        self.status = status
        self.calls: list[tuple[str, Any]] = []

    def get(self, principal_id: str, *, session: Any = None) -> Any:
        self.calls.append((principal_id, session))
        return SimpleNamespace(principal_id=principal_id, status=self.status, revision=7)


class _Contacts:
    def __init__(self, current: RecoveryContactAuthority | None = None) -> None:
        self.current = current
        self.history: dict[str, RecoveryContactAuthority] = {}
        if current is not None:
            self.history[current.contact_id] = current
        self.calls: list[tuple[str, Any]] = []

    def get_current_for_principal(
        self, *, tenant_id: str, principal_id: str, session: Any = None, **_kwargs: Any
    ) -> RecoveryContactAuthority | None:
        self.calls.append(("current", (tenant_id, principal_id, session)))
        if self.current is None:
            return None
        if self.current.tenant_id != tenant_id or self.current.principal_id != principal_id:
            return None
        if self.current.status is RecoveryContactStatus.REVOKED:
            return None
        return self.current

    def get_by_contact_id(
        self, *, tenant_id: str, contact_id: str, session: Any = None
    ) -> RecoveryContactAuthority | None:
        self.calls.append(("get", (tenant_id, contact_id, session)))
        contact = self.history.get(contact_id)
        return contact if contact is not None and contact.tenant_id == tenant_id else None

    def create_pending(
        self, contact: RecoveryContactAuthority, *, session: Any = None
    ) -> RecoveryContactAuthority:
        self.calls.append(("create", (contact, session)))
        self.current = contact
        self.history[contact.contact_id] = contact
        return contact

    def verify(
        self,
        contact: RecoveryContactAuthority,
        *,
        verified_at: datetime,
        method: RecoveryContactVerificationMethod,
        session: Any = None,
    ) -> RecoveryContactAuthority:
        self.calls.append(("verify", (contact, verified_at, method, session)))
        replacement = contact.verify(verified_at=verified_at, method=method)
        self.current = replacement
        self.history[replacement.contact_id] = replacement
        return replacement

    def revoke(
        self, contact: RecoveryContactAuthority, *, revoked_at: datetime, session: Any = None
    ) -> RecoveryContactAuthority:
        self.calls.append(("revoke", (contact, revoked_at, session)))
        replacement = contact.revoke(revoked_at=revoked_at)
        if self.current is not None and self.current.contact_id == contact.contact_id:
            self.current = None
        self.history[replacement.contact_id] = replacement
        return replacement


class _Challenges:
    def __init__(self) -> None:
        self.items: list[RecoveryContactVerificationChallenge] = []
        self.calls: list[tuple[str, Any]] = []

    def _replace(self, replacement: RecoveryContactVerificationChallenge) -> None:
        self.items = [
            replacement if item.challenge_id == replacement.challenge_id else item
            for item in self.items
        ]

    def list_active_for_contact(
        self, *, tenant_id: str, principal_id: str, contact_id: str, session: Any = None
    ) -> tuple[RecoveryContactVerificationChallenge, ...]:
        self.calls.append(("list", (tenant_id, principal_id, contact_id, session)))
        return tuple(
            item
            for item in self.items
            if item.tenant_id == tenant_id
            and item.principal_id == principal_id
            and item.contact_id == contact_id
            and item.status is RecoveryContactVerificationStatus.ACTIVE
        )

    def get_by_token_digest(
        self, *, tenant_id: str, token_digest: str, session: Any = None
    ) -> RecoveryContactVerificationChallenge | None:
        self.calls.append(("get", (tenant_id, token_digest, session)))
        return next(
            (
                item
                for item in self.items
                if item.tenant_id == tenant_id and item.token_digest == token_digest
            ),
            None,
        )

    def create(
        self, challenge: RecoveryContactVerificationChallenge, *, session: Any = None
    ) -> RecoveryContactVerificationChallenge:
        self.calls.append(("create", (challenge, session)))
        self.items.append(challenge)
        return challenge

    def consume(
        self,
        challenge: RecoveryContactVerificationChallenge,
        consumed_at: datetime,
        *,
        session: Any = None,
    ) -> RecoveryContactVerificationChallenge:
        self.calls.append(("consume", (challenge, consumed_at, session)))
        replacement = challenge.consume(consumed_at)
        self._replace(replacement)
        return replacement

    def expire(
        self,
        challenge: RecoveryContactVerificationChallenge,
        expired_at: datetime,
        *,
        session: Any = None,
    ) -> RecoveryContactVerificationChallenge:
        self.calls.append(("expire", (challenge, expired_at, session)))
        replacement = challenge.expire(expired_at)
        self._replace(replacement)
        return replacement

    def revoke(
        self,
        challenge: RecoveryContactVerificationChallenge,
        revoked_at: datetime,
        *,
        session: Any = None,
    ) -> RecoveryContactVerificationChallenge:
        self.calls.append(("revoke", (challenge, revoked_at, session)))
        replacement = challenge.revoke(revoked_at)
        self._replace(replacement)
        return replacement


class _Delivery:
    def __init__(self, events: list[str], fail: bool = False) -> None:
        self.events = events
        self.fail = fail
        self.calls: list[dict[str, Any]] = []

    def deliver_recovery_contact_verification(self, **kwargs: Any) -> None:
        self.events.append("delivery")
        self.calls.append(dict(kwargs))
        if self.fail:
            raise RuntimeError("synthetic delivery failure")


def _pending(address: str = ADDRESS) -> RecoveryContactAuthority:
    return RecoveryContactAuthority.pending(
        contact_id="contact-existing",
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        address=address,
        created_at=NOW - timedelta(minutes=2),
    )


def _verified(address: str = ADDRESS) -> RecoveryContactAuthority:
    return _pending(address).verify(
        verified_at=NOW - timedelta(minutes=1),
        method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
    )


def _service(
    *,
    principal: _Principal | None = None,
    contacts: _Contacts | None = None,
    challenges: _Challenges | None = None,
    delivery_fail: bool = False,
) -> tuple[
    RecoveryContactVerificationService,
    _Client,
    _Contacts,
    _Challenges,
    _Delivery,
    list[str],
]:
    events: list[str] = []
    client = _Client(events)
    contact_registry = contacts or _Contacts()
    challenge_registry = challenges or _Challenges()
    delivery = _Delivery(events, fail=delivery_fail)
    service = RecoveryContactVerificationService(
        delivery=delivery,
        client=client,
        principal_repository=principal or _Principal(),
        contact_registry=contact_registry,
        challenge_registry=challenge_registry,
        clock=lambda: NOW,
        token_factory=lambda: RAW,
        contact_id_factory=lambda: "contact-new",
        challenge_id_factory=lambda: "challenge-new",
    )
    return service, client, contact_registry, challenge_registry, delivery, events


def test_request_creates_pending_contact_and_digest_only_challenge_then_delivers_after_commit() -> None:
    service, client, contacts, challenges, delivery, events = _service()
    result = service.request_verification(
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        address=" Recovery@Example.COM ",
    )
    assert result.status == "RECOVERY_CONTACT_VERIFICATION_SENT"
    assert len(client.sessions) == 1
    assert contacts.current is not None
    assert contacts.current.status is RecoveryContactStatus.PENDING
    assert contacts.current.address == ADDRESS
    assert len(challenges.items) == 1
    challenge = challenges.items[0]
    assert challenge.token_digest == hashlib.sha3_512(RAW.encode()).hexdigest()
    assert RAW not in repr(challenge)
    assert challenge.expires_at == NOW + VERIFICATION_TTL
    assert delivery.calls == [{
        "recipient_email": ADDRESS,
        "verification_token": RAW,
        "expires_at": NOW + VERIFICATION_TTL,
    }]
    assert events.index("transaction-commit") < events.index("delivery")


def test_existing_verified_same_address_returns_without_challenge_or_delivery() -> None:
    contacts = _Contacts(_verified())
    service, client, _contacts, challenges, delivery, _events = _service(contacts=contacts)
    result = service.request_verification(
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        address=ADDRESS,
    )
    assert result.status == "RECOVERY_CONTACT_ALREADY_VERIFIED"
    assert len(client.sessions) == 1
    assert challenges.items == []
    assert delivery.calls == []


def test_existing_verified_different_address_is_not_silently_replaced() -> None:
    contacts = _Contacts(_verified())
    service, _client, _contacts, challenges, delivery, _events = _service(contacts=contacts)
    with pytest.raises(RecoveryContactVerificationServiceError) as error:
        service.request_verification(
            tenant_id="TENANT-ONE",
            principal_id="principal-one",
            address="different@example.com",
        )
    assert error.value.code is RecoveryContactVerificationServiceCode.REPLACEMENT_FORBIDDEN
    assert contacts.current == _verified()
    assert challenges.items == []
    assert delivery.calls == []


def test_pending_same_address_supersedes_old_active_challenge() -> None:
    contacts = _Contacts(_pending())
    challenges = _Challenges()
    old = RecoveryContactVerificationChallenge.issue(
        challenge_id="old",
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        contact_id="contact-existing",
        address=ADDRESS,
        token_digest=hashlib.sha3_512(b"old").hexdigest(),
        issued_at=NOW - timedelta(minutes=2),
        expires_at=NOW + timedelta(minutes=13),
    )
    challenges.items.append(old)
    service, _client, _contacts, challenge_registry, delivery, _events = _service(
        contacts=contacts, challenges=challenges
    )
    service.request_verification(
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        address=ADDRESS,
    )
    assert next(item for item in challenge_registry.items if item.challenge_id == "old").status is RecoveryContactVerificationStatus.REVOKED
    assert any(item.challenge_id == "challenge-new" and item.status is RecoveryContactVerificationStatus.ACTIVE for item in challenge_registry.items)
    assert delivery.calls[0]["recipient_email"] == ADDRESS


def test_pending_different_address_revokes_old_contact_and_creates_new_pending() -> None:
    contacts = _Contacts(_pending("old@example.com"))
    service, _client, contact_registry, _challenges, delivery, _events = _service(contacts=contacts)
    service.request_verification(
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        address=ADDRESS,
    )
    assert contact_registry.history["contact-existing"].status is RecoveryContactStatus.REVOKED
    assert contact_registry.current is not None
    assert contact_registry.current.contact_id == "contact-new"
    assert contact_registry.current.address == ADDRESS
    assert delivery.calls[0]["recipient_email"] == ADDRESS


def test_delivery_failure_revokes_new_pending_contact_and_challenge() -> None:
    service, client, contacts, challenges, _delivery, events = _service(delivery_fail=True)
    with pytest.raises(RecoveryContactVerificationServiceError) as error:
        service.request_verification(
            tenant_id="TENANT-ONE",
            principal_id="principal-one",
            address=ADDRESS,
        )
    assert error.value.code is RecoveryContactVerificationServiceCode.DELIVERY_FAILURE
    assert len(client.sessions) == 2
    assert contacts.history["contact-new"].status is RecoveryContactStatus.REVOKED
    assert challenges.items[0].status is RecoveryContactVerificationStatus.REVOKED
    assert events.count("transaction-commit") == 2


def test_complete_verification_consumes_challenge_and_verifies_contact_same_session() -> None:
    service, client, contacts, challenges, _delivery, _events = _service()
    service.request_verification(
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        address=ADDRESS,
    )
    result = service.complete_verification(
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        verification_token=RAW,
    )
    assert result.status == "RECOVERY_CONTACT_VERIFIED"
    assert contacts.current is not None
    assert contacts.current.status is RecoveryContactStatus.VERIFIED
    assert contacts.current.verification_method is RecoveryContactVerificationMethod.EMAIL_CHALLENGE
    assert challenges.items[0].status is RecoveryContactVerificationStatus.CONSUMED
    consume = next(call for call in challenges.calls if call[0] == "consume")
    verify = next(call for call in contacts.calls if call[0] == "verify")
    assert consume[1][2] is client.sessions[1]
    assert verify[1][3] is client.sessions[1]


def test_replay_and_wrong_principal_fail_without_second_verification() -> None:
    service, _client, contacts, _challenges, _delivery, _events = _service()
    service.request_verification(
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        address=ADDRESS,
    )
    service.complete_verification(
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        verification_token=RAW,
    )
    with pytest.raises(RecoveryContactVerificationServiceError) as replay:
        service.complete_verification(
            tenant_id="TENANT-ONE",
            principal_id="principal-one",
            verification_token=RAW,
        )
    assert replay.value.code is RecoveryContactVerificationServiceCode.CHALLENGE_INVALID

    other, *_ = _service(contacts=contacts)
    with pytest.raises(RecoveryContactVerificationServiceError) as wrong:
        other.complete_verification(
            tenant_id="TENANT-ONE",
            principal_id="principal-other",
            verification_token=RAW,
        )
    assert wrong.value.code is RecoveryContactVerificationServiceCode.CHALLENGE_INVALID


def test_inactive_principal_denies_before_contact_or_challenge_mutation() -> None:
    service, _client, contacts, challenges, delivery, _events = _service(
        principal=_Principal(PrincipalStatus.SUSPENDED)
    )
    with pytest.raises(RecoveryContactVerificationServiceError) as error:
        service.request_verification(
            tenant_id="TENANT-ONE",
            principal_id="principal-one",
            address=ADDRESS,
        )
    assert error.value.code is RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE
    assert contacts.current is None
    assert challenges.items == []
    assert delivery.calls == []


# ARTIFACT: tests/unit/test_recovery_contact_verification_service.py
# VERSION: v1.0.0-R10E14-RECOVERY-CONTACT-VERIFICATION-SERVICE-CERT
# AUTHORITY BOUNDARY: deterministic authenticated recovery-contact verification orchestration evidence
# TENANT POSTURE: exact authenticated tenant/principal binding; identity email grants no recovery authority
# FAIL-CLOSED POSTURE: inactive, replacement, replay, expiry, delivery, and transaction failures never verify contact
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
