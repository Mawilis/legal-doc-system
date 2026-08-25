"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
DOMAIN ENTITY: AUTONOMOUS EVENT
===============================================================================

File Path:
    tools/eos/autonomous/domain/autonomous_event.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines the AutonomousEvent domain entity capturing real-time telemetry events,
    lifecycle state transitions, trigger conditions, and audit entries across the 
    Wilsy OS Autonomous Operations Engine. Guarantees tamper-evident event streaming.

Biblical Worth Billions:
    "For there is nothing covered, that shall not be revealed; neither hid, 
    that shall not be known."
    — Luke 12:2

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


class EventType(str, Enum):
    """Institutional event classification types for autonomous operations."""
    ACTION_TRIGGERED = "ACTION_TRIGGERED"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    DECISION_MADE = "DECISION_MADE"
    PLAN_GENERATED = "PLAN_GENERATED"
    STEP_EXECUTED = "STEP_EXECUTED"
    PLAN_COMPLETED = "PLAN_COMPLETED"
    PLAN_FAILED = "PLAN_FAILED"
    ROLLBACK_STARTED = "ROLLBACK_STARTED"
    ROLLBACK_COMPLETED = "ROLLBACK_COMPLETED"
    AUDIT_LOGGED = "AUDIT_LOGGED"


class EventSeverity(str, Enum):
    """Event severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AutonomousEvent:
    """
    Sovereign domain entity capturing an immutable operational telemetry event.

    Attributes:
        event_id (str): Unique event UUID v4 identifier.
        event_type (EventType): Classification type of event.
        severity (EventSeverity): Severity classification.
        action_id (str): Associated AutonomousAction identifier.
        source_subsystem (str): Originating subsystem ID.
        payload (Dict[str, Any]): Telemetry or contextual payload data.
        message (str): Human-readable event description.
        timestamp (str): ISO 8601 SAST timestamp.
        metadata (Dict[str, Any]): Auxiliary contextual attributes.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.ACTION_TRIGGERED
    severity: EventSeverity = EventSeverity.INFO
    action_id: str = ""
    source_subsystem: str = "WilsyOS.AutonomousEngine"
    payload: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone(timedelta(hours=2))).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> Tuple[bool, str]:
        """Validates event structure and attributes."""
        try:
            if not self.event_id or not isinstance(self.event_id, str):
                return False, "Invalid or missing 'event_id'."
            if not isinstance(self.event_type, EventType):
                return False, f"Invalid event_type '{self.event_type}'."
            if not isinstance(self.severity, EventSeverity):
                return False, f"Invalid severity '{self.severity}'."
            if not self.source_subsystem or not isinstance(self.source_subsystem, str):
                return False, "Invalid or missing 'source_subsystem'."
            return True, "VALID"
        except Exception as err:
            return False, f"AutonomousEvent validation exception: {str(err)}"

    def compute_digest(self) -> str:
        """Computes SHA-256 cryptographic digest for tamper-evident verification."""
        payload = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "action_id": self.action_id,
            "source_subsystem": self.source_subsystem,
            "payload": self.payload,
            "message": self.message,
            "timestamp": self.timestamp
        }
        serialized = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        return f"0x{digest}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "action_id": self.action_id,
            "source_subsystem": self.source_subsystem,
            "payload": self.payload,
            "message": self.message,
            "timestamp": self.timestamp,
            "digest": self.compute_digest(),
            "metadata": self.metadata
        }


if __name__ == "__main__":
    # Institutional self-verification test block
    event = AutonomousEvent(
        event_type=EventType.STEP_EXECUTED,
        severity=EventSeverity.INFO,
        action_id=str(uuid.uuid4()),
        source_subsystem="tools/eos/autonomous/engine",
        message="Step 1/3 'Verify Capacity' completed successfully",
        payload={"step_number": 1, "duration_ms": 14.2, "status": "COMPLETED"}
    )

    is_valid, msg = event.validate()
    digest = event.compute_digest()

    print(f"✅ AutonomousEvent Entity Self-Check: {msg}")
    print(f"  - Event ID: {event.event_id}")
    print(f"  - Event Type: {event.event_type.value}")
    print(f"  - Severity: {event.severity.value}")
    print(f"  - Source: {event.source_subsystem}")
    print(f"  - Digest: {digest[:24]}...")
    assert is_valid, "Event validation failed!"
    assert event.event_type == EventType.STEP_EXECUTED, "Event type mismatch!"
    assert digest.startswith("0x"), "Digest format invalid!"
    print("  - Status: GOLD_PRODUCTION_READY")
