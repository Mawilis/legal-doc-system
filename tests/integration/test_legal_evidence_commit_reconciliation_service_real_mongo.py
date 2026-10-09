"""Real-Mongo certificate for Legal Evidence commit reconciliation.

TITLE: Legal Evidence Commit Reconciliation Service Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4C-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Prove C4C against one disposable UUID-isolated database on the loopback
    wilsyVendorCertRS replica set.

SCENARIOS:
    1. Unknown caller result where C3 already committed:
       -> COMMITTED_CONFIRMED
       -> no second metadata/usage/fence mutation.

    2. Provider success with durable uncertainty, missing metadata and ACTIVE
       reservation:
       -> exact C3 recovery
       -> COMMIT_RECOVERED
       -> atomic metadata/usage/reservation/fence commit.

    3. Missing metadata with reservation at expiry:
       -> P5D expiry only
       -> PROVIDER_OBJECT_UNRESOLVED
       -> no metadata/usage/provider deletion.

DATABASE SAFETY:
    Only loopback wilsyVendorCertRS on port 27027 is accepted. Every run uses a
    UUID-isolated disposable database. Canonical database "wilsy" is forbidden.

PROVIDER:
    No provider call is performed. C4 immutable provider-object evidence is the
    only provider-shaped input.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
)
from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import (
    LegalEvidenceCommitUncertainty,
    open_legal_evidence_commit_uncertainty,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
    COLLECTION as FENCE_COLLECTION,
    LegalEvidenceCapacityAdmissionFenceRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
    COLLECTION as RESERVATION_COLLECTION,
    LegalEvidenceCapacityReservationRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_commit_uncertainty_registry import (
    COLLECTION as UNCERTAINTY_COLLECTION,
    LegalEvidenceCommitUncertaintyRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_object_metadata_registry import (
    COLLECTION as METADATA_COLLECTION,
    LegalEvidenceObjectMetadataRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_usage_observation_registry import (
    COLLECTION as USAGE_COLLECTION,
    LegalEvidenceUsageObservationRegistry,
    ensure_indexes as ensure_usage_indexes,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)
from tools.eos.legal_operations.service.legal_evidence_capacity_reservation_lifecycle_service import (
    LegalEvidenceCapacityReservationLifecycleService,
)
from tools.eos.legal_operations.service.legal_evidence_commit_reconciliation_service import (
    LegalEvidenceCommitReconciliationOutcome,
    LegalEvidenceCommitReconciliationService,
)
from tools.eos.legal_operations.service.legal_evidence_two_plane_commit_service import (
    LegalEvidenceTwoPlaneCommitService,
)


URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_l10a2r_c4c_cert_"

AT = datetime(
    2026,
    9,
    30,
    15,
    20,
    0,
    123456,
    tzinfo=timezone.utc,
)

CONTENT = b"c4c-real-mongo-content"
CONTENT_LENGTH = len(CONTENT)

CONTENT_FP = hashlib.sha3_512(
    CONTENT
).hexdigest()

SOURCE_FP = hashlib.sha3_512(
    b"c4c-real-mongo-source"
).hexdigest()


class MongoContext:
    """Own one isolated C4C certification database and exact registries."""

    def __init__(
        self,
        client: MongoClient[Any],
        database_name: str,
    ) -> None:
        self.client = client
        self.database_name = database_name

        self.database = client.get_database(
            database_name,
            read_concern=ReadConcern(
                "majority"
            ),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )

        self.fences = self.database[
            FENCE_COLLECTION
        ]
        self.reservations = self.database[
            RESERVATION_COLLECTION
        ]
        self.usage = self.database[
            USAGE_COLLECTION
        ]
        self.metadata = self.database[
            METADATA_COLLECTION
        ]
        self.uncertainties = self.database[
            UNCERTAINTY_COLLECTION
        ]

        self.fence_registry = (
            LegalEvidenceCapacityAdmissionFenceRegistry(
                self.fences
            )
        )
        self.reservation_registry = (
            LegalEvidenceCapacityReservationRegistry(
                self.reservations
            )
        )
        self.usage_registry = (
            LegalEvidenceUsageObservationRegistry(
                self.usage
            )
        )
        self.metadata_registry = (
            LegalEvidenceObjectMetadataRegistry(
                self.metadata
            )
        )
        self.uncertainty_registry = (
            LegalEvidenceCommitUncertaintyRegistry(
                self.uncertainties
            )
        )

        self.fence_registry.ensure_indexes()
        self.reservation_registry.ensure_indexes()
        ensure_usage_indexes(
            self.usage
        )
        self.metadata_registry.ensure_indexes()
        self.uncertainty_registry.ensure_indexes()


def _fresh_context() -> MongoContext:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=10000,
        retryWrites=True,
        tz_aware=True,
    )

    try:
        hello = client.admin.command(
            "hello"
        )
        address = client.address

        if (
            address is None
            or address[0]
            not in {
                "127.0.0.1",
                "localhost",
            }
            or address[1] != 27027
        ):
            raise RuntimeError(
                "L10A2R_C4C_CERT_MONGO_NOT_LOOPBACK_27027"
            )

        if hello.get(
            "setName"
        ) != REPLICA_SET:
            raise RuntimeError(
                "L10A2R_C4C_CERT_REPLICA_SET_MISMATCH"
            )

        if hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is not True:
            raise RuntimeError(
                "L10A2R_C4C_CERT_WRITABLE_PRIMARY_REQUIRED"
            )

        if hello.get(
            "logicalSessionTimeoutMinutes"
        ) is None:
            raise RuntimeError(
                "L10A2R_C4C_CERT_SESSIONS_REQUIRED"
            )

        database_name = (
            DATABASE_PREFIX
            + uuid.uuid4().hex
        )

        if (
            database_name == "wilsy"
            or not database_name.startswith(
                DATABASE_PREFIX
            )
            or len(database_name) > 63
        ):
            raise RuntimeError(
                "L10A2R_C4C_CERT_DATABASE_GUARD_FAILED"
            )

        return MongoContext(
            client,
            database_name,
        )

    except BaseException:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_context() -> Iterator[MongoContext]:
    """Yield then destroy only the UUID-isolated C4C database."""
    context = _fresh_context()

    try:
        yield context
    finally:
        context.client.drop_database(
            context.database_name
        )

        assert (
            context.database_name
            not in context.client.list_database_names()
        )

        context.client.close()


def _start_transaction(
    session: Any,
) -> None:
    session.start_transaction(
        read_concern=ReadConcern(
            "snapshot"
        ),
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
    )


def _coordinates(
    label: str,
) -> tuple[
    str,
    str,
    str,
    str,
    str,
]:
    return (
        f"tenant-c4c-real-{label}",
        f"matter-c4c-real-{label}",
        f"document-c4c-real-{label}",
        f"ingestion-c4c-real-{label}",
        f"reservation-c4c-real-{label}",
    )


def _intent(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    ingestion_reference: str,
) -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        document_id=document_id,
        ingestion_reference=ingestion_reference,
        media_type="application/pdf",
        original_filename="evidence.pdf",
        admitted_max_content_length=CONTENT_LENGTH,
    )


def _object(
    intent: LegalEvidenceBinaryWriteIntent,
    *,
    label: str,
) -> LegalEvidenceBinaryObjectEvidence:
    return LegalEvidenceBinaryObjectEvidence(
        provider_name="aws-s3",
        storage_reference=(
            f"legal-evidence/v1/c4c-real-{label}"
        ),
        object_version_reference=(
            f"version-c4c-real-{label}"
        ),
        provider_integrity_reference=(
            f'"etag-c4c-real-{label}"'
        ),
        write_intent_fingerprint=(
            intent.fingerprint
        ),
        content_length=CONTENT_LENGTH,
        content_fingerprint=CONTENT_FP,
    )


def _reservation(
    *,
    tenant_id: str,
    document_id: str,
    ingestion_reference: str,
    reservation_id: str,
    expires_at: datetime,
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id=ingestion_reference,
        remaining_capacity_fingerprint="a" * 128,
        reserved_storage_bytes=CONTENT_LENGTH,
        reserved_ingress_bytes=CONTENT_LENGTH,
        reserved_document_versions=1,
        reserved_at=AT - timedelta(
            minutes=5
        ),
        expires_at=expires_at,
    )


def _uncertainty(
    *,
    reservation: LegalEvidenceCapacityReservation,
    intent: LegalEvidenceBinaryWriteIntent,
    object_evidence: LegalEvidenceBinaryObjectEvidence,
) -> LegalEvidenceCommitUncertainty:
    return open_legal_evidence_commit_uncertainty(
        reservation=reservation,
        intent=intent,
        object_evidence=object_evidence,
        observed_content_length=CONTENT_LENGTH,
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference=(
            "source-c4c-real"
        ),
        source_evidence_fingerprint=(
            SOURCE_FP
        ),
        detected_at=AT,
    )


def _seed(
    context: MongoContext,
    *,
    reservation: LegalEvidenceCapacityReservation,
    uncertainty: LegalEvidenceCommitUncertainty,
    label: str,
) -> None:
    with context.client.start_session() as session:
        _start_transaction(
            session
        )

        context.fence_registry.advance(
            tenant_id=reservation.tenant_id,
            expected_revision=None,
            coordination_reference=(
                f"seed-c4c-{label}"
            ),
            advanced_at=(
                reservation.reserved_at
                - timedelta(minutes=1)
            ),
            session=session,
        )

        context.reservation_registry.create_or_replay(
            reservation,
            idempotency_key=(
                f"seed-c4c-idempotency-{label}"
            ),
            session=session,
        )

        context.uncertainty_registry.create_or_replay(
            uncertainty,
            session=session,
        )

        session.commit_transaction()


def _lifecycle(
    context: MongoContext,
) -> LegalEvidenceCapacityReservationLifecycleService:
    return LegalEvidenceCapacityReservationLifecycleService(
        fence_registry=context.fence_registry,
        reservation_registry=context.reservation_registry,
        usage_registry=context.usage_registry,
    )


def _c3(
    context: MongoContext,
    lifecycle: LegalEvidenceCapacityReservationLifecycleService,
) -> LegalEvidenceTwoPlaneCommitService:
    return LegalEvidenceTwoPlaneCommitService(
        metadata_registry=context.metadata_registry,
        lifecycle_service=lifecycle,
    )


def _c4c(
    context: MongoContext,
) -> LegalEvidenceCommitReconciliationService:
    lifecycle = _lifecycle(
        context
    )

    c3 = _c3(
        context,
        lifecycle,
    )

    return LegalEvidenceCommitReconciliationService(
        uncertainty_registry=(
            context.uncertainty_registry
        ),
        metadata_registry=(
            context.metadata_registry
        ),
        reservation_registry=(
            context.reservation_registry
        ),
        usage_registry=(
            context.usage_registry
        ),
        lifecycle_service=lifecycle,
        two_plane_commit_service=c3,
    )


def test_real_unknown_result_already_committed_is_confirmed_without_second_mutation(
    mongo_context: MongoContext,
) -> None:
    label = "confirmed"

    (
        tenant,
        matter,
        document,
        ingestion,
        reservation_id,
    ) = _coordinates(
        label
    )

    intent = _intent(
        tenant_id=tenant,
        case_matter_id=matter,
        document_id=document,
        ingestion_reference=ingestion,
    )

    object_evidence = _object(
        intent,
        label=label,
    )

    reservation = _reservation(
        tenant_id=tenant,
        document_id=document,
        ingestion_reference=ingestion,
        reservation_id=reservation_id,
        expires_at=AT + timedelta(
            minutes=30
        ),
    )

    uncertainty = _uncertainty(
        reservation=reservation,
        intent=intent,
        object_evidence=object_evidence,
    )

    _seed(
        mongo_context,
        reservation=reservation,
        uncertainty=uncertainty,
        label=label,
    )

    lifecycle = _lifecycle(
        mongo_context
    )
    c3 = _c3(
        mongo_context,
        lifecycle,
    )

    committed_at = AT + timedelta(
        minutes=1
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(
            session
        )

        committed = c3.commit(
            reservation=reservation,
            intent=intent,
            object_evidence=object_evidence,
            observed_content_length=CONTENT_LENGTH,
            observed_content_fingerprint=CONTENT_FP,
            source_evidence_reference=(
                "source-c4c-real"
            ),
            source_evidence_fingerprint=SOURCE_FP,
            committed_at=committed_at,
            session=session,
        )

        session.commit_transaction()

    assert committed.reservation.status.value == (
        "CONSUMED"
    )

    before_metadata = (
        mongo_context.metadata.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
    )
    before_usage = (
        mongo_context.usage.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
    )
    before_fence = mongo_context.fences.find_one(
        {
            "tenant_id":
                tenant,
        }
    )

    assert before_metadata == 1
    assert before_usage == 1
    assert before_fence is not None
    assert before_fence[
        "revision"
    ] == 2

    service = _c4c(
        mongo_context
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(
            session
        )

        result = service.reconcile(
            tenant_id=tenant,
            uncertainty_id=(
                uncertainty.uncertainty_id
            ),
            intent=intent,
            reconciled_at=(
                committed_at
                + timedelta(minutes=1)
            ),
            session=session,
        )

        session.commit_transaction()

    assert result.outcome is (
        LegalEvidenceCommitReconciliationOutcome
        .COMMITTED_CONFIRMED
    )
    assert result.available is False
    assert (
        result.authorized_availability
        is False
    )
    assert result.orphan_proven is False
    assert (
        result.provider_delete_authorized
        is False
    )

    assert (
        mongo_context.metadata.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
        == 1
    )

    assert (
        mongo_context.usage.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
        == 1
    )

    after_fence = mongo_context.fences.find_one(
        {
            "tenant_id":
                tenant,
        }
    )

    assert after_fence is not None
    assert after_fence[
        "revision"
    ] == 2


def test_real_missing_metadata_active_reservation_recovers_exact_c3_commit(
    mongo_context: MongoContext,
) -> None:
    label = "recover"

    (
        tenant,
        matter,
        document,
        ingestion,
        reservation_id,
    ) = _coordinates(
        label
    )

    intent = _intent(
        tenant_id=tenant,
        case_matter_id=matter,
        document_id=document,
        ingestion_reference=ingestion,
    )

    object_evidence = _object(
        intent,
        label=label,
    )

    reservation = _reservation(
        tenant_id=tenant,
        document_id=document,
        ingestion_reference=ingestion,
        reservation_id=reservation_id,
        expires_at=AT + timedelta(
            minutes=30
        ),
    )

    uncertainty = _uncertainty(
        reservation=reservation,
        intent=intent,
        object_evidence=object_evidence,
    )

    _seed(
        mongo_context,
        reservation=reservation,
        uncertainty=uncertainty,
        label=label,
    )

    assert (
        mongo_context.metadata.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
        == 0
    )

    assert (
        mongo_context.usage.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
        == 0
    )

    before_fence = mongo_context.fences.find_one(
        {
            "tenant_id":
                tenant,
        }
    )

    assert before_fence is not None
    assert before_fence[
        "revision"
    ] == 1

    service = _c4c(
        mongo_context
    )

    recovered_at = AT + timedelta(
        minutes=2
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(
            session
        )

        result = service.reconcile(
            tenant_id=tenant,
            uncertainty_id=(
                uncertainty.uncertainty_id
            ),
            intent=intent,
            reconciled_at=recovered_at,
            session=session,
        )

        session.commit_transaction()

    assert result.outcome is (
        LegalEvidenceCommitReconciliationOutcome
        .COMMIT_RECOVERED
    )
    assert result.reservation.status.value == (
        "CONSUMED"
    )
    assert result.content is not None
    assert result.metadata is not None
    assert result.available is False
    assert (
        result.authorized_availability
        is False
    )
    assert result.orphan_proven is False
    assert (
        result.provider_delete_authorized
        is False
    )

    assert (
        mongo_context.metadata.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
        == 1
    )

    assert (
        mongo_context.usage.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
        == 1
    )

    durable_reservation = (
        mongo_context.reservations.find_one(
            {
                "tenant_id":
                    tenant,
                "reservation_id":
                    reservation_id,
            }
        )
    )

    assert durable_reservation is not None
    assert durable_reservation[
        "status"
    ] == "CONSUMED"

    after_fence = mongo_context.fences.find_one(
        {
            "tenant_id":
                tenant,
        }
    )

    assert after_fence is not None
    assert after_fence[
        "revision"
    ] == 2


def test_real_expired_uncertainty_reconciles_reservation_without_commit_or_delete(
    mongo_context: MongoContext,
) -> None:
    label = "expired"

    (
        tenant,
        matter,
        document,
        ingestion,
        reservation_id,
    ) = _coordinates(
        label
    )

    intent = _intent(
        tenant_id=tenant,
        case_matter_id=matter,
        document_id=document,
        ingestion_reference=ingestion,
    )

    object_evidence = _object(
        intent,
        label=label,
    )

    expires_at = AT + timedelta(
        minutes=2
    )

    reservation = _reservation(
        tenant_id=tenant,
        document_id=document,
        ingestion_reference=ingestion,
        reservation_id=reservation_id,
        expires_at=expires_at,
    )

    uncertainty = _uncertainty(
        reservation=reservation,
        intent=intent,
        object_evidence=object_evidence,
    )

    _seed(
        mongo_context,
        reservation=reservation,
        uncertainty=uncertainty,
        label=label,
    )

    service = _c4c(
        mongo_context
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(
            session
        )

        result = service.reconcile(
            tenant_id=tenant,
            uncertainty_id=(
                uncertainty.uncertainty_id
            ),
            intent=intent,
            reconciled_at=expires_at,
            session=session,
        )

        session.commit_transaction()

    assert result.outcome is (
        LegalEvidenceCommitReconciliationOutcome
        .PROVIDER_OBJECT_UNRESOLVED
    )

    assert result.reservation.status.value == (
        "EXPIRED"
    )
    assert result.content is None
    assert result.metadata is None
    assert result.available is False
    assert (
        result.authorized_availability
        is False
    )
    assert result.orphan_proven is False
    assert (
        result.provider_delete_authorized
        is False
    )

    assert (
        mongo_context.metadata.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
        == 0
    )

    assert (
        mongo_context.usage.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
        == 0
    )

    durable_reservation = (
        mongo_context.reservations.find_one(
            {
                "tenant_id":
                    tenant,
                "reservation_id":
                    reservation_id,
            }
        )
    )

    assert durable_reservation is not None
    assert durable_reservation[
        "status"
    ] == "EXPIRED"

    fence = mongo_context.fences.find_one(
        {
            "tenant_id":
                tenant,
        }
    )

    assert fence is not None
    assert fence[
        "revision"
    ] == 2

    assert (
        mongo_context.uncertainties.count_documents(
            {
                "tenant_id":
                    tenant,
                "uncertainty_id":
                    uncertainty.uncertainty_id,
            }
        )
        == 1
    )


# ARTIFACT: test_legal_evidence_commit_reconciliation_service_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4C-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical commit-state reconciliation certificate only
# DATABASE POSTURE: UUID disposable DB on loopback wilsyVendorCertRS only
# CONFIRMATION POSTURE: committed truth is verified without second mutation
# RECOVERY POSTURE: ACTIVE/unexpired missing metadata invokes exact C3 recovery
# EXPIRY POSTURE: expired missing-metadata state remains provider unresolved
# UNCERTAINTY POSTURE: durable C4B evidence survives reconciliation
# PROVIDER POSTURE: no provider IO or deletion
# RETENTION POSTURE: no retention/legal-hold authority
# AVAILABILITY POSTURE: all results remain unavailable
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
