"""Real-Mongo certification for the Payment Destination registry and resolver.

VERSION: v1.0.0-KENNEL-PAYMENT-DESTINATION-REGISTRY-MONGO-CERT
The test requires TEST_VENDOR_MONGO_URI and intentionally has no skip path.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Generator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection

from tools.eos.kennel.domain.payment_destination import PaymentDestination, PaymentDestinationError, PaymentDestinationStatus, PaymentDestinationVerificationState
from tools.eos.kennel.registry.payment_destination_registry import (PaymentDestinationCreateConflictError, PaymentDestinationEligibilityError, PaymentDestinationNotFoundError, PaymentDestinationPersistedRecordInvalidError, PaymentDestinationReferenceConflictError, PaymentDestinationRegistry,)


def _destination(tenant: str, beneficiary: str, *, status: PaymentDestinationStatus = PaymentDestinationStatus.ACTIVE, verification: PaymentDestinationVerificationState = PaymentDestinationVerificationState.VERIFIED, reference: str | None = None) -> PaymentDestination:
    now = datetime.now(timezone.utc)
    return PaymentDestination(f"pd-{uuid4().hex}", tenant, beneficiary, reference or f"ref-{uuid4().hex}", status, verification, now)


@pytest.fixture()
def context() -> Generator[tuple[MongoClient, Collection], None, None]:
    uri = os.environ.get("TEST_VENDOR_MONGO_URI")
    if not uri:
        raise RuntimeError("TEST_VENDOR_MONGO_URI is required for real-Mongo certification")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    db = client[f"payment_destination_cert_{uuid4().hex}"]
    collection = db["kennel_payment_destinations"]
    PaymentDestinationRegistry.ensure_indexes(collection)
    try:
        yield client, collection
    finally:
        client.drop_database(db.name)
        client.close()


def test_create_get_resolve_and_determinism(context: tuple[MongoClient, Collection]) -> None:
    _, collection = context; item = _destination("tenant-a", "beneficiary-a")
    assert PaymentDestinationRegistry.create(item, collection) == item
    assert PaymentDestinationRegistry.get("tenant-a", item.payment_destination_id, collection) == item
    resolved = PaymentDestinationRegistry.resolve("tenant-a", item.destination_reference, "beneficiary-a", collection)
    assert resolved.destination_fingerprint == item.fingerprint and resolved.destination_reference == item.destination_reference
    assert PaymentDestinationRegistry.resolve("tenant-a", item.destination_reference, "beneficiary-a", collection) == resolved


def test_exact_replay_and_identity_reference_conflicts(context: tuple[MongoClient, Collection]) -> None:
    _, collection = context; item = _destination("tenant-a", "b")
    assert PaymentDestinationRegistry.create(item, collection) == item
    assert PaymentDestinationRegistry.create(item, collection) == item
    divergent = PaymentDestination(item.payment_destination_id, item.tenant_id, "other", item.destination_reference, item.status, item.verification_state, item.created_at)
    with pytest.raises(PaymentDestinationCreateConflictError): PaymentDestinationRegistry.create(divergent, collection)
    ref_collision = _destination("tenant-a", "b2", reference=item.destination_reference)
    with pytest.raises(PaymentDestinationReferenceConflictError): PaymentDestinationRegistry.create(ref_collision, collection)


def test_tenant_and_beneficiary_isolation(context: tuple[MongoClient, Collection]) -> None:
    _, collection = context; item = _destination("tenant-a", "beneficiary-a"); PaymentDestinationRegistry.create(item, collection)
    with pytest.raises(PaymentDestinationNotFoundError): PaymentDestinationRegistry.get("tenant-b", item.payment_destination_id, collection)
    with pytest.raises(PaymentDestinationNotFoundError): PaymentDestinationRegistry.get_by_reference("tenant-b", item.destination_reference, collection)
    with pytest.raises(PaymentDestinationEligibilityError, match="BENEFICIARY_MISMATCH"): PaymentDestinationRegistry.resolve("tenant-a", item.destination_reference, "beneficiary-b", collection)
    other_tenant = _destination("tenant-b", "beneficiary-b", reference=item.destination_reference); PaymentDestinationRegistry.create(other_tenant, collection)


@pytest.mark.parametrize("verification", [PaymentDestinationVerificationState.UNVERIFIED, PaymentDestinationVerificationState.FAILED])
def test_ineligible_verification_states(context: tuple[MongoClient, Collection], verification: PaymentDestinationVerificationState) -> None:
    _, collection = context; item = _destination("t", "b", verification=verification); PaymentDestinationRegistry.create(item, collection)
    with pytest.raises(PaymentDestinationEligibilityError): PaymentDestinationRegistry.resolve("t", item.destination_reference, collection=collection)


def test_revocation_is_historical_and_idempotent(context: tuple[MongoClient, Collection]) -> None:
    _, collection = context; item = _destination("t", "b"); PaymentDestinationRegistry.create(item, collection); revoked_at = datetime.now(timezone.utc)
    revoked = PaymentDestinationRegistry.revoke("t", item.payment_destination_id, revoked_at, collection)
    assert revoked.status is PaymentDestinationStatus.REVOKED
    assert PaymentDestinationRegistry.revoke("t", item.payment_destination_id, revoked_at, collection) == revoked
    with pytest.raises(PaymentDestinationEligibilityError): PaymentDestinationRegistry.resolve("t", item.destination_reference, collection=collection)


def test_corruption_and_forbidden_fields_fail_closed(context: tuple[MongoClient, Collection]) -> None:
    _, collection = context; item = _destination("t", "b"); PaymentDestinationRegistry.create(item, collection)
    collection.update_one({"payment_destination_id": item.payment_destination_id}, {"$set": {"status": "UNKNOWN"}})
    with pytest.raises(PaymentDestinationPersistedRecordInvalidError): PaymentDestinationRegistry.get("t", item.payment_destination_id, collection)
    collection.delete_many({})
    with pytest.raises(PaymentDestinationError): PaymentDestination.from_persistence_dict({**item.to_persistence_dict(), "bank_account": "redacted"})


def test_caller_owned_transaction_read_write_and_abort(context: tuple[MongoClient, Collection]) -> None:
    client, collection = context; item = _destination("t", "b")
    with client.start_session() as session:
        session.start_transaction(); PaymentDestinationRegistry.create(item, collection, session=session)
        assert PaymentDestinationRegistry.get("t", item.payment_destination_id, collection, session=session) == item
        session.abort_transaction()
    with pytest.raises(PaymentDestinationNotFoundError): PaymentDestinationRegistry.get("t", item.payment_destination_id, collection)
    with client.start_session() as session:
        session.start_transaction(); PaymentDestinationRegistry.create(item, collection, session=session); session.commit_transaction()
    assert PaymentDestinationRegistry.get("t", item.payment_destination_id, collection) == item


def test_concurrent_duplicate_create_converges(context: tuple[MongoClient, Collection]) -> None:
    from concurrent.futures import ThreadPoolExecutor
    _, collection = context; item = _destination("t", "b")
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: PaymentDestinationRegistry.create(item, collection), range(2)))
    assert outcomes == [item, item] and collection.count_documents({"tenant_id": "t"}) == 1


def test_malformed_timestamp_and_fingerprint_rejected(context: tuple[MongoClient, Collection]) -> None:
    _, collection = context; item = _destination("t", "b"); PaymentDestinationRegistry.create(item, collection)
    collection.update_one({"payment_destination_id": item.payment_destination_id}, {"$set": {"created_at": "bad"}})
    with pytest.raises(PaymentDestinationPersistedRecordInvalidError): PaymentDestinationRegistry.get("t", item.payment_destination_id, collection)
    collection.update_one({"payment_destination_id": item.payment_destination_id}, {"$set": {"created_at": item.created_at, "destination_fingerprint": "0" * 128}})
    with pytest.raises(PaymentDestinationPersistedRecordInvalidError): PaymentDestinationRegistry.get("t", item.payment_destination_id, collection)


# ARTIFACT: test_payment_destination_registry_mongo.py
# VERSION: v1.0.0-KENNEL-PAYMENT-DESTINATION-REGISTRY-MONGO-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
