"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
DOMAIN ENTITY: AUTONOMOUS RESULT
===============================================================================

File Path:
    tools/eos/autonomous/domain/autonomous_result.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines the AutonomousResult domain entity encapsulating the immutable, 
    verifiable outcome of an AutonomousPlan execution run. Captures step summaries,
    rollback telemetry, execution metrics, and SHA-256 cryptographic digests.

Biblical Worth Billions:
    "Verily, verily, I say unto you, He that heareth my word, and believeth on him 
    that sent me, hath everlasting life, and shall not come into condemnation; 
    but is passed from death unto life."
    — John 5:24

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
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

# --- ABSOLUTE PATH BOOTSTRAP GUARANTEE ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tools.eos.autonomous.domain.autonomous_plan import PlanStatus


@dataclass
class AutonomousResult:
    """
    Domain Entity representing the immutable result of an executed AutonomousPlan.
    """
    plan_id: str
    action_id: str
    decision_id: str
    success: bool
    final_status: PlanStatus
    steps_completed: int
    steps_total: int
    rollback_performed: bool = False
    rollback_successful: Optional[bool] = None
    execution_duration_ms: float = 0.0
    message: str = ""
    error_details: Optional[str] = None
    telemetry: Dict[str, Any] = field(default_factory=dict)
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone(timedelta(hours=2))).isoformat()
    )

    def validate(self) -> Tuple[bool, str]:
        """
        Validates structural invariants of the AutonomousResult entity.
        """
        if not self.result_id or not isinstance(self.result_id, str):
            return False, "Invalid or missing 'result_id'."
        if not self.plan_id or not isinstance(self.plan_id, str):
            return False, "Invalid or missing 'plan_id'."
        if not self.action_id or not isinstance(self.action_id, str):
            return False, "Invalid or missing 'action_id'."
        if self.steps_total < 0:
            return False, "'steps_total' cannot be negative."
        if self.steps_completed < 0 or self.steps_completed > self.steps_total:
            return False, f"Invalid 'steps_completed' ({self.steps_completed}) for total ({self.steps_total})."
        if self.execution_duration_ms < 0.0:
            return False, "'execution_duration_ms' cannot be negative."

        return True, "AutonomousResult invariants verified."

    def compute_digest(self) -> str:
        """
        Computes an immutable cryptographic SHA-256 digest of the result.
        """
        payload = {
            "result_id": self.result_id,
            "plan_id": self.plan_id,
            "action_id": self.action_id,
            "decision_id": self.decision_id,
            "success": self.success,
            "final_status": self.final_status.value if hasattr(self.final_status, "value") else str(self.final_status),
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "rollback_performed": self.rollback_performed,
            "execution_duration_ms": round(self.execution_duration_ms, 4),
            "created_at": self.created_at,
        }
        serialized = json.dumps(payload, sort_keys=True)
        return "0x" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the result entity to a dictionary.
        """
        return {
            "result_id": self.result_id,
            "plan_id": self.plan_id,
            "action_id": self.action_id,
            "decision_id": self.decision_id,
            "success": self.success,
            "final_status": self.final_status.value if hasattr(self.final_status, "value") else str(self.final_status),
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "rollback_performed": self.rollback_performed,
            "rollback_successful": self.rollback_successful,
            "execution_duration_ms": self.execution_duration_ms,
            "message": self.message,
            "error_details": self.error_details,
            "telemetry": self.telemetry,
            "created_at": self.created_at,
            "digest": self.compute_digest(),
        }


if __name__ == "__main__":
    # Institutional self-verification block
    result = AutonomousResult(
        plan_id=str(uuid.uuid4()),
        action_id=str(uuid.uuid4()),
        decision_id=str(uuid.uuid4()),
        success=True,
        final_status=PlanStatus.COMPLETED,
        steps_completed=3,
        steps_total=3,
        execution_duration_ms=42.15,
        message="Execution completed with zero invariant violations."
    )

    valid, err = result.validate()
    print(f"✅ AutonomousResult Self-Check Validation: {err}")
    print(f"  - Result ID: {result.result_id}")
    print(f"  - Success: {result.success}")
    print(f"  - Digest: {result.compute_digest()[:24]}...")

    assert valid is True, f"Validation failed: {err}"
    assert result.compute_digest().startswith("0x"), "Digest format invalid!"
    print("  - Status: GOLD_PRODUCTION_READY")
