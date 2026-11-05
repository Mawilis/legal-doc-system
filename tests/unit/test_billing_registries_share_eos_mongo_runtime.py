"""Prove billing catalogue registries share the single EOS Mongo runtime.

No independent client, URI fallback, or registry-owned connection lifecycle is
permitted. Each registry resolves its named collection lazily from kernel.db.
"""
from __future__ import annotations

from typing import Any

from tools.eos.saas.billing import plan_registry, subscription_registry


class _Database:
    def __init__(self) -> None:
        self.requests: list[tuple[str, dict[str, Any]]] = []

    def get_collection(self, name: str, **kwargs: Any) -> object:
        self.requests.append((name, kwargs))
        return object()


def test_plan_and_subscription_registries_resolve_from_one_kernel_database(monkeypatch) -> None:
    database = _Database()
    monkeypatch.setattr(plan_registry, "get_database", lambda: database)
    monkeypatch.setattr(subscription_registry, "get_database", lambda: database)

    plan_registry.plans_collection.index_information()
    subscription_registry._collection().index_information()

    assert [name for name, _ in database.requests] == ["plans", "subscriptions"]
    assert all(options["write_concern"].document == {"w": "majority", "j": True}
               for _, options in database.requests)
    assert all(options["read_concern"].document == {"level": "majority"}
               for _, options in database.requests)


def test_registry_imports_do_not_construct_independent_mongo_clients() -> None:
    import inspect

    plan_source = inspect.getsource(plan_registry)
    subscription_source = inspect.getsource(subscription_registry)

    assert "MongoClient(" not in plan_source
    assert "MongoClient(" not in subscription_source
    assert "127.0.0.1:27017" not in plan_source
    assert "127.0.0.1:27017" not in subscription_source
    assert "get_database()" in plan_source
    assert "get_database()" in subscription_source
