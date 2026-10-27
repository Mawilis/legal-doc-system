"""Direct certificate for the G64 ratification workspace evidence model.

VERSION: v1.0.0-G64-CLICK-ATTESTATION-EVIDENCE-TEST
AUTHORITY: Pure evidence-model tests only; no route, persistence or access activation.
"""
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64ClickAttestation,
    G64Disposition,
    G64EvidenceReference,
    G64RatificationWorkspaceRecord,
    G64RecordState,
    G64WorkspaceEvidenceError,
    new_pending_decisions,
)

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)
FINGERPRINT = "a" * 128


def draft(**overrides):
    values = {
        "record_id": "g64-record-001",
        "institution_id": "wilsy-pty-ltd",
        "ratifier_principal_id": "principal-pending-verification",
        "contract_version": "v1.0.0-P47-R95-G62-DRAFT",
        "contract_sha3_512_fingerprint": FINGERPRINT,
        "created_at": NOW,
        "state": G64RecordState.DRAFT,
        "decisions": new_pending_decisions(),
    }
    values.update(overrides)
    return G64RatificationWorkspaceRecord(**values)


def test_new_record_keeps_all_ten_decisions_undecided_and_denies_authority():
    record = draft()
    assert record.unresolved_decision_ids == tuple(f"D{i:02}" for i in range(1, 11))
    assert record.permits_operational_access is False
    assert record.permits_reviewer_authorization is False
    assert record.claims_wall_enforcement is False
    document = record.to_document()
    assert document["authority_effect"] == "NONE"
    assert document["permits_operational_access"] is False


def test_fingerprint_is_deterministic_and_secret_free():
    record = draft()
    assert record.evidence_fingerprint() == record.evidence_fingerprint()
    assert len(record.evidence_fingerprint()) == 128
    assert record.to_document()["evidence_sha3_512"] == record.evidence_fingerprint()


def test_decision_register_must_include_exact_canonical_d01_to_d10():
    with pytest.raises(G64WorkspaceEvidenceError, match="DECISIONS_MUST_BE_COMPLETE_AND_CANONICAL"):
        draft(decisions=new_pending_decisions()[:-1])


def test_undecided_entry_cannot_smuggle_disposition_fields():
    from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import G64DecisionEntry

    with pytest.raises(G64WorkspaceEvidenceError, match="UNDECIDED_ENTRY_HAS_DECISION_FIELDS"):
        G64DecisionEntry(decision_id="D01", rationale="implicitly approved")


def test_selected_disposition_requires_scope_evidence_and_temporal_controls():
    from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import G64DecisionEntry

    evidence = G64EvidenceReference("evidence://governance/instrument-1", FINGERPRINT)
    selected = G64DecisionEntry(
        decision_id="D01",
        disposition=G64Disposition.APPROVE,
        rationale="Decision rationale recorded by the authorized decision maker.",
        scope=("institution:wilsy-pty-ltd", "operation:reviewer-role-grant"),
        accountable_source_owner="governance-owner-pending-independent-verification",
        evidence=(evidence,),
        effective_from=NOW,
        expires_or_review_at=NOW + timedelta(days=30),
        revocation_rule="Revoke on authority withdrawal or at expiry; deny until reverified.",
    )
    record = draft(decisions=(selected, *new_pending_decisions()[1:]))
    assert record.unresolved_decision_ids == tuple(f"D{i:02}" for i in range(2, 11))
    assert record.permits_operational_access is False


def test_invalid_fingerprint_is_rejected():
    with pytest.raises(G64WorkspaceEvidenceError, match="CONTRACT_FINGERPRINT_INVALID"):
        draft(contract_sha3_512_fingerprint="not-a-fingerprint")


def test_review_time_must_follow_effective_time():
    from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import G64DecisionEntry

    evidence = G64EvidenceReference("evidence://governance/instrument-1", FINGERPRINT)
    with pytest.raises(G64WorkspaceEvidenceError, match="REVIEW_MUST_FOLLOW_EFFECTIVE_TIME"):
        G64DecisionEntry(
            decision_id="D01",
            disposition=G64Disposition.DEFER,
            rationale="Defer pending verified institutional evidence.",
            scope=("institution:wilsy-pty-ltd",),
            accountable_source_owner="governance-owner-pending-independent-verification",
            evidence=(evidence,),
            effective_from=NOW,
            expires_or_review_at=NOW,
            revocation_rule="No access while deferred; re-review before any change.",
        )


def test_click_attestation_fingerprint_survives_lifecycle_transition_without_circularity():
    initial = draft()
    attestation = G64ClickAttestation(
        event_id="attestation-event-001",
        authenticated_principal_id="principal-pending-verification",
        authenticated_request_reference="session-ref-001",
        attested_at=NOW,
        record_sha3_512_fingerprint=initial.evidence_fingerprint(),
        attestation_text_version="g64-attestation-copy-v1",
    )
    attested = draft(
        state=G64RecordState.ATTESTED_PENDING_VERIFICATION,
        attestation=attestation,
    )
    assert attested.evidence_fingerprint() == initial.evidence_fingerprint()
    assert attested.to_document()["attestation"]["signature_kind"] == (
        "AUTHENTICATED_CLICK_TO_ATTEST_NOT_CRYPTOGRAPHIC_SIGNATURE"
    )
