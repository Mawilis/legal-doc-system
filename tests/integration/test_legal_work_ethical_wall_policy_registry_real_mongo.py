"""TITLE: WILSY OS G76-B Ethical Wall Registry Real-Mongo Certificate.
VERSION: v1.0.0-G76-B-REAL-MONGO-CERT
AUTHORITY: Disposable replica-set transaction evidence only.
EPITOME: Certifies indexes, atomic revision/currentness writes, replay,
    concurrency, terminal revocation, isolation and corruption fail-closure.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_work_ethical_wall_policy_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 introduces disposable real-Mongo G76-B proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID database and opaque fixtures; no production data.
TENANT BOUNDARY: Exact tenant, matter and policy scope.
AUTHORITY BOUNDARY: Durable evidence does not authorize operational access.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
import os
import threading
import uuid
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_work_ethical_wall_policy import (
    EthicalWallPolicyRevision as Revision,
    EthicalWallPolicyStatus,
    InstitutionalRatificationState,
)
from tools.eos.legal_operations.registry import (
    legal_work_ethical_wall_policy_registry as reg,
)

URI = os.environ["WILSY_G76_REAL_MONGO_URI"]
NOW = datetime(2026, 10, 21, 14, 0, tzinfo=UTC)


def revision(**changes: object) -> Revision:
    values: dict[str, object] = {
        "policy_id": "wall-1", "revision": 1, "predecessor_fingerprint": None,
        "tenant_id": "tenant-a", "case_matter_id": "matter-a",
        "protected_subject_fingerprints": ("a" * 128,),
        "restricted_principal_ids": ("principal-denied",),
        "permitted_principal_ids": ("principal-allowed",),
        "status": EthicalWallPolicyStatus.ACTIVE,
        "effective_from": NOW, "effective_until": NOW + timedelta(days=30),
        "source_evidence_reference": "source-1",
        "source_evidence_fingerprint": "b" * 128,
        "administrator_principal_id": "admin-1",
        "administrator_authorization_reference": "admin-auth-1",
        "administrator_authorization_fingerprint": "c" * 128,
        "ratification_state": InstitutionalRatificationState.APPROVED,
        "ratification_reference": "ratification-1",
        "ratification_fingerprint": "d" * 128,
    }
    values.update(changes)
    return Revision(**values)  # type: ignore[arg-type]


def successor(root: Revision, **changes: object) -> Revision:
    values: dict[str, object] = {
        "revision": root.revision + 1,
        "predecessor_fingerprint": root.fingerprint,
        "effective_from": root.effective_from + timedelta(days=1),
    }
    values.update(changes)
    return replace(root, **values)


@pytest.fixture()
def mongo_context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI, serverSelectionTimeoutMS=5000, uuidRepresentation="standard",
        tz_aware=True, tzinfo=UTC,
    )
    hello = client.admin.command("hello")
    assert hello.get("setName")
    assert hello.get("isWritablePrimary") is True
    database = client["wilsy_g76_" + uuid.uuid4().hex]
    revisions = database[reg.REVISION_COLLECTION]
    current = database[reg.CURRENT_COLLECTION]
    registry = reg.EthicalWallPolicyRegistry(revisions, current)
    registry.ensure_indexes()
    try:
        yield client, database, revisions, current, registry
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_indexes_are_unique_and_never_ttl(mongo_context: Any) -> None:
    _, _, revisions, current, _ = mongo_context
    indexes = list(revisions.list_indexes()) + list(current.list_indexes())
    named = {item["name"]: item for item in indexes}
    assert set(reg.INDEX_NAMES).issubset(named)
    assert sum(named[name].get("unique") is True for name in reg.INDEX_NAMES) == 5
    assert all("expireAfterSeconds" not in named[name] for name in reg.INDEX_NAMES)


def test_real_initial_exact_replay_and_currentness(mongo_context: Any) -> None:
    client, _, revisions, current, registry = mongo_context
    root = revision()
    for _ in range(2):
        with client.start_session() as session:
            with session.start_transaction():
                assert registry.append(root, session=session) == root
    with client.start_session() as session:
        with session.start_transaction():
            assert registry.get_current("tenant-a", "matter-a", "wall-1", session=session) == root
    assert revisions.count_documents({}) == 1
    assert current.count_documents({}) == 1


def test_real_divergent_and_stale_revisions_reject(mongo_context: Any) -> None:
    client, _, revisions, _, registry = mongo_context
    root = revision()
    first = successor(root, source_evidence_reference="source-2")
    with client.start_session() as session:
        with session.start_transaction():
            registry.append(root, session=session)
            registry.append(first, session=session)
    with pytest.raises(reg.EthicalWallPolicyConflict, match="DIVERGENT_REPLAY"):
        with client.start_session() as session:
            with session.start_transaction():
                registry.append(replace(first, source_evidence_reference="fork"), session=session)
    stale = replace(first, revision=3, predecessor_fingerprint=root.fingerprint,
                    effective_from=first.effective_from + timedelta(days=1))
    with pytest.raises(reg.EthicalWallPolicyConflict, match="STALE_REVISION"):
        with client.start_session() as session:
            with session.start_transaction():
                registry.append(stale, session=session)
    assert revisions.count_documents({}) == 2


def test_real_competing_writers_leave_one_authoritative_successor(mongo_context: Any) -> None:
    client, database, revisions, current, registry = mongo_context
    root = revision()
    with client.start_session() as session:
        with session.start_transaction():
            registry.append(root, session=session)
    candidates = (
        successor(root, source_evidence_reference="competing-a"),
        successor(root, source_evidence_reference="competing-b"),
    )
    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    lock = threading.Lock()

    def writer(candidate: Revision) -> None:
        thread_client: MongoClient[Any] = MongoClient(
            URI, serverSelectionTimeoutMS=5000, tz_aware=True, tzinfo=UTC,
        )
        thread_registry = reg.EthicalWallPolicyRegistry(
            thread_client[database.name][reg.REVISION_COLLECTION],
            thread_client[database.name][reg.CURRENT_COLLECTION],
        )
        try:
            barrier.wait(timeout=5)
            with thread_client.start_session() as session:
                with session.start_transaction():
                    thread_registry.append(candidate, session=session)
            result = "committed"
        except Exception as error:  # competing loser may surface at write or commit
            result = type(error).__name__
        finally:
            thread_client.close()
        with lock:
            outcomes.append(result)

    threads = [threading.Thread(target=writer, args=(item,)) for item in candidates]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    assert len(outcomes) == 2
    assert outcomes.count("committed") == 1
    assert revisions.count_documents({"revision": 2}) == 1
    pointer = current.find_one({"tenant_id": "tenant-a", "case_matter_id": "matter-a", "policy_id": "wall-1"})
    assert pointer is not None and pointer["revision"] == 2


def test_real_terminal_revocation_cannot_reopen(mongo_context: Any) -> None:
    client, _, revisions, _, registry = mongo_context
    root = revision()
    revoked = successor(
        root, status=EthicalWallPolicyStatus.REVOKED,
        ratification_state=InstitutionalRatificationState.REVOKED,
        ratification_reference="ratification-revoked",
        ratification_fingerprint="e" * 128,
    )
    with client.start_session() as session:
        with session.start_transaction():
            registry.append(root, session=session)
            registry.append(revoked, session=session)
    with pytest.raises(reg.EthicalWallPolicyConflict, match="TERMINAL_REVOKED"):
        with client.start_session() as session:
            with session.start_transaction():
                registry.append(successor(
                    revoked, status=EthicalWallPolicyStatus.ACTIVE,
                    ratification_state=InstitutionalRatificationState.APPROVED,
                ), session=session)
    assert revisions.count_documents({}) == 2


def test_real_failed_pointer_insert_aborts_revision_atomically(mongo_context: Any) -> None:
    client, _, revisions, current, registry = mongo_context
    current.insert_one({
        "tenant_id": "tenant-a", "case_matter_id": "matter-a", "policy_id": "wall-1",
        "revision": 99, "fingerprint": "f" * 128, "status": "ACTIVE",
        "effective_from": NOW,
    })
    with pytest.raises(reg.EthicalWallPolicyRetryTransaction):
        with client.start_session() as session:
            with session.start_transaction():
                registry.append(revision(), session=session)
    assert revisions.count_documents({}) == 0


def test_real_corruption_and_cross_scope_reads_fail_closed(mongo_context: Any) -> None:
    client, _, revisions, _, registry = mongo_context
    root = revision()
    with client.start_session() as session:
        with session.start_transaction():
            registry.append(root, session=session)
            assert registry.list_history("tenant-b", "matter-a", "wall-1", session=session) == ()
            assert registry.list_history("tenant-a", "matter-b", "wall-1", session=session) == ()
    revisions.update_one({"fingerprint": root.fingerprint}, {"$set": {"fingerprint": "f" * 128}})
    with pytest.raises(reg.EthicalWallPolicyPersistedInvalid):
        with client.start_session() as session:
            with session.start_transaction():
                registry.get_current("tenant-a", "matter-a", "wall-1", session=session)


def test_real_inactive_transaction_rejects_without_write(mongo_context: Any) -> None:
    client, _, revisions, _, registry = mongo_context
    with client.start_session() as session:
        with pytest.raises(reg.EthicalWallPolicyTransactionRequired):
            registry.append(revision(), session=session)
    assert revisions.count_documents({}) == 0


# ARTIFACT: test_legal_work_ethical_wall_policy_registry_real_mongo.py
# VERSION: v1.0.0-G76-B-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable transaction evidence only; no access grant
# TENANT POSTURE: exact tenant/matter/policy and corruption-blocked
# FAIL-CLOSED POSTURE: races, revocation, malformed state and transaction absence block
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
