"""
===============================================================================
WILSY OS — FG220 UNIFIED MARKETPLACE PUBLIC API FACADE
===============================================================================

Epitome:
    Unified entrypoint facade for the Wilsy OS FG220 marketplace subsystem.
    Exposes high-level synchronous and asynchronous operations for plugin lifecycle
    management, registry queries, and sandboxed execution.

Biblical Worth Billions:
    "Let all things be done decently and in order."
    — 1 Corinthians 14:40

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/marketplace_api.py
===============================================================================
"""

from typing import Dict, Any, List, Optional

from tools.eos.marketplace import logger
from tools.eos.marketplace.plugin_registry import PluginRegistry
from tools.eos.marketplace.capability_resolver import CapabilityResolver
from tools.eos.marketplace.plugin_installer import PluginInstaller, InstallationError
from tools.eos.marketplace.plugin_uninstaller import PluginUninstaller, UninstallationError
from tools.eos.marketplace.plugin_updater import PluginUpdater, UpdateError
from tools.eos.marketplace.plugin_lifecycle import PluginLifecycleManager, LifecycleTransitionError
from tools.eos.marketplace.plugin_sandbox import SandboxResult


class MarketplaceAPI:
    """
    High-level facade orchestrating all marketplace services and plugin operations.
    """

    def __init__(
        self,
        install_root_dir: Optional[str] = None,
        kernel_version: str = "1.5.0",
        target_abi: str = "FG211"
    ) -> None:
        """
        Initializes central registry, capability broker, installer, uninstaller,
        updater, and lifecycle management subsystems.
        """
        self.registry = PluginRegistry()
        self.capability_resolver = CapabilityResolver()
        
        self.installer = PluginInstaller(
            registry=self.registry,
            install_root_dir=install_root_dir
        )
        self.uninstaller = PluginUninstaller(registry=self.registry)
        self.updater = PluginUpdater(
            registry=self.registry,
            installer=self.installer,
            uninstaller=self.uninstaller
        )
        self.lifecycle_manager = PluginLifecycleManager(
            registry=self.registry,
            capability_resolver=self.capability_resolver
        )
        logger.info("[MARKETPLACE-API] Wilsy OS FG220 Marketplace Subsystem initialized successfully.")

    def register_platform_capability(self, name: str, service_instance: Any) -> None:
        """Registers a platform capability provider."""
        self.capability_resolver.register_capability(name, service_instance)

    def install_plugin(self, source_dir: str, manifest_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Installs a plugin package from directory."""
        try:
            descriptor = self.installer.install_from_directory(source_dir, manifest_dict)
            return {"success": True, "plugin_id": descriptor.manifest.id, "state": descriptor.state.value}
        except InstallationError as err:
            return {"success": False, "error": str(err)}

    def uninstall_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Uninstalls a plugin by ID."""
        try:
            summary = self.uninstaller.uninstall(plugin_id, purge_artifacts=True)
            return {"success": True, "summary": summary}
        except UninstallationError as err:
            return {"success": False, "error": str(err)}

    def update_plugin(self, source_dir: str, new_manifest_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Performs atomic update on an installed plugin."""
        try:
            descriptor = self.updater.update_plugin(source_dir, new_manifest_dict)
            return {"success": True, "plugin_id": descriptor.manifest.id, "version": descriptor.manifest.version}
        except UpdateError as err:
            return {"success": False, "error": str(err)}

    def activate_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Activates a plugin."""
        try:
            descriptor = self.lifecycle_manager.activate_plugin(plugin_id)
            return {"success": True, "plugin_id": plugin_id, "state": descriptor.state.value}
        except LifecycleTransitionError as err:
            return {"success": False, "error": str(err)}

    def deactivate_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Deactivates a plugin."""
        try:
            descriptor = self.lifecycle_manager.deactivate_plugin(plugin_id)
            return {"success": True, "plugin_id": plugin_id, "state": descriptor.state.value}
        except LifecycleTransitionError as err:
            return {"success": False, "error": str(err)}

    def execute_method(self, plugin_id: str, method_name: str, *args: Any, **kwargs: Any) -> SandboxResult:
        """Executes a sandboxed method on an active plugin."""
        return self.lifecycle_manager.execute_plugin_method(plugin_id, method_name, *args, **kwargs)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """Lists all registered plugins."""
        return [desc.to_dict() for desc in self.registry.list_all()]
