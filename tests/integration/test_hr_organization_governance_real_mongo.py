"""TITLE: WILSY OS HR03 Real Mongo Organization Governance Certificate
VERSION: v1.0.0-M03-HR03-REAL-MONGO-TRANSACTION-CERT
AUTHORITY: WILSY OS Core Governance
EPITOME: Certify live replica-set transactions for tenant-scoped HR business activity,
department amendment, revision history, abort rollback and command replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_hr_organization_governance_real_mongo.py
COLLABORATION / OWNERSHIP: WILSY OS HR Organization engineering
CERTIFICATION / UPDATE DATE: 2026-11-28
CHANGELOG: v1.0.0-M03-HR03-REAL-MONGO-TRANSACTION-CERT adds disposable local-only Mongo evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 test isolation.
SECURITY / PRIVACY POSTURE: Synthetic test-only data, UUID database, bounded cleanup, never production.
TENANT BOUNDARY: Distinct synthetic tenants, no root/founder credentials or fixtures.
AUTHORITY BOUNDARY: Direct source command certificates; HTTP IAM separately tested.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import os
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pymongo import MongoClient

from tools.eos.api import hr_workforce_directory_router as org
from tools.eos.api import hr_organization_business_context_router as business
from tools.eos.api import hr_organization_lifecycle_router as lifecycle

_VERSION = "v1.0.0-M03-HR03-REAL-MONGO-TRANSACTION-CERT"


def _auth(tenant: str, actor: str):
    """Synthetic already-authorized context; only integration service behavior tested."""
    return SimpleNamespace(
        tenant_id=tenant, identity=SimpleNamespace(identity_id=actor),
    )


@pytest.fixture
def mongo(monkeypatch):
    """Admit disposable loopback replica-set only; never fall back to Atlas."""
    uri = os.environ.get("WILSY_HR03_TEST_MONGO_URI", "")
    if not uri or not uri.startswith("mongodb://") or not any(
        host in uri for host in ("127.0.0.1", "localhost")
    ) or "mongodb+srv" in uri:
        pytest.skip("HR03 disposable loopback replica-set URI absent; not certified")
    client = MongoClient(uri, serverSelectionTimeoutMS=2000, retryWrites=True)
    try:
        topology = client.admin.command("hello")
        if not topology.get("setName"):
            pytest.skip("HR03 Mongo instance is not a replica-set; not certified")
    except Exception:
        pytest.skip("HR03 disposable Mongo replica-set unavailable; not certified")
    db_name = "wilsy_hr03_cert_" + uuid4().hex
    db = client[db_name]
    monkeypatch.setattr(org, "get_client", lambda: client)
    monkeypatch.setattr(org, "get_database", lambda: db)
    monkeypatch.setattr(lifecycle, "get_client", lambda: client)
    monkeypatch.setattr(lifecycle, "get_database", lambda: db)
    monkeypatch.setattr(business, "get_client", lambda: client)
    monkeypatch.setattr(business, "get_database", lambda: db)
    try:
        yield db, client
    finally:
        client.drop_database(db_name)
        client.close()


def test_independent_activity_profile_and_exact_tenant_readback(mongo):
    """Approve a tenant's activity profile; reject cross-tenant and self decision."""
    db, _ = mongo
    tenant_a, tenant_b = "TENANT-SYNTHETIC-A", "TENANT-SYNTHETIC-B"
    maker, checker = _auth(tenant_a, "HR-MAKER"), _auth(tenant_a, "HR-CHECKER")
    proposal = business.draft_business_activity_context(
        business.ActivityContextDraft(
            activity_ids=["technology", "legal"],
            reason="Synthetic mixed professional operating context",
        ), key="hr03-context-create-0000001", auth=maker,
    )["proposal"]
    submitted = business.submit_business_activity_context(
        proposal["proposal_id"],
        business.ContextRevision(expected_revision=1),
        key="hr03-context-submit-0000001", auth=maker,
    )["proposal"]
    with pytest.raises(HTTPException) as self_decision:
        business.decide_business_activity_context(
            proposal["proposal_id"],
            business.ContextDecision(expected_revision=submitted["revision"],
                decision="APPROVE",reason="Self-decision must remain denied"),
            key="hr03-context-self-denial-01",auth=maker,
        )
    assert self_decision.value.status_code == 403
    approved = business.decide_business_activity_context(
        proposal["proposal_id"],
        business.ContextDecision(expected_revision=submitted["revision"],
            decision="APPROVE", reason="Independent synthetic classification check"),
        key="hr03-context-approve-00001", auth=checker,
    )["proposal"]
    assert approved["status"] == "APPROVED"
    own = business.read_business_activity_context(auth=checker)
    foreign = business.read_business_activity_context(auth=_auth(tenant_b, "HR-OTHER"))
    assert own["activity_ids"] == ["technology", "legal"]
    assert own["revision"] == 1
    assert foreign["activity_ids"] == []
    assert foreign["status"] == "UNCONFIGURED"
    assert own["entity_status"] == "ENTITY_SOURCE_NOT_CONNECTED"


def test_governed_department_amendment_versions_and_exact_replay(mongo):
    """One maker/checker change creates immutable versions and exact replay."""
    db, _ = mongo
    tenant = "TENANT-SYNTHETIC-A"
    maker, checker = _auth(tenant, "HR-MAKER"), _auth(tenant, "HR-CHECKER")
    db[org._ORG_COLLECTION].insert_one({
        "tenant_id": tenant, "record_id": "DEP-OPERATIONS",
        "kind": "DEPARTMENT", "status": "APPROVED", "revision": 3,
        "name": "Operations", "parent_id": None, "effective_from": "2026-01-01",
        "created_by": "HR-ORIGINAL", "submitted_by": "HR-ORIGINAL",
    })
    request = lifecycle.ChangeDraft(
        change_type="AMEND", name="Operations and Delivery",
        effective_from=date(2026, 11, 27),
        reason="Updated operating model for delivery division",
    )
    proposed = lifecycle.propose_department_change(
        "DEP-OPERATIONS", request,
        key="hr03-department-change-create-01", auth=maker,
    )
    replay = lifecycle.propose_department_change(
        "DEP-OPERATIONS", request,
        key="hr03-department-change-create-01", auth=maker,
    )
    assert proposed == replay
    assert db[lifecycle._CHANGES].count_documents({"tenant_id":tenant}) == 1
    change = proposed["change"]
    submitted = lifecycle.submit_department_change(
        "DEP-OPERATIONS", change["change_id"],
        lifecycle.ExpectedRevision(expected_revision=change["revision"]),
        key="hr03-department-change-submit-01", auth=maker,
    )["change"]
    with pytest.raises(HTTPException) as denied:
        lifecycle.decide_department_change(
            "DEP-OPERATIONS", change["change_id"],
            lifecycle.ChangeDecision(expected_revision=submitted["revision"],
                decision="APPROVE", reason="Self-checker not permitted"),
            key="hr03-department-change-deny-001", auth=maker,
        )
    assert denied.value.status_code == 403
    result = lifecycle.decide_department_change(
        "DEP-OPERATIONS", change["change_id"],
        lifecycle.ChangeDecision(expected_revision=submitted["revision"],
            decision="APPROVE", reason="Second independent principal approved"),
        key="hr03-department-change-decide-01", auth=checker,
    )
    assert result["change"]["status"] == "APPROVED"
    current = db[org._ORG_COLLECTION].find_one(
        {"tenant_id":tenant, "record_id":"DEP-OPERATIONS"})
    assert current["revision"] == 4
    assert current["name"] == "Operations and Delivery"
    before = lifecycle.read_department_at_date(
        "DEP-OPERATIONS", date(2026,11,1),auth=checker)
    after = lifecycle.read_department_at_date(
        "DEP-OPERATIONS", date(2026,11,28),auth=checker)
    assert before["record"]["name"] == "Operations"
    assert after["record"]["name"] == "Operations and Delivery"
    assert db[lifecycle._VERSIONS].count_documents({
        "tenant_id":tenant,"record_id":"DEP-OPERATIONS"}) == 2
    assert db[lifecycle._CHANGE_EVENTS].count_documents({
        "tenant_id":tenant}) == 3


def test_aborted_transaction_preserves_current_department_and_events(mongo):
    """Mongo rollback cannot leave partial approved department or evidence."""
    db, client = mongo
    tenant = "TENANT-SYNTHETIC-A"
    records = db[org._ORG_COLLECTION]
    versions = db[lifecycle._VERSIONS]
    records.insert_one({
        "tenant_id":tenant,"kind":"DEPARTMENT","record_id":"DEP-ROLLBACK",
        "name":"Before","parent_id":None,"effective_from":"2026-01-01",
        "status":"APPROVED","revision":1,
    })
    change = {
        "change_type":"AMEND","effective_from":"2026-11-27",
        "name":"After","parent_id":None,"clear_parent":False,
    }
    with client.start_session() as session:
        session.start_transaction()
        original = records.find_one({
            "tenant_id":tenant,"kind":"DEPARTMENT","record_id":"DEP-ROLLBACK",
        }, session=session)
        lifecycle._apply_change(records,versions,original,change,tenant,session)
        session.abort_transaction()
    assert records.find_one({"tenant_id":tenant,"record_id":"DEP-ROLLBACK"})["name"] == "Before"
    assert versions.count_documents({"tenant_id":tenant,"record_id":"DEP-ROLLBACK"}) == 0


# ARTIFACT: tests/integration/test_hr_organization_governance_real_mongo.py
# VERSION: v1.0.0-M03-HR03-REAL-MONGO-TRANSACTION-CERT
# AUTHORITY BOUNDARY: Disposable real Mongo certificate, never a grant.
# TENANT POSTURE: Synthetic UUID database, separate tenant A/B, local only.
# FAIL-CLOSED POSTURE: Unavailable replica-set is a skipped, NOT certified gate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
