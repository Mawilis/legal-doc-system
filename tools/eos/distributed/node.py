"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Distributed Execution - Cluster Node Abstraction (FG157).
    Models physical and virtual compute nodes participating in the Wilsy OS 
    distributed execution fabric.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready node representation and resource tracking. Zero child's place.
    1 Corinthians 12:14 - "For the body is not one member, but many."

Collaboration & Maintenance:
    - [Architecture]: Atomic node structure tracking health, CPU, memory, and task capacity.
    - [Compliance]: Cryptographic node identity verification and status management.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict


class NodeStatus(str, Enum):
    """Lifecycle and operational status of a cluster node."""
    ONLINE = "ONLINE"
    BUSY = "BUSY"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    UNREACHABLE = "UNREACHABLE"


@dataclass(frozen=True)
class Node:
    """
    Immutable representation of a compute node within the distributed cluster topology.
    """
    node_id: str
    hostname: str
    ip_address: str
    max_task_capacity: int
    current_active_tasks: int = 0
    cpu_utilization_pct: float = 0.0
    memory_utilization_pct: float = 0.0
    status: NodeStatus = NodeStatus.ONLINE
    last_heartbeat: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # [FUNCTION EXPLANATION]: Factory constructor to initialize a new local or remote compute node.
    @classmethod
    def create(
        cls, 
        hostname: str, 
        ip_address: str = "127.0.0.1", 
        max_task_capacity: int = 8
    ) -> Node:
        """
        Creates a new Node instance with a unique cryptographic identifier.

        Args:
            hostname (str): System or cluster hostname.
            ip_address (str): Network address of the compute node.
            max_task_capacity (int): Maximum concurrent tasks allocated to this node.

        Returns:
            Node: Immutable node object.
        """
        node_id = f"node-{uuid.uuid4().hex[:12]}"
        return cls(
            node_id=node_id,
            hostname=hostname,
            ip_address=ip_address,
            max_task_capacity=max_task_capacity,
        )

    # [FUNCTION EXPLANATION]: Evaluates whether the node has spare capacity to accept an incoming task.
    def can_accept_task(self) -> bool:
        """
        Returns True if the node is ONLINE and has active task slots remaining.
        """
        return self.status == NodeStatus.ONLINE and self.current_active_tasks < self.max_task_capacity

    # [FUNCTION EXPLANATION]: Returns a new Node instance with updated resource telemetry metrics.
    def update_telemetry(
        self, 
        cpu_pct: float, 
        memory_pct: float, 
        active_tasks: int, 
        status: NodeStatus = NodeStatus.ONLINE
    ) -> Node:
        """
        Produces a updated frozen Node snapshot with fresh metrics and heartbeat timestamp.
        """
        data = asdict(self)
        data["cpu_utilization_pct"] = round(cpu_pct, 2)
        data["memory_utilization_pct"] = round(memory_pct, 2)
        data["current_active_tasks"] = active_tasks
        data["status"] = status
        data["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        return Node(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the node configuration into a dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serializes the node configuration into a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
