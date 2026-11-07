"""Durable orchestration for streamed candidate-evidence multipart uploads.

Mongo transactions are caller-owned and never span S3 network calls. The
INITIATING attempt is committed before provider initiation; provider progress
is committed after each accepted part. Uncertain outcomes remain explicit.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, AsyncIterable, Callable
import uuid

from tools.eos.saas.hr.candidate_evidence_storage import (
    MAX_CHUNK_BYTES,
    MAX_OBJECT_BYTES,
    CandidateEvidenceBinaryObjectEvidence,
    CandidateEvidenceWriteIntent,
)
from tools.eos.saas.hr.candidate_evidence_upload_attempt_registry import (
    CandidateEvidenceUploadAttempt,
    CandidateEvidenceUploadAttemptRegistry,
    UploadAttemptStatus,
)
from tools.eos.saas.hr.candidate_evidence_s3_storage_adapter import (
    PROVIDER_ID,
    CandidateEvidenceS3Error,
)

_TARGET_PART_BYTES = 8 * 1024 * 1024


class CandidateEvidenceUploadOrchestrationError(RuntimeError):
    def __init__(self, code: str, *, uncertain: bool = False):
        self.code = code
        self.uncertain = uncertain
        super().__init__(code)


class CandidateEvidenceUploadOrchestrator:
    """Coordinates a durable attempt registry and provider storage port.

    transaction(callback) must execute callback(session) in a committed
    replica-set transaction. It must not retain a transaction while provider
    calls or request streaming are in progress.
    """

    def __init__(
        self,
        *,
        registry: CandidateEvidenceUploadAttemptRegistry,
        storage: Any,
        transaction: Callable[[Callable[[Any], Any]], Any],
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        id_factory: Callable[[], str] = lambda: "UPL-" + uuid.uuid4().hex,
    ):
        self._registry = registry
        self._storage = storage
        self._transaction = transaction
        self._clock = clock
        self._id_factory = id_factory

    def _create_pending(self, intent: CandidateEvidenceWriteIntent, attempt_id: str,
                        actor_id: str, offer_id: str | None) -> CandidateEvidenceUploadAttempt:
        now = self._clock()
        pending = CandidateEvidenceUploadAttempt(
            tenant_id=intent.tenant_id,
            upload_attempt_id=attempt_id,
            candidate_id=intent.candidate_id,
            evidence_id=intent.evidence_id,
            evidence_version_id=intent.evidence_version_id,
            ingestion_reference=intent.ingestion_reference,
            intent_fingerprint=intent.fingerprint,
            provider_id=PROVIDER_ID,
            provider_upload_id=None,
            provider_object_reference=None,
            status=UploadAttemptStatus.INITIATING,
            revision=1,
            created_at=now,
            updated_at=now,
            offer_id=offer_id,
        )
        return self._transaction(lambda session: self._registry.create(pending, session=session))

    def _advance(self, *, tenant_id: str, attempt_id: str, actor_id: str,
                 status: UploadAttemptStatus, **changes: Any) -> CandidateEvidenceUploadAttempt:
        def command(session: Any):
            current = self._registry.get(
                tenant_id=tenant_id, upload_attempt_id=attempt_id, session=session,
            )
            updated = current.advance(
                status=status, expected_revision=current.revision,
                occurred_at=self._clock(), **changes,
            )
            return self._registry.transition(
                current, updated, expected_revision=current.revision,
                actor_principal_id=actor_id, session=session,
            )
        return self._transaction(command)

    async def upload(
        self,
        *,
        intent: CandidateEvidenceWriteIntent,
        chunks: AsyncIterable[bytes],
        actor_principal_id: str,
        offer_id: str | None = None,
    ) -> tuple[str, CandidateEvidenceBinaryObjectEvidence]:
        if not actor_principal_id or actor_principal_id != actor_principal_id.strip():
            raise CandidateEvidenceUploadOrchestrationError("UPLOAD_ACTOR_REQUIRED")
        attempt_id = self._id_factory()
        # Commit this record before S3 is contacted. A process crash from this
        # point forward leaves a durable item for reconciliation.
        self._create_pending(intent, attempt_id, actor_principal_id, offer_id)

        try:
            session = await asyncio.to_thread(self._storage.begin, intent)
        except Exception as error:
            # Keep INITIATING: provider initiation may have succeeded despite a
            # lost response. Reconciliation must inspect provider state.
            raise CandidateEvidenceUploadOrchestrationError(
                "UPLOAD_PROVIDER_INITIATION_UNCERTAIN", uncertain=True,
            ) from error

        self._advance(
            tenant_id=intent.tenant_id, attempt_id=attempt_id,
            actor_id=actor_principal_id, status=UploadAttemptStatus.INITIATED,
            provider_upload_id=session.provider_upload_id,
            provider_object_reference=session.storage_object_reference,
        )

        total = 0
        buffer = bytearray()
        try:
            async for incoming in chunks:
                if not isinstance(incoming, bytes) or not incoming:
                    raise CandidateEvidenceUploadOrchestrationError("UPLOAD_CHUNK_INVALID")
                if len(incoming) > MAX_CHUNK_BYTES:
                    raise CandidateEvidenceUploadOrchestrationError("UPLOAD_CHUNK_LIMIT_EXCEEDED")
                total += len(incoming)
                if total > min(intent.admitted_max_content_length, MAX_OBJECT_BYTES):
                    raise CandidateEvidenceUploadOrchestrationError("UPLOAD_OBJECT_LIMIT_EXCEEDED")
                buffer.extend(incoming)
                while len(buffer) >= _TARGET_PART_BYTES:
                    part = bytes(buffer[:_TARGET_PART_BYTES])
                    del buffer[:_TARGET_PART_BYTES]
                    await self._write_part(session, part, intent, attempt_id, actor_principal_id)
            if buffer:
                await self._write_part(session, bytes(buffer), intent, attempt_id, actor_principal_id)
            if total <= 0:
                raise CandidateEvidenceUploadOrchestrationError("UPLOAD_EMPTY_OBJECT")
        except Exception as error:
            try:
                await asyncio.to_thread(self._storage.abort, session)
                self._advance(
                    tenant_id=intent.tenant_id, attempt_id=attempt_id,
                    actor_id=actor_principal_id, status=UploadAttemptStatus.ABORTED,
                    failure_code=getattr(error, "code", "UPLOAD_STREAM_FAILED"),
                )
            except Exception:
                # Preserve the original failure; durable INITIATED/PARTS state
                # remains available for provider-side reconciliation.
                pass
            if isinstance(error, CandidateEvidenceUploadOrchestrationError):
                raise
            raise CandidateEvidenceUploadOrchestrationError("UPLOAD_STREAM_FAILED") from error

        try:
            evidence = await asyncio.to_thread(self._storage.complete, session)
        except CandidateEvidenceS3Error as error:
            if error.uncertain:
                self._advance(
                    tenant_id=intent.tenant_id, attempt_id=attempt_id,
                    actor_id=actor_principal_id,
                    status=UploadAttemptStatus.COMPLETION_UNCERTAIN,
                    failure_code=error.code,
                )
                raise CandidateEvidenceUploadOrchestrationError(
                    "UPLOAD_COMPLETION_UNCERTAIN", uncertain=True,
                ) from error
            raise CandidateEvidenceUploadOrchestrationError(error.code) from error
        except Exception as error:
            self._advance(
                tenant_id=intent.tenant_id, attempt_id=attempt_id,
                actor_id=actor_principal_id,
                status=UploadAttemptStatus.COMPLETION_UNCERTAIN,
                failure_code="PROVIDER_COMPLETION_UNCERTAIN",
            )
            raise CandidateEvidenceUploadOrchestrationError(
                "UPLOAD_COMPLETION_UNCERTAIN", uncertain=True,
            ) from error

        if evidence.byte_length != total or evidence.intent_fingerprint != intent.fingerprint:
            self._advance(
                tenant_id=intent.tenant_id, attempt_id=attempt_id,
                actor_id=actor_principal_id,
                status=UploadAttemptStatus.COMPLETION_UNCERTAIN,
                failure_code="PROVIDER_COMPLETION_OBSERVATION_MISMATCH",
            )
            raise CandidateEvidenceUploadOrchestrationError(
                "UPLOAD_COMPLETION_UNCERTAIN", uncertain=True,
            )
        self._advance(
            tenant_id=intent.tenant_id, attempt_id=attempt_id,
            actor_id=actor_principal_id, status=UploadAttemptStatus.PROVIDER_VERIFIED,
            byte_length=evidence.byte_length,
            object_version_reference=evidence.object_version_reference,
            content_digest_sha3_512=evidence.content_digest_sha3_512,
            provider_integrity_reference=evidence.provider_integrity_reference,
        )
        return attempt_id, evidence

    async def _write_part(self, session: Any, part: bytes,
                         intent: CandidateEvidenceWriteIntent, attempt_id: str,
                         actor_id: str) -> None:
        await asyncio.to_thread(self._storage.write_chunk, session, part)
        persisted_parts = tuple(
            {"part_number": item["PartNumber"], "etag": item["ETag"], "length": item["length"]}
            for item in session.parts
        )
        self._advance(
            tenant_id=intent.tenant_id, attempt_id=attempt_id,
            actor_id=actor_id, status=UploadAttemptStatus.PARTS_UPLOADED,
            parts=persisted_parts, byte_length=session.bytes_written,
        )


__all__ = [
    "CandidateEvidenceUploadOrchestrationError",
    "CandidateEvidenceUploadOrchestrator",
]
