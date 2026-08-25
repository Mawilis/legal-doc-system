"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Release Engine - Orchestrates artifact building, manifest generation, validation, and release pipelines.

Biblical Scale & Architecture:
    Production-ready release orchestration pipeline. Zero child's place.
    Guarantees cryptographically secure and fully validated distribution packages.

Collaboration & Maintenance:
    - [Architecture]: Master coordinator for automated repository releases.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path

from .artifact_builder import ArtifactBuilder
from .release_manifest import ReleaseManifest
from .release_validator import ReleaseValidator


class ReleaseEngine:
    """
    Orchestrates the full lifecycle of software releases from artifact compilation to final validation.
    """

    def __init__(self, workspace_root: Path | str = ".") -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def execute_release_pipeline(self, release_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the end-to-end release pipeline for a given specification.

        Args:
            release_spec (Dict[str, Any]): Specification containing version, artifacts, and metadata.

        Returns:
            Dict[str, Any]: Comprehensive release report and status.
        """
        manifest = ReleaseManifest.create_manifest(release_spec)
        build_result = ArtifactBuilder.build_artifacts(manifest, self.workspace_root)
        
        if not build_result.get("success", False):
            return {
                "status": "FAILED",
                "reason": "Artifact compilation failed.",
                "build_details": build_result,
            }

        validation_result = ReleaseValidator.validate_release(manifest, self.workspace_root)
        if not validation_result.get("valid", False):
            return {
                "status": "REJECTED",
                "reason": validation_result.get("error", "Release validation failed"),
                "manifest": manifest,
            }

        return {
            "status": "PUBLISHED",
            "manifest": manifest,
            "build_details": build_result,
            "validation_details": validation_result,
            "comments": "Release pipeline executed with pristine institutional integrity.",
        }
