"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/application/twin_simulation_service.py

Epitome:
    Executes non-mutating hypothetical simulation scenarios on graph state clones.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, and 
    counteth the cost, whether he have sufficient to finish it?"
    — Luke 14:28

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from tools.eos.digital_twin.application.twin_engine import TwinEngine

logger = logging.getLogger("WilsyOS.DigitalTwin.SimulationService")


class TwinSimulationService:
    """
    Simulates operational perturbations on hypothetical graph state clones.
    """

    def __init__(self, twin_engine: TwinEngine):
        if not isinstance(twin_engine, TwinEngine):
            raise TypeError("TwinSimulationService requires a valid TwinEngine instance.")

        self._twin_engine = twin_engine

    def simulate_node_failure(self, target_node_id: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        sim_id = f"SIM-FAIL-{uuid.uuid4().hex[:8].upper()}"

        node = self._twin_engine.state.get_entity(target_node_id)
        outgoing = self._twin_engine.state.get_outgoing_relationships(target_node_id)
        incoming = self._twin_engine.state.get_incoming_relationships(target_node_id)

        affected_rel_ids = [r.relationship_id for r in outgoing + incoming]
        affected_entity_ids = list(set([r.target_id for r in outgoing] + [r.source_id for r in incoming]))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = {
            "simulation_id": sim_id,
            "target_node_id": target_node_id,
            "node_found": node is not None,
            "blast_radius": len(affected_entity_ids),
            "affected_entities": affected_entity_ids,
            "affected_relationships_count": len(affected_rel_ids),
            "execution_time_ms": round(elapsed_ms, 4),
            "status": "COMPLETED"
        }
        self._twin_engine._emit_event("TwinSimulationFinished", result)
        return result

    def simulate_worker_decommission(self, worker_id: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        sim_id = f"SIM-WRK-DEC-{uuid.uuid4().hex[:8].upper()}"

        worker = self._twin_engine.state.get_entity(worker_id)
        outgoing_executions = self._twin_engine.state.get_outgoing_relationships(worker_id)

        if not worker:
            return {
                "simulation_id": sim_id,
                "status": "FAILED",
                "error": f"Worker [{worker_id}] not found in Digital Twin state."
            }

        reassigned_task_count = len(outgoing_executions)
        estimated_latency_increase_percent = round(reassigned_task_count * 1.85, 2)
        projected_failure_probability = min(round(reassigned_task_count * 0.025, 4), 0.95)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        simulation_result = {
            "simulation_id": sim_id,
            "target_worker_id": worker_id,
            "reassigned_tasks": reassigned_task_count,
            "estimated_latency_increase_percent": estimated_latency_increase_percent,
            "projected_failure_probability": projected_failure_probability,
            "execution_time_ms": round(elapsed_ms, 4),
            "status": "COMPLETED"
        }

        self._twin_engine._emit_event("TwinSimulationFinished", simulation_result)
        return simulation_result
