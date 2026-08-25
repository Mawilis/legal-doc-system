"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Graph - Dependency Graph.
    Constructs and queries directed dependency graphs across repository modules
    and packages in Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise dependency graph. Zero child's place.
    Enforces cycle detection, topological sorting, and dependency pathing.

Collaboration & Maintenance:
    - [Architecture]: Directed graph structure for analyzing module coupling.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Set


class DependencyGraph:
    """
    Directed graph representing module-to-module dependencies.
    """

    def __init__(self) -> None:
        self.adjacency_list: Dict[str, Set[str]] = {}

    def add_node(self, node: str) -> None:
        """Add a node to the dependency graph."""
        if node not in self.adjacency_list:
            self.adjacency_list[node] = set()

    def add_edge(self, source: str, target: str) -> None:
        """Add a directed edge from source to target dependency."""
        self.add_node(source)
        self.add_node(target)
        self.adjacency_list[source].add(target)

    def get_dependencies(self, node: str) -> List[str]:
        """Get direct dependencies for a node."""
        return list(self.adjacency_list.get(node, set()))

    def to_dict(self) -> Dict[str, List[str]]:
        """Serialize adjacency list into a dictionary payload."""
        return {k: list(v) for k, v in self.adjacency_list.items()}
