"""Immutable public trust metadata for legal-corpus document approval.

TITLE: WILSY OS Legal Corpus Approval Trust Root Domain
VERSION: v1.2.0-R1D-B0F-R9B-P5-R2-LEGAL-CORPUS-APPROVAL-TRUST-ROOT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Defines the distinct, source-owned Ed25519 public-key trust lineage
         for PLATFORM ``LEGAL_CORPUS_DOCUMENT_APPROVAL``. This value domain
         contains one historical retired predecessor and one active successor
         public key from separately governed R9B-P5 ceremonies.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_corpus_approval_trust_root.py
COLLABORATION / OWNERSHIP: A future signed approval-authorisation verifier
                            consumes this trust root; this module owns only
                            immutable public metadata and lifecycle predicates.
CERTIFICATION / UPDATE DATE: 2026-09-21
CHANGELOG: v1.2.0-R1D-B0F-R9B-P5-R2 retires the expired predecessor by
           lifecycle metadata only, admits exactly one externally governed
           successor public key, and preserves historical verification;
           private key material remains outside this repository.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Public metadata only. No private key, secret,
                            filesystem, network, database, signing, or
                            signature-verification operation is permitted.
TENANT BOUNDARY: PLATFORM scope only; no tenant, principal, or membership
                 authority is represented.
AUTHORITY BOUNDARY: Trust eligibility metadata only; this artifact does not
                    prove a human approval, verify a signature, approve text,
                    persist evidence, or authorize execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Unknown keys, malformed metadata, lifecycle drift,
                     fingerprint mismatch, duplicate membership, and R8
                     authority identities reject without fallback authority.
TRANSACTION BOUNDARY: Pure immutable in-process values; no DB/session/HTTP
                       lifecycle exists here.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Final, Mapping


VERSION: Final[str] = "v1.2.0-R1D-B0F-R9B-P5-R2-LEGAL-CORPUS-APPROVAL-TRUST-ROOT"
APPROVAL_SCOPE: Final[str] = "PLATFORM"
APPROVAL_AUTHORITY_ROLE: Final[str] = "WILSY_OS_LEGAL_CORPUS_APPROVAL_AUTHORITY"
APPROVAL_ISSUER_IDENTITY: Final[str] = "WILSY_OS_LEGAL_CORPUS_APPROVAL_AUTHORITY:V1"
APPROVAL_AUTHORITY_DOMAIN: Final[str] = "WILSY_LEGAL_CORPUS_APPROVAL_AUTHORITY"
APPROVAL_OPERATION: Final[str] = "LEGAL_CORPUS_DOCUMENT_APPROVAL"
APPROVAL_TRUST_ROOT_PROVENANCE: Final[str] = "WILSY_LEGAL_CORPUS_APPROVAL_TRUST_ROOT/V1"
ED25519_ALGORITHM: Final[str] = "Ed25519"
PUBLIC_KEY_ENCODING: Final[str] = "base64url_without_padding_raw_32_bytes"
KEY_ID_PREFIX: Final[str] = "prdca-key:legal-corpus-approval-"

# R9B-P5 public ceremony metadata. These constants intentionally contain no
# private key, signature, filesystem path, or secret-loading logic. The
# predecessor retains its original public identity and validity interval while
# the successor is the sole fresh-issuance key.
_PREDECESSOR_KEY_ID: Final[str] = "prdca-key:legal-corpus-approval-f8bc464615e8047f008909c36750348b"
_PREDECESSOR_PUBLIC_KEY_BASE64URL: Final[str] = "MgzL6fXojmva5bRPonUOdVLOEZFRJHd6gA1kJa1SXGE"
_PREDECESSOR_VALID_FROM: Final[datetime] = datetime(2026, 9, 19, 10, 3, 24, 50717, tzinfo=timezone.utc)
_PREDECESSOR_VALID_UNTIL: Final[datetime] = datetime(2026, 9, 20, 10, 3, 24, 50717, tzinfo=timezone.utc)
_PREDECESSOR_TRUST_FINGERPRINT: Final[str] = "88b2c725e8545c8a88259a74a517266202a99daa0145ed90dbef458e8e41bbdecbd24bc9a777acece7a9a5ebe0c20aa0e77ea210ee4b027c14058a65edcdeaad"
_SUCCESSOR_KEY_ID: Final[str] = "prdca-key:legal-corpus-approval-2084472fec6f273b537255d0b2dff9fb"
_SUCCESSOR_PUBLIC_KEY_BASE64URL: Final[str] = "12o_Ya2-muW1IXlcdIJF_Hu-2Nn3aKdIIqb4DYNcp9Q"
_SUCCESSOR_VALID_FROM: Final[datetime] = datetime(2026, 9, 21, 19, 48, 56, 907799, tzinfo=timezone.utc)
_SUCCESSOR_VALID_UNTIL: Final[datetime] = datetime(2026, 9, 22, 19, 48, 56, 907799, tzinfo=timezone.utc)
_SUCCESSOR_TRUST_FINGERPRINT: Final[str] = "f25151e216e1fadf4728c59583b64e84692685e6b12a0ed85a303e92e6a0039d1914151f9d070e6349083713464e4a753b1bd19a72031c94594385935f390b95"

_KEY_ID = re.compile(r"^prdca-key:legal-corpus-approval-[a-f0-9]{32}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3_HEX = re.compile(r"^[0-9a-f]{128}$")
_BASE64URL = re.compile(r"^[A-Za-z0-9_-]+$")
_MAX_TEXT = 256


class LegalCorpusApprovalTrustRootError(ValueError):
    """Stable, non-sensitive failure for approval trust metadata or lookup."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCorpusApprovalTrustStatus(StrEnum):
    """Closed lifecycle states for one approval public-key trust record."""

    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"


def _text(value: object, code: str, *, pattern: re.Pattern[str] | None = None) -> str:
    """Require bounded, printable, single-line governance metadata."""
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > _MAX_TEXT:
        raise LegalCorpusApprovalTrustRootError(code)
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise LegalCorpusApprovalTrustRootError(code)
    if pattern is not None and pattern.fullmatch(value) is None:
        raise LegalCorpusApprovalTrustRootError(code)
    return value


def _timestamp(value: object, code: str) -> datetime:
    """Require an aware timestamp and normalize it to UTC without clock reads."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalCorpusApprovalTrustRootError(code)
    return value.astimezone(timezone.utc)


def _public_key_bytes(value: object) -> bytes:
    """Validate canonical unpadded base64url encoding of exactly 32 raw bytes."""
    encoded = _text(value, "APPROVAL_TRUST_PUBLIC_KEY_INVALID")
    if "=" in encoded or _BASE64URL.fullmatch(encoded) is None:
        raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_PUBLIC_KEY_INVALID")
    try:
        decoded = base64.urlsafe_b64decode(encoded + "=" * ((4 - len(encoded) % 4) % 4))
    except (TypeError, ValueError):
        raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_PUBLIC_KEY_INVALID") from None
    if len(decoded) != 32 or base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii") != encoded:
        raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_PUBLIC_KEY_INVALID")
    return decoded


def _derived_key_id(public_key_base64url: str) -> str:
    """Derive the approval-specific key namespace from raw public bytes."""
    raw = _public_key_bytes(public_key_base64url)
    return KEY_ID_PREFIX + hashlib.sha3_512(raw).hexdigest()[:32]


def _canonical_timestamp(value: datetime) -> str:
    """Return the stable UTC timestamp used by fingerprints and documents."""
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _semantic_payload(
    *,
    key_id: str,
    issuer_identity: str,
    authority_role: str,
    authority_domain: str,
    algorithm: str,
    public_key_base64url: str,
    valid_from: datetime,
    valid_until: datetime,
    status: LegalCorpusApprovalTrustStatus,
    revision: int,
    permitted_operations: frozenset[str],
    scope: str,
    trust_root_provenance: str,
) -> dict[str, object]:
    """Build all semantic trust fields except the derived fingerprint."""
    return {
        "algorithm": algorithm,
        "authority_domain": authority_domain,
        "authority_role": authority_role,
        "issuer_identity": issuer_identity,
        "key_id": key_id,
        "permitted_operations": sorted(permitted_operations),
        "public_key_base64url": public_key_base64url,
        "revision": revision,
        "scope": scope,
        "status": status.value,
        "trust_root_provenance": trust_root_provenance,
        "valid_from": _canonical_timestamp(valid_from),
        "valid_until": _canonical_timestamp(valid_until),
    }


def _fingerprint(payload: Mapping[str, object]) -> str:
    """Compute deterministic lowercase SHA3-512 over canonical JSON bytes."""
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalCorpusApprovalTrustedKey:
    """Immutable public metadata for one approval trust key.

    This record is trust-root data, not a signature, authorization envelope, or
    proof that a human approved a document. Lifecycle changes require a new
    source-owned record with a higher revision.
    """

    key_id: str
    issuer_identity: str
    authority_role: str
    authority_domain: str
    algorithm: str
    public_key_base64url: str
    valid_from: datetime
    valid_until: datetime
    status: LegalCorpusApprovalTrustStatus
    revision: int
    permitted_operations: frozenset[str]
    scope: str
    trust_root_provenance: str
    trust_fingerprint: str

    def __post_init__(self) -> None:
        """Validate and normalize the complete immutable trust record."""
        issuer = _text(self.issuer_identity, "APPROVAL_TRUST_ISSUER_INVALID", pattern=_IDENTITY)
        role = _text(self.authority_role, "APPROVAL_TRUST_ROLE_INVALID", pattern=_IDENTITY)
        domain = _text(self.authority_domain, "APPROVAL_TRUST_DOMAIN_INVALID")
        scope = _text(self.scope, "APPROVAL_TRUST_SCOPE_INVALID")
        provenance = _text(self.trust_root_provenance, "APPROVAL_TRUST_PROVENANCE_INVALID")
        _text(self.key_id, "APPROVAL_TRUST_KEY_ID_INVALID", pattern=_KEY_ID)
        _public_key_bytes(self.public_key_base64url)
        derived = _derived_key_id(self.public_key_base64url)
        if self.key_id != derived:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_KEY_ID_INVALID")
        if issuer != APPROVAL_ISSUER_IDENTITY:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_ISSUER_INVALID")
        if role != APPROVAL_AUTHORITY_ROLE:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_ROLE_INVALID")
        if domain != APPROVAL_AUTHORITY_DOMAIN:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_DOMAIN_INVALID")
        if self.algorithm != ED25519_ALGORITHM:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_ALGORITHM_INVALID")
        if scope != APPROVAL_SCOPE:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_SCOPE_INVALID")
        if provenance != APPROVAL_TRUST_ROOT_PROVENANCE:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_PROVENANCE_INVALID")
        if not isinstance(self.permitted_operations, frozenset) or self.permitted_operations != frozenset({APPROVAL_OPERATION}):
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_OPERATION_INVALID")
        if not isinstance(self.status, LegalCorpusApprovalTrustStatus):
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_STATUS_INVALID")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_REVISION_INVALID")
        valid_from = _timestamp(self.valid_from, "APPROVAL_TRUST_VALIDITY_INVALID")
        valid_until = _timestamp(self.valid_until, "APPROVAL_TRUST_VALIDITY_INVALID")
        if valid_from >= valid_until:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_VALIDITY_INVALID")
        if not isinstance(self.trust_fingerprint, str) or _SHA3_HEX.fullmatch(self.trust_fingerprint) is None:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_FINGERPRINT_INVALID")
        object.__setattr__(self, "issuer_identity", issuer)
        object.__setattr__(self, "authority_role", role)
        object.__setattr__(self, "authority_domain", domain)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "trust_root_provenance", provenance)
        object.__setattr__(self, "valid_from", valid_from)
        object.__setattr__(self, "valid_until", valid_until)
        expected = self.fingerprint_for(
            key_id=self.key_id,
            issuer_identity=issuer,
            authority_role=role,
            authority_domain=domain,
            algorithm=self.algorithm,
            public_key_base64url=self.public_key_base64url,
            valid_from=valid_from,
            valid_until=valid_until,
            status=self.status,
            revision=self.revision,
            permitted_operations=self.permitted_operations,
            scope=scope,
            trust_root_provenance=provenance,
        )
        if expected != self.trust_fingerprint:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_FINGERPRINT_MISMATCH")

    @staticmethod
    def derive_key_id(public_key_base64url: str) -> str:
        """Return the approval-specific deterministic key ID for raw public bytes."""
        return _derived_key_id(public_key_base64url)

    @staticmethod
    def fingerprint_for(
        *,
        key_id: str,
        issuer_identity: str,
        authority_role: str,
        authority_domain: str,
        algorithm: str,
        public_key_base64url: str,
        valid_from: datetime,
        valid_until: datetime,
        status: LegalCorpusApprovalTrustStatus,
        revision: int,
        permitted_operations: frozenset[str],
        scope: str,
        trust_root_provenance: str,
    ) -> str:
        """Compute integrity evidence without issuing or authorizing anything."""
        normalized_key_id = _text(key_id, "APPROVAL_TRUST_KEY_ID_INVALID", pattern=_KEY_ID)
        normalized_issuer = _text(issuer_identity, "APPROVAL_TRUST_ISSUER_INVALID", pattern=_IDENTITY)
        normalized_role = _text(authority_role, "APPROVAL_TRUST_ROLE_INVALID", pattern=_IDENTITY)
        normalized_domain = _text(authority_domain, "APPROVAL_TRUST_DOMAIN_INVALID")
        normalized_scope = _text(scope, "APPROVAL_TRUST_SCOPE_INVALID")
        normalized_provenance = _text(trust_root_provenance, "APPROVAL_TRUST_PROVENANCE_INVALID")
        _public_key_bytes(public_key_base64url)
        if normalized_key_id != _derived_key_id(public_key_base64url):
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_KEY_ID_INVALID")
        if normalized_issuer != APPROVAL_ISSUER_IDENTITY:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_ISSUER_INVALID")
        if normalized_role != APPROVAL_AUTHORITY_ROLE:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_ROLE_INVALID")
        if normalized_domain != APPROVAL_AUTHORITY_DOMAIN:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_DOMAIN_INVALID")
        if algorithm != ED25519_ALGORITHM:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_ALGORITHM_INVALID")
        if normalized_scope != APPROVAL_SCOPE:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_SCOPE_INVALID")
        if normalized_provenance != APPROVAL_TRUST_ROOT_PROVENANCE:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_PROVENANCE_INVALID")
        if not isinstance(permitted_operations, frozenset) or permitted_operations != frozenset({APPROVAL_OPERATION}):
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_OPERATION_INVALID")
        if not isinstance(status, LegalCorpusApprovalTrustStatus):
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_STATUS_INVALID")
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_REVISION_INVALID")
        normalized_from = _timestamp(valid_from, "APPROVAL_TRUST_VALIDITY_INVALID")
        normalized_until = _timestamp(valid_until, "APPROVAL_TRUST_VALIDITY_INVALID")
        if normalized_from >= normalized_until:
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_VALIDITY_INVALID")
        return _fingerprint(_semantic_payload(
            key_id=normalized_key_id,
            issuer_identity=normalized_issuer,
            authority_role=normalized_role,
            authority_domain=normalized_domain,
            algorithm=algorithm,
            public_key_base64url=public_key_base64url,
            valid_from=normalized_from,
            valid_until=normalized_until,
            status=status,
            revision=revision,
            permitted_operations=permitted_operations,
            scope=normalized_scope,
            trust_root_provenance=normalized_provenance,
        ))

    def permits(self, operation: str, scope: str) -> bool:
        """Return whether this key permits exactly the requested operation/scope."""
        return operation in self.permitted_operations and scope == self.scope

    def is_valid_at(self, at: datetime) -> bool:
        """Return whether an aware instant is inside ``[valid_from, valid_until)``."""
        evaluation = _timestamp(at, "APPROVAL_TRUST_VALIDITY_INVALID")
        return self.valid_from <= evaluation < self.valid_until

    def can_issue(self, operation: str, scope: str, at: datetime) -> bool:
        """Return fresh-issuance eligibility, never human authorization."""
        return self.status is LegalCorpusApprovalTrustStatus.ACTIVE and self.permits(operation, scope) and self.is_valid_at(at)

    def can_verify_at(self, operation: str, scope: str, at: datetime) -> bool:
        """Return historical trust eligibility, not cryptographic verification."""
        return self.status is not LegalCorpusApprovalTrustStatus.REVOKED and self.permits(operation, scope) and self.is_valid_at(at)

    def to_document(self) -> dict[str, object]:
        """Return stable primitive serialization for a future verifier/registry."""
        return {
            "key_id": self.key_id,
            "issuer_identity": self.issuer_identity,
            "authority_role": self.authority_role,
            "authority_domain": self.authority_domain,
            "algorithm": self.algorithm,
            "public_key_base64url": self.public_key_base64url,
            "valid_from": _canonical_timestamp(self.valid_from),
            "valid_until": _canonical_timestamp(self.valid_until),
            "status": self.status.value,
            "revision": self.revision,
            "permitted_operations": sorted(self.permitted_operations),
            "scope": self.scope,
            "trust_root_provenance": self.trust_root_provenance,
            "trust_fingerprint": self.trust_fingerprint,
        }


@dataclass(frozen=True, slots=True)
class LegalCorpusApprovalTrustRoot:
    """Immutable source-owned membership of approval trusted public keys."""

    trusted_keys: tuple[LegalCorpusApprovalTrustedKey, ...] = ()

    def __post_init__(self) -> None:
        """Freeze membership and reject duplicate or foreign key records."""
        if not isinstance(self.trusted_keys, tuple) or not all(isinstance(key, LegalCorpusApprovalTrustedKey) for key in self.trusted_keys):
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_MEMBERSHIP_INVALID")
        ids = [key.key_id for key in self.trusted_keys]
        if len(ids) != len(set(ids)):
            raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_DUPLICATE_KEY")

    def resolve(self, key_id: str) -> LegalCorpusApprovalTrustedKey:
        """Return one exact key or fail closed for unknown/invalid identifiers."""
        normalized = _text(key_id, "APPROVAL_TRUST_KEY_ID_INVALID", pattern=_KEY_ID)
        for key in self.trusted_keys:
            if key.key_id == normalized:
                return key
        raise LegalCorpusApprovalTrustRootError("APPROVAL_TRUST_KEY_UNKNOWN")

    def all_keys(self) -> tuple[LegalCorpusApprovalTrustedKey, ...]:
        """Return the immutable membership snapshot."""
        return self.trusted_keys

    def production_key_count(self) -> int:
        """Return source-owned membership count without creating keys."""
        return len(self.trusted_keys)


_PRODUCTION_APPROVAL_PREDECESSOR: Final[LegalCorpusApprovalTrustedKey] = LegalCorpusApprovalTrustedKey(
    key_id=_PREDECESSOR_KEY_ID,
    issuer_identity=APPROVAL_ISSUER_IDENTITY,
    authority_role=APPROVAL_AUTHORITY_ROLE,
    authority_domain=APPROVAL_AUTHORITY_DOMAIN,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_PREDECESSOR_PUBLIC_KEY_BASE64URL,
    valid_from=_PREDECESSOR_VALID_FROM,
    valid_until=_PREDECESSOR_VALID_UNTIL,
    status=LegalCorpusApprovalTrustStatus.RETIRED,
    revision=2,
    permitted_operations=frozenset({APPROVAL_OPERATION}),
    scope=APPROVAL_SCOPE,
    trust_root_provenance=APPROVAL_TRUST_ROOT_PROVENANCE,
    trust_fingerprint=_PREDECESSOR_TRUST_FINGERPRINT,
)

_PRODUCTION_APPROVAL_SUCCESSOR: Final[LegalCorpusApprovalTrustedKey] = LegalCorpusApprovalTrustedKey(
    key_id=_SUCCESSOR_KEY_ID,
    issuer_identity=APPROVAL_ISSUER_IDENTITY,
    authority_role=APPROVAL_AUTHORITY_ROLE,
    authority_domain=APPROVAL_AUTHORITY_DOMAIN,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_SUCCESSOR_PUBLIC_KEY_BASE64URL,
    valid_from=_SUCCESSOR_VALID_FROM,
    valid_until=_SUCCESSOR_VALID_UNTIL,
    status=LegalCorpusApprovalTrustStatus.ACTIVE,
    revision=1,
    permitted_operations=frozenset({APPROVAL_OPERATION}),
    scope=APPROVAL_SCOPE,
    trust_root_provenance=APPROVAL_TRUST_ROOT_PROVENANCE,
    trust_fingerprint=_SUCCESSOR_TRUST_FINGERPRINT,
)

PRODUCTION_APPROVAL_TRUSTED_KEYS: Final[tuple[LegalCorpusApprovalTrustedKey, ...]] = (
    _PRODUCTION_APPROVAL_PREDECESSOR,
    _PRODUCTION_APPROVAL_SUCCESSOR,
)
PRODUCTION_APPROVAL_TRUST_ROOT: Final[LegalCorpusApprovalTrustRoot] = LegalCorpusApprovalTrustRoot(
    trusted_keys=PRODUCTION_APPROVAL_TRUSTED_KEYS
)

__all__ = [
    "APPROVAL_AUTHORITY_DOMAIN",
    "APPROVAL_AUTHORITY_ROLE",
    "APPROVAL_ISSUER_IDENTITY",
    "APPROVAL_OPERATION",
    "APPROVAL_SCOPE",
    "APPROVAL_TRUST_ROOT_PROVENANCE",
    "ED25519_ALGORITHM",
    "KEY_ID_PREFIX",
    "LegalCorpusApprovalTrustRoot",
    "LegalCorpusApprovalTrustRootError",
    "LegalCorpusApprovalTrustStatus",
    "LegalCorpusApprovalTrustedKey",
    "PRODUCTION_APPROVAL_TRUSTED_KEYS",
    "PRODUCTION_APPROVAL_TRUST_ROOT",
    "PUBLIC_KEY_ENCODING",
    "VERSION",
]


# ARTIFACT: legal_corpus_approval_trust_root.py
# VERSION: v1.2.0-R1D-B0F-R9B-P5-R2-LEGAL-CORPUS-APPROVAL-TRUST-ROOT
# AUTHORITY BOUNDARY: immutable PLATFORM approval public-key trust metadata only
# TENANT POSTURE: no tenant, principal, or membership authority
# FAIL-CLOSED POSTURE: invalid metadata, revoked keys, duplicates, and unknown keys reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
