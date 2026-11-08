"""Disposable replica-set certification for global session/refresh authority."""
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pymongo import MongoClient

from tools.eos.auth import global_principal_session_authority as authority_module
from tools.eos.auth.global_principal_session_authority import (
    GlobalPrincipalSessionAuthority,
    GlobalPrincipalSessionRejected,
    SESSION_COLLECTION,
    REFRESH_COLLECTION,
)
from tools.eos.auth.membership_selection_challenge import SelectedMembershipContext
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus


class Authorities:
    credential_revision = 2
    membership_revision = 3
    capacity_revision = 5
    membership_status = TenantMembershipStatus.ACTIVE
    capacity_status = TenantBusinessRoleStatus.ACTIVE

    def get_principal(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, status=PrincipalStatus.ACTIVE)

    def get_credential(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id,
                               credential_revision=self.credential_revision, mfa_enabled=True)

    def get_membership(self, principal_id, tenant_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id,
                               revision=self.membership_revision, status=self.membership_status)

    def get_capacity(self, principal_id, tenant_id, role, *, session=None):
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id, business_role=role,
                               revision=self.capacity_revision, status=self.capacity_status)


@pytest.fixture()
def mongo_authority(monkeypatch):
    uri = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI")
    if not uri:
        pytest.fail("TEST_GLOBAL_PRINCIPAL_MONGO_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    expected_replica_set = os.getenv(
        "TEST_GLOBAL_PRINCIPAL_MONGO_REPLICA_SET", "wilsyGlobalPrincipalCertRS"
    )
    actual_replica_set = client.admin.command("hello").get("setName")
    if actual_replica_set != expected_replica_set:
        client.close()
        pytest.fail(
            f"wrong certification replica set: expected {expected_replica_set!r}, "
            f"received {actual_replica_set!r}"
        )
    database_name = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_DATABASE")
    if database_name != "wilsy_global_principal_mfa_cert":
        client.close()
        pytest.fail(
            "TEST_GLOBAL_PRINCIPAL_MONGO_DATABASE must be "
            "'wilsy_global_principal_mfa_cert'"
        )
    db = client[database_name]
    suffix = uuid.uuid4().hex
    sessions = db[f"{SESSION_COLLECTION}_cert_{suffix}"]
    refresh = db[f"{REFRESH_COLLECTION}_cert_{suffix}"]
    GlobalPrincipalSessionAuthority.ensure_indexes(sessions, refresh)
    monkeypatch.setattr(authority_module, "create_access_token",
                        lambda *args, **kwargs: "synthetic-signed-access-token")
    authorities = Authorities()
    service = GlobalPrincipalSessionAuthority(
        sessions=sessions, refresh_tokens=refresh,
        principal_repository=SimpleNamespace(get=authorities.get_principal),
        credential_repository=SimpleNamespace(get_by_principal=authorities.get_credential),
        membership_repository=SimpleNamespace(resolve=authorities.get_membership),
        business_role_repository=SimpleNamespace(resolve_business_role=authorities.get_capacity),
        tenant_resolver=lambda tenant_id, session=None: SimpleNamespace(tenant_id=tenant_id),
    )
    try:
        yield client, db, service, authorities, sessions, refresh
    finally:
        sessions.drop()
        refresh.drop()
        client.close()


def selected(tenant="tenant-A"):
    return SelectedMembershipContext("principal-A", tenant, "tenant_owner",
                                     "EXECUTIVE_COMMAND_CENTRE", 2, 3, 5)


def issue(service, client, context=None):
    with client.start_session() as session:
        session.start_transaction()
        receipt = service.issue_after_mfa(context or selected(), session=session,
                                          now=datetime(2026, 11, 3, tzinfo=timezone.utc))
        session.commit_transaction()
        return receipt


def test_replica_set_atomic_issue_commit_and_abort(mongo_authority):
    client, _db, service, _auth, sessions, refresh = mongo_authority
    with client.start_session() as session:
        session.start_transaction()
        service.issue_after_mfa(selected(), session=session,
                                now=datetime(2026, 11, 3, tzinfo=timezone.utc))
        session.abort_transaction()
    assert sessions.count_documents({}) == 0
    assert refresh.count_documents({}) == 0
    receipt = issue(service, client)
    assert sessions.count_documents({"session_reference": receipt.session_reference}) == 1
    assert refresh.count_documents({"session_reference": receipt.session_reference}) == 1


def test_replica_set_refresh_rotation_replay_and_abort_rollback(mongo_authority):
    client, _db, service, _auth, sessions, refresh = mongo_authority
    first = issue(service, client)
    with client.start_session() as session:
        session.start_transaction()
        service.rotate_refresh_token(first.refresh_token, session=session,
                                     now=datetime(2026, 11, 3, 0, 1, tzinfo=timezone.utc))
        session.abort_transaction()
    assert refresh.count_documents({"consumed_at": None}) == 1
    with client.start_session() as session:
        session.start_transaction()
        rotated = service.rotate_refresh_token(first.refresh_token, session=session,
                                               now=datetime(2026, 11, 3, 0, 2, tzinfo=timezone.utc))
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(GlobalPrincipalSessionRejected):
            service.rotate_refresh_token(first.refresh_token, session=session,
                                         now=datetime(2026, 11, 3, 0, 3, tzinfo=timezone.utc))
        session.abort_transaction()
    assert refresh.count_documents({"consumed_at": None}) == 1
    assert refresh.count_documents({"token_digest": {"$exists": True}}) == 2
    assert rotated.refresh_token != first.refresh_token


def test_replica_set_revision_change_revokes_currentness_and_blocks_refresh(mongo_authority):
    client, _db, service, authorities, _sessions, _refresh = mongo_authority
    receipt = issue(service, client)
    authorities.membership_revision = 4
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-A",
                                          session_reference=receipt.session_reference)
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(GlobalPrincipalSessionRejected):
            service.rotate_refresh_token(receipt.refresh_token, session=session,
                                         now=datetime(2026, 11, 3, 0, 1, tzinfo=timezone.utc))
        session.abort_transaction()


def test_replica_set_cross_tenant_isolation_and_exact_revocation(mongo_authority):
    client, _db, service, _auth, sessions, refresh = mongo_authority
    receipt = issue(service, client)
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-B",
                                          session_reference=receipt.session_reference)
    with client.start_session() as session:
        session.start_transaction()
        assert not service.revoke_session(principal_id="principal-A", tenant_id="tenant-B",
                                          session_reference=receipt.session_reference, session=session)
        session.abort_transaction()
    assert sessions.count_documents({"revoked_at": None}) == 1
    with client.start_session() as session:
        session.start_transaction()
        assert service.revoke_session(principal_id="principal-A", tenant_id="tenant-A",
                                      session_reference=receipt.session_reference, session=session)
        session.commit_transaction()
    assert sessions.count_documents({"revoked_at": None}) == 0
    assert refresh.count_documents({"revoked_at": None}) == 0


def test_replica_set_concurrent_refresh_race_has_exactly_one_winner(mongo_authority):
    client, _db, service, _auth, _sessions, refresh = mongo_authority
    original = issue(service, client)
    barrier = Barrier(2)

    def rotate_once():
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait(timeout=10)
            try:
                receipt = service.rotate_refresh_token(
                    original.refresh_token,
                    session=session,
                    now=datetime(2026, 11, 3, 0, 1, tzinfo=timezone.utc),
                )
                session.commit_transaction()
                return ("success", receipt)
            except Exception as error:
                if session.in_transaction:
                    session.abort_transaction()
                return ("rejected", error)

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _index: rotate_once(), range(2)))

    assert sum(outcome[0] == "success" for outcome in outcomes) == 1
    assert sum(outcome[0] == "rejected" for outcome in outcomes) == 1
    assert refresh.count_documents({"consumed_at": None, "revoked_at": None}) == 1
    assert refresh.count_documents({"token_digest": {"$exists": True}}) == 2


def test_replica_set_revoked_membership_and_capacity_block_global_session(mongo_authority):
    client, _db, service, authorities, _sessions, _refresh = mongo_authority
    receipt = issue(service, client)
    authorities.membership_status = TenantMembershipStatus.SUSPENDED
    assert not service.is_session_current(
        principal_id="principal-A", tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )
    authorities.membership_status = TenantMembershipStatus.ACTIVE
    authorities.capacity_status = TenantBusinessRoleStatus.REVOKED
    assert not service.is_session_current(
        principal_id="principal-A", tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )


def test_replica_set_credential_revision_change_blocks_global_refresh(mongo_authority):
    client, _db, service, authorities, _sessions, _refresh = mongo_authority
    receipt = issue(service, client)
    authorities.credential_revision = 3
    assert not service.is_session_current(
        principal_id="principal-A", tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(GlobalPrincipalSessionRejected, match="CREDENTIAL_STALE"):
            service.rotate_refresh_token(
                receipt.refresh_token,
                session=session,
                now=datetime(2026, 11, 3, 0, 1, tzinfo=timezone.utc),
            )
        session.abort_transaction()
