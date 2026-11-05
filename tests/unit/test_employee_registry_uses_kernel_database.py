from __future__ import annotations

import inspect

import pytest

from tools.eos.saas.employee import employee_registry


class Cursor:
    def sort(self, *_args, **_kwargs):
        return self

    def skip(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def __iter__(self):
        return iter(())


class Collection:
    def __init__(self):
        self.find_queries = []
        self.find_one_queries = []

    def find(self, query):
        self.find_queries.append(query)
        return Cursor()

    def find_one(self, query):
        self.find_one_queries.append(query)
        return None


class Database:
    def __init__(self, collection):
        self.collection = collection
        self.lookups = []

    def __getitem__(self, name):
        self.lookups.append(name)
        assert name == "employees"
        return self.collection


def test_employee_registry_resolves_every_operation_from_kernel_database(monkeypatch):
    collection = Collection()
    database = Database(collection)
    calls = []

    def get_database():
        calls.append("kernel")
        return database

    monkeypatch.setattr(employee_registry, "get_database", get_database)
    registry = employee_registry.EmployeeRegistry()

    assert registry.search_employees("tenant-a", "wil") == []
    assert registry.get_employee_by_id("employee-1", "tenant-a") is None
    assert registry.get_employee_by_email("person@example.com", "tenant-a") is None
    assert registry.list_employees("tenant-a") == []

    assert calls == ["kernel"] * 4
    assert database.lookups == ["employees"] * 4
    assert len(collection.find_queries) == 2
    assert len(collection.find_one_queries) == 2
    assert all(query.get("tenantId") == "tenant-a" for query in (
        *collection.find_queries,
        *collection.find_one_queries,
    ))


def test_employee_registry_fails_closed_when_kernel_database_is_unavailable(monkeypatch):
    monkeypatch.setattr(employee_registry, "get_database", lambda: None)
    with pytest.raises(RuntimeError, match="EMPLOYEE_REGISTRY_DATABASE_UNAVAILABLE"):
        employee_registry.EmployeeRegistry().list_employees("tenant-a")


def test_employee_registry_has_no_private_mongo_connection_or_fallback():
    source = inspect.getsource(employee_registry)
    assert "MongoClient(" not in source
    assert "MONGODB_URI" not in source
    assert "MONGO_URI" not in source
    assert "127.0.0.1:27017" not in source
