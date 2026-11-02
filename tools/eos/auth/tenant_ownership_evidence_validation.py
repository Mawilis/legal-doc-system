"""Fail-closed ownership evidence validation primitives.

Pure validators deliberately do not issue VerifiedTenantOwnershipEvidence. They
validate provider receipts and source facts; governance composition remains a
separate, unavailable authority gate. Mongo writes require caller transactions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import re
from typing import Any, Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from .tenant_ownership_provider_ports import (
    RecoveryDecisionLookup, RecoveryDecisionReceipt, RegistrySnapshot,
    SigningReceipt, SigningRequest,
)

_HEX_256 = re.compile(r"[0-9a-f]{64}\Z")
_DOMAIN = b"WILSY:TENANT-OWNERSHIP:EVIDENCE:v1\0"


class OwnershipEvidenceValidationError(RuntimeError):
    """Stable denial code with no source or personal data."""


@dataclass(frozen=True, slots=True)
class RegistryAssessment:
    status: str
    selected_filing_reference: str | None
    source_fingerprint: str | None
    reason: str


def _utc(value: datetime, code: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise OwnershipEvidenceValidationError(code)
    return value.astimezone(timezone.utc)


def _fingerprint(value: str, code: str) -> str:
    if type(value) is not str or not _HEX_256.fullmatch(value):
        raise OwnershipEvidenceValidationError(code)
    return value


def assess_registry_snapshots(
    snapshots: tuple[RegistrySnapshot, ...],
    *,
    evaluated_at: datetime,
    max_age: timedelta,
) -> RegistryAssessment:
    """Resolve filing lineage deterministically; ambiguity and stale data deny."""
    now = _utc(evaluated_at, "REGISTRY_EVALUATION_TIME_INVALID")
    if max_age <= timedelta(0):
        raise OwnershipEvidenceValidationError("REGISTRY_MAX_AGE_INVALID")
    if not snapshots:
        return RegistryAssessment("DENY", None, None, "SOURCE_RECORD_MISSING")
    by_filing: dict[str, RegistrySnapshot] = {}
    for item in snapshots:
        if type(item) is not RegistrySnapshot:
            raise OwnershipEvidenceValidationError("REGISTRY_SNAPSHOT_INVALID")
        if item.filing_reference in by_filing:
            raise OwnershipEvidenceValidationError("REGISTRY_DUPLICATE_FILING_REFERENCE")
        retrieved = _utc(item.retrieved_at, "REGISTRY_RETRIEVAL_TIME_INVALID")
        effective = _utc(item.effective_at, "REGISTRY_EFFECTIVE_TIME_INVALID")
        _fingerprint(item.source_fingerprint, "REGISTRY_SOURCE_FINGERPRINT_INVALID")
        _fingerprint(item.attributes_fingerprint, "REGISTRY_ATTRIBUTES_FINGERPRINT_INVALID")
        if retrieved > now or effective > now:
            return RegistryAssessment("DENY", None, None, "SOURCE_RECORD_FROM_FUTURE")
        if now - retrieved > max_age:
            return RegistryAssessment("DENY", None, None, "SOURCE_RECORD_STALE")
        by_filing[item.filing_reference] = item
    if not by_filing:
        return RegistryAssessment("DENY", None, None, "NO_CURRENT_FILING")
    # Every supersession target must exist and remain in the same source/entity scope.
    superseded: set[str] = set()
    for item in by_filing.values():
        parent = item.supersedes_filing_reference
        if parent is not None:
            if parent == item.filing_reference:
                return RegistryAssessment("DENY", None, None, "FILING_LINEAGE_CYCLE")
            if parent not in by_filing:
                return RegistryAssessment("DENY", None, None, "SUPERSESSION_TARGET_MISSING")
            prior = by_filing[parent]
            if (prior.source_id, prior.record_reference, prior.jurisdiction) != (
                item.source_id, item.record_reference, item.jurisdiction
            ):
                return RegistryAssessment("DENY", None, None, "SUPERSESSION_SCOPE_MISMATCH")
            superseded.add(parent)
    # Detect cycles, including cycles longer than one edge.
    for start in by_filing:
        seen: set[str] = set()
        cursor: str | None = start
        while cursor is not None:
            if cursor in seen:
                return RegistryAssessment("DENY", None, None, "FILING_LINEAGE_CYCLE")
            seen.add(cursor)
            current = by_filing.get(cursor)
            cursor = current.supersedes_filing_reference if current else None
    heads = [item for key, item in by_filing.items() if key not in superseded]
    if len(heads) != 1:
        return RegistryAssessment("DENY", None, None, "CONFLICTING_CURRENT_FILINGS")
    head = heads[0]
    if head.record_status.upper() not in {"ACTIVE", "CURRENT"}:
        return RegistryAssessment("DENY", None, None, "SOURCE_RECORD_NOT_ACTIVE")
    return RegistryAssessment("VERIFIED_SOURCE_FACT", head.filing_reference,
                               head.source_fingerprint, "CURRENT_UNAMBIGUOUS_FILING")


class KeyStatusProvider(Protocol):
    def key_status(self, key_reference: str, revision: int, at: datetime) -> str: ...
    def public_key(self, key_reference: str, revision: int) -> Ed25519PublicKey: ...


class RecoveryKeyTrustProvider(Protocol):
    def recovery_key_status(
        self, authority_id: str, trust_root_reference: str, trust_root_fingerprint: str,
        key_reference: str, revision: int, at: datetime,
    ) -> str: ...
    def public_key(self, key_reference: str, revision: int) -> Ed25519PublicKey: ...


def signing_message(request: SigningRequest) -> bytes:
    """Canonical domain-separated message; binds digest, tenant, key and purpose."""
    digest = _fingerprint(request.payload_digest, "SIGNING_PAYLOAD_DIGEST_INVALID")
    if request.digest_algorithm.lower() != "sha256":
        raise OwnershipEvidenceValidationError("SIGNING_DIGEST_ALGORITHM_UNSUPPORTED")
    if not request.tenant_id or not request.purpose or not request.key_reference:
        raise OwnershipEvidenceValidationError("SIGNING_SCOPE_INVALID")
    if type(request.key_revision) is not int or request.key_revision < 1:
        raise OwnershipEvidenceValidationError("SIGNING_KEY_REVISION_INVALID")
    return _DOMAIN + b"|".join((
        b"sha256", digest.encode(), request.tenant_id.encode(),
        request.purpose.encode(), request.key_reference.encode(),
        str(request.key_revision).encode(),
    ))


def verify_signing_receipt(
    request: SigningRequest,
    receipt: SigningReceipt,
    keys: KeyStatusProvider,
) -> None:
    """Verify exact request binding, key revision, validity/revocation and Ed25519."""
    message = signing_message(request)
    if type(receipt) is not SigningReceipt:
        raise OwnershipEvidenceValidationError("SIGNING_RECEIPT_INVALID")
    if (receipt.key_reference, receipt.key_revision, receipt.payload_digest,
        receipt.purpose) != (request.key_reference, request.key_revision,
                             request.payload_digest, request.purpose):
        raise OwnershipEvidenceValidationError("SIGNING_RECEIPT_REQUEST_MISMATCH")
    signed_at = _utc(receipt.signed_at, "SIGNING_TIMESTAMP_INVALID")
    evaluated = _utc(request.evaluated_at, "SIGNING_EVALUATION_TIME_INVALID")
    if signed_at > evaluated:
        raise OwnershipEvidenceValidationError("SIGNING_TIMESTAMP_FROM_FUTURE")
    try:
        key_status = keys.key_status(request.key_reference, request.key_revision, evaluated)
    except Exception as error:
        raise OwnershipEvidenceValidationError("SIGNING_KEY_STATUS_UNAVAILABLE") from error
    if key_status != "ACTIVE":
        raise OwnershipEvidenceValidationError("SIGNING_KEY_NOT_CURRENT_OR_REVOKED")
    if receipt.algorithm != "Ed25519":
        raise OwnershipEvidenceValidationError("SIGNING_ALGORITHM_UNSUPPORTED")
    _fingerprint(receipt.custody_proof_fingerprint, "SIGNING_CUSTODY_PROOF_INVALID")
    try:
        signature = bytes.fromhex(receipt.signature)
        keys.public_key(request.key_reference, request.key_revision).verify(signature, message)
    except (ValueError, InvalidSignature, KeyError) as error:
        raise OwnershipEvidenceValidationError("SIGNING_SIGNATURE_INVALID") from error
    except Exception as error:
        raise OwnershipEvidenceValidationError("SIGNING_KEY_RESOLUTION_UNAVAILABLE") from error



@dataclass(frozen=True, slots=True, init=False)
class ValidatedRecoveryDecision:
    """Unforgeable-by-normal-construction technical validation receipt."""

    tenant_id: str
    legal_entity_reference: str
    recovery_case_reference: str
    recovery_case_fingerprint: str
    successor_principal_id: str
    decision_reference: str
    decision_fingerprint: str
    validation_fingerprint: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        del args, kwargs
        raise OwnershipEvidenceValidationError("VALIDATED_RECOVERY_DECISION_CONSTRUCTOR_DISABLED")


def _validated_recovery_decision(
    lookup: RecoveryDecisionLookup, receipt: RecoveryDecisionReceipt, message: bytes,
    signature: bytes,
) -> ValidatedRecoveryDecision:
    value = object.__new__(ValidatedRecoveryDecision)
    fields = {
        "tenant_id": lookup.tenant_id,
        "legal_entity_reference": lookup.legal_entity_reference,
        "recovery_case_reference": lookup.recovery_case_reference,
        "recovery_case_fingerprint": lookup.recovery_case_fingerprint,
        "successor_principal_id": lookup.successor_principal_id,
        "decision_reference": receipt.decision_reference,
        "decision_fingerprint": receipt.decision_fingerprint,
        "validation_fingerprint": sha256(message + signature).hexdigest(),
    }
    for name, item in fields.items():
        object.__setattr__(value, name, item)
    return value


@dataclass(frozen=True, slots=True)
class RecoveryDecisionEnvelope:
    receipt: RecoveryDecisionReceipt
    key_reference: str
    key_revision: int
    algorithm: str
    signature: str
    nonce: str


def recovery_decision_message(lookup: RecoveryDecisionLookup,
                              receipt: RecoveryDecisionReceipt,
                              key_reference: str, key_revision: int, nonce: str) -> bytes:
    """Canonical signed decision envelope bound to exact case and successor."""
    pairs = (
        (lookup.tenant_id, receipt.recovery_case_reference),
        (lookup.recovery_case_reference, receipt.recovery_case_reference),
        (lookup.recovery_case_fingerprint, receipt.recovery_case_fingerprint),
        (lookup.successor_principal_id, receipt.successor_principal_id),
    )
    if any(left != right for left, right in pairs):
        raise OwnershipEvidenceValidationError("RECOVERY_DECISION_SCOPE_MISMATCH")
    if not nonce or not key_reference or type(key_revision) is not int or key_revision < 1:
        raise OwnershipEvidenceValidationError("RECOVERY_DECISION_ENVELOPE_INVALID")
    return b"WILSY:TENANT-OWNERSHIP:RECOVERY:v1\0" + b"|".join(
        value.encode() for value in (
            lookup.tenant_id, lookup.legal_entity_reference,
            lookup.recovery_case_reference, lookup.recovery_case_fingerprint,
            lookup.successor_principal_id, receipt.authority_id,
            receipt.trust_root_reference, receipt.trust_root_fingerprint,
            receipt.decision_reference, receipt.decision_fingerprint,
            receipt.quorum_fingerprint, receipt.conflict_check_fingerprint,
            receipt.notice_and_objection_fingerprint, receipt.appeal_status,
            _utc(receipt.issued_at, "RECOVERY_DECISION_ISSUED_AT_INVALID").isoformat(),
            _utc(receipt.valid_until, "RECOVERY_DECISION_EXPIRY_INVALID").isoformat(),
            receipt.revocation_reference, key_reference, str(key_revision), nonce,
        )
    )


def validate_recovery_decision(
    lookup: RecoveryDecisionLookup,
    envelope: RecoveryDecisionEnvelope,
    keys: RecoveryKeyTrustProvider,
) -> ValidatedRecoveryDecision:
    """Validate independent authority receipt and return a persistence-only receipt."""
    receipt = envelope.receipt
    if type(receipt) is not RecoveryDecisionReceipt:
        raise OwnershipEvidenceValidationError("RECOVERY_DECISION_RECEIPT_INVALID")
    now = _utc(lookup.evaluated_at, "RECOVERY_EVALUATION_TIME_INVALID")
    issued = _utc(receipt.issued_at, "RECOVERY_DECISION_ISSUED_AT_INVALID")
    expires = _utc(receipt.valid_until, "RECOVERY_DECISION_EXPIRY_INVALID")
    if issued > now or expires <= now or expires <= issued:
        raise OwnershipEvidenceValidationError("RECOVERY_DECISION_NOT_CURRENT")
    if receipt.appeal_status not in {"RESOLVED", "NO_APPEAL_RIGHT"}:
        raise OwnershipEvidenceValidationError("RECOVERY_APPEAL_NOT_RESOLVED")
    for value in (receipt.trust_root_fingerprint, receipt.decision_fingerprint,
                  receipt.quorum_fingerprint, receipt.conflict_check_fingerprint,
                  receipt.notice_and_objection_fingerprint):
        _fingerprint(value, "RECOVERY_DECISION_EVIDENCE_FINGERPRINT_INVALID")
    if not receipt.authority_id or not receipt.revocation_reference:
        raise OwnershipEvidenceValidationError("RECOVERY_AUTHORITY_PROVENANCE_MISSING")
    if envelope.algorithm != "Ed25519":
        raise OwnershipEvidenceValidationError("RECOVERY_SIGNATURE_ALGORITHM_UNSUPPORTED")
    try:
        key_status = keys.recovery_key_status(
            receipt.authority_id, receipt.trust_root_reference, receipt.trust_root_fingerprint,
            envelope.key_reference, envelope.key_revision, now,
        )
    except Exception as error:
        raise OwnershipEvidenceValidationError("RECOVERY_KEY_STATUS_UNAVAILABLE") from error
    if key_status != "ACTIVE":
        raise OwnershipEvidenceValidationError("RECOVERY_SIGNING_KEY_NOT_CURRENT")
    message = recovery_decision_message(lookup, receipt, envelope.key_reference,
                                        envelope.key_revision, envelope.nonce)
    try:
        signature = bytes.fromhex(envelope.signature)
        keys.public_key(envelope.key_reference, envelope.key_revision).verify(
            signature, message
        )
    except (ValueError, InvalidSignature, KeyError) as error:
        raise OwnershipEvidenceValidationError("RECOVERY_DECISION_SIGNATURE_INVALID") from error
    except Exception as error:
        raise OwnershipEvidenceValidationError("RECOVERY_KEY_RESOLUTION_UNAVAILABLE") from error
    return _validated_recovery_decision(lookup, receipt, message, signature)


class RecoveryDecisionReplayRegistry:
    """Append-only decision replay ledger; caller owns transaction and commit."""

    COLLECTION = "tenant_ownership_recovery_decision_replays"

    def __init__(self, database: Any) -> None:
        self._rows = database[self.COLLECTION]
        self._rows.create_index([("tenant_id", ASCENDING), ("decision_reference", ASCENDING)],
                                unique=True, name="uq_tenant_recovery_decision")
        self._rows.create_index([("tenant_id", ASCENDING), ("recovery_case_reference", ASCENDING)],
                                unique=True, name="uq_tenant_recovery_case_once")

    def consume_validated(self, decision: ValidatedRecoveryDecision, *, session: Any) -> None:
        """Persist an already validated decision; no external calls occur in transaction."""
        if type(decision) is not ValidatedRecoveryDecision:
            raise OwnershipEvidenceValidationError("VALIDATED_RECOVERY_DECISION_REQUIRED")
        if session is None or not callable(getattr(session, "in_transaction", None)) or not session.in_transaction():
            raise OwnershipEvidenceValidationError("ACTIVE_TRANSACTION_REQUIRED")
        if not decision.tenant_id or not decision.decision_reference or not decision.decision_fingerprint:
            raise OwnershipEvidenceValidationError("RECOVERY_REPLAY_SCOPE_INVALID")
        try:
            self._rows.insert_one({
                "tenant_id": decision.tenant_id,
                "decision_reference": decision.decision_reference,
                "decision_fingerprint": decision.decision_fingerprint,
                "recovery_case_reference": decision.recovery_case_reference,
                "successor_principal_id": decision.successor_principal_id,
                "consumed_at": datetime.now(timezone.utc),
                "legal_entity_reference": decision.legal_entity_reference,
                "recovery_case_fingerprint": decision.recovery_case_fingerprint,
                "validation_fingerprint": decision.validation_fingerprint,
            }, session=session)
        except DuplicateKeyError as error:
            raise OwnershipEvidenceValidationError("RECOVERY_DECISION_REPLAY") from error
        except PyMongoError as error:
            raise OwnershipEvidenceValidationError("RECOVERY_REPLAY_PERSISTENCE_FAILED") from error
