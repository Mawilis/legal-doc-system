# TITLE: WILSY EOS Global Principal Legacy MFA Migration Real-Mongo Certificate
# VERSION: v1.0.1-GLOBAL-PRINCIPAL-MFA-LEGACY-MIGRATION-MONGO
# AUTHORITY: Disposable replica-set integration certification only.
# EPITOME: Verify proof-based legacy OTP migration, credential revision binding and removal of plaintext legacy secret from the new factor record.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_global_principal_mfa_legacy_migration_mongo.py
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Python EOS Global Principal MFA.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.1-GLOBAL-PRINCIPAL-MFA-LEGACY-MIGRATION-MONGO adds the mandatory
#   sovereign artifact contract; migration assertions and fixture behavior remain unchanged.
#   v1.0.0 established real-replica-set proof-based migration certification.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Synthetic legacy factor fixtures only; no production secrets or database credentials.
# TENANT BOUNDARY: Test-only principal context; no canonical tenant records are accessed.
# AUTHORITY BOUNDARY: Integration evidence only; does not authorize production migration or factor issuance.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive.

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
    database = client[database_name]
    suffix = uuid.uuid4().hex
    credentials = database[f"{CREDENTIAL_COLLECTION}_cert_{suffix}"]
    legacy = database[f"{LEGACY_FACTOR_COLLECTION}_cert_{suffix}"]
    factors = database[f"{GLOBAL_FACTOR_COLLECTION}_cert_{suffix}"]
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
        for collection in (credentials, legacy, factors):
            collection.drop()
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

# ARTIFACT: tests/integration/test_global_principal_mfa_legacy_migration_mongo.py
# VERSION: v1.0.1-GLOBAL-PRINCIPAL-MFA-LEGACY-MIGRATION-MONGO
# AUTHORITY BOUNDARY: Disposable MongoDB legacy migration test only.
# TENANT POSTURE: Synthetic principal fixture only; no production tenant state is changed.
# FAIL-CLOSED POSTURE: Invalid proof or migration state fails the integration suite.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
