from __future__ import annotations

"""
===============================================================================
WILSY OS LEARNING — KNOWLEDGE EVOLUTION TRACKER
===============================================================================
Epitome:
    Tracks the lifecycle, confidence scoring, and evolutionary refinement of
    institutional knowledge nodes across kernel execution history.

Biblical Worth Billions:
    "Line upon line, precept upon precept, here a little, and there a little."
    — Isaiah 28:10
    Knowledge evolves through continuous empirical verification. Hypothesis
    becomes rule only after proven consistency.

Collaboration & Ownership:
    - Founder & Lead Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Institutional Learning Engine
    - Phase / Milestone: Institutional Learning Engine
    - Target Directory: tools/eos/learning/
    - File Path: tools/eos/learning/knowledge_evolution.py
    - Runtime Alignment: Python 3.10+ Production Environment
===============================================================================
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeNode:
    """
    Represents an individual unit of evolved institutional knowledge.
    """
    node_id: str
    domain: str  # e.g., 'build_speed', 'defect_prevention', 'repo_layout'
    pattern_key: str
    recommendation: str
    confidence_score: float = 0.5  # Scale 0.0 to 1.0
    evidence_count: int = 1
    version: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def reinforce(self, weight: float = 0.05) -> None:
        """Reinforces confidence in this knowledge node upon verified success."""
        self.evidence_count += 1
        self.confidence_score = min(1.0, round(self.confidence_score + weight, 4))
        self.version += 1
        self.updated_at = time.time()

    def penalize(self, weight: float = 0.10) -> None:
        """Penalizes confidence when an unexpected error occurs under this model."""
        self.confidence_score = max(0.0, round(self.confidence_score - weight, 4))
        self.version += 1
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes knowledge node for export."""
        return {
            "node_id": self.node_id,
            "domain": self.domain,
            "pattern_key": self.pattern_key,
            "recommendation": self.recommendation,
            "confidence_score": self.confidence_score,
            "evidence_count": self.evidence_count,
            "version": self.version,
            "updated_at": self.updated_at,
        }


class KnowledgeEvolutionTracker:
    """
    Manages the active inventory of institutional knowledge nodes and evolves
    their confidence scores as new pipeline execution results arrive.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, KnowledgeNode] = {}

    def register_or_update(
        self,
        node_id: str,
        domain: str,
        pattern_key: str,
        recommendation: str,
        success: bool,
    ) -> KnowledgeNode:
        """
        Updates an existing knowledge node or creates a new one, adjusting confidence.
        """
        if node_id in self._nodes:
            node = self._nodes[node_id]
            if success:
                node.reinforce()
            else:
                node.penalize()
        else:
            initial_score = 0.6 if success else 0.3
            node = KnowledgeNode(
                node_id=node_id,
                domain=domain,
                pattern_key=pattern_key,
                recommendation=recommendation,
                confidence_score=initial_score,
            )
            self._nodes[node_id] = node

        return node

    def get_high_confidence_nodes(self, threshold: float = 0.7) -> List[KnowledgeNode]:
        """Returns all knowledge nodes whose confidence exceeds the operational threshold."""
        return [node for node in self._nodes.values() if node.confidence_score >= threshold]

    def export_all(self) -> List[Dict[str, Any]]:
        """Exports dictionary representation of all active knowledge nodes."""
        return [node.to_dict() for node in self._nodes.values()]


__all__ = ["KnowledgeNode", "KnowledgeEvolutionTracker"]
