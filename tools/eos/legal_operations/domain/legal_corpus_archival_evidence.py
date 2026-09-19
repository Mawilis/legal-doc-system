"""Truth-preserving archival evidence value objects for the legal corpus.

TITLE: WILSY OS Legal Corpus Archival Evidence Domain
VERSION: v1.0.1-R1D-B0F-B4-R8O-P3A-R1-LEGAL-CORPUS-ARCHIVAL-EVIDENCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Represents a future immutable archival package containing public
         authorization, trust-snapshot, document, R8D, and proposition-ledger
         evidence without retroactively asserting an admission event.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_corpus_archival_evidence.py
COLLABORATION / OWNERSHIP: The later governed capture surface supplies public
                            evidence; P3C will verify authenticity; a later
                            retirement gate adjudicates trust-root lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.0.1-R1D-B0F-B4-R8O-P3A-R1 separates substantive document-content
           validation from single-line metadata validation while preserving
           exact captured content and canonical digest authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Public authorization and public-key evidence only;
                            no private key, secret, filesystem, environment,
                            request, network, or database access exists here.
TENANT BOUNDARY: PLATFORM legal-corpus evidence only; no tenant or principal
                 authority is represented.
AUTHORITY BOUNDARY: Archival representation only. This module cannot issue,
                    authorize, admit, sign, approve, execute, or mutate.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Invalid schemas, identities, timestamps, hashes,
                     propositions, snapshots, claims, and fingerprints reject.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping, cast
from uuid import UUID

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    canonical_document_digest,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_authorization import (
    SCHEMA as AUTHORIZATION_SCHEMA,
    LegalCorpusOperatorAuthorizationOperation,
    LegalCorpusOperatorAuthorizationScope,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_trust_root import (
    AUTHORIZED_OPERATION as TRUST_AUTHORIZED_OPERATION,
    AUTHORITY_DOMAIN,
    ED25519_ALGORITHM,
    LegalCorpusOperatorKeyStatus,
    LegalCorpusOperatorTrustedKey,
    TRUST_ROOT_PROVENANCE,
    TRUST_ROOT_SCOPE,
)
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    AUTHORITY_SOURCE_VERSION,
    LegalCorpusProvisioningAuthorityEvidence,
    LegalCorpusProvisioningAuthorityScope,
    LegalCorpusProvisioningAuthoritySource,
    LegalCorpusProvisioningOperation,
)


VERSION: Final[str] = "v1.0.1-R1D-B0F-B4-R8O-P3A-R1-LEGAL-CORPUS-ARCHIVAL-EVIDENCE"
SCHEMA: Final[str] = "WILSY-LEGAL-CORPUS-ARCHIVAL-EVIDENCE/V1"
HISTORICAL_EVENT_TIME_SOURCE: Final[str] = "NONE"
HISTORICAL_EVENT_TIME_RECOVERY: Final[str] = "IMPOSSIBLE_FROM_CURRENT_CANONICAL_EVIDENCE"
D1_BINDING_SOURCE: Final[str] = "NONE"
D1_BINDING_RECOVERY: Final[str] = "IMPOSSIBLE_FROM_CURRENT_CANONICAL_EVIDENCE"
D1_R8D_RELATIONSHIP: Final[str] = "CONSISTENT_BUT_NOT_IDENTITY_BOUND"
R8D_AUTHORIZED_AT_SEMANTICS: Final[str] = "AUTHORIZATION_ISSUANCE_TIME_COPY"
_SHA3_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_KEY_ID: Final[re.Pattern[str]] = re.compile(r"^prdca-key:[a-z0-9][a-z0-9._-]{0,63}$")


class LegalCorpusArchivalEvidenceError(ValueError):
    """Stable, non-sensitive failure for archival evidence input or drift."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCorpusArchivalProposition(StrEnum):
    """The complete immutable P1-P9 proposition identity set."""

    P1_D1_SIGNATURE_AUTHENTIC = "P1_D1_SIGNATURE_AUTHENTIC"
    P2_D1_VALID_AT_SIGNED_ISSUANCE_TIME = "P2_D1_VALID_AT_SIGNED_ISSUANCE_TIME"
    P3_D1_VALID_AT_ACTUAL_ADMISSION_EVENT_TIME = "P3_D1_VALID_AT_ACTUAL_ADMISSION_EVENT_TIME"
    P4_D1_BOUND_TO_EXACT_R8D_EVENT = "P4_D1_BOUND_TO_EXACT_R8D_EVENT"
    P5_R8D_EXACT_AND_INTEGRITY_VALID = "P5_R8D_EXACT_AND_INTEGRITY_VALID"
    P6_DOCUMENT_EXACT_AND_CANONICAL = "P6_DOCUMENT_EXACT_AND_CANONICAL"
    P7_PUBLIC_KEY_MATCHES_D1_KEY_ID = "P7_PUBLIC_KEY_MATCHES_D1_KEY_ID"
    P8_TRUST_STATUS_OBSERVED_AT_ARCHIVAL_CAPTURE = "P8_TRUST_STATUS_OBSERVED_AT_ARCHIVAL_CAPTURE"
    P9_TRUST_ACTIVE_AT_ORIGINAL_ADMISSION_EVENT = "P9_TRUST_ACTIVE_AT_ORIGINAL_ADMISSION_EVENT"


class LegalCorpusArchivalClassification(StrEnum):
    """Machine-visible proposition states; UNPROVEN is not FALSE."""

    PROVEN = "PROVEN"
    UNPROVEN = "UNPROVEN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


def _text(value: object, code: str) -> str:
    """Require non-empty, stable single-line text without silent rewriting."""
    if not isinstance(value, str) or not value or value != value.strip() or "\n" in value or "\r" in value:
        raise LegalCorpusArchivalEvidenceError(code)
    return value


def _document_content(value: object, code: str) -> str:
    """Require substantive legal content while preserving its exact value."""
    if not isinstance(value, str) or not value.strip():
        raise LegalCorpusArchivalEvidenceError(code)
    return value


def _sha3(value: object, code: str) -> str:
    """Require a lowercase SHA3-512 hexadecimal value."""
    if not isinstance(value, str) or _SHA3_HEX.fullmatch(value) is None:
        raise LegalCorpusArchivalEvidenceError(code)
    return value


def _timestamp(value: object, code: str) -> datetime:
    """Require an aware timestamp and canonicalize it to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalCorpusArchivalEvidenceError(code)
    return value.astimezone(timezone.utc)


def _fingerprint(payload: Mapping[str, object]) -> str:
    """Hash one deterministic compact JSON preimage."""
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _uuid4(value: object) -> str:
    """Require the non-circular capture-authority package identity."""
    text = _text(value, "PACKAGE_ID_INVALID")
    try:
        parsed = UUID(text)
    except (ValueError, AttributeError):
        raise LegalCorpusArchivalEvidenceError("PACKAGE_ID_INVALID") from None
    if parsed.version != 4 or str(parsed) != text.lower():
        raise LegalCorpusArchivalEvidenceError("PACKAGE_ID_INVALID")
    return text.lower()


def _enum(value: object, enum_type: type[StrEnum], code: str) -> StrEnum:
    """Require an existing repository enum without inventing new authority."""
    if not isinstance(value, enum_type):
        raise LegalCorpusArchivalEvidenceError(code)
    return value


@dataclass(frozen=True, slots=True)
class LegalCorpusArchivalPropositionEntry:
    """Immutable evidence/limitation record for exactly one P1-P9 claim."""

    proposition: LegalCorpusArchivalProposition
    classification: LegalCorpusArchivalClassification
    evidence_source: str
    evidence_identity: str
    limitation_reason: str

    def __post_init__(self) -> None:
        proposition = _enum(self.proposition, LegalCorpusArchivalProposition, "PROPOSITION_ID_INVALID")
        classification = _enum(self.classification, LegalCorpusArchivalClassification, "PROPOSITION_CLASSIFICATION_INVALID")
        source = _text(self.evidence_source, "PROPOSITION_EVIDENCE_SOURCE_INVALID")
        identity = _text(self.evidence_identity, "PROPOSITION_EVIDENCE_IDENTITY_INVALID")
        limitation = _text(self.limitation_reason, "PROPOSITION_LIMITATION_INVALID") if self.limitation_reason else ""
        if classification is LegalCorpusArchivalClassification.PROVEN and (not source or not identity):
            raise LegalCorpusArchivalEvidenceError("PROVEN_PROPOSITION_EVIDENCE_REQUIRED")
        if classification is LegalCorpusArchivalClassification.UNPROVEN and not limitation:
            raise LegalCorpusArchivalEvidenceError("UNPROVEN_PROPOSITION_LIMITATION_REQUIRED")
        if classification is LegalCorpusArchivalClassification.NOT_APPLICABLE and not limitation:
            raise LegalCorpusArchivalEvidenceError("NOT_APPLICABLE_PROPOSITION_REASON_REQUIRED")
        object.__setattr__(self, "proposition", proposition)
        object.__setattr__(self, "classification", classification)
        object.__setattr__(self, "evidence_source", source)
        object.__setattr__(self, "evidence_identity", identity)
        object.__setattr__(self, "limitation_reason", limitation)

    def to_document(self) -> dict[str, str]:
        """Serialize stable primitive proposition evidence."""
        return {
            "proposition": self.proposition.value,
            "classification": self.classification.value,
            "evidence_source": self.evidence_source,
            "evidence_identity": self.evidence_identity,
            "limitation_reason": self.limitation_reason,
        }

    @classmethod
    def from_document(cls, payload: Mapping[str, object]) -> "LegalCorpusArchivalPropositionEntry":
        """Hydrate one proposition entry without performing verification or I/O."""
        if not isinstance(payload, Mapping) or set(payload) != {
            "proposition", "classification", "evidence_source", "evidence_identity", "limitation_reason"
        }:
            raise LegalCorpusArchivalEvidenceError("PROPOSITION_SCHEMA_INVALID")
        try:
            return cls(
                proposition=LegalCorpusArchivalProposition(cast(str, payload["proposition"])),
                classification=LegalCorpusArchivalClassification(cast(str, payload["classification"])),
                evidence_source=cast(str, payload["evidence_source"]),
                evidence_identity=cast(str, payload["evidence_identity"]),
                limitation_reason=cast(str, payload["limitation_reason"]),
            )
        except (TypeError, ValueError) as error:
            if isinstance(error, LegalCorpusArchivalEvidenceError):
                raise
            raise LegalCorpusArchivalEvidenceError("PROPOSITION_VALUE_INVALID") from None


@dataclass(frozen=True, slots=True)
class LegalCorpusArchivalTrustSnapshot:
    """Public trust material observed at archival capture time only."""

    key_id: str
    algorithm: str
    issuer: str
    authority_domain: str
    scope: str
    operation: str
    permitted_operations: tuple[str, ...]
    public_key: str
    valid_from: datetime
    valid_until: datetime | None
    status_observed_at_archival_capture: LegalCorpusOperatorKeyStatus
    revision: int
    trust_root_provenance: str
    trust_record_fingerprint: str
    snapshot_observed_at: datetime
    snapshot_source_identity: str
    snapshot_source_fingerprint: str
    snapshot_fingerprint: str

    def __post_init__(self) -> None:
        key_id = _text(self.key_id, "TRUST_SNAPSHOT_KEY_ID_INVALID")
        if _KEY_ID.fullmatch(key_id) is None:
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_KEY_ID_INVALID")
        algorithm = _text(self.algorithm, "TRUST_SNAPSHOT_ALGORITHM_INVALID")
        issuer = _text(self.issuer, "TRUST_SNAPSHOT_ISSUER_INVALID")
        authority_domain = _text(self.authority_domain, "TRUST_SNAPSHOT_AUTHORITY_DOMAIN_INVALID")
        scope = _text(self.scope, "TRUST_SNAPSHOT_SCOPE_INVALID")
        operation = _text(self.operation, "TRUST_SNAPSHOT_OPERATION_INVALID")
        if not isinstance(self.permitted_operations, tuple) or not self.permitted_operations or any(not isinstance(item, str) or not item for item in self.permitted_operations) or tuple(sorted(self.permitted_operations)) != self.permitted_operations:
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_PERMISSIONS_INVALID")
        public_key = _text(self.public_key, "TRUST_SNAPSHOT_PUBLIC_KEY_INVALID")
        valid_from = _timestamp(self.valid_from, "TRUST_SNAPSHOT_VALID_FROM_INVALID")
        valid_until = None if self.valid_until is None else _timestamp(self.valid_until, "TRUST_SNAPSHOT_VALID_UNTIL_INVALID")
        if valid_until is not None and valid_until <= valid_from:
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_VALIDITY_INVALID")
        if not isinstance(self.status_observed_at_archival_capture, LegalCorpusOperatorKeyStatus):
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_STATUS_INVALID")
        status = self.status_observed_at_archival_capture
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_REVISION_INVALID")
        provenance = _text(self.trust_root_provenance, "TRUST_SNAPSHOT_PROVENANCE_INVALID")
        trust_fingerprint = _sha3(self.trust_record_fingerprint, "TRUST_RECORD_FINGERPRINT_INVALID")
        observed_at = _timestamp(self.snapshot_observed_at, "TRUST_SNAPSHOT_OBSERVED_AT_INVALID")
        source_identity = _text(self.snapshot_source_identity, "TRUST_SNAPSHOT_SOURCE_IDENTITY_INVALID")
        source_fingerprint = _sha3(self.snapshot_source_fingerprint, "TRUST_SNAPSHOT_SOURCE_FINGERPRINT_INVALID")
        snapshot_fingerprint = _sha3(self.snapshot_fingerprint, "TRUST_SNAPSHOT_FINGERPRINT_INVALID")
        if algorithm != ED25519_ALGORITHM or authority_domain != AUTHORITY_DOMAIN or scope != TRUST_ROOT_SCOPE or operation != TRUST_AUTHORIZED_OPERATION or self.permitted_operations != (operation,) or provenance != TRUST_ROOT_PROVENANCE:
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_AUTHORITY_SCOPE_INVALID")
        try:
            expected_trust = LegalCorpusOperatorTrustedKey.fingerprint_for(
                key_id=key_id,
                algorithm=algorithm,
                public_key_base64url=public_key,
                issuer_identity=issuer,
                authority_domain=authority_domain,
                scope=scope,
                permitted_operations=frozenset(self.permitted_operations),
                valid_from=valid_from,
                valid_until=valid_until,
                status=status,
                revision=self.revision,
                trust_root_provenance=provenance,
            )
        except Exception as error:
            if isinstance(error, LegalCorpusArchivalEvidenceError):
                raise
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_PUBLIC_MATERIAL_INVALID") from None
        if expected_trust != trust_fingerprint:
            raise LegalCorpusArchivalEvidenceError("TRUST_RECORD_FINGERPRINT_MISMATCH")
        expected_snapshot = self.fingerprint_for(
            key_id=key_id,
            algorithm=algorithm,
            issuer=issuer,
            authority_domain=authority_domain,
            scope=scope,
            operation=operation,
            permitted_operations=self.permitted_operations,
            public_key=public_key,
            valid_from=valid_from,
            valid_until=valid_until,
            status_observed_at_archival_capture=status,
            revision=self.revision,
            trust_root_provenance=provenance,
            trust_record_fingerprint=trust_fingerprint,
            snapshot_observed_at=observed_at,
            snapshot_source_identity=source_identity,
            snapshot_source_fingerprint=source_fingerprint,
        )
        if expected_snapshot != snapshot_fingerprint:
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_FINGERPRINT_MISMATCH")
        for name, value in (("key_id", key_id), ("algorithm", algorithm), ("issuer", issuer), ("authority_domain", authority_domain), ("scope", scope), ("operation", operation), ("permitted_operations", self.permitted_operations), ("public_key", public_key), ("valid_from", valid_from), ("valid_until", valid_until), ("status_observed_at_archival_capture", status), ("revision", self.revision), ("trust_root_provenance", provenance), ("trust_record_fingerprint", trust_fingerprint), ("snapshot_observed_at", observed_at), ("snapshot_source_identity", source_identity), ("snapshot_source_fingerprint", source_fingerprint)):
            object.__setattr__(self, name, value)

    @staticmethod
    def fingerprint_for(
        *, key_id: str, algorithm: str, issuer: str, authority_domain: str, scope: str, operation: str, permitted_operations: tuple[str, ...], public_key: str,
        valid_from: datetime, valid_until: datetime | None,
        status_observed_at_archival_capture: LegalCorpusOperatorKeyStatus,
        revision: int, trust_root_provenance: str, trust_record_fingerprint: str, snapshot_observed_at: datetime,
        snapshot_source_identity: str, snapshot_source_fingerprint: str,
    ) -> str:
        """Compute the snapshot fingerprint excluding itself."""
        if not isinstance(status_observed_at_archival_capture, LegalCorpusOperatorKeyStatus):
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_STATUS_INVALID")
        payload = {
            "key_id": _text(key_id, "TRUST_SNAPSHOT_KEY_ID_INVALID"),
            "algorithm": _text(algorithm, "TRUST_SNAPSHOT_ALGORITHM_INVALID"),
            "issuer": _text(issuer, "TRUST_SNAPSHOT_ISSUER_INVALID"),
            "authority_domain": _text(authority_domain, "TRUST_SNAPSHOT_AUTHORITY_DOMAIN_INVALID"),
            "scope": _text(scope, "TRUST_SNAPSHOT_SCOPE_INVALID"),
            "operation": _text(operation, "TRUST_SNAPSHOT_OPERATION_INVALID"),
            "permitted_operations": tuple(sorted(permitted_operations)),
            "public_key": _text(public_key, "TRUST_SNAPSHOT_PUBLIC_KEY_INVALID"),
            "valid_from": _timestamp(valid_from, "TRUST_SNAPSHOT_VALID_FROM_INVALID").isoformat(),
            "valid_until": None if valid_until is None else _timestamp(valid_until, "TRUST_SNAPSHOT_VALID_UNTIL_INVALID").isoformat(),
            "status_observed_at_archival_capture": status_observed_at_archival_capture.value,
            "revision": revision,
            "trust_root_provenance": _text(trust_root_provenance, "TRUST_SNAPSHOT_PROVENANCE_INVALID"),
            "trust_record_fingerprint": _sha3(trust_record_fingerprint, "TRUST_RECORD_FINGERPRINT_INVALID"),
            "snapshot_observed_at": _timestamp(snapshot_observed_at, "TRUST_SNAPSHOT_OBSERVED_AT_INVALID").isoformat(),
            "snapshot_source_identity": _text(snapshot_source_identity, "TRUST_SNAPSHOT_SOURCE_IDENTITY_INVALID"),
            "snapshot_source_fingerprint": _sha3(snapshot_source_fingerprint, "TRUST_SNAPSHOT_SOURCE_FINGERPRINT_INVALID"),
        }
        return _fingerprint(payload)

    def to_document(self) -> dict[str, object]:
        """Serialize public trust evidence with capture-time semantics explicit."""
        return {
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "issuer": self.issuer,
            "authority_domain": self.authority_domain,
            "scope": self.scope,
            "operation": self.operation,
            "permitted_operations": list(self.permitted_operations),
            "public_key": self.public_key,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": None if self.valid_until is None else self.valid_until.isoformat(),
            "status_observed_at_archival_capture": self.status_observed_at_archival_capture.value,
            "revision": self.revision,
            "trust_root_provenance": self.trust_root_provenance,
            "trust_record_fingerprint": self.trust_record_fingerprint,
            "snapshot_observed_at": self.snapshot_observed_at.isoformat(),
            "snapshot_source_identity": self.snapshot_source_identity,
            "snapshot_source_fingerprint": self.snapshot_source_fingerprint,
            "snapshot_fingerprint": self.snapshot_fingerprint,
        }

    @classmethod
    def from_document(cls, payload: Mapping[str, object]) -> "LegalCorpusArchivalTrustSnapshot":
        """Hydrate and self-validate a public trust snapshot."""
        expected = {"key_id", "algorithm", "issuer", "authority_domain", "scope", "operation", "permitted_operations", "public_key", "valid_from", "valid_until", "status_observed_at_archival_capture", "revision", "trust_root_provenance", "trust_record_fingerprint", "snapshot_observed_at", "snapshot_source_identity", "snapshot_source_fingerprint", "snapshot_fingerprint"}
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_SCHEMA_INVALID")
        try:
            return cls(
                key_id=cast(str, payload["key_id"]), algorithm=cast(str, payload["algorithm"]), issuer=cast(str, payload["issuer"]), authority_domain=cast(str, payload["authority_domain"]), scope=cast(str, payload["scope"]), operation=cast(str, payload["operation"]), permitted_operations=tuple(cast(list[str], payload["permitted_operations"])), public_key=cast(str, payload["public_key"]),
                valid_from=datetime.fromisoformat(cast(str, payload["valid_from"])), valid_until=None if payload["valid_until"] is None else datetime.fromisoformat(cast(str, payload["valid_until"])),
                status_observed_at_archival_capture=LegalCorpusOperatorKeyStatus(cast(str, payload["status_observed_at_archival_capture"])), revision=cast(int, payload["revision"]), trust_root_provenance=cast(str, payload["trust_root_provenance"]), trust_record_fingerprint=cast(str, payload["trust_record_fingerprint"]), snapshot_observed_at=datetime.fromisoformat(cast(str, payload["snapshot_observed_at"])), snapshot_source_identity=cast(str, payload["snapshot_source_identity"]), snapshot_source_fingerprint=cast(str, payload["snapshot_source_fingerprint"]), snapshot_fingerprint=cast(str, payload["snapshot_fingerprint"]),
            )
        except (TypeError, ValueError) as error:
            raise LegalCorpusArchivalEvidenceError("TRUST_SNAPSHOT_VALUE_INVALID") from error


@dataclass(frozen=True, slots=True)
class LegalCorpusArchivalAuthorizationSnapshot:
    """Complete public D1 envelope, without performing signature verification."""

    schema: str
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
    authorization_file_sha3_512: str

    def __post_init__(self) -> None:
        if self.schema != AUTHORIZATION_SCHEMA:
            raise LegalCorpusArchivalEvidenceError("AUTHORIZATION_SNAPSHOT_SCHEMA_INVALID")
        values = {
            "authorization_id": _text(self.authorization_id, "AUTHORIZATION_SNAPSHOT_ID_INVALID"),
            "source_document_id": _text(self.source_document_id, "AUTHORIZATION_SNAPSHOT_DOCUMENT_ID_INVALID"),
            "source_version": _text(self.source_version, "AUTHORIZATION_SNAPSHOT_VERSION_INVALID"),
            "source_content_reference": _text(self.source_content_reference, "AUTHORIZATION_SNAPSHOT_REFERENCE_INVALID"),
            "replay_nonce": _text(self.replay_nonce, "AUTHORIZATION_SNAPSHOT_NONCE_INVALID"),
            "idempotency_key": _text(self.idempotency_key, "AUTHORIZATION_SNAPSHOT_IDEMPOTENCY_INVALID"),
            "authority_mechanism": _text(self.authority_mechanism, "AUTHORIZATION_SNAPSHOT_MECHANISM_INVALID"),
            "authority_mechanism_version": _text(self.authority_mechanism_version, "AUTHORIZATION_SNAPSHOT_MECHANISM_VERSION_INVALID"),
            "signature": _text(self.signature, "AUTHORIZATION_SNAPSHOT_SIGNATURE_INVALID"),
        }
        key_id = _text(self.key_id, "AUTHORIZATION_SNAPSHOT_KEY_ID_INVALID")
        if _KEY_ID.fullmatch(key_id) is None:
            raise LegalCorpusArchivalEvidenceError("AUTHORIZATION_SNAPSHOT_KEY_ID_INVALID")
        if not isinstance(self.operation, LegalCorpusOperatorAuthorizationOperation) or not isinstance(self.scope, LegalCorpusOperatorAuthorizationScope):
            raise LegalCorpusArchivalEvidenceError("AUTHORIZATION_SNAPSHOT_AUTHORITY_INVALID")
        if not isinstance(self.source_agreement_type, LegalAgreementType) or not isinstance(self.source_status, LegalDocumentStatus):
            raise LegalCorpusArchivalEvidenceError("AUTHORIZATION_SNAPSHOT_SOURCE_ENUM_INVALID")
        if self.source_status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            raise LegalCorpusArchivalEvidenceError("AUTHORIZATION_SNAPSHOT_NON_DRAFT_STATUS")
        issued_at = _timestamp(self.issued_at, "AUTHORIZATION_SNAPSHOT_ISSUED_AT_INVALID")
        not_before = _timestamp(self.not_before, "AUTHORIZATION_SNAPSHOT_NOT_BEFORE_INVALID")
        expires_at = _timestamp(self.expires_at, "AUTHORIZATION_SNAPSHOT_EXPIRES_AT_INVALID")
        if not_before > issued_at or issued_at > expires_at:
            raise LegalCorpusArchivalEvidenceError("AUTHORIZATION_SNAPSHOT_TIME_WINDOW_INVALID")
        digest = _sha3(self.source_sha3_512, "AUTHORIZATION_SNAPSHOT_SOURCE_DIGEST_INVALID")
        file_digest = _sha3(self.authorization_file_sha3_512, "AUTHORIZATION_FILE_FINGERPRINT_INVALID")
        for name, value in values.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "key_id", key_id)
        object.__setattr__(self, "issued_at", issued_at)
        object.__setattr__(self, "not_before", not_before)
        object.__setattr__(self, "expires_at", expires_at)
        object.__setattr__(self, "source_sha3_512", digest)
        object.__setattr__(self, "authorization_file_sha3_512", file_digest)

    def to_document(self) -> dict[str, object]:
        """Serialize the complete public D1 envelope and file fingerprint."""
        return {
            "schema": self.schema, "authorization_id": self.authorization_id, "key_id": self.key_id,
            "operation": self.operation.value, "scope": self.scope.value, "source_document_id": self.source_document_id,
            "source_agreement_type": self.source_agreement_type.value, "source_version": self.source_version,
            "source_status": self.source_status.value, "source_content_reference": self.source_content_reference,
            "source_sha3_512": self.source_sha3_512, "issued_at": self.issued_at.isoformat(),
            "not_before": self.not_before.isoformat(), "expires_at": self.expires_at.isoformat(),
            "replay_nonce": self.replay_nonce, "idempotency_key": self.idempotency_key,
            "authority_mechanism": self.authority_mechanism, "authority_mechanism_version": self.authority_mechanism_version,
            "signature": self.signature, "authorization_file_sha3_512": self.authorization_file_sha3_512,
        }

    @classmethod
    def from_document(cls, payload: Mapping[str, object]) -> "LegalCorpusArchivalAuthorizationSnapshot":
        """Hydrate the public envelope without invoking D1 verification."""
        expected = {"schema", "authorization_id", "key_id", "operation", "scope", "source_document_id", "source_agreement_type", "source_version", "source_status", "source_content_reference", "source_sha3_512", "issued_at", "not_before", "expires_at", "replay_nonce", "idempotency_key", "authority_mechanism", "authority_mechanism_version", "signature", "authorization_file_sha3_512"}
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise LegalCorpusArchivalEvidenceError("AUTHORIZATION_SNAPSHOT_SCHEMA_INVALID")
        try:
            return cls(
                schema=cast(str, payload["schema"]), authorization_id=cast(str, payload["authorization_id"]), key_id=cast(str, payload["key_id"]),
                operation=LegalCorpusOperatorAuthorizationOperation(cast(str, payload["operation"])), scope=LegalCorpusOperatorAuthorizationScope(cast(str, payload["scope"])),
                source_document_id=cast(str, payload["source_document_id"]), source_agreement_type=LegalAgreementType(cast(str, payload["source_agreement_type"])), source_version=cast(str, payload["source_version"]), source_status=LegalDocumentStatus(cast(str, payload["source_status"])), source_content_reference=cast(str, payload["source_content_reference"]), source_sha3_512=cast(str, payload["source_sha3_512"]),
                issued_at=datetime.fromisoformat(cast(str, payload["issued_at"])), not_before=datetime.fromisoformat(cast(str, payload["not_before"])), expires_at=datetime.fromisoformat(cast(str, payload["expires_at"])), replay_nonce=cast(str, payload["replay_nonce"]), idempotency_key=cast(str, payload["idempotency_key"]), authority_mechanism=cast(str, payload["authority_mechanism"]), authority_mechanism_version=cast(str, payload["authority_mechanism_version"]), signature=cast(str, payload["signature"]), authorization_file_sha3_512=cast(str, payload["authorization_file_sha3_512"]),
            )
        except (TypeError, ValueError) as error:
            raise LegalCorpusArchivalEvidenceError("AUTHORIZATION_SNAPSHOT_VALUE_INVALID") from error


@dataclass(frozen=True, slots=True)
class LegalCorpusArchivalR8DSnapshot:
    """Exact R8D evidence snapshot with issuance-time semantics preserved."""

    authority_evidence_id: str
    authority_evidence_fingerprint: str
    scope: LegalCorpusProvisioningAuthorityScope
    operation: LegalCorpusProvisioningOperation
    source_document_id: str
    source_agreement_type: LegalAgreementType
    source_version: str
    source_status: LegalDocumentStatus
    source_content_reference: str
    source_sha3_512: str
    authority_source_id: LegalCorpusProvisioningAuthoritySource
    authority_source_version: str
    actor_representation: str
    authorized_at: datetime
    authorized_at_semantics: str
    idempotency_key: str

    def __post_init__(self) -> None:
        for value, code in ((self.authority_evidence_id, "R8D_EVIDENCE_ID_INVALID"), (self.actor_representation, "R8D_ACTOR_INVALID"), (self.source_document_id, "R8D_DOCUMENT_ID_INVALID"), (self.source_version, "R8D_VERSION_INVALID"), (self.source_content_reference, "R8D_REFERENCE_INVALID"), (self.idempotency_key, "R8D_IDEMPOTENCY_INVALID")):
            _text(value, code)
        if not isinstance(self.scope, LegalCorpusProvisioningAuthorityScope) or self.scope is not LegalCorpusProvisioningAuthorityScope.PLATFORM:
            raise LegalCorpusArchivalEvidenceError("R8D_SCOPE_INVALID")
        if not isinstance(self.operation, LegalCorpusProvisioningOperation) or self.operation is not LegalCorpusProvisioningOperation.DRAFT_ADMISSION:
            raise LegalCorpusArchivalEvidenceError("R8D_OPERATION_INVALID")
        if not isinstance(self.source_agreement_type, LegalAgreementType) or not isinstance(self.source_status, LegalDocumentStatus):
            raise LegalCorpusArchivalEvidenceError("R8D_SOURCE_ENUM_INVALID")
        if self.source_status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            raise LegalCorpusArchivalEvidenceError("R8D_NON_DRAFT_STATUS")
        if not isinstance(self.authority_source_id, LegalCorpusProvisioningAuthoritySource) or self.authority_source_version != AUTHORITY_SOURCE_VERSION:
            raise LegalCorpusArchivalEvidenceError("R8D_AUTHORITY_SOURCE_INVALID")
        digest = _sha3(self.source_sha3_512, "R8D_SOURCE_DIGEST_INVALID")
        fingerprint = _sha3(self.authority_evidence_fingerprint, "R8D_FINGERPRINT_INVALID")
        timestamp = _timestamp(self.authorized_at, "R8D_AUTHORIZED_AT_INVALID")
        semantics = _text(self.authorized_at_semantics, "R8D_AUTHORIZED_AT_SEMANTICS_INVALID")
        if semantics != R8D_AUTHORIZED_AT_SEMANTICS:
            raise LegalCorpusArchivalEvidenceError("R8D_AUTHORIZED_AT_SEMANTICS_INVALID")
        try:
            expected = LegalCorpusProvisioningAuthorityEvidence.fingerprint_for(
                authority_evidence_id=self.authority_evidence_id, scope=self.scope, operation=self.operation, source_document_id=self.source_document_id, source_agreement_type=self.source_agreement_type, source_version=self.source_version, source_status=self.source_status, source_content_reference=self.source_content_reference, source_sha3_512=digest, authority_source_id=self.authority_source_id, authority_source_version=self.authority_source_version, actor_representation=self.actor_representation, authorized_at=timestamp, idempotency_key=self.idempotency_key,
            )
        except Exception:
            raise LegalCorpusArchivalEvidenceError("R8D_SEMANTIC_VALUE_INVALID") from None
        if expected != fingerprint:
            raise LegalCorpusArchivalEvidenceError("R8D_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "source_sha3_512", digest)
        object.__setattr__(self, "authority_evidence_fingerprint", fingerprint)
        object.__setattr__(self, "authorized_at", timestamp)
        object.__setattr__(self, "authorized_at_semantics", semantics)

    def to_document(self) -> dict[str, object]:
        """Serialize all R8D fields without relabelling authorization time."""
        return {
            "authority_evidence_id": self.authority_evidence_id, "authority_evidence_fingerprint": self.authority_evidence_fingerprint,
            "scope": self.scope.value, "operation": self.operation.value, "source_document_id": self.source_document_id,
            "source_agreement_type": self.source_agreement_type.value, "source_version": self.source_version, "source_status": self.source_status.value,
            "source_content_reference": self.source_content_reference, "source_sha3_512": self.source_sha3_512,
            "authority_source_id": self.authority_source_id.value, "authority_source_version": self.authority_source_version,
            "actor_representation": self.actor_representation, "authorized_at": self.authorized_at.isoformat(),
            "authorized_at_semantics": self.authorized_at_semantics, "idempotency_key": self.idempotency_key,
        }

    @classmethod
    def from_document(cls, payload: Mapping[str, object]) -> "LegalCorpusArchivalR8DSnapshot":
        """Hydrate and self-check one R8D snapshot."""
        expected = {"authority_evidence_id", "authority_evidence_fingerprint", "scope", "operation", "source_document_id", "source_agreement_type", "source_version", "source_status", "source_content_reference", "source_sha3_512", "authority_source_id", "authority_source_version", "actor_representation", "authorized_at", "authorized_at_semantics", "idempotency_key"}
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise LegalCorpusArchivalEvidenceError("R8D_SNAPSHOT_SCHEMA_INVALID")
        try:
            return cls(
                authority_evidence_id=cast(str, payload["authority_evidence_id"]), authority_evidence_fingerprint=cast(str, payload["authority_evidence_fingerprint"]), scope=LegalCorpusProvisioningAuthorityScope(cast(str, payload["scope"])), operation=LegalCorpusProvisioningOperation(cast(str, payload["operation"])), source_document_id=cast(str, payload["source_document_id"]), source_agreement_type=LegalAgreementType(cast(str, payload["source_agreement_type"])), source_version=cast(str, payload["source_version"]), source_status=LegalDocumentStatus(cast(str, payload["source_status"])), source_content_reference=cast(str, payload["source_content_reference"]), source_sha3_512=cast(str, payload["source_sha3_512"]), authority_source_id=LegalCorpusProvisioningAuthoritySource(cast(str, payload["authority_source_id"])), authority_source_version=cast(str, payload["authority_source_version"]), actor_representation=cast(str, payload["actor_representation"]), authorized_at=datetime.fromisoformat(cast(str, payload["authorized_at"])), authorized_at_semantics=cast(str, payload["authorized_at_semantics"]), idempotency_key=cast(str, payload["idempotency_key"]),
            )
        except (TypeError, ValueError) as error:
            raise LegalCorpusArchivalEvidenceError("R8D_SNAPSHOT_VALUE_INVALID") from error


@dataclass(frozen=True, slots=True)
class LegalCorpusArchivalDocumentSnapshot:
    """Complete immutable Charter value needed for canonical equality."""

    document_id: str
    agreement_type: LegalAgreementType
    version: str
    title: str
    jurisdiction: str
    locale: str
    effective_from: datetime
    status: LegalDocumentStatus
    content_reference: str
    content: str
    sha3_512: str
    created_at: datetime
    supersedes_document_id: str | None

    def __post_init__(self) -> None:
        for value, code in ((self.document_id, "DOCUMENT_SNAPSHOT_ID_INVALID"), (self.version, "DOCUMENT_SNAPSHOT_VERSION_INVALID"), (self.title, "DOCUMENT_SNAPSHOT_TITLE_INVALID"), (self.jurisdiction, "DOCUMENT_SNAPSHOT_JURISDICTION_INVALID"), (self.locale, "DOCUMENT_SNAPSHOT_LOCALE_INVALID"), (self.content_reference, "DOCUMENT_SNAPSHOT_REFERENCE_INVALID")):
            _text(value, code)
        _document_content(self.content, "DOCUMENT_SNAPSHOT_CONTENT_INVALID")
        if not isinstance(self.agreement_type, LegalAgreementType) or not isinstance(self.status, LegalDocumentStatus):
            raise LegalCorpusArchivalEvidenceError("DOCUMENT_SNAPSHOT_ENUM_INVALID")
        if self.status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            raise LegalCorpusArchivalEvidenceError("DOCUMENT_SNAPSHOT_NON_DRAFT_STATUS")
        effective = _timestamp(self.effective_from, "DOCUMENT_SNAPSHOT_EFFECTIVE_FROM_INVALID")
        created = _timestamp(self.created_at, "DOCUMENT_SNAPSHOT_CREATED_AT_INVALID")
        digest = _sha3(self.sha3_512, "DOCUMENT_SNAPSHOT_DIGEST_INVALID")
        if digest != canonical_document_digest(self.content, self.content_reference):
            raise LegalCorpusArchivalEvidenceError("DOCUMENT_SNAPSHOT_DIGEST_MISMATCH")
        if self.supersedes_document_id is not None:
            _text(self.supersedes_document_id, "DOCUMENT_SNAPSHOT_SUPERSESSION_INVALID")
        object.__setattr__(self, "effective_from", effective)
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "sha3_512", digest)

    def to_document(self) -> dict[str, object]:
        """Serialize the complete immutable document value."""
        return {
            "document_id": self.document_id, "agreement_type": self.agreement_type.value, "version": self.version,
            "title": self.title, "jurisdiction": self.jurisdiction, "locale": self.locale,
            "effective_from": self.effective_from.isoformat(), "status": self.status.value,
            "content_reference": self.content_reference, "content": self.content, "sha3_512": self.sha3_512,
            "created_at": self.created_at.isoformat(), "supersedes_document_id": self.supersedes_document_id,
        }

    @classmethod
    def from_document(cls, payload: Mapping[str, object]) -> "LegalCorpusArchivalDocumentSnapshot":
        """Hydrate and self-check one canonical document snapshot."""
        expected = {"document_id", "agreement_type", "version", "title", "jurisdiction", "locale", "effective_from", "status", "content_reference", "content", "sha3_512", "created_at", "supersedes_document_id"}
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise LegalCorpusArchivalEvidenceError("DOCUMENT_SNAPSHOT_SCHEMA_INVALID")
        try:
            return cls(
                document_id=cast(str, payload["document_id"]), agreement_type=LegalAgreementType(cast(str, payload["agreement_type"])), version=cast(str, payload["version"]), title=cast(str, payload["title"]), jurisdiction=cast(str, payload["jurisdiction"]), locale=cast(str, payload["locale"]), effective_from=datetime.fromisoformat(cast(str, payload["effective_from"])), status=LegalDocumentStatus(cast(str, payload["status"])), content_reference=cast(str, payload["content_reference"]), content=cast(str, payload["content"]), sha3_512=cast(str, payload["sha3_512"]), created_at=datetime.fromisoformat(cast(str, payload["created_at"])), supersedes_document_id=None if payload["supersedes_document_id"] is None else cast(str, payload["supersedes_document_id"]),
            )
        except (TypeError, ValueError) as error:
            raise LegalCorpusArchivalEvidenceError("DOCUMENT_SNAPSHOT_VALUE_INVALID") from error


_REQUIRED_PROPOSITIONS: Final[frozenset[LegalCorpusArchivalProposition]] = frozenset(LegalCorpusArchivalProposition)


@dataclass(frozen=True, slots=True)
class LegalCorpusArchivalEvidencePackage:
    """Complete immutable archival package; representation is not authority."""

    package_id: str
    propositions: tuple[LegalCorpusArchivalPropositionEntry, ...]
    historical_event_time_source: str
    historical_event_time_recovery: str
    d1_to_r8d_identity_binding_source: str
    d1_to_r8d_binding_recovery: str
    d1_r8d_relationship_classification: str
    trust_snapshot: LegalCorpusArchivalTrustSnapshot
    authorization_snapshot: LegalCorpusArchivalAuthorizationSnapshot
    r8d_snapshot: LegalCorpusArchivalR8DSnapshot
    document_snapshot: LegalCorpusArchivalDocumentSnapshot
    package_fingerprint: str

    def __post_init__(self) -> None:
        package_id = _uuid4(self.package_id)
        if not isinstance(self.propositions, tuple) or any(not isinstance(item, LegalCorpusArchivalPropositionEntry) for item in self.propositions):
            raise LegalCorpusArchivalEvidenceError("PROPOSITION_LEDGER_INVALID")
        if len(self.propositions) != len(_REQUIRED_PROPOSITIONS) or {item.proposition for item in self.propositions} != _REQUIRED_PROPOSITIONS:
            raise LegalCorpusArchivalEvidenceError("PROPOSITION_LEDGER_INCOMPLETE_OR_DUPLICATE")
        for field, expected in (("historical_event_time_source", HISTORICAL_EVENT_TIME_SOURCE), ("historical_event_time_recovery", HISTORICAL_EVENT_TIME_RECOVERY), ("d1_to_r8d_identity_binding_source", D1_BINDING_SOURCE), ("d1_to_r8d_binding_recovery", D1_BINDING_RECOVERY), ("d1_r8d_relationship_classification", D1_R8D_RELATIONSHIP)):
            if _text(getattr(self, field), "HISTORICAL_LIMITATION_INVALID") != expected:
                raise LegalCorpusArchivalEvidenceError("HISTORICAL_LIMITATION_INVALID")
        if not isinstance(self.trust_snapshot, LegalCorpusArchivalTrustSnapshot) or not isinstance(self.authorization_snapshot, LegalCorpusArchivalAuthorizationSnapshot) or not isinstance(self.r8d_snapshot, LegalCorpusArchivalR8DSnapshot) or not isinstance(self.document_snapshot, LegalCorpusArchivalDocumentSnapshot):
            raise LegalCorpusArchivalEvidenceError("ARCHIVAL_SNAPSHOT_INVALID")
        fingerprint = _sha3(self.package_fingerprint, "PACKAGE_FINGERPRINT_INVALID")
        expected = self.fingerprint_for(
            package_id=package_id, propositions=self.propositions, historical_event_time_source=HISTORICAL_EVENT_TIME_SOURCE, historical_event_time_recovery=HISTORICAL_EVENT_TIME_RECOVERY, d1_to_r8d_identity_binding_source=D1_BINDING_SOURCE, d1_to_r8d_binding_recovery=D1_BINDING_RECOVERY, d1_r8d_relationship_classification=D1_R8D_RELATIONSHIP, trust_snapshot=self.trust_snapshot, authorization_snapshot=self.authorization_snapshot, r8d_snapshot=self.r8d_snapshot, document_snapshot=self.document_snapshot,
        )
        if expected != fingerprint:
            raise LegalCorpusArchivalEvidenceError("PACKAGE_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "package_id", package_id)
        object.__setattr__(self, "package_fingerprint", fingerprint)

    @staticmethod
    def fingerprint_for(
        *, package_id: str, propositions: tuple[LegalCorpusArchivalPropositionEntry, ...], historical_event_time_source: str, historical_event_time_recovery: str, d1_to_r8d_identity_binding_source: str, d1_to_r8d_binding_recovery: str, d1_r8d_relationship_classification: str, trust_snapshot: LegalCorpusArchivalTrustSnapshot, authorization_snapshot: LegalCorpusArchivalAuthorizationSnapshot, r8d_snapshot: LegalCorpusArchivalR8DSnapshot, document_snapshot: LegalCorpusArchivalDocumentSnapshot,
    ) -> str:
        """Compute the package fingerprint excluding the fingerprint field."""
        ordered = tuple(sorted((item.to_document() for item in propositions), key=lambda item: cast(str, item["proposition"])))
        payload = {
            "schema": SCHEMA, "version": VERSION, "package_id": _uuid4(package_id), "propositions": ordered,
            "historical_event_time_source": _text(historical_event_time_source, "HISTORICAL_LIMITATION_INVALID"), "historical_event_time_recovery": _text(historical_event_time_recovery, "HISTORICAL_LIMITATION_INVALID"), "d1_to_r8d_identity_binding_source": _text(d1_to_r8d_identity_binding_source, "HISTORICAL_LIMITATION_INVALID"), "d1_to_r8d_binding_recovery": _text(d1_to_r8d_binding_recovery, "HISTORICAL_LIMITATION_INVALID"), "d1_r8d_relationship_classification": _text(d1_r8d_relationship_classification, "HISTORICAL_LIMITATION_INVALID"),
            "trust_snapshot": trust_snapshot.to_document(), "authorization_snapshot": authorization_snapshot.to_document(), "r8d_snapshot": r8d_snapshot.to_document(), "document_snapshot": document_snapshot.to_document(),
        }
        return _fingerprint(payload)

    def canonical_payload(self) -> dict[str, object]:
        """Return the deterministic package preimage without its fingerprint."""
        return {
            "schema": SCHEMA, "version": VERSION, "package_id": self.package_id,
            "propositions": tuple(sorted((item.to_document() for item in self.propositions), key=lambda item: cast(str, item["proposition"]))),
            "historical_event_time_source": self.historical_event_time_source, "historical_event_time_recovery": self.historical_event_time_recovery,
            "d1_to_r8d_identity_binding_source": self.d1_to_r8d_identity_binding_source, "d1_to_r8d_binding_recovery": self.d1_to_r8d_binding_recovery, "d1_r8d_relationship_classification": self.d1_r8d_relationship_classification,
            "trust_snapshot": self.trust_snapshot.to_document(), "authorization_snapshot": self.authorization_snapshot.to_document(), "r8d_snapshot": self.r8d_snapshot.to_document(), "document_snapshot": self.document_snapshot.to_document(),
        }

    def canonical_bytes(self) -> bytes:
        """Return compact sorted UTF-8 package bytes with no trailing newline."""
        return json.dumps(self.canonical_payload(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def to_document(self) -> dict[str, object]:
        """Serialize the complete package including its derived fingerprint."""
        return {**self.canonical_payload(), "package_fingerprint": self.package_fingerprint}

    @classmethod
    def from_document(cls, payload: Mapping[str, object]) -> "LegalCorpusArchivalEvidencePackage":
        """Hydrate and self-validate a complete archival package."""
        expected = {"schema", "version", "package_id", "propositions", "historical_event_time_source", "historical_event_time_recovery", "d1_to_r8d_identity_binding_source", "d1_to_r8d_binding_recovery", "d1_r8d_relationship_classification", "trust_snapshot", "authorization_snapshot", "r8d_snapshot", "document_snapshot", "package_fingerprint"}
        if not isinstance(payload, Mapping) or set(payload) != expected or payload.get("schema") != SCHEMA or payload.get("version") != VERSION:
            raise LegalCorpusArchivalEvidenceError("PACKAGE_SCHEMA_INVALID")
        raw_props = payload["propositions"]
        if not isinstance(raw_props, (list, tuple)):
            raise LegalCorpusArchivalEvidenceError("PROPOSITION_LEDGER_INVALID")
        try:
            return cls(
                package_id=cast(str, payload["package_id"]), propositions=tuple(LegalCorpusArchivalPropositionEntry.from_document(cast(Mapping[str, object], item)) for item in raw_props),
                historical_event_time_source=cast(str, payload["historical_event_time_source"]), historical_event_time_recovery=cast(str, payload["historical_event_time_recovery"]), d1_to_r8d_identity_binding_source=cast(str, payload["d1_to_r8d_identity_binding_source"]), d1_to_r8d_binding_recovery=cast(str, payload["d1_to_r8d_binding_recovery"]), d1_r8d_relationship_classification=cast(str, payload["d1_r8d_relationship_classification"]),
                trust_snapshot=LegalCorpusArchivalTrustSnapshot.from_document(cast(Mapping[str, object], payload["trust_snapshot"])), authorization_snapshot=LegalCorpusArchivalAuthorizationSnapshot.from_document(cast(Mapping[str, object], payload["authorization_snapshot"])), r8d_snapshot=LegalCorpusArchivalR8DSnapshot.from_document(cast(Mapping[str, object], payload["r8d_snapshot"])), document_snapshot=LegalCorpusArchivalDocumentSnapshot.from_document(cast(Mapping[str, object], payload["document_snapshot"])), package_fingerprint=cast(str, payload["package_fingerprint"]),
            )
        except (TypeError, ValueError) as error:
            if isinstance(error, LegalCorpusArchivalEvidenceError):
                raise
            raise LegalCorpusArchivalEvidenceError("PACKAGE_VALUE_INVALID") from error


__all__ = [
    "D1_BINDING_RECOVERY", "D1_BINDING_SOURCE", "D1_R8D_RELATIONSHIP",
    "HISTORICAL_EVENT_TIME_RECOVERY", "HISTORICAL_EVENT_TIME_SOURCE",
    "LegalCorpusArchivalAuthorizationSnapshot", "LegalCorpusArchivalClassification",
    "LegalCorpusArchivalDocumentSnapshot", "LegalCorpusArchivalEvidenceError",
    "LegalCorpusArchivalEvidencePackage", "LegalCorpusArchivalProposition",
    "LegalCorpusArchivalPropositionEntry", "LegalCorpusArchivalR8DSnapshot",
    "LegalCorpusArchivalTrustSnapshot", "R8D_AUTHORIZED_AT_SEMANTICS", "SCHEMA", "VERSION",
]


# ARTIFACT: legal_corpus_archival_evidence.py
# VERSION: v1.0.1-R1D-B0F-B4-R8O-P3A-R1-LEGAL-CORPUS-ARCHIVAL-EVIDENCE
# AUTHORITY BOUNDARY: immutable archival evidence representation only
# TENANT POSTURE: PLATFORM corpus evidence; no tenant/principal authority
# FAIL-CLOSED POSTURE: historical gaps remain explicit and unproven
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
