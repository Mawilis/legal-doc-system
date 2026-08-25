"""
===============================================================================
WILSY OS KERNEL ARCHITECTURE - ENTERPRISE ENGINEERING PLATFORM
===============================================================================
PROJECT: Wilsy OS (Billion-Dollar Sovereign Infrastructure)
SUBSYSTEM: Kernel ABI & Core Governance Framework
MILESTONE: FG178.5 - Kernel ABI Freeze
MODULE: kernel_version.py

COLLABORATION & ARCHITECTURAL NOTICE:
Defines immutable semantic versioning for the Wilsy OS Kernel ABI. Future
upgrades execute through explicitly versioned ABI increments rather than
silent or breaking structural modifications.
===============================================================================
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Tuple, Optional


class ABICompatibilityLevel(str, Enum):
    """Defines strict compatibility levels between runtime kernel and engine implementations."""
    EXACT = "EXACT"
    BACKWARD_COMPATIBLE = "BACKWARD_COMPATIBLE"
    DEPRECATED = "DEPRECATED"
    INCOMPATIBLE = "INCOMPATIBLE"


@dataclass(frozen=True)
class Version:
    """Semantic version representation for Wilsy OS kernel artifacts and interfaces."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.prerelease}" if self.prerelease else base

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    @classmethod
    def parse(cls, version_str: str) -> "Version":
        """Parse a semantic version string (e.g. '1.0.0' or '1.2.0-rc1')."""
        try:
            parts = version_str.strip().split("-")
            nums = [int(x) for x in parts[0].split(".")]
            prerelease = parts[1] if len(parts) > 1 else None
            return cls(major=nums[0], minor=nums[1], patch=nums[2], prerelease=prerelease)
        except Exception as err:
            raise ValueError(f"Invalid semantic version format string '{version_str}': {err}")

    def is_compatible_with(self, target: "Version") -> ABICompatibilityLevel:
        """Determines strict compatibility against a target kernel version."""
        if self.major != target.major:
            return ABICompatibilityLevel.INCOMPATIBLE
        if self.minor == target.minor and self.patch == target.patch:
            return ABICompatibilityLevel.EXACT
        if self.minor <= target.minor:
            return ABICompatibilityLevel.BACKWARD_COMPATIBLE
        return ABICompatibilityLevel.INCOMPATIBLE


# =============================================================================
# FROZEN KERNEL ABI SPECIFICATIONS (FG178.5 MANDATE)
# =============================================================================
KERNEL_VERSION: str = "1.0.0"
ABI_VERSION: str = "1.0"
RUNTIME_VERSION: str = "1.0"
ARTIFACT_VERSION: str = "1.0"
EVENT_VERSION: str = "1.0"
PROTOCOL_VERSION: str = "1.0"
SCHEMA_VERSION: str = "1.0"


@dataclass(frozen=True)
class KernelVersionSpec:
    """Comprehensive, immutable snapshot of active Wilsy OS Kernel Version identifiers."""
    kernel: Version = field(default_factory=lambda: Version.parse(KERNEL_VERSION))
    abi: str = ABI_VERSION
    runtime: str = RUNTIME_VERSION
    artifact: str = ARTIFACT_VERSION
    event: str = EVENT_VERSION
    protocol: str = PROTOCOL_VERSION
    schema: str = SCHEMA_VERSION

    def export_manifest(self) -> Dict[str, Any]:
        """Generates canonical dictionary representation for telemetry and attestations."""
        return {
            "kernel_version": str(self.kernel),
            "abi_version": self.abi,
            "runtime_version": self.runtime,
            "artifact_version": self.artifact,
            "event_version": self.event,
            "protocol_version": self.protocol,
            "schema_version": self.schema,
            "frozen_at_milestone": "FG178.5",
        }
