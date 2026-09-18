"""Authenticity-only verification of one archived legal-corpus authorization.

TITLE: WILSY OS Legal Corpus Operator Archival Authenticity Verifier
VERSION: v1.0.0-R1D-B0F-B4-R8O-P3C-LEGAL-CORPUS-ARCHIVAL-AUTHENTICITY-VERIFIER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Re-authenticates public D1 Ed25519 evidence at its signed issuance
         time using an archived trust snapshot, without asserting historical
         admission, current authorization, or any mutation capability.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_corpus_operator_archival_verification.py
COLLABORATION / OWNERSHIP: P3A supplies immutable public snapshots; this pure
                           verifier authenticates P1, P2, and P7; a later
                           P3C-C1 certificate and governed capture surface
                           remain separate artifacts.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.0.0-R1D-B0F-B4-R8O-P3C establishes a pure authenticity-only
           verifier that reuses D1 canonical payload helpers, verifies the
           archived trust-record fingerprint and Ed25519 signature at signed
           issuance time, and exposes explicit historical limits.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Public identifiers, timestamps, digests, and
                            public-key evidence only; no private-key,
                            filesystem, environment, network, request, or
                            database access exists here.
TENANT BOUNDARY: PLATFORM legal-corpus evidence only; no tenant or principal
                 authority is represented.
AUTHORITY BOUNDARY: Authenticity evidence only. This artifact cannot issue,
                    sign, authorize, admit, approve, review, accept, execute,
                    persist, or infer a historical admission event.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Snapshot drift, trust mismatch, inactive capture status,
                     key-window mismatch, or invalid signatures reject with a
                     stable non-sensitive error code.
"""
from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Final

from cryptography.exceptions import InvalidSignature

from tools.eos.legal_operations.domain.legal_corpus_archival_evidence import (
    LegalCorpusArchivalAuthorizationSnapshot,
    LegalCorpusArchivalEvidenceError,
    LegalCorpusArchivalTrustSnapshot,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_authorization import (
    SCHEMA as AUTHORIZATION_SCHEMA,
    LegalCorpusOperatorAuthorization,
    LegalCorpusOperatorAuthorizationError,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_trust_root import (
    AUTHORITY_DOMAIN,
    AUTHORIZED_OPERATION,
    ED25519_ALGORITHM,
    LegalCorpusOperatorKeyStatus,
    LegalCorpusOperatorTrustedKey,
    TRUST_ROOT_PROVENANCE,
    TRUST_ROOT_SCOPE,
)


VERSION: Final[str] = "v1.0.0-R1D-B0F-B4-R8O-P3C-LEGAL-CORPUS-ARCHIVAL-AUTHENTICITY-VERIFIER"
VERIFICATION_SCOPE: Final[str] = "D1_ARCHIVAL_AUTHENTICITY_AT_SIGNED_ISSUANCE"
_SIGNATURE_CHARS: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_-]+$")


class LegalCorpusOperatorArchivalVerificationError(ValueError):
    """Stable, non-sensitive fail-closed error for authenticity verification.

    The error contains only a bounded code. It does not expose signature,
    public-key, document, or exception internals, and it never grants an
    authorization or mutation capability.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _signature_bytes(value: object) -> bytes:
    """Decode one strict unpadded base64url Ed25519 signature."""
    if not isinstance(value, str) or not value or value != value.strip() or "=" in value:
        raise LegalCorpusOperatorArchivalVerificationError("SIGNATURE_ENCODING_INVALID")
    if _SIGNATURE_CHARS.fullmatch(value) is None:
        raise LegalCorpusOperatorArchivalVerificationError("SIGNATURE_ENCODING_INVALID")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * ((4 - len(value) % 4) % 4))
    except (binascii.Error, ValueError, TypeError):
        raise LegalCorpusOperatorArchivalVerificationError("SIGNATURE_ENCODING_INVALID") from None
    if len(decoded) != 64 or base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii") != value:
        raise LegalCorpusOperatorArchivalVerificationError("SIGNATURE_ENCODING_INVALID")
    return decoded


def _authorization_from_snapshot(
    snapshot: LegalCorpusArchivalAuthorizationSnapshot,
) -> LegalCorpusOperatorAuthorization:
    """Hydrate D1 structural semantics while retaining the P3A public boundary."""
    try:
        payload = snapshot.to_document()
        payload.pop("authorization_file_sha3_512", None)
        if payload.get("schema") != AUTHORIZATION_SCHEMA:
            raise LegalCorpusOperatorArchivalVerificationError("D1_SCHEMA_MISMATCH")
        return LegalCorpusOperatorAuthorization.from_document(payload)
    except LegalCorpusOperatorArchivalVerificationError:
        raise
    except (LegalCorpusOperatorAuthorizationError, KeyError, TypeError, ValueError) as error:
        raise LegalCorpusOperatorArchivalVerificationError("D1_SNAPSHOT_INVALID") from error


def _trust_snapshot_from_snapshot(
    snapshot: LegalCorpusArchivalTrustSnapshot,
) -> LegalCorpusArchivalTrustSnapshot:
    """Rehydrate P3A trust evidence so its own fingerprints are rechecked."""
    try:
        return LegalCorpusArchivalTrustSnapshot.from_document(snapshot.to_document())
    except (LegalCorpusArchivalEvidenceError, KeyError, TypeError, ValueError) as error:
        raise LegalCorpusOperatorArchivalVerificationError("TRUST_SNAPSHOT_INVALID") from error


def _authorization_snapshot_from_snapshot(
    snapshot: LegalCorpusArchivalAuthorizationSnapshot,
) -> LegalCorpusArchivalAuthorizationSnapshot:
    """Rehydrate P3A authorization evidence before D1 canonical reuse."""
    try:
        return LegalCorpusArchivalAuthorizationSnapshot.from_document(snapshot.to_document())
    except (LegalCorpusArchivalEvidenceError, KeyError, TypeError, ValueError) as error:
        raise LegalCorpusOperatorArchivalVerificationError("AUTHORIZATION_SNAPSHOT_INVALID") from error


def _trusted_key_from_snapshot(
    snapshot: LegalCorpusArchivalTrustSnapshot,
) -> LegalCorpusOperatorTrustedKey:
    """Reconstruct public trust material without consulting the live root."""
    try:
        expected_fingerprint = LegalCorpusOperatorTrustedKey.fingerprint_for(
            key_id=snapshot.key_id,
            algorithm=snapshot.algorithm,
            public_key_base64url=snapshot.public_key,
            issuer_identity=snapshot.issuer,
            authority_domain=snapshot.authority_domain,
            scope=snapshot.scope,
            permitted_operations=frozenset(snapshot.permitted_operations),
            valid_from=snapshot.valid_from,
            valid_until=snapshot.valid_until,
            status=snapshot.status_observed_at_archival_capture,
            revision=snapshot.revision,
            trust_root_provenance=snapshot.trust_root_provenance,
        )
    except (TypeError, ValueError) as error:
        raise LegalCorpusOperatorArchivalVerificationError("TRUST_RECORD_INVALID") from error
    if expected_fingerprint != snapshot.trust_record_fingerprint:
        raise LegalCorpusOperatorArchivalVerificationError("TRUST_RECORD_FINGERPRINT_MISMATCH")
    if snapshot.status_observed_at_archival_capture is not LegalCorpusOperatorKeyStatus.ACTIVE:
        raise LegalCorpusOperatorArchivalVerificationError("TRUST_STATUS_NOT_ACTIVE_AT_CAPTURE")
    try:
        return LegalCorpusOperatorTrustedKey(
            key_id=snapshot.key_id,
            algorithm=snapshot.algorithm,
            public_key_base64url=snapshot.public_key,
            issuer_identity=snapshot.issuer,
            authority_domain=snapshot.authority_domain,
            scope=snapshot.scope,
            permitted_operations=frozenset(snapshot.permitted_operations),
            valid_from=snapshot.valid_from,
            valid_until=snapshot.valid_until,
            status=snapshot.status_observed_at_archival_capture,
            revision=snapshot.revision,
            trust_root_provenance=snapshot.trust_root_provenance,
            fingerprint=snapshot.trust_record_fingerprint,
        )
    except (TypeError, ValueError) as error:
        raise LegalCorpusOperatorArchivalVerificationError("TRUST_RECORD_INVALID") from error


@dataclass(frozen=True, slots=True)
class LegalCorpusOperatorArchivalVerificationResult:
    """Immutable, explicitly bounded authenticity findings.

    Positive fields prove only signed D1 authenticity, signed-time validity,
    archived trust-window containment, public-key identity, and trust-record
    integrity. The negative fields permanently state that no admission event,
    D1-to-R8D identity binding, current validity, or mutation authority was
    established. No ambiguous authorization-status flag exists.
    """

    authorization_id: str
    key_id: str
    signed_issued_at: datetime
    signature_authentic: bool
    authorization_window_contains_issued_at: bool
    trust_validity_interval_contains_issued_at: bool
    public_key_identity_verified: bool
    trust_record_fingerprint_verified: bool
    historical_admission_event_time_available: bool
    d1_to_r8d_identity_binding_established: bool
    d1_bound_to_r8d: bool
    can_authorize_new_mutation: bool
    trust_status_observed_at_capture: LegalCorpusOperatorKeyStatus

    def __post_init__(self) -> None:
        """Enforce the result's non-authorizing semantic boundary."""
        if not isinstance(self.authorization_id, str) or not self.authorization_id.strip():
            raise LegalCorpusOperatorArchivalVerificationError("RESULT_AUTHORIZATION_ID_INVALID")
        if not isinstance(self.key_id, str) or not self.key_id.strip():
            raise LegalCorpusOperatorArchivalVerificationError("RESULT_KEY_ID_INVALID")
        if not isinstance(self.signed_issued_at, datetime) or self.signed_issued_at.tzinfo is None or self.signed_issued_at.utcoffset() is None:
            raise LegalCorpusOperatorArchivalVerificationError("RESULT_TIMESTAMP_INVALID")
        if self.trust_status_observed_at_capture is not LegalCorpusOperatorKeyStatus.ACTIVE:
            raise LegalCorpusOperatorArchivalVerificationError("RESULT_TRUST_STATUS_INVALID")
        required_true = (
            self.signature_authentic,
            self.authorization_window_contains_issued_at,
            self.trust_validity_interval_contains_issued_at,
            self.public_key_identity_verified,
            self.trust_record_fingerprint_verified,
        )
        if any(value is not True for value in required_true):
            raise LegalCorpusOperatorArchivalVerificationError("RESULT_POSITIVE_FINDING_INVALID")
        prohibited_true = (
            self.historical_admission_event_time_available,
            self.d1_to_r8d_identity_binding_established,
            self.d1_bound_to_r8d,
            self.can_authorize_new_mutation,
        )
        if any(value is not False for value in prohibited_true):
            raise LegalCorpusOperatorArchivalVerificationError("RESULT_AUTHORITY_BOUNDARY_INVALID")
        object.__setattr__(self, "signed_issued_at", self.signed_issued_at.astimezone(timezone.utc))

    def to_document(self) -> dict[str, object]:
        """Serialize stable primitive findings without introducing authority."""
        return {
            "verification_scope": VERIFICATION_SCOPE,
            "authorization_id": self.authorization_id,
            "key_id": self.key_id,
            "signed_issued_at": self.signed_issued_at.isoformat(timespec="microseconds"),
            "signature_authentic": self.signature_authentic,
            "authorization_window_contains_issued_at": self.authorization_window_contains_issued_at,
            "trust_validity_interval_contains_issued_at": self.trust_validity_interval_contains_issued_at,
            "public_key_identity_verified": self.public_key_identity_verified,
            "trust_record_fingerprint_verified": self.trust_record_fingerprint_verified,
            "historical_admission_event_time_available": self.historical_admission_event_time_available,
            "d1_to_r8d_identity_binding_established": self.d1_to_r8d_identity_binding_established,
            "d1_bound_to_r8d": self.d1_bound_to_r8d,
            "can_authorize_new_mutation": self.can_authorize_new_mutation,
            "trust_status_observed_at_capture": self.trust_status_observed_at_capture.value,
        }


def verify_archival_d1_authenticity(
    authorization_snapshot: LegalCorpusArchivalAuthorizationSnapshot,
    trust_snapshot: LegalCorpusArchivalTrustSnapshot,
) -> LegalCorpusOperatorArchivalVerificationResult:
    """Freshly verify public D1 authenticity at signed issuance time only.

    P3A snapshots are rehydrated and self-validated, the D1 canonical payload
    is reused verbatim, the archived trust record is fingerprint-checked, and
    Ed25519 is verified against the archived public key. No current wall clock,
    live trust-root resolver, R8D/document registry, database, filesystem, or
    mutation surface is consulted. The caller cannot provide an admission-event
    timestamp or turn this result into an authorization.

    :raises LegalCorpusOperatorArchivalVerificationError: on any structural,
        trust, signed-window, key-identity, or signature failure.
    """
    if not isinstance(authorization_snapshot, LegalCorpusArchivalAuthorizationSnapshot):
        raise LegalCorpusOperatorArchivalVerificationError("AUTHORIZATION_SNAPSHOT_REQUIRED")
    if not isinstance(trust_snapshot, LegalCorpusArchivalTrustSnapshot):
        raise LegalCorpusOperatorArchivalVerificationError("TRUST_SNAPSHOT_REQUIRED")
    authorization_snapshot = _authorization_snapshot_from_snapshot(authorization_snapshot)
    trust_snapshot = _trust_snapshot_from_snapshot(trust_snapshot)
    authorization = _authorization_from_snapshot(authorization_snapshot)
    trusted_key = _trusted_key_from_snapshot(trust_snapshot)
    if authorization.key_id != trusted_key.key_id:
        raise LegalCorpusOperatorArchivalVerificationError("D1_TRUST_KEY_ID_MISMATCH")
    if authorization.operation.value != AUTHORIZED_OPERATION or authorization.scope.value != TRUST_ROOT_SCOPE:
        raise LegalCorpusOperatorArchivalVerificationError("D1_AUTHORITY_SCOPE_INVALID")
    if trusted_key.algorithm != ED25519_ALGORITHM or trusted_key.authority_domain != AUTHORITY_DOMAIN or trusted_key.scope != TRUST_ROOT_SCOPE or trusted_key.trust_root_provenance != TRUST_ROOT_PROVENANCE or not trusted_key.permits(AUTHORIZED_OPERATION):
        raise LegalCorpusOperatorArchivalVerificationError("TRUST_AUTHORITY_SCOPE_INVALID")
    authorization_window_contains = authorization.not_before <= authorization.issued_at <= authorization.expires_at
    if not authorization_window_contains:
        raise LegalCorpusOperatorArchivalVerificationError("D1_ISSUANCE_OUTSIDE_AUTHORIZATION_WINDOW")
    trust_window_contains = trusted_key.is_valid_at(authorization.issued_at)
    if not trust_window_contains:
        raise LegalCorpusOperatorArchivalVerificationError("TRUST_WINDOW_MISMATCH_AT_ISSUANCE")
    try:
        trusted_key.public_key().verify(_signature_bytes(authorization.signature), authorization.canonical_payload_bytes())
    except (InvalidSignature, TypeError, ValueError):
        raise LegalCorpusOperatorArchivalVerificationError("SIGNATURE_INVALID") from None
    return LegalCorpusOperatorArchivalVerificationResult(
        authorization_id=authorization.authorization_id,
        key_id=authorization.key_id,
        signed_issued_at=authorization.issued_at,
        signature_authentic=True,
        authorization_window_contains_issued_at=True,
        trust_validity_interval_contains_issued_at=True,
        public_key_identity_verified=True,
        trust_record_fingerprint_verified=True,
        historical_admission_event_time_available=False,
        d1_to_r8d_identity_binding_established=False,
        d1_bound_to_r8d=False,
        can_authorize_new_mutation=False,
        trust_status_observed_at_capture=trust_snapshot.status_observed_at_archival_capture,
    )


__all__ = [
    "LegalCorpusOperatorArchivalVerificationError",
    "LegalCorpusOperatorArchivalVerificationResult",
    "VERSION",
    "VERIFICATION_SCOPE",
    "verify_archival_d1_authenticity",
]


# ARTIFACT: legal_corpus_operator_archival_verification.py
# VERSION: v1.0.0-R1D-B0F-B4-R8O-P3C-LEGAL-CORPUS-ARCHIVAL-AUTHENTICITY-VERIFIER
# AUTHORITY BOUNDARY: authenticity evidence only; no admission or mutation authority
# TENANT POSTURE: PLATFORM scope; no tenant or principal authority
# FAIL-CLOSED POSTURE: archived trust, signed-window, key identity, and signature drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
