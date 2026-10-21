"""P12C authenticated binding transport behavior certificate.

Tests exact identity forwarding, durable-source provenance, transaction
commit/rollback behavior and fail-closed HTTP translation.
No live database contact or independent legal authority.
"""
from __future__ import annotations
from typing import cast
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from tools.eos.api import legal_practitioner_matter_binding_router as api


def context():
    """Represent an already-authenticated dependency result."""
    return SimpleNamespace(
        tenant_id="tenant-A",
        identity=SimpleNamespace(identity_id="partner-A"),
    )


class Session:
    """Track lifecycle operations of an isolated fake transaction."""

    def __init__(self, fail_commit=False):
        self.in_transaction = False
        self.events = []
        self.fail_commit = fail_commit

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def start_transaction(self):
        self.in_transaction = True
        self.events.append("start")

    def commit_transaction(self):
        self.events.append("commit")
        if self.fail_commit:
            raise RuntimeError("COMMIT_FAILED")
        self.in_transaction = False

    def abort_transaction(self):
        self.events.append("abort")
        self.in_transaction = False


def test_commit_precedes_receipt(monkeypatch):
    session = Session()
    monkeypatch.setattr(
        api, "get_client",
        lambda: SimpleNamespace(start_session=lambda: session),
    )
    monkeypatch.setattr(api, "get_database", lambda: object())

    result = api._transaction(
        lambda tx, db: (tx.events.append("service"), {"ok": True})[1]
    )

    assert result == {"ok": True}
    assert session.events == ["start", "service", "commit"]


@pytest.mark.parametrize("fail_commit", [False, True])
def test_failure_never_returns_success(monkeypatch, fail_commit):
    session = Session(fail_commit=fail_commit)
    monkeypatch.setattr(
        api, "get_client",
        lambda: SimpleNamespace(start_session=lambda: session),
    )
    monkeypatch.setattr(api, "get_database", lambda: object())

    def callback(tx, db):
        if not fail_commit:
            raise RuntimeError("SERVICE_FAILED")
        return {"ok": True}

    with pytest.raises(HTTPException) as error:
        api._transaction(callback)

    assert error.value.status_code == 503
    assert session.events[-1] == "abort"
    assert session.in_transaction is False


def test_missing_database_fails_closed(monkeypatch):
    monkeypatch.setattr(api, "get_client", lambda: None)
    monkeypatch.setattr(api, "get_database", lambda: None)

    with pytest.raises(HTTPException) as error:
        api._transaction(lambda session, db: {"ok": True})

    assert error.value.status_code == 503


def test_grant_uses_durable_conflict_provenance(monkeypatch):
    seen = {}
    fingerprint = "a" * 128
    source = "b" * 128

    evidence = SimpleNamespace(
        tenant_id="tenant-A",
        case_matter_id="matter-A",
        practitioner_principal_id="lawyer-A",
        fingerprint=fingerprint,
        source_evidence_fingerprint=source,
    )
    disposition = SimpleNamespace(
        tenant_id="tenant-A",
        case_matter_id="matter-A",
        fingerprint=source,
        client_party_id="canonical-client",
        subject_identity_fingerprint="c" * 128,
    )

    monkeypatch.setattr(
        api, "_transaction", lambda callback: callback(None, object())
    )
    monkeypatch.setattr(
        api, "_collection", lambda database, name: name
    )
    monkeypatch.setattr(api, "get_by_id", lambda **kw: evidence)
    monkeypatch.setattr(
        api, "get_disposition_by_fingerprint",
        lambda *args, **kw: disposition,
    )

    def fake_grant(**kwargs):
        seen.update(kwargs)
        return SimpleNamespace(to_dict=lambda: {"status": "ACTIVE"})

    monkeypatch.setattr(api, "grant_binding", fake_grant)

    command = api.GrantPractitionerBindingCommand(
        case_matter_id="matter-A",
        practitioner_principal_id="lawyer-A",
        binding_id="binding-A",
        access_evidence_id="evidence-A",
        expected_access_evidence_fingerprint=fingerprint,
    )

    result = api.grant_practitioner_binding(
        command, cast(TenantAuthorizationContext, context()), None, None, None, None
    )

    assert result == {"status": "ACTIVE"}
    assert seen["tenant_id"] == "tenant-A"
    assert seen["authenticated_principal_id"] == "partner-A"
    assert seen["client_party_id"] == "canonical-client"
    assert seen["subject_identity_fingerprint"] == "c" * 128
    assert seen["granted_at"].tzinfo is not None


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", "tenant-B"),
        ("case_matter_id", "matter-B"),
        ("fingerprint", "d" * 128),
    ],
)
def test_grant_rejects_mismatched_disposition(
    monkeypatch, field, value
):
    fingerprint = "a" * 128
    source = "b" * 128

    evidence = SimpleNamespace(
        case_matter_id="matter-A",
        practitioner_principal_id="lawyer-A",
        fingerprint=fingerprint,
        source_evidence_fingerprint=source,
    )
    disposition = SimpleNamespace(
        tenant_id="tenant-A",
        case_matter_id="matter-A",
        fingerprint=source,
        client_party_id="client-A",
        subject_identity_fingerprint="c" * 128,
    )
    setattr(disposition, field, value)

    monkeypatch.setattr(
        api, "_transaction", lambda callback: callback(None, object())
    )
    monkeypatch.setattr(
        api, "_collection", lambda database, name: name
    )
    monkeypatch.setattr(api, "get_by_id", lambda **kw: evidence)
    monkeypatch.setattr(
        api, "get_disposition_by_fingerprint",
        lambda *args, **kw: disposition,
    )

    def forbidden_grant(**kwargs):
        pytest.fail("INVALID_PROVENANCE_REACHED_WRITE_SERVICE")

    monkeypatch.setattr(api, "grant_binding", forbidden_grant)

    command = api.GrantPractitionerBindingCommand(
        case_matter_id="matter-A",
        practitioner_principal_id="lawyer-A",
        binding_id="binding-A",
        access_evidence_id="evidence-A",
        expected_access_evidence_fingerprint=fingerprint,
    )

    with pytest.raises(HTTPException) as error:
        api.grant_practitioner_binding(
            command, cast(TenantAuthorizationContext, context()), None, None, None, None
        )
    assert error.value.status_code == 403


def test_revoke_uses_authenticated_principal(monkeypatch):
    seen = {}
    monkeypatch.setattr(
        api, "_transaction", lambda callback: callback(None, object())
    )
    monkeypatch.setattr(
        api, "_collection", lambda database, name: name
    )

    def fake_revoke(**kwargs):
        seen.update(kwargs)
        return SimpleNamespace(to_dict=lambda: {"status": "REVOKED"})

    monkeypatch.setattr(api, "revoke_binding", fake_revoke)

    command = api.RevokePractitionerBindingCommand(
        binding_id="binding-A",
        evidence_reference="revocation-A",
    )
    result = api.revoke_practitioner_binding(
        command, cast(TenantAuthorizationContext, context()), None, None, None, None
    )

    assert result == {"status": "REVOKED"}
    assert seen["authenticated_principal_id"] == "partner-A"
    assert seen["tenant_id"] == "tenant-A"
    assert seen["revoked_at"].tzinfo is not None


# ARTIFACT: test_legal_practitioner_matter_binding_http_behavior.py
# VERSION: v1.0.0-P12C-R4D-BEHAVIOR-CERTIFICATE
# AUTHORITY BOUNDARY: tests only; no legal content admission
# TENANT POSTURE: checks authenticated identity and scoped evidence
# FAIL-CLOSED POSTURE: invalid provenance and transactions reject
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
