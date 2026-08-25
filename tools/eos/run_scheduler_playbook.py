"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Integration Harness: Event-Driven Scheduler <-> Knowledge Playbook Engine.
    Wraps the FG172A Playbook Engine in an FG171B Engine Worker, schedules an
    execution via the FG171C Event Bus, and listens for compliance artifacts.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready integration layer. Zero child's place.
    Proverbs 24:3-4 - "Through wisdom is an house builded; and by understanding 
    it is established: And by knowledge shall the chambers be filled..."

Collaboration & Maintenance:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
===============================================================================
"""

import asyncio
import logging
import json
from typing import Any, Dict

from tools.eos.runtime.worker import BaseEngineWorker
from tools.eos.runtime.worker_registry import EngineWorkerRegistry
from tools.eos.runtime.scheduler_events import RuntimeEventBus, RuntimeEventTypeEnum
from tools.eos.runtime.scheduler_bridge import WorkerEventBridge
from tools.eos.runtime.scheduler import EventDrivenScheduler

from tools.eos.knowledge.playbook import (
    KnowledgeBasePlaybook,
    PlaybookRule,
    PlaybookExecutionEngine,
    PlaybookCategoryEnum,
    PlaybookSeverityEnum
)

# Configure logging for the harness
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("WilsyOS.Runner")


class PlaybookEngineWorker(BaseEngineWorker):
    """
    Production-ready worker wrapping the KnowledgeBase Playbook execution.
    Adheres to the immutable EngineWorkerResultDTO contract (FG171B).
    """

    @property
    def engine_name(self) -> str:
        return "legal_playbook_engine"

    # [FUNCTION EXPLANATION]: Fulfills BaseEngineWorker abstract interface for task execution.
    async def process_task(self, task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._execute_impl(payload)

    # [FUNCTION EXPLANATION]: Extracts playbook/document payload, instantiates the engine, and returns standardized output.
    async def _execute_impl(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pb_data = payload.get("playbook_data")
        doc_text = payload.get("document_text", "")
        doc_id = payload.get("document_id", "doc-unknown")

        if not pb_data or not doc_text:
            raise ValueError("Payload must contain 'playbook_data' and 'document_text'.")

        # Rehydrate the Playbook model
        playbook = KnowledgeBasePlaybook(**pb_data)
        engine = PlaybookExecutionEngine(playbook)

        # Execute playbook
        report = await engine.execute_playbook(document_id=doc_id, document_text=doc_text)

        # Convert report to dict for the DTO output
        output = report.model_dump()
        
        # Flag this execution output as an artifact so the EventBridge publishes an ARTIFACT_PUBLISHED event
        output["artifact"] = True
        output["artifact_type"] = "playbook_compliance_report"
        output["artifact_id"] = report.report_id

        return output


# [FUNCTION EXPLANATION]: Listener callback to intercept and print event bus traffic.
async def event_listener(event: Any) -> None:
    """Generic async listener to log emitted events from the RuntimeEventBus."""
    event_type = type(event).__name__
    event_data = {k: v for k, v in event.__dict__.items() if k not in ["payload", "output", "metadata"]}
    logger.info(f"\n>>> [EVENT BUS INTERCEPT] -> {event_type} Emitted:")
    logger.info(json.dumps(event_data, indent=2))
    print("-" * 60)


# [FUNCTION EXPLANATION]: Main async orchestration sequence.
async def main() -> None:
    logger.info("Initializing Wilsy OS Playbook Integration Harness...")

    # 1. Initialize Event Bus (FG171C)
    event_bus = RuntimeEventBus()
    event_bus.subscribe(RuntimeEventTypeEnum.TASK_STARTED, event_listener)
    event_bus.subscribe(RuntimeEventTypeEnum.TASK_COMPLETED, event_listener)
    event_bus.subscribe(RuntimeEventTypeEnum.ARTIFACT_PUBLISHED, event_listener)

    # 2. Initialize Worker Registry & Register the Playbook Worker (FG171B)
    registry = EngineWorkerRegistry()
    playbook_worker = PlaybookEngineWorker()
    registry.register_worker("legal_playbook_engine", playbook_worker)

    # 3. Initialize Event Bridge (Wires Scheduler to Registry)
    bridge = WorkerEventBridge(event_bus=event_bus, worker_registry=registry)

    # 4. Initialize Scheduler
    scheduler = EventDrivenScheduler(event_bus=event_bus)

    # 5. Define a mock NDA document and Playbook Data
    mock_nda_text = """
    This Non-Disclosure Agreement is governed by the laws of California.
    The Receiving Party shall hold the Confidential Information in strict confidence.
    This agreement does not include an arbitration clause.
    """

    mock_rule = PlaybookRule(
        title="Governing Law Requirement",
        category=PlaybookCategoryEnum.COMPLIANCE,
        severity=PlaybookSeverityEnum.CRITICAL,
        description="Agreements must specify the governing jurisdiction.",
        required_keywords=["governed by|governing law"],
        remediation_guidance="Add a standard governing law clause."
    )

    playbook = KnowledgeBasePlaybook(
        domain="Commercial Contracts",
        title="Standard NDA Policy",
        rules=[mock_rule]
    )

    payload = {
        "document_id": "doc-nda-9901",
        "document_text": mock_nda_text,
        "playbook_data": playbook.model_dump()
    }

    # 6. Schedule the task via the EventDrivenScheduler
    logger.info("\nDispatching Playbook Task to Scheduler...\n" + "="*60)
    task_id = await scheduler.schedule_task(
        engine_name="legal_playbook_engine",
        payload=payload
    )

    # 7. Wait briefly for async events to process across the bus
    await asyncio.sleep(0.5)

    await scheduler.shutdown()
    logger.info("Integration harness execution completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
