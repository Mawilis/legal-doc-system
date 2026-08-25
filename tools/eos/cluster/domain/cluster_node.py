"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/domain/cluster_node.py

Epitome:
    Domain entity representing a compute host node within the Wilsy OS
    cluster topology. Manages node hardware metadata, hosted worker instances,
    and aggregate compute resource utilization metrics.

Biblical Worth Billions:
    "Upon this rock I will build my church; and the gates of hell shall not 
    prevail against it."
    — Matthew 16:18

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Union

from tools.eos.cluster.domain.worker import Worker


@dataclass
class ClusterNode:
    """
    Domain model representing a host server / compute node.
    
    Attributes:
        node_id: Unique string identifier for the host node.
        hostname: Network FQDN or hostname of the node.
        ip_address: IPv4/IPv6 network address.
        cpu_cores: Number of logical CPU cores allocated.
        memory_gb: Total RAM allocated in Gigabytes.
        tags: Categorical key-value pairs for metadata filtering.
        workers: Dictionary mapping worker_id -> Worker instance hosted on this node.
        is_active: Whether the node is currently accepting job deployments.
        registered_at: UTC timestamp when the node joined the cluster.
    """
    node_id: str
    hostname: str
    ip_address: str = "127.0.0.1"
    cpu_cores: int = 8
    memory_gb: float = 16.0
    tags: Dict[str, str] = field(default_factory=dict)
    workers: Dict[str, Worker] = field(default_factory=dict)
    is_active: bool = True
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def attached_workers(self) -> Set[str]:
        """Returns the set of all worker IDs bound to this node."""
        return set(self.workers.keys())

    def attach_worker(self, worker: Union[Worker, str]) -> None:
        """Binds an execution worker or worker ID to this host node."""
        if isinstance(worker, Worker):
            worker.node_id = self.node_id
            self.workers[worker.worker_id] = worker
        elif isinstance(worker, str):
            # If string ID is passed directly, track worker ID key
            if worker not in self.workers:
                # Placeholder worker reference until full entity attached
                self.workers[worker] = Worker(worker_id=worker, node_id=self.node_id)

    def detach_worker(self, worker_id: str) -> Optional[Worker]:
        """Unbinds and returns a worker from this node if present."""
        return self.workers.pop(worker_id, None)

    @property
    def total_capacity(self) -> int:
        """Aggregates maximum worker task slots on this node."""
        return sum(w.max_capacity for w in self.workers.values() if isinstance(w, Worker))

    @property
    def current_load(self) -> int:
        """Aggregates currently executing tasks across all hosted workers."""
        return sum(w.current_load for w in self.workers.values() if isinstance(w, Worker))

    @property
    def load_factor(self) -> float:
        """Calculates aggregate node load ratio (0.0 to 1.0)."""
        tot = self.total_capacity
        if tot == 0:
            return 0.0
        return min(1.0, float(self.current_load) / float(tot))

    @property
    def health_score(self) -> float:
        """Calculates average health score across hosted workers."""
        valid_workers = [w for w in self.workers.values() if isinstance(w, Worker)]
        if not valid_workers:
            return 100.0 if self.is_active else 0.0
        return float(sum(w.health_score for w in valid_workers)) / float(len(valid_workers))

    def get_aggregate_capabilities(self) -> Set[str]:
        """Returns union of all capabilities provided by workers on this node."""
        caps: Set[str] = set()
        for w in self.workers.values():
            if not isinstance(w, Worker):
                continue
            w_caps = w.capabilities
            if isinstance(w_caps, (set, list, tuple)):
                caps.update(w_caps)
            elif hasattr(w_caps, "to_list"):
                to_list_fn = getattr(w_caps, "to_list")
                caps.update(to_list_fn())
            elif hasattr(w_caps, "capabilities"):
                inner = getattr(w_caps, "capabilities")
                if isinstance(inner, (set, list, tuple)):
                    caps.update(inner)
        return caps

    def to_dict(self) -> Dict[str, Any]:
        """Serializes node entity into dictionary representation."""
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "cpu_cores": self.cpu_cores,
            "memory_gb": self.memory_gb,
            "tags": self.tags,
            "is_active": self.is_active,
            "total_capacity": self.total_capacity,
            "current_load": self.current_load,
            "load_factor": self.load_factor,
            "health_score": round(self.health_score, 2),
            "worker_ids": list(self.workers.keys()),
            "registered_at": self.registered_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClusterNode":
        """Instantiates a ClusterNode entity from dictionary data."""
        reg_str = data.get("registered_at")
        reg_dt = datetime.fromisoformat(reg_str) if reg_str else datetime.now(timezone.utc)

        return cls(
            node_id=str(data["node_id"]),
            hostname=str(data["hostname"]),
            ip_address=str(data.get("ip_address", "127.0.0.1")),
            cpu_cores=int(data.get("cpu_cores", 8)),
            memory_gb=float(data.get("memory_gb", 16.0)),
            tags=data.get("tags", {}),
            is_active=bool(data.get("is_active", True)),
            registered_at=reg_dt
        )
