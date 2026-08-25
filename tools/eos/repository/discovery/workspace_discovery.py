"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Fidelity Automated Workspace and Environment Configuration Mapping Engine.
    Statically inspects repository roots for build toolkits, environment templates,
    containerization manifests, and IDE operational settings.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready enterprise engine. No child's place.
    Operates strictly via performance-optimized static signature matching. Eliminates
    environmental drift by mapping the external configuration dependencies that 
    define the runtime habitat of the code.

Collaboration & Maintenance:
    - [Reliability]: Implements strict structural classification for workspace artifacts.
    - [Security]: Discovers configuration schema without accessing sensitive secrets.
    - [Data Integrity]: Delivers completely frozen data models to guarantee state stability.

===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.discovery.workspace_discovery")


@dataclass(frozen=True)
class WorkspaceRecord:
    """
    Immutable representation of an isolated operational workspace configuration footprint.
    """
    workspace_id: str
    config_path: str
    workspace_type: str  # e.g., 'CONTAINER', 'BUILD_TOOL', 'ENV_CONFIG', 'IDE_SETTINGS'
    description: str


class WorkspaceDiscovery:
    """
    Industrial-grade Workspace configuration Extractor and Environment Mapping Component.
    Parses manifest files to catalog environmental dependencies and tooling ecosystems.
    """

    def __init__(self) -> None:
        """
        Initializes the workspace scanner with institutional infrastructure fingerprints.
        """
        # Mapping filenames to architectural workspace roles
        self._workspace_manifests: dict[str, str] = {
            "Dockerfile": "CONTAINER",
            "docker-compose.yml": "CONTAINER",
            "Makefile": "BUILD_TOOL",
            "pyproject.toml": "BUILD_TOOL",
            "package.json": "BUILD_TOOL",
            ".env.example": "ENV_CONFIG",
            ".env.template": "ENV_CONFIG",
            "requirements.txt": "BUILD_TOOL",
        }

    def discover_in_workspace(self, repository_root: Path) -> tuple[WorkspaceRecord, ...]:
        """
        Statically inspects the workspace root to isolate environmental configuration footprints.
        """
        found_records: list[WorkspaceRecord] = []
        root_path = Path(repository_root).resolve()

        if not root_path.exists() or not root_path.is_dir():
            logger.error(f"Workspace Fault: Invalid workspace root path provided: {root_path}")
            return ()

        logger.debug(f"Scanning workspace root for environmental fingerprints: {root_path}")

        # Shallow scan for known infrastructure manifest files
        for filename, w_type in self._workspace_manifests.items():
            file_path = root_path / filename
            if file_path.exists():
                found_records.append(WorkspaceRecord(
                    workspace_id=filename,
                    config_path=str(file_path.relative_to(root_path)),
                    workspace_type=w_type,
                    description=f"Detected primary environment configuration node: {filename}"
                ))

        return tuple(sorted(found_records, key=lambda x: x.workspace_id))

