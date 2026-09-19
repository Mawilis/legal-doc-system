"""Signed platform authorization for one exact legal-corpus draft.

TITLE: WILSY OS Legal Corpus Operator Authorization Domain
VERSION: v1.1.1-R1D-B0F-B4-R8J-JA-LEGAL-CORPUS-OPERATOR-AUTHORIZATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verifies an externally issued Ed25519 authorization against the
         canonical C1 operator trust root, which may contain governed public
         verification keys, and the Institutional Charter draft, then derives
         frozen R8D evidence without persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_corpus_operator_authorization.py
COLLABORATION / OWNERSHIP: An external governed issuer creates the signed
                           envelope; this value verifies it; R8D evidence
                           remains the next downstream immutable value.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.1.1-R1D-B0F-B4-R8J-JA repairs stale empty-production-trust-root
           sovereign metadata to reflect the governed C1 public-key root, with
           one production public key admitted at this gate. The patch makes no
           authorization-verification, signature, lifetime, Charter-binding,
           R8D-mapping, signing, private-key, or authorization-issuance change.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only opaque identifiers, public-key-derived issuer
                            identity, timestamps, and integrity digests are
                            represented; no secret material is accepted.
TENANT BOUNDARY: PLATFORM scope only; no tenant or principal authority exists.
AUTHORITY BOUNDARY: Verification of externally signed draft-admission evidence
                    only; D1 resolves only the canonical C1 trust root, rejects
                    caller-supplied trust, and does not issue, sign, approve,
                    persist, consume, or execute an authorization.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
TRANSACTION BOUNDARY: Pure in-process value and verification; no database,
                      session, transaction, HTTP, filesystem, or network work.
FAIL-CLOSED POSTURE: Unknown or untrusted public keys, invalid signatures,
                     lifecycle drift, temporal drift, and canonical-document
                     mismatch reject; a trusted public key is not itself a
                     valid signature or R8D evidence.
"""
from __future__ import annotations

import base64
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from dataclasses import dataclass, fields
from enum import StrEnum
from typing import Final, cast

from cryptography.exceptions import InvalidSignature

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_trust_root import (
    AUTHORITY_DOMAIN,
    AUTHORIZED_OPERATION as TRUST_ROOT_AUTHORIZED_OPERATION,
    ED25519_ALGORITHM,
    LegalCorpusOperatorKeyStatus,
    LegalCorpusOperatorTrustRoot,
    LegalCorpusOperatorTrustRootError,
    LegalCorpusOperatorTrustedKey,
    TRUST_ROOT_SCOPE,
)
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    AUTHORITY_SOURCE_VERSION,
    LegalCorpusProvisioningAuthorityEvidence,
    LegalCorpusProvisioningAuthorityScope,
    LegalCorpusProvisioningAuthoritySource,
    LegalCorpusProvisioningOperation,
)
from tools.eos.legal_operations.production_legal_corpus import get_institutional_charter_draft


VERSION: Final[str] = "v1.1.1-R1D-B0F-B4-R8J-JA-LEGAL-CORPUS-OPERATOR-AUTHORIZATION"
SCHEMA: Final[str] = "WILSY-LEGAL-CORPUS-OPERATOR-AUTHORIZATION/V1"
AUTHORITY_SCOPE: Final[str] = TRUST_ROOT_SCOPE
AUTHORIZED_OPERATION: Final[str] = TRUST_ROOT_AUTHORIZED_OPERATION
AUTHORITY_MECHANISM: Final[str] = "WILSY_LEGAL_CORPUS_OPERATOR_AUTHORIZATION"
AUTHORITY_MECHANISM_VERSION: Final[str] = "v1.0.0"
SIGNATURE_ALGORITHM: Final[str] = ED25519_ALGORITHM
# Human-approved NEW LEGAL-CORPUS GOVERNANCE POLICY following R8J-E:
# no clock-skew allowance; the signed authorization window may not exceed
# thirty minutes measured from issued_at. This is not reused from JWT, PRDCA,
# MFA, internal-service trust, or any other subsystem.
MAX_AUTHORIZATION_LIFETIME: Final[timedelta] = timedelta(minutes=30)
R8D_EVIDENCE_ID_PREFIX: Final[str] = "WILSY-R8D-AUTHORITY-EVIDENCE/V1:"
_KEY_ID = re.compile(r"^prdca-key:[a-z0-9][a-z0-9._-]{0,63}$")
_SHA3_HEX = re.compile(r"^[0-9a-f]{128}$")
SIGNATURE_ENCODING: Final[str] = "base64url_without_padding_64_bytes"


class LegalCorpusOperatorAuthorizationError(ValueError):
    """Base fail-closed error with a stable, non-sensitive code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCorpusOperatorAuthorizationShapeError(LegalCorpusOperatorAuthorizationError):
    """Reject malformed primitive envelope or required-field input."""


class LegalCorpusOperatorAuthorizationSchemaError(LegalCorpusOperatorAuthorizationError):
    """Reject an unknown or drifted authorization schema."""


class LegalCorpusOperatorAuthorizationOperationError(LegalCorpusOperatorAuthorizationError):
    """Reject operation, scope, status, mechanism, or authority drift."""


class LegalCorpusOperatorAuthorizationSignatureEncodingError(LegalCorpusOperatorAuthorizationError):
    """Reject non-canonical or malformed Ed25519 signature encoding."""


class LegalCorpusOperatorAuthorizationUnknownKeyError(LegalCorpusOperatorAuthorizationError):
    """Reject a key absent from the source-owned production trust root."""


class LegalCorpusOperatorAuthorizationUntrustedKeyError(LegalCorpusOperatorAuthorizationError):
    """Reject a resolved key that cannot authorize this operation and scope."""


class LegalCorpusOperatorAuthorizationSignatureError(LegalCorpusOperatorAuthorizationError):
    """Reject an Ed25519 signature that does not authenticate the payload."""


class LegalCorpusOperatorAuthorizationNotYetValidError(LegalCorpusOperatorAuthorizationError):
    """Reject an authorization before its signed validity window begins."""


class LegalCorpusOperatorAuthorizationExpiredError(LegalCorpusOperatorAuthorizationError):
    """Reject an authorization after its signed validity window ends."""


class LegalCorpusOperatorAuthorizationKeyValidityError(LegalCorpusOperatorAuthorizationError):
    """Reject an authorization issued outside the trusted key interval."""


class LegalCorpusOperatorAuthorizationCanonicalDocumentError(LegalCorpusOperatorAuthorizationError):
    """Reject a signed claim that does not equal the server-owned Charter."""


class LegalCorpusOperatorAuthorizationDerivationError(LegalCorpusOperatorAuthorizationError):
    """Reject inability to derive frozen R8D evidence after verification."""


class LegalCorpusOperatorAuthorizationOperation(StrEnum):
    """The sole operation this envelope can authorize."""

    DRAFT_ADMISSION = AUTHORIZED_OPERATION


class LegalCorpusOperatorAuthorizationScope(StrEnum):
    """The sole non-tenant scope this envelope can authorize."""

    PLATFORM = AUTHORITY_SCOPE


def _text(value: object, code: str) -> str:
    """Require bounded single-line text without normalizing signed claims."""
    if not isinstance(value, str) or not value or value != value.strip() or "\n" in value or "\r" in value:
        raise LegalCorpusOperatorAuthorizationShapeError(code)
    return value


def _timestamp(value: object, code: str) -> datetime:
    """Require an aware timestamp and normalize it to UTC microseconds."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalCorpusOperatorAuthorizationShapeError(code)
    return value.astimezone(timezone.utc)


def _canonical_timestamp(value: datetime) -> str:
    """Serialize timestamps independently of local timezone or repr()."""
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _signature_bytes(value: object) -> bytes:
    """Decode one canonical unpadded base64url Ed25519 signature."""
    encoded = _text(value, "SIGNATURE_REQUIRED")
    if "=" in encoded:
        raise LegalCorpusOperatorAuthorizationSignatureEncodingError("SIGNATURE_ENCODING_INVALID")
    try:
        decoded = base64.urlsafe_b64decode(encoded + "=" * ((4 - len(encoded) % 4) % 4))
    except (TypeError, ValueError):
        raise LegalCorpusOperatorAuthorizationSignatureEncodingError("SIGNATURE_ENCODING_INVALID") from None
    if len(decoded) != 64 or base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii") != encoded:
        raise LegalCorpusOperatorAuthorizationSignatureEncodingError("SIGNATURE_ENCODING_INVALID")
    return decoded


def _utc_now() -> datetime:
    """Return verifier clock authority; callers cannot supply a clock value."""
    return datetime.now(timezone.utc)


def _r8d_evidence_id(authorization_id: str) -> str:
    """Derive the frozen deterministic R8D evidence identity."""
    return hashlib.sha3_512((R8D_EVIDENCE_ID_PREFIX + authorization_id).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalCorpusOperatorAuthorization:
    """Immutable externally signed authority for one exact Charter draft.

    Construction checks shape and signed semantics only. ``verify`` resolves
    the canonical in-process trust root, authenticates the Ed25519 payload,
    evaluates the exact zero-skew validity window, requires an ACTIVE
    operational key, and binds the claims to the server-owned Charter.
    Successful verification authorizes a new transaction attempt at that
    instant; the caller must verify again for a fresh retry. Expiry after a
    transaction starts and post-attempt readback are outside this pure domain
    boundary. No method signs, consumes, persists, or creates a production key.
    """

    authorization_id: str
    key_id: str
    operation: LegalCorpusOperatorAuthorizationOperation
    scope: LegalCorpusOperatorAuthorizationScope
    source_document_id: str
    source_agreement_type: LegalAgreementType
    source_version: str
    source_status: LegalDocumentStatus
    source_content_reference: str
    source_sha3_512: str
    issued_at: datetime
    not_before: datetime
    expires_at: datetime
    replay_nonce: str
    idempotency_key: str
    authority_mechanism: str
    authority_mechanism_version: str
    signature: str

    def __post_init__(self) -> None:
        """Validate immutable signed-envelope invariants without trust lookup."""
        normalized = {
            "authorization_id": _text(self.authorization_id, "AUTHORIZATION_ID_INVALID"),
            "source_document_id": _text(self.source_document_id, "SOURCE_DOCUMENT_ID_INVALID"),
            "source_version": _text(self.source_version, "SOURCE_VERSION_INVALID"),
            "source_content_reference": _text(self.source_content_reference, "SOURCE_CONTENT_REFERENCE_INVALID"),
            "replay_nonce": _text(self.replay_nonce, "REPLAY_NONCE_REQUIRED"),
            "idempotency_key": _text(self.idempotency_key, "IDEMPOTENCY_KEY_REQUIRED"),
        }
        key_id = _text(self.key_id, "KEY_ID_INVALID")
        if _KEY_ID.fullmatch(key_id) is None:
            raise LegalCorpusOperatorAuthorizationShapeError("KEY_ID_INVALID")
        if not isinstance(self.operation, LegalCorpusOperatorAuthorizationOperation) or self.operation is not LegalCorpusOperatorAuthorizationOperation.DRAFT_ADMISSION:
            raise LegalCorpusOperatorAuthorizationOperationError("AUTHORIZED_OPERATION_INVALID")
        if not isinstance(self.scope, LegalCorpusOperatorAuthorizationScope) or self.scope is not LegalCorpusOperatorAuthorizationScope.PLATFORM:
            raise LegalCorpusOperatorAuthorizationOperationError("AUTHORITY_SCOPE_INVALID")
        if not isinstance(self.source_agreement_type, LegalAgreementType):
            raise LegalCorpusOperatorAuthorizationShapeError("SOURCE_AGREEMENT_TYPE_INVALID")
        if not isinstance(self.source_status, LegalDocumentStatus):
            raise LegalCorpusOperatorAuthorizationShapeError("SOURCE_STATUS_INVALID")
        if self.source_status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            raise LegalCorpusOperatorAuthorizationOperationError("NON_DRAFT_SOURCE_STATUS")
        if self.authority_mechanism != AUTHORITY_MECHANISM:
            raise LegalCorpusOperatorAuthorizationOperationError("AUTHORITY_MECHANISM_INVALID")
        if self.authority_mechanism_version != AUTHORITY_MECHANISM_VERSION:
            raise LegalCorpusOperatorAuthorizationOperationError("AUTHORITY_MECHANISM_VERSION_INVALID")
        digest = _text(self.source_sha3_512, "SOURCE_SHA3_512_INVALID")
        if _SHA3_HEX.fullmatch(digest) is None:
            raise LegalCorpusOperatorAuthorizationShapeError("SOURCE_SHA3_512_INVALID")
        issued_at = _timestamp(self.issued_at, "ISSUED_AT_INVALID")
        not_before = _timestamp(self.not_before, "NOT_BEFORE_INVALID")
        expires_at = _timestamp(self.expires_at, "EXPIRES_AT_INVALID")
        if not_before > expires_at or issued_at < not_before or issued_at > expires_at:
            raise LegalCorpusOperatorAuthorizationOperationError("AUTHORIZATION_VALIDITY_INTERVAL_INVALID")
        if expires_at - issued_at > MAX_AUTHORIZATION_LIFETIME:
            raise LegalCorpusOperatorAuthorizationOperationError("AUTHORIZATION_LIFETIME_EXCEEDED")
        _signature_bytes(self.signature)
        for name, value in normalized.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "key_id", key_id)
        object.__setattr__(self, "source_sha3_512", digest)
        object.__setattr__(self, "issued_at", issued_at)
        object.__setattr__(self, "not_before", not_before)
        object.__setattr__(self, "expires_at", expires_at)

    def canonical_payload(self) -> dict[str, str]:
        """Return the complete deterministic signed semantic payload only."""
        return {
            "authority_mechanism": self.authority_mechanism,
            "authority_mechanism_version": self.authority_mechanism_version,
            "authorization_id": self.authorization_id,
            "expires_at": _canonical_timestamp(self.expires_at),
            "idempotency_key": self.idempotency_key,
            "issued_at": _canonical_timestamp(self.issued_at),
            "key_id": self.key_id,
            "not_before": _canonical_timestamp(self.not_before),
            "operation": self.operation.value,
            "replay_nonce": self.replay_nonce,
            "schema": SCHEMA,
            "scope": self.scope.value,
            "source_agreement_type": self.source_agreement_type.value,
            "source_content_reference": self.source_content_reference,
            "source_document_id": self.source_document_id,
            "source_sha3_512": self.source_sha3_512,
            "source_status": self.source_status.value,
            "source_version": self.source_version,
        }

    def canonical_payload_bytes(self) -> bytes:
        """Return sorted compact UTF-8 JSON bytes; signature is excluded."""
        return json.dumps(self.canonical_payload(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def to_document(self) -> dict[str, str]:
        """Serialize the complete signed envelope without performing I/O."""
        return {**self.canonical_payload(), "signature": self.signature}

    @classmethod
    def from_document(cls, payload: Mapping[str, object]) -> "LegalCorpusOperatorAuthorization":
        """Hydrate exact primitive fields; parsing does not verify trust."""
        expected = {field.name for field in fields(cls)} | {"schema"}
        if not isinstance(payload, Mapping) or set(payload) != expected or payload.get("schema") != SCHEMA:
            raise LegalCorpusOperatorAuthorizationSchemaError("AUTHORIZATION_SCHEMA_INVALID")
        try:
            data = dict(payload)
            data.pop("schema")
            data["operation"] = LegalCorpusOperatorAuthorizationOperation(cast(str, data["operation"]))
            data["scope"] = LegalCorpusOperatorAuthorizationScope(cast(str, data["scope"]))
            data["source_agreement_type"] = LegalAgreementType(cast(str, data["source_agreement_type"]))
            data["source_status"] = LegalDocumentStatus(cast(str, data["source_status"]))
            for name in ("issued_at", "not_before", "expires_at"):
                data[name] = datetime.fromisoformat(cast(str, data[name]))
            return cls(
                authorization_id=cast(str, data["authorization_id"]),
                key_id=cast(str, data["key_id"]),
                operation=cast(LegalCorpusOperatorAuthorizationOperation, data["operation"]),
                scope=cast(LegalCorpusOperatorAuthorizationScope, data["scope"]),
                source_document_id=cast(str, data["source_document_id"]),
                source_agreement_type=cast(LegalAgreementType, data["source_agreement_type"]),
                source_version=cast(str, data["source_version"]),
                source_status=cast(LegalDocumentStatus, data["source_status"]),
                source_content_reference=cast(str, data["source_content_reference"]),
                source_sha3_512=cast(str, data["source_sha3_512"]),
                issued_at=cast(datetime, data["issued_at"]),
                not_before=cast(datetime, data["not_before"]),
                expires_at=cast(datetime, data["expires_at"]),
                replay_nonce=cast(str, data["replay_nonce"]),
                idempotency_key=cast(str, data["idempotency_key"]),
                authority_mechanism=cast(str, data["authority_mechanism"]),
                authority_mechanism_version=cast(str, data["authority_mechanism_version"]),
                signature=cast(str, data["signature"]),
            )
        except LegalCorpusOperatorAuthorizationError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise LegalCorpusOperatorAuthorizationShapeError("AUTHORIZATION_DOCUMENT_INVALID") from error

    def _verify_and_resolve(self) -> tuple[LegalCorpusOperatorTrustedKey, LegalDocumentVersion]:
        """Execute the mandated trust, signature, time, and corpus sequence."""
        try:
            trusted_key = LegalCorpusOperatorTrustRoot.resolve(self.key_id)
        except LegalCorpusOperatorTrustRootError as error:
            if error.code == "UNKNOWN_TRUSTED_KEY":
                raise LegalCorpusOperatorAuthorizationUnknownKeyError(error.code) from None
            raise LegalCorpusOperatorAuthorizationUntrustedKeyError("TRUSTED_KEY_INVALID") from None
        if (
            trusted_key.algorithm != SIGNATURE_ALGORITHM
            or trusted_key.authority_domain != AUTHORITY_DOMAIN
            or trusted_key.scope != AUTHORITY_SCOPE
            or not trusted_key.permits(self.operation.value)
        ):
            raise LegalCorpusOperatorAuthorizationUntrustedKeyError("TRUSTED_KEY_NOT_AUTHORIZED")
        if trusted_key.status is LegalCorpusOperatorKeyStatus.REVOKED:
            raise LegalCorpusOperatorAuthorizationUntrustedKeyError("TRUSTED_KEY_REVOKED")
        if trusted_key.status is not LegalCorpusOperatorKeyStatus.ACTIVE:
            raise LegalCorpusOperatorAuthorizationUntrustedKeyError("TRUSTED_KEY_NOT_OPERATIONALLY_ACTIVE")
        if not trusted_key.can_verify_at(self.operation.value, self.issued_at):
            raise LegalCorpusOperatorAuthorizationKeyValidityError("TRUSTED_KEY_VALIDITY_MISMATCH")
        signature = _signature_bytes(self.signature)
        try:
            trusted_key.public_key().verify(signature, self.canonical_payload_bytes())
        except (InvalidSignature, TypeError, ValueError):
            raise LegalCorpusOperatorAuthorizationSignatureError("SIGNATURE_INVALID") from None
        now = _timestamp(_utc_now(), "VERIFIER_CLOCK_INVALID")
        if now < self.not_before:
            raise LegalCorpusOperatorAuthorizationNotYetValidError("AUTHORIZATION_NOT_YET_VALID")
        if now > self.expires_at:
            raise LegalCorpusOperatorAuthorizationExpiredError("AUTHORIZATION_EXPIRED")
        document = get_institutional_charter_draft()
        if document.status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            raise LegalCorpusOperatorAuthorizationCanonicalDocumentError("NON_DRAFT_CANONICAL_SOURCE")
        bindings = (
            (self.source_document_id, document.document_id),
            (self.source_agreement_type, document.agreement_type),
            (self.source_version, document.version),
            (self.source_status, document.status),
            (self.source_content_reference, document.content_reference),
            (self.source_sha3_512, document.sha3_512),
        )
        if any(expected != actual for expected, actual in bindings):
            raise LegalCorpusOperatorAuthorizationCanonicalDocumentError("CANONICAL_DOCUMENT_MISMATCH")
        return trusted_key, document

    def verify(self) -> LegalCorpusOperatorTrustedKey:
        """Verify trust-root, Ed25519, validity, and canonical Charter binding."""
        trusted_key, _ = self._verify_and_resolve()
        return trusted_key

    def derive_provisioning_authority_evidence(self) -> LegalCorpusProvisioningAuthorityEvidence:
        """Derive frozen R8D evidence only after successful verification."""
        trusted_key, document = self._verify_and_resolve()
        evidence_id = _r8d_evidence_id(self.authorization_id)
        try:
            fingerprint = LegalCorpusProvisioningAuthorityEvidence.fingerprint_for(
                authority_evidence_id=evidence_id,
                scope=LegalCorpusProvisioningAuthorityScope.PLATFORM,
                operation=LegalCorpusProvisioningOperation.DRAFT_ADMISSION,
                source_document_id=document.document_id,
                source_agreement_type=document.agreement_type,
                source_version=document.version,
                source_status=document.status,
                source_content_reference=document.content_reference,
                source_sha3_512=document.sha3_512,
                authority_source_id=LegalCorpusProvisioningAuthoritySource.DEPLOYMENT_OPERATOR,
                authority_source_version=AUTHORITY_SOURCE_VERSION,
                actor_representation=trusted_key.issuer_identity,
                authorized_at=self.issued_at,
                idempotency_key=self.idempotency_key,
            )
            evidence = LegalCorpusProvisioningAuthorityEvidence(
                authority_evidence_id=evidence_id,
                scope=LegalCorpusProvisioningAuthorityScope.PLATFORM,
                operation=LegalCorpusProvisioningOperation.DRAFT_ADMISSION,
                source_document_id=document.document_id,
                source_agreement_type=document.agreement_type,
                source_version=document.version,
                source_status=document.status,
                source_content_reference=document.content_reference,
                source_sha3_512=document.sha3_512,
                authority_source_id=LegalCorpusProvisioningAuthoritySource.DEPLOYMENT_OPERATOR,
                authority_source_version=AUTHORITY_SOURCE_VERSION,
                actor_representation=trusted_key.issuer_identity,
                authorized_at=self.issued_at,
                idempotency_key=self.idempotency_key,
                evidence_fingerprint=fingerprint,
            )
            evidence.verify_against(document)
            return evidence
        except Exception as error:
            if isinstance(error, LegalCorpusOperatorAuthorizationError):
                raise
            raise LegalCorpusOperatorAuthorizationDerivationError("R8D_EVIDENCE_DERIVATION_FAILED") from error


def verify_legal_corpus_operator_authorization(
    authorization: LegalCorpusOperatorAuthorization,
) -> LegalCorpusOperatorTrustedKey:
    """Verify one immutable authorization without accepting caller authority."""
    if not isinstance(authorization, LegalCorpusOperatorAuthorization):
        raise LegalCorpusOperatorAuthorizationShapeError("AUTHORIZATION_VALUE_INVALID")
    return authorization.verify()


def derive_legal_corpus_provisioning_authority_evidence(
    authorization: LegalCorpusOperatorAuthorization,
) -> LegalCorpusProvisioningAuthorityEvidence:
    """Verify then derive deterministic R8D evidence for one authorization."""
    if not isinstance(authorization, LegalCorpusOperatorAuthorization):
        raise LegalCorpusOperatorAuthorizationShapeError("AUTHORIZATION_VALUE_INVALID")
    return authorization.derive_provisioning_authority_evidence()


__all__ = [
    "AUTHORIZED_OPERATION",
    "AUTHORITY_MECHANISM",
    "AUTHORITY_MECHANISM_VERSION",
    "AUTHORITY_SCOPE",
    "LegalCorpusOperatorAuthorization",
    "LegalCorpusOperatorAuthorizationCanonicalDocumentError",
    "LegalCorpusOperatorAuthorizationDerivationError",
    "LegalCorpusOperatorAuthorizationError",
    "LegalCorpusOperatorAuthorizationExpiredError",
    "LegalCorpusOperatorAuthorizationKeyValidityError",
    "LegalCorpusOperatorAuthorizationNotYetValidError",
    "LegalCorpusOperatorAuthorizationOperation",
    "LegalCorpusOperatorAuthorizationOperationError",
    "LegalCorpusOperatorAuthorizationSchemaError",
    "LegalCorpusOperatorAuthorizationScope",
    "LegalCorpusOperatorAuthorizationShapeError",
    "LegalCorpusOperatorAuthorizationSignatureEncodingError",
    "LegalCorpusOperatorAuthorizationSignatureError",
    "LegalCorpusOperatorAuthorizationUnknownKeyError",
    "LegalCorpusOperatorAuthorizationUntrustedKeyError",
    "MAX_AUTHORIZATION_LIFETIME",
    "R8D_EVIDENCE_ID_PREFIX",
    "SCHEMA",
    "SIGNATURE_ENCODING",
    "SIGNATURE_ALGORITHM",
    "VERSION",
    "derive_legal_corpus_provisioning_authority_evidence",
    "verify_legal_corpus_operator_authorization",
]


# ARTIFACT: legal_corpus_operator_authorization.py
# VERSION: v1.1.1-R1D-B0F-B4-R8J-JA-LEGAL-CORPUS-OPERATOR-AUTHORIZATION
# AUTHORITY BOUNDARY: external-signature verification and deterministic R8D derivation only
# TENANT POSTURE: PLATFORM scope; no tenant or principal authority
# FAIL-CLOSED POSTURE: canonical C1 public-key trust, invalid signatures, drift, and expiry reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
