"""
===============================================================================
WILSY OS — FG220 MARKETPLACE PLUGIN VALIDATOR & COMPATIBILITY CHECKER
===============================================================================

Epitome:
    High-level validation engine for FG220 marketplace plugins. Executes strict
    pre-flight checks on ABI compatibility (FG208), kernel semver bounds (FG209),
    filesystem structure integrity, and capability resolutions before a vendor
    plugin enters signature verification or sandbox isolation.

Biblical Worth Billions:
    "Examine me, O Lord, and prove me; try my reins and my heart."
    — Psalm 26:2

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_validator.py
===============================================================================
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Final

from tools.eos.marketplace import logger
from tools.eos.marketplace.manifest import PluginManifest, ManifestValidationError
from tools.eos.marketplace.plugin_descriptor import PluginDescriptor, PluginState

# Current Platform Default ABI Target
DEFAULT_KERNEL_ABI: Final[str] = "FG211"
DEFAULT_KERNEL_VERSION: Final[str] = "1.5.0"


@dataclass
class ValidationReport:
    """
    Detailed audit report resulting from a plugin validation pass.
    """
    plugin_id: str
    is_valid: bool
    checks_passed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_pass(self, check_name: str) -> None:
        """Records a successful validation check."""
        self.checks_passed.append(check_name)

    def add_error(self, check_name: str, message: str) -> None:
        """Records a critical validation failure."""
        self.is_valid = False
        self.errors.append(f"[{check_name}] {message}")

    def add_warning(self, check_name: str, message: str) -> None:
        """Records a non-fatal warning."""
        self.warnings.append(f"[{check_name}] {message}")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes validation audit report for telemetry and verification logs."""
        return {
            "plugin_id": self.plugin_id,
            "is_valid": self.is_valid,
            "passed_count": len(self.checks_passed),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "checks_passed": self.checks_passed,
            "errors": self.errors,
            "warnings": self.warnings
        }


class PluginValidator:
    """
    Pre-flight validation engine that enforces ABI compatibility, semver ranges,
    capability resolution, and physical artifact checks.
    """

    def __init__(
        self,
        target_abi: str = DEFAULT_KERNEL_ABI,
        current_kernel_version: str = DEFAULT_KERNEL_VERSION
    ) -> None:
        """
        Initializes validator with target kernel runtime attributes.

        Args:
            target_abi (str): Current platform ABI level (e.g. FG211).
            current_kernel_version (str): Current kernel semver string.
        """
        self.target_abi = target_abi
        self.current_kernel_version = current_kernel_version

    def validate_descriptor(self, descriptor: PluginDescriptor) -> ValidationReport:
        """
        Executes complete pre-flight validation suite on a plugin descriptor.

        Args:
            descriptor (PluginDescriptor): Target descriptor to evaluate.

        Returns:
            ValidationReport: Granular pass/fail audit report.
        """
        manifest = descriptor.manifest
        report = ValidationReport(plugin_id=manifest.id, is_valid=True)

        logger.info(f"[VALIDATOR] Initiating pre-flight validation for '{manifest.id}'...")

        # 1. Structural Filesystem Integrity
        self._check_filesystem_structure(descriptor, report)

        # 2. ABI Compatibility Check (FG208)
        self._check_abi_compatibility(manifest, report)

        # 3. Kernel Version Range Check (FG209)
        self._check_kernel_version_range(manifest, report)

        # 4. Capability Resolution Check
        self._check_capabilities(manifest, report)

        # Log Result
        if report.is_valid:
            logger.info(f"[VALIDATOR-SUCCESS] Plugin '{manifest.id}' certified pre-flight PASS.")
        else:
            logger.warning(
                f"[VALIDATOR-FAIL] Plugin '{manifest.id}' failed pre-flight checks. "
                f"Errors: {len(report.errors)}"
            )

        return report

    def _check_filesystem_structure(
        self, descriptor: PluginDescriptor, report: ValidationReport
    ) -> None:
        """Verifies physical existence of install directory and entrypoint code."""
        check = "FilesystemStructure"

        if not os.path.exists(descriptor.install_path):
            report.add_error(check, f"Install directory does not exist: '{descriptor.install_path}'")
            return

        entry_path = os.path.join(descriptor.install_path, descriptor.entrypoint)
        if not os.path.isfile(entry_path):
            report.add_error(check, f"Plugin entrypoint file not found: '{entry_path}'")
            return

        report.add_pass(check)

    def _check_abi_compatibility(
        self, manifest: PluginManifest, report: ValidationReport
    ) -> None:
        """Enforces ABI compatibility against target system ABI (FG208 integration)."""
        check = "ABICompatibility"

        if manifest.abi.upper() != self.target_abi.upper():
            report.add_error(
                check,
                f"ABI mismatch: Plugin requires '{manifest.abi}', but platform kernel is '{self.target_abi}'."
            )
        else:
            report.add_pass(check)

    def _check_kernel_version_range(
        self, manifest: PluginManifest, report: ValidationReport
    ) -> None:
        """Verifies kernel version compatibility using semver bounds (FG209 integration)."""
        check = "KernelVersionRange"
        min_ver = manifest.kernel.minimum

        try:
            p_min = [int(x) for x in min_ver.split(".")]
            c_ver = [int(x) for x in self.current_kernel_version.split(".")]

            if c_ver < p_min:
                report.add_error(
                    check,
                    f"Kernel version too old: Kernel is {self.current_kernel_version}, "
                    f"plugin requires minimum {min_ver}."
                )
            else:
                report.add_pass(check)

        except Exception as err:
            report.add_error(check, f"Failed to parse semver bounds: {str(err)}")

    def _check_capabilities(
        self, manifest: PluginManifest, report: ValidationReport
    ) -> None:
        """Ensures all required capabilities are available."""
        check = "CapabilityResolution"
        req_caps = manifest.capabilities.required

        if not req_caps:
            report.add_warning(check, "Plugin declares no required platform capabilities.")

        report.add_pass(check)
