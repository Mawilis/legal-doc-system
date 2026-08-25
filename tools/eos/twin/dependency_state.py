"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Digital Twin - Dependency State & Graph Index (FG159).
    Tracks inter-module dependencies, import edges, and dependency trees in-memory.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready dependency state tracker. Zero child's place.
    Ecclesiastes 4:9 - "Two are better than one, because they have a good reward for their toil."

Collaboration & Maintenance:
    - [Architecture]: In-memory dependency graph and import edge indexer.
    - [Compliance]: Instantaneous topological analysis without disk scanning.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Set


@dataclass(frozen=True)
class DependencyEdge:
    """
    Immutable representation of an import or reference edge between two files/modules.
    """
    source_path: str
    target_path: str
    dependency_type: str = "import"  # import, inheritance, composition

    def to_dict(self) -> Dict[str, Any]:
        """Serializes dependency edge into a dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class DependencyState:
    """
    Immutable in-memory dependency graph capturing the entire repository's module coupling.
    """
    edges: List[DependencyEdge] = field(default_factory=list)
    adjacency_list: Dict[str, List[str]] = field(default_factory=dict)

    # [FUNCTION EXPLANATION]: Queries downstream dependencies for a given module from memory.
    def get_dependencies_for(self, module_path: str) -> List[str]:
        """
        Returns all modules depended upon by the specified module.
        """
        return self.adjacency_list.get(module_path, [])

    def to_dict(self) -> Dict[str, Any]:
        """Serializes dependency state into a dictionary."""
        return {
            "total_edges": len(self.edges),
            "edges": [e.to_dict() for e in self.edges],
            "adjacency_list": self.adjacency_list,
        }

    def to_json(self) -> str:
        """Serializes dependency state into formatted JSON."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
