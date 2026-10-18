"""
WILSY OS — Transition Work-Materialization Receipt Registry Real-Mongo Certificate

VERSION:
    v1.0.0-P14-P15-RECEIPT-REGISTRY-REAL-MONGO-CERT

AUTHORITY:
    Wilsy OS Core Governance / Legal Operations.

EPITOME:
    Certifies immutable transition-to-work receipt durability against a caller-
    owned transaction on an owned disposable MongoDB replica set.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/
    test_legal_transition_work_materialization_receipt_registry_real_mongo.py

COLLABORATION / OWNERSHIP:
    Receipt domain -> receipt registry -> materializer service certification.

CERTIFICATION DATE:
    2026-10-16

CHANGELOG:
    v1.0.0 — Initial real-Mongo durability, replay, isolation, corruption,
    uniqueness, rollback, and non-TTL certificate.

COMPLIANCE / SECURITY / PRIVACY:
    POPIA section 19, GDPR Article 32, SOC 2 CC7.2; tenant-first reads and
    indexes. Test data is synthetic and contains no PII.

TENANT BOUNDARY:
    Every registry operation and every institutional index begins with tenant.

AUTHORITY BOUNDARY:
    Persistence evidence only. This artifact selects no policy and creates no
    work, assignment, supervision, IAM, deadline, notification, or AI truth.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution authority.

PROTECTED MONGO:
    The harness must inject an owned disposable replica-set URI. The protected
    campaign Mongo endpoint is forbidden and is never encoded in this file.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_transition_work_materialization_receipt import (
    LegalTransitionWorkMaterializationOutput,
    LegalTransitionWorkMaterializationReceipt,
)
from tools.eos.legal_operations.registry.legal_transition_work_materialization_receipt_registry import (
    COLLECTION_NAME,
    LegalTransitionWorkMaterializationReceiptRegistry,
    LegalTransitionWorkMaterializationReceiptRegistryConflictError,
    LegalTransitionWorkMaterializationReceiptRegistryNotFoundError,
    LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError,
    LegalTransitionWorkMaterializationReceiptRegistryTransactionRequiredError,
)


VERSION = "v1.0.0-P14-P15-RECEIPT-REGISTRY-REAL-MONGO-CERT"
MONGO_URI = os.environ[
    "TEST_LEGAL_TRANSITION_WORK_MATERIALIZATION_RECEIPT_MONGO_URI"
]
REPLICA_SET = os.environ[
    "TEST_LEGAL_TRANSITION_WORK_MATERIALIZATION_RECEIPT_REPLICA_SET"
]
NOW = datetime(2026, 10, 16, 8, 30, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


class _Context:
    """Own one isolated real-Mongo certificate database and registry."""

    def __init__(
        self,
        client: MongoClient[Any],
        database: Any,
        collection: Any,
    ) -> None:
        self.client = client
        self.database = database
        self.collection = collection
        self.registry = LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )


@pytest.fixture
def mongo_context() -> Iterator[_Context]:
    """Yield an isolated writable-primary database and remove it afterward."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        replicaSet=REPLICA_SET,
        serverSelectionTimeoutMS=5000,
        tz_aware=True,
    )
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True
    assert hello.get("setName") == REPLICA_SET

    database = client["wilsy_p14_receipt_" + uuid4().hex]
    collection = database[COLLECTION_NAME]
    context = _Context(client, database, collection)
    context.registry.ensure_indexes()

    try:
        yield context
    finally:
        client.drop_database(database.name)
        client.close()


def _output(
    work_item_id: str = "work-a",
    fingerprint: str = FP_C,
) -> LegalTransitionWorkMaterializationOutput:
    """Build one deterministic synthetic materialization output."""
    return LegalTransitionWorkMaterializationOutput(
        work_item_id=work_item_id,
        work_item_fingerprint=fingerprint,
    )


def _receipt(
    *,
    tenant_id: str = "tenant-law",
    case_matter_id: str = "matter-1",
    transition_id: str = "transition-1",
    policy_revision: int = 1,
    policy_fingerprint: str = FP_B,
    outputs: tuple[LegalTransitionWorkMaterializationOutput, ...] | None = None,
) -> LegalTransitionWorkMaterializationReceipt:
    """Build strict immutable synthetic receipt truth."""
    return LegalTransitionWorkMaterializationReceipt(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        transition_id=transition_id,
        transition_fingerprint=FP_A,
        workflow_definition_id="workflow-litigation",
        target_stage_definition_id="stage-filing",
        policy_id="policy-filing",
        policy_revision=policy_revision,
        policy_fingerprint=policy_fingerprint,
        outputs=outputs or (_output(),),
        materialized_at=NOW,
    )


def _commit_create(
    context: _Context,
    value: LegalTransitionWorkMaterializationReceipt,
) -> LegalTransitionWorkMaterializationReceipt:
    """Persist through the required caller-owned transaction boundary."""
    with context.client.start_session() as session:
        with session.start_transaction():
            return context.registry.create_or_replay(value, session=session)


def test_real_indexes_are_exact_unique_tenant_first_and_non_ttl(
    mongo_context: _Context,
) -> None:
    indexes = {
        entry["name"]: entry
        for entry in mongo_context.collection.list_indexes()
    }
    expected = {
        "legal_transition_work_materialization_receipt_identity_unique": (
            {"tenant_id": 1, "receipt_id": 1}, True
        ),
        "legal_transition_work_materialization_receipt_transition_unique": (
            {"tenant_id": 1, "transition_id": 1}, True
        ),
        "legal_transition_work_materialization_receipt_fingerprint_unique": (
            {"tenant_id": 1, "fingerprint": 1}, True
        ),
        "legal_transition_work_materialization_receipt_matter": (
            {"tenant_id": 1, "case_matter_id": 1}, False
        ),
        "legal_transition_work_materialization_receipt_policy": (
            {"tenant_id": 1, "policy_id": 1, "policy_revision": 1}, False
        ),
    }

    for name, (keys, unique) in expected.items():
        assert indexes[name]["key"] == keys
        assert (indexes[name].get("unique") is True) is unique

    assert all("expireAfterSeconds" not in value for value in indexes.values())


def test_real_active_caller_transaction_is_required(
    mongo_context: _Context,
) -> None:
    with mongo_context.client.start_session() as session:
        with pytest.raises(
            LegalTransitionWorkMaterializationReceiptRegistryTransactionRequiredError,
            match="ACTIVE_TRANSACTION_REQUIRED",
        ):
            mongo_context.registry.create_or_replay(_receipt(), session=session)


def test_real_first_insert_exact_replay_and_mongo_id_boundary(
    mongo_context: _Context,
) -> None:
    value = _receipt()
    assert _commit_create(mongo_context, value) == value
    assert _commit_create(mongo_context, value) == value
    assert mongo_context.collection.count_documents({}) == 1
    assert mongo_context.collection.find_one({"transition_id": value.transition_id})[
        "_id"
    ] is not None

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            assert mongo_context.registry.get_by_receipt_id(
                value.tenant_id, value.receipt_id, session=session
            ) == value


@pytest.mark.parametrize(
    "divergent",
    (
        _receipt(policy_revision=2, policy_fingerprint="d" * 128),
        _receipt(outputs=(_output("work-b", "e" * 128),)),
    ),
)
def test_real_divergent_transition_replay_fails_closed(
    mongo_context: _Context,
    divergent: LegalTransitionWorkMaterializationReceipt,
) -> None:
    _commit_create(mongo_context, _receipt())
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalTransitionWorkMaterializationReceiptRegistryConflictError,
                match="DIVERGENT_TRANSITION_REPLAY",
            ):
                mongo_context.registry.create_or_replay(divergent, session=session)
            session.abort_transaction()
    assert mongo_context.collection.count_documents({}) == 1


def test_real_cross_tenant_identity_and_reads_are_isolated(
    mongo_context: _Context,
) -> None:
    left = _receipt(tenant_id="tenant-left")
    right = _receipt(tenant_id="tenant-right")
    _commit_create(mongo_context, left)
    _commit_create(mongo_context, right)
    assert mongo_context.collection.count_documents({"transition_id": "transition-1"}) == 2

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            assert mongo_context.registry.get_by_transition_id(
                "tenant-left", "transition-1", session=session
            ) == left
            assert mongo_context.registry.get_by_transition_id(
                "tenant-right", "transition-1", session=session
            ) == right
            with pytest.raises(
                LegalTransitionWorkMaterializationReceiptRegistryNotFoundError
            ):
                mongo_context.registry.get_by_receipt_id(
                    "tenant-third", left.receipt_id, session=session
                )


def test_real_matter_and_policy_listings_are_exact_tenant_scoped(
    mongo_context: _Context,
) -> None:
    first = _receipt()
    second = _receipt(transition_id="transition-2")
    other_matter = _receipt(case_matter_id="matter-2", transition_id="transition-3")
    other_tenant = _receipt(tenant_id="tenant-other", transition_id="transition-4")
    for value in (first, second, other_matter, other_tenant):
        _commit_create(mongo_context, value)

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            assert mongo_context.registry.list_matter(
                "tenant-law", "matter-1", session=session
            ) == (first, second)
            assert mongo_context.registry.list_policy_revision(
                "tenant-law", "policy-filing", 1, session=session
            ) == (first, second, other_matter)


def test_real_caller_abort_removes_inserted_receipt(
    mongo_context: _Context,
) -> None:
    value = _receipt(transition_id="transition-abort")
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert mongo_context.registry.create_or_replay(value, session=session) == value
        assert mongo_context.collection.count_documents(
            {"transition_id": value.transition_id}, session=session
        ) == 1
        session.abort_transaction()
    assert mongo_context.collection.count_documents(
        {"transition_id": value.transition_id}
    ) == 0


@pytest.mark.parametrize(
    "mutation",
    (
        {"$set": {"fingerprint": "0" * 128}},
        {"$set": {"unexpected": "forbidden"}},
    ),
)
def test_real_persisted_corruption_and_extra_fields_reject_strictly(
    mongo_context: _Context,
    mutation: dict[str, object],
) -> None:
    value = _receipt(transition_id="transition-corrupt")
    _commit_create(mongo_context, value)
    mongo_context.collection.update_one(
        {"tenant_id": value.tenant_id, "transition_id": value.transition_id},
        mutation,
    )
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError
            ):
                mongo_context.registry.get_by_transition_id(
                    value.tenant_id, value.transition_id, session=session
                )


def test_real_unique_indexes_enforce_all_three_immutable_coordinates(
    mongo_context: _Context,
) -> None:
    value = _receipt()
    _commit_create(mongo_context, value)
    raw = value.to_dict()

    variants = []
    duplicate_receipt = dict(raw)
    duplicate_receipt.update(
        transition_id="transition-other", fingerprint="d" * 128
    )
    variants.append(duplicate_receipt)

    duplicate_transition = dict(raw)
    duplicate_transition.update(receipt_id="e" * 128, fingerprint="f" * 128)
    variants.append(duplicate_transition)

    duplicate_fingerprint = dict(raw)
    duplicate_fingerprint.update(receipt_id="1" * 128, transition_id="transition-third")
    variants.append(duplicate_fingerprint)

    for variant in variants:
        with pytest.raises(DuplicateKeyError):
            mongo_context.collection.insert_one(variant)


def test_real_sequential_competition_yields_one_truth_and_rejects_divergence(
    mongo_context: _Context,
) -> None:
    value = _receipt(transition_id="transition-race")
    assert _commit_create(mongo_context, value) == value
    assert _commit_create(mongo_context, value) == value
    divergent = _receipt(
        transition_id="transition-race",
        outputs=(_output("work-race-other", "9" * 128),),
    )
    with pytest.raises(LegalTransitionWorkMaterializationReceiptRegistryConflictError):
        _commit_create(mongo_context, divergent)
    assert mongo_context.collection.count_documents(
        {"tenant_id": value.tenant_id, "transition_id": value.transition_id}
    ) == 1


def test_real_registry_has_no_current_pointer_or_auxiliary_collection(
    mongo_context: _Context,
) -> None:
    assert not hasattr(mongo_context.registry, "_current_collection")
    assert mongo_context.database.list_collection_names() == [COLLECTION_NAME]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_transition_work_materialization_receipt_registry_real_mongo.py
# VERSION: v1.0.0-P14-P15-RECEIPT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated receipt durability evidence only
# TENANT POSTURE: tenant-first indexes, queries, reads and listings
# FAIL-CLOSED POSTURE: divergence, corruption and inactive transaction reject
# EXACT REPLAY / CALLER ROLLBACK / REAL UNIQUENESS: CERTIFIED BY THIS SUITE
# TTL / MUTABLE CURRENT POINTER: ABSENT
# POLICY SELECTION / WORK / ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# LEGAL-DEADLINE / NOTIFICATION / AI AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# PROTECTED CAMPAIGN MONGO ENDPOINT: FORBIDDEN
# END OF WILSY OS SOVEREIGN ARTIFACT
