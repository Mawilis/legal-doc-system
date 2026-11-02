"""Real replica-set certification of composed provider preflight plus replay persistence."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from urllib.parse import urlparse

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo import MongoClient

from tools.eos.auth.tenant_ownership_evidence_validation import (
    OwnershipEvidenceValidationError,
    RecoveryDecisionEnvelope,
    RecoveryDecisionReplayRegistry,
    recovery_decision_message,
    signing_message,
)
from tools.eos.auth.tenant_ownership_provider_composition import (
    ProviderEvidenceCompositionError,
    ProviderEvidencePreflightRequest,
    TenantOwnershipProviderEvidenceComposer,
)
from tools.eos.auth.tenant_ownership_provider_ports import (
    RecoveryDecisionLookup,
    RecoveryDecisionReceipt,
    RegistryLookup,
    RegistrySnapshot,
    SigningReceipt,
    SubjectProofingReceipt,
    SubjectProofingRequest,
)
from tools.eos.auth.tenant_ownership_verifier import TenantOwnershipOperation


@pytest.fixture
def mongo():
    uri = os.environ.get("WILSY_ISSUE_300_REAL_MONGO_URI")
    if not uri:
        pytest.fail("WILSY_ISSUE_300_REAL_MONGO_URI_REQUIRED_FOR_REAL_MONGO_CERTIFICATE")
    parsed = urlparse(uri)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or parsed.port is None:
        pytest.fail("ISSUE_300_LOOPBACK_MONGO_WITH_EXPLICIT_PORT_REQUIRED")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    name = "issue_300_provider_composition_" + uuid.uuid4().hex
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or hello.get("isWritablePrimary") is not True:
            pytest.fail("ISSUE_300_APPROVED_DISPOSABLE_REPLICA_SET_REQUIRED")
        yield client, client[name]
    finally:
        client.drop_database(name)
        client.close()


def fingerprint(value: str) -> str:
    return sha256(value.encode()).hexdigest()


class Registry:
    def __init__(self, now: datetime):
        self.now = now

    def fetch_history(self, lookup: RegistryLookup):
        return (RegistrySnapshot(
            "registry-source", lookup.legal_entity_reference, "filing-1", "1",
            lookup.jurisdiction, "company", "ACTIVE",
            self.now - timedelta(seconds=1), self.now - timedelta(days=1),
            fingerprint("registry"), fingerprint("attributes"), None,
        ),)


class Identity:
    def __init__(self, now: datetime):
        self.now = now

    def verify_subject(self, request: SubjectProofingRequest):
        return SubjectProofingReceipt(
            "identity-provider", "identity-verifier", "IAL2",
            request.subject_reference, "identity-evidence", fingerprint("identity"),
            self.now - timedelta(seconds=1), self.now + timedelta(hours=1), "identity-revocation",
        )


class Revocation:
    def is_revoked(self, revocation_reference: str, at: datetime) -> bool:
        return False


class Binding:
    def subject_reference_for(self, tenant_id: str, principal_id: str) -> str:
        return "subject-" + principal_id


class SigningKeys:
    def __init__(self):
        self.private = Ed25519PrivateKey.generate()

    def key_status(self, key_reference: str, revision: int, at: datetime) -> str:
        return "ACTIVE" if (key_reference, revision) == ("signing-key", 3) else "UNTRUSTED"

    def public_key(self, key_reference: str, revision: int):
        if (key_reference, revision) != ("signing-key", 3):
            raise KeyError(key_reference)
        return self.private.public_key()


class Signer:
    def __init__(self, keys: SigningKeys, now: datetime):
        self.keys = keys
        self.now = now

    def sign_digest(self, request):
        return SigningReceipt(
            "hsm", "independent-custodian", request.key_reference, request.key_revision,
            "Ed25519", self.keys.private.sign(signing_message(request)).hex(),
            request.payload_digest, request.purpose, self.now - timedelta(seconds=1),
            "signing-audit", fingerprint("custody"),
        )


class RecoveryKeys:
    def __init__(self):
        self.private = Ed25519PrivateKey.generate()

    def recovery_key_status(self, authority_id, trust_root_reference, trust_root_fingerprint,
                            key_reference, revision, at):
        expected = ("independent-recovery", "recovery-root", fingerprint("root"),
                    "recovery-key", 2)
        return "ACTIVE" if (authority_id, trust_root_reference, trust_root_fingerprint,
                            key_reference, revision) == expected else "UNTRUSTED"

    def public_key(self, key_reference: str, revision: int):
        if (key_reference, revision) != ("recovery-key", 2):
            raise KeyError(key_reference)
        return self.private.public_key()


class Recovery:
    def __init__(self, keys: RecoveryKeys, now: datetime, unavailable: bool = False):
        self.keys = keys
        self.now = now
        self.unavailable = unavailable

    def verify_decision(self, lookup: RecoveryDecisionLookup):
        if self.unavailable:
            raise TimeoutError("independent recovery authority unavailable")
        receipt = RecoveryDecisionReceipt(
            "independent-recovery", "recovery-root", fingerprint("root"),
            "decision-1", fingerprint("decision"), lookup.recovery_case_reference,
            lookup.recovery_case_fingerprint, lookup.successor_principal_id,
            fingerprint("quorum"), fingerprint("conflicts"), fingerprint("notice"),
            "RESOLVED", self.now - timedelta(seconds=1), self.now + timedelta(hours=1),
            "recovery-revocation",
        )
        message = recovery_decision_message(
            lookup, receipt, "recovery-key", 2, "decision-nonce"
        )
        return RecoveryDecisionEnvelope(
            receipt, "recovery-key", 2, "Ed25519",
            self.keys.private.sign(message).hex(), "decision-nonce",
        )


def make_composer(now: datetime, recovery: Recovery, recovery_keys: RecoveryKeys):
    signing_keys = SigningKeys()
    return TenantOwnershipProviderEvidenceComposer(
        registry=Registry(now), identity=Identity(now), subject_revocation=Revocation(),
        principal_binding=Binding(), signer=Signer(signing_keys, now),
        signing_keys=signing_keys, recovery=recovery, recovery_keys=recovery_keys,
    )


def make_request(now: datetime, lookup: RecoveryDecisionLookup):
    return ProviderEvidencePreflightRequest(
        tenant_id=lookup.tenant_id,
        legal_entity_reference=lookup.legal_entity_reference,
        jurisdiction="ZA",
        principal_id=lookup.successor_principal_id,
        operation=TenantOwnershipOperation.GOVERNED_RECOVERY,
        purpose="GOVERNED_RECOVERY",
        evaluated_at=now,
        max_registry_age=timedelta(days=1),
        signing_key_reference="signing-key",
        signing_key_revision=3,
        recovery_lookup=lookup,
    )


def test_composed_preflight_persists_only_inside_real_mongo_transaction(mongo):
    client, db = mongo
    now = datetime.now(timezone.utc)
    lookup = RecoveryDecisionLookup(
        "tenant-" + uuid.uuid4().hex, "entity-1", "case-1", fingerprint("case"),
        "successor-1", now,
    )
    recovery_keys = RecoveryKeys()
    preflight = make_composer(now, Recovery(recovery_keys, now), recovery_keys).compose(
        make_request(now, lookup)
    )
    assert preflight.recovery_validation is not None

    registry = RecoveryDecisionReplayRegistry(db)
    with client.start_session() as session:
        with session.start_transaction():
            registry.consume_validated(preflight.recovery_validation, session=session)
            session.abort_transaction()
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 0

    with client.start_session() as session:
        with session.start_transaction():
            registry.consume_validated(preflight.recovery_validation, session=session)
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 1

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(OwnershipEvidenceValidationError, match="RECOVERY_DECISION_REPLAY"):
                registry.consume_validated(preflight.recovery_validation, session=session)
            session.abort_transaction()
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 1


def test_composed_external_recovery_outage_never_opens_or_writes_transaction(mongo):
    _client, db = mongo
    now = datetime.now(timezone.utc)
    lookup = RecoveryDecisionLookup(
        "tenant-" + uuid.uuid4().hex, "entity-1", "case-1", fingerprint("case"),
        "successor-1", now,
    )
    recovery_keys = RecoveryKeys()
    composer = make_composer(now, Recovery(recovery_keys, now, unavailable=True), recovery_keys)
    registry = RecoveryDecisionReplayRegistry(db)
    with pytest.raises(ProviderEvidenceCompositionError, match="INDEPENDENT_RECOVERY_PROVIDER_UNAVAILABLE"):
        composer.compose(make_request(now, lookup))
    assert db[registry.COLLECTION].count_documents({"tenant_id": lookup.tenant_id}) == 0
