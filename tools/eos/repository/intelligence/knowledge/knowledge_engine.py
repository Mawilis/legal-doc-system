"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Enterprise Knowledge Engine indexing capabilities into unified semantic 
    knowledge graphs, establishing domain boundaries, and exporting links.

Biblical Worth Billions:
    "Through wisdom is an house builded; and by understanding it is established: 
    And by knowledge shall the chambers be filled with all precious and pleasant riches."
    — Proverbs 24:3-4

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy OS)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/knowledge/knowledge_engine.py
===============================================================================
"""

from __future__ import annotations

import json
import os
import logging
from typing import Dict, Any

from.knowledge_links import (
    KnowledgeLink,
    KnowledgeDomain,
    KnowledgeLinkCatalog,
)

logger = logging.getLogger("WilsyOS.FG231C.KnowledgeEngine")


class KnowledgeEngine:
    """
    Sovereign knowledge engine binding system capabilities and codebase entities 
    to enterprise knowledge graph taxonomy nodes and semantic documentation assets.
    """

    def __init__(self, primary_output_path: str = "reports/KnowledgeLinks.json") -> None:
        self.primary_output_path = primary_output_path
        self.catalog = KnowledgeLinkCatalog()

    def build_knowledge_links(self) -> KnowledgeLinkCatalog:
        """
        Populates semantic knowledge links across core platform capabilities.
        """
        links = [
            KnowledgeLink(
                capability_id="CAP-REPOSITORY-SCAN",
                domain=KnowledgeDomain.CORE_PLATFORM,
                doc_references=[
                    "docs/architecture/repository_scanner.md",
                    "docs/ast/python_parser_spec.md",
                ],
                semantic_tags=["ast", "parser", "inspection", "repository"],
            ),
            KnowledgeLink(
                capability_id="CAP-KNOWLEDGE-SYNCHRONIZATION",
                domain=KnowledgeDomain.DATA_INTELLIGENCE,
                doc_references=[
                    "docs/knowledge_graph/semantic_indexing.md",
                ],
                semantic_tags=["knowledge-graph", "ontology", "taxonomy"],
            ),
            KnowledgeLink(
                capability_id="CAP-PREDICTION-RISK-ASSESSMENT",
                domain=KnowledgeDomain.DATA_INTELLIGENCE,
                doc_references=[
                    "docs/prediction/blast_radius_analysis.md",
                ],
                semantic_tags=["predictive-risk", "blast-radius", "drift-detection"],
            ),
            KnowledgeLink(
                capability_id="CAP-GOVERNANCE-COMPLIANCE",
                domain=KnowledgeDomain.GOVERNANCE_COMPLIANCE,
                doc_references=[
                    "docs/security/zero_trust_governance.md",
                ],
                semantic_tags=["governance", "compliance", "policy", "attestation"],
            ),
            KnowledgeLink(
                capability_id="CAP-CONTROL-ROOM-DISPATCH",
                domain=KnowledgeDomain.RUNTIME_OPERATIONS,
                doc_references=[
                    "docs/telemetry/control_room_specs.md",
                ],
                semantic_tags=["telemetry", "control-room", "executive-dispatch"],
            ),
        ]

        for link in links:
            self.catalog.add_link(link)

        return self.catalog

    def execute_and_save(self) -> Dict[str, Any]:
        """
        Executes knowledge graph link generation and persists output JSON files.
        """
        logger.info("Executing Knowledge Engine...")
        self.build_knowledge_links()

        catalog_dict = self.catalog.to_dict()

        # Primary persistence target (reports/)
        os.makedirs(os.path.dirname(self.primary_output_path), exist_ok=True)
        with open(self.primary_output_path, "w", encoding="utf-8") as f:
            json.dump(catalog_dict, f, indent=2)

        # Local module mirror target
        local_dir = os.path.dirname(__file__)
        local_target = os.path.join(local_dir, "knowledge_links.json")
        with open(local_target, "w", encoding="utf-8") as f:
            json.dump(catalog_dict, f, indent=2)

        logger.info(
            "Successfully indexed %d knowledge links across %d domains.",
            len(self.catalog.links),
            len(set(l.domain for l in self.catalog.links.values())),
        )
        return catalog_dict