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


def event(*, amount=4000, message_id="message-1", transaction_reference="transaction-1", key_id="electrum-key-1", received_at=NOW):
    return ElectrumPayShapCompletionInboxEvent(
        provider_name="ELECTRUM",
        message_id=message_id,
        message_created_at=NOW,
        uetr="8f14e45f-ea5e-4f5f-9c5d-8f14e45fea5e",
        transaction_reference=transaction_reference,
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
    with pytest.raises(ElectrumCompletionInboxConflict, match="DIVERGENT_REPLAY"):
        ElectrumPayShapCompletionInboxRegistry.create(
            event(message_id="message-3", transaction_reference="transaction-2"), inbox
        )
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


def test_signed_http_completion_to_real_inbox_empty_204_and_replay(mongo_collections, monkeypatch):
    import hashlib
    import json
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import jwt

    import tools.eos.api.electrum_payshap_completion_router as router
    from tools.eos.kennel.providers.electrum_payshap_completion import verify_electrum_http_message_signature

    client, inbox, _ = mongo_collections
    provider_private = ec.generate_private_key(ec.SECP256R1())
    provider_private_pem = provider_private.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    provider_public_pem = provider_private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    wilsy_private = ec.generate_private_key(ec.SECP256R1())
    wilsy_private_pem = wilsy_private.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    wilsy_public_pem = wilsy_private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    config = router.ElectrumTransportConfiguration(
        verification_keys={"electrum-sandbox-kid": provider_public_pem},
        signing_private_key=wilsy_private_pem,
        signing_key_id="wilsy-sandbox-kid",
        signing_issuer="wilsy-sandbox-issuer",
    )
    monkeypatch.setattr(router, "_transport_configuration", lambda: config)
    monkeypatch.setattr(
        router, "_runtime",
        lambda: router.ElectrumCompletionRuntime(client=client, database=inbox.database),
    )
    app = FastAPI()
    app.state.electrum_completion_indexes_ready = True
    app.state.electrum_settlement_worker_enabled = True
    app.include_router(router.router)
    http = TestClient(app)

    payload = {
        "schema": "PaymentStatusReport",
        "messageIdentifiers": {
            "messageIdentification": "sandbox-completion-001",
            "creationDateTime": NOW.isoformat(),
        },
        "originalMessageIdentifiers": {
            "messageIdentification": "sandbox-authorisation-001",
            "creationDateTime": NOW.isoformat(),
        },
        "paymentScheme": {"schema": "ZA_RPP"},
        "transactionIdentifiers": {
            "endToEndIdentification": "e2e-reference-001",
            "uetr": "8f14e45f-ea5e-4f5f-9c5d-8f14e45fea5e",
            "transactionIdentification": "sandbox-rrn-001",
        },
        "status": {"outcome": "APPROVED"},
        "originalTransactionData": {
            "paymentMethod": "CreditTransfer",
            "amounts": {"bankSettlementAmount": {"currency": "ZAR", "value": 40.00}},
            "settlementDate": "2026-11-05",
            "creditorAccount": {"proxy": {"schema": "CUSTOM", "value": "wilsy-sandbox-proxy"}},
        },
    }

    def send(value):
        body = json.dumps(value, separators=(",", ":")).encode()
        token = jwt.encode(
            {
                "iss": "electrum.co.za",
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "electrum.co.za/content-digest": hashlib.sha256(body).hexdigest(),
            },
            provider_private_pem,
            algorithm="ES256",
            headers={"kid": "electrum-sandbox-kid", "typ": "JWT"},
        )
        return http.post(router.ROUTE_PATH, content=body, headers={"x-jwt-signature": token})

    first = send(payload)
    assert first.status_code == 204
    assert first.content == b""
    verify_electrum_http_message_signature(
        b"", first.headers["x-jwt-signature"],
        verification_keys={"wilsy-sandbox-kid": wilsy_public_pem},
        issuer="wilsy-sandbox-issuer",
    )
    assert inbox.count_documents({"message_id": "sandbox-completion-001"}) == 1

    replay = send(payload)
    assert replay.status_code == 204
    assert replay.content == b""
    assert inbox.count_documents({"message_id": "sandbox-completion-001"}) == 1

    divergent = dict(payload)
    divergent["originalTransactionData"] = dict(payload["originalTransactionData"])
    divergent["originalTransactionData"]["amounts"] = {
        "bankSettlementAmount": {"currency": "ZAR", "value": 41.00}
    }
    conflict = send(divergent)
    assert conflict.status_code == 409
    assert inbox.count_documents({"message_id": "sandbox-completion-001"}) == 1
