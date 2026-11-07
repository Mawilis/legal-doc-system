"""Replica-set transaction certification for provider completion recovery and custody."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
import hashlib

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.candidate_evidence import CandidateEvidenceKind
from tools.eos.saas.hr.candidate_evidence_registry import (
    COLLECTION as EVIDENCE_COLLECTION,
    EVENT_COLLECTION as EVIDENCE_EVENT_COLLECTION,
    CandidateEvidenceRegistry,
)
from tools.eos.saas.hr.candidate_evidence_storage import CandidateEvidenceBinaryObjectEvidence
from tools.eos.saas.hr.candidate_evidence_upload_attempt_registry import (
    COLLECTION as ATTEMPT_COLLECTION,
    EVENT_COLLECTION as ATTEMPT_EVENT_COLLECTION,
    CandidateEvidenceUploadAttempt,
    CandidateEvidenceUploadAttemptRegistry,
    UploadAttemptStatus,
)
from tools.eos.saas.hr.candidate_evidence_upload_reconciliation import CandidateEvidenceUploadReconciler

URI = os.getenv("HIRING_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")


class CompletedObjectStorage:
    def __init__(self, evidence):
        self.evidence = evidence

    def list_multipart_uploads(self):
        return []

    def inspect_completed_attempt(self, **kwargs):
        return self.evidence

    def object_key_for_scope(self, **kwargs):
        return "opaque-key"

    def storage_reference_for_scope(self, **kwargs):
        return "opaque-storage-reference"


def test_real_replica_set_recovers_uncertain_completion_and_commits_custody_with_attempt():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database_name = f"candidate_evidence_reconcile_{uuid.uuid4().hex}"
    db = client[database_name]
    now = datetime.now(timezone.utc)
    tenant = f"tenant-{uuid.uuid4().hex}"
    actor = f"principal-{uuid.uuid4().hex}"
    attempt_id = f"UPL-{uuid.uuid4().hex}"
    digest = hashlib.sha3_512(b"replica-set-recovered-evidence").hexdigest()
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        attempts_collection = db[ATTEMPT_COLLECTION]
        attempt_events = db[ATTEMPT_EVENT_COLLECTION]
        evidence_collection = db[EVIDENCE_COLLECTION]
        evidence_events = db[EVIDENCE_EVENT_COLLECTION]
        CandidateEvidenceUploadAttemptRegistry.ensure_indexes(attempts_collection, attempt_events)
        CandidateEvidenceRegistry.ensure_indexes(evidence_collection, evidence_events)
        attempt_registry = CandidateEvidenceUploadAttemptRegistry(attempts_collection, attempt_events)
        custody_registry = CandidateEvidenceRegistry(evidence_collection, evidence_events)

        pending = CandidateEvidenceUploadAttempt(
            tenant_id=tenant, upload_attempt_id=attempt_id,
            candidate_id="CAN-RECON-1", evidence_id="EVD-RECON-1",
            evidence_version_id="VER-RECON-1", ingestion_reference="ING-RECON-1",
            intent_fingerprint=digest, provider_id="aws_s3",
            provider_upload_id="opaque-upload-id", provider_object_reference="opaque-object-reference",
            status=UploadAttemptStatus.COMPLETION_UNCERTAIN, revision=1,
            created_at=now - timedelta(hours=3), updated_at=now - timedelta(hours=3),
            actor_principal_id=actor, evidence_kind=CandidateEvidenceKind.CANDIDATE_PROFILE.value,
            media_type="application/pdf", original_filename="profile.pdf",
            admitted_max_content_length=1024,
        )

        def transaction(callback):
            with client.start_session() as session:
                return session.with_transaction(
                    callback,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern(w="majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )

        transaction(lambda session: attempt_registry.create(pending, session=session))
        evidence = CandidateEvidenceBinaryObjectEvidence(
            intent_fingerprint=digest, storage_object_reference="opaque-storage-reference",
            object_version_reference="opaque-version-id", provider_integrity_reference="opaque-etag",
            byte_length=len(b"replica-set-recovered-evidence"),
            content_digest_sha3_512=hashlib.sha3_512(b"replica-set-recovered-evidence").hexdigest(),
            completed_at=now,
        )
        reconciler = CandidateEvidenceUploadReconciler(
            registry=attempt_registry, custody_registry=custody_registry,
            storage=CompletedObjectStorage(evidence), transaction=transaction,
            reconciliation_actor_principal_id="SYSTEM-HR-EVIDENCE-RECONCILER",
            clock=lambda: now, stale_after=timedelta(hours=1),
        )
        result = reconciler.run_once()

        def readback(session):
            attempt = attempt_registry.get(
                tenant_id=tenant, upload_attempt_id=attempt_id, session=session,
            )
            metadata = custody_registry.get(
                tenant_id=tenant, candidate_id="CAN-RECON-1",
                evidence_id="EVD-RECON-1", evidence_version_id="VER-RECON-1",
                session=session,
            )
            return attempt, metadata
        recovered, custody = transaction(readback)
        assert recovered.status is UploadAttemptStatus.CUSTODY_REGISTERED
        assert recovered.object_version_reference == "opaque-version-id"
        assert custody.evidence_kind is CandidateEvidenceKind.CANDIDATE_PROFILE
        assert custody.created_by_principal_id == actor
        assert result["completed_recovered"] == 1
        assert result["custody_registered"] == 1
        assert attempts_collection.count_documents({"tenant_id": tenant}) == 1
        assert attempt_events.count_documents({"tenant_id": tenant}) == 3
        assert evidence_collection.count_documents({"tenant_id": tenant}) == 1
        assert evidence_events.count_documents({"tenant_id": tenant}) == 1
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()
