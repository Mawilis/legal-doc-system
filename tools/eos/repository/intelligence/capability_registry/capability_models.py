"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Sovereign data models defining enterprise capability structures, rich 
    operational metadata, confidence metrics, lifecycle state bounds, and 
    event interface contracts for the Wilsy OS Enterprise Nervous System.

Biblical Worth Billions:
    "Whithersoever the spirit was to go, they went, thither was their spirit to go; 
    and the wheels were lifted up over against them: for the spirit of the living 
    creature was in the wheels." — Ezekiel 1:20

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/capability_registry/capability_models.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional


class CapabilityCriticality(str, Enum):
    """Enumeration of strict enterprise criticality tiers."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    MISSION_CRITICAL = "MISSION_CRITICAL"
    SOVEREIGN = "SOVEREIGN"


class CapabilityLifecycleState(str, Enum):
    """Lifecycle state bounds for registered platform capabilities."""
    EXPERIMENTAL = "EXPERIMENTAL"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


@dataclass
class CapabilityMetadata:
    """
    Sovereign metadata record for every executable capability in Wilsy OS.
    Enables zero-scan instant awareness for the AI operator and runtime event bus.
    """
    capability_id: str
    name: str
    purpose: str
    owner: str
    inputs: List[str]
    outputs: List[str]
    dependencies: List[str]
    produces_events: List[str]
    consumes_events: List[str]
    business_value: str
    criticality: CapabilityCriticality
    reuse_score: float
    execution_cost: str
    lifecycle_state: CapabilityLifecycleState
    security_level: str
    confidence: float
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Converts the capability metadata object into a serializable dictionary representation."""
        data = asdict(self)
        data["criticality"] = self.criticality.value if isinstance(self.criticality, CapabilityCriticality) else str(self.criticality)
        data["lifecycle_state"] = self.lifecycle_state.value if isinstance(self.lifecycle_state, CapabilityLifecycleState) else str(self.lifecycle_state)
        return data


@dataclass
class CapabilityRegistryCatalog:
    """
    Master container object representing the entire Enterprise Capability Brain catalog.
    """
    schema_version: str = "2.0.0"
    total_capabilities: int = 0
    capabilities: Dict[str, CapabilityMetadata] = field(default_factory=dict)

    def add_capability(self, cap: CapabilityMetadata) -> None:
        """Registers a verified capability into the sovereign brain index."""
        self.capabilities[cap.capability_id] = cap
        self.total_capabilities = len(self.capabilities)

    def get_capability(self, capability_id: str) -> Optional[CapabilityMetadata]:
        """Retrieves a capability by its unique identifier."""
        return self.capabilities.get(capability_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the entire catalog to JSON-compatible dictionary."""
        return {
            "schema_version": self.schema_version,
            "total_capabilities": self.total_capabilities,
            "capabilities": {k: v.to_dict() for k, v in self.capabilities.items()}
        }