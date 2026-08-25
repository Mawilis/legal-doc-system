"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Enterprise Capability Registry Engine constructing the OS Brain index 
    and managing sovereign capability contracts for Wilsy OS.

Biblical Worth Billions:
    "The heart of the wise teacheth his mouth, and addeth learning to his lips." — Proverbs 16:23

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy OS)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/capability_registry/capability_registry_engine.py
===============================================================================
"""

from __future__ import annotations

import json
import os
import logging
from typing import Dict, Any, List, Optional

from.capability_models import (
    CapabilityMetadata,
    CapabilityRegistryCatalog,
    CapabilityCriticality,
    CapabilityLifecycleState,
)
from.capability_contracts import CapabilityContractValidator

logger = logging.getLogger("WilsyOS.FG231C.CapabilityRegistryEngine")


class CapabilityRegistryEngine:
    """
    Sovereign capability engine responsible for aggregating, validating,
    and persisting the master Enterprise Capability Registry catalog.
    """

    def __init__(self, primary_output_path: str = "reports/CapabilityRegistry.json") -> None:
        self.primary_output_path = primary_output_path
        self.catalog = CapabilityRegistryCatalog()

    def add_capability(self, capability: CapabilityMetadata) -> None:
        """
        Registers a verified capability into the sovereign brain index.
        """
        self.catalog.add_capability(capability)

    def get_capability(self, capability_id: str) -> Optional[CapabilityMetadata]:
        """
        Retrieves a capability by its unique identifier.
        """
        return self.catalog.get_capability(capability_id)

    def list_capabilities(self) -> List[CapabilityMetadata]:
        """
        Lists all registered capabilities in the sovereign brain index.
        """
        return list(self.catalog.capabilities.values())

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the entire capability registry catalog into a JSON-compatible dictionary.
        """
        return self.catalog.to_dict()

    def build_core_capabilities(self) -> CapabilityRegistryCatalog:
        """
        Instantiates and validates the foundational enterprise capabilities.
        """
        core_capabilities = [
            CapabilityMetadata(
                capability_id="CAP-REPOSITORY-SCAN",
                name="Repository Intelligence Engine",
                purpose="Scans repository assets, AST structures, and dependency vectors across all code bases.",
                owner="Repository Intelligence Subsystem",
                inputs=["Filesystem", "Git HEAD Commit"],
                outputs=["Repository Inventory", "AST Graph Index"],
                dependencies=[],
                produces_events=["REPOSITORY_CHANGED"],
                consumes_events=["SCAN_TRIGGERED"],
                business_value="$1.0B Sovereign OS Asset Map",
                criticality=CapabilityCriticality.SOVEREIGN,
                reuse_score=0.98,
                execution_cost="0.001 ms",
                lifecycle_state=CapabilityLifecycleState.ACTIVE,
                security_level="LEVEL_5_SOVEREIGN",
                confidence=1.00,
            ),
            CapabilityMetadata(
                capability_id="CAP-KNOWLEDGE-SYNCHRONIZATION",
                name="Knowledge Graph Engine",
                purpose="Synchronizes enterprise semantic knowledge, concept bindings, and graph linkages.",
                owner="Knowledge Subsystem",
                inputs=["Repository Inventory", "Capability Registry"],
                outputs=["Knowledge Graph Index"],
                dependencies=["CAP-REPOSITORY-SCAN"],
                produces_events=["KNOWLEDGE_REFRESHED"],
                consumes_events=["REPOSITORY_CHANGED"],
                business_value="$500M Enterprise Context Anchor",
                criticality=CapabilityCriticality.HIGH,
                reuse_score=0.95,
                execution_cost="0.001 ms",
                lifecycle_state=CapabilityLifecycleState.ACTIVE,
                security_level="LEVEL_4_ENTERPRISE",
                confidence=0.99,
            ),
            CapabilityMetadata(
                capability_id="CAP-PREDICTIVE-RISK-ASSESSMENT",
                name="Predictive Risk Engine",
                purpose="Calculates architectural blast radius, complexity metrics, and potential failure cascades.",
                owner="Predictive Systems",
                inputs=["Dependency Graph", "Change Vectors"],
                outputs=["Risk Assessment Matrix"],
                dependencies=["CAP-KNOWLEDGE-SYNCHRONIZATION"],
                produces_events=["RISK_ASSESSED"],
                consumes_events=["KNOWLEDGE_REFRESHED"],
                business_value="$750M Sovereign Risk Mitigation",
                criticality=CapabilityCriticality.MISSION_CRITICAL,
                reuse_score=0.91,
                execution_cost="0.001 ms",
                lifecycle_state=CapabilityLifecycleState.ACTIVE,
                security_level="LEVEL_4_ENTERPRISE",
                confidence=0.97,
            ),
            CapabilityMetadata(
                capability_id="CAP-GOVERNANCE-COMPLIANCE",
                name="Governance & Compliance Engine",
                purpose="Verifies cryptographic integrity, policy adherence, and zero-trust attestation.",
                owner="Governance Subsystem",
                inputs=["Repository Delta", "Policy Contracts"],
                outputs=["Compliance Attestation"],
                dependencies=["CAP-PREDICTIVE-RISK-ASSESSMENT"],
                produces_events=["COMPLIANCE_ATTESTED"],
                consumes_events=["RISK_ASSESSED"],
                business_value="$1.0B Sovereign OS Governance",
                criticality=CapabilityCriticality.SOVEREIGN,
                reuse_score=1.00,
                execution_cost="0.001 ms",
                lifecycle_state=CapabilityLifecycleState.ACTIVE,
                security_level="LEVEL_5_SOVEREIGN",
                confidence=1.00,
            ),
            CapabilityMetadata(
                capability_id="CAP-EXECUTIVE-CONTROL-ROOM",
                name="Executive Control Room Engine",
                purpose="Dispatches real-time telemetry, event notifications, and AI operator alerts.",
                owner="Control Room Subsystem",
                inputs=["Event Graph Telemetry", "Digital Twin State"],
                outputs=["Live Dashboard Telemetry"],
                dependencies=["CAP-GOVERNANCE-COMPLIANCE"],
                produces_events=["DASHBOARD_UPDATED"],
                consumes_events=["COMPLIANCE_ATTESTED"],
                business_value="$1.0B Real-Time OS Monitoring",
                criticality=CapabilityCriticality.MISSION_CRITICAL,
                reuse_score=0.96,
                execution_cost="0.001 ms",
                lifecycle_state=CapabilityLifecycleState.ACTIVE,
                security_level="LEVEL_5_SOVEREIGN",
                confidence=0.99,
            ),
        ]

        for capability in core_capabilities:
            is_valid, errors = CapabilityContractValidator.validate(capability)
            if is_valid:
                self.catalog.add_capability(capability)
            else:
                logger.error(f"Capability contract validation failed for {capability.capability_id}: {errors}")
                raise ValueError(f"Capability contract validation failed for {capability.capability_id}: {errors}")

        return self.catalog

    def execute_and_save(self) -> Dict[str, Any]:
        """
        Executes the capability registry engine and persists the catalog to disk.
        """
        logger.info("Executing Capability Registry Engine...")
        self.build_core_capabilities()

        catalog_dict = self.catalog.to_dict()

        # Primary persistence target (reports/)
        os.makedirs(os.path.dirname(self.primary_output_path), exist_ok=True)
        with open(self.primary_output_path, "w", encoding="utf-8") as f:
            json.dump(catalog_dict, f, indent=2)

        # Local module mirror target
        local_dir = os.path.dirname(__file__)
        local_target = os.path.join(local_dir, "capability_registry.json")
        with open(local_target, "w", encoding="utf-8") as f:
            json.dump(catalog_dict, f, indent=2)

        logger.info(f"Successfully registered {len(self.catalog.capabilities)} capabilities into {self.primary_output_path}")
        return catalog_dict