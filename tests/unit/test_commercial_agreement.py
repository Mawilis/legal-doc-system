from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.entitlement.commercial_agreement import (
    CommercialAgreement,
    CommercialAgreementError,
    CommercialAgreementState,
    CommercialRenewalMode,
)
from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialOfferId,
    get_commercial_offer,
)

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-CERT-001"
AGREEMENT = "WILSY-AGREEMENT-CERT-001"
OFFER = get_commercial_offer(CommercialOfferId.LEGAL_OPERATIONS)


def draft(**overrides):
    values = {
        "tenant_id": TENANT,
        "agreement_id": AGREEMENT,
        "offer_id": OFFER.offer_id,
        "offer_fingerprint": OFFER.fingerprint,
        "contract_reference": "CONTRACT-CERT-001",
        "contract_version": "2026-11-01",
        "counterparty_legal_name": "Certificate Counterparty (Pty) Ltd",
        "effective_at": NOW,
        "expires_at": NOW + timedelta(days=365),
        "renewal_mode": CommercialRenewalMode.MANUAL,
        "notice_days": 30,
        "termination_terms_reference": "TERMS-CERT-001",
    }
    values.update(overrides)
    return CommercialAgreement(**values)


def test_draft_is_immutable_and_fingerprint_is_deterministic():
    first = draft()
    second = draft()
    assert first.fingerprint == second.fingerprint
    assert first.lifecycle_state is CommercialAgreementState.DRAFT
    assert first.to_dict()["offer_fingerprint"] == OFFER.fingerprint
    with pytest.raises(FrozenInstanceError):
        first.notice_days = 45


def test_agreement_binds_exact_canonical_offer_fingerprint():
    with pytest.raises(CommercialAgreementError, match="OFFER_BINDING_INVALID"):
        draft(offer_fingerprint="0" * 128)


@pytest.mark.parametrize("tenant", ["global", "root", "master", "*", "default"])
def test_pseudo_tenant_is_rejected(tenant):
    with pytest.raises(CommercialAgreementError, match="TENANT_(?:ID_)?INVALID"):
        draft(tenant_id=tenant)


def test_contract_and_terms_references_are_required():
    with pytest.raises(CommercialAgreementError, match="CONTRACT_REFERENCE_INVALID"):
        draft(contract_reference="")
    with pytest.raises(CommercialAgreementError, match="TERMINATION_TERMS_REFERENCE_INVALID"):
        draft(termination_terms_reference=" ")


def test_term_must_be_ordered_and_timezone_aware():
    with pytest.raises(CommercialAgreementError, match="TERM_INVALID"):
        draft(expires_at=NOW)
    with pytest.raises(CommercialAgreementError, match="EFFECTIVE_AT_INVALID"):
        draft(effective_at=datetime(2026, 11, 6, 12, 0))


def test_notice_days_are_bounded_and_boolean_is_not_an_integer():
    with pytest.raises(CommercialAgreementError, match="NOTICE_DAYS_INVALID"):
        draft(notice_days=True)
    with pytest.raises(CommercialAgreementError, match="NOTICE_DAYS_INVALID"):
        draft(notice_days=366)


def test_draft_cannot_carry_execution_or_activation_evidence():
    with pytest.raises(CommercialAgreementError, match="DRAFT_SHAPE_INVALID"):
        draft(
            executed_at=NOW,
            execution_evidence_reference="SIGNATURE-EVIDENCE-1",
            execution_evidence_fingerprint="a" * 128,
        )


def test_executed_agreement_requires_verified_evidence_coordinates():
    with pytest.raises(CommercialAgreementError, match="EXECUTION_REQUIRED"):
        draft(lifecycle_state=CommercialAgreementState.EXECUTED)


def test_executed_agreement_accepts_complete_evidence_pair():
    agreement = draft(
        lifecycle_state=CommercialAgreementState.EXECUTED,
        executed_at=NOW,
        execution_evidence_reference="SIGNATURE-EVIDENCE-1",
        execution_evidence_fingerprint="a" * 128,
    )
    assert agreement.lifecycle_state is CommercialAgreementState.EXECUTED
    assert agreement.executed_at == NOW


def test_active_agreement_requires_execution_and_activation_evidence():
    with pytest.raises(CommercialAgreementError, match="ACTIVATION_EVIDENCE_REQUIRED"):
        draft(
            lifecycle_state=CommercialAgreementState.ACTIVE,
            executed_at=NOW,
            execution_evidence_reference="SIGNATURE-EVIDENCE-1",
            execution_evidence_fingerprint="a" * 128,
        )


def test_active_agreement_binds_both_execution_and_activation_evidence():
    agreement = draft(
        lifecycle_state=CommercialAgreementState.ACTIVE,
        executed_at=NOW,
        execution_evidence_reference="SIGNATURE-EVIDENCE-1",
        execution_evidence_fingerprint="a" * 128,
        activated_at=NOW + timedelta(minutes=1),
        activation_evidence_reference="ACTIVATION-APPROVAL-1",
        activation_evidence_fingerprint="b" * 128,
    )
    assert agreement.lifecycle_state is CommercialAgreementState.ACTIVE
    assert agreement.to_dict()["activation_evidence_reference"] == "ACTIVATION-APPROVAL-1"


def test_execution_and_activation_evidence_pairs_must_be_complete():
    with pytest.raises(CommercialAgreementError, match="EVIDENCE_PAIR_INVALID"):
        draft(
            lifecycle_state=CommercialAgreementState.EXECUTED,
            executed_at=NOW,
            execution_evidence_reference="SIGNATURE-EVIDENCE-1",
        )


def test_execution_cannot_postdate_activation():
    with pytest.raises(CommercialAgreementError, match="ACTIVATION_CHRONOLOGY_INVALID"):
        draft(
            lifecycle_state=CommercialAgreementState.ACTIVE,
            executed_at=NOW + timedelta(minutes=2),
            execution_evidence_reference="SIGNATURE-EVIDENCE-1",
            execution_evidence_fingerprint="a" * 128,
            activated_at=NOW + timedelta(minutes=1),
            activation_evidence_reference="ACTIVATION-APPROVAL-1",
            activation_evidence_fingerprint="b" * 128,
        )


def test_supplied_fingerprint_must_match_canonical_snapshot():
    with pytest.raises(CommercialAgreementError, match="FINGERPRINT_MISMATCH"):
        draft(fingerprint="f" * 128)


def test_lifecycle_transitions_are_immutable_revisioned_and_evidence_bound():
    draft_agreement = draft()
    executed = draft_agreement.transition(
        CommercialAgreementState.EXECUTED,
        expected_revision=0,
        evidence_reference="SIGNATURE-EVIDENCE-1",
        evidence_fingerprint="a" * 128,
        occurred_at=NOW,
    )
    active = executed.transition(
        CommercialAgreementState.ACTIVE,
        expected_revision=1,
        evidence_reference="ACTIVATION-APPROVAL-1",
        evidence_fingerprint="b" * 128,
        occurred_at=NOW + timedelta(minutes=1),
    )
    suspended = active.transition(
        CommercialAgreementState.SUSPENDED,
        expected_revision=2,
        evidence_reference="SUSPENSION-DECISION-1",
        evidence_fingerprint="c" * 128,
        occurred_at=NOW + timedelta(minutes=2),
    )
    terminated = suspended.transition(
        CommercialAgreementState.TERMINATED,
        expected_revision=3,
        evidence_reference="TERMINATION-DECISION-1",
        evidence_fingerprint="d" * 128,
        occurred_at=NOW + timedelta(minutes=3),
    )
    assert [item.lifecycle_revision for item in (draft_agreement, executed, active, suspended, terminated)] == [0, 1, 2, 3, 4]
    assert draft_agreement.lifecycle_state is CommercialAgreementState.DRAFT
    assert terminated.lifecycle_state is CommercialAgreementState.TERMINATED
    assert len({item.fingerprint for item in (draft_agreement, executed, active, suspended, terminated)}) == 5


def test_stale_revision_and_illegal_lifecycle_transition_reject():
    agreement = draft()
    with pytest.raises(CommercialAgreementError, match="STALE_REVISION"):
        agreement.transition(
            CommercialAgreementState.EXECUTED,
            expected_revision=1,
            evidence_reference="SIGNATURE-EVIDENCE-1",
            evidence_fingerprint="a" * 128,
            occurred_at=NOW,
        )
    with pytest.raises(CommercialAgreementError, match="TRANSITION_NOT_ALLOWED"):
        agreement.transition(
            CommercialAgreementState.ACTIVE,
            expected_revision=0,
            evidence_reference="ACTIVATION-APPROVAL-1",
            evidence_fingerprint="b" * 128,
            occurred_at=NOW,
        )


def test_expiry_requires_elapsed_contract_term_and_independent_evidence():
    active = draft(
        lifecycle_state=CommercialAgreementState.ACTIVE,
        executed_at=NOW,
        execution_evidence_reference="SIGNATURE-EVIDENCE-1",
        execution_evidence_fingerprint="a" * 128,
        activated_at=NOW + timedelta(minutes=1),
        activation_evidence_reference="ACTIVATION-APPROVAL-1",
        activation_evidence_fingerprint="b" * 128,
    )
    with pytest.raises(CommercialAgreementError, match="EXPIRY_CHRONOLOGY_INVALID"):
        active.transition(
            CommercialAgreementState.EXPIRED,
            expected_revision=0,
            evidence_reference="EXPIRY-DECISION-1",
            evidence_fingerprint="c" * 128,
            occurred_at=NOW + timedelta(days=1),
        )
    expired = active.transition(
        CommercialAgreementState.EXPIRED,
        expected_revision=0,
        evidence_reference="EXPIRY-DECISION-1",
        evidence_fingerprint="c" * 128,
        occurred_at=NOW + timedelta(days=366),
    )
    assert expired.lifecycle_state is CommercialAgreementState.EXPIRED
