"""
* Epitome: Absolute Sovereign Enterprise Graph Builder for Wilsy OS. 
*          Constructs, optimizes, and analyzes dependency graphs and interconnected 
*          system topologies with biblical resilience and zero-defect precision.
* Collaboration Comments: 
    - Architect: Wilsy OS Core Engineering
    - Tier: Billion-Dollar Production Grade (v4.2.0-Sovereign)
    - Standards: Strict Type Hinting, Thread-Safe Concurrency, Immutable Auditing, 
      Zero-Defect Production Execution.
"""

import threading
import logging
import json
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime, timezone

# Configure high-performance production logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [WilsyOS-GraphBuilder]: %(message)s"
)
logger = logging.getLogger("EnterpriseGraphBuilder")

class EnterpriseGraphBuilder:
    """
    Core engine responsible for assembling topological graphs, performing cycle detection,
    and calculating traversal paths across the Wilsy OS enterprise grid.
    """
    
    _instance: Optional["EnterpriseGraphBuilder"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "EnterpriseGraphBuilder":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EnterpriseGraphBuilder, cls).__new__(cls)
                cls._instance._initialize_builder()
            return cls._instance

    def _initialize_builder(self) -> None:
        """Initializes thread-safe adjacency lists for advanced graph calculations."""
        self._adjacency_list: Dict[str, Set[str]] = {}
        self._node_weights: Dict[str, float] = {}
        self._state_lock: threading.RLock = threading.RLock()
        logger.info("EnterpriseGraphBuilder successfully initialized with sovereign adjacency structures.")

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> bool:
        """
        Adds a directed edge between two nodes with optional operational weight.

        Args:
            source (str): Source node identifier.
            target (str): Target node identifier.
            weight (float): Operational weight or latency metric.

        Returns:
            bool: True if edge addition is successful, False otherwise.
        """
        if not source or not target:
            logger.error("Invalid source or target node provided for edge construction.")
            return False

        with self._state_lock:
            try:
                if source not in self._adjacency_list:
                    self._adjacency_list[source] = set()
                self._adjacency_list[source].add(target)
                
                # Ensure target exists in adjacency list as well
                if target not in self._adjacency_list:
                    self._adjacency_list[target] = set()

                self._node_weights[f"{source}->{target}"] = weight
                logger.info(f"Graph edge built successfully: {source} -> {target} [weight: {weight}]")
                return True
            except Exception as e:
                logger.critical(f"Critical error building graph edge {source}->{target}: {str(e)}")
                return False

    def detect_cycles(self) -> List[List[str]]:
        """
        Detects circular dependencies within the sovereign network graph using DFS.

        Returns:
            List[List[str]]: A list of detected cycle paths.
        """
        with self._state_lock:
            visited: Set[str] = set()
            recursion_stack: Set[str] = set()
            cycles: List[List[str]] = []

            def dfs(node: str, path: List[str]) -> None:
                visited.add(node)
                recursion_stack.add(node)
                path.append(node)

                for neighbor in self._adjacency_list.get(node, set()):
                    if neighbor not in visited:
                        dfs(neighbor, list(path))
                    elif neighbor in recursion_stack:
                        cycle_start_idx = path.index(neighbor)
                        cycles.append(path[cycle_start_idx:] + [neighbor])

                recursion_stack.remove(node)

            for node in list(self._adjacency_list.keys()):
                if node not in visited:
                    dfs(node, [])

            if cycles:
                logger.warning(f"Detected {len(cycles)} circular dependencies in graph structure.")
            else:
                logger.info("Graph structural audit passed: Zero circular dependencies detected.")

            return cycles

    def export_graph_state(self) -> str:
        """
        Exports the current graph representation and weights as a serialized JSON string.
        """
        with self._state_lock:
            export_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "adjacency_list": {k: list(v) for k, v in self._adjacency_list.items()},
                "node_weights": self._node_weights,
                "total_nodes": len(self._adjacency_list)
            }
            return json.dumps(export_data, indent=4)

# Global singleton accessor for enterprise dependency injection
graph_builder = EnterpriseGraphBuilder()
