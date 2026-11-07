from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api import hr_workforce_directory_router as subject


class _Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def sort(self, value: Any) -> "_Cursor":
        return self

    def skip(self, value: int) -> "_Cursor":
        self.rows = self.rows[value:]
        return self

    def limit(self, value: int) -> "_Cursor":
        self.rows = self.rows[:value]
        return self

    def __iter__(self):
        return iter(self.rows)


class _Collection:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.query: dict[str, Any] | None = None
        self.projection: dict[str, int] | None = None

    def count_documents(self, query: dict[str, Any]) -> int:
        self.query = query
        return len(self.rows)

    def find(self, query: dict[str, Any], projection: dict[str, int]) -> _Cursor:
        self.query = query
        self.projection = projection
        return _Cursor(list(self.rows))


class _Database:
    def __init__(self, collection: _Collection) -> None:
        self.collection = collection

    def __getitem__(self, name: str) -> _Collection:
        assert name == "employees"
        return self.collection


def _client(monkeypatch: pytest.MonkeyPatch, database: object) -> TestClient:
    app = FastAPI()
    app.include_router(subject.router)
    app.dependency_overrides[subject._DIRECTORY_AUTHORITY] = lambda: SimpleNamespace(
        tenant_id="WILSYTENANT-4CD2FZ4O"
    )
    monkeypatch.setattr(subject, "get_database", lambda: database)
    return TestClient(app)


def test_directory_uses_authorised_tenant_and_only_directory_safe_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection = _Collection([{
        "employeeId": "EMP-1",
        "displayName": "Example Employee",
        "preferredName": "Example",
        "employment": {
            "jobTitle": "Engineer",
            "department": "Engineering",
            "managerId": "EMP-2",
            "status": "ACTIVE",
            "workLocation": "Remote",
        },
        "contact": {"workEmail": "example@example.invalid"},
        "financial": {"basicSalary": 999999, "bankAccount": {"number": "secret"}},
        "identification": {"nationalId": "secret"},
        "dateOfBirth": "2000-01-01",
    }])
    response = _client(monkeypatch, _Database(collection)).get(
        "/api/hr/workforce",
        params={"tenantId": "ATTACKER-TENANT", "q": "Example"},
        headers={"X-Tenant-ID": "ATTACKER-TENANT"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["employeeId"] == "EMP-1"
    assert body["items"][0]["workEmail"] == "example@example.invalid"
    assert "financial" not in body["items"][0]
    assert "identification" not in body["items"][0]
    assert collection.query["tenantId"] == "WILSYTENANT-4CD2FZ4O"
    assert collection.projection == subject._DIRECTORY_PROJECTION
    assert "financial" not in collection.projection
    assert "identification" not in collection.projection


def test_directory_fails_closed_when_hr_database_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = _client(monkeypatch, None).get("/api/hr/workforce")
    assert response.status_code == 503
    assert response.json()["detail"] == "Workforce directory source is unavailable."


def test_directory_search_escapes_regular_expression_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection = _Collection([])
    response = _client(monkeypatch, _Database(collection)).get(
        "/api/hr/workforce",
        params={"q": ".*"},
    )
    assert response.status_code == 200
    assert collection.query["$or"][0]["displayName"]["$regex"] == r"\.\*"
