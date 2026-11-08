"""Daily tenant-scoped compliance task scheduling for Python EOS."""
from __future__ import annotations

import asyncio
from datetime import datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from .durable_task_queue import enqueue_task

SAST = ZoneInfo("Africa/Johannesburg")
TENANT_COLLECTION = "tenants"


def enqueue_daily_compliance_scans(*, tenants: Any, tasks: Any, observed_at: datetime) -> int:
    """Enqueue one idempotent scan per ACTIVE tenant from canonical tenant records."""
    if not isinstance(observed_at, datetime) or observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError("COMPLIANCE_SCHEDULER_TIMESTAMP_INVALID")
    observed = observed_at.astimezone(timezone.utc)
    day_key = observed.astimezone(SAST).date().isoformat()
    count = 0
    for tenant in tenants.find({"status": "ACTIVE"}, {"tenantId": 1}):
        tenant_id = tenant.get("tenantId")
        if not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id.casefold() in {"global", "root", "master", "wilsy_root"}:
            continue
        enqueue_task(
            tasks, tenant_id=tenant_id, task_id=f"COMPLIANCE_SCAN:{day_key}",
            task_type="COMPLIANCE_SCAN", engine_name="COMPLIANCE_SCAN",
            payload={"observed_at": observed.isoformat()}, now=observed,
            priority=5, max_attempts=5,
        )
        count += 1
    return count


async def run_daily_compliance_scheduler(
    *, tenants: Any, tasks: Any, stop_event: asyncio.Event,
    clock: Any = None,
) -> None:
    """Schedule the daily 00:15 SAST compliance pass until graceful shutdown."""
    from datetime import datetime as DateTime
    now_fn = clock or (lambda: DateTime.now(timezone.utc))
    while not stop_event.is_set():
        now = now_fn()
        local_now = now.astimezone(SAST)
        next_run = datetime.combine(local_now.date(), time(0, 15), tzinfo=SAST)
        if local_now >= next_run:
            next_run += timedelta(days=1)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=(next_run - local_now).total_seconds())
        except asyncio.TimeoutError:
            enqueue_daily_compliance_scans(tenants=tenants, tasks=tasks, observed_at=now_fn())


__all__ = ["enqueue_daily_compliance_scans", "run_daily_compliance_scheduler"]
