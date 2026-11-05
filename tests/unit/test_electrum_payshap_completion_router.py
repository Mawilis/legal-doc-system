from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch
import hashlib
import json

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from fastapi import FastAPI
from fastapi.testclient import TestClient
import jwt

import tools.eos.api.electrum_payshap_completion_router as router_module
from tools.eos.kennel.providers.electrum_payshap_completion import (
    VerifiedElectrumMessage,
    verify_electrum_http_message_signature,
)
from tools.eos.kennel.registry.electrum_payshap_completion_inbox_registry import (
    ElectrumPayShapCompletionInboxEvent,
)


def _keypair():
    private = ec.generate_private_key(ec.SECP256R1())
    private_pem = private.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def _payload():
    return {
        "schema": "PaymentStatusReport",
        "messageIdentifiers": {
            "messageIdentification": "message-router-1",
            "creationDateTime": "2026-11-05T08:00:00Z",
        },
        "transactionIdentifiers": {
            "uetr": "8f14e45f-ea5e-4f5f-9c5d-8f14e45fea5e",
            "transactionIdentification": "transaction-router-1",
        },
        "status": {"outcome": "APPROVED"},
        "paymentScheme": {"schema": "ZA_RPP"},
        "originalTransactionData": {
            "paymentMethod": "CreditTransfer",
            "amounts": {"bankSettlementAmount": {"currency": "ZAR", "value": 10.00}},
            "creditorAccount": {"proxy": {"schema": "CUSTOM", "value": "proxy-1"}},
        },
    }


def _provider_signature(body, private):
    claims = {
        "iss": "electrum.co.za",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "electrum.co.za/content-digest": hashlib.sha256(body).hexdigest(),
    }
    return jwt.encode(
        claims, private, algorithm="ES256",
        headers={"kid": "electrum-key-1", "typ": "JWT"},
    )


def _setup(monkeypatch, *, replay=False):
    provider_private, provider_public = _keypair()
    wilsy_private, wilsy_public = _keypair()
    config = router_module.ElectrumTransportConfiguration(
        verification_keys={"electrum-key-1": provider_public},
        signing_private_key=wilsy_private,
        signing_key_id="wilsy-key-1",
        signing_issuer="wilsy-onboarding-issuer",
    )
    collection = Mock()
    db = Mock()
    db.get_collection.return_value.with_options.return_value = collection
    runtime = router_module.ElectrumCompletionRuntime(client=Mock(), database=db)
    monkeypatch.setattr(router_module, "_transport_configuration", lambda: config)
    monkeypatch.setattr(router_module, "_runtime", lambda: runtime)
    event = router_module.create_electrum_completion_inbox_event(
        _payload(),
        verified_message=VerifiedElectrumMessage(
            key_id="electrum-key-1",
            issuer="electrum.co.za",
            issued_at=int(datetime.now(timezone.utc).timestamp()),
            content_digest=hashlib.sha256(json.dumps(_payload(), separators=(",", ":")).encode()).hexdigest(),
        ),
        received_at=datetime.now(timezone.utc),
    )
    monkeypatch.setattr(
        router_module.ElectrumPayShapCompletionInboxRegistry,
        "create",
        lambda *args, **kwargs: (event, replay),
    )
    app = FastAPI()
    app.include_router(router_module.router)
    return TestClient(app), provider_private, wilsy_public, config


def test_http_ingress_persists_inbox_and_returns_signed_202(monkeypatch):
    client, provider_private, wilsy_public, config = _setup(monkeypatch)
    body = json.dumps(_payload(), separators=(",", ":")).encode()
    response = client.post(
        router_module.ROUTE_PATH,
        content=body,
        headers={"x-jwt-signature": _provider_signature(body, provider_private)},
    )
    assert response.status_code == 202
    assert response.json()["accepted"] is True
    assert response.json()["settlement_eligible"] is True
    verified = verify_electrum_http_message_signature(
        response.content,
        response.headers["x-jwt-signature"],
        verification_keys={"wilsy-key-1": wilsy_public},
        issuer=config.signing_issuer,
    )
    assert verified.content_digest == hashlib.sha256(response.content).hexdigest()


def test_http_ingress_replay_still_returns_signed_202(monkeypatch):
    client, provider_private, wilsy_public, config = _setup(monkeypatch, replay=True)
    body = json.dumps(_payload(), separators=(",", ":")).encode()
    response = client.post(
        router_module.ROUTE_PATH,
        content=body,
        headers={"x-jwt-signature": _provider_signature(body, provider_private)},
    )
    assert response.status_code == 202
    assert response.json()["replayed"] is True
    verify_electrum_http_message_signature(
        response.content, response.headers["x-jwt-signature"],
        verification_keys={"wilsy-key-1": wilsy_public}, issuer=config.signing_issuer,
    )


def test_http_ingress_rejects_missing_signature_with_signed_401(monkeypatch):
    client, _, wilsy_public, config = _setup(monkeypatch)
    response = client.post(router_module.ROUTE_PATH, content=json.dumps(_payload()).encode())
    assert response.status_code == 401
    assert response.json()["accepted"] is False
    verify_electrum_http_message_signature(
        response.content, response.headers["x-jwt-signature"],
        verification_keys={"wilsy-key-1": wilsy_public}, issuer=config.signing_issuer,
    )
