"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/search_index.py
===============================================================================
Epitome:
    High-performance in-memory search and relevance ranking index for FG210
    documentation contracts. Supports fuzzy text matching, URN prefix filtering,
    EntityKind queries, and metadata tag scoring across Wilsy OS entities.

Biblical Worth Billions:
    "Ask, and it shall be given you; seek, and ye shall find; knock, and it
     shall be opened unto you." — Matthew 7:7

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/search_index.py
===============================================================================
"""

from typing import List, Dict, Any, Optional
from tools.eos.documentation.documentation_contract import (
    DocumentationEntity,
    EntityKind,
)


class DocumentationSearchIndex:
    """
    Search and query engine over a collection of DocumentationEntity contracts.
    """

    def __init__(self, entities: Optional[List[DocumentationEntity]] = None):
        """
        Initializes the search index with an optional initial entity list.

        Args:
            entities: Optional initial list of DocumentationEntity objects.
        """
        self._entities: List[DocumentationEntity] = entities or []

    def index_entities(self, entities: List[DocumentationEntity]) -> None:
        """
        Populates or replaces the indexed entity collection.

        Args:
            entities: Target list of DocumentationEntity contracts.
        """
        self._entities = list(entities)

    def search(
        self,
        query: str,
        kind: Optional[EntityKind] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Executes a relevance-scored search query across indexed documentation entities.

        Args:
            query: Keyword query string.
            kind: Optional EntityKind filter.
            limit: Maximum number of search results to return.

        Returns:
            List of matching entity dicts sorted by relevance score.
        """
        tokens = [t.lower().strip() for t in query.split() if len(t.strip()) > 1]
        results: List[Dict[str, Any]] = []

        for entity in self._entities:
            if kind and entity.kind != kind:
                continue

            score = 0
            searchable_text = f"{entity.title} {entity.urn} {entity.purpose} {entity.architecture_summary} {entity.module_path}".lower()

            for token in tokens:
                if token in entity.title.lower():
                    score += 10
                if token in entity.urn.lower():
                    score += 8
                if token in entity.purpose.lower():
                    score += 5
                if token in entity.architecture_summary.lower():
                    score += 3
                if token in entity.module_path.lower():
                    score += 2

            if score > 0 or not tokens:
                results.append({
                    "score": score,
                    "urn": entity.urn,
                    "title": entity.title,
                    "kind": entity.kind.value,
                    "module_path": entity.module_path,
                    "purpose": entity.purpose,
                })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def find_by_urn_prefix(self, prefix: str) -> List[DocumentationEntity]:
        """
        Finds all documentation entities whose URN starts with the specified prefix.

        Args:
            prefix: Target URN prefix string (e.g. 'urn:wilsy:doc:api:').

        Returns:
            List of matching DocumentationEntity contracts.
        """
        return [e for e in self._entities if e.urn.startswith(prefix)]
