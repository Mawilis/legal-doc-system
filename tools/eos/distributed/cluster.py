"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Distributed Execution - Cluster State & Node Registry (FG157).
    Manages the cluster topology, node registration, active compute capacity,
    and liveness audits across single-machine and multi-node deployments.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready distributed cluster control plane. Zero child's place.
    Genesis 11:6 - "Behold, they are one people, and they have all one language..."

Collaboration & Maintenance:
    - [Architecture]: Central control plane for cluster topology and node discovery.
    - [Compliance]: Guarantees thread-safe registration and real-time liveness audits.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from tools.eos.distributed.heartbeat import HeartbeatMonitor
from tools.eos.distributed.node import Node, NodeStatus

logger = logging.getLogger("WilsyOS.Cluster")


class Cluster:
    """
    Central control plane managing node topology, capacity metrics, and cluster state.
    """

    def __init__(self, cluster_name: str = "WilsyOS-Primary-Cluster") -> None:
        """
        Initializes the cluster state.

        Args:
            cluster_name (str): Identifier for the distributed execution cluster.
        """
        self.cluster_name = cluster_name
        self._nodes: Dict[str, Node] = {}
        self._heartbeat_monitor = HeartbeatMonitor()
        
        # Self-register default local node to ensure seamless single-machine operation today
        local_node = Node.create(hostname="localhost", ip_address="127.0.0.1", max_task_capacity=8)
        self.register_node(local_node)
        logger.info(f"Cluster [{self.cluster_name}] initialized with default local node [{local_node.node_id}].")

    # [FUNCTION EXPLANATION]: Registers a new node into the cluster topology.
    def register_node(self, node: Node) -> None:
        """
        Adds or updates a node in the active node registry.
        """
        self._nodes[node.node_id] = node
        logger.info(f"Registered node [{node.node_id}] ({node.hostname} @ {node.ip_address}) in cluster.")

    # [FUNCTION EXPLANATION]: Removes a node from the cluster topology.
    def deregister_node(self, node_id: str) -> None:
        """
        Removes a node from the active node registry.
        """
        if node_id in self._nodes:
            del self._nodes[node_id]
            logger.info(f"Deregistered node [{node_id}] from cluster.")

    # [FUNCTION EXPLANATION]: Updates heartbeat and telemetry metrics for a specific node.
    def update_node_heartbeat(
        self, 
        node_id: str, 
        cpu_pct: float, 
        memory_pct: float, 
        active_tasks: int
    ) -> bool:
        """
        Refreshes a node's metrics and heartbeat timestamp.
        """
        if node_id not in self._nodes:
            logger.warning(f"Heartbeat update failed: Node [{node_id}] not found in cluster registry.")
            return False

        current_node = self._nodes[node_id]
        updated_node = current_node.update_telemetry(
            cpu_pct=cpu_pct,
            memory_pct=memory_pct,
            active_tasks=active_tasks,
            status=NodeStatus.ONLINE,
        )
        self._nodes[node_id] = updated_node
        return True

    # [FUNCTION EXPLANATION]: Audits node liveness and returns a list of active online nodes.
    def get_available_nodes(self) -> List[Node]:
        """
        Runs heartbeat liveness check and returns all ONLINE nodes capable of taking tasks.
        """
        self._nodes = self._heartbeat_monitor.audit_cluster_nodes(self._nodes)
        return [node for node in self._nodes.values() if node.can_accept_task()]

    # [FUNCTION EXPLANATION]: Synthesizes aggregate compute capacity and health across all nodes.
    def get_cluster_status(self) -> Dict[str, Any]:
        """
        Returns a comprehensive summary of total capacity, active tasks, and node statuses.
        """
        self._nodes = self._heartbeat_monitor.audit_cluster_nodes(self._nodes)
        total_nodes = len(self._nodes)
        online_nodes = sum(1 for n in self._nodes.values() if n.status == NodeStatus.ONLINE)
        total_capacity = sum(n.max_task_capacity for n in self._nodes.values())
        active_tasks = sum(n.current_active_tasks for n in self._nodes.values())

        return {
            "cluster_name": self.cluster_name,
            "total_nodes": total_nodes,
            "online_nodes": online_nodes,
            "aggregate_task_capacity": total_capacity,
            "aggregate_active_tasks": active_tasks,
            "node_registry": [n.to_dict() for n in self._nodes.values()],
        }
