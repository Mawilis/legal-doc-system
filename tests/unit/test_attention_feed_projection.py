"""TITLE: WILSY OS Daily Attention Authorised Feed Unit Certificate
VERSION: v1.0.2-EXACT-RULE-URGENCY-CERT
AUTHORITY: WILSY OS Core Engineering disposable test authority only.
EPITOME: Prove source ownership, tenant scope, counts, urgency, filters,
         stable cursor paging and strict fail-closed AttentionItem contracts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_attention_feed_projection.py
COLLABORATION / OWNERSHIP: UnifiedMyWorkProjection owns tested source
         contract; attention_feed_projection is only a read-only adapter.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.2-EXACT-RULE-URGENCY-CERT corrects the expected
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


# ARTIFACT: tests/unit/test_attention_feed_projection.py
# VERSION: v1.0.2-EXACT-RULE-URGENCY-CERT
# AUTHORITY BOUNDARY: Disposable pure-projection evidence; source commands absent.
# TENANT POSTURE: Synthetic tenant/principal only; cross-scope cursor invalid.
# FAIL-CLOSED POSTURE: Invalid coverage, totals and source scope throw.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
