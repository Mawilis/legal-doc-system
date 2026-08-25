"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Catalog - Inventories and indexes all generated reports, logs, and build artifacts.

Biblical Scale & Architecture:
    Production-ready artifact inventory system. Zero child's place.
    Maintains searchable metadata catalogs for all institutional deliverables.

Collaboration & Maintenance:
    - [Architecture]: Artifact cataloging and indexer.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class ArtifactCatalog:
    """
    Catalogs and indexes generated institutional artifacts.
    """

    def __init__(self, reports_dir: Path | str = "./reports") -> None:
        self.reports_dir = Path(reports_dir).resolve()

    def list_artifacts(self) -> List[Dict[str, Any]]:
        """
        Lists all serialized reports and generated artifacts in the repository.

        Returns:
            List[Dict[str, Any]]: Inventory list of artifact metadata.
        """
        if not self.reports_dir.exists():
            return []

        artifacts = []
        for file_path in self.reports_dir.glob("*_unified_report.json"):
            artifacts.append({
                "name": file_path.name,
                "path": str(file_path),
                "size_bytes": file_path.stat().st_size,
            })

        return artifacts
