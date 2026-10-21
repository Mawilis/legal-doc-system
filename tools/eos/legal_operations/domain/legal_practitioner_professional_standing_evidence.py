"""TITLE: WILSY OS Practitioner Professional Standing Evidence Domain.
VERSION: v1.0.0-R62-INSTITUTIONAL-PROFESSIONAL-EVIDENCE
AUTHORITY: Immutable external-source observation evidence only.
EPITOME: Preserve provenance for a bounded professional-standing or Fidelity
    Fund Certificate observation and derive a fail-closed documentary finding
    without inventing regulatory, reviewer, confidentiality, matter-access,
    supervision, reassignment, or professional-practice authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_practitioner_professional_standing_evidence.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Governance; external regulators remain
    authoritative for their published records; Wilsy records observations only.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG:
    2026-10-21 v1.0.0-R62-INSTITUTIONAL-PROFESSIONAL-EVIDENCE
    Introduces immutable SHA3-512 observation evidence, corruption-first
    currentness, and an explicit operational-access ratification contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Opaque subject identifiers and source references;
    no names, client content, matter content, credentials, or narrative reasons.
TENANT BOUNDARY: Every observation is bound to one exact Wilsy tenant and
    principal; cross-tenant evidence is blocked without existence disclosure.
AUTHORITY BOUNDARY: A VERIFIED observation remains documentary evidence only.
    It is not admission, practising authority, FFC authority, IAM, clearance,
    reviewer eligibility, approval, matter access, or reassignment authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Final, Iterable


VERSION: Final[str] = "v1.0.0-R62-INSTITUTIONAL-PROFESSIONAL-EVIDENCE"
SCHEMA: Final[str] = "WILSY-LEGAL-PRACTITIONER-PROFESSIONAL-EVIDENCE/V1"
SUPPORTED_JURISDICTIONS: Final[frozenset[str]] = frozenset({"ZA"})
_ID: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}\Z")


class ProfessionalStandingEvidenceError(ValueError):
    """Expose one stable, content-free evidence validation failure.

    The exception grants no regulatory, tenant, reviewer, matter, access,
    reassignment, persistence, transaction, or financial authority.
    """

    def __init__(self, code: str) -> None:
        """Create a bounded error without retaining rejected source values."""
        self.code = code
        super().__init__(code)


class ProfessionalEvidenceKind(StrEnum):
    """Separate professional-directory standing from FFC validity evidence."""

    PRACTISING_STATUS = "PRACTISING_STATUS"
    FIDELITY_FUND_CERTIFICATE_STATUS = "FIDELITY_FUND_CERTIFICATE_STATUS"


class ProfessionalEvidenceOutcome(StrEnum):
    """Describe the source observation, never Wilsy operational permission."""

    UNVERIFIED = "UNVERIFIED"
    VERIFIED_CURRENT = "VERIFIED_CURRENT"
    NOT_CURRENT = "NOT_CURRENT"
    REVOKED = "REVOKED"


class ProfessionalEvidenceMethod(StrEnum):
    """Identify how a human or governed adapter obtained source evidence."""

    PUBLIC_WEB_OBSERVATION = "PUBLIC_WEB_OBSERVATION"
    ATTESTED_DOCUMENT_REVIEW = "ATTESTED_DOCUMENT_REVIEW"


class ProfessionalStandingCurrentnessState(StrEnum):
    """Fail-closed documentary projection states; none authorizes access."""

    NO_EVIDENCE = "NO_EVIDENCE"
    VERIFIED_DOCUMENTARY_ONLY = "VERIFIED_DOCUMENTARY_ONLY"
    UNVERIFIED_BLOCKED = "UNVERIFIED_BLOCKED"
    NEGATIVE_BLOCKED = "NEGATIVE_BLOCKED"
    REVOKED_BLOCKED = "REVOKED_BLOCKED"
    EXPIRED_BLOCKED = "EXPIRED_BLOCKED"
    UNSUPPORTED_JURISDICTION_BLOCKED = "UNSUPPORTED_JURISDICTION_BLOCKED"
    SCOPE_MISMATCH_BLOCKED = "SCOPE_MISMATCH_BLOCKED"
    DUPLICATE_BLOCKED = "DUPLICATE_BLOCKED"
    CONTRADICTORY_BLOCKED = "CONTRADICTORY_BLOCKED"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class OperationalAccessRatificationDecision(StrEnum):
    """Name each independent authority still required for positive access."""

    PROFESSIONAL_EVIDENCE_ISSUER_AUTHORITY = (
        "PROFESSIONAL_EVIDENCE_ISSUER_AUTHORITY"
    )
    CURRENT_TENANT_AFFILIATION_AND_IDENTITY = (
        "CURRENT_TENANT_AFFILIATION_AND_IDENTITY"
    )
    EXACT_MATTER_CONFIDENTIALITY_PERMISSION = (
        "EXACT_MATTER_CONFIDENTIALITY_PERMISSION"
    )
    REVIEWER_ELIGIBILITY_AND_APPROVAL_AUTHORITY = (
        "REVIEWER_ELIGIBILITY_AND_APPROVAL_AUTHORITY"
    )
    CURRENT_ACKNOWLEDGMENT_AUTHORITY = "CURRENT_ACKNOWLEDGMENT_AUTHORITY"
    ETHICAL_WALL_CLEARANCE_AUTHORITY = "ETHICAL_WALL_CLEARANCE_AUTHORITY"
    SUPERVISION_APPROVAL_AUTHORITY = "SUPERVISION_APPROVAL_AUTHORITY"
    OPERATIONAL_ACCESS_ISSUANCE_AUTHORITY = "OPERATIONAL_ACCESS_ISSUANCE_AUTHORITY"


RATIFICATION_DECISIONS_REQUIRED: Final[
    tuple[OperationalAccessRatificationDecision, ...]
] = tuple(OperationalAccessRatificationDecision)


def _id(name: str, value: object) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise ProfessionalStandingEvidenceError(name.upper() + "_INVALID")
    if name == "tenant_id" and value.casefold() in {"default", "global", "root", "*"}:
        raise ProfessionalStandingEvidenceError("TENANT_ID_INVALID")
    return value


def _jurisdiction(value: object) -> str:
    if type(value) is not str or re.fullmatch(r"[A-Z]{2}", value) is None:
        raise ProfessionalStandingEvidenceError("JURISDICTION_INVALID")
    return value


def _time(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise ProfessionalStandingEvidenceError(name.upper() + "_INVALID")
    result = value.astimezone(timezone.utc)
    if result != value or result.microsecond:
        raise ProfessionalStandingEvidenceError(name.upper() + "_NONCANONICAL")
    return result


@dataclass(frozen=True, slots=True)
class LegalPractitionerProfessionalStandingEvidence:
    """Record one immutable external-source observation with exact provenance.

    Mutation semantics: none. Idempotency and persistence are not implemented.
    Tenant scope is exact. Source truth is observed, not imported as Wilsy
    authority. The record cannot authorize professional practice or access.
    """

    evidence_id: str
    tenant_id: str
    practitioner_principal_id: str
    verified_subject_id: str
    issuer_source_id: str
    jurisdiction: str
    evidence_kind: ProfessionalEvidenceKind | str
    outcome: ProfessionalEvidenceOutcome | str
    verification_method: ProfessionalEvidenceMethod | str
    evidence_reference: str
    source_uri: str
    observed_at: datetime
    valid_until: datetime
    revoked_at: datetime | None = None
    schema: str = SCHEMA
    evidence_version: str = VERSION
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        """Validate exact shape and bind every semantic field into SHA3-512."""
        if self.schema != SCHEMA or self.evidence_version != VERSION:
            raise ProfessionalStandingEvidenceError("SCHEMA_VERSION_INVALID")
        for name in (
            "evidence_id", "tenant_id", "practitioner_principal_id",
            "verified_subject_id", "issuer_source_id", "evidence_reference",
            "source_uri",
        ):
            object.__setattr__(self, name, _id(name, getattr(self, name)))
        object.__setattr__(self, "jurisdiction", _jurisdiction(self.jurisdiction))
        try:
            kind = ProfessionalEvidenceKind(self.evidence_kind)
            outcome = ProfessionalEvidenceOutcome(self.outcome)
            method = ProfessionalEvidenceMethod(self.verification_method)
        except (TypeError, ValueError) as error:
            raise ProfessionalStandingEvidenceError("EVIDENCE_ENUM_INVALID") from error
        object.__setattr__(self, "evidence_kind", kind)
        object.__setattr__(self, "outcome", outcome)
        object.__setattr__(self, "verification_method", method)
        observed = _time("observed_at", self.observed_at)
        valid_until = _time("valid_until", self.valid_until)
        if valid_until <= observed:
            raise ProfessionalStandingEvidenceError("VALIDITY_WINDOW_INVALID")
        object.__setattr__(self, "observed_at", observed)
        object.__setattr__(self, "valid_until", valid_until)
        if self.revoked_at is not None:
            revoked = _time("revoked_at", self.revoked_at)
            if revoked < observed:
                raise ProfessionalStandingEvidenceError("REVOCATION_TIME_INVALID")
            object.__setattr__(self, "revoked_at", revoked)
        if outcome is ProfessionalEvidenceOutcome.REVOKED and self.revoked_at is None:
            raise ProfessionalStandingEvidenceError("REVOCATION_TIME_REQUIRED")
        material = {
            name: (
                getattr(self, name).value
                if isinstance(getattr(self, name), StrEnum)
                else getattr(self, name).isoformat()
                if isinstance(getattr(self, name), datetime)
                else getattr(self, name)
            )
            for name in self.__dataclass_fields__
            if name != "fingerprint"
        }
        raw = json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        object.__setattr__(self, "fingerprint", sha3_512(raw).hexdigest())

    @property
    def permits_operational_access(self) -> bool:
        """Refuse to elevate professional evidence into operational access."""
        return False


@dataclass(frozen=True, slots=True)
class ProfessionalStandingCurrentness:
    """Return a non-authorizing, exact-scope documentary evaluation."""

    tenant_id: str
    practitioner_principal_id: str
    jurisdiction: str
    evidence_kind: ProfessionalEvidenceKind
    evaluation_time: datetime
    state: ProfessionalStandingCurrentnessState
    decisive_fingerprints: tuple[str, ...] = ()
    ratification_decisions_required: tuple[
        OperationalAccessRatificationDecision, ...
    ] = RATIFICATION_DECISIONS_REQUIRED

    @property
    def permits_operational_access(self) -> bool:
        """Always deny; G77 remains institutionally unratified."""
        return False

    @property
    def permits_reassignment_execution(self) -> bool:
        """Always deny reassignment execution from documentary evidence."""
        return False


def project_professional_standing_currentness(
    *,
    tenant_id: str,
    practitioner_principal_id: str,
    jurisdiction: str,
    evidence_kind: ProfessionalEvidenceKind | str,
    evaluation_time: datetime,
    evidence: Iterable[LegalPractitionerProfessionalStandingEvidence],
) -> ProfessionalStandingCurrentness:
    """Validate immutable evidence and derive a fail-closed documentary state.

    Missing, stale, ambiguous, contradictory, revoked, cross-tenant, and
    unsupported-jurisdiction evidence denies. A verified-current result remains
    documentary only and cannot satisfy G77 or any access prerequisite.
    """
    tenant = _id("tenant_id", tenant_id)
    practitioner = _id("practitioner_principal_id", practitioner_principal_id)
    requested_jurisdiction = _jurisdiction(jurisdiction)
    at = _time("evaluation_time", evaluation_time)
    try:
        requested_kind = ProfessionalEvidenceKind(evidence_kind)
    except (TypeError, ValueError) as error:
        raise ProfessionalStandingEvidenceError("EVIDENCE_KIND_INVALID") from error

    def result(
        state: ProfessionalStandingCurrentnessState,
        fingerprints: tuple[str, ...] = (),
    ) -> ProfessionalStandingCurrentness:
        return ProfessionalStandingCurrentness(
            tenant, practitioner, requested_jurisdiction, requested_kind,
            at, state, fingerprints,
        )

    if requested_jurisdiction not in SUPPORTED_JURISDICTIONS:
        return result(
            ProfessionalStandingCurrentnessState.UNSUPPORTED_JURISDICTION_BLOCKED
        )
    try:
        history = tuple(evidence)
        if not history:
            return result(ProfessionalStandingCurrentnessState.NO_EVIDENCE)
        ids: set[str] = set()
        references: set[str] = set()
        scoped: list[LegalPractitionerProfessionalStandingEvidence] = []
        for item in history:
            if (
                type(item) is not LegalPractitionerProfessionalStandingEvidence
                or replace(item).fingerprint != item.fingerprint
            ):
                return result(ProfessionalStandingCurrentnessState.CORRUPT_BLOCKED)
            if item.evidence_id in ids or item.evidence_reference in references:
                return result(ProfessionalStandingCurrentnessState.DUPLICATE_BLOCKED)
            ids.add(item.evidence_id)
            references.add(item.evidence_reference)
            if (
                item.tenant_id != tenant
                or item.practitioner_principal_id != practitioner
                or item.jurisdiction != requested_jurisdiction
                or item.evidence_kind is not requested_kind
            ):
                return result(
                    ProfessionalStandingCurrentnessState.SCOPE_MISMATCH_BLOCKED
                )
            scoped.append(item)
        observed = [item for item in scoped if item.observed_at <= at]
        if not observed:
            return result(ProfessionalStandingCurrentnessState.NO_EVIDENCE)
        active = [item for item in observed if at < item.valid_until]
        if not active:
            return result(
                ProfessionalStandingCurrentnessState.EXPIRED_BLOCKED,
                tuple(sorted(item.fingerprint for item in observed)),
            )
        if any(item.revoked_at is not None and item.revoked_at <= at for item in active):
            return result(
                ProfessionalStandingCurrentnessState.REVOKED_BLOCKED,
                tuple(sorted(item.fingerprint for item in active)),
            )
        outcomes = {item.outcome for item in active}
        fingerprints = tuple(sorted(item.fingerprint for item in active))
        if len(outcomes) != 1:
            return result(
                ProfessionalStandingCurrentnessState.CONTRADICTORY_BLOCKED,
                fingerprints,
            )
        outcome = next(iter(outcomes))
        if outcome is ProfessionalEvidenceOutcome.UNVERIFIED:
            state = ProfessionalStandingCurrentnessState.UNVERIFIED_BLOCKED
        elif outcome in (
            ProfessionalEvidenceOutcome.NOT_CURRENT,
            ProfessionalEvidenceOutcome.REVOKED,
        ):
            state = ProfessionalStandingCurrentnessState.NEGATIVE_BLOCKED
        else:
            state = ProfessionalStandingCurrentnessState.VERIFIED_DOCUMENTARY_ONLY
        return result(state, fingerprints)
    except Exception:
        return result(ProfessionalStandingCurrentnessState.CORRUPT_BLOCKED)


__all__ = [
    "VERSION", "SCHEMA", "SUPPORTED_JURISDICTIONS",
    "ProfessionalStandingEvidenceError", "ProfessionalEvidenceKind",
    "ProfessionalEvidenceOutcome", "ProfessionalEvidenceMethod",
    "ProfessionalStandingCurrentnessState",
    "OperationalAccessRatificationDecision", "RATIFICATION_DECISIONS_REQUIRED",
    "LegalPractitionerProfessionalStandingEvidence",
    "ProfessionalStandingCurrentness", "project_professional_standing_currentness",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_professional_standing_evidence.py
# VERSION: v1.0.0-R62-INSTITUTIONAL-PROFESSIONAL-EVIDENCE
# AUTHORITY BOUNDARY: immutable external-source observations and pure evaluation only
# TENANT POSTURE: exact tenant and principal; cross-scope evidence blocks
# FAIL-CLOSED POSTURE: missing, stale, ambiguous, contradictory, revoked,
# unsupported-jurisdiction and corrupt evidence never authorize
# OPERATIONAL ACCESS / REVIEW / CLEARANCE / REASSIGNMENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
