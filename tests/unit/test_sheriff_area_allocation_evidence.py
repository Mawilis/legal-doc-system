"""TITLE: Sheriff Section 3(2) Area Allocation Evidence Adversarial Certificate.
VERSION: v1.0.0-SHERIFF-STATUTORY-AREA-ALLOCATION-EVIDENCE-CERT
AUTHORITY: Pure immutable section 3(2) source-evidence certification only.
EPITOME: Prove distinct statutory bases, exact office/area/appointment
    provenance, separate Board consultation and FFC-readiness confirmation,
    group semantics, effective dates, lineage and no-authority guarantees.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_area_allocation_evidence.py
COLLABORATION / OWNERSHIP: Certificate for the separate section 3(2) area
    allocation evidence contract; Minister, Board, FFC, insurance, IAM and
    operational currentness remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-STATUTORY-AREA-ALLOCATION-EVIDENCE-CERT
    Establishes adversarial certification for section 3(2)(a) and (b) source
    evidence, Board prerequisite separation and non-authorizing behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and SHA3-512 digests.
TENANT BOUNDARY: Exact tenant, principal, office, appointment and area.
AUTHORITY BOUNDARY: No appointment authentication, area currentness, queue
    access, service execution, IAM, FFC/insurance authority or activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.sheriff_area_allocation_evidence import (
    SheriffAreaAllocationBasis,
    SheriffAreaAllocationEvidence,
    SheriffAreaAllocationEvidenceError,
    SheriffAreaAllocationObservationState,
    SheriffAreaAllocationVerificationMethod,
)


NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
FINGERPRINT_A = "a" * 128
FINGERPRINT_B = "b" * 128


def make_evidence(
    *,
    basis: SheriffAreaAllocationBasis = (
        SheriffAreaAllocationBasis.SECTION_3_2_A_AREA_ALLOCATION
    ),
    group: str | None = None,
    revision: int = 1,
    supersedes: str | None = None,
    effective_from: datetime = NOW - timedelta(days=1),
    effective_until: datetime | None = None,
    observation: SheriffAreaAllocationObservationState = (
        SheriffAreaAllocationObservationState.HUMAN_OBSERVED_PUBLIC_RECORD
    ),
    method: SheriffAreaAllocationVerificationMethod = (
        SheriffAreaAllocationVerificationMethod.PUBLIC_WEB_OBSERVATION
    ),
    verifier: str = "independent-verifier",
) -> SheriffAreaAllocationEvidence:
    """Build one synthetic section 3(2) allocation observation."""
    return SheriffAreaAllocationEvidence(
        tenant_id="tenant-a",
        allocation_id="allocation-1",
        revision=revision,
        sheriff_principal_id="sheriff-principal-1",
        sheriff_office_id="office-jhb",
        appointment_evidence_fingerprint=FINGERPRINT_A,
        appointed_court_reference="court-appointed",
        allocated_court_reference="court-allocated",
        district_id="district-jhb",
        service_area_reference="area-jhb-central",
        service_area_boundary_fingerprint=FINGERPRINT_B,
        allocation_basis=basis,
        ministerial_instrument_reference="ministerial-area-instrument-1",
        ministerial_instrument_fingerprint="c" * 128,
        board_consultation_reference="board-consultation-1",
        board_consultation_fingerprint="d" * 128,
        board_ffc_readiness_confirmation_reference="board-ffc-readiness-1",
        board_ffc_readiness_confirmation_fingerprint="e" * 128,
        source_uri="https://www.justice.gov.za/notice/synthetic-area-allocation",
        source_observation_state=observation,
        source_verification_method=method,
        source_verification_reference="area-observation-1",
        verified_by_principal_id=verifier,
        observed_at=NOW - timedelta(minutes=5),
        effective_from=effective_from,
        effective_until=effective_until,
        allocation_group_reference=group,
        supersedes_fingerprint=supersedes,
    )


def test_section_3_2_a_binds_exact_appointment_office_court_and_area() -> None:
    """One allocation is fingerprint-bound to its exact appointment and area."""
    value = make_evidence()
    assert value.tenant_id == "tenant-a"
    assert value.sheriff_principal_id == "sheriff-principal-1"
    assert value.sheriff_office_id == "office-jhb"
    assert value.appointed_court_reference == "court-appointed"
    assert value.allocated_court_reference == "court-allocated"
    assert value.service_area_reference == "area-jhb-central"
    assert value.appointment_evidence_fingerprint == FINGERPRINT_A
    assert value.service_area_boundary_fingerprint == FINGERPRINT_B
    assert len(value.fingerprint) == 128
    assert value.is_statutorily_current is False
    assert value.permits_operational_access is False
    assert value.permits_service_execution is False


def test_section_3_2_b_requires_explicit_additional_sheriff_group() -> None:
    """Multiple-sheriff appointments cannot be represented as an ungrouped area."""
    with pytest.raises(SheriffAreaAllocationEvidenceError) as caught:
        make_evidence(
            basis=SheriffAreaAllocationBasis.SECTION_3_2_B_ADDITIONAL_SHERIFF
        )
    assert caught.value.code == "SHERIFF_AREA_ALLOCATION_GROUP_REQUIRED"

    grouped = make_evidence(
        basis=SheriffAreaAllocationBasis.SECTION_3_2_B_ADDITIONAL_SHERIFF,
        group="multiple-sheriffs-area-group-1",
    )
    assert grouped.allocation_group_reference == "multiple-sheriffs-area-group-1"

    with pytest.raises(SheriffAreaAllocationEvidenceError) as caught:
        make_evidence(group="unexpected-group")
    assert caught.value.code == "SHERIFF_AREA_ALLOCATION_GROUP_UNEXPECTED"


def test_board_consultation_and_written_ffc_readiness_are_distinct_required_inputs() -> None:
    """The Board's consultation and written FFC readiness are separately fingerprinted."""
    value = make_evidence()
    assert value.board_consultation_reference != value.board_ffc_readiness_confirmation_reference
    assert value.board_consultation_fingerprint != value.board_ffc_readiness_confirmation_fingerprint

    with pytest.raises(SheriffAreaAllocationEvidenceError) as caught:
        SheriffAreaAllocationEvidence(
            tenant_id="tenant-a",
            allocation_id="allocation-1",
            revision=1,
            sheriff_principal_id="sheriff-principal-1",
            sheriff_office_id="office-jhb",
            appointment_evidence_fingerprint=FINGERPRINT_A,
            appointed_court_reference="court-appointed",
            allocated_court_reference="court-allocated",
            district_id="district-jhb",
            service_area_reference="area-jhb-central",
            service_area_boundary_fingerprint=FINGERPRINT_B,
            allocation_basis=SheriffAreaAllocationBasis.SECTION_3_2_A_AREA_ALLOCATION,
            ministerial_instrument_reference="ministerial-area-instrument-1",
            ministerial_instrument_fingerprint="c" * 128,
            board_consultation_reference="board-consultation-1",
            board_consultation_fingerprint="d" * 128,
            board_ffc_readiness_confirmation_reference="",
            board_ffc_readiness_confirmation_fingerprint="e" * 128,
            source_uri="https://www.justice.gov.za/notice/synthetic-area-allocation",
            source_observation_state=SheriffAreaAllocationObservationState.HUMAN_OBSERVED_PUBLIC_RECORD,
            source_verification_method=SheriffAreaAllocationVerificationMethod.PUBLIC_WEB_OBSERVATION,
            source_verification_reference="area-observation-1",
            verified_by_principal_id="independent-verifier",
            observed_at=NOW,
            effective_from=NOW,
            effective_until=None,
        )
    assert caught.value.code == "SHERIFF_AREA_ALLOCATION_BOARD_FFC_READINESS_CONFIRMATION_REFERENCE_INVALID"


def test_self_attestation_and_source_method_mismatch_reject() -> None:
    """The sheriff cannot verify their own allocation and method labels must match."""
    with pytest.raises(SheriffAreaAllocationEvidenceError) as caught:
        make_evidence(verifier="sheriff-principal-1")
    assert caught.value.code == "SHERIFF_AREA_ALLOCATION_SELF_ATTESTATION_FORBIDDEN"

    with pytest.raises(SheriffAreaAllocationEvidenceError) as caught:
        make_evidence(
            observation=SheriffAreaAllocationObservationState.AUTHENTICATED_RESPONSE,
            method=SheriffAreaAllocationVerificationMethod.PUBLIC_WEB_OBSERVATION,
        )
    assert caught.value.code == "SHERIFF_AREA_ALLOCATION_OBSERVATION_METHOD_MISMATCH"


def test_effective_window_and_revision_lineage_are_explicit() -> None:
    """Invalid term windows and root/successor lineage gaps reject."""
    with pytest.raises(SheriffAreaAllocationEvidenceError) as caught:
        make_evidence(
            effective_from=NOW,
            effective_until=NOW,
        )
    assert caught.value.code == "SHERIFF_AREA_ALLOCATION_EFFECTIVE_WINDOW_INVALID"

    with pytest.raises(SheriffAreaAllocationEvidenceError) as caught:
        make_evidence(revision=2)
    assert caught.value.code == "SHERIFF_AREA_ALLOCATION_SUCCESSOR_REQUIRED"

    with pytest.raises(SheriffAreaAllocationEvidenceError) as caught:
        make_evidence(supersedes=FINGERPRINT_A)
    assert caught.value.code == "SHERIFF_AREA_ALLOCATION_ROOT_SUPERSEDES_FORBIDDEN"

    successor = make_evidence(revision=2, supersedes=FINGERPRINT_A)
    assert successor.supersedes_fingerprint == FINGERPRINT_A


def test_semantic_fingerprint_is_deterministic_and_tamper_evident() -> None:
    """The complete statutory and source provenance payload is fingerprinted."""
    value = make_evidence()
    assert value.fingerprint == make_evidence().fingerprint
    assert value.to_dict()["fingerprint"] == value.fingerprint
    with pytest.raises(SheriffAreaAllocationEvidenceError) as caught:
        replace(value, fingerprint="0" * 128)
    assert caught.value.code == "SHERIFF_AREA_ALLOCATION_FINGERPRINT_MISMATCH"


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("tenant_id", "global"),
        ("sheriff_principal_id", ""),
        ("service_area_reference", " "),
        ("ministerial_instrument_fingerprint", "not-a-digest"),
        ("board_consultation_fingerprint", "g" * 128),
        ("service_area_boundary_fingerprint", "f" * 128),
    ],
)
def test_invalid_scope_and_fingerprints_reject(field: str, bad_value: str) -> None:
    """Malformed or pseudo identities and non-SHA3 fingerprints are rejected."""
    with pytest.raises(SheriffAreaAllocationEvidenceError):
        replace(make_evidence(), **{field: bad_value})
