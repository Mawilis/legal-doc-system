"""Real-Mongo serialization test for the G65/G77 shared wall fence.

Requires WILSY_G65_REAL_MONGO_URI pointing only to a disposable replica set.
This test proves fence write ordering, not institutional authority or route safety.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC
import os
import threading
import time
import uuid

import pytest
from pymongo import MongoClient

from dataclasses import replace

from tools.eos.legal_operations.domain.legal_work_ethical_wall_policy import (
    EthicalWallPolicyStatus,
    InstitutionalRatificationState,
)
from tools.eos.legal_operations.registry import legal_work_ethical_wall_policy_registry as policy_registry_module
from tests.unit.test_legal_work_ethical_wall_policy_registry import revision as make_policy_revision
from tests.unit.test_legal_work_ethical_wall_policy_registry import successor as make_policy_successor

from tools.eos.legal_operations.service.legal_work_ethical_wall_authorization_fence import (
    CanonicalWallAuthorizationFence,
    FENCE_COLLECTION,
    FENCE_INDEX_FIELDS,
    FENCE_INDEX_NAME,
    WallFenceUnavailable,
    ensure_fence_index,
)

URI = os.environ.get("WILSY_G65_REAL_MONGO_URI")
pytestmark = pytest.mark.skipif(not URI, reason="isolated G65 replica-set URI is not configured")


def test_fence_writes_serialize_disclosure_and_revocation_transactions() -> None:
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True, tzinfo=UTC)
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True and hello.get("setName")
    database = client["wilsy_g65_fence_" + uuid.uuid4().hex]
    collection = database[FENCE_COLLECTION]
    ensure_fence_index(collection)
    fence = CanonicalWallAuthorizationFence(collection)
    revisions = database[policy_registry_module.REVISION_COLLECTION]
    current = database[policy_registry_module.CURRENT_COLLECTION]
    registry = policy_registry_module.EthicalWallPolicyRegistry(
        revisions, current, fence
    )
    registry.ensure_indexes()

    root = make_policy_revision(
        tenant_id="tenant-fence-test",
        case_matter_id="matter-fence-test",
        policy_id="policy-fence-test",
    )
    with client.start_session() as session:
        with session.start_transaction():
            registry.append(root, session=session)

    scope = dict(
        tenant_id=root.tenant_id,
        case_matter_id=root.case_matter_id,
        practitioner_principal_id="principal-fence-test",
        policy_id=root.policy_id,
    )
    first_has_fence = threading.Event()
    allow_first_commit = threading.Event()
    second_started = threading.Event()
    outcomes: list[str] = []

    def disclosure_transaction() -> None:
        with client.start_session() as session:
            with session.start_transaction():
                # Exact same policy-wide sentinel used by the G79 coordinator.
                fence.contend(
                    tenant_id=scope["tenant_id"],
                    case_matter_id=scope["case_matter_id"],
                    practitioner_principal_id="policy",
                    policy_id=scope["policy_id"],
                    session=session,
                )
                fence.contend(**scope, session=session)
                first_has_fence.set()
                assert allow_first_commit.wait(timeout=10), "test coordination timed out"
            outcomes.append("disclosure-transaction-committed")

    revoked = make_policy_successor(
        root,
        status=EthicalWallPolicyStatus.REVOKED,
        ratification_state=InstitutionalRatificationState.REVOKED,
        ratification_reference="ratification-revoked",
        ratification_fingerprint="e" * 128,
    )

    def revocation_transaction() -> None:
        assert first_has_fence.wait(timeout=10), "disclosure did not acquire fence"
        for attempt in range(5):
            try:
                with client.start_session() as session:
                    with session.start_transaction():
                        second_started.set()
                        registry.append(revoked, session=session)
                outcomes.append("policy-revocation-committed")
                return
            except policy_registry_module.EthicalWallPolicyRetryTransaction:
                if attempt == 4:
                    raise
                # The production contract is whole-transaction retry after the
                # competing disclosure transaction releases the policy fence.
                assert allow_first_commit.wait(timeout=10), "disclosure did not release fence"
                continue
        raise AssertionError("policy revocation retry budget exhausted")

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(disclosure_transaction)
            assert first_has_fence.wait(timeout=10)
            second = pool.submit(revocation_transaction)
            assert second_started.wait(timeout=10)
            time.sleep(0.25)
            assert not second.done(), "policy revocation bypassed the held disclosure fence"
            allow_first_commit.set()
            first.result(timeout=15)
            second.result(timeout=15)
        assert outcomes == [
            "disclosure-transaction-committed",
            "policy-revocation-committed",
        ]
        with client.start_session() as session:
            with session.start_transaction():
                final = registry.get_current(
                    root.tenant_id, root.case_matter_id, root.policy_id,
                    session=session,
                )
        assert final.status is EthicalWallPolicyStatus.REVOKED
    finally:
        allow_first_commit.set()
        client.drop_database(database.name)
        client.close()
