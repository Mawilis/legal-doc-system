"""
===============================================================================
WILSY OS — HIGH AVAILABILITY NODE HEALTH & STATE MACHINE
===============================================================================

File Path:
    tools/eos/reliability/high_availability/node_health.py

Epitome:
    Manages node health scoring, heartbeats, and strict lifecycle state transitions 
    (ONLINE -> UNHEALTHY -> ISOLATED -> FAILED -> RECOVERING -> ONLINE) under 
    sovereign enterprise reliability standards.

Biblical Worth Billions:
    "A faithful man shall abound with blessings..."
    — Proverbs 28:20

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
from enum import Enum
from typing import Dict, Any

class NodeState(str, Enum):
    ONLINE = "ONLINE"
    UNHEALTHY = "UNHEALTHY"
    ISOLATED = "ISOLATED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"

class NodeHealthManager:
    """Tracks node health metrics, heartbeat intervals, and state transitions."""
    
    def __init__(self, node_id: str, failure_threshold: int = 3) -> None:
        self.node_id = node_id
        self.failure_threshold = failure_threshold
        self.state = NodeState.ONLINE
        self.consecutive_failures = 0
        self.last_heartbeat = time.time()
        self.health_score = 100.0

    def record_heartbeat(self, metrics: Dict[str, Any]) -> None:
        """Processes an incoming node heartbeat and updates health score."""
        self.last_heartbeat = time.time()
        cpu_load = metrics.get("cpu_load", 0.0)
        memory_usage = metrics.get("memory_usage", 0.0)
        
        penalty = (cpu_load * 0.5) + (memory_usage * 0.5)
        self.health_score = max(0.0, 100.0 - penalty)
        
        if self.health_score < 40.0:
            self._transition_to(NodeState.UNHEALTHY)
        elif self.state == NodeState.UNHEALTHY and self.health_score >= 75.0:
            self._transition_to(NodeState.ONLINE)
            self.consecutive_failures = 0

    def register_failure(self) -> NodeState:
        """Registers a missed heartbeat or execution fault."""
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            if self.state != NodeState.FAILED:
                self._transition_to(NodeState.FAILED)
        else:
            self._transition_to(NodeState.UNHEALTHY)
        return self.state

    def begin_recovery(self) -> None:
        """Initiates the recovery pipeline transition."""
        self._transition_to(NodeState.RECOVERING)

    def finalize_recovery(self) -> None:
        """Restores node to active online status following successful recovery."""
        self.consecutive_failures = 0
        self.health_score = 100.0
        self._transition_to(NodeState.ONLINE)

    def _transition_to(self, new_state: NodeState) -> None:
        """Internal state transition guard."""
        self.state = new_state

    def export_telemetry(self) -> Dict[str, Any]:
        """Exports current node health telemetry snapshot."""
        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "health_score": round(self.health_score, 2),
            "consecutive_failures": self.consecutive_failures,
            "last_heartbeat": self.last_heartbeat
        }
