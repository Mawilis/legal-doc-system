from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.global_principal_system_session_authority import (
    GlobalPrincipalSystemMfaChallengeService,
    GlobalPrincipalSystemSessionAuthority,
    GlobalPrincipalSystemSessionUnavailable,
    QUEUE_READ_PERMISSION,
    SYSTEM_ROLE,
    SYSTEM_SCOPE_MARKER,
    SYSTEM_WORKSPACE_ID,
)


NOW = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)


def test_system_mfa_challenge_is_principal_scoped_and_consumed_once():
    collection = Mock()
    service = GlobalPrincipalSystemMfaChallengeService(collection=collection)
    session = SimpleNamespace(in_transaction=True)
    token, expires_at = service.issue(
        principal_id="principal-system",
        credential_revision=8,
        session=session,
        now=NOW,
    )
    inserted = collection.insert_one.call_args.args[0]
    assert token.startswith("sysmfa_")
    assert inserted["principal_id"] == "principal-system"
    assert inserted["credential_revision"] == 8
    assert inserted["expires_at"] == expires_at
    assert inserted["consumed_at"] is None
    assert collection.insert_one.call_args.kwargs["session"] is session

    collection.find_one.return_value = {
        "principal_id": "principal-system",
        "credential_revision": 8,
    }
    context = service.get_factor_context(token, session=session, now=NOW)
    assert context.principal_id == "principal-system"
    assert context.credential_revision == 8

    collection.update_one.return_value = SimpleNamespace(modified_count=1)
    service.consume(
        token,
        principal_id="principal-system",
        credential_revision=8,
        session=session,
        now=NOW,
    )
    query = collection.update_one.call_args.args[0]
    assert query["principal_id"] == "principal-system"
    assert query["credential_revision"] == 8
    assert query["consumed_at"] is None
    assert collection.update_one.call_args.kwargs["session"] is session


def test_system_mfa_challenge_rejects_replay_and_foreign_principal():
    service = GlobalPrincipalSystemMfaChallengeService(collection=Mock())
    session = SimpleNamespace(in_transaction=True)
    collection = service._store()
    collection.find_one.return_value = None
    with pytest.raises(Exception, match="SYSTEM_MFA_CHALLENGE_INVALID_OR_EXPIRED"):
        service.get_factor_context("sysmfa_invalid", session=session, now=NOW)

    collection.update_one.return_value = SimpleNamespace(modified_count=0)
    with pytest.raises(Exception, match="SYSTEM_MFA_CHALLENGE_ALREADY_CONSUMED"):
        service.consume(
            "sysmfa_invalid",
            principal_id="foreign-principal",
            credential_revision=8,
            session=session,
            now=NOW,
        )


def test_system_session_issuance_requires_current_permission_and_platform_workforce(monkeypatch):
    principal_repository = Mock()
    principal_repository.get.return_value = SimpleNamespace(status=PrincipalStatus.ACTIVE)
    credential_repository = Mock()
    credential_repository.get_by_principal.return_value = SimpleNamespace(
        credential_revision=8,
        mfa_enabled=True,
    )
    authorizer = Mock()
    sessions = Mock()
    monkeypatch.setattr(
        "tools.eos.auth.global_principal_system_session_authority.create_access_token",
        lambda claims, **kwargs: (
            "signed-system-token"
            if claims["principal_scope"] == "SYSTEM"
            and claims["tenant_id"] == SYSTEM_SCOPE_MARKER
            and claims["workspace_id"] == SYSTEM_WORKSPACE_ID
            and claims["roles"] == [SYSTEM_ROLE]
            and claims["permissions"] == []
            else (_ for _ in ()).throw(AssertionError("invalid SYSTEM token projection"))
        ),
    )
    authority = GlobalPrincipalSystemSessionAuthority(
        sessions=sessions,
        refresh_tokens=Mock(),
        principal_repository=principal_repository,
        credential_repository=credential_repository,
        authorizer=authorizer,
    )
    session = SimpleNamespace(in_transaction=True)
    receipt = authority.issue_after_mfa(
        "principal-system",
        8,
        session=session,
        now=NOW,
    )
    assert receipt.access_token == "signed-system-token"
    assert receipt.principal_id == "principal-system"
    assert receipt.session_reference.startswith("WILSYS-SYSTEM-SESSION-")
    authorizer.require.assert_called_once_with(
        principal_id="principal-system",
        permission_id=QUEUE_READ_PERMISSION,
        session=session,
    )
    document = sessions.insert_one.call_args.args[0]
    assert document["principal_id"] == "principal-system"
    assert document["credential_revision"] == 8
    assert document["revoked_at"] is None
    assert sessions.insert_one.call_args.kwargs["session"] is session


def test_system_session_issuance_fails_closed_without_authorizer():
    principal_repository = Mock()
    principal_repository.get.return_value = SimpleNamespace(status=PrincipalStatus.ACTIVE)
    credential_repository = Mock()
    credential_repository.get_by_principal.return_value = SimpleNamespace(
        credential_revision=8,
        mfa_enabled=True,
    )
    authority = GlobalPrincipalSystemSessionAuthority(
        sessions=Mock(),
        principal_repository=principal_repository,
        credential_repository=credential_repository,
    )
    with pytest.raises(GlobalPrincipalSystemSessionUnavailable, match="SYSTEM_AUTHORIZER_UNAVAILABLE"):
        authority.issue_after_mfa(
            "principal-system",
            8,
            session=SimpleNamespace(in_transaction=True),
            now=NOW,
        )


def test_system_session_currentness_revalidates_authority_and_revocation():
    sessions = Mock()
    sessions.find_one.return_value = {"session_reference": "WILSYS-SYSTEM-SESSION-x"}
    principal_repository = Mock()
    principal_repository.get.return_value = SimpleNamespace(status=PrincipalStatus.ACTIVE)
    credential_repository = Mock()
    credential_repository.get_by_principal.return_value = SimpleNamespace(
        credential_revision=8,
        mfa_enabled=True,
    )
    authorizer = Mock()
    authority = GlobalPrincipalSystemSessionAuthority(
        sessions=sessions,
        principal_repository=principal_repository,
        credential_repository=credential_repository,
        authorizer=authorizer,
    )
    session = SimpleNamespace(in_transaction=True)
    assert authority.is_session_current(
        principal_id="principal-system",
        session_reference="WILSYS-SYSTEM-SESSION-x",
        expected_credential_revision=8,
        session=session,
        now=NOW,
    ) is True
    authorizer.require.assert_called_once()
    sessions.find_one.return_value = None
    assert authority.is_session_current(
        principal_id="principal-system",
        session_reference="WILSYS-SYSTEM-SESSION-x",
        expected_credential_revision=8,
        session=session,
        now=NOW,
    ) is False


def test_system_session_revocation_is_scoped_to_exact_principal_and_reference():
    sessions = Mock()
    sessions.update_one.return_value = SimpleNamespace(modified_count=1)
    authority = GlobalPrincipalSystemSessionAuthority(sessions=sessions, refresh_tokens=Mock())
    session = SimpleNamespace(in_transaction=True)
    assert authority.revoke(
        principal_id="principal-system",
        session_reference="WILSYS-SYSTEM-SESSION-x",
        session=session,
        now=NOW,
    ) is True
    query = sessions.update_one.call_args.args[0]
    assert query == {
        "principal_id": "principal-system",
        "session_reference": "WILSYS-SYSTEM-SESSION-x",
        "revoked_at": None,
    }


def test_system_refresh_rotation_consumes_old_bearer_and_issues_one_successor(monkeypatch):
    principal_repository = Mock()
    principal_repository.get.return_value = SimpleNamespace(status=PrincipalStatus.ACTIVE)
    credential_repository = Mock()
    credential_repository.get_by_principal.return_value = SimpleNamespace(
        credential_revision=8,
        mfa_enabled=True,
    )
    authorizer = Mock()
    sessions = Mock()
    refresh_tokens = Mock()
    refresh_tokens.find_one_and_update.return_value = {
        "principal_id": "principal-system",
        "credential_revision": 8,
        "session_reference": "WILSYS-SYSTEM-SESSION-current",
    }
    sessions.find_one.return_value = {
        "principal_id": "principal-system",
        "credential_revision": 8,
        "session_reference": "WILSYS-SYSTEM-SESSION-current",
        "expires_at": NOW.replace(year=NOW.year + 1, tzinfo=None),
    }
    monkeypatch.setattr(
        "tools.eos.auth.global_principal_system_session_authority.create_access_token",
        lambda claims, **_kwargs: (
            "rotated-access-token"
            if claims["principal_scope"] == "SYSTEM"
            else (_ for _ in ()).throw(AssertionError("non-SYSTEM token"))
        ),
    )
    authority = GlobalPrincipalSystemSessionAuthority(
        sessions=sessions,
        refresh_tokens=refresh_tokens,
        principal_repository=principal_repository,
        credential_repository=credential_repository,
        authorizer=authorizer,
    )
    session = SimpleNamespace(in_transaction=True)
    receipt = authority.rotate_refresh_token(
        "sysrefresh-current",
        session=session,
        now=NOW,
    )
    assert receipt.access_token == "rotated-access-token"
    assert receipt.refresh_token.startswith("sysrefresh_")
    assert receipt.refresh_token != "sysrefresh-current"
    assert receipt.refresh_expires_at.tzinfo is timezone.utc
    query = refresh_tokens.find_one_and_update.call_args.args[0]
    assert query["token_digest"]
    assert query["consumed_at"] is None
    assert query["revoked_at"] is None
    assert refresh_tokens.insert_one.call_count == 1
    assert refresh_tokens.insert_one.call_args.kwargs["session"] is session
    authorizer.require.assert_called_once()
