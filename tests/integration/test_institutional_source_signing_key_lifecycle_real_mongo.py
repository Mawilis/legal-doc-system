"""Real replica-set certification for source signing-key lifecycle."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import base64
from dataclasses import replace
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

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
                identity_proofing_evidence_reference="identity-evidence-001",
                source_authority_evidence_reference="source-authority-evidence-001",
                proposed_at=now - timedelta(minutes=4), idempotency_key="propose-1", session=session,
            )
            with pytest.raises(SourceSigningKeyRegistryConflict, match="NOT_INDEPENDENTLY_APPROVED"):
                registry.resolve(source_system_id=source, key_id="key-1", evaluated_at=now, session=session)
            with pytest.raises(SourceSigningKeyRegistryConflict, match="MAKER_CHECKER_VIOLATION"):
                registry.approve(
                    source_system_id=source, key_id="key-1", approved_by_principal_id="test-requester",
                    governance_decision_reference="test-governance-001",
                    approval_evidence_reference="approval-evidence-001",
                    approved_at=now - timedelta(minutes=1), idempotency_key="approve-self", session=session,
                )
            registry.approve(
                source_system_id=source, key_id="key-1", approved_by_principal_id="test-approver",
                governance_decision_reference="test-governance-001",
                approval_evidence_reference="approval-evidence-001",
                approved_at=now - timedelta(minutes=1), idempotency_key="approve-1", session=session,
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
                identity_proofing_evidence_reference="identity-evidence-002",
                source_authority_evidence_reference="source-authority-evidence-002",
                proposed_at=now - timedelta(seconds=30), idempotency_key="propose-2", session=session,
                rotation_id="rotation-001", supersedes_key_id="key-1",
                overlap_until=now + timedelta(hours=2),
            )
            registry.approve(
                source_system_id=source, key_id="key-2", approved_by_principal_id="test-approver",
                governance_decision_reference="test-governance-rotation-002",
                approval_evidence_reference="approval-evidence-002",
                approved_at=now - timedelta(seconds=15), idempotency_key="approve-2", session=session,
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
                approval_evidence_reference="test-revocation-approval-evidence",
                revoked_by_principal_id="test-revoker",
                governance_decision_reference="test-governance-revocation-003",
                idempotency_key="revoke-2", session=session,
            )
            assert revoked["event_type"] == "REVOKED"
            assert revoked["approval_evidence_reference"] == "test-revocation-approval-evidence"
            with pytest.raises(SourceSigningKeyRegistryConflict, match="REVOKED"):
                registry.resolve(
                    source_system_id=source, key_id="key-2",
                    evaluated_at=now, session=session,
                )
            # Historical evaluation before the revocation remains reproducible.
            assert registry.resolve(
                source_system_id=source, key_id="key-2",
                evaluated_at=now - timedelta(seconds=10), session=session,
            )["key_id"] == "key-2"

            replay = registry.propose(
                source_system_id=source, key_id="key-1", public_key_bytes=first_key,
                valid_from=now - timedelta(hours=2), valid_until=now + timedelta(hours=4),
                proposed_by_principal_id="test-requester", proposal_reference="proposal-001",
                identity_proofing_evidence_reference="identity-evidence-001",
                source_authority_evidence_reference="source-authority-evidence-001",
                proposed_at=now - timedelta(minutes=4), idempotency_key="propose-1", session=session,
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
                identity_proofing_evidence_reference="synthetic-identity-evidence",
                source_authority_evidence_reference="synthetic-source-authority-evidence",
                proposed_at=now - timedelta(minutes=2), idempotency_key="propose-revocable", session=session,
            )
            registry.approve(
                source_system_id=source, key_id="key-revocable",
                approved_by_principal_id="synthetic-approver",
                governance_decision_reference="synthetic-governance-enroll",
                approval_evidence_reference="synthetic-approval-evidence",
                approved_at=now - timedelta(minutes=1), idempotency_key="approve-revocable", session=session,
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
                approval_evidence_reference="synthetic://revocation-approval/1",
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



def test_concurrent_rotation_revocation_and_idempotent_replay_are_serialized():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True, retryWrites=True)
    db_name = f"source_key_concurrency_{uuid.uuid4().hex}"
    db = client[db_name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        keys, events = db[KEY_COLLECTION], db[EVENT_COLLECTION]
        InstitutionalSourceSigningKeyLifecycleRegistry.ensure_indexes(keys, events)
        registry = InstitutionalSourceSigningKeyLifecycleRegistry(keys, events)
        now = datetime.now(timezone.utc).replace(microsecond=0)
        source = "synthetic-concurrency-source"
        base_public = _public_key()

        def seed(session):
            registry.propose(
                source_system_id=source, key_id="base-key", public_key_bytes=base_public,
                valid_from=now - timedelta(minutes=5), valid_until=now + timedelta(hours=2),
                proposed_by_principal_id="synthetic-maker", proposal_reference="base-proposal",
                identity_proofing_evidence_reference="identity-base",
                source_authority_evidence_reference="authority-base",
                proposed_at=now - timedelta(minutes=3), idempotency_key="base-propose",
                session=session,
            )
            registry.approve(
                source_system_id=source, key_id="base-key",
                approved_by_principal_id="synthetic-approver",
                governance_decision_reference="base-approval",
                approval_evidence_reference="base-approval-evidence",
                approved_at=now - timedelta(minutes=2), idempotency_key="base-approve",
                session=session,
            )

        with client.start_session() as session:
            session.with_transaction(seed)

        rotation_barrier = Barrier(2)

        def rotate(key_id: str):
            public = _public_key()
            first_attempt = True
            def callback(session):
                nonlocal first_attempt
                if first_attempt:
                    first_attempt = False
                    rotation_barrier.wait(timeout=10)
                return registry.propose(
                    source_system_id=source, key_id=key_id, public_key_bytes=public,
                    valid_from=now - timedelta(seconds=1), valid_until=now + timedelta(hours=1),
                    proposed_by_principal_id=f"rotator-{key_id}",
                    proposal_reference=f"proposal-{key_id}",
                    identity_proofing_evidence_reference=f"identity-{key_id}",
                    source_authority_evidence_reference=f"authority-{key_id}",
                    proposed_at=now, idempotency_key=f"propose-{key_id}",
                    session=session,
                    rotation_id=f"rotation-{key_id}", supersedes_key_id="base-key",
                    overlap_until=now + timedelta(minutes=30),
                )
            with client.start_session() as session:
                return session.with_transaction(callback)

        rotation_results = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(rotate, "successor-a"), pool.submit(rotate, "successor-b")]
            for future in futures:
                try:
                    rotation_results.append(("success", future.result()))
                except SourceSigningKeyRegistryConflict as error:
                    rotation_results.append(("conflict", error.code))
        assert sum(outcome == "success" for outcome, _ in rotation_results) == 1
        assert sum(outcome == "conflict" for outcome, _ in rotation_results) == 1
        assert keys.count_documents({
            "source_system_id": source, "rotation.supersedes_key_id": "base-key",
        }) == 1

        revoke_barrier = Barrier(2)

        def revoke(revoker: str):
            first_attempt = True
            def callback(session):
                nonlocal first_attempt
                if first_attempt:
                    first_attempt = False
                    revoke_barrier.wait(timeout=10)
                return registry.revoke(
                    source_system_id=source, key_id="base-key", revoked_at=datetime.now(timezone.utc),
                    reason_reference=f"reason-{revoker}",
                    approval_evidence_reference=f"approval-{revoker}", revoked_by_principal_id=revoker,
                    governance_decision_reference=f"decision-{revoker}",
                    idempotency_key=f"revoke-{revoker}", session=session,
                )
            with client.start_session() as session:
                return session.with_transaction(callback)

        revoke_results = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(revoke, "revoker-a"), pool.submit(revoke, "revoker-b")]
            for future in futures:
                try:
                    revoke_results.append(("success", future.result()))
                except SourceSigningKeyRegistryConflict as error:
                    revoke_results.append(("conflict", error.code))
        assert sum(outcome == "success" for outcome, _ in revoke_results) == 1
        assert sum(outcome == "conflict" for outcome, _ in revoke_results) == 1
        assert events.count_documents({
            "source_system_id": source, "key_id": "base-key", "event_type": "REVOKED",
        }) == 1

        replay_source = "synthetic-concurrent-replay-source"
        replay_public = _public_key()
        replay_barrier = Barrier(2)

        def replay_proposal():
            first_attempt = True
            def callback(session):
                nonlocal first_attempt
                if first_attempt:
                    first_attempt = False
                    replay_barrier.wait(timeout=10)
                return registry.propose(
                    source_system_id=replay_source, key_id="replayed-key",
                    public_key_bytes=replay_public,
                    valid_from=now - timedelta(minutes=1), valid_until=now + timedelta(hours=1),
                    proposed_by_principal_id="replay-maker",
                    proposal_reference="same-proposal-reference",
                    identity_proofing_evidence_reference="replay-identity",
                    source_authority_evidence_reference="replay-authority",
                    proposed_at=now, idempotency_key="same-idempotency-key",
                    session=session,
                )
            with client.start_session() as session:
                return session.with_transaction(callback)

        replay_results = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(replay_proposal), pool.submit(replay_proposal)]
            for future in futures:
                try:
                    replay_results.append(("success", future.result()))
                except SourceSigningKeyRegistryConflict as error:
                    replay_results.append(("conflict", error.code))
        assert sum(outcome == "success" for outcome, _ in replay_results) == 1
        assert sum(outcome == "conflict" for outcome, _ in replay_results) == 1

        # A retry after the winning transaction must resolve to the original proposal.
        with client.start_session() as session:
            replay = registry.propose(
                source_system_id=replay_source, key_id="replayed-key",
                public_key_bytes=replay_public,
                valid_from=now - timedelta(minutes=1), valid_until=now + timedelta(hours=1),
                proposed_by_principal_id="replay-maker",
                proposal_reference="same-proposal-reference",
                identity_proofing_evidence_reference="replay-identity",
                source_authority_evidence_reference="replay-authority",
                proposed_at=now, idempotency_key="same-idempotency-key",
                session=session,
            )
        assert replay["key_id"] == "replayed-key"
        assert events.count_documents({
            "source_system_id": replay_source, "event_type": "PROPOSED",
        }) == 1
    finally:
        client.drop_database(db_name)
        client.close()
