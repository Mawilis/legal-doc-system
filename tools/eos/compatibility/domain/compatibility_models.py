"""
===============================================================================
WILSY OS — PLATFORM ARCHITECTURE PROTECTION & COMPATIBILITY ENGINE (FG208)
===============================================================================
Epitome:
    Defines immutable domain models, compatibility blocks, and status boundaries 
    for Kernel FG208. Enforces deterministic ABI version negotiation, capability 
    matching, and immutable decision generation to ensure zero-breaking-change 
    platform longevity.

Biblical Worth Billions:
    "Remove not the ancient landmark, which thy fathers have set."
    — Proverbs 22:28

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/domain/compatibility_models.py
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class CompatibilityStatus(str, Enum):
    """
    Strict 4-value enumeration governing engine execution clearance.
    
    COMPATIBLE: Engine natively matches Kernel ABI and capability requirements.
    ADAPTER_REQUIRED: Engine requires a version migration adapter wrapper.
    INCOMPATIBLE: Version boundaries or mandatory capability gaps prevent execution.
    REJECTED: Security violation, policy failure, or corrupt descriptor payload.
    """
    COMPATIBLE = "COMPATIBLE"
    ADAPTER_REQUIRED = "ADAPTER_REQUIRED"
    INCOMPATIBLE = "INCOMPATIBLE"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class EngineCompatibilityBlock:
    """
    Immutable compatibility block exposed by every Wilsy OS engine descriptor.
    
    Attributes:
        engine_id: Unique identifier for the enterprise engine plugin.
        engine_version: Semantic version of the engine payload.
        abi_version: Targeted ABI version contract (e.g., '2.0').
        minimum_kernel_version: Floor kernel version required for execution.
        maximum_kernel_version: Ceiling kernel version supported before upgrade.
        required_capabilities: Mandatory feature capabilities required from Kernel.
        optional_capabilities: Desirable capabilities utilized if present.
    """
    engine_id: str
    engine_version: str
    abi_version: str
    minimum_kernel_version: str
    maximum_kernel_version: str
    required_capabilities: List[str] = field(default_factory=list)
    optional_capabilities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes descriptor block to dictionary representation."""
        return {
            "engine_id": self.engine_id,
            "engine_version": self.engine_version,
            "abi_version": self.abi_version,
            "minimum_kernel_version": self.minimum_kernel_version,
            "maximum_kernel_version": self.maximum_kernel_version,
            "required_capabilities": list(self.required_capabilities),
            "optional_capabilities": list(self.optional_capabilities),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EngineCompatibilityBlock:
        """Instantiates descriptor block from raw dictionary data."""
        return cls(
            engine_id=data["engine_id"],
            engine_version=data["engine_version"],
            abi_version=data["abi_version"],
            minimum_kernel_version=data["minimum_kernel_version"],
            maximum_kernel_version=data["maximum_kernel_version"],
            required_capabilities=list(data.get("required_capabilities", [])),
            optional_capabilities=list(data.get("optional_capabilities", [])),
        )


@dataclass(frozen=True)
class CompatibilityDecision:
    """
    Immutable, cryptographically sealed decision object produced by the Compatibility Engine.
    
    Guarantees that no scheduler dispatch occurs without an authoritative, 
    tamper-evident clearance record.
    """
    execution_id: str
    engine_id: str
    kernel_version: str
    engine_version: str
    abi_version: str
    required_capabilities: List[str]
    optional_capabilities: List[str]
    missing_capabilities: List[str]
    adapter_selected: Optional[str]
    status: CompatibilityStatus
    checksum: str

    @classmethod
    def create(
        cls,
        execution_id: str,
        engine_id: str,
        kernel_version: str,
        engine_version: str,
        abi_version: str,
        required_capabilities: List[str],
        optional_capabilities: List[str],
        missing_capabilities: List[str],
        adapter_selected: Optional[str],
        status: CompatibilityStatus
    ) -> CompatibilityDecision:
        """
        Factory method that calculates SHA3-256 checksum across all fields 
        to guarantee decision immutability and auditability.
        """
        payload = {
            "execution_id": execution_id,
            "engine_id": engine_id,
            "kernel_version": kernel_version,
            "engine_version": engine_version,
            "abi_version": abi_version,
            "required_capabilities": sorted(required_capabilities),
            "optional_capabilities": sorted(optional_capabilities),
            "missing_capabilities": sorted(missing_capabilities),
            "adapter_selected": adapter_selected or "NONE",
            "status": status.value,
        }
        serialized_payload = json.dumps(payload, sort_keys=True).encode('utf-8')
        digest = hashlib.sha3_256(serialized_payload).hexdigest()

        return cls(
            execution_id=execution_id,
            engine_id=engine_id,
            kernel_version=kernel_version,
            engine_version=engine_version,
            abi_version=abi_version,
            required_capabilities=list(required_capabilities),
            optional_capabilities=list(optional_capabilities),
            missing_capabilities=list(missing_capabilities),
            adapter_selected=adapter_selected,
            status=status,
            checksum=digest
        )

    def is_executable(self) -> bool:
        """Determines whether scheduler dispatch is authorized based on decision status."""
        return self.status in (CompatibilityStatus.COMPATIBLE, CompatibilityStatus.ADAPTER_REQUIRED)

    def verify_checksum(self) -> bool:
        """Validates that internal checksum matches calculated SHA3-256 digest."""
        recalculated = CompatibilityDecision.create(
            execution_id=self.execution_id,
            engine_id=self.engine_id,
            kernel_version=self.kernel_version,
            engine_version=self.engine_version,
            abi_version=self.abi_version,
            required_capabilities=self.required_capabilities,
            optional_capabilities=self.optional_capabilities,
            missing_capabilities=self.missing_capabilities,
            adapter_selected=self.adapter_selected,
            status=self.status
        )
        return recalculated.checksum == self.checksum

    def to_dict(self) -> Dict[str, Any]:
        """Serializes immutable decision to dictionary format."""
        return {
            "execution_id": self.execution_id,
            "engine_id": self.engine_id,
            "kernel_version": self.kernel_version,
            "engine_version": self.engine_version,
            "abi_version": self.abi_version,
            "required_capabilities": list(self.required_capabilities),
            "optional_capabilities": list(self.optional_capabilities),
            "missing_capabilities": list(self.missing_capabilities),
            "adapter_selected": self.adapter_selected,
            "status": self.status.value,
            "checksum": self.checksum,
        }
