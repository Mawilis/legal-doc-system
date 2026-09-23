"""Direct certificate for WILSY OS recovery-contact verification completion.

TITLE: WILSY OS Recovery Contact Verification Completion Direct Certificate
VERSION: v1.0.0-R10E33-RECOVERY-CONTACT-VERIFICATION-COMPLETION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the caller-session transaction that consumes one email-control
         verification and establishes one ACTIVE verified recovery contact from
         current durable principal/email truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_contact_verification_service.py
COLLABORATION / OWNERSHIP: Exercises R10E21 with synthetic transaction/session,
                           verification/contact registries, and auth authority.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E33-RECOVERY-CONTACT-VERIFICATION-COMPLETION-CERT introduces
           direct evidence for session propagation, durable re-read, current-email
           digest binding, exact-principal enforcement, same-contact idempotent
           preservation, changed-contact replacement, verification consumption,
           callback re-invocation re-reads, bounded replay/integrity failures,
           and transaction failure mapping.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic token/email only; no network or real DB.
TENANT BOUNDARY: Durable verification controls tenant/principal/address authority.
AUTHORITY BOUNDARY: Verification-completion transaction test evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from tools.eos.saas.auth.password_recovery_contact import (
    VerifiedRecoveryContact,
    VerifiedRecoveryContactChannel,
)
from tools.eos.saas.auth.password_recovery_contact_verification import (
    RecoveryContactVerification,
)
from tools.eos.saas.auth.password_recovery_contact_verification_registry import (
    RecoveryContactVerificationLifecycleConflictError,
)
from tools.eos.saas.auth.password_recovery_contact_verification_service import (
    RecoveryContactVerificationCode,
    RecoveryContactVerificationService,
    RecoveryContactVerificationServiceError,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    recovery_address_digest,
)

TENANT = "WILSY-TENANT-VERIFY-COMPLETE-CERT"
PRINCIPAL = "WILSY-PRINCIPAL-VERIFY-COMPLETE-CERT"
EMAIL = "verified.user@example.com"
RAW_TOKEN = "synthetic-verification-token"
TOKEN_DIGEST = hashlib.sha3_512(RAW_TOKEN.encode("utf-8")).hexdigest()
ADDRESS_DIGEST = recovery_address_digest(EMAIL)
ISSUED = datetime(2026, 9, 22, 18, 0, tzinfo=timezone.utc)
OBSERVED = ISSUED + timedelta(minutes=5)
EXPIRES = ISSUED + timedelta(minutes=30)


def _verification() -> RecoveryContactVerification:
    return RecoveryContactVerification.issue(
        verification_id="WILSYVERIFY-COMPLETE-CERT",
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        address_digest=ADDRESS_DIGEST,
        token_digest=TOKEN_DIGEST,
        issued_at=ISSUED,
        expires_at=EXPIRES,
    )


def _user(*, email: str = EMAIL, tenant_id: str = TENANT, user_id: str = PRINCIPAL):
    return SimpleNamespace(id=user_id, tenantId=tenant_id, email=email)


class _VerificationRegistry:
    def __init__(self, current: RecoveryContactVerification | None = None) -> None:
        self.current = current or _verification()
        self.lookups = []
        self.consumes = []
        self.consume_error: Exception | None = None

    def get_by_token_digest(self, *, tenant_id, token_digest, session=None):
        self.lookups.append((tenant_id, token_digest, session))
        return self.current

    def consume(self, verification, consumed_at, *, session=None):
        self.consumes.append((verification, consumed_at, session))
        if self.consume_error is not None:
            raise self.consume_error
        return verification.consume(consumed_at)


class _ContactRegistry:
    def __init__(self, existing: VerifiedRecoveryContact | None = None) -> None:
        self.existing = existing
        self.lookups = []
        self.creates = []
        self.revokes = []

    def get_active_by_principal(
        self,
        *,
        tenant_id,
        principal_id,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        session=None,
    ):
        self.lookups.append((tenant_id, principal_id, channel, session))
        return self.existing

    def create(self, contact, *, session=None):
        self.creates.append((contact, session))
        return contact

    def revoke(self, contact, revoked_at, *, session=None):
        self.revokes.append((contact, revoked_at, session))
        return contact.revoke(revoked_at)


class _AuthAuthority:
    def __init__(self, user=None) -> None:
        self.user = user if user is not None else _user()
        self.revision_reads = []
        self.user_reads = []

    def get_credential_revision(self, tenant_id, user_id, *, session=None):
        self.revision_reads.append((tenant_id, user_id, session))
        return 9

    def get_user_by_id(self, user_id, *, session=None):
        self.user_reads.append((user_id, session))
        return self.user


class _Session:
    def __init__(self, *, callbacks: int = 1, fail_transaction: Exception | None = None) -> None:
        self.callbacks = callbacks
        self.fail_transaction = fail_transaction
        self.callback_count = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def with_transaction(self, callback):
        if self.fail_transaction is not None:
            raise self.fail_transaction
        for _ in range(self.callbacks):
            self.callback_count += 1
            callback(self)


class _Client:
    def __init__(self, session: _Session | None = None, *, start_error: Exception | None = None) -> None:
        self.session = session or _Session()
        self.start_error = start_error
        self.starts = 0

    def start_session(self):
        self.starts += 1
        if self.start_error is not None:
            raise self.start_error
        return self.session


def _service(
    *,
    verification_registry=None,
    contact_registry=None,
    auth=None,
    session=None,
    clock=lambda: OBSERVED,
):
    verification_registry = verification_registry or _VerificationRegistry()
    contact_registry = contact_registry or _ContactRegistry()
    auth = auth or _AuthAuthority()
    session = session or _Session()
    client = _Client(session)
    service = RecoveryContactVerificationService(
        client=client,
        verification_registry=verification_registry,
        contact_registry=contact_registry,
        auth_registry=auth,
        clock=clock,
    )
    return service, client, session, verification_registry, contact_registry, auth


def test_success_creates_contact_then_consumes_verification_on_one_session() -> None:
    service, client, session, verification_registry, contact_registry, auth = _service()

    result = service.verify_contact(
        tenant_id=TENANT,
        verification_token=RAW_TOKEN,
    )

    assert result.status == "RECOVERY_CONTACT_VERIFIED"
    assert client.starts == 1
    assert session.callback_count == 1
    assert verification_registry.lookups == [(TENANT, TOKEN_DIGEST, session)]
    assert auth.revision_reads == [(TENANT, PRINCIPAL, session)]
    assert auth.user_reads == [(PRINCIPAL, session)]
    assert contact_registry.lookups == [
        (TENANT, PRINCIPAL, VerifiedRecoveryContactChannel.EMAIL, session)
    ]
    assert len(contact_registry.creates) == 1
    created, create_session = contact_registry.creates[0]
    assert create_session is session
    assert created.tenant_id == TENANT
    assert created.principal_id == PRINCIPAL
    assert created.address_digest == ADDRESS_DIGEST
    assert created.verified_at == OBSERVED
    assert verification_registry.consumes == [
        (_verification(), OBSERVED, session)
    ]


def test_existing_same_digest_is_preserved_and_verification_is_consumed() -> None:
    existing = VerifiedRecoveryContact.issue(
        contact_id="WILSYCONTACT-EXISTING",
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=ADDRESS_DIGEST,
        verified_at=ISSUED - timedelta(days=1),
    )
    contact_registry = _ContactRegistry(existing)
    service, _, session, verification_registry, contact_registry, _ = _service(
        contact_registry=contact_registry
    )

    result = service.verify_contact(tenant_id=TENANT, verification_token=RAW_TOKEN)

    assert result.status == "RECOVERY_CONTACT_VERIFIED"
    assert contact_registry.revokes == []
    assert contact_registry.creates == []
    assert verification_registry.consumes == [(_verification(), OBSERVED, session)]


def test_changed_digest_revokes_prior_contact_and_creates_replacement() -> None:
    old_digest = recovery_address_digest("old@example.com")
    existing = VerifiedRecoveryContact.issue(
        contact_id="WILSYCONTACT-OLD",
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=old_digest,
        verified_at=ISSUED - timedelta(days=10),
    )
    contact_registry = _ContactRegistry(existing)
    service, _, session, verification_registry, contact_registry, _ = _service(
        contact_registry=contact_registry
    )

    service.verify_contact(tenant_id=TENANT, verification_token=RAW_TOKEN)

    assert contact_registry.revokes == [(existing, OBSERVED, session)]
    assert len(contact_registry.creates) == 1
    replacement, create_session = contact_registry.creates[0]
    assert create_session is session
    assert replacement.address_digest == ADDRESS_DIGEST
    assert verification_registry.consumes == [(_verification(), OBSERVED, session)]


def test_current_email_change_rejects_before_contact_mutation_or_consume() -> None:
    auth = _AuthAuthority(_user(email="changed@example.com"))
    service, _, _, verification_registry, contact_registry, _ = _service(auth=auth)

    with pytest.raises(RecoveryContactVerificationServiceError) as captured:
        service.verify_contact(tenant_id=TENANT, verification_token=RAW_TOKEN)

    assert captured.value.code is RecoveryContactVerificationCode.EMAIL_CHANGED
    assert contact_registry.creates == []
    assert contact_registry.revokes == []
    assert verification_registry.consumes == []


def test_principal_or_tenant_binding_mismatch_rejects() -> None:
    auth = _AuthAuthority(_user(tenant_id="OTHER-TENANT"))
    service, _, _, verification_registry, contact_registry, _ = _service(auth=auth)

    with pytest.raises(RecoveryContactVerificationServiceError) as captured:
        service.verify_contact(tenant_id=TENANT, verification_token=RAW_TOKEN)

    assert captured.value.code is RecoveryContactVerificationCode.PRINCIPAL_MISMATCH
    assert contact_registry.creates == []
    assert verification_registry.consumes == []


def test_consume_replay_conflict_maps_to_replayed_code() -> None:
    verification_registry = _VerificationRegistry()
    verification_registry.consume_error = RecoveryContactVerificationLifecycleConflictError(
        "RECOVERY_CONTACT_VERIFICATION_CONSUMED"
    )
    service, *_ = _service(verification_registry=verification_registry)

    with pytest.raises(RecoveryContactVerificationServiceError) as captured:
        service.verify_contact(tenant_id=TENANT, verification_token=RAW_TOKEN)

    assert captured.value.code is RecoveryContactVerificationCode.VERIFICATION_REPLAYED


def test_transaction_callback_reinvocation_re_reads_all_authority() -> None:
    session = _Session(callbacks=2)
    service, _, _, verification_registry, contact_registry, auth = _service(
        session=session
    )

    result = service.verify_contact(tenant_id=TENANT, verification_token=RAW_TOKEN)

    assert result.status == "RECOVERY_CONTACT_VERIFIED"
    assert len(verification_registry.lookups) == 2
    assert len(auth.revision_reads) == 2
    assert len(auth.user_reads) == 2
    assert len(contact_registry.lookups) == 2
    assert len(contact_registry.creates) == 2
    assert len(verification_registry.consumes) == 2
    assert all(call[2] is session for call in verification_registry.lookups)
    assert all(call[2] is session for call in auth.revision_reads)
    assert all(call[1] is session for call in contact_registry.creates)


@pytest.mark.parametrize(
    ("tenant_id", "token"),
    [
        ("", RAW_TOKEN),
        (" tenant", RAW_TOKEN),
        (TENANT, ""),
        (TENANT, "x" * 4097),
    ],
)
def test_invalid_selector_or_token_rejects_before_session(tenant_id, token) -> None:
    service, client, *_ = _service()

    with pytest.raises(RecoveryContactVerificationServiceError) as captured:
        service.verify_contact(tenant_id=tenant_id, verification_token=token)

    assert captured.value.code is RecoveryContactVerificationCode.INVALID_REQUEST
    assert client.starts == 0


def test_start_session_and_transaction_failures_map_without_success() -> None:
    start_client = _Client(start_error=RuntimeError("start failed"))
    start_service = RecoveryContactVerificationService(
        client=start_client,
        verification_registry=_VerificationRegistry(),
        contact_registry=_ContactRegistry(),
        auth_registry=_AuthAuthority(),
        clock=lambda: OBSERVED,
    )

    with pytest.raises(RecoveryContactVerificationServiceError) as start_error:
        start_service.verify_contact(tenant_id=TENANT, verification_token=RAW_TOKEN)
    assert start_error.value.code is RecoveryContactVerificationCode.TRANSACTION_FAILURE

    session = _Session(fail_transaction=RuntimeError("transaction failed"))
    service, *_ = _service(session=session)
    with pytest.raises(RecoveryContactVerificationServiceError) as transaction_error:
        service.verify_contact(tenant_id=TENANT, verification_token=RAW_TOKEN)
    assert transaction_error.value.code is RecoveryContactVerificationCode.TRANSACTION_FAILURE


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_contact_verification_service.py
# VERSION: v1.0.0-R10E33-RECOVERY-CONTACT-VERIFICATION-COMPLETION-CERT
# AUTHORITY BOUNDARY: deterministic completion-transaction test evidence only
# TENANT POSTURE: durable verification controls exact tenant/principal/address
# FAIL-CLOSED POSTURE: mismatch, email drift, replay, transaction failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
