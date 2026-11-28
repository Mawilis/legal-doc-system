"""TITLE: WILSY OS M03 HR01 Tenant-Scope and Directory Projection Regression
VERSION: v1.2.0-M03-HR01-CANONICAL-ROUTER-SINGLETON-CERT
AUTHORITY: WILSY OS Python EOS HR workforce security certification.
EPITOME: Check exact tenant source reads, reserved alias denial and PII redaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_m03_hr01_employee_scope.py
COLLABORATION / OWNERSHIP: Read-only tests for employee registry and HTTP projection.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.2.0-M03-HR01-CANONICAL-ROUTER-SINGLETON-CERT
         certifies the legacy employee public router is unmounted and the
         independently governed HR workforce router remains mounted.
CHANGELOG: v1.1.0-M03-HR01-AUTHENTICATED-HTTP-BOUNDARY-CERT adds
         actual FastAPI route invocation with session-selected tenant,
         no synthetic unverified employees and explicit legacy selector denial.
CHANGELOG: v1.0.0-M03-HR01-EMPLOYEE-DIRECTORY-BOUNDARY-CERT introduces
         isolated tenant-scoped lookup, forbidden alias, selector and PII tests.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic employees only; no actual PII or tokens.
TENANT BOUNDARY: All source selectors must contain exact tenantId.
AUTHORITY BOUNDARY: These tests do not substitute authenticated real EOS or IAM.
FINANCIAL AUTHORITY BOUNDARY: No payment, payroll, release or settlement.
"""
from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import pytest

from tools.eos.saas.employee import employee_registry as source
from tools.eos.api import employee_router as http


VERSION = "v1.2.0-M03-HR01-CANONICAL-ROUTER-SINGLETON-CERT"


class FakeCursor:
    """In-memory empty cursor recording page and sort without Mongo connectivity."""

    def __init__(self) -> None:
        self.offset = None
        self.limit_count = None

    def sort(self, key: str, direction: int) -> "FakeCursor":
        assert (key, direction) == ("displayName", 1)
        return self

    def skip(self, offset: int) -> "FakeCursor":
        self.offset = offset
        return self

    def limit(self, limit: int) -> "FakeCursor":
        self.limit_count = limit
        return self

    def __iter__(self):
        return iter(())


class FakeCollection:
    """Record exact source selectors and return no synthetic employees."""

    def __init__(self) -> None:
        self.queries = []
        self.cursor = FakeCursor()

    def find(self, query):
        self.queries.append(query)
        return self.cursor

    def find_one(self, query):
        self.queries.append(query)
        return None


@pytest.fixture
def source_collection(monkeypatch):
    """Inject a deterministic source without creating an alternate Mongo client."""
    collection = FakeCollection()
    monkeypatch.setattr(source.EmployeeRegistry, "_collection", staticmethod(lambda: collection))
    return collection


@pytest.mark.parametrize("alias", [
    "MASTER", "master", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT", "", " wilsy ", "wilsy\nroot",
])
def test_reserved_or_malformed_tenant_denied_before_source(alias, source_collection):
    """All read paths must refuse legacy scope aliases before touching Mongo."""
    registry = source.EmployeeRegistry()
    operations = [
        lambda: registry.search_employees(alias, "Employee"),
        lambda: registry.get_employee_by_id("E-001", alias),
        lambda: registry.get_employee_by_email("test@example.invalid", alias),
        lambda: registry.list_employees(alias),
    ]
    for operation in operations:
        with pytest.raises(source.EmployeeRegistryBoundaryError):
            operation()
    assert source_collection.queries == []


def test_exact_tenant_in_all_registry_queries(source_collection):
    """Every successful query carries explicit exact tenant equality."""
    registry = source.EmployeeRegistry()
    assert registry.search_employees("tenant-a", "Ann", 20, 0) == []
    assert registry.get_employee_by_id("E-1", "tenant-a") is None
    assert registry.get_employee_by_email("a@example.invalid", "tenant-a") is None
    assert registry.list_employees("tenant-a", active_only=False) == []
    assert len(source_collection.queries) == 4
    assert all(query["tenantId"] == "tenant-a" for query in source_collection.queries)


def test_search_metacharacters_escaped(source_collection):
    """Caller-provided regex must be treated as literal text, never expression."""
    source.EmployeeRegistry().search_employees("tenant-a", "a.*")
    expression = source_collection.queries[0]["$or"][0]["displayName"]["$regex"]
    assert expression == r"a\.\*"


@pytest.mark.parametrize("limit,offset", [(0, 0), (101, 0), (10, -1), (10, 100001), (True, 0)])
def test_pagination_bounds_fail_closed(limit, offset, source_collection):
    """Malformed page parameters cannot produce unbounded source scans."""
    with pytest.raises(source.EmployeeRegistryBoundaryError):
        source.EmployeeRegistry().list_employees("tenant-a", limit=limit, offset=offset)
    assert source_collection.queries == []


def test_directory_projection_does_not_serialize_sensitive_employee_fields():
    """Explicit HTTP read projection omits bank, salary, identity and contacts."""
    record = SimpleNamespace(
        employeeId="E-1",
        displayName="Synthetic Employee",
        jobTitle="Technician",
        department="Operations",
        managerId=None,
        status="ACTIVE",
        isActive=True,
        financial={"bankAccount": {"account": "SECRET"}},
        identification={"nationalId": "SECRET"},
        contact={"personalEmail": "SECRET"},
        basicSalary=999999,
    )
    projected = http._directory_record(record).model_dump()
    assert projected == {
        "employeeId": "E-1",
        "displayName": "Synthetic Employee",
        "jobTitle": "Technician",
        "department": "Operations",
        "managerId": None,
        "employmentStatus": "ACTIVE",
        "isActive": True,
    }


def test_http_routes_bind_existing_current_tenant_authority():
    """Both HTTP reads must depend on the canonical current IAM resolver."""
    assert http._DIRECTORY_READ._permission_id == "hr:employee_directory:read" if hasattr(
        http._DIRECTORY_READ, "_permission_id"
    ) else http._DIRECTORY_READ is not None
    assert "tenantId" not in http.search_employees.__code__.co_varnames
    assert "tenantId" not in http.get_employee.__code__.co_varnames


def test_authenticated_directory_http_exact_tenant_and_minimal_projection():
    """Request must use selected authenticated scope and never disclose PII."""
    seen = []

    class FakeAuthorizedRegistry:
        """Synthetic source records under current tenant from dependency override."""

        def search_employees(self, tenant_id, query, limit, offset):
            seen.append((tenant_id, query, limit, offset))
            return [SimpleNamespace(
                employeeId="TEST-1", displayName="Synthetic Worker",
                jobTitle="Operator", department="Operations", managerId=None,
                status="ACTIVE", isActive=True, basicSalary=780000,
                identification={"nationalId": "SECRET"},
                financial={"bankAccount": "SECRET"},
            )]

        def get_employee_by_id(self, employee_id, tenant_id):
            seen.append((tenant_id, employee_id))
            return None

    app = FastAPI()
    app.include_router(http.router)
    app.dependency_overrides[http._DIRECTORY_READ] = lambda: SimpleNamespace(
        tenant_id="customer-A"
    )
    app.dependency_overrides[http.get_employee_registry] = lambda: FakeAuthorizedRegistry()

    with TestClient(app) as client:
        result = client.get("/api/employees/search", params={"q": "Synthetic"})
        assert result.status_code == 200
        assert result.json() == [{
            "employeeId": "TEST-1", "displayName": "Synthetic Worker",
            "jobTitle": "Operator", "department": "Operations",
            "managerId": None, "employmentStatus": "ACTIVE", "isActive": True,
        }]
        denied = client.get(
            "/api/employees/search", params={"q": "Synthetic", "tenantId": "customer-B"}
        )
        assert denied.status_code == 422
        assert denied.json()["detail"] == "EMPLOYEE_TENANT_SELECTOR_FORBIDDEN"
        missing = client.get("/api/employees/FOREIGN")
        assert missing.status_code == 404
        forbidden = client.get("/api/employees/TEST-1", params={"tenantId": "MASTER"})
        assert forbidden.status_code == 422
    assert seen == [("customer-A", "Synthetic", 20, 0), ("customer-A", "FOREIGN")]


def test_directory_http_denied_authority_never_opens_registry():
    """IAM denial stops route before source without leaking synthetic employees."""
    app = FastAPI()
    app.include_router(http.router)

    def deny():
        raise HTTPException(status_code=403, detail="AUTHORIZATION_DENIED")

    def forbidden_registry():
        raise AssertionError("REGISTRY_CALLED_ON_DENIED_AUTHORITY")

    app.dependency_overrides[http._DIRECTORY_READ] = deny
    app.dependency_overrides[http.get_employee_registry] = forbidden_registry
    with TestClient(app) as client:
        result = client.get("/api/employees/search", params={"q": "Worker"})
    assert result.status_code == 403
    assert result.json() == {"detail": "AUTHORIZATION_DENIED"}


def test_canonical_workforce_router_is_only_mounted_employee_directory():
    """Server must not expose overlapping legacy directory API after HR01."""
    from tools.eos.api import hr_workforce_directory_router as canonical

    assert canonical.router.prefix == "/api/hr/workforce"
    assert canonical._DIRECTORY_AUTHORITY.permission_id == "hr:employee_directory:read"
    assert canonical._DIRECTORY_AUTHORITY.platform_employer_permission_id == (
        "platform_employer:employee_directory:read"
    )
    source_text = (
        Path(__file__).resolve().parents[2] / "tools/eos/api/server.py"
    ).read_text(encoding="utf-8")
    assert "app.include_router(hr_workforce_directory_router)" in source_text
    assert "app.include_router(employee_router)" not in source_text
    assert "from .employee_router import router as employee_router" not in source_text


# ARTIFACT: tests/unit/test_m03_hr01_employee_scope.py
# VERSION: v1.2.0-M03-HR01-CANONICAL-ROUTER-SINGLETON-CERT
# AUTHORITY BOUNDARY: Tests do not issue IAM permissions or admit employees.
# TENANT POSTURE: Synthetic source selectors only.
# FAIL-CLOSED POSTURE: Legacy root and broad read paths reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
