"""Independent verification and second-approval evidence for G64.

TITLE: G64 Independent Verification Evidence
VERSION: v1.0.0-G64-INDEPENDENT-VERIFICATION
AUTHORITY: Verification evidence shape only; no ratification or access authority.
EPITOME: Require an independent verifier and evidence-backed second-approval policy
         without guessing whether the institution mandates a second approval.
TENANT BOUNDARY: Exact tenant and institution scope are carried on every artifact.
AUTHORITY BOUNDARY: A passing verification is non-authorizing evidence only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Final

from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64EvidenceReference,
    G64WorkspaceEvidenceError,
    _fingerprint,
    _moment,
    _required_text,
    _token,
)

VERSION: Final[str] = "v1.0.0-G64-INDEPENDENT-VERIFICATION"


class G64VerificationOutcome(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"


class G64VerificationCheck(StrEnum):
    RATIFIER_AUTHORITY = "RATIFIER_AUTHORITY"
    CONTRACT_VERSION_AND_FINGERPRINT = "CONTRACT_VERSION_AND_FINGERPRINT"
    DECISION_REGISTER_COMPLETENESS = "DECISION_REGISTER_COMPLETENESS"
    DECISION_EVIDENCE_AND_SCOPE = "DECISION_EVIDENCE_AND_SCOPE"
    EFFECTIVE_REVIEW_AND_REVOCATION = "EFFECTIVE_REVIEW_AND_REVOCATION"
    INSTITUTION_BINDING = "INSTITUTION_BINDING"
    TENANT_BINDING = "TENANT_BINDING"
    SECOND_APPROVAL_POLICY = "SECOND_APPROVAL_POLICY"


@dataclass(frozen=True, slots=True)
class G64VerificationFinding:
    check: G64VerificationCheck
    passed: bool
    rationale: str
    evidence: tuple[G64EvidenceReference, ...]

    def __post_init__(self) -> None:
        if type(self.check) is not G64VerificationCheck:
            raise G64WorkspaceEvidenceError("VERIFICATION_CHECK_INVALID")
        if type(self.passed) is not bool:
            raise G64WorkspaceEvidenceError("VERIFICATION_RESULT_INVALID")
        _required_text("verification_rationale", self.rationale, maximum=2000)
        if type(self.evidence) is not tuple or not self.evidence:
            raise G64WorkspaceEvidenceError("VERIFICATION_EVIDENCE_REQUIRED")
        if any(type(item) is not G64EvidenceReference for item in self.evidence):
            raise G64WorkspaceEvidenceError("VERIFICATION_EVIDENCE_INVALID")

    def to_document(self) -> dict[str, object]:
        return {
            "check": self.check.value,
            "passed": self.passed,
            "rationale": self.rationale,
            "evidence": [item.to_document() for item in self.evidence],
        }


@dataclass(frozen=True, slots=True)
class G64IndependentVerification:
    verification_id: str
    tenant_id: str
    institution_id: str
    record_id: str
    record_sha3_512_fingerprint: str
    ratifier_principal_id: str
    verifier_principal_id: str
    verified_at: datetime
    outcome: G64VerificationOutcome
    findings: tuple[G64VerificationFinding, ...]

    def __post_init__(self) -> None:
        for name in ("verification_id", "tenant_id", "institution_id", "record_id",
                     "ratifier_principal_id", "verifier_principal_id"):
            _token(name, getattr(self, name))
        if self.verifier_principal_id == self.ratifier_principal_id:
            raise G64WorkspaceEvidenceError("INDEPENDENT_VERIFIER_MUST_DIFFER_FROM_RATIFIER")
        _fingerprint("record_fingerprint", self.record_sha3_512_fingerprint)
        _moment("verified_at", self.verified_at)
        if type(self.outcome) is not G64VerificationOutcome:
            raise G64WorkspaceEvidenceError("VERIFICATION_OUTCOME_INVALID")
        if type(self.findings) is not tuple or not self.findings:
            raise G64WorkspaceEvidenceError("VERIFICATION_FINDINGS_REQUIRED")
        if any(type(item) is not G64VerificationFinding for item in self.findings):
            raise G64WorkspaceEvidenceError("VERIFICATION_FINDING_INVALID")
        checks = tuple(item.check for item in self.findings)
        if len(set(checks)) != len(checks):
            raise G64WorkspaceEvidenceError("VERIFICATION_CHECK_DUPLICATED")
        passed = all(item.passed for item in self.findings)
        if self.outcome is G64VerificationOutcome.PASS and set(checks) != set(G64VerificationCheck):
            raise G64WorkspaceEvidenceError("PASS_REQUIRES_COMPLETE_VERIFICATION_CHECKLIST")
        if self.outcome is G64VerificationOutcome.PASS and not passed:
            raise G64WorkspaceEvidenceError("PASS_REQUIRES_ALL_RECORDED_CHECKS_TO_PASS")
        if self.outcome is G64VerificationOutcome.FAIL and passed:
            raise G64WorkspaceEvidenceError("FAIL_REQUIRES_A_FAILED_CHECK")

    def to_document(self) -> dict[str, object]:
        return {
            "schema": "WILSY-G64-INDEPENDENT-VERIFICATION/V1",
            "version": VERSION,
            "verification_id": self.verification_id,
            "tenant_id": self.tenant_id,
            "institution_id": self.institution_id,
            "record_id": self.record_id,
            "record_sha3_512_fingerprint": self.record_sha3_512_fingerprint,
            "ratifier_principal_id": self.ratifier_principal_id,
            "verifier_principal_id": self.verifier_principal_id,
            "verified_at": _moment("verified_at", self.verified_at).isoformat().replace("+00:00", "Z"),
            "outcome": self.outcome.value,
            "findings": [item.to_document() for item in self.findings],
            "permits_operational_access": False,
            "constitutes_ratification": False,
        }


@dataclass(frozen=True, slots=True)
class G64SecondApproval:
    approval_id: str
    tenant_id: str
    institution_id: str
    record_id: str
    record_sha3_512_fingerprint: str
    ratifier_principal_id: str
    verifier_principal_id: str
    approver_principal_id: str
    approved_at: datetime
    approved: bool
    policy_source: G64EvidenceReference
    policy_requires_second_approval: bool

    def __post_init__(self) -> None:
        for name in ("approval_id", "tenant_id", "institution_id", "record_id",
                     "ratifier_principal_id", "verifier_principal_id", "approver_principal_id"):
            _token(name, getattr(self, name))
        if type(self.approved) is not bool or type(self.policy_requires_second_approval) is not bool:
            raise G64WorkspaceEvidenceError("SECOND_APPROVAL_BOOLEAN_INVALID")
        if not self.policy_requires_second_approval:
            raise G64WorkspaceEvidenceError("SECOND_APPROVAL_NOT_REQUIRED_BY_EVIDENCED_POLICY")
        if len({self.ratifier_principal_id, self.verifier_principal_id, self.approver_principal_id}) != 3:
            raise G64WorkspaceEvidenceError("SECOND_APPROVER_MUST_BE_INDEPENDENT")
        _fingerprint("record_fingerprint", self.record_sha3_512_fingerprint)
        _moment("approved_at", self.approved_at)
        if type(self.policy_source) is not G64EvidenceReference:
            raise G64WorkspaceEvidenceError("SECOND_APPROVAL_POLICY_EVIDENCE_REQUIRED")

    def to_document(self) -> dict[str, object]:
        return {
            "schema": "WILSY-G64-SECOND-APPROVAL/V1",
            "approval_id": self.approval_id,
            "tenant_id": self.tenant_id,
            "institution_id": self.institution_id,
            "record_id": self.record_id,
            "record_sha3_512_fingerprint": self.record_sha3_512_fingerprint,
            "ratifier_principal_id": self.ratifier_principal_id,
            "verifier_principal_id": self.verifier_principal_id,
            "approver_principal_id": self.approver_principal_id,
            "approved_at": _moment("approved_at", self.approved_at).isoformat().replace("+00:00", "Z"),
            "approved": self.approved,
            "policy_requires_second_approval": self.policy_requires_second_approval,
            "policy_source": self.policy_source.to_document(),
            "permits_operational_access": False,
            "constitutes_ratification": False,
        }
