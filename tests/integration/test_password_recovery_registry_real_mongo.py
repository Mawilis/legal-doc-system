"""Real-Mongo integration certificate for the R10B2 recovery registry.

TITLE: WILSY OS Password Recovery Registry Real-Mongo Certificate
VERSION: v1.0.0-R10B4-PASSWORD-RECOVERY-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the existing password-recovery capability registry against
         an isolated disposable MongoDB replica set without starting the
         password-recovery service or changing production behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_password_recovery_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Tests only; the production R10B1 domain and R10B2
                           registry are read-only dependencies of this file.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10B4-PASSWORD-RECOVERY-REGISTRY-REAL-MONGO-CERT proves
           disposable real-Mongo indexes, uniqueness, durability, hydration,
           tenant scope, lifecycle CAS, competing consumers, and session use.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Loopback-only synthetic identities and SHA3-512
                            digests are used; no raw recovery token, password,
                            JWT, refresh token, MFA secret, or credential is
                            persisted or printed.
TENANT BOUNDARY: Every read and lifecycle operation retains exact synthetic
                 tenant scope; no canonical tenant data is used.
AUTHORITY BOUNDARY: Recovery-capability persistence and lifecycle evidence
                    only; no password, authentication, delivery, session,
                    role, membership, legal, or commercial authority.
TRANSACTION / SESSION BOUNDARY: The caller supplies and owns ClientSession;
                                the registry never creates, commits, aborts,
                                or retries transactions.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
EVIDENCE LIMITATION: This certificate does not prove the future recovery
                     service, HTTP routes, delivery, rate limiting, password
                     mutation, or Mongo server restart durability.
"""
from __future__ import annotations

import os
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.auth.password_recovery import (
    PasswordRecoveryCapability,
    PasswordRecoveryCapabilityStatus,
)
from tools.eos.saas.auth.password_recovery_registry import (
    COLLECTION,
    INDEX_DEFINITIONS,
    PasswordRecoveryCapabilityAlreadyExistsError,
    PasswordRecoveryCapabilityLifecycleConflictError,
    PasswordRecoveryCapabilityPersistedRecordInvalidError,
    PasswordRecoveryCapabilityPersistenceError,
    PasswordRecoveryCapabilityRegistry,
)


URI_ENV = "R10B4_PASSWORD_RECOVERY_MONGO_URI"
CERTIFICATION_DATABASE_PREFIX = "wilsy_r10b4_prc_"
REPLICA_SET = "wilsyR10B4RS"
BASE_TIME = datetime(2026, 9, 22, 12, 0, 0, 123456, tzinfo=timezone.utc)
EXPIRY_TIME = BASE_TIME + timedelta(hours=1)


class MongoCertificateContext:
    """Own only the run-scoped client, database, collection, and registry."""

    def __init__(self, client: MongoClient[Any], database_name: str) -> None:
        self.client = client
        self.database_name = database_name
        self.database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        self.collection = self.database[COLLECTION]
        self.registry = PasswordRecoveryCapabilityRegistry(self.collection)


def _uri() -> str:
    """Require an explicitly supplied, loopback-only disposable URI."""

    value = os.environ.get(URI_ENV, "").strip()
    if not value or "mongodb.net" in value.lower() or "atlas" in value.lower():
        raise RuntimeError(f"{URI_ENV} must name an explicit disposable local MongoDB")
    if "127.0.0.1" not in value and "localhost" not in value:
        raise RuntimeError(f"{URI_ENV} must be loopback-only")
    return value


def _epoch_microseconds(value: datetime) -> int:
    """Mirror the registry's deterministic metadata calculation for fixtures."""

    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (value.astimezone(timezone.utc) - epoch) // timedelta(microseconds=1)


def _capability(
    capability_id: str,
    seed: str,
    *,
    tenant_id: str = "tenant-r10b4-a",
    principal_id: str = "principal-r10b4",
) -> PasswordRecoveryCapability:
    """Build deterministic synthetic digest-only state."""

    import hashlib

    return PasswordRecoveryCapability.issue(
        capability_id=capability_id,
        tenant_id=tenant_id,
        principal_id=principal_id,
        token_digest=hashlib.sha3_512(seed.encode("utf-8")).hexdigest(),
        issued_at=BASE_TIME,
        expires_at=EXPIRY_TIME,
    )


def _document(capability: PasswordRecoveryCapability, **overrides: Any) -> dict[str, Any]:
    """Create a direct disposable-database fixture from production serialization."""

    payload = capability.to_document()
    payload["_issued_at_epoch_us"] = _epoch_microseconds(capability.issued_at)
    payload["_expires_at_epoch_us"] = _epoch_microseconds(capability.expires_at)
    payload.update(overrides)
    return payload


def _fresh_database() -> MongoCertificateContext:
    """Connect only to the explicit loopback disposable certification runtime."""

    uri = _uri()
    client: MongoClient[Any] = MongoClient(
        uri,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=3000,
        retryWrites=True,
    )
    try:
        hello = client.admin.command("hello")
        address = client.address
        if address is None or address[0] not in {"127.0.0.1", "localhost"}:
            raise RuntimeError("R10B4 Mongo runtime is not loopback")
        if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary", False):
            raise RuntimeError("R10B4 requires a writable disposable replica set")
        name = CERTIFICATION_DATABASE_PREFIX + uuid.uuid4().hex
        if name == "wilsy" or len(name) > 63:
            raise RuntimeError("R10B4 database identity guard failed")
        context = MongoCertificateContext(client, name)
        context.registry.ensure_indexes()
        return context
    except BaseException:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_context() -> Any:
    """Provide one isolated database and drop only that database afterward."""

    context = _fresh_database()
    try:
        yield context
    finally:
        context.client.drop_database(context.database_name)
        assert context.database_name not in context.client.list_database_names()
        context.client.close()


def test_real_indexes_and_index_ensure_idempotency(mongo_context: MongoCertificateContext) -> None:
    """Read Mongo's actual index metadata and prove repeated ensure is stable."""

    mongo_context.registry.ensure_indexes()
    indexes = list(mongo_context.collection.list_indexes())
    by_name = {item["name"]: item for item in indexes}
    expected = {name: (keys, unique) for keys, unique, name in INDEX_DEFINITIONS}
    assert set(by_name) == {"_id_", *expected}
    for name, (keys, unique) in expected.items():
        assert list(by_name[name]["key"].items()) == list(keys)
        assert by_name[name].get("unique", False) is unique
        assert "expireAfterSeconds" not in by_name[name]
    assert mongo_context.database.list_collection_names() == [COLLECTION]


def test_real_unique_indexes_and_insert_only_durability(mongo_context: MongoCertificateContext) -> None:
    """Trigger both Mongo unique indexes and verify one exact durable row."""

    first = _capability("r10b4-duplicate-id", "r10b4-duplicate-id")
    mongo_context.registry.create(first)
    with pytest.raises(PasswordRecoveryCapabilityAlreadyExistsError) as identity_error:
        mongo_context.registry.create(_capability(first.capability_id, "r10b4-other-seed"))
    assert identity_error.value.code == "RECOVERY_CAPABILITY_ID_DUPLICATE"

    with pytest.raises(PasswordRecoveryCapabilityAlreadyExistsError) as digest_error:
        mongo_context.registry.create(
            _capability("r10b4-duplicate-digest", "r10b4-duplicate-id")
        )
    assert digest_error.value.code == "RECOVERY_TOKEN_DIGEST_DUPLICATE"

    persisted = mongo_context.collection.find_one({"capability_id": first.capability_id})
    assert persisted is not None
    assert persisted["tenant_id"] == first.tenant_id
    assert persisted["principal_id"] == first.principal_id
    assert persisted["token_digest"] == first.token_digest
    assert persisted["status"] == PasswordRecoveryCapabilityStatus.ACTIVE.value
    assert all(secret not in persisted for secret in ("raw_token", "token", "password", "passwordHash"))
    assert mongo_context.collection.count_documents({"capability_id": first.capability_id}) == 1


def test_real_hydration_restart_and_tenant_scoped_reads(mongo_context: MongoCertificateContext) -> None:
    """Reinstantiate the registry and prove exact tenant-bound round trips."""

    capability = _capability("r10b4-round-trip", "r10b4-round-trip")
    mongo_context.registry.create(capability)
    restarted = PasswordRecoveryCapabilityRegistry(mongo_context.collection)
    assert restarted.get_by_capability_id(
        tenant_id=capability.tenant_id,
        capability_id=capability.capability_id,
    ) == capability
    assert restarted.get_by_token_digest(
        tenant_id=capability.tenant_id,
        token_digest=capability.token_digest,
    ) == capability
    assert restarted.get_by_capability_id(
        tenant_id="tenant-r10b4-b", capability_id=capability.capability_id
    ) is None
    assert restarted.get_by_token_digest(
        tenant_id="tenant-r10b4-b", token_digest=capability.token_digest
    ) is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"token_digest": "malformed"},
        {"status": "UNSUPPORTED"},
        {"status": "ACTIVE", "consumed_at": (BASE_TIME + timedelta(minutes=1)).isoformat()},
        {"_expires_at_epoch_us": _epoch_microseconds(EXPIRY_TIME) + 1},
    ],
)
def test_real_corruption_rejected_fail_closed(
    mongo_context: MongoCertificateContext,
    overrides: dict[str, Any],
) -> None:
    """Hydration rejects representative durable corruption without repair."""

    capability = _capability(
        f"r10b4-corrupt-{uuid.uuid4().hex}", f"r10b4-corrupt-{uuid.uuid4().hex}"
    )
    mongo_context.collection.insert_one(_document(capability, **overrides))
    with pytest.raises(PasswordRecoveryCapabilityPersistedRecordInvalidError) as error:
        mongo_context.registry.get_by_capability_id(
            tenant_id=capability.tenant_id, capability_id=capability.capability_id
        )
    assert error.value.code == "RECOVERY_PERSISTED_RECORD_INVALID"


def test_real_consume_cas_and_replay(mongo_context: MongoCertificateContext) -> None:
    """Prove one durable consume transition, preserved evidence, and replay failure."""

    capability = _capability("r10b4-consume", "r10b4-consume")
    consumed_at = BASE_TIME + timedelta(minutes=5)
    mongo_context.registry.create(capability)
    result = mongo_context.registry.consume(capability, consumed_at)
    assert result.status is PasswordRecoveryCapabilityStatus.CONSUMED
    persisted = mongo_context.collection.find_one({"capability_id": capability.capability_id})
    assert persisted and persisted["status"] == "CONSUMED"
    assert persisted["consumed_at"] == consumed_at.isoformat()
    assert mongo_context.collection.count_documents({"capability_id": capability.capability_id}) == 1
    with pytest.raises(PasswordRecoveryCapabilityLifecycleConflictError):
        mongo_context.registry.consume(capability, consumed_at + timedelta(minutes=1))
    replay_state = mongo_context.collection.find_one({"capability_id": capability.capability_id})
    assert replay_state and replay_state["status"] == "CONSUMED"


def test_real_revoke_cas_and_replay(mongo_context: MongoCertificateContext) -> None:
    """Prove one durable revoke transition and fail-closed replay."""

    capability = _capability("r10b4-revoke", "r10b4-revoke")
    revoked_at = BASE_TIME + timedelta(minutes=6)
    mongo_context.registry.create(capability)
    result = mongo_context.registry.revoke(capability, revoked_at)
    assert result.status is PasswordRecoveryCapabilityStatus.REVOKED
    persisted = mongo_context.collection.find_one({"capability_id": capability.capability_id})
    assert persisted and persisted["status"] == "REVOKED"
    assert persisted["revoked_at"] == revoked_at.isoformat()
    with pytest.raises(PasswordRecoveryCapabilityLifecycleConflictError):
        mongo_context.registry.revoke(capability, revoked_at + timedelta(minutes=1))
    replay_state = mongo_context.collection.find_one({"capability_id": capability.capability_id})
    assert replay_state and replay_state["status"] == "REVOKED"


def test_real_expire_boundary_and_replay(mongo_context: MongoCertificateContext) -> None:
    """Prove premature expiry fails, boundary expiry persists, and replay fails."""

    premature = _capability("r10b4-premature-expire", "r10b4-premature-expire")
    mongo_context.registry.create(premature)
    with pytest.raises(PasswordRecoveryCapabilityLifecycleConflictError) as premature_error:
        mongo_context.registry.expire(premature, EXPIRY_TIME - timedelta(microseconds=1))
    assert premature_error.value.code == "EXPIRY_BOUNDARY_NOT_REACHED"
    premature_state = mongo_context.collection.find_one({"capability_id": premature.capability_id})
    assert premature_state and premature_state["status"] == "ACTIVE"

    capability = _capability("r10b4-expire", "r10b4-expire")
    mongo_context.registry.create(capability)
    result = mongo_context.registry.expire(capability, EXPIRY_TIME)
    assert result.status is PasswordRecoveryCapabilityStatus.EXPIRED
    persisted = mongo_context.collection.find_one({"capability_id": capability.capability_id})
    assert persisted and persisted["status"] == "EXPIRED"
    assert persisted["expired_at"] == EXPIRY_TIME.isoformat()
    with pytest.raises(PasswordRecoveryCapabilityLifecycleConflictError):
        mongo_context.registry.expire(capability, EXPIRY_TIME + timedelta(minutes=1))
    assert mongo_context.collection.count_documents({"capability_id": capability.capability_id}) == 1


def test_real_competing_consumers_have_one_winner(mongo_context: MongoCertificateContext) -> None:
    """Use a barrier to prove Mongo CAS admits exactly one competing consumer."""

    capability = _capability("r10b4-competing-consume", "r10b4-competing-consume")
    mongo_context.registry.create(capability)
    barrier = threading.Barrier(2)
    outcomes: list[tuple[str, Any]] = []
    lock = threading.Lock()

    def consume() -> None:
        barrier.wait()
        try:
            value = PasswordRecoveryCapabilityRegistry(mongo_context.collection).consume(
                capability, BASE_TIME + timedelta(minutes=10)
            )
            outcome = ("success", value)
        except PasswordRecoveryCapabilityLifecycleConflictError as error:
            outcome = ("failure", error)
        with lock:
            outcomes.append(outcome)

    workers = [threading.Thread(target=consume) for _ in range(2)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=10)
    assert all(not worker.is_alive() for worker in workers)
    assert [kind for kind, _ in outcomes].count("success") == 1
    assert [kind for kind, _ in outcomes].count("failure") == 1
    persisted = mongo_context.collection.find_one({"capability_id": capability.capability_id})
    assert persisted and persisted["status"] == "CONSUMED"
    assert mongo_context.collection.count_documents({"capability_id": capability.capability_id}) == 1


def test_real_caller_session_and_transaction_ownership(mongo_context: MongoCertificateContext) -> None:
    """Prove caller-session forwarding, abort invisibility, and committed visibility."""

    aborted = _capability("r10b4-aborted-session", "r10b4-aborted-session")
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        mongo_context.registry.create(aborted, session=session)
        assert mongo_context.registry.get_by_capability_id(
            tenant_id=aborted.tenant_id, capability_id=aborted.capability_id, session=session
        ) == aborted
        assert mongo_context.registry.get_by_capability_id(
            tenant_id=aborted.tenant_id, capability_id=aborted.capability_id
        ) is None
        session.abort_transaction()
    assert mongo_context.collection.find_one({"capability_id": aborted.capability_id}) is None

    committed = _capability("r10b4-committed-session", "r10b4-committed-session")
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        mongo_context.registry.create(committed, session=session)
        session.commit_transaction()
    assert mongo_context.registry.get_by_capability_id(
        tenant_id=committed.tenant_id, capability_id=committed.capability_id
    ) == committed


def test_real_persistence_failure_is_not_absence_or_success(mongo_context: MongoCertificateContext) -> None:
    """A closed client is surfaced as bounded persistence failure."""

    dead_client: MongoClient[Any] = MongoClient(_uri(), serverSelectionTimeoutMS=3000)
    dead_collection = dead_client[mongo_context.database_name][COLLECTION]
    dead_client.close()
    with pytest.raises(PasswordRecoveryCapabilityPersistenceError) as error:
        PasswordRecoveryCapabilityRegistry(dead_collection).get_by_capability_id(
            tenant_id="tenant-r10b4-a", capability_id="closed-client"
        )
    assert error.value.code == "RECOVERY_READ_FAILED"


def test_real_database_boundary_contains_only_recovery_collection(mongo_context: MongoCertificateContext) -> None:
    """The disposable database contains no user, session, MFA, or financial data."""

    assert mongo_context.database.name != "wilsy"
    assert mongo_context.database.list_collection_names() == [COLLECTION]
    assert not mongo_context.database.list_collection_names(filter={"name": {"$in": ["users", "sessions", "refresh_tokens", "otp_secrets"]}})


# ARTIFACT: test_password_recovery_registry_real_mongo.py
# VERSION: v1.0.0-R10B4-PASSWORD-RECOVERY-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo recovery-capability evidence only
# TENANT POSTURE: UUID-isolated loopback database; no canonical wilsy writes
# FAIL-CLOSED POSTURE: actual duplicate, corruption, lifecycle, CAS, and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
