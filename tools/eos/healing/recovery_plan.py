"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Self Healing - Recovery Plan Architecture (FG155).
    Defines the immutable blueprint for resolving runtime anomalies, detailing
    patch instructions, rollback requirements, and execution sequences.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready recovery blueprint engine. Zero child's place.
    Jeremiah 30:17 - "For I will restore health to you, and your wounds I will heal, declares the Lord."

Collaboration & Maintenance:
    - [Architecture]: Immutable dataclass representing a systemic recovery blueprint.
    - [Compliance]: Cryptographically distinct plan IDs for audit and journaling.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List


class RecoveryStatus(str, Enum):
    """Lifecycle states of a recovery plan."""
    DRAFTED = "DRAFTED"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class RecoveryPlan:
    """
    Immutable structured plan for system recovery, patching, and verification.
    """
    plan_id: str
    timestamp: str
    issue_context: Dict[str, Any]
    action_steps: List[str]
    requires_rollback: bool
    estimated_success_rate: float
    status: RecoveryStatus = field(default=RecoveryStatus.DRAFTED)

    # [FUNCTION EXPLANATION]: Factory constructor to dynamically generate a recovery strategy.
    @classmethod
    def generate(
        cls, 
        issue_context: Dict[str, Any], 
        predicted_failure_mode: str, 
        severity: str
    ) -> RecoveryPlan:
        """
        Synthesizes a new recovery plan based on the failure context and severity.

        Args:
            issue_context (Dict[str, Any]): Telemetry and context of the fault.
            predicted_failure_mode (str): The specific mode of failure identified.
            severity (str): Assessed severity (e.g., LOW, HIGH, CATASTROPHIC).

        Returns:
            RecoveryPlan: A securely formulated blueprint for autonomous healing.
        """
        plan_id = f"heal-plan-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Formulate action steps dynamically
        steps: List[str] = ["ISOLATE_FAULT_DOMAIN", "CAPTURE_MEMORY_DUMP"]
        requires_rollback = False
        success_rate = 0.95

        if severity == "CATASTROPHIC" or predicted_failure_mode == "SYSTEM_INSTABILITY_OR_TIMEOUT":
            steps.extend(["INITIATE_FULL_ROLLBACK", "RE_INITIALIZE_KERNEL", "VERIFY_SYSTEM_INTEGRITY"])
            requires_rollback = True
            success_rate = 0.70
        elif severity == "HIGH":
            steps.extend(["APPLY_HOTFIX_PATCH", "RE_RUN_EXECUTION_STEP", "VERIFY_STATE_CHANGES"])
            success_rate = 0.85
        else:
            steps.extend(["FLUSH_CACHE", "RETRY_WITH_BACKOFF", "CONTINUE_EXECUTION"])

        return cls(
            plan_id=plan_id,
            timestamp=timestamp,
            issue_context=issue_context,
            action_steps=steps,
            requires_rollback=requires_rollback,
            estimated_success_rate=success_rate,
        )

    # [FUNCTION EXPLANATION]: Upgrades the plan's status, returning a new immutable instance.
    def transition_status(self, new_status: RecoveryStatus) -> RecoveryPlan:
        """
        Transitions the recovery plan to a new status state, returning a new frozen instance
        to maintain immutability.
        """
        data = asdict(self)
        data["status"] = new_status
        return RecoveryPlan(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the recovery plan to a standard dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serializes the recovery plan to a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
