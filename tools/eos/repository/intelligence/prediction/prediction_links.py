"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Prediction linkage structures connecting capabilities and AST nodes to 
    predictive risk vectors, architectural drift metrics, and impact scores.

Biblical Worth Billions:
    "A prudent man foreseeth the evil, and hideth himself; but the simple pass 
    on, and are punished." — Proverbs 27:12

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/prediction/prediction_links.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional


class RiskSeverity(str, Enum):
    """Predictive blast radius severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class PredictionLink:
    """
    Binds a capability or architectural node to predictive risk analysis metrics,
    blast radius estimations, and complexity vectors.
    """
    capability_id: str
    predicted_blast_radius_nodes: List[str]
    complexity_vector_score: float
    risk_severity: RiskSeverity
    drift_probability: float

    def to_dict(self) -> Dict[str, Any]:
        """Serializes prediction link model to a dictionary."""
        data = asdict(self)
        data["risk_severity"] = self.risk_severity.value if isinstance(self.risk_severity, RiskSeverity) else str(self.risk_severity)
        return data


@dataclass
class PredictionLinkCatalog:
    """
    Catalog indexing predictive risk mappings across platform capabilities.
    """
    links: Dict[str, PredictionLink] = field(default_factory=dict)

    def add_link(self, link: PredictionLink) -> None:
        """Registers a capability prediction link."""
        self.links[link.capability_id] = link

    def get_link(self, capability_id: str) -> Optional[PredictionLink]:
        """Retrieves prediction link model for a given capability ID."""
        return self.links.get(capability_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes prediction link catalog to dictionary representation."""
        return {
            "total_links": len(self.links),
            "links": {k: v.to_dict() for k, v in self.links.items()},
        }