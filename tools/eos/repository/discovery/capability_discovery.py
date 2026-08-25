"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Fidelity Automated Capability Discovery and Feature Mapping Engine.
    Statically inspects discovered codebase artifacts to extract, classify, 
    and index the logical capabilities exposed by the system architecture.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready discovery component. No child's place.
    Operates strictly as an immutable extractor over code paths. Uses pre-compiled
    structural validation patterns to isolate formal system functional markers 
    without running live modules or triggering runtime environment contamination.

Collaboration & Maintenance:
    - [Reliability]: Implements abstract pattern analysis over system node buffers.
    - [Security]: Enforces strict validation layers over structural capability metadata.
    - [Data Integrity]: Delivers completely frozen data models to block downstream mutations.

===============================================================================
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.discovery.capability_discovery")


@dataclass(frozen=True)
class CapabilitySignature:
    """
    Immutable representation of an isolated operational capability node signature.
    """
    capability_id: str
    target_module: str
    component_type: str  # e.g., 'class', 'function', 'decorator'
    description: str


class CapabilityDiscovery:
    """
    Industrial-grade Capability Extractor and Interface Discovery Component.
    Scans source code structures to catalog business logic boundaries and framework assets.
    """

    def __init__(self) -> None:
        """
        Initializes capability matching matrices with optimized tracking signatures.
        """
        # Architectural pattern: Matches @capability("domain.feature") or capability_id = "..."
        self._capability_decorator_regex = re.compile(
            r'@capability\s*\(\s*["\']([^"\']+)["\']\s*\)'
        )
        self._capability_explicit_assignment_regex = re.compile(
            r'CAPABILITY_ID\s*=\s*["\']([^"\']+)["\']'
        )

    def discover_in_file(self, repository_root: Path, relative_file_path: str) -> tuple[CapabilitySignature, ...]:
        """
        Statically inspects a single workspace file node to isolate embedded capability signatures.
        """
        full_path = Path(repository_root) / relative_file_path
        if not full_path.exists():
            logger.warning(f"Discovery Alert: Intended file node target does not exist: {full_path}")
            return ()

        # Restrict discovery analysis strictly to readable script segments
        if full_path.suffix not in {".py", ".ts", ".js"}:
            return ()

        logger.debug(f"Scanning target node structure for capabilities: {relative_file_path}")
        found_signatures: list[CapabilitySignature] = []

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as src_file:
                for line_idx, line in enumerate(src_file, start=1):
                    # Check for explicit structural annotation decorators
                    dec_match = self._capability_decorator_regex.search(line)
                    if dec_match:
                        cap_id = dec_match.group(1).strip()
                        found_signatures.append(
                            CapabilitySignature(
                                capability_id=cap_id,
                                target_module=relative_file_path,
                                component_type="decorator",
                                description=f"Decorated capability found at line {line_idx}"
                            )
                        )
                        continue

                    # Check for explicit block assignment definitions
                    assign_match = self._capability_explicit_assignment_regex.search(line)
                    if assign_match:
                        cap_id = assign_match.group(1).strip()
                        found_signatures.append(
                            CapabilitySignature(
                                capability_id=cap_id,
                                target_module=relative_file_path,
                                component_type="assignment",
                                description=f"Explicit CAPABILITY_ID assignment found at line {line_idx}"
                            )
                        )

        except Exception as err:
            logger.error(f"Discovery Fault: Structural processing error on node {relative_file_path}: {err}")
            # Keep system runtime intact; do not drop total loop processing state

        return tuple(found_signatures)

    def discover_all(self, repository_root: Path, file_manifest: tuple[str, ...]) -> tuple[CapabilitySignature, ...]:
        """
        Runs comprehensive capability tracking checks over an entire validated file manifest vector.
        """
        logger.info(f"Initiating full architectural Capability Discovery phase across {len(file_manifest)} nodes.")
        master_registry: list[CapabilitySignature] = []

        for relative_file_path in file_manifest:
            file_signatures = self.discover_in_file(repository_root, relative_file_path)
            master_registry.extend(file_signatures)

        logger.info(f"Capability Discovery phase finalized. Successfully registered {len(master_registry)} distinct signatures.")
        return tuple(sorted(master_registry, key=lambda x: x.capability_id))

