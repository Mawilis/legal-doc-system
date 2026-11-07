"""Provider-side reconciliation for interrupted candidate-evidence uploads.

The reconciler uses bounded caller-owned Mongo transactions around registry
reads/writes only. S3 discovery, part inspection, object readback and aborts
always happen outside Mongo transactions. It requires an explicitly supplied
EOS service principal for append-only reconciliation events.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from tools.eos.saas.domain.candidate_evidence import (
    CandidateEvidenceKind,
    CandidateEvidenceObjectMetadata,
)
from tools.eos.saas.hr.candidate_evidence_upload_attempt_registry import (
    CandidateEvidenceUploadAttempt,
    CandidateEvidenceUploadAttemptRegistry,
    UploadAttemptStatus,
)


class CandidateEvidenceUploadReconciliationError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class CandidateEvidenceUploadReconciler:
    def __init__(
        self,
        *,
        registry: CandidateEvidenceUploadAttemptRegistry,
        custody_registry: Any,
        storage: Any,
        transaction: Callable[[Callable[[Any], Any]], Any],
        reconciliation_actor_principal_id: str,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        stale_after: timedelta = timedelta(hours=2),
        batch_limit: int = 500,
    ):
        if not isinstance(reconciliation_actor_principal_id, str) or not reconciliation_actor_principal_id.strip():
            raise CandidateEvidenceUploadReconciliationError("RECONCILIATION_ACTOR_REQUIRED")
        if not isinstance(stale_after, timedelta) or stale_after <= timedelta(0):
            raise CandidateEvidenceUploadReconciliationError("RECONCILIATION_STALE_WINDOW_INVALID")
        if type(batch_limit) is not int or not 1 <= batch_limit <= 1000:
            raise CandidateEvidenceUploadReconciliationError("RECONCILIATION_BATCH_LIMIT_INVALID")
        self._registry = registry
        self._custody = custody_registry
        self._storage = storage
        self._transaction = transaction
        self._actor = reconciliation_actor_principal_id
        self._clock = clock
        self._stale_after = stale_after
        self._batch_limit = batch_limit

    def _load(self):
        return self._transaction(
            lambda session: self._registry.list_reconcilable(
                session=session, limit=self._batch_limit,
            )
        )

    def _advance(self, attempt: CandidateEvidenceUploadAttempt, status: UploadAttemptStatus, **changes):
        def command(session):
            current = self._registry.get(
                tenant_id=attempt.tenant_id,
                upload_attempt_id=attempt.upload_attempt_id,
                session=session,
            )
            updated = current.advance(
                status=status,
                expected_revision=current.revision,
                occurred_at=self._clock(),
                **changes,
            )
            return self._registry.transition(
                current, updated, expected_revision=current.revision,
                actor_principal_id=self._actor, session=session,
            )
        return self._transaction(command)

    def _key(self, attempt: CandidateEvidenceUploadAttempt) -> str:
        return self._storage.object_key_for_scope(
            tenant_id=attempt.tenant_id,
            candidate_id=attempt.candidate_id,
            evidence_id=attempt.evidence_id,
            evidence_version_id=attempt.evidence_version_id,
            ingestion_reference=attempt.ingestion_reference,
        )

    def _object_reference(self, attempt: CandidateEvidenceUploadAttempt) -> str:
        return self._storage.storage_reference_for_scope(
            tenant_id=attempt.tenant_id,
            candidate_id=attempt.candidate_id,
            evidence_id=attempt.evidence_id,
            evidence_version_id=attempt.evidence_version_id,
            ingestion_reference=attempt.ingestion_reference,
        )

    def _inspect_completed(self, attempt: CandidateEvidenceUploadAttempt):
        return self._storage.inspect_completed_attempt(
            tenant_id=attempt.tenant_id,
            candidate_id=attempt.candidate_id,
            evidence_id=attempt.evidence_id,
            evidence_version_id=attempt.evidence_version_id,
            ingestion_reference=attempt.ingestion_reference,
            intent_fingerprint=attempt.intent_fingerprint,
            media_type=attempt.media_type,
        )

    def _register_custody(self, attempt: CandidateEvidenceUploadAttempt, evidence: Any) -> bool:
        # Older attempts may predate durable recovery context. They remain
        # provider-verified but are never assigned invented evidence metadata.
        if not all((
            attempt.actor_principal_id, attempt.evidence_kind,
            attempt.media_type, attempt.original_filename,
            attempt.admitted_max_content_length,
        )):
            return False
        metadata = CandidateEvidenceObjectMetadata(
            tenant_id=attempt.tenant_id,
            candidate_id=attempt.candidate_id,
            evidence_id=attempt.evidence_id,
            evidence_version_id=attempt.evidence_version_id,
            evidence_kind=CandidateEvidenceKind(attempt.evidence_kind),
            media_type=attempt.media_type,
            original_filename=attempt.original_filename,
            byte_length=evidence.byte_length,
            content_digest_sha3_512=evidence.content_digest_sha3_512,
            storage_provider_id=attempt.provider_id,
            storage_object_reference=evidence.storage_object_reference,
            object_version_reference=evidence.object_version_reference,
            provider_integrity_reference=evidence.provider_integrity_reference,
            ingestion_reference=attempt.ingestion_reference,
            created_at=evidence.completed_at,
            created_by_principal_id=attempt.actor_principal_id,
            offer_id=attempt.offer_id,
        )

        def command(session):
            self._custody.register(
                metadata,
                actor_principal_id=attempt.actor_principal_id,
                idempotency_key=f"reconcile-custody:{attempt.upload_attempt_id}",
                session=session,
            )
            current = self._registry.get(
                tenant_id=attempt.tenant_id,
                upload_attempt_id=attempt.upload_attempt_id,
                session=session,
            )
            updated = current.advance(
                status=UploadAttemptStatus.CUSTODY_REGISTERED,
                expected_revision=current.revision,
                occurred_at=self._clock(),
            )
            return self._registry.transition(
                current, updated, expected_revision=current.revision,
                actor_principal_id=self._actor, session=session,
            )
        self._transaction(command)
        return True

    def run_once(self) -> dict[str, int]:
        attempts = self._load()
        # A full batch may be truncated. In that case cleanup of unrecognised
        # provider uploads is disabled to avoid aborting an attempt not loaded.
        provider_uploads = self._storage.list_multipart_uploads()
        by_key: dict[str, list[dict[str, Any]]] = {}
        for upload in provider_uploads:
            by_key.setdefault(upload["key"], []).append(upload)

        counters = {
            "examined": 0, "initiated_recovered": 0, "parts_reconciled": 0,
            "completed_recovered": 0, "custody_registered": 0,
            "attempts_orphaned": 0, "uploads_aborted": 0,
            "recovery_context_incomplete": 0,
        }
        known_pairs: set[tuple[str, str]] = set()
        for original in attempts:
            counters["examined"] += 1
            attempt = original
            key = self._key(attempt)
            matches = by_key.get(key, [])
            provider = next(
                (item for item in matches if (
                    attempt.provider_upload_id is None
                    or item["upload_id"] == attempt.provider_upload_id
                )),
                None,
            )
            if provider is not None:
                known_pairs.add((provider["key"], provider["upload_id"]))
                if attempt.status is UploadAttemptStatus.INITIATING:
                    attempt = self._advance(
                        attempt, UploadAttemptStatus.INITIATED,
                        provider_upload_id=provider["upload_id"],
                        provider_object_reference=self._object_reference(attempt),
                    )
                    counters["initiated_recovered"] += 1

                if attempt.status in {
                    UploadAttemptStatus.INITIATED,
                    UploadAttemptStatus.PARTS_UPLOADED,
                }:
                    parts = self._storage.list_uploaded_parts(
                        key=key, upload_id=provider["upload_id"],
                    )
                    normalized = tuple(sorted(parts, key=lambda item: item["PartNumber"]))
                    total = sum(item["length"] for item in normalized)
                    if (
                        len(normalized) > 10000
                        or total > (attempt.admitted_max_content_length or 100 * 1024 * 1024)
                        or any(item["PartNumber"] != index + 1 for index, item in enumerate(normalized))
                    ):
                        raise CandidateEvidenceUploadReconciliationError("RECONCILIATION_PROVIDER_PARTS_INVALID")
                    existing = tuple(dict(item) for item in attempt.parts)
                    if normalized and normalized != existing:
                        self._advance(
                            attempt, UploadAttemptStatus.PARTS_UPLOADED,
                            parts=normalized, byte_length=total,
                        )
                        counters["parts_reconciled"] += 1
                # A multipart session is still provider-live. Do not abort it
                # merely because the request is slow; updated_at is the stale
                # progress lease and only the uncertain terminal path is reaped.
                if attempt.status is UploadAttemptStatus.COMPLETION_UNCERTAIN:
                    if self._clock() - attempt.updated_at >= self._stale_after:
                        self._storage.abort_provider_upload(
                            key=key, upload_id=provider["upload_id"],
                        )
                        self._advance(attempt, UploadAttemptStatus.ABORTED,
                                      failure_code="RECONCILIATION_ABORTED_STALE_UNCERTAIN_UPLOAD")
                        counters["uploads_aborted"] += 1
                continue

            # No active multipart upload: inspect versioned objects before
            # considering the attempt abandoned or orphaned.
            evidence = self._inspect_completed(attempt)
            if evidence is not None:
                if attempt.admitted_max_content_length is not None and evidence.byte_length > attempt.admitted_max_content_length:
                    raise CandidateEvidenceUploadReconciliationError("RECONCILIATION_OBJECT_EXCEEDS_ADMITTED_LENGTH")
                if attempt.status is not UploadAttemptStatus.PROVIDER_VERIFIED:
                    attempt = self._advance(
                        attempt, UploadAttemptStatus.PROVIDER_VERIFIED,
                        byte_length=evidence.byte_length,
                        object_version_reference=evidence.object_version_reference,
                        content_digest_sha3_512=evidence.content_digest_sha3_512,
                        provider_integrity_reference=evidence.provider_integrity_reference,
                    )
                    counters["completed_recovered"] += 1
                if self._register_custody(attempt, evidence):
                    counters["custody_registered"] += 1
                else:
                    counters["recovery_context_incomplete"] += 1
                continue

            if self._clock() - attempt.updated_at < self._stale_after:
                continue
            if attempt.status is UploadAttemptStatus.INITIATING:
                self._advance(
                    attempt, UploadAttemptStatus.ORPHANED,
                    failure_code="RECONCILIATION_PROVIDER_INITIATION_NOT_FOUND",
                )
                counters["attempts_orphaned"] += 1
            elif attempt.status is UploadAttemptStatus.COMPLETION_UNCERTAIN:
                self._advance(
                    attempt, UploadAttemptStatus.ORPHANED,
                    failure_code="RECONCILIATION_COMPLETED_OBJECT_NOT_FOUND",
                )
                counters["attempts_orphaned"] += 1
            elif attempt.status in {
                UploadAttemptStatus.INITIATED,
                UploadAttemptStatus.PARTS_UPLOADED,
            }:
                self._advance(
                    attempt, UploadAttemptStatus.ABORTED,
                    failure_code="RECONCILIATION_PROVIDER_UPLOAD_NOT_FOUND",
                )
                counters["attempts_orphaned"] += 1
            elif attempt.status is UploadAttemptStatus.PROVIDER_VERIFIED:
                counters["recovery_context_incomplete"] += 1

        if len(attempts) < self._batch_limit:
            for upload in provider_uploads:
                pair = (upload["key"], upload["upload_id"])
                if pair in known_pairs:
                    continue
                initiated = upload.get("initiated_at")
                if isinstance(initiated, datetime) and self._clock() - initiated < self._stale_after:
                    continue
                self._storage.abort_provider_upload(key=upload["key"], upload_id=upload["upload_id"])
                counters["uploads_aborted"] += 1
        return counters


__all__ = [
    "CandidateEvidenceUploadReconciliationError",
    "CandidateEvidenceUploadReconciler",
]
