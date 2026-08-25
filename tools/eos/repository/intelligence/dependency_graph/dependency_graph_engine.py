"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Enterprise Dependency Graph Engine constructing directed capability execution
    networks, relationship weights, and cascade resolution paths for Wilsy OS.

Biblical Worth Billions:
    "For as the body is one, and hath many members, and all the members of that
    one body, being many, are one body: so also is Christ." — 1 Corinthians 12:12

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/dependency_graph/dependency_graph_engine.py
===============================================================================
"""

from __future__ import annotations

import json
import os
import logging
from typing import Dict, Any

from.dependency_models import ExecutionDependencyGraph, DependencyRelationshipType
from.dependency_resolver import DependencyResolver

logger = logging.getLogger("WilsyOS.FG231C.DependencyGraphEngine")


class DependencyGraphEngine:
    """
    Sovereign dependency graph engine responsible for constructing, linking,
    resolving cascade propagation paths, and persisting execution graph topology.
    """

    def __init__(self, primary_output_path: str = "reports/DependencyGraph.json") -> None:
        self.primary_output_path = primary_output_path
        self.graph = ExecutionDependencyGraph()

    def build_core_dependency_graph(self) -> ExecutionDependencyGraph:
        """
        Constructs the foundational execution dependency graph across core capabilities.
        """
        self.graph.add_edge(
            source="CAP-REPOSITORY-SCAN",
            target="CAP-KNOWLEDGE-SYNCHRONIZATION",
            relationship_type=DependencyRelationshipType.TRIGGERS,
            weight=1.0,
            criticality="SOVEREIGN",
        )
        self.graph.add_edge(
            source="CAP-KNOWLEDGE-SYNCHRONIZATION",
            target="CAP-PREDICTIVE-RISK-ASSESSMENT",
            relationship_type=DependencyRelationshipType.PROPAGATES_TO,
            weight=0.95,
            criticality="HIGH",
        )
        self.graph.add_edge(
            source="CAP-PREDICTIVE-RISK-ASSESSMENT",
            target="CAP-GOVERNANCE-COMPLIANCE",
            relationship_type=DependencyRelationshipType.ENFORCES,
            weight=1.0,
            criticality="MISSION_CRITICAL",
        )
        self.graph.add_edge(
            source="CAP-GOVERNANCE-COMPLIANCE",
            target="CAP-CONTROL-ROOM-DISPATCH",
            relationship_type=DependencyRelationshipType.DISPATCHES,
            weight=1.0,
            criticality="SOVEREIGN",
        )

        return self.graph

    def execute_and_save(self) -> Dict[str, Any]:
        """
        Builds the graph, calculates resolution paths, and persists output artifacts.
        """
        logger.info("Executing Dependency Graph Engine...")
        self.build_core_dependency_graph()

        resolver = DependencyResolver(self.graph)
        cascade_path = resolver.resolve_cascade_path("CAP-REPOSITORY-SCAN")

        graph_dict = self.graph.to_dict()
        graph_dict["master_cascade_path"] = cascade_path

        # Primary persistence target (reports/)
        os.makedirs(os.path.dirname(self.primary_output_path), exist_ok=True)
        with open(self.primary_output_path, "w", encoding="utf-8") as f:
            json.dump(graph_dict, f, indent=2)

        # Local module mirror target
        local_dir = os.path.dirname(__file__)
        local_target = os.path.join(local_dir, "dependency_graph.json")
        with open(local_target, "w", encoding="utf-8") as f:
            json.dump(graph_dict, f, indent=2)

        logger.info("Successfully calculated dependency graph with %d nodes and %d edges.", len(self.graph.nodes), len(self.graph.edges))
        return graph_dict