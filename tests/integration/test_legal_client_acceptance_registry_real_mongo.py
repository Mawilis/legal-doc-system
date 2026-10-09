"""Real-Mongo certificate for the durable L9A2 client-acceptance registry.

VERSION: v1.0.0-L9A2-CLIENT-ACCEPTANCE-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_acceptance_registry_real_mongo.py
TRANSACTION BOUNDARY: Test callers own every Mongo session and transaction.
AUTHORITY BOUNDARY: Physical immutable client-acceptance persistence/read evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
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

from tools.eos.legal_operations.domain.legal_client_acceptance import (
    ACCEPTANCE_FIELDS,
    LegalClientAcceptance,
    record_legal_client_acceptance,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import legal_client_acceptance_registry as registry


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 26, 14, 0, 0, 654321, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
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

        database = client[f"wilsy_l9a2_acceptance_{uuid.uuid4().hex}"]
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


def _matter(tenant: str, matter_id: str = "matter-1") -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def _acceptance(
    tenant: str,
    *,
    matter_id: str = "matter-1",
    acceptance_id: str = "acceptance-1",
    actor: str = "principal-client-1",
    scope: str = "client-information-review:v1",
) -> LegalClientAcceptance:
    return record_legal_client_acceptance(
        case_matter=_matter(tenant, matter_id),
        acceptance_id=acceptance_id,
        party_id="party-1",
        subject_reference="client:acme-1",
        subject_identity_fingerprint=FP_A,
        acceptance_scope=scope,
        actor_principal_id=actor,
        accepted_at=NOW,
        source_evidence_reference="client-evidence:1",
        source_evidence_fingerprint=FP_B,
    )


def _commit(
    client: MongoClient[Any],
    collection: Any,
    value: LegalClientAcceptance,
) -> LegalClientAcceptance:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_acceptance(value, collection, session=session)


def test_real_index_metadata_is_exact_unique_and_has_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert set(indexes) == {
        registry.ACCEPTANCE_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.MATTER_LOOKUP_INDEX_NAME,
    }
    assert dict(indexes[registry.ACCEPTANCE_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "acceptance_id": 1,
    }
    assert indexes[registry.ACCEPTANCE_ID_INDEX_NAME].get("unique") is True
    assert dict(indexes[registry.FINGERPRINT_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "fingerprint": 1,
    }
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert dict(indexes[registry.MATTER_LOOKUP_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "case_matter_id": 1,
        "accepted_at": -1,
    }
    assert indexes[registry.MATTER_LOOKUP_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_real_commit_exact_replay_row_count_and_utc_microseconds(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-replay-{uuid.uuid4().hex}"
    value = _acceptance(tenant)
    assert _commit(client, collection, value) == value
    assert _commit(client, collection, value) == value
    assert collection.count_documents({"tenant_id": tenant}) == 1

    with client.start_session() as session:
        with session.start_transaction():
            readback = registry.get_acceptance_by_fingerprint(
                tenant,
                value.fingerprint,
                collection,
                session=session,
            )
            assert readback.accepted_at.tzinfo is not None
            assert readback.accepted_at.utcoffset() == timezone.utc.utcoffset(NOW)
            assert readback.accepted_at.microsecond == 654321
    raw = collection.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)
    assert raw["accepted_at"] == "2026-09-26T14:00:00.654321Z"


def test_real_tenant_and_matter_reads_do_not_cross_or_collide(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    first = _acceptance(tenant_a, acceptance_id="acceptance-a", matter_id="matter-1")
    second = _acceptance(tenant_a, acceptance_id="acceptance-b", matter_id="matter-2")
    foreign = _acceptance(tenant_b, acceptance_id="acceptance-a", matter_id="matter-1")
    for value in (first, second, foreign):
        assert _commit(client, collection, value) == value

    with client.start_session() as session:
        with session.start_transaction():
            assert [
                item.acceptance_id
                for item in registry.list_matter_acceptances(
                    tenant_a, "matter-1", collection, session=session
                )
            ] == ["acceptance-a"]
            with pytest.raises(registry.LegalClientAcceptanceRegistryNotFoundError):
                registry.get_acceptance(tenant_b, "acceptance-b", collection, session=session)
    assert collection.count_documents({"tenant_id": tenant_a}) == 2
    assert collection.count_documents({"tenant_id": tenant_b}) == 1


def test_real_divergent_identity_fails_closed_without_update_or_delete(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-conflict-{uuid.uuid4().hex}"
    first = _acceptance(tenant)
    _commit(client, collection, first)
    divergent = _acceptance(tenant, actor="principal-client-2")
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientAcceptanceRegistryConflictError):
            registry.persist_acceptance(divergent, collection, session=session)
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_corruption_is_rejected_before_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _acceptance(tenant)
    _commit(client, collection, value)
    original = deepcopy(collection.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)

    collection.update_one(
        {"tenant_id": tenant},
        {"$set": {"source_evidence_fingerprint": "c" * 128}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientAcceptanceRegistryPersistedRecordInvalidError):
                registry.get_acceptance(tenant, value.acceptance_id, collection, session=session)

    collection.replace_one({"_id": original["_id"]}, original)
    collection.update_one(
        {"tenant_id": tenant},
        {"$set": {"unexpected": True}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientAcceptanceRegistryPersistedRecordInvalidError):
                registry.get_acceptance(tenant, value.acceptance_id, collection, session=session)
    collection.replace_one({"_id": original["_id"]}, original)


def test_real_caller_abort_leaves_zero_rows(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _acceptance(tenant)
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_acceptance(value, collection, session=session)
        assert collection.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 0


def test_real_competing_exact_consumers_do_not_duplicate(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    value = _acceptance(tenant)
    barrier = Barrier(2)

    def contender() -> str:
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                registry.persist_acceptance(value, collection, session=session)
                session.commit_transaction()
                return "COMMITTED"
            except registry.LegalClientAcceptanceRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"
            except registry.LegalClientAcceptanceRegistryConflictError:
                if session.in_transaction:
                    session.abort_transaction()
                return "CONFLICT"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _item: contender(), (1, 2)))
    assert all(outcome in {"COMMITTED", "RETRY_REQUIRED", "CONFLICT"} for outcome in outcomes)
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_row_has_only_canonical_domain_fields_and_no_authority_side_effects(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-shape-{uuid.uuid4().hex}"
    value = _acceptance(tenant)
    _commit(client, collection, value)
    row = collection.find_one({"tenant_id": tenant})
    assert isinstance(row, dict)
    assert set(row) == set(ACCEPTANCE_FIELDS) | {"_id"}
    assert not {
        "engagement_active", "representation_active", "court_authorized",
        "financial_authority", "portal_access",
    } & set(row)


# ARTIFACT: test_legal_client_acceptance_registry_real_mongo.py
# VERSION: v1.0.0-L9A2-CLIENT-ACCEPTANCE-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable client-acceptance persistence/read evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant/matter queries
# FAIL-CLOSED POSTURE: rollback/corruption/conflict/concurrency cannot create duplicate acceptance truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
