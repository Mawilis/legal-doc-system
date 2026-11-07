from datetime import datetime, timedelta, timezone
import hashlib

from tools.eos.saas.hr.candidate_evidence_upload_attempt_registry import (
    CandidateEvidenceUploadAttempt, UploadAttemptStatus,
)
from tools.eos.saas.hr.candidate_evidence_upload_reconciliation import (
    CandidateEvidenceUploadReconciler,
)
from tools.eos.saas.hr.candidate_evidence_storage import CandidateEvidenceBinaryObjectEvidence


NOW = datetime(2026, 11, 7, 20, 0, tzinfo=timezone.utc)
DIGEST = hashlib.sha3_512(b"evidence").hexdigest()


def attempt(status, *, old=False):
    created = NOW - timedelta(hours=4)
    updated = created if old else NOW
    provider_id = None if status is UploadAttemptStatus.INITIATING else "opaque-upload-id"
    object_ref = None if status is UploadAttemptStatus.INITIATING else "opaque-object-ref"
    return CandidateEvidenceUploadAttempt(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        upload_attempt_id="UPL-RECON-001",
        candidate_id="CAN-001",
        evidence_id="EVD-001",
        evidence_version_id="VER-001",
        ingestion_reference="ING-001",
        intent_fingerprint=DIGEST,
        provider_id="aws_s3",
        provider_upload_id=provider_id,
        provider_object_reference=object_ref,
        status=status,
        revision=1,
        created_at=created,
        updated_at=updated,
        offer_id=None,
        actor_principal_id="PRINCIPAL-001",
        evidence_kind="CANDIDATE_PROFILE",
        media_type="application/pdf",
        original_filename="profile.pdf",
        admitted_max_content_length=1024,
    )


class MemoryRegistry:
    def __init__(self, values):
        self.values = {value.upload_attempt_id: value for value in values}

    def list_reconcilable(self, *, session, limit):
        assert session is not None
        return tuple(self.values.values())[:limit]

    def get(self, *, tenant_id, upload_attempt_id, session):
        assert session is not None
        value = self.values[upload_attempt_id]
        assert value.tenant_id == tenant_id
        return value

    def transition(self, current, updated, *, expected_revision, actor_principal_id, session):
        assert session is not None
        assert current.revision == expected_revision
        self.values[current.upload_attempt_id] = updated
        return updated


class FakeStorage:
    def __init__(self, uploads=(), completed=None, parts=()):
        self.uploads = list(uploads)
        self.completed = completed
        self.parts = list(parts)
        self.aborted = []

    def object_key_for_scope(self, **scope):
        return "hr-candidate-evidence/v1/" + scope["tenant_id"] + "/" + scope["ingestion_reference"]

    def storage_reference_for_scope(self, **scope):
        return "opaque-object-reference"

    def list_multipart_uploads(self):
        return list(self.uploads)

    def list_uploaded_parts(self, *, key, upload_id):
        return list(self.parts)

    def inspect_completed_attempt(self, **scope):
        return self.completed

    def abort_provider_upload(self, *, key, upload_id):
        self.aborted.append((key, upload_id))


class MemoryCustody:
    def __init__(self):
        self.values = []

    def register(self, value, *, actor_principal_id, idempotency_key, session):
        assert session is not None
        self.values.append((value, actor_principal_id, idempotency_key))
        return value


def transaction(callback):
    return callback(object())


def reconciler(registry, storage, custody):
    return CandidateEvidenceUploadReconciler(
        registry=registry, custody_registry=custody, storage=storage,
        transaction=transaction,
        reconciliation_actor_principal_id="SYSTEM-HR-EVIDENCE-RECONCILER",
        clock=lambda: NOW, stale_after=timedelta(hours=2),
    )


def test_reconciles_lost_multipart_initiation_response():
    pending = attempt(UploadAttemptStatus.INITIATING, old=True)
    storage = FakeStorage(uploads=[{
        "key": "hr-candidate-evidence/v1/WILSYTENANT-4CD2FZ4O/ING-001",
        "upload_id": "opaque-upload-id",
        "initiated_at": NOW - timedelta(hours=3),
    }])
    registry = MemoryRegistry([pending])
    result = reconciler(registry, storage, MemoryCustody()).run_once()
    recovered = registry.values[pending.upload_attempt_id]
    assert recovered.status is UploadAttemptStatus.INITIATED
    assert recovered.provider_upload_id == "opaque-upload-id"
    assert result["initiated_recovered"] == 1


def test_recovers_uncertain_completion_and_registers_custody_atomically():
    uncertain = attempt(UploadAttemptStatus.COMPLETION_UNCERTAIN, old=True)
    evidence = CandidateEvidenceBinaryObjectEvidence(
        intent_fingerprint=uncertain.intent_fingerprint,
        storage_object_reference="opaque-object-reference",
        object_version_reference="opaque-version-id",
        provider_integrity_reference="opaque-etag",
        byte_length=8,
        content_digest_sha3_512=DIGEST,
        completed_at=NOW - timedelta(hours=3),
    )
    registry = MemoryRegistry([uncertain])
    custody = MemoryCustody()
    result = reconciler(registry, FakeStorage(completed=evidence), custody).run_once()
    recovered = registry.values[uncertain.upload_attempt_id]
    assert recovered.status is UploadAttemptStatus.CUSTODY_REGISTERED
    assert recovered.object_version_reference == "opaque-version-id"
    assert len(custody.values) == 1
    assert custody.values[0][0].created_by_principal_id == "PRINCIPAL-001"
    assert result["completed_recovered"] == 1
    assert result["custody_registered"] == 1


def test_stale_unknown_provider_multipart_is_aborted():
    storage = FakeStorage(uploads=[{
        "key": "hr-candidate-evidence/v1/unowned",
        "upload_id": "orphan-upload",
        "initiated_at": NOW - timedelta(hours=3),
    }])
    result = reconciler(MemoryRegistry([]), storage, MemoryCustody()).run_once()
    assert storage.aborted == [("hr-candidate-evidence/v1/unowned", "orphan-upload")]
    assert result["uploads_aborted"] == 1


def test_unresolved_initiating_attempt_can_be_marked_orphaned_without_provider_id():
    pending = attempt(UploadAttemptStatus.INITIATING, old=True)
    registry = MemoryRegistry([pending])
    result = reconciler(registry, FakeStorage(), MemoryCustody()).run_once()
    orphan = registry.values[pending.upload_attempt_id]
    assert orphan.status is UploadAttemptStatus.ORPHANED
    assert orphan.provider_upload_id is None
    assert result["attempts_orphaned"] == 1
