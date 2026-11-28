"""TITLE: WILSY OS Organization Governance Regression Certificate
VERSION: v1.0.0-M03-HR03-ORGANIZATION-LIFECYCLE-CERT
AUTHORITY: WILSY OS Core Governance
EPITOME: Synthetic exact-tenant and maker-checker, authorization and retirement impact contracts; no production records.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_organization_lifecycle_expansion.py
COLLABORATION / OWNERSHIP: WILSY OS HR Organization / Python EOS engineering
CERTIFICATION / UPDATE DATE: 2026-11-28
CHANGELOG: v1.0.0-M03-HR03-ORGANIZATION-LIFECYCLE-CERT adds governed source, consumer and evidence contracts without expanding IAM grants.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Bounded readback and event labels; no personnel/financial secrets, no fabricated external entity verification.
TENANT BOUNDARY: Exact authenticated EOS tenant; no root or Owner fallback.
AUTHORITY BOUNDARY: EOS source grants are separately required; maker and checker cannot be the same principal.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from tools.eos.api import hr_organization_lifecycle_router as lifecycle
from tools.eos.api import hr_organization_business_context_router as business
from tools.eos.api import hr_workforce_directory_router as org


def _identity(tenant="TENANT-SYNTHETIC-A", actor="HR-MAKER"):
    return SimpleNamespace(
        tenant_id=tenant,
        identity=SimpleNamespace(identity_id=actor),
    )


def _denied():
    raise HTTPException(status_code=403, detail="ORGANIZATION_PERMISSION_DENIED")


def test_expansion_routes_are_static_and_do_not_overlap_employee_detail():
    lifecycle_paths = [r.path for r in lifecycle.router.routes if hasattr(r, "path")]
    context_paths = [r.path for r in business.router.routes if hasattr(r, "path")]
    assert "/api/hr/workforce/structure/changes" in lifecycle_paths
    assert "/api/hr/workforce/structure/productivity" in lifecycle_paths
    assert "/api/hr/workforce/structure/context" in context_paths
    assert "/api/hr/workforce/structure/context/proposals" in context_paths
    assert all(path.startswith("/api/hr/workforce/structure/")
               for path in lifecycle_paths)
    assert all(path.startswith("/api/hr/workforce/structure/context")
               for path in context_paths)


def test_expansion_uses_independent_iam_before_any_persistence(monkeypatch):
    app = FastAPI()
    app.include_router(business.router)
    app.include_router(lifecycle.router)
    app.dependency_overrides[org._ORG_READ] = _denied
    app.dependency_overrides[org._ORG_CREATE] = _denied
    app.dependency_overrides[org._ORG_DECIDE] = _denied
    monkeypatch.setattr(lifecycle, "get_database",
                        lambda: (_ for _ in ()).throw(AssertionError("No database access")))
    monkeypatch.setattr(business, "get_database",
                        lambda: (_ for _ in ()).throw(AssertionError("No database access")))
    client = TestClient(app)
    for route in (
        "/api/hr/workforce/structure/changes",
        "/api/hr/workforce/structure/productivity",
        "/api/hr/workforce/structure/context",
        "/api/hr/workforce/structure/departments/DEP-X/impact",
        "/api/hr/workforce/structure/departments/DEP-X/history",
        "/api/hr/workforce/structure/departments/DEP-X/as-of?on=2026-11-01",
    ):
        response = client.get(route)
        assert response.status_code == 403, (route, response.text)
    headers = {"Idempotency-Key": "synthetic-command-key-0001"}
    denied_draft = client.post(
        "/api/hr/workforce/structure/context/proposals",
        json={"activity_ids": ["legal"], "reason": "Governed business classification"},
        headers=headers,
    )
    assert denied_draft.status_code == 403
    denied_change = client.post(
        "/api/hr/workforce/structure/departments/DEP-X/changes",
        json={"change_type": "RETIRE", "effective_from": "2026-12-01",
              "reason": "Department is closed"},
        headers=headers,
    )
    assert denied_change.status_code == 403


def test_business_profile_accepts_only_explicit_known_distinct_activity_ids(monkeypatch):
    monkeypatch.setattr(business, "_command",
                        lambda *args, **kwargs: (_ for _ in ()).throw(
                            AssertionError("Invalid activities cannot reach persistence")))
    auth = _identity()
    for ids in (["legal", "legal"], ["invented-industry"]):
        with pytest.raises(HTTPException) as caught:
            business.draft_business_activity_context(
                business.ActivityContextDraft(activity_ids=ids,
                                              reason="Five-word synthetic business reason"),
                key="business-context-key-0001", auth=auth,
            )
        assert caught.value.status_code == 422


class _Cursor:
    def __init__(self, rows):
        self.rows = list(rows)

    def sort(self, *args):
        return self

    def limit(self, count):
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class _Collection:
    def __init__(self, rows):
        self.rows = list(rows)
        self.queries = []

    def find_one(self, query, projection=None, **kwargs):
        self.queries.append(query)
        for row in self.rows:
            if all(row.get(k) == v for k, v in query.items()):
                return dict(row)
        return None

    def find(self, query, projection=None, **kwargs):
        self.queries.append(query)
        def match(row):
            return all(
                row.get(key) == value or (
                    key == "$or" and any(all(row.get(k) == v for k, v in option.items())
                                        for option in value)
                )
                for key, value in query.items()
            )
        return _Cursor([dict(row) for row in self.rows if match(row)])


class _Db:
    def __init__(self, collections):
        self.collections = collections

    def get_collection(self, name, **kwargs):
        return self.collections[name]


def test_business_context_does_not_infer_entity_or_activity_from_empty_authority(monkeypatch):
    current = _Collection([{
        "tenant_id": "FOREIGN-TENANT", "revision": 9, "activity_ids": ["financial"],
    }])
    proposals = _Collection([])
    db = _Db({business._CURRENT: current, business._PROPOSALS: proposals})
    monkeypatch.setattr(business, "get_database", lambda: db)
    answer = business.read_business_activity_context(_identity())
    assert answer["status"] == "UNCONFIGURED"
    assert answer["activity_ids"] == []
    assert answer["operating_entities"] == []
    assert answer["entity_status"] == "ENTITY_SOURCE_NOT_CONNECTED"
    assert answer["external_business_classification_verified"] is False
    assert current.queries[0] == {"tenant_id": "TENANT-SYNTHETIC-A"}


def test_retirement_impact_counts_approved_dependents_of_same_tenant():
    records = _Collection([
        {"tenant_id": "TENANT-SYNTHETIC-A", "kind": "POSITION",
         "record_id": "POS-ONE", "department_id": "DEP-OPS", "status": "APPROVED"},
        {"tenant_id": "TENANT-SYNTHETIC-A", "kind": "DEPARTMENT",
         "record_id": "DEP-CHILD", "parent_id": "DEP-OPS", "status": "APPROVED"},
        {"tenant_id": "FOREIGN-TENANT", "kind": "POSITION",
         "record_id": "POS-FOREIGN", "department_id": "DEP-OPS", "status": "APPROVED"},
    ])
    result = lifecycle._impact(records, "TENANT-SYNTHETIC-A", "DEP-OPS")
    assert result["retirement_blocked"] is True
    assert result["dependent_positions"] == ["POS-ONE"]
    assert result["dependent_departments"] == ["DEP-CHILD"]


def test_independent_checker_cannot_be_the_change_maker(monkeypatch):
    maker = _identity()
    row = {"tenant_id": maker.tenant_id, "record_id": "DEP-OPS",
           "change_id": "CHANGE-ONE", "created_by": maker.identity.identity_id,
           "submitted_by": maker.identity.identity_id, "status": "SUBMITTED",
           "revision": 2}
    class _Changes:
        def find_one(self, *args, **kwargs):
            return row
    def tx(callback, **kwargs):
        return callback(None, _Changes(), None, None, None)
    monkeypatch.setattr(lifecycle, "_run_command", tx)
    with pytest.raises(HTTPException) as denied:
        lifecycle.decide_department_change(
            "DEP-OPS", "CHANGE-ONE",
            lifecycle.ChangeDecision(expected_revision=2, decision="APPROVE",
                                     reason="Independently reviewed reasoning"),
            key="decision-key-000001", auth=maker,
        )
    assert denied.value.status_code == 403
    assert denied.value.detail == "ORGANIZATION_MAKER_CANNOT_APPROVE"


def test_business_context_checker_cannot_be_original_maker(monkeypatch):
    maker = _identity()
    row = {"tenant_id": maker.tenant_id, "created_by": maker.identity.identity_id,
           "submitted_by": maker.identity.identity_id,
           "status": "SUBMITTED", "revision": 2}
    class _Proposals:
        def find_one(self, *args, **kwargs):
            return row
    def action(callback, *args):
        return callback(_Proposals(), None, None)
    monkeypatch.setattr(business, "_command", action)
    with pytest.raises(HTTPException) as denied:
        business.decide_business_activity_context(
            "PROFILE-ONE",
            business.ContextDecision(expected_revision=2, decision="APPROVE",
                                     reason="Second principal approval"),
            key="decision-context-0001", auth=maker,
        )
    assert denied.value.status_code == 403
    assert denied.value.detail == "BUSINESS_CONTEXT_MAKER_CANNOT_APPROVE"


def test_business_context_effective_model_and_productivity_envelopes_are_explicit():
    data = business.ActivityContextDraft(activity_ids=["legal", "technology"],
                                         reason="Mixed legal and technology practice")
    assert data.activity_ids == ["legal", "technology"]
    report = lifecycle.ProductivityObservation(
        session_id="session_example_1234567", event="DRAFT_VERIFIED",
        count=1, elapsed_ms=12500,
    )
    assert report.elapsed_ms == 12500
    with pytest.raises(Exception):
        lifecycle.ProductivityObservation(
            session_id="session_example_1234567", event="DRAFT_VERIFIED",
            count=10000, elapsed_ms=12500,
        )


def test_hierarchy_reorganization_rejects_cycle_and_unknown_parents():
    records = _Collection([
        {"tenant_id": "TENANT-SYNTHETIC-A", "kind": "DEPARTMENT",
         "record_id": "DEP-CHILD", "parent_id": "DEP-ROOT", "status": "APPROVED"},
    ])
    current = {"record_id": "DEP-ROOT"}
    with pytest.raises(HTTPException) as cycle:
        lifecycle._check_hierarchy(
            records, current, {"parent_id": "DEP-CHILD"},
            "TENANT-SYNTHETIC-A", None,
        )
    assert cycle.value.detail == "ORGANIZATION_PARENT_CYCLE"
    with pytest.raises(HTTPException) as missing:
        lifecycle._check_hierarchy(
            records, current, {"parent_id": "DEP-UNKNOWN"},
            "TENANT-SYNTHETIC-A", None,
        )
    assert missing.value.detail == "ORGANIZATION_PARENT_NOT_APPROVED"
    lifecycle._check_hierarchy(
        records, current, {"clear_parent": True, "parent_id": None},
        "TENANT-SYNTHETIC-A", None,
    )


def test_bounded_as_of_read_cannot_show_a_future_version_or_another_tenant(monkeypatch):
    records = _Collection([
        {"tenant_id": "TENANT-SYNTHETIC-A", "kind": "DEPARTMENT",
         "record_id": "DEP-ROOT", "status": "APPROVED",
         "revision": 3, "name": "New Structure", "effective_from": "2026-12-01"},
    ])
    versions = _Collection([
        {"tenant_id": "TENANT-SYNTHETIC-A", "record_id": "DEP-ROOT",
         "revision": 1, "status": "APPROVED", "name": "Original",
         "effective_from": "2026-01-01", "parent_id": None},
        {"tenant_id": "TENANT-SYNTHETIC-A", "record_id": "DEP-ROOT",
         "revision": 3, "status": "APPROVED", "name": "New Structure",
         "effective_from": "2026-12-01", "parent_id": None},
        {"tenant_id": "FOREIGN-TENANT", "record_id": "DEP-ROOT",
         "revision": 4, "status": "RETIRED", "name": "Foreign",
         "effective_from": "2026-06-01", "parent_id": None},
    ])
    db = _Db({org._ORG_COLLECTION: records, lifecycle._VERSIONS: versions})
    monkeypatch.setattr(lifecycle, "get_database", lambda: db)
    snapshot = lifecycle.read_department_at_date(
        "DEP-ROOT", date(2026, 11, 28), auth=_identity(),
    )
    assert snapshot["record"]["name"] == "Original"
    assert snapshot["record"]["revision"] == 1
    assert snapshot["record"]["status"] == "APPROVED"
    with pytest.raises(HTTPException) as before:
        lifecycle.read_department_at_date(
            "DEP-ROOT", date(2025, 12, 31), auth=_identity(),
        )
    assert before.value.status_code == 404



def test_productivity_aggregates_client_metrics_without_a_200_event_ceiling(monkeypatch):
    class _Aggregated(_Collection):
        def aggregate(self, stages):
            assert stages[0] == {"$match": {"tenant_id": "TENANT-SYNTHETIC-A"}}
            return [
                {"_id": "FORM_OPENED", "count": 250, "samples": 250,
                 "mean_elapsed_ms": None},
                {"_id": "DRAFT_VERIFIED", "count": 210, "samples": 210,
                 "mean_elapsed_ms": 12000},
                {"_id": "MANUAL_FIELD_EDITED", "count": 360, "samples": 180,
                 "mean_elapsed_ms": None},
            ]
    events = _Collection([
        {"tenant_id": "TENANT-SYNTHETIC-A", "change_id": str(i),
         "action": "CHANGE_DRAFT", "occurred_at": "2026-11-28T10:00:00+00:00"}
        for i in range(201)
    ])
    db = _Db({
        lifecycle._CHANGE_EVENTS: events,
        lifecycle._OBSERVATIONS: _Aggregated([]),
    })
    monkeypatch.setattr(lifecycle, "get_database", lambda: db)
    result = lifecycle.read_organization_productivity(auth=_identity())
    assert result["source"] == "EOS_ORGANIZATION_CHANGE_EVENTS"
    assert result["recent_events_truncated"] is True
    assert result["bounded_events"] == 200
    assert result["client_report_source"] == "CLIENT_REPORTED"
    assert result["client_observation_sample"] == 640
    assert result["client_observed"]["MANUAL_FIELD_EDITED"] == 360
    assert result["client_mean_form_to_verified_seconds"] == 12.0
    assert result["accessibility_certified"] is False



def test_staffing_reconciliation_is_exact_tenant_and_never_claims_employee_linkage(monkeypatch):
    class _Employees:
        def aggregate(self, stages):
            assert stages[0] == {
                "$match": {"tenantId": "TENANT-SYNTHETIC-A",
                           "isActive": True, "deletedAt": None},
            }
            assert stages[1]["$group"]["_id"] == "$employment.department"
            return [
                {"_id": "Operations", "count": 5},
                {"_id": "Unknown legacy label", "count": 2},
                {"_id": "Finance", "count": 1},
            ]
    class _ReconcileDb(_Db):
        def __getitem__(self, name):
            assert name == "employees"
            return _Employees()
    rows = [
        {"tenant_id":"TENANT-SYNTHETIC-A","kind":"DEPARTMENT",
         "record_id":"DEP-OPS","status":"APPROVED","name":"Operations"},
        {"tenant_id":"TENANT-SYNTHETIC-A","kind":"DEPARTMENT",
         "record_id":"DEP-FIN-1","status":"APPROVED","name":"Finance"},
        {"tenant_id":"TENANT-SYNTHETIC-A","kind":"DEPARTMENT",
         "record_id":"DEP-FIN-2","status":"APPROVED","name":"FINANCE"},
        {"tenant_id":"FOREIGN-TENANT","kind":"DEPARTMENT",
         "record_id":"DEP-FOREIGN","status":"APPROVED","name":"Unknown legacy label"},
    ]
    db = _ReconcileDb({org._ORG_COLLECTION:_Collection(rows)})
    monkeypatch.setattr(lifecycle,"get_database",lambda:db)
    answer = lifecycle.read_department_staffing_reconciliation(
        auth=_identity(),directory_authority=_identity(),
    )
    assert answer["source_total_active"] == 8
    assert answer["candidate_matches"] == [{
        "department_id":"DEP-OPS","employee_count":5,
        "relationship":"LABEL_CANDIDATE_NOT_AUTHORIZED_ASSIGNMENT",
    }]
    assert answer["unmatched_active_employees"] == 2
    assert answer["ambiguous_active_employees"] == 1
    assert answer["employee_assignment_linkage_certified"] is False
    assert answer["retirement_approval_permitted"] is False


def test_staffing_reconciliation_denies_cross_tenant_before_database(monkeypatch):
    monkeypatch.setattr(lifecycle, "get_database",
                        lambda: (_ for _ in ()).throw(
                            AssertionError("Cross-tenant request cannot read Mongo")))
    with pytest.raises(HTTPException) as denied:
        lifecycle.read_department_staffing_reconciliation(
            auth=_identity("TENANT-SYNTHETIC-A"),
            directory_authority=_identity("TENANT-SYNTHETIC-B"),
        )
    assert denied.value.status_code == 403
    assert denied.value.detail == "ORGANIZATION_STAFFING_SCOPE_MISMATCH"


# ARTIFACT: tests/unit/test_hr_organization_lifecycle_expansion.py
# VERSION: v1.0.0-M03-HR03-ORGANIZATION-LIFECYCLE-CERT
# AUTHORITY BOUNDARY: Exact-tenant EOS authority and regression evidence; no grants or financial execution.
# TENANT POSTURE: Exact authorized tenant only; no cross-tenant records, Owner or root fallback.
# FAIL-CLOSED POSTURE: Missing or contradictory evidence is denied/unavailable, never approved.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
