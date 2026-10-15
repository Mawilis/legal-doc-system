"""
TITLE: WILSY OS Legal Work Supervision Binding Registry Real-Mongo Certificate

VERSION: v1.0.0-SV-P3-LEGAL-WORK-SUPERVISION-BINDING-REGISTRY-REAL-MONGO

EPITOME:
    Certify append-only Legal supervision durability and effective currentness
    against a real transactional Mongo replica set.

AUTHORITY BOUNDARY:
    Persistence/currentness only. No IAM, assignment authority, approval
    execution, workflow transition, billing, payment, execution or settlement.

CURRENTNESS:
    Derived from immutable successor chains plus effective dating.
    Multiple independent supervision chains may coexist.

TRANSACTION POSTURE:
    Every registry operation executes inside a caller-owned active transaction.

FINANCIAL POSTURE:
    NONE. Kennel EOS exclusively owns financial execution and settlement.
"""

from __future__ import annotations

import os
import threading
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_work_supervision_binding import (
    LegalSupervisionControlLevel,
    LegalSupervisionScope,
    LegalWorkSupervisionBinding,
)
from tools.eos.legal_operations.registry.legal_work_supervision_binding_registry import (
    BINDING_IDENTITY_INDEX_NAME,
    PREDECESSOR_INDEX_NAME,
    SUPERVISEE_INDEX_NAME,
    SUPERVISOR_INDEX_NAME,
    WORK_SCOPE_INDEX_NAME,
    LegalWorkSupervisionBindingRegistry,
    RegistryConflictError,
    RegistryNotFoundError,
    RegistryPersistedRecordInvalidError,
)


URI = os.environ["WILSY_SV_REAL_MONGO_URI"]

NOW = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)
TENANT = "tenant-a"
MATTER = "matter-a"
WORK = "work-a"
SUPERVISOR = "principal-supervisor"
SUPERVISEE = "principal-supervisee"


@pytest.fixture()
def mongo_context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    client.admin.command("ping")

    database = client[
        "wilsy_sv_supervision_"
        + uuid.uuid4().hex
    ]

    collection = database[
        "legal_work_supervision_bindings"
    ]

    registry = LegalWorkSupervisionBindingRegistry(
        collection
    )

    registry.ensure_indexes()

    try:
        yield (
            client,
            database,
            collection,
            registry,
        )
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def _binding(
    binding_id: str,
    *,
    supervisor: str = SUPERVISOR,
    supervisee: str = SUPERVISEE,
    tenant_id: str = TENANT,
    matter_id: str = MATTER,
    scope: LegalSupervisionScope = (
        LegalSupervisionScope.WORK_ITEM
    ),
    work_item_id: str | None = WORK,
    control_level: LegalSupervisionControlLevel = (
        LegalSupervisionControlLevel.REVIEW_REQUIRED
    ),
    effective_from: datetime = NOW,
    effective_until: datetime | None = None,
    supersedes: str | None = None,
) -> LegalWorkSupervisionBinding:
    return LegalWorkSupervisionBinding(
        supervision_binding_id=binding_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        scope=scope,
        work_item_id=work_item_id,
        supervisee_principal_id=supervisee,
        supervisor_principal_id=supervisor,
        control_level=control_level,
        supervision_plan_reference="plan:legal-supervision",
        supervision_basis_reference="basis:engagement",
        effective_from=effective_from,
        effective_until=effective_until,
        supersedes_supervision_binding_id=supersedes,
    )


def test_real_indexes_and_no_ttl(
    mongo_context: Any,
) -> None:
    _, _, collection, _ = mongo_context

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    for name in (
        BINDING_IDENTITY_INDEX_NAME,
        PREDECESSOR_INDEX_NAME,
        SUPERVISOR_INDEX_NAME,
        SUPERVISEE_INDEX_NAME,
        WORK_SCOPE_INDEX_NAME,
    ):
        assert name in indexes

    assert indexes[
        BINDING_IDENTITY_INDEX_NAME
    ]["unique"] is True

    assert indexes[
        PREDECESSOR_INDEX_NAME
    ]["unique"] is True

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )


def test_real_initial_exact_replay_and_current(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    value = _binding(
        "supervision-a"
    )

    with client.start_session() as session:
        with session.start_transaction():
            first = registry.persist(
                value,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            replay = registry.persist(
                value,
                session=session,
            )

            current = registry.list_current_for_supervisor(
                TENANT,
                SUPERVISOR,
                NOW,
                session=session,
            )

    assert first == value
    assert replay == value
    assert current == (value,)

    assert collection.count_documents(
        {
            "tenant_id": TENANT,
            "supervision_binding_id": "supervision-a",
        }
    ) == 1


def test_real_divergent_identity_replay_rejected(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    first = _binding(
        "supervision-a",
        control_level=(
            LegalSupervisionControlLevel.OVERSIGHT
        ),
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                first,
                session=session,
            )

    with pytest.raises(
        RegistryConflictError,
        match="DIVERGENT_REPLAY",
    ):
        with client.start_session() as session:
            with session.start_transaction():
                registry.persist(
                    _binding(
                        "supervision-a",
                        control_level=(
                            LegalSupervisionControlLevel.REVIEW_REQUIRED
                        ),
                    ),
                    session=session,
                )

    assert collection.count_documents(
        {
            "tenant_id": TENANT,
            "supervision_binding_id": "supervision-a",
        }
    ) == 1


def test_real_successor_lineage_and_effective_currentness(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    first = _binding(
        "supervision-a",
        control_level=(
            LegalSupervisionControlLevel.OVERSIGHT
        ),
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                first,
                session=session,
            )

    second = _binding(
        "supervision-b",
        control_level=(
            LegalSupervisionControlLevel.REVIEW_REQUIRED
        ),
        effective_from=NOW + timedelta(hours=1),
        supersedes=first.supervision_binding_id,
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                second,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            before = registry.list_current_for_supervisee(
                TENANT,
                SUPERVISEE,
                NOW + timedelta(minutes=30),
                session=session,
            )

            after = registry.list_current_for_supervisee(
                TENANT,
                SUPERVISEE,
                NOW + timedelta(hours=2),
                session=session,
            )

    assert before == (first,)
    assert after == (second,)


def test_real_multiple_independent_current_chains(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    one = _binding(
        "supervision-a",
        supervisee="principal-a",
        work_item_id="work-a",
    )

    two = _binding(
        "supervision-b",
        supervisee="principal-b",
        work_item_id="work-b",
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                one,
                session=session,
            )
            registry.persist(
                two,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            current = registry.list_current_for_supervisor(
                TENANT,
                SUPERVISOR,
                NOW,
                session=session,
            )

    assert tuple(
        item.supervision_binding_id
        for item in current
    ) == (
        "supervision-a",
        "supervision-b",
    )


def test_real_expiry_removes_leaf_from_currentness(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    value = _binding(
        "supervision-expiring",
        effective_until=NOW + timedelta(hours=1),
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                value,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            before = registry.list_current_for_supervisor(
                TENANT,
                SUPERVISOR,
                NOW + timedelta(minutes=30),
                session=session,
            )
            after = registry.list_current_for_supervisor(
                TENANT,
                SUPERVISOR,
                NOW + timedelta(hours=2),
                session=session,
            )

    assert before == (value,)
    assert after == ()


def test_real_foreign_tenant_isolation(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    value = _binding(
        "supervision-a"
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                value,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            assert (
                registry.list_current_for_supervisor(
                    "tenant-b",
                    SUPERVISOR,
                    NOW,
                    session=session,
                )
                == ()
            )

            with pytest.raises(
                RegistryNotFoundError,
                match="BINDING_NOT_FOUND",
            ):
                registry.get_by_binding_id(
                    "tenant-b",
                    "supervision-a",
                    session=session,
                )


def test_real_transaction_abort_rolls_back(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    session = client.start_session()

    try:
        session.start_transaction()

        registry.persist(
            _binding(
                "supervision-abort",
                work_item_id="work-abort",
            ),
            session=session,
        )

        session.abort_transaction()
    finally:
        session.end_session()

    assert collection.count_documents(
        {
            "tenant_id": TENANT,
            "supervision_binding_id":
                "supervision-abort",
        }
    ) == 0


def test_real_corrupt_persisted_row_rejected(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    collection.insert_one(
        {
            "tenant_id": TENANT,
            "supervision_binding_id": "corrupt-a",
            "case_matter_id": MATTER,
            "scope": "WORK_ITEM",
            "work_item_id": "work-corrupt",
            "supervisee_principal_id": SUPERVISEE,
            "supervisor_principal_id": SUPERVISOR,
        }
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                RegistryPersistedRecordInvalidError,
                match="PERSISTED_RECORD_INVALID",
            ):
                registry.list_current_for_supervisor(
                    TENANT,
                    SUPERVISOR,
                    NOW,
                    session=session,
                )


def test_real_competing_successors_have_one_durable_winner(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    root = _binding(
        "supervision-root",
        control_level=(
            LegalSupervisionControlLevel.OVERSIGHT
        ),
        work_item_id="work-race",
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                root,
                session=session,
            )

    barrier = threading.Barrier(2)

    results: list[
        tuple[str, str]
    ] = []

    lock = threading.Lock()

    def worker(
        suffix: str,
    ) -> None:
        value = _binding(
            f"supervision-{suffix}",
            control_level=(
                LegalSupervisionControlLevel.REVIEW_REQUIRED
            ),
            work_item_id="work-race",
            effective_from=(
                NOW + timedelta(hours=1)
            ),
            supersedes=root.supervision_binding_id,
        )

        worker_client: MongoClient[Any] = MongoClient(
            URI,
            serverSelectionTimeoutMS=5000,
            uuidRepresentation="standard",
        )

        try:
            worker_collection = worker_client[
                collection.database.name
            ][
                collection.name
            ]

            worker_registry = (
                LegalWorkSupervisionBindingRegistry(
                    worker_collection
                )
            )

            with worker_client.start_session() as session:
                session.start_transaction()

                barrier.wait(timeout=10)

                try:
                    persisted = worker_registry.persist(
                        value,
                        session=session,
                    )

                    session.commit_transaction()

                    outcome = (
                        "SUCCESS",
                        persisted.supervision_binding_id,
                    )
                except Exception as exc:
                    if session.in_transaction:
                        session.abort_transaction()

                    outcome = (
                        "FAILURE",
                        type(exc).__name__,
                    )

            with lock:
                results.append(
                    outcome
                )
        finally:
            worker_client.close()

    threads = [
        threading.Thread(
            target=worker,
            args=("a",),
            daemon=True,
        ),
        threading.Thread(
            target=worker,
            args=("b",),
            daemon=True,
        ),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(
            timeout=20
        )

    assert all(
        not thread.is_alive()
        for thread in threads
    )

    assert len(results) == 2

    successes = [
        value
        for outcome, value in results
        if outcome == "SUCCESS"
    ]

    failures = [
        value
        for outcome, value in results
        if outcome == "FAILURE"
    ]

    assert len(successes) == 1
    assert len(failures) == 1

    durable_successors = list(
        collection.find(
            {
                "tenant_id": TENANT,
                "supersedes_supervision_binding_id":
                    root.supervision_binding_id,
            }
        )
    )

    assert len(
        durable_successors
    ) == 1

    with client.start_session() as session:
        with session.start_transaction():
            current = registry.list_current_for_supervisor(
                TENANT,
                SUPERVISOR,
                NOW + timedelta(hours=2),
                session=session,
            )

    assert len(current) == 1
    assert (
        current[0].supervision_binding_id
        == durable_successors[0]["supervision_binding_id"]
    )


# AUTHORITY BOUNDARY:
# real-Mongo supervision persistence/currentness only.
# No IAM, assignment, approval execution or financial execution authority.
