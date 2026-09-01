"""WILSY OS — canonical playbook scheduler harness.

TITLE: Scheduler Playbook Integration Harness
VERSION: v1.0.0-WILSY-SCHEDULER-PLAYBOOK-CANONICAL
AUTHORITY: Wilsy OS Core Governance
EPITOME: Runs one explicit-tenant playbook analysis through the canonical FG171C scheduler and bridge.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/run_scheduler_playbook.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 migrates the playbook harness to frozen FG171C, requires caller-supplied tenant scope, rejects blank/forbidden sentinels, removes synthetic/default tenants, uses subscribe_async, removes sleep synchronization, retains deterministic shutdown, and introduces no authentication, KEXEC, persistence, transaction, or financial authority.
COMPLIANCE: Explicit scheduling scope; no persistence or financial execution authority.
SECURITY / PRIVACY POSTURE: Tenant is scope evidence only; payload content is not authority and event logs omit sensitive payloads.
TENANT BOUNDARY: Required caller-supplied tenant_id is stripped and validated; no tenant is invented or authorized here.
AUTHORITY BOUNDARY: Owns orchestration only; authentication, membership, authorization, identity, and execution authority remain external.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive financial execution authority.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
from typing import Any

from tools.eos.runtime import EventDrivenScheduler, RuntimeEventBus, WorkerEventBridge
from tools.eos.runtime.scheduler import SchedulerAuthorityError
from tools.eos.runtime.scheduler_events import RuntimeEventTypeEnum
from tools.eos.runtime.worker_registry import EngineWorkerRegistry
from tools.eos.runtime.worker import BaseEngineWorker
from tools.eos.knowledge.playbook import KnowledgeBasePlaybook, PlaybookRule, PlaybookExecutionEngine, PlaybookCategoryEnum, PlaybookSeverityEnum

logger = logging.getLogger("WilsyOS.Runner")
_FORBIDDEN_TENANTS = frozenset({"unknown", "none", "null", "tenant-default"})


class PlaybookAuthorityError(ValueError):
    """Raised when explicit scheduling scope is absent or forbidden."""


def validate_tenant_id(value: str) -> str:
    """Validate caller-supplied tenant scope; this does not authenticate it."""
    if not isinstance(value, str):
        raise PlaybookAuthorityError("tenant_id must be a string")
    tenant_id = value.strip()
    if not tenant_id or tenant_id.casefold() in _FORBIDDEN_TENANTS:
        raise PlaybookAuthorityError("tenant_id is invalid")
    return tenant_id


def build_parser() -> argparse.ArgumentParser:
    """Build a CLI parser requiring explicit tenant scheduling scope."""
    parser = argparse.ArgumentParser(description="Run the governed playbook scheduler harness")
    parser.add_argument("--tenant-id", required=True, help="Explicit tenant scope evidence")
    return parser


class PlaybookEngineWorker(BaseEngineWorker):
    """Adapt the canonical playbook engine to the standard worker contract."""
    @property
    def engine_name(self) -> str:
        return "legal_playbook_engine"

    async def process_task(self, task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute playbook analysis and return deterministic artifact evidence."""
        pb_data = payload.get("playbook_data")
        doc_text = payload.get("document_text", "")
        if not pb_data or not doc_text:
            raise ValueError("Payload must contain 'playbook_data' and 'document_text'.")
        playbook = KnowledgeBasePlaybook(**pb_data)
        report = await PlaybookExecutionEngine(playbook).execute_playbook(
            document_id=payload.get("document_id", "doc-unknown"), document_text=doc_text
        )
        output = report.model_dump()
        output.update({"artifact": True, "artifact_type": "playbook_compliance_report", "artifact_id": report.report_id})
        return output


async def event_listener(event: Any) -> None:
    """Log canonical event identity/status without treating payload as authority."""
    logger.info("event=%s execution=%s task=%s tenant=%s", type(event).__name__, getattr(event, "execution_id", None), getattr(event, "task_id", None), getattr(event, "tenant_id", None))


async def main(*, tenant_id: str) -> None:
    """Run one playbook lifecycle with explicit scope and deterministic cleanup."""
    validated_tenant_id = validate_tenant_id(tenant_id)
    event_bus = RuntimeEventBus()
    for event_type in (RuntimeEventTypeEnum.TASK_STARTED, RuntimeEventTypeEnum.TASK_COMPLETED, RuntimeEventTypeEnum.TASK_FAILED, RuntimeEventTypeEnum.ARTIFACT_PUBLISHED):
        event_bus.subscribe_async(event_type.value, event_listener)
    registry = EngineWorkerRegistry()
    registry.register_worker("legal_playbook_engine", PlaybookEngineWorker())
    WorkerEventBridge(event_bus=event_bus, worker_registry=registry)
    scheduler = EventDrivenScheduler(event_bus=event_bus)
    try:
        rule = PlaybookRule(title="Governing Law Requirement", category=PlaybookCategoryEnum.COMPLIANCE, severity=PlaybookSeverityEnum.CRITICAL, description="Agreements must specify the governing jurisdiction.", required_keywords=["governed by|governing law"], remediation_guidance="Add a standard governing law clause.")
        playbook = KnowledgeBasePlaybook(domain="Commercial Contracts", title="Standard NDA Policy", rules=[rule])
        task_id = await scheduler.schedule_task(engine_name="legal_playbook_engine", tenant_id=validated_tenant_id, payload={"document_id": "doc-nda-9901", "document_text": "This agreement is governed by California law.", "playbook_data": playbook.model_dump()})
        logger.info("playbook task scheduled: %s", task_id)
    finally:
        await scheduler.shutdown()


if __name__ == "__main__":
    args = build_parser().parse_args()
    try:
        asyncio.run(main(tenant_id=args.tenant_id))
    except (PlaybookAuthorityError, SchedulerAuthorityError) as error:
        raise SystemExit(str(error)) from error


# ARTIFACT: run_scheduler_playbook.py
# VERSION: v1.0.0-WILSY-SCHEDULER-PLAYBOOK-CANONICAL
# AUTHORITY BOUNDARY: orchestration only; no authentication, authorization, or financial authority.
# TENANT POSTURE: explicit validated caller scope; no default or synthesis.
# FAIL-CLOSED POSTURE: missing/blank/forbidden tenant references are rejected before runtime work.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
