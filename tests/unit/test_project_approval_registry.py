"""TITLE: WILSY OS Project Task Decision Domain Certificate
VERSION: v1.0.0-EXACT-REVIEWER-APPROVAL-CERT
AUTHORITY: Synthetic independently reviewed task business decision invariants.
EPITOME: Prove immutable review request, source checksum, self-review denial,
         designated reviewer, one terminal decision and revision conflict.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_approval_registry.py
COLLABORATION / OWNERSHIP: project_approval_registry; Projects route IAM separate.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-EXACT-REVIEWER-APPROVAL-CERT certifies independent business
         review and absence of financial execution, IAM or task status side effect.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers, no real user data.
TENANT BOUNDARY: Every approval identity binds exact tenant/project/task.
AUTHORITY BOUNDARY: No evidence of institutional signatures or financial grant.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS executes finances exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.projects.project_approval_registry import (
    ProjectApproval, ProjectApprovalConflict, ProjectApprovalError,
    ProjectApprovalNotFound, approval_id_for_request,
)

NOW = datetime(2026, 11, 18, 8, 0, tzinfo=timezone.utc)
TENANT = "tenant-a"
PROJECT = "prj-" + "a" * 48
TASK = "ptk-" + "b" * 48
AUTHOR = "owner-a"
REVIEWER = "contributor-b"


def request(**changes: object) -> ProjectApproval:
    """Construct a synthetic valid task business decision request."""
    values = dict(
        tenant_id=TENANT, project_id=PROJECT, task_id=TASK,
        approval_id=approval_id_for_request(TENANT, PROJECT, TASK, AUTHOR, "request-1"),
        requester_principal_id=AUTHOR, reviewer_principal_id=REVIEWER,
        rationale="Verify delivery acceptance evidence.", status="PENDING",
        requested_at=NOW,
    )
    values.update(changes)
    return ProjectApproval(**values)


def test_approval_roundtrip_checksum_and_terminal_decisions() -> None:
    """A source revision owns the decision; an approval does not mutate work."""
    original = request()
    assert ProjectApproval.hydrate(original.to_dict()) == original
    assert original.status == "PENDING" and original.revision == 1
    accepted = original.decide(
        reviewer_principal_id=REVIEWER, decision="APPROVED",
        rationale="Delivery verified.", expected_revision=1,
        occurred_at=NOW + timedelta(minutes=1),
    )
    assert accepted.status == "APPROVED"
    assert accepted.revision == 2
    assert original.status == "PENDING"
    assert accepted.fingerprint != original.fingerprint
    assert ProjectApproval.hydrate(accepted.to_dict()) == accepted
    with pytest.raises(ProjectApprovalConflict, match="TERMINAL"):
        accepted.decide(
            reviewer_principal_id=REVIEWER, decision="REJECTED",
            rationale="No.", expected_revision=2,
            occurred_at=NOW + timedelta(minutes=2),
        )


def test_only_designated_reviewer_may_decide() -> None:
    """Another participant or the requester cannot approve by possessing ID."""
    original = request()
    with pytest.raises(ProjectApprovalNotFound):
        original.decide(
            reviewer_principal_id=AUTHOR, decision="APPROVED",
            rationale="Self-approved.", expected_revision=1,
            occurred_at=NOW,
        )
    with pytest.raises(ProjectApprovalConflict, match="REVISION_CONFLICT"):
        original.decide(
            reviewer_principal_id=REVIEWER, decision="APPROVED",
            rationale="Evidence checked.", expected_revision=3,
            occurred_at=NOW,
        )


@pytest.mark.parametrize("changes", [
    {"tenant_id": "MASTER"}, {"tenant_id": "WILSY_ROOT"},
    {"project_id": "other"}, {"task_id": "other"},
    {"approval_id": "other"}, {"rationale": ""},
    {"reviewer_principal_id": AUTHOR},
    {"status": "APPROVED"}, {"status": "REJECTED"},
    {"revision": 2}, {"decided_at": NOW},
    {"requested_at": NOW.replace(tzinfo=None)},
])
def test_invalid_project_approval_state_denied(changes: dict[str, object]) -> None:
    """No malformed, foreign or forged approvals become persisted evidence."""
    with pytest.raises(ProjectApprovalError):
        request(**changes)


def test_tamper_unknown_fields_and_identity_scope_rejected() -> None:
    """Unknown decision claim or checksum change cannot hydrate."""
    original = request()
    forged = original.to_dict()
    forged["reviewer_principal_id"] = "another"
    with pytest.raises(ProjectApprovalError, match="FINGERPRINT_INVALID"):
        ProjectApproval.hydrate(forged)
    with pytest.raises(ProjectApprovalError, match="RECORD_INVALID"):
        ProjectApproval.hydrate({**original.to_dict(), "released_funds": True})
    first = original.approval_id
    assert first != approval_id_for_request("tenant-b", PROJECT, TASK, AUTHOR, "request-1")
    assert first != approval_id_for_request(TENANT, PROJECT, TASK, "other", "request-1")
    assert first != approval_id_for_request(
        TENANT, PROJECT, "ptk-" + "c" * 48, AUTHOR, "request-1",
    )


# ARTIFACT: test_project_approval_registry.py
# VERSION: v1.0.0-EXACT-REVIEWER-APPROVAL-CERT
# AUTHORITY BOUNDARY: source domain tests, not live IAM or financial approval
# TENANT POSTURE: exact task and explicit requester/reviewer
# FAIL-CLOSED POSTURE: checksum, stale CAS, self-review and foreign denial
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
