"""Real-Mongo certificate for atomic Legal Evidence capacity reservation.

TITLE: Legal Evidence Capacity Reservation Service Real-Mongo Certificate
VERSION: v1.0.0-L10A2Q-P5C-B-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Prove on an actual disposable Mongo replica set that two independent
    ingestion intents cannot both commit reservations whose combined effect
    exceeds canonical tenant/document capacity.

EPITOME:
    COMPLETE P3C USAGE
    + P4 REMAINING CAPACITY
    + DURABLE ACTIVE P5B RESERVATIONS
    + P5C-A TENANT SERIALIZATION FENCE
    -> AT MOST ONE ADMISSIBLE COMMIT
    != PROVIDER WRITE
    != USAGE COMMITTED
    != AUTHORIZED AVAILABILITY

DECISIVE RACE:
    Seed 24 canonical document-version usage observations under STARTER's
    canonical 25-version limit. Race two distinct 1-version ingestion intents
    for the same tenant/document. Exactly one may commit. The loser, when
    retried in a fresh transaction, must observe the winner's ACTIVE
    reservation and reject for document-version capacity.

REPLAY:
    An exact committed command replay returns the durable reservation without
    advancing the tenant admission fence or creating a second row.

TRANSACTION:
    Every service call executes inside one caller-owned snapshot transaction.
    The service never owns transaction retry. The test explicitly retries the
    losing logical command in a fresh transaction after the competing race.

DATABASE SAFETY:
    Only loopback wilsyVendorCertRS is accepted. One UUID-isolated disposable
    certification database is created and dropped. Canonical database "wilsy"
    is forbidden.

AUTHORITY BOUNDARY:
    Capacity admission/reservation evidence only. No binary provider, IAM,
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

from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    LegalEvidenceUsageObservation,
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
DATABASE_PREFIX = "wilsy_l10a2q_p5cb_cert_"

AT = datetime(
    2026,
    9,
    30,
    6,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)
SHA_A = "a" * 128
SHA_B = "b" * 128


class MongoContext:
    """Own one isolated P5C-B certification database."""

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
                "P5CB_CERT_MONGO_NOT_LOOPBACK"
            )

        if hello.get("setName") != REPLICA_SET:
            raise RuntimeError(
                "P5CB_CERT_REPLICA_SET_MISMATCH"
            )

        if hello.get("isWritablePrimary") is not True:
            raise RuntimeError(
                "P5CB_CERT_WRITABLE_PRIMARY_REQUIRED"
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
                "P5CB_CERT_DATABASE_GUARD_FAILED"
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
    """Yield and then remove only one UUID-isolated certification DB."""
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


def _start_transaction(session: Any) -> None:
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
    )


def _profile(
    tenant_id: str,
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
        evaluated_at=AT,
    )


def _command(
    *,
    tenant_id: str,
    document_id: str,
    label: str,
) -> LegalEvidenceCapacityReservationCommand:
    return LegalEvidenceCapacityReservationCommand(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=f"reservation-{label}",
        ingestion_intent_id=f"ingestion-{label}",
        idempotency_key=f"idempotency-{label}",
        reserved_storage_bytes=1,
        reserved_ingress_bytes=1,
        reserved_document_versions=1,
        reserved_at=AT,
        expires_at=AT + timedelta(minutes=15),
    )


def _seed_usage_to_twenty_four_versions(
    context: MongoContext,
    *,
    tenant_id: str,
    document_id: str,
) -> None:
    with context.client.start_session() as session:
        _start_transaction(session)

        for number in range(1, 25):
            hex_content = f"{number:0128x}"
            hex_evidence = f"{number + 1000:0128x}"

            observation = LegalEvidenceUsageObservation(
                tenant_id=tenant_id,
                usage_observation_id=(
                    f"usage-{document_id}-{number:02d}"
                ),
                case_matter_id=f"matter-{tenant_id}",
                document_id=document_id,
                content_reference=(
                    f"content-{document_id}-{number:02d}"
                ),
                content_fingerprint=hex_content,
                content_evidence_fingerprint=hex_evidence,
                storage_bytes_added=1,
                monthly_ingress_bytes=1,
                document_versions_added=1,
                occurred_at=AT - timedelta(minutes=1),
            )

            context.usage_registry.create_or_replay(
                observation,
                idempotency_key=(
                    f"usage-idempotency-{tenant_id}-{number:02d}"
                ),
                session=session,
            )

        session.commit_transaction()


def _seed_fence(
    context: MongoContext,
    *,
    tenant_id: str,
) -> None:
    with context.client.start_session() as session:
        _start_transaction(session)

        fence = context.fence_registry.advance(
            tenant_id=tenant_id,
            expected_revision=None,
            coordination_reference=(
                f"seed-{tenant_id}"
            ),
            advanced_at=AT - timedelta(minutes=2),
            session=session,
        )

        assert fence.revision == 1
        session.commit_transaction()


def _service(
    *,
    fence_registry: Any,
    usage_registry: Any,
    reservation_registry: Any,
) -> LegalEvidenceCapacityReservationService:
    return LegalEvidenceCapacityReservationService(
        fence_registry=fence_registry,
        usage_registry=usage_registry,
        reservation_registry=reservation_registry,
    )


class BarrierFenceRegistry:
    """Force competing transactions to read one fence revision before CAS."""

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


def test_real_exact_replay_does_not_advance_fence_or_duplicate_reservation(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5cb-replay"
    document = "document-p5cb-replay"

    _seed_usage_to_twenty_four_versions(
        mongo_context,
        tenant_id=tenant,
        document_id=document,
    )
    _seed_fence(
        mongo_context,
        tenant_id=tenant,
    )

    command = _command(
        tenant_id=tenant,
        document_id=document,
        label="replay",
    )
    profile = _profile(tenant)

    service = _service(
        fence_registry=mongo_context.fence_registry,
        usage_registry=mongo_context.usage_registry,
        reservation_registry=mongo_context.reservation_registry,
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        first = service.reserve(
            command=command,
            tenant_profile=profile,
            session=session,
        )

        session.commit_transaction()

    fence_after_first = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence_after_first is not None
    assert fence_after_first["revision"] == 2

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        replayed = service.reserve(
            command=command,
            tenant_profile=profile,
            session=session,
        )

        session.commit_transaction()

    assert replayed == first

    fence_after_replay = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence_after_replay is not None
    assert fence_after_replay["revision"] == 2

    assert mongo_context.reservations.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


def test_real_sequential_second_ingestion_rejects_last_version_oversubscription(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5cb-sequential"
    document = "document-p5cb-sequential"

    _seed_usage_to_twenty_four_versions(
        mongo_context,
        tenant_id=tenant,
        document_id=document,
    )
    _seed_fence(
        mongo_context,
        tenant_id=tenant,
    )

    profile = _profile(tenant)
    first_command = _command(
        tenant_id=tenant,
        document_id=document,
        label="sequential-a",
    )
    second_command = _command(
        tenant_id=tenant,
        document_id=document,
        label="sequential-b",
    )

    service = _service(
        fence_registry=mongo_context.fence_registry,
        usage_registry=mongo_context.usage_registry,
        reservation_registry=mongo_context.reservation_registry,
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        service.reserve(
            command=first_command,
            tenant_profile=profile,
            session=session,
        )
        session.commit_transaction()

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        with pytest.raises(
            LegalEvidenceCapacityAdmissionError,
            match=(
                "L10A2Q_P5CB_"
                "DOCUMENT_VERSION_CAPACITY_EXCEEDED"
            ),
        ):
            service.reserve(
                command=second_command,
                tenant_profile=profile,
                session=session,
            )

        session.abort_transaction()

    assert mongo_context.reservations.count_documents(
        {
            "tenant_id": tenant,
            "status": "ACTIVE",
        }
    ) == 1

    fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence is not None

    # The failed second admission advanced the fence only inside its aborted
    # transaction, therefore durable revision remains seed(1) + winner(1).
    assert fence["revision"] == 2


def test_real_competing_ingestions_cannot_both_commit_last_document_version(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5cb-race"
    document = "document-p5cb-race"

    _seed_usage_to_twenty_four_versions(
        mongo_context,
        tenant_id=tenant,
        document_id=document,
    )
    _seed_fence(
        mongo_context,
        tenant_id=tenant,
    )

    commands = {
        "A": _command(
            tenant_id=tenant,
            document_id=document,
            label="race-a",
        ),
        "B": _command(
            tenant_id=tenant,
            document_id=document,
            label="race-b",
        ),
    }
    profile = _profile(tenant)

    barrier = threading.Barrier(2)
    lock = threading.Lock()
    outcomes: dict[str, str] = {}

    def contender(label: str) -> None:
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

            fence_inner = (
                LegalEvidenceCapacityAdmissionFenceRegistry(
                    database[FENCE_COLLECTION]
                )
            )
            fence = BarrierFenceRegistry(
                fence_inner,
                barrier,
            )
            usage = LegalEvidenceUsageObservationRegistry(
                database[USAGE_COLLECTION]
            )
            reservations = (
                LegalEvidenceCapacityReservationRegistry(
                    database[RESERVATION_COLLECTION]
                )
            )
            service = _service(
                fence_registry=fence,
                usage_registry=usage,
                reservation_registry=reservations,
            )

            with client.start_session() as session:
                _start_transaction(session)

                try:
                    reservation = service.reserve(
                        command=commands[label],
                        tenant_profile=profile,
                        session=session,
                    )
                    session.commit_transaction()
                    result = (
                        f"SUCCESS:{reservation.reservation_id}"
                    )

                except (
                    LegalEvidenceCapacityAdmissionError,
                    LegalEvidenceCapacityAdmissionFenceConflictError,
                    LegalEvidenceCapacityAdmissionFencePersistenceError,
                    LegalEvidenceCapacityReservationConflictError,
                    LegalEvidenceCapacityReservationPersistenceError,
                    PyMongoError,
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
            args=("A",),
        ),
        threading.Thread(
            target=contender,
            args=("B",),
        ),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive()

    assert set(outcomes) == {
        "A",
        "B",
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

    assert mongo_context.reservations.count_documents(
        {
            "tenant_id": tenant,
            "status": "ACTIVE",
        }
    ) == 1

    persisted = list(
        mongo_context.reservations.find(
            {
                "tenant_id": tenant,
                "status": "ACTIVE",
            }
        )
    )
    assert len(persisted) == 1
    assert persisted[0]["reservation_id"] == (
        commands[winners[0]].reservation_id
    )

    fence = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence is not None

    # Seed revision 1 + exactly one committed admission = revision 2.
    assert fence["revision"] == 2

    # Retry the losing logical command from a completely fresh transaction.
    # It must now see the winner's ACTIVE reservation and reject capacity.
    retry_service = _service(
        fence_registry=mongo_context.fence_registry,
        usage_registry=mongo_context.usage_registry,
        reservation_registry=mongo_context.reservation_registry,
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        with pytest.raises(
            LegalEvidenceCapacityAdmissionError,
            match=(
                "L10A2Q_P5CB_"
                "DOCUMENT_VERSION_CAPACITY_EXCEEDED"
            ),
        ):
            retry_service.reserve(
                command=commands[losers[0]],
                tenant_profile=profile,
                session=session,
            )

        session.abort_transaction()

    # Retry failure is atomic: no second reservation and no durable fence
    # advancement from the aborted capacity-rejection transaction.
    assert mongo_context.reservations.count_documents(
        {
            "tenant_id": tenant,
            "status": "ACTIVE",
        }
    ) == 1

    fence_after_retry = mongo_context.fences.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert fence_after_retry is not None
    assert fence_after_retry["revision"] == 2


# ARTIFACT: test_legal_evidence_capacity_reservation_service_real_mongo.py
# VERSION: v1.0.0-L10A2Q-P5C-B-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo atomic capacity admission/reservation only
# TENANT POSTURE: exact tenant/document/profile/reservation isolation
# CONCURRENCY POSTURE: competing oversubscribing intents cannot both commit
# REPLAY POSTURE: exact replay creates no new reservation or fence revision
# EXPIRY POSTURE: durable ACTIVE state, not wall clock, consumes reservation capacity
# PROVIDER POSTURE: no binary-provider operation exists in this certificate
# TRANSACTION POSTURE: caller owns each snapshot transaction and retry scope
# RECONCILIATION POSTURE: P5D remains semantic lifecycle/reconciliation owner
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
