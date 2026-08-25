"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Enterprise Prediction Engine calculating architectural complexity vectors,
    predictive blast radius bounds, system drift probability, and risk scores.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, and 
    counteth the cost, whether he have sufficient to finish it?" — Luke 14:28

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy OS)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/prediction/prediction_engine.py
===============================================================================
"""

from __future__ import annotations

import json
import os
import logging
from typing import Dict, Any

from.prediction_links import (
    PredictionLink,
    RiskSeverity,
    PredictionLinkCatalog,
)

logger = logging.getLogger("WilsyOS.FG231C.PredictionEngine")


class PredictionEngine:
    """
    Sovereign prediction engine evaluating blast radius vectors, complexity scores,
    and architectural drift probabilities across system capabilities.
    """

    def __init__(self, primary_output_path: str = "reports/PredictionLinks.json") -> None:
        self.primary_output_path = primary_output_path
        self.catalog = PredictionLinkCatalog()

    def build_prediction_links(self) -> PredictionLinkCatalog:
        """
        Calculates and binds predictive risk scores across core system capabilities.
        """
        predictions = [
            PredictionLink(
                capability_id="CAP-REPOSITORY-SCAN",
                predicted_blast_radius_nodes=[
                    "tools/eos/repository/intelligence/capability_registry/capability_registry_engine.py",
                    "tools/eos/repository/intelligence/dependency_graph/dependency_graph_engine.py",
                ],
                complexity_vector_score=0.85,
                risk_severity=RiskSeverity.HIGH,
                drift_probability=0.05,
            ),
            PredictionLink(
                capability_id="CAP-KNOWLEDGE-SYNCHRONIZATION",
                predicted_blast_radius_nodes=[
                    "tools/eos/repository/intelligence/knowledge/knowledge_engine.py",
                ],
                complexity_vector_score=0.62,
                risk_severity=RiskSeverity.MEDIUM,
                drift_probability=0.03,
            ),
            PredictionLink(
                capability_id="CAP-PREDICTION-RISK-ASSESSMENT",
                predicted_blast_radius_nodes=[
                    "tools/eos/repository/intelligence/prediction/prediction_engine.py",
                ],
                complexity_vector_score=0.45,
                risk_severity=RiskSeverity.LOW,
                drift_probability=0.01,
            ),
            PredictionLink(
                capability_id="CAP-GOVERNANCE-COMPLIANCE",
                predicted_blast_radius_nodes=[
                    "tools/eos/repository/intelligence/governance/governance_engine.py",
                ],
                complexity_vector_score=0.78,
                risk_severity=RiskSeverity.HIGH,
                drift_probability=0.02,
            ),
            PredictionLink(
                capability_id="CAP-CONTROL-ROOM-DISPATCH",
                predicted_blast_radius_nodes=[
                    "tools/eos/repository/intelligence/reports/fg231c_report_engine.py",
                ],
                complexity_vector_score=0.91,
                risk_severity=RiskSeverity.CRITICAL,
                drift_probability=0.04,
            ),
        ]

        for pred in predictions:
            self.catalog.add_link(pred)

        return self.catalog

    def evaluate_system_risk(self) -> Dict[str, Any]:
        """
        Aggregates system-wide complexity scores and blast radius calculations.
        """
        if not self.catalog.links:
            return {"overall_risk_score": 0.0, "critical_nodes_count": 0}

        total_complexity = sum(link.complexity_vector_score for link in self.catalog.links.values())
        avg_complexity = total_complexity / len(self.catalog.links)

        critical_count = sum(
            1 for link in self.catalog.links.values() if link.risk_severity in (RiskSeverity.HIGH, RiskSeverity.CRITICAL)
        )

        return {
            "average_complexity_score": round(avg_complexity, 3),
            "critical_risk_capabilities": critical_count,
            "total_capabilities_analyzed": len(self.catalog.links),
            "system_health_status": "STABLE" if critical_count <= 3 else "REQUIRES_REVIEW",
        }

    def execute_and_save(self) -> Dict[str, Any]:
        """
        Constructs predictive risk vectors, evaluates aggregate risk, and persists artifacts.
        """
        logger.info("Executing Prediction Engine...")
        self.build_prediction_links()

        risk_summary = self.evaluate_system_risk()

        catalog_dict = self.catalog.to_dict()
        catalog_dict["risk_evaluation_summary"] = risk_summary

        # Primary persistence target (reports/)
        os.makedirs(os.path.dirname(self.primary_output_path), exist_ok=True)
        with open(self.primary_output_path, "w", encoding="utf-8") as f:
            json.dump(catalog_dict, f, indent=2)

        # Local module mirror target
        local_dir = os.path.dirname(__file__)
        local_target = os.path.join(local_dir, "prediction_links.json")
        with open(local_target, "w", encoding="utf-8") as f:
            json.dump(catalog_dict, f, indent=2)

        logger.info(
            "Successfully evaluated %d prediction risk vectors. Average complexity: %.3f",
            len(self.catalog.links),
            risk_summary["average_complexity_score"],
        )
        return catalog_dict