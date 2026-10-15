"""
TITLE: WILSY OS Legal Work Assignment Registry Real-Mongo Certificate

VERSION: v1.0.0-AS-P3-LEGAL-WORK-ASSIGNMENT-REGISTRY-REAL-MONGO

EPITOME:
    Certify append-only Legal work-assignment history and derived currentness
    against a real transactional Mongo replica set.

AUTHORITY BOUNDARY:
    Persistence/currentness only. No IAM, assignment-command, workflow,
    supervision, billing, payment, execution or settlement authority.

TRANSACTION POSTURE:
    Every registry operation executes inside a caller-owned active transaction.

CURRENTNESS:
    Derived from immutable lineage. No mutable current pointer.

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

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.registry.legal_work_assignment_registry import (
    ASSIGNEE_INDEX_NAME,
    ASSIGNMENT_IDENTITY_INDEX_NAME,
    INITIAL_WORK_ITEM_INDEX_NAME,
    PREDECESSOR_INDEX_NAME,
    WORK_ITEM_HISTORY_INDEX_NAME,
    LegalWorkAssignmentRegistry,
    RegistryConflictError,
    RegistryError,
    RegistryNotFoundError,
    RegistryPersistedRecordInvalidError,
)


URI = os.environ["WILSY_AS_REAL_MONGO_URI"]

NOW = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)
TENANT = "tenant-a"
MATTER = "matter-a"
WORK = "work-a"


@pytest.fixture()
def mongo_context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    client.admin.command("ping")

    database = client[
        "wilsy_as_assignment_"
        + uuid.uuid4().hex
    ]

    collection = database[
        "legal_work_assignments"
    ]

    registry = LegalWorkAssignmentRegistry(
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


def _assignment(
    assignment_id: str,
    assignee: str,
    *,
    tenant_id: str = TENANT,
    matter_id: str = MATTER,
    work_item_id: str = WORK,
    assigned_at: datetime = NOW,
    supersedes: str | None = None,
) -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id=assignment_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        work_item_id=work_item_id,
        assignee_principal_id=assignee,
        assigned_by_principal_id="principal-assigner",
        assigned_at=assigned_at,
        assignment_reason_reference="reason:staffing",
        authorization_evidence_reference="authz:assignment",
        supersedes_assignment_id=supersedes,
    )


def _tx(
    client: MongoClient[Any],
):
    session = client.start_session()
    session.start_transaction()
    return session


def test_real_indexes_and_no_ttl(
    mongo_context: Any,
) -> None:
    _, _, collection, _ = mongo_context

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    for name in (
        ASSIGNMENT_IDENTITY_INDEX_NAME,
        INITIAL_WORK_ITEM_INDEX_NAME,
        PREDECESSOR_INDEX_NAME,
        WORK_ITEM_HISTORY_INDEX_NAME,
        ASSIGNEE_INDEX_NAME,
    ):
        assert name in indexes

    assert indexes[
        ASSIGNMENT_IDENTITY_INDEX_NAME
    ]["unique"] is True

    assert indexes[
        INITIAL_WORK_ITEM_INDEX_NAME
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

    value = _assignment(
        "assignment-a",
        "principal-a",
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
            current = registry.resolve_current(
                TENANT,
                WORK,
                session=session,
            )

    assert first == value
    assert replay == value
    assert current == value
    assert collection.count_documents(
        {
            "tenant_id": TENANT,
            "work_item_id": WORK,
        }
    ) == 1


def test_real_divergent_identity_replay_rejected(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    first = _assignment(
        "assignment-a",
        "principal-a",
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
                    _assignment(
                        "assignment-a",
                        "principal-b",
                    ),
                    session=session,
                )

    assert collection.count_documents(
        {
            "tenant_id": TENANT,
            "work_item_id": WORK,
        }
    ) == 1


def test_real_reassignment_lineage_and_current_assignee(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    first = _assignment(
        "assignment-a",
        "principal-a",
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                first,
                session=session,
            )

    second = _assignment(
        "assignment-b",
        "principal-b",
        assigned_at=NOW + timedelta(minutes=1),
        supersedes=first.assignment_id,
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                second,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            history = registry.get_history(
                TENANT,
                WORK,
                session=session,
            )
            current = registry.resolve_current(
                TENANT,
                WORK,
                session=session,
            )
            old_principal = (
                registry.list_current_for_assignee(
                    TENANT,
                    "principal-a",
                    session=session,
                )
            )
            new_principal = (
                registry.list_current_for_assignee(
                    TENANT,
                    "principal-b",
                    session=session,
                )
            )

    assert history == (
        first,
        second,
    )
    assert current == second
    assert old_principal == ()
    assert new_principal == (second,)


def test_real_stale_predecessor_rejected(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    first = _assignment(
        "assignment-a",
        "principal-a",
    )

    second = _assignment(
        "assignment-b",
        "principal-b",
        assigned_at=NOW + timedelta(minutes=1),
        supersedes=first.assignment_id,
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                first,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                second,
                session=session,
            )

    with pytest.raises(
        RegistryConflictError,
        match="STALE_PREDECESSOR",
    ):
        with client.start_session() as session:
            with session.start_transaction():
                registry.persist(
                    _assignment(
                        "assignment-c",
                        "principal-c",
                        assigned_at=(
                            NOW
                            + timedelta(minutes=2)
                        ),
                        supersedes=first.assignment_id,
                    ),
                    session=session,
                )

    assert collection.count_documents(
        {
            "tenant_id": TENANT,
            "work_item_id": WORK,
        }
    ) == 2


def test_real_foreign_tenant_isolation(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    first = _assignment(
        "assignment-a",
        "principal-a",
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                first,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            assert (
                registry.resolve_current(
                    "tenant-b",
                    WORK,
                    session=session,
                )
                is None
            )

            with pytest.raises(
                RegistryNotFoundError,
                match="HISTORY_NOT_FOUND",
            ):
                registry.get_history(
                    "tenant-b",
                    WORK,
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
            _assignment(
                "assignment-abort",
                "principal-a",
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
            "assignment_id": "assignment-abort",
        }
    ) == 0


def test_real_corrupt_persisted_row_rejected(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    collection.insert_one(
        {
            "tenant_id": TENANT,
            "assignment_id": "corrupt-a",
            "case_matter_id": MATTER,
            "work_item_id": "work-corrupt",
            "assignee_principal_id": "principal-a",
        }
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                RegistryPersistedRecordInvalidError,
                match="PERSISTED_RECORD_INVALID",
            ):
                registry.get_history(
                    TENANT,
                    "work-corrupt",
                    session=session,
                )


def test_real_competing_successors_have_one_durable_winner(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    first = _assignment(
        "assignment-root",
        "principal-root",
        work_item_id="work-race",
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.persist(
                first,
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
        value = _assignment(
            f"assignment-{suffix}",
            f"principal-{suffix}",
            work_item_id="work-race",
            assigned_at=(
                NOW
                + timedelta(minutes=1)
            ),
            supersedes=first.assignment_id,
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

            worker_registry = LegalWorkAssignmentRegistry(
                worker_collection
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
                        persisted.assignment_id,
                    )
                except Exception as exc:
                    if session.in_transaction:
                        session.abort_transaction()

                    outcome = (
                        "FAILURE",
                        type(exc).__name__,
                    )

            with lock:
                results.append(outcome)
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
        thread.join(timeout=20)

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
                "work_item_id": "work-race",
                "supersedes_assignment_id":
                    first.assignment_id,
            }
        )
    )

    assert len(
        durable_successors
    ) == 1

    with client.start_session() as session:
        with session.start_transaction():
            current = registry.resolve_current(
                TENANT,
                "work-race",
                session=session,
            )

    assert current is not None
    assert (
        current.assignment_id
        == durable_successors[0]["assignment_id"]
    )


# AUTHORITY BOUNDARY:
# real-Mongo assignment persistence/currentness only.
# No IAM, workflow, supervision or financial execution authority.
