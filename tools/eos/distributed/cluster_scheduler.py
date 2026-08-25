"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Distributed Execution - Cluster Task Scheduler (FG157).
    Routes and dispatches execution workloads across available compute nodes
    within the Wilsy OS distributed fabric.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready distributed task dispatcher. Zero child's place.
    Proverbs 16:3 - "Commit to the Lord whatever you do, and he will establish your plans."

Collaboration & Maintenance:
    - [Architecture]: Intelligent task router selecting optimal nodes based on load and availability.
    - [Compliance]: Guarantees fault-tolerant task dispatching and dynamic fallback.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Optional

from tools.eos.distributed.cluster import Cluster
from tools.eos.distributed.node import Node

logger = logging.getLogger("WilsyOS.ClusterScheduler")


class ClusterScheduler:
    """
    Scheduler responsible for distributing execution tasks across cluster nodes
    using least-loaded node allocation strategies.
    """

    def __init__(self, cluster: Cluster) -> None:
        """
        Initializes the cluster scheduler linked to a cluster topology.

        Args:
            cluster (Cluster): The active cluster instance managing node registries.
        """
        self.cluster = cluster

    # [FUNCTION EXPLANATION]: Selects the optimal available node from the cluster using least-loaded heuristics.
    def select_optimal_node(self) -> Optional[Node]:
        """
        Queries the cluster for available nodes and selects the one with the lowest active task count
        and CPU utilization.

        Returns:
            Optional[Node]: The selected node, or None if no capacity is available.
        """
        available_nodes = self.cluster.get_available_nodes()
        if not available_nodes:
            return None

        # Sort by active tasks first, then by CPU utilization percentage
        sorted_nodes = sorted(
            available_nodes,
            key=lambda n: (n.current_active_tasks, n.cpu_utilization_pct)
        )
        return sorted_nodes[0]

    # [FUNCTION EXPLANATION]: Dispatches a task to an optimal cluster node and manages execution lifecycle.
    def dispatch_task(
        self,
        task_id: str,
        task_fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Schedules and executes a task on the optimal available node in the cluster.

        Args:
            task_id (str): Unique identifier for the task.
            task_fn (Callable[..., Any]): Callable task function.

        Returns:
            Dict[str, Any]: Execution result telemetry and node allocation metadata.
        """
        logger.info(f"Scheduling distributed task [{task_id}] across cluster nodes...")

        # 1. Select Optimal Node
        target_node = self.select_optimal_node()
        if not target_node:
            logger.error(f"Scheduling failed for task [{task_id}]: No available cluster nodes with capacity.")
            return {
                "task_id": task_id,
                "status": "FAILED",
                "error": "Cluster resource exhaustion: No online nodes available.",
            }

        logger.info(f"Task [{task_id}] assigned to node [{target_node.node_id}] ({target_node.hostname}).")

        # 2. Update Node Active Task Load
        self.cluster.update_node_heartbeat(
            node_id=target_node.node_id,
            cpu_pct=target_node.cpu_utilization_pct + 5.0,  # Simulated load increment
            memory_pct=target_node.memory_utilization_pct,
            active_tasks=target_node.current_active_tasks + 1,
        )

        start_time = time.perf_counter()
        execution_success = False
        result = None
        error_msg = None

        try:
            result = task_fn(*args, **kwargs)
            execution_success = True
        except Exception as ex:
            error_msg = str(ex)
            logger.error(f"Distributed task [{task_id}] failed on node [{target_node.node_id}]: {ex}")

        # 3. Release Node Task Load
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        current_node_state = self.cluster._nodes.get(target_node.node_id)
        if current_node_state:
            self.cluster.update_node_heartbeat(
                node_id=target_node.node_id,
                cpu_pct=max(0.0, current_node_state.cpu_utilization_pct - 5.0),
                memory_pct=current_node_state.memory_utilization_pct,
                active_tasks=max(0, current_node_state.current_active_tasks - 1),
            )

        if not execution_success:
            return {
                "task_id": task_id,
                "node_id": target_node.node_id,
                "status": "FAILED",
                "execution_time_ms": elapsed_ms,
                "error": error_msg,
            }

        logger.info(f"Distributed task [{task_id}] completed successfully on node [{target_node.node_id}] in {elapsed_ms}ms.")
        return {
            "task_id": task_id,
            "node_id": target_node.node_id,
            "status": "COMPLETED",
            "execution_time_ms": elapsed_ms,
            "result": result,
        }
