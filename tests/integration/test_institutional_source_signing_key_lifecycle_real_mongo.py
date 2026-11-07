"""Real replica-set certification for source signing-key lifecycle."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
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
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
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
            first = registry.enroll(
                source_system_id=source, key_id="key-1", public_key_bytes=first_key,
                valid_from=now, valid_until=now + timedelta(hours=4),
                governance_decision_reference="test-governance-001",
                approved_by_principal_id="test-approver",
                enrolled_at=now, idempotency_key="enroll-1", session=session,
            )
            assert first["key_id"] == "key-1"
            assert registry.resolve(
                source_system_id=source, key_id="key-1", evaluated_at=now,
                session=session,
            )["public_key_bytes"] == first_key

            with pytest.raises(SourceSigningKeyRegistryConflict, match="OUTSIDE_VALIDITY"):
                registry.resolve(
                    source_system_id=source, key_id="key-1",
                    evaluated_at=now - timedelta(seconds=1), session=session,
                )
            with pytest.raises(SourceSigningKeyRegistryConflict, match="OUTSIDE_VALIDITY"):
                registry.resolve(
                    source_system_id=source, key_id="key-1",
                    evaluated_at=now + timedelta(hours=4), session=session,
                )

            successor = registry.enroll(
                source_system_id=source, key_id="key-2", public_key_bytes=second_key,
                valid_from=now + timedelta(hours=1),
                valid_until=now + timedelta(hours=8),
                governance_decision_reference="test-governance-rotation-002",
                approved_by_principal_id="test-approver",
                enrolled_at=now, idempotency_key="enroll-2", session=session,
                rotation_id="rotation-001", supersedes_key_id="key-1",
                overlap_until=now + timedelta(hours=2),
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
                revoked_at=now + timedelta(hours=3),
                reason_reference="test-revocation-003",
                revoked_by_principal_id="test-revoker",
                governance_decision_reference="test-governance-revocation-003",
                idempotency_key="revoke-2", session=session,
            )
            assert revoked["event_type"] == "REVOKED"
            with pytest.raises(SourceSigningKeyRegistryConflict, match="REVOKED"):
                registry.resolve(
                    source_system_id=source, key_id="key-2",
                    evaluated_at=now + timedelta(hours=3), session=session,
                )
            # Historical evaluation before the revocation remains reproducible.
            assert registry.resolve(
                source_system_id=source, key_id="key-2",
                evaluated_at=now + timedelta(hours=2, minutes=30), session=session,
            )["key_id"] == "key-2"

            replay = registry.enroll(
                source_system_id=source, key_id="key-1", public_key_bytes=first_key,
                valid_from=now, valid_until=now + timedelta(hours=4),
                governance_decision_reference="test-governance-001",
                approved_by_principal_id="test-approver",
                enrolled_at=now, idempotency_key="enroll-1", session=session,
            )
            assert replay["key_id"] == "key-1"
            assert events.count_documents({"source_system_id": source}, session=session) == 3

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
