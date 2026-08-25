"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Enterprise Event Graph Engine establishing platform event subscriptions, 
    managing asynchronous event propagation topologies, and dispatching live system signals.

Biblical Worth Billions:
    "And I heard as it were the voice of a great multitude, and as the voice of 
    many waters, and as the voice of mighty thunderings, saying, Alleluia: for 
    the Lord God omnipotent reigneth." — Revelation 19:6

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/event_graph/event_graph_engine.py
===============================================================================
"""

from __future__ import annotations

import json
import os
import logging
from typing import Dict, Any

from.event_models import EnterpriseEvent, EventSeverity, EventGraphTopology
from.propagation_engine import EventPropagationEngine

logger = logging.getLogger("WilsyOS.FG231C.EventGraphEngine")


class EventGraphEngine:
    """
    Sovereign event graph engine responsible for configuring enterprise event 
    subscriptions, routing system signals, and persisting event graph execution traces.
    """

    def __init__(self, primary_output_path: str = "reports/EventGraph.json") -> None:
        self.primary_output_path = primary_output_path
        self.topology = EventGraphTopology()

    def build_core_event_topology(self) -> EventGraphTopology:
        """
        Configures subscriptions between enterprise event triggers and consuming capabilities.
        """
        # Event: SCAN_TRIGGERED
        self.topology.add_subscription("SCAN_TRIGGERED", "CAP-REPOSITORY-SCAN")

        # Event: REPOSITORY_CHANGED
        self.topology.add_subscription("REPOSITORY_CHANGED", "CAP-KNOWLEDGE-SYNCHRONIZATION")
        self.topology.add_subscription("REPOSITORY_CHANGED", "CAP-PREDICTION-RISK-ASSESSMENT")
        self.topology.add_subscription("REPOSITORY_CHANGED", "CAP-GOVERNANCE-COMPLIANCE")

        # Event: KNOWLEDGE_REFRESHED
        self.topology.add_subscription("KNOWLEDGE_REFRESHED", "CAP-PREDICTION-RISK-ASSESSMENT")

        # Event: RISK_RECALCULATED
        self.topology.add_subscription("RISK_RECALCULATED", "CAP-GOVERNANCE-COMPLIANCE")

        # Event: GOVERNANCE_VERIFIED
        self.topology.add_subscription("GOVERNANCE_VERIFIED", "CAP-CONTROL-ROOM-DISPATCH")

        # Event: TWIN_UPDATED
        self.topology.add_subscription("TWIN_UPDATED", "CAP-CONTROL-ROOM-DISPATCH")

        return self.topology

    def simulate_event_propagation(self, propagation_engine: EventPropagationEngine) -> Dict[str, Any]:
        """
        Simulates primary event propagation run to verify event graph routing integrity.
        """
        test_event = EnterpriseEvent(
            event_id="EVT-SIM-001",
            event_type="REPOSITORY_CHANGED",
            source_capability="CAP-REPOSITORY-SCAN",
            payload={"commit_hash": "a1b2c3d4", "files_changed": 12},
            severity=EventSeverity.CRITICAL,
        )

        consumed_count, targets = propagation_engine.dispatch_event(test_event)
        return {
            "simulation_event_id": test_event.event_id,
            "event_type": test_event.event_type,
            "target_count": consumed_count,
            "notified_capabilities": targets,
        }

    def execute_and_save(self) -> Dict[str, Any]:
        """
        Executes event topology creation, simulates event routing, and persists JSON artifacts.
        """
        logger.info("Executing Event Graph Engine...")
        self.build_core_event_topology()

        propagation_engine = EventPropagationEngine(self.topology)
        sim_result = self.simulate_event_propagation(propagation_engine)

        topology_dict = self.topology.to_dict()
        topology_dict["simulation_result"] = sim_result
        topology_dict["propagation_history"] = propagation_engine.get_propagation_history()

        # Primary persistence target (reports/)
        os.makedirs(os.path.dirname(self.primary_output_path), exist_ok=True)
        with open(self.primary_output_path, "w", encoding="utf-8") as f:
            json.dump(topology_dict, f, indent=2)

        # Local module mirror target
        local_dir = os.path.dirname(__file__)
        local_target = os.path.join(local_dir, "event_graph.json")
        with open(local_target, "w", encoding="utf-8") as f:
            json.dump(topology_dict, f, indent=2)

        logger.info(
            "Successfully configured event graph with %d registered events.",
            len(self.topology.registered_events),
        )
        return topology_dict