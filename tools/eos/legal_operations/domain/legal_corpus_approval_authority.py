"""Immutable evidence for approving one reviewed platform legal document.

TITLE: WILSY OS Legal Corpus Approval Authority Domain
VERSION: v1.0.0-R1D-B0F-B4-R9B-P1-LEGAL-CORPUS-APPROVAL-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Represents one explicit human-governed approval transition from an
         exact reviewed legal-document draft to a distinct immutable APPROVED
         version. Construction is evidence representation only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_corpus_approval_authority.py
COLLABORATION / OWNERSHIP: A later governed authorization/signing layer supplies
                            human authenticity; the document registry owns
                            append-only persistence of both document versions
                            and future approval evidence.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.0.0-R9B-P1 defines fixed PLATFORM document-approval evidence,
           complete source/target binding, deterministic SHA3-512 identity,
           and fail-closed succession verification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only bounded identifiers and public evidence
                            metadata are retained; secrets and private keys are
                            neither accepted nor accessed.
TENANT BOUNDARY: Platform corpus authority is tenant-neutral; tenant and
                 principal acceptance are separate evidence domains.
AUTHORITY BOUNDARY: This value represents approval evidence only. Construction
                    does not prove human authorization, verify a signature,
                    persist a document, accept terms, bind an organisation, or
                    authorize commercial or financial execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
TRANSACTION BOUNDARY: No database, session, transaction, HTTP, network, key,
                      or signing lifecycle exists in this pure artifact.
FAIL-CLOSED POSTURE: Invalid enums, text, digests, timestamps, lifecycle,
                     succession, fingerprints, or document divergence reject.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
)


VERSION: Final[str] = "v1.0.0-R1D-B0F-B4-R9B-P1-LEGAL-CORPUS-APPROVAL-AUTHORITY"
APPROVAL_SCOPE: Final[str] = "PLATFORM"
APPROVAL_OPERATION: Final[str] = "LEGAL_CORPUS_DOCUMENT_APPROVAL"
APPROVAL_EVIDENCE_SCHEMA_VERSION: Final[str] = "v1.0.0"
APPROVAL_AUTHORITY_SOURCE: Final[str] = "HUMAN_LEGAL_CORPUS_APPROVAL_AUTHORITY"
APPROVAL_AUTHORITY_MECHANISM: Final[str] = "HUMAN_GOVERNED_APPROVAL_RECORD"
APPROVAL_AUTHORITY_MECHANISM_VERSION: Final[str] = "v1.0.0"
APPROVAL_SIGNING_MECHANISM: Final[str] = "EXTERNAL_GOVERNED_SIGNER"
APPROVAL_SIGNING_MECHANISM_VERSION: Final[str] = "v1.0.0"
_SHA3_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_MAX_TEXT: Final[int] = 512


class LegalCorpusApprovalAuthorityScope(StrEnum):
    """The only scope in which this authority may operate."""

    PLATFORM = APPROVAL_SCOPE


class LegalCorpusApprovalOperation(StrEnum):
    """The only operation represented by this evidence value."""

    DOCUMENT_APPROVAL = APPROVAL_OPERATION


class LegalCorpusApprovalDecision(StrEnum):
    """Closed positive decision; rejection and withdrawal are other lanes."""

    APPROVE = "APPROVE"


class LegalCorpusApprovalAuthoritySource(StrEnum):
    """Closed human-governance source; callers cannot invent authority kinds."""

    HUMAN_GOVERNED = APPROVAL_AUTHORITY_SOURCE


class LegalCorpusApprovalAuthorityMechanism(StrEnum):
    """Closed mechanism identity for the later governed approval record."""

    HUMAN_APPROVAL_RECORD = APPROVAL_AUTHORITY_MECHANISM


class LegalCorpusApprovalSigningMechanism(StrEnum):
    """Evidence metadata for an external signer, not a verifier or key store."""

    EXTERNAL_GOVERNED_SIGNER = APPROVAL_SIGNING_MECHANISM


class LegalCorpusApprovalAuthorityError(ValueError):
    """Stable non-sensitive failure for malformed or divergent evidence."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _text(value: object, code: str) -> str:
    """Require bounded text and reject control/newline injection."""
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > _MAX_TEXT:
        raise LegalCorpusApprovalAuthorityError(code)
    normalized = value.strip()
    if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
        raise LegalCorpusApprovalAuthorityError(code)
    return normalized


def _timestamp(value: object, code: str) -> datetime:
    """Require an aware datetime and normalize it to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalCorpusApprovalAuthorityError(code)
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _document_bindings(prefix: str, document: LegalDocumentVersion) -> dict[str, object]:
    """Return every immutable document field that approval evidence binds."""
    return {
        f"{prefix}_document_id": document.document_id,
        f"{prefix}_agreement_type": document.agreement_type.value,
        f"{prefix}_version": document.version,
        f"{prefix}_title": document.title,
        f"{prefix}_jurisdiction": document.jurisdiction,
        f"{prefix}_locale": document.locale,
        f"{prefix}_effective_from": _iso(document.effective_from),
        f"{prefix}_status": document.status.value,
        f"{prefix}_content_reference": document.content_reference,
        f"{prefix}_content": document.content,
        f"{prefix}_sha3_512": document.sha3_512,
        f"{prefix}_created_at": _iso(document.created_at),
        f"{prefix}_supersedes_document_id": document.supersedes_document_id,
    }


def _semantic_payload(evidence: "LegalCorpusApprovalAuthorityEvidence") -> dict[str, object]:
    """Return all semantic fields except the derived fingerprint."""
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
        "approved_at": _iso(evidence.approved_at),
        "effective_from": _iso(evidence.effective_from),
        "idempotency_key": evidence.idempotency_key,
        "provenance_reference": evidence.provenance_reference,
    }
    payload.update(_document_bindings("source", evidence.source_document))
    payload.update(_document_bindings("approved", evidence.approved_document))
    return payload


def _fingerprint(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalCorpusApprovalAuthorityEvidence:
    """Immutable evidence for one reviewed-draft to approved-version transition.

    The supplied source and approved documents are copied into the evidence
    contract as immutable semantic bindings. Construction is not authorization
    verification; no key, signature, persistence, acceptance, execution, or
    transaction operation is performed.
    """

    approval_evidence_id: str
    schema_version: str
    scope: LegalCorpusApprovalAuthorityScope
    operation: LegalCorpusApprovalOperation
    approval_decision: LegalCorpusApprovalDecision
    approval_authority_source: LegalCorpusApprovalAuthoritySource
    approval_authority_mechanism: LegalCorpusApprovalAuthorityMechanism
    approval_authority_mechanism_version: str
    human_authority_representation: str
    approval_signing_mechanism: LegalCorpusApprovalSigningMechanism
    approval_signing_mechanism_version: str
    approval_signing_key_id: str
    approval_signature_reference: str
    source_document: LegalDocumentVersion
    approved_document: LegalDocumentVersion
    approved_at: datetime
    effective_from: datetime
    idempotency_key: str
    provenance_reference: str
    evidence_fingerprint: str

    @property
    def source_document_id(self) -> str:
        """Return the exact reviewed source document identifier."""
        return self.source_document.document_id

    @property
    def source_agreement_type(self) -> LegalAgreementType:
        """Return the exact reviewed source agreement family."""
        return self.source_document.agreement_type

    @property
    def source_version(self) -> str:
        """Return the exact reviewed source version."""
        return self.source_document.version

    @property
    def source_status(self) -> LegalDocumentStatus:
        """Return the exact reviewed source lifecycle status."""
        return self.source_document.status

    @property
    def source_content_reference(self) -> str:
        """Return the exact reviewed source content reference."""
        return self.source_document.content_reference

    @property
    def source_sha3_512(self) -> str:
        """Return the exact reviewed source digest."""
        return self.source_document.sha3_512

    @property
    def approved_document_id(self) -> str:
        """Return the exact approved target document identifier."""
        return self.approved_document.document_id

    @property
    def approved_agreement_type(self) -> LegalAgreementType:
        """Return the exact approved target agreement family."""
        return self.approved_document.agreement_type

    @property
    def approved_version(self) -> str:
        """Return the exact approved target version."""
        return self.approved_document.version

    @property
    def approved_status(self) -> LegalDocumentStatus:
        """Return the exact approved target lifecycle status."""
        return self.approved_document.status

    @property
    def approved_content_reference(self) -> str:
        """Return the exact approved target content reference."""
        return self.approved_document.content_reference

    @property
    def approved_sha3_512(self) -> str:
        """Return the exact approved target digest."""
        return self.approved_document.sha3_512

    @property
    def target_document_id(self) -> str:
        """Return the approved target identifier using target terminology."""
        return self.approved_document_id

    @property
    def target_version(self) -> str:
        """Return the approved target version using target terminology."""
        return self.approved_version

    def __post_init__(self) -> None:
        """Validate all fixed authority, lifecycle, identity, and integrity rules."""
        for value, code in (
            (self.approval_evidence_id, "APPROVAL_EVIDENCE_ID_INVALID"),
            (self.schema_version, "SCHEMA_VERSION_INVALID"),
            (self.approval_authority_mechanism_version, "AUTHORITY_MECHANISM_VERSION_INVALID"),
            (self.human_authority_representation, "HUMAN_AUTHORITY_REPRESENTATION_INVALID"),
            (self.approval_signing_mechanism_version, "SIGNING_MECHANISM_VERSION_INVALID"),
            (self.approval_signing_key_id, "SIGNING_KEY_ID_INVALID"),
            (self.approval_signature_reference, "SIGNATURE_REFERENCE_INVALID"),
            (self.idempotency_key, "IDEMPOTENCY_KEY_REQUIRED"),
            (self.provenance_reference, "PROVENANCE_REFERENCE_INVALID"),
        ):
            _text(value, code)
        if not isinstance(self.scope, LegalCorpusApprovalAuthorityScope) or self.scope is not LegalCorpusApprovalAuthorityScope.PLATFORM:
            raise LegalCorpusApprovalAuthorityError("APPROVAL_SCOPE_INVALID")
        if not isinstance(self.operation, LegalCorpusApprovalOperation) or self.operation is not LegalCorpusApprovalOperation.DOCUMENT_APPROVAL:
            raise LegalCorpusApprovalAuthorityError("APPROVAL_OPERATION_INVALID")
        if not isinstance(self.approval_decision, LegalCorpusApprovalDecision) or self.approval_decision is not LegalCorpusApprovalDecision.APPROVE:
            raise LegalCorpusApprovalAuthorityError("APPROVAL_DECISION_INVALID")
        if self.schema_version != APPROVAL_EVIDENCE_SCHEMA_VERSION:
            raise LegalCorpusApprovalAuthorityError("SCHEMA_VERSION_INVALID")
        if not isinstance(self.approval_authority_source, LegalCorpusApprovalAuthoritySource) or self.approval_authority_source is not LegalCorpusApprovalAuthoritySource.HUMAN_GOVERNED:
            raise LegalCorpusApprovalAuthorityError("APPROVAL_AUTHORITY_SOURCE_INVALID")
        if not isinstance(self.approval_authority_mechanism, LegalCorpusApprovalAuthorityMechanism) or self.approval_authority_mechanism is not LegalCorpusApprovalAuthorityMechanism.HUMAN_APPROVAL_RECORD:
            raise LegalCorpusApprovalAuthorityError("APPROVAL_AUTHORITY_MECHANISM_INVALID")
        if self.approval_authority_mechanism_version != APPROVAL_AUTHORITY_MECHANISM_VERSION:
            raise LegalCorpusApprovalAuthorityError("AUTHORITY_MECHANISM_VERSION_INVALID")
        if not isinstance(self.approval_signing_mechanism, LegalCorpusApprovalSigningMechanism) or self.approval_signing_mechanism is not LegalCorpusApprovalSigningMechanism.EXTERNAL_GOVERNED_SIGNER:
            raise LegalCorpusApprovalAuthorityError("SIGNING_MECHANISM_INVALID")
        if self.approval_signing_mechanism_version != APPROVAL_SIGNING_MECHANISM_VERSION:
            raise LegalCorpusApprovalAuthorityError("SIGNING_MECHANISM_VERSION_INVALID")
        if not isinstance(self.source_document, LegalDocumentVersion) or not isinstance(self.approved_document, LegalDocumentVersion):
            raise LegalCorpusApprovalAuthorityError("DOCUMENT_BINDING_INVALID")
        if self.source_document.agreement_type not in _ELIGIBLE_FAMILIES:
            raise LegalCorpusApprovalAuthorityError("APPROVAL_FAMILY_NOT_ELIGIBLE")
        if self.source_document.status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            raise LegalCorpusApprovalAuthorityError("SOURCE_NOT_REVIEWED_DRAFT")
        if self.approved_document.status is not LegalDocumentStatus.APPROVED:
            raise LegalCorpusApprovalAuthorityError("TARGET_NOT_APPROVED")
        _timestamp(self.approved_at, "APPROVED_AT_INVALID")
        _timestamp(self.effective_from, "EFFECTIVE_FROM_INVALID")
        if _SHA3_HEX.fullmatch(self.evidence_fingerprint) is None:
            raise LegalCorpusApprovalAuthorityError("EVIDENCE_FINGERPRINT_INVALID")
        normalized_approved_at = _timestamp(self.approved_at, "APPROVED_AT_INVALID")
        normalized_effective_from = _timestamp(self.effective_from, "EFFECTIVE_FROM_INVALID")
        object.__setattr__(self, "approval_evidence_id", self.approval_evidence_id.strip())
        object.__setattr__(self, "schema_version", self.schema_version.strip())
        object.__setattr__(self, "approval_authority_mechanism_version", self.approval_authority_mechanism_version.strip())
        object.__setattr__(self, "human_authority_representation", self.human_authority_representation.strip())
        object.__setattr__(self, "approval_signing_mechanism_version", self.approval_signing_mechanism_version.strip())
        object.__setattr__(self, "approval_signing_key_id", self.approval_signing_key_id.strip())
        object.__setattr__(self, "approval_signature_reference", self.approval_signature_reference.strip())
        object.__setattr__(self, "idempotency_key", self.idempotency_key.strip())
        object.__setattr__(self, "provenance_reference", self.provenance_reference.strip())
        object.__setattr__(self, "approved_at", normalized_approved_at)
        object.__setattr__(self, "effective_from", normalized_effective_from)
        self._verify_transition()
        if _fingerprint(_semantic_payload(self)) != self.evidence_fingerprint:
            raise LegalCorpusApprovalAuthorityError("EVIDENCE_FINGERPRINT_MISMATCH")

    @classmethod
    def fingerprint_for(
        cls,
        *,
        approval_evidence_id: str,
        schema_version: str,
        scope: LegalCorpusApprovalAuthorityScope,
        operation: LegalCorpusApprovalOperation,
        approval_decision: LegalCorpusApprovalDecision,
        approval_authority_source: LegalCorpusApprovalAuthoritySource,
        approval_authority_mechanism: LegalCorpusApprovalAuthorityMechanism,
        approval_authority_mechanism_version: str,
        human_authority_representation: str,
        approval_signing_mechanism: LegalCorpusApprovalSigningMechanism,
        approval_signing_mechanism_version: str,
        approval_signing_key_id: str,
        approval_signature_reference: str,
        source_document: LegalDocumentVersion,
        approved_document: LegalDocumentVersion,
        approved_at: datetime,
        effective_from: datetime,
        idempotency_key: str,
        provenance_reference: str,
    ) -> str:
        """Compute canonical fingerprint from complete evidence fields only."""
        try:
            evidence = cls(
                approval_evidence_id=approval_evidence_id,
                schema_version=schema_version,
                scope=scope,
                operation=operation,
                approval_decision=approval_decision,
                approval_authority_source=approval_authority_source,
                approval_authority_mechanism=approval_authority_mechanism,
                approval_authority_mechanism_version=approval_authority_mechanism_version,
                human_authority_representation=human_authority_representation,
                approval_signing_mechanism=approval_signing_mechanism,
                approval_signing_mechanism_version=approval_signing_mechanism_version,
                approval_signing_key_id=approval_signing_key_id,
                approval_signature_reference=approval_signature_reference,
                source_document=source_document,
                approved_document=approved_document,
                approved_at=approved_at,
                effective_from=effective_from,
                idempotency_key=idempotency_key,
                provenance_reference=provenance_reference,
                evidence_fingerprint="0" * 128,
            )
        except LegalCorpusApprovalAuthorityError as error:
            if error.code != "EVIDENCE_FINGERPRINT_MISMATCH":
                raise
            payload: dict[str, object] = {
                "approval_evidence_id": approval_evidence_id,
                "schema_version": schema_version,
                "scope": scope.value,
                "operation": operation.value,
                "approval_decision": approval_decision.value,
                "approval_authority_source": approval_authority_source.value,
                "approval_authority_mechanism": approval_authority_mechanism.value,
                "approval_authority_mechanism_version": approval_authority_mechanism_version,
                "human_authority_representation": human_authority_representation,
                "approval_signing_mechanism": approval_signing_mechanism.value,
                "approval_signing_mechanism_version": approval_signing_mechanism_version,
                "approval_signing_key_id": approval_signing_key_id,
                "approval_signature_reference": approval_signature_reference,
                "approved_at": _iso(_timestamp(approved_at, "APPROVED_AT_INVALID")),
                "effective_from": _iso(_timestamp(effective_from, "EFFECTIVE_FROM_INVALID")),
                "idempotency_key": idempotency_key,
                "provenance_reference": provenance_reference,
            }
            payload.update(_document_bindings("source", source_document))
            payload.update(_document_bindings("approved", approved_document))
            return _fingerprint(payload)
        else:
            return _fingerprint(_semantic_payload(evidence))

    def _verify_transition(self) -> None:
        """Enforce the proven immutable source-to-target succession relation."""
        if self.source_document.document_id != self.approved_document.document_id:
            raise LegalCorpusApprovalAuthorityError("DOCUMENT_ID_SUCCESSION_INVALID")
        if self.source_document.agreement_type is not self.approved_document.agreement_type:
            raise LegalCorpusApprovalAuthorityError("AGREEMENT_TYPE_SUCCESSION_INVALID")
        if self.source_document.version == self.approved_document.version:
            raise LegalCorpusApprovalAuthorityError("VERSION_SUCCESSION_INVALID")
        if self.approved_document.supersedes_document_id != self.source_document.document_id:
            raise LegalCorpusApprovalAuthorityError("SUPERSESSION_INVALID")
        if self.source_document.content != self.approved_document.content:
            raise LegalCorpusApprovalAuthorityError("REVIEWED_PROSE_DRIFT")
        if self.effective_from != _timestamp(self.approved_document.effective_from, "TARGET_EFFECTIVE_FROM_INVALID"):
            raise LegalCorpusApprovalAuthorityError("EFFECTIVE_FROM_MISMATCH")

    def verify_against(self, source_document: LegalDocumentVersion, approved_document: LegalDocumentVersion) -> None:
        """Require exact source/target bindings and the governed transition."""
        if not isinstance(source_document, LegalDocumentVersion) or not isinstance(approved_document, LegalDocumentVersion):
            raise LegalCorpusApprovalAuthorityError("DOCUMENT_BINDING_INVALID")
        if source_document != self.source_document:
            raise LegalCorpusApprovalAuthorityError("SOURCE_DOCUMENT_MISMATCH")
        if approved_document != self.approved_document:
            raise LegalCorpusApprovalAuthorityError("TARGET_DOCUMENT_MISMATCH")
        self._verify_transition()

    def to_document(self) -> dict[str, Any]:
        """Serialize complete immutable evidence using deterministic primitives."""
        payload = _semantic_payload(self)
        payload["evidence_fingerprint"] = self.evidence_fingerprint
        return payload


_ELIGIBLE_FAMILIES: Final[frozenset[LegalAgreementType]] = frozenset(
    {
        LegalAgreementType.INSTITUTIONAL_CHARTER,
        LegalAgreementType.USER_TERMS,
        LegalAgreementType.ACCEPTABLE_USE,
        LegalAgreementType.PRIVACY_NOTICE,
        LegalAgreementType.AI_ASSISTANCE_NOTICE,
        LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE,
    }
)


__all__ = [
    "APPROVAL_EVIDENCE_SCHEMA_VERSION",
    "APPROVAL_AUTHORITY_MECHANISM",
    "APPROVAL_AUTHORITY_MECHANISM_VERSION",
    "APPROVAL_AUTHORITY_SOURCE",
    "APPROVAL_OPERATION",
    "APPROVAL_SCOPE",
    "APPROVAL_SIGNING_MECHANISM",
    "APPROVAL_SIGNING_MECHANISM_VERSION",
    "LegalCorpusApprovalAuthorityError",
    "LegalCorpusApprovalAuthorityMechanism",
    "LegalCorpusApprovalAuthorityScope",
    "LegalCorpusApprovalAuthoritySource",
    "LegalCorpusApprovalDecision",
    "LegalCorpusApprovalOperation",
    "LegalCorpusApprovalSigningMechanism",
    "LegalCorpusApprovalAuthorityEvidence",
    "VERSION",
]


# ARTIFACT: legal_corpus_approval_authority.py
# VERSION: v1.0.0-R1D-B0F-B4-R9B-P1-LEGAL-CORPUS-APPROVAL-AUTHORITY
# AUTHORITY BOUNDARY: immutable approval-evidence representation and verification only
# TENANT POSTURE: PLATFORM scope; tenant/principal acceptance remains separate
# FAIL-CLOSED POSTURE: malformed, divergent, or non-approved transitions reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
