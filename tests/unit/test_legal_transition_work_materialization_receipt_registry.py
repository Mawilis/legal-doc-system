"""
WILSY OS — Transition Work Materialization Receipt Registry Certificate

VERSION:
    v1.0.0-P14-P14A-TRANSITION-WORK-MATERIALIZATION-RECEIPT-REGISTRY-RED-CERT

PURPOSE:
    Freeze immutable durable persistence semantics for transition-work
    materialization receipts before production registry authoring.

DURABILITY:
    - one exact receipt per tenant + transition;
    - tenant-first immutable receipt identity;
    - exact replay;
    - divergent replay rejection;
    - caller-owned active transaction;
    - strict persistence hydration;
    - no TTL;
    - no update / replace / delete;
    - no mutable current pointer.

AUTHORITY:
    Persistence and read projection only. No policy selection, work creation,
    assignment, supervision, IAM, legal-deadline, notification-delivery,
    AI-execution, billing, payment, settlement or financial authority.

COMPETITIVE POSTURE:
    Historical workflow automation cannot be reinterpreted by later mutable
    configuration because transition→policy→outputs are durably sealed.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

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


NOW = datetime(
    2026,
    10,
    16,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)

FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
FP_D = "d" * 128
FP_E = "e" * 128


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
        row = deepcopy(value)
        row["_id"] = f"fake-{len(self.rows) + 1}"
        self.rows.append(row)
        return _Result()

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> dict[str, Any] | None:
        for row in self.rows:
            if all(
                row.get(key) == expected
                for key, expected in query.items()
            ):
                return deepcopy(row)

        return None

    def find(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> list[dict[str, Any]]:
        return [
            deepcopy(row)
            for row in self.rows
            if all(
                row.get(key) == expected
                for key, expected in query.items()
            )
        ]


def _session(
    active: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(
        in_transaction=active
    )


def _output(
    *,
    work_item_id: str = "work-a",
    work_item_fingerprint: str = FP_C,
) -> LegalTransitionWorkMaterializationOutput:
    return LegalTransitionWorkMaterializationOutput(
        work_item_id=work_item_id,
        work_item_fingerprint=work_item_fingerprint,
    )


def _receipt(
    *,
    tenant_id: str = "tenant-law",
    case_matter_id: str = "matter-1",
    transition_id: str = "transition-1",
    transition_fingerprint: str = FP_A,
    policy_id: str = "policy-filing",
    policy_revision: int = 1,
    policy_fingerprint: str = FP_B,
    outputs: tuple[
        LegalTransitionWorkMaterializationOutput,
        ...,
    ] | None = None,
) -> LegalTransitionWorkMaterializationReceipt:
    return LegalTransitionWorkMaterializationReceipt(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        transition_id=transition_id,
        transition_fingerprint=transition_fingerprint,
        workflow_definition_id="workflow-litigation",
        target_stage_definition_id="stage-filing",
        policy_id=policy_id,
        policy_revision=policy_revision,
        policy_fingerprint=policy_fingerprint,
        outputs=outputs or (
            _output(),
        ),
        materialized_at=NOW,
    )


def test_collection_name_is_exact() -> None:
    assert COLLECTION_NAME == (
        "legal_transition_work_materialization_receipts"
    )


def test_indexes_are_tenant_first_exact_unique_and_non_ttl() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    by_name = {
        kwargs["name"]: (
            keys,
            kwargs,
        )
        for keys, kwargs in collection.indexes
    }

    receipt_keys, receipt = by_name[
        "legal_transition_work_materialization_receipt_identity_unique"
    ]
    transition_keys, transition = by_name[
        "legal_transition_work_materialization_receipt_transition_unique"
    ]
    fingerprint_keys, fingerprint = by_name[
        "legal_transition_work_materialization_receipt_fingerprint_unique"
    ]
    matter_keys, matter = by_name[
        "legal_transition_work_materialization_receipt_matter"
    ]
    policy_keys, policy = by_name[
        "legal_transition_work_materialization_receipt_policy"
    ]

    assert receipt_keys == [
        ("tenant_id", 1),
        ("receipt_id", 1),
    ]
    assert receipt["unique"] is True

    assert transition_keys == [
        ("tenant_id", 1),
        ("transition_id", 1),
    ]
    assert transition["unique"] is True

    assert fingerprint_keys == [
        ("tenant_id", 1),
        ("fingerprint", 1),
    ]
    assert fingerprint["unique"] is True

    assert matter_keys == [
        ("tenant_id", 1),
        ("case_matter_id", 1),
    ]
    assert matter.get("unique") is not True

    assert policy_keys == [
        ("tenant_id", 1),
        ("policy_id", 1),
        ("policy_revision", 1),
    ]
    assert policy.get("unique") is not True

    for _, kwargs in collection.indexes:
        assert "expireAfterSeconds" not in kwargs


def test_active_caller_transaction_is_required() -> None:
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            _Collection()
        )
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptRegistryTransactionRequiredError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _receipt(),
            session=_session(False),
        )


def test_create_and_exact_replay_preserve_same_truth() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    value = _receipt()

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


def test_fake_collection_models_mongo_id_without_weakening_domain() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    value = _receipt()

    created = registry.create_or_replay(
        value,
        session=_session(),
    )

    assert created == value
    assert "_id" in collection.rows[0]


def test_same_transition_cannot_bind_newer_policy_revision() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    original = _receipt()

    registry.create_or_replay(
        original,
        session=_session(),
    )

    newer = _receipt(
        policy_revision=2,
        policy_fingerprint=FP_D,
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptRegistryConflictError,
        match="DIVERGENT|TRANSITION",
    ):
        registry.create_or_replay(
            newer,
            session=_session(),
        )


def test_same_transition_cannot_bind_divergent_outputs() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    original = _receipt()

    registry.create_or_replay(
        original,
        session=_session(),
    )

    divergent = _receipt(
        outputs=(
            _output(
                work_item_id="work-b",
                work_item_fingerprint=FP_E,
            ),
        ),
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptRegistryConflictError,
        match="DIVERGENT|TRANSITION",
    ):
        registry.create_or_replay(
            divergent,
            session=_session(),
        )


def test_get_by_receipt_id_is_exact_and_tenant_scoped() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    left = _receipt(
        tenant_id="tenant-left",
    )
    right = _receipt(
        tenant_id="tenant-right",
    )

    registry.create_or_replay(
        left,
        session=_session(),
    )
    registry.create_or_replay(
        right,
        session=_session(),
    )

    assert registry.get_by_receipt_id(
        "tenant-left",
        left.receipt_id,
        session=_session(),
    ) == left

    assert registry.get_by_receipt_id(
        "tenant-right",
        right.receipt_id,
        session=_session(),
    ) == right


def test_get_by_transition_id_is_exact_and_tenant_scoped() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    left = _receipt(
        tenant_id="tenant-left",
        transition_id="transition-shared",
    )
    right = _receipt(
        tenant_id="tenant-right",
        transition_id="transition-shared",
    )

    registry.create_or_replay(
        left,
        session=_session(),
    )
    registry.create_or_replay(
        right,
        session=_session(),
    )

    assert registry.get_by_transition_id(
        "tenant-left",
        "transition-shared",
        session=_session(),
    ) == left

    assert registry.get_by_transition_id(
        "tenant-right",
        "transition-shared",
        session=_session(),
    ) == right


def test_missing_receipt_raises_typed_not_found() -> None:
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            _Collection()
        )
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptRegistryNotFoundError,
    ):
        registry.get_by_transition_id(
            "tenant-law",
            "transition-missing",
            session=_session(),
        )


def test_list_matter_is_tenant_scoped_and_deterministic() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    first = _receipt(
        transition_id="transition-1",
        transition_fingerprint=FP_A,
    )
    second = _receipt(
        transition_id="transition-2",
        transition_fingerprint=FP_D,
        policy_id="policy-review",
        policy_fingerprint=FP_E,
    )
    other = _receipt(
        tenant_id="tenant-other",
        transition_id="transition-3",
        transition_fingerprint=FP_D,
    )

    for value in (
        second,
        other,
        first,
    ):
        registry.create_or_replay(
            value,
            session=_session(),
        )

    values = registry.list_matter(
        "tenant-law",
        "matter-1",
        session=_session(),
    )

    assert {
        item.transition_id
        for item in values
    } == {
        "transition-1",
        "transition-2",
    }


def test_list_policy_revision_is_exact_and_tenant_scoped() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    first = _receipt(
        transition_id="transition-1",
    )
    second = _receipt(
        transition_id="transition-2",
        transition_fingerprint=FP_D,
    )
    other_policy = _receipt(
        transition_id="transition-3",
        transition_fingerprint=FP_E,
        policy_id="policy-other",
        policy_fingerprint=FP_D,
    )

    for value in (
        first,
        second,
        other_policy,
    ):
        registry.create_or_replay(
            value,
            session=_session(),
        )

    values = registry.list_policy_revision(
        "tenant-law",
        "policy-filing",
        1,
        session=_session(),
    )

    assert {
        item.transition_id
        for item in values
    } == {
        "transition-1",
        "transition-2",
    }


def test_persisted_corruption_rejects_strictly() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    value = _receipt()

    registry.create_or_replay(
        value,
        session=_session(),
    )

    collection.rows[0]["fingerprint"] = (
        "0" * 128
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError,
    ):
        registry.get_by_transition_id(
            value.tenant_id,
            value.transition_id,
            session=_session(),
        )


def test_unexpected_persisted_field_rejects_strictly() -> None:
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    value = _receipt()

    registry.create_or_replay(
        value,
        session=_session(),
    )

    collection.rows[0]["unexpected"] = True

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError,
    ):
        registry.get_by_transition_id(
            value.tenant_id,
            value.transition_id,
            session=_session(),
        )


def test_registry_has_no_mutable_or_authority_surfaces() -> None:
    methods = {
        name
        for name in dir(
            LegalTransitionWorkMaterializationReceiptRegistry
        )
        if not name.startswith("_")
    }

    forbidden = {
        "update",
        "replace",
        "delete",
        "upsert",
        "set_current",
        "resolve_policy",
        "select_policy",
        "create_work_item",
        "assign",
        "supervise",
        "authorize",
        "notify",
        "dispatch",
        "execute_ai",
        "invoice",
        "pay",
        "settle",
    }

    assert forbidden.isdisjoint(
        methods
    )


def test_competitive_replay_lock_is_explicit() -> None:
    """
    One tenant+transition may have exactly one immutable durable receipt.

    Later policy configuration and divergent output materialization cannot
    reinterpret or overwrite that historical transition.
    """
    collection = _Collection()
    registry = (
        LegalTransitionWorkMaterializationReceiptRegistry(
            collection
        )
    )

    original = _receipt()

    assert registry.create_or_replay(
        original,
        session=_session(),
    ) == original

    assert registry.create_or_replay(
        original,
        session=_session(),
    ) == original

    assert len(collection.rows) == 1


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_transition_work_materialization_receipt_registry.py
# VERSION: v1.0.0-P14-P14A-TRANSITION-WORK-MATERIALIZATION-RECEIPT-REGISTRY-RED-CERT
# AUTHORITY BOUNDARY: immutable receipt persistence/read contract only
# ONE TRANSITION / ONE RECEIPT: REQUIRED
# EXACT REPLAY: REQUIRED
# DIVERGENT OUTPUT / POLICY REPLAY: FORBIDDEN
# MONGO _id NORMALIZATION: persistence boundary only
# TTL / UPDATE / REPLACE / DELETE: FORBIDDEN
# POLICY SELECTION / WORK CREATION AUTHORITY: NONE
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# LEGAL-DEADLINE / NOTIFICATION / AI AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
