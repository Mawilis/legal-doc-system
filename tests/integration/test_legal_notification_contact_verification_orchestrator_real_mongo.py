"""Real-Mongo certificate for H7E Legal notification-contact completion."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha3_512
import os
import threading
import uuid
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactChannel,
    LegalNotificationContactVerification,
    LegalNotificationContactVerificationStatus,
)
from tools.eos.legal_operations.domain.legal_verified_notification_contact import (
    VerifiedLegalNotificationContact,
    VerifiedLegalNotificationContactStatus,
)
from tools.eos.legal_operations.orchestration.legal_notification_contact_verification_orchestrator import (
    LegalNotificationContactVerificationOrchestrationError,
    LegalNotificationContactVerificationOrchestrationRetryRequiredError,
    complete_legal_notification_contact_verification,
)
from tools.eos.legal_operations.registry.legal_notification_contact_verification_registry import (
    COLLECTION as VERIFICATION_COLLECTION,
    LegalNotificationContactVerificationRegistry,
)
from tools.eos.legal_operations.registry.legal_verified_notification_contact_registry import (
    COLLECTION as CONTACT_COLLECTION,
    VerifiedLegalNotificationContactRegistry,
)

VERSION = (
    "v1.0.0-L8-8H7E-LEGAL-NOTIFICATION-CONTACT-"
    "VERIFICATION-ORCHESTRATION-REAL-MONGO-CERT"
)

URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

NOW = datetime(2026, 10, 12, 18, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-legal-h7e"
PRINCIPAL = "principal-legal-h7e"
TOKEN_A = "legal-h7e-token-a"
TOKEN_B = "legal-h7e-token-b"
TOKEN_C = "legal-h7e-token-c"
ADDRESS_A = sha3_512(b"h7e-a@example.invalid").hexdigest()
ADDRESS_B = sha3_512(b"h7e-b@example.invalid").hexdigest()


def _digest(token: str) -> str:
    return sha3_512(token.encode("utf-8")).hexdigest()


@pytest.fixture()
def mongo_context() -> Any:
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)

    hello = client.admin.command("hello")
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    assert bool(hello.get("isWritablePrimary"))
    assert hello.get("logicalSessionTimeoutMinutes") is not None

    db_name = f"wilsy_h7e_vc_{uuid.uuid4().hex}"
    db = client[db_name]

    verification_collection = Collection(
        db,
        VERIFICATION_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    contact_collection = Collection(
        db,
        CONTACT_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )

    verification_registry = LegalNotificationContactVerificationRegistry(
        verification_collection
    )
    contact_registry = VerifiedLegalNotificationContactRegistry(
        contact_collection
    )

    verification_registry.ensure_indexes()
    contact_registry.ensure_indexes()

    try:
        yield (
            client,
            db,
            verification_collection,
            contact_collection,
            verification_registry,
            contact_registry,
        )
    finally:
        client.drop_database(db_name)
        client.close()


def _issue(
    registry: LegalNotificationContactVerificationRegistry,
    client: MongoClient[Any],
    *,
    verification_id: str,
    token: str,
    address_digest: str,
) -> LegalNotificationContactVerification:
    value = LegalNotificationContactVerification.issue(
        tenant_id=TENANT,
        verification_id=verification_id,
        principal_id=PRINCIPAL,
        channel=LegalNotificationContactChannel.EMAIL,
        address_digest=address_digest,
        token_digest=_digest(token),
        issued_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )

    with client.start_session() as session:
        session.start_transaction()
        try:
            persisted = registry.create(value, session=session)
            session.commit_transaction()
        except Exception:
            if session.in_transaction:
                session.abort_transaction()
            raise

    return persisted


def _complete(
    client: MongoClient[Any],
    verification_registry: LegalNotificationContactVerificationRegistry,
    contact_registry: VerifiedLegalNotificationContactRegistry,
    *,
    token: str,
    contact_id: str,
    observed_at: datetime,
) -> Any:
    with client.start_session() as session:
        session.start_transaction()
        try:
            result = complete_legal_notification_contact_verification(
                tenant_id=TENANT,
                contact_id=contact_id,
                verification_token=token,
                observed_at=observed_at,
                verification_registry=verification_registry,
                contact_registry=contact_registry,
                session=session,
            )
            session.commit_transaction()
            return result
        except Exception:
            if session.in_transaction:
                session.abort_transaction()
            raise


def test_real_topology_is_writable_replica_set_with_sessions(
    mongo_context: Any,
) -> None:
    client = mongo_context[0]
    hello = client.admin.command("hello")

    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert bool(hello["isWritablePrimary"])
    assert hello["logicalSessionTimeoutMinutes"] is not None


def test_real_fresh_completion_atomically_consumes_and_creates(
    mongo_context: Any,
) -> None:
    (
        client,
        _db,
        verification_collection,
        contact_collection,
        verification_registry,
        contact_registry,
    ) = mongo_context

    source = _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-a",
        token=TOKEN_A,
        address_digest=ADDRESS_A,
    )

    result = _complete(
        client,
        verification_registry,
        contact_registry,
        token=TOKEN_A,
        contact_id="h7e-contact-a",
        observed_at=NOW + timedelta(seconds=1),
    )

    assert result.authority_created is True
    assert result.verification.status is LegalNotificationContactVerificationStatus.CONSUMED
    assert result.contact.status is VerifiedLegalNotificationContactStatus.ACTIVE
    assert result.contact.contact_id == "h7e-contact-a"
    assert result.contact.address_digest == ADDRESS_A

    persisted_verification = verification_collection.find_one(
        {"verification_id": source.verification_id}
    )
    persisted_contact = contact_collection.find_one(
        {"contact_id": "h7e-contact-a"}
    )

    assert persisted_verification is not None
    assert persisted_verification["consumed_at"] is not None
    assert persisted_contact is not None
    assert persisted_contact["revoked_at"] is None


def test_real_same_address_retains_existing_authority_and_consumes_new_proof(
    mongo_context: Any,
) -> None:
    (
        client,
        _db,
        verification_collection,
        contact_collection,
        verification_registry,
        contact_registry,
    ) = mongo_context

    _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-same-1",
        token=TOKEN_A,
        address_digest=ADDRESS_A,
    )
    first = _complete(
        client,
        verification_registry,
        contact_registry,
        token=TOKEN_A,
        contact_id="h7e-contact-same",
        observed_at=NOW + timedelta(seconds=1),
    )

    _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-same-2",
        token=TOKEN_B,
        address_digest=ADDRESS_A,
    )
    second = _complete(
        client,
        verification_registry,
        contact_registry,
        token=TOKEN_B,
        contact_id="h7e-contact-unused",
        observed_at=NOW + timedelta(seconds=2),
    )

    assert first.contact.contact_id == "h7e-contact-same"
    assert second.contact.contact_id == "h7e-contact-same"
    assert second.authority_created is False

    assert contact_collection.count_documents({}) == 1
    assert verification_collection.count_documents(
        {"consumed_at": {"$ne": None}}
    ) == 2


def test_real_address_drift_revokes_old_and_creates_new_in_same_transaction(
    mongo_context: Any,
) -> None:
    (
        client,
        _db,
        _verification_collection,
        contact_collection,
        verification_registry,
        contact_registry,
    ) = mongo_context

    _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-drift-a",
        token=TOKEN_A,
        address_digest=ADDRESS_A,
    )
    _complete(
        client,
        verification_registry,
        contact_registry,
        token=TOKEN_A,
        contact_id="h7e-contact-old",
        observed_at=NOW + timedelta(seconds=1),
    )

    _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-drift-b",
        token=TOKEN_B,
        address_digest=ADDRESS_B,
    )
    replacement = _complete(
        client,
        verification_registry,
        contact_registry,
        token=TOKEN_B,
        contact_id="h7e-contact-new",
        observed_at=NOW + timedelta(seconds=2),
    )

    assert replacement.authority_created is True
    assert replacement.contact.address_digest == ADDRESS_B

    old = contact_collection.find_one({"contact_id": "h7e-contact-old"})
    new = contact_collection.find_one({"contact_id": "h7e-contact-new"})

    assert old is not None
    assert old["revoked_at"] is not None
    assert new is not None
    assert new["revoked_at"] is None


def test_real_caller_abort_rolls_back_verification_and_contact_mutation(
    mongo_context: Any,
) -> None:
    (
        client,
        _db,
        verification_collection,
        contact_collection,
        verification_registry,
        contact_registry,
    ) = mongo_context

    _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-abort",
        token=TOKEN_A,
        address_digest=ADDRESS_A,
    )

    with client.start_session() as session:
        session.start_transaction()

        result = complete_legal_notification_contact_verification(
            tenant_id=TENANT,
            contact_id="h7e-contact-abort",
            verification_token=TOKEN_A,
            observed_at=NOW + timedelta(seconds=1),
            verification_registry=verification_registry,
            contact_registry=contact_registry,
            session=session,
        )

        assert result.authority_created is True
        session.abort_transaction()

    row = verification_collection.find_one(
        {"verification_id": "h7e-verification-abort"}
    )
    assert row is not None
    assert row["consumed_at"] is None
    assert contact_collection.count_documents(
        {"contact_id": "h7e-contact-abort"}
    ) == 0


def test_real_consumed_provenance_replay_is_exact_and_mutation_free(
    mongo_context: Any,
) -> None:
    (
        client,
        _db,
        verification_collection,
        contact_collection,
        verification_registry,
        contact_registry,
    ) = mongo_context

    _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-replay",
        token=TOKEN_A,
        address_digest=ADDRESS_A,
    )

    first = _complete(
        client,
        verification_registry,
        contact_registry,
        token=TOKEN_A,
        contact_id="h7e-contact-replay",
        observed_at=NOW + timedelta(seconds=1),
    )

    before_verification = verification_collection.find_one(
        {"verification_id": "h7e-verification-replay"}
    )
    before_contact = contact_collection.find_one(
        {"contact_id": "h7e-contact-replay"}
    )

    replay = _complete(
        client,
        verification_registry,
        contact_registry,
        token=TOKEN_A,
        contact_id="ignored-replay-contact",
        observed_at=NOW + timedelta(seconds=2),
    )

    after_verification = verification_collection.find_one(
        {"verification_id": "h7e-verification-replay"}
    )
    after_contact = contact_collection.find_one(
        {"contact_id": "h7e-contact-replay"}
    )

    assert replay.authority_created is False
    assert replay.contact.fingerprint == first.contact.fingerprint
    assert before_verification == after_verification
    assert before_contact == after_contact
    assert contact_collection.count_documents({}) == 1


def test_real_invalid_consumed_replay_fails_closed_without_mutation(
    mongo_context: Any,
) -> None:
    (
        client,
        _db,
        verification_collection,
        contact_collection,
        verification_registry,
        contact_registry,
    ) = mongo_context

    _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-invalid-replay",
        token=TOKEN_A,
        address_digest=ADDRESS_A,
    )

    original = _complete(
        client,
        verification_registry,
        contact_registry,
        token=TOKEN_A,
        contact_id="h7e-contact-original",
        observed_at=NOW + timedelta(seconds=1),
    )

    contact_collection.delete_one(
        {"contact_id": original.contact.contact_id}
    )

    before_verification = verification_collection.find_one(
        {"verification_id": "h7e-verification-invalid-replay"}
    )

    with pytest.raises(
        LegalNotificationContactVerificationOrchestrationError
    ) as captured:
        _complete(
            client,
            verification_registry,
            contact_registry,
            token=TOKEN_A,
            contact_id="h7e-contact-new-invalid",
            observed_at=NOW + timedelta(seconds=2),
        )

    assert captured.value.code == "L8_8H7E_VERIFICATION_REPLAY_INVALID"
    assert contact_collection.count_documents({}) == 0

    after_verification = verification_collection.find_one(
        {"verification_id": "h7e-verification-invalid-replay"}
    )
    assert before_verification == after_verification


def test_real_competing_consumers_produce_one_durable_active_authority(
    mongo_context: Any,
) -> None:
    (
        client,
        _db,
        verification_collection,
        contact_collection,
        verification_registry,
        contact_registry,
    ) = mongo_context

    _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-race",
        token=TOKEN_C,
        address_digest=ADDRESS_A,
    )

    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    lock = threading.Lock()

    def contender(contact_id: str) -> None:
        try:
            with client.start_session() as session:
                session.start_transaction()
                barrier.wait()

                result = complete_legal_notification_contact_verification(
                    tenant_id=TENANT,
                    contact_id=contact_id,
                    verification_token=TOKEN_C,
                    observed_at=NOW + timedelta(seconds=1),
                    verification_registry=verification_registry,
                    contact_registry=contact_registry,
                    session=session,
                )

                session.commit_transaction()

                with lock:
                    outcomes.append(
                        f"PASS:{result.contact.contact_id}"
                    )
        except (
            LegalNotificationContactVerificationOrchestrationRetryRequiredError,
            LegalNotificationContactVerificationOrchestrationError,
            PyMongoError,
        ) as error:
            with lock:
                outcomes.append(f"REJECT:{type(error).__name__}")

    threads = [
        threading.Thread(
            target=contender,
            args=("h7e-contact-race-a",),
        ),
        threading.Thread(
            target=contender,
            args=("h7e-contact-race-b",),
        ),
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(outcomes) == 2
    assert sum(item.startswith("PASS:") for item in outcomes) == 1
    assert sum(item.startswith("REJECT:") for item in outcomes) == 1

    assert contact_collection.count_documents(
        {"revoked_at": None}
    ) == 1

    row = verification_collection.find_one(
        {"verification_id": "h7e-verification-race"}
    )
    assert row is not None
    assert row["consumed_at"] is not None


def test_real_database_contains_only_h7c_and_h7d_authority_collections(
    mongo_context: Any,
) -> None:
    (
        client,
        db,
        _verification_collection,
        _contact_collection,
        verification_registry,
        contact_registry,
    ) = mongo_context

    _issue(
        verification_registry,
        client,
        verification_id="h7e-verification-collections",
        token=TOKEN_A,
        address_digest=ADDRESS_A,
    )

    _complete(
        client,
        verification_registry,
        contact_registry,
        token=TOKEN_A,
        contact_id="h7e-contact-collections",
        observed_at=NOW + timedelta(seconds=1),
    )

    collections = set(db.list_collection_names())

    assert collections == {
        VERIFICATION_COLLECTION,
        CONTACT_COLLECTION,
    }


# ARTIFACT: test_legal_notification_contact_verification_orchestrator_real_mongo.py
# VERSION: v1.0.0-L8-8H7E-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-ORCHESTRATION-REAL-MONGO-CERT
# AUTHORITY: real-Mongo H7E atomic composition only
# TRANSACTION POSTURE: caller-owned transaction certified
# RAW TOKEN POSTURE: transient digest lookup only
# DISPATCH / DELIVERY AUTHORITY: none
# FINANCIAL AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
