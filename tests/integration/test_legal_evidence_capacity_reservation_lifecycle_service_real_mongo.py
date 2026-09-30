"""Real-Mongo certificate for semantic Legal Evidence reservation lifecycle.

TITLE: Legal Evidence Capacity Reservation Lifecycle Real-Mongo Certificate
VERSION: v1.0.0-L10A2Q-P5D-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Prove durable consume, release, expiry, exact replay, rollback atomicity and
    lifecycle-versus-admission serialization against a real Mongo replica set.

EPITOME:
    ACTIVE RESERVATION
    + P5C-A TENANT FENCE
    + CANONICAL CONTENT WHEN CONSUMING
    -> ONE DURABLE TERMINAL RESULT

    CONSUMED
    -> EXACT DURABLE P3 USAGE

    RELEASED / EXPIRED
    -> NO USAGE

    ABORTED TRANSACTION
    -> NO FENCE / USAGE / TERMINAL LEAKAGE

    LIFECYCLE RACE ADMISSION
    -> SAME TENANT FENCE
    -> AT MOST ONE COMMIT FROM ONE REVISION

DATABASE SAFETY:
    Only loopback wilsyVendorCertRS is accepted. One UUID-isolated disposable
    database is created and dropped. Canonical database "wilsy" is forbidden.

TRANSACTION:
    Every operation runs inside one caller-owned snapshot transaction.

AUTHORITY BOUNDARY:
    Reservation lifecycle and usage reconciliation only. No provider, IAM,
    retention, billing, payment, settlement or financial execution authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import threading
import uuid
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
)
from tools.eos.legal_operations.domain.legal_evidence_content import (
    register_legal_evidence_content,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
    COLLECTION as FENCE_COLLECTION,
    LegalEvidenceCapacityAdmissionFenceConflictError,
    LegalEvidenceCapacityAdmissionFencePersistenceError,
    LegalEvidenceCapacityAdmissionFenceRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
    COLLECTION as RESERVATION_COLLECTION,
    LegalEvidenceCapacityReservationConflictError,
    LegalEvidenceCapacityReservationPersistenceError,
    LegalEvidenceCapacityReservationRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_usage_observation_registry import (
    COLLECTION as USAGE_COLLECTION,
    LegalEvidenceUsageObservationRegistry,
    ensure_indexes as ensure_usage_indexes,
)
from tools.eos.legal_operations.service.legal_evidence_capacity_reservation_lifecycle_service import (
    LegalEvidenceCapacityReservationLifecycleError,
    LegalEvidenceCapacityReservationLifecycleService,
)
from tools.eos.legal_operations.service.legal_evidence_capacity_reservation_service import (
    LegalEvidenceCapacityAdmissionError,
    LegalEvidenceCapacityReservationCommand,
    LegalEvidenceCapacityReservationService,
)
from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityProfile,
)
from tools.eos.saas.billing.legal_evidence_capacity_tenant_profile_resolver import (
    LegalEvidenceCapacityTenantProfile,
)
from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
)


URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_l10a2q_p5d_cert_"

AT = datetime(
    2026,
    9,
    30,
    7,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)
SHA_A = "a" * 128
SHA_B = "b" * 128


class MongoContext:
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

        self.fences = self.database[FENCE_COLLECTION]
        self.reservations = self.database[RESERVATION_COLLECTION]
        self.usage = self.database[USAGE_COLLECTION]

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

        self.fence_registry.ensure_indexes()
        self.reservation_registry.ensure_indexes()
        ensure_usage_indexes(self.usage)


def _fresh_context() -> MongoContext:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=3000,
        retryWrites=True,
    )

    try:
        hello = client.admin.command("hello")
        address = client.address

        if (
            address is None
            or address[0] not in {
                "127.0.0.1",
                "localhost",
            }
        ):
            raise RuntimeError(
                "P5D_CERT_MONGO_NOT_LOOPBACK"
            )

        if hello.get("setName") != REPLICA_SET:
            raise RuntimeError(
                "P5D_CERT_REPLICA_SET_MISMATCH"
            )

        if hello.get("isWritablePrimary") is not True:
            raise RuntimeError(
                "P5D_CERT_WRITABLE_PRIMARY_REQUIRED"
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
                "P5D_CERT_DATABASE_GUARD_FAILED"
            )

        return MongoContext(
            client,
            database_name,
        )

    except BaseException:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_context() -> Any:
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
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
    )


def _seed(
    context: MongoContext,
    *,
    tenant_id: str,
    document_id: str,
    label: str,
    reserved_at: datetime = AT,
    expires_at: datetime | None = None,
) -> LegalEvidenceCapacityReservation:
    expiry = (
        expires_at
        if expires_at is not None
        else reserved_at + timedelta(minutes=20)
    )

    reservation = LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=f"reservation-{label}",
        ingestion_intent_id=f"ingestion-{label}",
        remaining_capacity_fingerprint=SHA_A,
        reserved_storage_bytes=1,
        reserved_ingress_bytes=1,
        reserved_document_versions=1,
        reserved_at=reserved_at,
        expires_at=expiry,
    )

    with context.client.start_session() as session:
        _start_transaction(session)

        context.fence_registry.advance(
            tenant_id=tenant_id,
            expected_revision=None,
            coordination_reference=f"seed-{label}",
            advanced_at=reserved_at - timedelta(minutes=1),
            session=session,
        )

        context.reservation_registry.create_or_replay(
            reservation,
            idempotency_key=f"seed-idempotency-{label}",
            session=session,
        )

        session.commit_transaction()

    return reservation


def _content(
    *,
    tenant_id: str,
    document_id: str,
    registered_at: datetime,
) -> Any:
    return register_legal_evidence_content(
        tenant_id=tenant_id,
        case_matter_id=f"matter-{tenant_id}",
        document_id=document_id,
        media_type="application/pdf",
        original_filename="evidence.pdf",
        content=b"x",
        source_evidence_reference=f"source-{tenant_id}",
        source_evidence_fingerprint=SHA_A,
        registered_at=registered_at,
    )


def _lifecycle_service(
    *,
    fence_registry: Any,
    reservation_registry: Any,
    usage_registry: Any,
) -> LegalEvidenceCapacityReservationLifecycleService:
    return LegalEvidenceCapacityReservationLifecycleService(
        fence_registry=fence_registry,
        reservation_registry=reservation_registry,
        usage_registry=usage_registry,
    )


def _admission_service(
    *,
    fence_registry: Any,
    reservation_registry: Any,
    usage_registry: Any,
) -> LegalEvidenceCapacityReservationService:
    return LegalEvidenceCapacityReservationService(
        fence_registry=fence_registry,
        reservation_registry=reservation_registry,
        usage_registry=usage_registry,
    )


def _profile(
    *,
    tenant_id: str,
    evaluated_at: datetime,
) -> LegalEvidenceCapacityTenantProfile:
    return LegalEvidenceCapacityTenantProfile(
        tenant_id=tenant_id,
        subscription_id=f"subscription-{tenant_id}",
        plan_id=f"plan-{tenant_id}",
        plan_catalogue_version=1,
        subscription_proof_hash=SHA_A,
        entitlement_id=f"entitlement-{tenant_id}",
        entitlement_revision=1,
        entitlement_fingerprint=SHA_B,
        product_id=TenantProductId.LEGAL_OPERATIONS,
        profile=LegalEvidenceCapacityProfile.STARTER,
        evaluated_at=evaluated_at,
    )


class BarrierFenceRegistry:
    """Force two transactions to observe one fence revision before CAS."""

    def __init__(
        self,
        inner: LegalEvidenceCapacityAdmissionFenceRegistry,
        barrier: threading.Barrier,
    ) -> None:
        self._inner = inner
        self._barrier = barrier

    def get(
        self,
        *,
        tenant_id: str,
        session: Any,
    ) -> Any:
        current = self._inner.get(
            tenant_id=tenant_id,
            session=session,
        )
        self._barrier.wait(timeout=5)
        return current

    def advance(
        self,
        *,
        tenant_id: str,
        expected_revision: int | None,
        coordination_reference: str,
        advanced_at: datetime,
        session: Any,
    ) -> Any:
        return self._inner.advance(
            tenant_id=tenant_id,
            expected_revision=expected_revision,
            coordination_reference=coordination_reference,
            advanced_at=advanced_at,
            session=session,
        )


def test_real_consume_commits_usage_and_terminal_state_atomically_and_replays(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5d-consume"
    document = "document-p5d-consume"
    reservation = _seed(
        mongo_context,
        tenant_id=tenant,
        document_id=document,
        label="consume",
    )

    content = _content(
        tenant_id=tenant,
        document_id=document,
        registered_at=AT + timedelta(minutes=1),
    )
    consumed_at = AT + timedelta(minutes=2)

    service = _lifecycle_service(
        fence_registry=mongo_context.fence_registry,
        reservation_registry=mongo_context.reservation_registry,
        usage_registry=mongo_context.usage_registry,
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        consumed = service.consume(
            tenant_id=tenant,
            reservation_id=reservation.reservation_id,
            content=content,
            consumed_at=consumed_at,
            session=session,
        )

        session.commit_transaction()

    assert consumed.status.value == "CONSUMED"

    row = mongo_context.reservations.find_one(
        {
            "tenant_id": tenant,
            "reservation_id": reservation.reservation_id,
        }
    )
    assert row is not None
    assert row["status"] == "CONSUMED"

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence is not None
    assert fence["revision"] == 2

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        replayed = service.consume(
            tenant_id=tenant,
            reservation_id=reservation.reservation_id,
            content=content,
            consumed_at=consumed_at,
            session=session,
        )

        session.commit_transaction()

    assert replayed.status.value == "CONSUMED"

    fence_after = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence_after is not None
    assert fence_after["revision"] == 2

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


@pytest.mark.parametrize(
    ("operation", "label"),
    [
        ("release", "release"),
        ("expire", "expire"),
    ],
)
def test_real_release_and_expire_commit_without_usage_and_exact_replay(
    mongo_context: MongoContext,
    operation: str,
    label: str,
) -> None:
    tenant = f"tenant-p5d-{label}"
    document = f"document-p5d-{label}"

    reservation = _seed(
        mongo_context,
        tenant_id=tenant,
        document_id=document,
        label=label,
    )

    service = _lifecycle_service(
        fence_registry=mongo_context.fence_registry,
        reservation_registry=mongo_context.reservation_registry,
        usage_registry=mongo_context.usage_registry,
    )

    observed_at = (
        AT + timedelta(minutes=2)
        if operation == "release"
        else reservation.expires_at
    )

    kwargs = {
        (
            "released_at"
            if operation == "release"
            else "expired_at"
        ): observed_at,
    }

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        result = getattr(
            service,
            operation,
        )(
            tenant_id=tenant,
            reservation_id=reservation.reservation_id,
            **kwargs,
            session=session,
        )

        session.commit_transaction()

    expected = (
        "RELEASED"
        if operation == "release"
        else "EXPIRED"
    )
    assert result.status.value == expected

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence is not None
    assert fence["revision"] == 2

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        replay = getattr(
            service,
            operation,
        )(
            tenant_id=tenant,
            reservation_id=reservation.reservation_id,
            **kwargs,
            session=session,
        )

        session.commit_transaction()

    assert replay.status.value == expected

    fence_after = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence_after is not None
    assert fence_after["revision"] == 2

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0


def test_real_aborted_consume_leaves_active_reservation_no_usage_and_old_fence(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5d-abort"
    document = "document-p5d-abort"

    reservation = _seed(
        mongo_context,
        tenant_id=tenant,
        document_id=document,
        label="abort",
    )

    content = _content(
        tenant_id=tenant,
        document_id=document,
        registered_at=AT + timedelta(minutes=1),
    )

    service = _lifecycle_service(
        fence_registry=mongo_context.fence_registry,
        reservation_registry=mongo_context.reservation_registry,
        usage_registry=mongo_context.usage_registry,
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        result = service.consume(
            tenant_id=tenant,
            reservation_id=reservation.reservation_id,
            content=content,
            consumed_at=AT + timedelta(minutes=2),
            session=session,
        )
        assert result.status.value == "CONSUMED"

        session.abort_transaction()

    row = mongo_context.reservations.find_one(
        {
            "tenant_id": tenant,
            "reservation_id": reservation.reservation_id,
        }
    )
    assert row is not None
    assert row["status"] == "ACTIVE"

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence is not None
    assert fence["revision"] == 1


def test_real_lifecycle_and_admission_cannot_both_commit_from_same_fence_revision(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5d-race"
    original_document = "document-p5d-race-original"
    new_document = "document-p5d-race-new"

    original = _seed(
        mongo_context,
        tenant_id=tenant,
        document_id=original_document,
        label="race-original",
        expires_at=AT + timedelta(minutes=30),
    )

    race_at = AT + timedelta(minutes=5)

    command = LegalEvidenceCapacityReservationCommand(
        tenant_id=tenant,
        document_id=new_document,
        reservation_id="reservation-p5d-race-new",
        ingestion_intent_id="ingestion-p5d-race-new",
        idempotency_key="idempotency-p5d-race-new",
        reserved_storage_bytes=1,
        reserved_ingress_bytes=1,
        reserved_document_versions=1,
        reserved_at=race_at,
        expires_at=race_at + timedelta(minutes=15),
    )
    profile = _profile(
        tenant_id=tenant,
        evaluated_at=race_at,
    )

    barrier = threading.Barrier(2)
    lock = threading.Lock()
    outcomes: dict[str, str] = {}

    def contender(
        label: str,
    ) -> None:
        client: MongoClient[Any] = MongoClient(
            URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000,
            retryWrites=True,
        )

        try:
            database = client.get_database(
                mongo_context.database_name,
                read_concern=ReadConcern("majority"),
                write_concern=WriteConcern(
                    w="majority",
                    j=True,
                ),
            )

            fence = BarrierFenceRegistry(
                LegalEvidenceCapacityAdmissionFenceRegistry(
                    database[FENCE_COLLECTION]
                ),
                barrier,
            )
            reservations = (
                LegalEvidenceCapacityReservationRegistry(
                    database[RESERVATION_COLLECTION]
                )
            )
            usage = LegalEvidenceUsageObservationRegistry(
                database[USAGE_COLLECTION]
            )

            with client.start_session() as session:
                _start_transaction(session)

                try:
                    if label == "LIFECYCLE":
                        service = _lifecycle_service(
                            fence_registry=fence,
                            reservation_registry=reservations,
                            usage_registry=usage,
                        )
                        value = service.release(
                            tenant_id=tenant,
                            reservation_id=original.reservation_id,
                            released_at=race_at,
                            session=session,
                        )
                        identity = value.reservation_id
                    else:
                        service = _admission_service(
                            fence_registry=fence,
                            reservation_registry=reservations,
                            usage_registry=usage,
                        )
                        value = service.reserve(
                            command=command,
                            tenant_profile=profile,
                            session=session,
                        )
                        identity = value.reservation_id

                    session.commit_transaction()
                    result = f"SUCCESS:{identity}"

                except (
                    LegalEvidenceCapacityReservationLifecycleError,
                    LegalEvidenceCapacityAdmissionError,
                    LegalEvidenceCapacityAdmissionFenceConflictError,
                    LegalEvidenceCapacityAdmissionFencePersistenceError,
                    LegalEvidenceCapacityReservationConflictError,
                    LegalEvidenceCapacityReservationPersistenceError,
                    PyMongoError,
                    threading.BrokenBarrierError,
                ) as error:
                    if session.in_transaction:
                        session.abort_transaction()

                    result = (
                        "FAIL:"
                        f"{type(error).__name__}:"
                        f"{error}"
                    )

                with lock:
                    outcomes[label] = result

        finally:
            client.close()

    threads = [
        threading.Thread(
            target=contender,
            args=("LIFECYCLE",),
        ),
        threading.Thread(
            target=contender,
            args=("ADMISSION",),
        ),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive()

    assert set(outcomes) == {
        "LIFECYCLE",
        "ADMISSION",
    }

    winners = [
        label
        for label, result in outcomes.items()
        if result.startswith("SUCCESS:")
    ]
    losers = [
        label
        for label, result in outcomes.items()
        if result.startswith("FAIL:")
    ]

    assert len(winners) == 1, outcomes
    assert len(losers) == 1, outcomes

    fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence is not None
    assert fence["revision"] == 2

    original_row = mongo_context.reservations.find_one(
        {
            "tenant_id": tenant,
            "reservation_id": original.reservation_id,
        }
    )
    assert original_row is not None

    new_row = mongo_context.reservations.find_one(
        {
            "tenant_id": tenant,
            "reservation_id": command.reservation_id,
        }
    )

    if winners[0] == "LIFECYCLE":
        assert original_row["status"] == "RELEASED"
        assert new_row is None
    else:
        assert original_row["status"] == "ACTIVE"
        assert new_row is not None
        assert new_row["status"] == "ACTIVE"

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    # Retry only the losing logical operation from a fresh snapshot. It must
    # serialize after the winner and commit as revision 3.
    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        if losers[0] == "LIFECYCLE":
            retry = _lifecycle_service(
                fence_registry=mongo_context.fence_registry,
                reservation_registry=mongo_context.reservation_registry,
                usage_registry=mongo_context.usage_registry,
            )
            result = retry.release(
                tenant_id=tenant,
                reservation_id=original.reservation_id,
                released_at=race_at,
                session=session,
            )
            assert result.status.value == "RELEASED"

        else:
            retry = _admission_service(
                fence_registry=mongo_context.fence_registry,
                reservation_registry=mongo_context.reservation_registry,
                usage_registry=mongo_context.usage_registry,
            )
            result = retry.reserve(
                command=command,
                tenant_profile=profile,
                session=session,
            )
            assert result.status.value == "ACTIVE"

        session.commit_transaction()

    fence_after_retry = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence_after_retry is not None
    assert fence_after_retry["revision"] == 3

    original_after = mongo_context.reservations.find_one(
        {
            "tenant_id": tenant,
            "reservation_id": original.reservation_id,
        }
    )
    new_after = mongo_context.reservations.find_one(
        {
            "tenant_id": tenant,
            "reservation_id": command.reservation_id,
        }
    )

    assert original_after is not None
    assert original_after["status"] == "RELEASED"
    assert new_after is not None
    assert new_after["status"] == "ACTIVE"

    assert mongo_context.usage.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0


# ARTIFACT: test_legal_evidence_capacity_reservation_lifecycle_service_real_mongo.py
# VERSION: v1.0.0-L10A2Q-P5D-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo semantic reservation lifecycle/reconciliation
# TENANT POSTURE: exact tenant/reservation/content binding
# CONSUMPTION POSTURE: CONSUMED and P3 usage are one transaction boundary
# RELEASE POSTURE: RELEASED creates no usage
# EXPIRY POSTURE: EXPIRED creates no usage
# REPLAY POSTURE: exact terminal replay advances no fence
# ABORT POSTURE: aborted lifecycle leaves no durable partial effects
# CONCURRENCY POSTURE: admission/lifecycle share one tenant serialization fence
# PROVIDER POSTURE: no binary-provider operation exists
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
