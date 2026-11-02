"""Real Mongo replica-set atomicity and replay certification for recovery decisions."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.auth.tenant_ownership_evidence_validation import (
    OwnershipEvidenceValidationError, RecoveryDecisionReplayRegistry,
)
from tools.eos.auth.tenant_ownership_provider_ports import RecoveryDecisionReceipt, RecoveryDecisionLookup


@pytest.fixture
def mongo():
    uri = os.environ.get("WILSY_ISSUE_300_REAL_MONGO_URI")
    if not uri:
        pytest.fail("WILSY_ISSUE_300_REAL_MONGO_URI_REQUIRED_FOR_REAL_MONGO_CERTIFICATE")
    parsed = urlparse(uri)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or parsed.port is None:
        pytest.fail("ISSUE_300_LOOPBACK_MONGO_WITH_EXPLICIT_PORT_REQUIRED")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    name = "issue_300_recovery_replay_" + uuid.uuid4().hex
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or hello.get("isWritablePrimary") is not True:
            pytest.fail("ISSUE_300_APPROVED_DISPOSABLE_REPLICA_SET_REQUIRED")
        yield client, client[name]
    finally:
        client.drop_database(name)
        client.close()


def fixture_decision():
    now = datetime.now(timezone.utc)
    lookup = RecoveryDecisionLookup(
        "tenant-" + uuid.uuid4().hex, "entity-1", "case-" + uuid.uuid4().hex,
        "a" * 64, "successor-1", now,
    )
    receipt = RecoveryDecisionReceipt(
        "independent-recovery", "recovery-root", "b" * 64,
        "decision-" + uuid.uuid4().hex, "c" * 64,
        lookup.recovery_case_reference, lookup.recovery_case_fingerprint,
        lookup.successor_principal_id, "d" * 64, "e" * 64, "f" * 64,
        "RESOLVED", now - timedelta(minutes=1), now + timedelta(hours=1), "revocation-1",
    )
    return lookup, receipt


def test_recovery_replay_ledger_is_atomic_and_replay_safe(mongo):
    client, db = mongo
    registry = RecoveryDecisionReplayRegistry(db)
    lookup, receipt = fixture_decision()

    # A consumed decision is not visible if the caller aborts its transaction.
    with client.start_session() as session:
        with session.start_transaction():
            registry.consume(lookup, receipt, session=session)
            session.abort_transaction()
    assert db[registry.COLLECTION].count_documents({}) == 0

    # The exact same decision may be consumed after the aborted transaction.
    with client.start_session() as session:
        with session.start_transaction():
            registry.consume(lookup, receipt, session=session)
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 1

    # Duplicate decision replay is rejected; abort the failed transaction.
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(OwnershipEvidenceValidationError, match="RECOVERY_DECISION_REPLAY"):
                registry.consume(lookup, receipt, session=session)
            session.abort_transaction()
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 1


def test_recovery_case_cannot_be_replayed_to_a_different_successor(mongo):
    client, db = mongo
    registry = RecoveryDecisionReplayRegistry(db)
    lookup, receipt = fixture_decision()
    with client.start_session() as session:
        with session.start_transaction():
            registry.consume(lookup, receipt, session=session)
    other = RecoveryDecisionLookup(
        lookup.tenant_id, lookup.legal_entity_reference, lookup.recovery_case_reference,
        lookup.recovery_case_fingerprint, "attacker-successor", lookup.evaluated_at,
    )
    other_receipt = RecoveryDecisionReceipt(
        receipt.authority_id, receipt.trust_root_reference, receipt.trust_root_fingerprint,
        "different-decision", "1" * 64, receipt.recovery_case_reference,
        receipt.recovery_case_fingerprint, "attacker-successor", receipt.quorum_fingerprint,
        receipt.conflict_check_fingerprint, receipt.notice_and_objection_fingerprint,
        receipt.appeal_status, receipt.issued_at, receipt.valid_until, receipt.revocation_reference,
    )
    with client.start_session() as session:
        with session.start_transaction():
            registry.consume(other, other_receipt, session=session)
    assert db[registry.COLLECTION].count_documents(
        {"tenant_id": lookup.tenant_id, "recovery_case_reference": lookup.recovery_case_reference}
    ) == 2



def test_real_mongo_composed_verification_denies_external_outage_then_commits(mongo):
    client, db = mongo
    registry = RecoveryDecisionReplayRegistry(db)
    lookup, receipt = fixture_decision()
    private_key = Ed25519PrivateKey.generate()

    class TrustProvider:
        unavailable = True

        def recovery_key_status(self, authority_id, trust_root_reference,
                                trust_root_fingerprint, key_reference, revision, at):
            if self.unavailable:
                raise TimeoutError("independent trust-list outage")
            if (authority_id, trust_root_reference, trust_root_fingerprint) != (
                "independent-recovery", "recovery-root", "b" * 64
            ):
                return "UNTRUSTED"
            return "ACTIVE"

        def public_key(self, key_reference, revision):
            if (key_reference, revision) != ("recovery-key", 1):
                raise KeyError(key_reference)
            return private_key.public_key()

    keys = TrustProvider()
    message = recovery_decision_message(lookup, receipt, "recovery-key", 1, "nonce-1")
    envelope = RecoveryDecisionEnvelope(
        receipt, "recovery-key", 1, "Ed25519",
        private_key.sign(message).hex(), "nonce-1",
    )

    # A trust-list outage must abort before any replay reservation is persisted.
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(OwnershipEvidenceValidationError, match="KEY_STATUS_UNAVAILABLE"):
                registry.consume_verified(lookup, envelope, keys, session=session)
            session.abort_transaction()
    assert db[registry.COLLECTION].count_documents({}) == 0

    # Once the independent provider is reachable, signature verification and
    # replay reservation commit atomically under the caller-owned transaction.
    keys.unavailable = False
    with client.start_session() as session:
        with session.start_transaction():
            registry.consume_verified(lookup, envelope, keys, session=session)
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 1
