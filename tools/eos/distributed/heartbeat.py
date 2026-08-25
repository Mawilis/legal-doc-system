"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Distributed Execution - Node Heartbeat Telemetry (FG157).
    Monitors node vitality, updates health signals, and marks dead or stale
    nodes across the distributed execution fabric.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready distributed health telemetry system. Zero child's place.
    Psalm 121:8 - "The Lord shall preserve thy going out and thy coming in from this time forth, and even for evermore."

Collaboration & Maintenance:
    - [Architecture]: Heartbeat monitor and node liveness detector.
    - [Compliance]: Detects unresponsive cluster nodes within deterministic timeout thresholds.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict

from tools.eos.distributed.node import Node, NodeStatus

logger = logging.getLogger("WilsyOS.Heartbeat")


class HeartbeatMonitor:
    """
    Evaluates node liveness and marks unreachable nodes when heartbeats lapse.
    """

    def __init__(self, heartbeat_timeout_seconds: float = 15.0) -> None:
        """
        Initializes the heartbeat monitor.

        Args:
            heartbeat_timeout_seconds (float): Threshold in seconds before a node is declared UNREACHABLE.
        """
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds

    # [FUNCTION EXPLANATION]: Audits node heartbeat timestamp against current UTC time to assess liveness.
    def evaluate_node_health(self, node: Node) -> Node:
        """
        Evaluates a node's heartbeat age. If the heartbeat has expired, returns a updated
        Node instance marked as UNREACHABLE.

        Args:
            node (Node): Node instance to evaluate.

        Returns:
            Node: Updated node object with current health status.
        """
        try:
            last_hb_dt = datetime.fromisoformat(node.last_heartbeat)
            now_dt = datetime.now(timezone.utc)
            elapsed_seconds = (now_dt - last_hb_dt).total_seconds()

            if elapsed_seconds > self.heartbeat_timeout_seconds:
                if node.status != NodeStatus.UNREACHABLE:
                    logger.warning(
                        f"Node [{node.node_id}] heartbeat lapsed ({round(elapsed_seconds, 1)}s elapsed). "
                        f"Marking status as UNREACHABLE."
                    )
                    return node.update_telemetry(
                        cpu_pct=node.cpu_utilization_pct,
                        memory_pct=node.memory_utilization_pct,
                        active_tasks=node.current_active_tasks,
                        status=NodeStatus.UNREACHABLE,
                    )
            return node
        except Exception as e:
            logger.error(f"Error checking heartbeat for node [{node.node_id}]: {e}")
            return node

    # [FUNCTION EXPLANATION]: Evaluates an entire map of cluster nodes and returns an updated node dictionary.
    def audit_cluster_nodes(self, nodes: Dict[str, Node]) -> Dict[str, Node]:
        """
        Audits all nodes in the cluster registry and updates status for stale nodes.

        Args:
            nodes (Dict[str, Node]): Map of node_id to Node instances.

        Returns:
            Dict[str, Node]: Updated node map.
        """
        updated_map: Dict[str, Node] = {}
        for node_id, node in nodes.items():
            updated_map[node_id] = self.evaluate_node_health(node)
        return updated_map
