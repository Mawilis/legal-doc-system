from datetime import datetime, timezone
from unittest.mock import MagicMock

from tools.eos.runtime.compliance_scan_scheduler import enqueue_daily_compliance_scans

NOW = datetime(2026, 11, 8, 12, tzinfo=timezone.utc)


def test_daily_scheduler_enqueues_one_deterministic_task_per_active_tenant():
    tenants, tasks = MagicMock(), MagicMock()
    tenants.find.return_value = [
        {"tenantId": "tenant-a"}, {"tenantId": "tenant-b"},
        {"tenantId": "WILSY_ROOT"}, {"tenantId": ""},
    ]
    assert enqueue_daily_compliance_scans(tenants=tenants, tasks=tasks, observed_at=NOW) == 2
    assert tenants.find.call_args.args[0] == {"status": "ACTIVE"}
    assert tasks.insert_one.call_count == 2
    first = tasks.insert_one.call_args_list[0].args[0]
    assert first["tenant_id"] == "tenant-b" or first["tenant_id"] == "tenant-a"
    assert first["task_id"] == "COMPLIANCE_SCAN:2026-11-08"
    assert first["engine_name"] == "COMPLIANCE_SCAN"
    assert first["payload"]["observed_at"] == NOW.isoformat()


def test_scheduler_rejects_naive_observation_time():
    tenants, tasks = MagicMock(), MagicMock()
    try:
        enqueue_daily_compliance_scans(
            tenants=tenants, tasks=tasks,
            observed_at=datetime(2026, 11, 8, 12),
        )
    except ValueError as error:
        assert str(error) == "COMPLIANCE_SCHEDULER_TIMESTAMP_INVALID"
    else:
        raise AssertionError("naive scheduler timestamp was accepted")
    tenants.find.assert_not_called()
    tasks.insert_one.assert_not_called()
