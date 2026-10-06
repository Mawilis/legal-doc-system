"""WILSY OS immutable human legal conflict-review determination.

TITLE: Legal Conflict Review Determination
VERSION: v1.0.0-L8-8G-LEGAL-CONFLICT-REVIEW-DETERMINATION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Record one immutable human legal-review determination over one exact
         certified L8-8D conflict-screening result without converting screening
         signals, automated inference, or legacy Node conflict state into legal
         clearance, waiver, recusal, representation or client-acceptance truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_conflict_review.py
COLLABORATION / OWNERSHIP: L8-8D owns screening semantics; L8-8E owns durable
                            screening evidence; L8-8F owns authoritative durable
                            screening composition. L8-8G owns only immutable
                            human-review determination semantics. A later IAM
                            composer must prove reviewer authority before durable
                            admission; later waiver, ethical-wall, recusal,
                            representation and client-acceptance domains remain
                            separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-L8-8G-LEGAL-CONFLICT-REVIEW-DETERMINATION establishes exact
           screening binding, closed human determination outcomes, mandatory
           reviewer principal plus authorization evidence, bounded review-reason
           reference, strict chronology, screening-status/outcome compatibility,
           deterministic SHA3-512 integrity and exact hydration. REVIEW_REQUIRED
           may be determined as CONFLICT_IDENTIFIED, NO_CONFLICT_IDENTIFIED, or
           ESCALATION_REQUIRED. NO_MATCH_FOUND may only be recorded as
           NO_CONFLICT_IDENTIFIED and remains explicitly distinct from a general
           clearance or future-conflict warranty.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores only opaque screening/matter/party/reviewer
                             identities and SHA3-512 evidence fingerprints; no
                             raw party PII, legal narrative, credentials or
                             privileged review text is persisted in this domain.
TENANT BOUNDARY: Tenant, party, matter and subject identity are derived only
                 from the supplied certified screening result.
AUTHORITY BOUNDARY: Human conflict determination evidence only. It creates no
                    waiver, informed consent, ethical wall, recusal completion,
                    client acceptance, engagement, representation mandate,
                    matter lifecycle mutation, legal advice or court finding.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: Pure in-memory immutable domain composition only; no
                      persistence/session/transaction lifecycle.
FAIL-CLOSED DECLARATION: Non-screening input, pseudo tenant, malformed reviewer
                         or evidence identity, incompatible screening/outcome,
                         invalid chronology, schema drift and fingerprint
                         divergence reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
)


VERSION: Final[str] = "v1.0.0-L8-8G-LEGAL-CONFLICT-REVIEW-DETERMINATION"
SCHEMA: Final[str] = "WILSY-LEGAL-CONFLICT-REVIEW-DETERMINATION/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalConflictReviewError(ValueError):
    """One fail-closed L8-8G determination-domain failure with stable code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalConflictReviewOutcome(StrEnum):
    """Closed human determinations; deliberately excludes waiver/clearance."""

    CONFLICT_IDENTIFIED = "CONFLICT_IDENTIFIED"
    NO_CONFLICT_IDENTIFIED = "NO_CONFLICT_IDENTIFIED"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"


_REVIEW_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "review_version",
    "tenant_id",
    "review_id",
    "screening_id",
    "screening_fingerprint",
    "source_party_id",
    "source_case_matter_id",
    "subject_identity_fingerprint",
    "screening_status",
    "reviewer_principal_id",
    "reviewer_authorization_reference",
    "reviewer_authorization_fingerprint",
    "outcome",
    "review_reason_reference",
    "reviewed_at",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "fingerprint",
)
REVIEW_FIELDS: Final[frozenset[str]] = frozenset(_REVIEW_FIELDS)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalConflictReviewError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L8_8G_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_8G_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L8_8G_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"L8_8G_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L8_8G_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L8_8G_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class LegalConflictReviewDetermination:
    """Immutable human review evidence bound to one exact screening."""

    tenant_id: str
    review_id: str
    screening_id: str
    screening_fingerprint: str
    source_party_id: str
    source_case_matter_id: str
    subject_identity_fingerprint: str
    screening_status: LegalConflictScreeningStatus | str
    reviewer_principal_id: str
    reviewer_authorization_reference: str
    reviewer_authorization_fingerprint: str
    outcome: LegalConflictReviewOutcome | str
    review_reason_reference: str
    reviewed_at: datetime
    source_evidence_reference: str
    source_evidence_fingerprint: str
    schema: str = SCHEMA
    review_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        review_id = _identity("review_id", self.review_id)
        screening_id = _identity("screening_id", self.screening_id)
        screening_fp = _fingerprint(
            "screening_fingerprint",
            self.screening_fingerprint,
        )
        source_party_id = _identity("source_party_id", self.source_party_id)
        source_case_matter_id = _identity(
            "source_case_matter_id",
            self.source_case_matter_id,
        )
        subject_fp = _fingerprint(
            "subject_identity_fingerprint",
            self.subject_identity_fingerprint,
        )
        reviewer = _identity(
            "reviewer_principal_id",
            self.reviewer_principal_id,
        )
        reviewer_auth_ref = _reference(
            "reviewer_authorization_reference",
            self.reviewer_authorization_reference,
        )
        reviewer_auth_fp = _fingerprint(
            "reviewer_authorization_fingerprint",
            self.reviewer_authorization_fingerprint,
        )
        review_reason = _reference(
            "review_reason_reference",
            self.review_reason_reference,
        )
        reviewed_at = _timestamp("reviewed_at", self.reviewed_at)
        source_ref = _reference(
            "source_evidence_reference",
            self.source_evidence_reference,
        )
        source_fp = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )
        try:
            screening_status = LegalConflictScreeningStatus(
                self.screening_status
            )
            outcome = LegalConflictReviewOutcome(self.outcome)
        except (TypeError, ValueError) as error:
            _fail("L8_8G_CLASSIFICATION_INVALID", error)

        if (
            screening_status is LegalConflictScreeningStatus.NO_MATCH_FOUND
            and outcome is not LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED
        ):
            _fail("L8_8G_OUTCOME_INCOMPATIBLE_WITH_SCREENING")
        if self.schema != SCHEMA or self.review_version != VERSION:
            _fail("L8_8G_IDENTITY_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "review_id", review_id)
        object.__setattr__(self, "screening_id", screening_id)
        object.__setattr__(self, "screening_fingerprint", screening_fp)
        object.__setattr__(self, "source_party_id", source_party_id)
        object.__setattr__(
            self,
            "source_case_matter_id",
            source_case_matter_id,
        )
        object.__setattr__(
            self,
            "subject_identity_fingerprint",
            subject_fp,
        )
        object.__setattr__(self, "screening_status", screening_status)
        object.__setattr__(self, "reviewer_principal_id", reviewer)
        object.__setattr__(
            self,
            "reviewer_authorization_reference",
            reviewer_auth_ref,
        )
        object.__setattr__(
            self,
            "reviewer_authorization_fingerprint",
            reviewer_auth_fp,
        )
        object.__setattr__(self, "outcome", outcome)
        object.__setattr__(self, "review_reason_reference", review_reason)
        object.__setattr__(self, "reviewed_at", reviewed_at)
        object.__setattr__(self, "source_evidence_reference", source_ref)
        object.__setattr__(self, "source_evidence_fingerprint", source_fp)

        payload = {
            field: _json_value(getattr(self, field))
            for field in _REVIEW_FIELDS[:-1]
        }
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L8_8G_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize exact review evidence without privileged review narrative."""
        return {
            field: _json_value(getattr(self, field))
            for field in _REVIEW_FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalConflictReviewDetermination":
        """Hydrate only exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(REVIEW_FIELDS):
            _fail("L8_8G_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(stored, result.fingerprint)
        ):
            _fail("L8_8G_FINGERPRINT_MISMATCH")
        return result


def determine_legal_conflict_review(
    *,
    screening: LegalConflictScreeningResult,
    review_id: str,
    reviewer_principal_id: str,
    reviewer_authorization_reference: str,
    reviewer_authorization_fingerprint: str,
    outcome: LegalConflictReviewOutcome | str,
    review_reason_reference: str,
    reviewed_at: datetime,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
) -> LegalConflictReviewDetermination:
    """Create one immutable human determination over exact screening evidence.

    The caller must later be a certified IAM composer that proves reviewer
    authority. This pure domain function cannot itself authenticate a principal.
    It binds the resulting determination to the exact screening fingerprint,
    source party, matter, subject identity, status and chronology.

    NO_CONFLICT_IDENTIFIED means only that the authorized reviewer found no
    conflict in the supplied screening context. It is not a general clearance,
    waiver, future-conflict warranty, representation authorization or client
    acceptance.
    """
    if type(screening) is not LegalConflictScreeningResult:
        _fail("L8_8G_SCREENING_REQUIRED")
    reviewed = _timestamp("reviewed_at", reviewed_at)
    if reviewed < screening.screened_at:
        _fail("L8_8G_REVIEWED_AT_INVALID")
    return LegalConflictReviewDetermination(
        tenant_id=screening.tenant_id,
        review_id=review_id,
        screening_id=screening.screening_id,
        screening_fingerprint=screening.fingerprint,
        source_party_id=screening.source_party_id,
        source_case_matter_id=screening.source_case_matter_id,
        subject_identity_fingerprint=screening.subject_identity_fingerprint,
        screening_status=screening.status,
        reviewer_principal_id=reviewer_principal_id,
        reviewer_authorization_reference=reviewer_authorization_reference,
        reviewer_authorization_fingerprint=(
            reviewer_authorization_fingerprint
        ),
        outcome=outcome,
        review_reason_reference=review_reason_reference,
        reviewed_at=reviewed,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
    )


__all__ = [
    "REVIEW_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalConflictReviewDetermination",
    "LegalConflictReviewError",
    "LegalConflictReviewOutcome",
    "determine_legal_conflict_review",
]


# ARTIFACT: legal_conflict_review.py
# VERSION: v1.0.0-L8-8G-LEGAL-CONFLICT-REVIEW-DETERMINATION
# AUTHORITY BOUNDARY: immutable human conflict-review determination evidence only
# TENANT POSTURE: tenant/party/matter/subject/screening identity derive from exact L8-8D screening
# FAIL-CLOSED POSTURE: malformed/incompatible/stale/drifted review evidence rejects; no automated clearance
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
