"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Knowledge Graph Snapshot - Captures point-in-time states of the knowledge graph.

Biblical Scale & Architecture:
    Production-ready graph snapshotting. Zero child's place.
    Enables immutable point-in-time graph state serialization and versioning.

Collaboration & Maintenance:
    - [Architecture]: Dataclass container representing graph nodes, edges, and metadata.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass
class GraphSnapshot:
    """
    Immutable snapshot container representing the state of the knowledge graph at a given timestamp.
    """

    snapshot_id: str
    timestamp: float
    nodes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the graph snapshot into an institutional dictionary payload.

        Returns:
            Dict[str, Any]: Serialized snapshot payload.
        """
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "nodes": dict(self.nodes),
            "edges": list(self.edges),
            "metadata": dict(self.metadata),
        }
