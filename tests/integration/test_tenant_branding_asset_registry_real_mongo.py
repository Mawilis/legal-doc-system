"""Real-Mongo certificate for D21B5B tenant branding asset bytes.

TITLE: Tenant Branding Asset Registry Real-Mongo Certificate
VERSION: v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Physically certify immutable bounded branding bytes, exact BSON
         round-trip integrity, tenant isolation, transaction rollback, corruption
         rejection and competing-create retry semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_branding_asset_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed D21B5B certificate only; D21B5A owns
                            metadata/content identity; caller owns transactions.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY-REAL-MONGO-CERT proves
           physical indexes, committed exact replay, BSON byte re-hash,
           fingerprint/kind resolution, tenant silence, rollback atomicity,
           corruption rejection and one-winner competing immutable creation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and bounded image
                             bytes only; no URLs, credentials or external calls.
TENANT BOUNDARY: Every physical record/query is exact tenant/reference scoped.
AUTHORITY BOUNDARY: Durable bytes/resolution only; no profile/current/entitlement
                    browser/IAM/legal-command authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Certificate owns test transactions; registry owns none.
FAIL-CLOSED DECLARATION: Once the replica-set fixture yields, any index,
                         transaction, byte, replay, corruption or concurrency
                         failure fails certification.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing import tenant_branding_asset_registry as registry
from tools.eos.saas.domain.tenant_branding_asset import (
    TenantBrandingAsset,
    TenantBrandingAssetKind,
    register_tenant_branding_asset,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 19, 0, tzinfo=timezone.utc)
FP = "a" * 128
PNG = b"\x89PNG\r\n\x1a\n" + b"real-mongo-brand"


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one isolated writable real-Mongo collection."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(
                f"host Mongo unavailable during hello: {type(error).__name__}: {error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")

        database = client[f"wilsy_d21b5b_branding_{uuid.uuid4().hex}"]
        collection = database.get_collection(
            registry.COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry.ensure_indexes(collection)
        yield client, database, collection
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _asset(
    tenant_id: str,
    *,
    reference: str | None = None,
    content: bytes = PNG,
    kind: TenantBrandingAssetKind = TenantBrandingAssetKind.LOGO,
) -> TenantBrandingAsset:
    """Create exact D21B5A evidence for real-Mongo tests."""
    asset_reference = reference or f"asset:{tenant_id}:logo:primary"
    return register_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_reference=asset_reference,
        asset_kind=kind,
        media_type="image/png",
        content=content,
        source_evidence_reference="upload-real-1",
        source_evidence_fingerprint=FP,
        registered_at=NOW,
    )


def _commit_create(
    client: MongoClient[Any],
    asset: TenantBrandingAsset,
    content: bytes,
    collection: Any,
) -> registry.TenantBrandingResolvedAsset:
    """Commit one immutable asset under caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.create_or_replay(
                asset,
                content,
                collection,
                session=session,
            )


def test_real_index_metadata_is_exact_and_has_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Physically prove reference uniqueness and nonunique content lookup."""
    _, _, collection = mongo_context
    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert set(indexes) == {
        registry.IDENTITY_INDEX_NAME,
        registry.CONTENT_INDEX_NAME,
    }
    assert dict(indexes[registry.IDENTITY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "asset_reference": 1,
    }
    assert indexes[registry.IDENTITY_INDEX_NAME].get("unique") is True
    assert dict(indexes[registry.CONTENT_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "content_fingerprint": 1,
    }
    assert indexes[registry.CONTENT_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_real_create_exact_replay_and_bson_byte_resolution(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Committed bytes replay exactly and resolve through SHA3/kind evidence."""
    client, _, collection = mongo_context
    tenant = f"tenant-create-{uuid.uuid4().hex}"
    value = _asset(tenant)
    first = _commit_create(client, value, PNG, collection)
    replay = _commit_create(client, value, PNG, collection)
    assert first.asset == replay.asset == value
    assert first.content == replay.content == PNG
    assert collection.count_documents({"tenant_id": tenant}) == 1

    with client.start_session() as session:
        with session.start_transaction():
            resolved = registry.resolve(
                tenant,
                value.asset_reference,
                expected_content_fingerprint=value.content_fingerprint,
                expected_kind=TenantBrandingAssetKind.LOGO,
                collection=collection,
                session=session,
            )
    assert resolved.asset == value
    assert resolved.content == PNG


def test_real_active_transaction_required_abort_and_tenant_isolation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """No registry-owned transaction; abort removes row; foreign scope is absent."""
    client, _, collection = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _asset(tenant)

    with pytest.raises(registry.TenantBrandingAssetRegistryTransactionRequiredError):
        registry.create_or_replay(value, PNG, collection, session=None)

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(value, PNG, collection, session=session)
        assert collection.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 0

    _commit_create(client, value, PNG, collection)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.TenantBrandingAssetRegistryNotFoundError):
                registry.resolve(
                    f"foreign-{uuid.uuid4().hex}",
                    value.asset_reference,
                    expected_content_fingerprint=value.content_fingerprint,
                    expected_kind=value.asset_kind,
                    collection=collection,
                    session=session,
                )


def test_real_expected_fingerprint_kind_and_corruption_fail_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Profile evidence mismatch and physical byte tampering always reject."""
    client, _, collection = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _asset(tenant)
    _commit_create(client, value, PNG, collection)

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.TenantBrandingAssetRegistryConflictError):
                registry.resolve(
                    tenant,
                    value.asset_reference,
                    expected_content_fingerprint="f" * 128,
                    expected_kind=value.asset_kind,
                    collection=collection,
                    session=session,
                )
            with pytest.raises(registry.TenantBrandingAssetRegistryConflictError):
                registry.resolve(
                    tenant,
                    value.asset_reference,
                    expected_content_fingerprint=value.content_fingerprint,
                    expected_kind=TenantBrandingAssetKind.FAVICON,
                    collection=collection,
                    session=session,
                )

    original = deepcopy(collection.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)
    collection.update_one(
        {"tenant_id": tenant},
        {"$set": {"content_bytes": PNG + b"tampered"}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.TenantBrandingAssetRegistryPersistedRecordInvalidError
            ):
                registry.resolve(
                    tenant,
                    value.asset_reference,
                    expected_content_fingerprint=value.content_fingerprint,
                    expected_kind=value.asset_kind,
                    collection=collection,
                    session=session,
                )
    collection.replace_one({"_id": original["_id"]}, original)


def test_real_same_content_can_back_two_distinct_references(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Content index is physically nonunique while reference identity is unique."""
    client, _, collection = mongo_context
    tenant = f"tenant-shared-{uuid.uuid4().hex}"
    first = _asset(tenant, reference=f"asset:{tenant}:logo:first")
    second = _asset(tenant, reference=f"asset:{tenant}:logo:second")
    _commit_create(client, first, PNG, collection)
    _commit_create(client, second, PNG, collection)
    assert collection.count_documents(
        {"tenant_id": tenant, "content_fingerprint": first.content_fingerprint}
    ) == 2


def test_real_competing_same_reference_has_one_commit_and_one_retry(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """A genuine divergent immutable-create race cannot commit two bindings."""
    client, _, collection = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    left_bytes = PNG + b"-left"
    right_bytes = PNG + b"-right"
    reference = f"asset:{tenant}:logo:raced"
    left = _asset(tenant, reference=reference, content=left_bytes)
    right = _asset(tenant, reference=reference, content=right_bytes)
    barrier = Barrier(2)

    def contender(
        command: tuple[TenantBrandingAsset, bytes],
    ) -> str:
        value, content = command
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                registry.create_or_replay(
                    value,
                    content,
                    collection,
                    session=session,
                )
                session.commit_transaction()
                return "COMMITTED"
            except registry.TenantBrandingAssetRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"
            except Exception as error:
                if session.in_transaction:
                    session.abort_transaction()
                return type(error).__name__

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(
            pool.map(
                contender,
                ((left, left_bytes), (right, right_bytes)),
            )
        )

    assert outcomes.count("COMMITTED") == 1
    assert outcomes.count("RETRY_REQUIRED") == 1
    assert collection.count_documents(
        {"tenant_id": tenant, "asset_reference": reference}
    ) == 1
    stored = collection.find_one(
        {"tenant_id": tenant, "asset_reference": reference}
    )
    assert isinstance(stored, dict)
    assert stored["content_fingerprint"] in {
        left.content_fingerprint,
        right.content_fingerprint,
    }


# ARTIFACT: test_tenant_branding_asset_registry_real_mongo.py
# VERSION: v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable branding-byte persistence/resolution evidence only; no profile/current/entitlement/browser/IAM/financial authority
# TENANT POSTURE: UUID-isolated database and exact tenant/reference persistence
# FAIL-CLOSED POSTURE: post-yield index/transaction/byte/corruption/concurrency failures fail certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
