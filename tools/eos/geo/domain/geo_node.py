"""
===============================================================================
WILSY OS — FG226 GLOBAL MULTI-REGION PLATFORM
DOMAIN SUBSYSTEM: GEO NODE TOPOLOGY & METADATA
===============================================================================

File Path:
    tools/eos/geo/domain/geo_node.py

Version:
    v226.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Enriches compute nodes with global geo-metadata (latitude, longitude, region, 
    availability zone, priority, health, replication group, and capabilities).

Biblical Worth Billions:
    "The earth is the Lord's, and the fulness thereof; the world, and they that dwell therein." 
    — Psalm 24:1

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List


@dataclass
class GeoNode:
    """
    Represents an enriched sovereign compute node across global data centers,
    tracking coordinates, priority routing weight, health status, and capabilities.
    """
    node_id: str = field(default_factory=lambda: f"GNODE-{uuid.uuid4().hex[:6].upper()}")
    region: str = "Africa"
    availability_zone: str = "af-south-1a"
    country: str = "South Africa"
    latitude: float = -26.2041
    longitude: float = 28.0473
    priority: int = 100
    health: str = "HEALTHY"
    cluster: str = "jnb-cluster-01"
    replication_group: str = "RG-GLOBAL-PRIMARY"
    capabilities: List[str] = field(default_factory=lambda: ["compute", "storage", "ai_inference"])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon node instantiation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the geo node attributes."""
        caps_sig = "".join(sorted(self.capabilities))
        raw_data = f"{self.node_id}:{self.region}:{self.availability_zone}:{self.latitude}:{self.longitude}:{self.priority}:{self.health}:{caps_sig}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the geo node into a dictionary representation."""
        return {
            "node_id": self.node_id,
            "region": self.region,
            "availability_zone": self.availability_zone,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "priority": self.priority,
            "health": self.health,
            "cluster": self.cluster,
            "replication_group": self.replication_group,
            "capabilities": self.capabilities,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
