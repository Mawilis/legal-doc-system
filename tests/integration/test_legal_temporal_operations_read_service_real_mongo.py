"""
P4-P1 Legal Temporal Operations read-service real-Mongo certificate.

AUTHORITY:
    Persistence-backed read certification only.

PROVES:
    - caller-owned active transaction is required;
    - only Productive-Work-visible matter IDs are queried;
    - hidden same-tenant matters do not surface;
    - same matter identity in another tenant does not surface;
    - canonical deadline provenance is preserved;
    - deterministic due_at / matter / deadline ordering survives real Mongo;
    - the temporal service creates no new persistence authority.

NO AUTHORITY:
    No IAM, visibility grant, assignment, supervision, deadline calculation,
    court/hearing creation, AI, billing, payment, settlement or financial
    execution authority.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
)
from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)
from tools.eos.legal_operations.registry import (
    legal_matter_deadline_registry as deadline_registry,
)
from tools.eos.legal_operations.service.legal_temporal_operations_read_service import (
    LegalTemporalOperationsReadService,
    LegalTemporalOperationsReadServiceTransactionRequiredError,
)


URI = os.environ["WILSY_P4_TEMPORAL_MONGO_URI"]
DATABASE_NAME = os.environ["WILSY_P4_TEMPORAL_MONGO_DB"]

TENANT = "tenant-p4-real"
FOREIGN_TENANT = "tenant-p4-foreign"

NOW = datetime(
    2026,
    10,
    18,
    15,
    30,
    tzinfo=timezone.utc,
)


@pytest.fixture()
def mongo() -> Iterator[tuple[MongoClient[Any], Any]]:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5_000,
    )

    client.admin.command("ping")

    database = client[DATABASE_NAME]

    collection = database[
        deadline_registry.COLLECTION
    ]

    deadline_registry.ensure_indexes(
        collection
    )

    try:
        yield client, collection
    finally:
        client.drop_database(
            DATABASE_NAME
        )
        client.close()


def _work(
    identity: str,
    matter: str,
) -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=identity,
        tenant_id=TENANT,
        case_matter_id=matter,
        title=identity,
        source_kind="LEGAL_WORKFLOW_STAGE",
        source_reference=f"stage:{identity}",
        source_evidence_fingerprint="1" * 128,
        status=LegalWorkItemStatus.OPEN,
        created_at=NOW,
        due_at=None,
    )


def _productive(
    *,
    assigned: tuple[LegalWorkItem, ...] = (),
    supervised: tuple[LegalWorkItem, ...] = (),
) -> LegalProductiveWorkProjection:
    return LegalProductiveWorkProjection(
        tenant_id=TENANT,
        principal_id="principal-p4-real",
        as_of=NOW,
        operating_contexts=(),
        capability_ids=(),
        assigned_work_items=assigned,
        supervised_work_items=supervised,
        overdue_work_items=(),
        due_soon_work_items=(),
    )


def _deadline(
    identity: str,
    matter: str,
    *,
    days: int,
    tenant: str = TENANT,
    source_fingerprint: str = "2" * 128,
) -> LegalMatterDeadline:
    return LegalMatterDeadline(
        tenant_id=tenant,
        case_matter_id=matter,
        deadline_id=identity,
        deadline_kind="FILING",
        title=identity,
        due_at=NOW + timedelta(days=days),
        source_type="COURT_ORDER",
        source_reference=f"evidence:{identity}",
        source_evidence_fingerprint=source_fingerprint,
        jurisdiction_reference="jurisdiction:za-high-court",
        created_at=NOW,
    )


def _persist(
    collection: Any,
    session: Any,
    *values: LegalMatterDeadline,
) -> None:
    for value in values:
        deadline_registry.persist_deadline(
            value,
            collection,
            session=session,
        )


def test_real_mongo_visible_matters_only_and_cross_tenant_nondisclosure(
    mongo: tuple[MongoClient[Any], Any],
) -> None:
    client, collection = mongo

    visible_a_early = _deadline(
        "deadline-visible-a-early",
        "matter-visible-a",
        days=1,
        source_fingerprint="a" * 128,
    )

    visible_a_late = _deadline(
        "deadline-visible-a-late",
        "matter-visible-a",
        days=7,
        source_fingerprint="b" * 128,
    )

    visible_b = _deadline(
        "deadline-visible-b",
        "matter-visible-b",
        days=2,
        source_fingerprint="c" * 128,
    )

    hidden = _deadline(
        "deadline-hidden",
        "matter-hidden",
        days=0,
        source_fingerprint="d" * 128,
    )

    foreign_same_matter = _deadline(
        "deadline-foreign",
        "matter-visible-a",
        days=0,
        tenant=FOREIGN_TENANT,
        source_fingerprint="e" * 128,
    )

    with client.start_session() as session:
        with session.start_transaction():
            _persist(
                collection,
                session,
                visible_a_late,
                hidden,
                visible_b,
                foreign_same_matter,
                visible_a_early,
            )

    productive = _productive(
        assigned=(
            _work(
                "work-a-1",
                "matter-visible-a",
            ),
            _work(
                "work-a-2",
                "matter-visible-a",
            ),
        ),
        supervised=(
            _work(
                "work-b",
                "matter-visible-b",
            ),
        ),
    )

    service = LegalTemporalOperationsReadService(
        deadline_collection=collection
    )

    with client.start_session() as session:
        with session.start_transaction():
            projection = service.project(
                productive_work=productive,
                session=session,
            )

            assert projection.visible_matter_ids == (
                "matter-visible-a",
                "matter-visible-b",
            )

            assert [
                row.deadline_id
                for row in projection.rows
            ] == [
                "deadline-visible-a-early",
                "deadline-visible-b",
                "deadline-visible-a-late",
            ]

            assert {
                row.case_matter_id
                for row in projection.rows
            } == {
                "matter-visible-a",
                "matter-visible-b",
            }

            assert all(
                row.deadline_id
                not in {
                    "deadline-hidden",
                    "deadline-foreign",
                }
                for row in projection.rows
            )

            assert (
                projection.rows[0].source_reference
                == visible_a_early.source_reference
            )

            assert (
                projection.rows[0].source_evidence_fingerprint
                == visible_a_early.source_evidence_fingerprint
            )

            assert (
                projection.rows[0].jurisdiction_reference
                == visible_a_early.jurisdiction_reference
            )


def test_real_mongo_empty_productive_visibility_reads_nothing(
    mongo: tuple[MongoClient[Any], Any],
) -> None:
    client, collection = mongo

    hidden = _deadline(
        "deadline-hidden-empty",
        "matter-hidden-empty",
        days=1,
    )

    with client.start_session() as session:
        with session.start_transaction():
            _persist(
                collection,
                session,
                hidden,
            )

    service = LegalTemporalOperationsReadService(
        deadline_collection=collection
    )

    with client.start_session() as session:
        with session.start_transaction():
            projection = service.project(
                productive_work=_productive(),
                session=session,
            )

            assert projection.visible_matter_ids == ()
            assert projection.rows == ()


def test_real_mongo_inactive_transaction_rejected_before_read(
    mongo: tuple[MongoClient[Any], Any],
) -> None:
    client, collection = mongo

    service = LegalTemporalOperationsReadService(
        deadline_collection=collection
    )

    with client.start_session() as session:
        assert session.in_transaction is False

        with pytest.raises(
            LegalTemporalOperationsReadServiceTransactionRequiredError,
            match="TEMPORAL_READ_TRANSACTION_REQUIRED",
        ):
            service.project(
                productive_work=_productive(
                    assigned=(
                        _work(
                            "work-a",
                            "matter-a",
                        ),
                    )
                ),
                session=session,
            )


def test_real_mongo_registry_indexes_remain_existing_deadline_indexes_only(
    mongo: tuple[MongoClient[Any], Any],
) -> None:
    _client, collection = mongo

    names = set(
        collection.index_information()
    )

    assert names == {
        "_id_",
        deadline_registry.TENANT_DEADLINE_UNIQUE_INDEX,
        deadline_registry.MATTER_DEADLINE_INDEX,
        deadline_registry.MATTER_DUE_INDEX,
        deadline_registry.MATTER_STATUS_DUE_INDEX,
    }

    assert not any(
        "ttl" in name.lower()
        for name in names
    )


# AUTHORITY BOUNDARY:
# Real-Mongo read certificate only.
# No new persistence, authority, visibility or financial capability.
