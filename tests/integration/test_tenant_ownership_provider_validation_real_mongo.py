"""Real replica-set certification for recovery decision replay protection."""
from __future__ import annotations

import os
import base64
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from tools.eos.auth.tenant_ownership_provider_ports import (
    RecoveryDecisionLookup, RecoveryDecisionReceipt,
)
from tools.eos.auth.tenant_ownership_provider_validation import (
    OwnershipProviderEvidenceError, RecoveryDecisionReplayRegistry, VerificationKey,
    recovery_decision_signing_payload,
)


@pytest.fixture
def mongo():
    uri = os.environ.get("WILSY_ISSUE_300_REAL_MONGO_URI")
    if not uri:
        pytest.fail("WILSY_ISSUE_300_REAL_MONGO_URI_REQUIRED_FOR_REAL_MONGO_CERTIFICATE")
    parsed = urlparse(uri)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or parsed.port is None:
        pytest.fail("ISSUE_300_LOOPBACK_MONGO_WITH_EXPLICIT_PORT_REQUIRED")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    name = "issue_300_recovery_" + uuid.uuid4().hex
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or hello.get("isWritablePrimary") is not True:
            pytest.fail("ISSUE_300_APPROVED_DISPOSABLE_REPLICA_SET_REQUIRED")
        yield client, client[name]
    finally:
        client.drop_database(name)
        client.close()


def test_recovery_decision_consumption_is_transactional_and_replay_safe(mongo):
    client, db = mongo
    registry = RecoveryDecisionReplayRegistry(db)
    registry.ensure_indexes()
    now = datetime.now(timezone.utc)
    fingerprint = "a" * 64
    lookup = RecoveryDecisionLookup(
        "tenant-" + uuid.uuid4().hex, "entity-1", "case-1", fingerprint, "successor-1", now,
    )
    receipt = RecoveryDecisionReceipt(
        "independent-authority", "governed-root", fingerprint, "decision-" + uuid.uuid4().hex,
        "b" * 64, lookup.recovery_case_reference, fingerprint, lookup.successor_principal_id,
        "c" * 64, "d" * 64, "e" * 64, "FINAL",
        now - timedelta(minutes=1), now + timedelta(days=1), "revocation-check",
    )

    private = ed25519.Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    key = VerificationKey(
        "key-1", 1, "ED25519", public_pem,
        now - timedelta(days=1), now + timedelta(days=1),
        trust_root_reference=receipt.trust_root_reference,
    )
    signature = base64.b64encode(private.sign(recovery_decision_signing_payload(lookup, receipt))).decode("ascii")

    with client.start_session() as session:
        with session.start_transaction():
            registry.consume(lookup, receipt, session=session, evaluated_at=now,
                             signature_b64=signature, verification_key=key)
            session.abort_transaction()
    assert db["tenant_ownership_recovery_decision_replays"].count_documents({}) == 0

    with client.start_session() as session:
        with session.start_transaction():
            registry.consume(lookup, receipt, session=session, evaluated_at=now,
                             signature_b64=signature, verification_key=key)
    assert db["tenant_ownership_recovery_decision_replays"].count_documents({}) == 1

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(OwnershipProviderEvidenceError, match="RECOVERY_DECISION_REPLAY"):
                registry.consume(lookup, receipt, session=session, evaluated_at=now,
                                 signature_b64=signature, verification_key=key)
            session.abort_transaction()

    # A second decision cannot be consumed for the same recovery case.
    second = RecoveryDecisionReceipt(
        receipt.authority_id, receipt.trust_root_reference, receipt.trust_root_fingerprint,
        "decision-second-" + uuid.uuid4().hex, "f" * 64, receipt.recovery_case_reference,
        receipt.recovery_case_fingerprint, receipt.successor_principal_id,
        receipt.quorum_fingerprint, receipt.conflict_check_fingerprint,
        receipt.notice_and_objection_fingerprint, receipt.appeal_status,
        receipt.issued_at, receipt.valid_until, receipt.revocation_reference,
    )
    second_signature = base64.b64encode(
        private.sign(recovery_decision_signing_payload(lookup, second))
    ).decode("ascii")
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(OwnershipProviderEvidenceError, match="RECOVERY_DECISION_REPLAY"):
                registry.consume(lookup, second, session=session, evaluated_at=now,
                                 signature_b64=second_signature, verification_key=key)
            session.abort_transaction()
