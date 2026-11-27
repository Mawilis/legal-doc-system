"""TITLE: WILSY OS Founder HR IAM Read-Only Preflight Certificate
VERSION: v1.0.0-FOUNDER-HR-PREFLIGHT-UNIT-CERT
AUTHORITY: Synthetic unit only; never mutates IAM or employee records.
TENANT BOUNDARY: Exact canonical company employer.
FAIL-CLOSED: A capacity alone, grant alone or Founder label alone is insufficient.
FINANCIAL EXECUTION: Kennel EOS exclusively.
"""
from __future__ import annotations

import json
from typing import Any

import pytest

from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID
from tools.eos.ops.founder_hr_iam_preflight import inspect_founder_hr_prerequisites


class _Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.max_count = 40

    def limit(self, limit: int) -> "_Cursor":
        self.max_count = limit
        return self

    def __iter__(self):
        return iter(self.rows[:self.max_count])


class _Collection:
    def __init__(self, name: str, records: list[dict[str, Any]]) -> None:
        self.name = name
        self.records = records

    def find(self, query: dict[str, object], projection: dict[str, int]) -> _Cursor:
        assert projection.get("_id") == 0
        return _Cursor([
            {key: value for key, value in doc.items() if projection.get(key)}
            for doc in self.records
            if all(doc.get(key) == value for key, value in query.items())
        ])

    def __getattr__(self, action: str):
        raise AssertionError(f"Unexpected IAM write: {action}")


class _Database:
    def __init__(self, rows: dict[str, list[dict[str, Any]]]) -> None:
        self.rows = rows
        self.read_collections: list[str] = []

    def __getitem__(self, collection: str) -> _Collection:
        self.read_collections.append(collection)
        assert collection != "employees"
        return _Collection(collection, self.rows.get(collection, []))


def _source(*, manager_capacity=False, manager_grant=False,
            director_capacity=False, director_grant=False) -> _Database:
    principal = "principal-synthetic"
    common = {"tenant_id": WILSY_COMPANY_TENANT_ID, "principal_id": principal}
    return _Database({
        "institutional_principal_designations": [{
            **common, "designation": "Founder", "business_role": "tenant_owner",
            "state": "ACTIVE", "grants_permissions": False,
        }],
        "tenant_memberships": [{**common, "status": "ACTIVE"}],
        "tenant_business_roles": [{**common, "status": "ACTIVE", "business_role": "tenant_owner"}],
        "tenant_business_role_assignments": [
            *([{**common, "status": "ACTIVE", "business_role": "tenant_hr_manager"}] if manager_capacity else []),
            *([{**common, "status": "ACTIVE", "business_role": "tenant_hr_director"}] if director_capacity else []),
        ],
        "role_assignments": [
            {**common, "status": "ACTIVE", "role_id": "ENTERPRISE_ADMIN"},
            *([{**common, "status": "ACTIVE", "role_id": "HR_MANAGER"}] if manager_grant else []),
            *([{**common, "status": "ACTIVE", "role_id": "HR_DIRECTOR"}] if director_grant else []),
            {"tenant_id": WILSY_COMPANY_TENANT_ID, "principal_id": "foreign-principal",
             "status": "ACTIVE", "role_id": "HR_MANAGER"},
        ],
    })


@pytest.mark.parametrize("manager_capacity,manager_grant", [
    (False, False), (True, False), (False, True),
])
def test_founder_owner_is_not_automatically_hr_authorized(
    manager_capacity: bool, manager_grant: bool,
) -> None:
    db = _source(manager_capacity=manager_capacity, manager_grant=manager_grant)
    report = inspect_founder_hr_prerequisites(db, WILSY_COMPANY_TENANT_ID)
    assert report["founder_designation_active"] is True
    assert report["tenant_owner_capacity_active"] is True
    assert report["enterprise_admin_role_active"] is True
    assert report["employer_hr_read_prerequisites_present"] is False
    assert report["status"] == "GOVERNED_HR_IAM_ISSUANCE_REQUIRED"
    assert report["hr_access_verified"] is False
    assert report["database_mutated"] is False
    rendered = json.dumps(report)
    assert "principal-synthetic" not in rendered
    assert "foreign-principal" not in rendered
    assert "employees" not in db.read_collections


@pytest.mark.parametrize("manager,director", [(True, False), (False, True)])
def test_matching_active_business_capacity_and_role_still_require_live_http(
    manager: bool, director: bool,
) -> None:
    db = _source(manager_capacity=manager, manager_grant=manager,
                 director_capacity=director, director_grant=director)
    report = inspect_founder_hr_prerequisites(db, WILSY_COMPANY_TENANT_ID)
    assert report["employer_hr_read_prerequisites_present"] is True
    assert report["status"] == "AUTHENTICATED_EOS_HTTP_VERIFICATION_REQUIRED"
    assert report["hr_access_verified"] is False
    assert report["database_mutated"] is False


def test_only_canonical_employer_scope_allowed() -> None:
    db = _source()
    with pytest.raises(ValueError, match="TENANT_NOT_CANONICAL"):
        inspect_founder_hr_prerequisites(db, "other-tenant")
    assert db.read_collections == []


def test_nonunique_founder_fails_closed_before_iam_resolution() -> None:
    db = _source()
    db.rows["institutional_principal_designations"].append(
        dict(db.rows["institutional_principal_designations"][0])
    )
    report = inspect_founder_hr_prerequisites(db, WILSY_COMPANY_TENANT_ID)
    assert report["status"] == "FOUNDER_DESIGNATION_NOT_UNIQUELY_VERIFIED"
    assert report["database_mutated"] is False
    assert db.read_collections == ["institutional_principal_designations"]


# ARTIFACT: tests/unit/test_founder_hr_iam_preflight.py
# VERSION: v1.0.0-FOUNDER-HR-PREFLIGHT-UNIT-CERT
# AUTHORITY BOUNDARY: Unit-only IAM read preflight; never issues any role.
# TENANT POSTURE: Exact canonical Founder employer.
# FAIL-CLOSED POSTURE: Partial evidence never reports activated HR access.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
