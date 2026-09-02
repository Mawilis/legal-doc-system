"""
===============================================================================
WILSY OS — FG220 PLUGIN CENTRAL REGISTRY & DISCOVERY INDEX
===============================================================================

Epitome:
    Central thread-safe plugin registry and discovery index for the Wilsy OS
    marketplace architecture. Provides lookup, filtering by capability/vendor/state,
    registration lifecycle tracking, and persistent state snapshots across the platform.

Biblical Worth Billions:
    "Through wisdom is an house builded; and by understanding it is established:
    And by knowledge shall the chambers be filled with all precious and pleasant riches."
    — Proverbs 24:3-4

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_registry.py
===============================================================================
"""

import json
import os
import threading
from typing import Dict, List, Optional, Any, Set

from tools.eos.marketplace import logger
from tools.eos.marketplace.manifest import PluginManifest
from tools.eos.marketplace.plugin_descriptor import PluginDescriptor, PluginState


class PluginAlreadyExistsError(Exception):
    """Exception raised when attempting to register a plugin ID that is already present."""
    pass


class PluginNotFoundError(Exception):
    """Exception raised when looking up a plugin ID that does not exist in the registry."""
    pass


class PluginRegistry:
    """
    Thread-safe, central registry for all marketplace plugins in Wilsy OS.
    Handles lifecycle tracking, fast dynamic indexing, and storage persistence.
    """

    def __init__(self, snapshot_path: Optional[str] = None) -> None:
        """
        Initializes an empty plugin registry instance with internal locking mechanisms.

        Args:
            snapshot_path (Optional[str]): Default filesystem path for registry persistence.
        """
        self._lock = threading.RLock()
        self._plugins: Dict[str, PluginDescriptor] = {}
        self.snapshot_path = snapshot_path or os.path.join(
            os.path.dirname(__file__), "registry_snapshot.json"
        )

    def register(self, descriptor: PluginDescriptor, allow_overwrite: bool = False) -> None:
        """
        Registers a plugin descriptor in the primary lookup table.

        Args:
            descriptor (PluginDescriptor): Hydrated descriptor instance.
            allow_overwrite (bool): If True, overwrites an existing entry with the same ID.

        Raises:
            PluginAlreadyExistsError: If plugin ID exists and allow_overwrite is False.
        """
        plugin_id = descriptor.manifest.id
        with self._lock:
            if plugin_id in self._plugins and not allow_overwrite:
                raise PluginAlreadyExistsError(
                    f"Plugin '{plugin_id}' is already registered in Wilsy OS registry."
                )

            self._plugins[plugin_id] = descriptor
            logger.info(
                f"[REGISTRY] Registered plugin '{plugin_id}' v{descriptor.manifest.version} "
                f"[State: {descriptor.state.value}]"
            )

    def unregister(self, plugin_id: str) -> PluginDescriptor:
        """
        Removes a plugin from the registry index.

        Args:
            plugin_id (str): Unique plugin identifier.

        Returns:
            PluginDescriptor: The removed plugin descriptor object.

        Raises:
            PluginNotFoundError: If the plugin ID is not present.
        """
        with self._lock:
            if plugin_id not in self._plugins:
                raise PluginNotFoundError(f"Cannot unregister: Plugin '{plugin_id}' not found.")

            removed = self._plugins.pop(plugin_id)
            logger.info(f"[REGISTRY] Unregistered plugin '{plugin_id}'.")
            return removed

    def get(self, plugin_id: str) -> Optional[PluginDescriptor]:
        """
        Retrieves a plugin descriptor by its unique ID.

        Args:
            plugin_id (str): Unique identifier.

        Returns:
            Optional[PluginDescriptor]: Descriptor if found, else None.
        """
        with self._lock:
            return self._plugins.get(plugin_id)

    def has(self, plugin_id: str) -> bool:
        """Checks if a plugin ID is currently registered."""
        with self._lock:
            return plugin_id in self._plugins

    def list_all(self, state_filter: Optional[PluginState] = None) -> List[PluginDescriptor]:
        """
        Lists registered plugins, optionally filtered by lifecycle state.

        Args:
            state_filter (Optional[PluginState]): Target state enum filter.

        Returns:
            List[PluginDescriptor]: List of matching plugin descriptors.
        """
        with self._lock:
            if state_filter is None:
                return list(self._plugins.values())
            return [p for p in self._plugins.values() if p.state == state_filter]

    def find_by_capability(self, capability_name: str) -> List[PluginDescriptor]:
        """
        Finds all registered plugins that declare a specific platform capability.

        Args:
            capability_name (str): Name of required or optional capability.

        Returns:
            List[PluginDescriptor]: List of plugins supporting the capability.
        """
        with self._lock:
            results = []
            for descriptor in self._plugins.values():
                req = descriptor.manifest.capabilities.required
                opt = descriptor.manifest.capabilities.optional
                if capability_name in req or capability_name in opt:
                    results.append(descriptor)
            return results

    def find_by_vendor(self, vendor_name: str) -> List[PluginDescriptor]:
        """
        Finds all plugins authored by a specific vendor.

        Args:
            vendor_name (str): Name of the author or vendor organization.

        Returns:
            List[PluginDescriptor]: Matching plugin descriptors.
        """
        with self._lock:
            return [
                p for p in self._plugins.values()
                if p.manifest.vendor.lower() == vendor_name.lower()
            ]

    def count(self) -> int:
        """Returns total number of registered plugins."""
        with self._lock:
            return len(self._plugins)

    def clear(self) -> None:
        """Clears all entries from the in-memory registry."""
        with self._lock:
            self._plugins.clear()
            logger.info("[REGISTRY] Cleared all registered plugins.")

    def save_snapshot(self, target_path: Optional[str] = None) -> str:
        """
        Persists current registry state to a JSON snapshot artifact.

        Args:
            target_path (Optional[str]): Custom destination file path.

        Returns:
            str: Path to saved snapshot file.
        """
        out_path = target_path or self.snapshot_path
        with self._lock:
            data = {
                "count": len(self._plugins),
                "plugins": {p_id: desc.to_dict() for p_id, desc in self._plugins.items()}
            }
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.info(f"[REGISTRY] Saved registry snapshot with {len(self._plugins)} plugins to: {out_path}")
            return out_path

    def get_summary(self) -> Dict[str, Any]:
        """
        Generates telemetry summary for marketplace catalog reporting.
        """
        with self._lock:
            total = len(self._plugins)
            states_count = {state.value: 0 for state in PluginState}
            vendors: Set[str] = set()

            for desc in self._plugins.values():
                states_count[desc.state.value] += 1
                vendors.add(desc.manifest.vendor)

            return {
                "total_installed": total,
                "states_breakdown": states_count,
                "unique_vendors_count": len(vendors),
                "unique_vendors": list(vendors)
            }
