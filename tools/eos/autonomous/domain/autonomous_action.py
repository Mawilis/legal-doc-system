"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
DOMAIN ENTITY: AUTONOMOUS ACTION
===============================================================================

File Path:
    tools/eos/autonomous/domain/autonomous_action.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines the core AutonomousAction domain entity representing an operational
    intent or requested task (e.g., Repository Scan, Documentation Generation,
    Snapshot Restore, Cluster Scaling) within Wilsy OS. Acts as the immutable
    input entity for policy evaluation, risk scoring, and execution planning.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, and
    counteth the cost, whether he have sufficient to finish it?"
    — Luke 14:28

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, Tuple


class ActionCategory(str, Enum):
    """Categorization of autonomous operational intents."""
    REPOSITORY = "REPOSITORY"
    DOCUMENTATION = "DOCUMENTATION"
    MARKETPLACE = "MARKETPLACE"
    CLUSTER = "CLUSTER"
    RELIABILITY = "RELIABILITY"
    GOVERNANCE = "GOVERNANCE"
    SNAPSHOT = "SNAPSHOT"
    GENERAL = "GENERAL"


class ActionPriority(str, Enum):
    """Priority levels for autonomous queue dispatch."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class AutonomousAction:
    """
    Sovereign domain entity encapsulating an intentional system operation.
    
    Attributes:
        action_type (str): Operational descriptor (e.g., REPOSITORY_SCAN, SCALE_CLUSTER).
        category (ActionCategory): Operational subsystem grouping.
        target_subsystem (str): Target Wilsy OS subsystem ID or path.
        priority (ActionPriority): Execution urgency level.
        parameters (Dict[str, Any]): Operation-specific execution arguments.
        requested_by (str): Initiator identifier (System, Digital Twin, Executive).
        action_id (str): Unique UUID v4 action identifier.
        created_at (str): ISO 8601 SAST creation timestamp.
        metadata (Dict[str, Any]): Auxiliary contextual attributes.
    """
    action_type: str
    category: ActionCategory
    target_subsystem: str
    priority: ActionPriority = ActionPriority.MEDIUM
    parameters: Dict[str, Any] = field(default_factory=dict)
    requested_by: str = "WilsyOS.AutonomousEngine"
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone(timedelta(hours=2))).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> Tuple[bool, str]:
        """
        Validates structural integrity and required field constraints.

        Returns:
            Tuple[bool, str]: (True, "VALID") or (False, error_reason).
        """
        try:
            if not self.action_id or not isinstance(self.action_id, str):
                return False, "Invalid or missing 'action_id'."
            if not self.action_type or not isinstance(self.action_type, str):
                return False, "Invalid or missing 'action_type'."
            if not isinstance(self.category, ActionCategory):
                return False, f"Invalid category '{self.category}'. Must be an instance of ActionCategory."
            if not self.target_subsystem or not isinstance(self.target_subsystem, str):
                return False, "Invalid or missing 'target_subsystem'."
            if not isinstance(self.parameters, dict):
                return False, "'parameters' must be a valid dictionary."
            return True, "VALID"
        except Exception as err:
            return False, f"Validation exception encountered: {str(err)}"

    def compute_digest(self) -> str:
        """
        Calculates an immutable SHA-256 cryptographic digest of the action entity payload.

        Returns:
            str: 64-character hexadecimal SHA-256 hash string prefixed with '0x'.
        """
        payload = {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "category": self.category.value if isinstance(self.category, ActionCategory) else str(self.category),
            "target_subsystem": self.target_subsystem,
            "priority": self.priority.value if isinstance(self.priority, ActionPriority) else str(self.priority),
            "parameters": self.parameters,
            "requested_by": self.requested_by,
            "created_at": self.created_at
        }
        serialized = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        return f"0x{digest}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes domain entity to a JSON-compatible dictionary."""
        data = asdict(self)
        data["category"] = self.category.value
        data["priority"] = self.priority.value
        data["digest"] = self.compute_digest()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutonomousAction":
        """Reconstructs domain entity from a dictionary payload with defensive parsing."""
        kwargs = dict(data)
        kwargs.pop("digest", None)
        
        if "category" in kwargs and isinstance(kwargs["category"], str):
            kwargs["category"] = ActionCategory(kwargs["category"])
        if "priority" in kwargs and isinstance(kwargs["priority"], str):
            kwargs["priority"] = ActionPriority(kwargs["priority"])
            
        return cls(**kwargs)


if __name__ == "__main__":
    # Institutional self-verification test block
    test_action = AutonomousAction(
        action_type="REPOSITORY_SCAN",
        category=ActionCategory.REPOSITORY,
        target_subsystem="tools/eos/repository",
        priority=ActionPriority.HIGH,
        parameters={"depth": "full", "include_uncommitted": False},
        requested_by="WilsyOS.DigitalTwin"
    )
    
    is_valid, msg = test_action.validate()
    digest = test_action.compute_digest()
    
    print(f"✅ AutonomousAction Entity Self-Check: {msg}")
    print(f"  - Action ID: {test_action.action_id}")
    print(f"  - Category: {test_action.category.value}")
    print(f"  - Digest: {digest[:24]}...")
    assert is_valid, "Entity validation failed!"
    assert digest.startswith("0x"), "Digest format invalid!"
    print("  - Status: GOLD_PRODUCTION_READY")
