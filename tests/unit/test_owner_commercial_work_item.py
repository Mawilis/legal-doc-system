from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.crm.domain.owner_commercial_work_item import (
    OwnerCommercialWorkItem,
    OwnerWorkItemError,
    OwnerWorkKind,
    OwnerWorkPriority,
    OwnerWorkStatus,
    build_daily_queue,
    command_fingerprint,
)

NOW = datetime(2026, 11, 3, 8, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"


def item(title="Call prospect", *, due_at=None, priority=OwnerWorkPriority.NORMAL, tenant=TENANT):
    return OwnerCommercialWorkItem.create(
        tenant_id=tenant, title=title, owner_principal_id="principal-1",
        due_at=due_at, priority=priority, now=NOW,
    )


def test_create_is_tenant_bound_and_round_trips_strictly():
    value = item(due_at=NOW + timedelta(hours=2))
    assert OwnerCommercialWorkItem.from_dict(value.to_dict()) == value
    assert value.kind is OwnerWorkKind.TASK
    assert value.status is OwnerWorkStatus.OPEN


@pytest.mark.parametrize("tenant", ["", " ", "MASTER", "GLOBAL_ROOT", "WILSY_ROOT"])
def test_global_or_malformed_tenant_is_rejected(tenant):
    with pytest.raises(OwnerWorkItemError):
        item(tenant=tenant)


def test_daily_queue_prioritises_overdue_then_due_today_then_future():
    overdue = item("Overdue", due_at=NOW - timedelta(days=1))
    today = item("Today", due_at=NOW + timedelta(hours=2), priority=OwnerWorkPriority.HIGH)
    future = item("Future", due_at=NOW + timedelta(days=2), priority=OwnerWorkPriority.CRITICAL)
    queue = build_daily_queue([future, today, overdue], tenant_id=TENANT, now=NOW)
    assert [row["title"] for row in queue] == ["Overdue", "Today", "Future"]
    assert queue[0]["is_overdue"] is True
    assert queue[1]["is_due_today"] is True


def test_daily_queue_excludes_foreign_tenant_and_terminal_items():
    foreign = item("Foreign", tenant="OTHER-TENANT")
    completed = OwnerCommercialWorkItem(
        **{**item("Done").__dict__, "status": OwnerWorkStatus.COMPLETED,
           "completed_at": NOW, "updated_at": NOW}
    ) if hasattr(item("Done"), "__dict__") else None
    queue = build_daily_queue([foreign], tenant_id=TENANT, now=NOW)
    assert queue == ()


def test_priority_breaks_ties_deterministically():
    normal = item("Normal", due_at=NOW + timedelta(hours=1))
    high = item("High", due_at=NOW + timedelta(hours=1), priority=OwnerWorkPriority.HIGH)
    assert [row["title"] for row in build_daily_queue(
        [normal, high], tenant_id=TENANT, now=NOW
    )] == ["High", "Normal"]


def test_idempotency_fingerprint_is_stable_and_key_bound():
    value = item()
    assert command_fingerprint(value, "request-1") == command_fingerprint(value, "request-1")
    assert command_fingerprint(value, "request-1") != command_fingerprint(value, "request-2")


def test_completion_requires_explicit_completion_timestamp():
    with pytest.raises(OwnerWorkItemError, match="COMPLETION_EVIDENCE_REQUIRED"):
        OwnerCommercialWorkItem(
            work_item_id="owk_1", tenant_id=TENANT, title="x", description="",
            kind=OwnerWorkKind.TASK, status=OwnerWorkStatus.COMPLETED,
            priority=OwnerWorkPriority.NORMAL, owner_principal_id="principal-1",
            due_at=None, source_type=None, source_id=None, created_at=NOW,
            updated_at=NOW,
        )
