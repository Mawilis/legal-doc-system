"""WILSY OS authoritative MFA router certificate.

TITLE: Authentication Router Authoritative MFA Certificate
VERSION: v1.5.1-REQUIRED-ASGI-REQUEST-LOGIN-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies exact setup, reconciliation, verification, persistence, and
         bounded tenant-discovery behavior without a live database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_auth_router_authoritative_mfa.py
COLLABORATION / OWNERSHIP: Exercises tools.eos.api.auth_router with deterministic
                           registry and tenant doubles.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG:
  v1.5.1-REQUIRED-ASGI-REQUEST-LOGIN-CERT supplies the remaining direct MFA-reconciliation login Request.
  v1.5.0 supplies concrete Request doubles
  for every direct login invocation and isolates rate-gate behavior by test.
  v1.4.3 balances all synthetic ASGI Request casts for static type checking.
  v1.4.2 corrects the closing delimiter on the synthetic Request doubles.
  v1.4.1 explicitly typed the first synthetic Request double.
  v1.4.0-GLOBAL-PRINCIPAL-FAILURE-THROTTLE-HTTP-CERT certifies HTTP admission,
  failure-only recording, authenticated-email reset, generic 429 retry guidance,
  and fail-closed throttle persistence handling.
  v1.3.0-R10C2F8A1-AUTH-ROUTER-AUTHORITATIVE-MFA-CERT-METADATA-REPAIR —
  Preserves the F8A PRE_AUTH fixture reconciliation unchanged and repairs
  only its accidentally regressed certificate version lineage and metadata;
  no test or production semantics changed.
  v1.1.0-R10C2F8A-AUTH-ROUTER-AUTHORITATIVE-MFA-CERT-RECONCILIATION —
  Reconciles the deterministic registry fixture with the explicit PRE_AUTH
  issuer while retaining generic compatibility and all authority assertions.
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
from typing import Any, cast

import pytest
from fastapi import HTTPException, Request

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
        self.generic_issuer_calls: list[tuple[Any, ...]] = []
        self.pre_auth_issuer_calls: list[tuple[str, str, str, list[str]]] = []
        self.access_issuer_calls: list[tuple[Any, ...]] = []
        self.persisted = user.mfaRegistered

    def authenticate(self, _email: str, _password: str) -> SimpleNamespace:
        return self.user

    def get_otp_secret(self, _user_id: str) -> str | None:
        return self.secret

    def get_otp_uri(self, _user_id: str, _email: str) -> str:
        self.get_uri_calls += 1
        return "otpauth://totp/Wilsy%20OS"

    def generate_jwt(self, *_args: Any) -> str:
        self.generic_issuer_calls.append(_args)
        return "temporary-token"

    def generate_pre_auth_jwt(
        self,
        user_id: str,
        tenant_id: str,
        role: str,
        permissions: list[str],
    ) -> str:
        self.pre_auth_issuer_calls.append(
            (user_id, tenant_id, role, list(permissions))
        )
        return "temporary-token"

    def generate_access_jwt(self, *_args: Any, **_kwargs: Any) -> str:
        self.access_issuer_calls.append(_args)
        raise AssertionError("MFA challenge must not use ACCESS issuance")

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


def _http_request() -> Request:
    """Return a typed synthetic ASGI request for direct route-function tests."""
    return cast(Request, SimpleNamespace(client=SimpleNamespace(host="203.0.113.25")))


@pytest.fixture(autouse=True)
def _default_allow_rate_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep existing MFA-state tests independent of Mongo throttle persistence."""

    class _AllowGate:
        def require_allowed(self, **_kwargs: Any) -> None:
            return None

        def record_failure(self, **_kwargs: Any) -> None:
            return None

        def record_success(self, **_kwargs: Any) -> None:
            return None

    monkeypatch.setattr(auth_router, "PrincipalAuthenticationRateLimit", _AllowGate)


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

    response = _run(auth_router.login(AuthRequest(email="person@example.com", password="valid", tenant_id="TENANT-TEST"), _http_request()))

    assert response.status == expected_status
    assert bool(response.qrCode) is qr_expected
    if not qr_expected:
        assert registry.get_uri_calls == 0
    assert response.refreshToken is None
    assert response.tempToken == "temporary-token"
    assert registry.pre_auth_issuer_calls == [
        ("WILSYAUTH-test", "TENANT-TEST", "FIELD_DEPUTY", ["legal:read"])
    ]
    assert registry.generic_issuer_calls == []
    assert registry.access_issuer_calls == []
    assert registry.session_calls == 0



def _http_state_factor_session_adapter(
    registry: Any,
    user: Any,
) -> Any:
    """Test-only seam for separately certified factor-currentness composition."""
    return registry.create_session(user)


def test_login_rejects_a_tenant_other_than_the_discovered_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _Registry(_user(enrolled=True), "SECRET")
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    with pytest.raises(HTTPException) as error:
        _run(
            auth_router.login(
                AuthRequest(
                    email="person@example.com",
                    password="valid",
                    tenant_id="TENANT-OTHER",
                ),
                _http_request(),
            )
        )

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid credentials"
    assert registry.get_uri_calls == 0
    assert registry.session_calls == 0


def test_login_requires_tenant_discovery_before_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _Registry(_user(enrolled=True), "SECRET")
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    with pytest.raises(HTTPException) as error:
        _run(
            auth_router.login(
                AuthRequest(email="person@example.com", password="valid"),
                _http_request(),
            )
        )

    assert error.value.status_code == 400
    assert registry.get_uri_calls == 0
    assert registry.session_calls == 0


def test_legacy_otp_verification_persists_and_rereads_before_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _Registry(_user(enrolled=False), "SECRET")
    monkeypatch.setattr(
        auth_router,
        "_create_factor_current_session",
        _http_state_factor_session_adapter,
    )
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

    response = _run(auth_router.verify_otp(VerifyOTPRequest(email="person@example.com", code="123456", tenant_id="TENANT-TEST")))

    assert response.status == "AUTHENTICATED"
    assert events == ["update", "reread", "session"]
    assert registry.session_calls == 1


def test_reconciled_user_returns_normal_mfa_challenge_on_next_login(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _Registry(_user(enrolled=False), "SECRET")
    monkeypatch.setattr(
        auth_router,
        "_create_factor_current_session",
        _http_state_factor_session_adapter,
    )
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    _run(auth_router.verify_otp(VerifyOTPRequest(email="person@example.com", code="123456", tenant_id="TENANT-TEST")))
    response = _run(auth_router.login(AuthRequest(email="person@example.com", password="valid", tenant_id="TENANT-TEST"), _http_request()))

    assert response.status == "MFA_REQUIRED"
    assert response.qrCode is None
    assert registry.get_uri_calls == 0
    assert registry.pre_auth_issuer_calls == [
        ("WILSYAUTH-test", "TENANT-TEST", "FIELD_DEPUTY", ["legal:read"])
    ]
    assert registry.generic_issuer_calls == []
    assert registry.access_issuer_calls == []


def test_otp_verification_rejects_a_tenant_other_than_discovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _Registry(_user(enrolled=True), "SECRET")
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    with pytest.raises(HTTPException) as error:
        _run(
            auth_router.verify_otp(
                VerifyOTPRequest(
                    email="person@example.com",
                    code="123456",
                    tenant_id="TENANT-OTHER",
                )
            )
        )

    assert error.value.status_code == 401
    assert registry.session_calls == 0


def test_invalid_otp_fails_closed_without_session(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _Registry(_user(enrolled=True), "SECRET")
    registry.verify_otp = lambda *_args: False  # type: ignore[method-assign]
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    with pytest.raises(HTTPException) as error:
        _run(auth_router.verify_otp(VerifyOTPRequest(email="person@example.com", code="123456", tenant_id="TENANT-TEST")))

    assert error.value.status_code == 401
    assert registry.session_calls == 0


def test_setup_persistence_failure_never_creates_session(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _Registry(_user(enrolled=False), None)
    registry.secret = "SECRET"
    registry.update_user = lambda *_args, **_kwargs: None  # type: ignore[method-assign]
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)

    with pytest.raises(HTTPException) as error:
        _run(auth_router.validate_mfa_setup(VerifyOTPRequest(email="person@example.com", code="123456", tenant_id="TENANT-TEST")))

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


def test_discovery_canonical_not_found_is_bounded_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _TenantRegistry:
        @staticmethod
        def resolve_canonical_tenant(
            _reference: str,
            *,
            allow_alias: bool = False,
        ) -> None:
            assert allow_alias is True
            raise auth_router.TenantRegistryError(
                "TENANT_REGISTRY_CANONICAL_NOT_FOUND"
            )

    monkeypatch.setattr(auth_router, "TenantRegistry", _TenantRegistry)

    with pytest.raises(HTTPException) as error:
        _run(
            auth_router.discover(
                DiscoverRequest(alias="unknown-workspace")
            )
        )

    assert error.value.status_code == 404
    assert error.value.detail == "Tenant not found"


def test_discovery_canonical_registry_fault_remains_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _TenantRegistry:
        @staticmethod
        def resolve_canonical_tenant(
            _reference: str,
            *,
            allow_alias: bool = False,
        ) -> None:
            assert allow_alias is True
            raise auth_router.TenantRegistryError(
                "TENANT_REGISTRY_CANONICAL_CORRUPT"
            )

    monkeypatch.setattr(auth_router, "TenantRegistry", _TenantRegistry)

    with pytest.raises(HTTPException) as error:
        _run(
            auth_router.discover(
                DiscoverRequest(alias="corrupt-workspace")
            )
        )

    assert error.value.status_code == 500


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


def test_http_login_records_only_failed_credentials_and_resets_after_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _Registry(_user(enrolled=True), "SECRET")
    calls: list[tuple[str, str]] = []

    class _Gate:
        def require_allowed(self, **kwargs: Any) -> None:
            calls.append(("check", kwargs["email"]))

        def record_failure(self, **kwargs: Any) -> None:
            calls.append(("failure", kwargs["email"]))

        def record_success(self, **kwargs: Any) -> None:
            calls.append(("success", kwargs["email"]))

    monkeypatch.setattr(auth_router, "PrincipalAuthenticationRateLimit", _Gate)
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)
    http_request = cast(Request, SimpleNamespace(client=SimpleNamespace(host="203.0.113.25")))

    response = _run(
        auth_router.login(
            AuthRequest(email="person@example.com", password="valid", tenant_id="TENANT-TEST"),
            http_request,
        )
    )

    assert response.status == "MFA_REQUIRED"
    assert calls == [
        ("check", "person@example.com"),
        ("success", "person@example.com"),
    ]


def test_http_login_records_failed_password_without_logging_raw_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _Registry(_user(enrolled=True), "SECRET")
    registry.authenticate = lambda *_args: None  # type: ignore[method-assign]
    calls: list[tuple[str, str]] = []
    telemetry: list[tuple[Any, ...]] = []

    class _Gate:
        def require_allowed(self, **kwargs: Any) -> None:
            calls.append(("check", kwargs["email"]))

        def record_failure(self, **kwargs: Any) -> None:
            calls.append(("failure", kwargs["email"]))

        def record_success(self, **kwargs: Any) -> None:
            raise AssertionError("failed authentication must not reset email failures")

    monkeypatch.setattr(auth_router, "PrincipalAuthenticationRateLimit", _Gate)
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)
    monkeypatch.setattr(auth_router, "broadcast_telemetry", lambda *args: telemetry.append(args))
    http_request = cast(Request, SimpleNamespace(client=SimpleNamespace(host="203.0.113.25")))

    with pytest.raises(HTTPException) as error:
        _run(
            auth_router.login(
                AuthRequest(email="person@example.com", password="wrong", tenant_id="TENANT-TEST"),
                http_request,
            )
        )

    assert error.value.status_code == 401
    assert calls == [
        ("check", "person@example.com"),
        ("failure", "person@example.com"),
    ]
    assert "person@example.com" not in repr(telemetry)


def test_http_login_returns_generic_429_before_credential_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tools.eos.auth.principal_authentication_rate_limit import (
        PrincipalAuthenticationRateLimited,
    )

    registry = _Registry(_user(enrolled=True), "SECRET")

    class _Gate:
        def require_allowed(self, **_kwargs: Any) -> None:
            raise PrincipalAuthenticationRateLimited(120)

    monkeypatch.setattr(auth_router, "PrincipalAuthenticationRateLimit", _Gate)
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)
    http_request = cast(Request, SimpleNamespace(client=SimpleNamespace(host="203.0.113.25")))

    with pytest.raises(HTTPException) as error:
        _run(
            auth_router.login(
                AuthRequest(email="person@example.com", password="wrong", tenant_id="TENANT-TEST"),
                http_request,
            )
        )

    assert error.value.status_code == 429
    assert error.value.headers == {"Retry-After": "120"}
    assert registry.get_uri_calls == 0
    assert registry.session_calls == 0


def test_http_login_fails_closed_when_throttle_authority_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tools.eos.auth.principal_authentication_rate_limit import (
        PrincipalAuthenticationRateLimitUnavailable,
    )

    registry = _Registry(_user(enrolled=True), "SECRET")

    class _Gate:
        def require_allowed(self, **_kwargs: Any) -> None:
            raise PrincipalAuthenticationRateLimitUnavailable("RATE_STORE_DOWN")

    monkeypatch.setattr(auth_router, "PrincipalAuthenticationRateLimit", _Gate)
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)
    http_request = cast(Request, SimpleNamespace(client=SimpleNamespace(host="203.0.113.25")))

    with pytest.raises(HTTPException) as error:
        _run(
            auth_router.login(
                AuthRequest(email="person@example.com", password="valid", tenant_id="TENANT-TEST"),
                http_request,
            )
        )

    assert error.value.status_code == 503
    assert registry.pre_auth_issuer_calls == []
    assert registry.session_calls == 0


# ARTIFACT: tests/unit/test_auth_router_authoritative_mfa.py
# VERSION: v1.5.1-REQUIRED-ASGI-REQUEST-LOGIN-CERT
# AUTHORITY BOUNDARY: deterministic HTTP-state certificate only
# TENANT POSTURE: unknown aliases fail closed without directory enumeration
# FAIL-CLOSED POSTURE: persistence uncertainty cannot issue a session
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
