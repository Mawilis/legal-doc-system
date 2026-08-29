"""Unit certification for fail-closed authentication authority projection."""
import asyncio
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request
import pytest
from tools.eos.auth import authentication
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.api.exceptions import UnauthorizedAccessException

class Repository:
    def __init__(self, status): self.status = status
    def get(self, principal_id):
        from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
        if self.status is None: raise PrincipalAuthorityNotFoundError("absent")
        return PrincipalAuthority(principal_id, self.status, 0)

def credentials(): return HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

def run(repository, payload=None, api_key=None):
    authentication.verify_access_token = lambda _: payload
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
    return asyncio.run(authentication.get_current_identity(request, credentials(), api_key, repository))

def test_active_requires_durable_authority_and_projects_status(monkeypatch):
    payload = {"identity_id": "p", "tenant_id": "t"}
    value = run(Repository(PrincipalStatus.ACTIVE), payload)
    assert value.identity_id == "p" and value.status is PrincipalStatus.ACTIVE

@pytest.mark.parametrize("status", [PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED, None])
def test_non_active_or_absent_principal_denied(status):
    with pytest.raises(UnauthorizedAccessException): run(Repository(status), {"identity_id": "p", "tenant_id": "t"})

def test_missing_reference_and_invalid_credential_denied():
    with pytest.raises(UnauthorizedAccessException): run(Repository(PrincipalStatus.ACTIVE), {"tenant_id": "t"})
    with pytest.raises(UnauthorizedAccessException): run(Repository(PrincipalStatus.ACTIVE), None)

def test_no_fallbacks_or_api_key_bypass():
    with pytest.raises(UnauthorizedAccessException): run(Repository(PrincipalStatus.ACTIVE), {"tenant_id": "DEFAULT"})
    with pytest.raises(UnauthorizedAccessException): run(Repository(PrincipalStatus.ACTIVE), {"identity_id": "p", "tenant_id": "t"}, "master")
