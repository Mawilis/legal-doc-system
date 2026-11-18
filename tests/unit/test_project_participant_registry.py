"""TITLE: WILSY OS Project Participant Authority Domain Certificate
VERSION: v1.0.0-PROJECT-PARTICIPATION-FAIL-CLOSED-CERT
AUTHORITY: Synthetic domain and authorization-registry verification only.
EPITOME: Verify exact tenant identity, immutable participant revisions, active
         and revoked state, deterministic fingerprints and no implicit revival.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_participant_registry.py
COLLABORATION / OWNERSHIP: ProjectParticipantRegistry and Projects policy;
         real Mongo persistence receives a separate disposable certificate.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-PROJECT-PARTICIPATION-FAIL-CLOSED-CERT proves immutable
         exact-tenant role state and revision/authorizer rejection.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque principal/tenant records only.
TENANT BOUNDARY: No implicit company root or founder project assignment.
AUTHORITY BOUNDARY: Domain participation never establishes IAM permission.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.projects.project_participant_registry import (
    ProjectParticipant, ProjectParticipantConflict, ProjectParticipantError,
)

NOW = datetime(2026, 11, 18, 8, 0, tzinfo=timezone.utc)
PROJECT = "prj-" + "b" * 48


def participant(**changes: object) -> ProjectParticipant:
    """Build synthetic role state without assigning any real principal."""
    value = dict(
        tenant_id="tenant-a", project_id=PROJECT,
        principal_id="principal-a", role="CONTRIBUTOR", state="ACTIVE",
        revision=1, granted_by_principal_id="owner-a",
        updated_by_principal_id="owner-a", created_at=NOW, updated_at=NOW,
    )
    value.update(changes)
    return ProjectParticipant(**value)


def test_participation_integrity_and_forged_state_denial() -> None:
    """The fingerprint covers every source-owned role and revision coordinate."""
    record = participant()
    assert len(record.fingerprint) == 128
    assert ProjectParticipant.hydrate(record.to_dict()) == record
    changed = record.to_dict()
    changed["role"] = "VIEWER"
    with pytest.raises(ProjectParticipantError, match="FINGERPRINT_INVALID"):
        ProjectParticipant.hydrate(changed)
    with pytest.raises(ProjectParticipantError, match="RECORD_INVALID"):
        ProjectParticipant.hydrate({**record.to_dict(), "forged_admin": True})


@pytest.mark.parametrize("changes", [
    {"tenant_id": "WILSY_ROOT"},
    {"tenant_id": "MASTER"},
    {"tenant_id": "WILSY_GLOBAL_ROOT"},
    {"project_id": "project-without-tenant"},
    {"principal_id": "  principal"},
    {"role": "OWNER"},
    {"state": "INVITED"},
    {"revision": 0},
    {"revision": True},
    {"created_at": NOW.replace(tzinfo=None)},
    {"updated_at": NOW - timedelta(seconds=1)},
])
def test_invalid_participant_identity_and_role_reject(changes: dict[str, object]) -> None:
    """Root aliases, fake roles, naive times and unbounded states deny."""
    with pytest.raises(ProjectParticipantError):
        participant(**changes)


def test_participation_revokes_once_under_strict_revision() -> None:
    """No implicit revival, role elevation or stale update is allowed."""
    source = participant()
    revoked = source.change(
        role="CONTRIBUTOR", state="REVOKED", actor_principal_id="owner-a",
        expected_revision=1, occurred_at=NOW + timedelta(seconds=1),
    )
    assert revoked.state == "REVOKED" and revoked.revision == 2
    assert source.state == "ACTIVE" and source.revision == 1
    assert revoked.fingerprint != source.fingerprint
    with pytest.raises(ProjectParticipantConflict, match="REVISION_CONFLICT"):
        source.change(
            role="CONTRIBUTOR", state="REVOKED", actor_principal_id="owner-a",
            expected_revision=2, occurred_at=NOW + timedelta(seconds=2),
        )
    with pytest.raises(ProjectParticipantConflict, match="ROLE_CHANGE_DENIED"):
        source.change(
            role="VIEWER", state="REVOKED", actor_principal_id="owner-a",
            expected_revision=1, occurred_at=NOW + timedelta(seconds=2),
        )
    with pytest.raises(ProjectParticipantConflict, match="TRANSITION_DENIED"):
        revoked.change(
            role="CONTRIBUTOR", state="REVOKED", actor_principal_id="owner-a",
            expected_revision=2, occurred_at=NOW + timedelta(seconds=2),
        )


# ARTIFACT: test_project_participant_registry.py
# VERSION: v1.0.0-PROJECT-PARTICIPATION-FAIL-CLOSED-CERT
# AUTHORITY BOUNDARY: unit evidence only; no role admission or grants
# TENANT POSTURE: synthetic exact tenant and principal
# FAIL-CLOSED POSTURE: invalid role/alias/revision/fingerprint deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
