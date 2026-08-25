"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Sovereign data models defining execution dependency edges, node topologies, 
    weight vectors, and execution propagation relationships for Wilsy OS.

Biblical Worth Billions:
    "Line upon line, line upon line; here a little, and there a little."
    — Isaiah 28:10

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/dependency_graph/dependency_models.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional


class DependencyRelationshipType(str, Enum):
    """Enumeration of strict enterprise execution linkage types."""
    EXECUTES = "EXECUTES"
    TRIGGERS = "TRIGGERS"
    ENFORCES = "ENFORCES"
    AUDITS = "AUDITS"
    PROPAGATES_TO = "PROPAGATES_TO"
    DISPATCHES = "DISPATCHES"


@dataclass
class DependencyEdge:
    """
    Represents a directed dependency edge between two enterprise capabilities.
    """
    source_capability: str
    target_capability: str
    relationship_type: DependencyRelationshipType
    weight: float = 1.0
    criticality: str = "HIGH"

    def to_dict(self) -> Dict[str, Any]:
        """Converts dependency edge to a dictionary representation."""
        data = asdict(self)
        data["relationship_type"] = (
            self.relationship_type.value
            if isinstance(self.relationship_type, DependencyRelationshipType)
            else str(self.relationship_type)
        )
        return data


@dataclass
class ExecutionDependencyGraph:
    """
    Master data model representing the platform-wide capability execution graph.
    """
    nodes: List[str] = field(default_factory=list)
    edges: List[DependencyEdge] = field(default_factory=list)

    def add_edge(
        self,
        source: str,
        target: str,
        relationship_type: DependencyRelationshipType,
        weight: float = 1.0,
        criticality: str = "HIGH",
    ) -> None:
        """Adds a directed dependency edge and registers participating nodes."""
        if source not in self.nodes:
            self.nodes.append(source)
        if target not in self.nodes:
            self.nodes.append(target)
        self.edges.append(
            DependencyEdge(
                source_capability=source,
                target_capability=target,
                relationship_type=relationship_type,
                weight=weight,
                criticality=criticality,
            )
        )

    def get_outgoing_edges(self, source_capability: str) -> List[DependencyEdge]:
        """Retrieves all outgoing dependency edges from a given source capability."""
        return [edge for edge in self.edges if edge.source_capability == source_capability]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the graph structure into a JSON-compatible dictionary."""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": self.nodes,
            "edges": [edge.to_dict() for edge in self.edges],
        }