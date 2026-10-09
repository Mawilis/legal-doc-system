"""WILSY OS Legal Evidence three-phase ingestion orchestration.

TITLE: Legal Evidence Ingestion Orchestration Service
VERSION: v1.0.2-L10A2R-C4D5D8-INGESTION-ORCHESTRATION-SERVICE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    SERVER-ISSUED INGESTION ADMISSION
    -> CALLER-OWNED MONGO PREPARE
       [CAPACITY RESERVATION + DURABLE C4D5C WRITE INTENT]
    -> CALLER COMMITS
    -> FRESH CALLER-OWNED POST-COMMIT READ
    -> IMMUTABLE DURABLE VERIFICATION EVIDENCE
    -> PROVIDER BEGIN OUTSIDE MONGO
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_ingestion_orchestration_service.py
COLLABORATION / OWNERSHIP:
    This service owns Legal Evidence ingestion call ordering only. C4D5D7 owns
    server-issued admission evidence; P5C-B owns capacity admission; C4D5C owns
    durable original write-intent evidence; the binary storage port owns the
    provider-neutral provider boundary; callers own Mongo transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.2-L10A2R-C4D5D8 repairs institutional public-API documentation and
    removes unsupported external-compliance alignment wording without changing
    runtime semantics. v1.0.1 hardened durable-verification capability binding;
    v1.0.0 established the three-phase ingestion boundary.
COMPLIANCE:
    Security and privacy engineering posture only. This artifact implements
    tenant-boundary, integrity and minimization controls but does not itself
    establish legal compliance, SOC certification or ISO certification/alignment.
SECURITY / PRIVACY POSTURE:
    No provider credential, secret, binary payload or caller-supplied ingestion
    identity is accepted. Durable/provider coordinates remain delegated to
    their certified owners.
TENANT BOUNDARY:
    Admission tenant/document/matter/ingestion coordinates are preserved
    exactly through reservation, C4D5C registration and provider begin.
AUTHORITY BOUNDARY:
    Call ordering and exact evidence correlation only. No content commit,
    lifecycle, retention, legal-hold, orphan, abort or deletion authority.
FINANCIAL AUTHORITY BOUNDARY:
    No billing, payment, settlement or financial execution authority.
    Kennel EOS remains exclusive financial execution authority.
TRANSACTION BOUNDARY:
    prepare() and verify_durable() require caller-owned active Mongo
    transactions but never start, commit, abort or retry them. begin_provider()
    accepts no Mongo session and performs no Mongo access. Provider I/O is
    therefore never represented as transactionally atomic with Mongo.
FAIL-CLOSED DECLARATION:
    Wrong evidence types, inactive transactions, scope/fingerprint divergence,
    non-active reservations, capacity-coordinate divergence, corrupt durable
    reads and provider-session divergence reject.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hmac
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
)
from tools.eos.legal_operations.domain.legal_evidence_ingestion_admission import (
    LegalEvidenceIngestionAdmission,
)
from tools.eos.legal_operations.registry.legal_evidence_binary_write_intent_registry import (
    LegalEvidenceBinaryWriteIntentRecord,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryStoragePort,
    LegalEvidenceBinaryWriteIntent,
    LegalEvidenceBinaryWriteSession,
    validate_write_session_for_intent,
)
from tools.eos.legal_operations.service.legal_evidence_capacity_reservation_service import (
    LegalEvidenceCapacityReservationCommand,
    LegalEvidenceCapacityReservationService,
)
from tools.eos.saas.billing.legal_evidence_capacity_tenant_profile_resolver import (
    LegalEvidenceCapacityTenantProfile,
)


VERSION: Final[str] = (
    "v1.0.2-L10A2R-C4D5D8-INGESTION-ORCHESTRATION-SERVICE"
)


class LegalEvidenceIngestionOrchestrationError(RuntimeError):
    """Base fail-closed C4D5D8 orchestration error.

    Authority: represents orchestration-contract failure only and grants no
    ingestion, provider, lifecycle, retention, deletion or financial authority.
    Tenant scope: callers receive no cross-tenant existence information.
    Mutation/idempotency: the exception performs no mutation and creates no
    replay authority. Transaction ownership remains with the caller.
    Fail-closed: malformed, divergent or unauthorized orchestration state raises
    rather than being coerced or inferred. Financial execution remains Kennel
    EOS exclusive.
    """


class LegalEvidenceIngestionTransactionRequiredError(
    LegalEvidenceIngestionOrchestrationError
):
    """Reject missing or inactive caller-owned Mongo transaction state.

    Authority: transaction precondition error only; it never starts, commits,
    aborts or retries a transaction. Tenant scope is unchanged because no
    persistence operation is permitted before this condition succeeds.
    Mutation/idempotency: no mutation or replay decision is performed here.
    Fail-closed: missing or inactive transaction state rejects immediately.
    No billing, payment, settlement or financial execution authority exists.
    """


def _active_transaction(
    session: Any,
) -> Any:
    if (
        session is None
        or not bool(
            getattr(
                session,
                "in_transaction",
                False,
            )
        )
    ):
        raise LegalEvidenceIngestionTransactionRequiredError(
            "L10A2R_C4D5D8_TRANSACTION_REQUIRED"
        )

    return session


def _exact_sha(
    left: str,
    right: str,
) -> bool:
    return (
        isinstance(left, str)
        and isinstance(right, str)
        and hmac.compare_digest(
            left,
            right,
        )
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidencePreparedIngestion:
    """Immutable in-memory result of one transaction-bound prepare phase.

    Authority: correlates admission, ACTIVE capacity reservation and C4D5C
    write-intent evidence only; it is not commit or provider-success proof.
    Tenant scope: all tenant/document/matter/ingestion coordinates must agree.
    Mutation/idempotency: construction performs no persistence; durable replay
    semantics remain owned by the reservation service and C4D5C registry.
    Transaction ownership: the caller owns the prepare transaction and must
    commit it before a fresh verify_durable() read. Fail-closed scope divergence
    rejects. No content-commit, retention, deletion or financial authority.
    """

    admission: LegalEvidenceIngestionAdmission
    reservation: LegalEvidenceCapacityReservation
    write_intent_record: LegalEvidenceBinaryWriteIntentRecord

    def __post_init__(
        self,
    ) -> None:
        if type(self.admission) is not LegalEvidenceIngestionAdmission:
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_ADMISSION_REQUIRED"
            )

        if type(self.reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_RESERVATION_REQUIRED"
            )

        if (
            type(self.write_intent_record)
            is not LegalEvidenceBinaryWriteIntentRecord
        ):
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_WRITE_INTENT_RECORD_REQUIRED"
            )

        admission = self.admission
        reservation = self.reservation
        intent = self.write_intent_record.intent

        if (
            reservation.status
            is not LegalEvidenceCapacityReservationStatus.ACTIVE
            or reservation.tenant_id != admission.tenant_id
            or reservation.document_id != admission.document_id
            or reservation.ingestion_intent_id
            != admission.ingestion_reference
            or reservation.reserved_storage_bytes
            != admission.declared_content_length
            or reservation.reserved_ingress_bytes
            != admission.declared_content_length
            or reservation.reserved_document_versions != 1
            or intent.tenant_id != admission.tenant_id
            or intent.case_matter_id != admission.case_matter_id
            or intent.document_id != admission.document_id
            or intent.ingestion_reference
            != admission.ingestion_reference
            or intent.media_type != admission.media_type
            or intent.original_filename
            != admission.original_filename
            or intent.admitted_max_content_length
            != admission.declared_content_length
        ):
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_PREPARED_SCOPE_MISMATCH"
            )


@dataclass(
    frozen=True,
    slots=True,
    init=False,
)
class LegalEvidenceDurableIngestionVerification:
    """Immutable service-issued result of an exact post-commit C4D5C re-read.

    Authority: proves only that this service instance re-read the exact durable
    C4D5C record correlated to prepared evidence; it grants no provider success,
    content commit, orphan, retention, abort or deletion authority.
    Tenant scope is inherited from the exact C4D5D7/C4D5C coordinates.
    Mutation/idempotency: it creates no persisted truth and has no replay
    authority. Transaction ownership remains with the caller of verify_durable().
    Public construction and cross-service reuse fail closed. No financial
    execution authority exists outside Kennel EOS.
    """

    admission_fingerprint: str
    reservation_fingerprint: str
    write_intent_record: LegalEvidenceBinaryWriteIntentRecord
    _issuer_capability: object

    def __init__(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        raise LegalEvidenceIngestionOrchestrationError(
            "L10A2R_C4D5D8_DURABLE_VERIFICATION_FACTORY_REQUIRED"
        )


class LegalEvidenceIngestionOrchestrationService:
    """Order certified Legal Evidence ingestion capabilities without new authority.

    Authority: composition/correlation only; subordinate certified components
    retain admission, capacity, persistence and provider contracts.
    Tenant scope: exact tenant/document/matter/ingestion agreement is mandatory.
    Mutation/idempotency: prepare delegates durable replay to existing owners;
    verify_durable is read-only; begin_provider performs provider begin only.
    Transaction ownership: caller owns all Mongo lifecycle and the service never
    starts, commits, aborts or retries transactions. Divergence fails closed.
    Billing, payment, settlement and financial execution are explicitly absent.
    """

    __slots__ = (
        "_capacity_service",
        "_write_intent_registry",
        "_storage",
        "_verification_capability",
    )

    def __init__(
        self,
        *,
        capacity_service: LegalEvidenceCapacityReservationService,
        write_intent_registry: Any,
        storage: LegalEvidenceBinaryStoragePort,
    ) -> None:
        if (
            capacity_service is None
            or write_intent_registry is None
            or storage is None
        ):
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_DEPENDENCIES_REQUIRED"
            )

        self._capacity_service = capacity_service
        self._write_intent_registry = write_intent_registry
        self._storage = storage
        self._verification_capability = object()

    def prepare(
        self,
        *,
        admission: LegalEvidenceIngestionAdmission,
        reservation_id: str,
        idempotency_key: str,
        tenant_profile: LegalEvidenceCapacityTenantProfile,
        reserved_at: datetime,
        expires_at: datetime,
        session: Any,
    ) -> LegalEvidencePreparedIngestion:
        """Prepare reservation and C4D5C evidence in one caller transaction.

        Authority: capacity/write-intent orchestration only; no provider I/O or
        content commit occurs. Tenant scope derives exclusively from the supplied
        server-issued admission. Mutation delegates to P5C-B and C4D5C, whose
        exact replay semantics remain authoritative. The caller owns the already
        active transaction and decides commit/abort/retry. Invalid type, scope or
        downstream evidence fails closed. No financial authority is acquired.
        """

        tx = _active_transaction(
            session
        )

        if type(admission) is not LegalEvidenceIngestionAdmission:
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_ADMISSION_REQUIRED"
            )

        admission.verify()

        command = LegalEvidenceCapacityReservationCommand(
            tenant_id=admission.tenant_id,
            document_id=admission.document_id,
            reservation_id=reservation_id,
            ingestion_intent_id=(
                admission.ingestion_reference
            ),
            idempotency_key=idempotency_key,
            reserved_storage_bytes=(
                admission.declared_content_length
            ),
            reserved_ingress_bytes=(
                admission.declared_content_length
            ),
            reserved_document_versions=1,
            reserved_at=reserved_at,
            expires_at=expires_at,
        )

        reservation = self._capacity_service.reserve(
            command=command,
            tenant_profile=tenant_profile,
            session=tx,
        )

        if type(reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_RESERVATION_REQUIRED"
            )

        intent = LegalEvidenceBinaryWriteIntent(
            tenant_id=admission.tenant_id,
            case_matter_id=admission.case_matter_id,
            document_id=admission.document_id,
            ingestion_reference=(
                admission.ingestion_reference
            ),
            media_type=admission.media_type,
            original_filename=(
                admission.original_filename
            ),
            admitted_max_content_length=(
                admission.declared_content_length
            ),
        )

        record = (
            self._write_intent_registry.create_or_replay(
                intent,
                registered_at=reserved_at,
                session=tx,
            )
        )

        return LegalEvidencePreparedIngestion(
            admission=admission,
            reservation=reservation,
            write_intent_record=record,
        )

    def verify_durable(
        self,
        *,
        prepared: LegalEvidencePreparedIngestion,
        session: Any,
    ) -> LegalEvidenceDurableIngestionVerification:
        """Verify exact durable C4D5C evidence in a fresh caller transaction.

        Authority: post-commit durable correlation only; no provider execution
        or new persisted truth. Tenant scope is the prepared admission tenant and
        ingestion reference. Mutation/idempotency: read-only and creates no
        durable replay state. Caller owns the active transaction and its
        commit/abort lifecycle. Missing, corrupt or divergent durable evidence
        fails closed. No content, deletion or financial authority is granted.
        """

        tx = _active_transaction(
            session
        )

        if type(prepared) is not LegalEvidencePreparedIngestion:
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_PREPARED_REQUIRED"
            )

        durable = (
            self._write_intent_registry
            .get_by_ingestion_reference(
                tenant_id=(
                    prepared.admission.tenant_id
                ),
                ingestion_reference=(
                    prepared.admission.ingestion_reference
                ),
                session=tx,
            )
        )

        if (
            type(durable)
            is not LegalEvidenceBinaryWriteIntentRecord
        ):
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_DURABLE_RECORD_REQUIRED"
            )

        expected = prepared.write_intent_record

        if (
            durable.intent != expected.intent
            or durable.registered_at
            != expected.registered_at
            or not _exact_sha(
                durable.record_fingerprint,
                expected.record_fingerprint,
            )
        ):
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_DURABLE_RECORD_MISMATCH"
            )

        verified = object.__new__(
            LegalEvidenceDurableIngestionVerification
        )

        object.__setattr__(
            verified,
            "admission_fingerprint",
            prepared.admission.fingerprint,
        )
        object.__setattr__(
            verified,
            "reservation_fingerprint",
            prepared.reservation.fingerprint,
        )
        object.__setattr__(
            verified,
            "write_intent_record",
            durable,
        )
        object.__setattr__(
            verified,
            "_issuer_capability",
            self._verification_capability,
        )

        return verified

    def begin_provider(
        self,
        *,
        verified: LegalEvidenceDurableIngestionVerification,
    ) -> LegalEvidenceBinaryWriteSession:
        """Begin provider execution from same-service durable verification only.

        Authority: delegates exactly one provider ``begin`` call and creates no
        content-commit, lifecycle, orphan, abort or deletion authority.
        Tenant scope is sealed by the verified C4D5C write intent.
        Mutation/idempotency: provider behavior remains owned by the injected
        storage port; this method creates no Mongo state or replay authority.
        It accepts no Mongo session and owns no transaction lifecycle.
        Fabricated/cross-service verification or divergent provider session
        fails closed. No billing, settlement or financial execution authority.
        """

        if (
            type(verified)
            is not LegalEvidenceDurableIngestionVerification
            or verified._issuer_capability
            is not self._verification_capability
        ):
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_DURABLE_VERIFICATION_REQUIRED"
            )

        session = self._storage.begin(
            verified.write_intent_record.intent
        )

        if type(session) is not LegalEvidenceBinaryWriteSession:
            raise LegalEvidenceIngestionOrchestrationError(
                "L10A2R_C4D5D8_WRITE_SESSION_REQUIRED"
            )

        validate_write_session_for_intent(
            intent=(
                verified.write_intent_record.intent
            ),
            session=session,
        )

        return session


__all__ = [
    "VERSION",
    "LegalEvidenceDurableIngestionVerification",
    "LegalEvidenceIngestionOrchestrationError",
    "LegalEvidenceIngestionOrchestrationService",
    "LegalEvidenceIngestionTransactionRequiredError",
    "LegalEvidencePreparedIngestion",
]


# ARTIFACT: legal_evidence_ingestion_orchestration_service.py
# VERSION: v1.0.2-L10A2R-C4D5D8-INGESTION-ORCHESTRATION-SERVICE
# AUTHORITY BOUNDARY: three-phase Legal Evidence ingestion call ordering only
# TENANT POSTURE: admission/reservation/C4D5C/provider intent scope must match exactly
# TRANSACTION POSTURE: caller owns Mongo lifecycle; provider begin accepts no Mongo session
# PROVIDER POSTURE: provider begin only after exact fresh durable C4D5C verification
# FAIL-CLOSED POSTURE: transaction, type, scope, fingerprint or provider-session divergence rejects
# CONTENT POSTURE: no content commit or canonical content identity authority
# ORPHAN POSTURE: no orphan proof
# ABORT POSTURE: no provider-abort authority
# DELETION POSTURE: no deletion authorization or execution authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
