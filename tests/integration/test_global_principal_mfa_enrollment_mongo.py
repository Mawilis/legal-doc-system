"""Real Mongo replica-set certification for global MFA enrollment transactions."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pyotp
import pytest
from pymongo import MongoClient

from tools.eos.auth.global_principal_mfa_enrollment_service import (
    CHALLENGE_COLLECTION,
    FACTOR_COLLECTION,
    GlobalPrincipalMfaEnrollmentService,
)
from tools.eos.auth.global_principal_totp_verifier import GlobalPrincipalTotpVerifier
from tools.eos.auth.principal_credential import PrincipalCredential
from tools.eos.auth.principal_credential_repository import (
    COLLECTION as CREDENTIAL_COLLECTION,
    PrincipalCredentialRepository,
)

NOW = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)


class _Kms:
    def __init__(self):
        self.secrets = {}

    def encrypt_secret(self, *, secret, principal_id, credential_revision):
        reference = f"cipher-{len(self.secrets) + 1}"
        self.secrets[reference] = (secret, principal_id, credential_revision)
        return {
            "schema": "TEST_KMS_ENVELOPE",
            "ciphertext_reference": reference,
            "principal_id": principal_id,
            "credential_revision": credential_revision,
        }

    def decrypt_secret(self, envelope, *, principal_id, credential_revision):
        secret, bound_principal, bound_revision = self.secrets[envelope["ciphertext_reference"]]
        if (bound_principal, bound_revision) != (principal_id, credential_revision):
            raise ValueError("encryption context mismatch")
        return secret


@pytest.fixture()
def enrollment_store():
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
    database = client[f"global_mfa_enrollment_{uuid.uuid4().hex}"]
    credentials = database[CREDENTIAL_COLLECTION]
    challenges = database[CHALLENGE_COLLECTION]
    factors = database[FACTOR_COLLECTION]
    legacy_factors = database["otp_secrets"]
    PrincipalCredentialRepository.ensure_indexes(credentials)
    GlobalPrincipalMfaEnrollmentService.ensure_indexes(challenges)
    GlobalPrincipalTotpVerifier.ensure_indexes(factors)
    PrincipalCredentialRepository.insert(
        PrincipalCredential(
            principal_id="principal-enrollment",
            normalized_email="enroll@example.com",
            password_hash="$2b$12$" + "a" * 53,
            credential_revision=0,
            mfa_enabled=False,
        ),
        credentials,
    )
    kms = _Kms()
    service = GlobalPrincipalMfaEnrollmentService(
        kms=kms,
        challenge_collection=challenges,
        factor_collection=factors,
        legacy_factor_collection=legacy_factors,
        credential_collection=credentials,
        credential_repository=PrincipalCredentialRepository,
    )
    try:
        yield client, credentials, challenges, factors, service
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_mongo_enrollment_is_atomic_and_retries_after_transaction_abort(enrollment_store):
    client, credentials, challenges, factors, service = enrollment_store

    with client.start_session() as session:
        session.start_transaction()
        receipt = service.issue(
            principal_id="principal-enrollment",
            credential_revision=0,
            session=session,
            now=NOW,
        )
        session.commit_transaction()

    code = pyotp.TOTP(receipt.secret, digits=6, interval=30).at(NOW)
    with client.start_session() as session:
        session.start_transaction()
        completion = service.confirm(
            challenge_token=receipt.challenge_token,
            code=code,
            session=session,
            now=NOW,
        )
        assert completion.credential_revision == 1
        session.abort_transaction()

    credential_after_abort = PrincipalCredentialRepository.get_by_principal(
        "principal-enrollment", credentials
    )
    assert credential_after_abort.mfa_enabled is False
    assert credential_after_abort.credential_revision == 0
    assert factors.count_documents({"principal_id": "principal-enrollment"}) == 0
    assert challenges.count_documents({"principal_id": "principal-enrollment"}) == 1

    with client.start_session() as session:
        session.start_transaction()
        completion = service.confirm(
            challenge_token=receipt.challenge_token,
            code=code,
            session=session,
            now=NOW,
        )
        session.commit_transaction()

    credential_after_commit = PrincipalCredentialRepository.get_by_principal(
        "principal-enrollment", credentials
    )
    factor = factors.find_one({"principal_id": "principal-enrollment"})
    assert completion.credential_revision == 1
    assert credential_after_commit.mfa_enabled is True
    assert credential_after_commit.credential_revision == 1
    assert factor["status"] == "ACTIVE"
    assert factor["credential_revision"] == 1
    assert factor["last_accepted_step"] == pyotp.TOTP(receipt.secret, interval=30).timecode(NOW)
    assert challenges.count_documents({"principal_id": "principal-enrollment"}) == 0
