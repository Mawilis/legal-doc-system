"""
===============================================================================
WILSY ENGINEERING KERNEL: CAPABILITY GRAPH BUILDER
===============================================================================
Epitome:
    CapabilityGraphBuilder: Functional Mapping Engine.
    Infers system capabilities from code structure and interlinks them with 
    the implementation modules.

Biblical Scale & Architecture:
    This engine converts raw modules into a functional domain map. It allows 
    Wilsy OS to understand its own expertise, forming the backbone of the 
    autonomous decision-making intelligence.

Collaboration & Maintenance:
    - [Reliability]: Implements pattern-based capability inference.
    - [Security]: Enforces functional integrity by mapping implementations.
    - [Data Integrity]: Produces a high-fidelity graph of system capabilities.
===============================================================================
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List, Tuple
from tools.eos.repository.discovery.knowledge_graph import InstitutionalKnowledgeGraph

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.builders.capability_graph_builder")

# Heuristic: Patterns that define a high-level business capability
CAPABILITY_PATTERN = re.compile(r"(?:class|def)\s+([A-Z][a-zA-Z0-9_]*(?:Engine|Predictor|Service|Manager|Controller))")

@dataclass(frozen=True)
class CapabilityEdge:
    source_node_id: str
    target_node_id: str
    edge_type: str  # 'IMPLEMENTS'

class CapabilityGraphBuilder:
    """
    Industrial-grade Graph Builder for Capability Inference.
    """

    def __init__(self, graph: InstitutionalKnowledgeGraph) -> None:
        self._graph = graph
        self._edges: List[CapabilityEdge] = []

    def _extract_capabilities(self, file_path: str) -> List[str]:
        """
        [Heuristic Analysis]: Detects functional capabilities based on identifiers.
        """
        capabilities = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                matches = CAPABILITY_PATTERN.findall(content)
                capabilities.extend(matches)
        except Exception:
            pass
        return capabilities

    def build(self) -> Tuple[CapabilityEdge, ...]:
        """
        [Autonomy Event]: Dynamically stitches capabilities to modules.
        """
        logger.info("Initiating Capability Graph build transaction via Inference.")
        
        nodes = self._graph.get_graph_state()
        
        for node in nodes:
            file_path = node.metadata.get("path")
            if file_path:
                inferred_caps = self._extract_capabilities(file_path)
                for cap in inferred_caps:
                    self._edges.append(CapabilityEdge(
                        source_node_id=cap,
                        target_node_id=node.node_id,
                        edge_type="IMPLEMENTS"
                    ))

        logger.info(f"Capability Graph built successfully. Generated {len(self._edges)} capability edges.")
        return tuple(self._edges)
