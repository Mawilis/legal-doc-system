"""Platform public-key trust root for legal-corpus admission authorization.

TITLE: WILSY OS Legal Corpus Operator Public Trust Root
VERSION: v1.8.0-R9B-P7-A3-H7-POST-PROVISIONING-SUCCESSOR-KEY-RETIREMENT-TRUST-ROOT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Defines the immutable, source-owned Ed25519 public-key records for the
         ``LEGAL_CORPUS_DRAFT_ADMISSION`` authorization verifier. Four
         historical records remain RETIRED after the governed Charter admission;
         private signing material remains outside this repository and is neither
         accessed nor represented.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_corpus_operator_trust_root.py
COLLABORATION / OWNERSHIP: The signed-authorization verifier consumes this
                           source-owned trust root; an external release or
                           offline signing authority retains private keys. No
                           command, registry, or service may replace this root.
CERTIFICATION / UPDATE DATE: 2026-09-21
CHANGELOG: v1.8.0-R9B-P7-A3-H7-POST-PROVISIONING-SUCCESSOR-KEY-RETIREMENT
           retires the exact successor public record at revision 2 after the
           governed Charter admission, preserving every public identity and
           validity field; no private-key access, signing, authorization
           issuance, or Mongo operation is performed by this source revision.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Public-key material and opaque issuer metadata only;
                            no private key, secret, key-file, network, Mongo,
                            environment, or request-context access.
TENANT BOUNDARY: PLATFORM scope only; no tenant, principal, membership, or
                 user authority is represented.
AUTHORITY BOUNDARY: Immutable public trust-root verification material only;
                    this artifact does not authenticate a shell user, hold
                    private signing material, sign, issue authorization, verify
                    a full envelope, or admit a legal document. Retirement is
                    lifecycle evidence only; no record is fresh issuance
                    authority in this source revision.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED DECLARATION: Unknown keys, malformed public keys, invalid
                          lifecycle records, fingerprint drift, expired
                          records, and RETIRED-key issuance attempts reject
                          without fallback authority. H3/H4 execution/archive
                          history remains external forensic evidence; physical
                          private-key erasure is not asserted.
"""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from types import MappingProxyType
from typing import Final, Mapping

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


VERSION: Final[str] = "v1.8.0-R9B-P7-A3-H7-POST-PROVISIONING-SUCCESSOR-KEY-RETIREMENT-TRUST-ROOT"
TRUST_ROOT_SCOPE: Final[str] = "PLATFORM"
AUTHORITY_DOMAIN: Final[str] = "WILSY_LEGAL_CORPUS_OPERATOR_AUTHORITY"
AUTHORIZED_OPERATION: Final[str] = "LEGAL_CORPUS_DRAFT_ADMISSION"
TRUST_ROOT_PROVENANCE: Final[str] = "WILSY_LEGAL_CORPUS_OPERATOR_TRUST_ROOT/V1"
ED25519_ALGORITHM: Final[str] = "Ed25519"
PUBLIC_KEY_ENCODING: Final[str] = "base64url_without_padding_raw_32_bytes"
_KEY_ID = re.compile(r"^prdca-key:[a-z0-9][a-z0-9._-]{0,63}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3_HEX = re.compile(r"^[0-9a-f]{128}$")


class LegalCorpusOperatorTrustRootError(ValueError):
    """Stable, non-sensitive failure for trust-root record or lookup input."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCorpusOperatorKeyStatus(StrEnum):
    """Immutable lifecycle states for one trusted public key."""

    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"


def _text(value: object, code: str, *, pattern: re.Pattern[str] | None = None) -> str:
    """Require bounded single-line text and optionally a canonical pattern."""
    if not isinstance(value, str) or not value or value != value.strip() or "\n" in value or "\r" in value:
        raise LegalCorpusOperatorTrustRootError(code)
    if pattern is not None and pattern.fullmatch(value) is None:
        raise LegalCorpusOperatorTrustRootError(code)
    return value


def _timestamp(value: object, code: str) -> datetime:
    """Require an aware timestamp and normalize it to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalCorpusOperatorTrustRootError(code)
    return value.astimezone(timezone.utc)


def _public_key_bytes(value: object) -> bytes:
    """Validate canonical raw Ed25519 public-key bytes encoded as base64url."""
    encoded = _text(value, "PUBLIC_KEY_ENCODING_INVALID")
    if "=" in encoded:
        raise LegalCorpusOperatorTrustRootError("PUBLIC_KEY_ENCODING_INVALID")
    try:
        decoded = urlsafe_b64decode(encoded + "=" * ((4 - len(encoded) % 4) % 4))
    except (TypeError, ValueError):
        raise LegalCorpusOperatorTrustRootError("PUBLIC_KEY_ENCODING_INVALID") from None
    if len(decoded) != 32 or urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii") != encoded:
        raise LegalCorpusOperatorTrustRootError("PUBLIC_KEY_ENCODING_INVALID")
    try:
        Ed25519PublicKey.from_public_bytes(decoded)
    except (TypeError, ValueError):
        raise LegalCorpusOperatorTrustRootError("PUBLIC_KEY_ENCODING_INVALID") from None
    return decoded


def _canonical_timestamp(value: datetime) -> str:
    """Return the repository-stable UTC timestamp representation."""
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _semantic_payload(
    *,
    key_id: str,
    algorithm: str,
    public_key_base64url: str,
    issuer_identity: str,
    authority_domain: str,
    scope: str,
    permitted_operations: frozenset[str],
    valid_from: datetime,
    valid_until: datetime | None,
    status: LegalCorpusOperatorKeyStatus,
    revision: int,
    trust_root_provenance: str,
) -> dict[str, object]:
    """Build every trust-bearing field except the derived fingerprint."""
    return {
        "algorithm": algorithm,
        "authority_domain": authority_domain,
        "issuer_identity": issuer_identity,
        "key_id": key_id,
        "permitted_operations": sorted(permitted_operations),
        "public_key_base64url": public_key_base64url,
        "revision": revision,
        "scope": scope,
        "status": status.value,
        "trust_root_provenance": trust_root_provenance,
        "valid_from": _canonical_timestamp(valid_from),
        "valid_until": None if valid_until is None else _canonical_timestamp(valid_until),
    }


def _fingerprint(payload: Mapping[str, object]) -> str:
    """Compute deterministic SHA3-512 integrity over canonical JSON bytes."""
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalCorpusOperatorTrustedKey:
    """Immutable public trust record for one least-privilege platform key.

    The value contains no private material and cannot transition lifecycle state
    in memory. A later governed source revision represents rotation, retirement,
    or revocation. Constructing a record is integrity validation, not signing or
    authorization issuance.
    """

    key_id: str
    algorithm: str
    public_key_base64url: str
    issuer_identity: str
    authority_domain: str
    scope: str
    permitted_operations: frozenset[str]
    valid_from: datetime
    valid_until: datetime | None
    status: LegalCorpusOperatorKeyStatus
    revision: int
    trust_root_provenance: str
    fingerprint: str

    def __post_init__(self) -> None:
        """Validate and normalize the complete immutable record."""
        key_id = _text(self.key_id, "KEY_ID_INVALID", pattern=_KEY_ID)
        issuer = _text(self.issuer_identity, "ISSUER_IDENTITY_REQUIRED", pattern=_IDENTITY)
        authority_domain = _text(self.authority_domain, "AUTHORITY_DOMAIN_INVALID")
        scope = _text(self.scope, "TRUST_ROOT_SCOPE_INVALID")
        provenance = _text(self.trust_root_provenance, "TRUST_ROOT_PROVENANCE_INVALID")
        _public_key_bytes(self.public_key_base64url)
        if self.algorithm != ED25519_ALGORITHM:
            raise LegalCorpusOperatorTrustRootError("ED25519_ALGORITHM_REQUIRED")
        if authority_domain != AUTHORITY_DOMAIN:
            raise LegalCorpusOperatorTrustRootError("AUTHORITY_DOMAIN_INVALID")
        if scope != TRUST_ROOT_SCOPE:
            raise LegalCorpusOperatorTrustRootError("TRUST_ROOT_SCOPE_INVALID")
        if provenance != TRUST_ROOT_PROVENANCE:
            raise LegalCorpusOperatorTrustRootError("TRUST_ROOT_PROVENANCE_INVALID")
        if not isinstance(self.permitted_operations, frozenset) or self.permitted_operations != frozenset({AUTHORIZED_OPERATION}):
            raise LegalCorpusOperatorTrustRootError("PERMITTED_OPERATION_INVALID")
        if not all(isinstance(operation, str) for operation in self.permitted_operations):
            raise LegalCorpusOperatorTrustRootError("PERMITTED_OPERATION_INVALID")
        if not isinstance(self.status, LegalCorpusOperatorKeyStatus):
            raise LegalCorpusOperatorTrustRootError("KEY_STATUS_INVALID")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise LegalCorpusOperatorTrustRootError("KEY_REVISION_INVALID")
        valid_from = _timestamp(self.valid_from, "VALID_FROM_INVALID")
        valid_until = None if self.valid_until is None else _timestamp(self.valid_until, "VALID_UNTIL_INVALID")
        if valid_until is not None and valid_until <= valid_from:
            raise LegalCorpusOperatorTrustRootError("KEY_VALIDITY_INTERVAL_INVALID")
        if not isinstance(self.fingerprint, str) or _SHA3_HEX.fullmatch(self.fingerprint) is None:
            raise LegalCorpusOperatorTrustRootError("TRUSTED_KEY_FINGERPRINT_INVALID")
        object.__setattr__(self, "key_id", key_id)
        object.__setattr__(self, "issuer_identity", issuer)
        object.__setattr__(self, "authority_domain", authority_domain)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "trust_root_provenance", provenance)
        object.__setattr__(self, "valid_from", valid_from)
        object.__setattr__(self, "valid_until", valid_until)
        expected = self.fingerprint_for(
            key_id=key_id,
            algorithm=self.algorithm,
            public_key_base64url=self.public_key_base64url,
            issuer_identity=issuer,
            authority_domain=authority_domain,
            scope=scope,
            permitted_operations=self.permitted_operations,
            valid_from=valid_from,
            valid_until=valid_until,
            status=self.status,
            revision=self.revision,
            trust_root_provenance=provenance,
        )
        if expected != self.fingerprint:
            raise LegalCorpusOperatorTrustRootError("TRUSTED_KEY_FINGERPRINT_MISMATCH")

    @staticmethod
    def fingerprint_for(
        *,
        key_id: str,
        algorithm: str,
        public_key_base64url: str,
        issuer_identity: str,
        authority_domain: str,
        scope: str,
        permitted_operations: frozenset[str],
        valid_from: datetime,
        valid_until: datetime | None,
        status: LegalCorpusOperatorKeyStatus,
        revision: int,
        trust_root_provenance: str,
    ) -> str:
        """Compute integrity evidence without issuing or authorizing anything."""
        normalized_key_id = _text(key_id, "KEY_ID_INVALID", pattern=_KEY_ID)
        normalized_issuer = _text(issuer_identity, "ISSUER_IDENTITY_REQUIRED", pattern=_IDENTITY)
        normalized_domain = _text(authority_domain, "AUTHORITY_DOMAIN_INVALID")
        normalized_scope = _text(scope, "TRUST_ROOT_SCOPE_INVALID")
        normalized_provenance = _text(trust_root_provenance, "TRUST_ROOT_PROVENANCE_INVALID")
        _public_key_bytes(public_key_base64url)
        if algorithm != ED25519_ALGORITHM:
            raise LegalCorpusOperatorTrustRootError("ED25519_ALGORITHM_REQUIRED")
        if normalized_domain != AUTHORITY_DOMAIN:
            raise LegalCorpusOperatorTrustRootError("AUTHORITY_DOMAIN_INVALID")
        if normalized_scope != TRUST_ROOT_SCOPE:
            raise LegalCorpusOperatorTrustRootError("TRUST_ROOT_SCOPE_INVALID")
        if normalized_provenance != TRUST_ROOT_PROVENANCE:
            raise LegalCorpusOperatorTrustRootError("TRUST_ROOT_PROVENANCE_INVALID")
        if not isinstance(permitted_operations, frozenset) or permitted_operations != frozenset({AUTHORIZED_OPERATION}):
            raise LegalCorpusOperatorTrustRootError("PERMITTED_OPERATION_INVALID")
        if not isinstance(status, LegalCorpusOperatorKeyStatus):
            raise LegalCorpusOperatorTrustRootError("KEY_STATUS_INVALID")
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise LegalCorpusOperatorTrustRootError("KEY_REVISION_INVALID")
        normalized_from = _timestamp(valid_from, "VALID_FROM_INVALID")
        normalized_until = None if valid_until is None else _timestamp(valid_until, "VALID_UNTIL_INVALID")
        if normalized_until is not None and normalized_until <= normalized_from:
            raise LegalCorpusOperatorTrustRootError("KEY_VALIDITY_INTERVAL_INVALID")
        return _fingerprint(
            _semantic_payload(
                key_id=normalized_key_id,
                algorithm=algorithm,
                public_key_base64url=public_key_base64url,
                issuer_identity=normalized_issuer,
                authority_domain=normalized_domain,
                scope=normalized_scope,
                permitted_operations=permitted_operations,
                valid_from=normalized_from,
                valid_until=normalized_until,
                status=status,
                revision=revision,
                trust_root_provenance=normalized_provenance,
            )
        )

    def public_key(self) -> Ed25519PublicKey:
        """Return the canonical public key; no private-key API exists here."""
        return Ed25519PublicKey.from_public_bytes(_public_key_bytes(self.public_key_base64url))

    def permits(self, operation: str) -> bool:
        """Return whether this record grants the one supported operation."""
        return operation in self.permitted_operations

    def is_valid_at(self, at: datetime) -> bool:
        """Evaluate only this key's validity interval at an aware timestamp."""
        evaluation = _timestamp(at, "EVALUATION_TIMESTAMP_INVALID")
        return self.valid_from <= evaluation and (self.valid_until is None or evaluation < self.valid_until)

    def can_verify_at(self, operation: str, at: datetime) -> bool:
        """Permit cryptographic lookup except for revoked keys.

        Signed-authorization validity-window and retirement-at-issuance rules
        remain the responsibility of the later authorization verifier.
        """
        return self.status is not LegalCorpusOperatorKeyStatus.REVOKED and self.permits(operation) and self.is_valid_at(at)

    def can_issue(self, operation: str, at: datetime) -> bool:
        """Indicate whether a later issuer may use this key for new authority."""
        return self.status is LegalCorpusOperatorKeyStatus.ACTIVE and self.permits(operation) and self.is_valid_at(at)

    def to_document(self) -> dict[str, object]:
        """Return deterministic primitive serialization for future certificates."""
        return {
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "public_key_base64url": self.public_key_base64url,
            "issuer_identity": self.issuer_identity,
            "authority_domain": self.authority_domain,
            "scope": self.scope,
            "permitted_operations": sorted(self.permitted_operations),
            "valid_from": _canonical_timestamp(self.valid_from),
            "valid_until": None if self.valid_until is None else _canonical_timestamp(self.valid_until),
            "status": self.status.value,
            "revision": self.revision,
            "trust_root_provenance": self.trust_root_provenance,
            "fingerprint": self.fingerprint,
        }


# R8O-P4-R7, R9B-P7-A2-H5, R9B-P7-A3-H4, and R9B-P7-A3-H7 preserve four
# RETIRED public records after the governed Charter admission; private signing
# material and authorization issuance remain outside this source artifact.
_FIRST_KEY_ID: Final[str] = "prdca-key:legal-corpus-69c7c3e9a67c7e552057d4c0670623be"
_FIRST_PUBLIC_KEY_BASE64URL: Final[str] = "jfG0IANHA_tSNyjyurpBtTId98fG2l_LhifnfQJ2cXg"
_FIRST_ISSUER_IDENTITY: Final[str] = "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY:V1"
_FIRST_VALID_FROM: Final[datetime] = datetime(2026, 9, 18, 5, 32, 16, tzinfo=timezone.utc)
_FIRST_VALID_UNTIL: Final[datetime] = datetime(2026, 9, 19, 5, 32, 16, tzinfo=timezone.utc)
_FIRST_KEY_FINGERPRINT: Final[str] = LegalCorpusOperatorTrustedKey.fingerprint_for(
    key_id=_FIRST_KEY_ID,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_FIRST_PUBLIC_KEY_BASE64URL,
    issuer_identity=_FIRST_ISSUER_IDENTITY,
    authority_domain=AUTHORITY_DOMAIN,
    scope=TRUST_ROOT_SCOPE,
    permitted_operations=frozenset({AUTHORIZED_OPERATION}),
    valid_from=_FIRST_VALID_FROM,
    valid_until=_FIRST_VALID_UNTIL,
    status=LegalCorpusOperatorKeyStatus.RETIRED,
    revision=2,
    trust_root_provenance=TRUST_ROOT_PROVENANCE,
)
_FIRST_TRUSTED_KEY: Final[LegalCorpusOperatorTrustedKey] = LegalCorpusOperatorTrustedKey(
    key_id=_FIRST_KEY_ID,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_FIRST_PUBLIC_KEY_BASE64URL,
    issuer_identity=_FIRST_ISSUER_IDENTITY,
    authority_domain=AUTHORITY_DOMAIN,
    scope=TRUST_ROOT_SCOPE,
    permitted_operations=frozenset({AUTHORIZED_OPERATION}),
    valid_from=_FIRST_VALID_FROM,
    valid_until=_FIRST_VALID_UNTIL,
    status=LegalCorpusOperatorKeyStatus.RETIRED,
    revision=2,
    trust_root_provenance=TRUST_ROOT_PROVENANCE,
    fingerprint=_FIRST_KEY_FINGERPRINT,
)
_SECOND_KEY_ID: Final[str] = "prdca-key:legal-corpus-159cfa91f279b045407396cd3ec8dca2"
_SECOND_PUBLIC_KEY_BASE64URL: Final[str] = "vlN3rieZr9YwuvQ6AwW_dD1aN06B2MLGqlFsxacgCpM"
_SECOND_ISSUER_IDENTITY: Final[str] = "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY:V1"
_SECOND_VALID_FROM: Final[datetime] = datetime(2026, 9, 19, 19, 33, 13, 213194, tzinfo=timezone.utc)
_SECOND_VALID_UNTIL: Final[datetime] = datetime(2026, 9, 20, 19, 33, 13, 213194, tzinfo=timezone.utc)
_SECOND_KEY_FINGERPRINT: Final[str] = LegalCorpusOperatorTrustedKey.fingerprint_for(
    key_id=_SECOND_KEY_ID,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_SECOND_PUBLIC_KEY_BASE64URL,
    issuer_identity=_SECOND_ISSUER_IDENTITY,
    authority_domain=AUTHORITY_DOMAIN,
    scope=TRUST_ROOT_SCOPE,
    permitted_operations=frozenset({AUTHORIZED_OPERATION}),
    valid_from=_SECOND_VALID_FROM,
    valid_until=_SECOND_VALID_UNTIL,
    status=LegalCorpusOperatorKeyStatus.RETIRED,
    revision=2,
    trust_root_provenance=TRUST_ROOT_PROVENANCE,
)
_SECOND_TRUSTED_KEY: Final[LegalCorpusOperatorTrustedKey] = LegalCorpusOperatorTrustedKey(
    key_id=_SECOND_KEY_ID,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_SECOND_PUBLIC_KEY_BASE64URL,
    issuer_identity=_SECOND_ISSUER_IDENTITY,
    authority_domain=AUTHORITY_DOMAIN,
    scope=TRUST_ROOT_SCOPE,
    permitted_operations=frozenset({AUTHORIZED_OPERATION}),
    valid_from=_SECOND_VALID_FROM,
    valid_until=_SECOND_VALID_UNTIL,
    status=LegalCorpusOperatorKeyStatus.RETIRED,
    revision=2,
    trust_root_provenance=TRUST_ROOT_PROVENANCE,
    fingerprint=_SECOND_KEY_FINGERPRINT,
)
_THIRD_KEY_ID: Final[str] = "prdca-key:legal-corpus-a5c22bcb6438d139981f7aec1465f695"
_THIRD_PUBLIC_KEY_BASE64URL: Final[str] = "nocEKzPIR01HXRV0BIxxsGaj0JmZaN75CUbaQS-lIVE"
_THIRD_ISSUER_IDENTITY: Final[str] = "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY:V1"
_THIRD_VALID_FROM: Final[datetime] = datetime(2026, 9, 20, 1, 30, 21, 168602, tzinfo=timezone.utc)
_THIRD_VALID_UNTIL: Final[datetime] = datetime(2026, 9, 21, 1, 30, 21, 168602, tzinfo=timezone.utc)
_THIRD_KEY_FINGERPRINT: Final[str] = LegalCorpusOperatorTrustedKey.fingerprint_for(
    key_id=_THIRD_KEY_ID,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_THIRD_PUBLIC_KEY_BASE64URL,
    issuer_identity=_THIRD_ISSUER_IDENTITY,
    authority_domain=AUTHORITY_DOMAIN,
    scope=TRUST_ROOT_SCOPE,
    permitted_operations=frozenset({AUTHORIZED_OPERATION}),
    valid_from=_THIRD_VALID_FROM,
    valid_until=_THIRD_VALID_UNTIL,
    status=LegalCorpusOperatorKeyStatus.RETIRED,
    revision=2,
    trust_root_provenance=TRUST_ROOT_PROVENANCE,
)
_THIRD_TRUSTED_KEY: Final[LegalCorpusOperatorTrustedKey] = LegalCorpusOperatorTrustedKey(
    key_id=_THIRD_KEY_ID,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_THIRD_PUBLIC_KEY_BASE64URL,
    issuer_identity=_THIRD_ISSUER_IDENTITY,
    authority_domain=AUTHORITY_DOMAIN,
    scope=TRUST_ROOT_SCOPE,
    permitted_operations=frozenset({AUTHORIZED_OPERATION}),
    valid_from=_THIRD_VALID_FROM,
    valid_until=_THIRD_VALID_UNTIL,
    status=LegalCorpusOperatorKeyStatus.RETIRED,
    revision=2,
    trust_root_provenance=TRUST_ROOT_PROVENANCE,
    fingerprint=_THIRD_KEY_FINGERPRINT,
)
_FOURTH_KEY_ID: Final[str] = "prdca-key:legal-corpus-f7d289cc9eca0ec760ef1cbef8316de3"
_FOURTH_PUBLIC_KEY_BASE64URL: Final[str] = "GmqIeQEE_owI-LejDNQCd216_pE408OOlAt1ZMWQXsc"
_FOURTH_ISSUER_IDENTITY: Final[str] = "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY:V1"
_FOURTH_VALID_FROM: Final[datetime] = datetime(2026, 9, 21, 20, 49, 35, 129582, tzinfo=timezone.utc)
_FOURTH_VALID_UNTIL: Final[datetime] = datetime(2026, 9, 22, 20, 49, 35, 129582, tzinfo=timezone.utc)
_FOURTH_KEY_FINGERPRINT: Final[str] = LegalCorpusOperatorTrustedKey.fingerprint_for(
    key_id=_FOURTH_KEY_ID,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_FOURTH_PUBLIC_KEY_BASE64URL,
    issuer_identity=_FOURTH_ISSUER_IDENTITY,
    authority_domain=AUTHORITY_DOMAIN,
    scope=TRUST_ROOT_SCOPE,
    permitted_operations=frozenset({AUTHORIZED_OPERATION}),
    valid_from=_FOURTH_VALID_FROM,
    valid_until=_FOURTH_VALID_UNTIL,
    status=LegalCorpusOperatorKeyStatus.RETIRED,
    revision=2,
    trust_root_provenance=TRUST_ROOT_PROVENANCE,
)
_FOURTH_TRUSTED_KEY: Final[LegalCorpusOperatorTrustedKey] = LegalCorpusOperatorTrustedKey(
    key_id=_FOURTH_KEY_ID,
    algorithm=ED25519_ALGORITHM,
    public_key_base64url=_FOURTH_PUBLIC_KEY_BASE64URL,
    issuer_identity=_FOURTH_ISSUER_IDENTITY,
    authority_domain=AUTHORITY_DOMAIN,
    scope=TRUST_ROOT_SCOPE,
    permitted_operations=frozenset({AUTHORIZED_OPERATION}),
    valid_from=_FOURTH_VALID_FROM,
    valid_until=_FOURTH_VALID_UNTIL,
    status=LegalCorpusOperatorKeyStatus.RETIRED,
    revision=2,
    trust_root_provenance=TRUST_ROOT_PROVENANCE,
    fingerprint=_FOURTH_KEY_FINGERPRINT,
)
TRUSTED_KEYS: Final[tuple[LegalCorpusOperatorTrustedKey, ...]] = (
    _FIRST_TRUSTED_KEY,
    _SECOND_TRUSTED_KEY,
    _THIRD_TRUSTED_KEY,
    _FOURTH_TRUSTED_KEY,
)
_TRUSTED_KEY_INDEX: Final[Mapping[str, LegalCorpusOperatorTrustedKey]] = MappingProxyType(
    {record.key_id: record for record in TRUSTED_KEYS}
)


class LegalCorpusOperatorTrustRoot:
    """Resolve source-owned trusted keys without accepting caller mappings."""

    @staticmethod
    def resolve(key_id: str) -> LegalCorpusOperatorTrustedKey:
        """Return one exact trusted key or raise a bounded unknown-key error."""
        normalized = _text(key_id, "KEY_ID_INVALID", pattern=_KEY_ID)
        record = _TRUSTED_KEY_INDEX.get(normalized)
        if record is None:
            raise LegalCorpusOperatorTrustRootError("UNKNOWN_TRUSTED_KEY")
        return record

    @staticmethod
    def all_keys() -> tuple[LegalCorpusOperatorTrustedKey, ...]:
        """Return the immutable source-owned key snapshot."""
        return TRUSTED_KEYS

    @staticmethod
    def production_key_count() -> int:
        """Return the number of source-owned production trusted keys."""
        return len(TRUSTED_KEYS)


__all__ = [
    "AUTHORIZED_OPERATION",
    "AUTHORITY_DOMAIN",
    "ED25519_ALGORITHM",
    "LegalCorpusOperatorKeyStatus",
    "LegalCorpusOperatorTrustRoot",
    "LegalCorpusOperatorTrustRootError",
    "LegalCorpusOperatorTrustedKey",
    "PUBLIC_KEY_ENCODING",
    "TRUSTED_KEYS",
    "TRUST_ROOT_PROVENANCE",
    "TRUST_ROOT_SCOPE",
    "VERSION",
]


# ARTIFACT: legal_corpus_operator_trust_root.py
# VERSION: v1.8.0-R9B-P7-A3-H7-POST-PROVISIONING-SUCCESSOR-KEY-RETIREMENT-TRUST-ROOT
# AUTHORITY BOUNDARY: immutable PLATFORM public-key trust material only
# TENANT POSTURE: no tenant, principal, membership, or user authority
# FAIL-CLOSED POSTURE: unknown keys, malformed records, and drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
