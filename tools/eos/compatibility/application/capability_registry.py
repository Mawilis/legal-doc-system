"""
===============================================================================
WILSY OS — PLATFORM CAPABILITY REGISTRY (FG208)
===============================================================================
Epitome:
    Serves as the sovereign platform's feature catalogue for enterprise capabilities.
    Provides capability registration, feature negotiation, maturity tracking, and
    kernel dependency resolution across all core and extension subsystems.

Biblical Worth Billions:
    "For as the body is one, and hath many members, and all the members of that
    one body, being many, are one body: so also is Christ."
    — 1 Corinthians 12:12

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/application/capability_registry.py
===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Tuple

logger = logging.getLogger("WilsyOS.Compatibility.CapabilityRegistry")


class PlatformCapability(str, Enum):
    """
    Standard enumeration of sovereign kernel and subsystem feature capabilities.
    """
    EXECUTION_CONTEXT = "ExecutionContext"
    EVENT_BUS = "EventBus"
    ARTIFACT_BUS = "ArtifactBus"
    ENGINE_REGISTRY = "EngineRegistry"
    SCHEDULER = "Scheduler"
    DASHBOARD = "Dashboard"
    DIGITAL_TWIN = "DigitalTwin"
    SENTINEL = "Sentinel"
    KNOWLEDGE_GRAPH = "KnowledgeGraph"
    MEMORY = "Memory"
    REPLAY = "Replay"
    GOVERNANCE = "Governance"
    OBSERVABILITY = "Observability"
    AI_REASONING = "AiReasoning"
    PREDICTION = "PredictionEngine"
    COMMAND_CENTER = "CommandCenter"


@dataclass(frozen=True)
class CapabilityMetadata:
    """Metadata descriptor for a platform capability entry."""
    name: str
    description: str
    is_core: bool
    introduced_in_kernel: str
    maturity_level: str  # GA, BETA, EXPERIMENTAL

    def to_dict(self) -> Dict[str, Any]:
        """Serializes capability descriptor to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "is_core": self.is_core,
            "introduced_in_kernel": self.introduced_in_kernel,
            "maturity_level": self.maturity_level
        }


class CapabilityRegistry:
    """
    Application registry managing available platform capabilities and feature negotiation.
    """

    def __init__(self) -> None:
        self._capabilities: Dict[str, CapabilityMetadata] = {}
        self._bootstrap_default_capabilities()

    def _bootstrap_default_capabilities(self) -> None:
        """Populates default kernel capabilities across execution, governance, and autonomy."""
        defaults = [
            CapabilityMetadata(PlatformCapability.EXECUTION_CONTEXT.value, "Sovereign runtime context and execution state", True, "1.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.EVENT_BUS.value, "Distributed asynchronous event communication bus", True, "1.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.ARTIFACT_BUS.value, "Cryptographic artifact storage and attestation bus", True, "1.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.ENGINE_REGISTRY.value, "Plugin engine lifecycle and registration store", True, "1.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.SCHEDULER.value, "Distributed task scheduler and worker dispatcher", True, "1.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.DASHBOARD.value, "Executive telemetry and status reporting dashboard", False, "1.5.0", "GA"),
            CapabilityMetadata(PlatformCapability.DIGITAL_TWIN.value, "Enterprise digital twin runtime state model", False, "2.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.SENTINEL.value, "Real-time threat monitoring and invariant protection", True, "2.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.KNOWLEDGE_GRAPH.value, "Graph database and semantic edge network", True, "2.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.MEMORY.value, "Institutional persistent memory vector engine", True, "2.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.REPLAY.value, "Deterministic state snapshot replay engine", True, "2.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.GOVERNANCE.value, "Policy assertion engine and safety gatekeeper", True, "1.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.OBSERVABILITY.value, "OpenTelemetry traces and resource metrics", True, "2.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.AI_REASONING.value, "Autonomous reasoning and decision synthesis", False, "2.0.0", "BETA"),
            CapabilityMetadata(PlatformCapability.PREDICTION.value, "Predictive load trend and anomaly forecasting", False, "2.0.0", "GA"),
            CapabilityMetadata(PlatformCapability.COMMAND_CENTER.value, "Global enterprise administration and orchestration", False, "2.0.0", "GA"),
        ]
        for cap in defaults:
            self.register_capability(cap)

    def register_capability(self, metadata: CapabilityMetadata) -> None:
        """Registers or updates a capability in the platform catalogue."""
        self._capabilities[metadata.name] = metadata
        logger.debug("Capability registered: %s (%s)", metadata.name, metadata.maturity_level)

    def has_capability(self, capability_name: str) -> bool:
        """Checks whether a specific capability is present in the registry."""
        return capability_name in self._capabilities

    def get_all_capabilities(self) -> List[CapabilityMetadata]:
        """Returns all registered capability descriptors."""
        return list(self._capabilities.values())

    def get_core_capabilities(self) -> List[str]:
        """Returns list of names for all core capabilities."""
        return [cap.name for cap in self._capabilities.values() if cap.is_core]

    def get_extension_capabilities(self) -> List[str]:
        """Returns list of names for all extension capabilities."""
        return [cap.name for cap in self._capabilities.values() if not cap.is_core]

    def evaluate_capability_requirements(
        self,
        required: List[str],
        optional: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Evaluates requested capabilities against available registry capabilities.
        
        Returns:
            Tuple of (missing_required_capabilities, available_optional_capabilities)
        """
        available = set(self._capabilities.keys())
        missing_required = [cap for cap in required if cap not in available]
        available_optional = [cap for cap in optional if cap in available]
        return sorted(missing_required), sorted(available_optional)
