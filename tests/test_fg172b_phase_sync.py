"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Master Verification Test for Phase Sync & System Notification Engine (FG172B).
    Verifies automatic updating of Knowledge Base Playbooks upon phase completion
    and system-wide alert notifications.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready verification test. Zero child's place.
    Proverbs 24:3-4 - "Through wisdom is an house builded; and by understanding it is established..."

Collaboration & Maintenance:
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import asyncio
import logging

from tools.eos.knowledge.phase_sync import PhaseCapabilityDTO, PhaseCompletionSyncEngine
from tools.eos.knowledge.playbook import KnowledgeBasePlaybook, PlaybookCategoryEnum, PlaybookSeverityEnum
from tools.eos.runtime.scheduler_events import RuntimeEventBus

logging.basicConfig(level=logging.INFO)


# [FUNCTION EXPLANATION]: Master verification for Phase Sync and Notification Engine.
async def run_master_verification() -> None:
    print("\n==================================================================")
    print("      WILSY OS: FG172B PHASE SYNC & NOTIFICATION VERIFICATION    ")
    print("==================================================================\n")

    # 1. Instantiate Core Event Bus & Knowledge Base Playbook
    bus = RuntimeEventBus()
    playbook = KnowledgeBasePlaybook(
        domain="Wilsy OS Core Architecture",
        title="Master Enterprise Engineering Playbook",
        version="1.0.0",
        rules=[],
    )

    sync_engine = PhaseCompletionSyncEngine(event_bus=bus, playbook=playbook)

    # 2. Define Phase Capability DTO for Completed Phase FG172A
    capability_fg172a = PhaseCapabilityDTO(
        phase_id="FG172A",
        phase_name="Knowledge Base Playbook Engine",
        rule_title="Rule Evaluation & Remediation Enforcement",
        category=PlaybookCategoryEnum.COMPLIANCE,
        severity=PlaybookSeverityEnum.CRITICAL,
        description="Enforces strict playbook evaluation, alias phrase matching, and remediation generation.",
        required_keywords=["playbook evaluation", "remediation guidance"],
        remediation_guidance="Ensure playbook rules support phrase aliases using '|' and regex pattern matching.",
    )

    # 3. Execute Record and Sync
    report = await sync_engine.record_and_sync_phase(capability_fg172a)

    # 4. Assertions
    assert report.previous_rule_count == 0
    assert report.updated_rule_count == 1
    assert len(playbook.rules) == 1
    assert playbook.rules[0].title == "[FG172A] Rule Evaluation & Remediation Enforcement"
    assert len(bus._emitted_history) == 1

    print(" -> SUCCESS: Playbook updated automatically with phase capability.")
    print(" -> SUCCESS: System notification broadcasted successfully.")
    print(" -> SUCCESS: RuntimeEventBus captured phase completion event.")

    print("\n==================================================================")
    print("         FG172B MASTER VERIFICATION: ALL SYSTEMS GREEN           ")
    print("==================================================================\n")


if __name__ == "__main__":
    asyncio.run(run_master_verification())
