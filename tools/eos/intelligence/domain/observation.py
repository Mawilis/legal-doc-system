"""
===============================================================================
WILSY OS — FG229 ENTERPRISE INTELLIGENCE LAYER SUBSYSTEM
DOMAIN: OBSERVATION & EVIDENCE ENTITIES
===============================================================================

File Path:
    tools/eos/intelligence/domain/observation.py

Version:
    v229.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines foundational entities for telemetry observations, evidence items, 
    hypotheses, recommendations, and explainable decision objects.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, and 
    counteth the cost, whether he have sufficient to finish it?" — Luke 14:28

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List


@dataclass
class Observation:
    """Read-only system observation collected from underlying subsystems."""
    observation_id: str = field(default_factory=lambda: f"OBS-{uuid.uuid4().hex[:6].upper()}")
    source_subsystem: str = "CLUSTER_MANAGER"
    metric_key: str = "CPU_UTILIZATION_PERCENT"
    raw_value: float = 87.5
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        self.checksum = hashlib.sha256(
            f"{self.observation_id}:{self.source_subsystem}:{self.metric_key}:{self.raw_value}:{self.timestamp}".encode("utf-8")
        ).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "source_subsystem": self.source_subsystem,
            "metric_key": self.metric_key,
            "raw_value": self.raw_value,
            "timestamp": self.timestamp,
            "checksum": self.checksum
        }


@dataclass
class Evidence:
    """Verifiable supporting evidence derived from one or more observations."""
    evidence_id: str = field(default_factory=lambda: f"EVD-{uuid.uuid4().hex[:6].upper()}")
    source_type: str = "TELEMETRY"
    summary: str = "High CPU load detected across Africa-South cluster nodes"
    observations: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """Explainable action recommendation for Autonomous Operations (FG224)."""
    recommendation_id: str = field(default_factory=lambda: f"REC-{uuid.uuid4().hex[:6].upper()}")
    action_title: str = "Provision 2 Additional Worker Nodes"
    target_subsystem: str = "FG224_AUTONOMOUS_OPERATIONS"
    confidence_score: float = 0.98
    risk_level: str = "LOW"
    evidence_chain: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "action_title": self.action_title,
            "target_subsystem": self.target_subsystem,
            "confidence_score": self.confidence_score,
            "risk_level": self.risk_level,
            "evidence_chain": self.evidence_chain,
            "created_at": self.created_at
        }
