
"""R65 disposable real-Mongo transactional and isolation certificate."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.domain.legal_practitioner_matter_access_review import (
    LegalPractitionerMatterAccessReview,
    MatterAccessReviewBlocker,
    MatterAccessReviewDecision,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_review_codec import (create_review, serialize, verify_integrity)
from tools.eos.legal_operations.registry import (
    legal_practitioner_matter_access_review_registry as registry,
)

PROTECTED_PORTS = {27017, 27027, 61391}


def make_review(
    *,
    tenant: str = "tenant-r65-a",
    request_id: str = "review-1",
    key: str = "idem-1",
) -> LegalPractitionerMatterAccessReview:
    return create_review(
        review_request_id=request_id,
        tenant_id=tenant,
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        requested_by_principal_id="partner-1",
        decision=MatterAccessReviewDecision.PENDING_REVIEW,
        blockers=(
            MatterAccessReviewBlocker.REGULATOR_ISSUER_TRUST_UNRATIFIED,
            MatterAccessReviewBlocker.ETHICAL_WALL_CLEARANCE_NOT_ESTABLISHED,
        ),
        reason_reference="reason-1",
        idempotency_key=key,
        recorded_at=datetime(2026, 10, 22, 4, 0, tzinfo=timezone.utc),
    )


@pytest.fixture(scope="module")
def isolated_mongo():
    executable = shutil.which("mongod")
    if not executable:
        pytest.fail("R65_MONGOD_BINARY_MISSING")

    # Only bind a brand-new loopback port. Never discover or reuse existing DBs.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    if port in PROTECTED_PORTS:
        pytest.fail("R65_PROTECTED_PORT_ALLOCATED")

    rs_name = "wilsy_r65_" + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix="wilsy-r65-mongo-") as folder:
        dbpath = Path(folder) / "db"
        dbpath.mkdir()
        log_path = Path(folder) / "mongod.log"

        with log_path.open("w") as output:
            proc = subprocess.Popen(
                [
                    executable,
                    "--bind_ip", "127.0.0.1",
                    "--port", str(port),
                    "--dbpath", str(dbpath),
                    "--replSet", rs_name,
                    "--nounixsocket",
                ],
                stdout=output,
                stderr=subprocess.STDOUT,
            )
            client = None
            bootstrap = None
            try:
                bootstrap = MongoClient(
                    host="127.0.0.1",
                    port=port,
                    directConnection=True,
                    serverSelectionTimeoutMS=500,
                    connectTimeoutMS=500,
                )
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    if proc.poll() is not None:
                        pytest.fail("R65_DISPOSABLE_MONGOD_EXITED")
                    try:
                        bootstrap.admin.command("ping")
                        break
                    except PyMongoError:
                        time.sleep(0.1)
                else:
                    pytest.fail("R65_DISPOSABLE_MONGOD_STARTUP_FAILED")

                bootstrap.admin.command(
                    "replSetInitiate",
                    {
                        "_id": rs_name,
                        "members": [
                            {"_id": 0, "host": f"127.0.0.1:{port}"}
                        ],
                    },
                )

                client = MongoClient(
                    host="127.0.0.1",
                    port=port,
                    replicaSet=rs_name,
                    serverSelectionTimeoutMS=500,
                )
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    try:
                        client.admin.command("ping")
                        break
                    except PyMongoError:
                        time.sleep(0.1)
                else:
                    pytest.fail("R65_DISPOSABLE_REPLICA_NOT_READY")

                dbname = "wilsy_r65_cert_" + uuid.uuid4().hex
                collection = client[dbname][registry.COLLECTION_NAME]
                registry.ensure_indexes(collection)

                yield client, collection, port

            finally:
                if client is not None:
                    client.close()
                if bootstrap is not None:
                    bootstrap.close()
                proc.terminate()
                try:
                    proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)


def test_indexes_transactions_replay_and_tenant_isolation(isolated_mongo):
    client, collection, port = isolated_mongo
    assert port not in PROTECTED_PORTS

    indexes = list(collection.list_indexes())
    names = {item["name"] for item in indexes}
    assert registry.IDENTITY_INDEX in names
    assert registry.IDEMPOTENCY_INDEX in names
    assert registry.SCOPE_INDEX in names
    assert all("expireAfterSeconds" not in item for item in indexes)

    value = make_review()
    with client.start_session() as session:
        with pytest.raises(registry.MatterAccessReviewTransactionRequired):
            registry.append_review(
                review=value, collection=collection, session=session
            )

        with session.start_transaction():
            first = registry.append_review(
                review=value, collection=collection, session=session
            )
            replay = registry.append_review(
                review=value, collection=collection, session=session
            )
            assert first == replay == value
            assert registry.get_review(
                tenant_id="tenant-r65-b",
                review_request_id=value.review_request_id,
                collection=collection,
                session=session,
            ) is None

    with client.start_session() as session:
        with session.start_transaction():
            assert registry.get_review(
                tenant_id=value.tenant_id,
                review_request_id=value.review_request_id,
                collection=collection,
                session=session,
            ) == value
            with pytest.raises(registry.MatterAccessReviewConflict):
                registry.append_review(
                    review=make_review(request_id="review-2"),
                    collection=collection,
                    session=session,
                )


def test_abort_durability_and_persisted_tamper_rejection(isolated_mongo):
    client, collection, _ = isolated_mongo
    aborted = make_review(request_id="aborted-1", key="aborted-idem")
    with client.start_session() as session:
        session.start_transaction()
        registry.append_review(
            review=aborted, collection=collection, session=session
        )
        session.abort_transaction()

    assert collection.find_one({
        "tenant_id": aborted.tenant_id,
        "review_request_id": aborted.review_request_id,
    }) is None

    value = make_review(request_id="tamper-1", key="tamper-idem")
    with client.start_session() as session:
        with session.start_transaction():
            registry.append_review(
                review=value, collection=collection, session=session
            )

    collection.update_one(
        {
            "tenant_id": value.tenant_id,
            "review_request_id": value.review_request_id,
        },
        {"$set": {"reason_reference": "altered-without-fingerprint"}},
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.MatterAccessReviewPersistedInvalid):
                registry.get_review(
                    tenant_id=value.tenant_id,
                    review_request_id=value.review_request_id,
                    collection=collection,
                    session=session,
                )
