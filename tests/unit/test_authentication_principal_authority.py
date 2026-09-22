"""Unit certification for fail-closed authentication authority projection.

TITLE: Authentication Principal Authority Certificate
VERSION: v1.0.0-R10C2F9A-AUTHENTICATION-PRINCIPAL-AUTHORITY-CERT-RECONCILIATION
AUTHORITY: Test-only evidence for canonical principal and durable revision gates.
EPITOME: Certifies that protected authentication reaches canonical principal
    authority and exact durable credential-revision comparison.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authentication_principal_authority.py
COLLABORATION / OWNERSHIP: Test-only certificate; authentication.py and its
    canonical AuthRegistry dependency remain read-only in this gate.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
    v1.0.0-R10C2F9A-AUTHENTICATION-PRINCIPAL-AUTHORITY-CERT-RECONCILIATION
    reconciles existing principal-authority fixtures with the protected ACCESS
    token contract and records the durable credential-revision read.
SECURITY/PRIVACY POSTURE: Synthetic identifiers only; no secrets or durable data.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic tenant context is passed only to the durable-read seam.
AUTHORITY BOUNDARY: This certificate observes production authentication seams; it
    does not create principal, credential, tenant, session, JWT, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
"""
import asyncio
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request
import pytest
from tools.eos.auth import authentication
from tools.eos.auth.jwt_provider import TokenPurpose
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.api.exceptions import UnauthorizedAccessException

class Repository:
    def __init__(self, status, calls=None):
        self.status = status
        self.calls = calls if calls is not None else []

    def get(self, principal_id):
        self.calls.append(principal_id)
        from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
        if self.status is None: raise PrincipalAuthorityNotFoundError("absent")
        return PrincipalAuthority(principal_id, self.status, 0)

class CredentialRegistry:
    def __init__(self, calls, revision=0):
        self.calls = calls
        self.revision = revision

    def get_credential_revision(self, tenant_id, principal_id):
        self.calls.append((tenant_id, principal_id))
        return self.revision

def credentials(): return HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

def access_payload(**claims):
    return {
        "token_purpose": TokenPurpose.ACCESS.value,
        "credential_revision": 0,
        **claims,
    }

def run(monkeypatch, repository, payload=None, api_key=None, registry_calls=None):
    durable_calls = registry_calls if registry_calls is not None else []
    monkeypatch.setattr(authentication, "verify_access_token", lambda _: payload)
    monkeypatch.setattr(
        authentication,
        "AuthRegistry",
        lambda: CredentialRegistry(durable_calls),
    )
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
    return asyncio.run(authentication.get_current_identity(request, credentials(), api_key, repository))

def test_active_requires_durable_authority_and_projects_status(monkeypatch):
    authority_calls = []
    durable_calls = []
    payload = access_payload(identity_id="p", tenant_id="t")
    value = run(
        monkeypatch,
        Repository(PrincipalStatus.ACTIVE, authority_calls),
        payload,
        registry_calls=durable_calls,
    )
    assert value.identity_id == "p" and value.status is PrincipalStatus.ACTIVE
    assert authority_calls == ["p"]
    assert durable_calls == [("t", "p")]

@pytest.mark.parametrize("status", [PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED, None])
def test_non_active_or_absent_principal_denied(status, monkeypatch):
    authority_calls = []
    with pytest.raises(UnauthorizedAccessException):
        run(
            monkeypatch,
            Repository(status, authority_calls),
            access_payload(identity_id="p", tenant_id="t"),
        )
    assert authority_calls == ["p"]

def test_missing_reference_and_invalid_credential_denied(monkeypatch):
    authority_calls = []
    with pytest.raises(UnauthorizedAccessException):
        run(
            monkeypatch,
            Repository(PrincipalStatus.ACTIVE, authority_calls),
            access_payload(tenant_id="t"),
        )
    with pytest.raises(UnauthorizedAccessException):
        run(monkeypatch, Repository(PrincipalStatus.ACTIVE, authority_calls), None)
    assert authority_calls == []

def test_no_fallbacks_or_api_key_bypass(monkeypatch):
    authority_calls = []
    durable_calls = []
    with pytest.raises(UnauthorizedAccessException):
        run(
            monkeypatch,
            Repository(PrincipalStatus.ACTIVE, authority_calls),
            access_payload(tenant_id="DEFAULT"),
            registry_calls=durable_calls,
        )
    with pytest.raises(UnauthorizedAccessException):
        run(
            monkeypatch,
            Repository(PrincipalStatus.ACTIVE, authority_calls),
            access_payload(identity_id="p", tenant_id="t"),
            "master",
            registry_calls=durable_calls,
        )
    assert authority_calls == []
    assert durable_calls == []

# ARTIFACT: test_authentication_principal_authority.py
# VERSION: v1.0.0-R10C2F9A-AUTHENTICATION-PRINCIPAL-AUTHORITY-CERT-RECONCILIATION
# AUTHORITY BOUNDARY: principal authority and durable credential-revision evidence only
# TENANT POSTURE: synthetic tenant context; no persistence or cross-tenant access
# FAIL-CLOSED POSTURE: invalid, non-ACCESS, non-active, absent, and bypass attempts deny
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
