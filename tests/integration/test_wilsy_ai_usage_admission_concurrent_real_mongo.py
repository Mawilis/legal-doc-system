"""TITLE: C1B usage admission concurrent real-Mongo certificate.
VERSION: v1.0.1-C1B-R3B
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certify durable tenant reservations and deterministic same-window
         serialization against the repository's local replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_usage_admission_concurrent_real_mongo.py
CHANGELOG: v1.0.1-C1B-R3B keeps the deterministic concurrency proof while
           selecting only canonical admission rows for raw inspection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone, timedelta
import os
from threading import Barrier, Thread
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.saas.billing.wilsy_ai_usage_admission_registry import WilsyAIUsageAdmissionRegistry, WilsyAIUsageAdmissionConflictError, ensure_indexes
from tools.eos.saas.domain.wilsy_ai_usage_admission import WilsyAIUsageAdmission


URI = os.getenv("WILSY_AI_ADMISSION_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")


def _admission(tenant: str, key: str, ident: str, units: int = 1) -> WilsyAIUsageAdmission:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return WilsyAIUsageAdmission(tenant, ident, key, "ent-a", "WILSY_AI_REASONING", 1, "a" * 128, now, now + timedelta(days=1), reserved_request_units=units, created_at=now, updated_at=now)


@pytest.fixture()
def database():
    client = MongoClient(URI, serverSelectionTimeoutMS=1500)
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary"):
            pytest.skip("C1B Mongo replica set is not a writable certified primary")
        db = client[f"c1b_admission_cert_{uuid4().hex}"]
        yield client, db
    except Exception as error:
        pytest.skip(f"C1B Mongo runtime unavailable: {type(error).__name__}")
    finally:
        client.close()


def test_durable_replay_isolation_and_abort(database) -> None:
    client, db = database
    collection = db.admissions
    ensure_indexes(collection)
    registry = WilsyAIUsageAdmissionRegistry(collection)
    with client.start_session() as session:
        with session.start_transaction():
            item = registry.create_or_replay(_admission("tenant-a", "k", "a"), session=session)
            assert registry.create_or_replay(item, session=session) == item
        with pytest.raises(WilsyAIUsageAdmissionConflictError):
            with session.start_transaction(): registry.create_or_replay(_admission("tenant-a", "k", "b"), session=session)
        with session.start_transaction():
            assert registry.get(tenant_id="tenant-a", admission_id="a", session=session) == item
            with pytest.raises(Exception): registry.get(tenant_id="tenant-b", admission_id="a", session=session)
        with pytest.raises(Exception):
            with session.start_transaction():
                registry.create_or_replay(_admission("tenant-a", "abort", "abort"), session=session)
                raise RuntimeError("abort")
    assert collection.find_one({"admission_id": "abort"}) is None


def test_concurrent_capacity_never_exceeds_limit(database) -> None:
    client, db = database
    collection = db.concurrent
    ensure_indexes(collection)
    registry = WilsyAIUsageAdmissionRegistry(collection)
    barrier = Barrier(2); outcomes: list[str] = []
    def worker(ident: str) -> None:
        with client.start_session() as session:
            try:
                with session.start_transaction():
                    barrier.wait(timeout=5)
                    registry.reserve(_admission("tenant-c", ident, ident), available_request_units=1, session=session)
                outcomes.append("WIN")
            except Exception:
                outcomes.append("LOSE")
    threads = [Thread(target=worker, args=(f"a-{i}",)) for i in range(2)]
    for thread in threads: thread.start()
    for thread in threads: thread.join(timeout=10)
    assert outcomes.count("WIN") == 1 and outcomes.count("LOSE") == 1
    admission_row = collection.find_one(
        {
            "tenant_id": "tenant-c",
            "state": {"$in": ["RESERVED", "CLAIMED", "COMPLETED", "RELEASED", "RECONCILIATION_REQUIRED"]},
        },
        projection={"window_start": 1},
    )
    assert admission_row is not None
    with client.start_session() as read_session:
        assert registry.held_request_units(tenant_id="tenant-c", entitlement_id="ent-a", window_start=admission_row["window_start"], session=read_session) == 1


# ARTIFACT: test_wilsy_ai_usage_admission_concurrent_real_mongo.py
# VERSION: v1.0.1-C1B-R3B
# END OF WILSY OS SOVEREIGN ARTIFACT
