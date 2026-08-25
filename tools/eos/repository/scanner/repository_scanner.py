"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Intelligence Framework - Repository Scanner.
    This component conducts high-performance, safe filesystem analysis to
    extract physical artifact counts, forming the baseline structural metrics
    used by the Wilsy OS Intelligence Framework.

Biblical Scale & Architecture:
    Designed for billion-dollar, ultra-scalable software ecosystems.
    Operates strictly as a read-only analysis scanner. It cleanly maps raw
    system realities into type-safe, validated domain metric records without
    altering filesystem states.

Collaboration & Maintenance:
    - [Architecture]: Follows clean-room isolation principles for core scanning layers.
    - [Security]: Guards path lookups strictly to protect against symlink loops.
    - [Performance]: Uses iterative path generators to parse massive enterprise trees
      without memory consumption spikes.

===============================================================================
"""

from __future__ import annotations

import logging
from pathlib import Path
from ..domain.models import RepositoryMetrics

# -----------------------------------------------------------------------------
# Telemetry & Logging Configuration
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RepositoryScanner:
    """
    High-Performance Repository Scanner.

    Responsible for exploring physical workspace pathways to quantify Python 
    modules, initializers, and package footprints within Wilsy OS modules.
    """

    def scan(self, repository_root: Path) -> RepositoryMetrics:
        """
        Scan the target workspace root and extract execution metric values.

        Traverses all sub-directories safely to track active packages and scripts
        while handling file system anomalies or missing read access vectors.

        Args:
            repository_root (Path): Physical directory entry location.

        Returns:
            RepositoryMetrics: A type-safe dataclass structure carrying verified counts.

        Raises:
            ValueError: If the target repository path is structurally invalid.
            PermissionError: If root system reads are blocked by access permissions.
        """
        # [COLLABORATION: System Path Verification]
        if not repository_root.exists():
            error_msg = f"Scanner failed: Target root path does not exist: {repository_root}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not repository_root.is_dir():
            error_msg = f"Scanner failed: Path target must be a valid directory: {repository_root}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Executing repository artifact scan at target: {repository_root}")

        file_count = 0
        directory_count = 0
        python_module_count = 0
        package_count = 0

        try:
            # [COLLABORATION: Traversal Optimization Matrix]
            # Iterating cleanly through the tree structure via rglob generator pattern
            for path in repository_root.rglob("*"):
                
                # Exclude hidden directories or hidden system tracks (.git, .idea, etc.)
                if any(part.startswith(".") for part in path.relative_to(repository_root).parts):
                    continue

                if path.is_dir():
                    directory_count += 1

                elif path.is_file():
                    file_count += 1

                    # Increment file tracking counters for Python modules
                    if path.suffix == ".py":
                        python_module_count += 1

                        # Match packages containing explicit initiation hooks
                        if path.name == "__init__.py":
                            package_count += 1

            logger.info(
                f"Scan finished. Files tracked: {file_count} | "
                f"Directories tracked: {directory_count} | "
                f"Modules parsed: {python_module_count} | "
                f"Packages registered: {package_count}"
            )

        except PermissionError as perm_err:
            # [COLLABORATION: Access Failures Security Management]
            logger.error(f"Ecosystem scan aborted due to missing disk system permissions: {perm_err}")
            raise

        # Return instantiated domain metrics block directly back into evaluation chain
        return RepositoryMetrics(
            file_count=file_count,
            directory_count=directory_count,
            python_module_count=python_module_count,
            package_count=package_count,
        )
