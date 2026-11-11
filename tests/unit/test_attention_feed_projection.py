"""TITLE: WILSY OS Daily Attention Authorised Feed Unit Certificate
VERSION: v1.3.0-THREE-SOURCE-ACTION-IAM-CERT
AUTHORITY: WILSY OS Core Engineering disposable test authority only.
EPITOME: Prove source ownership, tenant scope, counts, urgency, filters,
         stable cursor paging and strict fail-closed AttentionItem contracts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_attention_feed_projection.py
COLLABORATION / OWNERSHIP: UnifiedMyWorkProjection owns tested source
         contract; attention_feed_projection is only a read-only adapter.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: v1.3.0-THREE-SOURCE-ACTION-IAM-CERT certifies
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
from types import SimpleNamespace
from fastapi import HTTPException
from tools.eos.api.attention_router import attention_authorised_actions

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
    assert feed["coverage"]["notRepresentedSources"] == ["LEGAL", "INTELLIGENCE", "FINANCE", "PEOPLE"]
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

# ARTIFACT: tests/unit/test_attention_feed_projection.py
# VERSION: v1.3.0-THREE-SOURCE-ACTION-IAM-CERT
# AUTHORITY BOUNDARY: Disposable pure-projection evidence; source commands absent.
# TENANT POSTURE: Synthetic tenant/principal only; cross-scope cursor invalid.
# FAIL-CLOSED POSTURE: Invalid coverage, totals and source scope throw.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
