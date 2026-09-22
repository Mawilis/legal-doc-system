"""Direct certificate for WILSY OS password-recovery request issuance.

TITLE: WILSY OS Password Recovery Request Service Direct Certificate
VERSION: v1.0.0-R10E4-PASSWORD-RECOVERY-REQUEST-DIRECT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the R10E3 issuance boundary without network or Mongo runtime:
         verified-contact admission, anti-enumeration absence, current-email
         binding, token/digest separation, trusted fragment links, mandatory
         rate gating, delivery rollback, and secret-free public results.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_request_service.py
COLLABORATION / OWNERSHIP: Exercises R10E3 with deterministic in-memory authority
                           doubles; it does not replace real-Mongo or real-mail
                           certification.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E4-PASSWORD-RECOVERY-REQUEST-DIRECT-CERT introduces bounded
           direct evidence for issuance, absence, tenant/email drift, rate
           limiting, trusted-origin validation, fragment secret placement,
           capability revocation on delivery failure, and no raw-token return.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic addresses/tokens only; assertions ensure
                            raw capabilities are transient and public results
                            disclose no account or delivery truth.
TENANT BOUNDARY: Cross-tenant principal mismatch cannot issue or deliver.
AUTHORITY BOUNDARY: Test evidence only; no production authority is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Dependency and revocation failure assertions must raise
                     stable code-only service errors.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import pytest

from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.auth.password_recovery import PasswordRecoveryCapability
from tools.eos.saas.auth.password_recovery_contact import (
    VerifiedRecoveryContact,
    VerifiedRecoveryContactChannel,
)
from tools.eos.saas.auth.password_recovery_contact_registry import (
    VerifiedRecoveryContactRegistry,
)
from tools.eos.saas.auth.password_recovery_registry import (
    PasswordRecoveryCapabilityRegistry,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    PasswordRecoveryDeliveryMessage,
    PasswordRecoveryRequestDependencyError,
    PasswordRecoveryRequestRateLimitedError,
    PasswordRecoveryRequestResult,
    PasswordRecoveryRequestService,
    PasswordRecoveryRequestServiceError,
    normalize_recovery_email,
    recovery_address_digest,
)

OBSERVED = datetime(2026, 9, 22, 16, 0, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-TEST"
PRINCIPAL = "WILSYAUTH-TEST"
EMAIL = "operator@example.com"
DIGEST = hashlib.sha3_512(EMAIL.encode("utf-8")).hexdigest()


class ContactRegistryDouble(VerifiedRecoveryContactRegistry):
    """Deterministic ACTIVE-contact lookup double."""

    def __init__(self, contact: VerifiedRecoveryContact | None) -> None:
        self.contact = contact
        self.calls: list[dict[str, object]] = []

    def get_active_by_address_digest(self, **kwargs):  # type: ignore[no-untyped-def]
        self.calls.append(dict(kwargs))
        return self.contact


class CapabilityRegistryDouble(PasswordRecoveryCapabilityRegistry):
    """Capture durable capability create/revoke calls."""

    def __init__(self, *, revoke_error: Exception | None = None) -> None:
        self.created: list[PasswordRecoveryCapability] = []
        self.revoked: list[tuple[PasswordRecoveryCapability, datetime]] = []
        self.revoke_error = revoke_error

    def create(self, capability, *, session=None):  # type: ignore[no-untyped-def]
        self.created.append(capability)
        return capability

    def revoke(self, capability, revoked_at, *, session=None):  # type: ignore[no-untyped-def]
        if self.revoke_error is not None:
            raise self.revoke_error
        self.revoked.append((capability, revoked_at))
        return capability.revoke(revoked_at)


class AuthRegistryDouble(AuthRegistry):
    """Return one synthetic current principal without database access."""

    def __init__(self, user) -> None:  # type: ignore[no-untyped-def]
        self.user = user
        self.calls: list[str] = []

    def get_user_by_id(self, user_id: str, *, session=None):  # type: ignore[no-untyped-def]
        self.calls.append(user_id)
        return self.user


class RateGateDouble:
    """Mandatory rate gate double."""

    def __init__(self, *, limited: bool = False) -> None:
        self.limited = limited
        self.calls: list[dict[str, object]] = []

    def require_allowed(self, **kwargs):  # type: ignore[no-untyped-def]
        self.calls.append(dict(kwargs))
        if self.limited:
            raise PasswordRecoveryRequestRateLimitedError("RECOVERY_REQUEST_RATE_LIMITED")


class DeliveryDouble:
    """Capture one transient secret-bearing delivery message."""

    def __init__(self, *, error: Exception | None = None) -> None:
        self.error = error
        self.messages: list[PasswordRecoveryDeliveryMessage] = []

    def deliver(self, message: PasswordRecoveryDeliveryMessage) -> None:
        self.messages.append(message)
        if self.error is not None:
            raise self.error


def _contact() -> VerifiedRecoveryContact:
    return VerifiedRecoveryContact.issue(
        contact_id="WILSYRECOVERYCONTACT-TEST",
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=DIGEST,
        verified_at=OBSERVED - timedelta(days=30),
    )


def _user(*, email: str = EMAIL, tenant_id: str = TENANT):
    return SimpleNamespace(id=PRINCIPAL, email=email, tenantId=tenant_id)


def _service(
    *,
    contact: VerifiedRecoveryContact | None = None,
    user=None,
    rate_gate: RateGateDouble | None = None,
    delivery: DeliveryDouble | None = None,
    capability_registry: CapabilityRegistryDouble | None = None,
    origin: str = "https://app.wilsy.example",
    ttl: timedelta = timedelta(minutes=30),
):
    contact_registry = ContactRegistryDouble(contact)
    capabilities = capability_registry or CapabilityRegistryDouble()
    auth = AuthRegistryDouble(user)
    rate = rate_gate or RateGateDouble()
    mail = delivery or DeliveryDouble()
    service = PasswordRecoveryRequestService(
        contact_registry=contact_registry,
        capability_registry=capabilities,
        auth_registry=auth,
        rate_limit_gate=rate,
        delivery_adapter=mail,
        public_reset_origin=origin,
        capability_ttl=ttl,
    )
    return service, contact_registry, capabilities, auth, rate, mail


def test_normalize_and_digest_are_deterministic_without_verifying_address() -> None:
    assert normalize_recovery_email("  Operator@Example.COM ") == EMAIL
    assert recovery_address_digest(EMAIL) == DIGEST
    with pytest.raises(PasswordRecoveryRequestServiceError) as error:
        normalize_recovery_email("not-an-email")
    assert str(error.value) == "RECOVERY_REQUEST_INVALID"


@pytest.mark.parametrize(
    "origin",
    [
        "http://app.wilsy.example",
        "https://user:secret@app.wilsy.example",
        "https://app.wilsy.example?host=evil",
        "https://app.wilsy.example#secret",
        " https://app.wilsy.example",
    ],
)
def test_constructor_rejects_untrusted_public_origins(origin: str) -> None:
    with pytest.raises(PasswordRecoveryRequestServiceError) as error:
        _service(contact=None, user=None, origin=origin)
    assert str(error.value) == "RECOVERY_PUBLIC_ORIGIN_INVALID"


@pytest.mark.parametrize(
    "ttl",
    [timedelta(0), timedelta(seconds=-1), timedelta(hours=24, seconds=1)],
)
def test_constructor_rejects_invalid_capability_ttl(ttl: timedelta) -> None:
    with pytest.raises(PasswordRecoveryRequestServiceError) as error:
        _service(contact=None, user=None, ttl=ttl)
    assert str(error.value) == "RECOVERY_TTL_INVALID"


def test_absent_verified_contact_is_generic_and_never_issues_or_delivers() -> None:
    service, contacts, capabilities, auth, rate, delivery = _service(
        contact=None,
        user=None,
    )

    result = service.request_password_reset(
        tenant_id=TENANT,
        email=EMAIL,
        observed_at=OBSERVED,
    )

    assert result == PasswordRecoveryRequestResult()
    assert result.__dict__ == {"accepted": True}
    assert contacts.calls == [{
        "tenant_id": TENANT,
        "channel": VerifiedRecoveryContactChannel.EMAIL,
        "address_digest": DIGEST,
    }]
    assert len(rate.calls) == 1
    assert rate.calls[0]["address_digest"] == DIGEST
    assert auth.calls == []
    assert capabilities.created == []
    assert capabilities.revoked == []
    assert delivery.messages == []


def test_current_principal_email_mismatch_is_generic_without_issuance() -> None:
    service, _contacts, capabilities, auth, _rate, delivery = _service(
        contact=_contact(),
        user=_user(email="changed@example.com"),
    )

    result = service.request_password_reset(
        tenant_id=TENANT,
        email=EMAIL,
        observed_at=OBSERVED,
    )

    assert result.accepted is True
    assert auth.calls == [PRINCIPAL]
    assert capabilities.created == []
    assert delivery.messages == []


def test_cross_tenant_principal_projection_is_generic_without_issuance() -> None:
    service, _contacts, capabilities, _auth, _rate, delivery = _service(
        contact=_contact(),
        user=_user(tenant_id="OTHER-TENANT"),
    )

    result = service.request_password_reset(
        tenant_id=TENANT,
        email=EMAIL,
        observed_at=OBSERVED,
    )

    assert result.accepted is True
    assert capabilities.created == []
    assert delivery.messages == []


def test_rate_limit_rejects_before_contact_lookup_and_delivery() -> None:
    rate = RateGateDouble(limited=True)
    service, contacts, capabilities, auth, _rate, delivery = _service(
        contact=_contact(),
        user=_user(),
        rate_gate=rate,
    )

    with pytest.raises(PasswordRecoveryRequestRateLimitedError) as error:
        service.request_password_reset(
            tenant_id=TENANT,
            email=EMAIL,
            observed_at=OBSERVED,
        )

    assert str(error.value) == "RECOVERY_REQUEST_RATE_LIMITED"
    assert len(rate.calls) == 1
    assert contacts.calls == []
    assert auth.calls == []
    assert capabilities.created == []
    assert delivery.messages == []


def test_verified_contact_issues_digest_only_capability_and_fragment_link() -> None:
    service, _contacts, capabilities, auth, rate, delivery = _service(
        contact=_contact(),
        user=_user(),
    )

    result = service.request_password_reset(
        tenant_id=TENANT,
        email="Operator@Example.COM",
        observed_at=OBSERVED,
    )

    assert result == PasswordRecoveryRequestResult()
    assert auth.calls == [PRINCIPAL]
    assert len(rate.calls) == 1
    assert len(capabilities.created) == 1
    capability = capabilities.created[0]
    assert capability.tenant_id == TENANT
    assert capability.principal_id == PRINCIPAL
    assert capability.issued_at == OBSERVED
    assert capability.expires_at == OBSERVED + timedelta(minutes=30)
    assert len(capability.token_digest) == 128
    assert len(delivery.messages) == 1

    message = delivery.messages[0]
    assert message.recipient_email == EMAIL
    parsed = urlsplit(message.reset_url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "app.wilsy.example"
    assert parsed.path == "/reset-password"
    assert parsed.query == ""
    fragment = parse_qs(parsed.fragment)
    assert fragment["tenant"] == [TENANT]
    raw_token = fragment["recovery"][0]
    assert raw_token
    assert hashlib.sha3_512(raw_token.encode("utf-8")).hexdigest() == capability.token_digest
    assert raw_token not in repr(capability)
    assert raw_token not in repr(result)
    assert capabilities.revoked == []


def test_delivery_failure_revokes_created_capability_and_raises_internal_error() -> None:
    delivery = DeliveryDouble(error=RuntimeError("mail unavailable"))
    service, _contacts, capabilities, _auth, _rate, _delivery = _service(
        contact=_contact(),
        user=_user(),
        delivery=delivery,
    )

    with pytest.raises(PasswordRecoveryRequestDependencyError) as error:
        service.request_password_reset(
            tenant_id=TENANT,
            email=EMAIL,
            observed_at=OBSERVED,
        )

    assert str(error.value) == "RECOVERY_DELIVERY_FAILED"
    assert len(capabilities.created) == 1
    assert capabilities.revoked == [(capabilities.created[0], OBSERVED)]
    assert len(delivery.messages) == 1


def test_delivery_failure_with_unconfirmed_revocation_fails_closed() -> None:
    capabilities = CapabilityRegistryDouble(revoke_error=RuntimeError("db unavailable"))
    delivery = DeliveryDouble(error=RuntimeError("mail unavailable"))
    service, _contacts, _capabilities, _auth, _rate, _delivery = _service(
        contact=_contact(),
        user=_user(),
        delivery=delivery,
        capability_registry=capabilities,
    )

    with pytest.raises(PasswordRecoveryRequestDependencyError) as error:
        service.request_password_reset(
            tenant_id=TENANT,
            email=EMAIL,
            observed_at=OBSERVED,
        )

    assert str(error.value) == "RECOVERY_DELIVERY_FAILED_REVOCATION_UNCONFIRMED"
    assert len(capabilities.created) == 1
    assert len(delivery.messages) == 1


def test_result_surface_never_contains_identity_delivery_or_capability_truth() -> None:
    result = PasswordRecoveryRequestResult()
    assert result.accepted is True
    assert set(result.__dict__) == {"accepted"}
    rendered = repr(result).lower()
    for forbidden in ("email", "tenant", "principal", "token", "delivery", "capability"):
        assert forbidden not in rendered


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_request_service.py
# VERSION: v1.0.0-R10E4-PASSWORD-RECOVERY-REQUEST-DIRECT-CERT
# AUTHORITY BOUNDARY: deterministic direct certificate only
# TENANT POSTURE: synthetic exact-tenant evidence; cross-tenant issuance rejected
# FAIL-CLOSED POSTURE: rate, dependency, delivery, and revocation failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
