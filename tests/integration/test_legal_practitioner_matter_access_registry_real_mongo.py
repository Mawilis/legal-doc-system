"""WILSY P9-R105-P4F-R4 isolated real-Mongo practitioner registry certificate.

Runs a dedicated ephemeral localhost replica set. Does not use ambient URI,
shared production DB, protected 27027 or P6 61391. Each test run destroys
its own MongoDB process and data directory. No financial/access authority.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
import runpy
import socket
import subprocess
import time
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.registry import (
    legal_practitioner_matter_access_registry as registry,
)

ROOT = Path(__file__).resolve().parents[2]
MAKE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_access.py")
)["_make"]
MONGOD = "/opt/homebrew/bin/mongod"


@contextmanager
def transaction(client):
    with client.start_session() as session:
        with session.start_transaction():
            yield session


@pytest.fixture(scope="module")
def isolated_mongo():
    assert Path(MONGOD).is_file(), "ISOLATED_MONGOD_UNAVAILABLE"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    assert port not in (27017, 27027, 61391)
    replica = "wilsyP9Cert" + uuid.uuid4().hex[:12]
    dbname = "wilsy_p9_access_cert_" + uuid.uuid4().hex

    with TemporaryDirectory(prefix="wilsy-p9-r105-mongo-") as temporary:
        folder = Path(temporary)
        data = folder / "data"
        data.mkdir()
        log = folder / "mongod.log"
        process = None
        bootstrap = None
        client = None
        try:
            process = subprocess.Popen(
                [
                    MONGOD, "--dbpath", str(data),
                    "--port", str(port), "--bind_ip", "127.0.0.1",
                    "--replSet", replica, "--nounixsocket",
                    "--logpath", str(log), "--quiet",
                ],
                cwd=folder,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            bootstrap = MongoClient(
                f"mongodb://127.0.0.1:{port}/?directConnection=true",
                serverSelectionTimeoutMS=1000,
                connectTimeoutMS=1000,
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
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
                retryWrites=False,
                tz_aware=True,
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
                "legal_practitioner_matter_access_evidence",
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
                "ISOLATED_MONGOD_CLEANUP_FAILED"
            )


def test_01_real_unique_indexes_no_ttl(isolated_mongo):
    _, collection = isolated_mongo
    registry.ensure_indexes(collection)
    indexes = {
        value["name"]: value
        for value in collection.list_indexes()
        if value["name"] != "_id_"
    }
    assert set(indexes) == {
        registry.IDENTITY_INDEX,
        registry.REVISION_INDEX,
        registry.FINGERPRINT_INDEX,
    }
    assert all(value.get("unique") is True for value in indexes.values())
    assert all("expireAfterSeconds" not in value for value in indexes.values())


def test_02_null_transaction_denied(isolated_mongo):
    _, collection = isolated_mongo
    with pytest.raises(registry.PractitionerMatterAccessTransactionRequired):
        registry.append_evidence(
            evidence=MAKE(), collection=collection, session=None
        )


def test_03_inactive_transaction_denied(isolated_mongo):
    client, collection = isolated_mongo
    with client.start_session() as session:
        with pytest.raises(
            registry.PractitionerMatterAccessTransactionRequired
        ):
            registry.append_evidence(
                evidence=MAKE(), collection=collection, session=session
            )


def test_04_durable_append(isolated_mongo):
    client, collection = isolated_mongo
    item = MAKE()
    with transaction(client) as session:
        assert registry.append_evidence(
            evidence=item, collection=collection, session=session
        ) == item
    assert collection.count_documents({
        "tenant_id": item.tenant_id,
        "access_evidence_id": item.access_evidence_id,
    }) == 1


def test_05_exact_replay_one_row(isolated_mongo):
    client, collection = isolated_mongo
    item = MAKE()
    with transaction(client) as session:
        assert registry.append_evidence(
            evidence=item, collection=collection, session=session
        ) == item
    assert collection.count_documents({
        "tenant_id": item.tenant_id,
        "access_evidence_id": item.access_evidence_id,
    }) == 1


def test_06_divergent_replay_denied(isolated_mongo):
    client, collection = isolated_mongo
    item = MAKE()
    other = "f" * 128
    if item.source_evidence_fingerprint == other:
        other = "e" * 128
    divergent = _p47_recreate_evidence(
        item, source_evidence_fingerprint=other, fingerprint=""
    )
    with transaction(client) as session:
        with pytest.raises(registry.PractitionerMatterAccessConflict):
            registry.append_evidence(
                evidence=divergent, collection=collection, session=session
            )


def test_07_first_revision_fork_denied(isolated_mongo):
    client, collection = isolated_mongo
    item = MAKE()
    fork = _p47_recreate_evidence(
        item, access_evidence_id="p9-competing-root", fingerprint=""
    )
    with transaction(client) as session:
        with pytest.raises(registry.PractitionerMatterAccessConflict):
            registry.append_evidence(
                evidence=fork, collection=collection, session=session
            )


def test_08_tenant_isolation(isolated_mongo):
    client, collection = isolated_mongo
    item = MAKE()
    with transaction(client) as session:
        assert registry.get_by_id(
            tenant_id="different-tenant",
            access_evidence_id=item.access_evidence_id,
            collection=collection,
            session=session,
        ) is None

    other = _p47_recreate_evidence(item, tenant_id="different-tenant", fingerprint="")
    with transaction(client) as session:
        assert registry.append_evidence(
            evidence=other, collection=collection, session=session
        ) == other

    assert collection.count_documents({
        "access_evidence_id": item.access_evidence_id
    }) == 2


def test_09_transaction_abort_rolls_back(isolated_mongo):
    client, collection = isolated_mongo
    item = MAKE(
        access_evidence_id="p9-abort-probe",
        case_matter_id="p9-abort-matter",
    )
    with pytest.raises(RuntimeError, match="INTENTIONAL_ABORT"):
        with transaction(client) as session:
            registry.append_evidence(
                evidence=item, collection=collection, session=session
            )
            raise RuntimeError("INTENTIONAL_ABORT")

    assert collection.count_documents({
        "tenant_id": item.tenant_id,
        "access_evidence_id": item.access_evidence_id,
    }) == 0


def test_10_competing_writers_single_winner(isolated_mongo):
    client, collection = isolated_mongo
    original = MAKE()
    barrier = Barrier(2, timeout=15)

    def contender(number):
        candidate = _p47_recreate_evidence(
            original,
            access_evidence_id=f"p9-race-{number}",
            case_matter_id="p9-race-matter",
            practitioner_principal_id="p9-race-practitioner",
            fingerprint="",
        )
        try:
            with transaction(client) as session:
                barrier.wait()
                registry.append_evidence(
                    evidence=candidate,
                    collection=collection,
                    session=session,
                )
            return "COMMITTED"
        except Exception as exc:
            return type(exc).__name__

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(contender, n) for n in (1, 2)]
        results = [future.result(timeout=35) for future in futures]

    assert results.count("COMMITTED") == 1, results
    assert collection.count_documents({
        "tenant_id": original.tenant_id,
        "case_matter_id": "p9-race-matter",
        "practitioner_principal_id": "p9-race-practitioner",
        "revision": 1,
    }) == 1


def test_11_persisted_tampering_denied(isolated_mongo):
    client, collection = isolated_mongo
    item = MAKE()
    other = "f" * 128
    if item.source_evidence_fingerprint == other:
        other = "e" * 128

    collection.update_one(
        {
            "tenant_id": item.tenant_id,
            "access_evidence_id": item.access_evidence_id,
        },
        {"$set": {"source_evidence_fingerprint": other}},
    )

    with transaction(client) as session:
        with pytest.raises(registry.PractitionerMatterAccessPersistedInvalid):
            registry.get_by_id(
                tenant_id=item.tenant_id,
                access_evidence_id=item.access_evidence_id,
                collection=collection,
                session=session,
            )


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_registry_real_mongo.py
# VERSION: v1.0.0-P9-R105-P4F-R4
# TEST DATABASE AUTHORITY: DISPOSABLE LOCALHOST REPLICA SET ONLY
# OPERATIONAL MATTER ACCESS / FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT


def _p47_recreate_evidence(evidence, **changes):
    """Recreate changed evidence through the verified service factory."""
    from dataclasses import fields
    from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
        create_practitioner_matter_access,
    )
    values = {
        field.name: getattr(evidence, field.name)
        for field in fields(evidence)
        if field.name != "fingerprint"
    }
    changes.pop("fingerprint", None)
    values.update(changes)
    return create_practitioner_matter_access(**values)
