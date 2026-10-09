"""WILSY OS Legal Evidence preservation assessment domain.

TITLE: Legal Evidence Preservation Assessment
VERSION: v1.0.0-L10A2R-C4D4C-LEGAL-EVIDENCE-PRESERVATION-ASSESSMENT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Compose exact retention and legal-hold evidence for one Legal
         Evidence provider-object version into a preservation-only assessment
         without creating orphan proof or deletion authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_preservation_assessment.py
COLLABORATION / OWNERSHIP:
    C4D4A owns retention constraints. C4D4B owns legal-hold constraints.
    C4D4C composes those independently certified facts for one exact object.
    Orphan proof, deletion authorization, provider execution and reconciliation
    remain later separately certified gates.
CERTIFICATION / UPDATE DATE: 2026-09-30
CHANGELOG:
    v1.0.0-L10A2R-C4D4C establishes exact object-identity composition,
    deterministic preservation-state vocabulary and explicit caller-supplied
    assessment time while keeping all deletion/orphan authority false.
COMPLIANCE:
    Governance evidence composition only. This module does not select statutes,
    determine legal sufficiency, issue or release holds, or calculate retention
    periods.
SECURITY / PRIVACY POSTURE:
    Pure immutable in-process composition. No credentials, MongoDB, provider
    IO, raw evidence bytes, filesystem IO, network state or wall clock.
TENANT BOUNDARY:
    Retention and legal-hold constraints must bind the exact same non-global
    tenant/provider/storage/object-version identity or composition fails closed.
AUTHORITY BOUNDARY:
    Preservation assessment only. No orphan proof, disposal approval, deletion
    authorization, provider mutation, IAM, Court execution or commercial truth.
FINANCIAL AUTHORITY BOUNDARY:
    No billing, invoice, charge, payment, execution or settlement truth.
    Kennel EOS remains exclusive financial execution authority.

SEMANTIC CONTRACT:
    retention active
    -> preservation required

    legal hold blocks disposition
    -> preservation required

    retention elapsed
    + legal hold does not block
    -> no preservation block demonstrated by these two controls only

    no preservation block
    != orphan proof
    != deletion authorization
    != provider deletion execution

FAIL-CLOSED DECLARATION:
    Wrong types, cross-object composition, inconsistent assessment instant,
    impossible state and downstream-authority claims reject.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldAssessment,
    LegalEvidenceLegalHoldConstraint,
    assess_legal_evidence_legal_hold,
)
from tools.eos.legal_operations.domain.legal_evidence_retention_constraint import (
    LegalEvidenceRetentionAssessment,
    LegalEvidenceRetentionConstraint,
    assess_legal_evidence_retention,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D4C-LEGAL-EVIDENCE-PRESERVATION-ASSESSMENT"
)


class LegalEvidencePreservationAssessmentError(ValueError):
    """Stable fail-closed C4D4C preservation-composition error."""


class LegalEvidencePreservationState(StrEnum):
    """Closed preservation vocabulary; never deletion authority."""

    RETENTION_REQUIRED = "RETENTION_REQUIRED"
    LEGAL_HOLD_REQUIRED = "LEGAL_HOLD_REQUIRED"
    RETENTION_AND_LEGAL_HOLD_REQUIRED = (
        "RETENTION_AND_LEGAL_HOLD_REQUIRED"
    )
    NO_PRESERVATION_BLOCK_DEMONSTRATED = (
        "NO_PRESERVATION_BLOCK_DEMONSTRATED"
    )


def _utc(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidencePreservationAssessmentError(
            f"L10A2R_C4D4C_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _object_identity(
    constraint: LegalEvidenceRetentionConstraint
    | LegalEvidenceLegalHoldConstraint,
) -> tuple[str, str, str, str]:
    return (
        constraint.tenant_id,
        constraint.provider_name,
        constraint.storage_reference,
        constraint.object_version_reference,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidencePreservationAssessment:
    """Immutable preservation assessment for one exact provider object."""

    retention: LegalEvidenceRetentionAssessment
    legal_hold: LegalEvidenceLegalHoldAssessment
    assessed_at: datetime
    state: LegalEvidencePreservationState
    preservation_required: bool
    orphan_proven: bool = False
    deletion_authorized: bool = False
    provider_delete_authorized: bool = False

    def __post_init__(
        self,
    ) -> None:
        if type(self.retention) is not LegalEvidenceRetentionAssessment:
            raise LegalEvidencePreservationAssessmentError(
                "L10A2R_C4D4C_RETENTION_ASSESSMENT_REQUIRED"
            )

        if type(self.legal_hold) is not LegalEvidenceLegalHoldAssessment:
            raise LegalEvidencePreservationAssessmentError(
                "L10A2R_C4D4C_LEGAL_HOLD_ASSESSMENT_REQUIRED"
            )

        assessed = _utc(
            "assessed_at",
            self.assessed_at,
        )

        if (
            self.retention.assessed_at != assessed
            or self.legal_hold.assessed_at != assessed
        ):
            raise LegalEvidencePreservationAssessmentError(
                "L10A2R_C4D4C_ASSESSMENT_TIME_MISMATCH"
            )

        retention_identity = _object_identity(
            self.retention.constraint
        )
        hold_identity = _object_identity(
            self.legal_hold.constraint
        )

        if retention_identity != hold_identity:
            raise LegalEvidencePreservationAssessmentError(
                "L10A2R_C4D4C_OBJECT_IDENTITY_MISMATCH"
            )

        retention_blocks = not self.retention.retention_elapsed
        hold_blocks = self.legal_hold.disposition_blocked

        if retention_blocks and hold_blocks:
            expected_state = (
                LegalEvidencePreservationState
                .RETENTION_AND_LEGAL_HOLD_REQUIRED
            )
            expected_required = True
        elif retention_blocks:
            expected_state = (
                LegalEvidencePreservationState.RETENTION_REQUIRED
            )
            expected_required = True
        elif hold_blocks:
            expected_state = (
                LegalEvidencePreservationState.LEGAL_HOLD_REQUIRED
            )
            expected_required = True
        else:
            expected_state = (
                LegalEvidencePreservationState
                .NO_PRESERVATION_BLOCK_DEMONSTRATED
            )
            expected_required = False

        if (
            self.state is not expected_state
            or self.preservation_required is not expected_required
        ):
            raise LegalEvidencePreservationAssessmentError(
                "L10A2R_C4D4C_STATE_INVALID"
            )

        if (
            self.orphan_proven is not False
            or self.deletion_authorized is not False
            or self.provider_delete_authorized is not False
        ):
            raise LegalEvidencePreservationAssessmentError(
                "L10A2R_C4D4C_LATER_AUTHORITY_FORBIDDEN"
            )

        object.__setattr__(
            self,
            "assessed_at",
            assessed,
        )


def assess_legal_evidence_preservation(
    retention_constraint: LegalEvidenceRetentionConstraint,
    legal_hold_constraint: LegalEvidenceLegalHoldConstraint,
    *,
    assessed_at: datetime,
) -> LegalEvidencePreservationAssessment:
    """Compose retention and hold evidence without authorizing disposition."""

    if type(retention_constraint) is not LegalEvidenceRetentionConstraint:
        raise LegalEvidencePreservationAssessmentError(
            "L10A2R_C4D4C_RETENTION_CONSTRAINT_REQUIRED"
        )

    if type(legal_hold_constraint) is not LegalEvidenceLegalHoldConstraint:
        raise LegalEvidencePreservationAssessmentError(
            "L10A2R_C4D4C_LEGAL_HOLD_CONSTRAINT_REQUIRED"
        )

    assessed = _utc(
        "assessed_at",
        assessed_at,
    )

    if (
        _object_identity(retention_constraint)
        != _object_identity(legal_hold_constraint)
    ):
        raise LegalEvidencePreservationAssessmentError(
            "L10A2R_C4D4C_OBJECT_IDENTITY_MISMATCH"
        )

    retention = assess_legal_evidence_retention(
        retention_constraint,
        assessed_at=assessed,
    )

    hold = assess_legal_evidence_legal_hold(
        legal_hold_constraint,
        assessed_at=assessed,
    )

    retention_blocks = not retention.retention_elapsed
    hold_blocks = hold.disposition_blocked

    if retention_blocks and hold_blocks:
        state = (
            LegalEvidencePreservationState
            .RETENTION_AND_LEGAL_HOLD_REQUIRED
        )
        required = True
    elif retention_blocks:
        state = LegalEvidencePreservationState.RETENTION_REQUIRED
        required = True
    elif hold_blocks:
        state = LegalEvidencePreservationState.LEGAL_HOLD_REQUIRED
        required = True
    else:
        state = (
            LegalEvidencePreservationState
            .NO_PRESERVATION_BLOCK_DEMONSTRATED
        )
        required = False

    return LegalEvidencePreservationAssessment(
        retention=retention,
        legal_hold=hold,
        assessed_at=assessed,
        state=state,
        preservation_required=required,
    )


__all__ = [
    "VERSION",
    "LegalEvidencePreservationAssessment",
    "LegalEvidencePreservationAssessmentError",
    "LegalEvidencePreservationState",
    "assess_legal_evidence_preservation",
]


# ARTIFACT: legal_evidence_preservation_assessment.py
# VERSION: v1.0.0-L10A2R-C4D4C-LEGAL-EVIDENCE-PRESERVATION-ASSESSMENT
# AUTHORITY BOUNDARY: retention + legal-hold preservation composition only
# TENANT POSTURE: exact same tenant/provider/storage/object-version required
# FAIL-CLOSED POSTURE: cross-object, time mismatch, impossible state or authority claims reject
# ORPHAN POSTURE: no preservation block is not orphan proof
# DELETION POSTURE: no preservation block never authorizes deletion
# PROVIDER MUTATION POSTURE: none
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
