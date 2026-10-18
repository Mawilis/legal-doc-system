"""WILSY OS authorization-role revocation evidence registry real-Mongo certificate.

TITLE: Authorization Role Revocation Evidence Registry Real-Mongo Certificate
VERSION: v1.1.0-P1-R3C-E1-AUTHORIZATION-ROLE-REVOCATION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Certify physical indexes, caller-owned transactions, immutable replay,
         tenant isolation, corruption rejection, restart durability, and Mongo
         concurrency fencing for authorization-role revocation evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_authorization_role_revocation_evidence_registry_real_mongo.py
COLLABORATION / OWNERSHIP: H2 certifies the unchanged G1 registry and E1 value
                            object against the sanctioned local Mongo replica set.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.1.0-P1-R3C-E1 certifies exact tenant/idempotency historical reads,
           None absence, optional sessions, zero writes, corruption rejection,
           and restart durability; v1.0.0-P1-R3B-H2 established the real-Mongo
           transaction, replay, index, concurrency, and isolation certificate.
COMPLIANCE: NIST privileged-access lifecycle principles; POPIA section 19;
            GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no credentials, PII,
                             production database, or customer database access.
TENANT BOUNDARY: Exact tenant predicates and cross-tenant non-disclosure are
                 physically exercised; no tenant is inferred.
AUTHORITY BOUNDARY: Test-only persistence certification. It grants no authority,
                    mutates no role assignment, membership, business role,
                    session, refresh token, root, break-glass, or activation state.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial
                              execution and settlement.
TRANSACTION BOUNDARY: Every mutation uses a caller-owned genuine Mongo session
                      and transaction; the registry owns neither lifecycle.
FAIL-CLOSED DECLARATION: Unsupported topology, malformed durable evidence,
                         divergent replay, identity collision, and unsafe races fail.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os
from pathlib import Path
from threading import Barrier, Lock
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.monitoring import CommandFailedEvent, CommandListener, CommandStartedEvent, CommandSucceededEvent

from tools.eos.auth.authorization_role_revocation_evidence import (
    AuthorizationRoleRevocationEvidence,
)
from tools.eos.auth.authorization_role_revocation_evidence_registry import (
    COLLECTION,
    REVOCATION_ID_INDEX,
    TARGET_ROLE_TIMELINE_INDEX,
    TENANT_IDEMPOTENCY_INDEX,
    AuthorizationRoleRevocationEvidenceConflictError,
    AuthorizationRoleRevocationEvidenceNotFoundError,
    AuthorizationRoleRevocationEvidencePersistedRecordInvalidError,
    AuthorizationRoleRevocationEvidenceRegistry,
    AuthorizationRoleRevocationEvidenceRegistryError,
    AuthorizationRoleRevocationEvidenceTransactionRequiredError,
)


VERSION = "v1.1.0-P1-R3C-E1-AUTHORIZATION-ROLE-REVOCATION-REGISTRY-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_p1_r3b_h2_"
NOW = datetime(2026, 10, 13, 10, 30, 0, 123000, tzinfo=timezone.utc)
PRODUCTION = Path("tools/eos/auth/authorization_role_revocation_evidence_registry.py")
UNRELATED_COLLECTIONS = (
    "role_assignments",
    "tenant_memberships",
    "tenant_business_roles",
    "auth_sessions",
    "session_registry",
    "refresh_tokens",
    "root_rotations",
    "break_glass_activations",
    "privileged_activations",
    "financial_executions",
)


class PersistenceCommandRecorder(CommandListener):
    """Record real persistence commands without changing Mongo behavior."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._commands: list[str] = []

    def started(self, event: CommandStartedEvent) -> None:
        """Record one command name emitted by the genuine PyMongo client."""
        with self._lock:
            self._commands.append(event.command_name)

    def succeeded(self, event: CommandSucceededEvent) -> None:
        """Accept successful command telemetry without adding state."""

    def failed(self, event: CommandFailedEvent) -> None:
        """Accept failed command telemetry without masking the driver error."""

    def clear(self) -> None:
        """Reset observations before one bounded admission assertion."""
        with self._lock:
            self._commands.clear()

    def persistence_commands(self) -> tuple[str, ...]:
        """Return only read/write commands relevant to registry admission."""
        with self._lock:
            return tuple(name for name in self._commands if name in {"find", "insert", "update", "delete"})


def _client(*, recorder: PersistenceCommandRecorder | None = None) -> MongoClient[Any]:
    """Open and validate one genuine client to the sanctioned writable replica set."""
    listeners: list[CommandListener] = [] if recorder is None else [recorder]
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        retryWrites=True,
        tz_aware=True,
        event_listeners=listeners,
    )
    hello = client.admin.command("hello")
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    assert bool(hello.get("isWritablePrimary", hello.get("ismaster", False)))
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    return client


def _evidence(**changes: object) -> AuthorizationRoleRevocationEvidence:
    """Construct deterministic synthetic evidence without generating authority."""
    values: dict[str, object] = {
        "revocation_id": "revocation-h2-001",
        "tenant_id": "tenant-h2-a",
        "actor_principal_id": "principal-h2-admin",
        "target_principal_id": "principal-h2-target",
        "target_role_id": "AUDITOR",
        "target_assignment_prior_revision": 4,
        "target_assignment_result_revision": 5,
        "operation": "role_revoke",
        "reason_reference": "case:H2-001",
        "authorization_evidence_reference": "authorization-decision:h2-001",
        "authorization_evidence_fingerprint": "a" * 128,
        "idempotency_key": "idempotency-h2-001",
        "revoked_at": NOW,
    }
    values.update(changes)
    return AuthorizationRoleRevocationEvidence(**values)  # type: ignore[arg-type]


def _commit(
    client: MongoClient[Any],
    registry: AuthorizationRoleRevocationEvidenceRegistry,
    evidence: AuthorizationRoleRevocationEvidence,
) -> AuthorizationRoleRevocationEvidence:
    """Commit one registry call while retaining caller ownership of lifecycle."""
    with client.start_session() as session:
        session.start_transaction()
        try:
            result = registry.create_or_replay(evidence, session=session)
            session.commit_transaction()
            return result
        except BaseException:
            if session.in_transaction:
                session.abort_transaction()
            raise


def _retryable(error: BaseException) -> bool:
    """Recognize a driver-labelled retry reason anywhere in a bounded cause chain."""
    current: BaseException | None = error
    while current is not None:
        if isinstance(current, PyMongoError) and current.has_error_label("TransientTransactionError"):
            return True
        current = current.__cause__
    return False


def _compete(
    database_name: str,
    value: AuthorizationRoleRevocationEvidence,
    barrier: Barrier,
) -> str:
    """Run one independently-sessioned contender with bounded whole-transaction retry."""
    client = _client()
    registry = AuthorizationRoleRevocationEvidenceRegistry(client[database_name][COLLECTION])
    first_attempt = True
    try:
        for _attempt in range(5):
            with client.start_session() as session:
                session.start_transaction()
                try:
                    if first_attempt:
                        first_attempt = False
                        barrier.wait(timeout=15)
                    outcome = registry.create_or_replay(value, session=session)
                    session.commit_transaction()
                    return "SUCCESS:" + outcome.revocation_evidence_fingerprint
                except AuthorizationRoleRevocationEvidenceConflictError as error:
                    if session.in_transaction:
                        session.abort_transaction()
                    if error.code == "WHOLE_TRANSACTION_RETRY_REQUIRED" or _retryable(error):
                        continue
                    return "CONFLICT:" + error.code
                except AuthorizationRoleRevocationEvidenceRegistryError as error:
                    if session.in_transaction:
                        session.abort_transaction()
                    if _retryable(error):
                        continue
                    return "FAIL_CLOSED:" + error.code
                except PyMongoError as error:
                    if session.in_transaction:
                        session.abort_transaction()
                    if _retryable(error):
                        continue
                    return "DRIVER_FAIL_CLOSED:" + type(error).__name__
        return "WHOLE_TRANSACTION_RETRY_EXHAUSTED"
    finally:
        client.close()


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, AuthorizationRoleRevocationEvidenceRegistry, PersistenceCommandRecorder]]:
    """Yield one UUID-isolated disposable database and drop only that database."""
    recorder = PersistenceCommandRecorder()
    client = _client(recorder=recorder)
    database_name = DATABASE_PREFIX + uuid.uuid4().hex
    assert database_name.startswith(DATABASE_PREFIX)
    database = client[database_name]
    collection = database[COLLECTION]
    registry = AuthorizationRoleRevocationEvidenceRegistry(collection)
    registry.ensure_indexes()
    try:
        yield client, database, collection, registry, recorder
    finally:
        client.drop_database(database_name)
        client.close()


def test_real_runtime_collection_and_physical_index_metadata(mongo_context: tuple[Any, ...]) -> None:
    """Certify topology, exact collection, idempotent indexes, uniqueness, and no TTL."""
    client, database, collection, registry, _recorder = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert bool(hello.get("isWritablePrimary", hello.get("ismaster", False)))
    assert database.name.startswith(DATABASE_PREFIX)
    assert collection.name == COLLECTION == "authorization_role_revocation_evidence"
    registry.ensure_indexes()
    registry.ensure_indexes()
    indexes = {str(item["name"]): dict(item) for item in collection.list_indexes()}
    assert set(indexes) == {"_id_", REVOCATION_ID_INDEX, TENANT_IDEMPOTENCY_INDEX, TARGET_ROLE_TIMELINE_INDEX}
    assert dict(indexes[REVOCATION_ID_INDEX]["key"]) == {"revocation_id": 1}
    assert indexes[REVOCATION_ID_INDEX].get("unique") is True
    assert dict(indexes[TENANT_IDEMPOTENCY_INDEX]["key"]) == {"tenant_id": 1, "idempotency_key": 1}
    assert indexes[TENANT_IDEMPOTENCY_INDEX].get("unique") is True
    assert dict(indexes[TARGET_ROLE_TIMELINE_INDEX]["key"]) == {
        "tenant_id": 1,
        "target_principal_id": 1,
        "target_role_id": 1,
        "revoked_at": 1,
    }
    assert indexes[TARGET_ROLE_TIMELINE_INDEX].get("unique", False) is False
    assert all("expireAfterSeconds" not in item for item in indexes.values())
    assert all("fingerprint" not in name.casefold() for name in indexes)


def test_missing_and_inactive_transaction_reject_before_persistence(mongo_context: tuple[Any, ...]) -> None:
    """Prove admission rejection emits no real Mongo find or write command."""
    client, _database, _collection, registry, recorder = mongo_context
    value = _evidence()
    recorder.clear()
    with pytest.raises(AuthorizationRoleRevocationEvidenceTransactionRequiredError):
        registry.create_or_replay(value, session=None)
    assert recorder.persistence_commands() == ()
    with client.start_session() as inactive:
        assert inactive.in_transaction is False
        with pytest.raises(AuthorizationRoleRevocationEvidenceTransactionRequiredError):
            registry.create_or_replay(value, session=inactive)
    assert recorder.persistence_commands() == ()


def test_active_transaction_caller_abort_and_commit(mongo_context: tuple[Any, ...]) -> None:
    """Prove pending visibility, caller abort zero-write, and caller commit durability."""
    client, _database, collection, registry, _recorder = mongo_context
    value = _evidence()
    with client.start_session() as session:
        session.start_transaction()
        assert session.in_transaction is True
        assert registry.create_or_replay(value, session=session) == value
        assert collection.count_documents({"revocation_id": value.revocation_id}, session=session) == 1
        assert collection.count_documents({"revocation_id": value.revocation_id}) == 0
        assert session.in_transaction is True
        session.abort_transaction()
    assert collection.count_documents({"revocation_id": value.revocation_id}) == 0
    assert _commit(client, registry, value) == value
    assert collection.count_documents({"revocation_id": value.revocation_id}) == 1


def test_exact_replay_returns_historic_unchanged(mongo_context: tuple[Any, ...]) -> None:
    """Certify exact replay preserves one durable row, identity, and fingerprint."""
    client, _database, collection, registry, _recorder = mongo_context
    value = _evidence()
    assert _commit(client, registry, value) == value
    before = collection.find_one({"revocation_id": value.revocation_id})
    assert _commit(client, registry, value) == value
    assert collection.count_documents({"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key}) == 1
    assert collection.find_one({"revocation_id": value.revocation_id}) == before


def test_divergent_replay_and_revocation_collision_preserve_original(mongo_context: tuple[Any, ...]) -> None:
    """Reject idempotency divergence and global identity collision without hybrid rows."""
    client, _database, collection, registry, _recorder = mongo_context
    original = _evidence()
    _commit(client, registry, original)
    before = collection.find_one({"revocation_id": original.revocation_id})
    with pytest.raises(AuthorizationRoleRevocationEvidenceConflictError) as divergent:
        _commit(client, registry, _evidence(revocation_id="revocation-h2-002", reason_reference="case:H2-DIVERGENT"))
    assert divergent.value.code == "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
    with pytest.raises(AuthorizationRoleRevocationEvidenceConflictError) as collision:
        _commit(client, registry, _evidence(tenant_id="tenant-h2-b", idempotency_key="idempotency-h2-b"))
    assert collision.value.code == "REVOCATION_ID_COLLISION"
    assert collection.find_one({"revocation_id": original.revocation_id}) == before
    assert collection.count_documents({}) == 1


def test_tenant_isolation_and_independent_idempotency(mongo_context: tuple[Any, ...]) -> None:
    """Allow tenant-local key reuse while wrong-tenant reads remain non-disclosing absence."""
    client, _database, collection, registry, _recorder = mongo_context
    tenant_a = _evidence()
    tenant_b = _evidence(tenant_id="tenant-h2-b", revocation_id="revocation-h2-b")
    _commit(client, registry, tenant_a)
    _commit(client, registry, tenant_b)
    assert collection.count_documents({"idempotency_key": tenant_a.idempotency_key}) == 2
    with pytest.raises(AuthorizationRoleRevocationEvidenceNotFoundError):
        registry.get(tenant_id=tenant_a.tenant_id, revocation_id=tenant_b.revocation_id)
    assert registry.get(tenant_id=tenant_b.tenant_id, revocation_id=tenant_b.revocation_id) == tenant_b


def test_tenant_idempotency_read_exact_absence_sessions_and_zero_write(mongo_context: tuple[Any, ...]) -> None:
    """Certify exact historic lookup, None absence, optional sessions, and physical read-only behavior."""
    client, _database, collection, registry, recorder = mongo_context
    value = _evidence()
    _commit(client, registry, value)
    before_document = collection.find_one({"revocation_id": value.revocation_id})
    before_count = collection.count_documents({})
    before_indexes = tuple(collection.list_indexes())
    recorder.clear()
    resolved = registry.get_by_tenant_idempotency(
        tenant_id=value.tenant_id,
        idempotency_key=value.idempotency_key,
    )
    assert resolved == value
    assert resolved is not None
    assert resolved.revocation_id == value.revocation_id
    assert resolved.revoked_at == value.revoked_at
    assert resolved.authorization_evidence_reference == value.authorization_evidence_reference
    assert resolved.authorization_evidence_fingerprint == value.authorization_evidence_fingerprint
    assert resolved.revocation_evidence_fingerprint == value.revocation_evidence_fingerprint
    assert registry.get_by_tenant_idempotency(
        tenant_id="tenant-h2-wrong",
        idempotency_key=value.idempotency_key,
    ) is None
    assert registry.get_by_tenant_idempotency(
        tenant_id=value.tenant_id,
        idempotency_key="idempotency-h2-wrong",
    ) is None
    with client.start_session() as session:
        assert session.in_transaction is False
        assert registry.get_by_tenant_idempotency(
            tenant_id=value.tenant_id,
            idempotency_key=value.idempotency_key,
            session=session,
        ) == value
        assert session.in_transaction is False
        session.start_transaction()
        assert registry.get_by_tenant_idempotency(
            tenant_id=value.tenant_id,
            idempotency_key=value.idempotency_key,
            session=session,
        ) == value
        assert session.in_transaction is True
        session.abort_transaction()
    assert set(recorder.persistence_commands()) == {"find"}
    assert collection.count_documents({}) == before_count == 1
    assert collection.find_one({"revocation_id": value.revocation_id}) == before_document
    assert tuple(collection.list_indexes()) == before_indexes


@pytest.mark.parametrize(
    ("field", "corrupt_value"),
    (("revocation_evidence_fingerprint", "d" * 128), ("target_assignment_result_revision", 77)),
)
def test_tenant_idempotency_read_corruption_fails_closed(
    mongo_context: tuple[Any, ...], field: str, corrupt_value: object
) -> None:
    """Reject fingerprint and structural corruption without healing the durable row."""
    client, _database, collection, registry, _recorder = mongo_context
    value = _evidence()
    _commit(client, registry, value)
    assert collection.update_one(
        {"revocation_id": value.revocation_id}, {"$set": {field: corrupt_value}}
    ).modified_count == 1
    before = collection.find_one({"revocation_id": value.revocation_id})
    with pytest.raises(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError):
        registry.get_by_tenant_idempotency(
            tenant_id=value.tenant_id,
            idempotency_key=value.idempotency_key,
        )
    assert collection.find_one({"revocation_id": value.revocation_id}) == before


def test_tenant_idempotency_read_survives_fresh_client_and_registry(mongo_context: tuple[Any, ...]) -> None:
    """Prove committed replay discovery survives fresh client and registry construction."""
    client, database, _collection, registry, _recorder = mongo_context
    value = _evidence()
    _commit(client, registry, value)
    fresh_client = _client()
    try:
        restarted = AuthorizationRoleRevocationEvidenceRegistry(fresh_client[database.name][COLLECTION])
        assert restarted.get_by_tenant_idempotency(
            tenant_id=value.tenant_id,
            idempotency_key=value.idempotency_key,
        ) == value
    finally:
        fresh_client.close()


@pytest.mark.parametrize(
    ("field", "corrupt_value"),
    (("revocation_evidence_fingerprint", "f" * 128), ("target_assignment_result_revision", 99)),
)
def test_corrupt_historic_rows_fail_closed(
    mongo_context: tuple[Any, ...], field: str, corrupt_value: object
) -> None:
    """Reject fingerprint and structural corruption for both get and replay."""
    client, _database, collection, registry, _recorder = mongo_context
    value = _evidence()
    _commit(client, registry, value)
    assert collection.update_one({"revocation_id": value.revocation_id}, {"$set": {field: corrupt_value}}).modified_count == 1
    with pytest.raises(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError):
        registry.get(tenant_id=value.tenant_id, revocation_id=value.revocation_id)
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError):
            registry.create_or_replay(value, session=session)
        session.abort_transaction()
    assert collection.count_documents({}) == 1


def test_fresh_registry_and_client_durability_replay_and_corruption(mongo_context: tuple[Any, ...]) -> None:
    """Prove committed evidence and fail-closed corruption survive object and client restart."""
    client, database, collection, registry, _recorder = mongo_context
    value = _evidence()
    _commit(client, registry, value)
    fresh_registry = AuthorizationRoleRevocationEvidenceRegistry(collection)
    assert fresh_registry.get(tenant_id=value.tenant_id, revocation_id=value.revocation_id) == value
    fresh_client = _client()
    try:
        restarted = AuthorizationRoleRevocationEvidenceRegistry(fresh_client[database.name][COLLECTION])
        assert restarted.get(tenant_id=value.tenant_id, revocation_id=value.revocation_id) == value
        assert _commit(fresh_client, restarted, value) == value
        assert fresh_client[database.name][COLLECTION].count_documents({}) == 1
        fresh_client[database.name][COLLECTION].update_one(
            {"revocation_id": value.revocation_id},
            {"$set": {"revocation_evidence_fingerprint": "e" * 128}},
        )
        with pytest.raises(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError):
            restarted.get(tenant_id=value.tenant_id, revocation_id=value.revocation_id)
    finally:
        fresh_client.close()


def test_competing_identical_requests_converge_at_one_row(mongo_context: tuple[Any, ...]) -> None:
    """Certify unique-index fencing and governed whole-transaction convergence."""
    _client_owner, database, collection, _registry, _recorder = mongo_context
    value = _evidence()
    barrier = Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = tuple(future.result(timeout=45) for future in (
            pool.submit(_compete, database.name, value, barrier),
            pool.submit(_compete, database.name, value, barrier),
        ))
    assert any(outcome.startswith("SUCCESS:") for outcome in outcomes)
    assert all(outcome.startswith("SUCCESS:") or outcome == "WHOLE_TRANSACTION_RETRY_EXHAUSTED" for outcome in outcomes)
    assert collection.count_documents({"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key}) == 1
    raw = collection.find_one({"revocation_id": value.revocation_id})
    assert raw is not None and raw["revocation_evidence_fingerprint"] == value.revocation_evidence_fingerprint


def test_competing_divergent_requests_cannot_both_succeed(mongo_context: tuple[Any, ...]) -> None:
    """Certify divergent competitors produce one whole durable record and one rejection."""
    _client_owner, database, collection, _registry, _recorder = mongo_context
    left = _evidence(revocation_id="revocation-h2-left", reason_reference="case:H2-LEFT")
    right = _evidence(revocation_id="revocation-h2-right", reason_reference="case:H2-RIGHT")
    barrier = Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = tuple(future.result(timeout=45) for future in (
            pool.submit(_compete, database.name, left, barrier),
            pool.submit(_compete, database.name, right, barrier),
        ))
    assert sum(outcome.startswith("SUCCESS:") for outcome in outcomes) == 1
    assert any(outcome.startswith("CONFLICT:IDEMPOTENCY_KEY_DIVERGENT_REPLAY") for outcome in outcomes)
    assert collection.count_documents({"tenant_id": left.tenant_id, "idempotency_key": left.idempotency_key}) == 1
    durable = collection.find_one({"tenant_id": left.tenant_id, "idempotency_key": left.idempotency_key})
    assert durable is not None
    assert durable["revocation_evidence_fingerprint"] in {
        left.revocation_evidence_fingerprint,
        right.revocation_evidence_fingerprint,
    }


def test_unrelated_authority_collections_remain_absent_and_unmutated(mongo_context: tuple[Any, ...]) -> None:
    """Prove the registry changes only its evidence collection in the disposable database."""
    client, database, _collection, registry, _recorder = mongo_context
    before = {name: database[name].count_documents({}) for name in UNRELATED_COLLECTIONS}
    assert before == {name: 0 for name in UNRELATED_COLLECTIONS}
    _commit(client, registry, _evidence())
    after = {name: database[name].count_documents({}) for name in UNRELATED_COLLECTIONS}
    assert after == before
    assert set(database.list_collection_names()) == {COLLECTION}


def test_source_boundary_has_no_forbidden_authority_or_lifecycle_calls() -> None:
    """Certify source-level isolation from IAM mutation, Legal, finance, and session ownership."""
    source = PRODUCTION.read_text(encoding="utf-8")
    lowered = source.casefold()
    for forbidden_dependency in (
        "role_assignment_repository",
        "tools.eos.legal_operations",
        "tenant_membership",
        "tenant_business_role",
        "refresh_token",
        "financial_execution_repository",
    ):
        assert forbidden_dependency not in lowered
    for forbidden_call in (
        ".start_session(",
        ".start_transaction(",
        ".commit_transaction(",
        ".abort_transaction(",
        ".update_one(",
        ".replace_one(",
        ".delete_one(",
        ".delete_many(",
        ".compare_and_swap(",
    ):
        assert forbidden_call not in lowered
    assert "financial authority boundary: none" in lowered


# ARTIFACT: test_authorization_role_revocation_evidence_registry_real_mongo.py
# VERSION: v1.1.0-P1-R3C-E1-AUTHORIZATION-ROLE-REVOCATION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo evidence-registry certification only; no authorization, role mutation, policy, root, break-glass, activation, Legal Operations, or finance
# TENANT POSTURE: exact tenant isolation and non-disclosing wrong-tenant absence certified
# FAIL-CLOSED POSTURE: topology drift, missing transaction, corruption, divergence, collision, and unsafe concurrency reject
# DATABASE POSTURE: UUID-isolated disposable database only; no production or customer database authority
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
