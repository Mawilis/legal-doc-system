"""
===============================================================================
WILSY OS — FG226 GLOBAL MULTI-REGION PLATFORM
DOMAIN SUBSYSTEM: GEO WORKER TOPOLOGY
===============================================================================

File Path:
    tools/eos/geo/domain/geo_worker.py

Version:
    v226.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Manages execution workers bound to specific geo-nodes within the Global 
    Control Plane, tracking load, active tasks, and throughput capacity.

Biblical Worth Billions:
    "Whatsoever thy hand findeth to do, do it with thy might." — Ecclesiastes 9:10

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any


@dataclass
class GeoWorker:
    """
    Encapsulates a distributed execution worker operating within a geo-node,
    monitoring load and execution capacity across international zones.
    """
    worker_id: str = field(default_factory=lambda: f"GWRK-{uuid.uuid4().hex[:6].upper()}")
    node_id: str = "GNODE-DEFAULT"
    region: str = "Africa"
    load_percent: float = 12.5
    max_concurrency: int = 64
    status: str = "IDLE"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon worker instantiation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the geo worker attributes."""
        raw_data = f"{self.worker_id}:{self.node_id}:{self.region}:{self.load_percent}:{self.max_concurrency}:{self.status}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the geo worker into a dictionary representation."""
        return {
            "worker_id": self.worker_id,
            "node_id": self.node_id,
            "region": self.region,
            "load_percent": self.load_percent,
            "max_concurrency": self.max_concurrency,
            "status": self.status,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
