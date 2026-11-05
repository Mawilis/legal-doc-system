from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from starlette.requests import Request

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)

from tools.eos.auth.global_principal_mfa_enrollment_service import (
    GlobalPrincipalMfaEnrollmentCodeRejected,
)
from tools.eos.api.global_principal_auth_router import (
    GlobalCredentialRequest,
    GlobalMembershipSelectionRequest,
    GlobalMfaVerificationRequest,
    GlobalMfaEnrollmentStartRequest,
    GlobalMfaEnrollmentConfirmRequest,
    GlobalMfaLegacyMigrationRequest,
    start_global_mfa_enrollment,
    confirm_global_mfa_enrollment,
    migrate_legacy_global_mfa_factor,
    global_login,
    logout_global_session,
    router,
    select_membership,
    verify_global_mfa,
)


def _request() -> Request:
    app = FastAPI()
    app.state.global_principal_auth_indexes_ready = True
    app.state.global_principal_session_indexes_ready = True
    app.state.global_principal_mfa_factor_indexes_ready = True
    app.state.global_principal_totp_verifier = None
    return Request({"type": "http", "app": app, "headers": []})


def test_global_mfa_route_fails_closed_without_kms_factor_verifier() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(verify_global_mfa(
            GlobalMfaVerificationRequest(mfa_challenge="x" * 48, code="123456"),
            _request(),
        ))
    assert error.value.status_code == 503
    assert error.value.detail == "GLOBAL_MFA_KEY_SERVICE_UNAVAILABLE"


def test_global_logout_does_not_revoke_a_legacy_tenant_session() -> None:
    identity = SimpleNamespace(
        identity_id="principal",
        tenant_id="tenant",
        session_reference="WILSYSESSION-legacy",
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(logout_global_session(identity=identity))
    assert error.value.status_code == 409


def test_global_auth_routes_are_mounted_under_one_explicit_prefix() -> None:
    paths = {getattr(route, "path", None) for route in router.routes}
    assert paths == {
        "/auth/global/login",
        "/auth/global/membership-options",
        "/auth/global/select-membership",
        "/auth/global/verify-mfa",
        "/auth/global/refresh",
        "/auth/global/logout",
        "/auth/global/mfa/enrollment/start",
        "/auth/global/mfa/enrollment/confirm",
        "/auth/global/mfa/migrate-legacy",
    }


class _Session:
    def __init__(self) -> None:
        self.in_transaction = True
        self.committed = False
        self.ended = False

    def commit_transaction(self) -> None:
        self.committed = True
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.in_transaction = False

    def end_session(self) -> None:
        self.ended = True


def _request_with_state(**state_values):
    app = FastAPI()
    for key, value in state_values.items():
        setattr(app.state, key, value)
    return Request({
        "type": "http",
        "app": app,
        "headers": [],
        "client": ("127.0.0.1", 5000),
    })


def test_global_login_issues_tenant_neutral_selection_and_current_membership_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    class RateGate:
        def require_allowed(self, **_kwargs):
            return None
        def record_success(self, **_kwargs):
            return None
    class ChallengeService:
        def issue_membership_selection_challenge(self, **kwargs):
            assert kwargs["principal_id"] == "principal-global"
            assert kwargs["credential_revision"] == 7
            assert kwargs["session"] is session
            return SimpleNamespace(
                challenge_token="selection-token",
                expires_at=SimpleNamespace(isoformat=lambda: "2026-11-03T12:05:00+00:00"),
            )
    page = SimpleNamespace(
        memberships=(
            SimpleNamespace(
                tenant_id="tenant-a",
                membership_revision=3,
                capacities=(
                    SimpleNamespace(
                        business_role="tenant_owner",
                        workspace_id="EXECUTIVE_COMMAND_CENTRE",
                        business_role_revision=5,
                    ),
                ),
            ),
        ),
        next_cursor=None,
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.PrincipalAuthenticationRateLimit",
        RateGate,
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.authenticate_global_principal",
        lambda **_kwargs: SimpleNamespace(
            principal_id="principal-global", credential_revision=7, mfa_enabled=True
        ),
    )
    class FactorCollection:
        def find_one(self, query, *, projection, session):
            assert query["principal_id"] == "principal-global"
            assert query["credential_revision"] == 7
            assert query["status"] == "ACTIVE"
            assert projection == {"principal_id": 1}
            assert session.in_transaction is True
            return {"principal_id": "principal-global"}
    class Database:
        def __getitem__(self, _name):
            return FactorCollection()
    database = Database()
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router._begin_transaction",
        lambda: (session, database),
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.MembershipSelectionChallengeService",
        ChallengeService,
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.build_membership_selection_page",
        lambda **kwargs: page if kwargs["principal_id"] == "principal-global" and kwargs["session"] is session else None,
    )
    response = asyncio.run(global_login(
        GlobalCredentialRequest(email="person@example.com", password="ValidPassword!123"),
        _request_with_state(
            global_principal_auth_indexes_ready=True,
            global_principal_mfa_factor_indexes_ready=True,
            global_principal_totp_verifier=object(),
        ),
    ))
    assert response["status"] == "MEMBERSHIP_SELECTION_REQUIRED"
    assert response["selection_challenge"] == "selection-token"
    assert response["memberships"][0]["tenant_id"] == "tenant-a"
    assert response["memberships"][0]["capacities"][0]["business_role"] == "tenant_owner"
    assert session.committed and session.ended


def test_membership_selection_route_accepts_only_explicit_tenant_and_capacity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    observed = {}
    class ChallengeService:
        def select_membership_and_issue_mfa_challenge(self, **kwargs):
            observed.update(kwargs)
            return SimpleNamespace(
                challenge_token="mfa-token",
                expires_at=SimpleNamespace(isoformat=lambda: "2026-11-03T12:05:00+00:00"),
                tenant_id=kwargs["tenant_id"],
                business_role=kwargs["business_role"],
                workspace_id="EXECUTIVE_COMMAND_CENTRE",
            )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router._begin_transaction",
        lambda: (session, object()),
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.MembershipSelectionChallengeService",
        ChallengeService,
    )
    response = asyncio.run(select_membership(
        GlobalMembershipSelectionRequest(
            selection_challenge="selection-token",
            tenant_id="tenant-a",
            business_role="tenant_owner",
        ),
        _request_with_state(
            global_principal_auth_indexes_ready=True,
            global_principal_session_indexes_ready=True,
        ),
    ))
    assert response["status"] == "MFA_REQUIRED"
    assert response["mfa_challenge"] == "mfa-token"
    assert observed == {
        "selection_challenge_token": "selection-token",
        "tenant_id": "tenant-a",
        "business_role": "tenant_owner",
        "session": session,
    }
    assert session.committed and session.ended


def test_global_login_requires_migrated_current_mfa_factor_before_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    class RateGate:
        def require_allowed(self, **_kwargs):
            return None
        def record_success(self, **_kwargs):
            return None
    class FactorCollection:
        def find_one(self, _query, *, projection, session):
            assert projection == {"principal_id": 1}
            assert session.in_transaction is True
            return None
    class Database:
        def __getitem__(self, _name):
            return FactorCollection()
    class ChallengeService:
        def issue_membership_selection_challenge(self, **_kwargs):
            raise AssertionError("no selection challenge before factor migration")
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.PrincipalAuthenticationRateLimit",
        RateGate,
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.authenticate_global_principal",
        lambda **_kwargs: SimpleNamespace(
            principal_id="principal-global", credential_revision=7, mfa_enabled=True
        ),
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router._begin_transaction",
        lambda: (session, Database()),
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.MembershipSelectionChallengeService",
        ChallengeService,
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(global_login(
            GlobalCredentialRequest(email="person@example.com", password="ValidPassword!123"),
            _request_with_state(
                global_principal_auth_indexes_ready=True,
                global_principal_mfa_factor_indexes_ready=True,
                global_principal_totp_verifier=object(),
            ),
        ))
    assert error.value.status_code == 409
    assert error.value.detail == "GLOBAL_MFA_FACTOR_MIGRATION_REQUIRED"
    assert session.in_transaction is False
    assert session.ended


def test_global_login_routes_membership_free_principal_through_current_system_authority_and_mfa(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()

    class RateGate:
        def require_allowed(self, **_kwargs):
            return None
        def record_success(self, **_kwargs):
            return None

    class FactorCollection:
        def find_one(self, query, *, projection, session):
            assert query["principal_id"] == "platform-responder"
            assert query["credential_revision"] == 12
            assert query["status"] == "ACTIVE"
            assert projection == {"principal_id": 1}
            return {"principal_id": "platform-responder"}

    class Database:
        def __getitem__(self, _name):
            return FactorCollection()

    class SystemChallenge:
        def __init__(self, *, collection):
            assert collection is not None
        def issue(self, **kwargs):
            assert kwargs["principal_id"] == "platform-responder"
            assert kwargs["credential_revision"] == 12
            assert kwargs["session"] is session
            return "sysmfa-one-time", NOW + timedelta(minutes=5)

    class Authorizer:
        def require(self, **kwargs):
            assert kwargs["principal_id"] == "platform-responder"
            assert kwargs["permission_id"] == "system_services:queue:read"
            assert kwargs["session"] is session

    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.PrincipalAuthenticationRateLimit",
        RateGate,
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.authenticate_global_principal",
        lambda **_kwargs: SimpleNamespace(
            principal_id="platform-responder",
            credential_revision=12,
            mfa_enabled=True,
        ),
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router._begin_transaction",
        lambda: (session, Database()),
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.build_membership_selection_page",
        lambda **_kwargs: SimpleNamespace(memberships=(), next_cursor=None),
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.GlobalPrincipalSystemMfaChallengeService",
        SystemChallenge,
    )
    response = asyncio.run(global_login(
        GlobalCredentialRequest(email="platform@example.com", password="ValidPassword!123"),
        _request_with_state(
            global_principal_auth_indexes_ready=True,
            global_principal_mfa_factor_indexes_ready=True,
            global_principal_system_session_indexes_ready=True,
            global_principal_totp_verifier=object(),
            system_services_authority_ready=True,
            system_services_case_indexes_ready=True,
            system_services_authorizer=Authorizer(),
        ),
    ))
    assert response["status"] == "MFA_REQUIRED"
    assert response["scope"] == "SYSTEM"
    assert response["mfa_challenge"] == "sysmfa-one-time"
    assert response["workspace_id"] == "SYSTEM_SERVICES"
    assert "tenant_id" not in response
    assert session.committed and session.ended


def test_system_mfa_verification_consumes_challenge_and_issues_session_in_same_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    events = []

    class RateGate:
        def require_allowed(self, **_kwargs):
            return None
        def record_success(self, **_kwargs):
            return None

    class ChallengeService:
        def __init__(self, *, collection):
            assert collection is not None
        def get_factor_context(self, token, *, session, now):
            assert token == "sysmfa-valid"
            assert session is session_ref
            return SimpleNamespace(principal_id="platform-responder", credential_revision=12)
        def consume(self, token, **kwargs):
            events.append(("consume", kwargs["session"]))
            assert token == "sysmfa-valid"
            assert kwargs["principal_id"] == "platform-responder"
            assert kwargs["credential_revision"] == 12

    session_ref = session

    class CredentialRepository:
        @staticmethod
        def get_by_principal(principal_id, *, session):
            assert principal_id == "platform-responder"
            assert session is session_ref
            return SimpleNamespace(normalized_email="platform@example.com")

    class Verifier:
        def verify(self, **kwargs):
            assert kwargs["principal_id"] == "platform-responder"
            assert kwargs["credential_revision"] == 12
            assert kwargs["session"] is session_ref
            return True

    class SystemSessionAuthority:
        def __init__(self, *, sessions, refresh_tokens, authorizer):
            assert sessions is not None
            assert refresh_tokens is not None
            assert authorizer is not None
        def issue_after_mfa(self, principal_id, credential_revision, *, session, now):
            events.append(("issue", session))
            assert principal_id == "platform-responder"
            assert credential_revision == 12
            assert session is session_ref
            return SimpleNamespace(
                access_token="system-access",
                refresh_token="sysrefresh-rotatable",
                principal_id=principal_id,
                access_expires_at=NOW,
                refresh_expires_at=NOW,
            )

    class Database:
        def __getitem__(self, _name):
            return object()

    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router._begin_transaction",
        lambda: (session, Database()),
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.PrincipalAuthenticationRateLimit",
        RateGate,
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.PrincipalCredentialRepository",
        CredentialRepository,
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.GlobalPrincipalSystemMfaChallengeService",
        ChallengeService,
    )
    monkeypatch.setattr(
        "tools.eos.api.global_principal_auth_router.GlobalPrincipalSystemSessionAuthority",
        SystemSessionAuthority,
    )
    response = asyncio.run(verify_global_mfa(
        GlobalMfaVerificationRequest(mfa_challenge="sysmfa-valid", code="123456"),
        _request_with_state(
            global_principal_auth_indexes_ready=True,
            global_principal_session_indexes_ready=True,
            global_principal_system_session_indexes_ready=True,
            global_principal_mfa_factor_indexes_ready=True,
            global_principal_totp_verifier=Verifier(),
            system_services_authorizer=object(),
        ),
    ))
    assert response["status"] == "AUTHENTICATED"
    assert response["scope"] == "SYSTEM"
    assert response["access_token"] == "system-access"
    assert response["principal_id"] == "platform-responder"
    assert "tenant_id" not in response
    assert events == [("consume", session), ("issue", session)]
    assert session.committed and session.ended
