"""Authenticated signed-offer verification and acceptance integration on replica-set Mongo."""
from __future__ import annotations

import base64
import hashlib
import os
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern
from types import SimpleNamespace

import tools.eos.api.hiring_lifecycle_router as hiring_router
from tools.eos.api.errors import register_error_handlers
from tools.eos.saas.domain.candidate_evidence import CandidateEvidenceKind, CandidateEvidenceObjectMetadata
from tools.eos.saas.domain.hiring_lifecycle import EmploymentOffer, OfferDecision, OfferTerms, OfferStatus
from tools.eos.saas.hr.candidate_evidence_registry import (
    COLLECTION as EVIDENCE_COLLECTION, EVENT_COLLECTION as EVIDENCE_EVENT_COLLECTION,
    CandidateEvidenceRegistry,
)
from tools.eos.saas.hr.hiring_lifecycle_registry import (
    CANDIDATE_COLLECTION, OFFER_COLLECTION, EVENT_COLLECTION, HiringLifecycleRegistry,
)
from tools.eos.saas.hr.signed_offer_cryptographic_verification import (
    TRUST_COLLECTION, CandidateSignerKeyTrustRecord, CandidateSignerKeyTrustRegistry,
    canonical_signature_payload, encode_signature,
)

URI = os.getenv("HIRING_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")


def test_authenticated_signed_offer_verification_is_required_before_acceptance(monkeypatch):
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database_name = f"signed_offer_http_{uuid.uuid4().hex}"
    db = client[database_name]
    now = datetime.now(timezone.utc)
    tenant = f"tenant-{uuid.uuid4().hex}"
    director = f"principal-{uuid.uuid4().hex}"
    candidate_id = f"candidate-{uuid.uuid4().hex}"
    offer_id = f"offer-{uuid.uuid4().hex}"
    evidence_id = f"evidence-{uuid.uuid4().hex}"
    version_id = f"version-{uuid.uuid4().hex}"
    signer_key_id = f"signer-{uuid.uuid4().hex}"
    payload_bytes = b"exact signed offer PDF bytes"
    digest = hashlib.sha3_512(payload_bytes).hexdigest()
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        hiring_registry = HiringLifecycleRegistry(
            db[CANDIDATE_COLLECTION], db[OFFER_COLLECTION], db[EVENT_COLLECTION],
        )
        evidence_registry = CandidateEvidenceRegistry(
            db[EVIDENCE_COLLECTION], db[EVIDENCE_EVENT_COLLECTION],
        )
        HiringLifecycleRegistry.ensure_indexes(
            db[CANDIDATE_COLLECTION], db[OFFER_COLLECTION], db[EVENT_COLLECTION],
        )
        CandidateEvidenceRegistry.ensure_indexes(
            db[EVIDENCE_COLLECTION], db[EVIDENCE_EVENT_COLLECTION],
        )

        def transaction(callback):
            with client.start_session() as session:
                return session.with_transaction(
                    callback,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern(w="majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )

        terms = OfferTerms(
            position_title="Operations Analyst", employment_type="PERMANENT",
            work_location="Johannesburg", currency="ZAR",
            gross_compensation_minor=72000000, pay_frequency="MONTHLY",
            start_date=date.today() + timedelta(days=30),
            expires_at=now + timedelta(days=7),
        )
        draft = EmploymentOffer(
            tenant_id=tenant, offer_id=offer_id, requisition_id="REQ-SIGNED-1",
            candidate_id=candidate_id, terms=terms,
            prepared_by_principal_id=director, created_at=now,
        )
        def create_and_send(session):
            hiring_registry.create_offer(
                draft, actor_principal_id=director, occurred_at=now,
                session=session, idempotency_key="offer-create",
            )
            current = hiring_registry.get_offer(tenant_id=tenant, offer_id=offer_id, session=session)
            submitted_at = now + timedelta(minutes=1)
            updated = current.submit(actor_principal_id=director, submitted_at=submitted_at, expected_revision=1)
            current = hiring_registry.transition_offer(
                current=current, updated=updated, actor_principal_id=director,
                action="OFFER_SUBMITTED", occurred_at=submitted_at,
                expected_revision=1, session=session, idempotency_key="offer-submit",
            )
            decision_at = now + timedelta(minutes=2)
            updated = current.decide(
                OfferDecision(
                    decision_id="decision-signed-1", actor_principal_id=director,
                    approved=True, reason="Approved", decided_at=decision_at,
                ),
                expected_revision=2,
            )
            current = hiring_registry.transition_offer(
                current=current, updated=updated, actor_principal_id=director,
                action="OFFER_APPROVED", occurred_at=decision_at,
                expected_revision=2, session=session, idempotency_key="offer-approve",
            )
            sent_at = now + timedelta(minutes=3)
            updated = current.send(actor_principal_id=director, sent_at=sent_at, expected_revision=3)
            return hiring_registry.transition_offer(
                current=current, updated=updated, actor_principal_id=director,
                action="OFFER_SENT", occurred_at=sent_at,
                expected_revision=3, session=session, idempotency_key="offer-send",
            )
        sent_offer = transaction(create_and_send)
        assert sent_offer.status is OfferStatus.SENT

        evidence = CandidateEvidenceObjectMetadata(
            tenant_id=tenant, candidate_id=candidate_id, evidence_id=evidence_id,
            evidence_version_id=version_id, evidence_kind=CandidateEvidenceKind.SIGNED_OFFER,
            media_type="application/pdf", original_filename="signed-offer.pdf",
            byte_length=len(payload_bytes), content_digest_sha3_512=digest,
            storage_provider_id="aws_s3", storage_object_reference="opaque-object-reference",
            object_version_reference="opaque-version-reference",
            provider_integrity_reference="opaque-provider-etag",
            ingestion_reference=f"ING-{uuid.uuid4().hex}",
            created_at=now, created_by_principal_id=director, offer_id=offer_id,
        )
        transaction(lambda session: evidence_registry.register(
            evidence, actor_principal_id=director,
            idempotency_key="signed-offer-custody", session=session,
        ))

        private = Ed25519PrivateKey.generate()
        public = private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        trust = CandidateSignerKeyTrustRecord(
            tenant_id=tenant, candidate_id=candidate_id, signer_key_id=signer_key_id,
            public_key_b64url=base64.urlsafe_b64encode(public).decode("ascii").rstrip("="),
            key_fingerprint=hashlib.sha3_512(public).hexdigest(),
            valid_from=now - timedelta(days=1), valid_until=now + timedelta(days=30),
        )
        db[TRUST_COLLECTION].insert_one(trust.to_dict())
        signed_at = now + timedelta(minutes=4)
        signed_payload = canonical_signature_payload(
            tenant_id=tenant, candidate_id=candidate_id, offer_id=offer_id,
            evidence_id=evidence_id, evidence_version_id=version_id,
            content_digest_sha3_512=digest, signer_key_id=signer_key_id,
            signed_at=signed_at,
        )
        signature = encode_signature(private.sign(signed_payload))

        monkeypatch.setattr(hiring_router, "get_client", lambda: client)
        monkeypatch.setattr(hiring_router, "get_database", lambda: db)
        context = SimpleNamespace(
            tenant_id=tenant,
            identity=SimpleNamespace(identity_id=director),
        )
        app = FastAPI()
        app.include_router(hiring_router.router, prefix="/api")
        register_error_handlers(app, debug=False)
        app.dependency_overrides[hiring_router._OFFER_ACCEPT] = lambda: context

        with TestClient(app, raise_server_exceptions=False) as http:
            verified = http.post(
                f"/api/hr/hiring/offers/{offer_id}/evidence/{evidence_id}/{version_id}/verify",
                headers={"Idempotency-Key": "signed-offer-verify"},
                json={
                    "signer_key_id": signer_key_id,
                    "signed_at": signed_at.isoformat(),
                    "signature_b64url": signature,
                },
            )
            assert verified.status_code == 200, verified.text
            verification_reference = verified.json()["verification_reference"]

            accepted = http.post(
                f"/api/hr/hiring/offers/{offer_id}/accept",
                headers={"Idempotency-Key": "signed-offer-accept"},
                json={
                    "expected_revision": 4,
                    "evidence_reference": evidence_id,
                    "evidence_fingerprint": digest,
                    "evidence_version_id": version_id,
                },
            )
            assert accepted.status_code == 200, accepted.text
            assert accepted.json()["status"] == "ACCEPTED"
            assert accepted.json()["acceptance"]["signature_verification_reference"] == verification_reference

        assert db[TRUST_COLLECTION].count_documents({"tenant_id": tenant}) == 1
        assert db["wilsy_hr_signed_offer_verifications"].count_documents({"tenant_id": tenant}) == 1
        assert db["wilsy_hr_signed_offer_verification_events"].count_documents({"tenant_id": tenant}) == 1
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()
