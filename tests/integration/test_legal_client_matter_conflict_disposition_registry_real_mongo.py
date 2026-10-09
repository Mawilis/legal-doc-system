"""Real-Mongo certificate for the L9C3 conflict-disposition registry.

TITLE: WILSY OS Legal Client Matter Conflict Disposition Registry Real-Mongo Certificate
VERSION: v1.0.0-L9C4-CONFLICT-DISPOSITION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published immutable disposition registry against a
         writable disposable Mongo replica set: physical indexes, caller-owned
         commit/rollback, exact replay, collision rejection, tenant isolation,
         bounded history, strict corruption rejection and synchronized races.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_conflict_disposition_registry_real_mongo.py
COLLABORATION / OWNERSHIP: L9C3 owns the registry contract; this certificate
                            owns only disposable runtime evidence. Currentness,
                            IAM, Engagement, Representation, Court and finance
                            remain outside this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-27
TRANSACTION BOUNDARY: Every operation uses a real caller-owned session and
                      transaction; the registry never owns that lifecycle.
FAIL-CLOSED DECLARATION: A yielded fixture failure is a certificate failure;
                         infrastructure unavailability is skipped explicitly
                         for operator execution and never represented as pass.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDisposition,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_conflict_disposition_registry as registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 27, 20, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
FP_D = "d" * 128
FP_E = "e" * 128
FP_F = "f" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one UUID-isolated disposable collection after topology checks."""
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
            server_version = client.server_info().get("version")
        except PyMongoError as error:
            pytest.skip(
                f"real Mongo unavailable for operator runtime: {type(error).__name__}"
            )
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version, str) and server_version

        database_name = f"wilsy_l9c4_disp_reg_{uuid.uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
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


def _disposition(
    *,
    tenant_id: str = "tenant-a-l9c4",
    disposition_id: str = "disp-l9c4-1",
    idempotency_key: str = "disp-idempotency-l9c4-1",
    conflict_review_id: str = "review-l9c4-1",
    conflict_review_fingerprint: str = FP_B,
    occurred_offset: int = 0,
) -> LegalClientMatterConflictDisposition:
    """Build synthetic valid evidence without reading or writing upstream data."""
    occurred = NOW + timedelta(minutes=occurred_offset)
    return LegalClientMatterConflictDisposition(
        disposition_id=disposition_id,
        tenant_id=tenant_id,
        case_matter_id="matter-l9c4",
        matter_fingerprint=FP_A,
        screening_id="screening-l9c4",
        screening_fingerprint=FP_C,
        conflict_review_id=conflict_review_id,
        conflict_review_fingerprint=conflict_review_fingerprint,
        review_outcome="NO_CONFLICT_IDENTIFIED",
        client_party_id="party-l9c4",
        subject_identity_fingerprint=FP_D,
        disposition="ENGAGEMENT_PERMITTED",
        decision_actor_principal_id="principal-l9c4",
        authorization_evidence_reference="iam:l9c4:authorization",
        authorization_evidence_fingerprint=FP_E,
        supporting_evidence_reference="review:l9c4:evidence",
        supporting_evidence_fingerprint=FP_F,
        occurred_at=occurred,
        effective_from=occurred,
        idempotency_key=idempotency_key,
    )


def _commit(
    client: MongoClient[Any], collection: Any, value: LegalClientMatterConflictDisposition
) -> LegalClientMatterConflictDisposition:
    with client.start_session() as session:
        session.start_transaction()
        result = registry.persist_disposition(value, collection, session=session)
        session.commit_transaction()
        return result


def _read(
    client: MongoClient[Any], collection: Any, tenant_id: str, disposition_id: str
) -> LegalClientMatterConflictDisposition:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.get_disposition(
                tenant_id,
                disposition_id,
                collection,
                session=session,
            )


def test_real_index_metadata_is_exact_and_has_no_ttl_or_current_pointer(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Physical indexes match the published immutable-history contract."""
    _, database, collection = mongo_context
    indexes = {
        entry["name"]: entry
        for entry in collection.list_indexes()
        if entry["name"] != "_id_"
    }
    assert database.name != "wilsy"
    assert set(indexes) == {
        registry.DISPOSITION_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.REVIEW_LINEAGE_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
        registry.MATTER_FINGERPRINT_HISTORY_INDEX_NAME,
        registry.CLIENT_PARTY_HISTORY_INDEX_NAME,
        registry.SUBJECT_HISTORY_INDEX_NAME,
    }
    assert dict(indexes[registry.DISPOSITION_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "disposition_id": 1,
    }
    assert indexes[registry.DISPOSITION_ID_INDEX_NAME].get("unique") is True
    assert dict(indexes[registry.FINGERPRINT_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "fingerprint": 1,
    }
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert indexes[registry.IDEMPOTENCY_INDEX_NAME].get("unique") is True
    assert indexes[registry.REVIEW_LINEAGE_INDEX_NAME].get("unique") is True
    assert all("expireAfterSeconds" not in entry for entry in indexes.values())


def test_real_transaction_requires_caller_active_transaction(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Missing and inactive sessions fail before any write."""
    client, _, collection = mongo_context
    value = _disposition()
    with pytest.raises(registry.LegalClientMatterConflictDispositionRegistryTransactionRequiredError):
        registry.persist_disposition(value, collection, session=None)
    with client.start_session() as session:
        with pytest.raises(registry.LegalClientMatterConflictDispositionRegistryTransactionRequiredError):
            registry.persist_disposition(value, collection, session=session)


def test_real_commit_durability_and_exact_hydration(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """External commit makes one exact row visible to a new transaction."""
    client, _, collection = mongo_context
    value = _disposition()
    assert _commit(client, collection, value) == value
    assert _read(client, collection, value.tenant_id, value.disposition_id) == value
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_abort_rolls_back_without_registry_override(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """External abort leaves no observable durable disposition."""
    client, _, collection = mongo_context
    value = _disposition()
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_disposition(value, collection, session=session)
        assert collection.count_documents({"tenant_id": value.tenant_id}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 0


def test_real_exact_replay_has_one_semantic_row(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Exact replay reconciles to existing evidence without another insert."""
    client, _, collection = mongo_context
    value = _disposition()
    assert _commit(client, collection, value) == value
    assert _commit(client, collection, value) == value
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_divergent_disposition_id_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """One tenant/disposition identity cannot be rebound."""
    client, _, collection = mongo_context
    value = _disposition()
    _commit(client, collection, value)
    divergent = _disposition(
        idempotency_key="different-idempotency",
        conflict_review_id="different-review",
        conflict_review_fingerprint="1" * 128,
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientMatterConflictDispositionRegistryConflictError):
                registry.persist_disposition(divergent, collection, session=session)
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_divergent_idempotency_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """One tenant/idempotency identity cannot be rebound."""
    client, _, collection = mongo_context
    value = _disposition()
    _commit(client, collection, value)
    divergent = _disposition(
        disposition_id="different-disposition",
        idempotency_key=value.idempotency_key,
        conflict_review_id="different-review",
        conflict_review_fingerprint="1" * 128,
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientMatterConflictDispositionRegistryConflictError):
                registry.persist_disposition(divergent, collection, session=session)
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_review_lineage_is_unique_but_later_review_is_allowed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """One review lineage has one disposition; a later lineage is history."""
    client, _, collection = mongo_context
    first = _disposition()
    _commit(client, collection, first)
    divergent = _disposition(
        disposition_id="different-disposition",
        idempotency_key="different-idempotency",
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientMatterConflictDispositionRegistryConflictError):
                registry.persist_disposition(divergent, collection, session=session)
    later = _disposition(
        disposition_id="disp-l9c4-2",
        idempotency_key="disp-idempotency-l9c4-2",
        conflict_review_id="review-l9c4-2",
        conflict_review_fingerprint="1" * 128,
        occurred_offset=1,
    )
    assert _commit(client, collection, later) == later
    assert collection.count_documents({"tenant_id": first.tenant_id}) == 2


def test_real_tenant_scoped_identity_and_history_isolation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Overlapping opaque identities remain isolated by tenant in every read."""
    client, _, collection = mongo_context
    tenant_a = _disposition(tenant_id="tenant-a")
    tenant_b = _disposition(tenant_id="tenant-b")
    tenant_b_only = _disposition(
        tenant_id="tenant-b",
        disposition_id="disp-b-only",
        idempotency_key="disp-b-only-idempotency",
        conflict_review_id="review-b-only",
        conflict_review_fingerprint="1" * 128,
    )
    assert _commit(client, collection, tenant_a) == tenant_a
    assert _commit(client, collection, tenant_b) == tenant_b
    assert _commit(client, collection, tenant_b_only) == tenant_b_only
    assert collection.count_documents({}) == 3
    assert _read(client, collection, "tenant-a", tenant_a.disposition_id) == tenant_a
    assert _read(client, collection, "tenant-b", tenant_b.disposition_id) == tenant_b
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientMatterConflictDispositionRegistryNotFoundError):
                registry.get_disposition(
                    "tenant-a", tenant_b_only.disposition_id, collection, session=session
                )
            with pytest.raises(registry.LegalClientMatterConflictDispositionRegistryNotFoundError):
                registry.get_disposition_by_fingerprint(
                    "tenant-a", tenant_b.fingerprint, collection, session=session
                )
            with pytest.raises(registry.LegalClientMatterConflictDispositionRegistryNotFoundError):
                registry.get_disposition_by_fingerprint(
                    "tenant-a", tenant_b_only.fingerprint, collection, session=session
                )
            tenant_a_history = registry.list_dispositions_for_matter(
                "tenant-a",
                tenant_a.case_matter_id,
                tenant_a.client_party_id,
                collection,
                session=session,
            )
            assert len(tenant_a_history) == 1
            assert all(item.tenant_id == "tenant-a" for item in tenant_a_history)
            tenant_a_fingerprints = {item.fingerprint for item in tenant_a_history}
            assert tenant_a_fingerprints == {tenant_a.fingerprint}
            assert tenant_b.fingerprint not in tenant_a_fingerprints
            assert tenant_b_only.fingerprint not in tenant_a_fingerprints

            tenant_b_history = registry.list_dispositions_for_matter(
                "tenant-b",
                tenant_b.case_matter_id,
                tenant_b.client_party_id,
                collection,
                session=session,
            )
            assert len(tenant_b_history) == 2
            assert all(item.tenant_id == "tenant-b" for item in tenant_b_history)
            tenant_b_fingerprints = {item.fingerprint for item in tenant_b_history}
            assert tenant_b_fingerprints == {
                tenant_b.fingerprint,
                tenant_b_only.fingerprint,
            }
            assert tenant_a.fingerprint not in tenant_b_fingerprints
            assert all(item.tenant_id != tenant_a.tenant_id for item in tenant_b_history)


def test_real_bounded_context_history_preserves_earlier_evidence(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Exact five-dimensional history returns both immutable review lineages."""
    client, _, collection = mongo_context
    first = _disposition()
    later = _disposition(
        disposition_id="disp-l9c4-2",
        idempotency_key="disp-idempotency-l9c4-2",
        conflict_review_id="review-l9c4-2",
        conflict_review_fingerprint="1" * 128,
        occurred_offset=1,
    )
    _commit(client, collection, first)
    _commit(client, collection, later)
    with client.start_session() as session:
        with session.start_transaction():
            history = registry.list_dispositions_for_context(
                first.tenant_id,
                first.case_matter_id,
                first.matter_fingerprint,
                first.client_party_id,
                first.subject_identity_fingerprint,
                collection,
                session=session,
            )
    assert history == (first, later)
    assert history[0].to_dict() == first.to_dict()


@pytest.mark.parametrize(
    "field,value",
    [
        ("fingerprint", "not-a-sha3"),
        ("disposition", "NOT_A_DISPOSITION"),
        ("conflict_review_fingerprint", "not-a-lineage-fingerprint"),
        ("effective_from", "not-a-timestamp"),
    ],
)
def test_real_corrupt_bson_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
    field: str,
    value: object,
) -> None:
    """Malformed durable fields cannot be silently skipped or repaired."""
    client, _, collection = mongo_context
    original = _disposition()
    _commit(client, collection, original)
    stored = collection.find_one({"tenant_id": original.tenant_id})
    assert isinstance(stored, dict)
    tampered = deepcopy(stored)
    tampered[field] = value
    collection.replace_one({"_id": stored["_id"]}, tampered)
    try:
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(registry.LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError):
                    registry.get_disposition(
                        original.tenant_id,
                        original.disposition_id,
                        collection,
                        session=session,
                    )
    finally:
        collection.replace_one({"_id": stored["_id"]}, stored)


def test_real_raw_bson_contains_only_published_domain_fields(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Stored evidence has no current pointer, TTL control or downstream state."""
    client, database, collection = mongo_context
    value = _disposition()
    _commit(client, collection, value)
    row = collection.find_one({"tenant_id": value.tenant_id})
    assert isinstance(row, dict)
    assert set(row) == set(value.to_dict()) | {"_id"}
    forbidden = {"current", "currentness", "latest", "expires_at", "iam", "engagement"}
    assert not forbidden.intersection(row)
    assert database.list_collection_names() == [registry.COLLECTION]


def test_real_concurrent_exact_create_has_at_most_one_row(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Concurrent callers cannot produce duplicate semantic evidence."""
    client, _, collection = mongo_context
    value = _disposition()
    barrier = Barrier(2)

    def contender() -> str:
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                registry.persist_disposition(value, collection, session=session)
                session.commit_transaction()
                return "COMMITTED"
            except registry.LegalClientMatterConflictDispositionRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"
            except registry.LegalClientMatterConflictDispositionRegistryConflictError:
                if session.in_transaction:
                    session.abort_transaction()
                return "CONFLICT"
            except PyMongoError:
                if session.in_transaction:
                    session.abort_transaction()
                return "MONGO_ERROR"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: contender(), (1, 2)))
    assert collection.count_documents({"tenant_id": value.tenant_id}) <= 1
    assert sum(outcome == "COMMITTED" for outcome in outcomes) <= 1
    assert all(outcome in {"COMMITTED", "RETRY_REQUIRED", "CONFLICT", "MONGO_ERROR"} for outcome in outcomes)


def test_real_static_authority_audit_excludes_currentness_and_downstream_writes() -> None:
    """The published production registry has no downstream authority imports."""
    source = Path(
        "tools/eos/legal_operations/registry/legal_client_matter_conflict_disposition_registry.py"
    ).read_text(encoding="utf-8")
    assert "currentness" in source.lower()  # documented exclusion posture
    assert "get_current_disposition" not in source
    assert "latest_effective" not in source
    assert "current_pointer" not in source
    for forbidden in (
        "update_one",
        "replace_one",
        "delete_many",
        "start_transaction",
        "commit_transaction",
        "abort_transaction",
    ):
        assert forbidden not in source


# ARTIFACT: test_legal_client_matter_conflict_disposition_registry_real_mongo.py
# VERSION: v1.0.0-L9C4-CONFLICT-DISPOSITION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable physical disposition persistence/read evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant-scoped indexes/queries
# FAIL-CLOSED POSTURE: rollback/divergence/corruption/race cannot invent disposition truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
