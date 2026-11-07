"""Append-only institutional document-signature verification evidence.

A verification receipt is written only in the same caller-owned transaction as
the business command that relies on it. It stores cryptographic evidence, never
private keys, raw certificates, signatures, or document bytes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_256
import re
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

COLLECTION = "wilsy_institutional_document_signature_verifications"
EVENT_COLLECTION = "wilsy_institutional_document_signature_verification_events"


class InstitutionalSignatureEvidenceError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class InstitutionalSignatureEvidenceConflict(InstitutionalSignatureEvidenceError):
    pass


def _required(value: object, code: str, limit: int = 256) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > limit:
        raise InstitutionalSignatureEvidenceError(code)
    return value


def _hex(value: object, code: str, length: int = 64) -> str:
    if not isinstance(value, str) or re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is None:
        raise InstitutionalSignatureEvidenceError(code)
    return value


class InstitutionalSignatureEvidenceRegistry:
    """Persist signature verification receipts and append-only event evidence."""

    def __init__(self, records: Any, events: Any) -> None:
        if records is None or events is None:
            raise InstitutionalSignatureEvidenceError("INSTITUTIONAL_SIGNATURE_COLLECTIONS_REQUIRED")
        self._records = records
        self._events = events

    @staticmethod
    def ensure_indexes(records: Any, events: Any) -> None:
        try:
            records.create_index(
                [("tenant_id", ASCENDING), ("offer_id", ASCENDING),
                 ("evidence_id", ASCENDING), ("evidence_version_id", ASCENDING)],
                unique=True, name="uq_institutional_signature_offer_evidence_version",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True, name="uq_institutional_signature_event_idempotency",
            )
            events.create_index(
                [("verification_id", ASCENDING)],
                unique=True, name="uq_institutional_signature_event_verification",
            )
        except PyMongoError as error:
            raise InstitutionalSignatureEvidenceError("INSTITUTIONAL_SIGNATURE_INDEX_UNAVAILABLE") from error

    def record_verified(
        self,
        *,
        tenant_id: str,
        offer_id: str,
        candidate_id: str,
        evidence_id: str,
        evidence_version_id: str,
        evidence_digest_sha3_512: str,
        signed_manifest_digest_sha3_512: str,
        signer_certificate_sha256: str,
        signer_serial_number_hex: str,
        trust_root_sha256: str,
        signature_sha256: str,
        signature_algorithm: str,
        pki_verification_fingerprint: str,
        verified_at: datetime,
        actor_principal_id: str,
        idempotency_key: str,
        session: object,
    ) -> dict[str, Any]:
        if session is None:
            raise InstitutionalSignatureEvidenceError("INSTITUTIONAL_SIGNATURE_CALLER_TRANSACTION_REQUIRED")
        scope = {
            "tenant_id": _required(tenant_id, "INSTITUTIONAL_SIGNATURE_TENANT_INVALID"),
            "offer_id": _required(offer_id, "INSTITUTIONAL_SIGNATURE_OFFER_INVALID"),
            "candidate_id": _required(candidate_id, "INSTITUTIONAL_SIGNATURE_CANDIDATE_INVALID"),
            "evidence_id": _required(evidence_id, "INSTITUTIONAL_SIGNATURE_EVIDENCE_INVALID"),
            "evidence_version_id": _required(evidence_version_id, "INSTITUTIONAL_SIGNATURE_VERSION_INVALID"),
        }
        digests = {
            "evidence_digest_sha3_512": evidence_digest_sha3_512,
            "signed_manifest_digest_sha3_512": signed_manifest_digest_sha3_512,
            "signer_certificate_sha256": signer_certificate_sha256,
            "trust_root_sha256": trust_root_sha256,
            "signature_sha256": signature_sha256,
            "pki_verification_fingerprint": pki_verification_fingerprint,
        }
        for field, value in digests.items():
            _hex(value, f"INSTITUTIONAL_SIGNATURE_{field.upper()}_INVALID", 128 if field == "evidence_digest_sha3_512" else 64)
        serial = _required(signer_serial_number_hex, "INSTITUTIONAL_SIGNATURE_SERIAL_INVALID", 128)
        algorithm = _required(signature_algorithm, "INSTITUTIONAL_SIGNATURE_ALGORITHM_INVALID", 40)
        actor = _required(actor_principal_id, "INSTITUTIONAL_SIGNATURE_ACTOR_INVALID")
        key = _required(idempotency_key, "INSTITUTIONAL_SIGNATURE_IDEMPOTENCY_INVALID", 200)
        if type(verified_at) is not datetime or verified_at.tzinfo is None or verified_at.utcoffset() is None:
            raise InstitutionalSignatureEvidenceError("INSTITUTIONAL_SIGNATURE_TIME_INVALID")
        instant = verified_at.astimezone(timezone.utc)
        record = {
            **scope, **digests,
            "verification_id": "ISV-" + sha3_256("|".join((scope["tenant_id"], scope["offer_id"], scope["evidence_id"], scope["evidence_version_id"], pki_verification_fingerprint)).encode()).hexdigest()[:32].upper(),
            "signer_serial_number_hex": serial,
            "signature_algorithm": algorithm,
            "verified_at": instant,
            "actor_principal_id": actor,
            "schema": "wilsy.institutional.document_signature_verification.v2",
        }
        try:
            existing = self._records.find_one(scope, session=session)
            if existing is not None:
                existing.pop("_id", None)
                stored_time = existing.get("verified_at")
                if isinstance(stored_time, datetime) and stored_time.tzinfo is None:
                    existing["verified_at"] = stored_time.replace(tzinfo=timezone.utc)
                comparable = {key: value for key, value in existing.items() if key != "verification_id"}
                expected = {key: value for key, value in record.items() if key != "verification_id"}
                if comparable != expected:
                    raise InstitutionalSignatureEvidenceConflict("INSTITUTIONAL_SIGNATURE_EVIDENCE_ALREADY_VERIFIED_DIFFERENTLY")
                return existing
            self._records.insert_one(record, session=session)
            self._events.insert_one({
                "tenant_id": scope["tenant_id"],
                "idempotency_key": key,
                "verification_id": record["verification_id"],
                "offer_id": scope["offer_id"],
                "evidence_id": scope["evidence_id"],
                "evidence_version_id": scope["evidence_version_id"],
                "actor_principal_id": actor,
                "action": "INSTITUTIONAL_DOCUMENT_SIGNATURE_VERIFIED",
                "pki_verification_fingerprint": pki_verification_fingerprint,
                "occurred_at": instant,
                "schema": "wilsy.institutional.document_signature_verification_event.v1",
            }, session=session)
            return record
        except (InstitutionalSignatureEvidenceConflict,):
            raise
        except DuplicateKeyError as error:
            raise InstitutionalSignatureEvidenceConflict("INSTITUTIONAL_SIGNATURE_EVIDENCE_CONFLICT") from error
        except PyMongoError as error:
            raise InstitutionalSignatureEvidenceError("INSTITUTIONAL_SIGNATURE_WRITE_UNAVAILABLE") from error

    def get(self, *, tenant_id: str, offer_id: str, evidence_id: str,
            evidence_version_id: str, session: object) -> dict[str, Any]:
        if session is None:
            raise InstitutionalSignatureEvidenceError("INSTITUTIONAL_SIGNATURE_CALLER_TRANSACTION_REQUIRED")
        scope = {
            "tenant_id": _required(tenant_id, "INSTITUTIONAL_SIGNATURE_TENANT_INVALID"),
            "offer_id": _required(offer_id, "INSTITUTIONAL_SIGNATURE_OFFER_INVALID"),
            "evidence_id": _required(evidence_id, "INSTITUTIONAL_SIGNATURE_EVIDENCE_INVALID"),
            "evidence_version_id": _required(evidence_version_id, "INSTITUTIONAL_SIGNATURE_VERSION_INVALID"),
        }
        try:
            row = self._records.find_one(scope, session=session)
        except PyMongoError as error:
            raise InstitutionalSignatureEvidenceError("INSTITUTIONAL_SIGNATURE_READ_UNAVAILABLE") from error
        if row is None:
            raise InstitutionalSignatureEvidenceError("INSTITUTIONAL_SIGNATURE_VERIFICATION_REQUIRED")
        row.pop("_id", None)
        return row
