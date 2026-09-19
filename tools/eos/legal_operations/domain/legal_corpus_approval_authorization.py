"""Domain verification for one signed legal-corpus approval authorization.

TITLE: WILSY OS Legal Corpus Approval Authorization Domain
VERSION: v1.1.0-R1D-B0F-R9B-P2-R6-R1-LEGAL-CORPUS-APPROVAL-AUTHORIZATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verifies an externally issued Ed25519 approval envelope against the
         source-owned approval trust root and complete approval evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_corpus_approval_authorization.py
COLLABORATION / OWNERSHIP: The future governed issuer owns human ceremony and
                           signing. This domain owns only immutable envelope
                           shape, canonical payload, and verification proof.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.1.0-R6-R1 repairs verified-proof forgeability, evaluates trust at
           authorization issuance time, and adds expected-evidence binding.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Public approval metadata only; no private key,
                            secret, filesystem, network, database, or request
                            context is accessed.
TENANT BOUNDARY: PLATFORM scope only; tenant and principal acceptance remain
                 separate downstream evidence.
AUTHORITY BOUNDARY: Successful verification proves only that a trusted key
                    authenticated this exact approval envelope. It does not
                    approve prose, create persistence, or authorize execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Unknown keys, lifecycle drift, malformed encodings,
                     temporal drift, signature failure, and evidence mismatch
                     reject with stable non-sensitive codes.
TRANSACTION BOUNDARY: Pure immutable values and verification; no DB/session,
                      HTTP, signing, or transaction lifecycle exists.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Final, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from tools.eos.legal_operations.domain.legal_acceptance import LegalDocumentVersion
from tools.eos.legal_operations.domain.legal_corpus_approval_authority import (
    LegalCorpusApprovalAuthorityError,
    LegalCorpusApprovalAuthorityEvidence,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_trust_root import (
    APPROVAL_AUTHORITY_DOMAIN,
    APPROVAL_AUTHORITY_ROLE,
    APPROVAL_ISSUER_IDENTITY,
    APPROVAL_OPERATION,
    APPROVAL_SCOPE,
    ED25519_ALGORITHM,
    LegalCorpusApprovalTrustRoot,
    LegalCorpusApprovalTrustRootError,
    LegalCorpusApprovalTrustStatus,
    LegalCorpusApprovalTrustedKey,
)


VERSION: Final[str] = "v1.1.0-R1D-B0F-R9B-P2-R6-R1-LEGAL-CORPUS-APPROVAL-AUTHORIZATION"
SCHEMA: Final[str] = "WILSY-LEGAL-CORPUS-APPROVAL-AUTHORIZATION/V1"
AUTHORITY_SCOPE: Final[str] = APPROVAL_SCOPE
AUTHORIZED_OPERATION: Final[str] = APPROVAL_OPERATION
SIGNATURE_ALGORITHM: Final[str] = ED25519_ALGORITHM
MAX_AUTHORIZATION_LIFETIME: Final[timedelta] = timedelta(minutes=30)
SIGNATURE_ENCODING: Final[str] = "base64url_without_padding_64_bytes"
NONCE_ENCODING: Final[str] = "base64url_without_padding_32_bytes"
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
_BASE64URL_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class LegalCorpusApprovalAuthorizationError(ValueError):
    """Stable, non-sensitive fail-closed approval verification error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCorpusApprovalAuthorizationOperation(StrEnum):
    """The sole operation representable by this approval envelope."""

    DOCUMENT_APPROVAL = AUTHORIZED_OPERATION


class LegalCorpusApprovalAuthorizationScope(StrEnum):
    """The sole non-tenant scope representable by this approval envelope."""

    PLATFORM = AUTHORITY_SCOPE


_VERIFIED_RESULT_TOKEN: Final[object] = object()


def _timestamp(value: object, code: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalCorpusApprovalAuthorizationError(code)
    return value.astimezone(timezone.utc)


def _canonical_timestamp(value: datetime) -> str:
    return _timestamp(value, "AUTHORIZATION_SCHEMA_INVALID").isoformat(timespec="microseconds")


def _text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise LegalCorpusApprovalAuthorizationError(code)
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise LegalCorpusApprovalAuthorizationError(code)
    return value


def _uuid4(value: object) -> str:
    candidate = _text(value, "AUTHORIZATION_SCHEMA_INVALID")
    if _UUID_RE.fullmatch(candidate) is None:
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SCHEMA_INVALID")
    try:
        parsed = uuid.UUID(candidate)
    except (ValueError, AttributeError):
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SCHEMA_INVALID") from None
    if parsed.version != 4 or str(parsed) != candidate:
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SCHEMA_INVALID")
    return candidate


def _encoded_bytes(value: object, *, expected: int, code: str) -> bytes:
    candidate = _text(value, code)
    if "=" in candidate or _BASE64URL_RE.fullmatch(candidate) is None:
        raise LegalCorpusApprovalAuthorizationError(code)
    try:
        decoded = base64.urlsafe_b64decode(candidate + "=" * ((4 - len(candidate) % 4) % 4))
    except (TypeError, ValueError):
        raise LegalCorpusApprovalAuthorizationError(code) from None
    if len(decoded) != expected or base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii") != candidate:
        raise LegalCorpusApprovalAuthorizationError(code)
    return decoded


def _evidence_document(document: LegalDocumentVersion, prefix: str) -> dict[str, object]:
    """Enumerate every immutable document field in the governed evidence."""
    return {
        f"{prefix}_document_id": document.document_id,
        f"{prefix}_agreement_type": document.agreement_type.value,
        f"{prefix}_version": document.version,
        f"{prefix}_title": document.title,
        f"{prefix}_jurisdiction": document.jurisdiction,
        f"{prefix}_locale": document.locale,
        f"{prefix}_effective_from": _canonical_timestamp(document.effective_from),
        f"{prefix}_status": document.status.value,
        f"{prefix}_content_reference": document.content_reference,
        f"{prefix}_content": document.content,
        f"{prefix}_sha3_512": document.sha3_512,
        f"{prefix}_created_at": _canonical_timestamp(document.created_at),
        f"{prefix}_supersedes_document_id": document.supersedes_document_id,
    }


def _evidence_payload(evidence: LegalCorpusApprovalAuthorityEvidence) -> dict[str, object]:
    """Return all 44 governed evidence fields, including its fingerprint."""
    payload: dict[str, object] = {
        "approval_evidence_id": evidence.approval_evidence_id,
        "schema_version": evidence.schema_version,
        "scope": evidence.scope.value,
        "operation": evidence.operation.value,
        "approval_decision": evidence.approval_decision.value,
        "approval_authority_source": evidence.approval_authority_source.value,
        "approval_authority_mechanism": evidence.approval_authority_mechanism.value,
        "approval_authority_mechanism_version": evidence.approval_authority_mechanism_version,
        "human_authority_representation": evidence.human_authority_representation,
        "approval_signing_mechanism": evidence.approval_signing_mechanism.value,
        "approval_signing_mechanism_version": evidence.approval_signing_mechanism_version,
        "approval_signing_key_id": evidence.approval_signing_key_id,
        "approval_signature_reference": evidence.approval_signature_reference,
        "approved_at": _canonical_timestamp(evidence.approved_at),
        "effective_from": _canonical_timestamp(evidence.effective_from),
        "idempotency_key": evidence.idempotency_key,
        "provenance_reference": evidence.provenance_reference,
    }
    payload.update(_evidence_document(evidence.source_document, "source"))
    payload.update(_evidence_document(evidence.approved_document, "approved"))
    payload["evidence_fingerprint"] = evidence.evidence_fingerprint
    return payload


def _canonical_json(payload: Mapping[str, object]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_signed_payload(authorization: "LegalCorpusApprovalAuthorization") -> bytes:
    """Return exact UTF-8 bytes authenticated by the external signer."""
    evidence = authorization.approval_evidence
    payload: dict[str, object] = {
        "algorithm": authorization.algorithm,
        "approval_evidence": _evidence_payload(evidence),
        "approval_evidence_fingerprint": evidence.evidence_fingerprint,
        "authority_domain": authorization.authority_domain,
        "authority_role": authorization.authority_role,
        "authorization_id": authorization.authorization_id,
        "expires_at": _canonical_timestamp(authorization.expires_at),
        "idempotency_key": authorization.idempotency_key,
        "issued_at": _canonical_timestamp(authorization.issued_at),
        "issuer_identity": authorization.issuer_identity,
        "key_id": authorization.key_id,
        "nonce": authorization.nonce,
        "operation": authorization.operation.value,
        "schema": authorization.schema,
        "scope": authorization.scope.value,
        "trust_fingerprint": authorization.trust_fingerprint,
    }
    return _canonical_json(payload)


@dataclass(frozen=True, slots=True)
class LegalCorpusApprovalAuthorization:
    """Immutable unverified envelope; construction never authenticates it."""

    authorization_id: str
    issuer_identity: str
    authority_role: str
    authority_domain: str
    algorithm: str
    key_id: str
    trust_fingerprint: str
    operation: LegalCorpusApprovalAuthorizationOperation
    scope: LegalCorpusApprovalAuthorizationScope
    approval_evidence: LegalCorpusApprovalAuthorityEvidence
    issued_at: datetime
    expires_at: datetime
    nonce: str
    idempotency_key: str
    signature_base64url: str
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        """Validate signed-envelope shape without trust lookup or crypto."""
        object.__setattr__(self, "authorization_id", _uuid4(self.authorization_id))
        object.__setattr__(self, "idempotency_key", _uuid4(self.idempotency_key))
        object.__setattr__(self, "issuer_identity", _text(self.issuer_identity, "AUTHORIZATION_SCHEMA_INVALID"))
        object.__setattr__(self, "authority_role", _text(self.authority_role, "AUTHORIZATION_SCHEMA_INVALID"))
        object.__setattr__(self, "authority_domain", _text(self.authority_domain, "AUTHORIZATION_SCHEMA_INVALID"))
        object.__setattr__(self, "algorithm", _text(self.algorithm, "AUTHORIZATION_SCHEMA_INVALID"))
        object.__setattr__(self, "key_id", _text(self.key_id, "AUTHORIZATION_SCHEMA_INVALID"))
        object.__setattr__(self, "trust_fingerprint", _text(self.trust_fingerprint, "AUTHORIZATION_SCHEMA_INVALID"))
        object.__setattr__(self, "nonce", _text(self.nonce, "AUTHORIZATION_NONCE_INVALID"))
        _encoded_bytes(self.nonce, expected=32, code="AUTHORIZATION_NONCE_INVALID")
        _encoded_bytes(self.signature_base64url, expected=64, code="AUTHORIZATION_SIGNATURE_ENCODING_INVALID")
        if self.schema != SCHEMA or self.algorithm != SIGNATURE_ALGORITHM:
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SCHEMA_INVALID")
        if self.issuer_identity != APPROVAL_ISSUER_IDENTITY:
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_ISSUER_MISMATCH")
        if self.authority_role != APPROVAL_AUTHORITY_ROLE or self.authority_domain != APPROVAL_AUTHORITY_DOMAIN:
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SCHEMA_INVALID")
        if self.operation is not LegalCorpusApprovalAuthorizationOperation.DOCUMENT_APPROVAL:
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_OPERATION_MISMATCH")
        if self.scope is not LegalCorpusApprovalAuthorizationScope.PLATFORM:
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SCOPE_MISMATCH")
        if not isinstance(self.approval_evidence, LegalCorpusApprovalAuthorityEvidence):
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_EVIDENCE_MISMATCH")
        issued = _timestamp(self.issued_at, "AUTHORIZATION_SCHEMA_INVALID")
        expires = _timestamp(self.expires_at, "AUTHORIZATION_SCHEMA_INVALID")
        if expires <= issued or expires - issued > MAX_AUTHORIZATION_LIFETIME:
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SCHEMA_INVALID")
        object.__setattr__(self, "issued_at", issued)
        object.__setattr__(self, "expires_at", expires)

    @property
    def signature(self) -> str:
        """Compatibility alias for the canonical signature field."""
        return self.signature_base64url

    def signed_payload(self) -> bytes:
        """Return canonical bytes without performing verification."""
        return canonical_signed_payload(self)

    def to_document(self) -> dict[str, object]:
        """Return stable primitive envelope serialization."""
        return {
            "schema": self.schema,
            "authorization_id": self.authorization_id,
            "issuer_identity": self.issuer_identity,
            "authority_role": self.authority_role,
            "authority_domain": self.authority_domain,
            "algorithm": self.algorithm,
            "key_id": self.key_id,
            "trust_fingerprint": self.trust_fingerprint,
            "operation": self.operation.value,
            "scope": self.scope.value,
            "approval_evidence": _evidence_payload(self.approval_evidence),
            "issued_at": _canonical_timestamp(self.issued_at),
            "expires_at": _canonical_timestamp(self.expires_at),
            "nonce": self.nonce,
            "idempotency_key": self.idempotency_key,
            "signature_base64url": self.signature_base64url,
        }


@dataclass(frozen=True, slots=True, init=False)
class VerifiedLegalCorpusApprovalAuthorization:
    """Immutable proof returned only after trust and signature verification."""

    authorization: LegalCorpusApprovalAuthorization
    trusted_key: LegalCorpusApprovalTrustedKey
    verified_at: datetime

    def __init__(
        self,
        authorization: LegalCorpusApprovalAuthorization,
        trusted_key: LegalCorpusApprovalTrustedKey,
        verified_at: datetime,
        *,
        _token: object | None = None,
    ) -> None:
        """Reject ordinary construction; only the verifier's private factory may create proof."""
        if _token is not _VERIFIED_RESULT_TOKEN:
            raise TypeError("verified approval proof is created only by verification")
        if not isinstance(authorization, LegalCorpusApprovalAuthorization) or not isinstance(trusted_key, LegalCorpusApprovalTrustedKey):
            raise TypeError("verified approval proof inputs are invalid")
        object.__setattr__(self, "authorization", authorization)
        object.__setattr__(self, "trusted_key", trusted_key)
        object.__setattr__(self, "verified_at", _timestamp(verified_at, "AUTHORIZATION_SCHEMA_INVALID"))

    @property
    def approval_evidence(self) -> LegalCorpusApprovalAuthorityEvidence:
        """Return the completely bound approval evidence."""
        return self.authorization.approval_evidence

    @property
    def authorization_id(self) -> str:
        """Return the verified authorization identity."""
        return self.authorization.authorization_id


def _verified_result(
    authorization: LegalCorpusApprovalAuthorization,
    trusted_key: LegalCorpusApprovalTrustedKey,
    verified_at: datetime,
) -> VerifiedLegalCorpusApprovalAuthorization:
    """Private construction seam used only after every verification check."""
    return VerifiedLegalCorpusApprovalAuthorization(
        authorization,
        trusted_key,
        verified_at,
        _token=_VERIFIED_RESULT_TOKEN,
    )


def verify_legal_corpus_approval_authorization(
    authorization: LegalCorpusApprovalAuthorization,
    trust_root: LegalCorpusApprovalTrustRoot,
    *,
    now: datetime,
    expected_evidence: LegalCorpusApprovalAuthorityEvidence | None = None,
    source_document: LegalDocumentVersion | None = None,
    approved_document: LegalDocumentVersion | None = None,
) -> VerifiedLegalCorpusApprovalAuthorization:
    """Verify one envelope against supplied source-owned trust and documents.

    ``now`` is mandatory and caller-controlled. No wall clock, persistence,
    key generation, signing, or production approval side effect occurs.
    """
    if not isinstance(authorization, LegalCorpusApprovalAuthorization) or not isinstance(trust_root, LegalCorpusApprovalTrustRoot):
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SCHEMA_INVALID")
    evaluation = _timestamp(now, "AUTHORIZATION_SCHEMA_INVALID")
    if evaluation < authorization.issued_at:
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_NOT_YET_VALID")
    if evaluation >= authorization.expires_at:
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_EXPIRED")
    try:
        trusted_key = trust_root.resolve(authorization.key_id)
    except LegalCorpusApprovalTrustRootError:
        raise LegalCorpusApprovalAuthorizationError("UNKNOWN_APPROVAL_KEY") from None
    if trusted_key.status is LegalCorpusApprovalTrustStatus.REVOKED:
        raise LegalCorpusApprovalAuthorizationError("APPROVAL_KEY_REVOKED")
    if trusted_key.key_id != authorization.key_id:
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_KEY_ID_MISMATCH")
    if trusted_key.trust_fingerprint != authorization.trust_fingerprint:
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_TRUST_FINGERPRINT_MISMATCH")
    if trusted_key.issuer_identity != authorization.issuer_identity:
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_ISSUER_MISMATCH")
    if trusted_key.authority_role != authorization.authority_role or trusted_key.authority_domain != authorization.authority_domain:
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SCHEMA_INVALID")
    if not trusted_key.can_verify_at(AUTHORIZED_OPERATION, AUTHORITY_SCOPE, authorization.issued_at):
        if trusted_key.status is LegalCorpusApprovalTrustStatus.RETIRED:
            raise LegalCorpusApprovalAuthorizationError("APPROVAL_KEY_RETIRED")
        raise LegalCorpusApprovalAuthorizationError("APPROVAL_KEY_NOT_ACTIVE")
    if expected_evidence is not None:
        if not isinstance(expected_evidence, LegalCorpusApprovalAuthorityEvidence) or authorization.approval_evidence != expected_evidence:
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_EVIDENCE_MISMATCH")
    if source_document is not None or approved_document is not None:
        if source_document is None or approved_document is None:
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_EVIDENCE_MISMATCH")
        try:
            authorization.approval_evidence.verify_against(source_document, approved_document)
        except LegalCorpusApprovalAuthorityError:
            raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_EVIDENCE_MISMATCH") from None
    try:
        public_key = Ed25519PublicKey.from_public_bytes(
            base64.urlsafe_b64decode(trusted_key.public_key_base64url + "=" * ((4 - len(trusted_key.public_key_base64url) % 4) % 4))
        )
        public_key.verify(_encoded_bytes(authorization.signature_base64url, expected=64, code="AUTHORIZATION_SIGNATURE_ENCODING_INVALID"), authorization.signed_payload())
    except LegalCorpusApprovalAuthorizationError:
        raise
    except (InvalidSignature, ValueError, TypeError):
        raise LegalCorpusApprovalAuthorizationError("AUTHORIZATION_SIGNATURE_INVALID") from None
    return _verified_result(authorization, trusted_key, evaluation)


__all__ = [
    "AUTHORIZED_OPERATION",
    "AUTHORITY_SCOPE",
    "MAX_AUTHORIZATION_LIFETIME",
    "NONCE_ENCODING",
    "SCHEMA",
    "SIGNATURE_ALGORITHM",
    "SIGNATURE_ENCODING",
    "LegalCorpusApprovalAuthorization",
    "LegalCorpusApprovalAuthorizationError",
    "LegalCorpusApprovalAuthorizationOperation",
    "LegalCorpusApprovalAuthorizationScope",
    "VerifiedLegalCorpusApprovalAuthorization",
    "canonical_signed_payload",
    "verify_legal_corpus_approval_authorization",
    "VERSION",
]


# ARTIFACT: legal_corpus_approval_authorization.py
# VERSION: v1.1.0-R1D-B0F-R9B-P2-R6-R1-LEGAL-CORPUS-APPROVAL-AUTHORIZATION
# AUTHORITY BOUNDARY: verification of externally signed PLATFORM approval only
# TENANT POSTURE: tenant-neutral; acceptance and organisation binding are separate
# FAIL-CLOSED POSTURE: malformed, untrusted, expired, revoked, or divergent proof rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
