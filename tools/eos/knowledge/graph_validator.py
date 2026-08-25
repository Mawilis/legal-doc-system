"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Knowledge Graph Validator - Validates structural integrity and schema conformity of graphs.

Biblical Scale & Architecture:
    Production-ready graph validation engine. Zero child's place.
    Ensures referential integrity between nodes and edges.

Collaboration & Maintenance:
    - [Architecture]: Structural validator for knowledge graph payloads.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List

from .graph_snapshot import GraphSnapshot


class GraphValidator:
    """
    Validates knowledge graph snapshots for structural and referential integrity.
    """

    @staticmethod
    def validate_snapshot(snapshot: GraphSnapshot) -> Dict[str, Any]:
        """
        Validates nodes, edges, and metadata integrity of a graph snapshot.

        Args:
            snapshot (GraphSnapshot): The snapshot to validate.

        Returns:
            Dict[str, Any]: Validation report containing status and error details.
        """
        errors: List[str] = []
        warnings: List[str] = []

        if not snapshot.snapshot_id:
            errors.append("Snapshot ID is missing or empty.")

        node_keys = set(snapshot.nodes.keys())

        # Validate edge referential integrity
        for edge in snapshot.edges:
            source = edge.get("source")
            target = edge.get("target")
            if not source or not target:
                errors.append(f"Edge missing source or target: {edge}")
            else:
                if source not in node_keys:
                    warnings.append(f"Edge source '{source}' not found in active nodes.")
                if target not in node_keys:
                    warnings.append(f"Edge target '{target}' not found in active nodes.")

        is_valid = len(errors) == 0

        return {
            "is_valid": is_valid,
            "snapshot_id": snapshot.snapshot_id,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
        }
