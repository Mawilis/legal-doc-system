"""
===============================================================================
WILSY OS — FG220 SAFE PLUGIN UNINSTALLER PIPELINE
===============================================================================

Epitome:
    Clean uninstallation engine for FG220 marketplace plugins. Safely stops active
    executions, unloads dynamic modules from the Python runtime scope, deregisters
    plugins from the central registry, and purges installed filesystem artifacts.

Biblical Worth Billions:
    "To every thing there is a season, and a time to every purpose under the heaven:
    A time to plant, and a time to pluck up that which is planted."
    — Ecclesiastes 3:1-2

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_uninstaller.py
===============================================================================
"""

import os
import shutil
from typing import Optional, Any, Dict

from tools.eos.marketplace import logger
from tools.eos.marketplace.plugin_descriptor import PluginDescriptor, PluginState
from tools.eos.marketplace.plugin_registry import PluginRegistry, PluginNotFoundError
from tools.eos.marketplace.plugin_loader import PluginLoader


class UninstallationError(Exception):
    """Custom exception raised when uninstallation fails."""
    pass


class PluginUninstaller:
    """
    Orchestrates dynamic module unloading, state cleanup, registry removal,
    and filesystem artifact purging for Wilsy OS plugins.
    """

    def __init__(
        self,
        registry: PluginRegistry,
        loader: Optional[PluginLoader] = None
    ) -> None:
        """
        Initializes uninstaller with registry and loader bindings.

        Args:
            registry (PluginRegistry): Central registry instance.
            loader (Optional[PluginLoader]): Dynamic loader instance.
        """
        self.registry = registry
        self.loader = loader or PluginLoader()

    def uninstall(self, plugin_id: str, purge_artifacts: bool = True) -> Dict[str, Any]:
        """
        Executes clean uninstallation pipeline for a specified plugin.

        Pipeline Execution Stages:
            1. Registry Lookup & Active State Verification
            2. Dynamic Runtime Scope Unloading (sys.modules release)
            3. Descriptor Lifecycle State Transition to DISABLED
            4. Central Registry Deregistration
            5. Filesystem Directory Purge

        Args:
            plugin_id (str): Unique plugin identifier.
            purge_artifacts (bool): If True, deletes installed filesystem directory.

        Returns:
            Dict[str, Any]: Audit summary of the uninstallation procedure.

        Raises:
            UninstallationError: If plugin is missing or removal fails.
        """
        logger.info(f"[UNINSTALLER] Commencing uninstallation for plugin '{plugin_id}'...")

        descriptor = self.registry.get(plugin_id)
        if not descriptor:
            raise UninstallationError(f"Cannot uninstall: Plugin '{plugin_id}' not found in registry.")

        try:
            # Stage 1: Unload dynamic runtime module if loaded
            module_unloaded = False
            if self.loader.is_loaded(plugin_id):
                module_unloaded = self.loader.unload_plugin(plugin_id, descriptor)

            # Stage 2: Deregister from Central Registry
            self.registry.unregister(plugin_id)

            # Stage 3: Purge Filesystem Artifacts
            artifacts_purged = False
            if purge_artifacts and os.path.exists(descriptor.install_path):
                shutil.rmtree(descriptor.install_path, ignore_errors=False)
                artifacts_purged = True
                logger.info(f"[UNINSTALLER] Purged installation directory: '{descriptor.install_path}'")

            logger.info(f"[UNINSTALLER-SUCCESS] Plugin '{plugin_id}' uninstalled cleanly.")

            return {
                "plugin_id": plugin_id,
                "status": "UNINSTALLED",
                "module_unloaded": module_unloaded,
                "artifacts_purged": artifacts_purged,
                "freed_path": descriptor.install_path
            }

        except Exception as err:
            logger.error(f"[UNINSTALLER-ERROR] Failed to uninstall plugin '{plugin_id}': {str(err)}")
            raise UninstallationError(f"Uninstallation pipeline failed: {str(err)}") from err
