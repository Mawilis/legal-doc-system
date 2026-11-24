"""WILSY OS legacy invoice QR compatibility contract.

TITLE: WILSY OS Legacy Invoice QR Contract
VERSION: v1.0.0-SHA3-512-HISTORICAL-COMPATIBILITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Preserves the established signed invoice QR payload bytes and
         SHA3-512 secret-suffix signature for Python EOS issuance and validation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/invoice_qr_legacy_contract.py
COLLABORATION / OWNERSHIP: Python EOS billing HTTP router consumes this contract;
                           existing QR_SIGNING_SECRET/QR_SECRET remain key owners.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.0-SHA3-512-HISTORICAL-COMPATIBILITY ports the legacy ordered
           payload, base64url envelope, expiry bounds, HTTPS verifier origin,
           and SHA3-512(payload + separator + configured secret) bytes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ECT Act section 15.
SECURITY / PRIVACY POSTURE: Secrets are read only from existing environment
                            configuration and are never returned or logged.
TENANT BOUNDARY: Payload tenant is signed; HTTP consumers must independently
                 bind it to TenantAuthorizationContext before invoice lookup.
AUTHORITY BOUNDARY: Cryptographic compatibility only; does not authorize access,
                    invoice issuance, payment, execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement truth.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Mapping, cast
from urllib.parse import quote, urlsplit


QR_DEFAULT_EXPIRY_MS = 30 * 24 * 60 * 60 * 1000
QR_MAX_EXPIRY_MS = 90 * 24 * 60 * 60 * 1000
QR_SIGNATURE_PATTERN = re.compile(r"^[A-Fa-f0-9]{128}$")


class InvoiceQrContractError(ValueError):
    """Stable fail-closed error raised at the legacy invoice QR boundary.

    Authority: Describes contract/configuration failure only.
    Tenant scope: No tenant is authorized by this exception.
    Mutation/idempotency: None; QR construction and decode are pure operations.
    Transaction ownership: None.
    Financial boundary: No payment, execution, or settlement truth.
    """

    def __init__(self, code: str) -> None:
        """Create one error using a stable non-sensitive code."""
        super().__init__(code)
        self.code = code


@dataclass(frozen=True, slots=True)
class LegacyInvoiceQrPayload:
    """Exact legacy payload, signature and URL returned by the issuer.

    Authority: Compatibility result only; callers still require tenant IAM.
    Tenant scope: ``payload['tenantId']`` is signed but is not access authority.
    Mutation/idempotency: Immutable in-memory value; no persistence occurs.
    Transaction ownership: None.
    Financial boundary: Does not express payment, execution, or settlement.
    """

    payload: Mapping[str, Any]
    payload_json: str
    signature: str
    encoded_payload: str
    verification_url: str


@dataclass(frozen=True, slots=True)
class VerifiedLegacyInvoiceQrPayload:
    """Decoded legacy payload whose exact encoded bytes passed signature checks.

    Authority: Cryptographic evidence only; HTTP callers must authorize and
        resolve the tenant-owned persisted invoice before returning evidence.
    Tenant scope: The contained tenant identifier is untrusted until bound by IAM.
    Mutation/idempotency: Immutable decode result; verification is read-only.
    Transaction ownership: None.
    Financial boundary: No payment, execution, or settlement truth.
    """

    payload: Mapping[str, Any]
    payload_json: str


@dataclass(frozen=True, slots=True)
class _SigningConfiguration:
    secret: str
    base_url: str | None


def _now_ms() -> int:
    """Return current Unix time in milliseconds without a second clock source."""
    return time.time_ns() // 1_000_000


def _signing_configuration(
    secret: str | None,
    base_url: str | None,
    *,
    require_base_url: bool,
) -> _SigningConfiguration:
    """Read and validate the existing legacy environment contract."""
    selected_secret = secret
    if selected_secret is None:
        selected_secret = os.environ.get("QR_SIGNING_SECRET") or os.environ.get("QR_SECRET")
    if not isinstance(selected_secret, str) or len(selected_secret.strip()) < 32:
        raise InvoiceQrContractError("QR_SIGNING_CONFIGURATION_UNAVAILABLE")
    normalized_secret = selected_secret.strip()

    selected_base_url = base_url
    if selected_base_url is None:
        selected_base_url = os.environ.get("QR_VERIFICATION_BASE_URL")
    if not require_base_url:
        return _SigningConfiguration(normalized_secret, None)
    if not isinstance(selected_base_url, str) or not selected_base_url.strip():
        raise InvoiceQrContractError("QR_VERIFICATION_BASE_URL_UNAVAILABLE")

    parsed = urlsplit(selected_base_url.strip())
    if (
        parsed.scheme.lower() != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or any(ord(character) < 32 for character in selected_base_url)
    ):
        raise InvoiceQrContractError("QR_VERIFICATION_BASE_URL_INVALID")
    return _SigningConfiguration(normalized_secret, selected_base_url.strip().rstrip("/"))


def _ecmascript_number_json(value: Any) -> str:
    """Render a finite non-negative Number with JSON.stringify number thresholds."""
    if isinstance(value, bool):
        raise InvoiceQrContractError("QR_AMOUNT_INVALID")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise InvoiceQrContractError("QR_AMOUNT_INVALID") from error
    if not math.isfinite(number) or number < 0:
        raise InvoiceQrContractError("QR_AMOUNT_INVALID")
    if number == 0:
        return "0"

    rendered = repr(number).lower()
    if "e" not in rendered:
        return rendered[:-2] if rendered.endswith(".0") else rendered

    mantissa, exponent_text = rendered.split("e", 1)
    exponent = int(exponent_text)
    integer_part, _, fraction_part = mantissa.partition(".")
    digits = integer_part + fraction_part
    decimal_position = len(integer_part) + exponent
    scientific_exponent = decimal_position - 1

    if -6 <= scientific_exponent < 21:
        if decimal_position <= 0:
            return "0." + ("0" * -decimal_position) + digits
        if decimal_position >= len(digits):
            return digits + ("0" * (decimal_position - len(digits)))
        return digits[:decimal_position] + "." + digits[decimal_position:]

    coefficient = digits[0]
    if len(digits) > 1:
        coefficient += "." + digits[1:]
    exponent_suffix = f"+{scientific_exponent}" if scientific_exponent >= 0 else str(scientific_exponent)
    return f"{coefficient}e{exponent_suffix}"


def _json_string(value: str) -> str:
    """Encode one string using compact JSON-compatible JavaScript escapes."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _payload_json(payload: Mapping[str, Any]) -> str:
    """Serialize the fixed legacy field order and JavaScript amount spelling."""
    ordered_fields = (
        "documentId",
        "tenantId",
        "amount",
        "currency",
        "traceId",
        "sealHash",
        "merkleRoot",
        "documentType",
        "expiresAt",
        "issuedAt",
    )
    pieces: list[str] = []
    for field in ordered_fields:
        value = payload[field]
        encoded_value = _ecmascript_number_json(value) if field == "amount" else json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        )
        pieces.append(f"{_json_string(field)}:{encoded_value}")
    return "{" + ",".join(pieces) + "}"


def _signature(payload_json: str, secret: str) -> str:
    """Return the exact legacy uppercase SHA3-512 secret-suffix signature."""
    return hashlib.sha3_512(f"{payload_json}|{secret}".encode("utf-8")).hexdigest().upper()


def build_legacy_invoice_qr_payload(
    invoice_data: Mapping[str, Any],
    *,
    secret: str | None = None,
    base_url: str | None = None,
    now_ms: int | None = None,
    expires_at_ms: int | None = None,
) -> LegacyInvoiceQrPayload:
    """Build the historical signed invoice QR envelope without persisting it.

    :param invoice_data: Persisted invoice identity, tenant, total, currency,
        trace and optional seal/Merkle references.
    :param secret: Existing configured QR signing key; absent uses established
        ``QR_SIGNING_SECRET`` then ``QR_SECRET`` environment names.
    :param base_url: Existing HTTPS verifier origin; absent uses
        ``QR_VERIFICATION_BASE_URL``.
    :param now_ms: Deterministic test seam for the issuance instant.
    :param expires_at_ms: Optional explicit expiry, constrained to the legacy
        90 day maximum.
    :returns: Immutable legacy payload, exact JSON bytes, signature and URL.
    :raises InvoiceQrContractError: Invalid source fields or missing config.
    """
    if not isinstance(invoice_data, Mapping):
        raise InvoiceQrContractError("QR_SOURCE_INVALID")
    config = _signing_configuration(secret, base_url, require_base_url=True)

    required = ("invoiceId", "tenantId", "amount", "currency", "traceId")
    values = {key: invoice_data.get(key) for key in required}
    if any(value is None or value == "" for value in values.values()):
        raise InvoiceQrContractError("QR_SOURCE_FIELDS_UNAVAILABLE")

    try:
        amount = float(cast(Any, values["amount"]))
    except (TypeError, ValueError, OverflowError) as error:
        raise InvoiceQrContractError("QR_AMOUNT_INVALID") from error
    if not math.isfinite(amount) or amount < 0:
        raise InvoiceQrContractError("QR_AMOUNT_INVALID")

    issued_at = _now_ms() if now_ms is None else now_ms
    if isinstance(issued_at, bool) or not isinstance(issued_at, int) or issued_at < 0:
        raise InvoiceQrContractError("QR_ISSUED_AT_INVALID")
    expires_at = issued_at + QR_DEFAULT_EXPIRY_MS if expires_at_ms is None else expires_at_ms
    if (
        isinstance(expires_at, bool)
        or not isinstance(expires_at, int)
        or expires_at <= issued_at
        or expires_at > issued_at + QR_MAX_EXPIRY_MS
    ):
        raise InvoiceQrContractError("QR_EXPIRY_INVALID")

    payload: dict[str, Any] = {
        "documentId": str(values["invoiceId"]),
        "tenantId": str(values["tenantId"]),
        "amount": amount,
        "currency": str(values["currency"]).upper(),
        "traceId": str(values["traceId"]),
        "sealHash": str(invoice_data.get("sealHash") or ""),
        "merkleRoot": str(invoice_data.get("merkleRoot") or ""),
        "documentType": str(invoice_data.get("documentType") or "INVOICE").upper(),
        "expiresAt": expires_at,
        "issuedAt": issued_at,
    }
    if not payload["documentId"].strip() or not payload["tenantId"].strip() or not payload["traceId"].strip():
        raise InvoiceQrContractError("QR_SOURCE_FIELDS_UNAVAILABLE")

    serialized = _payload_json(payload)
    signature = _signature(serialized, config.secret)
    encoded_json = base64.urlsafe_b64encode(serialized.encode("utf-8")).rstrip(b"=").decode("ascii")
    encoded_payload = f"{encoded_json}.{signature}"
    verification_url = f"{config.base_url}/{quote(encoded_payload, safe='')}"
    return LegacyInvoiceQrPayload(payload, serialized, signature, encoded_payload, verification_url)


def verify_legacy_invoice_qr_payload(
    encoded_payload: str,
    *,
    secret: str | None = None,
    now_ms: int | None = None,
) -> VerifiedLegacyInvoiceQrPayload:
    """Validate exact legacy payload bytes, signature and bounded expiry.

    The result is cryptographic evidence only. Callers must compare the signed
    tenant to an authenticated TenantAuthorizationContext and query the invoice
    with that exact tenant before returning any persisted invoice information.

    :param encoded_payload: Historical ``base64url(JSON).UPPERCASE_SHA3`` value.
    :param secret: Existing configured QR key; no fallback key is generated.
    :param now_ms: Deterministic test seam for expiry checks.
    :returns: Immutable payload and exact signed JSON representation.
    :raises InvoiceQrContractError: Malformed, expired, tampered, or
        unconfigured evidence.
    """
    config = _signing_configuration(secret, None, require_base_url=False)
    if not isinstance(encoded_payload, str) or len(encoded_payload) > 16_384:
        raise InvoiceQrContractError("QR_PAYLOAD_INVALID")
    parts = encoded_payload.split(".")
    if len(parts) != 2 or not parts[0] or not QR_SIGNATURE_PATTERN.fullmatch(parts[1]):
        raise InvoiceQrContractError("QR_PAYLOAD_INVALID")

    try:
        padded = parts[0] + ("=" * (-len(parts[0]) % 4))
        raw_json = base64.b64decode(padded.encode("ascii"), altchars=b"-_", validate=True).decode("utf-8")
        payload = json.loads(raw_json)
    except (UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise InvoiceQrContractError("QR_PAYLOAD_INVALID") from error
    if not isinstance(payload, dict):
        raise InvoiceQrContractError("QR_PAYLOAD_INVALID")

    expected = _signature(raw_json, config.secret)
    if not hmac.compare_digest(expected.lower(), parts[1].lower()):
        raise InvoiceQrContractError("QR_SIGNATURE_MISMATCH")

    required = {
        "documentId": str,
        "tenantId": str,
        "amount": (int, float),
        "currency": str,
        "traceId": str,
        "sealHash": str,
        "merkleRoot": str,
        "documentType": str,
        "expiresAt": (int, float),
        "issuedAt": (int, float),
    }
    for field, expected_type in required.items():
        value = payload.get(field)
        if isinstance(value, bool) or not isinstance(value, expected_type):
            raise InvoiceQrContractError("QR_PAYLOAD_INVALID")
    if not all(payload[field].strip() for field in ("documentId", "tenantId", "currency", "traceId", "documentType")):
        raise InvoiceQrContractError("QR_PAYLOAD_INVALID")
    if not math.isfinite(float(payload["amount"])) or float(payload["amount"]) < 0:
        raise InvoiceQrContractError("QR_PAYLOAD_INVALID")

    current_time = _now_ms() if now_ms is None else now_ms
    expiry = float(payload["expiresAt"])
    if not math.isfinite(expiry) or expiry <= current_time:
        raise InvoiceQrContractError("QR_PAYLOAD_EXPIRED")
    issued_at = float(payload["issuedAt"])
    if (
        not math.isfinite(issued_at)
        or issued_at < 0
        or expiry <= issued_at
        or expiry > issued_at + QR_MAX_EXPIRY_MS
        or issued_at > current_time + 60_000
    ):
        raise InvoiceQrContractError("QR_PAYLOAD_INVALID")
    return VerifiedLegacyInvoiceQrPayload(payload, raw_json)


# ARTIFACT: WILSY OS Legacy Invoice QR Contract
# VERSION: v1.0.0-SHA3-512-HISTORICAL-COMPATIBILITY
# AUTHORITY BOUNDARY: Cryptographic compatibility only; HTTP caller IAM remains mandatory.
# TENANT POSTURE: Signed tenant labels are not authorization and require canonical binding.
# FAIL-CLOSED POSTURE: Missing configuration, malformed payload, signature, or expiry errors deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
