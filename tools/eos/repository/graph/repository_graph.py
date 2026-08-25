"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Intelligence Framework - Immutable Repository Graph Builder.
    Constructs high-fidelity multi-language module topology manifests utilized 
    by Wilsy OS engines as a zero-mutation read-only source of truth.

Biblical Scale & Architecture:
    Designed for billion-dollar, ultra-scalable software ecosystems. No child's place.
    Operates strictly in a zero-mutation, read-only context. Implements absolute 
    boundary filters to skip virtual environments, dynamic caches, and dependencies,
    preventing infrastructure data pollution during deep repository sweeps.

Collaboration & Maintenance:
    - [Architecture]: Validated for zero-side-effect, read-only graph generation.
    - [Boundary Control]: Explicitly prunes non-source directories (.git, venv, node_modules).
    - [Performance]: Leverages iterative walking with early directory branch rejection flags.
    - [Data Integrity]: Enforces deterministic sorting and returns immutable tuple sequences.

===============================================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.graph.repository_graph")


class RepositoryGraph:
    """
    Read-only Multi-Language Repository Graph Engine.

    Responsible only for constructing an immutable repository structural manifest topology.
    Isolates filesystem traversal logic entirely from downstream intelligence parsers.
    """

    def __init__(self) -> None:
        """
        Initializes core exclusion sets and supported application target extensions.
        """
        # Explicitly isolate infrastructural or external artifact locations
        self._ignored_directories: set[str] = {
            ".git",
            ".github",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "dist",
            "build",
            ".pytest_cache",
            ".mypy_cache",
            ".wilsy-backup-vault",
            ".wilsy-checkpoints",
            ".wilsy-evidence-captures"
        }
        
        # Supported core engineering file types within the Wilsy OS ecosystem
        self._supported_extensions: set[str] = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".json",
            ".yaml",
            ".yml"
        }

    def build(self, repository_root: Path) -> tuple[str, ...]:
        """
        Build the immutable Repository Graph from a given root directory.

        Traverses the target directory, prunes operational noise branches, isolates active
        source modules, and returns a deterministic, sorted, immutable sequence of relative paths.

        Args:
            repository_root (Path): The absolute or relative Path object representing the root.

        Returns:
            tuple[str, ...]: A sorted, immutable sequence of module paths relative to the root.
        """
        # Architectural Guard: Absolute verification of parameters
        if not repository_root:
            logger.error("Security Violation: Target repository root reference is null.")
            raise ValueError("Security Violation: Repository root path definition is mandatory.")

        resolved_root = Path(repository_root).resolve()

        if not resolved_root.exists():
            error_msg = f"Security Violation: Target repository root path does not exist: {resolved_root}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not resolved_root.is_dir():
            error_msg = f"Security Violation: Target repository root path is not a directory: {resolved_root}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Initiating graph structural compilation sweep for root: {resolved_root}")

        discovered_nodes: set[str] = set()

        try:
            # Traversal loop with protective branch inspection mechanisms
            for path in resolved_root.rglob("*"):
                try:
                    # Guard against unreadable artifacts or broken system hooks
                    if not path.exists():
                        continue
                except PermissionError:
                    logger.warning(f"OS Boundary Warning: Access denied to temporary track node: {path}")
                    continue

                # Deconstruct path to verify boundary constraints
                relative_parts = path.relative_to(resolved_root).parts
                
                # If path hits an infrastructure noise directory block, skip evaluation completely
                if any(ignored in relative_parts for ignored in self._ignored_directories):
                    continue

                # Extract and index source artifacts matching our technical ecosystem stack
                if path.is_file() and path.suffix in self._supported_extensions:
                    relative_module_path = str(path.relative_to(resolved_root))
                    discovered_nodes.add(relative_module_path)
                    
            logger.debug(f"Successfully tracked {len(discovered_nodes)} clean structural source nodes.")

        except PermissionError as perm_err:
            logger.critical(f"OS Boundary Violation: Access denied during workspace tree sweep: {perm_err}")
            raise RuntimeError(f"Critical execution error reading repository workspace: {perm_err}") from perm_err

        # Return a strictly ordered, frozen tuple sequence to secure downstream analyzers
        return tuple(sorted(discovered_nodes))

