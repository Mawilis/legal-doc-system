"""TITLE: Sheriff Fidelity Fund Certificate Evidence Adversarial Certificate.
VERSION: v1.0.0-SHERIFF-FIDELITY-FUND-CERTIFICATE-EVIDENCE-CERT
AUTHORITY: Pure immutable Board-issued FFC evidence certification only.
EPITOME: Prove section 32(2) year-end validity, section 32(3) acting fixed
    terms, exact principal/office/appointment scope, cancellation evidence,
    source provenance, chronology and no-authority guarantees.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_fidelity_fund_certificate_evidence.py
COLLABORATION / OWNERSHIP: Certificate for the separate Sheriff FFC evidence
    contract; Ministerial appointment, Board readiness, insurance, identity,
    currentness, IAM and contribution alternatives remain separate.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-FIDELITY-FUND-CERTIFICATE-EVIDENCE-CERT
    Establishes adversarial certification for annual and acting fixed-term
    Fidelity Fund Certificate observations and cancellation records.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and SHA3-512 digests.
TENANT BOUNDARY: Exact tenant, natural-person principal, Sheriff office,
    appointment and certificate scope.
AUTHORITY BOUNDARY: No Board authentication, FFC currentness, insurance,
    contribution proof, queue access, service execution, IAM or activation.
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
from tools.eos.legal_operations.domain.sheriff_fidelity_fund_certificate_evidence import (
    SheriffFfcEvidence,
    SheriffFfcEvidenceError,
    SheriffFfcObservedStatus,
    SheriffFfcValidityBasis,
)


UTC = timezone.utc
ISSUED = datetime(2025, 11, 30, 12, 0, tzinfo=UTC)
START = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
END = datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC)
OBSERVED = datetime(2026, 1, 2, 12, 0, tzinfo=UTC)
FP_A = "a" * 128
FP_B = "b" * 128


def make_annual(
    *,
    capacity: SheriffAppointmentCapacity = SheriffAppointmentCapacity.SHERIFF,
    status: SheriffFfcObservedStatus = SheriffFfcObservedStatus.ISSUED,
    cancelled_at: datetime | None = None,
    cancellation_reference: str | None = None,
    cancellation_fingerprint: str | None = None,
    observation: SheriffSourceObservationState = (
        SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD
    ),
    method: SheriffSourceVerificationMethod = (
        SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION
    ),
) -> SheriffFfcEvidence:
    """Build one synthetic section 32(2) annual certificate."""
    return SheriffFfcEvidence(
        tenant_id="tenant-a",
        certificate_id="ffc-2026-1",
        revision=1,
        subject_principal_id="sheriff-principal-1",
        subject_capacity=capacity,
        sheriff_office_id="office-jhb",
        appointment_evidence_fingerprint=FP_A,
        certificate_reference="ffc-reference-2026-1",
        certificate_fingerprint=FP_B,
        issuer_reference="south-african-board-for-sheriffs",
        validity_basis=SheriffFfcValidityBasis.SECTION_32_2_CALENDAR_YEAR,
        issued_at=ISSUED,
        valid_from=START,
        valid_until=END,
        observed_status=status,
        source_uri="https://sheriffs.org.za/fidelity-fund/synthetic-ffc",
        source_observation_state=observation,
        source_verification_method=method,
        source_verification_reference="ffc-observation-1",
        verified_by_principal_id="independent-verifier",
        observed_at=OBSERVED if cancelled_at is None else cancelled_at,
        certificate_year=2026,
        cancelled_at=cancelled_at,
        cancellation_reference=cancellation_reference,
        cancellation_fingerprint=cancellation_fingerprint,
    )


def make_acting(
    *,
    capacity: SheriffAppointmentCapacity = SheriffAppointmentCapacity.ACTING_SHERIFF,
    valid_from: datetime = START,
    valid_until: datetime = datetime(2026, 7, 1, 0, 0, tzinfo=UTC),
) -> SheriffFfcEvidence:
    """Build one synthetic section 32(3) acting-sheriff fixed-term certificate."""
    return SheriffFfcEvidence(
        tenant_id="tenant-a",
        certificate_id="acting-ffc-2026-1",
        revision=1,
        subject_principal_id="acting-sheriff-principal-1",
        subject_capacity=capacity,
        sheriff_office_id="office-jhb",
        appointment_evidence_fingerprint=FP_A,
        certificate_reference="acting-ffc-reference-2026-1",
        certificate_fingerprint=FP_B,
        issuer_reference="south-african-board-for-sheriffs",
        validity_basis=SheriffFfcValidityBasis.SECTION_32_3_ACTING_FIXED_TERM,
        issued_at=ISSUED,
        valid_from=valid_from,
        valid_until=valid_until,
        observed_status=SheriffFfcObservedStatus.ISSUED,
        source_uri="https://sheriffs.org.za/fidelity-fund/synthetic-acting-ffc",
        source_observation_state=SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD,
        source_verification_method=SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
        source_verification_reference="acting-ffc-observation-1",
        verified_by_principal_id="independent-verifier",
        observed_at=OBSERVED,
        certificate_year=None,
    )


def test_section_32_2_certificate_expires_at_end_of_explicit_certificate_year() -> None:
    """Calendar-year validity is explicit and never inferred from issue date."""
    value = make_annual()
    assert value.validity_basis is SheriffFfcValidityBasis.SECTION_32_2_CALENDAR_YEAR
    assert value.certificate_year == 2026
    assert value.valid_until == END
    assert value.is_current is False
    assert value.permits_operational_access is False
    assert value.permits_service_execution is False


def test_section_32_3_acting_fixed_term_is_between_one_month_and_one_year() -> None:
    """Only acting-sheriff certificates can use the section 32(3) fixed-term path."""
    value = make_acting()
    assert value.validity_basis is SheriffFfcValidityBasis.SECTION_32_3_ACTING_FIXED_TERM
    assert value.subject_capacity is SheriffAppointmentCapacity.ACTING_SHERIFF

    with pytest.raises(SheriffFfcEvidenceError) as caught:
        make_acting(valid_until=START + timedelta(days=29))
    assert caught.value.code == "SHERIFF_FFC_ACTING_TERM_OUT_OF_RANGE"

    with pytest.raises(SheriffFfcEvidenceError) as caught:
        make_acting(valid_until=datetime(2027, 1, 1, tzinfo=UTC))
    assert caught.value.code == "SHERIFF_FFC_ACTING_TERM_OUT_OF_RANGE"

    with pytest.raises(SheriffFfcEvidenceError) as caught:
        make_acting(capacity=SheriffAppointmentCapacity.SHERIFF)
    assert caught.value.code == "SHERIFF_FFC_SECTION_32_3_ACTING_ONLY"


def test_annual_certificate_year_and_year_end_must_match() -> None:
    """An annual FFC cannot claim a different year or arbitrary expiry."""
    with pytest.raises(SheriffFfcEvidenceError) as caught:
        replace(make_annual(), valid_until=datetime(2027, 12, 31, 23, 59, 59, tzinfo=UTC))
    assert caught.value.code == "SHERIFF_FFC_CALENDAR_YEAR_END_MISMATCH"


def test_cancellation_requires_distinct_reference_fingerprint_and_chronology() -> None:
    """Observed cancellation is an explicit Board source record, not a local flag."""
    cancelled = make_annual(
        status=SheriffFfcObservedStatus.CANCELLED,
        cancelled_at=datetime(2026, 2, 1, 0, 0, tzinfo=UTC),
        cancellation_reference="board-cancellation-1",
        cancellation_fingerprint="c" * 128,
    )
    assert cancelled.observed_status is SheriffFfcObservedStatus.CANCELLED

    with pytest.raises(SheriffFfcEvidenceError) as caught:
        make_annual(status=SheriffFfcObservedStatus.CANCELLED)
    assert caught.value.code == "SHERIFF_FFC_CANCELLATION_EVIDENCE_REQUIRED"

    with pytest.raises(SheriffFfcEvidenceError) as caught:
        make_annual(
            status=SheriffFfcObservedStatus.ISSUED,
            cancelled_at=datetime(2026, 2, 1, 0, 0, tzinfo=UTC),
            cancellation_reference="board-cancellation-1",
            cancellation_fingerprint="c" * 128,
        )
    assert caught.value.code == "SHERIFF_FFC_UNEXPECTED_CANCELLATION_EVIDENCE"


def test_source_method_and_subject_verifier_are_independent() -> None:
    """Source provenance labels and verifier independence are checked."""
    with pytest.raises(SheriffFfcEvidenceError):
        replace(make_annual(), verified_by_principal_id="sheriff-principal-1")

    with pytest.raises(SheriffFfcEvidenceError) as caught:
        make_annual(
            observation=SheriffSourceObservationState.AUTHENTICATED_RESPONSE,
            method=SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
        )
    assert caught.value.code == "SHERIFF_FFC_SOURCE_METHOD_MISMATCH"


def test_successor_lineage_and_fingerprint_tampering_reject() -> None:
    """A successor requires a predecessor; source changes cannot reuse a fingerprint."""
    with pytest.raises(SheriffFfcEvidenceError):
        replace(make_annual(), revision=2)

    with pytest.raises(SheriffFfcEvidenceError):
        replace(make_annual(), supersedes_fingerprint=FP_A)

    successor = replace(
        make_annual(),
        revision=2,
        supersedes_fingerprint=FP_A,
        fingerprint="",
    )
    assert successor.supersedes_fingerprint == FP_A

    with pytest.raises(SheriffFfcEvidenceError):
        replace(make_annual(), fingerprint="0" * 128)


def test_acting_contribution_alternative_is_not_misrepresented_as_an_ffc() -> None:
    """This certificate record has no contribution field or implicit substitute."""
    value = make_acting()
    assert not hasattr(value, "prescribed_contribution_reference")
    assert value.is_current is False
