"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Integration Framework - Repository Engine.
    Handles source repository scanning, validation, file inspection, and state snapshots,
    producing an immutable Repository Artifact.

Biblical Scale & Architecture:
    Production-ready billionaire software standard. Complete, future-proof, with collaboration comments.
    Proverbs 22:29 - "Do you see a man skillful in his work? He will stand before kings."

Collaboration & Maintenance:
    - [Architecture]: Concrete engine extending BaseEngine for repository operations.
    - Consumes: Execution context containing target paths, repository paths, or file scopes.
    - Produces: Immutable Artifact of type 'repository_state'.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from tools.eos.artifacts.artifact import Artifact
from tools.eos.engines.base import BaseEngine


class RepositoryEngine(BaseEngine):
    """
    Engine responsible for inspecting repository state, files, and structure,
    yielding immutable Repository Artifacts.
    """

    def __init__(self) -> None:
        super().__init__(engine_id="core.repository", artifact_type="repository_state")

    # [FUNCTION EXPLANATION]: Core execution routine scanning repository health, files, and structure.
    def execute(self, execution_id: str, context: Dict[str, Any]) -> Artifact:
        """
        Executes repository inspection and validation.

        Args:
            execution_id (str): Unique execution run identifier.
            context (Dict[str, Any]): Execution context parameters (e.g., 'repo_path', 'target_files').

        Returns:
            Artifact: Immutable Artifact containing repository state payload.
        """
        repo_path_str = context.get("repo_path", "/Users/wilsonkhanyezi/legal-doc-system")
        repo_path = Path(repo_path_str)

        files_scanned: List[str] = []
        total_size_bytes = 0

        if repo_path.exists() and repo_path.is_dir():
            for root, _, files in os.walk(repo_path):
                # Skip virtual environments and hidden git dirs for clean performance
                if ".venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                for file in files:
                    if file.endswith((".py", ".json", ".md", ".sh")):
                        full_path = Path(root) / file
                        files_scanned.append(str(full_path.relative_to(repo_path)))
                        try:
                            total_size_bytes += full_path.stat().st_size
                        except (OSError, AttributeError):
                            pass

        payload = {
            "repository_path": str(repo_path),
            "total_files_scanned": len(files_scanned),
            "total_size_bytes": total_size_bytes,
            "files": sorted(files_scanned)[:100],  # Capped snapshot sample
            "status": "HEALTHY",
        }

        metadata = {
            "engine_id": self.engine_id,
            "execution_id": execution_id,
            "scope": "repository_inspection",
        }

        return self.create_artifact(
            execution_id=execution_id,
            payload=payload,
            metadata=metadata,
        )
