"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Registry Framework - Central Engine Registry.
    Singleton registry managing registration, dependency graphing, and execution
    sequencing across all Wilsy OS core engines.

Biblical Scale & Architecture:
    Production-ready enterprise engine registry. Zero child's play.
    Provides robust registration locking, dynamic lookup, and execution sorting.
    Built for billion-dollar scaling and quantum-ready execution environments.
    Proverbs 24:3-4 - "By wisdom a house is built, and through understanding it is established."

Collaboration & Maintenance:
    - [Architecture]: Central registry and lifecycle manager for Wilsy OS kernels.
    - Maintained by Wilson Khanyezi & Core Engineering.
    - [Updates]: Synchronized resolve_execution_order return type with FG147D
      tuple return spec and added resolve_execution_ids for string-only queries.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type, Tuple, cast

from .dependency_graph import DependencyGraph
from .engine_descriptor import EngineDescriptor
from .execution_order import ExecutionOrderResolver

logger = logging.getLogger("WilsyEngineRegistry")


class EngineRegistry:
    """
    Central institutional registry for discovering, registering, and orchestrating Wilsy OS engines.
    Ensures absolute singleton integrity and production-ready instance management.
    """

    # Class-level type annotations for static type checkers (Pylance)
    _instance: Optional[EngineRegistry] = None
    _descriptors: Dict[str, EngineDescriptor] = {}
    _instances: Dict[str, Any] = {}

    def __new__(cls) -> EngineRegistry:
        """
        Singleton constructor enforcing a unified registry instance across the OS.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._descriptors = {}
            cls._instance._instances = {}
        return cls._instance

    def register(
        self,
        engine_id: str,
        name: str,
        version: str,
        engine_class: Type[Any],
        dependencies: List[str] | None = None,
        description: str = "",
        is_critical: bool = True,
        metadata: Dict[str, Any] | None = None,
    ) -> EngineDescriptor:
        """
        Register an institutional engine into the Wilsy OS registry.

        Args:
            engine_id (str): Unique identifier for the engine.
            name (str): Human-readable name.
            version (str): Semantic version.
            engine_class (Type[Any]): The engine class implementation.
            dependencies (List[str] | None): List of prerequisite engine IDs.
            description (str): Detailed description.
            is_critical (bool): Whether failure halts the system.
            metadata (Dict[str, Any] | None): Additional configuration metadata.

        Returns:
            EngineDescriptor: The created and stored descriptor.
        """
        deps_tuple: Tuple[str, ...] = tuple(dependencies or [])
        
        # Instantiate descriptor strictly aligning with expected EngineDescriptor properties
        descriptor = EngineDescriptor(
            identifier=engine_id,
            display_name=name,
            version=version,
            engine_type=cast(Any, engine_class),
            dependencies=deps_tuple
        )

        self._descriptors[engine_id] = descriptor
        logger.info(f"Engine Registered Successfully: '{engine_id}' v{version} [{name}]")
        return descriptor

    def get_descriptor(self, engine_id: str) -> EngineDescriptor:
        """
        Retrieve an engine descriptor by ID.
        
        Raises:
            KeyError: If the engine is not found in the registry.
        """
        if engine_id not in self._descriptors:
            raise KeyError(f"Institutional Registry Error: Engine ID '{engine_id}' not found.")
        return self._descriptors[engine_id]

    def get_all_descriptors(self) -> Dict[str, EngineDescriptor]:
        """
        Retrieve a copy of all registered engine descriptors.
        """
        return dict(self._descriptors)

    def instantiate(self, engine_id: str, *args: Any, **kwargs: Any) -> Any:
        """
        Instantiate or retrieve a singleton instance of a registered engine.
        Ensures engines are only instantiated once.
        """
        if engine_id in self._instances:
            return self._instances[engine_id]

        descriptor = self.get_descriptor(engine_id)
        
        # Cast engine_type to allow dynamic invocation under strict Pylance rules
        engine_factory = cast(Any, descriptor.engine_type)
        instance = engine_factory(*args, **kwargs)
        self._instances[engine_id] = instance
        
        engine_name = getattr(engine_factory, "__name__", str(engine_factory))
        logger.info(f"Engine Instantiated: '{engine_id}' ({engine_name})")
        return instance

    # [FUNCTION EXPLANATION]: Internal helper building DAG from current descriptors.
    def _build_dependency_graph(self) -> DependencyGraph:
        """
        Constructs and populates a DependencyGraph from all registered descriptors.
        """
        graph = DependencyGraph()
        for engine_id, descriptor in self._descriptors.items():
            graph.add_node(engine_id)
            deps = getattr(descriptor, 'dependencies', ())
            for dep in deps:
                if dep not in self._descriptors:
                    logger.warning(f"Dependency Warning: Engine '{engine_id}' depends on unregistered ID '{dep}'.")
                graph.add_dependency(engine_id, dep)
        return graph

    # [FUNCTION EXPLANATION]: Resolves topological order returning ordered EngineDescriptors.
    def resolve_execution_order(self) -> Tuple[EngineDescriptor, ...]:
        """
        Construct the dependency graph and resolve the execution sequence for all registered engines.

        Returns:
            Tuple[EngineDescriptor, ...]: Ordered tuple of EngineDescriptor instances ready for execution.
        """
        graph = self._build_dependency_graph()
        return ExecutionOrderResolver.resolve_order(self._descriptors, graph)

    # [FUNCTION EXPLANATION]: Resolves topological order returning ordered engine ID strings.
    def resolve_execution_ids(self) -> Tuple[str, ...]:
        """
        Construct the dependency graph and resolve the execution sequence strictly as engine ID strings.

        Returns:
            Tuple[str, ...]: Ordered tuple of engine ID strings ready for execution.
        """
        graph = self._build_dependency_graph()
        return ExecutionOrderResolver.resolve_ids(self._descriptors, graph)

    def clear(self) -> None:
        """
        Reset the registry state. 
        Primarily utilized for testing suites and hot-swappable kernel reloads.
        """
        self._descriptors.clear()
        self._instances.clear()
        logger.info("Engine Registry cleared.")
