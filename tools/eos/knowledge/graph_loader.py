"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Knowledge Graph Loader - Ingests and loads knowledge graph databases and snapshots.

Biblical Scale & Architecture:
    Production-ready graph loading engine. Zero child's place.
    Provides safe, atomic file ingestion for graph storage backend (.wilsy_graph.json).

Collaboration & Maintenance:
    - [Architecture]: File I/O handler for knowledge graph persistence.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .graph_snapshot import GraphSnapshot


class GraphLoader:
    """
    Loads knowledge graph snapshots and database files from disk.
    """

    @staticmethod
    def load_from_json(file_path: Path | str) -> Optional[GraphSnapshot]:
        """
        Loads a graph snapshot from a JSON persistence file.

        Args:
            file_path (Path | str): Path to the graph JSON file.

        Returns:
            Optional[GraphSnapshot]: Loaded snapshot instance or None on failure.
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return None

        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            
            return GraphSnapshot(
                snapshot_id=data.get("snapshot_id", "UNKNOWN"),
                timestamp=data.get("timestamp", 0.0),
                nodes=data.get("nodes", {}),
                edges=data.get("edges", []),
                metadata=data.get("metadata", {}),
            )
        except Exception:
            return None
