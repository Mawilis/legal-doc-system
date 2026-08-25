"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Knowledge linkage models mapping enterprise capabilities and codebase AST 
    entities to semantic knowledge graphs, documentation, and metadata assets.

Biblical Worth Billions:
    "A wise man will hear, and will increase learning; and a man of 
    understanding shall attain unto wise counsels." — Proverbs 1:5

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy OS)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/knowledge/knowledge_links.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional


class KnowledgeDomain(str, Enum):
    """Core domain boundaries for knowledge graph indexing."""
    CORE_PLATFORM = "CORE_PLATFORM"
    DATA_INTELLIGENCE = "DATA_INTELLIGENCE"
    GOVERNANCE_COMPLIANCE = "GOVERNANCE_COMPLIANCE"
    RUNTIME_OPERATIONS = "RUNTIME_OPERATIONS"


@dataclass
class KnowledgeLink:
    """
    Binds a capability to semantic documentation nodes, domain classifications,
    and metadata entities within the enterprise knowledge graph.
    """
    capability_id: str
    domain: KnowledgeDomain
    doc_references: List[str]
    semantic_tags: List[str]
    author: str = "Wilson Khanyezi"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes knowledge link model to a dictionary."""
        data = asdict(self)
        data["domain"] = self.domain.value if isinstance(self.domain, KnowledgeDomain) else str(self.domain)
        return data


@dataclass
class KnowledgeLinkCatalog:
    """
    Catalog storing capability-to-knowledge graph links.
    """
    links: Dict[str, KnowledgeLink] = field(default_factory=dict)

    def add_link(self, link: KnowledgeLink) -> None:
        """Registers a capability knowledge link."""
        self.links[link.capability_id] = link

    def get_link(self, capability_id: str) -> Optional[KnowledgeLink]:
        """Retrieves knowledge link for a given capability ID."""
        return self.links.get(capability_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes knowledge link catalog to dictionary representation."""
        return {
            "total_links": len(self.links),
            "links": {k: v.to_dict() for k, v in self.links.items()},
        }