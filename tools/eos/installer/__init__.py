"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Installer Framework Package Initialization.
    Exposes installer engine, installer manifest, and installer builder modules.

Biblical Scale & Architecture:
    Production-ready automated installation governance suite. Zero child's place.
    Enforces robust, bulletproof system bootstrapping and deployment initialization across Wilsy OS.

Collaboration & Maintenance:
    - [Architecture]: Package entrypoint for automated installation and environment bootstrapping subsystems.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from .installer_engine import InstallerEngine
from .installer_manifest import InstallerManifest
from .installer_builder import InstallerBuilder

__all__ = [
    "InstallerEngine",
    "InstallerManifest",
    "InstallerBuilder",
]
