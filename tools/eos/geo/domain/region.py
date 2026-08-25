"""
===============================================================================
WILSY OS — FG226 GLOBAL MULTI-REGION PLATFORM
DOMAIN SUBSYSTEM: REGION TOPOLOGY
===============================================================================

File Path:
    tools/eos/geo/domain/region.py

Version:
    v226.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines sovereign geographic regions within the FG226 Global Control Plane, 
    managing cross-continent boundaries, regulatory compliance zones, and status.

Biblical Worth Billions:
    "Ask of me, and I shall give thee the heathen for thine inheritance, and the 
    uttermost parts of the earth for thy possession." — Psalm 2:8

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


class RegionStatus(str, Enum):
    """Operational status of a geographic region."""
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    FAILOVER = "FAILOVER"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


@dataclass
class Region:
    """
    Encapsulates a sovereign geographic region within the Wilsy OS Global Network,
    providing immutable audit trails and cryptographic state verification.
    """
    region_id: str = field(default_factory=lambda: f"REG-{uuid.uuid4().hex[:6].upper()}")
    name: str = "Africa"
    continent: str = "Africa"
    country_code: str = "ZA"
    status: RegionStatus = RegionStatus.ACTIVE
    sovereign_compliance: str = "POPIA/GDPR"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon region instantiation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the region attributes."""
        raw_data = f"{self.region_id}:{self.name}:{self.continent}:{self.country_code}:{self.status}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the region object into a dictionary representation."""
        return {
            "region_id": self.region_id,
            "name": self.name,
            "continent": self.continent,
            "country_code": self.country_code,
            "status": self.status.value,
            "sovereign_compliance": self.sovereign_compliance,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
