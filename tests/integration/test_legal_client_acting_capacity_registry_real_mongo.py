"""Real-Mongo certificate for the durable L9A4-P1A2 capacity registry.

TITLE: WILSY OS Legal Client Acting Capacity Registry Real-Mongo Certificate
VERSION: v1.0.0-L9A4-P1A2-CLIENT-ACTING-CAPACITY-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Direct physical certification of immutable capacity persistence.
EPITOME: Prove the sanctioned replica-set topology, caller-owned transactions,
         exact indexes, replay/collision behavior, tenant and context isolation,
         immutable validity queries, UTC microsecond preservation, corruption
         rejection, rollback, concurrency and absence of unrelated authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_acting_capacity_registry_real_mongo.py
COLLABORATION / OWNERSHIP: The L9A4-P1A2 registry is the production subject;
                            this certificate owns only synthetic disposable
                            Mongo evidence. No canonical/shared database,
                            acceptance, engagement, representation, Court or
                            financial record is touched.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P1A2-CLIENT-ACTING-CAPACITY-REGISTRY-REAL-MONGO-CERT
           establishes physical index, transaction, replay, collision, scope,
           validity, corruption, rollback and competing-consumer evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated disposable database and synthetic
                             opaque values only; no secrets, tokens, PII,
                             production URI or canonical records are printed.
TENANT BOUNDARY: All assertions use exact synthetic tenant predicates.
AUTHORITY BOUNDARY: Physical persistence evidence only; no capacity issuance
                    or runtime authorization is created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Tests own every session and transaction; the registry
                      must not start, commit, abort or retry them.
FAIL-CLOSED DECLARATION: Topology, transaction, corruption, conflict, race or
                         rollback failure fails certification; no skips are used.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    ACTING_CAPACITY_FIELDS,
    LegalClientActingCapacity,
    LegalClientActingCapacityType,
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import (
    legal_client_acting_capacity_registry as registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 26, 14, 0, 0, 654321, tzinfo=timezone.utc)
SUBJECT_FP = "a" * 128
PARTY_SOURCE_FP = "b" * 128
CAPACITY_SOURCE_FP = "c" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Provide one writable loopback replica set and drop only its UUID DB."""
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
            pytest.fail(f"L9A4_P1A2_MONGO_UNAVAILABLE:{type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail("L9A4_P1A2_WRONG_REPLICA_SET")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L9A4_P1A2_NO_WRITABLE_PRIMARY")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("L9A4_P1A2_SESSIONS_UNAVAILABLE")

        database = client[f"wilsy_l9a4_p1a2_capacity_{uuid.uuid4().hex}"]
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
        matter_reference=f"CASE-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"matter-source:{matter_id}",
    )


def _capacity(
    tenant: str,
    *,
    capacity_id: str = "capacity-1",
    matter_id: str = "matter-1",
    principal_id: str = "principal-1",
    capacity_type: LegalClientActingCapacityType = LegalClientActingCapacityType.SELF,
    effective_from: datetime = NOW + timedelta(minutes=1),
    effective_until: datetime | None = NOW + timedelta(days=30),
) -> LegalClientActingCapacity:
    source_matter = _matter(tenant, matter_id)
    party = register_legal_matter_party(
        matter=source_matter,
        party_id=f"party-{matter_id}",
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="organization:synthetic-client",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic presentation",
        registered_at=NOW,
        source_evidence_reference=f"party-source:{matter_id}",
        source_evidence_fingerprint=PARTY_SOURCE_FP,
    )
    return record_legal_client_acting_capacity(
        case_matter=source_matter,
        party=party,
        capacity_id=capacity_id,
        principal_id=principal_id,
        capacity_type=capacity_type,
        effective_from=effective_from,
        effective_until=effective_until,
        source_evidence_reference=f"capacity-source:{capacity_id}",
        source_evidence_fingerprint=CAPACITY_SOURCE_FP,
    )


def _commit(
    client: MongoClient[Any],
    collection: Any,
    value: LegalClientActingCapacity,
) -> LegalClientActingCapacity:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_capacity(value, collection, session=session)


def test_real_topology_is_writable_replica_set_with_sessions_and_transactions(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, _ = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None


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
        registry.CAPACITY_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.MATTER_PRINCIPAL_INDEX_NAME,
        registry.MATTER_PARTY_INDEX_NAME,
        registry.MATTER_EFFECTIVE_INDEX_NAME,
    }
    assert dict(indexes[registry.CAPACITY_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "capacity_id": 1,
    }
    assert dict(indexes[registry.FINGERPRINT_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "fingerprint": 1,
    }
    assert indexes[registry.CAPACITY_ID_INDEX_NAME].get("unique") is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_real_commit_exact_replay_row_count_and_utc_microseconds(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-replay-{uuid.uuid4().hex}"
    value = _capacity(tenant)
    assert _commit(client, collection, value) == value
    assert _commit(client, collection, value) == value
    assert collection.count_documents({"tenant_id": tenant}) == 1
    with client.start_session() as session:
        with session.start_transaction():
            readback = registry.get_capacity_by_fingerprint(
                tenant, value.fingerprint, collection, session=session
            )
            assert readback.effective_from.tzinfo is not None
            assert readback.effective_from.utcoffset() == timezone.utc.utcoffset(NOW)
            assert readback.effective_from.microsecond == 654321
    raw = collection.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)
    assert raw["effective_from"] == "2026-09-26T14:01:00.654321Z"
    assert raw["effective_until"] == "2026-10-26T14:00:00.654321Z"


def test_real_tenant_matter_principal_party_reads_are_exactly_scoped(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    first = _capacity(tenant_a, capacity_id="capacity-a", principal_id="principal-a")
    second = _capacity(tenant_a, capacity_id="capacity-b", principal_id="principal-b")
    foreign = _capacity(tenant_b, capacity_id="capacity-foreign", principal_id="principal-a")
    for value in (first, second, foreign):
        assert _commit(client, collection, value) == value
    with client.start_session() as session:
        with session.start_transaction():
            principal_values = registry.list_matter_principal_capacities(
                tenant_a, first.case_matter_id, "principal-a", collection, session=session
            )
            party_values = registry.list_matter_party_capacities(
                tenant_a, first.case_matter_id, first.party_id, collection, session=session
            )
            assert [item.capacity_id for item in principal_values] == ["capacity-a"]
            assert [item.capacity_id for item in party_values] == ["capacity-b", "capacity-a"]
            with pytest.raises(registry.LegalClientActingCapacityRegistryNotFoundError):
                registry.get_capacity(tenant_a, foreign.capacity_id, collection, session=session)
    assert collection.count_documents({"tenant_id": tenant_a}) == 2
    assert collection.count_documents({"tenant_id": tenant_b}) == 1


def test_real_validity_excludes_expired_and_future_and_keeps_open_ended(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-validity-{uuid.uuid4().hex}"
    expired = _capacity(
        tenant,
        capacity_id="capacity-expired",
        effective_from=NOW - timedelta(days=3),
        effective_until=NOW - timedelta(days=1),
    )
    future = _capacity(
        tenant,
        capacity_id="capacity-future",
        effective_from=NOW + timedelta(days=3),
        effective_until=NOW + timedelta(days=4),
    )
    open_ended = _capacity(
        tenant,
        capacity_id="capacity-open",
        effective_from=NOW - timedelta(days=2),
        effective_until=None,
    )
    for value in (expired, future, open_ended):
        _commit(client, collection, value)
    with client.start_session() as session:
        with session.start_transaction():
            valid = registry.list_valid_capacities_at(
                tenant, open_ended.case_matter_id, NOW, collection, session=session
            )
            assert [item.capacity_id for item in valid] == ["capacity-open"]
            assert valid[0].effective_until is None


def test_real_divergent_collision_fails_without_update_or_delete(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-conflict-{uuid.uuid4().hex}"
    first = _capacity(tenant)
    _commit(client, collection, first)
    divergent = _capacity(tenant, principal_id="principal-other")
    before = deepcopy(collection.find_one({"tenant_id": tenant}))
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientActingCapacityRegistryConflictError):
            registry.persist_capacity(divergent, collection, session=session)
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 1
    assert collection.find_one({"tenant_id": tenant}) == before


def test_real_corruption_is_rejected_before_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _capacity(tenant)
    _commit(client, collection, value)
    original = deepcopy(collection.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)
    collection.update_one(
        {"tenant_id": tenant},
        {"$set": {"source_evidence_fingerprint": "d" * 128}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientActingCapacityRegistryPersistedRecordInvalidError):
                registry.get_capacity(tenant, value.capacity_id, collection, session=session)
    collection.replace_one({"_id": original["_id"]}, original)
    collection.update_one({"tenant_id": tenant}, {"$set": {"unexpected": True}})
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientActingCapacityRegistryPersistedRecordInvalidError):
                registry.get_capacity(tenant, value.capacity_id, collection, session=session)
    collection.replace_one({"_id": original["_id"]}, original)


def test_real_caller_abort_leaves_zero_rows(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _capacity(tenant)
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_capacity(value, collection, session=session)
        assert collection.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 0


def test_real_competing_consumers_do_not_duplicate(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    value = _capacity(tenant)
    barrier = Barrier(2)

    def contender(_: int) -> str:
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                registry.persist_capacity(value, collection, session=session)
                session.commit_transaction()
                return "COMMITTED"
            except registry.LegalClientActingCapacityRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"
            except registry.LegalClientActingCapacityRegistryConflictError:
                if session.in_transaction:
                    session.abort_transaction()
                return "CONFLICT"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(contender, (1, 2)))
    assert all(outcome in {"COMMITTED", "RETRY_REQUIRED", "CONFLICT"} for outcome in outcomes)
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_row_shape_has_only_domain_fields_and_no_other_authority_writes(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, database, collection = mongo_context
    tenant = f"tenant-shape-{uuid.uuid4().hex}"
    value = _capacity(tenant)
    _commit(client, collection, value)
    row = collection.find_one({"tenant_id": tenant})
    assert isinstance(row, dict)
    assert set(row) == set(ACTING_CAPACITY_FIELDS) | {"_id"}
    assert not {
        "acceptance_id", "engagement_id", "representation_id",
        "court_proceeding_id", "financial_authority",
    } & set(row)
    assert set(database.list_collection_names()) == {registry.COLLECTION}


# ARTIFACT: test_legal_client_acting_capacity_registry_real_mongo.py
# VERSION: v1.0.0-L9A4-P1A2-CLIENT-ACTING-CAPACITY-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable acting-capacity persistence/read evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant/matter/principal/party queries
# FAIL-CLOSED POSTURE: rollback/corruption/conflict/concurrency cannot create duplicate capacity truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
