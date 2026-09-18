"""Immutable authority evidence for admitting one legal-corpus draft.

TITLE: WILSY OS Legal Corpus Provisioning Authority Domain
VERSION: v1.0.0-R1D-B0F-B4-R8D-LEGAL-CORPUS-PROVISIONING-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Represents one explicit, digest-bound platform authorization to
         admit an exact server-owned legal-document draft. The value is
         forensic evidence only; it never persists or grants authority itself.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_corpus_provisioning_authority.py
COLLABORATION / OWNERSHIP: The future governed operator/deployment command
                           issues evidence; the future provisioning service
                           verifies it and composes the document registry.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R8D defines immutable PLATFORM draft-admission evidence,
           canonical SHA3-512 fingerprinting, and exact source verification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only opaque identifiers and an actor
                            representation are retained; secrets are rejected
                            by the caller and never required here.
TENANT BOUNDARY: PLATFORM corpus authority is intentionally tenant-neutral;
                 tenant/principal scope belongs to later acceptance evidence.
AUTHORITY BOUNDARY: Evidence representation and source matching only; object
                    construction is not authorization, review, approval,
                    acceptance, signature, or execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
TRANSACTION BOUNDARY: No database, session, transaction, network, or HTTP
                      ownership exists in this pure domain artifact.
FAIL-CLOSED POSTURE: Invalid scope, operation, source status, timestamps,
                     digests, fingerprints, or source mismatches are rejected.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
)


VERSION: Final[str] = "v1.0.0-R1D-B0F-B4-R8D-LEGAL-CORPUS-PROVISIONING-AUTHORITY"
AUTHORITY_SCOPE: Final[str] = "PLATFORM"
AUTHORIZED_OPERATION: Final[str] = "LEGAL_CORPUS_DRAFT_ADMISSION"
AUTHORITY_SOURCE_ID: Final[str] = "DEPLOYMENT_OPERATOR_LEGAL_CORPUS_ADMISSION"
AUTHORITY_SOURCE_VERSION: Final[str] = "v1.0.0"
_SHA3_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class LegalCorpusProvisioningAuthorityScope(StrEnum):
    """Non-tenant scope available to the corpus-admission authority."""

    PLATFORM = AUTHORITY_SCOPE


class LegalCorpusProvisioningOperation(StrEnum):
    """The only legal-corpus mutation operation authorized at this phase."""

    DRAFT_ADMISSION = AUTHORIZED_OPERATION


class LegalCorpusProvisioningAuthoritySource(StrEnum):
    """Fixed authority-source identity; callers cannot invent authority kinds."""

    DEPLOYMENT_OPERATOR = AUTHORITY_SOURCE_ID


class LegalCorpusProvisioningAuthorityError(ValueError):
    """Stable, non-sensitive failure raised for invalid authority evidence."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _text(value: object, code: str) -> str:
    """Require bounded, non-empty text without accepting line-control data."""
    if not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value:
        raise LegalCorpusProvisioningAuthorityError(code)
    return value.strip()


def _timestamp(value: object, code: str) -> datetime:
    """Require an aware timestamp and normalize it to UTC for canonical bytes."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalCorpusProvisioningAuthorityError(code)
    return value.astimezone(timezone.utc)


def _semantic_payload(
    *,
    authority_evidence_id: str,
    scope: LegalCorpusProvisioningAuthorityScope,
    operation: LegalCorpusProvisioningOperation,
    source_document_id: str,
    source_agreement_type: LegalAgreementType,
    source_version: str,
    source_status: LegalDocumentStatus,
    source_content_reference: str,
    source_sha3_512: str,
    authority_source_id: LegalCorpusProvisioningAuthoritySource,
    authority_source_version: str,
    actor_representation: str,
    authorized_at: datetime,
    idempotency_key: str,
) -> dict[str, str]:
    """Return every authority-bearing field except the derived fingerprint."""
    return {
        "authority_evidence_id": authority_evidence_id,
        "scope": scope.value,
        "operation": operation.value,
        "source_document_id": source_document_id,
        "source_agreement_type": source_agreement_type.value,
        "source_version": source_version,
        "source_status": source_status.value,
        "source_content_reference": source_content_reference,
        "source_sha3_512": source_sha3_512,
        "authority_source_id": authority_source_id.value,
        "authority_source_version": authority_source_version,
        "actor_representation": actor_representation,
        "authorized_at": authorized_at.astimezone(timezone.utc).isoformat(),
        "idempotency_key": idempotency_key,
    }


def _fingerprint(payload: dict[str, str]) -> str:
    """Hash canonical JSON bytes without Python representation dependence."""
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalCorpusProvisioningAuthorityEvidence:
    """Immutable evidence authorizing admission of one exact legal draft.

    Construction is deliberately not an issuing authority. A later explicit
    operator/deployment command must establish the external authorization and
    then provide this already-bound value to the provisioning service. This
    object performs no persistence, registry lookup, approval, acceptance,
    signature, commercial execution, payment, or settlement operation.
    """

    authority_evidence_id: str
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
    idempotency_key: str
    evidence_fingerprint: str

    def __post_init__(self) -> None:
        """Validate the complete immutable authority-evidence contract."""
        authority_id = _text(self.authority_evidence_id, "AUTHORITY_EVIDENCE_ID_INVALID")
        source_document_id = _text(self.source_document_id, "SOURCE_DOCUMENT_ID_INVALID")
        source_version = _text(self.source_version, "SOURCE_VERSION_INVALID")
        source_reference = _text(self.source_content_reference, "SOURCE_REFERENCE_INVALID")
        source_authority_version = _text(self.authority_source_version, "AUTHORITY_SOURCE_VERSION_INVALID")
        actor = _text(self.actor_representation, "ACTOR_REPRESENTATION_INVALID")
        idempotency = _text(self.idempotency_key, "IDEMPOTENCY_KEY_REQUIRED")
        if not isinstance(self.scope, LegalCorpusProvisioningAuthorityScope) or self.scope is not LegalCorpusProvisioningAuthorityScope.PLATFORM:
            raise LegalCorpusProvisioningAuthorityError("AUTHORITY_SCOPE_INVALID")
        if not isinstance(self.operation, LegalCorpusProvisioningOperation) or self.operation is not LegalCorpusProvisioningOperation.DRAFT_ADMISSION:
            raise LegalCorpusProvisioningAuthorityError("AUTHORIZED_OPERATION_INVALID")
        if not isinstance(self.source_agreement_type, LegalAgreementType):
            raise LegalCorpusProvisioningAuthorityError("SOURCE_AGREEMENT_TYPE_INVALID")
        if not isinstance(self.source_status, LegalDocumentStatus):
            raise LegalCorpusProvisioningAuthorityError("SOURCE_STATUS_INVALID")
        if self.source_status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            raise LegalCorpusProvisioningAuthorityError("NON_DRAFT_SOURCE_STATUS")
        if not isinstance(self.authority_source_id, LegalCorpusProvisioningAuthoritySource):
            raise LegalCorpusProvisioningAuthorityError("AUTHORITY_SOURCE_INVALID")
        if source_authority_version != AUTHORITY_SOURCE_VERSION:
            raise LegalCorpusProvisioningAuthorityError("AUTHORITY_SOURCE_VERSION_INVALID")
        if _SHA3_HEX.fullmatch(self.source_sha3_512) is None:
            raise LegalCorpusProvisioningAuthorityError("SOURCE_SHA3_512_INVALID")
        if _SHA3_HEX.fullmatch(self.evidence_fingerprint) is None:
            raise LegalCorpusProvisioningAuthorityError("EVIDENCE_FINGERPRINT_INVALID")
        normalized_timestamp = _timestamp(self.authorized_at, "AUTHORIZED_AT_INVALID")
        object.__setattr__(self, "authority_evidence_id", authority_id)
        object.__setattr__(self, "source_document_id", source_document_id)
        object.__setattr__(self, "source_version", source_version)
        object.__setattr__(self, "source_content_reference", source_reference)
        object.__setattr__(self, "authority_source_version", source_authority_version)
        object.__setattr__(self, "actor_representation", actor)
        object.__setattr__(self, "idempotency_key", idempotency)
        object.__setattr__(self, "authorized_at", normalized_timestamp)
        expected = self.fingerprint_for(
            authority_evidence_id=authority_id,
            scope=self.scope,
            operation=self.operation,
            source_document_id=source_document_id,
            source_agreement_type=self.source_agreement_type,
            source_version=source_version,
            source_status=self.source_status,
            source_content_reference=source_reference,
            source_sha3_512=self.source_sha3_512,
            authority_source_id=self.authority_source_id,
            authority_source_version=source_authority_version,
            actor_representation=actor,
            authorized_at=normalized_timestamp,
            idempotency_key=idempotency,
        )
        if expected != self.evidence_fingerprint:
            raise LegalCorpusProvisioningAuthorityError("EVIDENCE_FINGERPRINT_MISMATCH")

    @staticmethod
    def fingerprint_for(
        *,
        authority_evidence_id: str,
        scope: LegalCorpusProvisioningAuthorityScope,
        operation: LegalCorpusProvisioningOperation,
        source_document_id: str,
        source_agreement_type: LegalAgreementType,
        source_version: str,
        source_status: LegalDocumentStatus,
        source_content_reference: str,
        source_sha3_512: str,
        authority_source_id: LegalCorpusProvisioningAuthoritySource,
        authority_source_version: str,
        actor_representation: str,
        authorized_at: datetime,
        idempotency_key: str,
    ) -> str:
        """Compute the deterministic fingerprint; computation grants no authority."""
        if not isinstance(scope, LegalCorpusProvisioningAuthorityScope) or scope is not LegalCorpusProvisioningAuthorityScope.PLATFORM:
            raise LegalCorpusProvisioningAuthorityError("AUTHORITY_SCOPE_INVALID")
        if not isinstance(operation, LegalCorpusProvisioningOperation) or operation is not LegalCorpusProvisioningOperation.DRAFT_ADMISSION:
            raise LegalCorpusProvisioningAuthorityError("AUTHORIZED_OPERATION_INVALID")
        if not isinstance(source_agreement_type, LegalAgreementType):
            raise LegalCorpusProvisioningAuthorityError("SOURCE_AGREEMENT_TYPE_INVALID")
        if not isinstance(source_status, LegalDocumentStatus):
            raise LegalCorpusProvisioningAuthorityError("SOURCE_STATUS_INVALID")
        if source_status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            raise LegalCorpusProvisioningAuthorityError("NON_DRAFT_SOURCE_STATUS")
        if not isinstance(authority_source_id, LegalCorpusProvisioningAuthoritySource):
            raise LegalCorpusProvisioningAuthorityError("AUTHORITY_SOURCE_INVALID")
        if authority_source_version != AUTHORITY_SOURCE_VERSION:
            raise LegalCorpusProvisioningAuthorityError("AUTHORITY_SOURCE_VERSION_INVALID")
        if _SHA3_HEX.fullmatch(source_sha3_512) is None:
            raise LegalCorpusProvisioningAuthorityError("SOURCE_SHA3_512_INVALID")
        normalized_timestamp = _timestamp(authorized_at, "AUTHORIZED_AT_INVALID")
        payload = _semantic_payload(
            authority_evidence_id=_text(authority_evidence_id, "AUTHORITY_EVIDENCE_ID_INVALID"),
            scope=scope,
            operation=operation,
            source_document_id=_text(source_document_id, "SOURCE_DOCUMENT_ID_INVALID"),
            source_agreement_type=source_agreement_type,
            source_version=_text(source_version, "SOURCE_VERSION_INVALID"),
            source_status=source_status,
            source_content_reference=_text(source_content_reference, "SOURCE_REFERENCE_INVALID"),
            source_sha3_512=source_sha3_512,
            authority_source_id=authority_source_id,
            authority_source_version=_text(authority_source_version, "AUTHORITY_SOURCE_VERSION_INVALID"),
            actor_representation=_text(actor_representation, "ACTOR_REPRESENTATION_INVALID"),
            authorized_at=normalized_timestamp,
            idempotency_key=_text(idempotency_key, "IDEMPOTENCY_KEY_REQUIRED"),
        )
        return _fingerprint(payload)

    def verify_against(self, document: LegalDocumentVersion) -> None:
        """Require exact binding to one canonical, still-draft document value."""
        if not isinstance(document, LegalDocumentVersion):
            raise LegalCorpusProvisioningAuthorityError("SOURCE_DOCUMENT_INVALID")
        if document.status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            raise LegalCorpusProvisioningAuthorityError("NON_DRAFT_SOURCE_STATUS")
        bindings = (
            (self.source_document_id, document.document_id),
            (self.source_agreement_type, document.agreement_type),
            (self.source_version, document.version),
            (self.source_status, document.status),
            (self.source_content_reference, document.content_reference),
            (self.source_sha3_512, document.sha3_512),
        )
        if any(expected != actual for expected, actual in bindings):
            raise LegalCorpusProvisioningAuthorityError("SOURCE_DOCUMENT_MISMATCH")

    def to_document(self) -> dict[str, str]:
        """Serialize the complete immutable evidence using stable primitives."""
        return {
            "authority_evidence_id": self.authority_evidence_id,
            "scope": self.scope.value,
            "operation": self.operation.value,
            "source_document_id": self.source_document_id,
            "source_agreement_type": self.source_agreement_type.value,
            "source_version": self.source_version,
            "source_status": self.source_status.value,
            "source_content_reference": self.source_content_reference,
            "source_sha3_512": self.source_sha3_512,
            "authority_source_id": self.authority_source_id.value,
            "authority_source_version": self.authority_source_version,
            "actor_representation": self.actor_representation,
            "authorized_at": self.authorized_at.isoformat(),
            "idempotency_key": self.idempotency_key,
            "evidence_fingerprint": self.evidence_fingerprint,
        }


__all__ = [
    "AUTHORIZED_OPERATION",
    "AUTHORITY_SCOPE",
    "AUTHORITY_SOURCE_ID",
    "AUTHORITY_SOURCE_VERSION",
    "LegalCorpusProvisioningAuthorityError",
    "LegalCorpusProvisioningAuthorityEvidence",
    "LegalCorpusProvisioningAuthorityScope",
    "LegalCorpusProvisioningAuthoritySource",
    "LegalCorpusProvisioningOperation",
    "VERSION",
]


# ARTIFACT: legal_corpus_provisioning_authority.py
# VERSION: v1.0.0-R1D-B0F-B4-R8D-LEGAL-CORPUS-PROVISIONING-AUTHORITY
# AUTHORITY BOUNDARY: immutable draft-admission evidence representation only
# TENANT POSTURE: PLATFORM scope; tenant acceptance remains separate
# FAIL-CLOSED POSTURE: invalid or divergent authority/source data is rejected
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
