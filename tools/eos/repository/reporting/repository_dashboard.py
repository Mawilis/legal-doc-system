"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Reporting - Repository Dashboard.
    Aggregates classification, dependency mapping, statistics, and graph models
    into a unified repository intelligence report for Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise repository dashboard. Zero child's place.
    Enforces comprehensive operational visibility and reporting.

Collaboration & Maintenance:
    - [Architecture]: Unified reporting engine for repository intelligence.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path

from ..application.repository_classifier import RepositoryClassifier
from ..application.dependency_mapper import DependencyMapper
from ..application.repository_statistics import RepositoryStatistics
from ..graph.dependency_graph import DependencyGraph
from ..graph.module_graph import ModuleGraph
from ..graph.package_graph import PackageGraph


class RepositoryDashboard:
    """
    Synthesizes repository intelligence components into a comprehensive institutional dashboard.
    """

    @staticmethod
    def generate_dashboard(file_paths: List[Path | str]) -> Dict[str, Any]:
        """
        Generates a full repository intelligence dashboard report.

        Args:
            file_paths (List[Path | str]): Collection of repository files.

        Returns:
            Dict[str, Any]: Consolidated institutional repository report.
        """
        # 1. Classifications
        classification_breakdown = RepositoryClassifier.categorize_repository(file_paths)

        # 2. Dependency Mapping
        dependency_map = DependencyMapper.map_repository_dependencies(file_paths)

        # 3. Statistics
        statistics = RepositoryStatistics.aggregate_statistics(file_paths)

        # 4. Construct Graphs
        dep_graph = DependencyGraph()
        for source, targets in dependency_map.items():
            for target in targets:
                dep_graph.add_edge(source, target)

        module_graph = ModuleGraph()
        for fp in file_paths:
            path = Path(fp)
            if path.suffix == ".py":
                module_graph.register_module(path.stem)

        package_graph = PackageGraph()
        for fp in file_paths:
            path = Path(fp)
            if len(path.parts) > 1:
                package_graph.add_package(path.parts[0])

        return {
            "statistics": statistics,
            "classification_breakdown": classification_breakdown,
            "dependency_map": dependency_map,
            "graphs": {
                "dependency_graph": dep_graph.to_dict(),
                "module_graph": module_graph.to_dict(),
                "package_graph": package_graph.to_dict(),
            },
        }
