"""Tenant-scoped compliance scan worker for durable EOS execution.

This handler detects expired identity documents using the legacy source contract,
persists privacy-minimised findings and notification intents, and never sends
messages or changes client compliance status.
"""
from __future__ import annotations

from datetime import datetime, timezone
import asyncio
from hashlib import sha256
from typing import Any

from .worker_result import WorkerExecutionStatusEnum, WorkerResultDTO


class ComplianceScanWorker:
    engine_name = "COMPLIANCE_SCAN"

    def __init__(self, *, clients: Any, findings: Any, notification_outbox: Any,
                 mongo_client: Any) -> None:
        self.clients = clients
        self.findings = findings
        self.notification_outbox = notification_outbox
        self.mongo_client = mongo_client

    @staticmethod
    def _context(payload: dict[str, Any]) -> tuple[str, str, datetime]:
        context = payload.get("__eos_task_context")
        data = payload.get("data")
        if not isinstance(context, dict) or not isinstance(data, dict):
            raise ValueError("COMPLIANCE_TASK_CONTEXT_REQUIRED")
        tenant_id = context.get("tenant_id")
        task_id = context.get("task_id")
        observed = data.get("observed_at")
        if not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id.casefold() in {"global", "root", "master", "wilsy_root"}:
            raise ValueError("COMPLIANCE_TENANT_SCOPE_REQUIRED")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("COMPLIANCE_TASK_ID_REQUIRED")
        if not isinstance(observed, str):
            raise ValueError("COMPLIANCE_OBSERVED_AT_REQUIRED")
        try:
            timestamp = datetime.fromisoformat(observed.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("COMPLIANCE_OBSERVED_AT_INVALID") from error
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("COMPLIANCE_OBSERVED_AT_INVALID")
        return tenant_id, task_id, timestamp.astimezone(timezone.utc)

    async def execute(self, task_id: str, payload: dict[str, Any]) -> WorkerResultDTO:
        # PyMongo is synchronous; isolate it so the event loop can renew the task lease.
        return await asyncio.to_thread(self._execute_sync, task_id, payload)

    def _execute_sync(self, task_id: str, payload: dict[str, Any]) -> WorkerResultDTO:
        try:
            tenant_id, context_task_id, observed_at = self._context(payload)
            if context_task_id != task_id:
                raise ValueError("COMPLIANCE_TASK_ID_MISMATCH")
            cursor = self.clients.find(
                {"tenantId": tenant_id, "idExpiryDate": {"$lt": observed_at},
                 "complianceStatus": "VERIFIED"},
                {"_id": 1, "idExpiryDate": 1},
            )
            records = list(cursor)
            created = 0
            with self.mongo_client.start_session() as session:
                def persist(active_session: Any) -> int:
                    count = 0
                    for record in records:
                        source_id = str(record["_id"])
                        expiry = record.get("idExpiryDate")
                        if not isinstance(expiry, datetime):
                            continue
                        identity = sha256(
                            f"{tenant_id}|{source_id}|{expiry.isoformat()}|FICA_ID_EXPIRED".encode()
                        ).hexdigest()
                        finding = {
                            "tenant_id": tenant_id,
                            "finding_id": identity,
                            "source_type": "CLIENT_IDENTITY_DOCUMENT",
                            "source_record_reference": source_id,
                            "rule_code": "FICA_ID_EXPIRED",
                            "observed_at": observed_at,
                            "source_expiry_at": expiry,
                            "status": "OPEN",
                        }
                        result = self.findings.update_one(
                            {"tenant_id": tenant_id, "finding_id": identity},
                            {"$setOnInsert": finding},
                            upsert=True, session=active_session,
                        )
                        if result.upserted_id is not None:
                            self.notification_outbox.update_one(
                                {"tenant_id": tenant_id, "notification_id": identity},
                                {"$setOnInsert": {
                                    "tenant_id": tenant_id,
                                    "notification_id": identity,
                                    "event_type": "COMPLIANCE_FINDING_OPENED",
                                    "finding_id": identity,
                                    "delivery_status": "PENDING",
                                    "created_at": observed_at,
                                }},
                                upsert=True, session=active_session,
                            )
                            count += 1
                    return count
                created = session.with_transaction(persist)
            return WorkerResultDTO(
                task_id=task_id, status=WorkerExecutionStatusEnum.SUCCESS,
                execution_duration_ms=0.0,
                output={"tenant_id": tenant_id, "documents_scanned": len(records),
                        "new_findings": created, "notification_intents": created},
            )
        except Exception as error:
            code = str(error) if str(error).startswith("COMPLIANCE_") else "COMPLIANCE_SCAN_FAILED"
            return WorkerResultDTO(
                task_id=task_id, status=WorkerExecutionStatusEnum.FAILED,
                execution_duration_ms=0.0, output={}, error_details=code,
            )


def provision_compliance_scan_indexes(*, findings: Any, notification_outbox: Any) -> None:
    """Explicit deployment-time indexes; never invoked at import."""
    findings.create_index([("tenant_id", 1), ("finding_id", 1)], unique=True,
                          name="uq_compliance_finding_identity")
    notification_outbox.create_index([("tenant_id", 1), ("notification_id", 1)], unique=True,
                                     name="uq_compliance_notification_identity")
    notification_outbox.create_index([("delivery_status", 1), ("created_at", 1)],
                                     name="ix_compliance_notification_pending")
