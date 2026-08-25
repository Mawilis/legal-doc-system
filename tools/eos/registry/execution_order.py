"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Registry Framework - Execution Order Resolver (FG147D).
    Resolves deterministic topological execution sequences for registered engines
    across Wilsy OS, returning an immutable tuple of EngineDescriptor instances.

Biblical Scale & Architecture:
    Production-ready enterprise topological sort engine. Zero child's play.
    Guarantees strict prerequisite ordering prior to dependent initialization.
    Ecclesiastes 3:1 - "To every thing there is a season, and a time to every purpose under the heaven."

Collaboration & Maintenance:
    - [Architecture]: Pure topological sequence generator.
    - [Constraint]: NO runtime execution, NO scheduling, NO engine instantiation.
    - Consumes: DependencyGraph, Dict[str, EngineDescriptor]
    - Produces: Tuple[EngineDescriptor, ...]
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Dict, List, Set, Tuple

from .dependency_graph import DependencyGraph
from .engine_descriptor import EngineDescriptor

logger = logging.getLogger("WilsyExecutionOrder")


class ExecutionOrderResolver:
    """
    Resolves the deterministic topological execution order of registered engines
    based on their dependency graph relationships.
    """

    # [FUNCTION EXPLANATION]: Core topological sort producing an immutable tuple of EngineDescriptor objects.
    @staticmethod
    def resolve_order(
        descriptors: Dict[str, EngineDescriptor],
        graph: DependencyGraph,
    ) -> Tuple[EngineDescriptor, ...]:
        """
        Resolves a topologically sorted tuple of EngineDescriptors for deterministic execution.

        Args:
            descriptors (Dict[str, EngineDescriptor]): Dictionary mapping engine IDs to descriptors.
            graph (DependencyGraph): The constructed dependency graph.

        Returns:
            Tuple[EngineDescriptor, ...]: Immutable, ordered tuple of descriptors ready for execution.

        Raises:
            ValueError: If a circular dependency is detected or a required descriptor is missing.
        """
        # Step 1: Detect circular dependencies in the DAG
        cycles = graph.detect_cycles()
        if cycles:
            raise ValueError(
                f"Execution Order Resolution Failure: Circular dependency detected -> {' -> '.join(cycles)}"
            )

        visited: Set[str] = set()
        temp_marked: Set[str] = set()
        ordered_ids: List[str] = []

        # Access internal adjacency list for topological traversal
        adj_list = getattr(graph, "_adj_list", {})

        # [COLLABORATION COMMENT]: Recursive DFS visit with lexicographical tie-breaking for strict determinism
        def visit(node: str) -> None:
            if node in temp_marked:
                return
            if node not in visited:
                temp_marked.add(node)
                # Sort dependencies lexicographically to guarantee identical output across runs
                for dep in sorted(adj_list.get(node, set())):
                    visit(dep)
                temp_marked.remove(node)
                visited.add(node)
                ordered_ids.append(node)

        # Iterate through all registered engine IDs in lexicographical order
        for node in sorted(descriptors.keys()):
            if node not in visited:
                visit(node)

        # Step 2: Map sorted IDs to EngineDescriptor objects with strict existence validation
        ordered_descriptors: List[EngineDescriptor] = []
        for engine_id in ordered_ids:
            if engine_id not in descriptors:
                raise ValueError(
                    f"Execution Order Resolution Failure: Engine ID '{engine_id}' in graph has no matching descriptor."
                )
            ordered_descriptors.append(descriptors[engine_id])

        logger.info(
            f"Deterministic execution sequence resolved successfully for {len(ordered_descriptors)} engines."
        )
        return tuple(ordered_descriptors)

    # [FUNCTION EXPLANATION]: Helper method to resolve sequence strictly as engine ID strings.
    @staticmethod
    def resolve_ids(
        descriptors: Dict[str, EngineDescriptor],
        graph: DependencyGraph,
    ) -> Tuple[str, ...]:
        """
        Resolves a topologically sorted tuple of engine ID strings.

        Args:
            descriptors (Dict[str, EngineDescriptor]): Dictionary mapping engine IDs to descriptors.
            graph (DependencyGraph): The constructed dependency graph.

        Returns:
            Tuple[str, ...]: Immutable, ordered tuple of engine IDs.
        """
        descriptors_tuple = ExecutionOrderResolver.resolve_order(descriptors, graph)
        return tuple(desc.identifier for desc in descriptors_tuple)
