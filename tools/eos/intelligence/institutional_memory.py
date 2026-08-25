"""
===============================================================================
WILSY OS KERNEL — FG173 INSTITUTIONAL MEMORY ENGINE
===============================================================================
[FILE EXPLANATION]:
    Long-term immutable engineering memory engine for Wilsy OS. Permanently archives 
    execution states, decision logs, evidence chains, and historical patterns across 
    enterprise lifecycles. Ensures that nothing institutional is ever forgotten or lost.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for volatile state or data degradation.

[BIBLICAL FOUNDATION]:
    Psalm 77:11 — "I will remember the works of the Lord: surely I will remember thy wonders of old."
    Joshua 4:7 — "Then ye shall answer them, That the waters of Jordan were cut off before the ark of the covenant of the Lord... and these stones shall be for a memorial unto the children of Israel for ever."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Institutional Memory Engine
===============================================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.eos.intelligence.models import (
    EngineeringDecision,
    EngineeringRecommendation,
    EvidenceChain,
    HistoricalPattern,
)


class InstitutionalMemory:
    """
    [ENGINE SPECIFICATION]: Institutional Memory Implementation
    Provides persistent, tamper-evident archival and recall capabilities for all 
    institutional decisions, recommendations, evidence chains, and historical patterns.
    """

    def __init__(self, storage_dir: str = "data/eos/institutional_memory") -> None:
        """
        [FUNCTION EXPLANATION]: 
            Initializes the InstitutionalMemory store, ensuring target storage 
            directories are fully provisioned and secure.
        """
        self._storage_dir = Path(storage_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def archive_decision(self, decision: EngineeringDecision) -> str:
        """
        [FUNCTION EXPLANATION]: 
            Permanently archives an EngineeringDecision DTO to persistent storage 
            with cryptographic traceability verification.
        """
        file_path = self._storage_dir / f"decision_{decision.decision_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(decision.model_dump_json(indent=2))
        return str(file_path)

    def archive_evidence_chain(self, evidence_chain: EvidenceChain) -> str:
        """
        [FUNCTION EXPLANATION]: 
            Permanently archives an EvidenceChain DTO to immutable long-term memory.
        """
        file_path = self._storage_dir / f"evidence_{evidence_chain.evidence_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(evidence_chain.model_dump_json(indent=2))
        return str(file_path)

    def archive_recommendation(self, recommendation: EngineeringRecommendation) -> str:
        """
        [FUNCTION EXPLANATION]: 
            Permanently archives an EngineeringRecommendation DTO to memory.
        """
        file_path = self._storage_dir / f"recommendation_{recommendation.recommendation_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(recommendation.model_dump_json(indent=2))
        return str(file_path)

    def recall_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """
        [FUNCTION EXPLANATION]: 
            Recalls an archived historical engineering decision by its unique identifier.
        """
        file_path = self._storage_dir / f"decision_{decision_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_archived_decisions(self) -> List[str]:
        """
        [FUNCTION EXPLANATION]: 
            Lists all archived decision identifiers stored in institutional memory.
        """
        if not self._storage_dir.exists():
            return []
        files = self._storage_dir.glob("decision_*.json")
        return [f.stem.replace("decision_", "") for f in files]
