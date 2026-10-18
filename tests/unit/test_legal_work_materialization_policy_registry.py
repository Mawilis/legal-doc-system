"""
WILSY OS — Legal Work-Materialization Policy Registry Certificate

VERSION: v1.0.0-P14-P9A-WORK-MATERIALIZATION-POLICY-REGISTRY-RED-CERT

PURPOSE:
    Freeze the immutable durable-registry contract for versioned
    LegalWorkMaterializationPolicy truth before production registry authoring.

DURABILITY:
    - tenant-first immutable revision history;
    - caller-owned active transaction required;
    - exact replay;
    - divergent replay rejection;
    - strict hydration;
    - no TTL;
    - no update / replace / delete;
    - no mutable current pointer;
    - current/latest truth may only be derived from immutable history.

AUTHORITY:
    Persistence and read projection only. No work-item creation, assignment,
    supervision, IAM, professional, legal-deadline, notification-delivery,
    AI-execution or financial authority.

COMPETITIVE POSTURE:
    Preserves durable stage-trigger policy history, dependency-template rules,
    relative operational due rules and deterministic stage re-entry semantics
    with immutable provenance.
"""

from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_work_materialization_policy import (
    LegalOperationalDueRule,
    LegalWorkMaterializationPolicy,
    LegalWorkMaterializationTemplate,
)
from tools.eos.legal_operations.registry.legal_work_materialization_policy_registry import (
    COLLECTION_NAME,
    LegalWorkMaterializationPolicyRegistry,
    LegalWorkMaterializationPolicyRegistryConflictError,
    LegalWorkMaterializationPolicyRegistryNotFoundError,
    LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
    LegalWorkMaterializationPolicyRegistryRetryTransactionError,
    LegalWorkMaterializationPolicyRegistryTransactionRequiredError,
)


FP_A = "a" * 128
FP_B = "b" * 128


class _Result:
    inserted_id = "mongo-id"


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, dict[str, Any]]] = []

    def create_index(
        self,
        keys: Any,
        **kwargs: Any,
    ) -> str:
        self.indexes.append((keys, kwargs))
        return kwargs.get("name", "index")

    def insert_one(
        self,
        value: dict[str, Any],
        *,
        session: object,
    ) -> _Result:
        self.rows.append(deepcopy(value))
        return _Result()

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> dict[str, Any] | None:
        for row in self.rows:
            if all(row.get(key) == expected for key, expected in query.items()):
                return deepcopy(row)
        return None

    def find(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> list[dict[str, Any]]:
        rows = [
            deepcopy(row)
            for row in self.rows
            if all(row.get(key) == expected for key, expected in query.items())
        ]
        return rows


def _session(active: bool = True) -> SimpleNamespace:
    return SimpleNamespace(in_transaction=active)


def _template(
    template_id: str = "template-prepare",
) -> LegalWorkMaterializationTemplate:
    return LegalWorkMaterializationTemplate(
        work_template_id=template_id,
        title="Prepare governed filing",
        due_rule=LegalOperationalDueRule.TRANSITION_OFFSET,
        due_offset_seconds=3600,
        dependency_template_ids=(),
        condition_references=(),
    )


def _policy(
    *,
    tenant_id: str = "tenant-law",
    policy_id: str = "policy-filing",
    revision: int = 1,
    target_stage: str = "stage-filing",
    supersedes: str | None = None,
) -> LegalWorkMaterializationPolicy:
    return LegalWorkMaterializationPolicy(
        tenant_id=tenant_id,
        policy_id=policy_id,
        policy_revision=revision,
        workflow_definition_id="workflow-litigation",
        workflow_definition_fingerprint=FP_A,
        target_stage_definition_id=target_stage,
        target_stage_fingerprint=FP_B,
        templates=(_template(),),
        supersedes_fingerprint=supersedes,
    )


def test_collection_name_is_exact() -> None:
    assert COLLECTION_NAME == "legal_work_materialization_policies"


def test_indexes_are_tenant_first_non_ttl_and_exact() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    registry.ensure_indexes()

    by_name = {
        kwargs["name"]: (keys, kwargs)
        for keys, kwargs in collection.indexes
    }

    identity_keys, identity = by_name[
        "legal_work_materialization_policy_identity_unique"
    ]
    fingerprint_keys, fingerprint = by_name[
        "legal_work_materialization_policy_fingerprint_unique"
    ]
    stage_keys, stage = by_name[
        "legal_work_materialization_policy_workflow_stage"
    ]

    assert identity_keys == [
        ("tenant_id", 1),
        ("policy_id", 1),
        ("policy_revision", 1),
    ]
    assert identity["unique"] is True

    assert fingerprint_keys == [
        ("tenant_id", 1),
        ("fingerprint", 1),
    ]
    assert fingerprint["unique"] is True

    assert stage_keys == [
        ("tenant_id", 1),
        ("workflow_definition_id", 1),
        ("target_stage_definition_id", 1),
    ]
    assert stage.get("unique") is not True

    for _, kwargs in collection.indexes:
        assert "expireAfterSeconds" not in kwargs


def test_active_caller_transaction_is_required() -> None:
    registry = LegalWorkMaterializationPolicyRegistry(_Collection())

    with pytest.raises(
        LegalWorkMaterializationPolicyRegistryTransactionRequiredError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _policy(),
            session=_session(False),
        )


def test_first_revision_creates_and_exact_replay_returns_same_truth() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    value = _policy()

    created = registry.create_or_replay(
        value,
        session=_session(),
    )
    replay = registry.create_or_replay(
        value,
        session=_session(),
    )

    assert created == value
    assert replay == value
    assert len(collection.rows) == 1


def test_divergent_same_identity_replay_fails_closed() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    original = _policy()
    registry.create_or_replay(
        original,
        session=_session(),
    )

    divergent = LegalWorkMaterializationPolicy(
        tenant_id=original.tenant_id,
        policy_id=original.policy_id,
        policy_revision=original.policy_revision,
        workflow_definition_id=original.workflow_definition_id,
        workflow_definition_fingerprint=original.workflow_definition_fingerprint,
        target_stage_definition_id=original.target_stage_definition_id,
        target_stage_fingerprint=original.target_stage_fingerprint,
        templates=(
            LegalWorkMaterializationTemplate(
                work_template_id="template-other",
                title="Different materialization semantics",
                due_rule=LegalOperationalDueRule.NONE,
                due_offset_seconds=None,
                dependency_template_ids=(),
                condition_references=(),
            ),
        ),
        supersedes_fingerprint=None,
    )

    with pytest.raises(
        LegalWorkMaterializationPolicyRegistryConflictError,
        match="DIVERGENT",
    ):
        registry.create_or_replay(
            divergent,
            session=_session(),
        )


def test_revision_two_requires_exact_previous_revision_fingerprint() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    first = _policy()
    registry.create_or_replay(
        first,
        session=_session(),
    )

    second = _policy(
        revision=2,
        supersedes=first.fingerprint,
    )

    assert registry.create_or_replay(
        second,
        session=_session(),
    ) == second


def test_revision_gap_rejects() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    first = _policy()
    registry.create_or_replay(
        first,
        session=_session(),
    )

    with pytest.raises(
        LegalWorkMaterializationPolicyRegistryConflictError,
        match="REVISION",
    ):
        registry.create_or_replay(
            _policy(
                revision=3,
                supersedes=first.fingerprint,
            ),
            session=_session(),
        )


def test_revision_two_requires_supersedes_fingerprint() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    first = _policy()
    registry.create_or_replay(
        first,
        session=_session(),
    )

    with pytest.raises(
        LegalWorkMaterializationPolicyRegistryConflictError,
        match="SUPERSED",
    ):
        registry.create_or_replay(
            _policy(
                revision=2,
                supersedes=None,
            ),
            session=_session(),
        )


def test_revision_two_rejects_wrong_predecessor_fingerprint() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    first = _policy()
    registry.create_or_replay(
        first,
        session=_session(),
    )

    with pytest.raises(
        LegalWorkMaterializationPolicyRegistryConflictError,
        match="SUPERSED",
    ):
        registry.create_or_replay(
            _policy(
                revision=2,
                supersedes="c" * 128,
            ),
            session=_session(),
        )


def test_first_revision_forbids_supersedes_fingerprint() -> None:
    registry = LegalWorkMaterializationPolicyRegistry(_Collection())

    with pytest.raises(
        LegalWorkMaterializationPolicyRegistryConflictError,
        match="FIRST_REVISION",
    ):
        registry.create_or_replay(
            _policy(
                revision=1,
                supersedes="c" * 128,
            ),
            session=_session(),
        )


def test_get_revision_is_tenant_isolated() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    left = _policy(tenant_id="tenant-left")
    right = _policy(tenant_id="tenant-right")

    registry.create_or_replay(left, session=_session())
    registry.create_or_replay(right, session=_session())

    assert registry.get_revision(
        "tenant-left",
        "policy-filing",
        1,
        session=_session(),
    ) == left

    assert registry.get_revision(
        "tenant-right",
        "policy-filing",
        1,
        session=_session(),
    ) == right


def test_missing_revision_raises_typed_not_found() -> None:
    registry = LegalWorkMaterializationPolicyRegistry(_Collection())

    with pytest.raises(
        LegalWorkMaterializationPolicyRegistryNotFoundError,
    ):
        registry.get_revision(
            "tenant-law",
            "policy-filing",
            1,
            session=_session(),
        )


def test_history_is_revision_ordered_and_immutable() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    first = _policy()
    second = _policy(
        revision=2,
        supersedes=first.fingerprint,
    )

    registry.create_or_replay(first, session=_session())
    registry.create_or_replay(second, session=_session())

    history = registry.get_history(
        "tenant-law",
        "policy-filing",
        session=_session(),
    )

    assert tuple(
        item.policy_revision
        for item in history
    ) == (1, 2)

    assert history[0] == first
    assert history[1] == second


def test_latest_is_derived_from_history_not_current_pointer() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    first = _policy()
    second = _policy(
        revision=2,
        supersedes=first.fingerprint,
    )

    registry.create_or_replay(first, session=_session())
    registry.create_or_replay(second, session=_session())

    assert registry.get_latest(
        "tenant-law",
        "policy-filing",
        session=_session(),
    ) == second

    assert not hasattr(registry, "_current_collection")


def test_list_workflow_is_tenant_scoped() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    one = _policy(
        policy_id="policy-a",
    )
    two = _policy(
        policy_id="policy-b",
        target_stage="stage-review",
    )
    other = _policy(
        tenant_id="tenant-other",
        policy_id="policy-c",
    )

    for value in (one, two, other):
        registry.create_or_replay(
            value,
            session=_session(),
        )

    values = registry.list_workflow(
        "tenant-law",
        "workflow-litigation",
        session=_session(),
    )

    assert {
        item.policy_id
        for item in values
    } == {
        "policy-a",
        "policy-b",
    }


def test_list_workflow_stage_is_exact_and_tenant_scoped() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    filing = _policy(
        policy_id="policy-filing-a",
        target_stage="stage-filing",
    )
    review = _policy(
        policy_id="policy-review",
        target_stage="stage-review",
    )

    registry.create_or_replay(filing, session=_session())
    registry.create_or_replay(review, session=_session())

    values = registry.list_workflow_stage(
        "tenant-law",
        "workflow-litigation",
        "stage-filing",
        session=_session(),
    )

    assert values == (filing,)


def test_persisted_corruption_rejects_strictly() -> None:
    collection = _Collection()
    registry = LegalWorkMaterializationPolicyRegistry(collection)

    value = _policy()
    registry.create_or_replay(
        value,
        session=_session(),
    )

    collection.rows[0]["fingerprint"] = "0" * 128

    with pytest.raises(
        LegalWorkMaterializationPolicyRegistryPersistedRecordInvalidError,
    ):
        registry.get_revision(
            "tenant-law",
            "policy-filing",
            1,
            session=_session(),
        )


def test_registry_exposes_no_mutating_current_pointer_or_delete_surface() -> None:
    forbidden = {
        "update",
        "replace",
        "delete",
        "set_current",
        "update_current",
        "delete_current",
        "upsert",
    }

    methods = {
        name
        for name in dir(LegalWorkMaterializationPolicyRegistry)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(methods)


def test_registry_does_not_gain_operational_authority() -> None:
    forbidden = {
        "assign",
        "supervise",
        "authorize",
        "notify",
        "dispatch",
        "execute_ai",
        "pay",
        "settle",
        "invoice",
        "create_work_item",
    }

    methods = {
        name
        for name in dir(LegalWorkMaterializationPolicyRegistry)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(methods)


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_materialization_policy_registry.py
# VERSION: v1.0.0-P14-P9A-WORK-MATERIALIZATION-POLICY-REGISTRY-RED-CERT
# AUTHORITY BOUNDARY: persistence/read registry contract certificate only
# IMMUTABLE REVISION HISTORY: REQUIRED
# EXACT REPLAY: REQUIRED
# CURRENT POINTER: FORBIDDEN
# TTL / UPDATE / REPLACE / DELETE: FORBIDDEN
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# LEGAL-DEADLINE / NOTIFICATION / AI AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
