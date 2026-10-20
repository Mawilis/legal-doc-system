"""P4-R4-R3 dedicated, self-owned disposable-Mongo provisioning certificate.

Uses a random localhost port and a temporary replica-set data directory.
No ambient URI, shared database, protected port, or production identity.
Actor IAM, lifecycle and conflict-disposition readers remain isolated.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterator
from unittest.mock import Mock
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
    legal_practitioner_matter_access_registry as access_registry,
    legal_practitioner_matter_binding_registry as binding_registry,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_history_reader import (
    read_practitioner_matter_access_history,
)
from tools.eos.legal_operations.service import (
    legal_practitioner_matter_binding_provisioning_service as service,
)

ROOT = Path(__file__).resolve().parents[2]
POS = runpy.run_path(str(
    ROOT / "tests/unit/"
    "test_legal_practitioner_matter_binding_provisioning_positive.py"
))
CONTEXT = POS["context"]
REVOKE_KWARGS = POS["revoke_kwargs"]
MONGOD = Path("/opt/homebrew/bin/mongod")


@pytest.fixture(scope="module")
def isolated_mongo() -> Iterator[MongoClient[Any]]:
    assert MONGOD.is_file(), "DISPOSABLE_MONGOD_MISSING"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    assert port not in (27017, 27027, 61391)
    replica = "wilsyP9Provision" + uuid.uuid4().hex[:12]

    with TemporaryDirectory(prefix="wilsy-p9-provision-r3-") as temp:
        folder = Path(temp)
        data = folder / "data"
        data.mkdir()
        log = folder / "mongod.log"

        process = None
        bootstrap = None
        client = None

        try:
            process = subprocess.Popen(
                [
                    str(MONGOD),
                    "--dbpath", str(data),
                    "--port", str(port),
                    "--bind_ip", "127.0.0.1",
                    "--replSet", replica,
                    "--nounixsocket",
                    "--logpath", str(log),
                    "--quiet",
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

            deadline = time.monotonic() + 30
            while True:
                assert process.poll() is None, "DISPOSABLE_MONGOD_EXITED"
                try:
                    bootstrap.admin.command("ping")
                    break
                except PyMongoError:
                    assert time.monotonic() < deadline, "STARTUP_TIMEOUT"
                    time.sleep(0.25)

            bootstrap.admin.command({
                "replSetInitiate": {
                    "_id": replica,
                    "members": [{
                        "_id": 0,
                        "host": f"127.0.0.1:{port}",
                    }],
                }
            })

            client = MongoClient(
                f"mongodb://127.0.0.1:{port}/?replicaSet={replica}",
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
                retryWrites=False,
                tz_aware=True,
            )

            deadline = time.monotonic() + 35
            while True:
                assert process.poll() is None, "REPLICA_SET_PROCESS_EXITED"
                try:
                    hello = client.admin.command("hello")
                    if hello.get("isWritablePrimary") is True:
                        break
                except PyMongoError:
                    pass
                assert time.monotonic() < deadline, "ELECTION_TIMEOUT"
                time.sleep(0.25)

            assert hello["setName"] == replica
            assert hello.get("logicalSessionTimeoutMinutes") is not None

            with client.start_session() as session:
                assert session is not None

            yield client

        finally:
            if client is not None:
                client.close()
            if bootstrap is not None:
                bootstrap.close()
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)


@pytest.fixture()
def collections(isolated_mongo):
    name = "wilsy_p9_provision_" + uuid.uuid4().hex
    db = isolated_mongo[name]
    access = db["practitioner_access_evidence"]
    binding = db["practitioner_binding_history"]

    access_registry.ensure_indexes(access)
    binding_registry.ensure_indexes(binding)

    try:
        yield access, binding, isolated_mongo
    finally:
        isolated_mongo.drop_database(name)


def prepare(monkeypatch, collections):
    access, binding, client = collections
    kwargs, context = CONTEXT(monkeypatch)
    kwargs["access_evidence_collection"] = access
    kwargs["binding_collection"] = binding

    monkeypatch.setattr(
        service, "get_by_id", access_registry.get_by_id
    )
    monkeypatch.setattr(
        service,
        "read_practitioner_matter_access_history",
        read_practitioner_matter_access_history,
    )
    return kwargs, context, access, binding, client


def seed(client, collection, evidence):
    with client.start_session() as session:
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            access_registry.append_evidence(
                evidence=evidence,
                collection=collection,
                session=session,
            )


def test_physical_replica_topology_and_index_constraints(collections):
    access, binding, client = collections
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None

    for collection in (access, binding):
        indexes = list(collection.list_indexes())
        assert len(indexes) >= 3
        assert any(row.get("unique") is True for row in indexes)
        assert all("expireAfterSeconds" not in row for row in indexes)


def test_real_mongo_grant_and_revoke_are_immutable(monkeypatch, collections):
    kwargs, ctx, access, binding, client = prepare(
        monkeypatch, collections
    )
    seed(client, access, ctx["evidence"])

    with client.start_session() as session:
        kwargs["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            granted = service.grant_binding(**kwargs)
            assert granted.status.value == "ACTIVE"
            assert binding.count_documents(
                {"tenant_id": kwargs["tenant_id"]},
                session=session,
            ) == 1

    assert binding.count_documents({}) == 1

    with client.start_session() as session:
        kwargs["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            revoked = service.revoke_binding(**REVOKE_KWARGS(kwargs))
            assert revoked.status.value == "REVOKED"
            history = binding_registry.read_binding_history(
                tenant_id=kwargs["tenant_id"],
                binding_id=kwargs["binding_id"],
                collection=binding,
                session=session,
            )
            assert history == (granted, revoked)

    assert binding.count_documents({}) == 2


def test_physical_transaction_abort_leaves_no_binding(
    monkeypatch, collections
):
    kwargs, ctx, access, binding, client = prepare(
        monkeypatch, collections
    )
    seed(client, access, ctx["evidence"])

    with pytest.raises(RuntimeError, match="FORCED_ABORT"):
        with client.start_session() as session:
            kwargs["session"] = session
            with session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority"),
            ):
                service.grant_binding(**kwargs)
                assert binding.count_documents(
                    {}, session=session
                ) == 1
                raise RuntimeError("FORCED_ABORT")

    assert binding.count_documents({}) == 0


def test_physical_missing_policy_denied_before_binding(
    monkeypatch, collections
):
    kwargs, ctx, access, binding, client = prepare(
        monkeypatch, collections
    )
    with client.start_session() as session:
        kwargs["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            with pytest.raises(
                service.PractitionerBindingProvisioningDenied
            ):
                service.grant_binding(**kwargs)

    assert binding.count_documents({}) == 0


def test_physical_exact_replay_and_tenant_isolation(
    monkeypatch, collections
):
    kwargs, ctx, access, binding, client = prepare(
        monkeypatch, collections
    )
    seed(client, access, ctx["evidence"])

    with client.start_session() as session:
        kwargs["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            first = service.grant_binding(**kwargs)
            second = service.grant_binding(**kwargs)
            assert first == second

            assert binding_registry.read_binding_history(
                tenant_id="foreign-tenant",
                binding_id=kwargs["binding_id"],
                collection=binding,
                session=session,
            ) == ()

    assert binding.count_documents({}) == 1



def test_physical_competing_grants_one_winner(
    monkeypatch, collections
):
    """Different IDs cannot reserve the same active tenant/matter/practitioner."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    kwargs, ctx, access, binding, client = prepare(
        monkeypatch, collections
    )
    seed(client, access, ctx["evidence"])
    barrier = Barrier(2, timeout=12)

    def attempt(binding_id):
        local = dict(kwargs)
        local["binding_id"] = binding_id
        with client.start_session() as session:
            local["session"] = session
            try:
                with session.start_transaction(
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority"),
                ):
                    barrier.wait()
                    value = service.grant_binding(**local)
                return ("COMMITTED", value.binding_id)
            except Exception as exc:
                return ("DENIED", type(exc).__name__)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(attempt, "competing-binding-a")
        second = pool.submit(attempt, "competing-binding-b")
        outcomes = (first.result(timeout=35), second.result(timeout=35))

    assert sum(x[0] == "COMMITTED" for x in outcomes) == 1, outcomes
    assert sum(x[0] == "DENIED" for x in outcomes) == 1, outcomes

    records = list(binding.find({}))
    assert len(records) == 1
    assert records[0]["status"] == "ACTIVE"
    assert records[0]["binding_id"] in (
        "competing-binding-a", "competing-binding-b",
    )


def test_physical_sequential_scope_collision_denied(
    monkeypatch, collections
):
    """A second active binding ID cannot claim the same exact scope."""
    kwargs, ctx, access, binding, client = prepare(
        monkeypatch, collections
    )
    seed(client, access, ctx["evidence"])

    with client.start_session() as session:
        kwargs["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            first = service.grant_binding(**kwargs)
    assert first.status.value == "ACTIVE"

    another = dict(kwargs)
    another["binding_id"] = "different-binding-same-scope"

    with client.start_session() as session:
        another["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            with pytest.raises(
                service.PractitionerBindingProvisioningDenied
            ):
                service.grant_binding(**another)

    assert binding.count_documents({}) == 1


def test_physical_competing_revocations_one_success(
    monkeypatch, collections
):
    """Independent transactions cannot append two revocations."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    kwargs, ctx, access, binding, client = prepare(
        monkeypatch, collections
    )
    seed(client, access, ctx["evidence"])

    with client.start_session() as session:
        kwargs["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            active = service.grant_binding(**kwargs)

    barrier = Barrier(2, timeout=12)

    def attempt(reference):
        local = dict(kwargs)
        local["evidence_reference"] = reference
        with client.start_session() as session:
            local["session"] = session
            revocation = REVOKE_KWARGS(local)
            revocation["evidence_reference"] = reference
            try:
                with session.start_transaction(
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority"),
                ):
                    barrier.wait()
                    result = service.revoke_binding(**revocation)
                return ("COMMITTED", result.fingerprint)
            except Exception as exc:
                return ("DENIED", type(exc).__name__)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(attempt, "revocation-competing-a")
        second = pool.submit(attempt, "revocation-competing-b")
        outcomes = (first.result(timeout=35), second.result(timeout=35))

    assert sum(x[0] == "COMMITTED" for x in outcomes) == 1, outcomes
    assert sum(x[0] == "DENIED" for x in outcomes) == 1, outcomes

    records = list(binding.find({
        "tenant_id": active.tenant_id,
        "binding_id": active.binding_id,
    }))
    assert len(records) == 2
    assert sorted(x["status"] for x in records) == [
        "ACTIVE", "REVOKED",
    ]
    assert sum(x["status"] == "REVOKED" for x in records) == 1


def test_physical_revocation_blocks_unlinked_regrant(
    monkeypatch, collections
):
    """Historic active reservation cannot become a separate regrant."""
    kwargs, ctx, access, binding, client = prepare(
        monkeypatch, collections
    )
    seed(client, access, ctx["evidence"])

    with client.start_session() as session:
        kwargs["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            service.grant_binding(**kwargs)

    with client.start_session() as session:
        kwargs["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            service.revoke_binding(**REVOKE_KWARGS(kwargs))

    different = dict(kwargs)
    different["binding_id"] = "unlinked-regrant-attempt"
    with client.start_session() as session:
        different["session"] = session
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        ):
            with pytest.raises(
                service.PractitionerBindingProvisioningDenied
            ):
                service.grant_binding(**different)

    assert binding.count_documents({}) == 2

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4-R4-R3-P2-DISPOSABLE-MONGO
# END OF WILSY OS SOVEREIGN ARTIFACT
