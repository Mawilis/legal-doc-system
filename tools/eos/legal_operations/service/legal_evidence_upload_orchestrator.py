"""WILSY OS authenticated Legal Evidence upload orchestration.

TITLE: Authenticated Legal Evidence Upload Orchestrator
VERSION: v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Compose canonical ProcessDocument resolution, commercial capacity,
         durable write intent, streamed provider execution, two-plane commit,
         and commit-uncertainty evidence without creating parallel truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_upload_orchestrator.py
COLLABORATION / OWNERSHIP: Existing L8 lifecycle, D22 entitlement, L10A2
                            capacity/storage/commit authorities retain truth;
                            this module owns ordering and transaction mechanics.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L10A4 establishes the production composition boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant scope is server-authorized; provider
                             configuration remains server-side; responses omit
                             provider coordinates, credentials, PII and Mongo IDs.
TENANT BOUNDARY: The authorized tenant plus current ProcessDocument are the
                 exclusive tenant/document/matter authority.
AUTHORITY BOUNDARY: Orchestration only; no IAM, lifecycle, availability,
                    retention, deletion, provider, or financial truth is invented.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hmac
from typing import Any, BinaryIO, Final
from uuid import uuid4

from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import open_legal_evidence_commit_uncertainty
from tools.eos.legal_operations.domain.legal_evidence_content import MAX_CONTENT_BYTES
from tools.eos.legal_operations.domain.legal_evidence_ingestion_admission import LegalEvidenceIngestionAdmission
from tools.eos.legal_operations.domain.legal_operations_current_projection import resolve_current_lifecycle_snapshot
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ProcessDocument
from tools.eos.legal_operations.registry import legal_evidence_capacity_admission_fence_registry as fence_module
from tools.eos.legal_operations.registry import legal_evidence_capacity_reservation_registry as reservation_module
from tools.eos.legal_operations.registry import legal_evidence_commit_uncertainty_registry as uncertainty_module
from tools.eos.legal_operations.registry import legal_evidence_object_metadata_registry as metadata_module
from tools.eos.legal_operations.registry import legal_evidence_usage_observation_registry as usage_module
from tools.eos.legal_operations.registry.legal_evidence_binary_write_intent_registry import COLLECTION as INTENT_COLLECTION, LegalEvidenceBinaryWriteIntentRegistry
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import COLLECTION as LIFECYCLE_COLLECTION, LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import MAX_STREAM_CHUNK_BYTES, LegalEvidenceBinaryChunkEvidence, LegalEvidenceBinaryStoragePort, StreamingSHA3512
from tools.eos.legal_operations.service.legal_evidence_capacity_reservation_lifecycle_service import LegalEvidenceCapacityReservationLifecycleService
from tools.eos.legal_operations.service.legal_evidence_capacity_reservation_service import LegalEvidenceCapacityReservationService
from tools.eos.legal_operations.service.legal_evidence_ingestion_orchestration_service import LegalEvidenceIngestionOrchestrationService
from tools.eos.legal_operations.service.legal_evidence_two_plane_commit_service import LegalEvidenceTwoPlaneCommitService
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.billing.legal_evidence_capacity_tenant_profile_resolver import derive_legal_evidence_capacity_tenant_profile
from tools.eos.saas.domain.subscription import SubscriptionStatus
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import derive_tenant_product_entitlement_id
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as entitlement_module


VERSION: Final[str] = "v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-ORCHESTRATOR"
MAX_UPLOAD_BYTES: Final[int] = MAX_CONTENT_BYTES
RESERVATION_TTL: Final[timedelta] = timedelta(minutes=30)
_WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
_READ_CONCERN: Final[ReadConcern] = ReadConcern("snapshot")


class LegalEvidenceUploadError(RuntimeError):
    """Stable fail-closed upload composition failure with no authority grant."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class LegalEvidenceUploadResult:
    """Browser-safe canonical commit or durable reconciliation projection."""

    ingestion_reference: str
    document_id: str
    case_matter_id: str
    state: str
    content_reference: str | None
    content_fingerprint: str
    content_length: int
    uncertainty_id: str | None = None


def _collection(database: Any, name: str) -> Any:
    if database is None or not hasattr(database, "get_collection"):
        raise LegalEvidenceUploadError("LEGAL_EVIDENCE_PERSISTENCE_UNAVAILABLE")
    return database.get_collection(name, write_concern=_WRITE_CONCERN)


def _start_transaction(session: Any) -> None:
    session.start_transaction(read_concern=_READ_CONCERN, write_concern=_WRITE_CONCERN)


class LegalEvidenceUploadOrchestrator:
    """Execute one bounded upload while preserving all certified authorities.

    The caller supplies an already-authorized tenant and a seekable bounded
    transport stream. This service owns Mongo transaction lifecycles, but every
    domain/registry service retains its existing authority and replay contract.
    """

    def __init__(self, *, client: Any, database: Any, storage: LegalEvidenceBinaryStoragePort) -> None:
        if client is None or database is None or storage is None:
            raise LegalEvidenceUploadError("LEGAL_EVIDENCE_UPLOAD_DEPENDENCY_REQUIRED")
        self._client = client
        self._database = database
        self._storage = storage

    def _registries(self) -> tuple[Any, Any, Any, Any, Any, Any]:
        fence = fence_module.LegalEvidenceCapacityAdmissionFenceRegistry(_collection(self._database, fence_module.COLLECTION))
        reservation = reservation_module.LegalEvidenceCapacityReservationRegistry(_collection(self._database, reservation_module.COLLECTION))
        usage = usage_module.LegalEvidenceUsageObservationRegistry(_collection(self._database, usage_module.COLLECTION))
        intent = LegalEvidenceBinaryWriteIntentRegistry(_collection(self._database, INTENT_COLLECTION))
        metadata = metadata_module.LegalEvidenceObjectMetadataRegistry(_collection(self._database, metadata_module.COLLECTION))
        uncertainty = uncertainty_module.LegalEvidenceCommitUncertaintyRegistry(_collection(self._database, uncertainty_module.COLLECTION))
        fence.ensure_indexes()
        reservation.ensure_indexes()
        usage_module.ensure_indexes(_collection(self._database, usage_module.COLLECTION))
        intent.ensure_indexes()
        metadata.ensure_indexes()
        uncertainty.ensure_indexes()
        return fence, reservation, usage, intent, metadata, uncertainty

    def _current_document_and_profile(self, tenant_id: str, document_id: str, *, session: Any, admitted_at: datetime) -> tuple[ProcessDocument, Any]:
        history = LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id, "ProcessDocument", document_id,
            _collection(self._database, LIFECYCLE_COLLECTION), session=session,
        )
        document = resolve_current_lifecycle_snapshot(history, expected_type=ProcessDocument)
        if type(document) is not ProcessDocument or document.tenant_id != tenant_id or document.document_id != document_id:
            raise LegalEvidenceUploadError("LEGAL_EVIDENCE_DOCUMENT_UNAVAILABLE")

        subscriptions = tuple(
            item for item in SubscriptionRegistry.list_entities(
                tenant_id, collection=_collection(self._database, "subscriptions"), session=session,
            ) if item.status is SubscriptionStatus.ACTIVE
        )
        if len(subscriptions) != 1:
            raise LegalEvidenceUploadError("LEGAL_EVIDENCE_ACTIVE_SUBSCRIPTION_REQUIRED")
        entitlement_id = derive_tenant_product_entitlement_id(tenant_id, TenantProductId.LEGAL_OPERATIONS)
        entitlement = entitlement_module.get_current(
            tenant_id, entitlement_id,
            _collection(self._database, entitlement_module.HISTORY_COLLECTION),
            _collection(self._database, entitlement_module.CURRENT_COLLECTION),
            session=session,
        )
        profile = derive_legal_evidence_capacity_tenant_profile(
            tenant_id=tenant_id, subscription=subscriptions[0], entitlement=entitlement, evaluated_at=admitted_at,
        )
        return document, profile

    def upload(self, *, tenant_id: str, document_id: str, filename: str, media_type: str, content_length: int, stream: BinaryIO, idempotency_key: str) -> LegalEvidenceUploadResult:
        """Upload and canonically commit one exact server-scoped evidence object.

        Provider completion followed by an unproven Mongo outcome is persisted
        as uncertainty and returned as RECONCILIATION_REQUIRED, never COMMITTED.
        """
        if isinstance(content_length, bool) or not isinstance(content_length, int) or content_length <= 0 or content_length > MAX_UPLOAD_BYTES:
            raise LegalEvidenceUploadError("LEGAL_EVIDENCE_CONTENT_LENGTH_INVALID")
        if not all(isinstance(value, str) and value and value == value.strip() for value in (tenant_id, document_id, filename, media_type, idempotency_key)):
            raise LegalEvidenceUploadError("LEGAL_EVIDENCE_UPLOAD_INPUT_INVALID")
        now = datetime.now(timezone.utc)
        fence, reservation_registry, usage, intent_registry, metadata, uncertainty_registry = self._registries()
        capacity = LegalEvidenceCapacityReservationService(fence_registry=fence, usage_registry=usage, reservation_registry=reservation_registry)
        ingestion = LegalEvidenceIngestionOrchestrationService(capacity_service=capacity, write_intent_registry=intent_registry, storage=self._storage)
        lifecycle = LegalEvidenceCapacityReservationLifecycleService(fence_registry=fence, reservation_registry=reservation_registry, usage_registry=usage)
        two_plane = LegalEvidenceTwoPlaneCommitService(metadata_registry=metadata, lifecycle_service=lifecycle)

        with self._client.start_session() as session:
            _start_transaction(session)
            try:
                document, profile = self._current_document_and_profile(tenant_id, document_id, session=session, admitted_at=now)
                admission = LegalEvidenceIngestionAdmission.issue(
                    process_document=document, media_type=media_type, original_filename=filename,
                    declared_content_length=content_length, admitted_at=now,
                )
                reservation_id = f"legal-evidence-reservation:{uuid4().hex}"
                prepared = ingestion.prepare(
                    admission=admission, reservation_id=reservation_id, idempotency_key=idempotency_key,
                    tenant_profile=profile, reserved_at=now, expires_at=now + RESERVATION_TTL, session=session,
                )
                session.commit_transaction()
            except Exception:
                if bool(getattr(session, "in_transaction", False)):
                    session.abort_transaction()
                raise

        with self._client.start_session() as session:
            _start_transaction(session)
            try:
                verified = ingestion.verify_durable(prepared=prepared, session=session)
                session.commit_transaction()
            except Exception:
                if bool(getattr(session, "in_transaction", False)):
                    session.abort_transaction()
                raise

        write_session = ingestion.begin_provider(verified=verified)
        intent = prepared.write_intent_record.intent
        hasher = StreamingSHA3512()
        chunks: list[LegalEvidenceBinaryChunkEvidence] = []
        try:
            sequence = 0
            observed = 0
            while True:
                chunk = stream.read(MAX_STREAM_CHUNK_BYTES)
                if not chunk:
                    break
                if not isinstance(chunk, bytes) or observed + len(chunk) > content_length:
                    raise LegalEvidenceUploadError("LEGAL_EVIDENCE_STREAM_LENGTH_INVALID")
                hasher.update(chunk)
                chunks.append(self._storage.write_chunk(intent, write_session, sequence=sequence, chunk=chunk))
                sequence += 1
                observed += len(chunk)
            if observed != content_length or not chunks:
                raise LegalEvidenceUploadError("LEGAL_EVIDENCE_STREAM_LENGTH_INVALID")
            hashed_length, digest = hasher.finalize()
            if hashed_length != observed:
                raise LegalEvidenceUploadError("LEGAL_EVIDENCE_STREAM_LENGTH_INVALID")
            object_evidence = self._storage.complete(
                intent, write_session, chunks=tuple(chunks), content_length=observed, content_fingerprint=digest,
            )
        except Exception:
            try:
                self._storage.abort(intent, write_session)
            except Exception as abort_error:
                raise LegalEvidenceUploadError("LEGAL_EVIDENCE_PROVIDER_ABORT_UNPROVEN") from abort_error
            raise

        committed_at = datetime.now(timezone.utc)
        source_reference = admission.ingestion_reference
        source_fingerprint = admission.fingerprint
        try:
            with self._client.start_session() as session:
                _start_transaction(session)
                result = two_plane.commit(
                    reservation=prepared.reservation, intent=intent, object_evidence=object_evidence,
                    observed_content_length=content_length, observed_content_fingerprint=digest,
                    source_evidence_reference=source_reference, source_evidence_fingerprint=source_fingerprint,
                    committed_at=committed_at, session=session,
                )
                session.commit_transaction()
            if not hmac.compare_digest(result.content.content_fingerprint, digest):
                raise LegalEvidenceUploadError("LEGAL_EVIDENCE_COMMIT_CORRELATION_INVALID")
            return LegalEvidenceUploadResult(
                ingestion_reference=admission.ingestion_reference, document_id=document.document_id,
                case_matter_id=document.case_matter_id, state="COMMITTED",
                content_reference=result.content.content_reference,
                content_fingerprint=digest, content_length=content_length,
            )
        except Exception as commit_error:
            uncertainty = open_legal_evidence_commit_uncertainty(
                reservation=prepared.reservation, intent=intent, object_evidence=object_evidence,
                observed_content_length=content_length, observed_content_fingerprint=digest,
                source_evidence_reference=source_reference, source_evidence_fingerprint=source_fingerprint,
                detected_at=committed_at,
            )
            try:
                with self._client.start_session() as session:
                    _start_transaction(session)
                    persisted = uncertainty_registry.create_or_replay(uncertainty, session=session)
                    session.commit_transaction()
            except Exception as uncertainty_error:
                raise LegalEvidenceUploadError("LEGAL_EVIDENCE_COMMIT_OUTCOME_UNPROVEN") from uncertainty_error
            return LegalEvidenceUploadResult(
                ingestion_reference=admission.ingestion_reference, document_id=document.document_id,
                case_matter_id=document.case_matter_id, state="RECONCILIATION_REQUIRED",
                content_reference=None, content_fingerprint=digest, content_length=content_length,
                uncertainty_id=persisted.uncertainty_id,
            )


__all__ = ["MAX_UPLOAD_BYTES", "VERSION", "LegalEvidenceUploadError", "LegalEvidenceUploadOrchestrator", "LegalEvidenceUploadResult"]

# ARTIFACT: legal_evidence_upload_orchestrator.py
# VERSION: v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-ORCHESTRATOR
# AUTHORITY BOUNDARY: authenticated upload ordering only; subordinate authorities retain truth
# TENANT POSTURE: server-authorized tenant plus current ProcessDocument exclusively bind scope
# FAIL-CLOSED POSTURE: malformed, unavailable, divergent, provider or persistence outcomes reject
# PROVIDER POSTURE: provider completion alone never becomes canonical content truth
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
