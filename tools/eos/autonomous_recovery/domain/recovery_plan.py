"""
===============================================================================
WILSY OS — FG225 AUTONOMOUS RECOVERY ENGINE
DOMAIN SUBSYSTEM: RECOVERY PLAN
===============================================================================

File Path:
    tools/eos/autonomous_recovery/domain/recovery_plan.py

Version:
    v225.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines deterministic recovery plans, outlining sequential execution steps 
    and rollback compensatory hooks dispatched to the FG222 Reliability Platform.

Biblical Worth Billions:
    "A man's heart deviseth his way: but the Lord directeth his steps." 
    — Proverbs 16:9

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional


class PlanStatus(str, Enum):
    """Execution status of an autonomous recovery plan."""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class RecoveryStep:
    """Represents a single atomic execution step within a recovery plan."""
    step_id: str = field(default_factory=lambda: f"STEP-{uuid.uuid4().hex[:6].upper()}")
    action_type: str = "RESTART_WORKER"
    target: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_completed: bool = False
    error_message: str = ""


@dataclass
class RecoveryPlan:
    """
    Encapsulates a deterministic sequence of recovery steps mapped to an incident,
    ensuring safe orchestration without duplicating FG222 infrastructure logic.
    """
    plan_id: str = field(default_factory=lambda: f"PLAN-{uuid.uuid4().hex[:8].upper()}")
    incident_id: str = ""
    strategy_name: str = "DEFAULT_RECOVERY"
    steps: List[RecoveryStep] = field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon plan creation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the plan attributes."""
        step_signatures = "".join([s.step_id for s in self.steps])
        raw_data = f"{self.plan_id}:{self.incident_id}:{self.strategy_name}:{step_signatures}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def add_step(self, action_type: str, target: str, parameters: Optional[Dict[str, Any]] = None) -> RecoveryStep:
        """Appends an atomic execution step to the recovery plan."""
        step = RecoveryStep(action_type=action_type, target=target, parameters=parameters or {})
        self.steps.append(step)
        self.checksum = self._compute_checksum()
        return step

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the recovery plan into a dictionary representation."""
        return {
            "plan_id": self.plan_id,
            "incident_id": self.incident_id,
            "strategy_name": self.strategy_name,
            "steps": [
                {
                    "step_id": s.step_id,
                    "action_type": s.action_type,
                    "target": s.target,
                    "parameters": s.parameters,
                    "is_completed": s.is_completed,
                    "error_message": s.error_message
                } for s in self.steps
            ],
            "status": self.status.value,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
