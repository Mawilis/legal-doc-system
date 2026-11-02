"""Real-Mongo L8-6H transaction/rollback/replay integration certificate.

Requires a MongoDB replica set via TEST_DEPUTY_DEVICE_MONGO_URI.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from pymongo import MongoClient

from tools.eos.legal_operations.domain.deputy_device_provenance_authority import (
    DeputyDeviceProvenanceChallenge,
)
from tools.eos.legal_operations.domain.deputy_principal_binding import (
    DeputyPrincipalBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy
from tools.eos.legal_operations.registry.deputy_device_provenance_registry import (
    DeputyDeviceProvenanceRegistry,
    DeputyDeviceProvenanceRegistryConflictError,
)

MONGO_URI = os.getenv("TEST_DEPUTY_DEVICE_MONGO_URI")
pytestmark = pytest.mark.skipif(
    not MONGO_URI,
    reason="TEST_DEPUTY_DEVICE_MONGO_URI must point to a replica set",
)


class CurrentSessionAuthority:
    def is_session_current(
        self, tenant_id, user_id, session_reference, *, at=None, session=None
    ):
        assert tenant_id == "tenant-integration"
        assert user_id == "principal-integration"
        assert session_reference == "session-integration"
        assert session is not None and session.in_transaction
        return True


def _signature(private_key, challenge) -> bytes:
    der = private_key.sign(challenge.signed_payload(), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def test_mongo_transaction_rollback_atomic_consume_and_replay():
    assert MONGO_URI
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10_000)
    suffix = uuid.uuid4().hex
    database = client[f"deputy_device_cert_{suffix}"]
    challenges = database["challenges"]
    bindings = database["bindings"]
    try:
        tenant = "tenant-integration"
        principal = "principal-integration"
        deputy = Deputy(
            tenant_id=tenant,
            deputy_id="deputy-integration",
            sheriff_office_id="office-integration",
            display_name="Integration Deputy",
            badge_reference="badge-integration",
            evidence_reference="directory-integration",
        )
        binding = DeputyPrincipalBinding.from_deputy(
            principal_id=principal,
            deputy=deputy,
            bound_at=datetime.now(timezone.utc) - timedelta(days=1),
            evidence_reference="binding-integration",
        )
        bindings.insert_one(binding.to_dict())
        registry = DeputyDeviceProvenanceRegistry(
            challenges,
            auth_registry=CurrentSessionAuthority(),
            binding_collection=bindings,
        )
        registry.ensure_indexes()

        private_key = ec.generate_private_key(ec.SECP256R1())
        public_der = private_key.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        issued_at = datetime.now(timezone.utc)
        challenge = DeputyDeviceProvenanceChallenge.issue(
            binding=binding,
            session_reference="session-integration",
            challenge_id="challenge-integration",
            public_key_spki_der=public_der,
            nonce=os.urandom(32),
            issued_at=issued_at,
            expires_at=issued_at + timedelta(minutes=2),
        )

        # A caller abort must roll back the registry insert.
        with client.start_session() as session:
            session.start_transaction()
            registry.create(challenge, session=session)
            assert challenges.count_documents(
                {"tenant_id": tenant, "challenge_id": challenge.challenge_id},
                session=session,
            ) == 1
            session.abort_transaction()
        assert challenges.count_documents(
            {"tenant_id": tenant, "challenge_id": challenge.challenge_id}
        ) == 0

        # Commit the challenge, then atomically consume it in a second transaction.
        with client.start_session() as session:
            session.start_transaction()
            registry.create(challenge, session=session)
            session.commit_transaction()
        verified_at = datetime.now(timezone.utc)
        with client.start_session() as session:
            session.start_transaction()
            proof = registry.verify_and_consume(
                tenant_id=tenant,
                challenge_id=challenge.challenge_id,
                signature_p1363=_signature(private_key, challenge),
                verified_at=verified_at,
                session=session,
            )
            session.commit_transaction()

        row = challenges.find_one(
            {"tenant_id": tenant, "challenge_id": challenge.challenge_id}
        )
        assert row is not None
        assert row["consumed_at"] == verified_at.isoformat(timespec="microseconds")
        assert row["provenance"]["fingerprint"] == proof.fingerprint
        assert row["provenance_fingerprint"] == proof.fingerprint

        # A committed proof cannot be consumed again, even in a fresh transaction.
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(DeputyDeviceProvenanceRegistryConflictError):
                registry.verify_and_consume(
                    tenant_id=tenant,
                    challenge_id=challenge.challenge_id,
                    signature_p1363=_signature(private_key, challenge),
                    verified_at=datetime.now(timezone.utc),
                    session=session,
                )
            session.abort_transaction()
        final_row = challenges.find_one(
            {"tenant_id": tenant, "challenge_id": challenge.challenge_id}
        )
        assert final_row is not None
        assert final_row["provenance_fingerprint"] == proof.fingerprint
    finally:
        client.drop_database(database.name)
        client.close()
