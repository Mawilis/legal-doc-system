"""WILSY OS versioned legal-document and acceptance contracts.

TITLE: WILSY OS Legal Acceptance Domain
VERSION: v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Defines immutable document versions, acceptance evidence, and bounded
         status vocabularies without creating corporate-signatory authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_acceptance.py
COLLABORATION / OWNERSHIP: Document registry owns document truth; acceptance
                            registry owns evidence; policy/service compose them.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE establishes strict,
           deterministic immutable document and acceptance value objects.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Content is server-selected; client claims never
                            become document, tenant, principal, or authority truth.
TENANT BOUNDARY: Acceptance evidence always carries the authenticated tenant
                 and principal; cross-tenant evidence is rejected.
AUTHORITY BOUNDARY: Acknowledgement and acceptance evidence only; no authority
                    to bind an organisation, execute a contract, or transact.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final


VERSION: Final[str] = "v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE"
SHA3_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class LegalAcceptanceError(ValueError):
    """Base fail-closed legal-document or acceptance error."""


class LegalDocumentStatus(StrEnum):
    """Lifecycle status; only APPROVED can satisfy a production requirement."""

    DRAFT_REVIEW_REQUIRED = "DRAFT_REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    RETIRED = "RETIRED"


class LegalAgreementType(StrEnum):
    """Supported document families, including future commercial families."""

    INSTITUTIONAL_CHARTER = "INSTITUTIONAL_CHARTER"
    USER_TERMS = "USER_TERMS"
    ACCEPTABLE_USE = "ACCEPTABLE_USE"
    PRIVACY_NOTICE = "PRIVACY_NOTICE"
    AI_ASSISTANCE_NOTICE = "AI_ASSISTANCE_NOTICE"
    ADMIN_RESPONSIBILITY_NOTICE = "ADMIN_RESPONSIBILITY_NOTICE"
    MASTER_SUBSCRIPTION_AGREEMENT = "MASTER_SUBSCRIPTION_AGREEMENT"
    ORDER_FORM = "ORDER_FORM"
    DATA_PROCESSING_AGREEMENT = "DATA_PROCESSING_AGREEMENT"
    SECURITY_SLA_SCHEDULE = "SECURITY_SLA_SCHEDULE"
    PRODUCT_ADDENDUM = "PRODUCT_ADDENDUM"


class LegalAcceptanceStatus(StrEnum):
    """Server-derived acceptance plan result."""

    COMPLETE = "COMPLETE"
    USER_TERMS_REQUIRED = "USER_TERMS_REQUIRED"
    ADMIN_ACK_REQUIRED = "ADMIN_ACK_REQUIRED"
    OWNER_AGREEMENTS_REQUIRED = "OWNER_AGREEMENTS_REQUIRED"
    MATERIAL_REACCEPTANCE_REQUIRED = "MATERIAL_REACCEPTANCE_REQUIRED"
    DOCUMENT_APPROVAL_REQUIRED = "DOCUMENT_APPROVAL_REQUIRED"


class AcceptanceMethod(StrEnum):
    """Non-signature methods available to authenticated users."""

    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
    ACCEPTANCE = "ACCEPTANCE"


def _text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LegalAcceptanceError(code)
    return value.strip()


def _timestamp(value: object, code: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalAcceptanceError(code)
    return value.astimezone(timezone.utc)


def canonical_document_digest(content: str, content_reference: str) -> str:
    """Hash the complete immutable document payload deterministically."""
    payload = json.dumps(
        {"content": _text(content, "LEGAL_DOCUMENT_CONTENT_INVALID"),
         "content_reference": _text(content_reference, "LEGAL_DOCUMENT_REFERENCE_INVALID")},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha3_512(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalDocumentVersion:
    """Immutable server-owned document/version authority record."""

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
    supersedes_document_id: str | None = None

    def __post_init__(self) -> None:
        for value, code in (
            (self.document_id, "LEGAL_DOCUMENT_ID_INVALID"),
            (self.version, "LEGAL_DOCUMENT_VERSION_INVALID"),
            (self.title, "LEGAL_DOCUMENT_TITLE_INVALID"),
            (self.jurisdiction, "LEGAL_DOCUMENT_JURISDICTION_INVALID"),
            (self.locale, "LEGAL_DOCUMENT_LOCALE_INVALID"),
            (self.content_reference, "LEGAL_DOCUMENT_REFERENCE_INVALID"),
            (self.content, "LEGAL_DOCUMENT_CONTENT_INVALID"),
        ):
            _text(value, code)
        if not isinstance(self.agreement_type, LegalAgreementType):
            raise LegalAcceptanceError("LEGAL_DOCUMENT_AGREEMENT_TYPE_INVALID")
        if not isinstance(self.status, LegalDocumentStatus):
            raise LegalAcceptanceError("LEGAL_DOCUMENT_STATUS_INVALID")
        _timestamp(self.effective_from, "LEGAL_DOCUMENT_EFFECTIVE_FROM_INVALID")
        _timestamp(self.created_at, "LEGAL_DOCUMENT_CREATED_AT_INVALID")
        if SHA3_HEX.fullmatch(self.sha3_512) is None:
            raise LegalAcceptanceError("LEGAL_DOCUMENT_DIGEST_INVALID")
        if self.sha3_512 != canonical_document_digest(self.content, self.content_reference):
            raise LegalAcceptanceError("LEGAL_DOCUMENT_DIGEST_MISMATCH")
        if self.supersedes_document_id is not None:
            _text(self.supersedes_document_id, "LEGAL_DOCUMENT_SUPERSESSION_INVALID")

    def to_document(self) -> dict[str, Any]:
        """Serialize every immutable field; no update path is provided."""
        return {
            "document_id": self.document_id,
            "agreement_type": self.agreement_type.value,
            "version": self.version,
            "title": self.title,
            "jurisdiction": self.jurisdiction,
            "locale": self.locale,
            "effective_from": self.effective_from.isoformat(),
            "status": self.status.value,
            "content_reference": self.content_reference,
            "content": self.content,
            "sha3_512": self.sha3_512,
            "created_at": self.created_at.isoformat(),
            "supersedes_document_id": self.supersedes_document_id,
        }


@dataclass(frozen=True, slots=True)
class LegalAcceptanceEvidence:
    """Append-only evidence that one authenticated principal accepted one version."""

    acceptance_id: str
    tenant_id: str
    principal_id: str
    agreement_type: LegalAgreementType
    document_id: str
    document_version: str
    document_sha3_512: str
    accepted_at: datetime
    acceptance_method: AcceptanceMethod
    actor_role_at_acceptance: str
    session_id: str
    locale: str
    authority_representation: str
    evidence_fingerprint: str
    supersedes_acceptance_id: str | None = None
    idempotency_key: str | None = None

    def __post_init__(self) -> None:
        for value, code in (
            (self.acceptance_id, "LEGAL_ACCEPTANCE_ID_INVALID"),
            (self.tenant_id, "LEGAL_ACCEPTANCE_TENANT_INVALID"),
            (self.principal_id, "LEGAL_ACCEPTANCE_PRINCIPAL_INVALID"),
            (self.document_id, "LEGAL_ACCEPTANCE_DOCUMENT_INVALID"),
            (self.document_version, "LEGAL_ACCEPTANCE_VERSION_INVALID"),
            (self.actor_role_at_acceptance, "LEGAL_ACCEPTANCE_ROLE_INVALID"),
            (self.session_id, "LEGAL_ACCEPTANCE_SESSION_INVALID"),
            (self.locale, "LEGAL_ACCEPTANCE_LOCALE_INVALID"),
            (self.authority_representation, "LEGAL_ACCEPTANCE_AUTHORITY_INVALID"),
        ):
            _text(value, code)
        for value, code in ((self.tenant_id, "LEGAL_ACCEPTANCE_TENANT_INVALID"), (self.principal_id, "LEGAL_ACCEPTANCE_PRINCIPAL_INVALID")):
            if IDENTITY.fullmatch(value) is None:
                raise LegalAcceptanceError(code)
        if not isinstance(self.agreement_type, LegalAgreementType):
            raise LegalAcceptanceError("LEGAL_ACCEPTANCE_AGREEMENT_TYPE_INVALID")
        if not isinstance(self.acceptance_method, AcceptanceMethod):
            raise LegalAcceptanceError("LEGAL_ACCEPTANCE_METHOD_INVALID")
        _timestamp(self.accepted_at, "LEGAL_ACCEPTANCE_TIMESTAMP_INVALID")
        if SHA3_HEX.fullmatch(self.document_sha3_512) is None or SHA3_HEX.fullmatch(self.evidence_fingerprint) is None:
            raise LegalAcceptanceError("LEGAL_ACCEPTANCE_DIGEST_INVALID")
        if self.supersedes_acceptance_id is not None:
            _text(self.supersedes_acceptance_id, "LEGAL_ACCEPTANCE_SUPERSESSION_INVALID")

    @staticmethod
    def fingerprint_payload(
        *, tenant_id: str, principal_id: str, agreement_type: LegalAgreementType,
        document_id: str, document_version: str, document_sha3_512: str,
        acceptance_method: AcceptanceMethod, locale: str,
    ) -> str:
        """Compute deterministic evidence identity over semantic acceptance fields."""
        payload = {
            "tenant_id": tenant_id, "principal_id": principal_id,
            "agreement_type": agreement_type.value, "document_id": document_id,
            "document_version": document_version, "document_sha3_512": document_sha3_512,
            "acceptance_method": acceptance_method.value, "locale": locale,
        }
        return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def to_document(self) -> dict[str, Any]:
        """Serialize immutable evidence for append-only persistence."""
        return {
            "acceptance_id": self.acceptance_id, "tenant_id": self.tenant_id,
            "principal_id": self.principal_id, "agreement_type": self.agreement_type.value,
            "document_id": self.document_id, "document_version": self.document_version,
            "document_sha3_512": self.document_sha3_512, "accepted_at": self.accepted_at.isoformat(),
            "acceptance_method": self.acceptance_method.value,
            "actor_role_at_acceptance": self.actor_role_at_acceptance,
            "session_id": self.session_id, "locale": self.locale,
            "authority_representation": self.authority_representation,
            "evidence_fingerprint": self.evidence_fingerprint,
            "supersedes_acceptance_id": self.supersedes_acceptance_id,
            "idempotency_key": self.idempotency_key,
        }


__all__ = [
    "AcceptanceMethod", "LegalAcceptanceError", "LegalAcceptanceEvidence",
    "LegalAcceptanceStatus", "LegalAgreementType", "LegalDocumentStatus",
    "LegalDocumentVersion", "VERSION", "canonical_document_digest",
]

# ARTIFACT: legal_acceptance.py
# VERSION: v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE
# AUTHORITY BOUNDARY: immutable document and acceptance value contracts only
# TENANT POSTURE: tenant/principal are explicit and validated; no transport authority
# FAIL-CLOSED POSTURE: malformed, divergent, or unapproved evidence is rejected
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
