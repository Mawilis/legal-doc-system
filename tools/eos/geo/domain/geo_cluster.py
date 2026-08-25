"""
===============================================================================
WILSY OS — FG226 GLOBAL MULTI-REGION PLATFORM
DOMAIN SUBSYSTEM: GEO CLUSTER TOPOLOGY
===============================================================================

File Path:
    tools/eos/geo/domain/geo_cluster.py

Version:
    v226.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Encapsulates a regional cluster deployment within the global multi-region 
    topology, managing node consensus groups and cluster health state.

Biblical Worth Billions:
    "A threefold cord is not quickly broken." — Ecclesiastes 4:12

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List


class ClusterStatus(str, Enum):
    """Operational status of a geo cluster."""
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    SYNCING = "SYNCING"
    OFFLINE = "OFFLINE"


@dataclass
class GeoCluster:
    """
    Represents a regional cluster within the Wilsy OS Global Control Plane,
    grouping compute nodes and managing replication state.
    """
    cluster_id: str = field(default_factory=lambda: f"GCLS-{uuid.uuid4().hex[:6].upper()}")
    region_id: str = "REG-DEFAULT"
    name: str = "jnb-cluster-01"
    status: ClusterStatus = ClusterStatus.ONLINE
    node_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon cluster instantiation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the cluster attributes."""
        nodes_sig = "".join(sorted(self.node_ids))
        raw_data = f"{self.cluster_id}:{self.region_id}:{self.name}:{self.status}:{nodes_sig}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the geo cluster into a dictionary representation."""
        return {
            "cluster_id": self.cluster_id,
            "region_id": self.region_id,
            "name": self.name,
            "status": self.status.value,
            "node_ids": self.node_ids,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
