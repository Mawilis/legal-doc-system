"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/domain/twin_query.py

Epitome:
    Defines structured query contracts and evaluation models for institutional 
    interrogation of the Digital Twin graph state. Supports sub-millisecond filtering 
    across entity types, predicates, dependency graphs, orphaned artifacts, and 
    governance compliance checks.

Biblical Worth Billions:
    "Ask, and it shall be given you; seek, and ye shall find; knock, and it 
    shall be opened unto you."
    — Matthew 7:7

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import hashlib
import json
import time
from typing import Dict, List, Any, Optional
from tools.eos.digital_twin.domain.twin_state import TwinState


class TwinQueryResult:
    """
    Encapsulates the result set of an executed TwinQuery.

    Provides cryptographic hash verification of the query output for auditing
    and execution telemetry.
    """

    def __init__(
        self,
        query_id: str,
        query_type: str,
        matches: List[Dict[str, Any]],
        execution_time_ms: float
    ):
        """
        Initializes a query result set.

        Args:
            query_id (str): ID of the executing query.
            query_type (str): Type of query executed.
            matches (List[Dict[str, Any]]): List of entity or relationship records matched.
            execution_time_ms (float): Execution latency in milliseconds.
        """
        self._query_id = query_id
        self._query_type = query_type
        self._matches = matches
        self._matched_count = len(matches)
        self._execution_time_ms = execution_time_ms
        self._timestamp = time.time()
        self._result_hash = self._compute_result_hash()

    @property
    def query_id(self) -> str:
        return self._query_id

    @property
    def query_type(self) -> str:
        return self._query_type

    @property
    def matches(self) -> List[Dict[str, Any]]:
        return self._matches

    @property
    def matched_count(self) -> int:
        return self._matched_count

    @property
    def execution_time_ms(self) -> float:
        return self._execution_time_ms

    @property
    def result_hash(self) -> str:
        return self._result_hash

    def _compute_result_hash(self) -> str:
        """
        Computes a cryptographic SHA-256 digest of the result payload.
        """
        try:
            payload = {
                "query_id": self._query_id,
                "matched_count": self._matched_count,
                "matches": self._matches
            }
            serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        except Exception as e:
            raise RuntimeError(f"Failed to hash query result [{self._query_id}]: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        """Exports query result to a dictionary representation."""
        return {
            "query_id": self._query_id,
            "query_type": self._query_type,
            "matched_count": self._matched_count,
            "matches": self._matches,
            "execution_time_ms": self._execution_time_ms,
            "timestamp": self._timestamp,
            "result_hash": self._result_hash
        }


class TwinQuery:
    """
    Represents an institutional query definition to interrogate the living state graph.
    """

    def __init__(
        self,
        query_id: str,
        query_type: str,
        filters: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a TwinQuery contract.

        Args:
            query_id (str): Unique query identifier.
            query_type (str): Type category (e.g., 'ENTITY_SEARCH', 'DEPENDENCY_TRACE', 'ORPHAN_CHECK').
            filters (Optional[Dict[str, Any]]): Key-value filtering constraints.
        """
        if not query_id or not query_type:
            raise ValueError("TwinQuery requires query_id and query_type.")

        self._query_id = query_id
        self._query_type = query_type.upper()
        self._filters = filters or {}
        self._created_at = time.time()

    @property
    def query_id(self) -> str:
        return self._query_id

    @property
    def query_type(self) -> str:
        return self._query_type

    @property
    def filters(self) -> Dict[str, Any]:
        return self._filters

    def execute(self, state: TwinState) -> TwinQueryResult:
        """
        Evaluates the query against a given TwinState instance.

        Args:
            state (TwinState): The living state graph to query.

        Returns:
            TwinQueryResult: Cryptographically hashed result container.
        """
        if not isinstance(state, TwinState):
            raise TypeError("Query evaluation requires a valid TwinState instance.")

        start_time = time.perf_counter()
        matches: List[Dict[str, Any]] = []

        try:
            if self._query_type == "ENTITY_SEARCH":
                entity_type = self._filters.get("entity_type")
                if entity_type:
                    entities = state.get_entities_by_type(entity_type)
                else:
                    entities = list(state._entities.values())

                # Apply attribute filters if provided
                attr_filters = self._filters.get("attributes", {})
                for e in entities:
                    match = True
                    for k, v in attr_filters.items():
                        if e.attributes.get(k) != v:
                            match = False
                            break
                    if match:
                        matches.append(e.to_dict())

            elif self._query_type == "DEPENDENCY_TRACE":
                source_id = self._filters.get("source_id")
                if source_id:
                    relationships = state.get_outgoing_relationships(source_id)
                    predicate = self._filters.get("predicate")
                    for r in relationships:
                        if not predicate or r.predicate == predicate.upper():
                            matches.append(r.to_dict())

            elif self._query_type == "ORPHAN_CHECK":
                # Detect entities with no incoming or outgoing relationships
                for entity_id, entity in state._entities.items():
                    has_outgoing = len(state.get_outgoing_relationships(entity_id)) > 0
                    has_incoming = len(state.get_incoming_relationships(entity_id)) > 0
                    if not has_outgoing and not has_incoming:
                        matches.append(entity.to_dict())

            else:
                # Default generic attribute matcher
                for e in state._entities.values():
                    matches.append(e.to_dict())

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return TwinQueryResult(
                query_id=self._query_id,
                query_type=self._query_type,
                matches=matches,
                execution_time_ms=round(elapsed_ms, 4)
            )

        except Exception as e:
            raise RuntimeError(f"Error evaluating query [{self._query_id}]: {str(e)}")
