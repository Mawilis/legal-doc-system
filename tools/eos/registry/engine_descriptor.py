"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Registry Framework - Expanded Institutional Engine Descriptor.
    Provides complete institutional metadata, capabilities, ownership, priority
    weighting, and runtime state toggles for all Wilsy OS engines.

Biblical Scale & Architecture:
    Production-ready institutional descriptor schema.
    Isaiah 28:26 - "His God instructs him and teaches him the right way."

Collaboration & Maintenance:
    - [Architecture]: Standardized engine metadata contract across OS core layers.
    - Maintained by Wilson Khanyezi & Core Engineering.
    - [Updates]: Expanded to 11-field institutional schema supporting auditability,
      FG149 prioritization, and capabilities metadata.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Tuple, Dict


@dataclass(frozen=True)
class EngineDescriptor:
    """
    Immutable representation of an institutional engine registered in Wilsy OS.
    Encapsulates lifecycle attributes, dependency relationships, priority weights,
    and governance metadata.
    """

    identifier: str
    display_name: str
    version: str
    engine_type: Any
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    entrypoint: str = "execute"
    enabled: bool = True
    priority: int = 50
    author: str = "Wilson Khanyezi"
    institutional_owner: str = "Wilsy OS Core Engineering"

    def to_dict(self) -> Dict[str, Any]:
        """
        Export descriptor metadata into a JSON-serializable dictionary
        for dashboards, reporting, and auditing engines.
        """
        return {
            "identifier": self.identifier,
            "display_name": self.display_name,
            "version": self.version,
            "engine_type": str(self.engine_type),
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "entrypoint": self.entrypoint,
            "enabled": self.enabled,
            "priority": self.priority,
            "author": self.author,
            "institutional_owner": self.institutional_owner,
        }
