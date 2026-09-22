"""Direct certificate for authenticated recovery-contact verification issuance.

TITLE: WILSY OS Recovery Contact Verification Request Service Direct Certificate
VERSION: v1.0.0-R10E32-RECOVERY-CONTACT-VERIFICATION-REQUEST-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies that authenticated verification issuance re-reads durable
         principal/email truth, ignores browser contact claims, rate-limits,
         persists digest-only capability state, uses trusted fragment links,
         and revokes capability state on delivery failure.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_contact_verification_request_service.py
COLLABORATION / OWNERSHIP: Exercises R10E20 with synthetic canonical registries,
                           durable user projections, rate gate, and mail adapter.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E32-RECOVERY-CONTACT-VERIFICATION-REQUEST-CERT introduces
           direct evidence for ACTIVE identity admission, durable principal/email
           binding, already-verified short circuit, separate rate gating,
           digest-only issuance, trusted-origin fragment delivery, secret-free
           result, and delivery-failure revocation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic email/token material only; no network or DB.
TENANT BOUNDARY: Exact ACCESS tenant/principal must match durable user state.
AUTHORITY BOUNDARY: Verification-request orchestration test evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.auth.password_recovery_contact import (
    VerifiedRecoveryContact,
    VerifiedRecoveryContactChannel,
)
from tools.eos.saas.auth.password_recovery_contact_registry import (
    VerifiedRecoveryContactRegistry,
)
from tools.eos.saas.auth.password_recovery_contact_verification import (
    RecoveryContactVerification,
    RecoveryContactVerificationStatus,
)
from tools.eos.saas.auth.password_recovery_contact_verification_registry import (
    RecoveryContactVerificationRegistry,
)
from tools.eos.saas.auth.password_recovery_contact_verification_request_service import (
    RecoveryContactVerificationRequestError,
    RecoveryContactVerificationRequestService,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    PasswordRecoveryRequestRateLimitedError,
    recovery_address_digest,
)

TENANT = "WILSY-TENANT-VERIFY-REQUEST-CERT"
PRINCIPAL = "WILSY-PRINCIPAL-VERIFY-REQUEST-CERT"
DURABLE_EMAIL = "verified.user@example.com"
IDENTITY_EMAIL = "browser.claim@example.invalid"
OBSERVED = datetime(2026, 9, 22, 18, 0, tzinfo=timezone.utc)


def _identity(*, status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username="verified-user",
        email=IDENTITY_EMAIL,
        roles=[],
        permissions=[],
        auth_method="jwt",
        status=status,
    )


class _VerificationRegistry(RecoveryContactVerificationRegistry):
    def __init__(self) -> None:
        super().__init__(collection=object())
        self.created: list[RecoveryContactVerification] = []
        self.revoked: list[RecoveryContactVerification] = []

    def create(self, verification, *, session=None):
        assert session is None
        self.created.append(verification)
        return verification

    def revoke(self, verification, revoked_at, *, session=None):
        assert session is None
        self.revoked.append(verification)
        return verification.revoke(revoked_at)


class _ContactRegistry(VerifiedRecoveryContactRegistry):
    def __init__(self, existing: VerifiedRecoveryContact | None = None) -> None:
        super().__init__(collection=object())
        self.existing = existing
        self.lookups: list[tuple[str, str, VerifiedRecoveryContactChannel]] = []

    def get_active_by_principal(
        self,
        *,
        tenant_id,
        principal_id,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        session=None,
    ):
        assert session is None
        self.lookups.append((tenant_id, principal_id, channel))
        return self.existing


class _AuthRegistry(AuthRegistry):
    def __init__(self, user) -> None:
        super().__init__()
        self.user = user
        self.revision_reads: list[tuple[str, str]] = []
        self.user_reads: list[str] = []

    def get_credential_revision(self, tenant_id, user_id, *, session=None):
        assert session is None
        self.revision_reads.append((tenant_id, user_id))
        return 7

    def get_user_by_id(self, user_id, *, session=None):
        assert session is None
        self.user_reads.append(user_id)
        return self.user


class _RateGate:
    def __init__(self, error: Exception | None = None) -> None:
        self.calls: list[tuple[str, str, datetime]] = []
        self.error = error

    def require_allowed(self, *, tenant_id, address_digest, observed_at):
        self.calls.append((tenant_id, address_digest, observed_at))
        if self.error is not None:
            raise self.error


class _Delivery:
    def __init__(self, error: Exception | None = None) -> None:
        self.messages = []
        self.error = error

    def deliver(self, message):
        self.messages.append(message)
        if self.error is not None:
            raise self.error


def _user(*, email: str = DURABLE_EMAIL, tenant_id: str = TENANT, user_id: str = PRINCIPAL):
    return SimpleNamespace(id=user_id, tenantId=tenant_id, email=email)


def _service(
    *,
    existing: VerifiedRecoveryContact | None = None,
    user=None,
    rate_error: Exception | None = None,
    delivery_error: Exception | None = None,
):
    verification_registry = _VerificationRegistry()
    contact_registry = _ContactRegistry(existing)
    auth_registry = _AuthRegistry(user or _user())
    rate_gate = _RateGate(rate_error)
    delivery = _Delivery(delivery_error)
    service = RecoveryContactVerificationRequestService(
        verification_registry=verification_registry,
        contact_registry=contact_registry,
        auth_registry=auth_registry,
        rate_limit_gate=rate_gate,
        delivery_adapter=delivery,
        public_origin="https://app.wilsy.example",
        verification_ttl=timedelta(minutes=30),
    )
    return service, verification_registry, contact_registry, auth_registry, rate_gate, delivery


def test_success_uses_durable_email_not_identity_email_and_returns_secret_free_status() -> None:
    service, verification_registry, _, auth, rate, delivery = _service()

    result = service.request_verification(
        identity=_identity(),
        observed_at=OBSERVED,
    )

    assert result.status == "VERIFICATION_SENT"
    assert auth.revision_reads == [(TENANT, PRINCIPAL)]
    assert auth.user_reads == [PRINCIPAL]
    assert len(rate.calls) == 1
    assert rate.calls[0] == (
        TENANT,
        recovery_address_digest(DURABLE_EMAIL),
        OBSERVED,
    )
    assert len(verification_registry.created) == 1
    verification = verification_registry.created[0]
    assert verification.tenant_id == TENANT
    assert verification.principal_id == PRINCIPAL
    assert verification.address_digest == recovery_address_digest(DURABLE_EMAIL)
    assert verification.status is RecoveryContactVerificationStatus.ACTIVE
    assert len(verification.token_digest) == 128
    assert len(delivery.messages) == 1
    message = delivery.messages[0]
    assert message.recipient_email == DURABLE_EMAIL
    assert IDENTITY_EMAIL not in message.verification_url
    assert DURABLE_EMAIL not in message.verification_url
    assert not hasattr(result, "token")
    assert not hasattr(result, "email")


def test_verification_link_uses_configured_https_origin_and_fragment_secret() -> None:
    service, _, _, _, _, delivery = _service()

    service.request_verification(identity=_identity(), observed_at=OBSERVED)

    parsed = urlsplit(delivery.messages[0].verification_url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "app.wilsy.example"
    assert parsed.path == "/verify-recovery-contact"
    assert parsed.query == ""
    fragment = parse_qs(parsed.fragment)
    assert fragment["tenant"] == [TENANT]
    assert len(fragment["verification"][0]) > 32


def test_matching_active_contact_short_circuits_before_rate_or_delivery() -> None:
    existing = VerifiedRecoveryContact.issue(
        contact_id="WILSYCONTACT-EXISTING",
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=recovery_address_digest(DURABLE_EMAIL),
        verified_at=OBSERVED - timedelta(days=1),
    )
    service, verification_registry, _, _, rate, delivery = _service(existing=existing)

    result = service.request_verification(identity=_identity(), observed_at=OBSERVED)

    assert result.status == "VERIFICATION_NOT_REQUIRED"
    assert rate.calls == []
    assert verification_registry.created == []
    assert delivery.messages == []


def test_stale_active_contact_does_not_short_circuit_new_email_verification() -> None:
    stale = VerifiedRecoveryContact.issue(
        contact_id="WILSYCONTACT-STALE",
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=hashlib.sha3_512(b"old@example.com").hexdigest(),
        verified_at=OBSERVED - timedelta(days=5),
    )
    service, verification_registry, _, _, rate, delivery = _service(existing=stale)

    result = service.request_verification(identity=_identity(), observed_at=OBSERVED)

    assert result.status == "VERIFICATION_SENT"
    assert len(rate.calls) == 1
    assert len(verification_registry.created) == 1
    assert len(delivery.messages) == 1


def test_inactive_identity_and_durable_binding_mismatch_fail_closed() -> None:
    service, *_ = _service()

    with pytest.raises(RecoveryContactVerificationRequestError) as inactive:
        service.request_verification(
            identity=_identity(status=PrincipalStatus.SUSPENDED),
            observed_at=OBSERVED,
        )
    assert inactive.value.code == "RECOVERY_CONTACT_PRINCIPAL_NOT_ACTIVE"

    mismatch_service, *_ = _service(user=_user(tenant_id="OTHER-TENANT"))
    with pytest.raises(RecoveryContactVerificationRequestError) as mismatch:
        mismatch_service.request_verification(
            identity=_identity(),
            observed_at=OBSERVED,
        )
    assert mismatch.value.code == "RECOVERY_CONTACT_PRINCIPAL_BINDING_MISMATCH"


def test_rate_limit_maps_to_verification_specific_failure_before_issuance() -> None:
    service, verification_registry, _, _, rate, delivery = _service(
        rate_error=PasswordRecoveryRequestRateLimitedError("RECOVERY_REQUEST_RATE_LIMITED")
    )

    with pytest.raises(RecoveryContactVerificationRequestError) as captured:
        service.request_verification(identity=_identity(), observed_at=OBSERVED)

    assert captured.value.code == "RECOVERY_CONTACT_VERIFICATION_RATE_LIMITED"
    assert len(rate.calls) == 1
    assert verification_registry.created == []
    assert delivery.messages == []


def test_delivery_failure_revokes_new_verification_and_exposes_no_secret() -> None:
    service, verification_registry, _, _, _, delivery = _service(
        delivery_error=RuntimeError("synthetic mail failure")
    )

    with pytest.raises(RecoveryContactVerificationRequestError) as captured:
        service.request_verification(identity=_identity(), observed_at=OBSERVED)

    assert captured.value.code == "RECOVERY_CONTACT_VERIFICATION_DELIVERY_FAILED"
    assert len(verification_registry.created) == 1
    assert verification_registry.revoked == verification_registry.created
    assert len(delivery.messages) == 1
    assert delivery.messages[0].verification_url not in str(captured.value)


def test_unconfirmed_revocation_escalates_delivery_failure() -> None:
    service, verification_registry, _, _, _, _ = _service(
        delivery_error=RuntimeError("synthetic mail failure")
    )

    def fail_revoke(*args, **kwargs):
        raise RuntimeError("synthetic revoke failure")

    verification_registry.revoke = fail_revoke  # type: ignore[method-assign]

    with pytest.raises(RecoveryContactVerificationRequestError) as captured:
        service.request_verification(identity=_identity(), observed_at=OBSERVED)

    assert captured.value.code == (
        "RECOVERY_CONTACT_VERIFICATION_DELIVERY_FAILED_REVOCATION_UNCONFIRMED"
    )


@pytest.mark.parametrize(
    "origin",
    [
        "http://app.wilsy.example",
        "https://user:pass@app.wilsy.example",
        "https://app.wilsy.example?next=x",
        "https://app.wilsy.example#fragment",
        " https://app.wilsy.example",
    ],
)
def test_constructor_rejects_untrusted_public_origin(origin) -> None:
    with pytest.raises(RecoveryContactVerificationRequestError) as captured:
        RecoveryContactVerificationRequestService(
            verification_registry=_VerificationRegistry(),
            contact_registry=_ContactRegistry(),
            auth_registry=_AuthRegistry(_user()),
            rate_limit_gate=_RateGate(),
            delivery_adapter=_Delivery(),
            public_origin=origin,
        )
    assert captured.value.code == "RECOVERY_CONTACT_VERIFICATION_ORIGIN_INVALID"


def test_naive_observation_time_rejects_before_dependency_calls() -> None:
    service, verification_registry, _, auth, rate, delivery = _service()

    with pytest.raises(RecoveryContactVerificationRequestError) as captured:
        service.request_verification(
            identity=_identity(),
            observed_at=datetime(2026, 9, 22, 18, 0),
        )

    assert captured.value.code == "RECOVERY_CONTACT_VERIFICATION_TIME_INVALID"
    assert auth.revision_reads == []
    assert rate.calls == []
    assert verification_registry.created == []
    assert delivery.messages == []


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_contact_verification_request_service.py
# VERSION: v1.0.0-R10E32-RECOVERY-CONTACT-VERIFICATION-REQUEST-CERT
# AUTHORITY BOUNDARY: deterministic verification-issuance orchestration evidence
# TENANT POSTURE: exact ACCESS tenant/principal + durable email binding certified
# FAIL-CLOSED POSTURE: mismatch, rate, origin, delivery, revocation failure rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
