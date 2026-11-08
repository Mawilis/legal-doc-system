from datetime import datetime, timezone
from unittest.mock import MagicMock

from tools.eos.runtime.compliance_scan_worker import (
    ComplianceScanWorker,
    provision_compliance_scan_indexes,
)
from tools.eos.runtime.worker_result import WorkerExecutionStatusEnum

NOW = datetime(2026, 11, 8, 12, tzinfo=timezone.utc)


class Session:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def with_transaction(self, callback):
        return callback(self)


def worker_for(records):
    clients, findings, outbox, tasks, mongo = (MagicMock(), MagicMock(), MagicMock(),
                                                   MagicMock(), MagicMock())
    clients.find.return_value = records
    mongo.start_session.return_value = Session()
    findings.update_one.return_value.upserted_id = "new"
    tasks.update_one.return_value.modified_count = 1
    return ComplianceScanWorker(clients=clients, findings=findings,
                                notification_outbox=outbox, tasks=tasks,
                                mongo_client=mongo), clients, findings, outbox


def payload(tenant="tenant-a"):
    return {"__eos_task_context": {"tenant_id": tenant, "task_id": "task-a",
                              "worker_id": "worker-a", "lease_token": "lease-a"},
            "data": {"observed_at": NOW.isoformat()}}


def test_expired_identity_scan_is_tenant_scoped_and_emits_minimised_finding_and_outbox():
    worker, clients, findings, outbox = worker_for([
        {"_id": "client-1", "idExpiryDate": datetime(2026, 1, 1), "name": "private"},
    ])
    result = __import__("asyncio").run(worker.execute("task-a", payload()))
    assert result.status is WorkerExecutionStatusEnum.SUCCESS
    assert result.output["new_findings"] == 1
    query = clients.find.call_args.args[0]
    assert query["tenantId"] == "tenant-a"
    assert query["complianceStatus"] == "VERIFIED"
    assert query["idExpiryDate"]["$lt"] == NOW
    persisted = findings.update_one.call_args.args[1]["$setOnInsert"]
    assert "name" not in persisted and "private" not in repr(persisted)
    assert outbox.update_one.call_args.args[1]["$setOnInsert"]["delivery_status"] == "PENDING"


def test_repeat_finding_does_not_create_duplicate_notification_intent():
    worker, _, findings, outbox = worker_for([
        {"_id": "client-1", "idExpiryDate": datetime(2026, 1, 1)},
    ])
    findings.update_one.return_value.upserted_id = None
    result = __import__("asyncio").run(worker.execute("task-a", payload()))
    assert result.status is WorkerExecutionStatusEnum.SUCCESS
    outbox.update_one.assert_not_called()


def test_compliance_scan_rejects_global_tenant_scope():
    worker, clients, _, _ = worker_for([])
    result = __import__("asyncio").run(worker.execute("task-a", payload("WILSY_ROOT")))
    assert result.status is WorkerExecutionStatusEnum.FAILED
    assert result.error_details == "COMPLIANCE_TENANT_SCOPE_REQUIRED"
    clients.find.assert_not_called()


def test_compliance_scan_requires_explicit_aware_observation_time():
    worker, clients, _, _ = worker_for([])
    data = payload()
    data["data"]["observed_at"] = "2026-11-08T12:00:00"
    result = __import__("asyncio").run(worker.execute("task-a", data))
    assert result.status is WorkerExecutionStatusEnum.FAILED
    assert result.error_details == "COMPLIANCE_OBSERVED_AT_INVALID"
    clients.find.assert_not_called()


def test_compliance_indexes_are_explicit_and_unique():
    clients, findings, outbox = MagicMock(), MagicMock(), MagicMock()
    provision_compliance_scan_indexes(clients=clients, findings=findings, notification_outbox=outbox)
    assert clients.create_index.call_args.kwargs["name"] == "ix_compliance_expired_identity_scan"
    assert findings.create_index.call_args.kwargs["unique"] is True
    assert outbox.create_index.call_count == 2



def test_compliance_worker_fails_closed_when_live_task_lease_is_not_owned():
    import asyncio
    clients, findings, outbox, tasks, mongo = (MagicMock(), MagicMock(), MagicMock(),
                                                   MagicMock(), MagicMock())
    tasks.update_one.return_value.modified_count = 0
    mongo.start_session.return_value = Session()
    worker = ComplianceScanWorker(clients=clients, findings=findings,
                                  notification_outbox=outbox, tasks=tasks,
                                  mongo_client=mongo)
    result = asyncio.run(worker.execute("task-a", payload()))
    assert result.status is WorkerExecutionStatusEnum.FAILED
    assert result.error_details == "COMPLIANCE_TASK_LEASE_LOST"
    findings.update_one.assert_not_called()
    outbox.update_one.assert_not_called()
