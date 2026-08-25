"""
================================================================================
WILSY OS - ENTERPRISE OPERATING SYSTEM
================================================================================
FILE: tools/eos/repository/intelligence/capability_registry/capability_registry_manager.py
MODULE: Capability Registry Management
VERSION: 1.0.0
AUTHOR: Wilson Khanyezi & Wilsy OS Core Engineering Architecture Team
PURPOSE:
    Manages capability cataloging, dynamic capability lookup, health status,
    and metadata registration for all underlying intelligence services in Wilsy OS.

EPITOME / ARCHITECTURAL INTENT:
    Serves as the high-availability management interface for the Capability Registry.
    Ensures zero-downtime discovery, robust type safety, and seamless multi-tenant
    capability access controls across the enterprise suite.

COLLABORATION NOTES:
    - Maintained by Core Architecture & Legal SaaS Platform Engineering teams.
    - All dynamic type signatures must strictly use standard `typing` primitives.
================================================================================
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CapabilityRegistryManager:
    """
    Enterprise Capability Registry Manager responsible for maintaining system-wide
    capability states, lifecycle hooks, and service discovery indexes.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes the capability registry manager with optional runtime parameters.
        """
        self.config: Dict[str, Any] = config or {}
        self._capabilities: Dict[str, Dict[str, Any]] = {}
        logger.info("CapabilityRegistryManager initialized successfully.")

    def register_capability(
        self,
        capability_id: str,
        name: str,
        version: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Registers a new system capability or updates an existing entry.

        Args:
            capability_id: Unique string identifier for the capability.
            name: Human-readable name of the service or feature.
            version: Semantic version string.
            metadata: Optional additional metadata dictionary.

        Returns:
            Dict containing the registered capability record.
        """
        record: Dict[str, Any] = {
            "capability_id": capability_id,
            "name": name,
            "version": version,
            "metadata": metadata or {},
            "status": "ACTIVE"
        }
        self._capabilities[capability_id] = record
        logger.debug(f"Capability registered: {capability_id} (v{version})")
        return record

    def get_capability(self, capability_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a capability by its unique ID. Returns None if not found.
        """
        return self._capabilities.get(capability_id)

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all registered active capabilities.
        """
        return list(self._capabilities.values())

    def unregister_capability(self, capability_id: str) -> bool:
        """
        Removes a capability from the registry index.
        """
        if capability_id in self._capabilities:
            del self._capabilities[capability_id]
            logger.info(f"Capability unregistered: {capability_id}")
            return True
        return False