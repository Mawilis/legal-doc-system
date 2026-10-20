"""
WILSY OS — ENGINEERING MERKLE REAL-MONGO CERTIFICATE
VERSION: 1.0.0-EMP-P13
AUTHORITY: Independent persistence and transaction certification.
EPITOME: Disposable replica-set proof of immutable registry behavior.
ABSOLUTE CANONICAL PATH: tests/integration/test_engineering_merkle_proof_registry_real_mongo.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P13 — Isolated real-Mongo integration.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Protect pre-existing Mongo instances and forbid protected ports.
TENANT BOUNDARY: Explicit institutional scope with isolated test database.
AUTHORITY BOUNDARY: Integration tests only; no institutional anchoring.
FINANCIAL AUTHORITY BOUNDARY: None.
"""

from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tools.eos.kernel.engineering_merkle_proof import (
    build_inclusion_proof,
    merkle_root,
)
from tools.eos.kernel.engineering_merkle_proof_record import (
    EngineeringMerkleProofRecord,
)
from tools.eos.kernel.engineering_merkle_proof_registry import (
    EngineeringMerkleProofRegistry,
    EngineeringMerkleProofConflict,
    EngineeringMerkleProofPersistedInvalid,
    EngineeringMerkleProofTransactionRequired,
    IDENTITY_INDEX,
    RELEASE_INDEX,
)

PROTECTED_PORTS = frozenset((27027, 61391))


def record(
    *,
    institution="wilsy-engineering",
    release="P4C10",
    evidence_id="EVIDENCE-A",
    evidence=b"certified",
):
    entries = [evidence, b"other"]
    return EngineeringMerkleProofRecord.create(
        institution_id=institution,
        release_id=release,
        evidence_id=evidence_id,
        git_head="a" * 40,
        evidence=evidence,
        leaf_index=0,
        leaf_count=2,
        proof=build_inclusion_proof(entries, 0),
        merkle_root=merkle_root(entries),
    )


@pytest.fixture(scope="module")
def isolated_mongo():
    """Launch and own one disposable loopback MongoDB replica set.

    No pre-existing Mongo URI, process, data directory, or protected
    Mongo port is ever used. The fixture only terminates its child PID.
    """
    binary = shutil.which("mongod")
    assert binary is not None, "LOCAL_MONGOD_REQUIRED"

    with tempfile.TemporaryDirectory(prefix="wilsy_emp_p13_") as base:
        directory = Path(base)
        dbpath = directory / "db"
        dbpath.mkdir()
        logfile = directory / "mongod.log"
        replica_set = "wilsyEMP" + uuid.uuid4().hex[:12]
        database_name = "wilsy_emp_" + uuid.uuid4().hex

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
            assert 1024 <= port <= 65535
            assert port not in PROTECTED_PORTS

        uri = (
            f"mongodb://127.0.0.1:{port}/"
            "?directConnection=true"
            "&serverSelectionTimeoutMS=1000"
        )

        command = [
            binary,
            "--bind_ip", "127.0.0.1",
            "--port", str(port),
            "--replSet", replica_set,
            "--dbpath", str(dbpath),
            "--logpath", str(logfile),
            "--nounixsocket",
        ]

        child = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        client = None
        try:
            deadline = time.monotonic() + 35
            while time.monotonic() < deadline:
                if child.poll() is not None:
                    raise RuntimeError("OWN_MONGOD_EXITED_BEFORE_READY")
                candidate = MongoClient(uri)
                try:
                    candidate.admin.command("ping")
                    client = candidate
                    break
                except Exception:
                    candidate.close()
                    time.sleep(0.25)

            assert client is not None, "OWN_MONGOD_STARTUP_TIMEOUT"

            client.admin.command({
                "replSetInitiate": {
                    "_id": replica_set,
                    "members": [
                        {"_id": 0, "host": f"127.0.0.1:{port}"}
                    ],
                }
            })

            deadline = time.monotonic() + 35
            while time.monotonic() < deadline:
                hello = client.admin.command("hello")
                if hello.get("isWritablePrimary") is True:
                    break
                time.sleep(0.25)
            else:
                raise RuntimeError("OWN_REPLICA_SET_NOT_PRIMARY")

            assert child.poll() is None

            # Bootstrap discovery occurred before replica-set initiation.
            # Create a fresh replica-set-aware client after primary election.
            client.close()
            client = None

            uri = (
                f"mongodb://127.0.0.1:{port}/"
                f"?replicaSet={replica_set}"
                "&directConnection=true"
                "&serverSelectionTimeoutMS=5000"
            )

            client = MongoClient(uri)
            hello = client.admin.command("hello")

            if hello.get("setName") != replica_set:
                raise RuntimeError("OWN_REPLICA_SET_IDENTITY_MISMATCH")

            if hello.get("isWritablePrimary") is not True:
                raise RuntimeError("OWN_REPLICA_SET_NOT_PRIMARY")

            if not isinstance(
                hello.get("logicalSessionTimeoutMinutes"), int
            ):
                raise RuntimeError("OWN_REPLICA_SET_HAS_NO_LOGICAL_SESSIONS")

            print(
                f"\nOWN_REPLICA_SET_PORT={port}"
                f"\nOWN_REPLICA_SET_PID={child.pid}"
                f"\nOWN_ISOLATED_DATABASE={database_name}"
                f"\nOWN_REPLICA_SET_IDENTITY=VERIFIED"
                f"\nLOGICAL_SESSIONS=SUPPORTED",
                flush=True,
            )

            database = client[database_name]
            collection = database["engineering_merkle_proofs"]
            registry = EngineeringMerkleProofRegistry(collection)

            yield client, database, collection, registry, uri

        finally:
            if client is not None:
                client.close()

            # Terminate only the process created by this fixture.
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=12)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=12)

            assert child.poll() is not None


def commit_record(client, registry, value):
    with client.start_session() as session:
        with session.start_transaction():
            return registry.create_or_replay(value, session=session)


def test_indexes_are_real_unique_and_nonexpiring(isolated_mongo):
    _, _, collection, registry, _ = isolated_mongo
    registry.ensure_indexes()
    indexes = list(collection.list_indexes())
    named = {index["name"]: index for index in indexes}
    assert IDENTITY_INDEX in named
    assert RELEASE_INDEX in named
    assert named[IDENTITY_INDEX]["unique"] is True
    assert all("expireAfterSeconds" not in index for index in indexes)


def test_absent_transaction_rejected_without_write(isolated_mongo):
    client, _, collection, registry, _ = isolated_mongo
    before = collection.count_documents({})
    with pytest.raises(EngineeringMerkleProofTransactionRequired):
        registry.create_or_replay(record(), session=None)
    with client.start_session() as session:
        with pytest.raises(EngineeringMerkleProofTransactionRequired):
            registry.create_or_replay(record(), session=session)
    assert collection.count_documents({}) == before


def test_abort_writes_nothing_then_commit_is_durable(isolated_mongo):
    client, _, collection, registry, _ = isolated_mongo
    registry.ensure_indexes()
    value = record(evidence_id="TX-ABORT")
    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(value, session=session)
        assert collection.count_documents(
            {"evidence_id": "TX-ABORT"}, session=session
        ) == 1
        session.abort_transaction()
    assert collection.count_documents({"evidence_id": "TX-ABORT"}) == 0
    assert commit_record(client, registry, value) == value
    assert collection.count_documents({"evidence_id": "TX-ABORT"}) == 1


def test_restart_client_readback_and_exact_replay(isolated_mongo):
    client, _, collection, registry, uri = isolated_mongo
    registry.ensure_indexes()
    value = record(evidence_id="READBACK")
    commit_record(client, registry, value)
    assert commit_record(client, registry, value) == value
    assert collection.count_documents({"evidence_id": "READBACK"}) == 1

    with MongoClient(uri) as fresh:
        alternate = EngineeringMerkleProofRegistry(
            fresh[collection.database.name][collection.name]
        )
        assert alternate.get_by_identity(
            institution_id=value.institution_id,
            release_id=value.release_id,
            evidence_id=value.evidence_id,
        ) == value


def test_divergent_replay_fails_without_overwrite(isolated_mongo):
    client, _, collection, registry, _ = isolated_mongo
    registry.ensure_indexes()
    original = record(evidence_id="CONFLICT")
    commit_record(client, registry, original)
    with pytest.raises(EngineeringMerkleProofConflict):
        commit_record(
            client,
            registry,
            record(evidence_id="CONFLICT", evidence=b"altered"),
        )
    assert collection.count_documents({"evidence_id": "CONFLICT"}) == 1
    assert registry.get_by_identity(
        institution_id=original.institution_id,
        release_id=original.release_id,
        evidence_id=original.evidence_id,
    ) == original


def test_institutional_scope_isolation(isolated_mongo):
    client, _, _, registry, _ = isolated_mongo
    left = record(evidence_id="SCOPE")
    right = record(institution="another-institution", evidence_id="SCOPE")
    commit_record(client, registry, left)
    commit_record(client, registry, right)
    assert registry.get_by_identity(
        institution_id=left.institution_id,
        release_id=left.release_id,
        evidence_id=left.evidence_id,
    ) == left
    assert registry.get_by_identity(
        institution_id=right.institution_id,
        release_id=right.release_id,
        evidence_id=right.evidence_id,
    ) == right


def test_storage_unique_index_rejects_direct_collision(isolated_mongo):
    client, _, collection, registry, _ = isolated_mongo
    registry.ensure_indexes()
    value = record(evidence_id="UNIQUE")
    commit_record(client, registry, value)
    forged = value.to_dict()
    forged["provenance_hash"] = "f" * 64
    with pytest.raises(DuplicateKeyError):
        collection.insert_one(forged)


def test_corruption_fails_closed_on_read(isolated_mongo):
    client, _, collection, registry, _ = isolated_mongo
    value = record(evidence_id="CORRUPTION")
    commit_record(client, registry, value)

    # Test-only adversarial mutation, never a production registry API.
    collection.update_one(
        {
            "institution_id": value.institution_id,
            "release_id": value.release_id,
            "evidence_id": value.evidence_id,
        },
        {"$set": {"provenance_hash": "f" * 64}},
    )

    with pytest.raises(EngineeringMerkleProofPersistedInvalid):
        registry.get_by_identity(
            institution_id=value.institution_id,
            release_id=value.release_id,
            evidence_id=value.evidence_id,
        )



def test_competing_divergent_writers_single_durable_winner(isolated_mongo):
    """Two independent transactional writers cannot commit divergent identity."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    client, _, collection, registry, uri = isolated_mongo
    registry.ensure_indexes()

    first = record(evidence_id="P14-RACE", evidence=b"writer-A")
    second = record(evidence_id="P14-RACE", evidence=b"writer-B")
    assert first.provenance_hash != second.provenance_hash

    barrier = Barrier(2, timeout=15)

    def attempt(value):
        with MongoClient(uri, serverSelectionTimeoutMS=5000) as local:
            local_registry = EngineeringMerkleProofRegistry(
                local[collection.database.name][collection.name]
            )
            with local.start_session() as session:
                session.start_transaction()
                try:
                    barrier.wait()
                    local_registry.create_or_replay(value, session=session)
                    session.commit_transaction()
                    return ("committed", value.provenance_hash)
                except Exception as exc:
                    if session.in_transaction:
                        session.abort_transaction()
                    return ("rejected", type(exc).__name__)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, (first, second)))

    committed = [value for state, value in results if state == "committed"]
    rejected = [value for state, value in results if state == "rejected"]

    assert len(committed) == 1, results
    assert len(rejected) == 1, results

    query = {
        "institution_id": "wilsy-engineering",
        "release_id": "P4C10",
        "evidence_id": "P14-RACE",
    }
    assert collection.count_documents(query) == 1

    persisted = registry.get_by_identity(**query)
    assert persisted is not None
    assert persisted.provenance_hash == committed[0]
    assert persisted in (first, second)

    # Neither write path can silently replace the first durable version.
    losing = second if persisted == first else first
    with pytest.raises(EngineeringMerkleProofConflict):
        commit_record(client, registry, losing)

    assert collection.count_documents(query) == 1
    assert registry.get_by_identity(**query) == persisted



def checkpoint_registry_context(isolated_mongo):
    from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
        EngineeringMerkleCheckpointRegistry,
    )
    client, database, _, _, uri = isolated_mongo
    history = database["emp_checkpoint_history_p22"]
    current = database["emp_checkpoint_current_p22"]
    registry = EngineeringMerkleCheckpointRegistry(history, current)
    registry.ensure_indexes()
    return client, database, history, current, registry, uri


def checkpoint_p22(events, previous=None, log_id="p22-release-evidence"):
    from tools.eos.kernel.engineering_merkle_checkpoint import (
        EngineeringMerkleCheckpoint,
    )
    return EngineeringMerkleCheckpoint.create(
        institution_id="wilsy-engineering",
        log_id=log_id,
        events=events,
        previous_checkpoint=previous,
    )


def transaction_p22(client, callback):
    with client.start_session() as session:
        with session.start_transaction():
            return callback(session)


def test_checkpoint_genesis_abort_and_commit(isolated_mongo):
    from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
        EngineeringMerkleCheckpointRegistry,
    )

    client, _, history, current, registry, uri = (
        checkpoint_registry_context(isolated_mongo)
    )
    first = checkpoint_p22([b"A"], log_id="p22-genesis")

    with client.start_session() as session:
        session.start_transaction()
        assert registry.create_genesis(first, session=session) == first
        assert history.count_documents(
            {"log_id": first.log_id}, session=session
        ) == 1
        assert current.count_documents(
            {"log_id": first.log_id}, session=session
        ) == 1
        session.abort_transaction()

    assert history.count_documents({"log_id": first.log_id}) == 0
    assert current.count_documents({"log_id": first.log_id}) == 0

    assert transaction_p22(
        client, lambda session: registry.create_genesis(first, session=session)
    ) == first

    with MongoClient(uri) as fresh:
        reopened = EngineeringMerkleCheckpointRegistry(
            fresh[history.database.name][history.name],
            fresh[current.database.name][current.name],
        )
        assert reopened.get_current(
            institution_id=first.institution_id,
            log_id=first.log_id,
        ) == first
        assert reopened.get_history(
            institution_id=first.institution_id,
            log_id=first.log_id,
        ) == (first,)


def test_checkpoint_advance_abort_and_commit(isolated_mongo):
    client, _, history, current, registry, _ = (
        checkpoint_registry_context(isolated_mongo)
    )
    first = checkpoint_p22([b"A"], log_id="p22-advance")
    second = checkpoint_p22(
        [b"A", b"B"], previous=first, log_id=first.log_id
    )

    transaction_p22(
        client, lambda session: registry.create_genesis(first, session=session)
    )
    with client.start_session() as session:
        session.start_transaction()
        assert registry.advance(
            second,
            expected_checkpoint_hash=first.checkpoint_hash,
            session=session,
        ) == second
        assert history.count_documents(
            {"log_id": first.log_id}, session=session
        ) == 2
        session.abort_transaction()

    assert history.count_documents({"log_id": first.log_id}) == 1
    assert registry.get_current(
        institution_id=first.institution_id,
        log_id=first.log_id,
    ) == first

    transaction_p22(
        client,
        lambda session: registry.advance(
            second,
            expected_checkpoint_hash=first.checkpoint_hash,
            session=session,
        ),
    )

    assert registry.get_history(
        institution_id=first.institution_id,
        log_id=first.log_id,
    ) == (first, second)
    assert current.count_documents({"log_id": first.log_id}) == 1


def test_checkpoint_stale_head_rejected(isolated_mongo):
    from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
        EngineeringMerkleCheckpointConflict,
    )

    client, _, history, _, registry, _ = (
        checkpoint_registry_context(isolated_mongo)
    )
    first = checkpoint_p22([b"A"], log_id="p22-stale")
    second = checkpoint_p22(
        [b"A", b"B"], previous=first, log_id=first.log_id
    )
    third = checkpoint_p22(
        [b"A", b"B", b"C"], previous=second, log_id=first.log_id
    )

    transaction_p22(
        client, lambda session: registry.create_genesis(first, session=session)
    )
    transaction_p22(
        client,
        lambda session: registry.advance(
            second,
            expected_checkpoint_hash=first.checkpoint_hash,
            session=session,
        ),
    )

    with pytest.raises(EngineeringMerkleCheckpointConflict):
        transaction_p22(
            client,
            lambda session: registry.advance(
                third,
                expected_checkpoint_hash=first.checkpoint_hash,
                session=session,
            ),
        )

    assert history.count_documents({"log_id": first.log_id}) == 2
    assert registry.get_current(
        institution_id=first.institution_id,
        log_id=first.log_id,
    ) == second


def test_checkpoint_competing_successors_single_winner(isolated_mongo):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
        EngineeringMerkleCheckpointRegistry,
    )

    client, _, history, current, registry, uri = (
        checkpoint_registry_context(isolated_mongo)
    )
    first = checkpoint_p22([b"A"], log_id="p22-race")
    left = checkpoint_p22(
        [b"A", b"LEFT"], previous=first, log_id=first.log_id
    )
    right = checkpoint_p22(
        [b"A", b"RIGHT"], previous=first, log_id=first.log_id
    )

    transaction_p22(
        client, lambda session: registry.create_genesis(first, session=session)
    )

    barrier = Barrier(2, timeout=15)

    def attempt(candidate):
        with MongoClient(uri, serverSelectionTimeoutMS=5000) as local:
            local_registry = EngineeringMerkleCheckpointRegistry(
                local[history.database.name][history.name],
                local[current.database.name][current.name],
            )
            with local.start_session() as session:
                session.start_transaction()
                try:
                    barrier.wait()
                    local_registry.advance(
                        candidate,
                        expected_checkpoint_hash=first.checkpoint_hash,
                        session=session,
                    )
                    session.commit_transaction()
                    return ("committed", candidate.checkpoint_hash)
                except Exception as exc:
                    if session.in_transaction:
                        session.abort_transaction()
                    return ("rejected", type(exc).__name__)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, (left, right)))

    committed = [value for state, value in results if state == "committed"]
    rejected = [value for state, value in results if state == "rejected"]

    assert len(committed) == 1, results
    assert len(rejected) == 1, results
    assert history.count_documents({"log_id": first.log_id}) == 2
    assert current.count_documents({"log_id": first.log_id}) == 1

    winner = registry.get_current(
        institution_id=first.institution_id,
        log_id=first.log_id,
    )
    assert winner is not None
    assert winner.checkpoint_hash == committed[0]
    assert winner in (left, right)
    assert registry.get_history(
        institution_id=first.institution_id,
        log_id=first.log_id,
    ) == (first, winner)



def test_p23_pointer_corruption_rejected(isolated_mongo):
    from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
        EngineeringMerkleCheckpointPersistedInvalid,
    )
    client, _, _, current, registry, _ = checkpoint_registry_context(
        isolated_mongo
    )
    first = checkpoint_p22([b"A"], log_id="p23-pointer")
    transaction_p22(
        client, lambda session: registry.create_genesis(first, session=session)
    )
    current.update_one(
        {"institution_id": first.institution_id, "log_id": first.log_id},
        {"$set": {"checkpoint_hash": "f" * 64}},
    )
    with pytest.raises(EngineeringMerkleCheckpointPersistedInvalid):
        registry.get_current(
            institution_id=first.institution_id, log_id=first.log_id
        )


def test_p23_missing_history_rejected(isolated_mongo):
    from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
        EngineeringMerkleCheckpointPersistedInvalid,
    )
    client, _, history, _, registry, _ = checkpoint_registry_context(
        isolated_mongo
    )
    first = checkpoint_p22([b"A"], log_id="p23-missing")
    transaction_p22(
        client, lambda session: registry.create_genesis(first, session=session)
    )
    history.delete_one(
        {"institution_id": first.institution_id, "log_id": first.log_id}
    )
    with pytest.raises(EngineeringMerkleCheckpointPersistedInvalid):
        registry.get_current(
            institution_id=first.institution_id, log_id=first.log_id
        )


def test_p23_orphan_history_rejected(isolated_mongo):
    from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
        EngineeringMerkleCheckpointPersistedInvalid,
    )
    client, _, _, current, registry, _ = checkpoint_registry_context(
        isolated_mongo
    )
    first = checkpoint_p22([b"A"], log_id="p23-orphan")
    transaction_p22(
        client, lambda session: registry.create_genesis(first, session=session)
    )
    current.delete_one(
        {"institution_id": first.institution_id, "log_id": first.log_id}
    )
    with pytest.raises(EngineeringMerkleCheckpointPersistedInvalid):
        registry.get_current(
            institution_id=first.institution_id, log_id=first.log_id
        )


def test_p23_broken_history_link_rejected(isolated_mongo):
    from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
        EngineeringMerkleCheckpointPersistedInvalid,
    )
    client, _, history, _, registry, _ = checkpoint_registry_context(
        isolated_mongo
    )
    first = checkpoint_p22([b"A"], log_id="p23-link")
    second = checkpoint_p22(
        [b"A", b"B"], previous=first, log_id=first.log_id
    )
    transaction_p22(
        client, lambda session: registry.create_genesis(first, session=session)
    )
    transaction_p22(
        client,
        lambda session: registry.advance(
            second,
            expected_checkpoint_hash=first.checkpoint_hash,
            session=session,
        ),
    )
    history.update_one(
        {"checkpoint_hash": second.checkpoint_hash},
        {"$set": {"previous_checkpoint_hash": "f" * 64}},
    )
    with pytest.raises(EngineeringMerkleCheckpointPersistedInvalid):
        registry.get_current(
            institution_id=first.institution_id, log_id=first.log_id
        )


def test_p23_failed_cas_aborts_partial_history_write(isolated_mongo):
    from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
        EngineeringMerkleCheckpointRegistry,
        EngineeringMerkleCheckpointConflict,
    )

    client, _, history, current, registry, _ = (
        checkpoint_registry_context(isolated_mongo)
    )
    first = checkpoint_p22([b"A"], log_id="p23-cas-abort")
    second = checkpoint_p22(
        [b"A", b"B"], previous=first, log_id=first.log_id
    )
    transaction_p22(
        client, lambda session: registry.create_genesis(first, session=session)
    )

    class NoMatch:
        matched_count = 0

    class FailedCAS:
        def __init__(self, actual):
            self.actual = actual

        def update_one(self, *args, **kwargs):
            # A test-only injected CAS mismatch, after real history insert.
            return NoMatch()

        def __getattr__(self, name):
            return getattr(self.actual, name)

    faulted = EngineeringMerkleCheckpointRegistry(
        history, FailedCAS(current)
    )

    with pytest.raises(EngineeringMerkleCheckpointConflict):
        transaction_p22(
            client,
            lambda session: faulted.advance(
                second,
                expected_checkpoint_hash=first.checkpoint_hash,
                session=session,
            ),
        )

    # Context-managed transaction abort must remove inserted history.
    assert history.count_documents({"log_id": first.log_id}) == 1
    assert current.count_documents({"log_id": first.log_id}) == 1
    assert registry.get_history(
        institution_id=first.institution_id, log_id=first.log_id
    ) == (first,)
    assert registry.get_current(
        institution_id=first.institution_id, log_id=first.log_id
    ) == first


# ARTIFACT: ENGINEERING MERKLE REAL-MONGO CERTIFICATE
# VERSION: 1.0.0-EMP-P13
# AUTHORITY BOUNDARY: TEST-OWNED DISPOSABLE DATABASE ONLY
# TENANT POSTURE: UUID-ISOLATED DATABASE AND EXPLICIT SCOPE
# FAIL-CLOSED POSTURE: TRANSACTION, COLLISION, CORRUPTION REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
