"""
* Epitome: Absolute Sovereign Enterprise Dependency Resolver for Wilsy OS. 
*          Performs topological sorting, dependency resolution, and startup sequencing 
*          with divine fault-tolerance and zero circular dependency defects.
* Collaboration Comments: 
    - Architect: Wilsy OS Core Engineering
    - Tier: Billion-Dollar Production Grade (v4.2.0-Sovereign)
    - Standards: Strict Type Hinting, Thread-Safe Concurrency, Immutable Auditing, 
      Zero-Defect Production Execution.
"""

import threading
import logging
import json
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone

# Configure high-performance production logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [WilsyOS-DependencyResolver]: %(message)s"
)
logger = logging.getLogger("EnterpriseDependencyResolver")

class EnterpriseDependencyResolver:
    """
    Core resolver responsible for computing execution order (topological sort)
    among interdependent sovereign modules in Wilsy OS.
    """
    
    _instance: Optional["EnterpriseDependencyResolver"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "EnterpriseDependencyResolver":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EnterpriseDependencyResolver, cls).__new__(cls)
                cls._instance._initialize_resolver()
            return cls._instance

    def _initialize_resolver(self) -> None:
        """Initializes thread-safe dependency mapping catalogs."""
        self._dependencies: Dict[str, Set[str]] = {}
        self._state_lock: threading.RLock = threading.RLock()
        logger.info("EnterpriseDependencyResolver successfully initialized.")

    def add_dependency(self, module: str, depends_on: str) -> bool:
        """
        Registers a dependency relationship where 'module' requires 'depends_on'.

        Args:
            module (str): Dependent module identifier.
            depends_on (str): Prerequisite module identifier.

        Returns:
            bool: True if registration succeeds, False otherwise.
        """
        if not module or not depends_on:
            logger.error("Invalid module or prerequisite identifier provided.")
            return False

        with self._state_lock:
            if module not in self._dependencies:
                self._dependencies[module] = set()
            self._dependencies[module].add(depends_on)
            
            # Ensure prerequisite exists in mapping dictionary as a key
            if depends_on not in self._dependencies:
                self._dependencies[depends_on] = set()

            logger.info(f"Dependency registered: '{module}' requires prerequisite '{depends_on}'")
            return True

    def resolve_execution_order(self) -> List[str]:
        """
        Computes a valid topological startup order for all registered modules using Kahn's or DFS algorithm.

        Returns:
            List[str]: Ordered list of module identifiers ready for sovereign initialization.
        """
        with self._state_lock:
            in_degree: Dict[str, int] = {node: 0 for node in self._dependencies}
            
            # Compute in-degrees based on incoming dependencies
            for node, prereqs in self._dependencies.items():
                for prereq in prereqs:
                    if prereq in in_degree:
                        in_degree[prereq] += 1  # Prereq must run before node (so node points to prereq in requirement graph)

            # Re-evaluating standard topological sort direction:
            # If A depends on B, B must be initialized before A.
            # Adjacency representation: self._dependencies[A] contains B.
            # Therefore, B has an edge pointing to A (B -> A).
            
            adj: Dict[str, Set[str]] = {node: set() for node in self._dependencies}
            deg: Dict[str, int] = {node: 0 for node in self._dependencies}

            for module, prereqs in self._dependencies.items():
                for prereq in prereqs:
                    # prereq must run before module -> edge from prereq to module
                    adj[prereq].add(module)
                    deg[module] += 1

            # Queue nodes with zero in-degree
            queue: List[str] = [node for node, d in deg.items() if d == 0]
            execution_order: List[str] = []

            while queue:
                current = queue.pop(0)
                execution_order.append(current)

                for neighbor in adj.get(current, set()):
                    deg[neighbor] -= 1
                    if deg[neighbor] == 0:
                        queue.append(neighbor)

            if len(execution_order) != len(self._dependencies):
                logger.critical("Circular dependency detected during sovereign execution resolution!")
                raise ValueError("Circular dependency detected among enterprise modules.")

            logger.info(f"Successfully computed execution order for {len(execution_order)} modules.")
            return execution_order

    def export_resolver_state(self) -> str:
        """
        Exports dependency mappings as a serialized JSON string.
        """
        with self._state_lock:
            export_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "dependencies": {k: list(v) for k, v in self._dependencies.items()},
                "total_modules": len(self._dependencies)
            }
            return json.dumps(export_data, indent=4)

# Global singleton accessor for enterprise dependency injection
dependency_resolver = EnterpriseDependencyResolver()
