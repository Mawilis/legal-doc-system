"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
ORCHESTRATION SUBSYSTEM: AUTONOMOUS ORCHESTRATOR
===============================================================================

File Path:
    tools/eos/autonomous/orchestrator/autonomous_orchestrator.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Implements the AutonomousOrchestrator, providing end-to-end management 
    of autonomous system directives. Integrates policy evaluation, action 
    planning, and executor dispatch into a unified, thread-safe runtime engine.

Biblical Worth Billions:
    "Order and simplify are the first steps toward the mastery of a subject."
    — 1 Corinthians 14:40

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import os
import sys
import threading
import uuid
from typing import Any, Dict, List, Optional

# --- ABSOLUTE PATH BOOTSTRAP GUARANTEE ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tools.eos.autonomous.domain.autonomous_action import (
    AutonomousAction,
    ActionCategory,
    ActionPriority,
)
from tools.eos.autonomous.domain.autonomous_plan import AutonomousPlan
from tools.eos.autonomous.domain.autonomous_result import AutonomousResult
from tools.eos.autonomous.domain.autonomous_policy import AutonomousPolicy
from tools.eos.autonomous.policy.policy_registry import PolicyRegistry, policy_registry
from tools.eos.autonomous.planning.action_planner import ActionPlanner
from tools.eos.autonomous.execution.action_executor import ActionExecutor


class AutonomousOrchestrator:
    """
    Sovereign master coordinator for Wilsy OS autonomous execution sequences.
    """

    def __init__(
        self,
        registry: Optional[PolicyRegistry] = None,
        planner: Optional[ActionPlanner] = None,
        executor: Optional[ActionExecutor] = None
    ) -> None:
        self._lock = threading.RLock()
        self.registry = registry or policy_registry
        self.planner = planner or ActionPlanner()
        self.executor = executor or ActionExecutor()
        self._execution_history: List[Dict[str, Any]] = []

    def process_directive(
        self,
        title: str,
        description: str,
        actions: List[AutonomousAction],
        override_authority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates an autonomous directive end-to-end:
        1. Generates an AutonomousPlan via ActionPlanner.
        2. Retrieves active policies from PolicyRegistry.
        3. Dispatches execution sequence via ActionExecutor.
        4. Compiles audit telemetry records.
        """
        with self._lock:
            # Step 1: Create execution plan
            plan: AutonomousPlan = self.planner.create_plan(
                title=title,
                description=description,
                actions=actions
            )

            # Step 2: Fetch active policies
            active_policies: List[AutonomousPolicy] = self.registry.get_active_policies()

            # Step 3: Execute plan through executor gateway
            results: List[AutonomousResult] = self.executor.execute_plan(
                plan=plan,
                policies=active_policies,
                override_authority=override_authority
            )

            # Step 4: Determine overall status
            all_successful = all(
                getattr(res, "success", getattr(res, "is_success", False))
                for res in results
            ) if results else False

            plan_id = getattr(plan, "plan_id", getattr(plan, "id", "UNKNOWN_PLAN"))

            orchestration_summary = {
                "orchestration_id": f"ORC-{uuid.uuid4().hex[:10].upper()}",
                "plan_id": plan_id,
                "title": title,
                "status": "SUCCESS" if all_successful else "FAILED",
                "actions_executed": len(results),
                "total_actions": len(actions),
                "results": results
            }

            self._execution_history.append(orchestration_summary)
            return orchestration_summary

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Returns full execution history.
        """
        with self._lock:
            return list(self._execution_history)


# --- SOVEREIGN SINGLETON INSTANCE ---
orchestrator = AutonomousOrchestrator()


if __name__ == "__main__":
    # Institutional self-verification test block
    test_orchestrator = AutonomousOrchestrator()

    cat_repo = getattr(ActionCategory, "REPOSITORY", list(ActionCategory)[0])
    prio_high = getattr(ActionPriority, "HIGH", list(ActionPriority)[-1])

    action = AutonomousAction(
        action_type="SYNC_STATE",
        category=cat_repo,
        target_subsystem="orchestrator/sync",
        priority=prio_high
    )

    summary = test_orchestrator.process_directive(
        title="State Synchronization",
        description="Synchronizes autonomous orchestrator execution state across sub-nodes.",
        actions=[action]
    )

    assert summary is not None, "Orchestration returned null summary."
    assert summary["status"] == "SUCCESS", f"Expected SUCCESS status, got {summary['status']}"
    assert summary["actions_executed"] == 1, "Action execution count mismatch."

    print("✅ AutonomousOrchestrator Self-Verification Passed.")
    print("  - Directive Processing: Verified")
    print("  - Registry & Planner Integration: Verified")
    print("  - Executor Dispatch Pipeline: Verified")
    print("  - Status: GOLD_PRODUCTION_READY")
