"""TITLE: WILSY OS authenticated workforce directory and Overview HTTP certificate.
VERSION: v1.1.0-M03-WORKFORCE-OVERVIEW-CERT
AUTHORITY: WILSY OS Core Governance; regression evidence only.
EPITOME: Certifies exact-tenant, independently IAM-bound workforce directory and
         single-aggregation Overview, denied-before-read, and PII exclusion.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_workforce_directory_router.py
COLLABORATION / OWNERSHIP: Canonical Python EOS workforce router and its tests.
CERTIFICATION / UPDATE DATE: 2026-11-27.
CHANGELOG: v1.1.0-M03-WORKFORCE-OVERVIEW-CERT corrects the single-aggregation test contract and
           supplies institutional header and sovereign end seal.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic employees only; bank and identity
                             attributes must never appear in response.
TENANT BOUNDARY: Exact principal-derived tenant; hostile query/header never
                 influences authorized Mongo match.
AUTHORITY BOUNDARY: Tests override dependency for isolated route certification;
                    production route retains RequireTenantAuthorization.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS exclusively.
"""

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
        self.distinct_query: dict[str, Any] | None = None

    def count_documents(self, query: dict[str, Any]) -> int:
        self.query = query
        return len(self.rows)

    def aggregate(self, pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        assert len(pipeline) == 2
        assert "$match" in pipeline[0] and "$group" in pipeline[1]
        self.distinct_query = pipeline[0]["$match"]
        return ([{"active_employees": len(self.rows),
                  "departments": list({row.get("employment", {}).get("department")
                                       for row in self.rows})}] if self.rows else [])

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


def test_overview_uses_same_exact_tenant_and_never_exposes_employee_pii(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection = _Collection([{
        "employeeId": "SYNTH-1", "displayName": "Synthetic Example",
        "employment": {"department": "Operations"},
        "financial": {"bankAccount": "NEVER-EXPOSE"},
        "identification": {"nationalId": "NEVER-EXPOSE"},
    }])
    response = _client(monkeypatch, _Database(collection)).get(
        "/api/hr/workforce/overview",
        params={"tenantId": "FOREIGN"},
        headers={"X-Tenant-ID": "FOREIGN"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == "WILSY-PEOPLE-WORKFORCE-OVERVIEW/V1"
    assert body["tenant_id"] == "WILSYTENANT-4CD2FZ4O"
    assert body["metrics"] == {"active_employees": 1, "departments": 1}
    assert body["source"] == "AUTHORISED_HR_EMPLOYEE_REGISTRY"
    # Overview now uses a single match/group aggregation; count_documents is
    # deliberately not called (that would read a second unsynchronized view).
    assert collection.query is None
    assert collection.distinct_query == {
        "tenantId": "WILSYTENANT-4CD2FZ4O",
        "isActive": True, "deletedAt": None,
    }
    assert "NEVER-EXPOSE" not in response.text
    assert "Synthetic Example" not in response.text


def test_overview_fails_closed_without_database(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _client(monkeypatch, None).get("/api/hr/workforce/overview")
    assert response.status_code == 503
    assert response.json()["detail"] == "Workforce overview source is unavailable."


def test_overview_denied_principal_cannot_read_employee_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastapi import HTTPException
    app = FastAPI()
    app.include_router(subject.router)
    app.dependency_overrides[subject._DIRECTORY_AUTHORITY] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="HR_READ_DENIED")
    )
    monkeypatch.setattr(
        subject, "get_database",
        lambda: (_ for _ in ()).throw(AssertionError("Unauthorized database access")),
    )
    response = TestClient(app).get("/api/hr/workforce/overview")
    assert response.status_code == 403
    assert response.json() == {"detail": "HR_READ_DENIED"}


# ARTIFACT: tests/unit/test_hr_workforce_directory_router.py
# VERSION: v1.1.0-M03-WORKFORCE-OVERVIEW-CERT
# AUTHORITY BOUNDARY: Regression tests cannot grant HR or tenant IAM authority.
# TENANT POSTURE: Synthetic exact-tenant cases and explicit cross-scope denial.
# FAIL-CLOSED POSTURE: Missing source and denied authorization never return employee counts.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
