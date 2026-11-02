"""TITLE: Sheriff Natural-Person Identity Principal Binding Certificate.
VERSION: v1.0.0-SHERIFF-NATURAL-PERSON-PRINCIPAL-BINDING-CERT
AUTHORITY: Pure privacy-minimizing identity/principal binding certification only.
EPITOME: Prove exact issuer subject, WILSY principal, Ministerial appointment,
    Sheriff office, capacity, tenant, proof validity, binding validity and
    fail-closed identity issuer trust-root behavior without retaining PII.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_natural_person_principal_binding.py
COLLABORATION / OWNERSHIP: Certificate for identity issuer, WILSY principal
    and Sheriff appointment linkage; no identity issuer trust root or IAM grant.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-NATURAL-PERSON-PRINCIPAL-BINDING-CERT
    Adds adversarial tests for identity proof integrity, exact appointment
    binding, temporal validity, privacy and no-authority guarantees.
COMPLIANCE: POPIA sections 10, 19; GDPR Articles 5, 25, 32; SOC 2 CC6.1.
SECURITY / PRIVACY POSTURE: Synthetic opaque subject references and fingerprints;
    no identity numbers, names, DOBs, addresses, biometrics or raw documents.
TENANT BOUNDARY: Exact tenant, identity subject, principal, office and appointment.
AUTHORITY BOUNDARY: No verified identity, statutory appointment, IAM, queue,
    service, legal execution or production activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentCapacity,
    SheriffAppointmentIssuerAuthority,
    SheriffAppointmentSourceEvidence,
    SheriffAppointmentStatutoryBasis,
    SheriffSourceObservationState,
    SheriffSourceVerificationMethod,
)
from tools.eos.legal_operations.domain.sheriff_natural_person_principal_binding import (
    SheriffNaturalPersonBindingDecision,
    SheriffNaturalPersonBindingDecision,
    SheriffNaturalPersonBindingError,
    SheriffNaturalPersonBindingReason,
    SheriffNaturalPersonIdentityProof,
    SheriffNaturalPersonPrincipalBinding,
    verify_sheriff_natural_person_binding,
)


NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


def make_appointment(
    *,
    tenant_id: str = "tenant-a",
    principal_id: str = "sheriff-principal-1",
    subject_reference: str = "subject-reference-1",
) -> SheriffAppointmentSourceEvidence:
    """Build one synthetic Minister-issued Sheriff appointment."""
    return SheriffAppointmentSourceEvidence(
        tenant_id=tenant_id,
        evidence_id="appointment-evidence-1",
        revision=1,
        principal_id=principal_id,
        verified_subject_reference=subject_reference,
        sheriff_office_id="office-jhb",
        district_id="district-jhb",
        court_reference="court-jhb",
        service_area_references=("area-jhb-central",),
        capacity=SheriffAppointmentCapacity.SHERIFF,
        statutory_basis=SheriffAppointmentStatutoryBasis.SECTION_2_1,
        issuer_authority=SheriffAppointmentIssuerAuthority.MINISTER,
        instrument_reference="ministerial-instrument-1",
        instrument_fingerprint=FP_A,
        source_uri="https://www.justice.gov.za/notice/synthetic-appointment",
        source_observation_state=SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD,
        source_verification_method=SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
        source_verification_reference="appointment-observation-1",
        verified_by_principal_id="appointment-verifier",
        observed_at=NOW - timedelta(minutes=5),
        effective_from=NOW - timedelta(days=30),
        effective_until=None,
    )


def make_proof(
    *,
    tenant_id: str = "tenant-a",
    subject_reference: str = "subject-reference-1",
    observation: SheriffSourceObservationState = (
        SheriffSourceObservationState.AUTHENTICATED_RESPONSE
    ),
    method: SheriffSourceVerificationMethod = (
        SheriffSourceVerificationMethod.AUTHENTICATED_REGULATOR_RESPONSE
    ),
    valid_from: datetime = NOW - timedelta(days=1),
    valid_until: datetime = NOW + timedelta(days=1),
) -> SheriffNaturalPersonIdentityProof:
    """Build one synthetic opaque identity-issuer assertion."""
    return SheriffNaturalPersonIdentityProof(
        tenant_id=tenant_id,
        identity_proof_id="identity-proof-1",
        revision=1,
        identity_subject_reference=subject_reference,
        identity_issuer_reference="identity-issuer-1",
        identity_proof_reference="identity-proof-reference-1",
        identity_proof_fingerprint=FP_B,
        source_uri="https://identity.example.invalid/verification/opaque-reference",
        source_observation_state=observation,
        source_verification_method=method,
        source_verification_reference="identity-observation-1",
        verified_by_principal_id="identity-verifier",
        observed_at=NOW - timedelta(minutes=5),
        valid_from=valid_from,
        valid_until=valid_until,
    )


def make_binding(
    appointment: SheriffAppointmentSourceEvidence | None = None,
    *,
    tenant_id: str = "tenant-a",
    principal_id: str = "sheriff-principal-1",
    subject_reference: str = "subject-reference-1",
    office_id: str = "office-jhb",
    appointment_fingerprint: str | None = None,
    bound_by: str = "binding-verifier",
    effective_from: datetime = NOW - timedelta(days=1),
    effective_until: datetime | None = None,
) -> SheriffNaturalPersonPrincipalBinding:
    """Build one exact WILSY principal-to-natural-person binding."""
    exact_appointment = appointment or make_appointment()
    return SheriffNaturalPersonPrincipalBinding(
        tenant_id=tenant_id,
        principal_id=principal_id,
        identity_subject_reference=subject_reference,
        identity_proof_fingerprint=FP_B,
        appointment_evidence_fingerprint=(
            appointment_fingerprint or exact_appointment.fingerprint
        ),
        sheriff_office_id=office_id,
        capacity="SHERIFF",
        bound_by_principal_id=bound_by,
        effective_from=effective_from,
        effective_until=effective_until,
    )


def verify(
    *,
    proof: SheriffNaturalPersonIdentityProof | None = None,
    binding: SheriffNaturalPersonPrincipalBinding | None = None,
    appointment: SheriffAppointmentSourceEvidence | None = None,
    actor: PrincipalAuthority | None = None,
    evaluated_at: datetime = NOW,
) -> SheriffNaturalPersonBindingDecision:
    """Evaluate one exact natural-person identity/principal binding."""
    exact_appointment = appointment or make_appointment()
    return verify_sheriff_natural_person_binding(
        proof=proof or make_proof(),
        binding=binding or make_binding(exact_appointment),
        appointment=exact_appointment,
        actor_authority=actor or PrincipalAuthority(
            "binding-verifier", PrincipalStatus.ACTIVE, 1
        ),
        evaluated_at=evaluated_at,
    )


def test_best_identity_response_still_denies_without_identity_issuer_trust_root() -> None:
    """An authenticated-response label cannot itself authenticate an issuer."""
    decision = verify()
    assert (
        decision.reason
        is SheriffNaturalPersonBindingReason.IDENTITY_ISSUER_TRUST_ROOT_UNAVAILABLE
    )
    assert decision.natural_person_identity_verified is False
    assert decision.permits_operational_access is False
    assert decision.permits_legal_execution is False
    assert decision.replay_identity == verify().replay_identity


def test_exact_tenant_subject_principal_office_and_appointment_scope_is_required() -> None:
    """Cross-tenant, subject, principal, office or appointment mismatch denies."""
    appointment = make_appointment()
    assert (
        verify(binding=make_binding(appointment, tenant_id="tenant-b")).reason
        is SheriffNaturalPersonBindingReason.TENANT_SCOPE_MISMATCH
    )
    assert (
        verify(binding=make_binding(appointment, subject_reference="different-subject")).reason
        is SheriffNaturalPersonBindingReason.SUBJECT_SCOPE_MISMATCH
    )
    assert (
        verify(binding=make_binding(appointment, principal_id="different-principal")).reason
        is SheriffNaturalPersonBindingReason.PRINCIPAL_SCOPE_MISMATCH
    )
    assert (
        verify(binding=make_binding(appointment, office_id="different-office")).reason
        is SheriffNaturalPersonBindingReason.APPOINTMENT_SCOPE_MISMATCH
    )
    assert (
        verify(binding=make_binding(appointment, appointment_fingerprint=FP_A)).reason
        is SheriffNaturalPersonBindingReason.APPOINTMENT_SCOPE_MISMATCH
    )


def test_identity_proof_fingerprint_and_authenticated_source_are_required() -> None:
    """Proof and binding must carry the same exact issuer proof fingerprint."""
    with pytest.raises(SheriffNaturalPersonBindingError):
        make_proof(observation=SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD)

    proof = make_proof(observation=SheriffSourceObservationState.UNVERIFIED_SUBMISSION)
    decision = verify(proof=proof)
    assert decision.reason is SheriffNaturalPersonBindingReason.IDENTITY_PROOF_NOT_AUTHENTICATED


def test_inactive_or_wrong_binding_actor_denies() -> None:
    """Only the active exact independent binding actor may evaluate the proof."""
    actor = PrincipalAuthority("binding-verifier", PrincipalStatus.REVOKED, 2)
    assert (
        verify(actor=actor).reason
        is SheriffNaturalPersonBindingReason.ACTOR_INACTIVE
    )
    wrong_actor = PrincipalAuthority("different-verifier", PrincipalStatus.ACTIVE, 2)
    assert (
        verify(actor=wrong_actor).reason
        is SheriffNaturalPersonBindingReason.ACTOR_SCOPE_MISMATCH
    )


def test_identity_proof_and_binding_effective_windows_are_checked() -> None:
    """Future and expired proof or binding windows cannot pass."""
    future_proof = make_proof(
        valid_from=NOW + timedelta(days=1),
        valid_until=NOW + timedelta(days=2),
    )
    assert (
        verify(proof=future_proof).reason
        is SheriffNaturalPersonBindingReason.IDENTITY_PROOF_NOT_YET_VALID
    )
    expired_proof = make_proof(
        valid_from=NOW - timedelta(days=3),
        valid_until=NOW,
    )
    assert (
        verify(proof=expired_proof).reason
        is SheriffNaturalPersonBindingReason.IDENTITY_PROOF_EXPIRED
    )
    future_binding = make_binding(effective_from=NOW + timedelta(days=1))
    assert (
        verify(binding=future_binding).reason
        is SheriffNaturalPersonBindingReason.BINDING_NOT_YET_EFFECTIVE
    )
    expired_binding = make_binding(
        effective_from=NOW - timedelta(days=3),
        effective_until=NOW,
    )
    assert (
        verify(binding=expired_binding).reason
        is SheriffNaturalPersonBindingReason.BINDING_EXPIRED
    )


def test_self_binding_and_forged_decisions_reject() -> None:
    """A principal cannot bind itself and callers cannot construct decisions."""
    with pytest.raises(SheriffNaturalPersonBindingError):
        make_binding(bound_by="sheriff-principal-1")
    with pytest.raises(SheriffNaturalPersonBindingError):
        SheriffNaturalPersonBindingDecision()
