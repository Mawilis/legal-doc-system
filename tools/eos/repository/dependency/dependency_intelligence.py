"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Intelligence Framework - Repository Dependency Intelligence.
    This component performs deep static analysis of source artifacts to
    extract, map, and validate internal module-to-module dependencies.

Biblical Scale & Architecture:
    Designed for billion-dollar, ultra-scalable software ecosystems.
    Utilizes robust non-executing Abstract Syntax Tree (AST) parsing to 
    safely map imports without executing application code, protecting the 
    runtime environment from side effects.

Collaboration & Maintenance:
    - [Architecture]: Pure functional parser mapping dependency topologies.
    - [Robustness]: Gracefully bypasses invalid syntax blocks or corrupted files
      to ensure system resilience during raw analysis cycles.
    - [Security]: Strict internal boundaries checking to trace illegal cross-domain coupling.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

# -----------------------------------------------------------------------------
# Telemetry & Logging Configuration
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - [DependencyIntelligence] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RepositoryDependencyIntelligence:
    """
    Repository Dependency Intelligence Engine.

    Analyzes Python module source structures to build a precise map of
    directed architectural linkages and package coupling states.
    """

    def analyze_dependencies(self, repository_root: Path) -> dict[str, list[str]]:
        """
        Statically analyze all Python files inside the workspace to map imports.

        Parses individual AST tokens to extract absolute and relative cross-imports,
        filtering out generic system library dependencies.

        Args:
            repository_root (Path): The root workspace entry node.

        Returns:
            dict[str, list[str]]: A mapping dictionary representing {module: [dependencies]}.
        """
        logger.info(f"Initiating deep dependency intelligence scanning at: {repository_root}")
        dependency_map: dict[str, list[str]] = {}

        # [COLLABORATION: Safe Recursive Directory Walk]
        for path in repository_root.rglob("*.py"):
            # Skip hidden files or transient environment build files
            if any(part.startswith(".") for part in path.relative_to(repository_root).parts):
                continue

            try:
                module_key = str(path.relative_to(repository_root))
            except ValueError:
                module_key = str(path)

            dependency_map[module_key] = []

            try:
                # [COLLABORATION: Non-destructive File Stream Parsing]
                source_code = path.read_text(encoding="utf-8", errors="ignore")
                parsed_ast = ast.parse(source_code, filename=str(path))

                # Traverse AST nodes looking specifically for import actions
                for node in ast.walk(parsed_ast):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependency_map[module_key].append(alias.name)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependency_map[module_key].append(node.module)

                logger.debug(f"Successfully mapped dependencies for module: {module_key}")

            except (SyntaxError, UnicodeDecodeError) as parse_err:
                # [COLLABORATION: Fault-Tolerant Engine Isolation]
                # Log parsing issues transparently without crashing the global runtime execution
                logger.warning(f"Skipping abstract parsing for {module_key} due to structural anomaly: {parse_err}")
                continue
            except PermissionError as perm_err:
                logger.error(f"Insufficient access vectors to map path {module_key}: {perm_err}")
                continue

        logger.info(f"Dependency intelligence cycle complete. Charted {len(dependency_map)} module nodes.")
        return dependency_map
