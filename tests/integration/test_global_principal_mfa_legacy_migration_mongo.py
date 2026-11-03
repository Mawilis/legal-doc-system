"""Real Mongo replica-set certification for proof-based legacy MFA migration."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pyotp
import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from pymongo import MongoClient

from tools.eos.auth.global_principal_mfa_legacy_migration_service import (
    GLOBAL_FACTOR_COLLECTION,
    LEGACY_FACTOR_COLLECTION,
    GlobalPrincipalMfaLegacyMigrationService,
)
from tools.eos.auth.global_principal_totp_verifier import GlobalPrincipalTotpVerifier
from tools.eos.auth.principal_credential import PrincipalCredential
from tools.eos.auth.principal_credential_repository import (
    COLLECTION as CREDENTIAL_COLLECTION,
    PrincipalCredentialRepository,
)

NOW = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
SECRET = "JBSWY3DPEHPK3PXP"


class _Principals:
    def get(self, principal_id, *, session=None):
        assert session is not None
        return SimpleNamespace(principal_id=principal_id, status=PrincipalStatus.ACTIVE)


class _Kms:
    def __init__(self):
        self.secrets = {}

    def encrypt_secret(self, *, secret, principal_id, credential_revision):
        reference = f"legacy-migration-cipher-{len(self.secrets) + 1}"
        self.secrets[reference] = (secret, principal_id, credential_revision)
        return {
            "schema": "TEST_KMS",
            "ciphertext_reference": reference,
            "principal_id": principal_id,
            "credential_revision": credential_revision,
        }


@pytest.fixture()
def legacy_migration_store():
    uri = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI")
    if not uri:
        pytest.fail("TEST_GLOBAL_PRINCIPAL_MONGO_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    if client.admin.command("hello").get("setName") != "wilsyGlobalPrincipalCertRS":
        pytest.fail("wrong global-principal certification replica set")
    database = client[f"global_mfa_legacy_migration_{uuid.uuid4().hex}"]
    credentials = database[CREDENTIAL_COLLECTION]
    legacy = database[LEGACY_FACTOR_COLLECTION]
    factors = database[GLOBAL_FACTOR_COLLECTION]
    PrincipalCredentialRepository.ensure_indexes(credentials)
    GlobalPrincipalTotpVerifier.ensure_indexes(factors)
    PrincipalCredentialRepository.insert(
        PrincipalCredential(
            principal_id="principal-legacy-mfa",
            normalized_email="legacy@example.com",
            password_hash="$2b$12$" + "a" * 53,
            credential_revision=7,
            mfa_enabled=True,
        ),
        credentials,
    )
    legacy.insert_one({"user_id": "principal-legacy-mfa", "secret": SECRET})
    service = GlobalPrincipalMfaLegacyMigrationService(
        kms=_Kms(),
        legacy_factor_collection=legacy,
        factor_collection=factors,
        credential_collection=credentials,
        credential_repository=PrincipalCredentialRepository,
        principal_repository=_Principals(),
    )
    try:
        yield client, credentials, legacy, factors, service
    finally:
        client.drop_database(database.name)
        client.close()

def test_real_mongo_legacy_factor_proof_repairs_unset_mfa_flag_with_new_revision(legacy_migration_store):
    client, credentials, legacy, factors, service = legacy_migration_store
    PrincipalCredentialRepository.insert(
        PrincipalCredential(
            principal_id="principal-legacy-unset",
            normalized_email="legacy-unset@example.com",
            password_hash="$2b$12$" + "b" * 53,
            credential_revision=0,
            mfa_enabled=False,
        ),
        credentials,
    )
    legacy.insert_one({"user_id": "principal-legacy-unset", "secret": SECRET})
    with client.start_session() as session:
        session.start_transaction()
        receipt = service.migrate(
            principal_id="principal-legacy-unset",
            credential_revision=0,
            code=pyotp.TOTP(SECRET).at(NOW),
            session=session,
            now=NOW,
        )
        session.commit_transaction()
    updated = PrincipalCredentialRepository.get_by_principal(
        "principal-legacy-unset", credentials
    )
    factor = factors.find_one({"principal_id": "principal-legacy-unset"})
    assert receipt.credential_revision == 1
    assert updated.mfa_enabled is True
    assert updated.credential_revision == 1
    assert factor["credential_revision"] == 1


def test_real_mongo_legacy_factor_migration_is_atomic_and_preserves_source_until_cutover(legacy_migration_store):
    client, _credentials, legacy, factors, service = legacy_migration_store
    code = pyotp.TOTP(SECRET).at(NOW)

    with client.start_session() as session:
        session.start_transaction()
        service.migrate(
            principal_id="principal-legacy-mfa",
            credential_revision=7,
            code=code,
            session=session,
            now=NOW,
        )
        session.abort_transaction()

    assert factors.count_documents({"principal_id": "principal-legacy-mfa"}) == 0
    assert legacy.count_documents({"user_id": "principal-legacy-mfa"}) == 1

    with client.start_session() as session:
        session.start_transaction()
        receipt = service.migrate(
            principal_id="principal-legacy-mfa",
            credential_revision=7,
            code=code,
            session=session,
            now=NOW,
        )
        session.commit_transaction()

    factor = factors.find_one({"principal_id": "principal-legacy-mfa"})
    assert receipt.credential_revision == 7
    assert factor["status"] == "ACTIVE"
    assert factor["credential_revision"] == 7
    assert factor["migration_source"] == "LEGACY_OTP_SECRET_PROOF"
    assert "secret" not in factor
    assert legacy.count_documents({"user_id": "principal-legacy-mfa"}) == 1
