from datetime import datetime, timezone

import pytest

from tools.eos.security.institutional_source_key_governance_evidence import (
    InstitutionalSourceKeyGovernanceEvidenceError,
    UnavailableInstitutionalSourceKeyGovernanceEvidenceVerifier,
)


@pytest.mark.parametrize(
    "method",
    ("verify_proposal", "verify_approval", "verify_revocation"),
)
def test_unconfigured_institutional_source_governance_fails_closed(method):
    verifier = UnavailableInstitutionalSourceKeyGovernanceEvidenceVerifier()
    with pytest.raises(InstitutionalSourceKeyGovernanceEvidenceError) as error:
        getattr(verifier, method)(
            tenant_id="WILSYTENANT-4CD2FZ4O",
            source_system_id="synthetic-source",
            public_key_fingerprint_sha256="a" * 64,
            proposer_principal_id="synthetic-maker",
            approver_principal_id="synthetic-checker",
            revoker_principal_id="synthetic-revoker",
            key_id="synthetic-key",
            proposal_reference="synthetic-proposal",
            identity_proofing_evidence_reference="synthetic-identity",
            source_authority_evidence_reference="synthetic-authority",
            governance_decision_reference="synthetic-decision",
            approval_evidence_reference="synthetic-approval",
            reason_reference="synthetic-reason",
            evaluated_at=datetime.now(timezone.utc),
            session=object(),
        )
    assert error.value.code == "INSTITUTIONAL_SOURCE_KEY_GOVERNANCE_EVIDENCE_AUTHORITY_UNAVAILABLE"
