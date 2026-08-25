"""
===============================================================================
WILSY OS — FG226 GLOBAL MULTI-REGION PLATFORM
DOMAIN SUBSYSTEM: AVAILABILITY ZONE TOPOLOGY
===============================================================================

File Path:
    tools/eos/geo/domain/availability_zone.py

Version:
    v226.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Encapsulates isolated availability zones (AZs) within a geographic region,
    ensuring fault-tolerant multi-zone deployments and independent power/networking.

Biblical Worth Billions:
    "Two are better than one; because they have a good reward for their labour." 
    — Ecclesiastes 4:9

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


class AZStatus(str, Enum):
    """Operational status of an availability zone."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


@dataclass
class AvailabilityZone:
    """
    Represents a distinct availability zone within a sovereign region, 
    guaranteeing isolated failure domains and fault tolerance.
    """
    az_id: str = field(default_factory=lambda: f"AZ-{uuid.uuid4().hex[:6].upper()}")
    region_id: str = "REG-DEFAULT"
    name: str = "af-south-1a"
    status: AZStatus = AZStatus.HEALTHY
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon AZ instantiation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the AZ attributes."""
        raw_data = f"{self.az_id}:{self.region_id}:{self.name}:{self.status}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the availability zone into a dictionary representation."""
        return {
            "az_id": self.az_id,
            "region_id": self.region_id,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
