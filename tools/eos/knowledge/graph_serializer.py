"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Knowledge Graph Serializer - Serializes graph snapshots to persistent storage formats.

Biblical Scale & Architecture:
    Production-ready graph serialization engine. Zero child's place.
    Enforces atomic, indented JSON serialization for the knowledge graph state.

Collaboration & Maintenance:
    - [Architecture]: Atomic file persistence handler for knowledge graphs.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .graph_snapshot import GraphSnapshot


class GraphSerializer:
    """
    Serializes and saves knowledge graph snapshots to disk atomically.
    """

    @staticmethod
    def serialize_to_json(snapshot: GraphSnapshot, file_path: Path | str) -> bool:
        """
        Atomically serializes a graph snapshot to a JSON file.

        Args:
            snapshot (GraphSnapshot): The snapshot to serialize.
            file_path (Path | str): Destination file path.

        Returns:
            bool: True if serialization succeeded, False otherwise.
        """
        path = Path(file_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = snapshot.to_dict()
            
            # Atomic write via temporary file pattern
            temp_path = path.with_suffix(path.suffix + ".tmp")
            temp_path.write_text(json.dumps(payload, indent=4), encoding="utf-8")
            temp_path.replace(path)
            return True
        except Exception:
            return False
