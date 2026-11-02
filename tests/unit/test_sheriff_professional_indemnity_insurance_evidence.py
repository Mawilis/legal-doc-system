"""TITLE: Sheriff Professional Indemnity Insurance Evidence Certificate.
VERSION: v1.0.0-SHERIFF-PROFESSIONAL-INDEMNITY-INSURANCE-EVIDENCE-CERT
AUTHORITY: Pure immutable PI policy evidence certification only.
EPITOME: Prove exact policyholder and covered-principal mapping, capacity,
    appointment fingerprints, integer cover/deductible, currency, Board
    acceptance and minimum-standard links, validity, cancellation and no-
    authority guarantees under Sheriffs Act section 30(1)(b)-(2).
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_professional_indemnity_insurance_evidence.py
COLLABORATION / OWNERSHIP: Certificate for separate Sheriff PI insurance
    evidence; Board satisfaction/currentness, FFC, statutory appointment,
    identity and IAM remain separate.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-PROFESSIONAL-INDEMNITY-INSURANCE-EVIDENCE-CERT
    Adds adversarial tests for policy scope, coverage terms, Board links,
    cancellation, source provenance and no-authority guarantees.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and integer minor units.
TENANT BOUNDARY: Exact tenant, policyholder, covered principals, office and appointments.
AUTHORITY BOUNDARY: No Board satisfaction, insurance currentness, FFC, queue,
    service, IAM or production activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentCapacity,
    SheriffSourceObservationState,
    SheriffSourceVerificationMethod,
)
from tools.eos.legal_operations.domain.sheriff_professional_indemnity_insurance_evidence import (
    SheriffPiInsuranceEvidenceError,
    SheriffPiPolicyObservedStatus,
    SheriffProfessionalIndemnityInsuranceEvidence,
)


UTC = timezone.utc
ISSUED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
START = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
END = datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC)
OBSERVED = datetime(2026, 1, 2, 12, 0, tzinfo=UTC)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


def make_policy(
    *,
    status: SheriffPiPolicyObservedStatus = SheriffPiPolicyObservedStatus.ACTIVE,
    cancelled_at: datetime | None = None,
    cancellation_reference: str | None = None,
    cancellation_fingerprint: str | None = None,
    covered_principal_ids: tuple[str, ...] = (
        "sheriff-principal-1",
        "deputy-principal-1",
    ),
    covered_capacities: tuple[SheriffAppointmentCapacity, ...] = (
        SheriffAppointmentCapacity.SHERIFF,
        SheriffAppointmentCapacity.DEPUTY_SHERIFF,
    ),
    appointment_fingerprints: tuple[str, ...] = (FP_A, FP_C),
    coverage_amount_minor: int = 50_000_000,
    deductible_amount_minor: int = 250_000,
    currency_code: str = "ZAR",
    observation: SheriffSourceObservationState = (
        SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD
    ),
    method: SheriffSourceVerificationMethod = (
        SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION
    ),
) -> SheriffProfessionalIndemnityInsuranceEvidence:
    """Build one synthetic Sheriff/deputy PI insurance policy observation."""
    return SheriffProfessionalIndemnityInsuranceEvidence(
        tenant_id="tenant-a",
        policy_evidence_id="pi-policy-evidence-1",
        revision=1,
        policyholder_principal_id="sheriff-principal-1",
        covered_principal_ids=covered_principal_ids,
        covered_capacities=covered_capacities,
        sheriff_office_id="office-jhb",
        appointment_evidence_fingerprints=appointment_fingerprints,
        insurer_reference="insurer-reference-1",
        policy_reference="pi-policy-2026-1",
        policy_fingerprint=FP_A,
        coverage_scope_fingerprint=FP_B,
        coverage_amount_minor=coverage_amount_minor,
        deductible_amount_minor=deductible_amount_minor,
        currency_code=currency_code,
        board_acceptance_reference="board-pi-acceptance-1",
        board_acceptance_fingerprint=FP_C,
        board_minimum_standard_reference="board-pi-standard-2026",
        board_minimum_standard_fingerprint="d" * 128,
        issued_at=ISSUED,
        valid_from=START,
        valid_until=END,
        observed_status=status,
        source_uri="https://sheriffs.org.za/legal-obligations/synthetic-pi-policy",
        source_observation_state=observation,
        source_verification_method=method,
        source_verification_reference="pi-observation-1",
        verified_by_principal_id="independent-verifier",
        observed_at=OBSERVED if cancelled_at is None else cancelled_at,
        cancelled_at=cancelled_at,
        cancellation_reference=cancellation_reference,
        cancellation_fingerprint=cancellation_fingerprint,
    )


def test_policy_binds_exact_covered_people_office_appointments_and_board_links() -> None:
    """Every covered natural-person principal maps positionally to capacity and appointment."""
    value = make_policy()
    assert value.covered_principal_ids == (
        "sheriff-principal-1",
        "deputy-principal-1",
    )
    assert value.covered_capacities == (
        SheriffAppointmentCapacity.SHERIFF,
        SheriffAppointmentCapacity.DEPUTY_SHERIFF,
    )
    assert value.appointment_evidence_fingerprints == (FP_A, FP_C)
    assert value.sheriff_office_id == "office-jhb"
    assert value.board_acceptance_reference == "board-pi-acceptance-1"
    assert value.board_minimum_standard_reference == "board-pi-standard-2026"
    assert value.is_current is False
    assert value.permits_operational_access is False
    assert value.permits_service_execution is False


def test_multiple_deputies_can_share_the_same_covered_capacity() -> None:
    """Coverage capacity is positional; repeated Deputy capacity is valid."""
    value = make_policy(
        covered_principal_ids=(
            "sheriff-principal-1",
            "deputy-principal-1",
            "deputy-principal-2",
        ),
        covered_capacities=(
            SheriffAppointmentCapacity.SHERIFF,
            SheriffAppointmentCapacity.DEPUTY_SHERIFF,
            SheriffAppointmentCapacity.DEPUTY_SHERIFF,
        ),
        appointment_fingerprints=(FP_A, FP_B, FP_C),
    )
    assert len(value.covered_principal_ids) == 3
    assert value.covered_capacities[1] is SheriffAppointmentCapacity.DEPUTY_SHERIFF
    assert value.covered_capacities[2] is SheriffAppointmentCapacity.DEPUTY_SHERIFF


def test_missing_or_misaligned_appointment_scope_rejects() -> None:
    """Every covered principal requires its own exact appointment fingerprint."""
    with pytest.raises(SheriffPiInsuranceEvidenceError) as caught:
        make_policy(appointment_fingerprints=(FP_A,))
    assert caught.value.code == "SHERIFF_PI_INSURANCE_APPOINTMENT_FINGERPRINT_SCOPE_INVALID"

    with pytest.raises(SheriffPiInsuranceEvidenceError):
        make_policy(
            covered_principal_ids=("sheriff-principal-1", "sheriff-principal-1")
        )


def test_coverage_amount_currency_and_board_acceptance_are_required() -> None:
    """No hard-coded cover minimum; the exact Board standard and acceptance are linked."""
    with pytest.raises(SheriffPiInsuranceEvidenceError):
        make_policy(coverage_amount_minor=0)
    with pytest.raises(SheriffPiInsuranceEvidenceError):
        make_policy(deductible_amount_minor=-1)
    with pytest.raises(SheriffPiInsuranceEvidenceError):
        make_policy(currency_code="Zar")
    with pytest.raises(SheriffPiInsuranceEvidenceError):
        replace(make_policy(), board_acceptance_reference="")


def test_cancellation_requires_board_source_reference_and_chronology() -> None:
    """An observed cancellation cannot be represented by a local status flag."""
    cancelled = make_policy(
        status=SheriffPiPolicyObservedStatus.CANCELLED,
        cancelled_at=datetime(2026, 3, 1, 0, 0, tzinfo=UTC),
        cancellation_reference="insurer-cancellation-1",
        cancellation_fingerprint="e" * 128,
    )
    assert cancelled.observed_status is SheriffPiPolicyObservedStatus.CANCELLED

    with pytest.raises(SheriffPiInsuranceEvidenceError):
        make_policy(status=SheriffPiPolicyObservedStatus.CANCELLED)

    with pytest.raises(SheriffPiInsuranceEvidenceError):
        make_policy(
            status=SheriffPiPolicyObservedStatus.ACTIVE,
            cancelled_at=datetime(2026, 3, 1, 0, 0, tzinfo=UTC),
            cancellation_reference="insurer-cancellation-1",
            cancellation_fingerprint="e" * 128,
        )


def test_source_provenance_and_verifier_independence_are_enforced() -> None:
    """Public observation labels cannot claim authenticated regulator responses."""
    with pytest.raises(SheriffPiInsuranceEvidenceError):
        replace(make_policy(), verified_by_principal_id="sheriff-principal-1")

    with pytest.raises(SheriffPiInsuranceEvidenceError):
        make_policy(
            observation=SheriffSourceObservationState.AUTHENTICATED_RESPONSE,
            method=SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
        )


def test_policy_successor_and_fingerprint_tampering_reject() -> None:
    """Policy successor lineage and complete semantic fingerprint are enforced."""
    with pytest.raises(SheriffPiInsuranceEvidenceError):
        replace(make_policy(), revision=2)

    with pytest.raises(SheriffPiInsuranceEvidenceError):
        replace(make_policy(), supersedes_fingerprint=FP_A)

    successor = replace(
        make_policy(),
        revision=2,
        supersedes_fingerprint=FP_A,
        fingerprint="",
    )
    assert successor.supersedes_fingerprint == FP_A

    with pytest.raises(SheriffPiInsuranceEvidenceError):
        replace(make_policy(), fingerprint="0" * 128)
