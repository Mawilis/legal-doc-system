"""WILSY OS — Business Identity Registry real-Mongo certificate.

TITLE: Business Identity Registry Real Mongo Certificate
VERSION: v1.0.0-BUSINESS-IDENTITY-REGISTRY-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance

PURPOSE:
    Certify immutable Business Identity revision persistence against a real
    loopback MongoDB replica set with caller-owned transactions and a
    read-only canonical Tenant dependency.

DATABASE BOUNDARY:
- mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS only.
- UUID-isolated disposable database only.
- Database is dropped in fixture finalization.
- Production database state is never used.

AUTHORITY BOUNDARY:
- Business Identity persistence only.
- Tenant is read-only canonical ownership scope.
- No latest/current or unversioned Business Identity authority.
- No classification, taxonomy, entitlement, subscription, permission,
  authorization, activation, regulatory, tax-validity, AI-execution,
  or financial authority.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from tools.eos.saas.business_identity_registry import (
    COLLECTION_NAME,
    BusinessIdentityRegistry,
    BusinessIdentityRegistryError,
)
from tools.eos.saas.domain.business_identity import (
    BusinessIdentity,
)
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
)


MONGO_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

DATABASE_PREFIX = (
    "wilsy_business_identity_cert_"
)

NOW = datetime(
    2026,
    10,
    8,
    9,
    0,
    tzinfo=timezone.utc,
)


def tenant_document(
    tenant_id: str,
    *,
    name: str,
) -> dict[str, Any]:
    """Build one healthy canonical Tenant persistence document."""
    return {
        "tenant_id": tenant_id,
        "name": name,
        "organization": {
            "organization_name": name,
            "industry": "General",
            "plan": "ENTERPRISE",
            "legal_name": None,
            "tax_id": None,
            "contact_email": None,
            "regions": [
                "Africa",
            ],
            "created_at":
                "2026-08-30T00:00:00+00:00",
        },
        "industry": "General",
        "plan": "ENTERPRISE",
        "regions": [
            "Africa",
        ],
        "status": "ACTIVE",
        "created_at":
            "2026-08-30T00:00:00+00:00",
        "alias": tenant_id,
        "region": "ZA",
        "compliance_flags": {
            "certification": True,
        },
        "verified": False,
    }


class CanonicalTenantReadAdapter:
    """Bind canonical TenantRegistry hydration to one isolated collection."""

    def __init__(
        self,
        collection: Collection[Any],
    ) -> None:
        self._collection = collection
        self.calls = 0

    def resolve_canonical_tenant(
        self,
        tenant_reference: str,
        *,
        session: Any = None,
        allow_alias: bool = False,
    ) -> Any:
        """Resolve exact tenant identity using canonical TenantRegistry.get."""
        self.calls += 1

        if allow_alias:
            raise AssertionError(
                "ALIAS_RESOLUTION_NOT_AUTHORIZED"
            )

        return TenantRegistry.get(
            tenant_reference,
            collection=self._collection,
            session=session,
        )


def identity(
    *,
    business_identity_id: str = "BUSINESS-001",
    tenant_id: str = "tenant-a",
    revision: int = 1,
    organization_name: str = "Acme Holdings",
    legal_name: str = "Acme Holdings (Pty) Ltd",
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


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Database[Any],
        Collection[Any],
        Collection[Any],
        CanonicalTenantReadAdapter,
        BusinessIdentityRegistry,
    ]
]:
    """Provide one isolated real-Mongo tenant/Business Identity chain."""
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

    tenant_collection = database[
        "tenants"
    ]

    identity_collection = database[
        COLLECTION_NAME
    ]

    BusinessIdentityRegistry.ensure_indexes(
        identity_collection
    )

    tenant_adapter = CanonicalTenantReadAdapter(
        tenant_collection
    )

    identity_registry = BusinessIdentityRegistry(
        identity_collection,
        tenant_registry=tenant_adapter,
    )

    try:
        yield (
            client,
            database,
            tenant_collection,
            identity_collection,
            tenant_adapter,
            identity_registry,
        )
    finally:
        client.drop_database(
            database_name
        )
        client.close()


def persist_tenant(
    collection: Collection[Any],
    tenant_id: str,
    *,
    name: str | None = None,
) -> None:
    """Commit one isolated tenant before Business Identity operations."""
    collection.insert_one(
        tenant_document(
            tenant_id,
            name=(
                name
                if name is not None
                else tenant_id
            ),
        )
    )


def persist_identity(
    client: MongoClient[Any],
    registry: BusinessIdentityRegistry,
    value: BusinessIdentity,
) -> BusinessIdentity:
    """Commit one Business Identity revision using caller-owned transaction."""
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
        _tenant_collection,
        identity_collection,
        _tenant_adapter,
        _registry,
    ) = mongo_context

    indexes = {
        entry["name"]: entry
        for entry
        in identity_collection.list_indexes()
    }

    assert set(
        indexes
    ) == {
        "_id_",
        "business_identity_subject_revision_unique",
        "business_identity_fingerprint_unique",
        "business_identity_tenant_subject_revision",
        "business_identity_tenant_effective_from",
        "business_identity_subject_supersedes_revision",
    }

    assert list(
        indexes[
            "business_identity_subject_revision_unique"
        ]["key"].items()
    ) == [
        (
            "business_identity_id",
            1,
        ),
        (
            "revision",
            1,
        ),
    ]

    assert list(
        indexes[
            "business_identity_fingerprint_unique"
        ]["key"].items()
    ) == [
        (
            "identity_fingerprint",
            1,
        )
    ]

    assert (
        indexes[
            "business_identity_subject_revision_unique"
        ].get("unique")
        is True
    )

    assert (
        indexes[
            "business_identity_fingerprint_unique"
        ].get("unique")
        is True
    )

    assert all(
        "expireAfterSeconds"
        not in entry
        for entry in indexes.values()
    )


def test_missing_session_rejected_before_tenant_read_or_identity_write(
    mongo_context: Any,
) -> None:
    (
        _client,
        _database,
        tenant_collection,
        identity_collection,
        tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    with pytest.raises(
        BusinessIdentityRegistryError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create(
            identity(),
            session=None,
        )

    assert tenant_adapter.calls == 0
    assert identity_collection.count_documents({}) == 0


def test_inactive_transaction_rejected_before_tenant_read_or_identity_write(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    with client.start_session() as session:
        assert not session.in_transaction

        with pytest.raises(
            BusinessIdentityRegistryError,
            match="ACTIVE_TRANSACTION_REQUIRED",
        ):
            registry.create(
                identity(),
                session=session,
            )

    assert tenant_adapter.calls == 0
    assert identity_collection.count_documents({}) == 0


def test_missing_tenant_rejected_before_identity_insert(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        _tenant_collection,
        identity_collection,
        tenant_adapter,
        registry,
    ) = mongo_context

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessIdentityRegistryError,
                match="TENANT_INVALID",
            ):
                registry.create(
                    identity(),
                    session=session,
                )

    assert tenant_adapter.calls == 1
    assert identity_collection.count_documents({}) == 0


def test_committed_tenant_to_business_identity_roundtrip(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    candidate = identity()

    observed = persist_identity(
        client,
        registry,
        candidate,
    )

    assert observed == candidate
    assert identity_collection.count_documents({}) == 1

    assert registry.get_revision(
        candidate.business_identity_id,
        candidate.revision,
    ) == candidate

    assert registry.get_by_fingerprint(
        candidate.identity_fingerprint
    ) == candidate


def test_aborted_business_identity_insert_leaves_zero_rows(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    candidate = identity()

    with client.start_session() as session:
        session.start_transaction()

        observed = registry.create(
            candidate,
            session=session,
        )

        assert observed == candidate
        assert session.in_transaction

        session.abort_transaction()

    assert identity_collection.count_documents({}) == 0


def test_exact_replay_is_idempotent(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    candidate = identity()

    first = persist_identity(
        client,
        registry,
        candidate,
    )

    replay = persist_identity(
        client,
        registry,
        candidate,
    )

    assert first == candidate
    assert replay == candidate
    assert identity_collection.count_documents({}) == 1


def test_same_subject_revision_different_truth_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    durable = identity()

    persist_identity(
        client,
        registry,
        durable,
    )

    conflicting = identity(
        organization_name="Changed Organization",
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessIdentityRegistryError,
                match="SUBJECT_REVISION_CONFLICT",
            ):
                registry.create(
                    conflicting,
                    session=session,
                )

    assert identity_collection.count_documents({}) == 1


def test_same_fingerprint_different_truth_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    candidate = identity(
        business_identity_id="BUSINESS-CANDIDATE",
    )

    collision = identity(
        business_identity_id="BUSINESS-OTHER",
    ).to_dict()

    collision[
        "identity_fingerprint"
    ] = candidate.identity_fingerprint

    identity_collection.insert_one(
        collision
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessIdentityRegistryError,
                match="FINGERPRINT_CONFLICT",
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert identity_collection.count_documents({}) == 1


def test_later_revision_requires_declared_predecessor(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    candidate = identity(
        revision=2,
        supersedes_revision=1,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessIdentityRegistryError,
                match="PREDECESSOR_MISSING",
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert identity_collection.count_documents({}) == 0


def test_cross_tenant_predecessor_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    persist_tenant(
        tenant_collection,
        "tenant-b",
    )

    prior = identity(
        tenant_id="tenant-b",
        revision=1,
    )

    persist_identity(
        client,
        registry,
        prior,
    )

    candidate = identity(
        tenant_id="tenant-a",
        revision=2,
        supersedes_revision=1,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessIdentityRegistryError,
                match="PREDECESSOR_TENANT_MISMATCH",
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert identity_collection.count_documents({}) == 1


def test_corrupt_predecessor_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    prior = identity(
        revision=1,
    )

    persist_identity(
        client,
        registry,
        prior,
    )

    identity_collection.update_one(
        {
            "business_identity_id":
                prior.business_identity_id,
            "revision":
                prior.revision,
        },
        {
            "$set": {
                "identity_fingerprint":
                    "0" * 128,
            },
        },
    )

    candidate = identity(
        revision=2,
        supersedes_revision=1,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                BusinessIdentityRegistryError,
                match="PERSISTED_RECORD_INVALID",
            ):
                registry.create(
                    candidate,
                    session=session,
                )

    assert identity_collection.count_documents({}) == 1


def test_non_adjacent_supersession_remains_valid(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    first = identity(
        revision=1,
    )

    second = identity(
        revision=2,
        supersedes_revision=1,
    )

    seventh = identity(
        revision=7,
        supersedes_revision=2,
    )

    for value in (
        first,
        second,
        seventh,
    ):
        persist_identity(
            client,
            registry,
            value,
        )

    assert identity_collection.count_documents({}) == 3

    assert registry.get_revision(
        seventh.business_identity_id,
        seventh.revision,
    ) == seventh


def test_get_revision_and_fingerprint_roundtrip(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        _identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    candidate = identity()

    persist_identity(
        client,
        registry,
        candidate,
    )

    assert registry.get_revision(
        candidate.business_identity_id,
        candidate.revision,
    ) == candidate

    assert registry.get_by_fingerprint(
        candidate.identity_fingerprint
    ) == candidate


def test_subject_history_is_revision_ordered(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        _identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    first = identity(
        revision=1,
    )

    second = identity(
        revision=2,
        supersedes_revision=1,
    )

    seventh = identity(
        revision=7,
        supersedes_revision=2,
    )

    for value in (
        first,
        second,
        seventh,
    ):
        persist_identity(
            client,
            registry,
            value,
        )

    assert registry.get_history(
        "BUSINESS-001"
    ) == (
        first,
        second,
        seventh,
    )


def test_tenant_history_is_subject_then_revision_ordered(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        _identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    a1 = identity(
        business_identity_id="BUSINESS-A",
        revision=1,
    )

    a2 = identity(
        business_identity_id="BUSINESS-A",
        revision=2,
        supersedes_revision=1,
    )

    b1 = identity(
        business_identity_id="BUSINESS-B",
        revision=1,
    )

    for value in (
        b1,
        a1,
        a2,
    ):
        persist_identity(
            client,
            registry,
            value,
        )

    assert registry.get_by_tenant(
        "tenant-a"
    ) == (
        a1,
        a2,
        b1,
    )


def test_multiple_subject_ids_under_one_tenant_are_not_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    first = identity(
        business_identity_id="BUSINESS-A",
    )

    second = identity(
        business_identity_id="BUSINESS-B",
    )

    persist_identity(
        client,
        registry,
        first,
    )

    persist_identity(
        client,
        registry,
        second,
    )

    assert identity_collection.count_documents({}) == 2

    assert registry.get_by_tenant(
        "tenant-a"
    ) == (
        first,
        second,
    )


def test_corrupt_persisted_revision_rejected(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    candidate = identity()

    persist_identity(
        client,
        registry,
        candidate,
    )

    identity_collection.update_one(
        {
            "business_identity_id":
                candidate.business_identity_id,
            "revision":
                candidate.revision,
        },
        {
            "$set": {
                "identity_fingerprint":
                    "0" * 128,
            },
        },
    )

    with pytest.raises(
        BusinessIdentityRegistryError,
        match="PERSISTED_RECORD_INVALID",
    ):
        registry.get_revision(
            candidate.business_identity_id,
            candidate.revision,
        )


def test_concurrent_identical_revision_create_converges_to_one_durable_row(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    candidate = identity()

    barrier = Barrier(
        2
    )

    def worker() -> tuple[
        str,
        str,
    ]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    barrier.wait()

                    observed = registry.create(
                        candidate,
                        session=session,
                    )

            return (
                "success",
                observed.identity_fingerprint,
            )

        except (
            BusinessIdentityRegistryError,
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

    assert len(
        successes
    ) >= 1

    assert identity_collection.count_documents({}) == 1

    assert registry.get_revision(
        candidate.business_identity_id,
        candidate.revision,
    ) == candidate


def test_concurrent_conflicting_revision_create_yields_one_durable_truth(
    mongo_context: Any,
) -> None:
    (
        client,
        _database,
        tenant_collection,
        identity_collection,
        _tenant_adapter,
        registry,
    ) = mongo_context

    persist_tenant(
        tenant_collection,
        "tenant-a",
    )

    first = identity(
        organization_name="Truth A",
        legal_name="Truth A (Pty) Ltd",
    )

    second = identity(
        organization_name="Truth B",
        legal_name="Truth B (Pty) Ltd",
    )

    barrier = Barrier(
        2
    )

    def worker(
        candidate: BusinessIdentity,
    ) -> tuple[
        str,
        str,
    ]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    barrier.wait()

                    observed = registry.create(
                        candidate,
                        session=session,
                    )

            return (
                "success",
                observed.identity_fingerprint,
            )

        except (
            BusinessIdentityRegistryError,
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

    assert len(
        successes
    ) == 1

    assert len(
        failures
    ) == 1

    assert identity_collection.count_documents({}) == 1

    durable = identity_collection.find_one(
        {}
    )

    assert durable is not None

    assert durable[
        "identity_fingerprint"
    ] in {
        first.identity_fingerprint,
        second.identity_fingerprint,
    }


# ARTIFACT: test_business_identity_registry_real_mongo.py
