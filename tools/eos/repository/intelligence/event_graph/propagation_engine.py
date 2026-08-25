"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Sovereign event propagation and dispatch engine executing real-time event
    routing, listener activation, and dispatch trace logging across Wilsy OS.

Biblical Worth Billions:
    "Their sound went into all the earth, and their words unto the ends of the world."
    — Romans 10:18

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy OS)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/event_graph/propagation_engine.py
===============================================================================
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Tuple
from.event_models import EnterpriseEvent, EventGraphTopology

logger = logging.getLogger("WilsyOS.FG231C.EventPropagationEngine")


class EventPropagationEngine:
    """
    Sovereign event routing engine that dispatches events to subscribed
    capabilities and records the complete propagation audit trace.
    """

    def __init__(self, topology: EventGraphTopology) -> None:
        self.topology = topology
        self.propagation_log: List[Dict[str, Any]] = []

    def dispatch_event(self, event: EnterpriseEvent) -> Tuple[int, List[str]]:
        """
        Dispatches an enterprise signal through the registered topology handlers.
        Returns a tuple of (consumed_count, target_capability_ids).
        """
        target_capabilities = self.topology.subscriptions.get(event.event_type, [])
        consumed_count = len(target_capabilities)

        trace_entry = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "source_capability": event.source_capability,
            "targets_notified": target_capabilities,
            "consumed_count": consumed_count,
            "timestamp": event.timestamp,
        }
        self.propagation_log.append(trace_entry)

        logger.info(
            "Event %s [%s] dispatched from %s -> notified %d targets: %s",
            event.event_id,
            event.event_type,
            event.source_capability,
            consumed_count,
            target_capabilities,
        )

        return consumed_count, target_capabilities

    def get_propagation_history(self) -> List[Dict[str, Any]]:
        """Retrieves the full event propagation history log."""
        return self.propagation_log