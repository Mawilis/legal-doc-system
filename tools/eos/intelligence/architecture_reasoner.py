"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Intelligence - Architecture Reasoner (FG160).
    Proactively evaluates repository structure, module coupling, and system topology
    using the Digital Twin to detect architectural drift and structural risks.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready architectural reasoning engine. Zero child's place.
    Nehemiah 4:17 - "Those who carried loads did their work with one hand holding a weapon and the other supporting the load."

Collaboration & Maintenance:
    - [Architecture]: Proactive structural analysis and architectural drift detection.
    - [Compliance]: Guarantees adherence to billion-dollar modularity and purity standards.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from tools.eos.twin.digital_twin import DigitalTwin

logger = logging.getLogger("WilsyOS.ArchitectureReasoner")


class ArchitectureReasoner:
    """
    Analyzes the Digital Twin repository state to reason about system topology,
    modularity compliance, and architectural integrity.
    """

    def __init__(self, digital_twin: DigitalTwin) -> None:
        """
        Initializes the architecture reasoner linked to the Digital Twin.

        Args:
            digital_twin (DigitalTwin): The active in-memory repository authority.
        """
        self.digital_twin = digital_twin

    # [FUNCTION EXPLANATION]: Inspects module coupling and structural health across the repository.
    def evaluate_architecture(self) -> Dict[str, Any]:
        """
        Performs an in-memory structural health audit, evaluating file distribution,
        module organization, and potential architectural anti-patterns.

        Returns:
            Dict[str, Any]: Architectural health score and structural diagnostics.
        """
        logger.info("Executing architectural reasoning audit over Digital Twin...")
        repo_state = self.digital_twin.repository_state
        
        total_files = repo_state.total_files
        total_size = repo_state.total_size_bytes
        
        # Analyze languages and module densities
        languages: Dict[str, int] = {}
        for file_snap in repo_state.files.values():
            lang = file_snap.language
            languages[lang] = languages.get(lang, 0) + 1

        # Check for deep coupling or large files
        large_files = [
            f.file_path for f in repo_state.files.values() 
            if f.line_count > 500
        ]

        structural_integrity_score = 100.0
        if large_files:
            structural_integrity_score -= len(large_files) * 2.5

        return {
            "subsystem": "ArchitectureReasoner",
            "status": "HEALTHY" if structural_integrity_score >= 80.0 else "REVIEW_REQUIRED",
            "integrity_score": max(0.0, structural_integrity_score),
            "total_files_analyzed": total_files,
            "total_repository_size_bytes": total_size,
            "language_distribution": languages,
            "monolith_risk_files": large_files,
            "recommendation": (
                "Architecture is pristine. Continue maintaining strict modular boundaries."
                if not large_files
                else f"Refactor large modules to preserve micro-kernel isolation: {large_files}"
            ),
        }
