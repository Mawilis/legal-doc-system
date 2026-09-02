"""
===============================================================================
WILSY OS — FG220 DYNAMIC PLUGIN LOADER & ISOLATED INSTANTIATOR
===============================================================================

Epitome:
    Dynamic module loading and runtime instantiation engine for FG220 marketplace
    plugins. Safely imports vendor plugin entrypoints using importlib spec loaders,
    isolates module namespaces under 'wilsy.plugins.<id>', manages symbol dynamic
    binding, and enforces clean runtime unloading and garbage collection.

Biblical Worth Billions:
    "Prove all things; hold fast that which is good."
    — 1 Thessalonians 5:21

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_loader.py
===============================================================================
"""

import sys
import os
import time
import importlib.util
import types
from typing import Dict, Any, Optional, Type

from tools.eos.marketplace import logger
from tools.eos.marketplace.plugin_descriptor import PluginDescriptor, PluginState


class PluginLoadError(Exception):
    """Exception raised when dynamic plugin module loading fails."""
    pass


class PluginLoader:
    """
    Handles dynamic module importing, isolated namespace injection, entrypoint class
    instantiation, and clean unloading for Wilsy OS marketplace plugins.
    """

    def __init__(self) -> None:
        """Initializes internal dictionary tracking loaded module references."""
        self._loaded_modules: Dict[str, types.ModuleType] = {}

    def load_plugin(self, descriptor: PluginDescriptor) -> types.ModuleType:
        """
        Dynamically imports and initializes a plugin entrypoint module.

        Args:
            descriptor (PluginDescriptor): Target plugin descriptor in VERIFIED or LOADING state.

        Returns:
            types.ModuleType: Imported Python module instance.

        Raises:
            PluginLoadError: If entrypoint file is missing or fails execution during load.
        """
        start_time = time.perf_counter()
        plugin_id = descriptor.manifest.id
        entrypoint_path = os.path.join(descriptor.install_path, descriptor.entrypoint)

        if not os.path.isfile(entrypoint_path):
            error_msg = f"Plugin entrypoint file not found: '{entrypoint_path}'"
            descriptor.transition_to(PluginState.ERROR, error_msg)
            raise PluginLoadError(error_msg)

        # Module Namespace Isolation Key (e.g., wilsy.plugins.crm_analytics)
        module_name = f"wilsy.plugins.{plugin_id.replace('.', '_')}"

        try:
            descriptor.transition_to(PluginState.LOADING, "Loading plugin entrypoint into runtime")

            spec = importlib.util.spec_from_file_location(module_name, entrypoint_path)
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Failed to create module import spec for '{entrypoint_path}'.")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            self._loaded_modules[plugin_id] = module
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            descriptor.record_execution(elapsed_ms)

            logger.info(
                f"[LOADER] Dynamic load successful for '{plugin_id}' from '{entrypoint_path}' "
                f"in {elapsed_ms:.4f} ms"
            )
            return module

        except Exception as err:
            error_msg = f"Runtime error during dynamic plugin execution: {str(err)}"
            logger.error(f"[LOADER-ERROR] {error_msg}")
            if descriptor.state in [PluginState.LOADING, PluginState.VERIFIED]:
                descriptor.transition_to(PluginState.ERROR, error_msg)
            # Cleanup broken module reference
            sys.modules.pop(module_name, None)
            raise PluginLoadError(error_msg) from err

    def unload_plugin(self, plugin_id: str, descriptor: Optional[PluginDescriptor] = None) -> bool:
        """
        Safely unloads a plugin from system modules and releases reference holds.

        Args:
            plugin_id (str): Target plugin identifier.
            descriptor (Optional[PluginDescriptor]): Associated descriptor for state transition.

        Returns:
            bool: True if module was unloaded, False if it was not currently loaded.
        """
        module_name = f"wilsy.plugins.{plugin_id.replace('.', '_')}"
        unloaded = False

        if plugin_id in self._loaded_modules:
            del self._loaded_modules[plugin_id]
            unloaded = True

        if module_name in sys.modules:
            del sys.modules[module_name]
            unloaded = True

        if descriptor and descriptor.state == PluginState.ACTIVE:
            descriptor.transition_to(PluginState.DISABLED, "Unloaded from dynamic runtime")

        if unloaded:
            logger.info(f"[LOADER] Dynamic module '{module_name}' unloaded successfully.")

        return unloaded

    def is_loaded(self, plugin_id: str) -> bool:
        """Checks if a plugin module is currently loaded in the Python runtime."""
        return plugin_id in self._loaded_modules

    def get_module(self, plugin_id: str) -> Optional[types.ModuleType]:
        """Retrieves loaded module reference if active."""
        return self._loaded_modules.get(plugin_id)
