"""
WILSY OS — Legal Work-Materialization Policy Registry Real-Mongo Certificate

VERSION:
    v1.0.0-P14-P10-WORK-MATERIALIZATION-POLICY-REGISTRY-REAL-MONGO-CERT

PURPOSE:
    Certify immutable P14 materialization-policy durability against an owned
    writable disposable Mongo replica set.

PROVES:
    - tenant-first unique indexes;
    - absence of TTL;
    - exact replay;
    - immutable revision lineage;
    - divergent replay rejection;
    - revision-gap / predecessor rejection;
    - strict persisted-corruption rejection;
    - tenant isolation;
    - real Mongo uniqueness;
    - caller transaction abort rollback;
    - latest truth derived from immutable history.

AUTHORITY:
    Persistence evidence only. No work creation, assignment, supervision,
    IAM, professional, legal-deadline, notification-delivery, AI, billing,
    payment, settlement, or financial authority.

COMPETITIVE POSTURE:
    Durable versioned workflow-to-work rules retain historical reproducibility,
    stage re-entry provenance and fail-closed lineage beyond mutable task-rule
    configuration.

PROTECTED MONGO:
    Port 27027 is forbidden by campaign policy.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_work_materialization_policy import (
    LegalOperationalDueRule,
    LegalWorkMaterializationPolicy,
    LegalWorkMaterializationTemplate,
)
from tools.eos.legal_operations.registry.legal_work_materialization_policy_registry import (
    COLLECTION_NAME,
    LegalWorkMaterializationPolicyRegistry,
    LegalWorkMaterializationPolicyRegistryConflictError,
    LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
)


VERSION = (
    "v1.0.0-P14-P10-"
    "WORK-MATERIALIZATION-POLICY-REGISTRY-REAL-MONGO-CERT"
)

MONGO_URI = os.environ[
    "TEST_LEGAL_WORK_MATERIALIZATION_POLICY_MONGO_URI"
]

REPLICA_SET = os.environ[
    "TEST_LEGAL_WORK_MATERIALIZATION_POLICY_REPLICA_SET"
]

FP_A = "a" * 128
FP_B = "b" * 128


class _Context:
    def __init__(
        self,
        client: MongoClient[Any],
        database: Any,
        collection: Any,
    ) -> None:
        self.client = client
        self.database = database
        self.collection = collection
        self.registry = LegalWorkMaterializationPolicyRegistry(
            collection
        )


@pytest.fixture
def mongo_context() -> Iterator[_Context]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        replicaSet=REPLICA_SET,
        serverSelectionTimeoutMS=5000,
        tz_aware=True,
    )

    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True
    assert hello.get("setName") == REPLICA_SET

    database = client[
        "wilsy_p14_policy_"
        + uuid4().hex
    ]

    collection = database[
        COLLECTION_NAME
    ]

    context = _Context(
        client,
        database,
        collection,
    )

    context.registry.ensure_indexes()

    try:
        yield context
    finally:
        client.drop_database(database.name)
        client.close()


def _template(
    template_id: str = "template-prepare",
    *,
    dependency_template_ids: tuple[str, ...] = (),
) -> LegalWorkMaterializationTemplate:
    return LegalWorkMaterializationTemplate(
        work_template_id=template_id,
        title=f"Governed work {template_id}",
        due_rule=LegalOperationalDueRule.TRANSITION_OFFSET,
        due_offset_seconds=3600,
        dependency_template_ids=dependency_template_ids,
        condition_references=(),
    )


def _policy(
    *,
    tenant: str = "tenant-law",
    policy_id: str = "policy-filing",
    revision: int = 1,
    supersedes: str | None = None,
    target_stage: str = "stage-filing",
    title_suffix: str = "base",
) -> LegalWorkMaterializationPolicy:
    return LegalWorkMaterializationPolicy(
        tenant_id=tenant,
        policy_id=policy_id,
        policy_revision=revision,
        workflow_definition_id="workflow-litigation",
        workflow_definition_fingerprint=FP_A,
        target_stage_definition_id=target_stage,
        target_stage_fingerprint=FP_B,
        templates=(
            LegalWorkMaterializationTemplate(
                work_template_id="template-prepare",
                title=(
                    "Prepare governed filing "
                    + title_suffix
                ),
                due_rule=(
                    LegalOperationalDueRule.TRANSITION_OFFSET
                ),
                due_offset_seconds=3600,
                dependency_template_ids=(),
                condition_references=(),
            ),
            _template(
                "template-review",
                dependency_template_ids=(
                    "template-prepare",
                ),
            ),
        ),
        supersedes_fingerprint=supersedes,
    )


def _commit_create(
    context: _Context,
    value: LegalWorkMaterializationPolicy,
) -> LegalWorkMaterializationPolicy:
    with context.client.start_session() as session:
        with session.start_transaction():
            return context.registry.create_or_replay(
                value,
                session=session,
            )


def test_real_indexes_are_exact_unique_and_non_ttl(
    mongo_context: _Context,
) -> None:
    indexes = {
        entry["name"]: entry
        for entry in mongo_context.collection.list_indexes()
    }

    identity = indexes[
        "legal_work_materialization_policy_identity_unique"
    ]
    fingerprint = indexes[
        "legal_work_materialization_policy_fingerprint_unique"
    ]
    workflow_stage = indexes[
        "legal_work_materialization_policy_workflow_stage"
    ]

    assert identity["key"] == {
        "tenant_id": 1,
        "policy_id": 1,
        "policy_revision": 1,
    }
    assert identity["unique"] is True

    assert fingerprint["key"] == {
        "tenant_id": 1,
        "fingerprint": 1,
    }
    assert fingerprint["unique"] is True

    assert workflow_stage["key"] == {
        "tenant_id": 1,
        "workflow_definition_id": 1,
        "target_stage_definition_id": 1,
    }
    assert workflow_stage.get("unique") is not True

    assert all(
        "expireAfterSeconds" not in entry
        for entry in indexes.values()
    )


def test_real_exact_replay_and_two_revision_history(
    mongo_context: _Context,
) -> None:
    first = _policy()

    assert _commit_create(
        mongo_context,
        first,
    ) == first

    assert _commit_create(
        mongo_context,
        first,
    ) == first

    second = _policy(
        revision=2,
        supersedes=first.fingerprint,
        title_suffix="revision-two",
    )

    assert _commit_create(
        mongo_context,
        second,
    ) == second

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            history = mongo_context.registry.get_history(
                "tenant-law",
                "policy-filing",
                session=session,
            )

            latest = mongo_context.registry.get_latest(
                "tenant-law",
                "policy-filing",
                session=session,
            )

    assert tuple(
        value.policy_revision
        for value in history
    ) == (1, 2)

    assert history == (
        first,
        second,
    )
    assert latest == second

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": "tenant-law",
            "policy_id": "policy-filing",
        }
    ) == 2


def test_real_divergent_same_revision_rejects(
    mongo_context: _Context,
) -> None:
    original = _policy()
    _commit_create(
        mongo_context,
        original,
    )

    divergent = _policy(
        title_suffix="divergent",
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkMaterializationPolicyRegistryConflictError,
                match="DIVERGENT",
            ):
                mongo_context.registry.create_or_replay(
                    divergent,
                    session=session,
                )

            session.abort_transaction()

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": original.tenant_id,
            "policy_id": original.policy_id,
        }
    ) == 1


def test_real_revision_gap_and_wrong_predecessor_reject(
    mongo_context: _Context,
) -> None:
    first = _policy()
    _commit_create(
        mongo_context,
        first,
    )

    gap = _policy(
        revision=3,
        supersedes=first.fingerprint,
        title_suffix="gap",
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkMaterializationPolicyRegistryConflictError,
                match="REVISION",
            ):
                mongo_context.registry.create_or_replay(
                    gap,
                    session=session,
                )
            session.abort_transaction()

    wrong = _policy(
        revision=2,
        supersedes="c" * 128,
        title_suffix="wrong-predecessor",
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkMaterializationPolicyRegistryConflictError,
                match="SUPERSED",
            ):
                mongo_context.registry.create_or_replay(
                    wrong,
                    session=session,
                )
            session.abort_transaction()

    assert mongo_context.collection.count_documents(
        {}
    ) == 1


def test_real_cross_tenant_same_policy_identity_isolated(
    mongo_context: _Context,
) -> None:
    left = _policy(
        tenant="tenant-left",
    )
    right = _policy(
        tenant="tenant-right",
    )

    _commit_create(
        mongo_context,
        left,
    )
    _commit_create(
        mongo_context,
        right,
    )

    assert mongo_context.collection.count_documents(
        {
            "policy_id": "policy-filing",
            "policy_revision": 1,
        }
    ) == 2

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            assert mongo_context.registry.get_revision(
                "tenant-left",
                "policy-filing",
                1,
                session=session,
            ) == left

            assert mongo_context.registry.get_revision(
                "tenant-right",
                "policy-filing",
                1,
                session=session,
            ) == right


def test_real_caller_abort_rolls_back_insert(
    mongo_context: _Context,
) -> None:
    value = _policy(
        policy_id="policy-abort",
    )

    with mongo_context.client.start_session() as session:
        session.start_transaction()

        result = mongo_context.registry.create_or_replay(
            value,
            session=session,
        )

        assert result == value

        assert mongo_context.collection.count_documents(
            {
                "tenant_id": value.tenant_id,
                "policy_id": value.policy_id,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": value.tenant_id,
            "policy_id": value.policy_id,
        }
    ) == 0


def test_real_persisted_corruption_rejects_strictly(
    mongo_context: _Context,
) -> None:
    value = _policy(
        policy_id="policy-corrupt",
    )

    _commit_create(
        mongo_context,
        value,
    )

    mongo_context.collection.update_one(
        {
            "tenant_id": value.tenant_id,
            "policy_id": value.policy_id,
            "policy_revision": 1,
        },
        {
            "$set": {
                "fingerprint": "0" * 128,
            }
        },
    )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
            ):
                mongo_context.registry.get_revision(
                    value.tenant_id,
                    value.policy_id,
                    1,
                    session=session,
                )


def test_real_mongo_unique_identity_and_fingerprint_indexes_enforce(
    mongo_context: _Context,
) -> None:
    first = _policy(
        policy_id="policy-unique",
    )

    _commit_create(
        mongo_context,
        first,
    )

    raw = first.to_dict()

    duplicate_identity = dict(raw)
    duplicate_identity["fingerprint"] = "d" * 128

    with pytest.raises(DuplicateKeyError):
        mongo_context.collection.insert_one(
            duplicate_identity
        )

    duplicate_fingerprint = dict(raw)
    duplicate_fingerprint["policy_id"] = (
        "policy-other"
    )

    with pytest.raises(DuplicateKeyError):
        mongo_context.collection.insert_one(
            duplicate_fingerprint
        )


def test_real_stage_query_returns_exact_tenant_scope(
    mongo_context: _Context,
) -> None:
    filing = _policy(
        policy_id="policy-stage-filing",
        target_stage="stage-filing",
    )
    review = _policy(
        policy_id="policy-stage-review",
        target_stage="stage-review",
    )
    other = _policy(
        tenant="tenant-other",
        policy_id="policy-stage-other",
        target_stage="stage-filing",
    )

    for value in (
        filing,
        review,
        other,
    ):
        _commit_create(
            mongo_context,
            value,
        )

    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            values = (
                mongo_context.registry.list_workflow_stage(
                    "tenant-law",
                    "workflow-litigation",
                    "stage-filing",
                    session=session,
                )
            )

    assert values == (
        filing,
    )


def test_real_registry_has_no_ttl_or_mutable_current_document(
    mongo_context: _Context,
) -> None:
    indexes = tuple(
        mongo_context.collection.list_indexes()
    )

    assert all(
        "expireAfterSeconds" not in entry
        for entry in indexes
    )

    assert not hasattr(
        mongo_context.registry,
        "_current_collection",
    )

    assert mongo_context.database.list_collection_names() == [
        COLLECTION_NAME
    ]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_materialization_policy_registry_real_mongo.py
# VERSION: v1.0.0-P14-P10-WORK-MATERIALIZATION-POLICY-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo durability evidence only
# COMPETITIVE POSTURE: immutable stage-trigger/dependency/due-policy history
# CALLER TRANSACTION ROLLBACK: CERTIFIED
# TENANT ISOLATION: CERTIFIED
# EXACT REPLAY / REVISION LINEAGE: CERTIFIED
# TTL: ABSENT
# MUTABLE CURRENT POINTER: ABSENT
# WORK / ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# LEGAL-DEADLINE / NOTIFICATION / AI AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# PROTECTED MONGO 27027: FORBIDDEN
# END OF WILSY OS SOVEREIGN ARTIFACT
