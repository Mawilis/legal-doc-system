"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Graph - Package Graph.
    Models package-level hierarchies and inter-package dependencies across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise package graph. Zero child's place.
    Provides high-level architectural aggregation of package nodes.

Collaboration & Maintenance:
    - [Architecture]: Package-level graph structure for macro-architectural analysis.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Set


class PackageGraph:
    """
    Graph representation focusing on package hierarchies and inter-package relationships.
    """

    def __init__(self) -> None:
        self.packages: Dict[str, Set[str]] = {}

    def add_package(self, package_name: str) -> None:
        """Register a package node."""
        if package_name not in self.packages:
            self.packages[package_name] = set()

    def add_subpackage(self, parent_package: str, subpackage_name: str) -> None:
        """Register a subpackage relationship."""
        self.add_package(parent_package)
        self.add_package(subpackage_name)
        self.packages[parent_package].add(subpackage_name)

    def get_subpackages(self, package_name: str) -> List[str]:
        """Get subpackages for a registered package."""
        return list(self.packages.get(package_name, set()))

    def to_dict(self) -> Dict[str, List[str]]:
        """Serialize package graph into a dictionary payload."""
        return {k: list(v) for k, v in self.packages.items()}
