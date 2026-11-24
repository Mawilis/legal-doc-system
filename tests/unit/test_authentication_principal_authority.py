"""Unit certification for fail-closed authentication authority projection.

TITLE: Authentication Principal Authority Certificate
VERSION: v1.2.1-ENV-INDEPENDENT-TIMING-TEST
AUTHORITY: Test-only evidence for canonical principal and durable revision gates.
EPITOME: Certifies that protected authentication reaches canonical principal
    authority and exact durable credential-revision comparison.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authentication_principal_authority.py
COLLABORATION / OWNERSHIP: Test-only certificate; authentication.py and its
    canonical AuthRegistry dependency remain read-only in this gate.
CERTIFICATION / UPDATE DATE: 2026-11-24
CHANGELOG:
    2026-11-24 v1.2.1-ENV-INDEPENDENT-TIMING-TEST explicitly removes
    inherited opt-in diagnostic flag for disabled-telemetry assertion, then
    enables it inside the test. Shell instrumentation must never affect the
    same test's deterministic privacy and stage verification.
    2026-11-24 v1.2.0-NONBLOCKING-AUTHENTICATION-WORKER-CERT verifies
    synchronous principal and credential currentness occur outside the event
    loop while request-local opaque timing correlation reaches both worker
    operations unchanged. Every existing fail-closed assertion remains intact.
    2026-11-17 v1.1.1-TYPED-TEST-DOUBLE-CERT explicitly types the
    synthetic repository at the authentication test seam for Pyright;
    runtime assertions and production authority are unchanged.
    2026-11-15 v1.1.0-SCOPED-REQUEST-TIMING-CERT verifies disabled diagnostic
    silence and enabled privacy-safe authentication timing without changing
    credential or principal authority outcomes.
    v1.0.0-R10C2F9A-AUTHENTICATION-PRINCIPAL-AUTHORITY-CERT-RECONCILIATION
    reconciles existing principal-authority fixtures with the protected ACCESS
    token contract and records the durable credential-revision read.
SECURITY / PRIVACY POSTURE: Synthetic identifiers only; no secrets or durable data.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic tenant context is passed only to the durable-read seam.
AUTHORITY BOUNDARY: This certificate observes production authentication seams; it
    does not create principal, credential, tenant, session, JWT, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
"""
import asyncio
import logging
import threading
from typing import Any, cast
from types import SimpleNamespace
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request
import pytest
from tools.eos.auth import authentication
from tools.eos.auth.jwt_provider import TokenPurpose
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
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
    return asyncio.run(authentication.get_current_identity(request, credentials(), api_key, cast(PrincipalAuthorityRepository, repository)))



def test_durable_identity_reads_run_off_event_loop_with_same_request_trace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A slow PyMongo read must not monopolize asyncio or lose trace scope."""

    expected_trace = "TRC-MWHCMCDJ-HR4HXJ"
    caller_thread = threading.get_ident()
    observed: list[tuple[str, int, str]] = []

    class WorkerRepository(Repository):
        def get(self, principal_id: str) -> PrincipalAuthority:
            observed.append((
                "principal", threading.get_ident(),
                authentication.current_request_timing_correlation(),
            ))
            return super().get(principal_id)

    class WorkerRegistry(CredentialRegistry):
        def get_credential_revision(self, tenant_id: str, principal_id: str) -> int:
            observed.append((
                "credential", threading.get_ident(),
                authentication.current_request_timing_correlation(),
            ))
            return super().get_credential_revision(tenant_id, principal_id)

    monkeypatch.setattr(
        authentication, "verify_access_token",
        lambda _token: access_payload(identity_id="p", tenant_id="t"),
    )
    revision_calls: list[tuple[str, str]] = []
    monkeypatch.setattr(
        authentication, "AuthRegistry",
        lambda: WorkerRegistry(revision_calls),
    )
    request = Request({
        "type": "http", "method": "GET", "path": "/api/my-work",
        "headers": [(b"x-trace-id", expected_trace.encode("ascii"))],
    })
    identity = asyncio.run(authentication.get_current_identity(
        request, credentials(), None,
        cast(PrincipalAuthorityRepository, WorkerRepository(PrincipalStatus.ACTIVE)),
    ))
    assert identity.identity_id == "p"
    assert revision_calls == [("t", "p")]
    assert [stage for stage, _thread_id, _trace in observed] == [
        "principal", "credential",
    ]
    assert all(thread_id != caller_thread for _, thread_id, _ in observed)
    assert all(trace == expected_trace for _, _, trace in observed)


def test_active_requires_durable_authority_and_projects_status(monkeypatch):
    authority_calls = []
    durable_calls = []
    payload = access_payload(identity_id="p", tenant_id="t", session_reference="WILSYSESSION-test")
    value = run(
        monkeypatch,
        Repository(PrincipalStatus.ACTIVE, authority_calls),
        payload,
        registry_calls=durable_calls,
    )
    assert value.identity_id == "p" and value.status is PrincipalStatus.ACTIVE
    assert value.session_reference == "WILSYSESSION-test"
    assert authority_calls == ["p"]
    assert durable_calls == [("t", "p")]


def test_request_timing_is_opt_in_and_excludes_credential_and_identity_data(
    caplog, monkeypatch
):
    monkeypatch.delenv("WILSY_MY_WORK_TIMING", raising=False)
    payload = access_payload(
        identity_id="principal-private",
        tenant_id="tenant-private",
        session_reference="WILSYSESSION-private",
    )
    repository = Repository(PrincipalStatus.ACTIVE)
    monkeypatch.setattr(authentication, "verify_access_token", lambda _: payload)
    monkeypatch.setattr(authentication, "AuthRegistry", lambda: CredentialRegistry([]))
    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"x-trace-id", b"TRC-MWHCMCDJ-HR4HXJ")],
    })
    caplog.set_level(logging.INFO, logger="WilsyOS.Auth.Authentication")

    value = asyncio.run(
        authentication.get_current_identity(request, credentials(), None, cast(PrincipalAuthorityRepository, repository))
    )
    assert value.identity_id == "principal-private"
    assert not [
        record for record in caplog.records
        if record.getMessage().startswith("WILSY_REQUEST_TIMING")
    ]

    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    value = asyncio.run(
        authentication.get_current_identity(request, credentials(), None, cast(PrincipalAuthorityRepository, repository))
    )
    assert value.identity_id == "principal-private"
    events = [
        record.getMessage() for record in caplog.records
        if record.getMessage().startswith("WILSY_REQUEST_TIMING")
    ]
    assert any("trace_id=TRC-MWHCMCDJ-HR4HXJ" in event for event in events)
    assert any("stage=AUTH_ACCESS_TOKEN_VERIFICATION" in event for event in events)
    assert any("stage=AUTH_PRINCIPAL_CURRENTNESS" in event for event in events)
    assert any("stage=AUTHENTICATION_TOTAL" in event for event in events)
    serialized = "\n".join(events)
    for private_value in (
        "principal-private",
        "tenant-private",
        "WILSYSESSION-private",
        "Bearer token",
    ):
        assert private_value not in serialized

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



def _system_auth_request():
    app = SimpleNamespace(
        state=SimpleNamespace(system_services_authorizer=object())
    )
    return Request({
        "type": "http",
        "method": "GET",
        "path": "/system-services/workspace-bootstrap",
        "headers": [],
        "app": app,
    })


class _SystemSession:
    def __init__(self):
        self.in_transaction = False
        self.aborted = False
        self.committed = False
        self.ended = False

    def start_transaction(self):
        self.in_transaction = True

    def abort_transaction(self):
        self.aborted = True
        self.in_transaction = False

    def commit_transaction(self):
        self.committed = True
        self.in_transaction = False

    def end_session(self):
        self.ended = True


class _SystemClient:
    def __init__(self, session):
        self.session = session

    def start_session(self):
        return self.session


class _SystemDatabase:
    def __getitem__(self, _name):
        return object()


def _system_access_payload():
    return access_payload(
        identity_id="system-principal",
        tenant_id="SYSTEM",
        principal_scope="SYSTEM",
        session_reference="WILSYS-SYSTEM-SESSION-test",
        workspace_id="SYSTEM_SERVICES",
        roles=["SYSTEM_SERVICES"],
        permissions=[],
    )


def test_system_session_authority_outage_is_503_not_invalid_credential(monkeypatch):
    from tools.eos.auth.global_principal_system_session_authority import (
        GlobalPrincipalSystemSessionAuthority,
        GlobalPrincipalSystemSessionUnavailable,
    )

    session = _SystemSession()

    class UnavailableAuthority:
        def __init__(self, *, sessions, authorizer):
            assert sessions is not None
            assert authorizer is not None

        def is_session_current(self, **_kwargs):
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_AUTHORITY_OFFLINE")

    monkeypatch.setattr(authentication, "verify_access_token", lambda _: _system_access_payload())
    monkeypatch.setattr(authentication, "get_client", lambda: _SystemClient(session))
    monkeypatch.setattr(authentication, "get_database", lambda: _SystemDatabase())
    monkeypatch.setattr(authentication, "GlobalPrincipalSystemSessionAuthority", UnavailableAuthority)

    with pytest.raises(HTTPException) as raised:
        asyncio.run(authentication.get_current_identity(
            _system_auth_request(),
            credentials(),
            None,
            cast(Any, Repository(PrincipalStatus.ACTIVE)),
        ))
    assert raised.value.status_code == 503
    assert session.aborted and session.ended
    assert not session.committed


def test_system_session_rejection_remains_401_and_aborts(monkeypatch):
    from tools.eos.auth.global_principal_system_session_authority import (
        GlobalPrincipalSystemSessionRejected,
    )

    session = _SystemSession()

    class RejectedAuthority:
        def __init__(self, *, sessions, authorizer):
            assert sessions is not None
            assert authorizer is not None

        def is_session_current(self, **_kwargs):
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_SESSION_REVOKED")

    monkeypatch.setattr(authentication, "verify_access_token", lambda _: _system_access_payload())
    monkeypatch.setattr(authentication, "get_client", lambda: _SystemClient(session))
    monkeypatch.setattr(authentication, "get_database", lambda: _SystemDatabase())
    monkeypatch.setattr(authentication, "GlobalPrincipalSystemSessionAuthority", RejectedAuthority)

    with pytest.raises(UnauthorizedAccessException):
        asyncio.run(authentication.get_current_identity(
            _system_auth_request(),
            credentials(),
            None,
            cast(Any, Repository(PrincipalStatus.ACTIVE)),
        ))
    assert session.aborted and session.ended
    assert not session.committed

# ARTIFACT: test_authentication_principal_authority.py
# VERSION: v1.2.0-NONBLOCKING-AUTHENTICATION-WORKER-CERT
# AUTHORITY BOUNDARY: principal authority and durable credential-revision evidence only
# TENANT POSTURE: synthetic tenant context; no persistence or cross-tenant access
# FAIL-CLOSED POSTURE: invalid, non-ACCESS, non-active, absent, and bypass attempts deny
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
