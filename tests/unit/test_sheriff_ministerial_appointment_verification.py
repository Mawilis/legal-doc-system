"""TITLE: Sheriff Ministerial Appointment Verification Adversarial Certificate.
VERSION: v1.0.0-SHERIFF-MINISTERIAL-APPOINTMENT-VERIFICATION-CERT
AUTHORITY: Pure non-authorizing ministerial appointment verification only.
EPITOME: Prove capture digest, exact tenant/principal/subject/instrument scope,
    actor lifecycle, freshness, effective-window and trust-root denial behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_ministerial_appointment_verification.py
COLLABORATION / OWNERSHIP: Legal Operations source evidence and canonical
    principal lifecycle contracts; no statutory issuer trust root or IAM grant.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-MINISTERIAL-APPOINTMENT-VERIFICATION-CERT
    Adds adversarial tests for ministerial appointment verification and
    explicit denial while no authenticated Minister trust root exists.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and source bytes only.
TENANT BOUNDARY: Exact tenant, principal, actor, subject and instrument scope.
AUTHORITY BOUNDARY: No statutory appointment, IAM, office access, queue access,
    legal execution or production activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha3_512

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
from tools.eos.legal_operations.domain.sheriff_ministerial_appointment_verification import (
    MinisterialAppointmentCapture,
    MinisterialAppointmentFreshnessPolicy,
    MinisterialAppointmentVerificationDecision,
    MinisterialAppointmentVerificationReason,
    SheriffMinisterialAppointmentVerificationError,
    verify_ministerial_appointment,
)


NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
PAYLOAD = b'{"synthetic":"ministerial-appointment-instrument"}'
DIGEST = sha3_512(PAYLOAD).hexdigest()
INSTRUMENT_DIGEST = "a" * 128


def make_evidence(
    *,
    tenant_id: str = "tenant-a",
    effective_from: datetime = NOW - timedelta(days=1),
    effective_until: datetime | None = None,
    observation: SheriffSourceObservationState = (
        SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD
    ),
) -> SheriffAppointmentSourceEvidence:
    """Build one synthetic section 2(1) Minister-issued appointment observation."""
    return SheriffAppointmentSourceEvidence(
        tenant_id=tenant_id,
        evidence_id="appointment-evidence-1",
        revision=1,
        principal_id="sheriff-principal-1",
        verified_subject_reference="subject-reference-1",
        sheriff_office_id="office-jhb",
        district_id="district-jhb",
        court_reference="court-jhb",
        service_area_references=("area-jhb-central",),
        capacity=SheriffAppointmentCapacity.SHERIFF,
        statutory_basis=SheriffAppointmentStatutoryBasis.SECTION_2_1,
        issuer_authority=SheriffAppointmentIssuerAuthority.MINISTER,
        instrument_reference="ministerial-instrument-1",
        instrument_fingerprint=INSTRUMENT_DIGEST,
        source_uri="https://www.justice.gov.za/notice/synthetic-appointment",
        source_observation_state=observation,
        source_verification_method=(
            SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION
        ),
        source_verification_reference="observation-reference-1",
        verified_by_principal_id="independent-verifier",
        observed_at=NOW - timedelta(minutes=5),
        effective_from=effective_from,
        effective_until=effective_until,
    )


def make_capture(
    *,
    tenant_id: str = "tenant-a",
    principal_id: str = "sheriff-principal-1",
    checked_at: datetime = NOW - timedelta(minutes=5),
    instrument_reference: str = "ministerial-instrument-1",
    instrument_fingerprint: str = INSTRUMENT_DIGEST,
) -> MinisterialAppointmentCapture:
    """Build one transient capture bound to the exact source observation."""
    return MinisterialAppointmentCapture(
        tenant_id=tenant_id,
        actor_principal_id="verifier-principal-1",
        principal_id=principal_id,
        subject_reference="subject-reference-1",
        instrument_reference=instrument_reference,
        instrument_fingerprint=instrument_fingerprint,
        source_uri="https://www.justice.gov.za/notice/synthetic-appointment",
        source_verification_reference="observation-reference-1",
        checked_at=checked_at,
        captured_payload=PAYLOAD,
        capture_digest=DIGEST,
    )


def make_policy(
    max_capture_age: timedelta | None = timedelta(hours=24),
) -> MinisterialAppointmentFreshnessPolicy:
    """Build one explicit Wilsy observation-age policy."""
    return MinisterialAppointmentFreshnessPolicy(
        policy_id="ministerial-appointment-policy-1",
        max_capture_age=max_capture_age,
    )


def verify(
    *,
    evidence: SheriffAppointmentSourceEvidence | None = None,
    capture: MinisterialAppointmentCapture | None = None,
    actor: PrincipalAuthority | None = None,
    policy: MinisterialAppointmentFreshnessPolicy | None = None,
    evaluated_at: datetime = NOW,
) -> MinisterialAppointmentVerificationDecision:
    """Evaluate one exact-scope appointment capture."""
    return verify_ministerial_appointment(
        evidence=evidence or make_evidence(),
        capture=capture or make_capture(),
        actor_authority=actor
        or PrincipalAuthority("verifier-principal-1", PrincipalStatus.ACTIVE, 1),
        policy=policy or make_policy(),
        evaluated_at=evaluated_at,
    )


def test_best_documentary_capture_still_denies_without_minister_trust_root() -> None:
    """A clean public observation is never promoted to statutory appointment."""
    decision = verify()
    assert (
        decision.reason
        is MinisterialAppointmentVerificationReason.MINISTERIAL_ISSUER_TRUST_ROOT_UNAVAILABLE
    )
    assert decision.statutory_appointment_current is False
    assert decision.permits_operational_access is False
    assert decision.permits_legal_execution is False
    assert PAYLOAD not in repr(decision).encode("utf-8")
    assert decision.replay_identity == verify().replay_identity


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (PrincipalStatus.SUSPENDED, MinisterialAppointmentVerificationReason.ACTOR_INACTIVE),
        (PrincipalStatus.REVOKED, MinisterialAppointmentVerificationReason.ACTOR_INACTIVE),
    ],
)
def test_inactive_verifier_denies(
    status: PrincipalStatus,
    expected: MinisterialAppointmentVerificationReason,
) -> None:
    """Only an active exact verifier principal can reach source evaluation."""
    actor = PrincipalAuthority("verifier-principal-1", status, 2)
    assert verify(actor=actor).reason is expected


@pytest.mark.parametrize(
    ("capture", "expected"),
    [
        (
            make_capture(tenant_id="tenant-b"),
            MinisterialAppointmentVerificationReason.ACTOR_SCOPE_MISMATCH,
        ),
        (
            make_capture(principal_id="different-principal"),
            MinisterialAppointmentVerificationReason.ACTOR_SCOPE_MISMATCH,
        ),
        (
            make_capture(instrument_reference="different-instrument"),
            MinisterialAppointmentVerificationReason.INSTRUMENT_SCOPE_MISMATCH,
        ),
        (
            make_capture(instrument_fingerprint="b" * 128),
            MinisterialAppointmentVerificationReason.INSTRUMENT_SCOPE_MISMATCH,
        ),
    ],
)
def test_exact_tenant_principal_and_instrument_scope_denies(
    capture: MinisterialAppointmentCapture,
    expected: MinisterialAppointmentVerificationReason,
) -> None:
    """Cross-tenant or changed subject/instrument context cannot verify."""
    assert verify(capture=capture).reason is expected


def test_unavailable_disputed_and_unverified_source_states_deny() -> None:
    """Negative source states remain blocked before issuer trust evaluation."""
    for state, expected in (
        (
            SheriffSourceObservationState.UNVERIFIED_SUBMISSION,
            MinisterialAppointmentVerificationReason.SOURCE_UNVERIFIED,
        ),
        (
            SheriffSourceObservationState.DISPUTED,
            MinisterialAppointmentVerificationReason.SOURCE_DISPUTED,
        ),
        (
            SheriffSourceObservationState.SOURCE_UNAVAILABLE,
            MinisterialAppointmentVerificationReason.SOURCE_UNAVAILABLE,
        ),
    ):
        item = make_evidence(observation=state)
        assert verify(evidence=item).reason is expected


def test_missing_freshness_policy_denies() -> None:
    """Unknown capture-age policy is not interpreted as unlimited freshness."""
    assert (
        verify(policy=make_policy(None)).reason
        is MinisterialAppointmentVerificationReason.FRESHNESS_POLICY_UNKNOWN
    )


@pytest.mark.parametrize(
    ("checked_at", "expected"),
    [
        (
            NOW + timedelta(seconds=1),
            MinisterialAppointmentVerificationReason.CAPTURE_FUTURE_DATED,
        ),
        (
            NOW - timedelta(days=2),
            MinisterialAppointmentVerificationReason.CAPTURE_STALE,
        ),
    ],
)
def test_future_or_stale_capture_denies(
    checked_at: datetime,
    expected: MinisterialAppointmentVerificationReason,
) -> None:
    """Capture chronology and the explicit age policy are enforced."""
    assert verify(capture=make_capture(checked_at=checked_at)).reason is expected


def test_appointment_effective_window_is_checked_independently() -> None:
    """Future and expired instrument terms cannot be represented as current."""
    future = make_evidence(effective_from=NOW + timedelta(days=1))
    expired = make_evidence(
        effective_from=NOW - timedelta(days=10),
        effective_until=NOW,
    )
    assert (
        verify(evidence=future).reason
        is MinisterialAppointmentVerificationReason.APPOINTMENT_NOT_YET_EFFECTIVE
    )
    assert (
        verify(evidence=expired).reason
        is MinisterialAppointmentVerificationReason.APPOINTMENT_EXPIRED
    )


def test_capture_payload_digest_mismatch_rejects_at_boundary() -> None:
    """A caller cannot pair source bytes with a different claimed digest."""
    with pytest.raises(SheriffMinisterialAppointmentVerificationError):
        MinisterialAppointmentCapture(
            tenant_id="tenant-a",
            actor_principal_id="verifier-principal-1",
            principal_id="sheriff-principal-1",
            subject_reference="subject-reference-1",
            instrument_reference="ministerial-instrument-1",
            instrument_fingerprint=INSTRUMENT_DIGEST,
            source_uri="https://www.justice.gov.za/notice/synthetic-appointment",
            source_verification_reference="observation-reference-1",
            checked_at=NOW,
            captured_payload=PAYLOAD,
            capture_digest="0" * 128,
        )


def test_decision_cannot_be_constructed_or_replaced() -> None:
    """The decision issuer is private to the verifier and cannot be forged."""
    decision = verify()
    with pytest.raises(SheriffMinisterialAppointmentVerificationError):
        MinisterialAppointmentVerificationDecision()
    with pytest.raises(SheriffMinisterialAppointmentVerificationError):
        replace(decision, reason=MinisterialAppointmentVerificationReason.ACTOR_INACTIVE)
