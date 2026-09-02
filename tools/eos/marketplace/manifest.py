"""
===============================================================================
WILSY OS — FG220 PLUGIN MANIFEST PARSER & SCHEMA VALIDATOR
===============================================================================

Epitome:
    Authoritative manifest schema parser and validation engine for FG220 plugins.
    Enforces strict structural integrity, metadata completeness, semver range
    parsing, capability declarations, and required permission arrays before
    allowing any vendor plugin to enter the signature or sandbox verification pipeline.

Biblical Worth Billions:
    "Let all things be done decently and in order."
    — 1 Corinthians 14:40

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/manifest.py
===============================================================================
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Final

from tools.eos.marketplace import logger

# Identifier Regex: Reverse-domain or dot-separated lowercase format (e.g. crm.analytics)
PLUGIN_ID_REGEX: Final[re.Pattern] = re.compile(r"^[a-z0-9]+(\.[a-z0-9\-_]+)+$")
SEMVER_REGEX: Final[re.Pattern] = re.compile(r"^\d+\.\d+\.\d+$")

# Approved Platform Capabilities & Permissions Enums
APPROVED_CAPABILITIES: Final[set] = {
    "EventBus",
    "ExecutionContext",
    "DashboardContract",
    "DigitalTwin",
    "PredictionEngine",
    "ArtifactBus",
    "TelemetryLogger"
}

APPROVED_PERMISSIONS: Final[set] = {
    "repository.read",
    "repository.write",
    "documentation.read",
    "dashboard.read",
    "telemetry.emit",
    "storage.isolated"
}


class ManifestValidationError(Exception):
    """Custom exception thrown when a plugin manifest violates Wilsy OS schema contracts."""
    pass


@dataclass(frozen=True)
class KernelRange:
    """Represents required kernel semver minimum and maximum bounds."""
    minimum: str
    maximum: str

    def validate(self) -> None:
        """Validates semver syntax for kernel version bounds."""
        if not SEMVER_REGEX.match(self.minimum):
            raise ManifestValidationError(f"Invalid minimum kernel version format: {self.minimum}")


@dataclass(frozen=True)
class PluginCapabilities:
    """Container for required and optional engine capability bindings."""
    required: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)

    def validate(self) -> None:
        """Enforces approved platform capability names."""
        for cap in self.required + self.optional:
            if cap not in APPROVED_CAPABILITIES:
                raise ManifestValidationError(f"Unapproved or unknown platform capability: '{cap}'")


@dataclass
class PluginManifest:
    """
    Authoritative Manifest Data Structure for Wilsy OS Engine Marketplace.
    """
    id: str
    vendor: str
    version: str
    abi: str
    kernel: KernelRange
    capabilities: PluginCapabilities
    permissions: List[str]
    signature: str
    description: Optional[str] = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        """
        Hydrates and validates a PluginManifest instance from raw dictionary structure.

        Args:
            data (Dict[str, Any]): Raw dictionary parsed from YAML or JSON manifest file.

        Returns:
            PluginManifest: Validated and strongly-typed manifest object.

        Raises:
            ManifestValidationError: If required fields are missing or fail schema validation.
        """
        if not isinstance(data, dict):
            raise ManifestValidationError("Manifest payload must be a key-value dictionary.")

        # Check required root keys
        required_keys = ["id", "vendor", "version", "abi", "kernel", "capabilities", "permissions", "signature"]
        for k in required_keys:
            if k not in data:
                raise ManifestValidationError(f"Missing mandatory manifest key: '{k}'")

        # Parse Kernel Range
        kernel_data = data.get("kernel", {})
        if not isinstance(kernel_data, dict) or "minimum" not in kernel_data or "maximum" not in kernel_data:
            raise ManifestValidationError("Kernel key must contain 'minimum' and 'maximum' semver fields.")

        kernel_range = KernelRange(
            minimum=str(kernel_data["minimum"]),
            maximum=str(kernel_data["maximum"])
        )

        # Parse Capabilities
        cap_data = data.get("capabilities", {})
        if not isinstance(cap_data, dict):
            raise ManifestValidationError("Capabilities must be an object containing 'required' and/or 'optional' lists.")

        capabilities = PluginCapabilities(
            required=list(cap_data.get("required", [])),
            optional=list(cap_data.get("optional", []))
        )

        manifest = cls(
            id=str(data["id"]).strip(),
            vendor=str(data["vendor"]).strip(),
            version=str(data["version"]).strip(),
            abi=str(data["abi"]).strip(),
            kernel=kernel_range,
            capabilities=capabilities,
            permissions=list(data.get("permissions", [])),
            signature=str(data["signature"]).strip(),
            description=str(data.get("description", ""))
        )

        manifest.validate()
        return manifest

    def validate(self) -> None:
        """
        Executes strict schema and rule validation on the hydrated manifest.
        """
        # 1. Plugin ID format check
        if not PLUGIN_ID_REGEX.match(self.id):
            raise ManifestValidationError(
                f"Invalid plugin ID '{self.id}'. Must match pattern 'vendor.name' (e.g., 'crm.analytics')."
            )

        # 2. Version format check
        if not SEMVER_REGEX.match(self.version):
            raise ManifestValidationError(f"Invalid semver version string '{self.version}'. Expected format 'X.Y.Z'.")

        # 3. Kernel bounds check
        self.kernel.validate()

        # 4. Capability validation
        self.capabilities.validate()

        # 5. Permission array check
        for perm in self.permissions:
            if perm not in APPROVED_PERMISSIONS:
                raise ManifestValidationError(f"Unapproved or unknown platform permission: '{perm}'")

        # 6. Signature presence check
        if not self.signature or len(self.signature) < 16:
            raise ManifestValidationError("Manifest signature digest missing or dangerously short.")

        logger.debug(f"[MANIFEST-VALIDATED] Manifest for plugin '{self.id}' (v{self.version}) certified.")

    def to_dict(self) -> Dict[str, Any]:
        """Converts manifest back into dictionary representation for registry serialization."""
        return {
            "id": self.id,
            "vendor": self.vendor,
            "version": self.version,
            "abi": self.abi,
            "kernel": {
                "minimum": self.kernel.minimum,
                "maximum": self.kernel.maximum
            },
            "capabilities": {
                "required": self.capabilities.required,
                "optional": self.capabilities.optional
            },
            "permissions": self.permissions,
            "signature": self.signature,
            "description": self.description
        }
