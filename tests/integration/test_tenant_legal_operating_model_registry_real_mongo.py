"""Real-Mongo certificate for durable Tenant Legal Operating Models.

TITLE: Tenant Legal Operating Model Registry Real-Mongo Certificate
VERSION: v1.0.0-CX26-R2-DURABLE-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Physical certification of immutable operating-model persistence.
EPITOME: Prove topology, indexes, caller transactions, replay, isolation,
         currentness, rollback, concurrency, corruption, and restart durability.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_legal_operating_model_registry_real_mongo.py
COLLABORATION / OWNERSHIP: CX26 R2 registry is the production subject; this
                            certificate owns only UUID-isolated synthetic data.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-CX26-R2 establishes the sanctioned loopback certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque tenants; no customer data or secrets.
TENANT BOUNDARY: Every assertion uses exact synthetic tenant predicates.
AUTHORITY BOUNDARY: Configuration persistence proof only; no IAM or command authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Tests own every transaction; registry owns none.
FAIL-CLOSED DECLARATION: Topology, index, corruption, ambiguity, race,
                         rollback, outage, or durability failure fails.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from threading import Barrier
from typing import Any, Iterator, Mapping
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.tenant_legal_operating_model import TenantLegalOperatingModel
from tools.eos.legal_operations.registry import tenant_legal_operating_model_registry as registry

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 10, 13, 10, 15, 0, 987654, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one disposable database on the sanctioned writable replica set."""
    client: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000, retryWrites=True, tz_aware=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(f"CX26_R2_MONGO_UNAVAILABLE:{type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail("CX26_R2_WRONG_REPLICA_SET")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("CX26_R2_NO_WRITABLE_PRIMARY")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("CX26_R2_LOGICAL_SESSIONS_UNAVAILABLE")
        database = client[f"wilsy_cx26_r2_operating_model_{uuid.uuid4().hex}"]
        collection = database.get_collection(registry.COLLECTION_NAME, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        registry.TenantLegalOperatingModelRegistry(collection).ensure_indexes()
        yield client, database, collection
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def operating_model(
    tenant: str,
    identity: str = "operating-model-1",
    *,
    revision: int = 1,
    effective_from: datetime = BASE,
    supersedes: str | None = None,
    items: tuple[str, ...] = ("PERSONA_PARTNER", "PRACTICE_DISPUTES"),
) -> TenantLegalOperatingModel:
    """Build one canonical synthetic immutable configuration."""
    return TenantLegalOperatingModel(tenant_id=tenant, operating_model_id=identity, revision=revision, activated_item_ids=items, effective_from=effective_from, supersedes_operating_model_id=supersedes)


def commit(client: MongoClient[Any], collection: Any, value: TenantLegalOperatingModel) -> TenantLegalOperatingModel:
    """Commit one call while retaining caller transaction ownership."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.TenantLegalOperatingModelRegistry(collection).create_or_replay(value, session=session)


def test_real_topology_indexes_are_exact_tenant_first_unique_and_non_ttl(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    client, _database, collection = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    indexes = {item["name"]: item for item in collection.list_indexes() if item["name"] != "_id_"}
    assert set(indexes) == {registry.IDENTITY_INDEX_NAME, registry.FINGERPRINT_INDEX_NAME, registry.TENANT_HISTORY_INDEX_NAME, registry.CURRENTNESS_INDEX_NAME, registry.SUPERSESSION_INDEX_NAME}
    assert dict(indexes[registry.IDENTITY_INDEX_NAME]["key"]) == {"tenant_id": 1, "operating_model_id": 1}
    assert dict(indexes[registry.FINGERPRINT_INDEX_NAME]["key"]) == {"tenant_id": 1, "fingerprint": 1}
    assert indexes[registry.IDENTITY_INDEX_NAME].get("unique") is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert all(next(iter(dict(item["key"]))) == "tenant_id" for item in indexes.values())
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_real_replay_unique_constraints_isolation_and_microseconds(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    client, _database, collection = mongo_context
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    value, foreign = operating_model(tenant_a), operating_model(tenant_b)
    assert commit(client, collection, value) == value
    assert commit(client, collection, value) == value
    assert commit(client, collection, foreign) == foreign
    assert collection.count_documents({"tenant_id": tenant_a}) == 1
    assert collection.count_documents({"tenant_id": tenant_b}) == 1
    raw = collection.find_one({"tenant_id": tenant_a})
    assert isinstance(raw, dict)
    assert raw["effective_from"] == "2026-10-13T10:15:00.987654+00:00"
    assert not {"principal_id", "role_id", "business_role", "permission", "entitlement_id", "payment", "settlement"}.intersection(raw)
    duplicate_identity = value.to_dict()
    duplicate_identity["fingerprint"] = "f" * 128
    with pytest.raises(DuplicateKeyError):
        collection.insert_one(duplicate_identity)
    fingerprint_collision = value.to_dict()
    fingerprint_collision["operating_model_id"] = "different-model-id"
    with pytest.raises(DuplicateKeyError):
        collection.insert_one(fingerprint_collision)
    target = registry.TenantLegalOperatingModelRegistry(collection)
    with client.start_session() as session:
        with session.start_transaction():
            assert target.get_by_id(tenant_a, value.operating_model_id, session=session) == value
            with pytest.raises(registry.TenantLegalOperatingModelRegistryNotFoundError):
                target.get_by_id(tenant_a, "absent", session=session)


def test_real_divergent_replay_fails_without_mutation(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    client, _database, collection = mongo_context
    tenant = f"tenant-conflict-{uuid.uuid4().hex}"
    value = operating_model(tenant)
    commit(client, collection, value)
    before = deepcopy(collection.find_one({"tenant_id": tenant}))
    divergent = operating_model(tenant, items=("RISK_CONFLICTS",))
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.TenantLegalOperatingModelRegistryConflictError):
            registry.TenantLegalOperatingModelRegistry(collection).create_or_replay(divergent, session=session)
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 1
    assert collection.find_one({"tenant_id": tenant}) == before


def test_real_history_currentness_boundaries_and_future_exclusion(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    client, _database, collection = mongo_context
    tenant = f"tenant-history-{uuid.uuid4().hex}"
    first = operating_model(tenant)
    second_at = BASE + timedelta(days=1, microseconds=1)
    second = operating_model(tenant, "operating-model-2", revision=2, effective_from=second_at, supersedes=first.operating_model_id)
    third_at = second_at + timedelta(days=1)
    third = operating_model(tenant, "operating-model-3", revision=3, effective_from=third_at, supersedes=second.operating_model_id)
    for value in (third, first, second):
        commit(client, collection, value)
    target = registry.TenantLegalOperatingModelRegistry(collection)
    with client.start_session() as session:
        with session.start_transaction():
            assert target.list_tenant_history(tenant, session=session) == (first, second, third)
            with pytest.raises(registry.TenantLegalOperatingModelRegistryNotFoundError):
                target.resolve_current(tenant, BASE - timedelta(microseconds=1), session=session)
            assert target.resolve_current(tenant, BASE, session=session) == first
            assert target.resolve_current(tenant, second_at - timedelta(microseconds=1), session=session) == first
            assert target.resolve_current(tenant, second_at, session=session) == second
            assert target.resolve_current(tenant, third_at, session=session) == third
            assert third.effective_from.microsecond == 987655


def test_real_corruption_extra_field_and_supersession_reject(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    client, _database, collection = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    first = operating_model(tenant)
    commit(client, collection, first)
    original = deepcopy(collection.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)
    target = registry.TenantLegalOperatingModelRegistry(collection)
    for mutation in ({"fingerprint": "f" * 128}, {"unexpected": True}):
        collection.update_one({"tenant_id": tenant}, {"$set": mutation})
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(registry.TenantLegalOperatingModelRegistryPersistedRecordInvalidError):
                    target.get_by_id(tenant, first.operating_model_id, session=session)
        collection.replace_one({"_id": original["_id"]}, original)
    inconsistent = operating_model(tenant, "operating-model-2", revision=2, effective_from=BASE + timedelta(days=1), supersedes="wrong")
    commit(client, collection, inconsistent)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.TenantLegalOperatingModelRegistryConflictError):
                target.resolve_current(tenant, BASE + timedelta(days=2), session=session)


def test_real_abort_zero_write_and_registry_owns_no_transaction(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    client, _database, collection = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    target = registry.TenantLegalOperatingModelRegistry(collection)
    with client.start_session() as session:
        session.start_transaction()
        target.create_or_replay(operating_model(tenant), session=session)
        assert session.in_transaction is True
        assert collection.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 0
    assert all(not hasattr(target, name) for name in ("start_transaction", "commit_transaction", "abort_transaction", "commit", "abort", "update", "delete", "replace"))


def test_real_competing_exact_and_divergent_consumers_leave_one_truth(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    client, _database, collection = mongo_context

    def race(values: tuple[TenantLegalOperatingModel, TenantLegalOperatingModel]) -> list[str]:
        barrier = Barrier(2)

        def contender(value: TenantLegalOperatingModel) -> str:
            with client.start_session() as session:
                session.start_transaction()
                barrier.wait()
                try:
                    registry.TenantLegalOperatingModelRegistry(collection).create_or_replay(value, session=session)
                    session.commit_transaction()
                    return "COMMITTED"
                except registry.TenantLegalOperatingModelRegistryConflictError:
                    if session.in_transaction:
                        session.abort_transaction()
                    return "CONFLICT"
                except registry.TenantLegalOperatingModelRegistryRetryTransactionError:
                    if session.in_transaction:
                        session.abort_transaction()
                    return "RETRY_REQUIRED"
                except PyMongoError:
                    if session.in_transaction:
                        session.abort_transaction()
                    return "MONGO_RETRY_REQUIRED"

        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(contender, values))

    exact = operating_model(f"tenant-exact-race-{uuid.uuid4().hex}")
    exact_outcomes = race((exact, exact))
    assert "COMMITTED" in exact_outcomes
    assert all(item in {"COMMITTED", "RETRY_REQUIRED", "MONGO_RETRY_REQUIRED"} for item in exact_outcomes)
    assert collection.count_documents({"tenant_id": exact.tenant_id}) == 1
    tenant = f"tenant-divergent-race-{uuid.uuid4().hex}"
    left = operating_model(tenant, items=("PERSONA_PARTNER",))
    right = operating_model(tenant, items=("RISK_CONFLICTS",))
    divergent_outcomes = race((left, right))
    assert "COMMITTED" in divergent_outcomes
    assert all(item in {"COMMITTED", "CONFLICT", "RETRY_REQUIRED", "MONGO_RETRY_REQUIRED"} for item in divergent_outcomes)
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_failure_translation_and_restart_readback(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    client, _database, collection = mongo_context
    tenant = f"tenant-restart-{uuid.uuid4().hex}"
    value = operating_model(tenant)
    commit(client, collection, value)
    restarted = registry.TenantLegalOperatingModelRegistry(collection)
    with client.start_session() as session:
        with session.start_transaction():
            assert restarted.get_by_id(tenant, value.operating_model_id, session=session) == value

    class BrokenCollection:
        def find_one(self, query: Mapping[str, object], *, session: object) -> None:
            raise OperationFailure("synthetic real-certificate outage")

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.TenantLegalOperatingModelRegistryPersistenceError):
            registry.TenantLegalOperatingModelRegistry(BrokenCollection()).get_by_id(tenant, value.operating_model_id, session=session)
        session.abort_transaction()


# ARTIFACT: test_tenant_legal_operating_model_registry_real_mongo.py
# VERSION: v1.0.0-CX26-R2-DURABLE-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable configuration persistence/currentness proof only
# TENANT POSTURE: UUID-isolated database and exact synthetic tenant predicates
# FAIL-CLOSED POSTURE: topology, transaction, corruption, ambiguity, race, rollback, and outage fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN CERTIFICATE
