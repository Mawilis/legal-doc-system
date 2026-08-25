"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Fidelity Automated Ownership Discovery and Codebase Mapping Engine.
    Statically inspects module headers to isolate, categorize, and register 
    institutional ownership telemetry across the repository topography.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready enterprise engine. No child's place.
    Operates strictly as a read-only metadata extractor over source nodes. Uses
    bounded lookaheads to identify explicit structural ownership fields without
    introducing high-latency file scanning loops.

Collaboration & Maintenance:
    - [Reliability]: Implements bounded structural parsing over module headers.
    - [Security]: Enforces type-safe boundary enforcement over metadata records.
    - [Data Integrity]: Delivers completely frozen data models to eliminate side-effects.

===============================================================================
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.discovery.ownership_discovery")


@dataclass(frozen=True)
class OwnershipRecord:
    """
    Immutable representation of an isolated operational module ownership signature.
    """
    target_module: str
    owner_team: str
    maintainer_group: str


class OwnershipDiscovery:
    """
    Industrial-grade Ownership Extractor and Codebase Asset Mapping Component.
    Parses module metadata blocks to organize domain responsibility and routing matrices.
    """

    def __init__(self, header_scan_limit: int = 50) -> None:
        """
        Initializes the ownership scanner with bounded parsing constraints.
        
        Args:
            header_scan_limit (int): Max number of initial lines to scan to prevent full-file thrashed loops.
        """
        self._header_scan_limit = header_scan_limit
        
        # Pre-compiled high-performance structural regex compilation matrices
        self._owner_regex = re.compile(
            r'(?:[#*]|\b)(?:Owner|Team|Domain)\s*:\s*["\']?([^"\n\']+)["\']?', re.IGNORECASE
        )
        self._maintainer_regex = re.compile(
            r'(?:[#*]|\b)(?:Maintainer|Group|Lead)\s*:\s*["\']?([^"\n\']+)["\']?', re.IGNORECASE
        )

    def discover_in_file(self, repository_root: Path, relative_file_path: str) -> OwnershipRecord:
        """
        Statically inspects the header block of a source file node to extract structural ownership tags.
        """
        full_path = Path(repository_root) / relative_file_path
        default_record = OwnershipRecord(
            target_module=relative_file_path,
            owner_team="unassigned.core",
            maintainer_group="unassigned.general"
        )

        if not full_path.exists() or full_path.suffix not in {".py", ".ts", ".js", ".json"}:
            return default_record

        logger.debug(f"Scanning header boundaries for ownership telemetry: {relative_file_path}")

        owner_match_val = None
        maintainer_match_val = None

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as src_file:
                for idx, line in enumerate(src_file):
                    if idx >= self._header_scan_limit:
                        break

                    # Check for explicit owner definitions
                    if not owner_match_val:
                        o_match = self._owner_regex.search(line)
                        if o_match:
                            owner_match_val = o_match.group(1).strip()

                    # Check for explicit maintainer definitions
                    if not maintainer_match_val:
                        m_match = self._maintainer_regex.search(line)
                        if m_match:
                            maintainer_match_val = m_match.group(1).strip()

                    # Short-circuit loop early if both attributes are found
                    if owner_match_val and maintainer_match_val:
                        break

        except Exception as err:
            logger.error(f"Ownership Discovery Fault: Analysis failed on node {relative_file_path}: {err}")

        return OwnershipRecord(
            target_module=relative_file_path,
            owner_team=owner_match_val if owner_match_val else "unassigned.core",
            maintainer_group=maintainer_match_val if maintainer_match_val else "unassigned.general"
        )

    def discover_all(self, repository_root: Path, file_manifest: tuple[str, ...]) -> tuple[OwnershipRecord, ...]:
        """
        Compiles structural ownership matrices across an entire validated file manifest layout.
        """
        logger.info(f"Initiating full architectural Ownership Discovery pass across {len(file_manifest)} nodes.")
        ownership_registry: list[OwnershipRecord] = []

        for relative_file_path in file_manifest:
            record = self.discover_in_file(repository_root, relative_file_path)
            ownership_registry.append(record)

        logger.info("Ownership Discovery phase finalized successfully.")
        return tuple(sorted(ownership_registry, key=lambda x: x.target_module))

