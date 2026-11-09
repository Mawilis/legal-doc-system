# TITLE: WILSY EOS Global Principal TOTP Verifier Real-Mongo Certificate
# VERSION: v1.0.1-GLOBAL-PRINCIPAL-TOTP-VERIFIER-MONGO
# AUTHORITY: Disposable replica-set integration certification only.
# EPITOME: Verify principal-scoped TOTP factor persistence, single-use time-step replay control and transaction rollback against a real MongoDB replica set.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_global_principal_totp_verifier_mongo.py
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Python EOS Global Principal MFA verification authority.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.1-GLOBAL-PRINCIPAL-TOTP-VERIFIER-MONGO adds the mandatory sovereign
#   artifact contract; replay and transaction assertions are unchanged.
#   v1.0.0 established disposable replica-set TOTP verifier certification.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Synthetic TOTP fixtures and disposable MongoDB only; no production factor secrets or credentials.
# TENANT BOUNDARY: Synthetic principal context only; no canonical tenant records are accessed or mutated.
# AUTHORITY BOUNDARY: Test-only verification evidence; cannot activate production MFA factors or sessions.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive.

"""Real replica-set certification for global-principal TOTP replay control."""
import os
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pyotp
import pytest
from pymongo import MongoClient

from tools.eos.auth.global_principal_totp_verifier import (
    GlobalPrincipalFactorRejected,
    GlobalPrincipalTotpVerifier,
)


NOW = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
SECRET = "JBSWY3DPEHPK3PXP"


@pytest.fixture()
def factor_store():
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
    database = client[database_name]
    suffix = uuid.uuid4().hex
    factors = database[f"global_principal_mfa_factors_cert_{suffix}"]
    GlobalPrincipalTotpVerifier.ensure_indexes(factors)
    factors.insert_one({
        "principal_id": "principal-global",
        "status": "ACTIVE",
        "credential_revision": 7,
        "encrypted_secret": "test-kms-envelope",
    })
    credentials = SimpleNamespace(
        get_by_principal=lambda principal_id, session=None: SimpleNamespace(
            principal_id=principal_id, credential_revision=7, mfa_enabled=True
        )
    )
    verifier = GlobalPrincipalTotpVerifier(
        collection=factors,
        credential_repository=credentials,
        decrypt_secret=lambda envelope, *, principal_id, credential_revision: SECRET if envelope == "test-kms-envelope" and principal_id == "principal-global" and credential_revision == 7 else "",
    )
    try:
        yield client, factors, verifier
    finally:
        factors.drop()
        client.close()


def test_replica_set_factor_replay_write_rolls_back_with_caller_transaction(factor_store):
    client, factors, verifier = factor_store
    code = pyotp.TOTP(SECRET).at(NOW)
    with client.start_session() as session:
        session.start_transaction()
        assert verifier.verify(
            principal_id="principal-global", credential_revision=7,
            code=code, session=session, now=NOW,
        )
        session.abort_transaction()
    assert "last_accepted_step" not in factors.find_one({"principal_id": "principal-global"})

    with client.start_session() as session:
        session.start_transaction()
        assert verifier.verify(
            principal_id="principal-global", credential_revision=7,
            code=code, session=session, now=NOW,
        )
        session.commit_transaction()
    assert factors.find_one({"principal_id": "principal-global"})["last_accepted_step"] == pyotp.TOTP(SECRET).timecode(NOW)


def test_replica_set_rejects_replayed_totp_step(factor_store):
    client, factors, verifier = factor_store
    code = pyotp.TOTP(SECRET).at(NOW)
    with client.start_session() as session:
        session.start_transaction()
        assert verifier.verify(
            principal_id="principal-global", credential_revision=7,
            code=code, session=session, now=NOW,
        )
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(GlobalPrincipalFactorRejected, match="GLOBAL_FACTOR_REPLAYED"):
            verifier.verify(
                principal_id="principal-global", credential_revision=7,
                code=code, session=session, now=NOW,
            )
        session.abort_transaction()
    assert factors.count_documents({"last_accepted_step": {"$exists": True}}) == 1

# ARTIFACT: tests/integration/test_global_principal_totp_verifier_mongo.py
# VERSION: v1.0.1-GLOBAL-PRINCIPAL-TOTP-VERIFIER-MONGO
# AUTHORITY BOUNDARY: Disposable replica-set TOTP verification test only.
# TENANT POSTURE: Synthetic principal fixtures only; no production tenant state is changed.
# FAIL-CLOSED POSTURE: Replayed, stale or transactionally inconsistent factor use fails the integration suite.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
