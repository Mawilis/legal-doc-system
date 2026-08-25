"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/application/twin_query_service.py

Epitome:
    High-level institutional query service for interrogating the Digital Twin graph.

Biblical Worth Billions:
    "Counsel in the heart of man is like deep water; but a man of understanding 
    will draw it out."
    — Proverbs 20:5

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import uuid
from typing import Dict, Any, List, Optional
from tools.eos.digital_twin.domain.twin_query import TwinQuery, TwinQueryResult
from tools.eos.digital_twin.application.twin_engine import TwinEngine


class TwinQueryService:
    """
    High-level query execution interface for Wilsy OS institutional queries.
    """

    def __init__(self, twin_engine: TwinEngine):
        if not isinstance(twin_engine, TwinEngine):
            raise TypeError("TwinQueryService requires a valid TwinEngine instance.")

        self._twin_engine = twin_engine

    def filter_entities(self, entity_type: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query_id = f"QRY-FLTR-{uuid.uuid4().hex[:8].upper()}"
        filters = {}
        if entity_type:
            filters["entity_type"] = entity_type
        if attributes:
            filters["attributes"] = attributes
        query = TwinQuery(query_id=query_id, query_type="ENTITY_SEARCH", filters=filters)
        res = self._twin_engine.execute_query(query)
        return res.matches

    def get_entity_dependencies(self, entity_id: str, direction: str = "OUTGOING") -> List[Dict[str, Any]]:
        if direction.upper() == "OUTGOING":
            rels = self._twin_engine.state.get_outgoing_relationships(entity_id)
        else:
            rels = self._twin_engine.state.get_incoming_relationships(entity_id)
        return [r.to_dict() for r in rels]

    def query_plugins_by_abi(self, abi_version: str) -> TwinQueryResult:
        query_id = f"QRY-ABI-{uuid.uuid4().hex[:8].upper()}"
        query = TwinQuery(
            query_id=query_id,
            query_type="ENTITY_SEARCH",
            filters={"entity_type": "Plugin", "attributes": {"abi_version": abi_version}}
        )
        return self._twin_engine.execute_query(query)

    def query_worker_executions(self, worker_id: str) -> TwinQueryResult:
        query_id = f"QRY-WRK-{uuid.uuid4().hex[:8].upper()}"
        query = TwinQuery(
            query_id=query_id,
            query_type="DEPENDENCY_TRACE",
            filters={"source_id": worker_id, "predicate": "EXECUTES"}
        )
        return self._twin_engine.execute_query(query)

    def query_orphaned_artifacts(self) -> TwinQueryResult:
        query_id = f"QRY-ORPHAN-{uuid.uuid4().hex[:8].upper()}"
        query = TwinQuery(
            query_id=query_id,
            query_type="ORPHAN_CHECK",
            filters={}
        )
        return self._twin_engine.execute_query(query)
