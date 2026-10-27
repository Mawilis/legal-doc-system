"""G64 independent verification and second-approval evidence certificates."""
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64EvidenceReference,
    G64WorkspaceEvidenceError,
)
from tools.eos.legal_operations.domain.g64_ratification_workspace_verification import (
    G64IndependentVerification,
    G64SecondApproval,
    G64SecondApprovalPolicyDecision,
    G64VerificationCheck,
    G64VerificationFinding,
    G64VerificationOutcome,
)

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)
FINGERPRINT = "a" * 128
RECORD_FINGERPRINT = "b" * 128
EVIDENCE = G64EvidenceReference("evidence:source-001", FINGERPRINT)


def finding(check, passed=True):
    return G64VerificationFinding(
        check=check,
        passed=passed,
        rationale="Checked against the independently supplied evidence source.",
        evidence=(EVIDENCE,),
    )


def passing_verification():
    return G64IndependentVerification(
        verification_id="verification-001",
        tenant_id="tenant-001",
        institution_id="institution-001",
        record_id="record-001",
        record_sha3_512_fingerprint=RECORD_FINGERPRINT,
        ratifier_principal_id="principal-ratifier",
        verifier_principal_id="principal-independent-verifier",
        verified_at=NOW,
        outcome=G64VerificationOutcome.PASS,
        findings=tuple(finding(check) for check in G64VerificationCheck),
    )


def test_pass_requires_all_checks_and_never_grants_access():
    result = passing_verification().to_document()
    assert result["outcome"] == "PASS"
    assert result["permits_operational_access"] is False
    assert result["constitutes_ratification"] is False
    assert len(result["findings"]) == len(G64VerificationCheck)


def test_verifier_must_be_distinct_from_ratifier():
    with pytest.raises(
        G64WorkspaceEvidenceError,
        match="INDEPENDENT_VERIFIER_MUST_DIFFER_FROM_RATIFIER",
    ):
        G64IndependentVerification(
            verification_id="verification-001",
            tenant_id="tenant-001",
            institution_id="institution-001",
            record_id="record-001",
            record_sha3_512_fingerprint=RECORD_FINGERPRINT,
            ratifier_principal_id="same-principal",
            verifier_principal_id="same-principal",
            verified_at=NOW,
            outcome=G64VerificationOutcome.FAIL,
            findings=(finding(G64VerificationCheck.RATIFIER_AUTHORITY, False),),
        )


def test_pass_cannot_omit_required_verification_checks():
    with pytest.raises(
        G64WorkspaceEvidenceError,
        match="PASS_REQUIRES_COMPLETE_VERIFICATION_CHECKLIST",
    ):
        G64IndependentVerification(
            verification_id="verification-001",
            tenant_id="tenant-001",
            institution_id="institution-001",
            record_id="record-001",
            record_sha3_512_fingerprint=RECORD_FINGERPRINT,
            ratifier_principal_id="principal-ratifier",
            verifier_principal_id="principal-independent-verifier",
            verified_at=NOW,
            outcome=G64VerificationOutcome.PASS,
            findings=(finding(G64VerificationCheck.RATIFIER_AUTHORITY),),
        )


def test_failed_verification_must_record_at_least_one_failed_check():
    with pytest.raises(
        G64WorkspaceEvidenceError,
        match="FAIL_REQUIRES_A_FAILED_CHECK",
    ):
        G64IndependentVerification(
            verification_id="verification-001",
            tenant_id="tenant-001",
            institution_id="institution-001",
            record_id="record-001",
            record_sha3_512_fingerprint=RECORD_FINGERPRINT,
            ratifier_principal_id="principal-ratifier",
            verifier_principal_id="principal-independent-verifier",
            verified_at=NOW,
            outcome=G64VerificationOutcome.FAIL,
            findings=(finding(G64VerificationCheck.RATIFIER_AUTHORITY),),
        )


def test_second_approval_requires_explicit_evidenced_policy_requirement():
    with pytest.raises(
        G64WorkspaceEvidenceError,
        match="SECOND_APPROVAL_NOT_REQUIRED_BY_EVIDENCED_POLICY",
    ):
        G64SecondApproval(
            approval_id="approval-001",
            policy_decision_id="policy-decision-001",
            tenant_id="tenant-001",
            institution_id="institution-001",
            record_id="record-001",
            record_sha3_512_fingerprint=RECORD_FINGERPRINT,
            ratifier_principal_id="principal-ratifier",
            verifier_principal_id="principal-verifier",
            approver_principal_id="principal-approver",
            approved_at=NOW,
            approved=True,
            policy_source=EVIDENCE,
            policy_requires_second_approval=False,
        )


def test_second_approval_requires_three_distinct_principals():
    with pytest.raises(
        G64WorkspaceEvidenceError,
        match="SECOND_APPROVER_MUST_BE_INDEPENDENT",
    ):
        G64SecondApproval(
            approval_id="approval-001",
            tenant_id="tenant-001",
            institution_id="institution-001",
            record_id="record-001",
            record_sha3_512_fingerprint=RECORD_FINGERPRINT,
            ratifier_principal_id="principal-ratifier",
            verifier_principal_id="principal-verifier",
            approver_principal_id="principal-verifier",
            approved_at=NOW,
            approved=True,
            policy_source=EVIDENCE,
            policy_requires_second_approval=True,
        )


def test_second_approval_evidence_is_non_authorizing():
    approval = G64SecondApproval(
        approval_id="approval-001",
        tenant_id="tenant-001",
        institution_id="institution-001",
        record_id="record-001",
        record_sha3_512_fingerprint=RECORD_FINGERPRINT,
        ratifier_principal_id="principal-ratifier",
        verifier_principal_id="principal-verifier",
        approver_principal_id="principal-approver",
        approved_at=NOW,
        approved=True,
        policy_source=EVIDENCE,
        policy_requires_second_approval=True,
    ).to_document()
    assert approval["permits_operational_access"] is False
    assert approval["constitutes_ratification"] is False


def test_second_approval_policy_requires_independent_source_verification():
    policy = G64SecondApprovalPolicyDecision(
        policy_decision_id="policy-decision-001",
        tenant_id="tenant-001",
        institution_id="institution-001",
        record_id="record-001",
        record_sha3_512_fingerprint=RECORD_FINGERPRINT,
        determined_by_principal_id="principal-policy-owner",
        independently_verified_by_principal_id="principal-policy-verifier",
        determined_at=NOW,
        second_approval_required=False,
        policy_source=EVIDENCE,
        independent_verification_evidence=EVIDENCE,
    ).to_document()
    assert policy["second_approval_required"] is False
    assert policy["permits_operational_access"] is False
    assert policy["constitutes_ratification"] is False


def test_second_approval_policy_cannot_be_self_verified():
    with pytest.raises(
        G64WorkspaceEvidenceError,
        match="SECOND_APPROVAL_POLICY_VERIFIER_MUST_BE_INDEPENDENT",
    ):
        G64SecondApprovalPolicyDecision(
            policy_decision_id="policy-decision-001",
            tenant_id="tenant-001",
            institution_id="institution-001",
            record_id="record-001",
            record_sha3_512_fingerprint=RECORD_FINGERPRINT,
            determined_by_principal_id="same-principal",
            independently_verified_by_principal_id="same-principal",
            determined_at=NOW,
            second_approval_required=True,
            policy_source=EVIDENCE,
            independent_verification_evidence=EVIDENCE,
        )
