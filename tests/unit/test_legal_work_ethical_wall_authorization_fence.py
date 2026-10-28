"""Unit contract tests for the G65 shared authorization fence."""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from tools.eos.legal_operations.service.legal_work_ethical_wall_authorization_fence import (
    CanonicalWallAuthorizationFence,
    FENCE_COLLECTION,
    FENCE_INDEX_FIELDS,
    FENCE_INDEX_NAME,
    WallFenceUnavailable,
)


@dataclass
class Session:
    in_transaction: bool = True


class Result:
    matched_count = 1
    upserted_id = None


class Collection:
    def __init__(self) -> None:
        self.documents: dict[tuple[str, str, str, str], dict[str, object]] = {}
        self.updates: list[dict[str, object]] = []

    @staticmethod
    def key(scope: dict[str, str]) -> tuple[str, str, str, str]:
        return (
            scope["tenant_id"], scope["case_matter_id"],
            scope["practitioner_principal_id"], scope["policy_id"],
        )

    def update_one(self, scope, update, *, upsert, session):
        assert upsert is True
        assert session.in_transaction is True
        self.updates.append(dict(scope))
        key = self.key(scope)
        current = self.documents.get(key)
        if current is None:
            current = {**scope, "epoch": 0, "schema_version": 1}
            self.documents[key] = current
        current["epoch"] = int(current["epoch"]) + int(update["$inc"]["epoch"])
        return Result()

    def find_one(self, scope, *, session):
        assert session.in_transaction is True
        value = self.documents.get(self.key(scope))
        return dict(value) if value else None


def scope(**overrides: str) -> dict[str, str]:
    value = {
        "tenant_id": "tenant-a",
        "case_matter_id": "matter-a",
        "practitioner_principal_id": "principal-a",
        "policy_id": "policy-a",
    }
    value.update(overrides)
    return value


def test_disclosure_and_revocation_share_the_same_scope_fence() -> None:
    collection = Collection()
    fence = CanonicalWallAuthorizationFence(collection)
    first = fence.contend(**scope(), session=Session())
    second = fence.contend(**scope(), session=Session())

    assert first.epoch == 1
    assert second.epoch == 2
    assert collection.updates == [scope(), scope()]
    assert len(collection.documents) == 1


def test_different_tenant_scopes_do_not_share_a_fence() -> None:
    collection = Collection()
    fence = CanonicalWallAuthorizationFence(collection)

    first = fence.contend(**scope(), session=Session())
    second = fence.contend(**scope(tenant_id="tenant-b"), session=Session())

    assert first.epoch == second.epoch == 1
    assert len(collection.documents) == 2


def test_fence_refuses_to_operate_outside_an_active_transaction() -> None:
    collection = Collection()
    fence = CanonicalWallAuthorizationFence(collection)

    with pytest.raises(WallFenceUnavailable):
        fence.contend(**scope(), session=Session(in_transaction=False))

    assert collection.updates == []


def test_fence_rejects_missing_or_wildcard_scope() -> None:
    collection = Collection()
    fence = CanonicalWallAuthorizationFence(collection)

    with pytest.raises(WallFenceUnavailable):
        fence.contend(**scope(tenant_id="global"), session=Session())
    with pytest.raises(WallFenceUnavailable):
        fence.contend(**scope(policy_id=""), session=Session())

    assert collection.updates == []


def test_index_provisioner_creates_unique_compound_index() -> None:
    class IndexCollection:
        def __init__(self) -> None:
            self.calls: list[tuple[list[tuple[str, int]], dict[str, object]]] = []

        def create_index(self, fields, **options):
            self.calls.append((fields, options))
            return options["name"]

    collection = IndexCollection()
    from tools.eos.legal_operations.service.legal_work_ethical_wall_authorization_fence import ensure_fence_index

    ensure_fence_index(collection)
    assert collection.calls == [(
        list(FENCE_INDEX_FIELDS),
        {"name": FENCE_INDEX_NAME, "unique": True},
    )]


def test_index_contract_is_unique_and_scope_complete() -> None:
    assert FENCE_COLLECTION == "legal_ethical_wall_authorization_fences"
    assert FENCE_INDEX_NAME == "uq_g65_wall_authorization_fence_scope"
    assert FENCE_INDEX_FIELDS == (
        ("tenant_id", 1),
        ("case_matter_id", 1),
        ("practitioner_principal_id", 1),
        ("policy_id", 1),
    )
