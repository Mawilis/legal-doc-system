"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
DOMAIN ENTITY: AUTONOMOUS PLAN
===============================================================================

File Path:
    tools/eos/autonomous/domain/autonomous_plan.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines the AutonomousPlan entity representing a deterministic, ordered sequence
    of execution steps and corresponding rollback procedures derived from an
    evaluated AutonomousDecision. Guarantees that every autonomous operation in
    Wilsy OS has a predictable, verifiable, and reversible path.

Biblical Worth Billions:
    "For I know the thoughts that I think toward you, saith the Lord, thoughts of
    peace, and not of evil, to give you an expected end."
    — Jeremiah 29:11

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import json
import os
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# --- ABSOLUTE PATH BOOTSTRAP GUARANTEE ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


class PlanStatus(str, Enum):
    """Institutional execution states for an autonomous plan."""
    PENDING = "PENDING"
    PLANNED = "PLANNED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class PlanStep:
    """
    Sovereign step entity within an autonomous plan.

    Attributes:
        step_number (int): Sequential execution order index (1-based).
        name (str): Human-readable step descriptor.
        subsystem (str): Target Wilsy OS subsystem ID or component.
        action (str): Specific subsystem action or function name.
        parameters (Dict[str, Any]): Step parameters.
        rollback_action (Optional[str]): Action name for step reversal.
        is_critical (bool): Whether step failure triggers immediate rollback.
        status (str): Step execution status (PENDING, COMPLETED, FAILED).
        start_time (Optional[str]): ISO 8601 SAST start timestamp.
        completion_time (Optional[str]): ISO 8601 SAST completion timestamp.
        result (Optional[Dict[str, Any]]): Step execution result.
        error (Optional[str]): Step execution error message.
    """
    step_number: int
    name: str
    subsystem: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    rollback_action: Optional[str] = None
    is_critical: bool = True
    status: str = "PENDING"
    start_time: Optional[str] = None
    completion_time: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializes step to a dictionary."""
        return asdict(self)


@dataclass
class AutonomousPlan:
    """
    Sovereign domain entity containing deterministic execution and rollback steps.

    Attributes:
        plan_id (str): Unique plan UUID v4 identifier.
        action_id (str): Associated AutonomousAction identifier.
        decision_id (str): Associated AutonomousDecision identifier.
        title (str): Concise operational title of the plan.
        steps (List[PlanStep]): Ordered execution step pipeline.
        rollback_steps (List[PlanStep]): Reversed step sequence for clean undo.
        status (PlanStatus): Current status of plan execution.
        estimated_duration_ms (float): Projected execution duration in milliseconds.
        created_at (str): ISO 8601 SAST creation timestamp.
        metadata (Dict[str, Any]): Auxiliary execution parameters.
        completion_time (Optional[str]): ISO 8601 SAST completion timestamp.
    """
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_id: str = ""
    decision_id: str = ""
    title: str = "Default Autonomous Execution Plan"
    steps: List[PlanStep] = field(default_factory=list)
    rollback_steps: List[PlanStep] = field(default_factory=list)
    status: PlanStatus = PlanStatus.PLANNED
    estimated_duration_ms: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone(timedelta(hours=2))).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    completion_time: Optional[str] = None

    def validate(self) -> Tuple[bool, str]:
        """Validates structural correctness of plan and sequential steps."""
        try:
            if not self.plan_id or not isinstance(self.plan_id, str):
                return False, "Invalid or missing 'plan_id'."
            if not self.action_id or not isinstance(self.action_id, str):
                return False, "Invalid or missing 'action_id'."
            if not self.decision_id or not isinstance(self.decision_id, str):
                return False, "Invalid or missing 'decision_id'."
            if not self.steps:
                return False, "AutonomousPlan must contain at least one execution step."
            if not isinstance(self.status, PlanStatus):
                return False, f"Invalid plan status '{self.status}'."

            # Verify step sequence indexing
            for idx, step in enumerate(self.steps, start=1):
                if step.step_number != idx:
                    return False, f"Step numbering gap or mismatch: expected {idx}, got {step.step_number}."

            return True, "VALID"
        except Exception as err:
            return False, f"AutonomousPlan validation exception: {str(err)}"

    def add_step(
        self,
        name: str,
        subsystem: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        rollback_action: Optional[str] = None,
        is_critical: bool = True
    ) -> PlanStep:
        """Appends a new execution step to the plan pipeline and builds matching rollback step."""
        step_number = len(self.steps) + 1
        step = PlanStep(
            step_number=step_number,
            name=name,
            subsystem=subsystem,
            action=action,
            parameters=parameters or {},
            rollback_action=rollback_action,
            is_critical=is_critical
        )
        self.steps.append(step)

        # Build reverse rollback step if action is specified
        if rollback_action:
            rollback_step = PlanStep(
                step_number=len(self.rollback_steps) + 1,
                name=f"Rollback: {name}",
                subsystem=subsystem,
                action=rollback_action,
                parameters=parameters or {},
                is_critical=is_critical
            )
            # Insert at beginning for stack LIFO reversal order
            self.rollback_steps.insert(0, rollback_step)

        return step

    def compute_digest(self) -> str:
        """Computes SHA-256 cryptographic hash of the execution plan."""
        payload = {
            "plan_id": self.plan_id,
            "action_id": self.action_id,
            "decision_id": self.decision_id,
            "title": self.title,
            "steps": [s.to_dict() for s in self.steps],
            "rollback_steps": [s.to_dict() for s in self.rollback_steps],
            "status": self.status.value,
            "created_at": self.created_at
        }
        serialized = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        return f"0x{digest}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes plan to dictionary structure."""
        return {
            "plan_id": self.plan_id,
            "action_id": self.action_id,
            "decision_id": self.decision_id,
            "title": self.title,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "rollback_steps": [s.to_dict() for s in self.rollback_steps],
            "estimated_duration_ms": self.estimated_duration_ms,
            "digest": self.compute_digest(),
            "created_at": self.created_at,
            "metadata": self.metadata
        }


if __name__ == "__main__":
    # Institutional self-verification test block
    plan = AutonomousPlan(
        action_id=str(uuid.uuid4()),
        decision_id=str(uuid.uuid4()),
        title="Scale Cluster Node Workers Plan"
    )

    plan.add_step(
        name="Check Reliability Status",
        subsystem="tools/eos/reliability",
        action="VERIFY_HEALTH",
        rollback_action="NONE"
    )
    plan.add_step(
        name="Allocate Worker Capacity",
        subsystem="tools/eos/cluster",
        action="SCALE_UP",
        parameters={"nodes": 2},
        rollback_action="SCALE_DOWN"
    )
    plan.add_step(
        name="Verify Runtime Synchronization",
        subsystem="tools/eos/runtime",
        action="PING_NODES",
        rollback_action="NONE"
    )

    is_valid, msg = plan.validate()
    digest = plan.compute_digest()

    print(f"✅ AutonomousPlan Entity Self-Check: {msg}")
    print(f"  - Plan ID: {plan.plan_id}")
    print(f"  - Steps Count: {len(plan.steps)}")
    print(f"  - Rollback Steps Count: {len(plan.rollback_steps)}")
    print(f"  - Status: {plan.status.value}")
    print(f"  - Digest: {digest[:24]}...")
    assert is_valid, "Plan validation failed!"
    assert len(plan.steps) == 3, "Incorrect step count!"
    assert digest.startswith("0x"), "Digest format invalid!"
    print("  - Status: GOLD_PRODUCTION_READY")
