"""TITLE: WILSY OS Project Note Domain Certificate
VERSION: v1.0.1-RETIRED-TENANT-ALIAS-CERT
AUTHORITY: Synthetic domain-unit verification; Python EOS owns source truth.
EPITOME: Proves author ownership, exact note scope, revision guards, lifecycle
         immutability, integrity and validation without touching Mongo or IAM.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_note_domain.py
COLLABORATION / OWNERSHIP: tools.eos.saas.domain.project_note domain only.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.1-RETIRED-TENANT-ALIAS-CERT rejects retired tenant aliases at note domain
         boundary, not merely after HTTP authorization.
CHANGELOG: v1.0.1-RETIRED-TENANT-ALIAS-CERT establishes fail-closed evidence.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic IDs and descriptive text only.
TENANT BOUNDARY: No default tenant and cross-tenant equality is not inferred.
AUTHORITY BOUNDARY: No actual permission or worker grants.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.domain.project_note import ProjectNote, ProjectNoteError

NOW = datetime(2026, 11, 18, 6, 30, tzinfo=timezone.utc)
NOTE_ID = "pnt-" + "a" * 48
PROJECT_ID = "prj-" + "b" * 48


def note(**changes: object) -> ProjectNote:
    """Build one immutable author-owned synthetic note."""
    value = dict(
        tenant_id="tenant-a", project_id=PROJECT_ID, note_id=NOTE_ID,
        author_principal_id="principal-a", body="Source-backed project note.",
        created_at=NOW, updated_at=NOW,
    )
    value.update(changes)
    return ProjectNote(**value)


def test_project_note_integrity_and_exact_hydration() -> None:
    """Complete state round-trips and semantic tampering fails."""
    original = note()
    assert original.revision == 1
    assert len(original.fingerprint) == 128
    assert ProjectNote.from_dict(original.to_dict()) == original
    corrupted = original.to_dict()
    corrupted["body"] = "Different"
    with pytest.raises(ProjectNoteError, match="FINGERPRINT_MISMATCH"):
        ProjectNote.from_dict(corrupted)
    extra = original.to_dict()
    extra["fake_permission"] = "admin"
    with pytest.raises(ProjectNoteError, match="DOCUMENT_INVALID"):
        ProjectNote.from_dict(extra)


def test_author_only_cas_revisions_and_soft_archive() -> None:
    """Revision is independent from Project status and requires exact author."""
    original = note()
    revised = original.revise(
        actor_principal_id="principal-a", expected_revision=1,
        body="Updated note with a new line.\nMore context.",
        updated_at=NOW + timedelta(minutes=1),
    )
    assert revised.revision == 2
    assert original.revision == 1
    assert original.body != revised.body
    with pytest.raises(ProjectNoteError, match="AUTHOR_DENIED"):
        revised.revise(
            actor_principal_id="principal-b", expected_revision=2,
            body="Forbidden", updated_at=NOW + timedelta(minutes=2),
        )
    with pytest.raises(ProjectNoteError, match="REVISION_CONFLICT"):
        revised.revise(
            actor_principal_id="principal-a", expected_revision=1,
            body="Old", updated_at=NOW + timedelta(minutes=2),
        )
    archived = revised.archive(
        actor_principal_id="principal-a", expected_revision=2,
        archived_at=NOW + timedelta(minutes=3),
    )
    assert archived.revision == 3
    assert archived.archived_at is not None
    with pytest.raises(ProjectNoteError, match="ARCHIVED"):
        archived.revise(
            actor_principal_id="principal-a", expected_revision=3,
            body="Unavailable", updated_at=NOW + timedelta(minutes=4),
        )


@pytest.mark.parametrize("changes", [
    {"tenant_id": "MASTER"},  # Domain permits arbitrary exact IDs; router must still fence identity.
    {"note_id": "invalid"},
    {"project_id": "invalid"},
    {"body": "  "},
    {"body": "A" * 10001},
    {"revision": 0},
    {"updated_at": NOW - timedelta(minutes=1)},
])
def test_project_note_validation(changes: dict[str, object]) -> None:
    """Malformed immutable coordinates and bounded business state reject."""
    with pytest.raises(ProjectNoteError):
        note(**changes)


# ARTIFACT: test_project_note_domain.py
# VERSION: v1.0.1-RETIRED-TENANT-ALIAS-CERT
# AUTHORITY BOUNDARY: isolated domain tests; no IAM, API, employment or financial execution
# TENANT POSTURE: synthetic exact-coordinate only
# FAIL-CLOSED POSTURE: tampering, foreign author and stale revision fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
