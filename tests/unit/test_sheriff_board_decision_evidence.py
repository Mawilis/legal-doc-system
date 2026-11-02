"""TITLE: Sheriff Board Decision Evidence Adversarial Certificate.
VERSION: v1.0.0-SHERIFF-BOARD-DECISION-EVIDENCE-CERT
AUTHORITY: Pure immutable Board decision evidence certification only.
EPITOME: Prove statutory basis/kind/outcome compatibility, separate approval,
    consultation, FFC-readiness and exemption semantics, exact target linkage,
    source provenance, effective windows, lineage and no-authority guarantees.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_board_decision_evidence.py
COLLABORATION / OWNERSHIP: Certificate for the distinct Board decision
    evidence contract; Ministerial appointment, area allocation, FFC,
    insurance, identity, currentness and IAM remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-BOARD-DECISION-EVIDENCE-CERT
    Establishes adversarial certification for Board approvals, consultations,
    FFC-readiness confirmations and section 30(3) exemptions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and SHA3-512 digests.
TENANT BOUNDARY: Exact tenant, subject, office, appointment and area scope.
AUTHORITY BOUNDARY: No Board authentication, current approval, FFC/insurance,
    identity proof, queue access, service execution, IAM or activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffSourceObservationState,
    SheriffSourceVerificationMethod,
)
from tools.eos.legal_operations.domain.sheriff_board_decision_evidence import (
    SheriffBoardDecisionBasis,
    SheriffBoardDecisionEvidence,
    SheriffBoardDecisionEvidenceError,
    SheriffBoardDecisionKind,
    SheriffBoardDecisionOutcome,
)


NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


def make_evidence(
    *,
    basis: SheriffBoardDecisionBasis = SheriffBoardDecisionBasis.SECTION_6_1,
    kind: SheriffBoardDecisionKind = SheriffBoardDecisionKind.DEPUTY_APPOINTMENT_APPROVAL,
    outcome: SheriffBoardDecisionOutcome = SheriffBoardDecisionOutcome.APPROVED,
    appointment_fp: str | None = FP_A,
    area_fp: str | None = None,
    appointing_sheriff: str | None = "sheriff-principal-1",
    verifier: str = "board-evidence-verifier",
    revision: int = 1,
    supersedes: str | None = None,
    effective_from: datetime = NOW - timedelta(days=1),
    effective_until: datetime | None = None,
    observation: SheriffSourceObservationState = (
        SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD
    ),
    method: SheriffSourceVerificationMethod = (
        SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION
    ),
) -> SheriffBoardDecisionEvidence:
    """Build one synthetic Board decision evidence record."""
    return SheriffBoardDecisionEvidence(
        tenant_id="tenant-a",
        decision_id="board-decision-1",
        revision=revision,
        subject_principal_id="subject-principal-1",
        sheriff_office_id="office-jhb",
        decision_basis=basis,
        decision_kind=kind,
        decision_outcome=outcome,
        decision_reference="board-resolution-1",
        decision_fingerprint=FP_B,
        instrument_reference="statutory-instrument-1",
        instrument_fingerprint="c" * 128,
        source_uri="https://sheriffs.org.za/circulars/synthetic-board-decision",
        source_observation_state=observation,
        source_verification_method=method,
        source_verification_reference="board-observation-1",
        verified_by_principal_id=verifier,
        observed_at=NOW - timedelta(minutes=5),
        effective_from=effective_from,
        effective_until=effective_until,
        appointment_evidence_fingerprint=appointment_fp,
        area_allocation_evidence_fingerprint=area_fp,
        appointing_sheriff_principal_id=appointing_sheriff,
        conditions_fingerprint="d" * 128,
        supersedes_fingerprint=supersedes,
    )


def test_section_6_1_board_deputy_approval_is_distinct_and_non_authorizing() -> None:
    """Section 6(1) approval binds appointing Sheriff and exact appointment."""
    value = make_evidence()
    assert value.decision_basis is SheriffBoardDecisionBasis.SECTION_6_1
    assert value.decision_kind is SheriffBoardDecisionKind.DEPUTY_APPOINTMENT_APPROVAL
    assert value.decision_outcome is SheriffBoardDecisionOutcome.APPROVED
    assert value.appointing_sheriff_principal_id == "sheriff-principal-1"
    assert value.is_board_decision_current is False
    assert value.permits_operational_access is False
    assert value.permits_service_execution is False
    assert len(value.fingerprint) == 128


def test_consultation_is_not_approval_or_ffc_readiness() -> None:
    """Distinct Board actions cannot be conflated by outcome labels."""
    consultation = make_evidence(
        basis=SheriffBoardDecisionBasis.SECTION_3_2,
        kind=SheriffBoardDecisionKind.CONSULTATION,
        outcome=SheriffBoardDecisionOutcome.CONSULTED,
        area_fp=FP_A,
        appointing_sheriff=None,
    )
    readiness = make_evidence(
        basis=SheriffBoardDecisionBasis.SECTION_3_2,
        kind=SheriffBoardDecisionKind.FFC_READINESS_CONFIRMATION,
        outcome=SheriffBoardDecisionOutcome.PREPARED_TO_ISSUE_FFC,
        area_fp=FP_A,
        appointing_sheriff=None,
    )
    assert consultation.decision_kind is SheriffBoardDecisionKind.CONSULTATION
    assert readiness.decision_kind is SheriffBoardDecisionKind.FFC_READINESS_CONFIRMATION
    assert consultation.fingerprint != readiness.fingerprint

    with pytest.raises(SheriffBoardDecisionEvidenceError) as caught:
        make_evidence(
            basis=SheriffBoardDecisionBasis.SECTION_3_2,
            kind=SheriffBoardDecisionKind.CONSULTATION,
            outcome=SheriffBoardDecisionOutcome.APPROVED,
            area_fp=FP_A,
            appointing_sheriff=None,
        )
    assert caught.value.code == "SHERIFF_BOARD_DECISION_BASIS_KIND_OUTCOME_MISMATCH"


def test_section_5_1_b_readiness_confirmation_is_not_an_ffc() -> None:
    """Board readiness to issue an FFC is not certificate issuance."""
    value = make_evidence(
        basis=SheriffBoardDecisionBasis.SECTION_5_1_B,
        kind=SheriffBoardDecisionKind.FFC_READINESS_CONFIRMATION,
        outcome=SheriffBoardDecisionOutcome.PREPARED_TO_ISSUE_FFC,
        appointing_sheriff=None,
    )
    assert value.decision_outcome is SheriffBoardDecisionOutcome.PREPARED_TO_ISSUE_FFC
    assert value.is_board_decision_current is False


def test_section_30_3_exemption_is_narrowly_tied_to_section_5_1_a() -> None:
    """Only the specific exemption basis can carry the section 30(3) outcome."""
    value = make_evidence(
        basis=SheriffBoardDecisionBasis.SECTION_30_3_FOR_SECTION_5_1_A,
        kind=SheriffBoardDecisionKind.SECTION_30_EXEMPTION,
        outcome=SheriffBoardDecisionOutcome.EXEMPTED,
        appointing_sheriff=None,
    )
    assert value.decision_kind is SheriffBoardDecisionKind.SECTION_30_EXEMPTION

    with pytest.raises(SheriffBoardDecisionEvidenceError):
        make_evidence(
            basis=SheriffBoardDecisionBasis.SECTION_6_1,
            kind=SheriffBoardDecisionKind.SECTION_30_EXEMPTION,
            outcome=SheriffBoardDecisionOutcome.EXEMPTED,
        )


def test_area_decisions_require_both_appointment_and_area_allocation_linkage() -> None:
    """Section 3(2) decisions are tied to the exact area allocation and appointment."""
    with pytest.raises(SheriffBoardDecisionEvidenceError) as caught:
        make_evidence(
            basis=SheriffBoardDecisionBasis.SECTION_3_2,
            kind=SheriffBoardDecisionKind.CONSULTATION,
            outcome=SheriffBoardDecisionOutcome.CONSULTED,
            appointing_sheriff=None,
        )
    assert caught.value.code == "SHERIFF_BOARD_DECISION_AREA_ALLOCATION_LINK_REQUIRED"

    valid = make_evidence(
        basis=SheriffBoardDecisionBasis.SECTION_3_2,
        kind=SheriffBoardDecisionKind.CONSULTATION,
        outcome=SheriffBoardDecisionOutcome.CONSULTED,
        area_fp=FP_B,
        appointing_sheriff=None,
    )
    assert valid.area_allocation_evidence_fingerprint == FP_B


def test_section_6_1_requires_a_distinct_appointing_sheriff() -> None:
    """A deputy approval must identify the appointing Sheriff and reject self-appointment."""
    with pytest.raises(SheriffBoardDecisionEvidenceError):
        make_evidence(appointing_sheriff=None)

    with pytest.raises(SheriffBoardDecisionEvidenceError):
        make_evidence(appointing_sheriff="subject-principal-1")


def test_source_observation_method_and_self_attestation_are_enforced() -> None:
    """Source method labels and independent verifier identity are checked."""
    with pytest.raises(SheriffBoardDecisionEvidenceError):
        make_evidence(verifier="subject-principal-1")

    with pytest.raises(SheriffBoardDecisionEvidenceError):
        make_evidence(
            observation=SheriffSourceObservationState.AUTHENTICATED_RESPONSE,
            method=SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
        )


def test_effective_window_and_append_only_lineage_are_checked() -> None:
    """Invalid validity windows and root/successor lineage gaps reject."""
    with pytest.raises(SheriffBoardDecisionEvidenceError):
        make_evidence(effective_from=NOW, effective_until=NOW)

    with pytest.raises(SheriffBoardDecisionEvidenceError):
        make_evidence(revision=2)

    with pytest.raises(SheriffBoardDecisionEvidenceError):
        make_evidence(supersedes=FP_A)

    successor = make_evidence(revision=2, supersedes=FP_A)
    assert successor.supersedes_fingerprint == FP_A


def test_fingerprint_tampering_rejects() -> None:
    """Every semantic Board decision field is bound by the fingerprint."""
    value = make_evidence()
    assert value.fingerprint == make_evidence().fingerprint
    assert value.to_dict()["fingerprint"] == value.fingerprint
    with pytest.raises(SheriffBoardDecisionEvidenceError):
        replace(value, fingerprint="0" * 128)
