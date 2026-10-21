"""P47-R95-G51: disposable replica-set clearance registry certificate.

Never connects to ambient MongoDB or protected ports. Creates and destroys
only its own UUID-isolated localhost replica set and temporary database.
Documentary evidence only; no operational clearance or matter authorization.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
import socket
import subprocess
import time
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_clearance import (
    PractitionerConfidentialityClearanceEvent as Event,
)
from tools.eos.legal_operations.registry import (
    legal_work_practitioner_confidentiality_clearance_registry as reg,
)

MONGOD = "/opt/homebrew/bin/mongod"
PROTECTED = {27017, 27027, 61391}
NOW = datetime(2026, 10, 21, 9, tzinfo=timezone.utc)


def make(**changes):
    """Construct typed canonical evidence, then apply validated overrides."""
    from dataclasses import replace

    canonical = Event(
        tenant_id="tenant-g51",
        case_matter_id="matter-" + uuid.uuid4().hex,
        practitioner_principal_id="practitioner-g51",
        clearance_event_id="event-" + uuid.uuid4().hex,
        predecessor_event_id=None,
        decision="CLEARED",
        effective_at=NOW,
        expires_at=NOW + timedelta(days=30),
        issuer_principal_id="partner-g51",
        issuer_authorization_evidence_reference="iam-g51",
        conflict_provenance_fingerprint="a" * 128,
        confidentiality_decision_reference="review-g51",
    )
    return replace(canonical, **changes)


@contextmanager
def tx(client):
    with client.start_session() as session:
        with session.start_transaction():
            yield session


def history(collection, session, item):
    return reg.list_history(
        tenant_id=item.tenant_id,
        case_matter_id=item.case_matter_id,
        practitioner_principal_id=item.practitioner_principal_id,
        collection=collection,
        session=session,
    )


@pytest.fixture(scope="module")
def isolated():
    assert Path(MONGOD).is_file()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    assert port not in PROTECTED
    replica = "wilsyG51_" + uuid.uuid4().hex[:12]
    dbname = "wilsy_g51_cert_" + uuid.uuid4().hex

    with TemporaryDirectory(prefix="wilsy-g51-isolated-") as temp:
        folder = Path(temp)
        data = folder / "data"
        data.mkdir()
        process = None
        bootstrap = None
        client = None
        try:
            process = subprocess.Popen(
                [MONGOD, "--dbpath", str(data),
                 "--port", str(port), "--bind_ip", "127.0.0.1",
                 "--replSet", replica, "--nounixsocket",
                 "--logpath", str(folder / "mongod.log"), "--quiet"],
                cwd=folder, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            bootstrap = MongoClient(
                f"mongodb://127.0.0.1:{port}/?directConnection=true",
                serverSelectionTimeoutMS=1000, connectTimeoutMS=1000,
                retryWrites=False, tz_aware=True, tzinfo=timezone.utc,
            )
            deadline = time.monotonic() + 25
            while True:
                assert process.poll() is None, "ISOLATED_MONGOD_EXITED"
                try:
                    bootstrap.admin.command("ping")
                    break
                except PyMongoError:
                    assert time.monotonic() < deadline, "STARTUP_TIMEOUT"
                    time.sleep(0.25)

            bootstrap.admin.command({
                "replSetInitiate": {
                    "_id": replica,
                    "members": [{"_id": 0, "host": f"127.0.0.1:{port}"}],
                }
            })
            client = MongoClient(
                f"mongodb://127.0.0.1:{port}/?replicaSet={replica}",
                serverSelectionTimeoutMS=2000, connectTimeoutMS=2000,
                retryWrites=False, tz_aware=True, tzinfo=timezone.utc,
            )
            deadline = time.monotonic() + 30
            while True:
                try:
                    hello = client.admin.command("hello")
                    if (
                        hello.get("setName") == replica
                        and hello.get("isWritablePrimary") is True
                        and hello.get("logicalSessionTimeoutMinutes") is not None
                    ):
                        break
                except PyMongoError:
                    pass
                assert time.monotonic() < deadline, "PRIMARY_TIMEOUT"
                time.sleep(0.3)

            collection = client[dbname].get_collection(
                reg.COLLECTION,
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            )
            yield client, collection
        finally:
            if client is not None:
                client.close()
            if bootstrap is not None:
                bootstrap.close()
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
            assert process is None or process.poll() is not None, (
                "ISOLATED_MONGO_PROCESS_CLEANUP_FAILED"
            )


def test_01_indexes_and_no_ttl(isolated):
    _, collection = isolated
    reg.ensure_indexes(collection)
    indexes = list(collection.list_indexes())
    by_name = {index["name"]: index for index in indexes}
    assert {reg.IDENTITY_INDEX, reg.ROOT_INDEX, reg.SUCCESSOR_INDEX,
            reg.FINGERPRINT_INDEX, reg.SCOPE_INDEX}.issubset(by_name)
    assert all("expireAfterSeconds" not in index for index in indexes)
    assert sum(bool(by_name[name].get("unique")) for name in (
        reg.IDENTITY_INDEX, reg.ROOT_INDEX, reg.SUCCESSOR_INDEX,
        reg.FINGERPRINT_INDEX,
    )) == 4


def test_02_active_transaction_required(isolated):
    _, collection = isolated
    candidate = make()
    with pytest.raises(reg.ClearanceTransactionRequired):
        reg.append(event=candidate, collection=collection, session=None)
    with pytest.raises(reg.ClearanceTransactionRequired):
        reg.list_history(
            tenant_id=candidate.tenant_id,
            case_matter_id=candidate.case_matter_id,
            practitioner_principal_id=candidate.practitioner_principal_id,
            collection=collection, session=None,
        )


def test_03_append_bson_and_exact_replay(isolated):
    client, collection = isolated
    candidate = make()
    with tx(client) as session:
        assert reg.append(event=candidate, collection=collection, session=session) == candidate
    with tx(client) as session:
        assert reg.append(event=candidate, collection=collection, session=session) == candidate
        assert history(collection, session, candidate) == (candidate,)
    assert collection.count_documents({
        "tenant_id": candidate.tenant_id,
        "clearance_event_id": candidate.clearance_event_id,
    }) == 1


def test_04_divergent_replay_rejected(isolated):
    from dataclasses import replace
    client, collection = isolated
    candidate = make()
    with tx(client) as session:
        reg.append(event=candidate, collection=collection, session=session)
    forged = replace(candidate, confidentiality_decision_reference="different-review")
    with pytest.raises(reg.ClearanceConflict):
        with tx(client) as session:
            reg.append(event=forged, collection=collection, session=session)


def test_05_tenant_isolation(isolated):
    client, collection = isolated
    candidate = make()
    with tx(client) as session:
        reg.append(event=candidate, collection=collection, session=session)
    with tx(client) as session:
        assert reg.list_history(
            tenant_id="foreign-tenant",
            case_matter_id=candidate.case_matter_id,
            practitioner_principal_id=candidate.practitioner_principal_id,
            collection=collection, session=session,
        ) == ()


def test_06_revocation_successor(isolated):
    client, collection = isolated
    root = make()
    with tx(client) as session:
        reg.append(event=root, collection=collection, session=session)
    successor = make(
        tenant_id=root.tenant_id, case_matter_id=root.case_matter_id,
        practitioner_principal_id=root.practitioner_principal_id,
        predecessor_event_id=root.clearance_event_id,
        decision="REVOKED", effective_at=NOW + timedelta(days=1),
    )
    with tx(client) as session:
        reg.append(event=successor, collection=collection, session=session)
        assert len(history(collection, session, root)) == 2


def test_07_transaction_abort_rolls_back(isolated):
    client, collection = isolated
    candidate = make()
    with pytest.raises(RuntimeError, match="G51_INTENTIONAL_ABORT"):
        with tx(client) as session:
            reg.append(event=candidate, collection=collection, session=session)
            raise RuntimeError("G51_INTENTIONAL_ABORT")
    assert collection.count_documents({
        "tenant_id": candidate.tenant_id,
        "clearance_event_id": candidate.clearance_event_id,
    }) == 0


def test_08_competing_roots_one_commits(isolated):
    client, collection = isolated
    scope = "matter-race-" + uuid.uuid4().hex
    barrier = Barrier(2, timeout=15)

    def contender(number):
        candidate = make(
            case_matter_id=scope,
            clearance_event_id=f"race-root-{number}-{uuid.uuid4().hex}",
            confidentiality_decision_reference=f"review-race-{number}",
        )
        try:
            with tx(client) as session:
                barrier.wait()
                reg.append(event=candidate, collection=collection, session=session)
            return "COMMITTED"
        except Exception as exc:
            return type(exc).__name__

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(contender, n) for n in (1, 2)]
        results = [f.result(timeout=35) for f in futures]
    assert results.count("COMMITTED") == 1, results
    assert collection.count_documents({
        "tenant_id": "tenant-g51",
        "case_matter_id": scope,
        "practitioner_principal_id": "practitioner-g51",
        "predecessor_event_id": None,
    }) == 1


def test_09_persisted_tampering_rejected(isolated):
    client, collection = isolated
    candidate = make()
    with tx(client) as session:
        reg.append(event=candidate, collection=collection, session=session)
    collection.update_one(
        {"tenant_id": candidate.tenant_id,
         "clearance_event_id": candidate.clearance_event_id},
        {"$set": {"fingerprint": "f" * 128}},
    )
    with pytest.raises(reg.ClearancePersistedInvalid):
        with tx(client) as session:
            history(collection, session, candidate)


def test_10_second_root_rejected(isolated):
    client, collection = isolated
    root = make()
    with tx(client) as session:
        reg.append(event=root, collection=collection, session=session)
    another = make(
        tenant_id=root.tenant_id, case_matter_id=root.case_matter_id,
        practitioner_principal_id=root.practitioner_principal_id,
    )
    with pytest.raises(reg.ClearanceConflict):
        with tx(client) as session:
            reg.append(event=another, collection=collection, session=session)



def test_11_exact_partial_unique_index_contract(isolated):
    """Assert MongoDB actually installed the intended index predicates."""
    _, collection = isolated
    indexes = {
        item["name"]: item for item in collection.list_indexes()
    }

    root = indexes[reg.ROOT_INDEX]
    successor = indexes[reg.SUCCESSOR_INDEX]

    expected_scope = [
        ("tenant_id", 1),
        ("case_matter_id", 1),
        ("practitioner_principal_id", 1),
    ]

    assert list(root["key"].items()) == expected_scope
    assert root.get("unique") is True
    assert root["partialFilterExpression"] == {
        "predecessor_event_id": None
    }

    assert list(successor["key"].items()) == (
        expected_scope + [("predecessor_event_id", 1)]
    )
    assert successor.get("unique") is True
    assert successor["partialFilterExpression"] == {
        "predecessor_event_id": {"$type": "string"}
    }

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )


def test_12_competing_successors_single_winner(isolated):
    """Only one terminal successor may commit for an exact predecessor."""
    client, collection = isolated
    root = make()

    with tx(client) as session:
        reg.append(
            event=root,
            collection=collection,
            session=session,
        )

    barrier = Barrier(2, timeout=15)

    def contender(number):
        candidate = make(
            tenant_id=root.tenant_id,
            case_matter_id=root.case_matter_id,
            practitioner_principal_id=root.practitioner_principal_id,
            clearance_event_id=(
                "g54-successor-" + str(number) + "-" + uuid.uuid4().hex
            ),
            predecessor_event_id=root.clearance_event_id,
            decision="REVOKED" if number == 1 else "DENIED",
            effective_at=NOW + timedelta(hours=number),
            confidentiality_decision_reference="g54-review-" + str(number),
        )
        try:
            with tx(client) as session:
                barrier.wait()
                reg.append(
                    event=candidate,
                    collection=collection,
                    session=session,
                )
            return "COMMITTED"
        except Exception as exc:
            return type(exc).__name__

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(contender, number)
            for number in (1, 2)
        ]
        results = [
            future.result(timeout=40)
            for future in futures
        ]

    assert results.count("COMMITTED") == 1, results
    assert len(results) == 2

    exact_scope = {
        "tenant_id": root.tenant_id,
        "case_matter_id": root.case_matter_id,
        "practitioner_principal_id": root.practitioner_principal_id,
    }

    assert collection.count_documents({
        **exact_scope,
        "predecessor_event_id": root.clearance_event_id,
    }) == 1

    with tx(client) as session:
        durable = reg.list_history(
            **exact_scope,
            collection=collection,
            session=session,
        )

    assert len(durable) == 2
    assert sum(
        item.predecessor_event_id == root.clearance_event_id
        for item in durable
    ) == 1
    assert any(
        item.clearance_event_id == root.clearance_event_id
        for item in durable
    )
    assert all(
        item.tenant_id == root.tenant_id
        and item.case_matter_id == root.case_matter_id
        and item.practitioner_principal_id == root.practitioner_principal_id
        for item in durable
    )
