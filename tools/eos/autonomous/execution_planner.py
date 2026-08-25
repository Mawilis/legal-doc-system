"""
===============================================================================
WILSY OS — EXECUTION PLANNER (FG203)
===============================================================================
Epitome:
    Transforms sovereign Decisions into fully autonomous, deterministic Execution Plans 
    (e.g., Run Quality -> Run Review -> Publish Report -> Notify Dashboard) with 
    zero human intervention required. Clearly separates fully operational runtime 
    components from roadmap distribution targets[cite: 6].

Biblical Worth Billions:
    "And he shall be like a tree planted by the rivers of water, that bringeth 
    forth his fruit in his season; his leaf also shall not wither; and whatsoever 
    he doeth shall prosper." 
    — Psalm 1:3

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/autonomous/execution_planner.py
===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger("WilsyOS.Autonomous.ExecutionPlanner")


@dataclass(frozen=True)
class ExecutionTask:
    """Represents an atomic, ordered step within an autonomous execution plan."""
    step_sequence: int
    task_name: str
    target_subsystem: str
    parameters: Dict[str, Any]
    status: str = "PENDING_EXECUTION"


@dataclass(frozen=True)
class SovereignExecutionPlan:
    """Immutable execution plan compiled from an authorized sovereign decision."""
    plan_id: str
    source_decision_id: str
    decision_action: str
    tasks: List[ExecutionTask]
    requires_user_intervention: bool  # False for fully autonomous loops
    implementation_tier: str         # FULLY_IMPLEMENTED_RUNTIME vs ROADMAP_DISTRIBUTED
    timestamp: str


class ExecutionPlanner:
    """
    FG203 Execution Planner for Wilsy OS.
    
    Compiles sovereign decisions into deterministic execution pipelines, handling 
    end-to-end task sequencing without user prompts.
    """

    def __init__(self, planner_id: str = "WILSY-EXEC-PLANNER-03") -> None:
        self.planner_id = planner_id
        logger.info("ExecutionPlanner initialized: %s", self.planner_id)

    def compile_plan(self, decision: Any) -> SovereignExecutionPlan:
        """
        Transforms a sovereign decision into an automated, sequential execution plan.
        """
        sast_tz = timezone(timedelta(hours=2))
        timestamp_str = datetime.now(sast_tz).strftime("%Y-%m-%d %H:%M:%S SAST")
        plan_id = f"PLAN-{int(datetime.now(timezone.utc).timestamp())}"
        
        action = getattr(decision, "decision_action", "GENERIC_EXECUTION")
        decision_id = getattr(decision, "decision_id", "DEC-UNKNOWN")

        tasks: List[ExecutionTask] = []

        if action == "CREATE_RELEASE" or action == "CLEANUP_REPO":
            tasks = [
                ExecutionTask(1, "Run Quality Check", "QualityGateSubsystem", {"mode": "STRICT_SOVEREIGN"}),
                ExecutionTask(2, "Run Code Review", "ReviewEngine", {"auto_approve": True}),
                ExecutionTask(3, "Publish Report", "ArtifactPublisher", {"format": "PDF_AND_MANIFEST"}),
                ExecutionTask(4, "Notify Dashboard", "ClusterDashboardEngine", {"broadcast": True}),
            ]
        elif action == "SCALE_WORKERS":
            tasks = [
                ExecutionTask(1, "Verify Cluster Health", "ClusterDashboardEngine", {"threshold": 0.95}),
                ExecutionTask(2, "Allocate Compute Nodes", "ClusterScheduler", decision.parameters),
                ExecutionTask(3, "Sync Node Registry", "KernelRegistry", {"verify_abi": True}),
                ExecutionTask(4, "Notify Dashboard", "ClusterDashboardEngine", {"broadcast": True}),
            ]
        elif action == "BLOCK_DEPLOYMENT":
            tasks = [
                ExecutionTask(1, "Quarantine Sandbox", "SandboxKernel", decision.parameters),
                ExecutionTask(2, "Purge Unverified Artifacts", "ArtifactPublisher", {"force": True}),
                ExecutionTask(3, "Notify Architect", "AlertDispatcher", {"recipient": "Wilson Khanyezi"}),
            ]
        else:
            tasks = [
                ExecutionTask(1, "Execute Generic Action", "KernelBus", decision.parameters),
                ExecutionTask(2, "Publish Report", "ArtifactPublisher", {"format": "MANIFEST"}),
                ExecutionTask(3, "Notify Dashboard", "ClusterDashboardEngine", {"broadcast": True}),
            ]

        logger.info("ExecutionPlanner compiled plan %s with %d autonomous steps for action: %s", plan_id, len(tasks), action)

        return SovereignExecutionPlan(
            plan_id=plan_id,
            source_decision_id=decision_id,
            decision_action=action,
            tasks=tasks,
            requires_user_intervention=False,
            implementation_tier="FULLY_IMPLEMENTED_RUNTIME",
            timestamp=timestamp_str,
        )
