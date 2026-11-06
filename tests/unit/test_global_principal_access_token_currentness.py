from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from tools.eos.api.exceptions import UnauthorizedAccessException
from tools.eos.auth import authentication
from tools.eos.auth.principal_status import PrincipalStatus


def _credentials() -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="signed-token")


def _payload() -> dict[str, Any]:
    return {
        "token_purpose": "ACCESS",
        "credential_revision": 7,
        "identity_id": "principal-global",
        "tenant_id": "tenant-exact",
        "roles": ["tenant_owner"],
        "permissions": [],
        "session_reference": "WILSYGLOBALSESSION-abc",
        "membership_revision": 3,
        "capacity_revision": 5,
        "workspace_id": "EXECUTIVE_COMMAND_CENTRE",
        "principal_scope": "GLOBAL",
    }


def test_global_access_token_requires_exact_current_session_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: dict[str, Any] = {}
    class Sessions:
        def is_session_current(self, **kwargs: Any) -> bool:
            observed.update(kwargs)
            return True
    monkeypatch.setattr(authentication, "verify_access_token", lambda _token: _payload())
    monkeypatch.setattr(authentication, "_resolve_authority", lambda _repo, _pid: SimpleNamespace(
        principal_id="principal-global", status=PrincipalStatus.ACTIVE
    ))
    monkeypatch.setattr(authentication, "GlobalPrincipalSessionAuthority", Sessions)

    identity = asyncio.run(authentication.get_current_identity(
        request=cast(Any, object()), credentials=_credentials(), api_key=None, repository=cast(Any, object())
    ))
    assert identity.identity_id == "principal-global"
    assert identity.tenant_id == "tenant-exact"
    assert identity.roles == ["tenant_owner"]
    assert identity.permissions == []
    assert identity.principal_scope == "GLOBAL"
    assert identity.workspace_id == "EXECUTIVE_COMMAND_CENTRE"
    assert identity.membership_revision == 3
    assert identity.capacity_revision == 5
    assert observed == {
        "principal_id": "principal-global",
        "tenant_id": "tenant-exact",
        "session_reference": "WILSYGLOBALSESSION-abc",
        "expected_business_role": "tenant_owner",
        "expected_workspace_id": "EXECUTIVE_COMMAND_CENTRE",
        "expected_credential_revision": 7,
        "expected_membership_revision": 3,
        "expected_capacity_revision": 5,
    }


def test_global_access_token_rejected_when_global_session_is_not_current(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Sessions:
        def is_session_current(self, **_kwargs: Any) -> bool:
            return False
    monkeypatch.setattr(authentication, "verify_access_token", lambda _token: _payload())
    monkeypatch.setattr(authentication, "_resolve_authority", lambda _repo, _pid: SimpleNamespace(
        principal_id="principal-global", status=PrincipalStatus.ACTIVE
    ))
    monkeypatch.setattr(authentication, "GlobalPrincipalSessionAuthority", Sessions)
    with pytest.raises(UnauthorizedAccessException):
        asyncio.run(authentication.get_current_identity(
            request=cast(Any, object()), credentials=_credentials(), api_key=None, repository=cast(Any, object())
        ))


def test_tenant_bound_access_token_keeps_legacy_revision_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload.pop("principal_scope")
    payload.pop("membership_revision")
    payload.pop("capacity_revision")
    payload.pop("workspace_id")
    payload["session_reference"] = "WILSYSESSION-legacy"
    calls: list[tuple[str, str]] = []

    class Registry:
        def get_credential_revision(self, tenant_id: str, principal_id: str) -> int:
            calls.append((tenant_id, principal_id))
            return 7

    monkeypatch.setattr(authentication, "verify_access_token", lambda _token: payload)
    monkeypatch.setattr(authentication, "_resolve_authority", lambda _repo, _pid: SimpleNamespace(
        principal_id="principal-global", status=PrincipalStatus.ACTIVE
    ))
    monkeypatch.setattr(authentication, "AuthRegistry", Registry)
    identity = asyncio.run(authentication.get_current_identity(
        request=cast(Any, object()), credentials=_credentials(), api_key=None, repository=cast(Any, object())
    ))
    assert identity.session_reference == "WILSYSESSION-legacy"
    assert calls == [("tenant-exact", "principal-global")]


def test_system_access_token_requires_durable_system_session_and_current_workforce_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []

    class Session:
        in_transaction = False
        def start_transaction(self):
            events.append("start")
            self.in_transaction = True
        def commit_transaction(self):
            events.append("commit")
            self.in_transaction = False
        def abort_transaction(self):
            events.append("abort")
            self.in_transaction = False
        def end_session(self):
            events.append("end")

    class Client:
        def start_session(self):
            return Session()

    class Authority:
        def __init__(self, *, sessions, authorizer):
            assert sessions is not None
            assert authorizer is not None
        def is_session_current(self, **kwargs):
            events.append("revalidate")
            assert kwargs["principal_id"] == "platform-responder"
            assert kwargs["session_reference"] == "WILSYS-SYSTEM-SESSION-abc"
            assert kwargs["expected_credential_revision"] == 12
            assert kwargs["session"].in_transaction is True
            return True

    payload = {
        "token_purpose": "ACCESS",
        "credential_revision": 12,
        "identity_id": "platform-responder",
        "tenant_id": "SYSTEM",
        "roles": ["SYSTEM_SERVICES"],
        "permissions": [],
        "session_reference": "WILSYS-SYSTEM-SESSION-abc",
        "workspace_id": "SYSTEM_SERVICES",
        "principal_scope": "SYSTEM",
    }
    authorizer = object()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(
        system_services_authorizer=authorizer,
    )))
    monkeypatch.setattr(authentication, "verify_access_token", lambda _token: payload)
    monkeypatch.setattr(authentication, "_resolve_authority", lambda _repo, _pid: SimpleNamespace(
        principal_id="platform-responder", status=PrincipalStatus.ACTIVE
    ))
    monkeypatch.setattr(authentication, "get_client", lambda: Client())
    monkeypatch.setattr(authentication, "get_database", lambda: {"global_principal_system_sessions": object()})
    monkeypatch.setattr(authentication, "GlobalPrincipalSystemSessionAuthority", Authority)

    identity = asyncio.run(authentication.get_current_identity(
        request=cast(Any, request),
        credentials=_credentials(),
        api_key=None,
        repository=cast(Any, object()),
    ))
    assert identity.identity_id == "platform-responder"
    assert identity.tenant_id == "SYSTEM"
    assert identity.roles == ["SYSTEM_SERVICES"]
    assert identity.permissions == []
    assert identity.session_reference == "WILSYS-SYSTEM-SESSION-abc"
    assert events == ["start", "revalidate", "commit", "end"]


def test_system_access_token_cannot_smuggle_tenant_or_role_claims(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "token_purpose": "ACCESS",
        "credential_revision": 12,
        "identity_id": "platform-responder",
        "tenant_id": "TENANT-FORGED",
        "roles": ["TENANT_OWNER"],
        "permissions": ["*"],
        "session_reference": "WILSYS-SYSTEM-SESSION-abc",
        "workspace_id": "SYSTEM_SERVICES",
        "principal_scope": "SYSTEM",
    }
    monkeypatch.setattr(authentication, "verify_access_token", lambda _token: payload)
    monkeypatch.setattr(authentication, "_resolve_authority", lambda _repo, _pid: SimpleNamespace(
        principal_id="platform-responder", status=PrincipalStatus.ACTIVE
    ))
    with pytest.raises(UnauthorizedAccessException):
        asyncio.run(authentication.get_current_identity(
            request=cast(Any, object()),
            credentials=_credentials(),
            api_key=None,
            repository=cast(Any, object()),
        ))
