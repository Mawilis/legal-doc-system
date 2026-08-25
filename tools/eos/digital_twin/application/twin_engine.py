"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/application/twin_engine.py

Epitome:
    Core application orchestration engine for the Digital Twin Platform.
    Synthesizes observational telemetry from all Wilsy OS subsystems into a 
    living topology graph. Publishes architectural drift events to Event Bus.

Biblical Worth Billions:
    "I wisdom dwell with prudence, and find out knowledge of witty inventions."
    — Proverbs 8:12

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
import logging
from typing import Dict, List, Any, Optional
from tools.eos.digital_twin.domain.twin_entity import TwinEntity
from tools.eos.digital_twin.domain.twin_relationship import TwinRelationship
from tools.eos.digital_twin.domain.twin_state import TwinState
from tools.eos.digital_twin.domain.twin_state_graph import TwinStateGraph
from tools.eos.digital_twin.domain.twin_query import TwinQuery, TwinQueryResult

logger = logging.getLogger("WilsyOS.DigitalTwin.Engine")


class TwinEngine:
    """
    Central operational engine for the FG223 Digital Twin Intelligence Platform.
    """

    def __init__(
        self,
        execution_context: Optional[Any] = None,
        event_bus: Optional[Any] = None,
        state_graph: Optional[Any] = None
    ):
        self._execution_context = execution_context
        self._event_bus = event_bus
        self._state = state_graph if state_graph is not None else TwinStateGraph()
        self._initialized_at = time.time()
        self._telemetry_counter = {
            "entities_registered": 0,
            "relationships_registered": 0,
            "drift_events_emitted": 0,
            "queries_executed": 0
        }

    @property
    def state(self) -> TwinState:
        return self._state

    @property
    def telemetry(self) -> Dict[str, Any]:
        return {
            "uptime_seconds": round(time.time() - self._initialized_at, 4),
            "entity_count": self._state.entity_count,
            "relationship_count": self._state.relationship_count,
            "drift_count": self._state.drift_count,
            "counters": self._telemetry_counter
        }

    def register_entity(self, entity_id: str, entity_type: str, attributes: Dict[str, Any]) -> TwinEntity:
        try:
            entity = TwinEntity(entity_id=entity_id, entity_type=entity_type, attributes=attributes)
            is_drift = self._state.upsert_entity(entity)
            self._telemetry_counter["entities_registered"] += 1

            if is_drift:
                self._emit_event("TwinRiskDetected", {
                    "event_type": "ENTITY_DRIFT",
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "state_hash": entity.state_hash
                })
                self._telemetry_counter["drift_events_emitted"] += 1

            return entity
        except Exception as e:
            logger.error(f"Failed to register entity [{entity_id}]: {str(e)}")
            raise RuntimeError(f"TwinEngine entity registration failure: {str(e)}")

    def register_relationship(
        self,
        relationship_id: str,
        source_id: str,
        target_id: str,
        predicate: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> TwinRelationship:
        try:
            rel = TwinRelationship(
                relationship_id=relationship_id,
                source_id=source_id,
                target_id=target_id,
                predicate=predicate,
                attributes=attributes
            )
            is_drift = self._state.upsert_relationship(rel)
            self._telemetry_counter["relationships_registered"] += 1

            if is_drift:
                self._emit_event("TwinTopologyChanged", {
                    "event_type": "RELATIONSHIP_DRIFT",
                    "relationship_id": relationship_id,
                    "source_id": source_id,
                    "target_id": target_id,
                    "predicate": predicate
                })
                self._telemetry_counter["drift_events_emitted"] += 1

            return rel
        except Exception as e:
            logger.error(f"Failed to register relationship [{relationship_id}]: {str(e)}")
            raise RuntimeError(f"TwinEngine relationship registration failure: {str(e)}")

    def execute_query(self, query: TwinQuery) -> TwinQueryResult:
        result = query.execute(self._state)
        self._telemetry_counter["queries_executed"] += 1
        return result

    def _emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        if self._event_bus:
            try:
                event_payload = {
                    "event_type": event_type,
                    "timestamp": time.time(),
                    "payload": payload
                }
                if hasattr(self._event_bus, "publish"):
                    self._event_bus.publish(event_type, event_payload)
            except Exception as e:
                logger.warning(f"Event bus emission deferred for event [{event_type}]: {str(e)}")
