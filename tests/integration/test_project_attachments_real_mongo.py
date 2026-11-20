"""TITLE: WILSY OS Project Attachment Quarantine Replica Certificate
VERSION: v1.0.0-TASK-QUARANTINE-REPLAY-ISOLATION-CERT
AUTHORITY: Disposable Mongo source audit and idempotent file manifest writes.
EPITOME: Prove exact source rows, original replay, conflicting replay denial,
         foreign tenant/task isolation, and immutable quarantine audit.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_attachments_real_mongo.py
COLLABORATION / OWNERSHIP: ProjectAttachmentRegistry; Projects CI disposable RS.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-TASK-QUARANTINE-REPLAY-ISOLATION-CERT certifies
         source-bound metadata only. S3 and malware scanner remain independent.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic files/digests; no live provider object.
TENANT BOUNDARY: Exact tenant/project/task/uploader and command origin.
AUTHORITY BOUNDARY: Quarantine manifests cannot prove safe attachments.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.saas.projects.project_attachment_registry import (
    ProjectAttachment, ProjectAttachmentConflict, ProjectAttachmentNotFound,
    ProjectAttachmentRegistry, attachment_id_for_command,
)


def test_quarantine_manifest_exact_scope_replay_and_audit() -> None:
    """Certification never bypasses isolated Mongo indexes or source session."""
    uri = os.getenv("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable project replica not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    database = client.get_database("wilsy_project_attachment_cert")
    try:
        client.admin.command("ping")
        client.drop_database(database.name)
        manifests = database["wilsy_project_attachments"]
        events = database["wilsy_project_attachment_events"]
        ProjectAttachmentRegistry.ensure_indexes(manifests, events)
        assert manifests.index_information()["wilsy_project_attachment_identity"]["unique"]
        registry = ProjectAttachmentRegistry(manifests, events)
        tenant = "quarantine-test-tenant"
        project = "prj-" + "a" * 48
        task = "ptk-" + "b" * 48
        actor = "principal-contributor"
        key = "upload-uuid"
        instant = datetime.now(timezone.utc).replace(microsecond=0)
        source = ProjectAttachment(
            tenant_id=tenant, project_id=project, task_id=task,
            attachment_id=attachment_id_for_command(tenant, project, task, actor, key),
            uploader_principal_id=actor, filename="design.pdf",
            media_type="application/pdf", size_bytes=35,
            content_sha3_512="c" * 128,
            storage_receipt="d" * 128,
            created_at=instant,
        )

        def tx(fn):
            with client.start_session() as session:
                return session.with_transaction(
                    fn, read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        def create(session):
            return registry.create_or_replay(
                attachment=source, idempotency_key=key, session=session,
            )
        first = tx(create)
        assert first == source
        assert tx(create) == first
        assert first.state == "QUARANTINED"
        assert tx(lambda session: registry.get(
            tenant_id=tenant, project_id=project, task_id=task,
            attachment_id=first.attachment_id, session=session,
        )) == first
        timeline, more = tx(lambda session: registry.list_page(
            tenant_id=tenant, project_id=project, task_id=task, session=session,
        ))
        assert timeline == (first,) and more is False
        for different in (
            ("another-tenant", project, task),
            (tenant, "prj-" + "e" * 48, task),
            (tenant, project, "ptk-" + "f" * 48),
        ):
            empty, more = tx(lambda session: registry.list_page(
                tenant_id=different[0], project_id=different[1],
                task_id=different[2], session=session,
            ))
            assert empty == () and more is False
        with pytest.raises(ProjectAttachmentNotFound):
            tx(lambda session: registry.get(
                tenant_id="another-tenant", project_id=project,
                task_id=task, attachment_id=first.attachment_id,
                session=session,
            ))
        changed = ProjectAttachment(
            tenant_id=tenant, project_id=project, task_id=task,
            attachment_id=source.attachment_id, uploader_principal_id=actor,
            filename="unrelated.pdf", media_type="application/pdf",
            size_bytes=35, content_sha3_512="c" * 128,
            storage_receipt="d" * 128, created_at=instant,
        )
        with pytest.raises(ProjectAttachmentConflict, match="DIVERGENT_REPLAY"):
            tx(lambda session: registry.create_or_replay(
                attachment=changed, idempotency_key=key, session=session,
            ))
        assert manifests.count_documents({"tenant_id": tenant}) == 1
        assert events.count_documents({"tenant_id": tenant}) == 1
        stored = events.find_one({"tenant_id": tenant})
        assert stored["event_type"] == "PROJECT_ATTACHMENT_QUARANTINED"
        assert stored["result_fingerprint"] == first.fingerprint
    finally:
        client.drop_database(database.name)
        client.close()


# ARTIFACT: test_project_attachments_real_mongo.py
# VERSION: v1.0.0-TASK-QUARANTINE-REPLAY-ISOLATION-CERT
# AUTHORITY BOUNDARY: disposable source metadata proof, not S3/scan evidence
# TENANT POSTURE: exact task and upload command origin
# FAIL-CLOSED POSTURE: foreign, malformed, replay divergence denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
