"""WILSY OS real-Mongo certification for membership-selection challenge transactions.

TITLE: Membership Selection Challenge Real-Mongo Certification
VERSION: v1.0.2-CONSOLIDATION-EXPLICIT-REPLICA-CERT
AUTHORITY: Certifies challenge persistence and caller-owned transaction semantics only.
EPITOME: Exercises digest indexes, single-use challenge consumption, MFA binding
         and rollback against a disposable MongoDB replica set.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_membership_selection_challenge_mongo.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-10.
CHANGELOG:
    v1.0.2-CONSOLIDATION-EXPLICIT-REPLICA-CERT honors the existing explicit test replica-set selector while requiring a writable primary; retains all replay, expiry and rollback proofs.
    v1.0.1-GLOBAL-MEMBERSHIP-SELECTION-CHALLENGE-MONGO-TESTS uses an explicit
    hashlib import for deterministic persisted-digest inspection.
    v1.0.0 adds real replica-set coverage for committed selection/MFA transitions,
    replay rejection and transaction abort restoring an unconsumed selection token.
COMPLIANCE: Test artifact for POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Uses synthetic authority and isolated disposable databases.
TENANT BOUNDARY: Exact synthetic principal/tenant/capacity selection only.
AUTHORITY BOUNDARY: Tests challenge lifecycle; no real IAM or production authority mutation.
FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from pymongo import MongoClient

from tools.eos.auth.membership_selection_challenge import (
    MFA_PURPOSE,
    MembershipSelectionChallengeRejected,
    MembershipSelectionChallengeService,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus


class PrincipalRepository:
    """Synthetic ACTIVE global principal reader for isolated Mongo tests."""

    def get(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, status=PrincipalStatus.ACTIVE)


class CredentialRepository:
    """Synthetic current global credential reader with explicit MFA enrollment."""

    def get_by_principal(self, principal_id, *, session=None):
        return SimpleNamespace(
            principal_id=principal_id,
            credential_revision=2,
            mfa_enabled=True,
        )


class MembershipRepository:
    """Synthetic exact tenant membership reader."""

    def resolve(self, principal_id, tenant_id, *, session=None):
        return SimpleNamespace(
            principal_id=principal_id,
            tenant_id=tenant_id,
            status=TenantMembershipStatus.ACTIVE,
            revision=3,
        )


class BusinessRoleRepository:
    """Synthetic exact business capacity reader."""

    def resolve_business_role(self, principal_id, tenant_id, business_role, *, session=None):
        return SimpleNamespace(
            principal_id=principal_id,
            tenant_id=tenant_id,
            business_role=business_role,
            status=TenantBusinessRoleStatus.ACTIVE,
            revision=5,
        )


@pytest.fixture()
def mongo_challenge_service():
    """Provide a uniquely isolated challenge collection on the required replica set."""
    uri = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI")
    if not uri:
        pytest.fail("TEST_GLOBAL_PRINCIPAL_MONGO_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    expected = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_REPLICA_SET", "wilsyGlobalPrincipalCertRS")
    if hello.get("setName") != expected or hello.get("isWritablePrimary") is not True:
        pytest.fail("wrong membership-challenge certification replica set")
    database = client[f"membership_challenge_{uuid.uuid4().hex}"]
    collection = database["eos_authentication_challenges"]
    MembershipSelectionChallengeService.ensure_indexes(collection)
    service = MembershipSelectionChallengeService(
        collection=collection,
        principal_repository=PrincipalRepository(),
        credential_repository=CredentialRepository(),
        membership_repository=MembershipRepository(),
        business_role_repository=BusinessRoleRepository(),
        tenant_resolver=lambda tenant_id, session=None: SimpleNamespace(tenant_id=tenant_id),
    )
    try:
        yield client, collection, service
    finally:
        client.drop_database(database.name)
        client.close()


def issue_selection(service, session, now=None):
    """Issue one tenant-neutral challenge inside the supplied transaction."""
    return service.issue_membership_selection_challenge(
        principal_id="principal-mongo-1",
        credential_revision=2,
        session=session,
        now=now,
    )


def select_capacity(service, token, session, now=None):
    """Consume selection challenge and issue one revision-bound MFA challenge."""
    return service.select_membership_and_issue_mfa_challenge(
        selection_challenge_token=token,
        tenant_id="tenant-mongo-1",
        business_role="tenant_owner",
        session=session,
        now=now,
    )


def test_real_mongo_commits_selection_and_revision_bound_mfa_challenge(mongo_challenge_service):
    client, collection, service = mongo_challenge_service
    with client.start_session() as session:
        session.start_transaction()
        selection = issue_selection(service, session)
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()
        mfa = select_capacity(service, selection.challenge_token, session)
        session.commit_transaction()

    assert mfa.tenant_id == "tenant-mongo-1"
    assert mfa.business_role == "tenant_owner"
    assert mfa.workspace_id == "EXECUTIVE_COMMAND_CENTRE"
    assert (mfa.credential_revision, mfa.membership_revision, mfa.capacity_revision) == (2, 3, 5)
    assert collection.count_documents({"purpose": MFA_PURPOSE}) == 1
    assert collection.count_documents({"consumed_at": {"$ne": None}}) == 1


def test_real_mongo_replay_is_rejected_after_committed_consumption(mongo_challenge_service):
    client, _collection, service = mongo_challenge_service
    with client.start_session() as session:
        session.start_transaction()
        selection = issue_selection(service, session)
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()
        select_capacity(service, selection.challenge_token, session)
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(MembershipSelectionChallengeRejected, match="INVALID_EXPIRED_OR_CONSUMED"):
            select_capacity(service, selection.challenge_token, session)
        session.abort_transaction()


def test_real_mongo_abort_restores_selection_challenge_for_safe_retry(mongo_challenge_service):
    client, collection, service = mongo_challenge_service
    with client.start_session() as session:
        session.start_transaction()
        selection = issue_selection(service, session)
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()
        select_capacity(service, selection.challenge_token, session)
        session.abort_transaction()

    persisted = collection.find_one({"challenge_digest": hashlib.sha3_512(
        selection.challenge_token.encode("utf-8")
    ).hexdigest()})
    assert persisted is not None
    assert persisted["consumed_at"] is None
    assert collection.count_documents({"purpose": MFA_PURPOSE}) == 0

    with client.start_session() as session:
        session.start_transaction()
        retry = select_capacity(service, selection.challenge_token, session)
        session.commit_transaction()
    assert retry.challenge_token
    assert collection.count_documents({"purpose": MFA_PURPOSE}) == 1




def test_real_mongo_expired_selection_challenge_cannot_be_consumed(mongo_challenge_service):
    client, collection, service = mongo_challenge_service
    issued_at = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)
    with client.start_session() as session:
        session.start_transaction()
        selection = issue_selection(service, session, now=issued_at)
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(MembershipSelectionChallengeRejected, match="INVALID_EXPIRED_OR_CONSUMED"):
            select_capacity(
                service,
                selection.challenge_token,
                session,
                now=issued_at + timedelta(minutes=6),
            )
        session.abort_transaction()

    persisted = collection.find_one({
        "challenge_digest": hashlib.sha3_512(selection.challenge_token.encode("utf-8")).hexdigest()
    })
    assert persisted is not None
    assert persisted["consumed_at"] is None
    assert collection.count_documents({"purpose": MFA_PURPOSE}) == 0


# ARTIFACT: test_membership_selection_challenge_mongo.py
# VERSION: v1.0.2-CONSOLIDATION-EXPLICIT-REPLICA-CERT
# AUTHORITY BOUNDARY: real-Mongo challenge persistence and transaction certification only
# TENANT POSTURE: isolated synthetic principal/tenant/capacity scope
# FAIL-CLOSED POSTURE: replay, expiry and transaction failures reject; abort restores uncommitted state
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
