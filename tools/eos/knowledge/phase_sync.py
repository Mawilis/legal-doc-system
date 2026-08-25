"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Phase Completion & Knowledge Base Playbook Sync Engine (FG172B).
    Listens for Phase completion triggers, automatically updates the active
    Knowledge Base Playbook with new phase capabilities, and emits explicit
    system notifications across terminal and runtime buses.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready phase synchronization engine. Zero child's place.
    Isaiah 43:19 - "Behold, I will do a new thing; now it shall spring forth..."
    Proverbs 18:15 - "The heart of the prudent getteth knowledge; and the ear of the wise seeketh knowledge."

Collaboration & Maintenance:
    - [Architecture]: Automated phase completion listener & dynamic playbook sync engine.
    - [Diagnostics]: Multi-channel notifications and capability audit tracking.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from tools.eos.knowledge.playbook import (
    KnowledgeBasePlaybook,
    PlaybookCategoryEnum,
    PlaybookRule,
    PlaybookSeverityEnum,
)
from tools.eos.runtime.scheduler_events import RuntimeEventBus, SchedulerEventDTO, SchedulerEventTypeEnum

logger = logging.getLogger("WilsyOS.Knowledge.PhaseSync")


class PhaseCapabilityDTO(BaseModel):
    """Immutable capability record added upon completing an engineering phase."""
    model_config = ConfigDict(frozen=True)

    phase_id: str = Field(description="Unique phase ID (e.g., FG171C, FG172A).")
    phase_name: str = Field(description="Human-readable name of completed phase.")
    rule_title: str = Field(description="Playbook rule title derived from phase.")
    category: PlaybookCategoryEnum = Field(description="Functional rule category.")
    severity: PlaybookSeverityEnum = Field(default=PlaybookSeverityEnum.HIGH, description="Rule severity.")
    description: str = Field(description="Summary of phase capability added to playbook.")
    required_keywords: List[str] = Field(default_factory=list, description="Required terms/keywords for rule.")
    remediation_guidance: str = Field(description="Actionable guidance if capability fails.")


class PhaseCompletionReportDTO(BaseModel):
    """Execution output generated when a phase is synchronized with the playbook."""
    model_config = ConfigDict(frozen=True)

    sync_id: str = Field(default_factory=lambda: f"sync-{uuid4().hex[:8]}", description="Unique sync record ID.")
    phase_id: str = Field(description="Completed phase identifier.")
    playbook_id: str = Field(description="Target updated playbook ID.")
    previous_rule_count: int = Field(ge=0, description="Rule count prior to update.")
    updated_rule_count: int = Field(ge=0, description="Rule count after update.")
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of playbook update."
    )


class PhaseCompletionSyncEngine:
    """Engine responsible for updating Knowledge Base Playbooks upon phase completions and broadcasting alerts."""

    def __init__(self, event_bus: RuntimeEventBus, playbook: KnowledgeBasePlaybook) -> None:
        self._bus = event_bus
        self._playbook = playbook
        logger.info(
            f"PhaseCompletionSyncEngine initialized for Playbook [{playbook.playbook_id}] ({playbook.title})"
        )

    # [FUNCTION EXPLANATION]: Emits explicit visual alert notification to terminal logs.
    def _broadcast_system_notification(self, phase_capability: PhaseCapabilityDTO, report: PhaseCompletionReportDTO) -> None:
        alert_box = f"""
================================================================================
 🔔 WILSY OS SYSTEM NOTIFICATION: PHASE COMPLETION & KNOWLEDGE SYNC 🔔
================================================================================
 STATUS         : SUCCESS - PHASE [{phase_capability.phase_id}] VERIFIED
 PHASE NAME     : {phase_capability.phase_name}
 PLAYBOOK ID    : {report.playbook_id}
 RULE ADDED     : {phase_capability.rule_title} [{phase_capability.category.value}]
 RULE COUNT     : {report.previous_rule_count} -> {report.updated_rule_count} Rules
 SYNC TIMESTAMP : {report.updated_at}
================================================================================
"""
        print(alert_box)
        logger.info(f"Broadcast phase completion notification for [{phase_capability.phase_id}].")

    # [FUNCTION EXPLANATION]: Registers phase capability into playbook, broadcasts event, and notifies system.
    async def record_and_sync_phase(self, phase_capability: PhaseCapabilityDTO) -> PhaseCompletionReportDTO:
        """
        Syncs completed phase details into the active Knowledge Base Playbook,
        publishes a runtime event, and issues a system notification alert.
        """
        previous_count = len(self._playbook.rules)

        # 1. Convert Phase Capability into a Playbook Rule
        new_rule = PlaybookRule(
            title=f"[{phase_capability.phase_id}] {phase_capability.rule_title}",
            category=phase_capability.category,
            severity=phase_capability.severity,
            description=phase_capability.description,
            required_keywords=phase_capability.required_keywords,
            prohibited_keywords=[],
            remediation_guidance=phase_capability.remediation_guidance,
        )

        # 2. Append rule to active playbook rules list
        self._playbook.rules.append(new_rule)
        updated_count = len(self._playbook.rules)

        report = PhaseCompletionReportDTO(
            phase_id=phase_capability.phase_id,
            playbook_id=self._playbook.playbook_id,
            previous_rule_count=previous_count,
            updated_rule_count=updated_count,
        )

        # 3. Publish TASK_COMPLETED event to Event Bus for runtime audit
        sync_event = SchedulerEventDTO(
            event_type=SchedulerEventTypeEnum.TASK_COMPLETED,
            session_id="sys-phase-sync",
            tenant_id="wilsy-core",
            task_id=f"task-sync-{phase_capability.phase_id.lower()}",
            engine_name="PhaseCompletionSyncEngine",
            payload={
                "phase_id": phase_capability.phase_id,
                "phase_name": phase_capability.phase_name,
                "rule_added": new_rule.title,
                "updated_rule_count": updated_count,
            },
        )
        await self._bus.publish(sync_event)

        # 4. Broadcast Visual System Notification Alert
        self._broadcast_system_notification(phase_capability, report)

        return report
