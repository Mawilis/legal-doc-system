"""WILSY OS — Business Classification Projection V2 real-Mongo certificate.

TITLE: Business Classification Projection V2 Registry Real-Mongo Certificate
VERSION: v2.0.0-BUSINESS-CLASSIFICATION-PROJECTION-V2-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Certify the Business Identity -> Classification V2 persistence chain
    against a real disposable MongoDB replica-set database.

BOUNDARY:
- UUID-isolated disposable database only.
- Caller owns every session and transaction.
- Business Identity and taxonomy dependencies are read-only.
- V1 collection remains separate and untouched.
- No latest/current, entitlement, authorization, activation, or financial
  authority is created by this certificate.
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import threading
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from tools.eos.saas.business_classification_projection_registry import (
    COLLECTION_NAME as V1_COLLECTION_NAME,
)
from tools.eos.saas.business_classification_projection_v2_registry import (
    COLLECTION_NAME as V2_COLLECTION_NAME,
    BusinessClassificationProjectionV2Registry,
    BusinessClassificationProjectionV2RegistryError,
)
from tools.eos.saas.business_identity_registry import (
    COLLECTION_NAME as BUSINESS_IDENTITY_COLLECTION_NAME,
    BusinessIdentityRegistry,
)
from tools.eos.saas.domain.business_classification_projection import (
    BusinessActivity,
    BusinessActivityConfirmation,
    BusinessActivityRole,
    BusinessClassificationEvidence,
    BusinessClassificationReference,
    BusinessClassificationSourceKind,
)
from tools.eos.saas.domain.business_classification_projection_v2 import (
    BusinessClassificationProjectionV2,
)
from tools.eos.saas.domain.business_identity import (
    BusinessIdentity,
)
from tools.eos.saas.official_taxonomy_snapshot_registry import (
    COLLECTION_NAME as SNAPSHOT_COLLECTION_NAME,
    OfficialTaxonomySnapshotRegistry,
)


MONGO_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

DATABASE_PREFIX = (
    "wilsy_busclass_v2_cert_"
)

NOW = datetime(
    2026,
    10,
    8,
    18,
    0,
    tzinfo=timezone.utc,
)

PROFILE_DIGEST = hashlib.sha3_512(
    b"business-classification-v2-profile"
).hexdigest()

EVIDENCE_DIGEST = hashlib.sha3_512(
    b"business-classification-v2-evidence"
).hexdigest()

SNAPSHOT_DOCUMENT = {'schema_version': 'wilsy.official.taxonomy.snapshot.v1', 'snapshot_id': 'SNAPSHOT-001', 'scheme_id': 'ISIC', 'scheme_version': 'REV5', 'publisher': 'United Nations', 'jurisdiction': 'GLOBAL', 'publisher_status': 'official', 'release_date': '2025-01-01', 'effective_from': '2025-01-01', 'effective_until': None, 'ingested_at': '2026-10-08T00:01:00+00:00', 'source_artifacts': [{'artifact_id': 'STRUCTURE', 'kind': 'structure', 'source_reference': 'https://example.invalid/structure.csv', 'media_type': 'text/csv', 'language_tag': 'en', 'source_digest': 'b0d86ed69449c061484b797ada72310cd26a1cc4b2fb615c24a5f320eddfb65787608140dd680f16f003dc282ec59a8800ebef8c6ced6a08f0f7b47f89f08471', 'size_bytes': 123, 'retrieved_at': '2026-10-08T00:00:00+00:00', 'rights_reference': 'official publisher terms'}], 'supersedes_snapshot_id': None, 'snapshot_digest': '2594c41e1bcef87129bbf52c6cc3414e2fdb674690a087890dbab8cd13e24daa8cdb2e3cacb9b58f7a44350fa1c2da38b90556775efe43861648e6fb162ad359'}
SNAPSHOT_DIGEST = '2594c41e1bcef87129bbf52c6cc3414e2fdb674690a087890dbab8cd13e24daa8cdb2e3cacb9b58f7a44350fa1c2da38b90556775efe43861648e6fb162ad359'


class TrackingBusinessIdentityRegistry:
    """Read-only observer over the certified durable Business Identity registry."""

    def __init__(
        self,
        durable: BusinessIdentityRegistry,
    ) -> None:
        self._durable = durable
        self.revision_sessions: list[Any] = []
        self.fingerprint_sessions: list[Any] = []
        self.write_calls = 0

    def get_revision(
        self,
        business_identity_id: str,
        revision: int,
        *,
        session: Any = None,
    ) -> BusinessIdentity | None:
        self.revision_sessions.append(
            session
        )

        return self._durable.get_revision(
            business_identity_id,
            revision,
            session=session,
        )

    def get_by_fingerprint(
        self,
        identity_fingerprint: str,
        *,
        session: Any = None,
    ) -> BusinessIdentity | None:
        self.fingerprint_sessions.append(
            session
        )

        return self._durable.get_by_fingerprint(
            identity_fingerprint,
            session=session,
        )


class TrackingSnapshotRegistry:
    """Read-only observer over the certified taxonomy snapshot registry."""

    def __init__(
        self,
        durable: OfficialTaxonomySnapshotRegistry,
    ) -> None:
        self._durable = durable
        self.id_sessions: list[Any] = []
        self.digest_sessions: list[Any] = []
        self.write_calls = 0

    def get(
        self,
        snapshot_id: str,
        *,
        session: Any = None,
    ) -> Any:
        self.id_sessions.append(
            session
        )

        return self._durable.get(
            snapshot_id,
            session=session,
        )

    def get_by_digest(
        self,
        snapshot_digest: str,
        *,
        session: Any = None,
    ) -> Any:
        self.digest_sessions.append(
            session
        )

        return self._durable.get_by_digest(
            snapshot_digest,
            session=session,
        )


class RegistryBundle:
    """One isolated real-Mongo authority chain."""

    def __init__(
        self,
        *,
        client: MongoClient[Any],
        database: Database[Any],
        identity_collection: Collection[Any],
        snapshot_collection: Collection[Any],
        v1_collection: Collection[Any],
        v2_collection: Collection[Any],
        identity_registry: BusinessIdentityRegistry,
        snapshot_registry: OfficialTaxonomySnapshotRegistry,
        tracking_identity: TrackingBusinessIdentityRegistry,
        tracking_snapshot: TrackingSnapshotRegistry,
        registry: BusinessClassificationProjectionV2Registry,
    ) -> None:
        self.client = client
        self.database = database
        self.identity_collection = identity_collection
        self.snapshot_collection = snapshot_collection
        self.v1_collection = v1_collection
        self.v2_collection = v2_collection
        self.identity_registry = identity_registry
        self.snapshot_registry = snapshot_registry
        self.tracking_identity = tracking_identity
        self.tracking_snapshot = tracking_snapshot
        self.registry = registry


@contextmanager
def mongo_context() -> Iterator[RegistryBundle]:
    """Provide one UUID-isolated real-Mongo V2 dependency chain."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    client.admin.command(
        "ping"
    )

    database_name = (
        DATABASE_PREFIX
        + uuid.uuid4().hex
    )

    assert len(
        database_name
    ) < 64

    database = client[
        database_name
    ]

    identity_collection = database[
        BUSINESS_IDENTITY_COLLECTION_NAME
    ]

    snapshot_collection = database[
        SNAPSHOT_COLLECTION_NAME
    ]

    v1_collection = database[
        V1_COLLECTION_NAME
    ]

    v2_collection = database[
        V2_COLLECTION_NAME
    ]

    BusinessIdentityRegistry.ensure_indexes(
        identity_collection
    )

    OfficialTaxonomySnapshotRegistry(
        snapshot_collection
    ).ensure_indexes()

    BusinessClassificationProjectionV2Registry.ensure_indexes(
        v2_collection
    )

    # Directly seed already-certified immutable dependency truth.
    snapshot_collection.insert_one(
        deepcopy(
            SNAPSHOT_DOCUMENT
        )
    )

    identity_registry = BusinessIdentityRegistry.__new__(
        BusinessIdentityRegistry
    )

    # BusinessIdentity reads used by V2 do not require Tenant mutation.
    identity_registry._collection = identity_collection  # type: ignore[attr-defined]

    snapshot_registry = OfficialTaxonomySnapshotRegistry(
        snapshot_collection
    )

    tracking_identity = TrackingBusinessIdentityRegistry(
        identity_registry
    )

    tracking_snapshot = TrackingSnapshotRegistry(
        snapshot_registry
    )

    registry = BusinessClassificationProjectionV2Registry(
        v2_collection,
        business_identity_registry=tracking_identity,
        snapshot_registry=tracking_snapshot,
    )

    bundle = RegistryBundle(
        client=client,
        database=database,
        identity_collection=identity_collection,
        snapshot_collection=snapshot_collection,
        v1_collection=v1_collection,
        v2_collection=v2_collection,
        identity_registry=identity_registry,
        snapshot_registry=snapshot_registry,
        tracking_identity=tracking_identity,
        tracking_snapshot=tracking_snapshot,
        registry=registry,
    )

    try:
        yield bundle
    finally:
        client.drop_database(
            database_name
        )

        client.close()


def identity(
    *,
    business_identity_id: str = "BUSINESS-001",
    tenant_id: str = "tenant-a",
    revision: int = 1,
    organization_name: str = "Acme",
    legal_name: str = "Acme (Pty) Ltd",
    supersedes_revision: int | None = None,
) -> BusinessIdentity:
    """Build one immutable Business Identity revision."""
    return BusinessIdentity(
        business_identity_id=business_identity_id,
        tenant_id=tenant_id,
        revision=revision,
        organization_name=organization_name,
        legal_name=legal_name,
        created_at=NOW,
        effective_from=NOW,
        supersedes_revision=supersedes_revision,
    )


def seed_identity(
    bundle: RegistryBundle,
    value: BusinessIdentity,
) -> None:
    """Seed certified identity truth without invoking new identity authority."""
    bundle.identity_collection.insert_one(
        value.to_dict()
    )


def classification() -> BusinessClassificationReference:
    """Build one certified snapshot-bound classification reference."""
    return BusinessClassificationReference(
        scheme_id="ISIC",
        scheme_version="REV5",
        code="6201",
        title="Computer programming activities",
        jurisdiction="GLOBAL",
        taxonomy_snapshot_id="SNAPSHOT-001",
        taxonomy_snapshot_digest=SNAPSHOT_DIGEST,
    )


def evidence() -> BusinessClassificationEvidence:
    """Build one immutable evidence value."""
    return BusinessClassificationEvidence(
        evidence_id="EVIDENCE-1",
        source_kind=(
            BusinessClassificationSourceKind.TENANT_DECLARATION
        ),
        source_reference="tenant-profile:industry",
        observed_at=NOW,
        source_digest=EVIDENCE_DIGEST,
    )


def activity() -> BusinessActivity:
    """Build one immutable classified business activity."""
    return BusinessActivity(
        activity_id="ACTIVITY-1",
        role=BusinessActivityRole.PRIMARY,
        description="Synthetic business activity",
        confirmation=(
            BusinessActivityConfirmation.CONFIRMED
        ),
        confidence_basis_points=9500,
        evidence_refs=("EVIDENCE-1",),
        classifications=(classification(),),
    )


def projection(
    business: BusinessIdentity,
    *,
    projection_id: str = "PROJECTION-001",
    revision: int = 1,
    source_profile_digest: str = PROFILE_DIGEST,
    supersedes_projection_id: str | None = None,
) -> BusinessClassificationProjectionV2:
    """Build one V2 projection explicitly bound to Business Identity truth."""
    return BusinessClassificationProjectionV2(
        projection_id=projection_id,
        tenant_id=business.tenant_id,
        business_identity_id=(
            business.business_identity_id
        ),
        business_identity_revision=(
            business.revision
        ),
        business_identity_fingerprint=(
            business.identity_fingerprint
        ),
        revision=revision,
        source_profile_digest=source_profile_digest,
        evidences=(evidence(),),
        activities=(activity(),),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=supersedes_projection_id,
    )


def committed_create(
    bundle: RegistryBundle,
    value: BusinessClassificationProjectionV2,
) -> BusinessClassificationProjectionV2:
    """Create and commit one V2 projection in a caller-owned transaction."""
    with bundle.client.start_session() as session:
        session.start_transaction()

        try:
            observed = bundle.registry.create(
                value,
                session=session,
            )

            session.commit_transaction()

            return observed
        except Exception:
            if session.in_transaction:
                session.abort_transaction()
            raise


def test_real_v2_indexes_exact_and_no_ttl() -> None:
    with mongo_context() as bundle:
        indexes = {
            value["name"]: value
            for value in bundle.v2_collection.list_indexes()
        }

        expected = {
            "business_classification_v2_projection_id_unique",
            "business_classification_v2_fingerprint_unique",
            "business_classification_v2_tenant_business_revision_unique",
            "business_classification_v2_tenant_business_effective_from",
            "business_classification_v2_business_identity_binding",
            "business_classification_v2_tenant_supersedes_projection",
        }

        assert expected.issubset(
            indexes.keys()
        )

        assert indexes[
            "business_classification_v2_projection_id_unique"
        ]["unique"] is True

        assert indexes[
            "business_classification_v2_fingerprint_unique"
        ]["unique"] is True

        assert indexes[
            "business_classification_v2_tenant_business_revision_unique"
        ]["unique"] is True

        assert all(
            "expireAfterSeconds"
            not in index
            for index in indexes.values()
        )


def test_real_missing_or_inactive_transaction_rejected_before_dependency_reads() -> None:
    with mongo_context() as bundle:
        business = identity()
        seed_identity(
            bundle,
            business,
        )

        candidate = projection(
            business
        )

        with pytest.raises(
            BusinessClassificationProjectionV2RegistryError,
            match="ACTIVE_TRANSACTION_REQUIRED",
        ):
            bundle.registry.create(
                candidate,
                session=None,
            )

        with bundle.client.start_session() as session:
            with pytest.raises(
                BusinessClassificationProjectionV2RegistryError,
                match="ACTIVE_TRANSACTION_REQUIRED",
            ):
                bundle.registry.create(
                    candidate,
                    session=session,
                )

        assert bundle.tracking_identity.revision_sessions == []
        assert bundle.tracking_identity.fingerprint_sessions == []
        assert bundle.tracking_snapshot.id_sessions == []
        assert bundle.tracking_snapshot.digest_sessions == []
        assert bundle.v2_collection.count_documents({}) == 0


def test_real_business_identity_and_snapshot_reads_share_caller_session() -> None:
    with mongo_context() as bundle:
        business = identity()
        seed_identity(
            bundle,
            business,
        )

        with bundle.client.start_session() as session:
            session.start_transaction()

            bundle.registry.create(
                projection(
                    business
                ),
                session=session,
            )

            assert bundle.tracking_identity.revision_sessions == [
                session
            ]

            assert bundle.tracking_identity.fingerprint_sessions == [
                session
            ]

            assert bundle.tracking_snapshot.id_sessions == [
                session
            ]

            assert bundle.tracking_snapshot.digest_sessions == [
                session
            ]

            session.abort_transaction()

        assert bundle.v2_collection.count_documents({}) == 0


def test_real_commit_durability() -> None:
    with mongo_context() as bundle:
        business = identity()
        seed_identity(
            bundle,
            business,
        )

        candidate = projection(
            business
        )

        assert committed_create(
            bundle,
            candidate,
        ) == candidate

        durable = bundle.registry.get(
            candidate.projection_id
        )

        assert durable == candidate
        assert bundle.v2_collection.count_documents({}) == 1


def test_real_abort_zero_write() -> None:
    with mongo_context() as bundle:
        business = identity()
        seed_identity(
            bundle,
            business,
        )

        with bundle.client.start_session() as session:
            session.start_transaction()

            bundle.registry.create(
                projection(
                    business
                ),
                session=session,
            )

            assert bundle.v2_collection.count_documents(
                {},
                session=session,
            ) == 1

            session.abort_transaction()

        assert bundle.v2_collection.count_documents({}) == 0


def test_real_exact_replay() -> None:
    with mongo_context() as bundle:
        business = identity()
        seed_identity(
            bundle,
            business,
        )

        candidate = projection(
            business
        )

        committed_create(
            bundle,
            candidate,
        )

        replay = committed_create(
            bundle,
            candidate,
        )

        assert replay == candidate
        assert bundle.v2_collection.count_documents({}) == 1


def test_real_business_identity_binding_mismatch_rejected() -> None:
    with mongo_context() as bundle:
        first = identity(
            revision=1,
        )

        second = identity(
            revision=2,
            supersedes_revision=1,
        )

        seed_identity(
            bundle,
            first,
        )

        seed_identity(
            bundle,
            second,
        )

        candidate = BusinessClassificationProjectionV2(
            projection_id="MISMATCH-001",
            tenant_id=first.tenant_id,
            business_identity_id=first.business_identity_id,
            business_identity_revision=first.revision,
            business_identity_fingerprint=(
                second.identity_fingerprint
            ),
            revision=1,
            source_profile_digest=PROFILE_DIGEST,
            evidences=(evidence(),),
            activities=(activity(),),
            effective_from=NOW,
            created_at=NOW,
            supersedes_projection_id=None,
        )

        with bundle.client.start_session() as session:
            session.start_transaction()

            with pytest.raises(
                BusinessClassificationProjectionV2RegistryError,
                match="BUSINESS_IDENTITY_BINDING_MISMATCH",
            ):
                bundle.registry.create(
                    candidate,
                    session=session,
                )

            session.abort_transaction()

        assert bundle.v2_collection.count_documents({}) == 0


def test_real_cross_business_supersession_rejected() -> None:
    with mongo_context() as bundle:
        first = identity(
            business_identity_id="BUSINESS-A",
        )

        second = identity(
            business_identity_id="BUSINESS-B",
        )

        seed_identity(
            bundle,
            first,
        )

        seed_identity(
            bundle,
            second,
        )

        prior = projection(
            first,
            projection_id="PROJ-A-1",
        )

        committed_create(
            bundle,
            prior,
        )

        later = projection(
            second,
            projection_id="PROJ-B-2",
            revision=2,
            supersedes_projection_id="PROJ-A-1",
        )

        with bundle.client.start_session() as session:
            session.start_transaction()

            with pytest.raises(
                BusinessClassificationProjectionV2RegistryError,
                match="CROSS_BUSINESS_SUPERSESSION_FORBIDDEN",
            ):
                bundle.registry.create(
                    later,
                    session=session,
                )

            session.abort_transaction()

        assert bundle.v2_collection.count_documents({}) == 1


def test_real_two_businesses_same_tenant_each_revision_one() -> None:
    with mongo_context() as bundle:
        first = identity(
            business_identity_id="BUSINESS-A",
        )

        second = identity(
            business_identity_id="BUSINESS-B",
        )

        seed_identity(
            bundle,
            first,
        )

        seed_identity(
            bundle,
            second,
        )

        committed_create(
            bundle,
            projection(
                first,
                projection_id="PROJ-A-1",
            ),
        )

        committed_create(
            bundle,
            projection(
                second,
                projection_id="PROJ-B-1",
            ),
        )

        assert bundle.v2_collection.count_documents({}) == 2


def test_real_business_history_revision_ordering() -> None:
    with mongo_context() as bundle:
        business = identity()
        seed_identity(
            bundle,
            business,
        )

        first = projection(
            business,
            projection_id="PROJ-1",
            revision=1,
        )

        second = projection(
            business,
            projection_id="PROJ-2",
            revision=2,
            supersedes_projection_id="PROJ-1",
        )

        committed_create(
            bundle,
            first,
        )

        committed_create(
            bundle,
            second,
        )

        history = bundle.registry.get_by_business(
            business.tenant_id,
            business.business_identity_id,
        )

        assert [
            value.revision
            for value in history
        ] == [
            1,
            2,
        ]


def test_real_tenant_multi_business_ordering() -> None:
    with mongo_context() as bundle:
        business_b = identity(
            business_identity_id="BUSINESS-B",
        )

        business_a = identity(
            business_identity_id="BUSINESS-A",
        )

        seed_identity(
            bundle,
            business_a,
        )

        seed_identity(
            bundle,
            business_b,
        )

        committed_create(
            bundle,
            projection(
                business_b,
                projection_id="PROJ-B-1",
            ),
        )

        committed_create(
            bundle,
            projection(
                business_a,
                projection_id="PROJ-A-1",
            ),
        )

        history = bundle.registry.get_by_tenant(
            "tenant-a"
        )

        assert [
            (
                value.business_identity_id,
                value.revision,
            )
            for value in history
        ] == [
            ("BUSINESS-A", 1),
            ("BUSINESS-B", 1),
        ]


def test_real_corrupt_v2_projection_rejected() -> None:
    with mongo_context() as bundle:
        business = identity()
        seed_identity(
            bundle,
            business,
        )

        candidate = projection(
            business
        )

        document = candidate.to_dict()
        document["fingerprint"] = "0" * 128

        bundle.v2_collection.insert_one(
            document
        )

        with pytest.raises(
            BusinessClassificationProjectionV2RegistryError,
            match="PERSISTED_RECORD_INVALID",
        ):
            bundle.registry.get(
                candidate.projection_id
            )


def test_real_identical_concurrency_one_durable_at_least_one_success() -> None:
    with mongo_context() as bundle:
        business = identity()
        seed_identity(
            bundle,
            business,
        )

        candidate = projection(
            business
        )

        barrier = threading.Barrier(
            2
        )

        results: list[str] = []
        lock = threading.Lock()

        def worker() -> None:
            with bundle.client.start_session() as session:
                session.start_transaction()

                try:
                    barrier.wait(
                        timeout=5
                    )

                    bundle.registry.create(
                        candidate,
                        session=session,
                    )

                    session.commit_transaction()

                    outcome = "success"
                except (
                    BusinessClassificationProjectionV2RegistryError,
                    PyMongoError,
                ):
                    if session.in_transaction:
                        session.abort_transaction()

                    outcome = "error"

            with lock:
                results.append(
                    outcome
                )

        threads = [
            threading.Thread(
                target=worker
            )
            for _ in range(
                2
            )
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(
                timeout=10
            )

        assert all(
            not thread.is_alive()
            for thread in threads
        )

        assert results.count(
            "success"
        ) >= 1

        assert bundle.v2_collection.count_documents({}) == 1

        durable = bundle.registry.get(
            candidate.projection_id
        )

        assert durable == candidate


def test_real_conflicting_same_tenant_business_revision_one_durable_exactly_one_success() -> None:
    with mongo_context() as bundle:
        business = identity()
        seed_identity(
            bundle,
            business,
        )

        first = projection(
            business,
            projection_id="CONFLICT-A",
            source_profile_digest=hashlib.sha3_512(
                b"source-a"
            ).hexdigest(),
        )

        second = projection(
            business,
            projection_id="CONFLICT-B",
            source_profile_digest=hashlib.sha3_512(
                b"source-b"
            ).hexdigest(),
        )

        barrier = threading.Barrier(
            2
        )

        results: list[str] = []
        lock = threading.Lock()

        def worker(
            candidate: BusinessClassificationProjectionV2,
        ) -> None:
            with bundle.client.start_session() as session:
                session.start_transaction()

                try:
                    barrier.wait(
                        timeout=5
                    )

                    bundle.registry.create(
                        candidate,
                        session=session,
                    )

                    session.commit_transaction()

                    outcome = "success"
                except (
                    BusinessClassificationProjectionV2RegistryError,
                    PyMongoError,
                ):
                    if session.in_transaction:
                        session.abort_transaction()

                    outcome = "error"

            with lock:
                results.append(
                    outcome
                )

        threads = [
            threading.Thread(
                target=worker,
                args=(candidate,),
            )
            for candidate in (
                first,
                second,
            )
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(
                timeout=10
            )

        assert all(
            not thread.is_alive()
            for thread in threads
        )

        assert results.count(
            "success"
        ) == 1

        assert results.count(
            "error"
        ) == 1

        assert bundle.v2_collection.count_documents({}) == 1


def test_real_v1_collection_unchanged() -> None:
    with mongo_context() as bundle:
        bundle.v1_collection.insert_one(
            {
                "sentinel":
                    "historical-v1-preserved",
                "payload":
                    {
                        "generation":
                            "v1",
                    },
            }
        )

        before = list(
            bundle.v1_collection.find({})
        )

        business = identity()
        seed_identity(
            bundle,
            business,
        )

        committed_create(
            bundle,
            projection(
                business
            ),
        )

        after = list(
            bundle.v1_collection.find({})
        )

        assert after == before
        assert bundle.v2_collection.count_documents({}) == 1


# ARTIFACT: test_business_classification_projection_v2_registry_real_mongo.py
