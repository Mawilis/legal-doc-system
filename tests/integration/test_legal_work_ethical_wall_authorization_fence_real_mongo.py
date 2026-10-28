"""Real-Mongo serialization test for the G65/G77 shared wall fence.

Requires WILSY_G65_REAL_MONGO_URI pointing only to a disposable replica set.
This test proves fence write ordering, not institutional authority or route safety.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
import os
import threading
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.service.legal_work_ethical_wall_authorization_fence import (
    CanonicalWallAuthorizationFence,
    FENCE_COLLECTION,
    FENCE_INDEX_FIELDS,
    FENCE_INDEX_NAME,
    WallFenceUnavailable,
)

URI = os.environ.get("WILSY_G65_REAL_MONGO_URI")
pytestmark = pytest.mark.skipif(not URI, reason="isolated G65 replica-set URI is not configured")


def test_fence_writes_serialize_disclosure_and_revocation_transactions() -> None:
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True, tzinfo=UTC)
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True and hello.get("setName")
    database = client["wilsy_g65_fence_" + uuid.uuid4().hex]
    collection = database[FENCE_COLLECTION]
    collection.create_index(list(FENCE_INDEX_FIELDS), unique=True, name=FENCE_INDEX_NAME)
    fence = CanonicalWallAuthorizationFence(collection)
    scope = dict(
        tenant_id="tenant-fence-test",
        case_matter_id="matter-fence-test",
        practitioner_principal_id="principal-fence-test",
        policy_id="policy-fence-test",
    )
    first_has_fence = threading.Event()
    allow_first_commit = threading.Event()
    second_started = threading.Event()
    outcomes: list[tuple[str, int]] = []

    def disclosure_transaction() -> None:
        with client.start_session() as session:
            with session.start_transaction():
                token = fence.contend(**scope, session=session)
                outcomes.append(("disclosure", token.epoch))
                first_has_fence.set()
                assert allow_first_commit.wait(timeout=10), "test coordination timed out"

    def revocation_transaction() -> None:
        assert first_has_fence.wait(timeout=10), "disclosure did not acquire fence"
        second_started.set()
        with client.start_session() as session:
            with session.start_transaction():
                token = fence.contend(**scope, session=session)
                outcomes.append(("revocation", token.epoch))

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(disclosure_transaction)
            assert first_has_fence.wait(timeout=10)
            second = pool.submit(revocation_transaction)
            assert second_started.wait(timeout=10)
            # Give the second transaction a bounded opportunity to contend while
            # the first transaction owns the write. It must not complete first.
            assert not second.done(), "second transaction bypassed the held fence"
            allow_first_commit.set()
            first.result(timeout=15)
            second.result(timeout=15)
        assert [name for name, _ in outcomes] == ["disclosure", "revocation"]
        assert outcomes[1][1] > outcomes[0][1]
    finally:
        allow_first_commit.set()
        client.drop_database(database.name)
        client.close()
