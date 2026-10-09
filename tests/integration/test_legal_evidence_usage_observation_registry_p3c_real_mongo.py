"""Actual-Mongo certificate for complete Legal Evidence P3C usage retrieval.

TITLE: Legal Evidence P3C Complete Usage Retrieval Actual-Mongo Certificate
VERSION: v1.0.0-L10A2Q-P3C-LEGAL-EVIDENCE-USAGE-WINDOW-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Certify complete tenant-scoped Legal Evidence usage-window derivation against
    a writable Mongo replica set using real persisted P3 observations and one
    caller-owned snapshot transaction.

EPITOME:
    DURABLE P3 OBSERVATIONS
    -> EXHAUSTIVE TENANT RETRIEVAL
    -> STRICT HYDRATION
    -> COMPLETE P3C USAGE WINDOW
    != REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMISSION

COMPLETENESS POSTURE:
    The P3C read must inspect every persisted row for the requested tenant before
    as_of/month/document accounting. Future and prior corrupt tenant rows reject
    rather than disappearing behind a temporal Mongo predicate.

TENANT POSTURE:
    Neighboring tenant observations are absent from the requested tenant window.

TRANSACTION POSTURE:
    Caller owns start/commit/abort. The retrieval seam requires and preserves one
    already-active Mongo transaction.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_content import (
    register_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    LegalEvidenceUsageObservation,
    observe_legal_evidence_usage,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_window import (
    LegalEvidenceUsageWindow,
)
from tools.eos.legal_operations.registry.legal_evidence_usage_observation_registry import (
    COLLECTION,
    LegalEvidenceUsageObservationRegistry,
    LegalEvidenceUsageObservationRegistryError,
    ensure_indexes,
)


MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

AS_OF = datetime(2026, 9, 30, 18, 45, tzinfo=timezone.utc)
FP = "a" * 128


@pytest.fixture()
def mongo_context() -> Iterator[
    tuple[MongoClient[Any], Any, Any]
]:
    """Yield one UUID-isolated majority/journal P3C certification collection."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )
    client.admin.command("ping")

    database = client[
        f"wilsy_l10a2q_p3c_usage_cert_{uuid4().hex}"
    ]

    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(
            "majority",
            j=True,
        ),
        read_concern=ReadConcern("majority"),
    )
    ensure_indexes(collection)

    try:
        yield client, database, collection
    finally:
        client.drop_database(database.name)
        client.close()


def _observation(
    *,
    tenant_id: str = "tenant-p3c-real",
    document_id: str,
    occurred_at: datetime,
    content: bytes,
) -> LegalEvidenceUsageObservation:
    canonical = register_legal_evidence_content(
        tenant_id=tenant_id,
        case_matter_id="matter-p3c-real",
        document_id=document_id,
        media_type="application/pdf",
        original_filename=f"{document_id}.pdf",
        content=content,
        source_evidence_reference=(
            f"source:{tenant_id}:{document_id}:{occurred_at.isoformat()}"
        ),
        source_evidence_fingerprint=FP,
        registered_at=occurred_at,
    )
    return observe_legal_evidence_usage(
        content=canonical,
    )


def _persist(
    *,
    client: MongoClient[Any],
    registry: LegalEvidenceUsageObservationRegistry,
    observation: LegalEvidenceUsageObservation,
    key: str,
) -> None:
    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(
            observation,
            idempotency_key=key,
            session=session,
        )
        session.commit_transaction()


def test_real_complete_window_preserves_three_metric_scopes_and_tenant_isolation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalEvidenceUsageObservationRegistry(collection)

    prior_target = _observation(
        document_id="document-target",
        occurred_at=datetime(2026, 8, 20, 9, tzinfo=timezone.utc),
        content=b"prior-target-real",
    )
    current_target = _observation(
        document_id="document-target",
        occurred_at=datetime(2026, 9, 10, 9, tzinfo=timezone.utc),
        content=b"current-target-real",
    )
    current_other = _observation(
        document_id="document-other",
        occurred_at=datetime(2026, 9, 12, 9, tzinfo=timezone.utc),
        content=b"current-other-real",
    )
    future_target = _observation(
        document_id="document-target",
        occurred_at=datetime(2026, 10, 1, 9, tzinfo=timezone.utc),
        content=b"future-target-real",
    )
    neighbor = _observation(
        tenant_id="tenant-p3c-real-neighbor",
        document_id="document-target",
        occurred_at=datetime(2026, 9, 11, 9, tzinfo=timezone.utc),
        content=b"neighbor-real",
    )

    for key, item in (
        ("prior-target", prior_target),
        ("current-target", current_target),
        ("current-other", current_other),
        ("future-target", future_target),
        ("neighbor", neighbor),
    ):
        _persist(
            client=client,
            registry=registry,
            observation=item,
            key=key,
        )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        window = registry.get_complete_window_for_p4(
            tenant_id="tenant-p3c-real",
            document_id="document-target",
            as_of=AS_OF,
            session=session,
        )

        assert session.in_transaction is True
        assert type(window) is LegalEvidenceUsageWindow

        assert window.tenant_observation_count == 3
        assert window.tenant_storage_bytes_added == (
            prior_target.storage_bytes_added
            + current_target.storage_bytes_added
            + current_other.storage_bytes_added
        )

        assert window.monthly_observation_count == 2
        assert window.monthly_ingress_bytes_added == (
            current_target.monthly_ingress_bytes
            + current_other.monthly_ingress_bytes
        )

        assert window.document_observation_count == 2
        assert window.document_versions_added == (
            prior_target.document_versions_added
            + current_target.document_versions_added
        )

        assert window.tenant_id == "tenant-p3c-real"
        assert window.document_id == "document-target"
        assert window.as_of == AS_OF
        assert window.monthly_window_start == datetime(
            2026,
            9,
            1,
            tzinfo=timezone.utc,
        )
        assert window.monthly_window_end == AS_OF
        assert len(window.source_observation_set_fingerprint) == 128

        session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id": "tenant-p3c-real",
        }
    ) == 4
    assert collection.count_documents(
        {
            "tenant_id": "tenant-p3c-real-neighbor",
        }
    ) == 1


def test_real_legitimate_empty_window_is_explicit_complete_evidence(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalEvidenceUsageObservationRegistry(collection)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        window = registry.get_complete_window_for_p4(
            tenant_id="tenant-p3c-real-empty",
            document_id="document-empty",
            as_of=AS_OF,
            session=session,
        )

        assert session.in_transaction is True
        assert window.tenant_observation_count == 0
        assert window.monthly_observation_count == 0
        assert window.document_observation_count == 0
        assert window.tenant_storage_bytes_added == 0
        assert window.monthly_ingress_bytes_added == 0
        assert window.document_versions_added == 0
        assert len(window.source_observation_set_fingerprint) == 128

        session.abort_transaction()

    assert collection.count_documents({}) == 0


@pytest.mark.parametrize(
    ("occurred_at", "document_id", "key"),
    (
        (
            datetime(2026, 8, 1, tzinfo=timezone.utc),
            "document-prior-corrupt",
            "prior-corrupt",
        ),
        (
            datetime(2026, 10, 5, tzinfo=timezone.utc),
            "document-future-corrupt",
            "future-corrupt",
        ),
    ),
)
def test_real_corrupt_prior_or_future_tenant_row_cannot_hide_from_complete_read(
    mongo_context: tuple[MongoClient[Any], Any, Any],
    occurred_at: datetime,
    document_id: str,
    key: str,
) -> None:
    client, _, collection = mongo_context
    registry = LegalEvidenceUsageObservationRegistry(collection)

    observation = _observation(
        document_id=document_id,
        occurred_at=occurred_at,
        content=key.encode("utf-8"),
    )

    _persist(
        client=client,
        registry=registry,
        observation=observation,
        key=key,
    )

    result = collection.update_one(
        {
            "tenant_id": observation.tenant_id,
            "usage_observation_id": observation.usage_observation_id,
        },
        {
            "$set": {
                "occurred_at": "not-a-timestamp",
            }
        },
    )
    assert result.matched_count == 1
    assert result.modified_count == 1

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        with pytest.raises(
            LegalEvidenceUsageObservationRegistryError,
            match="L10A2Q_P3B_CORRUPT_OBSERVATION",
        ):
            registry.get_complete_window_for_p4(
                tenant_id=observation.tenant_id,
                document_id=document_id,
                as_of=AS_OF,
                session=session,
            )

        session.abort_transaction()


def test_real_source_set_fingerprint_is_deterministic_for_same_snapshot(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalEvidenceUsageObservationRegistry(collection)

    early = _observation(
        document_id="document-deterministic",
        occurred_at=datetime(2026, 9, 2, tzinfo=timezone.utc),
        content=b"early-real",
    )
    late = _observation(
        document_id="document-deterministic",
        occurred_at=datetime(2026, 9, 20, tzinfo=timezone.utc),
        content=b"late-real",
    )

    _persist(
        client=client,
        registry=registry,
        observation=late,
        key="late-real",
    )
    _persist(
        client=client,
        registry=registry,
        observation=early,
        key="early-real",
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        first = registry.get_complete_window_for_p4(
            tenant_id=early.tenant_id,
            document_id=early.document_id,
            as_of=AS_OF,
            session=session,
        )
        second = registry.get_complete_window_for_p4(
            tenant_id=early.tenant_id,
            document_id=early.document_id,
            as_of=AS_OF,
            session=session,
        )

        assert first == second
        assert (
            first.source_observation_set_fingerprint
            == second.source_observation_set_fingerprint
        )
        assert first.fingerprint == second.fingerprint

        session.abort_transaction()


# ARTIFACT: test_legal_evidence_usage_observation_registry_p3c_real_mongo.py
# VERSION: v1.0.0-L10A2Q-P3C-LEGAL-EVIDENCE-USAGE-WINDOW-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual-Mongo complete usage aggregation evidence only
# COMPLETENESS POSTURE: all tenant rows hydrated before temporal accounting
# TENANT POSTURE: exact tenant/document scope; neighboring tenant excluded
# TRANSACTION POSTURE: caller owns active snapshot transaction
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
