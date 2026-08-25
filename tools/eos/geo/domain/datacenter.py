"""
===============================================================================
WILSY OS — FG226 GLOBAL MULTI-REGION PLATFORM
DOMAIN SUBSYSTEM: DATACENTER TOPOLOGY
===============================================================================

File Path:
    tools/eos/geo/domain/datacenter.py

Version:
    v226.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Models physical or sovereign colocation datacenters hosting compute nodes 
    across global availability zones, tracking power, cooling, and latency.

Biblical Worth Billions:
    "The preparations of the heart in man, and the answer of the tongue, is from the Lord." 
    — Proverbs 16:1

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
from typing import Dict, Any


class DCStatus(str, Enum):
    """Operational status of a datacenter facility."""
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    EMERGENCY_POWER = "EMERGENCY_POWER"
    OFFLINE = "OFFLINE"


@dataclass
class Datacenter:
    """
    Encapsulates a physical datacenter facility within an availability zone,
    tracking sovereign compliance, capacity limits, and status.
    """
    dc_id: str = field(default_factory=lambda: f"DC-{uuid.uuid4().hex[:6].upper()}")
    az_id: str = "AZ-DEFAULT"
    name: str = "JNB-DC-01"
    location: str = "Johannesburg, South Africa"
    status: DCStatus = DCStatus.ONLINE
    rack_capacity: int = 128
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon datacenter instantiation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the datacenter attributes."""
        raw_data = f"{self.dc_id}:{self.az_id}:{self.name}:{self.location}:{self.status}:{self.rack_capacity}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the datacenter into a dictionary representation."""
        return {
            "dc_id": self.dc_id,
            "az_id": self.az_id,
            "name": self.name,
            "location": self.location,
            "status": self.status.value,
            "rack_capacity": self.rack_capacity,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
