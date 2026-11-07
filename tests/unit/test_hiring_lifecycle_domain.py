from datetime import date, datetime, timedelta, timezone

import pytest

from tools.eos.saas.domain.hiring_lifecycle import (
    CandidateApplication, CandidateStage, CandidateStageEvidence,
    EmploymentOffer, HiringLifecycleError, OfferAcceptanceEvidence,
    OfferDecision, OfferStatus, OfferTerms,
)

NOW = datetime(2026, 11, 7, 10, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"
EVIDENCE = "a" * 128


def candidate():
    return CandidateApplication(
        tenant_id=TENANT, candidate_id="CAN-001", requisition_id="REQ-001",
        candidate_profile_reference="candidate-profile://secure-source/opaque-001",
        source="CAREERS_PORTAL", created_by_principal_id="hr-manager",
        created_at=NOW,
    )


def stage_evidence(target, actor="hr-manager", reason="Completed review"):
    return CandidateStageEvidence(
        actor_principal_id=actor, target_stage=target, reason=reason,
        evidence_reference=f"hr-evidence://candidate/{target.value.lower()}",
        evidence_fingerprint=EVIDENCE, occurred_at=NOW,
    )


def offer():
    return EmploymentOffer(
        tenant_id=TENANT, offer_id="OFFER-001", requisition_id="REQ-001",
        candidate_id="CAN-001",
        terms=OfferTerms(
            position_title="Platform Engineer", employment_type="PERMANENT",
            work_location="Johannesburg", currency="ZAR",
            gross_compensation_minor=8500000, pay_frequency="MONTHLY",
            start_date=date(2027, 1, 1), expires_at=NOW + timedelta(days=21),
        ),
        prepared_by_principal_id="hr-manager", created_at=NOW,
    )


def test_candidate_pipeline_requires_sequential_evidence_backed_stages():
    value = candidate()
    with pytest.raises(HiringLifecycleError, match="TRANSITION_NOT_ALLOWED"):
        value.advance(CandidateStage.INTERVIEW, stage_evidence(CandidateStage.INTERVIEW), expected_revision=1)
    screening = value.advance(CandidateStage.SCREENING, stage_evidence(CandidateStage.SCREENING), expected_revision=1)
    interview = screening.advance(CandidateStage.INTERVIEW, stage_evidence(CandidateStage.INTERVIEW), expected_revision=2)
    references = interview.advance(CandidateStage.REFERENCE_CHECK, stage_evidence(CandidateStage.REFERENCE_CHECK), expected_revision=3)
    selected = references.advance(CandidateStage.SELECTED, stage_evidence(CandidateStage.SELECTED), expected_revision=4)
    assert selected.stage is CandidateStage.SELECTED
    assert selected.revision == 5
    with pytest.raises(HiringLifecycleError, match="TRANSITION_NOT_ALLOWED"):
        selected.advance(CandidateStage.INTERVIEW, stage_evidence(CandidateStage.INTERVIEW), expected_revision=5)


def test_candidate_decline_and_withdraw_are_explicit_terminal_outcomes():
    value = candidate()
    declined = value.advance(
        CandidateStage.DECLINED, stage_evidence(CandidateStage.DECLINED),
        expected_revision=1,
    )
    assert declined.stage is CandidateStage.DECLINED
    with pytest.raises(HiringLifecycleError, match="TRANSITION_NOT_ALLOWED"):
        declined.advance(
            CandidateStage.SCREENING, stage_evidence(CandidateStage.SCREENING),
            expected_revision=2,
        )
    withdrawn = value.advance(
        CandidateStage.WITHDRAWN, stage_evidence(CandidateStage.WITHDRAWN),
        expected_revision=1,
    )
    assert withdrawn.stage is CandidateStage.WITHDRAWN


def test_candidate_scope_and_opaque_profile_reference_are_preserved_without_pii():
    value = candidate()
    payload = value.to_dict()
    assert payload["tenant_id"] == TENANT
    assert payload["candidate_profile_reference"].startswith("candidate-profile://")
    assert "email" not in payload and "phone" not in payload and "full_name" not in payload


def test_candidate_hydration_is_strict_and_fingerprint_detects_tampering():
    value = candidate().advance(
        CandidateStage.SCREENING, stage_evidence(CandidateStage.SCREENING),
        expected_revision=1,
    )
    assert CandidateApplication.from_dict(value.to_dict()) == value
    changed = dict(value.to_dict())
    changed["candidate_profile_reference"] = "candidate-profile://tampered"
    with pytest.raises(HiringLifecycleError, match="FINGERPRINT_MISMATCH"):
        CandidateApplication.from_dict(changed)
    changed = dict(value.to_dict())
    changed["untrusted_extra"] = "not accepted"
    with pytest.raises(HiringLifecycleError, match="PERSISTED_SCHEMA_INVALID"):
        CandidateApplication.from_dict(changed)


def test_offer_requires_approval_before_sending_and_independent_maker_checker():
    value = offer()
    with pytest.raises(HiringLifecycleError, match="MUST_BE_APPROVED"):
        value.send(actor_principal_id="hr-manager", sent_at=NOW, expected_revision=1)
    submitted = value.submit(
        actor_principal_id="hr-manager", submitted_at=NOW, expected_revision=1,
    )
    with pytest.raises(HiringLifecycleError, match="MAKER_CHECKER"):
        submitted.decide(
            OfferDecision(
                decision_id="decision-self", actor_principal_id="hr-manager",
                approved=True, reason="Self approval is prohibited", decided_at=NOW,
            ),
            expected_revision=2,
        )
    approved = submitted.decide(
        OfferDecision(
            decision_id="decision-1", actor_principal_id="hr-director",
            approved=True, reason="Offer terms approved", decided_at=NOW,
        ),
        expected_revision=2,
    )
    assert approved.status is OfferStatus.APPROVED
    sent = approved.send(
        actor_principal_id="hr-manager", sent_at=NOW + timedelta(hours=1),
        expected_revision=3,
    )
    assert sent.status is OfferStatus.SENT
    assert sent.revision == 4


def test_offer_acceptance_requires_sent_offer_and_valid_acceptance_evidence():
    value = offer()
    evidence = OfferAcceptanceEvidence(
        evidence_reference="hr-document://signed-offer/opaque-001",
        evidence_fingerprint=EVIDENCE, accepted_at=NOW,
        signature_verification_reference="SOV-TEST-VERIFICATION-001",
    )
    with pytest.raises(HiringLifecycleError, match="MUST_BE_SENT"):
        value.accept(evidence, expected_revision=1)
    submitted = value.submit(
        actor_principal_id="hr-manager", submitted_at=NOW, expected_revision=1,
    )
    approved = submitted.decide(
        OfferDecision(
            decision_id="decision-1", actor_principal_id="hr-director",
            approved=True, reason="Approved", decided_at=NOW,
        ),
        expected_revision=2,
    )
    sent = approved.send(
        actor_principal_id="hr-manager", sent_at=NOW + timedelta(hours=1),
        expected_revision=3,
    )
    accepted = sent.accept(
        OfferAcceptanceEvidence(
            evidence_reference="hr-document://signed-offer/opaque-001",
            evidence_fingerprint=EVIDENCE,
            accepted_at=NOW + timedelta(hours=2),
            signature_verification_reference="SOV-TEST-VERIFICATION-001",
        ),
        expected_revision=4,
    )
    assert accepted.status is OfferStatus.ACCEPTED
    assert accepted.acceptance is not None
    payload = accepted.to_dict()
    assert "employee_id" not in payload
    assert "principal_id" not in payload
    assert "membership_id" not in payload
    assert "iam_grants" not in payload


def test_offer_expiry_and_compensation_values_are_validated():
    with pytest.raises(HiringLifecycleError, match="CURRENCY_INVALID"):
        OfferTerms(
            position_title="Engineer", employment_type="PERMANENT",
            work_location="Johannesburg", currency="ZAR1",
            gross_compensation_minor=1000, pay_frequency="MONTHLY",
            start_date=date(2027, 1, 1), expires_at=NOW + timedelta(days=2),
        )
    with pytest.raises(HiringLifecycleError, match="COMPENSATION_INVALID"):
        OfferTerms(
            position_title="Engineer", employment_type="PERMANENT",
            work_location="Johannesburg", currency="ZAR",
            gross_compensation_minor=True, pay_frequency="MONTHLY",
            start_date=date(2027, 1, 1), expires_at=NOW + timedelta(days=2),
        )


def test_offer_strict_hydration_and_fingerprint_tamper_detection():
    value = offer()
    assert EmploymentOffer.from_dict(value.to_dict()) == value
    changed = dict(value.to_dict())
    changed["candidate_id"] = "CAN-TAMPERED"
    with pytest.raises(HiringLifecycleError, match="FINGERPRINT_MISMATCH"):
        EmploymentOffer.from_dict(changed)



def test_offer_domain_rejects_acceptance_without_cryptographic_verification_reference():
    sent = offer().submit(
        actor_principal_id="hr-manager", submitted_at=NOW, expected_revision=1,
    ).decide(
        OfferDecision(
            decision_id="decision-no-signature-proof", actor_principal_id="hr-director",
            approved=True, reason="Approved", decided_at=NOW,
        ),
        expected_revision=2,
    ).send(
        actor_principal_id="hr-manager", sent_at=NOW + timedelta(hours=1),
        expected_revision=3,
    )
    evidence = OfferAcceptanceEvidence(
        evidence_reference="hr-document://signed-offer/unverified",
        evidence_fingerprint=EVIDENCE,
        accepted_at=NOW + timedelta(hours=2),
    )
    with pytest.raises(HiringLifecycleError, match="CRYPTOGRAPHIC_SIGNATURE_VERIFICATION_REQUIRED"):
        sent.accept(evidence, expected_revision=4)
