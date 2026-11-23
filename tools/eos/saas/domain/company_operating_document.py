"""TITLE: WILSY OS Company Operating Document Lifecycle.
VERSION: v1.1.0-EXPLICIT-FOUNDER-STRATEGY-RATIFICATION
AUTHORITY: Pure immutable company-document lifecycle; HTTP IAM owns admission.
EPITOME: Distinguishes prepared, submitted and independently approved published
Mission/Strategy revisions without inventing company policy or Founder sign-off.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/company_operating_document.py
COLLABORATION / OWNERSHIP: CompanyOperatingDocumentRegistry persists revisions;
company_operating_document_router reauthorizes exact company-tenant commands.
CERTIFICATION / UPDATE DATE: 2026-11-13
CHANGELOG: v1.1.0-EXPLICIT-FOUNDER-STRATEGY-RATIFICATION permits
Strategy-only same-actor ratification under one server-owned immutable
reference; HTTP and registry must verify durable Founder source authority.
All other document/approval combinations remain independently published.
CHANGELOG: v1.0.0-COMPANY-MISSION-STRATEGY-LIFECYCLE establishes bounded text,
immutable revisions, deterministic SHA3-512 evidence and independent publication.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Plain text only; no executable markup, logging,
credentials, inferred objectives, budgets, progress or generated policy.
TENANT BOUNDARY: Exact canonical WILSY company tenant only; no tenant fallback.
AUTHORITY BOUNDARY: Domain validation does not grant permission; source IAM must
admit each caller. Approval is the separately authorized publisher's decision.
FINANCIAL AUTHORITY BOUNDARY: No execution, accounting or settlement authority.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
from hmac import compare_digest
import json
import re
from typing import Any, Final, Mapping

from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID

VERSION: Final = "v1.1.0-EXPLICIT-FOUNDER-STRATEGY-RATIFICATION"
SCHEMA: Final = "WILSY-COMPANY-OPERATING-DOCUMENT/V1"
MAX_SECTIONS: Final = 24
MAX_CONTENT: Final = 100_000
FOUNDER_RATIFICATION_REFERENCE: Final = "WILSY-INSTITUTIONAL-FOUNDER-SELF-RATIFICATION-20261123"


class CompanyDocumentError(ValueError):
    """Stable validation/lifecycle failure; no authority or mutation is issued."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class CompanyDocumentClass(StrEnum):
    """Closed company-document classifications, never generic legal agreements."""

    MISSION = "MISSION"
    STRATEGY = "STRATEGY"


class CompanyDocumentState(StrEnum):
    """Preparation is distinct from submission and independent publication."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PUBLISHED = "PUBLISHED"


def _text(value: object, limit: int, code: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit or "\x00" in value:
        raise CompanyDocumentError(code)
    return value


def instant(value: str | datetime) -> str:
    """Return one UTC millisecond instant; naive or malformed time fails closed.

    Serialization is deterministic and matches Mongo's timestamp precision.
    No time is inferred for a missing publication date.
    """
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value
        if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("aware time required")
        return parsed.astimezone(timezone.utc).isoformat(timespec="milliseconds")
    except (TypeError, ValueError, OverflowError) as error:
        raise CompanyDocumentError("COMPANY_DOCUMENT_TIME_INVALID") from error


def semantic_fingerprint(payload: Mapping[str, Any]) -> str:
    """Hash the defined semantic payload using canonical JSON and SHA3-512.

    Mongo _id, bearer, transport correlation and latency are deliberately absent.
    This evidence proves payload integrity, not IAM possession or a signature.
    """
    try:
        canonical = json.dumps(dict(payload), sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as error:
        raise CompanyDocumentError("COMPANY_DOCUMENT_SERIALIZATION_INVALID") from error
    return sha3_512(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class CompanyDocumentSection:
    """Immutable plain-text section; navigation identifiers never execute markup."""

    section_id: str
    title: str
    body: str

    def __post_init__(self) -> None:
        if not isinstance(self.section_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", self.section_id):
            raise CompanyDocumentError("COMPANY_DOCUMENT_SECTION_ID_INVALID")
        _text(self.title, 160, "COMPANY_DOCUMENT_SECTION_TITLE_INVALID")
        _text(self.body, 20_000, "COMPANY_DOCUMENT_SECTION_BODY_INVALID")

    def to_dict(self) -> dict[str, str]:
        """Project this exact section; no content or authority is synthesized."""
        return {"section_id": self.section_id, "title": self.title, "body": self.body}


@dataclass(frozen=True, slots=True)
class CompanyOperatingDocumentRevision:
    """Immutable exact-company revision with source-owned lifecycle evidence.

    Instances are validation/evidence, never authorization. Caller-owned source
    transactions persist them; the HTTP boundary independently authorizes actors.
    Publication requires a different principal from the revision's author.
    """

    tenant_id: str
    classification: CompanyDocumentClass
    document_version: str
    revision: int
    state: CompanyDocumentState
    title: str
    sections: tuple[CompanyDocumentSection, ...]
    author_principal_id: str
    recorded_at: str
    previous_fingerprint: str | None = None
    approved_by_principal_id: str | None = None
    approval_reference: str | None = None
    effective_from: str | None = None

    def __post_init__(self) -> None:
        if self.tenant_id != WILSY_COMPANY_TENANT_ID:
            raise CompanyDocumentError("COMPANY_DOCUMENT_TENANT_DENIED")
        if not isinstance(self.classification, CompanyDocumentClass) or not isinstance(self.state, CompanyDocumentState):
            raise CompanyDocumentError("COMPANY_DOCUMENT_CLASSIFICATION_INVALID")
        if not isinstance(self.document_version, str) or not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", self.document_version) or len(self.document_version) > 40:
            raise CompanyDocumentError("COMPANY_DOCUMENT_VERSION_INVALID")
        if type(self.revision) is not int or self.revision < 1:
            raise CompanyDocumentError("COMPANY_DOCUMENT_REVISION_INVALID")
        _text(self.title, 200, "COMPANY_DOCUMENT_TITLE_INVALID")
        _text(self.author_principal_id, 256, "COMPANY_DOCUMENT_AUTHOR_INVALID")
        if not isinstance(self.sections, tuple) or not 1 <= len(self.sections) <= MAX_SECTIONS:
            raise CompanyDocumentError("COMPANY_DOCUMENT_SECTIONS_INVALID")
        if any(not isinstance(section, CompanyDocumentSection) for section in self.sections):
            raise CompanyDocumentError("COMPANY_DOCUMENT_SECTIONS_INVALID")
        if len({section.section_id for section in self.sections}) != len(self.sections) or sum(len(section.body) for section in self.sections) > MAX_CONTENT:
            raise CompanyDocumentError("COMPANY_DOCUMENT_SECTIONS_INVALID")
        if instant(self.recorded_at) != self.recorded_at:
            raise CompanyDocumentError("COMPANY_DOCUMENT_TIME_INVALID")
        if self.revision == 1 and self.previous_fingerprint is not None:
            raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
        if self.revision > 1 and (not isinstance(self.previous_fingerprint, str) or not re.fullmatch(r"[a-f0-9]{128}", self.previous_fingerprint)):
            raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
        if self.state is CompanyDocumentState.PUBLISHED:
            _text(self.approved_by_principal_id, 256, "COMPANY_DOCUMENT_APPROVER_REQUIRED")
            _text(self.approval_reference, 500, "COMPANY_DOCUMENT_APPROVAL_REQUIRED")
            if self.approved_by_principal_id == self.author_principal_id and not (
                self.classification is CompanyDocumentClass.STRATEGY
                and self.approval_reference == FOUNDER_RATIFICATION_REFERENCE
            ):
                raise CompanyDocumentError("COMPANY_DOCUMENT_INDEPENDENT_APPROVER_REQUIRED")
            if (self.approval_reference == FOUNDER_RATIFICATION_REFERENCE
                and (self.classification is not CompanyDocumentClass.STRATEGY
                     or self.approved_by_principal_id != self.author_principal_id)):
                raise CompanyDocumentError("COMPANY_DOCUMENT_FOUNDER_RATIFICATION_INVALID")
            if self.effective_from is None or instant(self.effective_from) != self.effective_from:
                raise CompanyDocumentError("COMPANY_DOCUMENT_EFFECTIVE_DATE_REQUIRED")
        elif any(value is not None for value in (self.approved_by_principal_id, self.approval_reference, self.effective_from)):
            raise CompanyDocumentError("COMPANY_DOCUMENT_UNPUBLISHED_APPROVAL_FORBIDDEN")

    @property
    def document_id(self) -> str:
        """Stable classification identity; revision and version stay distinct."""
        return "wilsy-company-" + self.classification.value.lower()

    def semantic_payload(self) -> dict[str, Any]:
        """Return all persisted semantic fields; exclude Mongo transport metadata."""
        return {
            "schema": SCHEMA, "tenant_id": self.tenant_id,
            "document_id": self.document_id, "classification": self.classification.value,
            "document_version": self.document_version, "revision": self.revision,
            "state": self.state.value, "title": self.title,
            "sections": [section.to_dict() for section in self.sections],
            "author_principal_id": self.author_principal_id, "recorded_at": self.recorded_at,
            "previous_fingerprint": self.previous_fingerprint,
            "approved_by_principal_id": self.approved_by_principal_id,
            "approval_reference": self.approval_reference, "effective_from": self.effective_from,
        }

    @property
    def fingerprint(self) -> str:
        """Deterministic SHA3-512 over every declared semantic field."""
        return semantic_fingerprint(self.semantic_payload())

    def to_dict(self) -> dict[str, Any]:
        """Serialize immutable content/evidence; no projection invents approval."""
        return {**self.semantic_payload(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> CompanyOperatingDocumentRevision:
        """Hydrate exact stored truth and reject altered fields or digest.

        Mongo _id is intentionally excluded; every other persisted field must
        match the defined payload. Corruption never becomes lawful absence.
        """
        try:
            record = dict(payload)
            record.pop("_id", None)
            sections = tuple(CompanyDocumentSection(**section) for section in record["sections"])
            revision = cls(
                tenant_id=record["tenant_id"], classification=CompanyDocumentClass(record["classification"]),
                document_version=record["document_version"], revision=record["revision"],
                state=CompanyDocumentState(record["state"]), title=record["title"], sections=sections,
                author_principal_id=record["author_principal_id"], recorded_at=record["recorded_at"],
                previous_fingerprint=record["previous_fingerprint"], approved_by_principal_id=record["approved_by_principal_id"],
                approval_reference=record["approval_reference"], effective_from=record["effective_from"],
            )
            if set(record) != set(revision.to_dict()) or record.get("schema") != SCHEMA or record.get("document_id") != revision.document_id:
                raise CompanyDocumentError("COMPANY_DOCUMENT_PERSISTED_INVALID")
            fingerprint = record.get("fingerprint")
            if not isinstance(fingerprint, str) or not compare_digest(fingerprint, revision.fingerprint):
                raise CompanyDocumentError("COMPANY_DOCUMENT_INTEGRITY_INVALID")
            return revision
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, CompanyDocumentError):
                raise
            raise CompanyDocumentError("COMPANY_DOCUMENT_PERSISTED_INVALID") from error

    def submit(self, principal_id: str, now: datetime) -> CompanyOperatingDocumentRevision:
        """Advance only the current author's DRAFT; no approval is inferred.

        Caller must separately hold current author permission in exact company
        scope. Persistence, expected-revision arbitration and replay are external.
        """
        if self.state is not CompanyDocumentState.DRAFT or principal_id != self.author_principal_id:
            raise CompanyDocumentError("COMPANY_DOCUMENT_SUBMISSION_DENIED")
        return replace(self, revision=self.revision + 1, state=CompanyDocumentState.SUBMITTED,
                       recorded_at=instant(now), previous_fingerprint=self.fingerprint)

    def publish(self, principal_id: str, approval_reference: str, effective_from: str,
                now: datetime) -> CompanyOperatingDocumentRevision:
        """Record an independently authorized publisher's approval/publication.

        Submission is not approval. Normal IAM publishers must be independent.
        The exact source-verified Founder may ratify only Strategy through the
        registry's separate server-owned action and immutable reference.
        """
        if self.state is not CompanyDocumentState.SUBMITTED:
            raise CompanyDocumentError("COMPANY_DOCUMENT_PUBLICATION_STATE_INVALID")
        return replace(self, revision=self.revision + 1, state=CompanyDocumentState.PUBLISHED,
                       recorded_at=instant(now), previous_fingerprint=self.fingerprint,
                       approved_by_principal_id=principal_id, approval_reference=approval_reference,
                       effective_from=instant(effective_from))


# ARTIFACT: company_operating_document.py
# VERSION: v1.1.0-EXPLICIT-FOUNDER-STRATEGY-RATIFICATION
# AUTHORITY BOUNDARY: Pure immutable lifecycle/evidence; HTTP IAM admits actors.
# TENANT POSTURE: Exact canonical WILSY company tenant only.
# FAIL-CLOSED POSTURE: Invalid text, time, lineage, digest or self-approval rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
