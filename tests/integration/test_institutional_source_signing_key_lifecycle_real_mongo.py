"""Real replica-set certification for source signing-key lifecycle."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import base64
from dataclasses import replace
import uuid

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from tools.eos.security.institutional_signer_source_adapters import (
    InstitutionalSignerSourceEvidence,
    InstitutionalSignerSourceLookup,
    InstitutionalSignerSourceAdapterError,
    RegistryBackedEd25519InstitutionalSignerSourceResponseAuthenticator,
    _canonical_source_response_payload,
)
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.security.institutional_source_signing_key_registry import (
    KEY_COLLECTION,
    EVENT_COLLECTION,
    InstitutionalSourceSigningKeyLifecycleRegistry,
    SourceSigningKeyRegistryConflict,
)

URI = __import__("os").getenv("INSTITUTIONAL_SOURCE_KEY_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="INSTITUTIONAL_SOURCE_KEY_TEST_MONGODB_URI is not configured")


def _public_key():
    private = Ed25519PrivateKey.generate()
    return private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def test_enrollment_expiry_revocation_and_rotation_are_transactional():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True)
    db_name = f"source_key_lifecycle_{uuid.uuid4().hex}"
    db = client[db_name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        keys, events = db[KEY_COLLECTION], db[EVENT_COLLECTION]
        InstitutionalSourceSigningKeyLifecycleRegistry.ensure_indexes(keys, events)
        registry = InstitutionalSourceSigningKeyLifecycleRegistry(keys, events)
        now = datetime.now(timezone.utc).replace(microsecond=0)
        source = "synthetic-test-source"
        first_key = _public_key()
        second_key = _public_key()

        def transaction(session):
            first = registry.propose(
                source_system_id=source, key_id="key-1", public_key_bytes=first_key,
                valid_from=now - timedelta(hours=2), valid_until=now + timedelta(hours=4),
                proposed_by_principal_id="test-requester", proposal_reference="proposal-001",
                proposed_at=now, idempotency_key="propose-1", session=session,
            )
            with pytest.raises(SourceSigningKeyRegistryConflict, match="NOT_INDEPENDENTLY_APPROVED"):
                registry.resolve(source_system_id=source, key_id="key-1", evaluated_at=now, session=session)
            with pytest.raises(SourceSigningKeyRegistryConflict, match="MAKER_CHECKER_VIOLATION"):
                registry.approve(
                    source_system_id=source, key_id="key-1", approved_by_principal_id="test-requester",
                    governance_decision_reference="test-governance-001",
                    approval_evidence_reference="approval-evidence-001",
                    approved_at=now, idempotency_key="approve-self", session=session,
                )
            registry.approve(
                source_system_id=source, key_id="key-1", approved_by_principal_id="test-approver",
                governance_decision_reference="test-governance-001",
                approval_evidence_reference="approval-evidence-001",
                approved_at=now, idempotency_key="approve-1", session=session,
            )
            assert first["key_id"] == "key-1"
            assert registry.resolve(
                source_system_id=source, key_id="key-1", evaluated_at=now,
                session=session,
            )["public_key_bytes"] == first_key

            with pytest.raises(SourceSigningKeyRegistryConflict, match="OUTSIDE_VALIDITY"):
                registry.resolve(
                    source_system_id=source, key_id="key-1",
                    evaluated_at=now - timedelta(hours=3), session=session,
                )
            with pytest.raises(SourceSigningKeyRegistryConflict, match="OUTSIDE_VALIDITY"):
                registry.resolve(
                    source_system_id=source, key_id="key-1",
                    evaluated_at=now + timedelta(hours=4), session=session,
                )

            successor = registry.propose(
                source_system_id=source, key_id="key-2", public_key_bytes=second_key,
                valid_from=now - timedelta(hours=1), valid_until=now + timedelta(hours=8),
                proposed_by_principal_id="test-rotator", proposal_reference="proposal-002",
                proposed_at=now, idempotency_key="propose-2", session=session,
                rotation_id="rotation-001", supersedes_key_id="key-1",
                overlap_until=now + timedelta(hours=2),
            )
            registry.approve(
                source_system_id=source, key_id="key-2", approved_by_principal_id="test-approver",
                governance_decision_reference="test-governance-rotation-002",
                approval_evidence_reference="approval-evidence-002",
                approved_at=now, idempotency_key="approve-2", session=session,
            )
            assert successor["rotation"]["supersedes_key_id"] == "key-1"
            assert registry.resolve(
                source_system_id=source, key_id="key-1",
                evaluated_at=now + timedelta(hours=1, minutes=30), session=session,
            )["key_id"] == "key-1"
            assert registry.resolve(
                source_system_id=source, key_id="key-2",
                evaluated_at=now + timedelta(hours=3), session=session,
            )["key_id"] == "key-2"
            with pytest.raises(SourceSigningKeyRegistryConflict, match="ROTATION_OVERLAP_ENDED"):
                registry.resolve(
                    source_system_id=source, key_id="key-1",
                    evaluated_at=now + timedelta(hours=2), session=session,
                )

            revoked = registry.revoke(
                source_system_id=source, key_id="key-2",
                revoked_at=now,
                reason_reference="test-revocation-003",
                revoked_by_principal_id="test-revoker",
                governance_decision_reference="test-governance-revocation-003",
                idempotency_key="revoke-2", session=session,
            )
            assert revoked["event_type"] == "REVOKED"
            with pytest.raises(SourceSigningKeyRegistryConflict, match="REVOKED"):
                registry.resolve(
                    source_system_id=source, key_id="key-2",
                    evaluated_at=now, session=session,
                )
            # Historical evaluation before the revocation remains reproducible.
            assert registry.resolve(
                source_system_id=source, key_id="key-2",
                evaluated_at=now - timedelta(minutes=1), session=session,
            )["key_id"] == "key-2"

            replay = registry.propose(
                source_system_id=source, key_id="key-1", public_key_bytes=first_key,
                valid_from=now - timedelta(hours=2), valid_until=now + timedelta(hours=4),
                proposed_by_principal_id="test-requester", proposal_reference="proposal-001",
                proposed_at=now, idempotency_key="propose-1", session=session,
            )
            assert replay["key_id"] == "key-1"
            assert events.count_documents({"source_system_id": source}, session=session) == 5

        with client.start_session() as session:
            session.with_transaction(
                transaction,
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    finally:
        client.drop_database(db_name)
        client.close()



def test_registry_backed_authenticator_observes_immediate_revocation():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True)
    db_name = f"source_key_revocation_{uuid.uuid4().hex}"
    db = client[db_name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        keys, events = db[KEY_COLLECTION], db[EVENT_COLLECTION]
        InstitutionalSourceSigningKeyLifecycleRegistry.ensure_indexes(keys, events)
        registry = InstitutionalSourceSigningKeyLifecycleRegistry(keys, events)
        now = datetime.now(timezone.utc).replace(microsecond=0)
        private = Ed25519PrivateKey.generate()
        public = private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        source = "synthetic-revocation-test-source"

        def transaction(session):
            registry.propose(
                source_system_id=source, key_id="key-revocable", public_key_bytes=public,
                valid_from=now - timedelta(minutes=5), valid_until=now + timedelta(hours=1),
                proposed_by_principal_id="synthetic-requester", proposal_reference="synthetic-proposal",
                proposed_at=now, idempotency_key="propose-revocable", session=session,
            )
            registry.approve(
                source_system_id=source, key_id="key-revocable",
                approved_by_principal_id="synthetic-approver",
                governance_decision_reference="synthetic-governance-enroll",
                approval_evidence_reference="synthetic-approval-evidence",
                approved_at=now, idempotency_key="approve-revocable", session=session,
            )
            lookup = InstitutionalSignerSourceLookup(
                tenant_id="WILSYTENANT-4CD2FZ4O",
                evidence_kind="IDENTITY_PROOFING",
                evidence_reference="synthetic://identity/record-1",
                subject_principal_id="synthetic-principal",
                certificate_fingerprint_sha256="a" * 64,
                evaluated_at=now,
            )
            response = InstitutionalSignerSourceEvidence(
                evidence_kind="IDENTITY_PROOFING",
                evidence_reference="synthetic://identity/record-1",
                tenant_id="WILSYTENANT-4CD2FZ4O",
                source_system_id=source,
                source_record_id="synthetic-record-1",
                source_revision="revision-1",
                subject_principal_id="synthetic-principal",
                certificate_fingerprint_sha256="a" * 64,
                evidence_fingerprint_sha256="b" * 64,
                status="ACTIVE",
                valid_from=now - timedelta(minutes=1),
                valid_until=now + timedelta(minutes=30),
                revoked=False,
                observed_at=now,
                response_signature_reference="synthetic://signature/1",
                response_signing_key_id="key-revocable",
                response_signature_base64=base64.b64encode(b"0" * 64).decode("ascii"),
            )
            response = replace(
                response,
                response_signature_base64=base64.b64encode(
                    private.sign(_canonical_source_response_payload(response))
                ).decode("ascii"),
            )
            authenticator = RegistryBackedEd25519InstitutionalSignerSourceResponseAuthenticator(
                registry=registry, session=session,
            )
            authenticator.authenticate_response(
                expected_source_system_id=source, lookup=lookup, response=response,
            )
            registry.revoke(
                source_system_id=source, key_id="key-revocable", revoked_at=now,
                reason_reference="synthetic://revocation/1",
                revoked_by_principal_id="synthetic-revoker",
                governance_decision_reference="synthetic-governance-revoke",
                idempotency_key="revoke-immediately", session=session,
            )
            with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
                authenticator.authenticate_response(
                    expected_source_system_id=source, lookup=lookup, response=response,
                )
            assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_SIGNING_KEY_NOT_CURRENT"

        with client.start_session() as session:
            session.with_transaction(
                transaction,
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    finally:
        client.drop_database(db_name)
        client.close()
