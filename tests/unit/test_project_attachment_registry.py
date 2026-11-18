"""TITLE: WILSY OS Quarantined Project Attachment Manifest Certificate
VERSION: v1.0.0-ATTACHMENT-EVIDENCE-FAIL-CLOSED-CERT
AUTHORITY: Synthetic task-scoped attachment source state and replay tests.
EPITOME: Prove immutable quarantine-only manifests, digest tamper rejection,
         tenant isolation, media restrictions and deterministic command IDs.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_attachment_registry.py
COLLABORATION / OWNERSHIP: project_attachment_registry, caller IAM separate.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-ATTACHMENT-EVIDENCE-FAIL-CLOSED-CERT certifies unscanned files
         cannot become approved/signed/downloadeable source truth by mutation.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque storage receipts only.
TENANT BOUNDARY: All identifiers and command fingerprints are exact task scope.
AUTHORITY BOUNDARY: Tests verify metadata only, never scan/provider evidence.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tools.eos.saas.projects.project_attachment_registry import (
    MAX_ATTACHMENT_BYTES, ProjectAttachment, ProjectAttachmentError,
    ProjectAttachmentNotFound, attachment_id_for_command,
)

NOW = datetime(2026, 11, 18, 9, 0, tzinfo=timezone.utc)
TENANT = "project-file-tenant"
PROJECT = "prj-" + "a" * 48
TASK = "ptk-" + "b" * 48
UPLOADER = "active-contributor"
KEY = "upload-command"


def manifest(**changes: object) -> ProjectAttachment:
    """Create synthetic provider-verified receipt metadata for one task."""
    fields: dict[str, object] = {
        "tenant_id": TENANT, "project_id": PROJECT, "task_id": TASK,
        "attachment_id": attachment_id_for_command(
            TENANT, PROJECT, TASK, UPLOADER, KEY,
        ),
        "uploader_principal_id": UPLOADER,
        "filename": "evidence.pdf", "media_type": "application/pdf",
        "size_bytes": 8096, "content_sha3_512": "c" * 128,
        "storage_receipt": "opaque-s3-version-verified",
        "created_at": NOW,
    }
    fields.update(changes)
    return ProjectAttachment(**fields)


def test_quarantine_source_hydrates_and_replay_identity_bound() -> None:
    """Source digest authenticates internal record shape, not malware verdict."""
    source = manifest()
    assert source.state == "QUARANTINED"
    assert source.revision == 1
    assert ProjectAttachment.hydrate(source.to_dict()) == source
    assert len(source.fingerprint) == 128
    assert source.attachment_id != attachment_id_for_command(
        "another-tenant", PROJECT, TASK, UPLOADER, KEY,
    )
    assert source.attachment_id != attachment_id_for_command(
        TENANT, PROJECT, "ptk-" + "d" * 48, UPLOADER, KEY,
    )


@pytest.mark.parametrize("changes", [
    {"tenant_id": "MASTER"}, {"tenant_id": "GLOBAL_ROOT"},
    {"project_id": "invalid"}, {"task_id": "invalid"},
    {"attachment_id": "invalid"}, {"filename": "../../secret.txt"},
    {"filename": ".hidden.pdf"}, {"filename": "folder/document.pdf"},
    {"media_type": "application/x-msdownload"},
    {"size_bytes": 0}, {"size_bytes": MAX_ATTACHMENT_BYTES + 1},
    {"size_bytes": True}, {"content_sha3_512": "bad"},
    {"state": "AVAILABLE"}, {"state": "SCANNED_CLEAN"},
    {"state": "APPROVED"}, {"state": "SIGNED"}, {"revision": 2},
    {"created_at": NOW.replace(tzinfo=None)},
])
def test_unverified_or_unsafe_attachment_is_never_available(changes) -> None:
    """Quarantine is non-bypassable regardless of browser or provider claims."""
    with pytest.raises(ProjectAttachmentError):
        manifest(**changes)


def test_forged_digest_or_extra_evidence_field_denied() -> None:
    """Do not accept altered file identity or fictional scanner evidence."""
    original = manifest().to_dict()
    with pytest.raises(ProjectAttachmentError, match="FINGERPRINT_INVALID"):
        ProjectAttachment.hydrate({**original, "filename": "other.pdf"})
    with pytest.raises(ProjectAttachmentError, match="RECORD_INVALID"):
        ProjectAttachment.hydrate({**original, "malware_clean": True})
    with pytest.raises(ProjectAttachmentError, match="RECORD_INVALID"):
        ProjectAttachment.hydrate({**original, "approved_at": NOW.isoformat()})


# ARTIFACT: test_project_attachment_registry.py
# VERSION: v1.0.0-ATTACHMENT-EVIDENCE-FAIL-CLOSED-CERT
# AUTHORITY BOUNDARY: immutable metadata only, not byte scan or approval
# TENANT POSTURE: exact task, principal and upload idempotency origin
# FAIL-CLOSED POSTURE: untrusted release claims and source tamper reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
