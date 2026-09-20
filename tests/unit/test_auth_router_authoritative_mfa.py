"""WILSY OS authoritative MFA router certificate.

TITLE: Authentication Router Authoritative MFA Certificate
VERSION: v1.2.1-PYRIGHT-CLOSURE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies exact setup, reconciliation, verification, persistence, and
         bounded tenant-discovery behavior without a live database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_auth_router_authoritative_mfa.py
COLLABORATION / OWNERSHIP: Exercises tools.eos.api.auth_router with deterministic
                           registry and tenant doubles.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG:
  v1.2.1-PYRIGHT-CLOSURE-CERT — Aligns the deterministic registry double's
  reread return annotation with its fail-closed inactive state.
  v1.1.0-AUTHORITATIVE-MFA-ROUTING-CERT — Added next-login reconciliation
  convergence and invalid-OTP fail-closed session assertions.
  v1.0.0-AUTHORITATIVE-MFA-ROUTING-CERT — Initial focused certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No real credentials, OTP secrets, tokens, or MongoDB.
TENANT BOUNDARY: Discovery returns only the exact registry match.
AUTHORITY BOUNDARY: HTTP-state translation only; AuthRegistry owns durable auth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

from tools.eos.api import auth_router
from tools.eos.saas.domain.auth import AuthRequest, DiscoverRequest, VerifyOTPRequest


def _user(*, enrolled: bool, user_id: str = "WILSYAUTH-test") -> SimpleNamespace:
    return SimpleNamespace(
        id=user_id,
        email="person@example.com",
        firstName="Test",
        lastName="Person",
        role="FIELD_DEPUTY",
        permissions=["legal:read"],
        tenantId="TENANT-TEST",
        mfaRegistered=enrolled,
        hasSignedCovenant=True,
    )


class _Registry:
    def __init__(self, user: SimpleNamespace, secret: str | None = None) -> None:
        self.user = user
        self.secret = secret
        self.get_uri_calls = 0
        self.update_calls = 0
        self.reread_calls = 0
        self.session_calls = 0
        self.persisted = user.mfaRegistered

    def authenticate(self, _email: str, _password: str) -> SimpleNamespace:
        return self.user

    def get_otp_secret(self, _user_id: str) -> str | None:
        return self.secret

    def get_otp_uri(self, _user_id: str, _email: str) -> str:
        self.get_uri_calls += 1
        return "otpauth://totp/Wilsy%20OS"

    def generate_jwt(self, *_args: Any) -> str:
        return "temporary-token"

    def verify_otp(self, _user_id: str, _code: str) -> bool:
        return True

    def update_user(self, _user_id: str, **kwargs: Any) -> SimpleNamespace | None:
        self.update_calls += 1
        self.persisted = bool(kwargs["mfaRegistered"])
        self.user.mfaRegistered = self.persisted
        return self.user

    def get_user_by_email(self, _email: str) -> SimpleNamespace:
        return self.user

    def get_user_by_id(self, _user_id: str) -> SimpleNamespace | None:
        self.reread_calls += 1
        return self.user if self.persisted else None

    def create_session(self, _user: SimpleNamespace) -> SimpleNamespace:
        self.session_calls += 1
        return SimpleNamespace(token="session-token")


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


@pytest.mark.parametrize(
    ("enrolled", "secret", "expected_status", "qr_expected"),
    [
        (True, "SECRET", "MFA_REQUIRED", False),
        (False, "SECRET", "MFA_RECONCILIATION_REQUIRED", False),
        (False, None, "MFA_SETUP", True),
    ],
)
def test_login_exposes_exact_authoritative_mfa_state(
    monkeypatch: pytest.MonkeyPatch,
    enrolled: bool,
    secret: str | None,
    expected_status: str,
    qr_expected: bool,
) -> None:
    registry = _Registry(_user(enrolled=enrolled), secret)
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    response = _run(auth_router.login(AuthRequest(email="person@example.com", password="valid")))

    assert response.status == expected_status
    assert bool(response.qrCode) is qr_expected
    if not qr_expected:
        assert registry.get_uri_calls == 0
    assert response.refreshToken is None


def test_legacy_otp_verification_persists_and_rereads_before_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _Registry(_user(enrolled=False), "SECRET")
    events: list[str] = []
    original_update = registry.update_user
    original_reread = registry.get_user_by_id
    original_session = registry.create_session

    def update(*args: Any, **kwargs: Any) -> Any:
        events.append("update")
        return original_update(*args, **kwargs)

    def reread(*args: Any, **kwargs: Any) -> Any:
        events.append("reread")
        return original_reread(*args, **kwargs)

    def session(*args: Any, **kwargs: Any) -> Any:
        events.append("session")
        return original_session(*args, **kwargs)

    registry.update_user = update  # type: ignore[method-assign]
    registry.get_user_by_id = reread  # type: ignore[method-assign]
    registry.create_session = session  # type: ignore[method-assign]
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    response = _run(auth_router.verify_otp(VerifyOTPRequest(email="person@example.com", code="123456")))

    assert response.status == "AUTHENTICATED"
    assert events == ["update", "reread", "session"]
    assert registry.session_calls == 1


def test_reconciled_user_returns_normal_mfa_challenge_on_next_login(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _Registry(_user(enrolled=False), "SECRET")
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    _run(auth_router.verify_otp(VerifyOTPRequest(email="person@example.com", code="123456")))
    response = _run(auth_router.login(AuthRequest(email="person@example.com", password="valid")))

    assert response.status == "MFA_REQUIRED"
    assert response.qrCode is None
    assert registry.get_uri_calls == 0


def test_invalid_otp_fails_closed_without_session(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _Registry(_user(enrolled=True), "SECRET")
    registry.verify_otp = lambda *_args: False  # type: ignore[method-assign]
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    with pytest.raises(HTTPException) as error:
        _run(auth_router.verify_otp(VerifyOTPRequest(email="person@example.com", code="123456")))

    assert error.value.status_code == 401
    assert registry.session_calls == 0


def test_setup_persistence_failure_never_creates_session(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _Registry(_user(enrolled=False), None)
    registry.secret = "SECRET"
    registry.update_user = lambda *_args, **_kwargs: None  # type: ignore[method-assign]
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    with pytest.raises(HTTPException) as error:
        _run(auth_router.validate_mfa_setup(VerifyOTPRequest(email="person@example.com", code="123456")))

    assert error.value.status_code == 500
    assert registry.session_calls == 0


def test_discovery_has_no_unknown_alias_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    class _TenantRegistry:
        @staticmethod
        def get_tenant_by_alias(_alias: str) -> None:
            return None

    monkeypatch.setattr(auth_router, "TenantRegistry", _TenantRegistry)
    with pytest.raises(HTTPException) as error:
        _run(auth_router.discover(DiscoverRequest(alias="unknown-workspace")))
    assert error.value.status_code == 404


def test_discovery_projects_only_server_issued_tenant_identity_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    organization = SimpleNamespace(
        organization_name="Acme Display",
        legal_name="Acme Legal Holdings (Pty) Ltd",
        regions=["Africa"],
        plan=SimpleNamespace(value="ENTERPRISE"),
    )
    tenant = SimpleNamespace(
        tenant_id="TENANT-ACME",
        alias="acme",
        organization=organization,
        status="ACTIVE",
        verified=True,
    )

    class _TenantRegistry:
        @staticmethod
        def get_tenant_by_alias(_alias: str) -> SimpleNamespace:
            return tenant

    monkeypatch.setattr(auth_router, "TenantRegistry", _TenantRegistry)
    response = _run(auth_router.discover(DiscoverRequest(alias="acme")))

    assert response["tenant"] == {
        "tenantId": "TENANT-ACME",
        "alias": "acme",
        "name": "Acme Display",
        "region": "Africa",
        "plan": "ENTERPRISE",
        "status": "ACTIVE",
        "legalName": "Acme Legal Holdings (Pty) Ltd",
        "verified": True,
    }


def test_discovery_does_not_infer_missing_legal_name_or_verification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    organization = SimpleNamespace(
        organization_name="Display Only",
        legal_name=None,
        regions=[],
        plan=SimpleNamespace(value="COMMUNITY"),
    )
    tenant = SimpleNamespace(
        tenant_id="TENANT-DISPLAY",
        alias="display",
        organization=organization,
        status="ACTIVE",
    )

    class _TenantRegistry:
        @staticmethod
        def get_tenant_by_alias(_alias: str) -> SimpleNamespace:
            return tenant

    monkeypatch.setattr(auth_router, "TenantRegistry", _TenantRegistry)
    response = _run(auth_router.discover(DiscoverRequest(alias="display")))

    assert "legalName" not in response["tenant"]
    assert "verified" not in response["tenant"]


def test_direct_terminal_or_financial_authority_is_not_exposed() -> None:
    source = auth_router.__file__
    assert source is not None
    text = open(source, encoding="utf-8").read()
    assert "ServiceExecution" not in text
    assert "ReturnOfService" not in text
    assert "refreshToken=" not in text


"""
ARTIFACT: tests/unit/test_auth_router_authoritative_mfa.py
VERSION: v1.2.1-PYRIGHT-CLOSURE-CERT
AUTHORITY BOUNDARY: deterministic HTTP-state certificate only
TENANT POSTURE: unknown aliases fail closed without directory enumeration
FAIL-CLOSED POSTURE: persistence uncertainty cannot issue a session
FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
END OF WILSY OS SOVEREIGN ARTIFACT
"""
