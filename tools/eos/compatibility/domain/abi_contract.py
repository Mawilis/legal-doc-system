"""
===============================================================================
WILSY OS — KERNEL ABI CONTRACT DOMAIN MODEL (FG208)
===============================================================================
Epitome:
    Defines the formal Kernel ABI Contract specifications for Wilsy OS.
    Encapsulates supported ABI major/minor versions, target kernel release numbers,
    supported capabilities, and semantic version constraint evaluation logic 
    to enforce platform backward and forward compatibility.

Biblical Worth Billions:
    "Thy word is a lamp unto my feet, and a light unto my path."
    — Psalm 119:105

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/domain/abi_contract.py
===============================================================================
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional


@dataclass(frozen=True)
class SemanticVersion:
    """
    Immutable representation of a semantic version string (e.g., '2.0.0' or '2.0').
    Supports comparison operators for bound verification.
    """
    major: int
    minor: int
    patch: int = 0

    @classmethod
    def parse(cls, version_str: str) -> SemanticVersion:
        """Parses a version string into a SemanticVersion instance."""
        clean_str = version_str.strip().lstrip("vV")
        clean_str = re.sub(r'^[<>=!~]+', '', clean_str)
        parts = clean_str.split(".")
        try:
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return cls(major=major, minor=minor, patch=patch)
        except (ValueError, IndexError) as err:
            raise ValueError(f"Invalid semantic version string: '{version_str}'") from err

    def __lt__(self, other: SemanticVersion) -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other: SemanticVersion) -> bool:
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __gt__(self, other: SemanticVersion) -> bool:
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __ge__(self, other: SemanticVersion) -> bool:
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class KernelABIContract:
    """
    Domain object defining the sovereign Kernel ABI contract specification.
    
    Attributes:
        kernel_version: Current running kernel semantic version (e.g., '2.0.0').
        abi_version: Active ABI specification version (e.g., '2.0').
        supported_abi_versions: List of ABI versions natively supported without adapters.
        core_capabilities: Mandatory capabilities guaranteed by this kernel version.
        extension_capabilities: Optional feature capabilities exposed by platform plugins.
    """
    kernel_version: str
    abi_version: str
    supported_abi_versions: List[str] = field(default_factory=lambda: ["1.0", "2.0"])
    core_capabilities: List[str] = field(default_factory=list)
    extension_capabilities: List[str] = field(default_factory=list)

    def is_abi_natively_supported(self, target_abi_version: str) -> bool:
        """Checks if the target ABI version is natively supported by the kernel contract."""
        return target_abi_version in self.supported_abi_versions

    def satisfies_version_bounds(self, min_version_str: str, max_version_str: str) -> bool:
        """
        Evaluates whether the kernel version falls strictly within min <= kernel < max.
        """
        kernel_semver = SemanticVersion.parse(self.kernel_version)
        min_semver = SemanticVersion.parse(min_version_str) if min_version_str else SemanticVersion(0, 0, 0)
        
        if not (kernel_semver >= min_semver):
            return False

        if max_version_str:
            max_semver = SemanticVersion.parse(max_version_str)
            if not (kernel_semver < max_semver):
                return False

        return True

    def get_missing_capabilities(self, required_capabilities: List[str]) -> List[str]:
        """
        Calculates any required capabilities not provided by core or extension capabilities.
        """
        available = set(self.core_capabilities) | set(self.extension_capabilities)
        missing = [cap for cap in required_capabilities if cap not in available]
        return sorted(missing)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes ABI Contract to dictionary format."""
        return {
            "kernel_version": self.kernel_version,
            "abi_version": self.abi_version,
            "supported_abi_versions": list(self.supported_abi_versions),
            "core_capabilities": list(self.core_capabilities),
            "extension_capabilities": list(self.extension_capabilities),
        }
