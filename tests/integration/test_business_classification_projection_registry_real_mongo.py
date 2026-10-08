"""WILSY OS — Business Classification Projection Registry real-Mongo certificate.

TITLE: Business Classification Projection Registry Real Mongo Certificate
VERSION: v1.0.0-BUSINESS-CLASSIFICATION-PROJECTION-REGISTRY-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Certify the immutable BusinessClassificationProjection registry against a
    real loopback MongoDB replica set using caller-owned transactions and a
    UUID-isolated disposable database.

DATABASE BOUNDARY:
- mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS only.
- UUID-isolated disposable database only.
- Database dropped in fixture finalization.
- Never production database state.

AUTHORITY BOUNDARY:
- Business classification truth only.
- Snapshot dependency is read-only during projection operations.
- No hierarchy/correspondence dependency.
- No entitlement, authorization, activation, AI-execution or financial authority.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import hashlib
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from tools.eos.saas.business_classification_projection_registry import (
    COLLECTION_NAME as PROJECTION_COLLECTION_NAME,
    BusinessClassificationProjectionRegistry,
    BusinessClassificationProjectionRegistryError,
)
from tools.eos.saas.domain.business_classification_projection import (
    BusinessActivity,
    BusinessActivityConfirmation,
    BusinessActivityRole,
    BusinessClassificationEvidence,
    BusinessClassificationProjection,
    BusinessClassificationReference,
    BusinessClassificationSourceKind,
)
from tools.eos.saas.domain.official_taxonomy_snapshot import (
    OfficialTaxonomyArtifactKind,
    OfficialTaxonomySnapshot,
    OfficialTaxonomySourceArtifact,
)
from tools.eos.saas.official_taxonomy_snapshot_registry import (
    COLLECTION_NAME as SNAPSHOT_COLLECTION_NAME,
    OfficialTaxonomySnapshotRegistry,
)


MONGO_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

NOW = datetime(
    2026,
    10,
    8,
    8,
    0,
    tzinfo=timezone.utc,
)

PROFILE_DIGEST_A = hashlib.sha3_512(
    b"tenant-profile-a"
).hexdigest()

PROFILE_DIGEST_B = hashlib.sha3_512(
    b"tenant-profile-b"
).hexdigest()

EVIDENCE_DIGEST_A = hashlib.sha3_512(
    b"classification-evidence-a"
).hexdigest()


def artifact(
    artifact_id: str = "STRUCTURE",
) -> OfficialTaxonomySourceArtifact:
    """Build one immutable official taxonomy source artifact."""
    return OfficialTaxonomySourceArtifact(
        artifact_id=artifact_id,
        kind=OfficialTaxonomyArtifactKind.STRUCTURE,
        source_reference=(
            "https://example.invalid/"
            + artifact_id.lower()
            + ".csv"
        ),
        media_type="text/csv",
        language_tag="en",
        source_digest=hashlib.sha3_512(
            artifact_id.encode("utf-8")
        ).hexdigest(),
        size_bytes=123,
        retrieved_at=datetime(
            2026,
            10,
            8,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        rights_reference="official publisher terms",
    )


def taxonomy_snapshot(
    *,
    snapshot_id: str = "SNAPSHOT-A",
    scheme_id: str = "ISIC",
    scheme_version: str = "REV5",
    jurisdiction: str = "GLOBAL",
    artifact_id: str = "STRUCTURE",
) -> OfficialTaxonomySnapshot:
    """Build one authoritative committed taxonomy snapshot."""
    return OfficialTaxonomySnapshot(
        snapshot_id=snapshot_id,
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        publisher="United Nations",
        jurisdiction=jurisdiction,
        publisher_status="official",
        release_date=date(
            2025,
            1,
            1,
        ),
        effective_from=date(
            2025,
            1,
            1,
        ),
        effective_until=None,
        ingested_at=datetime(
            2026,
            10,
            8,
            0,
            1,
            tzinfo=timezone.utc,
        ),
        source_artifacts=(
            artifact(
                artifact_id
            ),
        ),
        supersedes_snapshot_id=None,
    )


def evidence(
    evidence_id: str = "EVIDENCE-1",
) -> BusinessClassificationEvidence:
    """Build one immutable classification evidence value."""
    return BusinessClassificationEvidence(
        evidence_id=evidence_id,
        source_kind=(
            BusinessClassificationSourceKind.TENANT_DECLARATION
        ),
        source_reference="tenant-profile:industry",
        observed_at=NOW,
        source_digest=EVIDENCE_DIGEST_A,
    )


def classification(
    authoritative: OfficialTaxonomySnapshot,
    *,
    code: str = "TEST-CODE-A",
    title: str = "Synthetic certificate activity",
    snapshot_id: str | None = None,
    snapshot_digest: str | None = None,
    scheme_id: str | None = None,
    scheme_version: str | None = None,
    jurisdiction: str | None = None,
) -> BusinessClassificationReference:
    """Bind one captured classification to authoritative snapshot coordinates."""
    return BusinessClassificationReference(
        scheme_id=(
            authoritative.scheme_id
            if scheme_id is None
            else scheme_id
        ),
        scheme_version=(
            authoritative.scheme_version
            if scheme_version is None
            else scheme_version
        ),
        code=code,
        title=title,
        jurisdiction=(
            authoritative.jurisdiction
            if jurisdiction is None
            else jurisdiction
        ),
        taxonomy_snapshot_id=(
            authoritative.snapshot_id
            if snapshot_id is None
            else snapshot_id
        ),
        taxonomy_snapshot_digest=(
            authoritative.snapshot_digest
            if snapshot_digest is None
            else snapshot_digest
        ),
    )


def activity(
    authoritative: OfficialTaxonomySnapshot,
    *,
    classifications: tuple[
        BusinessClassificationReference,
        ...,
    ] | None = None,
) -> BusinessActivity:
    """Build one primary classified business activity."""
    return BusinessActivity(
        activity_id="ACTIVITY-1",
        role=BusinessActivityRole.PRIMARY,
        description="Synthetic business activity",
        confirmation=(
            BusinessActivityConfirmation.CONFIRMED
        ),
        confidence_basis_points=9500,
        evidence_refs=(
            "EVIDENCE-1",
        ),
        classifications=(
            classifications
            if classifications is not None
            else (
                classification(
                    authoritative
                ),
            )
        ),
    )


def projection(
    authoritative: OfficialTaxonomySnapshot,
    *,
    tenant_id: str = "tenant-a",
    projection_id: str = "PROJECTION-1",
    revision: int = 1,
    source_profile_digest: str = PROFILE_DIGEST_A,
    supersedes_projection_id: str | None = None,
    classifications: tuple[
        BusinessClassificationReference,
        ...,
    ] | None = None,
) -> BusinessClassificationProjection:
    """Build one immutable tenant-bound classification projection."""
    return BusinessClassificationProjection(
        projection_id=projection_id,
        tenant_id=tenant_id,
        revision=revision,
        source_profile_digest=source_profile_digest,
        evidences=(
            evidence(),
        ),
        activities=(
            activity(
                authoritative,
                classifications=classifications,
            ),
        ),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=supersedes_projection_id,
    )


class CountingSnapshotRegistry:
    """Read-only wrapper proving transaction rejection happens before reads."""

    def __init__(
        self,
        registry: OfficialTaxonomySnapshotRegistry,
    ) -> None:
        self._registry = registry
        self.get_calls = 0
        self.digest_calls = 0

    def get(
        self,
        snapshot_id: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomySnapshot | None:
        self.get_calls += 1

        return self._registry.get(
            snapshot_id,
            session=session,
        )

    def get_by_digest(
        self,
        snapshot_digest: str,
        *,
        session: Any = None,
    ) -> OfficialTaxonomySnapshot | None:
        self.digest_calls += 1

        return self._registry.get_by_digest(
            snapshot_digest,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Database[Any],
        Collection[Any],
        Collection[Any],
        OfficialTaxonomySnapshotRegistry,
        BusinessClassificationProjectionRegistry,
    ]
]:
    """Provide one UUID-isolated real-Mongo dependency chain per test."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    client.admin.command(
        "ping"
    )

    database_name = (
        "wilsy_busclass_cert_"
        + uuid.uuid4().hex
    )

    database = client[
        database_name
    ]

    snapshot_collection = database[
        SNAPSHOT_COLLECTION_NAME
    ]

    projection_collection = database[
        PROJECTION_COLLECTION_NAME
    ]

    snapshot_registry = (
        OfficialTaxonomySnapshotRegistry(
            snapshot_collection
        )
    )

    snapshot_registry.ensure_indexes()

    BusinessClassificationProjectionRegistry.ensure_indexes(
        projection_collection
    )

    projection_registry = (
        BusinessClassificationProjectionRegistry(
            projection_collection,
            snapshot_registry=snapshot_registry,
        )
    )

    try:
        yield (
            client,
            database,
            snapshot_collection,
            projection_collection,
            snapshot_registry,
            projection_registry,
        )
    finally:
        client.drop_database(
            database_name
        )
        client.close()


def persist_snapshot(
    client: MongoClient[Any],
    registry: OfficialTaxonomySnapshotRegistry,
    value: OfficialTaxonomySnapshot,
) -> None:
    """Commit one authoritative Snapshot before projection operations."""
    with client.start_session() as session:
        with session.start_transaction():
            registry.create(
                value,
                session=session,
            )


def persist_projection(
    client: MongoClient[Any],
    registry: BusinessClassificationProjectionRegistry,
    value: BusinessClassificationProjection,
) -> BusinessClassificationProjection:
    """Commit one immutable projection using a caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.create(
                value,
                session=session,
            )


def test_real_indexes_exact_and_no_ttl(
    mongo_context: Any,
) -> None:
    (
        _client,
        _database,
        _snapshot_collection,
        projection_collection,
        _snapshot_registry,
        _projection_registry,
    ) = mongo_context

    indexes = {
        entry["name"]: entry
        for entry in projection_collection.list_indexes()
    }

    assert set(
        indexes
    ) == {
        "_id_",
        "business_classification_projection_id_unique",
        "business_classification_projection_fingerprint_unique",
        "business_classification_tenant_revision_unique",
        "business_classification_tenant_effective_from",
        "business_classification_tenant_supersedes",
    }

    assert list(
        indexes[
            "business_classification_projection_id_unique"
        ]["key"].items()
    ) == [
        (
            "projection_id",
            1,
        )
    ]

    assert list(
        indexes[
            "business_classification_projection_fingerprint_unique"
        ]["key"].items()
    ) == [
        (
            "fingerprint",
            1,
        )
    ]

    assert list(
        indexes[
            "business_classification_tenant_revision_unique"
        ]["key"].items()
    ) == [
        (
            "tenant_id",
            1,
        ),
        (
            "revision",
            1,
        ),
    ]

    assert (
        indexes[
            "business_classification_projection_id_unique"
        ].get("unique")
        is True
    )

    assert (
        indexes[
            "business_classification_projection_fingerprint_unique"
        ].get("unique")
        is True
    )

    assert (
        indexes[
            "business_classification_tenant_revision_unique"
        ].get("unique")
        is True
    )

    assert all(
        "expireAfterSeconds"
        not in entry
        for entry in indexes.values()
    )


def test_missing_session_rejected_before_snapshot_read_or_projection_write(
    mongo_context: Any,
) -> None:
    (
        _client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        _projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    counting = CountingSnapshotRegistry(
        snapshot_registry
    )

    registry = BusinessClassificationProjectionRegistry(
        projection_collection,
        snapshot_registry=counting,
    )

    candidate = projection(
        authoritative
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create(
            candidate,
            session=None,
        )

    assert counting.get_calls == 0
    assert counting.digest_calls == 0
    assert projection_collection.count_documents({}) == 0


def test_inactive_transaction_rejected_before_snapshot_read_or_projection_write(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        _projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    counting = CountingSnapshotRegistry(
        snapshot_registry
    )

    registry = BusinessClassificationProjectionRegistry(
        projection_collection,
        snapshot_registry=counting,
    )

    candidate = projection(
        authoritative
    )

    with client.start_session() as session:
        assert not session.in_transaction

        with pytest.raises(
            BusinessClassificationProjectionRegistryError,
            match="ACTIVE_TRANSACTION_REQUIRED",
        ):
            registry.create(
                candidate,
                session=session,
            )

    assert counting.get_calls == 0
    assert counting.digest_calls == 0
    assert projection_collection.count_documents({}) == 0


def test_committed_snapshot_to_projection_roundtrip(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = projection(
        authoritative
    )

    observed = persist_projection(
        client,
        projection_registry,
        candidate,
    )

    assert observed == candidate
    assert projection_collection.count_documents({}) == 1
    assert projection_registry.get(
        candidate.projection_id
    ) == candidate
    assert projection_registry.get_by_fingerprint(
        candidate.fingerprint
    ) == candidate
    assert projection_registry.get_by_tenant_revision(
        candidate.tenant_id,
        candidate.revision,
    ) == candidate


def test_aborted_projection_insert_leaves_zero_rows(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = projection(
        authoritative
    )

    with client.start_session() as session:
        session.start_transaction()

        observed = projection_registry.create(
            candidate,
            session=session,
        )

        assert observed == candidate

        session.abort_transaction()

    assert projection_collection.count_documents({}) == 0


def test_exact_replay_is_idempotent(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = projection(
        authoritative
    )

    first = persist_projection(
        client,
        projection_registry,
        candidate,
    )

    replay = persist_projection(
        client,
        projection_registry,
        candidate,
    )

    assert first == candidate
    assert replay == candidate
    assert projection_collection.count_documents({}) == 1


def test_same_projection_id_different_truth_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    durable = projection(
        authoritative
    )

    persist_projection(
        client,
        projection_registry,
        durable,
    )

    conflicting = projection(
        authoritative,
        source_profile_digest=PROFILE_DIGEST_B,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessClassificationProjectionRegistryError,
                match="IDENTITY_CONFLICT",
            ):
                projection_registry.create(
                    conflicting,
                    session=session,
                )

    assert projection_collection.count_documents({}) == 1


def test_same_fingerprint_different_identity_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = projection(
        authoritative,
        projection_id="PROJECTION-CANDIDATE",
    )

    corrupt_collision = candidate.to_dict()
    corrupt_collision[
        "projection_id"
    ] = "PROJECTION-CORRUPT-COLLISION"

    projection_collection.insert_one(
        corrupt_collision
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessClassificationProjectionRegistryError,
                match="FINGERPRINT_CONFLICT",
            ):
                projection_registry.create(
                    candidate,
                    session=session,
                )

    assert projection_collection.count_documents({}) == 1


def test_same_tenant_revision_different_truth_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    durable = projection(
        authoritative,
        projection_id="PROJECTION-A",
    )

    persist_projection(
        client,
        projection_registry,
        durable,
    )

    conflicting = projection(
        authoritative,
        projection_id="PROJECTION-B",
        source_profile_digest=PROFILE_DIGEST_B,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessClassificationProjectionRegistryError,
                match="TENANT_REVISION_CONFLICT",
            ):
                projection_registry.create(
                    conflicting,
                    session=session,
                )

    assert projection_collection.count_documents({}) == 1


def test_missing_snapshot_binding_rejected_before_projection_insert(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        _snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    candidate = projection(
        authoritative
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessClassificationProjectionRegistryError,
                match="SNAPSHOT_BINDING_MISSING",
            ):
                projection_registry.create(
                    candidate,
                    session=session,
                )

    assert projection_collection.count_documents({}) == 0


def test_snapshot_id_digest_binding_conflict_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    first = taxonomy_snapshot(
        snapshot_id="SNAPSHOT-A",
        artifact_id="STRUCTURE-A",
    )

    second = taxonomy_snapshot(
        snapshot_id="SNAPSHOT-B",
        artifact_id="STRUCTURE-B",
    )

    persist_snapshot(
        client,
        snapshot_registry,
        first,
    )

    persist_snapshot(
        client,
        snapshot_registry,
        second,
    )

    conflicting_ref = classification(
        first,
        snapshot_id=first.snapshot_id,
        snapshot_digest=second.snapshot_digest,
    )

    candidate = projection(
        first,
        classifications=(
            conflicting_ref,
        ),
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessClassificationProjectionRegistryError,
                match="SNAPSHOT_BINDING_CONFLICT",
            ):
                projection_registry.create(
                    candidate,
                    session=session,
                )

    assert projection_collection.count_documents({}) == 0


def test_snapshot_scheme_version_jurisdiction_mismatch_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    cases = (
        {
            "scheme_id": "NAICS",
        },
        {
            "scheme_version": "REV4",
        },
        {
            "jurisdiction": "ZA",
        },
    )

    for number, overrides in enumerate(
        cases,
        1,
    ):
        reference = classification(
            authoritative,
            **overrides,
        )

        candidate = projection(
            authoritative,
            projection_id=(
                "PROJECTION-MISMATCH-"
                + str(number)
            ),
            classifications=(
                reference,
            ),
        )

        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(
                    BusinessClassificationProjectionRegistryError
                ):
                    projection_registry.create(
                        candidate,
                        session=session,
                    )

    assert projection_collection.count_documents({}) == 0


def test_later_revision_requires_existing_same_tenant_superseded_projection(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    prior = projection(
        authoritative,
        projection_id="PROJECTION-1",
        revision=1,
    )

    persist_projection(
        client,
        projection_registry,
        prior,
    )

    later = projection(
        authoritative,
        projection_id="PROJECTION-7",
        revision=7,
        supersedes_projection_id=prior.projection_id,
        source_profile_digest=PROFILE_DIGEST_B,
    )

    observed = persist_projection(
        client,
        projection_registry,
        later,
    )

    assert observed == later
    assert projection_collection.count_documents({}) == 2
    assert projection_registry.get(
        later.projection_id
    ) == later


def test_cross_tenant_supersession_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    prior = projection(
        authoritative,
        tenant_id="tenant-b",
        projection_id="TENANT-B-PROJECTION",
        revision=1,
    )

    persist_projection(
        client,
        projection_registry,
        prior,
    )

    candidate = projection(
        authoritative,
        tenant_id="tenant-a",
        projection_id="TENANT-A-PROJECTION",
        revision=2,
        supersedes_projection_id=prior.projection_id,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessClassificationProjectionRegistryError,
                match="CROSS_TENANT_SUPERSESSION_FORBIDDEN",
            ):
                projection_registry.create(
                    candidate,
                    session=session,
                )

    assert projection_collection.count_documents({}) == 1


def test_corrupt_superseded_projection_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    prior = projection(
        authoritative,
        projection_id="PROJECTION-PRIOR",
    )

    persist_projection(
        client,
        projection_registry,
        prior,
    )

    projection_collection.update_one(
        {
            "projection_id":
                prior.projection_id,
        },
        {
            "$set": {
                "unexpected_corruption":
                    True,
            },
        },
    )

    candidate = projection(
        authoritative,
        projection_id="PROJECTION-NEXT",
        revision=2,
        supersedes_projection_id=prior.projection_id,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessClassificationProjectionRegistryError,
                match="PERSISTED_RECORD_INVALID",
            ):
                projection_registry.create(
                    candidate,
                    session=session,
                )

    assert projection_collection.count_documents({}) == 1


def test_tenant_history_read_is_revision_ordered(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        _projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    first = projection(
        authoritative,
        projection_id="PROJECTION-1",
        revision=1,
    )

    second = projection(
        authoritative,
        projection_id="PROJECTION-2",
        revision=2,
        supersedes_projection_id=first.projection_id,
        source_profile_digest=PROFILE_DIGEST_B,
    )

    third = projection(
        authoritative,
        projection_id="PROJECTION-5",
        revision=5,
        supersedes_projection_id=second.projection_id,
        source_profile_digest=hashlib.sha3_512(
            b"tenant-profile-c"
        ).hexdigest(),
    )

    persist_projection(
        client,
        projection_registry,
        first,
    )

    persist_projection(
        client,
        projection_registry,
        second,
    )

    persist_projection(
        client,
        projection_registry,
        third,
    )

    assert projection_registry.get_by_tenant(
        "tenant-a"
    ) == (
        first,
        second,
        third,
    )


def test_corrupt_persisted_projection_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = projection(
        authoritative
    )

    persist_projection(
        client,
        projection_registry,
        candidate,
    )

    projection_collection.update_one(
        {
            "projection_id":
                candidate.projection_id,
        },
        {
            "$set": {
                "fingerprint":
                    "0" * 128,
            },
        },
    )

    with pytest.raises(
        BusinessClassificationProjectionRegistryError,
        match="PERSISTED_RECORD_INVALID",
    ):
        projection_registry.get(
            candidate.projection_id
        )


def test_concurrent_identical_projection_create_converges_to_one_durable_row(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    candidate = projection(
        authoritative
    )

    barrier = Barrier(2)

    def worker() -> tuple[
        str,
        str,
    ]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    barrier.wait()

                    observed = projection_registry.create(
                        candidate,
                        session=session,
                    )

            return (
                "success",
                observed.projection_id,
            )
        except (
            BusinessClassificationProjectionRegistryError,
            PyMongoError,
        ) as error:
            return (
                "failure",
                type(error).__name__,
            )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        results = list(
            executor.map(
                lambda _index: worker(),
                range(2),
            )
        )

    successes = [
        value
        for status, value
        in results
        if status == "success"
    ]

    assert len(successes) >= 1

    assert projection_collection.count_documents({}) == 1

    durable = projection_registry.get(
        candidate.projection_id
    )

    assert durable == candidate


def test_concurrent_conflicting_projection_create_yields_one_durable_truth(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _snapshot_collection,
        projection_collection,
        snapshot_registry,
        projection_registry,
    ) = mongo_context

    authoritative = taxonomy_snapshot()

    persist_snapshot(
        client,
        snapshot_registry,
        authoritative,
    )

    first = projection(
        authoritative,
        projection_id="PROJECTION-A",
        source_profile_digest=PROFILE_DIGEST_A,
    )

    second = projection(
        authoritative,
        projection_id="PROJECTION-B",
        source_profile_digest=PROFILE_DIGEST_B,
    )

    barrier = Barrier(2)

    def worker(
        candidate: BusinessClassificationProjection,
    ) -> tuple[
        str,
        str,
    ]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    barrier.wait()

                    observed = projection_registry.create(
                        candidate,
                        session=session,
                    )

            return (
                "success",
                observed.projection_id,
            )
        except (
            BusinessClassificationProjectionRegistryError,
            PyMongoError,
        ) as error:
            return (
                "failure",
                type(error).__name__,
            )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        futures = [
            executor.submit(
                worker,
                first,
            ),
            executor.submit(
                worker,
                second,
            ),
        ]

        results = [
            future.result()
            for future in futures
        ]

    successes = [
        value
        for status, value
        in results
        if status == "success"
    ]

    failures = [
        value
        for status, value
        in results
        if status == "failure"
    ]

    assert len(successes) == 1
    assert len(failures) == 1

    assert projection_collection.count_documents({}) == 1

    durable = projection_collection.find_one(
        {}
    )

    assert durable is not None

    assert durable[
        "projection_id"
    ] in {
        first.projection_id,
        second.projection_id,
    }


# ARTIFACT: test_business_classification_projection_registry_real_mongo.py
