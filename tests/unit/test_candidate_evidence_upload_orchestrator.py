import asyncio
from datetime import datetime, timezone
import hashlib

import pytest

from tools.eos.saas.hr.candidate_evidence_storage import (
    CandidateEvidenceBinaryObjectEvidence,
    CandidateEvidenceWriteIntent,
)
from tools.eos.saas.hr.candidate_evidence_upload_orchestrator import (
    CandidateEvidenceUploadOrchestrationError,
    CandidateEvidenceUploadOrchestrator,
)
from tools.eos.saas.hr.candidate_evidence_upload_attempt_registry import (
    CandidateEvidenceUploadAttempt,
    UploadAttemptStatus,
)


NOW = datetime(2026, 11, 7, 18, 0, tzinfo=timezone.utc)


def make_intent():
    return CandidateEvidenceWriteIntent(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        candidate_id="CAN-001",
        evidence_id="EVD-001",
        evidence_version_id="VER-001",
        ingestion_reference="ING-001",
        media_type="application/pdf",
        original_filename="profile.pdf",
        admitted_max_content_length=20 * 1024 * 1024,
    )


class MemoryRegistry:
    def __init__(self):
        self.rows = {}
        self.events = []

    def create(self, value, *, session):
        assert session is not None
        self.rows[value.upload_attempt_id] = value
        self.events.append(value.status)
        return value

    def get(self, *, tenant_id, upload_attempt_id, session):
        assert session is not None
        value = self.rows[upload_attempt_id]
        assert value.tenant_id == tenant_id
        return value

    def transition(self, current, updated, *, expected_revision, actor_principal_id, session):
        assert session is not None
        assert current.revision == expected_revision
        assert self.rows[current.upload_attempt_id].fingerprint == current.fingerprint
        self.rows[current.upload_attempt_id] = updated
        self.events.append(updated.status)
        return updated


class FakeStorage:
    def __init__(self, *, fail_complete=False):
        self.calls = []
        self.fail_complete = fail_complete

    def begin(self, intent):
        self.calls.append("begin")
        from tools.eos.saas.hr.candidate_evidence_storage import CandidateEvidenceWriteSession
        return CandidateEvidenceWriteSession(
            intent=intent,
            provider_upload_id="opaque/provider+upload==token",
            provider_object_key="hashed/object/key",
            storage_object_reference="hashed-object-reference",
            created_at=NOW,
        )

    def write_chunk(self, session, chunk):
        self.calls.append(("part", len(chunk)))
        number = len(session.parts) + 1
        etag = hashlib.sha3_256(chunk).hexdigest()
        session.parts.append({"PartNumber": number, "ETag": etag, "length": len(chunk)})
        session.bytes_written += len(chunk)
        session.hasher.update(chunk)
        return session.bytes_written

    def complete(self, session):
        self.calls.append("complete")
        if self.fail_complete:
            from tools.eos.saas.hr.candidate_evidence_s3_storage_adapter import CandidateEvidenceS3Error
            raise CandidateEvidenceS3Error("S3_COMPLETE_RESPONSE_LOST", uncertain=True)
        return CandidateEvidenceBinaryObjectEvidence(
            intent_fingerprint=session.intent.fingerprint,
            storage_object_reference=session.storage_object_reference,
            object_version_reference="opaque-version-id",
            provider_integrity_reference="opaque-etag",
            byte_length=session.bytes_written,
            content_digest_sha3_512=session.hasher.hexdigest(),
            completed_at=NOW,
        )

    def abort(self, session):
        self.calls.append("abort")
        session.closed = True


def transaction(callback):
    # Each callback represents a short, separately committed transaction.
    return callback(object())


async def chunks(*values):
    for value in values:
        yield value


def test_upload_commits_intent_before_provider_and_persists_each_part():
    registry = MemoryRegistry()
    storage = FakeStorage()
    orchestrator = CandidateEvidenceUploadOrchestrator(
        registry=registry, storage=storage, transaction=transaction,
        clock=lambda: NOW, id_factory=lambda: "UPL-TEST-001",
    )
    payload = b"x" * (8 * 1024 * 1024 + 123)
    attempt_id, evidence = asyncio.run(orchestrator.upload(
        intent=make_intent(), chunks=chunks(payload[:5_000_000], payload[5_000_000:]),
        actor_principal_id="PRINCIPAL-001",
    ))
    assert attempt_id == "UPL-TEST-001"
    assert registry.events[0] is UploadAttemptStatus.INITIATING
    assert storage.calls[0] == "begin"
    assert registry.events[1] is UploadAttemptStatus.INITIATED
    assert registry.events.count(UploadAttemptStatus.PARTS_UPLOADED) == 2
    final = registry.rows[attempt_id]
    assert final.status is UploadAttemptStatus.PROVIDER_VERIFIED
    assert final.byte_length == len(payload)
    assert final.object_version_reference == evidence.object_version_reference
    assert len(final.parts) == 2


def test_uncertain_completion_is_persisted_and_never_reported_as_verified():
    registry = MemoryRegistry()
    storage = FakeStorage(fail_complete=True)
    orchestrator = CandidateEvidenceUploadOrchestrator(
        registry=registry, storage=storage, transaction=transaction,
        clock=lambda: NOW, id_factory=lambda: "UPL-TEST-002",
    )
    with pytest.raises(CandidateEvidenceUploadOrchestrationError) as caught:
        asyncio.run(orchestrator.upload(
            intent=make_intent(), chunks=chunks(b"small final part"),
            actor_principal_id="PRINCIPAL-001",
        ))
    assert caught.value.uncertain is True
    assert registry.rows["UPL-TEST-002"].status is UploadAttemptStatus.COMPLETION_UNCERTAIN


def test_provider_initiation_failure_leaves_durable_initiating_attempt():
    class LostBegin(FakeStorage):
        def begin(self, intent):
            self.calls.append("begin")
            raise TimeoutError("provider response lost")

    registry = MemoryRegistry()
    storage = LostBegin()
    orchestrator = CandidateEvidenceUploadOrchestrator(
        registry=registry, storage=storage, transaction=transaction,
        clock=lambda: NOW, id_factory=lambda: "UPL-TEST-003",
    )
    with pytest.raises(CandidateEvidenceUploadOrchestrationError) as caught:
        asyncio.run(orchestrator.upload(
            intent=make_intent(), chunks=chunks(b"data"),
            actor_principal_id="PRINCIPAL-001",
        ))
    assert caught.value.uncertain is True
    pending = registry.rows["UPL-TEST-003"]
    assert pending.status is UploadAttemptStatus.INITIATING
    assert pending.provider_upload_id is None
    assert storage.calls == ["begin"]
