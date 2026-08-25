"""
===============================================================================
WILSY OS — FG226 GLOBAL MULTI-REGION PLATFORM
DISCOVERY SUBSYSTEM: GLOBAL REGISTRY
===============================================================================

File Path:
    tools/eos/geo/discovery/global_registry.py

Version:
    v226.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Provides a decentralized global registry aggregating nodes, workers, and 
    clusters across international continents (Africa, Europe, America, Asia, Australia).

Biblical Worth Billions:
    "He telleth the number of the stars; he calleth them all by their names." 
    — Psalm 147:4

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from tools.eos.geo.domain.geo_node import GeoNode


class GlobalRegistry:
    """
    Manages the global discovery registry for Wilsy OS, tracking multi-region 
    compute nodes, health states, and geographic distribution.
    """
    def __init__(self) -> None:
        self.nodes: Dict[str, GeoNode] = {}
        self.registry_created_at = datetime.now(timezone.utc).isoformat()

    def register_node(self, node: GeoNode) -> None:
        """Registers or updates a geo node within the global registry."""
        self.nodes[node.node_id] = node

    def deregister_node(self, node_id: str) -> Optional[GeoNode]:
        """Removes a geo node from the global registry."""
        return self.nodes.pop(node_id, None)

    def get_node(self, node_id: str) -> Optional[GeoNode]:
        """Retrieves a specific geo node by ID."""
        return self.nodes.get(node_id)

    def list_nodes_by_region(self, region: str) -> List[GeoNode]:
        """Filters and returns all active nodes within a specified region."""
        return [node for node in self.nodes.values() if node.region.lower() == region.lower()]

    def get_global_inventory(self) -> Dict[str, Any]:
        """Compiles a complete inventory of global nodes categorized by region."""
        inventory: Dict[str, List[Dict[str, Any]]] = {}
        for node in self.nodes.values():
            reg = node.region
            if reg not in inventory:
                inventory[reg] = []
            inventory[reg].append(node.to_dict())

        return {
            "total_nodes": len(self.nodes),
            "regions_registered": list(inventory.keys()),
            "inventory": inventory,
            "registry_checksum": hashlib.sha256(str(len(self.nodes)).encode("utf-8")).hexdigest()
        }
