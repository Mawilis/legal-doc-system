"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Intelligence - Repository Classifier.
    Classifies codebase modules, files, and architecture layers across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise classifier. Zero child's place.
    Enforces automated structural categorization and layer identification.

Collaboration & Maintenance:
    - [Architecture]: Rule-based module classifier for repository analysis.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class RepositoryClassifier:
    """
    Classifies repository modules and files into distinct architectural tiers and categories.
    """

    @staticmethod
    def classify_file(file_path: Path | str) -> str:
        """
        Classifies a given file path into an institutional category.

        Args:
            file_path (Path | str): Path to the file.

        Returns:
            str: Category identifier (e.g., 'CORE', 'CONTRACT', 'METRICS', 'LOGGING', 'TEST', 'UNKNOWN').
        """
        path_str = str(file_path).replace("\\", "/")

        if "tools/eos/core" in path_str:
            return "CORE_ENGINE"
        elif "tools/eos/contracts" in path_str:
            return "CONTRACT"
        elif "tools/eos/metrics" in path_str:
            return "METRICS"
        elif "tools.eos.kernel_logging" in path_str:
            return "LOGGING"
        elif "tools/eos/registry" in path_str:
            return "REGISTRY"
        elif "tools/eos/assurance" in path_str:
            return "ASSURANCE"
        elif "tools/eos/repository" in path_str:
            return "REPOSITORY_INTELLIGENCE"
        elif "test" in path_str.lower():
            return "TEST_SUITE"
        elif path_str.endswith("__init__.py"):
            return "PACKAGE_INIT"
        elif path_str.endswith(".py"):
            return "PYTHON_MODULE"
        
        return "GENERAL_ASSET"

    @classmethod
    def categorize_repository(cls, file_paths: List[Path | str]) -> Dict[str, List[str]]:
        """
        Categorizes a collection of file paths into architectural groupings.

        Args:
            file_paths (List[Path | str]): List of file paths.

        Returns:
            Dict[str, List[str]]: Mapping of category names to file paths.
        """
        categories: Dict[str, List[str]] = {}
        for fp in file_paths:
            cat = cls.classify_file(fp)
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(str(fp))
        return categories
