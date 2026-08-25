"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Plugin Manifest - Institutional Plugin Metadata & Declaration (FG166).
    Defines metadata schemas, version requirements, and permission policies
    for Wilsy OS extension plugins (Security, Docker, Terraform, AWS, Azure, K8s).
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional plugin manifests. Right planning and execution.
    Proverbs 16:3 - "Commit to the Lord whatever you do, and he will establish your plans."

Collaboration & Maintenance:
    - [Architecture]: Immutable dataclass for parsing and validating plugin manifests.
    - [Compliance]: Security permissions, author metadata, and version compatibility checks.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Tuple, Union

logger = logging.getLogger("WilsyOS.PluginManifest")


@dataclass(frozen=True)
class PluginManifest:
    """
    Immutable metadata declaration for a Wilsy OS extension plugin.
    """
    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    entry_point: str
    permissions: Tuple[str, ...] = field(default_factory=tuple)
    min_eos_version: str = "1.0.0"

    # [FUNCTION EXPLANATION]: Instantiates a PluginManifest from a dictionary payload.
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PluginManifest:
        """
        Creates a PluginManifest from a dictionary structure.

        Args:
            data (Dict[str, Any]): Raw dictionary data.

        Returns:
            PluginManifest: Validated manifest object.
        """
        return cls(
            plugin_id=data.get("plugin_id", "unknown-plugin"),
            name=data.get("name", "Unknown Plugin"),
            version=data.get("version", "1.0.0"),
            author=data.get("author", "Wilsy OS Engineering"),
            description=data.get("description", "No description provided."),
            entry_point=data.get("entry_point", "plugin.py"),
            permissions=tuple(data.get("permissions", [])),
            min_eos_version=data.get("min_eos_version", "1.0.0"),
        )

    # [FUNCTION EXPLANATION]: Loads and parses a plugin manifest JSON configuration file.
    @classmethod
    def from_file(cls, file_path: Union[Path, str]) -> PluginManifest:
        """
        Loads and parses a plugin manifest JSON file.

        Args:
            file_path (Path | str): Path to the manifest json file.

        Returns:
            PluginManifest: Parsed manifest object.
        """
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Plugin manifest file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Loaded plugin manifest from: {path}")
            return cls.from_dict(data)
