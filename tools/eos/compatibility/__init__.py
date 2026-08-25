"""
===============================================================================
WILSY OS — COMPATIBILITY SUBSYSTEM PACKAGE EXPORTS (FG208)
===============================================================================
Epitome:
    Unified public API surface for Kernel FG208 Compatibility & Version Negotiation.
    Exposes domain models, capability registries, migration adapters, application
    services, and reporting builders to the broader Wilsy OS architecture.

Biblical Worth Billions:
    "Bind up the testimony, seal the law among my disciples."
    — Isaiah 8:16

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/__init__.py
===============================================================================
"""

from tools.eos.compatibility.domain.compatibility_models import (
    CompatibilityStatus,
    EngineCompatibilityBlock,
    CompatibilityDecision,
)
from tools.eos.compatibility.domain.abi_contract import (
    SemanticVersion,
    KernelABIContract,
)
from tools.eos.compatibility.domain.compatibility_result import (
    CompatibilityEvaluationLog,
    CompatibilityEvaluationResult,
)
from tools.eos.compatibility.application.capability_registry import (
    PlatformCapability,
    CapabilityMetadata,
    CapabilityRegistry,
)
from tools.eos.compatibility.adapters.base_adapter import BaseCompatibilityAdapter
from tools.eos.compatibility.adapters.abi_v1_adapter import ABIV1ToV2Adapter
from tools.eos.compatibility.adapters.abi_v2_adapter import ABIV2NativeAdapter
from tools.eos.compatibility.application.adapter_manager import AdapterManager
from tools.eos.compatibility.application.compatibility_engine import CompatibilityEngine
from tools.eos.compatibility.reporting.compatibility_artifact import CompatibilityReportArtifact
from tools.eos.compatibility.reporting.compatibility_report_builder import CompatibilityReportBuilder
from tools.eos.compatibility.reporting.pdf_report_generator import CompatibilityPDFReportGenerator

__all__ = [
    # Domain Models
    "CompatibilityStatus",
    "EngineCompatibilityBlock",
    "CompatibilityDecision",
    "SemanticVersion",
    "KernelABIContract",
    "CompatibilityEvaluationLog",
    "CompatibilityEvaluationResult",
    # Capability Application Services
    "PlatformCapability",
    "CapabilityMetadata",
    "CapabilityRegistry",
    # Adapters
    "BaseCompatibilityAdapter",
    "ABIV1ToV2Adapter",
    "ABIV2NativeAdapter",
    "AdapterManager",
    # Core Engine
    "CompatibilityEngine",
    # Reporting
    "CompatibilityReportArtifact",
    "CompatibilityReportBuilder",
    "CompatibilityPDFReportGenerator",
]
