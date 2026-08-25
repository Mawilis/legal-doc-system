"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/diff_engine.py
===============================================================================
Epitome:
    Documentation diff and architectural drift detection engine for FG210.
    Compares baseline and target DocumentationEntity collections to identify
    added entities, deprecated contracts, schema changes, and parameter drifts.

Biblical Worth Billions:
    "Remove not the ancient landmark, which thy fathers have set."
    — Proverbs 22:28

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/diff_engine.py
===============================================================================
"""

from typing import Dict, List, Any
from tools.eos.documentation.documentation_contract import DocumentationEntity


class DocumentationDiffEngine:
    """
    Computes structural differences and drift analysis between two documentation snapshots.
    """

    @staticmethod
    def compute_diff(
        baseline: List[DocumentationEntity],
        target: List[DocumentationEntity],
    ) -> Dict[str, Any]:
        """
        Compares baseline documentation against a target snapshot and reports added,
        removed, and modified entities.

        Args:
            baseline: Initial baseline entity collection.
            target: Target/new entity collection.

        Returns:
            Dictionary detailing added, removed, and modified documentation URNs.
        """
        baseline_map = {e.urn: e for e in baseline}
        target_map = {e.urn: e for e in target}

        added_urns = set(target_map.keys()) - set(baseline_map.keys())
        removed_urns = set(baseline_map.keys()) - set(target_map.keys())
        common_urns = set(baseline_map.keys()) & set(target_map.keys())

        modified: List[Dict[str, Any]] = []

        for urn in common_urns:
            b_entity = baseline_map[urn]
            t_entity = target_map[urn]

            changes: List[str] = []

            if b_entity.version != t_entity.version:
                changes.append(f"version: '{b_entity.version}' -> '{t_entity.version}'")
            if b_entity.verification_status != t_entity.verification_status:
                changes.append(
                    f"verification_status: '{b_entity.verification_status.value}' -> '{t_entity.verification_status.value}'"
                )
            if b_entity.purpose != t_entity.purpose:
                changes.append("purpose updated")
            if len(b_entity.interfaces) != len(t_entity.interfaces):
                changes.append(
                    f"interface_count: {len(b_entity.interfaces)} -> {len(t_entity.interfaces)}"
                )

            if changes:
                modified.append({
                    "urn": urn,
                    "title": t_entity.title,
                    "changes": changes,
                })

        return {
            "baseline_count": len(baseline),
            "target_count": len(target),
            "added_count": len(added_urns),
            "removed_count": len(removed_urns),
            "modified_count": len(modified),
            "added": [target_map[urn].to_dict() for urn in added_urns],
            "removed": [baseline_map[urn].to_dict() for urn in removed_urns],
            "modified": modified,
        }
