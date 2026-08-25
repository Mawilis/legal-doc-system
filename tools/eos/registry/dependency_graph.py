"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Registry Framework - Dependency Graph Component (FG147C).
    Constructs, validates, and manages pure Directed Acyclic Graph (DAG) structures
    representing inter-engine structural requirements across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise dependency graph core. Zero child's place.
    Provides deterministic cycle detection, dependency validation, and pure structural queries.
    Proverbs 18:15 - "The heart of the discerning acquires knowledge, for the ears of the wise seek it out."

Collaboration & Maintenance:
    - [Architecture]: Pure DAG model for inter-component relationship modeling.
    - [Constraint]: NO scheduling, NO runtime execution logic. Relationship modeling ONLY.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("WilsyDependencyGraph")


class DependencyGraph:
    """
    Pure Directed Acyclic Graph (DAG) structure representing structural relationships
    and prerequisite requirements between registered Wilsy OS engines.
    """

    def __init__(self) -> None:
        """Initializes an empty dependency adjacency graph."""
        # Mapping from dependent node -> set of required dependency nodes (prerequisites)
        self._adj_list: Dict[str, Set[str]] = {}
        # Reverse mapping: required node -> set of engines depending on it
        self._dependents_list: Dict[str, Set[str]] = {}
        # Complete set of registered engine nodes
        self._nodes: Set[str] = set()

    # [FUNCTION EXPLANATION]: Ensures node existence across forward and reverse adjacency tables.
    def add_node(self, engine_id: str) -> None:
        """
        Ensures an engine node is registered in the graph structure.

        Args:
            engine_id (str): Unique string identifier of the engine node.
        """
        self._nodes.add(engine_id)
        if engine_id not in self._adj_list:
            self._adj_list[engine_id] = set()
        if engine_id not in self._dependents_list:
            self._dependents_list[engine_id] = set()

    # [COLLABORATION COMMENT]: Explicitly declares a directed edge from engine_id -> dependency_id.
    def add_dependency(self, engine_id: str, dependency_id: str) -> None:
        """
        Declare that `engine_id` structurally requires `dependency_id` to function.

        Args:
            engine_id (str): The dependent engine identifier.
            dependency_id (str): The required prerequisite engine identifier.
        """
        self.add_node(engine_id)
        self.add_node(dependency_id)
        self._adj_list[engine_id].add(dependency_id)
        self._dependents_list[dependency_id].add(engine_id)

    # [FUNCTION EXPLANATION]: Inspects graph for circular dependencies using standard 3-color DFS.
    def detect_cycles(self) -> List[str]:
        """
        Detect circular dependencies within the graph using Depth-First Search (DFS) node coloring.

        Returns:
            List[str]: A list representing the ordered cycle path if detected, else empty list.
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {node: WHITE for node in self._nodes}
        parent: Dict[str, Optional[str]] = {node: None for node in self._nodes}

        def dfs(node: str) -> List[str] | None:
            color[node] = GRAY
            for neighbor in self._adj_list.get(node, set()):
                if color[neighbor] == GRAY:
                    # Circular dependency detected - reconstruct the exact cycle path
                    cycle = [node]
                    curr: Optional[str] = node
                    while curr is not None and curr in parent and curr != neighbor:
                        curr = parent[curr]
                        if curr is not None:
                            cycle.append(curr)
                    cycle.append(neighbor)
                    return list(reversed(cycle))
                elif color[neighbor] == WHITE:
                    parent[neighbor] = node
                    result = dfs(neighbor)
                    if result:
                        return result
            color[node] = BLACK
            return None

        for node in sorted(self._nodes):
            if color[node] == WHITE:
                cycle_path = dfs(node)
                if cycle_path:
                    logger.error(f"Circular dependency detected in graph: {' -> '.join(cycle_path)}")
                    return cycle_path

        return []

    # [FUNCTION EXPLANATION]: Quick boolean check for cycle presence without returning the path.
    def has_cycle(self) -> bool:
        """
        Returns True if any circular dependency exists in the graph.
        """
        return len(self.detect_cycles()) > 0

    # [FUNCTION EXPLANATION]: Direct lookup for immediate prerequisites.
    def get_dependencies(self, engine_id: str) -> Set[str]:
        """
        Returns the set of direct prerequisites for a given engine node.
        """
        return set(self._adj_list.get(engine_id, set()))

    # [FUNCTION EXPLANATION]: Reverse lookup for engines that depend on this node.
    def get_dependents(self, engine_id: str) -> Set[str]:
        """
        Returns the set of engines that directly depend on the given engine node.
        """
        return set(self._dependents_list.get(engine_id, set()))

    # [FUNCTION EXPLANATION]: Transitive closure resolution for full sub-tree analysis.
    def get_all_transitive_dependencies(self, engine_id: str) -> Set[str]:
        """
        Recursively resolves all direct and indirect dependencies for an engine.
        """
        visited: Set[str] = set()

        def resolve(node: str) -> None:
            for dep in self._adj_list.get(node, set()):
                if dep not in visited:
                    visited.add(dep)
                    resolve(dep)

        resolve(engine_id)
        return visited

    # [FUNCTION EXPLANATION]: Checks whether a node exists within the graph.
    def has_node(self, engine_id: str) -> bool:
        """Checks if an engine exists in the graph."""
        return engine_id in self._nodes

    # [FUNCTION EXPLANATION]: Exposes immutable copy of registered node set.
    @property
    def nodes(self) -> Set[str]:
        """Returns a copy of all registered nodes."""
        return set(self._nodes)

    # [FUNCTION EXPLANATION]: Serialization for architecture visualization and system audits.
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the graph into a structural JSON-compatible dictionary payload.
        """
        return {
            "nodes": sorted(list(self._nodes)),
            "adjacency": {k: sorted(list(v)) for k, v in self._adj_list.items()},
            "dependents": {k: sorted(list(v)) for k, v in self._dependents_list.items()},
            "has_cycles": self.has_cycle(),
        }

    # [FUNCTION EXPLANATION]: Clear graph state for unit testing & hot reloads.
    def clear(self) -> None:
        """Resets the dependency graph state."""
        self._adj_list.clear()
        self._dependents_list.clear()
        self._nodes.clear()
        logger.info("DependencyGraph cleared successfully.")
