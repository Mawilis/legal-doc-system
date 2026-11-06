from datetime import datetime, timedelta, timezone
from dataclasses import replace

import pytest

from tools.eos.workspaces.domain.tenant_module_work_item import (
    TenantModuleWorkItem,
    ModuleWorkItemError,
    ModuleWorkKind,
    ModuleWorkPriority,
    ModuleWorkStatus,
    build_daily_queue,
    command_fingerprint,
)

NOW = datetime(2026, 11, 3, 8, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"


def item(title="Call prospect", *, due_at=None, priority=ModuleWorkPriority.NORMAL, tenant=TENANT):
    return TenantModuleWorkItem.create(
        tenant_id=tenant, title=title, created_by_principal_id="principal-1",
        due_at=due_at, priority=priority, now=NOW,
    )


def test_create_is_tenant_bound_and_round_trips_strictly():
    value = item(due_at=NOW + timedelta(hours=2))
    assert TenantModuleWorkItem.from_dict(value.to_dict()) == value
    assert value.kind is ModuleWorkKind.TASK
    assert value.status is ModuleWorkStatus.OPEN


@pytest.mark.parametrize("tenant", ["", " ", "MASTER", "GLOBAL_ROOT", "WILSY_ROOT"])
def test_global_or_malformed_tenant_is_rejected(tenant):
    with pytest.raises(ModuleWorkItemError):
        item(tenant=tenant)


def test_daily_queue_prioritises_overdue_then_due_today_then_future():
    overdue = item("Overdue", due_at=NOW - timedelta(days=1))
    today = item("Today", due_at=NOW + timedelta(hours=2), priority=ModuleWorkPriority.HIGH)
    future = item("Future", due_at=NOW + timedelta(days=2), priority=ModuleWorkPriority.CRITICAL)
    queue = build_daily_queue([future, today, overdue], tenant_id=TENANT, now=NOW)
    assert [row["title"] for row in queue] == ["Overdue", "Today", "Future"]
    assert queue[0]["is_overdue"] is True
    assert queue[1]["is_due_today"] is True


def test_daily_queue_excludes_foreign_tenant_and_terminal_items():
    foreign = item("Foreign", tenant="OTHER-TENANT")
    completed = replace(
        item("Done"), status=ModuleWorkStatus.COMPLETED,
        completed_at=NOW, updated_at=NOW,
    )
    queue = build_daily_queue([foreign, completed], tenant_id=TENANT, now=NOW)
    assert queue == ()


def test_priority_breaks_ties_deterministically():
    normal = item("Normal", due_at=NOW + timedelta(hours=1))
    high = item("High", due_at=NOW + timedelta(hours=1), priority=ModuleWorkPriority.HIGH)
    assert [row["title"] for row in build_daily_queue(
        [normal, high], tenant_id=TENANT, now=NOW
    )] == ["High", "Normal"]


def test_idempotency_fingerprint_is_stable_and_key_bound():
    value = item()
    assert command_fingerprint(value, "request-1") == command_fingerprint(value, "request-1")
    assert command_fingerprint(value, "request-1") != command_fingerprint(value, "request-2")


def test_completion_requires_explicit_completion_timestamp():
    with pytest.raises(ModuleWorkItemError, match="COMPLETION_EVIDENCE_REQUIRED"):
        TenantModuleWorkItem(
            work_item_id="tmw_1", tenant_id=TENANT, title="x", description="",
            kind=ModuleWorkKind.TASK, status=ModuleWorkStatus.COMPLETED,
            priority=ModuleWorkPriority.NORMAL, created_by_principal_id="principal-1",
            due_at=None, source_type=None, source_id=None, created_at=NOW,
            updated_at=NOW,
        )
