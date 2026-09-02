"""
===============================================================================
WILSY OS — FG220 RUNTIME CAPABILITY RESOLVER & SERVICE BROKER
===============================================================================

Epitome:
    Service brokerage and capability resolution engine for Wilsy OS plugins.
    Maintains a central registry of platform-provided service hooks (e.g., EventBus,
    Database, Logger) and validates/binds required capabilities for plugins at activation.

Biblical Worth Billions:
    "As every man hath received the gift, even so minister the same one to another,
    as good stewards of the manifold grace of God."
    — 1 Peter 4:10

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/capability_resolver.py
===============================================================================
"""

from typing import Dict, Any, List, Optional, Callable, Set

from tools.eos.marketplace import logger
from tools.eos.marketplace.plugin_descriptor import PluginDescriptor


class CapabilityResolutionError(Exception):
    """Exception raised when a required plugin capability is missing or fails binding."""
    pass


class CapabilityResolver:
    """
    Registry and broker for platform capabilities and plugin service dependency injection.
    """

    def __init__(self) -> None:
        """Initializes internal capability provider mapping."""
        self._capabilities: Dict[str, Any] = {}

    def register_capability(self, capability_name: str, service_instance: Any) -> None:
        """
        Registers a platform service provider under a named capability.

        Args:
            capability_name (str): Identifier of the capability (e.g., 'EventBus').
            service_instance (Any): Object or function implementing the capability.
        """
        self._capabilities[capability_name] = service_instance
        logger.info(f"[CAPABILITY-RESOLVER] Registered platform capability provider: '{capability_name}'")

    def unregister_capability(self, capability_name: str) -> None:
        """Removes a capability provider from the platform broker."""
        if capability_name in self._capabilities:
            del self._capabilities[capability_name]
            logger.info(f"[CAPABILITY-RESOLVER] Unregistered capability: '{capability_name}'")

    def has_capability(self, capability_name: str) -> bool:
        """Checks if a platform capability is currently available."""
        return capability_name in self._capabilities

    def get_capability(self, capability_name: str) -> Any:
        """
        Retrieves a registered platform capability service instance.

        Args:
            capability_name (str): Target capability name.

        Returns:
            Any: Service instance.

        Raises:
            CapabilityResolutionError: If capability is not registered.
        """
        if not self.has_capability(capability_name):
            raise CapabilityResolutionError(f"Requested platform capability '{capability_name}' is not registered.")
        return self._capabilities[capability_name]

    def resolve_for_plugin(self, descriptor: PluginDescriptor) -> Dict[str, Any]:
        """
        Resolves and validates all required capabilities for a plugin descriptor.

        Args:
            descriptor (PluginDescriptor): Target plugin descriptor.

        Returns:
            Dict[str, Any]: Dictionary mapping required capability names to active service instances.

        Raises:
            CapabilityResolutionError: If any required capability is missing.
        """
        plugin_id = descriptor.manifest.id
        required_caps = descriptor.manifest.capabilities.required
        resolved_services: Dict[str, Any] = {}

        logger.info(f"[CAPABILITY-RESOLVER] Resolving capabilities for plugin '{plugin_id}'...")

        missing_caps: List[str] = []
        for cap in required_caps:
            if self.has_capability(cap):
                resolved_services[cap] = self.get_capability(cap)
            else:
                missing_caps.append(cap)

        if missing_caps:
            error_msg = f"Plugin '{plugin_id}' failed capability resolution. Missing: {missing_caps}"
            logger.error(f"[CAPABILITY-ERROR] {error_msg}")
            raise CapabilityResolutionError(error_msg)

        logger.info(f"[CAPABILITY-SUCCESS] Successfully resolved {len(resolved_services)} capabilities for '{plugin_id}'.")
        return resolved_services
