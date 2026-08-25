"""
===============================================================================
WILSY ENGINEERING KERNEL: OWNERSHIP GRAPH BUILDER
===============================================================================
Epitome:
    OwnershipGraphBuilder: Governance & Accountability Engine.
    Infers administrative governance by mapping architectural assets to 
    logical administrative domains.

Biblical Scale & Architecture:
    This is the "Responsibility Matrix." It enforces that no module exists 
    without an owner, creating a high-fidelity governance trace for every 
    artifact in the billion-dollar system.

Collaboration & Maintenance:
    - [Reliability]: Implements domain-based ownership inference.
    - [Security]: Establishes immutable accountability paths for audit compliance.
    - [Data Integrity]: Delivers a production-grade governance graph.
===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Tuple
from tools.eos.repository.discovery.knowledge_graph import InstitutionalKnowledgeGraph

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.builders.ownership_graph_builder")

@dataclass(frozen=True)
class OwnershipEdge:
    """
    Immutable representation of a governance link between an admin domain and an asset.
    """
    team_node_id: str
    asset_node_id: str
    edge_type: str  # 'MAINTAINS'


class OwnershipGraphBuilder:
    """
    Industrial-grade Graph Builder component for Administrative Governance.
    """

    def __init__(self, graph: InstitutionalKnowledgeGraph) -> None:
        self._graph = graph
        self._edges: List[OwnershipEdge] = []

    def _infer_owner(self, node_id: str) -> str:
        """
        [Governance Heuristic]: Maps assets to administrative domains via path.
        """
        if "tools/" in node_id:
            return "ADMIN_SYSTEM_TOOLING"
        elif "src/" in node_id:
            return "ADMIN_PRODUCT_CORE"
        return "ADMIN_SYSTEM_GENERAL"

    def build(self) -> Tuple[OwnershipEdge, ...]:
        """
        Executes governance edge construction across all modules.
        """
        logger.info("Initiating Ownership Graph build transaction via Inference.")
        
        nodes = self._graph.get_graph_state()
        
        for node in nodes:
            # Governance: Assign ownership to every discovered module
            owner = self._infer_owner(node.node_id)
            
            self._edges.append(OwnershipEdge(
                team_node_id=owner,
                asset_node_id=node.node_id,
                edge_type="MAINTAINS"
            ))

        logger.info(f"Ownership Graph built successfully. Generated {len(self._edges)} governance edges.")
        return tuple(self._edges)
