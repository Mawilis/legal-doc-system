"""Electrum EPC PayShap completion transport contract.

The partner-side API uses signed ES256 JWTs in x-jwt-signature. This module
verifies the exact raw-body digest before parsing the final completion message.
It creates no settlement or invoice authority by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import hashlib
import hmac
import json
import re
import uuid
from typing import Mapping, Any

import jwt
from jwt import InvalidTokenError

from tools.eos.saas.domain.money import to_minor_units


ISSUER = "electrum.co.za"
SIGNATURE_HEADER = "x-jwt-signature"
CONTENT_DIGEST_CLAIM = "electrum.co.za/content-digest"
MAX_IAT_SKEW_SECONDS = 300


class ElectrumMessageAuthenticationError(ValueError):
    """Reject an unauthenticated, altered, stale, or mis-keyed Electrum message."""


class ElectrumCompletionContractError(ValueError):
    """Reject a malformed or unsupported Electrum completion message."""


@dataclass(frozen=True, slots=True)
class VerifiedElectrumMessage:
    key_id: str
    issuer: str
    issued_at: int
    content_digest: str


@dataclass(frozen=True, slots=True)
class ElectrumPayShapCompletion:
    message_id: str
    message_created_at: datetime
    uetr: str
    transaction_reference: str
    outcome: str
    payment_scheme: str
    payment_method: str
    amount_minor: int
    currency: str
    settlement_date: date | None
    creditor_account_fingerprint: str

    @property
    def settlement_eligible(self) -> bool:
        return self.outcome == "APPROVED"


def verify_electrum_http_message_signature(
    raw_body: bytes,
    signature_header: str,
    *,
    verification_keys: Mapping[str, str | bytes],
    now: datetime | None = None,
    issuer: str = ISSUER,
    max_iat_skew_seconds: int = MAX_IAT_SKEW_SECONDS,
) -> VerifiedElectrumMessage:
    """Verify ES256, onboarding issuer, five-minute iat window and raw-body digest.

    The algorithm is pinned in code; an untrusted JOSE alg header never chooses
    the verification algorithm. Multiple kid values are supported for rotation.
    """
    if not isinstance(raw_body, bytes):
        raise ElectrumMessageAuthenticationError("ELECTRUM_BODY_INVALID")
    if not isinstance(signature_header, str) or not signature_header.strip():
        raise ElectrumMessageAuthenticationError("ELECTRUM_SIGNATURE_REQUIRED")
    if not isinstance(verification_keys, Mapping) or not verification_keys:
        raise ElectrumMessageAuthenticationError("ELECTRUM_VERIFICATION_KEYS_UNAVAILABLE")
    if not isinstance(max_iat_skew_seconds, int) or max_iat_skew_seconds <= 0:
        raise ElectrumMessageAuthenticationError("ELECTRUM_IAT_POLICY_INVALID")

    now = now or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ElectrumMessageAuthenticationError("ELECTRUM_CLOCK_INVALID")

    token = signature_header.strip()
    try:
        header = jwt.get_unverified_header(token)
    except InvalidTokenError as error:
        raise ElectrumMessageAuthenticationError("ELECTRUM_JWT_HEADER_INVALID") from error

    key_id = header.get("kid")
    if not isinstance(key_id, str) or not key_id.strip():
        raise ElectrumMessageAuthenticationError("ELECTRUM_KEY_ID_REQUIRED")
    if header.get("alg") != "ES256":
        raise ElectrumMessageAuthenticationError("ELECTRUM_JWT_ALGORITHM_REJECTED")
    if header.get("typ") not in (None, "JWT"):
        raise ElectrumMessageAuthenticationError("ELECTRUM_JWT_TYPE_REJECTED")
    public_key = verification_keys.get(key_id)
    if not isinstance(public_key, (str, bytes)) or not public_key:
        raise ElectrumMessageAuthenticationError("ELECTRUM_KEY_ID_UNKNOWN")

    try:
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            issuer=issuer,
            options={"require": ["iss", "iat"], "verify_aud": False},
            leeway=0,
        )
    except InvalidTokenError as error:
        raise ElectrumMessageAuthenticationError("ELECTRUM_JWT_VERIFICATION_FAILED") from error

    issued_at = claims.get("iat")
    if isinstance(issued_at, bool) or not isinstance(issued_at, int):
        raise ElectrumMessageAuthenticationError("ELECTRUM_IAT_INVALID")
    if abs(int(now.timestamp()) - issued_at) > max_iat_skew_seconds:
        raise ElectrumMessageAuthenticationError("ELECTRUM_IAT_OUTSIDE_WINDOW")

    expected_digest = hashlib.sha256(raw_body).hexdigest()
    supplied_digest = claims.get(CONTENT_DIGEST_CLAIM)
    if raw_body:
        if (
            not isinstance(supplied_digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", supplied_digest) is None
            or not hmac.compare_digest(supplied_digest, expected_digest)
        ):
            raise ElectrumMessageAuthenticationError("ELECTRUM_CONTENT_DIGEST_MISMATCH")
    elif supplied_digest is not None:
        raise ElectrumMessageAuthenticationError("ELECTRUM_EMPTY_BODY_DIGEST_MUST_BE_OMITTED")

    return VerifiedElectrumMessage(
        key_id=key_id,
        issuer=issuer,
        issued_at=issued_at,
        content_digest=expected_digest,
    )


def sign_electrum_http_message(
    raw_body: bytes,
    *,
    private_key: str | bytes,
    key_id: str,
    issuer: str,
    issued_at: int,
) -> str:
    """Sign an Electrum partner-side HTTP response using ES256 and body digest."""
    if not isinstance(raw_body, bytes):
        raise ElectrumMessageAuthenticationError("ELECTRUM_RESPONSE_BODY_INVALID")
    if not isinstance(private_key, (str, bytes)) or not private_key:
        raise ElectrumMessageAuthenticationError("ELECTRUM_SIGNING_KEY_UNAVAILABLE")
    if not isinstance(key_id, str) or not key_id.strip():
        raise ElectrumMessageAuthenticationError("ELECTRUM_SIGNING_KEY_ID_REQUIRED")
    if not isinstance(issuer, str) or not issuer.strip():
        raise ElectrumMessageAuthenticationError("ELECTRUM_SIGNING_ISSUER_REQUIRED")
    if isinstance(issued_at, bool) or not isinstance(issued_at, int):
        raise ElectrumMessageAuthenticationError("ELECTRUM_IAT_INVALID")
    claims = {"iss": issuer, "iat": issued_at}
    if raw_body:
        claims[CONTENT_DIGEST_CLAIM] = hashlib.sha256(raw_body).hexdigest()
    try:
        return jwt.encode(
            claims,
            private_key,
            algorithm="ES256",
            headers={"kid": key_id, "typ": "JWT"},
        )
    except Exception as error:
        raise ElectrumMessageAuthenticationError("ELECTRUM_RESPONSE_SIGNING_FAILED") from error


def _required_text(value: Any, code: str, *, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ElectrumCompletionContractError(code)
    return value.strip()


def _aware_timestamp(value: Any, code: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ElectrumCompletionContractError(code)
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ElectrumCompletionContractError(code) from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ElectrumCompletionContractError(code)
    return result.astimezone(timezone.utc)


def electrum_creditor_account_fingerprint(account: Mapping[str, Any]) -> str:
    """Hash only the creditor account's stable identifier/proxy locator.

    Raw account numbers, proxy values and names are never persisted by this
    adapter. The opaque fingerprint is used to resolve an onboarded tenant
    binding and its already-authorized destination reference.
    """
    if not isinstance(account, Mapping):
        raise ElectrumCompletionContractError("ELECTRUM_CREDITOR_ACCOUNT_INVALID")
    locator = {
        key: account[key]
        for key in ("identification", "proxy")
        if key in account and account[key] is not None
    }
    if not locator:
        raise ElectrumCompletionContractError("ELECTRUM_CREDITOR_LOCATOR_REQUIRED")
    encoded = json.dumps(locator, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalize_electrum_payshap_completion(
    payload: Mapping[str, Any],
    *,
    verified_message: VerifiedElectrumMessage,
) -> ElectrumPayShapCompletion:
    """Validate the Electrum PaymentStatusReport completion schema.

    Only the final APPROVED outcome is settlement-eligible. Approval of an
    earlier partner-auth authorisation request is not a completion.
    """
    if not isinstance(verified_message, VerifiedElectrumMessage):
        raise ElectrumCompletionContractError("ELECTRUM_VERIFIED_TRANSPORT_REQUIRED")
    if not isinstance(payload, Mapping) or payload.get("schema") != "PaymentStatusReport":
        raise ElectrumCompletionContractError("ELECTRUM_PAYMENT_STATUS_REPORT_REQUIRED")

    status_data = payload.get("status")
    identifiers = payload.get("messageIdentifiers")
    transaction_ids = payload.get("transactionIdentifiers")
    payment_scheme = payload.get("paymentScheme")
    original_identifiers = payload.get("originalMessageIdentifiers")
    original = payload.get("originalTransactionData")
    if not all(isinstance(value, Mapping) for value in (
        status_data, identifiers, original_identifiers, transaction_ids, payment_scheme, original
    )):
        raise ElectrumCompletionContractError("ELECTRUM_COMPLETION_FIELDS_INVALID")

    outcome = _required_text(status_data.get("outcome"), "ELECTRUM_OUTCOME_INVALID", maximum=32)
    if outcome not in {"APPROVED", "CANCELLED", "PENDING", "REJECTED", "PARTIALLY_ACCEPTED"}:
        raise ElectrumCompletionContractError("ELECTRUM_OUTCOME_UNSUPPORTED")
    scheme = _required_text(payment_scheme.get("schema"), "ELECTRUM_SCHEME_INVALID", maximum=32)
    if scheme != "ZA_RPP":
        raise ElectrumCompletionContractError("ELECTRUM_SCHEME_NOT_PAYSHAP")
    payment_method = _required_text(original.get("paymentMethod"), "ELECTRUM_PAYMENT_METHOD_INVALID", maximum=32)
    if payment_method != "CreditTransfer":
        raise ElectrumCompletionContractError("ELECTRUM_PAYMENT_METHOD_NOT_CREDIT_TRANSFER")

    message_id = _required_text(
        identifiers.get("messageIdentification"), "ELECTRUM_MESSAGE_ID_INVALID", maximum=35
    )
    message_created_at = _aware_timestamp(
        identifiers.get("creationDateTime"), "ELECTRUM_MESSAGE_TIMESTAMP_INVALID"
    )
    _required_text(
        original_identifiers.get("messageIdentification"),
        "ELECTRUM_ORIGINAL_MESSAGE_ID_INVALID",
        maximum=35,
    )
    _aware_timestamp(
        original_identifiers.get("creationDateTime"),
        "ELECTRUM_ORIGINAL_MESSAGE_TIMESTAMP_INVALID",
    )
    uetr = _required_text(transaction_ids.get("uetr"), "ELECTRUM_UETR_INVALID", maximum=36)
    try:
        if str(uuid.UUID(uetr)) != uetr.lower():
            raise ValueError("non-canonical UUID")
    except (ValueError, AttributeError) as error:
        raise ElectrumCompletionContractError("ELECTRUM_UETR_INVALID") from error
    uetr = uetr.lower()

    end_to_end_identification = _required_text(
        transaction_ids.get("endToEndIdentification"),
        "ELECTRUM_END_TO_END_IDENTIFICATION_INVALID",
        maximum=35,
    )
    transaction_reference = _required_text(
        transaction_ids.get("transactionIdentification") or end_to_end_identification,
        "ELECTRUM_TRANSACTION_REFERENCE_INVALID",
        maximum=35,
    )
    amounts = original.get("amounts")
    if not isinstance(amounts, Mapping):
        raise ElectrumCompletionContractError("ELECTRUM_SETTLEMENT_AMOUNT_REQUIRED")
    bank_amount = amounts.get("bankSettlementAmount")
    if not isinstance(bank_amount, Mapping):
        raise ElectrumCompletionContractError("ELECTRUM_BANK_SETTLEMENT_AMOUNT_REQUIRED")
    currency = _required_text(bank_amount.get("currency"), "ELECTRUM_CURRENCY_INVALID", maximum=3)
    try:
        amount_minor = to_minor_units(bank_amount.get("value"), currency)
    except (TypeError, ValueError) as error:
        raise ElectrumCompletionContractError("ELECTRUM_AMOUNT_INVALID") from error
    if amount_minor <= 0:
        raise ElectrumCompletionContractError("ELECTRUM_AMOUNT_INVALID")

    settlement_date = None
    raw_date = original.get("settlementDate")
    if raw_date is not None:
        if not isinstance(raw_date, str):
            raise ElectrumCompletionContractError("ELECTRUM_SETTLEMENT_DATE_INVALID")
        try:
            settlement_date = date.fromisoformat(raw_date)
        except ValueError as error:
            raise ElectrumCompletionContractError("ELECTRUM_SETTLEMENT_DATE_INVALID") from error

    account_fingerprint = electrum_creditor_account_fingerprint(original.get("creditorAccount"))
    return ElectrumPayShapCompletion(
        message_id=message_id,
        message_created_at=message_created_at,
        uetr=uetr,
        transaction_reference=transaction_reference,
        outcome=outcome,
        payment_scheme=scheme,
        payment_method=payment_method,
        amount_minor=amount_minor,
        currency=currency,
        settlement_date=settlement_date,
        creditor_account_fingerprint=account_fingerprint,
    )


__all__ = [
    "ISSUER",
    "SIGNATURE_HEADER",
    "MAX_IAT_SKEW_SECONDS",
    "ElectrumMessageAuthenticationError",
    "ElectrumCompletionContractError",
    "VerifiedElectrumMessage",
    "ElectrumPayShapCompletion",
    "verify_electrum_http_message_signature",
    "sign_electrum_http_message",
    "electrum_creditor_account_fingerprint",
    "normalize_electrum_payshap_completion",
]
