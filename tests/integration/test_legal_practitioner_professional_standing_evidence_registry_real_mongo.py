"""TITLE: R63 Professional Standing Registry Disposable-Mongo Certificate.
VERSION: v1.0.0-R63-REGULATORY-EVIDENCE-REAL-MONGO-CERT
AUTHORITY: Isolated localhost replica-set integration evidence only.
EPITOME: Prove transactions, indexes, replay, concurrency, durability,
    tenant isolation, tamper rejection, revocation, and currentness in MongoDB.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_practitioner_professional_standing_evidence_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Wilsy OS Legal Operations and Core Governance.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG: 2026-10-21 v1.0.0 introduces the disposable real-Mongo certificate.
SECURITY / PRIVACY POSTURE: Random port, temporary data, synthetic identifiers.
TENANT BOUNDARY: Exact tenant-scoped reads and writes.
AUTHORITY BOUNDARY: Evidence persistence only; no HTTP, IAM, access, or reassignment.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import socket
import subprocess
from tempfile import TemporaryDirectory
import time
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.domain.legal_practitioner_professional_standing_evidence import (
    LegalPractitionerProfessionalStandingEvidence as Evidence,
    ProfessionalStandingCurrentnessState,
)
from tools.eos.legal_operations.registry.legal_practitioner_professional_standing_evidence_registry import (
    INDEX_NAMES,
    LPC_PRACTITIONER_DIRECTORY_ISSUER,
    LPC_PRACTITIONER_DIRECTORY_URI,
    ProfessionalStandingEvidencePersistedInvalid,
    ProfessionalStandingEvidenceRegistry,
    ProfessionalStandingEvidenceRevision,
)


NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
MONGOD = Path("/opt/homebrew/bin/mongod")


@pytest.fixture(scope="module")
def isolated_mongo() -> Iterator[MongoClient[Any]]:
    """Create and destroy a self-owned replica set; protected ports are forbidden."""
    assert MONGOD.is_file(), "DISPOSABLE_MONGOD_MISSING"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    assert port not in (27017, 27027, 61391)
    replica = "wilsyR63Evidence" + uuid.uuid4().hex[:10]
    with TemporaryDirectory(prefix="wilsy-r63-evidence-") as temporary:
        folder = Path(temporary)
        data = folder / "data"
        data.mkdir()
        process = subprocess.Popen(
            [
                str(MONGOD), "--dbpath", str(data), "--port", str(port),
                "--bind_ip", "127.0.0.1", "--replSet", replica,
                "--nounixsocket", "--logpath", str(folder / "mongod.log"), "--quiet",
            ],
            cwd=folder,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        bootstrap: MongoClient[Any] | None = None
        client: MongoClient[Any] | None = None
        try:
            bootstrap = MongoClient(
                f"mongodb://127.0.0.1:{port}/?directConnection=true",
                serverSelectionTimeoutMS=1000,
            )
            deadline = time.monotonic() + 30
            while True:
                assert process.poll() is None, "DISPOSABLE_MONGOD_EXITED"
                try:
                    bootstrap.admin.command("ping")
                    break
                except PyMongoError:
                    assert time.monotonic() < deadline, "DISPOSABLE_MONGOD_START_TIMEOUT"
                    time.sleep(0.2)
            bootstrap.admin.command({
                "replSetInitiate": {
                    "_id": replica,
                    "members": [{"_id": 0, "host": f"127.0.0.1:{port}"}],
                }
            })
            client = MongoClient(
                f"mongodb://127.0.0.1:{port}/?replicaSet={replica}",
                serverSelectionTimeoutMS=2000,
                retryWrites=False,
                tz_aware=True,
            )
            deadline = time.monotonic() + 35
            while True:
                try:
                    hello = client.admin.command("hello")
                    if hello.get("isWritablePrimary") is True:
                        break
                except PyMongoError:
                    pass
                assert process.poll() is None, "DISPOSABLE_REPLICA_SET_EXITED"
                assert time.monotonic() < deadline, "DISPOSABLE_REPLICA_SET_TIMEOUT"
                time.sleep(0.2)
            assert hello["setName"] == replica
            assert hello["isWritablePrimary"] is True
            yield client
        finally:
            if client is not None:
                client.close()
            if bootstrap is not None:
                bootstrap.close()
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)


@pytest.fixture()
def durable(isolated_mongo: MongoClient[Any]):
    """Provide one disposable database and a fully indexed registry."""
    name = "wilsy_r63_" + uuid.uuid4().hex
    collection = isolated_mongo[name]["professional_evidence"]
    subject = ProfessionalStandingEvidenceRegistry(collection)
    subject.ensure_indexes()
    try:
        yield isolated_mongo, collection, subject
    finally:
        isolated_mongo.drop_database(name)


@contextmanager
def transaction(client: MongoClient[Any]):
    """Own transaction lifecycle outside the registry under test."""
    with client.start_session() as session:
        session.start_transaction()
        try:
            yield session
            session.commit_transaction()
        except Exception:
            session.abort_transaction()
            raise


def evidence(**overrides: object) -> Evidence:
    """Create one official-source synthetic R62 observation."""
    values: dict[str, object] = {
        "evidence_id": "evidence-1", "tenant_id": "tenant-a",
        "practitioner_principal_id": "principal-a",
        "verified_subject_id": "lpc-106800",
        "issuer_source_id": LPC_PRACTITIONER_DIRECTORY_ISSUER,
        "jurisdiction": "ZA", "evidence_kind": "PRACTISING_STATUS",
        "outcome": "VERIFIED_CURRENT",
        "verification_method": "PUBLIC_WEB_OBSERVATION",
        "evidence_reference": "lpc-observation-1",
        "source_uri": LPC_PRACTITIONER_DIRECTORY_URI,
        "observed_at": NOW, "valid_until": NOW + timedelta(days=1),
    }
    values.update(overrides)
    return Evidence(**values)  # type: ignore[arg-type]


def revision(number: int = 1, predecessor: str | None = None, **overrides: object):
    """Create one registry lineage revision."""
    return ProfessionalStandingEvidenceRevision(number, predecessor, evidence(**overrides))


def test_real_mongo_indexes_transactions_replay_and_tenant_isolation(durable) -> None:
    client, collection, subject = durable
    indexes = collection.index_information()
    assert set(INDEX_NAMES).issubset(indexes)
    assert all("expireAfterSeconds" not in value for value in indexes.values())
    first = revision()
    with transaction(client) as session:
        assert subject.create_or_replay(first, session=session) == first
        assert subject.create_or_replay(first, session=session) == first
    with transaction(client) as session:
        current = subject.evaluate_currentness(
            tenant_id="tenant-a", practitioner_principal_id="principal-a",
            verified_subject_id="lpc-106800", jurisdiction="ZA",
            evidence_kind="PRACTISING_STATUS", evaluation_time=NOW, session=session,
        )
        other = subject.get_history_if_any(
            tenant_id="tenant-b", practitioner_principal_id="principal-a",
            verified_subject_id="lpc-106800", jurisdiction="ZA",
            evidence_kind="PRACTISING_STATUS", session=session,
        )
    assert current.state is ProfessionalStandingCurrentnessState.VERIFIED_DOCUMENTARY_ONLY
    assert current.permits_operational_access is False
    assert other == ()


def test_real_mongo_revocation_restart_durability_and_tamper_rejection(durable) -> None:
    client, collection, subject = durable
    first = revision()
    with transaction(client) as session:
        subject.create_or_replay(first, session=session)
    second = revision(
        2, first.registry_fingerprint, evidence_id="evidence-2",
        evidence_reference="lpc-observation-2", outcome="REVOKED",
        observed_at=NOW + timedelta(hours=1), revoked_at=NOW + timedelta(hours=1),
        valid_until=NOW + timedelta(days=2),
    )
    with transaction(client) as session:
        subject.create_or_replay(second, session=session)
    restarted = ProfessionalStandingEvidenceRegistry(collection)
    with transaction(client) as session:
        state = restarted.evaluate_currentness(
            tenant_id="tenant-a", practitioner_principal_id="principal-a",
            verified_subject_id="lpc-106800", jurisdiction="ZA",
            evidence_kind="PRACTISING_STATUS",
            evaluation_time=NOW + timedelta(hours=2), session=session,
        )
    assert state.state is ProfessionalStandingCurrentnessState.REVOKED_BLOCKED
    collection.update_one({"revision": 1}, {"$set": {"source_uri": "https://attacker.invalid/"}})
    with pytest.raises(ProfessionalStandingEvidencePersistedInvalid):
        with transaction(client) as session:
            restarted.get_history_if_any(
                tenant_id="tenant-a", practitioner_principal_id="principal-a",
                verified_subject_id="lpc-106800", jurisdiction="ZA",
                evidence_kind="PRACTISING_STATUS", session=session,
            )


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_professional_standing_evidence_registry_real_mongo.py
# VERSION: v1.0.0-R63-REGULATORY-EVIDENCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable persistence certificate; no operational grant
# TENANT POSTURE: exact tenant scope and isolated synthetic persistence
# FAIL-CLOSED POSTURE: tampering, revocation, ambiguity and absence never grant
# PROTECTED PORT 27027: FORBIDDEN AND UNUSED
# REASSIGNMENT / FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
