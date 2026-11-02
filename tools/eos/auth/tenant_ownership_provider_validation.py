"""Fail-closed conformance primitives for governed tenant ownership providers.

These validators establish cryptographic integrity, source consistency and replay
resistance only. They do not determine legal ownership, appoint an issuer, or
construct VerifiedTenantOwnershipEvidence. All Mongo writes require a caller-
owned active transaction.
"""
from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import re
from typing import Any, Final, Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.tenant_ownership_provider_ports import (
    RecoveryDecisionLookup,
    RecoveryDecisionReceipt,
    RegistrySnapshot,
)

VERSION: Final[str] = "v1.0.0-ISSUE-300-CONFORMANCE-CRYPTO-RECOVERY"
_DIGEST = re.compile(r"(?:sha256:)?[0-9a-f]{64}\Z", re.IGNORECASE)
_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}\Z")
RECOVERY_REPLAYS: Final[str] = "tenant_ownership_recovery_decision_replays"


class OwnershipProviderEvidenceError(ValueError):
    """Stable, content-free provider evidence rejection."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _token(name: str, value: object) -> str:
    if type(value) is not str or _TOKEN.fullmatch(value) is None:
        raise OwnershipProviderEvidenceError(f"{name.upper()}_INVALID")
    return value


def _instant(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise OwnershipProviderEvidenceError(f"{name.upper()}_MUST_BE_TIMEZONE_AWARE")
    return value.astimezone(timezone.utc)


def _fingerprint(name: str, value: object) -> str:
    if type(value) is not str or _DIGEST.fullmatch(value) is None:
        raise OwnershipProviderEvidenceError(f"{name.upper()}_INVALID")
    return value.lower().removeprefix("sha256:")


@dataclass(frozen=True, slots=True)
class RegistryFreshnessPolicy:
    max_age: timedelta = timedelta(hours=24)
    max_future_skew: timedelta = timedelta(minutes=2)


@dataclass(frozen=True, slots=True)
class RegistryLineageAssessment:
    current_filing_reference: str
    current_filing_revision: str
    source_fingerprint: str
    observed_filing_references: tuple[str, ...]


def assess_registry_lineage(
    snapshots: Iterable[RegistrySnapshot],
    *,
    evaluated_at: datetime,
    policy: RegistryFreshnessPolicy = RegistryFreshnessPolicy(),
) -> RegistryLineageAssessment:
    """Reject stale, future-dated, forked, cyclic or ambiguous filing histories."""
    now = _instant("evaluated_at", evaluated_at)
    items = tuple(snapshots)
    if not items:
        raise OwnershipProviderEvidenceError("REGISTRY_SNAPSHOT_REQUIRED")
    if policy.max_age <= timedelta(0) or policy.max_future_skew < timedelta(0):
        raise OwnershipProviderEvidenceError("REGISTRY_FRESHNESS_POLICY_INVALID")

    by_ref: dict[str, RegistrySnapshot] = {}
    identity: tuple[str, str, str] | None = None
    for item in items:
        if type(item) is not RegistrySnapshot:
            raise OwnershipProviderEvidenceError("REGISTRY_SNAPSHOT_INVALID")
        source = _token("source_id", item.source_id)
        record = _token("record_reference", item.record_reference)
        filing = _token("filing_reference", item.filing_reference)
        _token("filing_revision", item.filing_revision)
        jurisdiction = _token("jurisdiction", item.jurisdiction)
        _token("entity_type", item.entity_type)
        status = _token("record_status", item.record_status).upper()
        retrieved = _instant("registry_retrieved_at", item.retrieved_at)
        effective = _instant("registry_effective_at", item.effective_at)
        source_fp = _fingerprint("source_fingerprint", item.source_fingerprint)
        _fingerprint("attributes_fingerprint", item.attributes_fingerprint)
        if retrieved > now + policy.max_future_skew or effective > now + policy.max_future_skew:
            raise OwnershipProviderEvidenceError("REGISTRY_SNAPSHOT_FROM_FUTURE")
        if now - retrieved > policy.max_age:
            raise OwnershipProviderEvidenceError("REGISTRY_SNAPSHOT_STALE")
        if effective > retrieved + policy.max_future_skew:
            raise OwnershipProviderEvidenceError("REGISTRY_EFFECTIVE_AFTER_RETRIEVAL")
        key = (source, record, jurisdiction)
        if identity is None:
            identity = key
        elif identity != key:
            raise OwnershipProviderEvidenceError("REGISTRY_SOURCE_OR_ENTITY_CONFLICT")
        previous = by_ref.get(filing)
        if previous is not None and (
            previous.source_fingerprint != item.source_fingerprint
            or previous.attributes_fingerprint != item.attributes_fingerprint
            or previous.filing_revision != item.filing_revision
        ):
            raise OwnershipProviderEvidenceError("REGISTRY_FILING_FINGERPRINT_CONFLICT")
        by_ref[filing] = item
        if status not in {"ACTIVE", "CURRENT", "SUPERSEDED", "WITHDRAWN", "CANCELLED", "DISSOLVED"}:
            raise OwnershipProviderEvidenceError("REGISTRY_STATUS_UNRECOGNIZED")

    superseded_by: dict[str, str] = {}
    for filing, item in by_ref.items():
        parent = item.supersedes_filing_reference
        if parent is not None:
            _token("superseded_filing_reference", parent)
            if parent == filing or parent not in by_ref:
                raise OwnershipProviderEvidenceError("REGISTRY_SUPERSESSION_LINEAGE_INVALID")
            if parent in superseded_by:
                raise OwnershipProviderEvidenceError("REGISTRY_SUPERSESSION_FORK")
            superseded_by[parent] = filing

    for start in by_ref:
        seen: set[str] = set()
        current = start
        while current in superseded_by:
            if current in seen:
                raise OwnershipProviderEvidenceError("REGISTRY_SUPERSESSION_CYCLE")
            seen.add(current)
            current = superseded_by[current]

    terminal = [ref for ref in by_ref if ref not in superseded_by]
    if len(terminal) != 1:
        raise OwnershipProviderEvidenceError("REGISTRY_CURRENT_FILING_AMBIGUOUS")
    current_ref = terminal[0]
    current = by_ref[current_ref]
    if current.record_status.upper() not in {"ACTIVE", "CURRENT"}:
        raise OwnershipProviderEvidenceError("REGISTRY_CURRENT_RECORD_NOT_ACTIVE")
    return RegistryLineageAssessment(
        current_filing_reference=current_ref,
        current_filing_revision=current.filing_revision,
        source_fingerprint=_fingerprint("source_fingerprint", current.source_fingerprint),
        observed_filing_references=tuple(sorted(by_ref)),
    )


@dataclass(frozen=True, slots=True)
class VerificationKey:
    key_reference: str
    key_revision: int
    algorithm: str
    public_key_pem: bytes
    valid_from: datetime
    valid_until: datetime
    revoked_at: datetime | None = None
    superseded_at: datetime | None = None


def verify_provider_signature(
    *,
    message: bytes,
    signature_b64: str,
    key: VerificationKey,
    evaluated_at: datetime,
) -> str:
    """Verify exact bytes against one versioned key and its validity/revocation window."""
    now = _instant("evaluated_at", evaluated_at)
    _token("key_reference", key.key_reference)
    if type(key.key_revision) is not int or key.key_revision < 1:
        raise OwnershipProviderEvidenceError("SIGNING_KEY_REVISION_INVALID")
    start, end = _instant("key_valid_from", key.valid_from), _instant("key_valid_until", key.valid_until)
    if end <= start or now < start or now >= end:
        raise OwnershipProviderEvidenceError("SIGNING_KEY_NOT_CURRENT")
    if key.revoked_at is not None and now >= _instant("key_revoked_at", key.revoked_at):
        raise OwnershipProviderEvidenceError("SIGNING_KEY_REVOKED")
    if key.superseded_at is not None and now >= _instant("key_superseded_at", key.superseded_at):
        raise OwnershipProviderEvidenceError("SIGNING_KEY_SUPERSEDED")
    if type(message) is not bytes or not message:
        raise OwnershipProviderEvidenceError("SIGNING_MESSAGE_INVALID")
    try:
        signature = base64.b64decode(signature_b64, validate=True)
        public_key = serialization.load_pem_public_key(key.public_key_pem)
        algorithm = key.algorithm.upper()
        if algorithm == "ED25519" and isinstance(public_key, ed25519.Ed25519PublicKey):
            public_key.verify(signature, message)
        elif algorithm == "ECDSA_SHA256" and isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        elif algorithm == "RSA_PSS_SHA256" and isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(
                signature, message,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
        else:
            raise OwnershipProviderEvidenceError("SIGNING_ALGORITHM_KEY_TYPE_MISMATCH")
    except OwnershipProviderEvidenceError:
        raise
    except (ValueError, TypeError, binascii.Error, InvalidSignature) as error:
        raise OwnershipProviderEvidenceError("SIGNATURE_INVALID") from error
    return sha256(message).hexdigest()


def validate_recovery_decision(
    lookup: RecoveryDecisionLookup,
    receipt: RecoveryDecisionReceipt,
    *,
    evaluated_at: datetime,
) -> None:
    """Bind an independent, final, unappealed decision to one exact recovery case."""
    if type(lookup) is not RecoveryDecisionLookup or type(receipt) is not RecoveryDecisionReceipt:
        raise OwnershipProviderEvidenceError("RECOVERY_DECISION_TYPES_INVALID")
    now = _instant("evaluated_at", evaluated_at)
    for name in ("tenant_id", "legal_entity_reference", "recovery_case_reference", "successor_principal_id"):
        _token(name, getattr(lookup, name))
    for name in ("recovery_case_fingerprint",):
        _fingerprint(name, getattr(lookup, name))
    for name in ("authority_id", "trust_root_reference", "decision_reference", "appeal_status"):
        _token(name, getattr(receipt, name))
    for name in ("trust_root_fingerprint", "decision_fingerprint", "recovery_case_fingerprint",
                 "quorum_fingerprint", "conflict_check_fingerprint", "notice_and_objection_fingerprint"):
        _fingerprint(name, getattr(receipt, name))
    if (
        receipt.recovery_case_reference != lookup.recovery_case_reference
        or receipt.recovery_case_fingerprint != lookup.recovery_case_fingerprint
        or receipt.successor_principal_id != lookup.successor_principal_id
    ):
        raise OwnershipProviderEvidenceError("RECOVERY_DECISION_SCOPE_MISMATCH")
    if receipt.appeal_status.upper() not in {"FINAL", "NO_APPEAL", "APPEAL_EXHAUSTED"}:
        raise OwnershipProviderEvidenceError("RECOVERY_DECISION_NOT_FINAL")
    issued = _instant("recovery_decision_issued_at", receipt.issued_at)
    expires = _instant("recovery_decision_valid_until", receipt.valid_until)
    if issued > now or expires <= now or expires <= issued:
        raise OwnershipProviderEvidenceError("RECOVERY_DECISION_NOT_CURRENT")
    if not receipt.authority_id or not receipt.trust_root_reference:
        raise OwnershipProviderEvidenceError("RECOVERY_AUTHORITY_REQUIRED")


def _active_transaction(session: Any) -> None:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        raise OwnershipProviderEvidenceError("ACTIVE_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise OwnershipProviderEvidenceError("ACTIVE_TRANSACTION_REQUIRED")


class RecoveryDecisionReplayRegistry:
    """Atomically consume one decision once, inside the caller's Mongo transaction."""

    def __init__(self, database: Any) -> None:
        if database is None:
            raise OwnershipProviderEvidenceError("RECOVERY_REPLAY_DATABASE_REQUIRED")
        self._events = database[RECOVERY_REPLAYS]

    def ensure_indexes(self) -> None:
        self._events.create_index(
            [("tenant_id", ASCENDING), ("decision_reference", ASCENDING)],
            unique=True, name="tenant_ownership_recovery_decision_once",
        )
        self._events.create_index(
            [("tenant_id", ASCENDING), ("recovery_case_reference", ASCENDING)],
            unique=True, name="tenant_ownership_recovery_case_once",
        )

    def consume(
        self,
        lookup: RecoveryDecisionLookup,
        receipt: RecoveryDecisionReceipt,
        *,
        session: Any,
        evaluated_at: datetime,
    ) -> None:
        _active_transaction(session)
        validate_recovery_decision(lookup, receipt, evaluated_at=evaluated_at)
        try:
            self._events.insert_one({
                "tenant_id": lookup.tenant_id,
                "legal_entity_reference": lookup.legal_entity_reference,
                "recovery_case_reference": lookup.recovery_case_reference,
                "recovery_case_fingerprint": lookup.recovery_case_fingerprint,
                "successor_principal_id": lookup.successor_principal_id,
                "decision_reference": receipt.decision_reference,
                "decision_fingerprint": receipt.decision_fingerprint,
                "authority_id": receipt.authority_id,
                "trust_root_reference": receipt.trust_root_reference,
                "trust_root_fingerprint": receipt.trust_root_fingerprint,
                "issued_at": _instant("issued_at", receipt.issued_at),
                "consumed_at": _instant("evaluated_at", evaluated_at),
            }, session=session)
        except DuplicateKeyError as error:
            raise OwnershipProviderEvidenceError("RECOVERY_DECISION_REPLAY") from error
        except PyMongoError as error:
            raise OwnershipProviderEvidenceError("RECOVERY_DECISION_PERSISTENCE_FAILED") from error


__all__ = [
    "OwnershipProviderEvidenceError", "RECOVERY_REPLAYS", "RegistryFreshnessPolicy",
    "RegistryLineageAssessment", "RecoveryDecisionReplayRegistry", "VerificationKey",
    "VERSION", "assess_registry_lineage", "validate_recovery_decision",
    "verify_provider_signature",
]
