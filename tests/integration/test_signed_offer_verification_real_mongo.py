"""Replica-set persistence certification for signer trust and verification records."""
from __future__ import annotations

import base64
import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.saas.hr.signed_offer_cryptographic_verification import (
    TRUST_COLLECTION,
    VERIFICATION_COLLECTION,
    VERIFICATION_EVENT_COLLECTION,
    CandidateSignerKeyTrustRecord,
    CandidateSignerKeyTrustRegistry,
    SignedOfferSignatureEnvelope,
    SignedOfferVerificationRegistry,
    canonical_signature_payload,
    encode_signature,
    verify_signed_offer_signature,
)

URI = os.getenv("HIRING_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")


def test_real_replica_set_persists_trusted_key_and_verified_offer_signature_atomically():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database_name = f"signed_offer_verification_{uuid.uuid4().hex}"
    db = client[database_name]
    now = datetime.now(timezone.utc)
    tenant = f"tenant-{uuid.uuid4().hex}"
    candidate = f"candidate-{uuid.uuid4().hex}"
    offer = f"offer-{uuid.uuid4().hex}"
    evidence = f"evidence-{uuid.uuid4().hex}"
    version = f"version-{uuid.uuid4().hex}"
    signer_key_id = f"signer-{uuid.uuid4().hex}"
    digest = hashlib.sha3_512(b"exact signed-offer binary").hexdigest()
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        trust_collection = db[TRUST_COLLECTION]
        verification_collection = db[VERIFICATION_COLLECTION]
        event_collection = db[VERIFICATION_EVENT_COLLECTION]
        CandidateSignerKeyTrustRegistry.ensure_indexes(trust_collection)
        SignedOfferVerificationRegistry.ensure_indexes(verification_collection, event_collection)
        trust_registry = CandidateSignerKeyTrustRegistry(trust_collection)
        verification_registry = SignedOfferVerificationRegistry(verification_collection, event_collection)

        private = Ed25519PrivateKey.generate()
        public = private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        trust = CandidateSignerKeyTrustRecord(
            tenant_id=tenant, candidate_id=candidate, signer_key_id=signer_key_id,
            public_key_b64url=base64.urlsafe_b64encode(public).decode("ascii").rstrip("="),
            key_fingerprint=hashlib.sha3_512(public).hexdigest(),
            valid_from=now - timedelta(days=1), valid_until=now + timedelta(days=1),
        )
        trust_collection.insert_one(trust.to_dict())

        signed_at = now - timedelta(seconds=5)
        payload = canonical_signature_payload(
            tenant_id=tenant, candidate_id=candidate, offer_id=offer,
            evidence_id=evidence, evidence_version_id=version,
            content_digest_sha3_512=digest, signer_key_id=signer_key_id,
            signed_at=signed_at,
        )
        envelope = SignedOfferSignatureEnvelope(
            signer_key_id=signer_key_id, signed_at=signed_at,
            signature_b64url=encode_signature(private.sign(payload)),
        )
        record = verify_signed_offer_signature(
            tenant_id=tenant, candidate_id=candidate, offer_id=offer,
            evidence_id=evidence, evidence_version_id=version,
            content_digest_sha3_512=digest, envelope=envelope,
            trust=trust, verified_at=now,
        )

        def transaction(callback):
            with client.start_session() as session:
                return session.with_transaction(
                    callback,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern(w="majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )

        def persist(session):
            resolved = trust_registry.get(
                tenant_id=tenant, candidate_id=candidate,
                signer_key_id=signer_key_id, session=session,
            )
            assert resolved.key_fingerprint == trust.key_fingerprint
            created = verification_registry.register(
                record, actor_principal_id="HR-DIRECTOR-001",
                idempotency_key="signed-offer-verify-001", session=session,
            )
            replay = verification_registry.register(
                record, actor_principal_id="HR-DIRECTOR-001",
                idempotency_key="signed-offer-verify-replay", session=session,
            )
            readback = verification_registry.get(
                tenant_id=tenant, offer_id=offer, evidence_id=evidence,
                evidence_version_id=version, session=session,
            )
            assert created.fingerprint == replay.fingerprint == readback.fingerprint
            return readback

        persisted = transaction(persist)
        assert persisted.verification_reference == record.verification_reference
        assert persisted.status.value == "VERIFIED"
        assert verification_collection.count_documents({"tenant_id": tenant}) == 1
        assert event_collection.count_documents({"tenant_id": tenant}) == 1
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()
