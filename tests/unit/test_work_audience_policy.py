"""TITLE: WILSY OS Source-Owned Work Audience Taxonomy Certificate.
VERSION: v1.0.0-EXACT-WORK-AUDIENCE-TAXONOMY-CERT
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Synthetic source evidence certificate for Operating, Platform Build,
Unclassified and independently proven critical release gates.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_work_audience_policy.py
COLLABORATION / OWNERSHIP: WorkAudiencePolicy; current My Work adapters remain
separately authorized and are not replaced by this pure certificate.
CERTIFICATION / UPDATE DATE: 2026-11-23
CHANGELOG: v1.0.0-EXACT-WORK-AUDIENCE-TAXONOMY-CERT covers
unclassified, exact current evidence, foreign source, stale source,
invalid gates and unverified provenance without inferred permissions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and no network.
TENANT BOUNDARY: Exact tenant/source/record/revision assertions.
AUTHORITY BOUNDARY: Never creates a classification or source permission.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import pytest

from tools.eos.workspaces.service.work_audience_policy import (
    WorkAudience,
    WorkAudiencePolicyError,
    evaluate_work_audience,
)

SCOPE = dict(tenant_id="WILSYTENANT-4CD2FZ4O", source="PROJECTS",
             record_id="ptk-synthetic", source_revision=6)


def evidence(**changes):
    """Build explicitly claimed, source-owned synthetic current evidence."""
    return {
        "tenant_id": SCOPE["tenant_id"],
        "source": SCOPE["source"],
        "record_id": SCOPE["record_id"],
        "source_revision": SCOPE["source_revision"],
        "audience": "PLATFORM_BUILD",
        "evidence_ref": "source-command-1",
        "source_verified": True,
        "critical_gate": False,
        "critical_gate_evidence_ref": None,
        **changes,
    }


def test_absent_source_classification_remains_unclassified():
    """Missing source evidence does not secretly map by module or task title."""
    result = evaluate_work_audience(**SCOPE, evidence=None)
    assert result.audience is WorkAudience.UNCLASSIFIED
    assert result.source_evidence_ref is None
    assert result.critical_gate is False


def test_exact_source_classification_and_separate_critical_gate():
    """Proven source purpose does not automatically imply a release gate."""
    standard = evaluate_work_audience(**SCOPE, evidence=evidence())
    assert standard.audience is WorkAudience.PLATFORM_BUILD
    assert standard.source_revision == 6
    assert standard.critical_gate is False
    operating = evaluate_work_audience(**SCOPE, evidence=evidence(audience="OPERATING"))
    assert operating.audience is WorkAudience.OPERATING
    assert operating.critical_gate is False
    gated = evaluate_work_audience(**SCOPE, evidence=evidence(
        critical_gate=True, critical_gate_evidence_ref="release-impact-evidence-1",
    ))
    assert gated.audience is WorkAudience.PLATFORM_BUILD
    assert gated.critical_gate is True


@pytest.mark.parametrize("changes,code", [
    ({"tenant_id": "OTHER-TENANT"}, "WORK_AUDIENCE_SCOPE_MISMATCH"),
    ({"source": "CRM"}, "WORK_AUDIENCE_SCOPE_MISMATCH"),
    ({"record_id": "another-item"}, "WORK_AUDIENCE_SCOPE_MISMATCH"),
    ({"source_revision": 5}, "WORK_AUDIENCE_REVISION_MISMATCH"),
    ({"source_verified": False}, "WORK_AUDIENCE_SOURCE_UNVERIFIED"),
    ({"evidence_ref": ""}, "WORK_AUDIENCE_SOURCE_UNVERIFIED"),
    ({"audience": "UNCLASSIFIED"}, "WORK_AUDIENCE_CLASSIFICATION_INVALID"),
    ({"audience": "UNKNOWN"}, "WORK_AUDIENCE_CLASSIFICATION_INVALID"),
    ({"critical_gate": "true"}, "WORK_AUDIENCE_CRITICAL_GATE_INVALID"),
    ({"critical_gate": True}, "WORK_AUDIENCE_CRITICAL_GATE_UNVERIFIED"),
    ({"critical_gate_evidence_ref": "unsupported"}, "WORK_AUDIENCE_CRITICAL_GATE_UNVERIFIED"),
    ({"audience": "OPERATING", "critical_gate": True,
      "critical_gate_evidence_ref": "unsupported"}, "WORK_AUDIENCE_CRITICAL_GATE_UNVERIFIED"),
])
def test_unverified_or_foreign_evidence_fails_closed(changes, code):
    """Malicious or stale classification cannot authorize, filter or rank."""
    with pytest.raises(WorkAudiencePolicyError, match=code):
        evaluate_work_audience(**SCOPE, evidence=evidence(**changes))


def test_source_revision_and_proof_shape_must_be_exact():
    """Evidence cannot be detached from its persisted source revision."""
    with pytest.raises(WorkAudiencePolicyError, match="WORK_AUDIENCE_SOURCE_REVISION_INVALID"):
        evaluate_work_audience(**{**SCOPE, "source_revision": 0}, evidence=None)
    with pytest.raises(WorkAudiencePolicyError, match="WORK_AUDIENCE_REVISION_MISMATCH"):
        evaluate_work_audience(**{**SCOPE, "source_revision": None}, evidence=evidence())
    with pytest.raises(WorkAudiencePolicyError, match="WORK_AUDIENCE_EVIDENCE_INVALID"):
        evaluate_work_audience(**SCOPE, evidence={**evidence(), "extra": "unsupported"})


# ARTIFACT: test_work_audience_policy.py
# VERSION: v1.0.0-EXACT-WORK-AUDIENCE-TAXONOMY-CERT
# AUTHORITY BOUNDARY: Synthetic pure taxonomy assertions; no IAM command.
# TENANT POSTURE: Foreign/stale coordinate denial, no source disclosure.
# FAIL-CLOSED POSTURE: Missing and invalid evidence never becomes authority.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
