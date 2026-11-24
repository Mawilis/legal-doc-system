"""WILSY OS historical invoice QR compatibility certificate.

TITLE: Legacy Invoice QR Compatibility Tests
VERSION: v1.0.1-NODE-VECTOR-FIXTURE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Locks Python EOS signing and verification to a fixed signature
         produced by the retired Node SHA3-512 QR payload contract.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_invoice_qr_legacy_contract.py
COLLABORATION / OWNERSHIP: Python EOS QR contract, billing router, and client proof panel.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG:
  v1.0.1-NODE-VECTOR-FIXTURE constructs the large base64 test envelope from
    the exact 128-character legacy payload and retains the independently
    generated Node signature as a fixed compatibility vector.
  v1.0.0-NODE-VECTOR-COMPATIBILITY certifies exact field order, JSON bytes,
    base64url, legacy SHA3-512 signature, expiry, tamper rejection, and
    fail-closed configuration without production keys.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ECT Act section 15.
SECURITY / PRIVACY POSTURE: Fixed synthetic test secret only; no environment secrets or data.
TENANT BOUNDARY: Payload compatibility tests do not grant or simulate HTTP tenant authority.
AUTHORITY BOUNDARY: Pure cryptographic regression evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
"""
from __future__ import annotations

import base64
import json

import pytest

from tools.eos.saas.billing.invoice_qr_legacy_contract import (
    InvoiceQrContractError,
    build_legacy_invoice_qr_payload,
    verify_legacy_invoice_qr_payload,
)


_TEST_SECRET = "legacy-qr-compatibility-test-secret-32"
_LEGACY_SIGNATURE = (
    "ACF0BE4381507A3C491F248EF4872F76BB4D7501CA4E880ECF6BC9D442A54A130203183465D836518BE2CF93E3DF25F5783C63852382295D7F6C47D74030DDDD"
)
_LEGACY_JSON = (
    '{"documentId":"INV-HIST-001","tenantId":"TENANT-HIST-001",'
    '"amount":1250.5,"currency":"ZAR","traceId":"TRACE-HIST-001",'
    f'"sealHash":"{"a" * 128}","merkleRoot":"{"b" * 128}",'
    '"documentType":"INVOICE","expiresAt":1730000000000,"issuedAt":1729990000000}'
)
_LEGACY_ENCODED_JSON = base64.urlsafe_b64encode(_LEGACY_JSON.encode()).rstrip(b"=").decode()
_LEGACY_VECTOR = f"{_LEGACY_ENCODED_JSON}.{_LEGACY_SIGNATURE}"


def _invoice_data() -> dict[str, object]:
    return {
        "invoiceId": "INV-HIST-001",
        "tenantId": "TENANT-HIST-001",
        "amount": 1250.5,
        "currency": "zar",
        "traceId": "TRACE-HIST-001",
        "sealHash": "a" * 128,
        "merkleRoot": "b" * 128,
        "documentType": "invoice",
    }


def test_python_issuer_matches_fixed_retired_node_payload_vector() -> None:
    result = build_legacy_invoice_qr_payload(
        _invoice_data(),
        secret=_TEST_SECRET,
        base_url="https://wilsy.example/api/qr/verify",
        now_ms=1_729_990_000_000,
        expires_at_ms=1_730_000_000_000,
    )

    assert result.payload_json == _LEGACY_JSON
    assert result.encoded_payload == _LEGACY_VECTOR
    assert result.verification_url == f"https://wilsy.example/api/qr/verify/{_LEGACY_VECTOR}"


def test_python_verifier_accepts_historical_node_vector_and_preserves_raw_json() -> None:
    result = verify_legacy_invoice_qr_payload(
        _LEGACY_VECTOR,
        secret=_TEST_SECRET,
        now_ms=1_729_990_000_001,
    )

    assert result.payload["documentId"] == "INV-HIST-001"
    assert result.payload["tenantId"] == "TENANT-HIST-001"
    assert result.payload["amount"] == 1250.5
    assert result.payload["documentType"] == "INVOICE"
    assert result.payload_json == _LEGACY_JSON
    assert json.loads(result.payload_json) == dict(result.payload)


def test_tampered_signature_is_rejected() -> None:
    payload_part, signature = _LEGACY_VECTOR.split(".", 1)
    replacement = "0" if signature[-1] != "0" else "1"

    with pytest.raises(InvoiceQrContractError, match="QR_SIGNATURE_MISMATCH"):
        verify_legacy_invoice_qr_payload(
            f"{payload_part}.{signature[:-1]}{replacement}",
            secret=_TEST_SECRET,
            now_ms=1_729_990_000_001,
        )


def test_tampered_payload_bytes_are_rejected_even_when_base64_is_valid() -> None:
    payload_part, signature = _LEGACY_VECTOR.split(".", 1)
    tampered_json = _LEGACY_JSON.replace('"amount":1250.5', '"amount":1250.6')
    tampered_part = base64.urlsafe_b64encode(tampered_json.encode()).rstrip(b"=").decode()

    with pytest.raises(InvoiceQrContractError, match="QR_SIGNATURE_MISMATCH"):
        verify_legacy_invoice_qr_payload(
            f"{tampered_part}.{signature}",
            secret=_TEST_SECRET,
            now_ms=1_729_990_000_001,
        )


def test_expired_legacy_payload_is_rejected_after_signature_verification() -> None:
    with pytest.raises(InvoiceQrContractError, match="QR_PAYLOAD_EXPIRED"):
        verify_legacy_invoice_qr_payload(
            _LEGACY_VECTOR,
            secret=_TEST_SECRET,
            now_ms=1_730_000_000_000,
        )


def test_issuer_fails_closed_without_existing_signing_configuration() -> None:
    with pytest.raises(InvoiceQrContractError, match="QR_SIGNING_CONFIGURATION_UNAVAILABLE"):
        build_legacy_invoice_qr_payload(
            _invoice_data(),
            secret="short",
            base_url="https://wilsy.example/api/qr/verify",
            now_ms=1_729_990_000_000,
        )

    with pytest.raises(InvoiceQrContractError, match="QR_VERIFICATION_BASE_URL_UNAVAILABLE"):
        build_legacy_invoice_qr_payload(
            _invoice_data(),
            secret=_TEST_SECRET,
            base_url="",
            now_ms=1_729_990_000_000,
        )


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (1.0, '"amount":1'),
        (0.000001, '"amount":0.000001'),
        (0.0000001, '"amount":1e-7'),
        (1e20, '"amount":100000000000000000000'),
        (1e21, '"amount":1e+21'),
    ],
)
def test_issuer_uses_ecmascript_number_spelling(amount: float, expected: str) -> None:
    result = build_legacy_invoice_qr_payload(
        {**_invoice_data(), "amount": amount},
        secret=_TEST_SECRET,
        base_url="https://wilsy.example/api/qr/verify",
        now_ms=1_729_990_000_000,
    )

    assert expected in result.payload_json


# ARTIFACT: Legacy Invoice QR Compatibility Tests
# VERSION: v1.0.1-NODE-VECTOR-FIXTURE
# AUTHORITY BOUNDARY: Pure synthetic cryptographic compatibility evidence only.
# TENANT POSTURE: Signed tenant text is not authorization.
# FAIL-CLOSED POSTURE: Tampering, expiry and missing signer configuration fail closed.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
