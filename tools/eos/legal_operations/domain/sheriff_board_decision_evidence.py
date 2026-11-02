"""TITLE: WILSY OS Sheriff Board Decision Evidence.
VERSION: v1.0.0-SHERIFF-BOARD-DECISION-EVIDENCE
AUTHORITY: Immutable documentary evidence of distinct Board decisions only.
EPITOME: Preserve separate Board approvals, consultations, FFC-readiness
    confirmations and section 30(3) exemptions with exact statutory basis,
    target principal, appointment/area allocation fingerprint, decision
    outcome, conditions, source provenance and effective window.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/sheriff_board_decision_evidence.py
COLLABORATION / OWNERSHIP: South African Board for Sheriffs is the statutory
    decision-maker for the recorded Board decision; the Minister remains the
    appointment/area-allocation authority; source authentication, currentness,
    FFC, insurance, identity and IAM are separate gates.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-BOARD-DECISION-EVIDENCE
    Adds one immutable evidence contract for section 6(1) deputy approvals,
    section 5(1B), 2(3), 3(2) and 6B consultations/FFC-readiness confirmations,
    and section 30(3) exemptions for section 5(1A) appointments.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Opaque references and fingerprints only; no raw
    identity documents, credentials, personal data or Board deliberation text.
TENANT BOUNDARY: Exact tenant, subject principal, appointing sheriff, office,
    appointment and area-allocation fingerprints.
AUTHORITY BOUNDARY: Documentary evidence only. Does not authenticate the
    Board, establish a current approval, create a Ministerial appointment,
    issue an FFC, satisfy insurance, grant queue/IAM access or authorize service.
TRANSACTION BOUNDARY: Pure immutable value construction; no I/O or persistence.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final


VERSION: Final[str] = "v1.0.0-SHERIFF-BOARD-DECISION-EVIDENCE"
SCHEMA: Final[str] = "WILSY-SHERIFF-BOARD-DECISION-EVIDENCE/V1"
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}$"
)
_HEX_128: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*"}
)


class SheriffBoardDecisionEvidenceError(ValueError):
    """Reject malformed Board-decision documentary evidence."""

    def __init__(self, code: str) -> None:
        """Create one stable, content-free validation code."""
        self.code = code
        super().__init__(code)


class SheriffBoardDecisionKind(StrEnum):
    """Keep Board approval, consultation, confirmation and exemption distinct."""

    DEPUTY_APPOINTMENT_APPROVAL = "DEPUTY_APPOINTMENT_APPROVAL"
    CONSULTATION = "CONSULTATION"
    FFC_READINESS_CONFIRMATION = "FFC_READINESS_CONFIRMATION"
    SECTION_30_EXEMPTION = "SECTION_30_EXEMPTION"


class SheriffBoardDecisionBasis(StrEnum):
    """Identify the exact statutory provision authorizing the Board action."""

    SECTION_6_1 = "SECTION_6_1"
    SECTION_5_1_B = "SECTION_5_1_B"
    SECTION_2_3 = "SECTION_2_3"
    SECTION_3_2 = "SECTION_3_2"
    SECTION_6B_1 = "SECTION_6B_1"
    SECTION_30_3_FOR_SECTION_5_1_A = "SECTION_30_3_FOR_SECTION_5_1_A"


class SheriffBoardDecisionOutcome(StrEnum):
    """Typed outcomes; a consultation is never silently promoted to approval."""

    APPROVED = "APPROVED"
    REFUSED = "REFUSED"
    CONSULTED = "CONSULTED"
    CONSULTATION_NOT_COMPLETED = "CONSULTATION_NOT_COMPLETED"
    PREPARED_TO_ISSUE_FFC = "PREPARED_TO_ISSUE_FFC"
    NOT_PREPARED_TO_ISSUE_FFC = "NOT_PREPARED_TO_ISSUE_FFC"
    EXEMPTED = "EXEMPTED"
    NOT_EXEMPTED = "NOT_EXEMPTED"


_ALLOWED_OUTCOMES: Final[dict[
    tuple[SheriffBoardDecisionBasis, SheriffBoardDecisionKind],
    frozenset[SheriffBoardDecisionOutcome],
]] = {
    (SheriffBoardDecisionBasis.SECTION_6_1, SheriffBoardDecisionKind.DEPUTY_APPOINTMENT_APPROVAL):
        frozenset({SheriffBoardDecisionOutcome.APPROVED, SheriffBoardDecisionOutcome.REFUSED}),
    (SheriffBoardDecisionBasis.SECTION_5_1_B, SheriffBoardDecisionKind.FFC_READINESS_CONFIRMATION):
        frozenset({
            SheriffBoardDecisionOutcome.PREPARED_TO_ISSUE_FFC,
            SheriffBoardDecisionOutcome.NOT_PREPARED_TO_ISSUE_FFC,
        }),
    (SheriffBoardDecisionBasis.SECTION_2_3, SheriffBoardDecisionKind.CONSULTATION):
        frozenset({
            SheriffBoardDecisionOutcome.CONSULTED,
            SheriffBoardDecisionOutcome.CONSULTATION_NOT_COMPLETED,
        }),
    (SheriffBoardDecisionBasis.SECTION_2_3, SheriffBoardDecisionKind.FFC_READINESS_CONFIRMATION):
        frozenset({
            SheriffBoardDecisionOutcome.PREPARED_TO_ISSUE_FFC,
            SheriffBoardDecisionOutcome.NOT_PREPARED_TO_ISSUE_FFC,
        }),
    (SheriffBoardDecisionBasis.SECTION_3_2, SheriffBoardDecisionKind.CONSULTATION):
        frozenset({
            SheriffBoardDecisionOutcome.CONSULTED,
            SheriffBoardDecisionOutcome.CONSULTATION_NOT_COMPLETED,
        }),
    (SheriffBoardDecisionBasis.SECTION_3_2, SheriffBoardDecisionKind.FFC_READINESS_CONFIRMATION):
        frozenset({
            SheriffBoardDecisionOutcome.PREPARED_TO_ISSUE_FFC,
            SheriffBoardDecisionOutcome.NOT_PREPARED_TO_ISSUE_FFC,
        }),
    (SheriffBoardDecisionBasis.SECTION_6B_1, SheriffBoardDecisionKind.CONSULTATION):
        frozenset({
            SheriffBoardDecisionOutcome.CONSULTED,
            SheriffBoardDecisionOutcome.CONSULTATION_NOT_COMPLETED,
        }),
    (SheriffBoardDecisionBasis.SECTION_30_3_FOR_SECTION_5_1_A, SheriffBoardDecisionKind.SECTION_30_EXEMPTION):
        frozenset({SheriffBoardDecisionOutcome.EXEMPTED, SheriffBoardDecisionOutcome.NOT_EXEMPTED}),
}


def _identifier(name: str, value: object) -> str:
    """Require one canonical bounded opaque identifier."""
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise SheriffBoardDecisionEvidenceError(
            f"SHERIFF_BOARD_DECISION_{name.upper()}_INVALID"
        )
    if name == "tenant_id" and value.casefold() in _FORBIDDEN_TENANTS:
        raise SheriffBoardDecisionEvidenceError(
            "SHERIFF_BOARD_DECISION_TENANT_ID_INVALID"
        )
    return value


def _digest(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 fingerprint."""
    if type(value) is not str or _HEX_128.fullmatch(value) is None:
        raise SheriffBoardDecisionEvidenceError(
            f"SHERIFF_BOARD_DECISION_{name.upper()}_INVALID"
        )
    return value


def _instant(name: str, value: object) -> datetime:
    """Require an aware UTC instant with whole-second precision."""
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise SheriffBoardDecisionEvidenceError(
            f"SHERIFF_BOARD_DECISION_{name.upper()}_INVALID"
        )
    normalized = value.astimezone(timezone.utc)
    if normalized != value or normalized.microsecond:
        raise SheriffBoardDecisionEvidenceError(
            f"SHERIFF_BOARD_DECISION_{name.upper()}_NONCANONICAL"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class SheriffBoardDecisionEvidence:
    """One exact Board decision or consultation observation.

    Section 6(1) deputy approval, section 5(1B) readiness, section 2(3)/3(2)
    consultations and readiness confirmations, section 6B consultation, and
    section 30(3) exemptions are distinct records. A section 6B consultation
    never authorizes service of process. A readiness confirmation is not an
    FFC; the Board's later certificate issuance remains a separate record.
    """

    tenant_id: str
    decision_id: str
    revision: int
    subject_principal_id: str
    sheriff_office_id: str
    decision_basis: SheriffBoardDecisionBasis | str
    decision_kind: SheriffBoardDecisionKind | str
    decision_outcome: SheriffBoardDecisionOutcome | str
    decision_reference: str
    decision_fingerprint: str
    instrument_reference: str
    instrument_fingerprint: str
    source_uri: str
    source_observation_state: str
    source_verification_method: str
    source_verification_reference: str
    verified_by_principal_id: str
    observed_at: datetime
    effective_from: datetime
    effective_until: datetime | None
    appointment_evidence_fingerprint: str | None = None
    area_allocation_evidence_fingerprint: str | None = None
    appointing_sheriff_principal_id: str | None = None
    conditions_fingerprint: str | None = None
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = field(default="", compare=True)

    def __post_init__(self) -> None:
        """Validate statutory decision semantics and bind the complete record."""
        for name in (
            "tenant_id",
            "decision_id",
            "subject_principal_id",
            "sheriff_office_id",
            "decision_reference",
            "instrument_reference",
            "source_uri",
            "source_verification_reference",
            "verified_by_principal_id",
        ):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))
        for name in ("decision_fingerprint", "instrument_fingerprint"):
            object.__setattr__(self, name, _digest(name, getattr(self, name)))
        if type(self.revision) is not int or self.revision < 1:
            raise SheriffBoardDecisionEvidenceError(
                "SHERIFF_BOARD_DECISION_REVISION_INVALID"
            )
        if self.subject_principal_id == self.verified_by_principal_id:
            raise SheriffBoardDecisionEvidenceError(
                "SHERIFF_BOARD_DECISION_SELF_ATTESTATION_FORBIDDEN"
            )
        try:
            basis = SheriffBoardDecisionBasis(self.decision_basis)
            kind = SheriffBoardDecisionKind(self.decision_kind)
            outcome = SheriffBoardDecisionOutcome(self.decision_outcome)
        except (TypeError, ValueError) as error:
            raise SheriffBoardDecisionEvidenceError(
                "SHERIFF_BOARD_DECISION_ENUM_INVALID"
            ) from error
        allowed = _ALLOWED_OUTCOMES.get((basis, kind))
        if allowed is None or outcome not in allowed:
            raise SheriffBoardDecisionEvidenceError(
                "SHERIFF_BOARD_DECISION_BASIS_KIND_OUTCOME_MISMATCH"
            )
        object.__setattr__(self, "decision_basis", basis)
        object.__setattr__(self, "decision_kind", kind)
        object.__setattr__(self, "decision_outcome", outcome)

        appointment_fp = (
            None if self.appointment_evidence_fingerprint is None
            else _digest("appointment_evidence_fingerprint", self.appointment_evidence_fingerprint)
        )
        area_fp = (
            None if self.area_allocation_evidence_fingerprint is None
            else _digest("area_allocation_evidence_fingerprint", self.area_allocation_evidence_fingerprint)
        )
        appointing = (
            None if self.appointing_sheriff_principal_id is None
            else _identifier("appointing_sheriff_principal_id", self.appointing_sheriff_principal_id)
        )
        if basis is SheriffBoardDecisionBasis.SECTION_3_2:
            if appointment_fp is None or area_fp is None:
                raise SheriffBoardDecisionEvidenceError(
                    "SHERIFF_BOARD_DECISION_AREA_ALLOCATION_LINK_REQUIRED"
                )
        else:
            if appointment_fp is None or area_fp is not None:
                raise SheriffBoardDecisionEvidenceError(
                    "SHERIFF_BOARD_DECISION_APPOINTMENT_LINK_REQUIRED"
                )
        if basis is SheriffBoardDecisionBasis.SECTION_6_1:
            if appointing is None or appointing == self.subject_principal_id:
                raise SheriffBoardDecisionEvidenceError(
                    "SHERIFF_BOARD_DECISION_APPOINTING_SHERIFF_REQUIRED"
                )
        elif appointing is not None:
            raise SheriffBoardDecisionEvidenceError(
                "SHERIFF_BOARD_DECISION_APPOINTING_SHERIFF_UNEXPECTED"
            )
        conditions = (
            None if self.conditions_fingerprint is None
            else _digest("conditions_fingerprint", self.conditions_fingerprint)
        )
        predecessor = (
            None if self.supersedes_fingerprint is None
            else _digest("supersedes_fingerprint", self.supersedes_fingerprint)
        )
        if self.revision == 1 and predecessor is not None:
            raise SheriffBoardDecisionEvidenceError(
                "SHERIFF_BOARD_DECISION_ROOT_SUPERSEDES_FORBIDDEN"
            )
        if self.revision > 1 and predecessor is None:
            raise SheriffBoardDecisionEvidenceError(
                "SHERIFF_BOARD_DECISION_SUCCESSOR_REQUIRED"
            )
        object.__setattr__(self, "appointment_evidence_fingerprint", appointment_fp)
        object.__setattr__(self, "area_allocation_evidence_fingerprint", area_fp)
        object.__setattr__(self, "appointing_sheriff_principal_id", appointing)
        object.__setattr__(self, "conditions_fingerprint", conditions)
        object.__setattr__(self, "supersedes_fingerprint", predecessor)

        observed = _instant("observed_at", self.observed_at)
        start = _instant("effective_from", self.effective_from)
        end = None if self.effective_until is None else _instant("effective_until", self.effective_until)
        if end is not None and end <= start:
            raise SheriffBoardDecisionEvidenceError(
                "SHERIFF_BOARD_DECISION_EFFECTIVE_WINDOW_INVALID"
            )
        object.__setattr__(self, "observed_at", observed)
        object.__setattr__(self, "effective_from", start)
        object.__setattr__(self, "effective_until", end)
        if self.schema != SCHEMA or self.version != VERSION:
            raise SheriffBoardDecisionEvidenceError(
                "SHERIFF_BOARD_DECISION_SCHEMA_VERSION_INVALID"
            )
        calculated = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _digest("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, calculated):
                raise SheriffBoardDecisionEvidenceError(
                    "SHERIFF_BOARD_DECISION_FINGERPRINT_MISMATCH"
                )
        object.__setattr__(self, "fingerprint", calculated)

    def semantic_dict(self) -> dict[str, object]:
        """Return all immutable semantic fields without the computed fingerprint."""
        return {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "decision_id": self.decision_id,
            "revision": self.revision,
            "subject_principal_id": self.subject_principal_id,
            "sheriff_office_id": self.sheriff_office_id,
            "decision_basis": SheriffBoardDecisionBasis(self.decision_basis).value,
            "decision_kind": SheriffBoardDecisionKind(self.decision_kind).value,
            "decision_outcome": SheriffBoardDecisionOutcome(self.decision_outcome).value,
            "decision_reference": self.decision_reference,
            "decision_fingerprint": self.decision_fingerprint,
            "instrument_reference": self.instrument_reference,
            "instrument_fingerprint": self.instrument_fingerprint,
            "source_uri": self.source_uri,
            "source_observation_state": self.source_observation_state,
            "source_verification_method": self.source_verification_method,
            "source_verification_reference": self.source_verification_reference,
            "verified_by_principal_id": self.verified_by_principal_id,
            "observed_at": self.observed_at.isoformat(),
            "effective_from": self.effective_from.isoformat(),
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
            "appointment_evidence_fingerprint": self.appointment_evidence_fingerprint,
            "area_allocation_evidence_fingerprint": self.area_allocation_evidence_fingerprint,
            "appointing_sheriff_principal_id": self.appointing_sheriff_principal_id,
            "conditions_fingerprint": self.conditions_fingerprint,
            "supersedes_fingerprint": self.supersedes_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        """Hash the complete canonical decision record."""
        encoded = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return sha3_512(encoded).hexdigest()

    def to_dict(self) -> dict[str, object]:
        """Serialize documentary Board decision evidence."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @property
    def is_board_decision_current(self) -> bool:
        """A source observation never proves that the Board decision remains current."""
        return False

    @property
    def permits_operational_access(self) -> bool:
        """Board decision evidence never grants office or queue access."""
        return False

    @property
    def permits_service_execution(self) -> bool:
        """Board decision evidence never authorizes service or execution."""
        return False


__all__ = [
    "VERSION",
    "SCHEMA",
    "SheriffBoardDecisionEvidenceError",
    "SheriffBoardDecisionKind",
    "SheriffBoardDecisionBasis",
    "SheriffBoardDecisionOutcome",
    "SheriffBoardDecisionEvidence",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: sheriff_board_decision_evidence.py
# VERSION: v1.0.0-SHERIFF-BOARD-DECISION-EVIDENCE
# AUTHORITY BOUNDARY: documentary Board decisions only; no statutory currentness or operational authority
# TENANT POSTURE: exact tenant, subject, office, appointment and area-allocation references
# FAIL-CLOSED POSTURE: unsupported statutory basis/outcome, missing scope, stale or malformed evidence rejects
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
