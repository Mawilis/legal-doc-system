"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Sovereign event data models defining enterprise signals, event contract 
    structures, propagation metadata, and nervous system event topologies.

Biblical Worth Billions:
    "And there were voices, and thunders, and lightnings; and there was a great 
    earthquake, such as was not since men were upon the earth, so mighty an 
    earthquake, and so great." — Revelation 16:18

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/event_graph/event_models.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional


class EventSeverity(str, Enum):
    """Severity classification tiers for enterprise nervous system events."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SOVEREIGN = "SOVEREIGN"


@dataclass
class EnterpriseEvent:
    """
    Core data structure representing an immutable signal propagated across the platform.
    """
    event_id: str
    event_type: str
    source_capability: str
    payload: Dict[str, Any]
    severity: EventSeverity = EventSeverity.INFO
    propagation_depth: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Converts event instance into serializable dictionary."""
        data = asdict(self)
        data["severity"] = self.severity.value if isinstance(self.severity, EventSeverity) else str(self.severity)
        return data


@dataclass
class EventGraphTopology:
    """
    Master container recording active event subscriptions, event channels, and signal paths.
    """
    registered_events: List[str] = field(default_factory=list)
    subscriptions: Dict[str, List[str]] = field(default_factory=dict)  # event_type -> list of consuming capabilities

    def register_event(self, event_type: str) -> None:
        """Registers a unique event channel into the topology index."""
        if event_type not in self.registered_events:
            self.registered_events.append(event_type)

    def add_subscription(self, event_type: str, capability_id: str) -> None:
        """Binds a consuming capability to an event channel."""
        self.register_event(event_type)
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []
        if capability_id not in self.subscriptions[event_type]:
            self.subscriptions[event_type].append(capability_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the event topology into a dictionary."""
        return {
            "total_registered_events": len(self.registered_events),
            "registered_events": self.registered_events,
            "subscriptions": self.subscriptions,
        }