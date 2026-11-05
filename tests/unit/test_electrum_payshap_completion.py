from datetime import datetime, timezone
import hashlib
import json

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

from tools.eos.kennel.providers.electrum_payshap_completion import (
    ElectrumCompletionContractError,
    ElectrumMessageAuthenticationError,
    VerifiedElectrumMessage,
    normalize_electrum_payshap_completion,
    sign_electrum_http_message,
    verify_electrum_http_message_signature,
)

NOW = datetime(2026, 11, 5, 8, 0, tzinfo=timezone.utc)


def _keys():
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


def _signed(body, *, issuer="electrum.co.za", iat=None, key_id="electrum-key-1", algorithm="ES256"):
    private, public = _keys()
    claims = {
        "iss": issuer,
        "iat": int(NOW.timestamp()) if iat is None else iat,
        "electrum.co.za/content-digest": hashlib.sha256(body).hexdigest(),
    }
    token = jwt.encode(
        claims, private, algorithm=algorithm,
        headers={"kid": key_id, "typ": "JWT"},
    )
    return token, {key_id: public}


def _payload(outcome="APPROVED"):
    return {
        "schema": "PaymentStatusReport",
        "messageIdentifiers": {
            "messageIdentification": "electrum-message-001",
            "creationDateTime": "2026-11-05T08:00:00Z",
        },
        "originalMessageIdentifiers": {
            "messageIdentification": "original-message-1",
            "creationDateTime": "2026-11-05T07:59:00Z",
        },
        "transactionIdentifiers": {
            "endToEndIdentification": "e2e-reference-001",
            "uetr": "8f14e45f-ea5e-4f5f-9c5d-8f14e45fea5e",
            "transactionIdentification": "transaction-001",
        },
        "status": {"outcome": outcome},
        "paymentScheme": {"schema": "ZA_RPP"},
        "originalTransactionData": {
            "paymentMethod": "CreditTransfer",
            "amounts": {
                "bankSettlementAmount": {"currency": "ZAR", "value": 40.00},
                "instructedAmount": {"currency": "ZAR", "value": 40.00},
            },
            "settlementDate": "2026-11-05",
            "creditorAccount": {
                "proxy": {"schema": "CUSTOM", "value": "wilsy-customer-proxy"}
            },
        },
    }


def test_electrum_signature_verifies_es256_issuer_iat_and_body_digest():
    body = json.dumps(_payload(), separators=(",", ":")).encode()
    token, keys = _signed(body)
    verified = verify_electrum_http_message_signature(
        body, token, verification_keys=keys, now=NOW
    )
    assert verified.key_id == "electrum-key-1"
    assert verified.issuer == "electrum.co.za"
    assert verified.content_digest == hashlib.sha256(body).hexdigest()


def test_electrum_body_tampering_is_rejected():
    body = b'{"schema":"PaymentStatusReport"}'
    token, keys = _signed(body)
    with pytest.raises(ElectrumMessageAuthenticationError, match="CONTENT_DIGEST"):
        verify_electrum_http_message_signature(
            body + b" ", token, verification_keys=keys, now=NOW
        )


def test_electrum_stale_iat_and_unknown_kid_are_rejected():
    body = b'{"x":1}'
    token, keys = _signed(body, iat=int(NOW.timestamp()) - 301)
    with pytest.raises(ElectrumMessageAuthenticationError, match="IAT_OUTSIDE_WINDOW"):
        verify_electrum_http_message_signature(body, token, verification_keys=keys, now=NOW)
    fresh, _ = _signed(body, key_id="unknown")
    with pytest.raises(ElectrumMessageAuthenticationError, match="KEY_ID_UNKNOWN"):
        verify_electrum_http_message_signature(body, fresh, verification_keys=keys, now=NOW)


def test_electrum_wrong_issuer_is_rejected():
    body = b'{"x":1}'
    token, keys = _signed(body, issuer="attacker.example")
    with pytest.raises(ElectrumMessageAuthenticationError, match="VERIFICATION_FAILED"):
        verify_electrum_http_message_signature(body, token, verification_keys=keys, now=NOW)


def test_electrum_completion_maps_final_approved_payment_only():
    payload = _payload()
    body = json.dumps(payload, separators=(",", ":")).encode()
    token, keys = _signed(body)
    verified = verify_electrum_http_message_signature(body, token, verification_keys=keys, now=NOW)
    completion = normalize_electrum_payshap_completion(payload, verified_message=verified)
    assert completion.settlement_eligible
    assert completion.payment_scheme == "ZA_RPP"
    assert completion.uetr == payload["transactionIdentifiers"]["uetr"]
    assert completion.amount_minor == 4000
    assert completion.currency == "ZAR"
    assert completion.settlement_date.isoformat() == "2026-11-05"
    assert len(completion.creditor_account_fingerprint) == 64


@pytest.mark.parametrize("outcome", ["CANCELLED", "PENDING", "REJECTED", "PARTIALLY_ACCEPTED"])
def test_non_approved_completion_is_not_settlement_eligible(outcome):
    payload = _payload(outcome)
    completion = normalize_electrum_payshap_completion(
        payload, verified_message=VerifiedElectrumMessage(
            "electrum-key-1", "electrum.co.za", int(NOW.timestamp()), "a" * 64
        )
    )
    assert not completion.settlement_eligible


def test_approval_without_verified_transport_is_rejected():
    with pytest.raises(ElectrumCompletionContractError, match="VERIFIED_TRANSPORT"):
        normalize_electrum_payshap_completion(_payload(), verified_message=None)


def test_electrum_partner_response_is_also_signed_with_body_digest():
    private, public = _keys()
    body = b'{"accepted":true}'
    token = sign_electrum_http_message(
        body, private_key=private, key_id="wilsy-key-1",
        issuer="wilsy-onboarding-issuer", issued_at=int(NOW.timestamp()),
    )
    verified = verify_electrum_http_message_signature(
        body, token,
        verification_keys={"wilsy-key-1": public},
        now=NOW,
        issuer="wilsy-onboarding-issuer",
    )
    assert verified.key_id == "wilsy-key-1"
    assert verified.content_digest == hashlib.sha256(body).hexdigest()


def test_electrum_empty_ack_signature_omits_content_digest():
    from tools.eos.kennel.providers.electrum_payshap_completion import sign_electrum_http_message

    private, public = _keys()
    token = sign_electrum_http_message(
        b"",
        private_key=private,
        key_id="wilsy-key-1",
        issuer="wilsy-onboarding-issuer",
        issued_at=int(NOW.timestamp()),
    )
    claims = jwt.decode(
        token, public, algorithms=["ES256"], issuer="wilsy-onboarding-issuer"
    )
    assert "electrum.co.za/content-digest" not in claims
    verified = verify_electrum_http_message_signature(
        b"",
        token,
        verification_keys={"wilsy-key-1": public},
        now=NOW,
        issuer="wilsy-onboarding-issuer",
    )
    assert verified.content_digest == hashlib.sha256(b"").hexdigest()


def test_electrum_empty_ack_rejects_unnecessary_content_digest():
    private, public = _keys()
    token = jwt.encode(
        {
            "iss": "wilsy-onboarding-issuer",
            "iat": int(NOW.timestamp()),
            "electrum.co.za/content-digest": hashlib.sha256(b"").hexdigest(),
        },
        private,
        algorithm="ES256",
        headers={"kid": "wilsy-key-1", "typ": "JWT"},
    )
    with pytest.raises(ElectrumMessageAuthenticationError, match="EMPTY_BODY_DIGEST"):
        verify_electrum_http_message_signature(
            b"",
            token,
            verification_keys={"wilsy-key-1": public},
            now=NOW,
            issuer="wilsy-onboarding-issuer",
        )


def test_completion_requires_original_message_identifiers():
    payload = _payload()
    payload.pop("originalMessageIdentifiers")
    verified = VerifiedElectrumMessage(
        key_id="electrum-key-1",
        issuer="electrum.co.za",
        issued_at=int(NOW.timestamp()),
        content_digest="a" * 64,
    )
    with pytest.raises(ElectrumCompletionContractError, match="COMPLETION_FIELDS_INVALID"):
        normalize_electrum_payshap_completion(payload, verified_message=verified)


def test_completion_requires_end_to_end_identifier_and_uses_it_as_reference_fallback():
    verified = VerifiedElectrumMessage(
        key_id="electrum-key-1",
        issuer="electrum.co.za",
        issued_at=int(NOW.timestamp()),
        content_digest="a" * 64,
    )
    payload = _payload()
    payload["transactionIdentifiers"].pop("transactionIdentification")
    completion = normalize_electrum_payshap_completion(payload, verified_message=verified)
    assert completion.transaction_reference == "e2e-reference-001"

    payload["transactionIdentifiers"].pop("endToEndIdentification")
    with pytest.raises(ElectrumCompletionContractError, match="END_TO_END_IDENTIFICATION"):
        normalize_electrum_payshap_completion(payload, verified_message=verified)
