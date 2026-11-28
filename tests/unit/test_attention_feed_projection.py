"""TITLE: WILSY OS Daily Attention Authorised Feed Unit Certificate
VERSION: v1.7.0-ENTITLEMENT-ONLY-CRM-CAPABILITY-CERT
AUTHORITY: WILSY OS Core Engineering disposable test authority only.
EPITOME: Prove source ownership, tenant scope, counts, urgency, filters,
         stable cursor paging and strict fail-closed AttentionItem contracts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_attention_feed_projection.py
COLLABORATION / OWNERSHIP: UnifiedMyWorkProjection owns tested source
         contract; attention_feed_projection is only a read-only adapter.
CERTIFICATION / UPDATE DATE: 2026-11-24
CHANGELOG: v1.7.0-ENTITLEMENT-ONLY-CRM-CAPABILITY-CERT verifies
           the canonical CRM source-owned transaction invokes exact-tenant
           entitlement admission without scanning daily_queue, and retains
           403/503 failure propagation, worker-thread and IAM scope checks.
CHANGELOG: v1.6.1-PROJECTS-DEPENDENCY-EVIDENCE-FIXTURE
           supplies the required zero-dependency total, remaining and READY
           proof for the synthetic assigned Projects work item; the production
           validator still rejects absent, inconsistent and invented evidence.
CHANGELOG: v1.6.0-CRM-CAPABILITY-ISOLATED-READ-CERT verifies
           CRM-only capability admission uses existing CRM read IAM and a
           worker-thread source-owned entitlement transaction, rejects
           unadmitted, mismatched and omitted sources, and never fabricates
           source command authority. Other feed and command tests unchanged.
CHANGELOG: v1.5.1-EXPLICIT-FASTAPI-DEPENDENCY-FIXTURES explicitly supplies
           optional FastAPI dependencies as None when calling async routes
           directly; the framework resolves Depends only for HTTP dispatch.
CHANGELOG: v1.5.0-SIX-SOURCE-ATTENTION-REGRESSION covers admitted HR and
           PROJECTS sources, exact count parity, source filters and rejection
           of unadmitted source requests without creating source authority.
CHANGELOG: v1.4.0-ISOLATED-SOURCE-COMMAND-IAM-CERT ensures
           CRM create and complete availability is derived only from
           current exact-tenant CRM command context, never foreign sources.
           v1.3.0-THREE-SOURCE-ACTION-IAM-CERT certifies
           source create/complete permissions independently, including CRM;
           denied/unadmitted sources do not gain command availability.
           v1.2.0-SOURCE-COMMAND-AVAILABILITY-CERT proves
           source completion can be advertised only for matching read and
           independently authorized command contexts; foreign scope denies.
           v1.1.0-FIVE-HUNDRED-PAGE-READ-CERT verifies deterministic
           500-item pagination with no overlap or fabricated totals.
           v1.0.2-EXACT-RULE-URGENCY-CERT corrects the expected
           rules-only score: overdue NORMAL is 80 + 10, not 100.
           v1.0.1-COMPLETE-SOURCE-COVERAGE-CERT requires every
           omitted source to be named without claiming entitlement or access.
           v1.0.0-ATTENTION-FEED-CONTRACT-CERT introduces deterministic
           synthetic-authority negative and positive projection tests.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant IDs and records only.
TENANT BOUNDARY: Foreign source and unauthorized filter explicitly reject.
AUTHORITY BOUNDARY: Tests never issue actual EOS command authority.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement evidence.
FAIL-CLOSED POSTURE: Invalid source, cursor, count and tenant fail tests.
"""
from datetime import datetime, timedelta, timezone
from copy import deepcopy
import asyncio
import threading
from types import SimpleNamespace
from fastapi import HTTPException
from tools.eos.api import attention_router as attention_api
from tools.eos.api.attention_router import (
    attention_authorised_actions, attention_crm_actions,
    attention_operations_actions, attention_intelligence_actions,
)

import pytest

from tools.eos.workspaces.service.unified_my_work_projection import build_unified_my_work
from tools.eos.workspaces.service.attention_feed_projection import (
    AttentionFeedError,
    build_attention_feed,
)

NOW = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)
TENANT = "WILSY-ATTENTION-DISPOSABLE-TENANT"
PRINCIPAL = "WILSY-ATTENTION-DISPOSABLE-PRINCIPAL"


def snapshot(count=5, *, now=NOW):
    """Produce preadmitted EOS-shaped source truth, never mock browser authority."""
    items = [{
        "work_item_id": f"ops-{index}",
        "title": f"Governed action {index}",
        "description": f"Action {index} evidence",
        "status": "OPEN",
        "priority": "HIGH" if index % 2 else "NORMAL",
        "due_at": (
            NOW - timedelta(hours=3) if index == 0
            else NOW + timedelta(days=index)
        ).isoformat(),
    } for index in range(count)]
    projection = build_unified_my_work(
        tenant_id=TENANT, principal_id=PRINCIPAL, now=now,
        operations={"tenant_id": TENANT, "items": items},
        crm={"tenant_id": TENANT, "items": []},
    )
    projection["sources_included"] = ["OPERATIONS", "CRM"]
    projection["authority"]["permits_source_commands"] = False
    return projection


def test_attention_item_is_real_source_derived_and_non_executable():
    feed = build_attention_feed(snapshot(), limit=10)
    assert feed["schema"] == "WILSY-OS-ATTENTION-FEED/V1"
    assert feed["tenantId"] == TENANT
    assert feed["principalId"] == PRINCIPAL
    assert feed["counts"] == {
        "active": 5, "overdue": 1, "dueToday": 1, "highPriority": 2,
    }
    assert feed["coverage"]["admittedSources"] == ["OPERATIONS", "CRM"]
    assert feed["coverage"]["notRepresentedSources"] == ["LEGAL", "INTELLIGENCE", "HR", "PROJECTS", "FINANCE", "PEOPLE"]
    assert feed["coverage"]["completeEnterpriseCoverage"] is False
    assert feed["sources"] == [
        {"moduleId": "OPERATIONS", "state": "ok", "count": 5},
        {"moduleId": "CRM", "state": "empty", "count": 0},
    ]
    overdue = feed["items"][0]
    assert overdue["sourceRecordId"] == "ops-0"
    assert overdue["isOverdue"] is True
    assert overdue["urgencyScore"] == 90
    assert overdue["whyRanked"] == "Overdue source deadline"
    assert overdue["actionHints"] == ["OPEN"]
    assert overdue["authzScope"] == "SOURCE_SERVICE_ONLY"
    assert overdue["slaBreachAt"] is None
    assert feed["authority"]["attentionCommandsEnabled"] is False



def test_hr_and_projects_are_verified_attention_sources_without_new_authority():
    """The active exact-assignee Projects source cannot break Attention coverage."""
    project_id = "prj-" + "a" * 48
    task_id = "ptk-" + "b" * 48
    current = build_unified_my_work(
        tenant_id=TENANT, principal_id=PRINCIPAL, now=NOW,
        crm={"tenant_id": TENANT, "items": []},
        hr={"tenant_id": TENANT, "items": []},
        projects={"tenant_id": TENANT, "items": [{
            "work_item_id": task_id,
            "title": "Activate governed project attachments",
            "description": "Budget gated production activation",
            "status": "OPEN",
            "priority": "NORMAL",
            "project_id": project_id,
            "owner_principal_id": PRINCIPAL,
            "dependency_total": 0,
            "dependency_remaining": 0,
            "dependency_readiness": "READY",
            "due_at": None,
            "due_date": None,
        }]},
    )
    current["sources_included"] = ["CRM", "HR", "PROJECTS"]
    feed = build_attention_feed(current)
    assert feed["counts"]["active"] == 1
    assert feed["coverage"]["admittedSources"] == ["CRM", "HR", "PROJECTS"]
    assert "PROJECTS" not in feed["coverage"]["notRepresentedSources"]
    assert "HR" not in feed["coverage"]["notRepresentedSources"]
    assert feed["items"][0]["id"] == "PROJECTS:" + task_id
    assert feed["items"][0]["sourceModule"] == "PROJECTS"
    assert feed["items"][0]["authzScope"] == "SOURCE_SERVICE_ONLY"
    assert build_attention_feed(current, sources=("PROJECTS",))["counts"]["active"] == 1
    assert build_attention_feed(current, sources=("HR",))["counts"]["active"] == 0
    with pytest.raises(AttentionFeedError, match="ATTENTION_SOURCE_NOT_AUTHORIZED"):
        build_attention_feed(current, sources=("LEGAL",))

    invalid = deepcopy(current)
    invalid["summary"]["source_counts"]["PROJECTS"] = 0
    with pytest.raises(AttentionFeedError, match="ATTENTION_SOURCE_COUNTS_INVALID"):
        build_attention_feed(invalid)


def test_filters_operate_on_real_rows_and_authorised_sources():
    rows = snapshot()
    assert build_attention_feed(rows, view="overdue")["filteredTotal"] == 1
    assert build_attention_feed(rows, view="due_today")["filteredTotal"] == 1
    assert build_attention_feed(rows, view="high_priority")["filteredTotal"] == 2
    assert build_attention_feed(rows, query="Governed action 3")["filteredTotal"] == 1
    assert build_attention_feed(rows, sources=("CRM",))["counts"]["active"] == 0
    assert build_attention_feed(rows, sources=("CRM",))["sources"][0]["count"] == 5
    with pytest.raises(AttentionFeedError, match="ATTENTION_SOURCE_NOT_AUTHORIZED"):
        build_attention_feed(rows, sources=("LEGAL",))
    with pytest.raises(AttentionFeedError, match="ATTENTION_SOURCE_NOT_AUTHORIZED"):
        build_attention_feed(rows, sources=("PEOPLE",))


def test_cursor_pages_survive_fresh_read_clock_without_cross_tenant_leak():
    first = build_attention_feed(snapshot(), limit=2)
    assert len(first["items"]) == 2
    assert first["nextCursor"]
    newer = snapshot(now=NOW + timedelta(seconds=5))
    second = build_attention_feed(newer, cursor=first["nextCursor"], limit=2)
    assert len(second["items"]) == 2
    assert {x["id"] for x in first["items"]}.isdisjoint(
        {x["id"] for x in second["items"]}
    )
    assert build_attention_feed(
        newer, cursor=second["nextCursor"], limit=2
    )["nextCursor"] is None

    changed = snapshot(now=NOW + timedelta(days=2))
    with pytest.raises(AttentionFeedError, match="ATTENTION_CURSOR_INVALID"):
        build_attention_feed(changed, cursor=first["nextCursor"], limit=2)

    foreign = deepcopy(newer)
    foreign["tenant_id"] = "OTHER-TENANT"
    with pytest.raises(AttentionFeedError, match="ATTENTION_CURSOR_INVALID"):
        build_attention_feed(foreign, cursor=first["nextCursor"], limit=2)


@pytest.mark.parametrize("bad_cursor", ["***", "e30", "bnVsbA", "WzAsImIiXQ"])
def test_tampered_cursor_fails_closed(bad_cursor):
    with pytest.raises(AttentionFeedError, match="ATTENTION_CURSOR_INVALID"):
        build_attention_feed(snapshot(), cursor=bad_cursor)


def test_source_count_drift_and_row_tenant_mismatch_fail_closed():
    damaged = deepcopy(snapshot())
    damaged["summary"]["source_counts"]["OPERATIONS"] = 999
    with pytest.raises(AttentionFeedError, match="ATTENTION_SOURCE_COUNTS_INVALID"):
        build_attention_feed(damaged)

    damaged = deepcopy(snapshot())
    damaged["items"][0]["tenant_id"] = "FOREIGN"
    with pytest.raises(AttentionFeedError, match="ATTENTION_ITEM_INVALID"):
        build_attention_feed(damaged)


def test_five_hundred_source_items_page_without_duplicates_or_fabricated_total():
    """500-item source scan preserves exact count through five bounded pages."""
    data = snapshot(count=500)
    cursor = None
    seen = set()
    for _ in range(5):
        page = build_attention_feed(data, limit=100, cursor=cursor)
        assert page["counts"]["active"] == 500
        assert page["filteredTotal"] == 500
        assert len(page["items"]) == 100
        ids = {item["id"] for item in page["items"]}
        assert len(ids) == 100
        assert not seen.intersection(ids)
        seen.update(ids)
        cursor = page["nextCursor"]
    assert cursor is None
    assert len(seen) == 500


def test_no_authorised_source_cannot_be_presented_as_enterprise_clear():
    empty = build_unified_my_work(
        tenant_id=TENANT, principal_id=PRINCIPAL, now=NOW,
    )
    empty["sources_included"] = []
    feed = build_attention_feed(empty)
    assert feed["items"] == []
    assert feed["counts"]["active"] == 0
    assert feed["coverage"]["completeEnterpriseCoverage"] is False
    assert feed["coverage"]["admittedSources"] == []
    # Real HTTP dependency rejects zero admitted sources before this projection.
    # This pure adapter does not grant a workspace or an authorization decision.



async def certify_actions(source, **overrides):
    contexts = {
        "operations_context": None,
        "intelligence_context": None,
        "crm_context": None,
        "operations_create": None,
        "intelligence_create": None,
        "crm_create": None,
        "crm_update": None,
    }
    contexts.update(overrides)
    return await attention_authorised_actions(source=source, **contexts)


def test_attention_actions_only_advertise_independently_authorized_source():
    source = snapshot()
    good = SimpleNamespace(
        tenant_id=TENANT,
        identity=SimpleNamespace(identity_id=PRINCIPAL),
    )
    response = asyncio.run(certify_actions(
        source=source, operations_context=good, intelligence_context=None,
    ))
    assert response["schema"] == "WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1"
    assert response["tenantId"] == TENANT
    assert response["principalId"] == PRINCIPAL
    assert response["sourceActions"] == {"OPERATIONS": ["COMPLETE"]}
    assert response["authority"] == "SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE"

    expanded = asyncio.run(certify_actions(
        source, operations_context=good, operations_create=good,
        crm_context=good, crm_create=good,
    ))
    assert expanded["sourceActions"] == {
        "OPERATIONS": ["CREATE", "COMPLETE"],
        "CRM": ["CREATE", "COMPLETE"],
    }

    none = asyncio.run(certify_actions(
        source=source, operations_context=None, intelligence_context=None,
    ))
    assert none["sourceActions"] == {}
    # Intelligence is not in the admitted My Work scope for this fixture.
    omitted = asyncio.run(certify_actions(
        source=source, operations_context=None, intelligence_context=good,
    ))
    assert omitted["sourceActions"] == {}


def test_attention_actions_reject_foreign_command_context_without_disclosing_records():
    source = snapshot()
    foreign = SimpleNamespace(
        tenant_id="FOREIGN",
        identity=SimpleNamespace(identity_id=PRINCIPAL),
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(certify_actions(
            source=source, operations_context=foreign, intelligence_context=None,
        ))
    assert exc.value.status_code == 503
    assert exc.value.detail == "ATTENTION_ACTION_CONTEXT_INCONSISTENT"


def test_crm_capability_scope_uses_one_independent_source_read_on_worker(
    monkeypatch: pytest.MonkeyPatch,
):
    """CRM authorization cannot incur Projects/HR/Operations aggregate reads."""
    caller = threading.get_ident()
    observed = []

    def crm_entitlement(*, tenant_id):
        observed.append((tenant_id, threading.get_ident()))

    monkeypatch.setattr(attention_api, "_verify_crm_action_entitlement", crm_entitlement)
    identity = SimpleNamespace(identity_id=PRINCIPAL)
    allowed = SimpleNamespace(tenant_id=TENANT, identity=identity)
    result = asyncio.run(attention_api._read_exact_crm_action_scope(
        TENANT, identity, allowed,
    ))
    assert result == {
        "tenant_id": TENANT,
        "principal_id": PRINCIPAL,
        "sources_included": ["CRM"],
    }
    assert len(observed) == 1
    assert observed[0][0] == TENANT
    assert observed[0][1] != caller


@pytest.mark.parametrize("read_context, expected_code", [
    (None, 403),
    ("FOREIGN", 503),
])
def test_crm_capability_scope_rejects_denied_or_cross_tenant_source(
    monkeypatch: pytest.MonkeyPatch,
    read_context,
    expected_code,
):
    """Neither denied nor mismatched source IAM reaches CRM persistence."""
    calls = []
    monkeypatch.setattr(
        attention_api, "_verify_crm_action_entitlement",
        lambda *, tenant_id: calls.append(tenant_id),
    )
    identity = SimpleNamespace(identity_id=PRINCIPAL)
    context = None if read_context is None else SimpleNamespace(
        tenant_id=read_context, identity=identity,
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(attention_api._read_exact_crm_action_scope(
            TENANT, identity, context,
        ))
    assert exc.value.status_code == expected_code
    assert calls == []


def test_crm_capability_entitlement_uses_canonical_transaction_without_queue(
    monkeypatch: pytest.MonkeyPatch,
):
    """Only source-owned entitlement verification may admit CRM actions."""
    calls = []

    class CRMService:
        def _require_entitlement(self, tenant_id, session):
            calls.append((tenant_id, session))

        def daily_queue(self, **_kwargs):
            pytest.fail("Capability GET must not enumerate CRM task records")

    session = object()
    monkeypatch.setattr(
        attention_api.crm_source, "_transaction",
        lambda callback: callback(CRMService(), session),
    )
    attention_api._verify_crm_action_entitlement(tenant_id=TENANT)
    assert calls == [(TENANT, session)]


@pytest.mark.parametrize("detail, status_code", [
    ("OWNER_WORK_CRM_NOT_ENTITLED", 403),
    ("OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE", 503),
])
def test_crm_action_entitlement_fails_closed_from_source_transaction(
    monkeypatch: pytest.MonkeyPatch, detail, status_code,
):
    def denied(_callback):
        raise HTTPException(status_code=status_code, detail=detail)

    monkeypatch.setattr(attention_api.crm_source, "_transaction", denied)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(attention_api._read_exact_crm_action_scope(
            TENANT,
            SimpleNamespace(identity_id=PRINCIPAL),
            SimpleNamespace(
                tenant_id=TENANT, identity=SimpleNamespace(identity_id=PRINCIPAL),
            ),
        ))
    assert exc.value.status_code == status_code
    assert exc.value.detail == detail



def test_isolated_crm_commands_do_not_depend_on_other_module_authorization():
    source = snapshot()
    good = SimpleNamespace(
        tenant_id=TENANT,
        identity=SimpleNamespace(identity_id=PRINCIPAL),
    )
    allowed = asyncio.run(attention_crm_actions(source, create=good, complete=good, update=None))
    assert allowed["sourceActions"] == {"CRM": ["CREATE", "COMPLETE"]}
    denied = asyncio.run(attention_crm_actions(source, create=None, complete=None, update=None))
    assert denied["sourceActions"] == {}
    with pytest.raises(HTTPException) as exc:
        asyncio.run(attention_crm_actions(source, create=SimpleNamespace(
            tenant_id="FOREIGN",
            identity=SimpleNamespace(identity_id=PRINCIPAL),
        ), complete=None, update=None))
    assert exc.value.status_code == 503


def test_isolated_unadmitted_module_never_reports_command_capabilities():
    source = snapshot()
    good = SimpleNamespace(
        tenant_id=TENANT,
        identity=SimpleNamespace(identity_id=PRINCIPAL),
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(attention_intelligence_actions(source, create=good, complete=good))
    assert exc.value.status_code == 403
    allowed = asyncio.run(attention_operations_actions(source, create=good, complete=None))
    assert allowed["sourceActions"] == {"OPERATIONS": ["CREATE"]}

# ARTIFACT: tests/unit/test_attention_feed_projection.py
# VERSION: v1.7.0-ENTITLEMENT-ONLY-CRM-CAPABILITY-CERT
# AUTHORITY BOUNDARY: Disposable pure-projection evidence; source commands absent.
# TENANT POSTURE: Synthetic tenant/principal only; cross-scope cursor invalid.
# FAIL-CLOSED POSTURE: Invalid coverage, totals and source scope throw.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
