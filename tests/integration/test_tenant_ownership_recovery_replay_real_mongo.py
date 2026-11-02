"""Real Mongo replica-set atomicity and replay certification for recovery decisions."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo import MongoClient

from tools.eos.auth.tenant_ownership_evidence_validation import (
    OwnershipEvidenceValidationError, RecoveryDecisionEnvelope,
    RecoveryDecisionReplayRegistry, recovery_decision_message,
    validate_recovery_decision,
)
from tools.eos.auth.tenant_ownership_provider_ports import (
    RecoveryDecisionLookup, RecoveryDecisionReceipt,
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
    name = "issue_300_recovery_replay_" + uuid.uuid4().hex
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or hello.get("isWritablePrimary") is not True:
            pytest.fail("ISSUE_300_APPROVED_DISPOSABLE_REPLICA_SET_REQUIRED")
        yield client, client[name]
    finally:
        client.drop_database(name)
        client.close()


class TrustProvider:
    def __init__(self):
        self.private_key = Ed25519PrivateKey.generate()
        self.unavailable = False

    def recovery_key_status(self, authority_id, trust_root_reference,
                            trust_root_fingerprint, key_reference, revision, at):
        if self.unavailable:
            raise TimeoutError("independent trust-list outage")
        if (authority_id, trust_root_reference, trust_root_fingerprint,
            key_reference, revision) != (
            "independent-recovery", "recovery-root", "b" * 64, "recovery-key", 1
        ):
            return "UNTRUSTED"
        return "ACTIVE"

    def public_key(self, key_reference, revision):
        if (key_reference, revision) != ("recovery-key", 1):
            raise KeyError(key_reference)
        return self.private_key.public_key()


def signed_decision(keys, *, tenant_id=None, case_reference=None,
                    case_fingerprint=None, successor="successor-1"):
    now = datetime.now(timezone.utc)
    lookup = RecoveryDecisionLookup(
        tenant_id or "tenant-" + uuid.uuid4().hex,
        "entity-1",
        case_reference or "case-" + uuid.uuid4().hex,
        case_fingerprint or "a" * 64,
        successor,
        now,
    )
    receipt = RecoveryDecisionReceipt(
        "independent-recovery", "recovery-root", "b" * 64,
        "decision-" + uuid.uuid4().hex, "c" * 64,
        lookup.recovery_case_reference, lookup.recovery_case_fingerprint,
        lookup.successor_principal_id, "d" * 64, "e" * 64, "f" * 64,
        "RESOLVED", now - timedelta(minutes=1), now + timedelta(hours=1), "revocation-1",
    )
    message = recovery_decision_message(lookup, receipt, "recovery-key", 1, "nonce-1")
    envelope = RecoveryDecisionEnvelope(
        receipt, "recovery-key", 1, "Ed25519",
        keys.private_key.sign(message).hex(), "nonce-1",
    )
    return lookup, envelope


def test_recovery_replay_ledger_is_atomic_and_replay_safe(mongo):
    client, db = mongo
    keys = TrustProvider()
    registry = RecoveryDecisionReplayRegistry(db)
    lookup, envelope = signed_decision(keys)
    validated = validate_recovery_decision(lookup, envelope, keys)

    # Validation happens before transaction; the transaction only persists receipt.
    with client.start_session() as session:
        with session.start_transaction():
            registry.consume_validated(validated, session=session)
            session.abort_transaction()
    assert db[registry.COLLECTION].count_documents({}) == 0

    with client.start_session() as session:
        with session.start_transaction():
            registry.consume_validated(validated, session=session)
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 1

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(OwnershipEvidenceValidationError, match="RECOVERY_DECISION_REPLAY"):
                registry.consume_validated(validated, session=session)
            session.abort_transaction()
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 1


def test_recovery_case_cannot_be_resolved_for_a_second_successor(mongo):
    client, db = mongo
    keys = TrustProvider()
    registry = RecoveryDecisionReplayRegistry(db)
    lookup, envelope = signed_decision(keys)
    first = validate_recovery_decision(lookup, envelope, keys)
    with client.start_session() as session:
        with session.start_transaction():
            registry.consume_validated(first, session=session)

    second_lookup, second_envelope = signed_decision(
        keys, tenant_id=lookup.tenant_id,
        case_reference=lookup.recovery_case_reference,
        case_fingerprint=lookup.recovery_case_fingerprint,
        successor="attacker-successor",
    )
    second = validate_recovery_decision(second_lookup, second_envelope, keys)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(OwnershipEvidenceValidationError, match="RECOVERY_DECISION_REPLAY"):
                registry.consume_validated(second, session=session)
            session.abort_transaction()
    assert db[registry.COLLECTION].count_documents(
        {"tenant_id": lookup.tenant_id, "recovery_case_reference": lookup.recovery_case_reference}
    ) == 1


def test_external_trust_provider_outage_denies_before_mongo_transaction(mongo):
    client, db = mongo
    keys = TrustProvider()
    keys.unavailable = True
    registry = RecoveryDecisionReplayRegistry(db)
    lookup, envelope = signed_decision(keys)
    with pytest.raises(OwnershipEvidenceValidationError, match="RECOVERY_KEY_STATUS_UNAVAILABLE"):
        validate_recovery_decision(lookup, envelope, keys)
    assert db[registry.COLLECTION].count_documents({}) == 0

    keys.unavailable = False
    validated = validate_recovery_decision(lookup, envelope, keys)
    with client.start_session() as session:
        with session.start_transaction():
            registry.consume_validated(validated, session=session)
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 1
