"""Replica-set proof that MFA consumption and session issuance commit/abort together."""
import os
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pymongo import MongoClient

from tools.eos.auth import global_principal_session_authority as session_module
from tools.eos.auth.global_principal_mfa_session_transition import (
    GlobalPrincipalMfaSessionTransition,
)
from tools.eos.auth.global_principal_session_authority import (
    GlobalPrincipalSessionAuthority,
    SESSION_COLLECTION,
    REFRESH_COLLECTION,
)
from tools.eos.auth.membership_selection_challenge import (
    COLLECTION as CHALLENGE_COLLECTION,
    MembershipSelectionChallengeService,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus


class Authorities:
    credential_revision = 7
    membership_revision = 8
    capacity_revision = 9

    def get_principal(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, status=PrincipalStatus.ACTIVE)

    def get_credential(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id,
                               credential_revision=self.credential_revision, mfa_enabled=True)

    def get_membership(self, principal_id, tenant_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id,
                               revision=self.membership_revision, status=TenantMembershipStatus.ACTIVE)

    def get_capacity(self, principal_id, tenant_id, role, *, session=None):
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id, business_role=role,
                               revision=self.capacity_revision, status=TenantBusinessRoleStatus.ACTIVE)


@pytest.fixture()
def transition_fixture(monkeypatch):
    uri = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI")
    if not uri:
        pytest.fail("TEST_GLOBAL_PRINCIPAL_MONGO_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    expected_replica_set = os.getenv(
        "TEST_GLOBAL_PRINCIPAL_MONGO_REPLICA_SET", "wilsyGlobalPrincipalCertRS"
    )
    actual_replica_set = client.admin.command("hello").get("setName")
    if actual_replica_set != expected_replica_set:
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
    challenges, sessions, refresh = (
        db[f"{CHALLENGE_COLLECTION}_cert_{suffix}"],
        db[f"{SESSION_COLLECTION}_cert_{suffix}"],
        db[f"{REFRESH_COLLECTION}_cert_{suffix}"],
    )
    MembershipSelectionChallengeService.ensure_indexes(challenges)
    GlobalPrincipalSessionAuthority.ensure_indexes(sessions, refresh)
    monkeypatch.setattr(session_module, "create_access_token",
                        lambda *args, **kwargs: "synthetic-access-token")
    authorities = Authorities()
    deps = dict(
        principal_repository=SimpleNamespace(get=authorities.get_principal),
        credential_repository=SimpleNamespace(get_by_principal=authorities.get_credential),
        membership_repository=SimpleNamespace(resolve=authorities.get_membership),
        business_role_repository=SimpleNamespace(resolve_business_role=authorities.get_capacity),
        tenant_resolver=lambda tenant_id, session=None: SimpleNamespace(tenant_id=tenant_id),
    )
    challenge_service = MembershipSelectionChallengeService(
        collection=challenges, **deps
    )
    session_authority = GlobalPrincipalSessionAuthority(
        sessions=sessions, refresh_tokens=refresh, **deps
    )
    transition = GlobalPrincipalMfaSessionTransition(
        challenge_service=challenge_service,
        session_authority=session_authority,
    )
    try:
        yield client, challenges, sessions, refresh, challenge_service, transition
    finally:
        for collection in (challenges, sessions, refresh):
            collection.drop()
        client.close()


def create_mfa_challenge(client, challenge_service):
    with client.start_session() as session:
        session.start_transaction()
        selection = challenge_service.issue_membership_selection_challenge(
            principal_id="principal-atomic",
            credential_revision=7,
            session=session,
        )
        mfa = challenge_service.select_membership_and_issue_mfa_challenge(
            selection_challenge_token=selection.challenge_token,
            tenant_id="tenant-atomic",
            business_role="tenant_owner",
            session=session,
        )
        session.commit_transaction()
    return mfa


def test_mfa_consumption_and_session_issue_share_one_atomic_transaction(transition_fixture):
    client, challenges, sessions, refresh, challenge_service, transition = transition_fixture
    mfa = create_mfa_challenge(client, challenge_service)

    # A failed downstream session write followed by caller abort must restore
    # the one-time MFA challenge and leave no partial session or refresh record.
    with client.start_session() as session:
        session.start_transaction()
        transition.complete_after_verified_factor(
            mfa_challenge_token=mfa.challenge_token, session=session
        )
        session.abort_transaction()
    assert challenges.count_documents({"purpose": "SELECTED_MEMBERSHIP_MFA", "consumed_at": None}) == 1
    assert sessions.count_documents({}) == 0
    assert refresh.count_documents({}) == 0

    # A successful transition persists both records and consumes the challenge
    # only when the caller commits this exact transaction.
    with client.start_session() as session:
        session.start_transaction()
        receipt = transition.complete_after_verified_factor(
            mfa_challenge_token=mfa.challenge_token, session=session
        )
        session.commit_transaction()

    assert challenges.count_documents({"purpose": "SELECTED_MEMBERSHIP_MFA", "consumed_at": {"$ne": None}}) == 1
    assert sessions.count_documents({"session_reference": receipt.session_reference}) == 1
    assert refresh.count_documents({"session_reference": receipt.session_reference}) == 1
    assert refresh.count_documents({"token_digest": {"$exists": True}, "refresh_token": {"$exists": True}}) == 0


def test_revision_change_between_mfa_challenge_and_session_issue_aborts_both(transition_fixture):
    client, challenges, sessions, refresh, challenge_service, transition = transition_fixture
    mfa = create_mfa_challenge(client, challenge_service)
    # A changed membership epoch is rejected during challenge consumption;
    # transaction abort leaves the challenge retryable and issues no session.
    challenge_service._memberships = SimpleNamespace(
        resolve=lambda principal_id, tenant_id, *, session=None:
            SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id,
                            revision=99, status=TenantMembershipStatus.ACTIVE)
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(Exception):
            transition.complete_after_verified_factor(
                mfa_challenge_token=mfa.challenge_token, session=session
            )
        session.abort_transaction()
    assert challenges.count_documents({"purpose": "SELECTED_MEMBERSHIP_MFA", "consumed_at": None}) == 1
    assert sessions.count_documents({}) == 0
    assert refresh.count_documents({}) == 0
