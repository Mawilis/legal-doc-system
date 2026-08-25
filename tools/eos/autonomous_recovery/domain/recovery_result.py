"""
===============================================================================
WILSY OS — FG225 AUTONOMOUS RECOVERY ENGINE
DOMAIN SUBSYSTEM: RECOVERY RESULT
===============================================================================

File Path:
    tools/eos/autonomous_recovery/domain/recovery_result.py

Version:
    v225.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Encapsulates the final execution and verification outcome dispatched from 
    the FG222 Reliability Platform back to FG225 reporting and the event bus.

Biblical Worth Billions:
    "The memory of the just is blessed: but the name of the wicked shall rot." 
    — Proverbs 10:7

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
from typing import Dict, Any


class ResultStatus(str, Enum):
    """Final operational status of a recovery execution run."""
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILURE = "FAILURE"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class RecoveryResult:
    """
    Captures post-execution verification metrics and cryptographic evidence 
    certifying the success or failure of an autonomous recovery operation.
    """
    result_id: str = field(default_factory=lambda: f"RES-{uuid.uuid4().hex[:8].upper()}")
    plan_id: str = ""
    incident_id: str = ""
    status: ResultStatus = ResultStatus.FAILURE
    execution_duration_ms: float = 0.0
    verification_passed: bool = False
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon result creation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the result attributes."""
        raw_data = f"{self.result_id}:{self.plan_id}:{self.incident_id}:{self.status}:{self.verification_passed}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the recovery result into a dictionary representation."""
        return {
            "result_id": self.result_id,
            "plan_id": self.plan_id,
            "incident_id": self.incident_id,
            "status": self.status.value,
            "execution_duration_ms": self.execution_duration_ms,
            "verification_passed": self.verification_passed,
            "details": self.details,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
