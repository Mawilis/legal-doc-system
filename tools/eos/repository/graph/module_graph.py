"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Graph - Module Graph.
    Models inter-module relationships, export visibility, and structural cohesion
    across Wilsy OS codebases.

Biblical Scale & Architecture:
    Production-ready enterprise module graph. Zero child's place.
    Provides hierarchical module structuring and relationship querying.

Collaboration & Maintenance:
    - [Architecture]: Graph analyzer for individual Python module nodes and boundaries.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Set


class ModuleGraph:
    """
    Graph representation focusing on Python module nodes and their internal linkages.
    """

    def __init__(self) -> None:
        self.modules: Dict[str, Set[str]] = {}

    def register_module(self, module_name: str, exports: List[str] | None = None) -> None:
        """
        Register a module and its exported symbols.

        Args:
            module_name (str): Qualified name of the module.
            exports (List[str] | None): Optional list of exported symbols.
        """
        if module_name not in self.modules:
            self.modules[module_name] = set()
        if exports:
            for exp in exports:
                self.modules[module_name].add(exp)

    def get_module_exports(self, module_name: str) -> List[str]:
        """Get exports for a registered module."""
        return list(self.modules.get(module_name, set()))

    def to_dict(self) -> Dict[str, List[str]]:
        """Serialize module graph into a dictionary payload."""
        return {k: list(v) for k, v in self.modules.items()}
