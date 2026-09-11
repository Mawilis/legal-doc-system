"""Bounded host-backed certificate for the PRDCA Mongo ledger.

TITLE: PRDCA Ledger Real-Mongo Durability Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3L-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies durable PRDCA batch indexes, caller-owned commit/abort,
         exact replay, strict hydration, and transaction visibility on the
         certified local replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_prdca_ledger_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed certificate for prdca_ledger.py.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3L-R1 establishes bounded real-Mongo ledger
           durability and caller transaction evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Random disposable database; no secrets or provider calls.
TENANT BOUNDARY: Platform governance evidence only; no tenant authorization.
AUTHORITY BOUNDARY: Persistence certification only; no certificate semantics.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
REAL-MONGO ENVIRONMENT CONTRACT: TEST_VENDOR_MONGO_URI or the certified local
                                  wilsyVendorCertRS replica-set URI.
FAIL-CLOSED DECLARATION: Wrong topology, absent transactions, corruption,
                          duplicate artifacts, and failed cleanup reject.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import replace
from typing import Any, cast

import pytest
from pymongo import MongoClient

import tools.eos.governance.prdca as core
from tools.eos.governance.prdca_ledger import (
    COLLECTION,
    PRDCALedgerPersistedRecordInvalidError,
    PRDCAMongoLedger,
)


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


def _batch(seed: str = "a") -> core.PRDCACertificateBatch:
    def artifact_id(letter: str) -> str:
        return (letter * 128)[:128]

    payload: dict[str, object] = {"schema": "WILSY-TEST-PAYLOAD/V1"}
    envelope = {
        "envelope_schema": "WILSY-PRDCA-SIGNED-ENVELOPE/V1",
        "artifact_type": "PLATFORM_REGISTRATION_CERTIFICATE",
        "artifact_id": artifact_id(seed),
        "payload_schema": "WILSY-PLATFORM-REGISTRATION-CERTIFICATE/V1",
        "payload": payload,
        "campaign_identity": "M11-R8-R3B-P8-P3D-P5-R8-P3L",
        "issuer_authority": "WILSY_PLATFORM_REGISTRATION_AND_DEPLOYMENT_CERTIFICATION_AUTHORITY",
        "authority_key_id": "prdca-key:test",
        "signature_algorithm": "Ed25519",
        "signature": "signature",
        "issued_at": "2026-09-10T10:00:00.000000Z",
        "status": "ACTIVE",
    }
    dcc = dict(
        envelope,
        artifact_type="DEPLOYMENT_CERTIFICATION_CERTIFICATE",
        artifact_id=artifact_id("b" if seed == "a" else seed),
    )
    receipt = dict(
        envelope,
        artifact_type="DESCRIPTOR_VERIFICATION_RECEIPT",
        artifact_id=artifact_id("c" if seed == "a" else seed),
    )
    return core.PRDCACertificateBatch(
        platform_registration=core.PlatformRegistrationCertificateEnvelope(
            **{**envelope, "payload": cast(dict[str, object], envelope["payload"])}
        ),
        deployment_certification=core.DeploymentCertificationCertificateEnvelope(
            **{**dcc, "payload": cast(dict[str, object], dcc["payload"])}
        ),
        descriptor_receipt=core.DescriptorVerificationReceiptEnvelope(
            **{**receipt, "payload": cast(dict[str, object], receipt["payload"])}
        ),
    )


@pytest.fixture
def mongo_db() -> Any:
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", DEFAULT_URI)
    if "mongodb.net" in uri or "atlas" in uri.lower():
        pytest.fail("A local certified replica set is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    db_name = f"prdca_ledger_cert_{uuid.uuid4().hex}"
    db = client[db_name]
    try:
        yield client, db
    finally:
        client.drop_database(db_name)
        client.close()


def test_indexes_and_committed_round_trip(mongo_db: Any) -> None:
    client, db = mongo_db
    collection = db[COLLECTION]
    ledger = PRDCAMongoLedger(cast(Any, collection))
    ledger.ensure_indexes()
    indexes = {item["name"]: item for item in collection.list_indexes()}
    expected = {
        "prdca_platform_registration_artifact_unique": "platform_registration.artifact_id",
        "prdca_deployment_certification_artifact_unique": "deployment_certification.artifact_id",
        "prdca_descriptor_receipt_artifact_unique": "descriptor_receipt.artifact_id",
    }
    for name, field in expected.items():
        assert list(indexes[name]["key"].items()) == [(field, 1)]
        assert indexes[name].get("unique") is True
    batch = _batch()
    with client.start_session() as session:
        session.start_transaction()
        ledger.append_batch(batch, cast(Any, session))
        session.commit_transaction()
    hydrated = ledger.get_by_platform_registration_id("a" * 128)
    assert hydrated == batch
    assert collection.count_documents({}) == 1


def test_caller_abort_is_invisible_to_new_session(mongo_db: Any) -> None:
    client, db = mongo_db
    collection = db[COLLECTION]
    ledger = PRDCAMongoLedger(cast(Any, collection))
    ledger.ensure_indexes()
    with client.start_session() as session:
        session.start_transaction()
        ledger.append_batch(_batch(), cast(Any, session))
        assert collection.count_documents({}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({}) == 0


def test_exact_replay_is_noop_and_divergent_batch_conflicts(mongo_db: Any) -> None:
    client, db = mongo_db
    collection = db[COLLECTION]
    ledger = PRDCAMongoLedger(cast(Any, collection))
    ledger.ensure_indexes()
    with client.start_session() as session:
        session.start_transaction()
        ledger.append_batch(_batch(), cast(Any, session))
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        ledger.append_batch(_batch(), cast(Any, session))
        session.commit_transaction()
    assert collection.count_documents({}) == 1
    divergent_base = _batch()
    divergent = replace(
        divergent_base,
        deployment_certification=replace(
            divergent_base.deployment_certification, artifact_id="d" * 128
        ),
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(core.PRDCAArtifactConflictError):
            ledger.append_batch(divergent, cast(Any, session))
        session.abort_transaction()
    assert collection.count_documents({}) == 1


def test_corruption_rejects_strict_hydration(mongo_db: Any) -> None:
    client, db = mongo_db
    collection = db[COLLECTION]
    ledger = PRDCAMongoLedger(cast(Any, collection))
    ledger.ensure_indexes()
    with client.start_session() as session:
        session.start_transaction()
        ledger.append_batch(_batch(), cast(Any, session))
        session.commit_transaction()
    collection.update_one(
        {"platform_registration.artifact_id": "a" * 128},
        {"$set": {"batch_fingerprint": "0" * 128}},
    )
    with pytest.raises(PRDCALedgerPersistedRecordInvalidError):
        ledger.get_by_platform_registration_id("a" * 128)


def test_uncommitted_batch_is_not_visible_to_independent_client(mongo_db: Any) -> None:
    client, db = mongo_db
    collection = db[COLLECTION]
    ledger = PRDCAMongoLedger(cast(Any, collection))
    ledger.ensure_indexes()
    with client.start_session() as session:
        session.start_transaction()
        ledger.append_batch(_batch(), cast(Any, session))
        outside = MongoClient(
            os.environ.get("TEST_VENDOR_MONGO_URI", DEFAULT_URI),
            serverSelectionTimeoutMS=5000,
        )
        try:
            assert outside[db.name][COLLECTION].count_documents({}) == 0
        finally:
            outside.close()
        session.abort_transaction()


# ARTIFACT: test_prdca_ledger_real_mongo.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3L-R1
# AUTHORITY BOUNDARY: bounded real-Mongo PRDCA ledger certification only
# TENANT POSTURE: disposable platform-governance database
# FAIL-CLOSED POSTURE: wrong topology, rollback leakage, corruption, or conflict fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
