"""Adversarial unit tests for global-principal session and refresh authority."""
from datetime import datetime, timezone
from typing import Any, cast
from types import SimpleNamespace

import pytest
from pymongo.errors import PyMongoError

from tools.eos.auth import global_principal_session_authority as authority_module
from tools.eos.auth.global_principal_session_authority import (
    GlobalPrincipalSessionAuthority,
    GlobalPrincipalSessionRejected,
    GlobalPrincipalSessionUnavailable,
)
from tools.eos.auth.membership_selection_challenge import SelectedMembershipContext
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus


class Transaction:
    in_transaction = True


class Collection:
    def __init__(self):
        self.rows = []

    def create_index(self, *args, **kwargs):
        return kwargs.get("name", "test-index")

    def insert_one(self, doc, session=None):
        self.rows.append(dict(doc))
        return SimpleNamespace(inserted_id=len(self.rows))

    def find_one(self, query, session=None):
        return next((dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items()
                    if not isinstance(v, dict) and k != "expires_at")
                    and (not isinstance(query.get("expires_at"), dict)
                    or row["expires_at"] > query["expires_at"]["$gt"])), None)

    def find_one_and_update(self, query, update, return_document=None, session=None):
        row = next((row for row in self.rows if all(row.get(k) == v for k, v in query.items()
                    if not isinstance(v, dict))
                    and row["expires_at"] > query["expires_at"]["$gt"]), None)
        if row is None:
            return None
        row.update(update["$set"])
        return dict(row)

    def update_one(self, query, update, upsert=False, session=None):
        row = next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)
        if row is None:
            return SimpleNamespace(matched_count=0)
        row.update(update["$set"])
        return SimpleNamespace(matched_count=1)

    def update_many(self, query, update, session=None):
        count = 0
        for row in self.rows:
            if all(row.get(k) == v for k, v in query.items()):
                row.update(update["$set"])
                count += 1
        return SimpleNamespace(modified_count=count)


class Authorities:
    def __init__(self):
        self.credential_revision = 2
        self.membership_revision = 3
        self.capacity_revision = 5
        self.principal_status = PrincipalStatus.ACTIVE
        self.membership_status = TenantMembershipStatus.ACTIVE
        self.capacity_status = TenantBusinessRoleStatus.ACTIVE

    def principal(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, status=self.principal_status)

    def credential(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id,
                               credential_revision=self.credential_revision, mfa_enabled=True)

    def membership(self, principal_id, tenant_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id,
                               revision=self.membership_revision, status=self.membership_status)

    def capacity(self, principal_id, tenant_id, role, *, session=None):
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id, business_role=role,
                               revision=self.capacity_revision, status=self.capacity_status)


def setup(monkeypatch):
    authorities = Authorities()
    sessions, refresh = Collection(), Collection()
    monkeypatch.setattr(
        "tools.eos.auth.global_principal_session_authority.create_access_token",
        lambda *args, **kwargs: "signed-access-token",
    )
    service = GlobalPrincipalSessionAuthority(
        sessions=cast(Any, sessions), refresh_tokens=cast(Any, refresh),
        principal_repository=SimpleNamespace(get=authorities.principal),
        credential_repository=SimpleNamespace(get_by_principal=authorities.credential),
        membership_repository=SimpleNamespace(resolve=authorities.membership),
        business_role_repository=SimpleNamespace(resolve_business_role=authorities.capacity),
        tenant_resolver=lambda tenant_id, session=None: SimpleNamespace(tenant_id=tenant_id),
    )
    selected = SelectedMembershipContext("principal-A", "tenant-A", "tenant_owner",
                                         "EXECUTIVE_COMMAND_CENTRE", 2, 3, 5)
    return service, authorities, sessions, refresh, selected


def issue(service, selected):
    return service.issue_after_mfa(selected, session=Transaction(),
                                   now=datetime(2026, 11, 3, tzinfo=timezone.utc))


def test_issue_persists_digest_only_and_binds_exact_authority(monkeypatch):
    service, _, sessions, refresh, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    assert receipt.session_reference == sessions.rows[0]["session_reference"]
    assert receipt.refresh_token not in str(refresh.rows[0])
    assert refresh.rows[0]["principal_id"] == "principal-A"
    assert refresh.rows[0]["tenant_id"] == "tenant-A"
    assert sessions.rows[0]["membership_revision"] == 3
    assert sessions.rows[0]["capacity_revision"] == 5


def test_session_persistence_failure_propagates_without_transaction_ownership(monkeypatch):
    service, _, _, _, selected = setup(monkeypatch)
    class BrokenSessions:
        def insert_one(self, *_args, **_kwargs):
            raise PyMongoError("synthetic persistence failure")
    cast(Any, service)._sessions = cast(Any, BrokenSessions())
    transaction = Transaction()
    with pytest.raises(GlobalPrincipalSessionUnavailable, match="PERSISTENCE_FAILED"):
        service.issue_after_mfa(selected, session=transaction)
    assert transaction.in_transaction is True


def test_issue_requires_caller_owned_transaction(monkeypatch):
    service, _, _, _, selected = setup(monkeypatch)
    with pytest.raises(GlobalPrincipalSessionRejected, match="TRANSACTION_REQUIRED"):
        service.issue_after_mfa(selected, session=SimpleNamespace(in_transaction=False))


def test_refresh_is_single_use_and_rotates(monkeypatch):
    service, _, _, refresh, selected = setup(monkeypatch)
    first = issue(service, selected)
    rotated = service.rotate_refresh_token(
        first.refresh_token, session=Transaction(),
        now=datetime(2026, 11, 3, 0, 1, tzinfo=timezone.utc))
    assert rotated.session_reference == first.session_reference
    assert rotated.refresh_token != first.refresh_token
    assert refresh.rows[0]["consumed_at"] is not None
    with pytest.raises(GlobalPrincipalSessionRejected, match="GLOBAL_REFRESH_INVALID"):
        service.rotate_refresh_token(first.refresh_token, session=Transaction(),
                                     now=datetime(2026, 11, 3, 0, 2, tzinfo=timezone.utc))


def test_credential_revision_change_rejects_refresh(monkeypatch):
    service, authorities, _, refresh, selected = setup(monkeypatch)
    first = issue(service, selected)
    authorities.credential_revision = 3
    with pytest.raises(GlobalPrincipalSessionRejected, match="CREDENTIAL_STALE"):
        service.rotate_refresh_token(first.refresh_token, session=Transaction(),
                                     now=datetime(2026, 11, 3, 0, 1, tzinfo=timezone.utc))
    assert len(refresh.rows) == 1


def test_membership_and_capacity_revision_changes_invalidate_currentness(monkeypatch):
    service, authorities, _, _, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    authorities.membership_revision = 4
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-A",
                                          session_reference=receipt.session_reference)
    authorities.membership_revision = 3
    authorities.capacity_revision = 6
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-A",
                                          session_reference=receipt.session_reference)


def test_access_token_credential_epoch_must_match_persisted_session(monkeypatch):
    service, _, _, _, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    assert not service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
        expected_credential_revision=99,
    )


def test_workspace_mapping_change_invalidates_existing_global_session(monkeypatch):
    service, _, _, _, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    monkeypatch.setattr(authority_module, "resolve_workspace_id", lambda _role: "DIFFERENT_WORKSPACE")
    assert not service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )


def test_cross_tenant_session_lookup_and_revocation_are_isolated(monkeypatch):
    service, _, sessions, refresh, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-B",
                                          session_reference=receipt.session_reference)
    assert service.revoke_session(principal_id="principal-A", tenant_id="tenant-A",
                                  session_reference=receipt.session_reference, session=Transaction())
    assert sessions.rows[0]["revoked_at"] is not None
    assert refresh.rows[0]["revoked_at"] is not None
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-A",
                                          session_reference=receipt.session_reference)
