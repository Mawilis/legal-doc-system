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
    assert observed == {
        "principal_id": "principal-global",
        "tenant_id": "tenant-exact",
        "session_reference": "WILSYGLOBALSESSION-abc",
        "expected_business_role": "tenant_owner",
        "expected_workspace_id": "EXECUTIVE_COMMAND_CENTRE",
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
