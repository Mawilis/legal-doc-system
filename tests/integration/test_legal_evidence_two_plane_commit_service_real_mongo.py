"""Real-Mongo certificate for Legal Evidence two-plane commit orchestration.

TITLE: Legal Evidence Two-Plane Commit Service Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C3-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Prove on one disposable Mongo replica-set database that C3 commits C2
    metadata plus P5D fence/usage/reservation state in one caller-owned
    transaction, replays exactly, and leaks nothing when that transaction
    aborts.

EPITOME:
    VERIFIED PROVIDER OBJECT EVIDENCE
    + WILSY STREAM IDENTITY
    + ACTIVE RESERVATION
    -> C2 METADATA
    -> P5D USAGE / CONSUMED RESERVATION
    -> ONE ATOMIC MONGO COMMIT

    ABORTED TRANSACTION
    -> NO METADATA
    -> NO USAGE
    -> ACTIVE RESERVATION
    -> OLD FENCE REVISION

DATABASE SAFETY:
    Only loopback wilsyVendorCertRS is accepted. Every run uses one UUID-isolated
    disposable database. Canonical database "wilsy" is forbidden.

PROVIDER:
    No provider call is performed here. LegalEvidenceBinaryObjectEvidence is
    already-certified immutable evidence supplied to C3.

AVAILABILITY:
    A committed C3 result remains unavailable and grants no availability
    authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import uuid
from typing import Any, Iterator, TypedDict

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
    COLLECTION as FENCE_COLLECTION,
    LegalEvidenceCapacityAdmissionFenceRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
    COLLECTION as RESERVATION_COLLECTION,
    LegalEvidenceCapacityReservationRegistry,
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
from tools.eos.legal_operations.service.legal_evidence_two_plane_commit_service import (
    LegalEvidenceTwoPlaneCommitService,
)


URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_l10a2r_c3_cert_"

AT = datetime(
    2026,
    9,
    30,
    12,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)

CONTENT_FP = hashlib.sha3_512(
    b"c3-real-stream-content"
).hexdigest()

SOURCE_FP = hashlib.sha3_512(
    b"c3-real-source-evidence"
).hexdigest()

CONTENT_LENGTH = 37


class CommitKwargs(TypedDict):
    """Exact strongly typed C3 commit arguments excluding Mongo session."""

    reservation: LegalEvidenceCapacityReservation
    intent: LegalEvidenceBinaryWriteIntent
    object_evidence: LegalEvidenceBinaryObjectEvidence
    observed_content_length: int
    observed_content_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    committed_at: datetime


class MongoContext:
    """Own one isolated C3 certification database."""

    def __init__(
        self,
        client: MongoClient[Any],
        database_name: str,
    ) -> None:
        self.client = client
        self.database_name = database_name
        self.database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
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

        self.fence_registry.ensure_indexes()
        self.reservation_registry.ensure_indexes()
        ensure_usage_indexes(
            self.usage
        )
        self.metadata_registry.ensure_indexes()


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
        ):
            raise RuntimeError(
                "L10A2R_C3_CERT_MONGO_NOT_LOOPBACK"
            )

        if hello.get("setName") != REPLICA_SET:
            raise RuntimeError(
                "L10A2R_C3_CERT_REPLICA_SET_MISMATCH"
            )

        if hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is not True:
            raise RuntimeError(
                "L10A2R_C3_CERT_WRITABLE_PRIMARY_REQUIRED"
            )

        if hello.get(
            "logicalSessionTimeoutMinutes"
        ) is None:
            raise RuntimeError(
                "L10A2R_C3_CERT_SESSIONS_REQUIRED"
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
                "L10A2R_C3_CERT_DATABASE_GUARD_FAILED"
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
    """Yield then destroy only the UUID-isolated C3 database."""
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
        f"tenant-c3-real-{label}",
        f"matter-c3-real-{label}",
        f"document-c3-real-{label}",
        f"ingestion-c3-real-{label}",
        f"reservation-c3-real-{label}",
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
            f"legal-evidence/v1/c3-real-{label}"
        ),
        object_version_reference=(
            f"version-c3-real-{label}"
        ),
        provider_integrity_reference=(
            f'"etag-c3-real-{label}"'
        ),
        write_intent_fingerprint=intent.fingerprint,
        content_length=CONTENT_LENGTH,
        content_fingerprint=CONTENT_FP,
    )


def _seed_reservation(
    context: MongoContext,
    *,
    tenant_id: str,
    document_id: str,
    ingestion_reference: str,
    reservation_id: str,
    label: str,
) -> LegalEvidenceCapacityReservation:
    reservation = LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id=ingestion_reference,
        remaining_capacity_fingerprint="a" * 128,
        reserved_storage_bytes=CONTENT_LENGTH,
        reserved_ingress_bytes=CONTENT_LENGTH,
        reserved_document_versions=1,
        reserved_at=AT - timedelta(minutes=2),
        expires_at=AT + timedelta(minutes=20),
    )

    with context.client.start_session() as session:
        _start_transaction(
            session
        )

        context.fence_registry.advance(
            tenant_id=tenant_id,
            expected_revision=None,
            coordination_reference=f"seed-{label}",
            advanced_at=AT - timedelta(minutes=3),
            session=session,
        )

        context.reservation_registry.create_or_replay(
            reservation,
            idempotency_key=f"seed-idempotency-{label}",
            session=session,
        )

        session.commit_transaction()

    return reservation


def _service(
    context: MongoContext,
) -> LegalEvidenceTwoPlaneCommitService:
    lifecycle = (
        LegalEvidenceCapacityReservationLifecycleService(
            fence_registry=context.fence_registry,
            reservation_registry=context.reservation_registry,
            usage_registry=context.usage_registry,
        )
    )

    return LegalEvidenceTwoPlaneCommitService(
        metadata_registry=context.metadata_registry,
        lifecycle_service=lifecycle,
    )


def _commit_kwargs(
    *,
    reservation: LegalEvidenceCapacityReservation,
    intent: LegalEvidenceBinaryWriteIntent,
    object_evidence: LegalEvidenceBinaryObjectEvidence,
) -> CommitKwargs:
    return {
        "reservation": reservation,
        "intent": intent,
        "object_evidence": object_evidence,
        "observed_content_length": CONTENT_LENGTH,
        "observed_content_fingerprint": CONTENT_FP,
        "source_evidence_reference": "source-c3-real",
        "source_evidence_fingerprint": SOURCE_FP,
        "committed_at": AT,
    }


def test_real_two_plane_commit_is_atomic_and_exactly_replays(
    mongo_context: MongoContext,
) -> None:
    label = "commit"
    (
        tenant,
        matter,
        document,
        ingestion,
        reservation_id,
    ) = _coordinates(label)

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
    reservation = _seed_reservation(
        mongo_context,
        tenant_id=tenant,
        document_id=document,
        ingestion_reference=ingestion,
        reservation_id=reservation_id,
        label=label,
    )

    service = _service(
        mongo_context
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(
            session
        )

        first = service.commit(
            **_commit_kwargs(
                reservation=reservation,
                intent=intent,
                object_evidence=object_evidence,
            ),
            session=session,
        )

        assert first.available is False
        assert first.authorized_availability is False

        session.commit_transaction()

    assert mongo_context.metadata.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    durable_reservation = (
        mongo_context.reservations.find_one(
            {
                "tenant_id": tenant,
                "reservation_id": reservation_id,
            }
        )
    )
    assert durable_reservation is not None
    assert durable_reservation["status"] == "CONSUMED"

    durable_fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert durable_fence is not None
    assert durable_fence["revision"] == 2

    durable_metadata = mongo_context.metadata.find_one(
        {
            "tenant_id": tenant,
            "content_reference": first.content.content_reference,
        }
    )
    assert durable_metadata is not None
    assert "content_bytes" not in durable_metadata

    with mongo_context.client.start_session() as session:
        _start_transaction(
            session
        )

        replay = service.commit(
            **_commit_kwargs(
                reservation=reservation,
                intent=intent,
                object_evidence=object_evidence,
            ),
            session=session,
        )

        session.commit_transaction()

    assert replay == first

    assert mongo_context.metadata.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    replay_fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert replay_fence is not None
    assert replay_fence["revision"] == 2


def test_real_abort_rolls_back_metadata_usage_reservation_and_fence(
    mongo_context: MongoContext,
) -> None:
    label = "abort"
    (
        tenant,
        matter,
        document,
        ingestion,
        reservation_id,
    ) = _coordinates(label)

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
    reservation = _seed_reservation(
        mongo_context,
        tenant_id=tenant,
        document_id=document,
        ingestion_reference=ingestion,
        reservation_id=reservation_id,
        label=label,
    )

    service = _service(
        mongo_context
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(
            session
        )

        result = service.commit(
            **_commit_kwargs(
                reservation=reservation,
                intent=intent,
                object_evidence=object_evidence,
            ),
            session=session,
        )

        assert result.reservation.status.value == "CONSUMED"
        assert mongo_context.metadata.count_documents(
            {
                "tenant_id": tenant,
            },
            session=session,
        ) == 1
        assert mongo_context.usage.count_documents(
            {
                "tenant_id": tenant,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert mongo_context.metadata.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    durable_reservation = (
        mongo_context.reservations.find_one(
            {
                "tenant_id": tenant,
                "reservation_id": reservation_id,
            }
        )
    )
    assert durable_reservation is not None
    assert durable_reservation["status"] == "ACTIVE"

    durable_fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert durable_fence is not None
    assert durable_fence["revision"] == 1


def test_real_object_mismatch_rejects_before_any_mongo_mutation(
    mongo_context: MongoContext,
) -> None:
    label = "mismatch"
    (
        tenant,
        matter,
        document,
        ingestion,
        reservation_id,
    ) = _coordinates(label)

    intent = _intent(
        tenant_id=tenant,
        case_matter_id=matter,
        document_id=document,
        ingestion_reference=ingestion,
    )

    object_evidence = LegalEvidenceBinaryObjectEvidence(
        provider_name="aws-s3",
        storage_reference="legal-evidence/v1/c3-real-mismatch",
        object_version_reference="version-c3-real-mismatch",
        provider_integrity_reference='"etag-c3-real-mismatch"',
        write_intent_fingerprint=intent.fingerprint,
        content_length=CONTENT_LENGTH,
        content_fingerprint="b" * 128,
    )

    reservation = _seed_reservation(
        mongo_context,
        tenant_id=tenant,
        document_id=document,
        ingestion_reference=ingestion,
        reservation_id=reservation_id,
        label=label,
    )

    service = _service(
        mongo_context
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(
            session
        )

        with pytest.raises(
            RuntimeError,
            match="L10A2R_C3_OBJECT_CONTENT_MISMATCH",
        ):
            service.commit(
                **_commit_kwargs(
                    reservation=reservation,
                    intent=intent,
                    object_evidence=object_evidence,
                ),
                session=session,
            )

        session.abort_transaction()

    assert mongo_context.metadata.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    durable_reservation = (
        mongo_context.reservations.find_one(
            {
                "tenant_id": tenant,
                "reservation_id": reservation_id,
            }
        )
    )
    assert durable_reservation is not None
    assert durable_reservation["status"] == "ACTIVE"

    durable_fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert durable_fence is not None
    assert durable_fence["revision"] == 1


# ARTIFACT: test_legal_evidence_two_plane_commit_service_real_mongo.py
# VERSION: v1.0.0-L10A2R-C3-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical C2 + P5D transaction-composition certificate
# DATABASE POSTURE: disposable UUID DB on loopback wilsyVendorCertRS only
# PROVIDER POSTURE: immutable provider evidence only; no provider execution
# ATOMICITY POSTURE: metadata/usage/reservation/fence commit or abort together
# REPLAY POSTURE: exact replay adds no metadata, usage or fence advance
# AVAILABILITY POSTURE: committed result remains unavailable
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
