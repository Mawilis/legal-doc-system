"""Replica-set certification for Electrum inbox idempotency and tenant binding."""
from datetime import datetime, timezone
import os
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.kennel.registry.electrum_payshap_completion_inbox_registry import (
    ElectrumCompletionInboxConflict,
    ElectrumPayShapCompletionInboxEvent,
    ElectrumPayShapCompletionInboxRegistry,
)
from tools.eos.kennel.registry.electrum_provider_account_binding_registry import (
    ElectrumProviderAccountBindingError,
    ElectrumProviderAccountBindingRegistry,
)

URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
NOW = datetime(2026, 11, 5, 8, 0, tzinfo=timezone.utc)


@pytest.fixture()
def mongo_collections():
    assert os.environ.get("TEST_VENDOR_MONGO_URI") == URI
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    assert client.admin.command("hello").get("isWritablePrimary") is True
    db = client[f"electrum_inbox_{uuid4().hex}"]
    inbox = db["completion_inbox"]
    bindings = db["account_bindings"]
    ElectrumPayShapCompletionInboxRegistry.ensure_indexes(inbox)
    ElectrumProviderAccountBindingRegistry.ensure_indexes(bindings)
    try:
        yield client, inbox, bindings
    finally:
        client.drop_database(db.name)
        client.close()


def event(*, amount=4000, message_id="message-1", key_id="electrum-key-1", received_at=NOW):
    return ElectrumPayShapCompletionInboxEvent(
        provider_name="ELECTRUM",
        message_id=message_id,
        message_created_at=NOW,
        uetr="8f14e45f-ea5e-4f5f-9c5d-8f14e45fea5e",
        transaction_reference="transaction-1",
        outcome="APPROVED",
        payment_scheme="ZA_RPP",
        payment_method="CreditTransfer",
        amount_minor=amount,
        currency="ZAR",
        settlement_date="2026-11-05",
        creditor_account_fingerprint="a" * 64,
        content_digest="b" * 64,
        signature_key_id=key_id,
        received_at=received_at,
    )


def test_exact_provider_replay_is_idempotent_across_receipt_time_and_key_rotation(mongo_collections):
    _, inbox, _ = mongo_collections
    first, replay = ElectrumPayShapCompletionInboxRegistry.create(event(), inbox)
    assert replay is False
    second, replay = ElectrumPayShapCompletionInboxRegistry.create(
        event(key_id="electrum-key-2", received_at=datetime(2026, 11, 5, 8, 0, 30, tzinfo=timezone.utc)),
        inbox,
    )
    assert replay is True
    assert second.fingerprint == first.fingerprint
    assert inbox.count_documents({"provider_name": "ELECTRUM"}) == 1


def test_divergent_message_and_duplicate_transaction_are_rejected(mongo_collections):
    _, inbox, _ = mongo_collections
    ElectrumPayShapCompletionInboxRegistry.create(event(), inbox)
    with pytest.raises(ElectrumCompletionInboxConflict, match="DIVERGENT_REPLAY"):
        ElectrumPayShapCompletionInboxRegistry.create(event(amount=5000), inbox)
    with pytest.raises(ElectrumCompletionInboxConflict, match="DIVERGENT_REPLAY"):
        ElectrumPayShapCompletionInboxRegistry.create(event(message_id="message-2"), inbox)
    assert inbox.count_documents({}) == 1


def test_processing_projection_is_caller_transactional_and_replay_safe(mongo_collections):
    client, inbox, _ = mongo_collections
    value, _ = ElectrumPayShapCompletionInboxRegistry.create(event(), inbox)
    with client.start_session() as session:
        with pytest.raises(RuntimeError, match="abort"):
            with session.start_transaction():
                ElectrumPayShapCompletionInboxRegistry.mark_processed(
                    value, collection=inbox, session=session,
                    processed_at=NOW, allocation_id="allocation-1",
                )
                raise RuntimeError("abort")
    assert inbox.find_one({"message_id": "message-1"})["processing_status"] == "PENDING"
    with client.start_session() as session:
        with session.start_transaction():
            ElectrumPayShapCompletionInboxRegistry.mark_processed(
                value, collection=inbox, session=session,
                processed_at=NOW, allocation_id="allocation-1",
            )
    assert inbox.find_one({"message_id": "message-1"})["processing_status"] == "PROCESSED"
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(ElectrumCompletionInboxConflict):
                ElectrumPayShapCompletionInboxRegistry.mark_processed(
                    value, collection=inbox, session=session,
                    processed_at=NOW, allocation_id="allocation-2",
                )


def test_provider_account_binding_is_opaque_unique_and_destination_scoped(mongo_collections):
    client, _, bindings = mongo_collections
    fingerprint = "c" * 64
    with client.start_session() as session:
        with session.start_transaction():
            created = ElectrumProviderAccountBindingRegistry.create(
                binding_id="binding-a",
                creditor_account_fingerprint=fingerprint,
                payment_destination_reference="destination-a",
                collection=bindings, session=session,
            )
    with client.start_session() as session:
        with session.start_transaction():
            resolved = ElectrumProviderAccountBindingRegistry.get_by_creditor_account_fingerprint(
                fingerprint, bindings, session=session
            )
    assert resolved["binding_id"] == created["binding_id"] == "binding-a"
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(ElectrumProviderAccountBindingError, match="ACCOUNT_BINDING_CONFLICT"):
                ElectrumProviderAccountBindingRegistry.create(
                    binding_id="binding-b",
                    creditor_account_fingerprint=fingerprint,
                    payment_destination_reference="destination-b",
                    collection=bindings, session=session,
                )


def test_revision_guarded_retry_backoff_preserves_pending_event(mongo_collections):
    client, inbox, _ = mongo_collections
    value, _ = ElectrumPayShapCompletionInboxRegistry.create(event(), inbox)
    retry_at = datetime(2026, 11, 5, 8, 0, 2, tzinfo=timezone.utc)
    with client.start_session() as session:
        with session.start_transaction():
            ElectrumPayShapCompletionInboxRegistry.schedule_retry(
                value,
                collection=inbox,
                session=session,
                expected_revision=0,
                expected_attempt_count=0,
                retry_at=retry_at,
                error_code="EXECUTION_TRUTH_NOT_UNIQUE",
            )
    saved = inbox.find_one({"message_id": "message-1"})
    assert saved["processing_status"] == "PENDING"
    assert saved["processing_revision"] == 1
    assert saved["attempt_count"] == 1
    assert saved["available_at"] == retry_at.isoformat()
    with client.start_session() as session:
        with session.start_transaction():
            ElectrumPayShapCompletionInboxRegistry.mark_processed(
                value,
                collection=inbox,
                session=session,
                processed_at=retry_at,
                allocation_id="allocation-1",
                expected_revision=1,
            )
    assert inbox.find_one({"message_id": "message-1"})["processing_status"] == "PROCESSED"
