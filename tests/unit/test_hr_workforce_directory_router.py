"""TITLE: WILSY OS authenticated workforce directory and Overview HTTP certificate.
VERSION: v1.4.1-CONFIDENTIAL-ORGANIZATION-READ-CERT
AUTHORITY: WILSY OS Core Governance; regression evidence only.
EPITOME: Certifies exact-tenant, independently IAM-bound workforce directory and
         single-aggregation Overview, denied-before-read, and PII exclusion.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_workforce_directory_router.py
COLLABORATION / OWNERSHIP: Canonical Python EOS workforce router and its tests.
CERTIFICATION / UPDATE DATE: 2026-11-27.
CHANGELOG: v1.4.1-CONFIDENTIAL-ORGANIZATION-READ-CERT overrides independent proposal-read IAM only in the scoped transaction double; no directory-read shortcut is added to production.
CHANGELOG: v1.4.1-CONFIDENTIAL-ORGANIZATION-READ-CERT certifies no-permission-before-database, exact-tenant draft creation, replay-fingerprint denial, independent checker, unapproved-parent rejection and source-owned position records using deterministic transaction doubles.
CHANGELOG: v1.4.1-CONFIDENTIAL-ORGANIZATION-READ-CERT certifies bounded, PII-free exact-tenant observed department distribution and source-unavailable failure, without asserting approved organization authority.
CHANGELOG: v1.4.1-CONFIDENTIAL-ORGANIZATION-READ-CERT asserts a whitespace-only search never reaches Mongo; maintains exact-tenant single-detail, projection and absent-record certificates.
CHANGELOG: v1.2.0-M03-WORKFORCE-DETAIL-CERT verifies the separate authorized single employee directory read, protected-field exclusion, exact-tenant query and indistinguishable absent/foreign status.
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

    def find_one(self, query: dict[str, Any], projection: dict[str, int]) -> dict[str, Any] | None:
        self.query = query
        self.projection = projection
        for row in self.rows:
            if row.get("employeeId") == query.get("employeeId"):
                return row
        return None

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


def test_directory_rejects_whitespace_search_without_a_database_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A whitespace-only query must not silently become a full-directory scan."""
    collection = _Collection([])
    response = _client(monkeypatch, _Database(collection)).get(
        "/api/hr/workforce", params={"q": "   "},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "WORKFORCE_SEARCH_QUERY_INVALID"
    assert collection.query is None


def test_workforce_detail_is_exact_tenant_and_directory_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Detail uses existing IAM dependency and never serializes protected files."""
    collection = _Collection([{
        "employeeId": "EMP-1",
        "displayName": "Synthetic Worker",
        "employment": {
            "jobTitle": "Engineer", "department": "Operations",
            "managerId": "EMP-2", "status": "ACTIVE",
        },
        "contact": {"workEmail": "synthetic@example.invalid"},
        "financial": {"bankAccount": "HIDDEN"},
        "identification": {"nationalId": "HIDDEN"},
    }])
    response = _client(monkeypatch, _Database(collection)).get(
        "/api/hr/workforce/EMP-1",
        headers={"X-Tenant-ID": "UNTRUSTED-OTHER-TENANT"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == "WILSY-HR-WORKFORCE-DIRECTORY-DETAIL/V1"
    assert body["tenant_id"] == "WILSYTENANT-4CD2FZ4O"
    assert body["source"] == "AUTHORISED_HR_EMPLOYEE_REGISTRY"
    assert body["employee"]["employeeId"] == "EMP-1"
    assert body["employee"]["jobTitle"] == "Engineer"
    assert "financial" not in response.text
    assert "identification" not in response.text
    assert "HIDDEN" not in response.text
    assert collection.query == {
        "tenantId": "WILSYTENANT-4CD2FZ4O",
        "employeeId": "EMP-1", "isActive": True, "deletedAt": None,
    }
    assert collection.projection == subject._DIRECTORY_PROJECTION


def test_workforce_detail_not_found_is_opaque(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing employee identity and another tenant's absent identity are indistinguishable."""
    collection = _Collection([])
    response = _client(monkeypatch, _Database(collection)).get(
        "/api/hr/workforce/EMP-UNKNOWN",
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "WORKFORCE_EMPLOYEE_NOT_FOUND"
    assert collection.query["tenantId"] == "WILSYTENANT-4CD2FZ4O"


def test_workforce_detail_rejects_unsafe_identifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed IDs fail before any persistence operation."""
    collection = _Collection([])
    response = _client(monkeypatch, _Database(collection)).get(
        "/api/hr/workforce/EMP%20INVALID",
    )
    assert response.status_code == 422
    assert collection.query is None


def test_observed_workforce_organization_is_own_tenant_and_pii_free(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Organization is source-owned distribution, never approved positions."""
    class OrganizationCollection:
        def __init__(self) -> None:
            self.pipeline = None

        def aggregate(self, pipeline):
            self.pipeline = pipeline
            return [
                {"_id": "Engineering", "active_employees": 3},
                {"_id": "Operations", "active_employees": 2},
                {"_id": None, "active_employees": 1},
            ]

    collection = OrganizationCollection()
    response = _client(monkeypatch, _Database(collection)).get(
        "/api/hr/workforce/organization",
        headers={"X-Tenant-ID": "UNTRUSTED-TENANT"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "WILSYTENANT-4CD2FZ4O"
    assert body["status"] == "OBSERVED_EMPLOYEE_DISTRIBUTION"
    assert body["active_employees"] == 6
    assert body["department_count"] == 2
    assert body["unassigned_employees"] == 1
    assert body["departments"] == [
        {"name": "Engineering", "active_employees": 3},
        {"name": "Operations", "active_employees": 2},
    ]
    assert collection.pipeline[0]["$match"] == {
        "tenantId": "WILSYTENANT-4CD2FZ4O",
        "isActive": True,
        "deletedAt": None,
    }
    assert collection.pipeline[-1] == {"$limit": 201}
    assert "workEmail" not in response.text
    assert "bankAccount" not in response.text


def test_observed_workforce_organization_fails_closed_on_oversize(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An incomplete grouped distribution must never appear as verified."""
    class OversizedCollection:
        def aggregate(self, pipeline):
            return [
                {"_id": f"Department-{index}", "active_employees": 1}
                for index in range(201)
            ]

    response = _client(monkeypatch, _Database(OversizedCollection())).get(
        "/api/hr/workforce/organization"
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "WORKFORCE_ORGANIZATION_BOUND_EXCEEDED"


def test_observed_workforce_organization_requires_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unavailable database is never represented as a verified empty chart."""
    response = _client(monkeypatch, None).get("/api/hr/workforce/organization")
    assert response.status_code == 503
    assert response.json()["detail"] == "WORKFORCE_ORGANIZATION_SOURCE_UNAVAILABLE"



class _OrganizationDocumentStore:
    """Deterministic transaction double for proposed organization commands."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, bool]] = []

    def create_index(self, spec: Any, unique: bool = False) -> None:
        self.indexes.append((spec, unique))

    def find_one(self, query: dict[str, Any], session: Any = None) -> dict[str, Any] | None:
        return next((dict(row) for row in self.rows
                     if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, document: dict[str, Any], session: Any = None) -> None:
        self.rows.append(dict(document))

    def find_one_and_update(
        self, query: dict[str, Any], mutation: dict[str, Any],
        return_document: Any = None, session: Any = None,
    ) -> dict[str, Any] | None:
        row = next((value for value in self.rows
                    if all(value.get(k) == v for k, v in query.items())), None)
        if row is None:
            return None
        row.update(mutation.get("$set", {}))
        for field, count in mutation.get("$inc", {}).items():
            row[field] += count
        return dict(row)

    def find(self, query: dict[str, Any], projection: Any = None) -> _Cursor:
        return _Cursor([dict(row) for row in self.rows
                        if all(row.get(k) == v for k, v in query.items())])


class _OrganizationDatabase:
    def __init__(self) -> None:
        self.records = _OrganizationDocumentStore()
        self.events = _OrganizationDocumentStore()

    def get_collection(self, name: str, **_: Any) -> _OrganizationDocumentStore:
        return self.records if name == subject._ORG_COLLECTION else self.events


class _OrganizationSession:
    def __enter__(self) -> "_OrganizationSession":
        return self

    def __exit__(self, *_: Any) -> None:
        return None

    def with_transaction(self, callback: Any, **_: Any) -> Any:
        return callback(self)


class _OrganizationClient:
    def start_session(self) -> _OrganizationSession:
        return _OrganizationSession()


def _org_client(monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, _OrganizationDatabase, dict[str, str]]:
    """Override independent read, create and decide IAM only in these isolated tests."""
    store = _OrganizationDatabase()
    principal = {"identity_id": "HR-DIRECTOR"}
    app = FastAPI()
    app.include_router(subject.router)
    def authority() -> SimpleNamespace:
        return SimpleNamespace(
            tenant_id="WILSYTENANT-4CD2FZ4O",
            identity=SimpleNamespace(identity_id=principal["identity_id"]),
        )
    for dependency in (subject._DIRECTORY_AUTHORITY, subject._ORG_READ, subject._ORG_CREATE, subject._ORG_DECIDE):
        app.dependency_overrides[dependency] = authority
    monkeypatch.setattr(subject, "get_database", lambda: store)
    monkeypatch.setattr(subject, "get_client", lambda: _OrganizationClient())
    return TestClient(app), store, principal


def test_organization_department_and_position_require_independent_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Creator cannot approve and positions must reference approved departments."""
    client, db, actor = _org_client(monkeypatch)
    root = "/api/hr/workforce/structure"
    headers = {"Idempotency-Key": "create-dept-command-00001",
               "X-Tenant-ID": "FOREIGN-TENANT"}
    department = {
        "record_id": "DEP-OPERATIONS", "name": "Operations",
        "effective_from": "2026-12-01",
    }
    created = client.post(root + "/departments", json=department, headers=headers)
    assert created.status_code == 201
    assert created.json()["record"]["status"] == "DRAFT"
    assert created.json()["tenant_id"] == "WILSYTENANT-4CD2FZ4O"
    assert len(db.records.rows) == 1
    # Exact replay is durable and cannot create duplicate records/events.
    assert client.post(root + "/departments", json=department, headers=headers).json() == created.json()
    assert len(db.records.rows) == 1
    assert len(db.events.rows) == 1
    changed = client.post(root + "/departments", json={**department, "name": "Changed"},
                          headers=headers)
    assert changed.status_code == 409
    assert changed.json()["detail"] == "ORGANIZATION_IDEMPOTENCY_CONFLICT"

    position = {
        "record_id": "POS-OPERATIONS", "name": "Operations coordinator",
        "department_id": "DEP-OPERATIONS", "effective_from": "2026-12-01",
        "capacity": 3,
    }
    waiting = client.post(root + "/positions", json=position,
                          headers={"Idempotency-Key": "create-pos-command-00001"})
    assert waiting.status_code == 422
    assert waiting.json()["detail"] == "ORGANIZATION_PARENT_NOT_APPROVED"
    submitted = client.post(root + "/departments/DEP-OPERATIONS/submit",
                            json={"expected_revision": 1},
                            headers={"Idempotency-Key": "submit-dept-command-0001"})
    assert submitted.status_code == 200
    assert submitted.json()["record"]["revision"] == 2
    self_decision = client.post(
        root + "/departments/DEP-OPERATIONS/decision",
        json={"expected_revision": 2, "decision": "APPROVE", "reason": "Approved structure"},
        headers={"Idempotency-Key": "approve-dept-command-001"},
    )
    assert self_decision.status_code == 403
    assert self_decision.json()["detail"] == "ORGANIZATION_MAKER_CANNOT_APPROVE"
    actor["identity_id"] = "INDEPENDENT-CHECKER"
    approved = client.post(
        root + "/departments/DEP-OPERATIONS/decision",
        json={"expected_revision": 2, "decision": "APPROVE", "reason": "Approved structure"},
        headers={"Idempotency-Key": "approve-dept-command-001"},
    )
    assert approved.status_code == 200
    assert approved.json()["record"]["status"] == "APPROVED"
    actor["identity_id"] = "HR-DIRECTOR"
    created_position = client.post(root + "/positions", json=position,
        headers={"Idempotency-Key": "create-pos-command-00002"})
    assert created_position.status_code == 201
    assert created_position.json()["record"]["capacity"] == 3
    assert created_position.json()["record"]["status"] == "DRAFT"
    snapshot = client.get(root, headers={"X-Tenant-ID": "FOREIGN-TENANT"})
    assert snapshot.status_code == 200
    assert snapshot.json()["count"] == 2
    assert all(r["kind"] in ("DEPARTMENT","POSITION") for r in snapshot.json()["items"])
    assert all("created_by" not in r for r in snapshot.json()["items"])
    assert all(r["tenant_id"] == "WILSYTENANT-4CD2FZ4O" for r in db.records.rows)
    assert all(e["tenant_id"] == "WILSYTENANT-4CD2FZ4O" for e in db.events.rows)


def test_organization_write_permission_denies_before_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Organization creation is never inherited from directory-read IAM."""
    from fastapi import HTTPException
    app = FastAPI()
    app.include_router(subject.router)
    app.dependency_overrides[subject._ORG_CREATE] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="ORGANIZATION_PERMISSION_REQUIRED")
    )
    monkeypatch.setattr(subject, "get_database",
                        lambda: (_ for _ in ()).throw(AssertionError("No DB access allowed")))
    response = TestClient(app).post(
        "/api/hr/workforce/structure/departments",
        json={"record_id": "DEP-ONE", "name": "Example", "effective_from": "2026-12-01"},
        headers={"Idempotency-Key": "denied-org-command-001"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "ORGANIZATION_PERMISSION_REQUIRED"


# ARTIFACT: tests/unit/test_hr_workforce_directory_router.py
# VERSION: v1.4.1-CONFIDENTIAL-ORGANIZATION-READ-CERT
# AUTHORITY BOUNDARY: Regression tests cannot grant HR or tenant IAM authority.
# TENANT POSTURE: Synthetic exact-tenant cases and explicit cross-scope denial.
# FAIL-CLOSED POSTURE: Missing source and denied authorization never return employee counts.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
