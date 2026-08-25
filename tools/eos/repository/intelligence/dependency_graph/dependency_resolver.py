"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Sovereign execution path dependency resolver and cascade calculation engine
    for the Wilsy OS Enterprise Nervous System.

Biblical Worth Billions:
    "Ponder the path of thy feet, and let all thy ways be established."
    — Proverbs 4:26

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/dependency_graph/dependency_resolver.py
===============================================================================
"""

from __future__ import annotations

from typing import List, Dict, Set, Optional
from.dependency_models import ExecutionDependencyGraph, DependencyEdge


class DependencyResolver:
    """
    Sovereign resolver computing deterministic propagation paths and downstream
    impact sequences across capability networks.
    """

    def __init__(self, graph: ExecutionDependencyGraph) -> None:
        self.graph = graph

    def resolve_cascade_path(self, start_node: str) -> List[str]:
        """
        Calculates deterministic cascade execution sequence starting from a given trigger node.
        Uses Depth-First Search (DFS) while preserving path order and avoiding cycles.
        """
        visited: Set[str] = set()
        cascade_sequence: List[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            cascade_sequence.append(node)
            outgoing_edges = self.graph.get_outgoing_edges(node)
            for edge in outgoing_edges:
                if edge.target_capability not in visited:
                    dfs(edge.target_capability)

        if start_node in self.graph.nodes:
            dfs(start_node)

        return cascade_sequence

    def get_upstream_dependencies(self, target_node: str) -> List[str]:
        """
        Finds all capability nodes that directly or indirectly influence the target capability node.
        """
        upstream: Set[str] = set()

        def find_incoming(current: str) -> None:
            for edge in self.graph.edges:
                if edge.target_capability == current and edge.source_capability not in upstream:
                    upstream.add(edge.source_capability)
                    find_incoming(edge.source_capability)

        find_incoming(target_node)
        return list(upstream)