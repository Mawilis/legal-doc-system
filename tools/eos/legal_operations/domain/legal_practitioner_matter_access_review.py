"""TITLE: WILSY OS Institutional Practitioner Matter-Access Review Request.
VERSION: v1.0.0-R65-INSTITUTIONAL-ACCESS-REVIEW
AUTHORITY: Immutable firm-controlled pending or denied review evidence only.
EPITOME: Preserve an operationally useful request outcome while positive
    professional verification and matter access remain institutionally unratified.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_practitioner_matter_access_review.py
COLLABORATION / OWNERSHIP: Legal Operations owns request evidence; canonical
    IAM, matter, regulator, conflict, wall, acknowledgment and supervision
    authorities remain independent source owners.
CERTIFICATION / UPDATE DATE: 2026-10-22
CHANGELOG: 2026-10-22 v1.0.0-R65-INSTITUTIONAL-ACCESS-REVIEW introduces an
    immutable SHA3-512 pending/denied request contract with no approval state.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identifiers and blocker codes only; no PII,
    client content, regulator payload, conflict narrative or credentials.
TENANT BOUNDARY: Every request binds one exact non-pseudo tenant and matter.
AUTHORITY BOUNDARY: PENDING_REVIEW and DENIED never grant access, standing,
    FFC validity, approval, supervision, assignment or ethical-wall waiver.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import re
from typing import Final


VERSION: Final[str] = "v1.0.0-R65-INSTITUTIONAL-ACCESS-REVIEW"
SCHEMA: Final[str] = "WILSY-LEGAL-PRACTITIONER-MATTER-ACCESS-REVIEW/V1"
_ID: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}\Z")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "root", "*"})


class MatterAccessReviewError(ValueError):
    """Expose one stable validation code without retaining rejected content."""

    def __init__(self, code: str) -> None:
        """Create a bounded domain failure with no authority side effect."""
        self.code = code
        super().__init__(code)


class MatterAccessReviewDecision(StrEnum):
    """Limit R65 outcomes to non-authorizing operational states."""

    PENDING_REVIEW = "PENDING_REVIEW"
    DENIED = "DENIED"


class MatterAccessReviewBlocker(StrEnum):
    """Keep independent prerequisites visible without converting absence to clearance."""

    REGULATOR_ISSUER_TRUST_UNRATIFIED = "REGULATOR_ISSUER_TRUST_UNRATIFIED"
    PROFESSIONAL_STANDING_NOT_AUTHENTICATED = "PROFESSIONAL_STANDING_NOT_AUTHENTICATED"
    FFC_APPLICABILITY_NOT_AUTHENTICATED = "FFC_APPLICABILITY_NOT_AUTHENTICATED"
    PRACTITIONER_IAM_NOT_CURRENT = "PRACTITIONER_IAM_NOT_CURRENT"
    CONFLICT_PROVENANCE_NOT_CURRENT = "CONFLICT_PROVENANCE_NOT_CURRENT"
    ETHICAL_WALL_CLEARANCE_NOT_ESTABLISHED = "ETHICAL_WALL_CLEARANCE_NOT_ESTABLISHED"
    CLIENT_RESTRICTION_ACKNOWLEDGMENT_NOT_CURRENT = (
        "CLIENT_RESTRICTION_ACKNOWLEDGMENT_NOT_CURRENT"
    )
    SUPERVISION_REQUIREMENT_NOT_SATISFIED = "SUPERVISION_REQUIREMENT_NOT_SATISFIED"
    MATTER_SPECIFIC_APPROVER_NOT_RATIFIED = "MATTER_SPECIFIC_APPROVER_NOT_RATIFIED"
    OPERATIONAL_ACCESS_ISSUANCE_UNRATIFIED = "OPERATIONAL_ACCESS_ISSUANCE_UNRATIFIED"


def _identifier(name: str, value: object, *, tenant: bool = False) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise MatterAccessReviewError(f"R65_{name.upper()}_INVALID")
    if tenant and value.casefold() in _FORBIDDEN_TENANTS:
        raise MatterAccessReviewError("R65_TENANT_ID_INVALID")
    return value


def _instant(value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
        or value.microsecond
    ):
        raise MatterAccessReviewError("R65_RECORDED_AT_NONCANONICAL")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class LegalPractitionerMatterAccessReview:
    """Record one immutable, exact-scope pending or denied review outcome.

    Mutation semantics: none. Persistence and transaction lifecycle belong to
    the R65 registry and caller. Exact replay is keyed by ``idempotency_key``.
    No instance can represent approval or operational access.
    """

    review_request_id: str
    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    requested_by_principal_id: str
    decision: MatterAccessReviewDecision | str
    blockers: tuple[MatterAccessReviewBlocker | str, ...]
    reason_reference: str
    idempotency_key: str
    recorded_at: datetime
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = field(kw_only=True)

    def __post_init__(self) -> None:
        """Validate exact shape and bind all semantic material into SHA3-512."""
        if self.schema != SCHEMA or self.version != VERSION:
            raise MatterAccessReviewError("R65_SCHEMA_VERSION_INVALID")
        for name in (
            "review_request_id", "tenant_id", "case_matter_id",
            "practitioner_principal_id", "requested_by_principal_id",
            "reason_reference", "idempotency_key",
        ):
            object.__setattr__(
                self, name,
                _identifier(name, getattr(self, name), tenant=name == "tenant_id"),
            )
        try:
            decision = MatterAccessReviewDecision(self.decision)
            blockers = tuple(MatterAccessReviewBlocker(value) for value in self.blockers)
        except (TypeError, ValueError) as error:
            raise MatterAccessReviewError("R65_REVIEW_ENUM_INVALID") from error
        if not blockers or len(blockers) != len(set(blockers)):
            raise MatterAccessReviewError("R65_BLOCKERS_INVALID")
        blockers = tuple(sorted(blockers, key=lambda value: value.value))
        if decision is MatterAccessReviewDecision.PENDING_REVIEW and blockers == ():
            raise MatterAccessReviewError("R65_PENDING_BLOCKER_REQUIRED")
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "blockers", blockers)
        object.__setattr__(self, "recorded_at", _instant(self.recorded_at))
        if type(self.fingerprint) is not str or re.fullmatch(
            r"[0-9a-f]{128}", self.fingerprint
        ) is None:
            raise MatterAccessReviewError("R65_FINGERPRINT_INVALID")

    @property
    def permits_operational_access(self) -> bool:
        """Return false unconditionally because R65 carries no approval state."""
        return False



__all__ = [
    "VERSION", "SCHEMA", "MatterAccessReviewError",
    "MatterAccessReviewDecision", "MatterAccessReviewBlocker",
    "LegalPractitionerMatterAccessReview",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access_review.py
# VERSION: v1.0.0-R65-INSTITUTIONAL-ACCESS-REVIEW
# AUTHORITY BOUNDARY: IMMUTABLE PENDING OR DENIED REVIEW EVIDENCE ONLY
# TENANT POSTURE: EXACT NON-PSEUDO TENANT, MATTER AND PRINCIPAL SCOPE
# FAIL-CLOSED POSTURE: NO APPROVED STATE AND NO ABSENCE-AS-CLEARANCE
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
