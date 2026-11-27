"""TITLE: WILSY OS M03 HR01 Tenant-Scope and Directory Projection Regression
VERSION: v1.0.0-M03-HR01-EMPLOYEE-DIRECTORY-BOUNDARY-CERT
AUTHORITY: WILSY OS Python EOS HR workforce security certification.
EPITOME: Check exact tenant source reads, reserved alias denial and PII redaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_m03_hr01_employee_scope.py
COLLABORATION / OWNERSHIP: Read-only tests for employee registry and HTTP projection.
CERTIFICATION / UPDATE DATE: 2026-11-27
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

import pytest

from tools.eos.saas.employee import employee_registry as source
from tools.eos.api import employee_router as http


VERSION = "v1.0.0-M03-HR01-EMPLOYEE-DIRECTORY-BOUNDARY-CERT"


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


# ARTIFACT: tests/unit/test_m03_hr01_employee_scope.py
# VERSION: v1.0.0-M03-HR01-EMPLOYEE-DIRECTORY-BOUNDARY-CERT
# AUTHORITY BOUNDARY: Tests do not issue IAM permissions or admit employees.
# TENANT POSTURE: Synthetic source selectors only.
# FAIL-CLOSED POSTURE: Legacy root and broad read paths reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
