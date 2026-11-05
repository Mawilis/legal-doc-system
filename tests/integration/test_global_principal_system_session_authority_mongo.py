"""Real replica-set certificate for tenant-neutral SYSTEM MFA/session atomicity."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import bcrypt
import pytest
from pymongo import MongoClient

from tools.eos.auth.global_principal_system_session_authority import (
    CHALLENGE_COLLECTION,
    SESSION_COLLECTION,
    GlobalPrincipalSystemMfaChallengeService,
    GlobalPrincipalSystemSessionAuthority,
    GlobalPrincipalSystemSessionRejected,
)
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_credential import PrincipalCredential
from tools.eos.auth.principal_credential_repository import PrincipalCredentialRepository
from tools.eos.auth.principal_status import PrincipalStatus

URI = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI", "")


class _CurrentSystemAuthorizer:
    def require(self, *, principal_id, permission_id, session):
        assert principal_id.startswith("system-principal-")
        assert permission_id == "system_services:queue:read"
        assert session.in_transaction is True


def test_system_mfa_challenge_and_session_issue_revoke_and_rollback_are_atomic(monkeypatch: pytest.MonkeyPatch):
    if not URI:
        raise RuntimeError("TEST_GLOBAL_PRINCIPAL_MONGO_URI_REQUIRED")
    client = MongoClient(URI, serverSelectionTimeoutMS=5_000, retryWrites=True, tz_aware=True)
    database_name = "global_system_session_" + uuid.uuid4().hex
    database = client[database_name]
    monkeypatch.setattr(
        "tools.eos.auth.global_principal_system_session_authority.create_access_token",
        lambda _claims, **_kwargs: "synthetic-signed-system-token",
    )
    principal_id = "system-principal-" + uuid.uuid4().hex
    email = principal_id + "@example.test"
    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        principals = database["principal_authorities"]
        credentials = database["principal_credentials"]
        challenges = database[CHALLENGE_COLLECTION]
        sessions = database[SESSION_COLLECTION]
        PrincipalAuthorityRepository.ensure_indexes(principals)
        PrincipalCredentialRepository.ensure_indexes(credentials)
        GlobalPrincipalSystemMfaChallengeService.ensure_indexes(challenges)
        GlobalPrincipalSystemSessionAuthority.ensure_indexes(sessions)
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
            principals,
        )
        PrincipalCredentialRepository.insert(
            PrincipalCredential(
                principal_id=principal_id,
                normalized_email=email,
                password_hash=bcrypt.hashpw(b"synthetic-system-password", bcrypt.gensalt(rounds=4)).decode(),
                credential_revision=3,
                mfa_enabled=True,
            ),
            credentials,
        )
        challenge_service = GlobalPrincipalSystemMfaChallengeService(collection=challenges)
        authority = GlobalPrincipalSystemSessionAuthority(
            sessions=sessions,
            principal_collection=principals,
            credential_collection=credentials,
            authorizer=_CurrentSystemAuthorizer(),
        )

        with client.start_session() as session:
            session.start_transaction()
            token, expires_at = challenge_service.issue(
                principal_id=principal_id,
                credential_revision=3,
                session=session,
                now=now,
            )
            factor = challenge_service.get_factor_context(token, session=session, now=now)
            assert factor.principal_id == principal_id
            assert factor.credential_revision == 3
            challenge_service.consume(
                token,
                principal_id=principal_id,
                credential_revision=3,
                session=session,
                now=now,
            )
            receipt = authority.issue_after_mfa(
                principal_id,
                3,
                session=session,
                now=now,
            )
            session.commit_transaction()

        challenge_row = challenges.find_one({"principal_id": principal_id})
        assert challenge_row is not None
        assert challenge_row["consumed_at"] == now
        assert challenge_row["expires_at"] == expires_at
        session_row = sessions.find_one({"session_reference": receipt.session_reference})
        assert session_row is not None
        assert session_row["principal_id"] == principal_id
        assert session_row["credential_revision"] == 3
        assert session_row["revoked_at"] is None

        with client.start_session() as session:
            session.start_transaction()
            assert authority.is_session_current(
                principal_id=principal_id,
                session_reference=receipt.session_reference,
                expected_credential_revision=3,
                session=session,
                now=now,
            ) is True
            session.commit_transaction()

        with client.start_session() as session:
            session.start_transaction()
            assert authority.revoke(
                principal_id=principal_id,
                session_reference=receipt.session_reference,
                session=session,
                now=now,
            ) is True
            session.commit_transaction()

        with client.start_session() as session:
            session.start_transaction()
            assert authority.is_session_current(
                principal_id=principal_id,
                session_reference=receipt.session_reference,
                expected_credential_revision=3,
                session=session,
                now=now,
            ) is False
            session.commit_transaction()

        rollback_principal = principal_id + "-rollback"
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(rollback_principal, PrincipalStatus.ACTIVE, 0),
            principals,
        )
        PrincipalCredentialRepository.insert(
            PrincipalCredential(
                principal_id=rollback_principal,
                normalized_email=rollback_principal + "@example.test",
                password_hash=bcrypt.hashpw(b"synthetic-system-password", bcrypt.gensalt(rounds=4)).decode(),
                credential_revision=1,
                mfa_enabled=True,
            ),
            credentials,
        )
        rollback_token = None
        rollback_reference = None
        with client.start_session() as session:
            session.start_transaction()
            rollback_token, _ = challenge_service.issue(
                principal_id=rollback_principal,
                credential_revision=1,
                session=session,
                now=now,
            )
            rollback_receipt = authority.issue_after_mfa(
                rollback_principal,
                1,
                session=session,
                now=now,
            )
            rollback_reference = rollback_receipt.session_reference
            session.abort_transaction()

        assert challenges.find_one({"challenge_digest": __import__("hashlib").sha256(rollback_token.encode()).hexdigest()}) is None
        assert sessions.find_one({"session_reference": rollback_reference}) is None

        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(GlobalPrincipalSystemSessionRejected):
                challenge_service.get_factor_context(token, session=session, now=now)
            session.abort_transaction()
    finally:
        client.drop_database(database_name)
        client.close()
