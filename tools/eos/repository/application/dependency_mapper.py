"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Intelligence - Dependency Mapper.
    Analyzes Python source files to extract import statements and map inter-module
    dependencies across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise dependency mapper. Zero child's place.
    Ensures accurate AST-based import parsing and dependency tracking.

Collaboration & Maintenance:
    - [Architecture]: AST-based dependency parser for mapping intra-repo references.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Set


class DependencyMapper:
    """
    Parses Python files using AST to extract imports and map dependencies.
    """

    @staticmethod
    def extract_imports(file_path: Path | str) -> List[str]:
        """
        Extracts imported module names from a Python source file using AST.

        Args:
            file_path (Path | str): Path to the Python file.

        Returns:
            List[str]: List of imported module or package names.
        """
        path = Path(file_path)
        if not path.exists() or not path.suffix == ".py":
            return []

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(path))
        except Exception:
            return []

        imports: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return list(set(imports))

    @classmethod
    def map_repository_dependencies(cls, file_paths: List[Path | str]) -> Dict[str, List[str]]:
        """
        Maps dependencies across an entire repository file set.

        Args:
            file_paths (List[Path | str]): Collection of Python files.

        Returns:
            Dict[str, List[str]]: Mapping of file paths to their detected imports.
        """
        dependency_map: Dict[str, List[str]] = {}
        for fp in file_paths:
            path = Path(fp)
            if path.suffix == ".py":
                dependency_map[str(path)] = cls.extract_imports(path)
        return dependency_map
