"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Registry Framework - Dependency Resolver (FG148).
    Consumes EngineRegistry state, validates graph integrity, detects missing
    and circular dependencies, and generates an immutable ExecutionPlan.

Biblical Scale & Architecture:
    Production-ready institutional dependency resolution engine. Zero child's play.
    Proverbs 16:3 - "Commit to the Lord whatever you do, and he will establish your plans."

Collaboration & Maintenance:
    - [Architecture]: Decouples engine discovery from execution orchestration.
    - Consumes: EngineRegistry, DependencyGraph
    - Produces: ExecutionPlan
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Set

from .dependency_graph import DependencyGraph
from .engine_descriptor import EngineDescriptor
from .engine_registry import EngineRegistry
from .execution_order import ExecutionOrderResolver
from .execution_plan import ExecutionPlan

logger = logging.getLogger("WilsyDependencyResolver")


class DependencyResolver:
    """
    Translates engine registration state into an immutable ExecutionPlan.
    Enforces strict dependency validation, cycle prevention, and missing prerequisite detection.
    """

    # [FUNCTION EXPLANATION]: Core public resolver taking the EngineRegistry singleton and outputting an ExecutionPlan.
    @classmethod
    def resolve(
        cls,
        registry: Optional[EngineRegistry] = None,
        execution_id: Optional[str] = None,
    ) -> ExecutionPlan:
        """
        Resolves the global EngineRegistry into an immutable ExecutionPlan.

        Args:
            registry (Optional[EngineRegistry]): The registry instance. Defaults to EngineRegistry().
            execution_id (Optional[str]): Optional custom execution run ID.

        Returns:
            ExecutionPlan: An immutable execution plan ready for consumption by FG149 Scheduler.

        Raises:
            ValueError: If missing dependencies or circular paths exist in the graph.
        """
        target_registry = registry or EngineRegistry()
        descriptors = target_registry.get_all_descriptors()
        return cls.resolve_from_descriptors(descriptors, execution_id=execution_id)

    # [FUNCTION EXPLANATION]: Resolves an explicit dictionary of descriptors into an ExecutionPlan.
    @classmethod
    def resolve_from_descriptors(
        cls,
        descriptors: Dict[str, EngineDescriptor],
        execution_id: Optional[str] = None,
    ) -> ExecutionPlan:
        """
        Resolves a dictionary of descriptors into an ExecutionPlan.

        Args:
            descriptors (Dict[str, EngineDescriptor]): Map of engine IDs to descriptors.
            execution_id (Optional[str]): Custom execution run identifier.

        Returns:
            ExecutionPlan: Fully validated, topologically sorted execution plan.
        """
        graph = cls.build_graph(descriptors)

        # Step 1: Detect missing dependencies
        missing_deps = cls.detect_missing_dependencies(descriptors)
        if missing_deps:
            error_msg = f"Dependency Resolution Failure: Missing required engines -> {', '.join(missing_deps)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 2: Detect circular dependencies in the DAG
        cycles = graph.detect_cycles()
        if cycles:
            error_msg = f"Dependency Resolution Failure: Circular dependency detected -> {' -> '.join(cycles)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 3: Resolve topological execution order
        ordered_descriptors = ExecutionOrderResolver.resolve_order(descriptors, graph)

        # Step 4: Construct and return immutable execution plan
        plan = ExecutionPlan.create(
            ordered_descriptors=ordered_descriptors,
            execution_id=execution_id,
        )

        logger.info(
            f"ExecutionPlan successfully generated [{plan.execution_id}] with {plan.total_engines} engines "
            f"({plan.enabled_count} enabled). Checksum: {plan.checksum[:12]}"
        )
        return plan

    # [FUNCTION EXPLANATION]: Constructs DependencyGraph DAG from descriptor map.
    @staticmethod
    def build_graph(descriptors: Dict[str, EngineDescriptor]) -> DependencyGraph:
        """
        Constructs a DependencyGraph from a dictionary of EngineDescriptors.
        """
        graph = DependencyGraph()
        for engine_id, desc in descriptors.items():
            graph.add_node(engine_id)
            deps = getattr(desc, "dependencies", ())
            for dep in deps:
                graph.add_dependency(engine_id, dep)
        return graph

    # [FUNCTION EXPLANATION]: Scans for prerequisites declared by engines that are not registered.
    @staticmethod
    def detect_missing_dependencies(descriptors: Dict[str, EngineDescriptor]) -> List[str]:
        """
        Identifies dependencies declared by engines that are not registered in the system.

        Returns:
            List[str]: List of missing dependency error strings.
        """
        missing: List[str] = []
        for engine_id, desc in descriptors.items():
            deps = getattr(desc, "dependencies", ())
            for dep in deps:
                if dep not in descriptors:
                    missing.append(f"'{engine_id}' requires missing engine '{dep}'")
        return missing

    # [FUNCTION EXPLANATION]: Flags engines that are currently disabled.
    @staticmethod
    def detect_unreachable_engines(descriptors: Dict[str, EngineDescriptor]) -> Set[str]:
        """
        Identifies engines that are registered but currently disabled.

        Returns:
            Set[str]: Set of engine IDs marked as disabled.
        """
        return {engine_id for engine_id, desc in descriptors.items() if not desc.enabled}
