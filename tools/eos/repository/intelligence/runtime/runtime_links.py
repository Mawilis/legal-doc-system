"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Runtime linkage models binding platform capabilities and codebase AST nodes 
    to live execution metrics, health statuses, and runtime telemetry streams.

Biblical Worth Billions:
    "He that keepeth the commandment keepeth his own soul; but he that 
    despiseth his ways shall die." — Proverbs 19:16

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy OS)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/runtime/runtime_links.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional


class RuntimeStatus(str, Enum):
    """Execution status for active runtime capability bindings."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    INACTIVE = "INACTIVE"


@dataclass
class RuntimeLink:
    """
    Binds a capability or architectural node to real-time performance metrics,
    latency SLA tracking, error rate vectors, and runtime execution status.
    """
    capability_id: str
    status: RuntimeStatus
    avg_latency_ms: float
    error_rate_percentage: float
    throughput_rps: float
    monitored_endpoints: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes runtime link model to a dictionary."""
        data = asdict(self)
        data["status"] = self.status.value if isinstance(self.status, RuntimeStatus) else str(self.status)
        return data


@dataclass
class RuntimeLinkCatalog:
    """
    Catalog holding active runtime telemetry links across system capabilities.
    """
    links: Dict[str, RuntimeLink] = field(default_factory=dict)

    def add_link(self, link: RuntimeLink) -> None:
        """Registers a capability runtime telemetry link."""
        self.links[link.capability_id] = link

    def get_link(self, capability_id: str) -> Optional[RuntimeLink]:
        """Retrieves runtime telemetry link for a given capability ID."""
        return self.links.get(capability_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes runtime link catalog to dictionary representation."""
        return {
            "total_links": len(self.links),
            "links": {k: v.to_dict() for k, v in self.links.items()},
        }