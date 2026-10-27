"""Deterministic repository export of G64 evidence without ratification claims.

TITLE: G64 Ratification Workspace Repository Export
VERSION: v1.0.0-G64-EVIDENCE-ONLY-REPOSITORY-EXPORT
AUTHORITY: Canonical evidence serialization only; no repository credential or authority.
EPITOME: Produce a stable, secret-free evidence manifest while never declaring ratification.
"""
from __future__ import annotations

import hashlib
import json
from typing import Final

from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64RatificationWorkspaceRecord,
    G64RecordState,
    G64WorkspaceEvidenceError,
    _token,
)
from tools.eos.legal_operations.domain.g64_ratification_workspace_verification import (
    G64IndependentVerification,
    G64SecondApproval,
    G64SecondApprovalPolicyDecision,
    G64VerificationOutcome,
)

VERSION: Final[str] = "v1.0.0-G64-EVIDENCE-ONLY-REPOSITORY-EXPORT"


def build_repository_export_bytes(
    *,
    tenant_id: str,
    record: G64RatificationWorkspaceRecord,
    verification: G64IndependentVerification | None = None,
    second_approval_policy: G64SecondApprovalPolicyDecision | None = None,
    second_approval: G64SecondApproval | None = None,
) -> bytes:
    """Build deterministic evidence-only JSON; never commits or grants authority."""
    _token("tenant_id", tenant_id)
    if type(record) is not G64RatificationWorkspaceRecord:
        raise G64WorkspaceEvidenceError("EXPORT_RECORD_INVALID")
    record_fingerprint = record.evidence_fingerprint()
    unresolved = list(record.unresolved_decision_ids)
    status = "DRAFT_NOT_ATTESTED"
    if record.attestation is not None and record.state is G64RecordState.ATTESTED_PENDING_VERIFICATION:
        status = "INDEPENDENT_VERIFICATION_PENDING"
    if unresolved:
        status = "DECISIONS_UNRESOLVED"

    verification_document = None
    if verification is not None:
        if type(verification) is not G64IndependentVerification:
            raise G64WorkspaceEvidenceError("EXPORT_VERIFICATION_INVALID")
        if (
            verification.tenant_id != tenant_id
            or verification.institution_id != record.institution_id
            or verification.record_id != record.record_id
            or verification.record_sha3_512_fingerprint != record_fingerprint
            or verification.ratifier_principal_id != record.ratifier_principal_id
        ):
            raise G64WorkspaceEvidenceError("EXPORT_VERIFICATION_SCOPE_MISMATCH")
        verification_document = verification.to_document()
        status = (
            "INDEPENDENT_VERIFICATION_FAILED"
            if verification.outcome is G64VerificationOutcome.FAIL
            else "SECOND_APPROVAL_POLICY_UNVERIFIED"
        )

    policy_document = None
    if second_approval_policy is not None:
        if type(second_approval_policy) is not G64SecondApprovalPolicyDecision:
            raise G64WorkspaceEvidenceError("EXPORT_SECOND_APPROVAL_POLICY_INVALID")
        if (
            second_approval_policy.tenant_id != tenant_id
            or second_approval_policy.institution_id != record.institution_id
            or second_approval_policy.record_id != record.record_id
            or second_approval_policy.record_sha3_512_fingerprint != record_fingerprint
        ):
            raise G64WorkspaceEvidenceError("EXPORT_SECOND_APPROVAL_POLICY_SCOPE_MISMATCH")
        policy_document = second_approval_policy.to_document()
        if verification is None or verification.outcome is not G64VerificationOutcome.PASS:
            status = "INDEPENDENT_VERIFICATION_REQUIRED"
        elif second_approval_policy.second_approval_required:
            status = "SECOND_APPROVAL_PENDING"
        else:
            status = "EVIDENCE_READY_FOR_INSTITUTIONAL_REVIEW"

    approval_document = None
    if second_approval is not None:
        if type(second_approval) is not G64SecondApproval:
            raise G64WorkspaceEvidenceError("EXPORT_SECOND_APPROVAL_INVALID")
        if (
            second_approval.tenant_id != tenant_id
            or second_approval.institution_id != record.institution_id
            or second_approval.record_id != record.record_id
            or second_approval.record_sha3_512_fingerprint != record_fingerprint
            or second_approval_policy is None
            or not second_approval_policy.second_approval_required
            or second_approval.policy_decision_id != second_approval_policy.policy_decision_id
            or second_approval.policy_source != second_approval_policy.policy_source
        ):
            raise G64WorkspaceEvidenceError("EXPORT_SECOND_APPROVAL_SCOPE_MISMATCH")
        approval_document = second_approval.to_document()
        if verification is None or verification.outcome is not G64VerificationOutcome.PASS:
            status = "INDEPENDENT_VERIFICATION_REQUIRED"
        elif not second_approval.approved:
            status = "SECOND_APPROVAL_REJECTED"
        else:
            status = "EVIDENCE_READY_FOR_INSTITUTIONAL_REVIEW"

    if unresolved:
        status = "DECISIONS_UNRESOLVED"
    body = {
        "schema": "WILSY-G64-REPOSITORY-EVIDENCE-EXPORT/V1",
        "version": VERSION,
        "tenant_id": tenant_id,
        "institution_id": record.institution_id,
        "record_id": record.record_id,
        "record_sha3_512_fingerprint": record_fingerprint,
        "export_status": status,
        "record": record.to_document(),
        "independent_verification": verification_document,
        "second_approval_policy": policy_document,
        "second_approval": approval_document,
        "ratification_complete": False,
        "permits_operational_access": False,
        "constitutes_ratification": False,
        "repository_commit_is_signature": False,
        "authority_effect": "NONE",
    }
    encoded = json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False,
    ).encode("ascii")
    manifest = {**body, "manifest_sha3_512": hashlib.sha3_512(encoded).hexdigest()}
    return json.dumps(
        manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False,
    ).encode("ascii")
