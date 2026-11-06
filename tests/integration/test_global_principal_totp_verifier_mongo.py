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
    if client.admin.command("hello").get("setName") != "wilsyGlobalPrincipalCertRS":
        pytest.fail("wrong global-principal certification replica set")
    database = client[f"global_factor_{uuid.uuid4().hex}"]
    factors = database["global_principal_mfa_factors"]
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
        client.drop_database(database.name)
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
