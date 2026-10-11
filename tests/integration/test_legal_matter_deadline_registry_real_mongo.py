"""D2 legal-matter deadline registry real-Mongo certificate.

TITLE: Wilsy OS Legal Matter Deadline Registry Real-Mongo Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY-RM-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify indexes, transactions, replay, isolation, rollback and corruption rejection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system-legal-deadline-engine/tests/integration/test_legal_matter_deadline_registry_real_mongo.py
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY-RM-CERT establishes disposable replica-set evidence.
TENANT BOUNDARY: UUID-isolated database and exact tenant predicates.
TRANSACTION BOUNDARY: Test caller owns every session, transaction, commit and abort.
AUTHORITY BOUNDARY: Physical D1 persistence only; no added authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Infrastructure, index, replay or corruption drift fails.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_matter_deadline import LegalMatterDeadline
from tools.eos.legal_operations.registry import legal_matter_deadline_registry as registry

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
NOW = datetime(2026, 10, 11, 8, 0, tzinfo=timezone.utc)


def deadline(tenant: str, identity: str, *, days: int = 7, title: str = "Deadline") -> LegalMatterDeadline:
    return LegalMatterDeadline(tenant_id=tenant, case_matter_id="matter-1", deadline_id=identity, deadline_kind="FILING", title=title, due_at=NOW + timedelta(days=days), source_type="COURT_ORDER", source_reference=f"evidence:{identity}", source_evidence_fingerprint="a" * 128, jurisdiction_reference="jurisdiction:court-1", created_at=NOW)


@pytest.fixture
def mongo() -> Iterator[tuple[MongoClient[Any], Any]]:
    client: MongoClient[Any] = MongoClient(URI, serverSelectionTimeoutMS=3000, retryWrites=True, tz_aware=True)
    database: Any = None
    hello: dict[str, Any] = {}
    try:
        try: hello = client.admin.command("hello")
        except PyMongoError as error: pytest.fail(f"D2_MONGO_UNAVAILABLE:{type(error).__name__}")
        assert hello.get("setName") == "wilsyVendorCertRS"
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        database = client[f"legal_deadline_d2_{uuid.uuid4().hex}"]
        collection = database.get_collection(registry.COLLECTION, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        registry.ensure_indexes(collection)
        yield client, collection
    finally:
        if database is not None: client.drop_database(database.name)
        client.close()


def commit(client: MongoClient[Any], collection: Any, value: LegalMatterDeadline) -> LegalMatterDeadline:
    with client.start_session() as session:
        with session.start_transaction(): return registry.persist_deadline(value, collection, session=session)


def test_real_index_metadata_is_exact_non_ttl_and_tenant_first(mongo: tuple[MongoClient[Any], Any]) -> None:
    _, collection = mongo
    indexes = {row["name"]: row for row in collection.list_indexes() if row["name"] != "_id_"}
    assert set(indexes) == {registry.TENANT_DEADLINE_UNIQUE_INDEX, registry.MATTER_DEADLINE_INDEX, registry.MATTER_DUE_INDEX, registry.MATTER_STATUS_DUE_INDEX}
    assert dict(indexes[registry.TENANT_DEADLINE_UNIQUE_INDEX]["key"]) == {"tenant_id": 1, "deadline_id": 1}
    assert indexes[registry.TENANT_DEADLINE_UNIQUE_INDEX].get("unique") is True
    assert all("expireAfterSeconds" not in row for row in indexes.values())
    assert all(next(iter(dict(row["key"]))) == "tenant_id" for row in indexes.values())


def test_real_commit_replay_cross_tenant_divergence_and_absence(mongo: tuple[MongoClient[Any], Any]) -> None:
    client, collection = mongo
    left, right = deadline("tenant-a", "deadline-1"), deadline("tenant-b", "deadline-1")
    assert commit(client, collection, left) == left
    assert commit(client, collection, left) == left
    assert commit(client, collection, right) == right
    with client.start_session() as session:
        session.start_transaction()
        assert registry.get_deadline("tenant-a", "deadline-1", collection, session=session) == left
        with pytest.raises(registry.LegalMatterDeadlineRegistryNotFoundError): registry.get_deadline("tenant-c", "deadline-1", collection, session=session)
        with pytest.raises(registry.LegalMatterDeadlineRegistryConflictError): registry.persist_deadline(deadline("tenant-a", "deadline-1", title="Divergent"), collection, session=session)
        session.abort_transaction()
    assert collection.count_documents({"deadline_id": "deadline-1"}) == 2


def test_real_caller_abort_commit_ordering_and_strict_corruption(mongo: tuple[MongoClient[Any], Any]) -> None:
    client, collection = mongo
    aborted = deadline("tenant-x", "deadline-abort")
    with client.start_session() as session:
        session.start_transaction(); registry.persist_deadline(aborted, collection, session=session)
        assert collection.count_documents({"tenant_id": "tenant-x"}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": "tenant-x"}) == 0
    earlier, later = deadline("tenant-x", "deadline-a", days=2), deadline("tenant-x", "deadline-z", days=9)
    for value in (later, earlier): commit(client, collection, value)
    with client.start_session() as session:
        with session.start_transaction(): assert registry.list_matter_deadlines("tenant-x", "matter-1", collection, session=session) == (earlier, later)
    row = collection.find_one({"tenant_id": "tenant-x", "deadline_id": "deadline-a"})
    assert isinstance(row, dict) and set(row) - {"_id"} == set(earlier.to_dict())
    assert not any(key in row for key in ("payment", "settlement", "ai_generated", "overdue"))
    collection.update_one({"_id": row["_id"]}, {"$set": {"title": "tampered"}})
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalMatterDeadlineRegistryPersistedRecordInvalidError): registry.get_deadline("tenant-x", "deadline-a", collection, session=session)


# ARTIFACT: test_legal_matter_deadline_registry_real_mongo.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY-RM-CERT
# AUTHORITY BOUNDARY: physical exact D1 persistence certificate only
# TENANT POSTURE: isolated database and exact tenant-scoped indexes and queries
# FAIL-CLOSED POSTURE: index, transaction, replay, divergence, corruption and infrastructure drift fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
