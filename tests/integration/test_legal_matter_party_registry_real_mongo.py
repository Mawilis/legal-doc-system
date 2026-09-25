"""Real-Mongo certificate for L8-8B durable legal matter-party registry.

VERSION: v1.0.0-L8-8B-LEGAL-MATTER-PARTY-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_matter_party_registry_real_mongo.py
TRANSACTION BOUNDARY: Test caller owns all sessions/transactions.
AUTHORITY BOUNDARY: Physical party persistence/read evidence only.
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

from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import legal_matter_party_registry as registry


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 14, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


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

        database = client[f"wilsy_l8_8b_party_{uuid.uuid4().hex}"]
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


def _matter(
    tenant: str,
    matter_id: str = "matter-1",
) -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def _party(
    tenant: str,
    *,
    matter_id: str = "matter-1",
    party_id: str = "party-1",
    subject_fp: str = FP_A,
    subject_ref: str = "organization:acme",
    name: str = "Acme Legal",
) -> LegalMatterParty:
    return register_legal_matter_party(
        matter=_matter(tenant, matter_id),
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference=subject_ref,
        subject_identity_fingerprint=subject_fp,
        display_name=name,
        registered_at=NOW,
        source_evidence_reference=f"party-source:{party_id}",
        source_evidence_fingerprint=FP_B,
    )


def _commit(
    client: MongoClient[Any],
    collection: Any,
    value: LegalMatterParty,
) -> LegalMatterParty:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_party(value, collection, session=session)


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
        registry.PARTY_ID_INDEX_NAME,
        registry.MATTER_SUBJECT_INDEX_NAME,
        registry.MATTER_LOOKUP_INDEX_NAME,
        registry.SUBJECT_LOOKUP_INDEX_NAME,
    }
    assert dict(indexes[registry.PARTY_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "party_id": 1,
    }
    assert indexes[registry.PARTY_ID_INDEX_NAME].get("unique") is True
    assert dict(indexes[registry.MATTER_SUBJECT_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "case_matter_id": 1,
        "subject_identity_fingerprint": 1,
    }
    assert indexes[registry.MATTER_SUBJECT_INDEX_NAME].get("unique") is True
    assert indexes[registry.MATTER_LOOKUP_INDEX_NAME].get("unique") is not True
    assert indexes[registry.SUBJECT_LOOKUP_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_real_commit_replay_tenant_isolation_and_subject_lookup(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    first = _party(tenant_a, matter_id="matter-1", party_id="party-b")
    second = _party(tenant_a, matter_id="matter-2", party_id="party-a")
    foreign = _party(tenant_b, matter_id="matter-1", party_id="party-b")

    assert _commit(client, collection, first) == first
    assert _commit(client, collection, first) == first
    assert _commit(client, collection, second) == second
    assert _commit(client, collection, foreign) == foreign

    with client.start_session() as session:
        with session.start_transaction():
            occurrences = registry.find_subject_occurrences(
                tenant_a,
                FP_A,
                collection,
                session=session,
            )
            assert [(item.case_matter_id, item.party_id) for item in occurrences] == [
                ("matter-1", "party-b"),
                ("matter-2", "party-a"),
            ]
            matter_values = registry.list_matter_parties(
                tenant_a,
                "matter-1",
                collection,
                session=session,
            )
            assert [item.party_id for item in matter_values] == ["party-b"]
            with pytest.raises(registry.LegalMatterPartyRegistryNotFoundError):
                registry.get_party(
                    tenant_b,
                    "party-a",
                    collection,
                    session=session,
                )


def test_real_caller_abort_rolls_back_party_insert(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _party(tenant)

    with client.start_session() as session:
        session.start_transaction()
        registry.persist_party(value, collection, session=session)
        assert collection.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()

    assert collection.count_documents({"tenant_id": tenant}) == 0


def test_real_divergent_identity_and_matter_subject_conflicts_fail_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-conflict-{uuid.uuid4().hex}"
    first = _party(tenant)
    _commit(client, collection, first)

    divergent = _party(tenant, name="Different Name")
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalMatterPartyRegistryConflictError):
            registry.persist_party(divergent, collection, session=session)
        session.abort_transaction()

    alias_identity = _party(tenant, party_id="party-alias")
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalMatterPartyRegistryConflictError) as raised:
            registry.persist_party(alias_identity, collection, session=session)
        assert raised.value.code == "L8_8B_MATTER_SUBJECT_CONFLICT"
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_corruption_is_rejected_before_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _party(tenant)
    _commit(client, collection, value)
    original = deepcopy(collection.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)

    collection.update_one(
        {"tenant_id": tenant},
        {"$set": {"party_payload.display_name": "Tampered"}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.LegalMatterPartyRegistryPersistedRecordInvalidError
            ):
                registry.get_party(
                    tenant,
                    value.party_id,
                    collection,
                    session=session,
                )

    collection.replace_one({"_id": original["_id"]}, original)


def test_real_competing_same_matter_subject_has_one_commit_and_one_retry(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    left = _party(tenant, party_id="party-left")
    right = _party(tenant, party_id="party-right")
    barrier = Barrier(2)

    def contender(value: LegalMatterParty) -> str:
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                registry.persist_party(value, collection, session=session)
                session.commit_transaction()
                return "COMMITTED"
            except registry.LegalMatterPartyRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"
            except registry.LegalMatterPartyRegistryConflictError:
                if session.in_transaction:
                    session.abort_transaction()
                return "CONFLICT"
            except Exception as error:
                if session.in_transaction:
                    session.abort_transaction()
                return type(error).__name__

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(contender, (left, right)))

    assert outcomes.count("COMMITTED") == 1
    assert sum(
        outcome in {"RETRY_REQUIRED", "CONFLICT"}
        for outcome in outcomes
    ) == 1
    assert collection.count_documents({"tenant_id": tenant}) == 1
    row = collection.find_one({"tenant_id": tenant})
    assert isinstance(row, dict)
    assert row["party_id"] in {"party-left", "party-right"}


# ARTIFACT: test_legal_matter_party_registry_real_mongo.py
# VERSION: v1.0.0-L8-8B-LEGAL-MATTER-PARTY-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable party persistence/read evidence only
# TENANT POSTURE: UUID-isolated database and tenant-scoped indexes/queries
# FAIL-CLOSED POSTURE: rollback/conflict/corruption/concurrency cannot create duplicate party truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
