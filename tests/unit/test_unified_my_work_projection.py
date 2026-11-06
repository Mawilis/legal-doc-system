from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.workspaces.service.unified_my_work_projection import (
    SCHEMA,
    UnifiedMyWorkProjectionError,
    build_unified_my_work,
)


NOW = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"
PRINCIPAL = "principal-1"


def item(work_item_id="task-1", *, title="Prepare report", status="OPEN",
         priority="NORMAL", due_at=None):
    return {
        "work_item_id": work_item_id,
        "title": title,
        "status": status,
        "priority": priority,
        "due_at": due_at,
    }


def test_unifies_authorized_source_reads_and_preserves_source_ownership():
    result = build_unified_my_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        now=NOW,
        legal={
            "tenant_id": TENANT,
            "assigned_work_items": [item("legal-1", priority="HIGH")],
            "supervised_work_items": [item("legal-1", priority="HIGH")],
        },
        operations={"tenant_id": TENANT, "items": [item("ops-1")]},
        intelligence={"tenant_id": TENANT, "items": [item("intel-1")]},
        crm={"tenant_id": TENANT, "items": [item("crm-1")]},
    )

    assert result["schema"] == SCHEMA
    assert result["summary"]["active_count"] == 4
    assert result["summary"]["source_counts"] == {
        "LEGAL": 1, "OPERATIONS": 1, "INTELLIGENCE": 1, "CRM": 1,
    }
    legal = next(row for row in result["items"] if row["source"] == "LEGAL")
    assert legal["visibility_provenance"] == ["LEGAL_ASSIGNED", "LEGAL_SUPERVISED"]
    assert legal["action_authority"] == "SOURCE_SERVICE_ONLY"
    assert legal["completion_route"] is None
    assert result["authority"]["permits_completion"] is False
    assert result["authority"]["permits_approval"] is False


def test_queue_is_deterministic_and_orders_overdue_before_other_work():
    result = build_unified_my_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        now=NOW,
        operations={
            "tenant_id": TENANT,
            "items": [
                item("later", priority="CRITICAL", due_at=(NOW + timedelta(days=1)).isoformat()),
                item("overdue", priority="LOW", due_at=(NOW - timedelta(days=1)).isoformat()),
            ],
        },
    )
    assert [row["work_item_id"] for row in result["items"]] == ["overdue", "later"]
    assert result["summary"]["overdue_count"] == 1


def test_same_work_item_id_in_different_sources_does_not_collide():
    result = build_unified_my_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        now=NOW,
        operations={"tenant_id": TENANT, "items": [item("same")]},
        crm={"tenant_id": TENANT, "items": [item("same")]},
    )
    assert len(result["items"]) == 2
    assert {row["source_key"] for row in result["items"]} == {
        "OPERATIONS:same", "CRM:same",
    }


def test_rejects_foreign_tenant_source_before_projection():
    with pytest.raises(UnifiedMyWorkProjectionError, match="SOURCE_TENANT_MISMATCH"):
        build_unified_my_work(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            now=NOW,
            operations={"tenant_id": "FOREIGN-TENANT", "items": [item()]},
        )


def test_rejects_divergent_duplicate_from_same_authorized_source():
    with pytest.raises(UnifiedMyWorkProjectionError, match="SOURCE_ITEM_DIVERGENCE"):
        build_unified_my_work(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            now=NOW,
            legal={
                "tenant_id": TENANT,
                "assigned_work_items": [item("legal-1", title="Original")],
                "supervised_work_items": [item("legal-1", title="Changed")],
            },
        )


def test_excludes_terminal_items_without_rewriting_source_records():
    result = build_unified_my_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        now=NOW,
        crm={
            "tenant_id": TENANT,
            "items": [item("done", status="COMPLETED"), item("cancelled", status="CANCELLED")],
        },
    )
    assert result["items"] == []
    assert result["summary"]["active_count"] == 0


def test_rejects_naive_or_malformed_due_dates():
    for due_at in ("2026-11-06T12:00:00", "not-a-date"):
        with pytest.raises(UnifiedMyWorkProjectionError, match="SOURCE_DUE_AT_INVALID"):
            build_unified_my_work(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                now=NOW,
                operations={"tenant_id": TENANT, "items": [item(due_at=due_at)]},
            )


def test_rejects_malformed_source_item_instead_of_silently_dropping_it():
    with pytest.raises(UnifiedMyWorkProjectionError, match="SOURCE_ITEM_IDENTITY_INVALID"):
        build_unified_my_work(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            now=NOW,
            operations={"tenant_id": TENANT, "items": [{"title": "No source id", "status": "OPEN"}]},
        )
