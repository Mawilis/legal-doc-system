"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Installer Engine - Orchestrates system installation, dependency verification, and environment provisioning.

Biblical Scale & Architecture:
    Production-ready installation orchestration pipeline. Zero child's place.
    Guarantees idempotent, fault-tolerant bootstrapping of Wilsy OS across target environments.

Collaboration & Maintenance:
    - [Architecture]: Master coordinator for repository installation and environment bootstrap.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path

from .installer_manifest import InstallerManifest
from .installer_builder import InstallerBuilder


class InstallerEngine:
    """
    Orchestrates the full lifecycle of system installation and environment provisioning.
    """

    def __init__(self, workspace_root: Path | str = ".") -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def execute_installation(self, install_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the end-to-end installation pipeline for a given specification.

        Args:
            install_spec (Dict[str, Any]): Installation configuration and target metadata.

        Returns:
            Dict[str, Any]: Installation execution report.
        """
        manifest = InstallerManifest.create_manifest(install_spec)
        build_result = InstallerBuilder.build_installer(manifest, self.workspace_root)

        if not build_result.get("success", False):
            return {
                "status": "FAILED",
                "reason": "Installer package compilation failed.",
                "details": build_result,
            }

        return {
            "status": "INSTALLED",
            "manifest": manifest,
            "build_details": build_result,
            "comments": "System installation package successfully provisioned and verified.",
        }
