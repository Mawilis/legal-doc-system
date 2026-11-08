"""Independent institutional source-key governance evidence boundary.

No implementation is configured by default. A provider-specific adapter must
verify source authority and independent approval; references alone are never
accepted as proof. This contract is intentionally separate from human signer
certificate enrollment evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class VerifiedSourceKeyProposalAuthority:
    """Provider-verified identity and source authority for one exact proposal."""

    tenant_id: str
    source_system_id: str
    public_key_fingerprint_sha256: str
    proposer_principal_id: str
    identity_proofing_evidence_reference: str
    source_authority_evidence_reference: str
    evidence_fingerprint_sha256: str


@dataclass(frozen=True)
class VerifiedSourceKeyApproval:
    """Provider-verified independent approval of one exact immutable proposal."""

    tenant_id: str
    source_system_id: str
    key_id: str
    public_key_fingerprint_sha256: str
    proposer_principal_id: str
    approver_principal_id: str
    proposal_reference: str
    governance_decision_reference: str
    approval_evidence_reference: str
    evidence_fingerprint_sha256: str


@dataclass(frozen=True)
class VerifiedSourceKeyRevocationApproval:
    """Provider-verified approval of one exact key revocation command."""

    tenant_id: str
    source_system_id: str
    key_id: str
    public_key_fingerprint_sha256: str
    proposer_principal_id: str
    revoker_principal_id: str
    reason_reference: str
    governance_decision_reference: str
    approval_evidence_reference: str
    approver_principal_id: str
    evidence_fingerprint_sha256: str


class InstitutionalSourceKeyGovernanceEvidenceError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@runtime_checkable
class InstitutionalSourceKeyGovernanceEvidenceVerifier(Protocol):
    def verify_proposal(
        self, *, tenant_id: str, source_system_id: str,
        public_key_fingerprint_sha256: str, proposer_principal_id: str,
        identity_proofing_evidence_reference: str,
        source_authority_evidence_reference: str,
        evaluated_at: datetime, session: object,
    ) -> VerifiedSourceKeyProposalAuthority:
        """Verify proposal authority.

        Implementations may be invoked more than once because MongoDB may retry
        the enclosing transaction callback. Verification MUST be read-only,
        retry-safe, and idempotent for identical arguments; it MUST NOT perform
        non-transactional lifecycle writes or consume one-time evidence.
        The returned evidence fingerprint must identify the exact canonical
        evidence used for this decision.
        """
        ...

    def verify_approval(
        self, *, tenant_id: str, source_system_id: str, key_id: str,
        public_key_fingerprint_sha256: str, proposer_principal_id: str,
        approver_principal_id: str, proposal_reference: str,
        governance_decision_reference: str, approval_evidence_reference: str,
        evaluated_at: datetime, session: object,
    ) -> VerifiedSourceKeyApproval:
        """Verify approval of this exact immutable proposal.

        MongoDB may retry the enclosing transaction callback. Implementations
        MUST be read-only, retry-safe and idempotent for identical arguments,
        and MUST NOT consume one-time evidence or create external side effects.
        """
        ...

    def verify_revocation(
        self, *, tenant_id: str, source_system_id: str, key_id: str,
        public_key_fingerprint_sha256: str, proposer_principal_id: str,
        revoker_principal_id: str, reason_reference: str,
        governance_decision_reference: str, approval_evidence_reference: str,
        evaluated_at: datetime, session: object,
    ) -> VerifiedSourceKeyRevocationApproval:
        """Verify exact revocation approval and bind every actor and decision.

        MongoDB may retry the enclosing transaction callback. Implementations
        MUST be read-only, retry-safe and idempotent for identical arguments,
        and MUST NOT consume one-time evidence or create external side effects.
        The returned result must bind tenant, source, key fingerprint, proposer,
        revoker, reason, decision, evidence reference and approver.
        """
        ...


class UnavailableInstitutionalSourceKeyGovernanceEvidenceVerifier:
    """Default-deny verifier until an institutional source contract is onboarded."""

    def _unavailable(self) -> None:
        raise InstitutionalSourceKeyGovernanceEvidenceError(
            "INSTITUTIONAL_SOURCE_KEY_GOVERNANCE_EVIDENCE_AUTHORITY_UNAVAILABLE"
        )

    def verify_proposal(self, **_kwargs: object) -> VerifiedSourceKeyProposalAuthority:
        self._unavailable()

    def verify_approval(self, **_kwargs: object) -> VerifiedSourceKeyApproval:
        self._unavailable()

    def verify_revocation(self, **_kwargs: object) -> VerifiedSourceKeyRevocationApproval:
        self._unavailable()


__all__ = [
    "InstitutionalSourceKeyGovernanceEvidenceError",
    "InstitutionalSourceKeyGovernanceEvidenceVerifier",
    "VerifiedSourceKeyProposalAuthority", "VerifiedSourceKeyApproval",
    "VerifiedSourceKeyRevocationApproval",
    "UnavailableInstitutionalSourceKeyGovernanceEvidenceVerifier",
]
