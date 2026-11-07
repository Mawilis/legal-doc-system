"""Cryptographic candidate-signature verification for exact signed-offer evidence.

The signer public key must already be enrolled in the tenant/candidate trust
registry through a separately governed identity-proofing process. This module
never accepts a public key supplied by the verification request.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import base64
import hashlib
import json
import re
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo import ASCENDING


TRUST_COLLECTION = "wilsy_hr_candidate_signer_key_trust"
VERIFICATION_COLLECTION = "wilsy_hr_signed_offer_verifications"
VERIFICATION_EVENT_COLLECTION = "wilsy_hr_signed_offer_verification_events"
SIGNATURE_SCHEMA = "WILSY-HR-SIGNED-OFFER-SIGNATURE/V1"
VERIFICATION_SCHEMA = "WILSY-HR-SIGNED-OFFER-VERIFICATION/V1"
ALGORITHM = "Ed25519"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")
_HEX = re.compile(r"^[0-9a-f]{128}$")
_B64URL = re.compile(r"^[A-Za-z0-9_-]+$")


class SignedOfferVerificationError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class SignerKeyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"


def _fail(code: str, cause: BaseException | None = None):
    error = SignedOfferVerificationError(code)
    if cause is None:
        raise error
    raise error from cause


def _id(name: str, value: object) -> str:
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        _fail(f"SIGNED_OFFER_{name.upper()}_INVALID")
    return value


def _utc(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"SIGNED_OFFER_{name.upper()}_UTC_REQUIRED")
    return value.astimezone(timezone.utc)


def _decode_b64url(name: str, value: object, *, expected_length: int) -> bytes:
    if not isinstance(value, str) or not value or _B64URL.fullmatch(value) is None:
        _fail(f"SIGNED_OFFER_{name.upper()}_ENCODING_INVALID")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, TypeError) as error:
        _fail(f"SIGNED_OFFER_{name.upper()}_ENCODING_INVALID", error)
    canonical = base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=")
    if canonical != value or len(decoded) != expected_length:
        _fail(f"SIGNED_OFFER_{name.upper()}_LENGTH_INVALID")
    return decoded


def encode_signature(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


@dataclass(frozen=True, slots=True)
class CandidateSignerKeyTrustRecord:
    tenant_id: str
    candidate_id: str
    signer_key_id: str
    public_key_b64url: str
    key_fingerprint: str
    valid_from: datetime
    valid_until: datetime
    status: SignerKeyStatus = SignerKeyStatus.ACTIVE
    revoked_at: datetime | None = None
    revision: int = 1

    def __post_init__(self):
        for name in ("tenant_id", "candidate_id", "signer_key_id"):
            object.__setattr__(self, name, _id(name, getattr(self, name)))
        public_key = _decode_b64url("public_key", self.public_key_b64url, expected_length=32)
        if hashlib.sha3_512(public_key).hexdigest() != self.key_fingerprint or not _HEX.fullmatch(self.key_fingerprint):
            _fail("SIGNED_OFFER_TRUST_KEY_FINGERPRINT_MISMATCH")
        start, end = _utc("key_valid_from", self.valid_from), _utc("key_valid_until", self.valid_until)
        if end <= start:
            _fail("SIGNED_OFFER_TRUST_KEY_VALIDITY_INVALID")
        if type(self.status) is not SignerKeyStatus:
            _fail("SIGNED_OFFER_TRUST_KEY_STATUS_INVALID")
        revoked = None if self.revoked_at is None else _utc("key_revoked_at", self.revoked_at)
        if revoked is not None and revoked < start:
            _fail("SIGNED_OFFER_TRUST_KEY_REVOCATION_INVALID")
        if type(self.revision) is not int or self.revision < 1:
            _fail("SIGNED_OFFER_TRUST_KEY_REVISION_INVALID")
        object.__setattr__(self, "valid_from", start)
        object.__setattr__(self, "valid_until", end)
        object.__setattr__(self, "revoked_at", revoked)

    def active_at(self, instant: datetime) -> bool:
        instant = _utc("key_check_time", instant)
        return (
            self.status is SignerKeyStatus.ACTIVE
            and self.revoked_at is None
            and self.valid_from <= instant <= self.valid_until
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id, "candidate_id": self.candidate_id,
            "signer_key_id": self.signer_key_id,
            "public_key_b64url": self.public_key_b64url,
            "key_fingerprint": self.key_fingerprint,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "status": self.status.value,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]):
        return cls(
            tenant_id=value["tenant_id"], candidate_id=value["candidate_id"],
            signer_key_id=value["signer_key_id"], public_key_b64url=value["public_key_b64url"],
            key_fingerprint=value["key_fingerprint"],
            valid_from=datetime.fromisoformat(value["valid_from"]),
            valid_until=datetime.fromisoformat(value["valid_until"]),
            status=SignerKeyStatus(value["status"]),
            revoked_at=datetime.fromisoformat(value["revoked_at"]) if value.get("revoked_at") else None,
            revision=value["revision"],
        )


class CandidateSignerKeyTrustRegistry:
    """Read-only resolver; trust enrollment/revocation is a separate governed command."""

    def __init__(self, collection: Any):
        self._collection = collection

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        collection.create_index(
            [("tenant_id", ASCENDING), ("candidate_id", ASCENDING), ("signer_key_id", ASCENDING)],
            unique=True, name="uq_hr_candidate_signer_key",
        )

    def get(self, *, tenant_id: str, candidate_id: str, signer_key_id: str, session: Any):
        if session is None:
            _fail("SIGNED_OFFER_TRUST_LOOKUP_TRANSACTION_REQUIRED")
        try:
            row = self._collection.find_one(
                {"tenant_id": tenant_id, "candidate_id": candidate_id, "signer_key_id": signer_key_id},
                session=session,
            )
        except PyMongoError as error:
            _fail("SIGNED_OFFER_TRUST_LOOKUP_UNAVAILABLE", error)
        if row is None:
            _fail("SIGNED_OFFER_SIGNER_KEY_NOT_TRUSTED")
        row.pop("_id", None)
        return CandidateSignerKeyTrustRecord.from_dict(row)


@dataclass(frozen=True, slots=True)
class SignedOfferSignatureEnvelope:
    signer_key_id: str
    signed_at: datetime
    signature_b64url: str

    def __post_init__(self):
        object.__setattr__(self, "signer_key_id", _id("signer_key_id", self.signer_key_id))
        object.__setattr__(self, "signed_at", _utc("signature_signed_at", self.signed_at))
        _decode_b64url("signature", self.signature_b64url, expected_length=64)


@dataclass(frozen=True, slots=True)
class SignedOfferVerificationRecord:
    tenant_id: str
    candidate_id: str
    offer_id: str
    evidence_id: str
    evidence_version_id: str
    content_digest_sha3_512: str
    signer_key_id: str
    signer_key_fingerprint: str
    signature_fingerprint: str
    signed_at: datetime
    verified_at: datetime
    verification_reference: str
    algorithm: str = ALGORITHM
    status: VerificationStatus = VerificationStatus.VERIFIED
    schema: str = VERIFICATION_SCHEMA
    fingerprint: str = ""

    def __post_init__(self):
        for name in ("tenant_id", "candidate_id", "offer_id", "evidence_id",
                     "evidence_version_id", "signer_key_id", "verification_reference"):
            object.__setattr__(self, name, _id(name, getattr(self, name)))
        for name in ("content_digest_sha3_512", "signer_key_fingerprint", "signature_fingerprint"):
            value = getattr(self, name)
            if not isinstance(value, str) or not _HEX.fullmatch(value):
                _fail(f"SIGNED_OFFER_{name.upper()}_INVALID")
        signed, verified = _utc("signed_at", self.signed_at), _utc("verified_at", self.verified_at)
        if signed > verified:
            _fail("SIGNED_OFFER_VERIFICATION_TIME_INVALID")
        if self.algorithm != ALGORITHM or self.status is not VerificationStatus.VERIFIED or self.schema != VERIFICATION_SCHEMA:
            _fail("SIGNED_OFFER_VERIFICATION_CONTRACT_INVALID")
        payload = {
            "schema": self.schema, "tenant_id": self.tenant_id,
            "candidate_id": self.candidate_id, "offer_id": self.offer_id,
            "evidence_id": self.evidence_id, "evidence_version_id": self.evidence_version_id,
            "content_digest_sha3_512": self.content_digest_sha3_512,
            "signer_key_id": self.signer_key_id,
            "signer_key_fingerprint": self.signer_key_fingerprint,
            "signature_fingerprint": self.signature_fingerprint,
            "signed_at": signed.isoformat(), "verified_at": verified.isoformat(),
            "algorithm": self.algorithm, "status": self.status.value,
            "verification_reference": self.verification_reference,
        }
        calculated = hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if self.fingerprint and self.fingerprint != calculated:
            _fail("SIGNED_OFFER_VERIFICATION_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "signed_at", signed)
        object.__setattr__(self, "verified_at", verified)
        object.__setattr__(self, "fingerprint", calculated)

    def to_dict(self):
        return {
            "schema": self.schema, "tenant_id": self.tenant_id,
            "candidate_id": self.candidate_id, "offer_id": self.offer_id,
            "evidence_id": self.evidence_id, "evidence_version_id": self.evidence_version_id,
            "content_digest_sha3_512": self.content_digest_sha3_512,
            "signer_key_id": self.signer_key_id,
            "signer_key_fingerprint": self.signer_key_fingerprint,
            "signature_fingerprint": self.signature_fingerprint,
            "signed_at": self.signed_at.isoformat(), "verified_at": self.verified_at.isoformat(),
            "verification_reference": self.verification_reference,
            "algorithm": self.algorithm, "status": self.status.value,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]):
        return cls(
            tenant_id=value["tenant_id"], candidate_id=value["candidate_id"],
            offer_id=value["offer_id"], evidence_id=value["evidence_id"],
            evidence_version_id=value["evidence_version_id"],
            content_digest_sha3_512=value["content_digest_sha3_512"],
            signer_key_id=value["signer_key_id"],
            signer_key_fingerprint=value["signer_key_fingerprint"],
            signature_fingerprint=value["signature_fingerprint"],
            signed_at=datetime.fromisoformat(value["signed_at"]),
            verified_at=datetime.fromisoformat(value["verified_at"]),
            verification_reference=value["verification_reference"],
            algorithm=value["algorithm"], status=VerificationStatus(value["status"]),
            schema=value["schema"], fingerprint=value["fingerprint"],
        )


class SignedOfferVerificationRegistry:
    def __init__(self, records: Any, events: Any):
        self._records, self._events = records, events

    @staticmethod
    def ensure_indexes(records: Any, events: Any) -> None:
        records.create_index(
            [("tenant_id", ASCENDING), ("offer_id", ASCENDING),
             ("evidence_id", ASCENDING), ("evidence_version_id", ASCENDING)],
            unique=True, name="uq_hr_signed_offer_verification_scope",
        )
        records.create_index([("verification_reference", ASCENDING)], unique=True,
                             name="uq_hr_signed_offer_verification_reference")
        events.create_index([("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                            unique=True, name="uq_hr_signed_offer_verification_event_idempotency")

    def get(self, *, tenant_id: str, offer_id: str, evidence_id: str,
            evidence_version_id: str, session: Any):
        if session is None:
            _fail("SIGNED_OFFER_VERIFICATION_LOOKUP_TRANSACTION_REQUIRED")
        try:
            row = self._records.find_one({
                "tenant_id": tenant_id, "offer_id": offer_id,
                "evidence_id": evidence_id, "evidence_version_id": evidence_version_id,
            }, session=session)
        except PyMongoError as error:
            _fail("SIGNED_OFFER_VERIFICATION_LOOKUP_UNAVAILABLE", error)
        if row is None:
            _fail("SIGNED_OFFER_VERIFICATION_REQUIRED")
        row.pop("_id", None)
        return SignedOfferVerificationRecord.from_dict(row)

    def register(self, record: SignedOfferVerificationRecord, *,
                 actor_principal_id: str, idempotency_key: str, session: Any):
        if session is None:
            _fail("SIGNED_OFFER_VERIFICATION_TRANSACTION_REQUIRED")
        _id("actor_principal_id", actor_principal_id)
        _id("idempotency_key", idempotency_key)
        try:
            existing = self._records.find_one({
                "tenant_id": record.tenant_id, "offer_id": record.offer_id,
                "evidence_id": record.evidence_id,
                "evidence_version_id": record.evidence_version_id,
            }, session=session)
            if existing is not None:
                existing.pop("_id", None)
                prior = SignedOfferVerificationRecord.from_dict(existing)
                if prior.fingerprint == record.fingerprint:
                    return prior
                _fail("SIGNED_OFFER_VERIFICATION_SCOPE_CONFLICT")
            self._records.insert_one(record.to_dict(), session=session)
            self._events.insert_one({
                "tenant_id": record.tenant_id,
                "verification_reference": record.verification_reference,
                "event_type": "SIGNED_OFFER_CRYPTOGRAPHICALLY_VERIFIED",
                "record_fingerprint": record.fingerprint,
                "actor_principal_id": actor_principal_id,
                "idempotency_key": idempotency_key,
                "occurred_at": record.verified_at.isoformat(),
            }, session=session)
            return record
        except DuplicateKeyError as error:
            _fail("SIGNED_OFFER_VERIFICATION_CONFLICT", error)
        except PyMongoError as error:
            _fail("SIGNED_OFFER_VERIFICATION_WRITE_UNAVAILABLE", error)


def canonical_signature_payload(
    *, tenant_id: str, candidate_id: str, offer_id: str,
    evidence_id: str, evidence_version_id: str,
    content_digest_sha3_512: str, signer_key_id: str, signed_at: datetime,
) -> bytes:
    values = {
        "schema": SIGNATURE_SCHEMA,
        "tenant_id": _id("tenant_id", tenant_id),
        "candidate_id": _id("candidate_id", candidate_id),
        "offer_id": _id("offer_id", offer_id),
        "evidence_id": _id("evidence_id", evidence_id),
        "evidence_version_id": _id("evidence_version_id", evidence_version_id),
        "content_digest_sha3_512": content_digest_sha3_512,
        "signer_key_id": _id("signer_key_id", signer_key_id),
        "signed_at": _utc("signed_at", signed_at).isoformat(),
    }
    if not _HEX.fullmatch(content_digest_sha3_512):
        _fail("SIGNED_OFFER_CONTENT_DIGEST_INVALID")
    return json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8")


def verify_signed_offer_signature(
    *, tenant_id: str, candidate_id: str, offer_id: str,
    evidence_id: str, evidence_version_id: str,
    content_digest_sha3_512: str, envelope: SignedOfferSignatureEnvelope,
    trust: CandidateSignerKeyTrustRecord, verified_at: datetime,
) -> SignedOfferVerificationRecord:
    verified = _utc("verified_at", verified_at)
    if (
        trust.tenant_id != tenant_id or trust.candidate_id != candidate_id
        or trust.signer_key_id != envelope.signer_key_id
        or not trust.active_at(verified)
        or envelope.signed_at < trust.valid_from
        or envelope.signed_at > trust.valid_until
        or envelope.signed_at > verified
    ):
        _fail("SIGNED_OFFER_SIGNER_TRUST_INVALID")
    public_key = _decode_b64url("public_key", trust.public_key_b64url, expected_length=32)
    signature = _decode_b64url("signature", envelope.signature_b64url, expected_length=64)
    payload = canonical_signature_payload(
        tenant_id=tenant_id, candidate_id=candidate_id, offer_id=offer_id,
        evidence_id=evidence_id, evidence_version_id=evidence_version_id,
        content_digest_sha3_512=content_digest_sha3_512,
        signer_key_id=envelope.signer_key_id, signed_at=envelope.signed_at,
    )
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, payload)
    except (InvalidSignature, ValueError) as error:
        _fail("SIGNED_OFFER_SIGNATURE_INVALID", error)
    signature_fingerprint = hashlib.sha3_512(signature).hexdigest()
    reference_material = hashlib.sha3_512(payload + signature).hexdigest()
    reference = "SOV-" + reference_material[:32].upper()
    return SignedOfferVerificationRecord(
        tenant_id=tenant_id, candidate_id=candidate_id, offer_id=offer_id,
        evidence_id=evidence_id, evidence_version_id=evidence_version_id,
        content_digest_sha3_512=content_digest_sha3_512,
        signer_key_id=envelope.signer_key_id,
        signer_key_fingerprint=trust.key_fingerprint,
        signature_fingerprint=signature_fingerprint,
        signed_at=envelope.signed_at, verified_at=verified,
        verification_reference=reference,
    )


__all__ = [
    "ALGORITHM", "CandidateSignerKeyTrustRecord", "CandidateSignerKeyTrustRegistry",
    "SIGNATURE_SCHEMA", "SignerKeyStatus", "SignedOfferSignatureEnvelope",
    "SignedOfferVerificationError", "SignedOfferVerificationRecord",
    "SignedOfferVerificationRegistry", "VerificationStatus",
    "canonical_signature_payload", "encode_signature", "verify_signed_offer_signature",
    "TRUST_COLLECTION", "VERIFICATION_COLLECTION", "VERIFICATION_EVENT_COLLECTION",
]
