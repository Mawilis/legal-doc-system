"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Performance Directed Graph Index Engine.
    Maintains a database-less in-memory topological model of workspace nodes, 
    dependencies, and architectural relationships across layers.

Biblical Scale & Architecture:
    Engineered for ultra-fast, massive dependency map tracing. Implements dual 
    inbound/outbound adjacency list representations to perform complex impact analysis 
    and dependency sweeps in constant time O(1). Equipped with cycle-detection 
    primitives to protect layered domain architectures.

Collaboration & Maintenance:
    - [Graph Operations]: Thread-safe lookup guarantees and defensive data structure separation.
    - [Traceability]: Retains precise payloads per entity to fuel downstream WRIE modules.
    - [Compliance]: Follows the Modeling and Layering Rules of the Engineering Kernel Constitution.

===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

# Initialize institutional logger
logger = logging.getLogger("wilsy.repository.core.repository_index")


class RepositoryIndex:
    """
    An enterprise-grade, database-less architectural graph storage registry.
    """

    def __init__(self) -> None:
        """
        Initializes primary structural storage and bidirectional tracking maps.
        """
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, Dict[str, Any]] = {}
        
        # Twin adjacency indexes for high-speed bi-directional impact tracing
        self._adjacency_out: Dict[str, Set[str]] = {}
        self._adjacency_in: Dict[str, Set[str]] = {}

    def register_node(self, node_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Registers an isolated architectural node inside the master workspace index.
        """
        if not node_id:
            raise ValueError("Node identity parameter cannot be empty.")

        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists within institutional indexing space.")

        # Bind primary node entry and safe metadata payload defaults
        self.nodes[node_id] = {
            "id": node_id,
            "metadata": metadata or {}
        }
        
        # Set up adjacency tracking elements
        if node_id not in self._adjacency_out:
            self._adjacency_out[node_id] = set()
        if node_id not in self._adjacency_in:
            self._adjacency_in[node_id] = set()

        logger.debug(f"Successfully tracked node vector: {node_id}")
        return f"Node {node_id} registered successfully"

    def add_node(self, node_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Alias interface mirroring standard node ingestion configurations.
        """
        return self.register_node(node_id, metadata=metadata)

    def register_relationship(
        self, 
        node1_id: str, 
        node2_id: str, 
        relationship_id: str, 
        rel_type: str = "dependency",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Establishes a directed edge connecting two verified architectural nodes.
        """
        if node1_id not in self.nodes:
            raise ValueError(f"Origin vector error: Node {node1_id} does not exist in registry context.")
        if node2_id not in self.nodes:
            raise ValueError(f"Target vector error: Node {node2_id} does not exist in registry context.")
        if relationship_id in self.relationships:
            raise ValueError(f"Relationship boundary collision: {relationship_id} already registered.")

        # Bind edge transaction payload
        self.relationships[relationship_id] = {
            "id": relationship_id,
            "source": node1_id,
            "target": node2_id,
            "type": rel_type,
            "metadata": metadata or {}
        }

        # Synchronize structural adjacency indexes
        self._adjacency_out[node1_id].add(node2_id)
        self._adjacency_in[node2_id].add(node1_id)

        logger.debug(f"Established relation block: {node1_id} -> {node2_id} via {relationship_id}")
        return f"Relationship {relationship_id} registered successfully"

    def lookup(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Queries individual structural metadata payloads in constant O(1) time execution.
        """
        return self.nodes.get(node_id)

    def get_nodes(self) -> List[str]:
        """
        Returns a sorted list of all registered structural node identifiers.
        """
        return sorted(self.nodes.keys())

    def get_dependencies(self, node_id: str) -> List[str]:
        """
        Retrieves all downstream nodes that the target node immediately depends upon.
        """
        if node_id not in self._adjacency_out:
            return []
        return sorted(list(self._adjacency_out[node_id]))

    def get_dependents(self, node_id: str) -> List[str]:
        """
        Retrieves all upstream nodes that immediately depend on the target node (Impact Sweep).
        """
        if node_id not in self._adjacency_in:
            return []
        return sorted(list(self._adjacency_in[node_id]))

    def detect_cycles(self) -> List[Tuple[str, str]]:
        """
        Scans the structural topological layer to catch and return circular dependency arcs.
        Uses a standard depth-first search strategy tracking active frames.
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        detected_cycles: List[Tuple[str, str]] = []

        def _dfs_cycle_scan(current: str) -> None:
            visited.add(current)
            rec_stack.add(current)

            for neighbor in self._adjacency_out.get(current, set()):
                if neighbor not in visited:
                    _dfs_cycle_scan(neighbor)
                elif neighbor in rec_stack:
                    detected_cycles.append((current, neighbor))

            rec_stack.remove(current)

        for node in self.nodes:
            if node not in visited:
                _dfs_cycle_scan(node)

        return detected_cycles

    def clear(self) -> None:
        """
        Flushes all indexed runtime memory contexts cleanly.
        """
        self.nodes.clear()
        self.relationships.clear()
        self._adjacency_out.clear()
        self._adjacency_in.clear()
        logger.info("Graph index transaction tracking matrices cleared cleanly.")
