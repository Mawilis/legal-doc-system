"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Digital Twin - Module State & Symbol Registry (FG159).
    Tracks module-level components, classes, functions, imports, and exports
    within the in-memory Digital Twin model.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready module state registry. Zero child's place.
    Proverbs 24:3-4 - "Through wisdom a house is built, and by understanding it is established..."

Collaboration & Maintenance:
    - [Architecture]: In-memory module symbol index and structure tracking.
    - [Compliance]: Instantaneous inspection of classes, functions, and dependencies.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ModuleState:
    """
    Immutable in-memory model of a software module/package and its exported symbols.
    """
    module_path: str
    package_name: str
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    is_public: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serializes module state into a dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serializes module state into formatted JSON."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
