"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Registry Package Initialization (FG168).
    Exposes registry, manifest, checksum, and storage modules for institutional
    artifact tracking, verification, and content-addressable persistence across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready institutional artifact management suite. Zero child's place.
    Proverbs 24:3-4 - "Through wisdom is an house builded; and by understanding it is established:
    And by knowledge shall the chambers be filled with all precious and pleasant riches."

Collaboration & Maintenance:
    - [Architecture]: Package entrypoint for artifact cataloging and storage subsystems.
    - [Integrity]: Enforces immutable tracking and checksum verification across engines.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging

logger = logging.getLogger("WilsyOS.Artifacts")

try:
    from .registry import ArtifactRegistry
except ImportError:
    ArtifactRegistry = None  # type: ignore[assignment, misc]

try:
    from .manifest import ArtifactManifest
except ImportError:
    ArtifactManifest = None  # type: ignore[assignment, misc]

try:
    from .checksum import ArtifactChecksum
except ImportError:
    ArtifactChecksum = None  # type: ignore[assignment, misc]

try:
    from .storage import ArtifactStorage
except ImportError:
    ArtifactStorage = None  # type: ignore[assignment, misc]

__all__ = [
    "ArtifactRegistry",
    "ArtifactManifest",
    "ArtifactChecksum",
    "ArtifactStorage",
]
